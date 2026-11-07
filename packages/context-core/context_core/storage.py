"""The storage adapter: the only place that touches where a root lives.

Written from what abrir.py, cerrar.py and generar_vista.py do to files today (step 0, task 2 of
`shared-memory/product-design/entregables/hosted-path.md`): they read text and note its version, list folders, stat
files, write a file whole and atomically only if nobody changed it since it was read, create folders, move a file to
archive it, and hold a lock per project while they close. That is the whole interface. `FolderStorage` is the
connected-folder adapter; a Drive adapter (step 1) implements the same methods with Drive's file ids and etags.

Four rules every adapter keeps, because a bug above it must not reach outside the root (hosted-security.md):
- paths are POSIX strings relative to the root; absolute paths, «..», and anything resolving outside the root fail;
- links are not followed: a path through a symbolic link inside the root (a Drive shortcut, for the Drive adapter) is
  not part of the root, because a link can make a public path serve a restricted file or another project's register
  (review of consultar, finding 4). It reads as missing, is left out of listings, and cannot be written;
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

__all__ = ["Version", "Document", "Entry", "Conflict", "OutsideRoot", "NotUTF8", "Storage", "FolderStorage"]


@dataclass(frozen=True)
class Version:
    """What a write compares against. For a folder: mtime, size and content hash; for Drive: the etag."""
    token: str
    size: int
    modified_ns: int
    crlf: bool = False   # the file used «\r\n»: a write that names this version keeps it
    bom: bool = False    # it started with a UTF-8 BOM: kept too


@dataclass(frozen=True)
class Document:
    text: str          # «\r\n» turned into «\n», BOM dropped
    version: Version
    crlf: bool         # the file used «\r\n»: a write keeps it
    utf8: bool = True  # False: the bytes are not valid UTF-8; the text is a lossy reading and `write` refuses it


@dataclass(frozen=True)
class Entry:
    name: str
    kind: str          # "file" or "dir"
    size: int = 0
    modified_ns: int = 0


class Conflict(Exception):
    """The file changed between the read and the write."""


class NotUTF8(ValueError):
    """The file is not valid UTF-8: rewriting it from a lossy reading would corrupt it."""


class OutsideRoot(ValueError):
    """The path is absolute, climbs with «..», or resolves outside the root."""


@runtime_checkable
class Storage(Protocol):
    def read(self, path: str) -> Optional[Document]: ...
    def stat(self, path: str) -> Optional[Entry]: ...
    def list(self, path: str = "") -> list[Entry]: ...
    def write(self, path: str, text: str, *, expected: Optional[Version], crlf: Optional[bool] = None) -> Version: ...
    def make_dir(self, path: str) -> None: ...
    def move(self, src: str, dst: str) -> None: ...
    def lock(self, path: str) -> contextlib.AbstractContextManager[bool]: ...
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
        if not self._inside(p):
            raise OutsideRoot(path)
        return p

    def _through_link(self, p: pathlib.Path) -> bool:
        """Whether any part of the path below the root is a symbolic link: such a path is not part of the root."""
        q = p
        while q != self.root and self.root in q.parents:
            if q.is_symlink():
                return True
            q = q.parent
        return False

    def _served(self, path: str) -> Optional[pathlib.Path]:
        """The path to read, stat or list, or None when it goes through a link, wherever the link points: one link
        written by anyone must not stop the whole root from loading (review of 1.25.6, finding 4). A path that is wrong
        as written (absolute, «..») still raises."""
        rel = clean(path)
        p = self.root / rel if rel else self.root
        if self._through_link(p) or not self._inside(p):
            return None
        return p

    @staticmethod
    def _version(b: bytes, st: os.stat_result) -> Version:
        return Version(hashlib.sha1(b).hexdigest(), st.st_size, st.st_mtime_ns,
                       b"\r\n" in b, b.startswith(b"\xef\xbb\xbf"))

    def _inside(self, p: pathlib.Path) -> bool:
        real = pathlib.Path(os.path.realpath(p))
        return real == self.root or self.root in real.parents

    def read(self, path: str) -> Optional[Document]:
        p = self._served(path)
        if p is None:
            return None
        try:
            with open(p, "rb") as f:
                b = f.read()
            st = os.stat(p)
        except (FileNotFoundError, IsADirectoryError, NotADirectoryError, PermissionError):
            return None
        try:
            t, ok = b.decode("utf-8-sig"), True
        except UnicodeDecodeError:
            t, ok = b.decode("utf-8-sig", errors="replace"), False
        v = self._version(b, st)
        return Document(t.replace("\r\n", "\n"), v, v.crlf, ok)

    def stat(self, path: str) -> Optional[Entry]:
        p = self._served(path)
        if p is None:
            return None
        try:
            st = os.stat(p)
        except OSError:
            return None
        return Entry(p.name, "dir" if p.is_dir() else "file", st.st_size, st.st_mtime_ns)

    def list(self, path: str = "") -> list[Entry]:
        p = self._served(path)
        out: list[Entry] = []
        if p is None:
            return out
        try:
            names = sorted(os.listdir(p))
        except OSError:
            return out
        for n in names:
            # a link, wherever it points, is not part of the root
            if (p / n).is_symlink() or not self._inside(p / n):
                continue
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

    def write(self, path: str, text: str, *, expected: Optional[Version], crlf: Optional[bool] = None) -> Version:
        """Writes whole and atomically (a temporary beside it, then a rename). `expected=None` means the file must not
        exist yet; otherwise its content must still be the one read. Line endings and BOM follow `expected` unless
        `crlf` says otherwise. A file that is not valid UTF-8 is refused (`NotUTF8`). Callers hold `lock()` around read
        and write."""
        p = self._p(path)
        if self._through_link(p):
            raise OutsideRoot(path)
        now = self._current(p)
        if (expected is None) != (now is None) or (now and expected and now.token != expected.token):
            raise Conflict(path)
        if now is not None:
            try:
                p.read_bytes().decode("utf-8")
            except UnicodeDecodeError:
                raise NotUTF8(path)
        use_crlf = crlf if crlf is not None else bool(expected and expected.crlf)
        text = text.replace("\r\n", "\n")
        if use_crlf:
            text = text.replace("\n", "\r\n")
        if expected and expected.bom and not text.startswith("\ufeff"):
            text = "\ufeff" + text
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
        p = self._p(path)
        if self._through_link(p):
            raise OutsideRoot(path)
        p.mkdir(parents=True, exist_ok=True)

    def move(self, src: str, dst: str) -> None:
        """Moves a file within the root; fails if the destination exists (archiving never overwrites)."""
        s, d = self._p(src), self._p(dst)
        if self._through_link(s) or self._through_link(d):
            raise OutsideRoot(src if self._through_link(s) else dst)
        d.parent.mkdir(parents=True, exist_ok=True)
        # link + unlink: the link fails if the destination exists, with no window between a check and a rename
        try:
            os.link(s, d)
        except FileExistsError:
            raise Conflict(dst)
        except OSError:
            # a filesystem without hard links (some synced folders): the check-then-rename fallback
            if d.exists() or d.is_symlink():
                raise Conflict(dst)
            os.rename(s, d)
            return
        os.unlink(s)

    @contextlib.contextmanager
    def lock(self, path: str) -> Iterator[bool]:
        """A lock between processes of this machine, the same file as cerrar.py's Cerrojo so both exclude each other.
        Yields whether the lock was taken: False where there is no flock (Windows), and the caller decides."""
        h = hashlib.sha1(str(self._p(path).resolve()).encode()).hexdigest()[:16]
        f = None
        try:
            import fcntl
            f = open(os.path.join(tempfile.gettempdir(), f"memoria-cerrar-{h}.lock"), "a+")
            fcntl.flock(f, fcntl.LOCK_EX)
        except Exception:
            if f:
                f.close()
            f = None
        try:
            yield f is not None
        finally:
            if f:
                try:
                    import fcntl
                    fcntl.flock(f, fcntl.LOCK_UN)
                except Exception:
                    pass
                f.close()
