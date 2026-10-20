#!/usr/bin/env python3
"""Prepara, en el contenedor, la llamada que trae scripts del plugin a la computadora.

La computadora no ve el plugin y su $HOME empieza vacío en cada sesión. Este script
corre donde sí está el plugin y imprime cuatro líneas:

  VERSION <versión del plugin>
  METODO <primera línea del metodo.md del plugin>
  DESCARGA <comando para device_bash: trae cada archivo del repositorio en esa versión y lo comprueba>
  REINTENTO <el mismo comando con main en lugar de v<versión>>

Un archivo que ya está en el destino con la huella del plugin no se vuelve a traer. El comando
termina en `sha256sum -c`, así que detrás se le añade ` && <lo que se corre>` y eso solo corre
si todos los archivos cuadran.

Uso: python3 preparar.py <destino en la computadora> <ruta dentro del plugin>...
     python3 preparar.py '$HOME/tablero' skills/tablero/generar_vista.py skills/tablero/aplicar_cambios.py
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
    destino, rutas = argv[1], argv[2:]
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
