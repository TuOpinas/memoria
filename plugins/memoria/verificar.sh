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
        txt = open(path, encoding="utf-8", errors="replace").read()
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
        h("nombre de carpeta", nombre)

# --- áreas y proyectos ---
for area, aruta in areas:
    amd = os.path.join(aruta, "area.md")
    if not os.path.exists(amd):
        h("área sin area.md", area); continue
    fm, txt = cabecera(amd)
    if not re.search(r"^Dueñ[oa]: *\S", txt, re.M):
        h("área sin dueño", rel(amd))
    if "## Proyectos" not in txt:
        h("area.md sin bloque Proyectos", rel(amd))
    bloque = seccion_proyectos(txt)

    for proj in ls(aruta):
        pruta = os.path.join(aruta, proj)
        if not os.path.isdir(pruta) or proj.startswith("."):
            continue
        if not nombre_ok(proj) or nombre_con_orden_version_o_fecha(proj):
            h("nombre de carpeta", rel(pruta))
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
        if not m:
            h("cabecera sin estado", r)
        elif m.group(1) not in ESTADOS:
            h("estado que no existe", r, m.group(1))
        elif m.group(1) == "reemplazado" and "reemplazado_por" not in fm:
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
