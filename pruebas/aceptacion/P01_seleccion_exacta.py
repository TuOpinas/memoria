#!/usr/bin/env python3
"""P01 · Exact piece selection (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-22, en el plan).

- Only the piece's own tests run. Dado active pieces P1 and P10 with `P1_alta.py` and `P10_baja.py`, Cuando the check
  runs P1, Entonces only `P1_alta.py` runs.
- A failure is named by its piece. Dado P1's test failing and P10's passing, Cuando the check runs, Entonces it fails and
  names P1.

Contra la plantilla del workflow (pruebas-aceptacion.yml), con pytest: siempre el workflow entero sobre un pull request
de código. Cómo se monta cada escenario, y lo que pide de más, está en RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P01_seleccion_exacta.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import flujo  # noqa: E402

CODIGO = {"app/main.py": "x = 2\n"}


def escenarios(inf):
    acept, activas = flujo.plantilla_activas()

    # 1 · Solo P1 está activa; P10 tiene su prueba en la carpeta, que falla, y no cuenta todavía
    extra, leer = flujo.marcas()
    base = {activas: "P1\n",
            f"{acept}/P1_alta.py": flujo.sembrada("P1_alta", "pasa"),
            f"{acept}/P10_baja.py": flujo.sembrada("P10_baja", "falla")}
    rc, salida = flujo.comprobar(base, CODIGO, "P9 · otra cosa", extra)
    corrieron = {n for n, _ in leer()}
    problemas = []
    if "P1_alta" not in corrieron:
        problemas.append("P1_alta.py no corrió")
    if "P10_baja" in corrieron:
        problemas.append("P10_baja.py corrió: las pruebas de P1 tomaron también las de P10")
    problemas += flujo.verde(rc, salida)
    inf.escenario("Solo corren las pruebas de la pieza", problemas, salida if problemas else "")

    # 2 · El fallo nombra a su pieza (y, al revés, el de P10 nombra a P10 y no a P1)
    nombre = {"P1": "P1_alta", "P10": "P10_baja"}
    for falla, pasa in (("P1", "P10"), ("P10", "P1")):
        extra, leer = flujo.marcas()
        base = {activas: "P1\nP10\n",
                f"{acept}/{nombre[falla]}.py": flujo.sembrada(nombre[falla], "falla"),
                f"{acept}/{nombre[pasa]}.py": flujo.sembrada(nombre[pasa], "pasa")}
        rc, salida = flujo.comprobar(base, CODIGO, "P9 · otra cosa", extra)
        err = flujo.errores(salida)
        corrieron = {n for n, _ in leer()}
        problemas = []
        if rc == 0:
            problemas.append(f"el check pasó con la prueba de {falla} fallando")
        if nombre[falla] not in corrieron:
            problemas.append(f"la prueba de {falla} ({nombre[falla]}.py) no llegó a correr: el check no falla porque falle ella")
        if not flujo.nombra(err, falla):
            problemas.append(f"ningún error nombra a {falla}")
        if flujo.nombra(err, pasa):
            problemas.append(f"un error nombra a {pasa}, cuyas pruebas pasan: {[l for l in err if pasa in l][:1]}")
        inf.escenario(f"El fallo nombra a su pieza (falla {falla}, pasa {pasa})", problemas, salida if problemas else "")

    # 3 · Control: con las dos activas y pasando, el check queda en verde
    extra, leer = flujo.marcas()
    base = {activas: "P1\nP10\n",
            f"{acept}/P1_alta.py": flujo.sembrada("P1_alta", "pasa"),
            f"{acept}/P10_baja.py": flujo.sembrada("P10_baja", "pasa")}
    rc, salida = flujo.comprobar(base, CODIGO, "P9 · otra cosa", extra)
    corrieron = {n for n, _ in leer()}
    problemas = [f"no corrió {n}.py" for n in ("P1_alta", "P10_baja") if n not in corrieron] + flujo.verde(rc, salida)
    inf.escenario("Con todas las pruebas pasando, el check queda en verde", problemas, salida if problemas else "")


flujo.principal("P01", escenarios)
