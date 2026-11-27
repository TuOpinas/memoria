#!/usr/bin/env python3
"""P39 · A control without holes (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-26, en el plan).

- A file at the root does not stand in for pytest. Dado an active piece whose test fails, with pytest as runner,
  Cuando a pull request adds at the repository's root a `pytest.py` that prints passed tests, Entonces the control
  fails and names the piece.

Contra la plantilla del workflow (pruebas-aceptacion.yml), con flujo.py, como P30: el workflow entero sobre un
repositorio temporal con la base y la cabeza de un pull request. Cómo se monta está en RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P39_pytest_de_la_raiz.py (0 pasa, 1 falla, 2 no se
montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import flujo  # noqa: E402

# Un pytest.py de mentira en la raíz: por cada archivo .py que le pasan escribe la línea del resumen corto de una
# prueba pasada, y cierra como cierra pytest cuando todo pasa. Sale con 0.
PYTEST_FALSO = (
    "import sys\n"
    "archivos = [a for a in sys.argv[1:] if a.endswith('.py') and not a.startswith('-')]\n"
    "print('============================= test session starts ==============================')\n"
    "print('=========================== short test summary info ============================')\n"
    "for a in archivos:\n"
    "    print('PASSED ' + a + '::test_caso')\n"
    "print('============================== %d passed in 0.01s ===============================' % len(archivos))\n"
    "sys.exit(0)\n")


def escenarios(inf):
    acept, activas = flujo.plantilla_activas()
    extra, leer = flujo.marcas()
    base = {activas: "P05\nP06\n",
            f"{acept}/P05_alta.py": flujo.sembrada("P05_alta", "falla"),
            f"{acept}/P06_baja.py": flujo.sembrada("P06_baja", "pasa")}
    cabeza = {"pytest.py": PYTEST_FALSO, "app/main.py": "x = 2\n"}
    rc, salida = flujo.comprobar(base, cabeza, "P09 · otra cosa", extra, env_wf={"CORREDOR": "pytest"})
    err = flujo.errores(salida)
    problemas = []
    if rc == 0:
        problemas.append("el control quedó en verde con la prueba de P05 fallando y un pytest.py en la raíz")
    if not flujo.nombra(err, "P05"):
        problemas.append("ningún error nombra a P05")
    if flujo.nombra(err, "P06"):
        problemas.append("un error nombra a P06, cuyas pruebas pasan")
    if "P05_alta" not in {n for n, _ in leer()} and rc == 0:
        problemas.append("la prueba de P05 no llegó a correr: la corrió el pytest.py de la raíz")
    inf.escenario("A file at the root does not stand in for pytest (pytest.py en la raíz, P05 activa falla)",
                  problemas, salida if problemas else "")


flujo.principal("P39", escenarios)
