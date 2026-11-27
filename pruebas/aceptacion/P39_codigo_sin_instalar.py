#!/usr/bin/env python3
"""P39 · A control without holes (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-26, en el plan).

- Code that is not installed is still found. Dado an active piece whose test imports a package at the repository's
  root that is not installed, Cuando the control runs, on Python 3.9 and on the current one, Entonces the test passes.

Contra la plantilla del workflow (pruebas-aceptacion.yml), con flujo.py, como P30. El arnés corre los pasos con el
python3 del PATH: esa es «la actual». Para Python 3.9 la prueba busca «python3.9» en el PATH, con pytest, y pone
delante del PATH un python3 que lo llama; si no lo encuentra, lo dice en una línea «sin comprobar» y no lo cuenta.
Cómo se monta está en RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P39_codigo_sin_instalar.py (0 pasa, 1 falla, 2 no se
montó).
"""
import os, pathlib, shutil, subprocess, sys, tempfile

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import flujo  # noqa: E402

# La prueba de la pieza activa importa el paquete de la raíz dentro de la prueba, y deja su marca antes y después
PRUEBA = ("import os, sys\n\n\n"
          "def test_usa_el_paquete():\n"
          "    with open(os.environ['MARCAS'], 'a', encoding='utf-8') as f:\n"
          "        f.write('P05_alta %d.%d\\n' % sys.version_info[:2])\n"
          "    from app import VALOR\n"
          "    assert VALOR == 41\n"
          "    with open(os.environ['MARCAS'], 'a', encoding='utf-8') as f:\n"
          "        f.write('importado ' + str(os.getpid()) + '\\n')\n")


def caso(inf, nombre, version):
    acept, activas = flujo.plantilla_activas()
    extra, leer = flujo.marcas()
    base = {activas: "P05\n",
            "app/__init__.py": "VALOR = 41\n",
            f"{acept}/P05_alta.py": PRUEBA}
    rc, salida = flujo.comprobar(base, {"app/main.py": "x = 2\n"}, "P09 · otra cosa", extra, env_wf={"CORREDOR": "pytest"})
    marcas = {n for n, _ in leer()}
    versiones = {v for n, v in leer() if n == "P05_alta"}
    problemas = []
    if "P05_alta" not in marcas:
        problemas.append("la prueba de P05 no llegó a correr")
    elif versiones != {version}:
        problemas.append(f"la prueba de P05 corrió con Python {', '.join(sorted(versiones))}, no con {version}")
    elif "importado" not in marcas:
        problemas.append("la prueba de P05 corrió y no pudo importar el paquete app de la raíz")
    problemas += flujo.verde(rc, salida)
    inf.escenario(f"Code that is not installed is still found ({nombre})", problemas, salida if problemas else "")


def python39():
    """La ruta de un python3.9 del PATH que tiene pytest, o None."""
    p = shutil.which("python3.9")
    if not p:
        return None
    r = subprocess.run([p, "-m", "pytest", "--version"], capture_output=True)
    return p if r.returncode == 0 else None


def escenarios(inf):
    actual = subprocess.run(["python3", "-c", "import sys; print('%d.%d' % sys.version_info[:2])"],
                            capture_output=True, text=True).stdout.strip()
    caso(inf, f"Python actual, {actual}", actual)
    p39 = python39()
    if not p39:
        print("  sin comprobar P39 · Code that is not installed is still found (Python 3.9): no hay python3.9 con "
              "pytest en el PATH")
        return
    # un python3 que llama a python3.9, delante del PATH: los pasos del control lo toman como el python3 de la máquina
    d = pathlib.Path(tempfile.mkdtemp(prefix="p39-py39-"))
    try:
        (d / "python3").write_text(f"#!/usr/bin/env bash\nexec {p39!r} \"$@\"\n".replace("'", '"'), encoding="utf-8")
        (d / "python3").chmod(0o755)
        antes = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{d}{os.pathsep}{antes}"
        flujo._comprobado.discard("pytest")   # que el arnés vuelva a mirar pytest con este python3
        try:
            caso(inf, "Python 3.9", "3.9")
        finally:
            os.environ["PATH"] = antes
            flujo._comprobado.discard("pytest")
    finally:
        shutil.rmtree(d, True)


flujo.principal("P39", escenarios)
