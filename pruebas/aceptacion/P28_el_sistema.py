#!/usr/bin/env python3
"""P28 · The system (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-25, en el plan).

- One drawing instead of two. Dado a design whose «Infraestructura» has «Tipo», Cuando the tab opens, Entonces it shows
  «El sistema» and no drawing of components.
- Frames and order. Dado pieces of two providers, Cuando the tab opens, Entonces each is inside the frame of its
  provider, account and environment, those that only call are on top and those that only receive at the bottom.
- Colour tells the type. Dado pieces of «Tipo» `corre`, `guarda` and `externo`, Cuando the tab opens, Entonces each type
  has its colour and the legend names the three.
- Components go inside their piece. Dado components with «Corre en» naming a piece, Cuando the tab opens, Entonces that
  piece's box lists their names, and its window shows their rows of the table.
- A verb on a line is optional. Dado a connection with a verb and one without, Cuando the tab opens, Entonces the first
  line carries it and the second is drawn bare.
- Without «Tipo», as today. Dado a design with no «Tipo» column, Cuando the tab opens, Entonces components and
  infrastructure are drawn as in 1.29.1, with a warning that says what to add.

Por las dos entradas de F5: el generador del tablero sobre la raíz de muestra de P05_lectores.py (diseno.sistema;
tipo, componentes y verbos de cada pieza de infraestructura; corre_en de cada componente; los avisos) y
trazarDesarrollo(diseno) de la página, corrido con node como en P21_lineas_que_se_siguen.py (el dibujo «sistema»); el
título «El sistema», en la página leída como texto. Que la vista salga con ese título, los colores de verdad y lo que
enseña la ventana de una pieza quedan para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P28_el_sistema.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P21_lineas_que_se_siguen import *  # noqa: E402,F401,F403  (la muestra de P05, cómo se saca y se corre el trazado)

TITULO = "El sistema"
TABLA_VIEJA = """| Pieza | Para qué | Dónde | Conecta con |
|---|---|---|---|
| Servidor web | Sirve la tienda y la API | Nube · producción | Base de datos |
| Base de datos | Guarda clientes, pedidos y productos | Nube · producción | |
| Dominio | La dirección de la tienda | Registrador · producción | Servidor web |
"""
# Dos proveedores (Nube y Banco), tres contenedores, los tres tipos; Dominio solo llama, Base de datos y Pasarela solo
# reciben; Servidor web → Base de datos lleva verbo y Servidor web → Pasarela no
PIEZAS_S = [   # nombre, tipo, proveedor, cuenta, ambiente, conecta con
    ("Dominio", "externo", "Nube", "cuenta-dominios", "producción", "Servidor web"),
    ("Servidor web", "corre", "Nube", "tienda-prod", "producción", "Base de datos (lee) · Pasarela"),
    ("Base de datos", "guarda", "Nube", "tienda-prod", "producción", ""),
    ("Pasarela", "externo", "Banco", "cuenta-tienda", "producción", ""),
]
CONECTA = {"Dominio": ["Servidor web"], "Servidor web": ["Base de datos", "Pasarela"], "Base de datos": [], "Pasarela": []}
VERBOS = {"Dominio": {}, "Servidor web": {"Base de datos": "lee"}, "Base de datos": {}, "Pasarela": {}}
COMPONENTES_EN = {"Servidor web": ["Tienda web", "API"], "Dominio": [], "Base de datos": [], "Pasarela": []}
CORRE_EN = {"Tienda web": "Servidor web", "API": "Servidor web", "Motor de pagos": "", "Panel interno": ""}
FILAS_COMPONENTES = {"Tienda web": "| muestra/portal:web | API |", "API": "| muestra/portal:api | Motor de pagos |",
                     "Motor de pagos": "| muestra/portal:pagos | |", "Panel interno": "| muestra/portal:panel | API · Motor de pagos |"}


def con_tipo(tipos=None, corre_en=True):
    """Los cambios que ponen la «Infraestructura» con «En corto» y «Tipo» (tipos = {pieza: celda}, por defecto los de
    PIEZAS_S) y, con corre_en, la columna «Corre en» al final de «Componentes»."""
    t = "| Pieza | En corto | Tipo | Para qué | Proveedor | Cuenta | Ambiente | Conecta con |\n" + "|---|" * 8
    t = t.replace("||", "|") + "\n"
    for n, tipo, prov, cuenta, amb, con in PIEZAS_S:
        celda = (tipos or {}).get(n, tipo)
        t += f"| {n} | la pieza {n} | {celda} | Para {n} | {prov} | {cuenta} | {amb} | {con} |\n".replace("|  |", "| |")
    cambios = [(DISENO, TABLA_VIEJA, t)]
    if corre_en:
        cambios.append((DISENO, "| Componente | Qué hace | Dónde vive | Conecta con |\n|---|---|---|---|",
                        "| Componente | Qué hace | Dónde vive | Conecta con | Corre en |\n|---|---|---|---|---|"))
        cambios += [(DISENO, fila, f"{fila} {CORRE_EN[n]} |".replace("|  |", "| |")) for n, fila in FILAS_COMPONENTES.items()]
    return cambios


def sistema_de(cambios, problemas):
    """(pestaña, diseno, trazado) de la muestra con esos cambios; lo que falte, None con el porqué (también si
    trazarDesarrollo devuelve null o nada)."""
    d = pestana(*generar(cambios), problemas)
    if d is None:
        return None, None, None
    dis = saca(d, "diseno")
    if not isinstance(dis, dict):
        problemas.append(f"«diseno» es {json.dumps(dis, ensure_ascii=False)[:80]}")
        return d, None, None
    antes = len(problemas)
    t = correr(INICIO, FIN, "trazarDesarrollo", [dis], problemas)
    if t is None and len(problemas) == antes:
        problemas.append("trazarDesarrollo(diseno) devolvió null o nada")
    if t is not None and not isinstance(t, dict):
        problemas.append(f"trazarDesarrollo(diseno) devolvió {json.dumps(t, ensure_ascii=False)[:120]}, no un objeto")
        t = None
    return d, dis, t


def el_sistema(t, problemas):
    """El dibujo «sistema» del trazado, con la forma de los de F5, o None con el porqué."""
    if t is None:
        return None
    if "sistema" not in t:
        problemas.append("trazarDesarrollo(diseno) no trae «sistema»")
        return None
    return dibujo(t, "sistema", problemas)


def campo(problemas, que, fila, k, esperado):
    if not isinstance(fila, dict):
        problemas.append(f"falta {que}")
    elif k not in fila:
        problemas.append(f"{que} no trae «{k}» (tiene que ser {json.dumps(esperado, ensure_ascii=False)})")
    else:
        igual(problemas, f"«{k}» de {que}", fila[k], esperado)


def sin_aviso_de_tipo(d, problemas):
    malos = [t for t in avisos(d) if "Tipo" in t]
    if malos:
        problemas.append(f"con la columna «Tipo», un aviso la pide: {json.dumps(malos, ensure_ascii=False)}")


def escenarios(inf):
    # 1 · Un dibujo en lugar de dos: diseno.sistema es true; el trazado trae «sistema» y deja componentes e
    #     infraestructura en null; la página trae «El sistema». Añadido: ningún aviso pide «Tipo»
    problemas = []
    d, dis, t = sistema_de(con_tipo(), problemas)
    if dis is not None:
        campo(problemas, "«diseno»", dis, "sistema", True)
        sin_aviso_de_tipo(d, problemas)
    if el_sistema(t, problemas) is not None:
        for k in ("componentes", "infraestructura"):
            if t.get(k, "falta") is not None:
                problemas.append(f"con «Tipo», «{k}» del trazado es {json.dumps(t.get(k, 'falta'), ensure_ascii=False)[:80]}, "
                                 "no null")
    if not VISTA.is_file():
        raise flujo.Montaje(f"no está la página del tablero en {VISTA}")
    if TITULO not in VISTA.read_text(encoding="utf-8", errors="replace"):
        problemas.append(f"la página del tablero no tiene «{TITULO}»: la vista no se titula así")
    inf.escenario("Un dibujo en lugar de dos", problemas)

    # 2 · Marcos y orden: un contenedor por proveedor, cuenta y ambiente (tres), cada caja dentro de uno solo, Servidor
    #     web y Base de datos en el mismo; Dominio, que solo llama, más arriba que Base de datos y Pasarela, que solo
    #     reciben
    problemas = []
    d, dis, t = sistema_de(con_tipo(), problemas)
    v = el_sistema(t, problemas)
    if v is not None:
        caja = {c.get("titulo"): rect(c) for c in v["cajas"] if isinstance(c, dict)}
        marcos = [rect(c) for c in v["contenedores"] if isinstance(c, dict)]
        if len(marcos) != 3 or None in marcos:
            problemas.append(f"hay {len(marcos)} contenedores (o sin x, y, w, h), y la muestra pide tres: Nube · tienda-prod, "
                             "Nube · cuenta-dominios y Banco · cuenta-tienda")
        else:
            donde = {}
            for n, *_ in PIEZAS_S:
                r = caja.get(n)
                en = [i for i, m in enumerate(marcos) if r is not None and r[0] >= m[0] - TOL and r[1] >= m[1] - TOL
                      and r[0] + r[2] <= m[0] + m[2] + TOL and r[1] + r[3] <= m[1] + m[3] + TOL]
                if len(en) != 1:
                    problemas.append(f"la caja «{n}» está dentro de {len(en)} contenedores, no de uno")
                else:
                    donde[n] = en[0]
            if len(donde) == 4:
                if donde["Servidor web"] != donde["Base de datos"]:
                    problemas.append("Servidor web y Base de datos, de Nube · tienda-prod · producción, van en contenedores distintos")
                if len({donde["Servidor web"], donde["Dominio"], donde["Pasarela"]}) != 3:
                    problemas.append("Dominio, Pasarela y Servidor web, de cuentas o proveedores distintos, comparten contenedor")
        if all(caja.get(n) is not None for n in ("Dominio", "Base de datos", "Pasarela")):
            for n in ("Base de datos", "Pasarela"):
                if not caja["Dominio"][1] < caja[n][1]:
                    problemas.append(f"Dominio, que solo llama, no está más arriba que «{n}», que solo recibe "
                                     f"(y {caja['Dominio'][1]} y {caja[n][1]})")
        else:
            problemas.append(f"faltan cajas en «sistema»: hay {json.dumps(sorted(map(str, caja)), ensure_ascii=False)}")
    inf.escenario("Marcos y orden", problemas)

    # 3 · El color dice el tipo: cada pieza con su tipo, en el generador y en la caja; la leyenda, una entrada por cada
    #     tipo del dibujo (los tres), con texto
    problemas = []
    d, dis, t = sistema_de(con_tipo(), problemas)
    if dis is not None:
        vistas = por_clave(saca(dis, "infraestructura"), "nombre")
        for n, tipo, *_ in PIEZAS_S:
            campo(problemas, f"la pieza «{n}»", vistas.get(n), "tipo", tipo)
    v = el_sistema(t, problemas)
    if v is not None:
        cajas = {c.get("titulo"): c for c in v["cajas"] if isinstance(c, dict)}
        for n, tipo, *_ in PIEZAS_S:
            campo(problemas, f"la caja «{n}» de «sistema»", cajas.get(n), "tipo", tipo)
        ley = [x for x in v["leyenda"] if isinstance(x, dict)]
        if sorted(str(x.get("tipo")) for x in ley) != ["corre", "externo", "guarda"] or len(ley) != len(v["leyenda"]):
            problemas.append(f"la leyenda de «sistema» es {json.dumps(v['leyenda'], ensure_ascii=False)}, no una entrada por "
                             "cada tipo (corre, guarda, externo)")
        vacias = [x.get("tipo") for x in ley if not isinstance(x.get("texto"), str) or not x["texto"].strip()]
        if vacias:
            problemas.append(f"en la leyenda de «sistema», no tienen texto los tipos {json.dumps(vacias)}")
    inf.escenario("El color dice el tipo", problemas)

    # 3b · Añadido: una celda «Tipo» vacía da tipo ""
    problemas = []
    d = pestana(*generar(con_tipo({"Base de datos": ""})), problemas)
    if d is not None:
        vistas = por_clave(saca(d, "diseno", "infraestructura"), "nombre")
        campo(problemas, "la pieza «Base de datos»", vistas.get("Base de datos"), "tipo", "")
        campo(problemas, "la pieza «Servidor web»", vistas.get("Servidor web"), "tipo", "corre")
    inf.escenario("El color dice el tipo (celda vacía)", problemas)

    # 4 · Los componentes van dentro de su pieza: Tienda web y API corren en Servidor web; la pieza los lista en el
    #     orden de «Componentes», en el generador y en su caja
    problemas = []
    d, dis, t = sistema_de(con_tipo(), problemas)
    if dis is not None:
        vistas = por_clave(saca(dis, "infraestructura"), "nombre")
        for n, comps in COMPONENTES_EN.items():
            campo(problemas, f"la pieza «{n}»", vistas.get(n), "componentes", comps)
        vistas = por_clave(saca(dis, "componentes"), "nombre")
        for n, en in CORRE_EN.items():
            campo(problemas, f"el componente «{n}»", vistas.get(n), "corre_en", en)
    v = el_sistema(t, problemas)
    if v is not None:
        cajas = {c.get("titulo"): c for c in v["cajas"] if isinstance(c, dict)}
        for n, comps in COMPONENTES_EN.items():
            campo(problemas, f"la caja «{n}» de «sistema»", cajas.get(n), "componentes", comps)
    inf.escenario("Los componentes van dentro de su pieza", problemas)

    # 4b · Añadido: con «Tipo» y sin la columna «Corre en», cada componente lleva corre_en "" y ninguna pieza lista
    #      componentes
    problemas = []
    d = pestana(*generar(con_tipo(corre_en=False)), problemas)
    if d is not None:
        for n in CORRE_EN:
            campo(problemas, f"el componente «{n}»", por_clave(saca(d, "diseno", "componentes"), "nombre").get(n), "corre_en", "")
        for n in COMPONENTES_EN:
            campo(problemas, f"la pieza «{n}»", por_clave(saca(d, "diseno", "infraestructura"), "nombre").get(n), "componentes", [])
    inf.escenario("Los componentes van dentro de su pieza (sin «Corre en»)", problemas)

    # 5 · Un verbo en la línea es opcional: «Base de datos (lee)» lleva verbo y «Pasarela» no. conecta_con no cambia de
    #     forma y los verbos van en «verbos»; en el dibujo, una línea por conexión (tres) y un solo verbo, «lee»
    problemas = []
    d, dis, t = sistema_de(con_tipo(), problemas)
    if dis is not None:
        vistas = por_clave(saca(dis, "infraestructura"), "nombre")
        for n in CONECTA:
            campo(problemas, f"la pieza «{n}»", vistas.get(n), "conecta_con", CONECTA[n])
            campo(problemas, f"la pieza «{n}»", vistas.get(n), "verbos", VERBOS[n])
    v = el_sistema(t, problemas)
    if v is not None:
        caja = ids(v)
        pares = [(a, b) for a, bs in CONECTA.items() for b in bs]
        for a, b in pares:
            if caja.get(a) is None or caja.get(b) is None or not hay_linea(v, caja[a], caja[b]):
                problemas.append(f"«{a}» → «{b}» no tiene línea en «sistema»")
        if len(v["lineas"]) != len(pares):
            problemas.append(f"«sistema» tiene {len(v['lineas'])} líneas, y la muestra tiene {len(pares)} conexiones")
        vs = [(x.get("a"), x.get("b"), x.get("t")) for x in v["verbos"] if isinstance(x, dict)]
        if len(v["verbos"]) != 1 or not vs or {vs[0][0], vs[0][1]} != {caja.get("Servidor web"), caja.get("Base de datos")} \
                or vs[0][2] != "lee":
            problemas.append(f"los verbos de «sistema» son {json.dumps(vs, ensure_ascii=False)}: tiene que haber uno solo, "
                             "«lee», en Servidor web → Base de datos")
    inf.escenario("Un verbo en la línea es opcional", problemas)

    # 6 · Sin «Tipo», como hoy: la muestra de P05 tal cual. diseno.sistema es false, el trazado trae «sistema» null y los
    #     dibujos de componentes e infraestructura de 1.29.1 (una caja por fila), y un aviso (de cualquier parte) pide «Tipo»
    problemas = []
    d, dis, t = sistema_de([], problemas)
    if dis is not None:
        campo(problemas, "«diseno»", dis, "sistema", False)
        if not any("Tipo" in x for x in avisos(d)):
            problemas.append(f"ningún aviso nombra «Tipo»: avisos = "
                             f"{json.dumps(saca(d, 'avisos'), ensure_ascii=False)[:300]}")
    if t is not None:
        if "sistema" not in t:
            problemas.append("trazarDesarrollo(diseno) no trae «sistema» (tiene que ser null sin «Tipo»)")
        elif t["sistema"] is not None:
            problemas.append(f"sin «Tipo», «sistema» es {json.dumps(t['sistema'], ensure_ascii=False)[:80]}, no null")
        for vista, filas_ in (("componentes", COMPONENTES), ("infraestructura", INFRAESTRUCTURA)):
            v = dibujo(t, vista, problemas)
            if v is not None:
                igual(problemas, f"las cajas de «{vista}»", sorted(ids(v)), sorted(filas_))
    inf.escenario("Sin «Tipo», como hoy", problemas)


flujo.principal("P28", escenarios)
