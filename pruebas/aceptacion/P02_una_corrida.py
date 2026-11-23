#!/usr/bin/env python3
"""P02 · One run for all active pieces (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-22, en el plan).

- One run tests every active piece. Dado three active pieces, Cuando the check runs, Entonces one runner process tests
  all three and names any that failed.
- A skipped test does not count as passing. Dado an active piece with a skipped test, Cuando the check runs, Entonces it
  fails and names that piece.

Contra la plantilla del workflow (pruebas-aceptacion.yml), con pytest, el workflow entero sobre un pull request de código.
«One runner process»: todas las pruebas sembradas ven el mismo identificador de proceso. Cómo se monta cada escenario, y
lo que pide de más, está en RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P02_una_corrida.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import flujo  # noqa: E402

CODIGO = {"app/main.py": "x = 2\n"}
TRES = ("P1_alta", "P2_lista", "P3_baja")


def escenarios(inf):
    acept, activas = flujo.plantilla_activas()

    def tres(resultados):
        """P1, P2 y P3 activas con esos resultados, y P4 con una prueba que falla y que aún no está activa."""
        base = {activas: "P1\nP2\nP3\n", f"{acept}/P4_nueva.py": flujo.sembrada("P4_nueva", "falla")}
        for n, r in zip(TRES, resultados):
            base[f"{acept}/{n}.py"] = flujo.sembrada(n, r)
        extra, leer = flujo.marcas()
        rc, salida = flujo.comprobar(base, CODIGO, "P9 · otra cosa", extra)
        vistas = leer()
        problemas = []
        faltan = sorted(set(TRES) - {n for n, _ in vistas})
        if faltan:
            problemas.append(f"no corrieron las pruebas de {', '.join(faltan)}")
        if len({pid for _, pid in vistas}) > 1:
            problemas.append(f"las pruebas corrieron en {len({pid for _, pid in vistas})} procesos del ejecutor, no en uno")
        if "P4_nueva" in {n for n, _ in vistas}:
            problemas.append("corrió la prueba de P4, que no está activa")
        return rc, salida, problemas

    # 1 · Una corrida prueba todas las activas: fallan P1 y P3, pasa P2
    rc, salida, problemas = tres(("falla", "pasa", "falla"))
    err = flujo.errores(salida)
    if rc == 0:
        problemas.append("el check pasó con P1 y P3 fallando")
    for p in ("P1", "P3"):
        if not flujo.nombra(err, p):
            problemas.append(f"ningún error nombra a {p}, que falló")
    for p in ("P2", "P4"):
        if flujo.nombra(err, p):
            problemas.append(f"un error nombra a {p}, que no falló entre las activas")
    inf.escenario("Una corrida prueba todas las piezas activas", problemas, salida if problemas else "")

    # 2 · Una prueba saltada no cuenta como pasada: la pieza con una saltada, junto a otra que pasa entera
    for saltada, otra in (("P1", "P2"), ("P2", "P1")):
        extra, leer = flujo.marcas()
        base = {activas: "P1\nP2\n",
                f"{acept}/{saltada}_caso.py": flujo.sembrada(f"{saltada}_pasa", "pasa")
                + "\n\n" + flujo.otra(flujo.sembrada(f"{saltada}_saltada", "saltada")),
                f"{acept}/{otra}_caso.py": flujo.sembrada(f"{otra}_pasa", "pasa")}
        rc, salida = flujo.comprobar(base, CODIGO, "P9 · otra cosa", extra)
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
        inf.escenario(f"Una prueba saltada no cuenta como pasada (la saltada es de {saltada})", problemas,
                      salida if problemas else "")

    # 3 · Control: con las tres pasando, una sola corrida y el check en verde
    rc, salida, problemas = tres(("pasa", "pasa", "pasa"))
    problemas += flujo.verde(rc, salida)
    inf.escenario("Con todas las pruebas pasando, una sola corrida y el check en verde", problemas, salida if problemas else "")


flujo.principal("P02", escenarios)
