#!/usr/bin/env python3
"""P22 · Hours and stops in the plan (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-23, en el plan).

- A piece shows its hours. Dado a plan whose «Piezas» table has «Horas», Cuando the plan opens on the tab, Entonces each
  card shows its hours and each phase the sum of its pieces.
- A stop is marked. Dado a piece with text in «Para antes», Cuando the plan opens, Entonces its card carries a mark, and
  its window says what is asked before building it.
- Without the columns the plan is drawn as today. Dado a plan with neither column, Cuando it opens, Entonces it is drawn
  as in 1.29.0 and the tab does not warn.

Por la entrada de F2: el generador del tablero sobre la raíz de muestra de P05_lectores.py, y lo que escribe en
desarrollo/ventas--portal.json: plan.piezas[].horas (número o null) y para_antes (texto, "" sin él), y plan.fases[].horas
(la suma de las de sus piezas, o null). Que la tarjeta enseñe las horas y la marca, la suma en la fase y lo que dice la
ventana quedan para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P22_horas_y_paradas.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P05_lectores import *  # noqa: E402,F401,F403  (la muestra, cómo se corre el generador y lo que dice la muestra: una sola copia)

CABECERA = ("| Pieza | Fase | Qué entrega |\n|---|---|---|",
            "| Pieza | Fase | Qué entrega | Horas | Para antes |\n|---|---|---|---|---|")
FILA = {"P01": "| P01 · Lista de productos | F1 | La tienda muestra todos los productos con su categoría |",
        "P02": "| P02 · Precios | F1 | Cada producto muestra su precio vigente |",
        "P03": "| P03 · Pedido en línea | F2 | El cliente arma un pedido y lo paga |"}
PARADA = "Que Ana Pérez apruebe la lista de precios"


def columnas(celdas):
    """Los cambios que ponen «Horas» y «Para antes» detrás de «Qué entrega»: celdas = {pieza: (horas, para antes)}."""
    return [(PLAN,) + CABECERA] + [(PLAN, FILA[p], f"{FILA[p]} {h} | {pa} |") for p, (h, pa) in celdas.items()]


def horas_igual(problemas, que, visto, esperado):
    bien = visto is None if esperado is None else (
        isinstance(visto, (int, float)) and not isinstance(visto, bool) and abs(visto - esperado) < 1e-9)
    if not bien:
        problemas.append(f"{que} es {json.dumps(visto)}, y la muestra dice {json.dumps(esperado)}")


def revisa(d, problemas, piezas, fases):
    """piezas: {id: (horas, para antes)}; fases: {id: horas}. Las claves tienen que estar, también con null o ""."""
    vistas = por_clave(saca(d, "plan", "piezas"), "id")
    for pid, (h, pa) in piezas.items():
        p = vistas.get(pid)
        if p is None:
            problemas.append(f"falta la pieza {pid} en el plan")
            continue
        if "horas" not in p:
            problemas.append(f"la pieza {pid} no trae «horas» (tiene que ser {json.dumps(h)})")
        else:
            horas_igual(problemas, f"«horas» de {pid}", p["horas"], h)
        if "para_antes" not in p:
            problemas.append(f"la pieza {pid} no trae «para_antes» (tiene que ser {json.dumps(pa, ensure_ascii=False)})")
        else:
            igual(problemas, f"«para_antes» de {pid}", p["para_antes"], pa)
    vistas = por_clave(saca(d, "plan", "fases"), "id")
    for fid, h in fases.items():
        f = vistas.get(fid)
        if f is None:
            problemas.append(f"falta la fase {fid} en el plan")
        elif "horas" not in f:
            problemas.append(f"la fase {fid} no trae «horas» (tiene que ser {json.dumps(h)})")
        else:
            horas_igual(problemas, f"«horas» de la fase {fid}", f["horas"], h)


def sin_aviso(d, problemas):
    malos = [t for t in avisos(d, "plan") if "Horas" in t or "Para antes" in t]
    if malos:
        problemas.append(f"un aviso del plan menciona «Horas» o «Para antes»: {json.dumps(malos, ensure_ascii=False)}")


def escenarios(inf):
    # 1 · Una pieza enseña sus horas: «0.5», «0,75» y «1.5 h»; F1 suma 1.25 y F2, 1.5
    problemas = []
    d = pestana(*generar(columnas({"P01": ("0.5", ""), "P02": ("0,75", ""), "P03": ("1.5 h", "")})), problemas)
    if d is not None:
        revisa(d, problemas, {"P01": (0.5, ""), "P02": (0.75, ""), "P03": (1.5, "")}, {"F1": 1.25, "F2": 1.5})
        sin_aviso(d, problemas)
    inf.escenario("Una pieza enseña sus horas", problemas)

    # 1b · Añadido: la celda vacía es null y no cuenta en la suma; una fase sin ninguna pieza con horas, null. «1» entero
    problemas = []
    d = pestana(*generar(columnas({"P01": ("1", ""), "P02": ("", ""), "P03": ("", "")})), problemas)
    if d is not None:
        revisa(d, problemas, {"P01": (1, ""), "P02": (None, ""), "P03": (None, "")}, {"F1": 1, "F2": None})
    inf.escenario("Una pieza enseña sus horas (la celda vacía no cuenta)", problemas)

    # 2 · Una parada se marca: P02 lleva texto en «Para antes»; las otras, la celda vacía. Sin horas: las miran 1 y 1b
    problemas = []
    d = pestana(*generar(columnas({"P01": ("", ""), "P02": ("", PARADA), "P03": ("", "")})), problemas)
    if d is not None:
        vistas = por_clave(saca(d, "plan", "piezas"), "id")
        for pid, pa in (("P01", ""), ("P02", PARADA), ("P03", "")):
            if pid not in vistas:
                problemas.append(f"falta la pieza {pid} en el plan")
            elif "para_antes" not in vistas[pid]:
                problemas.append(f"la pieza {pid} no trae «para_antes» (tiene que ser {json.dumps(pa, ensure_ascii=False)})")
            else:
                igual(problemas, f"«para_antes» de {pid}", vistas[pid]["para_antes"], pa)
    inf.escenario("Una parada se marca", problemas)

    # 3 · Sin las columnas el plan se dibuja como hoy: la muestra tal cual; las fases y piezas de la 1.29.0, horas null,
    #     para_antes "", y ningún aviso del plan las pide
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        igual(problemas, "las fases y sus piezas", [(saca(f, "id"), saca(f, "piezas")) for f in saca(d, "plan", "fases") or []],
              [(f[0], f[6]) for f in FASES])
        revisa(d, problemas, {p: (None, "") for p in PIEZAS}, {"F1": None, "F2": None})
        sin_aviso(d, problemas)
    inf.escenario("Sin las columnas el plan se dibuja como hoy", problemas)


flujo.principal("P22", escenarios)
