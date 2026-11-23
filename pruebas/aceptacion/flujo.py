"""Arnés común de las pruebas de aceptación de P01–P03 (no es una prueba: correr.py solo corre los archivos que empiezan
por una pieza y «_»).

Lo que se prueba es la plantilla del workflow del kit de desarrollo, plugins/memoria/skills/desarrollo/plantillas/
pruebas-aceptacion.yml, como la correría GitHub en un pull request: se monta un repositorio de git temporal con la base y
la cabeza del pull request, y se corren, en orden, los pasos «run:» del workflow con su «env:» de arriba, el «env:» de
cada paso y lo que GitHub pone en ${{ … }} (base, cabeza y título del pull request). El ejecutor es pytest, como en la
plantilla. Solo biblioteca estándar (Python 3.9+), sin leer nada más del plugin.

Una prueba que usa este arnés sale con 0 si pasa, con 1 si falla y con 2 si no se pudo montar (sin git, sin pytest, sin
la plantilla): eso no es que la pieza falte, y correr.py lo cuenta como error.
"""
import os, pathlib, re, shutil, subprocess, sys, tempfile, traceback

RAIZ = pathlib.Path(__file__).resolve().parents[2]
YML = RAIZ / "plugins" / "memoria" / "skills" / "desarrollo" / "plantillas" / "pruebas-aceptacion.yml"
WORKFLOW = ".github/workflows/pruebas-aceptacion.yml"


class Montaje(Exception):
    """La prueba no se pudo montar: sale con 2."""


# ---------- leer la plantilla (sin PyYAML) ----------
def _valor(v):
    v = v.strip()
    if v[:1] in ("'", '"'):
        q = v[0]
        fin = v.find(q, 1)
        if fin > 0:
            return v[1:fin]
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
    try:
        i = next(i for i, l in enumerate(lineas) if re.match(r"^\s+steps:\s*$", l))
    except StopIteration:
        raise Montaje("la plantilla no tiene «steps:»")
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
        if actual is not None and c:
            clave, resto = c.group(1), c.group(2)
            if clave == "name":
                actual["nombre"] = _valor(resto)
            elif clave == "env" and not resto.strip():
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
                actual["run"] = resto + "\n"
        k += 1
    if not any(p["run"] for p in pasos):
        raise Montaje("la plantilla no tiene pasos «run:»")
    return env, pasos


# ---------- el repositorio del pull request ----------
def _git(d, *a):
    r = subprocess.run(["git", "-c", "user.name=Prueba", "-c", "user.email=p@e.test", "-c", "commit.gpgsign=false",
                        "-c", "core.hooksPath=/dev/null", "-C", str(d), *a], capture_output=True, text=True)
    if r.returncode != 0:
        raise Montaje(f"git {' '.join(a)}: {r.stderr.strip()}")
    return r.stdout.strip()


def _escribir(d, archivos):
    for ruta, texto in archivos.items():
        p = d / ruta
        if texto is None:
            if p.exists():
                _git(d, "rm", "-rq", ruta)
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texto, encoding="utf-8")


def repositorio(base, cabeza):
    """Un repositorio con la base (archivos de main) y una rama con los cambios del pull request (None borra). Lleva el
    workflow de la plantilla en su sitio, como un repositorio que ya montó el kit. Devuelve (carpeta, sha base, sha cabeza)."""
    if not shutil.which("git"):
        raise Montaje("no hay git")
    d = pathlib.Path(tempfile.mkdtemp(prefix="aceptacion-"))
    _git(d, "init", "-q", "-b", "main")
    todo = {WORKFLOW: YML.read_text(encoding="utf-8"), "app/main.py": "x = 1\n"}
    todo.update(base)
    _escribir(d, todo)
    _git(d, "add", "-A")
    _git(d, "commit", "-qm", "base")
    sha_base = _git(d, "rev-parse", "HEAD")
    _git(d, "checkout", "-qb", "pull-request")
    _escribir(d, cabeza)
    _git(d, "add", "-A")
    _git(d, "commit", "-qm", "cambio", "--allow-empty")
    return d, sha_base, _git(d, "rev-parse", "HEAD")


def _entorno(d, extra):
    if subprocess.run([sys.executable, "-m", "pytest", "--version"], capture_output=True).returncode != 0:
        raise Montaje("pytest no está instalado (python3 -m pip install pytest): la plantilla corre las pruebas con pytest")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GITHUB_", "PYTEST_"))}
    env.update(RUNNER_TEMP=tempfile.mkdtemp(prefix="runner-"),
               GITHUB_WORKFLOW_REF=f"prueba/repo/{WORKFLOW}@refs/pull/1/merge", GITHUB_WORKSPACE=str(d))
    env.update(extra or {})
    return env


def _expresiones(v, contexto):
    return re.sub(r"\$\{\{\s*([^}]*?)\s*\}\}", lambda m: contexto.get(m.group(1), ""), v)


def comprobar(base, cabeza, titulo, extra=None):
    """Corre el workflow entero sobre un pull request y devuelve (código de salida, salida). Como en GitHub, se para en el
    primer paso que falla. extra: variables para las pruebas sembradas (p. ej. dónde escriben sus marcas)."""
    env_wf, pasos = plantilla()
    d, sb, sh = repositorio(base, cabeza)
    contexto = {"github.event.pull_request.base.sha": sb, "github.event.pull_request.head.sha": sh,
                "github.event.pull_request.title": titulo}
    env = _entorno(d, extra)
    env.update({k: _expresiones(v, contexto) for k, v in env_wf.items()})
    salida = []
    for paso in pasos:
        if not paso["run"]:
            continue
        e = dict(env)
        e.update({k: _expresiones(v, contexto) for k, v in paso["env"].items()})
        guion = pathlib.Path(tempfile.mkstemp(suffix=".sh")[1])
        guion.write_text(paso["run"], encoding="utf-8")
        r = subprocess.run(["bash", "--noprofile", "--norc", "-e", str(guion)], cwd=d, env=e, capture_output=True,
                           text=True, stdin=subprocess.DEVNULL, timeout=600)
        salida.append(f"--- paso «{paso['nombre']}» (salida {r.returncode})\n{r.stdout}{r.stderr}")
        if r.returncode != 0:
            return r.returncode, "\n".join(salida)
    return 0, "\n".join(salida)


def prueba_de_pieza(pieza, archivos, extra=None):
    """Corre solo el comando de la plantilla para una pieza (PRUEBA, con {pieza} — o {piezas}, si la plantilla lo cambia —
    puesto a esa pieza) en un repositorio con esos archivos. Devuelve (código de salida, salida)."""
    env_wf, _ = plantilla()
    if "PRUEBA" not in env_wf:
        raise Montaje("la plantilla no tiene PRUEBA")
    d, _, _ = repositorio(archivos, {})
    env = _entorno(d, extra)
    env.update(env_wf)
    env.update(PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTEST_ADDOPTS="", PYTEST_PLUGINS="")
    c = env_wf["PRUEBA"].replace("{piezas}", pieza).replace("{pieza}", pieza)
    r = subprocess.run(["bash", "-c", c], cwd=d, env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=600)
    return r.returncode, r.stdout + r.stderr


# ---------- las pruebas sembradas y lo que dejan ----------
def sembrada(nombre, resultado="pasa", carpeta=None):
    """El texto de un archivo de pruebas de pytest con una prueba que deja su marca («<nombre> <pid>») en $MARCAS y
    luego pasa, falla o se salta."""
    final = {"pasa": "    assert True\n", "falla": "    assert False, 'falla a propósito'\n",
             "saltada": "    import pytest\n    pytest.skip('saltada a propósito')\n"}[resultado]
    return ("import os\n\n\ndef test_" + re.sub(r"\W", "_", nombre) + "():\n"
            f"    with open(os.environ['MARCAS'], 'a', encoding='utf-8') as f:\n"
            f"        f.write('{nombre} ' + str(os.getpid()) + '\\n')\n" + final)


def marcas():
    """Un archivo de marcas nuevo: (variables para comprobar(), función que lee [(nombre, pid)])."""
    f = pathlib.Path(tempfile.mkstemp(prefix="marcas-")[1])

    def leer():
        return [tuple(l.split()) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    return {"MARCAS": str(f)}, leer


def errores(salida):
    """Las líneas de error del workflow (::error::)."""
    return [l for l in salida.splitlines() if "::error::" in l]


def nombra(lineas, pieza):
    return any(re.search(r"(?<![A-Za-z0-9])" + re.escape(pieza) + r"(?![0-9])", l) for l in lineas)


def plantilla_activas():
    env_wf, _ = plantilla()
    return env_wf.get("ACEPTACION", "tests/aceptacion").rstrip("/"), env_wf.get("ACTIVAS", ".github/piezas-activas.txt")


# ---------- informar ----------
class Informe:
    def __init__(self, pieza):
        self.pieza, self.fallos = pieza, 0

    def escenario(self, titulo, problemas, salida=""):
        """problemas: lista de lo que no se cumple (vacía si el escenario se cumple)."""
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
    """Corre cuerpo(informe) y sale con 0, 1 o 2."""
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
    sys.exit(1 if inf.fallos else 0)
