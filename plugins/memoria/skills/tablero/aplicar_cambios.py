#!/usr/bin/env python3
"""Aplica a la raíz los cambios mecánicos de la cola de la Vista y reporta el resto.

La cola ("cambios" en la base de la página) trae siete tipos:
- fecha: cambio de fecha de un paso de «Siguientes pasos». Se aplica aquí, en la línea del paso.
- hecho: un paso marcado como hecho, con nota opcional. NO se aplica: cerrarlo bien pide
  quitar el paso, contar qué pasó en sesiones.md y a veces una decisión. Se reporta.
- nota: algo anotado para la próxima sesión. NO se aplica. Se reporta. Desde la 1.24, la de «Esperas a» lleva «espera» (a quién
  se esperaba) y, si era una decisión, «decision» (cuál); la sesión la registra como decisión de esa persona.
- prioridad: una prioridad del área marcada como cumplida o retirada. NO se aplica: area.md lo reescribe
  la sesión del responsable del área. Se reporta.
- corregir: quien usa el tablero dice que un paso no es lo que la vista cree (es rutina, es condicional, la fecha
  no es plazo, es decisión). NO se aplica: cambia dónde vive el paso o cómo se escribe, y eso es de sesión.
- respuesta (1.24): «Aceptar» o «Cuestionar» una decisión de otro proyecto que afecta a uno tuyo, desde «Decisiones que te
  afectan» o el registro. NO se aplica: un cuestionamiento es una entrada de decisiones.md y aceptar se cuenta en la bitácora,
  y las dos se escriben en la sesión del proyecto desde el que se registra («proyecto»). Se reporta. «decision» tiene que ser
  un identificador «area/proyecto#AAAA-MM-DD[-n]» y «valor», «aceptada» o «cuestionada».
- propuesta: algo que el barrido de la puesta al día (`barrido.py`) vio que una sesión olvidó. NO se aplica nunca aquí:
  la memoria propone y solo su responsable decide, en una sesión. Se reporta aparte, en "propuestas", como lo que se queda
  en la cola a propósito. Una que no cumple la forma (id de proyecto, línea única) va a "rechazados" y se borra.

Desde la 1.24.8 la página apunta en «por» la cuenta (correo) de quien marcó; falta en lo marcado antes, y entonces fue
quien montó el tablero. Pasa tal cual a "para_sesion".

Uso: aplicar_cambios.py <raiz> <cambios.json | carpeta con un JSON por cambio> --cuenta <correo> [--dry-run]
Solo toca las áreas cuya columna «Cuenta» en la tabla de áreas de guia.md lleva ese correo, como responsable o tras
«colabora:», y los proyectos cuya línea «Colabora:» de «Quién participa» lo lleva: la puesta al día corre con la
cuenta de quien la lanza y nadie escribe en el área de otro (contrato, prohibición 4). Las prioridades del área
son solo de su responsable: las que marca quien colabora se quedan para él.
Sin --cuenta no se aplica nada.
Salida: JSON por stdout con "aplicados" (ids que ya están en la carpeta y se pueden borrar
de la cola), "sin_match" (fechas cuyo paso ya no existe tal cual: se quedan para la sesión), "rechazados" (lo que no
cumple la forma: se borra de la cola y se dice en el resumen), "errores" (no se pudo escribir:
se quedan en la cola y se reintentan en la próxima corrida), "para_sesion" (lo que no es una fecha,
de las áreas y proyectos donde la cuenta es responsable o colabora) y "para_su_dueno" (lo demás: se queda en la cola
hasta que su responsable ponga al día su tablero o cierre una sesión; no se toca).
Una fecha aplicada no toca la fecha «actualizado» de la cabecera: es un cambio mecánico, no trabajo
sobre el proyecto, y moverla escondería en el tablero los plazos vencidos de los demás pasos.
La cola la escribe cualquier contribuidor del tablero, así que nada de ella se toma por bueno: el id del
proyecto tiene que ser «area--slug» con los nombres del contrato (minúsculas, dígitos y guiones), la ruta
resuelta tiene que quedar dentro de esa área, las fechas tienen que ser AAAA-MM-DD, y un paso o una nota
con saltos de línea no se aplica. Lo que no cumple va a "rechazados" y se borra de la cola.
"""
import sys, os, re, json, pathlib, datetime

RAIZ = pathlib.Path(sys.argv[1])
# 1.25.3: la carpeta cuelga de $HOME/mnt con el último tramo de su ruta como nombre, o con «<padre>--<tramo>» si otra
# carpeta conectada se llama igual. Si la ruta recibida no es la raíz, se busca ahí por nombre exacto (como abrir.py, sin
# adivinar entre varias); si tampoco, se para: antes daba «RAIZ ATRASADA» y un inventario vacío sin error, y aquí todo saldría rechazado y se borraría de la cola.
if not (RAIZ / "guia.md").exists() and "--desde-inventario" not in sys.argv:
    _mnt = pathlib.Path(os.path.expanduser("~")) / "mnt"
    _cand = [d for d in (sorted(_mnt.glob("*")) if _mnt.is_dir() else []) if (d.name == RAIZ.name or d.name.endswith("--" + RAIZ.name)) and (d / "guia.md").exists()]
    if len(_cand) == 1:
        RAIZ = _cand[0]; sys.argv[1] = str(RAIZ)
if not (RAIZ / "guia.md").exists():
    print(f"ERROR: {RAIZ} no es la raíz: no tiene guia.md en su primer nivel. " + ("Vuelve a traer guia.md a la copia con device_stage_files." if "--desde-inventario" in sys.argv else "Pasa la carpeta de `ls $HOME/mnt/` que lo tiene."), file=sys.stderr)
    sys.exit(2)
try:
    with open(RAIZ / "guia.md", encoding="utf-8-sig") as _g:
        _g.read(1)
except OSError as _e:
    print(f"ERROR: guia.md de {RAIZ} no se deja leer ({_e.strerror or _e}): si vive en Drive, puede no estar descargado todavía. No se sigue.", file=sys.stderr)
    sys.exit(2)
ENTRADA = pathlib.Path(sys.argv[2])
DRY = "--dry-run" in sys.argv
CUENTA = (sys.argv[sys.argv.index("--cuenta") + 1] if "--cuenta" in sys.argv and len(sys.argv) > sys.argv.index("--cuenta") + 1 else "").strip().lower()

# --- quién escribe: «Quién es quién» y la tabla de áreas de guia.md, y la línea «Colabora:» de un proyecto ---
# Desde el paso 0 de la versión alojada vive en un solo sitio, el paquete context_core (packages/context-core del repo),
# que packages/context-core/inline.py mete aquí, ya en el repo y comprobado con --check, para que el script siga corriendo
# descargado suelto: la misma copia en los ocho scripts que lo usan. Con ella vienen también la regla de lo restringido
# (la celda «Quién la lee» y la fila entera de la tabla de áreas, una sola para la sesión, el tablero, los permisos y la
# migración desde la 1.25.3), el primer párrafo de guia.md y los registros con sus archivados; se importa
# solo lo que este script usa. context_core/compat.py devuelve lo mismo que las copias de la 1.25.1
# (packages/context-core/tests/test_compat.py y test_access.py).
# --- context_core: generated by packages/context-core/inline.py from packages/context-core/context_core; do not edit by hand ---
def _context_core():
    import sys as _s, types as _t
    _fp = {
    'language': 'd0b48a181bc95a37dcc74b80724e1501839640381299b3869bd2dbfa24b10a97',
    'records': '22bc6fac9dc4a84f9e1f74cb653896ef4db22c56d7692c5e33382943982450fe',
    'rules': '5f126e6a2ed5169a437307399e7b3245f9e8e09b8629884f01b1b35d7421a468',
    'compat': '01bb747726884ae0cb2ac7075bc432e61ca4f8cd20cf3baf9c8a6d5fde9b772e',
    }
    _pkg, _todo = _s.modules.get("context_core"), list(_fp)
    if _pkg is not None:
        # already loaded (another script's region, or the installed package): only if it is this same code
        import hashlib as _h, importlib as _i
        _todo = []
        for _n in _fp:
            _m = _s.modules.get("context_core." + _n)
            if _m is None and getattr(_pkg, "__path__", None):
                _m = _i.import_module("context_core." + _n)
            if _m is None:
                _todo.append(_n); continue
            _got = getattr(_m, "__fingerprint__", None)
            if _got is None and getattr(_m, "__file__", None):
                with open(_m.__file__, encoding="utf-8") as _f:
                    _got = _h.sha256(_f.read().encode("utf-8")).hexdigest()
            if _got != _fp[_n]:
                raise ImportError("context_core." + _n + " is already loaded in this process from another version of the package"
                                  " than the one inlined in " + str(globals().get("__file__") or _s.argv[0]) + ": run each in its own process")
        if not _todo:
            return
    else:
        _pkg = _t.ModuleType("context_core"); _pkg.__path__ = []; _s.modules["context_core"] = _pkg
    _src = {
    'language': (
        '"""Language packs: how one language spells the method in the files.\n'
        '\n'
        'The record model has no language; a pack says how a root in that language names its reserved folders and files, its\n'
        'sections, the fields of its registers and the keys of its headers. A root has one language, chosen when it is set up and\n'
        "by default its owner's (decision of 2026-11-05: reserved names follow the root's language and existing roots keep their\n"
        'Spanish names). Spanish is the first and only complete pack; English comes with the language packs after area types.\n'
        '\n'
        'The words that decide what is restricted are here (review of 1.25.2, finding 9): the column names of the area table, the\n'
        'words of \xabAcceso\xbb and \xabQui\xe9n la lee\xbb, and the word that marks a project line, so a root in another language with its\n'
        'restricted area reads restricted. Not here yet, and still spelled inside `rules.py`: the fields of \xabQui\xe9n es qui\xe9n\xbb and\n'
        'the markers of the first paragraph of guia.md.\n'
        '"""\n'
        'from __future__ import annotations\n'
        '\n'
        'from dataclasses import dataclass, field\n'
        'from typing import Optional\n'
        '\n'
        '__all__ = ["Pack", "ES", "PACKS", "pack"]\n'
        '\n'
        '\n'
        '@dataclass(frozen=True)\n'
        'class Pack:\n'
        '    code: str\n'
        '    # reserved folders and files\n'
        '    guide: str\n'
        '    method: str\n'
        '    area_file: str\n'
        '    project_file: str\n'
        '    decisions_file: str\n'
        '    sessions_file: str\n'
        '    base: str\n'
        '    premises_file: str\n'
        '    deliverables: str\n'
        '    workshop: str\n'
        '    sources: str\n'
        '    restricted: str\n'
        '    # sections, as their \xab## \xbb heading\n'
        '    status: str\n'
        '    status_legacy_project: tuple\n'
        '    status_legacy_area: tuple\n'
        '    priorities_legacy: str\n'
        '    steps: str\n'
        '    who: str\n'
        '    objective: str\n'
        '    done_means: str\n'
        '    scope: str\n'
        '    what: str\n'
        '    projects: str\n'
        '    areas: str\n'
        '    # the lines of \xabQui\xe9n participa\xbb and of guia.md\n'
        '    responsible_labels: tuple\n'
        '    consumers_label: str\n'
        '    context_owner_label: str\n'
        '    administrator_label: str\n'
        '    # what decides restricted (rules.area_is_restricted, rules.is_restricted_cell, rules.starts_restricted), as regular\n'
        '    # expressions matched case-insensitively. Area table columns: lowercase header text without \xab*_`\xbb, as written\n'
        '    area_columns: dict            # responsible, account, readers, access, what -> tuple of header names\n'
        '    people_columns: dict          # responsible, account, collaborates -> tuple of header names, as heading_key() leaves them\n'
        '    restricted_lead: str          # the word at the start of \xabAcceso\xbb or \xabQui\xe9n la lee\xbb that makes the area restricted\n'
        '    open_lead: str                # the word at the start of \xabAcceso\xbb that makes it open\n'
        '    restricted_inline: str        # the same word on its own elsewhere in \xabQui\xe9n la lee\xbb (\xabDirecci\xf3n (restringida)\xbb)\n'
        '    restricted_stem: str          # what a negation must precede to cancel restricted_inline\n'
        '    restricted_negations: tuple   # \xabnunca restringida\xbb, \xabantes restringida\xbb\n'
        "    restricted_line: str          # the word at the start of a project's index line (after its name) that makes it restricted\n"
        '    # Estatus bullets, as heading_key() leaves them\n'
        '    status_fields: dict = field(default_factory=dict)\n'
        '    finished_marker: str = ""\n'
        '    # decisiones.md: (lowercase prefix, record field)\n'
        '    decision_fields: tuple = ()\n'
        '    pending_confirmation: str = ""\n'
        '    challenge_title: str = ""\n'
        '    # sesiones.md\n'
        '    session_wrote: tuple = ()\n'
        '    session_published: tuple = ()\n'
        '    session_topic: tuple = ()\n'
        '    session_progress: tuple = ()\n'
        '    session_pending: tuple = ()\n'
        '    session_by: tuple = ()\n'
        '    # header keys\n'
        '    key_state: str = ""\n'
        '    key_updated: str = ""\n'
        '    key_based_on: str = ""\n'
        '    key_replaced_by: str = ""\n'
        '    key_contribution: tuple = ()\n'
        '    # how a writer spells what it writes (context_core.write): one canonical form per field, where reading accepts several\n'
        '    write_session: dict = field(default_factory=dict)     # topic, progress, wrote, published, by\n'
        '    write_decision: dict = field(default_factory=dict)    # decided_by, raised_by, why, discarded, challenges, responds_to, replaces, affects\n'
        '    write_status: dict = field(default_factory=dict)      # completed, next, to_decide, concern\n'
        '    writers: dict = field(default_factory=dict)           # plugin, server: the word before the version in \xabSesi\xf3n de\xbb\n'
        '\n'
        '\n'
        'ES = Pack(\n'
        '    code="es",\n'
        '    guide="guia.md", method="metodo.md", area_file="area.md", project_file="proyecto.md",\n'
        '    decisions_file="decisiones.md", sessions_file="sesiones.md", base="base", premises_file="premisas.md",\n'
        '    deliverables="entregables", workshop="taller", sources="fuentes", restricted="restringido",\n'
        '    status="Estatus", status_legacy_project=("Estado actual", "En corto"), status_legacy_area=("Panorama",),\n'
        '    priorities_legacy="Prioridades ahora", steps="Siguientes pasos", who="Qui\xe9n participa", objective="Objetivo",\n'
        '    done_means="Terminado significa", scope="Alcance", what="Qu\xe9 es", projects="Proyectos", areas="\xc1reas",\n'
        '    responsible_labels=("responsable", "due\xf1o", "dueno", "due\xf1a"), consumers_label="consumen esto",\n'
        '    context_owner_label="Contexto com\xfan", administrator_label=r"Administra la carpeta(?: y pone o quita los accesos)?",\n'
        '    area_columns={"responsible": ("responsable", "due\xf1o", "dueno"), "account": ("cuenta", "colabora"),\n'
        '                  "readers": ("qui\xe9n la lee", "quien la lee"), "access": ("acceso",), "what": ("qu\xe9 es", "que es")},\n'
        '    people_columns={"responsible": ("responsable", "dueno", "duena"), "account": ("cuenta", "cuentas"),\n'
        '                    "collaborates": ("colabora", "colaboran", "colaboradores", "colaboradoras")},\n'
        '    restricted_lead=r"restringid[oa]s?", open_lead=r"abiert[oa]s?", restricted_inline=r"restringidas?",\n'
        '    restricted_stem="restringid", restricted_negations=("nada", "no", "nunca", "sin", "antes"),\n'
        '    restricted_line=r"restringid[oa]",\n'
        '    status_fields={"se completo": "completed", "siguiente": "next", "falta decidir": "to_decide", "preocupa": "concern"},\n'
        '    finished_marker="Proyecto terminado el",\n'
        '    decision_fields=(("decidi\xf3:", "decided_by"), ("decidio:", "decided_by"), ("por qu\xe9:", "why"), ("por que:", "why"),\n'
        '                     ("descartamos:", "discarded"), ("descartado:", "discarded"), ("afecta a:", "affects"),\n'
        '                     ("plante\xf3:", "raised_by"), ("planteo:", "raised_by"), ("cuestiona a:", "challenges"),\n'
        '                     ("responde a:", "responds_to"), ("reemplaza:", "replaces"), ("reemplaza a:", "replaces")),\n'
        '    pending_confirmation=r"\\(pendiente de confirma(r|ci\xf3n)\\)", challenge_title="cuestionamiento",\n'
        '    session_wrote=("escribi\xf3", "escribio"), session_published=("public\xf3", "publico"),\n'
        '    session_topic=("trabajamos en:", "tema:"), session_progress=("avances:",), session_pending=("pendiente:",),\n'
        '    session_by=("sesi\xf3n de:", "sesion de:"),\n'
        '    key_state="estado", key_updated="actualizado", key_based_on="basado_en", key_replaced_by="reemplazado_por",\n'
        '    key_contribution=("aportacion", "afirma"),\n'
        '    write_session={"topic": "Tema", "progress": "Avances", "wrote": "Escribi\xf3", "published": "Public\xf3", "by": "Sesi\xf3n de"},\n'
        '    write_decision={"decided_by": "Decidi\xf3", "raised_by": "Plante\xf3", "why": "Por qu\xe9", "discarded": "Descartado",\n'
        '                    "challenges": "Cuestiona a", "responds_to": "Responde a", "replaces": "Reemplaza", "affects": "Afecta a"},\n'
        '    write_status={"completed": "Se complet\xf3", "next": "Siguiente", "to_decide": "Falta decidir", "concern": "Preocupa"},\n'
        '    writers={"plugin": "plugin", "server": "servidor"},\n'
        ')\n'
        '\n'
        'PACKS = {"es": ES}\n'
        '\n'
        '\n'
        'def pack(code: Optional[str]) -> Pack:\n'
        '    """The pack for a language code; Spanish when no code is given. A code with no pack is an error, not Spanish:\n'
        '    reading an English root with Spanish names would find nothing and look empty."""\n'
        '    c = (code or "es").lower()\n'
        '    if c not in PACKS:\n'
        '        raise ValueError(f"no language pack for {code!r} (have: {\', \'.join(sorted(PACKS))})")\n'
        '    return PACKS[c]\n'
    ),
    'records': (
        '"""The record model: what a Memoria root is made of, as types.\n'
        '\n'
        'Written down from what `generar_vista.py`, `abrir.py` and `cerrar.py` read today (hosted-stack.md, \xabTwo constraints to\n'
        'design in step 0\xbb). Every field says which file and which key or section it comes from, so a caller never needs the\n'
        'file to know what a record means. A record is what the method knows, not how a file spells it: the legacy spellings\n'
        '(1.21 \xabDue\xf1o\xbb, \xabEstado actual\xbb, \xabPrioridades ahora\xbb; 1.22 \xabCuenta\xbb column) land in the same fields as the current ones.\n'
        '\n'
        'Nothing here reads or writes: `parse` builds records from text and `load` from a root.\n'
        '"""\n'
        'from __future__ import annotations\n'
        '\n'
        'from dataclasses import dataclass, field\n'
        'from typing import Optional\n'
        '\n'
        '__all__ = [\n'
        '    "Person", "PeopleRegistry", "AreaRow", "Premise", "Status", "DecisionRef", "Decision", "SessionEntry", "Step",\n'
        '    "Deliverable", "WorkshopFile", "IndexEntry", "Project", "Area", "Root",\n'
        ']\n'
        '\n'
        '\n'
        '# \u2500\u2500 people \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        '@dataclass\n'
        'class Person:\n'
        '    """One line of \xabQui\xe9n es qui\xe9n\xbb in guia.md (1.25): \xab- Name \xb7 account \xb7 field \xb7 field\xbb."""\n'
        '    name: str                                   # "?" for an account that has no name yet\n'
        '    accounts: set[str] = field(default_factory=set)        # Claude accounts (a bare email, or \xabcuentas: a@, b@\xbb)\n'
        '    drive_accounts: set[str] = field(default_factory=set)  # \xaben Drive: x@\xbb\n'
        '    no_account: bool = False                    # \xabsin cuenta\xbb\n'
        '    unconfirmed: bool = False                   # \xabsin confirmar\xbb\n'
        '    aliases: list[str] = field(default_factory=list)       # \xabtambi\xe9n: Other Spelling\xbb\n'
        '    organization: str = ""                      # \xabde: Organization\xbb\n'
        '    left_on: str = ""                           # \xabbaja AAAA-MM-DD\xbb ("s\xed" when the date is missing); a person who left does not write\n'
        '    shared_with: str = ""                       # \xabcompartida con: Name\xbb\n'
        '    registered_by: str = ""                     # \xabregistra: Name\xbb\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class PeopleRegistry:\n'
        '    """\xabQui\xe9n es qui\xe9n\xbb. A name or an account on two lines belongs to nobody: it is dropped from the lookups."""\n'
        '    declared: bool = False                      # the section exists (roots before 1.25 have accounts in the area table)\n'
        '    people: list[Person] = field(default_factory=list)\n'
        '    by_name: dict[str, Person] = field(default_factory=dict)     # key: parse.name_key(name)\n'
        '    by_account: dict[str, Person] = field(default_factory=dict)  # key: lowercased email\n'
        '    warnings: list[str] = field(default_factory=list)\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class AreaRow:\n'
        '    """One row of the \xab\xc1reas\xbb table of guia.md: who answers for the area and who reads it."""\n'
        '    slug: str                                   # folder name, without the slash\n'
        '    what: str                                   # \xabQu\xe9 es\xbb\n'
        '    responsible: str                            # \xabResponsable\xbb (1.22+) or \xabDue\xf1o\xbb (1.21), as written\n'
        '    responsible_accounts: set[str] = field(default_factory=set)   # 1.21/1.22: the email before \xabcolabora:\xbb; 1.25: from the registry\n'
        '    collaborators: list[str] = field(default_factory=list)        # 1.25 \xabColabora\xbb names; earlier, emails after \xabcolabora:\xbb\n'
        '    collaborator_accounts: set[str] = field(default_factory=set)\n'
        '    readers: str = ""                           # \xabQui\xe9n la lee\xbb, as written\n'
        '    access: str = ""                            # \xabAcceso\xbb (1.22+): \xabAbierta\xbb / \xabRestringida\xbb; empty before 1.22\n'
        "    restricted: bool = False                    # decided by the method's rule, fail closed (parse.area_is_restricted)\n"
        '    warnings: list[str] = field(default_factory=list)\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Premise:\n'
        '    """One line of base/premisas.md: \xab- P1 \xb7 text \xb7 Confirm\xf3: Name \xb7 AAAA-MM-DD \xb7 Reemplaza P0\xbb."""\n'
        '    id: str                                     # "P1"\n'
        '    text: str\n'
        '    line: str                                   # the whole line, as the opening prints it\n'
        '    confirmed_by: str = ""\n'
        '    date: str = ""\n'
        '    replaces: Optional[str] = None\n'
        '\n'
        '\n'
        '# \u2500\u2500 project parts \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        '@dataclass\n'
        'class Status:\n'
        '    """The \xabEstatus\xbb section of proyecto.md or area.md (1.22+), or what stands for it in older roots.\n'
        '\n'
        '    Current form:  \xabAAAA-MM-DD \xb7 **headline**\xbb then bullets \xabSe complet\xf3:\xbb, \xabSiguiente:\xbb, \xabFalta decidir:\xbb, \xabPreocupa:\xbb.\n'
        '    Legacy forms keep the whole text in `text` and leave the bullets empty: \xabEstado actual\xbb / \xabEn corto\xbb (projects,\n'
        '    1.21), \xabPanorama\xbb (areas, 1.21)."""\n'
        '    source: str                                 # the section it came from: "Estatus", "Estado actual", "En corto", "Panorama"\n'
        '    text: str                                   # the section as written\n'
        '    date: str = ""\n'
        '    headline: str = ""\n'
        '    completed: str = ""                         # \xabSe complet\xf3\xbb\n'
        '    next: list[str] = field(default_factory=list)   # \xabSiguiente\xbb, with its sub-bullets; for an area these are its priorities\n'
        '    to_decide: str = ""                         # \xabFalta decidir\xbb\n'
        '    concern: str = ""                           # \xabPreocupa\xbb\n'
        '    finished_on: str = ""                       # \xabProyecto terminado el AAAA-MM-DD\xbb: the project is closed\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class DecisionRef:\n'
        '    """A pointer to a decision or a premise, as \xabResponde a\xbb, \xabCuestiona a\xbb and \xabReemplaza\xbb write it."""\n'
        '    project: Optional[str]                      # "area--project", "premisa", or None when the text names no identifier\n'
        '    id: Optional[str]                           # "2026-10-15-2", "P3"\n'
        '    text: str                                   # as written\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Decision:\n'
        '    """One entry of decisiones.md: \xab## AAAA-MM-DD \xb7 title\xbb and its fields. Entries are never edited once written."""\n'
        '    id: str                                     # the date, plus -2, -3\u2026 counting from the oldest entry of that day; "" without a valid date\n'
        '    date: str\n'
        '    title: str\n'
        '    decided_by: str = ""                        # \xabDecidi\xf3\xbb\n'
        '    why: str = ""                               # \xabPor qu\xe9\xbb\n'
        '    discarded: str = ""                         # \xabDescartado\xbb / \xabDescartamos\xbb\n'
        '    affects: str = ""                           # \xabAfecta a\xbb, as written (paths and projects separated by \xab\xb7\xbb)\n'
        '    raised_by: str = ""                         # \xabPlante\xf3\xbb (challenges)\n'
        '    challenges: Optional[DecisionRef] = None    # \xabCuestiona a\xbb\n'
        '    responds_to: Optional[DecisionRef] = None   # \xabResponde a\xbb\n'
        '    replaces: Optional[DecisionRef] = None      # \xabReemplaza\xbb\n'
        '    pending_confirmation: bool = False          # \xabDecidi\xf3: Name (pendiente de confirmar)\xbb\n'
        '    kind: str = "decision"                      # "decision" or "challenge" (a \xabCuestiona a\xbb or a title \xabCuestionamiento: \u2026\xbb)\n'
        '    archived: bool = False                      # it comes from decisiones-AAAA.md, not the live file\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class SessionEntry:\n'
        '    """One entry of sesiones.md: \xab## AAAA-MM-DD\xbb and its fields."""\n'
        '    n: int                                      # position counting from the oldest entry: stable when entries are added on top\n'
        '    date: str\n'
        '    title: str                                  # the heading as written (sessions of the same day share it)\n'
        '    topic: str = ""                             # \xabTema\xbb / \xabTrabajamos en\xbb\n'
        '    progress: str = ""                          # \xabAvances\xbb\n'
        '    pending: str = ""                           # \xabPendiente\xbb (older roots)\n'
        '    by: str = ""                                # \xabSesi\xf3n de\xbb, without the plugin version\n'
        '    plugin_version: str = ""                    # \xab\xb7 plugin 1.25.1\xbb\n'
        '    server_version: str = ""                    # \xab\xb7 servidor 0.0.2\xbb: the entry was written by the hosted server\n'
        '    wrote: list[str] = field(default_factory=list)       # \xabEscribi\xf3\xbb, paths inside the project (restricted ones dropped)\n'
        '    published: list[str] = field(default_factory=list)   # \xabPublic\xf3\xbb\n'
        '    archived: bool = False\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Step:\n'
        '    """One bullet of \xabSiguientes pasos\xbb. The method writes owner and size in the text; the record keeps the text whole\n'
        '    and the dates it names, which is what the board and the close read."""\n'
        '    text: str\n'
        '    dates: list[str] = field(default_factory=list)\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Deliverable:\n'
        '    """A file in the project\'s entregables/. Its header for .md files; for other formats only the name and the area index."""\n'
        '    file: str                                   # "hosted-path.md"\n'
        '    name: str                                   # stem\n'
        '    format: str                                 # extension without the dot\n'
        '    title: Optional[str] = None                 # the H1\n'
        '    state: Optional[str] = None                 # \xabestado\xbb: borrador, vigente, reemplazado\u2026\n'
        '    updated: Optional[str] = None               # \xabactualizado\xbb, else the date of its line in the area index\n'
        '    based_on: list[str] = field(default_factory=list)     # \xabbasado_en\xbb, paths from the root\n'
        '    replaced_by: Optional[str] = None           # \xabreemplazado_por\xbb\n'
        '    contribution: Optional[str] = None          # \xabaportacion\xbb (1.22+; \xabafirma\xbb before): one line on what it holds\n'
        '    description: str = ""                       # its line in the area\'s \xabProyectos\xbb index\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class WorkshopFile:\n'
        '    """A file in taller/. Workshop is never shown as current; the record holds only what the board lists."""\n'
        '    path: str                                   # relative to taller/\n'
        '    title: Optional[str] = None\n'
        '    updated: Optional[str] = None\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class IndexEntry:\n'
        '    """A project line of the \xabProyectos\xbb block of area.md, with its deliverable sub-lines."""\n'
        '    slug: str\n'
        '    description: str\n'
        '    restricted: bool = False                    # the description starts with \xabrestringido\xbb\n'
        '    deliverables: dict[str, dict] = field(default_factory=dict)   # stem -> {"description", "updated"}\n'
        '    notes: list[str] = field(default_factory=list)\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Project:\n'
        '    """A project folder: proyecto.md, decisiones.md, sesiones.md, entregables/, taller/, fuentes/, restringido/."""\n'
        '    area: str\n'
        '    slug: str\n'
        '    restricted: bool = False                    # restricted projects keep only their index line: nothing inside is read\n'
        '    state: Optional[str] = None                 # proyecto.md \xabestado\xbb\n'
        '    updated: Optional[str] = None               # proyecto.md \xabactualizado\xbb\n'
        '    title: str = ""\n'
        '    objective: str = ""                         # \xabObjetivo\xbb\n'
        '    done_means: str = ""                        # \xabTerminado significa\xbb (older roots)\n'
        '    scope: str = ""                             # \xabAlcance\xbb\n'
        '    status: Optional[Status] = None\n'
        '    steps: list[Step] = field(default_factory=list)       # \xabSiguientes pasos\xbb\n'
        '    responsible: str = ""                       # \xabQui\xe9n participa\xbb: \xabResponsable:\xbb (1.22+) or \xabDue\xf1o:\xbb (1.21)\n'
        '    collaborators: list[str] = field(default_factory=list)   # \xabColabora:\xbb names (1.25) or \xabName (email)\xbb (1.22)\n'
        '    consumers: str = ""                         # \xabConsumen esto:\xbb (older roots)\n'
        '    decisions: list[Decision] = field(default_factory=list)  # newest first\n'
        '    sessions: list[SessionEntry] = field(default_factory=list)  # newest first\n'
        '    deliverables: list[Deliverable] = field(default_factory=list)\n'
        '    workshop: list[WorkshopFile] = field(default_factory=list)\n'
        '    index: Optional[IndexEntry] = None          # its line in area.md, if any\n'
        '\n'
        '    @property\n'
        '    def key(self) -> str:\n'
        '        """The identifier the board and the queue use: "area--project"."""\n'
        '        return f"{self.area}--{self.slug}"\n'
        '\n'
        '    @property\n'
        '    def closed(self) -> bool:\n'
        '        return bool(self.status and self.status.finished_on)\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Area:\n'
        '    """An area folder: area.md and its projects."""\n'
        '    slug: str\n'
        '    row: Optional[AreaRow] = None               # its row in guia.md; None for a folder the table does not name\n'
        '    restricted: bool = False\n'
        '    state: Optional[str] = None\n'
        '    updated: Optional[str] = None\n'
        '    title: str = ""\n'
        '    what: str = ""                              # \xabQu\xe9 es\xbb\n'
        '    status: Optional[Status] = None             # \xabEstatus\xbb (1.22+) or \xabPanorama\xbb\n'
        '    priorities: list[str] = field(default_factory=list)   # \xabSiguiente\xbb of the Estatus, or \xabPrioridades ahora\xbb (1.21)\n'
        '    responsible: str = ""                       # \xabQui\xe9n participa\xbb of area.md\n'
        '    index: dict[str, IndexEntry] = field(default_factory=dict)\n'
        '    projects: list[Project] = field(default_factory=list)\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Root:\n'
        '    """A whole root: the folder with guia.md and metodo.md at its first level."""\n'
        '    name: str\n'
        '    organization: str = ""                      # what goes before \xab\xb7\xbb in the H1 of guia.md\n'
        '    method_line: str = ""                       # first line of metodo.md: version and fingerprint\n'
        '    method_version: Optional[tuple[int, ...]] = None\n'
        '    method_fingerprint: Optional[str] = None\n'
        '    language: str = "es"                        # the root\'s language pack (language.py)\n'
        '    timezone: str = "America/Mexico_City"       # \xabZona horaria:\xbb of guia.md\n'
        '    context_owner: str = ""                     # \xabContexto com\xfan:\xbb (who answers for guia.md and base/)\n'
        '    administrator: str = ""                     # \xabAdministra la carpeta:\xbb\n'
        '    people: PeopleRegistry = field(default_factory=PeopleRegistry)\n'
        '    area_rows: list[AreaRow] = field(default_factory=list)\n'
        '    areas: list[Area] = field(default_factory=list)\n'
        '    premises: list[Premise] = field(default_factory=list)\n'
        '    warnings: list[str] = field(default_factory=list)\n'
        '\n'
        '    def area(self, slug: str) -> Optional[Area]:\n'
        '        return next((a for a in self.areas if a.slug == slug), None)\n'
        '\n'
        '    def project(self, key: str) -> Optional[Project]:\n'
        '        """By "area/project" or "area--project"."""\n'
        '        a, _, p = key.replace("--", "/").partition("/")\n'
        '        ar = self.area(a)\n'
        '        return next((x for x in ar.projects if x.slug == p), None) if ar else None\n'
        '\n'
        '    @property\n'
        '    def current_premises(self) -> list[Premise]:\n'
        '        replaced = {p.replaces for p in self.premises if p.replaces}\n'
        '        return [p for p in self.premises if p.id not in replaced]\n'
    ),
    'rules': (
        '"""The rules the plugin scripts share: who writes (the people registry, the area table\'s accounts, \xabColabora:\xbb), what is\n'
        "restricted, guia.md's first paragraph and the archived registers. Pure functions: no I/O, no globals, no clock.\n"
        '\n'
        'This is what `compat` reaches, and so what `inline.py` puts inside the scripts; the parsers of the other method files are\n'
        'in `parse`, which imports these and re-exports them. The words that decide restricted come from the language pack\n'
        '(review of 1.25.2, finding 9). `tests/test_compat.py` and `tests/test_access.py` compare these with the 1.25.1 rules\n'
        'frozen in `tests/reference/`.\n'
        '"""\n'
        'from __future__ import annotations\n'
        '\n'
        'import re\n'
        'import unicodedata\n'
        'from typing import Optional\n'
        '\n'
        'from .language import ES, Pack\n'
        'from .records import PeopleRegistry, Person\n'
        '\n'
        'EMAIL = re.compile(r"[\\w.+\'-]+@[\\w-]+(?:\\.[\\w-]+)*")\n'
        '_WORD_COLLABORATES = re.compile(r"\\bco-?labor\\w*\\s*:?", re.I)\n'
        '_LINE_COLLABORATES = re.compile(r"^\\s*[-*]?\\s*\\**\\s*colabora[n]?\\s*\\**\\s*:", re.I)\n'
        '\n'
        '\n'
        '# \u2500\u2500 names \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'def name_key(n: str) -> str:\n'
        '    """How two names compare: NFC, lowercase, without bold, quotes or parentheses, spaces joined. An accent counts."""\n'
        '    n = unicodedata.normalize("NFC", n or "").replace("\xa0", " ")\n'
        '    n = re.sub(r"\\s*\\([^)]*\\)", "", re.sub(r"[*_`\xab\xbb\\"]", "", n))\n'
        '    return re.sub(r"\\s+", " ", n).strip(" .,;:").lower()\n'
        '\n'
        '\n'
        'def heading_key(t: str) -> str:\n'
        '    """A heading to compare: without accents (NFC or NFD), case or punctuation."""\n'
        '    t = "".join(c for c in unicodedata.normalize("NFD", t or "") if unicodedata.category(c) != "Mn")\n'
        '    return re.sub(r"\\s+", " ", re.sub(r"[^a-z ]", "", t.lower())).strip()\n'
        '\n'
        '\n'
        '# \u2500\u2500 restricted \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'def is_restricted_cell(cell: str, lang: Pack = ES) -> bool:\n'
        '    """\xabQui\xe9n la lee\xbb declares the area restricted: the word at the start (\xabRestringida: \u2026\xbb), or \xabrestringida\xbb on its\n'
        '    own elsewhere (\xabDirecci\xf3n (restringida)\xbb) and not negated (\xabnunca restringida\xbb, \xabantes restringida\xbb)."""\n'
        '    c = cell or ""\n'
        '    if re.match(r"^[\\W_]*" + lang.restricted_lead + r"\\b", c, re.I):\n'
        '        return True\n'
        '    return bool(re.search(r"\\b" + lang.restricted_inline + r"\\b", c, re.I)) and not re.search(\n'
        '        r"\\b(?:" + "|".join(lang.restricted_negations) + r")\\s+(?:[^\\s]+\\s+)?" + lang.restricted_stem, c, re.I)\n'
        '\n'
        '\n'
        'def starts_restricted(line: str, lang: Pack = ES) -> bool:\n'
        '    """An index line \xab- `x/` \u2014 restringido: \u2026\xbb marks the project restricted."""\n'
        '    return bool(re.match(r"^[\\W_]*" + lang.restricted_line + r"\\b", line or "", re.I))\n'
        '\n'
        '\n'
        'def access_word(cell: str, lang: Pack = ES) -> Optional[bool]:\n'
        '    """What an \xabAcceso\xbb cell says: True for \xabRestringida\xbb, False for \xabAbierta\xbb, None for anything else (empty, unclear)."""\n'
        '    if re.match(r"^[\\W_]*" + lang.restricted_lead + r"\\b", cell or "", re.I):\n'
        '        return True\n'
        '    if re.match(r"^[\\W_]*" + lang.open_lead + r"\\b", cell or "", re.I):\n'
        '        return False\n'
        '    return None\n'
        '\n'
        '\n'
        'def _area_columns(header: list[str], lang: Pack = ES) -> dict:\n'
        '    n = [re.sub(r"[*_`]", "", x).strip().lower() for x in header]\n'
        '    default = {"responsible": 2, "account": 3, "readers": 4, "access": None, "what": 1}\n'
        '    return {k: next((i for i, x in enumerate(n) if x in names), default[k]) for k, names in lang.area_columns.items()}\n'
        '\n'
        '\n'
        'def area_is_restricted(cells: list[str], header: list[str], lang: Pack = ES) -> bool:\n'
        '    """Whether an area row of guia.md is restricted: the one rule that the opening, the board, the permissions check and the\n'
        '    migration use (verificar.sh reads only the \xabAcceso\xbb word, with access_word) (review of 1.25.2, finding 10). With an \xabAcceso\xbb column (1.22+), its word; otherwise,\n'
        '    or when it is empty or unclear, restricted if the table has a \xabColabora\xbb column (1.25: \xabQui\xe9n la lee\xbb no longer\n'
        '    carries \xabRestringida:\xbb, so it fails closed), and else the \xabQui\xe9n la lee\xbb rule. Same as area_restringida() in the\n'
        '    1.25.1 abrir.py, frozen in tests/reference/acceso_1_25_1.py."""\n'
        '    col = _area_columns(header, lang)\n'
        '    if col["access"] is not None and col["access"] < len(cells):\n'
        '        word = access_word(cells[col["access"]], lang)\n'
        '        if word is not None:\n'
        '            return word\n'
        '    if _people_columns(header, lang)["collaborates"] is not None:\n'
        '        return True\n'
        '    return is_restricted_cell(cells[col["readers"]] if col["readers"] < len(cells) else "", lang)\n'
        '\n'
        '\n'
        '# \u2500\u2500 people \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'def people_registry(guia: str) -> PeopleRegistry:\n'
        '    """\xabQui\xe9n es qui\xe9n\xbb of guia.md. Same rules as registro_personas() in the scripts."""\n'
        '    lines, inside, declared = [], False, False\n'
        '    for l in unicodedata.normalize("NFC", guia or "").split("\\n"):\n'
        '        m = re.match(r"^\\s*#{2,3}\\s+(.*?)\\s*$", l)\n'
        '        if m:\n'
        '            inside = heading_key(m.group(1)) == "quien es quien"\n'
        '            declared = declared or inside\n'
        '        elif inside:\n'
        '            lines.append(l)\n'
        '    reg = PeopleRegistry(declared=declared)\n'
        '    two_names, two_accounts = set(), set()\n'
        '    for l in lines:\n'
        '        if not re.match(r"^\\s*[-*]\\s+\\S", l):\n'
        '            continue\n'
        '        fields = [c.strip() for c in re.split(r"\\s+\xb7\\s+", l.strip()[1:].strip()) if c.strip()]\n'
        '        if not fields:\n'
        '            continue\n'
        '        p = Person(name=re.sub(r"\\s*\\([^)]*\\)", "", re.sub(r"[*_`]", "", fields[0])).strip())\n'
        '        if EMAIL.fullmatch(p.name.lower()):\n'
        '            p.accounts.add(p.name.lower()); p.name = "?"\n'
        '        elif EMAIL.search(p.name):\n'
        '            reg.warnings.append(f"\xab{fields[0]}\xbb: el nombre y la cuenta van separados por \xab \xb7 \xbb")\n'
        '        for c in fields[1:]:\n'
        '            cl = c.lower()\n'
        '            if EMAIL.fullmatch(cl):\n'
        '                p.accounts.add(cl)\n'
        '            elif re.search(r"\\bbaja\\b", cl):\n'
        '                p.left_on = (re.search(r"20\\d\\d-\\d\\d-\\d\\d", c) or [""])[0] or "s\xed"\n'
        '            elif re.match(r"^cuentas?\\s*:", cl):\n'
        '                p.accounts |= set(EMAIL.findall(cl))\n'
        '            elif re.match(r"^(en\\s+)?(google\\s+)?drive\\s*:", cl):\n'
        '                p.drive_accounts |= set(EMAIL.findall(cl))\n'
        '            elif re.match(r"^sin\\s+cuenta\\b", cl):\n'
        '                p.no_account = True\n'
        '            elif re.match(r"^sin\\s+confirmar\\b", cl):\n'
        '                p.unconfirmed = True\n'
        '            elif re.match(r"^tambi[e\xe9]n\\s*:", cl):\n'
        '                p.aliases += [a.strip() for a in re.split(r"[,;]", c.split(":", 1)[1]) if a.strip()]\n'
        '            elif re.match(r"^de\\s*:", cl):\n'
        '                p.organization = c.split(":", 1)[1].strip()\n'
        '            elif re.match(r"^compartida\\s+con\\s*:", cl):\n'
        '                p.shared_with = c.split(":", 1)[1].strip()\n'
        '            elif re.match(r"^registra\\s*:", cl):\n'
        '                p.registered_by = c.split(":", 1)[1].strip()\n'
        '            else:\n'
        '                reg.warnings.append(f"\xab{p.name}\xbb: no se entiende \xab{c}\xbb (van un correo, \xabsin cuenta\xbb, \xaben Drive: correo\xbb, \xabtambi\xe9n: nombre\xbb, \xabde: organizaci\xf3n\xbb o \xabbaja AAAA-MM-DD\xbb)")\n'
        '        if p.no_account and p.accounts:\n'
        '            reg.warnings.append(f"\xab{p.name}\xbb dice \xabsin cuenta\xbb y lleva una cuenta: se queda la cuenta")\n'
        '            p.no_account = False\n'
        '        if not p.accounts and not p.no_account and not p.left_on:\n'
        '            reg.warnings.append(f"\xab{p.name}\xbb no lleva ni su cuenta ni \xabsin cuenta\xbb")\n'
        '        reg.people.append(p)\n'
        '        for n in ([p.name] if p.name != "?" else []) + p.aliases:\n'
        '            k = name_key(n)\n'
        '            if k in reg.by_name and reg.by_name[k] is not p:\n'
        '                two_names.add(k)\n'
        '                reg.warnings.append(f"\xab{n}\xbb est\xe1 dos veces: dos personas con el mismo nombre se distinguen con el segundo apellido o una inicial (mientras, ese nombre no es de nadie)")\n'
        '            reg.by_name.setdefault(k, p)\n'
        '        for c in p.accounts:\n'
        '            if c in reg.by_account and reg.by_account[c] is not p:\n'
        '                two_accounts.add(c)\n'
        '                reg.warnings.append(f"la cuenta {c} est\xe1 en dos l\xedneas (\xab{reg.by_account[c].name}\xbb y \xab{p.name}\xbb; mientras, no es de nadie)")\n'
        '            reg.by_account.setdefault(c, p)\n'
        '    for k in two_names:\n'
        '        reg.by_name.pop(k, None)\n'
        '    for c in two_accounts:\n'
        '        reg.by_account.pop(c, None)\n'
        '    return reg\n'
        '\n'
        '\n'
        'def find_person(name_or_account: str, reg: PeopleRegistry) -> Optional[Person]:\n'
        '    t = (name_or_account or "").strip()\n'
        '    if EMAIL.fullmatch(t.lower()):\n'
        '        return reg.by_account.get(t.lower())\n'
        '    return reg.by_name.get(name_key(t))\n'
        '\n'
        '\n'
        'def names_in(text: str, reg: Optional[PeopleRegistry] = None) -> list[str]:\n'
        '    """The names of a cell or line (\xabColabora: Ana Ruiz, Luis Mej\xeda\xbb), split by \xab,\xbb or \xab;\xbb, and by \xab y \xbb / \xab e \xbb only\n'
        '    when the whole piece is not a registered name."""\n'
        '    reg = reg or PeopleRegistry()\n'
        '    t = re.sub(r"^\\s*[-*]?\\s*\\**\\s*(?:colabora[n]?|lo leen?|responsable)\\s*\\**\\s*:\\s*\\**", "", text or "", flags=re.I)\n'
        '    t = re.sub(r"\\s*\\([^)]*\\)", "", t)\n'
        '    out: list[str] = []\n'
        '    for piece in re.split(r"[,;]", t):\n'
        '        piece = piece.strip(" .*")\n'
        '        if not piece or piece.lower() in ("\u2014", "-", "nadie", "ninguno", "ninguna"):\n'
        '            continue\n'
        '        if find_person(piece, reg) is not None or not re.search(r"\\s(?:y|e)\\s", piece):\n'
        '            out.append(piece)\n'
        '        else:\n'
        '            out += [x.strip(" .*") for x in re.split(r"\\s+(?:y|e)\\s+", piece) if x.strip(" .*")]\n'
        '    return out\n'
        '\n'
        '\n'
        'def accounts_of_names(text: str, reg: PeopleRegistry) -> tuple[set[str], list[str]]:\n'
        '    out, missing = set(), []\n'
        '    for n in names_in(text, reg):\n'
        '        p = find_person(n, reg)\n'
        '        if p is None:\n'
        '            missing.append(n)\n'
        '        elif not p.left_on:\n'
        '            out |= p.accounts\n'
        '    return out, missing\n'
        '\n'
        '\n'
        'def account_cell(cell: str) -> tuple[set[str], set[str], Optional[str]]:\n'
        '    """(responsible, collaborators, warning) of a \xabCuenta\xbb cell \xabresp@x \xb7 colabora: a@x, b@x\xbb (up to 1.24). Fails closed."""\n'
        '    text = (cell or "").lower()\n'
        '    parts = _WORD_COLLABORATES.split(text, maxsplit=1)\n'
        '    before = set(EMAIL.findall(parts[0]))\n'
        '    after = set(EMAIL.findall(parts[1])) if len(parts) > 1 else set()\n'
        '    warning = None\n'
        '    if len(before) > 1:\n'
        '        warning = "m\xe1s de un correo antes de \xabcolabora:\xbb; nadie es responsable hasta que se corrija"\n'
        '        before = set()\n'
        '    elif not before:\n'
        '        warning = "sin el correo del responsable"\n'
        '    elif len(parts) > 1 and not re.search(r"\\bcolabora\\s*:", text):\n'
        '        warning = "la palabra para quien colabora va escrita \xabcolabora:\xbb"\n'
        '    return before, after, warning\n'
        '\n'
        '\n'
        'def _people_columns(header: list[str], lang: Pack = ES) -> dict:\n'
        '    n = [heading_key(x) for x in header]\n'
        '    return {k: next((i for i, x in enumerate(n) if x in names), None) for k, names in lang.people_columns.items()}\n'
        '\n'
        '\n'
        'def row_accounts(header: list[str], cells: list[str], reg: PeopleRegistry) -> tuple[set[str], set[str], Optional[str]]:\n'
        '    """(responsible, collaborators, warning) of an area row: from the \xabCuenta\xbb emails up to 1.24, from the \xabColabora\xbb\n'
        '    names and the registry in 1.25. Same as fila_cuentas()."""\n'
        '    col = _people_columns(header)\n'
        '    cell = lambda i: cells[i] if i is not None and i < len(cells) else ""\n'
        '    if col["account"] is not None or col["collaborates"] is None:\n'
        '        return account_cell(cell(col["account"] if col["account"] is not None else 3))\n'
        '    if not reg.declared:\n'
        '        return set(), set(), "la tabla nombra a quien colabora por su nombre y guia.md no tiene \xabQui\xe9n es qui\xe9n\xbb"\n'
        '    resp = re.sub(r"\\s*\\((?=[a-z\xe1\xe9\xed\xf3\xfa\xf1`])[^)]*\\)", "", cell(col["responsible"] if col["responsible"] is not None else 2))\n'
        '    rn = names_in(resp, reg)\n'
        '    warnings, of = [], set()\n'
        '    if len(rn) > 1 and find_person(rn[0], reg) is not None:\n'
        '        warnings.append(f"en Responsable, lo que sigue a \xab{rn[0]}\xbb va en \xabQu\xe9 es\xbb")\n'
        '        rn = rn[:1]\n'
        '    if len(rn) != 1:\n'
        '        warnings.append("el responsable es una sola persona del registro" if rn else "sin responsable")\n'
        '    else:\n'
        '        p = find_person(rn[0], reg)\n'
        '        if p is None:\n'
        '            warnings.append(f"\xab{rn[0]}\xbb no est\xe1 en \xabQui\xe9n es qui\xe9n\xbb")\n'
        '        elif p.left_on:\n'
        '            warnings.append(f"\xab{p.name}\xbb est\xe1 de baja")\n'
        '        elif p.accounts:\n'
        '            of = set(p.accounts)\n'
        '        elif p.registered_by and find_person(p.registered_by, reg) and find_person(p.registered_by, reg).accounts:\n'
        '            of = set(find_person(p.registered_by, reg).accounts)\n'
        '        else:\n'
        '            warnings.append(f"\xab{p.name}\xbb no tiene cuenta: o la tiene, o su l\xednea dice \xabregistra: Nombre\xbb de quien escribe por ella")\n'
        '    co, missing = accounts_of_names(cell(col["collaborates"]), reg)\n'
        '    warnings += [f"\xab{n}\xbb (Colabora) no est\xe1 en \xabQui\xe9n es qui\xe9n\xbb" for n in missing]\n'
        '    return of, co - of, "; ".join(warnings) or None\n'
        '\n'
        '\n'
        'def provisional_people(who: str, reg: PeopleRegistry) -> list[tuple[str, str]]:\n'
        '    """[(name, email)] of \xabColabora: Name (email)\xbb for someone not in the registry: the provisional entry (1.25)."""\n'
        '    out: list[tuple[str, str]] = []\n'
        '    if not reg.declared:\n'
        '        return out\n'
        '    for l in (who or "").split("\\n"):\n'
        '        if _LINE_COLLABORATES.match(l):\n'
        '            for n, c in re.findall(r"([^,;(:]+?)\\s*\\(\\s*(" + EMAIL.pattern + r")\\s*\\)", l):\n'
        '                n = n.strip(" .*")\n'
        '                if find_person(n, reg) is None and c.lower() not in reg.by_account:\n'
        '                    out.append((n, c.lower()))\n'
        '    return out\n'
        '\n'
        '\n'
        'def collaborator_accounts(who: str, reg: Optional[PeopleRegistry] = None) -> set[str]:\n'
        '    """The accounts of the \xabColabora:\xbb lines of a project\'s \xabQui\xe9n participa\xbb. Same as colaboran_en()."""\n'
        '    reg = reg or PeopleRegistry()\n'
        '    out: set[str] = set()\n'
        '    for l in (who or "").split("\\n"):\n'
        '        if _LINE_COLLABORATES.match(l):\n'
        '            if reg.declared:\n'
        '                out |= accounts_of_names(l, reg)[0] | {c for _, c in provisional_people(l, reg)}\n'
        '            else:\n'
        '                out |= set(EMAIL.findall(l.lower()))\n'
        '    return out\n'
        '\n'
        '\n'
        '# \u2500\u2500 \xabContexto com\xfan\xbb \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'def context_owner_name(line: str) -> str:\n'
        '    """The name of \xabContexto com\xfan: Name\xbb, without the account in parentheses or what follows a comma, stop or dash."""\n'
        '    t = re.sub(r"\\s*\\([^)]*\\)", "", (line or "").split(":", 1)[-1])\n'
        '    return re.split(r",|\\.\\s|\\.$|\\s[\u2014\u2013-]\\s|;", t.strip())[0].strip()\n'
        '\n'
        '\n'
        'def context_owner_accounts(line: str, reg: PeopleRegistry) -> set[str]:\n'
        '    """The account in parentheses (up to 1.24) or the registry\'s for that name (1.25)."""\n'
        '    c = set(EMAIL.findall((line or "").split(":", 1)[-1].lower()))\n'
        '    if c:\n'
        '        return c\n'
        '    p = find_person(context_owner_name(line), reg)\n'
        '    return set(p.accounts) if p and not p.left_on else set()\n'
        '\n'
        '\n'
        'def name_of_account(account: str, reg: PeopleRegistry) -> str:\n'
        '    p = reg.by_account.get((account or "").lower())\n'
        '    return p.name if p and p.name != "?" else ""\n'
        '\n'
        '\n'
        "# \u2500\u2500 guia.md's first paragraph, and archived registers \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
        '\n'
        'ABOUT_THE_FOLDER = r"`(?:metodo|guia)\\.md`|plugin `memoria`|Aqu\xed solo est\xe1 lo nuestro"\n'
        '\n'
        '\n'
        'def drop_folder_talk(sentences: list[str], rx: str = ABOUT_THE_FOLDER) -> list[str]:\n'
        '    """The sentences of guia.md\'s first paragraph without what talks about the folder or the method. Of a sentence joined\n'
        '    by \xab;\xbb to one that does not, the other stays (not split by a \xab;\xbb in parentheses); within each part, what comes before\n'
        '    the comma, colon or dash that opens the folder talk stays if it has three words or more. Same as sin_carpeta()."""\n'
        '    out = []\n'
        '    for f in sentences:\n'
        '        if not re.search(rx, f):\n'
        '            out.append(f); continue\n'
        '        keep = []\n'
        '        for c in [c.strip() for c in re.split(r";(?![^()]*\\))", f)]:\n'
        '            m = re.search(rx, c) if c else None\n'
        '            if c and not m:\n'
        '                keep.append(c); continue\n'
        '            cuts = [s.start() for s in re.finditer(r"[,:\u2014](?![^()]*\\))", c[:m.start()] if m else "")]\n'
        '            t = c[:cuts[-1]].strip() if cuts else ""\n'
        '            if len(t.split()) >= 3 and not re.search(rx, t):\n'
        '                keep.append(t)\n'
        '        if keep:\n'
        '            t = "; ".join(keep); t = t[0].upper() + t[1:]\n'
        '            out.append(t if t[-1] in ".!?" else t + ".")\n'
        '    return out\n'
        '\n'
        '\n'
        'ARCHIVED = re.compile(r"^(sesiones|decisiones)-(20\\d\\d)(?:-(\\d+))?\\.md$")\n'
        '\n'
        '\n'
        'def archived_names(names: list[str], register: str, year) -> list[str]:\n'
        '    """Of the names in a project folder, the archives of a register (\xabsesiones\xbb or \xabdecisiones\xbb) from `year` - 1 on,\n'
        '    newest first. Older ones are not read whole (escribir.md, section 8)."""\n'
        '    seen = []\n'
        '    for n in names:\n'
        '        m = ARCHIVED.match(n)\n'
        '        if m and m.group(1) == register and int(m.group(2)) >= int(year) - 1:\n'
        '            seen.append((int(m.group(2)), int(m.group(3) or 1), n))\n'
        '    return [n for _, _, n in sorted(seen, reverse=True)]\n'
        '\n'
        '\n'
        'def with_archives(live: Optional[str], archives: list[Optional[str]]) -> tuple[str, int]:\n'
        '    """(text, entries of the live register): the live register followed by the entries of its archives, as if they had\n'
        '    not been archived, so every decision keeps its identifier. Same as con_archivados()."""\n'
        '    parts = [live or ""]\n'
        '    for t in archives:\n'
        '        m = re.search(r"^## ", t or "", re.M)\n'
        '        if m:\n'
        '            parts.append((t or "")[m.start():])\n'
        '    return "\\n\\n".join(p.strip("\\n") for p in parts if p.strip()) + "\\n", len(re.findall(r"^## ", live or "", re.M))\n'
    ),
    'compat': (
        '"""The scripts\' Spanish names over the package, with the shapes they use today (dicts and tuples).\n'
        '\n'
        'The plugin scripts keep their Spanish until the language packs (decision of 2026-11-04). While each one moves onto the\n'
        'package, it imports these names in place of its own copy of the code, and nothing else in the script changes. A script\n'
        'that has moved no longer carries the copy; `packages/context-core/tests/test_compat.py` checks these return exactly what the copies do.\n'
        '"""\n'
        'from __future__ import annotations\n'
        '\n'
        'import pathlib\n'
        'import re\n'
        'from typing import Optional\n'
        '\n'
        'from . import rules\n'
        'from .records import PeopleRegistry, Person\n'
        '\n'
        '__all__ = ["SOBRE_LA_CARPETA", "sin_carpeta", "ARCHIVADO", "archivados_de", "con_archivados", "respuestas_viejas",\n'
        '           "restringida_celda", "area_restringida", "acceso_de", "CORREO", "PALABRA_COLABORA", "LINEA_COLABORA", "cuentas",\n'
        '           "clave_nombre", "registro_personas",\n'
        '           "persona", "nombres_de", "cuentas_de_nombres", "altas_provisionales", "columnas_personas", "fila_cuentas",\n'
        '           "nombre_contexto", "cuentas_contexto", "nombre_de", "colaboran_en"]\n'
        '\n'
        'CORREO = rules.EMAIL\n'
        'PALABRA_COLABORA = rules._WORD_COLLABORATES\n'
        'LINEA_COLABORA = rules._LINE_COLLABORATES\n'
        '\n'
        'cuentas = rules.account_cell\n'
        'clave_nombre = rules.name_key\n'
        'nombre_contexto = rules.context_owner_name\n'
        '\n'
        '\n'
        'def _persona(p: Person) -> dict:\n'
        '    return {"nombre": p.name, "cuentas": p.accounts, "drive": p.drive_accounts, "sin_cuenta": p.no_account,\n'
        '            "sin_confirmar": p.unconfirmed, "alias": p.aliases, "de": p.organization, "baja": p.left_on,\n'
        '            "compartida": p.shared_with, "registra": p.registered_by}\n'
        '\n'
        '\n'
        'class _Registro(dict):\n'
        '    """registro_personas()\'s dict, carrying the PeopleRegistry it was made from."""\n'
        '    registry: PeopleRegistry\n'
        '\n'
        '\n'
        'def _registro(reg: PeopleRegistry) -> _Registro:\n'
        '    dicts = {id(p): _persona(p) for p in reg.people}\n'
        '    r = _Registro(hay=reg.declared, personas=[dicts[id(p)] for p in reg.people],\n'
        '                  nombre={k: dicts[id(p)] for k, p in reg.by_name.items()},\n'
        '                  cuenta={k: dicts[id(p)] for k, p in reg.by_account.items()}, avisos=reg.warnings)\n'
        '    r.registry = reg\n'
        '    return r\n'
        '\n'
        '\n'
        'def _reg(reg) -> PeopleRegistry:\n'
        '    """Accepts what the scripts pass: the dict from registro_personas(), None or {}."""\n'
        '    return getattr(reg, "registry", None) or PeopleRegistry()\n'
        '\n'
        '\n'
        'def registro_personas(guia: str) -> dict:\n'
        '    return _registro(rules.people_registry(guia))\n'
        '\n'
        '\n'
        'def persona(nombre: str, reg) -> Optional[dict]:\n'
        '    """The person with that name, alias or account; None if missing or ambiguous."""\n'
        '    t = (nombre or "").strip()\n'
        '    if CORREO.fullmatch(t.lower()):\n'
        '        return (reg or {}).get("cuenta", {}).get(t.lower())\n'
        '    return (reg or {}).get("nombre", {}).get(clave_nombre(t))\n'
        '\n'
        '\n'
        'def nombres_de(texto: str, reg=None) -> list[str]:\n'
        '    return rules.names_in(texto, _reg(reg))\n'
        '\n'
        '\n'
        'def cuentas_de_nombres(texto: str, reg) -> tuple[set, list]:\n'
        '    return rules.accounts_of_names(texto, _reg(reg))\n'
        '\n'
        '\n'
        'def altas_provisionales(quien: str, reg) -> list:\n'
        '    return rules.provisional_people(quien, _reg(reg))\n'
        '\n'
        '\n'
        'def columnas_personas(cab: list) -> dict:\n'
        '    c = rules._people_columns(cab)\n'
        '    return {"responsable": c["responsible"], "cuenta": c["account"], "colabora": c["collaborates"]}\n'
        '\n'
        '\n'
        'def fila_cuentas(cab: list, celdas: list, reg) -> tuple:\n'
        '    return rules.row_accounts(cab, celdas, _reg(reg))\n'
        '\n'
        '\n'
        'def cuentas_contexto(linea: str, reg) -> set:\n'
        '    return rules.context_owner_accounts(linea, _reg(reg))\n'
        '\n'
        '\n'
        'def nombre_de(cuenta: str, reg) -> str:\n'
        '    return rules.name_of_account(cuenta, _reg(reg))\n'
        '\n'
        '\n'
        'def colaboran_en(quien: str, reg=None) -> set:\n'
        '    return rules.collaborator_accounts(quien, _reg(reg) if reg else None)\n'
        '\n'
        '\n'
        '# \u2500\u2500 el primer p\xe1rrafo de guia.md, los registros con sus archivados y la regla de lo restringido \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'SOBRE_LA_CARPETA = rules.ABOUT_THE_FOLDER\n'
        'sin_carpeta = rules.drop_folder_talk\n'
        'ARCHIVADO = rules.ARCHIVED\n'
        'restringida_celda = rules.is_restricted_cell\n'
        '\n'
        '\n'
        'def area_restringida(celdas: list, cab: list) -> bool:\n'
        '    """Whether a row of the area table is restricted, from the row and the table\'s header: the one rule (finding 10 of\n'
        '    the review of 1.25.2), the 1.25.1 abrir.py\'s area_restringida()."""\n'
        '    return rules.area_is_restricted(celdas, cab)\n'
        '\n'
        '\n'
        'def acceso_de(celda: str) -> Optional[bool]:\n'
        '    """\xabAcceso\xbb: True \xabRestringida\xbb, False \xabAbierta\xbb, None anything else."""\n'
        '    return rules.access_word(celda)\n'
        '\n'
        '\n'
        'def _nombres(carpeta) -> list:\n'
        '    try:\n'
        '        return [x.name for x in pathlib.Path(carpeta).iterdir()]\n'
        '    except OSError:\n'
        '        return []\n'
        '\n'
        '\n'
        'def archivados_de(carpeta, nombre, anio) -> list:\n'
        '    return rules.archived_names(_nombres(carpeta), nombre, anio)\n'
        '\n'
        '\n'
        'def con_archivados(carpeta, nombre, vivo, anio, leer_) -> tuple:\n'
        '    return rules.with_archives(vivo, [leer_(pathlib.Path(carpeta) / n) for n in archivados_de(carpeta, nombre, anio)])\n'
        '\n'
        '\n'
        'def respuestas_viejas(carpeta, anio, leer_) -> list:\n'
        '    """The \xabResponde a:\xbb lines of decision archives older than last year, which are not read whole."""\n'
        '    recientes = set(archivados_de(carpeta, "decisiones", anio))\n'
        '    out = []\n'
        '    for n in archivados_de(carpeta, "decisiones", 0):\n'
        '        if n not in recientes:\n'
        '            out += re.findall(r"^Responde a:[ \\t]*(.+)$", leer_(pathlib.Path(carpeta) / n) or "", re.M)\n'
        '    return out\n'
    ),
    }
    for _n in _todo:
        _m = _t.ModuleType("context_core." + _n); _m.__package__ = "context_core"; _m.__fingerprint__ = _fp[_n]
        _s.modules[_m.__name__] = _m
        exec(compile(_src[_n], "<context_core/" + _n + ".py>", "exec"), _m.__dict__)
        setattr(_pkg, _n, _m)
_context_core()
# --- end of context_core ---
from context_core.compat import (registro_personas, fila_cuentas, colaboran_en)  # noqa: E402
# --- fin de quién escribe ---

def mis_areas():
    """(áreas de las que la cuenta es responsable, áreas en las que colabora), según la tabla de áreas y «Quién es quién» de guia.md."""
    try:
        guia = (RAIZ / "guia.md").read_text(encoding="utf-8-sig")
    except OSError:
        return set(), set()
    m = re.search(r"^## Áreas\s*\n(.*?)(?=^## |\Z)", guia, re.S | re.M)
    if not m or not CUENTA:
        return set(), set()
    out, co, cab = set(), set(), None
    reg = registro_personas(guia)
    for l in m.group(1).split("\n"):
        if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
            continue
        celdas = [c.strip() for c in l.strip().strip("|").split("|")]
        if cab is None:
            cab = celdas; continue
        # cuentas enteras, no subcadenas: «ana@» no es «diana@»; cinco columnas, como abrir.py y el generador; y por el
        # encabezado, no por la posición: desde la 1.25 la cuarta columna puede ser Colabora, con nombres
        if len(celdas) >= 5:
            de, cb, _ = fila_cuentas(cab, celdas, reg)
            if CUENTA in de:
                out.add(celdas[0].strip("`").rstrip("/"))
            elif CUENTA in cb:
                co.add(celdas[0].strip("`").rstrip("/"))
    return out, co

MIAS, COLABORA = mis_areas()

def colabora_en_proyecto(area, slug):
    """La cuenta figura en la línea «Colabora:» de «Quién participa» de ese proyecto."""
    try:
        tp = (RAIZ / area / slug / "proyecto.md").read_text(encoding="utf-8-sig")
    except OSError:
        return False
    m = re.search(r"^## Quién participa\s*\n(.*?)(?=^## |\Z)", tp, re.S | re.M)
    try:
        reg = registro_personas((RAIZ / "guia.md").read_text(encoding="utf-8-sig"))
    except OSError:
        reg = None
    return CUENTA in colaboran_en(m.group(1) if m else "", reg)

def puede(t, c, area):
    """Las prioridades del área son de su responsable; lo demás lo escribe también quien colabora en el área o en el proyecto."""
    if not CUENTA or not area:
        return bool(CUENTA)
    if area in MIAS:
        return True
    if t == "prioridad":
        return False
    if area in COLABORA:
        return True
    a_, s_ = partes(c)
    return bool(a_) and colabora_en_proyecto(a_, s_)
REF_DEC = re.compile(r"[a-z0-9][a-z0-9-]*/[a-z0-9][a-z0-9-]*#20\d\d-\d\d-\d\d(?:-\d+)?", re.ASCII)   # area/proyecto#AAAA-MM-DD[-n]
NOMBRE = re.compile(r"[a-z0-9][a-z0-9-]*", re.ASCII)     # nombres de área y de proyecto, como el contrato (sección 6)
FECHA = re.compile(r"20[0-9]{2}-[0-9]{2}-[0-9]{2}", re.ASCII)

def nombre_ok(s):
    return isinstance(s, str) and NOMBRE.fullmatch(s) is not None     # fullmatch: un salto de línea final no pasa

def fecha_ok(s):
    if not (isinstance(s, str) and FECHA.fullmatch(s)):
        return False
    try:
        datetime.date.fromisoformat(s); return True        # 2026-02-30 no existe
    except ValueError:
        return False

def partes(c):
    """(area, slug) de un id «area--slug» bien formado; (None, None) si no lo es."""
    area, sep, slug = (c.get("proyecto") or "").partition("--") if isinstance(c.get("proyecto"), str) else ("", "", "")
    if not sep or not nombre_ok(area) or not nombre_ok(slug):
        return None, None
    return area, slug

def texto_de_una_linea(s):
    return isinstance(s, str) and s.strip() != "" and "\n" not in s and "\r" not in s

def cargar():
    docs = []
    if ENTRADA.is_dir():
        for p in sorted(ENTRADA.rglob("*.json")):
            d = json.loads(p.read_text(encoding="utf-8"))
            docs.append(d)
    else:
        d = json.loads(ENTRADA.read_text(encoding="utf-8"))
        docs = d if isinstance(d, list) else d.get("documents") or d.get("docs") or [d]
    out = []
    for d in docs:
        if "data" in d and isinstance(d["data"], dict):
            x = dict(d["data"]); x["id"] = d.get("id") or d.get("doc_id") or x.get("id")
        else:
            x = dict(d)
        if x.get("id"):
            out.append(x)
    return out

def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"^-\s*", "", s.strip()))

def aplicar_fecha(c):
    area, slug = partes(c)
    if not area:
        return "rechazados", f"id de proyecto mal formado: {c.get('proyecto')!r}"
    p = RAIZ / area / slug / "proyecto.md"
    try:
        dentro = p.resolve().is_relative_to((RAIZ / area).resolve())
    except (OSError, ValueError):
        dentro = False
    if not dentro:
        return "rechazados", f"la ruta sale del área: {area}/{slug}"
    if not p.exists():
        return "sin_match", f"no existe {area}/{slug}/proyecto.md"
    if not texto_de_una_linea(c.get("paso")):
        return "rechazados", "el cambio no dice a qué paso se refiere, o el paso trae saltos de línea"
    for k in ("fecha_anterior", "fecha_nueva"):
        if c.get(k) not in (None, "") and not fecha_ok(c.get(k)):
            return "rechazados", f"{k} no es una fecha AAAA-MM-DD que exista: {c.get(k)!r}"
    with open(p, encoding="utf-8", newline="") as fh:   # newline="" conserva los finales de línea del archivo
        texto = fh.read()
    m = re.search(r"(^## Siguientes pasos\s*\n)(.*?)(?=^## |\Z)", texto, re.S | re.M)
    if not m:
        return "sin_match", "proyecto.md sin sección Siguientes pasos"
    bloque = m.group(2)
    lineas = bloque.split("\n")
    ant, nue = c.get("fecha_anterior"), c.get("fecha_nueva")
    idx = next((i for i, l in enumerate(lineas) if norm(l) == norm(c["paso"])), None)
    if idx is None:
        # una corrida anterior pudo aplicarla y cortarse antes de vaciar la cola
        ya = {norm(c["paso"]).replace(ant, nue, 1)} if ant and nue else set()
        if nue and not ant: ya.add(norm(f"{nue}: " + norm(c["paso"])))
        if any(norm(l) in ya for l in lineas):
            return "aplicados", "ya estaba aplicada"
        return "sin_match", "el paso ya no está escrito igual"
    linea = lineas[idx]
    if ant and ant in linea:
        if nue:
            nueva = linea.replace(ant, nue, 1)
        else:
            nueva = re.sub(r"\s*(?:el|para el|antes del|hasta el)?\s*" + re.escape(ant) + r":?\s*", " ", linea, count=1)
            nueva = re.sub(r"\s{2,}", " ", nueva).rstrip()
    elif nue:
        cuerpo = re.sub(r"^(\s*-\s*)", "", linea)
        pref = re.match(r"^(\s*-\s*)", linea)
        nueva = (pref.group(1) if pref else "- ") + f"{nue}: " + cuerpo
    else:
        return "aplicados", "nada que cambiar"
    if nueva == linea:
        return "aplicados", "ya estaba así"
    lineas[idx] = nueva
    texto_nuevo = texto[:m.start(2)] + "\n".join(lineas) + texto[m.end(2):]
    if not DRY:
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(texto_nuevo)
    return "aplicados", f"{linea.strip()}  →  {nueva.strip()}"

rep = {"aplicados": [], "sin_match": [], "rechazados": [], "errores": [], "para_sesion": [], "para_su_dueno": [], "propuestas": [],
       "cuenta": CUENTA, "mis_areas": sorted(MIAS), "colabora": sorted(COLABORA), "dry_run": DRY}
for c in cargar():
    t = c.get("tipo")
    area = partes(c)[0] or (c.get("area") if nombre_ok(c.get("area")) else "") or ""
    if t == "propuesta":
        # las escribe el barrido del plugin, no un contribuidor: no se aplican, no esperan a ningún responsable; se cuentan aparte
        if not partes(c)[0] or not texto_de_una_linea(c.get("texto")) or \
           any(c.get(k) not in (None, "") and not texto_de_una_linea(c.get(k)) for k in ("por_que", "clase", "ruta", "afirma")) or \
           (c.get("rutas") is not None and not (isinstance(c["rutas"], list) and c["rutas"] and all(texto_de_una_linea(r) for r in c["rutas"]))):
            rep["rechazados"].append({"id": c["id"], "detalle": "propuesta sin proyecto «area--slug», sin texto, o con saltos de línea"})
            continue
        rep["propuestas"].append(c["id"])
        continue
    if t == "respuesta" and (not partes(c)[0] or not REF_DEC.fullmatch(str(c.get("decision") or "")) or c.get("valor") not in ("aceptada", "cuestionada")):
        rep["rechazados"].append({"id": c["id"], "detalle": "respuesta sin proyecto «area--slug», sin identificador de decisión o con un valor que no es «aceptada» ni «cuestionada»"})
        continue
    if t == "respuesta":
        # la decisión tiene que existir: su proyecto y una entrada con esa fecha en sus decisiones (riesgos de la 1.24)
        _ap, _fe = str(c["decision"]).split("#", 1)
        _dd = RAIZ / _ap / "decisiones.md"
        try:
            _hay = _dd.is_file() and re.search(r"(?m)^##\s+" + re.escape(_fe[:10]) + r"\b", _dd.read_text(encoding="utf-8")) is not None
        except (OSError, UnicodeError):
            _hay = True   # no se pudo leer: que lo vea la sesión
        if not _hay and not list((RAIZ / _ap).glob("decisiones-*.md")):
            rep["rechazados"].append({"id": c["id"], "detalle": f"respuesta a una decisión que no está en la carpeta: {c['decision']}"})
            continue
    if t in ("fecha", "hecho", "nota", "corregir", "prioridad", "respuesta") and c.get("proyecto") and not partes(c)[0]:
        rep["rechazados"].append({"id": c["id"], "detalle": f"id de proyecto mal formado: {c.get('proyecto')!r}"})
        continue
    if t in ("fecha", "hecho", "nota", "corregir", "prioridad", "respuesta") and not puede(t, c, area):
        rep["para_su_dueno"].append({"id": c["id"], "tipo": t, "proyecto": c.get("proyecto"), "area": area,
                                     "detalle": "falta --cuenta" if not CUENTA else (f"las prioridades de {area} son de su responsable" if t == "prioridad" and area in COLABORA else f"el área {area or '?'} no es de {CUENTA}")})
        continue
    if t == "fecha":
        try:
            estado, detalle = aplicar_fecha(c)
        except (OSError, UnicodeError) as e:   # sin permiso de escritura, archivo sin descargar…
            estado, detalle = "errores", f"{type(e).__name__}: {e}"
        rep[estado].append({"id": c["id"], "proyecto": c.get("proyecto"), "detalle": detalle})
    elif t in ("hecho", "nota", "corregir", "prioridad", "respuesta"):
        if any(not texto_de_una_linea(c[k]) for k in ("paso", "nota", "propuesta", "texto", "porque", "titulo", "decidio", "espera", "decision", "por") if c.get(k) not in (None, "")):
            rep["rechazados"].append({"id": c["id"], "detalle": "paso, nota, propuesta, texto o porqué con saltos de línea"})
            continue
        rep["para_sesion"].append({k: c.get(k) for k in ("id", "tipo", "proyecto", "paso", "nota", "propuesta", "campo", "creado", "area", "indice", "texto", "por")} | ({k: c.get(k) for k in ("decision", "valor", "porque", "titulo", "decidio")} if t == "respuesta" else {})
                                   | ({k: c[k] for k in ("espera", "decision") if c.get(k)} if t == "nota" else {}))
    else:
        rep["sin_match"].append({"id": c["id"], "detalle": f"tipo desconocido: {t}"})
print(json.dumps(rep, ensure_ascii=False, indent=1))
