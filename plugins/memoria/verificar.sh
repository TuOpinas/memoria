#!/usr/bin/env bash
# Comprueba la raíz de una organización contra el contrato, sin escribir nada. De cada .md
# lee la cabecera y busca enlaces wiki y rutas absolutas; no lee fuentes/ ni restringido/.
# Una carpeta que no se deja leer (restringida para esta cuenta) se salta sin más.
#
#   ./verificar.sh <ruta-a-la-raiz>
#
# Sale con 1 si hay hallazgos, 0 si la raíz está limpia.
set -euo pipefail
RAIZ="${1:?Falta la ruta de la raíz}"
python3 - "$RAIZ" <<'PY'
import os, re, sys, unicodedata
# --- quién escribe: «Quién es quién» y la tabla de áreas de guia.md, y la línea «Colabora:» de un proyecto ---
# La misma función en abrir.py, cerrar.py, permisos.py, migrar_estructura.py, aplicar_cambios.py, barrido.py,
# generar_vista.py y verificar.sh (cada uno se descarga suelto); pruebas/sesion/probar_cuentas.py comprueba que las
# ocho copias son idénticas. Desde la 1.25 cada persona está una vez en «Quién es quién» («Nombre · cuenta@») y la tabla
# de áreas la nombra por su nombre en Responsable y Colabora; hasta la 1.24, la celda Cuenta llevaba los correos. Se
# leen las dos formas: con registro y columna Colabora, por nombre; sin ellos, la celda Cuenta como siempre.
import unicodedata
CORREO = re.compile(r"[\w.+'-]+@[\w-]+(?:\.[\w-]+)*")
PALABRA_COLABORA = re.compile(r"\bco-?labor\w*\s*:?", re.I)
LINEA_COLABORA = re.compile(r"^\s*[-*]?\s*\**\s*colabora[n]?\s*\**\s*:", re.I)
def cuentas(celda):
    """(responsable, colaboran, aviso) de una celda Cuenta: «resp@x · colabora: a@x, b@x». Falla cerrado:
    con más de un correo antes de la palabra, o ninguno, nadie es responsable; cualquier palabra que empiece por
    «colabor» separa, para que «colaboradora:» o «colabora» sin dos puntos no conviertan a nadie en responsable."""
    texto = (celda or "").lower()
    partes = PALABRA_COLABORA.split(texto, maxsplit=1)
    antes = set(CORREO.findall(partes[0]))
    despues = set(CORREO.findall(partes[1])) if len(partes) > 1 else set()
    aviso = None
    if len(antes) > 1:
        aviso = "más de un correo antes de «colabora:»; nadie es responsable hasta que se corrija"
        antes = set()
    elif not antes:
        aviso = "sin el correo del responsable"
    elif len(partes) > 1 and not re.search(r"\bcolabora\s*:", texto):
        aviso = "la palabra para quien colabora va escrita «colabora:»"
    return antes, despues, aviso
def clave_nombre(n):
    """Cómo se comparan dos nombres: NFC (Mac y Windows escriben las tildes distinto), sin mayúsculas, sin negritas ni
    comillas, y con los espacios juntos. Nada más: sin acentos no es el mismo nombre."""
    n = unicodedata.normalize("NFC", n or "").replace(" ", " ")
    return re.sub(r"\s+", " ", re.sub(r"[*_`«»\"]", "", n)).strip(" .,;:").lower()
def registro_personas(guia):
    """«Quién es quién» de guia.md: {"hay", "personas", "nombre": {clave: persona}, "cuenta": {correo: persona}, "avisos"}.
    Una línea es «- Nombre · campo · campo»; los campos: un correo (su cuenta de Claude), «cuentas: a@, b@», «en Drive: x@»,
    «sin cuenta», «sin confirmar», «también: Otra Grafía», «de: Organización», «baja AAAA-MM-DD», «compartida con: Nombre»
    y «registra: Nombre». «?» como nombre es una cuenta que todavía no tiene nombre. Quien está de baja no escribe."""
    m = re.search(r"^##\s+Quién es quién\s*$(.*?)(?=^##\s|\Z)", guia or "", re.M | re.S)
    reg = {"hay": bool(m), "personas": [], "nombre": {}, "cuenta": {}, "avisos": []}
    for l in (m.group(1) if m else "").split("\n"):
        if not re.match(r"^\s*[-*]\s+\S", l):
            continue
        campos = [c.strip() for c in re.split(r"\s+·\s+|\s*·\s*", l.strip()[1:].strip()) if c.strip()]
        if not campos:
            continue
        p = {"nombre": re.sub(r"[*_`]", "", campos[0]).strip(), "cuentas": set(), "drive": set(), "sin_cuenta": False,
             "sin_confirmar": False, "alias": [], "de": "", "baja": "", "compartida": "", "registra": "", "linea": l.strip()}
        if CORREO.fullmatch(p["nombre"].lower()):
            p["cuentas"].add(p["nombre"].lower()); p["nombre"] = "?"
        for c in campos[1:]:
            cl = c.lower()
            if CORREO.fullmatch(cl):
                p["cuentas"].add(cl)
            elif re.match(r"^cuentas?\s*:", cl):
                p["cuentas"] |= set(CORREO.findall(cl))
            elif re.match(r"^(en\s+)?(google\s+)?drive\s*:", cl):
                p["drive"] |= set(CORREO.findall(cl))
            elif re.match(r"^sin\s+cuenta\b", cl):
                p["sin_cuenta"] = True
            elif re.match(r"^sin\s+confirmar\b", cl):
                p["sin_confirmar"] = True
            elif re.match(r"^tambi[eé]n\s*:", cl):
                p["alias"] += [a.strip() for a in re.split(r",|\s+y\s+", c.split(":", 1)[1]) if a.strip()]
            elif re.match(r"^de\s*:", cl):
                p["de"] = c.split(":", 1)[1].strip()
            elif re.match(r"^baja\b", cl):
                p["baja"] = (re.search(r"20\d\d-\d\d-\d\d", c) or [""])[0] or "sí"
            elif re.match(r"^compartida\s+con\s*:", cl):
                p["compartida"] = c.split(":", 1)[1].strip()
            elif re.match(r"^registra\s*:", cl):
                p["registra"] = c.split(":", 1)[1].strip()
            else:
                reg["avisos"].append(f"«{p['nombre']}»: no se entiende «{c}» (van un correo, «sin cuenta», «en Drive: correo», «también: nombre», «de: organización» o «baja AAAA-MM-DD»)")
        if p["sin_cuenta"] and p["cuentas"]:
            reg["avisos"].append(f"«{p['nombre']}» dice «sin cuenta» y lleva una cuenta: se queda la cuenta")
            p["sin_cuenta"] = False
        if not p["cuentas"] and not p["sin_cuenta"] and not p["de"]:
            reg["avisos"].append(f"«{p['nombre']}» no lleva ni su cuenta ni «sin cuenta»")
        reg["personas"].append(p)
        for n in ([p["nombre"]] if p["nombre"] != "?" else []) + p["alias"]:
            k = clave_nombre(n)
            if k in reg["nombre"] and reg["nombre"][k] is not p:
                reg["avisos"].append(f"«{n}» está dos veces: dos personas con el mismo nombre se distinguen con el segundo apellido o una inicial")
            reg["nombre"].setdefault(k, p)
        for c in p["cuentas"]:
            if c in reg["cuenta"]:
                reg["avisos"].append(f"la cuenta {c} está en dos líneas («{reg['cuenta'][c]['nombre']}» y «{p['nombre']}»)")
            reg["cuenta"].setdefault(c, p)
    return reg
def persona(nombre, reg):
    """La persona del registro con ese nombre o alias; None si no está."""
    return (reg or {}).get("nombre", {}).get(clave_nombre(re.sub(r"\s*\([^)]*\)", "", nombre or "")))
def nombres_de(texto):
    """Los nombres de una celda o una línea («Colabora: Ana Ruiz, Luis Mejía»): separados por comas, «;» o « y », sin
    la etiqueta del principio ni lo que va entre paréntesis."""
    t = re.sub(r"^\s*[-*]?\s*\**\s*(?:colabora[n]?|lo leen?|responsable)\s*\**\s*:\s*\**", "", texto or "", flags=re.I)
    t = re.sub(r"\s*\([^)]*\)", "", t)
    return [n.strip(" .*") for n in re.split(r",|;|\s+y\s+", t) if n.strip(" .*") and n.strip(" .*").lower() not in ("—", "-", "nadie", "ninguno", "ninguna")]
def cuentas_de_nombres(texto, reg):
    """(cuentas, nombres que no están en el registro) de una celda con nombres. Quien está de baja o sin cuenta no da
    ninguna; un correo escrito tal cual («Nombre (correo)», el alta provisional de un proyecto) cuenta."""
    out, faltan = set(CORREO.findall((texto or "").lower())), []
    for n in nombres_de(texto):
        p = persona(n, reg)
        if p is None:
            if not CORREO.fullmatch(n.lower()):
                faltan.append(n)
        elif not p["baja"]:
            out |= p["cuentas"]
    return out, faltan
def columnas_personas(cab):
    """Dónde están Responsable, Cuenta y Colabora en el encabezado de la tabla de áreas (None si no están)."""
    n = [re.sub(r"[*_`]", "", x).strip().lower() for x in cab]
    pos = lambda *ns: next((i for i, x in enumerate(n) if x in ns), None)
    return {"responsable": pos("responsable", "dueño", "dueno"), "cuenta": pos("cuenta"), "colabora": pos("colabora", "colaboran")}
def fila_cuentas(cab, celdas, reg):
    """(responsable, colaboran, aviso) de una fila de la tabla de áreas, como cuentas(): con la columna Cuenta (hasta la
    1.24), de sus correos; con la columna Colabora y «Quién es quién» (1.25), por los nombres. Sin encabezado reconocible,
    la cuarta columna como Cuenta, como siempre. Falla cerrado: un responsable que no está en el registro no es nadie."""
    col = columnas_personas(cab)
    if col["cuenta"] is not None or col["colabora"] is None:
        i = col["cuenta"] if col["cuenta"] is not None else 3
        return cuentas(celdas[i] if i < len(celdas) else "")
    if not (reg or {}).get("hay"):
        return set(), set(), "la tabla nombra a quien colabora por su nombre y guia.md no tiene «Quién es quién»"
    resp = celdas[col["responsable"] if col["responsable"] is not None else 2] if len(celdas) > 2 else ""
    rn = nombres_de(re.sub(r"\s*\((?=[a-záéíóúñ`])[^)]*\)", "", resp))
    avisos = []
    de = set()
    if len(rn) != 1:
        avisos.append("el responsable es una sola persona del registro" if rn else "sin responsable")
    else:
        p = persona(rn[0], reg)
        if p is None:
            avisos.append(f"«{rn[0]}» no está en «Quién es quién»")
        elif p["baja"]:
            avisos.append(f"«{p['nombre']}» está de baja")
        elif p["cuentas"]:
            de = set(p["cuentas"])
        elif p["registra"] and persona(p["registra"], reg) and persona(p["registra"], reg)["cuentas"]:
            de = set(persona(p["registra"], reg)["cuentas"])
        else:
            avisos.append(f"«{p['nombre']}» no tiene cuenta: o la tiene, o su línea dice «registra: Nombre» de quien escribe por ella")
    co, faltan = cuentas_de_nombres(celdas[col["colabora"]] if col["colabora"] < len(celdas) else "", reg)
    avisos += [f"«{n}» (Colabora) no está en «Quién es quién»" for n in faltan]
    return de, co - de, "; ".join(avisos) or None
def cuentas_contexto(linea, reg):
    """Las cuentas de quien responde por el contexto: la que va entre paréntesis en «Contexto común: Nombre (correo)»
    (hasta la 1.24) o la del registro para ese nombre (1.25)."""
    t = (linea or "").split(":", 1)[-1]
    c = set(CORREO.findall(t.lower()))
    if c:
        return c
    p = persona(t.strip().rstrip("."), reg)
    return set(p["cuentas"]) if p and not p["baja"] else set()
def nombre_de(cuenta, reg):
    """El nombre del registro de esa cuenta, o "" si no está (o es «?»)."""
    p = (reg or {}).get("cuenta", {}).get((cuenta or "").lower())
    return p["nombre"] if p and p["nombre"] != "?" else ""
def colaboran_en(quien, reg=None):
    """Las cuentas de las líneas «Colabora:» de «Quién participa» de un proyecto (todas las líneas): los correos escritos
    tal cual y, con registro, las de los nombres."""
    out = set()
    for l in (quien or "").split("\n"):
        if LINEA_COLABORA.match(l):
            out |= cuentas_de_nombres(l, reg)[0] if reg else set(CORREO.findall(l.lower()))
    return out
# --- fin de quién escribe ---

raiz = sys.argv[1]
ESTADOS = {"borrador", "vigente", "reemplazado"}
PROHIBIDAS = {"varios", "otros", "temp", "borrador", "metodo", "plantillas"}
hallazgos = set()
sin_afirma = []   # entregables y taller sin «aportacion:» (o «afirma:», su nombre hasta la 1.21): se cuentan, no bloquean
sin_basado = []   # taller sin «basado_en»: se cuenta, no bloquea (obligatoria desde la 1.22 en lo que se crea)
anterior = []     # lo que sigue con la estructura de la 1.21: se cuenta, no bloquea; lo migra la apertura de su responsable o la del responsable de contexto
sin_charset = []  # .html sin <meta charset="utf-8">: abiertos desde la carpeta salen con los acentos rotos
SUELTOS_OK = {"guia.md", "metodo.md", "desktop.ini", "Icon\r"}
ROTADO = re.compile(r"^(sesiones|decisiones)-\d{4}(-\d+)?\.md$")   # el registro que se rota por año

def h(clase, ruta, detalle=""):
    hallazgos.add((clase, ruta, detalle))

def ls(p):
    try:
        return sorted(os.listdir(p))
    except OSError:
        return []

def rel(p):
    return os.path.relpath(p, raiz)

def cabecera(path):
    try:
        txt = open(path, encoding="utf-8-sig", errors="replace").read()
    except OSError:
        return None, ""
    if not txt.startswith("---\n"):
        return None, txt
    fin = txt.find("\n---", 4)
    return (txt[4:fin] if fin != -1 else ""), txt

def nombre_ok(n):
    base = n[:-3] if n.endswith(".md") else n
    if base != base.lower():
        return False
    if any(unicodedata.category(c) == "Mn" for c in unicodedata.normalize("NFD", base)):
        return False
    return re.fullmatch(r"[a-z0-9][a-z0-9-]*", base) is not None

def nombre_con_orden_version_o_fecha(n):
    base = n[:-3] if n.endswith(".md") else n
    return bool(re.match(r"^\d+-", base) or re.search(r"(^|-)v\d+($|-)", base) or re.search(r"\d{4}-\d{2}-\d{2}", base))

def seccion_proyectos(txt):
    m = re.search(r"^## Proyectos\s*\n(.*?)(?=^## |\Z)", txt, re.S | re.M)
    return m.group(1) if m else ""

# --- raíz ---
for req in ("guia.md", "metodo.md", "base/contexto.md", "base/glosario.md", "base/sistemas.md"):
    if not os.path.exists(os.path.join(raiz, req)):
        h("falta en la raíz", req)
for extra in ("base/ajustes.md", "base/plantillas"):
    if os.path.exists(os.path.join(raiz, extra)):
        h("ya no existe en el método", extra, "lo propio de la organización va en guia.md")

areas = []
for nombre in ls(raiz):
    ruta = os.path.join(raiz, nombre)
    if nombre.startswith("."):
        continue
    if os.path.isfile(ruta):
        if nombre not in SUELTOS_OK:
            h("archivo suelto en la raíz", nombre)
        continue
    if nombre in ("base", ".git"):
        continue
    if nombre.lower() == "claude outputs":
        n = sum(1 for _, _, fs in os.walk(ruta) for f in fs if not f.startswith("."))
        if n:
            h("archivos de Claude sin proyecto", nombre, "%d archivo%s: cada uno va a su proyecto («ordena Claude outputs»)" % (n, "" if n == 1 else "s"))
        continue
    areas.append((nombre, ruta))
    if not nombre_ok(nombre) or nombre_con_orden_version_o_fecha(nombre):
        h("nombre de carpeta", nombre, *([] if nombre_ok(nombre) else ["con espacios, mayúsculas o acentos, las referencias a sus decisiones («Afecta a», «Cuestiona a», «Responde a») dejan de funcionar"]))

# --- guia.md: el mapa que leen abrir.py y el tablero ---
# La tabla de áreas es lo que da a cada cuenta su área: una fila con columnas de menos, un encabezado distinto
# de «## Áreas» o una cuenta sin «@» dejan a alguien sin área sin que nadie lo note.
guia_areas = {}
notas_personas = []
REG = registro_personas("")
try:
    guia_txt = open(os.path.join(raiz, "guia.md"), encoding="utf-8-sig", errors="replace").read()
except OSError:
    guia_txt = ""
if guia_txt:
    if not re.search(r"^## Áreas\s*$", guia_txt, re.M):
        h("guia.md sin la sección «## Áreas»", "guia.md", "con ese título exacto; es la que leen abrir.py y el tablero")
    # «Quién es quién» (1.25): cada persona una vez, con su nombre y su cuenta
    REG = registro_personas(guia_txt)
    for _av in REG["avisos"]:
        h("«Quién es quién» mal escrito", "guia.md", _av)
    for _p in REG["personas"]:
        if _p["nombre"] == "?":
            h("cuenta sin nombre en «Quién es quién»", "guia.md", "%s: sigue escribiendo, pero le falta el nombre de la persona" % ", ".join(sorted(_p["cuentas"])))
        elif _p["sin_cuenta"] and not _p["baja"]:
            notas_personas.append("%s no tiene cuenta de Claude («sin cuenta»): no escribe en ninguna área" % _p["nombre"])
    m = re.search(r"^## Áreas\s*\n(.*?)(?=^## |\Z)", guia_txt, re.S | re.M)
    col = None
    for l in (m.group(1) if m else "").split("\n"):
        if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
            continue
        celdas = [c.strip() for c in l.strip().strip("|").split("|")]
        if col is None:
            # por el encabezado: «Responsable» y «Acceso» desde la 1.22; «Dueño» y sin «Acceso» hasta la 1.21
            n_ = [re.sub(r"[*_`]", "", x).strip().lower() for x in celdas]
            pos = lambda *ns, d=None: next((i for i, x in enumerate(n_) if x in ns), d)
            col = {"resp": pos("responsable", "dueño", "dueno", d=2), "cuenta": pos("cuenta", "colabora", d=3), "lee": pos("quién la lee", "quien la lee", d=4), "acceso": pos("acceso")}
            cab_guia = celdas
            NUEVA = columnas_personas(celdas)["cuenta"] is None and columnas_personas(celdas)["colabora"] is not None
            if NUEVA and not REG["hay"]:
                h("guia.md sin «Quién es quién»", "guia.md", "la tabla nombra a las personas por su nombre (columna Colabora): sus cuentas van en «## Quién es quién», una línea por persona")
            if REG["hay"] and not NUEVA:
                h("«Quién es quién» con la columna Cuenta", "guia.md", "con «Quién es quién», la tabla lleva «Colabora» con nombres en lugar de «Cuenta» con correos")
            if col["acceso"] is None or any(x in ("dueño", "dueno") for x in n_):
                anterior.append("guia.md (columnas «Dueño» y «Quién la lee» sin «Acceso»)")
            continue
        slug = celdas[0].strip("`").rstrip("/")
        minimo = max(v for v in col.values() if v is not None) + 1
        if len(celdas) < minimo:
            h("fila de la tabla de áreas con columnas de menos", "guia.md", "«%s» tiene %d y hacen falta %d (%s)" % (slug, len(celdas), minimo, "área, qué es, responsable, cuenta, quién la lee, acceso" if col["acceso"] is not None else "área, qué es, dueño, cuenta, quién la lee")); continue
        guia_areas[slug] = {"dueno": celdas[col["resp"]], "cuenta": celdas[col["cuenta"]]}
        if col["acceso"] is not None and not re.match(r"^[\W_]*(abiert|restringid)[oa]s?\b", celdas[col["acceso"]], re.I):
            h("columna Acceso sin «Abierta» ni «Restringida»", slug, "dice «%s»" % celdas[col["acceso"]])
        _de, _co, _av = fila_cuentas(cab_guia, celdas, REG)
        if _av and NUEVA:
            h("fila de la tabla de áreas que no se deja leer", slug, _av + ": Responsable y Colabora llevan nombres de «Quién es quién»")
        elif _av:
            h("celda Cuenta mal escrita en guia.md", slug, _av + ": primero el correo del responsable y, si hace falta, «· colabora: correo, correo»")
        if NUEVA and col["acceso"] is not None and re.match(r"^[\W_]*restringid", celdas[col["acceso"]], re.I):
            for _n in nombres_de(re.sub(r"^[\W_]*restringid[oa]s?\s*:?", "", celdas[col["lee"]], flags=re.I)):
                if not persona(_n, REG):
                    h("nombre que no está en «Quién es quién»", slug, "«%s», en «Quién la lee»" % _n)
        if not NUEVA and PALABRA_COLABORA.search(celdas[col["cuenta"]]) and not _co:
            h("«colabora:» sin cuentas en guia.md", slug, "detrás de «colabora:» van los correos de quienes colaboran, separados por comas")
        if not os.path.isdir(os.path.join(raiz, slug)):
            h("área del mapa sin carpeta", slug, "está en la tabla de guia.md y no hay carpeta con ese nombre")
    if m and not guia_areas:
        h("tabla de áreas vacía", "guia.md")
    if not re.search(r"^Contexto común", guia_txt, re.M):
        h("guia.md sin «Contexto común»", "guia.md", "la línea que dice quién mantiene guia.md y base/")
    _z = re.search(r"^\s*[-*]?\s*\**\s*zona horaria\s*\**\s*:\s*\**\s*`?\s*([A-Za-z0-9_+-]+(?:/[A-Za-z0-9_+-]+){0,2})", guia_txt, re.M | re.I)
    if _z:
        try:
            from zoneinfo import ZoneInfo
            ZoneInfo(_z.group(1))
        except ImportError:
            pass
        except Exception:
            h("zona horaria no válida en guia.md", "guia.md", "«%s»: tiene que ser una zona como America/Mexico_City o Europe/Madrid" % _z.group(1))

# --- copias en conflicto de Drive: «sesiones (1).md» o «proyecto [Conflict].md» junto a su original ---
CONFLICTO = re.compile(r"^(?P<base>.+?)\s*(\(\d+\)|\[[^\]]*conflict[^\]]*\])\.md$", re.I)
for d_, ds_, fs_ in os.walk(raiz):
    ds_[:] = [x for x in ds_ if not x.startswith(".")]
    for f_ in fs_:
        m_ = CONFLICTO.match(f_)
        if m_ and os.path.isfile(os.path.join(d_, m_.group("base") + ".md")):
            h("copia en conflicto de Drive", rel(os.path.join(d_, f_)), "dos personas escribieron %s.md a la vez: se juntan las dos versiones y la copia va a la papelera" % m_.group("base"))

# --- áreas y proyectos ---
for area, aruta in areas:
    amd = os.path.join(aruta, "area.md")
    if not os.path.exists(amd):
        h("área sin area.md", area); continue
    fm, txt = cabecera(amd)
    if guia_txt and area not in guia_areas:
        h("carpeta de área que no está en guia.md", area, "sin su fila en la tabla de áreas nadie escribe en ella")
    md = re.search(r"^(?:Responsable|Dueñ[oa]): *(.+?)\s*$", txt, re.M)
    if not md and not (guia_txt and REG["hay"]):
        h("área sin responsable", rel(amd))
    # desde la 1.25 no se compara con la celda Responsable de guia.md: la fuente es la tabla, y la línea del area.md se
    # retira con la migración (comparar dos fuentes es lo que daba los falsos «responsable distinto» de 2026-11-02)
    if guia_txt and REG["hay"]:
        for _l in seccion_proyectos(txt).split("\n"):
            _mr = re.match(r"^- `([^`/]+)/?`\s*[—–:-]?\s*[\W_]*restringid[oa]\s*:\s*(?:due[ñn][oa]|responsable)\s+([^.;,]+)", _l, re.I)
            if _mr and not persona(_mr.group(2), REG):
                h("nombre que no está en «Quién es quién»", "%s/%s" % (area, _mr.group(1)), "«%s», responsable en la línea del proyecto restringido de area.md" % _mr.group(2).strip())
    if re.search(r"^## (Panorama|Prioridades ahora)\s*$|^Dueñ[oa]:", txt, re.M):
        anterior.append(rel(amd))
    if "## Proyectos" not in txt:
        h("area.md sin bloque Proyectos", rel(amd))
    bloque = seccion_proyectos(txt)

    for proj in ls(aruta):
        pruta = os.path.join(aruta, proj)
        if not os.path.isdir(pruta) or proj.startswith("."):
            continue
        if not nombre_ok(proj) or nombre_con_orden_version_o_fecha(proj):
            h("nombre de carpeta", rel(pruta), *([] if nombre_ok(proj) else ["con espacios, mayúsculas o acentos, las referencias a sus decisiones («Afecta a», «Cuestiona a», «Responde a») dejan de funcionar"]))
        if not os.path.exists(os.path.join(pruta, "proyecto.md")):
            h("carpeta en un área que no es un proyecto", rel(pruta)); continue

        for req in ("proyecto.md", "decisiones.md", "sesiones.md"):
            if not os.path.exists(os.path.join(pruta, req)):
                h("proyecto incompleto", rel(pruta), "falta " + req)
        for d in ("entregables", "taller", "fuentes"):
            if not os.path.isdir(os.path.join(pruta, d)):
                h("proyecto incompleto", rel(pruta), "falta " + d + "/")

        for x in ls(pruta):
            xr = os.path.join(pruta, x)
            if os.path.isdir(xr) and x not in ("entregables", "taller", "fuentes", "restringido") and not x.startswith("."):
                h("carpeta que la estructura no contempla", rel(xr))
            if x.lower() in PROHIBIDAS:
                h("carpeta prohibida", rel(xr))
            if os.path.isfile(xr) and x.endswith(".md") and x not in ("proyecto.md", "decisiones.md", "sesiones.md") and not ROTADO.match(x):
                h("archivo suelto en la raíz del proyecto", rel(xr))

        # un solo nivel de agrupación dentro de entregables/, taller/ y fuentes/
        for sub in ("entregables", "taller", "fuentes"):
            sruta = os.path.join(pruta, sub)
            if not os.path.isdir(sruta):
                continue
            for g in ls(sruta):
                gr = os.path.join(sruta, g)
                if sub == "taller" and g in ("decisiones.md", "sesiones.md"):
                    h("registro dentro de taller/", rel(gr), "los registros del proyecto son los de su raíz")
                if os.path.isdir(gr) and not g.startswith("."):
                    if sub != "fuentes" and (not nombre_ok(g) or nombre_con_orden_version_o_fecha(g)):
                        h("nombre de carpeta", rel(gr))
                    for gg in ls(gr):
                        if os.path.isdir(os.path.join(gr, gg)) and not gg.startswith("."):
                            h("un nivel de agrupación de más", rel(os.path.join(gr, gg)))

        # restringido/ es plano
        rruta = os.path.join(pruta, "restringido")
        if os.path.isdir(rruta):
            for g in ls(rruta):
                if os.path.isdir(os.path.join(rruta, g)) and not g.startswith("."):
                    h("subcarpeta dentro de restringido/", rel(os.path.join(rruta, g)), "es plano")

        # el bloque Proyectos tiene que listar todos los entregables vigentes,
        # salvo en un proyecto cerrado, que ocupa solo su línea
        pfm, ptxt = cabecera(os.path.join(pruta, "proyecto.md"))
        cerrado = "Proyecto terminado el" in ptxt
        if re.search(r"^## (En corto|Estado actual|Terminado significa)\s*$|^(Dueñ[oa]|Consumen esto):", ptxt or "", re.M) or \
                any(os.path.isfile(os.path.join(pruta, x, "enlaces.md")) for x in ("fuentes", "restringido")):
            anterior.append(rel(os.path.join(pruta, "proyecto.md")))
        _qp = re.search(r"^## Quién participa\s*\n(.*?)(?=^## |\Z)", ptxt or "", re.S | re.M)
        for _l in (_qp.group(1).split("\n") if _qp else []):
            if not (guia_txt and REG["hay"]):
                if LINEA_COLABORA.match(_l) and not re.search(r"\([^)]*@[^)]*\)", _l):
                    h("«Colabora:» sin cuentas en proyecto.md", rel(pruta), "cada persona va como «Nombre Apellido (correo)»: sin la cuenta no se sabe quién escribe")
                continue
            # con «Quién es quién» (1.25), los nombres de un proyecto abierto están en el registro; «Nombre (correo)» de
            # quien aún no está es el alta provisional, que el responsable de contexto pasa al registro
            if cerrado or not re.match(r"^\s*[-*]?\s*\**\s*(colabora[n]?|responsable|lo\s+leen?)\s*\**\s*:", _l, re.I):
                continue
            for _n, _c in re.findall(r"([^,;(:]+?)\s*\(\s*(" + CORREO.pattern + r")\s*\)", _l):
                if _c.lower() not in REG["cuenta"]:
                    notas_personas.append("%s (%s) colabora en %s y no está en «Quién es quién»: el responsable de contexto añade su línea y en el proyecto queda solo el nombre" % (_n.strip(), _c.lower(), rel(pruta)))
            for _n in nombres_de(_l):
                _pp = persona(_n, REG)
                if _pp is None and not CORREO.fullmatch(_n.lower()) and not re.search(re.escape(_n) + r"\s*\([^)]*@", _l):
                    h("nombre que no está en «Quién es quién»", rel(pruta), "«%s», en «Quién participa»" % _n)
                elif _pp and _pp["baja"]:
                    h("persona de baja en un proyecto abierto", rel(pruta), "«%s» está de baja en «Quién es quién»" % _n)
        ed = os.path.join(pruta, "entregables")
        if os.path.isdir(ed) and not cerrado:
            for f in ls(ed):
                if not f.endswith(".md"):
                    continue
                efm, _ = cabecera(os.path.join(ed, f))
                if efm and re.search(r"^estado: *vigente", efm, re.M) and not re.search(r"(?<![\w-])" + re.escape(f[:-3]) + r"(?![\w-])", bloque):
                    h("entregable vigente que no está en el bloque Proyectos", rel(os.path.join(ed, f)))
        if not re.search(r"`" + re.escape(proj) + r"/?`", bloque):
            h("proyecto que no está en el bloque Proyectos de su área", rel(pruta))

# --- los .html: sin charset, abiertos desde la carpeta se ven con los acentos rotos (escribir.md, prohibición 23) ---
for dp, dn, fn in os.walk(raiz):
    dn[:] = [d for d in dn if not d.startswith(".")]
    for f in fn:
        if f.endswith(".html") and not f.startswith("."):
            try:
                cab = open(os.path.join(dp, f), "rb").read(4096).decode("utf-8", "ignore").lower()
            except OSError:
                continue
            if not re.search(r"<meta[^>]+charset\s*=\s*['\"]?utf-8", cab):
                sin_charset.append(rel(os.path.join(dp, f)))

# --- todos los .md ---
for dp, dn, fn in os.walk(raiz):
    dn[:] = [d for d in dn if not d.startswith(".") and not (dp == raiz and d.lower() == "claude outputs")]
    for f in fn:
        if not f.endswith(".md"):
            continue
        p = os.path.join(dp, f)
        r = rel(p)
        if r in ("guia.md", "metodo.md"):
            continue
        # fuentes/ y restringido/ son material, no documentos del método: no se editan,
        # así que no se les pide cabecera ni nombre. Sus inventario.md (enlaces.md hasta la 1.21) sí son nuestros.
        if ("/fuentes/" in "/" + r or "/restringido/" in "/" + r) and f not in ("inventario.md", "enlaces.md"):
            continue
        if not nombre_ok(f) or (nombre_con_orden_version_o_fecha(f) and not ROTADO.match(f)):
            h("nombre de archivo", r)
        fm, txt = cabecera(p)
        if fm is None:
            h("sin cabecera", r); continue
        m = re.search(r"^estado: *(\S+)", fm, re.M)
        estado = m.group(1).strip("'\"") if m else None   # con o sin comillas, como abrir.py y el tablero
        if not m:
            h("cabecera sin estado", r)
        elif estado not in ESTADOS:
            h("estado que no existe", r, m.group(1))
        elif estado == "reemplazado" and "reemplazado_por" not in fm:
            h("reemplazado sin reemplazado_por", r)
        a = re.search(r"^actualizado: *(\S+)", fm, re.M)
        if not a:
            h("cabecera sin actualizado", r)
        elif not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.group(1)):
            h("fecha mal formada", r, a.group(1))
        if "/entregables/" in r and "basado_en" not in fm:
            h("entregable sin basado_en", r)
        if ("/entregables/" in r or "/taller/" in r) and estado != "reemplazado" and not re.search(r"^(?:aportacion|afirma): *[^\s'\"]|^(?:aportacion|afirma): *['\"][^'\"\s]", fm, re.M):
            sin_afirma.append(r)
        if "/taller/" in r and estado != "reemplazado" and "basado_en" not in fm:
            sin_basado.append(r)
        if ("/entregables/" in r or "/taller/" in r) and re.search(r"^afirma:", fm, re.M):
            anterior.append(r + " (afirma)")
        # un [[ dentro de codigo, en linea o en bloque, no es un enlace: es hablar de ellos
        sin_codigo = re.sub(r"`[^`\n]*`", "", re.sub(r"```.*?```", "", txt, flags=re.S))
        if "[[" in sin_codigo:
            h("enlace wiki", r)
        # solo se marca una ruta absoluta que apunta a un archivo del método;
        # una ruta de máquina citada dentro de un runbook es contenido legítimo
        if re.search(r"/(Users|home|Volumes)/[^\s`)]*\.md\b", txt):
            h("ruta absoluta a un archivo del método", r)
        if f in ("inventario.md", "enlaces.md") and len([l for l in txt.splitlines() if l.startswith("|")]) <= 2:
            h(f + " sin filas", r)

def nota_afirma():
    if sin_charset:
        print("\nNota: %d archivo%s .html sin `<meta charset=\"utf-8\">`: abiertos desde la carpeta, los acentos salen rotos. Añade la etiqueta en su <head>: %s" % (len(sin_charset), "" if len(sin_charset) == 1 else "s", ", ".join(sorted(sin_charset)[:5]) + (" …" if len(sin_charset) > 5 else "")))
    if sin_afirma:
        print("\nNota: %d archivo%s de entregables/ y taller/ sin `aportacion:`. No bloquea en lo que ya existía; el barrido del tablero propone una línea y su responsable la acepta." % (len(sin_afirma), "" if len(sin_afirma) == 1 else "s"))
    if sin_basado:
        print("\nNota: %d archivo%s de taller/ sin `basado_en`. No bloquea en lo que ya existía; lo que se crea desde la 1.22 la lleva (`[]` si no se usó nada)." % (len(sin_basado), "" if len(sin_basado) == 1 else "s"))
    for _n in notas_personas:
        print("\nNota: " + _n + ".")
    if anterior:
        print("\nNota: %d archivo%s con la estructura de la 1.21 (En corto, Panorama, Dueño, afirma, enlaces.md…). No bloquea: la raíz funciona mezclada, y lo migra la apertura de su responsable, o la del responsable de contexto, con el plugin 1.22: %s" % (len(anterior), "" if len(anterior) == 1 else "s", ", ".join(anterior[:5]) + (" …" if len(anterior) > 5 else "")))

if not hallazgos:
    print("La raíz cumple el contrato.")
    nota_afirma()
    sys.exit(0)
print("%d hallazgos:\n" % len(hallazgos))
ancho = max(len(c) for c, _, _ in hallazgos)
for clase, ruta, detalle in sorted(hallazgos):
    print("  %-*s  %s%s" % (ancho, clase, ruta, ("  (" + detalle + ")") if detalle else ""))
nota_afirma()
sys.exit(1)
PY
