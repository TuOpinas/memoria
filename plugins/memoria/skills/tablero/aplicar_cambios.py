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
import sys, re, json, pathlib, datetime

RAIZ = pathlib.Path(sys.argv[1])
ENTRADA = pathlib.Path(sys.argv[2])
DRY = "--dry-run" in sys.argv
CUENTA = (sys.argv[sys.argv.index("--cuenta") + 1] if "--cuenta" in sys.argv and len(sys.argv) > sys.argv.index("--cuenta") + 1 else "").strip().lower()

# --- quién escribe: «Quién es quién» y la tabla de áreas de guia.md, y la línea «Colabora:» de un proyecto ---
# La misma función en abrir.py, cerrar.py, permisos.py, migrar_estructura.py, aplicar_cambios.py, barrido.py,
# generar_vista.py y verificar.sh (cada uno se descarga suelto); pruebas/sesion/probar_cuentas.py comprueba que las
# ocho copias son idénticas. Desde la 1.25 cada persona está una vez en «Quién es quién» («Nombre · cuenta@») y la tabla
# de áreas la nombra por su nombre en Responsable y Colabora; hasta la 1.24, la celda Cuenta llevaba los correos. Se
# leen las dos formas: con registro y columna Colabora, por nombre; sin ellos, la celda Cuenta como siempre. Todo falla
# cerrado: un nombre o una cuenta que no se resuelve sin duda no da escritura a nadie.
import unicodedata
CORREO = re.compile(r"[\w.+'-]+@[\w-]+(?:\.[\w-]+)*")
PALABRA_COLABORA = re.compile(r"\bco-?labor\w*\s*:?", re.I)
LINEA_COLABORA = re.compile(r"^\s*[-*]?\s*\**\s*colabora[n]?\s*\**\s*:", re.I)
def cuentas(celda):
    """(responsable, colaboran, aviso) de una celda Cuenta: «resp@x · colabora: a@x, b@x». Falla cerrado:
    con más de un correo antes de la palabra, o ninguno, nadie es responsable; cualquier palabra que empiece por
    «colabor» separa, para que «colaboradora:» o «colabora» sin dos puntos no conviertan a nadie en responsable."""
    texto = (celda or "").lower()
    partes = PALABRA_COLABORA.split(texto, maxsplit=1)
    antes = set(CORREO.findall(partes[0]))
    despues = set(CORREO.findall(partes[1])) if len(partes) > 1 else set()
    aviso = None
    if len(antes) > 1:
        aviso = "más de un correo antes de «colabora:»; nadie es responsable hasta que se corrija"
        antes = set()
    elif not antes:
        aviso = "sin el correo del responsable"
    elif len(partes) > 1 and not re.search(r"\bcolabora\s*:", texto):
        aviso = "la palabra para quien colabora va escrita «colabora:»"
    return antes, despues, aviso
def clave_nombre(n):
    """Cómo se comparan dos nombres: NFC (Mac y Windows escriben las tildes distinto), sin mayúsculas, sin negritas,
    comillas ni lo que va entre paréntesis, y con los espacios juntos. Nada más: sin tilde no es el mismo nombre."""
    n = unicodedata.normalize("NFC", n or "").replace(" ", " ")
    n = re.sub(r"\s*\([^)]*\)", "", re.sub(r"[*_`«»\"]", "", n))
    return re.sub(r"\s+", " ", n).strip(" .,;:").lower()
def _titulo(t):
    """Un encabezado para compararlo: sin tildes (en NFC o NFD), sin mayúsculas ni signos."""
    t = "".join(c for c in unicodedata.normalize("NFD", t or "") if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", "", t.lower())).strip()
def registro_personas(guia):
    """«Quién es quién» de guia.md: {"hay", "personas", "nombre": {clave: persona}, "cuenta": {correo: persona}, "avisos"}.
    Una línea es «- Nombre · campo · campo» (el «·» con espacios a los lados); los campos: un correo (su cuenta de Claude),
    «cuentas: a@, b@», «en Drive: x@», «sin cuenta», «sin confirmar», «también: Otra Grafía», «de: Organización»,
    «baja AAAA-MM-DD», «compartida con: Nombre» y «registra: Nombre». «?» como nombre es una cuenta que todavía no tiene
    nombre. Quien está de baja no escribe; un nombre o una cuenta que está en dos líneas no es de nadie."""
    lineas, dentro, hay = [], False, False
    for l in unicodedata.normalize("NFC", guia or "").split("\n"):
        m = re.match(r"^\s*#{2,3}\s+(.*?)\s*$", l)
        if m:
            dentro = _titulo(m.group(1)) == "quien es quien"
            hay = hay or dentro
        elif dentro:
            lineas.append(l)
    reg = {"hay": hay, "personas": [], "nombre": {}, "cuenta": {}, "avisos": []}
    dos_nombres, dos_cuentas = set(), set()
    for l in lineas:
        if not re.match(r"^\s*[-*]\s+\S", l):
            continue
        campos = [c.strip() for c in re.split(r"\s+·\s+", l.strip()[1:].strip()) if c.strip()]
        if not campos:
            continue
        p = {"nombre": re.sub(r"\s*\([^)]*\)", "", re.sub(r"[*_`]", "", campos[0])).strip(), "cuentas": set(), "drive": set(),
             "sin_cuenta": False, "sin_confirmar": False, "alias": [], "de": "", "baja": "", "compartida": "", "registra": ""}
        if CORREO.fullmatch(p["nombre"].lower()):
            p["cuentas"].add(p["nombre"].lower()); p["nombre"] = "?"
        elif CORREO.search(p["nombre"]):
            reg["avisos"].append(f"«{campos[0]}»: el nombre y la cuenta van separados por « · »")
        for c in campos[1:]:
            cl = c.lower()
            if CORREO.fullmatch(cl):
                p["cuentas"].add(cl)
            elif re.search(r"\bbaja\b", cl):
                p["baja"] = (re.search(r"20\d\d-\d\d-\d\d", c) or [""])[0] or "sí"
            elif re.match(r"^cuentas?\s*:", cl):
                p["cuentas"] |= set(CORREO.findall(cl))
            elif re.match(r"^(en\s+)?(google\s+)?drive\s*:", cl):
                p["drive"] |= set(CORREO.findall(cl))
            elif re.match(r"^sin\s+cuenta\b", cl):
                p["sin_cuenta"] = True
            elif re.match(r"^sin\s+confirmar\b", cl):
                p["sin_confirmar"] = True
            elif re.match(r"^tambi[eé]n\s*:", cl):
                p["alias"] += [a.strip() for a in re.split(r"[,;]", c.split(":", 1)[1]) if a.strip()]
            elif re.match(r"^de\s*:", cl):
                p["de"] = c.split(":", 1)[1].strip()
            elif re.match(r"^compartida\s+con\s*:", cl):
                p["compartida"] = c.split(":", 1)[1].strip()
            elif re.match(r"^registra\s*:", cl):
                p["registra"] = c.split(":", 1)[1].strip()
            else:
                reg["avisos"].append(f"«{p['nombre']}»: no se entiende «{c}» (van un correo, «sin cuenta», «en Drive: correo», «también: nombre», «de: organización» o «baja AAAA-MM-DD»)")
        if p["sin_cuenta"] and p["cuentas"]:
            reg["avisos"].append(f"«{p['nombre']}» dice «sin cuenta» y lleva una cuenta: se queda la cuenta")
            p["sin_cuenta"] = False
        if not p["cuentas"] and not p["sin_cuenta"] and not p["baja"]:
            reg["avisos"].append(f"«{p['nombre']}» no lleva ni su cuenta ni «sin cuenta»")
        reg["personas"].append(p)
        for n in ([p["nombre"]] if p["nombre"] != "?" else []) + p["alias"]:
            k = clave_nombre(n)
            if k in reg["nombre"] and reg["nombre"][k] is not p:
                dos_nombres.add(k)
                reg["avisos"].append(f"«{n}» está dos veces: dos personas con el mismo nombre se distinguen con el segundo apellido o una inicial (mientras, ese nombre no es de nadie)")
            reg["nombre"].setdefault(k, p)
        for c in p["cuentas"]:
            if c in reg["cuenta"] and reg["cuenta"][c] is not p:
                dos_cuentas.add(c)
                reg["avisos"].append(f"la cuenta {c} está en dos líneas («{reg['cuenta'][c]['nombre']}» y «{p['nombre']}»; mientras, no es de nadie)")
            reg["cuenta"].setdefault(c, p)
    for k in dos_nombres:
        reg["nombre"].pop(k, None)
    for c in dos_cuentas:
        reg["cuenta"].pop(c, None)
    return reg
def persona(nombre, reg):
    """La persona del registro con ese nombre, alias o cuenta; None si no está o es ambiguo."""
    t = (nombre or "").strip()
    if CORREO.fullmatch(t.lower()):
        return (reg or {}).get("cuenta", {}).get(t.lower())
    return (reg or {}).get("nombre", {}).get(clave_nombre(t))
def nombres_de(texto, reg=None):
    """Los nombres de una celda o una línea («Colabora: Ana Ruiz, Luis Mejía»): sin la etiqueta del principio ni lo que va
    entre paréntesis, separados por comas o «;». Un tramo que no es un nombre del registro se parte además por « y » o
    « e », así que «José Ortega y Gasset» se queda entero si así está declarado."""
    t = re.sub(r"^\s*[-*]?\s*\**\s*(?:colabora[n]?|lo leen?|responsable)\s*\**\s*:\s*\**", "", texto or "", flags=re.I)
    t = re.sub(r"\s*\([^)]*\)", "", t)
    out = []
    for tramo in re.split(r"[,;]", t):
        tramo = tramo.strip(" .*")
        if not tramo or tramo.lower() in ("—", "-", "nadie", "ninguno", "ninguna"):
            continue
        if persona(tramo, reg) is not None or not re.search(r"\s(?:y|e)\s", tramo):
            out.append(tramo)
        else:
            out += [x.strip(" .*") for x in re.split(r"\s+(?:y|e)\s+", tramo) if x.strip(" .*")]
    return out
def cuentas_de_nombres(texto, reg):
    """(cuentas, nombres que no están en el registro) de una celda con nombres. Un correo suelto cuenta solo si es de una
    persona del registro; quien está de baja o sin cuenta no da ninguna."""
    out, faltan = set(), []
    for n in nombres_de(texto, reg):
        p = persona(n, reg)
        if p is None:
            faltan.append(n)
        elif not p["baja"]:
            out |= p["cuentas"]
    return out, faltan
def altas_provisionales(quien, reg):
    """[(nombre, correo)] de las líneas «Colabora:» de un proyecto con «Nombre (correo)» de alguien que no está en el
    registro: el alta provisional (1.25). Solo con registro; sin él, «Nombre (correo)» es la forma de siempre."""
    out = []
    if not (reg or {}).get("hay"):
        return out
    for l in (quien or "").split("\n"):
        if LINEA_COLABORA.match(l):
            for n, c in re.findall(r"([^,;(:]+?)\s*\(\s*(" + CORREO.pattern + r")\s*\)", l):
                n = n.strip(" .*")
                if persona(n, reg) is None and c.lower() not in reg["cuenta"]:
                    out.append((n, c.lower()))
    return out
def columnas_personas(cab):
    """Dónde están Responsable, Cuenta y Colabora en el encabezado de la tabla de áreas (None si no están)."""
    n = [_titulo(x) for x in cab]
    pos = lambda *ns: next((i for i, x in enumerate(n) if x in ns), None)
    return {"responsable": pos("responsable", "dueno", "duena"), "cuenta": pos("cuenta", "cuentas"),
            "colabora": pos("colabora", "colaboran", "colaboradores", "colaboradoras")}
def fila_cuentas(cab, celdas, reg):
    """(responsable, colaboran, aviso) de una fila de la tabla de áreas, como cuentas(): con la columna Cuenta (hasta la
    1.24), de sus correos; con la columna Colabora y «Quién es quién» (1.25), por los nombres. Sin encabezado reconocible,
    la cuarta columna como Cuenta, como siempre. Falla cerrado: un responsable que no está en el registro no es nadie."""
    col = columnas_personas(cab)
    celda = lambda i: celdas[i] if i is not None and i < len(celdas) else ""
    if col["cuenta"] is not None or col["colabora"] is None:
        return cuentas(celda(col["cuenta"] if col["cuenta"] is not None else 3))
    if not (reg or {}).get("hay"):
        return set(), set(), "la tabla nombra a quien colabora por su nombre y guia.md no tiene «Quién es quién»"
    resp = re.sub(r"\s*\((?=[a-záéíóúñ`])[^)]*\)", "", celda(col["responsable"] if col["responsable"] is not None else 2))
    rn = nombres_de(resp, reg)
    avisos, de = [], set()
    if len(rn) > 1 and persona(rn[0], reg) is not None:
        avisos.append(f"en Responsable, lo que sigue a «{rn[0]}» va en «Qué es»")
        rn = rn[:1]
    if len(rn) != 1:
        avisos.append("el responsable es una sola persona del registro" if rn else "sin responsable")
    else:
        p = persona(rn[0], reg)
        if p is None:
            avisos.append(f"«{rn[0]}» no está en «Quién es quién»")
        elif p["baja"]:
            avisos.append(f"«{p['nombre']}» está de baja")
        elif p["cuentas"]:
            de = set(p["cuentas"])
        elif p["registra"] and persona(p["registra"], reg) and persona(p["registra"], reg)["cuentas"]:
            de = set(persona(p["registra"], reg)["cuentas"])
        else:
            avisos.append(f"«{p['nombre']}» no tiene cuenta: o la tiene, o su línea dice «registra: Nombre» de quien escribe por ella")
    co, faltan = cuentas_de_nombres(celda(col["colabora"]), reg)
    avisos += [f"«{n}» (Colabora) no está en «Quién es quién»" for n in faltan]
    return de, co - de, "; ".join(avisos) or None
def nombre_contexto(linea):
    """El nombre de «Contexto común: Nombre», sin la cuenta entre paréntesis ni lo que sigue a una coma, un punto o una raya."""
    t = re.sub(r"\s*\([^)]*\)", "", (linea or "").split(":", 1)[-1])
    return re.split(r",|\.\s|\.$|\s[—–-]\s|;", t.strip())[0].strip()
def cuentas_contexto(linea, reg):
    """Las cuentas de quien responde por el contexto: la que va entre paréntesis en «Contexto común: Nombre (correo)»
    (hasta la 1.24) o la del registro para ese nombre (1.25)."""
    c = set(CORREO.findall((linea or "").split(":", 1)[-1].lower()))
    if c:
        return c
    p = persona(nombre_contexto(linea), reg)
    return set(p["cuentas"]) if p and not p["baja"] else set()
def nombre_de(cuenta, reg):
    """El nombre del registro de esa cuenta, o "" si no está (o es «?»)."""
    p = (reg or {}).get("cuenta", {}).get((cuenta or "").lower())
    return p["nombre"] if p and p["nombre"] != "?" else ""
def colaboran_en(quien, reg=None):
    """Las cuentas de las líneas «Colabora:» de «Quién participa» de un proyecto (todas las líneas). Sin registro, los
    correos escritos tal cual; con él, las de los nombres, y el correo entre paréntesis solo en un alta provisional."""
    out = set()
    for l in (quien or "").split("\n"):
        if LINEA_COLABORA.match(l):
            if (reg or {}).get("hay"):
                out |= cuentas_de_nombres(l, reg)[0] | {c for _, c in altas_provisionales(l, reg)}
            else:
                out |= set(CORREO.findall(l.lower()))
    return out
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
