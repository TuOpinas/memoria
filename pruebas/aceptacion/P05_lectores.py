#!/usr/bin/env python3
"""P05 · Readers and the design template (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-23, en el plan).

- A design from the template is read. Dado a design made from the template, with «Grupo» in «Datos», «Entidades» in
  «Conceptos» and «Conecta con» in «Componentes» and «Infraestructura», Cuando it is read, Entonces it returns the
  objective, the steps of «Cómo funciona», the rules, and each entity, concept, component and infrastructure piece with
  its links.
- A plan and its last follow-up are read. Dado a plan made from the template and a follow-up with two entries, Cuando
  they are read, Entonces it returns the phases, the pieces with their scenarios, and each piece's state and the date
  from the newest entry only.
- A table that cannot be read is named, not a crash. Dado a design without one of its columns or sections, Cuando it is
  read, Entonces the reader names what is missing and returns the rest.

Por la única entrada de las cuatro piezas de F2: el generador del tablero sobre una copia de P05_muestra/, y lo que
escribe en desarrollo/ventas--portal.json. Cómo se monta cada escenario está en RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P05_lectores.py (0 pasa, 1 falla, 2 no se montó).
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


def revisa_diseno(d, problemas, partes=("objetivo", "como_funciona", "reglas", "entidades", "conceptos", "componentes",
                                        "infraestructura")):
    """Compara diseno.<parte> con lo que dice la muestra, parte por parte."""
    dis = saca(d, "diseno")
    if not isinstance(dis, dict):
        problemas.append(f"«diseno» es {json.dumps(dis)}, no lo leído del diseño")
        return
    if "objetivo" in partes:
        igual(problemas, "el objetivo", dis.get("objetivo"), OBJETIVO)
    if "como_funciona" in partes:
        igual(problemas, "«Cómo funciona»", dis.get("como_funciona"), PASOS)
    if "reglas" in partes:
        igual(problemas, "las reglas", dis.get("reglas"), REGLAS)
    if "entidades" in partes:
        vistas = por_clave(dis.get("entidades"), "nombre")
        for nombre, (grupo, relaciones) in ENTIDADES.items():
            e = vistas.get(nombre)
            if e is None:
                problemas.append(f"falta la entidad «{nombre}»")
                continue
            igual(problemas, f"el grupo de «{nombre}»", e.get("grupo"), grupo)
            igual(problemas, f"las relaciones de «{nombre}»", e.get("relaciones"), relaciones)
    if "conceptos" in partes:
        vistos = por_clave(dis.get("conceptos"), "nombre")
        for nombre, entidades in CONCEPTOS.items():
            if nombre not in vistos:
                problemas.append(f"falta el concepto «{nombre}»")
            else:
                igual(problemas, f"las entidades del concepto «{nombre}»", vistos[nombre].get("entidades"), entidades)
    for parte, filas in (("componentes", COMPONENTES), ("infraestructura", INFRAESTRUCTURA)):
        if parte not in partes:
            continue
        vistas = por_clave(dis.get(parte), "nombre")
        for nombre, conecta in filas.items():
            if nombre not in vistas:
                problemas.append(f"falta «{nombre}» en {parte}")
            else:
                igual(problemas, f"«Conecta con» de «{nombre}» ({parte})", vistas[nombre].get("conecta_con"), conecta)


def escenarios(inf):
    # 1 · Se lee un diseño hecho con la plantilla (con «Grupo», «Entidades» y «Conecta con»)
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        revisa_diseno(d, problemas)
    inf.escenario("Se lee un diseño hecho con la plantilla", problemas)

    # 2 · Se leen un plan y su último seguimiento: fases, piezas con sus escenarios, y el estado y la fecha de cada
    #     pieza, de la entrada más reciente y solo de ella (P03 está solo en la anterior)
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        igual(problemas, "las fases y sus piezas", [(saca(f, "id"), saca(f, "piezas")) for f in saca(d, "plan", "fases") or []],
              [(f[0], f[6]) for f in FASES])
        vistas = por_clave(saca(d, "plan", "piezas"), "id")
        igual(problemas, "las piezas del plan", sorted(vistas), sorted(PIEZAS))
        for pid, (_, _, _, _, escs) in PIEZAS.items():
            p = vistas.get(pid, {})
            igual(problemas, f"los títulos de los escenarios de {pid}",
                  [saca(e, "titulo") for e in p.get("escenarios") or []], [t for t, _ in escs])
        for pid, estado in ULTIMO.items():
            p = vistas.get(pid, {})
            igual(problemas, f"el estado de {pid}", p.get("estado"), estado)
            igual(problemas, f"la fecha del estado de {pid}", p.get("fecha_estado"), FECHA_ULTIMO)
        p3 = vistas.get("P03", {})
        if p3.get("estado") == "en curso" or p3.get("fecha_estado") == FECHA_ANTERIOR:
            problemas.append(f"P03 lleva el estado de la entrada anterior ({FECHA_ANTERIOR}), que no es la más reciente")
    inf.escenario("Se leen un plan y su último seguimiento", problemas)

    # 3 · Una tabla que no se puede leer se nombra, no rompe: el diseño sin una columna, y sin una sección
    sin_grupo = [(DISENO, "| Entidad | Grupo | Qué es | Se relaciona con |\n|---|---|---|---|",
                  "| Entidad | Qué es | Se relaciona con |\n|---|---|---|")]
    sin_grupo += [(DISENO, f"| {n} | {g} |", f"| {n} |") for n, (g, _) in ENTIDADES.items()]
    sin_reglas = [(DISENO, "## Reglas\nLas reglas de negocio que el producto tiene que cumplir.\n\n| Regla | Excepción |\n"
                           "|---|---|\n| Un pedido se paga antes de prepararse | Los clientes frecuentes pagan al recibir |\n"
                           "| Un producto agotado no se puede pedir | Ninguna |\n\n", "")]
    for que, falta, cambios, resto in (
            ("sin la columna «Grupo» de «Datos»", "Grupo", sin_grupo,
             ("objetivo", "como_funciona", "reglas", "conceptos", "componentes", "infraestructura")),
            ("sin la sección «Reglas»", "Reglas", sin_reglas,
             ("objetivo", "como_funciona", "entidades", "conceptos", "componentes", "infraestructura"))):
        problemas = []
        d = pestana(*generar(cambios), problemas)
        if d is not None:
            if not any(falta in t for t in avisos(d)):
                problemas.append(f"ningún aviso nombra «{falta}»: avisos = {json.dumps(avisos(d), ensure_ascii=False)}")
            revisa_diseno(d, problemas, resto)
        inf.escenario(f"Una tabla que no se puede leer se nombra, no rompe ({que})", problemas)


flujo.principal("P05", escenarios)
