"""The rules the plugin scripts share: who writes (the people registry, the area table's accounts, «Colabora:»), what is
restricted, guia.md's first paragraph, the archived registers and the minimum plugin version that may write. Pure functions: no I/O, no globals, no clock.

This is what `compat` reaches, and so what `inline.py` puts inside the scripts; the parsers of the other method files are
in `parse`, which imports these and re-exports them. The words that decide restricted come from the language pack
(review of 1.25.2, finding 9). `tests/test_compat.py` and `tests/test_access.py` compare these with the 1.25.1 rules
frozen in `tests/reference/`.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Optional

from .language import ES, Pack
from .records import PeopleRegistry, Person

EMAIL = re.compile(r"[\w.+'-]+@[\w-]+(?:\.[\w-]+)*")
_WORD_COLLABORATES = re.compile(r"\bco-?labor\w*\s*:?", re.I)
_LINE_COLLABORATES = re.compile(r"^\s*[-*]?\s*\**\s*colabora[n]?\s*\**\s*:", re.I)


# ── names ──────────────────────────────────────────────────────────────────────────────────────────────────────────

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

def is_restricted_cell(cell: str, lang: Pack = ES) -> bool:
    """«Quién la lee» declares the area restricted: the word at the start («Restringida: …»), or «restringida» on its
    own elsewhere («Dirección (restringida)») and not negated («nunca restringida», «antes restringida»)."""
    c = cell or ""
    if re.match(r"^[\W_]*" + lang.restricted_lead + r"\b", c, re.I):
        return True
    return bool(re.search(r"\b" + lang.restricted_inline + r"\b", c, re.I)) and not re.search(
        r"\b(?:" + "|".join(lang.restricted_negations) + r")\s+(?:[^\s]+\s+)?" + lang.restricted_stem, c, re.I)


def starts_restricted(line: str, lang: Pack = ES) -> bool:
    """An index line «- `x/` — restringido: …» marks the project restricted."""
    return bool(re.match(r"^[\W_]*" + lang.restricted_line + r"\b", line or "", re.I))


def access_word(cell: str, lang: Pack = ES) -> Optional[bool]:
    """What an «Acceso» cell says: True for «Restringida», False for «Abierta», None for anything else (empty, unclear)."""
    if re.match(r"^[\W_]*" + lang.restricted_lead + r"\b", cell or "", re.I):
        return True
    if re.match(r"^[\W_]*" + lang.open_lead + r"\b", cell or "", re.I):
        return False
    return None


def _area_columns(header: list[str], lang: Pack = ES) -> dict:
    n = [re.sub(r"[*_`]", "", x).strip().lower() for x in header]
    default = {"responsible": 2, "account": 3, "readers": 4, "access": None, "what": 1}
    return {k: next((i for i, x in enumerate(n) if x in names), default[k]) for k, names in lang.area_columns.items()}


def area_is_restricted(cells: list[str], header: list[str], lang: Pack = ES) -> bool:
    """Whether an area row of guia.md is restricted: the one rule that the opening, the board, the permissions check and the
    migration use (verificar.sh reads only the «Acceso» word, with access_word) (review of 1.25.2, finding 10). With an «Acceso» column (1.22+), its word; otherwise,
    or when it is empty or unclear, restricted if the table has a «Colabora» column (1.25: «Quién la lee» no longer
    carries «Restringida:», so it fails closed), and else the «Quién la lee» rule. Same as area_restringida() in the
    1.25.1 abrir.py, frozen in tests/reference/acceso_1_25_1.py."""
    col = _area_columns(header, lang)
    if col["access"] is not None and col["access"] < len(cells):
        word = access_word(cells[col["access"]], lang)
        if word is not None:
            return word
    if _people_columns(header, lang)["collaborates"] is not None:
        return True
    return is_restricted_cell(cells[col["readers"]] if col["readers"] < len(cells) else "", lang)


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


def _people_columns(header: list[str], lang: Pack = ES) -> dict:
    n = [heading_key(x) for x in header]
    return {k: next((i for i, x in enumerate(n) if x in names), None) for k, names in lang.people_columns.items()}


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


# ── «Contexto común» ───────────────────────────────────────────────────────────────────────────────────────────────

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


# ── the minimum plugin version (1.26) ────────────────────────────────────────────────────────────────────────────

_VERSION = re.compile(r"(?<![\d.])(\d+)\.(\d+)(?:\.(\d+))?(?!\.?\d)")


def version_tuple(text: str) -> Optional[tuple]:
    """«1.26» or «1.26.0» (the first version in `text`) as (1, 26, 0); None without one."""
    m = _VERSION.search(text or "")
    return (int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)) if m else None


def minimum_plugin_version(guia: str, lang: Pack = ES) -> tuple[bool, Optional[tuple]]:
    """(declared, version) from the section «## Versión mínima del plugin» of guia.md, written by the migration that needs
    it. (False, None): no section, anyone may write. (True, None): a section with no version in its first paragraph,
    which nobody may write under until it is fixed (fail closed: a typo must not let an old plugin through)."""
    m = re.search(r"^##[ \t]+" + re.escape(lang.minimum_plugin) + r"[ \t]*$(.*?)(?=^##[ \t]|\Z)", guia or "", re.M | re.S)
    if not m:
        return False, None
    first = next((b for b in re.split(r"\n\s*\n", m.group(1).strip()) if b.strip()), "")
    return True, version_tuple(first)


def plugin_may_write(plugin_version: str, guia: str, lang: Pack = ES) -> tuple[str, Optional[tuple]]:
    """Whether a plugin may write in the root of this guia.md: ("ok", minimum or None), ("below", minimum),
    ("unreadable", None) for a section with no version, or ("unknown", minimum) for a plugin version that does not parse.
    Reading is never gated; only writing (decision of 2026-11-08)."""
    declared, minimum = minimum_plugin_version(guia, lang)
    if not declared:
        return "ok", None
    if minimum is None:
        return "unreadable", None
    mine = version_tuple(plugin_version)
    if mine is None:
        return "unknown", minimum
    return ("ok" if mine >= minimum else "below"), minimum
