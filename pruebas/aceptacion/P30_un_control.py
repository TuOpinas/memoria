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
- A project's own runner is part of the kit. Dado a repository with a runner of its own, Cuando a pull request that is
  not «Kit · » changes it, Entonces the control fails and names the runner; a «Kit · » pull request may change it.

Contra la plantilla del workflow (pruebas-aceptacion.yml), con flujo.py, como P01 a P03: el workflow entero sobre un
repositorio temporal con la base y la cabeza de un pull request. Contrato de la pieza: decisión
shared-memory/plugin-memoria#2026-11-25-5 y las enmiendas del encargo de F7. Cómo se monta cada escenario está en
RESUMEN.md. Lo que pide otro «CORREDOR» (vitest, un corredor propio, vacío) se monta con flujo.comprobar(env_wf=…,
ejecutables=…), que trae el pull request «Kit · » de flujo.py; sin él, la prueba sale con 2 (no se pudo montar).
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P30_un_control.py (0 pasa, 1 falla, 2 no se montó).
"""
import inspect, json, pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import flujo  # noqa: E402

CODIGO = {"app/main.py": "x = 2\n"}
CORREDOR_PROPIO = "scripts/corredor-aceptacion"   # se declara «CORREDOR: ./scripts/corredor-aceptacion»
SUFIJO = "_test.go"   # el final de los archivos de prueba con el corredor propio: ni .py ni .test.ts


def montar(arriba, base, cabeza, titulo, extra, ejecutables=()):
    """Corre el control con el «env:» de arriba cambiado (arriba: {"CORREDOR": …, "CONFIG": …}; "" lo deja vacío, None
    quita la clave), como lo deja un proyecto que montó el kit, y con esos archivos del repositorio ejecutables."""
    if "env_wf" not in inspect.signature(flujo.comprobar).parameters:
        raise flujo.Montaje("falta el cambio del kit: flujo.comprobar() no admite env_wf ni ejecutables, que trae el pull "
                            "request «Kit · » de flujo.py; sin él no se puede cambiar CORREDOR ni dejar ejecutable el "
                            "Vitest de mentira o el corredor propio")
    return flujo.comprobar(base, cabeza, titulo, extra, env_wf=arriba, ejecutables=ejecutables)


# ---------- lo que la prueba escribe: el Vitest de mentira y el corredor propio ----------
def vitest_falso(estados):
    """El texto de un node_modules/.bin/vitest de mentira. estados: {ruta relativa: "passed" | "failed" |
    "passed_con_saltada" | "sin_resultado"}. Toma los archivos que le piden (los argumentos que no son opciones filtran
    por ruta, como Vitest; sin ninguno, todos), deja una marca por cada uno en $MARCAS y escribe en --outputFile.json un
    informe con la forma del de Vitest. «passed_con_saltada» es un archivo «passed» con una prueba que pasa y otra
    «skipped»; los «sin_resultado» no salen en el informe."""
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
            "  const pruebas = e === 'passed_con_saltada'\n"
            "    ? [{status: 'passed', fullName: r + ' caso'}, {status: 'skipped', fullName: r + ' saltada'}]\n"
            "    : [{status: e, fullName: r + ' caso'}];\n"
            "  resultados.push({name: path.resolve(r), status: e === 'passed_con_saltada' ? 'passed' : e, "
            "assertionResults: pruebas});\n"
            "}\n"
            "fs.writeFileSync(salida, JSON.stringify({testResults: resultados}));\n"
            "process.exit(falla ? 1 : 0);\n")


def corredor_falso(estados, sale=0):
    """El texto de un corredor propio de pocas líneas. estados: {nombre del archivo sin SUFIJO: "PASA" | "FALLA" |
    "NO_CORRIO" | "sin_linea"}. Por cada archivo que recibe deja una marca y escribe su línea; escribe también líneas que
    no cuentan, y sale con «sale»."""
    casos = "".join(f"    {n}) echo \"{e} $f\" ;;\n" if e != "sin_linea" else f"    {n}) : ;;\n" for n, e in estados.items())
    return ("#!/usr/bin/env bash\n"
            "echo \"corredor de muestra: $# archivos\"   # no cuenta\n"
            "for f in \"$@\"; do\n"
            f"  n=$(basename \"$f\"); n=${{n%\"{SUFIJO}\"}}\n"
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


def rojo_y_dice(problemas, rc, salida, que, texto, minusculas=False):
    """Rojo, y una línea «::error::» contiene texto."""
    if rc == 0:
        problemas.append(f"el control pasó con {que}")
    err = flujo.errores(salida)
    if not any(texto in (l.lower() if minusculas else l) for l in err):
        problemas.append(f"ningún error del control dice «{texto}»")


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

    #     «Escenarios · H22a» con un archivo de H22b falla: un error nombra H22b_x.py y ninguno H22a_x.py, que es suyo
    extra, _ = flujo.marcas()
    cabeza = {f"{acept}/H22a_x.py": flujo.sembrada("H22a_x", "falla"),
              f"{acept}/H22b_x.py": flujo.sembrada("H22b_x", "falla")}
    rc, salida = flujo.comprobar({}, cabeza, "Escenarios · H22a", extra)
    problemas = []
    if rc == 0:
        problemas.append("el control pasó con H22b_x.py en «Escenarios · H22a»")
    if not any("H22b_x.py" in l for l in flujo.errores(salida)):
        problemas.append("ningún error nombra a H22b_x.py")
    nombran_suyo = [l for l in flujo.errores(salida) if "H22a_x.py" in l]
    if nombran_suyo:
        problemas.append(f"un error nombra a H22a_x.py, que es de H22a: {nombran_suyo[0][:160]}")
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

    # Lo que pide otro CORREDOR: con el arnés del pull request «Kit · »
    con_otro_corredor(inf, acept, activas)


def con_otro_corredor(inf, acept, activas):
    """Los casos con vitest, con un corredor propio y sin corredor."""
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

    propio = {"CORREDOR": "./" + CORREDOR_PROPIO, "SUFIJO": SUFIJO, "CONFIG": None}

    def con_propio(estados, sale=0, cabeza=None, titulo="P09 · otra cosa", activas_="P05\nP06\n", arriba=propio,
                   en_cabeza=()):
        """estados: los de corredor_falso. Los archivos de prueba van en la base, salvo los de «en_cabeza», que trae el
        pull request."""
        base = {activas: activas_, CORREDOR_PROPIO: corredor_falso(estados, sale)}
        cab = dict(cabeza if cabeza is not None else CODIGO)
        for n in estados:
            (cab if n in en_cabeza else base)[f"{acept}/{n}{SUFIJO}"] = "// la corre el corredor propio\n"
        extra, leer = flujo.marcas()
        rc, salida = montar(arriba, base, cab, titulo, extra, ejecutables=(CORREDOR_PROPIO,))
        return rc, salida, {n for n, _ in leer()}

    # 1 · Las mismas reglas con cualquiera de las dos (vitest): el mismo pull request de código, con P05 fallando
    problemas = []
    rc, salida, corrieron = con_vitest({"P05_alta": "failed", "P06_baja": "passed"})
    rojo_y_nombra(problemas, rc, salida, corrieron, "P05", "P06")
    inf.escenario("Las mismas reglas con cualquiera de las dos (vitest)", problemas, salida if problemas else "")

    #     Con vitest, un archivo «passed» con una prueba saltada no pasa (como con pytest): P05 activa da rojo
    problemas = []
    rc, salida, corrieron = con_vitest({"P05_alta": "passed_con_saltada", "P06_baja": "passed"})
    rojo_y_nombra(problemas, rc, salida, corrieron, "P05", "P06")
    inf.escenario("Las mismas reglas con cualquiera de las dos (vitest, P05 «passed» con una prueba saltada)", problemas,
                  salida if problemas else "")

    # 2 · El corredor propio de un proyecto: una prueba de P05 que falla da rojo y nombra a P05; todas en PASA, verde
    problemas = []
    rc, salida, corrieron = con_propio({"P05_alta": "FALLA", "P06_baja": "PASA"})
    rojo_y_nombra(problemas, rc, salida, corrieron, "P05", "P06")
    inf.escenario("El corredor propio de un proyecto (falla P05)", problemas, salida if problemas else "")

    rc, salida, corrieron = con_propio({"P05_alta": "PASA", "P06_baja": "PASA"})
    problemas = [f"no corrió {n}{SUFIJO}" for n in ("P05_alta", "P06_baja") if n not in corrieron] + flujo.verde(rc, salida)
    inf.escenario("El corredor propio de un proyecto (todas pasan)", problemas, salida if problemas else "")

    #     Las mismas reglas en el pull request de escenarios: «Escenarios · P05» que no añade P05 a la lista, verde si su
    #     prueba falla (FALLA) y rojo si pasa (PASA). P01 ya está activa y pasa
    for resultado, verde_ in (("FALLA", True), ("PASA", False)):
        rc, salida, corrieron = con_propio({"P01_alta": "PASA", "P05_alta": resultado}, cabeza={},
                                           titulo="Escenarios · P05", activas_="P01\n", en_cabeza=("P05_alta",))
        problemas = [] if "P05_alta" in corrieron else [f"P05_alta{SUFIJO} no corrió"]
        if verde_:
            problemas += flujo.verde(rc, salida)
        elif rc == 0:
            problemas.append("el control quedó en verde con la prueba de P05 que pasa y P05 fuera de la lista")
        inf.escenario(f"El corredor propio de un proyecto («Escenarios · P05» sin añadirla, su prueba dice {resultado}: "
                      f"{'verde' if verde_ else 'rojo'})", problemas, salida if problemas else "")

    #     Añadido: el corredor sale con otro código que 0: el control falla y dice que no se pudieron correr; y el
    #     corredor se llamó, para que no pase por otra cosa que falle antes
    rc, salida, corrieron = con_propio({"P05_alta": "PASA", "P06_baja": "PASA"}, sale=3)
    problemas = [] if corrieron else ["el corredor propio no se llamó: no hay marcas suyas"]
    rojo_y_dice(problemas, rc, salida, "el corredor saliendo con 3", "no se pudieron correr", minusculas=True)
    inf.escenario("El corredor propio de un proyecto (sale con 3)", problemas, salida if problemas else "")

    #     Con corredor propio y sin SUFIJO (sin declarar, o vacío): rojo, y un error dice «SUFIJO»
    problemas = []
    for que, valor in (("SUFIJO sin declarar", None), ("SUFIJO vacío", "")):
        rc, salida, _ = con_propio({"P05_alta": "PASA", "P06_baja": "PASA"}, arriba={**propio, "SUFIJO": valor})
        p = []
        rojo_y_dice(p, rc, salida, que, "SUFIJO")
        problemas += [f"{que}: {x}" for x in p]
    inf.escenario("El corredor propio de un proyecto (sin SUFIJO)", problemas, salida if problemas else "")

    # 3 · Un archivo que no se corrió cuenta como no corrido: el corredor propio no escribe línea para P05_alta, y el
    #     informe de Vitest no lo trae. Añadido: el corredor dice «NO_CORRIO» de él
    for que, (rc, salida, corrieron), archivo in (
            ("el corredor propio no escribe su línea", con_propio({"P05_alta": "sin_linea", "P06_baja": "PASA"}),
             f"P05_alta{SUFIJO}"),
            ("el corredor propio dice NO_CORRIO", con_propio({"P05_alta": "NO_CORRIO", "P06_baja": "PASA"}),
             f"P05_alta{SUFIJO}"),
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
        rojo_y_dice(problemas, rc, salida, que, palabra)
        inf.escenario(f"Sin corredor no hay control ({que})", problemas, salida if problemas else "")

    # 8 · El corredor propio es parte del kit: un pull request que no es «Kit · » y lo cambia falla y nombra el
    #     corredor, aunque todas las pruebas pasen; uno «Kit · …» que lo cambia queda en verde
    todas = {"P05_alta": "PASA", "P06_baja": "PASA"}
    cambio = {CORREDOR_PROPIO: corredor_falso(todas) + "# cambio\n", **CODIGO}
    rc, salida, _ = con_propio(todas, cabeza=cambio)
    problemas = [] if rc != 0 else ["el control pasó con un pull request «P09 · …» que cambia el corredor propio"]
    if not any(CORREDOR_PROPIO in l for l in flujo.errores(salida)):
        problemas.append(f"ningún error nombra el corredor ({CORREDOR_PROPIO})")
    inf.escenario("El corredor propio es parte del kit (un pull request que no es «Kit · » lo cambia: rojo)", problemas,
                  salida if problemas else "")

    rc, salida, _ = con_propio(todas, cabeza={CORREDOR_PROPIO: cambio[CORREDOR_PROPIO]},
                               titulo="Kit · el corredor de aceptación")
    problemas = flujo.verde(rc, salida)
    inf.escenario("El corredor propio es parte del kit (un pull request «Kit · …» lo cambia: verde)", problemas,
                  salida if problemas else "")


flujo.principal("P30", escenarios)
