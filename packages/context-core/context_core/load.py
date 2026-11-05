"""A whole root -> `Root`, read through a storage adapter.

What it never reads, whoever asks: restringido/, fuentes/, and anything inside a restricted area or project (they keep
only their row and index line). Access by account is the caller's job; the record says what is restricted, not who
may open it.
"""
from __future__ import annotations

import os
import posixpath
from typing import Optional, Union

from . import parse
from .records import Area, Project, Root, WorkshopFile
from .storage import FolderStorage, Storage

SKIP_AT_ROOT = {"base", "Claude outputs", "fuentes", "taller", "restringido"}
NEVER_READ = {"restringido", "fuentes"}


def _j(*parts: str) -> str:
    return posixpath.join(*[p for p in parts if p])


def _text(st: Storage, path: str) -> Optional[str]:
    doc = st.read(path)
    return doc.text if doc else None


def _dirs(st: Storage, path: str) -> list[str]:
    return [e.name for e in st.list(path) if e.kind == "dir" and not e.name.startswith(".")]


def _has(st: Storage, path: str) -> bool:
    return st.stat(path) is not None


def _md_files(st: Storage, path: str, prefix: str = "") -> list[str]:
    out = []
    for e in st.list(path):
        if e.name.startswith(".") or e.name in NEVER_READ:
            continue
        if e.kind == "dir":
            out += _md_files(st, _j(path, e.name), _j(prefix, e.name))
        elif e.name.endswith(".md"):
            out.append(_j(prefix, e.name))
    return out


def load_project(st: Storage, area: Area, slug: str) -> Project:
    index = area.index.get(slug)
    base = _j(area.slug, slug)
    if (index and index.restricted) or area.restricted:
        return Project(area=area.slug, slug=slug, restricted=True, index=index)
    pr = parse.project_file(area.slug, slug, _text(st, _j(base, "proyecto.md")) or "")
    pr.index = index
    pr.decisions = parse.decisions(_text(st, _j(base, "decisiones.md")) or "")
    pr.sessions = parse.sessions(_text(st, _j(base, "sesiones.md")) or "")
    d = _j(base, "entregables")
    files = [e.name for e in st.list(d) if e.kind == "file" and not e.name.startswith(".")]
    pr.deliverables = [parse.deliverable(n, _text(st, _j(d, n)) if n.endswith(".md") else None, index) for n in files]
    for rel in sorted(_md_files(st, _j(base, "taller"))):
        fm, body = parse.frontmatter(_text(st, _j(base, "taller", rel)) or "")
        pr.workshop.append(WorkshopFile(path=rel, title=parse.h1(body) or None, updated=fm.get("actualizado") or None))
    return pr


def load_root(source: Union[Storage, str, os.PathLike]) -> Root:
    """From a Storage, or a folder path (wrapped in FolderStorage)."""
    st: Storage = source if isinstance(source, Storage) else FolderStorage(source)
    guia = _text(st, "guia.md") or ""
    first = ((_text(st, "metodo.md") or "").split("\n", 1) or [""])[0].strip()
    version, fingerprint = parse.method_line(first)
    reg = parse.people_registry(guia)
    title = parse.h1(guia)
    r = Root(name=st.name, organization=title.split("·", 1)[0].strip() if "·" in title else title,
             method_line=first, method_version=version, method_fingerprint=fingerprint,
             timezone=parse.timezone_of(guia), context_owner=parse.guia_line(guia, "Contexto común"),
             administrator=parse.guia_line(guia, r"Administra la carpeta(?: y pone o quita los accesos)?"),
             people=reg, area_rows=parse.area_rows(guia, reg),
             premises=parse.premises(_text(st, "base/premisas.md") or ""))
    r.warnings += reg.warnings
    rows = {row.slug: row for row in r.area_rows}
    top = set(_dirs(st, ""))
    slugs = [s for s in rows if s in top]
    slugs += [s for s in sorted(top) if s not in slugs and s not in SKIP_AT_ROOT and _has(st, _j(s, "area.md"))]
    for s in slugs:
        row = rows.get(s)
        restricted = row.restricted if row else False
        if restricted:
            area = Area(slug=s, row=row, restricted=True)
        else:
            area = parse.area_file(s, _text(st, _j(s, "area.md")) or "")
            area.row = row
        sub = set(_dirs(st, s)) if not restricted else set()
        projects = list(area.index)
        projects += [n for n in sorted(sub) if n not in projects and _has(st, _j(s, n, "proyecto.md"))]
        area.projects = [load_project(st, area, p) for p in projects if p in sub or p in area.index]
        r.areas.append(area)
    return r
