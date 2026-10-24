#!/usr/bin/env python3
"""Prepara, en el contenedor, la llamada que trae scripts del plugin a la computadora.

La computadora no ve el plugin y su $HOME empieza vacío en cada sesión. Este script
corre donde sí está el plugin y imprime cuatro líneas:

  VERSION <versión del plugin>
  METODO <primera línea del metodo.md del plugin>
  DESCARGA <comando para device_bash: trae cada archivo del repositorio en esa versión y lo comprueba>
  REINTENTO <el mismo comando con main en lugar de v<versión>>

De DESCARGA y REINTENTO se usa lo que va detrás de la etiqueta y su espacio.

Un archivo que ya está en el destino con la huella del plugin no se vuelve a traer. El comando
termina en `sha256sum -c`, así que detrás se le añade ` && <lo que se corre>` y eso solo corre
si todos los archivos cuadran.

Uso: python3 preparar.py <destino en la computadora> <ruta dentro del plugin>... [--trabajo <carpeta de trabajo>]
     python3 preparar.py '$HOME/tablero' skills/tablero/generar_vista.py skills/tablero/aplicar_cambios.py --trabajo <trabajo>

Con --trabajo deja la carpeta de trabajo lista para la puesta al día del tablero: la crea, vacía lo que haya de otra
corrida o de otro tablero (`base`, `salida`, `cola`, `cierres`, `copia-tablero` y, con --copia, la copia de los archivos de
la raíz), deja `retenidos.json` y `ajenos.json` vacíos y escribe `inicio.json` con el instante en que empieza, del que
plan_subida.py saca la duración. Corre antes que nada, también sin consola.
"""
import hashlib
import json
import os
import shlex
import sys

REPO = "https://raw.githubusercontent.com/TuOpinas/memoria"


def main(argv):
    if len(argv) < 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    trabajo = copia = None
    for nombre in ("--trabajo", "--copia"):
        if nombre in argv:
            i = argv.index(nombre)
            valor = argv[i + 1] if len(argv) > i + 1 else None
            argv = argv[:i] + argv[i + 2:]
            if nombre == "--trabajo":
                trabajo = valor
            else:
                copia = valor
    destino, rutas = argv[1], argv[2:]
    if trabajo:
        import shutil, datetime
        os.makedirs(trabajo, exist_ok=True)
        # lo de otra corrida o de otro tablero se va: la base entera (meta/estado se vuelve a bajar en 1a), la salida,
        # la cola, los cierres y la copia de los archivos de la raíz (si se dio con --copia)
        for sub in ("base", "salida", "cola", "cierres", "copia-tablero"):
            shutil.rmtree(os.path.join(trabajo, sub), ignore_errors=True)
        if copia:
            shutil.rmtree(copia, ignore_errors=True)
        for nombre in ("retenidos.json", "ajenos.json"):
            with open(os.path.join(trabajo, nombre), "w", encoding="utf-8") as f:
                f.write("[]")         # la cola los rellena si hay algo que retener; si no, ya están
        with open(os.path.join(trabajo, "inicio.json"), "w", encoding="utf-8") as f:
            json.dump({"inicio": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}, f)
    plugin = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(plugin, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        version = json.load(f)["version"]
    with open(os.path.join(plugin, "metodo.md"), encoding="utf-8") as f:
        metodo = f.readline().rstrip("\n")
    huellas = []
    for r in rutas:
        p = os.path.join(plugin, r)
        if os.path.isabs(r) or ".." in r.split("/") or not os.path.isfile(p):
            print(f"No está en el plugin: {r}", file=sys.stderr)
            return 1
        with open(p, "rb") as f:
            huellas.append((os.path.basename(r), r, hashlib.sha256(f.read()).hexdigest()))
    nombres = [n for n, _, _ in huellas]
    if len(set(nombres)) != len(nombres):
        print("Dos rutas con el mismo nombre de archivo se pisarían en el destino", file=sys.stderr)
        return 1
    # el destino va entre comillas dobles para que $HOME se expanda en la computadora
    if '"' in destino or "`" in destino:
        print("El destino no puede llevar comillas ni acentos graves", file=sys.stderr)
        return 1

    def comando(ref):
        partes = [f'mkdir -p "{destino}"', f'cd "{destino}"']
        for nombre, ruta, h in huellas:
            n = shlex.quote(nombre)
            url = shlex.quote(f"{REPO}/{ref}/plugins/memoria/{ruta}")
            partes.append(f"{{ echo '{h}  {nombre}' | sha256sum -c --status 2>/dev/null || curl -sfL -o {n} {url}; }}")
        lista = " ".join(f"{h} {shlex.quote(n)}" for n, _, h in huellas)
        partes.append(f"printf '%s  %s\\n' {lista} | sha256sum -c --quiet")
        return " && ".join(partes)

    print(f"VERSION {version}")
    print(f"METODO {metodo}")
    print(f"DESCARGA {comando('v' + version)}")
    print(f"REINTENTO {comando('main')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
