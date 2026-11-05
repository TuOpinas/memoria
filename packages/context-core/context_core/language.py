"""Language packs: how one language spells the method in the files.

The record model has no language; a pack says how a root in that language names its reserved folders and files, its
sections, the fields of its registers and the keys of its headers. A root has one language, chosen when it is set up and
by default its owner's (decision of 2026-11-05: reserved names follow the root's language and existing roots keep their
Spanish names). Spanish is the first and only complete pack; English comes with the language packs after area types.

Not here yet, and still spelled inside `parse.py`: the words of «Quién es quién» and of the area table (they are the
1.25.1 rules, frozen in tests/reference/ and compared line by line) and the markers of the first paragraph of guia.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

__all__ = ["Pack", "ES", "PACKS", "pack"]


@dataclass(frozen=True)
class Pack:
    code: str
    # reserved folders and files
    guide: str
    method: str
    area_file: str
    project_file: str
    decisions_file: str
    sessions_file: str
    base: str
    premises_file: str
    deliverables: str
    workshop: str
    sources: str
    restricted: str
    # sections, as their «## » heading
    status: str
    status_legacy_project: tuple
    status_legacy_area: tuple
    priorities_legacy: str
    steps: str
    who: str
    objective: str
    done_means: str
    scope: str
    what: str
    projects: str
    areas: str
    # the lines of «Quién participa» and of guia.md
    responsible_labels: tuple
    consumers_label: str
    context_owner_label: str
    administrator_label: str
    # Estatus bullets, as heading_key() leaves them
    status_fields: dict = field(default_factory=dict)
    finished_marker: str = ""
    # decisiones.md: (lowercase prefix, record field)
    decision_fields: tuple = ()
    pending_confirmation: str = ""
    challenge_title: str = ""
    # sesiones.md
    session_wrote: tuple = ()
    session_published: tuple = ()
    session_topic: tuple = ()
    session_progress: tuple = ()
    session_pending: tuple = ()
    session_by: tuple = ()
    # header keys
    key_state: str = ""
    key_updated: str = ""
    key_based_on: str = ""
    key_replaced_by: str = ""
    key_contribution: tuple = ()


ES = Pack(
    code="es",
    guide="guia.md", method="metodo.md", area_file="area.md", project_file="proyecto.md",
    decisions_file="decisiones.md", sessions_file="sesiones.md", base="base", premises_file="premisas.md",
    deliverables="entregables", workshop="taller", sources="fuentes", restricted="restringido",
    status="Estatus", status_legacy_project=("Estado actual", "En corto"), status_legacy_area=("Panorama",),
    priorities_legacy="Prioridades ahora", steps="Siguientes pasos", who="Quién participa", objective="Objetivo",
    done_means="Terminado significa", scope="Alcance", what="Qué es", projects="Proyectos", areas="Áreas",
    responsible_labels=("responsable", "dueño", "dueno", "dueña"), consumers_label="consumen esto",
    context_owner_label="Contexto común", administrator_label=r"Administra la carpeta(?: y pone o quita los accesos)?",
    status_fields={"se completo": "completed", "siguiente": "next", "falta decidir": "to_decide", "preocupa": "concern"},
    finished_marker="Proyecto terminado el",
    decision_fields=(("decidió:", "decided_by"), ("decidio:", "decided_by"), ("por qué:", "why"), ("por que:", "why"),
                     ("descartamos:", "discarded"), ("descartado:", "discarded"), ("afecta a:", "affects"),
                     ("planteó:", "raised_by"), ("planteo:", "raised_by"), ("cuestiona a:", "challenges"),
                     ("responde a:", "responds_to"), ("reemplaza:", "replaces"), ("reemplaza a:", "replaces")),
    pending_confirmation=r"\(pendiente de confirma(r|ción)\)", challenge_title="cuestionamiento",
    session_wrote=("escribió", "escribio"), session_published=("publicó", "publico"),
    session_topic=("trabajamos en:", "tema:"), session_progress=("avances:",), session_pending=("pendiente:",),
    session_by=("sesión de:", "sesion de:"),
    key_state="estado", key_updated="actualizado", key_based_on="basado_en", key_replaced_by="reemplazado_por",
    key_contribution=("aportacion", "afirma"),
)

PACKS = {"es": ES}


def pack(code: Optional[str]) -> Pack:
    """The pack for a language code; Spanish when the code is missing or has no pack yet."""
    return PACKS.get((code or "es").lower(), ES)
