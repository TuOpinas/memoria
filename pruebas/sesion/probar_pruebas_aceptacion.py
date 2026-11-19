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


def script(paso="Las pruebas de aceptación van en su propio pull request"):
    """El bloque «run: |» de un paso, sin su sangría, y los valores de env del workflow."""
    texto = YML.read_text(encoding="utf-8")
    i = texto.index("- name: " + paso)
    m = re.compile(r"^(\s*)run: \|\n((?:\1  .*\n|\s*\n)+)", re.M).search(texto, i)
    sangria = len(m.group(1)) + 2
    cuerpo = "".join(l[sangria:] + "\n" for l in m.group(2).rstrip("\n").split("\n"))
    env = {k: re.search(rf"^\s*{k}:\s*(\S.*?)\s*(?:#.*)?$", texto, re.M).group(1) for k in ("ACEPTACION", "ACTIVAS", "PRUEBA")}
    return cuerpo, env


def git(d, *a):
    return subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True, check=True).stdout.strip()


def repo(sin_carpeta=False):
    d = pathlib.Path(tempfile.mkdtemp())
    git(d, "init", "-q", "-b", "main")
    git(d, "config", "user.email", "p@e.test")
    git(d, "config", "user.name", "Prueba")
    for f in ("app/main.py", "tests/aceptacion/test_p01.py", "tests/unit/test_x.py", "pruebas/aceptación/test_p01.py",
              ".github/workflows/pruebas-aceptacion.yml"):
        if sin_carpeta and f.startswith(("tests/aceptacion/", ".github/")):
            continue
        (d / f).parent.mkdir(parents=True, exist_ok=True)
        (d / f).write_text("x = 1\n", encoding="utf-8")
    git(d, "add", "-A")
    git(d, "commit", "-qm", "base")
    return d, git(d, "rev-parse", "HEAD")


def pr(cambios, acept=None, sin_carpeta=False):
    """Aplica los cambios en una rama y corre el paso; devuelve (código de salida, salida)."""
    d, base = repo(sin_carpeta)
    git(d, "checkout", "-qb", "pieza")
    for orden, ruta, destino in cambios:
        if orden == "escribir":
            (d / ruta).parent.mkdir(parents=True, exist_ok=True)
            (d / ruta).write_text("y = 2\n", encoding="utf-8")
        elif orden == "borrar":
            git(d, "rm", "-rq", ruta)
        elif orden == "mover":
            (d / destino).parent.mkdir(parents=True, exist_ok=True)
            git(d, "mv", ruta, destino)
    git(d, "add", "-A")
    git(d, "commit", "-qm", "cambio")
    cuerpo, envw = script()
    env = dict(os.environ, BASE=base, HEAD=git(d, "rev-parse", "HEAD"), ACEPTACION=acept if acept is not None else envw["ACEPTACION"],
               RUNNER_TEMP=tempfile.mkdtemp())
    env.pop("GITHUB_WORKFLOW_REF", None)   # en el CI de este repositorio apunta a pruebas.yml, no al workflow que se prueba
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

c, o = pr([("escribir", "app/main.py", None), ("escribir", "tests/aceptacion/test_año.py", None)])
ok(c == 1, "una prueba con acento en el nombre cuenta como dentro: con código, falla")
c, o = pr([("escribir", "tests/aceptacion/test_sesión.py", None), ("escribir", "tests/aceptacion/test_p01.py", None)])
ok(c == 0, "y un pull request de escenarios con acentos pasa")
c, o = pr([("escribir", "app/main.py", None), ("escribir", "pruebas/aceptación/test_p01.py", None)], acept="pruebas/aceptación")
ok(c == 1, "una carpeta con acento, también")
for buena in ("./tests/aceptacion", "././tests/aceptacion", "tests/aceptacion//"):
    c, o = pr([("escribir", "app/main.py", None), ("escribir", "tests/aceptacion/test_p01.py", None)], acept=buena)
    ok(c == 1, f"con ACEPTACION «{buena}», la carpeta se reconoce")
for mala in ("app/main.py", ""):
    c, o = pr([("escribir", "app/main.py", None)], acept=mala)
    ok(c == 1 and "no es una carpeta" in o, f"con ACEPTACION «{mala}», que no es una carpeta, falla y lo dice")
c, o = pr([("borrar", "tests/aceptacion", None), ("escribir", "app/main.py", None)])
ok(c == 1 and "quita o mueve" in o, "quitar la carpeta de las pruebas falla")
c, o = pr([("escribir", ".github/workflows/pruebas-aceptacion.yml", None), ("escribir", "app/main.py", None)])
ok(c == 1 and "va en su propio pull request" in o, "cambiar el workflow junto con código falla")
c, o = pr([("escribir", ".github/workflows/pruebas-aceptacion.yml", None), ("escribir", "CLAUDE.md", None)])
ok(c == 0, "cambiarlo con el CLAUDE.md pasa: es el kit")

print("Montar el kit en un repositorio que aún no tiene pruebas de aceptación")
c, o = pr([("escribir", ".github/workflows/pruebas-aceptacion.yml", None), ("escribir", "CLAUDE.md", None)], sin_carpeta=True)
ok(c == 0, "el pull request que trae el workflow y el CLAUDE.md pasa")
c, o = pr([("escribir", ".github/workflows/pruebas-aceptacion.yml", None), ("escribir", "tests/aceptacion/.gitkeep", None)], sin_carpeta=True)
ok(c == 0, "con la carpeta vacía, también")
c, o = pr([("escribir", "app/main.py", None)], sin_carpeta=True)
ok(c == 0 and "no hay nada que proteger" in o, "una pieza antes de que haya escenarios pasa, y lo dice")

print("Las piezas activas y los pull requests de escenarios")
CUERPO2, ENVW = script("Pasan las pruebas de las piezas activas, y fallan las de un pull request de escenarios")


def activas(pruebas, lista, titulo):
    """pruebas: {pieza: sale con 0 o 1}; lista: el texto de ACTIVAS o None; corre el segundo paso con el título."""
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "tests/aceptacion").mkdir(parents=True)
    for p, rc in pruebas.items():
        (d / f"tests/aceptacion/{p}.sh").write_text(f"exit {rc}\n", encoding="utf-8")
    if lista is not None:
        (d / ".github").mkdir()
        (d / ".github/piezas-activas.txt").write_text(lista, encoding="utf-8")
    env = dict(os.environ, ACEPTACION="tests/aceptacion", ACTIVAS=ENVW["ACTIVAS"], PRUEBA="sh tests/aceptacion/{pieza}.sh",
               TITULO=titulo)
    r = subprocess.run(["bash", "-c", CUERPO2], cwd=d, env=env, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


ok("{pieza}" in ENVW["PRUEBA"] and ENVW["ACTIVAS"].endswith(".txt"), "la plantilla trae ACTIVAS y PRUEBA con {pieza}")
c, o = activas({"P01": 1}, None, "Escenarios · P01")
ok(c == 0, "un pull request de escenarios se une en verde si sus pruebas fallan")
c, o = activas({"P01": 0}, None, "Escenarios · P01")
ok(c == 1 and "ya pasan" in o, "si sus pruebas ya pasan antes de construir la pieza, falla")
c, o = activas({"P01": 1, "P02": 1}, None, "Escenarios · P01 + P02 · alta y lista")
ok(c == 0, "uno de varias piezas, también")
c, o = activas({"P01": 1}, None, "P01 · alta de clientes")
ok(c == 0, "una pieza que aún no está en la lista no corre sus pruebas")
c, o = activas({"P01": 0}, "P01\n", "P01 · alta de clientes")
ok(c == 0, "la pieza que se añade a la lista pasa si sus pruebas pasan")
c, o = activas({"P01": 1}, "# piezas activas\nP01\n", "P01 · alta de clientes")
ok(c == 1 and "no pasan" in o, "y falla si no pasan")
c, o = activas({"P01": 0, "P02": 1}, "P01", "P02 · lista")
ok(c == 0, "las de otra pieza aún no activa no cuentan")
c, o = activas({"P01": 0, "P02": 1}, "P01", "Escenarios · P02")
ok(c == 0, "un pull request de escenarios corre también las activas, y pasa si pasan")
c, o = activas({"P01": 1}, "P01", "Escenarios · P01")
ok(c == 1, "cambiar los escenarios de una pieza activa sigue exigiendo que pasen")
c, o = activas({"P01": 0}, "P01; rm -rf /\n", "P01 · x")
ok(c == 1 and "no es un identificador" in o, "una línea de la lista que no es un identificador falla, sin correr nada")
c, o = activas({"P01": 1}, None, "Escenarios · $(touch pwned)")
ok(c == 1 and "no dice qué pieza" in o, "un título que no es una pieza falla, sin correr nada")

print()
print("Todo bien." if not fallos else f"{fallos} fallo(s).")
sys.exit(1 if fallos else 0)
