#!/usr/bin/env python3
"""Compara los permisos reales de la carpeta compartida con lo que declara la raíz (guia.md, los area.md, las líneas
«Colabora:» de los proyectos y las carpetas restringido/). No escribe nada y no toca Drive: Claude lee los permisos
con el conector de Google Drive y se los pasa en un JSON. Lo usa la sesión del responsable de contexto (skill sesion,
anexo permisos.md).

Uso:
  permisos.py <raiz> --plan              qué carpetas hay que mirar en Drive (áreas, proyectos, restringido/)
  permisos.py <raiz> --drive drive.json  qué no cuadra, en llano, con lo que hay que cambiar en Drive
  permisos.py <raiz> --drive drive.json --tablero   lo mismo en JSON, para meta/permisos del tablero

drive.json:
  {"raiz": {"permisos": [{"email": "...", "role": "organizer", "type": "user"}, ...]},
   "areas": {"<area>": {"permisos": [...], "limitada": false} | null},
   "proyectos": {"<area>/<proyecto>": {"permisos": [...], "limitada": false} | null},
   "restringidos": {"<area>/<proyecto>": {"permisos": [...], "limitada": true} | null}}
«limitada» es el inheritedPermissionsDisabled de la carpeta (acceso limitado); null, que no se encontró en Drive.
Los permisos de una carpeta incluyen los heredados de la unidad, como los da el conector. «type» es el del conector
(user, group, domain, anyone); sin él se toma por user. Un grupo se avisa y no se cuenta como persona; un dominio o
«cualquiera con el enlace» se avisa siempre.
"""
import json, pathlib, re, sys

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
# --- el administrador principal: una sola persona (1.22.2) ---
# La misma función en abrir.py y permisos.py (cada uno se descarga suelto); pruebas/sesion/probar_permisos.py comprueba
# que las dos copias son idénticas. Recibe el texto de «Quién responde por qué» y {nombre en minúscula: cuentas} de la
# tabla de áreas, y dice si quien administra la carpeta y quien responde por el contexto son la misma persona.
def administrador_unico(quien, por_nombre):
    """(veredicto, adm, ctx): «una», «dos» o «no se sabe» (un lado trae solo un nombre que no está en la tabla y el otro
    una cuenta: no se afirma nada). Dos correos de la misma persona («En Drive: a@claude es a@drive») cuentan como una."""
    ctx, adm, en_drive = "", "", ""
    for l in (quien or "").split("\n"):
        s = l.strip().lstrip("-* ").strip()
        if s.lower().startswith("contexto común"):
            ctx = s.split(":", 1)[-1].strip().rstrip(".").strip()
        elif s.lower().startswith("administra"):
            adm = s.split(":", 1)[-1].strip().rstrip(".").strip()
        elif re.match(r"^(en\s+)?(google\s+)?drive\s*:", s, re.I):
            en_drive = s.split(":", 1)[-1]
    misma = {}
    for par in re.split(r"[,;·]|\s+y\s+", en_drive.lower()):
        cs = CORREO.findall(par)
        if len(cs) == 2:
            misma[cs[1]] = cs[0]
    def personas(linea):
        """(cuentas, nombres) de una línea: las cuentas que trae o que la tabla da a sus nombres, y los nombres que la
        tabla reconoce; si no reconoce ninguno, el primer tramo antes de una coma o un punto («Ana Prueba, de forma
        provisional. Hoy vive…» es Ana Prueba), que es donde va el nombre."""
        cuentas, nombres = {misma.get(c, c) for c in CORREO.findall(linea.lower())}, []
        tramos = [n.strip().rstrip(".").strip() for n in re.split(r",|\by\b|\be\b|·|;", re.sub(r"\([^)]*\)", "", linea))]
        for n in tramos:
            if n.lower() in por_nombre:
                nombres.append(n.lower()); cuentas |= {misma.get(c, c) for c in por_nombre[n.lower()]}
        if not nombres:
            n = re.split(r"\.\s", tramos[0] if tramos else "")[0].strip().lower()
            if n and not CORREO.fullmatch(n) and len(n.split()) >= 2:
                nombres.append(n)
        return cuentas, nombres
    ca, na = personas(adm); cc, nc = personas(ctx)
    if not adm or not ctx:
        return "no se sabe", adm, ctx
    if len(ca) > 1 or len(na) > 1:
        return "dos", adm, ctx
    if ca and cc:
        return ("una" if ca & cc else "dos"), adm, ctx
    if na and nc:
        return ("una" if na == nc else "dos"), adm, ctx
    return "no se sabe", adm, ctx
# --- fin del administrador principal ---

ROL = {"organizer": "Administrador", "fileOrganizer": "Gestor de contenido", "writer": "Colaborador",
       "commenter": "Comentarista", "reader": "Lector", "owner": "Propietario"}
ROL_MI = {"owner": "Propietario", "writer": "Editor", "commenter": "Comentarista", "reader": "Lector"}
ESCRIBE = {"organizer", "fileOrganizer", "writer", "owner"}


def leer(p):
    try:
        return p.read_text(encoding="utf-8-sig")
    except OSError:
        return None


def seccion(texto, nombre):
    m = re.search(r"^##\s+" + re.escape(nombre) + r"\s*$(.*?)(?=^##\s|\Z)", texto or "", re.M | re.S)
    return m.group(1) if m else ""


def restringida_celda(celda):
    c = celda or ""
    if re.match(r"^[\W_]*restringid[oa]s?\b", c, re.I):
        return True
    return bool(re.search(r"\brestringidas?\b", c, re.I)) and not re.search(r"\b(?:nada|no|nunca|sin|antes)\s+(?:[^\s]+\s+)?restringid", c, re.I)


def columnas_areas(cab):
    """Dónde está cada columna de la tabla de áreas, por su encabezado (como abrir.py): «Responsable» o «Dueño»,
    «Cuenta», «Quién la lee» y, desde la 1.22, «Acceso»."""
    n = [re.sub(r"[*_`]", "", x).strip().lower() for x in cab]
    def pos(*nombres, defecto=None):
        return next((i for i, x in enumerate(n) if x in nombres), defecto)
    return {"responsable": pos("responsable", "dueño", "dueno", defecto=2), "cuenta": pos("cuenta", "colabora", defecto=3),
            "lectores": pos("quién la lee", "quien la lee", defecto=4), "acceso": pos("acceso")}


def solo_nombre(d):
    return re.sub(r"\s*\((?=[a-záéíóúñ`])[^)]*\)", "", d or "").strip()


def raiz_declarada(raiz):
    guia = leer(raiz / "guia.md") or ""
    areas, filas, col = [], seccion(guia, "Áreas").split("\n"), None
    reg = registro_personas(guia)
    for l in filas:
        if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
            continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if col is None:
            col = columnas_areas(c); cab = c; continue
        if len(c) > max(v for v in col.values() if v is not None):
            de, co, aviso = fila_cuentas(cab, c, reg)
            lect = c[col["lectores"]]
            if col["acceso"] is not None and re.match(r"^[\W_]*(restringid|abiert)[oa]s?\b", c[col["acceso"]], re.I):
                # 1.22: «Acceso» dice si está restringida y «Quién la lee», a quiénes; con otra cosa o vacía, la regla de la 1.21
                restr = bool(re.match(r"^[\W_]*restringid[oa]s?\b", c[col["acceso"]], re.I))
                lect = ("Restringida: " + lect) if restr and not re.match(r"^[\W_]*restringid", lect, re.I) else lect
            else:
                restr = restringida_celda(lect)
            areas.append({"slug": c[0].strip("`").rstrip("/"), "nombre": c[0].strip("`").rstrip("/"), "dueno": solo_nombre(c[col["responsable"]]),
                          "duenos": de, "colaboran": co, "restringida": restr, "lectores": lect, "acceso": col["acceso"] is not None,
                          "aviso": aviso, "en_celda": set(CORREO.findall((c[col["cuenta"]] or "").lower())) | de | co})
    quien = quien_responde_txt = seccion(guia, "Quién responde por qué")
    ctx, adm, en_drive = "", "", ""
    for l in quien.split("\n"):
        s = l.strip().lstrip("-* ").strip()
        if s.lower().startswith("contexto común"):
            ctx = s.split(":", 1)[-1]
        elif s.lower().startswith("administra"):
            adm = s.split(":", 1)[-1]
        elif re.match(r"^(en\s+)?(google\s+)?drive\s*:", s, re.I):
            en_drive = s.split(":", 1)[-1]
    # «En Drive: jjalfaro@me.com es juanjo@tuopinas.mx, ana@x es ana@y»: la cuenta de Claude de la tabla y la cuenta con
    # la que esa persona entra a Drive, cuando no son la misma. Lo declarado se compara en Drive con la segunda. Lo que
    # no se deja leer se avisa, porque callar da justo los falsos avisos que la línea quiere evitar.
    drive_de, avisos_drive = {}, []
    for par in re.split(r"[,;·]|\s+y\s+", en_drive.lower()):
        if not par.strip():
            continue
        cs = CORREO.findall(par)
        if len(cs) != 2:
            avisos_drive.append(f"el tramo «{par.strip()[:60]}» de «En Drive:» no da dos correos (va «cuenta@claude es cuenta@drive»)")
            continue
        drive_de[cs[0]] = cs[1]
    # desde la 1.25, «en Drive: otra@» va en la línea de cada persona de «Quién es quién»
    for p_ in reg["personas"]:
        for dc in sorted(p_["drive"])[:1]:
            for c_ in p_["cuentas"]:
                drive_de[c_] = dc
    # cuenta de cada nombre, por la tabla de áreas (el responsable) y por los correos que la línea lleve entre paréntesis;
    # el nombre, sin lo que siga a una coma («Juanjo Jiménez-Alfaro, de forma provisional»)
    por_nombre = {}
    for a in areas:
        if a["dueno"] and len(a["duenos"]) == 1:
            n = a["dueno"].split(",")[0].strip().lower()
            por_nombre.setdefault(n, set()).update(a["duenos"])
    # y por «Quién es quién» (1.25): el nombre y sus alias dan las cuentas; quien no usa Claude pero entra a Drive, la de Drive
    for p_ in reg["personas"]:
        if p_["baja"] or p_["nombre"] == "?":
            continue
        cs_ = set(p_["cuentas"]) or set(p_["drive"])
        for n in [p_["nombre"]] + p_["alias"]:
            if cs_:
                por_nombre[clave_nombre(n)] = cs_
    en_tabla = set(c for a in areas for c in a["en_celda"]) | set(CORREO.findall((ctx + " " + adm).lower())) | set(reg["cuenta"])
    for c, d in drive_de.items():
        if c not in en_tabla and d in en_tabla:
            avisos_drive.append(f"en «En Drive:», {c} es {d} está al revés: primero va la cuenta de la tabla ({d}) y después la de Drive")
        elif c not in en_tabla:
            avisos_drive.append(f"en «En Drive:», {c} no está en ninguna celda Cuenta ni en «Quién responde por qué»: comprueba el correo")
    def cuentas_de(linea):
        out = set(CORREO.findall(linea.lower()))
        nombres = re.sub(r"\([^)]*\)", "", linea)
        for n in re.split(r",|\by\b|\be\b|·", nombres):
            n = n.strip().rstrip(".").strip()
            out |= por_nombre.get(n.lower(), set()) | por_nombre.get(clave_nombre(n), set())
        return out
    admins, ctxc = cuentas_de(adm), cuentas_de(ctx)
    def nombres_de(texto):
        """(cuentas, nombres sin cuenta) de una lista de personas: «Ana Prueba y Beto Prueba», «dirección», «a@x, b@x»."""
        out, sin = set(CORREO.findall((texto or "").lower())), []
        for n in re.split(r",|\by\b|\be\b|·|;", re.sub(r"\([^)]*\)", "", texto or "")):
            n = n.strip().rstrip(".").strip()
            if not n or CORREO.fullmatch(n.lower()):
                continue
            if n.lower() in por_nombre or clave_nombre(n) in por_nombre:
                out |= por_nombre.get(n.lower()) or por_nombre[clave_nombre(n)]
            else:
                sin.append(n)
        return out, sin
    for a in areas:
        # quién lee un área restringida: lo que sigue a «Restringida:» en «Quién la lee», resuelto por la tabla
        m = re.search(r"restringid[oa]s?\s*:\s*(.*)$", a["lectores"], re.I | re.S)
        a["leen"], a["leen_sin_cuenta"] = nombres_de(m.group(1)) if m else (set(), [])
    proyectos, no_mirados = [], []
    for a in areas:
        dir_a = raiz / a["slug"]
        if not dir_a.is_dir():
            if a["restringida"]:
                no_mirados.append((f"los proyectos de {a['slug']}/ (área restringida sin carpeta aquí)", True))
            continue
        lineas = {}
        for l in seccion(re.sub(r"^---.*?^---\s*$", "", leer(dir_a / "area.md") or "", count=1, flags=re.S | re.M), "Proyectos").split("\n"):
            m = re.match(r"^- `([^`/]+)/?`\s*[—–:-]?\s*(.*)$", l)
            if m:
                lineas[m.group(1)] = m.group(2)
        try:
            hijos = sorted(d for d in dir_a.iterdir() if d.is_dir() and not d.name.startswith("."))
        except OSError:
            hijos = []
        vistos = set()
        for d in hijos:
            pm = leer(d / "proyecto.md")
            if pm is None and d.name not in lineas:
                continue
            vistos.add(d.name)
            quien = seccion(pm or "", "Quién participa")
            col = colaboran_en(quien, reg if reg["hay"] else None)
            # quién lee un proyecto restringido y su restringido/ (1.25): «Lo lee: Nombre, Nombre» en «Quién participa»
            ml = re.search(r"^\s*[-*]?\s*\**\s*lo\s+leen?\s*\**\s*:\s*(.+)$", quien, re.I | re.M)
            leen_p, leen_p_sin = nombres_de(ml.group(1)) if ml else (set(), [])
            # el alta provisional (1.25): «Colabora: Nombre (correo)» de alguien que aún no está en «Quién es quién»
            prov = [(n_.strip(), c_.lower()) for l_ in quien.split("\n") if LINEA_COLABORA.match(l_)
                    for n_, c_ in re.findall(r"([^,;(]+?)\s*\(\s*(" + CORREO.pattern + r")\s*\)", re.sub(r"^[^:]*:", "", l_))
                    if reg["hay"] and c_.lower() not in reg["cuenta"]]
            md = re.search(r"^\s*[-*]?\s*\**\s*(?:due[ñn][oa]|responsable)\s*\**\s*:\s*(.+)$", quien, re.I | re.M)
            if not md:
                md = re.match(r"^[\W_]*restringid[oa]\s*:\s*(?:due[ñn][oa]|responsable)\s+([^.;,]+)", lineas.get(d.name, ""), re.I)
            dueno, dueno_sin = nombres_de(md.group(1)) if md else (set(), [])
            if pm is None and d.name in lineas:
                no_mirados.append((f"{a['slug']}/{d.name}/ (sin proyecto.md legible aquí)", True))
            proyectos.append({"id": f"{a['slug']}/{d.name}", "area": a["slug"], "colaboran": col, "dueno": dueno, "dueno_sin": dueno_sin + leen_p_sin, "leen": leen_p, "provisionales": prov,
                              "restringido": bool(re.match(r"^[\W_]*restringid[oa]\b", lineas.get(d.name, ""), re.I)),
                              "tiene_restringido": (d / "restringido").is_dir()})
        for slug, linea in lineas.items():
            if slug in vistos:
                continue
            if re.match(r"^[\W_]*restringid[oa]\b", linea, re.I):
                # restringido para esta cuenta: su acceso limitado se mira en Drive igual; quién colabora, no
                md = re.match(r"^[\W_]*restringid[oa]\s*:\s*(?:due[ñn][oa]|responsable)\s+([^.;,]+)", linea, re.I)
                dueno, dueno_sin = nombres_de(md.group(1)) if md else (set(), [])
                proyectos.append({"id": f"{a['slug']}/{slug}", "area": a["slug"], "colaboran": set(), "dueno": dueno, "dueno_sin": dueno_sin, "leen": set(),
                                  "restringido": True, "tiene_restringido": False})
                no_mirados.append((f"{a['slug']}/{slug}/ (restringido, sin carpeta aquí)", False))
            else:
                no_mirados.append((f"{a['slug']}/{slug}/ (en el índice del área, sin carpeta aquí)", True))
    sin_confirmar = {c for p_ in reg["personas"] if p_["sin_confirmar"] for c in p_["cuentas"] | p_["drive"]}
    return areas, proyectos, admins, ctxc, adm.strip(), ctx.strip(), no_mirados, (drive_de, avisos_drive, quien_responde_txt, por_nombre, sin_confirmar)


def plan(raiz):
    areas, proyectos, admins, ctxc, adm, ctx, no_mirados, _ = raiz_declarada(raiz)
    print("Carpetas que hay que mirar en Drive (permisos y si tienen acceso limitado):")
    print("- la raíz (la unidad compartida, o la carpeta raíz en «Mi unidad»)")
    for a in areas:
        print(f"- área {a['slug']}/" + (" (declarada restringida)" if a["restringida"] else ""))
    for p in proyectos:
        if p["colaboran"] or p["restringido"]:
            print(f"- proyecto {p['id']}/" + (" (con «Colabora:»)" if p["colaboran"] else "") + (" (declarado restringido)" if p["restringido"] else ""))
        if p["tiene_restringido"]:
            print(f"- restringido {p['id']}/restringido/")
    if not admins:
        print(f"(aviso: no se sabe la cuenta de quien administra la carpeta: «{adm or 'no consta'}» en guia.md)")
    for n, _ in no_mirados:
        print(f"(no se pudo mirar: {n}; sin consola, tráelo con espejo.py permisos)")
    for p in proyectos:
        for n, c in p.get("provisionales") or []:
            print(f"ALTA {n} · {c} (colabora en {p['id']} y no está en «Quién es quién»: el responsable de contexto añade su línea a guia.md y deja en el proyecto solo el nombre)")


def comparar(raiz, drive):
    areas, proyectos, admins, ctxc, adm, ctx, no_mirados, (drive_de, avisos_drive, quien_responde, por_nombre, sin_confirmar) = raiz_declarada(raiz)
    # lo declarado, con la cuenta con la que cada quien entra a Drive («En Drive:» de guia.md)
    d = lambda c: drive_de.get(c, c)
    claude_de = {v: k for k, v in drive_de.items()}
    for a in areas:
        a["duenos"] = set(map(d, a["duenos"])); a["colaboran"] = set(map(d, a["colaboran"])); a["leen"] = set(map(d, a["leen"])); a["en_celda"] = set(map(d, a["en_celda"]))
    for p in proyectos:
        p["colaboran"] = set(map(d, p["colaboran"])); p["dueno"] = set(map(d, p["dueno"])); p["leen"] = set(map(d, p["leen"]))
    admins, ctxc = set(map(d, admins)), set(map(d, ctxc))
    raizp = (drive.get("raiz") or {}).get("permisos") or []
    mi_unidad = not any(x.get("role") in ("organizer", "fileOrganizer") for x in raizp) and any(x.get("role") == "owner" for x in raizp)
    NOM = ROL_MI if mi_unidad else ROL
    ESCRIBE_BIEN = {"writer", "owner"} if mi_unidad else {"organizer", "fileOrganizer"}
    BIEN = "el rol de Drive «Editor»" if mi_unidad else "el rol de Drive «Gestor de contenido»"
    def roles(perms):
        """Personas (correo → rol); los grupos aparte, y los permisos sin persona (dominio, cualquiera con el enlace)."""
        r, grupos, abiertos = {}, {}, []
        for x in perms or []:
            e = (x.get("email") or x.get("emailAddress") or "").lower()
            t = (x.get("type") or ("user" if e else "")).lower()
            if t == "group" and e:
                grupos[e] = x.get("role", "")
            elif t in ("domain", "anyone") or not e:
                abiertos.append(("todo el dominio" + (f" {x['domain']}" if x.get("domain") else "") if t == "domain" else
                                 "cualquiera con el enlace" if t == "anyone" else "una entrada sin correo", x.get("role", "")))
            else:
                r[e] = x.get("role", "")
        return r, grupos, abiertos
    def admin(e, rol):
        return e in admins or (not admins and rol in ("organizer", "owner"))
    hall, notas, acciones, a_decidir = [], [], [], 0
    rr, rg, ra = roles(raizp)
    # si Drive conoce también a la persona por su cuenta de Claude, es la misma persona: se mira como la de Drive
    def alias(r):
        for c in list(r):
            dc = drive_de.get(c)
            if not dc or dc == c:
                continue
            if dc not in r:
                r[dc] = r.pop(c)
            else:   # las dos cuentas en Drive: la persona es una, con el rol más alto de los dos
                orden = ["reader", "commenter", "writer", "fileOrganizer", "organizer", "owner"]
                r[dc] = max(r.pop(c), r[dc], key=lambda x: orden.index(x) if x in orden else -1)
        return r
    alias(rr)
    for n_ in avisos_drive:
        notas.append(n_)
    if not raizp:
        hall.append("No llegaron los permisos de la raíz: sin ellos no se puede revisar nada. Vuelve a leerlos con el conector de Google Drive.")
    if not admins and rr:
        org = sorted(e for e, rol in rr.items() if rol in ("organizer", "owner"))
        notas.append(f"No se sabe la cuenta de quien administra la carpeta («{adm or 'no consta'}» en guia.md), así que se tomó por administrador a quien tiene el rol de Drive «{NOM.get('owner' if mi_unidad else 'organizer')}» en la raíz: {', '.join(org) or 'nadie'}. Pon su correo en guia.md.")
    for a in areas:
        if a["aviso"]:
            notas.append(f"La fila del área {a['slug']}/ en guia.md no se deja leer ({a['aviso']}): hasta que se corrija no se puede decir quién debe escribir ahí.")
    def abiertos_en(donde, abiertos, grupos, hall, notas):
        """Lo que no es una persona: un dominio o el enlace, siempre; un grupo, para comprobar a sus miembros."""
        for que, rol in abiertos:
            if rol in ESCRIBE:
                hall.append(f"{donde} está abierta a {que} con el rol de Drive «{NOM.get(rol, rol)}»: puede escribir cualquiera. Quítalo desde la web y comparte solo con las personas de guia.md.")
            else:
                notas.append(f"{donde} la lee {que} (rol de Drive «{NOM.get(rol, rol)}»). Si no es a propósito, quítalo desde la web.")
        for g, rol in sorted(grupos.items()):
            if rol in ESCRIBE and not admin(g, rol):
                hall.append(f"El grupo {g} tiene el rol de Drive «{NOM.get(rol, rol)}» en {donde.lower()}: puede escribir todo su miembro. Bájale el rol de Drive a «Lector» y da la escritura por persona, como dice guia.md.")
            else:
                notas.append(f"{donde} la lee el grupo {g} (rol de Drive «{NOM.get(rol, rol)}»): esta revisión no ve a sus miembros; comprueba en Google quién está en él.")
    abiertos_en("La carpeta entera", ra, rg, hall, notas)
    por_grupo = bool(rg or ra)
    def sin_acceso(donde):
        return " (no figura con su correo en " + donde + (": puede entrar por un grupo o por el dominio, compruébalo)" if por_grupo else ")")
    # 1. la raíz: quien no administra, solo lectura; quien administra, como dice guia.md
    escriben_en_raiz = set()
    for e, rol in sorted(rr.items()):
        if rol in ESCRIBE and not admin(e, rol):
            escriben_en_raiz.add(e)
            suyas = [a["slug"] for a in areas if e in a["duenos"] | a["colaboran"]]
            if suyas:
                hall.append(f"{e} tiene el rol de Drive «{NOM.get(rol, rol)}» en toda la carpeta, así que puede escribir en todas las áreas. Cámbiale el rol de Drive a «Lector» en la raíz y dale {BIEN} solo en la carpeta de {', '.join(suyas)}.")
            elif any(e in a["en_celda"] and a["aviso"] for a in areas):
                notas.append(f"{e} tiene el rol de Drive «{NOM.get(rol, rol)}» en toda la carpeta y aparece en una celda Cuenta que no se deja leer: corrige la celda antes de tocar su rol.")
            else:
                a_decidir += 1
                hall.append(f"{e} tiene el rol de Drive «{NOM.get(rol, rol)}» en toda la carpeta, así que puede escribir en todas las áreas, y guia.md no lo declara responsable ni colaborador de ninguna. ¿Debe escribir? Si sí, que el responsable de contexto lo declare en guia.md y dale {BIEN} solo en esa carpeta; si no, cámbiale el rol de Drive a «Lector» en la raíz.")
    # el administrador principal (1.22.2): quien administra la carpeta, responde por el contexto y es su dueño en Drive es
    # una sola persona, y lee todo, también lo restringido
    _ver, _, _ = administrador_unico(quien_responde, por_nombre)
    if _ver == "dos":
        hall.append(f"Quien administra la carpeta («{adm.strip() or 'no consta'}») y quien responde por el contexto («{ctx.strip() or 'no consta'}») son personas distintas en guia.md: "
                    "son una sola persona, que además es la dueña de la carpeta en Drive y lee todo. Corrige «Quién responde por qué».")
    if len(admins) > 1:
        admins = set()     # con dos administradores declarados no se dice a quién darle qué: antes se corrige guia.md
    for e in sorted(admins):
        if rr and e not in rr:
            hall.append(f"{e} figura en guia.md como quien administra la carpeta, pero no tiene acceso a ella.")
        elif rr.get(e) and not mi_unidad and rr[e] != "organizer":
            hall.append(f"{e} figura en guia.md como quien administra la carpeta, pero en la unidad es el rol de Drive «{NOM.get(rr[e], rr[e])}»: dale el rol de Drive «Administrador».")
        elif rr.get(e) and mi_unidad and rr[e] != "owner":
            hall.append(f"{e} figura en guia.md como quien administra la carpeta, pero en Drive no es su propietario (rol de Drive «{NOM.get(rr[e], rr[e])}»): la carpeta tiene que ser suya; transfiere la propiedad desde la web.")
    declaradas = set()
    for a in areas:
        declaradas |= a["duenos"] | a["colaboran"]
    for p in proyectos:
        declaradas |= p["colaboran"]
    for e in sorted(declaradas | ctxc):
        if rr and e not in rr and not any(e in (a["duenos"] | a["colaboran"]) and a["restringida"] for a in areas):
            if por_grupo:
                notas.append(f"{e} aparece en guia.md o en un proyecto y no figura con su correo en la carpeta: puede entrar por un grupo o por el dominio; si no, compártesela con el rol de Drive «Lector».")
            elif avisos_drive or e in claude_de:
                notas.append(f"{e} aparece en guia.md o en un proyecto y no figura en la carpeta; la línea «En Drive:» no se deja leer entera: corrígela antes de compartir nada.")
            elif e in sin_confirmar:
                notas.append(f"{e} aparece en guia.md o en un proyecto y no tiene acceso a la carpeta, pero su línea de «Quién es quién» dice «sin confirmar»: comprueba con esa persona que la cuenta es suya antes de compartirle la carpeta.")
            else:
                hall.append(f"{e} aparece en guia.md o en un proyecto, pero no tiene acceso a la carpeta: compártesela con el rol de Drive «Lector» (si entra a Drive con otra cuenta, decláralo en «En Drive:» de guia.md).")
                acciones.append({"tipo": "compartir", "cuenta": e, "carpeta": "", "rol": "reader"})
    def limitar(carpeta, conservan, sin_resolver, ar):
        """La acción de limitar con el conector, solo si se sabe a quién conservar; si no, queda para la web."""
        conservan = sorted(c for c in conservan if not admin(c, ar.get(c, "")))
        escriben = [c for c in conservan if ar.get(c) in ESCRIBE]
        if sin_resolver or not conservan:
            return None
        return {"tipo": "limitar", "carpeta": carpeta, "conservan": conservan, "escriben": escriben}
    def web(sin_resolver):
        return (" Hazlo desde la web, que enseña quién conserva el acceso: aquí no se sabe la cuenta de " + ", ".join(sin_resolver) + "."
                if sin_resolver else " Márcala con acceso limitado.")
    # 2. cada área: escriben su responsable y quienes colaboran, nadie más
    for a in areas:
        info = (drive.get("areas") or {}).get(a["slug"])
        if info is None:
            if not a["restringida"] and (raiz / a["slug"]).is_dir():
                notas.append(f"El área {a['slug']}/ no se encontró en Drive con esta cuenta: puede faltar la carpeta o no tener acceso.")
            continue
        ar, ag, aa = roles(info.get("permisos"))
        alias(ar)
        abiertos_en(f"El área {a['slug']}/", aa, ag, hall, notas)
        for e in sorted(a["duenos"] | a["colaboran"]):
            rol = ar.get(e)
            papel = "responsable" if e in a["duenos"] else "colabora"
            if rol in ESCRIBE_BIEN:
                continue
            if rol == "writer" and not mi_unidad:
                hall.append(f"{e} ({papel} en {a['slug']}) tiene el rol de Drive «Colaborador» en su área, que no deja mover ni borrar archivos: cámbialo a «Gestor de contenido» en la carpeta {a['slug']}.")
            else:
                hall.append(f"{e} ({papel} en {a['slug']}) no puede escribir en su área" + (f" (tiene el rol de Drive «{NOM.get(rol, rol)}»)" if rol else sin_acceso("la carpeta")) + f": dale {BIEN} en la carpeta {a['slug']}.")
        for e, rol in sorted(ar.items()):
            if rol in ESCRIBE and e not in a["duenos"] | a["colaboran"] and not admin(e, rol) and e not in escriben_en_raiz:
                if a["aviso"] and e in a["en_celda"]:
                    notas.append(f"{e} escribe en {a['slug']} (rol de Drive «{NOM.get(rol, rol)}») y aparece en su celda Cuenta, que no se deja leer: corrige la celda antes de tocar su rol.")
                elif a["aviso"] and not a["en_celda"]:
                    notas.append(f"{e} escribe en {a['slug']} (rol de Drive «{NOM.get(rol, rol)}») y el área no declara ninguna cuenta ({a['aviso']}): si es su responsable{(' ' + a['dueno']) if a['dueno'] else ''} o colabora, nada que cambiar; ponlo en la celda Cuenta de guia.md.")
                else:
                    a_decidir += 1
                    hall.append(f"{e} puede escribir en {a['slug']} (rol de Drive «{NOM.get(rol, rol)}») y guia.md no lo declara responsable ni colaborador de esa área. ¿Debe escribir? Si sí, que el responsable de contexto lo declare en guia.md" + ("" if rol in ESCRIBE_BIEN else f" y súbele el rol a {BIEN.replace('el rol de Drive ', '')} en esa carpeta, porque «{NOM.get(rol, rol)}» no deja mover ni borrar archivos") + "; si no, cámbiale el rol de Drive a «Lector» ahí.")
        lim = bool(info.get("limitada"))
        if a["restringida"] and not lim:
            conservan = a["duenos"] | a["colaboran"] | a["leen"] | set(c for p in proyectos if p["area"] == a["slug"] for c in p["colaboran"] | p["dueno"])
            acc = limitar(a["slug"], conservan, a["leen_sin_cuenta"], ar)
            hall.append(f"El área {a['slug']}/ está declarada restringida en guia.md, pero en Drive no tiene acceso limitado: la lee todo el equipo." + web(a["leen_sin_cuenta"] if not acc else []))
            if acc:
                acciones.append(acc)
        elif lim and not a["restringida"]:
            hall.append(f"El área {a['slug']}/ tiene acceso limitado en Drive, pero guia.md no la declara restringida: " + ("pon «Restringida» en su columna «Acceso»" if a.get("acceso") else "escribe «Restringida: …» en su columna «Quién la lee»") + ", o quita el acceso limitado.")
        elif lim:
            for e in sorted(admins):
                if ar and e not in ar and rr.get(e) not in ("organizer", "owner"):   # el administrador de la unidad o el propietario hereda el acceso
                    if ag:
                        notas.append(f"{e} administra la carpeta y no aparece entre quienes leen el área restringida {a['slug']}/; puede entrar por un grupo ({', '.join(sorted(ag))}). Compruébalo: quien administra lo lee todo.")
                    else:
                        hall.append(f"{e} administra la carpeta y no lee el área restringida {a['slug']}/: quien administra lo lee todo. Dale acceso desde la web.")
            fuera = sorted(e for e in ar if e not in a["duenos"] | a["colaboran"] | a["leen"] and not admin(e, ar[e]))
            if fuera:
                notas.append(f"El área restringida {a['slug']}/ la leen además {', '.join(fuera)}; guia.md dice «{a['lectores']}». Compruébalo.")
    # 3. proyectos: quien colabora en uno escribe en su carpeta; los declarados restringidos, con acceso limitado
    for p in proyectos:
        info = (drive.get("proyectos") or {}).get(p["id"])
        if (p["colaboran"] or p["restringido"]) and info is None and p["id"] in (drive.get("proyectos") or {}):
            notas.append(f"El proyecto {p['id']}/ no se encontró en Drive con esta cuenta.")
        ar_ = next((a for a in areas if a["slug"] == p["area"]), {"duenos": set(), "colaboran": set()})
        conservan = ar_["duenos"] | ar_["colaboran"] | p["colaboran"] | p["dueno"] | p["leen"]
        if info:
            pr, pg, pa = roles(info.get("permisos"))
            alias(pr)
            abiertos_en(f"El proyecto {p['id']}/", pa, pg, hall, notas)
            for e in sorted(p["colaboran"]):
                rol = pr.get(e)
                if rol not in ESCRIBE_BIEN:
                    hall.append(f"{e} colabora en {p['id']} pero no puede escribir en su carpeta" + (f" (tiene el rol de Drive «{NOM.get(rol, rol)}»)" if rol else sin_acceso("ella")) + f": dale {BIEN} en la carpeta {p['id']}.")
            if p["restringido"] and not info.get("limitada"):
                acc = limitar(p["id"], conservan, p["dueno_sin"], pr)
                hall.append(f"El proyecto {p['id']}/ está declarado restringido en su area.md, pero en Drive no tiene acceso limitado." + web(p["dueno_sin"] if not acc else []))
                if acc:
                    acciones.append(acc)
        if p["tiene_restringido"] or p["id"] in (drive.get("restringidos") or {}):
            ri = (drive.get("restringidos") or {}).get(p["id"])
            if ri is not None and not ri.get("limitada"):
                rr_, _, _ = roles(ri.get("permisos")); alias(rr_)
                acc = limitar(p["id"] + "/restringido", conservan, p["dueno_sin"], rr_)
                hall.append(f"La carpeta restringido/ de {p['id']} no tiene acceso limitado en Drive: la lee todo el equipo." + web(p["dueno_sin"] if not acc else []))
                if acc:
                    acciones.append(acc)
    for n, importa in no_mirados:
        if importa:
            notas.append(f"No se pudo mirar {n}: sus «Colabora:» y si está restringido quedan sin revisar.")
    if JSON_TABLERO:
        # lo que el tablero de quien responde por el contexto guarda en meta/permisos (skill tablero)
        print(json.dumps({"tipo_unidad": "mi-unidad" if mi_unidad else "unidad", "cambios": hall, "comprobar": notas,
                          "acciones": {"con_conector": acciones, "a_mano": len(hall) - len(acciones) - a_decidir, "a_decidir": a_decidir}}, ensure_ascii=False))
        return
    print("=== PERMISOS")
    print(f"Tipo: {'«Mi unidad» (roles Lector y Editor)' if mi_unidad else 'unidad compartida'}")
    if not hall:
        print("Todo cuadra: los permisos de Drive son los que declara la carpeta." + (" Queda algo por comprobar:" if notas else ""))
    if hall:
        print(f"Para cambiar en Drive ({len(hall)}):")
        for h in hall:
            print(f"- {h}")
    if notas:
        print("Para comprobar:")
        for n in notas:
            print(f"- {n}")
    # lo que el conector de Google Drive deja hacer, con el sí de quien administra (anexo permisos.md); el resto, a mano
    print("=== ACCIONES")
    print(json.dumps({"tipo_unidad": "mi-unidad" if mi_unidad else "unidad", "con_conector": acciones,
                      "a_mano": len(hall) - len(acciones) - a_decidir, "a_decidir": a_decidir}, ensure_ascii=False))


JSON_TABLERO = "--tablero" in sys.argv
if JSON_TABLERO:
    sys.argv.remove("--tablero")

if __name__ == "__main__":
    if len(sys.argv) < 3 or not (pathlib.Path(sys.argv[1]) / "guia.md").is_file():
        sys.exit("Uso: permisos.py <raiz> --plan | --drive drive.json  (la raíz es la carpeta con guia.md y metodo.md)")
    R = pathlib.Path(sys.argv[1])
    if sys.argv[2] == "--plan":
        plan(R)
    elif sys.argv[2] == "--drive" and len(sys.argv) > 3:
        comparar(R, json.loads(pathlib.Path(sys.argv[3]).read_text(encoding="utf-8")))
    else:
        sys.exit("Uso: permisos.py <raiz> --plan | --drive drive.json")
