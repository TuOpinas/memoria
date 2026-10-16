#!/usr/bin/env python3
"""Genera los documentos de la Vista a partir de una raíz del método Memoria.

Lee solo la superficie pública: guia.md, cada area.md y, de cada proyecto,
proyecto.md, decisiones.md, sesiones.md y las cabeceras de entregables/.
Nunca abre fuentes/, taller/, restringido/ ni base/ (salvo base/premisas.md, que es de toda la organización): de fuentes/ y taller/ solo mira las fechas
de modificación, para el aviso de trabajo sin sesión.

Uso: generar_vista.py <raiz> <carpeta-de-salida> [--modo publico|completo] [--tarea <id de la tarea programada que regenera la vista>] [--version <versión del plugin que lo ejecuta>]
La carpeta de salida va fuera de la raíz (es derivada y se regenera entera); nunca dentro de la carpeta de la organización.

Dos modos. «publico» (el de siempre si no se dice otro): la superficie pública del contrato. De un área cuya columna
«Quién la lee» en guia.md dice «Restringida», y de un proyecto cuya línea del índice de area.md empieza por «restringido» o que no está en ese índice,
solo nombre y dueño, aunque la cuenta que corre el script pueda leerlos; de cada sesión, solo fecha y título.
«completo»: todo lo que la cuenta pueda leer, con las cinco sesiones más recientes enteras. Un tablero completo no se comparte.
En los dos modos, lo que la cuenta no puede leer sale como restringido.
Escribe un JSON por documento: meta/estado.json, areas/<slug>.json,
proyectos/<area>--<slug>.json, cada uno con una huella de su contenido; un indice.json con la lista de archivos, huellas y
tamaños; y meta/enfoque-candidatos.json, que no va a la base: lo usa la puesta al día para «Por dónde empezar».
"""
import sys, os, re, json, datetime, pathlib, hashlib
try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Mexico_City")
except Exception:
    TZ = datetime.timezone.utc

RAIZ = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2])
def _arg(nombre):
    return sys.argv[sys.argv.index(nombre) + 1] if nombre in sys.argv and len(sys.argv) > sys.argv.index(nombre) + 1 else None
TAREA = _arg("--tarea")
VERSION_PLUGIN = _arg("--version")
# --ruta se acepta por compatibilidad con tareas viejas y no se guarda: la ruta de Drive lleva el correo de la persona
MODO = (_arg("--modo") or "publico").lower()
if MODO not in ("publico", "completo"):
    sys.exit("--modo admite publico o completo")
PUBLICO = MODO == "publico"
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
metodo = leer(RAIZ / "metodo.md") or ""
version_metodo = ""
m = re.search(r"(\d+\.\d+(?:\.\d+)?)", metodo.split("\n")[0]) if metodo else None
if m:
    version_metodo = m.group(1)
org = titulo_h1(guia).split("·")[0].strip() or RAIZ.name

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

def entregables_de(carpeta, indice):
    out = []
    d = carpeta / "entregables"
    if not d.exists():
        return out
    try:
        nombres = sorted(os.listdir(d))
    except PermissionError:
        return out
    for n in nombres:
        p = d / n
        if n.startswith(".") or p.is_dir():
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
            try:
                ent["actualizado"] = datetime.datetime.fromtimestamp(p.stat().st_mtime, TZ).date().isoformat()
                ent["fecha_de_archivo"] = True
            except OSError:
                pass
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

def senales(paso_texto, area_doc, pdoc, todos):
    """Señales objetivas de importancia. Vencido no cuenta, por decisión del 2026-10-08."""
    sig = PALABRAS_SIG(paso_texto)
    prio = None
    for i, pr in enumerate(area_doc.get("prioridades", [])):
        if len(sig & PALABRAS_SIG(pr)) >= 3: prio = i + 1; break
    cliente = pdoc["area"] == "clientes" or bool(re.search(r"\b(cliente|propuesta|contrato|firma|factur\w*|cobro|precio|impi|acuerdo de confidencialidad)\b", paso_texto.lower()))
    return {"prioridad_area": prio, "cliente_o_dinero": cliente}

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
        area_doc["motivo"] = "declarada" if (PUBLICO and area_doc["restringido"]) else (por_que_no(carpeta / "area.md") or "sin-leer")
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
    # proyectos: los del índice más cualquier carpeta con proyecto.md
    slugs = list(indice.keys())
    try:
        for n in sorted(os.listdir(carpeta)):
            if (carpeta / n).is_dir() and not n.startswith(".") and n not in slugs and (carpeta / n / "proyecto.md").exists():
                slugs.append(n)
    except PermissionError:
        pass
    orden_p = 0
    for slug in slugs:
        orden_p += 1
        pc = carpeta / slug
        pid = f"{a['slug']}--{slug}"
        area_doc["proyectos"].append(pid)
        ref = indice.get(slug, {"descripcion": "", "entregables": {}, "notas": []})
        # se declara restringido el proyecto cuya línea del índice empieza por «restringido»; mencionar que una parte suya lo está no cuenta.
        # En público, un proyecto que no está en el índice del área tampoco se muestra: sin su línea no se sabe si es restringido
        declarado = bool(re.match(r"^[\W_]*restringid[oa]\b", ref["descripcion"], re.I)) or (PUBLICO and slug not in indice)
        tp = None if (PUBLICO and declarado) else leer(pc / "proyecto.md")
        pdoc = {
            "id": pid, "area": a["slug"], "slug": slug, "nombre": slug, "orden": orden_p,
            "indice_descripcion": ref["descripcion"], "indice_notas": ref["notas"],
            "legible": tp is not None, "restringido": tp is None,
        }
        if tp is None:
            pdoc["motivo"] = "declarado" if (PUBLICO and declarado) else (por_que_no(pc / "proyecto.md") or "sin-leer")
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
                p_.update(senales(texto, area_doc, pdoc, None))
                if p_["naturaleza"] in ("rutina", "caducidad") and p_["fecha"]:
                    # una revisión periódica o una caducidad no vence: se revisa; el tablero la muestra aparte
                    p_["revisar"] = p_["fecha"]; p_["fecha"] = None
            pasos.append(p_)
        pdoc["pasos"] = pasos
        dec = parse_decisiones(leer(pc / "decisiones.md"))
        pdoc["decisiones_total"] = sum(1 for d_ in dec if d_.get("tipo") != "cuestionamiento")
        pdoc["decisiones"] = dec
        pdoc["sesiones_total"] = len(ses)
        pdoc["sesiones"] = [{"fecha": s["fecha"], "titulo": s["titulo"]} for s in ses[:5]] if PUBLICO else ses[:5]
        pdoc["ultima_sesion"] = ultima_real
        # trabajo sin sesión: archivos que cambiaron después de la última entrada de la bitácora, sea de una
        # sesión o de una tarea que dejó su línea «(tarea)». Solo se mira la fecha de modificación, nunca el
        # contenido; proyecto.md no cuenta, porque la tarea del tablero lo toca al aplicar fechas, y restringido/ no se mira.
        ultima_entrada = ses[0]["fecha"] if ses and fecha_valida(ses[0]["fecha"]) else None
        if ultima_entrada and not pdoc["cerrado"]:
            donde, ultimo = {}, None
            objetivos = [("entregables", pc / "entregables"), ("taller", pc / "taller"), ("fuentes", pc / "fuentes")]
            for nombre, d in objetivos:
                for raiz_, dirs, files in os.walk(d) if d.exists() else []:
                    dirs[:] = [x for x in dirs if not x.startswith(".")]
                    for f in files:
                        if f.startswith("."):
                            continue
                        try:
                            fm_ = datetime.datetime.fromtimestamp(os.stat(os.path.join(raiz_, f)).st_mtime, TZ).date().isoformat()
                        except OSError:
                            continue
                        if fm_ > ultima_entrada:
                            donde[nombre] = donde.get(nombre, 0) + 1
                            ultimo = max(ultimo or fm_, fm_)
            try:
                fd = datetime.datetime.fromtimestamp(os.stat(pc / "decisiones.md").st_mtime, TZ).date().isoformat()
                if fd > ultima_entrada:
                    donde["decisiones"] = 1; ultimo = max(ultimo or fd, fd)
            except OSError:
                pass
            if donde:
                pdoc["sin_sesion"] = {"desde": ultima_entrada, "ultimo": ultimo, "donde": donde, "archivos": sum(donde.values())}
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

# ---------- carpetas de la raíz que no son de ningún área ----------
# «Claude outputs» es donde la app de Claude deja lo que produce; cualquier otra carpeta suelta en la
# raíz también queda fuera de la memoria. Solo se cuentan archivos y fechas; los nombres, solo en completo.
fuera = []
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
            try:
                fecha = datetime.datetime.fromtimestamp(os.stat(os.path.join(raiz_, f)).st_mtime, TZ).date().isoformat()
            except OSError:
                continue
            arch.append((fecha, os.path.relpath(os.path.join(raiz_, f), RAIZ / n)))
    if not arch: continue
    arch.sort(reverse=True)
    item = {"carpeta": n, "de_claude": n.lower() == "claude outputs", "archivos": len(arch), "ultimo": arch[0][0], "primero": arch[-1][0]}
    if not PUBLICO:
        item["nombres"] = [{"fecha": f_, "nombre": n_} for f_, n_ in arch[:40]]
    fuera.append(item)

docs["meta"]["estado"] = {
    "organizacion": org, "snapshot": HOY, "sincronizado": datetime.datetime.now(TZ).isoformat(timespec="minutes"),
    "version_metodo": version_metodo, "contexto_comun": contexto_comun, "administra": administra,
    "areas": [a["slug"] for a in areas_guia], "fuente": "Generado desde la raíz con generar_vista.py", "tarea": TAREA,
    "version_tablero": VERSION_PLUGIN, "modo": MODO,
    "fuera": fuera, "premisas": premisas, "cuestionamientos": cuestionamientos,
}

# ---------- escribir ----------
# Cada documento lleva una huella de su contenido (sin la hora de sincronización) para que la puesta al día
# suba solo los que cambiaron; indice.json lista cada archivo con su huella y su tamaño.
def huella(data):
    sin = {k: v for k, v in data.items() if k not in ("sincronizado", "huella")}
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
