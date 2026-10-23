#!/usr/bin/env python3
"""Escribe lo que deja un cierre de sesión (skill sesion, anexo cerrar.md), archivo por archivo y sin pisar a nadie.

La skill prepara los textos; este script los escribe. De cada archivo hace leer → cambiar → escribir, y comprueba
justo antes de escribir que el archivo sigue como lo leyó (misma fecha, tamaño y contenido); si cambió entre medias,
vuelve a leerlo y aplica el cambio sobre lo nuevo (compare-and-swap). Así, dos cierres sobre el mismo proyecto a la vez
no se pierden una entrada ni un paso: cada entrada va encima de lo que haya, y cada reemplazo se aplica sobre la
versión que está en el disco. Lo que otra persona escribió desde que se abrió la sesión se dice (--abierto).

Uso:
  cerrar.py <raiz> <area>/<proyecto> <cambios.json> [--abierto <hora ISO de la apertura>] [--version <versión del plugin>]

cambios.json, todo opcional salvo «sesion»:
  {"sesion": "## AAAA-MM-DD (título)\\nSesión de: …\\nTrabajamos en: …\\nAvances: …\\nPendiente: …",
   "decisiones": ["## AAAA-MM-DD · Título\\nDecidió: …\\nPor qué: …", …],
   "proyecto": {"en_corto": "texto entero del bloque En corto, sin el encabezado",
                "reemplazos": [{"de": "texto exacto viejo", "a": "texto nuevo"}, …]},
   "area": {"linea": "- `slug/` — descripción", "entregables": ["  - nombre — descripción · actualizado AAAA-MM-DD", …]},
   "panorama": "texto entero del bloque Panorama de area.md, sin el encabezado",
   "otros": [{"ruta": "<relativa a la raíz>", "reemplazos": [{"de": "…", "a": "…"}]}, …]}

Cada entrada de registro va arriba del todo, debajo del título; una entrada igual que ya esté no se repite. Un
reemplazo cuyo texto viejo no aparece exactamente una vez no se aplica y se devuelve en «sin_match», para que la
sesión lo ajuste (la tarea del tablero pudo poner una fecha en esa línea). `actualizado` de la cabecera se pone a hoy
en cada archivo escrito. Imprime un JSON: «escritos», «sin_match», «ajenos» (archivos que alguien cambió desde la
apertura, con la hora), «reintentos», «hora» (ahora, ISO 8601 en minutos UTC, para la marca del tablero) y
«documento» (el id de esa marca). No toca nada fuera del proyecto salvo area.md (paso 5 y Panorama) y «otros».
"""
import datetime
import hashlib
import json
import os
import pathlib
import re
import sys
import time

HOY = datetime.date.today().isoformat()
INTENTOS = 5


def leer(p):
    with open(p, "rb") as f:
        b = f.read()
    st = os.stat(p)
    return b.decode("utf-8-sig"), (st.st_mtime_ns, st.st_size, hashlib.sha1(b).hexdigest())


def igual(p, firma):
    try:
        st = os.stat(p)
    except OSError:
        return firma is None
    if (st.st_mtime_ns, st.st_size) != firma[:2]:
        return False
    with open(p, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest() == firma[2]


def escribir(p, texto):
    """Escribe en un archivo temporal al lado y lo pone en su sitio: nadie lee un archivo a medias."""
    tmp = p.with_name(p.name + ".cerrar-tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(texto)
    os.replace(tmp, p)


def cabecera_hoy(t):
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m:
        return t
    cab = re.sub(r"^actualizado:.*$", f"actualizado: {HOY}", m.group(1), count=1, flags=re.M)
    if "actualizado:" not in cab:
        cab += f"\nactualizado: {HOY}"
    return f"---\n{cab}\n---\n" + t[m.end():]


def con_entrada_arriba(t, entrada):
    """Una entrada nueva de registro, debajo del título y encima de las demás; si ya está, nada."""
    entrada = entrada.strip() + "\n"
    if entrada.strip() in t:
        return t, False
    m = re.search(r"^# .*\n", t, re.M)
    if m:
        i = m.end()
        resto = t[i:]
        # el texto que va entre el título y la primera entrada (una nota, una línea en blanco) se conserva arriba
        j = re.search(r"^## ", resto, re.M)
        if j:
            prefacio, cuerpo = resto[:j.start()], resto[j.start():]
            if not prefacio.strip():
                prefacio = "\n"
            elif not prefacio.endswith("\n\n"):
                prefacio = prefacio.rstrip("\n") + "\n\n"
            return t[:i] + prefacio + entrada + "\n" + cuerpo, True
        return t[:i] + "\n" + entrada + ("\n" + resto.lstrip("\n") if resto.strip() else ""), True
    return t.rstrip("\n") + "\n\n" + entrada, True


def con_bloque(t, nombre, cuerpo):
    """Reescribe entero el bloque «## nombre» (lo crea debajo del título si no existe)."""
    cuerpo = cuerpo.strip() + "\n"
    m = re.search(r"^## " + re.escape(nombre) + r"\s*\n(.*?)(?=^## |\Z)", t, re.M | re.S)
    if m:
        return t[:m.start(1)] + cuerpo + ("\n" if not cuerpo.endswith("\n\n") else "") + t[m.end(1):]
    mt = re.search(r"^# .*\n", t, re.M)
    i = mt.end() if mt else 0
    return t[:i] + f"\n## {nombre}\n{cuerpo}\n" + t[i:].lstrip("\n")


def con_reemplazos(t, reemplazos, sin_match, ruta):
    for r in reemplazos or []:
        de, a = r.get("de", ""), r.get("a", "")
        n = t.count(de) if de else 0
        if n != 1:
            sin_match.append({"ruta": ruta, "de": de[:120], "veces": n})
            continue
        t = t.replace(de, a)
    return t


def con_linea_proyecto(t, slug, linea, entregables):
    """En el bloque Proyectos de area.md: la línea del proyecto y las de sus entregables, sin tocar las demás."""
    m = re.search(r"^## Proyectos\s*\n(.*?)(?=^## |\Z)", t, re.M | re.S)
    if not m:
        return t, False
    bloque = m.group(1).split("\n")
    nuevo = [linea.rstrip()] + [e.rstrip() for e in entregables or []]
    i = next((k for k, l in enumerate(bloque) if re.match(r"^- `" + re.escape(slug) + r"/?`", l)), None)
    if i is None:
        # proyecto nuevo en el índice: al final de las líneas de proyectos
        ultimo = max((k for k, l in enumerate(bloque) if l.startswith("- `") or l.startswith("  - ")), default=-1)
        bloque[ultimo + 1:ultimo + 1] = nuevo
    else:
        j = i + 1
        while j < len(bloque) and bloque[j].startswith("  "):
            j += 1
        bloque[i:j] = nuevo
    return t[:m.start(1)] + "\n".join(bloque) + t[m.end(1):], True


def cambiar(p, f, abierto, salida, rel=None):
    """Lee, cambia con f y escribe solo si el archivo sigue igual que al leerlo; si no, repite sobre lo nuevo."""
    rel = rel or str(p)
    for intento in range(INTENTOS):
        t, firma = leer(p)
        if abierto and firma[0] / 1e9 > abierto and rel not in salida["_vistos"]:
            salida["ajenos"].append({"ruta": rel, "hora": datetime.datetime.fromtimestamp(firma[0] / 1e9).astimezone().isoformat(timespec="minutes")})
        salida["_vistos"].add(rel)
        nuevo, hubo = f(t)
        if not hubo or nuevo == t:
            return False
        nuevo = cabecera_hoy(nuevo)
        if igual(p, firma):
            escribir(p, nuevo)
            if intento:
                salida["reintentos"] += intento
            return True
        time.sleep(0.05 * (intento + 1))
    salida["sin_match"].append({"ruta": rel, "de": "(el archivo cambió cinco veces seguidas mientras se escribía)", "veces": -1})
    return False


def main(argv):
    if len(argv) < 4:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    raiz, activo, cambios = pathlib.Path(argv[1]), argv[2].strip("/"), json.loads(pathlib.Path(argv[3]).read_text(encoding="utf-8"))
    abierto = None
    if "--abierto" in argv:
        try:
            abierto = datetime.datetime.fromisoformat(argv[argv.index("--abierto") + 1]).timestamp()
        except (ValueError, IndexError):
            print("--abierto va con una hora ISO 8601 (la de REGISTROS de abrir.py)", file=sys.stderr)
            return 2
    if "/" not in activo or not (raiz / "guia.md").is_file() or not (raiz / activo).is_dir():
        print("Uso: cerrar.py <raiz> <area>/<proyecto> <cambios.json>", file=sys.stderr)
        return 2
    area, slug = activo.split("/", 1)
    pd = raiz / activo
    salida = {"escritos": [], "sin_match": [], "ajenos": [], "reintentos": 0, "_vistos": set()}

    def rel(p):
        return p.relative_to(raiz).as_posix()

    # 2. sesiones.md
    if cambios.get("sesion"):
        p = pd / "sesiones.md"
        if cambiar(p, lambda t: con_entrada_arriba(t, cambios["sesion"]), abierto, salida, rel(p)):
            salida["escritos"].append(rel(p))
    # 3. decisiones.md: de la más antigua a la más nueva, para que la última quede arriba
    if cambios.get("decisiones"):
        p = pd / "decisiones.md"
        def f(t):
            hubo = False
            for d in cambios["decisiones"]:
                t, h = con_entrada_arriba(t, d)
                hubo = hubo or h
            return t, hubo
        if cambiar(p, f, abierto, salida, rel(p)):
            salida["escritos"].append(rel(p))
    # 4. proyecto.md: En corto entero y reemplazos exactos en lo demás
    pr = cambios.get("proyecto") or {}
    if pr.get("en_corto") or pr.get("reemplazos"):
        p = pd / "proyecto.md"
        def f(t):
            t0 = t
            t = con_reemplazos(t, pr.get("reemplazos"), salida["sin_match"], rel(p))
            if pr.get("en_corto"):
                t = con_bloque(t, "En corto", pr["en_corto"])
            return t, t != t0
        if cambiar(p, f, abierto, salida, rel(p)):
            salida["escritos"].append(rel(p))
    # 5 y 10. area.md: la línea del proyecto y el Panorama
    ar = cambios.get("area") or {}
    if ar.get("linea") or cambios.get("panorama"):
        p = raiz / area / "area.md"
        def f(t):
            t0 = t
            if ar.get("linea"):
                t, _ = con_linea_proyecto(t, slug, ar["linea"], ar.get("entregables"))
            if cambios.get("panorama"):
                t = con_bloque(t, "Panorama", cambios["panorama"])
            return t, t != t0
        if cambiar(p, f, abierto, salida, rel(p)):
            salida["escritos"].append(rel(p))
    # otros archivos, por reemplazos exactos
    for o in cambios.get("otros") or []:
        p = raiz / o["ruta"]
        if not p.is_file() or ".." in o["ruta"].split("/"):
            salida["sin_match"].append({"ruta": o["ruta"], "de": "(no existe)", "veces": 0}); continue
        def f(t, o=o, p=p):
            n = con_reemplazos(t, o.get("reemplazos"), salida["sin_match"], rel(p))
            return n, n != t
        if cambiar(p, f, abierto, salida, rel(p)):
            salida["escritos"].append(rel(p))
    ahora = datetime.datetime.now(datetime.timezone.utc)
    salida["hora"] = ahora.strftime("%Y-%m-%dT%H:%MZ")
    salida["documento"] = f"{area}--{slug}--{ahora.strftime('%Y%m%d%H%M')}"
    salida.pop("_vistos")
    print(json.dumps(salida, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
