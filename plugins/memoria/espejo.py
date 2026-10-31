#!/usr/bin/env python3
"""La copia de la raíz en el contenedor, para trabajar sin consola en la computadora.

Sin consola quiere decir que la raíz está conectada pero el shell de la computadora no la monta (le pasa a una unidad de
Google Drive para escritorio en Windows, con letra o colgada de una carpeta). Las herramientas que traen y escriben archivos
(device_stage_files, device_commit_files) sí llegan a ella, así que se trabaja sobre una copia en el contenedor: los scripts
del plugin corren sobre la copia y lo que cambia se devuelve a la computadora. Este script no toca la computadora: dice qué
traer, lleva la cuenta de lo que se va a escribir y prepara lo que hay que devolver. Lleva su estado junto a la copia, en
<copia>.estado.json.

Devolver es lo delicado: un archivo de la copia puede estar viejo, a medias o vacío, y device_commit_files lo escribiría
encima del de verdad. Por eso solo se devuelve lo que se registró al traerlo (con su fecha y su tamaño en la computadora) o
lo que se declaró nuevo, y nunca un .md vacío, que pierde su cabecera o que encoge a menos de la mitad, salvo con --forzar.

  espejo.py rutas <copia> [<area>/<proyecto>] [--listado <device_list_dir de la carpeta del proyecto>]
      Qué traer para abrir sesión, por rondas: imprime una ruta por línea (relativa a la raíz) de lo que falta en la copia, o
      COMPLETA. Primera ronda: guia.md, metodo.md, base/premisas.md y base/contexto.md; segunda: el area.md de cada área de la
      tabla de guia.md; tercera, solo con proyecto: el decisiones.md de cada proyecto del índice de su área (lo único que
      abrir.py lee de los demás) y proyecto.md, decisiones.md y sesiones.md del proyecto activo; cuarta, los archivados de
      este año y del anterior que nombra la línea «Archivado:» de esos registros y, con --listado, todos los archivados del
      proyecto activo que hay en la computadora (1.23). Lo que no se trajo se vuelve a
      pedir, salvo lo apuntado con «falta». En la misma conversación la copia se reutiliza: abrir otro proyecto pide solo lo
      suyo, y guia.md, el area.md y los tres archivos del proyecto que se abre se vuelven a pedir si llegaron hace más de diez
      minutos.

  espejo.py permisos <copia>
      Qué traer para revisar los permisos (skill sesion, anexo permisos.md) sobre la copia: el proyecto.md de cada proyecto
      del índice de cada área, por rondas como «rutas» (primero guia.md y los area.md si faltan). Lo que no se trae se
      apunta con «falta»: permisos.py --plan dice qué quedó sin mirar.

  espejo.py falta <copia> <ruta>...
      Apunta lo que no existe en la computadora (device_stage_files rechazó la llamada por ese archivo) para no pedirlo más.

  espejo.py registrar <copia> <ruta> <mtimeMs> <bytes> [<ruta> <mtimeMs> <bytes>...]
      Antes de escribir en un archivo de la copia: apunta la fecha y el tamaño que dio device_stage_files al traerlo, y
      comprueba que el archivo ya llegó entero a la copia (mismo tamaño). Si no, sale con 3: espera unos segundos y repite.

  espejo.py nuevo <copia> <ruta>...
      Declara un archivo que esta sesión crea y que no existe en la computadora (comprobado con device_list_dir de su carpeta).

  espejo.py devolver <copia> <ruta de la raíz en la computadora> [--forzar <ruta>]... [--salidas <carpeta>]
      Lo registrado que cambió y lo nuevo que existe, listo para device_commit_files: copia cada archivo a una carpeta nueva de
      salidas (nunca una ruta ya usada) e imprime un JSON con «lotes» (de 50 como mucho, cada entrada con stagedPath,
      devicePath y, si no es nuevo, expectedMtimeMs; los nuevos van primero y en lotes propios, para que lo que depende de
      ellos se devuelva solo si llegaron), «retenidos» (lo que no pasa la comprobación de contenido, con el motivo)
      y «sin_registrar» (lo que cambió en la copia sin registrar: no se devuelve). Las salidas son /mnt/project-files/ si
      existe y si no /mnt/user-data/outputs/.

  espejo.py instantanea <copia>
      Guarda cómo está la copia, para que «devolver» avise de lo que cambie sin estar registrado. Se corre en cuanto la copia
      está completa.

  espejo.py hecho <copia> <ruta>...
      Lo que device_commit_files escribió (su lista «written», en rutas relativas). Deja de estar registrado: antes de volver a
      escribir en él hay que traerlo y registrarlo otra vez. Cuando no queda nada pendiente, borra sus carpetas de salidas.

  espejo.py marcadores <copia> <archivo con una ruta por línea>
      Crea vacíos, con su nombre, los archivos que no se traen pero el tablero tiene que listar (los entregables que no son
      .md). Nunca toca uno que ya esté. Se corre antes de la instantánea; como no se registran, nunca se devuelven.

  espejo.py subcopia <copia> <destino> <archivo con una ruta por línea>
      Copia esas rutas de la copia a otra carpeta, con su estructura (la copia exacta que pide la generación del tablero).

  espejo.py migracion <copia> <listado>
  espejo.py migracion <copia> --plan <json de migrar_estructura.py --plan>
  espejo.py migracion <copia> --hecha <json de migrar_estructura.py>
      La migración a la estructura de la 1.22 sin consola (skill sesion, migracion.md), en tres tiempos. Con el listado (una
      ruta relativa a la raíz por línea, sacada de device_list_dir de las áreas que se migran), qué traer, por rondas como
      «rutas»: guia.md, cada area.md, el proyecto.md y el sesiones.md de cada proyecto y los .md de sus entregables/ y
      taller/ (solo los de las áreas listadas; la migración reescribe sus cabeceras y su cuerpo nunca sale del contenedor);
      con COMPLETA, deja con su nombre y vacíos los fuentes/ y restringido/ enlaces.md o inventario.md del listado (la
      migración solo los renombra, nunca los lee) y guarda la instantánea. Con --plan, qué traer otra vez y registrar
      (TRAER, los archivos que la migración cambia) y declara nuevos los del taller que crea. Con --hecha, comprueba que
      todo lo que la migración cambió está registrado o declarado, y dice qué renombrar con el conector (RENOMBRAR).

Nunca escribe dentro de la raíz de la computadora ni pide nada de fuentes/, taller/ ni restringido/, salvo los .md del
taller de las áreas que se migran.
"""
import hashlib
import json
import os
import pathlib
import re
import shutil
import sys
import time

FUERA = ("fuentes", "taller", "restringido")
LOTE = 50


def anio_de_la_organizacion(copia):
    """El año de hoy en la zona de la organización («Zona horaria:» de guia.md; si no, Ciudad de México), no el del contenedor,
    que va en UTC: la noche del 31 de diciembre ya diría el año siguiente y traería los archivados de otro año (1.24.2)."""
    try:
        from zoneinfo import ZoneInfo
        import datetime
        m = re.search(r"^\s*[-*]?\s*\**\s*zona horaria\s*\**\s*:\s*\**\s*`?\s*([A-Za-z0-9_+-]+(?:/[A-Za-z0-9_+-]+){0,2})", leer(pathlib.Path(copia) / "guia.md") or "", re.M | re.I)
        try:
            zona = ZoneInfo(m.group(1)) if m else ZoneInfo("America/Mexico_City")
        except Exception:
            zona = ZoneInfo("America/Mexico_City")
        return datetime.datetime.now(zona).year
    except Exception:
        return time.localtime().tm_year


def leer(p):
    try:
        return pathlib.Path(p).read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return None


def seccion(texto, nombre):
    m = re.search(r"^##\s+" + re.escape(nombre) + r"\s*$(.*?)(?=^##\s|\Z)", texto or "", re.M | re.S)
    return m.group(1) if m else ""


def sin_cabecera(texto):
    if texto and texto.startswith("---"):
        partes = texto.split("\n---", 1)
        if len(partes) == 2:
            return partes[1]
    return texto or ""


def areas_de(guia):
    """Los slugs de la tabla de áreas de guia.md, como la leen abrir.py y el tablero: la primera columna, sin comillas ni barra."""
    slugs, cab = [], False
    for l in seccion(guia, "Áreas").split("\n"):
        if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
            continue
        if not cab:
            cab = True
            continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        s = c[0].strip("`").rstrip("/").strip() if c else ""
        if s and "/" not in s and s not in (".", ".."):
            slugs.append(s)
    return slugs


def proyectos_de(texto_area):
    return [m.group(1) for m in re.finditer(r"^- `([^`/]+)/?`", seccion(sin_cabecera(texto_area), "Proyectos"), re.M)]


def limpia(r):
    r = r.strip().replace("\\", "/").strip("/")
    if not r or any(p in ("", ".", "..") for p in r.split("/")):
        raise SystemExit(f"Ruta no válida: «{r}» (va relativa a la raíz, sin «..»).")
    return r


def ruta_estado(copia):
    return pathlib.Path(str(copia).rstrip("/") + ".estado.json")


def estado(copia):
    p = ruta_estado(copia)
    e = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    for k, v in (("faltan", []), ("registrados", {}), ("nuevos", []), ("pendientes", {}), ("salidas", [])):
        e.setdefault(k, v)
    return e


def guarda(copia, e):
    p = ruta_estado(copia)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(e, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")


def huella(p):
    return hashlib.sha1(pathlib.Path(p).read_bytes()).hexdigest()


FRESCO = 10 * 60   # segundos: lo del proyecto que se abre, traído hace más, se vuelve a traer


def archivados_del_listado(ruta):
    """Los registros archivados (`sesiones-AAAA*.md`, `decisiones-AAAA*.md`) del primer nivel de la carpeta del proyecto, de
    cualquier año, según el resultado de device_list_dir guardado en un archivo. Vacío si no se lee."""
    try:
        d = json.loads(pathlib.Path(ruta).read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return []
    ents = (d.get("entries") if isinstance(d, dict) else d) or []
    return sorted(str(e.get("name")) for e in ents if isinstance(e, dict) and e.get("type") == "file"
                  and re.match(r"^(sesiones|decisiones)-20\d\d(?:-\d+)?\.md$", str(e.get("name") or "")))


def rutas(copia, activo, listado=None):
    copia = pathlib.Path(copia)
    faltan = set(estado(copia)["faltan"])
    # en la misma conversación la copia se reutiliza: solo se pide lo que no está. Lo que dice cómo está el proyecto que se
    # abre (guia.md, su area.md y sus tres archivos) se vuelve a pedir si se trajo hace más de diez minutos: la fecha de un
    # archivo de la copia es la de cuándo llegó
    frescos = {"guia.md"} | ({f"{activo.split('/')[0]}/area.md"} | {f"{activo}/{n}" for n in ("proyecto.md", "decisiones.md", "sesiones.md")} if activo else set())
    viejo = lambda r: r in frescos and (copia / r).is_file() and time.time() - (copia / r).stat().st_mtime > FRESCO
    ausente = lambda r: not (copia / r).is_file() and r not in faltan
    falta = lambda r: (ausente(r) or viejo(r)) and r not in faltan
    ronda = [r for r in ("guia.md", "metodo.md", "base/premisas.md", "base/contexto.md") if ausente(r)]
    if not ronda:
        guia = leer(copia / "guia.md")
        if guia is None:
            print("Sin guia.md en la copia: no es la raíz, o la cuenta no la lee.", file=sys.stderr)
            return 1
        areas = areas_de(guia)
        ronda = [f"{a}/area.md" for a in areas if ausente(f"{a}/area.md")]
        if not ronda:
            ronda = sorted(r for r in frescos if viejo(r) and not r.endswith(("proyecto.md", "decisiones.md", "sesiones.md")))
            # sin proyecto, abrir.py solo lee hasta los area.md; con proyecto, de los demás solo lee decisiones.md (el barrido
            # de «Afecta a», «Cuestiona a» y «Responde a»), y del activo sus tres archivos
            if activo:
                for a in areas:
                    ronda += [f"{a}/{p}/decisiones.md" for p in proyectos_de(leer(copia / a / "area.md"))]
                ronda += [f"{activo}/{n}" for n in ("proyecto.md", "decisiones.md", "sesiones.md")]
            ronda = [r for r in dict.fromkeys(ronda) if falta(r) and not set(r.split("/")[:-1]) & set(FUERA)]
            # cuarta ronda, cuando ya están los registros: sus archivados de este año y del anterior, que abrir.py lee junto al
            # vivo (1.23). Los nombra la línea «Archivado:» del registro vivo; los que no existan se apuntan con «falta»
            if activo and not ronda:
                anio = anio_de_la_organizacion(copia)
                vivos = [f"{a}/{p}/decisiones.md" for a in areas for p in proyectos_de(leer(copia / a / "area.md"))] + [f"{activo}/sesiones.md", f"{activo}/decisiones.md"]
                for r in dict.fromkeys(vivos):
                    m = re.search(r"^Archivado:(.*)$", leer(copia / r) or "", re.M)
                    nombre = r.rsplit("/", 1)[1][:-3]
                    for n in re.findall(r"\b(" + nombre + r"-(20\d\d)(?:-\d+)?\.md)", m.group(1) if m else ""):
                        if int(n[1]) >= anio - 1:
                            ronda.append(r.rsplit("/", 1)[0] + "/" + n[0])
                # con el listado de la carpeta del proyecto (device_list_dir), todos sus archivados, de cualquier año: también
                # los hechos a mano o en otra computadora, que «Archivado:» no nombra, para que la rotación no elija un nombre
                # que ya existe y para que sus «Responde a:» cierren cuestionamientos (revisión de la 1.23, segunda vuelta)
                if listado:
                    ronda += [f"{activo}/{n}" for n in archivados_del_listado(listado)]
                ronda = [r for r in dict.fromkeys(ronda) if ausente(r)]
    print("\n".join(ronda) if ronda else "COMPLETA")
    return 0


def permisos(copia):
    """Lo que permisos.py necesita además de la apertura: el proyecto.md de cada proyecto del índice de cada área."""
    copia = pathlib.Path(copia)
    faltan = set(estado(copia)["faltan"])
    ausente = lambda r: not (copia / r).is_file() and r not in faltan
    ronda = [r for r in ("guia.md",) if ausente(r)]
    if not ronda:
        guia = leer(copia / "guia.md")
        if guia is None:
            print("Sin guia.md en la copia: no es la raíz, o la cuenta no la lee.", file=sys.stderr)
            return 1
        areas = areas_de(guia)
        ronda = [f"{a}/area.md" for a in areas if ausente(f"{a}/area.md")]
        if not ronda:
            for a in areas:
                ronda += [f"{a}/{p}/proyecto.md" for p in proyectos_de(leer(copia / a / "area.md")) if ausente(f"{a}/{p}/proyecto.md")]
    print("\n".join(ronda) if ronda else "COMPLETA")
    return 0


def falta(copia, rs):
    e = estado(copia)
    e["faltan"] = sorted(set(e["faltan"]) | {limpia(r) for r in rs})
    guarda(copia, e)
    return 0


def registrar(copia, args):
    if not args or len(args) % 3:
        print("registrar va con tríos: <ruta> <mtimeMs> <bytes>", file=sys.stderr)
        return 2
    copia, e, mal = pathlib.Path(copia), estado(copia), []
    for i in range(0, len(args), 3):
        r, mt, by = limpia(args[i]), int(float(args[i + 1])), int(args[i + 2])
        p = copia / r
        if not p.is_file() or p.stat().st_size != by:
            mal.append(f"{r} (en la copia: {p.stat().st_size if p.is_file() else 'no está'} bytes; en la computadora: {by})")
            continue
        e["registrados"][r] = {"mtimeMs": mt, "bytes": by, "huella": huella(p),
                               "cabecera": p.read_bytes().lstrip(b"\xef\xbb\xbf").startswith(b"---")}
        if r in e["nuevos"]:
            e["nuevos"].remove(r)
    guarda(copia, e)
    if mal:
        print("Aún no llegó entero a la copia: espera unos segundos y vuelve a registrar " + "; ".join(mal), file=sys.stderr)
        return 3
    print(f"{len(args) // 3} registrados")
    return 0


def nuevo(copia, rs):
    e = estado(copia)
    for r in map(limpia, rs):
        if r in e["registrados"]:
            print(f"{r} ya existe en la computadora (se trajo y se registró): no es nuevo.", file=sys.stderr)
            return 2
        if r not in e["nuevos"]:
            e["nuevos"].append(r)
    guarda(copia, e)
    return 0


def motivo_retenido(antes_bytes, ruta, contenido_antes_tenia_cabecera):
    t = ruta.read_bytes()
    if ruta.suffix.lower() != ".md":
        return None
    if not t.strip():
        return "está vacío"
    if contenido_antes_tenia_cabecera and not t.lstrip(b"\xef\xbb\xbf").startswith(b"---"):
        return "perdió su cabecera"
    if antes_bytes and len(t) < antes_bytes / 2:
        return f"encoge de {antes_bytes} a {len(t)} bytes"
    return None


def devolver(copia, raiz_dispositivo, forzar, salidas):
    copia, e = pathlib.Path(copia), estado(copia)
    if salidas is None:
        salidas = "/mnt/project-files" if os.path.isdir("/mnt/project-files") else "/mnt/user-data/outputs"
    destino = pathlib.Path(salidas) / f"espejo-{time.strftime('%Y%m%d%H%M%S')}-{os.getpid()}"
    sep = "\\" if "\\" in raiz_dispositivo and "/" not in raiz_dispositivo else "/"
    base = raiz_dispositivo.rstrip("/\\")
    entradas, retenidos = [], []
    for r in sorted(e["nuevos"]):
        p = copia / r
        if not p.is_file():
            continue
        motivo = None if r in forzar else motivo_retenido(0, p, False)
        if motivo:
            retenidos.append({"rel": r, "motivo": motivo})
            continue
        entradas.append((r, None))
    n_nuevos = len(entradas)
    for r, reg in sorted(e["registrados"].items()):
        p = copia / r
        if not p.is_file() or huella(p) == reg["huella"]:
            continue
        motivo = None if r in forzar else motivo_retenido(reg["bytes"], p, reg.get("cabecera", False))
        if motivo:
            retenidos.append({"rel": r, "motivo": motivo})
            continue
        entradas.append((r, reg["mtimeMs"]))
    # lo que cambió en la copia desde la instantánea sin estar registrado ni declarado nuevo: no se devuelve, se avisa
    conocidos = set(e["registrados"]) | set(e["nuevos"])
    sin_registrar = []
    if e.get("instantanea"):
        for d, ds, fs in os.walk(copia):
            for f in fs:
                r = (pathlib.Path(d) / f).relative_to(copia).as_posix()
                if f.endswith(".cerrar-tmp"):   # un temporal de cerrar.py que quedó a medias: nunca se devuelve
                    continue
                if r not in conocidos and e["instantanea"].get(r) != huella(pathlib.Path(d) / f):
                    sin_registrar.append(r)
    lotes, lote = [], []
    for i, (r, mt) in enumerate(entradas):
        if i == n_nuevos and lote and n_nuevos < len(entradas):   # los nuevos van solos en su(s) lote(s), primero
            lotes.append(lote); lote = []
        dst = destino / r
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(copia / r, dst)
        x = {"stagedPath": str(dst), "devicePath": base + sep + sep.join(r.split("/")), "rel": r}
        if mt is not None:
            x["expectedMtimeMs"] = mt
        e["pendientes"][r] = str(dst)
        lote.append(x)
        if len(lote) == LOTE:
            lotes.append(lote); lote = []
    if lote:
        lotes.append(lote)
    if entradas:
        e["salidas"] = sorted(set(e["salidas"]) | {str(destino)})
    guarda(copia, e)
    print(json.dumps({"lotes": lotes, "retenidos": retenidos, "sin_registrar": sorted(sin_registrar)}, ensure_ascii=False, indent=1))
    return 0


def instantanea(copia):
    instantanea_silenciosa(pathlib.Path(copia))
    print(f"{len(estado(copia)['instantanea'])} archivos")
    return 0


def hecho(copia, rs):
    e = estado(copia)
    for r in map(limpia, rs):
        e["registrados"].pop(r, None)
        e["pendientes"].pop(r, None)
        p = pathlib.Path(copia) / r
        if e.get("instantanea") is not None and p.is_file():
            e["instantanea"][r] = huella(p)
        if r in e["nuevos"]:
            e["nuevos"].remove(r)
    if not e["pendientes"]:
        for s in e["salidas"]:
            shutil.rmtree(s, ignore_errors=True)
        e["salidas"] = []
    guarda(copia, e)
    print(f"pendientes: {len(e['pendientes'])}")
    return 0


def marcadores(copia, lista):
    """Archivos vacíos con el nombre de los que no se traen (los entregables que no son .md), para que el tablero los liste.
    Nunca toca uno que ya esté en la copia. No se devuelven: no están registrados."""
    copia, n = pathlib.Path(copia), 0
    for r in pathlib.Path(lista).read_text(encoding="utf-8").split("\n"):
        if not r.strip():
            continue
        p = copia / limpia(r)
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.touch(); n += 1
    print(f"{n} marcadores")
    return 0


def subcopia(copia, destino, lista):
    copia, destino = pathlib.Path(copia), pathlib.Path(destino)
    for r in pathlib.Path(lista).read_text(encoding="utf-8").split("\n"):
        if not r.strip():
            continue
        r = limpia(r)
        (destino / r).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(copia / r, destino / r)
    return 0


MIG_TRAER = (re.compile(r"^[^/]+/area\.md$"), re.compile(r"^[^/]+/[^/]+/(proyecto|sesiones)\.md$"),
             re.compile(r"^[^/]+/[^/]+/(entregables|taller)/(?:[^/.][^/]*/)?[^/.][^/]*\.md$"))
MIG_MARCA = re.compile(r"^[^/]+/[^/]+/(fuentes|restringido)/(enlaces|inventario)\.md$")


def migracion(copia, resto):
    copia, e = pathlib.Path(copia), estado(copia)
    m = e.setdefault("migracion", {})
    if resto and resto[0] in ("--plan", "--hecha"):
        if len(resto) != 2:
            print("migracion --plan y --hecha van con el JSON que imprimió migrar_estructura.py", file=sys.stderr)
            return 2
        try:
            s = json.loads(pathlib.Path(resto[1]).read_text(encoding="utf-8"))
        except (OSError, ValueError) as ex:
            print(f"No pude leer el JSON de la migración: {ex}", file=sys.stderr)
            return 2
        listado = set(m.get("listado", []))
        cambia = list(s.get("archivos", {})) + list(s.get("entradas", []))
        nuevos = list(s.get("nuevos", []))
        if resto[0] == "--plan":
            for r in nuevos:
                if r in listado:   # la migración no lo crea si existe; si lo pide, la copia está incompleta
                    print(f"{r} existe en la computadora y no está en la copia: tráelo y vuelve a correr el plan.", file=sys.stderr)
                    return 2
                if r not in e["nuevos"]:
                    e["nuevos"].append(r)
            guarda(copia, e)
            traer = sorted(set(r for r in cambia if r not in nuevos))
            print("TRAER\n" + "\n".join(traer) if traer else "NADA QUE TRAER")
            return 0
        conocidos = set(e["registrados"]) | set(e["nuevos"])
        faltan = sorted(set(r for r in cambia + nuevos if r not in conocidos))
        # los renombrados de la copia son marcadores vacíos: la instantánea los da por sabidos para que «devolver» no avise
        inst = e.get("instantanea") or {}
        for viejo, nuevo_ in s.get("renombrados", []):
            inst.pop(viejo, None)
            if (copia / nuevo_).is_file():
                inst[nuevo_] = huella(copia / nuevo_)
        e["instantanea"] = inst
        guarda(copia, e)
        print(json.dumps({"listo": not faltan and not s.get("fallidos"), "sin_registrar": faltan, "fallidos": s.get("fallidos", []),
                          "renombrar": s.get("renombrados", [])}, ensure_ascii=False))
        return 0 if not faltan else 3
    if len(resto) != 1:
        print("migracion va con el listado, o con --plan o --hecha y el JSON de la migración", file=sys.stderr)
        return 2
    try:
        lineas = [l for l in pathlib.Path(resto[0]).read_text(encoding="utf-8").split("\n") if l.strip() and not l.strip().endswith(("/", "\\"))]
    except OSError as ex:
        print(f"No pude leer el listado: {ex}", file=sys.stderr)
        return 2
    listado = sorted(set(map(limpia, lineas)))
    m["listado"] = listado
    faltan = set(e["faltan"])
    viejo = lambda r: time.time() - (copia / r).stat().st_mtime > FRESCO
    ronda = [r for r in ["guia.md"] + [r for r in listado if any(x.match(r) for x in MIG_TRAER)]
             if r not in faltan and (not (copia / r).is_file() or (r == "guia.md" and viejo(r)))]
    if ronda:
        guarda(copia, e)
        print("\n".join(dict.fromkeys(ronda)))
        return 0
    for r in listado:
        if MIG_MARCA.match(r) and not (copia / r).exists():
            (copia / r).parent.mkdir(parents=True, exist_ok=True)
            (copia / r).touch()
    guarda(copia, e)
    instantanea_silenciosa(copia)
    print("COMPLETA")
    return 0


def instantanea_silenciosa(copia):
    e = estado(copia)
    e["instantanea"] = {(pathlib.Path(d) / f).relative_to(copia).as_posix(): huella(pathlib.Path(d) / f)
                        for d, ds, fs in os.walk(copia) for f in fs}
    guarda(copia, e)


def main(argv):
    if len(argv) < 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    orden, copia, resto = argv[1], argv[2], argv[3:]
    if orden == "rutas":
        listado = None
        if "--listado" in resto:
            i = resto.index("--listado"); listado = resto[i + 1] if i + 1 < len(resto) else None; del resto[i:i + 2]
        return rutas(copia, resto[0].strip("/") if resto else None, listado)
    if orden == "permisos":
        return permisos(copia)
    if orden == "falta":
        return falta(copia, resto)
    if orden == "registrar":
        return registrar(copia, resto)
    if orden == "nuevo":
        return nuevo(copia, resto)
    if orden == "instantanea":
        return instantanea(copia)
    if orden == "hecho":
        return hecho(copia, resto)
    if orden == "marcadores" and len(resto) == 1:
        return marcadores(copia, resto[0])
    if orden == "subcopia" and len(resto) == 2:
        return subcopia(copia, resto[0], resto[1])
    if orden == "migracion":
        return migracion(copia, resto)
    if orden == "devolver" and resto:
        raiz, forzar, salidas, i = resto[0], set(), None, 1
        while i < len(resto):
            if resto[i] == "--forzar" and i + 1 < len(resto):
                forzar.add(limpia(resto[i + 1])); i += 2
            elif resto[i] == "--salidas" and i + 1 < len(resto):
                salidas = resto[i + 1]; i += 2
            else:
                print(f"No entiendo «{resto[i]}».", file=sys.stderr)
                return 2
        return devolver(copia, raiz, forzar, salidas)
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
