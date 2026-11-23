#!/usr/bin/env python3
"""P10 · Data model on the tab (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-23, en el plan).

- The entities are drawn with their relations. Dado a design whose «Datos» has entities in two groups with relations
  between them, Cuando the tab's data model opens, Entonces every entity shows inside its group and every relation as a
  line between its two entities.
- An entity shows its detail and its concepts. Dado a `Detalle:` line that points to a document with a row for that
  entity, and two concepts that name it, Cuando the entity is clicked, Entonces that row's detail and the two concepts show.
- A mismatch is said, not hidden. Dado an entity of the design with no row in the detail document, and a row there that
  the design lacks, Cuando the data model opens, Entonces everything is painted and the tab names both.

Por la única entrada de las cuatro piezas de F2: el generador del tablero sobre una copia de P05_muestra/, y lo que
escribe en desarrollo/ventas--portal.json. El dibujo y el clic quedan para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P10_modelo_de_datos.py (0 pasa, 1 falla, 2 no se montó).
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


def escenarios(inf):
    # 1 · Las entidades se dibujan con sus relaciones: cada una en su grupo (dos grupos), cada relación entre dos
    #     entidades que están
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        vistas = por_clave(saca(d, "diseno", "entidades"), "nombre")
        igual(problemas, "las entidades", sorted(vistas), sorted(ENTIDADES))
        for nombre, (grupo, relaciones) in ENTIDADES.items():
            e = vistas.get(nombre, {})
            igual(problemas, f"el grupo de «{nombre}»", e.get("grupo"), grupo)
            igual(problemas, f"las relaciones de «{nombre}»", e.get("relaciones"), relaciones)
        for nombre, e in vistas.items():
            for r in e.get("relaciones") or []:
                if saca(r, "con") not in vistas:
                    problemas.append(f"la relación de «{nombre}» con {saca(r, 'con')!r} no acaba en una entidad")
    inf.escenario("Las entidades se dibujan con sus relaciones", problemas)

    # 2 · Una entidad muestra su detalle y sus conceptos: «cliente» tiene fila en el documento de «Detalle:» y la
    #     nombran dos conceptos (Pedido y Cliente frecuente)
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        cliente = por_clave(saca(d, "diseno", "entidades"), "nombre").get("cliente")
        if cliente is None:
            problemas.append("falta la entidad «cliente»")
        else:
            detalle = cliente.get("detalle")
            esperado = {"Campos": "nombre, correo, teléfono", "Dónde se guarda": "tabla clientes"}
            if not isinstance(detalle, dict) or any(detalle.get(k) != v for k, v in esperado.items()):
                problemas.append(f"el detalle de «cliente» es {json.dumps(detalle, ensure_ascii=False)}, y su fila de "
                                 f"{DETALLE} dice {json.dumps(esperado, ensure_ascii=False)}")
            igual(problemas, "los conceptos de «cliente»", sorted(cliente.get("conceptos") or []),
                  sorted(["Pedido", "Cliente frecuente"]))
    inf.escenario("Una entidad muestra su detalle y sus conceptos", problemas)

    # 3 · Un desajuste se dice, no se esconde: «factura» está en el diseño y no en el detalle; «envio», al revés
    problemas = []
    cambios = [(DISENO, "| categoria | Catálogo | Un grupo de productos | |\n",
                "| categoria | Catálogo | Un grupo de productos | |\n"
                "| factura | Ventas | El comprobante de un pedido | pedido (1:1) |\n"),
               (DETALLE, "| categoria | nombre | tabla categorias |\n",
                "| categoria | nombre | tabla categorias |\n| envio | dirección, fecha | tabla envios |\n")]
    d = pestana(*generar(cambios), problemas)
    if d is not None:
        igual(problemas, "las entidades", sorted(por_clave(saca(d, "diseno", "entidades"), "nombre")),
              sorted(list(ENTIDADES) + ["factura"]))
        datos = avisos(d, "datos")
        de_factura = [i for i, t in enumerate(datos) if "factura" in t]
        de_envio = [i for i, t in enumerate(datos) if "envio" in t]
        if not de_factura:
            problemas.append("ningún aviso de la parte «datos» nombra «factura», la entidad sin detalle")
        if not de_envio:
            problemas.append("ningún aviso de la parte «datos» nombra «envio», la fila que el diseño no tiene")
        if de_factura and de_envio and set(de_factura) == set(de_envio) and len(de_factura) == 1:
            problemas.append("los dos desajustes van en un solo aviso, no en dos")
        if problemas:
            problemas.append(f"avisos = {json.dumps(saca(d, 'avisos'), ensure_ascii=False)}")
    inf.escenario("Un desajuste se dice, no se esconde", problemas)


flujo.principal("P10", escenarios)
