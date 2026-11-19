"""The development kit (1.27): how a project that builds software is read. Pure functions: text in, data out; no I/O,
no network, no clock.

A project is a development project when its proyecto.md has a «## Desarrollo» section
(tecnologia/metodologia-desarrollo#2026-11-18-4). The section points to each piece of the kit (the two configurations,
the design, the plan and the follow-up) and names the people of each role. The design and the plan are two living
documents whose fixed tables this module reads (#2026-11-18-10); the configurations are seven lines each with a dated
state (#2026-11-18-11). A piece's status comes from its pull requests into the main branch by one rule (#2026-11-18-10
and -12), and this module
applies it to pull requests the caller already read: it never calls GitHub.

The keys of the method's files are Spanish and are compared as the decisions say: NFC, without accents or case. The code
names things in English; the Spanish names the specification uses (`seccion_desarrollo`, `piezas_faltantes`,
`leer_diseno`, `leer_plan`, `leer_configuracion`, `estado_piezas`) are aliases of the same functions, at the end.
"""
from __future__ import annotations

import dataclasses
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Callable, Iterable, Mapping, Optional

__all__ = [
    "SECTION", "PATH_KEYS", "ROLE_KEYS", "TO_BUILD", "DevPerson", "DevSection", "Missing",
    "Relation", "Entity", "Design", "Phase", "Piece", "Plan", "ConfigRow", "ApprovedChange", "Configuration",
    "PullRequest", "PieceStatus", "PieceReport",
    "key", "development_section", "missing_pieces", "read_design", "read_plan", "read_configuration", "piece_status",
    "as_dict",
    "seccion_desarrollo", "piezas_faltantes", "leer_diseno", "leer_plan", "leer_configuracion", "estado_piezas",
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
GITHUB_USER = re.compile(r"^@?([A-Za-z0-9](?:[A-Za-z0-9._-]{0,38}))$")   # «_» for Enterprise Managed Users
DATE = re.compile(r"\b(20\d\d-\d\d-\d\d)\b")


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


def _tables(block: str) -> list:
    """Every Markdown table in a block, as (header, rows). Cells keep their text; a row shorter than the header is
    padded, one longer is cut (a «|» inside a cell is the writer's problem, and the method's tables forbid it)."""
    out, header, rows = [], None, []
    for line in block.split("\n") + [""]:
        s = line.strip()
        if not s.startswith("|"):
            if header is not None:
                out.append((header, rows))
            header, rows = None, []
            continue
        if re.match(r"^\|[\s:|-]+\|?\s*$", s):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if header is None:
            header = cells
        else:
            rows.append((cells + [""] * len(header))[:len(header)])
    return out


def _table(block: str) -> tuple:
    """(header, rows) of the first table in a block; ([], []) without one."""
    t = _tables(block)
    return t[0] if t else ([], [])


def _placeholder(cells: Iterable[str]) -> bool:
    """A row the template left as it was: every non-empty cell is «[…]»."""
    full = [c for c in cells if c.strip()]
    return not full or all(re.match(r"^\[[^\]]*\]$", c.strip()) for c in full)


def _columns(header: list, expected: Iterable[str]) -> tuple[dict, list]:
    """Where each expected column is, by its key, and the expected ones that are not there."""
    at = {}
    for i, h in enumerate(header):
        at.setdefault(key(h), i)
    found, missing = {}, []
    for e in expected:
        if key(e) in at:
            found[e] = at[key(e)]
        else:
            missing.append(e)
    return found, missing


def _ident(cell: str) -> tuple[str, str]:
    """«P01 · name» -> ("P01", "name"); a cell with no « · » is all identifier."""
    c = _clean(cell)
    parts = SEPARATOR.split(c, maxsplit=1)
    return parts[0].strip(), (parts[1].strip() if len(parts) > 1 else "")


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
    near_miss: bool = False                                # a «## Desarrollo» that looks like the kit but is not recognised
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


_LINE = re.compile(r"^[-*]?\s*\**\s*([^:*]+?)\s*\**\s*:\s*\**\s*(.*)$")


def _line_key(line: str) -> Optional[str]:
    """The kit's key a line of the section starts with, in ALL_KEYS spelling, or None."""
    m = _LINE.match((line or "").strip())
    return _BY_KEY.get(key(m.group(1))) if m else None


def development_section(project_text: str) -> DevSection:
    """The «## Desarrollo» section of a proyecto.md, split in repositories, paths, «Paso a Prod» and the roles with
    their people. Keys compared without accents or case (NFC or NFD alike); people separated by « · » and each one's
    data by commas. What it does not recognise comes back in `unknown`."""
    sec = _sections(project_text).get(key(SECTION))
    out = DevSection()
    if sec is None:
        return out
    # «Desarrollo» is a common heading in Spanish: the section marks a development project only with «Repositorios:» or
    # two keys of the kit, comments aside (review of 1.27.0, finding 20, and its fixes, finding 10). One that looks like
    # the kit and is not recognised is said in `near_miss`, so a misspelt section is not silently invisible.
    claves = {k for k in (_line_key(l) for l in sec[1].split("\n") if not l.strip().startswith("<!--")) if k}
    if REPOSITORIES not in claves and len(claves) < 2:
        # a near miss: a «Clave:» line that is no key of the kit but starts like one («Repositorio:», «Construyen:»)
        prefijos = {key(k)[:6] for k in ALL_KEYS}
        out.near_miss = any(m and not _line_key(l) and key(m.group(1))[:6] in prefijos
                            for l in sec[1].split("\n") for m in [_LINE.match(l.strip())])
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


# ── the design ─────────────────────────────────────────────────────────────────────────────────────────────────────

DESIGN_TABLES = {
    "Reglas": ("Regla", "Excepción"),
    "Componentes": ("Componente", "Qué hace", "Dónde vive"),
    "Datos": ("Entidad", "Qué es", "Se relaciona con"),
    "Conceptos": ("Concepto", "Significa", "No es"),
    "Infraestructura": ("Pieza", "Para qué", "Dónde"),
}
DESIGN_TEXT = ("Objetivo", "Prototipo")
CARDINALITIES = {"1:n": "1:N", "1:1": "1:1", "n:m": "N:M", "n:n": "N:M", "m:n": "N:M"}


@dataclass
class Relation:
    target: str
    cardinality: str                            # "1:N" (this entity is the «one» side), "1:1", "N:M"


@dataclass
class Entity:
    name: str                                   # its name in the code
    what: str = ""
    relations: list = field(default_factory=list)


@dataclass
class Design:
    objective: str = ""
    prototype: str = ""
    rules: list = field(default_factory=list)          # [{"regla", "excepcion"}]
    components: list = field(default_factory=list)     # [{"componente", "que_hace", "donde_vive"}]
    entities: list = field(default_factory=list)       # [Entity]
    concepts: list = field(default_factory=list)       # [{"concepto", "significa", "no_es": [..]}]
    infrastructure: list = field(default_factory=list) # [{"pieza", "para_que", "donde"}]
    missing: list = field(default_factory=list)        # «sección Datos», «columna Dónde vive en Componentes»
    warnings: list = field(default_factory=list)


def _field_name(column: str) -> str:
    return key(column).replace(" ", "_")


def _relations(cell: str, entity: str, warnings: list) -> list:
    out = []
    for part in (x.strip() for x in _clean(cell).split(",") if x.strip()):
        if part in ("-", "—", "–") or _placeholder([part]):
            continue
        m = re.match(r"^(.+?)\s*\(\s*([0-9NnMm]\s*:\s*[0-9NnMm])\s*\)$", part)
        if not m:
            warnings.append(f"Datos, {entity}: «{part}» no lleva su cardinalidad entre paréntesis, como «otra (1:N)»")
            continue
        card = CARDINALITIES.get(re.sub(r"\s", "", m.group(2)).lower())
        if card is None:
            warnings.append(f"Datos, {entity}: «{m.group(2)}» no es 1:N, 1:1 ni N:M (una N:1 se escribe en la otra entidad)")
            continue
        out.append(Relation(target=_clean(m.group(1)), cardinality=card))
    return out


def read_design(text: str) -> Design:
    """The design's tables by their section and column titles, with the relations split («otra (1:N)»), and the
    expected sections or columns it did not find."""
    secs = _sections(text)
    d = Design()
    d.objective = secs.get(key("Objetivo"), ("", ""))[1].strip()
    d.prototype = secs.get(key("Prototipo"), ("", ""))[1].strip()
    for name in DESIGN_TEXT:
        if key(name) not in secs:
            d.missing.append(f"sección {name}")
    for name, cols in DESIGN_TABLES.items():
        if key(name) not in secs:
            d.missing.append(f"sección {name}")
            continue
        header, rows = _table(secs[key(name)][1])
        if not header:
            d.missing.append(f"tabla de {name}")
            continue
        at, missing = _columns(header, cols)
        d.missing += [f"columna {c} en {name}" for c in missing]
        if cols[0] in missing:
            continue
        cell = lambda row, c: row[at[c]].strip() if c in at else ""
        for row in rows:
            if _placeholder(row):
                continue
            if name == "Datos":
                ent = _clean(cell(row, "Entidad"))
                if not ent:
                    continue
                d.entities.append(Entity(name=ent, what=cell(row, "Qué es"),
                                         relations=_relations(cell(row, "Se relaciona con"), ent, d.warnings)))
            else:
                item = {_field_name(c): (_clean(cell(row, c)) if c in (cols[0], "Dónde vive") else cell(row, c)) for c in cols}
                if not item[_field_name(cols[0])]:
                    continue
                if name == "Conceptos":
                    item["no_es"] = [x.strip() for x in _clean(item["no_es"]).split(",")
                                     if x.strip() and not _placeholder([x])]
                {"Reglas": d.rules, "Componentes": d.components, "Conceptos": d.concepts,
                 "Infraestructura": d.infrastructure}[name].append(item)
    names = {}
    for e in d.entities:
        if key(e.name) in names:
            d.warnings.append(f"Datos: la entidad «{e.name}» está dos veces")
        names.setdefault(key(e.name), e.name)
    for e in d.entities:
        for r in e.relations:
            if key(r.target) not in names:
                d.warnings.append(f"Datos, {e.name}: se relaciona con «{r.target}», que no es una entidad de la tabla")
    return d


# ── the plan ───────────────────────────────────────────────────────────────────────────────────────────────────────

PHASE_COLUMNS = ("Fase", "Qué podrá hacer quién", "Versión", "Listo cuando", "Estado")
PIECE_COLUMNS = ("Pieza", "Fase", "Qué entrega", "Hecha cuando")
PHASE_STATES = ("cerrada", "en curso", "pendiente")


@dataclass
class Phase:
    id: str
    name: str = ""
    who_can: str = ""
    version: str = ""
    done_when: str = ""
    state: str = ""                             # one of PHASE_STATES, or "" when it is not one


@dataclass
class Piece:
    id: str
    name: str = ""
    phase: str = ""                             # the phase's id
    delivers: str = ""
    done_when: str = ""


@dataclass
class Plan:
    phases: list = field(default_factory=list)
    pieces: list = field(default_factory=list)
    missing: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def piece(self, ident: str) -> Optional[Piece]:
        for p in self.pieces:
            if p.id.casefold() == (ident or "").casefold():
                return p
        return None


def read_plan(text: str) -> Plan:
    """The plan's two tables (Fases, Piezas) by their section and column titles, and the expected sections or columns
    it did not find. Warns on a repeated piece, a piece in a phase that is not in the table, a state that is not one of
    the three and more than one phase in progress."""
    secs = _sections(text)
    pl = Plan()
    for name, cols in (("Fases", PHASE_COLUMNS), ("Piezas", PIECE_COLUMNS)):
        if key(name) not in secs:
            pl.missing.append(f"sección {name}")
            continue
        header, rows = _table(secs[key(name)][1])
        if not header:
            pl.missing.append(f"tabla de {name}")
            continue
        at, missing = _columns(header, cols)
        pl.missing += [f"columna {c} en {name}" for c in missing]
        if cols[0] in missing:
            continue
        cell = lambda row, c: row[at[c]].strip() if c in at else ""
        for row in rows:
            if _placeholder(row):
                continue
            ident, label = _ident(cell(row, cols[0]))
            if not ident or _placeholder([ident]):
                continue
            if name == "Fases":
                state = key(cell(row, "Estado"))
                st = next((s for s in PHASE_STATES if key(s) == state), "")
                if cell(row, "Estado") and not st:
                    pl.warnings.append(f"Fases, {ident}: «{cell(row, 'Estado')}» no es cerrada, en curso ni pendiente")
                pl.phases.append(Phase(id=ident, name=label, who_can=cell(row, "Qué podrá hacer quién"),
                                       version=_clean(cell(row, "Versión")), done_when=cell(row, "Listo cuando"), state=st))
            else:
                if pl.piece(ident):
                    pl.warnings.append(f"Piezas: «{ident}» está dos veces; un identificador no se reutiliza")
                    continue
                pl.pieces.append(Piece(id=ident, name=label, phase=_ident(cell(row, "Fase"))[0],
                                       delivers=cell(row, "Qué entrega"), done_when=cell(row, "Hecha cuando")))
    if sum(1 for f in pl.phases if f.state == "en curso") > 1:
        pl.warnings.append("Fases: hay más de una en curso")
    phases = {f.id.casefold() for f in pl.phases}
    for p in pl.pieces:
        if pl.phases and p.phase and p.phase.casefold() not in phases:
            pl.warnings.append(f"Piezas, {p.id}: la fase «{p.phase}» no está en Fases")
    return pl


# ── the two configurations ─────────────────────────────────────────────────────────────────────────────────────────

STATES = ("cumple", "no cumple", "no aplica", "excepción")


@dataclass
class ConfigRow:
    id: str                                     # PL1…PL7, R1…R7
    what: str = ""
    states: dict = field(default_factory=dict)  # column ("Estado", or a repository) -> {"estado", "fecha", "texto"}


@dataclass
class ApprovedChange:
    date: str
    what: str
    approved_by: str


@dataclass
class Configuration:
    kind: str = ""                              # "plataforma" | "repositorios" | ""
    columns: list = field(default_factory=list) # the state columns: ["Estado"] or the repositories
    rows: list = field(default_factory=list)
    changes: list = field(default_factory=list) # «Cambios aprobados», newest first as written
    latest: str = ""                            # the most recent date of any state
    oldest: str = ""                            # the oldest date of a row that is checked by date («cumple», «no cumple»)
    unchecked: list = field(default_factory=list)  # «PL3» or «R2 org/repo»: cells with no state yet
    missing: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


def _state(cell: str) -> Optional[dict]:
    c = _clean(cell)
    if not c:
        return None
    m = DATE.search(c)
    word = key(SEPARATOR.split(c, maxsplit=1)[0] if "·" in c else DATE.sub("", c))
    st = next((s for s in STATES if key(s) == word), "")
    return {"estado": st, "fecha": m.group(1) if m else "", "texto": c}


def read_configuration(text: str) -> Configuration:
    """The rows PL and R of a configuration with each state and its date («cumple · AAAA-MM-DD»), and the table
    «Cambios aprobados». The platform's state column is «Estado»; a repositories configuration has one column per
    repository after «Cómo se comprueba»."""
    cf = Configuration()
    header, rows = None, []
    body = _nfc(text)
    secs = _sections(body)
    # the main table is the first one whose first column is «#», outside «Cambios aprobados»
    changes_block = secs.get(key("Cambios aprobados"), ("", ""))[1]
    # cut by position, not by text: an empty section's block is «\n», and replacing it removed every line break
    # (review of 1.27.0, finding 26)
    main = body
    for mm in re.finditer(r"^## (.+)$", body, re.M):
        if key(mm.group(1)) == key("Cambios aprobados"):
            nxt = re.search(r"^## ", body[mm.end():], re.M)
            main = body[:mm.start()] + (body[mm.end() + nxt.start():] if nxt else "")
            break
    for h, r in _tables(main):
        if key(h[0]) == "":
            header, rows = h, r
            break
    if header is None:
        cf.missing.append("tabla con la columna #")
    else:
        at, missing = _columns(header, ("Qué se cumple", "Cómo se comprueba"))
        cf.missing += [f"columna {c}" for c in missing]
        if "Estado" in header or key("Estado") in (key(x) for x in header):
            cf.kind, state_cols = "plataforma", [i for i, h in enumerate(header) if key(h) == key("Estado")][:1]
        else:
            cf.kind = "repositorios"
            after = at.get("Cómo se comprueba", 1)
            state_cols = list(range(after + 1, len(header)))
            if not state_cols:
                cf.missing.append("columna de un repositorio")
        cf.columns = [_clean(header[i]) for i in state_cols]
        for row in rows:
            ident = _clean(row[0])
            if not re.match(r"^(PL|R)\d+$", ident, re.I):
                continue
            cr = ConfigRow(id=ident.upper(), what=row[at["Qué se cumple"]].strip() if "Qué se cumple" in at else "")
            for i in state_cols:
                st = _state(row[i])
                cr.states[_clean(header[i])] = st
                if st and not st["estado"] and not _placeholder([row[i]]):
                    cf.warnings.append(f"{cr.id}, {_clean(header[i])}: «{st['texto']}» no es cumple, no cumple, no aplica ni excepción")
                elif st and st["estado"] in ("cumple", "no cumple") and not st["fecha"]:
                    cf.warnings.append(f"{cr.id}, {_clean(header[i])}: «{st['estado']}» sin fecha")
                if st and st["fecha"] > cf.latest:
                    cf.latest = st["fecha"]
                if st and st["fecha"] and (not cf.oldest or st["fecha"] < cf.oldest):
                    cf.oldest = st["fecha"]
                if st is None or _placeholder([row[i]]):
                    cf.unchecked.append(cr.id + ("" if cf.kind == "plataforma" else " " + _clean(header[i])))
            cf.rows.append(cr)
    if changes_block or key("Cambios aprobados") in secs:
        h, r = _table(changes_block)
        at, missing = _columns(h, ("Fecha", "Qué cambió", "Aprobó"))
        if h:
            cf.missing += [f"columna {c} en Cambios aprobados" for c in missing]
        if not missing:
            for row in r:
                if not _placeholder(row):
                    cf.changes.append(ApprovedChange(_clean(row[at["Fecha"]]), row[at["Qué cambió"]].strip(),
                                                     _clean(row[at["Aprobó"]])))
    elif cf.kind == "plataforma":
        cf.missing.append("sección Cambios aprobados")
    return cf


# ── the status of each piece ───────────────────────────────────────────────────────────────────────────────────────

PENDING, IN_PROGRESS, MERGED, DELIVERED = "pendiente", "en curso", "unida", "entregada"
_ORDER = {PENDING: 0, IN_PROGRESS: 1, MERGED: 2, DELIVERED: 3}


@dataclass
class PullRequest:
    """A pull request as the caller read it from GitHub. `state`: "open", "closed" (without merging) or "merged"."""
    repo: str
    number: int
    title: str
    state: str
    author: str = ""
    bot: bool = False                           # GitHub's user type «Bot», or a login ending in «[bot]»
    merge_commit: str = ""
    to_main: bool = True                        # its base is the repository's main branch; the others are steps inside a block
    merged_at: str = ""                         # ISO; orders a piece's merges, so a revert merged last is seen


@dataclass
class PieceStatus:
    id: str
    status: str                                 # PENDING | IN_PROGRESS | MERGED | DELIVERED
    pull_requests: list = field(default_factory=list)      # «repo#number» that count
    reverted: bool = False                      # its last merged pull request is a revert: what it delivered is undone


@dataclass
class PieceReport:
    pieces: list = field(default_factory=list)             # [PieceStatus], in the plan's order
    outside_plan: list = field(default_factory=list)       # [PullRequest] without a piece, or with one not in the plan
    ignored: list = field(default_factory=list)            # [PullRequest] closed without merging, or from bots


def _pieces_of(title: str) -> list:
    """The identifiers a pull request's title starts with, followed by « · »: one («P03 · …»), or the pieces of a block
    joined by « + » («P01 + P02 · …», tecnologia/metodologia-desarrollo#2026-11-18-12). A GitHub revert («Revert "P03 ·
    …"») carries its pieces. [] when there is none."""
    t, _ = _unwrap_reverts(title)
    m = re.match(r"^([^\s·+]+(?:\s*\+\s*[^\s·+]+)*)\s+·\s+\S", t)
    return [x.strip() for x in m.group(1).split("+")] if m else []


def _unwrap_reverts(title: str) -> tuple:
    """(the innermost title, how many «Revert "…"» wrap it). Reverting a revert, GitHub's way of putting it back,
    nests them («Revert "Revert "P01 · a""»)."""
    t, n = _nfc(title).strip(), 0
    while True:
        m = re.match(r'^Revert\s+"(.*)"$', t) or re.match(r'^Revert\s+"(.*)$', t)
        if not m:
            return t, n
        t, n = m.group(1).strip(), n + 1


def _is_revert(title: str) -> bool:
    """An odd number of «Revert» undoes the piece; an even number puts it back (review of 1.27.0, fixes 1, finding 15)."""
    return _unwrap_reverts(title)[1] % 2 == 1


def _is_bot(pr: PullRequest) -> bool:
    return pr.bot or pr.author.lower().endswith("[bot]")


def piece_status(plan: Plan, pull_requests: Iterable[PullRequest],
                 delivered: Optional[Mapping[str, Iterable[int]]] = None) -> PieceReport:
    """Each piece's status by the rule of tecnologia/metodologia-desarrollo#2026-11-18-10 and -12, from pull requests
    already read. `delivered` maps a repository to the numbers of its merged pull requests inside its last step to Prod
    (the caller works that out from the release or tag «Paso a Prod» leaves); without it no piece is delivered.

    Only pull requests into the main branch count: those into another branch are steps inside a block (-12). A block's
    pull request counts for every piece its title names. With several pull requests the least advanced decides. A pull
    request closed without merging does not count, and neither do bots'. One without a piece, or naming a piece the plan
    does not have, is outside the plan. A piece whose last merged pull request is a revert is in progress again, with
    `reverted`."""
    inside = {r.lower(): {int(n) for n in nums} for r, nums in (delivered or {}).items()}
    by_piece: dict = {p.id.casefold(): [] for p in plan.pieces}
    rep = PieceReport()
    for pr in pull_requests:
        if pr.state not in ("open", "merged") or _is_bot(pr) or not pr.to_main:
            rep.ignored.append(pr)
            continue
        idents = _pieces_of(pr.title)
        if not idents or any(i.casefold() not in by_piece for i in idents):
            rep.outside_plan.append(pr)
            continue
        for i in dict.fromkeys(x.casefold() for x in idents):
            by_piece[i].append(pr)
    for p in plan.pieces:
        prs = by_piece[p.id.casefold()]
        if not prs:
            status = PENDING
        else:
            def one(pr):
                if pr.state == "open":
                    return IN_PROGRESS
                return DELIVERED if pr.number in inside.get(pr.repo.lower(), ()) else MERGED
            status = min((one(pr) for pr in prs), key=_ORDER.get)
        # a revert merged after the piece's other merges undoes it: the piece is back in progress (finding 15)
        merged = sorted((pr for pr in prs if pr.state == "merged"), key=lambda pr: (pr.merged_at, pr.number))
        reverted = bool(merged) and _is_revert(merged[-1].title)
        if reverted:
            status = IN_PROGRESS
        rep.pieces.append(PieceStatus(p.id, status, [f"{pr.repo}#{pr.number}" for pr in prs], reverted))
    return rep


# ── out ────────────────────────────────────────────────────────────────────────────────────────────────────────────

_ENTRY = re.compile(r"(?m)^(?=## 20\d\d-\d\d-\d\d)")
_READ = re.compile(r"^Leído\b[^:\n]*:.*[\w.-]+/[\w.-]+ en `[0-9a-f]{7,40}`", re.M)


def follow_up_entries(text: str) -> list:
    """The real entries of a follow-up file, newest first, as dicts with «date», «repos» (lower-case owner/name read),
    «watched» (its «**Rompe las reglas:**» line, at the start of a line, does not say «sin vigilar») and «design» (its
    «Comparó:» line includes «diseño»). A real entry has its «Leído:» line with each repository's commit; a hand-written
    note does not count, and neither does one marked «**Incompleto, no se guarda:**». One rule for the follow-up script
    and the opening (fixes 5, finding 12; fixes 6, findings 3 and 14)."""
    body = text or ""
    if body.startswith("---\n") and "\n---\n" in body[4:]:
        body = body[body.index("\n---\n", 4) + 5:]
    out = []
    for e in _ENTRY.split(body):
        m = re.match(r"## (20\d\d-\d\d-\d\d)\b", e)
        read = _READ.search(e)
        if not m or not read or re.search(r"^\*\*Incompleto, no se guarda:\*\*", e, re.M):
            continue
        compared = re.search(r"^Comparó:(.*)$", e, re.M)
        out.append({"date": m.group(1),
                    "repos": [x.lower() for x in re.findall(r"([\w.-]+/[\w.-]+) en `[0-9a-f]{7,40}`", read.group(0))],
                    "watched": bool(re.search(r"^\*\*Rompe las reglas:\*\*", e, re.M))
                               and not re.search(r"^\*\*Rompe las reglas:\*\* sin (vigilar|comprobar)", e, re.M),
                    "design": bool(compared and "diseño" in compared.group(1))})
    return out


def as_dict(obj):
    """Any result of this module as plain dicts and lists, for the board's JSON."""
    return dataclasses.asdict(obj) if dataclasses.is_dataclass(obj) else obj


# the specification's names (especificacion-version-plugin-kit-desarrollo.md, 3.2)
seccion_desarrollo = development_section
piezas_faltantes = missing_pieces
leer_diseno = read_design
leer_plan = read_plan
leer_configuracion = read_configuration
estado_piezas = piece_status
entradas_seguimiento = follow_up_entries
