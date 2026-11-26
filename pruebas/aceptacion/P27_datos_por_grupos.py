#!/usr/bin/env python3
"""P27 · The data model by groups (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-25, en el plan).

- Groups are stacked. Dado a design with a «Grupos» table and a «Grupo» on each entity, Cuando the tab opens, Entonces
  there is one container per group, in the table's order, with its entities inside, each with its name and its «En
  corto».
- The centre, and what stands apart. Dado one group with «Papel» `centro` and another with `aparte`, Cuando the tab
  opens, Entonces the first has a thick border, and the second is dashed with no line to or from it.
- Lines between groups and inside one. Dado a group with «Se relaciona con» and two related entities of one group,
  Cuando the tab opens, Entonces there is one line between the two containers with its verb and one between the two
  entities; a relation between entities of different groups is not drawn and is listed in each one's window.
- Colour and legend come from the groups. Dado three groups, Cuando the tab opens, Entonces each has its own colour, and
  the legend has a line per group with its «En corto».
- All relations, on demand. Dado the drawing by groups, Cuando «Todas las relaciones» is pressed, Entonces the drawing
  by flow of 1.29.1 is shown, and pressing again brings the groups back.
- Without the table, as today. Dado a design with no «Grupos» table, Cuando the tab opens, Entonces the data are drawn
  as in 1.29.1, with a warning that says what to add.
- An entity with no group is said. Dado an entity whose group is not in the table, Cuando the tab opens, Entonces it is
  drawn last, apart, and the tab warns which one it is.

Por las dos entradas de F5: el generador del tablero sobre la raíz de muestra de P05_lectores.py (diseno.grupos y los
avisos) y trazarDesarrollo(diseno, opciones) de la página, corrido con node como en P21_lineas_que_se_siguen.py (modo,
contenedores, cajas, líneas, verbos, leyenda y banda de «datos»); el botón «Todas las relaciones», en la página leída
como texto. Que pulsarlo cambie el dibujo y vuelva, los colores y el grosor de verdad, y que la ventana de una entidad
liste sus relaciones con otros grupos quedan para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P27_datos_por_grupos.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P21_lineas_que_se_siguen import *  # noqa: E402,F401,F403  (la muestra de P05, cómo se saca y se corre el trazado)

BOTON = 'data-accion="todas-las-relaciones"'
TABLA_DATOS = """| Entidad | Grupo | Qué es | Se relaciona con |
|---|---|---|---|
| cliente | Ventas | Quien compra en la tienda | pedido (1:N) |
| pedido | Ventas | Lo que un cliente pide de una vez | producto (N:M) |
| producto | Catálogo | Lo que la tienda vende | categoria (N:1) |
| categoria | Catálogo | Un grupo de productos | |
"""

# La muestra de cuatro grupos: Enlaces relaciona, Cosas es el centro, Registro (debajo) lo actualiza y Acceso va aparte.
# cosa → carpeta, del mismo grupo; enlace → cosa y acto → cosa, de grupos distintos. Acceso tiene una relación dentro
# (permiso → persona) y una con Cosas, para ver que ninguna línea lo toca
ENTIDADES_G = [   # nombre, en corto, grupo, relaciones
    ("enlace", "une dos cosas", "Enlaces", "cosa (une)"),
    ("cosa", "lo que se trabaja", "Cosas", "carpeta (vive en)"),
    ("carpeta", "dónde vive", "Cosas", ""),
    ("acto", "un cambio", "Registro", "cosa (deja)"),
    ("persona", "quién entra", "Acceso", ""),
    ("permiso", "qué puede", "Acceso", "persona (de)"),
]
GRUPOS = [   # nombre, en corto, papel, se relaciona con
    ("Enlaces", "lo que relaciona", "", "Cosas (une)"),
    ("Cosas", "con lo que se trabaja", "centro", ""),
    ("Registro", "lo que pasó", "", "Cosas (actualiza)"),
    ("Acceso", "quién puede", "aparte", "Cosas (protege)"),
]
GRUPOS_JSON = [
    {"nombre": "Enlaces", "en_corto": "lo que relaciona", "papel": "", "relaciones": [{"con": "Cosas", "verbo": "une"}]},
    {"nombre": "Cosas", "en_corto": "con lo que se trabaja", "papel": "centro", "relaciones": []},
    {"nombre": "Registro", "en_corto": "lo que pasó", "papel": "", "relaciones": [{"con": "Cosas", "verbo": "actualiza"}]},
    {"nombre": "Acceso", "en_corto": "quién puede", "papel": "aparte", "relaciones": [{"con": "Cosas", "verbo": "protege"}]},
]
SUELTA = ("suelta", "sin grupo", "Huérfanos", "")


def con_grupos(entidades=ENTIDADES_G, grupos=GRUPOS):
    """El cambio que pone en «Datos» la tabla de entidades de la muestra de grupos y, detrás, la tabla «Grupos»."""
    t = "| Entidad | En corto | Grupo | Qué es | Se relaciona con |\n|---|---|---|---|---|\n"
    t += "".join(f"| {n} | {c} | {g} | La entidad {n} | {r} |\n".replace("|  |", "| |") for n, c, g, r in entidades)
    t += "\n| Grupo | En corto | Papel | Se relaciona con |\n|---|---|---|---|\n"
    t += "".join(f"| {n} | {c} | {p} | {r} |\n".replace("|  |", "| |").replace("|  |", "| |") for n, c, p, r in grupos)
    # sin la línea «Detalle:», que nombraría cada entidad nueva en un aviso de desajuste (P10)
    return (DISENO, TABLA_DATOS + "\nDetalle: ventas/portal/entregables/datos-detalle.md\n", t)


TRES = ([e for e in ENTIDADES_G if e[2] != "Acceso"], GRUPOS[:3])


def trazar_con(diseno, problemas, opciones=None):
    """trazarDesarrollo(diseno) o trazarDesarrollo(diseno, opciones), corrido con node, o None con el porqué."""
    if not isinstance(diseno, dict):
        if not shutil.which("node"):
            raise flujo.Montaje("no hay node en el PATH: el trazado de la página se corre con él")
        problemas.append(f"«diseno» es {json.dumps(diseno, ensure_ascii=False)[:80]}: no hay qué trazar")
        return None
    t = correr(INICIO, FIN, "trazarDesarrollo", [diseno] if opciones is None else [diseno, opciones], problemas)
    if t is not None and not isinstance(t, dict):
        problemas.append(f"trazarDesarrollo devolvió {json.dumps(t, ensure_ascii=False)[:120]}, no un objeto")
        return None
    return t


def datos_de(cambios, problemas, opciones=None):
    """(pestaña, diseno, dibujo de «datos») de la muestra con esos cambios; lo que falte, None."""
    d = pestana(*generar(cambios), problemas)
    if d is None:
        return None, None, None
    dis = saca(d, "diseno")
    t = trazar_con(dis, problemas, opciones)
    v = dibujo(t, "datos", problemas) if t is not None else None
    return d, dis, v


def modo(problemas, v, esperado, que="«datos»"):
    if v is not None and v.get("modo") != esperado:
        problemas.append(f"«modo» de {que} es {json.dumps(v.get('modo'))}, no «{esperado}»")
        return False
    return v is not None


def dentro(r, c):
    return (r[0] >= c[0] - TOL and r[1] >= c[1] - TOL and r[0] + r[2] <= c[0] + c[2] + TOL
            and r[1] + r[3] <= c[1] + c[3] + TOL)


def contenedores_por_id(v):
    return {c.get("id"): c for c in v["contenedores"] if isinstance(c, dict)}


def cajas_por_titulo(v):
    return {c.get("titulo"): c for c in v["cajas"] if isinstance(c, dict)}


def texto_de(x):
    return " ".join(x) if isinstance(x, list) and all(isinstance(s, str) for s in x) else x


def lineas_entre(v, entre):
    return [l for l in v["lineas"] if isinstance(l, dict) and l.get("entre") == entre]


def escenarios(inf):
    # 1 · Los grupos se apilan: diseno.grupos como la tabla; en el dibujo, modo «grupos», un contenedor por grupo en el
    #     orden de la tabla y de arriba abajo, y cada entidad dentro del suyo con su nombre y su «En corto»
    problemas = []
    d, dis, v = datos_de([con_grupos()], problemas)
    if dis is not None:
        if "grupos" not in dis:
            problemas.append("«diseno» no trae «grupos»")
        else:
            igual(problemas, "«diseno.grupos»", dis["grupos"], GRUPOS_JSON)
        malos = [t for t in avisos(d, "diseno") if "Grupos" in t]
        if malos:   # Añadido: con la tabla puesta, ningún aviso la pide
            problemas.append(f"con la tabla «Grupos», un aviso la pide: {json.dumps(malos, ensure_ascii=False)}")
    if modo(problemas, v, "grupos"):
        cs = [c for c in v["contenedores"] if isinstance(c, dict)]
        igual(problemas, "los «id» de los contenedores, en orden", [c.get("id") for c in cs], [g[0] for g in GRUPOS])
        ys = [c.get("y") for c in cs]
        if not num(*ys) or any(b <= a for a, b in zip(ys, ys[1:])):
            problemas.append(f"las «y» de los contenedores no crecen en el orden de la tabla: {json.dumps(ys)}")
        porid, caja = contenedores_por_id(v), cajas_por_titulo(v)
        for n, corto, g, _ in ENTIDADES_G:
            c = caja.get(n)
            if c is None:
                problemas.append(f"no hay caja con título «{n}»")
                continue
            igual(problemas, f"«grupo» de la caja «{n}»", c.get("grupo"), g)
            if "nombre" not in c or "corto" not in c:
                problemas.append(f"la caja «{n}» no trae «nombre» y «corto»")
            else:
                igual(problemas, f"«nombre» de la caja «{n}», junto", texto_de(c["nombre"]), n)
                igual(problemas, f"«corto» de la caja «{n}», junto", texto_de(c["corto"]), corto)
            rc, rk = rect(c), rect(porid.get(g))
            if rc is None or rk is None or not dentro(rc, rk):
                problemas.append(f"la caja «{n}» no está dentro del contenedor «{g}»: {rc} en {rk}")
    inf.escenario("Los grupos se apilan", problemas)

    # 2 · El centro, y lo que va aparte: grueso solo el de papel centro, discontinuo solo el de aparte; ninguna línea
    #     toca el contenedor aparte ni sus cajas, aunque Acceso tiene una relación con Cosas y otra dentro
    problemas = []
    d, dis, v = datos_de([con_grupos()], problemas)
    if modo(problemas, v, "grupos"):
        for c in v["contenedores"]:
            if not isinstance(c, dict):
                continue
            for k, cual in (("papel", None), ("grueso", "centro"), ("discontinuo", "aparte")):
                if k not in c:
                    problemas.append(f"el contenedor «{c.get('id')}» no trae «{k}»")
                elif cual is not None:
                    igual(problemas, f"«{k}» del contenedor «{c.get('id')}»", c[k], c.get("papel") == cual)
            igual(problemas, f"«papel» del contenedor «{c.get('id')}»", c.get("papel"),
                  {g[0]: g[2] for g in GRUPOS}.get(c.get("id")))
        caja = ids(v)
        aparte = {"Acceso", caja.get("persona"), caja.get("permiso")} - {None}
        malas = [(l.get("a"), l.get("b")) for l in v["lineas"] if isinstance(l, dict) and {l.get("a"), l.get("b")} & aparte]
        if malas:
            problemas.append(f"líneas que tocan el grupo aparte o sus cajas: {json.dumps(malas, ensure_ascii=False)}")
    inf.escenario("El centro, y lo que va aparte", problemas)

    # 3 · Líneas entre grupos y dentro de uno: una entre Enlaces y Cosas con «une» y una entre Registro y Cosas con
    #     «actualiza»; una entre cosa y carpeta con «vive en»; ninguna entre cajas de grupos distintos (enlace → cosa,
    #     acto → cosa). La relación entre grupos distintos sigue en las entidades (la ventana la lista: verificación)
    problemas = []
    d, dis, v = datos_de([con_grupos()], problemas)
    if dis is not None:
        rels = por_clave(saca(dis, "entidades"), "nombre")
        for n, con in (("enlace", "cosa"), ("acto", "cosa")):
            if not any(isinstance(r, dict) and r.get("con") == con for r in saca(rels, n, "relaciones") or []):
                problemas.append(f"la relación «{n}» → «{con}» ya no está en «diseno.entidades»")
    if modo(problemas, v, "grupos"):
        caja, grupo_de = ids(v), {c.get("id"): c.get("grupo") for c in v["cajas"] if isinstance(c, dict)}
        for l in v["lineas"]:
            if not isinstance(l, dict) or l.get("entre") not in ("grupos", "cajas"):
                problemas.append(f"una línea no dice «entre»: «grupos» o «cajas»: {json.dumps(l, ensure_ascii=False)[:120]}")
            elif l["entre"] == "cajas" and (grupo_de.get(l.get("a")) != grupo_de.get(l.get("b")) or l.get("a") not in grupo_de):
                problemas.append(f"la línea entre cajas {l.get('a')} → {l.get('b')} une cajas de grupos distintos")
        for a, b, entre, verbo in (("Enlaces", "Cosas", "grupos", "une"), ("Registro", "Cosas", "grupos", "actualiza"),
                                   (caja.get("cosa"), caja.get("carpeta"), "cajas", "vive en")):
            n = [l for l in lineas_entre(v, entre) if {l.get("a"), l.get("b")} == {a, b}]
            if len(n) != 1:
                problemas.append(f"entre {a} y {b} hay {len(n)} líneas «entre: {entre}», no una")
            if not any(isinstance(x, dict) and {x.get("a"), x.get("b")} == {a, b} and x.get("t") == verbo for x in v["verbos"]):
                problemas.append(f"la línea entre {a} y {b} no tiene su verbo «{verbo}» en «verbos»")
        for a, b in (("enlace", "cosa"), ("acto", "cosa")):
            if caja.get(a) and caja.get(b) and hay_linea(v, caja[a], caja[b]):
                problemas.append(f"«{a}» → «{b}», de grupos distintos, tiene línea")
        if v.get("banda", "falta") is not None:
            problemas.append(f"«banda» es {json.dumps(v.get('banda', 'falta'), ensure_ascii=False)[:80]}, no null")
    inf.escenario("Líneas entre grupos y dentro de uno", problemas)

    # 4 · El color y la leyenda salen de los grupos: con tres grupos, cada contenedor con un color distinto y la leyenda
    #     con una entrada por grupo y su «En corto»
    def colores_y_leyenda(grupos, problemas, v):
        if not modo(problemas, v, "grupos"):
            return
        colores = [c.get("color") for c in v["contenedores"] if isinstance(c, dict)]
        if len(colores) != len(grupos) or None in colores or len(set(map(str, colores))) != len(colores):
            problemas.append(f"los «color» de los contenedores son {json.dumps(colores)}: no uno distinto por grupo")
        ley = sorted((str(x.get("grupo")), str(x.get("texto"))) for x in v["leyenda"] if isinstance(x, dict))
        if ley != sorted((g[0], g[1]) for g in grupos) or len(v["leyenda"]) != len(grupos):
            problemas.append(f"la leyenda es {json.dumps(v['leyenda'], ensure_ascii=False)}, no una entrada por grupo con "
                             "su «En corto»")
    problemas = []
    d, dis, v = datos_de([con_grupos(*TRES)], problemas)
    colores_y_leyenda(TRES[1], problemas, v)
    inf.escenario("El color y la leyenda salen de los grupos", problemas)

    # 4b · Añadido: lo mismo con los cuatro grupos, el aparte incluido
    problemas = []
    d, dis, v = datos_de([con_grupos()], problemas)
    colores_y_leyenda(GRUPOS, problemas, v)
    inf.escenario("El color y la leyenda salen de los grupos (cuatro, con el aparte)", problemas)

    # 5 · Todas las relaciones, a petición: sin opciones, modo «grupos»; con {"datos": "todas"}, modo «flujo» y el mismo
    #     dibujo de «datos» que el del mismo diseño sin grupos (el de 1.29.1, con su banda y sus líneas); la página tiene
    #     el botón
    problemas = []
    d, dis, v = datos_de([con_grupos()], problemas)
    modo(problemas, v, "grupos")
    if dis is not None:
        t = trazar_con(dis, problemas, {"datos": "todas"})
        todas = dibujo(t, "datos", problemas) if t is not None else None
        sin = dict(dis, grupos=[])
        t = trazar_con(sin, problemas)
        base = dibujo(t, "datos", problemas) if t is not None else None
        if modo(problemas, todas, "flujo", "«datos» con {\"datos\": \"todas\"}") and modo(problemas, base, "flujo",
                                                                                         "«datos» sin grupos"):
            if todas != base:
                dif = sorted(k for k in set(todas) | set(base) if todas.get(k) != base.get(k))
                problemas.append(f"con {{\"datos\": \"todas\"}}, el dibujo de «datos» no es el del flujo de 1.29.1 (el "
                                 f"mismo diseño sin grupos): cambian {json.dumps(dif)}")
            caja = ids(todas)
            if caja.get("enlace") and caja.get("cosa") and not hay_linea(todas, caja["enlace"], caja["cosa"]):
                problemas.append("con {\"datos\": \"todas\"}, «enlace» → «cosa» (grupos distintos) no tiene línea")
    if BOTON not in pagina_texto():
        problemas.append(f"la página del tablero no tiene «{BOTON}»: no hay botón «Todas las relaciones»")
    inf.escenario("Todas las relaciones, a petición", problemas)

    # 6 · Sin la tabla, como hoy: la muestra de P05 tal cual; diseno.grupos es [], un aviso de la parte «diseno» nombra
    #     «Grupos», y «datos» se dibuja en modo «flujo» con una caja por entidad y una línea por relación
    problemas = []
    d, dis, v = datos_de([], problemas)
    if dis is not None:
        if "grupos" not in dis:
            problemas.append("«diseno» no trae «grupos» (tiene que ser [])")
        else:
            igual(problemas, "«diseno.grupos»", dis["grupos"], [])
        if not any("Grupos" in t for t in avisos(d, "diseno")):
            problemas.append(f"ningún aviso de la parte «diseno» nombra «Grupos»: avisos = "
                             f"{json.dumps(saca(d, 'avisos'), ensure_ascii=False)[:300]}")
    if modo(problemas, v, "flujo"):
        nombres, pares = filas(dis, "datos")
        caja = ids(v)
        faltan = [n for n in nombres if n not in caja]
        if faltan:
            problemas.append(f"no hay caja con título {json.dumps(faltan, ensure_ascii=False)}")
        for a, b in pares:
            if a in caja and b in caja and not hay_linea(v, caja[a], caja[b]):
                problemas.append(f"«{a}» → «{b}» no tiene línea")
    inf.escenario("Sin la tabla, como hoy", problemas)

    # 7 · Una entidad sin grupo se dice: «suelta», del grupo «Huérfanos», que no está en la tabla. Un aviso la nombra; su
    #     caja lleva grupo "", no está en ningún contenedor y queda debajo del último
    problemas = []
    d, dis, v = datos_de([con_grupos(ENTIDADES_G + [SUELTA])], problemas)
    if d is not None and not any("suelta" in t for t in avisos(d)):
        problemas.append(f"ningún aviso nombra «suelta»: avisos = {json.dumps(saca(d, 'avisos'), ensure_ascii=False)[:300]}")
    if modo(problemas, v, "grupos"):
        c = cajas_por_titulo(v).get("suelta")
        rs = [rect(k) for k in v["contenedores"] if isinstance(k, dict)]
        if c is None:
            problemas.append("no hay caja con título «suelta»")
        else:
            igual(problemas, "«grupo» de la caja «suelta»", c.get("grupo"), "")
            r = rect(c)
            if r is None or None in rs or not rs:
                problemas.append(f"la caja «suelta» o los contenedores no traen x, y, w, h: {r}, {rs}")
            else:
                if any(dentro(r, k) or solapan(r, k) for k in rs):
                    problemas.append(f"la caja «suelta» está dentro de un contenedor o lo pisa: {r}")
                fondo = max(k[1] + k[3] for k in rs)
                if not r[1] > fondo:
                    problemas.append(f"la «y» de la caja «suelta» ({r[1]}) no pasa del borde de abajo del último contenedor "
                                     f"({fondo})")
    inf.escenario("Una entidad sin grupo se dice", problemas)


def pagina_texto():
    if not VISTA.is_file():
        raise flujo.Montaje(f"no está la página del tablero en {VISTA}")
    return VISTA.read_text(encoding="utf-8", errors="replace")


flujo.principal("P27", escenarios)
