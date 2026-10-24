#!/usr/bin/env python3
"""Migra una raíz del método a la estructura de la 1.22, solo en lo que escribe la cuenta (skill sesion).

Uso: migrar_estructura.py <raiz> --cuenta <correo> [--plan] [--plugin X.Y.Z] [--nombre "Nombre Apellido"]

Lo ofrece la apertura cuando abrir.py dice «Estructura: ANTERIOR»; con el sí de la persona se corre sin --plan. Con
--plan no escribe nada y dice qué haría. Toca solo las áreas de las que la cuenta es responsable (la celda Cuenta de
guia.md, antes de «colabora:») y guia.md si la cuenta es la del responsable de contexto; las áreas de otras cuentas
esperan a que su responsable abra sesión con el plugin 1.22, y una raíz mezclada funciona porque scripts y skills leen
los dos nombres durante la 1.22.

Lo que renombra (contrato, escribir.md, secciones 2, 3, 4 y 5):
  guia.md       la columna «Dueño» pasa a «Responsable»; se añade «Acceso» («Restringida» o «Abierta», por lo que
                decía «Quién la lee»), y «Quién la lee» se queda con a quiénes; «enlaces.md» pasa a «inventario.md».
  area.md       «Panorama» y «Prioridades ahora» se juntan en «Estatus» (la fecha y la primera frase del Panorama en
                negrita, el resto detrás, y las prioridades debajo de «Siguiente»); «Dueño:» pasa a «Responsable:»; la
                línea de un entregable vigente se toma de su aportacion si la tiene; las secciones van en el orden de
                la 1.22 (Estatus, Qué es, Proyectos, Quién participa).
  proyecto.md   «En corto» pasa a «Estatus»; «Terminado significa» se suma a «Objetivo»; «Sí:» y «No:» de Alcance
                pasan a «Entra:» y «No entra:»; «Dueño:» pasa a «Responsable:» y sale «Consumen esto:»; «Estado actual»
                sale del archivo vivo a taller/estado-anterior.md, entero, para que nada se pierda (la siguiente sesión
                lleva lo que dure a Alcance o al Estatus); un proyecto cerrado deja «Proyecto terminado el …» en su
                Estatus; las secciones van en el orden de la 1.22 (Estatus, Objetivo, Alcance, Siguientes pasos, Quién
                participa).
  cabeceras     «afirma:» pasa a «aportacion:» en entregables/ y taller/, y en basado_en «fuentes/enlaces.md» pasa a
                «fuentes/inventario.md»; `actualizado` no se mueve, porque no cambia el contenido.
  archivos      fuentes/enlaces.md y restringido/enlaces.md pasan a inventario.md (si ya existe uno, no se pisa: se dice).
  sesiones.md   una entrada «## AAAA-MM-DD (migracion)» arriba en cada proyecto migrado, con lo que se renombró.

No toca decisiones.md, las entradas ya escritas de sesiones.md, base/ ni lo que hay dentro de fuentes/ y restringido/
salvo su inventario. La fecha es la del día en la zona horaria de guia.md. Repetirlo no hace nada: lo ya migrado no
tiene marcas viejas. Imprime un JSON: «areas», «guia», «pendientes» (áreas de otras cuentas con estructura vieja no se
miran: se nombran las áreas que no son de la cuenta), «archivos» (ruta: lista de cambios), «renombrados», «conflictos»,
«fallidos» y «entradas» (los sesiones.md donde dejó su entrada).
"""
import datetime, json, os, pathlib, re, sys, tempfile

# --- las marcas de la estructura anterior: las mismas que abrir.py (ESTRUCTURA_VIEJA); probar_migrar.py lo comprueba ---
ESTRUCTURA_VIEJA = {
    "area": [r"^## Panorama\s*$", r"^## Prioridades ahora\s*$", r"^\s*[-*]?\s*\**\s*Due[ñn][oa]\s*\**\s*:"],
    "proyecto": [r"^## En corto\s*$", r"^## Estado actual\s*$", r"^## Terminado significa\s*$",
                 r"^\s*[-*]?\s*\**\s*Due[ñn][oa]\s*\**\s*:", r"^\s*[-*]?\s*\**\s*Consumen esto\s*\**\s*:"],
    "archivos": ["fuentes/enlaces.md", "restringido/enlaces.md"],
}

# --- quién escribe: la celda Cuenta de guia.md y la línea «Colabora:» de un proyecto ---
# La misma función en abrir.py, aplicar_cambios.py, generar_vista.py y verificar.sh (cada uno se descarga suelto);
# pruebas/sesion/probar_cuentas.py comprueba que las cuatro copias son idénticas.
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
def colaboran_en(quien):
    """Las cuentas de las líneas «Colabora:» de «Quién participa» de un proyecto (todas las líneas)."""
    return set(c for l in (quien or "").split("\n") if LINEA_COLABORA.match(l) for c in CORREO.findall(l.lower()))
# --- fin de quién escribe ---


def restringida_celda(celda):
    """«Quién la lee» declaraba el área restringida (hasta la 1.21): la palabra al inicio, o suelta sin negarla."""
    c = celda or ""
    if re.match(r"^[\W_]*restringid[oa]s?\b", c, re.I):
        return True
    return bool(re.search(r"\brestringidas?\b", c, re.I)) and not re.search(r"\b(?:nada|no|nunca|sin|antes)\s+(?:[^\s]+\s+)?restringid", c, re.I)


def quienes(celda):
    """«Restringida: dirección» → «Dirección»; «Dirección (restringida)» → «Dirección»; lo demás, tal cual."""
    t = celda or ""
    if not restringida_celda(t):
        return t.strip()
    if re.match(r"^[\W_]*restringid[oa]s?\b", t, re.I):
        t = re.sub(r"^[\W_]*restringid[oa]s?\b[*_»\"”'’\s]*", "", t, flags=re.I)
    else:
        t = re.sub(r"\s*[(\[—–,-]?\s*\brestringidas?\b\s*[)\]]?", "", t, flags=re.I)
    t = re.sub(r"^[:—–,-]\s*", "", t.strip())
    t = re.sub(r"^(?:la|lo)\s+leen\s+", "", t, flags=re.I)
    t = re.sub(r"^(?:a|al|para|solo|sólo|únicamente)\s+", "", t, flags=re.I).strip()
    m = re.fullmatch(r"\((.*)\)", t)
    t = (m.group(1) if m else t).strip()
    return (t[:1].upper() + t[1:]) if t else "Quien administra la carpeta"


def zona_horaria(raiz, defecto="America/Mexico_City"):
    try:
        m = re.search(r"^\s*[-*]?\s*\**\s*zona horaria\s*\**\s*:\s*\**\s*`?\s*([A-Za-z0-9_+-]+(?:/[A-Za-z0-9_+-]+){0,2})",
                      (raiz / "guia.md").read_text(encoding="utf-8-sig"), re.M | re.I)
    except OSError:
        m = None
    try:
        from zoneinfo import ZoneInfo
    except Exception:
        return None
    for z in ([m.group(1)] if m and not m.group(1).startswith("[") else []) + [defecto]:
        try:
            return ZoneInfo(z)
        except Exception:
            continue
    return None


# ---------- leer y escribir ----------
def leer(p):
    b = p.read_bytes()
    t = b.decode("utf-8-sig")
    return t.replace("\r\n", "\n"), "\r\n" in t


def escribir(p, texto, crlf):
    if crlf:
        texto = texto.replace("\n", "\r\n")
    fd, tmp = tempfile.mkstemp(prefix="." + p.name + ".", suffix=".migrar-tmp", dir=p.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(texto)
        os.replace(tmp, p)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def partir(texto):
    """(cabecera con sus «---», prólogo hasta el primer «## » (el título), [(nombre, cuerpo)…])."""
    m = re.match(r"^---\n.*?\n---\n", texto, re.S)
    cab = m.group(0) if m else ""
    resto = texto[len(cab):]
    trozos = re.split(r"^(?=## )", resto, flags=re.M)
    prologo = trozos[0] if trozos and not trozos[0].startswith("## ") else ""
    secciones = []
    for t in trozos:
        if not t.startswith("## "):
            continue
        cabl, _, cuerpo = t.partition("\n")
        secciones.append((cabl[3:].strip(), cuerpo))
    return cab, prologo, secciones


def juntar(cab, prologo, secciones):
    out = cab + prologo
    if secciones and not out.endswith("\n\n"):
        out = out.rstrip("\n") + "\n\n"
    for i, (n, c) in enumerate(secciones):
        c = c.strip("\n")
        out += f"## {n}\n" + (c + "\n" if c else "") + ("\n" if i < len(secciones) - 1 else "")
    return out


def ordenar(secciones, orden):
    """Las secciones conocidas en el orden de la 1.22; las demás, después, en su orden de siempre."""
    conocidas = [s for n in orden for s in secciones if s[0] == n]
    otras = [s for s in secciones if s[0] not in orden]
    return conocidas + otras


def sec(secciones, nombre):
    return next((c for n, c in secciones if n == nombre), None)


def sin(secciones, *nombres):
    return [s for s in secciones if s[0] not in nombres]


def poner(secciones, nombre, cuerpo):
    if any(n == nombre for n, _ in secciones):
        return [(n, cuerpo if n == nombre else c) for n, c in secciones]
    return secciones + [(nombre, cuerpo)]


def clave_cabecera(texto, clave):
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    if not m:
        return None
    v = re.search(r"^" + re.escape(clave) + r":[ \t]*(.*)$", m.group(1), re.M)
    if not v:
        return None
    v = v.group(1).strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v or None


# ---------- las transformaciones ----------
FRASE = re.compile(r"^(.+?[.!?])(\s+|$)(.*)$", re.S)


def estatus_area(panorama, prioridades):
    """El Estatus del área desde el Panorama y las Prioridades ahora de la 1.21, sin inventar nada."""
    lineas = []
    p = (panorama or "").strip()
    if p:
        m = re.match(r"^(20\d\d-\d\d-\d\d)\s*·\s*(.+)$", p, re.S)
        fecha, texto = (m.group(1), m.group(2).strip()) if m else (None, p)
        texto = re.sub(r"\s*\n\s*", " ", texto)
        mf = FRASE.match(texto)
        frase, resto = (mf.group(1), mf.group(3).strip()) if mf else (texto, "")
        lineas.append((f"{fecha} · " if fecha else "") + f"**{frase}**" + (f" {resto}" if resto else ""))
    prios = []
    for l in (prioridades or "").split("\n"):
        t = l.strip()
        if not t:
            continue
        if re.match(r"^([-*]|\d+[.)])\s+", t):
            prios.append(re.sub(r"^([-*]|\d+[.)])\s+", "", t))
        elif prios:
            prios[-1] += " " + t
        else:
            prios.append(t)
    if prios:
        lineas.append("- **Siguiente:**")
        lineas += [f"  - {x}" for x in prios]
    return "\n".join(lineas)


def migrar_area(texto, carpeta, cambios):
    cab, prologo, ss = partir(texto)
    pan, pri = sec(ss, "Panorama"), sec(ss, "Prioridades ahora")
    if sec(ss, "Estatus") is None and (pan is not None or pri is not None):
        est = estatus_area(pan, pri)
        ss = sin(ss, "Panorama", "Prioridades ahora")
        if est:
            ss = poner(ss, "Estatus", est + "\n")
        cambios.append("Panorama y Prioridades ahora → Estatus")
    elif pan is not None or pri is not None:
        ss = sin(ss, "Panorama", "Prioridades ahora")
        cambios.append("quitados Panorama y Prioridades ahora (ya había Estatus)")
    q = sec(ss, "Quién participa")
    if q is not None and re.search(r"^\s*[-*]?\s*\**\s*Due[ñn][oa]\s*\**\s*:", q, re.M):
        ss = poner(ss, "Quién participa", re.sub(r"^(\s*[-*]?\s*\**\s*)Due[ñn][oa](\s*\**\s*:)", r"\1Responsable\2", q, flags=re.M))
        cambios.append("Dueño → Responsable")
    pr = sec(ss, "Proyectos")
    if pr is not None:
        nuevo = re.sub(r"(restringid[oa]\s*:\s*)due[ñn][oa](\s+)", r"\1responsable\2", pr, flags=re.I)
        # la línea de cada entregable vigente, de su aportacion (o su afirma, que esta misma migración renombra)
        actual, out = None, []
        for l in nuevo.split("\n"):
            m = re.match(r"^- `([^`/]+)/?`", l)
            if m:
                actual = m.group(1)
            me = re.match(r"^(\s+- )([\w.-]+)( — )(.*?)(\s·\s*actualizado\s+20\d\d-\d\d-\d\d.*)?$", l)
            if actual and me:
                f = carpeta / actual / "entregables" / (me.group(2) + ".md")
                try:
                    t_ = f.read_text(encoding="utf-8-sig").replace("\r\n", "\n") if f.is_file() else ""
                except OSError:
                    t_ = ""
                ap = clave_cabecera(t_, "aportacion") or clave_cabecera(t_, "afirma")
                if ap and ap != me.group(4).strip():
                    l = f"{me.group(1)}{me.group(2)}{me.group(3)}{ap}{me.group(5) or ''}"
            out.append(l)
        nuevo = "\n".join(out)
        if nuevo != pr:
            ss = poner(ss, "Proyectos", nuevo)
            cambios.append("bloque Proyectos: «responsable» en los restringidos y la línea de los entregables desde su aportacion")
    ss2 = ordenar(ss, ["Estatus", "Qué es", "Proyectos", "Quién participa"])
    if [n for n, _ in ss2] != [n for n, _ in ss]:
        cambios.append("secciones en el orden de la 1.22")
    nuevo = juntar(cab, prologo, ss2)
    return nuevo if cambios else texto


def migrar_proyecto(texto, cambios):
    """(texto nuevo, Estado actual que sale a taller/ o None)."""
    cab, prologo, ss = partir(texto)
    estado = sec(ss, "Estado actual")
    corto = sec(ss, "En corto")
    if sec(ss, "Estatus") is None and corto is not None:
        ss = [("Estatus" if n == "En corto" else n, c) for n, c in ss]
        cambios.append("En corto → Estatus")
    elif corto is not None:
        ss = sin(ss, "En corto")
        cambios.append("quitado En corto (ya había Estatus)")
    # un proyecto cerrado lo decía en Estado actual: pasa al Estatus
    mt = re.search(r"Proyecto terminado el\s*(20\d\d-\d\d-\d\d)", estado or "")
    if mt and not re.search(r"Proyecto terminado el", sec(ss, "Estatus") or ""):
        f = mt.group(1)
        prev = (sec(ss, "Estatus") or "").strip().split("\n")[0]
        prev = re.sub(r"^20\d\d-\d\d-\d\d\s*[·:—-]\s*", "", prev).strip()
        prev = re.sub(r"^\*\*(.*?)\*\*", r"\1", prev).strip()
        ss = poner(ss, "Estatus", f"{f} · **Proyecto terminado el {f}.**" + (f" {prev}" if prev else "") + "\n")
        cambios.append("«Proyecto terminado» pasa al Estatus")
    term = sec(ss, "Terminado significa")
    if term is not None:
        t = re.sub(r"\s*\n\s*", " ", term.strip())
        obj = (sec(ss, "Objetivo") or "").strip()
        if t and not t.startswith("["):
            obj = (obj + (" " if obj else "") + t).strip()
        ss = sin(ss, "Terminado significa")
        ss = poner(ss, "Objetivo", obj + "\n")
        cambios.append("Terminado significa → segunda frase de Objetivo")
    al = sec(ss, "Alcance")
    if al is not None:
        n = re.sub(r"^(\s*[-*]?\s*\**\s*)S[íi](\s*\**\s*:)", r"\1Entra\2", al, flags=re.M)
        n = re.sub(r"(^|[.;]\s+|\s{2,})(\s*[-*]?\s*\**\s*)No(\s*\**\s*:)", r"\1\2No entra\3", n, flags=re.M)
        if n != al:
            ss = poner(ss, "Alcance", n)
            cambios.append("Alcance: Sí/No → Entra/No entra")
    q = sec(ss, "Quién participa")
    if q is not None:
        n = re.sub(r"^(\s*[-*]?\s*\**\s*)Due[ñn][oa](\s*\**\s*:)", r"\1Responsable\2", q, flags=re.M)
        n = re.sub(r"^\s*[-*]?\s*\**\s*Consumen esto\s*\**\s*:.*\n?", "", n, flags=re.M)
        if n != q:
            ss = poner(ss, "Quién participa", n)
            cambios.append("Quién participa: Responsable, sin Consumen esto")
    if estado is not None:
        ss = sin(ss, "Estado actual")
        cambios.append("Estado actual → taller/estado-anterior.md")
    ss2 = ordenar(ss, ["Estatus", "Objetivo", "Alcance", "Siguientes pasos", "Quién participa"])
    if [n for n, _ in ss2] != [n for n, _ in ss]:
        cambios.append("secciones en el orden de la 1.22")
    nuevo = juntar(cab, prologo, ss2)
    nuevo = re.sub(r"\b(fuentes|restringido)/enlaces\.md\b", r"\1/inventario.md", nuevo)
    return (nuevo if cambios or nuevo != texto else texto), estado


def migrar_cabecera(texto):
    """«afirma:» → «aportacion:» y basado_en a fuentes/inventario.md, solo dentro de la cabecera."""
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    if not m:
        return texto
    c = m.group(1)
    n = re.sub(r"^afirma:", "aportacion:", c, flags=re.M) if not re.search(r"^aportacion:", c, re.M) else re.sub(r"^afirma:.*\n?", "", c, flags=re.M)
    n = re.sub(r"(fuentes|restringido)/enlaces\.md\b", r"\1/inventario.md", n)
    return texto if n == c else f"---\n{n}\n---\n" + texto[m.end():]


def migrar_guia(texto, cambios):
    m = re.search(r"^##\s+Áreas\s*\n(.*?)(?=^##\s|\Z)", texto, re.M | re.S)
    if not m:
        return texto
    lineas, col, out = m.group(1).split("\n"), None, []
    for l in lineas:
        if not l.startswith("|"):
            out.append(l); continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if re.match(r"^\|[\s:|-]+\|?\s*$", l):
            out.append(l if col is None or col.get("ok") else "|" + "|".join(["---"] * col["n"]) + "|"); continue
        if col is None:
            n_ = [re.sub(r"[*_`]", "", x).strip().lower() for x in c]
            lee = next((i for i, x in enumerate(n_) if x in ("quién la lee", "quien la lee")), None)
            acc = next((i for i, x in enumerate(n_) if x == "acceso"), None)
            resp = next((i for i, x in enumerate(n_) if x in ("dueño", "dueno")), None)
            col = {"lee": lee, "acc": acc, "ok": acc is not None or lee is None, "n": len(c) + (1 if acc is None and lee is not None else 0)}
            if resp is not None:
                c[resp] = "Responsable"; cambios.append("guia.md: columna Dueño → Responsable")
            if acc is None and lee is not None:
                c.insert(lee + 1, "Acceso"); cambios.append("guia.md: columna Acceso")
            out.append("| " + " | ".join(c) + " |"); continue
        if not col["ok"] and col["lee"] is not None and len(c) > col["lee"]:
            celda = c[col["lee"]]
            c[col["lee"]] = quienes(celda)
            c.insert(col["lee"] + 1, "Restringida" if restringida_celda(celda) else "Abierta")
        out.append("| " + " | ".join(c) + " |")
    nuevo = texto[:m.start(1)] + "\n".join(out) + texto[m.end(1):]
    n2 = re.sub(r"\b(fuentes|restringido)/enlaces\.md\b", r"\1/inventario.md", nuevo)
    if n2 != nuevo:
        cambios.append("guia.md: enlaces.md → inventario.md")
    return n2


def con_entrada_arriba(t, entrada):
    entrada = entrada.strip() + "\n"
    if entrada.strip() in t:
        return t
    m = re.search(r"^# .*\n", t, re.M)
    if m:
        i = m.end()
        resto = t[i:]
        j = re.search(r"^## ", resto, re.M)
        if j:
            prefacio = resto[:j.start()]
            prefacio = "\n" if not prefacio.strip() else prefacio.rstrip("\n") + "\n\n"
            return t[:i] + prefacio + entrada + "\n" + resto[j.start():]
        return t[:i] + "\n" + entrada + ("\n" + resto.lstrip("\n") if resto.strip() else "")
    return t.rstrip("\n") + "\n\n" + entrada


def cabecera_hoy(t, hoy):
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m:
        return t
    cab = re.sub(r"^actualizado:.*$", f"actualizado: {hoy}", m.group(1), count=1, flags=re.M)
    return f"---\n{cab}\n---\n" + t[m.end():]


# ---------- main ----------
def main(argv):
    if len(argv) < 2 or "--cuenta" not in argv:
        print(__doc__.strip(), file=sys.stderr); return 2
    raiz = pathlib.Path(argv[1])
    if not (raiz / "guia.md").is_file():
        print("La raíz es la carpeta con guia.md y metodo.md.", file=sys.stderr); return 2
    op = lambda k, d=None: argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else d
    cuenta = (op("--cuenta") or "").strip().lower()
    plan = "--plan" in argv
    version = op("--plugin", "1.22")
    tz = zona_horaria(raiz)
    hoy = datetime.datetime.now(tz).date().isoformat()

    guia, guia_crlf = leer(raiz / "guia.md")
    m = re.search(r"^##\s+Áreas\s*\n(.*?)(?=^##\s|\Z)", guia, re.M | re.S)
    areas, col = [], None
    for l in (m.group(1) if m else "").split("\n"):
        if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
            continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if col is None:
            n_ = [re.sub(r"[*_`]", "", x).strip().lower() for x in c]
            col = {"resp": next((i for i, x in enumerate(n_) if x in ("responsable", "dueño", "dueno")), 2),
                   "cuenta": next((i for i, x in enumerate(n_) if x == "cuenta"), 3)}
            continue
        if len(c) > max(col.values()):
            areas.append({"slug": c[0].strip("`").rstrip("/"), "nombre": re.sub(r"\s*\([^)]*\)", "", c[col["resp"]]).strip(),
                          "responsables": cuentas(c[col["cuenta"]])[0]})
    ctx = ""
    for l in (re.search(r"^##\s+Quién responde por qué\s*\n(.*?)(?=^##\s|\Z)", guia, re.M | re.S) or [None, ""])[1].split("\n"):
        if l.strip().lower().lstrip("-* ").startswith("contexto común"):
            ctx = l
    # como abrir.py: la cuenta entre paréntesis en «Contexto común»; sin ella, la de las áreas cuyo responsable se llama igual
    cuenta_ctx = set(CORREO.findall(ctx.lower()))
    nombre_ctx = re.sub(r"\s*\([^)]*\)", "", ctx.split(":", 1)[-1]).strip().rstrip(".").strip().lower()
    es_resp = cuenta in cuenta_ctx or (not cuenta_ctx and bool(nombre_ctx) and any(cuenta in a["responsables"] and a["nombre"].lower() == nombre_ctx for a in areas))
    mias = [a for a in areas if cuenta in a["responsables"]]
    nombre = op("--nombre") or (mias[0]["nombre"] if mias else cuenta)
    salida = {"plan": plan, "hoy": hoy, "areas": [a["slug"] for a in mias], "guia": False,
              "pendientes": [a["slug"] for a in areas if cuenta not in a["responsables"]],
              "archivos": {}, "renombrados": [], "conflictos": [], "fallidos": [], "entradas": []}
    escritos = {}   # ruta → (texto, crlf): todo se prepara antes y se escribe al final

    def anotar(rel, cambios):
        if cambios:
            salida["archivos"].setdefault(rel, []).extend(cambios)

    if es_resp:
        cambios = []
        nuevo = migrar_guia(guia, cambios)
        if nuevo != guia:
            escritos["guia.md"] = (nuevo, guia_crlf); salida["guia"] = True; anotar("guia.md", cambios)

    for a in mias:
        carpeta = raiz / a["slug"]
        if not carpeta.is_dir():
            continue
        try:
            proyectos = sorted(d for d in carpeta.iterdir() if d.is_dir() and not d.name.startswith(".") and (d / "proyecto.md").is_file())
        except OSError as ex:
            salida["fallidos"].append({"ruta": a["slug"], "motivo": str(ex)}); continue
        for d in proyectos:
            rel_p = d.relative_to(raiz).as_posix()
            hecho = []
            try:
                tp, crlf = leer(d / "proyecto.md")
            except (OSError, UnicodeDecodeError) as ex:
                salida["fallidos"].append({"ruta": rel_p + "/proyecto.md", "motivo": str(ex)}); continue
            cambios = []
            nuevo, estado = migrar_proyecto(tp, cambios)
            if nuevo != tp:
                escritos[rel_p + "/proyecto.md"] = (nuevo, crlf); anotar(rel_p + "/proyecto.md", cambios); hecho += cambios
            if estado is not None and estado.strip():
                destino = d / "taller" / "estado-anterior.md"
                if destino.exists():
                    salida["conflictos"].append({"ruta": rel_p + "/taller/estado-anterior.md", "motivo": "ya existe: Estado actual no se sacó de proyecto.md"})
                    escritos.pop(rel_p + "/proyecto.md", None); hecho = []
                    salida["archivos"].pop(rel_p + "/proyecto.md", None)
                else:
                    act = clave_cabecera(tp, "actualizado") or hoy
                    titulo = (re.search(r"^# (.+)$", tp, re.M) or [None, d.name])[1]
                    cuerpo = (f"---\nestado: borrador\nactualizado: {act}\n"
                              f"aportacion: \"El estado de {titulo} tal como lo contaba proyecto.md antes de la 1.22; lo que siga valiendo va al Estatus o a Alcance.\"\n"
                              f"basado_en:\n  - {rel_p}/proyecto.md\n---\n\n# Estado de {titulo} hasta la 1.22\n\n{estado.strip()}\n")
                    escritos[rel_p + "/taller/estado-anterior.md"] = (cuerpo, False)
            # inventarios
            for sub in ("fuentes", "restringido"):
                v, n_ = d / sub / "enlaces.md", d / sub / "inventario.md"
                if v.is_file():
                    if n_.exists():
                        salida["conflictos"].append({"ruta": f"{rel_p}/{sub}/enlaces.md", "motivo": "ya hay un inventario.md al lado: no se pisa; juntarlos a mano"})
                    else:
                        salida["renombrados"].append([f"{rel_p}/{sub}/enlaces.md", f"{rel_p}/{sub}/inventario.md"]); hecho.append(f"{sub}/enlaces.md → {sub}/inventario.md")
            # cabeceras de entregables y taller
            for sub in ("entregables", "taller"):
                for dp, dn, fn in os.walk(d / sub):
                    dn[:] = [x for x in dn if not x.startswith(".")]
                    for f in fn:
                        if not f.endswith(".md") or f.startswith("."):
                            continue
                        p = pathlib.Path(dp) / f
                        rel = p.relative_to(raiz).as_posix()
                        try:
                            t, crlf2 = leer(p)
                        except (OSError, UnicodeDecodeError) as ex:
                            salida["fallidos"].append({"ruta": rel, "motivo": str(ex)}); continue
                        n2 = migrar_cabecera(t)
                        if n2 != t:
                            escritos[rel] = (n2, crlf2); anotar(rel, ["cabecera: afirma → aportacion, basado_en a inventario.md"])
                            hecho.append(f"cabecera de {p.relative_to(d).as_posix()}")
            if hecho:
                salida["entradas"].append(rel_p + "/sesiones.md")
                resumen = sorted(set(h for h in hecho if not h.startswith("cabecera de ")))
                ncab = sum(1 for h in hecho if h.startswith("cabecera de "))
                avances = "; ".join(resumen + ([f"«afirma» → «aportacion» en {ncab} cabecera{'s' if ncab != 1 else ''}"] if ncab else []))
                entrada = (f"## {hoy} (migracion)\nTema: la estructura del método pasa a la de la 1.22.\n"
                           f"Avances: {avances}.\nSesión de: {nombre} · plugin {version}")
                escritos.setdefault(rel_p + "/sesiones.md#entrada", (entrada, False))
        # area.md
        pa = carpeta / "area.md"
        if pa.is_file():
            try:
                ta, crlf = leer(pa)
            except (OSError, UnicodeDecodeError) as ex:
                salida["fallidos"].append({"ruta": a["slug"] + "/area.md", "motivo": str(ex)}); continue
            cambios = []
            nuevo = migrar_area(ta, carpeta, cambios)
            if nuevo != ta:
                escritos[a["slug"] + "/area.md"] = (nuevo, crlf); anotar(a["slug"] + "/area.md", cambios)

    if not plan:
        for rel, (texto, crlf) in escritos.items():
            try:
                if rel.endswith("#entrada"):
                    p = raiz / rel[:-len("#entrada")]
                    t, c2 = leer(p)
                    escribir(p, cabecera_hoy(con_entrada_arriba(t, texto), hoy), c2)
                else:
                    p = raiz / rel
                    p.parent.mkdir(parents=True, exist_ok=True)
                    escribir(p, texto, crlf)
            except (OSError, UnicodeDecodeError) as ex:
                salida["fallidos"].append({"ruta": rel.split("#")[0], "motivo": str(ex)})
        for viejo, nuevo in salida["renombrados"]:
            try:
                os.rename(raiz / viejo, raiz / nuevo)
            except OSError as ex:
                salida["fallidos"].append({"ruta": viejo, "motivo": str(ex)})
    print(json.dumps(salida, ensure_ascii=False, indent=1))
    return 1 if salida["fallidos"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
