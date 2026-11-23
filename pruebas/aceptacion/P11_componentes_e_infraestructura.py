#!/usr/bin/env python3
"""P11 · Components and infrastructure on the tab (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-23, en el plan).

- Each diagram shows what connects to what. Dado «Componentes» and «Infraestructura» with «Conecta con» filled, Cuando
  their diagrams open, Entonces every row is a box and every connection a line between its two boxes.
- A connection to something unknown is said. Dado a «Conecta con» that names something its table does not have, Cuando
  the diagram opens, Entonces the rest is painted and the tab names it.

Por la única entrada de las cuatro piezas de F2: el generador del tablero sobre la raíz de muestra de P05_lectores.py, y lo que
escribe en desarrollo/ventas--portal.json. El dibujo queda para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P11_componentes_e_infraestructura.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P05_lectores import *  # noqa: E402,F401,F403  (la muestra, cómo se corre el generador y lo que dice la muestra: una sola copia)


def escenarios(inf):
    # 1 · Cada diagrama muestra qué se conecta con qué: cada fila es una caja, cada conexión va entre dos cajas
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        for parte, filas in (("componentes", COMPONENTES), ("infraestructura", INFRAESTRUCTURA)):
            vistas = por_clave(saca(d, "diseno", parte), "nombre")
            igual(problemas, f"las cajas de {parte}", sorted(vistas), sorted(filas))
            for nombre, conecta in filas.items():
                igual(problemas, f"«Conecta con» de «{nombre}» ({parte})", saca(vistas, nombre, "conecta_con"), conecta)
            for nombre, f in vistas.items():
                for otro in f.get("conecta_con") or []:
                    if otro not in vistas:
                        problemas.append(f"la conexión de «{nombre}» con «{otro}» no acaba en una caja de {parte}")
    inf.escenario("Cada diagrama muestra qué se conecta con qué", problemas)

    # 2 · Una conexión a algo desconocido se dice: «Panel interno» conecta con «Buzón», que no está en «Componentes»,
    #     y «Dominio» con «CDN», que no está en «Infraestructura»
    problemas = []
    cambios = [(DISENO, "| Panel interno | Donde la tienda prepara los pedidos | muestra/portal:panel | API · Motor de pagos |",
                "| Panel interno | Donde la tienda prepara los pedidos | muestra/portal:panel | API · Motor de pagos · Buzón |"),
               (DISENO, "| Dominio | La dirección de la tienda | Registrador · producción | Servidor web |",
                "| Dominio | La dirección de la tienda | Registrador · producción | Servidor web · CDN |")]
    d = pestana(*generar(cambios), problemas)
    if d is not None:
        for parte, filas, desconocido, fila in (("componentes", COMPONENTES, "Buzón", "Panel interno"),
                                               ("infraestructura", INFRAESTRUCTURA, "CDN", "Dominio")):
            vistas = por_clave(saca(d, "diseno", parte), "nombre")
            igual(problemas, f"las cajas de {parte}", sorted(vistas), sorted(filas))
            for otro in filas[fila]:
                if otro not in (saca(vistas, fila, "conecta_con") or []):
                    problemas.append(f"la conexión de «{fila}» con «{otro}», que sí está, ya no se pinta")
            if not any(desconocido in t for t in avisos(d, parte)):
                problemas.append(f"ningún aviso de la parte «{parte}» nombra «{desconocido}»: "
                                 f"avisos = {json.dumps(saca(d, 'avisos'), ensure_ascii=False)}")
    inf.escenario("Una conexión a algo desconocido se dice", problemas)


flujo.principal("P11", escenarios)
