#!/usr/bin/env python3
"""Prueba el workflow de aceptación de este repositorio (.github/workflows/pruebas-aceptacion.yml), que es la plantilla del
kit adaptada a memoria y que las pruebas de aceptación de P01–P03 no cubren: ellas prueban la plantilla.

Corre el workflow entero, con el arnés de pruebas/aceptacion/flujo.py, sobre pull requests de mentira, y comprueba que
queda en verde o en rojo como dicen las decisiones shared-memory/plugin-memoria#2026-11-22-2, -3 y -9 y el CLAUDE.md. Cada
caso viene de la revisión de calidad del kit (revision-de-calidad-kit-aceptacion-memoria.md).

Uso, desde la raíz del repositorio: python3 pruebas/sesion/probar_aceptacion_memoria.py (0 todo bien, 1 algo falla, 2 no se
pudo montar: sin git, sin bash 4 o sin pytest en el python3 del PATH).
"""
import pathlib, sys

sys.dont_write_bytecode = True
RAIZ = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "pruebas" / "aceptacion"))
import flujo  # noqa: E402

WF = RAIZ / ".github" / "workflows" / "pruebas-aceptacion.yml"
flujo.YML = WF
A = "pruebas/aceptacion"
E = "pruebas/evals/escenarios"
L = ".github/piezas-activas.txt"
CORRER = (RAIZ / A / "correr.py").read_text(encoding="utf-8")
CODIGO = {"plugins/memoria/x.py": "x = 2\n"}


def prueba(resultado):
    """Un archivo de prueba mínimo para correr.py: pasa, falla o se salta, con su línea RESULTADO."""
    codigo = {"pasa": 0, "falla": 1, "saltada": 77}[resultado]
    return f"import sys\nprint('RESULTADO: {resultado}')\nsys.exit({codigo})\n"


BASE = {f"{A}/correr.py": CORRER}
# una prueba que pasa mientras el código diga «x = 1»: un pull request de código la puede romper
DEPENDE = ("import pathlib, sys\nok = pathlib.Path('plugins/memoria/x.py').read_text().strip() == 'x = 1'\n"
           "print('RESULTADO: ' + ('pasa' if ok else 'falla'))\nsys.exit(0 if ok else 1)\n")


def base(**extra):
    d = dict(BASE)
    d.update(extra)
    return d


def caso(nombre, base_, cabeza, titulo, espera, cuerpo="", autor="persona", mensaje=None, despues=None):
    """espera: «verde» o «rojo»; un caso rojo lleva el texto que tiene que estar en su error, para que no valga
    cualquier fallo."""
    try:
        rc, salida = flujo.comprobar(base_, cabeza, titulo, cuerpo=cuerpo, autor=autor, despues=despues)
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


def main():
    activa_pasa = base(**{L: "P05\n", f"{A}/P05_x.py": prueba("pasa")})
    activa_falla = base(**{L: "P05\n", f"{A}/P05_x.py": prueba("falla")})
    con_pruebas = base(**{f"{A}/P05_x.py": prueba("falla")})
    wf = WF.read_text(encoding="utf-8")
    r = [
        caso("Kit: el workflow y CLAUDE.md", base(), {"CLAUDE.md": "x\n", ".github/workflows/pruebas-aceptacion.yml": wf + "\n"}, "Kit · x", "verde"),
        caso("Kit con código", base(), {"CLAUDE.md": "x\n", **CODIGO}, "Kit · x", "rojo", mensaje="Kit · "),
        caso("Kit que no cambia el kit", base(), CODIGO, "Kit · x", "rojo", mensaje="no cambia nada del kit"),
        caso("correr.py en un pull request de escenarios", activa_pasa, {f"{A}/correr.py": CORRER + "\n"}, "Escenarios · P06", "rojo", mensaje="Kit · "),
        caso("Borrar correr.py con piezas activas, como kit", activa_falla, {f"{A}/correr.py": None}, "Kit · quitar", "rojo", mensaje="correr.py"),
        caso("Escenarios con código", base(), {f"{A}/P06_x.py": prueba("falla"), **CODIGO}, "Escenarios · P06", "rojo", mensaje="sin código"),
        caso("Escenarios de una pieza que no está en el título", activa_pasa, {f"{A}/P06_x.py": prueba("falla"), f"{A}/P07_x.py": prueba("falla")}, "Escenarios · P06", "rojo", mensaje="P07"),
        caso("Escenarios que reescriben una activa sin sacarla", activa_falla, {f"{A}/P05_x.py": prueba("pasa")}, "Escenarios · P05", "rojo", mensaje="activa"),
        caso("Escenarios que cambian una activa y la sacan", activa_pasa, {L: "", f"{A}/P05_x.py": prueba("falla")}, "Escenarios · P05", "verde"),
        caso("Escenarios que solo sacan una activa", activa_pasa, {L: ""}, "Escenarios · P05", "rojo", mensaje="quita P05"),
        caso("Un archivo suelto en la carpeta de aceptación", base(), {f"{A}/ayuda.py": "x = 1\n"}, "Escenarios · P06", "rojo", mensaje="solo van"),
        caso("Escenarios cuyas pruebas fallan", base(), {f"{A}/P06_x.py": prueba("falla")}, "Escenarios · P06", "verde"),
        caso("Escenarios cuyas pruebas ya pasan", base(), {f"{A}/P06_x.py": prueba("pasa")}, "Escenarios · P06", "rojo", mensaje="ya pasan"),
        caso("Escenarios cuyas pruebas solo se saltan", base(), {f"{A}/P06_x.py": prueba("saltada")}, "Escenarios · P06", "rojo", mensaje="saltarse"),
        caso("Escenarios de una pieza con eval, con su línea Evals:", base(), {f"{E}/30-P04-cita.md": "x\n"}, "Escenarios · P04", "verde", cuerpo="Evals: 30-P04-cita"),
        caso("Escenarios de una pieza con eval, sin la línea", base(), {f"{E}/30-P04-cita.md": "x\n"}, "Escenarios · P04", "rojo", mensaje="Evals: 30-P04-cita"),
        caso("Escenarios de una pieza sin pruebas", base(), {f"{A}/RESUMEN.md": "x\n"}, "Escenarios · P07", "rojo", mensaje="no tiene pruebas"),
        caso("Retirar los escenarios de una pieza", con_pruebas, {f"{A}/P05_x.py": None}, "Escenarios · P05", "verde"),
        caso("Revertir unos escenarios", con_pruebas, {f"{A}/P05_x.py": None}, 'Revert "Escenarios · P05 (#9)"', "verde"),
        caso("El arnés de evals con código", base(), {"pruebas/evals/correr.py": "x = 1\n", **CODIGO}, "P05 · 1.27.1", "verde"),
        caso("Un eval sin pieza con código", base(), {f"{E}/12-algo.md": "x\n", **CODIGO}, "1.27.1: algo", "verde"),
        caso("Versión que no añade su pieza con pruebas", con_pruebas, CODIGO, "P05 · 1.27.1", "rojo", mensaje="no está en"),
        caso("Versión que la añade y falla", con_pruebas, {L: "P05\n", **CODIGO}, "P05 · 1.27.1", "rojo", mensaje="no pasan"),
        caso("Versión que la añade y pasa", base(**{f"{A}/P05_x.py": prueba("pasa")}), {L: "P05\n", **CODIGO}, "P05 · 1.27.1", "verde"),
        caso("Versión con piezas sin pruebas en la carpeta (eval, técnica)", base(**{f"{A}/P05_x.py": prueba("pasa")}), {L: "P05\n", **CODIGO}, "P04 + P05 + P12 · 1.27.1", "verde"),
        caso("Título con la pieza mal escrita («P05: …»)", con_pruebas, CODIGO, "P05: 1.27.1", "rojo", mensaje="P01 · "),
        caso("Título con la pieza mal escrita («P05, P06 · …»)", con_pruebas, CODIGO, "P05, P06 · 1.27.1", "rojo", mensaje="no es un identificador"),
        caso("Quitar una activa en un pull request de código", activa_pasa, {L: "", **CODIGO}, "P09 · otra", "rojo", mensaje="quita P05"),
        caso("Llamarse reversión sin serlo", activa_falla, {L: "", **CODIGO}, 'Revert "P05 · algo que no existe"', "rojo", mensaje="quita P05"),
        caso("La lista borrada en un pull request de código", activa_falla, {L: None, **CODIGO}, "P09 · otra", "rojo", mensaje="quita P05"),
        caso("Activa que pasa, pull request de código", activa_pasa, CODIGO, "P09 · otra", "verde"),
        caso("Activa que falla, pull request de código", activa_falla, CODIGO, "P09 · otra", "rojo", mensaje="no pasan"),
        caso("Dependabot sube las acciones de dos workflows", activa_pasa, {".github/workflows/pruebas-aceptacion.yml": wf + "\n", ".github/workflows/pruebas.yml": "x\n"}, "Bump actions", "verde", autor="dependabot[bot]"),
        caso("Dependabot no salta las pruebas activas", activa_falla, {".github/workflows/pruebas.yml": "x\n"}, "Bump actions", "rojo", autor="dependabot[bot]", mensaje="no pasan"),
        caso("Un archivo de pruebas con acento, sin añadir la pieza", base(**{f"{A}/P05_migración.py": prueba("falla")}), CODIGO, "P05 · 1.27.1", "rojo", mensaje="no está en"),
        caso("Una rama atrasada rompe una pieza que main ya activó", base(**{"plugins/memoria/x.py": "x = 1\n", f"{A}/P05_x.py": DEPENDE}), CODIGO, "1.27.2: un arreglo", "rojo", mensaje="no pasan", despues={L: "P05\n"}),
        caso("Una rama atrasada respecto a main, sin tocar nada de eso", activa_pasa, CODIGO, "1.27.2: un arreglo", "verde", despues={"plugins/memoria/y.py": "y = 1\n"}),
        caso("Revertir una versión con el título de GitHub", base(), CODIGO, 'Revert "1.27.0: el kit de desarrollo (#83)"', "verde"),
        caso("Revertir un kit", base(), {"CLAUDE.md": "x\n"}, 'Revert "Kit · arreglos (#86)"', "verde"),
        caso("Revertir una reversión", base(), CODIGO, 'Revert "Revert "P05 · 1.27.1 (#90)" (#91)"', "verde"),
        caso("Revertir unos escenarios de una pieza activa", base(**{L: "", f"{A}/P05_x.py": prueba("falla")}), {L: "P05\n", f"{A}/P05_x.py": prueba("pasa")}, 'Revert "Escenarios · P05 (#9)"', "verde"),
        caso("Un título corriente que empieza por letras y cifras", base(), CODIGO, "Python3.9: arreglo de cerrar.py", "verde"),
        caso("Un eval con sus datos", base(), {f"{E}/30-P04-cita.md": "x\n", f"{E}/30-P04-cita.json": "{}\n"}, "Escenarios · P04", "verde", cuerpo="Evals: 30-P04-cita"),
        caso("La versión cambia los datos del eval de su pieza", base(**{f"{E}/30-P04-cita.json": "{}\n"}), {f"{E}/30-P04-cita.json": '{"x": 1}\n', **CODIGO}, "P04 · 1.27.2", "rojo", mensaje="sin código"),
        caso("Un eval sin pieza cuyo nombre parece una", base(), {f"{E}/31-oauth2-login.md": "x\n", **CODIGO}, "1.27.2: algo", "verde"),
        caso("«Evals: ninguno» que nombra el eval", base(), {f"{E}/30-P04-cita.md": "x\n"}, "Escenarios · P04", "rojo", cuerpo="Evals: ninguno (no corro 30-P04-cita)", mensaje="Evals: 30-P04-cita"),
        caso("El eval en una segunda línea Evals:", base(), {f"{E}/30-P04-cita.md": "x\n"}, "Escenarios · P04", "rojo", cuerpo="Evals:\nEvals: 30-P04-cita", mensaje="Evals: 30-P04-cita"),
        caso("Otro eval cuyo nombre empieza igual", base(), {f"{E}/30-P04-cita.md": "x\n"}, "Escenarios · P04", "rojo", cuerpo="Evals: 30-P04-cita-larga", mensaje="Evals: 30-P04-cita"),
        caso("Una línea mal escrita en la lista", base(**{f"{A}/P05_x.py": prueba("falla"), f"{A}/P06_x.py": prueba("falla")}), {L: "P05, P06\n", **CODIGO}, "1.27.1: dos piezas", "rojo", mensaje="no son un identificador"),
        caso("Corregir las pruebas de una activa que siguen pasando, sacándola", activa_pasa, {L: "", f"{A}/P05_x.py": prueba("pasa") + "# corregida\n"}, "Escenarios · P05", "rojo", mensaje="ya pasan"),
    ]
    print(f"{sum(r)} de {len(r)}")
    return 0 if all(r) else 1


if __name__ == "__main__":
    sys.exit(main())
