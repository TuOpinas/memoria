"""The development kit (1.27): how the plugin recognises a project that builds software. Pure functions: text in, data
out; no I/O, no network, no clock.

A project is a development project when its proyecto.md has a «## Desarrollo» section
(tecnologia/metodologia-desarrollo#2026-11-18-4). The section points to each piece of the kit (the configuration, the
design, the plan and the follow-up) and names the people of each role. This module reads the section and says which
pieces are missing. Since 1.28.0 it also reads the design, the plan and the last follow-up entry for the board's
«Desarrollo» tab (shared-memory/plugin-memoria#2026-11-22-5, P05): `development_view` turns them into what the tab draws,
and names what it cannot read instead of failing. The status of each piece in GitHub is still applied by the model from
the plan's rule (tecnologia/metodologia-desarrollo#2026-11-19-2); the view only shows what the last follow-up wrote.

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
    "read_design", "read_plan", "read_follow_up", "design_detail_path", "development_view", "vista_desarrollo",
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
                r = r.strip("<>")
                g = re.match(r"^(?:https?://(?:www\.)?|git@)?github\.com[/:]([^/\s]+)/([^/\s#?]+)", r, re.I)
                if g:
                    r = g.group(1) + "/" + (g.group(2)[:-4] if g.group(2).lower().endswith(".git") else g.group(2))
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


# ── the design, the plan and the follow-up, for the board's «Desarrollo» tab (1.28.0) ─────────────────────────────

def _header(text: str) -> dict:
    """The «key: value» lines of a front matter, by key (only what the view needs: «actualizado»)."""
    m = re.match(r"^---\n(.*?)\n---\n", _nfc(text), re.S)
    out = {}
    for line in (m.group(1).split("\n") if m else []):
        k, _, v = line.partition(":")
        if v:
            out[key(k)] = v.strip().strip('"')
    return out


def _cells(line: str) -> list:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _table(lines: list) -> tuple:
    """The first Markdown table in `lines`: (titles, rows as lists of cells), or ([], []) without one."""
    i = next((n for n, l in enumerate(lines) if l.strip().startswith("|")), None)
    if i is None or i + 1 >= len(lines) or not re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
        return [], []
    titles, rows = _cells(lines[i]), []
    for l in lines[i + 2:]:
        if not l.strip().startswith("|"):
            break
        rows.append(_cells(l))
    return titles, rows


def _columns(titles: list, wanted: list, what: str, warn) -> dict:
    """Where each wanted column is, by key; a missing one is named in a warning and maps to None."""
    at = {key(t): n for n, t in enumerate(titles)}
    out = {}
    for w in wanted:
        out[w] = at.get(key(w))
        if out[w] is None:
            warn(f"a la tabla de «{what}» le falta la columna «{w}»")
    return out


def _cell(row: list, n) -> str:
    return _clean(row[n]) if n is not None and n < len(row) else ""


def _list(cell: str) -> list:
    return [x.strip() for x in SEPARATOR.split(cell) if x.strip()]


def _split_id(cell: str) -> tuple:
    """«P01 · Lista de productos» -> ("P01", "Lista de productos"); «F1» -> ("F1", "")."""
    m = re.match(r"^\s*([A-Za-z]+\d+)\s*(?:[·:—-]\s*(.*))?$", _clean(cell))
    return (m.group(1).upper(), (m.group(2) or "").strip()) if m else ("", _clean(cell))


def _paragraph(body: str) -> str:
    """The first paragraph of a section that is not a table, a list or a comment."""
    out = []
    for l in body.split("\n"):
        t = l.strip()
        if not t:
            if out:
                break
            continue
        if t.startswith(("|", "<!--", "#")) or re.match(r"^([-*]|\d+[.)])\s", t):
            if out:
                break
            continue
        out.append(t)
    return " ".join(out)


def design_detail_path(design_text: str) -> str:
    """The path of the line «Detalle: ruta» under «Datos», or "" without one."""
    sec = _sections(design_text).get(key("Datos"))
    m = re.search(r"^\s*Detalle\s*:\s*(.+?)\s*$", sec[1], re.M) if sec else None
    return _clean(m.group(1)).lstrip("/") if m else ""


_HOW = (key("Cómo funciona"), key("How it works"))


def read_design(text: str, detail_text=None, detail_path: str = "") -> tuple:
    """The design as the tab draws it, and its warnings as [(part, text)]. A missing section or column is named and the
    rest is returned; a «Conecta con» or a relation to something its table lacks is named and left out of the lines."""
    warnings = []
    warn = lambda part: (lambda t: warnings.append((part, t)))
    secs = _sections(text)

    def section(name, part, aliases=()):
        for k in (key(name),) + tuple(aliases):
            if k in secs:
                return secs[k][1]
        warn(part)(f"al diseño le falta la sección «{name}»")
        return None

    out = {"objetivo": "", "como_funciona": [], "reglas": [], "entidades": [], "conceptos": [], "componentes": [],
           "infraestructura": []}
    body = section("Objetivo", "diseno")
    if body is not None:
        out["objetivo"] = _paragraph(body)
    body = section("Cómo funciona", "diseno", _HOW)
    if body is not None:
        out["como_funciona"] = [m.group(1).strip() for m in re.finditer(r"^\s*\d+[.)]\s+(.+)$", body, re.M)]
    body = section("Reglas", "diseno")
    if body is not None:
        t, rows = _table(body.split("\n"))
        c = _columns(t, ["Regla", "Excepción"], "Reglas", warn("diseno"))
        out["reglas"] = [{"regla": _cell(r, c["Regla"]), "excepcion": _cell(r, c["Excepción"])} for r in rows]
    for name, part, cols, fields in (
            ("Componentes", "componentes", ["Componente", "Qué hace", "Dónde vive", "Conecta con"], ["nombre", "que_hace", "donde"]),
            ("Infraestructura", "infraestructura", ["Pieza", "Para qué", "Dónde", "Conecta con"], ["nombre", "para_que", "donde"])):
        body = section(name, part)
        if body is None:
            continue
        t, rows = _table(body.split("\n"))
        c = _columns(t, cols, name, warn(part))
        items = [dict(zip(fields, (_cell(r, c[x]) for x in cols[:3])), conecta_con=_list(_cell(r, c["Conecta con"]))) for r in rows]
        names = {i["nombre"] for i in items}
        for i in items:
            for o in [o for o in i["conecta_con"] if o not in names]:
                warn(part)(f"«{i['nombre']}» conecta con «{o}», que no está en «{name}»")
                i["conecta_con"].remove(o)
        out[part] = items
    body = section("Datos", "datos")
    if body is not None:
        t, rows = _table(body.split("\n"))
        c = _columns(t, ["Entidad", "Grupo", "Qué es", "Se relaciona con"], "Datos", warn("datos"))
        for r in rows:
            rel = []
            for x in re.split(r"\s+·\s+|,\s*", _cell(r, c["Se relaciona con"])):
                m = re.match(r"^\s*([^()]+?)\s*(?:\(([^)]*)\))?\s*$", x)
                if m and m.group(1):
                    rel.append({"con": m.group(1).strip(), "tipo": (m.group(2) or "").strip()})
            out["entidades"].append({"nombre": _cell(r, c["Entidad"]), "grupo": _cell(r, c["Grupo"]) if c["Grupo"] is not None else None,
                                     "que_es": _cell(r, c["Qué es"]), "relaciones": rel, "detalle": None, "conceptos": []})
        names = {e["nombre"] for e in out["entidades"]}
        for e in out["entidades"]:
            for x in [x for x in e["relaciones"] if x["con"] not in names]:
                warn("datos")(f"«{e['nombre']}» se relaciona con «{x['con']}», que no está en «Datos»")
                e["relaciones"].remove(x)
    body = section("Conceptos", "diseno")
    if body is not None:
        t, rows = _table(body.split("\n"))
        c = _columns(t, ["Concepto", "Significa", "No es", "Entidades"], "Conceptos", warn("diseno"))
        out["conceptos"] = [{"nombre": _cell(r, c["Concepto"]), "significa": _cell(r, c["Significa"]), "no_es": _cell(r, c["No es"]),
                             "entidades": _list(_cell(r, c["Entidades"]))} for r in rows]
    by_name = {key(e["nombre"]): e for e in out["entidades"]}
    for k_ in out["conceptos"]:
        for n in k_["entidades"]:
            if key(n) in by_name:
                by_name[key(n)]["conceptos"].append(k_["nombre"])
    if detail_path:
        if detail_text is None:
            warn("datos")(f"el detalle de los datos ({detail_path}) no se pudo leer")
        else:
            t, rows = _table(_nfc(detail_text).split("\n"))
            if not t:
                warn("datos")(f"el detalle de los datos ({detail_path}) no tiene una tabla")
            seen = set()
            for r in rows:
                k = key(_cell(r, 0))
                if k in by_name:
                    by_name[k]["detalle"] = {t[n]: _clean(r[n]) for n in range(1, min(len(t), len(r)))}
                    seen.add(k)
                elif k:
                    warn("datos")(f"«{_cell(r, 0)}» está en el detalle ({detail_path}) y no en «Datos» del diseño")
            for k, e in by_name.items():
                if k not in seen and t:
                    warn("datos")(f"«{e['nombre']}» no tiene fila en el detalle ({detail_path})")
    return out, warnings


_PLAIN = re.compile(r"^###\s+([A-Za-z]+\d+)\s+(?:en llano|in plain words)\s*$", re.I)


def read_plan(text: str) -> tuple:
    """The plan as the tab draws it: its phases in order with their pieces, and each piece with what it delivers, who
    approved its scenarios and the scenarios. Warnings as [(part, text)]."""
    warnings = []
    warn = lambda t: warnings.append(("plan", t))
    secs = _sections(text)
    phases, pieces = [], []
    sec = secs.get(key("Fases"))
    t, rows = _table(sec[1].split("\n")) if sec else ([], [])
    if not rows:
        warn("la tabla de fases del plan no se pudo leer")
    else:
        c = _columns(t, ["Fase", "Qué podrá hacer quién", "Versión", "Listo cuando"], "Fases", warn)
        for r in rows:
            fid, name = _split_id(_cell(r, c["Fase"]))
            phases.append({"id": fid, "nombre": name, "que_podra": _cell(r, c["Qué podrá hacer quién"]), "version": _cell(r, c["Versión"]),
                           "listo_cuando": _cell(r, c["Listo cuando"]), "en_llano": "", "arregla": [], "piezas": []})
        plain, cur = {}, None
        for l in _nfc(sec[1]).split("\n"):
            m = _PLAIN.match(l.strip())
            if m:
                cur = plain.setdefault(m.group(1).upper(), [])
            elif l.startswith("### "):
                cur = None
            elif cur is not None:
                cur.append(l)
        for f in phases:
            ls = plain.get(f["id"], [])
            f["en_llano"] = _paragraph("\n".join(ls))
            pt, pr = _table(ls)
            f["arregla"] = [{"pieza": _cell(r, 0), "que": _cell(r, 1)} for r in pr if len(r) > 1]
    sec = secs.get(key("Piezas"))
    t, rows = _table(sec[1].split("\n")) if sec else ([], [])
    if not rows:
        warn("la tabla de piezas del plan no se pudo leer")
    else:
        c = _columns(t, ["Pieza", "Fase", "Qué entrega"], "Piezas", warn)
        for r in rows:
            pid, name = _split_id(_cell(r, c["Pieza"]))
            pieces.append({"id": pid, "nombre": name, "fase": _split_id(_cell(r, c["Fase"]))[0], "entrega": _cell(r, c["Qué entrega"]),
                           "aprobo": "", "escenarios": [], "estado": None, "fecha_estado": None})
    by_id = {p["id"]: p for p in pieces}
    for f in phases:
        f["piezas"] = [p["id"] for p in pieces if p["fase"] == f["id"]]
    sec = secs.get(key("Hecha cuando"))
    cur, scen = None, None
    for l in (_nfc(sec[1]).split("\n") if sec else []):
        m = re.match(r"^###\s+([A-Za-z]+\d+)\b", l)
        if m:
            cur, scen = by_id.get(m.group(1).upper()), None
            continue
        if cur is None:
            continue
        a = re.match(r"^\s*Aprob[oó]\s*:\s*(.*)$", l)
        b = re.match(r"^\s*[-*]\s+\*\*(.+?)\*\*\s*(.*)$", l)
        if a and not scen:
            cur["aprobo"] = _clean(a.group(1))
        elif b:
            scen = {"titulo": b.group(1).strip(), "texto": b.group(2).strip()}
            cur["escenarios"].append(scen)
        elif scen is not None and l.startswith((" ", "\t")) and l.strip():
            scen["texto"] = (scen["texto"] + "\n" + l.strip()).strip()
        elif not l.strip():
            continue
        else:
            scen = None
    return {"fases": phases, "piezas": pieces}, warnings


def read_follow_up(text: str) -> tuple:
    """The newest entry of a follow-up: (its date, {piece: state}), or ("", {}) without one."""
    entries = []
    for name, body in _sections(text).values():
        m = re.match(r"^(\d{4}-\d{2}-\d{2})\b", name)
        if m:
            entries.append((m.group(1), body))
    if not entries:
        return "", {}
    date, body = max(entries, key=lambda e: e[0])
    states = {}
    lines = body.split("\n")
    while lines:
        t, rows = _table(lines)
        if not t:
            break
        c = {key(x): n for n, x in enumerate(t)}
        if key("Pieza") in c and key("Estado") in c:
            for r in rows:
                pid = _split_id(_cell(r, c[key("Pieza")]))[0]
                if pid:
                    states[pid] = _cell(r, c[key("Estado")])
            break
        i = next(n for n, l in enumerate(lines) if l.strip().startswith("|"))
        lines = lines[i + 2 + len(rows):]
    return date, states


def development_view(section: DevSection, read: Callable[[str], object]) -> dict:
    """What the «Desarrollo» tab draws for a project with the section: the sources with their dates, the design, the plan
    with each piece's state from the newest follow-up entry, and what could not be read or does not match. `read(path)`
    gives the text of a path from the root, or None."""
    view = {"fuentes": {"diseno": None, "plan": None, "seguimiento": None}, "diseno": None, "plan": None, "avisos": []}
    say = lambda part, text: view["avisos"].append({"parte": part, "texto": text})

    def source(k, part):
        path = section.paths.get(k, "")
        if not path or path == TO_BUILD:
            say(part, f"«{k}» está por crear" if path == TO_BUILD else f"la sección no dice «{k}»")
            return "", None
        text = read(path)
        if text is None:
            say(part, f"«{k}» ({path}) no se pudo leer")
        return path, text

    path, text = source(DESIGN, "diseno")
    if text is not None:
        dp = design_detail_path(text)
        view["diseno"], w = read_design(text, read(dp) if dp else None, dp)
        view["avisos"] += [{"parte": p, "texto": t} for p, t in w]
        view["fuentes"]["diseno"] = {"ruta": path, "actualizado": _header(text).get("actualizado")}
    path, text = source(PLAN, "plan")
    if text is not None:
        view["plan"], w = read_plan(text)
        view["avisos"] += [{"parte": p, "texto": t} for p, t in w]
        view["fuentes"]["plan"] = {"ruta": path, "actualizado": _header(text).get("actualizado")}
    path = section.paths.get(FOLLOW_UP, "")
    if not path or path == TO_BUILD:
        say("seguimiento", "aún no hay seguimiento: las piezas salen sin estado")
    else:
        text = read(path)
        date, states = read_follow_up(text) if text is not None else ("", {})
        if text is None:
            say("seguimiento", f"el seguimiento ({path}) no se pudo leer")
        elif not date:
            say("seguimiento", f"el seguimiento ({path}) no tiene ninguna entrada con fecha")
        else:
            view["fuentes"]["seguimiento"] = {"ruta": path, "fecha": date}
            for p in (view["plan"] or {}).get("piezas", []):
                if p["id"] in states:
                    p["estado"], p["fecha_estado"] = states[p["id"]], date
    return view


# the Spanish names the plugin's scripts use
seccion_desarrollo = development_section
piezas_faltantes = missing_pieces
vista_desarrollo = development_view
