#!/usr/bin/env python3
"""P39 · A control without holes (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-26, en el plan).

- An async test pytest cannot run. Dado a scenarios pull request with an `async def` test and no async plugin, or with
  the plugin and without its mark, Cuando the control runs with pytest, Entonces it fails and says that the plugin or
  the mark is missing, not the piece.

Contra la plantilla del workflow (pruebas-aceptacion.yml), con flujo.py, como P30. El plugin async no se instala: en
CI solo está pytest (8.3.5), así que el «plugin» es uno de pocas líneas en el conftest.py de la carpeta, que corre con
asyncio las pruebas async que llevan su marca («asincrona») y deja pasar las demás, como hacen pytest-asyncio y anyio.
Lo que dice el error se busca con pocas palabras, sin distinguir mayúsculas: «plugin» o «marca». Cómo se monta está en
RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P39_async_sin_plugin.py (0 pasa, 1 falla, 2 no se
montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import flujo  # noqa: E402

CLAVES = ("plugin", "marca")

# el plugin async de mentira: corre con asyncio las pruebas async marcadas «asincrona»; las demás no las toca
PLUGIN = ("import asyncio, inspect\n\nimport pytest\n\n\n"
          "def pytest_configure(config):\n"
          "    config.addinivalue_line('markers', 'asincrona: corre la prueba async con asyncio')\n\n\n"
          "@pytest.hookimpl(tryfirst=True)\n"
          "def pytest_pyfunc_call(pyfuncitem):\n"
          "    if inspect.iscoroutinefunction(pyfuncitem.obj) and pyfuncitem.get_closest_marker('asincrona'):\n"
          "        args = {a: pyfuncitem.funcargs[a] for a in pyfuncitem._fixtureinfo.argnames}\n"
          "        asyncio.run(pyfuncitem.obj(**args))\n"
          "        return True\n")

# sin plugin: la prueba lleva la marca de pytest-asyncio, que no está
SIN_PLUGIN = ("import pytest\n\n\n"
              "@pytest.mark.asyncio\n"
              "async def test_hace_lo_nuevo():\n"
              "    from app.pieza_que_aun_no_existe import lo_nuevo\n"
              "    assert await lo_nuevo() == 1\n")

# con el plugin y sin su marca
SIN_MARCA = ("async def test_hace_lo_nuevo():\n"
             "    from app.pieza_que_aun_no_existe import lo_nuevo\n"
             "    assert await lo_nuevo() == 1\n")


def escenarios(inf):
    acept, activas = flujo.plantilla_activas()
    base = {activas: "P01\n", f"{acept}/P01_alta.py": flujo.sembrada("P01_alta", "pasa")}
    for que, cabeza in (("sin plugin async", {f"{acept}/P05_alta.py": SIN_PLUGIN}),
                        ("con el plugin y sin su marca", {f"{acept}/conftest.py": PLUGIN,
                                                          f"{acept}/P05_alta.py": SIN_MARCA})):
        extra, _ = flujo.marcas()
        rc, salida = flujo.comprobar(base, cabeza, "Escenarios · P05", extra, env_wf={"CORREDOR": "pytest"})
        problemas = []
        if "P05_alta.py" not in salida:
            problemas.append("pytest no llegó a P05_alta.py: el caso no se montó como dice el escenario")
        if rc == 0:
            problemas.append(f"el control quedó en verde con una prueba async {que}")
        if not any(any(c in l.lower() for c in CLAVES) for l in flujo.errores(salida)):
            problemas.append("ningún error dice que falta el plugin o la marca («" + "», «".join(CLAVES) + "»)")
        inf.escenario(f"An async test pytest cannot run ({que})", problemas, salida if problemas else "")


flujo.principal("P39", escenarios)
