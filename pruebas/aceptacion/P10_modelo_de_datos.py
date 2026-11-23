#!/usr/bin/env python3
"""P10 · Data model on the tab (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-23, en el plan).

- The entities are drawn with their relations. Dado a design whose «Datos» has entities in two groups with relations
  between them, Cuando the tab's data model opens, Entonces every entity shows inside its group and every relation as a
  line between its two entities.
- An entity shows its detail and its concepts. Dado a `Detalle:` line that points to a document with a row for that
  entity, and two concepts that name it, Cuando the entity is clicked, Entonces that row's detail and the two concepts show.
- A mismatch is said, not hidden. Dado an entity of the design with no row in the detail document, and a row there that
  the design lacks, Cuando the data model opens, Entonces everything is painted and the tab names both.

Por la única entrada de las cuatro piezas de F2: el generador del tablero sobre la raíz de muestra de P05_lectores.py, y lo que
escribe en desarrollo/ventas--portal.json. El dibujo y el clic quedan para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P10_modelo_de_datos.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P05_lectores import *  # noqa: E402,F401,F403  (la muestra, cómo se corre el generador y lo que dice la muestra: una sola copia)


def escenarios(inf):
    # 1 · Las entidades se dibujan con sus relaciones: cada una en su grupo (dos grupos), cada relación entre dos
    #     entidades que están
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        vistas = por_clave(saca(d, "diseno", "entidades"), "nombre")
        igual(problemas, "las entidades", sorted(vistas), sorted(ENTIDADES))
        for nombre, (grupo, relaciones) in ENTIDADES.items():
            e = vistas.get(nombre, {})
            igual(problemas, f"el grupo de «{nombre}»", e.get("grupo"), grupo)
            igual(problemas, f"las relaciones de «{nombre}»", e.get("relaciones"), relaciones)
        for nombre, e in vistas.items():
            for r in e.get("relaciones") or []:
                if saca(r, "con") not in vistas:
                    problemas.append(f"la relación de «{nombre}» con {saca(r, 'con')!r} no acaba en una entidad")
    inf.escenario("Las entidades se dibujan con sus relaciones", problemas)

    # 2 · Una entidad muestra su detalle y sus conceptos: «cliente» tiene fila en el documento de «Detalle:» y la
    #     nombran dos conceptos (Pedido y Cliente frecuente)
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        cliente = por_clave(saca(d, "diseno", "entidades"), "nombre").get("cliente")
        if cliente is None:
            problemas.append("falta la entidad «cliente»")
        else:
            detalle = cliente.get("detalle")
            esperado = {"Campos": "nombre, correo, teléfono", "Dónde se guarda": "tabla clientes"}
            if not isinstance(detalle, dict) or any(detalle.get(k) != v for k, v in esperado.items()):
                problemas.append(f"el detalle de «cliente» es {json.dumps(detalle, ensure_ascii=False)}, y su fila de "
                                 f"{DETALLE} dice {json.dumps(esperado, ensure_ascii=False)}")
            igual(problemas, "los conceptos de «cliente»", sorted(c for c in cliente.get("conceptos") or [] if isinstance(c, str)),
                  sorted(["Pedido", "Cliente frecuente"]))
    inf.escenario("Una entidad muestra su detalle y sus conceptos", problemas)

    # 3 · Un desajuste se dice, no se esconde: «factura» está en el diseño y no en el detalle; «envio», al revés
    problemas = []
    cambios = [(DISENO, "| categoria | Catálogo | Un grupo de productos | |\n",
                "| categoria | Catálogo | Un grupo de productos | |\n"
                "| factura | Ventas | El comprobante de un pedido | pedido (1:1) |\n"),
               (DETALLE, "| categoria | nombre | tabla categorias |\n",
                "| categoria | nombre | tabla categorias |\n| envio | dirección, fecha | tabla envios |\n")]
    d = pestana(*generar(cambios), problemas)
    if d is not None:
        igual(problemas, "las entidades", sorted(por_clave(saca(d, "diseno", "entidades"), "nombre")),
              sorted(list(ENTIDADES) + ["factura"]))
        datos = avisos(d, "datos")
        de_factura = [i for i, t in enumerate(datos) if "factura" in t]
        de_envio = [i for i, t in enumerate(datos) if "envio" in t]
        if not de_factura:
            problemas.append("ningún aviso de la parte «datos» nombra «factura», la entidad sin detalle")
        if not de_envio:
            problemas.append("ningún aviso de la parte «datos» nombra «envio», la fila que el diseño no tiene")
        if de_factura and de_envio and set(de_factura) == set(de_envio) and len(de_factura) == 1:
            problemas.append("los dos desajustes van en un solo aviso, no en dos")
        if problemas:
            problemas.append(f"avisos = {json.dumps(saca(d, 'avisos'), ensure_ascii=False)}")
    inf.escenario("Un desajuste se dice, no se esconde", problemas)


flujo.principal("P10", escenarios)
