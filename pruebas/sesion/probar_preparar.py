#!/usr/bin/env python3
"""Prueba preparar.py, que arma la llamada que trae scripts del plugin a la computadora, sin red.

Uso: python3 pruebas/sesion/probar_preparar.py
"""
import os, pathlib, shutil, subprocess, sys, tempfile

AQUI = pathlib.Path(__file__).resolve().parent
PLUGIN = AQUI.parent.parent / "plugins" / "memoria"
PREP = PLUGIN / "preparar.py"
fallos = 0


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t)
    fallos += 0 if c else 1


def prep(*a):
    r = subprocess.run([sys.executable, str(PREP), *a], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


print("preparar.py")
c, o, _ = prep("$HOME/memoria", "skills/sesion/abrir.py")
lineas = dict(l.split(" ", 1) for l in o.strip().split("\n"))
ok(c == 0 and set(lineas) == {"VERSION", "METODO", "DESCARGA", "REINTENTO"}, "imprime VERSION, METODO, DESCARGA y REINTENTO")
ok('mkdir -p "$HOME/memoria"' in lineas["DESCARGA"], "deja $HOME sin expandir, entre comillas dobles, para que se expanda en la computadora")
ok("/v" + lineas["VERSION"] + "/plugins/memoria/skills/sesion/abrir.py" in lineas["DESCARGA"] and "/main/plugins/memoria/" in lineas["REINTENTO"], "DESCARGA va a la etiqueta de la versión y REINTENTO a main")
ok(lineas["METODO"] == (PLUGIN / "metodo.md").read_text(encoding="utf-8").split("\n")[0], "METODO es la primera línea del metodo.md del plugin")

tmp = pathlib.Path(tempfile.mkdtemp())
d = tmp / "destino"
c, o, _ = prep(str(d), "skills/sesion/abrir.py")
cmd = o.split("DESCARGA ", 1)[1].split("\n")[0]
d.mkdir()
shutil.copy(PLUGIN / "skills/sesion/abrir.py", d / "abrir.py")
# sin red: curl apunta a un sitio que no responde; si el archivo ya cuadra, no se llama
env = dict(os.environ, PATH=str(tmp / "bin") + os.pathsep + os.environ["PATH"])
(tmp / "bin").mkdir()
(tmp / "bin" / "curl").write_text("#!/bin/sh\necho llamado >> \"%s\"\nexit 22\n" % (tmp / "curl.log"))
(tmp / "bin" / "curl").chmod(0o755)
r = subprocess.run(["bash", "-c", cmd + " && echo CORRE"], capture_output=True, text=True, env=env)
ok(r.returncode == 0 and "CORRE" in r.stdout and not (tmp / "curl.log").exists(), "un archivo que ya está con su huella no se vuelve a traer y lo de detrás corre")
(d / "abrir.py").write_text("otro contenido\n")
r = subprocess.run(["bash", "-c", cmd + " && echo CORRE"], capture_output=True, text=True, env=env)
ok(r.returncode != 0 and "CORRE" not in r.stdout and (tmp / "curl.log").exists(), "un archivo que no cuadra se intenta traer y, si falla, lo de detrás no corre")
c, _, e = prep(str(d), "../memoria/preparar.py")
ok(c != 0, "rechaza una ruta con ..")
c, _, e = prep(str(d), "skills/tablero/vista.html", "skills/no-existe.py")
ok(c != 0, "rechaza una ruta que no está en el plugin")
shutil.rmtree(tmp, ignore_errors=True)
print("\nTodo bien." if not fallos else f"\n{fallos} fallos.")
sys.exit(1 if fallos else 0)
