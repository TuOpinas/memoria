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


_PATH = re.compile(r"`?(?<![\w.-])([a-z0-9][\w.-]*(?:/[\w.-]+)+/?)(#20\d\d-\d\d-\d\d(?:-\d+)?)?`?")


def _cut(path: str, root: Root, lang: Pack) -> Optional[str]:
    """The public form of one path, or None when it stays as written."""
    parts = path.strip("/").split("/")
    if lang.restricted in parts:
        i = parts.index(lang.restricted)
        return "/".join(parts[:i]) if i else lang.restricted + "/"
    area = root.area(parts[0])
    if area is None:
        return None
    if area.restricted:
        return parts[0] + "/"
    if len(parts) > 1:
        pr = next((p for p in area.projects if p.slug == parts[1]), None)
        if pr is not None and pr.restricted:
            return f"{parts[0]}/{parts[1]}"
    return None


def public_reference(text: str, root: Root, lang: Pack = ES) -> str:
    """`text` with each reference into a restricted zone cut to the zone's name (see the module's docstring)."""
    def sub(m: re.Match) -> str:
        cut = _cut(m.group(1), root, lang)
        return m.group(0) if cut is None else cut
    return _PATH.sub(sub, text or "")
