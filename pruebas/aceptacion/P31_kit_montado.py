#!/usr/bin/env python3
"""P31 · The kit set up, or said (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-25, en el plan).

- The opening asks to check the repository. Dado a development project with «Repositorios: org/repo», Cuando its
  session opens, Entonces the opening's answer tells the session to check, in each repository it connects, the kit's
  rules, the control and its runner, and to say in one line what is missing.
- Nothing is said in other projects. Dado a project without the «Desarrollo» section, Cuando its session opens, Entonces
  the opening says nothing about it.

Como P23: la apertura de sesión (plugins/memoria/skills/sesion/abrir.py) sobre la raíz de muestra de P05_lectores.py
(MUESTRA), escrita en una carpeta temporal, y lo que imprime en su sección «=== RESPUESTA». Que la sesión compruebe de
verdad el repositorio queda para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P31_kit_montado.py (0 pasa, 1 falla, 2 no se montó).
"""
import atexit, json, pathlib, re, shutil, subprocess, sys, tempfile

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from P05_lectores import MUESTRA, flujo  # noqa: E402  (la raíz de muestra; flujo: Informe, principal y Montaje)

REPO = AQUI.parents[1]
ABRIR = REPO / "plugins" / "memoria" / "skills" / "sesion" / "abrir.py"
CUENTA = "ana@muestra.mx"
PORTAL, CAMPANA = "ventas/portal", "ventas/campana"   # con la sección «## Desarrollo» y sin ella
REPOSITORIO = "muestra/portal"                         # el de «Repositorios:» del portal en la muestra
PIDE = ("comprueba", "CLAUDE.md", "control", "corredor", "una línea", "falta")
EXACTAS = ("CLAUDE.md",)                               # se buscan con sus mayúsculas; las demás, sin distinguirlas
NO_DICE = ("corredor", "control de pruebas")


def abrir(proyecto):
    """Escribe MUESTRA en una carpeta temporal y abre la sesión del proyecto con la apertura del plugin, desde la raíz
    del repositorio. Devuelve (código de salida, salida)."""
    if not ABRIR.is_file():
        raise flujo.Montaje(f"no está la apertura de sesión en {ABRIR}")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="aceptacion-p31-"))
    atexit.register(shutil.rmtree, tmp, True)
    raiz = tmp / "raiz"
    for ruta, texto in MUESTRA.items():
        (raiz / ruta).parent.mkdir(parents=True, exist_ok=True)
        (raiz / ruta).write_text(texto, encoding="utf-8")
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
    dentro, visto, out = False, False, []
    for l in salida.splitlines():
        if l.startswith("=== "):
            if dentro:
                break
            dentro = l.startswith("=== RESPUESTA")
            visto = visto or dentro
            continue
        if dentro:
            out.append(l)
    if not visto:
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


def falta_en(paso):
    return [f for f in PIDE if (f not in paso if f in EXACTAS else f.lower() not in paso.lower())]


def escenarios(inf):
    # 1 · La apertura pide comprobar el repositorio: el paso que nombra los repositorios, o uno junto a él, pide
    #     comprobar las reglas del kit (CLAUDE.md), el control y su corredor, y decir en una línea lo que falta
    problemas = []
    texto = respuesta(*abrir(PORTAL), problemas)
    if texto is not None:
        todos = pasos(texto)
        donde = [i for i, p in enumerate(todos) if REPOSITORIO in p]
        if not donde:
            problemas.append(f"ningún paso de la RESPUESTA nombra «{REPOSITORIO}»: pasos = {json.dumps(todos, ensure_ascii=False)}")
        else:
            i = donde[0]
            junto = [todos[k] for k in (i, i - 1, i + 1) if 0 <= k < len(todos)]
            if not any(not falta_en(p) for p in junto):
                problemas.append(f"ni el paso que nombra «{REPOSITORIO}» ni uno junto a él dice todo lo que pide comprobar; "
                                 f"al paso que lo nombra le falta {', '.join('«' + f + '»' for f in falta_en(todos[i]))}: "
                                 f"{json.dumps(todos[i], ensure_ascii=False)[:300]}")
    inf.escenario("La apertura pide comprobar el repositorio", problemas)

    # 2 · En otros proyectos no se dice nada: la campaña, sin «## Desarrollo». Que haya RESPUESTA con pasos, para que no
    #     pase por no decir nada de nada
    problemas = []
    texto = respuesta(*abrir(CAMPANA), problemas)
    if texto is not None:
        if not pasos(texto):
            problemas.append("la RESPUESTA de la campaña no tiene pasos numerados: no hay apertura que juzgar")
        for f in NO_DICE:
            for l in texto.splitlines():
                if f in l.lower():
                    problemas.append(f"la RESPUESTA de la campaña, que no tiene «Desarrollo», dice «{f}»: {l.strip()[:200]}")
    inf.escenario("En otros proyectos no se dice nada", problemas)


flujo.principal("P31", escenarios)
