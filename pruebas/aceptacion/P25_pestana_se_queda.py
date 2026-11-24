#!/usr/bin/env python3
"""P25 · The tab stays between projects (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-23, en el plan).

- Desarrollo stays open. Dado a development project open on its Desarrollo tab, Cuando another development project is
  chosen in the side menu, Entonces it opens on its Desarrollo tab.
- Without the tab, it falls back. Dado a development project open on its Desarrollo tab, Cuando a project that is not
  a development one is chosen, Entonces it opens on Estatus.

Por una función de la página: pestanaAlCambiar(abierta, destino), del bloque entre «// >>> pestaña» y «// <<< pestaña»
de vista.html, que se saca como texto y se corre con node como trazarDesarrollo en P21_lineas_que_se_siguen.py. abierta
es la pestaña del proyecto abierto; destino, el proyecto elegido (desarrollo: true si es de desarrollo, sin la clave si
no). Que el menú lateral la use al elegir un proyecto queda para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P25_pestana_se_queda.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P21_lineas_que_se_siguen import *  # noqa: E402,F401,F403  (cómo se saca y se corre un bloque de la página)

INICIO_P, FIN_P = "// >>> pestaña", "// <<< pestaña"


def pestana_al_cambiar(abierta, destino, problemas):
    return correr(INICIO_P, FIN_P, "pestanaAlCambiar", [abierta, destino], problemas)


def escenarios(inf):
    # 1 · Desarrollo se queda abierta: de «desarrollo» a otro proyecto de desarrollo, se abre en «desarrollo»
    problemas = []
    destino = {"id": "ventas--tienda", "nombre": "Tienda", "desarrollo": True}
    r = pestana_al_cambiar("desarrollo", destino, problemas)
    if not problemas:
        igual(problemas, "la pestaña con la que se abre otro proyecto de desarrollo", r, "desarrollo")
    inf.escenario("Desarrollo se queda abierta", problemas)

    # 2 · Sin la pestaña, vuelve a Estatus: de «desarrollo» a un proyecto sin la clave «desarrollo», se abre en «estatus»
    problemas = []
    destino = {"id": "ventas--campana", "nombre": "Campaña"}
    r = pestana_al_cambiar("desarrollo", destino, problemas)
    if not problemas:
        igual(problemas, "la pestaña con la que se abre un proyecto que no es de desarrollo", r, "estatus")
    inf.escenario("Sin la pestaña, vuelve a Estatus", problemas)


flujo.principal("P25", escenarios)
