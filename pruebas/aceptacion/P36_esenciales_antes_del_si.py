#!/usr/bin/env python3
"""P36 · The essential scenarios, walked before each yes (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-27, en el plan).

- An essential scenario is marked. Dado a scenario whose title ends with «(esencial)», Cuando the plan shows on the
  board, Entonces the piece's window marks it as essential.
- The verification gets the essential ones of earlier phases, apart. Dado a plan with F1 delivered and two essential
  scenarios in it, and F2 under way, Cuando the reader lists what F2's verification walks, Entonces it gives F2's
  scenarios and, apart, F1's two essential ones.
- No essential ones, only the phase's. Dado earlier phases with no essential scenario, Cuando the reader lists what the
  verification walks, Entonces it gives only the phase's scenarios.
- A failing essential one stops the yes. Dado a verification report where an essential scenario of an earlier phase
  fails, Cuando the session would ask for the yes, Entonces it does not ask for it and says which one failed; this is
  checked by the verification, not by a test.

Por la interfaz pública de packages/context-core, importada dentro de cada prueba y no arriba del archivo:
context_core.dev_view.read_plan(texto) sobre el plan de la muestra de P05_lectores.py, cambiado en la prueba (cada
pieza trae escenarios: [{"titulo", "esencial"}]), y la función nueva escenarios_a_verificar(plan, fase), que devuelve
{"fase": [títulos], "esenciales": [{"pieza", "titulo"}]}. Y la página del tablero (vista.html) leída como texto, que
marca el escenario esencial con «data-esencial». La marca en pantalla y el cuarto escenario quedan para la
verificación: lo dice RESUMEN.md, y esta prueba lo imprime.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P36_esenciales_antes_del_si.py (0 pasa, 1 falla, 2 no se montó).
"""
import json, pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta ni en packages/context-core
AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from P05_lectores import MUESTRA, PLAN, flujo  # noqa: E402  (la muestra; flujo: Informe, principal y Montaje)

REPO = AQUI.parents[1]
CONTEXT_CORE = REPO / "packages" / "context-core"
VISTA = REPO / "plugins" / "memoria" / "skills" / "tablero" / "vista.html"
MARCA = "data-esencial"
SUFIJO = "(esencial)"

# Los títulos de la muestra, por pieza y fase
T01 = ("Se ven todos los productos", "Un catálogo vacío se dice")   # P01, F1
T02 = ("Cada producto muestra su precio",)                         # P02, F1
T03 = ("Un pedido pagado queda registrado",)                       # P03, F2

# F1 entregada (cerrada) y F2 en curso
FASES = [("| P01 y P02 pasan | en curso |", "| P01 y P02 pasan | cerrada |"),
         ("| P03 pasa | pendiente |", "| P03 pasa | en curso |")]


def esencial(titulo):
    """El cambio que pone « (esencial)» al final del título de un escenario."""
    return (f"- **{titulo}**\n", f"- **{titulo} {SUFIJO}**\n")


def plan_con(cambios):
    texto = MUESTRA[PLAN]
    for viejo, nuevo in cambios:
        if texto.count(viejo) != 1:
            raise flujo.Montaje(f"el plan de la muestra no tiene una sola vez «{viejo.strip()[:60]}»")
        texto = texto.replace(viejo, nuevo)
    return texto


def dev_view():
    """El módulo context_core.dev_view, importado aquí y no arriba del archivo."""
    if not (CONTEXT_CORE / "context_core").is_dir():
        raise flujo.Montaje(f"no está el paquete context_core en {CONTEXT_CORE}")
    if str(CONTEXT_CORE) not in sys.path:
        sys.path.insert(0, str(CONTEXT_CORE))
    import context_core.dev_view as m
    return m


def leer(texto, problemas):
    """El plan leído por read_plan (el primero de lo que devuelve), o None con el porqué."""
    r = dev_view().read_plan(texto)
    plan = r[0] if isinstance(r, tuple) else r
    if not isinstance(plan, dict):
        problemas.append(f"read_plan no devuelve un plan (un objeto): {json.dumps(plan, ensure_ascii=False, default=str)[:200]}")
        return None
    return plan


def limpio(t):
    """El título sin « (esencial)» al final: la prueba acepta que el lector lo deje o lo quite."""
    t = t.strip() if isinstance(t, str) else t
    return t[:-len(SUFIJO)].rstrip() if isinstance(t, str) and t.endswith(SUFIJO) else t


def marcas(plan, problemas, esperado):
    """esperado = {pieza: [(título, esencial)]}: los escenarios de cada pieza traen su título y «esencial» (bool)."""
    piezas = {p.get("id"): p for p in plan.get("piezas") or [] if isinstance(p, dict)}
    for pid, escs in esperado.items():
        vistos = (piezas.get(pid) or {}).get("escenarios")
        if not isinstance(vistos, list):
            problemas.append(f"la pieza {pid} no trae su lista de escenarios")
            continue
        titulos = [limpio(e.get("titulo")) if isinstance(e, dict) else None for e in vistos]
        if titulos != [t for t, _ in escs]:
            problemas.append(f"los títulos de los escenarios de {pid} son {json.dumps(titulos, ensure_ascii=False)}, y la "
                             f"muestra dice {json.dumps([t for t, _ in escs], ensure_ascii=False)}")
            continue
        for e, (t, es) in zip(vistos, escs):
            if "esencial" not in e:
                problemas.append(f"el escenario «{t}» de {pid} no trae «esencial» (tiene que ser {json.dumps(es)})")
            elif e["esencial"] is not es:
                problemas.append(f"«esencial» del escenario «{t}» de {pid} es {json.dumps(e['esencial'])}, y tiene que ser {json.dumps(es)}")


def a_verificar(plan, fase, problemas, fase_esperada, esenciales_esperados):
    """escenarios_a_verificar(plan, fase) da los títulos de la fase y, aparte, los esenciales de las anteriores. Se
    comparan sin orden y sin « (esencial)» al final."""
    m = dev_view()
    f = getattr(m, "escenarios_a_verificar", None)
    if not callable(f):
        problemas.append("context_core.dev_view no tiene la función escenarios_a_verificar")
        return
    r = f(plan, fase)
    if not isinstance(r, dict) or "fase" not in r or "esenciales" not in r:
        problemas.append(f"escenarios_a_verificar(plan, {fase!r}) no da {{\"fase\", \"esenciales\"}}: "
                         f"{json.dumps(r, ensure_ascii=False, default=str)[:300]}")
        return
    vistos_fase = sorted(limpio(t) for t in r["fase"] or [] if isinstance(t, str))
    if vistos_fase != sorted(fase_esperada) or len(r["fase"] or []) != len(fase_esperada):
        problemas.append(f"para {fase}, «fase» es {json.dumps(r['fase'], ensure_ascii=False)}, y tiene que ser "
                         f"{json.dumps(sorted(fase_esperada), ensure_ascii=False)}")
    vistos = sorted((e.get("pieza"), limpio(e.get("titulo"))) for e in r["esenciales"] or [] if isinstance(e, dict))
    if vistos != sorted(esenciales_esperados) or len(r["esenciales"] or []) != len(esenciales_esperados):
        problemas.append(f"para {fase}, «esenciales» es {json.dumps(r['esenciales'], ensure_ascii=False)}, y tiene que ser "
                         f"{json.dumps([{'pieza': p, 'titulo': t} for p, t in sorted(esenciales_esperados)], ensure_ascii=False)}")


def pagina():
    if not VISTA.is_file():
        raise flujo.Montaje(f"no está la página del tablero en {VISTA}")
    return VISTA.read_text(encoding="utf-8", errors="replace")


def escenarios(inf):
    # 1 · Un escenario esencial se marca: el primero de P01 termina en «(esencial)». read_plan lo da esencial y los demás
    #     no; la página marca el escenario con «data-esencial»
    problemas = []
    plan = leer(plan_con([esencial(T01[0])]), problemas)
    if plan is not None:
        marcas(plan, problemas, {"P01": [(T01[0], True), (T01[1], False)], "P02": [(T02[0], False)],
                                 "P03": [(T03[0], False)]})
    if MARCA not in pagina():
        problemas.append(f"la página del tablero no tiene «{MARCA}»: la ventana de la pieza no marca el escenario esencial")
    inf.escenario("An essential scenario is marked", problemas)

    # 1b · Añadido: sin ninguno marcado (la muestra tal cual), todos traen «esencial» false
    problemas = []
    plan = leer(MUESTRA[PLAN], problemas)
    if plan is not None:
        marcas(plan, problemas, {"P01": [(t, False) for t in T01], "P02": [(T02[0], False)], "P03": [(T03[0], False)]})
    inf.escenario("An essential scenario is marked (none marked, none essential)", problemas)

    # 2 · La verificación recibe aparte los esenciales de fases anteriores: F1 cerrada con los dos escenarios de P01
    #     esenciales (P02 no), F2 en curso. Para F2: su escenario y, aparte, los dos de P01
    problemas = []
    plan = leer(plan_con(FASES + [esencial(T01[0]), esencial(T01[1])]), problemas)
    if plan is not None:
        a_verificar(plan, "F2", problemas, list(T03), [("P01", T01[0]), ("P01", T01[1])])
    inf.escenario("The verification gets the essential ones of earlier phases, apart", problemas)

    # 2b · Añadido: un esencial de la propia fase (el de P03) va con los de la fase, no aparte
    problemas = []
    plan = leer(plan_con(FASES + [esencial(T01[0]), esencial(T01[1]), esencial(T03[0])]), problemas)
    if plan is not None:
        a_verificar(plan, "F2", problemas, list(T03), [("P01", T01[0]), ("P01", T01[1])])
    inf.escenario("The verification gets the essential ones of earlier phases, apart (one of the phase's own)", problemas)

    # 3 · Sin esenciales, solo los de la fase: F1 cerrada sin ninguno marcado. Para F2, su escenario y ningún esencial.
    #     Añadido: para F1, que no tiene fases antes, sus tres escenarios y ningún esencial
    problemas = []
    plan = leer(plan_con(FASES), problemas)
    if plan is not None:
        a_verificar(plan, "F2", problemas, list(T03), [])
        a_verificar(plan, "F1", problemas, list(T01 + T02), [])
    inf.escenario("No essential ones, only the phase's", problemas)

    # 4 · Un esencial fallado para el sí: no es de esta prueba
    print(f"  queda para la verificación: P36 · A failing essential one stops the yes (lo comprueba la verificación, "
          f"no una prueba: ver RESUMEN.md)")


flujo.principal("P36", escenarios)
