#!/usr/bin/env bash
# Comprueba la raíz de una organización contra el contrato, sin escribir nada. De cada .md
# lee la cabecera y busca enlaces wiki y rutas absolutas; no lee fuentes/ ni restringido/.
# Una carpeta que no se deja leer (restringida para esta cuenta) se salta sin más.
#
#   ./verificar.sh <ruta-a-la-raiz>
#
# Sale con 1 si hay hallazgos, 0 si la raíz está limpia.
set -euo pipefail
RAIZ="${1:?Falta la ruta de la raíz}"
python3 - "$RAIZ" <<'PY'
import os, re, sys, unicodedata
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

raiz = sys.argv[1]
ESTADOS = {"borrador", "vigente", "reemplazado"}
PROHIBIDAS = {"varios", "otros", "temp", "borrador", "metodo", "plantillas"}
hallazgos = set()
SUELTOS_OK = {"guia.md", "metodo.md", "desktop.ini", "Icon\r"}
ROTADO = re.compile(r"^(sesiones|decisiones)-\d{4}(-\d+)?\.md$")   # el registro que se rota por año

def h(clase, ruta, detalle=""):
    hallazgos.add((clase, ruta, detalle))

def ls(p):
    try:
        return sorted(os.listdir(p))
    except OSError:
        return []

def rel(p):
    return os.path.relpath(p, raiz)

def cabecera(path):
    try:
        txt = open(path, encoding="utf-8-sig", errors="replace").read()
    except OSError:
        return None, ""
    if not txt.startswith("---\n"):
        return None, txt
    fin = txt.find("\n---", 4)
    return (txt[4:fin] if fin != -1 else ""), txt

def nombre_ok(n):
    base = n[:-3] if n.endswith(".md") else n
    if base != base.lower():
        return False
    if any(unicodedata.category(c) == "Mn" for c in unicodedata.normalize("NFD", base)):
        return False
    return re.fullmatch(r"[a-z0-9][a-z0-9-]*", base) is not None

def nombre_con_orden_version_o_fecha(n):
    base = n[:-3] if n.endswith(".md") else n
    return bool(re.match(r"^\d+-", base) or re.search(r"(^|-)v\d+($|-)", base) or re.search(r"\d{4}-\d{2}-\d{2}", base))

def seccion_proyectos(txt):
    m = re.search(r"^## Proyectos\s*\n(.*?)(?=^## |\Z)", txt, re.S | re.M)
    return m.group(1) if m else ""

# --- raíz ---
for req in ("guia.md", "metodo.md", "base/contexto.md", "base/glosario.md", "base/sistemas.md"):
    if not os.path.exists(os.path.join(raiz, req)):
        h("falta en la raíz", req)
for extra in ("base/ajustes.md", "base/plantillas"):
    if os.path.exists(os.path.join(raiz, extra)):
        h("ya no existe en el método", extra, "lo propio de la organización va en guia.md")

areas = []
for nombre in ls(raiz):
    ruta = os.path.join(raiz, nombre)
    if nombre.startswith("."):
        continue
    if os.path.isfile(ruta):
        if nombre not in SUELTOS_OK:
            h("archivo suelto en la raíz", nombre)
        continue
    if nombre in ("base", ".git"):
        continue
    if nombre.lower() == "claude outputs":
        n = sum(1 for _, _, fs in os.walk(ruta) for f in fs if not f.startswith("."))
        if n:
            h("archivos de Claude sin proyecto", nombre, "%d archivo%s: cada uno va a su proyecto («ordena Claude outputs»)" % (n, "" if n == 1 else "s"))
        continue
    areas.append((nombre, ruta))
    if not nombre_ok(nombre) or nombre_con_orden_version_o_fecha(nombre):
        h("nombre de carpeta", nombre, *([] if nombre_ok(nombre) else ["con espacios, mayúsculas o acentos, las referencias a sus decisiones («Afecta a», «Cuestiona a», «Responde a») dejan de funcionar"]))

# --- guia.md: el mapa que leen abrir.py y el tablero ---
# La tabla de áreas es lo que da a cada cuenta su área: una fila con columnas de menos, un encabezado distinto
# de «## Áreas» o una cuenta sin «@» dejan a alguien sin área sin que nadie lo note.
guia_areas = {}
try:
    guia_txt = open(os.path.join(raiz, "guia.md"), encoding="utf-8-sig", errors="replace").read()
except OSError:
    guia_txt = ""
if guia_txt:
    if not re.search(r"^## Áreas\s*$", guia_txt, re.M):
        h("guia.md sin la sección «## Áreas»", "guia.md", "con ese título exacto; es la que leen abrir.py y el tablero")
    m = re.search(r"^## Áreas\s*\n(.*?)(?=^## |\Z)", guia_txt, re.S | re.M)
    primera = True
    for l in (m.group(1) if m else "").split("\n"):
        if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
            continue
        if primera:
            primera = False; continue
        celdas = [c.strip() for c in l.strip().strip("|").split("|")]
        slug = celdas[0].strip("`").rstrip("/")
        if len(celdas) < 5:
            h("fila de la tabla de áreas con columnas de menos", "guia.md", "«%s» tiene %d y hacen falta 5 (área, qué es, dueño, cuenta, quién la lee)" % (slug, len(celdas))); continue
        guia_areas[slug] = {"dueno": celdas[2], "cuenta": celdas[3]}
        _de, _co, _av = cuentas(celdas[3])
        if _av:
            h("celda Cuenta mal escrita en guia.md", slug, _av + ": primero el correo del dueño y, si hace falta, «· colabora: correo, correo»")
        if PALABRA_COLABORA.search(celdas[3]) and not _co:
            h("«colabora:» sin cuentas en guia.md", slug, "detrás de «colabora:» van los correos de quienes colaboran, separados por comas")
        if not os.path.isdir(os.path.join(raiz, slug)):
            h("área del mapa sin carpeta", slug, "está en la tabla de guia.md y no hay carpeta con ese nombre")
    if m and not guia_areas:
        h("tabla de áreas vacía", "guia.md")
    if not re.search(r"^Contexto común", guia_txt, re.M):
        h("guia.md sin «Contexto común»", "guia.md", "la línea que dice quién mantiene guia.md y base/")
    _z = re.search(r"^\s*[-*]?\s*\**\s*zona horaria\s*\**\s*:\s*\**\s*`?\s*([A-Za-z0-9_+-]+(?:/[A-Za-z0-9_+-]+){0,2})", guia_txt, re.M | re.I)
    if _z:
        try:
            from zoneinfo import ZoneInfo
            ZoneInfo(_z.group(1))
        except ImportError:
            pass
        except Exception:
            h("zona horaria no válida en guia.md", "guia.md", "«%s»: tiene que ser una zona como America/Mexico_City o Europe/Madrid" % _z.group(1))

# --- áreas y proyectos ---
for area, aruta in areas:
    amd = os.path.join(aruta, "area.md")
    if not os.path.exists(amd):
        h("área sin area.md", area); continue
    fm, txt = cabecera(amd)
    if guia_txt and area not in guia_areas:
        h("carpeta de área que no está en guia.md", area, "sin su fila en la tabla de áreas nadie escribe en ella")
    md = re.search(r"^Dueñ[oa]: *(.+?)\s*$", txt, re.M)
    if not md:
        h("área sin dueño", rel(amd))
    elif area in guia_areas and md.group(1).strip().lower() != guia_areas[area]["dueno"].strip().lower():
        h("dueño distinto en guia.md y en area.md", area, "guia.md dice «%s» y area.md «%s»" % (guia_areas[area]["dueno"], md.group(1).strip()))
    if "## Proyectos" not in txt:
        h("area.md sin bloque Proyectos", rel(amd))
    bloque = seccion_proyectos(txt)

    for proj in ls(aruta):
        pruta = os.path.join(aruta, proj)
        if not os.path.isdir(pruta) or proj.startswith("."):
            continue
        if not nombre_ok(proj) or nombre_con_orden_version_o_fecha(proj):
            h("nombre de carpeta", rel(pruta), *([] if nombre_ok(proj) else ["con espacios, mayúsculas o acentos, las referencias a sus decisiones («Afecta a», «Cuestiona a», «Responde a») dejan de funcionar"]))
        if not os.path.exists(os.path.join(pruta, "proyecto.md")):
            h("carpeta en un área que no es un proyecto", rel(pruta)); continue

        for req in ("proyecto.md", "decisiones.md", "sesiones.md"):
            if not os.path.exists(os.path.join(pruta, req)):
                h("proyecto incompleto", rel(pruta), "falta " + req)
        for d in ("entregables", "taller", "fuentes"):
            if not os.path.isdir(os.path.join(pruta, d)):
                h("proyecto incompleto", rel(pruta), "falta " + d + "/")

        for x in ls(pruta):
            xr = os.path.join(pruta, x)
            if os.path.isdir(xr) and x not in ("entregables", "taller", "fuentes", "restringido") and not x.startswith("."):
                h("carpeta que la estructura no contempla", rel(xr))
            if x.lower() in PROHIBIDAS:
                h("carpeta prohibida", rel(xr))
            if os.path.isfile(xr) and x.endswith(".md") and x not in ("proyecto.md", "decisiones.md", "sesiones.md") and not ROTADO.match(x):
                h("archivo suelto en la raíz del proyecto", rel(xr))

        # un solo nivel de agrupación dentro de entregables/, taller/ y fuentes/
        for sub in ("entregables", "taller", "fuentes"):
            sruta = os.path.join(pruta, sub)
            if not os.path.isdir(sruta):
                continue
            for g in ls(sruta):
                gr = os.path.join(sruta, g)
                if sub == "taller" and g in ("decisiones.md", "sesiones.md"):
                    h("registro dentro de taller/", rel(gr), "los registros del proyecto son los de su raíz")
                if os.path.isdir(gr) and not g.startswith("."):
                    if sub != "fuentes" and (not nombre_ok(g) or nombre_con_orden_version_o_fecha(g)):
                        h("nombre de carpeta", rel(gr))
                    for gg in ls(gr):
                        if os.path.isdir(os.path.join(gr, gg)) and not gg.startswith("."):
                            h("un nivel de agrupación de más", rel(os.path.join(gr, gg)))

        # restringido/ es plano
        rruta = os.path.join(pruta, "restringido")
        if os.path.isdir(rruta):
            for g in ls(rruta):
                if os.path.isdir(os.path.join(rruta, g)) and not g.startswith("."):
                    h("subcarpeta dentro de restringido/", rel(os.path.join(rruta, g)), "es plano")

        # el bloque Proyectos tiene que listar todos los entregables vigentes,
        # salvo en un proyecto cerrado, que ocupa solo su línea
        pfm, ptxt = cabecera(os.path.join(pruta, "proyecto.md"))
        cerrado = "Proyecto terminado el" in ptxt
        _qp = re.search(r"^## Quién participa\s*\n(.*?)(?=^## |\Z)", ptxt or "", re.S | re.M)
        for _l in (_qp.group(1).split("\n") if _qp else []):
            if LINEA_COLABORA.match(_l) and not re.search(r"\([^)]*@[^)]*\)", _l):
                h("«Colabora:» sin cuentas en proyecto.md", rel(pruta), "cada persona va como «Nombre Apellido (correo)»: sin la cuenta no se sabe quién escribe")
        ed = os.path.join(pruta, "entregables")
        if os.path.isdir(ed) and not cerrado:
            for f in ls(ed):
                if not f.endswith(".md"):
                    continue
                efm, _ = cabecera(os.path.join(ed, f))
                if efm and re.search(r"^estado: *vigente", efm, re.M) and not re.search(r"(?<![\w-])" + re.escape(f[:-3]) + r"(?![\w-])", bloque):
                    h("entregable vigente que no está en el bloque Proyectos", rel(os.path.join(ed, f)))
        if not re.search(r"`" + re.escape(proj) + r"/?`", bloque):
            h("proyecto que no está en el bloque Proyectos de su área", rel(pruta))

# --- todos los .md ---
for dp, dn, fn in os.walk(raiz):
    dn[:] = [d for d in dn if not d.startswith(".") and not (dp == raiz and d.lower() == "claude outputs")]
    for f in fn:
        if not f.endswith(".md"):
            continue
        p = os.path.join(dp, f)
        r = rel(p)
        if r in ("guia.md", "metodo.md"):
            continue
        # fuentes/ y restringido/ son material, no documentos del método: no se editan,
        # así que no se les pide cabecera ni nombre. Sus enlaces.md sí son nuestros.
        if ("/fuentes/" in "/" + r or "/restringido/" in "/" + r) and f != "enlaces.md":
            continue
        if not nombre_ok(f) or (nombre_con_orden_version_o_fecha(f) and not ROTADO.match(f)):
            h("nombre de archivo", r)
        fm, txt = cabecera(p)
        if fm is None:
            h("sin cabecera", r); continue
        m = re.search(r"^estado: *(\S+)", fm, re.M)
        estado = m.group(1).strip("'\"") if m else None   # con o sin comillas, como abrir.py y el tablero
        if not m:
            h("cabecera sin estado", r)
        elif estado not in ESTADOS:
            h("estado que no existe", r, m.group(1))
        elif estado == "reemplazado" and "reemplazado_por" not in fm:
            h("reemplazado sin reemplazado_por", r)
        a = re.search(r"^actualizado: *(\S+)", fm, re.M)
        if not a:
            h("cabecera sin actualizado", r)
        elif not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.group(1)):
            h("fecha mal formada", r, a.group(1))
        if "/entregables/" in r and "basado_en" not in fm:
            h("entregable sin basado_en", r)
        # un [[ dentro de codigo, en linea o en bloque, no es un enlace: es hablar de ellos
        sin_codigo = re.sub(r"`[^`\n]*`", "", re.sub(r"```.*?```", "", txt, flags=re.S))
        if "[[" in sin_codigo:
            h("enlace wiki", r)
        # solo se marca una ruta absoluta que apunta a un archivo del método;
        # una ruta de máquina citada dentro de un runbook es contenido legítimo
        if re.search(r"/(Users|home|Volumes)/[^\s`)]*\.md\b", txt):
            h("ruta absoluta a un archivo del método", r)
        if f == "enlaces.md" and len([l for l in txt.splitlines() if l.startswith("|")]) <= 2:
            h("enlaces.md sin filas", r)

if not hallazgos:
    print("La raíz cumple el contrato.")
    sys.exit(0)
print("%d hallazgos:\n" % len(hallazgos))
ancho = max(len(c) for c, _, _ in hallazgos)
for clase, ruta, detalle in sorted(hallazgos):
    print("  %-*s  %s%s" % (ancho, clase, ruta, ("  (" + detalle + ")") if detalle else ""))
sys.exit(1)
PY
