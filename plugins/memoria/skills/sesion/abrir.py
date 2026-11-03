#!/usr/bin/env python3
"""Lo que hay que leer para abrir una sesión, en una sola llamada y sin escribir nada.

Uso: abrir.py <raiz> [<area>/<proyecto>] [--cuenta <correo>] [--plugin "<primera línea del metodo.md del plugin>"] [--sin-fechas [--listado <archivo>] [--outputs <archivo>]] [--minima] [--origen "<ruta de la raíz en la computadora>"]

Con --origen (la ruta de la raíz que da get_device_info) y la cuenta del administrador principal, si la raíz vive en
Google Drive imprime en CUENTA la línea PERMISOS, para ofrecer la revisión de permisos al abrir (1.24.2).

Con --minima (la apertura mínima, la primera respuesta de cualquier conversación con la carpeta conectada) imprime solo
la primera línea de metodo.md con su veredicto, el nombre de la organización, la cuenta, una línea por proyecto de cada
área legible (de un área restringida, solo si es de la cuenta) y los archivos sueltos en «Claude outputs», con su fecha:
sin guia.md entero, sin premisas y sin proyecto activo aunque se pase uno. Lo suelto en «Claude outputs» sale en todos los
modos, al final, también al abrir un proyecto, porque la primera respuesta de la conversación lo dice siempre.

Sin proyecto imprime el nivel 0 (primera línea de metodo.md, guia.md, premisas vigentes) y la lista de proyectos de
cada área legible, para saber cuál se abre. Con proyecto añade el nivel 1 (el bloque Proyectos de su área, proyecto.md,
las cinco decisiones y las tres sesiones más recientes, las cabeceras de entregables/) y los avisos de apertura:
cuestionamientos abiertos, decisiones de otros proyectos que lo nombran en «Afecta a:», entregables desfasados o en
borrador viejo, trabajo sin sesión y la fecha de base/contexto.md. Con --cuenta dice qué áreas son de esa cuenta y,
si es la del responsable de contexto, también los cuestionamientos a premisas. Con --plugin compara la versión y la
huella del metodo.md de la raíz con las del plugin, en numérico («1.14.10» es mayor que «1.14.9»), y dice el veredicto:
RAIZ ATRASADA (se copia el del plugin), AL DIA, PLUGIN ATRASADO (no se copia nada y se avisa) o MISMA VERSION, HUELLA
DISTINTA (no se toca). La comparación la hace el script, no quien lo lee.

Nunca abre taller/, fuentes/, restringido/ ni base/ (salvo premisas.md y la cabecera de contexto.md; de taller/ y fuentes/
del proyecto activo solo mira fechas), ni las sesiones de otros proyectos, ni los proyectos que no están en el índice de su
área (salvo el activo). De las demás decisiones solo mira las líneas «Afecta a:», «Cuestiona a:» y «Responde a:»
y la cabecera de su entrada. Lo restringido no sale salvo que el proyecto activo esté dentro, y lo que no se deja leer
se cuenta, sin suponer qué hay.

Con --sin-fechas corre sobre una copia en el contenedor (sesión sin consola: la copia la arma espejo.py y sus fechas de
archivo son las de la copia, no las de la computadora). No usa ninguna fecha de archivo: no da el aviso de trabajo sin sesión
por fechas, sino el instante desde el que hay que mirarlo en el listado de la computadora (device_list_dir, mtimeMs), y en
REGISTROS solo da el tamaño. Con --listado <archivo> (el resultado de device_list_dir recursivo de la carpeta del
proyecto, guardado tal cual en un archivo del contenedor) calcula él el aviso de trabajo sin sesión, con fecha y hora en la
zona de la organización, como en la computadora: nadie compara milisegundos a mano. Con --outputs <archivo> (el
device_list_dir recursivo de «Claude outputs», guardado igual) da lo suelto ahí con sus fechas, como con consola. Con
--sin-fechas y la raíz atrasada, deja el metodo.md del plugin en una carpeta nueva de salidas del contenedor y la RESPUESTA
dice con qué device_commit_files escribirlo: es lo único que escribe, y fuera de la raíz (1.24.9).

La apertura mínima corre siempre así, en el contenedor sobre una copia (1.24.9): en la computadora no se ejecuta nada
descargado, que el modo Auto de la app frena cuando la petición no tiene que ver con la memoria.
"""
import datetime, json, os, pathlib, re, sys, time

RAIZ = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
RAIZ_RESUELTA = False
if RAIZ is not None and not (RAIZ / "guia.md").is_file():
    # la ruta que da get_device_info (/Users/…/Carpeta) no existe en esta consola, donde la carpeta cuelga de $HOME/mnt con
    # su último tramo como nombre: se resuelve aquí para que un error de ruta no cueste dos llamadas más
    _mnt = pathlib.Path(os.path.expanduser("~")) / "mnt"
    _raices = [d for d in (sorted(_mnt.glob("*")) if _mnt.is_dir() else []) if (d / "guia.md").is_file() and (d / "metodo.md").is_file()]
    _cand = [d for d in _raices if d.name == RAIZ.name or d.name.endswith("--" + RAIZ.name)] or (_raices if len(_raices) == 1 else [])
    if _cand:
        sys.argv[1] = str(_cand[0]); RAIZ = _cand[0]; RAIZ_RESUELTA = True
    elif len(_raices) > 1:
        sys.exit("Esa ruta no existe en esta consola y hay varias raíces bajo $HOME/mnt: " + ", ".join(d.name for d in _raices) + ". Pasa la de $HOME/mnt/<nombre>.")
if RAIZ is not None and not (RAIZ / "guia.md").is_file() and len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
    # lo que la apertura necesita saber, en una línea que se reconoce (1.24.8): la conversación no tiene que comprobar antes
    # si la carpeta es una raíz ni si la consola la ve
    _mnt = pathlib.Path(os.path.expanduser("~")) / "mnt"
    _monta = _mnt.is_dir() and any(d.name == RAIZ.name or d.name.endswith("--" + RAIZ.name) for d in _mnt.glob("*"))
    if _monta or RAIZ.is_dir():
        print(f"NO ES RAIZ: {RAIZ.name} no tiene guia.md y metodo.md en su primer nivel. No es una memoria: no se dice nada de esto.")
    else:
        print(f"SIN CONSOLA: esta consola no ve {RAIZ.name}. Si la carpeta es una memoria, se trabaja como dice el anexo sin-consola-sesion.md de la skill sesion; "
              "se sabe trayendo guia.md y metodo.md con device_stage_files.")
    sys.exit(0)
if RAIZ is None or not (RAIZ / "guia.md").is_file():
    sys.exit("Uso: abrir.py <raiz> [<area>/<proyecto>] [--cuenta <correo>] [--plugin \"<primera línea del metodo.md del plugin>\"] [--sin-fechas [--listado <archivo>]] [--minima] [--origen \"<ruta de la raíz en la computadora>\"]  (la raíz es la carpeta con guia.md y metodo.md: en esta consola, la de $HOME/mnt/ cuyo nombre es el último tramo de la ruta que da get_device_info)")
args = [a for a in sys.argv[2:]]
CUENTA = None
if "--cuenta" in args:
    i = args.index("--cuenta"); CUENTA = (args[i + 1] if i + 1 < len(args) else "").strip().lower(); del args[i:i + 2]
PLUGIN = None
if "--plugin" in args:
    i = args.index("--plugin"); PLUGIN = (args[i + 1] if i + 1 < len(args) else "").strip(); del args[i:i + 2]
MINIMA = "--minima" in args
if MINIMA:
    args.remove("--minima")
SIN_FECHAS = "--sin-fechas" in args
if SIN_FECHAS:
    args.remove("--sin-fechas")
ORIGEN = None
if "--origen" in args:
    i = args.index("--origen"); ORIGEN = (args[i + 1] if i + 1 < len(args) else "").strip(); del args[i:i + 2]
OUTPUTS, OUTPUTS_CORTADO = None, [False]
if "--outputs" in args:
    # el device_list_dir recursivo de «Claude outputs» guardado tal cual: sin consola, la copia no trae esa carpeta (1.24.9)
    i = args.index("--outputs"); OUTPUTS = args[i + 1] if i + 1 < len(args) else None; del args[i:i + 2]
LISTADO = None
if "--listado" in args:
    i = args.index("--listado"); LISTADO = args[i + 1] if i + 1 < len(args) else None; del args[i:i + 2]
ACTIVO = args[0].strip("/") if args and not MINIMA else None
ZONA_AVISO = None
VEREDICTO, VERSION_RAIZ, VERSION_PLUGIN = None, None, None
PERMISOS = False
DECIR = []          # «aviso para decirlo» de CUENTA: una fila del recuadro cada uno (1.24.8)
_LEIDOS = {}


def en_drive(origen):
    """Si la ruta de la raíz en la computadora (la de get_device_info) es de Google Drive para escritorio: en Mac, bajo
    Library/CloudStorage/GoogleDrive-… o /Volumes/GoogleDrive; en Mac y Windows, con una carpeta «Google Drive», «My Drive»
    o su nombre en otro idioma, o la de las unidades compartidas («G:/Mi unidad/…» entra por ahí). Una letra de unidad sola
    no lo dice (D: puede ser un disco o un USB), ni una carpeta de iCloud, Dropbox, OneDrive o Box sin esos nombres."""
    o = (origen or "").replace("\\", "/")
    return bool(re.search(r"/Library/CloudStorage/GoogleDrive-|^/Volumes/GoogleDrive(/|$)|/Google Drive(/|$)|"
                          r"/(My Drive|Mi unidad|Meu Drive|Mon Drive|Meine Ablage|Il mio Drive|Mijn Drive|"
                          r"Shared drives|Unidades compartidas|Drives partilhados|Drives partagés|Geteilte Ablagen|Drive condivisi)(/|$)", o, re.I))


def zona_horaria(raiz, defecto="America/Mexico_City"):
    """La zona de la organización: la línea «Zona horaria: Europe/Madrid» de guia.md (con viñeta, negrita o comillas
    invertidas, y UTC o Etc/GMT+5), si la hay; si no, Ciudad de México. Una zona que no vale se avisa en ZONA_AVISO."""
    global ZONA_AVISO
    try:
        _g = (raiz / "guia.md").read_bytes().decode("utf-8-sig", errors="replace").replace("\r\n", "\n")
        _LEIDOS[str(raiz / "guia.md")] = _g      # la misma lectura que después hace leer(): guia.md se lee una vez
        m = re.search(r"^\s*[-*]?\s*\**\s*zona horaria\s*\**\s*:\s*\**\s*`?\s*([A-Za-z0-9_+-]+(?:/[A-Za-z0-9_+-]+){0,2})", _g, re.M | re.I)
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
TZ = zona_horaria(pathlib.Path(sys.argv[1]))
HOY = datetime.datetime.now(TZ).date()
FECHA = re.compile(r"\b(20\d\d-\d\d-\d\d)\b")


def fecha_ok(f):
    try:
        datetime.date.fromisoformat(f); return True
    except (TypeError, ValueError):
        return False
no_legibles = []


def leer(p):
    """El texto de p, una sola vez por apertura: guia.md, los area.md y decisiones.md se piden en varios pasos, y en una
    carpeta de Drive cada lectura es una descarga (1.22.2). Lo que no se deja leer se cuenta, sin suponer qué hay."""
    k = str(p)
    if k not in _LEIDOS:
        try:
            _LEIDOS[k] = pathlib.Path(p).read_bytes().decode("utf-8-sig", errors="replace").replace("\r\n", "\n")
        except FileNotFoundError:
            _LEIDOS[k] = None
        except OSError:
            no_legibles.append(rel(p))   # sin permiso o sin descargar
            _LEIDOS[k] = None
    return _LEIDOS[k]


def rel(p):
    try:
        return pathlib.Path(p).relative_to(RAIZ).as_posix()
    except ValueError:
        return str(p)


def cabecera(texto):
    m = re.match(r"^---\n(.*?)\n---\n?", texto or "", re.S)
    fm, ultima = {}, None
    if not m:
        return fm, texto or ""
    for l in m.group(1).split("\n"):
        mm = re.match(r"^(\w+):\s*(.*)$", l)
        if mm:
            ultima = mm.group(1); v = mm.group(2).strip()
            fm[ultima] = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()] if v.startswith("[") and v.endswith("]") else v.strip("'\"")
        elif ultima and re.match(r"^\s+-\s+", l):
            if not isinstance(fm.get(ultima), list):
                fm[ultima] = []
            fm[ultima].append(re.sub(r"^\s+-\s+", "", l).strip().strip("'\""))
    return fm, texto[m.end():]


def seccion(texto, nombre):
    m = re.search(r"^## " + re.escape(nombre) + r"\s*\n(.*?)(?=^## |\Z)", texto or "", re.S | re.M)
    return m.group(1).strip() if m else ""


def entradas(texto):
    """Las entradas «## …» de un registro, en el orden del archivo, con su fecha."""
    out = []
    partes = re.split(r"^(?=## )", texto or "", flags=re.M)
    for p in partes:
        if not p.startswith("## "):
            continue
        cab = p.split("\n", 1)[0]
        f = FECHA.search(cab)
        fecha = f.group(1) if f and fecha_ok(f.group(1)) else ""   # una fecha inválida (2026-13-45) es como no tenerla
        out.append({"fecha": fecha, "cab": cab[3:].strip(), "texto": p.rstrip()})
    return out


def recientes(texto, n):
    es = entradas(texto)
    return sorted(es, key=lambda e: e["fecha"], reverse=True)[:n]   # sin fecha válida, al final




def hora_de(p):
    """«HH:MM» de la modificación de p en la zona de la organización, o «»."""
    try:
        return "" if SIN_FECHAS else datetime.datetime.fromtimestamp(os.stat(p).st_mtime, TZ).strftime("%H:%M")
    except OSError:
        return ""


def mtime(p):
    if SIN_FECHAS:   # en la copia, la fecha de archivo es la de la copia: no dice nada
        return None
    try:
        return datetime.datetime.fromtimestamp(os.stat(p).st_mtime, TZ).date()   # el día en la zona de la organización, como el tablero
    except OSError:
        return None


def titulo(n):
    print(f"\n=== {n}")


# --- quién escribe: «Quién es quién» y la tabla de áreas de guia.md, y la línea «Colabora:» de un proyecto ---
# La misma función en abrir.py, cerrar.py, permisos.py, migrar_estructura.py, aplicar_cambios.py, barrido.py,
# generar_vista.py y verificar.sh (cada uno se descarga suelto); pruebas/sesion/probar_cuentas.py comprueba que las
# ocho copias son idénticas. Desde la 1.25 cada persona está una vez en «Quién es quién» («Nombre · cuenta@») y la tabla
# de áreas la nombra por su nombre en Responsable y Colabora; hasta la 1.24, la celda Cuenta llevaba los correos. Se
# leen las dos formas: con registro y columna Colabora, por nombre; sin ellos, la celda Cuenta como siempre.
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
    """Cómo se comparan dos nombres: NFC (Mac y Windows escriben las tildes distinto), sin mayúsculas, sin negritas ni
    comillas, y con los espacios juntos. Nada más: sin acentos no es el mismo nombre."""
    n = unicodedata.normalize("NFC", n or "").replace(" ", " ")
    return re.sub(r"\s+", " ", re.sub(r"[*_`«»\"]", "", n)).strip(" .,;:").lower()
def registro_personas(guia):
    """«Quién es quién» de guia.md: {"hay", "personas", "nombre": {clave: persona}, "cuenta": {correo: persona}, "avisos"}.
    Una línea es «- Nombre · campo · campo»; los campos: un correo (su cuenta de Claude), «cuentas: a@, b@», «en Drive: x@»,
    «sin cuenta», «sin confirmar», «también: Otra Grafía», «de: Organización», «baja AAAA-MM-DD», «compartida con: Nombre»
    y «registra: Nombre». «?» como nombre es una cuenta que todavía no tiene nombre. Quien está de baja no escribe."""
    m = re.search(r"^##\s+Quién es quién\s*$(.*?)(?=^##\s|\Z)", guia or "", re.M | re.S)
    reg = {"hay": bool(m), "personas": [], "nombre": {}, "cuenta": {}, "avisos": []}
    for l in (m.group(1) if m else "").split("\n"):
        if not re.match(r"^\s*[-*]\s+\S", l):
            continue
        campos = [c.strip() for c in re.split(r"\s+·\s+|\s*·\s*", l.strip()[1:].strip()) if c.strip()]
        if not campos:
            continue
        p = {"nombre": re.sub(r"[*_`]", "", campos[0]).strip(), "cuentas": set(), "drive": set(), "sin_cuenta": False,
             "sin_confirmar": False, "alias": [], "de": "", "baja": "", "compartida": "", "registra": "", "linea": l.strip()}
        if CORREO.fullmatch(p["nombre"].lower()):
            p["cuentas"].add(p["nombre"].lower()); p["nombre"] = "?"
        for c in campos[1:]:
            cl = c.lower()
            if CORREO.fullmatch(cl):
                p["cuentas"].add(cl)
            elif re.match(r"^cuentas?\s*:", cl):
                p["cuentas"] |= set(CORREO.findall(cl))
            elif re.match(r"^(en\s+)?(google\s+)?drive\s*:", cl):
                p["drive"] |= set(CORREO.findall(cl))
            elif re.match(r"^sin\s+cuenta\b", cl):
                p["sin_cuenta"] = True
            elif re.match(r"^sin\s+confirmar\b", cl):
                p["sin_confirmar"] = True
            elif re.match(r"^tambi[eé]n\s*:", cl):
                p["alias"] += [a.strip() for a in re.split(r",|\s+y\s+", c.split(":", 1)[1]) if a.strip()]
            elif re.match(r"^de\s*:", cl):
                p["de"] = c.split(":", 1)[1].strip()
            elif re.match(r"^baja\b", cl):
                p["baja"] = (re.search(r"20\d\d-\d\d-\d\d", c) or [""])[0] or "sí"
            elif re.match(r"^compartida\s+con\s*:", cl):
                p["compartida"] = c.split(":", 1)[1].strip()
            elif re.match(r"^registra\s*:", cl):
                p["registra"] = c.split(":", 1)[1].strip()
            else:
                reg["avisos"].append(f"«{p['nombre']}»: no se entiende «{c}» (van un correo, «sin cuenta», «en Drive: correo», «también: nombre», «de: organización» o «baja AAAA-MM-DD»)")
        if p["sin_cuenta"] and p["cuentas"]:
            reg["avisos"].append(f"«{p['nombre']}» dice «sin cuenta» y lleva una cuenta: se queda la cuenta")
            p["sin_cuenta"] = False
        if not p["cuentas"] and not p["sin_cuenta"] and not p["de"]:
            reg["avisos"].append(f"«{p['nombre']}» no lleva ni su cuenta ni «sin cuenta»")
        reg["personas"].append(p)
        for n in ([p["nombre"]] if p["nombre"] != "?" else []) + p["alias"]:
            k = clave_nombre(n)
            if k in reg["nombre"] and reg["nombre"][k] is not p:
                reg["avisos"].append(f"«{n}» está dos veces: dos personas con el mismo nombre se distinguen con el segundo apellido o una inicial")
            reg["nombre"].setdefault(k, p)
        for c in p["cuentas"]:
            if c in reg["cuenta"]:
                reg["avisos"].append(f"la cuenta {c} está en dos líneas («{reg['cuenta'][c]['nombre']}» y «{p['nombre']}»)")
            reg["cuenta"].setdefault(c, p)
    return reg
def persona(nombre, reg):
    """La persona del registro con ese nombre o alias; None si no está."""
    return (reg or {}).get("nombre", {}).get(clave_nombre(re.sub(r"\s*\([^)]*\)", "", nombre or "")))
def nombres_de(texto):
    """Los nombres de una celda o una línea («Colabora: Ana Ruiz, Luis Mejía»): separados por comas, «;» o « y », sin
    la etiqueta del principio ni lo que va entre paréntesis."""
    t = re.sub(r"^\s*[-*]?\s*\**\s*(?:colabora[n]?|lo leen?|responsable)\s*\**\s*:\s*\**", "", texto or "", flags=re.I)
    t = re.sub(r"\s*\([^)]*\)", "", t)
    return [n.strip(" .*") for n in re.split(r",|;|\s+y\s+", t) if n.strip(" .*") and n.strip(" .*").lower() not in ("—", "-", "nadie", "ninguno", "ninguna")]
def cuentas_de_nombres(texto, reg):
    """(cuentas, nombres que no están en el registro) de una celda con nombres. Quien está de baja o sin cuenta no da
    ninguna; un correo escrito tal cual («Nombre (correo)», el alta provisional de un proyecto) cuenta."""
    out, faltan = set(CORREO.findall((texto or "").lower())), []
    for n in nombres_de(texto):
        p = persona(n, reg)
        if p is None:
            if not CORREO.fullmatch(n.lower()):
                faltan.append(n)
        elif not p["baja"]:
            out |= p["cuentas"]
    return out, faltan
def columnas_personas(cab):
    """Dónde están Responsable, Cuenta y Colabora en el encabezado de la tabla de áreas (None si no están)."""
    n = [re.sub(r"[*_`]", "", x).strip().lower() for x in cab]
    pos = lambda *ns: next((i for i, x in enumerate(n) if x in ns), None)
    return {"responsable": pos("responsable", "dueño", "dueno"), "cuenta": pos("cuenta"), "colabora": pos("colabora", "colaboran")}
def fila_cuentas(cab, celdas, reg):
    """(responsable, colaboran, aviso) de una fila de la tabla de áreas, como cuentas(): con la columna Cuenta (hasta la
    1.24), de sus correos; con la columna Colabora y «Quién es quién» (1.25), por los nombres. Sin encabezado reconocible,
    la cuarta columna como Cuenta, como siempre. Falla cerrado: un responsable que no está en el registro no es nadie."""
    col = columnas_personas(cab)
    if col["cuenta"] is not None or col["colabora"] is None:
        i = col["cuenta"] if col["cuenta"] is not None else 3
        return cuentas(celdas[i] if i < len(celdas) else "")
    if not (reg or {}).get("hay"):
        return set(), set(), "la tabla nombra a quien colabora por su nombre y guia.md no tiene «Quién es quién»"
    resp = celdas[col["responsable"] if col["responsable"] is not None else 2] if len(celdas) > 2 else ""
    rn = nombres_de(re.sub(r"\s*\((?=[a-záéíóúñ`])[^)]*\)", "", resp))
    avisos = []
    de = set()
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
    co, faltan = cuentas_de_nombres(celdas[col["colabora"]] if col["colabora"] < len(celdas) else "", reg)
    avisos += [f"«{n}» (Colabora) no está en «Quién es quién»" for n in faltan]
    return de, co - de, "; ".join(avisos) or None
def cuentas_contexto(linea, reg):
    """Las cuentas de quien responde por el contexto: la que va entre paréntesis en «Contexto común: Nombre (correo)»
    (hasta la 1.24) o la del registro para ese nombre (1.25)."""
    t = (linea or "").split(":", 1)[-1]
    c = set(CORREO.findall(t.lower()))
    if c:
        return c
    p = persona(t.strip().rstrip("."), reg)
    return set(p["cuentas"]) if p and not p["baja"] else set()
def nombre_de(cuenta, reg):
    """El nombre del registro de esa cuenta, o "" si no está (o es «?»)."""
    p = (reg or {}).get("cuenta", {}).get((cuenta or "").lower())
    return p["nombre"] if p and p["nombre"] != "?" else ""
def colaboran_en(quien, reg=None):
    """Las cuentas de las líneas «Colabora:» de «Quién participa» de un proyecto (todas las líneas): los correos escritos
    tal cual y, con registro, las de los nombres."""
    out = set()
    for l in (quien or "").split("\n"):
        if LINEA_COLABORA.match(l):
            out |= cuentas_de_nombres(l, reg)[0] if reg else set(CORREO.findall(l.lower()))
    return out
# --- fin de quién escribe ---
# --- el primer párrafo de guia.md sin lo que habla de la carpeta ---
# La misma función en abrir.py y en generar_vista.py (cada uno se descarga suelto); pruebas/tablero/paridad.py comprueba
# que las dos copias son idénticas y dan lo mismo (1.23; antes vivía dentro de cada script, fuera de la comprobación).
SOBRE_LA_CARPETA = r"`(?:metodo|guia)\.md`|plugin `memoria`|Aquí solo está lo nuestro"
def sin_carpeta(frases, rx=SOBRE_LA_CARPETA):
    """Las frases del primer párrafo de guia.md sin lo que habla de la carpeta o del método; de una frase unida con «;» a
    otra que no habla de ellos, se queda la otra (1.22.5), y no se parte por un «;» entre paréntesis. Dentro de cada parte,
    se queda lo que va antes de la coma, los dos puntos o la raya que abre lo de la carpeta, si es una frase de tres palabras
    o más: «Acme fabrica muebles, como dice `guia.md`» deja «Acme fabrica muebles» (1.24.8)."""
    out = []
    for f in frases:
        if not re.search(rx, f):
            out.append(f); continue
        quedan = []
        for c in [c.strip() for c in re.split(r";(?![^()]*\))", f)]:
            m = re.search(rx, c) if c else None
            if c and not m:
                quedan.append(c); continue
            cortes = [s.start() for s in re.finditer(r"[,:—](?![^()]*\))", c[:m.start()] if m else "")]
            t = c[:cortes[-1]].strip() if cortes else ""
            if len(t.split()) >= 3 and not re.search(rx, t):
                quedan.append(t)
        if quedan:
            t = "; ".join(quedan); t = t[0].upper() + t[1:]
            out.append(t if t[-1] in ".!?" else t + ".")
    return out
# --- fin del primer párrafo ---
# --- los registros con sus archivados ---
# La misma función en abrir.py, generar_vista.py y barrido.py (cada uno se descarga suelto); pruebas/tablero/paridad.py
# comprueba que las tres copias son idénticas (1.23).
ARCHIVADO = re.compile(r"^(sesiones|decisiones)-(20\d\d)(?:-(\d+))?\.md$")
def archivados_de(carpeta, nombre, anio):
    """Los nombres de los archivados de un registro («sesiones» o «decisiones») de este año y del anterior, del más nuevo
    al más viejo. Los de años anteriores no se leen: lo que una decisión vieja sostiene ya está en Alcance o en el Estatus,
    y quien la cita la busca por el año que lleva su identificador."""
    vistos = []
    try:
        nombres = [x.name for x in pathlib.Path(carpeta).iterdir()]
    except OSError:
        nombres = []
    for n in nombres:
        m = ARCHIVADO.match(n)
        if m and m.group(1) == nombre and int(m.group(2)) >= int(anio) - 1:
            vistos.append((int(m.group(2)), int(m.group(3) or 1), n))
    return [n for _, _, n in sorted(vistos, reverse=True)]
def con_archivados(carpeta, nombre, vivo, anio, leer_):
    """(texto, entradas del vivo): el registro vivo seguido de las entradas de sus archivados recientes, como si no se
    hubiera archivado, así que los identificadores de cada decisión son los de siempre. Lo que no se deja leer se salta."""
    partes = [vivo or ""]
    for n in archivados_de(carpeta, nombre, anio):
        t = leer_(pathlib.Path(carpeta) / n) or ""
        m = re.search(r"^## ", t, re.M)
        if m:
            partes.append(t[m.start():])
    return "\n\n".join(p.strip("\n") for p in partes if p.strip()) + "\n", len(re.findall(r"^## ", vivo or "", re.M))
def respuestas_viejas(carpeta, anio, leer_):
    """Las líneas «Responde a:» de los archivados de decisiones de antes del año anterior, que no se leen enteros: un
    cuestionamiento respondido hace años sigue respondido (revisión de la 1.23, hallazgo 5). Es un patrón de línea."""
    recientes = set(archivados_de(carpeta, "decisiones", anio))
    out = []
    for n in archivados_de(carpeta, "decisiones", 0):
        if n not in recientes:
            out += re.findall(r"^Responde a:[ \t]*(.+)$", leer_(pathlib.Path(carpeta) / n) or "", re.M)
    return out
# --- fin de los registros ---
# --- el administrador principal: una sola persona (1.22.2) ---
# La misma función en abrir.py y permisos.py (cada uno se descarga suelto); pruebas/sesion/probar_permisos.py comprueba
# que las dos copias son idénticas. Recibe el texto de «Quién responde por qué» y {nombre en minúscula: cuentas} de la
# tabla de áreas, y dice si quien administra la carpeta y quien responde por el contexto son la misma persona.
def administrador_unico(quien, por_nombre):
    """(veredicto, adm, ctx): «una», «dos» o «no se sabe» (un lado trae solo un nombre que no está en la tabla y el otro
    una cuenta: no se afirma nada). Dos correos de la misma persona («En Drive: a@claude es a@drive») cuentan como una."""
    ctx, adm, en_drive = "", "", ""
    for l in (quien or "").split("\n"):
        s = l.strip().lstrip("-* ").strip()
        if s.lower().startswith("contexto común"):
            ctx = s.split(":", 1)[-1].strip().rstrip(".").strip()
        elif s.lower().startswith("administra"):
            adm = s.split(":", 1)[-1].strip().rstrip(".").strip()
        elif re.match(r"^(en\s+)?(google\s+)?drive\s*:", s, re.I):
            en_drive = s.split(":", 1)[-1]
    misma = {}
    for par in re.split(r"[,;·]|\s+y\s+", en_drive.lower()):
        cs = CORREO.findall(par)
        if len(cs) == 2:
            misma[cs[1]] = cs[0]
    def personas(linea):
        """(cuentas, nombres) de una línea: las cuentas que trae o que la tabla da a sus nombres, y los nombres que la
        tabla reconoce; si no reconoce ninguno, el primer tramo antes de una coma o un punto («Ana Prueba, de forma
        provisional. Hoy vive…» es Ana Prueba), que es donde va el nombre."""
        cuentas, nombres = {misma.get(c, c) for c in CORREO.findall(linea.lower())}, []
        tramos = [n.strip().rstrip(".").strip() for n in re.split(r",|\by\b|\be\b|·|;", re.sub(r"\([^)]*\)", "", linea))]
        for n in tramos:
            if n.lower() in por_nombre:
                nombres.append(n.lower()); cuentas |= {misma.get(c, c) for c in por_nombre[n.lower()]}
        if not nombres:
            n = re.split(r"\.\s", tramos[0] if tramos else "")[0].strip().lower()
            if n and not CORREO.fullmatch(n) and len(n.split()) >= 2:
                nombres.append(n)
        return cuentas, nombres
    ca, na = personas(adm); cc, nc = personas(ctx)
    if not adm or not ctx:
        return "no se sabe", adm, ctx
    if len(ca) > 1 or len(na) > 1:
        return "dos", adm, ctx
    if ca and cc:
        return ("una" if ca & cc else "dos"), adm, ctx
    if na and nc:
        return ("una" if na == nc else "dos"), adm, ctx
    return "no se sabe", adm, ctx
# --- fin del administrador principal ---
def restringida_celda(celda):
    """«Quién la lee» declara el área restringida: la palabra al inicio («Restringida: …», «Restringido a …»), o
    «restringida» como palabra suelta en otra parte de la celda («Dirección (restringida)») sin negarla («nunca
    restringida», «antes restringida»). «Los proyectos restringidos aparte» no la declara. Igual en abrir.py,
    generar_vista.py y vista.html (restringidaCelda)."""
    c = celda or ""
    if re.match(r"^[\W_]*restringid[oa]s?\b", c, re.I):
        return True
    return bool(re.search(r"\brestringidas?\b", c, re.I)) and not re.search(r"\b(?:nada|no|nunca|sin|antes)\s+(?:[^\s]+\s+)?restringid", c, re.I)


# ---------- nivel 0 ----------
try:
    with open(RAIZ / "metodo.md", encoding="utf-8-sig", errors="replace") as f_:
        linea_metodo = f_.readline().strip()
except OSError:
    linea_metodo = "(sin metodo.md)"
guia = leer(RAIZ / "guia.md") or ""
print("=== METODO (primera línea)")
print(linea_metodo)
if RAIZ_RESUELTA:   # se pasó la ruta de la computadora: se dice cuál es la de la consola, que es la que vale para leer y escribir
    print(f"RAIZ: {RAIZ} · la carpeta en esta consola; todo lo que se lea o escriba aquí va con esta ruta, nunca con la de get_device_info")
print(f"HOY: {HOY.isoformat()} · zona {getattr(TZ, 'key', TZ)} · la fecha de todo lo que se escribe hoy en la carpeta; no la del reloj de la consola ni del contenedor, que van en UTC")

def version_huella(linea):
    """(tupla de la versión, huella) de una primera línea de metodo.md; (None, None) si no la trae."""
    m = re.search(r"versi[oó]n\s+(\d+(?:\.\d+)*)", linea or "", re.I)
    h = re.search(r"huella\s+([0-9a-f]+)", linea or "", re.I)
    return (tuple(int(x) for x in m.group(1).split(".")) if m else None), (h.group(1) if h else None)

if PLUGIN is not None:
    vr, hr = version_huella(linea_metodo)
    vp, hp = version_huella(PLUGIN)
    txt = lambda v: ".".join(map(str, v)) if v else "sin versión"
    if not vp:
        ver = "SIN VEREDICTO: la línea del plugin no trae versión"
    elif not vr or vp > vr or (vp == vr and not hr):
        ver = "RAIZ ATRASADA: se copia el metodo.md del plugin"
    elif vp < vr:
        ver = "PLUGIN ATRASADO: no se copia nada; se avisa de que la carpeta usa una versión más nueva"
    elif hr == hp:
        ver = "AL DIA"
    else:
        ver = "MISMA VERSION, HUELLA DISTINTA: no se toca"
    print(f"Veredicto: {ver} (raíz {txt(vr)}, plugin {txt(vp)})")
    VEREDICTO = ver.split(":")[0]
    VERSION_RAIZ, VERSION_PLUGIN = txt(vr), txt(vp)
m_org = re.search(r"^#\s+(.+)$", guia, re.M)
ORGANIZACION = m_org.group(1).split("·")[0].strip() if m_org else ""
if MINIMA:
    titulo("ORGANIZACION")
    print(ORGANIZACION or "(guia.md sin título)")
else:
    titulo("GUIA")
    # la receta para conectarse y la nota de la versión son para personas: no hacen falta para trabajar (1.19)
    omitidas, guia_sesion = [], guia
    for sec in ("Quién es quién", "Cómo conectarte", "Versión del método"):   # «Quién es quién» lo leen los scripts; la cuenta de la sesión sale en CUENTA (1.25)
        m_ = re.search(r"^##\s+" + re.escape(sec) + r"\s*$.*?(?=^##\s|\Z)", guia_sesion, re.M | re.S)
        if m_:
            guia_sesion = guia_sesion[:m_.start()] + guia_sesion[m_.end():]; omitidas.append(sec)
    print(guia_sesion.strip())
    if omitidas:
        print(f"(se omiten {' y '.join('«' + s + '»' for s in omitidas)}: si hacen falta, se leen en guia.md)")

def columnas_areas(cab):
    """Dónde está cada columna de la tabla de áreas, por su encabezado: la 1.22 dice «Responsable» y añade «Acceso»;
    hasta la 1.21, «Dueño» y sin «Acceso». Sin encabezado reconocible, las posiciones de siempre."""
    n = [re.sub(r"[*_`]", "", x).strip().lower() for x in cab]
    def pos(*nombres, defecto=None):
        return next((i for i, x in enumerate(n) if x in nombres), defecto)
    return {"responsable": pos("responsable", "dueño", "dueno", defecto=2), "cuenta": pos("cuenta", "colabora", defecto=3),
            "lectores": pos("quién la lee", "quien la lee", defecto=4), "acceso": pos("acceso")}


def area_restringida(c, col):
    """Con columna «Acceso» (1.22), restringida si dice «Restringida» y abierta si dice «Abierta»; con otra cosa o vacía,
    y sin la columna, la regla de «Quién la lee» de la 1.21: nunca se falla abierto."""
    if col["acceso"] is not None and col["acceso"] < len(c):
        v = c[col["acceso"]]
        if re.match(r"^[\W_]*restringid[oa]s?\b", v, re.I):
            return True
        if re.match(r"^[\W_]*abiert[oa]s?\b", v, re.I):
            return False
    return restringida_celda(c[col["lectores"]] if col["lectores"] < len(c) else "")


areas = []
filas = seccion(guia, "Áreas").split("\n")
col_areas = None
cab_areas = None
REG = registro_personas(guia)
guia_anterior = False
for l in filas:
    if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
        continue
    c = [x.strip() for x in l.strip().strip("|").split("|")]
    if col_areas is None:
        col_areas = columnas_areas(c); cab_areas = c
        guia_anterior = col_areas["acceso"] is None or any(re.sub(r"[*_`]", "", x).strip().lower() in ("dueño", "dueno") for x in c)
        continue
    minimo = max(v for v in col_areas.values() if v is not None) + 1
    if len(c) >= minimo:
        de, co, av = fila_cuentas(cab_areas, c, REG)
        if av:
            print(f"(aviso: la fila de «{c[0].strip('`')}» en la tabla de áreas de guia.md: {av})")
        areas.append({"slug": c[0].strip("`").rstrip("/"), "dueno": c[col_areas["responsable"]], "cuentas_dueno": de, "colaboran": co,
                      "restringida": area_restringida(c, col_areas), "lectores": c[col_areas["lectores"]],
                      "en_celda": set(CORREO.findall(c[col_areas["cuenta"]].lower())) | {x for n in nombres_de(c[col_areas["responsable"]] + "," + c[col_areas["cuenta"]]) for x in ((persona(n, REG) or {}).get("cuentas") or set())}, "aviso": av})
    else:
        print(f"(aviso: la fila «{c[0].strip('`')}» de la tabla de áreas de guia.md tiene {len(c)} columnas y hacen falta {minimo}; esa área no se lee hasta que se corrija)")
if ZONA_AVISO:
    print(f"(aviso: {ZONA_AVISO})")
if not areas:
    print("(aviso: no se encontró ninguna área en la sección «## Áreas» de guia.md: sin ella nadie tiene área ni cuenta; que el responsable de contexto revise guia.md)")
# como el tablero: la línea que empieza por «Contexto común», cortada por su primer «:» (la plantilla de `nuevo` escribe
# «Contexto común (`guia.md` y `base/`): Nombre (correo).»); sin correo, la cuenta del responsable es la de las áreas
# de las que es responsable
resp_contexto = ""
for l in seccion(guia, "Quién responde por qué").split("\n"):
    if l.strip().lower().lstrip("-* ").startswith("contexto común"):
        resp_contexto = l.split(":", 1)[-1].strip().rstrip(".").strip()
# la cuenta del responsable va entre paréntesis en esa misma línea («Contexto común: Nombre (correo)»); sin ella,
# como antes, es la de las áreas de las que esa persona es responsable
cuenta_resp = cuentas_contexto(resp_contexto, REG)
resp_contexto = re.sub(r"\s*\([^)]*\)", "", resp_contexto).strip()
# el nombre de la celda sin lo que va entre paréntesis, como migrar_estructura.py: los dos tienen que reconocer a la misma persona
es_resp = bool(CUENTA) and (CUENTA in cuenta_resp or (bool(resp_contexto) and not cuenta_resp and any(CUENTA in a["cuentas_dueno"] and re.sub(r"\s*\([^)]*\)", "", a["dueno"]).strip().lower() == resp_contexto.lower() for a in areas)))

premisas = []
for l in (leer(RAIZ / "base" / "premisas.md") or "").split("\n"):
    m = re.match(r"^\s*-\s*(P\d+)\s*·\s*(.+)$", l)
    if m:
        partes = [x.strip() for x in m.group(2).split("·")]
        r = next((re.search(r"P\d+", x, re.I).group(0).upper() for x in partes[1:] if re.match(r"reemplaza\b", x, re.I) and re.search(r"P\d+", x, re.I)), None)
        f = next((x for x in partes[1:] if re.fullmatch(r"20\d\d-\d\d-\d\d", x)), "")
        premisas.append((m.group(1).upper(), l.strip(), r, f))
reemplazadas = {r for _, _, r, _ in premisas if r}
if not MINIMA:
    titulo("PREMISAS VIGENTES")
    print("\n".join(l for pid, l, _, _ in premisas if pid not in reemplazadas) or "(no hay base/premisas.md o no tiene premisas)")

if CUENTA:
    titulo("CUENTA")
    mias = [a["slug"] for a in areas if CUENTA in a["cuentas_dueno"]]
    colab = [a["slug"] for a in areas if CUENTA in a["colaboran"] and CUENTA not in a["cuentas_dueno"]]
    proy_co = []
    if ACTIVO and "/" in ACTIVO and ACTIVO.split("/")[0] not in mias + colab:
        tp_ = leer(RAIZ / ACTIVO / "proyecto.md")
        if tp_ and CUENTA in colaboran_en(seccion(cabecera(tp_)[1], "Quién participa"), REG if REG["hay"] else None):
            proy_co = [ACTIVO]
    donde_ = ", ".join([f"{s} (responsable)" for s in mias] + [f"{s} (colabora)" for s in colab] + [f"{s} (colabora en el proyecto)" for s in proy_co])
    if not donde_:
        DECIR.append("No escribes en ninguna área: dime en cuál trabajas.")
    print(f"{CUENTA}: escribe en {donde_ if donde_ else 'ninguna área (preguntar en cuál trabaja antes de escribir)'}"
          + ("; es la del responsable de contexto (también guia.md y base/)" if es_resp else ""))
    # «Quién es quién» (1.25): el nombre de la cuenta sale del registro, y «Sesión de:» lo lleva sin preguntarlo
    if REG["hay"]:
        _yo = REG["cuenta"].get(CUENTA)
        if _yo and _yo["nombre"] != "?" and not _yo["compartida"]:
            print(f"NOMBRE {_yo['nombre']} (de «Quién es quién»: es el de «Sesión de:», sin preguntarlo)")
        elif _yo and _yo["compartida"]:
            print(f"NOMBRE (la cuenta la comparten {_yo['nombre']} y {_yo['compartida']}: «Sesión de:» lleva el de quien trabaja hoy, que se pregunta)")
        elif _yo:
            DECIR.append(f"Tu cuenta está en «Quién es quién» de guia.md sin nombre («? · {CUENTA}»): dime tu nombre y se lo paso al responsable de contexto.")
        else:
            DECIR.append(f"Tu cuenta {CUENTA} no está en «Quién es quién» de guia.md, así que no escribes en ninguna área hasta que el responsable de contexto la añada (si tu línea tiene un error en la cuenta, es ahí donde se corrige). Dime en qué área trabajas y te preparo el texto para pasárselo.")
        if _yo and _yo["baja"]:
            DECIR.append(f"Tu línea de «Quién es quién» dice «baja»: no escribes en ninguna área de esta carpeta.")
        if es_resp:
            _pend = [p_["nombre"] for p_ in REG["personas"] if p_["sin_confirmar"]]
            _sinn = [sorted(p_["cuentas"])[0] for p_ in REG["personas"] if p_["nombre"] == "?" and p_["cuentas"]]
            for _av in REG["avisos"]:
                DECIR.append(f"En «Quién es quién» de guia.md: {_av}.")
            if _sinn:
                DECIR.append(f"En «Quién es quién», {len(_sinn)} cuenta(s) sin nombre ({', '.join(_sinn)}): siguen escribiendo, pero hay que ponerles el nombre de la persona.")
            if _pend:
                DECIR.append(f"En «Quién es quién», «sin confirmar»: {', '.join(_pend)}. Se quita la marca cuando esa persona abra su primera sesión con esa cuenta (lo dice su «Sesión de:»).")
    # el administrador principal es una sola persona (1.22.2): se le dice al responsable de contexto si guia.md nombra a dos
    _ver, _adm, _ctx = administrador_unico(seccion(guia, "Quién responde por qué"), {**{re.sub(r"\s*\([^)]*\)", "", a["dueno"]).split(",")[0].strip().lower(): a["cuentas_dueno"] for a in areas if a["cuentas_dueno"]},
                                         **{clave_nombre(n): {sorted(p_["cuentas"])[0]} for p_ in REG["personas"] if p_["cuentas"] and not p_["baja"] for n in [p_["nombre"]] + p_["alias"] if n != "?"}})
    if es_resp and _ver == "dos":
        DECIR.append(f"guia.md nombra a dos personas: «{_adm}» administra la carpeta y «{_ctx}» responde por el contexto. Son una sola, la dueña de la carpeta en Drive, que lo lee todo y migra todas las áreas. Se corrige en «Quién responde por qué».")
    # el primer párrafo de guia.md es lo que el tablero enseña arriba de Inicio: si sigue con la plantilla o vacío, se le dice a
    # quien lo escribe (revisión de la 1.22.4, hallazgo 7). Las mismas reglas que generar_vista.py
    if es_resp:
        _cuerpo = re.sub(r"^\s*#[^\n]*\n", "", re.sub(r"\A---\n.*?\n---\n", "", guia, count=1, flags=re.S), count=1)
        _p1 = next((b.strip() for b in re.split(r"\n\s*\n", _cuerpo.strip()) if b.strip() and not b.strip().startswith(("|", "- "))), "")
        _p1 = re.sub(r"\*\*([^*]+)\*\*", r"\1", re.sub(r"<!--.*?-->", "", _p1, flags=re.S)).strip()
        _frases = sin_carpeta(re.split(r"(?<=[.!?])\s+", _p1))
        if (not _p1 or _p1.startswith(("#", ">", "*", "```", "|")) or re.match(r"^\d+[.)]\s", _p1) or re.match(r"^Esta carpeta es la memoria de trabajo de\b", _p1)
                or re.search(r"\[(?:[^\]\n]*\s[^\]\n]*|[Oo]rganizaci[oó]n)\](?![(\[])", _p1) or not " ".join(_frases).strip()):
            DECIR.append("El primer párrafo de guia.md no dice qué es la organización, y el tablero no enseña nada arriba de Inicio. Se escribe en una o dos frases, a qué se dedica y para quién, sin hablar de la carpeta (lo de la carpeta pasa al segundo párrafo); lo escribes tú, con tu sí al texto.")
    # la revisión de permisos se ofrece al abrir (1.24.2, decidido el 2026-10-30): solo al administrador principal y solo si
    # la raíz vive en Google Drive (la ruta de --origen, con consola o sin ella). La fecha
    # de la última revisión vive en el tablero (meta/permisos), no en la carpeta: la mira la sesión, no este script
    if es_resp and en_drive(ORIGEN):
        PERMISOS = True
        print("PERMISOS: la raíz vive en Google Drive y esta cuenta la administra (qué se hace con esto: la sección RESPUESTA, o «Permisos de Drive» en la skill)")
    # la cuenta está en la celda de un área pero la celda no se deja leer (dos correos sin «colabora:», por ejemplo):
    # se dice cuál y cómo se escribe, para que no parezca un fallo y lo corrija quien lleva guia.md
    for a in areas:
        if a["aviso"] and CUENTA in a["en_celda"] and CUENTA not in a["cuentas_dueno"] | a["colaboran"]:
            DECIR.append(f"Tu cuenta está en la celda Cuenta de «{a['slug']}» en guia.md pero no cuenta como tuya ({a['aviso']}). Se escribe «correo del responsable · colabora: otro@…, otro@…»; la corrige el responsable de contexto, y mientras tanto dime en qué área trabajas.")


def solo_nombre(d):
    """El responsable sin las notas entre paréntesis de su celda («Ana (escribe también Beto…)»), que empiezan en minúscula;
    «Dirección (Ana, Beto)» se queda. Como el tablero."""
    return re.sub(r"\s*\((?=[a-záéíóúñ`])[^)]*\)", "", d or "").strip()


# ---------- la estructura de la 1.22 ----------
# La misma función en migrar_estructura.py, que renombra justo lo que esta detecta; probar_migrar.py comprueba que coinciden.
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


def area_anterior(slug):
    """Cierto si el área (su area.md, o algún proyecto con proyecto.md dentro) tiene todavía la estructura de la 1.21.
    Un area.md con «Responsable:» en «Quién participa» y ninguna marca vieja se da por migrada sin bajar a sus proyectos:
    solo la migración o un área creada con la 1.22 lo escriben, y la migración escribe area.md la última, solo si todos
    sus proyectos quedaron migrados. Así la apertura no lee todos los proyecto.md de una raíz migrada (1.22.1). Con
    «Estatus» no basta: un cierre 1.22 lo escribe también en un área sin migrar."""
    t = leer(RAIZ / slug / "area.md")
    cuerpo = cabecera(t)[1] if t else ""
    if t and marcas_anteriores(cuerpo, "area"):
        return True
    if t and re.search(r"^\s*[-*]?\s*\**\s*Responsable\s*\**\s*:", seccion(cuerpo, "Quién participa"), re.M):
        return False
    try:
        proyectos = sorted(d for d in (RAIZ / slug).iterdir() if d.is_dir() and not d.name.startswith(".") and (d / "proyecto.md").is_file())
    except OSError:
        return False
    for d in proyectos:
        if marcas_anteriores(cabecera(leer(d / "proyecto.md") or "")[1], "proyecto") or any((d / f).is_file() for f in ARCHIVOS_ANTERIORES):
            return True
    return False


EN_USO_MIN = 120   # como migrar_estructura.py: un proyecto ajeno tocado hace menos puede estar en sesión en otra computadora


def area_en_uso(slug):
    """Cierto si todo lo que queda por migrar en el área (los proyectos con marcas viejas) lo tocó alguien hace menos de
    EN_USO_MIN minutos: la migración lo dejaría igual, así que no se ofrece ahora y se dice. Sin fechas (la copia), falso."""
    if SIN_FECHAS:
        return False
    try:
        proyectos = [d for d in (RAIZ / slug).iterdir() if d.is_dir() and not d.name.startswith(".") and (d / "proyecto.md").is_file()]
    except OSError:
        return False
    viejos = [d for d in proyectos if marcas_anteriores(cabecera(leer(d / "proyecto.md") or "")[1], "proyecto") or any((d / f).is_file() for f in ARCHIVOS_ANTERIORES)]
    def tocado(d):
        for n in ("proyecto.md", "sesiones.md"):
            try:
                t = os.stat(d / n).st_mtime
            except OSError:
                continue
            if t > time.time() + 60 or time.time() - t < EN_USO_MIN * 60:
                return True
        return False
    return bool(viejos) and all(tocado(d) for d in viejos)


titulo("ESTRUCTURA")
ESTRUCTURA_ANTERIOR = ""
if not CUENTA:
    print("Veredicto: SIN CUENTA")
else:
    # el responsable de contexto migra también las áreas de otros responsables (1.22.1), las que su carpeta deja leer
    propias_viejas = [a["slug"] for a in areas if CUENTA in a["cuentas_dueno"] and area_anterior(a["slug"])]
    # la misma regla que migrar_estructura.py: todas las áreas con carpeta, restringidas incluidas
    ajenas_viejas, ajenas_en_uso = [], []
    for a in areas:
        if es_resp and CUENTA not in a["cuentas_dueno"] and (RAIZ / a["slug"]).is_dir() and area_anterior(a["slug"]):
            (ajenas_en_uso if area_en_uso(a["slug"]) else ajenas_viejas).append(f"{a['slug']} (de {solo_nombre(a['dueno']) or 'otro responsable'})")
    guia_vieja = es_resp and guia_anterior
    if propias_viejas or ajenas_viejas or guia_vieja:
        ESTRUCTURA_ANTERIOR = ", ".join(propias_viejas + ajenas_viejas + (["guia.md"] if guia_vieja else []))
        print("Veredicto: ANTERIOR en " + ESTRUCTURA_ANTERIOR
              + " · se pregunta antes de responder («La estructura» en la skill sesion)")
    else:
        print("Veredicto: AL DIA")
    if ajenas_en_uso:
        print(f"(en uso, no se ofrece ahora: {', '.join(ajenas_en_uso)}; alguien tocó lo que queda por migrar hace menos de {EN_USO_MIN} minutos y puede estar en sesión en otra computadora. Se ofrece en una apertura más tarde; no hace falta decir nada.)")


def primera_frase(l, minimo=40, maximo=220):
    """Hasta el primer punto que cierra frase fuera de paréntesis y de `código` (no «S. de R.L.»: lo que sigue va en
    minúscula o es otra inicial); si no lo hay antes de «maximo», se corta en una palabra con «…»."""
    nivel, cod = 0, False
    # «restringido: responsable Nombre. Descripción…» («dueño» hasta la 1.21): el nombre no es la primera frase; se salta
    m = re.match(r"^(.*?[—–:-]\s*restringid[oa]\s*:\s*(?:due[ñn][oa]|responsable)\s+[^.;]+[.;]\s*)(.+)$", l, re.I)
    if m:
        return m.group(1) + primera_frase(m.group(2), min(minimo, 20), maximo)
    for i, ch in enumerate(l):
        if ch == "`":
            cod = not cod
        elif not cod and ch == "(":
            nivel += 1
        elif not cod and ch == ")":
            nivel = max(0, nivel - 1)
        elif ch == "." and not cod and nivel == 0 and i >= minimo and (i + 1 == len(l) or (l[i + 1] == " " and (i + 2 >= len(l) or l[i + 2].isupper() or l[i + 2] in "«`")) ):
            if not re.search(r"\b[A-ZÁÉÍÓÚÑ]$", l[:i]):
                return l[:i + 1]
        if i >= maximo:
            return l[:l.rfind(" ", 0, maximo)].rstrip(",;:") + "…"
    return l


def indice_proyectos(texto_area):
    """{slug: línea del índice} del bloque Proyectos, más las líneas de entregables debajo de cada uno."""
    idx, actual = {}, None
    for l in seccion(cabecera(texto_area)[1], "Proyectos").split("\n"):
        m = re.match(r"^- `([^`/]+)/?`\s*[—–:-]?\s*(.*)$", l)
        if m:
            actual = m.group(1); idx[actual] = {"linea": l.strip(), "sub": []}; continue
        if re.match(r"^- `", l):
            actual = None; continue
        if actual and re.match(r"^\s+- ", l):
            idx[actual]["sub"].append(l.rstrip())
    return idx


def declarado(linea):
    return bool(re.match(r"^- `[^`]+`\s*[—–:-]?\s*[\W_]*restringid[oa]\b", linea, re.I))


def lectores_de(celda):
    """A quiénes se lee, para «restringida a …», de la celda «Quién la lee». Como el tablero."""
    t = celda or ""
    if re.match(r"^[\W_]*restringid[oa]s?\b", t, re.I):
        t = re.sub(r"^[\W_]*restringid[oa]s?\b[*_»\"”'’\s]*", "", t, flags=re.I)
    else:
        t = re.sub(r"\s*[(\[—–,-]?\s*\brestringidas?\b\s*[)\]]?", "", t, flags=re.I)
    t = re.sub(r"^[:—–,-]\s*", "", t.strip())
    t = re.sub(r"^(?:la|lo)\s+leen\s+", "", t, flags=re.I).strip()
    m = re.fullmatch(r"\((.*)\)", t)
    t = (m.group(1) if m else t).strip()
    return "" if not t else t if re.match(r"^(?:a|al|para|solo|sólo|únicamente|por|entre)\b", t, re.I) else "a " + t


def de_la_cuenta(a):
    """El área es de la cuenta de esta sesión: responsable o colabora. Entonces la puede leer aunque esté restringida."""
    return bool(CUENTA) and CUENTA in (a["cuentas_dueno"] | a["colaboran"])


def motivo_area(slug):
    """Por qué no se lee un área: restringida según guia.md (Drive no baja a la computadora lo que la cuenta no puede
    abrir, así que su carpeta tampoco está), salvo que sea de la cuenta; sin carpeta en esta computadora; o no se pudo
    leer. El mismo criterio que el tablero con --cuenta, salvo un caso: un área restringida que la cuenta lee sin ser
    responsable ni colaborar (quien administra la carpeta) aquí sale restringida, porque lo restringido no se muestra fuera de
    su área; el tablero, que es solo de quien lo monta, la muestra entera."""
    a = next((x for x in areas if x["slug"] == slug), None)
    quien = solo_nombre(a["dueno"]) if a else "su responsable"
    if a and a["restringida"] and not de_la_cuenta(a):
        lect = lectores_de(a["lectores"])
        return f"restringida{' ' + lect if lect else ''}; si hace falta acceso, se pide a {quien}"
    if not (RAIZ / slug).exists():
        if a and de_la_cuenta(a):
            return "es de esta cuenta, pero su carpeta aún no se creó o no está sincronizada en esta computadora"
        return f"aún no se creó, no está sincronizada en esta computadora o la cuenta no tiene acceso; responde {quien}"
    return f"no se pudo leer: sin permiso o sin descargar; responde {quien}"


def claude_outputs():
    """Lo que la app dejó en «Claude outputs»: nombre y fecha, sin abrir nada; se propone colocarlo en su proyecto.
    Sale en todos los modos, también al abrir un proyecto, pero solo a la cuenta del responsable de contexto (o sin
    --cuenta): a las demás no se les dice nada al abrir, y lo que cae ahí en su conversación lo recoge el hook."""
    titulo("CLAUDE OUTPUTS")
    if CUENTA and not es_resp:
        print("(no se muestra a esta cuenta: solo a quien responde por guia.md y base/)")
        return []
    # cada suelto es (ruta dentro de la carpeta, fecha en segundos): de la carpeta o, sin consola, del listado (1.24.9)
    sueltos = []
    if SIN_FECHAS and OUTPUTS:
        try:
            d_ = json.loads(pathlib.Path(OUTPUTS).read_text(encoding="utf-8"))
            ents = (d_.get("entries") if isinstance(d_, dict) else d_) or []
            OUTPUTS_CORTADO[0] = bool(isinstance(d_, dict) and d_.get("truncated"))
        except (OSError, ValueError, AttributeError):
            ents = []
        # un archivo o una carpeta del primer nivel es un suelto; la fecha de una carpeta, la de lo más nuevo que tenga dentro
        nom = lambda e: str(e.get("name") or "").replace("\\", "/").strip("/")
        ents = [e for e in ents if isinstance(e, dict) and nom(e) and not any(x.startswith(".") for x in nom(e).split("/"))]
        fechas = {}
        for e in ents:
            if e.get("type") == "file":
                for k in range(1, len(nom(e).split("/")) + 1):
                    r_ = "/".join(nom(e).split("/")[:k]); fechas[r_] = max(fechas.get(r_, 0), (e.get("mtimeMs") or 0) / 1000)
        sueltos = sorted(((nom(e), fechas.get(nom(e), 0)) for e in ents if "/" not in nom(e) and e.get("type") in ("file", "dir")),
                         key=lambda x: x[1], reverse=True)
    elif not SIN_FECHAS:
        try:
            co = next((d for d in RAIZ.iterdir() if d.is_dir() and d.name.lower() == "claude outputs"), RAIZ / "Claude outputs")
            sueltos = sorted(((p.relative_to(co).as_posix(), p.stat().st_mtime) for p in co.rglob("*")
                              if p.is_file() and not any(x.startswith(".") for x in p.relative_to(co).parts)),
                             key=lambda x: x[1], reverse=True)
        except OSError:
            sueltos = []
    if not sueltos:
        print("(vacía o no existe)")
        return []
    print(f"{len(sueltos)} archivos sueltos")
    # en la mínima basta el número: la fila de la RESPUESTA lo resume, y los nombres los lista quien los coloca (1.24.9)
    if MINIMA:
        return sueltos
    for r_, m_ in sueltos[:30]:
        f = " · " + datetime.datetime.fromtimestamp(m_, TZ).date().isoformat() if m_ else ""
        print(f"- {r_}{f}")
    if len(sueltos) > 30:
        print(f"(y {len(sueltos) - 30} más)")
    return sueltos


CONFIDENCIAL = re.compile(r"contrat|propuesta|cotizaci|curr[ií]cul|\bcv\b|n[oó]mina|salari|sueldo|factura|\brfc\b|curp|\bnss\b|\bnda\b|confidencial|contrase|password", re.I)


def celda(t):
    """Una celda de tabla de Markdown: sin saltos de línea ni «|»."""
    return re.sub(r"\s*[\r\n|]+\s*", " · ", t).strip()


def ruta_en_la_computadora(rel):
    """La ruta de un archivo de la raíz en la computadora, con el separador de la ruta que dio get_device_info: en Windows
    va con barras invertidas, como hace espejo.py."""
    o = ORIGEN or str(RAIZ)
    sep = "\\" if "\\" in o and "/" not in o.replace("\\", "") else "/"
    return o.rstrip("/\\") + sep + rel.replace("/", sep)


def metodo_para_subir():
    """El metodo.md del plugin con el que corre este script, copiado a una carpeta nueva de salidas del contenedor para
    device_commit_files (1.24.9). Solo si su primera línea es la del --plugin; si no, None y se sigue como siempre."""
    fuente = pathlib.Path(__file__).resolve().parents[2] / "metodo.md"
    try:
        texto = fuente.read_text(encoding="utf-8")
    except OSError:
        return None
    if not PLUGIN or PLUGIN not in texto[:400]:
        return None
    # MEMORIA_SALIDAS solo lo usan las pruebas, donde no existen las carpetas de salidas del contenedor
    base = next((pathlib.Path(b) for b in (os.environ.get("MEMORIA_SALIDAS") or "", "/mnt/project-files", "/mnt/user-data/outputs") if b and pathlib.Path(b).is_dir()), None)
    if base is None:
        return None
    # un nombre por versión, reutilizado: cada conversación con la raíz atrasada no deja otra copia de 137 KB
    destino = base / f"metodo-{VERSION_PLUGIN or 'plugin'}" / "metodo.md"
    try:
        if not (destino.is_file() and destino.read_text(encoding="utf-8") == texto):
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(texto, encoding="utf-8")
    except OSError:
        return None
    return str(destino)


def respuesta(sueltos, completa=False, sin_proyecto=False):
    """El recuadro con sus filas y, en orden, lo que toca, ya decidido (1.24.8). Así la conversación hace la apertura mínima
    sin cargar la skill sesion (su anexo minima.md, que inyecta el aviso de arranque), y la completa no recalcula filas.
    Nada de aquí remite a una skill: lo que hay que hacer viene escrito."""
    titulo("RESPUESTA (la apertura completa: el recuadro y lo que toca)" if completa else "RESPUESTA (la apertura mínima: haz esto y nada más)")
    vr_ = version_huella(linea_metodo)[0]
    version = VERSION_PLUGIN if VEREDICTO == "RAIZ ATRASADA" else (".".join(map(str, vr_)) if vr_ else "?")
    raiz_ = str(RAIZ)
    filas = []
    if VEREDICTO == "PLUGIN ATRASADO":
        filas.append(f"**Método:** esta carpeta usa una versión del método más nueva que la de tu Claude ({VERSION_RAIZ} frente a {VERSION_PLUGIN}). "
                     "Actualízalo en la app de Claude, en Customize → Plugins, con el botón Update del marketplace memoria-marketplace, o pide ayuda a quien administra la carpeta.")
    filas += [f"**Aviso:** {d}" for d in DECIR]
    if sueltos:
        f_ = f", el último del {datetime.datetime.fromtimestamp(sueltos[0][1], TZ).date().isoformat()}" if sueltos[0][1] else ""
        conf = sum(1 for r_, _ in sueltos if CONFIDENCIAL.search(r_.rsplit("/", 1)[-1]))
        filas.append(f"**Claude outputs:** {'más de ' if OUTPUTS_CORTADO[0] else ''}{len(sueltos)} archivo{'s' if len(sueltos) != 1 else ''} suelto{'s' if len(sueltos) != 1 else ''}{f_}"
                     + (f"; {'uno parece confidencial' if conf == 1 else f'{conf} parecen confidenciales'}" if conf else "") + ".")
    cab = "La respuesta empieza con este recuadro, tal cual"
    if PERMISOS:
        cab += " (la fila de permisos, si toca, la añade su paso)"
    if completa:
        cab += "; si en esta conversación ya salió, no se repite: solo sus filas nuevas, como filas de «Memoria · avisos», y una pregunta ya hecha no se repite"
    print(cab + ":")
    print(f"| Memoria de trabajo · {celda(ORGANIZACION or 'sin nombre')} · v{version} |")
    print("|---|")
    for f_ in filas:
        print(f"| {celda(f_)} |")
    pasos = []
    copia_metodo = metodo_para_subir() if VEREDICTO == "RAIZ ATRASADA" and SIN_FECHAS else None
    if copia_metodo:
        # sin consola, o en la apertura mínima, que no ejecuta nada descargado en la computadora (1.24.9): el metodo.md del
        # plugin instalado ya está en una carpeta de salidas, y basta escribirlo
        pasos.append("Antes de responder y sin decirlo, pon al día el método de la raíz: device_commit_files con "
                     f"stagedPath «{copia_metodo}» y devicePath «{ruta_en_la_computadora('metodo.md')}», y después, en el Bash que siga o en uno propio, `rm -rf \"{pathlib.Path(copia_metodo).parent}\"`. Si no sale en «written», no se dice nada y el recuadro lleva "
                     f"v{VERSION_RAIZ or '?'}, la versión que tiene la raíz.")
    elif VEREDICTO == "RAIZ ATRASADA" and SIN_FECHAS:
        # sin carpeta de salidas device_commit_files no tiene de dónde escribir, y descargar en la computadora es lo que se evita
        pasos.append(f"El método de la raíz no se pone al día en esta conversación: no se dice nada y el recuadro lleva v{VERSION_RAIZ or '?'}, la versión que tiene la raíz.")
    elif VEREDICTO == "RAIZ ATRASADA":
        pasos.append("Antes de responder y sin decirlo, pon al día el método de la raíz, en una llamada a device_bash: lo que va detrás de «METODO_DESCARGA » en el aviso de arranque, "
                     f"seguido de ` && cp \"$HOME/memoria/metodo.md\" \"{raiz_}/metodo.md\" && head -1 \"{raiz_}/metodo.md\"`. "
                     "Si la comprobación falla, una vez más con main en lugar de v<versión> en sus dos direcciones; si tampoco, o el aviso no trae METODO_DESCARGA, "
                     "como dice «El método» de la skill sesion. Si la línea que imprime head no dice la versión nueva (la escritura falló por permisos), no se dice nada y el recuadro lleva "
                     f"v{VERSION_RAIZ or '?'}, la versión que tiene la raíz.")
    if ESTRUCTURA_ANTERIOR:
        pasos.append("Antes de responder: la respuesta es solo el recuadro y esta pregunta, con AskUserQuestion si está (opciones «Migrar ahora» y «Después»; sin ella, en texto, y se espera): "
                     f"«Tu parte de la carpeta usa la estructura de antes de la 1.22 ({ESTRUCTURA_ANTERIOR}). ¿La paso a la nueva antes de seguir? Renombra secciones y claves sin perder nada y deja una línea en la bitácora de cada proyecto.»"
                     + (" Añade que las áreas «(de …)» son de otros responsables y que su bitácora dirá quién las migró." if "(de " in ESTRUCTURA_ANTERIOR else "")
                     + " Con «Migrar ahora», el anexo migracion.md de la skill sesion; con «Después», no se vuelve a preguntar en esta conversación. "
                     "Los pasos que siguen a este van en la respuesta siguiente, después de la contestación; si ya se había respondido cuando llegó esta apertura, la pregunta va igual, sola tras el recuadro. "
                     "En una tarea programada no se pregunta ni se migra.")
    if PERMISOS:
        if completa:
            pasos.append("Permisos de Drive: como en la apertura mínima; si ya se ofreció en esta conversación, nada.")
        else:
            pasos.append("Permisos de Drive, solo si la sesión tiene el conector de Google Drive y el de artifacts (herramientas mcp__claude-artifacts__…; si no, nada, y no se dice): "
                         "ToolSearch de mcp__claude-artifacts__list_artifacts y mcp__claude-artifacts__db_get; con el slug del artifact «Tablero "
                         + (ORGANIZACION or "<organización>") + "» de esta cuenta, db_get de meta/permisos. Se ofrece si no existe, si su «revisado» es de hace más de 30 días, "
                         "o si su lista «cambios» no está vacía y es de hace más de 7 días: una fila «**Permisos de Drive:** sin revisar desde el <fecha>» (o «nunca se revisaron», "
                         "o «quedan <n> cambios de la revisión del <fecha>») y, al final, la pregunta «¿Reviso ahora los permisos de Drive?» con «Revisar ahora» y «Después». "
                         "Sin tablero o si una llamada falla, nada. Con «Revisar ahora», el anexo permisos.md de la skill sesion; con «Después», no se vuelve a ofrecer en esta conversación.")
    if completa and not sin_proyecto:
        pasos.append("Antes de responder, la cola del tablero: ToolSearch de mcp__claude-artifacts__list_artifacts, db_query y read_file (o Artifact y ArtifactData si la sesión tiene las de antes); "
                     f"si list_artifacts trae un «Tablero {ORGANIZACION or '<organización>'}» de esta cuenta, se lee y se enseña como dice el anexo cola.md de la skill sesion. Sin el conector o sin tablero, nada, y no se dice.")
    # con un proyecto que no se pudo leer, la apertura sale igual, con el recuadro, y la respuesta pregunta cuál era (1.24.9)
    pasos.append(f"Di en una línea que «{ACTIVO}» no se encuentra (no existe, es restringido o no está descargado) y pregunta cuál se abre, con los proyectos de su área del bloque Proyectos de arriba; "
                 "no lo crees sin que lo pidan (la skill nuevo)." if sin_proyecto else
                 "Responde con la sesión: dónde quedó todo, los recuadros de la memoria, los avisos y la propuesta de trabajo, como dice «Qué respondo» de la skill sesion."
                 if completa else "Responde a lo que se pidió.")
    if sueltos:
        pasos.append("La última acción de la respuesta: «¿Coloco ahora lo que hay en Claude outputs?», con AskUserQuestion si está (opciones «Colocar ahora» y «Después», "
                     "en la misma llamada que la de los permisos si la hay; sin la herramienta, esa misma pregunta en texto, una sola vez). Con «Colocar ahora», «Ordenar Claude outputs» "
                     "de la skill donde-va; con «Después», no se vuelve a preguntar en esta conversación, ni al abrir después un proyecto.")
    for i, p_ in enumerate(pasos, 1):
        print(f"{i}. {p_}")
    if not completa:
        print("Nada más de esta salida se dice: ni la lista de proyectos, que solo sirve para saber si la petición es trabajo de uno, ni avisos.")


area_activa = ACTIVO.split("/")[0] if ACTIVO and "/" in ACTIVO else None
TOPE_PROYECTOS = 40
n_proy = 0
if not ACTIVO:
    titulo("PROYECTOS POR ÁREA (para saber cuál se abre)")
    for a in areas:
        if a["restringida"] and not de_la_cuenta(a):
            # lo restringido no sale salvo que la cuenta sea de esa área o el proyecto activo esté dentro
            print(f"- {a['slug']}/ · {motivo_area(a['slug'])}"); continue
        t = leer(RAIZ / a["slug"] / "area.md")
        if t is None:
            print(f"- {a['slug']}/ · {motivo_area(a['slug'])}"); continue
        for slug, d in indice_proyectos(t).items():
            # solo para saber cuál se abre: la primera frase de la línea, no el resumen entero (1.19)
            l_ = d["linea"].replace(f"`{slug}/`", f"`{a['slug']}/{slug}/`", 1)
            # en la mínima basta reconocer el proyecto: la ruta y unas palabras, no la frase entera, y con tope (1.24.8)
            if MINIMA:
                n_proy += 1
                if n_proy > TOPE_PROYECTOS:
                    continue
            print(primera_frase(l_, minimo=20, maximo=90) if MINIMA else primera_frase(l_))
    if MINIMA and n_proy > TOPE_PROYECTOS:
        print(f"(y {n_proy - TOPE_PROYECTOS} proyectos más: sin --minima se listan todos)")
    if no_legibles:
        print(f"\n(no se pudieron leer: {len(no_legibles)})")
    # sin proyecto todavía, la RESPUESTA también sale: la apertura completa que sigue con el proyecto no la repite
    respuesta(claude_outputs(), completa=not MINIMA)
    sys.exit(0)

# ---------- nivel 1 ----------
if "/" not in ACTIVO:
    sys.exit(f"El proyecto va como <area>/<proyecto>, no «{ACTIVO}».")
pc = RAIZ / ACTIVO
area_txt = leer(RAIZ / area_activa / "area.md")
titulo(f"AREA {area_activa} · bloque Proyectos")
print(seccion(cabecera(area_txt)[1], "Proyectos") if area_txt is not None else f"(no se pudo leer area.md: {motivo_area(area_activa)})")
tp = leer(pc / "proyecto.md")
if tp is None:
    titulo("PROYECTO")
    print("(no se pudo leer proyecto.md: el proyecto no existe, es restringido o no está descargado)")
    respuesta(claude_outputs(), completa=True, sin_proyecto=True)
    sys.exit(0)
titulo(f"PROYECTO {ACTIVO}/proyecto.md")
print(tp.strip())
if CUENTA:
    # colaborar en un solo proyecto: una línea «Colabora:» en «Quién participa» con la cuenta entre paréntesis
    a_act = next((a for a in areas if a["slug"] == area_activa), None)
    if a_act and CUENTA in a_act["cuentas_dueno"]:
        rol = "responsable del área"
    elif a_act and CUENTA in a_act["colaboran"]:
        rol = "colabora en el área"
    elif CUENTA in colaboran_en(seccion(cabecera(tp)[1], "Quién participa"), REG if REG["hay"] else None):
        rol = "colabora en este proyecto"
    else:
        rol = "no escribe aquí (preguntar antes de escribir)"
    titulo("CUENTA EN EL PROYECTO")
    print(f"{CUENTA}: {rol}")
# para el cierre: cuándo cambió cada registro por última vez; si cambian mientras dura la sesión, otra persona escribió
titulo("REGISTROS (hora de la última escritura)")
print(f"ahora: {datetime.datetime.now(TZ).isoformat(timespec='seconds')}   (para --abierto de cerrar.py)")
for n_ in ("proyecto.md", "decisiones.md", "sesiones.md"):
    if SIN_FECHAS:
        try:
            print(f"{n_}: {os.stat(pc / n_).st_size} bytes (sin consola: la hora es la de la copia; al cerrar se releen siempre)")
        except OSError:
            print(f"{n_}: no se pudo leer")
        continue
    try:
        st_ = datetime.datetime.fromtimestamp(os.stat(pc / n_).st_mtime, TZ)
        print(f"{n_}: {st_.isoformat(timespec='seconds')} · {os.stat(pc / n_).st_size} bytes" + (f" · hace {int((datetime.datetime.now(TZ) - st_).total_seconds() // 60)} minutos: si no fue esta cuenta, otra persona trabaja ahora en el proyecto" if (datetime.datetime.now(TZ) - st_).total_seconds() < 3600 else ""))
    except OSError:
        print(f"{n_}: no se pudo leer")
# los registros con sus archivados recientes: después de archivar, el vivo puede tener una entrada o ninguna (1.23)
dec_txt, _ = con_archivados(pc, "decisiones", leer(pc / "decisiones.md") or "", HOY.year, leer)
ses_txt, _ = con_archivados(pc, "sesiones", leer(pc / "sesiones.md") or "", HOY.year, leer)
titulo("DECISIONES (las 5 más recientes)")
print("\n\n".join(e["texto"] for e in recientes(dec_txt, 5)) or "(ninguna)")
titulo("SESIONES (las 3 más recientes)")
ses = [e for e in recientes(ses_txt, 4) if "(migracion)" not in e["cab"]][:3]   # la entrada de la migración no cuenta como sesión
print("\n\n".join(e["texto"] for e in ses) or "(ninguna)")
# la última sesión de trabajo: las entradas «(tarea)», «(tablero)» y «(migracion)» no son sesiones, y lo que cambió
# después de la última real sigue siendo trabajo sin sesión aunque una tarea o la migración hayan escrito después
ultima_real = next((e["fecha"] for e in sorted(entradas(ses_txt), key=lambda e: e["fecha"], reverse=True)
                    if fecha_ok(e["fecha"]) and not re.search(r"\((tarea|tablero|migracion)\)", e["cab"], re.I)), None)
ultima_ses = ultima_real
# «Proyecto terminado el …» abre el Estatus desde la 1.22; hasta la 1.21, Estado actual o En corto
cerrado = any(re.search(r"Proyecto terminado el\s*20\d\d-\d\d-\d\d", seccion(cabecera(tp)[1], n_)) for n_ in ("Estatus", "Estado actual", "En corto"))

titulo("ENTREGABLES (cabeceras)")
avisos = []
# un proyecto que la migración dejó a medias (un conflicto) en un área ya migrada: la apertura mínima no baja a los
# proyectos de un área migrada, así que se dice aquí, al abrirlo
_marcas = marcas_anteriores(cabecera(tp)[1], "proyecto") + [f for f in ARCHIVOS_ANTERIORES if (pc / f).is_file()]
if _marcas and not area_anterior(area_activa):
    avisos.append(f"Estructura a medias: este proyecto conserva {', '.join('«' + m + '»' for m in _marcas)} de antes de la 1.22 y su área ya "
                  f"está migrada. Se propone pasarlo ahora con migrar_estructura.py (migracion.md, «Con el sí»), que solo toca lo que falta; "
                  f"si da un conflicto (un estado-anterior.md o un inventario.md que ya existía), se junta a mano en esta sesión.")
ents = []
d = pc / "entregables"
try:
    nombres = sorted(n for n in os.listdir(d) if not n.startswith(".") and (d / n).is_file()) if d.exists() else []
except OSError:
    nombres = []
for n in nombres:
    p = d / n
    if not n.endswith(".md"):
        print(f"- {n} · sin cabecera" + (f" (fecha de archivo {mtime(p)})" if mtime(p) else "")); continue
    t = leer(p)
    if t is None:
        print(f"- {n} · no se pudo leer"); continue
    fm, _ = cabecera(t)
    est, act = fm.get("estado", "?"), fm.get("actualizado", "?")
    base = fm.get("basado_en") if isinstance(fm.get("basado_en"), list) else []
    print(f"- {n} · {est} · actualizado {act}" + (f" · basado_en: {', '.join(base)}" if base else ""))
    ents.append((n, est, act))
    if est == "borrador" and fecha_ok(act) and (HOY - datetime.date.fromisoformat(act)).days > 30:
        avisos.append(f"Borrador viejo: entregables/{n} lleva {(HOY - datetime.date.fromisoformat(act)).days} días en borrador (actualizado {act}).")
    mas_nuevas = []
    for b in (base if est not in ("reemplazado",) else []):
        b_ = re.sub(r"^\./", "", b.strip("`"))
        for c in (pc / b_, RAIZ / b_):
            partes_c = c.relative_to(RAIZ).parts if RAIZ in c.parents else ()
            if not b_.endswith(".md") or not partes_c or partes_c[0] == "base" or {"restringido", "fuentes", "taller"} & set(partes_c):
                break   # no se abre: sin cabecera que comparar, o de donde abrir no lee
            if c.is_file():
                tb = leer(c)
                fb = cabecera(tb)[0].get("actualizado") if tb else None
                if fecha_ok(fb) and fecha_ok(act) and fb > act:
                    mas_nuevas.append(f"{b_} ({fb})")
                break
    if mas_nuevas:
        avisos.append(f"Puede estar desfasado: entregables/{n} (actualizado {act}) se basa en algo más nuevo: {', '.join(mas_nuevas)}.")
    if fecha_ok(act) and ultima_ses and act > ultima_ses and not cerrado:
        avisos.append(f"Trabajo sin sesión: entregables/{n} tiene actualizado {act}, posterior a la última sesión ({ultima_ses}).")

# trabajo sin sesión por fechas de archivo (nunca el contenido) en entregables/, taller/ y fuentes/
def listado_sin_sesion(ruta, desde):
    """[(fecha, hora, ruta)] de lo que el listado de device_list_dir da como cambiado desde «desde» (un datetime en la zona):
    decisiones.md y los archivos de entregables/, taller/ y fuentes/, fuera de restringido/ y de lo que empieza por punto.
    None si el listado no sirve: no se lee, viene truncado o no es el de la carpeta del proyecto (no trae proyecto.md en su
    primer nivel); entonces se mira a mano, porque un listado que no sirve no puede decir «no hay trabajo sin sesión»."""
    try:
        d = json.loads(pathlib.Path(ruta).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if isinstance(d, dict) and d.get("truncated"):
        return None
    ents = (d.get("entries") if isinstance(d, dict) else d) or []
    nombre = lambda e: str(e.get("name") or "").replace("\\", "/")
    if not any(nombre(e) in ("proyecto.md", "sesiones.md") for e in ents if isinstance(e, dict)):
        return None
    out, lim = [], desde.timestamp() * 1000
    for e in ents:
        if not isinstance(e, dict):
            continue
        n, ms = nombre(e), e.get("mtimeMs")
        partes = n.split("/")
        if e.get("type") != "file" or not isinstance(ms, (int, float)) or ms < lim or any(x.startswith(".") or x == "restringido" for x in partes):
            continue
        if n == "decisiones.md" or (len(partes) > 1 and partes[0] in ("entregables", "taller", "fuentes")):
            t = datetime.datetime.fromtimestamp(ms / 1000, TZ)
            out.append((t.date().isoformat(), t.strftime("%H:%M"), n))
    return sorted(out, reverse=True)


if SIN_FECHAS and ultima_ses and not cerrado:
    # sin consola las fechas de verdad solo están en el listado de la computadora (device_list_dir, en milisegundos):
    # con --listado se calculan aquí; sin él, o si no sirve, se da el instante desde el que mirarlo a mano
    _desde = datetime.datetime.combine(datetime.date.fromisoformat(ultima_ses) + datetime.timedelta(days=1), datetime.time(0), TZ)
    _lista = listado_sin_sesion(LISTADO, _desde) if LISTADO else None
    if _lista:
        avisos.append("Trabajo sin sesión por fecha de archivo, después del " + ultima_ses + ": "
                      + "; ".join(f"{a} ({f} {h})" for f, h, a in _lista[:12]) + (" …" if len(_lista) > 12 else "")
                      + ". Quién lo cambió no consta: se pregunta qué pasó y se propone registrarlo.")
    elif _lista is None:
        avisos.append(("El listado no sirve (no se lee, viene truncado o no es el de la carpeta del proyecto). " if LISTADO else "")
                      + f"Trabajo sin sesión: con device_list_dir (recursivo) de la carpeta del proyecto, "
                      f"cuenta los archivos de entregables/, taller/ y fuentes/ (fuera de restringido/), y decisiones.md, con mtimeMs mayor o igual que "
                      f"{int(_desde.timestamp() * 1000)} (después del {ultima_ses}); si hay alguno, se pregunta qué pasó y se propone registrarlo.")
if not SIN_FECHAS and ultima_ses and not cerrado:
    lim = datetime.date.fromisoformat(ultima_ses)
    donde, lista = {}, []
    md = mtime(pc / "decisiones.md")
    if md and md > lim:
        donde["decisiones"] = 1; lista.append((md.isoformat(), hora_de(pc / "decisiones.md"), "decisiones.md"))
    for sub in ("entregables", "taller", "fuentes"):
        for r_, ds, fs in os.walk(pc / sub):
            ds[:] = [x for x in ds if not x.startswith(".") and x != "restringido"]
            for f in fs:
                m_ = mtime(os.path.join(r_, f))
                if not f.startswith(".") and m_ and m_ > lim:
                    donde[sub] = donde.get(sub, 0) + 1
                    lista.append((m_.isoformat(), hora_de(os.path.join(r_, f)), pathlib.Path(r_, f).relative_to(pc).as_posix()))
    if donde:
        # qué archivo y cuándo; quién lo cambió no consta (la carpeta no lo guarda y Drive no se lo da al plugin), así que se pregunta
        lista.sort(reverse=True)
        avisos.append("Trabajo sin sesión por fecha de archivo, después del " + ultima_ses + ": "
                      + ", ".join(f"{k} {v}" for k, v in donde.items()) + ". Qué y cuándo: "
                      + "; ".join(f"{a} ({f} {h})".replace(" )", ")") for f, h, a in lista[:12]) + (" …" if len(lista) > 12 else "")
                      + ". Quién lo cambió no consta: se pregunta qué pasó y se propone registrarlo.")

# ---------- el barrido: Afecta a / Cuestiona a / Responde a en toda la raíz ----------
def proyectos_legibles():
    """(area, slug, carpeta) de cada proyecto cuyas decisiones se pueden mirar desde el proyecto activo."""
    for a in areas:
        if a["restringida"] and a["slug"] != area_activa:
            continue
        carpeta = RAIZ / a["slug"]
        t = leer(carpeta / "area.md")
        idx = indice_proyectos(t) if t is not None else {}
        try:
            hijos = sorted(n for n in os.listdir(carpeta) if (carpeta / n / "decisiones.md").is_file()) if carpeta.is_dir() else []
        except OSError:
            hijos = []
        for slug in hijos:
            # un proyecto sin línea en el índice de su área no se sabe si es restringido: no se mira, como en el tablero
            if f"{a['slug']}/{slug}" != ACTIVO and (slug not in idx or declarado(idx[slug]["linea"])):
                continue
            yield a["slug"], slug, carpeta / slug


respuestas, cuestiona, afecta = set(), [], []
mis_cuestionamientos, me_responden = {}, []
patron_proy = re.compile(r"(?<![\w/-])" + re.escape(ACTIVO) + r"(?![\w-])")
# un área entera como destino: «operacion/» o «operacion/ (el área entera)», nunca «operacion/soporte»
patron_area = re.compile(r"(?<![\w/-])" + re.escape(area_activa) + r"/(?![\w-])")
for a_slug, slug, carpeta in proyectos_legibles():
    # con los archivados de este año y del anterior: una decisión archivada sigue avisando y respondiendo (1.23)
    t, _ = con_archivados(carpeta, "decisiones", leer(carpeta / "decisiones.md"), HOY.year, leer)
    for r_ in respuestas_viejas(carpeta, HOY.year, leer):
        for m in re.finditer(r"([a-z0-9][\w.-]*/[a-z0-9][\w.-]*)#(20\d\d-\d\d-\d\d(?:-\d+)?)", r_):
            respuestas.add((m.group(1), m.group(2)))
        for m in re.finditer(r"premisa\s+(P\d+)", r_, re.I):
            respuestas.add(("premisa", m.group(1).upper()))
    if not t.strip():
        continue
    origen = f"{a_slug}/{slug}"
    # identificador de cada entrada: fecha y -2, -3… contando desde la más antigua del mismo día (de abajo arriba)
    es = entradas(t)
    cuenta = {}
    for e in reversed(es):
        if not e["fecha"]:
            e["id"] = ""                       # sin fecha válida no hay identificador (contrato, sección 4)
            continue
        n = cuenta[e["fecha"]] = cuenta.get(e["fecha"], 0) + 1
        e["id"] = e["fecha"] + ("" if n == 1 else f"-{n}")
    for e in es:
        campos = {k: (re.search(r"^" + k + r":\s*(.+)$", e["texto"], re.M | re.I) or [None, ""])[1] for k in ("Decidió", "Planteó", "Por qué", "Afecta a", "Cuestiona a", "Responde a")}
        if campos["Responde a"]:
            for m in re.finditer(r"([a-z0-9][\w.-]*/[a-z0-9][\w.-]*)#(20\d\d-\d\d-\d\d(?:-\d+)?)", campos["Responde a"]):
                respuestas.add((m.group(1), m.group(2)))
            for m in re.finditer(r"premisa\s+(P\d+)", campos["Responde a"], re.I):
                respuestas.add(("premisa", m.group(1).upper()))
        if origen == ACTIVO:
            if campos["Cuestiona a"] and e["id"]:
                mp_ = re.search(r"premisa\s+(P\d+)", campos["Cuestiona a"], re.I)
                mis_cuestionamientos[e["id"]] = (e["cab"], e["fecha"], mp_.group(1).upper() if mp_ else None)
            continue
        if campos["Responde a"]:
            for m in re.finditer(r"([a-z0-9][\w.-]*/[a-z0-9][\w.-]*)#(20\d\d-\d\d-\d\d(?:-\d+)?)", campos["Responde a"]):
                if m.group(1) == ACTIVO:
                    me_responden.append((origen, e, campos, m.group(2)))
        if campos["Cuestiona a"]:
            m = re.search(r"([a-z0-9][\w.-]*/[a-z0-9][\w.-]*)#", campos["Cuestiona a"])
            mp = re.search(r"premisa\s+(P\d+)", campos["Cuestiona a"], re.I)
            if (m and m.group(1) == ACTIVO) or (mp and es_resp):
                cuestiona.append((origen, e, campos, ("premisa", mp.group(1).upper()) if mp and not m else None))
        if campos["Afecta a"] and (patron_proy.search(campos["Afecta a"]) or patron_area.search(campos["Afecta a"])):
            afecta.append((origen, e, campos))

# un cuestionamiento sigue abierto si nadie respondió a su identificador; una premisa nueva que reemplaza a la
# cuestionada después del cuestionamiento también lo responde
reemplazo_fecha = {r: (f or "9999") for _, _, r, f in premisas if r}   # sin fecha, como el tablero: la responde
abiertos = []
for origen, e, c, prem in cuestiona:
    if not e["id"]:
        avisos.insert(0, f"Un cuestionamiento sin fecha válida en {origen} («{e['cab']}») nombra este proyecto: no tiene identificador y no se puede responder hasta que su responsable lo registre con fecha.")
        continue
    if (origen, e["id"]) in respuestas:
        continue
    if prem and prem[1] in reemplazo_fecha and reemplazo_fecha[prem[1]] >= e["fecha"]:
        continue
    abiertos.append((origen, e, c, prem))
# una línea por cuestionamiento, y el «Por qué» solo de los tres más recientes: con muchos, el aviso no crece sin tope
abiertos.sort(key=lambda x: (x[1]["fecha"], int(x[1]["id"].rsplit("-", 1)[1]) if x[1]["id"].count("-") == 3 else 1), reverse=True)
lineas_cq = []
for i, (origen, e, c, prem) in enumerate(abiertos):
    objetivo = f"la premisa {prem[1]}" if prem else c["Cuestiona a"]
    linea = f"Cuestionamiento abierto ({origen}#{e['id']}): «{e['cab']}». Planteó: {c['Planteó'] or c['Decidió'] or 'no consta'}. Cuestiona a: {objetivo}."
    if i < 3 and c["Por qué"]:
        linea += f" Por qué: {c['Por qué'][:300]}"
    lineas_cq.append(linea)
avisos[0:0] = lineas_cq
sin_fecha = [x for x in afecta if not x[1]["fecha"]]
afecta = [x for x in afecta if x[1]["fecha"]]
nuevos = [x for x in afecta if not ultima_real or x[1]["fecha"] >= ultima_real]
for origen, e, c in sorted(nuevos, key=lambda x: x[1]["fecha"], reverse=True):
    avisos.append(f"Le afecta una decisión de {origen} ({origen}#{e['id']}): «{e['cab']}». Decidió: {c['Decidió'] or 'no consta'}. Afecta a: {c['Afecta a'][:300]}")
# a quien cuestionó: la respuesta del responsable, si llegó después de su última sesión
for origen, e, c, cid in me_responden:
    if cid not in mis_cuestionamientos:
        continue   # «Responde a» apunta a una entrada de este proyecto que no es un cuestionamiento
    if not e["fecha"]:
        avisos.append(f"Una entrada sin fecha válida de {origen} responde a tu cuestionamiento {ACTIVO}#{cid} («{e['cab']}»): conviene que su responsable la registre con fecha.")
    elif not ultima_real or e["fecha"] >= ultima_real:
        avisos.insert(0, f"Respondieron tu cuestionamiento {ACTIVO}#{cid} («{mis_cuestionamientos[cid][0]}»): {origen}#{e['id']}, «{e['cab']}». Decidió: {c['Decidió'] or 'no consta'}. Por qué: {c['Por qué'][:300]}")
# una premisa cuestionada desde aquí y reemplazada después por otra: también es una respuesta
for cid, (cab_, fecha_, prem_) in mis_cuestionamientos.items():
    if prem_ and prem_ in reemplazo_fecha and reemplazo_fecha[prem_] != "9999" and reemplazo_fecha[prem_] >= fecha_ and (not ultima_real or reemplazo_fecha[prem_] >= ultima_real):
        nueva = next((l for pid, l, r, f in premisas if r == prem_), "")
        avisos.insert(0, f"Respondieron tu cuestionamiento {ACTIVO}#{cid} («{cab_}»): la premisa {prem_} se reemplazó el {reemplazo_fecha[prem_]}: {nueva}")
for origen, e, c in sin_fecha:
    avisos.append(f"Una entrada sin fecha válida de {origen} nombra este proyecto en «Afecta a» («{e['cab']}»): no se puede citar ni saber si es nueva; conviene que su responsable la revise.")
viejos = len(afecta) - len(nuevos)

# copias en conflicto: cuando dos computadoras escriben el mismo archivo antes de sincronizarse, Drive guarda las dos
# («sesiones (1).md», «proyecto [Conflict].md»). Solo cuenta una copia cuyo original está al lado. Van primero: hasta
# juntarlas, una de las dos versiones no la lee nadie.
CONFLICTO = re.compile(r"^(?P<base>.+?)\s*(\(\d+\)|\[[^\]]*conflict[^\]]*\])\.md$", re.I)
for carpeta_, donde_ in ((pc, "este proyecto"), (RAIZ / area_activa, f"el área {area_activa}"), (RAIZ, "la raíz")):
    try:
        nombres_ = sorted(os.listdir(carpeta_))
    except OSError:
        continue
    for n_ in nombres_:
        m_ = CONFLICTO.match(n_)
        if m_ and (carpeta_ / (m_.group("base") + ".md")).is_file():
            avisos.insert(0, f"Copia en conflicto en {donde_}: «{n_}» junto a «{m_.group('base')}.md». Drive guardó dos versiones porque dos personas "
                             f"escribieron a la vez; se juntan antes de seguir, como dice «Copias en conflicto» en cerrar.md.")

ctx = leer(RAIZ / "base" / "contexto.md")
fc = cabecera(ctx)[0].get("actualizado") if ctx else None
if fecha_ok(fc) and (HOY - datetime.date.fromisoformat(fc)).days > 90:
    avisos.append(f"base/contexto.md lleva {(HOY - datetime.date.fromisoformat(fc)).days} días sin actualizarse (actualizado {fc}).")

titulo("AVISOS")
print("\n".join("- " + a for a in avisos) or "(ninguno)")
if viejos:
    print(f"(además, {viejos} decisiones de otros proyectos anteriores a la última sesión lo nombran en «Afecta a:»; ya se vieron)")
if no_legibles:
    print(f"(no se pudieron leer {len(no_legibles)} archivos o carpetas: restringidos o sin descargar; no se supone qué hay)")
respuesta(claude_outputs(), completa=True)
