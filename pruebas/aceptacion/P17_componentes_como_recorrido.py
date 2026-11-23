#!/usr/bin/env python3
"""P17 · Components as a route (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-23, en el plan).

- The route is a row of arrows. Dado «Componentes» with a line «Flujo: A → B → C», Cuando the components open, Entonces
  A, B and C are drawn in a row with arrows in that order.
- External is told apart without colour alone. Dado a component marked «Externo: sí», Cuando the components open,
  Entonces it is drawn apart from the own ones by more than its colour.
- A connection to something unknown is said. Dado a «Conecta con» that names a component the table does not have,
  Cuando the components open, Entonces the rest is drawn and the tab names it.

Por la entrada de F2: el generador del tablero sobre la raíz de muestra de P05_lectores.py, y lo que escribe en
desarrollo/ventas--portal.json: diseno.componentes[].externo y diseno.componentes_flujo (o null sin línea «Flujo:»). El
dibujo (la fila, las flechas, cómo se distingue lo externo además del color) queda para la verificación: lo dice
RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P17_componentes_como_recorrido.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P05_lectores import *  # noqa: E402,F401,F403  (la muestra, cómo se corre el generador y lo que dice la muestra: una sola copia)

FIN_COMPONENTES = "\n\n## Datos\n"   # lo que sigue a la tabla de «Componentes»
FLUJO_DATOS = (DISENO, "\n\nDetalle: ventas/portal/entregables/datos-detalle.md",
               "\n\n**Flujo:** cliente → pedido → producto\n\nDetalle: ventas/portal/entregables/datos-detalle.md")
EXTERNOS = {"Tienda web": False, "API": False, "Motor de pagos": True, "Panel interno": False}


def con_flujo(linea):
    """El cambio que pone la línea «Flujo:» en «Componentes», debajo de la tabla."""
    return (DISENO, FIN_COMPONENTES, "\n\n" + linea + FIN_COMPONENTES)


def con_externo(panel_conecta="API · Motor de pagos"):
    """Los cambios que añaden la columna «Externo» a «Componentes»: «sí» en «Motor de pagos», vacía en los demás."""
    return [(DISENO, "| Componente | Qué hace | Dónde vive | Conecta con |\n|---|---|---|---|",
             "| Componente | Qué hace | Dónde vive | Externo | Conecta con |\n|---|---|---|---|---|"),
            (DISENO, "| muestra/portal:web | API |", "| muestra/portal:web | | API |"),
            (DISENO, "| muestra/portal:api | Motor de pagos |", "| muestra/portal:api | | Motor de pagos |"),
            (DISENO, "| muestra/portal:pagos | |", "| muestra/portal:pagos | sí | |"),
            (DISENO, "| muestra/portal:panel | API · Motor de pagos |", f"| muestra/portal:panel | | {panel_conecta} |")]


def cajas(d, problemas):
    """Las cuatro cajas de «Componentes», con lo que conecta cada una y si es externa."""
    vistas = por_clave(saca(d, "diseno", "componentes"), "nombre")
    igual(problemas, "las cajas de los componentes", sorted(vistas), sorted(COMPONENTES))
    for nombre, conecta in COMPONENTES.items():
        igual(problemas, f"«Conecta con» de «{nombre}»", saca(vistas, nombre, "conecta_con"), conecta)
        igual(problemas, f"«externo» de «{nombre}»", saca(vistas, nombre, "externo"), EXTERNOS[nombre])


def recorrido(d, problemas, esperado):
    dis = saca(d, "diseno")
    if not isinstance(dis, dict) or "componentes_flujo" not in dis:
        problemas.append("«diseno» no trae «componentes_flujo»")
    else:
        igual(problemas, "«componentes_flujo»", dis["componentes_flujo"], esperado)


def escenarios(inf):
    # 1 · El recorrido es una fila de flechas: «Flujo: Tienda web → API → Motor de pagos». «Datos» tiene su propia
    #     línea «Flujo:», que no es la de los componentes
    problemas = []
    d = pestana(*generar(con_externo() + [con_flujo("**Flujo:** Tienda web → API → Motor de pagos"), FLUJO_DATOS]), problemas)
    if d is not None:
        recorrido(d, problemas, ["Tienda web", "API", "Motor de pagos"])
        cajas(d, problemas)
    inf.escenario("El recorrido es una fila de flechas", problemas)

    # 2 · Lo externo se distingue: «Motor de pagos» lleva «sí» en «Externo»; los demás, la celda vacía. Sin línea
    #     «Flujo:» en «Componentes», no hay recorrido (null)
    problemas = []
    d = pestana(*generar(con_externo()), problemas)
    if d is not None:
        cajas(d, problemas)
        recorrido(d, problemas, None)
    inf.escenario("Lo externo se distingue, no solo por el color", problemas)

    # 3 · Una conexión a algo desconocido se dice: con la tabla nueva (columna «Externo» y línea «Flujo:»), «Panel
    #     interno» conecta también con «Buzón», que no está (la línea, sin negrita y con «->»)
    problemas = []
    d = pestana(*generar(con_externo("API · Motor de pagos · Buzón")
                         + [con_flujo("Flujo: Tienda web -> API -> Motor de pagos")]), problemas)
    if d is not None:
        cajas(d, problemas)
        recorrido(d, problemas, ["Tienda web", "API", "Motor de pagos"])
        if not any("Buzón" in t for t in avisos(d, "componentes")):
            problemas.append(f"ningún aviso de la parte «componentes» nombra «Buzón»: "
                             f"avisos = {json.dumps(saca(d, 'avisos'), ensure_ascii=False)}")
    inf.escenario("Una conexión a algo desconocido se dice", problemas)


flujo.principal("P17", escenarios)
