#!/usr/bin/env python3
"""P08 · Board's Desarrollo tab: summary and plan (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-23, en el plan).

Los siete escenarios de «Hecha cuando», uno por uno: el resumen y el plan como tablero, el detalle de una fase, el de
una pieza, la fecha de cada fuente, sin seguimiento, con la tabla de piezas ilegible, y la marca «Desarrollo».

Por la única entrada de las cuatro piezas de F2: el generador del tablero sobre una copia de P05_muestra/, y lo que
escribe en desarrollo/ventas--portal.json y en proyectos/. Lo que solo se ve en pantalla (columnas, tarjetas, el clic que
abre el detalle, la marca dondequiera que se lista el proyecto) queda para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P08_pestana_desarrollo.py (0 pasa, 1 falla, 2 no se montó).
"""
import atexit, json, pathlib, shutil, subprocess, sys, tempfile

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import flujo  # noqa: E402  (solo Informe, principal y Montaje: la línea «RESULTADO:» y la salida 2 si no se monta)

REPO = AQUI.parents[1]
GENERADOR = REPO / "plugins" / "memoria" / "skills" / "tablero" / "generar_vista.py"
MUESTRA = AQUI / "P05_muestra"
PORTAL, CAMPANA = "ventas--portal", "ventas--campana"   # con la sección «## Desarrollo» y sin ella
PROYECTO_MD = "ventas/portal/proyecto.md"
DISENO = "ventas/portal/entregables/diseno.md"
PLAN = "ventas/portal/entregables/plan.md"
SEGUIMIENTO = "ventas/portal/entregables/seguimiento.md"
DETALLE = "ventas/portal/entregables/datos-detalle.md"


def generar(cambios=(), borrar=()):
    """Copia la raíz de muestra (P05_muestra/) a una carpeta temporal, le hace los cambios del escenario y corre sobre ella
    el generador del tablero, desde la raíz del repositorio. cambios: (ruta, texto que está una sola vez, texto nuevo).
    Devuelve (código de salida, lo que dijo, carpeta de salida)."""
    if not GENERADOR.is_file():
        raise flujo.Montaje(f"no está el generador del tablero en {GENERADOR}")
    if not (MUESTRA / "guia.md").is_file():
        raise flujo.Montaje(f"no está la raíz de muestra en {MUESTRA}")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="aceptacion-f2-"))
    atexit.register(shutil.rmtree, tmp, True)
    raiz = tmp / "raiz"
    shutil.copytree(MUESTRA, raiz)
    for ruta, viejo, nuevo in cambios:
        p = raiz / ruta
        texto = p.read_text(encoding="utf-8")
        if texto.count(viejo) != 1:
            raise flujo.Montaje(f"{ruta} de la muestra no tiene una sola vez «{viejo[:60]}»")
        p.write_text(texto.replace(viejo, nuevo), encoding="utf-8")
    for ruta in borrar:
        (raiz / ruta).unlink()
    sal = tmp / "salida"
    try:
        r = subprocess.run([sys.executable, "-I", str(GENERADOR), str(raiz), str(sal)], cwd=str(REPO),
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                           errors="replace", timeout=120)
    except subprocess.TimeoutExpired:
        return None, "pasó de 120 segundos", sal
    return r.returncode, r.stdout, sal


def leer(sal, coleccion, ident):
    p = sal / coleccion / f"{ident}.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def pestana(rc, salida, sal, problemas):
    """El JSON que carga la pestaña Desarrollo del portal (desarrollo/ventas--portal.json), o None con el porqué."""
    if rc != 0:
        ultimas = [l for l in (salida or "").splitlines() if l.strip()][-3:]
        problemas.append(f"el generador del tablero salió con {rc}, no con 0: {' | '.join(ultimas)}")
        return None
    d = leer(sal, "desarrollo", PORTAL)
    if d is None:
        problemas.append(f"el generador no escribió desarrollo/{PORTAL}.json: la pestaña Desarrollo no tiene qué cargar")
    return d


def saca(d, *claves):
    """d[claves[0]][claves[1]]…, o None si falta algo por el camino."""
    for c in claves:
        if isinstance(d, dict) and c in d:
            d = d[c]
        elif isinstance(d, list) and isinstance(c, int) and -len(d) <= c < len(d):
            d = d[c]
        else:
            return None
    return d


def por_clave(lista, clave):
    """{fila[clave]: fila} de una lista de filas (las que no son dict o no tienen la clave se ignoran)."""
    return {f[clave]: f for f in (lista if isinstance(lista, list) else []) if isinstance(f, dict) and clave in f}


def avisos(d, parte=None):
    """Los textos de los avisos, de una parte o de todas."""
    return [a.get("texto", "") for a in (saca(d, "avisos") or []) if isinstance(a, dict)
            and isinstance(a.get("texto", ""), str) and (parte is None or a.get("parte") == parte)]


def igual(problemas, que, visto, esperado):
    if visto != esperado:
        problemas.append(f"{que} es {json.dumps(visto, ensure_ascii=False)}, y la muestra dice "
                         f"{json.dumps(esperado, ensure_ascii=False)}")


# ---------- lo que dice la muestra (P05_muestra/ventas/portal/entregables/) ----------
OBJETIVO = "Que los clientes de la tienda hagan y sigan sus pedidos en línea, sin llamar por teléfono."
PASOS = ["El cliente elige productos del catálogo.", "El cliente confirma su pedido y lo paga.",
         "La tienda prepara el pedido y avisa al cliente."]
REGLAS = [{"regla": "Un pedido se paga antes de prepararse", "excepcion": "Los clientes frecuentes pagan al recibir"},
          {"regla": "Un producto agotado no se puede pedir", "excepcion": "Ninguna"}]
ENTIDADES = {   # nombre: (grupo, relaciones)
    "cliente": ("Ventas", [{"con": "pedido", "tipo": "1:N"}]),
    "pedido": ("Ventas", [{"con": "producto", "tipo": "N:M"}]),
    "producto": ("Catálogo", [{"con": "categoria", "tipo": "N:1"}]),
    "categoria": ("Catálogo", []),
}
CONCEPTOS = {"Pedido": ["pedido", "cliente"], "Cliente frecuente": ["cliente"], "Catálogo": ["producto", "categoria"]}
COMPONENTES = {"Tienda web": ["API"], "API": ["Motor de pagos"], "Motor de pagos": [],
               "Panel interno": ["API", "Motor de pagos"]}
INFRAESTRUCTURA = {"Servidor web": ["Base de datos"], "Base de datos": [], "Dominio": ["Servidor web"]}
FASES = [  # id, nombre, que_podra, version, listo_cuando, en_llano, piezas
    ("F1", "Catálogo", "El cliente ve los productos y sus precios", "1.0.0", "P01 y P02 pasan",
     "El cliente puede ver en línea qué vende la tienda y a qué precio.", ["P01", "P02"]),
    ("F2", "Pedidos", "El cliente pide y paga en línea", "1.1.0", "P03 pasa",
     "El cliente puede hacer y pagar su pedido sin llamar.", ["P03"]),
]
PIEZAS = {  # id: (nombre, fase, entrega, aprobó, [(título, [líneas del texto])])
    "P01": ("Lista de productos", "F1", "La tienda muestra todos los productos con su categoría", "Ana Pérez, 2026-11-12",
            [("Se ven todos los productos", ["Dado un catálogo con tres productos", "Cuando el cliente abre la tienda",
                                             "Entonces ve los tres productos con su categoría"]),
             ("Un catálogo vacío se dice", ["Dado un catálogo sin productos", "Cuando el cliente abre la tienda",
                                            "Entonces la tienda dice que aún no hay productos"])]),
    "P02": ("Precios", "F1", "Cada producto muestra su precio vigente", "Ana Pérez, 2026-11-13",
            [("Cada producto muestra su precio", ["Dado un producto con precio", "Cuando el cliente lo ve",
                                                  "Entonces ve su precio vigente"])]),
    "P03": ("Pedido en línea", "F2", "El cliente arma un pedido y lo paga", "Ana Pérez, 2026-11-14",
            [("Un pedido pagado queda registrado", ["Dado un cliente con dos productos elegidos", "Cuando paga su pedido",
                                                    "Entonces el pedido queda registrado como pagado"])]),
}
# El seguimiento tiene dos entradas: la de arriba (2026-11-20) nombra P01 y P02; la de abajo (2026-11-10), las tres
ULTIMO = {"P01": "unida", "P02": "en curso"}
FECHA_ULTIMO, FECHA_ANTERIOR = "2026-11-20", "2026-11-10"
FECHA_DISENO, FECHA_PLAN = "2026-11-15", "2026-11-18"


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
    inf.escenario("La pestaña muestra el resumen y el plan como tablero", problemas)

    # 2 · Una fase abre su detalle: en llano, qué podrá hacer quién, versión y «Listo cuando»
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        vistas = por_clave(saca(d, "plan", "fases"), "id")
        for fid, nombre, que_podra, version, listo, llano, _ in FASES:
            f = vistas.get(fid)
            if f is None:
                problemas.append(f"no está la fase {fid}")
                continue
            for campo, esperado in (("nombre", nombre), ("en_llano", llano), ("que_podra", que_podra),
                                    ("version", version), ("listo_cuando", listo)):
                igual(problemas, f"«{campo}» de {fid}", f.get(campo), esperado)
    inf.escenario("Una fase abre su detalle", problemas)

    # 3 · Una pieza abre su detalle: qué entrega, sus escenarios y quién los aprobó
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        vistas = por_clave(saca(d, "plan", "piezas"), "id")
        for pid, (nombre, fase, entrega, aprobo, escs) in PIEZAS.items():
            p = vistas.get(pid)
            if p is None:
                problemas.append(f"no está la pieza {pid}")
                continue
            for campo, esperado in (("nombre", nombre), ("fase", fase), ("entrega", entrega), ("aprobo", aprobo)):
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
        for parte, ruta, campo, fecha in (("diseno", DISENO, "actualizado", FECHA_DISENO),
                                          ("plan", PLAN, "actualizado", FECHA_PLAN),
                                          ("seguimiento", SEGUIMIENTO, "fecha", FECHA_ULTIMO)):
            f = saca(d, "fuentes", parte)
            if not isinstance(f, dict):
                problemas.append(f"«fuentes.{parte}» es {json.dumps(f)}")
                continue
            igual(problemas, f"la fecha de «fuentes.{parte}»", f.get(campo), fecha)
            if not str(f.get("ruta", "")).endswith(ruta):
                problemas.append(f"la ruta de «fuentes.{parte}» es {json.dumps(f.get('ruta'), ensure_ascii=False)}, no {ruta}")
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
