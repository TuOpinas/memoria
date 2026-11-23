#!/usr/bin/env python3
"""P02 · One run for all active pieces (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-22, en el plan).

- One run tests every active piece. Dado three active pieces, Cuando the check runs, Entonces one runner process tests
  all three and names any that failed.
- A skipped test does not count as passing. Dado an active piece with a skipped test, Cuando the check runs, Entonces it
  fails and names that piece.

Contra la plantilla del workflow (pruebas-aceptacion.yml), con pytest, el workflow entero sobre un pull request de código.
Los archivos de pruebas se llaman como pide P03 (la pieza y «_»). «One runner process»: todas las pruebas sembradas ven el
mismo identificador de proceso.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P02_una_corrida.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import flujo  # noqa: E402


def escenarios(inf):
    acept, activas = flujo.plantilla_activas()

    # 1 · One run tests every active piece: P1 y P3 fallan, P2 pasa
    extra, leer = flujo.marcas()
    base = {activas: "P1\nP2\nP3\n",
            f"{acept}/P1_alta.py": flujo.sembrada("P1_alta", "falla"),
            f"{acept}/P2_lista.py": flujo.sembrada("P2_lista", "pasa"),
            f"{acept}/P3_baja.py": flujo.sembrada("P3_baja", "falla")}
    rc, salida = flujo.comprobar(base, {"app/main.py": "x = 2\n"}, "P9 · otra cosa", extra)
    vistas = leer()
    corrieron = {n for n, _ in vistas}
    procesos = {pid for _, pid in vistas}
    err = flujo.errores(salida)
    problemas = []
    faltan = sorted({"P1_alta", "P2_lista", "P3_baja"} - corrieron)
    if faltan:
        problemas.append(f"no corrieron las pruebas de {', '.join(faltan)}")
    if len(procesos) > 1:
        problemas.append(f"las pruebas corrieron en {len(procesos)} procesos del ejecutor, no en uno")
    if rc == 0:
        problemas.append("el check pasó con P1 y P3 fallando")
    for p in ("P1", "P3"):
        if not flujo.nombra(err, p):
            problemas.append(f"ningún error nombra a {p}, que falló")
    if flujo.nombra(err, "P2"):
        problemas.append("un error nombra a P2, cuyas pruebas pasan")
    inf.escenario("One run tests every active piece", problemas, salida if problemas else "")

    # 2 · A skipped test does not count as passing: la pieza con una prueba saltada, entre otras que pasan
    for saltada, otra in (("P1", "P2"), ("P2", "P1")):
        extra, leer = flujo.marcas()
        base = {activas: "P1\nP2\n",
                f"{acept}/{saltada}_caso.py": flujo.sembrada(f"{saltada}_pasa", "pasa")
                + "\n\n" + flujo.sembrada(f"{saltada}_saltada", "saltada").split("\n\n\n", 1)[1],
                f"{acept}/{otra}_caso.py": flujo.sembrada(f"{otra}_pasa", "pasa")}
        rc, salida = flujo.comprobar(base, {"app/main.py": "x = 2\n"}, "P9 · otra cosa", extra)
        corrieron = {n for n, _ in leer()}
        err = flujo.errores(salida)
        problemas = []
        if f"{saltada}_saltada" not in corrieron:
            problemas.append(f"la prueba saltada de {saltada} no llegó a cargarse: el check no falla por ella")
        if rc == 0:
            problemas.append(f"el check pasó con una prueba de {saltada} saltada")
        if not flujo.nombra(err, saltada):
            problemas.append(f"ningún error nombra a {saltada}, la de la prueba saltada")
        if flujo.nombra(err, otra):
            problemas.append(f"un error nombra a {otra}, cuyas pruebas pasan todas")
        inf.escenario(f"A skipped test does not count as passing ({saltada} con una saltada)", problemas,
                      salida if problemas else "")


flujo.principal("P02", escenarios)
