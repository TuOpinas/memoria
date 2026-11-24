#!/usr/bin/env python3
"""P23 · Opening connects the repositories (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-23, en el plan).

- The opening names the repositories to connect. Dado a development project with «Repositorios: org/repo», Cuando its
  session opens, Entonces the opening's answer tells the session to connect each one with write access before working.
- A repository that cannot be connected is said. Dado a repository the session cannot connect, Cuando the session opens,
  Entonces the answer says so in one line with the reason, and the session goes on.
- Nothing is said in other projects. Dado a project without the «Desarrollo» section, Cuando its session opens, Entonces
  the opening says nothing about repositories.

Por la apertura de sesión (plugins/memoria/skills/sesion/abrir.py) sobre la raíz de muestra de P05_lectores.py (MUESTRA),
escrita en una carpeta temporal, y lo que imprime en su sección «=== RESPUESTA». Que la sesión conecte de verdad los
repositorios queda para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P23_repositorios_al_abrir.py (0 pasa, 1 falla, 2 no se montó).
"""
import atexit, json, pathlib, re, shutil, subprocess, sys, tempfile

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from P05_lectores import MUESTRA, flujo  # noqa: E402  (la raíz de muestra, una sola copia; flujo: Informe, principal y Montaje)

REPO = AQUI.parents[1]
ABRIR = REPO / "plugins" / "memoria" / "skills" / "sesion" / "abrir.py"
CUENTA = "ana@muestra.mx"
PORTAL, CAMPANA = "ventas/portal", "ventas/campana"   # con la sección «## Desarrollo» y sin ella
PROYECTO_MD = "ventas/portal/proyecto.md"
UN_REPO = "Repositorios: muestra/portal\n"
DOS_REPOS = "Repositorios: muestra/portal · muestra/api\n"


def abrir(proyecto, cambios=()):
    """Escribe MUESTRA en una carpeta temporal, le hace los cambios (ruta, texto que está una sola vez, texto nuevo) y abre
    la sesión del proyecto con la apertura del plugin, desde la raíz del repositorio. Devuelve (código de salida, salida)."""
    if not ABRIR.is_file():
        raise flujo.Montaje(f"no está la apertura de sesión en {ABRIR}")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="aceptacion-p23-"))
    atexit.register(shutil.rmtree, tmp, True)
    raiz = tmp / "raiz"
    for ruta, texto in MUESTRA.items():
        (raiz / ruta).parent.mkdir(parents=True, exist_ok=True)
        (raiz / ruta).write_text(texto, encoding="utf-8")
    for ruta, viejo, nuevo in cambios:
        p = raiz / ruta
        texto = p.read_text(encoding="utf-8")
        if texto.count(viejo) != 1:
            raise flujo.Montaje(f"{ruta} de la muestra no tiene una sola vez «{viejo.strip()[:60]}»")
        p.write_text(texto.replace(viejo, nuevo), encoding="utf-8")
    # sin tope propio: lo pone correr.py, que corta la corrida entera y la da por no corrida (2), no por fallada
    r = subprocess.run([sys.executable, "-I", str(ABRIR), str(raiz), proyecto, "--cuenta", CUENTA], cwd=str(REPO),
                       stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                       errors="replace")
    return r.returncode, r.stdout


def respuesta(rc, salida, problemas):
    """El texto de la sección «=== RESPUESTA…», hasta la siguiente «=== » o el final; None (con el porqué) si no la hay."""
    if rc != 0:
        ultimas = [l for l in (salida or "").splitlines() if l.strip()][-3:]
        problemas.append(f"la apertura salió con {rc}, no con 0: {' | '.join(ultimas)}")
        return None
    lineas, dentro, out = salida.splitlines(), False, []
    for l in lineas:
        if l.startswith("=== "):
            if dentro:
                break
            dentro = l.startswith("=== RESPUESTA")
            continue
        if dentro:
            out.append(l)
    if not dentro:
        problemas.append("la apertura no imprimió ninguna sección «=== RESPUESTA»")
        return None
    return "\n".join(out)


def pasos(texto):
    """Los pasos numerados de la RESPUESTA: cada uno desde su línea «N. » hasta la siguiente o el final."""
    out = []
    for l in texto.splitlines():
        if re.match(r"^\s*\d+\.\s", l):
            out.append(l.strip())
        elif out and l.strip():
            out[-1] += "\n" + l.strip()
    return out


def paso_de(texto, repos, problemas):
    """El paso de la RESPUESTA que nombra todos los repositorios, tal cual; None (con el porqué) si no lo hay."""
    todos = pasos(texto)
    if not todos:
        problemas.append("la RESPUESTA no tiene pasos numerados («1. …»)")
        return None
    con_todos = [p for p in todos if all(r in p for r in repos)]
    if not con_todos:
        problemas.append(f"ningún paso de la RESPUESTA nombra {' y '.join('«' + r + '»' for r in repos)}"
                         + (" en el mismo paso" if len(repos) > 1 else "")
                         + f": pasos = {json.dumps(todos, ensure_ascii=False)}")
        return None
    return con_todos[0]


def contiene(problemas, paso, *frases):
    for f in frases:
        if f.lower() not in paso.lower():
            problemas.append(f"el paso que nombra los repositorios no dice «{f}»: {json.dumps(paso, ensure_ascii=False)}")


def escenarios(inf):
    # 1 · La apertura nombra los repositorios que conectar: el portal, con «Repositorios: muestra/portal»
    problemas = []
    texto = respuesta(*abrir(PORTAL), problemas)
    if texto is not None:
        paso = paso_de(texto, ["muestra/portal"], problemas)
        if paso is not None:
            contiene(problemas, paso, "con escritura", "antes de trabajar")
    inf.escenario("La apertura nombra los repositorios que conectar", problemas)

    #     … y cada uno: con dos repositorios, los dos en el mismo paso
    problemas = []
    texto = respuesta(*abrir(PORTAL, [(PROYECTO_MD, UN_REPO, DOS_REPOS)]), problemas)
    if texto is not None:
        paso = paso_de(texto, ["muestra/portal", "muestra/api"], problemas)
        if paso is not None:
            contiene(problemas, paso, "con escritura", "antes de trabajar")
    inf.escenario("La apertura nombra los repositorios que conectar (dos repositorios)", problemas)

    # 2 · Un repositorio que no se puede conectar se dice: el mismo paso pide decirlo en una línea con el motivo, y seguir
    problemas = []
    texto = respuesta(*abrir(PORTAL), problemas)
    if texto is not None:
        paso = paso_de(texto, ["muestra/portal"], problemas)
        if paso is not None:
            contiene(problemas, paso, "una línea", "motivo", "sigue")
    inf.escenario("Un repositorio que no se puede conectar se dice", problemas)

    # 3 · En otros proyectos no se dice nada: la campaña, sin «## Desarrollo». Que haya RESPUESTA con pasos, para que no
    #     pase por no decir nada de nada
    problemas = []
    rc, salida = abrir(CAMPANA)
    texto = respuesta(rc, salida, problemas)
    if texto is not None:
        if not pasos(texto):
            problemas.append("la RESPUESTA de la campaña no tiene pasos numerados: no hay apertura que juzgar")
        # la apertura entera, no solo la RESPUESTA: el escenario dice que no dice nada
        for l in salida.splitlines():
            for f in ("repositorio", "con escritura"):
                if f in l.lower():
                    problemas.append(f"la apertura de la campaña, que no tiene «Desarrollo», dice «{f}»: {l.strip()[:200]}")
    inf.escenario("En otros proyectos no se dice nada", problemas)


flujo.principal("P23", escenarios)
