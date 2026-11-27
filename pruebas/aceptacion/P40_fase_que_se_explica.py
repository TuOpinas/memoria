#!/usr/bin/env python3
"""P40 · The phase that explains itself (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-27, en el plan).

- The window says why the phase exists and what each piece brings. Dado a phase whose block «in plain words» (or «en
  llano») has a paragraph and a table of piece and what it fixes, Cuando its window opens on the board, Entonces the
  paragraph and the table show above the version, hours and «Listo cuando», each piece with its text.
- The card carries the first sentence. Dado the same phase, Cuando the plan shows on the Desarrollo tab, Entonces its
  card carries the paragraph's first sentence under its name, and nothing more of the block.
- A phase without the block shows as today. Dado a phase with no block «in plain words», Cuando its card and its window
  show, Entonces they show what they show today, with no empty space and no error.
- A table that names a piece the phase does not have still shows. Dado a block whose table names a piece that is not in
  the phase, Cuando the window opens, Entonces that row shows as written, and the rest of the window is unchanged.

Por dos entradas: el generador del tablero sobre la raíz de muestra de P05_lectores.py (plan.fases[].en_llano, el
párrafo, y plan.fases[].arregla, [{"pieza", "que"}] en el orden de la tabla), y la función faseEnLlano(fase) de la
página del tablero (el bloque entre «// >>> fase en llano» y «// <<< fase en llano» de vista.html), que se saca como
texto y se corre con node, como pestanaAlCambiar en P25, sobre la fase que dejó el generador. Devuelve null o
{"primera", "parrafo", "filas": [[pieza, que], …]}. Dónde pinta la página el párrafo, la tabla y la primera frase queda para la
verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P40_fase_que_se_explica.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P21_lineas_que_se_siguen import *  # noqa: E402,F401,F403  (la muestra de P05, el generador y cómo se corre un bloque de la página)

INICIO_L, FIN_L = "// >>> fase en llano", "// <<< fase en llano"

# El párrafo de «### F1 en llano» de la muestra pasa a tener dos frases: la tarjeta lleva solo la primera
PRIMERA = "El cliente puede ver en línea qué vende la tienda y a qué precio."
SEGUNDA = "Así deja de llamar para preguntar."
PARRAFO = f"{PRIMERA} {SEGUNDA}"
DOS_FRASES = (PLAN, f"### F1 en llano\n{PRIMERA}\n", f"### F1 en llano\n{PARRAFO}\n")
FILAS_F1 = [["P01", "Ver los productos sin llamar"], ["P02", "Saber el precio de cada producto"]]
# Una fila más en la tabla de F1, cuya pieza (P03) es de F2
AJENA = ["P03", "Pedir sin tener que llamar"]
CON_AJENA = (PLAN, "| P02 | Saber el precio de cada producto |\n",
             f"| P02 | Saber el precio de cada producto |\n| {AJENA[0]} | {AJENA[1]} |\n")
# El bloque de F2, entero: sin él, F2 no tiene bloque
BLOQUE_F2 = ("### F2 en llano\nEl cliente puede hacer y pagar su pedido sin llamar.\n\n| Pieza | Qué arregla |\n"
             "|---|---|\n| P03 | Pedir y pagar en línea |\n\n")
SIN_F2 = (PLAN, BLOQUE_F2, "")
# El mismo bloque de F1 con el título en inglés
EN_INGLES = (PLAN, "### F1 en llano\n", "### F1 in plain words\n")


def fase_de(d, fid, problemas):
    f = por_clave(saca(d, "plan", "fases"), "id").get(fid)
    if f is None:
        problemas.append(f"el plan del tablero no trae la fase {fid}")
    return f


def revisa_datos(f, fid, parrafo, filas, problemas):
    """plan.fases[fid].en_llano es el párrafo y .arregla las filas, [{"pieza", "que"}] en el orden de la tabla."""
    igual(problemas, f"«en_llano» de la fase {fid}", f.get("en_llano"), parrafo)
    arregla = f.get("arregla")
    if not isinstance(arregla, list):
        problemas.append(f"«arregla» de la fase {fid} es {json.dumps(arregla, ensure_ascii=False)}, no una lista")
        return
    igual(problemas, f"«arregla» de la fase {fid} como [pieza, que]",
          [[saca(a, "pieza"), saca(a, "que")] for a in arregla], filas)


NO_CORRIO = object()   # faseEnLlano no se pudo correr: correr ya dijo por qué


def en_llano(fase, problemas):
    antes = len(problemas)
    r = correr(INICIO_L, FIN_L, "faseEnLlano", [fase], problemas)
    return NO_CORRIO if len(problemas) > antes else r


def revisa_llano(r, fid, primera, parrafo, filas, problemas, claves=("primera", "parrafo", "filas")):
    if r is NO_CORRIO:
        return
    if not isinstance(r, dict):
        problemas.append(f"faseEnLlano(fase {fid}) devolvió {json.dumps(r, ensure_ascii=False)[:120]}, y la fase tiene "
                         "bloque: tiene que ser {\"primera\", \"parrafo\", \"filas\"}")
        return
    esperado = {"primera": primera, "parrafo": parrafo, "filas": filas}
    for k in claves:
        igual(problemas, f"«{k}» de faseEnLlano(fase {fid})", r.get(k), esperado[k])


def escenarios(inf):
    # 1 · La ventana dice por qué existe la fase y qué trae cada pieza: el párrafo entero y las filas, en su orden,
    #     llegan a los datos y faseEnLlano los da para la ventana
    problemas = []
    d = pestana(*generar([DOS_FRASES]), problemas)
    if d is not None:
        f = fase_de(d, "F1", problemas)
        if f is not None:
            revisa_datos(f, "F1", PARRAFO, FILAS_F1, problemas)
            revisa_llano(en_llano(f, problemas), "F1", PRIMERA, PARRAFO, FILAS_F1, problemas, ("parrafo", "filas"))
    inf.escenario("The window says why the phase exists and what each piece brings", problemas)

    # 1b · Añadido: el bloque titulado «in plain words» se lee igual que «en llano»
    problemas = []
    d = pestana(*generar([DOS_FRASES, EN_INGLES]), problemas)
    if d is not None:
        f = fase_de(d, "F1", problemas)
        if f is not None:
            revisa_datos(f, "F1", PARRAFO, FILAS_F1, problemas)
            revisa_llano(en_llano(f, problemas), "F1", PRIMERA, PARRAFO, FILAS_F1, problemas)
    inf.escenario("The window says why the phase exists and what each piece brings (block «in plain words»)", problemas)

    # 2 · La tarjeta lleva la primera frase: «primera» es solo la primera frase del párrafo, sin la segunda ni nada de
    #     la tabla. Y con el párrafo de una sola frase (F2 de la muestra), es el párrafo entero
    problemas = []
    d = pestana(*generar([DOS_FRASES]), problemas)
    if d is not None:
        f1, f2 = fase_de(d, "F1", problemas), fase_de(d, "F2", problemas)
        if f1 is not None:
            r = en_llano(f1, problemas)
            revisa_llano(r, "F1", PRIMERA, PARRAFO, FILAS_F1, problemas, ("primera",))
            if isinstance(r, dict) and isinstance(r.get("primera"), str):
                for sobra in [SEGUNDA] + [t for _, t in FILAS_F1]:
                    if sobra in r["primera"]:
                        problemas.append(f"«primera» de la fase F1 lleva «{sobra}», que no es la primera frase")
        if f2 is not None:
            revisa_llano(en_llano(f2, problemas), "F2", "El cliente puede hacer y pagar su pedido sin llamar.",
                         "El cliente puede hacer y pagar su pedido sin llamar.", [["P03", "Pedir y pagar en línea"]],
                         problemas, ("primera",))
    inf.escenario("The card carries the first sentence", problemas)

    # 3 · Una fase sin el bloque se ve como hoy: sin «### F2 en llano», el generador sale con 0, F2 llega con su
    #     versión, «Listo cuando» y piezas como siempre, con el párrafo vacío y sin filas, y faseEnLlano da null sin
    #     lanzar. F1, que sí lo tiene, no cambia
    problemas = []
    d = pestana(*generar([SIN_F2]), problemas)
    if d is not None:
        f1, f2 = fase_de(d, "F1", problemas), fase_de(d, "F2", problemas)
        if f2 is not None:
            for k, v in (("version", "1.1.0"), ("listo_cuando", "P03 pasa"), ("piezas", ["P03"])):
                igual(problemas, f"«{k}» de la fase F2", f2.get(k), v)
            if f2.get("en_llano") not in ("", None):
                problemas.append(f"«en_llano» de la fase F2, sin bloque, es {json.dumps(f2.get('en_llano'), ensure_ascii=False)}")
            if f2.get("arregla") not in ([], None):
                problemas.append(f"«arregla» de la fase F2, sin bloque, es {json.dumps(f2.get('arregla'), ensure_ascii=False)}")
            r = en_llano(f2, problemas)
            if r is not NO_CORRIO and r is not None:
                problemas.append(f"faseEnLlano(fase F2) sin bloque devolvió {json.dumps(r, ensure_ascii=False)[:120]}, no null: "
                                 "la tarjeta y la ventana dejarían un hueco")
        if f1 is not None:
            revisa_llano(en_llano(f1, problemas), "F1", PRIMERA, PRIMERA, FILAS_F1, problemas)
    inf.escenario("A phase without the block shows as today", problemas)

    # 3b · Añadido: una fase sin las claves «en_llano» ni «arregla» (datos de un tablero anterior) también da null sin lanzar
    problemas = []
    vieja = {"id": "F9", "nombre": "Antigua", "version": "0.9.0", "listo_cuando": "P90 pasa", "piezas": ["P90"]}
    r = en_llano(vieja, problemas)
    if r is not NO_CORRIO and r is not None:
        problemas.append(f"faseEnLlano de una fase sin «en_llano» ni «arregla» devolvió {json.dumps(r, ensure_ascii=False)[:120]}, no null")
    inf.escenario("A phase without the block shows as today (no keys in the data)", problemas)

    # 4 · Una tabla que nombra una pieza que la fase no tiene se ve igual: la fila de P03 en el bloque de F1 llega tal
    #     cual, en su sitio; el párrafo, la primera frase y las otras filas no cambian, y P03 no pasa a ser de F1
    problemas = []
    d = pestana(*generar([DOS_FRASES, CON_AJENA]), problemas)
    if d is not None:
        f = fase_de(d, "F1", problemas)
        if f is not None:
            filas = FILAS_F1 + [AJENA]
            revisa_datos(f, "F1", PARRAFO, filas, problemas)
            igual(problemas, "las piezas de la fase F1", f.get("piezas"), ["P01", "P02"])
            revisa_llano(en_llano(f, problemas), "F1", PRIMERA, PARRAFO, filas, problemas)
    inf.escenario("A table that names a piece the phase does not have still shows", problemas)


flujo.principal("P40", escenarios)
