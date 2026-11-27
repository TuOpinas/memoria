#!/usr/bin/env python3
"""Prueba el control de aceptación de este repositorio (.github/workflows/pruebas-aceptacion.yml) y su corredor propio,
pruebas/aceptacion/correr.py. No es una prueba de una pieza: correr.py solo corre los archivos que empiezan por una pieza
y «_».

1. El control es la plantilla del kit (plugins/memoria/skills/desarrollo/plantillas/pruebas-aceptacion.yml) con lo que
   este repositorio rellena, y nada más: lo construye adaptar() y tiene que salir igual, línea por línea. Lo que la
   plantilla decide lo prueban probar_pruebas_aceptacion.py y las pruebas de aceptación de P01–P03 y P30.
2. Con correr.py como corredor propio, el control queda en verde o en rojo sobre pull requests de mentira, con el arnés
   de flujo.py.
3. correr.py, llamado con piezas como dice el CLAUDE.md, sale con 0, 1 o 2.

Uso, desde la raíz del repositorio: python3 pruebas/aceptacion/probar_control.py (0 todo bien, 1 algo falla, 2 no se
pudo montar: sin git o sin bash 4). Va en «Kit · » con el control: los dos están en la carpeta del kit o en él.
"""
import pathlib, subprocess, sys, tempfile

sys.dont_write_bytecode = True
AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
import flujo  # noqa: E402

WF = RAIZ / ".github" / "workflows" / "pruebas-aceptacion.yml"
PLANTILLA = RAIZ / "plugins" / "memoria" / "skills" / "desarrollo" / "plantillas" / "pruebas-aceptacion.yml"
A = "pruebas/aceptacion"
L = ".github/piezas-activas.txt"
CORRER = (AQUI / "correr.py").read_text(encoding="utf-8")
CODIGO = {"plugins/memoria/x.py": "x = 2\n"}

CABECERA = """# Las pruebas de aceptación de memoria: la plantilla del kit de desarrollo del plugin (1.31.1), con este repositorio en
# su «env:» y su entorno, y nada más; probar_control.py, junto al corredor, comprueba que es así. El corredor es propio,
# pruebas/aceptacion/correr.py, que corre cada script de prueba y responde por el contrato de abajo. Los evals no entran
# en este control: cuestan tokens y no siempre dan lo mismo, y corren con la etiqueta «evals» antes del sí
# (shared-memory/plugin-memoria#2026-11-22-3). Decisiones tecnologia/metodologia-desarrollo#2026-11-19-7 y
# shared-memory/plugin-memoria#2026-11-25-5.
"""
CAMBIOS = [
    ("  ACEPTACION: tests/aceptacion   ", "  ACEPTACION: pruebas/aceptacion "),
    ("  CORREDOR: pytest" + " " * 25, "  CORREDOR: ./pruebas/aceptacion/correr.py "),
    ('  SUFIJO: ""     ', '  SUFIJO: ".py"  '),
    ("      - name: Prepara el entorno\n        run: |\n          # lo rellena el repositorio: instalar lo que necesitan "
     "las pruebas (p. ej. pip install -r requirements.txt; con\n          # vitest, npm ci)\n          true\n",
     "      - uses: actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0  # v7.1.0\n"
     "        with:\n          python-version: '3.12'\n"
     "      - name: Prepara el entorno\n        run: |\n          # las de P01–P03 corren la plantilla del kit con pytest; las de P19–P21 y P25, node, que trae la imagen\n"
     "          python3 -I -m pip install -q pytest==8.3.5\n"),
]


def adaptar(plantilla):
    """La plantilla con lo que rellena este repositorio: su cabecera, el «env:» y el entorno."""
    lineas = plantilla.split("\n")
    if "#" not in lineas:
        raise SystemExit("La plantilla ya no separa su primer párrafo con una línea «#»: ponlo al día.")
    texto = CABECERA + "\n".join(lineas[lineas.index("#"):])   # su primer párrafo dice cómo se copia: va el nuestro
    for viejo, nuevo in CAMBIOS:
        if texto.count(viejo) != 1:
            raise SystemExit(f"La plantilla cambió y adaptar() ya no encuentra «{viejo.strip()[:60]}»: ponlo al día.")
        texto = texto.replace(viejo, nuevo)
    return texto


def prueba(resultado):
    """Un script de prueba mínimo para correr.py: pasa, falla, se salta o sale sin su línea RESULTADO."""
    if resultado == "rota":
        return "import sys\nsys.exit(0)\n"
    codigo = {"pasa": 0, "falla": 1, "saltada": 77}[resultado]
    return f"import sys\nprint('RESULTADO: {resultado}')\nsys.exit({codigo})\n"


def base(**extra):
    d = {f"{A}/correr.py": CORRER}
    d.update(extra)
    return d


def caso(nombre, base_, cabeza, titulo, espera, mensaje=None, autor="persona"):
    try:
        rc, salida = flujo.comprobar(base_, cabeza, titulo, autor=autor, ejecutables=[f"{A}/correr.py"])
    except flujo.Montaje as e:
        print(f"ERROR no se pudo montar: {e}")
        sys.exit(2)
    errores = flujo.errores(salida)
    bien = (rc == 0) == (espera == "verde") and (mensaje is None or any(mensaje in l for l in errores))
    print(("bien " if bien else "MAL  ") + f"{nombre} (esperaba {espera}, salió {rc})")
    if not bien:
        for l in (errores or salida.splitlines())[-4:]:
            print("        | " + l[:200])
    return bien


def por_piezas():
    """correr.py con piezas: 0 si pasan, 1 si fallan o se saltan, 2 si no se pudieron correr."""
    r = []
    for nombre, archivos, espera in [("pasa", {"P05_x.py": "pasa"}, 0), ("falla", {"P05_x.py": "falla"}, 1),
                                     ("se salta", {"P05_x.py": "saltada"}, 1), ("rota", {"P05_x.py": "rota"}, 2),
                                     ("sin archivos", {}, 2), ("H22a no toma H22", {"H22a_x.py": "pasa", "H22_x.py": "falla"}, 0)]:
        d = pathlib.Path(tempfile.mkdtemp()) / A
        d.mkdir(parents=True)
        (d / "correr.py").write_text(CORRER, encoding="utf-8")
        for f, que in archivos.items():
            (d / f).write_text(prueba(que), encoding="utf-8")
        pieza = "H22a" if "H22a_x.py" in archivos else "P05"
        rc = subprocess.run([sys.executable, "-I", str(d / "correr.py"), pieza], cwd=d.parents[1],
                            capture_output=True, text=True).returncode
        bien = rc == espera
        print(("bien " if bien else "MAL  ") + f"correr.py {pieza}: {nombre} (esperaba {espera}, salió {rc})")
        r.append(bien)
    return r


def main():
    esperado = adaptar(PLANTILLA.read_text(encoding="utf-8"))
    igual = WF.read_text(encoding="utf-8") == esperado
    print(("bien " if igual else "MAL  ") + "el control es la plantilla con lo de este repositorio"
          + ("" if igual else ": genéralo con «python3 pruebas/aceptacion/probar_control.py --escribe»"))
    flujo.YML = WF
    activa = lambda que, **x: base(**{L: "P05\n", f"{A}/P05_x.py": prueba(que)}, **x)
    wf = WF.read_text(encoding="utf-8")
    r = [igual,
         caso("Activa que pasa, pull request de código", activa("pasa"), CODIGO, "P09 · otra", "verde"),
         caso("Activa que falla", activa("falla"), CODIGO, "P09 · otra", "rojo", mensaje="P05"),
         caso("Activa que se salta", activa("saltada"), CODIGO, "P09 · otra", "rojo", mensaje="no corrió"),
         caso("Activa que sale sin su línea RESULTADO", activa("rota"), CODIGO, "P09 · otra", "rojo", mensaje="no corrió"),
         caso("Escenarios cuyas pruebas fallan", base(), {f"{A}/P06_x.py": prueba("falla")}, "Escenarios · P06", "verde"),
         caso("Escenarios cuyas pruebas ya pasan", base(), {f"{A}/P06_x.py": prueba("pasa")}, "Escenarios · P06", "rojo", mensaje="ya pasan"),
         caso("Escenarios cuyas pruebas solo se saltan", base(), {f"{A}/P06_x.py": prueba("saltada")}, "Escenarios · P06", "rojo", mensaje="no fallaron como pruebas"),
         caso("correr.py fuera de un «Kit · »", activa("pasa"), {f"{A}/correr.py": CORRER + "\n"}, "P09 · otra", "rojo", mensaje="correr.py"),
         caso("correr.py en un «Kit · »", activa("pasa"), {f"{A}/correr.py": CORRER + "\n"}, "Kit · corredor", "verde"),
         caso("Kit: el control, su prueba y CLAUDE.md", activa("pasa"),
              {WF.relative_to(RAIZ).as_posix(): wf + "\n", ".github/workflows/pruebas.yml": "x\n", "CLAUDE.md": "x\n",
               f"{A}/probar_control.py": "x = 1\n"}, "Kit · control", "verde"),
         caso("Kit con código", base(), {"CLAUDE.md": "x\n", **CODIGO}, "Kit · x", "rojo", mensaje="Kit · "),
         caso("Dependabot sube las acciones", activa("pasa"), {".github/workflows/pruebas.yml": "x\n"}, "Bump actions", "verde", autor="dependabot[bot]"),
         caso("Un eval sin pieza con código", base(), {"pruebas/evals/escenarios/12-algo.md": "x\n", **CODIGO}, "1.31.2: algo", "verde")]
    r += por_piezas()
    print(f"{sum(r)} de {len(r)}")
    return 0 if all(r) else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--escribe"]:
        WF.write_text(adaptar(PLANTILLA.read_text(encoding="utf-8")), encoding="utf-8")
        sys.exit(0)
    sys.exit(main())
