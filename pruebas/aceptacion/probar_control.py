#!/usr/bin/env python3
"""Prueba el control de aceptación de este repositorio (.github/workflows/pruebas-aceptacion.yml) y su corredor propio,
pruebas/aceptacion/correr.py. No es una prueba de una pieza: correr.py solo corre los archivos que empiezan por una pieza
y «_».

1. El control es la plantilla del kit (plugins/memoria/skills/desarrollo/plantillas/pruebas-aceptacion.yml) con lo que
   este repositorio rellena, y nada más: lo construye adaptar() y tiene que salir igual, línea por línea, sin contar el
   commit al que va fijada cada acción, que sube Dependabot en el workflow y no en la plantilla. Su cabecera lleva la
   huella de la plantilla de la que salió: si la plantilla cambió después (una versión que la cambia va antes que el
   «Kit · » que regenera el control, porque el control no deja juntar un workflow con código), lo dice y no falla; si
   no cambió y el control no sale igual, alguien lo tocó a mano, y falla. Lo que la plantilla decide lo prueban
   probar_pruebas_aceptacion.py y las pruebas de aceptación de P01–P03 y P30.
2. Con correr.py como corredor propio, el control queda en verde o en rojo sobre pull requests de mentira, con el arnés
   de flujo.py.
3. correr.py, llamado con piezas como dice el CLAUDE.md, sale con 0, 1 o 2.

Uso, desde la raíz del repositorio: python3 pruebas/aceptacion/probar_control.py (0 todo bien, 1 algo falla, 2 no se
pudo montar: sin git o sin bash 4). Va en «Kit · » con el control: los dos están en la carpeta del kit o en él.
"""
import hashlib, pathlib, re, subprocess, sys, tempfile

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

CABECERA = """# Las pruebas de aceptación de memoria: la plantilla del kit de desarrollo del plugin, con este repositorio en su
# «env:» y su entorno, y nada más; probar_control.py, junto al corredor, comprueba que es así. El corredor es propio,
# pruebas/aceptacion/correr.py, que corre cada script de prueba y responde por el contrato de abajo. Los evals no entran
# en este control: cuestan tokens y no siempre dan lo mismo, y corren con la etiqueta «evals» antes del sí
# (shared-memory/plugin-memoria#2026-11-22-3). Decisiones tecnologia/metodologia-desarrollo#2026-11-19-7 y
# shared-memory/plugin-memoria#2026-11-25-5. Plantilla: {huella}
"""
CAMBIOS = [
    ("  ACEPTACION: tests/aceptacion   ", "  ACEPTACION: pruebas/aceptacion "),
    ("  CORREDOR: pytest" + " " * 25, "  CORREDOR: ./pruebas/aceptacion/correr.py "),
    ('  SUFIJO: ""     ', '  SUFIJO: ".py"  '),
    ("      - name: Prepara el entorno\n        run: |\n          # lo rellena el repositorio: instalar lo que necesitan "
     "las pruebas (p. ej. pip install -r requirements.txt; con\n          # vitest, npm ci)\n          true\n",
     "      - uses: actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0  # v7.1.0\n"
     "        with:\n          python-version: '3.12'\n"
     "      - name: Prepara el entorno\n        run: |\n          # pytest para P01–P03 y P30, que corren la plantilla del kit; node, que trae la imagen, para P19–P21, P25, P27, P28 y P30\n"
     "          python3 -I -m pip install -q pytest==8.3.5\n"),
]


def cuerpo(plantilla):
    """La plantilla sin su primer párrafo, que dice cómo se copia: lo que el control lleva de ella."""
    lineas = plantilla.split("\n")
    if "#" not in lineas:
        raise ValueError("la plantilla ya no separa su primer párrafo con una línea «#»: pon al día adaptar()")
    return "\n".join(lineas[lineas.index("#"):])


def huella(texto):
    """La huella del cuerpo de una plantilla, sin los commits de sus acciones."""
    return hashlib.sha256(sin_commits(texto).encode("utf-8")).hexdigest()[:12]


def sin_commits(texto):
    """Cada «uses: acción@commit  # vX» sin el commit ni la versión: los sube Dependabot en el workflow."""
    return re.sub(r"(uses: [^@\s]+)@[0-9a-f]{40}(\s+#.*)?", r"\1@…", texto)


def adaptar(plantilla):
    """La plantilla con lo que rellena este repositorio: su cabecera, con la huella de la plantilla, el «env:» y el
    entorno."""
    texto = CABECERA.format(huella=huella(cuerpo(plantilla))) + cuerpo(plantilla)   # su primer párrafo dice cómo se copia: va el nuestro
    for viejo, nuevo in CAMBIOS:
        if texto.count(viejo) != 1:
            raise ValueError(f"adaptar() ya no encuentra «{viejo.strip()[:60]}» en la plantilla: ponlo al día")
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
                                     ("sin archivos", {}, 2), ("H22a no toma H22", {"H22a_x.py": "pasa", "H22_x.py": "falla"}, 0),
                                     ("p05_y.py también es de P05", {"P05_x.py": "pasa", "p05_y.py": "falla"}, 1)]:
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


def desadaptar(control):
    """Lo que el control dice que tomó de la plantilla: sin su cabecera y con lo de este repositorio deshecho."""
    m = re.search(r"Plantilla: ([0-9a-f]{12})\n", control)
    fin = CABECERA.split("{huella}")[1]
    if not m or not control.startswith(CABECERA.split("{huella}")[0]) or not control[m.end() - 1:].startswith(fin):
        return None, ""
    texto = sin_commits(control[m.end() - 1 + len(fin):])
    for viejo, nuevo in CAMBIOS:
        viejo, nuevo = sin_commits(viejo), sin_commits(nuevo)
        if texto.count(nuevo) != 1:
            return None, ""
        texto = texto.replace(nuevo, viejo)
    return m.group(1), texto


def comparar(plantilla, control, nombre, decir=print):
    """True si el control es la plantilla adaptada, o la adaptada de una plantilla anterior que su huella nombra."""
    try:
        esperado = adaptar(plantilla)
    except ValueError:
        esperado = None   # la plantilla cambió lo que adaptar() rellena: el control se mira contra su propia huella
    if esperado is not None and sin_commits(control) == sin_commits(esperado):
        decir(f"bien {nombre} es la plantilla con lo de este repositorio")
        return True
    dice, tomado = desadaptar(control)
    if dice and dice == huella(tomado) and dice != huella(cuerpo(plantilla)):
        decir(f"::warning::{nombre} va detrás de la plantilla: regenéralo en un «Kit · » justo después de esta versión")
        decir(f"bien {nombre} va detrás de la plantilla, que cambió después: regenéralo en un «Kit · » con "
              "«python3 pruebas/aceptacion/probar_control.py --escribe»")
        return True
    decir(f"MAL  {nombre} no es la plantilla con lo de este repositorio: no se cambia a mano; genéralo con "
          "«python3 pruebas/aceptacion/probar_control.py --escribe»")
    return False


def huella_y_commits():
    """Un «Bump …» y una plantilla nueva pasan; un cambio a mano, no."""
    plantilla = PLANTILLA.read_text(encoding="utf-8")
    control = adaptar(plantilla)
    nueva = plantilla + "# una línea nueva de la plantilla\n"
    a_mano = control + "# una línea escrita a mano\n"
    otra = re.search(r"Plantilla: ([0-9a-f]{12})", control).group(1)
    sin_anclas = plantilla.replace("  ACEPTACION: tests/aceptacion", "  ACEPTACION: tests/acceptance")
    uses = re.search(r"uses: [^@\s]+@[0-9a-f]{40}", control)
    if not uses:
        raise SystemExit("El control ya no tiene acciones fijadas por commit: pon al día huella_y_commits().")
    casos = [("un «Bump …» del commit de una acción", plantilla, re.sub(r"(uses: [^@\s]+@)[0-9a-f]{40}", r"\g<1>" + "0" * 40, control, count=1), True),
             ("una plantilla nueva que cambia lo que se rellena", sin_anclas, control, True),
             ("una plantilla nueva antes de regenerar", nueva, control, True),
             ("un cambio a mano", plantilla, a_mano, False),
             ("un cambio a mano con otra huella", plantilla, a_mano.replace(otra, "0" * 12), False),
             ("una acción sin fijar a un commit", plantilla, re.sub(r"(uses: [^@\s]+@)[0-9a-f]{40}", r"\g<1>main", control, count=1), False)]
    r = []
    for nombre, p, c, espera in casos:
        bien = comparar(p, c, nombre, decir=lambda _: None) == espera
        print(("bien " if bien else "MAL  ") + f"{nombre}: {'pasa' if espera else 'falla'}")
        r.append(bien)
    return r


def main():
    igual = comparar(PLANTILLA.read_text(encoding="utf-8"), WF.read_text(encoding="utf-8"), "el control")
    flujo.YML = WF
    activa = lambda que, **x: base(**{L: "P05\n", f"{A}/P05_x.py": prueba(que)}, **x)
    r = [igual,
         caso("Activa que pasa, pull request de código", activa("pasa"), CODIGO, "P09 · otra", "verde"),
         caso("Activa que falla", activa("falla"), CODIGO, "P09 · otra", "rojo", mensaje="P05"),
         caso("Activa que se salta", activa("saltada"), CODIGO, "P09 · otra", "rojo", mensaje="no corrió"),
         caso("Activa que sale sin su línea RESULTADO", activa("rota"), CODIGO, "P09 · otra", "rojo", mensaje="no corrió"),
         caso("Escenarios cuyas pruebas fallan", base(), {f"{A}/P06_x.py": prueba("falla")}, "Escenarios · P06", "verde"),
         caso("Escenarios cuyas pruebas ya pasan", base(), {f"{A}/P06_x.py": prueba("pasa")}, "Escenarios · P06", "rojo", mensaje="ya pasan"),
         caso("Escenarios cuyas pruebas solo se saltan", base(), {f"{A}/P06_x.py": prueba("saltada")}, "Escenarios · P06", "rojo", mensaje="no fallaron como pruebas")]
    r += huella_y_commits()
    r += por_piezas()
    print(f"{sum(r)} de {len(r)}")
    return 0 if all(r) else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--escribe"]:
        nuevo = adaptar(PLANTILLA.read_text(encoding="utf-8"))
        # los commits que Dependabot ya subió en el control se quedan: la plantilla no los sigue
        fijados = dict(re.findall(r"uses: ([^@\s]+)(@[0-9a-f]{40}(?:\s+#.*)?)", WF.read_text(encoding="utf-8"))) if WF.exists() else {}
        nuevo = re.sub(r"uses: ([^@\s]+)@[0-9a-f]{40}(\s+#.*)?", lambda m: "uses: " + m.group(1) + fijados.get(m.group(1), m.group(0)[len("uses: " + m.group(1)):]), nuevo)
        WF.write_text(nuevo, encoding="utf-8")
        sys.exit(0)
    sys.exit(main())
