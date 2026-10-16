#!/usr/bin/env python3
"""Genera los documentos de la Vista a partir de una raíz del método Memoria.

Lee solo la superficie pública: guia.md, cada area.md y, de cada proyecto,
proyecto.md, decisiones.md, sesiones.md y las cabeceras de entregables/.
Nunca abre fuentes/, taller/, restringido/ ni base/ (salvo base/premisas.md, que es de toda la organización): de fuentes/ y taller/ solo mira las fechas
de modificación, para el aviso de trabajo sin sesión.

Uso: generar_vista.py <raiz> <carpeta-de-salida> [--modo publico|completo] [--tarea <id de la tarea programada que regenera la vista>] [--manual] [--version <versión del plugin que lo ejecuta>]
--manual: la tarea no tiene horario y solo corre desde el botón «Sincronizar ahora»
La carpeta de salida va fuera de la raíz (es derivada y se regenera entera); nunca dentro de la carpeta de la organización.

En dos tiempos, cuando la raíz está en otra computadora y el resultado tiene que llegar a Claude sin pasar por la conversación:
  1. En la computadora:  generar_vista.py <raiz> --inventario [--modo …]
     Imprime un JSON con «leer» (las rutas, relativas a la raíz, de los archivos que hay que traer) e «inventario» (lo poco
     que el generador necesita y no está dentro de esos archivos: fechas de modificación, lo que no se pudo leer, la lista
     de proyectos y las carpetas sueltas). No escribe nada.
  2. Donde se tenga la copia de esos archivos, con su misma estructura:
     generar_vista.py <copia> <carpeta-de-salida> --desde-inventario <inventario.json> [--modo …] [--tarea …] [--version …]
     Comprueba que la copia trae exactamente los archivos de «leer» y genera lo mismo que el modo de un tiempo en la computadora.

Dos modos. «publico» (el de siempre si no se dice otro): la superficie pública del contrato. De un área cuya columna
«Quién la lee» en guia.md dice «Restringida», y de un proyecto cuya línea del índice de area.md empieza por «restringido» o que no está en ese índice,
solo nombre y dueño, aunque la cuenta que corre el script pueda leerlos; de cada sesión, solo fecha y título.
«completo»: todo lo que la cuenta pueda leer, con las cinco sesiones más recientes enteras. Un tablero completo no se comparte.
En los dos modos, lo que la cuenta no puede leer sale como restringido.
Escribe un JSON por documento: meta/estado.json, areas/<slug>.json,
proyectos/<area>--<slug>.json, cada uno con una huella de su contenido; un indice.json con la lista de archivos, huellas y
tamaños; y meta/enfoque-candidatos.json, que no va a la base: lo usa la puesta al día para «Por dónde empezar».
"""
import sys, os, re, json, datetime, pathlib, hashlib, unicodedata
try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Mexico_City")
except Exception:
    TZ = datetime.timezone.utc

RAIZ = pathlib.Path(sys.argv[1])
def _arg(nombre):
    return sys.argv[sys.argv.index(nombre) + 1] if nombre in sys.argv and len(sys.argv) > sys.argv.index(nombre) + 1 else None
# primer tiempo: solo inventario, sin carpeta de salida; segundo tiempo: la raíz es una copia y lo demás viene del inventario
INVENTARIO = "--inventario" in sys.argv
_inv_ruta = _arg("--desde-inventario")
INV = json.loads(pathlib.Path(_inv_ruta).read_text(encoding="utf-8")) if _inv_ruta else None
if INV is not None and INV.get("formato") != 1:
    sys.exit("El inventario no es de este generador (formato distinto de 1): vuelve a sacarlo en la computadora con esta misma versión.")
OUT = None if INVENTARIO else pathlib.Path(sys.argv[2])
TAREA = _arg("--tarea")
# una tarea sin horario solo corre desde el botón: el tablero no espera que se ponga al día cada mañana
TAREA_MANUAL = bool(TAREA) and "--manual" in sys.argv
VERSION_PLUGIN = _arg("--version")
# --lineas: el inventario sale en líneas (inventario, cuántos archivos, sus rutas) para leerlo sin otra llamada.
# --si-cambia <huella>: si la huella de la raíz coincide, solo imprime «AL DIA» y no hace falta traer nada.
LINEAS = "--lineas" in sys.argv
SI_CAMBIA = _arg("--si-cambia")
# --cola-retenida <json>: ids de la cola que la puesta al día deja a propósito (esperan al dueño de otra área,
# a una sesión, o no encontraron su paso); el botón no los cuenta como «hace falta sincronizar».
_ret = _arg("--cola-retenida")
COLA_RETENIDA = json.loads(pathlib.Path(_ret).read_text(encoding="utf-8")) if _ret else None
# --ruta se acepta por compatibilidad con tareas viejas y no se guarda: la ruta de Drive lleva el correo de la persona
MODO = (_arg("--modo") or "publico").lower()
if MODO not in ("publico", "completo"):
    sys.exit("--modo admite publico o completo")
PUBLICO = MODO == "publico"
if INV is not None and INV.get("modo") != MODO:
    sys.exit(f"El inventario se sacó en modo {INV.get('modo')} y esto se genera en modo {MODO}: tienen que coincidir.")
HOY = datetime.datetime.now(TZ).date().isoformat()

def leer(p):
    """Texto del archivo, o None si no se puede leer (sin permiso, sin descargar, borrado). Un archivo
    con otra codificación no tumba la generación: se lee con reemplazos."""
    try:
        return p.read_bytes().decode("utf-8-sig", errors="replace").replace("\r\n", "\n")
    except OSError:
        return None

def por_que_no(p):
    """Por qué no se pudo leer p: «sin-acceso» (permiso), «sin-carpeta» (la carpeta no existe en esta
    computadora), «sin-archivo» (la carpeta existe y el archivo no), «sin-leer» (otro fallo: sin descargar…)."""
    try:
        p.read_bytes(); return None
    except PermissionError:
        return "sin-acceso"
    except FileNotFoundError:
        return "sin-carpeta" if not p.parent.exists() else "sin-archivo"
    except OSError:
        return "sin-leer"

def fecha_valida(f):
    try:
        datetime.date.fromisoformat(f); return True
    except (ValueError, TypeError):
        return False

def es_sesion_de_tarea(titulo):
    # las tareas programadas dejan su línea en sesiones.md marcada así; no son sesiones de trabajo
    return bool(re.search(r"\((tarea|tablero)\)", titulo or "", re.I))

def frontmatter(texto):
    m = re.match(r"^---\n(.*?)\n---\n?", texto, re.S)
    fm = {}
    if not m:
        return fm, texto
    ultima = None
    for linea in m.group(1).split("\n"):
        mm = re.match(r"^(\w+):\s*(.*)$", linea)
        if mm:
            ultima = mm.group(1)
            v = mm.group(2).strip()
            # listas en línea («[]», «[a, b]»); las de varias líneas se suman abajo
            fm[ultima] = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()] if v.startswith("[") and v.endswith("]") else v.strip("'\"")
            continue
        ml = re.match(r"^\s+-\s+(.*)$", linea)
        if ml and ultima:
            if not isinstance(fm.get(ultima), list):
                fm[ultima] = []
            fm[ultima].append(ml.group(1).strip().strip("'\""))
    return fm, texto[m.end():]

def seccion(texto, nombre):
    m = re.search(r"^## " + re.escape(nombre) + r"\s*\n(.*?)(?=^## |\Z)", texto, re.S | re.M)
    return m.group(1).strip() if m else ""

def titulo_h1(texto):
    m = re.search(r"^# (.+)$", texto, re.M)
    return m.group(1).strip() if m else ""

def bullets(texto):
    out = []
    for l in texto.split("\n"):
        s = l.strip()
        if s.startswith("- "):
            out.append(s[2:].strip())
    return out

def lineas_no_vacias(texto):
    return [l.rstrip() for l in texto.split("\n") if l.strip()]

def primer_parrafo(texto):
    # primer bloque de texto que no sea tabla ni lista
    for bloque in re.split(r"\n\s*\n", texto.strip()):
        b = bloque.strip()
        if not b or b.startswith("|") or b.startswith("- "):
            continue
        return b
    return texto.strip().split("\n")[0] if texto.strip() else ""

def fechas_en(texto):
    return re.findall(r"\b(20\d\d-\d\d-\d\d)\b", texto)

# ---------- guia.md ----------
guia = leer(RAIZ / "guia.md") or ""
version_metodo = ""
if INV is not None:
    version_metodo = INV.get("version_metodo", "")
else:
    # de metodo.md solo importa su primera línea
    try:
        with open(RAIZ / "metodo.md", encoding="utf-8-sig", errors="replace") as f_:
            m = re.search(r"(\d+\.\d+(?:\.\d+)?)", f_.readline())
        if m:
            version_metodo = m.group(1)
    except OSError:
        pass
NOMBRE_RAIZ = INV.get("raiz_nombre") if INV is not None else RAIZ.name
org = titulo_h1(guia).split("·")[0].strip() or NOMBRE_RAIZ

areas_guia = []
tabla = seccion(guia, "Áreas")
primera = True
for l in tabla.split("\n"):
    if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
        continue
    if primera:   # la fila de títulos
        primera = False; continue
    celdas = [c.strip() for c in l.strip().strip("|").split("|")]
    if len(celdas) < 5:
        continue
    slug = celdas[0].strip("`").rstrip("/")
    areas_guia.append({"slug": slug, "que": celdas[1], "dueno": celdas[2], "cuenta": celdas[3], "lectores": celdas[4]})

quien = seccion(guia, "Quién responde por qué")
contexto_comun = ""
administra = ""
for l in quien.split("\n"):
    if l.lower().startswith("contexto común"):
        contexto_comun = l.split(":", 1)[-1].strip().rstrip(".")
    if l.lower().startswith("administra"):
        administra = l.split(":", 1)[-1].strip().rstrip(".")

# ---------- premisas: el único archivo de base/ que lee el tablero ----------
premisas = []
for l in (leer(RAIZ / "base" / "premisas.md") or "").split("\n"):
    mm = re.match(r"^\s*-\s*(P\d+)\s*·\s*(.+)$", l)
    if not mm:
        continue
    partes = [x.strip() for x in mm.group(2).split("·")]
    pr = {"id": mm.group(1).upper(), "texto": partes[0], "confirmo": "", "fecha": "", "reemplaza": ""}
    for x in partes[1:]:
        if x.lower().startswith("confirmó:") or x.lower().startswith("confirmo:"):
            pr["confirmo"] = x.split(":", 1)[1].strip()
        elif re.match(r"^20\d\d-\d\d-\d\d$", x):
            pr["fecha"] = x
        elif x.lower().startswith("reemplaza a"):
            mr = re.search(r"P\d+", x, re.I); pr["reemplaza"] = mr.group(0).upper() if mr else ""
    premisas.append(pr)
reemplazadas = {p_["reemplaza"] for p_ in premisas if p_["reemplaza"]}
for p_ in premisas:
    p_["vigente"] = p_["id"] not in reemplazadas

# ---------- proyectos ----------
def parse_decisiones(texto):
    out = []
    if not texto:
        return out
    partes = re.split(r"^## ", texto, flags=re.M)[1:]
    for p in partes:
        cab, _, cuerpo = p.partition("\n")
        mm = re.match(r"(20\d\d-\d\d-\d\d)\s*·\s*(.*)", cab.strip())
        if mm:
            fecha, titulo = mm.group(1), mm.group(2).strip()
        else:
            fecha, titulo = (fechas_en(cab) or [""])[0], cab.strip()
        campos = {"decidio": "", "porque": "", "descartamos": "", "afecta": "", "planteo": "", "cuestiona": "", "responde": ""}
        actual = None
        for l in cuerpo.split("\n"):
            s = l.strip()
            low = s.lower()
            if low.startswith("decidió:") or low.startswith("decidio:"):
                actual = "decidio"; campos[actual] = s.split(":", 1)[1].strip()
            elif low.startswith("por qué:") or low.startswith("por que:"):
                actual = "porque"; campos[actual] = s.split(":", 1)[1].strip()
            elif low.startswith("descartamos:"):
                actual = "descartamos"; campos[actual] = s.split(":", 1)[1].strip()
            elif low.startswith("afecta a:"):
                actual = "afecta"; campos[actual] = s.split(":", 1)[1].strip()
            elif low.startswith("planteó:") or low.startswith("planteo:"):
                actual = "planteo"; campos[actual] = s.split(":", 1)[1].strip()
            elif low.startswith("cuestiona a:"):
                actual = "cuestiona"; campos[actual] = s.split(":", 1)[1].strip()
            elif low.startswith("responde a:"):
                actual = "responde"; campos[actual] = s.split(":", 1)[1].strip()
            elif actual and s:
                campos[actual] += "\n" + s
        d_ = {"fecha": fecha, "titulo": titulo, **campos}
        # solo el marcador del contrato: «Decidió: Nombre (pendiente de confirmar)»; mencionarlo en el por qué no cuenta
        if re.search(r"\(pendiente de confirma(r|ción)\)", campos["decidio"].lower()):
            d_["por_confirmar"] = True
        if campos["cuestiona"] or re.match(r"cuestionamiento\b", titulo, re.I):
            d_["tipo"] = "cuestionamiento"
            t_ = re.sub(r"^cuestionamiento\s*:\s*", "", titulo, flags=re.I) or titulo
            d_["titulo"] = t_[:1].upper() + t_[1:]
        for k in ("planteo", "cuestiona", "responde"):
            if not d_[k]: del d_[k]
        out.append(d_)
    # identificador: la fecha y, si ese día hay más de una entrada, -2, -3… contando desde la de más abajo (la más antigua)
    # una entrada sin fecha válida no tiene identificador: no se puede citar
    cuenta = {}
    for d_ in reversed(out):
        if not fecha_valida(d_["fecha"]):
            d_["id"] = ""; continue
        n = cuenta[d_["fecha"]] = cuenta.get(d_["fecha"], 0) + 1
        d_["id"] = d_["fecha"] + ("" if n == 1 else f"-{n}")
    out.sort(key=lambda d: d["fecha"], reverse=True)
    return out

def ref_decision(texto):
    """De «area/proyecto#2026-10-15-2 (…)» devuelve («area--proyecto», «2026-10-15-2»); de «premisa P3», («premisa», «P3»)."""
    t = (texto or "").strip()
    mp = re.search(r"\bpremisa\s+(P\d+)", t, re.I)
    if mp:
        return ("premisa", mp.group(1).upper())
    m = re.search(r"`?([a-z0-9][\w.-]*)/([a-z0-9][\w.-]*)#(20\d\d-\d\d-\d\d(?:-\d+)?)", t)
    return (f"{m.group(1)}--{m.group(2)}", m.group(3)) if m else (None, None)

def parse_sesiones(texto):
    out = []
    if not texto:
        return out
    partes = re.split(r"^## ", texto, flags=re.M)[1:]
    for p in partes:
        cab, _, cuerpo = p.partition("\n")
        fecha = (fechas_en(cab) or [""])[0]
        titulo = cab.strip()
        campos = {"trabajamos": "", "avances": "", "pendiente": ""}
        actual = None
        for l in cuerpo.split("\n"):
            s = l.strip()
            low = s.lower()
            if low.startswith("trabajamos en:"):
                actual = "trabajamos"; campos[actual] = s.split(":", 1)[1].strip()
            elif low.startswith("avances:"):
                actual = "avances"; campos[actual] = s.split(":", 1)[1].strip()
            elif low.startswith("pendiente:"):
                actual = "pendiente"; campos[actual] = s.split(":", 1)[1].strip()
            elif actual and s:
                campos[actual] += "\n" + s
        out.append({"fecha": fecha, "titulo": titulo, **campos})
    out.sort(key=lambda d: d["fecha"], reverse=True)
    return out

def parse_indice_proyectos(texto_area):
    """Devuelve {slug: {"descripcion":..., "entregables":{stem: {"descripcion","actualizado"}}, "notas":[...]}}"""
    bloque = seccion(texto_area, "Proyectos")
    idx = {}
    actual = None
    for l in bloque.split("\n"):
        m1 = re.match(r"^- `([^`]+?)/?`\s*[—–:-]?\s*(.*)$", l)
        if m1 and ("/" in m1.group(1) or m1.group(1).startswith(".")):
            actual = None; continue          # un proyecto es una carpeta del área: «../otra-area/…» no es un proyecto y no se sigue
        if m1:
            actual = m1.group(1)
            idx[actual] = {"descripcion": m1.group(2).strip(), "entregables": {}, "notas": []}
            continue
        m2 = re.match(r"^\s+- (.*)$", l)
        if m2 and actual:
            item = m2.group(1).strip()
            m3 = re.match(r"^([\w\-, ]+?)\s+[—–-]\s+(.*?)(?:\s*·\s*actualizado\s*(20\d\d-\d\d-\d\d))?\s*$", item)
            if m3 and m3.group(3):
                for stem in [s.strip() for s in m3.group(1).split(",")]:
                    idx[actual]["entregables"][stem] = {"descripcion": m3.group(2).strip(), "actualizado": m3.group(3)}
            else:
                idx[actual]["notas"].append(item)
    return idx

def fecha_de(p):
    """Fecha de modificación de p (día, hora de Ciudad de México), o None."""
    try:
        return datetime.datetime.fromtimestamp(os.stat(p).st_mtime, TZ).date().isoformat()
    except OSError:
        return None

def rel(p):
    return pathlib.Path(p).relative_to(RAIZ).as_posix()

def fechas_de_entregables(carpeta):
    """{archivo: fecha} de los entregables cuya fecha solo puede salir del archivo: los que no son .md, los .md que
    no se dejan leer y los que no traen «actualizado» en su cabecera. Es lo que el inventario lleva de cada proyecto."""
    d = carpeta / "entregables"
    out = {}
    try:
        nombres = sorted(os.listdir(d)) if d.exists() else []
    except OSError:
        return out
    for n in nombres:
        p = d / n
        if n.startswith(".") or p.is_dir():
            continue
        if n.endswith(".md"):
            t = leer(p)
            if t is not None and frontmatter(t)[0].get("actualizado"):
                continue
        f = fecha_de(p)
        if f:
            out[n] = f
        else:
            out[n] = None
    return out

def entregables_de(carpeta, indice):
    out = []
    d = carpeta / "entregables"
    fechas_inv = None
    if INV is not None:
        # la copia trae solo los .md legibles; los demás nombres y sus fechas vienen del inventario
        fechas_inv = INV.get("entregables", {}).get(rel(carpeta), {})
        try:
            copiados = [n for n in os.listdir(d) if not n.startswith(".") and n.endswith(".md")] if d.exists() else []
        except OSError:
            copiados = []
        nombres = sorted(set(copiados) | set(fechas_inv))
    else:
        if not d.exists():
            return out
        try:
            nombres = sorted(os.listdir(d))
        except OSError:
            return out
    for n in nombres:
        p = d / n
        if n.startswith(".") or (fechas_inv is None and p.is_dir()):
            continue
        stem = pathlib.Path(n).stem
        ent = {"archivo": n, "nombre": stem, "estado": None, "actualizado": None, "descripcion": "", "formato": pathlib.Path(n).suffix.lstrip(".")}
        if n.endswith(".md"):
            t = leer(p)
            if t is not None:
                fm, cuerpo_e = frontmatter(t)
                ent["titulo"] = titulo_h1(cuerpo_e) or None
                ent["estado"] = fm.get("estado")
                if isinstance(fm.get("basado_en"), list):
                    ent["basado_en"] = [re.sub(r"^\./", "", b) for b in fm["basado_en"]]
                ent["actualizado"] = fm.get("actualizado")
                if fm.get("reemplazado_por"):
                    ent["reemplazado_por"] = fm["reemplazado_por"]
        ref = indice.get(stem) or (indice.get(stem[:-3]) if stem.endswith("-en") else None)
        if ref:
            ent["descripcion"] = ref["descripcion"]
            if not ent["actualizado"]:
                ent["actualizado"] = ref["actualizado"]
        if not ent["actualizado"]:
            f = fechas_inv.get(n) if fechas_inv is not None else fecha_de(p)
            if f:
                ent["actualizado"] = f
                ent["fecha_de_archivo"] = True
        out.append(ent)
    return out


# ---------- clasificación de pasos ----------
STOP = set("de la el los las un una y o en a al del para por con sin que se su sus lo le les es son como más ya no si este esta esto ese esa eso hay hasta desde sobre entre cuando donde cada muy también antes después tras ante aún sólo solo mismo misma otra otro otros otras todo toda todos todas ser estar tener hacer poner".split())
PALABRAS_SIG = lambda t: {w for w in re.findall(r"[a-záéíóúñ]{4,}", t.lower()) if w not in STOP}

def naturaleza(texto):
    t = texto.strip().lower()
    t = re.sub(r"^(20\d\d-\d\d-\d\d:?\s*)", "", t)
    if re.match(r"^(sostener|mantener|seguir |continuar|cada (semana|mes|lunes|viernes))", t): return "rutina"
    if re.search(r"(según su caducidad|caducidad|vence en (enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)|se revisa en \w+ de 20\d\d|revisión (fijada|trimestral|anual))", t): return "caducidad"
    if re.match(r"^(esperar|recoger la respuesta|a la espera|aguardar)", t) or re.search(r"\bsi no (escribe|contesta|responde|llama|ha llamado|hay respuesta)\b", t) or re.match(r"^(cuando|en cuanto) \w+ (conteste|responda|escriba|confirme|mande|envíe)", t): return "espera"
    if re.match(r"^(al cumplirse|al (firmarse|arrancar|migrar|contratar|cerrar|terminar)|cuando |en unas semanas|en una o dos semanas|retomar|más adelante|después de|tras |una vez que|mirar en )", t): return "condicional"
    if re.match(r"^(decidir|definir|confirmar|elegir|acordar|aprobar|fijar|cerrar `?[\w\-/.]+\.md|pasar(lo|la)? a vigente|revisar .{0,80} para pasar(lo|la)? a vigente|resolver|replantear)", t): return "decision"
    return "accion"

RUIDO = set("tuopinas juanjo claude cowork memoria pro google workspace fácil facil mac macbook air ahora después".split())
def tokens_tema(texto):
    """Tokens que sirven para agrupar pasos de proyectos distintos: entregables citados, nombres propios, herramientas y roles."""
    toks = set()
    for m in re.findall(r"`([^`]+)`", texto):
        base = m.strip("/").split("/")[-1]
        base = re.sub(r"\.(md|html|pdf|docx|xlsx)$", "", base)
        if base and base not in ("proyecto", "decisiones", "sesiones", "area", "guia", "fuentes", "taller", "entregables"): toks.add(base.lower())
    sin_cod = re.sub(r"`[^`]+`", " ", texto)
    # nombres propios de una o más palabras seguidas con mayúscula, no al inicio de frase
    for m in re.finditer(r"(?<![.\n])(?<=[\s(,;:])((?:[A-ZÁÉÍÓÚ][\wáéíóúñ&+.]*\s?){1,3})", sin_cod):
        nombre = m.group(1).strip().lower()
        if nombre and nombre not in RUIDO and not re.match(r"^(al|si|en|la|el|los|las|un|una|es|hoy|lo|se|no|su|sus|con|de|para|por|que|ese|esa|este|esta|cada|antes|después|mirar)$", nombre):
            toks.add(nombre)
    for rol in ("abogado", "contador", "notario", "banco"):
        if re.search(r"\b" + rol + r"\b", sin_cod.lower()): toks.add(rol)
    for tool in ("posthog", "linkedin", "github", "cloudflare", "drive", "odoo", "granola", "whatsapp", "gmail", "dmarc", "impi", "search console", "slack", "squarespace"):
        if tool in sin_cod.lower(): toks.add(tool)
    return {t for t in toks if t not in RUIDO}


PLAZO_ANTES = r"(antes del|antes de|para el|hasta el|a más tardar el|fecha límite:?|vence el|vencido el|vencida el|el próximo|el lunes|el martes|el miércoles|el jueves|el viernes|el sábado|el domingo|lunes|martes|miércoles|jueves|viernes|esperar (?:al|hasta el)|en la revisión del|revisión (?:trimestral|anual)? ?del|el)\s*"
CONTEXTO_ANTES = r"(compartió(?: por \w+)? el|compartid[oa]s? el|mandó el|envió el|respondió el|dijo el|llegó el|salió el|arrancó el|se montó el|quedó el|hizo el|cambió el|pasó el|enviad[oa]s? el|rehech[oa]s? el|comprobad[oa] el|publicad[oa] el|puest[oa] al día el|decisión del|desde el|montó el|creado el|creada el|firmad[oa] el|registrad[oa] el|actualizad[oa] el|del día|abierta el|cerrad[oa] el|entregad[oa] el|presentad[oa] el|hallazgo del|sesión del|propuesta del|criterio del|detectad[oa] el|revisad[oa] el|contestó el|escribió el|quedaron el)\s*"
def plazos_en(texto):
    out = []
    previa = None   # cómo se leyó la fecha anterior, para «el 2026-09-01 y el 2026-09-02»
    for m in re.finditer(r"\b(20\d\d-\d\d-\d\d)\b", texto):
        f = m.group(1)
        if not fecha_valida(f): continue
        antes = texto[max(0, m.start()-40):m.start()].lower()
        despues = texto[m.end():m.end()+12].lower()
        if m.start() <= 2: out.append(f); previa = True; continue          # «2026-10-13: buscar a…»
        if previa is not None and re.search(r"20\d\d-\d\d-\d\d\s*(y|o|,)\s*(el\s*)?$", antes):
            if previa: out.append(f)
            continue
        previa = False
        if re.search(r"(?<![\wáéíóú])" + CONTEXTO_ANTES + r"$", antes): continue             # «enviada el 2026-09-21»
        mp = re.search(r"([a-záéíóúñ]+)\s+el\s*$", antes)
        if mp and re.search(r"((ad|id|ech|ich|uest|uelt|biert|scrit|suelt)[oa]s?|ó|aron|ieron|é|ía|ían)$", mp.group(1)): continue   # «registradas el», «quedó el»: contexto
        if re.search(r"(?<![\wáéíóú])" + PLAZO_ANTES + r"$", antes) or despues.startswith(" a las") or (despues.startswith(":") and not re.search(r"\bdel\s*$", antes)):
            out.append(f); previa = True
    return out

def senales(paso_texto, area_doc, pdoc):
    """Señales objetivas de importancia. Vencido no cuenta, por decisión del 2026-10-08."""
    sig = PALABRAS_SIG(paso_texto)
    prio = None
    for i, pr in enumerate(area_doc.get("prioridades", [])):
        if len(sig & PALABRAS_SIG(pr)) >= 3: prio = i + 1; break
    cliente = pdoc["area"] == "clientes" or bool(re.search(r"\b(cliente|propuesta|contrato|firma|factur\w*|cobro|precio|impi|acuerdo de confidencialidad)\b", paso_texto.lower()))
    return {"prioridad_area": prio, "cliente_o_dinero": cliente}

def sin_sesion_de(pc, ses, cerrado):
    """Trabajo sin sesión de un proyecto, mirando solo fechas de archivo (nunca contenido), o None.
    Con inventario, viene ya calculado de la computadora, donde están las fechas de verdad."""
    if INV is not None:
        return INV.get("sin_sesion", {}).get(rel(pc))
    ultima_entrada = ses[0]["fecha"] if ses and fecha_valida(ses[0]["fecha"]) else None
    if not ultima_entrada or cerrado:
        return None
    donde, ultimo = {}, None
    objetivos = [("entregables", pc / "entregables"), ("taller", pc / "taller"), ("fuentes", pc / "fuentes")]
    for nombre, d in objetivos:
        for raiz_, dirs, files in os.walk(d) if d.exists() else []:
            dirs[:] = [x for x in dirs if not x.startswith(".")]
            for f in files:
                if f.startswith("."):
                    continue
                fm_ = fecha_de(os.path.join(raiz_, f))
                if not fm_:
                    continue
                if fm_ > ultima_entrada:
                    donde[nombre] = donde.get(nombre, 0) + 1
                    ultimo = max(ultimo or fm_, fm_)
    fd = fecha_de(pc / "decisiones.md")
    if fd and fd > ultima_entrada:
        donde["decisiones"] = 1; ultimo = max(ultimo or fd, fd)
    if donde:
        return {"desde": ultima_entrada, "ultimo": ultimo, "donde": donde, "archivos": sum(donde.values())}
    return None

def motivo_de(p):
    """Por qué no se leyó p: en la computadora se pregunta al disco; con inventario, lo dice el inventario."""
    if INV is not None:
        return INV.get("motivos", {}).get(rel(p), "sin-leer")
    return por_que_no(p) or "sin-leer"

def proyectos_de(carpeta, indice):
    """Los proyectos de un área: los de su índice más cualquier carpeta con proyecto.md, en ese orden."""
    if INV is not None:
        return list(INV.get("proyectos", {}).get(rel(carpeta), list(indice.keys())))
    slugs = list(indice.keys())
    try:
        for n in sorted(os.listdir(carpeta)):
            if (carpeta / n).is_dir() and not n.startswith(".") and n not in slugs and (carpeta / n / "proyecto.md").exists():
                slugs.append(n)
    except OSError:
        pass
    return slugs

def fuera_de_la_memoria():
    """Carpetas de la raíz que no son de ningún área: «Claude outputs» es donde la app de Claude deja lo que produce;
    cualquier otra carpeta suelta también queda fuera. Solo se cuentan archivos y fechas; los nombres, solo en completo."""
    if INV is not None:
        return INV.get("fuera", [])
    fuera_ = []
    slugs_area = {a["slug"] for a in areas_guia}
    try:
        sueltas = [n for n in sorted(os.listdir(RAIZ)) if (RAIZ / n).is_dir() and not n.startswith(".") and n not in slugs_area and n != "base"]
    except OSError:
        sueltas = []
    for n in sueltas:
        arch = []
        for raiz_, dirs, files in os.walk(RAIZ / n):
            dirs[:] = [x for x in dirs if not x.startswith(".")]
            for f in files:
                if f.startswith("."): continue
                fecha = fecha_de(os.path.join(raiz_, f))
                if not fecha:
                    continue
                arch.append((fecha, os.path.relpath(os.path.join(raiz_, f), RAIZ / n)))
        if not arch: continue
        arch.sort(reverse=True)
        item = {"carpeta": n, "de_claude": n.lower() == "claude outputs", "archivos": len(arch), "ultimo": arch[0][0], "primero": arch[-1][0]}
        if not PUBLICO:
            item["nombres"] = [{"fecha": f_, "nombre": n_} for f_, n_ in arch[:40]]
        fuera_.append(item)
    return fuera_

def es_declarado(ref, slug, indice):
    # se declara restringido el proyecto cuya línea del índice empieza por «restringido»; mencionar que una parte suya lo está no cuenta.
    # En público, un proyecto que no está en el índice del área tampoco se muestra: sin su línea no se sabe si es restringido
    return bool(re.match(r"^[\W_]*restringid[oa]\b", ref["descripcion"], re.I)) or (PUBLICO and slug not in indice)

def huella_copia(tamanos):
    """Huella de una copia: cada ruta (en NFC, para que los acentos de macOS no la cambien) con su tamaño."""
    lineas = sorted(f"{unicodedata.normalize('NFC', r)}\t{t}" for r, t in tamanos.items())
    return hashlib.sha1("\n".join(lineas).encode("utf-8")).hexdigest()[:16]

def sello(inv):
    """Sello del inventario: detecta que se copió mal al pasarlo de la computadora a Claude."""
    sin = {k: v for k, v in inv.items() if k != "sello"}
    return hashlib.sha1(json.dumps(sin, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:12]

# ---------- primer tiempo: el inventario, en la computadora ----------
if INVENTARIO:
    leer_ = []
    inv = {"formato": 1, "raiz_nombre": RAIZ.name, "modo": MODO, "generado": HOY, "version_metodo": version_metodo,
           "motivos": {}, "proyectos": {}, "entregables": {}, "sin_sesion": {}}
    def _si_legible(p):
        if leer(p) is not None:
            leer_.append(rel(p)); return True
        return False
    _si_legible(RAIZ / "guia.md")
    _si_legible(RAIZ / "base" / "premisas.md")
    for a in areas_guia:
        carpeta = RAIZ / a["slug"]
        restringida = "restring" in a["lectores"].lower()
        if PUBLICO and restringida:
            continue                      # en público, de un área restringida no se trae nada
        texto = leer(carpeta / "area.md")
        if texto is None:
            inv["motivos"][rel(carpeta / "area.md")] = por_que_no(carpeta / "area.md") or "sin-leer"
            continue
        leer_.append(rel(carpeta / "area.md"))
        indice = parse_indice_proyectos(frontmatter(texto)[1])
        slugs = proyectos_de(carpeta, indice)
        inv["proyectos"][rel(carpeta)] = slugs
        for slug in slugs:
            pc = carpeta / slug
            ref = indice.get(slug, {"descripcion": "", "entregables": {}, "notas": []})
            if PUBLICO and es_declarado(ref, slug, indice):
                continue                  # ni se lee ni se trae
            tp = leer(pc / "proyecto.md")
            if tp is None:
                inv["motivos"][rel(pc / "proyecto.md")] = por_que_no(pc / "proyecto.md") or "sin-leer"
                continue
            leer_.append(rel(pc / "proyecto.md"))
            ses = parse_sesiones(leer(pc / "sesiones.md")) if _si_legible(pc / "sesiones.md") else []
            _si_legible(pc / "decisiones.md")
            cerrado = bool(re.search(r"Proyecto terminado el\s*20\d\d-\d\d-\d\d", seccion(frontmatter(tp)[1], "Estado actual")))
            ss_ = sin_sesion_de(pc, ses, cerrado)
            if ss_:
                inv["sin_sesion"][rel(pc)] = ss_
            d = pc / "entregables"
            try:
                for n in sorted(os.listdir(d)) if d.exists() else []:
                    if n.endswith(".md") and not n.startswith(".") and (d / n).is_file():
                        _si_legible(d / n)
            except OSError:
                pass
            fe = fechas_de_entregables(pc)
            if fe:
                inv["entregables"][rel(pc)] = fe
    inv["fuera"] = fuera_de_la_memoria()
    leer_ = list(dict.fromkeys(leer_))       # un área repetida en guia.md no trae dos veces lo mismo
    inv["huella_leer"] = huella_copia({r: os.path.getsize(RAIZ / r) for r in leer_})
    inv["archivos_leer"] = len(leer_)
    # Huella de la raíz entera tal como la ve el tablero: cada archivo que lee con su tamaño y su fecha de modificación,
    # más lo que el inventario sabe de lo demás (fechas de entregables, trabajo sin sesión, «Claude outputs»), el día y este mismo script.
    # Si coincide con la que guardó la última sincronización, el tablero ya está al día y la puesta al día no tiene que regenerarlo.
    _mt = sorted(f"{unicodedata.normalize('NFC', r)}\t{os.path.getsize(RAIZ / r)}\t{int(os.path.getmtime(RAIZ / r))}" for r in leer_)
    _resto = {k: inv[k] for k in ("modo", "version_metodo", "motivos", "proyectos", "entregables", "sin_sesion", "fuera")}
    inv["huella_raiz"] = hashlib.sha1(json.dumps([HOY, hashlib.sha1(pathlib.Path(__file__).read_bytes()).hexdigest(), _mt, _resto],
                                                 ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    inv["sello"] = sello(inv)
    if SI_CAMBIA and SI_CAMBIA == inv["huella_raiz"]:
        print("AL DIA")
        sys.exit(0)
    if LINEAS:
        print(json.dumps(inv, ensure_ascii=False, separators=(",", ":")))
        print(len(leer_))
        print("\n".join(leer_))
    else:
        print(json.dumps({"leer": leer_, "inventario": inv}, ensure_ascii=False, separators=(",", ":")))
    sys.exit(0)

# ---------- segundo tiempo: la copia tiene que ser exactamente la de «leer» ----------
if INV is not None:
    if INV.get("sello") != sello(INV):
        sys.stderr.write("El inventario no llegó entero o se copió con algún cambio: vuelve a escribir la primera línea del paso del inventario, tal cual.\n")
        sys.exit(4)
    _copiados = {}
    for raiz_, dirs, files in os.walk(RAIZ):
        dirs[:] = [x for x in dirs if not x.startswith(".")]
        for f in files:
            if not f.startswith("."):
                _copiados[rel(os.path.join(raiz_, f))] = os.path.getsize(os.path.join(raiz_, f))
    if huella_copia(_copiados) != INV.get("huella_leer"):
        sys.stderr.write(f"La copia no coincide con el inventario: trae {len(_copiados)} archivos y el inventario pide {INV.get('archivos_leer')}, "
                         "o alguno llegó con otro tamaño. Espera unos segundos y repite; si sigue, vacía la carpeta de la copia y vuelve a traer los archivos.\n")
        sys.exit(3)

docs = {"meta": {}, "areas": {}, "proyectos": {}}
orden_area = 0
for a in areas_guia:
    orden_area += 1
    carpeta = RAIZ / a["slug"]
    texto = leer(carpeta / "area.md")
    area_doc = {
        "slug": a["slug"], "nombre": a["slug"], "que": a["que"], "dueno": a["dueno"], "cuenta": a["cuenta"],
        "lectores": a["lectores"], "restringido": "restring" in a["lectores"].lower(), "orden": orden_area,
        "prioridades": [], "actualizado": None, "legible": texto is not None, "proyectos": [],
    }
    if texto is None or (PUBLICO and area_doc["restringido"]):
        area_doc["legible"] = False
        # por qué no se muestra: declarada restringida, sin acceso, o la carpeta no está en esta computadora
        area_doc["motivo"] = "declarada" if (PUBLICO and area_doc["restringido"]) else motivo_de(carpeta / "area.md")
        docs["areas"][a["slug"]] = area_doc
        continue
    fm, cuerpo = frontmatter(texto)
    area_doc["nombre"] = titulo_h1(cuerpo) or a["slug"]
    area_doc["actualizado"] = fm.get("actualizado")
    area_doc["prioridades"] = bullets(seccion(cuerpo, "Prioridades ahora"))
    area_doc["que_largo"] = seccion(cuerpo, "Qué es")
    pan = seccion(cuerpo, "Panorama").strip()
    mpan = re.match(r"^(20\d\d-\d\d-\d\d)\s*·\s*(.+)$", pan, re.S)
    area_doc["panorama"] = {"fecha": mpan.group(1), "texto": mpan.group(2).strip()} if mpan else ({"fecha": None, "texto": pan} if pan else None)
    indice = parse_indice_proyectos(cuerpo)
    slugs = proyectos_de(carpeta, indice)
    orden_p = 0
    for slug in slugs:
        orden_p += 1
        pc = carpeta / slug
        pid = f"{a['slug']}--{slug}"
        area_doc["proyectos"].append(pid)
        ref = indice.get(slug, {"descripcion": "", "entregables": {}, "notas": []})
        declarado = es_declarado(ref, slug, indice)
        tp = None if (PUBLICO and declarado) else leer(pc / "proyecto.md")
        pdoc = {
            "id": pid, "area": a["slug"], "slug": slug, "nombre": slug, "orden": orden_p,
            "indice_descripcion": ref["descripcion"], "indice_notas": ref["notas"],
            "legible": tp is not None, "restringido": tp is None,
        }
        if tp is None:
            pdoc["motivo"] = "declarado" if (PUBLICO and declarado) else motivo_de(pc / "proyecto.md")
            docs["proyectos"][pid] = pdoc
            continue
        fm, cuerpo = frontmatter(tp)
        pdoc.update({
            "nombre": titulo_h1(cuerpo) or slug,
            "estado_cabecera": fm.get("estado"), "actualizado": fm.get("actualizado"),
            "objetivo": seccion(cuerpo, "Objetivo"),
            "terminado": seccion(cuerpo, "Terminado significa"),
            "alcance": seccion(cuerpo, "Alcance"),
            "quien": seccion(cuerpo, "Quién participa"),
            "estado_actual": seccion(cuerpo, "Estado actual"),
            "en_corto": seccion(cuerpo, "En corto"),
            "siguientes_pasos": lineas_no_vacias(seccion(cuerpo, "Siguientes pasos")),
        })
        pdoc["estado_resumen"] = primer_parrafo(pdoc["estado_actual"])
        pdoc["cerrado"] = bool(re.search(r"Proyecto terminado el\s*20\d\d-\d\d-\d\d", pdoc["estado_actual"]))
        mq = re.search(r"Dueño:\s*(.+)", pdoc["quien"])
        pdoc["dueno"] = mq.group(1).strip() if mq else a["dueno"]
        mc = re.search(r"Consumen esto:\s*(.+)", pdoc["quien"])
        pdoc["consumen"] = mc.group(1).strip() if mc else ""
        ses = parse_sesiones(leer(pc / "sesiones.md"))
        reales = [s_ for s_ in ses if not es_sesion_de_tarea(s_["titulo"])]
        ultima_real = reales[0]["fecha"] if reales else None
        # pasos con fecha. Una fecha más de 30 días anterior a la última sesión (o, sin sesiones, a «actualizado»)
        # se toma por contexto viejo, no por plazo. No se mide desde «actualizado» cuando hay sesión, porque la
        # tarea lo mueve al cerrar un paso y escondería los plazos vencidos de los demás.
        pasos = []
        base_ref = ultima_real if fecha_valida(ultima_real) else (pdoc.get("actualizado") if fecha_valida(pdoc.get("actualizado")) else HOY)
        ref_fecha = datetime.date.fromisoformat(base_ref) - datetime.timedelta(days=30)
        for l in pdoc["siguientes_pasos"]:
            # una fecha es plazo solo si el texto la trata como tal; las que cuentan algo pasado son contexto
            fs = [f for f in plazos_en(l) if f >= ref_fecha.isoformat()]
            texto = re.sub(r"^-\s*", "", l)
            cab = bool(re.match(r"^[A-Za-zÁÉÍÓÚáéíóúñÑ][^.]{0,30}:$", texto.strip()))
            p_ = {"texto": texto, "fecha": min(fs) if fs else None}
            if not cab:
                p_["naturaleza"] = naturaleza(texto)
                p_["temas"] = sorted(tokens_tema(texto))
                p_.update(senales(texto, area_doc, pdoc))
                if p_["naturaleza"] in ("rutina", "caducidad") and p_["fecha"]:
                    # una revisión periódica o una caducidad no vence: se revisa; el tablero la muestra aparte
                    p_["revisar"] = p_["fecha"]; p_["fecha"] = None
            pasos.append(p_)
        pdoc["pasos"] = pasos
        dec = parse_decisiones(leer(pc / "decisiones.md"))
        pdoc["decisiones_total"] = sum(1 for d_ in dec if d_.get("tipo") != "cuestionamiento")
        pdoc["decisiones"] = dec
        pdoc["sesiones_total"] = len(ses)
        # fechas de las sesiones de trabajo de los últimos 90 días (sin las de tarea): para la actividad por semana del tablero
        _lim = (datetime.date.fromisoformat(HOY) - datetime.timedelta(days=90)).isoformat()
        pdoc["sesiones_fechas"] = sorted({s["fecha"] for s in reales if fecha_valida(s["fecha"]) and s["fecha"] >= _lim}, reverse=True)
        pdoc["sesiones"] = [{"fecha": s["fecha"], "titulo": s["titulo"]} for s in ses[:5]] if PUBLICO else ses[:5]
        pdoc["ultima_sesion"] = ultima_real
        # trabajo sin sesión: archivos que cambiaron después de la última entrada de la bitácora, sea de una
        # sesión o de una tarea que dejó su línea «(tarea)». Solo se mira la fecha de modificación, nunca el
        # contenido; proyecto.md no cuenta, porque la tarea del tablero lo toca al aplicar fechas, y restringido/ no se mira.
        ss_ = sin_sesion_de(pc, ses, pdoc["cerrado"])
        if ss_:
            pdoc["sin_sesion"] = ss_
        pdoc["entregables"] = entregables_de(pc, ref["entregables"])
        pdoc["entregables_vigentes"] = sum(1 for e in pdoc["entregables"] if e["estado"] == "vigente")
        docs["proyectos"][pid] = pdoc
    docs["areas"][a["slug"]] = area_doc

# ---------- cuestionamientos: quién cuestionó qué, y si el dueño ya respondió ----------
respuestas = set()
for pid, pdoc in docs["proyectos"].items():
    for d_ in pdoc.get("decisiones") or []:
        if d_.get("responde"):
            q, i = ref_decision(d_["responde"])
            if q: respuestas.add((q, i))
# una premisa nueva que reemplaza a P<n> responde a los cuestionamientos de P<n> anteriores a ella (contrato, sección 4)
reemplazos = {p_["reemplaza"]: p_["fecha"] for p_ in premisas if p_["reemplaza"]}
cuestionamientos = []
for pid, pdoc in docs["proyectos"].items():
    for d_ in pdoc.get("decisiones") or []:
        if d_.get("tipo") != "cuestionamiento":
            continue
        q, i = ref_decision(d_.get("cuestiona"))
        abierto = (pid, d_["id"]) not in respuestas
        if abierto and q == "premisa" and i in reemplazos and (reemplazos[i] or "9999") >= (d_["fecha"] or ""):
            abierto = False
        c = {"desde": pid, "id": d_["id"], "fecha": d_["fecha"], "titulo": d_["titulo"], "planteo": d_.get("planteo", ""),
             "porque": d_.get("porque", ""), "a_proyecto": q, "a_id": i, "abierto": abierto}
        d_["abierto"] = c["abierto"]
        cuestionamientos.append(c)
        if q and q != "premisa" and q in docs["proyectos"]:
            for t in docs["proyectos"][q].get("decisiones") or []:
                if t["id"] == i:
                    t.setdefault("cuestionado_por", []).append({k: c[k] for k in ("desde", "id", "fecha", "titulo", "planteo", "abierto")})
            if c["abierto"]:
                docs["proyectos"][q]["cuestionamientos_abiertos"] = docs["proyectos"][q].get("cuestionamientos_abiertos", 0) + 1
cuestionamientos.sort(key=lambda c: c["fecha"], reverse=True)

# ---------- grupos candidatos: pasos de proyectos distintos que comparten un tema ----------
por_tema = {}
for pid, pdoc in docs["proyectos"].items():
    if pdoc.get("cerrado") or not pdoc.get("legible"): continue
    for s_ in pdoc.get("pasos", []):
        if "naturaleza" not in s_: continue
        for t in s_["temas"]:
            por_tema.setdefault(t, []).append({"proyecto": pid, "paso": s_["texto"], "naturaleza": s_["naturaleza"]})
candidatos = []
for t, lista in por_tema.items():
    proys = {x["proyecto"] for x in lista}
    if len(lista) >= 2 and (len(proys) >= 2 or len(lista) >= 3):
        candidatos.append({"tema": t, "proyectos": sorted(proys), "pasos": lista})
candidatos.sort(key=lambda c: (-len(c["proyectos"]), -len(c["pasos"])))
# puntuación por paso: prioridad del área (3), cliente o dinero (2), desbloquea a otros proyectos (2)
temas_cruzados = {c["tema"] for c in candidatos if len(c["proyectos"]) >= 2}
for pid, pdoc in docs["proyectos"].items():
    for s_ in pdoc.get("pasos", []):
        if "naturaleza" not in s_: continue
        s_["desbloquea"] = bool(set(s_["temas"]) & temas_cruzados)
        pts = (3 if s_.get("prioridad_area") else 0) + (2 if s_.get("cliente_o_dinero") else 0) + (2 if s_["desbloquea"] else 0)
        if s_["naturaleza"] in ("rutina", "caducidad"): pts = 0
        s_["puntos"] = pts
# los candidatos no van a la base (la página no los lee): quedan en salida/meta/enfoque-candidatos.json para «Por dónde empezar»,
# con una huella de grupos y prioridades para saber si cambió algo desde la última vez sin releer nada
_prios = {s_: docs["areas"][s_].get("prioridades", []) for s_ in sorted(docs["areas"])}
_huella_cand = hashlib.sha1(json.dumps([candidatos[:25], _prios], ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]
enfoque_candidatos = {"generado": HOY, "huella": _huella_cand, "grupos": candidatos[:25]}

fuera = fuera_de_la_memoria()

docs["meta"]["estado"] = {
    "organizacion": org, "snapshot": HOY, "sincronizado": datetime.datetime.now(TZ).isoformat(timespec="minutes"),
    "version_metodo": version_metodo, "contexto_comun": contexto_comun, "administra": administra,
    "areas": [a["slug"] for a in areas_guia], "fuente": "Generado desde la raíz con generar_vista.py", "tarea": TAREA, "tarea_manual": TAREA_MANUAL,
    "version_tablero": VERSION_PLUGIN, "modo": MODO,
    "fuera": fuera, "premisas": premisas, "cuestionamientos": cuestionamientos,
}
if INV is not None and INV.get("huella_raiz"):
    docs["meta"]["estado"]["huella_raiz"] = INV["huella_raiz"]
if COLA_RETENIDA is not None:
    docs["meta"]["estado"]["cola_retenida"] = sorted(str(x) for x in COLA_RETENIDA)

# ---------- escribir ----------
# Cada documento lleva una huella de su contenido (sin la hora de sincronización) para que la puesta al día
# suba solo los que cambiaron; indice.json lista cada archivo con su huella y su tamaño.
def huella(data):
    sin = {k: v for k, v in data.items() if k not in ("sincronizado", "huella", "huella_raiz", "cola_retenida")}
    return hashlib.sha1(json.dumps(sin, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]
indice_archivos = []
for col, items in docs.items():
    for did, data in items.items():
        data["huella"] = huella(data)
        d = OUT / col
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"{did}.json"
        p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        indice_archivos.append({"coleccion": col, "doc_id": did, "archivo": str(p.relative_to(OUT)), "huella": data["huella"], "bytes": p.stat().st_size})
(OUT / "meta").mkdir(parents=True, exist_ok=True)
(OUT / "meta" / "enfoque-candidatos.json").write_text(json.dumps(enfoque_candidatos, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "indice.json").write_text(json.dumps(indice_archivos, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(docs['areas'])} áreas, {len(docs['proyectos'])} proyectos, snapshot {HOY}")
