"""Writing the method's files: the text changes every writer applies, and the entries a writer composes from fields.

One copy for the plugin's cerrar.py and the hosted server (decision of 2026-11-05: an operation moves onto the package
when its tool is built, and both call the same function). Pure functions, text in and text out: reading the file, the
lock and the write that fails if the file changed are the caller's, through its storage adapter.

Two parts:
- The text changes, moved here from cerrar.py 1.25.4 with the same results (tests/test_write.py checks them against
  the 1.25.4 copies frozen in tests/reference/): the header's `actualizado`, a register entry on top, a whole «## »
  block rewritten. cerrar.py takes them through `compat` under its Spanish names.
- The entries composed from fields (a session entry, a decision, an Estatus), for a writer that receives fields and
  not text, the server. Each field is checked first: a field that is one line has no line break of any kind, and a text
  field cannot carry a heading, a header line, or a line that a reader would take for another field of the same
  register (a «Publicó:» inside «Avances» would read as a publication). The writer, not the caller, puts the date and
  the author.
"""
from __future__ import annotations

import re
from typing import Iterable, Optional

from .language import ES, Pack

__all__ = ["with_header_today", "only_header_changed", "with_entry_on_top", "with_entries_on_top", "without_block",
           "with_block", "DECISION_ID", "is_decision_ref", "FieldError", "one_line", "text_field", "session_entry",
           "decision_entry", "status_block"]


# ── text changes (cerrar.py 1.25.4: cabecera_hoy, solo_cabecera, con_entrada_arriba, sin_bloque, con_bloque) ────────

def with_header_today(text: str, today: str) -> str:
    """The header's `actualizado` set to `today`, added if missing. A file without a header is left as it is."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return text
    head = re.sub(r"^actualizado:.*$", f"actualizado: {today}", m.group(1), count=1, flags=re.M)
    if "actualizado:" not in head:
        head += f"\nactualizado: {today}"
    return f"---\n{head}\n---\n" + text[m.end():]


def only_header_changed(before: str, after: str) -> bool:
    """True if the only change between the two texts is inside the header (between the two first «---»)."""
    m1, m2 = re.match(r"^---\n.*?\n---\n", before, re.S), re.match(r"^---\n.*?\n---\n", after, re.S)
    return bool(m1 and m2) and before[m1.end():] == after[m2.end():] and before != after


def with_entry_on_top(text: str, entry: str) -> tuple:
    """A new register entry under the title and above the rest; if it is already there, nothing. Returns (text, added)."""
    entry = entry.strip() + "\n"
    if entry.strip() in text:
        return text, False
    m = re.search(r"^# .*\n", text, re.M)
    if m:
        i = m.end()
        rest = text[i:]
        j = re.search(r"^## ", rest, re.M)
        if j:
            preface, body = rest[:j.start()], rest[j.start():]
            if not preface.strip():
                preface = "\n"
            elif not preface.endswith("\n\n"):
                preface = preface.rstrip("\n") + "\n\n"
            return text[:i] + preface + entry + "\n" + body, True
        # no entries yet (a register just opened, or just archived with its «Archivado:» line): what is under the title
        # stays before the first entry
        return text[:i] + ("\n" + rest.strip("\n") + "\n" if rest.strip() else "") + "\n" + entry, True
    return text.rstrip("\n") + "\n\n" + entry, True


def with_entries_on_top(text: str, entries: Iterable[str]) -> tuple:
    """Several entries given from the oldest to the newest, so the last one given ends on top (cerrar.py's order, which
    fixes the identifiers `#AAAA-MM-DD-n` of entries of the same day). Returns (text, any added)."""
    added = False
    for e in entries:
        text, a = with_entry_on_top(text, e)
        added = added or a
    return text, added


def without_block(text: str, name: str) -> str:
    """The whole «## name» block removed, if it is there."""
    return re.sub(r"^## " + re.escape(name) + r"\s*\n.*?(?=^## |\Z)", "", text, count=1, flags=re.M | re.S)


def with_block(text: str, name: str, body: str, before: Optional[str] = None, aliases: Iterable[str] = ()) -> str:
    """The whole «## name» block rewritten. If it does not exist, it is created under the title or, with `before`, just
    before that block (at the end if that one is missing too). The blocks named in `aliases` (older names of the same
    block) are removed, wherever they were."""
    body = body.strip() + "\n"
    for old in aliases:
        text = without_block(text, old)
    m = re.search(r"^## " + re.escape(name) + r"\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if m:
        return text[:m.start(1)] + body + "\n" + text[m.end(1):]
    new = f"## {name}\n{body}\n"
    if before:
        mb = re.search(r"^## " + re.escape(before) + r"\s*$", text, re.M)
        if mb:
            return text[:mb.start()] + new + text[mb.start():]
        return text.rstrip("\n") + "\n\n" + new
    mt = re.search(r"^# .*\n", text, re.M)
    i = mt.end() if mt else 0
    return text[:i] + "\n" + new + text[i:].lstrip("\n")


# ── fields ───────────────────────────────────────────────────────────────────────────────────────────────────────────

# an entry's identifier, as escribir.md §4 writes it: `area/proyecto#AAAA-MM-DD`, with -2, -3… for later entries of the
# same day, and a bare `#AAAA-MM-DD` inside the same project; the slug alphabet is parse.decision_ref's
DECISION_ID = re.compile(r"^`?(?:[a-z0-9][\w.-]*/[a-z0-9][\w.-]*)?#20\d\d-\d\d-\d\d(?:-\d+)?`?(?: · .+)?$")

# every character str.splitlines() and Markdown readers treat as a line break, «\n» included
_BREAKS = re.compile("[\r\n\v\f\x1c\x1d\x1e\x85  ]")
_OTHER_BREAKS = re.compile("[\r\v\f\x1c\x1d\x1e\x85  ]")


class FieldError(ValueError):
    """A field the writer refuses. `field` is the caller's name for it; the message names nothing else."""

    def __init__(self, field: str, message: str):
        super().__init__(f"{field} {message}")
        self.field = field


def is_decision_ref(text: str) -> bool:
    return bool(DECISION_ID.match((text or "").strip()))


def _labels(pack: Pack, register: str) -> list:
    """The lowercase labels a reader takes as a field of this register, without their colon."""
    if register == "sessions":
        words = pack.session_topic + pack.session_progress + pack.session_pending + pack.session_by
        words += pack.session_wrote + pack.session_published
    elif register == "decisions":
        words = tuple(w for w, _ in pack.decision_fields)
    else:
        raise ValueError(f"no register {register!r}")
    return sorted({w.rstrip(":").strip().lower() for w in words}, key=len, reverse=True)


def one_line(value: str, field: str, required: bool = True, limit: int = 600) -> str:
    v = (value or "").strip()
    if required and not v:
        raise FieldError(field, "is required")
    if _BREAKS.search(v):
        raise FieldError(field, "must be one line")
    if len(v) > limit:
        raise FieldError(field, f"is longer than {limit} characters")
    return v


def text_field(value: str, field: str, register: str, pack: Pack = ES, required: bool = True, limit: int = 4000) -> str:
    """A field that may run over several lines, as written in `register` ("sessions" or "decisions"): «\\r\\n» becomes
    «\\n»; any other line break, a heading, a header line or a line starting with a field label of that register is
    refused. Returned normalised, so what is written is exactly what was checked."""
    v = (value or "").replace("\r\n", "\n").strip()
    if required and not v:
        raise FieldError(field, "is required")
    if _OTHER_BREAKS.search(v):
        raise FieldError(field, "cannot contain a line break other than a plain newline")
    if len(v) > limit:
        raise FieldError(field, f"is longer than {limit} characters")
    labels = _labels(pack, register)
    for line in v.split("\n"):
        s = line.strip().lower()
        if s.startswith("#") or re.match(r"^---\s*$", s):
            raise FieldError(field, "cannot contain a heading or a header line")
        for label in labels:
            if s.startswith(label) and re.match(r"\s*:", s[len(label):]):
                raise FieldError(field, f"cannot contain a line that starts with a field of the register («{label}:»)")
    return v


# ── entries composed from fields ─────────────────────────────────────────────────────────────────────────────────────

def session_entry(date: str, topic: str, progress: str, by: str, writer: str, version: str,
                  wrote: Iterable[str] = (), published: Iterable[str] = (), pack: Pack = ES) -> str:
    """A sesiones.md entry (escribir.md §4). `writer` is "plugin" or "server"; the date and the author are the
    writer's, never the caller's. Each field is checked as `one_line` or `text_field`."""
    w = pack.write_session
    topic = one_line(topic, "topic")
    progress = text_field(progress, "progress", "sessions", pack)
    by = one_line(by, "by", limit=120)
    lines = [f"## {one_line(date, 'date')}", f"{w['topic']}: {topic}", f"{w['progress']}: {progress}"]
    wrote, published = _paths(wrote, "wrote"), _paths(published, "published")
    if wrote:
        lines.append(f"{w['wrote']}: {', '.join(wrote)}")
    if published:
        lines.append(f"{w['published']}: {', '.join(published)}")
    lines.append(f"{w['by']}: {by} · {pack.writers[writer]} {one_line(version, 'version')}")
    return "\n".join(lines)


def _paths(paths: Iterable[str], field: str) -> list:
    out = []
    for p in paths or ():
        p = one_line(p, field, limit=300)
        if "," in p:
            raise FieldError(field, f"{p!r} is not a path")
        if p not in out:
            out.append(p)
    return out


def decision_entry(date: str, title: str, decided_by: str, why: str, discarded: str = "", replaces: str = "",
                   responds_to: str = "", affects: str = "", pack: Pack = ES) -> str:
    """A decisiones.md decision (escribir.md §4), its lines in the contract's order and only those that say something.
    `replaces` and `responds_to` must be entry identifiers."""
    w = pack.write_decision
    lines = [f"## {one_line(date, 'date')} · {one_line(title, 'title')}",
             f"{w['decided_by']}: {one_line(decided_by, 'decided_by', limit=200)}",
             f"{w['why']}: {text_field(why, 'why', 'decisions', pack)}"]
    discarded = text_field(discarded, "discarded", "decisions", pack, required=False)
    if discarded:
        lines.append(f"{w['discarded']}: {discarded}")
    for key, value in (("replaces", replaces), ("responds_to", responds_to)):
        v = one_line(value, key, required=False)
        if v and not is_decision_ref(v):
            raise FieldError(key, "must be an entry identifier, «area/project#AAAA-MM-DD · its title»")
        if v:
            lines.append(f"{w[key]}: {v}")
    affects = one_line(affects, "affects", required=False)
    if affects:
        lines.append(f"{w['affects']}: {affects}")
    return "\n".join(lines)


def status_block(date: str, headline: str, completed: str = "", next: str = "", to_decide: str = "",
                 concern: str = "", pack: Pack = ES) -> str:
    """The body of an Estatus block (escribir.md §3): the date and the bold sentence, then the lines that say
    something. A project's first Estatus may carry only «Siguiente»; a closed project's, only the sentence that starts
    with the pack's finished marker."""
    w = pack.write_status
    headline = one_line(headline, "headline")
    if headline.startswith("**") or headline.endswith("**"):
        raise FieldError("headline", "is written without the asterisks: the writer puts them")
    lines = [f"{one_line(date, 'date')} · **{headline}**"]
    for key, value in (("completed", completed), ("next", next), ("to_decide", to_decide), ("concern", concern)):
        v = one_line(value, key, required=False)
        if v:
            lines.append(f"- **{w[key]}:** {v}")
    if len(lines) == 1 and not headline.startswith(pack.finished_marker):
        raise FieldError("next", "is required, unless the headline closes the project («" + pack.finished_marker + " …»)")
    return "\n".join(lines)
