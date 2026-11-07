"""Text of one method file -> records. Pure functions: no I/O, no globals, no clock.

Ported from the plugin scripts with the same rules. The rules the scripts already take from the package (who writes,
what is restricted, the first paragraph of guia.md, the archived registers) are in `rules`, re-exported here; the rest
(decisions, sessions, Estatus, the area index, deliverables) the scripts still carry as their own copies, and
`tests/test_parity.py` runs those copies and these on the same inputs and fails on any difference.
"""
from __future__ import annotations

import datetime
import re
import unicodedata
from typing import Optional

from .language import ES, Pack
from .records import (
    Area, AreaRow, Decision, DecisionRef, Deliverable, IndexEntry, PeopleRegistry, Premise, Project, SessionEntry,
    Status, Step,
)
# the shared rules live in rules.py (what the scripts carry); re-exported so parse.X keeps naming every rule
from .rules import (  # noqa: F401
    ABOUT_THE_FOLDER, ARCHIVED, EMAIL, _LINE_COLLABORATES, _WORD_COLLABORATES, _area_columns, _people_columns,
    access_word, account_cell, accounts_of_names, archived_names, area_is_restricted, collaborator_accounts,
    context_owner_accounts, context_owner_name, drop_folder_talk, find_person, heading_key, is_restricted_cell,
    name_key, name_of_account, names_in, people_registry, provisional_people, row_accounts, starts_restricted,
    with_archives,
)



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


# ── guia.md ────────────────────────────────────────────────────────────────────────────────────────────────────────

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


def area_rows(guia: str, reg: PeopleRegistry, lang: Pack = ES, warnings: Optional[list] = None) -> list[AreaRow]:
    """The rows of the «Áreas» table. The slug is the first cell without backticks and the trailing slash, as the 1.25.1
    generator reads it; a row with fewer cells than the header needs is left out and said in `warnings`, so its area has
    no row and loads closed."""
    header, rows = _table_rows(section(guia, lang.areas))
    if header is None:
        return []
    col = _area_columns(header, lang)
    pcol = _people_columns(header, lang)
    needed = max(v for v in col.values() if v is not None) + 1
    # Stricter than the scripts' 1.25.1 rule, for the server only (review of 1.25.3): a header in which none of the pack's
    # column names appears (another language, a misspelling) is read by position and could read a restricted area open,
    # and so could an «Acceso» word the pack does not know. Both load closed, with a warning.
    norm = [re.sub(r"[*_`]", "", x).strip().lower() for x in header]
    unknown_header = not any(x in names for names in lang.area_columns.values() for x in norm)
    if unknown_header and warnings is not None:
        warnings.append("ninguna columna de la tabla de áreas lleva un nombre conocido: todas las áreas se leen restringidas")
    out = []
    # A slug on two rows, counted over every row (a short one too) and compared as macOS, Drive and Windows compare
    # names (review of 1.25.6, finding 3): which row wins would decide whether a restricted area reads open.
    slug_key = lambda c: unicodedata.normalize("NFC", c.strip("`").rstrip("/")).casefold()
    counts: dict[str, int] = {}
    for cells in rows:
        if cells and cells[0].strip("`").rstrip("/"):
            counts[slug_key(cells[0])] = counts.get(slug_key(cells[0]), 0) + 1
    for cells in rows:
        if not cells or not cells[0].strip("`").rstrip("/"):
            continue
        if len(cells) < needed:
            if warnings is not None:
                warnings.append(f"la fila «{cells[0].strip('`')}» de la tabla de áreas tiene {len(cells)} columnas y hacen falta {needed}")
            continue
        get = lambda i: cells[i] if i is not None and i < len(cells) else ""
        resp_acc, coll_acc, warning = row_accounts(header, cells, reg)
        collaborators = (names_in(get(pcol["collaborates"]), reg) if pcol["collaborates"] is not None and pcol["account"] is None
                         else sorted(coll_acc))
        out.append(AreaRow(
            slug=cells[0].strip("`").rstrip("/"), what=get(col["what"]), responsible=get(col["responsible"]),
            responsible_accounts=resp_acc, collaborators=collaborators, collaborator_accounts=coll_acc,
            readers=get(col["readers"]), access=get(col["access"]),
            restricted=(unknown_header or area_is_restricted(cells, header, lang)
                        or (col["access"] is not None and get(col["access"]).strip() != "" and access_word(get(col["access"]), lang) is None)),
            warnings=[warning] if warning else []))
    # The area keeps its first full row, loads closed, and the guide is said to need fixing (review of consultar, finding 2)
    seen: dict[str, AreaRow] = {}
    for row in out:
        seen.setdefault(slug_key(row.slug), row)
    for k, n in counts.items():
        if n > 1:
            if k in seen:
                seen[k].restricted = True
            if warnings is not None:
                warnings.append(f"el área «{k}» tiene {n} filas en la tabla de áreas: se lee restringida hasta que quede una")
    return list(seen.values())


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

def status(body: str, legacy: Optional[tuple] = None, lang: Pack = ES) -> Optional[Status]:
    """The «Estatus» of proyecto.md or area.md, or the first legacy section present (the project's by default)."""
    legacy = lang.status_legacy_project if legacy is None else legacy
    text, source = section(body, lang.status), lang.status
    if not text:
        source = next((n for n in legacy if section(body, n)), "")
        if not source:
            return None
        text = section(body, source)
    st = Status(source=source, text=text)
    m = re.search(re.escape(lang.finished_marker) + r"\s*(20\d\d-\d\d-\d\d)", text)
    if m:
        st.finished_on = m.group(1)
    if source != lang.status:
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
        key = lang.status_fields.get(heading_key(mf.group(1))) if mf and not l.startswith("  ") else None
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


def area_priorities(body: str, lang: Pack = ES) -> list[str]:
    """«Siguiente» of the area's Estatus (1.22+), or «Prioridades ahora» (1.21). The board's queue cites them by number."""
    est = section(body, lang.status)
    nxt = next((k for k, v in lang.status_fields.items() if v == "next"), "siguiente")
    if est:
        out, inside = [], False
        for l in est.split("\n"):
            if re.match(r"^\s*[-*]\s*\**\s*" + nxt + r"\s*:?\s*\**\s*:?\s*(.*)$", l, re.I):
                rest = re.sub(r"^\s*[-*]\s*\**\s*" + nxt + r"\s*:?\s*\**\s*:?\s*", "", l, flags=re.I).strip()
                if rest:
                    out.append(rest)
                inside = True; continue
            if inside and re.match(r"^\s{2,}[-*]\s+", l):
                out.append(re.sub(r"^\s+[-*]\s+", "", l).strip()); continue
            if inside and l.strip():
                inside = False
        return out
    return bullets(section(body, lang.priorities_legacy))


# ── decisiones.md and sesiones.md ──────────────────────────────────────────────────────────────────────────────────

def decision_ref(text: str, here: Optional[str] = None) -> Optional[DecisionRef]:
    """«area/project#2026-10-15-2 (…)», «premisa P3», or the same project's bare «#2026-10-15-2» (escribir.md, section 4),
    which takes `here` ("area--project") as its project; None for an empty field."""
    t = (text or "").strip()
    if not t:
        return None
    mp = re.search(r"\bpremisa\s+(P\d+)", t, re.I)
    if mp:
        return DecisionRef("premisa", mp.group(1).upper(), t)
    # «area/project#id», also with the register's file («…/decisiones.md#id», «…/decisiones-2026.md#id») and in any case
    # (review of 1.25.6, finding 6); slugs are compared lowercased
    m = re.search(r"(?<![\w.-])([a-z0-9][\w.-]*)/([a-z0-9][\w.-]*?)(?:/[\w.-]+\.md)?#(20\d\d-\d\d-\d\d(?:-\d+)?)", t, re.I)
    if m:
        return DecisionRef(f"{m.group(1).lower()}--{m.group(2).lower()}", m.group(3), t)
    h_area = (here or "").replace("/", "--").partition("--")[0]
    # «project#id», relative to the current area
    mp2 = re.search(r"(?<![\w./-])([a-z0-9][\w-]*)#(20\d\d-\d\d-\d\d(?:-\d+)?)", t, re.I)
    if mp2 and h_area and not re.fullmatch(r"[\w-]+\.md", mp2.group(1), re.I):
        return DecisionRef(f"{h_area}--{mp2.group(1).lower()}", mp2.group(2), t)
    # the same project: «#id» or «decisiones.md#id»
    mb = re.search(r"(?:(?<![\w/.-])|(?<=\.md))#(20\d\d-\d\d-\d\d(?:-\d+)?)\b", t)
    if mb and here:
        return DecisionRef(here.replace("/", "--"), mb.group(1), t)
    return DecisionRef(None, None, t)


def decisions(text: str, live: Optional[int] = None, lang: Pack = ES, here: Optional[str] = None) -> list[Decision]:
    """The entries of decisiones.md, newest first. With `live`, entries after the first `live` come from an archive.
    `here` ("area--project") resolves the bare «#AAAA-MM-DD» references to this project."""
    raw: list[dict] = []
    for p in re.split(r"^## ", text or "", flags=re.M)[1:]:
        head, _, body = p.partition("\n")
        mm = re.match(r"(20\d\d-\d\d-\d\d)\s*·\s*(.*)", head.strip())
        date, title = (mm.group(1), mm.group(2).strip()) if mm else ((dates_in(head) or [""])[0], head.strip())
        f = {k: "" for _, k in lang.decision_fields}
        current = None
        for l in body.split("\n"):
            s = l.strip()
            low = s.lower()
            hit = next((k for pre, k in lang.decision_fields if low.startswith(pre)), None)
            if hit:
                current = hit; f[hit] = s.split(":", 1)[1].strip()
            elif current and s:
                f[current] += "\n" + s
        raw.append({"date": date, "title": title, **f})
    out: list[Decision] = []
    for i, r in enumerate(raw):
        d = Decision(id="", date=r["date"], title=r["title"], decided_by=r["decided_by"], why=r["why"],
                     discarded=r["discarded"], affects=r["affects"], raised_by=r["raised_by"],
                     challenges=decision_ref(r["challenges"], here), responds_to=decision_ref(r["responds_to"], here),
                     replaces=decision_ref(r["replaces"], here),
                     pending_confirmation=bool(re.search(lang.pending_confirmation, r["decided_by"].lower())),
                     archived=live is not None and i >= live)
        if r["challenges"] or re.match(lang.challenge_title + r"\b", d.title, re.I):
            d.kind = "challenge"
            t = re.sub(r"^" + lang.challenge_title + r"\s*:\s*", "", d.title, flags=re.I) or d.title
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


def sessions(text: str, live: Optional[int] = None, lang: Pack = ES, headers_only: bool = False) -> list[SessionEntry]:
    """The entries of sesiones.md, newest first. With `headers_only` (what a reader outside the session may see: review
    of consultar, finding 1), each entry keeps its heading, the first line of «Tema», who wrote it and «Escribió» /
    «Publicó», and nothing of its body: no «Avances», no «Pendiente», no line that follows a field."""
    docs = "|".join(re.escape(x) for x in lang.session_wrote + lang.session_published)
    raw = re.split(r"^## ", text or "", flags=re.M)[1:]
    hidden = {lang.workshop, lang.sources}   # with headers_only, «Escribió» leaves out what an outside reader may not open
    out: list[SessionEntry] = []
    for i, p in enumerate(raw):
        head, _, body = p.partition("\n")
        e = SessionEntry(n=len(raw) - 1 - i, date=(dates_in(head) or [""])[0], title=head.strip(),
                         archived=live is not None and i >= live)
        current = None
        other_field = False
        for l in body.split("\n"):
            s = l.strip()
            low = s.lower()
            m_doc = re.match(r"^(" + docs + r")\s*:\s*(.*)$", low)
            if m_doc:
                current = None
                other_field = True
                target = e.wrote if m_doc.group(1) in lang.session_wrote else e.published
                for r in s.split(":", 1)[1].split(","):
                    r = r.strip().strip("`").strip()
                    folders = {unicodedata.normalize("NFC", x).casefold() for x in r.replace("\\", "/").split("/")}
                    if r and lang.restricted not in folders and not (headers_only and folders & hidden) \
                            and r not in target and len(target) < 20:
                        target.append(r[:160])
                continue
            if low.startswith(lang.session_topic):
                if headers_only and (e.topic or other_field):
                    current = None   # only the first «Tema» before any other field is the heading's (finding 5)
                    continue
                current = "topic"; e.topic = s.split(":", 1)[1].strip()
            elif low.startswith(lang.session_progress):
                other_field = True
                current = "progress"; e.progress = s.split(":", 1)[1].strip()
            elif low.startswith(lang.session_pending):
                other_field = True
                current = "pending"; e.pending = s.split(":", 1)[1].strip()
            elif low.startswith(lang.session_by):
                current = None
                other_field = True
                rest = s.split(":", 1)[1].strip()
                e.by = re.split(r"\s+[·\-–—]\s+|\s*\(", rest, maxsplit=1)[0].strip()[:80]
                mv = re.search(r"\b" + re.escape(lang.writers.get("plugin", "plugin")) + r"\s+(\d+(?:\.\d+)+)", rest)
                e.plugin_version = mv.group(1) if mv else ""
                ms = re.search(r"\b" + re.escape(lang.writers.get("server", "servidor")) + r"\s+(\d+(?:\.\d+)+)", rest)
                e.server_version = ms.group(1) if ms else ""
            elif current and s:
                setattr(e, current, getattr(e, current) + "\n" + s)
        if headers_only:
            e.topic, e.progress, e.pending = e.topic.split("\n", 1)[0][:300], "", ""
        out.append(e)
    out.sort(key=lambda e: e.date, reverse=True)
    return out


# ── area.md and proyecto.md ────────────────────────────────────────────────────────────────────────────────────────

def _slug_key(slug: str) -> str:
    """How two spellings of a project's folder compare: NFC, casefold, and the separators and dots a path cleaning
    drops («secreto\\», «secreto/.», «secreto » name the same folder as «secreto»)."""
    t = unicodedata.normalize("NFC", slug).replace("\\", "/").strip()
    while t and t[-1] in "/. ":
        t = t[:-1]
    return t.casefold()


def project_index(area_text: str, lang: Pack = ES, warnings: Optional[list] = None) -> dict[str, IndexEntry]:
    """The «Proyectos» block of area.md: one entry per «- `slug/` — description», with its deliverable sub-lines.

    A slug on two lines, compared as macOS, Drive and Windows compare names (NFC, casefold), keeps its first line and
    reads restricted, with a warning: which line won would decide whether a restricted project reads open (second
    review of consultar, finding 1), the same rule as a slug on two rows of the guide's area table."""
    idx: dict[str, IndexEntry] = {}
    by_key: dict[str, str] = {}
    twice: set = set()
    current = None
    for l in section(area_text, lang.projects).split("\n"):
        m1 = re.match(r"^- `([^`]+?)/?`\s*[—–:-]?\s*(.*)$", l)
        if m1 and ("/" in m1.group(1) or m1.group(1).startswith(".")):
            current = None; continue
        if m1:
            slug, desc = m1.group(1), m1.group(2).strip()
            key = _slug_key(slug)
            if key in by_key:
                current = by_key[key]
                if key not in twice and warnings is not None:
                    warnings.append(f"el proyecto «{current}» está dos veces en el índice de su área: se lee restringido hasta que quede una línea")
                idx[current].restricted = True
                twice.add(key)
                continue
            by_key[key] = current = slug
            # a slug that is not one plain folder name («secreto\\», «secreto.», a trailing space) can reach a real
            # folder through the storage's path cleaning: it reads restricted (review of 1.25.7, finding 2)
            plain = slug == slug.strip() and not slug.endswith(".") and "\\" not in slug
            idx[current] = IndexEntry(slug=current, description=desc,
                                      restricted=starts_restricted(desc, lang) or not plain)
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
    # A project line marked restricted anywhere in area.md (a second «Proyectos» heading, a «*» bullet) closes the
    # project it names: the index is read from the first block only, and an ignored mark would read it open
    # (review of 1.25.7, finding 3).
    for l in (area_text or "").split("\n"):
        m = re.match(r"^\s*[-*+]\s+`([^`]+?)`\s*[—–:-]?\s*(.*)$", l)
        if not m or not starts_restricted(m.group(2).strip(), lang):
            continue
        key = _slug_key(m.group(1))
        if key in by_key and not idx[by_key[key]].restricted:
            idx[by_key[key]].restricted = True
            if warnings is not None:
                warnings.append(f"el proyecto «{by_key[key]}» está marcado restringido fuera del índice de su área: se lee restringido")
    return idx


def who_takes_part(body: str, lang: Pack = ES) -> tuple[str, list[str], str, str]:
    """(responsible, collaborator lines' names, consumers, raw section) of «Quién participa»."""
    raw = section(body, lang.who)
    resp, coll, cons = "", [], ""
    for l in raw.split("\n"):
        m = re.match(r"^\s*[-*]?\s*\**\s*(" + "|".join(lang.responsible_labels) + r")\s*\**\s*:\s*(.+)$", l, re.I)
        if m and not resp:
            resp = re.sub(r"\s*\([^)]*\)\s*$", "", m.group(2).strip()).strip()
        elif _LINE_COLLABORATES.match(l):
            coll += names_in(l)
        else:
            mc = re.match(r"^\s*[-*]?\s*" + lang.consumers_label + r"\s*:\s*(.+)$", l, re.I)
            if mc:
                cons = mc.group(1).strip()
    return resp, coll, cons, raw


def project_file(area: str, slug: str, text: str, lang: Pack = ES) -> Project:
    fm, body = frontmatter(text or "")
    resp, coll, cons, _ = who_takes_part(body, lang)
    steps_ = [Step(text=b, dates=dates_in(b)) for b in bullets(section(body, lang.steps))]
    return Project(area=area, slug=slug, state=fm.get(lang.key_state) or None, updated=fm.get(lang.key_updated) or None,
                   title=h1(body), objective=section(body, lang.objective), done_means=section(body, lang.done_means),
                   scope=section(body, lang.scope), status=status(body, lang=lang), steps=steps_, responsible=resp,
                   collaborators=coll, consumers=cons)


def area_file(slug: str, text: str, lang: Pack = ES, warnings: Optional[list] = None) -> Area:
    fm, body = frontmatter(text or "")
    resp, _, _, _ = who_takes_part(body, lang)
    return Area(slug=slug, state=fm.get(lang.key_state) or None, updated=fm.get(lang.key_updated) or None, title=h1(body),
                what=section(body, lang.what), status=status(body, legacy=lang.status_legacy_area, lang=lang),
                priorities=area_priorities(body, lang), responsible=resp, index=project_index(text or "", lang, warnings))


def deliverable(file: str, text: Optional[str], index: Optional[IndexEntry], lang: Pack = ES) -> Deliverable:
    stem = file.rsplit(".", 1)[0] if "." in file else file
    d = Deliverable(file=file, name=stem, format=file.rsplit(".", 1)[1] if "." in file else "")
    if text is not None and file.endswith(".md"):
        fm, body = frontmatter(text)
        d.title = h1(body) or None
        d.state = fm.get(lang.key_state) or None
        d.updated = fm.get(lang.key_updated) or None
        if isinstance(fm.get(lang.key_based_on), list):
            d.based_on = [re.sub(r"^\./", "", b) for b in fm[lang.key_based_on]]
        d.replaced_by = fm.get(lang.key_replaced_by) or None
        new_key, old_key = lang.key_contribution
        ap = fm.get(new_key) if isinstance(fm.get(new_key), str) and fm[new_key].strip() else fm.get(old_key)
        if isinstance(ap, str) and ap.strip():
            d.contribution = ap.strip()[:240]
    ref = index.deliverables.get(stem) if index else None
    if ref is None and index and stem.endswith("-en"):
        ref = index.deliverables.get(stem[:-3])
    if ref:
        d.description = ref["description"]
        d.updated = d.updated or ref["updated"]
    return d
