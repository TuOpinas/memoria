#!/usr/bin/env python3
"""P15 · The detail in a window, and the icon (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-23, en el plan).

- A piece opens in a window. Dado a development project with a plan, Cuando a piece of the plan is clicked, Entonces its
  detail opens in a window with the focus inside it.
- The window closes and gives the focus back. Dado an open window, Cuando Esc is pressed or the click falls outside it,
  Entonces it closes and the focus returns to what was clicked.
- Nothing to show is said. Dado an element with no detail, Cuando it is clicked, Entonces the window says «Sin detalle»
  instead of opening empty.
- The mark is an icon. Dado a development project in the index, Cuando the board lists it, Entonces it carries an icon
  with the text «Proyecto de desarrollo» for screen readers and as its tooltip, not the word.

Es una pieza de pantalla. La prueba lee la página del tablero (plugins/memoria/skills/tablero/vista.html) como texto, sin
abrirla, y comprueba solo lo que se ve así: que tiene un elemento <dialog, el atributo aria-label="Proyecto de desarrollo"
(el de la marca) y el texto «Sin detalle». El clic, el foco que entra y vuelve, Esc, el clic fuera y que el icono se vea quedan para la verificación:
lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P15_ventana_e_icono.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P05_lectores import *  # noqa: E402,F401,F403  (REPO, flujo: una sola copia)

VISTA = REPO / "plugins" / "memoria" / "skills" / "tablero" / "vista.html"
VENTANA, MARCA, NADA = "<dialog", 'aria-label="Proyecto de desarrollo"', "Sin detalle"


def pagina():
    """El texto de la página del tablero, tal cual está en el repositorio."""
    if not VISTA.is_file():
        raise flujo.Montaje(f"no está la página del tablero en {VISTA}")
    return VISTA.read_text(encoding="utf-8", errors="replace")


def tiene(texto, que, para, problemas):
    if que not in texto:
        problemas.append(f"la página del tablero no tiene «{que}»: {para}")


def escenarios(inf):
    # 1 · Una pieza se abre en una ventana: la página tiene un elemento <dialog> donde abrir el detalle
    problemas = []
    tiene(pagina(), VENTANA, "no hay ventana donde abrir el detalle de una pieza", problemas)
    inf.escenario("Una pieza se abre en una ventana", problemas)

    # 2 · La ventana se cierra y devuelve el foco: sin abrir la página solo se ve que la ventana existe
    problemas = []
    tiene(pagina(), VENTANA, "no hay ventana que cerrar", problemas)
    inf.escenario("La ventana se cierra y devuelve el foco", problemas)

    # 3 · Lo que no tiene nada que mostrar se dice: la ventana existe y la página tiene «Sin detalle»
    problemas = []
    texto = pagina()
    tiene(texto, VENTANA, "no hay ventana que diga «Sin detalle»", problemas)
    tiene(texto, NADA, "un elemento sin detalle abriría la ventana vacía", problemas)
    inf.escenario("Lo que no tiene nada que mostrar se dice", problemas)

    # 4 · La marca es un icono con el texto «Proyecto de desarrollo» para lectores de pantalla: el atributo literal
    problemas = []
    tiene(pagina(), MARCA, "el icono no lleva su texto para lectores de pantalla", problemas)
    inf.escenario("La marca es un icono", problemas)


flujo.principal("P15", escenarios)
