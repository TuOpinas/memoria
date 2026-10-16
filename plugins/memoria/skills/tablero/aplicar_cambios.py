#!/usr/bin/env python3
"""Aplica a la raíz los cambios mecánicos de la cola de la Vista y reporta el resto.

La cola ("cambios" en la base de la página) trae cinco tipos:
- fecha: cambio de fecha de un paso de «Siguientes pasos». Se aplica aquí, en la línea del paso.
- hecho: un paso marcado como hecho, con nota opcional. NO se aplica: cerrarlo bien pide
  quitar el paso, contar qué pasó en sesiones.md y a veces una decisión. Se reporta.
- nota: algo anotado para la próxima sesión. NO se aplica. Se reporta.
- prioridad: una prioridad del área marcada como cumplida o retirada. NO se aplica: area.md lo reescribe
  la sesión del dueño del área. Se reporta.
- corregir: quien usa el tablero dice que un paso no es lo que la vista cree (es rutina, es condicional, la fecha
  no es plazo, es decisión). NO se aplica: cambia dónde vive el paso o cómo se escribe, y eso es de sesión.

Uso: aplicar_cambios.py <raiz> <cambios.json | carpeta con un JSON por cambio> --cuenta <correo> [--dry-run]
Solo toca las áreas cuya columna «Cuenta» en la tabla de áreas de guia.md lleva ese correo: la puesta
al día corre con la cuenta de quien la lanza y nadie escribe en el área de otro (contrato, prohibición 4).
Sin --cuenta no se aplica nada.
Salida: JSON por stdout con "aplicados" (ids que ya están en la carpeta y se pueden borrar
de la cola), "sin_match" (fechas cuyo paso ya no existe tal cual), "errores" (no se pudo escribir:
se quedan en la cola y se reintentan en la próxima corrida), "para_sesion" (lo que no es una fecha,
de las áreas de la cuenta) y "para_su_dueno" (todo lo de áreas de otra cuenta: se queda en la cola
hasta que su dueño ponga al día su tablero o cierre una sesión; no se toca).
Una fecha aplicada no toca la fecha «actualizado» de la cabecera: es un cambio mecánico, no trabajo
sobre el proyecto, y moverla escondería en el tablero los plazos vencidos de los demás pasos.
"""
import sys, re, json, pathlib

RAIZ = pathlib.Path(sys.argv[1])
ENTRADA = pathlib.Path(sys.argv[2])
DRY = "--dry-run" in sys.argv
CUENTA = (sys.argv[sys.argv.index("--cuenta") + 1] if "--cuenta" in sys.argv and len(sys.argv) > sys.argv.index("--cuenta") + 1 else "").strip().lower()

def mis_areas():
    """Slugs de las áreas de guia.md cuya columna Cuenta lleva el correo de --cuenta."""
    try:
        guia = (RAIZ / "guia.md").read_text(encoding="utf-8-sig")
    except OSError:
        return set()
    m = re.search(r"^## Áreas\s*\n(.*?)(?=^## |\Z)", guia, re.S | re.M)
    if not m or not CUENTA:
        return set()
    out, primera = set(), True
    for l in m.group(1).split("\n"):
        if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
            continue
        if primera:
            primera = False; continue
        celdas = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(celdas) >= 4 and CUENTA in celdas[3].lower():
            out.add(celdas[0].strip("`").rstrip("/"))
    return out

MIAS = mis_areas()

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
    area, _, slug = (c.get("proyecto") or "").partition("--")
    p = RAIZ / area / slug / "proyecto.md"
    if not p.exists():
        return "sin_match", f"no existe {area}/{slug}/proyecto.md"
    if not c.get("paso"):
        return "sin_match", "el cambio no dice a qué paso se refiere"
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

rep = {"aplicados": [], "sin_match": [], "errores": [], "para_sesion": [], "para_su_dueno": [],
       "cuenta": CUENTA, "mis_areas": sorted(MIAS), "dry_run": DRY}
for c in cargar():
    t = c.get("tipo")
    area = (c.get("proyecto") or "").partition("--")[0] or c.get("area") or ""
    if t in ("fecha", "hecho", "nota", "corregir", "prioridad") and (not CUENTA or (area and area not in MIAS)):
        rep["para_su_dueno"].append({"id": c["id"], "tipo": t, "proyecto": c.get("proyecto"), "area": area,
                                     "detalle": "falta --cuenta" if not CUENTA else f"el área {area or '?'} no es de {CUENTA}"})
        continue
    if t == "fecha":
        try:
            estado, detalle = aplicar_fecha(c)
        except (OSError, UnicodeError) as e:   # sin permiso de escritura, archivo sin descargar…
            estado, detalle = "errores", f"{type(e).__name__}: {e}"
        rep[estado].append({"id": c["id"], "proyecto": c.get("proyecto"), "detalle": detalle})
    elif t in ("hecho", "nota", "corregir", "prioridad"):
        rep["para_sesion"].append({k: c.get(k) for k in ("id", "tipo", "proyecto", "paso", "nota", "propuesta", "campo", "creado", "area", "indice", "texto")})
    else:
        rep["sin_match"].append({"id": c["id"], "detalle": f"tipo desconocido: {t}"})
print(json.dumps(rep, ensure_ascii=False, indent=1))
