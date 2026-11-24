#!/usr/bin/env python3
"""P21 · Lines that can be followed (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-23, en el plan).

- No line passes over a box. Dado the designs of product-design and plugin-memoria as samples, Cuando their three
  drawings open, Entonces every line runs in right angles and crosses no box but the two it joins.
- A verb sits on a free stretch. Dado a relation with its verb, Cuando the drawing opens, Entonces the verb overlaps no
  box and no other verb.
- Text keeps its size. Dado a drawing wider than the page, Cuando it opens, Entonces it scrolls sideways and its text is
  not drawn smaller than 13 px.
- A long label wraps. Dado a box or a container whose label does not fit one line, Cuando the drawing opens, Entonces
  the label takes a second line; if it still does not fit it is cut and the whole text is in its tooltip.

Por las dos entradas de F5: el generador del tablero sobre la raíz de muestra de P05_lectores.py, con las secciones
«Componentes», «Datos» e «Infraestructura» de las dos muestras de abajo, y la función trazarDesarrollo(diseno) de la
página del tablero (el bloque entre «// >>> trazado» y «// <<< trazado» de vista.html), que se saca como texto y se corre
con node sobre el «diseno» que dejó el generador. El desplazamiento de lado en pantalla queda para la verificación: lo
dice RESUMEN.md.
P19 y P20 importan de aquí cómo se saca y se corre el trazado y las dos muestras; P25, cómo se saca y se corre
un bloque de la página.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P21_lineas_que_se_siguen.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P05_lectores import *  # noqa: E402,F401,F403  (la muestra, cómo se corre el generador y lo que dice la muestra: una sola copia)
import atexit, json, re, shutil, subprocess, tempfile  # noqa: E402

VISTA = REPO / "plugins" / "memoria" / "skills" / "tablero" / "vista.html"
INICIO, FIN = "// >>> trazado", "// <<< trazado"
VISTAS = ("datos", "componentes", "infraestructura")
TOL = 0.5   # px: lo que se perdona al tocar un borde

# ---------- las dos muestras del encargo, tal cual (las secciones que lee el generador) ----------
MUESTRA_PLUGIN = '''## Componentes
| Componente | Qué hace | Dónde vive | Externo | Conecta con |
|---|---|---|---|---|
| Claude | Runs the skills, reads and writes through the person's tools | Anthropic | sí | Start notice and controls · Skills |
| Start notice and controls | The minimum opening on every conversation; asks to open the memory and keeps outputs out of it | TuOpinas/memoria:plugins/memoria/hooks/ | | Session scripts |
| Skills | The method: session, contract, style, deliverable, review, quality, director, board, development and the rest | TuOpinas/memoria:plugins/memoria/skills/ | | Session scripts · Board scripts · Subagents |
| Session scripts | Open, close, permissions, maintenance and migration of a project | TuOpinas/memoria:plugins/memoria/skills/sesion/*.py | | context_core · The folder |
| Board scripts | Generate the board's data, apply its queue, plan the upload and sweep for what sessions forgot | TuOpinas/memoria:plugins/memoria/skills/tablero/*.py | | context_core · The folder · The board |
| context_core | The rules the scripts share, inlined in each one | TuOpinas/memoria:packages/context-core/ | | |
| Subagents | Scenarios, verification in each model, follow-up | TuOpinas/memoria:plugins/memoria/agents/ | | GitHub |
| The folder | The organization's memory in Drive | Google Drive of each organization | sí | |
| The board | The page and its base, per person | Claude artifacts | sí | |
| GitHub | The repository, its checks and the published versions | GitHub | sí | |

**Flujo:** Claude → Skills → Session scripts → The folder

## Datos
| Entidad | Grupo | Qué es | Se relaciona con |
|---|---|---|---|
| Guide | Root | `guia.md`: areas, who is who, house rules; `metodo.md` beside it | |
| Area | Root | `area.md`: its status, priorities and the list of its projects | Guide (vive en) |
| Project | Project | `proyecto.md`: status, objective, scope, next steps, who takes part, development section | Area (vive en) |
| Decision | Project | An entry of `decisiones.md`, with its identifier; never edited | Project (cambia) · Session (en) |
| Session | Project | An entry of `sesiones.md`: what was done, by whom and with which version | Project (cuenta) |
| Deliverable | Project | A document of `entregables/` with its header: state, date, contribution, sources | Project (vive en) |
| Workshop note | Project | A document of `taller/`: work in progress, private to the area | Project (vive en) |
| Source | Project | Material from outside in `fuentes/`, with its inventory | Project (vive en) |
| Board data | Board | The files the board publishes: areas, projects, detail, development, suggestions | Project (lee) · Area (lee) |
| Board queue | Board | What was marked on the board and the marks of closed sessions | Project (cambia) |

**Flujo:** Session → Decision

## Infraestructura
| Pieza | Para qué | Proveedor | Cuenta | Ambiente | Conecta con |
|---|---|---|---|---|---|
| Repository and marketplace | The code, its checks and the published versions | GitHub | TuOpinas | Prod | |
| Acceptance and test checks | The suite and the acceptance tests on every pull request | GitHub | TuOpinas | CI | Repository and marketplace |
| Organization folder | Each organization's memory | Google Drive | of each organization | Prod | |
| Board page and base | One page per person, with its base | Claude | of each person | Prod | Organization folder |
| Board task | The scheduled task that brings the board up to date | Claude | of each person | Prod | Board page and base · Organization folder |
| Test root | Where a candidate is checked before the yes | Google Drive | TuOpinas | Release | |
'''

MUESTRA_PRODUCTO = '''## Componentes
| Componente | En corto | Qué hace | Dónde vive | Externo | Conecta con |
|---|---|---|---|---|---|
| Agent client | an agent of the person | Any agent that speaks the protocol; it calls the handlers on a person's behalf | The person's computer, phone or cloud session | sí | The handlers |
| Access gate | fails closed | Sign-in; who may read and write, fail closed | example/service:app/gate.py, rules.py | | |
| The handlers | open, find, save, close | The four calls the clients make | example/service:app/main.py | | Access gate · File store · The ledger |
| File store | file adapter and locks | The file adapter and the lock per path | example/service:app/files.py, locks.py | | Customer files |
| The ledger | the database | The tables, functions and policies, and the pool | example/service:schema/, app/ledger.py | | |
| Admin site | pages and forms | Pages and forms to set an account up | example/service:app/site.py | | Access gate · The ledger |
| The release | applies with a yes | Summary, release with approval, adopt | example/service:release/ | | The ledger |
| Customer files | its documents | The account's own file storage, where its documents stay | The customer's workspace | sí | |

**Flujo:** Agent client → The handlers → Access gate → The ledger

## Datos
| Entidad | En corto | Grupo | Qué es | Se relaciona con |
|---|---|---|---|---|
| Members | who belongs | People | Who belongs, and which login is which person | |
| Map | the map, and who reads | Map | The map of the account and who reads each place | Members (N:1) |
| Items | the state of each item | Items | Current state of each item | Map (vive en) · Members (N:1) |
| Links | links and context | Items | How items relate, and their context | Items (une) · Map (vive en) |
| Visits | what was read and shown | Ledger | Who worked, what they were shown and what they read | Map (en) · Members (de) |
| Requests | waits for a yes | Ledger | What an agent asked for and waits for a person's yes | Acts (se vuelve) · Items (sobre) · Map (vive en) · Members (espera a) |
| Acts | only added, never edited | Ledger | Every change and its order, never edited | Items (deja) · Map (vive en) · Members (firma) · Visits (en) |
| Labels | per language | Labels | The product's text per language | |

**Flujo:** Requests → Acts → Items

## Infraestructura
| Pieza | En corto | Para qué | Proveedor | Cuenta | Ambiente | Conecta con |
|---|---|---|---|---|---|---|
| app-server | containers | The service and the admin site, one instance | Cloud One | example-prod | Prod | app-db · Files |
| app-db | managed Postgres | PostgreSQL with point-in-time restore, and a daily export kept 90 days | Cloud One | example-prod | Prod | |
| Release, secrets, alerts | build and secret store | Build triggers, secret store, mail alerts | Cloud One | example-prod | Prod | app-server · app-db |
| api.example.com, admin.example.com | DNS | The connector and the admin site | Edge Two | example.com | Prod | app-server |
| CI | throwaway Postgres | A throwaway PostgreSQL that stands in for staging | Code Three | example | CI | |
| Files | the customer's documents | The account's documents, in its own shared storage | Workspace Four | the customer's | Prod | |
'''

MUESTRAS = (("plugin-memoria", MUESTRA_PLUGIN), ("product-design", MUESTRA_PRODUCTO))

# Para el rótulo largo: una caja más en «Componentes» de la muestra de P05, con un nombre de 70 letras
LARGO = "Servicio que concilia cada noche los pagos de la tienda con el banco XY"
CON_LARGO = (DISENO, "| Panel interno | Donde la tienda prepara los pedidos | muestra/portal:panel | API · Motor de pagos |\n",
             "| Panel interno | Donde la tienda prepara los pedidos | muestra/portal:panel | API · Motor de pagos |\n"
             f"| {LARGO} | Cuadra lo cobrado | muestra/portal:conciliacion | Motor de pagos |\n")


# Para P19 y P20, la base de P20 en la muestra de P05. Flujo cliente → pedido → producto; pedido y producto apuntan a categoria, que está fuera: categoria es la base.
# categoria no apunta a nada, así que ninguna línea sale de ella. pedido → producto, con su verbo, es la otra relación
CON_BASE = [(DISENO, "| Lo que un cliente pide de una vez | producto (N:M) |",
             "| Lo que un cliente pide de una vez | producto (lleva) · categoria (de) |"),
            (DISENO, "| Lo que la tienda vende | categoria (N:1) |", "| Lo que la tienda vende | categoria (vive en) |"),
            (DISENO, "\n\nDetalle: ventas/portal/entregables/datos-detalle.md",
             "\n\n**Flujo:** cliente → pedido → producto\n\nDetalle: ventas/portal/entregables/datos-detalle.md")]

def con_muestra(texto):
    """El cambio que pone en el diseño de la muestra de P05 las secciones «Componentes», «Datos» e «Infraestructura» de
    una de las dos muestras, en sus sitios (el documento entero es el «texto que está una sola vez»)."""
    viejo = MUESTRA[DISENO]
    arriba, infra = texto.split("## Infraestructura\n", 1)
    i, j = viejo.index("## Componentes\n"), viejo.index("## Conceptos\n")
    nuevo = viejo[:i] + arriba.rstrip("\n") + "\n\n" + viejo[j:]
    k, m = nuevo.index("## Infraestructura\n"), nuevo.index("## Prototipo\n")
    nuevo = nuevo[:k] + "## Infraestructura\n" + infra.rstrip("\n") + "\n\n" + nuevo[m:]
    return (DISENO, viejo, nuevo)


# ---------- sacar el bloque de la página y correrlo con node ----------
_JS = r'''
const fs = require("fs");
const [bloqueF, nombre, argsF] = process.argv.slice(2);
const salir = (o) => { process.stdout.write(JSON.stringify(o)); };
let f;
try {
  f = new Function(fs.readFileSync(bloqueF, "utf8") + "\n; return " + nombre + ";")();
} catch (e) { salir({ _error: "el bloque no se pudo cargar: " + e }); process.exit(0); }
if (typeof f !== "function") { salir({ _error: "el bloque no define la función " + nombre }); process.exit(0); }
let r;
try { r = f(...JSON.parse(fs.readFileSync(argsF, "utf8"))); }
catch (e) { salir({ _error: nombre + "(...) lanzó: " + e }); process.exit(0); }
salir({ _r: r === undefined ? null : r });
'''


def bloque(problemas, inicio=INICIO, fin=FIN, funcion="trazarDesarrollo"):
    """El texto entre la línea que empieza por «inicio» y la que empieza por «fin» de vista.html, o None con el porqué."""
    if not VISTA.is_file():
        raise flujo.Montaje(f"no está la página del tablero en {VISTA}")
    lineas = VISTA.read_text(encoding="utf-8", errors="replace").split("\n")
    ini = [i for i, l in enumerate(lineas) if l.lstrip().startswith(inicio)]
    fi = [i for i, l in enumerate(lineas) if l.lstrip().startswith(fin)]
    if len(ini) != 1 or len(fi) != 1 or fi[0] <= ini[0]:
        problemas.append(f"la página del tablero no trae un bloque entre una línea «{inicio}» y otra «{fin}» "
                         f"(hay {len(ini)} de inicio y {len(fi)} de fin): no hay {funcion} que correr")
        return None
    return "\n".join(lineas[ini[0] + 1:fi[0]])


def correr(inicio, fin, funcion, args, problemas):
    """Saca de la página el bloque entre «inicio» y «fin», lo corre con node y devuelve lo que da funcion(*args),
    o None con el porqué en problemas. Sin node en el PATH, la prueba no se monta."""
    node = shutil.which("node")
    if not node:
        raise flujo.Montaje(f"no hay node en el PATH: {funcion} de la página se corre con él")
    b = bloque(problemas, inicio, fin, funcion)
    if b is None:
        return None
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="aceptacion-bloque-"))
    atexit.register(shutil.rmtree, tmp, True)
    (tmp / "bloque.js").write_text(b, encoding="utf-8")
    (tmp / "args.json").write_text(json.dumps(list(args), ensure_ascii=False), encoding="utf-8")
    (tmp / "correr.js").write_text(_JS, encoding="utf-8")
    try:
        r = subprocess.run([node, str(tmp / "correr.js"), str(tmp / "bloque.js"), funcion, str(tmp / "args.json")],
                           cwd=str(tmp), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           text=True, errors="replace", timeout=60)
    except subprocess.TimeoutExpired:
        problemas.append(f"{funcion}(...) pasó de 60 segundos")
        return None
    try:
        o = json.loads(([l for l in r.stdout.splitlines() if l.strip()] or [""])[-1])
        if not isinstance(o, dict):
            raise ValueError
    except ValueError:
        problemas.append(f"node no devolvió lo que da {funcion} (salió con {r.returncode}): {r.stderr.strip()[-200:]}")
        return None
    if "_error" in o:
        problemas.append(o["_error"])
        return None
    return o.get("_r")


def trazar(diseno, problemas):
    """Lo que devuelve trazarDesarrollo(diseno) del bloque de la página, corrido con node, o None con el porqué."""
    if not isinstance(diseno, dict):
        if not shutil.which("node"):
            raise flujo.Montaje("no hay node en el PATH: el trazado de la página se corre con él")
        problemas.append(f"«diseno» es {json.dumps(diseno, ensure_ascii=False)[:80]}: no hay qué trazar")
        return None
    t = correr(INICIO, FIN, "trazarDesarrollo", [diseno], problemas)
    if t is None:
        return None
    if not isinstance(t, dict) or any(k not in t for k in VISTAS):
        problemas.append(f"trazarDesarrollo(diseno) devolvió {json.dumps(t, ensure_ascii=False)[:120]}, no "
                         "{\"datos\", \"componentes\", \"infraestructura\"}")
        return None
    return t


def dibujo(t, vista, problemas):
    """La vista del trazado (datos, componentes o infraestructura) como dict, o None con el porqué."""
    v = t.get(vista)
    if not isinstance(v, dict):
        problemas.append(f"el dibujo de «{vista}» es {json.dumps(v, ensure_ascii=False)[:80]}, y la sección tiene filas")
        return None
    for k, tipo in (("cajas", list), ("contenedores", list), ("lineas", list), ("verbos", list), ("leyenda", list)):
        if not isinstance(v.get(k), tipo):
            problemas.append(f"«{k}» del dibujo de «{vista}» es {json.dumps(v.get(k), ensure_ascii=False)[:80]}, no una lista")
            return None
    return v


def num(*xs):
    return all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in xs)


def rect(o):
    """(x, y, w, h) de un objeto del trazado, o None si no son números."""
    if not isinstance(o, dict) or not num(o.get("x"), o.get("y"), o.get("w"), o.get("h")):
        return None
    return float(o["x"]), float(o["y"]), float(o["w"]), float(o["h"])


def solapan(r1, r2):
    """Si dos rectángulos comparten área (tocarse por el borde no cuenta)."""
    ax, ay, aw, ah = r1
    bx, by, bw, bh = r2
    return min(ax + aw, bx + bw) - max(ax, bx) > TOL and min(ay + ah, by + bh) - max(ay, by) > TOL


def cruza(p, q, r):
    """Si el tramo recto p-q (horizontal o vertical) pasa por el interior de r."""
    x, y, w, h = r
    (x1, y1), (x2, y2) = p, q
    if abs(y1 - y2) <= TOL:   # horizontal
        return y + TOL < y1 < y + h - TOL and min(max(x1, x2), x + w - TOL) - max(min(x1, x2), x + TOL) > 0
    if abs(x1 - x2) <= TOL:   # vertical
        return x + TOL < x1 < x + w - TOL and min(max(y1, y2), y + h - TOL) - max(min(y1, y2), y + TOL) > 0
    return False


def en(p, r):
    """Si el punto p cae en el rectángulo r o a 12 px de él como mucho (el sitio de la punta de flecha)."""
    x, y, w, h = r
    return x - 12 <= p[0] <= x + w + 12 and y - 12 <= p[1] <= y + h + 12


def ids(v):
    """{titulo: id} de las cajas de un dibujo."""
    return {c.get("titulo"): c.get("id") for c in v["cajas"] if isinstance(c, dict)}


def filas(dis, vista):
    """Los nombres de las filas de la sección de una vista, y los pares (de, a) que se dibujan con línea (en «Datos», sin
    los que van a la base ni los que salen de ella)."""
    parte = {"datos": "entidades", "componentes": "componentes", "infraestructura": "infraestructura"}[vista]
    vistas = [f for f in (saca(dis, parte) or []) if isinstance(f, dict) and isinstance(f.get("nombre"), str)]
    nombres = [f["nombre"] for f in vistas]
    pares = []
    base = saca(dis, "datos_disposicion", "abajo") or [] if vista == "datos" else []
    for f in vistas:
        if vista == "datos" and f["nombre"] in base:
            continue   # lo que sale de la base no se dibuja (P20: ninguna línea llega a ella ni sale de ella)
        if vista == "datos":
            destinos = [r.get("con") for r in (f.get("relaciones") or []) if isinstance(r, dict) and r.get("base") is not True]
        else:
            destinos = list(f.get("conecta_con") or [])
        pares += [(f["nombre"], c) for c in destinos if c in nombres]
    return nombres, pares


def hay_linea(v, a, b):
    """Si alguna línea del dibujo une las cajas a y b (en cualquier sentido)."""
    return any(isinstance(l, dict) and {l.get("a"), l.get("b")} == {a, b} for l in v["lineas"])


def rotulo(problemas, que, lineas, titulo, largo=False):
    """Un rótulo de 1 o 2 líneas: entero en una; si no, en dos cuyo texto junto es el título; si tampoco, cortado con
    «…» al final de la segunda. largo: tiene que ir en dos líneas."""
    if not isinstance(titulo, str) or not titulo.strip():
        problemas.append(f"{que} no lleva «titulo» (el texto entero del tooltip)")
        return
    if not isinstance(lineas, list) or not 1 <= len(lineas) <= 2 or not all(isinstance(l, str) for l in lineas):
        problemas.append(f"el rótulo de {que} es {json.dumps(lineas, ensure_ascii=False)}, no una lista de 1 o 2 líneas")
        return
    junto = " ".join(lineas)
    if largo and len(lineas) != 2:
        problemas.append(f"{que} tiene un nombre de {len(titulo)} letras y su rótulo va en una línea: "
                         f"{json.dumps(lineas, ensure_ascii=False)}")
    if len(lineas) == 1:
        if lineas[0] != titulo:
            problemas.append(f"el rótulo de {que} es «{lineas[0]}» en una sola línea, y su título es «{titulo}»: "
                             "si no cabe, pasa a una segunda línea antes de cortarse")
        return
    if lineas[0].endswith("…"):
        problemas.append(f"el rótulo de {que} se corta en la primera línea: {json.dumps(lineas, ensure_ascii=False)}")
        return
    norm = lambda s: re.sub(r"\s+", " ", s).strip()  # noqa: E731
    if lineas[1].endswith("…"):
        visto = lineas[1][:-1].rstrip()
        if not (norm(titulo).startswith(norm(lineas[0] + " " + visto)) or norm(titulo).startswith(norm(lineas[0] + visto))):
            problemas.append(f"el rótulo cortado de {que} ({json.dumps(lineas, ensure_ascii=False)}) no es el comienzo de su "
                             f"título «{titulo}»")
    elif norm(junto) != norm(titulo) and "".join(lineas) != titulo:
        problemas.append(f"las dos líneas del rótulo de {que} ({json.dumps(lineas, ensure_ascii=False)}) no son, juntas, su "
                         f"título «{titulo}»")


def trazados(problemas_por, cuales=None):
    """Genera la muestra de cada diseño y lo traza: {nombre: (diseno, trazado)}. Lo que falla va a problemas_por[nombre]."""
    out = {}
    for nombre, texto in MUESTRAS if cuales is None else cuales:
        ps = problemas_por.setdefault(nombre, [])
        d = pestana(*generar([con_muestra(texto)] if texto else [CON_LARGO]), ps)
        dis = saca(d, "diseno") if d is not None else None
        t = trazar(dis, ps) if d is not None else None
        out[nombre] = (dis, t)
    return out


def escenarios(inf):
    previos = {}
    hechos = trazados(previos)   # las dos muestras, generadas y trazadas una vez para los cuatro escenarios

    def cada_vista(problemas, mirar):
        for nombre, (dis, t) in hechos.items():
            problemas += [f"{nombre}: {p}" for p in previos[nombre]]
            if t is None:
                continue
            for vista in VISTAS:
                v = dibujo(t, vista, problemas)
                if v is not None:
                    mirar(f"{vista} de {nombre}", dis, vista, v, problemas)

    # 1 · Ninguna línea pasa por encima de una caja: en ángulo recto, y sin cruzar más caja que las dos que une.
    #     Añadido: cada fila es una caja y cada relación o conexión que se dibuja tiene su línea, para que no pase vacío
    def lineas(que, dis, vista, v, problemas):
        nombres, pares = filas(dis, vista)
        caja = ids(v)
        faltan = [n for n in nombres if n not in caja]
        if faltan:
            problemas.append(f"en {que}, no hay caja con título {json.dumps(faltan, ensure_ascii=False)}")
        for a, b in pares:
            if a in caja and b in caja and not hay_linea(v, caja[a], caja[b]):
                problemas.append(f"en {que}, «{a}» → «{b}» no tiene línea")
        rects = {c.get("id"): rect(c) for c in v["cajas"] if isinstance(c, dict)}
        for l in v["lineas"]:
            pts = l.get("puntos") if isinstance(l, dict) else None
            if not isinstance(pts, list) or len(pts) < 2 or not all(isinstance(p, list) and len(p) == 2 and num(*p) for p in pts):
                problemas.append(f"en {que}, una línea no trae al menos dos puntos [x, y]: {json.dumps(l, ensure_ascii=False)[:120]}")
                continue
            a, b = l.get("a"), l.get("b")
            if rects.get(a) is None or rects.get(b) is None:
                problemas.append(f"en {que}, la línea {a} → {b} no une dos cajas del dibujo")
                continue
            if not en(pts[0], rects[a]) or not en(pts[-1], rects[b]):
                problemas.append(f"en {que}, la línea {a} → {b} no sale de su caja o no llega a la otra")
            for p, q in zip(pts, pts[1:]):
                if abs(p[0] - q[0]) > TOL and abs(p[1] - q[1]) > TOL:
                    problemas.append(f"en {que}, la línea {a} → {b} tiene un tramo en diagonal: {p} → {q}")
                    continue
                for cid, r in rects.items():
                    if cid not in (a, b) and r is not None and cruza(p, q, r):
                        problemas.append(f"en {que}, la línea {a} → {b} pasa por encima de la caja {cid} ({p} → {q})")
    problemas = []
    cada_vista(problemas, lineas)
    inf.escenario("Ninguna línea pasa por encima de una caja", problemas)

    # 2 · Un verbo va en un tramo libre: no se solapa con ninguna caja ni con otro verbo. Cada relación con verbo que
    #     se dibuja (ni hacia la base ni desde ella) tiene el suyo (las dos muestras los llevan en «Datos»)
    def verbos(que, dis, vista, v, problemas):
        cajas = [(c.get("id"), rect(c)) for c in v["cajas"] if isinstance(c, dict)]
        vs = [(x, rect(x)) for x in v["verbos"] if isinstance(x, dict)]
        if vista == "datos":
            caja = ids(v)
            base = saca(dis, "datos_disposicion", "abajo") or []
            for e in saca(dis, "entidades") or []:
                if not isinstance(e, dict) or e.get("nombre") in base:
                    continue   # lo que sale de la base no se dibuja ni lleva verbo
                for r in e.get("relaciones") or []:
                    if isinstance(r, dict) and r.get("verbo") and r.get("base") is not True:
                        a, b = caja.get(e.get("nombre")), caja.get(r.get("con"))
                        if not any({x.get("a"), x.get("b")} == {a, b} and x.get("t") == r["verbo"] for x, _ in vs):
                            problemas.append(f"en {que}, «{e.get('nombre')}» → «{r.get('con')}» ({r['verbo']}) no tiene su verbo en «verbos»")
        for i, (x, r) in enumerate(vs):
            if r is None:
                problemas.append(f"en {que}, el verbo {json.dumps(x, ensure_ascii=False)[:80]} no trae x, y, w, h")
                continue
            for cid, rc in cajas:
                if rc is not None and solapan(r, rc):
                    problemas.append(f"en {que}, el verbo «{x.get('t')}» ({x.get('a')} → {x.get('b')}) se solapa con la caja {cid}")
            for y, r2 in vs[i + 1:]:
                if r2 is not None and solapan(r, r2):
                    problemas.append(f"en {que}, el verbo «{x.get('t')}» se solapa con el verbo «{y.get('t')}»")
    problemas = []
    cada_vista(problemas, verbos)
    inf.escenario("Un verbo va en un tramo libre", problemas)

    # 3 · El texto guarda su tamaño: el tamaño de letra más pequeño de cada dibujo es de 13 px o más
    def tamano(que, dis, vista, v, problemas):
        if not num(v.get("px_min")) or v["px_min"] < 13:
            problemas.append(f"en {que}, «px_min» es {json.dumps(v.get('px_min'))}, no 13 o más")
    problemas = []
    cada_vista(problemas, tamano)
    inf.escenario("El texto guarda su tamaño", problemas)

    # 4 · Un rótulo largo pasa a dos líneas, y si tampoco cabe se corta con el texto entero en su título: cada caja y
    #     cada contenedor de las dos muestras, y una caja con un nombre de 70 letras en la muestra de P05
    def rotulos(que, dis, vista, v, problemas):
        for c in v["cajas"]:
            if isinstance(c, dict):
                rotulo(problemas, f"la caja «{c.get('titulo')}» ({que})", c.get("nombre"), c.get("titulo"))
        for c in v["contenedores"]:
            if isinstance(c, dict):
                rotulo(problemas, f"el contenedor «{c.get('titulo')}» ({que})", c.get("rotulo"), c.get("titulo"))
    problemas = []
    cada_vista(problemas, rotulos)
    largo = {}
    dis, t = trazados(largo, [("la muestra de P05 con un nombre largo", None)])["la muestra de P05 con un nombre largo"]
    problemas += largo["la muestra de P05 con un nombre largo"]
    if t is not None:
        v = dibujo(t, "componentes", problemas)
        if v is not None:
            c = [c for c in v["cajas"] if isinstance(c, dict) and c.get("titulo") == LARGO]
            if not c:
                problemas.append(f"en componentes, no hay caja con título «{LARGO}»")
            else:
                rotulo(problemas, f"la caja de {len(LARGO)} letras", c[0].get("nombre"), c[0].get("titulo"), largo=True)
    inf.escenario("Un rótulo largo pasa a dos líneas", problemas)


if __name__ == "__main__":   # P19 y P20 importan de aquí lo común
    flujo.principal("P21", escenarios)
