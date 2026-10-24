#!/usr/bin/env python3
"""Escribe lo que deja un cierre de sesión (skill sesion, anexo cerrar.md), archivo por archivo y sin pisar a nadie.

La skill prepara los textos; este script los escribe. De cada archivo hace leer → cambiar → escribir bajo un cerrojo por
archivo, y comprueba justo antes de escribir que el archivo sigue como lo leyó (misma fecha, tamaño y contenido); si cambió
entre medias, vuelve a leerlo y aplica el cambio sobre lo nuevo (compare-and-swap). Así, dos cierres sobre el mismo
proyecto a la vez no se pierden una entrada ni un paso: cada entrada va encima de lo que haya, y cada reemplazo se aplica
sobre la versión que está en el disco. Lo que otra persona escribió desde que se abrió la sesión se dice (--abierto).

Uso:
  cerrar.py <raiz> <area>/<proyecto> <cambios.json> [--cuenta <correo>] [--abierto <hora ISO de la línea «ahora» de abrir.py>]
            [--sin-fechas] [--forzar <ruta>]... [--fuera-del-area <ruta>]... [--cualquier-fecha]

cambios.json, todo opcional:
  {"sesion": "## AAAA-MM-DD\\nTrabajamos en: …\\nAvances: …\\nPendiente: …\\nSesión de: Nombre · plugin X.Y.Z",
   "decisiones": ["## AAAA-MM-DD · Título\\nDecidió: …\\nPor qué: …", …],
   "proyecto": {"en_corto": "texto entero del bloque En corto, sin el encabezado",
                "reemplazos": [{"de": "texto exacto viejo", "a": "texto nuevo"}, …]},
   "area": {"linea": "- `slug/` — descripción", "entregables": ["  - nombre — descripción · actualizado AAAA-MM-DD", …]},
   "panorama": "texto entero del bloque Panorama de area.md, sin el encabezado",
   "otros": [{"ruta": "<relativa a la raíz, dentro del área del proyecto>", "reemplazos": [{"de": "…", "a": "…"}]}, …]}

Antes de escribir nada se comprueba todo: «sesion» empieza por «## AAAA-MM-DD» y cada decisión por «## AAAA-MM-DD · », y esa
fecha es hoy o ayer en la zona horaria de guia.md (la línea HOY de abrir.py), nunca la del reloj de la consola o del
contenedor, que van en UTC y por la tarde ya dicen mañana; una fecha distinta a propósito pasa solo con --cualquier-fecha;
cada ruta de «otros» está dentro del área del proyecto (fuera, solo con --fuera-del-area y nunca guia.md, base/ ni
restringido/). Con --cuenta, el Panorama lo escribe solo el dueño del área (la celda Cuenta de guia.md) y la línea del
proyecto en area.md, el dueño o quien colabora en el área; lo que no toca va en «rechazados». Cada entrada de registro va
arriba del todo, debajo del título; una igual que ya esté no se repite. Un reemplazo cuyo texto viejo no aparece
exactamente una vez, cruza un encabezado «## » o pasa de doce líneas no se aplica y vuelve en «sin_match». Un archivo que
encogería a menos de la mitad no se escribe salvo con --forzar <ruta>. `actualizado` de la cabecera se pone a hoy (salvo cuando lo único que cambia es la cabecera, como añadir `afirma`) (en la
zona horaria de guia.md) en cada archivo escrito; los finales de línea se conservan como estaban.

Imprime siempre un JSON: «escritos», «sin_match», «rechazados», «fallidos» (un archivo que no se pudo leer o escribir, con
el motivo), «ajenos» (archivos que alguien cambió desde --abierto, con la hora; también los que cambiaron mientras este
cierre escribía; nunca los que este mismo cierre escribió), «reintentos», «hora» (ahora, ISO 8601 en minutos UTC, para la
marca del tablero), «documento» (el id de esa marca) y «escrito_en» (la hora de esta escritura, para pasar como --abierto si
se repite la llamada). Con --sin-fechas (sin consola: la copia lleva la fecha de cuándo se trajo) «ajenos» va vacío.
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

# --- quién escribe: la celda Cuenta de guia.md y la línea «Colabora:» de un proyecto ---
# La misma función en abrir.py, aplicar_cambios.py, generar_vista.py y verificar.sh (cada uno se descarga suelto);
# pruebas/sesion/probar_cuentas.py comprueba que las cuatro copias son idénticas.
CORREO = re.compile(r"[\w.+'-]+@[\w-]+(?:\.[\w-]+)*")
PALABRA_COLABORA = re.compile(r"\bco-?labor\w*\s*:?", re.I)
LINEA_COLABORA = re.compile(r"^\s*[-*]?\s*\**\s*colabora[n]?\s*\**\s*:", re.I)
def cuentas(celda):
    """(dueño, colaboran, aviso) de una celda Cuenta: «dueno@x · colabora: a@x, b@x». Falla cerrado:
    con más de un correo antes de la palabra, o ninguno, nadie es dueño; cualquier palabra que empiece por
    «colabor» separa, para que «colaboradora:» o «colabora» sin dos puntos no conviertan a nadie en dueño."""
    texto = (celda or "").lower()
    partes = PALABRA_COLABORA.split(texto, maxsplit=1)
    antes = set(CORREO.findall(partes[0]))
    despues = set(CORREO.findall(partes[1])) if len(partes) > 1 else set()
    aviso = None
    if len(antes) > 1:
        aviso = "más de un correo antes de «colabora:»; nadie es dueño hasta que se corrija"
        antes = set()
    elif not antes:
        aviso = "sin el correo del dueño"
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
    """(dueños, colaboran) del área según la tabla de guia.md."""
    try:
        guia = (raiz / "guia.md").read_text(encoding="utf-8-sig")
    except OSError:
        return set(), set()
    m = re.search(r"^##\s+Áreas\s*$(.*?)(?=^##\s|\Z)", guia, re.M | re.S)
    cab = False
    for l in (m.group(1) if m else "").split("\n"):
        if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
            continue
        if not cab:
            cab = True; continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) >= 4 and c[0].strip("`").rstrip("/") == area:
            de, co, _ = cuentas(c[3])
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
        return t[:i] + "\n" + entrada + ("\n" + resto.lstrip("\n") if resto.strip() else ""), True
    return t.rstrip("\n") + "\n\n" + entrada, True


def con_bloque(t, nombre, cuerpo, antes_de=None):
    """Reescribe entero el bloque «## nombre». Si no existe, lo crea debajo del título o, con antes_de, justo antes de
    ese bloque (al final si tampoco está)."""
    cuerpo = cuerpo.strip() + "\n"
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
                    # un cambio que se queda dentro de la cabecera (añadir o corregir `afirma`, por ejemplo) no mueve
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
    i = 0
    while i < len(args):
        a = args[i]
        if a in opciones and i + 1 < len(args):
            opciones[a] = args[i + 1]; i += 2
        elif a == "--forzar" and i + 1 < len(args):
            forzar.add(args[i + 1].strip("/")); i += 2
        elif a == "--fuera-del-area" and i + 1 < len(args):
            fuera.add(args[i + 1].strip("/")); i += 2
        elif a in ("--sin-fechas", "--cualquier-fecha"):
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
    cuenta = (opciones["--cuenta"] or "").strip().lower()
    duenos, colaboran = celda_cuenta(raiz, area) if cuenta else (set(), set())
    puede_area = not cuenta or cuenta in duenos | colaboran
    puede_panorama = not cuenta or cuenta in duenos
    limpiar_temporales(pd, pa)

    # 2. sesiones.md
    if ses:
        c.cambiar(pd / "sesiones.md", lambda t, sm: con_entrada_arriba(t, ses))
    # 3. decisiones.md: de la más antigua a la más nueva, para que la última quede arriba
    if cambios.get("decisiones"):
        def f_dec(t, sm):
            hubo = False
            for d in cambios["decisiones"]:
                t, h = con_entrada_arriba(t, d); hubo = hubo or h
            return t, hubo
        c.cambiar(pd / "decisiones.md", f_dec)
    # 4. proyecto.md: En corto entero y reemplazos exactos en lo demás
    pr = cambios.get("proyecto") or {}
    if pr.get("en_corto") or pr.get("reemplazos"):
        def f_pro(t, sm):
            t0 = t
            t = con_reemplazos(t, pr.get("reemplazos"), sm, c.rel(pd / "proyecto.md"))
            if pr.get("en_corto"):
                t = con_bloque(t, "En corto", pr["en_corto"])
            return t, t != t0
        c.cambiar(pd / "proyecto.md", f_pro)
    # 5 y 10. area.md: la línea del proyecto y el Panorama
    ar = cambios.get("area") or {}
    if ar.get("linea") and not puede_area:
        s["rechazados"].append({"ruta": c.rel(pa), "motivo": f"la línea del proyecto en area.md la escribe el dueño del área o quien colabora en ella; {cuenta} no está en su celda Cuenta: pásasela al dueño"})
        ar = {}
    pan = cambios.get("panorama")
    if pan and not puede_panorama:
        s["rechazados"].append({"ruta": c.rel(pa), "motivo": f"el Panorama lo escribe solo el dueño del área; {cuenta} no lo es"})
        pan = None
    if ar.get("linea") or pan:
        def f_area(t, sm):
            t0 = t
            if ar.get("linea"):
                t, ok = con_linea_proyecto(t, slug, ar["linea"], ar.get("entregables"))
                if not ok:
                    sm.append({"ruta": c.rel(pa), "de": "(bloque Proyectos)", "veces": 0, "motivo": "area.md no tiene bloque «## Proyectos»: la línea no se escribió"})
            if pan:
                t = con_bloque(t, "Panorama", pan, antes_de="Quién participa")
            return t, t != t0
        c.cambiar(pa, f_area)
    # otros archivos del área, por reemplazos exactos
    for r, o in otros:
        p = raiz / r
        if not p.is_file():
            s["fallidos"].append({"ruta": r, "motivo": "no existe"}); continue
        def f_otro(t, sm, o=o, r=r):
            n = con_reemplazos(t, o.get("reemplazos"), sm, r)
            return n, n != t
        c.cambiar(p, f_otro)
    c.guardar_estado()
    ahora = datetime.datetime.now(datetime.timezone.utc)
    s["hora"] = ahora.strftime("%Y-%m-%dT%H:%MZ")
    s["documento"] = f"{area}--{slug}--{ahora.strftime('%Y%m%d%H%M')}"
    s["escrito_en"] = datetime.datetime.now(tz).isoformat(timespec="seconds")
    print(json.dumps(s, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
