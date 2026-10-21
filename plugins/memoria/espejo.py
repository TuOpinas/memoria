#!/usr/bin/env python3
"""La copia de la raíz en el contenedor, para trabajar sin consola en la computadora.

Sin consola quiere decir que la raíz está conectada pero el shell de la computadora no la monta (le pasa a una unidad de
Google Drive para escritorio en Windows, con letra o colgada de una carpeta). Las herramientas que traen y escriben archivos
(device_stage_files, device_commit_files) sí llegan a ella, así que se trabaja sobre una copia en el contenedor: los scripts
del plugin corren sobre la copia y lo que cambia se devuelve a la computadora. Este script no toca la computadora: dice qué
traer, guarda cómo estaba la copia y prepara lo que hay que devolver.

  espejo.py rutas <copia> [<area>/<proyecto>]
      Qué traer para abrir sesión, por rondas: imprime una ruta por línea (relativa a la raíz) de lo que falta en la copia, o
      COMPLETA. Primera ronda: guia.md, metodo.md y base/premisas.md y base/contexto.md; segunda: el area.md de cada área de
      la tabla de guia.md; tercera: proyecto.md, decisiones.md y sesiones.md de cada proyecto del índice de su área, y del
      proyecto activo aunque no esté en el índice. Lo que se pidió y no llegó (no existe, o la cuenta no lo lee) no se vuelve
      a pedir. Las cabeceras de entregables/ del proyecto activo no salen de aquí: se traen desde su listado.

  espejo.py instantanea <copia>
      Guarda la huella de cada archivo de la copia, para saber después qué cambió en ella. Se corre en cuanto la copia está
      completa, y otra vez después de cada devolución.

  espejo.py devolver <copia> <ruta de la raíz en la computadora> [<carpeta de salidas>]
      Lo que cambió o se creó en la copia desde la última instantánea, listo para device_commit_files: copia cada archivo a una
      carpeta nueva de salidas (nunca una ruta ya usada: la herramienta puede mandar la copia anterior sin avisar) e imprime un
      JSON con stagedPath, devicePath y rel de cada uno. Las salidas son /mnt/project-files/ si existe y si no
      /mnt/user-data/outputs/. No devuelve nada que se haya borrado de la copia: borrar o mover no se hace por aquí.

Nunca escribe dentro de la raíz de la computadora ni pide nada de fuentes/, taller/ ni restringido/.
"""
import hashlib
import json
import os
import pathlib
import re
import shutil
import sys
import time

FUERA = ("fuentes", "taller", "restringido")


def leer(p):
    try:
        return pathlib.Path(p).read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return None


def seccion(texto, nombre):
    m = re.search(r"^##\s+" + re.escape(nombre) + r"\s*$(.*?)(?=^##\s|\Z)", texto or "", re.M | re.S)
    return m.group(1) if m else ""


def sin_cabecera(texto):
    if texto and texto.startswith("---"):
        partes = texto.split("\n---", 1)
        if len(partes) == 2:
            return partes[1]
    return texto or ""


def areas_de(guia):
    """Los slugs de la tabla de áreas de guia.md, como la leen abrir.py y el tablero: la primera columna, sin comillas ni barra."""
    slugs, cab = [], False
    for l in seccion(guia, "Áreas").split("\n"):
        if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
            continue
        if not cab:
            cab = True
            continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        s = c[0].strip("`").rstrip("/").strip() if c else ""
        if s and "/" not in s and s not in (".", ".."):
            slugs.append(s)
    return slugs


def proyectos_de(texto_area):
    return [m.group(1) for m in re.finditer(r"^- `([^`/]+)/?`", seccion(sin_cabecera(texto_area), "Proyectos"), re.M)]


def ruta_pedidos(copia):
    return pathlib.Path(str(copia).rstrip("/") + ".pedidos")


def rutas(copia, activo):
    copia = pathlib.Path(copia)
    pedidos_f = ruta_pedidos(copia)
    pedidos = set(pedidos_f.read_text(encoding="utf-8").split("\n")) if pedidos_f.exists() else set()
    falta = lambda r: not (copia / r).is_file() and r not in pedidos
    ronda = [r for r in ("guia.md", "metodo.md", "base/premisas.md", "base/contexto.md") if falta(r)]
    if not ronda:
        guia = leer(copia / "guia.md")
        if guia is None:
            print("Sin guia.md en la copia: no es la raíz, o la cuenta no la lee.", file=sys.stderr)
            return 1
        areas = areas_de(guia)
        ronda = [f"{a}/area.md" for a in areas if falta(f"{a}/area.md")]
        if not ronda:
            for a in areas:
                for p in proyectos_de(leer(copia / a / "area.md")):
                    ronda += [f"{a}/{p}/{n}" for n in ("proyecto.md", "decisiones.md", "sesiones.md")]
            if activo:
                ronda += [f"{activo}/{n}" for n in ("proyecto.md", "decisiones.md", "sesiones.md")]
            ronda = [r for r in dict.fromkeys(ronda) if falta(r) and not set(r.split("/")[:-1]) & set(FUERA)]
    if not ronda:
        print("COMPLETA")
        return 0
    pedidos_f.parent.mkdir(parents=True, exist_ok=True)
    pedidos_f.write_text("\n".join(sorted(pedidos | set(ronda))), encoding="utf-8")
    print("\n".join(ronda))
    return 0


def huellas(copia):
    copia = pathlib.Path(copia)
    h = {}
    for d, ds, fs in os.walk(copia):
        for f in fs:
            p = pathlib.Path(d) / f
            h[p.relative_to(copia).as_posix()] = hashlib.sha1(p.read_bytes()).hexdigest()
    return h


def ruta_manifiesto(copia):
    return pathlib.Path(str(copia).rstrip("/") + ".manifiesto.json")


def instantanea(copia):
    h = huellas(copia)
    ruta_manifiesto(copia).write_text(json.dumps(h, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    print(f"{len(h)} archivos")
    return 0


def devolver(copia, raiz_dispositivo, salidas=None):
    copia = pathlib.Path(copia)
    m = ruta_manifiesto(copia)
    if not m.exists():
        print("No hay instantánea de esta copia: corre «espejo.py instantanea» en cuanto la copia esté completa, antes de editar.", file=sys.stderr)
        return 2
    antes = json.loads(m.read_text(encoding="utf-8"))
    cambios = [r for r, h in sorted(huellas(copia).items()) if antes.get(r) != h]
    if not cambios:
        print("[]")
        return 0
    if salidas is None:
        salidas = "/mnt/project-files" if os.path.isdir("/mnt/project-files") else "/mnt/user-data/outputs"
    destino = pathlib.Path(salidas) / f"espejo-{time.strftime('%Y%m%d%H%M%S')}-{os.getpid()}"
    sep = "\\" if "\\" in raiz_dispositivo and "/" not in raiz_dispositivo else "/"
    base = raiz_dispositivo.rstrip("/\\")
    salida = []
    for r in cambios:
        partes = r.split("/")
        dst = destino / r
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(copia / r, dst)
        salida.append({"stagedPath": str(dst), "devicePath": base + sep + sep.join(partes), "rel": r, "nuevo": r not in antes})
    print(json.dumps(salida, ensure_ascii=False, indent=1))
    return 0


def main(argv):
    if len(argv) < 3 or argv[1] not in ("rutas", "instantanea", "devolver"):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    if argv[1] == "rutas":
        return rutas(argv[2], argv[3].strip("/") if len(argv) > 3 else None)
    if argv[1] == "instantanea":
        return instantanea(argv[2])
    if len(argv) < 4:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    return devolver(argv[2], argv[3], argv[4] if len(argv) > 4 else None)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
