#!/usr/bin/env python3
"""P20 · The shared base without lines (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-23, en el plan).

- The base is a band with no lines. Dado a data model with a «Flujo:» where two or more entities point to one outside
  the flow, Cuando it opens, Entonces that entity is drawn in a band under the flow and no line reaches it.
- The relations to the base are still told. Dado an entity with a relation to the base, Cuando its window opens,
  Entonces the window lists that relation with its verb, and a note under the drawing says where they are.
- Any other relation keeps its line. Dado a relation between two entities that are not the base, Cuando the data model
  opens, Entonces its line is drawn with its verb.

Por las dos entradas de F5: el generador del tablero sobre la raíz de muestra de P05_lectores.py (las relaciones hacia la
base llevan "base": true) y trazarDesarrollo(diseno) de la página, corrido con node como en P21_lineas_que_se_siguen.py
(la banda, las líneas, los verbos y la nota). Que la ventana liste la relación queda para la verificación: lo dice
RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P20_base_sin_lineas.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P21_lineas_que_se_siguen import *  # noqa: E402,F401,F403  (la muestra de P05, cómo se saca y se corre el trazado, y la base de P20)

RELACIONES = {
    "cliente": [{"con": "pedido", "tipo": "1:N"}],
    "pedido": [{"con": "producto", "tipo": "", "verbo": "lleva"}, {"con": "categoria", "tipo": "", "verbo": "de", "base": True}],
    "producto": [{"con": "categoria", "tipo": "", "verbo": "vive en", "base": True}],
    "categoria": [],
}


def relaciones(d, problemas, esperado):
    vistas = por_clave(saca(d, "diseno", "entidades"), "nombre")
    for nombre, rels in esperado.items():
        igual(problemas, f"las relaciones de «{nombre}»", saca(vistas, nombre, "relaciones"), rels)


def datos(d, problemas):
    """El dibujo de «Datos» de la pestaña, con {titulo: id} de sus cajas, o (None, {})."""
    t = trazar(saca(d, "diseno"), problemas)
    v = dibujo(t, "datos", problemas) if t is not None else None
    return v, (ids(v) if v is not None else {})


def escenarios(inf):
    # 1 · La base es una banda sin líneas: las relaciones hacia categoria llevan "base": true y las demás no llevan la
    #     clave; en el dibujo, categoria está en la banda y ninguna línea llega a ella ni sale de ella
    problemas = []
    d = pestana(*generar(CON_BASE), problemas)
    if d is not None:
        relaciones(d, problemas, RELACIONES)
        v, caja = datos(d, problemas)
        if v is not None:
            base = caja.get("categoria")
            banda = v.get("banda")
            if base is None:
                problemas.append("el dibujo de «Datos» no tiene caja con título «categoria»")
            elif not isinstance(banda, dict) or base not in (banda.get("ids") or []):
                problemas.append(f"«banda» es {json.dumps(banda, ensure_ascii=False)[:120]}: categoria ({base}) no está en ella")
            if base is not None:
                malas = [l for l in v["lineas"] if isinstance(l, dict) and base in (l.get("a"), l.get("b"))]
                if malas:
                    problemas.append(f"{len(malas)} líneas llegan a la base o salen de ella: "
                                     f"{json.dumps([(l.get('a'), l.get('b')) for l in malas], ensure_ascii=False)}")
        # y en la muestra de plugin-memoria de P21, donde la base, Project, apunta a Area: tampoco sale línea de ella
        d = pestana(*generar([con_muestra(MUESTRA_PLUGIN)]), problemas)
        v, caja = datos(d, problemas) if d is not None else (None, {})
        if v is not None:
            sale = [l.get("b") for l in v["lineas"] if isinstance(l, dict) and caja.get("Project") in (l.get("a"), l.get("b"))]
            if caja.get("Project") is None or sale:
                problemas.append(f"plugin-memoria: la base, Project, no tiene caja o tiene líneas: {json.dumps(sale)}")
    inf.escenario("La base es una banda sin líneas", problemas)

    # 1b · Añadido: sin línea «Flujo:» no hay base: ninguna relación lleva la clave «base» y no hay banda
    problemas = []
    d = pestana(*generar(CON_BASE[:2]), problemas)
    if d is not None:
        con_clave = [e.get("nombre") for e in saca(d, "diseno", "entidades") or [] if isinstance(e, dict)
                     and any(isinstance(r, dict) and "base" in r for r in e.get("relaciones") or [])]
        if con_clave:
            problemas.append(f"sin línea «Flujo:», llevan la clave «base» relaciones de {json.dumps(con_clave, ensure_ascii=False)}")
        v, _ = datos(d, problemas)
        if v is not None and v.get("banda") is not None:
            problemas.append(f"sin línea «Flujo:», «banda» es {json.dumps(v.get('banda'), ensure_ascii=False)[:120]}, no null")
    inf.escenario("La base es una banda sin líneas (sin «Flujo:» no hay base)", problemas)

    # 2 · Las relaciones con la base se siguen contando: la de producto lleva su verbo y "base": true, y el dibujo trae
    #     una nota que dice dónde están
    problemas = []
    d = pestana(*generar(CON_BASE), problemas)
    if d is not None:
        relaciones(d, problemas, {"producto": RELACIONES["producto"]})
        v, _ = datos(d, problemas)
        if v is not None and (not isinstance(v.get("nota"), str) or not v["nota"].strip()):
            problemas.append(f"la «nota» del dibujo de «Datos» es {json.dumps(v.get('nota'), ensure_ascii=False)}: no dice "
                             "dónde están las relaciones con la base")
    inf.escenario("Las relaciones con la base se siguen contando", problemas)

    # 3 · Cualquier otra relación guarda su línea: pedido → producto (lleva) tiene su línea y su verbo
    problemas = []
    d = pestana(*generar(CON_BASE), problemas)
    if d is not None:
        v, caja = datos(d, problemas)
        if v is not None:
            a, b = caja.get("pedido"), caja.get("producto")
            if a is None or b is None:
                problemas.append("el dibujo de «Datos» no tiene caja con título «pedido» o «producto»")
            else:
                if not hay_linea(v, a, b):
                    problemas.append("pedido → producto no tiene línea en el dibujo")
                if not any(isinstance(x, dict) and {x.get("a"), x.get("b")} == {a, b} and x.get("t") == "lleva"
                           for x in v["verbos"]):
                    problemas.append(f"pedido → producto no tiene su verbo «lleva» en «verbos»: "
                                     f"{json.dumps(v['verbos'], ensure_ascii=False)[:160]}")
    inf.escenario("Cualquier otra relación guarda su línea", problemas)


flujo.principal("P20", escenarios)
