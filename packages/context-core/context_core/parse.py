"""Text of one method file -> records. Pure functions: no I/O, no globals, no clock.

Ported from the plugin scripts with the same rules; where `abrir.py`, `cerrar.py` and `generar_vista.py` each carry a
copy of a function (the «who writes» block, the restricted rule, the people registry), this is the one copy they will
call once step 0 moves them onto the package. `tests/test_parity.py` runs the script copies and these on the same
inputs and fails on any difference.
"""
from __future__ import annotations

import datetime
import re
import unicodedata
from typing import Optional

from .records import (
    Area, AreaRow, Decision, DecisionRef, Deliverable, IndexEntry, PeopleRegistry, Person, Premise, Project,
    SessionEntry, Status, Step,
)

EMAIL = re.compile(r"[\w.+'-]+@[\w-]+(?:\.[\w-]+)*")
_WORD_COLLABORATES = re.compile(r"\bco-?labor\w*\s*:?", re.I)
_LINE_COLLABORATES = re.compile(r"^\s*[-*]?\s*\**\s*colabora[n]?\s*\**\s*:", re.I)


# ── text helpers ───────────────────────────────────────────────────────────────────────────────────────────────────

def frontmatter(text: str) -> tuple[dict, str]:
    """(header, body). Inline lists «[a, b]» and multi-line «- a» lists become lists; everything else a string."""
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    fm: dict = {}
    if not m:
        return fm, text
    last = None
    for line in m.group(1).split("\n"):
        mm = re.match(r"^(\w+):\s*(.*)$", line)
        if mm:
            last = mm.group(1)
            v = mm.group(2).strip()
            fm[last] = ([x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
                        if v.startswith("[") and v.endswith("]") else v.strip("'\""))
            continue
        ml = re.match(r"^\s+-\s+(.*)$", line)
        if ml and last:
            if not isinstance(fm.get(last), list):
                fm[last] = []
            fm[last].append(ml.group(1).strip().strip("'\""))
    return fm, text[m.end():]


def section(text: str, name: str) -> str:
    m = re.search(r"^## " + re.escape(name) + r"\s*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1).strip() if m else ""


def h1(text: str) -> str:
    m = re.search(r"^# (.+)$", text, re.M)
    return m.group(1).strip() if m else ""


def bullets(text: str) -> list[str]:
    return [s[2:].strip() for s in (l.strip() for l in text.split("\n")) if s.startswith("- ")]


def dates_in(text: str) -> list[str]:
    return re.findall(r"\b(20\d\d-\d\d-\d\d)\b", text or "")


def valid_date(d: Optional[str]) -> bool:
    try:
        datetime.date.fromisoformat(d)  # type: ignore[arg-type]
        return True
    except (ValueError, TypeError):
        return False


def name_key(n: str) -> str:
    """How two names compare: NFC, lowercase, without bold, quotes or parentheses, spaces joined. An accent counts."""
    n = unicodedata.normalize("NFC", n or "").replace(" ", " ")
    n = re.sub(r"\s*\([^)]*\)", "", re.sub(r"[*_`«»\"]", "", n))
    return re.sub(r"\s+", " ", n).strip(" .,;:").lower()


def heading_key(t: str) -> str:
    """A heading to compare: without accents (NFC or NFD), case or punctuation."""
    t = "".join(c for c in unicodedata.normalize("NFD", t or "") if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", "", t.lower())).strip()


# ── restricted ─────────────────────────────────────────────────────────────────────────────────────────────────────

def is_restricted_cell(cell: str) -> bool:
    """«Quién la lee» declares the area restricted: the word at the start («Restringida: …»), or «restringida» on its
    own elsewhere («Dirección (restringida)») and not negated («nunca restringida», «antes restringida»)."""
    c = cell or ""
    if re.match(r"^[\W_]*restringid[oa]s?\b", c, re.I):
        return True
    return bool(re.search(r"\brestringidas?\b", c, re.I)) and not re.search(
        r"\b(?:nada|no|nunca|sin|antes)\s+(?:[^\s]+\s+)?restringid", c, re.I)


def starts_restricted(line: str) -> bool:
    """An index line «- `x/` — restringido: …» marks the project restricted."""
    return bool(re.match(r"^[\W_]*restringid[oa]\b", line or "", re.I))


# ── people ─────────────────────────────────────────────────────────────────────────────────────────────────────────

def people_registry(guia: str) -> PeopleRegistry:
    """«Quién es quién» of guia.md. Same rules as registro_personas() in the scripts."""
    lines, inside, declared = [], False, False
    for l in unicodedata.normalize("NFC", guia or "").split("\n"):
        m = re.match(r"^\s*#{2,3}\s+(.*?)\s*$", l)
        if m:
            inside = heading_key(m.group(1)) == "quien es quien"
            declared = declared or inside
        elif inside:
            lines.append(l)
    reg = PeopleRegistry(declared=declared)
    two_names, two_accounts = set(), set()
    for l in lines:
        if not re.match(r"^\s*[-*]\s+\S", l):
            continue
        fields = [c.strip() for c in re.split(r"\s+·\s+", l.strip()[1:].strip()) if c.strip()]
        if not fields:
            continue
        p = Person(name=re.sub(r"\s*\([^)]*\)", "", re.sub(r"[*_`]", "", fields[0])).strip())
        if EMAIL.fullmatch(p.name.lower()):
            p.accounts.add(p.name.lower()); p.name = "?"
        elif EMAIL.search(p.name):
            reg.warnings.append(f"«{fields[0]}»: el nombre y la cuenta van separados por « · »")
        for c in fields[1:]:
            cl = c.lower()
            if EMAIL.fullmatch(cl):
                p.accounts.add(cl)
            elif re.search(r"\bbaja\b", cl):
                p.left_on = (re.search(r"20\d\d-\d\d-\d\d", c) or [""])[0] or "sí"
            elif re.match(r"^cuentas?\s*:", cl):
                p.accounts |= set(EMAIL.findall(cl))
            elif re.match(r"^(en\s+)?(google\s+)?drive\s*:", cl):
                p.drive_accounts |= set(EMAIL.findall(cl))
            elif re.match(r"^sin\s+cuenta\b", cl):
                p.no_account = True
            elif re.match(r"^sin\s+confirmar\b", cl):
                p.unconfirmed = True
            elif re.match(r"^tambi[eé]n\s*:", cl):
                p.aliases += [a.strip() for a in re.split(r"[,;]", c.split(":", 1)[1]) if a.strip()]
            elif re.match(r"^de\s*:", cl):
                p.organization = c.split(":", 1)[1].strip()
            elif re.match(r"^compartida\s+con\s*:", cl):
                p.shared_with = c.split(":", 1)[1].strip()
            elif re.match(r"^registra\s*:", cl):
                p.registered_by = c.split(":", 1)[1].strip()
            else:
                reg.warnings.append(f"«{p.name}»: no se entiende «{c}» (van un correo, «sin cuenta», «en Drive: correo», «también: nombre», «de: organización» o «baja AAAA-MM-DD»)")
        if p.no_account and p.accounts:
            reg.warnings.append(f"«{p.name}» dice «sin cuenta» y lleva una cuenta: se queda la cuenta")
            p.no_account = False
        if not p.accounts and not p.no_account and not p.left_on:
            reg.warnings.append(f"«{p.name}» no lleva ni su cuenta ni «sin cuenta»")
        reg.people.append(p)
        for n in ([p.name] if p.name != "?" else []) + p.aliases:
            k = name_key(n)
            if k in reg.by_name and reg.by_name[k] is not p:
                two_names.add(k)
                reg.warnings.append(f"«{n}» está dos veces: dos personas con el mismo nombre se distinguen con el segundo apellido o una inicial (mientras, ese nombre no es de nadie)")
            reg.by_name.setdefault(k, p)
        for c in p.accounts:
            if c in reg.by_account and reg.by_account[c] is not p:
                two_accounts.add(c)
                reg.warnings.append(f"la cuenta {c} está en dos líneas («{reg.by_account[c].name}» y «{p.name}»; mientras, no es de nadie)")
            reg.by_account.setdefault(c, p)
    for k in two_names:
        reg.by_name.pop(k, None)
    for c in two_accounts:
        reg.by_account.pop(c, None)
    return reg


def find_person(name_or_account: str, reg: PeopleRegistry) -> Optional[Person]:
    t = (name_or_account or "").strip()
    if EMAIL.fullmatch(t.lower()):
        return reg.by_account.get(t.lower())
    return reg.by_name.get(name_key(t))


def names_in(text: str, reg: Optional[PeopleRegistry] = None) -> list[str]:
    """The names of a cell or line («Colabora: Ana Ruiz, Luis Mejía»), split by «,» or «;», and by « y » / « e » only
    when the whole piece is not a registered name."""
    reg = reg or PeopleRegistry()
    t = re.sub(r"^\s*[-*]?\s*\**\s*(?:colabora[n]?|lo leen?|responsable)\s*\**\s*:\s*\**", "", text or "", flags=re.I)
    t = re.sub(r"\s*\([^)]*\)", "", t)
    out: list[str] = []
    for piece in re.split(r"[,;]", t):
        piece = piece.strip(" .*")
        if not piece or piece.lower() in ("—", "-", "nadie", "ninguno", "ninguna"):
            continue
        if find_person(piece, reg) is not None or not re.search(r"\s(?:y|e)\s", piece):
            out.append(piece)
        else:
            out += [x.strip(" .*") for x in re.split(r"\s+(?:y|e)\s+", piece) if x.strip(" .*")]
    return out


def accounts_of_names(text: str, reg: PeopleRegistry) -> tuple[set[str], list[str]]:
    out, missing = set(), []
    for n in names_in(text, reg):
        p = find_person(n, reg)
        if p is None:
            missing.append(n)
        elif not p.left_on:
            out |= p.accounts
    return out, missing


def account_cell(cell: str) -> tuple[set[str], set[str], Optional[str]]:
    """(responsible, collaborators, warning) of a «Cuenta» cell «resp@x · colabora: a@x, b@x» (up to 1.24). Fails closed."""
    text = (cell or "").lower()
    parts = _WORD_COLLABORATES.split(text, maxsplit=1)
    before = set(EMAIL.findall(parts[0]))
    after = set(EMAIL.findall(parts[1])) if len(parts) > 1 else set()
    warning = None
    if len(before) > 1:
        warning = "más de un correo antes de «colabora:»; nadie es responsable hasta que se corrija"
        before = set()
    elif not before:
        warning = "sin el correo del responsable"
    elif len(parts) > 1 and not re.search(r"\bcolabora\s*:", text):
        warning = "la palabra para quien colabora va escrita «colabora:»"
    return before, after, warning


def _people_columns(header: list[str]) -> dict:
    n = [heading_key(x) for x in header]
    pos = lambda *ns: next((i for i, x in enumerate(n) if x in ns), None)
    return {"responsible": pos("responsable", "dueno", "duena"), "account": pos("cuenta", "cuentas"),
            "collaborates": pos("colabora", "colaboran", "colaboradores", "colaboradoras")}


def row_accounts(header: list[str], cells: list[str], reg: PeopleRegistry) -> tuple[set[str], set[str], Optional[str]]:
    """(responsible, collaborators, warning) of an area row: from the «Cuenta» emails up to 1.24, from the «Colabora»
    names and the registry in 1.25. Same as fila_cuentas()."""
    col = _people_columns(header)
    cell = lambda i: cells[i] if i is not None and i < len(cells) else ""
    if col["account"] is not None or col["collaborates"] is None:
        return account_cell(cell(col["account"] if col["account"] is not None else 3))
    if not reg.declared:
        return set(), set(), "la tabla nombra a quien colabora por su nombre y guia.md no tiene «Quién es quién»"
    resp = re.sub(r"\s*\((?=[a-záéíóúñ`])[^)]*\)", "", cell(col["responsible"] if col["responsible"] is not None else 2))
    rn = names_in(resp, reg)
    warnings, of = [], set()
    if len(rn) > 1 and find_person(rn[0], reg) is not None:
        warnings.append(f"en Responsable, lo que sigue a «{rn[0]}» va en «Qué es»")
        rn = rn[:1]
    if len(rn) != 1:
        warnings.append("el responsable es una sola persona del registro" if rn else "sin responsable")
    else:
        p = find_person(rn[0], reg)
        if p is None:
            warnings.append(f"«{rn[0]}» no está en «Quién es quién»")
        elif p.left_on:
            warnings.append(f"«{p.name}» está de baja")
        elif p.accounts:
            of = set(p.accounts)
        elif p.registered_by and find_person(p.registered_by, reg) and find_person(p.registered_by, reg).accounts:
            of = set(find_person(p.registered_by, reg).accounts)
        else:
            warnings.append(f"«{p.name}» no tiene cuenta: o la tiene, o su línea dice «registra: Nombre» de quien escribe por ella")
    co, missing = accounts_of_names(cell(col["collaborates"]), reg)
    warnings += [f"«{n}» (Colabora) no está en «Quién es quién»" for n in missing]
    return of, co - of, "; ".join(warnings) or None


def provisional_people(who: str, reg: PeopleRegistry) -> list[tuple[str, str]]:
    """[(name, email)] of «Colabora: Name (email)» for someone not in the registry: the provisional entry (1.25)."""
    out: list[tuple[str, str]] = []
    if not reg.declared:
        return out
    for l in (who or "").split("\n"):
        if _LINE_COLLABORATES.match(l):
            for n, c in re.findall(r"([^,;(:]+?)\s*\(\s*(" + EMAIL.pattern + r")\s*\)", l):
                n = n.strip(" .*")
                if find_person(n, reg) is None and c.lower() not in reg.by_account:
                    out.append((n, c.lower()))
    return out


def collaborator_accounts(who: str, reg: Optional[PeopleRegistry] = None) -> set[str]:
    """The accounts of the «Colabora:» lines of a project's «Quién participa». Same as colaboran_en()."""
    reg = reg or PeopleRegistry()
    out: set[str] = set()
    for l in (who or "").split("\n"):
        if _LINE_COLLABORATES.match(l):
            if reg.declared:
                out |= accounts_of_names(l, reg)[0] | {c for _, c in provisional_people(l, reg)}
            else:
                out |= set(EMAIL.findall(l.lower()))
    return out


# ── guia.md ────────────────────────────────────────────────────────────────────────────────────────────────────────

def _area_columns(header: list[str]) -> dict:
    n = [re.sub(r"[*_`]", "", x).strip().lower() for x in header]
    pos = lambda *ns, default=None: next((i for i, x in enumerate(n) if x in ns), default)
    return {"responsible": pos("responsable", "dueño", "dueno", default=2), "account": pos("cuenta", "colabora", default=3),
            "readers": pos("quién la lee", "quien la lee", default=4), "access": pos("acceso"), "what": pos("qué es", "que es", default=1)}


def area_is_restricted(cells: list[str], header: list[str]) -> bool:
    """With an «Acceso» column (1.22+), its word; otherwise, or when it is empty or unclear, the «Quién la lee» rule.
    In 1.25 («Colabora» column) an unclear «Acceso» fails closed. Same as area_restringida() in abrir.py."""
    col = _area_columns(header)
    if col["access"] is not None and col["access"] < len(cells):
        v = cells[col["access"]]
        if re.match(r"^[\W_]*restringid[oa]s?\b", v, re.I):
            return True
        if re.match(r"^[\W_]*abiert[oa]s?\b", v, re.I):
            return False
    if _people_columns(header)["collaborates"] is not None:
        return True
    return is_restricted_cell(cells[col["readers"]] if col["readers"] < len(cells) else "")


def _table_rows(block: str) -> tuple[Optional[list[str]], list[list[str]]]:
    header, rows = None, []
    for l in block.split("\n"):
        s = l.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if re.match(r"^\|[\s:|-]+\|?\s*$", s):
            continue
        if header is None:
            header = cells
        else:
            rows.append(cells)
    return header, rows


def area_rows(guia: str, reg: PeopleRegistry) -> list[AreaRow]:
    header, rows = _table_rows(section(guia, "Áreas"))
    if header is None:
        return []
    col = _area_columns(header)
    pcol = _people_columns(header)
    out = []
    for cells in rows:
        m = re.search(r"`([^`/]+)/?`", cells[0]) if cells else None
        if not m:
            continue
        get = lambda i: cells[i] if i is not None and i < len(cells) else ""
        resp_acc, coll_acc, warning = row_accounts(header, cells, reg)
        collaborators = (names_in(get(pcol["collaborates"]), reg) if pcol["collaborates"] is not None and pcol["account"] is None
                         else sorted(coll_acc))
        out.append(AreaRow(
            slug=m.group(1), what=get(col["what"]), responsible=get(col["responsible"]),
            responsible_accounts=resp_acc, collaborators=collaborators, collaborator_accounts=coll_acc,
            readers=get(col["readers"]), access=get(col["access"]), restricted=area_is_restricted(cells, header),
            warnings=[warning] if warning else []))
    return out


def guia_line(guia: str, label: str) -> str:
    m = re.search(r"^\s*[-*]?\s*\**\s*" + label + r"\s*\**\s*:\s*(.+)$", guia or "", re.M | re.I)
    return m.group(1).strip() if m else ""


def timezone_of(guia: str, default: str = "America/Mexico_City") -> str:
    m = re.search(r"^\s*[-*]?\s*\**\s*zona horaria\s*\**\s*:\s*\**\s*`?\s*([A-Za-z0-9_+-]+(?:/[A-Za-z0-9_+-]+){0,2})",
                  guia or "", re.M | re.I)
    return m.group(1) if m and not m.group(1).startswith("[") else default


def method_line(first_line: str) -> tuple[Optional[tuple[int, ...]], Optional[str]]:
    m = re.search(r"versi[oó]n\s+(\d+(?:\.\d+)*)", first_line or "", re.I)
    h = re.search(r"huella\s+([0-9a-f]+)", first_line or "", re.I)
    return (tuple(int(x) for x in m.group(1).split(".")) if m else None), (h.group(1) if h else None)


def premises(text: str) -> list[Premise]:
    out = []
    for l in (text or "").split("\n"):
        m = re.match(r"^\s*-\s*(P\d+)\s*·\s*(.+)$", l)
        if not m:
            continue
        parts = [x.strip() for x in m.group(2).split("·")]
        rep = next((re.search(r"P\d+", x, re.I).group(0).upper() for x in parts[1:]
                    if re.match(r"reemplaza\b", x, re.I) and re.search(r"P\d+", x, re.I)), None)
        date = next((x for x in parts[1:] if re.fullmatch(r"20\d\d-\d\d-\d\d", x)), "")
        conf = next((x.split(":", 1)[1].strip() for x in parts[1:] if re.match(r"confirm[oó]\s*:", x, re.I)), "")
        out.append(Premise(id=m.group(1).upper(), text=parts[0], line=l.strip(), confirmed_by=conf, date=date, replaces=rep))
    return out


# ── Estatus ────────────────────────────────────────────────────────────────────────────────────────────────────────

_STATUS_FIELDS = {"se completo": "completed", "siguiente": "next", "falta decidir": "to_decide", "preocupa": "concern"}


def status(body: str, legacy: tuple[str, ...] = ("Estado actual", "En corto")) -> Optional[Status]:
    """The «Estatus» of proyecto.md or area.md, or the first legacy section present."""
    text, source = section(body, "Estatus"), "Estatus"
    if not text:
        source = next((n for n in legacy if section(body, n)), "")
        if not source:
            return None
        text = section(body, source)
    st = Status(source=source, text=text)
    m = re.search(r"Proyecto terminado el\s*(20\d\d-\d\d-\d\d)", text)
    if m:
        st.finished_on = m.group(1)
    if source != "Estatus":
        st.date = (dates_in(text.split("\n", 1)[0]) or [""])[0]
        return st
    lines = text.split("\n")
    first = lines[0] if lines else ""
    mh = re.match(r"^\s*(20\d\d-\d\d-\d\d)\s*·\s*(.*)$", first)
    if mh:
        st.date = mh.group(1)
        st.headline = re.sub(r"^\*\*(.*)\*\*$", r"\1", mh.group(2).strip())
    current = None
    for l in lines[1:]:
        mf = re.match(r"^\s*[-*]\s*\**\s*([^:*]+?)\s*(?::\s*\**|\**\s*:)\s*(.*)$", l)
        key = _STATUS_FIELDS.get(heading_key(mf.group(1))) if mf and not l.startswith("  ") else None
        if key:
            current = key
            rest = mf.group(2).strip()
            if key == "next":
                if rest:
                    st.next.append(rest)
            else:
                setattr(st, key, rest)
            continue
        if current == "next" and re.match(r"^\s{2,}[-*]\s+", l):
            st.next.append(re.sub(r"^\s+[-*]\s+", "", l).strip())
        elif current and l.strip() and current != "next":
            setattr(st, current, (getattr(st, current) + "\n" + l.strip()).strip())
    return st


def area_priorities(body: str) -> list[str]:
    """«Siguiente» of the area's Estatus (1.22+), or «Prioridades ahora» (1.21). The board's queue cites them by number."""
    est = section(body, "Estatus")
    if est:
        out, inside = [], False
        for l in est.split("\n"):
            if re.match(r"^\s*[-*]\s*\**\s*Siguiente\s*:?\s*\**\s*:?\s*(.*)$", l, re.I):
                rest = re.sub(r"^\s*[-*]\s*\**\s*Siguiente\s*:?\s*\**\s*:?\s*", "", l, flags=re.I).strip()
                if rest:
                    out.append(rest)
                inside = True; continue
            if inside and re.match(r"^\s{2,}[-*]\s+", l):
                out.append(re.sub(r"^\s+[-*]\s+", "", l).strip()); continue
            if inside and l.strip():
                inside = False
        return out
    return bullets(section(body, "Prioridades ahora"))


# ── decisiones.md and sesiones.md ──────────────────────────────────────────────────────────────────────────────────

def decision_ref(text: str) -> Optional[DecisionRef]:
    """«area/project#2026-10-15-2 (…)» or «premisa P3»; None for an empty field."""
    t = (text or "").strip()
    if not t:
        return None
    mp = re.search(r"\bpremisa\s+(P\d+)", t, re.I)
    if mp:
        return DecisionRef("premisa", mp.group(1).upper(), t)
    m = re.search(r"`?([a-z0-9][\w.-]*)/([a-z0-9][\w.-]*)#(20\d\d-\d\d-\d\d(?:-\d+)?)", t)
    return DecisionRef(f"{m.group(1)}--{m.group(2)}", m.group(3), t) if m else DecisionRef(None, None, t)


_DECISION_FIELDS = (("decidió:", "decided_by"), ("decidio:", "decided_by"), ("por qué:", "why"), ("por que:", "why"),
                    ("descartamos:", "discarded"), ("descartado:", "discarded"), ("afecta a:", "affects"),
                    ("planteó:", "raised_by"), ("planteo:", "raised_by"), ("cuestiona a:", "challenges"),
                    ("responde a:", "responds_to"), ("reemplaza:", "replaces"), ("reemplaza a:", "replaces"))


def decisions(text: str, live: Optional[int] = None) -> list[Decision]:
    """The entries of decisiones.md, newest first. With `live`, entries after the first `live` come from an archive."""
    raw: list[dict] = []
    for p in re.split(r"^## ", text or "", flags=re.M)[1:]:
        head, _, body = p.partition("\n")
        mm = re.match(r"(20\d\d-\d\d-\d\d)\s*·\s*(.*)", head.strip())
        date, title = (mm.group(1), mm.group(2).strip()) if mm else ((dates_in(head) or [""])[0], head.strip())
        f = {k: "" for _, k in _DECISION_FIELDS}
        current = None
        for l in body.split("\n"):
            s = l.strip()
            low = s.lower()
            hit = next((k for pre, k in _DECISION_FIELDS if low.startswith(pre)), None)
            if hit:
                current = hit; f[hit] = s.split(":", 1)[1].strip()
            elif current and s:
                f[current] += "\n" + s
        raw.append({"date": date, "title": title, **f})
    out: list[Decision] = []
    for i, r in enumerate(raw):
        d = Decision(id="", date=r["date"], title=r["title"], decided_by=r["decided_by"], why=r["why"],
                     discarded=r["discarded"], affects=r["affects"], raised_by=r["raised_by"],
                     challenges=decision_ref(r["challenges"]), responds_to=decision_ref(r["responds_to"]),
                     replaces=decision_ref(r["replaces"]),
                     pending_confirmation=bool(re.search(r"\(pendiente de confirma(r|ción)\)", r["decided_by"].lower())),
                     archived=live is not None and i >= live)
        if r["challenges"] or re.match(r"cuestionamiento\b", d.title, re.I):
            d.kind = "challenge"
            t = re.sub(r"^cuestionamiento\s*:\s*", "", d.title, flags=re.I) or d.title
            d.title = t[:1].upper() + t[1:]
        out.append(d)
    count: dict[str, int] = {}
    for d in reversed(out):
        if not valid_date(d.date):
            continue
        n = count[d.date] = count.get(d.date, 0) + 1
        d.id = d.date + ("" if n == 1 else f"-{n}")
    out.sort(key=lambda d: d.date, reverse=True)
    return out


def sessions(text: str, live: Optional[int] = None) -> list[SessionEntry]:
    raw = re.split(r"^## ", text or "", flags=re.M)[1:]
    out: list[SessionEntry] = []
    for i, p in enumerate(raw):
        head, _, body = p.partition("\n")
        e = SessionEntry(n=len(raw) - 1 - i, date=(dates_in(head) or [""])[0], title=head.strip(),
                         archived=live is not None and i >= live)
        current = None
        for l in body.split("\n"):
            s = l.strip()
            low = s.lower()
            m_doc = re.match(r"^(escribió|escribio|publicó|publico)\s*:\s*(.*)$", low)
            if m_doc:
                current = None
                target = e.wrote if m_doc.group(1).startswith("escrib") else e.published
                for r in s.split(":", 1)[1].split(","):
                    r = r.strip().strip("`").strip()
                    if r and "restringido" not in r.split("/") and r not in target and len(target) < 20:
                        target.append(r[:160])
                continue
            if low.startswith("trabajamos en:") or low.startswith("tema:"):
                current = "topic"; e.topic = s.split(":", 1)[1].strip()
            elif low.startswith("avances:"):
                current = "progress"; e.progress = s.split(":", 1)[1].strip()
            elif low.startswith("pendiente:"):
                current = "pending"; e.pending = s.split(":", 1)[1].strip()
            elif low.startswith("sesión de:") or low.startswith("sesion de:"):
                current = None
                rest = s.split(":", 1)[1].strip()
                e.by = re.split(r"\s+[·\-–—]\s+|\s*\(", rest, maxsplit=1)[0].strip()[:80]
                mv = re.search(r"plugin\s+(\d+(?:\.\d+)+)", rest)
                e.plugin_version = mv.group(1) if mv else ""
            elif current and s:
                setattr(e, current, getattr(e, current) + "\n" + s)
        out.append(e)
    out.sort(key=lambda e: e.date, reverse=True)
    return out


# ── area.md and proyecto.md ────────────────────────────────────────────────────────────────────────────────────────

def project_index(area_text: str) -> dict[str, IndexEntry]:
    """The «Proyectos» block of area.md: one entry per «- `slug/` — description», with its deliverable sub-lines."""
    idx: dict[str, IndexEntry] = {}
    current = None
    for l in section(area_text, "Proyectos").split("\n"):
        m1 = re.match(r"^- `([^`]+?)/?`\s*[—–:-]?\s*(.*)$", l)
        if m1 and ("/" in m1.group(1) or m1.group(1).startswith(".")):
            current = None; continue
        if m1:
            current = m1.group(1)
            desc = m1.group(2).strip()
            idx[current] = IndexEntry(slug=current, description=desc, restricted=starts_restricted(desc))
            continue
        m2 = re.match(r"^\s+- (.*)$", l)
        if m2 and current:
            item = m2.group(1).strip()
            m3 = re.match(r"^([\w\-, ]+?)\s+[—–-]\s+(.*?)(?:\s*·\s*actualizado\s*(20\d\d-\d\d-\d\d))?\s*$", item)
            if m3 and m3.group(3):
                for stem in [s.strip() for s in m3.group(1).split(",")]:
                    idx[current].deliverables[stem] = {"description": m3.group(2).strip(), "updated": m3.group(3)}
            else:
                idx[current].notes.append(item)
    return idx


def who_takes_part(body: str) -> tuple[str, list[str], str, str]:
    """(responsible, collaborator lines' names, consumers, raw section) of «Quién participa»."""
    raw = section(body, "Quién participa")
    resp, coll, cons = "", [], ""
    for l in raw.split("\n"):
        m = re.match(r"^\s*[-*]?\s*\**\s*(responsable|dueño|dueno|dueña)\s*\**\s*:\s*(.+)$", l, re.I)
        if m and not resp:
            resp = re.sub(r"\s*\([^)]*\)\s*$", "", m.group(2).strip()).strip()
        elif _LINE_COLLABORATES.match(l):
            coll += names_in(l)
        else:
            mc = re.match(r"^\s*[-*]?\s*consumen esto\s*:\s*(.+)$", l, re.I)
            if mc:
                cons = mc.group(1).strip()
    return resp, coll, cons, raw


def project_file(area: str, slug: str, text: str) -> Project:
    fm, body = frontmatter(text or "")
    resp, coll, cons, _ = who_takes_part(body)
    steps_ = [Step(text=b, dates=dates_in(b)) for b in bullets(section(body, "Siguientes pasos"))]
    return Project(area=area, slug=slug, state=fm.get("estado") or None, updated=fm.get("actualizado") or None,
                   title=h1(body), objective=section(body, "Objetivo"), done_means=section(body, "Terminado significa"),
                   scope=section(body, "Alcance"), status=status(body), steps=steps_, responsible=resp,
                   collaborators=coll, consumers=cons)


def area_file(slug: str, text: str) -> Area:
    fm, body = frontmatter(text or "")
    resp, _, _, _ = who_takes_part(body)
    return Area(slug=slug, state=fm.get("estado") or None, updated=fm.get("actualizado") or None, title=h1(body),
                what=section(body, "Qué es"), status=status(body, legacy=("Panorama",)),
                priorities=area_priorities(body), responsible=resp, index=project_index(text or ""))


def deliverable(file: str, text: Optional[str], index: Optional[IndexEntry]) -> Deliverable:
    stem = file.rsplit(".", 1)[0] if "." in file else file
    d = Deliverable(file=file, name=stem, format=file.rsplit(".", 1)[1] if "." in file else "")
    if text is not None and file.endswith(".md"):
        fm, body = frontmatter(text)
        d.title = h1(body) or None
        d.state = fm.get("estado") or None
        d.updated = fm.get("actualizado") or None
        if isinstance(fm.get("basado_en"), list):
            d.based_on = [re.sub(r"^\./", "", b) for b in fm["basado_en"]]
        d.replaced_by = fm.get("reemplazado_por") or None
        ap = fm.get("aportacion") if isinstance(fm.get("aportacion"), str) and fm["aportacion"].strip() else fm.get("afirma")
        if isinstance(ap, str) and ap.strip():
            d.contribution = ap.strip()[:240]
    ref = index.deliverables.get(stem) if index else None
    if ref is None and index and stem.endswith("-en"):
        ref = index.deliverables.get(stem[:-3])
    if ref:
        d.description = ref["description"]
        d.updated = d.updated or ref["updated"]
    return d


def context_owner_name(line: str) -> str:
    """The name of «Contexto común: Name», without the account in parentheses or what follows a comma, stop or dash."""
    t = re.sub(r"\s*\([^)]*\)", "", (line or "").split(":", 1)[-1])
    return re.split(r",|\.\s|\.$|\s[—–-]\s|;", t.strip())[0].strip()


def context_owner_accounts(line: str, reg: PeopleRegistry) -> set[str]:
    """The account in parentheses (up to 1.24) or the registry's for that name (1.25)."""
    c = set(EMAIL.findall((line or "").split(":", 1)[-1].lower()))
    if c:
        return c
    p = find_person(context_owner_name(line), reg)
    return set(p.accounts) if p and not p.left_on else set()


def name_of_account(account: str, reg: PeopleRegistry) -> str:
    p = reg.by_account.get((account or "").lower())
    return p.name if p and p.name != "?" else ""


# ── guia.md's first paragraph, and archived registers ──────────────────────────────────────────────────────────────

ABOUT_THE_FOLDER = r"`(?:metodo|guia)\.md`|plugin `memoria`|Aquí solo está lo nuestro"


def drop_folder_talk(sentences: list[str], rx: str = ABOUT_THE_FOLDER) -> list[str]:
    """The sentences of guia.md's first paragraph without what talks about the folder or the method. Of a sentence joined
    by «;» to one that does not, the other stays (not split by a «;» in parentheses); within each part, what comes before
    the comma, colon or dash that opens the folder talk stays if it has three words or more. Same as sin_carpeta()."""
    out = []
    for f in sentences:
        if not re.search(rx, f):
            out.append(f); continue
        keep = []
        for c in [c.strip() for c in re.split(r";(?![^()]*\))", f)]:
            m = re.search(rx, c) if c else None
            if c and not m:
                keep.append(c); continue
            cuts = [s.start() for s in re.finditer(r"[,:—](?![^()]*\))", c[:m.start()] if m else "")]
            t = c[:cuts[-1]].strip() if cuts else ""
            if len(t.split()) >= 3 and not re.search(rx, t):
                keep.append(t)
        if keep:
            t = "; ".join(keep); t = t[0].upper() + t[1:]
            out.append(t if t[-1] in ".!?" else t + ".")
    return out


ARCHIVED = re.compile(r"^(sesiones|decisiones)-(20\d\d)(?:-(\d+))?\.md$")


def archived_names(names: list[str], register: str, year) -> list[str]:
    """Of the names in a project folder, the archives of a register («sesiones» or «decisiones») from `year` - 1 on,
    newest first. Older ones are not read whole (escribir.md, section 8)."""
    seen = []
    for n in names:
        m = ARCHIVED.match(n)
        if m and m.group(1) == register and int(m.group(2)) >= int(year) - 1:
            seen.append((int(m.group(2)), int(m.group(3) or 1), n))
    return [n for _, _, n in sorted(seen, reverse=True)]


def with_archives(live: Optional[str], archives: list[Optional[str]]) -> tuple[str, int]:
    """(text, entries of the live register): the live register followed by the entries of its archives, as if they had
    not been archived, so every decision keeps its identifier. Same as con_archivados()."""
    parts = [live or ""]
    for t in archives:
        m = re.search(r"^## ", t or "", re.M)
        if m:
            parts.append((t or "")[m.start():])
    return "\n\n".join(p.strip("\n") for p in parts if p.strip()) + "\n", len(re.findall(r"^## ", live or "", re.M))
