"""A whole root -> `Root`.

For now it reads a folder on disk directly; task 2 of step 0 puts a storage adapter between this module and the files
(`folder` first, then Drive), and nothing above this module changes. What it never reads, whoever asks: restringido/,
fuentes/, and anything inside a restricted area or project (they keep only their row and index line). Access by account
is the caller's job once the server exists; the record says what is restricted, not who may open it.
"""
from __future__ import annotations

import pathlib
import re
from typing import Optional

from . import parse
from .records import Area, Project, Root, WorkshopFile

SKIP_AT_ROOT = {"base", "Claude outputs", "fuentes", "taller", "restringido"}


def _read(p: pathlib.Path) -> Optional[str]:
    try:
        return p.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    except (OSError, UnicodeDecodeError):
        return None


def _dirs(p: pathlib.Path) -> list[str]:
    try:
        return sorted(n for n in (x.name for x in p.iterdir() if x.is_dir()) if not n.startswith("."))
    except OSError:
        return []


def load_project(root: pathlib.Path, area: Area, slug: str) -> Project:
    index = area.index.get(slug)
    folder = root / area.slug / slug
    if (index and index.restricted) or area.restricted:
        return Project(area=area.slug, slug=slug, restricted=True, index=index)
    pr = parse.project_file(area.slug, slug, _read(folder / "proyecto.md") or "")
    pr.index = index
    pr.decisions = parse.decisions(_read(folder / "decisiones.md") or "")
    pr.sessions = parse.sessions(_read(folder / "sesiones.md") or "")
    d = folder / "entregables"
    try:
        files = sorted(x.name for x in d.iterdir() if x.is_file() and not x.name.startswith("."))
    except OSError:
        files = []
    pr.deliverables = [parse.deliverable(n, _read(d / n) if n.endswith(".md") else None, index) for n in files]
    t = folder / "taller"
    if t.is_dir():
        for f in sorted(t.rglob("*.md")):
            if any(part.startswith(".") for part in f.relative_to(t).parts):
                continue
            fm, body = parse.frontmatter(_read(f) or "")
            pr.workshop.append(WorkshopFile(path=str(f.relative_to(t)), title=parse.h1(body) or None,
                                            updated=fm.get("actualizado") or None))
    return pr


def load_root(path: str | pathlib.Path) -> Root:
    root = pathlib.Path(path)
    guia = _read(root / "guia.md") or ""
    first = ((_read(root / "metodo.md") or "").split("\n", 1) or [""])[0].strip()
    version, fingerprint = parse.method_line(first)
    reg = parse.people_registry(guia)
    title = parse.h1(guia)
    r = Root(name=root.name, organization=title.split("·", 1)[0].strip() if "·" in title else title,
             method_line=first, method_version=version, method_fingerprint=fingerprint,
             timezone=parse.timezone_of(guia), context_owner=parse.guia_line(guia, "Contexto común"),
             administrator=parse.guia_line(guia, r"Administra la carpeta(?: y pone o quita los accesos)?"),
             people=reg, area_rows=parse.area_rows(guia, reg),
             premises=parse.premises(_read(root / "base" / "premisas.md") or ""))
    r.warnings += reg.warnings
    rows = {row.slug: row for row in r.area_rows}
    # areas: the table's order, then any other folder with area.md
    slugs = [s for s in rows if (root / s).is_dir()]
    slugs += [s for s in _dirs(root) if s not in slugs and s not in SKIP_AT_ROOT and (root / s / "area.md").exists()]
    for s in slugs:
        row = rows.get(s)
        restricted = row.restricted if row else False
        if restricted:
            area = Area(slug=s, row=row, restricted=True)
        else:
            area = parse.area_file(s, _read(root / s / "area.md") or "")
            area.row = row
        projects = list(area.index)
        if not restricted:
            projects += [n for n in _dirs(root / s) if n not in projects and (root / s / n / "proyecto.md").exists()]
        area.projects = [load_project(root, area, p) for p in projects if (root / s / p).is_dir() or area.index.get(p)]
        r.areas.append(area)
    return r
