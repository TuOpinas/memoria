"""The development kit (1.27): how the plugin recognises a project that builds software. Pure functions: text in, data
out; no I/O, no network, no clock.

A project is a development project when its proyecto.md has a «## Desarrollo» section
(tecnologia/metodologia-desarrollo#2026-11-18-4). The section points to each piece of the kit (the configuration, the
design, the plan and the follow-up) and names the people of each role. This module reads the section and says which
pieces are missing; it reads nothing else. The design and the plan are read by the model, not by code, and the status of
each piece is applied by the model from the plan's rule (tecnologia/metodologia-desarrollo#2026-11-19-2).

The keys of the method's files are Spanish and are compared as the decisions say: NFC, without accents or case. The code
names things in English; `seccion_desarrollo` and `piezas_faltantes` are aliases of the same functions, at the end.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Callable

__all__ = [
    "SECTION", "PATH_KEYS", "ROLE_KEYS", "ALL_KEYS", "TO_BUILD", "DevPerson", "DevSection", "Missing",
    "key", "development_section", "missing_pieces", "seccion_desarrollo", "piezas_faltantes",
]

SECTION = "Desarrollo"
TO_BUILD = "por crear"

# the section's keys, as written in the template (plantilla-seccion-desarrollo.md), in their order
REPOSITORIES = "Repositorios"
PLATFORM = "Configuración de plataforma"
REPOSITORY_CONFIG = "Configuración de repositorios"
DESIGN = "Diseño"
PLAN = "Plan"
FOLLOW_UP = "Seguimiento"
STEP_TO_PROD = "Paso a Prod"
PATH_KEYS = (PLATFORM, REPOSITORY_CONFIG, DESIGN, PLAN, FOLLOW_UP)
ROLE_KEYS = ("Acepta", "Audita", "Construye", "Administra")
ALL_KEYS = (REPOSITORIES,) + PATH_KEYS + (STEP_TO_PROD,) + ROLE_KEYS

SEPARATOR = re.compile(r"\s+·\s+")          # « · » between values; a bare «·» inside a name is not a separator
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
EMAIL = re.compile(r"^[\w.+'-]+@[\w-]+(?:\.[\w-]+)+$")
GITHUB_USER = re.compile(r"^@?([A-Za-z0-9](?:[A-Za-z0-9-]{0,38}))$")


# ── comparing ──────────────────────────────────────────────────────────────────────────────────────────────────────

def key(text: str) -> str:
    """How a key, a heading or a column title compares: NFC or NFD alike, without accents, case, markup or punctuation."""
    t = unicodedata.normalize("NFD", text or "")
    t = "".join(c for c in t if unicodedata.category(c) != "Mn").replace(" ", " ").lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", t)).strip()


def _nfc(text: str) -> str:
    return unicodedata.normalize("NFC", (text or "").replace("\r\n", "\n").replace("\r", "\n")).replace(" ", " ")


def _clean(value: str) -> str:
    """A value as written, without the Markdown around it: backticks, bold, a link's brackets (its target is kept)."""
    v = value.strip()
    v = re.sub(r"\[([^\]]*)\]\(([^)]*)\)", lambda m: m.group(2) or m.group(1), v)
    return v.replace("`", "").replace("**", "").strip()


def _is_to_build(value: str) -> bool:
    return key(value) == key(TO_BUILD)


def _sections(body: str) -> dict:
    """Every «## » section of a text by its key, cut at the next «## » (the same cut abrir.py, cerrar.py and
    verificar.sh make). The first of two with the same key wins. Fenced code blocks are skipped, so a «## » inside an
    example does not open a section."""
    out: dict = {}
    name, lines, fence = None, [], False
    for line in _nfc(body).split("\n"):
        if re.match(r"^\s*(```|~~~)", line):
            fence = not fence
        if not fence and line.startswith("## "):
            if name is not None and key(name) not in out:
                out[key(name)] = (name, "\n".join(lines))
            name, lines = line[3:].strip(), []
        elif name is not None:
            lines.append(line)
    if name is not None and key(name) not in out:
        out[key(name)] = (name, "\n".join(lines))
    return out


# ── the «Desarrollo» section ───────────────────────────────────────────────────────────────────────────────────────

@dataclass
class DevPerson:
    """One person of a role: «Nombre Apellido (correo, @usuario)»; the GitHub user is left out without an account."""
    name: str
    email: str = ""
    user: str = ""                              # GitHub login, without «@»
    raw: str = ""


@dataclass
class DevSection:
    """The «## Desarrollo» section of a proyecto.md. `found` False means the project is not a development project."""
    found: bool = False
    repositories: list = field(default_factory=list)       # «organización/repositorio»
    paths: dict = field(default_factory=dict)              # PATH_KEYS -> path from the root, or TO_BUILD
    step_to_prod: str = ""                                 # «Paso a Prod», as written
    roles: dict = field(default_factory=dict)              # ROLE_KEYS -> [DevPerson]
    present: list = field(default_factory=list)            # the keys that have a line, in ALL_KEYS spelling
    to_build: list = field(default_factory=list)           # the keys whose value is «por crear»
    unknown: list = field(default_factory=list)            # lines of the section it does not recognise
    warnings: list = field(default_factory=list)


_BY_KEY = {key(k): k for k in ALL_KEYS}


def _person(text: str) -> tuple[DevPerson, list]:
    t = text.strip()
    warnings = []
    m = re.match(r"^(.*?)\s*\(([^()]*)\)\s*$", t)
    name, inside = (m.group(1), m.group(2)) if m else (t, "")
    p = DevPerson(name=_clean(name), raw=t)
    for item in (x.strip() for x in inside.split(",")):
        if not item:
            continue
        if EMAIL.match(item):
            if p.email:
                warnings.append(f"«{t}»: dos correos; se toma el primero")
            else:
                p.email = item.lower()
        elif item.startswith("@") and GITHUB_USER.match(item):
            p.user = GITHUB_USER.match(item).group(1)
        else:
            warnings.append(f"«{t}»: «{item}» no es un correo ni un usuario de GitHub (@usuario)")
    if not p.name:
        warnings.append(f"«{t}»: falta el nombre")
    return p, warnings


def development_section(project_text: str) -> DevSection:
    """The «## Desarrollo» section of a proyecto.md, split in repositories, paths, «Paso a Prod» and the roles with
    their people. Keys compared without accents or case (NFC or NFD alike); people separated by « · » and each one's
    data by commas. What it does not recognise comes back in `unknown`."""
    sec = _sections(project_text).get(key(SECTION))
    out = DevSection()
    if sec is None:
        return out
    out.found = True
    for raw in sec[1].split("\n"):
        line = raw.strip()
        if not line or re.match(r"^<!--.*-->$", line):
            continue
        m = re.match(r"^[-*]?\s*\**\s*([^:*]+?)\s*\**\s*:\s*\**\s*(.*)$", line)
        k = _BY_KEY.get(key(m.group(1))) if m else None
        if k is None:
            out.unknown.append(line)
            continue
        if k in out.present:
            out.warnings.append(f"«{k}» aparece dos veces; vale la primera")
            continue
        out.present.append(k)
        value = _clean(m.group(2))
        if _is_to_build(value):
            out.to_build.append(k)
            if k in PATH_KEYS:
                out.paths[k] = TO_BUILD
            elif k in ROLE_KEYS:
                out.roles[k] = []
            continue
        if k == REPOSITORIES:
            for r in (x.strip() for x in SEPARATOR.split(value) if x.strip()):
                # pegado como enlace de GitHub: se queda con organización/repositorio
                r = re.sub(r"^(?:https?://)?(?:www\.)?github\.com/", "", r).rstrip("/")
                r = r[:-4] if r.endswith(".git") else r
                if REPO.match(r):
                    if r.lower() not in (x.lower() for x in out.repositories):
                        out.repositories.append(r)
                else:
                    out.warnings.append(f"«{r}» en Repositorios no es organización/repositorio")
        elif k in PATH_KEYS:
            out.paths[k] = value.strip().lstrip("/")
        elif k == STEP_TO_PROD:
            out.step_to_prod = value
        else:
            people = []
            for t in (x for x in SEPARATOR.split(value) if x.strip()):
                p, w = _person(t)
                people.append(p)
                out.warnings += w
            out.roles[k] = people
    return out


@dataclass
class Missing:
    """A piece of the kit that is missing: its line, or the file its line points to."""
    key: str                                    # in ALL_KEYS spelling
    reason: str                                 # "sin línea" | "por crear" | "no existe" | "vacía"
    path: str = ""


def missing_pieces(section: DevSection, exists: Callable[[str], bool]) -> list:
    """The lines of the section that are missing or point to a file that is not there, with `exists(path)` saying
    whether a path from the root exists. «Seguimiento: por crear» does not count: the plugin creates it at the first
    follow-up. Empty for a project without the section."""
    if not section.found:
        return []
    out = []
    for k in ALL_KEYS:
        if k not in section.present:
            out.append(Missing(k, "sin línea"))
        elif k in section.to_build:
            if k != FOLLOW_UP:
                out.append(Missing(k, "por crear"))
        elif k == REPOSITORIES and not section.repositories:
            out.append(Missing(k, "vacía"))
        elif k in ROLE_KEYS and not section.roles.get(k):
            out.append(Missing(k, "vacía"))
        elif k == STEP_TO_PROD and not section.step_to_prod:
            out.append(Missing(k, "vacía"))
        elif k in PATH_KEYS:
            v = section.paths.get(k, "")
            if not v:
                out.append(Missing(k, "vacía"))
            elif not exists(v):
                out.append(Missing(k, "no existe", v))
    return out


# the Spanish names the plugin's scripts use
seccion_desarrollo = development_section
piezas_faltantes = missing_pieces
