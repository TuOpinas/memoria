#!/usr/bin/env python3
"""P15 · The icon, always seen and explained, F5 (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-23, en el plan).

- The icon survives a long name. Dado a development project whose name does not fit the side menu, Cuando the menu
  lists it, Entonces the name is cut and the icon is still shown after it.
- The icon explains itself at once. Dado the icon in the side menu, in its area or beside the title, Cuando it is
  hovered, focused or tapped, Entonces the board's own tooltip shows «Proyecto de desarrollo».

Los cuatro escenarios de F4 siguen en P15_ventana_e_icono.py, sin cambios. Es de pantalla: la prueba lee la página del
tablero (plugins/memoria/skills/tablero/vista.html) como texto, sin abrirla, y comprueba solo lo que se ve así: el nombre
del menú lateral en un elemento class="side-nombre" con una regla CSS de .side-nombre que corta con text-overflow:ellipsis,
y el tooltip propio, data-tip="Proyecto de desarrollo", sin title="Proyecto de desarrollo". Que el icono se vea tras el
nombre cortado y que el tooltip salga al pasar, al enfocar o al tocar quedan para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P15_icono_siempre.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, re, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P05_lectores import *  # noqa: E402,F401,F403  (REPO, flujo: una sola copia)

VISTA = REPO / "plugins" / "memoria" / "skills" / "tablero" / "vista.html"
CLASE = 'class="side-nombre"'
REGLA = re.compile(r"\.side-nombre(?![\w-])[^{}]*\{[^}]*text-overflow\s*:\s*ellipsis")
TIP, TITULO = 'data-tip="Proyecto de desarrollo"', 'title="Proyecto de desarrollo"'


def pagina():
    """El texto de la página del tablero, tal cual está en el repositorio."""
    if not VISTA.is_file():
        raise flujo.Montaje(f"no está la página del tablero en {VISTA}")
    return VISTA.read_text(encoding="utf-8", errors="replace")


def escenarios(inf):
    # 1 · El icono sobrevive a un nombre largo: el nombre va en su propio elemento, que se corta con «…», y el icono fuera
    problemas = []
    texto = pagina()
    if CLASE not in texto:
        problemas.append(f"la página del tablero no tiene «{CLASE}»: el nombre del menú lateral no va en su propio elemento")
    if not REGLA.search(texto):
        problemas.append("la página del tablero no tiene una regla CSS de «.side-nombre» con «text-overflow:ellipsis»: "
                         "un nombre largo no se corta")
    inf.escenario("El icono sobrevive a un nombre largo", problemas)

    # 2 · El icono se explica al momento: el tooltip propio del tablero (data-tip), no el del navegador (title)
    problemas = []
    texto = pagina()
    if TIP not in texto:
        problemas.append(f"la página del tablero no tiene «{TIP}»: el icono no lleva el tooltip propio del tablero")
    if TITULO in texto:
        problemas.append(f"la página del tablero aún tiene «{TITULO}»: el tooltip del navegador tarda y no sale al tocar")
    inf.escenario("El icono se explica al momento", problemas)


flujo.principal("P15", escenarios)
