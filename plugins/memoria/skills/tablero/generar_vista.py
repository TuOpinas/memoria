#!/usr/bin/env python3
"""Genera los documentos de la Vista a partir de una raíz del método Memoria.

Lee solo la superficie pública: guia.md, cada area.md y, de cada proyecto,
proyecto.md, decisiones.md, sesiones.md y las cabeceras de entregables/.
Nunca abre fuentes/, taller/, restringido/ ni base/ (salvo base/premisas.md, que es de toda la organización): de fuentes/ y taller/ solo mira las fechas
de modificación, para el aviso de trabajo sin sesión.

Uso: generar_vista.py <raiz> <carpeta-de-salida> [--tarea <id de la tarea programada que regenera la vista>] [--manual] [--version <versión del plugin que lo ejecuta>]
--manual: la tarea no tiene horario y solo corre desde el botón «Sincronizar ahora»
La carpeta de salida va fuera de la raíz (es derivada y se regenera entera); nunca dentro de la carpeta de la organización.

En dos tiempos, cuando la raíz está en otra computadora y el resultado tiene que llegar a Claude sin pasar por la conversación:
  1. En la computadora:  generar_vista.py <raiz> --inventario
     Imprime un JSON con «leer» (las rutas, relativas a la raíz, de los archivos que hay que traer) e «inventario» (lo poco
     que el generador necesita y no está dentro de esos archivos: fechas de modificación, lo que no se pudo leer, la lista
     de proyectos y las carpetas sueltas). No escribe nada.
  2. Donde se tenga la copia de esos archivos, con su misma estructura:
     generar_vista.py <copia> <carpeta-de-salida> --desde-inventario <inventario.json> [--tarea …] [--version …]
     Comprueba que la copia trae exactamente los archivos de «leer» y genera lo mismo que el modo de un tiempo en la computadora.

Sin consola en la computadora (la raíz no se monta en su shell), el inventario corre en el contenedor sobre una copia completa
de la superficie pública que arma espejo.py, con --sin-fechas: las fechas de archivo de una copia son las de la copia, así que
no se usan. Las huellas miran el contenido en lugar de la fecha, y no hay aviso de trabajo sin sesión ni fechas de archivo.

Un solo modo desde la 1.18: todo lo que la cuenta pueda leer, con las cinco sesiones más recientes enteras; lo que no
puede leer sale como restringido, con su nombre y su dueño. El tablero es de su dueño y no se comparte. --modo se acepta
y no se usa: las tareas montadas antes de la 1.18 lo pasan, con «publico» o «completo».
Escribe un JSON por documento: meta/estado.json, areas/<slug>.json,
proyectos/<area>--<slug>.json, cada uno con una huella de su contenido; un indice.json con la lista de archivos, huellas y
tamaños; y meta/enfoque-candidatos.json, que no va a la base: lo usa la puesta al día para «Por dónde empezar».
"""
import sys, os, re, json, datetime, pathlib, hashlib, unicodedata

# --- quién escribe: la celda Cuenta de guia.md y la línea «Colabora:» de un proyecto ---
# La misma función en abrir.py, aplicar_cambios.py, generar_vista.py y verificar.sh (cada uno se descarga suelto);
# pruebas/sesion/probar_cuentas.py comprueba que las cuatro copias son idénticas.
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
def colaboran_en(quien):
    """Las cuentas de las líneas «Colabora:» de «Quién participa» de un proyecto (todas las líneas)."""
    return set(c for l in (quien or "").split("\n") if LINEA_COLABORA.match(l) for c in CORREO.findall(l.lower()))
# --- fin de quién escribe ---
RAIZ = pathlib.Path(sys.argv[1])
ZONA_AVISO = None
def zona_horaria(raiz, defecto="America/Mexico_City"):
    """La zona de la organización: la línea «Zona horaria: Europe/Madrid» de guia.md (con viñeta, negrita o comillas
    invertidas, y UTC o Etc/GMT+5), si la hay; si no, Ciudad de México. Una zona que no vale se avisa en ZONA_AVISO."""
    global ZONA_AVISO
    try:
        m = re.search(r"^\s*[-*]?\s*\**\s*zona horaria\s*\**\s*:\s*\**\s*`?\s*([A-Za-z0-9_+-]+(?:/[A-Za-z0-9_+-]+){0,2})", (raiz / "guia.md").read_text(encoding="utf-8-sig"), re.M | re.I)
    except OSError:
        m = None
    try:
        from zoneinfo import ZoneInfo
    except Exception:
        return None
    if m and not m.group(1).startswith("["):
        try:
            return ZoneInfo(m.group(1))
        except Exception:
            ZONA_AVISO = f"la zona horaria «{m.group(1)}» de guia.md no es una zona válida (por ejemplo America/Mexico_City o Europe/Madrid); se usa {defecto}"
    try:
        return ZoneInfo(defecto)
    except Exception:
        return None
TZ = zona_horaria(RAIZ) or datetime.timezone.utc
def _arg(nombre):
    return sys.argv[sys.argv.index(nombre) + 1] if nombre in sys.argv and len(sys.argv) > sys.argv.index(nombre) + 1 else None
# --cuenta <correo>: la cuenta que genera el tablero. Si la carpeta de un área suya (dueña o colabora) no está en la
# computadora, no es que esté restringida para ella: aún no se creó o no se sincronizó (1.18.2)
CUENTA_TABLERO = (_arg("--cuenta") or "").strip().lower()
# Lo restringido se declara con la palabra al inicio: de la columna «Quién la lee» de guia.md, y de la línea del
# proyecto en el bloque Proyectos de su área, con o sin marcas delante («**restringido**:»). Mismo criterio que abrir.py.
RE_RESTRINGIDA = re.compile(r"^[\W_]*restringid[oa]\b", re.I)
def restringida_celda(celda):
    """«Quién la lee» declara el área restringida: la palabra al inicio («Restringida: …», «Restringido a …»), o
    «restringida» como palabra suelta en otra parte de la celda («Dirección (restringida)») sin negarla («nunca
    restringida», «antes restringida»). «Los proyectos restringidos aparte» no la declara. Igual en abrir.py,
    generar_vista.py y vista.html (restringidaCelda)."""
    c = celda or ""
    if re.match(r"^[\W_]*restringid[oa]s?\b", c, re.I):
        return True
    return bool(re.search(r"\brestringidas?\b", c, re.I)) and not re.search(r"\b(?:nada|no|nunca|sin|antes)\s+(?:[^\s]+\s+)?restringid", c, re.I)

def sin_palabra_restringido(linea):
    """La línea sin la palabra que la declara: «**restringido**: márgenes» → «márgenes»."""
    return re.sub(r"^[\W_]*restringid[oa]\b[*_»\"”'’\s]*[:—–,-]?\s*", "", linea or "", flags=re.I).strip()
# --veredicto-metodo "<primera línea del metodo.md del plugin>": compara versión y huella con el metodo.md de la raíz,
# en numérico («1.14.10» es mayor que «1.14.9»), imprime el veredicto y termina. Lo usa el paso 1b de tarea.md: la
# comparación la hace el script, no quien lo lee. Mismo criterio que abrir.py de la skill sesion.
_plugin_linea = _arg("--veredicto-metodo")
if _plugin_linea is not None:
    def _vh(linea):
        m = re.search(r"versi[oó]n\s+(\d+(?:\.\d+)*)", linea or "", re.I)
        h = re.search(r"huella\s+([0-9a-f]+)", linea or "", re.I)
        return (tuple(int(x) for x in m.group(1).split(".")) if m else None), (h.group(1) if h else None)
    try:
        with open(RAIZ / "metodo.md", encoding="utf-8-sig", errors="replace") as _f:
            _raiz_linea = _f.readline().strip()
    except OSError:
        _raiz_linea = ""
    vr, hr = _vh(_raiz_linea); vp, hp = _vh(_plugin_linea)
    _t = lambda v: ".".join(map(str, v)) if v else "sin versión"
    if not vp: ver = "SIN VEREDICTO: la línea del plugin no trae versión"
    elif not vr or vp > vr or (vp == vr and not hr): ver = "RAIZ ATRASADA: se copia el metodo.md del plugin"
    elif vp < vr: ver = "PLUGIN ATRASADO: no se copia nada"
    elif hr == hp: ver = "AL DIA"
    else: ver = "MISMA VERSION, HUELLA DISTINTA: no se toca"
    print(f"{ver} (raíz {_t(vr)}, plugin {_t(vp)})")
    sys.exit(0)
# primer tiempo: solo inventario, sin carpeta de salida; segundo tiempo: la raíz es una copia y lo demás viene del inventario
INVENTARIO = "--inventario" in sys.argv
SIN_FECHAS = "--sin-fechas" in sys.argv
_inv_ruta = _arg("--desde-inventario")
INV = json.loads(pathlib.Path(_inv_ruta).read_text(encoding="utf-8")) if _inv_ruta else None
if INV is not None and INV.get("formato") != 1:
    sys.exit("El inventario no es de este generador (formato distinto de 1): vuelve a sacarlo en la computadora con esta misma versión.")
OUT = None if INVENTARIO else pathlib.Path(sys.argv[2])
TAREA = _arg("--tarea")
# una tarea sin horario solo corre desde el botón: el tablero no espera que se ponga al día cada mañana
TAREA_MANUAL = bool(TAREA) and "--manual" in sys.argv
VERSION_PLUGIN = _arg("--version")
# --lineas: el inventario sale en líneas (inventario, cuántos archivos, sus rutas) para leerlo sin otra llamada.
# --si-cambia <huella>: si la huella de la raíz coincide, solo imprime «AL DIA» y no hace falta traer nada.
# --sin-cambios <h1,h2,…>: las huellas de proyecto que guardó la última puesta al día (meta/estado «huellas»). Un proyecto
# cuya huella está en la lista no ha cambiado: el inventario no pide sus archivos y lo marca en «reusar», y la generación
# toma su documento de la base (--previos) en lugar de rehacerlo. Lo mismo con las carpetas fuera de la memoria.
LINEAS = "--lineas" in sys.argv
SI_CAMBIA = _arg("--si-cambia")
SIN_CAMBIOS = {h for h in (_arg("--sin-cambios") or "").split(",") if h and h != "-"}
# --taller-igual pid:huella,…: las huellas del taller de cada proyecto que guardó la última puesta al día (meta/estado,
# «huellas_taller»). Un proyecto que cambió pero cuyo taller no, no vuelve a mandar sus cabeceras por la conversación:
# el inventario lo apunta en «taller_reusar» y la generación toma sus piezas del detalle de la base (--previos).
TALLER_IGUAL = dict(x.split(":", 1) for x in (_arg("--taller-igual") or "").split(",") if ":" in x)
# --previos <volcado de la base>: de donde la generación toma los documentos que el inventario marca en «reusar»
PREVIOS = pathlib.Path(_arg("--previos")) if _arg("--previos") else None
# --cola-retenida <json>: ids de la cola que la puesta al día deja a propósito (esperan al dueño de otra área,
# a una sesión, o no encontraron su paso); el botón no los cuenta como «hace falta sincronizar».
# --cola-ajena <json>: de esos, los que son de un área de otra cuenta; la página dice a quién pasárselos
_aj = _arg("--cola-ajena")
COLA_AJENA = json.loads(pathlib.Path(_aj).read_text(encoding="utf-8")) if _aj else None
_ret = _arg("--cola-retenida")
COLA_RETENIDA = json.loads(pathlib.Path(_ret).read_text(encoding="utf-8")) if _ret else None
# --ruta se acepta por compatibilidad con tareas viejas y no se guarda: la ruta de Drive lleva el correo de la persona
# un solo modo desde la 1.18; --modo, si llega de una tarea vieja, no cambia nada
MODO = "completo"
HOY = datetime.datetime.now(TZ).date().isoformat()

def leer(p):
    """Texto del archivo, o None si no se puede leer (sin permiso, sin descargar, borrado). Un archivo
    con otra codificación no tumba la generación: se lee con reemplazos."""
    try:
        return p.read_bytes().decode("utf-8-sig", errors="replace").replace("\r\n", "\n")
    except OSError:
        return None

def por_que_no(p):
    """Por qué no se pudo leer p: «sin-acceso» (permiso), «sin-carpeta» (la carpeta no existe en esta
    computadora), «sin-archivo» (la carpeta existe y el archivo no), «sin-leer» (otro fallo: sin descargar…)."""
    try:
        p.read_bytes(); return None
    except PermissionError:
        return "sin-acceso"
    except FileNotFoundError:
        return "sin-carpeta" if not p.parent.exists() else "sin-archivo"
    except OSError:
        return "sin-leer"

def fecha_valida(f):
    try:
        datetime.date.fromisoformat(f); return True
    except (ValueError, TypeError):
        return False

def es_sesion_de_tarea(titulo):
    # las tareas programadas dejan su línea en sesiones.md marcada así; no son sesiones de trabajo
    return bool(re.search(r"\((tarea|tablero)\)", titulo or "", re.I))

def frontmatter(texto):
    m = re.match(r"^---\n(.*?)\n---\n?", texto, re.S)
    fm = {}
    if not m:
        return fm, texto
    ultima = None
    for linea in m.group(1).split("\n"):
        mm = re.match(r"^(\w+):\s*(.*)$", linea)
        if mm:
            ultima = mm.group(1)
            v = mm.group(2).strip()
            # listas en línea («[]», «[a, b]»); las de varias líneas se suman abajo
            fm[ultima] = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()] if v.startswith("[") and v.endswith("]") else v.strip("'\"")
            continue
        ml = re.match(r"^\s+-\s+(.*)$", linea)
        if ml and ultima:
            if not isinstance(fm.get(ultima), list):
                fm[ultima] = []
            fm[ultima].append(ml.group(1).strip().strip("'\""))
    return fm, texto[m.end():]

def seccion(texto, nombre):
    m = re.search(r"^## " + re.escape(nombre) + r"\s*\n(.*?)(?=^## |\Z)", texto, re.S | re.M)
    return m.group(1).strip() if m else ""

def titulo_h1(texto):
    m = re.search(r"^# (.+)$", texto, re.M)
    return m.group(1).strip() if m else ""

def bullets(texto):
    out = []
    for l in texto.split("\n"):
        s = l.strip()
        if s.startswith("- "):
            out.append(s[2:].strip())
    return out

def lineas_no_vacias(texto):
    return [l.rstrip() for l in texto.split("\n") if l.strip()]

def primer_parrafo(texto):
    # primer bloque de texto que no sea tabla ni lista
    for bloque in re.split(r"\n\s*\n", texto.strip()):
        b = bloque.strip()
        if not b or b.startswith("|") or b.startswith("- "):
            continue
        return b
    return texto.strip().split("\n")[0] if texto.strip() else ""

def fechas_en(texto):
    return re.findall(r"\b(20\d\d-\d\d-\d\d)\b", texto)

# lo que la base del tablero admite: un doc_id sin espacios ni acentos y un documento de menos de 1 MB (plan_subida.py)
ID_VALIDO = re.compile(r"^(?!\.\.?$)[A-Za-z0-9_\-.~:@+]{1,200}$")
LIMITE_DOC = 1_000_000

# ---------- guia.md ----------
guia = leer(RAIZ / "guia.md") or ""
version_metodo = ""
if INV is not None:
    version_metodo = INV.get("version_metodo", "")
else:
    # de metodo.md solo importa su primera línea
    try:
        with open(RAIZ / "metodo.md", encoding="utf-8-sig", errors="replace") as f_:
            m = re.search(r"(\d+\.\d+(?:\.\d+)?)", f_.readline())
        if m:
            version_metodo = m.group(1)
    except OSError:
        pass
NOMBRE_RAIZ = INV.get("raiz_nombre") if INV is not None else RAIZ.name
org = titulo_h1(guia).split("·")[0].strip() or NOMBRE_RAIZ

areas_guia, guia_avisos = [], []
tabla = seccion(guia, "Áreas")
primera = True
for l in tabla.split("\n"):
    if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
        continue
    if primera:   # la fila de títulos
        primera = False; continue
    celdas = [c.strip() for c in l.strip().strip("|").split("|")]
    if len(celdas) < 5:
        # una fila con columnas de menos no desaparece en silencio: el tablero lo dice en «La memoria al día»
        guia_avisos.append(f"la fila «{celdas[0].strip('`')}» de la tabla de áreas tiene {len(celdas)} columnas y hacen falta 5 (área, qué es, dueño, cuenta, quién la lee)")
        continue
    slug = celdas[0].strip("`").rstrip("/")
    areas_guia.append({"slug": slug, "que": celdas[1], "dueno": celdas[2], "cuenta": celdas[3], "lectores": celdas[4]})
    if cuentas(celdas[3])[2]:
        guia_avisos.append(f"la celda Cuenta de «{slug}» en guia.md: {cuentas(celdas[3])[2]}")
if ZONA_AVISO:
    guia_avisos.append(ZONA_AVISO)
if not areas_guia and guia:
    guia_avisos.append("no se encontró ninguna área en la sección «## Áreas» de guia.md: sin ella nadie tiene área ni cuenta")

quien = seccion(guia, "Quién responde por qué")
contexto_comun = ""
administra = ""
for l in quien.split("\n"):
    if l.lower().startswith("contexto común"):
        contexto_comun = l.split(":", 1)[-1].strip().rstrip(".")
    if l.lower().startswith("administra"):
        administra = l.split(":", 1)[-1].strip().rstrip(".")
# los nombres, sin la cuenta entre paréntesis: el tablero no lleva correos
contexto_comun = CORREO.sub("", re.sub(r"\s*(\([^)]*\)|<[^>]*>)", "", contexto_comun)).strip(" .")
administra = CORREO.sub("", re.sub(r"\s*(\([^)]*\)|<[^>]*>)", "", administra)).strip(" .")

# ---------- premisas: el único archivo de base/ que lee el tablero ----------
premisas = []
for l in (leer(RAIZ / "base" / "premisas.md") or "").split("\n"):
    mm = re.match(r"^\s*-\s*(P\d+)\s*·\s*(.+)$", l)
    if not mm:
        continue
    partes = [x.strip() for x in mm.group(2).split("·")]
    pr = {"id": mm.group(1).upper(), "texto": partes[0], "confirmo": "", "fecha": "", "reemplaza": ""}
    for x in partes[1:]:
        if x.lower().startswith("confirmó:") or x.lower().startswith("confirmo:"):
            pr["confirmo"] = x.split(":", 1)[1].strip()
        elif re.match(r"^20\d\d-\d\d-\d\d$", x):
            pr["fecha"] = x
        elif x.lower().startswith("reemplaza a"):
            mr = re.search(r"P\d+", x, re.I); pr["reemplaza"] = mr.group(0).upper() if mr else ""
    premisas.append(pr)
reemplazadas = {p_["reemplaza"] for p_ in premisas if p_["reemplaza"]}
for p_ in premisas:
    p_["vigente"] = p_["id"] not in reemplazadas

# ---------- proyectos ----------
def parse_decisiones(texto):
    out = []
    if not texto:
        return out
    partes = re.split(r"^## ", texto, flags=re.M)[1:]
    for p in partes:
        cab, _, cuerpo = p.partition("\n")
        mm = re.match(r"(20\d\d-\d\d-\d\d)\s*·\s*(.*)", cab.strip())
        if mm:
            fecha, titulo = mm.group(1), mm.group(2).strip()
        else:
            fecha, titulo = (fechas_en(cab) or [""])[0], cab.strip()
        campos = {"decidio": "", "porque": "", "descartamos": "", "afecta": "", "planteo": "", "cuestiona": "", "responde": "", "reemplaza": ""}
        actual = None
        for l in cuerpo.split("\n"):
            s = l.strip()
            low = s.lower()
            if low.startswith("decidió:") or low.startswith("decidio:"):
                actual = "decidio"; campos[actual] = s.split(":", 1)[1].strip()
            elif low.startswith("por qué:") or low.startswith("por que:"):
                actual = "porque"; campos[actual] = s.split(":", 1)[1].strip()
            elif low.startswith("descartamos:"):
                actual = "descartamos"; campos[actual] = s.split(":", 1)[1].strip()
            elif low.startswith("afecta a:"):
                actual = "afecta"; campos[actual] = s.split(":", 1)[1].strip()
            elif low.startswith("planteó:") or low.startswith("planteo:"):
                actual = "planteo"; campos[actual] = s.split(":", 1)[1].strip()
            elif low.startswith("cuestiona a:"):
                actual = "cuestiona"; campos[actual] = s.split(":", 1)[1].strip()
            elif low.startswith("responde a:"):
                actual = "responde"; campos[actual] = s.split(":", 1)[1].strip()
            elif low.startswith("reemplaza:") or low.startswith("reemplaza a:"):
                actual = "reemplaza"; campos[actual] = s.split(":", 1)[1].strip()
            elif actual and s:
                campos[actual] += "\n" + s
        d_ = {"fecha": fecha, "titulo": titulo, **campos}
        # solo el marcador del contrato: «Decidió: Nombre (pendiente de confirmar)»; mencionarlo en el por qué no cuenta
        if re.search(r"\(pendiente de confirma(r|ción)\)", campos["decidio"].lower()):
            d_["por_confirmar"] = True
        if campos["cuestiona"] or re.match(r"cuestionamiento\b", titulo, re.I):
            d_["tipo"] = "cuestionamiento"
            t_ = re.sub(r"^cuestionamiento\s*:\s*", "", titulo, flags=re.I) or titulo
            d_["titulo"] = t_[:1].upper() + t_[1:]
        for k in ("planteo", "cuestiona", "responde", "reemplaza"):
            if not d_[k]: del d_[k]
        out.append(d_)
    # identificador: la fecha y, si ese día hay más de una entrada, -2, -3… contando desde la de más abajo (la más antigua)
    # una entrada sin fecha válida no tiene identificador: no se puede citar
    cuenta = {}
    for d_ in reversed(out):
        if not fecha_valida(d_["fecha"]):
            d_["id"] = ""; continue
        n = cuenta[d_["fecha"]] = cuenta.get(d_["fecha"], 0) + 1
        d_["id"] = d_["fecha"] + ("" if n == 1 else f"-{n}")
    out.sort(key=lambda d: d["fecha"], reverse=True)
    return out

def ref_decision(texto):
    """De «area/proyecto#2026-10-15-2 (…)» devuelve («area--proyecto», «2026-10-15-2»); de «premisa P3», («premisa», «P3»)."""
    t = (texto or "").strip()
    mp = re.search(r"\bpremisa\s+(P\d+)", t, re.I)
    if mp:
        return ("premisa", mp.group(1).upper())
    m = re.search(r"`?([a-z0-9][\w.-]*)/([a-z0-9][\w.-]*)#(20\d\d-\d\d-\d\d(?:-\d+)?)", t)
    return (f"{m.group(1)}--{m.group(2)}", m.group(3)) if m else (None, None)

def parse_sesiones(texto):
    out = []
    if not texto:
        return out
    partes = re.split(r"^## ", texto, flags=re.M)[1:]
    for p in partes:
        cab, _, cuerpo = p.partition("\n")
        fecha = (fechas_en(cab) or [""])[0]
        titulo = cab.strip()
        campos = {"trabajamos": "", "avances": "", "pendiente": ""}
        quien = ""
        actual = None
        for l in cuerpo.split("\n"):
            s = l.strip()
            low = s.lower()
            if low.startswith("trabajamos en:"):
                actual = "trabajamos"; campos[actual] = s.split(":", 1)[1].strip()
            elif low.startswith("avances:"):
                actual = "avances"; campos[actual] = s.split(":", 1)[1].strip()
            elif low.startswith("pendiente:"):
                actual = "pendiente"; campos[actual] = s.split(":", 1)[1].strip()
            elif low.startswith("sesión de:") or low.startswith("sesion de:"):
                actual = None
                # quién cerró, sin la versión del plugin: «Sesión de: Nombre Apellido · plugin 1.16.0» → «Nombre Apellido»
                quien = re.split(r"\s+[·\-–—]\s+|\s*\(", s.split(":", 1)[1].strip(), maxsplit=1)[0].strip()[:80]
            elif actual and s:
                campos[actual] += "\n" + s
        out.append({"fecha": fecha, "titulo": titulo, **campos, **({"quien": quien} if quien else {})})
    out.sort(key=lambda d: d["fecha"], reverse=True)
    return out

def parse_indice_proyectos(texto_area):
    """Devuelve {slug: {"descripcion":..., "entregables":{stem: {"descripcion","actualizado"}}, "notas":[...]}}"""
    bloque = seccion(texto_area, "Proyectos")
    idx = {}
    actual = None
    for l in bloque.split("\n"):
        m1 = re.match(r"^- `([^`]+?)/?`\s*[—–:-]?\s*(.*)$", l)
        if m1 and ("/" in m1.group(1) or m1.group(1).startswith(".")):
            actual = None; continue          # un proyecto es una carpeta del área: «../otra-area/…» no es un proyecto y no se sigue
        if m1:
            actual = m1.group(1)
            idx[actual] = {"descripcion": m1.group(2).strip(), "entregables": {}, "notas": []}
            continue
        m2 = re.match(r"^\s+- (.*)$", l)
        if m2 and actual:
            item = m2.group(1).strip()
            m3 = re.match(r"^([\w\-, ]+?)\s+[—–-]\s+(.*?)(?:\s*·\s*actualizado\s*(20\d\d-\d\d-\d\d))?\s*$", item)
            if m3 and m3.group(3):
                for stem in [s.strip() for s in m3.group(1).split(",")]:
                    idx[actual]["entregables"][stem] = {"descripcion": m3.group(2).strip(), "actualizado": m3.group(3)}
            else:
                idx[actual]["notas"].append(item)
    return idx

def fecha_de(p):
    """Fecha de modificación de p (día, en la zona de la organización), o None. Sin fechas (una copia), siempre None."""
    if SIN_FECHAS:
        return None
    try:
        return datetime.datetime.fromtimestamp(os.stat(p).st_mtime, TZ).date().isoformat()
    except OSError:
        return None

def momento(p):
    """Fecha y hora de modificación de p («AAAA-MM-DD», «HH:MM») en la zona de la organización, o (None, None)."""
    if SIN_FECHAS:
        return None, None
    try:
        t = datetime.datetime.fromtimestamp(os.stat(p).st_mtime, TZ)
        return t.date().isoformat(), t.strftime("%H:%M")
    except OSError:
        return None, None

def marca(p):
    """Lo que dice si p cambió: su fecha de modificación en la computadora; en una copia (sin fechas), su contenido."""
    if SIN_FECHAS:
        return hashlib.sha1(pathlib.Path(p).read_bytes()).hexdigest()[:12]
    return int(os.path.getmtime(p))

def rel(p):
    return pathlib.Path(p).relative_to(RAIZ).as_posix()

def fechas_de_entregables(carpeta):
    """{archivo: fecha} de los entregables cuya fecha solo puede salir del archivo: los que no son .md, los .md que
    no se dejan leer y los que no traen «actualizado» en su cabecera. Es lo que el inventario lleva de cada proyecto."""
    d = carpeta / "entregables"
    out = {}
    try:
        nombres = sorted(os.listdir(d)) if d.exists() else []
    except OSError:
        return out
    for n in nombres:
        p = d / n
        if n.startswith(".") or p.is_dir():
            continue
        if n.endswith(".md"):
            t = leer(p)
            if t is not None and frontmatter(t)[0].get("actualizado"):
                continue
        f = fecha_de(p)
        if f:
            out[n] = f
        else:
            out[n] = None
    return out

def entregables_de(carpeta, indice):
    out = []
    d = carpeta / "entregables"
    fechas_inv = None
    if INV is not None:
        # la copia trae solo los .md legibles; los demás nombres y sus fechas vienen del inventario
        fechas_inv = INV.get("entregables", {}).get(rel(carpeta), {})
        try:
            copiados = [n for n in os.listdir(d) if not n.startswith(".") and n.endswith(".md")] if d.exists() else []
        except OSError:
            copiados = []
        nombres = sorted(set(copiados) | set(fechas_inv))
    else:
        if not d.exists():
            return out
        try:
            nombres = sorted(os.listdir(d))
        except OSError:
            return out
    for n in nombres:
        p = d / n
        if n.startswith(".") or (fechas_inv is None and p.is_dir()):
            continue
        stem = pathlib.Path(n).stem
        ent = {"archivo": n, "nombre": stem, "estado": None, "actualizado": None, "descripcion": "", "formato": pathlib.Path(n).suffix.lstrip(".")}
        if n.endswith(".md"):
            t = leer(p)
            if t is not None:
                fm, cuerpo_e = frontmatter(t)
                ent["titulo"] = titulo_h1(cuerpo_e) or None
                ent["estado"] = fm.get("estado")
                if isinstance(fm.get("basado_en"), list):
                    ent["basado_en"] = [re.sub(r"^\./", "", b) for b in fm["basado_en"]]
                ent["actualizado"] = fm.get("actualizado")
                if fm.get("reemplazado_por"):
                    ent["reemplazado_por"] = fm["reemplazado_por"]
                if isinstance(fm.get("afirma"), str) and fm["afirma"].strip():
                    ent["afirma"] = fm["afirma"].strip()[:240]
        ref = indice.get(stem) or (indice.get(stem[:-3]) if stem.endswith("-en") else None)
        if ref:
            ent["descripcion"] = ref["descripcion"]
            if not ent["actualizado"]:
                ent["actualizado"] = ref["actualizado"]
        if not ent["actualizado"]:
            f = fechas_inv.get(n) if fechas_inv is not None else fecha_de(p)
            if f:
                ent["actualizado"] = f
                ent["fecha_de_archivo"] = True
        out.append(ent)
    return out


def taller_de(carpeta):
    """El inventario del taller de un proyecto: de cada archivo de `taller/` (primer nivel), lo que dice su cabecera y nada
    del cuerpo (estado, actualizado, afirma, basado_en, reemplazado_por, el título). El cuerpo es taller privado del área;
    su inventario se enseña a quien lee el área (decisión 2026-10-23). Con inventario, viene ya sacado de la computadora."""
    if SIN_FECHAS:   # sin consola la copia no trae el taller (espejo.py nunca lo pide): el inventario no existe
        return []
    if INV is not None:
        if rel(carpeta) in (INV.get("taller_reusar") or []):
            det_ = _de_la_base("detalle", rel(carpeta).replace("/", "--")) if PREVIOS else None
            if not isinstance(det_, dict):
                sys.stderr.write(f"A la base le falta el detalle de {rel(carpeta)}, que el inventario pidió reutilizar para su taller: vuelve al inventario sin --taller-igual.\n")
                sys.exit(5)
            return [{k: v for k, v in pz.items() if k != "tipo"} for pz in ((det_.get("que_hay") or {}).get("piezas") or []) if pz.get("tipo") == "taller"]
        return INV.get("taller", {}).get(rel(carpeta), [])
    d = carpeta / "taller"
    out = []
    try:
        nombres = sorted(os.listdir(d)) if d.exists() else []
        # un nivel de agrupación, como permite el contrato (sección 3): «sub/nota.md»
        for sub in [x for x in nombres if (d / x).is_dir() and not x.startswith(".") and x != "restringido"]:
            nombres += [f"{sub}/{x}" for x in sorted(os.listdir(d / sub)) if not x.startswith(".") and (d / sub / x).is_file()]
    except OSError:
        return out
    for n in nombres:
        p = d / n
        if n.startswith(".") or p.is_dir():
            continue
        pz = {"archivo": n, "nombre": pathlib.Path(n).stem, "estado": None, "actualizado": None, "formato": pathlib.Path(n).suffix.lstrip(".")}
        if n.endswith(".md"):
            t = leer(p)
            if t is not None:
                fm, cuerpo_ = frontmatter(t)
                pz["titulo"] = titulo_h1(cuerpo_) or None
                pz["estado"] = fm.get("estado")
                pz["actualizado"] = fm.get("actualizado")
                if fm.get("reemplazado_por"):
                    pz["reemplazado_por"] = fm["reemplazado_por"]
                if isinstance(fm.get("afirma"), str) and fm["afirma"].strip():
                    pz["afirma"] = fm["afirma"].strip()[:240]
        if not pz["actualizado"]:
            f = fecha_de(p)
            if f:
                pz["actualizado"] = f; pz["fecha_de_archivo"] = True
        out.append(pz)
    return out


def entregables_en_subcarpetas(carpeta):
    """Cuántos archivos hay en subcarpetas de entregables/: el inventario no los trae todavía, y se dice en vez de callarlo."""
    if SIN_FECHAS:   # sin consola la copia no trae subcarpetas: no hay nada que contar
        return 0
    if INV is not None:
        return INV.get("entregables_sub", {}).get(rel(carpeta), 0)
    d = carpeta / "entregables"
    try:
        return sum(1 for sub in os.listdir(d) if (d / sub).is_dir() and not sub.startswith(".") and sub != "restringido"
                   for x in os.listdir(d / sub) if not x.startswith(".") and (d / sub / x).is_file()) if d.exists() else 0
    except OSError:
        return 0


def que_hay(pdoc, taller, dec):
    """La capa calculada de «Qué hay» (decisión 2026-10-23): de cada pieza, cuántas decisiones del proyecto son posteriores
    a su última actualización, qué pasos de «Siguientes pasos» la nombran (lo que la bloquea), si el taller la cita algún
    entregable; y la trayectoria: las cadenas de decisiones que se reemplazan y de entregables reemplazados."""
    piezas = [dict(e, tipo="entregable") for e in pdoc.get("entregables", [])] + [dict(t, tipo="taller") for t in taller]
    fechas_dec = sorted((d_["fecha"] for d_ in dec if fecha_valida(d_["fecha"]) and d_.get("tipo") != "cuestionamiento"), reverse=True)
    pasos = [p_["texto"] for p_ in pdoc.get("pasos", []) if p_.get("naturaleza")]
    citas = set()
    for e in pdoc.get("entregables", []):
        for b in e.get("basado_en") or []:
            citas.add(b.split("/")[-1])
    for pz in piezas:
        act = pz.get("actualizado")
        if act and fecha_valida(act) and pz.get("estado") in ("vigente", "borrador"):
            desp = [f for f in fechas_dec if f > act]
            if desp:
                pz["decisiones_despues"] = len(desp); pz["ultima_decision_despues"] = desp[0]
        # los pasos que la nombran: por el nombre del archivo o por dos palabras significativas del título
        claves = {pz["nombre"].lower()}
        sig = PALABRAS_SIG(pz.get("titulo") or "")
        bloq = []
        for t_ in pasos:
            tl = t_.lower()
            if any(k in tl for k in claves) or (len(sig) >= 2 and len(sig & PALABRAS_SIG(t_)) >= 2):
                bloq.append(t_[:160])
        if bloq:
            pz["pasos"] = bloq[:3]
        if pz["tipo"] == "taller":
            pz["citada"] = pz["archivo"] in citas
    # trayectoria por decisiones: «Reemplaza: AAAA-MM-DD · …» encadena la nueva con la vieja
    por_id = {d_["id"]: d_ for d_ in dec if d_.get("id")}
    reemplaza, reemplazada = {}, set()
    for d_ in dec:
        for fid in re.findall(r"20\d\d-\d\d-\d\d(?:-\d+)?", d_.get("reemplaza") or ""):
            if fid in por_id and fid != d_.get("id"):
                reemplaza.setdefault(d_["id"], []).append(fid); reemplazada.add(fid)
    cadenas = []
    for d_ in dec:
        if d_.get("id") in reemplaza and d_["id"] not in reemplazada:
            nodos, cur, vistos = [], d_["id"], set()
            while cur and cur not in vistos and len(nodos) < 6:
                vistos.add(cur); x = por_id[cur]
                nodos.append({"fecha": x["fecha"], "titulo": x["titulo"][:140]})
                cur = (reemplaza.get(cur) or [None])[0]
            nodos.reverse()
            cadenas.append({"de": "decisiones", "pasos": nodos})
    # trayectoria por entregables: reemplazado_por apunta al sustituto, por nombre de archivo
    por_arch = {pz["archivo"]: pz for pz in piezas}
    sucesor = {}
    for pz in piezas:
        rp = (pz.get("reemplazado_por") or "").split("/")[-1]
        if rp in por_arch and rp != pz["archivo"]:
            sucesor[pz["archivo"]] = rp
    con_sucesor = set(sucesor.values())
    for a0 in sorted(sucesor):
        if a0 in con_sucesor:
            continue
        nodos, cur, vistos = [], a0, set()
        while cur and cur not in vistos and len(nodos) < 6:
            vistos.add(cur); x = por_arch[cur]
            nodos.append({"fecha": x.get("actualizado"), "titulo": (x.get("titulo") or x["nombre"])[:140]})
            cur = sucesor.get(cur)
        cadenas.append({"de": "taller" if x["tipo"] == "taller" else "entregables", "pasos": nodos})   # x: el último nodo recorrido
    cadenas.sort(key=lambda c: (c["pasos"][-1].get("fecha") or ""), reverse=True)
    def cuenta(lista):
        c = {"borrador": 0, "vigente": 0, "reemplazado": 0, "otros": 0}
        for x in lista:
            c[x.get("estado") if x.get("estado") in c else "otros"] += 1
        return c
    resumen = {"taller": cuenta(taller), "entregables": cuenta(pdoc.get("entregables", [])), "decisiones": len(fechas_dec),
               "sin_afirma": sum(1 for pz in piezas if pz.get("estado") != "reemplazado" and pz["archivo"].endswith(".md") and not pz.get("afirma")),
               "desfasadas": sum(1 for pz in piezas if pz.get("decisiones_despues")),
               "bloqueadas": sum(1 for pz in piezas if pz.get("pasos")),
               "cadenas": len(cadenas)}
    if pdoc.get("_sub"):
        resumen["entregables_en_subcarpetas"] = pdoc["_sub"]    # se listan en la siguiente versión; mientras, se cuentan
    if cadenas:
        resumen["ultimo_giro"] = cadenas[0]["pasos"][-1]
    if SIN_FECHAS:
        resumen["taller"] = None   # sin consola no se inventaría el taller; la página lo dice
    return resumen, {"piezas": piezas, "trayectoria": cadenas[:8]}


# ---------- clasificación de pasos ----------
STOP = set("de la el los las un una y o en a al del para por con sin que se su sus lo le les es son como más ya no si este esta esto ese esa eso hay hasta desde sobre entre cuando donde cada muy también antes después tras ante aún sólo solo mismo misma otra otro otros otras todo toda todos todas ser estar tener hacer poner".split())
PALABRAS_SIG = lambda t: {w for w in re.findall(r"[a-záéíóúñ]{4,}", t.lower()) if w not in STOP}

def naturaleza(texto):
    t = texto.strip().lower()
    t = re.sub(r"^(20\d\d-\d\d-\d\d:?\s*)", "", t)
    if re.match(r"^(sostener|mantener|seguir |continuar|cada (semana|mes|lunes|viernes))", t): return "rutina"
    if re.search(r"(según su caducidad|caducidad|vence en (enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)|se revisa en \w+ de 20\d\d|revisión (fijada|trimestral|anual))", t): return "caducidad"
    if re.match(r"^(esperar|recoger la respuesta|a la espera|aguardar)", t) or re.search(r"\bsi no (escribe|contesta|responde|llama|ha llamado|hay respuesta)\b", t) or re.match(r"^(cuando|en cuanto) \w+ (conteste|responda|escriba|confirme|mande|envíe)", t): return "espera"
    if re.match(r"^(al cumplirse|al (firmarse|arrancar|migrar|contratar|cerrar|terminar)|cuando |en unas semanas|en una o dos semanas|retomar|más adelante|después de|tras |una vez que|mirar en )", t): return "condicional"
    if re.match(r"^(decidir|definir|confirmar|elegir|acordar|aprobar|fijar|cerrar `?[\w\-/.]+\.md|pasar(lo|la)? a vigente|revisar .{0,80} para pasar(lo|la)? a vigente|resolver|replantear)", t): return "decision"
    return "accion"

# palabras que aparecen en todas partes y no agrupan nada: las genéricas, el nombre de la organización y sus dueños
RUIDO = set("claude cowork memoria pro google workspace mac ahora después".split())
# un dueño solo es ruido si lleva la mitad de las áreas o más: entonces sale en casi todos los pasos y no distingue
_duenos = [a["dueno"] for a in areas_guia]
RUIDO |= {w.lower() for w in re.findall(r"[\wáéíóúñ]+", org + " " + " ".join(d for d in set(_duenos) if len(_duenos) > 1 and _duenos.count(d) * 2 > len(_duenos))) if len(w) > 2}
def tokens_tema(texto):
    """Tokens que sirven para agrupar pasos de proyectos distintos: entregables citados, nombres propios, herramientas y roles."""
    toks = set()
    for m in re.findall(r"`([^`]+)`", texto):
        base = m.strip("/").split("/")[-1]
        base = re.sub(r"\.(md|html|pdf|docx|xlsx)$", "", base)
        if base and base not in ("proyecto", "decisiones", "sesiones", "area", "guia", "fuentes", "taller", "entregables"): toks.add(base.lower())
    sin_cod = re.sub(r"`[^`]+`", " ", texto)
    # nombres propios de una o más palabras seguidas con mayúscula, no al inicio de frase
    for m in re.finditer(r"(?<![.\n])(?<=[\s(,;:])((?:[A-ZÁÉÍÓÚ][\wáéíóúñ&+.]*\s?){1,3})", sin_cod):
        nombre = m.group(1).strip().lower()
        if nombre and nombre not in RUIDO and not re.match(r"^(al|si|en|la|el|los|las|un|una|es|hoy|lo|se|no|su|sus|con|de|para|por|que|ese|esa|este|esta|cada|antes|después|mirar)$", nombre):
            toks.add(nombre)
    for rol in ("abogado", "contador", "notario", "banco"):
        if re.search(r"\b" + rol + r"\b", sin_cod.lower()): toks.add(rol)
    for tool in ("posthog", "linkedin", "github", "gitlab", "cloudflare", "drive", "odoo", "whatsapp", "gmail", "outlook", "slack", "teams", "jira", "clickup", "figma", "notion", "hubspot", "salesforce", "sap", "shopify", "stripe", "aws"):
        if re.search(r"\b" + re.escape(tool) + r"\b", sin_cod.lower()): toks.add(tool)
    # un token de varias palabras es ruido si lo es alguna de ellas («ana pérez» con «ana» de dueña de casi todo)
    return {t for t in toks if t not in RUIDO and not (set(t.split()) & RUIDO)}


PLAZO_ANTES = r"(antes del|antes de|para el|hasta el|a más tardar el|fecha límite:?|vence el|vencido el|vencida el|el próximo|el lunes|el martes|el miércoles|el jueves|el viernes|el sábado|el domingo|lunes|martes|miércoles|jueves|viernes|esperar (?:al|hasta el)|en la revisión del|revisión (?:trimestral|anual)? ?del|el)\s*"
CONTEXTO_ANTES = r"(compartió(?: por \w+)? el|compartid[oa]s? el|mandó el|envió el|respondió el|dijo el|llegó el|salió el|arrancó el|se montó el|quedó el|hizo el|cambió el|pasó el|enviad[oa]s? el|rehech[oa]s? el|comprobad[oa] el|publicad[oa] el|puest[oa] al día el|decisión del|desde el|montó el|creado el|creada el|firmad[oa] el|registrad[oa] el|actualizad[oa] el|del día|abierta el|cerrad[oa] el|entregad[oa] el|presentad[oa] el|hallazgo del|sesión del|propuesta del|criterio del|detectad[oa] el|revisad[oa] el|contestó el|escribió el|quedaron el)\s*"
def plazos_en(texto):
    out = []
    previa = None   # cómo se leyó la fecha anterior, para «el 2026-09-01 y el 2026-09-02»
    for m in re.finditer(r"\b(20\d\d-\d\d-\d\d)\b", texto):
        f = m.group(1)
        if not fecha_valida(f): continue
        antes = texto[max(0, m.start()-40):m.start()].lower()
        despues = texto[m.end():m.end()+12].lower()
        if m.start() <= 2: out.append(f); previa = True; continue          # «2026-10-13: buscar a…»
        if previa is not None and re.search(r"20\d\d-\d\d-\d\d\s*(y|o|,)\s*(el\s*)?$", antes):
            if previa: out.append(f)
            continue
        previa = False
        if re.search(r"(?<![\wáéíóú])" + CONTEXTO_ANTES + r"$", antes): continue             # «enviada el 2026-09-21»
        mp = re.search(r"([a-záéíóúñ]+)\s+el\s*$", antes)
        if mp and re.search(r"((ad|id|ech|ich|uest|uelt|biert|scrit|suelt)[oa]s?|ó|aron|ieron|é|ía|ían)$", mp.group(1)): continue   # «registradas el», «quedó el»: contexto
        if re.search(r"(?<![\wáéíóú])" + PLAZO_ANTES + r"$", antes) or despues.startswith(" a las") or (despues.startswith(":") and not re.search(r"\bdel\s*$", antes)):
            out.append(f); previa = True
    return out

def senales(paso_texto, area_doc, pdoc):
    """Señales objetivas de importancia. Vencido no cuenta, por decisión del 2026-10-08."""
    sig = PALABRAS_SIG(paso_texto)
    prio = None
    for i, pr in enumerate(area_doc.get("prioridades", [])):
        if len(sig & PALABRAS_SIG(pr)) >= 3: prio = i + 1; break
    cliente = pdoc["area"] == "clientes" or bool(re.search(r"\b(cliente|propuesta|contrato|firma|factur\w*|cobro|precio|impi|acuerdo de confidencialidad)\b", paso_texto.lower()))
    return {"prioridad_area": prio, "cliente_o_dinero": cliente}

def sin_sesion_de(pc, ses, cerrado):
    """Trabajo sin sesión de un proyecto, mirando solo fechas de archivo (nunca contenido), o None.
    Con inventario, viene ya calculado de la computadora, donde están las fechas de verdad."""
    if INV is not None:
        return INV.get("sin_sesion", {}).get(rel(pc))
    ultima_entrada = ses[0]["fecha"] if ses and fecha_valida(ses[0]["fecha"]) else None
    if not ultima_entrada or cerrado:
        return None
    donde, ultimo, lista = {}, None, []
    objetivos = [("entregables", pc / "entregables"), ("taller", pc / "taller"), ("fuentes", pc / "fuentes")]
    for nombre, d in objetivos:
        for raiz_, dirs, files in os.walk(d) if d.exists() else []:
            dirs[:] = [x for x in dirs if not x.startswith(".") and x != "restringido"]
            for f in files:
                if f.startswith("."):
                    continue
                fm_, hora_ = momento(os.path.join(raiz_, f))
                if not fm_:
                    continue
                if fm_ > ultima_entrada:
                    donde[nombre] = donde.get(nombre, 0) + 1
                    ultimo = max(ultimo or fm_, fm_)
                    # qué archivo y cuándo; el nombre del taller es inventario público (contrato, sección 7); el de fuentes/ no sale
                    lista.append({"archivo": pathlib.Path(raiz_, f).relative_to(pc).as_posix() if nombre != "fuentes" else "fuentes/…",
                                  "fecha": fm_, "hora": hora_})
    fd, hd = momento(pc / "decisiones.md")
    if fd and fd > ultima_entrada:
        donde["decisiones"] = 1; ultimo = max(ultimo or fd, fd); lista.append({"archivo": "decisiones.md", "fecha": fd, "hora": hd})
    if donde:
        # quién hizo cada cambio no consta: la carpeta no lo guarda y Drive no se lo da al plugin. Se dice qué y cuándo.
        lista.sort(key=lambda x: (x["fecha"], x["hora"] or ""), reverse=True)
        return {"desde": ultima_entrada, "ultimo": ultimo, "donde": donde, "archivos": sum(donde.values()), "lista": lista[:12]}
    return None

def motivo_de(p):
    """Por qué no se leyó p: en la computadora se pregunta al disco; con inventario, lo dice el inventario."""
    if INV is not None:
        return INV.get("motivos", {}).get(rel(p), "sin-leer")
    return por_que_no(p) or "sin-leer"

def proyectos_de(carpeta, indice):
    """Los proyectos de un área: los de su índice más cualquier carpeta con proyecto.md, en ese orden."""
    if INV is not None:
        return list(INV.get("proyectos", {}).get(rel(carpeta), list(indice.keys())))
    slugs = list(indice.keys())
    try:
        for n in sorted(os.listdir(carpeta)):
            if (carpeta / n).is_dir() and not n.startswith(".") and n not in slugs and (carpeta / n / "proyecto.md").exists():
                slugs.append(n)
    except OSError:
        pass
    return slugs

def fuera_de_la_memoria():
    """Carpetas de la raíz que no son de ningún área: «Claude outputs» es donde la app de Claude deja lo que produce;
    cualquier otra carpeta suelta también queda fuera. Solo se cuentan archivos y fechas; los nombres, solo en completo."""
    if INV is not None:
        return INV.get("fuera", [])
    fuera_ = []
    slugs_area = {a["slug"] for a in areas_guia}
    try:
        sueltas = [n for n in sorted(os.listdir(RAIZ)) if (RAIZ / n).is_dir() and not n.startswith(".") and n not in slugs_area and n != "base"]
    except OSError:
        sueltas = []
    for n in sueltas:
        arch = []
        for raiz_, dirs, files in os.walk(RAIZ / n):
            dirs[:] = [x for x in dirs if not x.startswith(".")]
            for f in files:
                if f.startswith("."): continue
                fecha = fecha_de(os.path.join(raiz_, f))
                if not fecha:
                    continue
                arch.append((fecha, os.path.relpath(os.path.join(raiz_, f), RAIZ / n)))
        if not arch: continue
        arch.sort(reverse=True)
        item = {"carpeta": n, "de_claude": n.lower() == "claude outputs", "archivos": len(arch), "ultimo": arch[0][0], "primero": arch[-1][0]}
        item["nombres"] = [{"fecha": f_, "nombre": n_} for f_, n_ in arch[:40]]
        fuera_.append(item)
    return fuera_

def huella_copia(tamanos):
    """Huella de una copia: cada ruta (en NFC, para que los acentos de macOS no la cambien) con su tamaño."""
    lineas = sorted(f"{unicodedata.normalize('NFC', r)}\t{t}" for r, t in tamanos.items())
    return hashlib.sha1("\n".join(lineas).encode("utf-8")).hexdigest()[:16]

def sello(inv):
    """Sello del inventario: detecta que se copió mal al pasarlo de la computadora a Claude."""
    sin = {k: v for k, v in inv.items() if k != "sello"}
    return hashlib.sha1(json.dumps(sin, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:12]

# ---------- primer tiempo: el inventario, en la computadora ----------
if INVENTARIO:
    leer_ = []
    inv = {"formato": 1, "raiz_nombre": RAIZ.name, "modo": MODO, "generado": HOY, "version_metodo": version_metodo,
           "motivos": {}, "proyectos": {}, "entregables": {}, "sin_sesion": {}}
    _script = hashlib.sha1(pathlib.Path(__file__).read_bytes()).hexdigest()
    huellas, reusar, por_proyecto, huellas_taller = {}, [], {}, {}   # huellas: {pid: huella}; por_proyecto: {area/proyecto: (sus archivos, sus entregables, su trabajo sin sesión)}
    def _si_legible(p, lista=None):
        if leer(p) is not None:
            (leer_ if lista is None else lista).append(rel(p)); return True
        return False
    def _huella_proyecto(*partes):
        return hashlib.sha1(json.dumps(partes, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:12]
    _si_legible(RAIZ / "guia.md")
    _si_legible(RAIZ / "base" / "premisas.md")
    for a in areas_guia:
        carpeta = RAIZ / a["slug"]
        texto = leer(carpeta / "area.md")
        if texto is None:
            inv["motivos"][rel(carpeta / "area.md")] = por_que_no(carpeta / "area.md") or "sin-leer"
            continue
        leer_.append(rel(carpeta / "area.md"))
        indice = parse_indice_proyectos(frontmatter(texto)[1])
        prioridades_ = bullets(seccion(frontmatter(texto)[1], "Prioridades ahora"))
        slugs = proyectos_de(carpeta, indice)
        inv["proyectos"][rel(carpeta)] = slugs
        for slug in slugs:
            pc = carpeta / slug
            ref = indice.get(slug, {"descripcion": "", "entregables": {}, "notas": []})
            tp = leer(pc / "proyecto.md")
            if tp is None:
                inv["motivos"][rel(pc / "proyecto.md")] = por_que_no(pc / "proyecto.md") or "sin-leer"
                continue
            suyos = [rel(pc / "proyecto.md")]
            ses = parse_sesiones(leer(pc / "sesiones.md")) if _si_legible(pc / "sesiones.md", suyos) else []
            _si_legible(pc / "decisiones.md", suyos)
            fm_p, cuerpo_p = frontmatter(tp)
            cerrado = bool(re.search(r"Proyecto terminado el\s*20\d\d-\d\d-\d\d", seccion(cuerpo_p, "Estado actual")))
            ss_ = sin_sesion_de(pc, ses, cerrado)
            d = pc / "entregables"
            try:
                for n in sorted(os.listdir(d)) if d.exists() else []:
                    if n.endswith(".md") and not n.startswith(".") and (d / n).is_file():
                        _si_legible(d / n, suyos)
            except OSError:
                pass
            fe = fechas_de_entregables(pc)
            tal = taller_de(pc)
            sub_ = entregables_en_subcarpetas(pc)
            # La huella del proyecto: todo lo que entra en su documento antes de cruzarlo con los demás. Sus archivos (tamaño y
            # fecha), lo que el área dice de él (su fila de guia.md, su línea del índice, las prioridades), sus fechas de entregables,
            # su trabajo sin sesión, el modo y este script. Del día solo cuenta lo que lo usa: qué sesiones caen en los últimos
            # 90 días y, si no tiene sesiones ni «actualizado», la fecha de hoy. Así un proyecto que no se tocó no se vuelve a traer
            # aunque cambie el día.
            _reales = [s_ for s_ in ses if not es_sesion_de_tarea(s_["titulo"])]
            reales_ = [s_["fecha"] for s_ in _reales if fecha_valida(s_["fecha"])]
            _lim = (datetime.date.fromisoformat(HOY) - datetime.timedelta(days=90)).isoformat()
            # igual que la generación: la última sesión es la primera de la lista aunque su fecha no sea válida
            sin_ref = not fecha_valida(_reales[0]["fecha"] if _reales else None) and not fecha_valida(fm_p.get("actualizado"))
            h = _huella_proyecto(_script, MODO, a, ref, prioridades_, slug,
                                 [(r_, os.path.getsize(RAIZ / r_), marca(RAIZ / r_)) for r_ in suyos],
                                 sorted({f_ for f_ in reales_ if f_ >= _lim}), HOY if sin_ref else "", fe, ss_, tal, sub_)
            pid = f"{a['slug']}--{slug}"
            por_proyecto[rel(pc)] = (suyos, fe, ss_, tal, sub_)
            # un id que la base no admite (espacios, acentos) nunca llega a ella: no se puede reutilizar
            if ID_VALIDO.match(pid):
                huellas[pid] = h
            if pid in huellas and h in SIN_CAMBIOS:
                reusar.append(pid)
                continue
            leer_.extend(suyos)
            if ss_:
                inv["sin_sesion"][rel(pc)] = ss_
            if fe:
                inv["entregables"][rel(pc)] = fe
            if tal:
                h_tal = hashlib.sha1(json.dumps(tal, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:12]
                huellas_taller[pid] = h_tal
                if TALLER_IGUAL.get(pid) == h_tal:
                    inv.setdefault("taller_reusar", []).append(rel(pc))     # el taller no cambió: sus piezas salen de la base
                else:
                    inv.setdefault("taller", {})[rel(pc)] = tal
            if sub_:
                inv.setdefault("entregables_sub", {})[rel(pc)] = sub_
    fuera_ = fuera_de_la_memoria()
    h_fuera = "f" + _huella_proyecto(_script, MODO, fuera_)[1:]
    huellas["meta/fuera"] = h_fuera
    if h_fuera in SIN_CAMBIOS:
        inv["fuera_reusar"] = True
    else:
        inv["fuera"] = fuera_
    # Huella de la raíz entera tal como la ve el tablero: cada archivo que lee con su tamaño y su fecha de modificación,
    # más lo que el inventario sabe de lo demás (fechas de entregables, trabajo sin sesión, «Claude outputs»), el día y este mismo script.
    # Si coincide con la que guardó la última sincronización, el tablero ya está al día y la puesta al día no tiene que regenerarlo.
    # Se calcula sobre la raíz entera, también con los proyectos que se reutilizan.
    todos = list(dict.fromkeys(leer_ + [r_ for suyos, _, _, _, _ in por_proyecto.values() for r_ in suyos]))
    _mt = sorted(f"{unicodedata.normalize('NFC', r)}\t{os.path.getsize(RAIZ / r)}\t{marca(RAIZ / r)}" for r in todos)
    _resto = {k: inv[k] for k in ("modo", "version_metodo", "motivos", "proyectos")}
    _resto["entregables"] = {p_: fe for p_, (_, fe, _, _, _) in por_proyecto.items() if fe}
    _resto["sin_sesion"] = {p_: ss for p_, (_, _, ss, _, _) in por_proyecto.items() if ss}
    _resto["taller"] = {p_: t_ for p_, (_, _, _, t_, _) in por_proyecto.items() if t_}
    _resto["entregables_sub"] = {p_: n_ for p_, (_, _, _, _, n_) in por_proyecto.items() if n_}
    _resto["fuera"] = fuera_
    inv["huella_raiz"] = hashlib.sha1(json.dumps([HOY, _script, _mt, _resto],
                                                 ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    leer_ = list(dict.fromkeys(leer_))       # un área repetida en guia.md no trae dos veces lo mismo
    inv["huella_leer"] = huella_copia({r: os.path.getsize(RAIZ / r) for r in leer_})
    inv["archivos_leer"] = len(leer_)
    inv["huellas"] = huellas
    if huellas_taller:
        inv["huellas_taller"] = huellas_taller
    if reusar:
        inv["reusar"] = reusar
    inv["sello"] = sello(inv)
    if SI_CAMBIA and SI_CAMBIA == inv["huella_raiz"]:
        # al día: la segunda línea es el instante de esta comprobación en la zona de la organización, que la puesta al día
        # deja como «sincronizado» (plan_subida.py --cierre); así ningún modelo escribe una hora
        print("AL DIA")
        print(datetime.datetime.now(TZ).isoformat(timespec="minutes"))
        sys.exit(0)
    if LINEAS:
        print(json.dumps(inv, ensure_ascii=False, separators=(",", ":")))
        print(len(leer_))
        print("\n".join(leer_))
    else:
        print(json.dumps({"leer": leer_, "inventario": inv}, ensure_ascii=False, separators=(",", ":")))
    sys.exit(0)

# ---------- segundo tiempo: la copia tiene que ser exactamente la de «leer» ----------
if INV is not None:
    if INV.get("sello") != sello(INV):
        sys.stderr.write("El inventario no llegó entero o se copió con algún cambio: vuelve a escribir la primera línea del paso del inventario, tal cual.\n")
        sys.exit(4)
    _copiados = {}
    for raiz_, dirs, files in os.walk(RAIZ):
        dirs[:] = [x for x in dirs if not x.startswith(".")]
        for f in files:
            if not f.startswith("."):
                _copiados[rel(os.path.join(raiz_, f))] = os.path.getsize(os.path.join(raiz_, f))
    if huella_copia(_copiados) != INV.get("huella_leer"):
        sys.stderr.write(f"La copia no coincide con el inventario: trae {len(_copiados)} archivos y el inventario pide {INV.get('archivos_leer')}, "
                         "o alguno llegó con otro tamaño. Espera unos segundos y repite; si sigue, vacía la carpeta de la copia y vuelve a traer los archivos.\n")
        sys.exit(3)

# ---------- lo que se reutiliza de la base: proyectos y carpetas sueltas que no cambiaron desde la última puesta al día ----------
def _de_la_base(col, doc):
    """El documento tal como lo dejó ArtifactData con out_dir (a veces envuelto en «data»), o None."""
    try:
        d = json.loads((PREVIOS / col / f"{doc}.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return None
    return d.get("data", d) if isinstance(d, dict) else None

REUSAR = set(INV.get("reusar", [])) if INV is not None else set()
previos = {}
if REUSAR or (INV is not None and INV.get("fuera_reusar")):
    faltan = []
    for pid in sorted(REUSAR):
        d_ = _de_la_base("proyectos", pid) if PREVIOS else None
        if not isinstance(d_, dict) or d_.get("id") != pid:
            faltan.append(pid); continue
        # lo que se partió al detalle (1.19) vuelve a su sitio, para partirlo abajo igual que un proyecto rehecho
        if any(d_.get(k) for k in ("sesiones_aparte", "estado_aparte", "que_hay_aparte")) or any(x.get("texto_aparte") for x in d_.get("decisiones") or []):
            det_ = _de_la_base("detalle", pid)
            if not isinstance(det_, dict):
                faltan.append(f"detalle/{pid}"); continue
            for x in d_.get("decisiones") or []:
                k_ = x.pop("texto_aparte", None)
                if k_:
                    x.update((det_.get("decisiones") or {}).get(k_) or {})
            if d_.pop("sesiones_aparte", None):
                d_["sesiones"] = (d_.get("sesiones") or []) + (det_.get("sesiones") or [])
            if d_.pop("estado_aparte", None):
                d_["estado_actual"] = det_.get("estado_actual") or ""
            if d_.pop("que_hay_aparte", None):
                d_["_que_hay_detalle"] = det_.get("que_hay") or {"piezas": [], "trayectoria": []}
        # fuera lo que sale de cruzarlo con los demás proyectos, que se vuelve a calcular abajo
        for k in ("huella", "cuestionamientos_abiertos"):
            d_.pop(k, None)
        for dec_ in d_.get("decisiones") or []:
            dec_.pop("cuestionado_por", None); dec_.pop("abierto", None)
        for s_ in d_.get("pasos") or []:
            s_.pop("desbloquea", None); s_.pop("puntos", None)
        previos[pid] = d_
    est_ = _de_la_base("meta", "estado") if PREVIOS else None
    if INV.get("fuera_reusar") and not (isinstance(est_, dict) and isinstance(est_.get("fuera"), list)):
        faltan.append("meta/estado (fuera)")
    if faltan:
        sys.stderr.write("La base no tiene lo que el inventario pide reutilizar (" + ", ".join(faltan[:5]) + "): "
                         "vuelve a sacar el inventario sin --sin-cambios y trae todo lo que pida.\n")
        sys.exit(5)
    FUERA_PREVIO = est_.get("fuera") if INV.get("fuera_reusar") else None

docs = {"meta": {}, "areas": {}, "proyectos": {}}
orden_area = 0
for a in areas_guia:
    orden_area += 1
    carpeta = RAIZ / a["slug"]
    texto = leer(carpeta / "area.md")
    area_doc = {
        "slug": a["slug"], "nombre": a["slug"], "que": a["que"], "dueno": a["dueno"],
        # quienes colaboran, por su cuenta: el tablero es de su dueño y no se comparte
        "colaboran": sorted(cuentas(a["cuenta"])[1]),
        "lectores": a["lectores"], "restringido": restringida_celda(a["lectores"]), "orden": orden_area,
        "prioridades": [], "actualizado": None, "legible": texto is not None, "proyectos": [],
    }
    if texto is None:
        area_doc["legible"] = False
        # por qué no se muestra. Lo que declara guia.md manda sobre lo que se ve en el disco: Drive no baja a la
        # computadora las carpetas que la cuenta no puede abrir, y un área restringida parecería «sin carpeta». Salvo
        # que el área sea de la cuenta que genera el tablero: entonces la puede leer, y lo que falta es la carpeta
        mia = bool(CUENTA_TABLERO) and CUENTA_TABLERO in set().union(*cuentas(a["cuenta"])[:2])
        area_doc["motivo"] = "restringido" if area_doc["restringido"] and not mia else motivo_de(carpeta / "area.md")
        if mia:
            area_doc["mio"] = True     # la página no le dice «pregunta a» a su propio dueño
        docs["areas"][a["slug"]] = area_doc
        continue
    fm, cuerpo = frontmatter(texto)
    area_doc["nombre"] = titulo_h1(cuerpo) or a["slug"]
    area_doc["actualizado"] = fm.get("actualizado")
    area_doc["prioridades"] = bullets(seccion(cuerpo, "Prioridades ahora"))
    area_doc["que_largo"] = seccion(cuerpo, "Qué es")
    pan = seccion(cuerpo, "Panorama").strip()
    mpan = re.match(r"^(20\d\d-\d\d-\d\d)\s*·\s*(.+)$", pan, re.S)
    area_doc["panorama"] = {"fecha": mpan.group(1), "texto": mpan.group(2).strip()} if mpan else ({"fecha": None, "texto": pan} if pan else None)
    indice = parse_indice_proyectos(cuerpo)
    slugs = proyectos_de(carpeta, indice)
    orden_p = 0
    for slug in slugs:
        orden_p += 1
        pc = carpeta / slug
        pid = f"{a['slug']}--{slug}"
        area_doc["proyectos"].append(pid)
        ref = indice.get(slug, {"descripcion": "", "entregables": {}, "notas": []})
        if pid in previos:
            # no cambió desde la última puesta al día: su documento de la base, con su orden de hoy
            pdoc = previos[pid]
            pdoc["orden"] = orden_p
            docs["proyectos"][pid] = pdoc
            continue
        tp = leer(pc / "proyecto.md")
        pdoc = {
            "id": pid, "area": a["slug"], "slug": slug, "nombre": slug, "orden": orden_p,
            "legible": tp is not None, "restringido": tp is None,
        }
        if tp is None:
            # su línea del índice del área es pública: se muestra sin la palabra «restringido», y si la lleva, el motivo
            # es ese aunque la carpeta no esté en la computadora (lo mismo que con un área). Que el área esté restringida
            # no cuenta: si se llegó a sus proyectos es que la cuenta lee su area.md. Y si el área es de la cuenta que
            # genera el tablero como dueña, lo restringido de dentro también lo lee (el dueño de un área lo es de lo
            # restringido dentro de ella; quien colabora, no necesariamente)
            linea = ref.get("descripcion", "")
            mia = bool(CUENTA_TABLERO) and CUENTA_TABLERO in cuentas(a["cuenta"])[0]
            declarado = bool(RE_RESTRINGIDA.match(linea)) and not mia
            linea = sin_palabra_restringido(linea) if RE_RESTRINGIDA.match(linea) else linea.strip()
            if linea:
                pdoc["descripcion"] = linea
            pdoc["motivo"] = "restringido" if declarado else motivo_de(pc / "proyecto.md")
            if mia:
                pdoc["mio"] = True
            docs["proyectos"][pid] = pdoc
            continue
        fm, cuerpo = frontmatter(tp)
        pdoc.update({
            "nombre": titulo_h1(cuerpo) or slug,
            "estado_cabecera": fm.get("estado"), "actualizado": fm.get("actualizado"),
            "objetivo": seccion(cuerpo, "Objetivo"),
            "terminado": seccion(cuerpo, "Terminado significa"),
            "alcance": seccion(cuerpo, "Alcance"),
            "quien": seccion(cuerpo, "Quién participa"),
            "estado_actual": seccion(cuerpo, "Estado actual"),
            "en_corto": seccion(cuerpo, "En corto"),
            "siguientes_pasos": lineas_no_vacias(seccion(cuerpo, "Siguientes pasos")),
        })
        pdoc["estado_resumen"] = primer_parrafo(pdoc["estado_actual"])
        pdoc["cerrado"] = bool(re.search(r"Proyecto terminado el\s*20\d\d-\d\d-\d\d", pdoc["estado_actual"]))
        mq = re.search(r"Dueño:\s*(.+)", pdoc["quien"])
        pdoc["dueno"] = mq.group(1).strip() if mq else a["dueno"]
        # los nombres, sin las cuentas: la cuenta solo sirve para saber quién escribe, y no sale en ningún tablero
        nombres_co = []
        for l in pdoc["quien"].split("\n"):
            if LINEA_COLABORA.match(l):
                resto = CORREO.sub("", re.sub(r"\([^)]*\)", "", LINEA_COLABORA.sub("", l, count=1)))
                nombres_co += [x.strip(" *-<>") for x in resto.split(",") if x.strip(" *-<>")]
        pdoc["colaboran"] = nombres_co
        mc = re.search(r"Consumen esto:\s*(.+)", pdoc["quien"])
        pdoc["consumen"] = mc.group(1).strip() if mc else ""
        pdoc.pop("quien", None)   # la sección en bruto lleva las cuentas de quien colabora: no viaja a la base
        ses = parse_sesiones(leer(pc / "sesiones.md"))
        reales = [s_ for s_ in ses if not es_sesion_de_tarea(s_["titulo"])]
        ultima_real = reales[0]["fecha"] if reales else None
        # pasos con fecha. Una fecha es plazo solo si el texto la trata como tal («antes del», «para el», al inicio
        # de la línea…); las que cuentan algo pasado («enviada el») son contexto y plazos_en ya las deja fuera.
        # Un plazo viejo no se descarta por viejo: está vencido, y eso es lo que el tablero tiene que enseñar.
        pasos = []
        for l in pdoc.pop("siguientes_pasos"):
            fs = plazos_en(l)
            texto = re.sub(r"^-\s*", "", l)
            cab = bool(re.match(r"^[A-Za-zÁÉÍÓÚáéíóúñÑ][^.]{0,30}:$", texto.strip()))
            p_ = {"texto": texto, "fecha": min(fs) if fs else None}
            if not cab:
                p_["naturaleza"] = naturaleza(texto)
                p_["temas"] = sorted(tokens_tema(texto))
                p_.update(senales(texto, area_doc, pdoc))
                if p_["naturaleza"] in ("rutina", "caducidad") and p_["fecha"]:
                    # una revisión periódica o una caducidad no vence: se revisa; el tablero la muestra aparte
                    p_["revisar"] = p_["fecha"]; p_["fecha"] = None
            pasos.append(p_)
        pdoc["pasos"] = pasos
        dec = parse_decisiones(leer(pc / "decisiones.md"))
        pdoc["decisiones_total"] = sum(1 for d_ in dec if d_.get("tipo") != "cuestionamiento")
        pdoc["decisiones"] = dec
        pdoc["sesiones_total"] = len(reales)   # las entradas «(tarea)» no son sesiones (contrato, sección 4)
        pdoc["sesiones_registro"] = len(ses)    # entradas del registro, con las «(tarea)»: lo que enseña la pestaña Bitácora
        # fechas de las sesiones de trabajo de los últimos 90 días (sin las de tarea): para la actividad por semana del tablero
        _lim = (datetime.date.fromisoformat(HOY) - datetime.timedelta(days=90)).isoformat()
        pdoc["sesiones_fechas"] = sorted({s["fecha"] for s in reales if fecha_valida(s["fecha"]) and s["fecha"] >= _lim}, reverse=True)
        pdoc["sesiones"] = ses[:5]
        pdoc["ultima_sesion"] = ultima_real
        # trabajo sin sesión: archivos que cambiaron después de la última entrada de la bitácora, sea de una
        # sesión o de una tarea que dejó su línea «(tarea)». Solo se mira la fecha de modificación, nunca el
        # contenido; proyecto.md no cuenta, porque la tarea del tablero lo toca al aplicar fechas, y restringido/ no se mira.
        ss_ = sin_sesion_de(pc, ses, pdoc["cerrado"])
        if ss_:
            pdoc["sin_sesion"] = ss_
        pdoc["entregables"] = entregables_de(pc, ref["entregables"])
        pdoc["entregables_vigentes"] = sum(1 for e in pdoc["entregables"] if e["estado"] == "vigente")
        pdoc["_sub"] = entregables_en_subcarpetas(pc)
        pdoc["que_hay"], pdoc["_que_hay_detalle"] = que_hay(pdoc, taller_de(pc), dec)
        pdoc.pop("_sub", None)
        docs["proyectos"][pid] = pdoc
    docs["areas"][a["slug"]] = area_doc

# ---------- cuestionamientos: quién cuestionó qué, y si el dueño ya respondió ----------
respuestas = set()
for pid, pdoc in docs["proyectos"].items():
    for d_ in pdoc.get("decisiones") or []:
        if d_.get("responde"):
            q, i = ref_decision(d_["responde"])
            if q: respuestas.add((q, i))
# una premisa nueva que reemplaza a P<n> responde a los cuestionamientos de P<n> anteriores a ella (contrato, sección 4)
reemplazos = {p_["reemplaza"]: p_["fecha"] for p_ in premisas if p_["reemplaza"]}
cuestionamientos = []
for pid, pdoc in docs["proyectos"].items():
    for d_ in pdoc.get("decisiones") or []:
        if d_.get("tipo") != "cuestionamiento":
            continue
        q, i = ref_decision(d_.get("cuestiona"))
        abierto = (pid, d_["id"]) not in respuestas
        if abierto and q == "premisa" and i in reemplazos and (reemplazos[i] or "9999") >= (d_["fecha"] or ""):
            abierto = False
        c = {"desde": pid, "id": d_["id"], "fecha": d_["fecha"], "titulo": d_["titulo"], "planteo": d_.get("planteo", ""),
             "porque": d_.get("porque", ""), "a_proyecto": q, "a_id": i, "abierto": abierto}
        d_["abierto"] = c["abierto"]
        cuestionamientos.append(c)
        if q and q != "premisa" and q in docs["proyectos"]:
            for t in docs["proyectos"][q].get("decisiones") or []:
                if t["id"] == i:
                    t.setdefault("cuestionado_por", []).append({k: c[k] for k in ("desde", "id", "fecha", "titulo", "planteo", "abierto")})
            if c["abierto"]:
                docs["proyectos"][q]["cuestionamientos_abiertos"] = docs["proyectos"][q].get("cuestionamientos_abiertos", 0) + 1
cuestionamientos.sort(key=lambda c: c["fecha"], reverse=True)

# ---------- grupos candidatos: pasos de proyectos distintos que comparten un tema ----------
por_tema = {}
for pid, pdoc in docs["proyectos"].items():
    if pdoc.get("cerrado") or not pdoc.get("legible"): continue
    for s_ in pdoc.get("pasos", []):
        if "naturaleza" not in s_: continue
        for t in s_["temas"]:
            por_tema.setdefault(t, []).append({"proyecto": pid, "paso": s_["texto"], "naturaleza": s_["naturaleza"]})
candidatos = []
for t, lista in por_tema.items():
    proys = {x["proyecto"] for x in lista}
    if len(lista) >= 2 and (len(proys) >= 2 or len(lista) >= 3):
        candidatos.append({"tema": t, "proyectos": sorted(proys), "pasos": lista})
candidatos.sort(key=lambda c: (-len(c["proyectos"]), -len(c["pasos"])))
# puntuación por paso: prioridad del área (3), cliente o dinero (2), desbloquea a otros proyectos (2)
temas_cruzados = {c["tema"] for c in candidatos if len(c["proyectos"]) >= 2}
for pid, pdoc in docs["proyectos"].items():
    for s_ in pdoc.get("pasos", []):
        if "naturaleza" not in s_: continue
        s_["desbloquea"] = bool(set(s_["temas"]) & temas_cruzados)
        pts = (3 if s_.get("prioridad_area") else 0) + (2 if s_.get("cliente_o_dinero") else 0) + (2 if s_["desbloquea"] else 0)
        if s_["naturaleza"] in ("rutina", "caducidad"): pts = 0
        s_["puntos"] = pts
# los candidatos no van a la base (la página no los lee): quedan en salida/meta/enfoque-candidatos.json para «Por dónde empezar»,
# con una huella de grupos y prioridades para saber si cambió algo desde la última vez sin releer nada
_prios = {s_: docs["areas"][s_].get("prioridades", []) for s_ in sorted(docs["areas"])}
_huella_cand = hashlib.sha1(json.dumps([candidatos[:25], _prios], ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]
enfoque_candidatos = {"generado": HOY, "huella": _huella_cand, "grupos": candidatos[:25]}

fuera = FUERA_PREVIO if (INV is not None and INV.get("fuera_reusar")) else fuera_de_la_memoria()

docs["meta"]["estado"] = {
    "organizacion": org, "snapshot": HOY, "sincronizado": datetime.datetime.now(TZ).isoformat(timespec="minutes"), "zona": str(TZ),
    "huella_candidatos": _huella_cand,     # la de «Por dónde empezar» que esta corrida ofreció: si no cambia, no se renueva
    "version_metodo": version_metodo, "contexto_comun": contexto_comun, "administra": administra,
    "areas": [a["slug"] for a in areas_guia], "tarea": TAREA, "tarea_manual": TAREA_MANUAL,
    "version_tablero": VERSION_PLUGIN, "modo": MODO,
    "fuera": [f for f in (fuera or []) if not f.get("guia")] + [{"carpeta": "guia.md", "archivos": 0, "de_claude": False, "guia": t} for t in guia_avisos],
    "premisas": premisas, "cuestionamientos": cuestionamientos,
}
# un tablero que era público pasa hoy a mostrarlo todo (1.18): la página lo avisa una semana. Solo se escribe el día del
# cambio; la subida de meta/estado es un update, así que la fecha se conserva en las puestas al día siguientes
_est_previo = _de_la_base("meta", "estado") if PREVIOS else None
if isinstance(_est_previo, dict) and _est_previo.get("modo") == "publico":
    docs["meta"]["estado"]["paso_a_completo"] = HOY
if INV is not None and INV.get("huella_raiz"):
    docs["meta"]["estado"]["huella_raiz"] = INV["huella_raiz"]
if INV is not None and INV.get("huellas"):
    # las huellas de cada proyecto y de lo que queda fuera: la próxima puesta al día las pasa con --sin-cambios.
    # Las de los documentos que la base rechazaría por tamaño no se guardan: no llegan a ella y no se pueden reutilizar.
    _gr = {pid for pid, d_ in docs["proyectos"].items()
           if len(json.dumps(d_, ensure_ascii=False, indent=1).encode("utf-8")) > LIMITE_DOC}
    docs["meta"]["estado"]["huellas"] = sorted({h for k, h in INV["huellas"].items() if k not in _gr})
if INV is not None and INV.get("huellas_taller"):
    docs["meta"]["estado"]["huellas_taller"] = {k: h for k, h in INV["huellas_taller"].items() if k in docs["proyectos"]}
if COLA_RETENIDA is not None:
    docs["meta"]["estado"]["cola_retenida"] = sorted(str(x) for x in COLA_RETENIDA)
if COLA_AJENA is not None:
    docs["meta"]["estado"]["cola_ajena"] = sorted(str(x) for x in COLA_AJENA)

# ---------- el detalle, aparte (1.19) ----------
# La página carga todos los proyectos al abrirse, y casi la mitad de lo que bajaba era texto que solo se lee al entrar
# en un proyecto. De cada proyecto se queda en «proyectos» lo que pintan el inicio, las listas y el resumen, y va a
# «detalle/<proyecto>», que la página trae al pedirlo: el porqué y los descartes de las decisiones que no son de las
# cinco más recientes (los cuestionamientos se quedan enteros), las sesiones de la bitácora menos la última, y el estado
# actual completo cuando el proyecto tiene «En corto» (sin él, el resumen lo enseña entero y se queda).
# Un proyecto reutilizado de la base (--sin-cambios) se vuelve a juntar con su detalle al leerlo, y se parte igual aquí.
DECISIONES_ENTERAS = 5
docs["detalle"] = {}
for pid, pd in docs["proyectos"].items():
    det, textos, n_ = {}, {}, 0
    for i, d_ in enumerate(pd.get("decisiones") or []):
        if d_.get("tipo") == "cuestionamiento":
            continue
        n_ += 1
        if n_ <= DECISIONES_ENTERAS:
            continue
        t_ = {c: d_.pop(c) for c in ("porque", "descartamos") if d_.get(c)}
        if t_:
            k = d_.get("id") or f"n{i}"
            textos[k] = t_; d_["texto_aparte"] = k
    if textos:
        det["decisiones"] = textos
    ses_ = pd.get("sesiones") or []
    if len(ses_) > 1:
        det["sesiones"] = ses_[1:]; pd["sesiones"] = ses_[:1]; pd["sesiones_aparte"] = len(ses_) - 1
    ea = (pd.get("estado_actual") or "").strip()
    if pd.get("en_corto") and len(ea) > len((pd.get("estado_resumen") or "").strip()) + 20:
        det["estado_actual"] = pd.pop("estado_actual"); pd["estado_aparte"] = True
    qh = pd.pop("_que_hay_detalle", None)
    if qh and (qh["piezas"] or qh["trayectoria"]):
        det["que_hay"] = qh; pd["que_hay_aparte"] = True
    if det:
        docs["detalle"][pid] = det

# ---------- escribir ----------
# Cada documento lleva una huella de su contenido (sin la hora de sincronización) para que la puesta al día
# suba solo los que cambiaron; indice.json lista cada archivo con su huella y su tamaño.
def huella(data):
    sin = {k: v for k, v in data.items() if k not in ("sincronizado", "huella", "huella_raiz", "huellas", "huellas_taller", "cola_retenida", "cola_ajena")}
    return hashlib.sha1(json.dumps(sin, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]
indice_archivos = []
for col, items in docs.items():
    for did, data in items.items():
        data["huella"] = huella(data)
        d = OUT / col
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"{did}.json"
        p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        indice_archivos.append({"coleccion": col, "doc_id": did, "archivo": str(p.relative_to(OUT)), "huella": data["huella"], "bytes": p.stat().st_size})
(OUT / "meta").mkdir(parents=True, exist_ok=True)
(OUT / "meta" / "enfoque-candidatos.json").write_text(json.dumps(enfoque_candidatos, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "indice.json").write_text(json.dumps(indice_archivos, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(docs['areas'])} áreas, {len(docs['proyectos'])} proyectos, snapshot {HOY}")
