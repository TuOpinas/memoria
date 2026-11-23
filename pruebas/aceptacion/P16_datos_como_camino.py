#!/usr/bin/env python3
"""P16 · The data model as a path (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-23, en el plan).

- The flow is one row, in its order. Dado a design whose «Datos» has a line «Flujo: A → B → C», Cuando the data model
  opens, Entonces A, B and C are drawn in one row, in that order.
- A relation carries its verb. Dado a relation written with its verb, «Things (vive en)», Cuando the data model opens,
  Entonces its line carries «vive en», not «N:1».
- Without a flow it is drawn as before. Dado a design with no «Flujo:» line, Cuando the data model opens, Entonces it is
  drawn as in 1.28.0 and the tab says what to add.
- An unknown entity in the flow is said. Dado a «Flujo:» that names an entity «Datos» does not have, Cuando the data
  model opens, Entonces the rest is drawn and the tab names it.

Por la entrada de F2: el generador del tablero sobre la raíz de muestra de P05_lectores.py, y lo que escribe en
desarrollo/ventas--portal.json: diseno.entidades[].relaciones ({"con", "tipo"}, con «verbo» solo si lo lleva) y diseno.datos_disposicion
({"flujo", "arriba", "abajo"}, o null sin línea «Flujo:»). El dibujo (la fila, las líneas, el verbo sobre la línea) queda
para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P16_datos_como_camino.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P05_lectores import *  # noqa: E402,F401,F403  (la muestra, cómo se corre el generador y lo que dice la muestra: una sola copia)

DETALLE_LINEA = "\n\nDetalle: ventas/portal/entregables/datos-detalle.md"


def con_flujo(linea):
    """El cambio que pone la línea «Flujo:» en «Datos», debajo de la tabla."""
    return (DISENO, DETALLE_LINEA, "\n\n" + linea + DETALLE_LINEA)


def disposicion(d, problemas):
    """diseno.datos_disposicion como dict con sus tres listas, o None con el porqué."""
    dis = saca(d, "diseno", "datos_disposicion")
    if not isinstance(dis, dict) or any(not isinstance(dis.get(k), list) for k in ("flujo", "arriba", "abajo")):
        problemas.append(f"«datos_disposicion» es {json.dumps(dis, ensure_ascii=False)}, no "
                         "{\"flujo\": [...], \"arriba\": [...], \"abajo\": [...]}")
        return None
    return dis


def reparto(problemas, dis, esperado):
    """Compara flujo, arriba y abajo, y que cada entidad de «Datos» esté en una sola de las tres."""
    for k in ("flujo", "arriba", "abajo"):
        igual(problemas, f"«{k}» de datos_disposicion", dis.get(k) if k == "flujo" else sorted(dis.get(k)), esperado[k])
    todas = dis["flujo"] + dis["arriba"] + dis["abajo"]
    if sorted(todas) != sorted(ENTIDADES):
        problemas.append(f"flujo, arriba y abajo juntos son {json.dumps(sorted(todas), ensure_ascii=False)}: cada entidad "
                         f"de «Datos» tiene que estar en una sola ({json.dumps(sorted(ENTIDADES), ensure_ascii=False)})")


def sin_aviso_de_flujo(d, problemas):
    malos = [t for t in avisos(d, "datos") if "Flujo:" in t]
    if malos:
        problemas.append(f"con la línea «Flujo:» puesta, un aviso de los datos pide ponerla: {json.dumps(malos, ensure_ascii=False)}")


def entidades_como_antes(d, problemas):
    """Las cuatro entidades con su grupo, y cada relación exactamente como en 1.28.0 ({"con", "tipo"}, sin «verbo»)."""
    vistas = por_clave(saca(d, "diseno", "entidades"), "nombre")
    igual(problemas, "las entidades", sorted(vistas), sorted(ENTIDADES))
    for nombre, (grupo, relaciones) in ENTIDADES.items():
        e = vistas.get(nombre, {})
        igual(problemas, f"el grupo de «{nombre}»", e.get("grupo"), grupo)
        igual(problemas, f"las relaciones de «{nombre}»", e.get("relaciones"), relaciones)


def escenarios(inf):
    # 1 · El flujo es una fila, en su orden: «Flujo: cliente → pedido → producto»; categoría, a la que solo apunta
    #     producto, va arriba
    problemas = []
    d = pestana(*generar([con_flujo("**Flujo:** cliente → pedido → producto")]), problemas)
    if d is not None:
        dis = disposicion(d, problemas)
        if dis is not None:
            reparto(problemas, dis, {"flujo": ["cliente", "pedido", "producto"], "arriba": ["categoria"], "abajo": []})
        sin_aviso_de_flujo(d, problemas)
    inf.escenario("El flujo es una fila, en su orden", problemas)

    # 1b · Añadido: la misma línea sin negrita y con «->», en otro orden
    problemas = []
    d = pestana(*generar([con_flujo("Flujo: producto -> pedido -> cliente")]), problemas)
    if d is not None:
        dis = disposicion(d, problemas)
        if dis is not None:
            reparto(problemas, dis, {"flujo": ["producto", "pedido", "cliente"], "arriba": ["categoria"], "abajo": []})
        sin_aviso_de_flujo(d, problemas)
    inf.escenario("El flujo es una fila, en su orden (sin negrita y con «->»)", problemas)

    # 1c · Añadido: lo que está fuera del flujo y recibe dos flechas del flujo va abajo. Flujo «cliente → producto»;
    #      producto pasa a relacionarse con pedido, así que a pedido apuntan cliente y producto
    problemas = []
    d = pestana(*generar([con_flujo("**Flujo:** cliente → producto"),
                          (DISENO, "| Lo que la tienda vende | categoria (N:1) |", "| Lo que la tienda vende | pedido (N:M) |")]),
                problemas)
    if d is not None:
        dis = disposicion(d, problemas)
        if dis is not None:
            reparto(problemas, dis, {"flujo": ["cliente", "producto"], "arriba": ["categoria"], "abajo": ["pedido"]})
    inf.escenario("El flujo es una fila, en su orden (lo que recibe dos flechas va abajo)", problemas)

    # 2 · Una relación lleva su verbo: «producto · categoria (vive en)»
    problemas = []
    d = pestana(*generar([(DISENO, "| Lo que la tienda vende | categoria (N:1) |", "| Lo que la tienda vende | categoria (vive en) |")]),
                problemas)
    if d is not None:
        vistas = por_clave(saca(d, "diseno", "entidades"), "nombre")
        igual(problemas, "las relaciones de «producto»", saca(vistas, "producto", "relaciones"),
              [{"con": "categoria", "tipo": "", "verbo": "vive en"}])
        igual(problemas, "las relaciones de «cliente», que solo lleva cardinalidad", saca(vistas, "cliente", "relaciones"),
              [{"con": "pedido", "tipo": "1:N"}])
    inf.escenario("Una relación lleva su verbo", problemas)

    # 2b · Añadido: con cardinalidad y verbo, «categoria (N:1, vive en)», lleva los dos
    problemas = []
    d = pestana(*generar([(DISENO, "| Lo que la tienda vende | categoria (N:1) |",
                           "| Lo que la tienda vende | categoria (N:1, vive en) |")]), problemas)
    if d is not None:
        igual(problemas, "las relaciones de «producto»", saca(por_clave(saca(d, "diseno", "entidades"), "nombre"), "producto",
                                                             "relaciones"), [{"con": "categoria", "tipo": "N:1", "verbo": "vive en"}])
    inf.escenario("Una relación lleva su verbo (con cardinalidad y verbo)", problemas)

    # 3 · Sin flujo se dibuja como antes: la muestra tal cual, sin línea «Flujo:»
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        entidades_como_antes(d, problemas)
        dis = saca(d, "diseno")
        if not isinstance(dis, dict) or "datos_disposicion" not in dis:
            problemas.append("«diseno» no trae «datos_disposicion» (tiene que ser null sin línea «Flujo:»)")
        elif dis["datos_disposicion"] is not None:
            problemas.append(f"sin línea «Flujo:», «datos_disposicion» es "
                             f"{json.dumps(dis['datos_disposicion'], ensure_ascii=False)}, no null")
        if not any("Flujo:" in t for t in avisos(d, "datos")):
            problemas.append(f"ningún aviso de la parte «datos» dice que falta «Flujo:»: "
                             f"avisos = {json.dumps(saca(d, 'avisos'), ensure_ascii=False)}")
    inf.escenario("Sin flujo se dibuja como antes", problemas)

    # 4 · Una entidad desconocida en el flujo se dice: «envio» no está en «Datos»
    problemas = []
    d = pestana(*generar([con_flujo("**Flujo:** cliente → pedido → envio → producto")]), problemas)
    if d is not None:
        entidades_como_antes(d, problemas)
        dis = disposicion(d, problemas)
        if dis is not None:
            reparto(problemas, dis, {"flujo": ["cliente", "pedido", "producto"], "arriba": ["categoria"], "abajo": []})
        if not any("envio" in t for t in avisos(d, "datos")):
            problemas.append(f"ningún aviso de la parte «datos» nombra «envio»: "
                             f"avisos = {json.dumps(saca(d, 'avisos'), ensure_ascii=False)}")
    inf.escenario("Una entidad desconocida en el flujo se dice", problemas)


flujo.principal("P16", escenarios)
