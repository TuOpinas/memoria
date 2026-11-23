#!/usr/bin/env python3
"""P03 · «Has tests» by file name (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-22, en el plan).

- A test file must start with its piece. Dado a scenarios pull request with a test file that does not start with its
  piece and «_», Cuando the check runs, Entonces it fails and says how to name the file.
- A badly written title does not slip through. Dado P01 has tests in the folder, Cuando a code pull request titled
  «P01: alta» runs the check, Entonces it fails and says the title must start «P01 · ».

Contra la plantilla del workflow (pruebas-aceptacion.yml), con pytest, el workflow entero sobre el pull request. Cómo se
monta cada escenario, y lo que pide de más, está en RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P03_nombre_y_titulo.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import flujo  # noqa: E402

CODIGO = {"app/main.py": "x = 2\n"}


def escenarios(inf):
    acept, activas = flujo.plantilla_activas()

    # 1 · El archivo de una prueba empieza por su pieza: «Escenarios · P1» trae un archivo bien nombrado, que falla
    #     como debe, y otro mal nombrado
    for malo in ("test_P1_extra.py", "P1extra.py", "extra_P1.py", "P2_extra.py"):
        extra, _ = flujo.marcas()
        cabeza = {f"{acept}/P1_alta.py": flujo.sembrada("P1_alta", "falla"),
                  f"{acept}/{malo}": flujo.sembrada("extra", "falla")}
        rc, salida = flujo.comprobar({}, cabeza, "Escenarios · P1", extra)
        err = flujo.errores(salida)
        problemas = []
        if rc == 0:
            problemas.append(f"el check pasó con {malo}, que no empieza por «P1_»")
        if not any(malo in l and "P1_" in l.replace(malo, "") for l in err):
            problemas.append(f"ningún error nombra a {malo} y dice que tiene que empezar por «P1_»")
        inf.escenario(f"El archivo de una prueba empieza por su pieza ({malo})", problemas, salida if problemas else "")

    # 1 bis · Control: «Escenarios · P1» con su archivo bien nombrado, que falla porque la pieza no existe, y el
    #         conftest.py de la carpeta, que no es de ninguna pieza, queda en verde
    extra, leer = flujo.marcas()
    cabeza = {f"{acept}/P1_alta.py": flujo.sembrada("P1_alta", "falla"), f"{acept}/conftest.py": "# lo que las pruebas comparten\n"}
    rc, salida = flujo.comprobar({}, cabeza, "Escenarios · P1", extra)
    problemas = ([] if "P1_alta" in {n for n, _ in leer()} else ["P1_alta.py no corrió"]) + flujo.verde(rc, salida)
    inf.escenario("Un pull request de escenarios bien nombrado queda en verde", problemas, salida if problemas else "")

    # 2 · Un título mal escrito no se cuela: la pieza tiene pruebas y el título no empieza por «<pieza> · »
    for pieza, titulo in (("P01", "P01: alta"), ("P07", "P07: alta"), ("P01", "P01 - alta")):
        extra, _ = flujo.marcas()
        base = {f"{acept}/{pieza}_alta.py": flujo.sembrada(f"{pieza}_alta", "falla")}
        rc, salida = flujo.comprobar(base, CODIGO, titulo, extra)
        err = flujo.errores(salida)
        problemas = []
        if rc == 0:
            problemas.append(f"el check pasó con el título «{titulo}»")
        if not any(f"{pieza} · " in l for l in err):
            problemas.append(f"ningún error dice que el título tiene que empezar «{pieza} · »")
        inf.escenario(f"Un título mal escrito no se cuela («{titulo}»)", problemas, salida if problemas else "")

    # 2 bis · Control: el mismo título mal escrito, de una pieza que no tiene pruebas, no falla por el título. P1 no
    #         tiene ningún archivo «P1_…»; sí los hay de P10 y uno de P01 que lleva «P1» en el nombre
    extra, _ = flujo.marcas()
    base = {f"{acept}/P10_baja.py": flujo.sembrada("P10_baja", "falla"),
            f"{acept}/P01_usa_P1.py": flujo.sembrada("P01_usa_P1", "falla")}
    rc, salida = flujo.comprobar(base, CODIGO, "P1: algo", extra)
    inf.escenario("Un título así, de una pieza sin pruebas, no falla por el título", flujo.verde(rc, salida),
                  salida if rc else "")

    # 2 ter · Control: el pull request de la pieza, bien titulado, que la añade a la lista y cuyas pruebas pasan
    extra, leer = flujo.marcas()
    base = {f"{acept}/P01_alta.py": flujo.sembrada("P01_alta", "pasa")}
    cabeza = dict(CODIGO)
    cabeza[activas] = "P01\n"
    rc, salida = flujo.comprobar(base, cabeza, "P01 · alta", extra)
    problemas = ([] if "P01_alta" in {n for n, _ in leer()} else ["P01_alta.py no corrió"]) + flujo.verde(rc, salida)
    inf.escenario("El pull request de la pieza, bien titulado, queda en verde", problemas, salida if problemas else "")


flujo.principal("P03", escenarios)
