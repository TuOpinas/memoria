#!/usr/bin/env python3
"""Escribe lo que deja un cierre de sesión (skill sesion, anexo cerrar.md), archivo por archivo y sin pisar a nadie.

La skill prepara los textos; este script los escribe. De cada archivo hace leer → cambiar → escribir bajo un cerrojo por
archivo, y comprueba justo antes de escribir que el archivo sigue como lo leyó (misma fecha, tamaño y contenido); si cambió
entre medias, vuelve a leerlo y aplica el cambio sobre lo nuevo (compare-and-swap). Así, dos cierres sobre el mismo
proyecto a la vez no se pierden una entrada ni un paso: cada entrada va encima de lo que haya, y cada reemplazo se aplica
sobre la versión que está en el disco. Lo que otra persona escribió desde que se abrió la sesión se dice (--abierto).

Uso:
  cerrar.py <raiz> <area>/<proyecto> <cambios.json> [--cuenta <correo>] [--abierto <hora ISO de la línea «ahora» de abrir.py>]
            [--sin-fechas] [--forzar <ruta>]... [--fuera-del-area <ruta>]... [--cualquier-fecha] [--sin-rotar] [--comprobar]

cambios.json, todo opcional:
  {"sesion": "## AAAA-MM-DD\\nTema: …\\nAvances: …\\nSesión de: Nombre · plugin X.Y.Z",
   "decisiones": ["## AAAA-MM-DD · Título\\nDecidió: …\\nPor qué: …\\nDescartado: …", …],
   "escribio": ["entregables/x.md", "taller/y.md"], "publico": ["entregables/z.md"],
   "proyecto": {"estatus": "texto entero del bloque Estatus, sin el encabezado: «AAAA-MM-DD · **frase**» y sus viñetas",
                "reemplazos": [{"de": "texto exacto viejo", "a": "texto nuevo"}, …]},
   "area": {"linea": "- `slug/` — descripción",
            "entregables": [{"archivo": "x.md"}, "  - nombre — línea ya escrita · actualizado AAAA-MM-DD", …]},
   "estatus_area": "texto entero del bloque Estatus de area.md, sin el encabezado, con las prioridades debajo de «Siguiente»",
   "otros": [{"ruta": "<relativa a la raíz, dentro del área del proyecto>", "reemplazos": [{"de": "…", "a": "…"}]}, …]}

Se escriben solo los nombres de la 1.22, también en una raíz sin migrar: el bloque Estatus va debajo del título y retira un
«En corto» o un «Panorama» que haya; en un área, retira también «Prioridades ahora», y las prioridades que no estén ya en el
Estatus nuevo se añaden debajo de «Siguiente» (vuelven en «fundidas»), para que no se pierda ninguna; sin ninguno de los
viejos, el Estatus se crea debajo del título. Cada Estatus tiene que empezar por «AAAA-MM-DD · **…**». Una entrada nueva con
«Trabajamos en:», «Pendiente:» o «Descartamos:» se rechaza: los registros viejos se quedan como están, pero lo nuevo se
escribe con «Tema:» y «Descartado:». Un entregable dado como {"archivo": "x.md"} se escribe en area.md como
«  - x — <su aportacion> · actualizado <su fecha>», leídas de su cabecera en entregables/ (o «afirma», si la cabecera aún
no se migró); sin ninguna de las dos, se conserva la línea que ese entregable ya tenía en el bloque y va en «sin_match». Si
«entregables» no viene, las líneas que había debajo del proyecto se conservan: el índice nunca pierde un entregable por un
cierre. «otros» se escribe antes que area.md, para que la línea de un entregable que se publica en la misma llamada lleve
la fecha nueva.

«escribio» y «publico» son los documentos que la sesión escribió (creó o cambió en su contenido) y los que publicó (pasó a
vigente con la skill revisar), con su ruta dentro del proyecto. Van a la entrada de la sesión como «Escribió: …» y
«Publicó: …», justo antes de «Sesión de:», cada una solo si trae algo; así el tablero atribuye cada documento a quien lo
escribió y a quien lo publicó (escribir.md, formato de sesiones.md). Cada ruta tiene que estar en entregables/ o taller/ del
proyecto y existir; lo que se publica, en entregables/ y vigente. Con --abierto, la salida trae en «sin_nombrar» los
documentos de entregables/ y taller/ que cambiaron desde que se abrió y no van en ninguna de las dos listas, para que la
sesión diga si son suyos: no se atribuyen solos, porque pudo escribirlos otra persona. Con --comprobar no se escribe nada:
se validan la forma y la autoría (no los reemplazos ni los permisos) y se devuelven «entrada» (la entrada tal como quedaría, con sus líneas) y «sin_nombrar», para enseñarla
completa antes de pedir el sí. Una «Escribió:» o «Publicó:» tecleada en «sesion» se rechaza, y con «escribio» o «publico»
la entrada tiene que llevar «Sesión de: Nombre».

Antes de escribir una entrada en sesiones.md o en decisiones.md, si el registro pasa de 1.500 líneas o de 100 KB, o su
entrada más nueva es de un año anterior, se archiva entero como «<registro>-<año>.md» (si ya existe, «-2», «-3»…) y el vivo
queda con su cabecera, su título y la línea «Archivado:»; la entrada de hoy va en el nuevo. Vuelve en «rotados» (de, a,
motivo, entradas). --sin-rotar lo evita. abrir.py y el tablero leen los archivados de este año y del anterior junto al vivo.

Antes de escribir nada se comprueba todo: «sesion» empieza por «## AAAA-MM-DD» y cada decisión por «## AAAA-MM-DD · », y esa
fecha es hoy o ayer en la zona horaria de guia.md (la línea HOY de abrir.py), nunca la del reloj de la consola o del
contenedor, que van en UTC y por la tarde ya dicen mañana; una fecha distinta a propósito pasa solo con --cualquier-fecha;
cada ruta de «otros» está dentro del área del proyecto (fuera, solo con --fuera-del-area y nunca guia.md, base/ ni
restringido/). Con --cuenta, el Estatus del área lo escribe solo su responsable (la celda Cuenta de guia.md) y la línea del
proyecto en area.md, el responsable o quien colabora en el área; lo que no toca va en «rechazados». Cada entrada de registro va
arriba del todo, debajo del título; una igual que ya esté no se repite. Un reemplazo cuyo texto viejo no aparece
exactamente una vez, cruza un encabezado «## » o pasa de doce líneas no se aplica y vuelve en «sin_match». Un archivo que
encogería a menos de la mitad no se escribe salvo con --forzar <ruta>. `actualizado` de la cabecera se pone a hoy (salvo cuando lo único que cambia es la cabecera, como añadir `aportacion`) (en la
zona horaria de guia.md) en cada archivo escrito; los finales de línea se conservan como estaban.

Lo primero, antes que todo lo demás (1.26): si guia.md tiene la sección «Versión mínima del plugin» y este script es de un
plugin anterior a esa versión (ESTE_PLUGIN, que pone release.sh), o la sección no dice qué versión, no escribe nada, ni con
--comprobar: imprime el JSON con «error» (el motivo en llano, con cómo actualizar), «solo_lectura», «version_minima» y
«plugin», y sale con 6.

Imprime siempre un JSON: «escritos», «sin_match», «rechazados», «fallidos» (un archivo que no se pudo leer o escribir, con
el motivo), «ajenos» (archivos que alguien cambió desde --abierto, con la hora; también los que cambiaron mientras este
cierre escribía; nunca los que este mismo cierre escribió), «reintentos», «hora» (ahora, ISO 8601 en minutos UTC, para la
marca del tablero), «documento» (el id de esa marca) y «escrito_en» (la hora de esta escritura, para pasar como --abierto si
se repite la llamada); y, si alguno de «publico» no quedó vigente tras los reemplazos de «otros», «no_publicado» con
esas rutas y un «error»: no se escribe la entrada ni lo demás (solo «otros» y, si tocaba, la rotación de los registros), y la
llamada se repite arreglada, sin los reemplazos de «otros» que ya salieron en «escritos» (1.24.2). Con --sin-fechas (sin consola: la copia lleva la fecha de cuándo se trajo) «ajenos» va vacío.
"""
import datetime
import hashlib
import json
import os
import pathlib
import re
import sys
import tempfile
import time

ESTE_PLUGIN = "1.25.8"   # la versión del plugin de este script: la pone release.sh, y con ella se compara la versión mínima de la raíz (1.26)
INTENTOS = 5
MAX_LINEAS_REEMPLAZO = 12
LIMITE_LINEAS, LIMITE_BYTES = 1500, 100_000   # la rotación de los registros (escribir.md, sección 8; por tamaño desde la 1.23)

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
    'language': '24b071b179cb457779fa0f747e95755a960bbb1f93ebee8e54117271b19de191',
    'records': '074bd7a0994a2cdf904cfa82827c7f26b226caff14317513a01d1a2af6a34def',
    'rules': 'f2f559f0c6a875d658946566ea70f1363c07c2f60cc6b5ecd669a68a372034f2',
    'compat': '257a02f646182e3afcba1c1ba2811bc636decee93d25c9df143b48e377e82f77',
    'write': '0775119f7676e9dc1a9a47c880c6fcea328ef4217e355394b627cd48f5ea2179',
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
        '    # guia.md: the section that declares the oldest plugin that may write in the root (1.26)\n'
        '    minimum_plugin: str = ""\n'
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
        '    minimum_plugin="Versi\xf3n m\xednima del plugin",\n'
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
        '    old_responses: list[DecisionRef] = field(default_factory=list)  # \xabResponde a\xbb of decision archives older than last year, not read whole\n'
        '    loaded: frozenset = frozenset()             # which parts load_project read (load.PARTS); empty: only its index line\n'
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
        "restricted, guia.md's first paragraph, the archived registers and the minimum plugin version that may write. Pure functions: no I/O, no globals, no clock.\n"
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
        '\n'
        '\n'
        '# \u2500\u2500 the minimum plugin version (1.26) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        '_VERSION = re.compile(r"(?<![\\d.])(\\d+)\\.(\\d+)(?:\\.(\\d+))?(?!\\.?\\d)")\n'
        '\n'
        '\n'
        'def version_tuple(text: str) -> Optional[tuple]:\n'
        '    """\xab1.26\xbb or \xab1.26.0\xbb (the first version in `text`) as (1, 26, 0); None without one."""\n'
        '    m = _VERSION.search(text or "")\n'
        '    return (int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)) if m else None\n'
        '\n'
        '\n'
        'def minimum_plugin_version(guia: str, lang: Pack = ES) -> tuple[bool, Optional[tuple]]:\n'
        '    """(declared, version) from the section \xab## Versi\xf3n m\xednima del plugin\xbb of guia.md, written by the migration that needs\n'
        '    it. (False, None): no section, anyone may write. (True, None): a section with no version in its first paragraph,\n'
        '    which nobody may write under until it is fixed (fail closed: a typo must not let an old plugin through)."""\n'
        '    m = re.search(r"^##[ \\t]+" + re.escape(lang.minimum_plugin) + r"[ \\t]*$(.*?)(?=^##[ \\t]|\\Z)", guia or "", re.M | re.S)\n'
        '    if not m:\n'
        '        return False, None\n'
        '    first = next((b for b in re.split(r"\\n\\s*\\n", m.group(1).strip()) if b.strip()), "")\n'
        '    return True, version_tuple(first)\n'
        '\n'
        '\n'
        'def plugin_may_write(plugin_version: str, guia: str, lang: Pack = ES) -> tuple[str, Optional[tuple]]:\n'
        '    """Whether a plugin may write in the root of this guia.md: ("ok", minimum or None), ("below", minimum),\n'
        '    ("unreadable", None) for a section with no version, or ("unknown", minimum) for a plugin version that does not parse.\n'
        '    Reading is never gated; only writing (decision of 2026-11-08)."""\n'
        '    declared, minimum = minimum_plugin_version(guia, lang)\n'
        '    if not declared:\n'
        '        return "ok", None\n'
        '    if minimum is None:\n'
        '        return "unreadable", None\n'
        '    mine = version_tuple(plugin_version)\n'
        '    if mine is None:\n'
        '        return "unknown", minimum\n'
        '    return ("ok" if mine >= minimum else "below"), minimum\n'
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
        '           "nombre_contexto", "cuentas_contexto", "nombre_de", "colaboran_en", "RECETA_ACTUALIZAR", "puerta_de_escritura"]\n'
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
        '\n'
        '\n'
        '# \u2500\u2500 la versi\xf3n m\xednima del plugin (1.26) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'RECETA_ACTUALIZAR = ("Actual\xedzalo en la app de Claude, en Customize \u2192 Plugins, con el bot\xf3n Update del marketplace memoria-marketplace "\n'
        '                     "(en Claude Code, /plugin marketplace update memoria-marketplace), o pide ayuda a quien administra la carpeta.")\n'
        '\n'
        '\n'
        'def puerta_de_escritura(version_plugin: str, guia: str) -> tuple:\n'
        '    """(puede escribir, versi\xf3n m\xednima como texto o None, motivo en llano o ""): la secci\xf3n \xabVersi\xf3n m\xednima del plugin\xbb\n'
        '    de guia.md frente a la versi\xf3n del plugin que corre. El motivo es lo que se le dice a la persona."""\n'
        '    estado, minima = rules.plugin_may_write(version_plugin, guia)\n'
        '    txt = ".".join(map(str, minima)) if minima else None\n'
        '    if estado == "ok":\n'
        '        return True, txt, ""\n'
        '    if estado == "unreadable":\n'
        '        return False, None, ("La secci\xf3n \xabVersi\xf3n m\xednima del plugin\xbb de guia.md no dice qu\xe9 versi\xf3n: hasta que el responsable de "\n'
        '                             "contexto la corrija, no se escribe nada en esta carpeta. Leer y consultar siguen funcionando.")\n'
        '    if estado == "unknown":\n'
        '        return False, txt, (f"No s\xe9 qu\xe9 versi\xf3n del plugin corre aqu\xed (\xab{version_plugin}\xbb) y esta carpeta pide la {txt} o una m\xe1s "\n'
        '                            "nueva para escribir: no se escribe nada. Leer y consultar siguen funcionando.")\n'
        '    return False, txt, (f"Tu plugin memoria es la {version_plugin} y esta carpeta pide la {txt} o una m\xe1s nueva para escribir: "\n'
        '                        "puedes leer y consultar, pero no se escribe nada (ni sesiones, ni decisiones, ni documentos, ni el tablero) "\n'
        '                        f"hasta que lo actualices. {RECETA_ACTUALIZAR}")\n'
    ),
    'write': (
        '"""Writing the method\'s files: the text changes every writer applies, and the entries a writer composes from fields.\n'
        '\n'
        "One copy for the plugin's cerrar.py and the hosted server (decision of 2026-11-05: an operation moves onto the package\n"
        'when its tool is built, and both call the same function). Pure functions, text in and text out: reading the file, the\n'
        "lock and the write that fails if the file changed are the caller's, through its storage adapter.\n"
        '\n'
        'Two parts:\n'
        "Input texts are what the storage adapter's `Document.text` gives: \xab\\n\xbb line endings and no BOM.\n"
        '\n'
        '- The text changes, moved here from cerrar.py 1.25.4 with the same results (tests/test_write.py checks them against\n'
        "  the 1.25.4 copies frozen in tests/reference/): the header's `actualizado`, a register entry on top, a whole \xab## \xbb\n"
        '  block rewritten. cerrar.py imports them from here under its Spanish names.\n'
        '- The entries composed from fields (a session entry, a decision, an Estatus), for a writer that receives fields and\n'
        '  not text, the server. Each field is checked first: a field that is one line has no line break of any kind, and a text\n'
        '  field cannot carry a heading, a header line, or a line that a reader would take for another field of the same\n'
        '  register (a \xabPublic\xf3:\xbb inside \xabAvances\xbb would read as a publication). The writer, not the caller, puts the date and\n'
        '  the author.\n'
        '"""\n'
        'from __future__ import annotations\n'
        '\n'
        'import re\n'
        'import unicodedata\n'
        'from typing import Iterable, Optional\n'
        '\n'
        'from .language import ES, Pack\n'
        '\n'
        '__all__ = ["with_header_today", "only_header_changed", "with_entry_on_top", "with_entries_on_top", "without_block",\n'
        '           "with_block", "DECISION_ID", "is_decision_ref", "FieldError", "one_line", "text_field", "session_entry",\n'
        '           "decision_entry", "status_block"]\n'
        '\n'
        '\n'
        '# \u2500\u2500 text changes (cerrar.py 1.25.4: cabecera_hoy, solo_cabecera, con_entrada_arriba, sin_bloque, con_bloque) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'def with_header_today(text: str, today: str) -> str:\n'
        '    """The header\'s `actualizado` set to `today`, added if missing. A file without a header is left as it is."""\n'
        '    m = re.match(r"^---\\n(.*?)\\n---\\n", text, re.S)\n'
        '    if not m:\n'
        '        return text\n'
        '    head = re.sub(r"^actualizado:.*$", f"actualizado: {today}", m.group(1), count=1, flags=re.M)\n'
        '    if "actualizado:" not in head:\n'
        '        head += f"\\nactualizado: {today}"\n'
        '    return f"---\\n{head}\\n---\\n" + text[m.end():]\n'
        '\n'
        '\n'
        'def only_header_changed(before: str, after: str) -> bool:\n'
        '    """True if the only change between the two texts is inside the header (between the two first \xab---\xbb)."""\n'
        '    m1, m2 = re.match(r"^---\\n.*?\\n---\\n", before, re.S), re.match(r"^---\\n.*?\\n---\\n", after, re.S)\n'
        '    return bool(m1 and m2) and before[m1.end():] == after[m2.end():] and before != after\n'
        '\n'
        '\n'
        'def with_entry_on_top(text: str, entry: str) -> tuple:\n'
        '    """A new register entry under the title and above the rest; if it is already there, nothing. Returns (text, added)."""\n'
        '    entry = entry.strip() + "\\n"\n'
        '    if entry.strip() in text:\n'
        '        return text, False\n'
        '    m = re.search(r"^# .*\\n", text, re.M)\n'
        '    if m:\n'
        '        i = m.end()\n'
        '        rest = text[i:]\n'
        '        j = re.search(r"^## ", rest, re.M)\n'
        '        if j:\n'
        '            preface, body = rest[:j.start()], rest[j.start():]\n'
        '            if not preface.strip():\n'
        '                preface = "\\n"\n'
        '            elif not preface.endswith("\\n\\n"):\n'
        '                preface = preface.rstrip("\\n") + "\\n\\n"\n'
        '            return text[:i] + preface + entry + "\\n" + body, True\n'
        '        # no entries yet (a register just opened, or just archived with its \xabArchivado:\xbb line): what is under the title\n'
        '        # stays before the first entry\n'
        '        return text[:i] + ("\\n" + rest.strip("\\n") + "\\n" if rest.strip() else "") + "\\n" + entry, True\n'
        '    return text.rstrip("\\n") + "\\n\\n" + entry, True\n'
        '\n'
        '\n'
        'def with_entries_on_top(text: str, entries: Iterable[str]) -> tuple:\n'
        '    """Several entries given from the oldest to the newest, so the last one given ends on top (cerrar.py\'s order, which\n'
        '    fixes the identifiers `#AAAA-MM-DD-n` of entries of the same day). Returns (text, any added)."""\n'
        '    added = False\n'
        '    for e in entries:\n'
        '        text, a = with_entry_on_top(text, e)\n'
        '        added = added or a\n'
        '    return text, added\n'
        '\n'
        '\n'
        'def without_block(text: str, name: str) -> str:\n'
        '    """The whole \xab## name\xbb block removed, if it is there."""\n'
        '    return re.sub(r"^## " + re.escape(name) + r"\\s*\\n.*?(?=^## |\\Z)", "", text, count=1, flags=re.M | re.S)\n'
        '\n'
        '\n'
        'def with_block(text: str, name: str, body: str, before: Optional[str] = None, aliases: Iterable[str] = ()) -> str:\n'
        '    """The whole \xab## name\xbb block rewritten. If it does not exist, it is created under the title or, with `before`, just\n'
        '    before that block (at the end if that one is missing too). The blocks named in `aliases` (older names of the same\n'
        '    block) are removed, wherever they were."""\n'
        '    body = body.strip() + "\\n"\n'
        '    for old in aliases:\n'
        '        text = without_block(text, old)\n'
        '    m = re.search(r"^## " + re.escape(name) + r"\\s*\\n(.*?)(?=^## |\\Z)", text, re.M | re.S)\n'
        '    if m:\n'
        '        return text[:m.start(1)] + body + "\\n" + text[m.end(1):]\n'
        '    new = f"## {name}\\n{body}\\n"\n'
        '    if before:\n'
        '        mb = re.search(r"^## " + re.escape(before) + r"\\s*$", text, re.M)\n'
        '        if mb:\n'
        '            return text[:mb.start()] + new + text[mb.start():]\n'
        '        return text.rstrip("\\n") + "\\n\\n" + new\n'
        '    mt = re.search(r"^# .*\\n", text, re.M)\n'
        '    i = mt.end() if mt else 0\n'
        '    return text[:i] + "\\n" + new + text[i:].lstrip("\\n")\n'
        '\n'
        '\n'
        '# \u2500\u2500 fields \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        "# an entry's identifier, as escribir.md \xa74 writes it: `area/proyecto#AAAA-MM-DD`, with -2, -3\u2026 for later entries of the\n"
        "# same day, and a bare `#AAAA-MM-DD` inside the same project; the slug alphabet is parse.decision_ref's\n"
        'DECISION_ID = re.compile(r"^`?(?:[a-z0-9][\\w.-]*/[a-z0-9][\\w.-]*)?#20\\d\\d-\\d\\d-\\d\\d(?:-\\d+)?`?(?:\\s*(?:\xb7|\\().*)?$")\n'
        '# in the title after an identifier: another identifier or a premise, which readers would take as the target instead\n'
        '_SECOND_TARGET = re.compile(r"#20\\d\\d-\\d\\d-\\d\\d|premisa\\s+P\\d", re.I)\n'
        '_INVISIBLE = re.compile("[\\u00ad\\u200b-\\u200f\\u2060-\\u2064\\ufeff]")\n'
        '_VERSION = re.compile(r"^\\d+(?:\\.\\d+)+$")\n'
        '# what parse.sessions splits \xabSesi\xf3n de\xbb on to find the name: an author cannot contain it\n'
        '_BY_SEPARATORS = re.compile(r"\\s+[\xb7\\-\u2013\u2014]\\s+|\\(")\n'
        '\n'
        '# every character str.splitlines() and Markdown readers treat as a line break, \xab\\n\xbb included\n'
        '_BREAKS = re.compile("[\\r\\n\\v\\f\\x1c\\x1d\\x1e\\x85\u2028'
        '\u2029'
        ']")\n'
        '_OTHER_BREAKS = re.compile("[\\r\\v\\f\\x1c\\x1d\\x1e\\x85\u2028'
        '\u2029'
        ']")\n'
        '\n'
        '\n'
        'class FieldError(ValueError):\n'
        '    """A field the writer refuses. `field` is the caller\'s name for it; the message names nothing else."""\n'
        '\n'
        '    def __init__(self, field: str, message: str):\n'
        '        super().__init__(f"{field} {message}")\n'
        '        self.field = field\n'
        '\n'
        '\n'
        'def is_decision_ref(text: str) -> bool:\n'
        '    """One entry identifier, alone or with its title; never a second identifier or a premise inside the title."""\n'
        '    t = (text or "").strip()\n'
        '    m = re.match(r"^`?(?:[a-z0-9][\\w.-]*/[a-z0-9][\\w.-]*)?#20\\d\\d-\\d\\d-\\d\\d(?:-\\d+)?`?", t)\n'
        '    return bool(DECISION_ID.match(t)) and bool(m) and not _SECOND_TARGET.search(t[m.end():])\n'
        '\n'
        '\n'
        'def _key(line: str) -> str:\n'
        '    """A line as every reader would see it: compatibility forms folded (NFKC), case folded (\xab\u017f\xbb is \xabs\xbb), invisible\n'
        '    characters dropped, and the Markdown that only changes how it looks (a quote, a list bullet) removed."""\n'
        '    k = _INVISIBLE.sub("", unicodedata.normalize("NFKC", line)).casefold().strip()\n'
        '    while True:\n'
        '        k2 = re.sub(r"^(?:>|[-*+](?=\\s)|\\d+[.)](?=\\s))\\s*", "", k)\n'
        '        if k2 == k:\n'
        '            return k\n'
        '        k = k2\n'
        '\n'
        '\n'
        'def _labels(pack: Pack, register: str) -> list:\n'
        '    """The lowercase labels a reader takes as a field of this register, without their colon."""\n'
        '    if register == "sessions":\n'
        '        words = pack.session_topic + pack.session_progress + pack.session_pending + pack.session_by\n'
        '        words += pack.session_wrote + pack.session_published\n'
        '    elif register == "decisions":\n'
        '        words = tuple(w for w, _ in pack.decision_fields)\n'
        '    else:\n'
        '        raise ValueError(f"no register {register!r}")\n'
        '    return sorted({_key(w.rstrip(":")) for w in words}, key=len, reverse=True)\n'
        '\n'
        '\n'
        'def one_line(value: str, field: str, required: bool = True, limit: int = 600) -> str:\n'
        '    v = (value or "").strip()\n'
        '    if required and not v:\n'
        '        raise FieldError(field, "is required")\n'
        '    if _BREAKS.search(v):\n'
        '        raise FieldError(field, "must be one line")\n'
        '    if len(v) > limit:\n'
        '        raise FieldError(field, f"is longer than {limit} characters")\n'
        '    return v\n'
        '\n'
        '\n'
        'def text_field(value: str, field: str, register: str, pack: Pack = ES, required: bool = True, limit: int = 4000) -> str:\n'
        '    """A field that may run over several lines, as written in `register` ("sessions" or "decisions"): \xab\\\\r\\\\n\xbb becomes\n'
        '    \xab\\\\n\xbb; any other line break, a heading, a header line or a line starting with a field label of that register is\n'
        '    refused. Returned normalised (each line stripped, blank lines dropped, as the readers read it), so what is written\n'
        '    is exactly what was checked and what is read back."""\n'
        '    v = (value or "").replace("\\r\\n", "\\n")\n'
        '    if _OTHER_BREAKS.search(v):\n'
        '        raise FieldError(field, "cannot contain a line break other than a plain newline")\n'
        '    # the readers strip every line and skip blank ones: written that way, what is read back is what was given\n'
        '    v = "\\n".join(l.strip() for l in v.split("\\n") if l.strip())\n'
        '    if required and not v:\n'
        '        raise FieldError(field, "is required")\n'
        '    if len(v) > limit:\n'
        '        raise FieldError(field, f"is longer than {limit} characters")\n'
        '    labels = _labels(pack, register)\n'
        '    for line in v.split("\\n"):\n'
        '        s = _key(line)\n'
        '        bare = re.sub(r"\\s", "", _INVISIBLE.sub("", line))\n'
        '        if s.startswith("#") or re.match(r"^(?:-{3,}|={3,}|_{3,}|\\*{3,})$", bare):\n'
        '            raise FieldError(field, "cannot contain a heading, a header line or a rule")\n'
        '        for label in labels:\n'
        '            if s.startswith(label) and re.match(r"\\s*:", s[len(label):]):\n'
        '                raise FieldError(field, f"cannot contain a line that starts with a field of the register (\xab{label}:\xbb)")\n'
        '    return v\n'
        '\n'
        '\n'
        '# \u2500\u2500 entries composed from fields \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'def session_entry(date: str, topic: str, progress: str, by: str, writer: str, version: str,\n'
        '                  wrote: Iterable[str] = (), published: Iterable[str] = (), pack: Pack = ES) -> str:\n'
        '    """A sesiones.md entry (escribir.md \xa74). `writer` is "plugin" or "server"; the date and the author are the\n'
        '    writer\'s, never the caller\'s. Each field is checked as `one_line` or `text_field`."""\n'
        '    w = pack.write_session\n'
        '    if writer not in pack.writers:\n'
        '        raise FieldError("writer", f"must be one of {\', \'.join(sorted(pack.writers))}")\n'
        '    topic = one_line(topic, "topic")\n'
        '    progress = text_field(progress, "progress", "sessions", pack)\n'
        '    by = one_line(by, "by", limit=80)\n'
        '    words = "|".join(re.escape(x) for x in pack.writers.values())\n'
        '    if _BY_SEPARATORS.search(by) or re.search(r"\\b(?:" + words + r")\\s+\\d", by, re.I):\n'
        '        raise FieldError("by", "cannot contain \xab \xb7 \xbb, \xab - \xbb, \xab(\xbb or a writer and a version: readers split the line there")\n'
        '    version = one_line(version, "version", limit=20)\n'
        '    if not _VERSION.match(version):\n'
        '        raise FieldError("version", "must be a version like 1.25.5")\n'
        '    lines = [f"## {one_line(date, \'date\')}", f"{w[\'topic\']}: {topic}", f"{w[\'progress\']}: {progress}"]\n'
        '    wrote, published = _paths(wrote, "wrote", pack), _paths(published, "published", pack)\n'
        '    if wrote:\n'
        '        lines.append(f"{w[\'wrote\']}: {\', \'.join(wrote)}")\n'
        '    if published:\n'
        '        lines.append(f"{w[\'published\']}: {\', \'.join(published)}")\n'
        '    lines.append(f"{w[\'by\']}: {by} \xb7 {pack.writers[writer]} {version}")\n'
        '    return "\\n".join(lines)\n'
        '\n'
        '\n'
        'def _paths(paths: Iterable[str], field: str, pack: Pack = ES) -> list:\n'
        '    """Paths inside the project, as cerrar.py accepts them: relative, no \xab..\xbb, nothing restricted, nothing the reader\n'
        '    would strip or split (\xab`\xbb, \xab,\xbb)."""\n'
        '    out = []\n'
        '    for p in paths or ():\n'
        '        p = one_line(p, field, limit=300)\n'
        '        parts = p.split("/")\n'
        '        if "," in p or "`" in p or p.startswith("/") or ".." in parts or pack.restricted in parts:\n'
        '            raise FieldError(field, f"{p!r} is not a path inside the project that can be named")\n'
        '        if p not in out:\n'
        '            out.append(p)\n'
        '    return out\n'
        '\n'
        '\n'
        'def decision_entry(date: str, title: str, decided_by: str, why: str, discarded: str = "", replaces: str = "",\n'
        '                   responds_to: str = "", affects: str = "", project: str = "", pack: Pack = ES) -> str:\n'
        '    """A decisiones.md decision (escribir.md \xa74), its lines in the contract\'s order and only those that say something.\n'
        '    `replaces` and `responds_to` must be entry identifiers; a bare \xab#AAAA-MM-DD\xbb is qualified with `project`\n'
        '    (\xabarea/project\xbb), since readers resolve only the full form. A challenge is not composed here: a title that reads as\n'
        '    one is refused."""\n'
        '    w = pack.write_decision\n'
        '    title = one_line(title, "title")\n'
        '    if re.match(re.escape(pack.challenge_title) + r"\\b", title, re.I):\n'
        '        raise FieldError("title", f"cannot start with \xab{pack.challenge_title}\xbb: readers take the entry for a challenge")\n'
        '    lines = [f"## {one_line(date, \'date\')} \xb7 {title}",\n'
        '             f"{w[\'decided_by\']}: {one_line(decided_by, \'decided_by\', limit=200)}",\n'
        '             f"{w[\'why\']}: {text_field(why, \'why\', \'decisions\', pack)}"]\n'
        '    discarded = text_field(discarded, "discarded", "decisions", pack, required=False)\n'
        '    if discarded:\n'
        '        lines.append(f"{w[\'discarded\']}: {discarded}")\n'
        '    for key, value in (("replaces", replaces), ("responds_to", responds_to)):\n'
        '        v = one_line(value, key, required=False)\n'
        '        if v and not is_decision_ref(v):\n'
        '            raise FieldError(key, "must be an entry identifier, \xabarea/project#AAAA-MM-DD \xb7 its title\xbb")\n'
        '        if v.lstrip("`").startswith("#"):\n'
        '            if not re.match(r"^[a-z0-9][\\w.-]*/[a-z0-9][\\w.-]*$", project or ""):\n'
        '                raise FieldError(key, "names an entry of this project: give it as \xabarea/project#AAAA-MM-DD\xbb")\n'
        '            v = project + v.lstrip("`").replace("`", "", 1) if v.startswith("`") else project + v\n'
        '        if v:\n'
        '            lines.append(f"{w[key]}: {v}")\n'
        '    affects = one_line(affects, "affects", required=False)\n'
        '    if affects:\n'
        '        lines.append(f"{w[\'affects\']}: {affects}")\n'
        '    return "\\n".join(lines)\n'
        '\n'
        '\n'
        'def status_block(date: str, headline: str, completed: str = "", next: str = "", to_decide: str = "",\n'
        '                 concern: str = "", pack: Pack = ES) -> str:\n'
        '    """The body of an Estatus block (escribir.md \xa73): the date and the bold sentence, then the lines that say\n'
        "    something. A project's first Estatus may carry only \xabSiguiente\xbb; a closed project's, only the sentence that starts\n"
        '    with the pack\'s finished marker."""\n'
        '    w = pack.write_status\n'
        '    headline = one_line(headline, "headline")\n'
        '    if headline.startswith("**") or headline.endswith("**"):\n'
        '        raise FieldError("headline", "is written without the asterisks: the writer puts them")\n'
        '    marker = re.compile(re.escape(pack.finished_marker), re.I)\n'
        '    closes = headline.startswith(pack.finished_marker)\n'
        '    if closes and not re.match(re.escape(pack.finished_marker) + r"\\s+20\\d\\d-\\d\\d-\\d\\d\\b", headline):\n'
        '        raise FieldError("headline", f"closes the project only with its date: \xab{pack.finished_marker} AAAA-MM-DD.\xbb")\n'
        '    if marker.search(headline[len(pack.finished_marker):] if closes else headline):\n'
        '        raise FieldError("headline", f"can say \xab{pack.finished_marker}\xbb only at its start: readers take it as closing the project")\n'
        '    lines = [f"{one_line(date, \'date\')} \xb7 **{headline}**"]\n'
        '    for key, value in (("completed", completed), ("next", next), ("to_decide", to_decide), ("concern", concern)):\n'
        '        v = one_line(value, key, required=False)\n'
        '        if marker.search(v):\n'
        '            raise FieldError(key, f"cannot say \xab{pack.finished_marker}\xbb: readers take it as closing the project")\n'
        '        if v:\n'
        '            lines.append(f"- **{w[key]}:** {v}")\n'
        '    if len(lines) == 1 and not closes:\n'
        '        raise FieldError("next", "is required, unless the headline closes the project (\xab" + pack.finished_marker + " \u2026\xbb)")\n'
        '    return "\\n".join(lines)\n'
    ),
    }
    for _n in _todo:
        _m = _t.ModuleType("context_core." + _n); _m.__package__ = "context_core"; _m.__fingerprint__ = _fp[_n]
        _s.modules[_m.__name__] = _m
        exec(compile(_src[_n], "<context_core/" + _n + ".py>", "exec"), _m.__dict__)
        setattr(_pkg, _n, _m)
_context_core()
# --- end of context_core ---
from context_core.compat import (registro_personas, fila_cuentas, puerta_de_escritura)  # noqa: E402
# los cambios sobre el texto viven en context_core.write desde la 1.25.5: el servidor escribe con las mismas funciones
from context_core.write import (with_header_today as cabecera_hoy, only_header_changed as solo_cabecera,  # noqa: E402
                                with_entry_on_top as con_entrada_arriba, without_block as sin_bloque, with_block)


def con_bloque(t, nombre, cuerpo, antes_de=None, alias=()):
    return with_block(t, nombre, cuerpo, before=antes_de, aliases=alias)
# --- fin de quién escribe ---


def zona_horaria(raiz, defecto="America/Mexico_City"):
    """La zona de la organización, como la lee abrir.py: la línea «Zona horaria:» de guia.md; si no, Ciudad de México."""
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


def celda_cuenta(raiz, area):
    """(responsables, colaboran) del área según la tabla de guia.md: la celda Cuenta hasta la 1.24, Responsable y
    Colabora por «Quién es quién» desde la 1.25."""
    try:
        guia = (raiz / "guia.md").read_text(encoding="utf-8-sig")
    except OSError:
        return set(), set()
    m = re.search(r"^##\s+Áreas\s*$(.*?)(?=^##\s|\Z)", guia, re.M | re.S)
    cab, reg = None, registro_personas(guia)
    for l in (m.group(1) if m else "").split("\n"):
        if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
            continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if cab is None:   # las columnas por su encabezado; sin él, la cuarta como Cuenta, como siempre
            cab = c; continue
        if c[0].strip("`").rstrip("/") == area:
            de, co, _ = fila_cuentas(cab, c, reg)
            return de, co
    return set(), set()


# ---------- leer y escribir ----------
def leer(p):
    with open(p, "rb") as f:
        b = f.read()
    st = os.stat(p)
    t = b.decode("utf-8-sig", errors="replace")
    crlf = "\r\n" in t
    return t.replace("\r\n", "\n"), (st.st_mtime_ns, st.st_size, hashlib.sha1(b).hexdigest()), crlf


def igual(p, firma):
    try:
        st = os.stat(p)
    except OSError:
        return False
    if (st.st_mtime_ns, st.st_size) != firma[:2]:
        return False
    with open(p, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest() == firma[2]


def escribir(p, texto, crlf):
    """Escribe en un temporal único al lado y lo pone en su sitio: nadie lee un archivo a medias."""
    if crlf:
        texto = texto.replace("\n", "\r\n")
    fd, tmp = tempfile.mkstemp(prefix="." + p.name + ".", suffix=".cerrar-tmp", dir=p.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(texto)
        os.replace(tmp, p)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return os.stat(p).st_mtime_ns


class Cerrojo:
    """Un cerrojo por archivo entre procesos de la misma computadora (en el /tmp que comparten las conversaciones)."""
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


# ---------- los cambios sobre el texto ----------
def con_reemplazos(t, reemplazos, sin_match, ruta):
    for r in reemplazos or []:
        de, a = r.get("de", ""), r.get("a", "")
        n = t.count(de) if de else 0
        if n != 1:
            sin_match.append({"ruta": ruta, "de": de[:120], "veces": n, "motivo": "no aparece exactamente una vez"}); continue
        if re.search(r"^## ", de, re.M) or de.count("\n") >= MAX_LINEAS_REEMPLAZO:
            sin_match.append({"ruta": ruta, "de": de[:120], "veces": n, "motivo": "cruza un encabezado o pasa de doce líneas: parte el reemplazo"}); continue
        t = t.replace(de, a)
    return t


def clave_cabecera(texto, clave):
    """El valor de una clave de la cabecera YAML, sin comillas; None si no está."""
    m = re.match(r"^---\n(.*?)\n---\n", texto.replace("\r\n", "\n"), re.S)
    if not m:
        return None
    v = re.search(r"^" + re.escape(clave) + r":[ \t]*(.*)$", m.group(1), re.M)
    if not v:
        return None
    v = v.group(1).strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1].replace('\\"', '"')
    return v or None


def sublineas_de(t, slug):
    """{nombre: línea} de los entregables que el bloque Proyectos ya lista debajo de un proyecto."""
    m = re.search(r"^## Proyectos\s*\n(.*?)(?=^## |\Z)", t, re.M | re.S)
    out, dentro = {}, False
    for l in (m.group(1) if m else "").split("\n"):
        if re.match(r"^- `" + re.escape(slug) + r"/?`", l):
            dentro = True; continue
        if dentro and l.startswith("  "):
            mm = re.match(r"^\s+-\s+([\w.-]+)", l)
            if mm:
                out[mm.group(1)] = l.rstrip()
            continue
        dentro = False
    return out


def lineas_entregables(pd, entregables, sin_match, rel, existentes):
    """Las líneas de los entregables para area.md: un texto se deja tal cual; {"archivo": "x.md"} se arma con la
    aportacion y la fecha de su cabecera (sección 2 de escribir.md: la línea es su aportacion). Si no se puede armar,
    se conserva la línea que ese entregable ya tenía: el índice nunca pierde una por un cierre."""
    fuera = []
    for e in entregables or []:
        if isinstance(e, str):
            fuera.append(e); continue
        nombre = str((e or {}).get("archivo", "")).replace("\\", "/").strip("/")
        nombre = nombre[len("entregables/"):] if nombre.startswith("entregables/") else nombre
        tallo = pathlib.PurePosixPath(nombre).stem if nombre else ""
        p = pd / "entregables" / nombre
        if not nombre or ".." in nombre.split("/") or not p.is_file():
            sin_match.append({"ruta": rel, "de": f"(entregable {nombre or '?'})", "veces": 0, "motivo": "no existe en entregables/" + ("; se conservó su línea de antes" if tallo in existentes else "")})
            if tallo in existentes:
                fuera.append(existentes[tallo])
            continue
        try:
            texto = p.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            texto = ""
        aporta = clave_cabecera(texto, "aportacion") or clave_cabecera(texto, "afirma")
        fecha = clave_cabecera(texto, "actualizado")
        if not aporta:
            sin_match.append({"ruta": rel, "de": f"(entregable {nombre})", "veces": 0, "motivo": "no tiene aportacion en la cabecera" + ("; se conservó su línea de antes" if tallo in existentes else ": pásale la línea escrita")})
            if tallo in existentes:
                fuera.append(existentes[tallo])
            continue
        fuera.append(f"  - {tallo} — {aporta}" + (f" · actualizado {fecha}" if fecha else ""))
    return fuera


def prioridades_viejas(t):
    """Las viñetas de «Prioridades ahora» (hasta la 1.21), para no perder ninguna al escribir el Estatus del área."""
    m = re.search(r"^## Prioridades ahora\s*\n(.*?)(?=^## |\Z)", t, re.M | re.S)
    out = []
    for l in (m.group(1) if m else "").split("\n"):
        x = l.strip()
        if re.match(r"^([-*]|\d+[.)])\s+", x):
            out.append(re.sub(r"^([-*]|\d+[.)])\s+", "", x))
        elif x and out:
            out[-1] += " " + x
    return [x for x in out if not x.startswith("[")]


def con_siguientes(estatus, nuevas):
    """Añade debajo de «Siguiente» las prioridades que el Estatus no trae (por su texto). Devuelve (texto, añadidas)."""
    faltan = [x for x in nuevas if x and x not in estatus]
    if not faltan:
        return estatus, []
    lineas = estatus.rstrip("\n").split("\n")
    idx = next((k for k, l in enumerate(lineas) if re.match(r"^\s*[-*]\s*\**\s*Siguiente\s*:?\s*\**\s*:?", l, re.I)), None)
    if idx is None:
        idx = next((k for k, l in enumerate(lineas) if re.match(r"^\s*[-*]\s*\**\s*Se completó", l, re.I)), 0)
        lineas[idx + 1:idx + 1] = ["- **Siguiente:**"]; idx += 1
    fin = idx + 1
    while fin < len(lineas) and re.match(r"^\s{2,}[-*]\s+", lineas[fin]):
        fin += 1
    lineas[fin:fin] = [f"  - {x}" for x in faltan]
    return "\n".join(lineas) + "\n", faltan


def con_linea_proyecto(t, slug, linea, entregables):
    """En el bloque Proyectos de area.md: la línea del proyecto y las de sus entregables, sin tocar las demás."""
    m = re.search(r"^## Proyectos\s*\n(.*?)(?=^## |\Z)", t, re.M | re.S)
    if not m:
        return t, False
    bloque = m.group(1).split("\n")
    nuevo = [linea.rstrip()] + [e.rstrip() for e in entregables or []]
    i = next((k for k, l in enumerate(bloque) if re.match(r"^- `" + re.escape(slug) + r"/?`", l)), None)
    if i is None:
        ultimo = max((k for k, l in enumerate(bloque) if l.startswith("- `") or l.startswith("  - ")), default=-1)
        bloque[ultimo + 1:ultimo + 1] = nuevo
    else:
        j = i + 1
        while j < len(bloque) and bloque[j].startswith("  "):
            j += 1
        bloque[i:j] = nuevo
    return t[:m.start(1)] + "\n".join(bloque) + t[m.end(1):], True


def rutas_documento(lista, pd, que, malos, publicar=False, otros_de=None):
    """Normaliza las rutas de «escribio» o «publico»: relativas al proyecto, dentro de entregables/ o taller/, existentes.
    Lo publicado, en entregables/ y con `estado: vigente`, mirado sobre el texto que dejarán los reemplazos de «otros» de
    esta misma llamada (publicar y cerrar en una sola llamada). Lo que no cumple va a «malos» y no se escribe nada."""
    if lista is None:
        return []
    if not isinstance(lista, list):
        malos.append(f"«{que}» va como lista de rutas"); return []
    fuera = []
    for r in lista:
        r = str(r or "").replace("\\", "/").strip().strip("/")
        partes = r.split("/")
        if not r or ".." in partes or partes[0] not in ("entregables", "taller") or len(partes) < 2:
            malos.append(f"«{que}» lleva «{r or '(vacío)'}»: va la ruta dentro del proyecto, en entregables/ o taller/"); continue
        if publicar and partes[0] != "entregables":
            malos.append(f"«{que}» lleva «{r}»: solo se publica lo de entregables/"); continue
        p = pd / r
        if not p.is_file():
            malos.append(f"«{que}» lleva «{r}», que no existe en el proyecto"); continue
        if publicar and r.endswith(".md"):
            try:
                texto_ = p.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
                texto_ = con_reemplazos(texto_, (otros_de or {}).get(r), [], r)
                estado = clave_cabecera(texto_, "estado")
            except (OSError, UnicodeDecodeError):
                estado = None
            if estado != "vigente":
                malos.append(f"«{que}» lleva «{r}», que no está vigente: lo publica la skill revisar antes de cerrar"); continue
        if r not in fuera:
            fuera.append(r)
    return fuera


def con_autoria(entrada, escribio, publico):
    """Pone «Escribió:» y «Publicó:» en la entrada, justo antes de «Sesión de:» (al final si no la tiene)."""
    extra = ([f"Escribió: {', '.join(escribio)}"] if escribio else []) + ([f"Publicó: {', '.join(publico)}"] if publico else [])
    if not extra:
        return entrada
    lineas = entrada.strip("\n").split("\n")
    i = next((k for k, l in enumerate(lineas) if re.match(r"^Sesi[oó]n de\s*:", l)), len(lineas))
    lineas[i:i] = extra
    return "\n".join(lineas)


def sin_nombrar(pd, abierto, nombrados):
    """Documentos de entregables/ y taller/ cambiados desde que se abrió la sesión y que no van en las listas."""
    out = []
    for sub in ("entregables", "taller"):
        base = pd / sub
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            rel = p.relative_to(pd).as_posix()
            if not p.is_file() or any(x.startswith(".") for x in rel.split("/")) or rel in nombrados:
                continue
            try:
                if p.stat().st_mtime > abierto:
                    out.append(rel)
            except OSError:
                pass
    return out


def motivo_rotacion(t, hoy, por_anio=True):
    """Por qué hay que archivar un registro antes de escribir en él, o None: pasa de 1.500 líneas o de 100 KB, o su entrada
    más nueva es de un año anterior al de hoy. Devuelve (motivo, año del archivado)."""
    anios = re.findall(r"^## (20\d\d)-\d\d-\d\d", t, re.M)
    if not anios:
        return None
    anio = max(anios)
    if t.count("\n") + 1 > LIMITE_LINEAS:
        return f"pasa de {LIMITE_LINEAS} líneas", anio
    if len(t.encode("utf-8")) > LIMITE_BYTES:
        return f"pasa de {LIMITE_BYTES // 1000} KB", anio
    if por_anio and anio < hoy[:4]:
        return "cambió el año", anio
    return None


def nombre_archivado(carpeta, nombre, anio):
    """«decisiones-2026.md»; si ya existe, «decisiones-2026-2.md», «-3»…"""
    k, n = 1, f"{nombre}-{anio}.md"
    while (carpeta / n).exists():
        k += 1; n = f"{nombre}-{anio}-{k}.md"
    return n


def entradas_de(t):
    """Las entradas «## …» de un registro, en orden, cada una con su texto sin los saltos del final."""
    return [x.rstrip("\n") for x in re.split(r"^(?=## )", t, flags=re.M) if x.startswith("## ")]


def archivados_en(carpeta, nombre):
    """Todos los archivados de un registro que hay en la carpeta, de más viejo a más nuevo (también los hechos a mano)."""
    vistos = []
    for x in carpeta.iterdir():
        m = re.match(r"^" + nombre + r"-(20\d\d)(?:-(\d+))?\.md$", x.name)
        if m:
            vistos.append((int(m.group(1)), int(m.group(2) or 1), x.name))
    return [n for *_, n in sorted(vistos)]


def registro_nuevo(t, nombre, archivado, hoy, carpeta):
    """El registro vivo recién abierto: su cabecera, su título y la línea «Archivado:» con todos sus archivados, de más
    viejo a más nuevo, para quien lo abra sin el plugin. Las entradas siguen en el archivado, con su identificador."""
    titulo_ = (re.search(r"^# .*$", t, re.M) or [f"# {nombre.capitalize()}"])[0]
    # los que nombraba la línea anterior (sin consola, la copia puede no tenerlos todos) y los que hay en la carpeta
    linea = (re.search(r"^Archivado:.*$", t, re.M) or [""])[0]
    clave = lambda n: tuple(int(x) for x in re.findall(r"\d+", n))
    todos = sorted(set(re.findall(r"\b(" + nombre + r"-20\d\d(?:-\d+)?\.md)", linea)) | set(archivados_en(carpeta, nombre)) | {archivado}, key=clave)
    return (f"---\nestado: vigente\nactualizado: {hoy}\n---\n{titulo_}\n\n"
            f"Archivado: {', '.join(todos)}. Las entradas anteriores están ahí y se citan igual, con su identificador.\n")


# ---------- un archivo ----------
class Cierre:
    def __init__(self, raiz, tz, abierto, sin_fechas, forzar):
        self.raiz, self.tz, self.abierto, self.sin_fechas, self.forzar = raiz, tz, abierto, sin_fechas, forzar
        self.hoy = datetime.datetime.now(tz).date().isoformat()
        self.salida = {"escritos": [], "sin_match": [], "rechazados": [], "fallidos": [], "ajenos": [], "reintentos": 0}
        self.vistos = set()
        # lo que este mismo cierre (u otra llamada suya en esta sesión) escribió, para no darlo por ajeno: el estado va
        # por raíz y por sesión (la hora de apertura), así otra sesión en la misma computadora no lo hereda
        h = hashlib.sha1(f"{raiz.resolve()}|{abierto}".encode()).hexdigest()[:16]
        self.estado = pathlib.Path(tempfile.gettempdir()) / f"memoria-cerrar-{h}.json"
        try:
            self.propios = json.loads(self.estado.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.propios = {}

    def rel(self, p):
        return p.relative_to(self.raiz).as_posix()

    def hora(self, ns):
        return datetime.datetime.fromtimestamp(ns / 1e9, self.tz).isoformat(timespec="minutes")

    def ajeno(self, rel, firma, durante=False):
        if self.sin_fechas or any(a["ruta"] == rel for a in self.salida["ajenos"]):
            return
        propio = self.propios.get(rel) == firma[0]
        if durante or (self.abierto and firma[0] / 1e9 > self.abierto and not propio):
            self.salida["ajenos"].append({"ruta": rel, "hora": self.hora(firma[0]), **({"durante": True} if durante else {})})

    def cambiar(self, p, f):
        """Lee, cambia con f y escribe solo si el archivo sigue igual que al leerlo; si no, repite sobre lo nuevo."""
        rel = self.rel(p)
        try:
            with Cerrojo(p):
                for intento in range(INTENTOS):
                    t, firma, crlf = leer(p)
                    if rel not in self.vistos:
                        self.ajeno(rel, firma)
                    elif intento:
                        self.ajeno(rel, firma, durante=True)
                    self.vistos.add(rel)
                    sin_match = []
                    nuevo, hubo = f(t, sin_match)
                    if not hubo or nuevo == t:
                        self.salida["sin_match"] += sin_match
                        return False
                    # un cambio que se queda dentro de la cabecera (añadir o corregir `aportacion`, por ejemplo) no mueve
                    # `actualizado`: la fecha dice cuándo cambió lo que el documento sostiene, no su cabecera (escribir.md, sección 5)
                    if not solo_cabecera(t, nuevo):
                        nuevo = cabecera_hoy(nuevo, self.hoy)
                    if len(nuevo) < len(t) / 2 and rel not in self.forzar:
                        self.salida["rechazados"].append({"ruta": rel, "motivo": f"encogería de {len(t)} a {len(nuevo)} caracteres; si es a propósito, --forzar {rel}"})
                        return False
                    if igual(p, firma):
                        ns = escribir(p, nuevo, crlf)
                        self.propios[rel] = ns
                        self.salida["sin_match"] += sin_match
                        self.salida["reintentos"] += intento
                        self.salida["escritos"].append(rel)
                        return True
                    time.sleep(0.05 * (intento + 1))
            self.salida["fallidos"].append({"ruta": rel, "motivo": "el archivo cambió cinco veces seguidas mientras se escribía"})
        except (OSError, UnicodeDecodeError) as ex:
            self.salida["fallidos"].append({"ruta": rel, "motivo": f"{type(ex).__name__}: {ex}"})
        return False

    def rotar(self, p, nombre, por_anio=True):
        """Archiva el registro antes de escribir en él si toca (escribir.md, sección 8): lo copia entero a «<nombre>-<año>.md»
        y deja el vivo con su cabecera, su título y la línea «Archivado:». Bajo el mismo cerrojo que las escrituras. Si ya
        hay un archivado idéntico (una rotación que no llegó a encoger el vivo), no lo duplica: solo encoge el vivo. Si el
        vivo cambia entre medias o no se puede escribir, el archivado recién creado se borra y no queda nada a medias."""
        rel = self.rel(p)
        try:
            # una mirada rápida, sin cerrojo: por el tamaño, y si es pequeño, su texto (que entonces cabe en 100 KB)
            if os.stat(p).st_size <= LIMITE_BYTES:
                with open(p, "rb") as f_:
                    if not motivo_rotacion(f_.read().decode("utf-8-sig", errors="replace"), self.hoy, por_anio):
                        return
            with Cerrojo(p):
                t, firma, crlf = leer(p)
                m = motivo_rotacion(t, self.hoy, por_anio)
                if not m:
                    return
                if rel not in self.vistos:
                    self.ajeno(rel, firma); self.vistos.add(rel)
                n_ent = len(re.findall(r"^## ", t, re.M))
                # el archivado lleva cabecera aunque el vivo no la tuviera: un archivado no se edita después
                # sin barras dentro de las llaves de un f-string: Python anterior a 3.12 no lo admite (1.23.1)
                mas_nueva = max(re.findall(r"^## (20\d\d-\d\d-\d\d)", t, re.M))
                arch_txt = t if re.match(r"^---\n", t) else f"---\nestado: vigente\nactualizado: {mas_nueva}\n---\n" + t
                # un archivado del mismo año cuyas entradas están todas en el vivo es una rotación que no llegó a encoger el
                # vivo (o se devolvió a medias y después alguien escribió): no se duplica, y el vivo se queda con lo que el
                # archivado no tiene (revisión de la 1.23, segunda vuelta)
                ents_vivo = entradas_de(t)
                igual_a = None
                for x in archivados_en(p.parent, nombre):
                    if not x.startswith(f"{nombre}-{m[1]}"):
                        continue
                    ea = entradas_de((p.parent / x).read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n"))
                    if ea and all(e in ents_vivo for e in ea):
                        igual_a, quedan = x, [e for e in ents_vivo if e not in ea]
                        break
                creado = None
                if igual_a:
                    arch = igual_a
                else:
                    arch = nombre_archivado(p.parent, nombre, m[1])
                    creado = p.parent / arch
                    fd = os.open(creado, os.O_WRONLY | os.O_CREAT | os.O_EXCL)   # nunca encima de un archivado que ya existe
                    with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
                        f.write(arch_txt.replace("\n", "\r\n") if crlf else arch_txt)
                try:
                    if not igual(p, firma):
                        raise OSError("el registro cambió mientras se archivaba; se archiva en el próximo cierre")
                    nuevo_vivo = registro_nuevo(t, nombre, arch, self.hoy, p.parent)
                    if igual_a and quedan:
                        nuevo_vivo = nuevo_vivo.rstrip("\n") + "\n\n" + "\n\n".join(quedan) + "\n"
                    self.propios[rel] = escribir(p, nuevo_vivo, crlf)
                except OSError:
                    if creado:
                        creado.unlink(missing_ok=True)
                    raise
                if creado:
                    self.propios[self.rel(creado)] = os.stat(creado).st_mtime_ns
                    self.salida["escritos"].append(self.rel(creado))
                self.salida["escritos"].append(rel)
                self.salida.setdefault("rotados", []).append({"de": rel, "a": self.rel(p.parent / arch), "motivo": m[0], "entradas": n_ent,
                                                             **({"ya_estaba": True} if igual_a else {})})
        except (OSError, UnicodeDecodeError) as ex:
            self.salida["fallidos"].append({"ruta": rel, "motivo": f"al archivar: {ex}"})

    def guardar_estado(self):
        try:
            self.estado.write_text(json.dumps(self.propios), encoding="utf-8")
        except OSError:
            pass


def limpiar_temporales(pd, pa):
    for d in (pd, pa):
        try:
            for x in d.iterdir():
                if x.name.endswith(".cerrar-tmp") and time.time() - x.stat().st_mtime > 60:
                    x.unlink()
        except OSError:
            pass


# ---------- main ----------
def main(argv):
    if len(argv) < 4:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    raiz, activo = pathlib.Path(argv[1]), argv[2].strip("/")
    opciones, args = {"--cuenta": None, "--abierto": None}, argv[4:]
    sin_fechas, forzar, fuera = "--sin-fechas" in args, set(), set()
    cualquier_fecha = "--cualquier-fecha" in args
    sin_rotar = "--sin-rotar" in args
    comprobar = "--comprobar" in args
    i = 0
    while i < len(args):
        a = args[i]
        if a in opciones and i + 1 < len(args):
            opciones[a] = args[i + 1]; i += 2
        elif a == "--forzar" and i + 1 < len(args):
            forzar.add(args[i + 1].strip("/")); i += 2
        elif a == "--fuera-del-area" and i + 1 < len(args):
            fuera.add(args[i + 1].strip("/")); i += 2
        elif a in ("--sin-fechas", "--cualquier-fecha", "--sin-rotar", "--comprobar"):
            i += 1
        else:
            print(f"No entiendo «{a}».", file=sys.stderr); return 2
    if "/" not in activo or not (raiz / "guia.md").is_file() or not (raiz / activo).is_dir():
        print("Uso: cerrar.py <raiz> <area>/<proyecto> <cambios.json>", file=sys.stderr); return 2
    try:
        cambios = json.loads(pathlib.Path(argv[3]).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as ex:
        print(f"No se pudo leer cambios.json: {ex}", file=sys.stderr); return 2
    tz = zona_horaria(raiz)
    abierto = None
    if opciones["--abierto"]:
        v = opciones["--abierto"].strip().replace("Z", "+00:00")
        try:
            dt = datetime.datetime.fromisoformat(v)
        except ValueError:
            print("--abierto va con la hora de la línea «ahora» de REGISTROS de abrir.py (ISO 8601)", file=sys.stderr); return 2
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
        abierto = dt.timestamp()
    area, slug = activo.split("/", 1)
    pd, pa = raiz / activo, raiz / area / "area.md"
    c = Cierre(raiz, tz, abierto, sin_fechas, forzar)
    s = c.salida

    # --- todo se comprueba antes de escribir nada ---
    # la versión mínima del plugin de la raíz (1.26): con un plugin anterior no se escribe nada, ni con --comprobar se da por bueno
    try:
        _guia = (raiz / "guia.md").read_text(encoding="utf-8-sig")
    except OSError as ex:
        print(json.dumps({"error": f"guia.md no se deja leer ({ex.strerror or ex}): no se escribe nada", **s}, ensure_ascii=False)); return 1
    _puede, _minima, _motivo = puerta_de_escritura(ESTE_PLUGIN, _guia)
    if not _puede:
        print(json.dumps({"error": _motivo, "solo_lectura": True, "version_minima": _minima, "plugin": ESTE_PLUGIN, **s}, ensure_ascii=False)); return 6
    malos = []
    ses = cambios.get("sesion")
    if ses and not re.match(r"^## \d{4}-\d{2}-\d{2}", ses.strip()):
        malos.append("«sesion» tiene que empezar por «## AAAA-MM-DD»")
    for d in cambios.get("decisiones") or []:
        if not re.match(r"^## \d{4}-\d{2}-\d{2} · \S", d.strip()):
            malos.append("cada decisión tiene que empezar por «## AAAA-MM-DD · Título»")
    # la fecha de cada entrada es la del día en la zona de la organización: hoy, o ayer si la sesión cruzó la medianoche
    if not malos and not cualquier_fecha:
        hoy = datetime.datetime.now(tz).date()
        validas = {hoy.isoformat(), (hoy - datetime.timedelta(days=1)).isoformat()}
        for que, e in [("«sesion»", ses)] + [("una decisión", d) for d in cambios.get("decisiones") or []]:
            if not e:
                continue
            f = e.strip()[3:13]
            if f not in validas:
                malos.append(f"{que} lleva la fecha {f} y hoy es {hoy.isoformat()} en {getattr(tz, 'key', tz)} (la línea HOY de abrir.py): "
                             "las fechas de la carpeta van en la zona de la organización, no en la del reloj de la consola o del contenedor; "
                             "si la fecha es a propósito, --cualquier-fecha")
    # lo nuevo se escribe con los nombres de la 1.22; los registros viejos no se tocan
    if ses and re.search(r"^(Trabajamos en|Pendiente)\s*:", ses, re.M):
        malos.append("«sesion» va con «Tema:» y sin «Pendiente:» (lo que sigue va en «Siguiente» del Estatus)")
    for d in cambios.get("decisiones") or []:
        if re.search(r"^Descartamos\s*:", d, re.M):
            malos.append("una decisión lleva «Descartado:», no «Descartamos:»")
    for que, e in (("«estatus»", (cambios.get("proyecto") or {}).get("estatus")), ("«estatus_area»", cambios.get("estatus_area"))):
        if e and not re.match(r"^\s*20\d\d-\d\d-\d\d\s*·\s*\*\*.+?\*\*", e.strip(), re.S):
            malos.append(f"{que} empieza por «AAAA-MM-DD · **frase**», como dice escribir.md")
    # los reemplazos de «otros» sobre documentos de este proyecto, por su ruta dentro de él: publicar (estado: vigente) y
    # cerrar pueden ir en la misma llamada
    otros_de = {}
    for o in cambios.get("otros") or []:
        r_ = str((o or {}).get("ruta", "")).replace("\\", "/").strip("/")
        if r_.startswith(activo + "/"):
            otros_de.setdefault(r_[len(activo) + 1:], []).extend(o.get("reemplazos") or [])
    escribio = rutas_documento(cambios.get("escribio"), pd, "escribio", malos)
    publico = rutas_documento(cambios.get("publico"), pd, "publico", malos, publicar=True, otros_de=otros_de)
    if (escribio or publico) and not ses:
        malos.append("«escribio» y «publico» van en la entrada de la sesión: hace falta «sesion»")
    # quién escribió y quién publicó solo los pone el script: una línea tecleada no se acepta, venga o no la lista
    if ses and re.search(r"^(Escribi[oó]|Public[oó])\s*:", ses, re.M):
        malos.append("«sesion» trae «Escribió:» o «Publicó:» escritos a mano: van solo en «escribio» y «publico», y los escribe el script")
    if ses and (escribio or publico) and not re.search(r"^Sesi[oó]n de\s*:\s*[^\s·]", ses, re.M):
        malos.append("con «escribio» o «publico», la entrada lleva «Sesión de: Nombre Apellido»: sin nombre no hay a quién atribuirlos")
    otros = []
    for o in cambios.get("otros") or []:
        r = str(o.get("ruta", "")).replace("\\", "/").strip("/")
        partes = r.split("/")
        dentro = r.startswith(area + "/")
        if not r or ".." in partes or r.startswith("/") or r in ("guia.md", "metodo.md") or partes[0] == "base" or "restringido" in partes:
            malos.append(f"«otros» no puede tocar {r or '(sin ruta)'}")
        elif not dentro and r not in fuera:
            s["rechazados"].append({"ruta": r, "motivo": "fuera del área del proyecto; solo con --fuera-del-area cuando una regla del área lo pide"})
        else:
            otros.append((r, o))
    if malos:
        print(json.dumps({"error": "; ".join(malos), **s}, ensure_ascii=False)); return 1
    if comprobar:
        # antes de enseñar la entrada: lo que se escribiría y lo que cambió desde la apertura sin nombrarse, sin escribir nada
        out = {"comprobado": True, **({"entrada": con_autoria(ses, escribio, publico)} if ses else {})}
        if abierto and not sin_fechas:
            out["sin_nombrar"] = sin_nombrar(pd, abierto, set(escribio) | set(publico))
        print(json.dumps(out, ensure_ascii=False)); return 0
    cuenta = (opciones["--cuenta"] or "").strip().lower()
    duenos, colaboran = celda_cuenta(raiz, area) if cuenta else (set(), set())
    puede_area = not cuenta or cuenta in duenos | colaboran
    puede_estatus_area = not cuenta or cuenta in duenos
    limpiar_temporales(pd, pa)

    # 9. la rotación, antes de escribir: un registro que pasa de 1.500 líneas o de 100 KB, o de otro año, se archiva y la
    # entrada de hoy abre el nuevo (1.23: antes la hacía la sesión a mano)
    # Se miran los dos registros en todo cierre que escribe en uno de ellos: un decisiones.md grande se archiva aunque hoy no
    # haya decisión (revisión de la 1.23, hallazgo 4)
    # Por el año, solo el registro en el que se escribe: archivar por año las únicas decisiones de un proyecto quieto en un
    # cierre sin decisión las sacaría de lo que se lee al año siguiente (revisión de la 1.23, segunda vuelta)
    if not sin_rotar and (ses or cambios.get("decisiones")):
        for nombre_, escribe in (("sesiones", bool(ses)), ("decisiones", bool(cambios.get("decisiones")))):
            if (pd / f"{nombre_}.md").is_file():
                c.rotar(pd / f"{nombre_}.md", nombre_, por_anio=escribe)
    # otros archivos del área, por reemplazos exactos. Van antes de la entrada de sesiones.md (1.24.2): al publicar y cerrar
    # en una llamada, el «estado: vigente» del documento se escribe primero, y si no se pudo, la entrada no dice «Publicó:»
    # de un borrador (revisión de la 1.23.0, segunda vuelta)
    for r, o in otros:
        p = raiz / r
        if not p.is_file():
            s["fallidos"].append({"ruta": r, "motivo": "no existe"}); continue
        def f_otro(t, sm, o=o, r=r):
            n = con_reemplazos(t, o.get("reemplazos"), sm, r)
            return n, n != t
        c.cambiar(p, f_otro)
    def _vigente_ya(r):
        if not r.endswith(".md"):
            return True
        try:
            return clave_cabecera((pd / r).read_text(encoding="utf-8-sig").replace("\r\n", "\n"), "estado") == "vigente"
        except (OSError, UnicodeDecodeError):
            return False
    # si algo de «publico» no quedó vigente, no se escribe nada más (ni la entrada, ni la línea del entregable en area.md):
    # se dice, se arregla lo de «otros» y se repite la misma llamada, que escribe la entrada entera una sola vez (1.24.2)
    _quedo_borrador = [x for x in publico if not _vigente_ya(x)]
    if _quedo_borrador:
        s["no_publicado"] = _quedo_borrador
        print(json.dumps({"error": "no quedó vigente lo que se publica: " + ", ".join(_quedo_borrador) + ". No se escribió la entrada ni lo demás; "
                          "arregla el reemplazo de «otros» (mira «sin_match» y «rechazados») y repite la llamada sin los reemplazos de «otros» "
                          "que ya se escribieron (los archivos de «escritos»)", **s}, ensure_ascii=False))
        return 1
    # 2. sesiones.md
    if ses:
        entrada = con_autoria(ses, escribio, publico)
        c.cambiar(pd / "sesiones.md", lambda t, sm: con_entrada_arriba(t, entrada))
    # 3. decisiones.md: de la más antigua a la más nueva, para que la última quede arriba
    if cambios.get("decisiones"):
        def f_dec(t, sm):
            hubo = False
            for d in cambios["decisiones"]:
                t, h = con_entrada_arriba(t, d); hubo = hubo or h
            return t, hubo
        c.cambiar(pd / "decisiones.md", f_dec)
    # 4. proyecto.md: Estatus entero (sustituye a «En corto» si la raíz no se migró) y reemplazos exactos en lo demás
    pr = cambios.get("proyecto") or {}
    estatus = pr.get("estatus")
    if estatus or pr.get("reemplazos"):
        def f_pro(t, sm):
            t0 = t
            t = con_reemplazos(t, pr.get("reemplazos"), sm, c.rel(pd / "proyecto.md"))
            if estatus:
                t = con_bloque(t, "Estatus", estatus, alias=("En corto",))
            return t, t != t0
        c.cambiar(pd / "proyecto.md", f_pro)
    # 5 y 10. area.md: la línea del proyecto (con las de sus entregables) y el Estatus del área
    ar = cambios.get("area") or {}
    if ar.get("linea") and not puede_area:
        s["rechazados"].append({"ruta": c.rel(pa), "motivo": f"la línea del proyecto en area.md la escribe el responsable del área o quien colabora en ella; {cuenta} no está en su fila de la tabla de áreas de guia.md: pásasela al responsable"})
        ar = {}
    est_area = cambios.get("estatus_area")
    if est_area and not puede_estatus_area:
        s["rechazados"].append({"ruta": c.rel(pa), "motivo": f"el Estatus del área lo escribe solo su responsable; {cuenta} no lo es"})
        est_area = None
    if ar.get("linea") or est_area:
        def f_area(t, sm):
            t0 = t
            if ar.get("linea"):
                existentes = sublineas_de(t, slug)
                lineas = lineas_entregables(pd, ar.get("entregables"), sm, c.rel(pa), existentes) if "entregables" in ar else list(existentes.values())
                t, ok = con_linea_proyecto(t, slug, ar["linea"], lineas)
                if not ok:
                    sm.append({"ruta": c.rel(pa), "de": "(bloque Proyectos)", "veces": 0, "motivo": "area.md no tiene bloque «## Proyectos»: la línea no se escribió"})
            if est_area:
                # las prioridades de un «Prioridades ahora» que el Estatus nuevo no traiga entran en «Siguiente»; después
                # se retiran «Panorama» y «Prioridades ahora»: desde la 1.22 el Estatus es la única sección de estatus
                est, fundidas = con_siguientes(est_area.strip() + "\n", prioridades_viejas(t))
                if fundidas:
                    s["fundidas"] = s.get("fundidas", []) + fundidas
                t = con_bloque(t, "Estatus", est, alias=("Panorama", "Prioridades ahora"))
            return t, t != t0
        c.cambiar(pa, f_area)
    c.guardar_estado()
    s["escritos"] = list(dict.fromkeys(s["escritos"]))   # un archivo, una vez, aunque lo escriban la rotación y la entrada
    if abierto and not sin_fechas:
        propios = {e[len(activo) + 1:] for e in s["escritos"] if e.startswith(activo + "/")}
        s["sin_nombrar"] = sin_nombrar(pd, abierto, set(escribio) | set(publico) | propios)
    ahora = datetime.datetime.now(datetime.timezone.utc)
    s["hora"] = ahora.strftime("%Y-%m-%dT%H:%MZ")
    s["documento"] = f"{area}--{slug}--{ahora.strftime('%Y%m%d%H%M')}"
    s["escrito_en"] = datetime.datetime.now(tz).isoformat(timespec="seconds")
    # «respuesta» va primero (1.25.1): lo que la conversación hace con esta salida, en el momento en que la lee, con la marca
    # del tablero ya armada; hasta la 1.25.0 ese paso vivía al final de cerrar.md y un cierre lo dejó sin hacer
    print(json.dumps({"respuesta": respuesta(s, raiz, pd, area, slug, cuenta, bool(ses), sin_fechas), **s}, ensure_ascii=False))
    return 0


def respuesta(s, raiz, pd, area, slug, cuenta, cierre, sin_fechas):
    """Qué hace la conversación con esta salida, en orden. Es un cierre solo si esta llamada escribió la entrada de la
    bitácora: entonces van la devolución (sin consola), lo pendiente (sin_match, rechazados, fallidos), la marca del tablero
    y el recuadro de cierre con su fila del tablero. Una llamada a mitad de sesión (solo reemplazos) no es un cierre: no deja
    marca ni dice «sesión cerrada». Los avisos de «ajenos» y «sin_nombrar» van en llano en los dos casos. Los textos de la
    carpeta no mandan aquí: solo se cita el título del proyecto, para la marca."""
    def titulo(p, defecto):
        try:
            texto = leer(p)[0]
        except OSError:
            return defecto
        m = re.search(r"^#\s+(.+)$", texto, re.M)
        return (m.group(1).split("·")[0].strip() if m else defecto) or defecto
    pasos = []
    llano = []
    for a in s.get("ajenos") or []:
        h = (a.get("hora") or "")[11:16]
        llano.append(f"alguien más escribió {a['ruta']} {'mientras cerrábamos' if a.get('durante') else 'a las ' + h}; sumé lo de hoy encima")
    for r in s.get("sin_nombrar") or []:
        llano.append(f"{r} cambió desde que abrimos y no lo escribió esta sesión")
    pendientes = [(k, txt) for k, txt in (("sin_match", "un reemplazo que no cuadró"), ("rechazados", "lo que esta cuenta no puede escribir"), ("fallidos", "un archivo que no se pudo escribir")) if s.get(k)]
    if not cierre:
        pasos.append("Esta llamada no cierra la sesión (no escribió la entrada de la bitácora): di en una línea qué quedó escrito, con el enlace computer:// de cada archivo de «escritos», y la sesión sigue abierta. Sin marca del tablero y sin recuadro de cierre.")
        for k, txt in pendientes:
            pasos.append(f"Hay «{k}» ({txt}): se resuelve como dice cerrar.md.")
        if llano:
            pasos.append("Además, en una línea cada uno: " + " · ".join(f"«{x}»" for x in llano) + ".")
        return pasos
    n = 1
    if sin_fechas:
        pasos.append(f"{n}. Primero devuelve los archivos a la computadora, como dice sin-consola-sesion.md: `espejo.py devolver` y device_commit_files; si uno vuelve por mtime-drift, se trae, se registra y se repite cerrar.py con el mismo cambios.json (una entrada que ya está no se repite). Solo con todos en «written» sigue lo de abajo."); n += 1
    for k, txt in pendientes:
        pasos.append(f"{n}. Hay «{k}» ({txt}): se resuelve como dice cerrar.md, repitiendo la llamada solo con eso y con --abierto escrito_en. Esa llamada no vuelve a pedir la marca (no lleva la entrada): la marca de abajo se escribe una vez, después de resolverlo."); n += 1
    nombre = titulo(pd / "proyecto.md", slug)
    org = titulo(raiz / "guia.md", "<organización>")
    marca = {"op": "set", "path": f"cierres/{s['documento']}",
             "data": {"proyecto": f"{area}--{slug}", "nombre": nombre, "hora": s["hora"], "cuenta": cuenta or ""}}
    pasos.append(
        f"{n}. La marca del tablero, antes de responder: la persona pidió cerrar la sesión y avisar al tablero es parte del cierre, así que se escribe sin preguntar. db_write del conector claude-artifacts (ToolSearch de mcp__claude-artifacts__db_write si no está cargada) "
        f"en el tablero de esta cuenta que se buscó al abrir, «Tablero {org}» (o «Tablero {org} completo», el nombre de antes de la 1.18; si no se buscó, list_artifacts ahora), con ops: "
        f"{json.dumps([marca], ensure_ascii=False)} (un documento nuevo: sin ifVersion). Con dos tableros de la raíz, en los dos. Sin el conector en esta conversación, o sin tablero, no se escribe nada y la fila de abajo lo dice."); n += 1
    pasos.append(
        f"{n}. El recuadro «Memoria · sesión cerrada · {len(s['escritos'])} archivo{'s' if len(s['escritos']) != 1 else ''}» (uno más si se juntó una copia en conflicto): una fila por archivo de «escritos» con su enlace computer:// y qué cambió, "
        "y una última fila para el tablero, siempre una de estas: «Tablero: avisado» (la marca se escribió), «Tablero: no se pudo avisar (<motivo en pocas palabras>): sincronízalo desde su botón o con «sincroniza el tablero»», "
        "«Tablero: sin el conector de artifacts en esta conversación: sincronízalo desde su botón», o «Tablero: esta cuenta no tiene» (list_artifacts no lo trae)."); n += 1
    if llano:
        pasos.append(f"{n}. Debajo del recuadro, en texto normal y en una línea cada uno: " + " · ".join(f"«{x}»" for x in llano) + "."); n += 1
    pasos.append(f"{n}. Debajo también, solo si hay algo, lo que dice «Qué respondo al terminar» de cerrar.md: qué queda para la próxima en una línea, a quién avisar de otra área por un «Afecta a:», lo que quedó en fuentes/ pendiente de decidir si es confidencial, y la revisión de permisos si el paso 10b lo pide. Nada más: el resumen largo ya está en los archivos.")
    return pasos


if __name__ == "__main__":
    sys.exit(main(sys.argv))
