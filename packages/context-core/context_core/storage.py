"""The storage adapter: the only place that touches where a root lives.

Written from what abrir.py, cerrar.py and generar_vista.py do to files today (step 0, task 2 of
`shared-memory/product-design/entregables/hosted-path.md`): they read text and note its version, list folders, stat
files, write a file whole and atomically only if nobody changed it since it was read, create folders, move a file to
archive it, and hold a lock per project while they close. That is the whole interface. `FolderStorage` is the
connected-folder adapter; a Drive adapter (step 1) implements the same methods with Drive's file ids and etags.

Three rules every adapter keeps, because a bug above it must not reach outside the root (hosted-security.md):
- paths are POSIX strings relative to the root; absolute paths, «..», and anything resolving outside the root fail;
- there is no delete: the method never deletes a file, so the adapter cannot;
- a write names the version it read, and fails with `Conflict` if the file changed since (two closes at once).
"""
from __future__ import annotations

import contextlib
import hashlib
import os
import pathlib
import posixpath
import tempfile
from dataclasses import dataclass
from typing import Iterator, Optional, Protocol, runtime_checkable

__all__ = ["Version", "Document", "Entry", "Conflict", "OutsideRoot", "Storage", "FolderStorage"]


@dataclass(frozen=True)
class Version:
    """What a write compares against. For a folder: mtime, size and content hash; for Drive: the etag."""
    token: str
    size: int
    modified_ns: int


@dataclass(frozen=True)
class Document:
    text: str          # «\r\n» turned into «\n», BOM dropped
    version: Version
    crlf: bool         # the file used «\r\n»: a write keeps it


@dataclass(frozen=True)
class Entry:
    name: str
    kind: str          # "file" or "dir"
    size: int = 0
    modified_ns: int = 0


class Conflict(Exception):
    """The file changed between the read and the write."""


class OutsideRoot(ValueError):
    """The path is absolute, climbs with «..», or resolves outside the root."""


@runtime_checkable
class Storage(Protocol):
    def read(self, path: str) -> Optional[Document]: ...
    def stat(self, path: str) -> Optional[Entry]: ...
    def list(self, path: str = "") -> list[Entry]: ...
    def write(self, path: str, text: str, *, expected: Optional[Version], crlf: bool = False) -> Version: ...
    def make_dir(self, path: str) -> None: ...
    def move(self, src: str, dst: str) -> None: ...
    def lock(self, path: str) -> contextlib.AbstractContextManager: ...
    @property
    def name(self) -> str: ...


def clean(path: str) -> str:
    """The canonical relative path, or OutsideRoot."""
    p = (path or "").replace("\\", "/")
    if p.startswith("/") or (len(p) > 1 and p[1] == ":"):
        raise OutsideRoot(path)
    parts = [x for x in p.split("/") if x not in ("", ".")]
    if any(x == ".." for x in parts):
        raise OutsideRoot(path)
    return posixpath.join(*parts) if parts else ""


class FolderStorage:
    """A root that is a folder on this machine (the plugin's case: Drive for desktop, iCloud, a local folder)."""

    def __init__(self, root: str | os.PathLike):
        self.root = pathlib.Path(root).resolve()

    @property
    def name(self) -> str:
        return self.root.name

    def _p(self, path: str) -> pathlib.Path:
        rel = clean(path)
        p = self.root / rel if rel else self.root
        # a symlink inside the root must not lead out of it
        real = pathlib.Path(os.path.realpath(p))
        if real != self.root and self.root not in real.parents:
            raise OutsideRoot(path)
        return p

    @staticmethod
    def _version(b: bytes, st: os.stat_result) -> Version:
        return Version(hashlib.sha1(b).hexdigest(), st.st_size, st.st_mtime_ns)

    def read(self, path: str) -> Optional[Document]:
        p = self._p(path)
        try:
            with open(p, "rb") as f:
                b = f.read()
            st = os.stat(p)
        except (FileNotFoundError, IsADirectoryError, NotADirectoryError, PermissionError):
            return None
        t = b.decode("utf-8-sig", errors="replace")
        return Document(t.replace("\r\n", "\n"), self._version(b, st), "\r\n" in t)

    def stat(self, path: str) -> Optional[Entry]:
        p = self._p(path)
        try:
            st = os.stat(p)
        except OSError:
            return None
        return Entry(p.name, "dir" if p.is_dir() else "file", st.st_size, st.st_mtime_ns)

    def list(self, path: str = "") -> list[Entry]:
        p = self._p(path)
        out = []
        try:
            names = sorted(os.listdir(p))
        except OSError:
            return out
        for n in names:
            try:
                st = os.stat(p / n)
            except OSError:
                continue
            out.append(Entry(n, "dir" if (p / n).is_dir() else "file", st.st_size, st.st_mtime_ns))
        return out

    def _current(self, p: pathlib.Path) -> Optional[Version]:
        try:
            with open(p, "rb") as f:
                b = f.read()
            return self._version(b, os.stat(p))
        except FileNotFoundError:
            return None

    def write(self, path: str, text: str, *, expected: Optional[Version], crlf: bool = False) -> Version:
        """Writes whole and atomically (a temporary beside it, then a rename). `expected=None` means the file must not
        exist yet; otherwise its content must still be the one read. Callers hold `lock()` around read and write."""
        p = self._p(path)
        now = self._current(p)
        if (expected is None) != (now is None) or (now and expected and now.token != expected.token):
            raise Conflict(path)
        if crlf:
            text = text.replace("\n", "\r\n")
        fd, tmp = tempfile.mkstemp(prefix="." + p.name + ".", suffix=".memoria-tmp", dir=p.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
                f.write(text)
            os.replace(tmp, p)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
        return self._current(p)  # type: ignore[return-value]

    def make_dir(self, path: str) -> None:
        self._p(path).mkdir(parents=True, exist_ok=True)

    def move(self, src: str, dst: str) -> None:
        """Moves a file within the root; fails if the destination exists (archiving never overwrites)."""
        s, d = self._p(src), self._p(dst)
        if d.exists():
            raise Conflict(dst)
        d.parent.mkdir(parents=True, exist_ok=True)
        os.rename(s, d)

    @contextlib.contextmanager
    def lock(self, path: str) -> Iterator[None]:
        """A lock between processes of this machine, as cerrar.py's Cerrojo: a file in the shared temp folder."""
        h = hashlib.sha1(str(self._p(path).resolve()).encode()).hexdigest()[:16]
        f = None
        try:
            import fcntl
            f = open(os.path.join(tempfile.gettempdir(), f"memoria-lock-{h}.lock"), "a+")
            fcntl.flock(f, fcntl.LOCK_EX)
        except Exception:
            f = None
        try:
            yield
        finally:
            if f:
                try:
                    import fcntl
                    fcntl.flock(f, fcntl.LOCK_UN)
                except Exception:
                    pass
                f.close()
