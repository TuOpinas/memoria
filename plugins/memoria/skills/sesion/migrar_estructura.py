#!/usr/bin/env python3
"""Migra una raíz del método a la estructura de la 1.22, solo en lo que escribe la cuenta (skill sesion).

Uso: migrar_estructura.py <raiz> --cuenta <correo> [--plan] [--plugin X.Y.Z] [--nombre "Nombre Apellido"] [--sin-consola]

Lo ofrece la apertura cuando abrir.py dice «ESTRUCTURA: ANTERIOR»; con el sí de la persona se corre una vez, sin --plan.
Con --plan no escribe nada y dice qué haría. Toca solo las áreas de las que la cuenta es responsable (la celda Cuenta de
guia.md, antes de «colabora:») y guia.md si la cuenta es la del responsable de contexto; las áreas de otras cuentas
esperan a que su responsable abra sesión con el plugin 1.22, y una raíz mezclada funciona porque scripts y skills leen
los dos nombres durante la 1.22. Sin consola (la carpeta no está montada en la computadora) se corre en el contenedor sobre
la copia que arma «espejo.py migracion», con --sin-consola (la entrada de la bitácora lleva la marca), y lo que cambia se
devuelve con espejo.py; los renombrados de archivo los hace después el conector de Drive (skill sesion, migracion.md).

Lo que renombra (contrato, escribir.md, secciones 2, 3, 4 y 5), sin perder nada:
  guia.md       en la primera tabla de «## Áreas», la columna «Dueño» pasa a «Responsable» y se añade «Acceso»
                («Restringida» o «Abierta», por lo que dice «Quién la lee»). La celda «Quién la lee» se deja como está,
                también si empieza por «Restringida:», para que un plugin 1.21 siga viendo el área restringida mientras
                dure la 1.22; los lectores 1.22 ya la limpian. «enlaces.md» pasa a «inventario.md».
  area.md       «Panorama» y «Prioridades ahora» se juntan en «Estatus» (la fecha y la primera frase del Panorama en
                negrita, el resto detrás, las prioridades debajo de «Siguiente» y una línea por proyecto activo con la
                frase de su Estatus); si ya había un «Estatus» al lado, se queda el más reciente por fecha, las
                prioridades que falten se añaden a «Siguiente» y el otro bloque va a taller/estatus-anterior.md; «Dueño:»
                pasa a «Responsable:» en «Quién participa»; la línea de un entregable vigente se toma de su aportacion si
                la tiene; las secciones van en el orden de la 1.22 (Estatus, Qué es, Proyectos, Quién participa).
  proyecto.md   «En corto» pasa a «Estatus»; con un «Estatus» ya al lado, se queda el más reciente y el otro va al
                taller; sin «En corto», el Estatus nace con la fecha de `actualizado` y la primera frase de «Estado
                actual» en negrita; un proyecto cerrado lleva en su Estatus «Proyecto terminado el …» y cómo acabó.
                «Terminado significa» se suma a «Objetivo»; «Sí:» y «No:» de Alcance pasan a «Entra:» y «No entra:»;
                «Dueño:» pasa a «Responsable:» y sale «Consumen esto:», en «Quién participa»; «Estado actual» sale
                entero a taller/estado-anterior.md (en un proyecto cerrado se queda resumido en el Estatus y no se crea
                archivo); las secciones van en el orden de la 1.22 (Estatus, Objetivo, Alcance, Siguientes pasos, Quién
                participa).
  cabeceras     «afirma:» pasa a «aportacion:» en entregables/ y taller/, y en basado_en «fuentes/enlaces.md» pasa a
                «fuentes/inventario.md»; `actualizado` no se mueve, porque no cambia el contenido.
  archivos      fuentes/enlaces.md y restringido/enlaces.md pasan a inventario.md (si ya existe uno, no se pisa: se dice).
  sesiones.md   una entrada «## AAAA-MM-DD (migracion)» arriba en cada proyecto migrado, de una frase.

Cómo escribe: primero los archivos nuevos del taller y, solo si cada uno quedó escrito, su proyecto.md; cada archivo se
relee y se vuelve a transformar en el momento de escribirlo, bajo un cerrojo por archivo, como cerrar.py, para no pisar
un cierre que llegue entre medias. No toca decisiones.md, las entradas ya escritas de sesiones.md, base/ ni lo que hay
dentro de fuentes/ y restringido/ salvo su inventario. La fecha es la del día en la zona horaria de guia.md. Repetirlo
no hace nada. Imprime un JSON compacto con, primero, lo que hay que mirar: «conflictos» (un inventario.md o un
estado-anterior.md que ya existían), «fallidos», «entradas» (los sesiones.md donde dejó su entrada, o la dejaría con
--plan), «resumen» (cuántos archivos por tipo de cambio), «areas», «guia», «pendientes» (áreas de otras cuentas), «nuevos»
(los archivos del taller que crea), «renombrados» y, al final, «archivos» (ruta: cambios).
"""
import datetime, hashlib, json, os, pathlib, re, sys, tempfile

# --- las marcas de la estructura anterior: la misma función en abrir.py; probar_migrar.py comprueba que coinciden ---
def marcas_anteriores(texto, tipo):
    """Qué marcas de la estructura de la 1.21 tiene un area.md («area») o un proyecto.md («proyecto»): las secciones
    viejas, y «Dueño:» o «Consumen esto:» solo dentro de «Quién participa», que es donde la migración las renombra."""
    secs = set(re.findall(r"^## (.+?)\s*$", texto or "", re.M))
    viejas = {"area": ("Panorama", "Prioridades ahora"), "proyecto": ("En corto", "Estado actual", "Terminado significa")}[tipo]
    out = [x for x in viejas if x in secs]
    m = re.search(r"^## Quién participa\s*\n(.*?)(?=^## |\Z)", texto or "", re.M | re.S)
    q = m.group(1) if m else ""
    if re.search(r"^\s*[-*]?\s*\**\s*Due[ñn][oa]\s*\**\s*:", q, re.M):
        out.append("Dueño")
    if tipo == "proyecto" and re.search(r"^\s*[-*]?\s*\**\s*Consumen esto\s*\**\s*:", q, re.M):
        out.append("Consumen esto")
    return out
ARCHIVOS_ANTERIORES = ("fuentes/enlaces.md", "restringido/enlaces.md")

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
    return (t[:1].upper() + t[1:]) if t else ""


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
FECHA_BLOQUE = re.compile(r"^\s*(20\d\d-\d\d-\d\d)\s*[·:—-]")


def fecha_bloque(cuerpo):
    m = FECHA_BLOQUE.match((cuerpo or "").strip())
    return m.group(1) if m else ""


def plantilla(t):
    """Un texto de plantilla sin rellenar («[Tres a cinco líneas…]»), que no es contenido."""
    return (t or "").strip().startswith("[")


def primera_frase(texto):
    """La primera frase de un texto, saltando las tablas, los encabezados y las viñetas que vayan delante; sin prosa, vacía."""
    parrafos = [x.strip() for x in re.split(r"\n\s*\n", (texto or "").strip()) if x.strip()]
    prosa = next((x for x in parrafos if not re.match(r"^(\||#|[-*]\s|\d+[.)]\s|```)", x)), "")
    if not prosa:
        return "", ""
    t = re.sub(r"\s*\n\s*", " ", prosa)
    mf = FRASE.match(t)
    return (mf.group(1), mf.group(3).strip()) if mf else (t, "")


def lista(cuerpo):
    """Las viñetas de un bloque, cada una en una línea (las continuaciones se pegan a la anterior)."""
    out = []
    for l in (cuerpo or "").split("\n"):
        t = l.strip()
        if not t:
            continue
        if re.match(r"^([-*]|\d+[.)])\s+", t):
            out.append(re.sub(r"^([-*]|\d+[.)])\s+", "", t))
        elif out:
            out[-1] += " " + t
        else:
            out.append(t)
    return out


def siguientes_de(estatus):
    """Las prioridades que cuelgan de «Siguiente» en un Estatus de área (sangradas debajo, o en la misma línea)."""
    out, dentro = [], False
    for l in (estatus or "").split("\n"):
        m = re.match(r"^\s*[-*]\s*\**\s*Siguiente\s*:?\s*\**\s*:?\s*(.*)$", l, re.I)
        if m:
            dentro = True
            if m.group(1).strip():
                out.append(m.group(1).strip())
            continue
        if dentro and re.match(r"^\s{2,}[-*]\s+", l):
            out.append(re.sub(r"^\s+[-*]\s+", "", l).strip()); continue
        if dentro and l.strip():
            dentro = False
    return out


def con_siguientes(estatus, nuevas):
    """Añade debajo de «Siguiente» las prioridades que el Estatus no tiene (por su texto); crea la línea si no está."""
    faltan = [x for x in nuevas if x and x not in (estatus or "")]
    if not faltan:
        return estatus
    lineas = (estatus or "").rstrip("\n").split("\n")
    idx = next((k for k, l in enumerate(lineas) if re.match(r"^\s*[-*]\s*\**\s*Siguiente\s*:?\s*\**\s*:?", l, re.I)), None)
    if idx is None:
        # después de «Se completó» si está, si no después de la primera línea
        idx = next((k for k, l in enumerate(lineas) if re.match(r"^\s*[-*]\s*\**\s*Se completó", l, re.I)), 0)
        lineas[idx + 1:idx + 1] = ["- **Siguiente:**"]
        idx += 1
    fin = idx + 1
    while fin < len(lineas) and re.match(r"^\s{2,}[-*]\s+", lineas[fin]):
        fin += 1
    lineas[fin:fin] = [f"  - {x}" for x in faltan]
    return "\n".join(lineas) + "\n"


def estatus_area(panorama, prioridades, proyectos=()):
    """El Estatus del área desde el Panorama y las Prioridades ahora de la 1.21, más una línea por proyecto activo,
    sin inventar nada: una plantilla sin rellenar no cuenta."""
    lineas = []
    p = (panorama or "").strip()
    if p and not plantilla(p):
        m = re.match(r"^(20\d\d-\d\d-\d\d)\s*·\s*(.+)$", p, re.S)
        fecha, texto = (m.group(1), m.group(2).strip()) if m else (None, p)
        frase, resto = primera_frase(texto)
        lineas.append((f"{fecha} · " if fecha else "") + f"**{frase}**" + (f" {resto}" if resto else ""))
    prios = [x for x in lista(prioridades) if not plantilla(x)]
    if prios:
        lineas.append("- **Siguiente:**")
        lineas += [f"  - {x}" for x in prios]
    lineas += [f"- `{slug}/`: {frase}" for slug, frase in proyectos if frase]
    return "\n".join(lineas)


def frase_proyecto(texto_proyecto):
    """La frase de estado de un proyecto para la línea del área: la de su Estatus o «En corto»; sin ellos, la primera
    de «Estado actual». Vacía si no hay o es plantilla."""
    _, _, ss = partir(texto_proyecto or "")
    for n in ("Estatus", "En corto"):
        c = (sec(ss, n) or "").strip()
        if c and not plantilla(c):
            l0 = c.split("\n")[0]
            l0 = re.sub(r"^20\d\d-\d\d-\d\d\s*[·:—-]\s*", "", l0).strip()
            return re.sub(r"\*\*(.+?)\*\*", r"\1", l0).strip()
    c = (sec(ss, "Estado actual") or "").strip()
    return "" if not c or plantilla(c) else primera_frase(c)[0]


def mas_reciente(a, b):
    """De dos bloques de estatus, el de fecha más nueva en su primera línea; en empate o sin fechas, el primero."""
    return b if fecha_bloque(b) > fecha_bloque(a) else a


def migrar_area(texto, carpeta, cambios, proyectos=()):
    """(texto nuevo, bloque viejo que va al taller o None)."""
    cab, prologo, ss = partir(texto)
    pan, pri, est = sec(ss, "Panorama"), sec(ss, "Prioridades ahora"), sec(ss, "Estatus")
    aparte = None
    if pan is not None or pri is not None:
        nuevo_est = estatus_area(pan, pri, proyectos)
        if est is None:
            ss = sin(ss, "Panorama", "Prioridades ahora")
            if nuevo_est:
                ss = poner(ss, "Estatus", nuevo_est + "\n")
            cambios.append("Panorama y Prioridades ahora → Estatus")
        else:
            # ya había Estatus (un cierre 1.22 sobre el área sin migrar, o un Panorama escrito después con la 1.21):
            # se queda el más reciente, las prioridades que falten entran en «Siguiente» y el otro va al taller
            gana = mas_reciente(est, nuevo_est) if pan is not None and not plantilla(pan) else est
            pierde = nuevo_est if gana is est else est
            gana = con_siguientes(gana, [x for x in lista(pri) if not plantilla(x)] + siguientes_de(pierde))
            ss = sin(ss, "Panorama", "Prioridades ahora")
            ss = poner(ss, "Estatus", gana.rstrip("\n") + "\n")
            if pierde and pierde.strip() and pierde.strip() != gana.strip():
                aparte = pierde
            cambios.append("Panorama y Prioridades ahora fundidos en el Estatus" + (" (el bloque que no ganó, al taller)" if aparte else ""))
    q = sec(ss, "Quién participa")
    if q is not None and re.search(r"^\s*[-*]?\s*\**\s*Due[ñn][oa]\s*\**\s*:", q, re.M):
        ss = poner(ss, "Quién participa", re.sub(r"^(\s*[-*]?\s*\**\s*)Due[ñn][oa](\s*\**\s*:)", r"\1Responsable\2", q, flags=re.M))
        cambios.append("Dueño → Responsable")
    pr = sec(ss, "Proyectos")
    if pr is not None:
        nuevo = re.sub(r"(restringid[oa]\s*:\s*)due[ñn][oa](\s+)", r"\1responsable\2", pr, flags=re.I)
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
    return (nuevo if cambios else texto), aparte


def migrar_proyecto(texto, cambios, mover_estado=True):
    """(texto nuevo, lo que va a taller/estado-anterior.md o None). Con mover_estado=False, «Estado actual» se queda."""
    cab, prologo, ss = partir(texto)
    estado = sec(ss, "Estado actual")
    corto = sec(ss, "En corto")
    est = sec(ss, "Estatus")
    aparte = []
    if corto is not None:
        if est is None:
            ss = [("Estatus" if n == "En corto" else n, c) for n, c in ss]
            cambios.append("En corto → Estatus")
        else:
            gana = mas_reciente(est, corto)
            pierde = corto if gana is est else est
            ss = sin(ss, "En corto")
            ss = poner(ss, "Estatus", gana)
            if pierde.strip():
                aparte.append(("## Estatus que no ganó al fundir", pierde))
            cambios.append("En corto y Estatus fundidos (el más reciente se queda; el otro, al taller)")
    cerrado = re.search(r"Proyecto terminado el\s*(20\d\d-\d\d-\d\d)", estado or "")
    est_txt = (sec(ss, "Estatus") or "").strip()
    act = clave_cabecera(texto, "actualizado") or ""
    if cerrado and "Proyecto terminado el" not in est_txt:
        # un proyecto cerrado lo decía en «Estado actual»: el Estatus dice que terminó y cómo acabó, y conserva lo que
        # ya tuviera debajo; no se crea archivo en el taller
        f = cerrado.group(1)
        lineas = est_txt.split("\n") if est_txt else []
        l0 = lineas[0] if lineas else ""
        fecha = fecha_bloque(l0) or f
        l0 = re.sub(r"^20\d\d-\d\d-\d\d\s*[·:—-]\s*", "", l0).strip()
        l0 = re.sub(r"\*\*(.+?)\*\*", r"\1", l0).strip()
        resto_estado = re.sub(r"\s*\n\s*", " ", re.sub(r".*?Proyecto terminado el\s*20\d\d-\d\d-\d\d\.?\s*", "", (estado or "").strip(), count=1, flags=re.S)).strip()
        como = l0 or primera_frase(resto_estado)[0]
        primera = f"{fecha} · **Proyecto terminado el {f}.**" + (f" {como}" if como else "")
        ss = poner(ss, "Estatus", "\n".join([primera] + lineas[1:]) + "\n")
        cambios.append("«Proyecto terminado» pasa al Estatus")
        if mover_estado and estado is not None:
            ss = sin(ss, "Estado actual")
            cambios.append("Estado actual resumido en el Estatus")
        estado = None   # nada va al taller
    elif not est_txt and estado is not None and estado.strip() and not plantilla(estado):
        # sin «En corto»: un Estatus mínimo con la fecha de la cabecera y la primera frase del estado, que ya era público
        frase, _ = primera_frase(estado)
        ss = poner(ss, "Estatus", (f"{act} · " if act else "") + f"**{frase}**\n")
        cambios.append("Estatus mínimo desde la primera frase de Estado actual")
    term = sec(ss, "Terminado significa")
    if term is not None:
        t = re.sub(r"\s*\n\s*", " ", term.strip())
        obj = (sec(ss, "Objetivo") or "").strip()
        if t and not plantilla(t):
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
    if estado is not None and mover_estado:
        ss = sin(ss, "Estado actual")
        cambios.append("Estado actual → taller/estado-anterior.md")
        if estado.strip():
            aparte.insert(0, ("## Estado actual", estado))
    ss2 = ordenar(ss, ["Estatus", "Objetivo", "Alcance", "Siguientes pasos", "Quién participa"])
    if [n for n, _ in ss2] != [n for n, _ in ss]:
        cambios.append("secciones en el orden de la 1.22")
    nuevo = juntar(cab, prologo, ss2)
    nuevo = renombrar_inventario(nuevo)
    return (nuevo if cambios or nuevo != texto else texto), (aparte or None)


def renombrar_inventario(t):
    return re.sub(r"\b(fuentes|restringido)/enlaces\.md\b", r"\1/inventario.md", t)


def migrar_cabecera(texto):
    """«afirma:» → «aportacion:» y basado_en a fuentes/inventario.md, solo dentro de la cabecera."""
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    if not m:
        return texto
    c = m.group(1)
    n = re.sub(r"^afirma:", "aportacion:", c, flags=re.M) if not re.search(r"^aportacion:", c, re.M) else re.sub(r"^afirma:.*\n?", "", c, flags=re.M)
    n = renombrar_inventario(n)
    return texto if n == c else f"---\n{n}\n---\n" + texto[m.end():]


def columnas(cabecera):
    n_ = [re.sub(r"[*_`]", "", x).strip().lower() for x in cabecera]
    pos = lambda *ns: next((i for i, x in enumerate(n_) if x in ns), None)
    return {"resp": pos("responsable", "dueño", "dueno"), "dueno": pos("dueño", "dueno"), "cuenta": pos("cuenta"),
            "lee": pos("quién la lee", "quien la lee"), "acc": pos("acceso")}


def migrar_guia(texto, cambios):
    """Solo la primera tabla de «## Áreas»: «Dueño» → «Responsable» en el encabezado y la columna «Acceso» detrás de
    «Quién la lee», que se deja tal cual (con «Restringida:» si lo lleva, para los plugins 1.21)."""
    m = re.search(r"^##\s+Áreas\s*\n(.*?)(?=^##\s|\Z)", texto, re.M | re.S)
    if not m:
        return texto
    lineas, col, out, en_tabla, tabla_hecha = m.group(1).split("\n"), None, [], False, False
    for l in lineas:
        if not l.startswith("|") or tabla_hecha:
            if en_tabla and not l.startswith("|"):
                tabla_hecha = True
            out.append(l); continue
        en_tabla = True
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if re.match(r"^\|[\s:|-]+\|?\s*$", l):
            out.append(l if col is None or col["ok"] else "|" + "|".join(["---"] * col["n"]) + "|"); continue
        if col is None:
            cc = columnas(c)
            col = {"lee": cc["lee"], "ok": cc["acc"] is not None or cc["lee"] is None, "n": len(c) + (1 if cc["acc"] is None and cc["lee"] is not None else 0)}
            if cc["dueno"] is not None:
                c[cc["dueno"]] = "Responsable"; cambios.append("guia.md: columna Dueño → Responsable")
            if cc["acc"] is None and cc["lee"] is not None:
                c.insert(cc["lee"] + 1, "Acceso"); cambios.append("guia.md: columna Acceso")
            out.append("| " + " | ".join(c) + " |"); continue
        if not col["ok"] and col["lee"] is not None and len(c) > col["lee"]:
            c.insert(col["lee"] + 1, "Restringida" if restringida_celda(c[col["lee"]]) else "Abierta")
        out.append("| " + " | ".join(c) + " |")
    nuevo = texto[:m.start(1)] + "\n".join(out) + texto[m.end(1):]
    n2 = renombrar_inventario(nuevo)
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


def yaml_linea(t):
    """Una línea para una clave de cabecera entre comillas dobles: sin saltos y con las comillas escapadas."""
    return re.sub(r"\s*\n\s*", " ", (t or "")).replace("\\", "\\\\").replace('"', '\\"')


def archivo_taller(rel_p, titulo, act, bloques, nombre):
    """El archivo del taller que recibe lo que sale de un archivo vivo: cabecera, título y cada bloque con su encabezado."""
    cuerpo = "\n\n".join(f"{enc}\n\n{txt.strip()}" for enc, txt in bloques)
    return (f"---\nestado: borrador\nactualizado: {act}\n"
            f"aportacion: \"{yaml_linea(f'Lo que {nombre} decía antes de la 1.22 y salió de él al migrar; lo que siga valiendo va al Estatus o a Alcance.')}\"\n"
            f"basado_en:\n  - {rel_p}/{nombre}\n---\n\n# {titulo}: lo anterior a la 1.22\n\n{cuerpo}\n")


class Cerrojo:
    """Un cerrojo por archivo entre procesos de la misma computadora, el mismo que usa cerrar.py."""
    def __init__(self, p):
        h = hashlib.sha1(str(pathlib.Path(p).resolve()).encode()).hexdigest()[:16]
        self.ruta = os.path.join(tempfile.gettempdir(), f"memoria-cerrar-{h}.lock")
        self.f = None
    def __enter__(self):
        try:
            import fcntl
            self.f = open(self.ruta, "a+")
            fcntl.flock(self.f, fcntl.LOCK_EX)
        except Exception:
            self.f = None
        return self
    def __exit__(self, *a):
        if self.f:
            try:
                import fcntl
                fcntl.flock(self.f, fcntl.LOCK_UN)
            except Exception:
                pass
            self.f.close()


# ---------- main ----------
def main(argv):
    if len(argv) < 2 or "--cuenta" not in argv:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    raiz = pathlib.Path(argv[1])
    if not (raiz / "guia.md").is_file():
        print("La raíz es la carpeta con guia.md y metodo.md.", file=sys.stderr)
        return 2
    op = lambda k, d=None: argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else d
    cuenta = (op("--cuenta") or "").strip().lower()
    plan = "--plan" in argv
    version = op("--plugin", "1.22")
    tz = zona_horaria(raiz)
    hoy = datetime.datetime.now(tz).date().isoformat()

    guia, _ = leer(raiz / "guia.md")
    m = re.search(r"^##\s+Áreas\s*\n(.*?)(?=^##\s|\Z)", guia, re.M | re.S)
    areas, col = [], None
    for l in (m.group(1) if m else "").split("\n"):
        if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
            if col is not None and not l.startswith("|"):
                break   # solo la primera tabla de la sección
            continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if col is None:
            cc = columnas(c)
            col = {"resp": cc["resp"] if cc["resp"] is not None else 2, "cuenta": cc["cuenta"] if cc["cuenta"] is not None else 3}
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
    salida = {"plan": plan, "hoy": hoy, "conflictos": [], "fallidos": [], "entradas": [], "resumen": {},
              "areas": [a["slug"] for a in mias], "guia": False, "pendientes": [a["slug"] for a in areas if cuenta not in a["responsables"]],
              "nuevos": [], "renombrados": [], "archivos": {}}
    # lo que se va a escribir: cada entrada es (ruta relativa, función texto→texto nuevo, o texto entero si es nuevo)
    # el orden importa: taller antes que proyecto.md, y la entrada de la bitácora al final
    tareas = []

    def anotar(rel, cambios):
        if cambios:
            salida["archivos"][rel] = cambios

    if es_resp:
        cambios = []
        nuevo = migrar_guia(guia, cambios)
        if nuevo != guia:
            salida["guia"] = True; anotar("guia.md", cambios)
            tareas.append(("guia.md", lambda t: migrar_guia(t, [])))

    for a in mias:
        carpeta = raiz / a["slug"]
        if not carpeta.is_dir():
            continue
        try:
            proyectos = sorted(d for d in carpeta.iterdir() if d.is_dir() and not d.name.startswith(".") and (d / "proyecto.md").is_file())
        except OSError as ex:
            salida["fallidos"].append({"ruta": a["slug"], "motivo": str(ex)}); continue
        # los proyectos declarados restringidos en el índice del área no llevan línea en su Estatus (contrato, sección 2)
        try:
            ta0, _ = leer(carpeta / "area.md")
        except (OSError, UnicodeDecodeError):
            ta0 = ""
        restringidos = set(re.findall(r"^- `([^`/]+)/?`\s*[—–:-]?\s*[\W_]*restringid[oa]\b", sec(partir(ta0)[2], "Proyectos") or "", re.M | re.I))
        frases = []
        for d in proyectos:
            rel_p = d.relative_to(raiz).as_posix()
            hecho = []
            try:
                tp, _ = leer(d / "proyecto.md")
            except (OSError, UnicodeDecodeError) as ex:
                salida["fallidos"].append({"ruta": rel_p + "/proyecto.md", "motivo": str(ex)}); continue
            destino = d / "taller" / "estado-anterior.md"
            mover = not destino.exists()
            cambios = []
            nuevo, aparte = migrar_proyecto(tp, cambios, mover_estado=mover)
            if not mover and sec(partir(tp)[2], "Estado actual") is not None:
                salida["conflictos"].append({"ruta": rel_p + "/taller/estado-anterior.md", "motivo": "ya existía: «Estado actual» se queda en proyecto.md; lo demás se migró"})
            if nuevo != tp:
                anotar(rel_p + "/proyecto.md", cambios); hecho += cambios
                taller_rel = None
                if aparte:
                    act = clave_cabecera(tp, "actualizado") or hoy
                    titulo = (re.search(r"^# (.+)$", tp, re.M) or [None, d.name])[1]
                    taller_rel = rel_p + "/taller/estado-anterior.md"
                    tareas.append((taller_rel, archivo_taller(rel_p, titulo, act, aparte, "proyecto.md"))); salida["nuevos"].append(taller_rel)
                tareas.append((rel_p + "/proyecto.md", (lambda mv: (lambda t: migrar_proyecto(t, [], mover_estado=mv)[0]))(mover), taller_rel))
            if not cerrado_en(tp) and d.name not in restringidos:
                fr = frase_proyecto(nuevo)
                if fr:
                    frases.append((d.name, fr))
            for sub in ("fuentes", "restringido"):
                v, n_ = d / sub / "enlaces.md", d / sub / "inventario.md"
                if v.is_file():
                    if n_.exists():
                        salida["conflictos"].append({"ruta": f"{rel_p}/{sub}/enlaces.md", "motivo": "ya hay un inventario.md al lado: no se pisa; juntarlos a mano"})
                    else:
                        salida["renombrados"].append([f"{rel_p}/{sub}/enlaces.md", f"{rel_p}/{sub}/inventario.md"]); hecho.append("inventario")
            for sub in ("entregables", "taller"):
                for dp, dn, fn in os.walk(d / sub):
                    dn[:] = [x for x in dn if not x.startswith(".")]
                    for f in fn:
                        if not f.endswith(".md") or f.startswith("."):
                            continue
                        p = pathlib.Path(dp) / f
                        rel = p.relative_to(raiz).as_posix()
                        try:
                            t, _ = leer(p)
                        except (OSError, UnicodeDecodeError) as ex:
                            salida["fallidos"].append({"ruta": rel, "motivo": str(ex)}); continue
                        if migrar_cabecera(t) != t:
                            anotar(rel, ["cabecera: afirma → aportacion, basado_en a inventario.md"]); hecho.append("cabecera")
                            tareas.append((rel, migrar_cabecera))
            if hecho:
                entrada = (f"## {hoy} (migracion)\nTema: la estructura del método pasa a la de la 1.22.\n"
                           f"Avances: secciones, claves y archivos renombrados por el plugin, sin cambiar contenido"
                           + ("; lo que salió de proyecto.md quedó en taller/estado-anterior.md" if any(k == rel_p + "/taller/estado-anterior.md" for k, *_ in tareas) else "")
                           + f".\nSesión de: {nombre} · plugin {version}" + (" · sin consola" if "--sin-consola" in argv else ""))
                tareas.append((rel_p + "/sesiones.md#entrada", entrada))
        pa = carpeta / "area.md"
        if pa.is_file():
            try:
                ta, _ = leer(pa)
            except (OSError, UnicodeDecodeError) as ex:
                salida["fallidos"].append({"ruta": a["slug"] + "/area.md", "motivo": str(ex)}); continue
            cambios = []
            nuevo, aparte = migrar_area(ta, carpeta, cambios, frases)
            if nuevo != ta:
                anotar(a["slug"] + "/area.md", cambios)
                taller_rel = None
                if aparte:
                    # el bloque que no ganó va al taller del primer proyecto del área: el área no tiene taller propio
                    if proyectos:
                        dp0 = proyectos[0]
                        taller_rel = dp0.relative_to(raiz).as_posix() + "/taller/estatus-anterior-del-area.md"
                        if (raiz / taller_rel).exists():
                            salida["conflictos"].append({"ruta": taller_rel, "motivo": "ya existía: el bloque de estatus que no ganó no se guardó"}); taller_rel = None
                        else:
                            tareas.append((taller_rel, archivo_taller(a["slug"], a["slug"], clave_cabecera(ta, "actualizado") or hoy, [("## Estatus del área que no ganó al fundir", aparte)], "area.md"))); salida["nuevos"].append(taller_rel)
                    else:
                        salida["conflictos"].append({"ruta": a["slug"] + "/area.md", "motivo": "había dos bloques de estatus y el área no tiene proyectos donde guardar el que no ganó"})
                tareas.append((a["slug"] + "/area.md", (lambda cp, fr: (lambda t: migrar_area(t, cp, [], fr)[0]))(carpeta, frases), taller_rel))

    resumen = {}
    for cambios in salida["archivos"].values():
        for c in cambios:
            resumen[c] = resumen.get(c, 0) + 1
    salida["resumen"] = resumen

    if plan:
        salida["entradas"] = [tarea[0][:-len("#entrada")] for tarea in tareas if tarea[0].endswith("#entrada")]
    else:
        escritos_ok = set()
        for tarea in tareas:
            rel, que = tarea[0], tarea[1]
            depende = tarea[2] if len(tarea) > 2 else None
            if depende and depende not in escritos_ok:
                salida["fallidos"].append({"ruta": rel, "motivo": f"no se escribió porque falló {depende}; nada se perdió"})
                salida["archivos"].pop(rel, None)
                continue
            try:
                if rel.endswith("#entrada"):
                    p = raiz / rel[:-len("#entrada")]
                    with Cerrojo(p):
                        t, c2 = leer(p)
                        escribir(p, cabecera_hoy(con_entrada_arriba(t, que), hoy), c2)
                    salida["entradas"].append(rel[:-len("#entrada")])
                elif isinstance(que, str):
                    p = raiz / rel
                    p.parent.mkdir(parents=True, exist_ok=True)
                    escribir(p, que, False)
                    escritos_ok.add(rel)
                else:
                    p = raiz / rel
                    with Cerrojo(p):
                        t, crlf = leer(p)   # se relee y se vuelve a transformar: lo que otro escribió entre medias se respeta
                        n = que(t)
                        if n != t:
                            escribir(p, n, crlf)
                    escritos_ok.add(rel)
            except (OSError, UnicodeDecodeError) as ex:
                salida["fallidos"].append({"ruta": rel.split("#")[0], "motivo": str(ex)})
        salida["nuevos"] = [r for r in salida["nuevos"] if r in escritos_ok]
        for viejo, nuevo in salida["renombrados"]:
            try:
                os.rename(raiz / viejo, raiz / nuevo)
            except OSError as ex:
                salida["fallidos"].append({"ruta": viejo, "motivo": str(ex)})
    print(json.dumps(salida, ensure_ascii=False))
    return 1 if salida["fallidos"] else 0


def cerrado_en(texto_proyecto):
    _, _, ss = partir(texto_proyecto or "")
    return any(re.search(r"Proyecto terminado el\s*20\d\d-\d\d-\d\d", sec(ss, n) or "") for n in ("Estatus", "Estado actual", "En corto"))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
