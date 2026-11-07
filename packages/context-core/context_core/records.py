"""The record model: what a Memoria root is made of, as types.

Written down from what `generar_vista.py`, `abrir.py` and `cerrar.py` read today (hosted-stack.md, «Two constraints to
design in step 0»). Every field says which file and which key or section it comes from, so a caller never needs the
file to know what a record means. A record is what the method knows, not how a file spells it: the legacy spellings
(1.21 «Dueño», «Estado actual», «Prioridades ahora»; 1.22 «Cuenta» column) land in the same fields as the current ones.

Nothing here reads or writes: `parse` builds records from text and `load` from a root.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

__all__ = [
    "Person", "PeopleRegistry", "AreaRow", "Premise", "Status", "DecisionRef", "Decision", "SessionEntry", "Step",
    "Deliverable", "WorkshopFile", "IndexEntry", "Project", "Area", "Root",
]


# ── people ─────────────────────────────────────────────────────────────────────────────────────────────────────────

@dataclass
class Person:
    """One line of «Quién es quién» in guia.md (1.25): «- Name · account · field · field»."""
    name: str                                   # "?" for an account that has no name yet
    accounts: set[str] = field(default_factory=set)        # Claude accounts (a bare email, or «cuentas: a@, b@»)
    drive_accounts: set[str] = field(default_factory=set)  # «en Drive: x@»
    no_account: bool = False                    # «sin cuenta»
    unconfirmed: bool = False                   # «sin confirmar»
    aliases: list[str] = field(default_factory=list)       # «también: Other Spelling»
    organization: str = ""                      # «de: Organization»
    left_on: str = ""                           # «baja AAAA-MM-DD» ("sí" when the date is missing); a person who left does not write
    shared_with: str = ""                       # «compartida con: Name»
    registered_by: str = ""                     # «registra: Name»


@dataclass
class PeopleRegistry:
    """«Quién es quién». A name or an account on two lines belongs to nobody: it is dropped from the lookups."""
    declared: bool = False                      # the section exists (roots before 1.25 have accounts in the area table)
    people: list[Person] = field(default_factory=list)
    by_name: dict[str, Person] = field(default_factory=dict)     # key: parse.name_key(name)
    by_account: dict[str, Person] = field(default_factory=dict)  # key: lowercased email
    warnings: list[str] = field(default_factory=list)


@dataclass
class AreaRow:
    """One row of the «Áreas» table of guia.md: who answers for the area and who reads it."""
    slug: str                                   # folder name, without the slash
    what: str                                   # «Qué es»
    responsible: str                            # «Responsable» (1.22+) or «Dueño» (1.21), as written
    responsible_accounts: set[str] = field(default_factory=set)   # 1.21/1.22: the email before «colabora:»; 1.25: from the registry
    collaborators: list[str] = field(default_factory=list)        # 1.25 «Colabora» names; earlier, emails after «colabora:»
    collaborator_accounts: set[str] = field(default_factory=set)
    readers: str = ""                           # «Quién la lee», as written
    access: str = ""                            # «Acceso» (1.22+): «Abierta» / «Restringida»; empty before 1.22
    restricted: bool = False                    # decided by the method's rule, fail closed (parse.area_is_restricted)
    warnings: list[str] = field(default_factory=list)


@dataclass
class Premise:
    """One line of base/premisas.md: «- P1 · text · Confirmó: Name · AAAA-MM-DD · Reemplaza P0»."""
    id: str                                     # "P1"
    text: str
    line: str                                   # the whole line, as the opening prints it
    confirmed_by: str = ""
    date: str = ""
    replaces: Optional[str] = None


# ── project parts ──────────────────────────────────────────────────────────────────────────────────────────────────

@dataclass
class Status:
    """The «Estatus» section of proyecto.md or area.md (1.22+), or what stands for it in older roots.

    Current form:  «AAAA-MM-DD · **headline**» then bullets «Se completó:», «Siguiente:», «Falta decidir:», «Preocupa:».
    Legacy forms keep the whole text in `text` and leave the bullets empty: «Estado actual» / «En corto» (projects,
    1.21), «Panorama» (areas, 1.21)."""
    source: str                                 # the section it came from: "Estatus", "Estado actual", "En corto", "Panorama"
    text: str                                   # the section as written
    date: str = ""
    headline: str = ""
    completed: str = ""                         # «Se completó»
    next: list[str] = field(default_factory=list)   # «Siguiente», with its sub-bullets; for an area these are its priorities
    to_decide: str = ""                         # «Falta decidir»
    concern: str = ""                           # «Preocupa»
    finished_on: str = ""                       # «Proyecto terminado el AAAA-MM-DD»: the project is closed


@dataclass
class DecisionRef:
    """A pointer to a decision or a premise, as «Responde a», «Cuestiona a» and «Reemplaza» write it."""
    project: Optional[str]                      # "area--project", "premisa", or None when the text names no identifier
    id: Optional[str]                           # "2026-10-15-2", "P3"
    text: str                                   # as written


@dataclass
class Decision:
    """One entry of decisiones.md: «## AAAA-MM-DD · title» and its fields. Entries are never edited once written."""
    id: str                                     # the date, plus -2, -3… counting from the oldest entry of that day; "" without a valid date
    date: str
    title: str
    decided_by: str = ""                        # «Decidió»
    why: str = ""                               # «Por qué»
    discarded: str = ""                         # «Descartado» / «Descartamos»
    affects: str = ""                           # «Afecta a», as written (paths and projects separated by «·»)
    raised_by: str = ""                         # «Planteó» (challenges)
    challenges: Optional[DecisionRef] = None    # «Cuestiona a»
    responds_to: Optional[DecisionRef] = None   # «Responde a»
    replaces: Optional[DecisionRef] = None      # «Reemplaza»
    pending_confirmation: bool = False          # «Decidió: Name (pendiente de confirmar)»
    kind: str = "decision"                      # "decision" or "challenge" (a «Cuestiona a» or a title «Cuestionamiento: …»)
    archived: bool = False                      # it comes from decisiones-AAAA.md, not the live file


@dataclass
class SessionEntry:
    """One entry of sesiones.md: «## AAAA-MM-DD» and its fields."""
    n: int                                      # position counting from the oldest entry: stable when entries are added on top
    date: str
    title: str                                  # the heading as written (sessions of the same day share it)
    topic: str = ""                             # «Tema» / «Trabajamos en»
    progress: str = ""                          # «Avances»
    pending: str = ""                           # «Pendiente» (older roots)
    by: str = ""                                # «Sesión de», without the plugin version
    plugin_version: str = ""                    # «· plugin 1.25.1»
    server_version: str = ""                    # «· servidor 0.0.2»: the entry was written by the hosted server
    wrote: list[str] = field(default_factory=list)       # «Escribió», paths inside the project (restricted ones dropped)
    published: list[str] = field(default_factory=list)   # «Publicó»
    archived: bool = False


@dataclass
class Step:
    """One bullet of «Siguientes pasos». The method writes owner and size in the text; the record keeps the text whole
    and the dates it names, which is what the board and the close read."""
    text: str
    dates: list[str] = field(default_factory=list)


@dataclass
class Deliverable:
    """A file in the project's entregables/. Its header for .md files; for other formats only the name and the area index."""
    file: str                                   # "hosted-path.md"
    name: str                                   # stem
    format: str                                 # extension without the dot
    title: Optional[str] = None                 # the H1
    state: Optional[str] = None                 # «estado»: borrador, vigente, reemplazado…
    updated: Optional[str] = None               # «actualizado», else the date of its line in the area index
    based_on: list[str] = field(default_factory=list)     # «basado_en», paths from the root
    replaced_by: Optional[str] = None           # «reemplazado_por»
    contribution: Optional[str] = None          # «aportacion» (1.22+; «afirma» before): one line on what it holds
    description: str = ""                       # its line in the area's «Proyectos» index


@dataclass
class WorkshopFile:
    """A file in taller/. Workshop is never shown as current; the record holds only what the board lists."""
    path: str                                   # relative to taller/
    title: Optional[str] = None
    updated: Optional[str] = None


@dataclass
class IndexEntry:
    """A project line of the «Proyectos» block of area.md, with its deliverable sub-lines."""
    slug: str
    description: str
    restricted: bool = False                    # the description starts with «restringido»
    deliverables: dict[str, dict] = field(default_factory=dict)   # stem -> {"description", "updated"}
    notes: list[str] = field(default_factory=list)


@dataclass
class Project:
    """A project folder: proyecto.md, decisiones.md, sesiones.md, entregables/, taller/, fuentes/, restringido/."""
    area: str
    slug: str
    restricted: bool = False                    # restricted projects keep only their index line: nothing inside is read
    state: Optional[str] = None                 # proyecto.md «estado»
    updated: Optional[str] = None               # proyecto.md «actualizado»
    title: str = ""
    objective: str = ""                         # «Objetivo»
    done_means: str = ""                        # «Terminado significa» (older roots)
    scope: str = ""                             # «Alcance»
    status: Optional[Status] = None
    steps: list[Step] = field(default_factory=list)       # «Siguientes pasos»
    responsible: str = ""                       # «Quién participa»: «Responsable:» (1.22+) or «Dueño:» (1.21)
    collaborators: list[str] = field(default_factory=list)   # «Colabora:» names (1.25) or «Name (email)» (1.22)
    consumers: str = ""                         # «Consumen esto:» (older roots)
    decisions: list[Decision] = field(default_factory=list)  # newest first
    sessions: list[SessionEntry] = field(default_factory=list)  # newest first
    deliverables: list[Deliverable] = field(default_factory=list)
    workshop: list[WorkshopFile] = field(default_factory=list)
    index: Optional[IndexEntry] = None          # its line in area.md, if any

    @property
    def key(self) -> str:
        """The identifier the board and the queue use: "area--project"."""
        return f"{self.area}--{self.slug}"

    @property
    def closed(self) -> bool:
        return bool(self.status and self.status.finished_on)


@dataclass
class Area:
    """An area folder: area.md and its projects."""
    slug: str
    row: Optional[AreaRow] = None               # its row in guia.md; None for a folder the table does not name
    restricted: bool = False
    state: Optional[str] = None
    updated: Optional[str] = None
    title: str = ""
    what: str = ""                              # «Qué es»
    status: Optional[Status] = None             # «Estatus» (1.22+) or «Panorama»
    priorities: list[str] = field(default_factory=list)   # «Siguiente» of the Estatus, or «Prioridades ahora» (1.21)
    responsible: str = ""                       # «Quién participa» of area.md
    index: dict[str, IndexEntry] = field(default_factory=dict)
    projects: list[Project] = field(default_factory=list)


@dataclass
class Root:
    """A whole root: the folder with guia.md and metodo.md at its first level."""
    name: str
    organization: str = ""                      # what goes before «·» in the H1 of guia.md
    method_line: str = ""                       # first line of metodo.md: version and fingerprint
    method_version: Optional[tuple[int, ...]] = None
    method_fingerprint: Optional[str] = None
    language: str = "es"                        # the root's language pack (language.py)
    timezone: str = "America/Mexico_City"       # «Zona horaria:» of guia.md
    context_owner: str = ""                     # «Contexto común:» (who answers for guia.md and base/)
    administrator: str = ""                     # «Administra la carpeta:»
    people: PeopleRegistry = field(default_factory=PeopleRegistry)
    area_rows: list[AreaRow] = field(default_factory=list)
    areas: list[Area] = field(default_factory=list)
    premises: list[Premise] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def area(self, slug: str) -> Optional[Area]:
        return next((a for a in self.areas if a.slug == slug), None)

    def project(self, key: str) -> Optional[Project]:
        """By "area/project" or "area--project"."""
        a, _, p = key.replace("--", "/").partition("/")
        ar = self.area(a)
        return next((x for x in ar.projects if x.slug == p), None) if ar else None

    @property
    def current_premises(self) -> list[Premise]:
        replaced = {p.replaces for p in self.premises if p.replaces}
        return [p for p in self.premises if p.id not in replaced]
