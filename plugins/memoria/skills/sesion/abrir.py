#!/usr/bin/env python3
"""Lo que hay que leer para abrir una sesión, en una sola llamada y sin escribir nada.

Uso: abrir.py <raiz> [<area>/<proyecto>] [--cuenta <correo>] [--plugin "<primera línea del metodo.md del plugin>"]

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
"""
import datetime, os, pathlib, re, sys

RAIZ = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
if RAIZ is None or not (RAIZ / "guia.md").is_file():
    sys.exit("Uso: abrir.py <raiz> [<area>/<proyecto>] [--cuenta <correo>] [--plugin \"<primera línea del metodo.md del plugin>\"]  (la raíz es la carpeta con guia.md y metodo.md)")
args = [a for a in sys.argv[2:]]
CUENTA = None
if "--cuenta" in args:
    i = args.index("--cuenta"); CUENTA = (args[i + 1] if i + 1 < len(args) else "").strip().lower(); del args[i:i + 2]
PLUGIN = None
if "--plugin" in args:
    i = args.index("--plugin"); PLUGIN = (args[i + 1] if i + 1 < len(args) else "").strip(); del args[i:i + 2]
ACTIVO = args[0].strip("/") if args else None
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
    try:
        return pathlib.Path(p).read_bytes().decode("utf-8-sig", errors="replace").replace("\r\n", "\n")
    except FileNotFoundError:
        return None
    except OSError:
        no_legibles.append(rel(p))   # sin permiso o sin descargar: se cuenta, sin suponer qué hay
        return None


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




def mtime(p):
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
    """(dueño, colaboran, aviso) de una celda Cuenta: «dueno@x · colabora: a@x, b@x». Falla cerrado:
    con más de un correo antes de la palabra, o ninguno, nadie es dueño; cualquier palabra que empiece por
    «colabor» separa, para que «colaboradora:» o «colabora» sin dos puntos no conviertan a nadie en dueño."""
    texto = (celda or "").lower()
    partes = PALABRA_COLABORA.split(texto, maxsplit=1)
    antes = set(CORREO.findall(partes[0]))
    despues = set(CORREO.findall(partes[1])) if len(partes) > 1 else set()
    aviso = None
    if len(antes) > 1:
        aviso = "más de un correo antes de «colabora:»; nadie es dueño hasta que se corrija"
        antes = set()
    elif not antes:
        aviso = "sin el correo del dueño"
    elif len(partes) > 1 and not re.search(r"\bcolabora\s*:", texto):
        aviso = "la palabra para quien colabora va escrita «colabora:»"
    return antes, despues, aviso
def colaboran_en(quien):
    """Las cuentas de las líneas «Colabora:» de «Quién participa» de un proyecto (todas las líneas)."""
    return set(c for l in (quien or "").split("\n") if LINEA_COLABORA.match(l) for c in CORREO.findall(l.lower()))
# --- fin de quién escribe ---


# ---------- nivel 0 ----------
try:
    with open(RAIZ / "metodo.md", encoding="utf-8-sig", errors="replace") as f_:
        linea_metodo = f_.readline().strip()
except OSError:
    linea_metodo = "(sin metodo.md)"
guia = leer(RAIZ / "guia.md") or ""
print("=== METODO (primera línea)")
print(linea_metodo)

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
titulo("GUIA")
print(guia.strip())

areas = []
filas = seccion(guia, "Áreas").split("\n")
cab_vista = False
for l in filas:
    if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
        continue
    if not cab_vista:
        cab_vista = True; continue
    c = [x.strip() for x in l.strip().strip("|").split("|")]
    if len(c) >= 5:
        de, co, av = cuentas(c[3])
        if av:
            print(f"(aviso: la celda Cuenta de «{c[0].strip('`')}» en guia.md: {av})")
        areas.append({"slug": c[0].strip("`").rstrip("/"), "dueno": c[2], "cuentas_dueno": de, "colaboran": co, "restringida": "restring" in c[4].lower()})
    else:
        print(f"(aviso: la fila «{c[0].strip('`')}» de la tabla de áreas de guia.md tiene {len(c)} columnas y hacen falta 5; esa área no se lee hasta que se corrija)")
if ZONA_AVISO:
    print(f"(aviso: {ZONA_AVISO})")
if not areas:
    print("(aviso: no se encontró ninguna área en la sección «## Áreas» de guia.md: sin ella nadie tiene área ni cuenta; que el responsable de contexto revise guia.md)")
# como el tablero: la línea que empieza por «Contexto común», cortada por su primer «:» (la plantilla de `nuevo` escribe
# «Contexto común (`guia.md` y `base/`): Nombre (correo).»); sin correo, la cuenta del responsable es la de las áreas
# de las que es dueño
resp_contexto = ""
for l in seccion(guia, "Quién responde por qué").split("\n"):
    if l.strip().lower().startswith("contexto común"):
        resp_contexto = l.split(":", 1)[-1].strip().rstrip(".").strip()
# la cuenta del responsable va entre paréntesis en esa misma línea («Contexto común: Nombre (correo)»); sin ella,
# como antes, es la de las áreas de las que esa persona es dueña
cuenta_resp = set(CORREO.findall(resp_contexto.lower()))
resp_contexto = re.sub(r"\s*\([^)]*\)", "", resp_contexto).strip()
es_resp = bool(CUENTA) and (CUENTA in cuenta_resp or (bool(resp_contexto) and not cuenta_resp and any(CUENTA in a["cuentas_dueno"] and a["dueno"].strip().lower() == resp_contexto.lower() for a in areas)))

premisas = []
for l in (leer(RAIZ / "base" / "premisas.md") or "").split("\n"):
    m = re.match(r"^\s*-\s*(P\d+)\s*·\s*(.+)$", l)
    if m:
        partes = [x.strip() for x in m.group(2).split("·")]
        r = next((re.search(r"P\d+", x, re.I).group(0).upper() for x in partes[1:] if x.lower().startswith("reemplaza a") and re.search(r"P\d+", x, re.I)), None)
        f = next((x for x in partes[1:] if re.fullmatch(r"20\d\d-\d\d-\d\d", x)), "")
        premisas.append((m.group(1).upper(), l.strip(), r, f))
reemplazadas = {r for _, _, r, _ in premisas if r}
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
    donde_ = ", ".join([f"{s} (dueño)" for s in mias] + [f"{s} (colabora)" for s in colab] + [f"{s} (colabora en el proyecto)" for s in proy_co])
    print(f"{CUENTA}: escribe en {donde_ if donde_ else 'ninguna área (preguntar en cuál trabaja antes de escribir)'}"
          + ("; es la del responsable de contexto (también guia.md y base/)" if es_resp else ""))


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


area_activa = ACTIVO.split("/")[0] if ACTIVO and "/" in ACTIVO else None
if not ACTIVO:
    titulo("PROYECTOS POR ÁREA (para saber cuál se abre)")
    for a in areas:
        if a["restringida"]:
            print(f"- {a['slug']}/ · restringida, dueño {a['dueno']}"); continue
        t = leer(RAIZ / a["slug"] / "area.md")
        if t is None:
            motivo = "su carpeta no está en esta computadora" if not (RAIZ / a["slug"]).exists() else "no se pudo leer"
            print(f"- {a['slug']}/ · {motivo}, dueño {a['dueno']}"); continue
        for slug, d in indice_proyectos(t).items():
            print(d["linea"].replace(f"`{slug}/`", f"`{a['slug']}/{slug}/`", 1))
    if no_legibles:
        print(f"\n(no se pudieron leer: {len(no_legibles)})")
    sys.exit(0)

# ---------- nivel 1 ----------
if "/" not in ACTIVO:
    sys.exit(f"El proyecto va como <area>/<proyecto>, no «{ACTIVO}».")
pc = RAIZ / ACTIVO
area_txt = leer(RAIZ / area_activa / "area.md")
titulo(f"AREA {area_activa} · bloque Proyectos")
def motivo_area(slug):
    """El mismo motivo que da el nivel 0: sin carpeta, restringida según guia.md, o no se pudo leer."""
    if not (RAIZ / slug).exists():
        return "su carpeta no está en esta computadora"
    if any(a["slug"] == slug and a["restringida"] for a in areas):
        return "restringida para esta cuenta"
    return "no se pudo leer: sin permiso o sin descargar"
print(seccion(cabecera(area_txt)[1], "Proyectos") if area_txt is not None else f"(no se pudo leer area.md: {motivo_area(area_activa)})")
tp = leer(pc / "proyecto.md")
if tp is None:
    titulo("PROYECTO")
    print("(no se pudo leer proyecto.md: el proyecto no existe, es restringido o no está descargado; se dice y se para)")
    sys.exit(0)
titulo(f"PROYECTO {ACTIVO}/proyecto.md")
print(tp.strip())
if CUENTA:
    # colaborar en un solo proyecto: una línea «Colabora:» en «Quién participa» con la cuenta entre paréntesis
    a_act = next((a for a in areas if a["slug"] == area_activa), None)
    if a_act and CUENTA in a_act["cuentas_dueno"]:
        rol = "dueño del área"
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
for n_ in ("proyecto.md", "decisiones.md", "sesiones.md"):
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
ses = recientes(ses_txt, 3)
print("\n\n".join(e["texto"] for e in ses) or "(ninguna)")
ultima_ses = next((e["fecha"] for e in sorted(entradas(ses_txt), key=lambda e: e["fecha"], reverse=True) if fecha_ok(e["fecha"])), None)
# para los avisos de otras áreas cuenta la última sesión de trabajo: las entradas «(tarea)» o «(tablero)» no son sesiones
ultima_real = next((e["fecha"] for e in sorted(entradas(ses_txt), key=lambda e: e["fecha"], reverse=True)
                    if fecha_ok(e["fecha"]) and not re.search(r"\((tarea|tablero)\)", e["cab"], re.I)), None)
cerrado = bool(re.search(r"Proyecto terminado el\s*20\d\d-\d\d-\d\d", seccion(cabecera(tp)[1], "Estado actual")))

titulo("ENTREGABLES (cabeceras)")
avisos = []
ents = []
d = pc / "entregables"
try:
    nombres = sorted(n for n in os.listdir(d) if not n.startswith(".") and (d / n).is_file()) if d.exists() else []
except OSError:
    nombres = []
for n in nombres:
    p = d / n
    if not n.endswith(".md"):
        print(f"- {n} · sin cabecera (fecha de archivo {mtime(p)})"); continue
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
if ultima_ses and not cerrado:
    lim = datetime.date.fromisoformat(ultima_ses)
    donde = {}
    md = mtime(pc / "decisiones.md")
    if md and md > lim:
        donde["decisiones"] = 1
    for sub in ("entregables", "taller", "fuentes"):
        for r_, ds, fs in os.walk(pc / sub):
            ds[:] = [x for x in ds if not x.startswith(".") and x != "restringido"]
            for f in fs:
                m_ = mtime(os.path.join(r_, f))
                if not f.startswith(".") and m_ and m_ > lim:
                    donde[sub] = donde.get(sub, 0) + 1
    if donde:
        avisos.append("Trabajo sin sesión por fecha de archivo, después del " + ultima_ses + ": "
                      + ", ".join(f"{k} {v}" for k, v in donde.items()) + " (se pregunta qué pasó y se propone registrarlo).")

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
        avisos.insert(0, f"Un cuestionamiento sin fecha válida en {origen} («{e['cab']}») nombra este proyecto: no tiene identificador y no se puede responder hasta que su dueño lo registre con fecha.")
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
# a quien cuestionó: la respuesta del dueño, si llegó después de su última sesión
for origen, e, c, cid in me_responden:
    if cid not in mis_cuestionamientos:
        continue   # «Responde a» apunta a una entrada de este proyecto que no es un cuestionamiento
    if not e["fecha"]:
        avisos.append(f"Una entrada sin fecha válida de {origen} responde a tu cuestionamiento {ACTIVO}#{cid} («{e['cab']}»): conviene que su dueño la registre con fecha.")
    elif not ultima_real or e["fecha"] >= ultima_real:
        avisos.insert(0, f"Respondieron tu cuestionamiento {ACTIVO}#{cid} («{mis_cuestionamientos[cid][0]}»): {origen}#{e['id']}, «{e['cab']}». Decidió: {c['Decidió'] or 'no consta'}. Por qué: {c['Por qué'][:300]}")
# una premisa cuestionada desde aquí y reemplazada después por otra: también es una respuesta
for cid, (cab_, fecha_, prem_) in mis_cuestionamientos.items():
    if prem_ and prem_ in reemplazo_fecha and reemplazo_fecha[prem_] != "9999" and reemplazo_fecha[prem_] >= fecha_ and (not ultima_real or reemplazo_fecha[prem_] >= ultima_real):
        nueva = next((l for pid, l, r, f in premisas if r == prem_), "")
        avisos.insert(0, f"Respondieron tu cuestionamiento {ACTIVO}#{cid} («{cab_}»): la premisa {prem_} se reemplazó el {reemplazo_fecha[prem_]}: {nueva}")
for origen, e, c in sin_fecha:
    avisos.append(f"Una entrada sin fecha válida de {origen} nombra este proyecto en «Afecta a» («{e['cab']}»): no se puede citar ni saber si es nueva; conviene que su dueño la revise.")
viejos = len(afecta) - len(nuevos)

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
