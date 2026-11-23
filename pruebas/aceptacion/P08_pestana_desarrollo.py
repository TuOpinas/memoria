#!/usr/bin/env python3
"""P08 · Board's Desarrollo tab: summary and plan (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-23, en el plan).

Los siete escenarios de «Hecha cuando», uno por uno: el resumen y el plan como tablero, el detalle de una fase, el de
una pieza, la fecha de cada fuente, sin seguimiento, con la tabla de piezas ilegible, y la marca «Desarrollo».

Por la única entrada de las cuatro piezas de F2: el generador del tablero sobre la raíz de muestra de P05_lectores.py, y lo que
escribe en desarrollo/ventas--portal.json y en proyectos/. Lo que solo se ve en pantalla (columnas, tarjetas, el clic que
abre el detalle, la marca dondequiera que se lista el proyecto) queda para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P08_pestana_desarrollo.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P05_lectores import *  # noqa: E402,F401,F403  (la muestra, cómo se corre el generador y lo que dice la muestra: una sola copia)


def resumen(d, problemas):
    """El resumen de la pestaña: objetivo, «Cómo funciona» en orden y reglas."""
    igual(problemas, "el objetivo", saca(d, "diseno", "objetivo"), OBJETIVO)
    igual(problemas, "«Cómo funciona», en orden", saca(d, "diseno", "como_funciona"), PASOS)
    igual(problemas, "las reglas", saca(d, "diseno", "reglas"), REGLAS)


def escenarios(inf):
    # 1 · La pestaña muestra el resumen y el plan como tablero: una columna por fase, en orden, con sus piezas, y el
    #     estado del último seguimiento y su fecha
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        resumen(d, problemas)
        igual(problemas, "las columnas del tablero (fases en orden, con sus piezas)",
              [(saca(f, "id"), saca(f, "piezas")) for f in saca(d, "plan", "fases") or []], [(f[0], f[6]) for f in FASES])
        vistas = por_clave(saca(d, "plan", "piezas"), "id")
        for pid in PIEZAS:
            if pid not in vistas:
                problemas.append(f"no hay tarjeta de {pid}")
        for pid, estado in ULTIMO.items():
            igual(problemas, f"el estado de la tarjeta de {pid}", saca(vistas, pid, "estado"), estado)
        igual(problemas, "la fecha del seguimiento", saca(d, "fuentes", "seguimiento", "fecha"), FECHA_ULTIMO)
        if avisos(d, "plan"):   # con el plan entero no hay nada que avisar de él (lo contrario, en el escenario 6)
            problemas.append(f"hay avisos del plan con el plan entero: {json.dumps(avisos(d, 'plan'), ensure_ascii=False)}")
    inf.escenario("La pestaña muestra el resumen y el plan como tablero", problemas)

    # 2 · Una fase abre su detalle: en llano, qué podrá hacer quién, versión y «Listo cuando»
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        vistas = por_clave(saca(d, "plan", "fases"), "id")
        for fid, _, que_podra, version, listo, llano, _ in FASES:
            f = vistas.get(fid)
            if f is None:
                problemas.append(f"no está la fase {fid}")
                continue
            for campo, esperado in (("que_podra", que_podra), ("version", version), ("listo_cuando", listo)):
                igual(problemas, f"«{campo}» de {fid}", f.get(campo), esperado)
            if not isinstance(f.get("en_llano"), str) or llano not in f["en_llano"]:   # la frase; puede traer más
                problemas.append(f"«en_llano» de {fid} no trae «{llano}»")
    inf.escenario("Una fase abre su detalle", problemas)

    # 3 · Una pieza abre su detalle: qué entrega, sus escenarios y quién los aprobó
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        vistas = por_clave(saca(d, "plan", "piezas"), "id")
        for pid, (_, _, entrega, aprobo, escs) in PIEZAS.items():
            p = vistas.get(pid)
            if p is None:
                problemas.append(f"no está la pieza {pid}")
                continue
            for campo, esperado in (("entrega", entrega), ("aprobo", aprobo)):
                igual(problemas, f"«{campo}» de {pid}", p.get(campo), esperado)
            vistos = p.get("escenarios") or []
            igual(problemas, f"los títulos de los escenarios de {pid}", [saca(e, "titulo") for e in vistos],
                  [t for t, _ in escs])
            for (titulo, lineas), e in zip(escs, vistos):
                texto = saca(e, "texto") or ""
                for linea in lineas:
                    if not isinstance(texto, str) or linea not in texto:
                        problemas.append(f"el texto del escenario «{titulo}» de {pid} no trae «{linea}»")
    inf.escenario("Una pieza abre su detalle", problemas)

    # 4 · Cada fuente dice su fecha: la del diseño, la del plan y la del seguimiento
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        for parte, campo, fecha in (("diseno", "actualizado", FECHA_DISENO), ("plan", "actualizado", FECHA_PLAN),
                                    ("seguimiento", "fecha", FECHA_ULTIMO)):
            f = saca(d, "fuentes", parte)
            if not isinstance(f, dict):
                problemas.append(f"«fuentes.{parte}» es {json.dumps(f)}")
                continue
            igual(problemas, f"la fecha de «fuentes.{parte}»", f.get(campo), fecha)
    inf.escenario("Cada fuente dice su fecha", problemas)

    # 5 · Sin seguimiento el plan se sigue viendo: «Seguimiento: por crear» y sin el archivo
    problemas = []
    d = pestana(*generar([(PROYECTO_MD, f"Seguimiento: {SEGUIMIENTO}", "Seguimiento: por crear")], [SEGUIMIENTO]),
                problemas)
    if d is not None:
        fuentes = saca(d, "fuentes")
        if not isinstance(fuentes, dict) or "seguimiento" not in fuentes or fuentes["seguimiento"] is not None:
            problemas.append(f"«fuentes.seguimiento» no es null: {json.dumps(saca(fuentes, 'seguimiento'), ensure_ascii=False)}")
        vistas = por_clave(saca(d, "plan", "piezas"), "id")
        igual(problemas, "las piezas del plan", sorted(vistas), sorted(PIEZAS))
        igual(problemas, "las fases del plan", [saca(f, "id") for f in saca(d, "plan", "fases") or []], [f[0] for f in FASES])
        for pid, p in vistas.items():
            if p.get("estado") is not None or p.get("fecha_estado") is not None:
                problemas.append(f"{pid} lleva estado sin haber seguimiento: {p.get('estado')!r}, {p.get('fecha_estado')!r}")
        if not avisos(d, "seguimiento"):
            problemas.append("ningún aviso de la parte «seguimiento» dice que aún no hay seguimiento")
    inf.escenario("Sin seguimiento el plan se sigue viendo", problemas)

    # 6 · Lo que no se puede leer se dice, y lo demás se pinta: la tabla de piezas del plan, ilegible
    problemas = []
    tabla = ("| Pieza | Fase | Qué entrega |\n|---|---|---|\n"
             "| P01 · Lista de productos | F1 | La tienda muestra todos los productos con su categoría |\n"
             "| P02 · Precios | F1 | Cada producto muestra su precio vigente |\n"
             "| P03 · Pedido en línea | F2 | El cliente arma un pedido y lo paga |\n")
    d = pestana(*generar([(PLAN, tabla, "Pieza, fase y qué entrega: P01 en F1, P02 en F1 y P03 en F2.\n")]), problemas)
    if d is not None:
        if not avisos(d, "plan"):
            problemas.append(f"ningún aviso de la parte «plan» dice que su tabla de piezas no se pudo leer: "
                             f"avisos = {json.dumps(saca(d, 'avisos'), ensure_ascii=False)}")
        resumen(d, problemas)
    inf.escenario("Lo que no se puede leer se dice, y lo demás se pinta", problemas)

    # 7 · Los proyectos de desarrollo llevan una marca: el portal (con la sección) sí, la campaña (sin ella) no
    problemas = []
    rc, salida, sal = generar()
    if rc != 0:
        problemas.append(f"el generador del tablero salió con {rc}, no con 0")
    else:
        con, sin = leer(sal, "proyectos", PORTAL), leer(sal, "proyectos", CAMPANA)
        if con is None or sin is None:
            problemas.append("faltan proyectos/ventas--portal.json o proyectos/ventas--campana.json")
        else:
            if con.get("desarrollo") is not True:
                problemas.append(f"el portal, con «## Desarrollo», no lleva la marca: «desarrollo» es {con.get('desarrollo')!r}")
            if sin.get("desarrollo", False) is not False:
                problemas.append(f"la campaña, sin la sección, lleva la marca: «desarrollo» es {sin.get('desarrollo')!r}")
        if leer(sal, "desarrollo", PORTAL) is None:
            problemas.append(f"el portal no tiene pestaña: no hay desarrollo/{PORTAL}.json")
        if (sal / "desarrollo" / f"{CAMPANA}.json").exists():
            problemas.append(f"la campaña, sin la sección, tiene pestaña: hay desarrollo/{CAMPANA}.json")
    inf.escenario("Los proyectos de desarrollo llevan una marca", problemas)


flujo.principal("P08", escenarios)
