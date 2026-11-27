#!/usr/bin/env python3
"""P39 · A control without holes (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-26, en el plan).

- What already passed still passes. Dado an active piece whose tests pass, with each of the three runners, Cuando a pull
  request of code runs the control, Entonces it is green.

Contra la plantilla del workflow (pruebas-aceptacion.yml), con flujo.py, como P30: con pytest, con un Vitest de mentira
(un guion de node en node_modules/.bin/vitest que escribe un informe con la forma del de Vitest) y con un corredor
propio de pocas líneas. Con pytest, además del caso simple, uno con lo que un proyecto de verdad pone en las pruebas
que pasan: una fixture del conftest.py, una prueba async con su plugin y su marca, y una parametrizada. Es un seguro:
lo que arregla P39 no puede poner en rojo pruebas que pasan. Cómo se monta está en RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P39_lo_que_ya_pasaba.py (0 pasa, 1 falla, 2 no se
montó).
"""
import json, pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import flujo  # noqa: E402

CODIGO = {"app/main.py": "x = 2\n"}
CORREDOR_PROPIO = "scripts/corredor-aceptacion"
SUFIJO = "_test.go"

# con pytest: un conftest.py con una fixture y un plugin async de pocas líneas (corre con asyncio las pruebas async
# marcadas «asincrona»), y pruebas que lo usan
CONFTEST = ("import asyncio, inspect\n\nimport pytest\n\n\n"
            "def pytest_configure(config):\n"
            "    config.addinivalue_line('markers', 'asincrona: corre la prueba async con asyncio')\n\n\n"
            "@pytest.hookimpl(tryfirst=True)\n"
            "def pytest_pyfunc_call(pyfuncitem):\n"
            "    if inspect.iscoroutinefunction(pyfuncitem.obj) and pyfuncitem.get_closest_marker('asincrona'):\n"
            "        args = {a: pyfuncitem.funcargs[a] for a in pyfuncitem._fixtureinfo.argnames}\n"
            "        asyncio.run(pyfuncitem.obj(**args))\n"
            "        return True\n\n\n"
            "@pytest.fixture\n"
            "def muestra():\n"
            "    return {'uno': 1}\n")
CON_FIXTURE = ("import os\n\nimport pytest\n\n\n"
               "def _marca(n):\n"
               "    with open(os.environ['MARCAS'], 'a', encoding='utf-8') as f:\n"
               "        f.write(n + ' ' + str(os.getpid()) + '\\n')\n\n\n"
               "def test_con_fixture(muestra):\n"
               "    _marca('fixture')\n"
               "    assert muestra['uno'] == 1\n\n\n"
               "@pytest.mark.asincrona\n"
               "async def test_async_con_su_marca(muestra):\n"
               "    _marca('async')\n"
               "    assert muestra['uno'] == 1\n\n\n"
               "@pytest.mark.parametrize('n', [1, 2])\n"
               "def test_parametrizada(n):\n"
               "    _marca('param' + str(n))\n"
               "    assert n > 0\n")


def vitest_falso(estados):
    """Un node_modules/.bin/vitest de mentira. estados: {ruta relativa: "passed" | "failed"}. Toma los archivos que le
    piden, deja una marca por cada uno en $MARCAS y escribe en --outputFile.json un informe con la forma del de Vitest."""
    return ("#!/usr/bin/env node\n"
            "const fs = require('fs'), path = require('path');\n"
            f"const ESTADOS = {json.dumps(estados)};\n"
            "const args = process.argv.slice(2); let salida = null; const filtros = [];\n"
            "for (let i = 0; i < args.length; i++) {\n"
            "  const a = args[i];\n"
            "  if (a.startsWith('--outputFile.json=')) salida = a.slice('--outputFile.json='.length);\n"
            "  else if (a === '--outputFile.json') salida = args[++i];\n"
            "  else if (['--config', '-c', '--reporter', '--root', '-r', '--dir'].includes(a)) i++;\n"
            "  else if (a.startsWith('-')) {}\n"
            "  else if (a === 'run' && filtros.length === 0 && i === 0) {}\n"
            "  else filtros.push(a.replace(/^\\.\\//, ''));\n"
            "}\n"
            "if (!salida) { console.error('vitest de mentira: falta --outputFile.json'); process.exit(2); }\n"
            "const tomados = Object.keys(ESTADOS).filter(r => !filtros.length || filtros.some(f => r.includes(f) || "
            "path.resolve(r).includes(f)));\n"
            "const resultados = []; let falla = false;\n"
            "for (const r of tomados) {\n"
            "  fs.appendFileSync(process.env.MARCAS, path.basename(r).replace(/\\.test\\.ts$/, '') + ' ' + process.pid + '\\n');\n"
            "  const e = ESTADOS[r]; if (e === 'failed') falla = true;\n"
            "  resultados.push({name: path.resolve(r), status: e, assertionResults: [{status: e, fullName: r + ' caso'}]});\n"
            "}\n"
            "fs.writeFileSync(salida, JSON.stringify({testResults: resultados}));\n"
            "process.exit(falla ? 1 : 0);\n")


def corredor_falso(estados):
    """Un corredor propio de pocas líneas: por cada archivo deja una marca y escribe su línea; sale con 0."""
    casos = "".join(f"    {n}) echo \"{e} $f\" ;;\n" for n, e in estados.items())
    return ("#!/usr/bin/env bash\n"
            "for f in \"$@\"; do\n"
            f"  n=$(basename \"$f\"); n=${{n%\"{SUFIJO}\"}}\n"
            "  echo \"$n $$\" >> \"$MARCAS\"\n"
            "  case \"$n\" in\n" + casos +
            "    *) echo \"FALLA $f\" ;;\n"
            "  esac\n"
            "done\n"
            "exit 0\n")


def juzga(inf, titulo, rc, salida, corrieron, esperadas):
    problemas = [f"no corrió {n}" for n in esperadas if n not in corrieron] + flujo.verde(rc, salida, "el control")
    inf.escenario(f"What already passed still passes ({titulo})", problemas, salida if problemas else "")


def escenarios(inf):
    acept, activas = flujo.plantilla_activas()

    # pytest, simple: P05 y P06 activas, sus pruebas pasan
    extra, leer = flujo.marcas()
    base = {activas: "P05\nP06\n",
            f"{acept}/P05_alta.py": flujo.sembrada("P05_alta", "pasa"),
            f"{acept}/P06_baja.py": flujo.sembrada("P06_baja", "pasa")}
    rc, salida = flujo.comprobar(base, CODIGO, "P09 · otra cosa", extra, env_wf={"CORREDOR": "pytest"})
    juzga(inf, "pytest", rc, salida, {n for n, _ in leer()}, ("P05_alta", "P06_baja"))

    # Añadido · pytest con fixture del conftest.py, async con su plugin y su marca, y parametrizada
    extra, leer = flujo.marcas()
    base = {activas: "P05\n", f"{acept}/conftest.py": CONFTEST, f"{acept}/P05_alta.py": CON_FIXTURE}
    rc, salida = flujo.comprobar(base, CODIGO, "P09 · otra cosa", extra, env_wf={"CORREDOR": "pytest"})
    juzga(inf, "pytest, con fixture, async con su plugin y su marca, y parametrizada", rc, salida,
          {n for n, _ in leer()}, ("fixture", "async", "param1", "param2"))

    # Vitest
    config = f"{acept}/vitest.config.ts"
    bin_vitest = "node_modules/.bin/vitest"
    base = {activas: "P05\nP06\n", config: "export default {}\n",
            bin_vitest: vitest_falso({f"{acept}/P05_alta.test.ts": "passed", f"{acept}/P06_baja.test.ts": "passed"})}
    for n in ("P05_alta", "P06_baja"):
        base[f"{acept}/{n}.test.ts"] = "import { test } from 'vitest'\ntest('caso', () => {})\n"
    extra, leer = flujo.marcas()
    rc, salida = flujo.comprobar(base, CODIGO, "P09 · otra cosa", extra, env_wf={"CORREDOR": "vitest", "CONFIG": config},
                                 ejecutables=(bin_vitest,))
    juzga(inf, "Vitest", rc, salida, {n for n, _ in leer()}, ("P05_alta", "P06_baja"))

    # un corredor propio
    base = {activas: "P05\nP06\n", CORREDOR_PROPIO: corredor_falso({"P05_alta": "PASA", "P06_baja": "PASA"})}
    for n in ("P05_alta", "P06_baja"):
        base[f"{acept}/{n}{SUFIJO}"] = "// la corre el corredor propio\n"
    extra, leer = flujo.marcas()
    rc, salida = flujo.comprobar(base, CODIGO, "P09 · otra cosa", extra,
                                 env_wf={"CORREDOR": "./" + CORREDOR_PROPIO, "SUFIJO": SUFIJO, "CONFIG": None},
                                 ejecutables=(CORREDOR_PROPIO,))
    juzga(inf, "corredor propio", rc, salida, {n for n, _ in leer()}, ("P05_alta", "P06_baja"))


flujo.principal("P39", escenarios)
