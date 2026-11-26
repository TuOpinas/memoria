#!/usr/bin/env python3
"""Prueba el workflow de la plantilla del kit de desarrollo (1.27), skills/desarrollo/plantillas/pruebas-aceptacion.yml:
falla si un mismo pull request cambia las pruebas de aceptación y algo fuera de ellas, y pasa si cambia solo una de las
dos cosas (tecnologia/metodologia-desarrollo#2026-11-19-2). Desde la 1.30.0 corre con el corredor que declara CORREDOR
(shared-memory/plugin-memoria#2026-11-25-5): aquí, pytest y un corredor propio de pocas líneas; vitest lo prueba P30.

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


def errores(o):
    return "\n".join(l for l in o.splitlines() if "::error::" in l)


def script(paso="Las pruebas de aceptación van en su propio pull request"):
    """El bloque «run: |» de un paso, sin su sangría, y los valores de env del workflow."""
    texto = YML.read_text(encoding="utf-8")
    i = texto.index("- name: " + paso)
    m = re.compile(r"^(\s*)run: \|\n((?:\1  .*\n|\s*\n)+)", re.M).search(texto, i)
    sangria = len(m.group(1)) + 2
    cuerpo = "".join(l[sangria:] + "\n" for l in m.group(2).rstrip("\n").split("\n"))
    env = {k: re.search(rf"^\s*{k}:\s*(\S.*?)\s*(?:#.*)?$", texto, re.M).group(1).strip('"').strip("'") for k in ("ACEPTACION", "ACTIVAS", "CORREDOR", "CONFIG", "SUFIJO")}
    return cuerpo, env


def git(d, *a):
    return subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True, check=True).stdout.strip()


def repo(sin_carpeta=False):
    d = pathlib.Path(tempfile.mkdtemp())
    git(d, "init", "-q", "-b", "main")
    git(d, "config", "user.email", "p@e.test")
    git(d, "config", "user.name", "Prueba")
    for f in ("app/main.py", "tests/aceptacion/P01_caso.py", "tests/unit/test_x.py", "pruebas/aceptación/P01_caso.py",
              ".github/workflows/pruebas-aceptacion.yml"):
        if sin_carpeta and f.startswith(("tests/aceptacion/", ".github/")):
            continue
        (d / f).parent.mkdir(parents=True, exist_ok=True)
        (d / f).write_text("x = 1\n", encoding="utf-8")
    git(d, "add", "-A")
    git(d, "commit", "-qm", "base")
    return d, git(d, "rev-parse", "HEAD")


def pr(cambios, acept=None, sin_carpeta=False, titulo="P09 · algo", lista=None, main_despues=None, base_extra=0, env_wf=None,
       base_textos=None):
    """Aplica los cambios en una rama y corre el primer paso; devuelve (código de salida, salida). lista: el texto de la
    lista de piezas activas en la base; main_despues: archivos que llegan a main después de abrir la rama; base_textos:
    {ruta: texto} en la base. En los cambios, («texto», ruta, texto) escribe ese texto."""
    d, base = repo(sin_carpeta)
    if base_textos:
        for ruta, texto in base_textos.items():
            (d / ruta).parent.mkdir(parents=True, exist_ok=True)
            (d / ruta).write_text(texto, encoding="utf-8")
        git(d, "add", "-A"); git(d, "commit", "-qm", "textos"); base = git(d, "rev-parse", "HEAD")
    if base_extra:
        (d / "tests/aceptacion/datos").mkdir(parents=True, exist_ok=True)
        for i in range(base_extra):
            (d / f"tests/aceptacion/datos/caso_{i:04d}.json").write_text("{}", encoding="utf-8")
        git(d, "add", "-A"); git(d, "commit", "-qm", "muchos"); base = git(d, "rev-parse", "HEAD")
    if lista is not None:
        (d / ".github").mkdir(exist_ok=True)
        (d / ".github/piezas-activas.txt").write_text(lista, encoding="utf-8")
        git(d, "add", "-A"); git(d, "commit", "-qm", "lista"); base = git(d, "rev-parse", "HEAD")
    git(d, "checkout", "-qb", "pieza")
    for orden, ruta, destino in cambios:
        if orden == "escribir":
            (d / ruta).parent.mkdir(parents=True, exist_ok=True)
            (d / ruta).write_text("y = 2\n", encoding="utf-8")
        elif orden == "texto":
            (d / ruta).parent.mkdir(parents=True, exist_ok=True)
            (d / ruta).write_text(destino, encoding="utf-8")
        elif orden == "lista":
            (d / ".github").mkdir(exist_ok=True)
            (d / ".github/piezas-activas.txt").write_text(ruta, encoding="utf-8")
        elif orden == "borrar":
            git(d, "rm", "-rq", ruta)
        elif orden == "mover":
            (d / destino).parent.mkdir(parents=True, exist_ok=True)
            git(d, "mv", ruta, destino)
    git(d, "add", "-A")
    git(d, "commit", "-qm", "cambio", "--allow-empty")
    if main_despues:
        git(d, "checkout", "-q", "main")
        for f in main_despues:
            (d / f).parent.mkdir(parents=True, exist_ok=True)
            (d / f).write_text("z = 3\n", encoding="utf-8")
        git(d, "add", "-A"); git(d, "commit", "-qm", "main sigue"); base = git(d, "rev-parse", "HEAD")
        git(d, "checkout", "-q", "pieza")
    cuerpo, envw = script()
    env = dict(os.environ, BASE=base, HEAD=git(d, "rev-parse", "HEAD"), ACEPTACION=acept if acept is not None else envw["ACEPTACION"],
               RUNNER_TEMP=tempfile.mkdtemp(), ACTIVAS=envw["ACTIVAS"], TITULO=titulo, CORREDOR=envw["CORREDOR"],
               CONFIG=envw["CONFIG"], SUFIJO=envw["SUFIJO"])
    env.pop("GITHUB_WORKFLOW_REF", None)   # en el CI de este repositorio apunta a pruebas.yml, no al workflow que se prueba
    env.update(env_wf or {})
    p = subprocess.run(["bash", "-c", cuerpo], cwd=d, env=env, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


print("El workflow de las pruebas de aceptación")
c, o = pr([("escribir", "tests/aceptacion/P01_caso.py", None), ("escribir", "tests/aceptacion/P02_caso.py", None)])
ok(c == 0, "un pull request que solo toca las pruebas de aceptación pasa")
c, o = pr([("escribir", "app/main.py", None), ("escribir", "tests/unit/test_x.py", None)])
ok(c == 0, "el de una pieza que no las toca pasa")
c, o = pr([("escribir", "app/main.py", None), ("escribir", "tests/aceptacion/P01_caso.py", None)])
ok(c == 1 and "::error::" in o, "uno que cambia las dos cosas falla, con el error en claro")
c, o = pr([("mover", "tests/aceptacion/P01_caso.py", "tests/unit/P01_caso.py")])
ok(c == 1, "mover una prueba de aceptación fuera de su carpeta cuenta en los dos sitios y falla")
c, o = pr([("escribir", "tests/aceptacion-viejas/P01_z.py", None), ("escribir", "tests/aceptacion/P01_caso.py", None)])
ok(c == 1, "una carpeta que solo empieza igual cuenta como fuera")
c, o = pr([("escribir", "app/main.py", None), ("escribir", "tests/aceptacion/P01_caso.py", None)], acept="tests/aceptacion/")
ok(c == 1, "con la barra final en ACEPTACION, igual")

c, o = pr([("escribir", "app/main.py", None), ("escribir", "tests/aceptacion/P01_año.py", None)])
ok(c == 1, "una prueba con acento en el nombre cuenta como dentro: con código, falla")
c, o = pr([("escribir", "tests/aceptacion/P01_sesión.py", None), ("escribir", "tests/aceptacion/P01_caso.py", None)])
ok(c == 0, "y un pull request de escenarios con acentos pasa")
c, o = pr([("escribir", "app/main.py", None), ("escribir", "pruebas/aceptación/P01_caso.py", None)], acept="pruebas/aceptación")
ok(c == 1, "una carpeta con acento, también")
for buena in ("./tests/aceptacion", "././tests/aceptacion", "tests/aceptacion//"):
    c, o = pr([("escribir", "app/main.py", None), ("escribir", "tests/aceptacion/P01_caso.py", None)], acept=buena)
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

print("Dependabot que solo sube acciones (1.30.1)")
WF_ANTES = "    steps:\n      - uses: actions/checkout@aaaa  # v6.0.0\n        with:\n          fetch-depth: 0\n"
WF_DESPUES = WF_ANTES.replace("@aaaa  # v6.0.0", "@bbbb  # v7.0.1")
FLUJOS = {".github/workflows/pruebas-aceptacion.yml": WF_ANTES, ".github/workflows/pruebas.yml": WF_ANTES}
SUBE = [("texto", f, WF_DESPUES) for f in FLUJOS]
BOT = {"AUTOR": "dependabot[bot]"}
c, o = pr(SUBE, titulo="Bump actions/checkout from 6.0.0 to 7.0.1", base_textos=FLUJOS, env_wf=BOT)
ok(c == 0 and "no se le aplican" in o, "un pull request de dependabot[bot] que solo cambia líneas «uses:» de .github/workflows/ pasa")
c, o = pr(SUBE[:1] + [("texto", ".github/workflows/pruebas.yml", WF_DESPUES.replace("fetch-depth: 0", "fetch-depth: 1"))],
          titulo="Bump actions/checkout", base_textos=FLUJOS, env_wf=BOT)
ok(c == 1 and "no vale" in o and "va en su propio pull request" in errores(o), "si además cambia otra línea del workflow, falla con la regla de siempre")
for otro in ("app/main.py", ".github/dependabot.yml"):
    c, o = pr(SUBE + [("escribir", otro, None)], titulo="Bump actions/checkout", base_textos=FLUJOS, env_wf=BOT)
    ok(c == 1 and "no vale" in o and "va en su propio pull request" in errores(o), f"si además cambia {otro}, fuera de .github/workflows/, también")
c, o = pr(SUBE, titulo="Bump actions/checkout", base_textos=FLUJOS, env_wf={"AUTOR": "persona"})
ok(c == 1 and "va en su propio pull request" in errores(o), "el mismo cambio de una persona falla como antes")

print("Montar el kit en un repositorio que aún no tiene pruebas de aceptación")
c, o = pr([("escribir", ".github/workflows/pruebas-aceptacion.yml", None), ("escribir", "CLAUDE.md", None)], sin_carpeta=True)
ok(c == 0, "el pull request que trae el workflow y el CLAUDE.md pasa")
c, o = pr([("escribir", ".github/workflows/pruebas-aceptacion.yml", None), ("escribir", "tests/aceptacion/.gitkeep", None)], sin_carpeta=True)
ok(c == 0, "con la carpeta vacía, también")
c, o = pr([("escribir", "app/main.py", None)], sin_carpeta=True)
ok(c == 0 and "no hay nada que proteger" in o, "una pieza antes de que haya escenarios pasa, y lo dice")

print("El nombre de los archivos y el título (1.27.1)")
for malo in ("test_P01_extra.py", "P01extra.py", "P02_extra.py", "sub/P01_x.py"):
    c, o = pr([("escribir", "tests/aceptacion/P01_caso.py", None), ("escribir", f"tests/aceptacion/{malo}", None)], titulo="Escenarios · P01")
    ok(c == 1 and malo in o and "«P01_»" in o, f"en «Escenarios · P01», {malo} falla y dice cómo se llama")
c, o = pr([("escribir", "tests/aceptacion/P01_caso.py", None), ("escribir", "tests/aceptacion/conftest.py", None), ("escribir", "tests/aceptacion/RESUMEN.md", None)], titulo="Escenarios · P01")
ok(c == 0, "conftest.py y el resumen entran con los escenarios")
for titulo in ("P01: alta", "P01 - alta", "p01 alta"):
    c, o = pr([("escribir", "app/main.py", None)], titulo=titulo)
    ok(c == 1 and " · »" in o, f"«{titulo}», de una pieza con pruebas, falla y dice cómo empieza el título")
c, o = pr([("escribir", "app/main.py", None)], titulo="P1: algo")
ok(c == 0, "el mismo título de una pieza sin pruebas no falla por el título")
c, o = pr([("escribir", "app/main.py", None), ("escribir", "tests/aceptacion-no/x.py", None)], titulo="P01: alta", main_despues=["tests/aceptacion/P01_canción.py"])
ok(c == 1 and " · »" in o, "tampoco se cuela si la prueba de la pieza lleva acento en el nombre")
c, o = pr([("escribir", "app/main.py", None)], titulo="Arreglo de un texto")
ok(c == 0, "un título sin pieza sigue pasando: es «fuera del plan», y lo dice el seguimiento")
for sufijo in ("*.spec.ts", "\\.spec.ts"):
    c, o = pr([("escribir", "app/main.py", None)], env_wf={"CORREDOR": "./corredor", "SUFIJO": sufijo})
    ok(c == 1 and "SUFIJO" in "\n".join(l for l in o.splitlines() if "::error::" in l), f"un SUFIJO «{sufijo}», con comodín o contrabarra, falla y lo dice")

print("Las piezas activas y los pull requests de escenarios")
CUERPO2, ENVW = script("Pasan las pruebas de las piezas activas, y fallan las de un pull request de escenarios")


CUERPOS = {"pasa": "def test_caso():\n    assert True\n", "falla": "def test_caso():\n    assert False\n",
           "rota": "def test_caso(:\n", "saltada": "import pytest\n\n\ndef test_caso():\n    pytest.skip('luego')\n",
           "vacia": "x = 1\n"}


def activas(pruebas, lista, titulo, corredor=False, archivos=None, carpeta="tests/aceptacion", entorno=None):
    """pruebas: {pieza: pasa | falla | rota | saltada | vacia}, cada una en su archivo «<pieza>_caso.py» (o los de
    «archivos», {nombre: resultado}); lista: el texto de ACTIVAS o None; corre el segundo paso con el título, con pytest
    o, con «corredor» (el texto de un guion; None si no existe), con un corredor propio, ./corredor, y SUFIJO .py."""
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "tests/aceptacion").mkdir(parents=True)
    for p, r in pruebas.items():
        (d / f"tests/aceptacion/{p}_caso.py").write_text(CUERPOS[r], encoding="utf-8")
    for n, r in (archivos or {}).items():
        (d / f"tests/aceptacion/{n}").write_text(CUERPOS[r], encoding="utf-8")
    if lista is not None:
        (d / ".github").mkdir()
        (d / ".github/piezas-activas.txt").write_text(lista, encoding="utf-8")
    propio = {}
    if corredor is not False:
        propio = {"CORREDOR": "./corredor", "SUFIJO": ".py"}
        if corredor:
            (d / "corredor").write_text(corredor, encoding="utf-8")
            (d / "corredor").chmod(0o755)
    env = dict(os.environ, ACEPTACION=carpeta, ACTIVAS=ENVW["ACTIVAS"], CORREDOR=ENVW["CORREDOR"], CONFIG=ENVW["CONFIG"],
               SUFIJO=ENVW["SUFIJO"], TITULO=titulo, RUNNER_TEMP=tempfile.mkdtemp(), PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTEST_ADDOPTS="", PYTEST_PLUGINS="")
    env.update(propio)
    env.update(entorno or {})
    r = subprocess.run(["bash", "-c", CUERPO2], cwd=d, env=env, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


ok(ENVW["CORREDOR"] == "pytest" and ENVW["ACTIVAS"].endswith(".txt"), "la plantilla trae ACTIVAS y «CORREDOR: pytest»")
c, o = activas({"P01": "falla"}, None, "Escenarios · P01")
ok(c == 0, "un pull request de escenarios se une en verde si sus pruebas fallan")
c, o = activas({"P01": "pasa"}, None, "Escenarios · P01")
ok(c == 1 and "ya pasan" in o, "si sus pruebas ya pasan antes de construir la pieza, falla")
c, o = activas({"P01": "falla", "P02": "falla"}, None, "Escenarios · P01 + P02 · alta y lista")
ok(c == 0, "uno de varias piezas, también")
c, o = activas({"P01": "falla"}, None, "P09 · otra cosa")
ok(c == 0, "una pieza que aún no está en la lista no corre sus pruebas")
c, o = activas({"P01": "pasa"}, "P01\n", "P01 · alta de clientes")
ok(c == 0, "la pieza que se añade a la lista pasa si sus pruebas pasan")
c, o = activas({"P01": "falla"}, "# piezas activas\nP01\n", "P01 · alta de clientes")
ok(c == 1 and "no pasan" in o, "y falla si no pasan")
c, o = activas({"P01": "pasa", "P02": "falla"}, "P01", "P02 · lista")
ok(c == 0, "las de otra pieza aún no activa no cuentan")
c, o = activas({"P01": "pasa", "P02": "falla"}, "P01", "Escenarios · P02")
ok(c == 0, "un pull request de escenarios corre también las activas, y pasa si pasan")
c, o = activas({"P01": "falla"}, "P01", "Escenarios · P01")
ok(c == 1, "cambiar los escenarios de una pieza activa sigue exigiendo que pasen")
c, o = activas({"P01": "pasa"}, "P01; rm -rf /\n", "P01 · x")
ok(c == 1 and "no es un identificador" in o, "una línea de la lista que no es un identificador falla, sin correr nada")
c, o = activas({"P01": "falla"}, None, "Escenarios · $(touch pwned)")
ok(c == 1 and "no dice qué pieza" in o, "un título que no es una pieza falla, sin correr nada")

print("Las pruebas de una pieza son sus archivos, y todas las activas corren de una vez (1.27.1)")
c, o = activas({"P1": "pasa"}, "P1\n", "P9 · x", archivos={"P10_caso.py": "falla", "AP1_caso.py": "falla", "test_P1_otro.py": "falla"})
ok(c == 0 and "P10_caso" not in o and "AP1_caso" not in o, "P1 no corre las de P10 ni las de un archivo que solo contiene «P1_»")
c, o = activas({"P1": "falla", "P2": "pasa", "P3": "falla"}, "P1\nP2\nP3\n", "P9 · x")
e = errores(o)
ok(c == 1 and " P1," in e and " P3," in e and "P2" not in e and o.count("test session starts") == 1, "una corrida para todas, y el error nombra las que fallan y solo esas")
c, o = activas({"P1": "saltada", "P2": "pasa"}, "P1\nP2\n", "P9 · x")
ok(c == 1 and "de P1 no pasaron todas" in errores(o) and "P2" not in errores(o), "una saltada no cuenta como pasada, y se nombra su pieza")
c, o = activas({"P2": "pasa"}, "P1\nP2\n", "P9 · x")
ok(c == 1 and "P1 está en la lista" in errores(o), "una pieza activa sin archivos de pruebas falla y dice cómo se llaman")
c, o = activas({"P1": "rota", "P2": "pasa"}, "P1\nP2\n", "P9 · x")
ok(c == 1 and " P1," in errores(o) and "P2" not in errores(o), "un archivo que no carga cuenta contra su pieza")

print("«Fallan» quiere decir que fallaron como pruebas")
c, o = activas({}, None, "Escenarios · P01")
ok(c == 1 and "No hay pruebas de P01" in o, "sin pruebas de la pieza: falla y dice cómo se llaman sus archivos")
c, o = activas({"P01": "rota"}, None, "Escenarios · P01")
ok(c == 1 and "no fallaron como pruebas" in o, "un error al cargarlas: falla y lo dice")
for titulo, lista in (("Escenarios · P01", None), ("P9 · x", "P01\n")):
    c, o = activas({"P01": "pasa" if lista else "falla"}, lista, titulo, archivos={"conftest.py": "rota"})
    ok(c == 1 and ("no fallaron como pruebas" in o or "no se pudieron correr" in o), f"un conftest.py que no carga (salida 4) en «{titulo}»: falla y lo dice")
c, o = activas({"P01": "vacia"}, "P01\n", "P9 · x")
ok(c == 1 and "P01, que ya cuenta, no corrió" in errores(o), "un archivo sin pruebas, que no corre, no cuenta como pasado")
for carpeta in ("./tests/aceptacion", "tests/aceptacion//"):
    c, o = activas({"P01": "pasa", "P02": "falla"}, "P01\nP02\n", "P9 · x", carpeta=carpeta, archivos={"P01_con espacio.py": "pasa"})
    ok(c == 1 and " P02," in errores(o) and "P01" not in errores(o), f"con ACEPTACION «{carpeta}» y un archivo con espacio, el error nombra solo la que falla")
c, o = activas({"P01": "falla"}, None, "Escenarios · P01", corredor=None)
ok(c == 1 and "no se pudieron correr" in o, "el corredor que no está: falla y lo dice")
SIN_PYTEST = pathlib.Path(tempfile.mkdtemp())   # un python3 que no ve lo instalado: «No module named pytest»
(SIN_PYTEST / "python3").write_text(f'#!/bin/sh\nexec "{sys.executable}" -I -S "$@"\n', encoding="utf-8")
(SIN_PYTEST / "python3").chmod(0o755)
c, o = activas({"P01": "falla"}, None, "Escenarios · P01", entorno={"PATH": f"{SIN_PYTEST}{os.pathsep}{os.environ['PATH']}"})
ok(c == 1 and "pytest no está instalado" in errores(o), "con pytest sin instalar, un «Escenarios · P01» falla y lo dice")
LEE = '#!/usr/bin/env bash\ncat > /dev/null\nfor f; do case "$f" in *P02_*) echo "FALLA $f" ;; *) echo "PASA $f" ;; esac; done\n'
c, o = activas({"P01": "pasa", "P02": "falla"}, "P01\nP02\n", "P03 · x", corredor=LEE)
ok(c == 1 and "P02" in errores(o) and "P01" not in errores(o), "un corredor que lee la entrada estándar no se come la lista")

print("La configuración del ejecutor de fuera de la carpeta no pone en verde las pruebas (con pytest de verdad)")
TRAMPAS = {
    "conftest.py": "import pytest\ndef pytest_collection_modifyitems(items):\n    for i in items: i.add_marker(pytest.mark.skip)\n",
    "tests/conftest.py": ("import pytest\n@pytest.hookimpl(hookwrapper=True)\ndef pytest_runtest_makereport(item, call):\n"
                          "    o = yield; o.get_result().outcome = 'passed'\n"),
    "pyproject.toml": "[tool.pytest.ini_options]\naddopts = '--co'\n",
    "pytest.ini": "[pytest]\naddopts = -p no:python\n",
    "setup.cfg": "[tool:pytest]\naddopts = --co\n",
}


def con_pytest(trampa, lista, titulo, prueba_p01="assert False", conftest_dentro=None, extra=None, entorno=None,
               cabecera=""):
    """Un repositorio con la prueba de P01 en la carpeta y un archivo de fuera que intenta ponerla en verde; corre el
    segundo paso con el pytest de la plantilla."""
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "tests/aceptacion").mkdir(parents=True)
    (d / "tests/aceptacion/P01_caso.py").write_text(f"{cabecera}def test_p01_caso({'dato' if conftest_dentro else ''}):\n    {prueba_p01}\n", encoding="utf-8")
    for ruta, texto in (extra or {}).items():
        (d / ruta).parent.mkdir(parents=True, exist_ok=True)
        (d / ruta).write_text(texto, encoding="utf-8")
    if conftest_dentro:
        (d / "tests/aceptacion/conftest.py").write_text(conftest_dentro, encoding="utf-8")
    if trampa:
        (d / trampa).parent.mkdir(parents=True, exist_ok=True)
        (d / trampa).write_text(TRAMPAS[trampa], encoding="utf-8")
    if lista is not None:
        (d / ".github").mkdir()
        (d / ".github/piezas-activas.txt").write_text(lista, encoding="utf-8")
    env = dict(os.environ, ACEPTACION=ENVW["ACEPTACION"], ACTIVAS=ENVW["ACTIVAS"], CORREDOR=ENVW["CORREDOR"],
               CONFIG=ENVW["CONFIG"], SUFIJO=ENVW["SUFIJO"], TITULO=titulo,
               RUNNER_TEMP=tempfile.mkdtemp(), PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTEST_ADDOPTS="", PYTEST_PLUGINS="")
    env.update(entorno or {})
    r = subprocess.run(["bash", "-c", CUERPO2], cwd=d, env=env, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


yml = YML.read_text(encoding="utf-8")
ok(all(f'{v}: ""' in yml for v in ("PYTEST_ADDOPTS", "PYTEST_PLUGINS")) and 'PYTEST_DISABLE_PLUGIN_AUTOLOAD: "1"' in yml,
   "el paso no carga solos los plugins que instala el código, ni lee PYTEST_ADDOPTS o PYTEST_PLUGINS del entorno")
ok(all(x in yml for x in ("pytest -c /dev/null", '--confcutdir="$dir"', "--rootdir=.")), "pytest no lee la configuración de fuera")
try:
    import pytest as _pytest  # noqa: F401
    hay_pytest = True
except ImportError:
    hay_pytest = False
if not hay_pytest:
    print("  (sin pytest instalado: se saltan los casos con pytest de verdad)")
    ok(not os.environ.get("CI"), "en CI, pytest está instalado")
else:
    for trampa in TRAMPAS:
        c, o = con_pytest(trampa, "P01\n", "P02 · otra cosa")
        ok(c == 1 and "no pasan" in o, f"un {trampa} fuera de la carpeta no pone en verde las pruebas de una pieza activa")
        c, o = con_pytest(trampa, None, "Escenarios · P01")
        ok(c == 0, f"ni hace que las de un pull request de escenarios «ya pasen» ({trampa})")
    c, o = con_pytest(None, "P01\n", "P02 · x", prueba_p01="assert dato == 1",
                      conftest_dentro="import pytest\n@pytest.fixture\ndef dato():\n    return 1\n")
    ok(c == 0, "el conftest.py de la propia carpeta sí cuenta")
    c, o = con_pytest(None, "P01\n", "P02 · x", prueba_p01="pass")
    ok(c == 0, "y unas pruebas que pasan, pasan")
    for var, valor in (("PYTEST_ADDOPTS", "--co"), ("PYTEST_PLUGINS", "trampa")):
        c, o = con_pytest(None, "P01\n", "P02 · x", entorno={var: valor},
                          extra={"trampa.py": "import pytest\ndef pytest_collection_modifyitems(items):\n    for i in items: i.add_marker(pytest.mark.skip)\n"})
        ok(c == 1, f"{var} que dejó algo instalado no las pone en verde")
    c, o = con_pytest(None, "P01\n", "P02 · x", prueba_p01="from app.p01 import f\n    assert f() == 2",
                      extra={"app/__init__.py": "", "app/p01.py": "import pytest\ndef f():\n    pytest.skip('luego')\n"})
    ok(c == 1 and "no pasaron todas" in o, "el código de la pieza que salta su prueba no la pone en verde")
    c, o = con_pytest(None, "P01\n", "P02 · x", prueba_p01="import asyncio\n    assert False", cabecera="async ")
    ok(c == 1, "una prueba async sin su plugin no cuenta como verde")
    c, o = con_pytest(None, "P01\n", "P02 · x", prueba_p01="from app.p01 import f\n    assert f() == 2",
                      extra={"app/__init__.py": "", "app/p01.py": "def f():\n    return 2\n"})
    ok(c == 0, "el código del repositorio se importa sin instalarlo ni configurar nada")
    c, o = con_pytest(None, None, "Escenarios · P01", prueba_p01="from app.p01 import f\n    assert f() == 2",
                      extra={"app/__init__.py": ""})
    ok(c == 0 and "ModuleNotFoundError: No module named 'app.p01'" in o,
       "en un pull request de escenarios, lo que falta es la pieza, no el paquete de la aplicación")

c, o = pr([("escribir", "tests/aceptacion/__init__.py", None)], titulo="Escenarios · P01")
ok(c == 1 and "__init__.py" in o, "una carpeta de aceptación con __init__.py falla: pytest ejecutaría el de arriba")

print("La lista de piezas activas no pierde ninguna pieza (#2026-11-19-7)")
c, o = pr([("lista", "P02\n", None), ("escribir", "app/main.py", None)], lista="P01\nP02\n", titulo="P03 · x")
ok(c == 1 and "quita P01" in o, "quitar una pieza de la lista con código falla")
c, o = pr([("borrar", ".github/piezas-activas.txt", None), ("escribir", "app/main.py", None)], lista="P01\n", titulo="P03 · x")
ok(c == 1 and "quita P01" in o, "borrar la lista, también")
c, o = pr([("lista", "P02\n", None), ("escribir", "tests/aceptacion/P01_caso.py", None)], lista="P01\nP02\n", titulo="Escenarios · P01 · nuevo caso")
ok(c == 0 and "sale de la lista" in o, "el pull request de escenarios de P01 la saca mientras cambian sus escenarios")
c, o = pr([("lista", "P01\n", None), ("escribir", "tests/aceptacion/P01_caso.py", None)], lista="P01\nP02\n", titulo="Escenarios · P01 · x")
ok(c == 1 and "quita P02" in o, "pero no otra pieza")
c, o = pr([("escribir", "app/main.py", None)], lista="P02\n", titulo="P01 · alta")
ok(c == 1 and "no está en" in o, "el pull request de una pieza con pruebas en la carpeta que no la añade falla")
c, o = pr([("escribir", "app/main.py", None), ("lista", "P02\nP01\n", None)], lista="P02\n", titulo="P01 · alta")
ok(c == 0, "y pasa si la añade")
c, o = pr([("escribir", "app/main.py", None)], lista="P02\n", titulo="P05 · migrar la base")
ok(c == 0, "una pieza técnica, sin pruebas en la carpeta, no necesita la lista")
c, o = pr([("escribir", "app/main.py", None)], sin_carpeta=True, titulo="P01 · alta", main_despues=["tests/aceptacion/P02_caso.py"])
ok(c == 0, "una rama abierta antes de los primeros escenarios no sale como «quita la carpeta»")

print("Lo que abrió la protección de la lista (revisión de sus arreglos)")
c, o = pr([("lista", "P02\n", None), ("escribir", "app/main.py", None)], lista="P01\nP02\n", titulo="Escenarios · P01 · arreglo")
ok(c == 1 and "quita P01" in o, "un «Escenarios · P01» que cambia código no puede sacar P01 de la lista")
c, o = pr([("lista", "P02\n", None), ("escribir", "tests/aceptacion/P01_caso.py", None)], lista="P01\nP02\n", titulo="Escenarios · P01")
ok(c == 0, "con el título que pone el agente, «Escenarios · P01», sí la saca")
c, o = pr([("lista", "P02\n", None), ("escribir", "app/main.py", None)], lista="P01\nP02\n", titulo='Revert "P01 · alta de clientes"')
ok(c == 0 and "reversión saca P01" in o, "la reversión de una pieza la saca de la lista, y lo avisa")
c, o = pr([("lista", "P01\n", None), ("escribir", "app/main.py", None)], lista="P01\nP02\n", titulo='Revert "P01 · alta"')
ok(c == 1 and "quita P02" in o, "pero no otra")
c, o = pr([("escribir", "app/main.py", None)], lista="p01\n", titulo="P01 · ajuste")
ok(c == 0, "la lista y el título se comparan sin mayúsculas")
c, o = pr([("borrar", ".github/piezas-activas.txt", None), ("escribir", ".github/piezas-activas.txt/P01", None), ("escribir", "app/main.py", None)], lista="P01\n", titulo="P03 · x")
ok(c == 1, "la lista cambiada por una carpeta falla")
c, o = pr([("escribir", "app/main.py", None)], lista="", titulo="P01 · alta", base_extra=2500)
ok(c == 1 and "no está en" in o, "una pieza con pruebas que no se añade falla también con 2.500 archivos en la carpeta")

print()
print("Todo bien." if not fallos else f"{fallos} fallo(s).")
sys.exit(1 if fallos else 0)
