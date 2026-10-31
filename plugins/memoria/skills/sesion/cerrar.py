#!/usr/bin/env python3
"""Escribe lo que deja un cierre de sesión (skill sesion, anexo cerrar.md), archivo por archivo y sin pisar a nadie.

La skill prepara los textos; este script los escribe. De cada archivo hace leer → cambiar → escribir bajo un cerrojo por
archivo, y comprueba justo antes de escribir que el archivo sigue como lo leyó (misma fecha, tamaño y contenido); si cambió
entre medias, vuelve a leerlo y aplica el cambio sobre lo nuevo (compare-and-swap). Así, dos cierres sobre el mismo
proyecto a la vez no se pierden una entrada ni un paso: cada entrada va encima de lo que haya, y cada reemplazo se aplica
sobre la versión que está en el disco. Lo que otra persona escribió desde que se abrió la sesión se dice (--abierto).

Uso:
  cerrar.py <raiz> <area>/<proyecto> <cambios.json> [--cuenta <correo>] [--abierto <hora ISO de la línea «ahora» de abrir.py>]
            [--sin-fechas] [--forzar <ruta>]... [--fuera-del-area <ruta>]... [--cualquier-fecha] [--sin-rotar] [--comprobar]

cambios.json, todo opcional:
  {"sesion": "## AAAA-MM-DD\\nTema: …\\nAvances: …\\nSesión de: Nombre · plugin X.Y.Z",
   "decisiones": ["## AAAA-MM-DD · Título\\nDecidió: …\\nPor qué: …\\nDescartado: …", …],
   "escribio": ["entregables/x.md", "taller/y.md"], "publico": ["entregables/z.md"],
   "proyecto": {"estatus": "texto entero del bloque Estatus, sin el encabezado: «AAAA-MM-DD · **frase**» y sus viñetas",
                "reemplazos": [{"de": "texto exacto viejo", "a": "texto nuevo"}, …]},
   "area": {"linea": "- `slug/` — descripción",
            "entregables": [{"archivo": "x.md"}, "  - nombre — línea ya escrita · actualizado AAAA-MM-DD", …]},
   "estatus_area": "texto entero del bloque Estatus de area.md, sin el encabezado, con las prioridades debajo de «Siguiente»",
   "otros": [{"ruta": "<relativa a la raíz, dentro del área del proyecto>", "reemplazos": [{"de": "…", "a": "…"}]}, …]}

Se escriben solo los nombres de la 1.22, también en una raíz sin migrar: el bloque Estatus va debajo del título y retira un
«En corto» o un «Panorama» que haya; en un área, retira también «Prioridades ahora», y las prioridades que no estén ya en el
Estatus nuevo se añaden debajo de «Siguiente» (vuelven en «fundidas»), para que no se pierda ninguna; sin ninguno de los
viejos, el Estatus se crea debajo del título. Cada Estatus tiene que empezar por «AAAA-MM-DD · **…**». Una entrada nueva con
«Trabajamos en:», «Pendiente:» o «Descartamos:» se rechaza: los registros viejos se quedan como están, pero lo nuevo se
escribe con «Tema:» y «Descartado:». Un entregable dado como {"archivo": "x.md"} se escribe en area.md como
«  - x — <su aportacion> · actualizado <su fecha>», leídas de su cabecera en entregables/ (o «afirma», si la cabecera aún
no se migró); sin ninguna de las dos, se conserva la línea que ese entregable ya tenía en el bloque y va en «sin_match». Si
«entregables» no viene, las líneas que había debajo del proyecto se conservan: el índice nunca pierde un entregable por un
cierre. «otros» se escribe antes que area.md, para que la línea de un entregable que se publica en la misma llamada lleve
la fecha nueva.

«escribio» y «publico» son los documentos que la sesión escribió (creó o cambió en su contenido) y los que publicó (pasó a
vigente con la skill revisar), con su ruta dentro del proyecto. Van a la entrada de la sesión como «Escribió: …» y
«Publicó: …», justo antes de «Sesión de:», cada una solo si trae algo; así el tablero atribuye cada documento a quien lo
escribió y a quien lo publicó (escribir.md, formato de sesiones.md). Cada ruta tiene que estar en entregables/ o taller/ del
proyecto y existir; lo que se publica, en entregables/ y vigente. Con --abierto, la salida trae en «sin_nombrar» los
documentos de entregables/ y taller/ que cambiaron desde que se abrió y no van en ninguna de las dos listas, para que la
sesión diga si son suyos: no se atribuyen solos, porque pudo escribirlos otra persona. Con --comprobar no se escribe nada:
se validan la forma y la autoría (no los reemplazos ni los permisos) y se devuelven «entrada» (la entrada tal como quedaría, con sus líneas) y «sin_nombrar», para enseñarla
completa antes de pedir el sí. Una «Escribió:» o «Publicó:» tecleada en «sesion» se rechaza, y con «escribio» o «publico»
la entrada tiene que llevar «Sesión de: Nombre».

Antes de escribir una entrada en sesiones.md o en decisiones.md, si el registro pasa de 1.500 líneas o de 100 KB, o su
entrada más nueva es de un año anterior, se archiva entero como «<registro>-<año>.md» (si ya existe, «-2», «-3»…) y el vivo
queda con su cabecera, su título y la línea «Archivado:»; la entrada de hoy va en el nuevo. Vuelve en «rotados» (de, a,
motivo, entradas). --sin-rotar lo evita. abrir.py y el tablero leen los archivados de este año y del anterior junto al vivo.

Antes de escribir nada se comprueba todo: «sesion» empieza por «## AAAA-MM-DD» y cada decisión por «## AAAA-MM-DD · », y esa
fecha es hoy o ayer en la zona horaria de guia.md (la línea HOY de abrir.py), nunca la del reloj de la consola o del
contenedor, que van en UTC y por la tarde ya dicen mañana; una fecha distinta a propósito pasa solo con --cualquier-fecha;
cada ruta de «otros» está dentro del área del proyecto (fuera, solo con --fuera-del-area y nunca guia.md, base/ ni
restringido/). Con --cuenta, el Estatus del área lo escribe solo su responsable (la celda Cuenta de guia.md) y la línea del
proyecto en area.md, el responsable o quien colabora en el área; lo que no toca va en «rechazados». Cada entrada de registro va
arriba del todo, debajo del título; una igual que ya esté no se repite. Un reemplazo cuyo texto viejo no aparece
exactamente una vez, cruza un encabezado «## » o pasa de doce líneas no se aplica y vuelve en «sin_match». Un archivo que
encogería a menos de la mitad no se escribe salvo con --forzar <ruta>. `actualizado` de la cabecera se pone a hoy (salvo cuando lo único que cambia es la cabecera, como añadir `aportacion`) (en la
zona horaria de guia.md) en cada archivo escrito; los finales de línea se conservan como estaban.

Imprime siempre un JSON: «escritos», «sin_match», «rechazados», «fallidos» (un archivo que no se pudo leer o escribir, con
el motivo), «ajenos» (archivos que alguien cambió desde --abierto, con la hora; también los que cambiaron mientras este
cierre escribía; nunca los que este mismo cierre escribió), «reintentos», «hora» (ahora, ISO 8601 en minutos UTC, para la
marca del tablero), «documento» (el id de esa marca) y «escrito_en» (la hora de esta escritura, para pasar como --abierto si
se repite la llamada); y, si alguno de «publico» no quedó vigente tras los reemplazos de «otros», «no_publicado» con
esas rutas y un «error»: no se escribe nada más que «otros», y la misma llamada se repite cuando estén arreglados (1.24.2). Con --sin-fechas (sin consola: la copia lleva la fecha de cuándo se trajo) «ajenos» va vacío.
"""
import datetime
import hashlib
import json
import os
import pathlib
import re
import sys
import tempfile
import time

INTENTOS = 5
MAX_LINEAS_REEMPLAZO = 12
LIMITE_LINEAS, LIMITE_BYTES = 1500, 100_000   # la rotación de los registros (escribir.md, sección 8; por tamaño desde la 1.23)

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


def zona_horaria(raiz, defecto="America/Mexico_City"):
    """La zona de la organización, como la lee abrir.py: la línea «Zona horaria:» de guia.md; si no, Ciudad de México."""
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


def celda_cuenta(raiz, area):
    """(responsables, colaboran) del área según la tabla de guia.md."""
    try:
        guia = (raiz / "guia.md").read_text(encoding="utf-8-sig")
    except OSError:
        return set(), set()
    m = re.search(r"^##\s+Áreas\s*$(.*?)(?=^##\s|\Z)", guia, re.M | re.S)
    col = None
    for l in (m.group(1) if m else "").split("\n"):
        if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
            continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if col is None:   # la columna Cuenta por su encabezado; sin él, la cuarta, como siempre
            n_ = [re.sub(r"[*_`]", "", x).strip().lower() for x in c]
            col = next((i for i, x in enumerate(n_) if x == "cuenta"), 3); continue
        if len(c) > col and c[0].strip("`").rstrip("/") == area:
            de, co, _ = cuentas(c[col])
            return de, co
    return set(), set()


# ---------- leer y escribir ----------
def leer(p):
    with open(p, "rb") as f:
        b = f.read()
    st = os.stat(p)
    t = b.decode("utf-8-sig", errors="replace")
    crlf = "\r\n" in t
    return t.replace("\r\n", "\n"), (st.st_mtime_ns, st.st_size, hashlib.sha1(b).hexdigest()), crlf


def igual(p, firma):
    try:
        st = os.stat(p)
    except OSError:
        return False
    if (st.st_mtime_ns, st.st_size) != firma[:2]:
        return False
    with open(p, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest() == firma[2]


def escribir(p, texto, crlf):
    """Escribe en un temporal único al lado y lo pone en su sitio: nadie lee un archivo a medias."""
    if crlf:
        texto = texto.replace("\n", "\r\n")
    fd, tmp = tempfile.mkstemp(prefix="." + p.name + ".", suffix=".cerrar-tmp", dir=p.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(texto)
        os.replace(tmp, p)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return os.stat(p).st_mtime_ns


class Cerrojo:
    """Un cerrojo por archivo entre procesos de la misma computadora (en el /tmp que comparten las conversaciones)."""
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


# ---------- los cambios sobre el texto ----------
def cabecera_hoy(t, hoy):
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m:
        return t
    cab = re.sub(r"^actualizado:.*$", f"actualizado: {hoy}", m.group(1), count=1, flags=re.M)
    if "actualizado:" not in cab:
        cab += f"\nactualizado: {hoy}"
    return f"---\n{cab}\n---\n" + t[m.end():]


def solo_cabecera(antes, despues):
    """Cierto si lo único que cambió entre los dos textos está dentro de la cabecera (entre los dos «---» iniciales)."""
    m1, m2 = re.match(r"^---\n.*?\n---\n", antes, re.S), re.match(r"^---\n.*?\n---\n", despues, re.S)
    return bool(m1 and m2) and antes[m1.end():] == despues[m2.end():] and antes != despues


def con_entrada_arriba(t, entrada):
    """Una entrada nueva de registro, debajo del título y encima de las demás; si ya está, nada."""
    entrada = entrada.strip() + "\n"
    if entrada.strip() in t:
        return t, False
    m = re.search(r"^# .*\n", t, re.M)
    if m:
        i = m.end()
        resto = t[i:]
        j = re.search(r"^## ", resto, re.M)
        if j:
            prefacio, cuerpo = resto[:j.start()], resto[j.start():]
            if not prefacio.strip():
                prefacio = "\n"
            elif not prefacio.endswith("\n\n"):
                prefacio = prefacio.rstrip("\n") + "\n\n"
            return t[:i] + prefacio + entrada + "\n" + cuerpo, True
        # sin entradas todavía (un registro recién abierto, o recién archivado con su línea «Archivado:»): lo que haya
        # debajo del título se queda delante de la primera entrada
        return t[:i] + ("\n" + resto.strip("\n") + "\n" if resto.strip() else "") + "\n" + entrada, True
    return t.rstrip("\n") + "\n\n" + entrada, True


def sin_bloque(t, nombre):
    """Quita entero el bloque «## nombre», si está."""
    return re.sub(r"^## " + re.escape(nombre) + r"\s*\n.*?(?=^## |\Z)", "", t, count=1, flags=re.M | re.S)


def con_bloque(t, nombre, cuerpo, antes_de=None, alias=()):
    """Reescribe entero el bloque «## nombre». Si no existe, lo crea debajo del título o, con antes_de, justo antes de
    ese bloque (al final si tampoco está). Los bloques de alias (los nombres de la 1.21) se retiran siempre: desde la
    1.22 solo queda el nombre nuevo, y en su sitio de la 1.22, no en el que tenía el viejo."""
    cuerpo = cuerpo.strip() + "\n"
    for viejo in alias:
        t = sin_bloque(t, viejo)
    m = re.search(r"^## " + re.escape(nombre) + r"\s*\n(.*?)(?=^## |\Z)", t, re.M | re.S)
    if m:
        return t[:m.start(1)] + cuerpo + "\n" + t[m.end(1):]
    nuevo = f"## {nombre}\n{cuerpo}\n"
    if antes_de:
        ma = re.search(r"^## " + re.escape(antes_de) + r"\s*$", t, re.M)
        if ma:
            return t[:ma.start()] + nuevo + t[ma.start():]
        return t.rstrip("\n") + "\n\n" + nuevo
    mt = re.search(r"^# .*\n", t, re.M)
    i = mt.end() if mt else 0
    return t[:i] + "\n" + nuevo + t[i:].lstrip("\n")


def con_reemplazos(t, reemplazos, sin_match, ruta):
    for r in reemplazos or []:
        de, a = r.get("de", ""), r.get("a", "")
        n = t.count(de) if de else 0
        if n != 1:
            sin_match.append({"ruta": ruta, "de": de[:120], "veces": n, "motivo": "no aparece exactamente una vez"}); continue
        if re.search(r"^## ", de, re.M) or de.count("\n") >= MAX_LINEAS_REEMPLAZO:
            sin_match.append({"ruta": ruta, "de": de[:120], "veces": n, "motivo": "cruza un encabezado o pasa de doce líneas: parte el reemplazo"}); continue
        t = t.replace(de, a)
    return t


def clave_cabecera(texto, clave):
    """El valor de una clave de la cabecera YAML, sin comillas; None si no está."""
    m = re.match(r"^---\n(.*?)\n---\n", texto.replace("\r\n", "\n"), re.S)
    if not m:
        return None
    v = re.search(r"^" + re.escape(clave) + r":[ \t]*(.*)$", m.group(1), re.M)
    if not v:
        return None
    v = v.group(1).strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1].replace('\\"', '"')
    return v or None


def sublineas_de(t, slug):
    """{nombre: línea} de los entregables que el bloque Proyectos ya lista debajo de un proyecto."""
    m = re.search(r"^## Proyectos\s*\n(.*?)(?=^## |\Z)", t, re.M | re.S)
    out, dentro = {}, False
    for l in (m.group(1) if m else "").split("\n"):
        if re.match(r"^- `" + re.escape(slug) + r"/?`", l):
            dentro = True; continue
        if dentro and l.startswith("  "):
            mm = re.match(r"^\s+-\s+([\w.-]+)", l)
            if mm:
                out[mm.group(1)] = l.rstrip()
            continue
        dentro = False
    return out


def lineas_entregables(pd, entregables, sin_match, rel, existentes):
    """Las líneas de los entregables para area.md: un texto se deja tal cual; {"archivo": "x.md"} se arma con la
    aportacion y la fecha de su cabecera (sección 2 de escribir.md: la línea es su aportacion). Si no se puede armar,
    se conserva la línea que ese entregable ya tenía: el índice nunca pierde una por un cierre."""
    fuera = []
    for e in entregables or []:
        if isinstance(e, str):
            fuera.append(e); continue
        nombre = str((e or {}).get("archivo", "")).replace("\\", "/").strip("/")
        nombre = nombre[len("entregables/"):] if nombre.startswith("entregables/") else nombre
        tallo = pathlib.PurePosixPath(nombre).stem if nombre else ""
        p = pd / "entregables" / nombre
        if not nombre or ".." in nombre.split("/") or not p.is_file():
            sin_match.append({"ruta": rel, "de": f"(entregable {nombre or '?'})", "veces": 0, "motivo": "no existe en entregables/" + ("; se conservó su línea de antes" if tallo in existentes else "")})
            if tallo in existentes:
                fuera.append(existentes[tallo])
            continue
        try:
            texto = p.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            texto = ""
        aporta = clave_cabecera(texto, "aportacion") or clave_cabecera(texto, "afirma")
        fecha = clave_cabecera(texto, "actualizado")
        if not aporta:
            sin_match.append({"ruta": rel, "de": f"(entregable {nombre})", "veces": 0, "motivo": "no tiene aportacion en la cabecera" + ("; se conservó su línea de antes" if tallo in existentes else ": pásale la línea escrita")})
            if tallo in existentes:
                fuera.append(existentes[tallo])
            continue
        fuera.append(f"  - {tallo} — {aporta}" + (f" · actualizado {fecha}" if fecha else ""))
    return fuera


def prioridades_viejas(t):
    """Las viñetas de «Prioridades ahora» (hasta la 1.21), para no perder ninguna al escribir el Estatus del área."""
    m = re.search(r"^## Prioridades ahora\s*\n(.*?)(?=^## |\Z)", t, re.M | re.S)
    out = []
    for l in (m.group(1) if m else "").split("\n"):
        x = l.strip()
        if re.match(r"^([-*]|\d+[.)])\s+", x):
            out.append(re.sub(r"^([-*]|\d+[.)])\s+", "", x))
        elif x and out:
            out[-1] += " " + x
    return [x for x in out if not x.startswith("[")]


def con_siguientes(estatus, nuevas):
    """Añade debajo de «Siguiente» las prioridades que el Estatus no trae (por su texto). Devuelve (texto, añadidas)."""
    faltan = [x for x in nuevas if x and x not in estatus]
    if not faltan:
        return estatus, []
    lineas = estatus.rstrip("\n").split("\n")
    idx = next((k for k, l in enumerate(lineas) if re.match(r"^\s*[-*]\s*\**\s*Siguiente\s*:?\s*\**\s*:?", l, re.I)), None)
    if idx is None:
        idx = next((k for k, l in enumerate(lineas) if re.match(r"^\s*[-*]\s*\**\s*Se completó", l, re.I)), 0)
        lineas[idx + 1:idx + 1] = ["- **Siguiente:**"]; idx += 1
    fin = idx + 1
    while fin < len(lineas) and re.match(r"^\s{2,}[-*]\s+", lineas[fin]):
        fin += 1
    lineas[fin:fin] = [f"  - {x}" for x in faltan]
    return "\n".join(lineas) + "\n", faltan


def con_linea_proyecto(t, slug, linea, entregables):
    """En el bloque Proyectos de area.md: la línea del proyecto y las de sus entregables, sin tocar las demás."""
    m = re.search(r"^## Proyectos\s*\n(.*?)(?=^## |\Z)", t, re.M | re.S)
    if not m:
        return t, False
    bloque = m.group(1).split("\n")
    nuevo = [linea.rstrip()] + [e.rstrip() for e in entregables or []]
    i = next((k for k, l in enumerate(bloque) if re.match(r"^- `" + re.escape(slug) + r"/?`", l)), None)
    if i is None:
        ultimo = max((k for k, l in enumerate(bloque) if l.startswith("- `") or l.startswith("  - ")), default=-1)
        bloque[ultimo + 1:ultimo + 1] = nuevo
    else:
        j = i + 1
        while j < len(bloque) and bloque[j].startswith("  "):
            j += 1
        bloque[i:j] = nuevo
    return t[:m.start(1)] + "\n".join(bloque) + t[m.end(1):], True


def rutas_documento(lista, pd, que, malos, publicar=False, otros_de=None):
    """Normaliza las rutas de «escribio» o «publico»: relativas al proyecto, dentro de entregables/ o taller/, existentes.
    Lo publicado, en entregables/ y con `estado: vigente`, mirado sobre el texto que dejarán los reemplazos de «otros» de
    esta misma llamada (publicar y cerrar en una sola llamada). Lo que no cumple va a «malos» y no se escribe nada."""
    if lista is None:
        return []
    if not isinstance(lista, list):
        malos.append(f"«{que}» va como lista de rutas"); return []
    fuera = []
    for r in lista:
        r = str(r or "").replace("\\", "/").strip().strip("/")
        partes = r.split("/")
        if not r or ".." in partes or partes[0] not in ("entregables", "taller") or len(partes) < 2:
            malos.append(f"«{que}» lleva «{r or '(vacío)'}»: va la ruta dentro del proyecto, en entregables/ o taller/"); continue
        if publicar and partes[0] != "entregables":
            malos.append(f"«{que}» lleva «{r}»: solo se publica lo de entregables/"); continue
        p = pd / r
        if not p.is_file():
            malos.append(f"«{que}» lleva «{r}», que no existe en el proyecto"); continue
        if publicar and r.endswith(".md"):
            try:
                texto_ = p.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
                texto_ = con_reemplazos(texto_, (otros_de or {}).get(r), [], r)
                estado = clave_cabecera(texto_, "estado")
            except (OSError, UnicodeDecodeError):
                estado = None
            if estado != "vigente":
                malos.append(f"«{que}» lleva «{r}», que no está vigente: lo publica la skill revisar antes de cerrar"); continue
        if r not in fuera:
            fuera.append(r)
    return fuera


def con_autoria(entrada, escribio, publico):
    """Pone «Escribió:» y «Publicó:» en la entrada, justo antes de «Sesión de:» (al final si no la tiene)."""
    extra = ([f"Escribió: {', '.join(escribio)}"] if escribio else []) + ([f"Publicó: {', '.join(publico)}"] if publico else [])
    if not extra:
        return entrada
    lineas = entrada.strip("\n").split("\n")
    i = next((k for k, l in enumerate(lineas) if re.match(r"^Sesi[oó]n de\s*:", l)), len(lineas))
    lineas[i:i] = extra
    return "\n".join(lineas)


def sin_nombrar(pd, abierto, nombrados):
    """Documentos de entregables/ y taller/ cambiados desde que se abrió la sesión y que no van en las listas."""
    out = []
    for sub in ("entregables", "taller"):
        base = pd / sub
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            rel = p.relative_to(pd).as_posix()
            if not p.is_file() or any(x.startswith(".") for x in rel.split("/")) or rel in nombrados:
                continue
            try:
                if p.stat().st_mtime > abierto:
                    out.append(rel)
            except OSError:
                pass
    return out


def motivo_rotacion(t, hoy, por_anio=True):
    """Por qué hay que archivar un registro antes de escribir en él, o None: pasa de 1.500 líneas o de 100 KB, o su entrada
    más nueva es de un año anterior al de hoy. Devuelve (motivo, año del archivado)."""
    anios = re.findall(r"^## (20\d\d)-\d\d-\d\d", t, re.M)
    if not anios:
        return None
    anio = max(anios)
    if t.count("\n") + 1 > LIMITE_LINEAS:
        return f"pasa de {LIMITE_LINEAS} líneas", anio
    if len(t.encode("utf-8")) > LIMITE_BYTES:
        return f"pasa de {LIMITE_BYTES // 1000} KB", anio
    if por_anio and anio < hoy[:4]:
        return "cambió el año", anio
    return None


def nombre_archivado(carpeta, nombre, anio):
    """«decisiones-2026.md»; si ya existe, «decisiones-2026-2.md», «-3»…"""
    k, n = 1, f"{nombre}-{anio}.md"
    while (carpeta / n).exists():
        k += 1; n = f"{nombre}-{anio}-{k}.md"
    return n


def entradas_de(t):
    """Las entradas «## …» de un registro, en orden, cada una con su texto sin los saltos del final."""
    return [x.rstrip("\n") for x in re.split(r"^(?=## )", t, flags=re.M) if x.startswith("## ")]


def archivados_en(carpeta, nombre):
    """Todos los archivados de un registro que hay en la carpeta, de más viejo a más nuevo (también los hechos a mano)."""
    vistos = []
    for x in carpeta.iterdir():
        m = re.match(r"^" + nombre + r"-(20\d\d)(?:-(\d+))?\.md$", x.name)
        if m:
            vistos.append((int(m.group(1)), int(m.group(2) or 1), x.name))
    return [n for *_, n in sorted(vistos)]


def registro_nuevo(t, nombre, archivado, hoy, carpeta):
    """El registro vivo recién abierto: su cabecera, su título y la línea «Archivado:» con todos sus archivados, de más
    viejo a más nuevo, para quien lo abra sin el plugin. Las entradas siguen en el archivado, con su identificador."""
    titulo_ = (re.search(r"^# .*$", t, re.M) or [f"# {nombre.capitalize()}"])[0]
    # los que nombraba la línea anterior (sin consola, la copia puede no tenerlos todos) y los que hay en la carpeta
    linea = (re.search(r"^Archivado:.*$", t, re.M) or [""])[0]
    clave = lambda n: tuple(int(x) for x in re.findall(r"\d+", n))
    todos = sorted(set(re.findall(r"\b(" + nombre + r"-20\d\d(?:-\d+)?\.md)", linea)) | set(archivados_en(carpeta, nombre)) | {archivado}, key=clave)
    return (f"---\nestado: vigente\nactualizado: {hoy}\n---\n{titulo_}\n\n"
            f"Archivado: {', '.join(todos)}. Las entradas anteriores están ahí y se citan igual, con su identificador.\n")


# ---------- un archivo ----------
class Cierre:
    def __init__(self, raiz, tz, abierto, sin_fechas, forzar):
        self.raiz, self.tz, self.abierto, self.sin_fechas, self.forzar = raiz, tz, abierto, sin_fechas, forzar
        self.hoy = datetime.datetime.now(tz).date().isoformat()
        self.salida = {"escritos": [], "sin_match": [], "rechazados": [], "fallidos": [], "ajenos": [], "reintentos": 0}
        self.vistos = set()
        # lo que este mismo cierre (u otra llamada suya en esta sesión) escribió, para no darlo por ajeno: el estado va
        # por raíz y por sesión (la hora de apertura), así otra sesión en la misma computadora no lo hereda
        h = hashlib.sha1(f"{raiz.resolve()}|{abierto}".encode()).hexdigest()[:16]
        self.estado = pathlib.Path(tempfile.gettempdir()) / f"memoria-cerrar-{h}.json"
        try:
            self.propios = json.loads(self.estado.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.propios = {}

    def rel(self, p):
        return p.relative_to(self.raiz).as_posix()

    def hora(self, ns):
        return datetime.datetime.fromtimestamp(ns / 1e9, self.tz).isoformat(timespec="minutes")

    def ajeno(self, rel, firma, durante=False):
        if self.sin_fechas or any(a["ruta"] == rel for a in self.salida["ajenos"]):
            return
        propio = self.propios.get(rel) == firma[0]
        if durante or (self.abierto and firma[0] / 1e9 > self.abierto and not propio):
            self.salida["ajenos"].append({"ruta": rel, "hora": self.hora(firma[0]), **({"durante": True} if durante else {})})

    def cambiar(self, p, f):
        """Lee, cambia con f y escribe solo si el archivo sigue igual que al leerlo; si no, repite sobre lo nuevo."""
        rel = self.rel(p)
        try:
            with Cerrojo(p):
                for intento in range(INTENTOS):
                    t, firma, crlf = leer(p)
                    if rel not in self.vistos:
                        self.ajeno(rel, firma)
                    elif intento:
                        self.ajeno(rel, firma, durante=True)
                    self.vistos.add(rel)
                    sin_match = []
                    nuevo, hubo = f(t, sin_match)
                    if not hubo or nuevo == t:
                        self.salida["sin_match"] += sin_match
                        return False
                    # un cambio que se queda dentro de la cabecera (añadir o corregir `aportacion`, por ejemplo) no mueve
                    # `actualizado`: la fecha dice cuándo cambió lo que el documento sostiene, no su cabecera (escribir.md, sección 5)
                    if not solo_cabecera(t, nuevo):
                        nuevo = cabecera_hoy(nuevo, self.hoy)
                    if len(nuevo) < len(t) / 2 and rel not in self.forzar:
                        self.salida["rechazados"].append({"ruta": rel, "motivo": f"encogería de {len(t)} a {len(nuevo)} caracteres; si es a propósito, --forzar {rel}"})
                        return False
                    if igual(p, firma):
                        ns = escribir(p, nuevo, crlf)
                        self.propios[rel] = ns
                        self.salida["sin_match"] += sin_match
                        self.salida["reintentos"] += intento
                        self.salida["escritos"].append(rel)
                        return True
                    time.sleep(0.05 * (intento + 1))
            self.salida["fallidos"].append({"ruta": rel, "motivo": "el archivo cambió cinco veces seguidas mientras se escribía"})
        except (OSError, UnicodeDecodeError) as ex:
            self.salida["fallidos"].append({"ruta": rel, "motivo": f"{type(ex).__name__}: {ex}"})
        return False

    def rotar(self, p, nombre, por_anio=True):
        """Archiva el registro antes de escribir en él si toca (escribir.md, sección 8): lo copia entero a «<nombre>-<año>.md»
        y deja el vivo con su cabecera, su título y la línea «Archivado:». Bajo el mismo cerrojo que las escrituras. Si ya
        hay un archivado idéntico (una rotación que no llegó a encoger el vivo), no lo duplica: solo encoge el vivo. Si el
        vivo cambia entre medias o no se puede escribir, el archivado recién creado se borra y no queda nada a medias."""
        rel = self.rel(p)
        try:
            # una mirada rápida, sin cerrojo: por el tamaño, y si es pequeño, su texto (que entonces cabe en 100 KB)
            if os.stat(p).st_size <= LIMITE_BYTES:
                with open(p, "rb") as f_:
                    if not motivo_rotacion(f_.read().decode("utf-8-sig", errors="replace"), self.hoy, por_anio):
                        return
            with Cerrojo(p):
                t, firma, crlf = leer(p)
                m = motivo_rotacion(t, self.hoy, por_anio)
                if not m:
                    return
                if rel not in self.vistos:
                    self.ajeno(rel, firma); self.vistos.add(rel)
                n_ent = len(re.findall(r"^## ", t, re.M))
                # el archivado lleva cabecera aunque el vivo no la tuviera: un archivado no se edita después
                # sin barras dentro de las llaves de un f-string: Python anterior a 3.12 no lo admite (1.23.1)
                mas_nueva = max(re.findall(r"^## (20\d\d-\d\d-\d\d)", t, re.M))
                arch_txt = t if re.match(r"^---\n", t) else f"---\nestado: vigente\nactualizado: {mas_nueva}\n---\n" + t
                # un archivado del mismo año cuyas entradas están todas en el vivo es una rotación que no llegó a encoger el
                # vivo (o se devolvió a medias y después alguien escribió): no se duplica, y el vivo se queda con lo que el
                # archivado no tiene (revisión de la 1.23, segunda vuelta)
                ents_vivo = entradas_de(t)
                igual_a = None
                for x in archivados_en(p.parent, nombre):
                    if not x.startswith(f"{nombre}-{m[1]}"):
                        continue
                    ea = entradas_de((p.parent / x).read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n"))
                    if ea and all(e in ents_vivo for e in ea):
                        igual_a, quedan = x, [e for e in ents_vivo if e not in ea]
                        break
                creado = None
                if igual_a:
                    arch = igual_a
                else:
                    arch = nombre_archivado(p.parent, nombre, m[1])
                    creado = p.parent / arch
                    fd = os.open(creado, os.O_WRONLY | os.O_CREAT | os.O_EXCL)   # nunca encima de un archivado que ya existe
                    with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
                        f.write(arch_txt.replace("\n", "\r\n") if crlf else arch_txt)
                try:
                    if not igual(p, firma):
                        raise OSError("el registro cambió mientras se archivaba; se archiva en el próximo cierre")
                    nuevo_vivo = registro_nuevo(t, nombre, arch, self.hoy, p.parent)
                    if igual_a and quedan:
                        nuevo_vivo = nuevo_vivo.rstrip("\n") + "\n\n" + "\n\n".join(quedan) + "\n"
                    self.propios[rel] = escribir(p, nuevo_vivo, crlf)
                except OSError:
                    if creado:
                        creado.unlink(missing_ok=True)
                    raise
                if creado:
                    self.propios[self.rel(creado)] = os.stat(creado).st_mtime_ns
                    self.salida["escritos"].append(self.rel(creado))
                self.salida["escritos"].append(rel)
                self.salida.setdefault("rotados", []).append({"de": rel, "a": self.rel(p.parent / arch), "motivo": m[0], "entradas": n_ent,
                                                             **({"ya_estaba": True} if igual_a else {})})
        except (OSError, UnicodeDecodeError) as ex:
            self.salida["fallidos"].append({"ruta": rel, "motivo": f"al archivar: {ex}"})

    def guardar_estado(self):
        try:
            self.estado.write_text(json.dumps(self.propios), encoding="utf-8")
        except OSError:
            pass


def limpiar_temporales(pd, pa):
    for d in (pd, pa):
        try:
            for x in d.iterdir():
                if x.name.endswith(".cerrar-tmp") and time.time() - x.stat().st_mtime > 60:
                    x.unlink()
        except OSError:
            pass


# ---------- main ----------
def main(argv):
    if len(argv) < 4:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    raiz, activo = pathlib.Path(argv[1]), argv[2].strip("/")
    opciones, args = {"--cuenta": None, "--abierto": None}, argv[4:]
    sin_fechas, forzar, fuera = "--sin-fechas" in args, set(), set()
    cualquier_fecha = "--cualquier-fecha" in args
    sin_rotar = "--sin-rotar" in args
    comprobar = "--comprobar" in args
    i = 0
    while i < len(args):
        a = args[i]
        if a in opciones and i + 1 < len(args):
            opciones[a] = args[i + 1]; i += 2
        elif a == "--forzar" and i + 1 < len(args):
            forzar.add(args[i + 1].strip("/")); i += 2
        elif a == "--fuera-del-area" and i + 1 < len(args):
            fuera.add(args[i + 1].strip("/")); i += 2
        elif a in ("--sin-fechas", "--cualquier-fecha", "--sin-rotar", "--comprobar"):
            i += 1
        else:
            print(f"No entiendo «{a}».", file=sys.stderr); return 2
    if "/" not in activo or not (raiz / "guia.md").is_file() or not (raiz / activo).is_dir():
        print("Uso: cerrar.py <raiz> <area>/<proyecto> <cambios.json>", file=sys.stderr); return 2
    try:
        cambios = json.loads(pathlib.Path(argv[3]).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as ex:
        print(f"No se pudo leer cambios.json: {ex}", file=sys.stderr); return 2
    tz = zona_horaria(raiz)
    abierto = None
    if opciones["--abierto"]:
        v = opciones["--abierto"].strip().replace("Z", "+00:00")
        try:
            dt = datetime.datetime.fromisoformat(v)
        except ValueError:
            print("--abierto va con la hora de la línea «ahora» de REGISTROS de abrir.py (ISO 8601)", file=sys.stderr); return 2
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
        abierto = dt.timestamp()
    area, slug = activo.split("/", 1)
    pd, pa = raiz / activo, raiz / area / "area.md"
    c = Cierre(raiz, tz, abierto, sin_fechas, forzar)
    s = c.salida

    # --- todo se comprueba antes de escribir nada ---
    malos = []
    ses = cambios.get("sesion")
    if ses and not re.match(r"^## \d{4}-\d{2}-\d{2}", ses.strip()):
        malos.append("«sesion» tiene que empezar por «## AAAA-MM-DD»")
    for d in cambios.get("decisiones") or []:
        if not re.match(r"^## \d{4}-\d{2}-\d{2} · \S", d.strip()):
            malos.append("cada decisión tiene que empezar por «## AAAA-MM-DD · Título»")
    # la fecha de cada entrada es la del día en la zona de la organización: hoy, o ayer si la sesión cruzó la medianoche
    if not malos and not cualquier_fecha:
        hoy = datetime.datetime.now(tz).date()
        validas = {hoy.isoformat(), (hoy - datetime.timedelta(days=1)).isoformat()}
        for que, e in [("«sesion»", ses)] + [("una decisión", d) for d in cambios.get("decisiones") or []]:
            if not e:
                continue
            f = e.strip()[3:13]
            if f not in validas:
                malos.append(f"{que} lleva la fecha {f} y hoy es {hoy.isoformat()} en {getattr(tz, 'key', tz)} (la línea HOY de abrir.py): "
                             "las fechas de la carpeta van en la zona de la organización, no en la del reloj de la consola o del contenedor; "
                             "si la fecha es a propósito, --cualquier-fecha")
    # lo nuevo se escribe con los nombres de la 1.22; los registros viejos no se tocan
    if ses and re.search(r"^(Trabajamos en|Pendiente)\s*:", ses, re.M):
        malos.append("«sesion» va con «Tema:» y sin «Pendiente:» (lo que sigue va en «Siguiente» del Estatus)")
    for d in cambios.get("decisiones") or []:
        if re.search(r"^Descartamos\s*:", d, re.M):
            malos.append("una decisión lleva «Descartado:», no «Descartamos:»")
    for que, e in (("«estatus»", (cambios.get("proyecto") or {}).get("estatus")), ("«estatus_area»", cambios.get("estatus_area"))):
        if e and not re.match(r"^\s*20\d\d-\d\d-\d\d\s*·\s*\*\*.+?\*\*", e.strip(), re.S):
            malos.append(f"{que} empieza por «AAAA-MM-DD · **frase**», como dice escribir.md")
    # los reemplazos de «otros» sobre documentos de este proyecto, por su ruta dentro de él: publicar (estado: vigente) y
    # cerrar pueden ir en la misma llamada
    otros_de = {}
    for o in cambios.get("otros") or []:
        r_ = str((o or {}).get("ruta", "")).replace("\\", "/").strip("/")
        if r_.startswith(activo + "/"):
            otros_de.setdefault(r_[len(activo) + 1:], []).extend(o.get("reemplazos") or [])
    escribio = rutas_documento(cambios.get("escribio"), pd, "escribio", malos)
    publico = rutas_documento(cambios.get("publico"), pd, "publico", malos, publicar=True, otros_de=otros_de)
    if (escribio or publico) and not ses:
        malos.append("«escribio» y «publico» van en la entrada de la sesión: hace falta «sesion»")
    # quién escribió y quién publicó solo los pone el script: una línea tecleada no se acepta, venga o no la lista
    if ses and re.search(r"^(Escribi[oó]|Public[oó])\s*:", ses, re.M):
        malos.append("«sesion» trae «Escribió:» o «Publicó:» escritos a mano: van solo en «escribio» y «publico», y los escribe el script")
    if ses and (escribio or publico) and not re.search(r"^Sesi[oó]n de\s*:\s*[^\s·]", ses, re.M):
        malos.append("con «escribio» o «publico», la entrada lleva «Sesión de: Nombre Apellido»: sin nombre no hay a quién atribuirlos")
    otros = []
    for o in cambios.get("otros") or []:
        r = str(o.get("ruta", "")).replace("\\", "/").strip("/")
        partes = r.split("/")
        dentro = r.startswith(area + "/")
        if not r or ".." in partes or r.startswith("/") or r in ("guia.md", "metodo.md") or partes[0] == "base" or "restringido" in partes:
            malos.append(f"«otros» no puede tocar {r or '(sin ruta)'}")
        elif not dentro and r not in fuera:
            s["rechazados"].append({"ruta": r, "motivo": "fuera del área del proyecto; solo con --fuera-del-area cuando una regla del área lo pide"})
        else:
            otros.append((r, o))
    if malos:
        print(json.dumps({"error": "; ".join(malos), **s}, ensure_ascii=False)); return 1
    if comprobar:
        # antes de enseñar la entrada: lo que se escribiría y lo que cambió desde la apertura sin nombrarse, sin escribir nada
        out = {"comprobado": True, **({"entrada": con_autoria(ses, escribio, publico)} if ses else {})}
        if abierto and not sin_fechas:
            out["sin_nombrar"] = sin_nombrar(pd, abierto, set(escribio) | set(publico))
        print(json.dumps(out, ensure_ascii=False)); return 0
    cuenta = (opciones["--cuenta"] or "").strip().lower()
    duenos, colaboran = celda_cuenta(raiz, area) if cuenta else (set(), set())
    puede_area = not cuenta or cuenta in duenos | colaboran
    puede_estatus_area = not cuenta or cuenta in duenos
    limpiar_temporales(pd, pa)

    # 9. la rotación, antes de escribir: un registro que pasa de 1.500 líneas o de 100 KB, o de otro año, se archiva y la
    # entrada de hoy abre el nuevo (1.23: antes la hacía la sesión a mano)
    # Se miran los dos registros en todo cierre que escribe en uno de ellos: un decisiones.md grande se archiva aunque hoy no
    # haya decisión (revisión de la 1.23, hallazgo 4)
    # Por el año, solo el registro en el que se escribe: archivar por año las únicas decisiones de un proyecto quieto en un
    # cierre sin decisión las sacaría de lo que se lee al año siguiente (revisión de la 1.23, segunda vuelta)
    if not sin_rotar and (ses or cambios.get("decisiones")):
        for nombre_, escribe in (("sesiones", bool(ses)), ("decisiones", bool(cambios.get("decisiones")))):
            if (pd / f"{nombre_}.md").is_file():
                c.rotar(pd / f"{nombre_}.md", nombre_, por_anio=escribe)
    # otros archivos del área, por reemplazos exactos. Van antes de la entrada de sesiones.md (1.24.2): al publicar y cerrar
    # en una llamada, el «estado: vigente» del documento se escribe primero, y si no se pudo, la entrada no dice «Publicó:»
    # de un borrador (revisión de la 1.23.0, segunda vuelta)
    for r, o in otros:
        p = raiz / r
        if not p.is_file():
            s["fallidos"].append({"ruta": r, "motivo": "no existe"}); continue
        def f_otro(t, sm, o=o, r=r):
            n = con_reemplazos(t, o.get("reemplazos"), sm, r)
            return n, n != t
        c.cambiar(p, f_otro)
    def _vigente_ya(r):
        if not r.endswith(".md"):
            return True
        try:
            return clave_cabecera((pd / r).read_text(encoding="utf-8-sig").replace("\r\n", "\n"), "estado") == "vigente"
        except (OSError, UnicodeDecodeError):
            return False
    # si algo de «publico» no quedó vigente, no se escribe nada más (ni la entrada, ni la línea del entregable en area.md):
    # se dice, se arregla lo de «otros» y se repite la misma llamada, que escribe la entrada entera una sola vez (1.24.2)
    _quedo_borrador = [x for x in publico if not _vigente_ya(x)]
    if _quedo_borrador:
        s["no_publicado"] = _quedo_borrador
        print(json.dumps({"error": "no quedó vigente lo que se publica: " + ", ".join(_quedo_borrador) + ". No se escribió la entrada ni lo demás; "
                          "arregla el reemplazo de «otros» (mira «sin_match» y «rechazados») y repite la misma llamada", **s}, ensure_ascii=False))
        return 1
    # 2. sesiones.md
    if ses:
        entrada = con_autoria(ses, escribio, publico)
        c.cambiar(pd / "sesiones.md", lambda t, sm: con_entrada_arriba(t, entrada))
    # 3. decisiones.md: de la más antigua a la más nueva, para que la última quede arriba
    if cambios.get("decisiones"):
        def f_dec(t, sm):
            hubo = False
            for d in cambios["decisiones"]:
                t, h = con_entrada_arriba(t, d); hubo = hubo or h
            return t, hubo
        c.cambiar(pd / "decisiones.md", f_dec)
    # 4. proyecto.md: Estatus entero (sustituye a «En corto» si la raíz no se migró) y reemplazos exactos en lo demás
    pr = cambios.get("proyecto") or {}
    estatus = pr.get("estatus")
    if estatus or pr.get("reemplazos"):
        def f_pro(t, sm):
            t0 = t
            t = con_reemplazos(t, pr.get("reemplazos"), sm, c.rel(pd / "proyecto.md"))
            if estatus:
                t = con_bloque(t, "Estatus", estatus, alias=("En corto",))
            return t, t != t0
        c.cambiar(pd / "proyecto.md", f_pro)
    # 5 y 10. area.md: la línea del proyecto (con las de sus entregables) y el Estatus del área
    ar = cambios.get("area") or {}
    if ar.get("linea") and not puede_area:
        s["rechazados"].append({"ruta": c.rel(pa), "motivo": f"la línea del proyecto en area.md la escribe el responsable del área o quien colabora en ella; {cuenta} no está en su celda Cuenta: pásasela al responsable"})
        ar = {}
    est_area = cambios.get("estatus_area")
    if est_area and not puede_estatus_area:
        s["rechazados"].append({"ruta": c.rel(pa), "motivo": f"el Estatus del área lo escribe solo su responsable; {cuenta} no lo es"})
        est_area = None
    if ar.get("linea") or est_area:
        def f_area(t, sm):
            t0 = t
            if ar.get("linea"):
                existentes = sublineas_de(t, slug)
                lineas = lineas_entregables(pd, ar.get("entregables"), sm, c.rel(pa), existentes) if "entregables" in ar else list(existentes.values())
                t, ok = con_linea_proyecto(t, slug, ar["linea"], lineas)
                if not ok:
                    sm.append({"ruta": c.rel(pa), "de": "(bloque Proyectos)", "veces": 0, "motivo": "area.md no tiene bloque «## Proyectos»: la línea no se escribió"})
            if est_area:
                # las prioridades de un «Prioridades ahora» que el Estatus nuevo no traiga entran en «Siguiente»; después
                # se retiran «Panorama» y «Prioridades ahora»: desde la 1.22 el Estatus es la única sección de estatus
                est, fundidas = con_siguientes(est_area.strip() + "\n", prioridades_viejas(t))
                if fundidas:
                    s["fundidas"] = s.get("fundidas", []) + fundidas
                t = con_bloque(t, "Estatus", est, alias=("Panorama", "Prioridades ahora"))
            return t, t != t0
        c.cambiar(pa, f_area)
    c.guardar_estado()
    s["escritos"] = list(dict.fromkeys(s["escritos"]))   # un archivo, una vez, aunque lo escriban la rotación y la entrada
    if abierto and not sin_fechas:
        propios = {e[len(activo) + 1:] for e in s["escritos"] if e.startswith(activo + "/")}
        s["sin_nombrar"] = sin_nombrar(pd, abierto, set(escribio) | set(publico) | propios)
    ahora = datetime.datetime.now(datetime.timezone.utc)
    s["hora"] = ahora.strftime("%Y-%m-%dT%H:%MZ")
    s["documento"] = f"{area}--{slug}--{ahora.strftime('%Y%m%d%H%M')}"
    s["escrito_en"] = datetime.datetime.now(tz).isoformat(timespec="seconds")
    print(json.dumps(s, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
