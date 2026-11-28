#!/usr/bin/env python3
"""P35 · Repositories connected only for whoever builds (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-27, en el plan).

- Whoever builds gets write access. Dado a development project whose «Construye» names the account that opens it,
  Cuando the session opens, Entonces the opening asks to connect each repository with write access, as today.
- Anyone else gets nothing at opening. Dado an account named only in «Acepta» or «Audita», or in no role, Cuando the
  session opens, Entonces the opening connects no repository, and says that if what is asked needs the code it connects
  it read-only.
- Several builders. Dado «Construye» with two people, Cuando either of them opens the session, Entonces that account
  gets write access.
- A builder without an account is found by name. Dado «Construye» with a name and no account, and that name with its
  account in «Quién es quién» of `guia.md`, Cuando that account opens the session, Entonces it gets write access; if the
  name is not in «Quién es quién», no account gets it and the opening says why.

Por la apertura de sesión (plugins/memoria/skills/sesion/abrir.py) con --cuenta, sobre la raíz de muestra de
P05_lectores.py escrita en una carpeta temporal, como P23, y lo que imprime en su sección «=== RESPUESTA». Que la sesión
conecte de verdad los repositorios, y con qué permiso, queda para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P35_escritura_solo_para_quien_construye.py (0 pasa, 1 falla, 2 no se montó).
"""
import atexit, json, pathlib, re, shutil, subprocess, sys, tempfile

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from P05_lectores import MUESTRA, flujo  # noqa: E402  (la raíz de muestra, una sola copia; flujo: Informe, principal y Montaje)

REPO = AQUI.parents[1]
ABRIR = REPO / "plugins" / "memoria" / "skills" / "sesion" / "abrir.py"
PORTAL = "ventas/portal"
PROYECTO_MD, GUIA = "ventas/portal/proyecto.md", "guia.md"
REPOSITORIO = "muestra/portal"
ESCRITURA, LECTURA = "con escritura", "solo para leer"
PALABRA = "escritura"   # para quien no construye, la RESPUESTA no la dice en ninguna forma

ANA, MARTA, PABLO, LUIS = "ana@muestra.mx", "marta@muestra.mx", "pablo@muestra.mx", "luis@muestra.mx"
OTRA = "otra@muestra.mx"   # en «Quién es quién» de nadie y en ningún rol

# Quién es quién con cuatro personas con cuenta (Luis, que en la muestra no tiene, pasa a tenerla)
QUIEN = ("- Ana Pérez · ana@muestra.mx\n- Luis Gómez · sin cuenta\n",
         "- Ana Pérez · ana@muestra.mx\n- Luis Gómez · luis@muestra.mx\n- Marta Ruiz · marta@muestra.mx\n"
         "- Pablo Díaz · pablo@muestra.mx\n")
# Los roles: acepta Marta, audita Pablo, construye y administra Ana
ROLES = [(PROYECTO_MD, "Acepta: Ana Pérez (ana@muestra.mx)\n", "Acepta: Marta Ruiz (marta@muestra.mx)\n"),
         (PROYECTO_MD, "Audita: Ana Pérez (ana@muestra.mx)\n", "Audita: Pablo Díaz (pablo@muestra.mx)\n")]
BASE = [(GUIA,) + QUIEN] + ROLES
CONSTRUYE = "Construye: Ana Pérez (ana@muestra.mx)\n"


def construye(linea):
    """El cambio que pone otra línea «Construye:»."""
    return (PROYECTO_MD, CONSTRUYE, f"Construye: {linea}\n")


def abrir(cuenta, cambios=()):
    """Escribe MUESTRA en una carpeta temporal, le hace los cambios (ruta, texto que está una sola vez, texto nuevo) y abre
    la sesión del portal con esa cuenta, desde la raíz del repositorio. Devuelve (código de salida, salida)."""
    if not ABRIR.is_file():
        raise flujo.Montaje(f"no está la apertura de sesión en {ABRIR}")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="aceptacion-p35-"))
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
    r = subprocess.run([sys.executable, "-I", str(ABRIR), str(raiz), PORTAL, "--cuenta", cuenta], cwd=str(REPO),
                       stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                       errors="replace")
    return r.returncode, r.stdout


def respuesta(cuenta, cambios, problemas):
    """El texto de la sección «=== RESPUESTA…» de la apertura con esa cuenta; None (con el porqué) si no la hay."""
    rc, salida = abrir(cuenta, cambios)
    if rc != 0:
        ultimas = [l for l in (salida or "").splitlines() if l.strip()][-3:]
        problemas.append(f"con {cuenta}, la apertura salió con {rc}, no con 0: {' | '.join(ultimas)}")
        return None
    dentro, out = False, []
    for l in salida.splitlines():
        if l.startswith("=== "):
            if dentro:
                break
            dentro = l.startswith("=== RESPUESTA")
            continue
        if dentro:
            out.append(l)
    if not dentro:
        problemas.append(f"con {cuenta}, la apertura no imprimió ninguna sección «=== RESPUESTA»")
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


def con_escritura(cuenta, cambios, problemas):
    """La apertura pide, en un paso que nombra el repositorio, conectarlo con escritura antes de trabajar, como hoy."""
    texto = respuesta(cuenta, cambios, problemas)
    if texto is None:
        return
    todos = pasos(texto)
    con_repo = [p for p in todos if REPOSITORIO in p]
    if not con_repo:
        problemas.append(f"con {cuenta}, ningún paso de la RESPUESTA nombra «{REPOSITORIO}»: "
                         f"pasos = {json.dumps(todos, ensure_ascii=False)[:400]}")
    elif not any(ESCRITURA in p.lower() and "antes de trabajar" in p.lower() for p in con_repo):
        problemas.append(f"con {cuenta}, el paso que nombra «{REPOSITORIO}» no pide conectarlo «{ESCRITURA}» «antes de "
                         f"trabajar»: {json.dumps(con_repo[0], ensure_ascii=False)[:400]}")


def sin_escritura(cuenta, cambios, problemas):
    """La apertura no pide conectar nada con escritura: ninguna línea de la RESPUESTA dice «escritura», en ninguna
    forma («con escritura», «acceso de escritura», ni para decir que no). Devuelve el texto de la RESPUESTA (o None)."""
    texto = respuesta(cuenta, cambios, problemas)
    if texto is None:
        return None
    if not pasos(texto):
        problemas.append(f"con {cuenta}, la RESPUESTA no tiene pasos numerados: no hay apertura que juzgar")
    for l in texto.splitlines():
        if PALABRA in l.lower():
            problemas.append(f"con {cuenta}, que no construye, la RESPUESTA dice «{PALABRA}»: {l.strip()[:300]}")
    return texto


def solo_lectura(cuenta, texto, problemas):
    """Un paso de la RESPUESTA dice que, si hace falta el código, se conecta «solo para leer»."""
    if texto is not None and not any(LECTURA in p.lower() for p in pasos(texto)):
        problemas.append(f"con {cuenta}, ningún paso de la RESPUESTA dice «{LECTURA}»: "
                         f"pasos = {json.dumps(pasos(texto), ensure_ascii=False)[:400]}")


def escenarios(inf):
    # 1 · Quien construye recibe escritura: Ana, en «Construye» con su correo, abre la sesión. Añadido: el mismo
    #     proyecto abierto por Marta, que solo acepta, no la recibe (sin eso la fila pasaría hoy, que todos la reciben)
    problemas = []
    con_escritura(ANA, BASE, problemas)
    sin_escritura(MARTA, BASE, problemas)
    inf.escenario("Whoever builds gets write access", problemas)

    # 2 · Los demás no reciben nada al abrir: Marta (solo «Acepta»), Pablo (solo «Audita») y una cuenta en ningún rol.
    #     Ninguna línea de la RESPUESTA dice «escritura», y un paso dice que, si hace falta el código, se conecta
    #     «solo para leer»
    for cuenta, que in ((MARTA, "only in Acepta"), (PABLO, "only in Audita"), (OTRA, "in no role")):
        problemas = []
        texto = sin_escritura(cuenta, BASE, problemas)
        solo_lectura(cuenta, texto, problemas)
        inf.escenario(f"Anyone else gets nothing at opening ({que})", problemas)

    # 3 · Varios que construyen: «Construye» con Ana y Marta, separadas por « · ». Cada una recibe escritura
    problemas = []
    dos = BASE + [construye("Ana Pérez (ana@muestra.mx) · Marta Ruiz (marta@muestra.mx)")]
    for cuenta in (ANA, MARTA):
        con_escritura(cuenta, dos, problemas)
    inf.escenario("Several builders", problemas)

    # 4 · Quien construye sin cuenta se encuentra por su nombre: «Construye: Luis Gómez», y Luis con su cuenta en
    #     «Quién es quién». Luis recibe escritura; Ana (que administra) no
    problemas = []
    por_nombre = BASE + [construye("Luis Gómez")]
    con_escritura(LUIS, por_nombre, problemas)
    sin_escritura(ANA, por_nombre, problemas)
    inf.escenario("A builder without an account is found by name", problemas)

    #     … y si el nombre no está en «Quién es quién» («Construye: Rosa Vidal»), ninguna cuenta recibe escritura y la
    #     apertura dice por qué: nombra a Rosa Vidal y «Quién es quién»
    problemas = []
    fuera = BASE + [construye("Rosa Vidal")]
    for cuenta in (ANA, MARTA, LUIS, OTRA):
        texto = sin_escritura(cuenta, fuera, problemas)
        if texto is not None:
            for f in ("Rosa Vidal", "Quién es quién"):
                if f.lower() not in texto.lower():
                    problemas.append(f"con {cuenta}, la RESPUESTA no dice por qué nadie recibe escritura: no nombra «{f}»")
    inf.escenario("A builder without an account is found by name (the name is not in «Quién es quién»)", problemas)


flujo.principal("P35", escenarios)
