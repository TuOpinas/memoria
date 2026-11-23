#!/usr/bin/env python3
"""P03 · «Has tests» by file name (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-22, en el plan).

- A test file must start with its piece. Dado a scenarios pull request with a test file that does not start with its
  piece and «_», Cuando the check runs, Entonces it fails and says how to name the file.
- A badly written title does not slip through. Dado P01 has tests in the folder, Cuando a code pull request titled
  «P01: alta» runs the check, Entonces it fails and says the title must start «P01 · ».

Contra la plantilla del workflow (pruebas-aceptacion.yml), con pytest, el workflow entero sobre el pull request. «Says how
to name the file»: un error dice el prefijo «P1_» fuera del nombre del archivo mal puesto.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P03_nombre_y_titulo.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import flujo  # noqa: E402


def escenarios(inf):
    acept, _ = flujo.plantilla_activas()

    # 1 · A test file must start with its piece: «Escenarios · P1» con un archivo que no empieza por «P1_»
    for malo in ("test_P1_alta.py", "P1alta.py", "alta_P1.py"):
        base = {f"{acept}/P2_lista.py": flujo.sembrada("P2_lista", "pasa")}
        extra, _ = flujo.marcas()
        rc, salida = flujo.comprobar(base, {f"{acept}/{malo}": flujo.sembrada("P1_alta", "falla")}, "Escenarios · P1", extra)
        err = flujo.errores(salida)
        problemas = []
        if rc == 0:
            problemas.append(f"el check pasó con {malo}, que no empieza por «P1_»")
        if not any("P1_" in l.replace(malo, "") for l in err):
            problemas.append("ningún error dice que el archivo tiene que empezar por «P1_»")
        inf.escenario(f"A test file must start with its piece ({malo})", problemas, salida if problemas else "")

    # 2 · A badly written title does not slip through
    base = {f"{acept}/P01_alta.py": flujo.sembrada("P01_alta", "falla")}
    extra, _ = flujo.marcas()
    rc, salida = flujo.comprobar(base, {"app/main.py": "x = 2\n"}, "P01: alta", extra)
    err = flujo.errores(salida)
    problemas = []
    if rc == 0:
        problemas.append("el check pasó con el título «P01: alta»")
    if not any("P01 · " in l for l in err):
        problemas.append("ningún error dice que el título tiene que empezar «P01 · »")
    inf.escenario("A badly written title does not slip through («P01: alta»)", problemas, salida if problemas else "")


flujo.principal("P03", escenarios)
