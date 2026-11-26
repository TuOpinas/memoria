#!/usr/bin/env python3
"""P29 · Roles that fit any project (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-25, en el plan).

- «Audita: nadie» is not something missing. Dado a «Desarrollo» section with «Audita: nadie», Cuando its session opens,
  Entonces the opening gives no warning about it.
- «Recibe» is optional. Dado a section with no «Recibe» line, and another with one, Cuando each opens, Entonces neither
  warns, and the second reads the person as it reads the other roles.
- The other three still count. Dado a section with «Acepta», «Construye» or «Administra» empty, Cuando its session
  opens, Entonces the opening warns as today.
- The templates carry the roles. Dado the kit's templates, Cuando a project is set up from them, Entonces the section
  explains the five lines, and the repository's rules say to stop and ask whoever accepts.

Por dos entradas. La apertura de sesión (plugins/memoria/skills/sesion/abrir.py) sobre la raíz de muestra de
P05_lectores.py (MUESTRA), escrita en una carpeta temporal con los cambios del escenario, y sus líneas «Desarrollo:» de
la sección «=== AVISOS». Y el lector de la sección, por la interfaz pública de packages/context-core
(context_core.development: development_section y missing_pieces), que se importa dentro de cada prueba. Las plantillas
del kit (seccion-desarrollo.md y claude-md.md) se leen como texto. Cómo se monta cada escenario está en RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P29_roles.py (0 pasa, 1 falla, 2 no se montó).
"""
import atexit, json, pathlib, re, shutil, subprocess, sys, tempfile

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta ni en packages/context-core
AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from P05_lectores import MUESTRA, flujo  # noqa: E402  (la raíz de muestra; flujo: Informe, principal y Montaje)

REPO = AQUI.parents[1]
ABRIR = REPO / "plugins" / "memoria" / "skills" / "sesion" / "abrir.py"
CONTEXT_CORE = REPO / "packages" / "context-core"
PLANTILLAS = REPO / "plugins" / "memoria" / "skills" / "desarrollo" / "plantillas"
CUENTA = "ana@muestra.mx"
PORTAL = "ventas/portal"
PROYECTO_MD = "ventas/portal/proyecto.md"
ROLES = ("Acepta", "Audita", "Construye", "Administra")
LINEA = {r: f"{r}: Ana Pérez (ana@muestra.mx)\n" for r in ROLES}   # cómo dice cada rol la muestra
RECIBE = "Recibe: Ana Pérez (ana@muestra.mx)\n"
CINCO = ("Acepta", "Audita", "Construye", "Administra", "Recibe")


def cambiar(texto, cambios, donde):
    for viejo, nuevo in cambios:
        if texto.count(viejo) != 1:
            raise flujo.Montaje(f"{donde} de la muestra no tiene una sola vez «{viejo.strip()[:60]}»")
        texto = texto.replace(viejo, nuevo)
    return texto


def abrir(cambios=()):
    """Escribe MUESTRA en una carpeta temporal, cambia su ventas/portal/proyecto.md ((texto que está una sola vez, texto
    nuevo)) y abre la sesión del portal con la apertura del plugin, desde la raíz del repositorio. Devuelve (código, salida)."""
    if not ABRIR.is_file():
        raise flujo.Montaje(f"no está la apertura de sesión en {ABRIR}")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="aceptacion-p29-"))
    atexit.register(shutil.rmtree, tmp, True)
    raiz = tmp / "raiz"
    for ruta, texto in MUESTRA.items():
        (raiz / ruta).parent.mkdir(parents=True, exist_ok=True)
        (raiz / ruta).write_text(cambiar(texto, cambios, ruta) if ruta == PROYECTO_MD else texto, encoding="utf-8")
    # sin tope propio: lo pone correr.py, que corta la corrida entera y la da por no corrida (2), no por fallada
    r = subprocess.run([sys.executable, "-I", str(ABRIR), str(raiz), PORTAL, "--cuenta", CUENTA], cwd=str(REPO),
                       stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                       errors="replace")
    return r.returncode, r.stdout


def avisos_desarrollo(rc, salida, problemas):
    """Las líneas de «=== AVISOS» que empiezan por «Desarrollo:» (sin la viñeta); None (con el porqué) si no hay sección."""
    if rc != 0:
        ultimas = [l for l in (salida or "").splitlines() if l.strip()][-3:]
        problemas.append(f"la apertura salió con {rc}, no con 0: {' | '.join(ultimas)}")
        return None
    dentro, visto, out = False, False, []
    for l in salida.splitlines():
        if l.startswith("=== "):
            if dentro:
                break
            dentro = l.startswith("=== AVISOS")
            visto = visto or dentro
            continue
        if dentro:
            t = re.sub(r"^\s*[-*]\s+", "", l).strip()
            if t.startswith("Desarrollo:"):
                out.append(t)
    if not visto:
        problemas.append("la apertura no imprimió ninguna sección «=== AVISOS»")
        return None
    return out


def lector(texto):
    """La sección leída por la interfaz pública de context_core, importada aquí y no arriba del archivo:
    (sección, piezas que faltan). existe(ruta) siempre es True: las rutas de la muestra no se juzgan aquí."""
    if not (CONTEXT_CORE / "context_core").is_dir():
        raise flujo.Montaje(f"no está el paquete context_core en {CONTEXT_CORE}")
    if str(CONTEXT_CORE) not in sys.path:
        sys.path.insert(0, str(CONTEXT_CORE))
    from context_core.development import development_section, missing_pieces
    s = development_section(texto)
    return s, list(missing_pieces(s, lambda ruta: True))


def seccion(cambios=()):
    return lector(cambiar(MUESTRA[PROYECTO_MD], cambios, PROYECTO_MD))


def claves(faltan):
    return [getattr(m, "key", None) for m in faltan]


def personas(lista):
    return [(getattr(p, "name", None), getattr(p, "email", None)) for p in (lista or [])]


def sin_aviso(problemas, rol, faltan, avisos):
    if rol in claves(faltan):
        m = [m for m in faltan if getattr(m, "key", None) == rol][0]
        problemas.append(f"el lector da «{rol}» como pieza que falta (reason = {getattr(m, 'reason', None)!r})")
    if avisos is not None:
        for a in avisos:
            if rol in a:
                problemas.append(f"un aviso de la apertura nombra «{rol}»: {a[:200]}")


def con_aviso(problemas, rol, faltan, avisos):
    if rol not in claves(faltan):
        problemas.append(f"el lector no da «{rol}» como pieza que falta: keys = {json.dumps(claves(faltan), ensure_ascii=False)}")
    if avisos is not None and not any(rol in a for a in avisos):
        problemas.append(f"ninguna línea «Desarrollo:» de los avisos nombra «{rol}»: {json.dumps(avisos, ensure_ascii=False)}")


def plantilla(nombre):
    p = PLANTILLAS / nombre
    if not p.is_file():
        raise flujo.Montaje(f"no está la plantilla {p.relative_to(REPO)}")
    return p.read_text(encoding="utf-8")


def bloque_ejemplo(texto):
    """Las líneas del primer bloque de código («```») de la plantilla de la sección."""
    m = re.search(r"^```[^\n]*\n(.*?)^```", texto, re.S | re.M)
    return m.group(1).splitlines() if m else []


def vinetas_roles(texto):
    """{rol: texto de su viñeta «- **Rol:** …»} de las viñetas que siguen a la línea «Qué hace cada rol»."""
    lineas = texto.splitlines()
    i = next((k for k, l in enumerate(lineas) if "Qué hace cada rol" in l), None)
    if i is None:
        return None
    out, empezadas = {}, False
    for l in lineas[i + 1:]:
        if not l.strip():
            if empezadas:
                break
            continue
        m = re.match(r"^\s*-\s+\*\*([^*:]+):\*\*(.*)$", l)
        if m:
            empezadas = True
            out[m.group(1).strip()] = m.group(2).strip()
        elif l.lstrip().startswith("-") or not empezadas:
            if empezadas:
                break
        else:   # continuación de la viñeta anterior
            ultimo = list(out)[-1]
            out[ultimo] += " " + l.strip()
    return out


def escenarios(inf):
    # 1 · «Audita: nadie» no es algo que falte: ni en el lector (su lista de personas es [] y no falta) ni en la
    #     apertura. Vale con cualquier mayúscula: «Nadie» y «NADIE» son filas añadidas
    for nadie in ("nadie", "Nadie", "NADIE"):
        cambios = [(LINEA["Audita"], f"Audita: {nadie}\n")]
        problemas = []
        s, faltan = seccion(cambios)
        roles = getattr(s, "roles", None)
        if not isinstance(roles, dict) or "Audita" not in roles:
            problemas.append(f"el lector no trae el rol «Audita» en s.roles: {roles!r}")
        elif roles["Audita"] != []:
            problemas.append(f"con «Audita: {nadie}», s.roles['Audita'] no es [] sino "
                             f"{json.dumps(personas(roles['Audita']), ensure_ascii=False)}")
        sin_aviso(problemas, "Audita", faltan, avisos_desarrollo(*abrir(cambios), problemas))
        inf.escenario(f"«Audita: nadie» no es algo que falte («Audita: {nadie}»)", problemas)

    # 2 · «Recibe» es opcional: sin la línea (la muestra tal cual) no avisa; con ella tampoco, y la persona se lee como la
    #     de los otros roles (mismo nombre y correo que la misma persona escrita en «Acepta:», que en la muestra es ella)
    problemas = []
    s, faltan = seccion()
    sin_aviso(problemas, "Recibe", faltan, avisos_desarrollo(*abrir(), problemas))
    cambios = [(LINEA["Administra"], LINEA["Administra"] + RECIBE)]
    s, faltan = seccion(cambios)
    sin_aviso(problemas, "Recibe", faltan, avisos_desarrollo(*abrir(cambios), problemas))
    roles = getattr(s, "roles", None)
    if not isinstance(roles, dict) or "Recibe" not in roles:
        problemas.append(f"con «{RECIBE.strip()}», el lector no trae «Recibe» en s.roles: claves = "
                         f"{json.dumps(sorted(roles) if isinstance(roles, dict) else roles, ensure_ascii=False)}")
    else:
        esperado = personas((roles.get("Acepta") or [])[:1])
        if not esperado or esperado[0][0] != "Ana Pérez":
            raise flujo.Montaje(f"la muestra no lee «Acepta» como Ana Pérez: {esperado!r}")
        if personas(roles["Recibe"]) != esperado:
            problemas.append(f"s.roles['Recibe'] es {json.dumps(personas(roles['Recibe']), ensure_ascii=False)}, y la "
                             f"misma persona en «Acepta» se lee {json.dumps(esperado, ensure_ascii=False)}")
    inf.escenario("«Recibe» es opcional", problemas)

    # 3 · Los otros tres siguen contando: cada uno con su línea vacía avisa, en el lector y en la apertura. «Audita:»
    #     vacía (sin «nadie») es una fila añadida: vacía no es «nadie»
    for rol in ("Acepta", "Construye", "Administra", "Audita"):
        cambios = [(LINEA[rol], f"{rol}:\n")]
        problemas = []
        s, faltan = seccion(cambios)
        con_aviso(problemas, rol, faltan, avisos_desarrollo(*abrir(cambios), problemas))
        inf.escenario(f"Los otros tres siguen contando («{rol}» vacía)", problemas)

    # 4 · Las plantillas llevan los roles: la sección explica las cinco líneas y las reglas del repositorio dicen que se
    #     pare y pregunte a quien acepta
    problemas = []
    sec = plantilla("seccion-desarrollo.md")
    ejemplo = bloque_ejemplo(sec)
    if not ejemplo:
        problemas.append("seccion-desarrollo.md no tiene un bloque de ejemplo («```»)")
    for rol in CINCO:
        if ejemplo and not any(l.startswith(rol + ":") for l in ejemplo):
            problemas.append(f"el bloque de ejemplo de seccion-desarrollo.md no tiene una línea «{rol}:»")
    vin = vinetas_roles(sec)
    if vin is None:
        problemas.append("seccion-desarrollo.md no tiene «Qué hace cada rol»")
        vin = {}
    for rol in CINCO:
        if rol not in vin:
            problemas.append(f"bajo «Qué hace cada rol» no hay una viñeta «- **{rol}:**» (hay: {', '.join(vin) or 'ninguna'})")
    if "Audita" in vin:
        a = vin["Audita"].lower()
        if "nadie" not in a:
            problemas.append(f"la viñeta de Audita no dice «nadie»: {vin['Audita'][:200]}")
        for f in ("da el sí", "decide en los puntos de control"):
            if f in a:
                problemas.append(f"la viñeta de Audita todavía dice «{f}»")
    if "Acepta" in vin:
        for f in ("puntos de control", "da el sí"):
            if f not in vin["Acepta"].lower():
                problemas.append(f"la viñeta de Acepta no dice «{f}»: {vin['Acepta'][:200]}")
    cmd = plantilla("claude-md.md").lower()
    if "pregunta a quien acepta" not in cmd:
        problemas.append("claude-md.md no dice «pregunta a quien acepta»")
    if "pregunta a quien audita" in cmd:
        problemas.append("claude-md.md todavía dice «pregunta a quien audita»")
    inf.escenario("Las plantillas llevan los roles", problemas)


flujo.principal("P29", escenarios)
