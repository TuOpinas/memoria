#!/usr/bin/env python3
"""Aplica a la raíz los cambios mecánicos de la cola de la Vista y reporta el resto.

La cola ("cambios" en la base de la página) trae seis tipos:
- fecha: cambio de fecha de un paso de «Siguientes pasos». Se aplica aquí, en la línea del paso.
- hecho: un paso marcado como hecho, con nota opcional. NO se aplica: cerrarlo bien pide
  quitar el paso, contar qué pasó en sesiones.md y a veces una decisión. Se reporta.
- nota: algo anotado para la próxima sesión. NO se aplica. Se reporta.
- prioridad: una prioridad del área marcada como cumplida o retirada. NO se aplica: area.md lo reescribe
  la sesión del dueño del área. Se reporta.
- corregir: quien usa el tablero dice que un paso no es lo que la vista cree (es rutina, es condicional, la fecha
  no es plazo, es decisión). NO se aplica: cambia dónde vive el paso o cómo se escribe, y eso es de sesión.
- propuesta: algo que el barrido de la puesta al día (`barrido.py`) vio que una sesión olvidó. NO se aplica nunca aquí:
  la memoria propone y solo su dueño decide, en una sesión. Se reporta aparte, en "propuestas", como lo que se queda
  en la cola a propósito. Una que no cumple la forma (id de proyecto, línea única) va a "rechazados" y se borra.

Uso: aplicar_cambios.py <raiz> <cambios.json | carpeta con un JSON por cambio> --cuenta <correo> [--dry-run]
Solo toca las áreas cuya columna «Cuenta» en la tabla de áreas de guia.md lleva ese correo, como dueño o tras
«colabora:», y los proyectos cuya línea «Colabora:» de «Quién participa» lo lleva: la puesta al día corre con la
cuenta de quien la lanza y nadie escribe en el área de otro (contrato, prohibición 4). Las prioridades del área
son solo de su dueño: las que marca quien colabora se quedan para él.
Sin --cuenta no se aplica nada.
Salida: JSON por stdout con "aplicados" (ids que ya están en la carpeta y se pueden borrar
de la cola), "sin_match" (fechas cuyo paso ya no existe tal cual: se quedan para la sesión), "rechazados" (lo que no
cumple la forma: se borra de la cola y se dice en el resumen), "errores" (no se pudo escribir:
se quedan en la cola y se reintentan en la próxima corrida), "para_sesion" (lo que no es una fecha,
de las áreas y proyectos donde la cuenta es dueña o colabora) y "para_su_dueno" (lo demás: se queda en la cola
hasta que su dueño ponga al día su tablero o cierre una sesión; no se toca).
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

def mis_areas():
    """(áreas de las que la cuenta es dueña, áreas en las que colabora), según la columna Cuenta de guia.md."""
    try:
        guia = (RAIZ / "guia.md").read_text(encoding="utf-8-sig")
    except OSError:
        return set(), set()
    m = re.search(r"^## Áreas\s*\n(.*?)(?=^## |\Z)", guia, re.S | re.M)
    if not m or not CUENTA:
        return set(), set()
    out, co, primera = set(), set(), True
    for l in m.group(1).split("\n"):
        if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
            continue
        if primera:
            primera = False; continue
        celdas = [c.strip() for c in l.strip().strip("|").split("|")]
        # cuentas enteras, no subcadenas: «ana@» no es «diana@»; y cinco columnas, como abrir.py y el generador
        if len(celdas) >= 5:
            de, cb, _ = cuentas(celdas[3])
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
    return CUENTA in colaboran_en(m.group(1) if m else "")

def puede(t, c, area):
    """Las prioridades del área son de su dueño; lo demás lo escribe también quien colabora en el área o en el proyecto."""
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
    if t in ("fecha", "hecho", "nota", "corregir", "prioridad", "propuesta") and c.get("proyecto") and not partes(c)[0]:
        rep["rechazados"].append({"id": c["id"], "detalle": f"id de proyecto mal formado: {c.get('proyecto')!r}"})
        continue
    if t in ("fecha", "hecho", "nota", "corregir", "prioridad", "propuesta") and not puede(t, c, area):
        rep["para_su_dueno"].append({"id": c["id"], "tipo": t, "proyecto": c.get("proyecto"), "area": area,
                                     "detalle": "falta --cuenta" if not CUENTA else (f"las prioridades de {area} son de su dueño" if t == "prioridad" and area in COLABORA else f"el área {area or '?'} no es de {CUENTA}")})
        continue
    if t == "fecha":
        try:
            estado, detalle = aplicar_fecha(c)
        except (OSError, UnicodeError) as e:   # sin permiso de escritura, archivo sin descargar…
            estado, detalle = "errores", f"{type(e).__name__}: {e}"
        rep[estado].append({"id": c["id"], "proyecto": c.get("proyecto"), "detalle": detalle})
    elif t in ("hecho", "nota", "corregir", "prioridad"):
        if any(not texto_de_una_linea(c[k]) for k in ("paso", "nota", "propuesta", "texto") if c.get(k) not in (None, "")):
            rep["rechazados"].append({"id": c["id"], "detalle": "paso, nota, propuesta o texto con saltos de línea"})
            continue
        rep["para_sesion"].append({k: c.get(k) for k in ("id", "tipo", "proyecto", "paso", "nota", "propuesta", "campo", "creado", "area", "indice", "texto")})
    elif t == "propuesta":
        if not partes(c)[0] or any(not texto_de_una_linea(c.get(k)) for k in ("texto",)) or \
           any(c.get(k) not in (None, "") and not texto_de_una_linea(c.get(k)) for k in ("por_que", "clase", "ruta", "afirma")) or \
           (c.get("rutas") is not None and not (isinstance(c["rutas"], list) and c["rutas"] and all(texto_de_una_linea(r) for r in c["rutas"]))):
            rep["rechazados"].append({"id": c["id"], "detalle": "propuesta sin proyecto «area--slug», sin texto, o con saltos de línea"})
            continue
        rep["propuestas"].append(c["id"])
    else:
        rep["sin_match"].append({"id": c["id"], "detalle": f"tipo desconocido: {t}"})
print(json.dumps(rep, ensure_ascii=False, indent=1))
