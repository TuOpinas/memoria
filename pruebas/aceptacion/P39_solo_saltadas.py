#!/usr/bin/env python3
"""P39 · A control without holes (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-26, en el plan).

- Scenarios that only skip are not green. Dado a scenarios pull request where one file fails and another file of the
  same piece only skips or expects a failure, Cuando the control runs with pytest, with Vitest or with a runner of its
  own, Entonces it fails and says that not every test ran.

Contra la plantilla del workflow (pruebas-aceptacion.yml), con flujo.py, como P30: con pytest, con un Vitest de mentira
(un guion de node en node_modules/.bin/vitest que escribe un informe con la forma del de Vitest) y con un corredor
propio de pocas líneas. «Dice que no corrieron todas» se busca en las líneas de error con pocas palabras: «no corr»,
«sin correr» o «saltad», sin distinguir mayúsculas. Cómo se monta está en RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P39_solo_saltadas.py (0 pasa, 1 falla, 2 no se montó).
"""
import json, pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import flujo  # noqa: E402

TITULO = "Escenarios · P05"
CLAVES = ("no corr", "sin correr", "saltad")
CORREDOR_PROPIO = "scripts/corredor-aceptacion"
SUFIJO = "_test.go"

# lo que hace el segundo archivo de P05 con pytest: solo se salta o espera un fallo
SALTA = {
    "pytest.skip": ("import pytest\n\n\ndef test_por_hacer():\n    pytest.skip('por hacer')\n"),
    "pytest.importorskip": ("import pytest\n\npytest.importorskip('modulo_que_no_esta_p39')\n\n\n"
                            "def test_con_el_modulo():\n    assert False\n"),
    "xfail": ("import pytest\n\n\n@pytest.mark.xfail(reason='la pieza aún no existe')\n"
              "def test_esperada():\n    assert False\n"),
}


def vitest_falso(estados):
    """Un node_modules/.bin/vitest de mentira. estados: {ruta relativa: "passed" | "failed" | "skipped"}. Toma los
    archivos que le piden (los argumentos que no son opciones filtran por ruta; sin ninguno, todos) y escribe en
    --outputFile.json un informe con la forma del de Vitest: un archivo «skipped» trae solo una prueba «skipped»."""
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
            "  const e = ESTADOS[r]; if (e === 'failed') falla = true;\n"
            "  resultados.push({name: path.resolve(r), status: e, assertionResults: [{status: e, fullName: r + ' caso'}]});\n"
            "}\n"
            "fs.writeFileSync(salida, JSON.stringify({testResults: resultados}));\n"
            "process.exit(falla ? 1 : 0);\n")


def corredor_falso(estados):
    """Un corredor propio de pocas líneas. estados: {nombre del archivo sin SUFIJO: "PASA" | "FALLA" | "NO_CORRIO"}.
    Escribe una línea por archivo que recibe y sale con 0."""
    casos = "".join(f"    {n}) echo \"{e} $f\" ;;\n" for n, e in estados.items())
    return ("#!/usr/bin/env bash\n"
            "for f in \"$@\"; do\n"
            f"  n=$(basename \"$f\"); n=${{n%\"{SUFIJO}\"}}\n"
            "  case \"$n\" in\n" + casos +
            "    *) echo \"FALLA $f\" ;;\n"
            "  esac\n"
            "done\n"
            "exit 0\n")


def juzga(inf, titulo, rc, salida):
    problemas = []
    if rc == 0:
        problemas.append("el control quedó en verde con un archivo de P05 que solo se salta o espera un fallo")
    if not any(any(c in l.lower() for c in CLAVES) for l in flujo.errores(salida)):
        problemas.append("ningún error dice que no corrieron todas («" + "», «".join(CLAVES) + "»)")
    inf.escenario(f"Scenarios that only skip are not green ({titulo})", problemas, salida if problemas else "")


def escenarios(inf):
    acept, activas = flujo.plantilla_activas()
    base_pytest = {activas: "P01\n", f"{acept}/P01_alta.py": flujo.sembrada("P01_alta", "pasa")}

    # pytest: P05_falla.py falla; P05_salta.py solo se salta o espera un fallo, de tres maneras
    for como, texto in SALTA.items():
        extra, leer = flujo.marcas()
        cabeza = {f"{acept}/P05_falla.py": flujo.sembrada("P05_falla", "falla"), f"{acept}/P05_salta.py": texto}
        rc, salida = flujo.comprobar(base_pytest, cabeza, TITULO, extra, env_wf={"CORREDOR": "pytest"})
        if "P05_falla" not in {n for n, _ in leer()}:
            inf.escenario(f"Scenarios that only skip are not green (pytest, {como})",
                          ["P05_falla.py no llegó a correr: el caso no se montó como dice el escenario"], salida)
            continue
        juzga(inf, f"pytest, {como}", rc, salida)

    # Vitest: el informe da P05_falla como «failed» y P05_salta con su única prueba «skipped»
    config = f"{acept}/vitest.config.ts"
    bin_vitest = "node_modules/.bin/vitest"
    base = {activas: "P01\n", config: "export default {}\n", f"{acept}/P01_alta.test.ts": "test('caso', () => {})\n",
            bin_vitest: vitest_falso({f"{acept}/P01_alta.test.ts": "passed", f"{acept}/P05_falla.test.ts": "failed",
                                      f"{acept}/P05_salta.test.ts": "skipped"})}
    cabeza = {f"{acept}/P05_falla.test.ts": "test('caso', () => { throw new Error('falla') })\n",
              f"{acept}/P05_salta.test.ts": "test.skip('caso', () => {})\n"}
    extra, _ = flujo.marcas()
    rc, salida = flujo.comprobar(base, cabeza, TITULO, extra, env_wf={"CORREDOR": "vitest", "CONFIG": config},
                                 ejecutables=(bin_vitest,))
    juzga(inf, "Vitest, una prueba skipped", rc, salida)

    # un corredor propio: FALLA de P05_falla y NO_CORRIO de P05_salta, que se saltó
    base = {activas: "P01\n", f"{acept}/P01_alta{SUFIJO}": "// la corre el corredor propio\n",
            CORREDOR_PROPIO: corredor_falso({"P01_alta": "PASA", "P05_falla": "FALLA", "P05_salta": "NO_CORRIO"})}
    cabeza = {f"{acept}/P05_falla{SUFIJO}": "// falla\n", f"{acept}/P05_salta{SUFIJO}": "// se salta\n"}
    extra, _ = flujo.marcas()
    rc, salida = flujo.comprobar(base, cabeza, TITULO, extra,
                                 env_wf={"CORREDOR": "./" + CORREDOR_PROPIO, "SUFIJO": SUFIJO, "CONFIG": None},
                                 ejecutables=(CORREDOR_PROPIO,))
    juzga(inf, "corredor propio, NO_CORRIO del archivo saltado", rc, salida)


flujo.principal("P39", escenarios)
