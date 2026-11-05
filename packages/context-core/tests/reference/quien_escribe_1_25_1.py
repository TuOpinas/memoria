"""Frozen reference: the «quién escribe» block as the plugin scripts carried it in 1.25.1, before they took it from
context_core. Kept only so the tests can check that context_core.compat returns exactly what it did. Never imported by
the plugin or the server; do not edit."""
import re
# --- quién escribe: «Quién es quién» y la tabla de áreas de guia.md, y la línea «Colabora:» de un proyecto ---
# La misma función en abrir.py, cerrar.py, permisos.py, migrar_estructura.py, aplicar_cambios.py, barrido.py,
# generar_vista.py y verificar.sh (cada uno se descarga suelto); pruebas/sesion/probar_cuentas.py comprueba que las
# ocho copias son idénticas. Desde la 1.25 cada persona está una vez en «Quién es quién» («Nombre · cuenta@») y la tabla
# de áreas la nombra por su nombre en Responsable y Colabora; hasta la 1.24, la celda Cuenta llevaba los correos. Se
# leen las dos formas: con registro y columna Colabora, por nombre; sin ellos, la celda Cuenta como siempre. Todo falla
# cerrado: un nombre o una cuenta que no se resuelve sin duda no da escritura a nadie.
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
    """Cómo se comparan dos nombres: NFC (Mac y Windows escriben las tildes distinto), sin mayúsculas, sin negritas,
    comillas ni lo que va entre paréntesis, y con los espacios juntos. Nada más: sin tilde no es el mismo nombre."""
    n = unicodedata.normalize("NFC", n or "").replace(" ", " ")
    n = re.sub(r"\s*\([^)]*\)", "", re.sub(r"[*_`«»\"]", "", n))
    return re.sub(r"\s+", " ", n).strip(" .,;:").lower()
def _titulo(t):
    """Un encabezado para compararlo: sin tildes (en NFC o NFD), sin mayúsculas ni signos."""
    t = "".join(c for c in unicodedata.normalize("NFD", t or "") if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", "", t.lower())).strip()
def registro_personas(guia):
    """«Quién es quién» de guia.md: {"hay", "personas", "nombre": {clave: persona}, "cuenta": {correo: persona}, "avisos"}.
    Una línea es «- Nombre · campo · campo» (el «·» con espacios a los lados); los campos: un correo (su cuenta de Claude),
    «cuentas: a@, b@», «en Drive: x@», «sin cuenta», «sin confirmar», «también: Otra Grafía», «de: Organización»,
    «baja AAAA-MM-DD», «compartida con: Nombre» y «registra: Nombre». «?» como nombre es una cuenta que todavía no tiene
    nombre. Quien está de baja no escribe; un nombre o una cuenta que está en dos líneas no es de nadie."""
    lineas, dentro, hay = [], False, False
    for l in unicodedata.normalize("NFC", guia or "").split("\n"):
        m = re.match(r"^\s*#{2,3}\s+(.*?)\s*$", l)
        if m:
            dentro = _titulo(m.group(1)) == "quien es quien"
            hay = hay or dentro
        elif dentro:
            lineas.append(l)
    reg = {"hay": hay, "personas": [], "nombre": {}, "cuenta": {}, "avisos": []}
    dos_nombres, dos_cuentas = set(), set()
    for l in lineas:
        if not re.match(r"^\s*[-*]\s+\S", l):
            continue
        campos = [c.strip() for c in re.split(r"\s+·\s+", l.strip()[1:].strip()) if c.strip()]
        if not campos:
            continue
        p = {"nombre": re.sub(r"\s*\([^)]*\)", "", re.sub(r"[*_`]", "", campos[0])).strip(), "cuentas": set(), "drive": set(),
             "sin_cuenta": False, "sin_confirmar": False, "alias": [], "de": "", "baja": "", "compartida": "", "registra": ""}
        if CORREO.fullmatch(p["nombre"].lower()):
            p["cuentas"].add(p["nombre"].lower()); p["nombre"] = "?"
        elif CORREO.search(p["nombre"]):
            reg["avisos"].append(f"«{campos[0]}»: el nombre y la cuenta van separados por « · »")
        for c in campos[1:]:
            cl = c.lower()
            if CORREO.fullmatch(cl):
                p["cuentas"].add(cl)
            elif re.search(r"\bbaja\b", cl):
                p["baja"] = (re.search(r"20\d\d-\d\d-\d\d", c) or [""])[0] or "sí"
            elif re.match(r"^cuentas?\s*:", cl):
                p["cuentas"] |= set(CORREO.findall(cl))
            elif re.match(r"^(en\s+)?(google\s+)?drive\s*:", cl):
                p["drive"] |= set(CORREO.findall(cl))
            elif re.match(r"^sin\s+cuenta\b", cl):
                p["sin_cuenta"] = True
            elif re.match(r"^sin\s+confirmar\b", cl):
                p["sin_confirmar"] = True
            elif re.match(r"^tambi[eé]n\s*:", cl):
                p["alias"] += [a.strip() for a in re.split(r"[,;]", c.split(":", 1)[1]) if a.strip()]
            elif re.match(r"^de\s*:", cl):
                p["de"] = c.split(":", 1)[1].strip()
            elif re.match(r"^compartida\s+con\s*:", cl):
                p["compartida"] = c.split(":", 1)[1].strip()
            elif re.match(r"^registra\s*:", cl):
                p["registra"] = c.split(":", 1)[1].strip()
            else:
                reg["avisos"].append(f"«{p['nombre']}»: no se entiende «{c}» (van un correo, «sin cuenta», «en Drive: correo», «también: nombre», «de: organización» o «baja AAAA-MM-DD»)")
        if p["sin_cuenta"] and p["cuentas"]:
            reg["avisos"].append(f"«{p['nombre']}» dice «sin cuenta» y lleva una cuenta: se queda la cuenta")
            p["sin_cuenta"] = False
        if not p["cuentas"] and not p["sin_cuenta"] and not p["baja"]:
            reg["avisos"].append(f"«{p['nombre']}» no lleva ni su cuenta ni «sin cuenta»")
        reg["personas"].append(p)
        for n in ([p["nombre"]] if p["nombre"] != "?" else []) + p["alias"]:
            k = clave_nombre(n)
            if k in reg["nombre"] and reg["nombre"][k] is not p:
                dos_nombres.add(k)
                reg["avisos"].append(f"«{n}» está dos veces: dos personas con el mismo nombre se distinguen con el segundo apellido o una inicial (mientras, ese nombre no es de nadie)")
            reg["nombre"].setdefault(k, p)
        for c in p["cuentas"]:
            if c in reg["cuenta"] and reg["cuenta"][c] is not p:
                dos_cuentas.add(c)
                reg["avisos"].append(f"la cuenta {c} está en dos líneas («{reg['cuenta'][c]['nombre']}» y «{p['nombre']}»; mientras, no es de nadie)")
            reg["cuenta"].setdefault(c, p)
    for k in dos_nombres:
        reg["nombre"].pop(k, None)
    for c in dos_cuentas:
        reg["cuenta"].pop(c, None)
    return reg
def persona(nombre, reg):
    """La persona del registro con ese nombre, alias o cuenta; None si no está o es ambiguo."""
    t = (nombre or "").strip()
    if CORREO.fullmatch(t.lower()):
        return (reg or {}).get("cuenta", {}).get(t.lower())
    return (reg or {}).get("nombre", {}).get(clave_nombre(t))
def nombres_de(texto, reg=None):
    """Los nombres de una celda o una línea («Colabora: Ana Ruiz, Luis Mejía»): sin la etiqueta del principio ni lo que va
    entre paréntesis, separados por comas o «;». Un tramo que no es un nombre del registro se parte además por « y » o
    « e », así que «José Ortega y Gasset» se queda entero si así está declarado."""
    t = re.sub(r"^\s*[-*]?\s*\**\s*(?:colabora[n]?|lo leen?|responsable)\s*\**\s*:\s*\**", "", texto or "", flags=re.I)
    t = re.sub(r"\s*\([^)]*\)", "", t)
    out = []
    for tramo in re.split(r"[,;]", t):
        tramo = tramo.strip(" .*")
        if not tramo or tramo.lower() in ("—", "-", "nadie", "ninguno", "ninguna"):
            continue
        if persona(tramo, reg) is not None or not re.search(r"\s(?:y|e)\s", tramo):
            out.append(tramo)
        else:
            out += [x.strip(" .*") for x in re.split(r"\s+(?:y|e)\s+", tramo) if x.strip(" .*")]
    return out
def cuentas_de_nombres(texto, reg):
    """(cuentas, nombres que no están en el registro) de una celda con nombres. Un correo suelto cuenta solo si es de una
    persona del registro; quien está de baja o sin cuenta no da ninguna."""
    out, faltan = set(), []
    for n in nombres_de(texto, reg):
        p = persona(n, reg)
        if p is None:
            faltan.append(n)
        elif not p["baja"]:
            out |= p["cuentas"]
    return out, faltan
def altas_provisionales(quien, reg):
    """[(nombre, correo)] de las líneas «Colabora:» de un proyecto con «Nombre (correo)» de alguien que no está en el
    registro: el alta provisional (1.25). Solo con registro; sin él, «Nombre (correo)» es la forma de siempre."""
    out = []
    if not (reg or {}).get("hay"):
        return out
    for l in (quien or "").split("\n"):
        if LINEA_COLABORA.match(l):
            for n, c in re.findall(r"([^,;(:]+?)\s*\(\s*(" + CORREO.pattern + r")\s*\)", l):
                n = n.strip(" .*")
                if persona(n, reg) is None and c.lower() not in reg["cuenta"]:
                    out.append((n, c.lower()))
    return out
def columnas_personas(cab):
    """Dónde están Responsable, Cuenta y Colabora en el encabezado de la tabla de áreas (None si no están)."""
    n = [_titulo(x) for x in cab]
    pos = lambda *ns: next((i for i, x in enumerate(n) if x in ns), None)
    return {"responsable": pos("responsable", "dueno", "duena"), "cuenta": pos("cuenta", "cuentas"),
            "colabora": pos("colabora", "colaboran", "colaboradores", "colaboradoras")}
def fila_cuentas(cab, celdas, reg):
    """(responsable, colaboran, aviso) de una fila de la tabla de áreas, como cuentas(): con la columna Cuenta (hasta la
    1.24), de sus correos; con la columna Colabora y «Quién es quién» (1.25), por los nombres. Sin encabezado reconocible,
    la cuarta columna como Cuenta, como siempre. Falla cerrado: un responsable que no está en el registro no es nadie."""
    col = columnas_personas(cab)
    celda = lambda i: celdas[i] if i is not None and i < len(celdas) else ""
    if col["cuenta"] is not None or col["colabora"] is None:
        return cuentas(celda(col["cuenta"] if col["cuenta"] is not None else 3))
    if not (reg or {}).get("hay"):
        return set(), set(), "la tabla nombra a quien colabora por su nombre y guia.md no tiene «Quién es quién»"
    resp = re.sub(r"\s*\((?=[a-záéíóúñ`])[^)]*\)", "", celda(col["responsable"] if col["responsable"] is not None else 2))
    rn = nombres_de(resp, reg)
    avisos, de = [], set()
    if len(rn) > 1 and persona(rn[0], reg) is not None:
        avisos.append(f"en Responsable, lo que sigue a «{rn[0]}» va en «Qué es»")
        rn = rn[:1]
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
    co, faltan = cuentas_de_nombres(celda(col["colabora"]), reg)
    avisos += [f"«{n}» (Colabora) no está en «Quién es quién»" for n in faltan]
    return de, co - de, "; ".join(avisos) or None
def nombre_contexto(linea):
    """El nombre de «Contexto común: Nombre», sin la cuenta entre paréntesis ni lo que sigue a una coma, un punto o una raya."""
    t = re.sub(r"\s*\([^)]*\)", "", (linea or "").split(":", 1)[-1])
    return re.split(r",|\.\s|\.$|\s[—–-]\s|;", t.strip())[0].strip()
def cuentas_contexto(linea, reg):
    """Las cuentas de quien responde por el contexto: la que va entre paréntesis en «Contexto común: Nombre (correo)»
    (hasta la 1.24) o la del registro para ese nombre (1.25)."""
    c = set(CORREO.findall((linea or "").split(":", 1)[-1].lower()))
    if c:
        return c
    p = persona(nombre_contexto(linea), reg)
    return set(p["cuentas"]) if p and not p["baja"] else set()
def nombre_de(cuenta, reg):
    """El nombre del registro de esa cuenta, o "" si no está (o es «?»)."""
    p = (reg or {}).get("cuenta", {}).get((cuenta or "").lower())
    return p["nombre"] if p and p["nombre"] != "?" else ""
def colaboran_en(quien, reg=None):
    """Las cuentas de las líneas «Colabora:» de «Quién participa» de un proyecto (todas las líneas). Sin registro, los
    correos escritos tal cual; con él, las de los nombres, y el correo entre paréntesis solo en un alta provisional."""
    out = set()
    for l in (quien or "").split("\n"):
        if LINEA_COLABORA.match(l):
            if (reg or {}).get("hay"):
                out |= cuentas_de_nombres(l, reg)[0] | {c for _, c in altas_provisionales(l, reg)}
            else:
                out |= set(CORREO.findall(l.lower()))
    return out
