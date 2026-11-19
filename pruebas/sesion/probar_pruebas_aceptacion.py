#!/usr/bin/env python3
"""Prueba el workflow de la plantilla del kit de desarrollo (1.27), skills/desarrollo/plantillas/pruebas-aceptacion.yml:
falla si un mismo pull request cambia las pruebas de aceptación y algo fuera de ellas, y pasa si cambia solo una de las
dos cosas (tecnologia/metodologia-desarrollo#2026-11-19-2).

Uso: python3 pruebas/sesion/probar_pruebas_aceptacion.py
Saca el script del paso del workflow y lo corre con bash en un repositorio de git temporal, como lo correría GitHub con
la base y la cabeza del pull request.
"""
import os, pathlib, re, subprocess, sys, tempfile

AQUI = pathlib.Path(__file__).resolve().parent
YML = AQUI.parent.parent / "plugins" / "memoria" / "skills" / "desarrollo" / "plantillas" / "pruebas-aceptacion.yml"
fallos = 0


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t)
    fallos += 0 if c else 1


def script():
    """El bloque «run: |» del paso, sin su sangría, y el valor de ACEPTACION de env."""
    texto = YML.read_text(encoding="utf-8")
    m = re.search(r"^(\s*)run: \|\n((?:\1  .*\n|\s*\n)+)", texto, re.M)
    sangria = len(m.group(1)) + 2
    cuerpo = "".join(l[sangria:] + "\n" for l in m.group(2).rstrip("\n").split("\n"))
    acept = re.search(r"^\s*ACEPTACION:\s*(\S+)", texto, re.M).group(1)
    return cuerpo, acept


def git(d, *a):
    return subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True, check=True).stdout.strip()


def repo():
    d = pathlib.Path(tempfile.mkdtemp())
    git(d, "init", "-q", "-b", "main")
    git(d, "config", "user.email", "p@e.test")
    git(d, "config", "user.name", "Prueba")
    for f in ("app/main.py", "tests/aceptacion/test_p01.py", "tests/unit/test_x.py"):
        (d / f).parent.mkdir(parents=True, exist_ok=True)
        (d / f).write_text("x = 1\n", encoding="utf-8")
    git(d, "add", "-A")
    git(d, "commit", "-qm", "base")
    return d, git(d, "rev-parse", "HEAD")


def pr(cambios, acept=None):
    """Aplica los cambios en una rama y corre el paso; devuelve (código de salida, salida)."""
    d, base = repo()
    git(d, "checkout", "-qb", "pieza")
    for orden, ruta, destino in cambios:
        if orden == "escribir":
            (d / ruta).parent.mkdir(parents=True, exist_ok=True)
            (d / ruta).write_text("y = 2\n", encoding="utf-8")
        elif orden == "mover":
            (d / destino).parent.mkdir(parents=True, exist_ok=True)
            git(d, "mv", ruta, destino)
    git(d, "add", "-A")
    git(d, "commit", "-qm", "cambio")
    cuerpo, acept_yml = script()
    env = dict(os.environ, BASE=base, HEAD=git(d, "rev-parse", "HEAD"), ACEPTACION=acept or acept_yml)
    p = subprocess.run(["bash", "-c", cuerpo], cwd=d, env=env, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


print("El workflow de las pruebas de aceptación")
c, o = pr([("escribir", "tests/aceptacion/test_p01.py", None), ("escribir", "tests/aceptacion/test_p02.py", None)])
ok(c == 0, "un pull request que solo toca las pruebas de aceptación pasa")
c, o = pr([("escribir", "app/main.py", None), ("escribir", "tests/unit/test_x.py", None)])
ok(c == 0, "el de una pieza que no las toca pasa")
c, o = pr([("escribir", "app/main.py", None), ("escribir", "tests/aceptacion/test_p01.py", None)])
ok(c == 1 and "::error::" in o, "uno que cambia las dos cosas falla, con el error en claro")
c, o = pr([("mover", "tests/aceptacion/test_p01.py", "tests/unit/test_p01.py")])
ok(c == 1, "mover una prueba de aceptación fuera de su carpeta cuenta en los dos sitios y falla")
c, o = pr([("escribir", "tests/aceptacion-viejas/test_z.py", None), ("escribir", "tests/aceptacion/test_p01.py", None)])
ok(c == 1, "una carpeta que solo empieza igual cuenta como fuera")
c, o = pr([("escribir", "app/main.py", None), ("escribir", "tests/aceptacion/test_p01.py", None)], acept="tests/aceptacion/")
ok(c == 1, "con la barra final en ACEPTACION, igual")

print()
print("Todo bien." if not fallos else f"{fallos} fallo(s).")
sys.exit(1 if fallos else 0)
