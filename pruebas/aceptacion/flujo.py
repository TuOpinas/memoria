"""Arnés común de las pruebas de aceptación de P01–P03 (no es una prueba: correr.py solo corre los archivos que empiezan
por una pieza y «_»).

Lo que se prueba es la plantilla del workflow del kit de desarrollo, plugins/memoria/skills/desarrollo/plantillas/
pruebas-aceptacion.yml, como la correría GitHub en un pull request: se monta un repositorio de git temporal con la base y
la cabeza del pull request, y se corren, en orden, los pasos «run:» del workflow con su «env:» de arriba, el «env:» de
cada paso y lo que GitHub pone en ${{ … }} (base, cabeza y título del pull request). Con comprobar(env_wf=…) la prueba
cambia el «env:» de arriba como lo deja un proyecto que montó el kit, y el ejecutor cambia con su «CORREDOR»;
quitar «CORREDOR» con None exige pytest, igual que no declararlo. Con
comprobar(ejecutables=…) deja archivos del repositorio ejecutables (un corredor propio, un node_modules/.bin/vitest de
mentira). Solo biblioteca estándar (Python 3.9+), sin leer nada más del plugin.

Del workflow se entiende un subconjunto: arriba, «name», «on» (con «pull_request»), «permissions», «concurrency», «env»
y «jobs»; un
solo job con «name», «runs-on», «timeout-minutes» y «steps»; pasos con «name», «uses», «with», «env» y «run: |»; valores
de una línea, y las expresiones de base, cabeza y título del pull request, solo en «env». Ante cualquier otra cosa («if:»,
«shell:», «defaults:», otro job, otra expresión, un paso que escribe en $GITHUB_ENV o $GITHUB_PATH) la prueba no se monta
(salida 2) en vez de correr algo distinto de lo que correría GitHub. Los pasos corren con «bash -e», que es lo que usa
GitHub cuando el paso no dice «shell:» (sin pipefail: si lo necesita, el paso lo pone), y la plantilla pide bash 4 o
posterior. El entorno de los pasos se arma desde cero (PATH, HOME, idioma y carpeta temporal), para que el color de la
terminal, PYTHONPATH o la configuración de git de quien corre no cambien el resultado.

Una prueba que usa este arnés sale con 0 si pasa, con 1 si falla y con 2 si no se pudo montar (sin git, sin la plantilla,
sin pytest con el corredor pytest, sin node o npx con el corredor vitest): eso no es que la pieza falte, y correr.py lo
cuenta como error.
"""
import atexit, itertools, os, pathlib, re, shutil, signal, subprocess, sys, tempfile, traceback

RAIZ = pathlib.Path(__file__).resolve().parents[2]
YML = RAIZ / "plugins" / "memoria" / "skills" / "desarrollo" / "plantillas" / "pruebas-aceptacion.yml"
WORKFLOW = ".github/workflows/pruebas-aceptacion.yml"


class Montaje(Exception):
    """La prueba no se pudo montar: sale con 2."""


# ---------- temporales: una carpeta por proceso, que se borra al salir ----------
_TMP = None
_cuenta = itertools.count(1)


def _tmp(nombre, carpeta=False):
    global _TMP
    if _TMP is None:
        _TMP = pathlib.Path(tempfile.mkdtemp(prefix="aceptacion-"))
        atexit.register(shutil.rmtree, _TMP, True)
        try:   # que un SIGTERM también pase por atexit
            signal.signal(signal.SIGTERM, lambda *_: sys.exit(2))
        except (ValueError, OSError):
            pass
    p = _TMP / f"{nombre}-{next(_cuenta)}"
    if carpeta:
        p.mkdir()
    return p


# ---------- leer la plantilla (sin PyYAML) ----------
def _valor(v):
    v = v.strip()
    if v[:1] in ("'", '"'):
        q = v[0]
        fin = v.find(q, 1)
        if fin > 0:
            resto = v[fin + 1:].strip()
            if resto and not resto.startswith("#"):
                raise Montaje(f"no se entiende el valor {v!r} de la plantilla (comillas dentro de comillas)")
            return v[1:fin]
    if v[:1] in ("|", ">"):
        raise Montaje(f"no se entiende el valor {v!r} de la plantilla (varias líneas)")
    m = re.search(r"\s#", v)
    return (v[:m.start()] if m else v).strip()


def _mapa(lineas, i, sangria):
    """Un mapa «clave: valor» de una sola línea por clave, desde la línea i, con esa sangría."""
    out = {}
    while i < len(lineas):
        l = lineas[i]
        if not l.strip() or l.lstrip().startswith("#"):
            i += 1
            continue
        s = len(l) - len(l.lstrip())
        if s < sangria:
            break
        if s == sangria:
            m = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", l)
            if m:
                out[m.group(1)] = _valor(m.group(2))
        i += 1
    return out


def plantilla():
    """(env del workflow, [pasos]): cada paso es {"nombre", "env", "run"}; los de «uses:» no llevan run."""
    if not YML.is_file():
        raise Montaje(f"no está la plantilla {YML.relative_to(RAIZ)}")
    lineas = YML.read_text(encoding="utf-8").split("\n")
    env = {}
    for i, l in enumerate(lineas):
        if l.startswith("env:"):
            env = _mapa(lineas, i + 1, 2)
            break
    def claves(sangria, desde=0, hasta=None):
        return [(i, m.group(1)) for i, l in enumerate(lineas[desde:hasta], desde)
                for m in [re.match(r"^" + " " * sangria + r"([^\s#-][^:]*):", l)] if m]
    arriba = claves(0)
    for _, c in arriba:
        if c not in ("name", "on", "permissions", "concurrency", "env", "jobs"):
            raise Montaje(f"la plantilla usa «{c}:» arriba, que este arnés no entiende")
    pos = {c: i for i, c in arriba}
    if "on" not in pos or "jobs" not in pos:
        raise Montaje("la plantilla no tiene «on:» o «jobs:»")
    fin_on = min([i for i, _ in arriba if i > pos["on"]] or [len(lineas)])
    en_on = [c for _, c in claves(2, pos["on"] + 1, fin_on)]
    if en_on != ["pull_request"]:
        raise Montaje(f"«on:» tiene que ser solo «pull_request» (tiene {', '.join(en_on) or 'otra forma'})")
    for _, c in claves(4, pos["on"] + 1, fin_on):
        if c != "types":
            raise Montaje(f"«on: pull_request» usa «{c}:», que este arnés no entiende")
    if len(claves(2, pos["jobs"] + 1)) != 1:
        raise Montaje("la plantilla tiene más de un job: este arnés solo entiende uno")
    for _, c in claves(4, pos["jobs"] + 1):
        if c not in ("name", "runs-on", "timeout-minutes", "steps"):
            raise Montaje(f"el job usa «{c}:», que este arnés no entiende")
    donde = [i for i, l in enumerate(lineas) if re.match(r"^\s+steps:\s*$", l)]
    if not donde:
        raise Montaje("la plantilla no tiene «steps:»")
    if len(donde) > 1:
        raise Montaje("la plantilla tiene más de un job: este arnés solo entiende uno")
    i = donde[0]
    j = i + 1
    while j < len(lineas) and not lineas[j].strip():
        j += 1
    m = re.match(r"^(\s*)- ", lineas[j])
    if not m:
        raise Montaje("no se reconocen los pasos de la plantilla")
    ind = len(m.group(1))
    pasos, actual = [], None
    k = j
    while k < len(lineas):
        l = lineas[k]
        if l.strip() and (len(l) - len(l.lstrip())) < ind:
            break
        if re.match(r"^" + " " * ind + r"- ", l):
            actual = {"nombre": "", "env": {}, "run": None}
            pasos.append(actual)
            l = " " * (ind + 2) + l[ind + 2:]
            lineas[k] = l
        c = re.match(r"^" + " " * (ind + 2) + r"([a-z-]+):\s*(.*)$", l)
        if l.strip() and not l.lstrip().startswith("#") and (len(l) - len(l.lstrip())) == ind + 2 and not c:
            raise Montaje(f"no se entiende esta línea de un paso de la plantilla: {l.strip()[:60]}")
        if actual is not None and c:
            clave, resto = c.group(1), c.group(2)
            if clave not in ("name", "uses", "with", "env", "run"):
                raise Montaje(f"el paso «{actual['nombre']}» usa «{clave}:», que este arnés no entiende")
            if clave == "name":
                actual["nombre"] = _valor(resto)
            elif clave == "env":
                if resto.strip():
                    raise Montaje(f"el paso «{actual['nombre']}» trae su «env:» en una línea, que este arnés no entiende")
                actual["env"] = _mapa(lineas, k + 1, ind + 4)
            elif clave == "run":
                if resto.strip().startswith("|"):
                    cuerpo, n = [], k + 1
                    while n < len(lineas) and (not lineas[n].strip() or (len(lineas[n]) - len(lineas[n].lstrip())) > ind + 2):
                        cuerpo.append(lineas[n])
                        n += 1
                    while cuerpo and not cuerpo[-1].strip():
                        cuerpo.pop()
                    sang = min((len(x) - len(x.lstrip()) for x in cuerpo if x.strip()), default=0)
                    actual["run"] = "\n".join(x[sang:] for x in cuerpo) + "\n"
                    k = n
                    continue
                if resto.strip().startswith(">"):
                    raise Montaje("un «run: >» de la plantilla no se entiende")
                actual["run"] = resto + "\n"
        k += 1
    if not any(p["run"] for p in pasos):
        raise Montaje("la plantilla no tiene pasos «run:»")
    for p in pasos:
        if p["run"] and "${{" in p["run"]:
            raise Montaje(f"el paso «{p['nombre']}» usa una expresión de GitHub dentro de «run:», que este arnés no sustituye")
        if p["run"] and re.search(r"GITHUB_(ENV|PATH)\b", p["run"]):
            raise Montaje(f"el paso «{p['nombre']}» escribe en $GITHUB_ENV o $GITHUB_PATH, que este arnés no aplica")
    return env, pasos


# ---------- el repositorio del pull request ----------
def _limpio():
    """Un entorno armado desde cero: solo dónde están los programas, la carpeta personal, el idioma y la carpeta
    temporal. Nada de git, de GitHub, de pytest ni de Python de quien corre, y git sin configuración de fuera."""
    env = {k: v for k, v in os.environ.items()
           if k in ("PATH", "HOME", "LANG", "TMPDIR", "SYSTEMROOT") or k.startswith("LC_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", XDG_CONFIG_HOME=str(_tmp("xdg", carpeta=True)))
    return env


def _git(d, *a):
    r = subprocess.run(["git", "-c", "user.name=Prueba", "-c", "user.email=p@e.test", "-c", "commit.gpgsign=false",
                        "-c", "core.hooksPath=/dev/null", "-c", "core.excludesFile=/dev/null", "-c", "core.attributesFile=/dev/null",
                        "-C", str(d), *a], capture_output=True, text=True, errors="replace", env=_limpio())
    if r.returncode != 0:
        raise Montaje(f"git {' '.join(a)}: {r.stderr.strip()}")
    return r.stdout.strip()


def _escribir(d, archivos, ejecutables=()):
    """Escribe los archivos (None borra). Los que están en «ejecutables» quedan con permiso de ejecución (0755), que
    git guarda en el commit como 100755."""
    for ruta, texto in archivos.items():
        p = d / ruta
        if texto is None:
            if p.exists():
                _git(d, "rm", "-rq", ruta)
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texto, encoding="utf-8")
        if ruta in ejecutables:
            p.chmod(0o755)
            if not os.access(p, os.X_OK):
                raise Montaje(f"{ruta} no queda ejecutable: la carpeta temporal está en un sistema de archivos noexec")


def repositorio(base, cabeza, despues=None, ejecutables=()):
    """Un repositorio con la base (archivos de main) y una rama con los cambios del pull request (None borra). Lleva el
    workflow de la plantilla en su sitio, como un repositorio que ya montó el kit. Con «despues», main recibe esos cambios
    después de cortarse la rama, y lo que queda en la carpeta es la unión de las dos, como el checkout de GitHub en un pull
    request. Las rutas de «ejecutables» (una lista o tupla, escritas igual que en la base, la cabeza o «despues») quedan
    ejecutables en la carpeta y en los commits. Devuelve (carpeta, sha base, sha cabeza)."""
    if not shutil.which("git"):
        raise Montaje("no hay git")
    if not isinstance(ejecutables, (list, tuple)):
        raise Montaje("ejecutables: tiene que ser una lista o tupla de rutas, no " + type(ejecutables).__name__)
    sueltas = [r for r in ejecutables if r not in {**base, **cabeza, **(despues or {})}]
    if sueltas:
        raise Montaje("ejecutables: no están en la base, la cabeza ni «despues»: " + ", ".join(map(str, sueltas)))
    ejecutables = frozenset(ejecutables)
    d = _tmp("repo", carpeta=True)
    _git(d, "init", "-q", "-b", "main")
    _git(d, "config", "core.fileMode", "true")
    todo = {WORKFLOW: YML.read_text(encoding="utf-8"), "app/main.py": "x = 1\n"}
    todo.update(base)
    _escribir(d, todo, ejecutables)
    _git(d, "add", "-A")
    _git(d, "commit", "-qm", "base")
    sha_base = _git(d, "rev-parse", "HEAD")
    _git(d, "checkout", "-qb", "pull-request")
    _escribir(d, cabeza, ejecutables)
    _git(d, "add", "-A")
    _git(d, "commit", "-qm", "cambio", "--allow-empty")
    sha_cabeza = _git(d, "rev-parse", "HEAD")
    if despues:
        _git(d, "checkout", "-q", "main")
        _escribir(d, despues, ejecutables)
        _git(d, "add", "-A")
        _git(d, "commit", "-qm", "main sigue")
        sha_base = _git(d, "rev-parse", "HEAD")
        _git(d, "checkout", "-q", "--detach", sha_cabeza)
        _git(d, "merge", "-q", "--no-edit", "main")
    # como deja el repositorio actions/checkout en un pull request: HEAD suelto y sin ramas locales
    _git(d, "checkout", "-q", "--detach")
    _git(d, "update-ref", "refs/remotes/origin/main", sha_base)
    _git(d, "branch", "-qD", "main", "pull-request")
    return d, sha_base, sha_cabeza


_comprobado = set()


def _requisitos(env, corredor=None):
    """Lo que los pasos necesitan del entorno, con el mismo PATH con el que corren: si falta, no se monta (2). Depende
    del «CORREDOR» del «env:» de arriba: sin él o con «pytest», pytest en el python3 del PATH; con «vitest», node y npx;
    con cualquier otro valor (un corredor propio, vacío, otra palabra) ninguno de los dos, que lo que falte lo dice el
    control."""
    tipo = "pytest" if corredor is None or corredor == "pytest" else "vitest" if corredor == "vitest" else "otro"
    if tipo in _comprobado:
        return
    if not shutil.which("bash", path=env.get("PATH")):
        raise Montaje("no hay bash")
    r = subprocess.run(["bash", "-c", "echo ${BASH_VERSINFO[0]}"], capture_output=True, text=True, env=env)
    if not r.stdout.strip().isdigit() or int(r.stdout.strip()) < 4:
        raise Montaje("el bash del PATH es anterior al 4 (macOS trae el 3.2): los pasos del workflow no corren con él")
    if tipo == "pytest":
        if subprocess.run(["bash", "-c", "python3 -m pytest --version"], capture_output=True, env=env).returncode != 0:
            raise Montaje("el python3 del PATH no tiene pytest (python3 -m pip install pytest): la plantilla corre las pruebas con él")
    elif tipo == "vitest":
        faltan = [p for p in ("node", "npx") if not shutil.which(p, path=env.get("PATH"))]
        if faltan:
            raise Montaje(f"con «CORREDOR: vitest» los pasos necesitan {' y '.join(faltan)} en el PATH, y no está"
                          + ("n" if len(faltan) > 1 else ""))
    _comprobado.add(tipo)


def _entorno(d, extra, corredor=None):
    env = _limpio()
    _requisitos(env, corredor)
    archivos = {}
    for v in ("GITHUB_OUTPUT", "GITHUB_ENV", "GITHUB_STEP_SUMMARY"):
        archivos[v] = _tmp(v.lower())
        archivos[v].write_text("", encoding="utf-8")
    env.update({k: str(v) for k, v in archivos.items()})
    env.update(RUNNER_TEMP=str(_tmp("runner", carpeta=True)),
               GITHUB_WORKFLOW_REF=f"prueba/repo/{WORKFLOW}@refs/pull/1/merge", GITHUB_WORKSPACE=str(d))
    env.update(extra or {})
    return env


def _expresiones(v, contexto):
    def una(m):
        if m.group(1) not in contexto:
            raise Montaje(f"la plantilla usa la expresión «{m.group(1)}», que este arnés no conoce")
        return contexto[m.group(1)]
    return re.sub(r"\$\{\{\s*([^}]*?)\s*\}\}", una, v)


def comprobar(base, cabeza, titulo, extra=None, cuerpo="", autor="persona", despues=None, omitir=("Prepara el entorno",),
              env_wf=None, ejecutables=()):
    """Corre el workflow entero sobre un pull request y devuelve (código de salida, salida). Como en GitHub, se para en el
    primer paso que falla. extra: variables para las pruebas sembradas (p. ej. dónde escriben sus marcas); el «env:» de
    la plantilla las pisa. despues: lo que main recibe después de cortarse la rama (ver repositorio). omitir: pasos que no
    se corren; por defecto el que instala, para no cambiar el entorno de quien corre las pruebas (el arnés ya comprueba
    que está lo que pide el corredor). env_wf: cambios al «env:» de arriba de la plantilla, como los deja un proyecto que
    montó el kit ({"CORREDOR": "vitest", "CONFIG": None}: un valor lo pone, aunque sea "", y None quita la clave); van al
    entorno de los pasos, que es de donde el control lee «CORREDOR» y «CONFIG», como en GitHub. ejecutables:
    rutas del repositorio temporal que quedan con permiso de ejecución, en la carpeta y en git (ver repositorio)."""
    plantilla_env, pasos = plantilla()
    efectivo = dict(plantilla_env)
    for k, v in (env_wf or {}).items():
        if v is None:
            efectivo.pop(k, None)
        else:
            efectivo[k] = v
    d, sb, sh = repositorio(base, cabeza, despues, ejecutables)
    contexto = {"github.event.pull_request.base.sha": sb, "github.event.pull_request.head.sha": sh,
                "github.event.pull_request.title": titulo, "github.event.pull_request.body": cuerpo,
                "github.event.pull_request.user.login": autor, "github.event.pull_request.number": "1"}
    env = _entorno(d, extra, efectivo.get("CORREDOR"))
    env.update({k: _expresiones(v, contexto) for k, v in efectivo.items()})
    salida = []
    for paso in pasos:
        if not paso["run"] or paso["nombre"] in omitir:
            continue
        e = dict(env)
        e.update({k: _expresiones(v, contexto) for k, v in paso["env"].items()})
        guion = _tmp("paso.sh")
        guion.write_text(paso["run"], encoding="utf-8")
        r = subprocess.run(["bash", "--noprofile", "--norc", "-e", str(guion)], cwd=d, env=e, capture_output=True,
                           text=True, errors="replace", stdin=subprocess.DEVNULL, timeout=600)
        salida.append(f"--- paso «{paso['nombre']}» (salida {r.returncode})\n{r.stdout}{r.stderr}")
        if r.returncode != 0:
            return r.returncode, "\n".join(salida)
    return 0, "\n".join(salida)


# ---------- las pruebas sembradas y lo que dejan ----------
def sembrada(nombre, resultado="pasa", funcion=None):
    """El texto de un archivo de pruebas de pytest con una prueba que deja su marca («<nombre> <pid>») en $MARCAS y
    luego pasa, falla o se salta. La función no lleva la pieza en su nombre, para que un error que repita el nombre de
    la prueba no parezca nombrar la pieza, salvo que se pida una con «funcion». otra(texto) deja solo la función, para
    sumarla a otro archivo."""
    final = {"pasa": "    assert True\n", "falla": "    assert False, 'falla a propósito'\n",
             "saltada": "    import pytest\n    pytest.skip('saltada a propósito')\n"}[resultado]
    return ("import os\n\n\ndef " + (funcion or "test_caso_" + str(next(_cuenta))) + "():\n"
            f"    with open(os.environ['MARCAS'], 'a', encoding='utf-8') as f:\n"
            f"        f.write('{nombre} ' + str(os.getpid()) + '\\n')\n" + final)


def marcas():
    """Un archivo de marcas nuevo: (variables para comprobar(), función que lee [(nombre, pid)])."""
    f = _tmp("marcas")
    f.write_text("", encoding="utf-8")

    def leer():
        return [tuple(l.split()) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    return {"MARCAS": str(f)}, leer


def otra(texto):
    """La función de una sembrada, sin su «import os», para ponerla en un archivo que ya tiene otra."""
    return texto.split("\n\n\n", 1)[1]


def errores(salida):
    """Las líneas de error del workflow: «::error::…» o «::error title=…::…»."""
    return [l for l in salida.splitlines() if re.search(r"::error( [^:]*)?::", l)]


def nombra(lineas, pieza):
    return any(re.search(r"(?<![A-Za-z0-9])" + re.escape(pieza) + r"(?![0-9])", l) for l in lineas)


def verde(rc, salida, que="el check"):
    """Los problemas de un caso que tiene que quedar en verde: salida 0 y ningún error."""
    problemas = []
    if rc != 0:
        problemas.append(f"{que} no quedó en verde (salió con {rc})")
    if errores(salida):
        problemas.append(f"{que} dio un error: {errores(salida)[0][:160]}")
    return problemas


def plantilla_activas():
    env_wf, _ = plantilla()
    return env_wf.get("ACEPTACION", "tests/aceptacion").rstrip("/"), env_wf.get("ACTIVAS", ".github/piezas-activas.txt")


# ---------- informar ----------
class Informe:
    def __init__(self, pieza):
        self.pieza, self.fallos, self.total = pieza, 0, 0

    def escenario(self, titulo, problemas, salida=""):
        """problemas: lista de lo que no se cumple (vacía si el escenario se cumple)."""
        self.total += 1
        if problemas:
            self.fallos += 1
            print(f"  FALLA {self.pieza} · {titulo}")
            for p in problemas:
                print(f"        porque {p}")
            if salida:
                ultimas = [l for l in salida.splitlines() if l.strip()][-6:]
                print("        lo último que dijo el workflow:")
                for l in ultimas:
                    print("          | " + l[:200])
        else:
            print(f"  bien  {self.pieza} · {titulo}")


def principal(pieza, cuerpo):
    """Corre cuerpo(informe) y sale con 0, 1 o 2. La última línea es «RESULTADO: pasa» o «RESULTADO: falla»: correr.py
    solo cuenta una salida 0 o 1 que la traiga, para que una prueba que no arranca no pase por una que falla."""
    inf = Informe(pieza)
    try:
        cuerpo(inf)
    except Montaje as e:
        print(f"  ERROR {pieza}: la prueba no se pudo montar: {e}")
        sys.exit(2)
    except Exception:
        print(f"  ERROR {pieza}: la prueba se rompió (es un error de la prueba, no de la pieza):")
        traceback.print_exc(file=sys.stdout)
        sys.exit(2)
    if not inf.total:
        print(f"  ERROR {pieza}: la prueba no comprobó ningún escenario")
        sys.exit(2)
    print("RESULTADO: " + ("falla" if inf.fallos else "pasa"), flush=True)
    sys.exit(1 if inf.fallos else 0)
