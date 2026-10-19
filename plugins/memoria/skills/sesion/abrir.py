#!/usr/bin/env python3
"""Lo que hay que leer para abrir una sesión, en una sola llamada y sin escribir nada.

Uso: abrir.py <raiz> [<area>/<proyecto>] [--cuenta <correo>]

Sin proyecto imprime el nivel 0 (primera línea de metodo.md, guia.md, premisas vigentes) y la lista de proyectos de
cada área legible, para saber cuál se abre. Con proyecto añade el nivel 1 (el bloque Proyectos de su área, proyecto.md,
las cinco decisiones y las tres sesiones más recientes, las cabeceras de entregables/) y los avisos de apertura:
cuestionamientos abiertos, decisiones de otros proyectos que lo nombran en «Afecta a:», entregables desfasados o en
borrador viejo, trabajo sin sesión y la fecha de base/contexto.md. Con --cuenta dice qué áreas son de esa cuenta y,
si es la del responsable de contexto, también los cuestionamientos a premisas.

Nunca abre taller/, fuentes/ ni restringido/ (de taller/ y fuentes/ del proyecto activo solo mira fechas), ni las
sesiones de otros proyectos. De las demás decisiones solo mira las líneas «Afecta a:», «Cuestiona a:» y «Responde a:»
y la cabecera de su entrada. Lo restringido no sale salvo que el proyecto activo esté dentro, y lo que no se deja leer
se cuenta, sin suponer qué hay.
"""
import datetime, os, pathlib, re, sys

RAIZ = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
if RAIZ is None or not (RAIZ / "guia.md").is_file():
    sys.exit("Uso: abrir.py <raiz> [<area>/<proyecto>] [--cuenta <correo>]  (la raíz es la carpeta con guia.md y metodo.md)")
args = [a for a in sys.argv[2:]]
CUENTA = None
if "--cuenta" in args:
    i = args.index("--cuenta"); CUENTA = (args[i + 1] if i + 1 < len(args) else "").strip().lower(); del args[i:i + 2]
ACTIVO = args[0].strip("/") if args else None
try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Mexico_City")
except Exception:
    TZ = None
HOY = datetime.datetime.now(TZ).date()
FECHA = re.compile(r"\b(20\d\d-\d\d-\d\d)\b")
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
        out.append({"fecha": f.group(1) if f else "", "cab": cab[3:].strip(), "texto": p.rstrip()})
    return out


def recientes(texto, n):
    es = entradas(texto)
    return sorted(es, key=lambda e: e["fecha"], reverse=True)[:n]


def fecha_ok(f):
    try:
        datetime.date.fromisoformat(f); return True
    except (TypeError, ValueError):
        return False


def mtime(p):
    try:
        return datetime.datetime.fromtimestamp(os.stat(p).st_mtime, TZ).date()   # el día en Ciudad de México, como el tablero
    except OSError:
        return None


def titulo(n):
    print(f"\n=== {n}")


# ---------- nivel 0 ----------
try:
    with open(RAIZ / "metodo.md", encoding="utf-8-sig", errors="replace") as f_:
        linea_metodo = f_.readline().strip()
except OSError:
    linea_metodo = "(sin metodo.md)"
guia = leer(RAIZ / "guia.md") or ""
print("=== METODO (primera línea)")
print(linea_metodo)
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
        areas.append({"slug": c[0].strip("`").rstrip("/"), "dueno": c[2], "cuenta": c[3].lower(), "restringida": "restring" in c[4].lower()})
contexto = re.search(r"^Contexto común:\s*(.+)$", seccion(guia, "Quién responde por qué"), re.M | re.I)
resp_contexto = contexto.group(1).strip().rstrip(".") if contexto else ""
es_resp = bool(CUENTA) and any(a["cuenta"] == CUENTA and a["dueno"] and a["dueno"] in resp_contexto for a in areas)

premisas = []
for l in (leer(RAIZ / "base" / "premisas.md") or "").split("\n"):
    m = re.match(r"^\s*-\s*(P\d+)\s*·\s*(.+)$", l)
    if m:
        r = re.search(r"Reemplaza a\s+(P\d+)", m.group(2), re.I)
        premisas.append((m.group(1).upper(), l.strip(), r.group(1).upper() if r else None))
reemplazadas = {r for _, _, r in premisas if r}
titulo("PREMISAS VIGENTES")
print("\n".join(l for pid, l, _ in premisas if pid not in reemplazadas) or "(no hay base/premisas.md o no tiene premisas)")

if CUENTA:
    titulo("CUENTA")
    mias = [a["slug"] for a in areas if a["cuenta"] == CUENTA]
    print(f"{CUENTA}: escribe en {', '.join(mias) if mias else 'ninguna área (preguntar en cuál trabaja antes de escribir)'}"
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
print(seccion(cabecera(area_txt)[1], "Proyectos") if area_txt is not None else "(no se pudo leer area.md: restringida o sin descargar)")
tp = leer(pc / "proyecto.md")
if tp is None:
    titulo("PROYECTO")
    print("(no se pudo leer proyecto.md: el proyecto no existe, es restringido o no está descargado; se dice y se para)")
    sys.exit(0)
titulo(f"PROYECTO {ACTIVO}/proyecto.md")
print(tp.strip())
dec_txt = leer(pc / "decisiones.md") or ""
ses_txt = leer(pc / "sesiones.md") or ""
titulo("DECISIONES (las 5 más recientes)")
print("\n\n".join(e["texto"] for e in recientes(dec_txt, 5)) or "(ninguna)")
titulo("SESIONES (las 3 más recientes)")
ses = recientes(ses_txt, 3)
print("\n\n".join(e["texto"] for e in ses) or "(ninguna)")
ultima_ses = next((e["fecha"] for e in sorted(entradas(ses_txt), key=lambda e: e["fecha"], reverse=True) if fecha_ok(e["fecha"])), None)

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
            if c.is_file() and "restringido" not in c.parts:
                tb = leer(c)
                fb = cabecera(tb)[0].get("actualizado") if tb else None
                if fecha_ok(fb) and fecha_ok(act) and fb > act:
                    mas_nuevas.append(f"{b_} ({fb})")
                break
    if mas_nuevas:
        avisos.append(f"Puede estar desfasado: entregables/{n} (actualizado {act}) se basa en algo más nuevo: {', '.join(mas_nuevas)}.")
    if fecha_ok(act) and ultima_ses and act > ultima_ses:
        avisos.append(f"Trabajo sin sesión: entregables/{n} tiene actualizado {act}, posterior a la última sesión ({ultima_ses}).")

# trabajo sin sesión por fechas de archivo (nunca el contenido) en entregables/, taller/ y fuentes/
if ultima_ses:
    lim = datetime.date.fromisoformat(ultima_ses)
    donde = {}
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
            if f"{a['slug']}/{slug}" != ACTIVO and slug in idx and declarado(idx[slug]["linea"]):
                continue
            yield a["slug"], slug, carpeta / slug
        # decisiones dentro de restringido/ solo si el proyecto activo está dentro
        for r_, ds, fs in os.walk(carpeta):
            ds[:] = [x for x in ds if not x.startswith(".")]
            if "restringido" in pathlib.Path(r_).relative_to(carpeta).parts and "decisiones.md" in fs:
                if (RAIZ / ACTIVO) in pathlib.Path(r_).parents or pathlib.Path(r_) == RAIZ / ACTIVO:
                    yield a["slug"], rel(r_), pathlib.Path(r_)


respuestas, cuestiona, afecta = set(), [], []
patron_proy = re.compile(r"(?<![\w/-])" + re.escape(ACTIVO) + r"(?![\w-])")
for a_slug, slug, carpeta in proyectos_legibles():
    t = leer(carpeta / "decisiones.md")
    if not t:
        continue
    origen = f"{a_slug}/{slug}" if "/" not in slug else slug
    # identificador de cada entrada: fecha y -2, -3… contando desde la más antigua del mismo día (de abajo arriba)
    es = entradas(t)
    cuenta = {}
    for e in reversed(es):
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
            continue
        if campos["Cuestiona a"]:
            m = re.search(r"([a-z0-9][\w.-]*/[a-z0-9][\w.-]*)#", campos["Cuestiona a"])
            mp = re.search(r"premisa\s+(P\d+)", campos["Cuestiona a"], re.I)
            if (m and m.group(1) == ACTIVO) or (mp and es_resp):
                cuestiona.append((origen, e, campos, ("premisa", mp.group(1).upper()) if mp and not m else None))
        if campos["Afecta a"] and patron_proy.search(campos["Afecta a"]):
            afecta.append((origen, e, campos))

# un cuestionamiento sigue abierto si nadie respondió a su identificador; una premisa nueva que reemplaza a la
# cuestionada después del cuestionamiento también lo responde
reemplazo_fecha = {}
for pid, l, r in premisas:
    f = FECHA.search(l)
    if r:
        reemplazo_fecha[r] = f.group(1) if f else ""
for origen, e, c, prem in cuestiona:
    if (origen, e["id"]) in respuestas:
        continue
    if prem and prem[1] in reemplazo_fecha and reemplazo_fecha[prem[1]] >= e["fecha"]:
        continue
    objetivo = f"la premisa {prem[1]}" if prem else c["Cuestiona a"]
    avisos.insert(0, f"Cuestionamiento abierto ({origen}#{e['id']}): «{e['cab']}». Planteó: {c['Planteó'] or c['Decidió'] or 'no consta'}. "
                     f"Cuestiona a: {objetivo}. Por qué: {c['Por qué'][:300]}")
nuevos = [x for x in afecta if not ultima_ses or x[1]["fecha"] > ultima_ses]
for origen, e, c in sorted(nuevos, key=lambda x: x[1]["fecha"], reverse=True):
    avisos.append(f"Le afecta una decisión de {origen} ({origen}#{e['id']}): «{e['cab']}». Decidió: {c['Decidió'] or 'no consta'}. Afecta a: {c['Afecta a'][:300]}")
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
