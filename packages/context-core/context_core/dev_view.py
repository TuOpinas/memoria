"""The board's «Desarrollo» tab (1.28.0, P05): reads the design, the plan and the newest follow-up entry of a development
project and says what it cannot read or what does not match, instead of failing. Pure functions: text in, data out.
Only the board's generator imports it, so the scripts that open a session do not carry it.
"""
from __future__ import annotations

import re
from typing import Callable

from .development import (key, _sections, _nfc, _clean, SEPARATOR, DevSection, DESIGN, PLAN, FOLLOW_UP, TO_BUILD)

__all__ = ["read_design", "read_plan", "read_follow_up", "design_detail_path", "development_view", "vista_desarrollo"]


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


def _optional(titles: list, name: str):
    """Where an optional column is, by key, or None without it: its absence is not warned."""
    return {key(t): n for n, t in enumerate(titles)}.get(key(name))


def _roles(names: list, edges: list, flow, outside=()) -> dict:
    """Each box's role in its drawing (1.29.1, P19): «flujo», «destino» or «resto». `edges` are the drawn lines (a, b);
    `flow` the names of the section's «Flujo:» line, or None without one; `outside` what always goes with the rest (what
    is external, the shared base)."""
    into, out_ = {}, {}
    for a, b in edges:
        out_[a] = out_.get(a, 0) + 1
        into[b] = into.get(b, 0) + 1
    roles = {}
    for n in names:
        if n in outside:
            roles[n] = "resto"
        elif flow is not None and n in flow:
            roles[n] = "flujo"
        elif into.get(n) and not out_.get(n):
            roles[n] = "destino"
        elif flow is None and (into.get(n) or out_.get(n)):
            roles[n] = "flujo"
        else:
            roles[n] = "resto"
    return roles


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
    m = re.search(r"^\s*\**\s*Detalle\s*\**\s*:\s*\**\s*(.+?)\s*$", sec[1], re.M) if sec else None
    return _clean(m.group(1)).lstrip("/") if m else ""


_HOW = (key("Cómo funciona"), key("How it works"))
_CARD = re.compile(r"^\s*(?:[0-9]+|[NnMm*])\s*(?::|\.\.)\s*(?:[0-9]+|[NnMm*])\s*$")


def _flow(body: str) -> list:
    """The names of a line «Flujo: A → B → C» of a section (1.29.0), in order, or None without one."""
    m = re.search(r"^[ \t]*(?:[-*][ \t]+)?\**[ \t]*Flujo[ \t]*\**[ \t]*:[ \t]*\**[ \t]*(.*?)[ \t]*$", body, re.M)
    if not m:
        return None
    text = _clean(m.group(1)).strip("* ")
    if not text or text.startswith("["):   # vacía, o el hueco de la plantilla sin rellenar: como si no estuviera
        return None
    return [x.strip() for x in re.split(r"\s*(?:→|->)\s*", text) if x.strip()]


def _known(flow, names: list, what: str, warn) -> list:
    """The flow's names that its table has, in order; the others are named in a warning."""
    by_key, out = {key(n): n for n in names}, []
    for n in flow:
        k = by_key.get(key(n))
        if k is None:
            warn(f"«Flujo:» de «{what}» nombra «{n}», que no está en la tabla")
        elif k in out:
            warn(f"«Flujo:» de «{what}» repite «{n}»: se dibuja una vez, donde sale primero")
        else:
            out.append(k)
    return out


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
           "infraestructura": [], "datos_disposicion": None, "componentes_flujo": None, "infraestructura_contenedores": None}
    body = section("Objetivo", "diseno")
    if body is not None:
        out["objetivo"] = _paragraph(body)
    body = section("Cómo funciona", "diseno", _HOW)
    if body is not None:
        out["como_funciona"] = [m.group(1).strip() for m in re.finditer(r"^\s*(?:\d+[.)]|[-*])\s+(.+)$", body, re.M)]
        if not out["como_funciona"]:
            warn("diseno")("«Cómo funciona» no tiene pasos: van como lista numerada")
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
        keys = {key(x) for x in t}
        by_account = part == "infraestructura" and key("Proveedor") in keys
        if by_account:
            # 1.29.0 (P18): «Dónde» parted into Proveedor, Cuenta and Ambiente
            cols = ["Pieza", "Para qué", "Proveedor", "Cuenta", "Ambiente", "Conecta con"]
        c = _columns(t, cols, name, warn(part))
        if by_account:
            items = [{"nombre": _cell(r, c["Pieza"]), "para_que": _cell(r, c["Para qué"]), "proveedor": _cell(r, c["Proveedor"]),
                      "cuenta": _cell(r, c["Cuenta"]), "ambiente": _cell(r, c["Ambiente"]),
                      # «donde» también, para una página 1.28.0 que aún no se republicó y lee solo ese campo
                      "donde": " · ".join(x for x in (_cell(r, c["Proveedor"]), _cell(r, c["Cuenta"]), _cell(r, c["Ambiente"])) if x),
                      "conecta_con": _list(_cell(r, c["Conecta con"]))} for r in rows]
        else:
            items = [dict(zip(fields, (_cell(r, c[x]) for x in cols[:3])), conecta_con=_list(_cell(r, c["Conecta con"]))) for r in rows]
        short = _optional(t, "En corto")
        for i, r in zip(items, rows):
            i["en_corto"] = _cell(r, short)
        if part == "componentes":
            # 1.29.0 (P17): an optional «Externo» column
            ext = {key(x): n for n, x in enumerate(t)}.get(key("Externo"))
            for i, r in zip(items, rows):
                i["externo"] = bool(re.match(r"^\s*(s[ií]|yes|x|✓|externo)\b", _cell(r, ext), re.I))
        names = {i["nombre"] for i in items}
        for i in items:
            for o in [o for o in i["conecta_con"] if o not in names]:
                warn(part)(f"«{i['nombre']}» conecta con «{o}», que no está en «{name}»")
                i["conecta_con"].remove(o)
        out[part] = items
        if part == "componentes":
            f = _flow(body)
            if f is not None:
                out["componentes_flujo"] = _known(f, [i["nombre"] for i in items], name, warn(part))
            elif items:
                warn(part)("«Componentes» no tiene línea «Flujo:»: añade «Flujo: A → B → C» con el recorrido de la llamada "
                           "principal, y los componentes se dibujan como ese recorrido")
        elif by_account:
            boxes = {}
            for i in items:
                k = (key(i["proveedor"]), key(i["cuenta"]))
                if k not in boxes:
                    boxes[k] = {"proveedor": i["proveedor"], "cuenta": i["cuenta"], "ambiente": i["ambiente"], "piezas": []}
                boxes[k]["piezas"].append(i["nombre"])
                if i["ambiente"] and i["ambiente"] not in boxes[k]["ambiente"].split(" · "):
                    boxes[k]["ambiente"] = " · ".join(x for x in (boxes[k]["ambiente"], i["ambiente"]) if x)
            out["infraestructura_contenedores"] = list(boxes.values())
        elif items:
            warn(part)("«Infraestructura» lleva «Dónde» en una columna: pártela en «Proveedor», «Cuenta» y «Ambiente» "
                       "para que cada proveedor y cuenta se dibuje como un contenedor")
    comps, fl = out["componentes"], out["componentes_flujo"]
    edges = [(i["nombre"], o) for i in comps for o in i["conecta_con"]] + list(zip(fl or [], (fl or [])[1:]))
    roles = _roles([i["nombre"] for i in comps], edges, fl, {i["nombre"] for i in comps if i.get("externo")})
    for i in comps:
        i["rol"] = roles[i["nombre"]]
    infra = out["infraestructura"]
    roles = _roles([i["nombre"] for i in infra], [(i["nombre"], o) for i in infra for o in i["conecta_con"]], None)
    for i in infra:
        i["rol"] = roles[i["nombre"]]
    body = section("Datos", "datos")
    if body is not None:
        t, rows = _table(body.split("\n"))
        c = _columns(t, ["Entidad", "Grupo", "Qué es", "Se relaciona con"], "Datos", warn("datos"))
        short = _optional(t, "En corto")
        for r in rows:
            rel = []
            for x in (y for y in re.split(r"\s+·\s+|,\s*(?![^()]*\))", _cell(r, c["Se relaciona con"])) if y.strip()):
                m = re.match(r"^\s*([^()\s][^()]*?)\s*(?:\(([^)]*)\))?\s*$", x)
                if m:
                    # 1.29.0 (P16): a cardinality is the type; anything else between brackets is the relation's verb
                    inside = (m.group(2) or "").strip()
                    parts = [y.strip() for y in inside.split(",") if y.strip()]
                    card = [y for y in parts if _CARD.match(y)]
                    verb = [y for y in parts if not _CARD.match(y)]
                    r_ = {"con": m.group(1).strip(), "tipo": ", ".join(card)}
                    if verb:
                        r_["verbo"] = ", ".join(verb)
                    rel.append(r_)
                else:
                    warn("datos")(f"no se entiende la relación «{x.strip()}» de «{_cell(r, c['Entidad'])}»: va como «entidad (tipo)», separadas por « · »")
            out["entidades"].append({"nombre": _cell(r, c["Entidad"]), "grupo": _cell(r, c["Grupo"]) if c["Grupo"] is not None else None,
                                     "que_es": _cell(r, c["Qué es"]), "en_corto": _cell(r, short), "relaciones": rel,
                                     "detalle": None, "conceptos": []})
        names = {e["nombre"] for e in out["entidades"]}
        for e in out["entidades"]:
            for x in [x for x in e["relaciones"] if x["con"] not in names]:
                warn("datos")(f"«{e['nombre']}» se relaciona con «{x['con']}», que no está en «Datos»")
                e["relaciones"].remove(x)
        # 1.29.0 (P16): the flow's entities in one row; the one two or more of them point to, below; the rest, above
        f = _flow(body)
        if f is None:
            if out["entidades"]:
                warn("datos")("«Datos» no tiene línea «Flujo:»: añade «Flujo: A → B → C» con las entidades por las que pasa "
                              "un cambio, y el modelo se dibuja como un camino")
        else:
            flow = _known(f, [e["nombre"] for e in out["entidades"]], "Datos", warn("datos"))
            pointed = {}
            for e in out["entidades"]:
                if e["nombre"] in flow:
                    for x in {x["con"] for x in e["relaciones"]}:
                        pointed[x] = pointed.get(x, 0) + 1
            rest = [e["nombre"] for e in out["entidades"] if e["nombre"] not in flow]
            out["datos_disposicion"] = {"flujo": flow, "arriba": [n for n in rest if pointed.get(n, 0) < 2],
                                        "abajo": [n for n in rest if pointed.get(n, 0) >= 2]}
            # 1.29.1 (P20): what two or more of the flow point to is the shared base, a band with no lines
            base = set(out["datos_disposicion"]["abajo"])
            for e in out["entidades"]:
                for x in e["relaciones"]:
                    if x["con"] in base:
                        x["base"] = True
        dis = out["datos_disposicion"]
        base = set(dis["abajo"]) if dis else set()
        roles = _roles([e["nombre"] for e in out["entidades"]],
                       [(e["nombre"], x["con"]) for e in out["entidades"] for x in e["relaciones"]
                        if not x.get("base") and e["nombre"] not in base],
                       dis["flujo"] if dis else None, base)
        for e in out["entidades"]:
            e["rol"] = roles[e["nombre"]]
    body = section("Conceptos", "diseno")
    if body is not None:
        t, rows = _table(body.split("\n"))
        c = _columns(t, ["Concepto", "Significa", "No es", "Entidades"], "Conceptos", warn("diseno"))
        out["conceptos"] = [{"nombre": _cell(r, c["Concepto"]), "significa": _cell(r, c["Significa"]), "no_es": _cell(r, c["No es"]),
                             "entidades": [e for e in re.split(r"\s+·\s+|,\s*", _cell(r, c["Entidades"])) if e.strip()]} for r in rows]
    by_name = {key(e["nombre"]): e for e in out["entidades"]}
    for k_ in out["conceptos"]:
        for n in k_["entidades"]:
            if key(n) in by_name:
                by_name[key(n)]["conceptos"].append(k_["nombre"])
            else:
                warn("datos")(f"el concepto «{k_['nombre']}» nombra «{n}», que no está en «Datos»")
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


def _hours(cell: str, pid: str, warn):
    """The hours of a piece (1.29.1, P22): «1», «0.5», «0,75», «1.5 h»; None if empty, and a warning if unreadable."""
    if not cell:
        return None
    m = re.match(r"^\s*~?\s*(\d+(?:[.,]\d+)?)\s*(?:h|horas?|hours?)?\s*$", cell, re.I)
    if not m:
        warn(f"no se leen las horas de {pid} («{cell}»): van como un número de horas, «1.5»")
        return None
    v = float(m.group(1).replace(",", "."))
    return int(v) if v == int(v) else v


_PLAIN = re.compile(r"^###\s+([A-Za-z]+\d+)\s*[·:—-]?\s*(?:en llano|in plain words)\s*$", re.I)


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
            if not fid:
                warn(f"no se lee el identificador de la fase «{_cell(r, c['Fase'])}»: va como «F1 · nombre»")
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
        hours, stop = _optional(t, "Horas"), _optional(t, "Para antes")
        for r in rows:
            pid, name = _split_id(_cell(r, c["Pieza"]))
            if not pid:
                warn(f"no se lee el identificador de la pieza «{_cell(r, c['Pieza'])}»: va como «P01 · nombre»")
                continue
            pieces.append({"id": pid, "nombre": name, "fase": _split_id(_cell(r, c["Fase"]))[0], "entrega": _cell(r, c["Qué entrega"]),
                           "aprobo": "", "escenarios": [], "estado": None, "fecha_estado": None,
                           "horas": _hours(_cell(r, hours), pid, warn), "para_antes": _cell(r, stop)})
    by_id = {p["id"]: p for p in pieces}
    for f in phases:
        f["piezas"] = [p["id"] for p in pieces if p["fase"] == f["id"]]
        hs = [p["horas"] for p in pieces if p["fase"] == f["id"] and p["horas"] is not None]
        f["horas"] = round(sum(hs), 2) if hs else None
    ids = {f["id"] for f in phases}
    for p in pieces:
        if phases and p["fase"] not in ids:
            warn(f"{p['id']} es de la fase «{p['fase']}», que no está en «Fases»: no sale en el tablero")
    sec = secs.get(key("Hecha cuando"))
    cur, scen = None, None
    for l in (_nfc(sec[1]).split("\n") if sec else []):
        m = re.match(r"^###\s+([A-Za-z]+\d+)\b", l)
        if m:
            cur, scen = by_id.get(m.group(1).upper()), None
            continue
        if cur is None:
            continue
        a = re.match(r"^\s*\**\s*Aprob[oó]\s*\**\s*:\s*\**\s*(.*)$", l)
        b = re.match(r"^\s*[-*]\s+\*\*(.+?)\*\*\s*(.*)$", l)
        if a and not scen:
            # aprobado es nombre y fecha; «pending» o el hueco de la plantilla no aprueban nada
            cur["aprobo"] = _clean(a.group(1)) if re.search(r"\d{4}-\d{2}-\d{2}", a.group(1)) else ""
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
    lines = body.split("\n")   # la entrada sin tabla «Pieza | Estado» vuelve sin estados, y la vista lo dice
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
        elif not states:
            say("seguimiento", f"la entrada del {date} del seguimiento no tiene la tabla «Pieza | Estado»: las piezas salen sin estado")
        else:
            view["fuentes"]["seguimiento"] = {"ruta": path, "fecha": date}
            for p in (view["plan"] or {}).get("piezas", []):
                if p["id"] in states:
                    p["estado"], p["fecha_estado"] = states[p["id"]], date
    return view


vista_desarrollo = development_view
