"""A whole root -> `Root`, read through a storage adapter.

What it never reads, whoever asks: restringido/, fuentes/, and anything inside a restricted area or project (they keep
only their row and index line). It fails closed, as the 1.25.1 scripts do: an area folder with no valid row in guia.md
and a project folder with no line in its area's index are loaded as restricted and not read. Access by account is the
caller's job; the record says what is restricted, not who may open it.
"""
from __future__ import annotations

import datetime
import os
import posixpath
import re
from typing import Iterable, Optional, Union

from . import parse, rules
from .language import Pack, pack
from .records import Area, Project, Root, WorkshopFile
from .storage import FolderStorage, Storage

OUTPUTS = "Claude outputs"   # Claude's own folder, not the method's: the same in every language

# What load_project can read of a project, by level (review of consultar, finding 6): a caller asks for what it serves,
# so a question about one area does not read every register and workshop file of the root.
PARTS = frozenset({"project", "decisions", "sessions", "session_bodies", "deliverables", "workshop"})
# Opt-in, not in the default: sessions merged with their archives change `SessionEntry.n` for 1.25.5's callers.
EVERY_PART = PARTS | {"session_archives"}
# What a reader outside a session may be served (convenciones, section 7): no session bodies, no workshop.
PUBLIC = frozenset({"project", "decisions", "sessions", "deliverables"})
REGISTERS = frozenset({"decisions"})   # enough for the challenge index across the root


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


def _register(st: Storage, base: str, names: list[str], live_name: str, register: str, year: int) -> tuple[str, int]:
    """The live register followed by this year's and last year's archives, and how many entries are live: the ids are
    counted over the merged text, so a day split by a rotation keeps the same ids (finding 5c)."""
    live = _text(st, _j(base, live_name))
    archives = [_text(st, _j(base, n)) for n in rules.archived_names(names, register, year)]
    return rules.with_archives(live, archives)


def _parts(parts: Iterable[str]) -> frozenset:
    if isinstance(parts, str):
        raise TypeError("parts is a set of names, not one string")
    out = frozenset(parts)
    if out - EVERY_PART:
        raise ValueError(f"unknown parts: {', '.join(sorted(out - EVERY_PART))}")
    return out


def current_year(timezone: str) -> int:
    """The year in the organization's time zone: a server in UTC must not move to the next year before it does."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.datetime.now(ZoneInfo(timezone)).year
    except Exception:
        return datetime.date.today().year


def load_project(st: Storage, area: Area, slug: str, lang: Pack, parts: Iterable[str] = PARTS,
                 year: Optional[int] = None) -> Project:
    """One project, reading only `parts` (see PARTS). Decisions include this year's and last year's archives; of older
    decision archives only what answers a decision is kept (`old_responses`). Sessions include their archives only with
    "session_archives". Session bodies come only with "session_bodies"; without it each entry keeps its heading and the
    first line of «Tema»."""
    parts = _parts(parts)
    index = area.index.get(slug)
    base = _j(area.slug, slug)
    if index is None or index.restricted or area.restricted:
        return Project(area=area.slug, slug=slug, restricted=True, index=index)
    if not parts:
        return Project(area=area.slug, slug=slug, index=index)
    year = year or datetime.date.today().year   # load_root passes the organization's year
    key = f"{area.slug}--{slug}"
    names = [e.name for e in st.list(base) if e.kind == "file"] if parts & {"decisions", "sessions"} else []
    if "project" in parts:
        pr = parse.project_file(area.slug, slug, _text(st, _j(base, lang.project_file)) or "", lang)
    else:
        pr = Project(area=area.slug, slug=slug)
    pr.index = index
    pr.loaded = parts
    if "decisions" in parts:
        stem = lang.decisions_file.rsplit(".", 1)[0]
        text, live = _register(st, base, names, lang.decisions_file, stem, year)
        pr.decisions = parse.decisions(text, live=live, lang=lang, here=key)
        recent = set(rules.archived_names(names, stem, year))
        for n in rules.archived_names(names, stem, 0):
            if n not in recent:
                pr.old_responses += [d.responds_to for d in parse.decisions(_text(st, _j(base, n)) or "", lang=lang, here=key)
                                     if d.responds_to and d.responds_to.id]
    if "sessions" in parts:
        if "session_archives" in parts:
            stem = lang.sessions_file.rsplit(".", 1)[0]
            text, live = _register(st, base, names, lang.sessions_file, stem, year)
        else:
            text, live = _text(st, _j(base, lang.sessions_file)) or "", None
        pr.sessions = parse.sessions(text, live=live, lang=lang, headers_only="session_bodies" not in parts)
    if "deliverables" in parts:
        d = _j(base, lang.deliverables)
        files = [e.name for e in st.list(d) if e.kind == "file" and not e.name.startswith(".")]
        pr.deliverables = [parse.deliverable(n, _text(st, _j(d, n)) if n.endswith(".md") else None, index, lang) for n in files]
    if "workshop" in parts:
        for rel in sorted(_md_files(st, _j(base, lang.workshop), lang)):
            fm, body = parse.frontmatter(_text(st, _j(base, lang.workshop, rel)) or "")
            pr.workshop.append(WorkshopFile(path=rel, title=parse.h1(body) or None, updated=fm.get(lang.key_updated) or None))
    return pr


def load_root(source: Union[Storage, str, os.PathLike], language: Optional[str] = None, *,
              projects: Union[bool, Iterable[str]] = True, parts: Iterable[str] = PARTS,
              year: Optional[int] = None) -> Root:
    """From a Storage, or a folder path (wrapped in FolderStorage), in the root's language (Spanish by default).

    By level: the guide, the premises and every open area's area.md are always read. `projects` says which projects are
    read, with `parts` (True: all; False: none; or keys "area/project" or "area--project"); the others keep only their
    index line (`loaded` empty). `year` is the current year for the archives (today's by default)."""
    st: Storage = source if isinstance(source, Storage) else FolderStorage(source)
    lang = pack(language)
    guia = _text(st, lang.guide) or ""
    first = ((_text(st, lang.method) or "").split("\n", 1) or [""])[0].strip()
    version, fingerprint = parse.method_line(first)
    reg = parse.people_registry(guia)
    row_warnings: list = []
    title = parse.h1(guia)
    r = Root(name=st.name, organization=title.split("·", 1)[0].strip() if "·" in title else title,
             method_line=first, method_version=version, method_fingerprint=fingerprint,
             language=lang.code, timezone=parse.timezone_of(guia),
             context_owner=parse.guia_line(guia, lang.context_owner_label),
             administrator=parse.guia_line(guia, lang.administrator_label),
             people=reg, area_rows=parse.area_rows(guia, reg, lang, warnings=row_warnings),
             premises=parse.premises(_text(st, _j(lang.base, lang.premises_file)) or ""))
    r.warnings += reg.warnings + row_warnings
    year = year or current_year(r.timezone)
    parts = _parts(parts)
    if isinstance(projects, str):
        projects = [projects]
    if projects is True or projects is False:
        want = lambda a, p: projects
    else:
        keys = {k.replace("--", "/").strip("/") for k in projects}
        want = lambda a, p: f"{a}/{p}" in keys
    rows = {row.slug: row for row in r.area_rows}
    top = set(_dirs(st, ""))
    slugs = [s for s in rows if s in top]
    slugs += [s for s in sorted(top) if s not in slugs and s not in _skip_at_root(lang) and _has(st, _j(s, lang.area_file))]
    for s in slugs:
        row = rows.get(s)
        restricted = row.restricted if row else True   # an area the table does not declare is not read
        if restricted:
            area = Area(slug=s, row=row, restricted=True)
        else:
            area = parse.area_file(s, _text(st, _j(s, lang.area_file)) or "", lang)
            area.row = row
        sub = set(_dirs(st, s)) if not restricted else set()
        names = list(area.index)
        names += [n for n in sorted(sub) if n not in names and _has(st, _j(s, n, lang.project_file))]
        area.projects = [load_project(st, area, p, lang, parts if want(s, p) else (), year)
                         for p in names if p in sub or p in area.index]
        r.areas.append(area)
    return r


def load_public(source: Union[Storage, str, os.PathLike], language: Optional[str] = None, *,
                projects: Union[bool, Iterable[str]] = True, registers_only: bool = False,
                year: Optional[int] = None) -> Root:
    """What a reader outside a session may be served, and nothing else (review of 1.25.6, finding 7): `PUBLIC` parts
    (or only the decisions, with `registers_only`), never session bodies or the workshop, and every reference in the
    decisions and the sessions' «Escribió» and «Publicó» cut at the edge of a restricted zone (views.public_reference).
    The server reads through this, not through load_root."""
    from . import views
    lang = pack(language)
    r = load_root(source, language, projects=projects, parts=REGISTERS if registers_only else PUBLIC, year=year)
    for area in r.areas:
        for pr in area.projects:
            here = pr.key
            for d in pr.decisions:
                d.affects = views.public_reference(d.affects, r, lang, here)
                for ref in (d.challenges, d.responds_to, d.replaces):
                    if ref is not None:
                        ref.text = views.public_reference(ref.text, r, lang, here)
            for e in pr.sessions:
                e.wrote = [views.public_reference(x, r, lang, here) for x in e.wrote]
                e.published = [views.public_reference(x, r, lang, here) for x in e.published]
    return r
