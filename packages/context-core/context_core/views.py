"""What a reader may be served of a loaded root, beyond what `load` already leaves out.

Two things every caller that serves a root needs the same way, so they live here and not in each caller (review of
`consultar`, findings 5 and 7): the challenge index, and references reduced at the edge of a restricted zone.

- `challenge_index(root)`: every challenge of the loaded registers (live, this year's and last year's archives) with
  the decisions that answer it, wherever the answer is written (another project, an older archive). A challenge is open
  while nothing answers it. `consultar`, `abrir_sesion` and the board read the same index.
- `public_reference(text, root)`: a field that names paths or decisions («Afecta a», «Cuestiona a», «Escribió») with
  every reference into a restricted zone cut to the name of the zone, which `convenciones` section 7 lets anyone see:
  a restricted area to «area/», a restricted project to «area/project», anything inside `restringido/` to the project
  (or folder) that holds it.

Pure functions over records: they read nothing.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Optional

from .language import ES, Pack
from .records import Decision, DecisionRef, Root

__all__ = ["Challenge", "challenge_index", "open_challenges", "public_reference"]


@dataclass
class Challenge:
    """A challenge entry and what answers it."""
    project: str                                # "area--project" where the challenge is written
    decision: Decision                          # the challenge entry itself
    target: Optional[DecisionRef]               # what it challenges: a decision or a premise
    answers: list[str] = field(default_factory=list)   # "area--project#id" of each answer; "(archivo antiguo)" when only an old archive has it

    @property
    def key(self) -> str:
        return f"{self.project}#{self.decision.id}"

    @property
    def open(self) -> bool:
        return not self.answers


def challenge_index(root: Root) -> list[Challenge]:
    """Every challenge in the projects whose decisions were loaded, newest first, with its answers."""
    found: list[Challenge] = []
    answers: dict[tuple, list[str]] = {}
    for area in root.areas:
        for pr in area.projects:
            if pr.restricted or "decisions" not in pr.loaded:
                continue
            for d in pr.decisions:
                if d.kind == "challenge" and d.id:
                    found.append(Challenge(project=pr.key, decision=d, target=d.challenges))
                r = d.responds_to
                if r and r.project and r.id:
                    answers.setdefault((r.project, r.id), []).append(f"{pr.key}#{d.id}" if d.id else pr.key)
            for r in pr.old_responses:
                if r.project and r.id:
                    answers.setdefault((r.project, r.id), []).append(f"{pr.key} (archivo antiguo)")
    for c in found:
        c.answers = answers.get((c.project, c.decision.id), [])
    found.sort(key=lambda c: c.decision.date, reverse=True)
    return found


def open_challenges(root: Root) -> list[Challenge]:
    return [c for c in challenge_index(root) if c.open]


def _key(name: str) -> str:
    """How two spellings of one folder name compare: NFC and casefold, as macOS, Drive and Windows treat them."""
    return unicodedata.normalize("NFC", name).casefold()


# A field names several references separated by « · » or line breaks; a reference is cut whole, with whatever note
# follows it, never only the piece a path pattern finds (review of 1.25.6, finding 1: a file name with spaces). Commas
# and semicolons do not separate: they also live inside a reference's note in brackets, and splitting there let the
# note's tail through (second review of consultar, finding 2).
_SEP = re.compile(r"(\s+·\s+|\n)")


def _zones(root: Root):
    """(restricted area keys, open area keys -> Area, every known area key -> its slug as written)."""
    names, closed, opened = {}, set(), {}
    for row in root.area_rows:
        names.setdefault(_key(row.slug), row.slug)
        if row.restricted:
            closed.add(_key(row.slug))
    for a in root.areas:
        names.setdefault(_key(a.slug), a.slug)
        if a.restricted:
            closed.add(_key(a.slug))
        else:
            opened[_key(a.slug)] = a
    # an area with a row but no loaded folder (on Drive the server may not list it) counts as restricted
    closed |= {k for k in names if k not in opened}
    return closed, opened, names


def _cut(ref: str, root: Root, lang: Pack, here: Optional[str], zones) -> Optional[str]:
    """The public form of one reference, or None when it stays as written."""
    closed, opened, names = zones
    t = unicodedata.normalize("NFC", ref.strip().strip("`'\"«»").replace("\\", "/"))
    path = t.split("#", 1)[0]
    parts = [x for x in path.split("/") if x not in ("", ".", "..")]
    if not parts:
        return None
    # prose around a path: the area is the last word before its «/», a project the first word after it
    last = lambda x: (re.findall(r"[\w.-]+$", x) or [""])[0]
    lead = lambda x: (re.match(r"[\w.-]*", x.strip()).group(0))
    keys = [_key(last(parts[0]) if len(parts) > 1 else parts[0])] + [_key(lead(x)) for x in parts[1:]]
    start = next((i for i, k in enumerate(keys) if k in names and (len(parts) > 1 or "#" in t or k == _key(path.strip()))), None)
    restricted = _key(lang.restricted)
    if start is None:
        # relative to the current project or area: «restringido/x.md», «secreto/plan.md», «secreto#2026-01-02»
        h_area, _, h_proj = (here or "").replace("--", "/").partition("/")
        if h_area and _key(h_area) in names:
            first = keys[0]
            area = opened.get(_key(h_area))
            if restricted in keys:
                return f"{names[_key(h_area)]}/{h_proj}" if h_proj and keys.index(restricted) == 0 else lang.restricted + "/"
            if area is not None:
                pr = next((x for x in area.projects if _key(x.slug) == first), None)
                if pr is not None and pr.restricted:
                    return f"{area.slug}/{pr.slug}"
            return None
        return lang.restricted + "/" if restricted in keys else None
    akey = keys[start]
    if akey in closed:
        return names[akey] + "/"
    area = opened[akey]
    rest = keys[start + 1:]
    if rest:
        pr = next((x for x in area.projects if _key(x.slug) == rest[0]), None)
        if pr is not None and (pr.restricted or restricted in rest):
            return f"{area.slug}/{pr.slug}"
    if restricted in rest:
        return area.slug + "/"
    return None


def public_reference(text: str, root: Root, lang: Pack = ES, here: Optional[str] = None) -> str:
    """`text` with each reference into a restricted zone cut to the zone's name (see the module's docstring).
    `here` ("area--project") resolves references written relative to the current project."""
    zones = _zones(root)
    out = []
    for piece in _SEP.split(text or ""):
        if not piece or _SEP.fullmatch(piece):
            out.append(piece)
            continue
        cut = _cut_piece(piece, root, lang, here, zones)
        out.append(piece if cut is None else cut)
    return "".join(out)


_TOKEN = re.compile(r"[^\s,;()\[\]{}<>]+")


def _cut_piece(piece: str, root: Root, lang: Pack, here: Optional[str], zones) -> Optional[str]:
    """One piece of a field (between « · » or line breaks): every path-like token in it is checked, not only the first,
    so «a.md, ventas/secreto/plan.md» or a note «(ver también restringido/x.md)» cannot carry a restricted reference
    past the cut (review of 1.25.7, finding 1). If any token touches a restricted zone, the whole piece becomes the
    names of the zones it touches; otherwise it stays as written."""
    whole = _cut(piece, root, lang, here, zones)
    found = [whole] if whole else []
    for tok in _TOKEN.findall(piece):
        if not any(c in tok for c in "/\\#"):
            continue
        c = _cut(tok, root, lang, here, zones)
        if c and c not in found:
            found.append(c)
    return " · ".join(found) if found else None
