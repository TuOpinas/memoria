#!/usr/bin/env python3
"""Lo que hay que leer para abrir una sesión, en una sola llamada y sin escribir nada.

Uso: abrir.py <raiz> [<area>/<proyecto>] [--cuenta <correo>] [--plugin "<primera línea del metodo.md del plugin>"] [--sin-fechas [--listado <archivo>] [--outputs <archivo>]] [--minima] [--origen "<ruta de la raíz en la computadora>"]

Con --origen (la ruta de la raíz que da get_device_info) y la cuenta del administrador principal, si la raíz vive en
Google Drive imprime en CUENTA la línea PERMISOS, para ofrecer la revisión de permisos al abrir (1.24.2).

Con --minima (la apertura mínima, la primera respuesta de cualquier conversación con la carpeta conectada) imprime solo
la primera línea de metodo.md con su veredicto, el nombre de la organización, la cuenta, una línea por proyecto de cada
área legible (de un área restringida, solo si es de la cuenta) y los archivos sueltos en «Claude outputs», con su fecha:
sin guia.md entero, sin premisas y sin proyecto activo aunque se pase uno. Lo suelto en «Claude outputs» sale en todos los
modos, al final, también al abrir un proyecto, porque la primera respuesta de la conversación lo dice siempre.

Sin proyecto imprime el nivel 0 (primera línea de metodo.md, guia.md, premisas vigentes) y la lista de proyectos de
cada área legible, para saber cuál se abre. Con proyecto añade el nivel 1 (el bloque Proyectos de su área, proyecto.md
con sus diez primeros siguientes pasos y la cuenta del resto, las cinco decisiones y las tres sesiones más recientes, las
cabeceras de entregables/), el INVENTARIO de lo que no imprimió (cuántas entradas tienen los registros y cuánto pesan con
sus archivados, las notas de taller/ y los informes de revisión con su tamaño y las cinco notas más recientes por su
cabecera, las filas de fuentes/inventario.md: 1.26.3) y los avisos de apertura: cuestionamientos abiertos, decisiones de
otros proyectos que lo nombran en «Afecta a:», entregables desfasados o en borrador viejo, trabajo sin sesión, decisiones
escritas después de la última entrada de la bitácora (1.26.4: una sesión que no se cerró), notas de
taller que nada del proyecto cita (1.26.3) y la fecha de base/contexto.md. Con --cuenta dice qué áreas son de esa cuenta y,
si es la del responsable de contexto, también los cuestionamientos a premisas. Con --plugin compara la versión y la
huella del metodo.md de la raíz con las del plugin, en numérico («1.14.10» es mayor que «1.14.9»), y dice el veredicto:
RAIZ ATRASADA (se copia el del plugin), AL DIA, PLUGIN ATRASADO (no se copia nada y se avisa) o MISMA VERSION, HUELLA
DISTINTA (no se toca). La comparación la hace el script, no quien lo lee.

Nunca abre taller/, fuentes/, restringido/ ni base/ (salvo premisas.md y la cabecera de contexto.md; de taller/ del
proyecto activo solo mira fechas, tamaños y cabeceras, y de fuentes/ fechas y las filas de su inventario), ni las sesiones de otros proyectos, ni los proyectos que no están en el índice de su
área (salvo el activo). De las demás decisiones solo mira las líneas «Afecta a:», «Cuestiona a:» y «Responde a:»
y la cabecera de su entrada. Lo restringido no sale salvo que el proyecto activo esté dentro, y lo que no se deja leer
se cuenta, sin suponer qué hay.

Con --sin-fechas corre sobre una copia en el contenedor (sesión sin consola: la copia la arma espejo.py y sus fechas de
archivo son las de la copia, no las de la computadora). No usa ninguna fecha de archivo: no da el aviso de trabajo sin sesión
por fechas, sino el instante desde el que hay que mirarlo en el listado de la computadora (device_list_dir, mtimeMs), y en
REGISTROS solo da el tamaño. Con --listado <archivo> (el resultado de device_list_dir recursivo de la carpeta del
proyecto, guardado tal cual en un archivo del contenedor) calcula él el aviso de trabajo sin sesión, con fecha y hora en la
zona de la organización, como en la computadora: nadie compara milisegundos a mano. Con --outputs <archivo> (el
device_list_dir recursivo de «Claude outputs», guardado igual) da lo suelto ahí con sus fechas, como con consola. Con
--sin-fechas y la raíz atrasada, deja el metodo.md del plugin en una carpeta nueva de salidas del contenedor y la RESPUESTA
dice con qué device_commit_files escribirlo: es lo único que escribe, y fuera de la raíz (1.24.9).

La apertura mínima corre siempre así, en el contenedor sobre una copia (1.24.9): en la computadora no se ejecuta nada
descargado, que el modo Auto de la app frena cuando la petición no tiene que ver con la memoria.
"""
import datetime, json, os, pathlib, re, sys, time

ESTE_PLUGIN = "1.26.11"   # la versión del plugin de este script: la pone release.sh, y con ella se compara la versión mínima de la raíz (1.26)


def copia_del_metodo(plugin_linea, version):
    """El metodo.md del plugin con el que corre este script, copiado a una carpeta de salidas del contenedor para
    device_commit_files (1.24.9). Solo si su primera línea es la de --plugin; si no, None. Un nombre por versión, reutilizado:
    cada conversación con la raíz atrasada no deja otra copia de 137 KB."""
    fuente = pathlib.Path(__file__).resolve().parents[2] / "metodo.md"
    try:
        texto = fuente.read_text(encoding="utf-8")
    except OSError:
        return None
    if not plugin_linea or plugin_linea not in texto[:400]:
        return None
    # MEMORIA_SALIDAS solo lo usan las pruebas, donde no existen las carpetas de salidas del contenedor
    base = next((pathlib.Path(b) for b in (os.environ.get("MEMORIA_SALIDAS") or "", "/mnt/project-files", "/mnt/user-data/outputs") if b and pathlib.Path(b).is_dir()), None)
    if base is None:
        return None
    destino = base / f"metodo-{version or 'plugin'}" / "metodo.md"
    try:
        if not (destino.is_file() and destino.read_text(encoding="utf-8") == texto):
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(texto, encoding="utf-8")
    except OSError:
        return None
    return str(destino)


if len(sys.argv) > 1 and sys.argv[1] == "--metodo-para-subir":
    # la apertura completa con consola, cuando la raíz está atrasada y la mínima no lo puso al día (1.25.1): imprime la ruta de
    # la copia, lista para device_commit_files; nada, y sale con 1, si no cuadra
    _pl = sys.argv[sys.argv.index("--plugin") + 1].strip() if "--plugin" in sys.argv and sys.argv.index("--plugin") + 1 < len(sys.argv) else ""
    _m = re.search(r"versi[oó]n\s+(\d+(?:\.\d+)*)", _pl)
    _d = copia_del_metodo(_pl, _m.group(1) if _m else None)
    if _d:
        print(_d)
    sys.exit(0 if _d else 1)

RAIZ = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
RAIZ_RESUELTA = False
if RAIZ is not None and not (RAIZ / "guia.md").is_file():
    # la ruta que da get_device_info (/Users/…/Carpeta) no existe en esta consola, donde la carpeta cuelga de $HOME/mnt con
    # su último tramo como nombre (o «<padre>--<tramo>» si otra carpeta conectada se llama igual): se resuelve aquí para que un error de ruta no cueste dos llamadas más
    _mnt = pathlib.Path(os.path.expanduser("~")) / "mnt"
    _raices = [d for d in (sorted(_mnt.glob("*")) if _mnt.is_dir() else []) if (d / "guia.md").is_file() and (d / "metodo.md").is_file()]
    _cand = [d for d in _raices if d.name == RAIZ.name or d.name.endswith("--" + RAIZ.name)] or (_raices if len(_raices) == 1 else [])
    if _cand:
        sys.argv[1] = str(_cand[0]); RAIZ = _cand[0]; RAIZ_RESUELTA = True
    elif len(_raices) > 1:
        sys.exit("Esa ruta no existe en esta consola y hay varias raíces bajo $HOME/mnt: " + ", ".join(d.name for d in _raices) + ". Pasa la de $HOME/mnt/<nombre>.")
if RAIZ is not None and not (RAIZ / "guia.md").is_file() and len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
    # lo que la apertura necesita saber, en una línea que se reconoce (1.24.8): la conversación no tiene que comprobar antes
    # si la carpeta es una raíz ni si la consola la ve
    _mnt = pathlib.Path(os.path.expanduser("~")) / "mnt"
    _monta = _mnt.is_dir() and any(d.name == RAIZ.name or d.name.endswith("--" + RAIZ.name) for d in _mnt.glob("*"))
    if _monta or RAIZ.is_dir():
        print(f"NO ES RAIZ: {RAIZ.name} no tiene guia.md y metodo.md en su primer nivel. No es una memoria: no se dice nada de esto.")
    else:
        print(f"SIN CONSOLA: esta consola no ve {RAIZ.name}. Si la carpeta es una memoria, se trabaja como dice el anexo sin-consola-sesion.md de la skill sesion; "
              "se sabe trayendo guia.md y metodo.md con device_stage_files.")
    sys.exit(0)
if RAIZ is None or not (RAIZ / "guia.md").is_file():
    sys.exit("Uso: abrir.py <raiz> [<area>/<proyecto>] [--cuenta <correo>] [--plugin \"<primera línea del metodo.md del plugin>\"] [--sin-fechas [--listado <archivo>]] [--minima] [--origen \"<ruta de la raíz en la computadora>\"]  (la raíz es la carpeta con guia.md y metodo.md: en esta consola, la de $HOME/mnt/ que se llama como el último tramo de la ruta que da get_device_info, o «<padre>--<tramo>»)")
args = [a for a in sys.argv[2:]]
CUENTA = None
if "--cuenta" in args:
    i = args.index("--cuenta"); CUENTA = (args[i + 1] if i + 1 < len(args) else "").strip().lower(); del args[i:i + 2]
PLUGIN = None
if "--plugin" in args:
    i = args.index("--plugin"); PLUGIN = (args[i + 1] if i + 1 < len(args) else "").strip(); del args[i:i + 2]
MINIMA = "--minima" in args
if MINIMA:
    args.remove("--minima")
SIN_FECHAS = "--sin-fechas" in args
if SIN_FECHAS:
    args.remove("--sin-fechas")
ORIGEN = None
if "--origen" in args:
    i = args.index("--origen"); ORIGEN = (args[i + 1] if i + 1 < len(args) else "").strip(); del args[i:i + 2]
OUTPUTS, OUTPUTS_CORTADO = None, [False]
if "--outputs" in args:
    # el device_list_dir recursivo de «Claude outputs» guardado tal cual: sin consola, la copia no trae esa carpeta (1.24.9)
    i = args.index("--outputs"); OUTPUTS = args[i + 1] if i + 1 < len(args) else None; del args[i:i + 2]
LISTADO = None
if "--listado" in args:
    i = args.index("--listado"); LISTADO = args[i + 1] if i + 1 < len(args) else None; del args[i:i + 2]
ACTIVO = args[0].strip("/") if args and not MINIMA else None
ZONA_AVISO = None
VEREDICTO, VERSION_RAIZ, VERSION_PLUGIN = None, None, None
PERMISOS = False
DECIR = []          # «aviso para decirlo» de CUENTA: una fila del recuadro cada uno (1.24.8)
_LEIDOS = {}


def en_drive(origen):
    """Si la ruta de la raíz en la computadora (la de get_device_info) es de Google Drive para escritorio: en Mac, bajo
    Library/CloudStorage/GoogleDrive-… o /Volumes/GoogleDrive; en Mac y Windows, con una carpeta «Google Drive», «My Drive»
    o su nombre en otro idioma, o la de las unidades compartidas («G:/Mi unidad/…» entra por ahí). Una letra de unidad sola
    no lo dice (D: puede ser un disco o un USB), ni una carpeta de iCloud, Dropbox, OneDrive o Box sin esos nombres."""
    o = (origen or "").replace("\\", "/")
    return bool(re.search(r"/Library/CloudStorage/GoogleDrive-|^/Volumes/GoogleDrive(/|$)|/Google Drive(/|$)|"
                          r"/(My Drive|Mi unidad|Meu Drive|Mon Drive|Meine Ablage|Il mio Drive|Mijn Drive|"
                          r"Shared drives|Unidades compartidas|Drives partilhados|Drives partagés|Geteilte Ablagen|Drive condivisi)(/|$)", o, re.I))


def zona_horaria(raiz, defecto="America/Mexico_City"):
    """La zona de la organización: la línea «Zona horaria: Europe/Madrid» de guia.md (con viñeta, negrita o comillas
    invertidas, y UTC o Etc/GMT+5), si la hay; si no, Ciudad de México. Una zona que no vale se avisa en ZONA_AVISO."""
    global ZONA_AVISO
    try:
        _g = (raiz / "guia.md").read_bytes().decode("utf-8-sig", errors="replace").replace("\r\n", "\n")
        _LEIDOS[str(raiz / "guia.md")] = _g      # la misma lectura que después hace leer(): guia.md se lee una vez
        m = re.search(r"^\s*[-*]?\s*\**\s*zona horaria\s*\**\s*:\s*\**\s*`?\s*([A-Za-z0-9_+-]+(?:/[A-Za-z0-9_+-]+){0,2})", _g, re.M | re.I)
    except OSError:
        m = None
    try:
        from zoneinfo import ZoneInfo
    except Exception:
        return None
    if m and not m.group(1).startswith("["):
        try:
            return ZoneInfo(m.group(1))
        except Exception:
            ZONA_AVISO = f"la zona horaria «{m.group(1)}» de guia.md no es una zona válida (por ejemplo America/Mexico_City o Europe/Madrid); se usa {defecto}"
    try:
        return ZoneInfo(defecto)
    except Exception:
        return None
TZ = zona_horaria(pathlib.Path(sys.argv[1]))
HOY = datetime.datetime.now(TZ).date()
FECHA = re.compile(r"\b(20\d\d-\d\d-\d\d)\b")


def fecha_ok(f):
    try:
        datetime.date.fromisoformat(f); return True
    except (TypeError, ValueError):
        return False
no_legibles = []


def leer(p):
    """El texto de p, una sola vez por apertura: guia.md, los area.md y decisiones.md se piden en varios pasos, y en una
    carpeta de Drive cada lectura es una descarga (1.22.2). Lo que no se deja leer se cuenta, sin suponer qué hay."""
    k = str(p)
    if k not in _LEIDOS:
        try:
            _LEIDOS[k] = pathlib.Path(p).read_bytes().decode("utf-8-sig", errors="replace").replace("\r\n", "\n")
        except FileNotFoundError:
            _LEIDOS[k] = None
        except OSError:
            no_legibles.append(rel(p))   # sin permiso o sin descargar
            _LEIDOS[k] = None
    return _LEIDOS[k]


def rel(p):
    try:
        return pathlib.Path(p).relative_to(RAIZ).as_posix()
    except ValueError:
        return str(p)


def cabecera(texto):
    m = re.match(r"^---\n(.*?)\n---\n?", texto or "", re.S)
    fm, ultima = {}, None
    if not m:
        return fm, texto or ""
    for l in m.group(1).split("\n"):
        mm = re.match(r"^(\w+):\s*(.*)$", l)
        if mm:
            ultima = mm.group(1); v = mm.group(2).strip()
            fm[ultima] = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()] if v.startswith("[") and v.endswith("]") else v.strip("'\"")
        elif ultima and re.match(r"^\s+-\s+", l):
            if not isinstance(fm.get(ultima), list):
                fm[ultima] = []
            fm[ultima].append(re.sub(r"^\s+-\s+", "", l).strip().strip("'\""))
    return fm, texto[m.end():]


def seccion(texto, nombre):
    m = re.search(r"^## " + re.escape(nombre) + r"\s*\n(.*?)(?=^## |\Z)", texto or "", re.S | re.M)
    return m.group(1).strip() if m else ""


def entradas(texto):
    """Las entradas «## …» de un registro, en el orden del archivo, con su fecha."""
    out = []
    partes = re.split(r"^(?=## )", texto or "", flags=re.M)
    for p in partes:
        if not p.startswith("## "):
            continue
        cab = p.split("\n", 1)[0]
        f = FECHA.search(cab)
        fecha = f.group(1) if f and fecha_ok(f.group(1)) else ""   # una fecha inválida (2026-13-45) es como no tenerla
        out.append({"fecha": fecha, "cab": cab[3:].strip(), "texto": p.rstrip()})
    return out


def recientes(texto, n):
    es = entradas(texto)
    return sorted(es, key=lambda e: e["fecha"], reverse=True)[:n]   # sin fecha válida, al final




def hora_de(p):
    """«HH:MM» de la modificación de p en la zona de la organización, o «»."""
    try:
        return "" if SIN_FECHAS else datetime.datetime.fromtimestamp(os.stat(p).st_mtime, TZ).strftime("%H:%M")
    except OSError:
        return ""


def mtime(p):
    if SIN_FECHAS:   # en la copia, la fecha de archivo es la de la copia: no dice nada
        return None
    try:
        return datetime.datetime.fromtimestamp(os.stat(p).st_mtime, TZ).date()   # el día en la zona de la organización, como el tablero
    except OSError:
        return None


def titulo(n):
    print(f"\n=== {n}")


def tam(p):
    try:
        return pathlib.Path(p).stat().st_size
    except OSError:
        return 0


def kb(b):
    return f"{b / 1000:.0f} KB" if b >= 1000 else f"{b} bytes"


def cabeza_de(p):
    """El principio de un .md, sin leer su cuerpo: los primeros 16 KB bastan para cualquier cabecera. Lo que no se deja leer
    se cuenta, como en leer()."""
    try:
        with open(p, "rb") as f:
            return f.read(16384).decode("utf-8-sig", errors="replace").replace("\r\n", "\n")
    except OSError:
        no_legibles.append(rel(p))
        return ""


PASOS_IMPRESOS = 10   # «Siguientes pasos» que imprime la apertura; el resto se cuenta (1.26.3)


def con_pasos_recortados(texto, n=PASOS_IMPRESOS):
    """proyecto.md para imprimir, con «Siguientes pasos» en sus n primeros pasos y una línea que cuenta el resto. Solo
    cambia lo que se imprime: el archivo no se toca. Un paso es una viñeta o un número al principio de la línea; lo
    sangrado debajo va con su paso."""
    m = re.search(r"^## Siguientes pasos[ \t]*\n(.*?)(?=^## |\Z)", texto, re.S | re.M)
    if not m:
        return texto
    lineas = m.group(1).split("\n")
    pasos = [i for i, l in enumerate(lineas) if re.match(r"^(?:[-*+]|\d+[.)])\s", l)]
    if len(pasos) <= n:
        return texto
    cuerpo = "\n".join(lineas[:pasos[n]]).rstrip("\n")
    k = len(pasos) - n
    # texto que no es un paso ni va sangrado debajo de uno (un párrafo al final de la sección): se dice que queda
    suelto = any(l.strip() and not l[:1].isspace() and not re.match(r"^(?:[-*+]|\d+[.)])\s", l) for l in lineas[pasos[n]:])
    cuerpo += (f"\n- … y {k} {'paso' if k == 1 else 'pasos'} más en proyecto.md{', con texto debajo' if suelto else ''}, sin imprimir: "
               "se leen cuando la pregunta los pide, y enteros antes de revisar los pasos al cerrar.\n")
    return texto[:m.start(1)] + cuerpo + ("\n" if m.end(1) < len(texto) else "") + texto[m.end(1):]


# --- quién escribe: «Quién es quién» y la tabla de áreas de guia.md, y la línea «Colabora:» de un proyecto ---
# Desde el paso 0 de la versión alojada vive en un solo sitio, el paquete context_core (packages/context-core del repo),
# que packages/context-core/inline.py mete aquí, ya en el repo y comprobado con --check, para que el script siga corriendo
# descargado suelto: la misma copia en los ocho scripts que lo usan. Con ella vienen también la regla de lo restringido
# (la celda «Quién la lee» y la fila entera de la tabla de áreas, una sola para la sesión, el tablero, los permisos y la
# migración desde la 1.25.3), el primer párrafo de guia.md y los registros con sus archivados; se importa
# solo lo que este script usa. context_core/compat.py devuelve lo mismo que las copias de la 1.25.1
# (packages/context-core/tests/test_compat.py y test_access.py).
# --- context_core: generated by packages/context-core/inline.py from packages/context-core/context_core; do not edit by hand ---
def _context_core():
    import sys as _s, types as _t
    _fp = {
    'language': '9e900919e12e7a17d2eef48ac8da0f72ea4a20ed11a31f1268ea2dfcfaecad64',
    'records': '074bd7a0994a2cdf904cfa82827c7f26b226caff14317513a01d1a2af6a34def',
    'rules': '11b5a591b02632ccf7f2fd2df551f16305ee58245e86f15e847f357e241ade45',
    'compat': '2d7b357ba25bef9e78c5ab08b995b5bbe0f86c6a504bbb84bf1739e16c4a8dab',
    'minimum': '6f201e7a41557d8fa840f17df7d3d239dbd1c9b926b179488ac6cce399246630',
    'development': '8d66fbd49e6b19382cf0439bfe3df870e6a7300a4924bfac0df619d730f2c1bb',
    }
    _pkg, _todo = _s.modules.get("context_core"), list(_fp)
    if _pkg is not None:
        # already loaded (another script's region, or the installed package): only if it is this same code
        import hashlib as _h, importlib as _i
        _todo = []
        for _n in _fp:
            _m = _s.modules.get("context_core." + _n)
            if _m is None and getattr(_pkg, "__path__", None):
                _m = _i.import_module("context_core." + _n)
            if _m is None:
                _todo.append(_n); continue
            _got = getattr(_m, "__fingerprint__", None)
            if _got is None and getattr(_m, "__file__", None):
                with open(_m.__file__, encoding="utf-8") as _f:
                    _got = _h.sha256(_f.read().encode("utf-8")).hexdigest()
            if _got != _fp[_n]:
                raise ImportError("context_core." + _n + " is already loaded in this process from another version of the package"
                                  " than the one inlined in " + str(globals().get("__file__") or _s.argv[0]) + ": run each in its own process")
        if not _todo:
            return
    else:
        _pkg = _t.ModuleType("context_core"); _pkg.__path__ = []; _s.modules["context_core"] = _pkg
    _src = {
    'language': (
        '"""Language packs: how one language spells the method in the files.\n'
        '\n'
        'The record model has no language; a pack says how a root in that language names its reserved folders and files, its\n'
        'sections, the fields of its registers and the keys of its headers. A root has one language, chosen when it is set up and\n'
        "by default its owner's (decision of 2026-11-05: reserved names follow the root's language and existing roots keep their\n"
        'Spanish names). Spanish is the first and only complete pack; English comes with the language packs after area types.\n'
        '\n'
        'The words that decide what is restricted are here (review of 1.25.2, finding 9): the column names of the area table, the\n'
        'words of \xabAcceso\xbb and \xabQui\xe9n la lee\xbb, and the word that marks a project line, so a root in another language with its\n'
        'restricted area reads restricted. Not here yet, and still spelled inside `rules.py`: the fields of \xabQui\xe9n es qui\xe9n\xbb and\n'
        'the markers of the first paragraph of guia.md.\n'
        '"""\n'
        'from __future__ import annotations\n'
        '\n'
        'from dataclasses import dataclass, field\n'
        'from typing import Optional\n'
        '\n'
        '__all__ = ["Pack", "ES", "PACKS", "pack"]\n'
        '\n'
        '\n'
        '@dataclass(frozen=True)\n'
        'class Pack:\n'
        '    code: str\n'
        '    # reserved folders and files\n'
        '    guide: str\n'
        '    method: str\n'
        '    area_file: str\n'
        '    project_file: str\n'
        '    decisions_file: str\n'
        '    sessions_file: str\n'
        '    base: str\n'
        '    premises_file: str\n'
        '    deliverables: str\n'
        '    workshop: str\n'
        '    sources: str\n'
        '    restricted: str\n'
        '    # sections, as their \xab## \xbb heading\n'
        '    status: str\n'
        '    status_legacy_project: tuple\n'
        '    status_legacy_area: tuple\n'
        '    priorities_legacy: str\n'
        '    steps: str\n'
        '    who: str\n'
        '    objective: str\n'
        '    done_means: str\n'
        '    scope: str\n'
        '    what: str\n'
        '    projects: str\n'
        '    areas: str\n'
        '    # the lines of \xabQui\xe9n participa\xbb and of guia.md\n'
        '    responsible_labels: tuple\n'
        '    consumers_label: str\n'
        '    context_owner_label: str\n'
        '    administrator_label: str\n'
        '    # what decides restricted (rules.area_is_restricted, rules.is_restricted_cell, rules.starts_restricted), as regular\n'
        '    # expressions matched case-insensitively. Area table columns: lowercase header text without \xab*_`\xbb, as written\n'
        '    area_columns: dict            # responsible, account, readers, access, what -> tuple of header names\n'
        '    people_columns: dict          # responsible, account, collaborates -> tuple of header names, as heading_key() leaves them\n'
        '    restricted_lead: str          # the word at the start of \xabAcceso\xbb or \xabQui\xe9n la lee\xbb that makes the area restricted\n'
        '    open_lead: str                # the word at the start of \xabAcceso\xbb that makes it open\n'
        '    restricted_inline: str        # the same word on its own elsewhere in \xabQui\xe9n la lee\xbb (\xabDirecci\xf3n (restringida)\xbb)\n'
        '    restricted_stem: str          # what a negation must precede to cancel restricted_inline\n'
        '    restricted_negations: tuple   # \xabnunca restringida\xbb, \xabantes restringida\xbb\n'
        "    restricted_line: str          # the word at the start of a project's index line (after its name) that makes it restricted\n"
        '    # Estatus bullets, as heading_key() leaves them\n'
        '    status_fields: dict = field(default_factory=dict)\n'
        '    finished_marker: str = ""\n'
        '    # decisiones.md: (lowercase prefix, record field)\n'
        '    decision_fields: tuple = ()\n'
        '    pending_confirmation: str = ""\n'
        '    challenge_title: str = ""\n'
        '    # sesiones.md\n'
        '    session_wrote: tuple = ()\n'
        '    session_published: tuple = ()\n'
        '    session_topic: tuple = ()\n'
        '    session_progress: tuple = ()\n'
        '    session_pending: tuple = ()\n'
        '    session_by: tuple = ()\n'
        '    # header keys\n'
        '    key_state: str = ""\n'
        '    key_updated: str = ""\n'
        '    key_based_on: str = ""\n'
        '    key_replaced_by: str = ""\n'
        '    key_contribution: tuple = ()\n'
        '    # how a writer spells what it writes (context_core.write): one canonical form per field, where reading accepts several\n'
        '    write_session: dict = field(default_factory=dict)     # topic, progress, wrote, published, by\n'
        '    write_decision: dict = field(default_factory=dict)    # decided_by, raised_by, why, discarded, challenges, responds_to, replaces, affects\n'
        '    write_status: dict = field(default_factory=dict)      # completed, next, to_decide, concern\n'
        '    writers: dict = field(default_factory=dict)           # plugin, server: the word before the version in \xabSesi\xf3n de\xbb\n'
        '    # guia.md: the section that declares the oldest plugin that may write in the root (1.26)\n'
        '    minimum_plugin: str = ""\n'
        '    # sesiones.md entries that are not sessions: \xab## AAAA-MM-DD (tarea)\xbb and the like. They tell what happened, and no\n'
        '    # reader counts them as a session (escribir.md, section 8). The last one is the maintenance trace (1.26.8), whose\n'
        '    # entry names what it fixed, the instant of the last real close and its own\n'
        '    non_session_tags: tuple = ()\n'
        '    maintenance_tag: str = ""\n'
        '    session_fixed: tuple = ()\n'
        '    session_last_close: tuple = ()                       # \xab\xdaltimo cierre:\xbb, the instant of the last real close\n'
        '    session_written: tuple = ()                          # \xabEscrita:\xbb, the instant the maintenance entry was written\n'
        '\n'
        '\n'
        'ES = Pack(\n'
        '    code="es",\n'
        '    guide="guia.md", method="metodo.md", area_file="area.md", project_file="proyecto.md",\n'
        '    decisions_file="decisiones.md", sessions_file="sesiones.md", base="base", premises_file="premisas.md",\n'
        '    deliverables="entregables", workshop="taller", sources="fuentes", restricted="restringido",\n'
        '    status="Estatus", status_legacy_project=("Estado actual", "En corto"), status_legacy_area=("Panorama",),\n'
        '    priorities_legacy="Prioridades ahora", steps="Siguientes pasos", who="Qui\xe9n participa", objective="Objetivo",\n'
        '    done_means="Terminado significa", scope="Alcance", what="Qu\xe9 es", projects="Proyectos", areas="\xc1reas",\n'
        '    responsible_labels=("responsable", "due\xf1o", "dueno", "due\xf1a"), consumers_label="consumen esto",\n'
        '    context_owner_label="Contexto com\xfan", administrator_label=r"Administra la carpeta(?: compartida)?(?: y pone o quita los accesos)?",\n'
        '    area_columns={"responsible": ("responsable", "due\xf1o", "dueno"), "account": ("cuenta", "colabora"),\n'
        '                  "readers": ("qui\xe9n la lee", "quien la lee"), "access": ("acceso",), "what": ("qu\xe9 es", "que es")},\n'
        '    people_columns={"responsible": ("responsable", "dueno", "duena"), "account": ("cuenta", "cuentas"),\n'
        '                    "collaborates": ("colabora", "colaboran", "colaboradores", "colaboradoras")},\n'
        '    restricted_lead=r"restringid[oa]s?", open_lead=r"abiert[oa]s?", restricted_inline=r"restringidas?",\n'
        '    restricted_stem="restringid", restricted_negations=("nada", "no", "nunca", "sin", "antes"),\n'
        '    restricted_line=r"restringid[oa]",\n'
        '    status_fields={"se completo": "completed", "siguiente": "next", "falta decidir": "to_decide", "preocupa": "concern"},\n'
        '    finished_marker="Proyecto terminado el",\n'
        '    decision_fields=(("decidi\xf3:", "decided_by"), ("decidio:", "decided_by"), ("por qu\xe9:", "why"), ("por que:", "why"),\n'
        '                     ("descartamos:", "discarded"), ("descartado:", "discarded"), ("afecta a:", "affects"),\n'
        '                     ("plante\xf3:", "raised_by"), ("planteo:", "raised_by"), ("cuestiona a:", "challenges"),\n'
        '                     ("responde a:", "responds_to"), ("reemplaza:", "replaces"), ("reemplaza a:", "replaces")),\n'
        '    pending_confirmation=r"\\(pendiente de confirma(r|ci\xf3n)\\)", challenge_title="cuestionamiento",\n'
        '    session_wrote=("escribi\xf3", "escribio"), session_published=("public\xf3", "publico"),\n'
        '    session_topic=("trabajamos en:", "tema:"), session_progress=("avances:",), session_pending=("pendiente:",),\n'
        '    session_by=("sesi\xf3n de:", "sesion de:"),\n'
        '    key_state="estado", key_updated="actualizado", key_based_on="basado_en", key_replaced_by="reemplazado_por",\n'
        '    key_contribution=("aportacion", "afirma"),\n'
        '    write_session={"topic": "Tema", "progress": "Avances", "wrote": "Escribi\xf3", "published": "Public\xf3", "by": "Sesi\xf3n de",\n'
        '                   "fixed": "Arregl\xf3", "last_close": "\xdaltimo cierre", "written": "Escrita"},\n'
        '    write_decision={"decided_by": "Decidi\xf3", "raised_by": "Plante\xf3", "why": "Por qu\xe9", "discarded": "Descartado",\n'
        '                    "challenges": "Cuestiona a", "responds_to": "Responde a", "replaces": "Reemplaza", "affects": "Afecta a"},\n'
        '    write_status={"completed": "Se complet\xf3", "next": "Siguiente", "to_decide": "Falta decidir", "concern": "Preocupa"},\n'
        '    writers={"plugin": "plugin", "server": "servidor"},\n'
        '    minimum_plugin="Versi\xf3n m\xednima del plugin",\n'
        '    non_session_tags=("tarea", "tablero", "migracion", "mantenimiento"), maintenance_tag="mantenimiento",\n'
        '    session_fixed=("arregl\xf3:", "arreglo:"), session_last_close=("\xfaltimo cierre:", "ultimo cierre:"), session_written=("escrita:",),\n'
        ')\n'
        '\n'
        'PACKS = {"es": ES}\n'
        '\n'
        '\n'
        'def pack(code: Optional[str]) -> Pack:\n'
        '    """The pack for a language code; Spanish when no code is given. A code with no pack is an error, not Spanish:\n'
        '    reading an English root with Spanish names would find nothing and look empty."""\n'
        '    c = (code or "es").lower()\n'
        '    if c not in PACKS:\n'
        '        raise ValueError(f"no language pack for {code!r} (have: {\', \'.join(sorted(PACKS))})")\n'
        '    return PACKS[c]\n'
    ),
    'records': (
        '"""The record model: what a Memoria root is made of, as types.\n'
        '\n'
        'Written down from what `generar_vista.py`, `abrir.py` and `cerrar.py` read today (hosted-stack.md, \xabTwo constraints to\n'
        'design in step 0\xbb). Every field says which file and which key or section it comes from, so a caller never needs the\n'
        'file to know what a record means. A record is what the method knows, not how a file spells it: the legacy spellings\n'
        '(1.21 \xabDue\xf1o\xbb, \xabEstado actual\xbb, \xabPrioridades ahora\xbb; 1.22 \xabCuenta\xbb column) land in the same fields as the current ones.\n'
        '\n'
        'Nothing here reads or writes: `parse` builds records from text and `load` from a root.\n'
        '"""\n'
        'from __future__ import annotations\n'
        '\n'
        'from dataclasses import dataclass, field\n'
        'from typing import Optional\n'
        '\n'
        '__all__ = [\n'
        '    "Person", "PeopleRegistry", "AreaRow", "Premise", "Status", "DecisionRef", "Decision", "SessionEntry", "Step",\n'
        '    "Deliverable", "WorkshopFile", "IndexEntry", "Project", "Area", "Root",\n'
        ']\n'
        '\n'
        '\n'
        '# \u2500\u2500 people \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        '@dataclass\n'
        'class Person:\n'
        '    """One line of \xabQui\xe9n es qui\xe9n\xbb in guia.md (1.25): \xab- Name \xb7 account \xb7 field \xb7 field\xbb."""\n'
        '    name: str                                   # "?" for an account that has no name yet\n'
        '    accounts: set[str] = field(default_factory=set)        # Claude accounts (a bare email, or \xabcuentas: a@, b@\xbb)\n'
        '    drive_accounts: set[str] = field(default_factory=set)  # \xaben Drive: x@\xbb\n'
        '    no_account: bool = False                    # \xabsin cuenta\xbb\n'
        '    unconfirmed: bool = False                   # \xabsin confirmar\xbb\n'
        '    aliases: list[str] = field(default_factory=list)       # \xabtambi\xe9n: Other Spelling\xbb\n'
        '    organization: str = ""                      # \xabde: Organization\xbb\n'
        '    left_on: str = ""                           # \xabbaja AAAA-MM-DD\xbb ("s\xed" when the date is missing); a person who left does not write\n'
        '    shared_with: str = ""                       # \xabcompartida con: Name\xbb\n'
        '    registered_by: str = ""                     # \xabregistra: Name\xbb\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class PeopleRegistry:\n'
        '    """\xabQui\xe9n es qui\xe9n\xbb. A name or an account on two lines belongs to nobody: it is dropped from the lookups."""\n'
        '    declared: bool = False                      # the section exists (roots before 1.25 have accounts in the area table)\n'
        '    people: list[Person] = field(default_factory=list)\n'
        '    by_name: dict[str, Person] = field(default_factory=dict)     # key: parse.name_key(name)\n'
        '    by_account: dict[str, Person] = field(default_factory=dict)  # key: lowercased email\n'
        '    warnings: list[str] = field(default_factory=list)\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class AreaRow:\n'
        '    """One row of the \xab\xc1reas\xbb table of guia.md: who answers for the area and who reads it."""\n'
        '    slug: str                                   # folder name, without the slash\n'
        '    what: str                                   # \xabQu\xe9 es\xbb\n'
        '    responsible: str                            # \xabResponsable\xbb (1.22+) or \xabDue\xf1o\xbb (1.21), as written\n'
        '    responsible_accounts: set[str] = field(default_factory=set)   # 1.21/1.22: the email before \xabcolabora:\xbb; 1.25: from the registry\n'
        '    collaborators: list[str] = field(default_factory=list)        # 1.25 \xabColabora\xbb names; earlier, emails after \xabcolabora:\xbb\n'
        '    collaborator_accounts: set[str] = field(default_factory=set)\n'
        '    readers: str = ""                           # \xabQui\xe9n la lee\xbb, as written\n'
        '    access: str = ""                            # \xabAcceso\xbb (1.22+): \xabAbierta\xbb / \xabRestringida\xbb; empty before 1.22\n'
        "    restricted: bool = False                    # decided by the method's rule, fail closed (parse.area_is_restricted)\n"
        '    warnings: list[str] = field(default_factory=list)\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Premise:\n'
        '    """One line of base/premisas.md: \xab- P1 \xb7 text \xb7 Confirm\xf3: Name \xb7 AAAA-MM-DD \xb7 Reemplaza P0\xbb."""\n'
        '    id: str                                     # "P1"\n'
        '    text: str\n'
        '    line: str                                   # the whole line, as the opening prints it\n'
        '    confirmed_by: str = ""\n'
        '    date: str = ""\n'
        '    replaces: Optional[str] = None\n'
        '\n'
        '\n'
        '# \u2500\u2500 project parts \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        '@dataclass\n'
        'class Status:\n'
        '    """The \xabEstatus\xbb section of proyecto.md or area.md (1.22+), or what stands for it in older roots.\n'
        '\n'
        '    Current form:  \xabAAAA-MM-DD \xb7 **headline**\xbb then bullets \xabSe complet\xf3:\xbb, \xabSiguiente:\xbb, \xabFalta decidir:\xbb, \xabPreocupa:\xbb.\n'
        '    Legacy forms keep the whole text in `text` and leave the bullets empty: \xabEstado actual\xbb / \xabEn corto\xbb (projects,\n'
        '    1.21), \xabPanorama\xbb (areas, 1.21)."""\n'
        '    source: str                                 # the section it came from: "Estatus", "Estado actual", "En corto", "Panorama"\n'
        '    text: str                                   # the section as written\n'
        '    date: str = ""\n'
        '    headline: str = ""\n'
        '    completed: str = ""                         # \xabSe complet\xf3\xbb\n'
        '    next: list[str] = field(default_factory=list)   # \xabSiguiente\xbb, with its sub-bullets; for an area these are its priorities\n'
        '    to_decide: str = ""                         # \xabFalta decidir\xbb\n'
        '    concern: str = ""                           # \xabPreocupa\xbb\n'
        '    finished_on: str = ""                       # \xabProyecto terminado el AAAA-MM-DD\xbb: the project is closed\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class DecisionRef:\n'
        '    """A pointer to a decision or a premise, as \xabResponde a\xbb, \xabCuestiona a\xbb and \xabReemplaza\xbb write it."""\n'
        '    project: Optional[str]                      # "area--project", "premisa", or None when the text names no identifier\n'
        '    id: Optional[str]                           # "2026-10-15-2", "P3"\n'
        '    text: str                                   # as written\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Decision:\n'
        '    """One entry of decisiones.md: \xab## AAAA-MM-DD \xb7 title\xbb and its fields. Entries are never edited once written."""\n'
        '    id: str                                     # the date, plus -2, -3\u2026 counting from the oldest entry of that day; "" without a valid date\n'
        '    date: str\n'
        '    title: str\n'
        '    decided_by: str = ""                        # \xabDecidi\xf3\xbb\n'
        '    why: str = ""                               # \xabPor qu\xe9\xbb\n'
        '    discarded: str = ""                         # \xabDescartado\xbb / \xabDescartamos\xbb\n'
        '    affects: str = ""                           # \xabAfecta a\xbb, as written (paths and projects separated by \xab\xb7\xbb)\n'
        '    raised_by: str = ""                         # \xabPlante\xf3\xbb (challenges)\n'
        '    challenges: Optional[DecisionRef] = None    # \xabCuestiona a\xbb\n'
        '    responds_to: Optional[DecisionRef] = None   # \xabResponde a\xbb\n'
        '    replaces: Optional[DecisionRef] = None      # \xabReemplaza\xbb\n'
        '    pending_confirmation: bool = False          # \xabDecidi\xf3: Name (pendiente de confirmar)\xbb\n'
        '    kind: str = "decision"                      # "decision" or "challenge" (a \xabCuestiona a\xbb or a title \xabCuestionamiento: \u2026\xbb)\n'
        '    archived: bool = False                      # it comes from decisiones-AAAA.md, not the live file\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class SessionEntry:\n'
        '    """One entry of sesiones.md: \xab## AAAA-MM-DD\xbb and its fields."""\n'
        '    n: int                                      # position counting from the oldest entry: stable when entries are added on top\n'
        '    date: str\n'
        '    title: str                                  # the heading as written (sessions of the same day share it)\n'
        '    topic: str = ""                             # \xabTema\xbb / \xabTrabajamos en\xbb\n'
        '    progress: str = ""                          # \xabAvances\xbb\n'
        '    pending: str = ""                           # \xabPendiente\xbb (older roots)\n'
        '    by: str = ""                                # \xabSesi\xf3n de\xbb, without the plugin version\n'
        '    plugin_version: str = ""                    # \xab\xb7 plugin 1.25.1\xbb\n'
        '    server_version: str = ""                    # \xab\xb7 servidor 0.0.2\xbb: the entry was written by the hosted server\n'
        '    wrote: list[str] = field(default_factory=list)       # \xabEscribi\xf3\xbb, paths inside the project (restricted ones dropped)\n'
        '    published: list[str] = field(default_factory=list)   # \xabPublic\xf3\xbb\n'
        '    archived: bool = False\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Step:\n'
        '    """One bullet of \xabSiguientes pasos\xbb. The method writes owner and size in the text; the record keeps the text whole\n'
        '    and the dates it names, which is what the board and the close read."""\n'
        '    text: str\n'
        '    dates: list[str] = field(default_factory=list)\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Deliverable:\n'
        '    """A file in the project\'s entregables/. Its header for .md files; for other formats only the name and the area index."""\n'
        '    file: str                                   # "hosted-path.md"\n'
        '    name: str                                   # stem\n'
        '    format: str                                 # extension without the dot\n'
        '    title: Optional[str] = None                 # the H1\n'
        '    state: Optional[str] = None                 # \xabestado\xbb: borrador, vigente, reemplazado\u2026\n'
        '    updated: Optional[str] = None               # \xabactualizado\xbb, else the date of its line in the area index\n'
        '    based_on: list[str] = field(default_factory=list)     # \xabbasado_en\xbb, paths from the root\n'
        '    replaced_by: Optional[str] = None           # \xabreemplazado_por\xbb\n'
        '    contribution: Optional[str] = None          # \xabaportacion\xbb (1.22+; \xabafirma\xbb before): one line on what it holds\n'
        '    description: str = ""                       # its line in the area\'s \xabProyectos\xbb index\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class WorkshopFile:\n'
        '    """A file in taller/. Workshop is never shown as current; the record holds only what the board lists."""\n'
        '    path: str                                   # relative to taller/\n'
        '    title: Optional[str] = None\n'
        '    updated: Optional[str] = None\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class IndexEntry:\n'
        '    """A project line of the \xabProyectos\xbb block of area.md, with its deliverable sub-lines."""\n'
        '    slug: str\n'
        '    description: str\n'
        '    restricted: bool = False                    # the description starts with \xabrestringido\xbb\n'
        '    deliverables: dict[str, dict] = field(default_factory=dict)   # stem -> {"description", "updated"}\n'
        '    notes: list[str] = field(default_factory=list)\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Project:\n'
        '    """A project folder: proyecto.md, decisiones.md, sesiones.md, entregables/, taller/, fuentes/, restringido/."""\n'
        '    area: str\n'
        '    slug: str\n'
        '    restricted: bool = False                    # restricted projects keep only their index line: nothing inside is read\n'
        '    state: Optional[str] = None                 # proyecto.md \xabestado\xbb\n'
        '    updated: Optional[str] = None               # proyecto.md \xabactualizado\xbb\n'
        '    title: str = ""\n'
        '    objective: str = ""                         # \xabObjetivo\xbb\n'
        '    done_means: str = ""                        # \xabTerminado significa\xbb (older roots)\n'
        '    scope: str = ""                             # \xabAlcance\xbb\n'
        '    status: Optional[Status] = None\n'
        '    steps: list[Step] = field(default_factory=list)       # \xabSiguientes pasos\xbb\n'
        '    responsible: str = ""                       # \xabQui\xe9n participa\xbb: \xabResponsable:\xbb (1.22+) or \xabDue\xf1o:\xbb (1.21)\n'
        '    collaborators: list[str] = field(default_factory=list)   # \xabColabora:\xbb names (1.25) or \xabName (email)\xbb (1.22)\n'
        '    consumers: str = ""                         # \xabConsumen esto:\xbb (older roots)\n'
        '    decisions: list[Decision] = field(default_factory=list)  # newest first\n'
        '    sessions: list[SessionEntry] = field(default_factory=list)  # newest first\n'
        '    deliverables: list[Deliverable] = field(default_factory=list)\n'
        '    workshop: list[WorkshopFile] = field(default_factory=list)\n'
        '    index: Optional[IndexEntry] = None          # its line in area.md, if any\n'
        '    old_responses: list[DecisionRef] = field(default_factory=list)  # \xabResponde a\xbb of decision archives older than last year, not read whole\n'
        '    loaded: frozenset = frozenset()             # which parts load_project read (load.PARTS); empty: only its index line\n'
        '\n'
        '    @property\n'
        '    def key(self) -> str:\n'
        '        """The identifier the board and the queue use: "area--project"."""\n'
        '        return f"{self.area}--{self.slug}"\n'
        '\n'
        '    @property\n'
        '    def closed(self) -> bool:\n'
        '        return bool(self.status and self.status.finished_on)\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Area:\n'
        '    """An area folder: area.md and its projects."""\n'
        '    slug: str\n'
        '    row: Optional[AreaRow] = None               # its row in guia.md; None for a folder the table does not name\n'
        '    restricted: bool = False\n'
        '    state: Optional[str] = None\n'
        '    updated: Optional[str] = None\n'
        '    title: str = ""\n'
        '    what: str = ""                              # \xabQu\xe9 es\xbb\n'
        '    status: Optional[Status] = None             # \xabEstatus\xbb (1.22+) or \xabPanorama\xbb\n'
        '    priorities: list[str] = field(default_factory=list)   # \xabSiguiente\xbb of the Estatus, or \xabPrioridades ahora\xbb (1.21)\n'
        '    responsible: str = ""                       # \xabQui\xe9n participa\xbb of area.md\n'
        '    index: dict[str, IndexEntry] = field(default_factory=dict)\n'
        '    projects: list[Project] = field(default_factory=list)\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Root:\n'
        '    """A whole root: the folder with guia.md and metodo.md at its first level."""\n'
        '    name: str\n'
        '    organization: str = ""                      # what goes before \xab\xb7\xbb in the H1 of guia.md\n'
        '    method_line: str = ""                       # first line of metodo.md: version and fingerprint\n'
        '    method_version: Optional[tuple[int, ...]] = None\n'
        '    method_fingerprint: Optional[str] = None\n'
        '    language: str = "es"                        # the root\'s language pack (language.py)\n'
        '    timezone: str = "America/Mexico_City"       # \xabZona horaria:\xbb of guia.md\n'
        '    context_owner: str = ""                     # \xabContexto com\xfan:\xbb (who answers for guia.md and base/)\n'
        '    administrator: str = ""                     # \xabAdministra la carpeta:\xbb\n'
        '    people: PeopleRegistry = field(default_factory=PeopleRegistry)\n'
        '    area_rows: list[AreaRow] = field(default_factory=list)\n'
        '    areas: list[Area] = field(default_factory=list)\n'
        '    premises: list[Premise] = field(default_factory=list)\n'
        '    warnings: list[str] = field(default_factory=list)\n'
        '\n'
        '    def area(self, slug: str) -> Optional[Area]:\n'
        '        return next((a for a in self.areas if a.slug == slug), None)\n'
        '\n'
        '    def project(self, key: str) -> Optional[Project]:\n'
        '        """By "area/project" or "area--project"."""\n'
        '        a, _, p = key.replace("--", "/").partition("/")\n'
        '        ar = self.area(a)\n'
        '        return next((x for x in ar.projects if x.slug == p), None) if ar else None\n'
        '\n'
        '    @property\n'
        '    def current_premises(self) -> list[Premise]:\n'
        '        replaced = {p.replaces for p in self.premises if p.replaces}\n'
        '        return [p for p in self.premises if p.id not in replaced]\n'
    ),
    'rules': (
        '"""The rules the plugin scripts share: who writes (the people registry, the area table\'s accounts, \xabColabora:\xbb), what is\n'
        "restricted, guia.md's first paragraph and the archived registers. Pure functions: no I/O, no globals, no clock.\n"
        '\n'
        'This is what `compat` reaches, and so what `inline.py` puts inside the scripts; the parsers of the other method files are\n'
        'in `parse`, which imports these and re-exports them. The words that decide restricted come from the language pack\n'
        '(review of 1.25.2, finding 9). `tests/test_compat.py` and `tests/test_access.py` compare these with the 1.25.1 rules\n'
        'frozen in `tests/reference/`.\n'
        '"""\n'
        'from __future__ import annotations\n'
        '\n'
        'import datetime\n'
        'import re\n'
        'import unicodedata\n'
        'from typing import Optional\n'
        '\n'
        'from .language import ES, Pack\n'
        'from .records import PeopleRegistry, Person\n'
        '\n'
        'EMAIL = re.compile(r"[\\w.+\'-]+@[\\w-]+(?:\\.[\\w-]+)*")\n'
        '_WORD_COLLABORATES = re.compile(r"\\bco-?labor\\w*\\s*:?", re.I)\n'
        '_LINE_COLLABORATES = re.compile(r"^\\s*[-*]?\\s*\\**\\s*colabora[n]?\\s*\\**\\s*:", re.I)\n'
        '\n'
        '\n'
        '# \u2500\u2500 names \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'def name_key(n: str) -> str:\n'
        '    """How two names compare: NFC, lowercase, without bold, quotes or parentheses, spaces joined. An accent counts."""\n'
        '    n = unicodedata.normalize("NFC", n or "").replace("\xa0", " ")\n'
        '    n = re.sub(r"\\s*\\([^)]*\\)", "", re.sub(r"[*_`\xab\xbb\\"]", "", n))\n'
        '    return re.sub(r"\\s+", " ", n).strip(" .,;:").lower()\n'
        '\n'
        '\n'
        'def heading_key(t: str) -> str:\n'
        '    """A heading to compare: without accents (NFC or NFD), case or punctuation."""\n'
        '    t = "".join(c for c in unicodedata.normalize("NFD", t or "") if unicodedata.category(c) != "Mn")\n'
        '    return re.sub(r"\\s+", " ", re.sub(r"[^a-z ]", "", t.lower())).strip()\n'
        '\n'
        '\n'
        '# \u2500\u2500 restricted \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'def is_restricted_cell(cell: str, lang: Pack = ES) -> bool:\n'
        '    """\xabQui\xe9n la lee\xbb declares the area restricted: the word at the start (\xabRestringida: \u2026\xbb), or \xabrestringida\xbb on its\n'
        '    own elsewhere (\xabDirecci\xf3n (restringida)\xbb) and not negated (\xabnunca restringida\xbb, \xabantes restringida\xbb)."""\n'
        '    c = cell or ""\n'
        '    if re.match(r"^[\\W_]*" + lang.restricted_lead + r"\\b", c, re.I):\n'
        '        return True\n'
        '    return bool(re.search(r"\\b" + lang.restricted_inline + r"\\b", c, re.I)) and not re.search(\n'
        '        r"\\b(?:" + "|".join(lang.restricted_negations) + r")\\s+(?:[^\\s]+\\s+)?" + lang.restricted_stem, c, re.I)\n'
        '\n'
        '\n'
        'def starts_restricted(line: str, lang: Pack = ES) -> bool:\n'
        '    """An index line \xab- `x/` \u2014 restringido: \u2026\xbb marks the project restricted."""\n'
        '    return bool(re.match(r"^[\\W_]*" + lang.restricted_line + r"\\b", line or "", re.I))\n'
        '\n'
        '\n'
        'def access_word(cell: str, lang: Pack = ES) -> Optional[bool]:\n'
        '    """What an \xabAcceso\xbb cell says: True for \xabRestringida\xbb, False for \xabAbierta\xbb, None for anything else (empty, unclear)."""\n'
        '    if re.match(r"^[\\W_]*" + lang.restricted_lead + r"\\b", cell or "", re.I):\n'
        '        return True\n'
        '    if re.match(r"^[\\W_]*" + lang.open_lead + r"\\b", cell or "", re.I):\n'
        '        return False\n'
        '    return None\n'
        '\n'
        '\n'
        'def _area_columns(header: list[str], lang: Pack = ES) -> dict:\n'
        '    n = [re.sub(r"[*_`]", "", x).strip().lower() for x in header]\n'
        '    default = {"responsible": 2, "account": 3, "readers": 4, "access": None, "what": 1}\n'
        '    return {k: next((i for i, x in enumerate(n) if x in names), default[k]) for k, names in lang.area_columns.items()}\n'
        '\n'
        '\n'
        'def area_is_restricted(cells: list[str], header: list[str], lang: Pack = ES) -> bool:\n'
        '    """Whether an area row of guia.md is restricted: the one rule that the opening, the board, the permissions check and the\n'
        '    migration use (verificar.sh reads only the \xabAcceso\xbb word, with access_word) (review of 1.25.2, finding 10). With an \xabAcceso\xbb column (1.22+), its word; otherwise,\n'
        '    or when it is empty or unclear, restricted if the table has a \xabColabora\xbb column (1.25: \xabQui\xe9n la lee\xbb no longer\n'
        '    carries \xabRestringida:\xbb, so it fails closed), and else the \xabQui\xe9n la lee\xbb rule. Same as area_restringida() in the\n'
        '    1.25.1 abrir.py, frozen in tests/reference/acceso_1_25_1.py."""\n'
        '    col = _area_columns(header, lang)\n'
        '    if col["access"] is not None and col["access"] < len(cells):\n'
        '        word = access_word(cells[col["access"]], lang)\n'
        '        if word is not None:\n'
        '            return word\n'
        '    if _people_columns(header, lang)["collaborates"] is not None:\n'
        '        return True\n'
        '    return is_restricted_cell(cells[col["readers"]] if col["readers"] < len(cells) else "", lang)\n'
        '\n'
        '\n'
        '# \u2500\u2500 people \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'def people_registry(guia: str) -> PeopleRegistry:\n'
        '    """\xabQui\xe9n es qui\xe9n\xbb of guia.md. Same rules as registro_personas() in the scripts."""\n'
        '    lines, inside, declared = [], False, False\n'
        '    for l in unicodedata.normalize("NFC", guia or "").split("\\n"):\n'
        '        m = re.match(r"^\\s*#{2,3}\\s+(.*?)\\s*$", l)\n'
        '        if m:\n'
        '            inside = heading_key(m.group(1)) == "quien es quien"\n'
        '            declared = declared or inside\n'
        '        elif inside:\n'
        '            lines.append(l)\n'
        '    reg = PeopleRegistry(declared=declared)\n'
        '    two_names, two_accounts = set(), set()\n'
        '    for l in lines:\n'
        '        if not re.match(r"^\\s*[-*]\\s+\\S", l):\n'
        '            continue\n'
        '        fields = [c.strip() for c in re.split(r"\\s+\xb7\\s+", l.strip()[1:].strip()) if c.strip()]\n'
        '        if not fields:\n'
        '            continue\n'
        '        p = Person(name=re.sub(r"\\s*\\([^)]*\\)", "", re.sub(r"[*_`]", "", fields[0])).strip())\n'
        '        if EMAIL.fullmatch(p.name.lower()):\n'
        '            p.accounts.add(p.name.lower()); p.name = "?"\n'
        '        elif EMAIL.search(p.name):\n'
        '            reg.warnings.append(f"\xab{fields[0]}\xbb: el nombre y la cuenta van separados por \xab \xb7 \xbb")\n'
        '        for c in fields[1:]:\n'
        '            cl = c.lower()\n'
        '            if EMAIL.fullmatch(cl):\n'
        '                p.accounts.add(cl)\n'
        '            elif re.search(r"\\bbaja\\b", cl):\n'
        '                p.left_on = (re.search(r"20\\d\\d-\\d\\d-\\d\\d", c) or [""])[0] or "s\xed"\n'
        '            elif re.match(r"^cuentas?\\s*:", cl):\n'
        '                p.accounts |= set(EMAIL.findall(cl))\n'
        '            elif re.match(r"^(en\\s+)?(google\\s+)?drive\\s*:", cl):\n'
        '                p.drive_accounts |= set(EMAIL.findall(cl))\n'
        '            elif re.match(r"^sin\\s+cuenta\\b", cl):\n'
        '                p.no_account = True\n'
        '            elif re.match(r"^sin\\s+confirmar\\b", cl):\n'
        '                p.unconfirmed = True\n'
        '            elif re.match(r"^tambi[e\xe9]n\\s*:", cl):\n'
        '                p.aliases += [a.strip() for a in re.split(r"[,;]", c.split(":", 1)[1]) if a.strip()]\n'
        '            elif re.match(r"^de\\s*:", cl):\n'
        '                p.organization = c.split(":", 1)[1].strip()\n'
        '            elif re.match(r"^compartida\\s+con\\s*:", cl):\n'
        '                p.shared_with = c.split(":", 1)[1].strip()\n'
        '            elif re.match(r"^registra\\s*:", cl):\n'
        '                p.registered_by = c.split(":", 1)[1].strip()\n'
        '            else:\n'
        '                reg.warnings.append(f"\xab{p.name}\xbb: no se entiende \xab{c}\xbb (van un correo, \xabsin cuenta\xbb, \xaben Drive: correo\xbb, \xabtambi\xe9n: nombre\xbb, \xabde: organizaci\xf3n\xbb o \xabbaja AAAA-MM-DD\xbb)")\n'
        '        if p.no_account and p.accounts:\n'
        '            reg.warnings.append(f"\xab{p.name}\xbb dice \xabsin cuenta\xbb y lleva una cuenta: se queda la cuenta")\n'
        '            p.no_account = False\n'
        '        if not p.accounts and not p.no_account and not p.left_on:\n'
        '            reg.warnings.append(f"\xab{p.name}\xbb no lleva ni su cuenta ni \xabsin cuenta\xbb")\n'
        '        reg.people.append(p)\n'
        '        for n in ([p.name] if p.name != "?" else []) + p.aliases:\n'
        '            k = name_key(n)\n'
        '            if k in reg.by_name and reg.by_name[k] is not p:\n'
        '                two_names.add(k)\n'
        '                reg.warnings.append(f"\xab{n}\xbb est\xe1 dos veces: dos personas con el mismo nombre se distinguen con el segundo apellido o una inicial (mientras, ese nombre no es de nadie)")\n'
        '            reg.by_name.setdefault(k, p)\n'
        '        for c in p.accounts:\n'
        '            if c in reg.by_account and reg.by_account[c] is not p:\n'
        '                two_accounts.add(c)\n'
        '                reg.warnings.append(f"la cuenta {c} est\xe1 en dos l\xedneas (\xab{reg.by_account[c].name}\xbb y \xab{p.name}\xbb; mientras, no es de nadie)")\n'
        '            reg.by_account.setdefault(c, p)\n'
        '    for k in two_names:\n'
        '        reg.by_name.pop(k, None)\n'
        '    for c in two_accounts:\n'
        '        reg.by_account.pop(c, None)\n'
        '    return reg\n'
        '\n'
        '\n'
        'def find_person(name_or_account: str, reg: PeopleRegistry) -> Optional[Person]:\n'
        '    t = (name_or_account or "").strip()\n'
        '    if EMAIL.fullmatch(t.lower()):\n'
        '        return reg.by_account.get(t.lower())\n'
        '    return reg.by_name.get(name_key(t))\n'
        '\n'
        '\n'
        'def names_in(text: str, reg: Optional[PeopleRegistry] = None) -> list[str]:\n'
        '    """The names of a cell or line (\xabColabora: Ana Ruiz, Luis Mej\xeda\xbb), split by \xab,\xbb or \xab;\xbb, and by \xab y \xbb / \xab e \xbb only\n'
        '    when the whole piece is not a registered name."""\n'
        '    reg = reg or PeopleRegistry()\n'
        '    t = re.sub(r"^\\s*[-*]?\\s*\\**\\s*(?:colabora[n]?|lo leen?|responsable)\\s*\\**\\s*:\\s*\\**", "", text or "", flags=re.I)\n'
        '    t = re.sub(r"\\s*\\([^)]*\\)", "", t)\n'
        '    out: list[str] = []\n'
        '    for piece in re.split(r"[,;]", t):\n'
        '        piece = piece.strip(" .*")\n'
        '        if not piece or piece.lower() in ("\u2014", "-", "nadie", "ninguno", "ninguna"):\n'
        '            continue\n'
        '        if find_person(piece, reg) is not None or not re.search(r"\\s(?:y|e)\\s", piece):\n'
        '            out.append(piece)\n'
        '        else:\n'
        '            out += [x.strip(" .*") for x in re.split(r"\\s+(?:y|e)\\s+", piece) if x.strip(" .*")]\n'
        '    return out\n'
        '\n'
        '\n'
        'def accounts_of_names(text: str, reg: PeopleRegistry) -> tuple[set[str], list[str]]:\n'
        '    out, missing = set(), []\n'
        '    for n in names_in(text, reg):\n'
        '        p = find_person(n, reg)\n'
        '        if p is None:\n'
        '            missing.append(n)\n'
        '        elif not p.left_on:\n'
        '            out |= p.accounts\n'
        '    return out, missing\n'
        '\n'
        '\n'
        'def account_cell(cell: str) -> tuple[set[str], set[str], Optional[str]]:\n'
        '    """(responsible, collaborators, warning) of a \xabCuenta\xbb cell \xabresp@x \xb7 colabora: a@x, b@x\xbb (up to 1.24). Fails closed."""\n'
        '    text = (cell or "").lower()\n'
        '    parts = _WORD_COLLABORATES.split(text, maxsplit=1)\n'
        '    before = set(EMAIL.findall(parts[0]))\n'
        '    after = set(EMAIL.findall(parts[1])) if len(parts) > 1 else set()\n'
        '    warning = None\n'
        '    if len(before) > 1:\n'
        '        warning = "m\xe1s de un correo antes de \xabcolabora:\xbb; nadie es responsable hasta que se corrija"\n'
        '        before = set()\n'
        '    elif not before:\n'
        '        warning = "sin el correo del responsable"\n'
        '    elif len(parts) > 1 and not re.search(r"\\bcolabora\\s*:", text):\n'
        '        warning = "la palabra para quien colabora va escrita \xabcolabora:\xbb"\n'
        '    return before, after, warning\n'
        '\n'
        '\n'
        'def _people_columns(header: list[str], lang: Pack = ES) -> dict:\n'
        '    n = [heading_key(x) for x in header]\n'
        '    return {k: next((i for i, x in enumerate(n) if x in names), None) for k, names in lang.people_columns.items()}\n'
        '\n'
        '\n'
        'def row_accounts(header: list[str], cells: list[str], reg: PeopleRegistry) -> tuple[set[str], set[str], Optional[str]]:\n'
        '    """(responsible, collaborators, warning) of an area row: from the \xabCuenta\xbb emails up to 1.24, from the \xabColabora\xbb\n'
        '    names and the registry in 1.25. Same as fila_cuentas()."""\n'
        '    col = _people_columns(header)\n'
        '    cell = lambda i: cells[i] if i is not None and i < len(cells) else ""\n'
        '    if col["account"] is not None or col["collaborates"] is None:\n'
        '        return account_cell(cell(col["account"] if col["account"] is not None else 3))\n'
        '    if not reg.declared:\n'
        '        return set(), set(), "la tabla nombra a quien colabora por su nombre y guia.md no tiene \xabQui\xe9n es qui\xe9n\xbb"\n'
        '    resp = re.sub(r"\\s*\\((?=[a-z\xe1\xe9\xed\xf3\xfa\xf1`])[^)]*\\)", "", cell(col["responsible"] if col["responsible"] is not None else 2))\n'
        '    rn = names_in(resp, reg)\n'
        '    warnings, of = [], set()\n'
        '    if len(rn) > 1 and find_person(rn[0], reg) is not None:\n'
        '        warnings.append(f"en Responsable, lo que sigue a \xab{rn[0]}\xbb va en \xabQu\xe9 es\xbb")\n'
        '        rn = rn[:1]\n'
        '    if len(rn) != 1:\n'
        '        warnings.append("el responsable es una sola persona del registro" if rn else "sin responsable")\n'
        '    else:\n'
        '        p = find_person(rn[0], reg)\n'
        '        if p is None:\n'
        '            warnings.append(f"\xab{rn[0]}\xbb no est\xe1 en \xabQui\xe9n es qui\xe9n\xbb")\n'
        '        elif p.left_on:\n'
        '            warnings.append(f"\xab{p.name}\xbb est\xe1 de baja")\n'
        '        elif p.accounts:\n'
        '            of = set(p.accounts)\n'
        '        elif p.registered_by and find_person(p.registered_by, reg) and find_person(p.registered_by, reg).accounts:\n'
        '            of = set(find_person(p.registered_by, reg).accounts)\n'
        '        else:\n'
        '            warnings.append(f"\xab{p.name}\xbb no tiene cuenta: o la tiene, o su l\xednea dice \xabregistra: Nombre\xbb de quien escribe por ella")\n'
        '    co, missing = accounts_of_names(cell(col["collaborates"]), reg)\n'
        '    warnings += [f"\xab{n}\xbb (Colabora) no est\xe1 en \xabQui\xe9n es qui\xe9n\xbb" for n in missing]\n'
        '    return of, co - of, "; ".join(warnings) or None\n'
        '\n'
        '\n'
        'def provisional_people(who: str, reg: PeopleRegistry) -> list[tuple[str, str]]:\n'
        '    """[(name, email)] of \xabColabora: Name (email)\xbb for someone not in the registry: the provisional entry (1.25)."""\n'
        '    out: list[tuple[str, str]] = []\n'
        '    if not reg.declared:\n'
        '        return out\n'
        '    for l in (who or "").split("\\n"):\n'
        '        if _LINE_COLLABORATES.match(l):\n'
        '            for n, c in re.findall(r"([^,;(:]+?)\\s*\\(\\s*(" + EMAIL.pattern + r")\\s*\\)", l):\n'
        '                n = n.strip(" .*")\n'
        '                if find_person(n, reg) is None and c.lower() not in reg.by_account:\n'
        '                    out.append((n, c.lower()))\n'
        '    return out\n'
        '\n'
        '\n'
        'def collaborator_accounts(who: str, reg: Optional[PeopleRegistry] = None) -> set[str]:\n'
        '    """The accounts of the \xabColabora:\xbb lines of a project\'s \xabQui\xe9n participa\xbb. Same as colaboran_en()."""\n'
        '    reg = reg or PeopleRegistry()\n'
        '    out: set[str] = set()\n'
        '    for l in (who or "").split("\\n"):\n'
        '        if _LINE_COLLABORATES.match(l):\n'
        '            if reg.declared:\n'
        '                out |= accounts_of_names(l, reg)[0] | {c for _, c in provisional_people(l, reg)}\n'
        '            else:\n'
        '                out |= set(EMAIL.findall(l.lower()))\n'
        '    return out\n'
        '\n'
        '\n'
        '# \u2500\u2500 \xabContexto com\xfan\xbb \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'def context_owner_name(line: str) -> str:\n'
        '    """The name of \xabContexto com\xfan: Name\xbb, without the account in parentheses or what follows a comma, stop or dash."""\n'
        '    t = re.sub(r"\\s*\\([^)]*\\)", "", (line or "").split(":", 1)[-1])\n'
        '    return re.split(r",|\\.\\s|\\.$|\\s[\u2014\u2013-]\\s|;", t.strip())[0].strip()\n'
        '\n'
        '\n'
        'def context_owner_accounts(line: str, reg: PeopleRegistry) -> set[str]:\n'
        '    """The account in parentheses (up to 1.24) or the registry\'s for that name (1.25)."""\n'
        '    c = set(EMAIL.findall((line or "").split(":", 1)[-1].lower()))\n'
        '    if c:\n'
        '        return c\n'
        '    p = find_person(context_owner_name(line), reg)\n'
        '    return set(p.accounts) if p and not p.left_on else set()\n'
        '\n'
        '\n'
        'def name_of_account(account: str, reg: PeopleRegistry) -> str:\n'
        '    p = reg.by_account.get((account or "").lower())\n'
        '    return p.name if p and p.name != "?" else ""\n'
        '\n'
        '\n'
        "# \u2500\u2500 guia.md's first paragraph, and archived registers \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
        '\n'
        'ABOUT_THE_FOLDER = r"`(?:metodo|guia)\\.md`|plugin `memoria`|Aqu\xed solo est\xe1 lo nuestro"\n'
        '\n'
        '\n'
        'def drop_folder_talk(sentences: list[str], rx: str = ABOUT_THE_FOLDER) -> list[str]:\n'
        '    """The sentences of guia.md\'s first paragraph without what talks about the folder or the method. Of a sentence joined\n'
        '    by \xab;\xbb to one that does not, the other stays (not split by a \xab;\xbb in parentheses); within each part, what comes before\n'
        '    the comma, colon or dash that opens the folder talk stays if it has three words or more. Same as sin_carpeta()."""\n'
        '    out = []\n'
        '    for f in sentences:\n'
        '        if not re.search(rx, f):\n'
        '            out.append(f); continue\n'
        '        keep = []\n'
        '        for c in [c.strip() for c in re.split(r";(?![^()]*\\))", f)]:\n'
        '            m = re.search(rx, c) if c else None\n'
        '            if c and not m:\n'
        '                keep.append(c); continue\n'
        '            cuts = [s.start() for s in re.finditer(r"[,:\u2014](?![^()]*\\))", c[:m.start()] if m else "")]\n'
        '            t = c[:cuts[-1]].strip() if cuts else ""\n'
        '            if len(t.split()) >= 3 and not re.search(rx, t):\n'
        '                keep.append(t)\n'
        '        if keep:\n'
        '            t = "; ".join(keep); t = t[0].upper() + t[1:]\n'
        '            out.append(t if t[-1] in ".!?" else t + ".")\n'
        '    return out\n'
        '\n'
        '\n'
        'ARCHIVED = re.compile(r"^(sesiones|decisiones)-(20\\d\\d)(?:-(\\d+))?\\.md$")\n'
        '\n'
        '\n'
        'def archived_names(names: list[str], register: str, year) -> list[str]:\n'
        '    """Of the names in a project folder, the archives of a register (\xabsesiones\xbb or \xabdecisiones\xbb) from `year` - 1 on,\n'
        '    newest first. Older ones are not read whole (escribir.md, section 8)."""\n'
        '    seen = []\n'
        '    for n in names:\n'
        '        m = ARCHIVED.match(n)\n'
        '        if m and m.group(1) == register and int(m.group(2)) >= int(year) - 1:\n'
        '            seen.append((int(m.group(2)), int(m.group(3) or 1), n))\n'
        '    return [n for _, _, n in sorted(seen, reverse=True)]\n'
        '\n'
        '\n'
        'def with_archives(live: Optional[str], archives: list[Optional[str]]) -> tuple[str, int]:\n'
        '    """(text, entries of the live register): the live register followed by the entries of its archives, as if they had\n'
        '    not been archived, so every decision keeps its identifier. Same as con_archivados()."""\n'
        '    parts = [live or ""]\n'
        '    for t in archives:\n'
        '        m = re.search(r"^## ", t or "", re.M)\n'
        '        if m:\n'
        '            parts.append((t or "")[m.start():])\n'
        '    return "\\n\\n".join(p.strip("\\n") for p in parts if p.strip()) + "\\n", len(re.findall(r"^## ", live or "", re.M))\n'
        '\n'
        '\n'
        '\n'
        '# \u2500\u2500 entries of sesiones.md that are not sessions (1.26.8) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        '_PATTERNS: dict = {}\n'
        '\n'
        '\n'
        'def _patterns(lang: Pack) -> tuple:\n'
        '    """(any tag, the maintenance tag) compiled once per pack: is_session runs once per entry of every log read."""\n'
        '    k = id(lang)\n'
        '    if k not in _PATTERNS:\n'
        '        tags = "|".join(re.escape(x) for x in lang.non_session_tags)\n'
        '        _PATTERNS[k] = (re.compile(r"\\((?:" + tags + r")\\)", re.I), re.compile(r"\\(" + re.escape(lang.maintenance_tag) + r"\\)", re.I))\n'
        '    return _PATTERNS[k]\n'
        '\n'
        '\n'
        'def is_session(heading: str, lang: Pack = ES) -> bool:\n'
        '    """Whether a heading of sesiones.md (\xab## 2026-11-17 (tarea)\xbb, with or without \xab## \xbb) is a work session. The entries\n'
        '    of a scheduled task, the board, a migration and the maintenance trace tell what they did, but are not sessions: no\n'
        '    reader takes them as the last session, nor counts them, nor shows them among the recent ones."""\n'
        '    return not _patterns(lang)[0].search(heading or "")\n'
        '\n'
        '\n'
        'def is_maintenance(heading: str, lang: Pack = ES) -> bool:\n'
        '    return bool(_patterns(lang)[1].search(heading or ""))\n'
        '\n'
        '\n'
        'def _field(text: str, names: tuple) -> Optional[str]:\n'
        '    for l in (text or "").split("\\n"):\n'
        '        low = l.strip().lower()\n'
        '        for n in names:\n'
        '            if low.startswith(n):\n'
        '                return l.strip()[len(n):].strip()\n'
        '    return None\n'
        '\n'
        '\n'
        'def path_key(path: str) -> str:\n'
        '    """How two spellings of a path inside a project compare: \xab/\xbb separators, NFC (macOS and Drive may give NFD) and case\n'
        '    folded (disks that do not tell case apart)."""\n'
        '    return unicodedata.normalize("NFC", (path or "").replace("\\\\", "/").strip().strip("/")).casefold()\n'
        '\n'
        '\n'
        'def maintenance_files(entry: str, lang: Pack = ES) -> list[str]:\n'
        '    """The paths a maintenance entry says it fixed, inside the project: \xabArregl\xf3: taller/a.md (cabecera),\n'
        '    entregables/b.md (antes b.md)\xbb. What follows a path in parentheses is not a path."""\n'
        '    v = _field(entry, lang.session_fixed) or ""\n'
        '    out = []\n'
        '    for part in re.split(r",\\s*(?![^()]*\\))", v):\n'
        '        r = re.sub(r"\\s*\\(.*\\)\\s*$", "", part.strip()).strip().strip("`").strip().replace("\\\\", "/")\n'
        '        if r and r not in out:\n'
        '            out.append(r)\n'
        '    return out\n'
        '\n'
        '\n'
        'def _instant(value: Optional[str]) -> tuple:\n'
        '    """(readable, epoch seconds or None) of an ISO 8601 instant with its offset. \xabninguno\xbb reads as no instant; a value\n'
        '    without an offset does not read, because each reader would take it in its own zone."""\n'
        '    v = (value or "").split()[0] if (value or "").strip() else ""\n'
        '    if not v:\n'
        '        return False, None\n'
        '    if v.strip(".").lower() in ("ninguno", "ninguna"):\n'
        '        return True, None\n'
        '    try:\n'
        '        d = datetime.datetime.fromisoformat(v.replace("Z", "+00:00"))\n'
        '    except ValueError:\n'
        '        return False, None\n'
        '    return (True, d.timestamp()) if d.tzinfo is not None else (False, None)\n'
        '\n'
        '\n'
        'def maintenance_trace(entries: list[tuple[str, str]], log_mtime: Optional[float], lang: Pack = ES) -> tuple:\n'
        '    """(reference, discounted) for whoever compares file dates with the last close of a project (1.26.8).\n'
        '\n'
        '    `entries` are (heading, text) of sesiones.md newest first; `log_mtime` its modification time (epoch seconds). The\n'
        '    entries above the last real session that are not sessions ((tarea), (tablero), (migracion), (mantenimiento)) are\n'
        '    walked together. If a maintenance entry is among them, `reference` is the \xab\xdaltimo cierre\xbb of the newest one (the\n'
        '    instant of the last real close, carried from entry to entry) and `discounted` maps each file the maintenance entries\n'
        "    name (by path_key) to the instant until which it is discounted: its own entry's \xabEscrita\xbb plus a minute. A file that\n"
        "    changed after that is someone's work and keeps showing, whatever else writes the log later. Without a maintenance\n"
        '    entry above the last session, `reference` is `log_mtime` and nothing is discounted, as before 1.26.8. \xab\xdaltimo\n'
        '    cierre: ninguno\xbb gives None: there was no close. A value that does not read gives `log_mtime`, and an \xabEscrita\xbb that\n'
        '    does not read bounds its files by `log_mtime`."""\n'
        '    ref_set, ref = False, log_mtime\n'
        '    discounted: dict = {}\n'
        '    for head, text in entries:\n'
        '        if is_session(head, lang):\n'
        '            break\n'
        '        if not is_maintenance(head, lang):\n'
        '            continue\n'
        '        if not ref_set:\n'
        '            ok, ts = _instant(_field(text, lang.session_last_close))\n'
        '            ref, ref_set = (ts if ok else log_mtime), True\n'
        '        ok, written = _instant(_field(text, lang.session_written))\n'
        '        bound = (written if ok and written is not None else log_mtime)\n'
        '        for r in maintenance_files(text, lang):\n'
        '            k = path_key(r)\n'
        '            if bound is not None:\n'
        '                discounted[k] = max(discounted.get(k, 0), bound + 60)\n'
        '    return ref, discounted\n'
        '\n'
        '\n'
        'def discounted_file(path: str, seconds: Optional[float], discounted: dict) -> bool:\n'
        '    """Whether a file (path inside the project, its modification time) is a maintenance fix nobody changed since."""\n'
        '    b = discounted.get(path_key(path)) if discounted else None\n'
        '    return b is not None and seconds is not None and seconds <= b\n'
        '\n'
        '\n'
        'def project_finished(body: str, lang: Pack = ES) -> bool:\n'
        '    """\xabProyecto terminado el AAAA-MM-DD\xbb in the status section, under its 1.22 name or the older ones."""\n'
        '    for name in (lang.status,) + tuple(lang.status_legacy_project):\n'
        '        m = re.search(r"^##\\s+" + re.escape(name) + r"\\s*$(.*?)(?=^## |\\Z)", body or "", re.M | re.S)\n'
        '        if m and re.search(re.escape(lang.finished_marker) + r"\\s*20\\d\\d-\\d\\d-\\d\\d", m.group(1)):\n'
        '            return True\n'
        '    return False\n'
        '\n'
        '\n'
        '# \u2500\u2500 the people lines of \xabQui\xe9n participa\xbb (1.26) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'PEOPLE_LINE = re.compile(r"^\\s*[-*]?\\s*\\**\\s*(?:colabora[n]?|responsable|due[\xf1n][oa])\\s*\\**\\s*:", re.I)\n'
        '\n'
        '\n'
        'def people_lines(section: str) -> list[str]:\n'
        '    """The \xabResponsable:\xbb, \xabDue\xf1o:\xbb or \xabColabora:\xbb lines of a \xabQui\xe9n participa\xbb section. From 1.26 an area.md does not\n'
        '    carry them: who answers for an area and who collaborates in it is said only by guia.md."""\n'
        '    return [l for l in (section or "").split("\\n") if PEOPLE_LINE.match(l)]\n'
    ),
    'compat': (
        '"""The scripts\' Spanish names over the package, with the shapes they use today (dicts and tuples).\n'
        '\n'
        'The plugin scripts keep their Spanish until the language packs (decision of 2026-11-04). While each one moves onto the\n'
        'package, it imports these names in place of its own copy of the code, and nothing else in the script changes. A script\n'
        'that has moved no longer carries the copy; `packages/context-core/tests/test_compat.py` checks these return exactly what the copies do.\n'
        '"""\n'
        'from __future__ import annotations\n'
        '\n'
        'import pathlib\n'
        'import re\n'
        'from typing import Optional\n'
        '\n'
        'from . import rules\n'
        'from .records import PeopleRegistry, Person\n'
        '\n'
        '__all__ = ["SOBRE_LA_CARPETA", "sin_carpeta", "ARCHIVADO", "archivados_de", "con_archivados", "respuestas_viejas",\n'
        '           "restringida_celda", "area_restringida", "acceso_de", "CORREO", "PALABRA_COLABORA", "LINEA_COLABORA", "cuentas",\n'
        '           "clave_nombre", "registro_personas",\n'
        '           "persona", "nombres_de", "cuentas_de_nombres", "altas_provisionales", "columnas_personas", "fila_cuentas",\n'
        '           "nombre_contexto", "cuentas_contexto", "nombre_de", "colaboran_en", "personas_en_area",\n'
        '           "es_sesion", "es_mantenimiento", "arreglados", "rastro_mantenimiento", "descontado", "clave_ruta",\n'
        '           "proyecto_terminado"]\n'
        '\n'
        'CORREO = rules.EMAIL\n'
        'PALABRA_COLABORA = rules._WORD_COLLABORATES\n'
        'LINEA_COLABORA = rules._LINE_COLLABORATES\n'
        '\n'
        'cuentas = rules.account_cell\n'
        'clave_nombre = rules.name_key\n'
        'nombre_contexto = rules.context_owner_name\n'
        'es_sesion = rules.is_session\n'
        'es_mantenimiento = rules.is_maintenance\n'
        'arreglados = rules.maintenance_files\n'
        'rastro_mantenimiento = rules.maintenance_trace\n'
        'descontado = rules.discounted_file\n'
        'clave_ruta = rules.path_key\n'
        'proyecto_terminado = rules.project_finished\n'
        '\n'
        '\n'
        'def _persona(p: Person) -> dict:\n'
        '    return {"nombre": p.name, "cuentas": p.accounts, "drive": p.drive_accounts, "sin_cuenta": p.no_account,\n'
        '            "sin_confirmar": p.unconfirmed, "alias": p.aliases, "de": p.organization, "baja": p.left_on,\n'
        '            "compartida": p.shared_with, "registra": p.registered_by}\n'
        '\n'
        '\n'
        'class _Registro(dict):\n'
        '    """registro_personas()\'s dict, carrying the PeopleRegistry it was made from."""\n'
        '    registry: PeopleRegistry\n'
        '\n'
        '\n'
        'def _registro(reg: PeopleRegistry) -> _Registro:\n'
        '    dicts = {id(p): _persona(p) for p in reg.people}\n'
        '    r = _Registro(hay=reg.declared, personas=[dicts[id(p)] for p in reg.people],\n'
        '                  nombre={k: dicts[id(p)] for k, p in reg.by_name.items()},\n'
        '                  cuenta={k: dicts[id(p)] for k, p in reg.by_account.items()}, avisos=reg.warnings)\n'
        '    r.registry = reg\n'
        '    return r\n'
        '\n'
        '\n'
        'def _reg(reg) -> PeopleRegistry:\n'
        '    """Accepts what the scripts pass: the dict from registro_personas(), None or {}."""\n'
        '    return getattr(reg, "registry", None) or PeopleRegistry()\n'
        '\n'
        '\n'
        'def registro_personas(guia: str) -> dict:\n'
        '    return _registro(rules.people_registry(guia))\n'
        '\n'
        '\n'
        'def persona(nombre: str, reg) -> Optional[dict]:\n'
        '    """The person with that name, alias or account; None if missing or ambiguous."""\n'
        '    t = (nombre or "").strip()\n'
        '    if CORREO.fullmatch(t.lower()):\n'
        '        return (reg or {}).get("cuenta", {}).get(t.lower())\n'
        '    return (reg or {}).get("nombre", {}).get(clave_nombre(t))\n'
        '\n'
        '\n'
        'def nombres_de(texto: str, reg=None) -> list[str]:\n'
        '    return rules.names_in(texto, _reg(reg))\n'
        '\n'
        '\n'
        'def cuentas_de_nombres(texto: str, reg) -> tuple[set, list]:\n'
        '    return rules.accounts_of_names(texto, _reg(reg))\n'
        '\n'
        '\n'
        'def altas_provisionales(quien: str, reg) -> list:\n'
        '    return rules.provisional_people(quien, _reg(reg))\n'
        '\n'
        '\n'
        'def columnas_personas(cab: list) -> dict:\n'
        '    c = rules._people_columns(cab)\n'
        '    return {"responsable": c["responsible"], "cuenta": c["account"], "colabora": c["collaborates"]}\n'
        '\n'
        '\n'
        'def fila_cuentas(cab: list, celdas: list, reg) -> tuple:\n'
        '    return rules.row_accounts(cab, celdas, _reg(reg))\n'
        '\n'
        '\n'
        'def cuentas_contexto(linea: str, reg) -> set:\n'
        '    return rules.context_owner_accounts(linea, _reg(reg))\n'
        '\n'
        '\n'
        'def nombre_de(cuenta: str, reg) -> str:\n'
        '    return rules.name_of_account(cuenta, _reg(reg))\n'
        '\n'
        '\n'
        'def colaboran_en(quien: str, reg=None) -> set:\n'
        '    return rules.collaborator_accounts(quien, _reg(reg) if reg else None)\n'
        '\n'
        '\n'
        '# \u2500\u2500 el primer p\xe1rrafo de guia.md, los registros con sus archivados y la regla de lo restringido \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'SOBRE_LA_CARPETA = rules.ABOUT_THE_FOLDER\n'
        'sin_carpeta = rules.drop_folder_talk\n'
        'ARCHIVADO = rules.ARCHIVED\n'
        'restringida_celda = rules.is_restricted_cell\n'
        '\n'
        '\n'
        'def area_restringida(celdas: list, cab: list) -> bool:\n'
        '    """Whether a row of the area table is restricted, from the row and the table\'s header: the one rule (finding 10 of\n'
        '    the review of 1.25.2), the 1.25.1 abrir.py\'s area_restringida()."""\n'
        '    return rules.area_is_restricted(celdas, cab)\n'
        '\n'
        '\n'
        'def acceso_de(celda: str) -> Optional[bool]:\n'
        '    """\xabAcceso\xbb: True \xabRestringida\xbb, False \xabAbierta\xbb, None anything else."""\n'
        '    return rules.access_word(celda)\n'
        '\n'
        '\n'
        'def _nombres(carpeta) -> list:\n'
        '    try:\n'
        '        return [x.name for x in pathlib.Path(carpeta).iterdir()]\n'
        '    except OSError:\n'
        '        return []\n'
        '\n'
        '\n'
        'def archivados_de(carpeta, nombre, anio) -> list:\n'
        '    return rules.archived_names(_nombres(carpeta), nombre, anio)\n'
        '\n'
        '\n'
        'def con_archivados(carpeta, nombre, vivo, anio, leer_) -> tuple:\n'
        '    return rules.with_archives(vivo, [leer_(pathlib.Path(carpeta) / n) for n in archivados_de(carpeta, nombre, anio)])\n'
        '\n'
        '\n'
        'def respuestas_viejas(carpeta, anio, leer_) -> list:\n'
        '    """The \xabResponde a:\xbb lines of decision archives older than last year, which are not read whole."""\n'
        '    recientes = set(archivados_de(carpeta, "decisiones", anio))\n'
        '    out = []\n'
        '    for n in archivados_de(carpeta, "decisiones", 0):\n'
        '        if n not in recientes:\n'
        '            out += re.findall(r"^Responde a:[ \\t]*(.+)$", leer_(pathlib.Path(carpeta) / n) or "", re.M)\n'
        '    return out\n'
        '\n'
        '\n'
        '\n'
        'def personas_en_area(texto_area: str) -> list:\n'
        '    """Las l\xedneas \xabResponsable:\xbb, \xabDue\xf1o:\xbb o \xabColabora:\xbb de \xabQui\xe9n participa\xbb de un area.md, que la 1.26 quita."""\n'
        '    m = re.search(r"^## Qui\xe9n participa\\s*\\n(.*?)(?=^## |\\Z)", texto_area or "", re.M | re.S)\n'
        '    return rules.people_lines(m.group(1) if m else "")\n'
    ),
    'minimum': (
        '"""The minimum plugin version a root declares in guia.md (1.26): below it, a plugin reads but does not write.\n'
        '\n'
        'Its own module, so only the scripts that gate writing carry it (abrir.py, cerrar.py, migrar_estructura.py,\n'
        'aplicar_cambios.py, generar_vista.py; review of 1.26, finding on size). The English functions are the rule; the Spanish\n'
        'names at the end are what the scripts use, as `compat` does.\n'
        '\n'
        'The section is found tolerantly and read strictly, so that an error never opens the gate (review of 1.26): any heading\n'
        'level, case, accents, bold or a colon after the title still declare it; its version is the first thing in the title\n'
        'after the name or in its first paragraph, and anything else reads as unreadable, which closes writing. Two sections give\n'
        'the highest version, and an unreadable one closes.\n'
        '"""\n'
        'from __future__ import annotations\n'
        '\n'
        'import re\n'
        'import unicodedata\n'
        'from typing import Optional\n'
        '\n'
        'from .language import ES, Pack\n'
        '\n'
        '__all__ = ["version_tuple", "minimum_plugin_version", "plugin_may_write", "STRUCTURE_MINIMUM",\n'
        '           "VERSION_MINIMA_ESTRUCTURA", "RECETA_ACTUALIZAR", "puerta_de_escritura", "seccion_minima"]\n'
        '\n'
        '# the minimum the current structure needs: what the migration writes, and what an opening calls \xabbehind\xbb (1.26: \xabQui\xe9n es\n'
        '# qui\xe9n\xbb; 1.26.8: the maintenance entries of sesiones.md, which an older plugin would count as sessions). Every structure\n'
        '# change raises it with its migration\n'
        'STRUCTURE_MINIMUM = "1.26.8"\n'
        '\n'
        '_VERSION = re.compile(r"(?<![\\d.])(\\d+)\\.(\\d+)(?:\\.(\\d+))?(?!\\.?\\d)")\n'
        '_LEADING = re.compile(r"^[\\s*_`\xab\\"(]*(?:v(?:ersi[o\xf3]n)?\\s*)?(\\d+)\\.(\\d+)(?:\\.(\\d+))?(?!\\.?\\d)", re.I)\n'
        '\n'
        '\n'
        'def version_tuple(text: str) -> Optional[tuple]:\n'
        '    """\xab1.26\xbb or \xab1.26.0\xbb (the first version in `text`) as (1, 26, 0); None without one."""\n'
        '    m = _VERSION.search(text or "")\n'
        '    return (int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)) if m else None\n'
        '\n'
        '\n'
        'def _key(t: str) -> str:\n'
        '    t = "".join(c for c in unicodedata.normalize("NFD", t or "") if unicodedata.category(c) != "Mn")\n'
        '    return re.sub(r"\\s+", " ", re.sub(r"[^a-z0-9. ]", " ", t.lower())).strip()\n'
        '\n'
        '\n'
        'def _leading(text: str) -> Optional[tuple]:\n'
        '    m = _LEADING.match(text or "")\n'
        '    return (int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)) if m else None\n'
        '\n'
        '\n'
        'def minimum_plugin_version(guia: str, lang: Pack = ES) -> tuple[bool, Optional[tuple]]:\n'
        '    """(declared, version) from the section \xabVersi\xf3n m\xednima del plugin\xbb of guia.md. (False, None): no such section,\n'
        '    anyone may write. (True, None): a section whose version cannot be read, which nobody may write under until it is\n'
        '    fixed. A heading counts as the section when it says \xabm\xednima\xbb and \xabplugin\xbb (any case, accents, level or bold)."""\n'
        '    text = unicodedata.normalize("NFC", (guia or "").replace("\\r\\n", "\\n").replace("\\r", "\\n"))\n'
        '    name = _key(lang.minimum_plugin)\n'
        '    words = [w for w in name.split() if len(w) > 3]\n'
        '    heads = list(re.finditer(r"^[ \\t]*#{1,6}[ \\t]*(.*?)[ \\t#]*$", text, re.M))\n'
        '    found, versions = False, []\n'
        '    for i, h in enumerate(heads):\n'
        '        k = _key(h.group(1))\n'
        '        if not (k.startswith(name) or all(w in k for w in words[-2:])):\n'
        '            continue\n'
        '        found = True\n'
        '        body = text[h.end():heads[i + 1].start() if i + 1 < len(heads) else len(text)]\n'
        '        rest = k[len(name):] if k.startswith(name) else ""\n'
        '        v = _leading(rest) if rest.strip() else None\n'
        '        if v is None:\n'
        '            first = next((b for b in re.split(r"\\n\\s*\\n", body.strip()) if b.strip()), "")\n'
        '            v = _leading(first)\n'
        '        if v is None:\n'
        '            return True, None\n'
        '        versions.append(v)\n'
        '    return (True, max(versions)) if found else (False, None)\n'
        '\n'
        '\n'
        'def plugin_may_write(plugin_version: str, guia: str, lang: Pack = ES) -> tuple[str, Optional[tuple]]:\n'
        '    """Whether a plugin may write in the root of this guia.md: ("ok", minimum or None), ("below", minimum),\n'
        '    ("unreadable", None) for a section with no readable version, or ("unknown", minimum) for a plugin version that does\n'
        '    not parse. Reading is never gated; only writing (decision of 2026-11-08)."""\n'
        '    declared, minimum = minimum_plugin_version(guia, lang)\n'
        '    if not declared:\n'
        '        return "ok", None\n'
        '    if minimum is None:\n'
        '        return "unreadable", None\n'
        '    mine = version_tuple(plugin_version)\n'
        '    if mine is None:\n'
        '        return "unknown", minimum\n'
        '    return ("ok" if mine >= minimum else "below"), minimum\n'
        '\n'
        '\n'
        '# \u2500\u2500 las mismas reglas con los nombres de los scripts \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'VERSION_MINIMA_ESTRUCTURA = STRUCTURE_MINIMUM\n'
        'RECETA_ACTUALIZAR = ("en la app de Claude, Customize \u2192 Plugins, el bot\xf3n Update del marketplace memoria-marketplace "\n'
        '                     "(en Claude Code, /plugin marketplace update memoria-marketplace), o pide ayuda a quien administra la carpeta")\n'
        '\n'
        '\n'
        'def seccion_minima(version: str = STRUCTURE_MINIMUM) -> str:\n'
        '    """La secci\xf3n que escribe la migraci\xf3n. Dice qu\xe9 no hacer, porque un plugin anterior a la 1.26 solo la lee como regla."""\n'
        '    return ("## Versi\xf3n m\xednima del plugin\\n"\n'
        '            f"{version}. Con un plugin anterior, esta carpeta se lee y se consulta, pero no se escribe nada: no se cierra sesi\xf3n, ni se "\n'
        '            "registran decisiones, ni se crean o cambian documentos, ni se pone al d\xeda el tablero; primero se actualiza el plugin. "\n'
        '            f"Para actualizar: {RECETA_ACTUALIZAR}.\\n")\n'
        '\n'
        '\n'
        'def puerta_de_escritura(version_plugin: str, guia: str) -> tuple:\n'
        '    """(puede escribir, versi\xf3n m\xednima como texto o None, motivo en llano o ""): la secci\xf3n \xabVersi\xf3n m\xednima del plugin\xbb\n'
        '    de guia.md frente a la versi\xf3n del plugin que corre. El motivo es lo que se le dice a la persona."""\n'
        '    estado, minima = plugin_may_write(version_plugin, guia)\n'
        '    txt = ".".join(map(str, minima)) if minima else None\n'
        '    if estado == "ok":\n'
        '        return True, txt, ""\n'
        '    if estado == "unreadable":\n'
        '        return False, None, ("La secci\xf3n \xabVersi\xf3n m\xednima del plugin\xbb de guia.md no dice qu\xe9 versi\xf3n: no se escribe nada en esta "\n'
        '                             "carpeta hasta que su primer p\xe1rrafo empiece por la versi\xf3n (por ejemplo \xab1.26.8.\xbb). La corrige el "\n'
        '                             "responsable de contexto, en su sesi\xf3n o a mano. Leer y consultar siguen funcionando.")\n'
        '    if estado == "unknown":\n'
        '        return False, txt, (f"No s\xe9 qu\xe9 versi\xf3n del plugin corre aqu\xed (\xab{version_plugin}\xbb) y esta carpeta pide la {txt} o una m\xe1s "\n'
        '                            "nueva para escribir: no se escribe nada. Leer y consultar siguen funcionando.")\n'
        '    return False, txt, (f"Tu plugin memoria es la {version_plugin} y esta carpeta pide la {txt} o una m\xe1s nueva para escribir: "\n'
        '                        "puedes leer y consultar, pero no se escribe nada (ni sesiones, ni decisiones, ni documentos, ni el tablero) "\n'
        '                        f"hasta que lo actualices: {RECETA_ACTUALIZAR}.")\n'
    ),
    'development': (
        '"""The development kit (1.27): how a project that builds software is read. Pure functions: text in, data out; no I/O,\n'
        'no network, no clock.\n'
        '\n'
        'A project is a development project when its proyecto.md has a \xab## Desarrollo\xbb section\n'
        '(tecnologia/metodologia-desarrollo#2026-11-18-4). The section points to each piece of the kit (the two configurations,\n'
        'the design, the plan and the follow-up) and names the people of each role. The design and the plan are two living\n'
        'documents whose fixed tables this module reads (#2026-11-18-10); the configurations are seven lines each with a dated\n'
        "state (#2026-11-18-11). A piece's status comes from its pull requests into the main branch by one rule (#2026-11-18-10\n"
        'and -12), and this module\n'
        'applies it to pull requests the caller already read: it never calls GitHub.\n'
        '\n'
        "The keys of the method's files are Spanish and are compared as the decisions say: NFC, without accents or case. The code\n"
        'names things in English; the Spanish names the specification uses (`seccion_desarrollo`, `piezas_faltantes`,\n'
        '`leer_diseno`, `leer_plan`, `leer_configuracion`, `estado_piezas`) are aliases of the same functions, at the end.\n'
        '"""\n'
        'from __future__ import annotations\n'
        '\n'
        'import dataclasses\n'
        'import re\n'
        'import unicodedata\n'
        'from dataclasses import dataclass, field\n'
        'from typing import Callable, Iterable, Mapping, Optional\n'
        '\n'
        '__all__ = [\n'
        '    "SECTION", "PATH_KEYS", "ROLE_KEYS", "TO_BUILD", "DevPerson", "DevSection", "Missing",\n'
        '    "Relation", "Entity", "Design", "Phase", "Piece", "Plan", "ConfigRow", "ApprovedChange", "Configuration",\n'
        '    "PullRequest", "PieceStatus", "PieceReport",\n'
        '    "key", "development_section", "missing_pieces", "read_design", "read_plan", "read_configuration", "piece_status",\n'
        '    "as_dict",\n'
        '    "seccion_desarrollo", "piezas_faltantes", "leer_diseno", "leer_plan", "leer_configuracion", "estado_piezas",\n'
        ']\n'
        '\n'
        'SECTION = "Desarrollo"\n'
        'TO_BUILD = "por crear"\n'
        '\n'
        "# the section's keys, as written in the template (plantilla-seccion-desarrollo.md), in their order\n"
        'REPOSITORIES = "Repositorios"\n'
        'PLATFORM = "Configuraci\xf3n de plataforma"\n'
        'REPOSITORY_CONFIG = "Configuraci\xf3n de repositorios"\n'
        'DESIGN = "Dise\xf1o"\n'
        'PLAN = "Plan"\n'
        'FOLLOW_UP = "Seguimiento"\n'
        'STEP_TO_PROD = "Paso a Prod"\n'
        'PATH_KEYS = (PLATFORM, REPOSITORY_CONFIG, DESIGN, PLAN, FOLLOW_UP)\n'
        'ROLE_KEYS = ("Acepta", "Audita", "Construye", "Administra")\n'
        'ALL_KEYS = (REPOSITORIES,) + PATH_KEYS + (STEP_TO_PROD,) + ROLE_KEYS\n'
        '\n'
        'SEPARATOR = re.compile(r"\\s+\xb7\\s+")          # \xab \xb7 \xbb between values; a bare \xab\xb7\xbb inside a name is not a separator\n'
        'REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")\n'
        'EMAIL = re.compile(r"^[\\w.+\'-]+@[\\w-]+(?:\\.[\\w-]+)+$")\n'
        'GITHUB_USER = re.compile(r"^@?([A-Za-z0-9](?:[A-Za-z0-9._-]{0,38}))$")   # \xab_\xbb for Enterprise Managed Users\n'
        'DATE = re.compile(r"\\b(20\\d\\d-\\d\\d-\\d\\d)\\b")\n'
        '\n'
        '\n'
        '# \u2500\u2500 comparing \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'def key(text: str) -> str:\n'
        '    """How a key, a heading or a column title compares: NFC or NFD alike, without accents, case, markup or punctuation."""\n'
        '    t = unicodedata.normalize("NFD", text or "")\n'
        '    t = "".join(c for c in t if unicodedata.category(c) != "Mn").replace("\xa0", " ").lower()\n'
        '    return re.sub(r"\\s+", " ", re.sub(r"[^a-z0-9 ]", " ", t)).strip()\n'
        '\n'
        '\n'
        'def _nfc(text: str) -> str:\n'
        '    return unicodedata.normalize("NFC", (text or "").replace("\\r\\n", "\\n").replace("\\r", "\\n")).replace("\xa0", " ")\n'
        '\n'
        '\n'
        'def _clean(value: str) -> str:\n'
        '    """A value as written, without the Markdown around it: backticks, bold, a link\'s brackets (its target is kept)."""\n'
        '    v = value.strip()\n'
        '    v = re.sub(r"\\[([^\\]]*)\\]\\(([^)]*)\\)", lambda m: m.group(2) or m.group(1), v)\n'
        '    return v.replace("`", "").replace("**", "").strip()\n'
        '\n'
        '\n'
        'def _is_to_build(value: str) -> bool:\n'
        '    return key(value) == key(TO_BUILD)\n'
        '\n'
        '\n'
        'def _sections(body: str) -> dict:\n'
        '    """Every \xab## \xbb section of a text by its key, cut at the next \xab## \xbb (the same cut abrir.py, cerrar.py and\n'
        '    verificar.sh make). The first of two with the same key wins. Fenced code blocks are skipped, so a \xab## \xbb inside an\n'
        '    example does not open a section."""\n'
        '    out: dict = {}\n'
        '    name, lines, fence = None, [], False\n'
        '    for line in _nfc(body).split("\\n"):\n'
        '        if re.match(r"^\\s*(```|~~~)", line):\n'
        '            fence = not fence\n'
        '        if not fence and line.startswith("## "):\n'
        '            if name is not None and key(name) not in out:\n'
        '                out[key(name)] = (name, "\\n".join(lines))\n'
        '            name, lines = line[3:].strip(), []\n'
        '        elif name is not None:\n'
        '            lines.append(line)\n'
        '    if name is not None and key(name) not in out:\n'
        '        out[key(name)] = (name, "\\n".join(lines))\n'
        '    return out\n'
        '\n'
        '\n'
        'def _tables(block: str) -> list:\n'
        '    """Every Markdown table in a block, as (header, rows). Cells keep their text; a row shorter than the header is\n'
        '    padded, one longer is cut (a \xab|\xbb inside a cell is the writer\'s problem, and the method\'s tables forbid it)."""\n'
        '    out, header, rows = [], None, []\n'
        '    for line in block.split("\\n") + [""]:\n'
        '        s = line.strip()\n'
        '        if not s.startswith("|"):\n'
        '            if header is not None:\n'
        '                out.append((header, rows))\n'
        '            header, rows = None, []\n'
        '            continue\n'
        '        if re.match(r"^\\|[\\s:|-]+\\|?\\s*$", s):\n'
        '            continue\n'
        '        cells = [c.strip() for c in s.strip("|").split("|")]\n'
        '        if header is None:\n'
        '            header = cells\n'
        '        else:\n'
        '            rows.append((cells + [""] * len(header))[:len(header)])\n'
        '    return out\n'
        '\n'
        '\n'
        'def _table(block: str) -> tuple:\n'
        '    """(header, rows) of the first table in a block; ([], []) without one."""\n'
        '    t = _tables(block)\n'
        '    return t[0] if t else ([], [])\n'
        '\n'
        '\n'
        'def _placeholder(cells: Iterable[str]) -> bool:\n'
        '    """A row the template left as it was: every non-empty cell is \xab[\u2026]\xbb."""\n'
        '    full = [c for c in cells if c.strip()]\n'
        '    return not full or all(re.match(r"^\\[[^\\]]*\\]$", c.strip()) for c in full)\n'
        '\n'
        '\n'
        'def _columns(header: list, expected: Iterable[str]) -> tuple[dict, list]:\n'
        '    """Where each expected column is, by its key, and the expected ones that are not there."""\n'
        '    at = {}\n'
        '    for i, h in enumerate(header):\n'
        '        at.setdefault(key(h), i)\n'
        '    found, missing = {}, []\n'
        '    for e in expected:\n'
        '        if key(e) in at:\n'
        '            found[e] = at[key(e)]\n'
        '        else:\n'
        '            missing.append(e)\n'
        '    return found, missing\n'
        '\n'
        '\n'
        'def _ident(cell: str) -> tuple[str, str]:\n'
        '    """\xabP01 \xb7 name\xbb -> ("P01", "name"); a cell with no \xab \xb7 \xbb is all identifier."""\n'
        '    c = _clean(cell)\n'
        '    parts = SEPARATOR.split(c, maxsplit=1)\n'
        '    return parts[0].strip(), (parts[1].strip() if len(parts) > 1 else "")\n'
        '\n'
        '\n'
        '# \u2500\u2500 the \xabDesarrollo\xbb section \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        '@dataclass\n'
        'class DevPerson:\n'
        '    """One person of a role: \xabNombre Apellido (correo, @usuario)\xbb; the GitHub user is left out without an account."""\n'
        '    name: str\n'
        '    email: str = ""\n'
        '    user: str = ""                              # GitHub login, without \xab@\xbb\n'
        '    raw: str = ""\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class DevSection:\n'
        '    """The \xab## Desarrollo\xbb section of a proyecto.md. `found` False means the project is not a development project."""\n'
        '    found: bool = False\n'
        '    repositories: list = field(default_factory=list)       # \xaborganizaci\xf3n/repositorio\xbb\n'
        '    paths: dict = field(default_factory=dict)              # PATH_KEYS -> path from the root, or TO_BUILD\n'
        '    step_to_prod: str = ""                                 # \xabPaso a Prod\xbb, as written\n'
        '    roles: dict = field(default_factory=dict)              # ROLE_KEYS -> [DevPerson]\n'
        '    present: list = field(default_factory=list)            # the keys that have a line, in ALL_KEYS spelling\n'
        '    to_build: list = field(default_factory=list)           # the keys whose value is \xabpor crear\xbb\n'
        '    near_miss: bool = False                                # a \xab## Desarrollo\xbb that looks like the kit but is not recognised\n'
        '    unknown: list = field(default_factory=list)            # lines of the section it does not recognise\n'
        '    warnings: list = field(default_factory=list)\n'
        '\n'
        '\n'
        '_BY_KEY = {key(k): k for k in ALL_KEYS}\n'
        '\n'
        '\n'
        'def _person(text: str) -> tuple[DevPerson, list]:\n'
        '    t = text.strip()\n'
        '    warnings = []\n'
        '    m = re.match(r"^(.*?)\\s*\\(([^()]*)\\)\\s*$", t)\n'
        '    name, inside = (m.group(1), m.group(2)) if m else (t, "")\n'
        '    p = DevPerson(name=_clean(name), raw=t)\n'
        '    for item in (x.strip() for x in inside.split(",")):\n'
        '        if not item:\n'
        '            continue\n'
        '        if EMAIL.match(item):\n'
        '            if p.email:\n'
        '                warnings.append(f"\xab{t}\xbb: dos correos; se toma el primero")\n'
        '            else:\n'
        '                p.email = item.lower()\n'
        '        elif item.startswith("@") and GITHUB_USER.match(item):\n'
        '            p.user = GITHUB_USER.match(item).group(1)\n'
        '        else:\n'
        '            warnings.append(f"\xab{t}\xbb: \xab{item}\xbb no es un correo ni un usuario de GitHub (@usuario)")\n'
        '    if not p.name:\n'
        '        warnings.append(f"\xab{t}\xbb: falta el nombre")\n'
        '    return p, warnings\n'
        '\n'
        '\n'
        '_LINE = re.compile(r"^[-*]?\\s*\\**\\s*([^:*]+?)\\s*\\**\\s*:\\s*\\**\\s*(.*)$")\n'
        '\n'
        '\n'
        'def _line_key(line: str) -> Optional[str]:\n'
        '    """The kit\'s key a line of the section starts with, in ALL_KEYS spelling, or None."""\n'
        '    m = _LINE.match((line or "").strip())\n'
        '    return _BY_KEY.get(key(m.group(1))) if m else None\n'
        '\n'
        '\n'
        'def development_section(project_text: str) -> DevSection:\n'
        '    """The \xab## Desarrollo\xbb section of a proyecto.md, split in repositories, paths, \xabPaso a Prod\xbb and the roles with\n'
        "    their people. Keys compared without accents or case (NFC or NFD alike); people separated by \xab \xb7 \xbb and each one's\n"
        '    data by commas. What it does not recognise comes back in `unknown`."""\n'
        '    sec = _sections(project_text).get(key(SECTION))\n'
        '    out = DevSection()\n'
        '    if sec is None:\n'
        '        return out\n'
        '    # \xabDesarrollo\xbb is a common heading in Spanish: the section marks a development project only with \xabRepositorios:\xbb or\n'
        '    # two keys of the kit, comments aside (review of 1.27.0, finding 20, and its fixes, finding 10). One that looks like\n'
        '    # the kit and is not recognised is said in `near_miss`, so a misspelt section is not silently invisible.\n'
        '    claves = {k for k in (_line_key(l) for l in sec[1].split("\\n") if not l.strip().startswith("<!--")) if k}\n'
        '    if REPOSITORIES not in claves and len(claves) < 2:\n'
        '        # a near miss: a \xabClave:\xbb line that is no key of the kit but starts like one (\xabRepositorio:\xbb, \xabConstruyen:\xbb)\n'
        '        prefijos = {key(k)[:6] for k in ALL_KEYS}\n'
        '        out.near_miss = any(m and not _line_key(l) and key(m.group(1))[:6] in prefijos\n'
        '                            for l in sec[1].split("\\n") for m in [_LINE.match(l.strip())])\n'
        '        return out\n'
        '    out.found = True\n'
        '    for raw in sec[1].split("\\n"):\n'
        '        line = raw.strip()\n'
        '        if not line or re.match(r"^<!--.*-->$", line):\n'
        '            continue\n'
        '        m = re.match(r"^[-*]?\\s*\\**\\s*([^:*]+?)\\s*\\**\\s*:\\s*\\**\\s*(.*)$", line)\n'
        '        k = _BY_KEY.get(key(m.group(1))) if m else None\n'
        '        if k is None:\n'
        '            out.unknown.append(line)\n'
        '            continue\n'
        '        if k in out.present:\n'
        '            out.warnings.append(f"\xab{k}\xbb aparece dos veces; vale la primera")\n'
        '            continue\n'
        '        out.present.append(k)\n'
        '        value = _clean(m.group(2))\n'
        '        if _is_to_build(value):\n'
        '            out.to_build.append(k)\n'
        '            if k in PATH_KEYS:\n'
        '                out.paths[k] = TO_BUILD\n'
        '            elif k in ROLE_KEYS:\n'
        '                out.roles[k] = []\n'
        '            continue\n'
        '        if k == REPOSITORIES:\n'
        '            for r in (x.strip() for x in SEPARATOR.split(value) if x.strip()):\n'
        '                if REPO.match(r):\n'
        '                    if r.lower() not in (x.lower() for x in out.repositories):\n'
        '                        out.repositories.append(r)\n'
        '                else:\n'
        '                    out.warnings.append(f"\xab{r}\xbb en Repositorios no es organizaci\xf3n/repositorio")\n'
        '        elif k in PATH_KEYS:\n'
        '            out.paths[k] = value.strip().lstrip("/")\n'
        '        elif k == STEP_TO_PROD:\n'
        '            out.step_to_prod = value\n'
        '        else:\n'
        '            people = []\n'
        '            for t in (x for x in SEPARATOR.split(value) if x.strip()):\n'
        '                p, w = _person(t)\n'
        '                people.append(p)\n'
        '                out.warnings += w\n'
        '            out.roles[k] = people\n'
        '    return out\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Missing:\n'
        '    """A piece of the kit that is missing: its line, or the file its line points to."""\n'
        '    key: str                                    # in ALL_KEYS spelling\n'
        '    reason: str                                 # "sin l\xednea" | "por crear" | "no existe" | "vac\xeda"\n'
        '    path: str = ""\n'
        '\n'
        '\n'
        'def missing_pieces(section: DevSection, exists: Callable[[str], bool]) -> list:\n'
        '    """The lines of the section that are missing or point to a file that is not there, with `exists(path)` saying\n'
        '    whether a path from the root exists. \xabSeguimiento: por crear\xbb does not count: the plugin creates it at the first\n'
        '    follow-up. Empty for a project without the section."""\n'
        '    if not section.found:\n'
        '        return []\n'
        '    out = []\n'
        '    for k in ALL_KEYS:\n'
        '        if k not in section.present:\n'
        '            out.append(Missing(k, "sin l\xednea"))\n'
        '        elif k in section.to_build:\n'
        '            if k != FOLLOW_UP:\n'
        '                out.append(Missing(k, "por crear"))\n'
        '        elif k == REPOSITORIES and not section.repositories:\n'
        '            out.append(Missing(k, "vac\xeda"))\n'
        '        elif k in ROLE_KEYS and not section.roles.get(k):\n'
        '            out.append(Missing(k, "vac\xeda"))\n'
        '        elif k == STEP_TO_PROD and not section.step_to_prod:\n'
        '            out.append(Missing(k, "vac\xeda"))\n'
        '        elif k in PATH_KEYS:\n'
        '            v = section.paths.get(k, "")\n'
        '            if not v:\n'
        '                out.append(Missing(k, "vac\xeda"))\n'
        '            elif not exists(v):\n'
        '                out.append(Missing(k, "no existe", v))\n'
        '    return out\n'
        '\n'
        '\n'
        '# \u2500\u2500 the design \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'DESIGN_TABLES = {\n'
        '    "Reglas": ("Regla", "Excepci\xf3n"),\n'
        '    "Componentes": ("Componente", "Qu\xe9 hace", "D\xf3nde vive"),\n'
        '    "Datos": ("Entidad", "Qu\xe9 es", "Se relaciona con"),\n'
        '    "Conceptos": ("Concepto", "Significa", "No es"),\n'
        '    "Infraestructura": ("Pieza", "Para qu\xe9", "D\xf3nde"),\n'
        '}\n'
        'DESIGN_TEXT = ("Objetivo", "Prototipo")\n'
        'CARDINALITIES = {"1:n": "1:N", "1:1": "1:1", "n:m": "N:M", "n:n": "N:M", "m:n": "N:M"}\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Relation:\n'
        '    target: str\n'
        '    cardinality: str                            # "1:N" (this entity is the \xabone\xbb side), "1:1", "N:M"\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Entity:\n'
        '    name: str                                   # its name in the code\n'
        '    what: str = ""\n'
        '    relations: list = field(default_factory=list)\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Design:\n'
        '    objective: str = ""\n'
        '    prototype: str = ""\n'
        '    rules: list = field(default_factory=list)          # [{"regla", "excepcion"}]\n'
        '    components: list = field(default_factory=list)     # [{"componente", "que_hace", "donde_vive"}]\n'
        '    entities: list = field(default_factory=list)       # [Entity]\n'
        '    concepts: list = field(default_factory=list)       # [{"concepto", "significa", "no_es": [..]}]\n'
        '    infrastructure: list = field(default_factory=list) # [{"pieza", "para_que", "donde"}]\n'
        '    missing: list = field(default_factory=list)        # \xabsecci\xf3n Datos\xbb, \xabcolumna D\xf3nde vive en Componentes\xbb\n'
        '    warnings: list = field(default_factory=list)\n'
        '\n'
        '\n'
        'def _field_name(column: str) -> str:\n'
        '    return key(column).replace(" ", "_")\n'
        '\n'
        '\n'
        'def _relations(cell: str, entity: str, warnings: list) -> list:\n'
        '    out = []\n'
        '    for part in (x.strip() for x in _clean(cell).split(",") if x.strip()):\n'
        '        if part in ("-", "\u2014", "\u2013") or _placeholder([part]):\n'
        '            continue\n'
        '        m = re.match(r"^(.+?)\\s*\\(\\s*([0-9NnMm]\\s*:\\s*[0-9NnMm])\\s*\\)$", part)\n'
        '        if not m:\n'
        '            warnings.append(f"Datos, {entity}: \xab{part}\xbb no lleva su cardinalidad entre par\xe9ntesis, como \xabotra (1:N)\xbb")\n'
        '            continue\n'
        '        card = CARDINALITIES.get(re.sub(r"\\s", "", m.group(2)).lower())\n'
        '        if card is None:\n'
        '            warnings.append(f"Datos, {entity}: \xab{m.group(2)}\xbb no es 1:N, 1:1 ni N:M (una N:1 se escribe en la otra entidad)")\n'
        '            continue\n'
        '        out.append(Relation(target=_clean(m.group(1)), cardinality=card))\n'
        '    return out\n'
        '\n'
        '\n'
        'def read_design(text: str) -> Design:\n'
        '    """The design\'s tables by their section and column titles, with the relations split (\xabotra (1:N)\xbb), and the\n'
        '    expected sections or columns it did not find."""\n'
        '    secs = _sections(text)\n'
        '    d = Design()\n'
        '    d.objective = secs.get(key("Objetivo"), ("", ""))[1].strip()\n'
        '    d.prototype = secs.get(key("Prototipo"), ("", ""))[1].strip()\n'
        '    for name in DESIGN_TEXT:\n'
        '        if key(name) not in secs:\n'
        '            d.missing.append(f"secci\xf3n {name}")\n'
        '    for name, cols in DESIGN_TABLES.items():\n'
        '        if key(name) not in secs:\n'
        '            d.missing.append(f"secci\xf3n {name}")\n'
        '            continue\n'
        '        header, rows = _table(secs[key(name)][1])\n'
        '        if not header:\n'
        '            d.missing.append(f"tabla de {name}")\n'
        '            continue\n'
        '        at, missing = _columns(header, cols)\n'
        '        d.missing += [f"columna {c} en {name}" for c in missing]\n'
        '        if cols[0] in missing:\n'
        '            continue\n'
        '        cell = lambda row, c: row[at[c]].strip() if c in at else ""\n'
        '        for row in rows:\n'
        '            if _placeholder(row):\n'
        '                continue\n'
        '            if name == "Datos":\n'
        '                ent = _clean(cell(row, "Entidad"))\n'
        '                if not ent:\n'
        '                    continue\n'
        '                d.entities.append(Entity(name=ent, what=cell(row, "Qu\xe9 es"),\n'
        '                                         relations=_relations(cell(row, "Se relaciona con"), ent, d.warnings)))\n'
        '            else:\n'
        '                item = {_field_name(c): (_clean(cell(row, c)) if c in (cols[0], "D\xf3nde vive") else cell(row, c)) for c in cols}\n'
        '                if not item[_field_name(cols[0])]:\n'
        '                    continue\n'
        '                if name == "Conceptos":\n'
        '                    item["no_es"] = [x.strip() for x in _clean(item["no_es"]).split(",")\n'
        '                                     if x.strip() and not _placeholder([x])]\n'
        '                {"Reglas": d.rules, "Componentes": d.components, "Conceptos": d.concepts,\n'
        '                 "Infraestructura": d.infrastructure}[name].append(item)\n'
        '    names = {}\n'
        '    for e in d.entities:\n'
        '        if key(e.name) in names:\n'
        '            d.warnings.append(f"Datos: la entidad \xab{e.name}\xbb est\xe1 dos veces")\n'
        '        names.setdefault(key(e.name), e.name)\n'
        '    for e in d.entities:\n'
        '        for r in e.relations:\n'
        '            if key(r.target) not in names:\n'
        '                d.warnings.append(f"Datos, {e.name}: se relaciona con \xab{r.target}\xbb, que no es una entidad de la tabla")\n'
        '    return d\n'
        '\n'
        '\n'
        '# \u2500\u2500 the plan \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'PHASE_COLUMNS = ("Fase", "Qu\xe9 podr\xe1 hacer qui\xe9n", "Versi\xf3n", "Listo cuando", "Estado")\n'
        'PIECE_COLUMNS = ("Pieza", "Fase", "Qu\xe9 entrega", "Hecha cuando")\n'
        'PHASE_STATES = ("cerrada", "en curso", "pendiente")\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Phase:\n'
        '    id: str\n'
        '    name: str = ""\n'
        '    who_can: str = ""\n'
        '    version: str = ""\n'
        '    done_when: str = ""\n'
        '    state: str = ""                             # one of PHASE_STATES, or "" when it is not one\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Piece:\n'
        '    id: str\n'
        '    name: str = ""\n'
        '    phase: str = ""                             # the phase\'s id\n'
        '    delivers: str = ""\n'
        '    done_when: str = ""\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Plan:\n'
        '    phases: list = field(default_factory=list)\n'
        '    pieces: list = field(default_factory=list)\n'
        '    missing: list = field(default_factory=list)\n'
        '    warnings: list = field(default_factory=list)\n'
        '\n'
        '    def piece(self, ident: str) -> Optional[Piece]:\n'
        '        for p in self.pieces:\n'
        '            if p.id.casefold() == (ident or "").casefold():\n'
        '                return p\n'
        '        return None\n'
        '\n'
        '\n'
        'def read_plan(text: str) -> Plan:\n'
        '    """The plan\'s two tables (Fases, Piezas) by their section and column titles, and the expected sections or columns\n'
        '    it did not find. Warns on a repeated piece, a piece in a phase that is not in the table, a state that is not one of\n'
        '    the three and more than one phase in progress."""\n'
        '    secs = _sections(text)\n'
        '    pl = Plan()\n'
        '    for name, cols in (("Fases", PHASE_COLUMNS), ("Piezas", PIECE_COLUMNS)):\n'
        '        if key(name) not in secs:\n'
        '            pl.missing.append(f"secci\xf3n {name}")\n'
        '            continue\n'
        '        header, rows = _table(secs[key(name)][1])\n'
        '        if not header:\n'
        '            pl.missing.append(f"tabla de {name}")\n'
        '            continue\n'
        '        at, missing = _columns(header, cols)\n'
        '        pl.missing += [f"columna {c} en {name}" for c in missing]\n'
        '        if cols[0] in missing:\n'
        '            continue\n'
        '        cell = lambda row, c: row[at[c]].strip() if c in at else ""\n'
        '        for row in rows:\n'
        '            if _placeholder(row):\n'
        '                continue\n'
        '            ident, label = _ident(cell(row, cols[0]))\n'
        '            if not ident or _placeholder([ident]):\n'
        '                continue\n'
        '            if name == "Fases":\n'
        '                state = key(cell(row, "Estado"))\n'
        '                st = next((s for s in PHASE_STATES if key(s) == state), "")\n'
        '                if cell(row, "Estado") and not st:\n'
        '                    pl.warnings.append(f"Fases, {ident}: \xab{cell(row, \'Estado\')}\xbb no es cerrada, en curso ni pendiente")\n'
        '                pl.phases.append(Phase(id=ident, name=label, who_can=cell(row, "Qu\xe9 podr\xe1 hacer qui\xe9n"),\n'
        '                                       version=_clean(cell(row, "Versi\xf3n")), done_when=cell(row, "Listo cuando"), state=st))\n'
        '            else:\n'
        '                if pl.piece(ident):\n'
        '                    pl.warnings.append(f"Piezas: \xab{ident}\xbb est\xe1 dos veces; un identificador no se reutiliza")\n'
        '                    continue\n'
        '                pl.pieces.append(Piece(id=ident, name=label, phase=_ident(cell(row, "Fase"))[0],\n'
        '                                       delivers=cell(row, "Qu\xe9 entrega"), done_when=cell(row, "Hecha cuando")))\n'
        '    if sum(1 for f in pl.phases if f.state == "en curso") > 1:\n'
        '        pl.warnings.append("Fases: hay m\xe1s de una en curso")\n'
        '    phases = {f.id.casefold() for f in pl.phases}\n'
        '    for p in pl.pieces:\n'
        '        if pl.phases and p.phase and p.phase.casefold() not in phases:\n'
        '            pl.warnings.append(f"Piezas, {p.id}: la fase \xab{p.phase}\xbb no est\xe1 en Fases")\n'
        '    return pl\n'
        '\n'
        '\n'
        '# \u2500\u2500 the two configurations \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'STATES = ("cumple", "no cumple", "no aplica", "excepci\xf3n")\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class ConfigRow:\n'
        '    id: str                                     # PL1\u2026PL7, R1\u2026R7\n'
        '    what: str = ""\n'
        '    states: dict = field(default_factory=dict)  # column ("Estado", or a repository) -> {"estado", "fecha", "texto"}\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class ApprovedChange:\n'
        '    date: str\n'
        '    what: str\n'
        '    approved_by: str\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class Configuration:\n'
        '    kind: str = ""                              # "plataforma" | "repositorios" | ""\n'
        '    columns: list = field(default_factory=list) # the state columns: ["Estado"] or the repositories\n'
        '    rows: list = field(default_factory=list)\n'
        '    changes: list = field(default_factory=list) # \xabCambios aprobados\xbb, newest first as written\n'
        '    latest: str = ""                            # the most recent date of any state\n'
        '    oldest: str = ""                            # the oldest date of a row that is checked by date (\xabcumple\xbb, \xabno cumple\xbb)\n'
        '    unchecked: list = field(default_factory=list)  # \xabPL3\xbb or \xabR2 org/repo\xbb: cells with no state yet\n'
        '    missing: list = field(default_factory=list)\n'
        '    warnings: list = field(default_factory=list)\n'
        '\n'
        '\n'
        'def _state(cell: str) -> Optional[dict]:\n'
        '    c = _clean(cell)\n'
        '    if not c:\n'
        '        return None\n'
        '    m = DATE.search(c)\n'
        '    word = key(SEPARATOR.split(c, maxsplit=1)[0] if "\xb7" in c else DATE.sub("", c))\n'
        '    st = next((s for s in STATES if key(s) == word), "")\n'
        '    return {"estado": st, "fecha": m.group(1) if m else "", "texto": c}\n'
        '\n'
        '\n'
        'def read_configuration(text: str) -> Configuration:\n'
        '    """The rows PL and R of a configuration with each state and its date (\xabcumple \xb7 AAAA-MM-DD\xbb), and the table\n'
        "    \xabCambios aprobados\xbb. The platform's state column is \xabEstado\xbb; a repositories configuration has one column per\n"
        '    repository after \xabC\xf3mo se comprueba\xbb."""\n'
        '    cf = Configuration()\n'
        '    header, rows = None, []\n'
        '    body = _nfc(text)\n'
        '    secs = _sections(body)\n'
        '    # the main table is the first one whose first column is \xab#\xbb, outside \xabCambios aprobados\xbb\n'
        '    changes_block = secs.get(key("Cambios aprobados"), ("", ""))[1]\n'
        "    # cut by position, not by text: an empty section's block is \xab\\n\xbb, and replacing it removed every line break\n"
        '    # (review of 1.27.0, finding 26)\n'
        '    main = body\n'
        '    for mm in re.finditer(r"^## (.+)$", body, re.M):\n'
        '        if key(mm.group(1)) == key("Cambios aprobados"):\n'
        '            nxt = re.search(r"^## ", body[mm.end():], re.M)\n'
        '            main = body[:mm.start()] + (body[mm.end() + nxt.start():] if nxt else "")\n'
        '            break\n'
        '    for h, r in _tables(main):\n'
        '        if key(h[0]) == "":\n'
        '            header, rows = h, r\n'
        '            break\n'
        '    if header is None:\n'
        '        cf.missing.append("tabla con la columna #")\n'
        '    else:\n'
        '        at, missing = _columns(header, ("Qu\xe9 se cumple", "C\xf3mo se comprueba"))\n'
        '        cf.missing += [f"columna {c}" for c in missing]\n'
        '        if "Estado" in header or key("Estado") in (key(x) for x in header):\n'
        '            cf.kind, state_cols = "plataforma", [i for i, h in enumerate(header) if key(h) == key("Estado")][:1]\n'
        '        else:\n'
        '            cf.kind = "repositorios"\n'
        '            after = at.get("C\xf3mo se comprueba", 1)\n'
        '            state_cols = list(range(after + 1, len(header)))\n'
        '            if not state_cols:\n'
        '                cf.missing.append("columna de un repositorio")\n'
        '        cf.columns = [_clean(header[i]) for i in state_cols]\n'
        '        for row in rows:\n'
        '            ident = _clean(row[0])\n'
        '            if not re.match(r"^(PL|R)\\d+$", ident, re.I):\n'
        '                continue\n'
        '            cr = ConfigRow(id=ident.upper(), what=row[at["Qu\xe9 se cumple"]].strip() if "Qu\xe9 se cumple" in at else "")\n'
        '            for i in state_cols:\n'
        '                st = _state(row[i])\n'
        '                cr.states[_clean(header[i])] = st\n'
        '                if st and not st["estado"] and not _placeholder([row[i]]):\n'
        '                    cf.warnings.append(f"{cr.id}, {_clean(header[i])}: \xab{st[\'texto\']}\xbb no es cumple, no cumple, no aplica ni excepci\xf3n")\n'
        '                elif st and st["estado"] in ("cumple", "no cumple") and not st["fecha"]:\n'
        '                    cf.warnings.append(f"{cr.id}, {_clean(header[i])}: \xab{st[\'estado\']}\xbb sin fecha")\n'
        '                if st and st["fecha"] > cf.latest:\n'
        '                    cf.latest = st["fecha"]\n'
        '                if st and st["fecha"] and (not cf.oldest or st["fecha"] < cf.oldest):\n'
        '                    cf.oldest = st["fecha"]\n'
        '                if st is None or _placeholder([row[i]]):\n'
        '                    cf.unchecked.append(cr.id + ("" if cf.kind == "plataforma" else " " + _clean(header[i])))\n'
        '            cf.rows.append(cr)\n'
        '    if changes_block or key("Cambios aprobados") in secs:\n'
        '        h, r = _table(changes_block)\n'
        '        at, missing = _columns(h, ("Fecha", "Qu\xe9 cambi\xf3", "Aprob\xf3"))\n'
        '        if h:\n'
        '            cf.missing += [f"columna {c} en Cambios aprobados" for c in missing]\n'
        '        if not missing:\n'
        '            for row in r:\n'
        '                if not _placeholder(row):\n'
        '                    cf.changes.append(ApprovedChange(_clean(row[at["Fecha"]]), row[at["Qu\xe9 cambi\xf3"]].strip(),\n'
        '                                                     _clean(row[at["Aprob\xf3"]])))\n'
        '    elif cf.kind == "plataforma":\n'
        '        cf.missing.append("secci\xf3n Cambios aprobados")\n'
        '    return cf\n'
        '\n'
        '\n'
        '# \u2500\u2500 the status of each piece \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        'PENDING, IN_PROGRESS, MERGED, DELIVERED = "pendiente", "en curso", "unida", "entregada"\n'
        '_ORDER = {PENDING: 0, IN_PROGRESS: 1, MERGED: 2, DELIVERED: 3}\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class PullRequest:\n'
        '    """A pull request as the caller read it from GitHub. `state`: "open", "closed" (without merging) or "merged"."""\n'
        '    repo: str\n'
        '    number: int\n'
        '    title: str\n'
        '    state: str\n'
        '    author: str = ""\n'
        "    bot: bool = False                           # GitHub's user type \xabBot\xbb, or a login ending in \xab[bot]\xbb\n"
        '    merge_commit: str = ""\n'
        "    to_main: bool = True                        # its base is the repository's main branch; the others are steps inside a block\n"
        '    merged_at: str = ""                         # ISO; orders a piece\'s merges, so a revert merged last is seen\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class PieceStatus:\n'
        '    id: str\n'
        '    status: str                                 # PENDING | IN_PROGRESS | MERGED | DELIVERED\n'
        '    pull_requests: list = field(default_factory=list)      # \xabrepo#number\xbb that count\n'
        '    reverted: bool = False                      # its last merged pull request is a revert: what it delivered is undone\n'
        '\n'
        '\n'
        '@dataclass\n'
        'class PieceReport:\n'
        "    pieces: list = field(default_factory=list)             # [PieceStatus], in the plan's order\n"
        '    outside_plan: list = field(default_factory=list)       # [PullRequest] without a piece, or with one not in the plan\n'
        '    ignored: list = field(default_factory=list)            # [PullRequest] closed without merging, or from bots\n'
        '\n'
        '\n'
        'def _pieces_of(title: str) -> list:\n'
        '    """The identifiers a pull request\'s title starts with, followed by \xab \xb7 \xbb: one (\xabP03 \xb7 \u2026\xbb), or the pieces of a block\n'
        '    joined by \xab + \xbb (\xabP01 + P02 \xb7 \u2026\xbb, tecnologia/metodologia-desarrollo#2026-11-18-12). A GitHub revert (\xabRevert "P03 \xb7\n'
        '    \u2026"\xbb) carries its pieces. [] when there is none."""\n'
        '    t, _ = _unwrap_reverts(title)\n'
        '    m = re.match(r"^([^\\s\xb7+]+(?:\\s*\\+\\s*[^\\s\xb7+]+)*)\\s+\xb7\\s+\\S", t)\n'
        '    return [x.strip() for x in m.group(1).split("+")] if m else []\n'
        '\n'
        '\n'
        'def _unwrap_reverts(title: str) -> tuple:\n'
        '    """(the innermost title, how many \xabRevert "\u2026"\xbb wrap it). Reverting a revert, GitHub\'s way of putting it back,\n'
        '    nests them (\xabRevert "Revert "P01 \xb7 a""\xbb)."""\n'
        '    t, n = _nfc(title).strip(), 0\n'
        '    while True:\n'
        '        m = re.match(r\'^Revert\\s+"(.*)"$\', t) or re.match(r\'^Revert\\s+"(.*)$\', t)\n'
        '        if not m:\n'
        '            return t, n\n'
        '        t, n = m.group(1).strip(), n + 1\n'
        '\n'
        '\n'
        'def _is_revert(title: str) -> bool:\n'
        '    """An odd number of \xabRevert\xbb undoes the piece; an even number puts it back (review of 1.27.0, fixes 1, finding 15)."""\n'
        '    return _unwrap_reverts(title)[1] % 2 == 1\n'
        '\n'
        '\n'
        'def _is_bot(pr: PullRequest) -> bool:\n'
        '    return pr.bot or pr.author.lower().endswith("[bot]")\n'
        '\n'
        '\n'
        'def piece_status(plan: Plan, pull_requests: Iterable[PullRequest],\n'
        '                 delivered: Optional[Mapping[str, Iterable[int]]] = None) -> PieceReport:\n'
        '    """Each piece\'s status by the rule of tecnologia/metodologia-desarrollo#2026-11-18-10 and -12, from pull requests\n'
        '    already read. `delivered` maps a repository to the numbers of its merged pull requests inside its last step to Prod\n'
        '    (the caller works that out from the release or tag \xabPaso a Prod\xbb leaves); without it no piece is delivered.\n'
        '\n'
        "    Only pull requests into the main branch count: those into another branch are steps inside a block (-12). A block's\n"
        '    pull request counts for every piece its title names. With several pull requests the least advanced decides. A pull\n'
        "    request closed without merging does not count, and neither do bots'. One without a piece, or naming a piece the plan\n"
        '    does not have, is outside the plan. A piece whose last merged pull request is a revert is in progress again, with\n'
        '    `reverted`."""\n'
        '    inside = {r.lower(): {int(n) for n in nums} for r, nums in (delivered or {}).items()}\n'
        '    by_piece: dict = {p.id.casefold(): [] for p in plan.pieces}\n'
        '    rep = PieceReport()\n'
        '    for pr in pull_requests:\n'
        '        if pr.state not in ("open", "merged") or _is_bot(pr) or not pr.to_main:\n'
        '            rep.ignored.append(pr)\n'
        '            continue\n'
        '        idents = _pieces_of(pr.title)\n'
        '        if not idents or any(i.casefold() not in by_piece for i in idents):\n'
        '            rep.outside_plan.append(pr)\n'
        '            continue\n'
        '        for i in dict.fromkeys(x.casefold() for x in idents):\n'
        '            by_piece[i].append(pr)\n'
        '    for p in plan.pieces:\n'
        '        prs = by_piece[p.id.casefold()]\n'
        '        if not prs:\n'
        '            status = PENDING\n'
        '        else:\n'
        '            def one(pr):\n'
        '                if pr.state == "open":\n'
        '                    return IN_PROGRESS\n'
        '                return DELIVERED if pr.number in inside.get(pr.repo.lower(), ()) else MERGED\n'
        '            status = min((one(pr) for pr in prs), key=_ORDER.get)\n'
        "        # a revert merged after the piece's other merges undoes it: the piece is back in progress (finding 15)\n"
        '        merged = sorted((pr for pr in prs if pr.state == "merged"), key=lambda pr: (pr.merged_at, pr.number))\n'
        '        reverted = bool(merged) and _is_revert(merged[-1].title)\n'
        '        if reverted:\n'
        '            status = IN_PROGRESS\n'
        '        rep.pieces.append(PieceStatus(p.id, status, [f"{pr.repo}#{pr.number}" for pr in prs], reverted))\n'
        '    return rep\n'
        '\n'
        '\n'
        '# \u2500\u2500 out \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n'
        '\n'
        '_ENTRY = re.compile(r"(?m)^(?=## 20\\d\\d-\\d\\d-\\d\\d)")\n'
        '_READ = re.compile(r"^Le\xeddo\\b[^:\\n]*:.*[\\w.-]+/[\\w.-]+ en `[0-9a-f]{7,40}`", re.M)\n'
        '\n'
        '\n'
        'def follow_up_entries(text: str) -> list:\n'
        '    """The real entries of a follow-up file, newest first, as dicts with \xabdate\xbb, \xabrepos\xbb (lower-case owner/name read)\n'
        '    and \xabwhole\xbb (it has no \xabSin comprobar:\xbb line: everything that applied was read whole). A real entry has its \xabLe\xeddo:\xbb\n'
        "    line with each repository's commit; a hand-written note does not count, and neither does one marked \xab**Incompleto,\n"
        '    no se guarda:**\xbb. One rule for the follow-up script and the opening (plugin-memoria#2026-11-19-5)."""\n'
        '    body = text or ""\n'
        '    if body.startswith("---\\n") and "\\n---\\n" in body[4:]:\n'
        '        body = body[body.index("\\n---\\n", 4) + 5:]\n'
        '    out = []\n'
        '    for e in _ENTRY.split(body):\n'
        '        m = re.match(r"## (20\\d\\d-\\d\\d-\\d\\d)\\b", e)\n'
        '        read = _READ.search(e)\n'
        '        if not m or not read or re.search(r"^\\*\\*Incompleto, no se guarda:\\*\\*", e, re.M):\n'
        '            continue\n'
        '        out.append({"date": m.group(1),\n'
        '                    "repos": [x.lower() for x in re.findall(r"([\\w.-]+/[\\w.-]+) en `[0-9a-f]{7,40}`", read.group(0))],\n'
        '                    "whole": bool(re.search(r"^Compar\xf3:", e, re.M)) and not re.search(r"^Sin comprobar:", e, re.M)})\n'
        '    return out\n'
        '\n'
        '\n'
        'def as_dict(obj):\n'
        '    """Any result of this module as plain dicts and lists, for the board\'s JSON."""\n'
        '    return dataclasses.asdict(obj) if dataclasses.is_dataclass(obj) else obj\n'
        '\n'
        '\n'
        "# the specification's names (especificacion-version-plugin-kit-desarrollo.md, 3.2)\n"
        'seccion_desarrollo = development_section\n'
        'piezas_faltantes = missing_pieces\n'
        'leer_diseno = read_design\n'
        'leer_plan = read_plan\n'
        'leer_configuracion = read_configuration\n'
        'estado_piezas = piece_status\n'
        'entradas_seguimiento = follow_up_entries\n'
    ),
    }
    for _n in _todo:
        _m = _t.ModuleType("context_core." + _n); _m.__package__ = "context_core"; _m.__fingerprint__ = _fp[_n]
        _s.modules[_m.__name__] = _m
        exec(compile(_src[_n], "<context_core/" + _n + ".py>", "exec"), _m.__dict__)
        setattr(_pkg, _n, _m)
_context_core()
# --- end of context_core ---
from context_core.compat import (CORREO, registro_personas, persona, nombres_de, fila_cuentas,  # noqa: E402
                                 nombre_contexto, cuentas_contexto, colaboran_en, sin_carpeta,
                                 con_archivados, respuestas_viejas, area_restringida, personas_en_area,
                                 es_sesion, es_mantenimiento, arreglados, rastro_mantenimiento,
                                 descontado)
from context_core.minimum import puerta_de_escritura, RECETA_ACTUALIZAR, VERSION_MINIMA_ESTRUCTURA  # noqa: E402
from context_core.development import (entradas_seguimiento, seccion_desarrollo, piezas_faltantes, leer_diseno, leer_plan,  # noqa: E402
                                      leer_configuracion, PATH_KEYS as CLAVES_KIT, FOLLOW_UP as SEGUIMIENTO_KIT)
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
    # una persona con dos cuentas («cuentas: a@, b@» en «Quién es quién») sigue siendo una (1.26.1): se cuentan
    # personas, no correos; un correo que la tabla no da a nadie cuenta como una persona más
    quien = {c: n for n, cs in por_nombre.items() for c in cs}
    pa, pc = {quien.get(c, c) for c in ca}, {quien.get(c, c) for c in cc}
    if len(pa) > 1 or len(na) > 1:
        return "dos", adm, ctx
    if ca and cc:
        return ("una" if pa & pc else "dos"), adm, ctx
    if na and nc:
        return ("una" if na == nc else "dos"), adm, ctx
    return "no se sabe", adm, ctx
# --- fin del administrador principal ---


# ---------- nivel 0 ----------
try:
    with open(RAIZ / "metodo.md", encoding="utf-8-sig", errors="replace") as f_:
        linea_metodo = f_.readline().strip()
except OSError:
    linea_metodo = "(sin metodo.md)"
guia = leer(RAIZ / "guia.md") or ""
print("=== METODO (primera línea)")
print(linea_metodo)
if RAIZ_RESUELTA:   # se pasó la ruta de la computadora: se dice cuál es la de la consola, que es la que vale para leer y escribir
    print(f"RAIZ: {RAIZ} · la carpeta en esta consola; todo lo que se lea o escriba aquí va con esta ruta, nunca con la de get_device_info")
print(f"HOY: {HOY.isoformat()} · zona {getattr(TZ, 'key', TZ)} · la fecha de todo lo que se escribe hoy en la carpeta; no la del reloj de la consola ni del contenedor, que van en UTC")

def version_huella(linea):
    """(tupla de la versión, huella) de una primera línea de metodo.md; (None, None) si no la trae."""
    m = re.search(r"versi[oó]n\s+(\d+(?:\.\d+)*)", linea or "", re.I)
    h = re.search(r"huella\s+([0-9a-f]+)", linea or "", re.I)
    return (tuple(int(x) for x in m.group(1).split(".")) if m else None), (h.group(1) if h else None)

if PLUGIN is not None:
    vr, hr = version_huella(linea_metodo)
    vp, hp = version_huella(PLUGIN)
    txt = lambda v: ".".join(map(str, v)) if v else "sin versión"
    if not vp:
        ver = "SIN VEREDICTO: la línea del plugin no trae versión"
    elif not vr or vp > vr or (vp == vr and not hr):
        ver = "RAIZ ATRASADA: se copia el metodo.md del plugin"
    elif vp < vr:
        ver = "PLUGIN ATRASADO: no se copia nada; se avisa de que la carpeta usa una versión más nueva"
    elif hr == hp:
        ver = "AL DIA"
    else:
        ver = "MISMA VERSION, HUELLA DISTINTA: no se toca"
    print(f"Veredicto: {ver} (raíz {txt(vr)}, plugin {txt(vp)})")
    VEREDICTO = ver.split(":")[0]
    VERSION_RAIZ, VERSION_PLUGIN = txt(vr), txt(vp)
# la versión mínima del plugin que puede escribir en la raíz, de su guia.md (1.26): por debajo, la sesión lee pero no escribe
PUEDE_ESCRIBIR, VERSION_MINIMA, MOTIVO_SOLO_LECTURA = puerta_de_escritura(ESTE_PLUGIN, guia)
if VERSION_MINIMA or not PUEDE_ESCRIBIR:
    print(f"ESCRITURA: {'abierta' if PUEDE_ESCRIBIR else 'SOLO LECTURA'} (plugin {ESTE_PLUGIN}, mínima de la raíz {VERSION_MINIMA or 'ilegible'})")
m_org = re.search(r"^#\s+(.+)$", guia, re.M)
ORGANIZACION = m_org.group(1).split("·")[0].strip() if m_org else ""
if MINIMA:
    titulo("ORGANIZACION")
    print(ORGANIZACION or "(guia.md sin título)")
else:
    titulo("GUIA")
    # la receta para conectarse y la nota de la versión son para personas: no hacen falta para trabajar (1.19)
    omitidas, guia_sesion = [], guia
    for sec in ("Quién es quién", "Cómo conectarte", "Versión del método", "Versión mínima del plugin"):   # «Quién es quién» lo leen los scripts; la cuenta de la sesión sale en CUENTA (1.25); la versión mínima, en ESCRITURA (1.26)
        m_ = re.search(r"^##\s+" + re.escape(sec) + r"\s*$.*?(?=^##\s|\Z)", guia_sesion, re.M | re.S)
        if m_:
            guia_sesion = guia_sesion[:m_.start()] + guia_sesion[m_.end():]; omitidas.append(sec)
    print(guia_sesion.strip())
    if omitidas:
        print(f"(se omiten {' y '.join('«' + s + '»' for s in omitidas)}: si hacen falta, se leen en guia.md)")

def columnas_areas(cab):
    """Dónde está cada columna de la tabla de áreas, por su encabezado: la 1.22 dice «Responsable» y añade «Acceso»;
    hasta la 1.21, «Dueño» y sin «Acceso». Sin encabezado reconocible, las posiciones de siempre."""
    n = [re.sub(r"[*_`]", "", x).strip().lower() for x in cab]
    def pos(*nombres, defecto=None):
        return next((i for i, x in enumerate(n) if x in nombres), defecto)
    return {"responsable": pos("responsable", "dueño", "dueno", defecto=2), "cuenta": pos("cuenta", "colabora", defecto=3),
            "lectores": pos("quién la lee", "quien la lee", defecto=4), "acceso": pos("acceso")}


# Si un área está restringida lo dice area_restringida(fila, encabezado), de context_core (arriba): con columna «Acceso»
# (1.22), restringida si dice «Restringida» y abierta si dice «Abierta»; con otra cosa o vacía, restringida si la tabla
# tiene «Colabora» (1.25), y si no, la regla de «Quién la lee» de la 1.21: nunca se falla abierto. La misma regla en el
# tablero, permisos.py, migrar_estructura.py y verificar.sh (1.25.3).


areas = []
filas = seccion(guia, "Áreas").split("\n")
col_areas = None
cab_areas = None
REG = registro_personas(guia)
AVISOS_FILA = set()
guia_anterior = False
for l in filas:
    if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
        continue
    c = [x.strip() for x in l.strip().strip("|").split("|")]
    if col_areas is None:
        col_areas = columnas_areas(c); cab_areas = c
        guia_anterior = col_areas["acceso"] is None or any(re.sub(r"[*_`]", "", x).strip().lower() in ("dueño", "dueno") for x in c)
        continue
    minimo = max(v for v in col_areas.values() if v is not None) + 1
    if len(c) >= minimo:
        de, co, av = fila_cuentas(cab_areas, c, REG)
        if av:
            if av not in AVISOS_FILA:
                print(f"(aviso: la fila de «{c[0].strip('`')}» en la tabla de áreas de guia.md: {av})" if "no tiene «Quién es quién»" not in av else f"(aviso: {av}: nadie escribe en ninguna área hasta que se añada)")
            AVISOS_FILA.add(av if "no tiene «Quién es quién»" in av else c[0] + av)
        areas.append({"slug": c[0].strip("`").rstrip("/"), "dueno": c[col_areas["responsable"]], "cuentas_dueno": de, "colaboran": co,
                      "restringida": area_restringida(c, cab_areas), "lectores": c[col_areas["lectores"]],
                      "en_celda": set(CORREO.findall(c[col_areas["cuenta"]].lower())) | {x for n in nombres_de(c[col_areas["responsable"]] + "," + c[col_areas["cuenta"]]) for x in ((persona(n, REG) or {}).get("cuentas") or set())}, "aviso": av})
    else:
        print(f"(aviso: la fila «{c[0].strip('`')}» de la tabla de áreas de guia.md tiene {len(c)} columnas y hacen falta {minimo}; esa área no se lee hasta que se corrija)")
if ZONA_AVISO:
    print(f"(aviso: {ZONA_AVISO})")
if not areas:
    print("(aviso: no se encontró ninguna área en la sección «## Áreas» de guia.md: sin ella nadie tiene área ni cuenta; que el responsable de contexto revise guia.md)")
# como el tablero: la línea que empieza por «Contexto común», cortada por su primer «:» (la plantilla de `nuevo` escribe
# «Contexto común (`guia.md` y `base/`): Nombre (correo).»); sin correo, la cuenta del responsable es la de las áreas
# de las que es responsable
resp_contexto = ""
for l in seccion(guia, "Quién responde por qué").split("\n"):
    if l.strip().lower().lstrip("-* ").startswith("contexto común"):
        resp_contexto = l.split(":", 1)[-1].strip().rstrip(".").strip()
# la cuenta del responsable va entre paréntesis en esa misma línea («Contexto común: Nombre (correo)»); sin ella,
# como antes, es la de las áreas de las que esa persona es responsable
cuenta_resp = cuentas_contexto(resp_contexto, REG)
if REG["hay"] and resp_contexto and not cuenta_resp:
    print(f"(aviso: «Contexto común» de guia.md nombra a «{nombre_contexto(resp_contexto)}», que no está en «Quién es quién»: nadie responde por guia.md ni base/ hasta que se corrija)")
resp_contexto = re.sub(r"\s*\([^)]*\)", "", resp_contexto).strip()
# el nombre de la celda sin lo que va entre paréntesis, como migrar_estructura.py: los dos tienen que reconocer a la misma persona
es_resp = bool(CUENTA) and (CUENTA in cuenta_resp or (bool(resp_contexto) and not cuenta_resp and any(CUENTA in a["cuentas_dueno"] and re.sub(r"\s*\([^)]*\)", "", a["dueno"]).strip().lower() == resp_contexto.lower() for a in areas)))

premisas = []
for l in (leer(RAIZ / "base" / "premisas.md") or "").split("\n"):
    m = re.match(r"^\s*-\s*(P\d+)\s*·\s*(.+)$", l)
    if m:
        partes = [x.strip() for x in m.group(2).split("·")]
        r = next((re.search(r"P\d+", x, re.I).group(0).upper() for x in partes[1:] if re.match(r"reemplaza\b", x, re.I) and re.search(r"P\d+", x, re.I)), None)
        f = next((x for x in partes[1:] if re.fullmatch(r"20\d\d-\d\d-\d\d", x)), "")
        premisas.append((m.group(1).upper(), l.strip(), r, f))
reemplazadas = {r for _, _, r, _ in premisas if r}
if not MINIMA:
    titulo("PREMISAS VIGENTES")
    print("\n".join(l for pid, l, _, _ in premisas if pid not in reemplazadas) or "(no hay base/premisas.md o no tiene premisas)")

if CUENTA:
    titulo("CUENTA")
    mias = [a["slug"] for a in areas if CUENTA in a["cuentas_dueno"]]
    colab = [a["slug"] for a in areas if CUENTA in a["colaboran"] and CUENTA not in a["cuentas_dueno"]]
    proy_co = []
    if ACTIVO and "/" in ACTIVO and ACTIVO.split("/")[0] not in mias + colab:
        tp_ = leer(RAIZ / ACTIVO / "proyecto.md")
        if tp_ and CUENTA in colaboran_en(seccion(cabecera(tp_)[1], "Quién participa"), REG if REG["hay"] else None):
            proy_co = [ACTIVO]
    donde_ = ", ".join([f"{s} (responsable)" for s in mias] + [f"{s} (colabora)" for s in colab] + [f"{s} (colabora en el proyecto)" for s in proy_co])
    if not donde_ and PUEDE_ESCRIBIR:
        DECIR.append("No escribes en ninguna área: dime en cuál trabajas.")
    if not PUEDE_ESCRIBIR:   # la versión mínima manda sobre todo lo demás: con un plugin anterior no se escribe en ningún sitio (1.26)
        donde_ = "nada: SOLO LECTURA por la versión mínima del plugin (ESCRITURA, arriba)" + (f"; con un plugin al día, en {donde_}" if donde_ else "")
    print(f"{CUENTA}: escribe en {donde_ if donde_ else 'ninguna área (preguntar en cuál trabaja antes de escribir)'}"
          + ("; es la del responsable de contexto (también guia.md y base/)" if es_resp else ""))
    # «Quién es quién» (1.25): el nombre de la cuenta sale del registro, y «Sesión de:» lo lleva sin preguntarlo
    if REG["hay"]:
        _yo = REG["cuenta"].get(CUENTA)
        if _yo and _yo["nombre"] != "?" and not _yo["compartida"]:
            if not MINIMA:   # la mínima no cierra sesión: el nombre lo da la apertura del proyecto
                print(f"NOMBRE {_yo['nombre']} (de «Quién es quién»: es el de «Sesión de:», sin preguntarlo)")
        elif _yo and _yo["compartida"]:
            if not MINIMA:
                print(f"NOMBRE (la cuenta la comparten {_yo['nombre']} y {_yo['compartida']}: «Sesión de:» lleva el de quien trabaja hoy, que se pregunta)")
        elif _yo:
            DECIR.append(f"Tu cuenta está en «Quién es quién» de guia.md sin nombre («? · {CUENTA}»): dime tu nombre y se lo paso al responsable de contexto.")
        elif proy_co:
            DECIR.append(f"Escribes en {proy_co[0]} por su línea «Colabora:» (alta provisional); tu cuenta {CUENTA} todavía no está en «Quién es quién» de guia.md, y la añade el responsable de contexto.")
        elif not _yo:
            DECIR.append(f"Tu cuenta {CUENTA} no está en «Quién es quién» de guia.md, así que no escribes en ninguna área hasta que el responsable de contexto la añada (si tu línea tiene un error en la cuenta, es ahí donde se corrige). Dime en qué área trabajas y te preparo el texto para pasárselo.")
        if _yo and _yo["baja"]:
            DECIR.append(f"Tu línea de «Quién es quién» dice «baja»: no escribes en ninguna área de esta carpeta.")
        if es_resp:
            _pend = [p_["nombre"] for p_ in REG["personas"] if p_["sin_confirmar"]]
            _sinn = [sorted(p_["cuentas"])[0] for p_ in REG["personas"] if p_["nombre"] == "?" and p_["cuentas"]]
            for _av in REG["avisos"]:
                DECIR.append(f"En «Quién es quién» de guia.md: {_av}.")
            if _sinn:
                DECIR.append(f"En «Quién es quién», {len(_sinn)} cuenta(s) sin nombre ({', '.join(_sinn)}): escriben donde la tabla pone su correo, y hay que ponerles el nombre de la persona.")
            if _pend:
                DECIR.append(f"En «Quién es quién», «sin confirmar»: {', '.join(_pend)}. Cuando esa persona haya abierto sesión con esa cuenta (su «Sesión de:» en un proyecto, o que te lo confirme), quitas la marca de su línea.")
    # el administrador principal es una sola persona (1.22.2): se le dice al responsable de contexto si guia.md nombra a dos
    _ver, _adm, _ctx = administrador_unico(seccion(guia, "Quién responde por qué"), {**{re.sub(r"\s*\([^)]*\)", "", a["dueno"]).split(",")[0].strip().lower(): a["cuentas_dueno"] for a in areas if a["cuentas_dueno"]},
                                         **{k: set(p_["cuentas"]) for k, p_ in REG["nombre"].items() if p_["cuentas"] and not p_["baja"]}})
    if es_resp and _ver == "dos":
        DECIR.append(f"guia.md nombra a dos personas: «{_adm}» administra la carpeta y «{_ctx}» responde por el contexto. Son una sola, la dueña de la carpeta en Drive, que lo lee todo y migra todas las áreas. Se corrige en «Quién responde por qué».")
    # el primer párrafo de guia.md es lo que el tablero enseña arriba de Inicio: si sigue con la plantilla o vacío, se le dice a
    # quien lo escribe (revisión de la 1.22.4, hallazgo 7). Las mismas reglas que generar_vista.py
    if es_resp:
        _cuerpo = re.sub(r"^\s*#[^\n]*\n", "", re.sub(r"\A---\n.*?\n---\n", "", guia, count=1, flags=re.S), count=1)
        _p1 = next((b.strip() for b in re.split(r"\n\s*\n", _cuerpo.strip()) if b.strip() and not b.strip().startswith(("|", "- "))), "")
        _p1 = re.sub(r"\*\*([^*]+)\*\*", r"\1", re.sub(r"<!--.*?-->", "", _p1, flags=re.S)).strip()
        _frases = sin_carpeta(re.split(r"(?<=[.!?])\s+", _p1))
        if (not _p1 or _p1.startswith(("#", ">", "*", "```", "|")) or re.match(r"^\d+[.)]\s", _p1) or re.match(r"^Esta carpeta es la memoria de trabajo de\b", _p1)
                or re.search(r"\[(?:[^\]\n]*\s[^\]\n]*|[Oo]rganizaci[oó]n)\](?![(\[])", _p1) or not " ".join(_frases).strip()):
            DECIR.append("El primer párrafo de guia.md no dice qué es la organización, y el tablero no enseña nada arriba de Inicio. Se escribe en una o dos frases, a qué se dedica y para quién, sin hablar de la carpeta (lo de la carpeta pasa al segundo párrafo); lo escribes tú, con tu sí al texto.")
    # la revisión de permisos se ofrece al abrir (1.24.2, decidido el 2026-10-30): solo al administrador principal y solo si
    # la raíz vive en Google Drive (la ruta de --origen, con consola o sin ella). La fecha
    # de la última revisión vive en el tablero (meta/permisos), no en la carpeta: la mira la sesión, no este script
    if es_resp and en_drive(ORIGEN):
        PERMISOS = True
        print("PERMISOS: la raíz vive en Google Drive y esta cuenta la administra (qué se hace con esto: la sección RESPUESTA, o «Permisos de Drive» en la skill)")
    # la cuenta está en la celda de un área pero la celda no se deja leer (dos correos sin «colabora:», por ejemplo):
    # se dice cuál y cómo se escribe, para que no parezca un fallo y lo corrija quien lleva guia.md
    for a in areas:
        if a["aviso"] and CUENTA in a["en_celda"] and CUENTA not in a["cuentas_dueno"] | a["colaboran"]:
            DECIR.append(f"Tu cuenta está en la fila de «{a['slug']}» en guia.md pero no cuenta como tuya ({a['aviso']}). " + ("Responsable y Colabora llevan nombres de «Quién es quién»" if REG["hay"] else "Se escribe «correo del responsable · colabora: otro@…, otro@…»") + "; la corrige el responsable de contexto, y mientras tanto dime en qué área trabajas.")


def solo_nombre(d):
    """El responsable sin las notas entre paréntesis de su celda («Ana (escribe también Beto…)»), que empiezan en minúscula;
    «Dirección (Ana, Beto)» se queda. Como el tablero."""
    return re.sub(r"\s*\((?=[a-záéíóúñ`])[^)]*\)", "", d or "").strip()


# ---------- la estructura de la 1.22 ----------
# La misma función en migrar_estructura.py, que renombra justo lo que esta detecta; probar_migrar.py comprueba que coinciden.
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


def area_anterior(slug):
    """Cierto si el área (su area.md, o algún proyecto con proyecto.md dentro) tiene todavía la estructura de la 1.21.
    Un area.md con «Responsable:» en «Quién participa» y ninguna marca vieja se da por migrada sin bajar a sus proyectos:
    solo la migración o un área creada con la 1.22 lo escriben, y la migración escribe area.md la última, solo si todos
    sus proyectos quedaron migrados. Así la apertura no lee todos los proyecto.md de una raíz migrada (1.22.1). Con
    «Estatus» no basta: un cierre 1.22 lo escribe también en un área sin migrar."""
    t = leer(RAIZ / slug / "area.md")
    cuerpo = cabecera(t)[1] if t else ""
    if t and marcas_anteriores(cuerpo, "area"):
        return True
    if t and re.search(r"^\s*[-*]?\s*\**\s*Responsable(?: y colaboradores)?\s*\**\s*:", seccion(cuerpo, "Quién participa"), re.M):
        return False   # «Responsable y colaboradores: en … guia.md» lo deja la migración de las personas (1.26)
    try:
        proyectos = sorted(d for d in (RAIZ / slug).iterdir() if d.is_dir() and not d.name.startswith(".") and (d / "proyecto.md").is_file())
    except OSError:
        return False
    for d in proyectos:
        if marcas_anteriores(cabecera(leer(d / "proyecto.md") or "")[1], "proyecto") or any((d / f).is_file() for f in ARCHIVOS_ANTERIORES):
            return True
    return False


EN_USO_MIN = 120   # como migrar_estructura.py: un proyecto ajeno tocado hace menos puede estar en sesión en otra computadora


def area_en_uso(slug):
    """Cierto si todo lo que queda por migrar en el área (los proyectos con marcas viejas) lo tocó alguien hace menos de
    EN_USO_MIN minutos: la migración lo dejaría igual, así que no se ofrece ahora y se dice. Sin fechas (la copia), falso."""
    if SIN_FECHAS:
        return False
    try:
        proyectos = [d for d in (RAIZ / slug).iterdir() if d.is_dir() and not d.name.startswith(".") and (d / "proyecto.md").is_file()]
    except OSError:
        return False
    viejos = [d for d in proyectos if marcas_anteriores(cabecera(leer(d / "proyecto.md") or "")[1], "proyecto") or any((d / f).is_file() for f in ARCHIVOS_ANTERIORES)]
    def tocado(d):
        for n in ("proyecto.md", "sesiones.md"):
            try:
                t = os.stat(d / n).st_mtime
            except OSError:
                continue
            if t > time.time() + 60 or time.time() - t < EN_USO_MIN * 60:
                return True
        return False
    return bool(viejos) and all(tocado(d) for d in viejos)


titulo("ESTRUCTURA")
ESTRUCTURA_ANTERIOR = ""
PERSONAS_ANTERIOR = ""
VERSION_MINIMA_FALTA = False   # una raíz con «Quién es quién» que todavía no pide el plugin de esa estructura

if not CUENTA:
    print("Veredicto: SIN CUENTA")
else:
    # el responsable de contexto migra también las áreas de otros responsables (1.22.1), las que su carpeta deja leer
    propias_viejas = [a["slug"] for a in areas if CUENTA in a["cuentas_dueno"] and area_anterior(a["slug"])]
    # la misma regla que migrar_estructura.py: todas las áreas con carpeta, restringidas incluidas
    ajenas_viejas, ajenas_en_uso = [], []
    for a in areas:
        if es_resp and CUENTA not in a["cuentas_dueno"] and (RAIZ / a["slug"]).is_dir() and area_anterior(a["slug"]):
            (ajenas_en_uso if area_en_uso(a["slug"]) else ajenas_viejas).append(f"{a['slug']} (de {solo_nombre(a['dueno']) or 'otro responsable'})")
    guia_vieja = es_resp and guia_anterior
    if propias_viejas or ajenas_viejas or guia_vieja:
        ESTRUCTURA_ANTERIOR = ", ".join(propias_viejas + ajenas_viejas + (["guia.md"] if guia_vieja else []))
        print("Veredicto: ANTERIOR en " + ESTRUCTURA_ANTERIOR
              + " · se pregunta antes de responder («La estructura» en la skill sesion)")
    else:
        print("Veredicto: AL DIA")
    # las personas (1.26): la guía sin «Quién es quién» la migra el responsable de contexto, con todas las áreas; con el
    # registro ya en guia.md, cada responsable migra el «Quién participa» de sus area.md en su apertura
    _gm = REG["hay"] and not any(re.sub(r"[*_`]", "", x).strip().lower() == "cuenta" for x in (cab_areas or []))
    _vm = VERSION_MINIMA and tuple(int(x) for x in VERSION_MINIMA.split(".")) >= tuple(int(x) for x in VERSION_MINIMA_ESTRUCTURA.split("."))
    if es_resp and not _gm:
        PERSONAS_ANTERIOR = "guia.md"
    elif es_resp and _gm and PUEDE_ESCRIBIR and not _vm:
        # montada ya con «Quién es quién» (1.25), o migrada a mano: falta que pida el plugin que la lee (revisión de la 1.26)
        PERSONAS_ANTERIOR, VERSION_MINIMA_FALTA = "guia.md", True
    if _gm and not PERSONAS_ANTERIOR:
        PERSONAS_ANTERIOR = ", ".join(a["slug"] for a in areas if (CUENTA in a["cuentas_dueno"] or es_resp) and (RAIZ / a["slug"]).is_dir()
                                      and personas_en_area(leer(RAIZ / a["slug"] / "area.md") or ""))
    if PERSONAS_ANTERIOR:
        print("Personas: ANTERIOR en " + PERSONAS_ANTERIOR + (" (falta la versión mínima del plugin)" if VERSION_MINIMA_FALTA else "")
              + (" · se pregunta antes de responder (la RESPUESTA)" if PUEDE_ESCRIBIR and not ESTRUCTURA_ANTERIOR
                 else " · no se pregunta en esta apertura" + (": solo lectura" if not PUEDE_ESCRIBIR else ": antes, la estructura de la 1.22")))
    if ajenas_en_uso:
        print(f"(en uso, no se ofrece ahora: {', '.join(ajenas_en_uso)}; alguien tocó lo que queda por migrar hace menos de {EN_USO_MIN} minutos y puede estar en sesión en otra computadora. Se ofrece en una apertura más tarde; no hace falta decir nada.)")


def primera_frase(l, minimo=40, maximo=220):
    """Hasta el primer punto que cierra frase fuera de paréntesis y de `código` (no «S. de R.L.»: lo que sigue va en
    minúscula o es otra inicial); si no lo hay antes de «maximo», se corta en una palabra con «…»."""
    nivel, cod = 0, False
    # «restringido: responsable Nombre. Descripción…» («dueño» hasta la 1.21): el nombre no es la primera frase; se salta
    m = re.match(r"^(.*?[—–:-]\s*restringid[oa]\s*:\s*(?:due[ñn][oa]|responsable)\s+[^.;]+[.;]\s*)(.+)$", l, re.I)
    if m:
        return m.group(1) + primera_frase(m.group(2), min(minimo, 20), maximo)
    for i, ch in enumerate(l):
        if ch == "`":
            cod = not cod
        elif not cod and ch == "(":
            nivel += 1
        elif not cod and ch == ")":
            nivel = max(0, nivel - 1)
        elif ch == "." and not cod and nivel == 0 and i >= minimo and (i + 1 == len(l) or (l[i + 1] == " " and (i + 2 >= len(l) or l[i + 2].isupper() or l[i + 2] in "«`")) ):
            if not re.search(r"\b[A-ZÁÉÍÓÚÑ]$", l[:i]):
                return l[:i + 1]
        if i >= maximo:
            return l[:l.rfind(" ", 0, maximo)].rstrip(",;:") + "…"
    return l


def indice_proyectos(texto_area):
    """{slug: línea del índice} del bloque Proyectos, más las líneas de entregables debajo de cada uno."""
    idx, actual = {}, None
    for l in seccion(cabecera(texto_area)[1], "Proyectos").split("\n"):
        m = re.match(r"^- `([^`/]+)/?`\s*[—–:-]?\s*(.*)$", l)
        if m:
            actual = m.group(1); idx[actual] = {"linea": l.strip(), "sub": []}; continue
        if re.match(r"^- `", l):
            actual = None; continue
        if actual and re.match(r"^\s+- ", l):
            idx[actual]["sub"].append(l.rstrip())
    return idx


def declarado(linea):
    return bool(re.match(r"^- `[^`]+`\s*[—–:-]?\s*[\W_]*restringid[oa]\b", linea, re.I))


def lectores_de(celda):
    """A quiénes se lee, para «restringida a …», de la celda «Quién la lee». Como el tablero."""
    t = celda or ""
    if re.match(r"^[\W_]*restringid[oa]s?\b", t, re.I):
        t = re.sub(r"^[\W_]*restringid[oa]s?\b[*_»\"”'’\s]*", "", t, flags=re.I)
    else:
        t = re.sub(r"\s*[(\[—–,-]?\s*\brestringidas?\b\s*[)\]]?", "", t, flags=re.I)
    t = re.sub(r"^[:—–,-]\s*", "", t.strip())
    t = re.sub(r"^(?:la|lo)\s+leen\s+", "", t, flags=re.I).strip()
    m = re.fullmatch(r"\((.*)\)", t)
    t = (m.group(1) if m else t).strip()
    return "" if not t else t if re.match(r"^(?:a|al|para|solo|sólo|únicamente|por|entre)\b", t, re.I) else "a " + t


def de_la_cuenta(a):
    """El área es de la cuenta de esta sesión: responsable o colabora. Entonces la puede leer aunque esté restringida."""
    return bool(CUENTA) and CUENTA in (a["cuentas_dueno"] | a["colaboran"])


def motivo_area(slug):
    """Por qué no se lee un área: restringida según guia.md (Drive no baja a la computadora lo que la cuenta no puede
    abrir, así que su carpeta tampoco está), salvo que sea de la cuenta; sin carpeta en esta computadora; o no se pudo
    leer. El mismo criterio que el tablero con --cuenta, salvo un caso: un área restringida que la cuenta lee sin ser
    responsable ni colaborar (quien administra la carpeta) aquí sale restringida, porque lo restringido no se muestra fuera de
    su área; el tablero, que es solo de quien lo monta, la muestra entera."""
    a = next((x for x in areas if x["slug"] == slug), None)
    quien = solo_nombre(a["dueno"]) if a else "su responsable"
    if a and a["restringida"] and not de_la_cuenta(a):
        lect = lectores_de(a["lectores"])
        return f"restringida{' ' + lect if lect else ''}; si hace falta acceso, se pide a {quien}"
    if not (RAIZ / slug).exists():
        if a and de_la_cuenta(a):
            return "es de esta cuenta, pero su carpeta aún no se creó o no está sincronizada en esta computadora"
        return f"aún no se creó, no está sincronizada en esta computadora o la cuenta no tiene acceso; responde {quien}"
    return f"no se pudo leer: sin permiso o sin descargar; responde {quien}"


def claude_outputs():
    """Lo que la app dejó en «Claude outputs»: nombre y fecha, sin abrir nada; se propone colocarlo en su proyecto.
    Sale en todos los modos, también al abrir un proyecto, pero solo a la cuenta del responsable de contexto (o sin
    --cuenta): a las demás no se les dice nada al abrir, y lo que cae ahí en su conversación lo recoge el hook."""
    titulo("CLAUDE OUTPUTS")
    if CUENTA and not es_resp:
        print("(no se muestra a esta cuenta: solo a quien responde por guia.md y base/)")
        return []
    # cada suelto es (ruta dentro de la carpeta, fecha en segundos): de la carpeta o, sin consola, del listado (1.24.9)
    sueltos = []
    if SIN_FECHAS and OUTPUTS:
        try:
            d_ = json.loads(pathlib.Path(OUTPUTS).read_text(encoding="utf-8"))
            ents = (d_.get("entries") if isinstance(d_, dict) else d_) or []
            OUTPUTS_CORTADO[0] = bool(isinstance(d_, dict) and d_.get("truncated"))
        except (OSError, ValueError, AttributeError):
            ents = []
        # un archivo o una carpeta del primer nivel es un suelto; la fecha de una carpeta, la de lo más nuevo que tenga dentro
        nom = lambda e: str(e.get("name") or "").replace("\\", "/").strip("/")
        ents = [e for e in ents if isinstance(e, dict) and nom(e) and not any(x.startswith(".") for x in nom(e).split("/"))]
        fechas = {}
        for e in ents:
            if e.get("type") == "file":
                for k in range(1, len(nom(e).split("/")) + 1):
                    r_ = "/".join(nom(e).split("/")[:k]); fechas[r_] = max(fechas.get(r_, 0), (e.get("mtimeMs") or 0) / 1000)
        sueltos = sorted(((nom(e), fechas.get(nom(e), 0)) for e in ents if "/" not in nom(e) and e.get("type") in ("file", "dir")),
                         key=lambda x: x[1], reverse=True)
    elif not SIN_FECHAS:
        try:
            co = next((d for d in RAIZ.iterdir() if d.is_dir() and d.name.lower() == "claude outputs"), RAIZ / "Claude outputs")
            sueltos = sorted(((p.relative_to(co).as_posix(), p.stat().st_mtime) for p in co.rglob("*")
                              if p.is_file() and not any(x.startswith(".") for x in p.relative_to(co).parts)),
                             key=lambda x: x[1], reverse=True)
        except OSError:
            sueltos = []
    if not sueltos:
        print("(vacía o no existe)")
        return []
    print(f"{len(sueltos)} archivos sueltos")
    # en la mínima basta el número: la fila de la RESPUESTA lo resume, y los nombres los lista quien los coloca (1.24.9)
    if MINIMA:
        return sueltos
    for r_, m_ in sueltos[:30]:
        f = " · " + datetime.datetime.fromtimestamp(m_, TZ).date().isoformat() if m_ else ""
        print(f"- {r_}{f}")
    if len(sueltos) > 30:
        print(f"(y {len(sueltos) - 30} más)")
    return sueltos


CONFIDENCIAL = re.compile(r"contrat|propuesta|cotizaci|curr[ií]cul|\bcv\b|n[oó]mina|salari|sueldo|factura|\brfc\b|curp|\bnss\b|\bnda\b|confidencial|contrase|password", re.I)


def celda(t):
    """Una celda de tabla de Markdown: sin saltos de línea ni «|»."""
    return re.sub(r"\s*[\r\n|]+\s*", " · ", t).strip()


def ruta_en_la_computadora(rel):
    """La ruta de un archivo de la raíz en la computadora, con el separador de la ruta que dio get_device_info: en Windows
    va con barras invertidas, como hace espejo.py."""
    o = ORIGEN or str(RAIZ)
    sep = "\\" if "\\" in o and "/" not in o.replace("\\", "") else "/"
    return o.rstrip("/\\") + sep + rel.replace("/", sep)


def metodo_para_subir():
    """La copia del metodo.md del plugin para device_commit_files, con el --plugin y la versión de esta corrida."""
    return copia_del_metodo(PLUGIN, VERSION_PLUGIN)


def respuesta(sueltos, completa=False, sin_proyecto=False):
    """El recuadro con sus filas y, en orden, lo que toca, ya decidido (1.24.8). Así la conversación hace la apertura mínima
    sin cargar la skill sesion (su anexo minima.md, que inyecta el aviso de arranque), y la completa no recalcula filas.
    Nada de aquí remite a una skill: lo que hay que hacer viene escrito."""
    titulo("RESPUESTA (la apertura completa: el recuadro y lo que toca)" if completa else "RESPUESTA (la apertura mínima: haz esto y nada más)")
    vr_ = version_huella(linea_metodo)[0]
    version = VERSION_PLUGIN if VEREDICTO == "RAIZ ATRASADA" and PUEDE_ESCRIBIR else (".".join(map(str, vr_)) if vr_ else "?")
    raiz_ = str(RAIZ)
    filas = []
    if not PUEDE_ESCRIBIR:
        filas.append(f"**Solo lectura:** {MOTIVO_SOLO_LECTURA}")
    if VEREDICTO == "PLUGIN ATRASADO" and PUEDE_ESCRIBIR:
        filas.append(f"**Método:** esta carpeta usa una versión del método más nueva que la de tu Claude ({VERSION_RAIZ} frente a {VERSION_PLUGIN}). "
                     f"Actualízalo: {RECETA_ACTUALIZAR}.")
    filas += [f"**Aviso:** {d}" for d in DECIR]
    if sueltos:
        f_ = f", el último del {datetime.datetime.fromtimestamp(sueltos[0][1], TZ).date().isoformat()}" if sueltos[0][1] else ""
        conf = sum(1 for r_, _ in sueltos if CONFIDENCIAL.search(r_.rsplit("/", 1)[-1]))
        filas.append(f"**Claude outputs:** {'más de ' if OUTPUTS_CORTADO[0] else ''}{len(sueltos)} archivo{'s' if len(sueltos) != 1 else ''} suelto{'s' if len(sueltos) != 1 else ''}{f_}"
                     + (f"; {'uno parece confidencial' if conf == 1 else f'{conf} parecen confidenciales'}" if conf else "") + ".")
    cab = "La respuesta empieza con este recuadro, tal cual"
    if PERMISOS and PUEDE_ESCRIBIR:
        cab += " (la fila de permisos, si toca, la añade su paso)"
    if completa:
        cab += "; si en esta conversación ya salió, no se repite: solo sus filas nuevas, como filas de «Memoria · avisos», y una pregunta ya hecha no se repite"
    print(cab + ":")
    print(f"| Memoria de trabajo · {celda(ORGANIZACION or 'sin nombre')} · v{version} |")
    print("|---|")
    for f_ in filas:
        print(f"| {celda(f_)} |")
    pasos = []
    if not PUEDE_ESCRIBIR and VERSION_MINIMA is None and es_resp:
        # una sección sin versión legible: ningún plugin la arregla solo, y es quien lleva guia.md quien puede (revisión de la 1.26)
        pasos.append("Esta conversación es de solo lectura en la carpeta (fila «Solo lectura»), con una excepción: como responsable de contexto, la sesión puede corregir, "
                     "con su sí y un solo Edit, el primer párrafo de la sección «Versión mínima del plugin» de guia.md para que empiece por la versión "
                     f"({VERSION_MINIMA_ESTRUCTURA}. y el resto como estaba), y después volver a abrir; nada más se escribe hasta entonces. Se le dice así, en una línea.")
    elif not PUEDE_ESCRIBIR:
        # la puerta de la 1.26: se lee y se consulta, pero en esta conversación no se escribe nada en la carpeta
        pasos.append("Esta conversación es de solo lectura en la carpeta (fila «Solo lectura»): se lee, se consulta y se responde, pero no se escribe nada en ella "
                     "con ninguna herramienta (ni Write, ni Edit, ni device_bash, ni device_commit_files, ni el conector de Drive), no se cierra sesión, no se migra, no se pone al día el tablero "
                     "y no se pone al día metodo.md. Si piden algo que escribe, se dice en una línea que primero hay que actualizar el plugin, y se puede preparar el texto en la conversación.")
    copia_metodo = metodo_para_subir() if VEREDICTO == "RAIZ ATRASADA" and SIN_FECHAS and PUEDE_ESCRIBIR else None
    if copia_metodo:
        # sin consola, o en la apertura mínima, que no ejecuta nada descargado en la computadora (1.24.9): el metodo.md del
        # plugin instalado ya está en una carpeta de salidas, y basta escribirlo
        pasos.append("Antes de responder y sin decirlo, pon al día el método de la raíz: ToolSearch de mcp__remote-devices__device_commit_files (no viene cargada) y device_commit_files con "
                     f"stagedPath «{copia_metodo}» y devicePath «{ruta_en_la_computadora('metodo.md')}», y después, en el Bash que siga o en uno propio, `rm -rf \"{pathlib.Path(copia_metodo).parent}\"`. Si no sale en «written», no se dice nada y el recuadro lleva "
                     f"v{VERSION_RAIZ or '?'}, la versión que tiene la raíz.")
    elif not PUEDE_ESCRIBIR:
        pass
    elif VEREDICTO == "RAIZ ATRASADA" and SIN_FECHAS:
        # sin carpeta de salidas device_commit_files no tiene de dónde escribir, y descargar en la computadora es lo que se evita
        pasos.append(f"El método de la raíz no se pone al día en esta conversación: no se dice nada y el recuadro lleva v{VERSION_RAIZ or '?'}, la versión que tiene la raíz.")
    elif VEREDICTO == "RAIZ ATRASADA":
        # con consola (1.25.1): sin descargar nada en la computadora, como la mínima; lo normal es que la mínima de esta
        # misma conversación ya lo haya hecho, y entonces este paso no se repite
        pasos.append("Antes de responder y sin decirlo, pon al día el método de la raíz, salvo que la apertura mínima ya lo hiciera en esta conversación: en el contenedor, Bash "
                     f"`python3 \"<PLUGIN del aviso de arranque>/skills/sesion/abrir.py\" --metodo-para-subir --plugin \"{PLUGIN}\"` imprime la ruta de una copia del metodo.md del plugin "
                     f"(si no imprime nada, no se pone al día y no se dice); ToolSearch de mcp__remote-devices__device_commit_files y device_commit_files con stagedPath esa ruta y devicePath «{ruta_en_la_computadora('metodo.md')}»; "
                     "después, en el Bash que siga o en uno propio, `rm -rf` de la carpeta de esa copia. Si no sale en «written», no se dice nada y el recuadro lleva "
                     f"v{VERSION_RAIZ or '?'}, la versión que tiene la raíz.")
    if ESTRUCTURA_ANTERIOR and PUEDE_ESCRIBIR:
        pasos.append("Antes de responder: la respuesta es solo el recuadro y esta pregunta, con AskUserQuestion si está (opciones «Migrar ahora» y «Después»; sin ella, en texto, y se espera): "
                     f"«Tu parte de la carpeta usa la estructura de antes de la 1.22 ({ESTRUCTURA_ANTERIOR}). ¿La paso a la nueva antes de seguir? Renombra secciones y claves sin perder nada y deja una línea en la bitácora de cada proyecto.»"
                     + (" Añade que las áreas «(de …)» son de otros responsables y que su bitácora dirá quién las migró." if "(de " in ESTRUCTURA_ANTERIOR else "")
                     + " Con «Migrar ahora», el anexo migracion.md de la skill sesion; con «Después», no se vuelve a preguntar en esta conversación. "
                     "Los pasos que siguen a este van en la respuesta siguiente, después de la contestación; si ya se había respondido cuando llegó esta apertura, la pregunta va igual, sola tras el recuadro. "
                     "En una tarea programada no se pregunta ni se migra.")
    if PERSONAS_ANTERIOR and PUEDE_ESCRIBIR and not ESTRUCTURA_ANTERIOR:
        _pre = "Antes de responder: la respuesta es solo el recuadro y esta pregunta, con AskUserQuestion si está (opciones «Migrar ahora» y «Después»; sin ella, en texto, y se espera): "
        _pos = (" Con «Migrar ahora», el anexo migracion.md de la skill sesion («Las personas»); con «Después», no se vuelve a preguntar en esta conversación. "
                "Los pasos que siguen a este van en la respuesta siguiente, después de la contestación. En una tarea programada no se pregunta ni se migra.")
        if VERSION_MINIMA_FALTA:
            # sin versión mínima, el motivo es el de la 1.26 (los nombres de «Colabora»); con una anterior a la de la
            # estructura, el de la 1.26.8: las entradas del mantenimiento, que un plugin anterior contaría como sesiones
            if VERSION_MINIMA:
                pasos.append(_pre + f"«Tu carpeta pide el plugin {VERSION_MINIMA} para escribir. Desde la {VERSION_MINIMA_ESTRUCTURA}, el mantenimiento de la carpeta deja en la bitácora de cada proyecto "
                             "lo que arregla, y un plugin anterior lo contaría como una sesión. ¿Subo la versión mínima a la " + VERSION_MINIMA_ESTRUCTURA + "? Quien tenga uno anterior podrá leer, pero no escribir hasta actualizar: la migración te dirá quién cerró sesión hace poco con uno anterior, para avisarle antes.»" + _pos)
            else:
                pasos.append(_pre + f"«Tu carpeta ya nombra a las personas en «Quién es quién», pero no pide el plugin {VERSION_MINIMA_ESTRUCTURA} para escribir, y uno anterior a la 1.25 "
                             "leería los nombres de «Colabora» como si fueran correos. ¿Añado a guia.md la versión mínima del plugin? Quien tenga uno anterior podrá leer, pero no escribir hasta actualizar.»" + _pos)
        elif PERSONAS_ANTERIOR == "guia.md":
            pasos.append(_pre + "«Tu carpeta nombra a las personas como antes de la 1.25: correos en la tabla de áreas y en los proyectos. ¿La paso a «Quién es quién», una línea por persona en guia.md con su cuenta? "
                         f"Nadie pierde escritura ni lectura, y la carpeta pasa a pedir el plugin {VERSION_MINIMA_ESTRUCTURA} para escribir: la migración te dirá quién cerró sesión hace poco con uno anterior, para avisarle.»" + _pos)
        else:
            pasos.append(_pre + f"«En {PERSONAS_ANTERIOR}, el «Quién participa» de area.md todavía repite el responsable y quien colabora, que desde la 1.26 dice solo guia.md. ¿Lo quito, y con él los correos "
                         "de «Quién participa» de sus proyectos (cada uno deja su línea en la bitácora)? No cambia quién escribe.»" + _pos)
    if PERMISOS and PUEDE_ESCRIBIR:
        if completa:
            pasos.append("Permisos de Drive: como en la apertura mínima; si ya se ofreció en esta conversación, nada.")
        else:
            pasos.append("Permisos de Drive, solo si la sesión tiene el conector de Google Drive y el de artifacts (herramientas mcp__claude-artifacts__…; si no, nada, y no se dice): "
                         "ToolSearch de mcp__claude-artifacts__list_artifacts y mcp__claude-artifacts__db_get; con el slug del artifact «Tablero "
                         + (ORGANIZACION or "<organización>") + "» de esta cuenta, db_get de meta/permisos. Se ofrece si no existe, si su «revisado» es de hace más de 30 días, "
                         "o si su lista «cambios» no está vacía y es de hace más de 7 días: una fila «**Permisos de Drive:** sin revisar desde el <fecha>» (o «nunca se revisaron», "
                         "o «quedan <n> cambios de la revisión del <fecha>») y, al final, la pregunta «¿Reviso ahora los permisos de Drive?» con «Revisar ahora» y «Después». "
                         "Sin tablero o si una llamada falla, nada. Con «Revisar ahora», el anexo permisos.md de la skill sesion; con «Después», no se vuelve a ofrecer en esta conversación.")
    if completa and not sin_proyecto and PUEDE_ESCRIBIR:
        pasos.append("Antes de responder, la cola del tablero: ToolSearch de mcp__claude-artifacts__list_artifacts, db_query y read_file (o Artifact y ArtifactData si la sesión tiene las de antes); "
                     f"si list_artifacts trae un «Tablero {ORGANIZACION or '<organización>'}» de esta cuenta, se lee y se enseña como dice el anexo cola.md de la skill sesion. Sin el conector o sin tablero, nada, y no se dice.")
    # con un proyecto que no se pudo leer, la apertura sale igual, con el recuadro, y la respuesta pregunta cuál era (1.24.9)
    pasos.append(f"Di en una línea que «{ACTIVO}» no se encuentra (no existe, es restringido o no está descargado) y pregunta cuál se abre, con los proyectos de su área del bloque Proyectos de arriba; "
                 "no lo crees sin que lo pidan (la skill nuevo)." if sin_proyecto else
                 "Responde con la sesión: dónde quedó todo, los recuadros de la memoria, los avisos y la propuesta de trabajo, como dice «Qué respondo» de la skill sesion."
                 if completa else "Responde a lo que se pidió.")
    if sueltos and PUEDE_ESCRIBIR:
        pasos.append("La última acción de la respuesta: «¿Coloco ahora lo que hay en Claude outputs?», con AskUserQuestion si está (opciones «Colocar ahora» y «Después», "
                     "en la misma llamada que la de los permisos si la hay; sin la herramienta, esa misma pregunta en texto, una sola vez). Con «Colocar ahora», «Ordenar Claude outputs» "
                     "de la skill donde-va; con «Después», no se vuelve a preguntar en esta conversación, ni al abrir después un proyecto.")
    for i, p_ in enumerate(pasos, 1):
        print(f"{i}. {p_}")
    if not completa:
        print("Nada más de esta salida se dice: ni la lista de proyectos, que solo sirve para saber si la petición es trabajo de uno, ni avisos.")


area_activa = ACTIVO.split("/")[0] if ACTIVO and "/" in ACTIVO else None
TOPE_PROYECTOS = 40
n_proy = 0
if not ACTIVO:
    titulo("PROYECTOS POR ÁREA (para saber cuál se abre)")
    for a in areas:
        if a["restringida"] and not de_la_cuenta(a):
            # lo restringido no sale salvo que la cuenta sea de esa área o el proyecto activo esté dentro
            print(f"- {a['slug']}/ · {motivo_area(a['slug'])}"); continue
        t = leer(RAIZ / a["slug"] / "area.md")
        if t is None:
            print(f"- {a['slug']}/ · {motivo_area(a['slug'])}"); continue
        for slug, d in indice_proyectos(t).items():
            # solo para saber cuál se abre: la primera frase de la línea, no el resumen entero (1.19)
            l_ = d["linea"].replace(f"`{slug}/`", f"`{a['slug']}/{slug}/`", 1)
            # en la mínima basta reconocer el proyecto: la ruta y unas palabras, no la frase entera, y con tope (1.24.8)
            if MINIMA:
                n_proy += 1
                if n_proy > TOPE_PROYECTOS:
                    continue
            print(primera_frase(l_, minimo=20, maximo=90) if MINIMA else primera_frase(l_))
    if MINIMA and n_proy > TOPE_PROYECTOS:
        print(f"(y {n_proy - TOPE_PROYECTOS} proyectos más: sin --minima se listan todos)")
    if no_legibles:
        print(f"\n(no se pudieron leer: {len(no_legibles)})")
    # sin proyecto todavía, la RESPUESTA también sale: la apertura completa que sigue con el proyecto no la repite
    respuesta(claude_outputs(), completa=not MINIMA)
    sys.exit(0)

# ---------- nivel 1 ----------
if "/" not in ACTIVO:
    sys.exit(f"El proyecto va como <area>/<proyecto>, no «{ACTIVO}».")
pc = RAIZ / ACTIVO
area_txt = leer(RAIZ / area_activa / "area.md")
titulo(f"AREA {area_activa} · bloque Proyectos")
print(seccion(cabecera(area_txt)[1], "Proyectos") if area_txt is not None else f"(no se pudo leer area.md: {motivo_area(area_activa)})")
tp = leer(pc / "proyecto.md")
if tp is None:
    titulo("PROYECTO")
    print("(no se pudo leer proyecto.md: el proyecto no existe, es restringido o no está descargado)")
    respuesta(claude_outputs(), completa=True, sin_proyecto=True)
    sys.exit(0)
titulo(f"PROYECTO {ACTIVO}/proyecto.md")
print(con_pasos_recortados(tp.strip()))
if CUENTA:
    # colaborar en un solo proyecto: una línea «Colabora:» en «Quién participa» con la cuenta entre paréntesis
    a_act = next((a for a in areas if a["slug"] == area_activa), None)
    if a_act and CUENTA in a_act["cuentas_dueno"]:
        rol = "responsable del área"
    elif a_act and CUENTA in a_act["colaboran"]:
        rol = "colabora en el área"
    elif CUENTA in colaboran_en(seccion(cabecera(tp)[1], "Quién participa"), REG if REG["hay"] else None):
        rol = "colabora en este proyecto"
    else:
        rol = "no escribe aquí (preguntar antes de escribir)"
    titulo("CUENTA EN EL PROYECTO")
    print(f"{CUENTA}: {rol}")
# para el cierre: cuándo cambió cada registro por última vez; si cambian mientras dura la sesión, otra persona escribió
titulo("REGISTROS (hora de la última escritura)")
print(f"ahora: {datetime.datetime.now(TZ).isoformat(timespec='seconds')}   (para --abierto de cerrar.py)")
for n_ in ("proyecto.md", "decisiones.md", "sesiones.md"):
    if SIN_FECHAS:
        try:
            print(f"{n_}: {os.stat(pc / n_).st_size} bytes (sin consola: la hora es la de la copia; al cerrar se releen siempre)")
        except OSError:
            print(f"{n_}: no se pudo leer")
        continue
    try:
        st_ = datetime.datetime.fromtimestamp(os.stat(pc / n_).st_mtime, TZ)
        print(f"{n_}: {st_.isoformat(timespec='seconds')} · {os.stat(pc / n_).st_size} bytes" + (f" · hace {int((datetime.datetime.now(TZ) - st_).total_seconds() // 60)} minutos: si no fue esta cuenta, otra persona trabaja ahora en el proyecto" if (datetime.datetime.now(TZ) - st_).total_seconds() < 3600 else ""))
    except OSError:
        print(f"{n_}: no se pudo leer")
# los registros con sus archivados recientes: después de archivar, el vivo puede tener una entrada o ninguna (1.23)
dec_txt, _ = con_archivados(pc, "decisiones", leer(pc / "decisiones.md") or "", HOY.year, leer)
ses_txt, _ = con_archivados(pc, "sesiones", leer(pc / "sesiones.md") or "", HOY.year, leer)
titulo("DECISIONES (las 5 más recientes)")
print("\n\n".join(e["texto"] for e in recientes(dec_txt, 5)) or "(ninguna)")
titulo("SESIONES (las 3 más recientes)")
# las entradas «(tarea)», «(tablero)», «(migracion)» y «(mantenimiento)» no son sesiones (context_core, 1.26.8): no ocupan
# el sitio de una sesión real. Los arreglos del mantenimiento posteriores a la última sesión de esta cuenta se dicen en
# una línea cada uno, para que se sepa por qué cambió un archivo aunque otra persona haya cerrado sesión después
_ENTS = entradas(ses_txt)   # en el orden del archivo: lo más nuevo arriba
_SOBRE = _ENTS[:next((i for i, e in enumerate(_ENTS) if es_sesion(e["cab"])), len(_ENTS))]   # lo de encima de la última sesión
_HAY_ARREGLOS = any(es_mantenimiento(e["cab"]) for e in _SOBRE)
ses = sorted((e for e in _ENTS if es_sesion(e["cab"])), key=lambda e: e["fecha"], reverse=True)[:3]
print("\n\n".join(e["texto"] for e in ses) or "(ninguna)")
_YO = (REG["cuenta"].get(CUENTA) or {}).get("nombre") if CUENTA and REG.get("hay") else None
_tras = []
for e in _ENTS:
    if es_sesion(e["cab"]):
        quien_ = re.search(r"^Sesi[oó]n de\s*:\s*([^·\n]+)", e["texto"], re.M)
        if not _YO or (quien_ and quien_.group(1).strip() == _YO):
            break
        continue
    if not es_mantenimiento(e["cab"]):
        continue
    _a = arreglados(e["texto"])
    _tras.append(f"- {e['cab']} · arregló " + ", ".join(_a[:6]) + (" …" if len(_a) > 6 else ""))
if _tras:
    print("(arreglos del mantenimiento desde tu última sesión aquí, sin ser sesiones:)\n" + "\n".join(_tras[:6]) + (f"\n- … y {len(_tras) - 6} más" if len(_tras) > 6 else ""))
# la última sesión de trabajo: lo que cambió después de la última real sigue siendo trabajo sin sesión aunque una tarea, la
# migración o el mantenimiento hayan escrito después
ultima_real = ses[0]["fecha"] if ses and fecha_ok(ses[0]["fecha"]) else None
# el rastro del mantenimiento (1.26.8): si por encima de la última sesión hay arreglos, la referencia del último cierre es
# su «Último cierre», y cada archivo que nombran se descuenta hasta la hora de su propia entrada
def _seg_bitacora():
    if not SIN_FECHAS:
        try:
            return os.stat(pc / "sesiones.md").st_mtime
        except OSError:
            return None
    return segundos_del_listado(LISTADO, "sesiones.md") if LISTADO and listado_de(LISTADO) is not None else None


_LISTADOS = {}


def listado_de(ruta):
    """El listado de device_list_dir, leído una vez; None si no sirve (no se lee, viene truncado o no es el de la carpeta
    del proyecto), con la misma regla que listado_sin_sesion."""
    if ruta not in _LISTADOS:
        try:
            d = json.loads(pathlib.Path(ruta).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            d = None
        if isinstance(d, dict) and d.get("truncated"):
            d = None
        ents = ((d.get("entries") if isinstance(d, dict) else d) or []) if d is not None else []
        nombre = lambda e: str(e.get("name") or "").replace("\\", "/")
        if d is not None and not any(isinstance(e, dict) and nombre(e) in ("proyecto.md", "sesiones.md") for e in ents):
            d = None
        _LISTADOS[ruta] = d
    return _LISTADOS[ruta]


def segundos_del_listado(ruta, nombre):
    """Los segundos de modificación de un archivo del primer nivel de la carpeta del proyecto en el listado de la computadora."""
    d = listado_de(ruta)
    for e in ((d.get("entries") if isinstance(d, dict) else d) or []):
        if isinstance(e, dict) and str(e.get("name") or "").replace("\\", "/") == nombre and isinstance(e.get("mtimeMs"), (int, float)):
            return e["mtimeMs"] / 1000
    return None


_RASTRO = []


def rastro_de_la_bitacora():
    """(referencia del último cierre, {archivo: hasta cuándo se descuenta}), una vez."""
    if not _RASTRO:
        _RASTRO.append(rastro_mantenimiento([(e["cab"], e["texto"]) for e in _ENTS], _seg_bitacora()))
    return _RASTRO[0]


def arreglado(rel, segundos_):
    """Si `rel` (dentro del proyecto) lo nombra un arreglo del mantenimiento posterior a la última sesión y nadie lo cambió
    después de su entrada."""
    if segundos_ is None or not _HAY_ARREGLOS:
        return False
    return descontado(rel, segundos_, rastro_de_la_bitacora()[1])


def segundos(p):
    """La fecha de un archivo del proyecto: la del disco con consola; sin ella, la del listado de la computadora si lo hay."""
    if SIN_FECHAS:
        try:
            return segundos_del_listado(LISTADO, pathlib.Path(p).relative_to(pc).as_posix()) if LISTADO and listado_de(LISTADO) is not None else None
        except ValueError:
            return None
    try:
        return os.stat(p).st_mtime
    except OSError:
        return None
ultima_ses = ultima_real
# «Proyecto terminado el …» abre el Estatus desde la 1.22; hasta la 1.21, Estado actual o En corto
cerrado = any(re.search(r"Proyecto terminado el\s*20\d\d-\d\d-\d\d", seccion(cabecera(tp)[1], n_)) for n_ in ("Estatus", "Estado actual", "En corto"))

titulo("ENTREGABLES (cabeceras)")
avisos = []
# un proyecto que la migración dejó a medias (un conflicto) en un área ya migrada: la apertura mínima no baja a los
# proyectos de un área migrada, así que se dice aquí, al abrirlo
_marcas = marcas_anteriores(cabecera(tp)[1], "proyecto") + [f for f in ARCHIVOS_ANTERIORES if (pc / f).is_file()]
if _marcas and not area_anterior(area_activa):
    avisos.append(f"Estructura a medias: este proyecto conserva {', '.join('«' + m + '»' for m in _marcas)} de antes de la 1.22 y su área ya "
                  f"está migrada. Se propone pasarlo ahora con migrar_estructura.py (migracion.md, «Con el sí»), que solo toca lo que falta; "
                  f"si da un conflicto (un estado-anterior.md o un inventario.md que ya existía), se junta a mano en esta sesión.")
ents = []
d = pc / "entregables"
try:
    nombres = sorted(n for n in os.listdir(d) if not n.startswith(".") and (d / n).is_file()) if d.exists() else []
except OSError:
    nombres = []
for n in nombres:
    p = d / n
    if not n.endswith(".md"):
        print(f"- {n} · sin cabecera" + (f" (fecha de archivo {mtime(p)})" if mtime(p) else "")); continue
    t = leer(p)
    if t is None:
        print(f"- {n} · no se pudo leer"); continue
    fm, _ = cabecera(t)
    est, act = fm.get("estado", "?"), fm.get("actualizado", "?")
    base = fm.get("basado_en") if isinstance(fm.get("basado_en"), list) else []
    print(f"- {n} · {est} · actualizado {act} · {kb(tam(p))}" + (f" · basado_en: {', '.join(base)}" if base else ""))
    ents.append((n, est, act))
    if est == "borrador" and fecha_ok(act) and (HOY - datetime.date.fromisoformat(act)).days > 30:
        avisos.append(f"Borrador viejo: entregables/{n} lleva {(HOY - datetime.date.fromisoformat(act)).days} días en borrador (actualizado {act}).")
    mas_nuevas = []
    for b in (base if est not in ("reemplazado",) else []):
        b_ = re.sub(r"^\./", "", b.strip("`"))
        for c in (pc / b_, RAIZ / b_):
            partes_c = c.relative_to(RAIZ).parts if RAIZ in c.parents else ()
            if not b_.endswith(".md") or not partes_c or partes_c[0] == "base" or {"restringido", "fuentes", "taller"} & set(partes_c):
                break   # no se abre: sin cabecera que comparar, o de donde abrir no lee
            if c.is_file():
                tb = leer(c)
                fb = cabecera(tb)[0].get("actualizado") if tb else None
                if fecha_ok(fb) and fecha_ok(act) and fb > act:
                    mas_nuevas.append(f"{b_} ({fb})")
                break
    if mas_nuevas:
        avisos.append(f"Puede estar desfasado: entregables/{n} (actualizado {act}) se basa en algo más nuevo: {', '.join(mas_nuevas)}.")
    if fecha_ok(act) and ultima_ses and act > ultima_ses and not cerrado and not arreglado(f"entregables/{n}", segundos(p)):
        avisos.append(f"Trabajo sin sesión: entregables/{n} tiene actualizado {act}, posterior a la última sesión ({ultima_ses}).")

# trabajo sin sesión por fechas de archivo (nunca el contenido) en entregables/, taller/ y fuentes/
def listado_sin_sesion(ruta, desde):
    """[(fecha, hora, ruta)] de lo que el listado de device_list_dir da como cambiado desde «desde» (un datetime en la zona):
    decisiones.md y los archivos de entregables/, taller/ y fuentes/, fuera de restringido/ y de lo que empieza por punto.
    None si el listado no sirve: no se lee, viene truncado o no es el de la carpeta del proyecto (no trae proyecto.md en su
    primer nivel); entonces se mira a mano, porque un listado que no sirve no puede decir «no hay trabajo sin sesión»."""
    d = listado_de(ruta)
    if d is None:
        return None
    ents = (d.get("entries") if isinstance(d, dict) else d) or []
    nombre = lambda e: str(e.get("name") or "").replace("\\", "/")
    if not any(nombre(e) in ("proyecto.md", "sesiones.md") for e in ents if isinstance(e, dict)):
        return None
    out, lim = [], desde.timestamp() * 1000
    for e in ents:
        if not isinstance(e, dict):
            continue
        n, ms = nombre(e), e.get("mtimeMs")
        partes = n.split("/")
        if e.get("type") != "file" or not isinstance(ms, (int, float)) or ms < lim or any(x.startswith(".") or x == "restringido" for x in partes):
            continue
        if (n == "decisiones.md" or (len(partes) > 1 and partes[0] in ("entregables", "taller", "fuentes"))) and not arreglado(n, ms / 1000):
            t = datetime.datetime.fromtimestamp(ms / 1000, TZ)
            out.append((t.date().isoformat(), t.strftime("%H:%M"), n))
    return sorted(out, reverse=True)


# decisiones escritas después de la última entrada de la bitácora (1.26.4): desde que una decisión se escribe en cuanto se
# confirma, el cierre escribe decisiones.md antes que sesiones.md, así que tras un cierre la bitácora es la más reciente de
# las dos. Si decisiones.md es más nuevo por más de un minuto (lo que tarda una llamada de cerrar.py, también la de un
# plugin anterior, que escribía en el otro orden), hay decisiones que ninguna entrada cuenta todavía: de una sesión que no
# se cerró o de una que sigue abierta. Mira la hora, no solo el día: el aviso por día no ve una decisión del mismo día que
# la última sesión. Límite conocido: cualquier escritura posterior en sesiones.md (el cierre de otra persona, una entrada
# «(tarea)» o «(tablero)») lo apaga; entonces lo ve el cierre, que trae en «registradas_hoy» las de hoy que no son suyas.
def aviso_decisiones_sin_sesion(s_dec, s_ses):
    if s_dec is None or s_ses is None or s_dec - s_ses <= 60:
        return None
    dd, ds = datetime.datetime.fromtimestamp(s_dec, TZ), datetime.datetime.fromtimestamp(s_ses, TZ)
    desde = max(ds.date().isoformat(), ultima_ses or "")   # las del día de la última sesión o posteriores
    # las que la última entrada ya cuenta por su título no son candidatas
    ultima_txt = next((e["texto"].lower() for e in recientes(ses_txt, 40) if es_sesion(e["cab"])), "")
    cands = [e["cab"].split("·", 1)[-1].strip() for e in recientes(dec_txt, 40) if e["fecha"] and e["fecha"] >= desde]
    cands = [x for x in cands if x.lower() not in ultima_txt]
    if not cands:
        return None   # nada que ninguna entrada cuente: fechas de archivo movidas (una copia, un juntado), no una decisión suelta
    return (f"Decisiones sin sesión: decisiones.md cambió el {dd.date().isoformat()} a las {dd.strftime('%H:%M')}, después "
            + ("del último cierre antes de los arreglos del mantenimiento" if _top_arreglo else "que sesiones.md")
            + f" ({ds.date().isoformat()} {ds.strftime('%H:%M')}). Entre estas hay alguna que ninguna entrada de la bitácora cuenta: "
            + "; ".join(f"«{x}»" for x in cands[:5]) + (f" y {len(cands) - 5} más" if len(cands) > 5 else "")
            + ". Puede ser de una sesión que no se cerró o de una que sigue abierta: se pregunta de quién es y qué pasó, y solo si es de "
            "quien cierra hoy la cuenta la entrada de hoy, sin volver a escribirla.")


_top_arreglo = _HAY_ARREGLOS
REF_BITACORA, _DESC = rastro_de_la_bitacora()
ARREGLADOS = sorted({r for e in _SOBRE if es_mantenimiento(e["cab"]) for r in arreglados(e["texto"])})
_dec_sin_sesion = None
if not cerrado:
    if not SIN_FECHAS:
        try:
            _dec_sin_sesion = aviso_decisiones_sin_sesion(os.stat(pc / "decisiones.md").st_mtime, REF_BITACORA)
        except OSError:
            pass
    elif LISTADO and listado_de(LISTADO) is not None:
        _dec_sin_sesion = aviso_decisiones_sin_sesion(segundos_del_listado(LISTADO, "decisiones.md"), REF_BITACORA)
if _dec_sin_sesion:
    avisos.append(_dec_sin_sesion)

if SIN_FECHAS and ultima_ses and not cerrado:
    # sin consola las fechas de verdad solo están en el listado de la computadora (device_list_dir, en milisegundos):
    # con --listado se calculan aquí; sin él, o si no sirve, se da el instante desde el que mirarlo a mano
    _desde = datetime.datetime.combine(datetime.date.fromisoformat(ultima_ses) + datetime.timedelta(days=1), datetime.time(0), TZ)
    _lista = listado_sin_sesion(LISTADO, _desde) if LISTADO else None
    if _lista and _dec_sin_sesion:   # decisiones.md ya va en su propio aviso
        _lista = [x for x in _lista if x[2] != "decisiones.md"] or []
    if _lista:
        avisos.append("Trabajo sin sesión por fecha de archivo, después del " + ultima_ses + ": "
                      + "; ".join(f"{a} ({f} {h})" for f, h, a in _lista[:12]) + (" …" if len(_lista) > 12 else "")
                      + ". Quién lo cambió no consta: se pregunta qué pasó y se propone registrarlo.")
    elif _lista is None:
        avisos.append(("El listado no sirve (no se lee, viene truncado o no es el de la carpeta del proyecto). " if LISTADO else "")
                      + f"Trabajo sin sesión: con device_list_dir (recursivo) de la carpeta del proyecto, "
                      f"cuenta los archivos de entregables/, taller/ y fuentes/ (fuera de restringido/), y decisiones.md, con mtimeMs mayor o igual que "
                      f"{int(_desde.timestamp() * 1000)} (después del {ultima_ses}); si hay alguno, se pregunta qué pasó y se propone registrarlo. "
                      + (f"No cuentan, porque los arregló el mantenimiento, {', '.join(ARREGLADOS[:20])}{f' y {len(ARREGLADOS) - 20} más (la entrada «(mantenimiento)» de sesiones.md)' if len(ARREGLADOS) > 20 else ''}, mientras su mtimeMs no pase en más de 60000 a la hora «Escrita» de su entrada. " if ARREGLADOS else "")
                      + (f"Además, si el mtimeMs de decisiones.md pasa en más de 60000 a {int(REF_BITACORA * 1000)} (el último cierre antes de los arreglos del mantenimiento), "
                         if _top_arreglo and REF_BITACORA is not None else "Además, si el mtimeMs de decisiones.md pasa en más de 60000 al de sesiones.md, ")
                      + "hay decisiones que ninguna entrada cuenta (1.26.4): se pregunta de quién son.")
if not SIN_FECHAS and ultima_ses and not cerrado:
    lim = datetime.date.fromisoformat(ultima_ses)
    donde, lista = {}, []
    md = mtime(pc / "decisiones.md")
    if md and md > lim and not _dec_sin_sesion:   # si va en su propio aviso, no se repite aquí
        donde["decisiones"] = 1; lista.append((md.isoformat(), hora_de(pc / "decisiones.md"), "decisiones.md"))
    for sub in ("entregables", "taller", "fuentes"):
        for r_, ds, fs in os.walk(pc / sub):
            ds[:] = [x for x in ds if not x.startswith(".") and x != "restringido"]
            for f in fs:
                m_ = mtime(os.path.join(r_, f))
                if not f.startswith(".") and m_ and m_ > lim and not arreglado(pathlib.Path(r_, f).relative_to(pc).as_posix(), segundos(os.path.join(r_, f))):
                    donde[sub] = donde.get(sub, 0) + 1
                    lista.append((m_.isoformat(), hora_de(os.path.join(r_, f)), pathlib.Path(r_, f).relative_to(pc).as_posix()))
    if donde:
        # qué archivo y cuándo; quién lo cambió no consta (la carpeta no lo guarda y Drive no se lo da al plugin), así que se pregunta
        lista.sort(reverse=True)
        avisos.append("Trabajo sin sesión por fecha de archivo, después del " + ultima_ses + ": "
                      + ", ".join(f"{k} {v}" for k, v in donde.items()) + ". Qué y cuándo: "
                      + "; ".join(f"{a} ({f} {h})".replace(" )", ")") for f, h, a in lista[:12]) + (" …" if len(lista) > 12 else "")
                      + ". Quién lo cambió no consta: se pregunta qué pasó y se propone registrarlo.")

# ---------- el inventario: lo que esta apertura no imprimió, con cuánto pesa (1.26.3) ----------
# Cuentas, tamaños y líneas de cabecera, nunca cuerpos: con él la sesión decide cuánto más lee (SKILL.md, «Cuánto se
# lee»). Del taller del proyecto activo solo mira cabeceras, que son su parte pública (convenciones, sección 7).
def notas_del_taller(pc_):
    """(notas .md, otros archivos, informes) de taller/ del proyecto, como rutas dentro de él: sin lo que empieza por punto
    ni restringido/; los informes de taller/revisiones-de-calidad/ aparte, porque se atan por su nombre (1.26.3). La misma
    regla que sin_citar() de cerrar.py: si cambia aquí, cambia allí."""
    notas_, otros_, informes_ = [], [], []
    if not (pc_ / "taller").is_dir():
        return notas_, otros_, informes_
    for r_, ds, fs in os.walk(pc_ / "taller"):
        ds[:] = sorted(x for x in ds if not x.startswith(".") and x != "restringido")
        for f in sorted(fs):
            if f.startswith("."):
                continue
            rr = pathlib.Path(r_, f).relative_to(pc_).as_posix()
            (informes_ if rr.startswith("taller/revisiones-de-calidad/") else notas_ if f.endswith(".md") else otros_).append(rr)
    return notas_, otros_, informes_


def basado_en_de(texto):
    """Las líneas de basado_en de una cabecera como texto donde buscar citas: en lista (sangrada o no) o en una línea."""
    m = re.match(r"^---\n(.*?)\n---", texto or "", re.S)
    b = re.search(r"^basado_en\s*:(.*(?:\n[ \t]*-.*)*)", m.group(1), re.M) if m else None
    return b.group(1) if b else ""


def citada(rr, activo, textos):
    """Si alguno de los textos nombra la ruta rr del proyecto: sola, con «./», «../» o la ruta del proyecto delante, y
    entre comillas, negritas o ángulos; nombres comparados en NFC. La misma función que en cerrar.py."""
    import unicodedata
    nfc = lambda s: unicodedata.normalize("NFC", s or "")
    patron = re.compile(r"(?:^|(?<=[\s`'\"(\[,:·«*_<>]))(?:\./|(?:\.\./)+|" + re.escape(nfc(activo)) + r"/)?" + re.escape(nfc(rr)) + r"(?![\w/-])", re.M)
    return any(patron.search(nfc(t)) for t in textos)


# el kit de desarrollo (1.27): solo en un proyecto con la sección «## Desarrollo», una línea por aviso. Lee los archivos que
# la sección nombra (las dos configuraciones, el diseño, el plan y el seguimiento), nunca GitHub: el estado de las piezas
# es del seguimiento que alguien pide (skill desarrollo). Lo de un área restringida ajena, restringido/, fuentes/ o
# taller/ de otro proyecto no se abre: se dice que no se pudo comprobar, sin suponer qué hay.
KIT = seccion_desarrollo(tp)
KIT_INV = ""
NOMBRE_KIT = {"Configuración de plataforma": "la configuración de plataforma", "Configuración de repositorios": "la configuración de repositorios",
              "Diseño": "el diseño", "Plan": "el plan", "Seguimiento": "el seguimiento"}


def ruta_del_kit(r):
    """(ruta absoluta, se puede abrir) de una ruta de la sección, desde la raíz."""
    partes = pathlib.PurePosixPath(r).parts
    if not partes or ".." in partes or r.startswith(("/", "~")):
        return None, False
    if ACTIVO and r.startswith(ACTIVO + "/"):
        return RAIZ / r, "restringido" not in partes[2:]
    ajena = next((a for a in areas if a["slug"] == partes[0]), None)
    if (ajena and ajena["restringida"] and partes[0] != area_activa) or {"restringido", "fuentes", "taller"} & set(partes[1:]):
        return RAIZ / r, False
    return RAIZ / r, True


if not KIT.found and KIT.near_miss:
    avisos.append("Desarrollo: la sección «Desarrollo» tiene líneas que parecen del kit pero no se reconocen (la clave se escribe "
                  "«Repositorios:», «Construye:»…, como en skills/desarrollo/plantillas/seccion-desarrollo.md): mientras no se "
                  "corrija, el proyecto no se trata como de desarrollo.")
if KIT.found:
    _no_comprobadas, _faltan, _textos, _pesos = [], {}, {}, []

    def _existe(r):
        ab, abrible = ruta_del_kit(r)
        if ab is None:
            return False
        if not abrible:
            _no_comprobadas.append(r)
            return True        # no se puede mirar: ni se da por que falta ni se lee
        return ab.is_file()

    for m in piezas_faltantes(KIT, _existe):
        _faltan.setdefault(m.reason, []).append(m.key + (f" ({m.path})" if m.path else ""))
    _uno = {"sin línea": "no tiene su línea en la sección", "vacía": "tiene la línea vacía",
            "por crear": "está por crear", "no existe": "apunta a un archivo que no existe"}
    _varios = {"sin línea": "no tienen su línea en la sección", "vacía": "tienen la línea vacía",
               "por crear": "están por crear", "no existe": "apuntan a un archivo que no existe"}
    for motivo, claves in _faltan.items():
        # la frase de las plantillas solo cuando lo que falta tiene plantilla: los repositorios y las personas no (hallazgo 24)
        con_plantilla = motivo == "por crear" and any(c.split(" (")[0] in CLAVES_KIT and c.split(" (")[0] != SEGUIMIENTO_KIT for c in claves)
        avisos.append(f"Desarrollo: {', '.join(claves)} " + (_varios if len(claves) > 1 else _uno).get(motivo, motivo)
                      + (". Las plantillas del diseño, el plan y las configuraciones están en el plugin (skills/desarrollo/plantillas/)." if con_plantilla else "."))
    if KIT.unknown:
        avisos.append("Desarrollo: la sección tiene líneas que no reconozco: " + " · ".join("«" + u[:80] + "»" for u in KIT.unknown[:5]) + ".")
    for w in KIT.warnings[:5]:
        avisos.append(f"Desarrollo: {w}.")
    if _no_comprobadas:
        avisos.append("Desarrollo: no se pudo comprobar, porque está donde este proyecto no lee: " + ", ".join(_no_comprobadas) + ".")
    for clave in CLAVES_KIT:
        r = KIT.paths.get(clave, "")
        ab, abrible = ruta_del_kit(r) if r and r != "por crear" else (None, False)
        if ab is not None and abrible and ab.is_file():
            t_ = leer(ab)
            if t_ is not None:
                _textos[clave] = (r, t_)
                if not (ACTIVO and r.startswith(ACTIVO + "/entregables/")):
                    _pesos.append(f"{NOMBRE_KIT[clave][3:]} {r} ({kb(tam(ab))})")
    # lo que falta dentro del diseño, del plan y de las configuraciones (sus secciones y columnas fijas), y lo que su
    # lectura encontró mal: un identificador repetido, dos fases en curso, una relación a nada (hallazgo 14)
    _leidos = {}
    for clave, leer_ in (("Diseño", leer_diseno), ("Plan", leer_plan), ("Configuración de plataforma", leer_configuracion),
                         ("Configuración de repositorios", leer_configuracion)):
        if clave not in _textos:
            continue
        _leidos[clave] = leer_(_textos[clave][1])
        faltan_ = _leidos[clave].missing
        if faltan_:
            avisos.append(f"Desarrollo: {re.sub(r'^a el ', 'al ', 'a ' + NOMBRE_KIT[clave])} ({_textos[clave][0]}) le falta {', '.join(faltan_[:6])}"
                          + (f" y {len(faltan_) - 6} más" if len(faltan_) > 6 else "") + ": el plugin lee esos títulos tal cual.")
        if _leidos[clave].warnings:
            w_ = _leidos[clave].warnings
            avisos.append(f"Desarrollo: en {NOMBRE_KIT[clave]}, " + "; ".join(w_[:3]) + (f"; y {len(w_) - 3} más" if len(w_) > 3 else "") + ".")
    # desfasado: el diseño o el plan son anteriores a una decisión de este proyecto que los nombra en «Afecta a»
    for clave in ("Diseño", "Plan"):
        if clave not in _textos:
            continue
        r, t_ = _textos[clave]
        act_ = cabecera(t_)[0].get("actualizado", "")
        if not fecha_ok(act_):
            continue
        nombres_ = {r, pathlib.PurePosixPath(r).name}
        if ACTIVO and r.startswith(ACTIVO + "/"):
            nombres_.add(r[len(ACTIVO) + 1:])
        pat_ = re.compile(r"(?<![\w/.-])(?:" + "|".join(re.escape(x) for x in sorted(nombres_, key=len, reverse=True)) + r")(?![\w-])")
        cuenta_ = {}
        for e in reversed(entradas(dec_txt)):
            if not e["fecha"]:
                continue
            n_ = cuenta_[e["fecha"]] = cuenta_.get(e["fecha"], 0) + 1
            e["id"] = e["fecha"] + ("" if n_ == 1 else f"-{n_}")
        nuevas_ = [e for e in entradas(dec_txt) if e["fecha"] and e["fecha"] > act_
                   and pat_.search((re.search(r"^Afecta a:\s*(.+)$", e["texto"], re.M) or [None, ""])[1])]
        if nuevas_:
            e = max(nuevas_, key=lambda x: x["fecha"])
            avisos.append(f"Desarrollo: {NOMBRE_KIT[clave]} ({r}, actualizado {act_}) puede estar desfasado: la decisión del {e['fecha']} "
                          f"«{e['cab'].split('·', 1)[-1].strip()[:120]}» lo nombra en «Afecta a»"
                          + (f", y {len(nuevas_) - 1} más" if len(nuevas_) > 1 else "") + ".")
    # el último seguimiento: la fecha de su entrada más nueva («## AAAA-MM-DD …»), o su actualizado
    if KIT.paths.get(SEGUIMIENTO_KIT) == "por crear" or "Seguimiento" in _textos:
        f_seg = ""
        if "Seguimiento" in _textos:
            m_ = re.search(r"^## .*?\b(20\d\d-\d\d-\d\d)\b", cabecera(_textos["Seguimiento"][1])[1], re.M)
            f_seg = m_.group(1) if m_ and fecha_ok(m_.group(1)) else cabecera(_textos["Seguimiento"][1])[0].get("actualizado", "")
        # la misma regla que seguimiento.py, desde context_core: una entrada de verdad tiene su «Leído:» con el commit, y es
        # entera si comparó todo lo que le tocaba (sin «Sin comprobar:»); el sí y la auditoría se apoyan en la última entera
        if "Seguimiento" in _textos:
            ents_ = entradas_seguimiento(_textos["Seguimiento"][1])
            f_seg = max((x["date"] for x in ents_), default="")
            f_vig = max((x["date"] for x in ents_ if x["whole"]), default="")
        else:
            f_vig = ""
        avisos.append(f"Desarrollo: el último seguimiento es del {f_seg} (hace {(HOY - datetime.date.fromisoformat(f_seg)).days} días)"
                      + ("." if f_vig == f_seg else (f"; el último que se leyó entero es del {f_vig}." if f_vig else "; ninguno se leyó entero."))
                      if fecha_ok(f_seg) else "Desarrollo: todavía no hay ningún seguimiento; lo pide cualquiera que lea el proyecto (skill desarrollo).")
    # la auditoría mensual: la línea comprobada hace más tiempo de las dos configuraciones, más de 31 días, o líneas sin
    # comprobar; una sola celda reciente no la apaga (hallazgo 10)
    confs_ = [_leidos[c] for c in ("Configuración de plataforma", "Configuración de repositorios") if c in _leidos]
    if confs_:
        fechas_ = [c.oldest for c in confs_ if c.oldest]
        f_aud = min(fechas_) if fechas_ else ""
        sin_ = [x for c in confs_ for x in c.unchecked]
        auditas = any(p.email and p.email == (CUENTA or "").lower() for p in KIT.roles.get("Audita", []))
        vieja = fecha_ok(f_aud) and (HOY - datetime.date.fromisoformat(f_aud)).days > 31
        if vieja or sin_ or not fecha_ok(f_aud):
            partes_ = ([f"la línea comprobada hace más tiempo es del {f_aud} (hace {(HOY - datetime.date.fromisoformat(f_aud)).days} días)"] if vieja else []) \
                + ([f"{len(sin_)} {'línea sigue' if len(sin_) == 1 else 'líneas siguen'} sin comprobar ({', '.join(sin_[:6])}{'…' if len(sin_) > 6 else ''})"] if sin_ else []) \
                + (["ninguna línea tiene una comprobación con fecha"] if not fecha_ok(f_aud) and not sin_ else [])
            avisos.append("Desarrollo: toca la auditoría mensual: " + "; ".join(partes_) + "."
                          + (" Te toca a ti: auditas este proyecto." if auditas else
                             " La hace quien audita: " + (", ".join(p.name for p in KIT.roles.get("Audita", [])) or "nadie en «Audita»") + "."))
    if _pesos:
        KIT_INV = "kit de desarrollo, fuera de entregables/ del proyecto: " + ", ".join(_pesos) + "."

titulo("INVENTARIO (lo que esta apertura no imprimió)")
for nombre_r, txt_r, impresas in (("decisiones", dec_txt, 5), ("sesiones", ses_txt, len(ses))):
    todos_r = sorted((n for n in os.listdir(pc) if re.match(rf"^{nombre_r}-\d{{4}}(-\d+)?\.md$", n)), reverse=True) if pc.is_dir() else []
    recientes_r = [n for n in todos_r if int(n[len(nombre_r) + 1:len(nombre_r) + 5]) >= HOY.year - 1]
    viejos_r = [n for n in todos_r if n not in recientes_r]
    partes_r = [f"{len(entradas(leer(pc / (nombre_r + '.md')) or ''))} en {nombre_r}.md ({kb(tam(pc / (nombre_r + '.md')))})"]
    partes_r += [f"{len(entradas(leer(pc / n) or ''))} en {n} ({kb(tam(pc / n))})" for n in recientes_r]
    linea_r = f"{nombre_r}: {len(entradas(txt_r))} entradas, " + ", ".join(partes_r) + f"; se imprimieron {min(impresas, len(entradas(txt_r)))}."
    if viejos_r:
        linea_r += " Archivados anteriores, sin leer: " + ", ".join(f"{n} ({kb(tam(pc / n))})" for n in viejos_r) + "."
    print(linea_r)
# sin consola, la copia de espejo.py no trae taller/ ni fuentes/ (o solo lo que la sesión creó o la migración trajo): no se
# cuentan nunca, para no dar por total lo que es una parte
if SIN_FECHAS:
    print("taller/ y fuentes/: no vienen enteros en la copia de una sesión sin consola; no se cuentan.")
    notas, otros_taller, informes, cabezas, cab_notas = [], [], [], {}, {}
else:
    notas, otros_taller, informes = notas_del_taller(pc)
    cabezas = {rr: cabeza_de(pc / rr) for rr in notas}   # solo la cabecera: los primeros 16 KB
    cab_notas = {rr: cabecera(cabezas[rr])[0] for rr in notas}
    if notas or otros_taller or informes:
        print(f"taller/: {len(notas)} notas ({kb(sum(tam(pc / r) for r in notas))})"
              + (f", {len(otros_taller)} {'archivo que no es nota' if len(otros_taller) == 1 else 'archivos que no son notas'} ({kb(sum(tam(pc / r) for r in otros_taller))})" if otros_taller else "")
              + (f" y {len(informes)} informes de revisión en taller/revisiones-de-calidad/ ({kb(sum(tam(pc / r) for r in informes))})" if informes else "") + ".")
    for rr in sorted(notas, key=lambda r: cab_notas[r].get("actualizado", "") if fecha_ok(cab_notas[r].get("actualizado", "")) else "", reverse=True)[:5]:
        fm = cab_notas[rr]
        print(f"- {rr} · {fm.get('estado', 'sin cabecera')} · actualizado {fm.get('actualizado', '?')} · {kb(tam(pc / rr))}"
              + (f" · {str(fm.get('aportacion') or fm.get('afirma'))[:200]}" if fm.get("aportacion") or fm.get("afirma") else ""))
    inv_f = next((pc / "fuentes" / n for n in ("inventario.md", "enlaces.md") if (pc / "fuentes" / n).is_file()), None)
    if inv_f is not None:
        lineas_f = (leer(inv_f) or "").split("\n")
        sep_ = re.compile(r"^\|[\s:|-]+\|?\s*$")
        # una fila de tabla que no es su encabezado (la línea antes del separador) ni el separador, o una viñeta
        filas_f = sum(1 for i, l in enumerate(lineas_f) if (l.startswith("|") and not sep_.match(l) and not (i + 1 < len(lineas_f) and sep_.match(lineas_f[i + 1])))
                      or re.match(r"^[-*] ", l))
        print(f"fuentes/{inv_f.name}: {filas_f} {'fila' if filas_f == 1 else 'filas'} ({kb(tam(inv_f))}).")
    elif (pc / "fuentes").is_dir():
        print("fuentes/: sin inventario.")
if KIT_INV:
    print(KIT_INV)

# una nota del taller está atada cuando algo del proyecto la nombra: proyecto.md, decisiones.md con sus archivados
# recientes, o el basado_en de un entregable (con sus subcarpetas) o de otra nota. Los informes de revisión no cuentan ni
# como notas ni como citas, y las notas reemplazadas no se avisan. La misma regla que sin_citar() de cerrar.py
if notas and not cerrado:
    bases = {rr: basado_en_de(cabezas[rr]) for rr in notas}
    if d.is_dir():
        for r_, ds, fs in os.walk(d):
            ds[:] = [x for x in ds if not x.startswith(".") and x != "restringido"]
            for f in fs:
                if f.endswith(".md") and not f.startswith("."):
                    bases[pathlib.Path(r_, f).relative_to(pc).as_posix()] = basado_en_de(leer(pathlib.Path(r_, f)))
    sueltas = [rr for rr in notas if cab_notas[rr].get("estado") != "reemplazado"
               and not citada(rr, ACTIVO, [tp, dec_txt] + [t for k, t in bases.items() if k != rr])]
    if sueltas:
        sueltas.sort(key=lambda r: cab_notas[r].get("actualizado", "") if fecha_ok(cab_notas[r].get("actualizado", "")) else "", reverse=True)
        avisos.append(f"Notas de taller que nada cita: {len(sueltas)} de {len(notas)} (ni un basado_en del proyecto, ni proyecto.md, ni decisiones.md). "
                      "Las más recientes: " + ", ".join(rr + (f" ({cab_notas[rr]['actualizado']})" if cab_notas[rr].get("actualizado") else "") for rr in sueltas[:5]) + ".")

# ---------- el barrido: Afecta a / Cuestiona a / Responde a en toda la raíz ----------
def proyectos_legibles():
    """(area, slug, carpeta) de cada proyecto cuyas decisiones se pueden mirar desde el proyecto activo."""
    for a in areas:
        if a["restringida"] and a["slug"] != area_activa:
            continue
        carpeta = RAIZ / a["slug"]
        t = leer(carpeta / "area.md")
        idx = indice_proyectos(t) if t is not None else {}
        try:
            hijos = sorted(n for n in os.listdir(carpeta) if (carpeta / n / "decisiones.md").is_file()) if carpeta.is_dir() else []
        except OSError:
            hijos = []
        for slug in hijos:
            # un proyecto sin línea en el índice de su área no se sabe si es restringido: no se mira, como en el tablero
            if f"{a['slug']}/{slug}" != ACTIVO and (slug not in idx or declarado(idx[slug]["linea"])):
                continue
            yield a["slug"], slug, carpeta / slug


respuestas, cuestiona, afecta = set(), [], []
mis_cuestionamientos, me_responden = {}, []
patron_proy = re.compile(r"(?<![\w/-])" + re.escape(ACTIVO) + r"(?![\w-])")
# un área entera como destino: «operacion/» o «operacion/ (el área entera)», nunca «operacion/soporte»
patron_area = re.compile(r"(?<![\w/-])" + re.escape(area_activa) + r"/(?![\w-])")
for a_slug, slug, carpeta in proyectos_legibles():
    # con los archivados de este año y del anterior: una decisión archivada sigue avisando y respondiendo (1.23)
    t, _ = con_archivados(carpeta, "decisiones", leer(carpeta / "decisiones.md"), HOY.year, leer)
    for r_ in respuestas_viejas(carpeta, HOY.year, leer):
        for m in re.finditer(r"([a-z0-9][\w.-]*/[a-z0-9][\w.-]*)#(20\d\d-\d\d-\d\d(?:-\d+)?)", r_):
            respuestas.add((m.group(1), m.group(2)))
        for m in re.finditer(r"premisa\s+(P\d+)", r_, re.I):
            respuestas.add(("premisa", m.group(1).upper()))
    if not t.strip():
        continue
    origen = f"{a_slug}/{slug}"
    # identificador de cada entrada: fecha y -2, -3… contando desde la más antigua del mismo día (de abajo arriba)
    es = entradas(t)
    cuenta = {}
    for e in reversed(es):
        if not e["fecha"]:
            e["id"] = ""                       # sin fecha válida no hay identificador (contrato, sección 4)
            continue
        n = cuenta[e["fecha"]] = cuenta.get(e["fecha"], 0) + 1
        e["id"] = e["fecha"] + ("" if n == 1 else f"-{n}")
    for e in es:
        campos = {k: (re.search(r"^" + k + r":\s*(.+)$", e["texto"], re.M | re.I) or [None, ""])[1] for k in ("Decidió", "Planteó", "Por qué", "Afecta a", "Cuestiona a", "Responde a")}
        if campos["Responde a"]:
            for m in re.finditer(r"([a-z0-9][\w.-]*/[a-z0-9][\w.-]*)#(20\d\d-\d\d-\d\d(?:-\d+)?)", campos["Responde a"]):
                respuestas.add((m.group(1), m.group(2)))
            for m in re.finditer(r"premisa\s+(P\d+)", campos["Responde a"], re.I):
                respuestas.add(("premisa", m.group(1).upper()))
        if origen == ACTIVO:
            if campos["Cuestiona a"] and e["id"]:
                mp_ = re.search(r"premisa\s+(P\d+)", campos["Cuestiona a"], re.I)
                mis_cuestionamientos[e["id"]] = (e["cab"], e["fecha"], mp_.group(1).upper() if mp_ else None)
            continue
        if campos["Responde a"]:
            for m in re.finditer(r"([a-z0-9][\w.-]*/[a-z0-9][\w.-]*)#(20\d\d-\d\d-\d\d(?:-\d+)?)", campos["Responde a"]):
                if m.group(1) == ACTIVO:
                    me_responden.append((origen, e, campos, m.group(2)))
        if campos["Cuestiona a"]:
            m = re.search(r"([a-z0-9][\w.-]*/[a-z0-9][\w.-]*)#", campos["Cuestiona a"])
            mp = re.search(r"premisa\s+(P\d+)", campos["Cuestiona a"], re.I)
            if (m and m.group(1) == ACTIVO) or (mp and es_resp):
                cuestiona.append((origen, e, campos, ("premisa", mp.group(1).upper()) if mp and not m else None))
        if campos["Afecta a"] and (patron_proy.search(campos["Afecta a"]) or patron_area.search(campos["Afecta a"])):
            afecta.append((origen, e, campos))

# un cuestionamiento sigue abierto si nadie respondió a su identificador; una premisa nueva que reemplaza a la
# cuestionada después del cuestionamiento también lo responde
reemplazo_fecha = {r: (f or "9999") for _, _, r, f in premisas if r}   # sin fecha, como el tablero: la responde
abiertos = []
for origen, e, c, prem in cuestiona:
    if not e["id"]:
        avisos.insert(0, f"Un cuestionamiento sin fecha válida en {origen} («{e['cab']}») nombra este proyecto: no tiene identificador y no se puede responder hasta que su responsable lo registre con fecha.")
        continue
    if (origen, e["id"]) in respuestas:
        continue
    if prem and prem[1] in reemplazo_fecha and reemplazo_fecha[prem[1]] >= e["fecha"]:
        continue
    abiertos.append((origen, e, c, prem))
# una línea por cuestionamiento, y el «Por qué» solo de los tres más recientes: con muchos, el aviso no crece sin tope
abiertos.sort(key=lambda x: (x[1]["fecha"], int(x[1]["id"].rsplit("-", 1)[1]) if x[1]["id"].count("-") == 3 else 1), reverse=True)
lineas_cq = []
for i, (origen, e, c, prem) in enumerate(abiertos):
    objetivo = f"la premisa {prem[1]}" if prem else c["Cuestiona a"]
    linea = f"Cuestionamiento abierto ({origen}#{e['id']}): «{e['cab']}». Planteó: {c['Planteó'] or c['Decidió'] or 'no consta'}. Cuestiona a: {objetivo}."
    if i < 3 and c["Por qué"]:
        linea += f" Por qué: {c['Por qué'][:300]}"
    lineas_cq.append(linea)
avisos[0:0] = lineas_cq
sin_fecha = [x for x in afecta if not x[1]["fecha"]]
afecta = [x for x in afecta if x[1]["fecha"]]
nuevos = [x for x in afecta if not ultima_real or x[1]["fecha"] >= ultima_real]
for origen, e, c in sorted(nuevos, key=lambda x: x[1]["fecha"], reverse=True):
    avisos.append(f"Le afecta una decisión de {origen} ({origen}#{e['id']}): «{e['cab']}». Decidió: {c['Decidió'] or 'no consta'}. Afecta a: {c['Afecta a'][:300]}")
# a quien cuestionó: la respuesta del responsable, si llegó después de su última sesión
for origen, e, c, cid in me_responden:
    if cid not in mis_cuestionamientos:
        continue   # «Responde a» apunta a una entrada de este proyecto que no es un cuestionamiento
    if not e["fecha"]:
        avisos.append(f"Una entrada sin fecha válida de {origen} responde a tu cuestionamiento {ACTIVO}#{cid} («{e['cab']}»): conviene que su responsable la registre con fecha.")
    elif not ultima_real or e["fecha"] >= ultima_real:
        avisos.insert(0, f"Respondieron tu cuestionamiento {ACTIVO}#{cid} («{mis_cuestionamientos[cid][0]}»): {origen}#{e['id']}, «{e['cab']}». Decidió: {c['Decidió'] or 'no consta'}. Por qué: {c['Por qué'][:300]}")
# una premisa cuestionada desde aquí y reemplazada después por otra: también es una respuesta
for cid, (cab_, fecha_, prem_) in mis_cuestionamientos.items():
    if prem_ and prem_ in reemplazo_fecha and reemplazo_fecha[prem_] != "9999" and reemplazo_fecha[prem_] >= fecha_ and (not ultima_real or reemplazo_fecha[prem_] >= ultima_real):
        nueva = next((l for pid, l, r, f in premisas if r == prem_), "")
        avisos.insert(0, f"Respondieron tu cuestionamiento {ACTIVO}#{cid} («{cab_}»): la premisa {prem_} se reemplazó el {reemplazo_fecha[prem_]}: {nueva}")
for origen, e, c in sin_fecha:
    avisos.append(f"Una entrada sin fecha válida de {origen} nombra este proyecto en «Afecta a» («{e['cab']}»): no se puede citar ni saber si es nueva; conviene que su responsable la revise.")
viejos = len(afecta) - len(nuevos)

# copias en conflicto: cuando dos computadoras escriben el mismo archivo antes de sincronizarse, Drive guarda las dos
# («sesiones (1).md», «proyecto [Conflict].md»). Solo cuenta una copia cuyo original está al lado. Van primero: hasta
# juntarlas, una de las dos versiones no la lee nadie.
CONFLICTO = re.compile(r"^(?P<base>.+?)\s*(\(\d+\)|\[[^\]]*conflict[^\]]*\])\.md$", re.I)
for carpeta_, donde_ in ((pc, "este proyecto"), (RAIZ / area_activa, f"el área {area_activa}"), (RAIZ, "la raíz")):
    try:
        nombres_ = sorted(os.listdir(carpeta_))
    except OSError:
        continue
    for n_ in nombres_:
        m_ = CONFLICTO.match(n_)
        if m_ and (carpeta_ / (m_.group("base") + ".md")).is_file():
            avisos.insert(0, f"Copia en conflicto en {donde_}: «{n_}» junto a «{m_.group('base')}.md». Drive guardó dos versiones porque dos personas "
                             f"escribieron a la vez; se juntan antes de seguir, como dice «Copias en conflicto» en cerrar.md.")

ctx = leer(RAIZ / "base" / "contexto.md")
fc = cabecera(ctx)[0].get("actualizado") if ctx else None
if fecha_ok(fc) and (HOY - datetime.date.fromisoformat(fc)).days > 90:
    avisos.append(f"base/contexto.md lleva {(HOY - datetime.date.fromisoformat(fc)).days} días sin actualizarse (actualizado {fc}).")

titulo("AVISOS")
print("\n".join("- " + a for a in avisos) or "(ninguno)")
if viejos:
    print(f"(además, {viejos} decisiones de otros proyectos anteriores a la última sesión lo nombran en «Afecta a:»; ya se vieron)")
if no_legibles:
    print(f"(no se pudieron leer {len(no_legibles)} archivos o carpetas: restringidos o sin descargar; no se supone qué hay)")
respuesta(claude_outputs(), completa=True)
