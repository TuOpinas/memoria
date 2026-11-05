#!/usr/bin/env python3
"""Migra una raíz del método a la estructura de la 1.22, en lo que escribe la cuenta (skill sesion).

Uso: migrar_estructura.py <raiz> --cuenta <correo> [--plan] [--plugin X.Y.Z] [--nombre "Nombre Apellido"] [--sin-consola]

Lo ofrece la apertura cuando abrir.py dice «ESTRUCTURA: ANTERIOR»; con el sí de la persona se corre una vez, sin --plan.
Con --plan no escribe nada y dice qué haría. Toca las áreas de las que la cuenta es responsable (la celda Cuenta de
guia.md, antes de «colabora:»); si es la del responsable de contexto, además guia.md y todas las demás áreas con carpeta,
restringidas incluidas (desde la 1.22.1: es quien administra la carpeta y su dueño en Drive, y así una raíz no queda a
medias por un responsable que no abre sesión), con la entrada de la bitácora de esos proyectos diciendo por quién. Lo
que no migra (un área sin carpeta) va a «pendientes» con su motivo. Cualquier otra cuenta deja las
áreas ajenas para su responsable, y una raíz mezclada funciona porque scripts y skills leen los dos nombres durante la 1.22.
Sin consola (la carpeta no está montada en la computadora) se corre en el contenedor sobre la copia que arma «espejo.py
migracion», con --sin-consola (la entrada de la bitácora lleva la marca), y lo que cambia se devuelve con espejo.py;
los renombrados de archivo los hace después el conector de Drive (skill sesion, migracion.md).

Lo que renombra (contrato, escribir.md, secciones 2, 3, 4 y 5), sin perder nada:
  guia.md       en la primera tabla de «## Áreas», la columna «Dueño» pasa a «Responsable» y se añade «Acceso»
                («Restringida» o «Abierta», por lo que dice «Quién la lee»). La celda «Quién la lee» se deja como está,
                también si empieza por «Restringida:», para que un plugin 1.21 siga viendo el área restringida mientras
                dure la 1.22; los lectores 1.22 ya la limpian. «enlaces.md» pasa a «inventario.md».
  area.md       «Panorama» y «Prioridades ahora» se juntan en «Estatus» (la fecha y la primera frase del Panorama en
                negrita, el resto detrás, las prioridades debajo de «Siguiente» y una línea por proyecto activo con la
                frase de su Estatus); si ya había un «Estatus» al lado, se queda el más reciente por fecha, las
                prioridades que falten se añaden a «Siguiente» y el otro bloque va a taller/estatus-anterior.md; «Dueño:»
                pasa a «Responsable:» en «Quién participa»; la línea de un entregable vigente se toma de su aportacion si
                la tiene; las secciones van en el orden de la 1.22 (Estatus, Qué es, Proyectos, Quién participa).
  proyecto.md   «En corto» pasa a «Estatus»; con un «Estatus» ya al lado, se queda el más reciente y el otro va al
                taller; sin «En corto», el Estatus nace con la fecha de `actualizado` y la primera frase de «Estado
                actual» en negrita; un proyecto cerrado lleva en su Estatus «Proyecto terminado el …» y cómo acabó.
                «Terminado significa» se suma a «Objetivo»; «Sí:» y «No:» de Alcance pasan a «Entra:» y «No entra:»;
                «Dueño:» pasa a «Responsable:» y sale «Consumen esto:», en «Quién participa»; «Estado actual» sale
                entero a taller/estado-anterior.md (en un proyecto cerrado se queda resumido en el Estatus y no se crea
                archivo); las secciones van en el orden de la 1.22 (Estatus, Objetivo, Alcance, Siguientes pasos, Quién
                participa).
  cabeceras     «afirma:» pasa a «aportacion:» en entregables/ y taller/, y en basado_en «fuentes/enlaces.md» pasa a
                «fuentes/inventario.md»; `actualizado` no se mueve, porque no cambia el contenido.
  archivos      fuentes/enlaces.md y restringido/enlaces.md pasan a inventario.md (si ya existe uno, no se pisa: se dice).
  sesiones.md   una entrada «## AAAA-MM-DD (migracion)» arriba en cada proyecto migrado, de una frase.

Cómo escribe: primero los archivos nuevos del taller y, solo si cada uno quedó escrito, su proyecto.md; la entrada de la
bitácora solo si su proyecto.md quedó escrito, y area.md al final, solo si todos los proyecto.md del área quedaron escritos
(la apertura da un área por migrada por su area.md: un fallo deja la pregunta en pie, y repetir el script lo completa); cada archivo se
relee y se vuelve a transformar en el momento de escribirlo, bajo un cerrojo por archivo, como cerrar.py, para no pisar
un cierre que llegue entre medias. No toca decisiones.md, las entradas ya escritas de sesiones.md, base/ ni lo que hay
dentro de fuentes/ y restringido/ salvo su inventario. La fecha es la del día en la zona horaria de guia.md. Repetirlo
no hace nada. Imprime un JSON compacto con, primero, lo que hay que mirar: «conflictos» (un inventario.md o un
estado-anterior.md que ya existían), «fallidos», «entradas» (los sesiones.md donde dejó su entrada, o la dejaría con
--plan), «resumen» (cuántos archivos por tipo de cambio), «areas», «ajenas» (las de otros responsables que migra el de
contexto), «guia», «pendientes» (las áreas de otras cuentas que no migra, con su motivo), «nuevos»
(los archivos del taller que crea), «renombrados» y, al final, «archivos» (ruta: cambios).
"""
import datetime, hashlib, json, os, pathlib, re, sys, tempfile, time

EN_USO_MIN = 120   # un proyecto ajeno tocado hace menos se deja: puede estar en sesión en otra computadora

# --- las marcas de la estructura anterior: la misma función en abrir.py; probar_migrar.py comprueba que coinciden ---
def marcas_anteriores(texto, tipo):
    """Qué marcas de la estructura de la 1.21 tiene un area.md («area») o un proyecto.md («proyecto»): las secciones
    viejas, y «Dueño:» o «Consumen esto:» solo dentro de «Quién participa», que es donde la migración las renombra."""
    secs = set(re.findall(r"^## (.+?)\s*$", texto or "", re.M))
    viejas = {"area": ("Panorama", "Prioridades ahora"), "proyecto": ("En corto", "Estado actual", "Terminado significa")}[tipo]
    out = [x for x in viejas if x in secs]
    m = re.search(r"^## Quién participa\s*\n(.*?)(?=^## |\Z)", texto or "", re.M | re.S)
    q = m.group(1) if m else ""
    if re.search(r"^\s*[-*]?\s*\**\s*Due[ñn][oa]\s*\**\s*:", q, re.M):
        out.append("Dueño")
    if tipo == "proyecto" and re.search(r"^\s*[-*]?\s*\**\s*Consumen esto\s*\**\s*:", q, re.M):
        out.append("Consumen esto")
    return out
ARCHIVOS_ANTERIORES = ("fuentes/enlaces.md", "restringido/enlaces.md")

# --- quién escribe: «Quién es quién» y la tabla de áreas de guia.md, y la línea «Colabora:» de un proyecto ---
# Desde el paso 0 de la versión alojada vive en un solo sitio, el paquete context_core (packages/context-core del repo),
# que packages/context-core/inline.py mete aquí al publicar para que el script siga corriendo descargado suelto. El
# bloque es idéntico en los ocho scripts que lo usan (pruebas/sesion/probar_cuentas.py) y context_core/compat.py devuelve
# lo mismo que la copia de la 1.25.1 (packages/context-core/tests/test_compat.py).
# --- context_core: generated by packages/context-core/inline.py from packages/context-core/context_core; do not edit by hand ---
def _context_core():
    import sys as _s, types as _t
    if "context_core.compat" in _s.modules:
        return
    _src = {
    'language': '"""Language packs: how one language spells the method in the files.\n\nThe record model has no language; a pack says how a root in that language names its reserved folders and files, its\nsections, the fields of its registers and the keys of its headers. A root has one language, chosen when it is set up and\nby default its owner\'s (decision of 2026-11-05: reserved names follow the root\'s language and existing roots keep their\nSpanish names). Spanish is the first and only complete pack; English comes with the language packs after area types.\n\nNot here yet, and still spelled inside `parse.py`: the words of «Quién es quién» and of the area table (they are the\n1.25.1 rules, frozen in tests/reference/ and compared line by line) and the markers of the first paragraph of guia.md.\n"""\nfrom __future__ import annotations\n\nfrom dataclasses import dataclass, field\nfrom typing import Optional\n\n__all__ = ["Pack", "ES", "PACKS", "pack"]\n\n\n@dataclass(frozen=True)\nclass Pack:\n    code: str\n    # reserved folders and files\n    guide: str\n    method: str\n    area_file: str\n    project_file: str\n    decisions_file: str\n    sessions_file: str\n    base: str\n    premises_file: str\n    deliverables: str\n    workshop: str\n    sources: str\n    restricted: str\n    # sections, as their «## » heading\n    status: str\n    status_legacy_project: tuple\n    status_legacy_area: tuple\n    priorities_legacy: str\n    steps: str\n    who: str\n    objective: str\n    done_means: str\n    scope: str\n    what: str\n    projects: str\n    areas: str\n    # the lines of «Quién participa» and of guia.md\n    responsible_labels: tuple\n    consumers_label: str\n    context_owner_label: str\n    administrator_label: str\n    # Estatus bullets, as heading_key() leaves them\n    status_fields: dict = field(default_factory=dict)\n    finished_marker: str = ""\n    # decisiones.md: (lowercase prefix, record field)\n    decision_fields: tuple = ()\n    pending_confirmation: str = ""\n    challenge_title: str = ""\n    # sesiones.md\n    session_wrote: tuple = ()\n    session_published: tuple = ()\n    session_topic: tuple = ()\n    session_progress: tuple = ()\n    session_pending: tuple = ()\n    session_by: tuple = ()\n    # header keys\n    key_state: str = ""\n    key_updated: str = ""\n    key_based_on: str = ""\n    key_replaced_by: str = ""\n    key_contribution: tuple = ()\n\n\nES = Pack(\n    code="es",\n    guide="guia.md", method="metodo.md", area_file="area.md", project_file="proyecto.md",\n    decisions_file="decisiones.md", sessions_file="sesiones.md", base="base", premises_file="premisas.md",\n    deliverables="entregables", workshop="taller", sources="fuentes", restricted="restringido",\n    status="Estatus", status_legacy_project=("Estado actual", "En corto"), status_legacy_area=("Panorama",),\n    priorities_legacy="Prioridades ahora", steps="Siguientes pasos", who="Quién participa", objective="Objetivo",\n    done_means="Terminado significa", scope="Alcance", what="Qué es", projects="Proyectos", areas="Áreas",\n    responsible_labels=("responsable", "dueño", "dueno", "dueña"), consumers_label="consumen esto",\n    context_owner_label="Contexto común", administrator_label=r"Administra la carpeta(?: y pone o quita los accesos)?",\n    status_fields={"se completo": "completed", "siguiente": "next", "falta decidir": "to_decide", "preocupa": "concern"},\n    finished_marker="Proyecto terminado el",\n    decision_fields=(("decidió:", "decided_by"), ("decidio:", "decided_by"), ("por qué:", "why"), ("por que:", "why"),\n                     ("descartamos:", "discarded"), ("descartado:", "discarded"), ("afecta a:", "affects"),\n                     ("planteó:", "raised_by"), ("planteo:", "raised_by"), ("cuestiona a:", "challenges"),\n                     ("responde a:", "responds_to"), ("reemplaza:", "replaces"), ("reemplaza a:", "replaces")),\n    pending_confirmation=r"\\(pendiente de confirma(r|ción)\\)", challenge_title="cuestionamiento",\n    session_wrote=("escribió", "escribio"), session_published=("publicó", "publico"),\n    session_topic=("trabajamos en:", "tema:"), session_progress=("avances:",), session_pending=("pendiente:",),\n    session_by=("sesión de:", "sesion de:"),\n    key_state="estado", key_updated="actualizado", key_based_on="basado_en", key_replaced_by="reemplazado_por",\n    key_contribution=("aportacion", "afirma"),\n)\n\nPACKS = {"es": ES}\n\n\ndef pack(code: Optional[str]) -> Pack:\n    """The pack for a language code; Spanish when the code is missing or has no pack yet."""\n    return PACKS.get((code or "es").lower(), ES)\n',
    'records': '"""The record model: what a Memoria root is made of, as types.\n\nWritten down from what `generar_vista.py`, `abrir.py` and `cerrar.py` read today (hosted-stack.md, «Two constraints to\ndesign in step 0»). Every field says which file and which key or section it comes from, so a caller never needs the\nfile to know what a record means. A record is what the method knows, not how a file spells it: the legacy spellings\n(1.21 «Dueño», «Estado actual», «Prioridades ahora»; 1.22 «Cuenta» column) land in the same fields as the current ones.\n\nNothing here reads or writes: `parse` builds records from text and `load` from a root.\n"""\nfrom __future__ import annotations\n\nfrom dataclasses import dataclass, field\nfrom typing import Optional\n\n__all__ = [\n    "Person", "PeopleRegistry", "AreaRow", "Premise", "Status", "DecisionRef", "Decision", "SessionEntry", "Step",\n    "Deliverable", "WorkshopFile", "IndexEntry", "Project", "Area", "Root",\n]\n\n\n# ── people ─────────────────────────────────────────────────────────────────────────────────────────────────────────\n\n@dataclass\nclass Person:\n    """One line of «Quién es quién» in guia.md (1.25): «- Name · account · field · field»."""\n    name: str                                   # "?" for an account that has no name yet\n    accounts: set[str] = field(default_factory=set)        # Claude accounts (a bare email, or «cuentas: a@, b@»)\n    drive_accounts: set[str] = field(default_factory=set)  # «en Drive: x@»\n    no_account: bool = False                    # «sin cuenta»\n    unconfirmed: bool = False                   # «sin confirmar»\n    aliases: list[str] = field(default_factory=list)       # «también: Other Spelling»\n    organization: str = ""                      # «de: Organization»\n    left_on: str = ""                           # «baja AAAA-MM-DD» ("sí" when the date is missing); a person who left does not write\n    shared_with: str = ""                       # «compartida con: Name»\n    registered_by: str = ""                     # «registra: Name»\n\n\n@dataclass\nclass PeopleRegistry:\n    """«Quién es quién». A name or an account on two lines belongs to nobody: it is dropped from the lookups."""\n    declared: bool = False                      # the section exists (roots before 1.25 have accounts in the area table)\n    people: list[Person] = field(default_factory=list)\n    by_name: dict[str, Person] = field(default_factory=dict)     # key: parse.name_key(name)\n    by_account: dict[str, Person] = field(default_factory=dict)  # key: lowercased email\n    warnings: list[str] = field(default_factory=list)\n\n\n@dataclass\nclass AreaRow:\n    """One row of the «Áreas» table of guia.md: who answers for the area and who reads it."""\n    slug: str                                   # folder name, without the slash\n    what: str                                   # «Qué es»\n    responsible: str                            # «Responsable» (1.22+) or «Dueño» (1.21), as written\n    responsible_accounts: set[str] = field(default_factory=set)   # 1.21/1.22: the email before «colabora:»; 1.25: from the registry\n    collaborators: list[str] = field(default_factory=list)        # 1.25 «Colabora» names; earlier, emails after «colabora:»\n    collaborator_accounts: set[str] = field(default_factory=set)\n    readers: str = ""                           # «Quién la lee», as written\n    access: str = ""                            # «Acceso» (1.22+): «Abierta» / «Restringida»; empty before 1.22\n    restricted: bool = False                    # decided by the method\'s rule, fail closed (parse.area_is_restricted)\n    warnings: list[str] = field(default_factory=list)\n\n\n@dataclass\nclass Premise:\n    """One line of base/premisas.md: «- P1 · text · Confirmó: Name · AAAA-MM-DD · Reemplaza P0»."""\n    id: str                                     # "P1"\n    text: str\n    line: str                                   # the whole line, as the opening prints it\n    confirmed_by: str = ""\n    date: str = ""\n    replaces: Optional[str] = None\n\n\n# ── project parts ──────────────────────────────────────────────────────────────────────────────────────────────────\n\n@dataclass\nclass Status:\n    """The «Estatus» section of proyecto.md or area.md (1.22+), or what stands for it in older roots.\n\n    Current form:  «AAAA-MM-DD · **headline**» then bullets «Se completó:», «Siguiente:», «Falta decidir:», «Preocupa:».\n    Legacy forms keep the whole text in `text` and leave the bullets empty: «Estado actual» / «En corto» (projects,\n    1.21), «Panorama» (areas, 1.21)."""\n    source: str                                 # the section it came from: "Estatus", "Estado actual", "En corto", "Panorama"\n    text: str                                   # the section as written\n    date: str = ""\n    headline: str = ""\n    completed: str = ""                         # «Se completó»\n    next: list[str] = field(default_factory=list)   # «Siguiente», with its sub-bullets; for an area these are its priorities\n    to_decide: str = ""                         # «Falta decidir»\n    concern: str = ""                           # «Preocupa»\n    finished_on: str = ""                       # «Proyecto terminado el AAAA-MM-DD»: the project is closed\n\n\n@dataclass\nclass DecisionRef:\n    """A pointer to a decision or a premise, as «Responde a», «Cuestiona a» and «Reemplaza» write it."""\n    project: Optional[str]                      # "area--project", "premisa", or None when the text names no identifier\n    id: Optional[str]                           # "2026-10-15-2", "P3"\n    text: str                                   # as written\n\n\n@dataclass\nclass Decision:\n    """One entry of decisiones.md: «## AAAA-MM-DD · title» and its fields. Entries are never edited once written."""\n    id: str                                     # the date, plus -2, -3… counting from the oldest entry of that day; "" without a valid date\n    date: str\n    title: str\n    decided_by: str = ""                        # «Decidió»\n    why: str = ""                               # «Por qué»\n    discarded: str = ""                         # «Descartado» / «Descartamos»\n    affects: str = ""                           # «Afecta a», as written (paths and projects separated by «·»)\n    raised_by: str = ""                         # «Planteó» (challenges)\n    challenges: Optional[DecisionRef] = None    # «Cuestiona a»\n    responds_to: Optional[DecisionRef] = None   # «Responde a»\n    replaces: Optional[DecisionRef] = None      # «Reemplaza»\n    pending_confirmation: bool = False          # «Decidió: Name (pendiente de confirmar)»\n    kind: str = "decision"                      # "decision" or "challenge" (a «Cuestiona a» or a title «Cuestionamiento: …»)\n    archived: bool = False                      # it comes from decisiones-AAAA.md, not the live file\n\n\n@dataclass\nclass SessionEntry:\n    """One entry of sesiones.md: «## AAAA-MM-DD» and its fields."""\n    n: int                                      # position counting from the oldest entry: stable when entries are added on top\n    date: str\n    title: str                                  # the heading as written (sessions of the same day share it)\n    topic: str = ""                             # «Tema» / «Trabajamos en»\n    progress: str = ""                          # «Avances»\n    pending: str = ""                           # «Pendiente» (older roots)\n    by: str = ""                                # «Sesión de», without the plugin version\n    plugin_version: str = ""                    # «· plugin 1.25.1»\n    wrote: list[str] = field(default_factory=list)       # «Escribió», paths inside the project (restricted ones dropped)\n    published: list[str] = field(default_factory=list)   # «Publicó»\n    archived: bool = False\n\n\n@dataclass\nclass Step:\n    """One bullet of «Siguientes pasos». The method writes owner and size in the text; the record keeps the text whole\n    and the dates it names, which is what the board and the close read."""\n    text: str\n    dates: list[str] = field(default_factory=list)\n\n\n@dataclass\nclass Deliverable:\n    """A file in the project\'s entregables/. Its header for .md files; for other formats only the name and the area index."""\n    file: str                                   # "hosted-path.md"\n    name: str                                   # stem\n    format: str                                 # extension without the dot\n    title: Optional[str] = None                 # the H1\n    state: Optional[str] = None                 # «estado»: borrador, vigente, reemplazado…\n    updated: Optional[str] = None               # «actualizado», else the area index, else the file date\n    updated_from_file: bool = False\n    based_on: list[str] = field(default_factory=list)     # «basado_en», paths from the root\n    replaced_by: Optional[str] = None           # «reemplazado_por»\n    contribution: Optional[str] = None          # «aportacion» (1.22+; «afirma» before): one line on what it holds\n    description: str = ""                       # its line in the area\'s «Proyectos» index\n\n\n@dataclass\nclass WorkshopFile:\n    """A file in taller/. Workshop is never shown as current; the record holds only what the board lists."""\n    path: str                                   # relative to taller/\n    title: Optional[str] = None\n    updated: Optional[str] = None\n\n\n@dataclass\nclass IndexEntry:\n    """A project line of the «Proyectos» block of area.md, with its deliverable sub-lines."""\n    slug: str\n    description: str\n    restricted: bool = False                    # the description starts with «restringido»\n    deliverables: dict[str, dict] = field(default_factory=dict)   # stem -> {"description", "updated"}\n    notes: list[str] = field(default_factory=list)\n\n\n@dataclass\nclass Project:\n    """A project folder: proyecto.md, decisiones.md, sesiones.md, entregables/, taller/, fuentes/, restringido/."""\n    area: str\n    slug: str\n    restricted: bool = False                    # restricted projects keep only their index line: nothing inside is read\n    state: Optional[str] = None                 # proyecto.md «estado»\n    updated: Optional[str] = None               # proyecto.md «actualizado»\n    title: str = ""\n    objective: str = ""                         # «Objetivo»\n    done_means: str = ""                        # «Terminado significa» (older roots)\n    scope: str = ""                             # «Alcance»\n    status: Optional[Status] = None\n    steps: list[Step] = field(default_factory=list)       # «Siguientes pasos»\n    responsible: str = ""                       # «Quién participa»: «Responsable:» (1.22+) or «Dueño:» (1.21)\n    collaborators: list[str] = field(default_factory=list)   # «Colabora:» names (1.25) or «Name (email)» (1.22)\n    consumers: str = ""                         # «Consumen esto:» (older roots)\n    decisions: list[Decision] = field(default_factory=list)  # newest first\n    sessions: list[SessionEntry] = field(default_factory=list)  # newest first\n    deliverables: list[Deliverable] = field(default_factory=list)\n    workshop: list[WorkshopFile] = field(default_factory=list)\n    index: Optional[IndexEntry] = None          # its line in area.md, if any\n\n    @property\n    def key(self) -> str:\n        """The identifier the board and the queue use: "area--project"."""\n        return f"{self.area}--{self.slug}"\n\n    @property\n    def closed(self) -> bool:\n        return bool(self.status and self.status.finished_on)\n\n\n@dataclass\nclass Area:\n    """An area folder: area.md and its projects."""\n    slug: str\n    row: Optional[AreaRow] = None               # its row in guia.md; None for a folder the table does not name\n    restricted: bool = False\n    state: Optional[str] = None\n    updated: Optional[str] = None\n    title: str = ""\n    what: str = ""                              # «Qué es»\n    status: Optional[Status] = None             # «Estatus» (1.22+) or «Panorama»\n    priorities: list[str] = field(default_factory=list)   # «Siguiente» of the Estatus, or «Prioridades ahora» (1.21)\n    responsible: str = ""                       # «Quién participa» of area.md\n    index: dict[str, IndexEntry] = field(default_factory=dict)\n    projects: list[Project] = field(default_factory=list)\n\n\n@dataclass\nclass Root:\n    """A whole root: the folder with guia.md and metodo.md at its first level."""\n    name: str\n    organization: str = ""                      # what goes before «·» in the H1 of guia.md\n    method_line: str = ""                       # first line of metodo.md: version and fingerprint\n    method_version: Optional[tuple[int, ...]] = None\n    method_fingerprint: Optional[str] = None\n    language: str = "es"                        # the root\'s language pack (language.py)\n    timezone: str = "America/Mexico_City"       # «Zona horaria:» of guia.md\n    context_owner: str = ""                     # «Contexto común:» (who answers for guia.md and base/)\n    administrator: str = ""                     # «Administra la carpeta:»\n    people: PeopleRegistry = field(default_factory=PeopleRegistry)\n    area_rows: list[AreaRow] = field(default_factory=list)\n    areas: list[Area] = field(default_factory=list)\n    premises: list[Premise] = field(default_factory=list)\n    warnings: list[str] = field(default_factory=list)\n\n    def area(self, slug: str) -> Optional[Area]:\n        return next((a for a in self.areas if a.slug == slug), None)\n\n    def project(self, key: str) -> Optional[Project]:\n        """By "area/project" or "area--project"."""\n        a, _, p = key.replace("--", "/").partition("/")\n        ar = self.area(a)\n        return next((x for x in ar.projects if x.slug == p), None) if ar else None\n\n    @property\n    def current_premises(self) -> list[Premise]:\n        replaced = {p.replaces for p in self.premises if p.replaces}\n        return [p for p in self.premises if p.id not in replaced]\n',
    'parse': '"""Text of one method file -> records. Pure functions: no I/O, no globals, no clock.\n\nPorted from the plugin scripts with the same rules; where `abrir.py`, `cerrar.py` and `generar_vista.py` each carry a\ncopy of a function (the «who writes» block, the restricted rule, the people registry), this is the one copy they will\ncall once step 0 moves them onto the package. `tests/test_parity.py` runs the script copies and these on the same\ninputs and fails on any difference.\n"""\nfrom __future__ import annotations\n\nimport datetime\nimport re\nimport unicodedata\nfrom typing import Optional\n\nfrom .language import ES, Pack\nfrom .records import (\n    Area, AreaRow, Decision, DecisionRef, Deliverable, IndexEntry, PeopleRegistry, Person, Premise, Project,\n    SessionEntry, Status, Step,\n)\n\nEMAIL = re.compile(r"[\\w.+\'-]+@[\\w-]+(?:\\.[\\w-]+)*")\n_WORD_COLLABORATES = re.compile(r"\\bco-?labor\\w*\\s*:?", re.I)\n_LINE_COLLABORATES = re.compile(r"^\\s*[-*]?\\s*\\**\\s*colabora[n]?\\s*\\**\\s*:", re.I)\n\n\n# ── text helpers ───────────────────────────────────────────────────────────────────────────────────────────────────\n\ndef frontmatter(text: str) -> tuple[dict, str]:\n    """(header, body). Inline lists «[a, b]» and multi-line «- a» lists become lists; everything else a string."""\n    m = re.match(r"^---\\n(.*?)\\n---\\n?", text, re.S)\n    fm: dict = {}\n    if not m:\n        return fm, text\n    last = None\n    for line in m.group(1).split("\\n"):\n        mm = re.match(r"^(\\w+):\\s*(.*)$", line)\n        if mm:\n            last = mm.group(1)\n            v = mm.group(2).strip()\n            fm[last] = ([x.strip().strip("\'\\"") for x in v[1:-1].split(",") if x.strip()]\n                        if v.startswith("[") and v.endswith("]") else v.strip("\'\\""))\n            continue\n        ml = re.match(r"^\\s+-\\s+(.*)$", line)\n        if ml and last:\n            if not isinstance(fm.get(last), list):\n                fm[last] = []\n            fm[last].append(ml.group(1).strip().strip("\'\\""))\n    return fm, text[m.end():]\n\n\ndef section(text: str, name: str) -> str:\n    m = re.search(r"^## " + re.escape(name) + r"\\s*\\n(.*?)(?=^## |\\Z)", text, re.S | re.M)\n    return m.group(1).strip() if m else ""\n\n\ndef h1(text: str) -> str:\n    m = re.search(r"^# (.+)$", text, re.M)\n    return m.group(1).strip() if m else ""\n\n\ndef bullets(text: str) -> list[str]:\n    return [s[2:].strip() for s in (l.strip() for l in text.split("\\n")) if s.startswith("- ")]\n\n\ndef dates_in(text: str) -> list[str]:\n    return re.findall(r"\\b(20\\d\\d-\\d\\d-\\d\\d)\\b", text or "")\n\n\ndef valid_date(d: Optional[str]) -> bool:\n    try:\n        datetime.date.fromisoformat(d)  # type: ignore[arg-type]\n        return True\n    except (ValueError, TypeError):\n        return False\n\n\ndef name_key(n: str) -> str:\n    """How two names compare: NFC, lowercase, without bold, quotes or parentheses, spaces joined. An accent counts."""\n    n = unicodedata.normalize("NFC", n or "").replace("\xa0", " ")\n    n = re.sub(r"\\s*\\([^)]*\\)", "", re.sub(r"[*_`«»\\"]", "", n))\n    return re.sub(r"\\s+", " ", n).strip(" .,;:").lower()\n\n\ndef heading_key(t: str) -> str:\n    """A heading to compare: without accents (NFC or NFD), case or punctuation."""\n    t = "".join(c for c in unicodedata.normalize("NFD", t or "") if unicodedata.category(c) != "Mn")\n    return re.sub(r"\\s+", " ", re.sub(r"[^a-z ]", "", t.lower())).strip()\n\n\n# ── restricted ─────────────────────────────────────────────────────────────────────────────────────────────────────\n\ndef is_restricted_cell(cell: str) -> bool:\n    """«Quién la lee» declares the area restricted: the word at the start («Restringida: …»), or «restringida» on its\n    own elsewhere («Dirección (restringida)») and not negated («nunca restringida», «antes restringida»)."""\n    c = cell or ""\n    if re.match(r"^[\\W_]*restringid[oa]s?\\b", c, re.I):\n        return True\n    return bool(re.search(r"\\brestringidas?\\b", c, re.I)) and not re.search(\n        r"\\b(?:nada|no|nunca|sin|antes)\\s+(?:[^\\s]+\\s+)?restringid", c, re.I)\n\n\ndef starts_restricted(line: str) -> bool:\n    """An index line «- `x/` — restringido: …» marks the project restricted."""\n    return bool(re.match(r"^[\\W_]*restringid[oa]\\b", line or "", re.I))\n\n\n# ── people ─────────────────────────────────────────────────────────────────────────────────────────────────────────\n\ndef people_registry(guia: str) -> PeopleRegistry:\n    """«Quién es quién» of guia.md. Same rules as registro_personas() in the scripts."""\n    lines, inside, declared = [], False, False\n    for l in unicodedata.normalize("NFC", guia or "").split("\\n"):\n        m = re.match(r"^\\s*#{2,3}\\s+(.*?)\\s*$", l)\n        if m:\n            inside = heading_key(m.group(1)) == "quien es quien"\n            declared = declared or inside\n        elif inside:\n            lines.append(l)\n    reg = PeopleRegistry(declared=declared)\n    two_names, two_accounts = set(), set()\n    for l in lines:\n        if not re.match(r"^\\s*[-*]\\s+\\S", l):\n            continue\n        fields = [c.strip() for c in re.split(r"\\s+·\\s+", l.strip()[1:].strip()) if c.strip()]\n        if not fields:\n            continue\n        p = Person(name=re.sub(r"\\s*\\([^)]*\\)", "", re.sub(r"[*_`]", "", fields[0])).strip())\n        if EMAIL.fullmatch(p.name.lower()):\n            p.accounts.add(p.name.lower()); p.name = "?"\n        elif EMAIL.search(p.name):\n            reg.warnings.append(f"«{fields[0]}»: el nombre y la cuenta van separados por « · »")\n        for c in fields[1:]:\n            cl = c.lower()\n            if EMAIL.fullmatch(cl):\n                p.accounts.add(cl)\n            elif re.search(r"\\bbaja\\b", cl):\n                p.left_on = (re.search(r"20\\d\\d-\\d\\d-\\d\\d", c) or [""])[0] or "sí"\n            elif re.match(r"^cuentas?\\s*:", cl):\n                p.accounts |= set(EMAIL.findall(cl))\n            elif re.match(r"^(en\\s+)?(google\\s+)?drive\\s*:", cl):\n                p.drive_accounts |= set(EMAIL.findall(cl))\n            elif re.match(r"^sin\\s+cuenta\\b", cl):\n                p.no_account = True\n            elif re.match(r"^sin\\s+confirmar\\b", cl):\n                p.unconfirmed = True\n            elif re.match(r"^tambi[eé]n\\s*:", cl):\n                p.aliases += [a.strip() for a in re.split(r"[,;]", c.split(":", 1)[1]) if a.strip()]\n            elif re.match(r"^de\\s*:", cl):\n                p.organization = c.split(":", 1)[1].strip()\n            elif re.match(r"^compartida\\s+con\\s*:", cl):\n                p.shared_with = c.split(":", 1)[1].strip()\n            elif re.match(r"^registra\\s*:", cl):\n                p.registered_by = c.split(":", 1)[1].strip()\n            else:\n                reg.warnings.append(f"«{p.name}»: no se entiende «{c}» (van un correo, «sin cuenta», «en Drive: correo», «también: nombre», «de: organización» o «baja AAAA-MM-DD»)")\n        if p.no_account and p.accounts:\n            reg.warnings.append(f"«{p.name}» dice «sin cuenta» y lleva una cuenta: se queda la cuenta")\n            p.no_account = False\n        if not p.accounts and not p.no_account and not p.left_on:\n            reg.warnings.append(f"«{p.name}» no lleva ni su cuenta ni «sin cuenta»")\n        reg.people.append(p)\n        for n in ([p.name] if p.name != "?" else []) + p.aliases:\n            k = name_key(n)\n            if k in reg.by_name and reg.by_name[k] is not p:\n                two_names.add(k)\n                reg.warnings.append(f"«{n}» está dos veces: dos personas con el mismo nombre se distinguen con el segundo apellido o una inicial (mientras, ese nombre no es de nadie)")\n            reg.by_name.setdefault(k, p)\n        for c in p.accounts:\n            if c in reg.by_account and reg.by_account[c] is not p:\n                two_accounts.add(c)\n                reg.warnings.append(f"la cuenta {c} está en dos líneas («{reg.by_account[c].name}» y «{p.name}»; mientras, no es de nadie)")\n            reg.by_account.setdefault(c, p)\n    for k in two_names:\n        reg.by_name.pop(k, None)\n    for c in two_accounts:\n        reg.by_account.pop(c, None)\n    return reg\n\n\ndef find_person(name_or_account: str, reg: PeopleRegistry) -> Optional[Person]:\n    t = (name_or_account or "").strip()\n    if EMAIL.fullmatch(t.lower()):\n        return reg.by_account.get(t.lower())\n    return reg.by_name.get(name_key(t))\n\n\ndef names_in(text: str, reg: Optional[PeopleRegistry] = None) -> list[str]:\n    """The names of a cell or line («Colabora: Ana Ruiz, Luis Mejía»), split by «,» or «;», and by « y » / « e » only\n    when the whole piece is not a registered name."""\n    reg = reg or PeopleRegistry()\n    t = re.sub(r"^\\s*[-*]?\\s*\\**\\s*(?:colabora[n]?|lo leen?|responsable)\\s*\\**\\s*:\\s*\\**", "", text or "", flags=re.I)\n    t = re.sub(r"\\s*\\([^)]*\\)", "", t)\n    out: list[str] = []\n    for piece in re.split(r"[,;]", t):\n        piece = piece.strip(" .*")\n        if not piece or piece.lower() in ("—", "-", "nadie", "ninguno", "ninguna"):\n            continue\n        if find_person(piece, reg) is not None or not re.search(r"\\s(?:y|e)\\s", piece):\n            out.append(piece)\n        else:\n            out += [x.strip(" .*") for x in re.split(r"\\s+(?:y|e)\\s+", piece) if x.strip(" .*")]\n    return out\n\n\ndef accounts_of_names(text: str, reg: PeopleRegistry) -> tuple[set[str], list[str]]:\n    out, missing = set(), []\n    for n in names_in(text, reg):\n        p = find_person(n, reg)\n        if p is None:\n            missing.append(n)\n        elif not p.left_on:\n            out |= p.accounts\n    return out, missing\n\n\ndef account_cell(cell: str) -> tuple[set[str], set[str], Optional[str]]:\n    """(responsible, collaborators, warning) of a «Cuenta» cell «resp@x · colabora: a@x, b@x» (up to 1.24). Fails closed."""\n    text = (cell or "").lower()\n    parts = _WORD_COLLABORATES.split(text, maxsplit=1)\n    before = set(EMAIL.findall(parts[0]))\n    after = set(EMAIL.findall(parts[1])) if len(parts) > 1 else set()\n    warning = None\n    if len(before) > 1:\n        warning = "más de un correo antes de «colabora:»; nadie es responsable hasta que se corrija"\n        before = set()\n    elif not before:\n        warning = "sin el correo del responsable"\n    elif len(parts) > 1 and not re.search(r"\\bcolabora\\s*:", text):\n        warning = "la palabra para quien colabora va escrita «colabora:»"\n    return before, after, warning\n\n\ndef _people_columns(header: list[str]) -> dict:\n    n = [heading_key(x) for x in header]\n    pos = lambda *ns: next((i for i, x in enumerate(n) if x in ns), None)\n    return {"responsible": pos("responsable", "dueno", "duena"), "account": pos("cuenta", "cuentas"),\n            "collaborates": pos("colabora", "colaboran", "colaboradores", "colaboradoras")}\n\n\ndef row_accounts(header: list[str], cells: list[str], reg: PeopleRegistry) -> tuple[set[str], set[str], Optional[str]]:\n    """(responsible, collaborators, warning) of an area row: from the «Cuenta» emails up to 1.24, from the «Colabora»\n    names and the registry in 1.25. Same as fila_cuentas()."""\n    col = _people_columns(header)\n    cell = lambda i: cells[i] if i is not None and i < len(cells) else ""\n    if col["account"] is not None or col["collaborates"] is None:\n        return account_cell(cell(col["account"] if col["account"] is not None else 3))\n    if not reg.declared:\n        return set(), set(), "la tabla nombra a quien colabora por su nombre y guia.md no tiene «Quién es quién»"\n    resp = re.sub(r"\\s*\\((?=[a-záéíóúñ`])[^)]*\\)", "", cell(col["responsible"] if col["responsible"] is not None else 2))\n    rn = names_in(resp, reg)\n    warnings, of = [], set()\n    if len(rn) > 1 and find_person(rn[0], reg) is not None:\n        warnings.append(f"en Responsable, lo que sigue a «{rn[0]}» va en «Qué es»")\n        rn = rn[:1]\n    if len(rn) != 1:\n        warnings.append("el responsable es una sola persona del registro" if rn else "sin responsable")\n    else:\n        p = find_person(rn[0], reg)\n        if p is None:\n            warnings.append(f"«{rn[0]}» no está en «Quién es quién»")\n        elif p.left_on:\n            warnings.append(f"«{p.name}» está de baja")\n        elif p.accounts:\n            of = set(p.accounts)\n        elif p.registered_by and find_person(p.registered_by, reg) and find_person(p.registered_by, reg).accounts:\n            of = set(find_person(p.registered_by, reg).accounts)\n        else:\n            warnings.append(f"«{p.name}» no tiene cuenta: o la tiene, o su línea dice «registra: Nombre» de quien escribe por ella")\n    co, missing = accounts_of_names(cell(col["collaborates"]), reg)\n    warnings += [f"«{n}» (Colabora) no está en «Quién es quién»" for n in missing]\n    return of, co - of, "; ".join(warnings) or None\n\n\ndef provisional_people(who: str, reg: PeopleRegistry) -> list[tuple[str, str]]:\n    """[(name, email)] of «Colabora: Name (email)» for someone not in the registry: the provisional entry (1.25)."""\n    out: list[tuple[str, str]] = []\n    if not reg.declared:\n        return out\n    for l in (who or "").split("\\n"):\n        if _LINE_COLLABORATES.match(l):\n            for n, c in re.findall(r"([^,;(:]+?)\\s*\\(\\s*(" + EMAIL.pattern + r")\\s*\\)", l):\n                n = n.strip(" .*")\n                if find_person(n, reg) is None and c.lower() not in reg.by_account:\n                    out.append((n, c.lower()))\n    return out\n\n\ndef collaborator_accounts(who: str, reg: Optional[PeopleRegistry] = None) -> set[str]:\n    """The accounts of the «Colabora:» lines of a project\'s «Quién participa». Same as colaboran_en()."""\n    reg = reg or PeopleRegistry()\n    out: set[str] = set()\n    for l in (who or "").split("\\n"):\n        if _LINE_COLLABORATES.match(l):\n            if reg.declared:\n                out |= accounts_of_names(l, reg)[0] | {c for _, c in provisional_people(l, reg)}\n            else:\n                out |= set(EMAIL.findall(l.lower()))\n    return out\n\n\n# ── guia.md ────────────────────────────────────────────────────────────────────────────────────────────────────────\n\ndef _area_columns(header: list[str]) -> dict:\n    n = [re.sub(r"[*_`]", "", x).strip().lower() for x in header]\n    pos = lambda *ns, default=None: next((i for i, x in enumerate(n) if x in ns), default)\n    return {"responsible": pos("responsable", "dueño", "dueno", default=2), "account": pos("cuenta", "colabora", default=3),\n            "readers": pos("quién la lee", "quien la lee", default=4), "access": pos("acceso"), "what": pos("qué es", "que es", default=1)}\n\n\ndef area_is_restricted(cells: list[str], header: list[str]) -> bool:\n    """With an «Acceso» column (1.22+), its word; otherwise, or when it is empty or unclear, the «Quién la lee» rule.\n    In 1.25 («Colabora» column) an unclear «Acceso» fails closed. Same as area_restringida() in abrir.py."""\n    col = _area_columns(header)\n    if col["access"] is not None and col["access"] < len(cells):\n        v = cells[col["access"]]\n        if re.match(r"^[\\W_]*restringid[oa]s?\\b", v, re.I):\n            return True\n        if re.match(r"^[\\W_]*abiert[oa]s?\\b", v, re.I):\n            return False\n    if _people_columns(header)["collaborates"] is not None:\n        return True\n    return is_restricted_cell(cells[col["readers"]] if col["readers"] < len(cells) else "")\n\n\ndef _table_rows(block: str) -> tuple[Optional[list[str]], list[list[str]]]:\n    header, rows = None, []\n    for l in block.split("\\n"):\n        s = l.strip()\n        if not s.startswith("|"):\n            continue\n        cells = [c.strip() for c in s.strip("|").split("|")]\n        if re.match(r"^\\|[\\s:|-]+\\|?\\s*$", s):\n            continue\n        if header is None:\n            header = cells\n        else:\n            rows.append(cells)\n    return header, rows\n\n\ndef area_rows(guia: str, reg: PeopleRegistry, lang: Pack = ES) -> list[AreaRow]:\n    header, rows = _table_rows(section(guia, lang.areas))\n    if header is None:\n        return []\n    col = _area_columns(header)\n    pcol = _people_columns(header)\n    out = []\n    for cells in rows:\n        m = re.search(r"`([^`/]+)/?`", cells[0]) if cells else None\n        if not m:\n            continue\n        get = lambda i: cells[i] if i is not None and i < len(cells) else ""\n        resp_acc, coll_acc, warning = row_accounts(header, cells, reg)\n        collaborators = (names_in(get(pcol["collaborates"]), reg) if pcol["collaborates"] is not None and pcol["account"] is None\n                         else sorted(coll_acc))\n        out.append(AreaRow(\n            slug=m.group(1), what=get(col["what"]), responsible=get(col["responsible"]),\n            responsible_accounts=resp_acc, collaborators=collaborators, collaborator_accounts=coll_acc,\n            readers=get(col["readers"]), access=get(col["access"]), restricted=area_is_restricted(cells, header),\n            warnings=[warning] if warning else []))\n    return out\n\n\ndef guia_line(guia: str, label: str) -> str:\n    m = re.search(r"^\\s*[-*]?\\s*\\**\\s*" + label + r"\\s*\\**\\s*:\\s*(.+)$", guia or "", re.M | re.I)\n    return m.group(1).strip() if m else ""\n\n\ndef timezone_of(guia: str, default: str = "America/Mexico_City") -> str:\n    m = re.search(r"^\\s*[-*]?\\s*\\**\\s*zona horaria\\s*\\**\\s*:\\s*\\**\\s*`?\\s*([A-Za-z0-9_+-]+(?:/[A-Za-z0-9_+-]+){0,2})",\n                  guia or "", re.M | re.I)\n    return m.group(1) if m and not m.group(1).startswith("[") else default\n\n\ndef method_line(first_line: str) -> tuple[Optional[tuple[int, ...]], Optional[str]]:\n    m = re.search(r"versi[oó]n\\s+(\\d+(?:\\.\\d+)*)", first_line or "", re.I)\n    h = re.search(r"huella\\s+([0-9a-f]+)", first_line or "", re.I)\n    return (tuple(int(x) for x in m.group(1).split(".")) if m else None), (h.group(1) if h else None)\n\n\ndef premises(text: str) -> list[Premise]:\n    out = []\n    for l in (text or "").split("\\n"):\n        m = re.match(r"^\\s*-\\s*(P\\d+)\\s*·\\s*(.+)$", l)\n        if not m:\n            continue\n        parts = [x.strip() for x in m.group(2).split("·")]\n        rep = next((re.search(r"P\\d+", x, re.I).group(0).upper() for x in parts[1:]\n                    if re.match(r"reemplaza\\b", x, re.I) and re.search(r"P\\d+", x, re.I)), None)\n        date = next((x for x in parts[1:] if re.fullmatch(r"20\\d\\d-\\d\\d-\\d\\d", x)), "")\n        conf = next((x.split(":", 1)[1].strip() for x in parts[1:] if re.match(r"confirm[oó]\\s*:", x, re.I)), "")\n        out.append(Premise(id=m.group(1).upper(), text=parts[0], line=l.strip(), confirmed_by=conf, date=date, replaces=rep))\n    return out\n\n\n# ── Estatus ────────────────────────────────────────────────────────────────────────────────────────────────────────\n\ndef status(body: str, legacy: Optional[tuple] = None, lang: Pack = ES) -> Optional[Status]:\n    """The «Estatus» of proyecto.md or area.md, or the first legacy section present (the project\'s by default)."""\n    legacy = lang.status_legacy_project if legacy is None else legacy\n    text, source = section(body, lang.status), lang.status\n    if not text:\n        source = next((n for n in legacy if section(body, n)), "")\n        if not source:\n            return None\n        text = section(body, source)\n    st = Status(source=source, text=text)\n    m = re.search(re.escape(lang.finished_marker) + r"\\s*(20\\d\\d-\\d\\d-\\d\\d)", text)\n    if m:\n        st.finished_on = m.group(1)\n    if source != lang.status:\n        st.date = (dates_in(text.split("\\n", 1)[0]) or [""])[0]\n        return st\n    lines = text.split("\\n")\n    first = lines[0] if lines else ""\n    mh = re.match(r"^\\s*(20\\d\\d-\\d\\d-\\d\\d)\\s*·\\s*(.*)$", first)\n    if mh:\n        st.date = mh.group(1)\n        st.headline = re.sub(r"^\\*\\*(.*)\\*\\*$", r"\\1", mh.group(2).strip())\n    current = None\n    for l in lines[1:]:\n        mf = re.match(r"^\\s*[-*]\\s*\\**\\s*([^:*]+?)\\s*(?::\\s*\\**|\\**\\s*:)\\s*(.*)$", l)\n        key = lang.status_fields.get(heading_key(mf.group(1))) if mf and not l.startswith("  ") else None\n        if key:\n            current = key\n            rest = mf.group(2).strip()\n            if key == "next":\n                if rest:\n                    st.next.append(rest)\n            else:\n                setattr(st, key, rest)\n            continue\n        if current == "next" and re.match(r"^\\s{2,}[-*]\\s+", l):\n            st.next.append(re.sub(r"^\\s+[-*]\\s+", "", l).strip())\n        elif current and l.strip() and current != "next":\n            setattr(st, current, (getattr(st, current) + "\\n" + l.strip()).strip())\n    return st\n\n\ndef area_priorities(body: str, lang: Pack = ES) -> list[str]:\n    """«Siguiente» of the area\'s Estatus (1.22+), or «Prioridades ahora» (1.21). The board\'s queue cites them by number."""\n    est = section(body, lang.status)\n    nxt = next((k for k, v in lang.status_fields.items() if v == "next"), "siguiente")\n    if est:\n        out, inside = [], False\n        for l in est.split("\\n"):\n            if re.match(r"^\\s*[-*]\\s*\\**\\s*" + nxt + r"\\s*:?\\s*\\**\\s*:?\\s*(.*)$", l, re.I):\n                rest = re.sub(r"^\\s*[-*]\\s*\\**\\s*" + nxt + r"\\s*:?\\s*\\**\\s*:?\\s*", "", l, flags=re.I).strip()\n                if rest:\n                    out.append(rest)\n                inside = True; continue\n            if inside and re.match(r"^\\s{2,}[-*]\\s+", l):\n                out.append(re.sub(r"^\\s+[-*]\\s+", "", l).strip()); continue\n            if inside and l.strip():\n                inside = False\n        return out\n    return bullets(section(body, lang.priorities_legacy))\n\n\n# ── decisiones.md and sesiones.md ──────────────────────────────────────────────────────────────────────────────────\n\ndef decision_ref(text: str) -> Optional[DecisionRef]:\n    """«area/project#2026-10-15-2 (…)» or «premisa P3»; None for an empty field."""\n    t = (text or "").strip()\n    if not t:\n        return None\n    mp = re.search(r"\\bpremisa\\s+(P\\d+)", t, re.I)\n    if mp:\n        return DecisionRef("premisa", mp.group(1).upper(), t)\n    m = re.search(r"`?([a-z0-9][\\w.-]*)/([a-z0-9][\\w.-]*)#(20\\d\\d-\\d\\d-\\d\\d(?:-\\d+)?)", t)\n    return DecisionRef(f"{m.group(1)}--{m.group(2)}", m.group(3), t) if m else DecisionRef(None, None, t)\n\n\ndef decisions(text: str, live: Optional[int] = None, lang: Pack = ES) -> list[Decision]:\n    """The entries of decisiones.md, newest first. With `live`, entries after the first `live` come from an archive."""\n    raw: list[dict] = []\n    for p in re.split(r"^## ", text or "", flags=re.M)[1:]:\n        head, _, body = p.partition("\\n")\n        mm = re.match(r"(20\\d\\d-\\d\\d-\\d\\d)\\s*·\\s*(.*)", head.strip())\n        date, title = (mm.group(1), mm.group(2).strip()) if mm else ((dates_in(head) or [""])[0], head.strip())\n        f = {k: "" for _, k in lang.decision_fields}\n        current = None\n        for l in body.split("\\n"):\n            s = l.strip()\n            low = s.lower()\n            hit = next((k for pre, k in lang.decision_fields if low.startswith(pre)), None)\n            if hit:\n                current = hit; f[hit] = s.split(":", 1)[1].strip()\n            elif current and s:\n                f[current] += "\\n" + s\n        raw.append({"date": date, "title": title, **f})\n    out: list[Decision] = []\n    for i, r in enumerate(raw):\n        d = Decision(id="", date=r["date"], title=r["title"], decided_by=r["decided_by"], why=r["why"],\n                     discarded=r["discarded"], affects=r["affects"], raised_by=r["raised_by"],\n                     challenges=decision_ref(r["challenges"]), responds_to=decision_ref(r["responds_to"]),\n                     replaces=decision_ref(r["replaces"]),\n                     pending_confirmation=bool(re.search(lang.pending_confirmation, r["decided_by"].lower())),\n                     archived=live is not None and i >= live)\n        if r["challenges"] or re.match(lang.challenge_title + r"\\b", d.title, re.I):\n            d.kind = "challenge"\n            t = re.sub(r"^" + lang.challenge_title + r"\\s*:\\s*", "", d.title, flags=re.I) or d.title\n            d.title = t[:1].upper() + t[1:]\n        out.append(d)\n    count: dict[str, int] = {}\n    for d in reversed(out):\n        if not valid_date(d.date):\n            continue\n        n = count[d.date] = count.get(d.date, 0) + 1\n        d.id = d.date + ("" if n == 1 else f"-{n}")\n    out.sort(key=lambda d: d.date, reverse=True)\n    return out\n\n\ndef sessions(text: str, live: Optional[int] = None, lang: Pack = ES) -> list[SessionEntry]:\n    docs = "|".join(re.escape(x) for x in lang.session_wrote + lang.session_published)\n    raw = re.split(r"^## ", text or "", flags=re.M)[1:]\n    out: list[SessionEntry] = []\n    for i, p in enumerate(raw):\n        head, _, body = p.partition("\\n")\n        e = SessionEntry(n=len(raw) - 1 - i, date=(dates_in(head) or [""])[0], title=head.strip(),\n                         archived=live is not None and i >= live)\n        current = None\n        for l in body.split("\\n"):\n            s = l.strip()\n            low = s.lower()\n            m_doc = re.match(r"^(" + docs + r")\\s*:\\s*(.*)$", low)\n            if m_doc:\n                current = None\n                target = e.wrote if m_doc.group(1) in lang.session_wrote else e.published\n                for r in s.split(":", 1)[1].split(","):\n                    r = r.strip().strip("`").strip()\n                    if r and lang.restricted not in r.split("/") and r not in target and len(target) < 20:\n                        target.append(r[:160])\n                continue\n            if low.startswith(lang.session_topic):\n                current = "topic"; e.topic = s.split(":", 1)[1].strip()\n            elif low.startswith(lang.session_progress):\n                current = "progress"; e.progress = s.split(":", 1)[1].strip()\n            elif low.startswith(lang.session_pending):\n                current = "pending"; e.pending = s.split(":", 1)[1].strip()\n            elif low.startswith(lang.session_by):\n                current = None\n                rest = s.split(":", 1)[1].strip()\n                e.by = re.split(r"\\s+[·\\-–—]\\s+|\\s*\\(", rest, maxsplit=1)[0].strip()[:80]\n                mv = re.search(r"plugin\\s+(\\d+(?:\\.\\d+)+)", rest)\n                e.plugin_version = mv.group(1) if mv else ""\n            elif current and s:\n                setattr(e, current, getattr(e, current) + "\\n" + s)\n        out.append(e)\n    out.sort(key=lambda e: e.date, reverse=True)\n    return out\n\n\n# ── area.md and proyecto.md ────────────────────────────────────────────────────────────────────────────────────────\n\ndef project_index(area_text: str, lang: Pack = ES) -> dict[str, IndexEntry]:\n    """The «Proyectos» block of area.md: one entry per «- `slug/` — description», with its deliverable sub-lines."""\n    idx: dict[str, IndexEntry] = {}\n    current = None\n    for l in section(area_text, lang.projects).split("\\n"):\n        m1 = re.match(r"^- `([^`]+?)/?`\\s*[—–:-]?\\s*(.*)$", l)\n        if m1 and ("/" in m1.group(1) or m1.group(1).startswith(".")):\n            current = None; continue\n        if m1:\n            current = m1.group(1)\n            desc = m1.group(2).strip()\n            idx[current] = IndexEntry(slug=current, description=desc, restricted=starts_restricted(desc))\n            continue\n        m2 = re.match(r"^\\s+- (.*)$", l)\n        if m2 and current:\n            item = m2.group(1).strip()\n            m3 = re.match(r"^([\\w\\-, ]+?)\\s+[—–-]\\s+(.*?)(?:\\s*·\\s*actualizado\\s*(20\\d\\d-\\d\\d-\\d\\d))?\\s*$", item)\n            if m3 and m3.group(3):\n                for stem in [s.strip() for s in m3.group(1).split(",")]:\n                    idx[current].deliverables[stem] = {"description": m3.group(2).strip(), "updated": m3.group(3)}\n            else:\n                idx[current].notes.append(item)\n    return idx\n\n\ndef who_takes_part(body: str, lang: Pack = ES) -> tuple[str, list[str], str, str]:\n    """(responsible, collaborator lines\' names, consumers, raw section) of «Quién participa»."""\n    raw = section(body, lang.who)\n    resp, coll, cons = "", [], ""\n    for l in raw.split("\\n"):\n        m = re.match(r"^\\s*[-*]?\\s*\\**\\s*(" + "|".join(lang.responsible_labels) + r")\\s*\\**\\s*:\\s*(.+)$", l, re.I)\n        if m and not resp:\n            resp = re.sub(r"\\s*\\([^)]*\\)\\s*$", "", m.group(2).strip()).strip()\n        elif _LINE_COLLABORATES.match(l):\n            coll += names_in(l)\n        else:\n            mc = re.match(r"^\\s*[-*]?\\s*" + lang.consumers_label + r"\\s*:\\s*(.+)$", l, re.I)\n            if mc:\n                cons = mc.group(1).strip()\n    return resp, coll, cons, raw\n\n\ndef project_file(area: str, slug: str, text: str, lang: Pack = ES) -> Project:\n    fm, body = frontmatter(text or "")\n    resp, coll, cons, _ = who_takes_part(body, lang)\n    steps_ = [Step(text=b, dates=dates_in(b)) for b in bullets(section(body, lang.steps))]\n    return Project(area=area, slug=slug, state=fm.get(lang.key_state) or None, updated=fm.get(lang.key_updated) or None,\n                   title=h1(body), objective=section(body, lang.objective), done_means=section(body, lang.done_means),\n                   scope=section(body, lang.scope), status=status(body, lang=lang), steps=steps_, responsible=resp,\n                   collaborators=coll, consumers=cons)\n\n\ndef area_file(slug: str, text: str, lang: Pack = ES) -> Area:\n    fm, body = frontmatter(text or "")\n    resp, _, _, _ = who_takes_part(body, lang)\n    return Area(slug=slug, state=fm.get(lang.key_state) or None, updated=fm.get(lang.key_updated) or None, title=h1(body),\n                what=section(body, lang.what), status=status(body, legacy=lang.status_legacy_area, lang=lang),\n                priorities=area_priorities(body, lang), responsible=resp, index=project_index(text or "", lang))\n\n\ndef deliverable(file: str, text: Optional[str], index: Optional[IndexEntry], lang: Pack = ES) -> Deliverable:\n    stem = file.rsplit(".", 1)[0] if "." in file else file\n    d = Deliverable(file=file, name=stem, format=file.rsplit(".", 1)[1] if "." in file else "")\n    if text is not None and file.endswith(".md"):\n        fm, body = frontmatter(text)\n        d.title = h1(body) or None\n        d.state = fm.get(lang.key_state) or None\n        d.updated = fm.get(lang.key_updated) or None\n        if isinstance(fm.get(lang.key_based_on), list):\n            d.based_on = [re.sub(r"^\\./", "", b) for b in fm[lang.key_based_on]]\n        d.replaced_by = fm.get(lang.key_replaced_by) or None\n        new_key, old_key = lang.key_contribution\n        ap = fm.get(new_key) if isinstance(fm.get(new_key), str) and fm[new_key].strip() else fm.get(old_key)\n        if isinstance(ap, str) and ap.strip():\n            d.contribution = ap.strip()[:240]\n    ref = index.deliverables.get(stem) if index else None\n    if ref is None and index and stem.endswith("-en"):\n        ref = index.deliverables.get(stem[:-3])\n    if ref:\n        d.description = ref["description"]\n        d.updated = d.updated or ref["updated"]\n    return d\n\n\ndef context_owner_name(line: str) -> str:\n    """The name of «Contexto común: Name», without the account in parentheses or what follows a comma, stop or dash."""\n    t = re.sub(r"\\s*\\([^)]*\\)", "", (line or "").split(":", 1)[-1])\n    return re.split(r",|\\.\\s|\\.$|\\s[—–-]\\s|;", t.strip())[0].strip()\n\n\ndef context_owner_accounts(line: str, reg: PeopleRegistry) -> set[str]:\n    """The account in parentheses (up to 1.24) or the registry\'s for that name (1.25)."""\n    c = set(EMAIL.findall((line or "").split(":", 1)[-1].lower()))\n    if c:\n        return c\n    p = find_person(context_owner_name(line), reg)\n    return set(p.accounts) if p and not p.left_on else set()\n\n\ndef name_of_account(account: str, reg: PeopleRegistry) -> str:\n    p = reg.by_account.get((account or "").lower())\n    return p.name if p and p.name != "?" else ""\n\n\n# ── guia.md\'s first paragraph, and archived registers ──────────────────────────────────────────────────────────────\n\nABOUT_THE_FOLDER = r"`(?:metodo|guia)\\.md`|plugin `memoria`|Aquí solo está lo nuestro"\n\n\ndef drop_folder_talk(sentences: list[str], rx: str = ABOUT_THE_FOLDER) -> list[str]:\n    """The sentences of guia.md\'s first paragraph without what talks about the folder or the method. Of a sentence joined\n    by «;» to one that does not, the other stays (not split by a «;» in parentheses); within each part, what comes before\n    the comma, colon or dash that opens the folder talk stays if it has three words or more. Same as sin_carpeta()."""\n    out = []\n    for f in sentences:\n        if not re.search(rx, f):\n            out.append(f); continue\n        keep = []\n        for c in [c.strip() for c in re.split(r";(?![^()]*\\))", f)]:\n            m = re.search(rx, c) if c else None\n            if c and not m:\n                keep.append(c); continue\n            cuts = [s.start() for s in re.finditer(r"[,:—](?![^()]*\\))", c[:m.start()] if m else "")]\n            t = c[:cuts[-1]].strip() if cuts else ""\n            if len(t.split()) >= 3 and not re.search(rx, t):\n                keep.append(t)\n        if keep:\n            t = "; ".join(keep); t = t[0].upper() + t[1:]\n            out.append(t if t[-1] in ".!?" else t + ".")\n    return out\n\n\nARCHIVED = re.compile(r"^(sesiones|decisiones)-(20\\d\\d)(?:-(\\d+))?\\.md$")\n\n\ndef archived_names(names: list[str], register: str, year) -> list[str]:\n    """Of the names in a project folder, the archives of a register («sesiones» or «decisiones») from `year` - 1 on,\n    newest first. Older ones are not read whole (escribir.md, section 8)."""\n    seen = []\n    for n in names:\n        m = ARCHIVED.match(n)\n        if m and m.group(1) == register and int(m.group(2)) >= int(year) - 1:\n            seen.append((int(m.group(2)), int(m.group(3) or 1), n))\n    return [n for _, _, n in sorted(seen, reverse=True)]\n\n\ndef with_archives(live: Optional[str], archives: list[Optional[str]]) -> tuple[str, int]:\n    """(text, entries of the live register): the live register followed by the entries of its archives, as if they had\n    not been archived, so every decision keeps its identifier. Same as con_archivados()."""\n    parts = [live or ""]\n    for t in archives:\n        m = re.search(r"^## ", t or "", re.M)\n        if m:\n            parts.append((t or "")[m.start():])\n    return "\\n\\n".join(p.strip("\\n") for p in parts if p.strip()) + "\\n", len(re.findall(r"^## ", live or "", re.M))\n',
    'compat': '"""The scripts\' Spanish names over the package, with the shapes they use today (dicts and tuples).\n\nThe plugin scripts keep their Spanish until the language packs (decision of 2026-11-04). While each one moves onto the\npackage, it imports these names in place of its own copy of the code, and nothing else in the script changes. A script\nthat has moved no longer carries the copy; `packages/context-core/tests/test_compat.py` checks these return exactly what the copies do.\n"""\nfrom __future__ import annotations\n\nimport pathlib\nimport re\nfrom typing import Optional\n\nfrom . import parse\nfrom .records import PeopleRegistry, Person\n\n__all__ = ["SOBRE_LA_CARPETA", "sin_carpeta", "ARCHIVADO", "archivados_de", "con_archivados", "respuestas_viejas",\n           "restringida_celda", "CORREO", "PALABRA_COLABORA", "LINEA_COLABORA", "cuentas", "clave_nombre", "_titulo", "registro_personas",\n           "persona", "nombres_de", "cuentas_de_nombres", "altas_provisionales", "columnas_personas", "fila_cuentas",\n           "nombre_contexto", "cuentas_contexto", "nombre_de", "colaboran_en"]\n\nCORREO = parse.EMAIL\nPALABRA_COLABORA = parse._WORD_COLLABORATES\nLINEA_COLABORA = parse._LINE_COLLABORATES\n\ncuentas = parse.account_cell\nclave_nombre = parse.name_key\n_titulo = parse.heading_key\nnombre_contexto = parse.context_owner_name\n\n\ndef _persona(p: Person) -> dict:\n    return {"nombre": p.name, "cuentas": p.accounts, "drive": p.drive_accounts, "sin_cuenta": p.no_account,\n            "sin_confirmar": p.unconfirmed, "alias": p.aliases, "de": p.organization, "baja": p.left_on,\n            "compartida": p.shared_with, "registra": p.registered_by}\n\n\nclass _Registro(dict):\n    """registro_personas()\'s dict, carrying the PeopleRegistry it was made from."""\n    registry: PeopleRegistry\n\n\ndef _registro(reg: PeopleRegistry) -> _Registro:\n    dicts = {id(p): _persona(p) for p in reg.people}\n    r = _Registro(hay=reg.declared, personas=[dicts[id(p)] for p in reg.people],\n                  nombre={k: dicts[id(p)] for k, p in reg.by_name.items()},\n                  cuenta={k: dicts[id(p)] for k, p in reg.by_account.items()}, avisos=reg.warnings)\n    r.registry = reg\n    return r\n\n\ndef _reg(reg) -> PeopleRegistry:\n    """Accepts what the scripts pass: the dict from registro_personas(), None or {}."""\n    return getattr(reg, "registry", None) or PeopleRegistry()\n\n\ndef registro_personas(guia: str) -> dict:\n    return _registro(parse.people_registry(guia))\n\n\ndef persona(nombre: str, reg) -> Optional[dict]:\n    """The person with that name, alias or account; None if missing or ambiguous."""\n    t = (nombre or "").strip()\n    if CORREO.fullmatch(t.lower()):\n        return (reg or {}).get("cuenta", {}).get(t.lower())\n    return (reg or {}).get("nombre", {}).get(clave_nombre(t))\n\n\ndef nombres_de(texto: str, reg=None) -> list[str]:\n    return parse.names_in(texto, _reg(reg))\n\n\ndef cuentas_de_nombres(texto: str, reg) -> tuple[set, list]:\n    return parse.accounts_of_names(texto, _reg(reg))\n\n\ndef altas_provisionales(quien: str, reg) -> list:\n    return parse.provisional_people(quien, _reg(reg))\n\n\ndef columnas_personas(cab: list) -> dict:\n    c = parse._people_columns(cab)\n    return {"responsable": c["responsible"], "cuenta": c["account"], "colabora": c["collaborates"]}\n\n\ndef fila_cuentas(cab: list, celdas: list, reg) -> tuple:\n    return parse.row_accounts(cab, celdas, _reg(reg))\n\n\ndef cuentas_contexto(linea: str, reg) -> set:\n    return parse.context_owner_accounts(linea, _reg(reg))\n\n\ndef nombre_de(cuenta: str, reg) -> str:\n    return parse.name_of_account(cuenta, _reg(reg))\n\n\ndef colaboran_en(quien: str, reg=None) -> set:\n    return parse.collaborator_accounts(quien, _reg(reg) if reg else None)\n\n\n# ── el primer párrafo de guia.md, los registros con sus archivados y la regla de lo restringido ──────────────────────\n\nSOBRE_LA_CARPETA = parse.ABOUT_THE_FOLDER\nsin_carpeta = parse.drop_folder_talk\nARCHIVADO = parse.ARCHIVED\nrestringida_celda = parse.is_restricted_cell\n\n\ndef _nombres(carpeta) -> list:\n    try:\n        return [x.name for x in pathlib.Path(carpeta).iterdir()]\n    except OSError:\n        return []\n\n\ndef archivados_de(carpeta, nombre, anio) -> list:\n    return parse.archived_names(_nombres(carpeta), nombre, anio)\n\n\ndef con_archivados(carpeta, nombre, vivo, anio, leer_) -> tuple:\n    return parse.with_archives(vivo, [leer_(pathlib.Path(carpeta) / n) for n in archivados_de(carpeta, nombre, anio)])\n\n\ndef respuestas_viejas(carpeta, anio, leer_) -> list:\n    """The «Responde a:» lines of decision archives older than last year, which are not read whole."""\n    recientes = set(archivados_de(carpeta, "decisiones", anio))\n    out = []\n    for n in archivados_de(carpeta, "decisiones", 0):\n        if n not in recientes:\n            out += re.findall(r"^Responde a:[ \\t]*(.+)$", leer_(pathlib.Path(carpeta) / n) or "", re.M)\n    return out\n',
    }
    _pkg = _t.ModuleType("context_core"); _pkg.__path__ = []; _s.modules["context_core"] = _pkg
    for _n in ['language', 'records', 'parse', 'compat']:
        _m = _t.ModuleType("context_core." + _n); _m.__package__ = "context_core"
        _s.modules[_m.__name__] = _m
        exec(compile(_src[_n], "<context_core/" + _n + ".py>", "exec"), _m.__dict__)
        setattr(_pkg, _n, _m)
_context_core()
# --- end of context_core ---
from context_core.compat import (CORREO, PALABRA_COLABORA, LINEA_COLABORA, cuentas, clave_nombre, _titulo,  # noqa: E402
                                 registro_personas, persona, nombres_de, cuentas_de_nombres, altas_provisionales,
                                 columnas_personas, fila_cuentas, nombre_contexto, cuentas_contexto, nombre_de,
                                 colaboran_en)
# --- fin de quién escribe ---


from context_core.compat import restringida_celda  # noqa: E402  (desde el paso 0, en context_core)


def quienes(celda):
    """«Restringida: dirección» → «Dirección»; «Dirección (restringida)» → «Dirección»; lo demás, tal cual."""
    t = celda or ""
    if not restringida_celda(t):
        return t.strip()
    if re.match(r"^[\W_]*restringid[oa]s?\b", t, re.I):
        t = re.sub(r"^[\W_]*restringid[oa]s?\b[*_»\"”'’\s]*", "", t, flags=re.I)
    else:
        t = re.sub(r"\s*[(\[—–,-]?\s*\brestringidas?\b\s*[)\]]?", "", t, flags=re.I)
    t = re.sub(r"^[:—–,-]\s*", "", t.strip())
    t = re.sub(r"^(?:la|lo)\s+leen\s+", "", t, flags=re.I)
    t = re.sub(r"^(?:a|al|para|solo|sólo|únicamente)\s+", "", t, flags=re.I).strip()
    m = re.fullmatch(r"\((.*)\)", t)
    t = (m.group(1) if m else t).strip()
    return (t[:1].upper() + t[1:]) if t else ""


def zona_horaria(raiz, defecto="America/Mexico_City"):
    try:
        m = re.search(r"^\s*[-*]?\s*\**\s*zona horaria\s*\**\s*:\s*\**\s*`?\s*([A-Za-z0-9_+-]+(?:/[A-Za-z0-9_+-]+){0,2})",
                      (raiz / "guia.md").read_text(encoding="utf-8-sig"), re.M | re.I)
    except OSError:
        m = None
    try:
        from zoneinfo import ZoneInfo
    except Exception:
        return None
    for z in ([m.group(1)] if m and not m.group(1).startswith("[") else []) + [defecto]:
        try:
            return ZoneInfo(z)
        except Exception:
            continue
    return None


# ---------- leer y escribir ----------
def leer(p):
    b = p.read_bytes()
    t = b.decode("utf-8-sig")
    return t.replace("\r\n", "\n"), "\r\n" in t


def escribir(p, texto, crlf):
    if crlf:
        texto = texto.replace("\n", "\r\n")
    fd, tmp = tempfile.mkstemp(prefix="." + p.name + ".", suffix=".migrar-tmp", dir=p.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(texto)
        os.replace(tmp, p)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def partir(texto):
    """(cabecera con sus «---», prólogo hasta el primer «## » (el título), [(nombre, cuerpo)…])."""
    m = re.match(r"^---\n.*?\n---\n", texto, re.S)
    cab = m.group(0) if m else ""
    resto = texto[len(cab):]
    trozos = re.split(r"^(?=## )", resto, flags=re.M)
    prologo = trozos[0] if trozos and not trozos[0].startswith("## ") else ""
    secciones = []
    for t in trozos:
        if not t.startswith("## "):
            continue
        cabl, _, cuerpo = t.partition("\n")
        secciones.append((cabl[3:].strip(), cuerpo))
    return cab, prologo, secciones


def juntar(cab, prologo, secciones):
    out = cab + prologo
    if secciones and not out.endswith("\n\n"):
        out = out.rstrip("\n") + "\n\n"
    for i, (n, c) in enumerate(secciones):
        c = c.strip("\n")
        out += f"## {n}\n" + (c + "\n" if c else "") + ("\n" if i < len(secciones) - 1 else "")
    return out


def ordenar(secciones, orden):
    """Las secciones conocidas en el orden de la 1.22; las demás, después, en su orden de siempre."""
    conocidas = [s for n in orden for s in secciones if s[0] == n]
    otras = [s for s in secciones if s[0] not in orden]
    return conocidas + otras


def sec(secciones, nombre):
    return next((c for n, c in secciones if n == nombre), None)


def sin(secciones, *nombres):
    return [s for s in secciones if s[0] not in nombres]


def poner(secciones, nombre, cuerpo):
    if any(n == nombre for n, _ in secciones):
        return [(n, cuerpo if n == nombre else c) for n, c in secciones]
    return secciones + [(nombre, cuerpo)]


def clave_cabecera(texto, clave):
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    if not m:
        return None
    v = re.search(r"^" + re.escape(clave) + r":[ \t]*(.*)$", m.group(1), re.M)
    if not v:
        return None
    v = v.group(1).strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v or None


# ---------- las transformaciones ----------
FRASE = re.compile(r"^(.+?[.!?])(\s+|$)(.*)$", re.S)
FECHA_BLOQUE = re.compile(r"^\s*(20\d\d-\d\d-\d\d)\s*[·:—-]")


def fecha_bloque(cuerpo):
    m = FECHA_BLOQUE.match((cuerpo or "").strip())
    return m.group(1) if m else ""


def plantilla(t):
    """Un texto de plantilla sin rellenar («[Tres a cinco líneas…]»), que no es contenido."""
    return (t or "").strip().startswith("[")


def primera_frase(texto):
    """La primera frase de un texto, saltando las tablas, los encabezados y las viñetas que vayan delante; sin prosa, vacía."""
    parrafos = [x.strip() for x in re.split(r"\n\s*\n", (texto or "").strip()) if x.strip()]
    prosa = next((x for x in parrafos if not re.match(r"^(\||#|[-*]\s|\d+[.)]\s|```)", x)), "")
    if not prosa:
        return "", ""
    t = re.sub(r"\s*\n\s*", " ", prosa)
    mf = FRASE.match(t)
    return (mf.group(1), mf.group(3).strip()) if mf else (t, "")


def lista(cuerpo):
    """Las viñetas de un bloque, cada una en una línea (las continuaciones se pegan a la anterior)."""
    out = []
    for l in (cuerpo or "").split("\n"):
        t = l.strip()
        if not t:
            continue
        if re.match(r"^([-*]|\d+[.)])\s+", t):
            out.append(re.sub(r"^([-*]|\d+[.)])\s+", "", t))
        elif out:
            out[-1] += " " + t
        else:
            out.append(t)
    return out


def siguientes_de(estatus):
    """Las prioridades que cuelgan de «Siguiente» en un Estatus de área (sangradas debajo, o en la misma línea)."""
    out, dentro = [], False
    for l in (estatus or "").split("\n"):
        m = re.match(r"^\s*[-*]\s*\**\s*Siguiente\s*:?\s*\**\s*:?\s*(.*)$", l, re.I)
        if m:
            dentro = True
            if m.group(1).strip():
                out.append(m.group(1).strip())
            continue
        if dentro and re.match(r"^\s{2,}[-*]\s+", l):
            out.append(re.sub(r"^\s+[-*]\s+", "", l).strip()); continue
        if dentro and l.strip():
            dentro = False
    return out


def con_siguientes(estatus, nuevas):
    """Añade debajo de «Siguiente» las prioridades que el Estatus no tiene (por su texto); crea la línea si no está."""
    faltan = [x for x in nuevas if x and x not in (estatus or "")]
    if not faltan:
        return estatus
    lineas = (estatus or "").rstrip("\n").split("\n")
    idx = next((k for k, l in enumerate(lineas) if re.match(r"^\s*[-*]\s*\**\s*Siguiente\s*:?\s*\**\s*:?", l, re.I)), None)
    if idx is None:
        # después de «Se completó» si está, si no después de la primera línea
        idx = next((k for k, l in enumerate(lineas) if re.match(r"^\s*[-*]\s*\**\s*Se completó", l, re.I)), 0)
        lineas[idx + 1:idx + 1] = ["- **Siguiente:**"]
        idx += 1
    fin = idx + 1
    while fin < len(lineas) and re.match(r"^\s{2,}[-*]\s+", lineas[fin]):
        fin += 1
    lineas[fin:fin] = [f"  - {x}" for x in faltan]
    return "\n".join(lineas) + "\n"


def estatus_area(panorama, prioridades, proyectos=()):
    """El Estatus del área desde el Panorama y las Prioridades ahora de la 1.21, más una línea por proyecto activo,
    sin inventar nada: una plantilla sin rellenar no cuenta."""
    lineas = []
    p = (panorama or "").strip()
    if p and not plantilla(p):
        m = re.match(r"^(20\d\d-\d\d-\d\d)\s*·\s*(.+)$", p, re.S)
        fecha, texto = (m.group(1), m.group(2).strip()) if m else (None, p)
        frase, resto = primera_frase(texto)
        lineas.append((f"{fecha} · " if fecha else "") + f"**{frase}**" + (f" {resto}" if resto else ""))
    prios = [x for x in lista(prioridades) if not plantilla(x)]
    if prios:
        lineas.append("- **Siguiente:**")
        lineas += [f"  - {x}" for x in prios]
    lineas += [f"- `{slug}/`: {frase}" for slug, frase in proyectos if frase]
    return "\n".join(lineas)


def frase_proyecto(texto_proyecto):
    """La frase de estado de un proyecto para la línea del área: la de su Estatus o «En corto»; sin ellos, la primera
    de «Estado actual». Vacía si no hay o es plantilla."""
    _, _, ss = partir(texto_proyecto or "")
    for n in ("Estatus", "En corto"):
        c = (sec(ss, n) or "").strip()
        if c and not plantilla(c):
            l0 = c.split("\n")[0]
            l0 = re.sub(r"^20\d\d-\d\d-\d\d\s*[·:—-]\s*", "", l0).strip()
            return re.sub(r"\*\*(.+?)\*\*", r"\1", l0).strip()
    c = (sec(ss, "Estado actual") or "").strip()
    return "" if not c or plantilla(c) else primera_frase(c)[0]


def mas_reciente(a, b):
    """De dos bloques de estatus, el de fecha más nueva en su primera línea; en empate o sin fechas, el primero."""
    return b if fecha_bloque(b) > fecha_bloque(a) else a


def migrar_area(texto, carpeta, cambios, proyectos=()):
    """(texto nuevo, bloque viejo que va al taller o None)."""
    cab, prologo, ss = partir(texto)
    pan, pri, est = sec(ss, "Panorama"), sec(ss, "Prioridades ahora"), sec(ss, "Estatus")
    aparte = None
    if pan is not None or pri is not None:
        nuevo_est = estatus_area(pan, pri, proyectos)
        if est is None:
            ss = sin(ss, "Panorama", "Prioridades ahora")
            if nuevo_est:
                ss = poner(ss, "Estatus", nuevo_est + "\n")
            cambios.append("Panorama y Prioridades ahora → Estatus")
        else:
            # ya había Estatus (un cierre 1.22 sobre el área sin migrar, o un Panorama escrito después con la 1.21):
            # se queda el más reciente, las prioridades que falten entran en «Siguiente» y el otro va al taller
            gana = mas_reciente(est, nuevo_est) if pan is not None and not plantilla(pan) else est
            pierde = nuevo_est if gana is est else est
            gana = con_siguientes(gana, [x for x in lista(pri) if not plantilla(x)] + siguientes_de(pierde))
            ss = sin(ss, "Panorama", "Prioridades ahora")
            ss = poner(ss, "Estatus", gana.rstrip("\n") + "\n")
            if pierde and pierde.strip() and pierde.strip() != gana.strip():
                aparte = pierde
            cambios.append("Panorama y Prioridades ahora fundidos en el Estatus" + (" (el bloque que no ganó, al taller)" if aparte else ""))
    q = sec(ss, "Quién participa")
    if q is not None and re.search(r"^\s*[-*]?\s*\**\s*Due[ñn][oa]\s*\**\s*:", q, re.M):
        ss = poner(ss, "Quién participa", re.sub(r"^(\s*[-*]?\s*\**\s*)Due[ñn][oa](\s*\**\s*:)", r"\1Responsable\2", q, flags=re.M))
        cambios.append("Dueño → Responsable")
    pr = sec(ss, "Proyectos")
    if pr is not None:
        nuevo = re.sub(r"(restringid[oa]\s*:\s*)due[ñn][oa](\s+)", r"\1responsable\2", pr, flags=re.I)
        actual, out = None, []
        for l in nuevo.split("\n"):
            m = re.match(r"^- `([^`/]+)/?`", l)
            if m:
                actual = m.group(1)
            me = re.match(r"^(\s+- )([\w.-]+)( — )(.*?)(\s·\s*actualizado\s+20\d\d-\d\d-\d\d.*)?$", l)
            if actual and me:
                f = carpeta / actual / "entregables" / (me.group(2) + ".md")
                try:
                    t_ = f.read_text(encoding="utf-8-sig").replace("\r\n", "\n") if f.is_file() else ""
                except OSError:
                    t_ = ""
                ap = clave_cabecera(t_, "aportacion") or clave_cabecera(t_, "afirma")
                if ap and ap != me.group(4).strip():
                    l = f"{me.group(1)}{me.group(2)}{me.group(3)}{ap}{me.group(5) or ''}"
            out.append(l)
        nuevo = "\n".join(out)
        if nuevo != pr:
            ss = poner(ss, "Proyectos", nuevo)
            cambios.append("bloque Proyectos: «responsable» en los restringidos y la línea de los entregables desde su aportacion")
    ss2 = ordenar(ss, ["Estatus", "Qué es", "Proyectos", "Quién participa"])
    if [n for n, _ in ss2] != [n for n, _ in ss]:
        cambios.append("secciones en el orden de la 1.22")
    nuevo = juntar(cab, prologo, ss2)
    return (nuevo if cambios else texto), aparte


def migrar_proyecto(texto, cambios, mover_estado=True):
    """(texto nuevo, lo que va a taller/estado-anterior.md o None). Con mover_estado=False, «Estado actual» se queda."""
    cab, prologo, ss = partir(texto)
    estado = sec(ss, "Estado actual")
    corto = sec(ss, "En corto")
    est = sec(ss, "Estatus")
    aparte = []
    if corto is not None:
        if est is None:
            ss = [("Estatus" if n == "En corto" else n, c) for n, c in ss]
            cambios.append("En corto → Estatus")
        else:
            gana = mas_reciente(est, corto)
            pierde = corto if gana is est else est
            ss = sin(ss, "En corto")
            ss = poner(ss, "Estatus", gana)
            if pierde.strip():
                aparte.append(("## Estatus que no ganó al fundir", pierde))
            cambios.append("En corto y Estatus fundidos (el más reciente se queda; el otro, al taller)")
    cerrado = re.search(r"Proyecto terminado el\s*(20\d\d-\d\d-\d\d)", estado or "")
    est_txt = (sec(ss, "Estatus") or "").strip()
    act = clave_cabecera(texto, "actualizado") or ""
    if cerrado and "Proyecto terminado el" not in est_txt:
        # un proyecto cerrado lo decía en «Estado actual»: el Estatus dice que terminó y cómo acabó, y conserva lo que
        # ya tuviera debajo; no se crea archivo en el taller
        f = cerrado.group(1)
        lineas = est_txt.split("\n") if est_txt else []
        l0 = lineas[0] if lineas else ""
        fecha = fecha_bloque(l0) or f
        l0 = re.sub(r"^20\d\d-\d\d-\d\d\s*[·:—-]\s*", "", l0).strip()
        l0 = re.sub(r"\*\*(.+?)\*\*", r"\1", l0).strip()
        resto_estado = re.sub(r"\s*\n\s*", " ", re.sub(r".*?Proyecto terminado el\s*20\d\d-\d\d-\d\d\.?\s*", "", (estado or "").strip(), count=1, flags=re.S)).strip()
        como = l0 or primera_frase(resto_estado)[0]
        primera = f"{fecha} · **Proyecto terminado el {f}.**" + (f" {como}" if como else "")
        ss = poner(ss, "Estatus", "\n".join([primera] + lineas[1:]) + "\n")
        cambios.append("«Proyecto terminado» pasa al Estatus")
        if mover_estado and estado is not None:
            ss = sin(ss, "Estado actual")
            cambios.append("Estado actual resumido en el Estatus")
        estado = None   # nada va al taller
    elif not est_txt and estado is not None and estado.strip() and not plantilla(estado):
        # sin «En corto»: un Estatus mínimo con la fecha de la cabecera y la primera frase del estado, que ya era público
        frase, _ = primera_frase(estado)
        ss = poner(ss, "Estatus", (f"{act} · " if act else "") + f"**{frase}**\n")
        cambios.append("Estatus mínimo desde la primera frase de Estado actual")
    term = sec(ss, "Terminado significa")
    if term is not None:
        t = re.sub(r"\s*\n\s*", " ", term.strip())
        obj = (sec(ss, "Objetivo") or "").strip()
        if t and not plantilla(t):
            obj = (obj + (" " if obj else "") + t).strip()
        ss = sin(ss, "Terminado significa")
        ss = poner(ss, "Objetivo", obj + "\n")
        cambios.append("Terminado significa → segunda frase de Objetivo")
    al = sec(ss, "Alcance")
    if al is not None:
        n = re.sub(r"^(\s*[-*]?\s*\**\s*)S[íi](\s*\**\s*:)", r"\1Entra\2", al, flags=re.M)
        n = re.sub(r"(^|[.;]\s+|\s{2,})(\s*[-*]?\s*\**\s*)No(\s*\**\s*:)", r"\1\2No entra\3", n, flags=re.M)
        if n != al:
            ss = poner(ss, "Alcance", n)
            cambios.append("Alcance: Sí/No → Entra/No entra")
    q = sec(ss, "Quién participa")
    if q is not None:
        n = re.sub(r"^(\s*[-*]?\s*\**\s*)Due[ñn][oa](\s*\**\s*:)", r"\1Responsable\2", q, flags=re.M)
        n = re.sub(r"^\s*[-*]?\s*\**\s*Consumen esto\s*\**\s*:.*\n?", "", n, flags=re.M)
        if n != q:
            ss = poner(ss, "Quién participa", n)
            cambios.append("Quién participa: Responsable, sin Consumen esto")
    if estado is not None and mover_estado:
        ss = sin(ss, "Estado actual")
        cambios.append("Estado actual → taller/estado-anterior.md")
        if estado.strip():
            aparte.insert(0, ("## Estado actual", estado))
    ss2 = ordenar(ss, ["Estatus", "Objetivo", "Alcance", "Siguientes pasos", "Quién participa"])
    if [n for n, _ in ss2] != [n for n, _ in ss]:
        cambios.append("secciones en el orden de la 1.22")
    nuevo = juntar(cab, prologo, ss2)
    nuevo = renombrar_inventario(nuevo)
    return (nuevo if cambios or nuevo != texto else texto), (aparte or None)


def renombrar_inventario(t):
    return re.sub(r"\b(fuentes|restringido)/enlaces\.md\b", r"\1/inventario.md", t)


def migrar_cabecera(texto):
    """«afirma:» → «aportacion:» y basado_en a fuentes/inventario.md, solo dentro de la cabecera."""
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    if not m:
        return texto
    c = m.group(1)
    n = re.sub(r"^afirma:", "aportacion:", c, flags=re.M) if not re.search(r"^aportacion:", c, re.M) else re.sub(r"^afirma:.*\n?", "", c, flags=re.M)
    n = renombrar_inventario(n)
    return texto if n == c else f"---\n{n}\n---\n" + texto[m.end():]


def columnas(cabecera):
    n_ = [re.sub(r"[*_`]", "", x).strip().lower() for x in cabecera]
    pos = lambda *ns: next((i for i, x in enumerate(n_) if x in ns), None)
    return {"resp": pos("responsable", "dueño", "dueno"), "dueno": pos("dueño", "dueno"), "cuenta": pos("cuenta"),
            "lee": pos("quién la lee", "quien la lee"), "acc": pos("acceso")}


def migrar_guia(texto, cambios):
    """Solo la primera tabla de «## Áreas»: «Dueño» → «Responsable» en el encabezado y la columna «Acceso» detrás de
    «Quién la lee», que se deja tal cual (con «Restringida:» si lo lleva, para los plugins 1.21)."""
    m = re.search(r"^##\s+Áreas\s*\n(.*?)(?=^##\s|\Z)", texto, re.M | re.S)
    if not m:
        return texto
    lineas, col, out, en_tabla, tabla_hecha = m.group(1).split("\n"), None, [], False, False
    for l in lineas:
        if not l.startswith("|") or tabla_hecha:
            if en_tabla and not l.startswith("|"):
                tabla_hecha = True
            out.append(l); continue
        en_tabla = True
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if re.match(r"^\|[\s:|-]+\|?\s*$", l):
            out.append(l if col is None or col["ok"] else "|" + "|".join(["---"] * col["n"]) + "|"); continue
        if col is None:
            cc = columnas(c)
            col = {"lee": cc["lee"], "ok": cc["acc"] is not None or cc["lee"] is None, "n": len(c) + (1 if cc["acc"] is None and cc["lee"] is not None else 0)}
            if cc["dueno"] is not None:
                c[cc["dueno"]] = "Responsable"; cambios.append("guia.md: columna Dueño → Responsable")
            if cc["acc"] is None and cc["lee"] is not None:
                c.insert(cc["lee"] + 1, "Acceso"); cambios.append("guia.md: columna Acceso")
            out.append("| " + " | ".join(c) + " |"); continue
        if not col["ok"] and col["lee"] is not None and len(c) > col["lee"]:
            c.insert(col["lee"] + 1, "Restringida" if restringida_celda(c[col["lee"]]) else "Abierta")
        out.append("| " + " | ".join(c) + " |")
    nuevo = texto[:m.start(1)] + "\n".join(out) + texto[m.end(1):]
    n2 = renombrar_inventario(nuevo)
    if n2 != nuevo:
        cambios.append("guia.md: enlaces.md → inventario.md")
    return n2


def con_entrada_arriba(t, entrada):
    entrada = entrada.strip() + "\n"
    if entrada.strip() in t:
        return t
    m = re.search(r"^# .*\n", t, re.M)
    if m:
        i = m.end()
        resto = t[i:]
        j = re.search(r"^## ", resto, re.M)
        if j:
            prefacio = resto[:j.start()]
            prefacio = "\n" if not prefacio.strip() else prefacio.rstrip("\n") + "\n\n"
            return t[:i] + prefacio + entrada + "\n" + resto[j.start():]
        return t[:i] + "\n" + entrada + ("\n" + resto.lstrip("\n") if resto.strip() else "")
    return t.rstrip("\n") + "\n\n" + entrada


def cabecera_hoy(t, hoy):
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m:
        return t
    cab = re.sub(r"^actualizado:.*$", f"actualizado: {hoy}", m.group(1), count=1, flags=re.M)
    return f"---\n{cab}\n---\n" + t[m.end():]


def yaml_linea(t):
    """Una línea para una clave de cabecera entre comillas dobles: sin saltos y con las comillas escapadas."""
    return re.sub(r"\s*\n\s*", " ", (t or "")).replace("\\", "\\\\").replace('"', '\\"')


def archivo_taller(rel_p, titulo, act, bloques, nombre):
    """El archivo del taller que recibe lo que sale de un archivo vivo: cabecera, título y cada bloque con su encabezado."""
    cuerpo = "\n\n".join(f"{enc}\n\n{txt.strip()}" for enc, txt in bloques)
    return (f"---\nestado: borrador\nactualizado: {act}\n"
            f"aportacion: \"{yaml_linea(f'Lo que {nombre} decía antes de la 1.22 y salió de él al migrar; lo que siga valiendo va al Estatus o a Alcance.')}\"\n"
            f"basado_en:\n  - {rel_p}/{nombre}\n---\n\n# {titulo}: lo anterior a la 1.22\n\n{cuerpo}\n")


class Cerrojo:
    """Un cerrojo por archivo entre procesos de la misma computadora, el mismo que usa cerrar.py."""
    def __init__(self, p):
        h = hashlib.sha1(str(pathlib.Path(p).resolve()).encode()).hexdigest()[:16]
        self.ruta = os.path.join(tempfile.gettempdir(), f"memoria-cerrar-{h}.lock")
        self.f = None
    def __enter__(self):
        try:
            import fcntl
            self.f = open(self.ruta, "a+")
            fcntl.flock(self.f, fcntl.LOCK_EX)
        except Exception:
            self.f = None
        return self
    def __exit__(self, *a):
        if self.f:
            try:
                import fcntl
                fcntl.flock(self.f, fcntl.LOCK_UN)
            except Exception:
                pass
            self.f.close()


def fecha_de(p):
    """Cuándo cambió p en la computadora (segundos). Con consola, su fecha de archivo; sin consola (--sin-consola, sobre la
    copia), la que registró espejo.py con device_list_dir, porque la de la copia es la de la traída; sin registro, None."""
    if SIN_CONSOLA:
        try:
            e = json.loads(pathlib.Path(str(RAIZ_COPIA).rstrip("/") + ".estado.json").read_text(encoding="utf-8"))
            r = e.get("registrados", {}).get(pathlib.Path(p).relative_to(RAIZ_COPIA).as_posix())
            return r["mtimeMs"] / 1000 if r else None
        except (OSError, ValueError, KeyError):
            return None
    try:
        return pathlib.Path(p).stat().st_mtime
    except OSError:
        return None
SIN_CONSOLA, RAIZ_COPIA = False, None


# ---------- main ----------
def main(argv):
    if len(argv) < 2 or "--cuenta" not in argv:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    raiz = pathlib.Path(argv[1])
    global SIN_CONSOLA, RAIZ_COPIA
    SIN_CONSOLA, RAIZ_COPIA = "--sin-consola" in argv, raiz
    if not (raiz / "guia.md").is_file():
        print("La raíz es la carpeta con guia.md y metodo.md.", file=sys.stderr)
        return 2
    op = lambda k, d=None: argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else d
    cuenta = (op("--cuenta") or "").strip().lower()
    plan = "--plan" in argv
    version = op("--plugin", "1.22")
    tz = zona_horaria(raiz)
    hoy = datetime.datetime.now(tz).date().isoformat()

    guia, _ = leer(raiz / "guia.md")
    reg_ = registro_personas(guia)
    m = re.search(r"^##\s+Áreas\s*\n(.*?)(?=^##\s|\Z)", guia, re.M | re.S)
    areas, col = [], None
    for l in (m.group(1) if m else "").split("\n"):
        if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
            if col is not None and not l.startswith("|"):
                break   # solo la primera tabla de la sección
            continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if col is None:
            cc = columnas(c); cab_ = c
            col = {"resp": cc["resp"] if cc["resp"] is not None else 2, "cuenta": cc["cuenta"] if cc["cuenta"] is not None else 3}
            lee_, acc_ = cc["lee"] if cc["lee"] is not None else 4, cc["acc"]
            continue
        if len(c) > max(col.values()):
            # restringida como la lee abrir.py: «Acceso» si la hay; si no, o si no dice Abierta ni Restringida, «Quién la lee»
            v_acc = c[acc_] if acc_ is not None and acc_ < len(c) else ""
            restr = (True if re.match(r"^[\W_]*restringid[oa]s?\b", v_acc, re.I) else False if re.match(r"^[\W_]*abiert[oa]s?\b", v_acc, re.I)
                     else restringida_celda(c[lee_] if lee_ < len(c) else ""))
            _fc = fila_cuentas(cab_, c, reg_)
            areas.append({"slug": c[0].strip("`").rstrip("/"), "nombre": re.sub(r"\s*\([^)]*\)", "", c[col["resp"]]).strip(),
                          "responsables": _fc[0], "colaboran": _fc[1], "restringida": restr})
    ctx = ""
    for l in (re.search(r"^##\s+Quién responde por qué\s*\n(.*?)(?=^##\s|\Z)", guia, re.M | re.S) or [None, ""])[1].split("\n"):
        if l.strip().lower().lstrip("-* ").startswith("contexto común"):
            ctx = l
    # como abrir.py: la cuenta entre paréntesis en «Contexto común»; sin ella, la de las áreas cuyo responsable se llama igual
    cuenta_ctx = cuentas_contexto(ctx, reg_)
    nombre_ctx = re.sub(r"\s*\([^)]*\)", "", ctx.split(":", 1)[-1]).strip().rstrip(".").strip().lower()
    es_resp = cuenta in cuenta_ctx or (not cuenta_ctx and bool(nombre_ctx) and any(cuenta in a["responsables"] and a["nombre"].lower() == nombre_ctx for a in areas))
    propias = [a for a in areas if cuenta in a["responsables"]]
    nombre = op("--nombre") or nombre_de(cuenta, reg_) or (propias[0]["nombre"] if propias else cuenta)
    # el responsable de contexto migra todas las áreas con carpeta, también las de otros responsables y las restringidas
    # (1.22.1): es quien administra la carpeta y su dueño en Drive, y lo peor que puede pasar es que algo se quede sin migrar
    def motivo_ajena(a):
        return "sin carpeta en esta computadora" if not (raiz / a["slug"]).is_dir() else None
    mias = [a for a in areas if (cuenta in a["responsables"] and (raiz / a["slug"]).is_dir()) or (es_resp and cuenta not in a["responsables"] and not motivo_ajena(a))]
    salida = {"plan": plan, "hoy": hoy, "conflictos": [], "fallidos": [], "entradas": [], "resumen": {},
              "areas": [a["slug"] for a in mias], "ajenas": [a["slug"] for a in mias if cuenta not in a["responsables"]],
              "guia": False, "pendientes": [{"area": a["slug"], "motivo": motivo_ajena(a) if es_resp else "de otra cuenta: la migra su responsable"}
                                           for a in areas if a not in mias and cuenta not in a["responsables"]],
              "nuevos": [], "renombrados": [], "archivos": {}}
    # lo que se va a escribir: cada entrada es (ruta relativa, función texto→texto nuevo, o texto entero si es nuevo)
    # el orden importa: taller antes que proyecto.md, y la entrada de la bitácora al final
    tareas = []

    def anotar(rel, cambios):
        if cambios:
            salida["archivos"][rel] = cambios

    if es_resp:
        cambios = []
        nuevo = migrar_guia(guia, cambios)
        if nuevo != guia:
            salida["guia"] = True; anotar("guia.md", cambios)
            tareas.append(("guia.md", lambda t: migrar_guia(t, [])))

    for a in mias:
        carpeta = raiz / a["slug"]
        if not carpeta.is_dir():
            continue
        try:
            proyectos = sorted(d for d in carpeta.iterdir() if d.is_dir() and not d.name.startswith(".") and (d / "proyecto.md").is_file())
        except OSError as ex:
            salida["fallidos"].append({"ruta": a["slug"], "motivo": str(ex)}); continue
        # los proyectos declarados restringidos en el índice del área no llevan línea en su Estatus (contrato, sección 2)
        try:
            ta0, _ = leer(carpeta / "area.md")
        except (OSError, UnicodeDecodeError):
            ta0 = ""
        restringidos = set(re.findall(r"^- `([^`/]+)/?`\s*[—–:-]?\s*[\W_]*restringid[oa]\b", sec(partir(ta0)[2], "Proyectos") or "", re.M | re.I))
        frases, proy_area = [], []
        ajena = cuenta not in a["responsables"]
        en_uso = []
        for d in proyectos:
            rel_p = d.relative_to(raiz).as_posix()
            hecho = []
            try:
                tp, _ = leer(d / "proyecto.md")
            except (OSError, UnicodeDecodeError) as ex:
                salida["fallidos"].append({"ruta": rel_p + "/proyecto.md", "motivo": str(ex)}); continue
            # el cerrojo solo vale en esta computadora: en un área de otro responsable, un proyecto que alguien tocó hace
            # menos de EN_USO_MIN minutos puede estar abierto en otra máquina, y se deja para la siguiente apertura (1.22.2).
            # Solo si todavía tiene algo que migrar: lo ya migrado (también por esta misma migración hace un momento) no se
            # toca y no frena; y la fecha tiene que ser pasada: una futura es un reloj desfasado, y se dice aparte
            if ajena and (marcas_anteriores(tp[len(partir(tp)[0]):], "proyecto") or any((d / f).is_file() for f in ARCHIVOS_ANTERIORES)):
                reciente, futuro = [], []
                for n in ("proyecto.md", "sesiones.md"):
                    t = fecha_de(d / n)
                    if t is None:
                        continue
                    if t > time.time() + 60:
                        futuro.append(n)
                    elif time.time() - t < EN_USO_MIN * 60:
                        reciente.append(n)
                if reciente or futuro:
                    en_uso.append(f"{d.name} ({', '.join(reciente)}: cambió hace menos de {EN_USO_MIN} minutos)" if reciente
                                  else f"{d.name} ({', '.join(futuro)}: su fecha está en el futuro, un reloj desfasado)")
                    continue
            destino = d / "taller" / "estado-anterior.md"
            mover = not destino.exists()
            cambios = []
            nuevo, aparte = migrar_proyecto(tp, cambios, mover_estado=mover)
            if not mover and sec(partir(tp)[2], "Estado actual") is not None:
                salida["conflictos"].append({"ruta": rel_p + "/taller/estado-anterior.md", "motivo": "ya existía: «Estado actual» se queda en proyecto.md; lo demás se migró"})
            if nuevo != tp:
                anotar(rel_p + "/proyecto.md", cambios); hecho += cambios
                taller_rel = None
                if aparte:
                    act = clave_cabecera(tp, "actualizado") or hoy
                    titulo = (re.search(r"^# (.+)$", tp, re.M) or [None, d.name])[1]
                    taller_rel = rel_p + "/taller/estado-anterior.md"
                    tareas.append((taller_rel, archivo_taller(rel_p, titulo, act, aparte, "proyecto.md"))); salida["nuevos"].append(taller_rel)
                tareas.append((rel_p + "/proyecto.md", (lambda mv: (lambda t: migrar_proyecto(t, [], mover_estado=mv)[0]))(mover), taller_rel))
                proy_area.append(rel_p + "/proyecto.md")
            if not cerrado_en(tp) and d.name not in restringidos:
                fr = frase_proyecto(nuevo)
                if fr:
                    frases.append((d.name, fr))
            for sub in ("fuentes", "restringido"):
                v, n_ = d / sub / "enlaces.md", d / sub / "inventario.md"
                if v.is_file():
                    if n_.exists():
                        salida["conflictos"].append({"ruta": f"{rel_p}/{sub}/enlaces.md", "motivo": "ya hay un inventario.md al lado: no se pisa; juntarlos a mano"})
                    else:
                        salida["renombrados"].append([f"{rel_p}/{sub}/enlaces.md", f"{rel_p}/{sub}/inventario.md"]); hecho.append("inventario")
            for sub in ("entregables", "taller"):
                for dp, dn, fn in os.walk(d / sub):
                    dn[:] = [x for x in dn if not x.startswith(".")]
                    for f in fn:
                        if not f.endswith(".md") or f.startswith("."):
                            continue
                        p = pathlib.Path(dp) / f
                        rel = p.relative_to(raiz).as_posix()
                        try:
                            t, _ = leer(p)
                        except (OSError, UnicodeDecodeError) as ex:
                            salida["fallidos"].append({"ruta": rel, "motivo": str(ex)}); continue
                        if migrar_cabecera(t) != t:
                            anotar(rel, ["cabecera: afirma → aportacion, basado_en a inventario.md"]); hecho.append("cabecera")
                            tareas.append((rel, migrar_cabecera))
            if hecho:
                entrada = (f"## {hoy} (migracion)\nTema: la estructura del método pasa a la de la 1.22.\n"
                           f"Avances: secciones, claves y archivos renombrados por el plugin, sin cambiar contenido"
                           + ("; lo que salió de proyecto.md quedó en taller/estado-anterior.md" if any(k == rel_p + "/taller/estado-anterior.md" for k, *_ in tareas) else "")
                           + f".\nSesión de: {nombre}" + ("" if cuenta in a["responsables"] else f", responsable de contexto, por {a['nombre'] or 'el responsable del área'}")
                           + f" · plugin {version}" + (" · sin consola" if "--sin-consola" in argv else ""))
                # la entrada dice que se migró: solo si proyecto.md quedó escrito (si no, no se migró y no se registra)
                tareas.append((rel_p + "/sesiones.md#entrada", entrada, [rel_p + "/proyecto.md"] if rel_p + "/proyecto.md" in salida["archivos"] else None))
        pa = carpeta / "area.md"
        if en_uso:
            # sin todos sus proyectos, area.md no se migra: la pregunta vuelve y la siguiente apertura completa lo que falta
            salida["pendientes"].append({"area": a["slug"], "motivo": f"en uso: {'; '.join(en_uso)}; puede estar en sesión en otra computadora y se completa en la siguiente apertura"})
            salida["areas"].remove(a["slug"]); salida["ajenas"].remove(a["slug"])
        if pa.is_file() and not en_uso:
            try:
                ta, _ = leer(pa)
            except (OSError, UnicodeDecodeError) as ex:
                salida["fallidos"].append({"ruta": a["slug"] + "/area.md", "motivo": str(ex)}); continue
            cambios = []
            nuevo, aparte = migrar_area(ta, carpeta, cambios, frases)
            if nuevo != ta:
                anotar(a["slug"] + "/area.md", cambios)
                taller_rel = None
                if aparte:
                    # el bloque que no ganó va al taller del primer proyecto del área: el área no tiene taller propio
                    if proyectos:
                        dp0 = proyectos[0]
                        taller_rel = dp0.relative_to(raiz).as_posix() + "/taller/estatus-anterior-del-area.md"
                        if (raiz / taller_rel).exists():
                            salida["conflictos"].append({"ruta": taller_rel, "motivo": "ya existía: el bloque de estatus que no ganó no se guardó"}); taller_rel = None
                        else:
                            tareas.append((taller_rel, archivo_taller(a["slug"], a["slug"], clave_cabecera(ta, "actualizado") or hoy, [("## Estatus del área que no ganó al fundir", aparte)], "area.md"))); salida["nuevos"].append(taller_rel)
                    else:
                        salida["conflictos"].append({"ruta": a["slug"] + "/area.md", "motivo": "había dos bloques de estatus y el área no tiene proyectos donde guardar el que no ganó"})
                # area.md, que la apertura usa para dar el área por migrada, va al final y solo si todos sus proyectos
                # quedaron escritos: un proyecto que falló deja el área en la estructura anterior y la pregunta vuelve
                tareas.append((a["slug"] + "/area.md", (lambda cp, fr: (lambda t: migrar_area(t, cp, [], fr)[0]))(carpeta, frases), ([taller_rel] if taller_rel else []) + proy_area))

    resumen = {}
    for cambios in salida["archivos"].values():
        for c in cambios:
            resumen[c] = resumen.get(c, 0) + 1
    salida["resumen"] = resumen

    if plan:
        salida["entradas"] = [tarea[0][:-len("#entrada")] for tarea in tareas if tarea[0].endswith("#entrada")]
    else:
        escritos_ok = set()
        for tarea in tareas:
            rel, que = tarea[0], tarea[1]
            depende = tarea[2] if len(tarea) > 2 else None
            depende = [depende] if isinstance(depende, str) else (depende or [])
            falta = [x for x in depende if x not in escritos_ok]
            if falta:
                salida["fallidos"].append({"ruta": rel.split("#")[0], "motivo": f"no se escribió porque falló {', '.join(falta)}; nada se perdió, y repetir la migración lo completa"})
                salida["archivos"].pop(rel, None)
                continue
            try:
                if rel.endswith("#entrada"):
                    p = raiz / rel[:-len("#entrada")]
                    with Cerrojo(p):
                        t, c2 = leer(p)
                        escribir(p, cabecera_hoy(con_entrada_arriba(t, que), hoy), c2)
                    salida["entradas"].append(rel[:-len("#entrada")])
                elif isinstance(que, str):
                    p = raiz / rel
                    p.parent.mkdir(parents=True, exist_ok=True)
                    escribir(p, que, False)
                    escritos_ok.add(rel)
                else:
                    p = raiz / rel
                    with Cerrojo(p):
                        t, crlf = leer(p)   # se relee y se vuelve a transformar: lo que otro escribió entre medias se respeta
                        n = que(t)
                        if n != t:
                            escribir(p, n, crlf)
                    escritos_ok.add(rel)
            except (OSError, UnicodeDecodeError) as ex:
                salida["fallidos"].append({"ruta": rel.split("#")[0], "motivo": str(ex)})
        salida["nuevos"] = [r for r in salida["nuevos"] if r in escritos_ok]
        for viejo, nuevo in salida["renombrados"]:
            try:
                os.rename(raiz / viejo, raiz / nuevo)
            except OSError as ex:
                salida["fallidos"].append({"ruta": viejo, "motivo": str(ex)})
    print(json.dumps(salida, ensure_ascii=False))
    return 1 if salida["fallidos"] else 0


def cerrado_en(texto_proyecto):
    _, _, ss = partir(texto_proyecto or "")
    return any(re.search(r"Proyecto terminado el\s*20\d\d-\d\d-\d\d", sec(ss, n) or "") for n in ("Estatus", "Estado actual", "En corto"))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
