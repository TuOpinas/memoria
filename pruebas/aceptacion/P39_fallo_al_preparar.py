#!/usr/bin/env python3
"""P39 · A control without holes (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-26, en el plan).

- A failure in preparation is not the piece missing. Dado a scenarios pull request whose test gives `ERROR` in a
  fixture, with pytest, Cuando the control runs, Entonces it fails and says that the preparation failed, and that what
  the piece does not have yet is imported inside the test.

Contra la plantilla del workflow (pruebas-aceptacion.yml), con flujo.py, como P30. La fixture importa lo que la pieza
aún no tiene, y eso lanza ModuleNotFoundError al preparar la prueba: pytest da «ERROR …::prueba». Lo que dice el error
se busca con pocas palabras, sin distinguir mayúsculas: una línea de error dice «prepar» (falló la preparación) y,
en la misma línea, «dentro» o «en la prueba» (se importa dentro de la prueba); y ninguna dice «no se pudo cargar», que
es el error de un archivo que no carga. Cómo se monta está en RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P39_fallo_al_preparar.py (0 pasa, 1 falla, 2 no se
montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import flujo  # noqa: E402

PRUEBA = ("import os\n\nimport pytest\n\n\n"
          "@pytest.fixture\n"
          "def pieza():\n"
          "    with open(os.environ['MARCAS'], 'a', encoding='utf-8') as f:\n"
          "        f.write('fixture ' + str(os.getpid()) + '\\n')\n"
          "    from app.pieza_que_aun_no_existe import lo_nuevo   # lo que la pieza aún no tiene, al preparar\n"
          "    return lo_nuevo\n\n\n"
          "def test_hace_lo_nuevo(pieza):\n"
          "    assert pieza() == 1\n")


def escenarios(inf):
    acept, activas = flujo.plantilla_activas()
    extra, leer = flujo.marcas()
    base = {activas: "P01\n", f"{acept}/P01_alta.py": flujo.sembrada("P01_alta", "pasa")}
    cabeza = {f"{acept}/P05_alta.py": PRUEBA}
    rc, salida = flujo.comprobar(base, cabeza, "Escenarios · P05", extra, env_wf={"CORREDOR": "pytest"})
    err = [l.lower() for l in flujo.errores(salida)]
    problemas = []
    if "fixture" not in {n for n, _ in leer()}:
        raise flujo.Montaje("la fixture de P05_alta.py no llegó a correr: el caso no se montó como dice el escenario")
    if rc == 0:
        problemas.append("el control quedó en verde con la prueba de P05 en ERROR al prepararla")
    if not any("prepar" in l for l in err):
        problemas.append("ningún error dice que falló la preparación («prepar»)")
    elif not any("prepar" in l and ("dentro" in l or "en la prueba" in l) for l in err):
        problemas.append("ninguna línea que dice «prepar» dice también «dentro» o «en la prueba» (dónde se importa)")
    if any("no se pudo cargar" in l for l in err):
        problemas.append("el error es el de un archivo que «no se pudo cargar», no el de una preparación que falla")
    inf.escenario("A failure in preparation is not the piece missing (ERROR en una fixture)", problemas,
                  salida if problemas else "")


flujo.principal("P39", escenarios)
