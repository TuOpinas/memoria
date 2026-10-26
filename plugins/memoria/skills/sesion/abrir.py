#!/usr/bin/env python3
"""Lo que hay que leer para abrir una sesión, en una sola llamada y sin escribir nada.

Uso: abrir.py <raiz> [<area>/<proyecto>] [--cuenta <correo>] [--plugin "<primera línea del metodo.md del plugin>"] [--sin-fechas [--listado <archivo>]] [--minima]

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
zona de la organización, como en la computadora: nadie compara milisegundos a mano.
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
if RAIZ is None or not (RAIZ / "guia.md").is_file():
    sys.exit("Uso: abrir.py <raiz> [<area>/<proyecto>] [--cuenta <correo>] [--plugin \"<primera línea del metodo.md del plugin>\"] [--sin-fechas] [--minima]  (la raíz es la carpeta con guia.md y metodo.md: en esta consola, la de $HOME/mnt/ cuyo nombre es el último tramo de la ruta que da get_device_info)")
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
LISTADO = None
if "--listado" in args:
    i = args.index("--listado"); LISTADO = args[i + 1] if i + 1 < len(args) else None; del args[i:i + 2]
ACTIVO = args[0].strip("/") if args and not MINIMA else None
ZONA_AVISO = None
_LEIDOS = {}
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
if MINIMA:
    titulo("ORGANIZACION")
    m_ = re.search(r"^#\s+(.+)$", guia, re.M)
    print((m_.group(1).split("·")[0].strip() if m_ else "(guia.md sin título)"))
else:
    titulo("GUIA")
    # la receta para conectarse y la nota de la versión son para personas: no hacen falta para trabajar (1.19)
    omitidas, guia_sesion = [], guia
    for sec in ("Cómo conectarte", "Versión del método"):
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
    return {"responsable": pos("responsable", "dueño", "dueno", defecto=2), "cuenta": pos("cuenta", defecto=3),
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
guia_anterior = False
for l in filas:
    if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
        continue
    c = [x.strip() for x in l.strip().strip("|").split("|")]
    if col_areas is None:
        col_areas = columnas_areas(c)
        guia_anterior = col_areas["acceso"] is None or any(re.sub(r"[*_`]", "", x).strip().lower() in ("dueño", "dueno") for x in c)
        continue
    minimo = max(v for v in col_areas.values() if v is not None) + 1
    if len(c) >= minimo:
        de, co, av = cuentas(c[col_areas["cuenta"]])
        if av:
            print(f"(aviso: la celda Cuenta de «{c[0].strip('`')}» en guia.md: {av})")
        areas.append({"slug": c[0].strip("`").rstrip("/"), "dueno": c[col_areas["responsable"]], "cuentas_dueno": de, "colaboran": co,
                      "restringida": area_restringida(c, col_areas), "lectores": c[col_areas["lectores"]],
                      "en_celda": set(CORREO.findall(c[col_areas["cuenta"]].lower())), "aviso": av})
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
cuenta_resp = set(CORREO.findall(resp_contexto.lower()))
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
        if tp_ and CUENTA in colaboran_en(seccion(cabecera(tp_)[1], "Quién participa")):
            proy_co = [ACTIVO]
    donde_ = ", ".join([f"{s} (responsable)" for s in mias] + [f"{s} (colabora)" for s in colab] + [f"{s} (colabora en el proyecto)" for s in proy_co])
    print(f"{CUENTA}: escribe en {donde_ if donde_ else 'ninguna área (preguntar en cuál trabaja antes de escribir)'}"
          + ("; es la del responsable de contexto (también guia.md y base/)" if es_resp else ""))
    # el administrador principal es una sola persona (1.22.2): se le dice al responsable de contexto si guia.md nombra a dos
    _ver, _adm, _ctx = administrador_unico(seccion(guia, "Quién responde por qué"), {re.sub(r"\s*\([^)]*\)", "", a["dueno"]).split(",")[0].strip().lower(): a["cuentas_dueno"] for a in areas if a["cuentas_dueno"]})
    if es_resp and _ver == "dos":
        print(f"(aviso para decirlo: guia.md nombra a dos personas, «{_adm}» administra la carpeta y «{_ctx}» responde por el contexto; "
              "son una sola, la dueña de la carpeta en Drive, que lo lee todo y migra todas las áreas. Se corrige en «Quién responde por qué».)")
    # el primer párrafo de guia.md es lo que el tablero enseña arriba de Inicio: si sigue con la plantilla o vacío, se le dice a
    # quien lo escribe (revisión de la 1.22.4, hallazgo 7). Las mismas reglas que generar_vista.py
    if es_resp:
        _cuerpo = re.sub(r"^\s*#[^\n]*\n", "", re.sub(r"\A---\n.*?\n---\n", "", guia, count=1, flags=re.S), count=1)
        _p1 = next((b.strip() for b in re.split(r"\n\s*\n", _cuerpo.strip()) if b.strip() and not b.strip().startswith(("|", "- "))), "")
        _p1 = re.sub(r"\*\*([^*]+)\*\*", r"\1", re.sub(r"<!--.*?-->", "", _p1, flags=re.S)).strip()
        # una frase que habla de la carpeta se quita; si va unida con «;» a otra que no, se queda la otra (1.22.5)
        def _sin_carpeta(frases, rx=r"`(?:metodo|guia)\.md`|plugin `memoria`|Aquí solo está lo nuestro"):
            out = []
            for f in frases:
                if not re.search(rx, f):
                    out.append(f); continue
                partes = [c.strip() for c in f.split(";")]
                quedan = [c for c in partes if c and not re.search(rx, c)]
                if quedan and len(partes) > 1:
                    t = "; ".join(quedan); out.append(t if t[-1] in ".!?" else t + ".")
            return out
        _frases = _sin_carpeta(re.split(r"(?<=[.!?])\s+", _p1))
        if (not _p1 or _p1.startswith(("#", ">", "*", "```", "|")) or re.match(r"^\d+[.)]\s", _p1) or re.match(r"^Esta carpeta es la memoria de trabajo de\b", _p1)
                or re.search(r"\[(?:[^\]\n]*\s[^\]\n]*|[Oo]rganizaci[oó]n)\](?![(\[])", _p1) or not " ".join(_frases).strip()):
            print("(aviso para decirlo: el primer párrafo de guia.md no dice qué es la organización, y el tablero no enseña nada arriba de Inicio. "
                  "Se escribe en una o dos frases, a qué se dedica y para quién, sin hablar de la carpeta; lo de la carpeta pasa al segundo párrafo. "
                  "Lo escribe esta cuenta, con su sí al texto.)")
    # la cuenta está en la celda de un área pero la celda no se deja leer (dos correos sin «colabora:», por ejemplo):
    # se dice cuál y cómo se escribe, para que no parezca un fallo y lo corrija quien lleva guia.md
    for a in areas:
        if a["aviso"] and CUENTA in a["en_celda"] and CUENTA not in a["cuentas_dueno"] | a["colaboran"]:
            print(f"(aviso para decirlo: esta cuenta está en la celda Cuenta de «{a['slug']}» en guia.md, pero no cuenta como suya: {a['aviso']}. "
                  f"Se escribe «correo del responsable · colabora: otro@…, otro@…»; la corrige el responsable de contexto, y mientras tanto se pregunta en qué área trabaja.)")


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
        print("Veredicto: ANTERIOR en " + ", ".join(propias_viejas + ajenas_viejas + (["guia.md"] if guia_vieja else []))
              + " · se pregunta antes de responder («Puesta al día de la estructura»)")
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
        print("(no se muestra a esta cuenta: solo a quien responde por guia.md y base/" + ("; sin consola, device_list_dir de la carpeta y lo de los últimos 14 días)" if SIN_FECHAS else ")"))
        return
    try:
        co = next((d for d in RAIZ.iterdir() if d.is_dir() and d.name.lower() == "claude outputs"), RAIZ / "Claude outputs")
        sueltos = sorted((p for p in co.rglob("*") if p.is_file() and not any(x.startswith(".") for x in p.relative_to(co).parts)),
                         key=lambda p: p.stat().st_mtime, reverse=True)
    except OSError:
        co, sueltos = RAIZ / "Claude outputs", []
    if not sueltos:
        print("(vacía o no existe)" if not SIN_FECHAS else "(sin consola no se ve en la copia: se mira con device_list_dir de la carpeta «Claude outputs» de la raíz)")
        return
    print(f"{len(sueltos)} archivos sueltos")
    for p in sueltos[:30]:
        f = "" if SIN_FECHAS else " · " + datetime.datetime.fromtimestamp(p.stat().st_mtime, TZ).date().isoformat()
        print(f"- {p.relative_to(co).as_posix()}{f}")
    if len(sueltos) > 30:
        print(f"(y {len(sueltos) - 30} más)")


area_activa = ACTIVO.split("/")[0] if ACTIVO and "/" in ACTIVO else None
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
            print(primera_frase(l_))
    if no_legibles:
        print(f"\n(no se pudieron leer: {len(no_legibles)})")
    claude_outputs()
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
    print("(no se pudo leer proyecto.md: el proyecto no existe, es restringido o no está descargado; se dice y se para)")
    claude_outputs()
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
    elif CUENTA in colaboran_en(seccion(cabecera(tp)[1], "Quién participa")):
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
dec_txt = leer(pc / "decisiones.md") or ""
ses_txt = leer(pc / "sesiones.md") or ""
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
    t = leer(carpeta / "decisiones.md")
    if not t:
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
claude_outputs()
