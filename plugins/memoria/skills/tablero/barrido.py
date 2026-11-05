#!/usr/bin/env python3
"""El barrido de lo que las sesiones olvidaron: propuestas para la cola del tablero.

Corre dentro de la puesta al día del tablero (`regenerar.md`, paso 5f2), en el contenedor, sobre la copia que ya trae
solo lo que cambió desde la última vez, y no escribe en la carpeta: deja en <salida> lo que hay que subir a la
colección «cambios» del tablero, donde cada propuesta es un documento de tipo «propuesta». La memoria propone y solo
su responsable decide: una propuesta no cambia ningún archivo; la sesión que el responsable abre la enseña y el cierre escribe
lo que él acepta.

Uso:  barrido.py <copia> <salida> [--cola <volcado de «cambios»>] [--base <volcado de la base>] [--hoy AAAA-MM-DD] [--cuenta <correo>]
          con --base lee `juzgado` de su meta/estado: lo que el modelo ya vio en corridas anteriores y no dio propuesta
          (extractos que no eran decisión, piezas sin `afirma` que no se pudo decir, conjuntos ya contrastados) no se vuelve a pedir
          con --cuenta solo barre las áreas donde la cuenta es responsable o colabora (y los proyectos ajenos que la nombran en
          «Colabora:»): la memoria propone a quien puede escribir, y lo de otra área lo barre el tablero de su responsable.
          «hoy» es, si no se da, el `snapshot` de <salida>/meta/estado.json (el día en la zona de la organización, que
          el generador ya puso ahí) y, si tampoco está, el de esta máquina, que va en UTC: no es una fecha para escribir.
      barrido.py --cola-pendiente <volcado de «cambios»>   → imprime cuántos cambios de la cola NO son propuestas
      barrido.py --sumar-juicio <salida> <juicio.json> [--cola <volcado de «cambios»>]
          suma al barrido lo que el modelo juzgó: <juicio.json> es {"decisiones": [{"proyecto": "area--slug",
          "fecha": "AAAA-MM-DD", "decision": "una línea"}], "afirma": [{"ruta": "area/proyecto/entregables/x.md",
          "afirma": "una línea"}], "candidatos": [{"proyecto": "area--slug", "rutas": ["…", "…"], "entregable": "una línea"}],
          "contradicciones": [{"proyecto": "area--slug", "rutas": ["…", "…"], "texto": "una línea"}],
          "resumenes": [{"proyecto": "area--slug", "publicado": "una o dos frases", "taller": "una o dos frases"}]}, solo de lo que
          «para_juicio», «para_afirma», «para_contraste» y «para_resumen» pidieron (una lista sola vale como decisiones)

Detecta, con lo que está escrito y sin modelo:
  estado-desfasado  `proyecto.md` es más viejo que la última sesión que registra `sesiones.md`.
  paso-hecho        un paso de «Siguientes pasos» cuyas palabras casi todas están en «Avances:» de una de las dos últimas
                    sesiones: el registro parece darlo por hecho y el paso sigue ahí.
y deja para el modelo lo que solo un modelo puede decidir:
  para_juicio   las sesiones de los últimos días que cuentan una decisión («decidimos», «se acordó»…) cuando
                `decisiones.md` no tiene ninguna entrada de esa fecha.
  para_afirma   los entregables y los archivos del taller que no llevan `afirma:` (hasta 24 por corrida; primero los de
                los proyectos con sesiones más recientes y, en cada uno, entregables antes que taller y vigentes antes que borradores), con su título y, en los entregables, el arranque de su cuerpo,
                para que el modelo escriba la línea que dice qué sostienen. Del taller solo hay título y cabecera (la copia
                no trae su cuerpo, que es privado del área): si con eso no se puede decir qué sostiene, se salta.
  para_contraste los proyectos (hasta 5) con dos o más piezas con `afirma`, con esas líneas: el modelo dice qué piezas
                del taller podrían alimentar un entregable que no existe (candidatos) y qué dos piezas sostienen cosas
                incompatibles (contradicciones). Solo las líneas «afirma», nunca los cuerpos.
  para_resumen  los proyectos (hasta 6, y unos 12 KB) de todo lo que lee la cuenta cuyo «Qué hay» cambió desde su
                último resumen escrito, o que no tienen ninguno, y que no se pidieron ya con la misma huella: título,
                estado y aportación de cada pieza, para que el modelo escriba dos frases,
                lo publicado y lo que hay en el taller (1.22.4). Se guardan en <salida>/resumenes/, no en la cola: no
                cambian la carpeta, solo lo que enseña la pestaña.

Cada propuesta tiene un id estable (`prop-<clase>-<huella>`): la misma observación no se vuelve a proponer, una que
el responsable descartó (estado «descartada») no vuelve, y una que ya no es cierta (el responsable puso al día lo que decía) se
borra de la cola. Solo se toca lo de los proyectos que vienen en la copia; los demás se dejan como están.

Salida, en <salida>: `barrido.json` con «anadir» (id y archivo), «borrar» (id y if_version), «para_juicio» y
«proyectos» (los que se barrieron), y un `cambios/<id>.json` por propuesta nueva. Todo texto va en una sola línea.
"""
import sys, re, json, pathlib, hashlib, datetime, unicodedata

STOP = set("de la el los las un una y o en a al del para por con sin que se su sus lo le les es son como más ya no si este esta esto "
           "esos esas pero cuando donde sobre entre desde hasta hay ser fue han había solo todo todos cada otro otra muy también "
           "paso pasos hacer hecho hacer queda quedó falta".split())
STOP = {"".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c) != "Mn") for w in STOP}
MAX_AFIRMA = 24      # 1.22.3: el inventario necesita la línea de cada pieza; con 6 por corrida tardaba semanas
DATO_PERSONAL = re.compile(r"[\w.+'-]+@[\w-]+\.[\w.-]+|\b[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}\b|\b[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d\b|\b\d[\d .-]{9,}\d\b")
MAX_CONTRASTE = 5
BYTES_CONTRASTE = 12000   # 1.22.5: lo que pesan juntas sus piezas, como BYTES_RESUMEN
JUZGAR_MAX = 15000        # 1.22.5: lo que se imprime para juzgar; si pasa, va a juzgar.json y se imprime su ruta
MAX_RESUMEN = 6        # 1.22.4: los resúmenes de «Qué hay» que se piden por corrida, como mucho
BYTES_RESUMEN = 12000  # y lo que pesan juntas sus piezas: el tope es lo que entra al contexto del modelo
# la cola no crece sin tope (1.22.1, hallazgo 31 de la revisión de la 1.21): como mucho tantas propuestas pendientes por
# proyecto de las que se pueden volver a pedir (las mecánicas; las afirma, con su tope aparte), y una pendiente que una sesión posterior del
# proyecto dejó sin resolver durante tantos días se retira y queda juzgada, para que no vuelva igual
MAX_PENDIENTES = 8
# las «aportacion» pendientes llevan su propio tope (1.22.3): son muchas, se aceptan de golpe desde Qué hay y no deben
# quitarle hueco a lo mecánico
MAX_PENDIENTES_AFIRMA = 30
clave_pend = lambda proyecto, clase: f"{proyecto}|afirma" if clase == "afirma" else proyecto
CADUCIDAD_DIAS = 60
NIEGA = re.compile(r"\b(no|falta|faltan|pendiente|pendientes|sin|todav[ií]a|a[úu]n|hasta que|queda|quedan|sigue|siguen)\b", re.I)
DECIDIO = re.compile(r"\b(decidimos|decidí|decidieron|se decidi[óo]|se acord[óo]|acordamos|quedó acordado|quedó decidido|elegimos|se eligi[óo]|aprobamos|se aprob[óo]|descartamos|se descart[óo])\b", re.I)


def una_linea(s, tope=300):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= tope else s[:tope - 1].rstrip() + "…"


def leer(p):
    try:
        return p.read_text(encoding="utf-8-sig")
    except OSError:
        return ""


def cabecera(texto):
    m = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", texto, re.S)
    out = {}
    for l in (m.group(1).split("\n") if m else []):
        k, _, v = l.partition(":")
        if _:
            out[k.strip()] = v.strip().strip("'\"")
    return out


def seccion(texto, nombre):
    m = re.search(r"^## " + re.escape(nombre) + r"\s*\n(.*?)(?=^## |\Z)", texto, re.S | re.M)
    return m.group(1) if m else ""


def fecha_ok(f):
    try:
        datetime.date.fromisoformat(f)
        return bool(re.fullmatch(r"20\d\d-\d\d-\d\d", f))
    except ValueError:
        return False


def entradas(texto):
    """[(fecha, titulo, cuerpo)] de un registro, en el orden del archivo."""
    out, parts = [], re.split(r"^## (?=\d{4}-\d{2}-\d{2})", texto, flags=re.M)
    for p in parts[1:]:
        cab, _, cuerpo = p.partition("\n")
        f = cab[:10]
        if fecha_ok(f):
            out.append((f, cab, cuerpo))
    return out


def campo(cuerpo, nombre):
    m = re.search(r"^" + nombre + r":\s*(.*?)(?=^\w[\wñáéíóú ]*:|\Z)", cuerpo, re.S | re.M)
    return m.group(1).strip() if m else ""


def palabras(t):
    """Raíces de las palabras con contenido (cuatro letras, sin tildes): «mandar» y «mandó» cuentan como la misma."""
    sin = unicodedata.normalize("NFD", t.lower())
    sin = "".join(c for c in sin if unicodedata.category(c) != "Mn" or c == "\u0303")
    return {w[:4] for w in re.findall(r"[a-zñ]{4,}", sin) if w not in STOP}


def pasos_de(texto):
    out = []
    for l in seccion(texto, "Siguientes pasos").split("\n"):
        if re.match(r"^\s*[-*]\s+\S", l):
            out.append(re.sub(r"^\s*[-*]\s+", "", l).strip())
    return out


def huella(*partes):
    return hashlib.sha1("\x1f".join(partes).encode("utf-8")).hexdigest()[:10]


def id_juicio(clase, pid, clave):
    return f"prop-{clase}-{huella(pid, clave)}"


def cargar_cola(carpeta):
    docs = []
    if carpeta and pathlib.Path(carpeta).exists():
        for p in sorted(pathlib.Path(carpeta).rglob("*.json")):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if not isinstance(d, dict):
                continue
            data = d["data"] if isinstance(d.get("data"), dict) else d
            docs.append({"id": d.get("id") or d.get("doc_id") or p.stem, "version": d.get("version"), "data": data})
    return docs


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
# --- los registros con sus archivados ---
# Desde el paso 0 de la versión alojada, en context_core (metido con «quién escribe»); igual en abrir.py,
# generar_vista.py y barrido.py (pruebas/tablero/paridad.py).
from context_core.compat import ARCHIVADO, archivados_de, con_archivados, respuestas_viejas  # noqa: E402,F401
# --- fin de los registros ---


def areas_de_la_cuenta(copia, cuenta):
    """Las áreas donde la cuenta es responsable o colabora, por la tabla de áreas y «Quién es quién» de guia.md (como
    aplicar_cambios.py, por el encabezado desde la 1.25); None sin cuenta."""
    if not cuenta:
        return None
    guia = leer(copia / "guia.md")
    reg = registro_personas(guia)
    m = re.search(r"^## Áreas\s*\n(.*?)(?=^## |\Z)", guia, re.S | re.M)
    out, cab = set(), None
    for l in (m.group(1).split("\n") if m else []):
        if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
            continue
        celdas = [c.strip() for c in l.strip().strip("|").split("|")]
        if cab is None:
            cab = celdas; continue
        if len(celdas) >= 5:
            de, co, _ = fila_cuentas(cab, celdas, reg)
            if cuenta in de | co:
                out.add(celdas[0].strip("`").rstrip("/"))
    return out


def colabora_en(proy, cuenta):
    tp = leer(proy / "proyecto.md")
    m = re.search(r"^## Quién participa\s*\n(.*?)(?=^## |\Z)", tp, re.S | re.M)
    return bool(cuenta) and cuenta in colaboran_en(m.group(1) if m else "", registro_personas(leer(proy.parent.parent / "guia.md")))


def proyectos_de(copia, cuenta=None):
    """Los proyectos que el barrido mira: con --cuenta, solo los de las áreas donde es responsable o colabora, y los proyectos
    ajenos donde su «Colabora:» la nombra. La memoria propone a quien puede escribir; lo de otra área lo barre su responsable."""
    mias = areas_de_la_cuenta(copia, cuenta)
    for area in sorted(p for p in copia.iterdir() if p.is_dir() and (p / "area.md").exists()):
        for proy in sorted(p for p in area.iterdir() if p.is_dir() and (p / "proyecto.md").exists()):
            if mias is not None and area.name not in mias and not colabora_en(proy, cuenta):
                continue
            yield area.name, proy


def zona_de(salida):
    """La zona horaria que el generador dejó en <salida>/meta/estado.json, o la de México; `creado` se estampa con ella."""
    try:
        from zoneinfo import ZoneInfo
        m = json.loads((pathlib.Path(salida) / "meta" / "estado.json").read_text(encoding="utf-8"))
        m = m.get("data", m) if isinstance(m, dict) and "data" in m else m
        return ZoneInfo((m or {}).get("zona") or "America/Mexico_City")
    except Exception:
        return datetime.timezone(datetime.timedelta(hours=-6))


def ahora_en(salida):
    return datetime.datetime.now(zona_de(salida)).isoformat(timespec="minutes")


def juzgado_de(base):
    """Lo que el modelo ya juzgó sin hallazgo, guardado en meta/estado por plan_subida.py: {"ids": [...], "contraste": [...]}."""
    try:
        d = json.loads((pathlib.Path(base) / "meta" / "estado.json").read_text(encoding="utf-8")) if base else {}
        d = d.get("data", d) if isinstance(d, dict) and "data" in d else d
        j = (d or {}).get("juzgado") or {}
        return {"ids": set(j.get("ids") or []), "contraste": set(j.get("contraste") or []), "resumenes": set(j.get("resumenes") or [])}
    except (OSError, ValueError):
        return {"ids": set(), "contraste": set(), "resumenes": set()}


def id_contraste(pid, rutas):
    return id_juicio("contraste", pid, "contraste|" + "|".join(sorted(rutas)))


def piezas_de(salida, pid):
    """Las piezas de «Qué hay» que dejó el generador para el proyecto (entregables y taller, solo cabeceras), o []."""
    try:
        det = json.loads((salida / "detalle" / f"{pid}.json").read_text(encoding="utf-8"))
        return (det.get("que_hay") or {}).get("piezas") or []
    except (OSError, ValueError):
        return []


def barrer(copia, hoy, hay_propuesta=lambda i: False, salida=None, en_cola=lambda pid: [], cuenta=None, juzgado=None, lleno=frozenset(), recientes=None, hueco=None):
    juzgado = juzgado or {"ids": set(), "contraste": set()}
    visto = lambda i: hay_propuesta(i) or i in juzgado["ids"]      # ya propuesto, o ya juzgado sin hallazgo
    """(propuestas, para_juicio, para_afirma, para_contraste, vistos, ids de las propuestas de juicio que siguen siendo ciertas)."""
    props, juicio, afirma, contraste, vistos, validas = [], [], [], [], [], set()
    for area, proy in proyectos_de(copia, cuenta):
        pid = f"{area}--{proy.name}"
        vistos.append(pid)
        tp = leer(proy / "proyecto.md")
        ses_t, dec_t = leer(proy / "sesiones.md"), leer(proy / "decisiones.md")
        # lo que se compara lleva los archivados de este año y del anterior (1.23): una decisión registrada antes de archivar
        # sigue registrada; la rotación de abajo mira solo el registro vivo
        ses = entradas(con_archivados(proy, "sesiones", ses_t, hoy[:4], leer)[0])
        dec_todas = con_archivados(proy, "decisiones", dec_t, hoy[:4], leer)[0]
        reales = [e for e in ses if "(tarea)" not in e[1] and "(migracion)" not in e[1]]
        cerrado = any(re.search(r"Proyecto terminado el \d{4}-\d{2}-\d{2}", seccion(tp, n_)) for n_ in ("Estatus", "Estado actual", "En corto"))
        reciente = max((e[0] for e in reales if fecha_ok(e[0])), default="")      # la última sesión real: el tope de afirma va primero a lo activo
        if recientes is not None:
            recientes[pid] = reciente      # y la caducidad de la cola solo cuenta si hubo sesión después de proponer

        def prop(clase, clave, texto, por_que):
            props.append({"id": f"prop-{clase}-{huella(pid, clave)}", "data": {
                "tipo": "propuesta", "clase": clase, "proyecto": pid, "texto": una_linea(texto), "por_que": una_linea(por_que),
                "origen": "barrido", "estado": "pendiente"}})

        # estado desfasado
        act = cabecera(tp).get("actualizado", "")
        if reales and not cerrado and fecha_ok(act):
            ultima = max(e[0] for e in reales)
            if act < ultima:
                prop("estado-desfasado", f"{act}>{ultima}",
                     f"Poner al día «Estatus» y «Siguientes pasos»: son de {act} y la última sesión es de {ultima}.",
                     "proyecto.md es más viejo que la última entrada de sesiones.md")
        # pasos que el registro da por hechos: las palabras del paso están en una frase de Avances que no lo niega.
        # Se mira frase por frase, porque «revisamos la encuesta; falta mandarla» comparte las palabras del paso y dice lo contrario.
        if reales and not cerrado:
            for e in reales[:2]:
                frases = [f for f in re.split(r"[.;\n]+", campo(e[2], "Avances")) if f.strip()]
                if not frases:
                    continue
                for paso in pasos_de(tp):
                    pp = palabras(re.sub(r"\b20\d\d-\d\d-\d\d\b", " ", paso))
                    if len(pp) < 3:
                        continue
                    # la frase que coincide no lo niega, y la siguiente tampoco lo niega hablando de lo mismo («…; falta mandarla»)
                    hecho = any(len(pp & palabras(f)) >= 0.7 * len(pp) and not NIEGA.search(f)
                                and not (i + 1 < len(frases) and NIEGA.search(frases[i + 1]) and pp & palabras(frases[i + 1]))
                                for i, f in enumerate(frases))
                    if hecho:
                        # el id sale de las raíces del paso, no de su texto: fecharlo o retocarlo no lo convierte en otra observación
                        prop("paso-hecho", "|".join(sorted(pp)) + f"|{e[0]}",
                             f"Quitar de «Siguientes pasos»: «{una_linea(paso, 140)}». La sesión del {e[0]} parece darlo por hecho.",
                             f"sesiones.md ({e[0]}) lo cuenta en Avances")
        # la rotación ya no se propone: la hace cerrar.py en el próximo cierre, sin preguntar (revisión de la 1.23, hallazgo 4);
        # las propuestas «rotacion» que queden en la cola se borran solas, porque esta corrida no las vuelve a dar
        # decisiones que se cuentan en una sesión y no están registradas
        fechas_dec = {e[0] for e in entradas(dec_todas)}
        limite = (datetime.date.fromisoformat(hoy) - datetime.timedelta(days=14)).isoformat()
        # registrada el mismo día o el siguiente: el cierre acepta hoy o ayer, y una sesión que cruza la medianoche fecha la
        # bitácora un día y la decisión el otro
        registrada = lambda f: f in fechas_dec or (fecha_ok(f) and (datetime.date.fromisoformat(f) + datetime.timedelta(days=1)).isoformat() in fechas_dec)
        for e in reales:
            if not registrada(e[0]) and DECIDIO.search(" ".join(campo(e[2], k) for k in ("Tema", "Trabajamos en", "Avances"))):
                validas.add(id_juicio("decision-sin-registrar", pid, "decision|" + e[0]))      # sigue siendo cierta mientras no se registre
        for e in reales[:3]:
            if e[0] >= limite and not registrada(e[0]):
                texto = " ".join(campo(e[2], k) for k in ("Tema", "Trabajamos en", "Avances"))
                if DECIDIO.search(texto) and not visto(id_juicio("decision-sin-registrar", pid, "decision|" + e[0])):
                    juicio.append({"proyecto": pid, "fecha": e[0], "extracto": una_linea(texto, 600)})
        # entregables que no dicen qué sostienen (en un proyecto terminado ya no se pide: nadie lo va a abrir)
        for f in sorted((proy / "entregables").glob("*.md")) if (proy / "entregables").is_dir() and not cerrado else []:
            ft = leer(f)
            cab = cabecera(ft)
            if cab.get("estado") == "reemplazado" or cab.get("aportacion", "").strip() or cab.get("afirma", "").strip():
                continue
            ruta = f"{area}/{proy.name}/entregables/{f.name}"
            validas.add(id_juicio("afirma", pid, "afirma|" + ruta))
            if not visto(id_juicio("afirma", pid, "afirma|" + ruta)):
                cuerpo = re.sub(r"^---\s*\n.*?\n---\s*\n", "", ft, count=1, flags=re.S)
                titulo = next((l[2:].strip() for l in cuerpo.split("\n") if l.startswith("# ")), f.stem)
                arranque = " ".join(l.strip() for l in cuerpo.split("\n") if l.strip() and not l.startswith("#"))[:250]
                afirma.append({"proyecto": pid, "ruta": ruta, "titulo": una_linea(titulo, 120), "arranque": una_linea(arranque, 250), "_vigente": cab.get("estado") == "vigente", "_reciente": reciente})
        # el taller: sus cabeceras las dejó el generador en el detalle; su cuerpo no está en la copia ni se lee nunca
        piezas = piezas_de(salida, pid) if salida else []
        if not any(pz.get("tipo") == "taller" for pz in piezas):
            # sin inventario del taller (sin consola, o un detalle que no lo trae), lo que nombra «/taller/» ni se juzga ni se retira
            for d in en_cola(pid):
                if "/taller/" in json.dumps(d["data"].get("rutas") or d["data"].get("ruta") or ""):
                    validas.add(d["id"])
        rutas = set()
        con_afirma = []
        for pz in piezas:
            ruta = f"{area}/{proy.name}/{'entregables' if pz.get('tipo') == 'entregable' else 'taller'}/{pz.get('archivo', '')}"
            rutas.add(ruta)
            if pz.get("afirma") and pz.get("estado") != "reemplazado":
                con_afirma.append({"ruta": ruta, "estado": pz.get("estado"), "afirma": una_linea(pz["afirma"], 240)})
            if pz.get("tipo") != "taller" or not str(pz.get("archivo", "")).endswith(".md") or pz.get("estado") == "reemplazado" or pz.get("afirma"):
                continue
            validas.add(id_juicio("afirma", pid, "afirma|" + ruta))
            if not visto(id_juicio("afirma", pid, "afirma|" + ruta)):
                afirma.append({"proyecto": pid, "ruta": ruta, "titulo": una_linea(pz.get("titulo") or pz.get("nombre") or "", 120),
                               "arranque": None, "_vigente": pz.get("estado") == "vigente", "_taller": True, "_reciente": reciente})
        # candidatos a entregable y contradicciones: solo un modelo los ve, sobre las líneas «afirma» (nunca los cuerpos)
        # el contraste se pide una vez por conjunto de piezas: si ese conjunto ya se juzgó (con o sin hallazgo), no se repite
        if len(con_afirma) >= 2 and len(contraste) < MAX_CONTRASTE and id_contraste(pid, [x["ruta"] for x in con_afirma[:20]]) not in juzgado["contraste"]:
            item_ = {"proyecto": pid, "piezas": con_afirma[:20]}
            # con tope de bytes, como los resúmenes: es lo que entra al contexto del modelo (revisión 1.22.5)
            if sum(len(json.dumps(c, ensure_ascii=False).encode("utf-8")) for c in contraste + [item_]) <= BYTES_CONTRASTE:
                contraste.append(item_)
        # una propuesta de candidato o de contradicción sigue valiendo mientras existan todas las piezas que nombra
        for d in en_cola(pid):
            if d["data"].get("clase") in ("candidato-entregable", "contradiccion") and set(d["data"].get("rutas") or []) <= rutas and d["data"].get("rutas"):
                validas.add(d["id"])
    # el tope de MAX_AFIRMA, primero para los proyectos con sesiones más recientes (1.22.1: la primera puesta al día real
    # dio las seis a un solo proyecto por orden alfabético); dentro de cada uno, entregables antes que taller y vigentes antes
    afirma = [x for x in afirma if x["proyecto"] not in lleno]      # un proyecto ya al tope no recibe más: el modelo no lo juzga en balde
    afirma.sort(key=lambda x: x["ruta"])
    afirma.sort(key=lambda x: (x.get("_taller", False), not x["_vigente"]))
    afirma.sort(key=lambda x: x.get("_reciente") or "", reverse=True)
    # y a cada proyecto, como mucho los huecos que le quedan en la cola (1.22.3): lo que el tope tiraría no se juzga en balde
    usados, cabe = {}, []
    for x in afirma:
        lim = (hueco or {}).get(x["proyecto"], MAX_PENDIENTES_AFIRMA)
        if usados.get(x["proyecto"], 0) < lim:
            usados[x["proyecto"]] = usados.get(x["proyecto"], 0) + 1; cabe.append(x)
    afirma = [{k: v for k, v in x.items() if k not in ("_vigente", "_taller", "_reciente")} for x in cabe[:MAX_AFIRMA]]
    return props, juicio, afirma, contraste, vistos, validas


def sumar_juicio(salida, juicio, cola):
    """Convierte lo que el modelo juzgó en propuestas, sin dejarle escribir documentos de la cola: solo cuenta lo que el
    barrido pidió juzgar (mismo proyecto y misma fecha, o la misma ruta), con una línea de texto; lo ya propuesto no se repite."""
    bar = json.loads((salida / "barrido.json").read_text(encoding="utf-8"))
    if isinstance(juicio, list):
        juicio = {"decisiones": juicio}
    # todo lo que se puso delante del modelo queda juzgado, haya hallazgo o no: no se vuelve a pedir (plan_subida lo lleva a meta/estado)
    # las caducadas que el barrido ya dejó juzgadas se conservan; se parte siempre de lo que dejó el barrido, no de una pasada
    # anterior de --sumar-juicio, para que correrlo dos veces dé lo mismo (revisión 1.22.5)
    if "juzgado_inicial" not in bar:
        bar["juzgado_inicial"] = bar.get("juzgado") or {}
    previo = bar["juzgado_inicial"]
    bar["juzgado"] = {"ids": sorted(set(previo.get("ids") or [])
                                    | {id_juicio("decision-sin-registrar", j["proyecto"], "decision|" + j["fecha"]) for j in bar.get("para_juicio", [])}
                                    | {id_juicio("afirma", j["proyecto"], "afirma|" + j["ruta"]) for j in bar.get("para_afirma", [])}),
                      "contraste": sorted(set(previo.get("contraste") or []) | {id_contraste(c["proyecto"], [x["ruta"] for x in c["piezas"]]) for c in bar.get("para_contraste", [])}),
                      # un resumen pedido no se vuelve a pedir con la misma huella, aunque el modelo lo saltara (revisión 1.22.4)
                      "resumenes": sorted(set(previo.get("resumenes") or []) | {f"{r['proyecto']}|{r['huella']}" for r in bar.get("para_resumen", [])})}
    # solo se guardan las huellas vigentes: la de otro «Qué hay» ya no frena nada y haría crecer meta/estado
    _vig = {f"{p_.stem}|{(_datos_doc(p_) or {}).get('que_hay_huella')}" for p_ in (salida / "proyectos").glob("*.json")} if (salida / "proyectos").exists() else set()
    if _vig:
        bar["juzgado"]["resumenes"] = [x for x in bar["juzgado"]["resumenes"] if x.removesuffix("|reintento") in _vig]
    pedido = {(j["proyecto"], j["fecha"]) for j in bar.get("para_juicio", [])}
    pedido_afirma = {j["ruta"]: j["proyecto"] for j in bar.get("para_afirma", [])}
    titulo_de = {j["ruta"]: j.get("titulo") or "" for j in bar.get("para_afirma", [])}
    pedido_contraste = {c["proyecto"]: {x["ruta"] for x in c["piezas"]} for c in bar.get("para_contraste", [])}
    ya = {d["id"] for d in cargar_cola(cola) if d["data"].get("tipo") == "propuesta"} | {x["id"] for x in bar["anadir"]}
    ahora = ahora_en(salida)
    nuevas = {"decisiones": 0, "afirma": 0, "candidatos": 0, "contradicciones": 0}
    pendientes = dict(bar.get("pendientes") or {})      # las que el barrido dejó por proyecto, contando las suyas
    sin_hueco = set()

    def guardar(pid, data):
        # el tope solo frena lo que se puede volver a pedir sin perder nada (una línea aportacion); una decisión sin
        # registrar, un candidato o una contradicción entran siempre: son pocos y se piden una vez por conjunto
        k = clave_pend(data["proyecto"], data["clase"])
        if data["clase"] == "afirma" and pendientes.get(k, 0) >= MAX_PENDIENTES_AFIRMA:
            sin_hueco.add(pid)      # no entra, y se volverá a pedir cuando el proyecto tenga hueco
            return False
        pendientes[k] = pendientes.get(k, 0) + 1
        (salida / "cambios").mkdir(parents=True, exist_ok=True)
        (salida / "cambios" / f"{pid}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        bar["anadir"].append({"id": pid, "archivo": f"cambios/{pid}.json"}); ya.add(pid)
        return True

    for j in juicio.get("decisiones", []) if isinstance(juicio.get("decisiones"), list) else []:
        if not isinstance(j, dict) or (j.get("proyecto"), j.get("fecha")) not in pedido:
            continue
        dec = una_linea(str(j.get("decision") or ""), 200)
        pid = id_juicio("decision-sin-registrar", j["proyecto"], "decision|" + j["fecha"])
        if not dec or pid in ya:
            continue
        ok_ = guardar(pid, {"tipo": "propuesta", "clase": "decision-sin-registrar", "proyecto": j["proyecto"],
                      "texto": una_linea(f"Registrar en decisiones.md lo que la sesión del {j['fecha']} cuenta como decidido: {dec}"),
                      "por_que": "sesiones.md la narra y decisiones.md no tiene entrada de esa fecha", "origen": "barrido",
                      "estado": "pendiente", "creado": ahora})
        if ok_:
            nuevas["decisiones"] += 1
    for j in juicio.get("afirma", []) if isinstance(juicio.get("afirma"), list) else []:
        if not isinstance(j, dict) or j.get("ruta") not in pedido_afirma:
            continue
        linea = una_linea(str(j.get("afirma") or "").replace('"', "'"), 200)
        if DATO_PERSONAL.search(linea):
            continue      # un correo, un RFC o CURP, una cuenta o un número largo no van a una línea que lee todo el que lee el área
        proy = pedido_afirma[j["ruta"]]
        pid = id_juicio("afirma", proy, "afirma|" + j["ruta"])
        if not linea or pid in ya:
            continue
        # en lenguaje llano, con el título del documento: es lo que enseñan la apertura y el tablero (1.22.5)
        tit = titulo_de.get(j["ruta"]) or j["ruta"].rsplit("/", 1)[-1].removesuffix(".md").replace("-", " ")
        ok_ = guardar(pid, {"tipo": "propuesta", "clase": "afirma", "proyecto": proy, "ruta": j["ruta"], "afirma": linea, "titulo": tit,
                      "texto": una_linea(f"Frase de resumen para «{tit}»: «{linea}»"),
                      "por_que": "sale en el tablero bajo el nombre del documento, para saber de qué trata sin abrirlo", "origen": "barrido",
                      "estado": "pendiente", "creado": ahora})
        if ok_:
            nuevas["afirma"] += 1
    for clase, clave, campo_txt, cabeza, por_que in (
            ("candidato-entregable", "candidatos", "entregable", "Candidato a entregable", "varias piezas del taller sostienen lo mismo y ningún entregable lo recoge"),
            ("contradiccion", "contradicciones", "texto", "Contradicción", "dos piezas del proyecto sostienen cosas que no pueden ser ciertas a la vez")):
        for j in juicio.get(clave, []) if isinstance(juicio.get(clave), list) else []:
            if not isinstance(j, dict) or j.get("proyecto") not in pedido_contraste:
                continue
            rutas = sorted({str(r) for r in (j.get("rutas") or []) if isinstance(r, str)})
            if len(rutas) < 2 or not set(rutas) <= pedido_contraste[j["proyecto"]]:
                continue      # solo piezas que el barrido puso delante, y al menos dos
            linea = una_linea(str(j.get(campo_txt) or ""), 200)
            pid = id_juicio(clase, j["proyecto"], clase + "|" + "|".join(rutas))
            if not linea or pid in ya:
                continue
            cortas = ", ".join(r.split("/", 2)[-1] for r in rutas)
            ok_ = guardar(pid, {"tipo": "propuesta", "clase": clase, "proyecto": j["proyecto"], "rutas": rutas,
                          "texto": una_linea(f"{cabeza}: {linea} (de {cortas})"), "por_que": por_que, "origen": "barrido",
                          "estado": "pendiente", "creado": ahora})
            if ok_:
                nuevas[clave] += 1
    # los resúmenes de «Qué hay» (1.22.4): no son propuestas; van a <salida>/resumenes/ y al índice, para que la subida los lleve
    pedido_resumen = {r["proyecto"]: r["huella"] for r in bar.get("para_resumen", [])}
    n_res, rechazados = 0, []
    for j in juicio.get("resumenes", []) if isinstance(juicio.get("resumenes"), list) else []:
        if not isinstance(j, dict) or j.get("proyecto") not in pedido_resumen:
            continue
        ent, tal = una_linea(str(j.get("publicado") or ""), 320), una_linea(str(j.get("taller") or ""), 320)
        if not (ent or tal) or DATO_PERSONAL.search(ent + " " + tal):
            rechazados.append(f"{j['proyecto']}: {'vacío' if not (ent or tal) else 'parece llevar un dato personal'}")
            # uno rechazado por el filtro se vuelve a pedir una vez en la siguiente corrida; si vuelve a fallar, espera a que
            # cambie lo que hay (revisión 1.22.4, segunda vuelta)
            if ent or tal:
                clave_ = f"{j['proyecto']}|{pedido_resumen[j['proyecto']]}"
                if clave_ + "|reintento" not in (previo.get("resumenes") or []):
                    bar["juzgado"]["resumenes"] = [x for x in bar["juzgado"]["resumenes"] if x != clave_] + [clave_ + "|reintento"]
            continue
        doc = {"proyecto": j["proyecto"], "ent": ent, "tal": tal, "huella_qh": pedido_resumen[j["proyecto"]], "fecha": str(ahora)[:10]}
        doc["huella"] = hashlib.sha1(json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]
        (salida / "resumenes").mkdir(parents=True, exist_ok=True)
        ruta = salida / "resumenes" / f"{j['proyecto']}.json"
        ruta.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        ind_p = salida / "indice.json"
        try:
            ind = json.loads(ind_p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            ind = None
        if isinstance(ind, list):
            ind = [x for x in ind if not (x.get("coleccion") == "resumenes" and x.get("doc_id") == j["proyecto"])]
            ind.append({"coleccion": "resumenes", "doc_id": j["proyecto"], "archivo": f"resumenes/{j['proyecto']}.json", "huella": doc["huella"], "bytes": ruta.stat().st_size})
            ind_p.write_text(json.dumps(ind, ensure_ascii=False, indent=1), encoding="utf-8")
        n_res += 1
    bar["juzgado"]["ids"] = [i for i in bar["juzgado"]["ids"] if i not in sin_hueco]
    (salida / "barrido.json").write_text(json.dumps(bar, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"sin_hueco": len(sin_hueco), "propuestas_nuevas_por_juicio": nuevas["decisiones"], "propuestas_afirma": nuevas["afirma"],
                      "propuestas_candidatos": nuevas["candidatos"], "propuestas_contradicciones": nuevas["contradicciones"], "resumenes": n_res, "resumenes_rechazados": rechazados}, ensure_ascii=False))


def _datos_doc(p):
    try:
        d = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return d.get("data", d) if isinstance(d, dict) else None


def para_resumen(salida, base, vistos, juz=None):
    """Los proyectos cuyo «Qué hay» necesita un resumen escrito: todo lo que la cuenta lee, menos lo restringido y lo cerrado
    (el resumen solo usa títulos y aportaciones, que ya lee). Lo pedido queda juzgado con su huella y no se vuelve a pedir
    hasta que cambie, haya salido o no (revisión 1.22.4, hallazgo 4), salvo uno que el filtro de datos personales rechazó,
    que se pide una vez más (1.22.5). Van primero dos de los que nunca tuvieron resumen y después los que cambiaron; uno que
    no cabe en BYTES_RESUMEN se salta y se prueba el siguiente; tope de MAX_RESUMEN proyectos."""
    ya = (juz or {}).get("resumenes") or set()
    cambiados, nunca = [], []
    docs = sorted((salida / "proyectos").glob("*.json")) if (salida / "proyectos").exists() else []
    for p_ in docs:
        pd = _datos_doc(p_) or {}
        h = pd.get("que_hay_huella")
        if not h or pd.get("restringido") or pd.get("cerrado") or f"{p_.stem}|{h}" in ya:
            continue
        previo = _datos_doc(pathlib.Path(base) / "resumenes" / f"{p_.stem}.json") if base else None
        if previo and previo.get("huella_qh") == h:
            continue
        det = _datos_doc(salida / "detalle" / f"{p_.stem}.json") or {}
        qh = det.get("que_hay") if isinstance(det.get("que_hay"), dict) else pd.get("que_hay") if isinstance(pd.get("que_hay"), dict) else {}
        piezas = qh.get("piezas") or []
        if not piezas:
            continue
        item = {"proyecto": p_.stem, "huella": h, "nombre": pd.get("nombre") or p_.stem,
                "piezas": [{k: v for k, v in {"tipo": z.get("tipo"), "titulo": una_linea(z.get("titulo") or z.get("nombre") or "", 120),
                                              "estado": z.get("estado"), "aportacion": una_linea(z.get("afirma") or "", 220)}.items() if v}
                           for z in piezas[:30]]}
        (cambiados if p_.stem in vistos or previo else nunca).append(item)
    # los dos huecos de los que nunca tuvieron resumen van primero, para que los que cambiaron no llenen antes los bytes; uno
    # que no cabe se salta y se prueba con el siguiente (revisión 1.22.4, segunda vuelta)
    orden = nunca[:2] + cambiados[:MAX_RESUMEN - 2]
    orden += [x for x in cambiados + nunca if x not in orden]
    out, peso = [], 0
    for x in orden:
        b = len(json.dumps(x, ensure_ascii=False).encode("utf-8"))
        if len(out) >= MAX_RESUMEN:
            break
        if peso + b > BYTES_RESUMEN:
            continue
        out.append(x); peso += b
    return out


def main():
    a = sys.argv[1:]
    if a and a[0] == "--sumar-juicio":
        opt = lambda n: a[a.index(n) + 1] if n in a and len(a) > a.index(n) + 1 else None
        sumar_juicio(pathlib.Path(a[1]), json.loads(pathlib.Path(a[2]).read_text(encoding="utf-8")), opt("--cola"))
        return
    if a and a[0] == "--cola-pendiente":
        docs = cargar_cola(a[1] if len(a) > 1 else None)
        print(sum(1 for d in docs if d["data"].get("tipo") != "propuesta"))
        return
    if len(a) < 2:
        sys.exit(__doc__)
    copia, salida = pathlib.Path(a[0]), pathlib.Path(a[1])
    opt = lambda n: a[a.index(n) + 1] if n in a and len(a) > a.index(n) + 1 else None
    hoy = opt("--hoy")
    if not hoy:
        try:
            m = json.loads((salida / "meta" / "estado.json").read_text(encoding="utf-8"))
            hoy = (m.get("data", m) if isinstance(m, dict) else {}).get("snapshot")
        except (OSError, ValueError):
            hoy = None
        hoy = hoy or datetime.date.today().isoformat()
    if not fecha_ok(hoy):
        sys.exit("--hoy no es una fecha AAAA-MM-DD")
    todas = [d for d in cargar_cola(opt("--cola")) if d["data"].get("tipo") == "propuesta"]
    # una propuesta que un cierre ya aplicó (1.24.1: su marca en la base dice «aplicada») se retira sin más
    aplicadas = [d for d in todas if d["data"].get("estado") == "aplicada"]
    existentes = [d for d in todas if d["data"].get("estado") != "aplicada"]
    ya = {d["id"]: d for d in todas}
    por_proyecto = {}
    for d in existentes:
        por_proyecto.setdefault(d["data"].get("proyecto"), []).append(d)
    juz = juzgado_de(opt("--base"))
    previas = {}
    for d in existentes:
        # las aceptadas ya no esperan juicio: no ocupan hueco en la cola (1.22.3)
        if d["data"].get("estado") not in ("descartada", "aceptada"):
            k = clave_pend(d["data"].get("proyecto"), d["data"].get("clase"))
            previas[k] = previas.get(k, 0) + 1
    recientes = {}
    props, juicio, afirma, contraste, vistos, validas = barrer(copia, hoy, lambda i: i in ya, salida, lambda pid: por_proyecto.get(pid, []),
                                                              (opt("--cuenta") or "").strip().lower() or None, juz,
                                                              lleno={k[:-7] for k, v in previas.items() if k.endswith("|afirma") and v >= MAX_PENDIENTES_AFIRMA}, recientes=recientes,
                                                              hueco={k[:-7]: max(0, MAX_PENDIENTES_AFIRMA - v) for k, v in previas.items() if k.endswith("|afirma")})
    nuevos_ids = {p["id"] for p in props} | validas      # las de juicio siguen valiendo mientras lo mecánico lo diga
    ahora = ahora_en(salida)
    # caduca una pendiente de hace más de CADUCIDAD_DIAS si su proyecto tuvo después una sesión real que no la resolvió
    # (la sesión la enseña al abrir): se retira y queda juzgada, para que no vuelva igual. Una que nadie pudo ver, porque
    # su proyecto no tuvo sesión, no caduca; una aceptada desde el tablero tampoco (1.22.3): la espera el próximo cierre.
    lim = (datetime.date.fromisoformat(hoy) - datetime.timedelta(days=CADUCIDAD_DIAS)).isoformat()
    caducadas = {d["id"] for d in existentes if d["data"].get("estado") not in ("descartada", "aceptada") and fecha_ok(str(d["data"].get("creado") or "")[:10])
                 and str(d["data"]["creado"])[:10] < lim and recientes.get(d["data"].get("proyecto"), "") > str(d["data"]["creado"])[:10]}
    pendientes = {}
    for d in existentes:
        if d["data"].get("estado") not in ("descartada", "aceptada") and d["id"] not in caducadas and (d["data"].get("proyecto") not in vistos or d["id"] in nuevos_ids):
            k = clave_pend(d["data"].get("proyecto"), d["data"].get("clase"))
            pendientes[k] = pendientes.get(k, 0) + 1
    (salida / "cambios").mkdir(parents=True, exist_ok=True)
    anadir, sin_hueco = [], 0
    for p in props:
        if p["id"] in ya or p["id"] in juz["ids"]:
            continue            # ya está (pendiente o descartada), o caducó sin que nadie la resolviera: no se vuelve a proponer
        k = clave_pend(p["data"]["proyecto"], p["data"].get("clase"))
        if pendientes.get(k, 0) >= MAX_PENDIENTES:
            sin_hueco += 1; continue      # el proyecto ya tiene bastantes pendientes: entra cuando se resuelvan
        pendientes[k] = pendientes.get(k, 0) + 1
        p["data"]["creado"] = ahora
        (salida / "cambios" / f"{p['id']}.json").write_text(json.dumps(p["data"], ensure_ascii=False), encoding="utf-8")
        anadir.append({"id": p["id"], "archivo": f"cambios/{p['id']}.json"})
    borrar = [{"id": d["id"], "if_version": d["version"]} for d in aplicadas]
    for d in existentes:
        # una aceptada desde el tablero la espera el cierre, aunque lo mecánico deje de proponerla (1.22.3). Solo se retira la
        # aceptada de «aportacion» cuya pieza ya la tiene (la escribió el cierre o alguien a mano): ya no hay nada que aplicar
        if d["data"].get("estado") == "aceptada":
            # «rotacion» ya no existe desde la 1.23 (la hace el cierre): se retira aunque esté aceptada, que nadie la aplicará
            if (d["data"].get("clase") == "afirma" and d["data"].get("proyecto") in vistos and d["id"] not in nuevos_ids) or d["data"].get("clase") == "rotacion":
                borrar.append({"id": d["id"], "if_version": d["version"]})
            continue
        if (d["data"].get("proyecto") in vistos and d["id"] not in nuevos_ids) or d["id"] in caducadas:
            borrar.append({"id": d["id"], "if_version": d["version"]})
    resumen = para_resumen(salida, opt("--base"), set(vistos), juz)
    (salida / "barrido.json").write_text(json.dumps(
        {"anadir": anadir, "borrar": borrar, "para_juicio": juicio, "para_afirma": afirma, "para_contraste": contraste, "para_resumen": resumen, "proyectos": vistos,
         "pendientes": pendientes, "juzgado": {"ids": sorted(caducadas), "contraste": [], "resumenes": sorted(x for x in juz["resumenes"] if x.endswith("|reintento"))}}, ensure_ascii=False, indent=1), encoding="utf-8")
    cuenta = {"propuestas_nuevas": len(anadir), "propuestas_que_ya_no_valen": len(borrar), "caducadas": len(caducadas), "sin_hueco": sin_hueco, "para_juicio": len(juicio),
              "para_afirma": len(afirma), "para_contraste": len(contraste), "para_resumen": len(resumen), "proyectos_barridos": len(vistos)}
    # lo que el modelo tiene que juzgar viaja en la misma salida: no hace falta leer barrido.json (revisión 1.22.4, hallazgo 20)
    juzgar = {k: v for k, v in (("para_juicio", juicio), ("para_afirma", afirma), ("para_contraste", contraste), ("para_resumen", resumen)) if v}
    if juzgar:
        # si no cabe en la salida que ve el modelo, va a un archivo pequeño, solo con eso, y se imprime su ruta (revisión 1.22.5)
        txt_ = json.dumps(juzgar, ensure_ascii=False)
        if len(txt_) <= JUZGAR_MAX:
            cuenta["juzgar"] = juzgar
        else:
            (salida / "juzgar.json").write_text(txt_, encoding="utf-8")
            cuenta["juzgar_en"] = str(salida / "juzgar.json")
    print(json.dumps(cuenta, ensure_ascii=False))


if __name__ == "__main__":
    main()
