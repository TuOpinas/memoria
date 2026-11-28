#!/usr/bin/env python3
"""P34 · What is built, on the drawings (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-27, en el plan).

- Each box takes its piece's state. Dado a design whose «Datos», «Componentes» and «Infraestructura» carry a «Pieza»
  column, and a last follow-up with one of those pieces `entregada`, one `en curso` and one `pendiente`, Cuando the
  Desarrollo tab shows the drawings, Entonces each box shows its piece's state in its border and how strongly it is
  drawn, and its colour still says its group or type.
- Without the column, as today. Dado a design with no «Pieza» column, Cuando the drawings show, Entonces they are drawn
  as today, with no state and no warning.
- A piece the plan does not have. Dado a row whose «Pieza» names a piece the plan does not have, Cuando the drawings
  show, Entonces that box is drawn without state and the piece is named under the drawing.
- What was merged outside the design. Dado a last follow-up that lists what was merged and the design does not have,
  Cuando the drawings show, Entonces it is said under the drawing.

Por el generador del tablero sobre la raíz de muestra de P05_lectores.py, con una columna «Pieza» al final de «Datos»,
«Componentes» e «Infraestructura» (en esta, la primera columna pasa a llamarse «Recurso»: #2026-11-27-13) y otra
última entrada de seguimiento, y lo que escribe en desarrollo/ventas--portal.json:
diseno.entidades[], diseno.componentes[] y diseno.infraestructura[] con «pieza» y «estado»; diseno.piezas_desconocidas y
diseno.fuera_del_diseno. Y la página del tablero (vista.html) leída como texto: «data-estado» en las cajas, y que nombre
piezas_desconocidas y fuera_del_diseno, lo que va bajo el dibujo. El borde y la intensidad de cada caja según su estado,
y que su color siga diciendo su grupo o tipo, quedan para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P34_lo_construido_en_los_dibujos.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P05_lectores import *  # noqa: E402,F401,F403  (la muestra, cómo se corre el generador y lo que dice la muestra: una sola copia)

VISTA = REPO / "plugins" / "memoria" / "skills" / "tablero" / "vista.html"
MARCA_ESTADO = "data-estado"
BAJO_EL_DIBUJO = ("piezas_desconocidas", "fuera_del_diseno")

# ---------- la columna «Pieza» al final de las tres tablas del diseño de la muestra ----------
# (parte del JSON, cabecera de la tabla, {nombre de la caja: (fila tal cual en la muestra, pieza)})
TABLAS = (
    ("entidades", "| Entidad | Grupo | Qué es | Se relaciona con |\n|---|---|---|---|", {
        "cliente": ("| cliente | Ventas | Quien compra en la tienda | pedido (1:N) |", "P01"),
        "pedido": ("| pedido | Ventas | Lo que un cliente pide de una vez | producto (N:M) |", "P03"),
        "producto": ("| producto | Catálogo | Lo que la tienda vende | categoria (N:1) |", "P02"),
        "categoria": ("| categoria | Catálogo | Un grupo de productos | |", ""),
    }),
    ("componentes", "| Componente | Qué hace | Dónde vive | Conecta con |\n|---|---|---|---|", {
        "Tienda web": ("| Tienda web | La página donde el cliente pide | muestra/portal:web | API |", "P01"),
        "API": ("| API | Guarda y entrega los pedidos | muestra/portal:api | Motor de pagos |", "P02"),
        "Motor de pagos": ("| Motor de pagos | Cobra los pedidos | muestra/portal:pagos | |", "P03"),
        "Panel interno": ("| Panel interno | Donde la tienda prepara los pedidos | muestra/portal:panel | API · Motor de pagos |", ""),
    }),
    # En la muestra de P05, la primera columna de «Infraestructura» se llama «Pieza» (el nombre de la caja), como en un
    # diseño de antes. Con la columna del plan, esa primera pasa a llamarse «Recurso» y «Pieza» va al final, la pieza
    # del plan, como en las otras dos tablas (shared-memory/plugin-memoria#2026-11-27-13)
    ("infraestructura", "| Pieza | Para qué | Dónde | Conecta con |\n|---|---|---|---|", {
        "Servidor web": ("| Servidor web | Sirve la tienda y la API | Nube · producción | Base de datos |", "P02"),
        "Base de datos": ("| Base de datos | Guarda clientes, pedidos y productos | Nube · producción | |", "P01"),
        "Dominio": ("| Dominio | La dirección de la tienda | Registrador · producción | Servidor web |", ""),
    }),
)


RECURSO = "| Recurso |"   # la primera columna de «Infraestructura» en un diseño con la columna del plan


def con_pieza(otras=None):
    """Los cambios que ponen la columna «Pieza» al final de las tres tablas, y en «Infraestructura» llaman «Recurso» a
    la primera. otras = {nombre: pieza} cambia la de una caja."""
    cambios = []
    for parte, cabecera, filas in TABLAS:
        cab, sep = cabecera.split("\n")
        if parte == "infraestructura":
            cab = cab.replace("| Pieza |", RECURSO, 1)
        cambios.append((DISENO, cabecera, f"{cab} Pieza |\n{sep}---|"))
        for nombre, (fila, pieza) in filas.items():
            pieza = (otras or {}).get(nombre, pieza)
            cambios.append((DISENO, fila, f"{fila} {pieza} |"))
    return cambios


# ---------- la última entrada del seguimiento de la muestra, y las que la sustituyen ----------
ULTIMA = "## 2026-11-20\n| Pieza | Estado |\n|---|---|\n| P01 | unida |\n| P02 | en curso |\n"
ANTERIOR = "## 2026-11-10\n| Pieza | Estado |\n|---|---|\n| P01 | en curso |\n| P02 | pendiente |\n| P03 | en curso |\n"


def ultima(estados, puntos=""):
    """La última entrada con estos estados ({pieza: estado}, en orden) y, detrás de la tabla, estos puntos."""
    filas = "".join(f"| {p} | {e} |\n" for p, e in estados.items())
    return (SEGUIMIENTO, ULTIMA, "## 2026-11-20\n| Pieza | Estado |\n|---|---|\n" + filas + (f"\n{puntos}" if puntos else ""))


TRES = {"P01": "entregada", "P02": "en curso", "P03": "pendiente"}   # una de cada, como pide el escenario
FUERA = ("Servicio de cupones (muestra/portal#41)", "Exportación a Excel (muestra/portal#43)")
PUNTOS = ("1. Estado de cada pieza: la tabla de arriba.\n"
          "2. Pull requests abiertos: ninguno.\n"
          "3. Pruebas fuera de la lista de activas: ninguna.\n"
          f"4. Unido fuera del diseño: {FUERA[0]} · {FUERA[1]}\n")
FUERA_ANTERIOR = "Buscador de pedidos (muestra/portal#12)"
PUNTOS_ANTERIOR = f"\n4. Unido fuera del diseño: {FUERA_ANTERIOR}\n"


def pagina():
    if not VISTA.is_file():
        raise flujo.Montaje(f"no está la página del tablero en {VISTA}")
    return VISTA.read_text(encoding="utf-8", errors="replace")


def cajas(d, problemas, esperado, estados, quitar_piezas=False):
    """Cada caja de las tres partes trae «pieza» y «estado». esperado = {nombre: pieza} por parte (de TABLAS si None);
    estados = {pieza: estado}. Sin pieza («» en la tabla, o quitar_piezas), «pieza» y «estado» son null."""
    dis = saca(d, "diseno")
    if not isinstance(dis, dict):
        problemas.append(f"«diseno» es {json.dumps(dis)}, no lo leído del diseño")
        return
    for parte, _, filas in TABLAS:
        vistas = por_clave(dis.get(parte), "nombre")
        for nombre, (_, pieza) in filas.items():
            pieza = None if quitar_piezas else (esperado or {}).get(nombre, pieza) or None
            caja = vistas.get(nombre)
            if caja is None:
                problemas.append(f"falta «{nombre}» en {parte}")
                continue
            for k, v in (("pieza", pieza), ("estado", estados.get(pieza) if pieza else None)):
                if k not in caja:
                    problemas.append(f"«{nombre}» ({parte}) no trae «{k}» (tiene que ser {json.dumps(v, ensure_ascii=False)})")
                elif k == "pieza" and v is None and caja[k] in (None, ""):
                    pass   # una celda vacía se lee como null o como «»
                else:
                    igual(problemas, f"«{k}» de «{nombre}» ({parte})", caja[k], v)


def lista(problemas, d, k):
    """diseno[k], que tiene que estar; None (con el porqué) si no está."""
    dis = saca(d, "diseno")
    if not isinstance(dis, dict) or k not in dis:
        problemas.append(f"«diseno» no trae «{k}»")
        return None
    return dis[k]


def en_pagina(problemas, *cadenas):
    texto = pagina()
    for c in cadenas:
        if c not in texto:
            problemas.append(f"la página del tablero no tiene «{c}»")


def escenarios(inf):
    # 1 · Cada caja lleva el estado de su pieza: la columna «Pieza» en las tres tablas (P01, P02, P03 y una fila sin
    #     pieza en cada una) y la última entrada con P01 entregada, P02 en curso y P03 pendiente. El grupo y lo demás de
    #     cada caja, como hoy (el color sigue diciendo su grupo o tipo). La página trae «data-estado»
    problemas = []
    d = pestana(*generar(con_pieza() + [ultima(TRES)]), problemas)
    if d is not None:
        cajas(d, problemas, None, TRES)
        revisa_diseno(d, problemas, ("entidades", "componentes", "infraestructura"))
        desconocidas = lista(problemas, d, "piezas_desconocidas")
        if desconocidas is not None:
            igual(problemas, "«piezas_desconocidas»", desconocidas, [])
        malos = [t for t in avisos(d) if "Pieza" in t]
        if malos:
            problemas.append(f"con la columna bien puesta, un aviso nombra «Pieza»: {json.dumps(malos, ensure_ascii=False)}")
    en_pagina(problemas, MARCA_ESTADO)
    inf.escenario("Each box takes its piece's state", problemas)

    # 1b · Añadido: el estado va tal cual de la última entrada, también «unida» y «revertida»; una pieza que la última
    #      entrada no nombra (P03, aunque la anterior sí) no tiene estado
    problemas = []
    otros = {"P01": "unida", "P02": "revertida"}
    d = pestana(*generar(con_pieza() + [ultima(otros)]), problemas)
    if d is not None:
        cajas(d, problemas, None, otros)
    inf.escenario("Each box takes its piece's state (unida, revertida, and a piece the last entry does not name)", problemas)

    # 2 · Sin la columna, como hoy: la muestra tal cual. Cada caja con «pieza» y «estado» null, ninguna pieza
    #     desconocida, ningún aviso que nombre «Pieza», y el diseño leído como en P05
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        cajas(d, problemas, None, {}, quitar_piezas=True)
        revisa_diseno(d, problemas)
        desconocidas = lista(problemas, d, "piezas_desconocidas")
        if desconocidas is not None:
            igual(problemas, "«piezas_desconocidas»", desconocidas, [])
        malos = [t for t in avisos(d) if "Pieza" in t]
        if malos:
            problemas.append(f"sin la columna, un aviso nombra «Pieza»: {json.dumps(malos, ensure_ascii=False)}")
    inf.escenario("Without the column, as today", problemas)

    # 2b · Añadido: un diseño de antes, cuya «Infraestructura» no tiene «Recurso» (la muestra de P05 tal cual): su
    #      «Pieza» es el nombre de la caja. Las tres cajas salen con su nombre y su «Conecta con», sin pieza ni estado,
    #      y ningún nombre de caja pasa por pieza desconocida (aunque el seguimiento dé estados)
    problemas = []
    d = pestana(*generar([ultima(TRES)]), problemas)
    if d is not None:
        dis = saca(d, "diseno")
        vistas = por_clave(dis.get("infraestructura") if isinstance(dis, dict) else None, "nombre")
        for nombre in INFRAESTRUCTURA:
            caja = vistas.get(nombre)
            if caja is None:
                problemas.append(f"falta «{nombre}» en infraestructura: su «Pieza» de antes es el nombre de la caja")
                continue
            for k in ("pieza", "estado"):
                if k not in caja:
                    problemas.append(f"«{nombre}» (infraestructura) no trae «{k}» (tiene que ser null)")
                elif caja[k] is not None and not (k == "pieza" and caja[k] == ""):   # pieza: null o «»; estado: null
                    problemas.append(f"«{k}» de «{nombre}» (infraestructura) es {json.dumps(caja[k], ensure_ascii=False)}"
                                     ", y en un diseño sin «Recurso» la caja no tiene pieza")
        revisa_diseno(d, problemas, ("infraestructura",))
        desconocidas = lista(problemas, d, "piezas_desconocidas")
        if desconocidas is not None:
            malas = [n for n in INFRAESTRUCTURA if n in json.dumps(desconocidas, ensure_ascii=False)]
            if malas:
                problemas.append(f"«piezas_desconocidas» trae nombres de cajas de infraestructura: {malas}")
    inf.escenario("Without the column, as today (an «Infraestructura» without «Recurso»: its «Pieza» is the box's name)",
                  problemas)

    # 3 · Una pieza que el plan no tiene: «pedido» dice P09. Esa caja sin estado (también si el seguimiento nombra P09:
    #     añadido), las demás con el suyo, y P09 en piezas_desconocidas, que la página nombra
    problemas = []
    con_p09 = dict(TRES, P09="entregada")
    d = pestana(*generar(con_pieza({"pedido": "P09"}) + [ultima(con_p09)]), problemas)
    if d is not None:
        cajas(d, problemas, {"pedido": "P09"}, TRES)   # P09 no está en TRES: «pedido» sin estado
        desconocidas = lista(problemas, d, "piezas_desconocidas")
        if desconocidas is not None:
            igual(problemas, "«piezas_desconocidas»", desconocidas, ["P09"])
    en_pagina(problemas, BAJO_EL_DIBUJO[0])
    inf.escenario("A piece the plan does not have", problemas)

    # 4 · Lo unido fuera del diseño: la última entrada dice en su punto 4 dos cosas unidas que el diseño no tiene;
    #     fuera_del_diseno las trae, y la página lo nombra. Añadido: no trae el punto 4 de la entrada anterior ni los
    #     otros puntos de la última
    problemas = []
    d = pestana(*generar([ultima({"P01": "unida", "P02": "en curso"}, PUNTOS),
                          (SEGUIMIENTO, ANTERIOR, ANTERIOR + PUNTOS_ANTERIOR)]), problemas)
    if d is not None:
        fuera = lista(problemas, d, "fuera_del_diseno")
        if fuera is not None:
            texto = json.dumps(fuera, ensure_ascii=False)
            for f in FUERA:
                if f not in texto:
                    problemas.append(f"«fuera_del_diseno» no trae «{f}», del punto 4 de la última entrada: {texto[:300]}")
            for f, de in ((FUERA_ANTERIOR, "el punto 4 de la entrada anterior"),
                          ("Pull requests abiertos", "el punto 2"), ("Pruebas fuera de la lista", "el punto 3")):
                if f in texto:
                    problemas.append(f"«fuera_del_diseno» trae «{f}», de {de}: {texto[:300]}")
    en_pagina(problemas, BAJO_EL_DIBUJO[1])
    inf.escenario("What was merged outside the design", problemas)

    # 4b · Añadido: sin punto 4 en la última entrada (la muestra tal cual), fuera_del_diseno está y va vacío
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        fuera = lista(problemas, d, "fuera_del_diseno")
        if fuera:
            problemas.append(f"sin punto 4, «fuera_del_diseno» no va vacío: {json.dumps(fuera, ensure_ascii=False)[:300]}")
    inf.escenario("What was merged outside the design (no point 4, nothing said)", problemas)


flujo.principal("P34", escenarios)
