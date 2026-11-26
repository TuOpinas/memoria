#!/usr/bin/env python3
"""P26 · The plan by state (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-25, en el plan).

- States are told apart. Dado a follow-up that gives one piece as finished, one as under way and one with no state,
  Cuando the plan opens, Entonces the finished one is dimmed with a check and folded at the end of its column, the one
  under way goes first and highlighted, and the other is drawn as today.
- The phase says what is left. Dado a phase with hours in its pieces and some finished, Cuando the plan opens, Entonces
  its header says the hours left of the total and the pieces finished of the total, and a closed phase is folded.
- A pending decision reads as one. Dado a piece with text in «Para antes», Cuando the plan opens, Entonces its mark says
  «decisión pendiente» and its window «Decisión pendiente antes de construirla: …».
- The phase's close is seen. Dado a phase with hours for its close in the plan, Cuando the plan opens, Entonces its
  column ends with a «Cierre de fase» line with those hours, and the phase's total counts them.
- A technical piece is marked. Dado a piece whose «Hecha cuando» says it is technical, with no scenarios, Cuando the
  plan opens, Entonces its card carries «técnica».
- Without a follow-up, as today. Dado a project with no follow-up, Cuando the plan opens, Entonces every piece is drawn
  as in 1.29.1, with the warning it already gives.

Por las dos entradas de F5: el generador del tablero sobre la raíz de muestra de P05_lectores.py (plan.piezas[].grupo y
tecnica; plan.fases[].horas_cierre, horas_total, piezas_total, piezas_hechas y horas_faltan), y la página del tablero
(vista.html) leída como texto, para la marca «técnica» (data-marca="tecnica"), los textos de la decisión pendiente y
«Cierre de fase». El atenuado, la palomita, el plegado, el orden en la columna, lo que dice la cabecera de la fase y que
la línea «Cierre de fase» salga al pie de la columna con sus horas quedan para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P26_plan_por_estado.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P05_lectores import *  # noqa: E402,F401,F403  (la muestra, cómo se corre el generador y lo que dice la muestra: una sola copia)

VISTA = REPO / "plugins" / "memoria" / "skills" / "tablero" / "vista.html"
MARCA_TECNICA = 'data-marca="tecnica"'
PENDIENTE, VENTANA_PENDIENTE = "decisión pendiente", "Decisión pendiente antes de construirla:"
CIERRE = "Cierre de fase"

# «Horas» y «Para antes» en «Piezas», como en P22
CABECERA_PIEZAS = ("| Pieza | Fase | Qué entrega |\n|---|---|---|",
                   "| Pieza | Fase | Qué entrega | Horas | Para antes |\n|---|---|---|---|---|")
FILA = {"P01": "| P01 · Lista de productos | F1 | La tienda muestra todos los productos con su categoría |",
        "P02": "| P02 · Precios | F1 | Cada producto muestra su precio vigente |",
        "P03": "| P03 · Pedido en línea | F2 | El cliente arma un pedido y lo paga |"}
PARADA = "Que Ana Pérez apruebe la lista de precios"

# «Horas de cierre» al final de «Fases»; y el estado de cada fase
CABECERA_FASES = ("| Fase | Qué podrá hacer quién | Versión | Listo cuando | Estado |\n|---|---|---|---|---|",
                  "| Fase | Qué podrá hacer quién | Versión | Listo cuando | Estado | Horas de cierre |\n|---|---|---|---|---|---|")
FASE = {"F1": "| F1 · Catálogo | El cliente ve los productos y sus precios | 1.0.0 | P01 y P02 pasan | en curso |",
        "F2": "| F2 · Pedidos | El cliente pide y paga en línea | 1.1.0 | P03 pasa | pendiente |"}

ULTIMA = "## 2026-11-20\n| Pieza | Estado |\n|---|---|\n| P01 | unida |\n| P02 | en curso |\n"
# La última entrada con P01 entregada: la muestra de P05 la da «unida», que en 1.30.0 es en curso, no hecha
ENTREGADA = (SEGUIMIENTO, ULTIMA, ULTIMA.replace("| P01 | unida |", "| P01 | Entregada |"))
SIN_SEGUIMIENTO = ([(PROYECTO_MD, f"Seguimiento: {SEGUIMIENTO}", "Seguimiento: por crear")], [SEGUIMIENTO])
P03_ESCENARIO = ("- **Un pedido pagado queda registrado**\n  Dado un cliente con dos productos elegidos\n"
                 "  Cuando paga su pedido\n  Entonces el pedido queda registrado como pagado\n")


def piezas_con(celdas):
    """«Horas» y «Para antes» detrás de «Qué entrega»: celdas = {pieza: (horas, para antes)}."""
    return [(PLAN,) + CABECERA_PIEZAS] + [(PLAN, FILA[p], f"{FILA[p]} {h} | {pa} |") for p, (h, pa) in celdas.items()]


def fases_con(cierre=None, estados=None):
    """La tabla «Fases» con la columna «Horas de cierre» (cierre = {fase: celda}) y/o otro estado (estados = {fase: estado})."""
    cambios = [(PLAN,) + CABECERA_FASES] if cierre is not None else []
    for f, fila in FASE.items():
        nueva = fila
        if estados and f in estados:
            nueva = nueva.rsplit("|", 2)[0] + f"| {estados[f]} |"
        if cierre is not None:
            nueva += f" {cierre[f]} |"
        if nueva != fila:
            cambios.append((PLAN, fila, nueva))
    return cambios


def pagina():
    if not VISTA.is_file():
        raise flujo.Montaje(f"no está la página del tablero en {VISTA}")
    return VISTA.read_text(encoding="utf-8", errors="replace")


def num_igual(problemas, que, visto, esperado):
    bien = visto is None if esperado is None else (
        isinstance(visto, (int, float)) and not isinstance(visto, bool) and abs(visto - esperado) < 1e-9)
    if not bien:
        problemas.append(f"{que} es {json.dumps(visto)}, y la muestra dice {json.dumps(esperado)}")


def clave(problemas, que, fila, k, esperado, numero=False):
    """fila[k] tiene que estar (también con null) y valer esperado."""
    if not isinstance(fila, dict):
        problemas.append(f"falta {que}")
    elif k not in fila:
        problemas.append(f"{que} no trae «{k}» (tiene que ser {json.dumps(esperado, ensure_ascii=False)})")
    elif numero:
        num_igual(problemas, f"«{k}» de {que}", fila[k], esperado)
    else:
        igual(problemas, f"«{k}» de {que}", fila[k], esperado)


def grupos(d, problemas, esperado):
    vistas = por_clave(saca(d, "plan", "piezas"), "id")
    for pid, g in esperado.items():
        clave(problemas, f"la pieza {pid}", vistas.get(pid), "grupo", g)


def fases(d, problemas, esperado):
    """esperado = {fase: {clave: valor}}; las de horas se comparan como números."""
    vistas = por_clave(saca(d, "plan", "fases"), "id")
    for fid, claves in esperado.items():
        for k, v in claves.items():
            clave(problemas, f"la fase {fid}", vistas.get(fid), k, v, numero=k.startswith("horas"))


def sin_aviso_de_cierre(d, problemas):
    malos = [t for t in avisos(d, "plan") if "Horas de cierre" in t]
    if malos:
        problemas.append(f"sin la columna, un aviso del plan menciona «Horas de cierre»: {json.dumps(malos, ensure_ascii=False)}")


def escenarios(inf):
    # 1 · Los estados se distinguen: P01 «Entregada» (hecha), P02 «en curso» y P03 sin estado en la última entrada
    #     (pendiente)
    problemas = []
    d = pestana(*generar([ENTREGADA]), problemas)
    if d is not None:
        grupos(d, problemas, {"P01": "hecha", "P02": "en_curso", "P03": "pendiente"})
    inf.escenario("Los estados se distinguen", problemas)

    # 1b · Añadido: «Unida» (aún no entregada) y «Revertida» son en curso, sin distinguir mayúsculas; un estado que no
    #      es de esos («pendiente») es pendiente. Y «ENTREGADA (1.0.0)» es hecha
    problemas = []
    otra = "## 2026-11-20\n| Pieza | Estado |\n|---|---|\n| P01 | UNIDA |\n| P02 | revertida |\n| P03 | pendiente |\n"
    d = pestana(*generar([(SEGUIMIENTO, ULTIMA, otra)]), problemas)
    if d is not None:
        grupos(d, problemas, {"P01": "en_curso", "P02": "en_curso", "P03": "pendiente"})
    otra = ULTIMA.replace("| P01 | unida |", "| P01 | ENTREGADA (1.0.0) |")
    d = pestana(*generar([(SEGUIMIENTO, ULTIMA, otra)]), problemas)
    if d is not None:
        grupos(d, problemas, {"P01": "hecha"})
    inf.escenario("Los estados se distinguen (unida, revertida, otro estado y entregada en mayúsculas)", problemas)

    # 2 · La fase dice lo que le falta: P01 0.5 h (entregada: hecha), P02 0.75 h (en curso), P03 1.5 h. Sin «Horas de
    #     cierre». F1: 1.25 de total, faltan 0.75, 1 de 2 piezas hechas; F2: 1.5, faltan 1.5, 0 de 1. Con F1 cerrada,
    #     le faltan 0. Añadido: con P01 solo «unida» no está hecha: F1 0 de 2 y faltan 1.25
    problemas = []
    horas = piezas_con({"P01": ("0.5", ""), "P02": ("0.75", ""), "P03": ("1.5", "")})
    d = pestana(*generar(horas + [ENTREGADA]), problemas)
    if d is not None:
        fases(d, problemas, {
            "F1": {"horas": 1.25, "horas_cierre": None, "horas_total": 1.25, "horas_faltan": 0.75, "piezas_total": 2,
                   "piezas_hechas": 1},
            "F2": {"horas": 1.5, "horas_cierre": None, "horas_total": 1.5, "horas_faltan": 1.5, "piezas_total": 1,
                   "piezas_hechas": 0}})
        sin_aviso_de_cierre(d, problemas)
    d = pestana(*generar(horas + [ENTREGADA] + fases_con(estados={"F1": "cerrada", "F2": "en curso"})), problemas)
    if d is not None:
        fases(d, problemas, {"F1": {"horas_total": 1.25, "horas_faltan": 0}, "F2": {"horas_faltan": 1.5}})
    d = pestana(*generar(horas), problemas)
    if d is not None:
        fases(d, problemas, {"F1": {"horas_faltan": 1.25, "piezas_hechas": 0}})
    inf.escenario("La fase dice lo que le falta", problemas)

    # 2b · Añadido: sin horas en ninguna parte, el total y lo que falta son null, y las piezas se cuentan igual
    problemas = []
    d = pestana(*generar([ENTREGADA]), problemas)
    if d is not None:
        fases(d, problemas, {
            "F1": {"horas_total": None, "horas_faltan": None, "piezas_total": 2, "piezas_hechas": 1},
            "F2": {"horas_total": None, "horas_faltan": None, "piezas_total": 1, "piezas_hechas": 0}})
        sin_aviso_de_cierre(d, problemas)
    inf.escenario("La fase dice lo que le falta (sin horas)", problemas)

    # 3 · Una decisión pendiente se lee como tal: P02 lleva texto en «Para antes» y sigue llegando; la página trae el
    #     rótulo «decisión pendiente» y el texto de la ventana
    problemas = []
    d = pestana(*generar(piezas_con({"P01": ("", ""), "P02": ("", PARADA), "P03": ("", "")})), problemas)
    if d is not None:
        vistas = por_clave(saca(d, "plan", "piezas"), "id")
        for pid, pa in (("P01", ""), ("P02", PARADA), ("P03", "")):
            clave(problemas, f"la pieza {pid}", vistas.get(pid), "para_antes", pa)
    texto = pagina()
    for cadena, que in ((PENDIENTE, "el rótulo de la marca"), (VENTANA_PENDIENTE, "el texto de la ventana")):
        if cadena not in texto:
            problemas.append(f"la página del tablero no tiene «{cadena}» ({que})")
    inf.escenario("Una decisión pendiente se lee como tal", problemas)

    # 4 · El cierre de la fase se ve: «Horas de cierre» F1 «0,5» y F2 «1.5 h», con las horas de las piezas de 2 y P01
    #     entregada. F1: 1.25 + 0.5 = 1.75, faltan 0.75 + 0.5 = 1.25; F2: 1.5 + 1.5 = 3, faltan 3. La página trae
    #     «Cierre de fase»
    problemas = []
    d = pestana(*generar(horas + [ENTREGADA] + fases_con(cierre={"F1": "0,5", "F2": "1.5 h"})), problemas)
    if d is not None:
        fases(d, problemas, {
            "F1": {"horas": 1.25, "horas_cierre": 0.5, "horas_total": 1.75, "horas_faltan": 1.25},
            "F2": {"horas": 1.5, "horas_cierre": 1.5, "horas_total": 3, "horas_faltan": 3}})
    if CIERRE not in pagina():
        problemas.append(f"la página del tablero no tiene «{CIERRE}»: la columna no acaba con la línea del cierre")
    inf.escenario("El cierre de la fase se ve", problemas)

    # 4b · Añadido: sin horas en las piezas, la celda vacía es null y «1» cuenta solo: F1 todo null; F2 cierre 1, total 1,
    #      faltan 1
    problemas = []
    d = pestana(*generar(fases_con(cierre={"F1": "", "F2": "1"})), problemas)
    if d is not None:
        fases(d, problemas, {
            "F1": {"horas": None, "horas_cierre": None, "horas_total": None, "horas_faltan": None},
            "F2": {"horas": None, "horas_cierre": 1, "horas_total": 1, "horas_faltan": 1}})
    inf.escenario("El cierre de la fase se ve (celda vacía, y sin horas en las piezas)", problemas)

    # 5 · Una pieza técnica se marca: el bloque de P03 en «Hecha cuando» dice «Pieza técnica, sin escenarios» (con
    #     mayúscula) en lugar de su escenario; P01 y P02 no. La página trae la marca de la tarjeta
    problemas = []
    d = pestana(*generar([(PLAN, P03_ESCENARIO, "Pieza técnica, sin escenarios.\n")]), problemas)
    if d is not None:
        vistas = por_clave(saca(d, "plan", "piezas"), "id")
        for pid, t in (("P01", False), ("P02", False), ("P03", True)):
            clave(problemas, f"la pieza {pid}", vistas.get(pid), "tecnica", t)
    texto = pagina()
    if MARCA_TECNICA not in texto:
        problemas.append(f"la página del tablero no tiene «{MARCA_TECNICA}»: la tarjeta no lleva el rótulo «técnica»")
    inf.escenario("Una pieza técnica se marca", problemas)

    # 6 · Sin seguimiento, como hoy: «Seguimiento: por crear» y sin el archivo. Las piezas sin estado y con grupo null,
    #     las fases con sus piezas, piezas_hechas y horas_faltan null, y el aviso del seguimiento que ya sale
    problemas = []
    d = pestana(*generar(*SIN_SEGUIMIENTO), problemas)
    if d is not None:
        igual(problemas, "las fases y sus piezas", [(saca(f, "id"), saca(f, "piezas")) for f in saca(d, "plan", "fases") or []],
              [(f[0], f[6]) for f in FASES])
        vistas = por_clave(saca(d, "plan", "piezas"), "id")
        igual(problemas, "las piezas del plan", sorted(vistas), sorted(PIEZAS))
        for pid, p in vistas.items():
            if p.get("estado") is not None or p.get("fecha_estado") is not None:
                problemas.append(f"{pid} lleva estado sin haber seguimiento: {p.get('estado')!r}, {p.get('fecha_estado')!r}")
        grupos(d, problemas, {p: None for p in PIEZAS})
        fases(d, problemas, {"F1": {"piezas_total": 2, "piezas_hechas": None, "horas_faltan": None},
                             "F2": {"piezas_total": 1, "piezas_hechas": None, "horas_faltan": None}})
        if not avisos(d, "seguimiento"):
            problemas.append("ningún aviso de la parte «seguimiento» dice que aún no hay seguimiento")
        sin_aviso_de_cierre(d, problemas)
    # Añadido: sin seguimiento pero con horas, lo que falta sigue siendo null (el total, no)
    d = pestana(*generar(horas + SIN_SEGUIMIENTO[0], SIN_SEGUIMIENTO[1]), problemas)
    if d is not None:
        fases(d, problemas, {"F1": {"horas_total": 1.25, "horas_faltan": None}})
    inf.escenario("Sin seguimiento, como hoy", problemas)


flujo.principal("P26", escenarios)
