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
from .language import Pack, pack
from .records import Area, Project, Root, WorkshopFile
from .storage import FolderStorage, Storage

OUTPUTS = "Claude outputs"   # Claude's own folder, not the method's: the same in every language


def _skip_at_root(lang: Pack) -> set:
    return {lang.base, OUTPUTS, lang.sources, lang.workshop, lang.restricted}


def _never_read(lang: Pack) -> set:
    return {lang.restricted, lang.sources}


def _j(*parts: str) -> str:
    return posixpath.join(*[p for p in parts if p])


def _text(st: Storage, path: str) -> Optional[str]:
    doc = st.read(path)
    return doc.text if doc else None


def _dirs(st: Storage, path: str) -> list[str]:
    return [e.name for e in st.list(path) if e.kind == "dir" and not e.name.startswith(".")]


def _has(st: Storage, path: str) -> bool:
    return st.stat(path) is not None


def _md_files(st: Storage, path: str, lang: Pack, prefix: str = "") -> list[str]:
    out = []
    for e in st.list(path):
        if e.name.startswith(".") or e.name in _never_read(lang):
            continue
        if e.kind == "dir":
            out += _md_files(st, _j(path, e.name), lang, _j(prefix, e.name))
        elif e.name.endswith(".md"):
            out.append(_j(prefix, e.name))
    return out


def load_project(st: Storage, area: Area, slug: str, lang: Pack) -> Project:
    index = area.index.get(slug)
    base = _j(area.slug, slug)
    if (index and index.restricted) or area.restricted:
        return Project(area=area.slug, slug=slug, restricted=True, index=index)
    pr = parse.project_file(area.slug, slug, _text(st, _j(base, lang.project_file)) or "", lang)
    pr.index = index
    pr.decisions = parse.decisions(_text(st, _j(base, lang.decisions_file)) or "", lang=lang)
    pr.sessions = parse.sessions(_text(st, _j(base, lang.sessions_file)) or "", lang=lang)
    d = _j(base, lang.deliverables)
    files = [e.name for e in st.list(d) if e.kind == "file" and not e.name.startswith(".")]
    pr.deliverables = [parse.deliverable(n, _text(st, _j(d, n)) if n.endswith(".md") else None, index, lang) for n in files]
    for rel in sorted(_md_files(st, _j(base, lang.workshop), lang)):
        fm, body = parse.frontmatter(_text(st, _j(base, lang.workshop, rel)) or "")
        pr.workshop.append(WorkshopFile(path=rel, title=parse.h1(body) or None, updated=fm.get(lang.key_updated) or None))
    return pr


def load_root(source: Union[Storage, str, os.PathLike], language: Optional[str] = None) -> Root:
    """From a Storage, or a folder path (wrapped in FolderStorage), in the root's language (Spanish by default)."""
    st: Storage = source if isinstance(source, Storage) else FolderStorage(source)
    lang = pack(language)
    guia = _text(st, lang.guide) or ""
    first = ((_text(st, lang.method) or "").split("\n", 1) or [""])[0].strip()
    version, fingerprint = parse.method_line(first)
    reg = parse.people_registry(guia)
    title = parse.h1(guia)
    r = Root(name=st.name, organization=title.split("·", 1)[0].strip() if "·" in title else title,
             method_line=first, method_version=version, method_fingerprint=fingerprint,
             language=lang.code, timezone=parse.timezone_of(guia),
             context_owner=parse.guia_line(guia, lang.context_owner_label),
             administrator=parse.guia_line(guia, lang.administrator_label),
             people=reg, area_rows=parse.area_rows(guia, reg, lang),
             premises=parse.premises(_text(st, _j(lang.base, lang.premises_file)) or ""))
    r.warnings += reg.warnings
    rows = {row.slug: row for row in r.area_rows}
    top = set(_dirs(st, ""))
    slugs = [s for s in rows if s in top]
    slugs += [s for s in sorted(top) if s not in slugs and s not in _skip_at_root(lang) and _has(st, _j(s, lang.area_file))]
    for s in slugs:
        row = rows.get(s)
        restricted = row.restricted if row else False
        if restricted:
            area = Area(slug=s, row=row, restricted=True)
        else:
            area = parse.area_file(s, _text(st, _j(s, lang.area_file)) or "", lang)
            area.row = row
        sub = set(_dirs(st, s)) if not restricted else set()
        projects = list(area.index)
        projects += [n for n in sorted(sub) if n not in projects and _has(st, _j(s, n, lang.project_file))]
        area.projects = [load_project(st, area, p, lang) for p in projects if p in sub or p in area.index]
        r.areas.append(area)
    return r
