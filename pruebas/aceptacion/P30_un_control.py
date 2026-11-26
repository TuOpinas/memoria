#!/usr/bin/env python3
"""P30 · One control, a runner per project (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-25, en el plan).

- The same rules with either tool. Dado a repository whose configuration declares pytest, and another that declares
  Vitest, Cuando a pull request of code leaves a test of an active piece failing, Entonces in both the control fails and
  names the piece.
- A project's own runner. Dado a runner written by the project that answers by the contract, Cuando the control runs,
  Entonces it applies the same rules as with the kit's two.
- A file that was not run counts as not run. Dado a test file of an active piece that the tool does not run, Cuando the
  control runs, Entonces it fails and names the file.
- No runner, no control. Dado a repository with the control and no runner declared, or without the configuration its
  runner needs, Cuando the control runs, Entonces it fails and says what is missing.
- An identifier may end in a letter. Dado pieces H22, H22a and H22b, Cuando a pull request is titled «H22a · …»,
  Entonces the control takes H22a's tests and not the others'.
- A piece already built enters passing. Dado a scenarios pull request that adds its piece to the active list, Cuando
  the control runs, Entonces it is green only if those tests pass.
- A piece not built still has to fail. Dado a scenarios pull request that does not add its piece to the list, Cuando
  the control runs, Entonces it is green only if those tests fail as tests.

Contra la plantilla del workflow (pruebas-aceptacion.yml), con flujo.py, como P01 a P03: el workflow entero sobre un
repositorio temporal con la base y la cabeza de un pull request. Contrato de la pieza: decisión
shared-memory/plugin-memoria#2026-11-25-5. Cómo se monta cada escenario está en RESUMEN.md.

Lo que corre con pytest (el valor de la plantilla) se prueba primero. Lo que pide otro «CORREDOR» (vitest, un corredor
propio, vacío) está escrito al final, en con_otro_corredor(), y no se monta: flujo.py no deja cambiar el «env:» de
arriba del workflow ni dejar ejecutable un archivo del repositorio (ver montar()). Esa parte queda para un pull request
«Kit · »; hasta entonces este archivo sale con 2 después de juzgar lo de pytest.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P30_un_control.py (0 pasa, 1 falla, 2 no se montó).
"""
import json, pathlib, shutil, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import flujo  # noqa: E402

CODIGO = {"app/main.py": "x = 2\n"}
CORREDOR_PROPIO = "scripts/corredor-aceptacion"   # se declara «CORREDOR: ./scripts/corredor-aceptacion»
EXT_PROPIO = ".py"   # el contrato no dice cómo se llaman los archivos con un corredor propio: ver RESUMEN.md


# ---------- lo que flujo.py no deja montar ----------
NO_MONTA = ("flujo.py no deja montar este caso: comprobar() pone el «env:» de arriba de la plantilla después de «extra» "
            "(la línea «env.update({k: _expresiones(v, contexto) for k, v in env_wf.items()})»), así que CORREDOR y CONFIG "
            "no se pueden cambiar por caso, y los pasos salen de la plantilla, no del workflow del repositorio temporal; "
            "además _escribir() deja los archivos sin permiso de ejecución, y el Vitest de mentira "
            "(node_modules/.bin/vitest) y el corredor propio tienen que ser ejecutables. Queda para un pull request «Kit · »")


def montar(arriba, base, cabeza, titulo, extra, ejecutables=()):
    """Corre el control con el «env:» de arriba cambiado (arriba: {"CORREDOR": …, "CONFIG": …}, None quita la clave),
    como lo deja un proyecto que montó el kit, y con esos archivos del repositorio ejecutables. flujo.py no lo deja: no
    se monta (salida 2)."""
    raise flujo.Montaje(NO_MONTA)


# ---------- lo que la prueba escribe: el Vitest de mentira y el corredor propio ----------
def vitest_falso(estados):
    """El texto de un node_modules/.bin/vitest de mentira. estados: {ruta relativa: "passed" | "failed" | "sin_resultado"}.
    Toma los archivos que le piden (los argumentos que no son opciones filtran por ruta, como Vitest; sin ninguno, todos),
    deja una marca por cada uno en $MARCAS y escribe en --outputFile.json un informe con la forma del de Vitest; los
    «sin_resultado» no salen en el informe."""
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
            "  const e = ESTADOS[r]; if (e === 'sin_resultado') continue; if (e === 'failed') falla = true;\n"
            "  resultados.push({name: path.resolve(r), status: e, assertionResults: [{status: e, fullName: r + ' caso'}]});\n"
            "}\n"
            "fs.writeFileSync(salida, JSON.stringify({testResults: resultados}));\n"
            "process.exit(falla ? 1 : 0);\n")


def corredor_falso(estados, sale=0):
    """El texto de un corredor propio de pocas líneas. estados: {nombre del archivo sin extensión: "PASA" | "FALLA" |
    "NO_CORRIO" | "sin_linea"}. Por cada archivo que recibe deja una marca y escribe su línea; escribe también líneas que
    no cuentan, y sale con «sale»."""
    casos = "".join(f"    {n}) echo \"{e} $f\" ;;\n" if e != "sin_linea" else f"    {n}) : ;;\n" for n, e in estados.items())
    return ("#!/usr/bin/env bash\n"
            "echo \"corredor de muestra: $# archivos\"   # no cuenta\n"
            "for f in \"$@\"; do\n"
            "  n=$(basename \"$f\"); n=${n%.*}\n"
            "  echo \"$n $$\" >> \"$MARCAS\"\n"
            "  case \"$n\" in\n" + casos +
            "    *) echo \"FALLA $f\" ;;\n"
            "  esac\n"
            "  echo \"  (detalle de $n, que no cuenta)\"\n"
            "done\n"
            f"exit {sale}\n")


# ---------- comprobaciones comunes ----------
def rojo_y_nombra(problemas, rc, salida, corrieron, falla, pasa, que="el control"):
    err = flujo.errores(salida)
    if rc == 0:
        problemas.append(f"{que} pasó con la prueba de {falla} fallando")
    if falla not in {n.split("_")[0] for n in corrieron}:
        problemas.append(f"la prueba de {falla} no llegó a correr: el control no falla porque falle ella")
    if not flujo.nombra(err, falla):
        problemas.append(f"ningún error nombra a {falla}")
    if pasa and flujo.nombra(err, pasa):
        problemas.append(f"un error nombra a {pasa}, cuyas pruebas pasan")


def escenarios(inf):
    acept, activas = flujo.plantilla_activas()
    env_wf, _ = flujo.plantilla()

    # 1 · Las mismas reglas con cualquiera de las dos (pytest): la plantilla declara «CORREDOR: pytest», y un pull
    #     request de código con la prueba de P05 (activa) fallando da rojo y nombra a P05, no a P06, que pasa
    problemas = []
    if env_wf.get("CORREDOR") != "pytest":
        problemas.append(f"el «env:» de arriba de la plantilla no declara «CORREDOR: pytest» "
                         f"(CORREDOR = {json.dumps(env_wf.get('CORREDOR'))})")
    extra, leer = flujo.marcas()
    base = {activas: "P05\nP06\n",
            f"{acept}/P05_alta.py": flujo.sembrada("P05_alta", "falla"),
            f"{acept}/P06_baja.py": flujo.sembrada("P06_baja", "pasa")}
    rc, salida = flujo.comprobar(base, CODIGO, "P09 · otra cosa", extra)
    rojo_y_nombra(problemas, rc, salida, {n for n, _ in leer()}, "P05", "P06")
    inf.escenario("Las mismas reglas con cualquiera de las dos (pytest)", problemas, salida if problemas else "")

    # 5 · Un identificador puede acabar en letra: H22, H22a y H22b en la carpeta; solo H22a activa y su prueba pasa; las
    #     de las otras fallarían. «H22a · …» queda en verde y solo corre la de H22a
    extra, leer = flujo.marcas()
    base = {activas: "H22a\n",
            f"{acept}/H22_x.py": flujo.sembrada("H22_x", "falla"),
            f"{acept}/H22a_x.py": flujo.sembrada("H22a_x", "pasa"),
            f"{acept}/H22b_x.py": flujo.sembrada("H22b_x", "falla")}
    rc, salida = flujo.comprobar(base, CODIGO, "H22a · alta", extra)
    corrieron = {n for n, _ in leer()}
    problemas = [] if "H22a_x" in corrieron else ["H22a_x.py no corrió"]
    problemas += [f"{n}.py corrió: no es de H22a" for n in ("H22_x", "H22b_x") if n in corrieron]
    problemas += flujo.verde(rc, salida)
    inf.escenario("Un identificador puede acabar en letra («H22a · …» toma solo las de H22a)", problemas,
                  salida if problemas else "")

    #     Añadido: al revés, H22 activa y pasando, H22a y H22b fallarían: «H22 · …» toma solo la de H22
    extra, leer = flujo.marcas()
    base = {activas: "H22\n",
            f"{acept}/H22_x.py": flujo.sembrada("H22_x", "pasa"),
            f"{acept}/H22a_x.py": flujo.sembrada("H22a_x", "falla"),
            f"{acept}/H22b_x.py": flujo.sembrada("H22b_x", "falla")}
    rc, salida = flujo.comprobar(base, CODIGO, "H22 · alta", extra)
    corrieron = {n for n, _ in leer()}
    problemas = [] if "H22_x" in corrieron else ["H22_x.py no corrió"]
    problemas += [f"{n}.py corrió: no es de H22" for n in ("H22a_x", "H22b_x") if n in corrieron]
    problemas += flujo.verde(rc, salida)
    inf.escenario("Un identificador puede acabar en letra («H22 · …» no toma las de H22a ni H22b)", problemas,
                  salida if problemas else "")

    #     «Escenarios · H22a» con un archivo de H22b falla, y el error nombra el archivo
    extra, _ = flujo.marcas()
    cabeza = {f"{acept}/H22a_x.py": flujo.sembrada("H22a_x", "falla"),
              f"{acept}/H22b_x.py": flujo.sembrada("H22b_x", "falla")}
    rc, salida = flujo.comprobar({}, cabeza, "Escenarios · H22a", extra)
    problemas = []
    if rc == 0:
        problemas.append("el control pasó con H22b_x.py en «Escenarios · H22a»")
    if not any("H22b_x.py" in l for l in flujo.errores(salida)):
        problemas.append("ningún error nombra a H22b_x.py")
    inf.escenario("Un identificador puede acabar en letra («Escenarios · H22a» con un archivo de H22b)", problemas,
                  salida if problemas else "")

    #     Añadido: control, «Escenarios · H22a» con solo su archivo, que falla como debe, queda en verde
    extra, leer = flujo.marcas()
    cabeza = {f"{acept}/H22a_x.py": flujo.sembrada("H22a_x", "falla")}
    rc, salida = flujo.comprobar({}, cabeza, "Escenarios · H22a", extra)
    problemas = ([] if "H22a_x" in {n for n, _ in leer()} else ["H22a_x.py no corrió"]) + flujo.verde(rc, salida)
    inf.escenario("Un identificador puede acabar en letra («Escenarios · H22a» con solo lo suyo)", problemas,
                  salida if problemas else "")

    # 6 y 7 · «Escenarios · P05»: con P05 añadida a la lista en el mismo cambio, verde solo si sus pruebas pasan; sin
    #     añadirla, verde solo si fallan como pruebas. P01 ya está activa y pasa
    def escenarios_p05(anade, resultado):
        extra, leer = flujo.marcas()
        base = {activas: "P01\n", f"{acept}/P01_alta.py": flujo.sembrada("P01_alta", "pasa")}
        cabeza = {f"{acept}/P05_alta.py": flujo.sembrada("P05_alta", resultado)}
        if anade:
            cabeza[activas] = "P01\nP05\n"
        rc, salida = flujo.comprobar(base, cabeza, "Escenarios · P05", extra)
        problemas = [] if "P05_alta" in {n for n, _ in leer()} else ["P05_alta.py no corrió"]
        return rc, salida, problemas

    for anade, resultado, verde_ in ((True, "pasa", True), (True, "falla", False),
                                     (False, "falla", True), (False, "pasa", False)):
        rc, salida, problemas = escenarios_p05(anade, resultado)
        if verde_:
            problemas += flujo.verde(rc, salida)
        elif rc == 0:
            problemas.append(f"el control quedó en verde con la prueba de P05 que {resultado}"
                             + (" y P05 añadida a la lista" if anade else " y P05 fuera de la lista"))
        titulo = ("Una pieza ya construida entra pasando" if anade else "Una pieza sin construir tiene que fallar")
        caso = f"{'la añade' if anade else 'no la añade'} y su prueba {resultado}: {'verde' if verde_ else 'rojo'}"
        inf.escenario(f"{titulo} ({caso})", problemas, salida if problemas else "")

    # Lo que pide otro CORREDOR: no se monta (sale con 2, después de lo anterior)
    con_otro_corredor(inf, acept, activas)


def con_otro_corredor(inf, acept, activas):
    """Los casos con vitest, con un corredor propio y sin corredor. Escritos hasta donde se puede: montar() no se monta."""
    if not shutil.which("node"):
        raise flujo.Montaje("no hay node en el PATH: el Vitest de mentira es un guion de node")
    config = f"{acept}/vitest.config.ts"
    vitest = {"CORREDOR": "vitest", "CONFIG": config}
    bin_vitest = "node_modules/.bin/vitest"

    def con_vitest(estados, cabeza=None, titulo="P09 · otra cosa", arriba=vitest, sin_config=False):
        base = {activas: "P05\nP06\n", bin_vitest: vitest_falso({f"{acept}/{n}.test.ts": e for n, e in estados.items()})}
        if not sin_config:
            base[config] = "export default {}\n"
        for n in estados:
            base[f"{acept}/{n}.test.ts"] = "import { test } from 'vitest'\ntest('caso', () => {})\n"
        extra, leer = flujo.marcas()
        rc, salida = montar(arriba, base, cabeza or CODIGO, titulo, extra, ejecutables=(bin_vitest,))
        return rc, salida, {n for n, _ in leer()}

    propio = {"CORREDOR": "./" + CORREDOR_PROPIO, "CONFIG": None}

    def con_propio(estados, sale=0, cabeza=None, titulo="P09 · otra cosa"):
        base = {activas: "P05\nP06\n", CORREDOR_PROPIO: corredor_falso(estados, sale)}
        for n in estados:
            base[f"{acept}/{n}{EXT_PROPIO}"] = "# la corre el corredor propio\n"
        extra, leer = flujo.marcas()
        rc, salida = montar(propio, base, cabeza or CODIGO, titulo, extra, ejecutables=(CORREDOR_PROPIO,))
        return rc, salida, {n for n, _ in leer()}

    # 1 · Las mismas reglas con cualquiera de las dos (vitest): el mismo pull request de código, con P05 fallando
    problemas = []
    rc, salida, corrieron = con_vitest({"P05_alta": "failed", "P06_baja": "passed"})
    rojo_y_nombra(problemas, rc, salida, corrieron, "P05", "P06")
    inf.escenario("Las mismas reglas con cualquiera de las dos (vitest)", problemas, salida if problemas else "")

    # 2 · El corredor propio de un proyecto: una prueba de P05 que falla da rojo y nombra a P05; todas en PASA, verde
    problemas = []
    rc, salida, corrieron = con_propio({"P05_alta": "FALLA", "P06_baja": "PASA"})
    rojo_y_nombra(problemas, rc, salida, corrieron, "P05", "P06")
    inf.escenario("El corredor propio de un proyecto (falla P05)", problemas, salida if problemas else "")

    rc, salida, corrieron = con_propio({"P05_alta": "PASA", "P06_baja": "PASA"})
    problemas = [f"no corrió {n}" for n in ("P05_alta", "P06_baja") if n not in corrieron] + flujo.verde(rc, salida)
    inf.escenario("El corredor propio de un proyecto (todas pasan)", problemas, salida if problemas else "")

    #     Añadido: el corredor sale con otro código que 0: el control falla y dice que no se pudieron correr
    rc, salida, _ = con_propio({"P05_alta": "PASA", "P06_baja": "PASA"}, sale=3)
    problemas = []
    if rc == 0:
        problemas.append("el control pasó con el corredor saliendo con 3")
    if not any("no se pudieron correr" in l.lower() for l in flujo.errores(salida)):
        problemas.append("ningún error dice que las pruebas no se pudieron correr")
    inf.escenario("El corredor propio de un proyecto (sale con 3)", problemas, salida if problemas else "")

    # 3 · Un archivo que no se corrió cuenta como no corrido: el corredor propio no escribe línea para P05_alta, y el
    #     informe de Vitest no lo trae. Añadido: el corredor dice «NO_CORRIO» de él
    for que, (rc, salida, corrieron), archivo in (
            ("el corredor propio no escribe su línea", con_propio({"P05_alta": "sin_linea", "P06_baja": "PASA"}),
             f"P05_alta{EXT_PROPIO}"),
            ("el corredor propio dice NO_CORRIO", con_propio({"P05_alta": "NO_CORRIO", "P06_baja": "PASA"}),
             f"P05_alta{EXT_PROPIO}"),
            ("el informe de Vitest no lo trae", con_vitest({"P05_alta": "sin_resultado", "P06_baja": "passed"}),
             "P05_alta.test.ts")):
        problemas = []
        if rc == 0:
            problemas.append(f"el control pasó sin resultado de {archivo}")
        if not any(archivo in l for l in flujo.errores(salida)):
            problemas.append(f"ningún error nombra a {archivo}")
        inf.escenario(f"Un archivo que no se corrió cuenta como no corrido ({que})", problemas, salida if problemas else "")

    # 4 · Sin corredor no hay control: CORREDOR vacío (y, añadido, con otra palabra), y vitest sin el archivo de CONFIG
    for que, arriba, sin_config, palabra in (("CORREDOR vacío", {"CORREDOR": "", "CONFIG": None}, False, "CORREDOR"),
                                             ("CORREDOR con otra palabra", {"CORREDOR": "jest", "CONFIG": None}, False,
                                              "CORREDOR"),
                                             ("vitest sin el archivo de CONFIG", vitest, True, "CONFIG")):
        rc, salida, _ = con_vitest({"P05_alta": "passed", "P06_baja": "passed"}, arriba=arriba, sin_config=sin_config)
        problemas = []
        if rc == 0:
            problemas.append(f"el control pasó con {que}")
        if palabra not in salida:
            problemas.append(f"la salida del control no dice «{palabra}»")
        inf.escenario(f"Sin corredor no hay control ({que})", problemas, salida if problemas else "")

    # Añadido (más allá de los escenarios): el corredor propio es del kit; un pull request que no es «Kit · » y lo
    # cambia falla, aunque todas las pruebas pasen
    rc, salida, _ = con_propio({"P05_alta": "PASA", "P06_baja": "PASA"},
                               cabeza={CORREDOR_PROPIO: corredor_falso({"P05_alta": "PASA", "P06_baja": "PASA"})
                                       + "# cambio\n", **CODIGO})
    problemas = [] if rc != 0 else ["el control pasó con un pull request «P09 · …» que cambia el corredor propio"]
    inf.escenario("El corredor propio es del kit (un pull request que no es «Kit · » lo cambia)", problemas,
                  salida if problemas else "")


flujo.principal("P30", escenarios)
