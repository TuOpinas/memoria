#!/usr/bin/env python3
"""Evals del plugin: conversaciones guionadas contra una raíz de prueba, con el plugin cargado y una computadora de
mentira (dispositivo.py), que comprueban lo que Claude hace con las skills, no solo lo que hacen los scripts.

Cuestan tokens del plan (cada escenario es una conversación con el modelo), así que corren antes de publicar una
versión y cuando se pide, no en cada commit. Corren desde una sesión de Claude Code (usan su cuenta) o con una clave
de API en ANTHROPIC_API_KEY.

Uso: python3 pruebas/evals/correr.py [escenario ...] [--modelo opus|sonnet|haiku|<id>] [--salida <carpeta>] [--plugin <carpeta del plugin>]
     sin escenarios corre todos los de escenarios/. El escenario se nombra por su archivo sin «.md».

Cada escenario es un .md con cabecera: raiz (carpeta de pruebas/tablero/ o ruta), cuenta (correo de la conversación),
consola (si/no), plataforma (darwin/win32), max_turnos, preparar (pasos sobre la copia de la raíz antes de empezar),
turnos (lo que la persona dice, en orden), entre (lo que otra persona hace después del turno N: «N paso») y comprobar (las comprobaciones, abajo). Deja en la carpeta de salida un
JSON con las medidas y las comprobaciones de cada escenario, y la transcripción de cada uno.
"""
import argparse
import asyncio
import datetime
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time

AQUI = pathlib.Path(__file__).resolve().parent
REPO = AQUI.parent.parent
PLUGIN = REPO / "plugins" / "memoria"
# donde la sesión tiene sus plugins: /root en las sesiones en la nube; en GitHub (evals.yml) el $HOME del runner
PLUGINS_INSTALADOS = pathlib.Path(os.environ.get("MEMORIA_EVALS_PLUGINS") or "/root/.claude/plugins")
sys.path.insert(0, str(AQUI))
from dispositivo import Dispositivo  # noqa: E402

from zoneinfo import ZoneInfo
HOY = datetime.datetime.now(ZoneInfo("America/Mexico_City")).date().isoformat()   # la zona que se le da a la conversación
ALIAS = {"opus": "claude-opus-5-5", "sonnet": "claude-sonnet-5-5", "haiku": "claude-haiku-5-5", "fable": "claude-fable-5-1"}


# ---------- el escenario ----------
def leer_escenario(p):
    t = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", t, re.S)
    if not m:
        raise SystemExit(f"{p}: sin cabecera")
    e, clave = {"nombre": p.stem, "descripcion": m.group(2).strip()}, None
    for l in m.group(1).split("\n"):
        if not l.strip():
            continue
        if re.match(r"^\s+-\s", l) and clave:
            e.setdefault(clave, []).append(l.strip()[2:].strip().strip('"'))
        elif ":" in l and not l.startswith(" "):
            clave, v = l.split(":", 1)
            clave, v = clave.strip(), v.strip()
            if v:
                e[clave] = v
            else:
                e[clave] = []
    for k in ("turnos", "comprobar", "preparar", "entre"):
        e.setdefault(k, [])
    e["consola"] = e.get("consola", "si").lower() not in ("no", "false")
    e["plataforma"] = e.get("plataforma", "win32" if not e["consola"] else "darwin")
    e["max_turnos"] = int(e.get("max_turnos", 40))
    return e


def preparar_raiz(e, trabajo):
    origen = pathlib.Path(e.get("raiz", "raiz"))
    if not origen.is_absolute():
        origen = AQUI.parent / "tablero" / origen
    raiz = trabajo / "Prueba"
    shutil.copytree(origen, raiz)
    # la cuenta de la conversación es la de quien corre el eval (Claude Code la pone); el escenario dice qué cuenta de la
    # raíz de prueba ocupa esa persona (`cuenta: ana@ejemplo.test`), y en la copia esa cuenta se escribe con el correo real
    real = os.environ.get("CLAUDE_CODE_USER_EMAIL", "").strip().lower()
    papel = e.get("cuenta", "ana@ejemplo.test").lower()
    if not real:
        raise SystemExit("No se sabe la cuenta de la conversación (CLAUDE_CODE_USER_EMAIL): corre los evals desde una sesión de Claude Code, o ponla en esa variable.")
    patron = re.compile(r"(?<![\w.+'-])" + re.escape(papel) + r"(?![\w-])", re.I)
    if real != papel:
        for d, _, fs in os.walk(raiz):
            for f in fs:
                if f.endswith(".md"):
                    p = pathlib.Path(d, f)
                    t = p.read_text(encoding="utf-8", errors="replace")
                    if real in t.lower():
                        raise SystemExit(f"{e['nombre']}: la cuenta real {real} ya aparece en {p.relative_to(raiz)}: tendría dos papeles.")
                    if patron.search(t):
                        p.write_text(patron.sub(real, t), encoding="utf-8")
    # fechas de archivo fijas, como en probar.sh: todo del 2026-08-01
    viejo = time.mktime((2026, 8, 1, 12, 0, 0, 0, 0, -1))
    for d, _, fs in os.walk(raiz):
        for f in fs:
            os.utime(os.path.join(d, f), (viejo, viejo))
    for paso in e["preparar"]:
        aplicar_paso(e, raiz, paso)
    return raiz


def aplicar_paso(e, raiz, paso):
    """Un paso de «preparar» (antes de empezar) o de «entre» (después de un turno: lo que otra persona hace mientras)."""
    if True:
        orden, _, arg = paso.partition(" ")
        if orden == "copia-en-conflicto":      # copia-en-conflicto <ruta.md>: una copia «(1)» con una entrada más
            p = raiz / arg
            t = p.read_text(encoding="utf-8")
            partes = t.split("\n## ", 1)
            extra = "## 2026-09-30 (desde otra computadora)\nSesión de: Carla Prueba\nTrabajamos en: la copia en conflicto, para la prueba.\nAvances: ENTRADA-CONFLICTO escrita en la otra copia.\nPendiente: nada.\n\n"
            (p.parent / (p.stem + " (1)" + p.suffix)).write_text(partes[0] + "\n" + extra + ("## " + partes[1] if len(partes) > 1 else ""), encoding="utf-8")
        elif orden == "migrar":                # migrar: la raíz pasa a la estructura de la 1.22 por la cuenta del escenario, antes de empezar
            real = os.environ.get("CLAUDE_CODE_USER_EMAIL", "").strip().lower() or e.get("cuenta", "ana@ejemplo.test")
            r = subprocess.run([sys.executable, str(AQUI.parent.parent / "plugins/memoria/skills/sesion/migrar_estructura.py"), str(raiz), "--cuenta", real, "--plugin", "1.22.0"], capture_output=True, text=True)
            if r.returncode != 0:
                raise SystemExit(f"{e['nombre']}: la migración de preparar falló: {r.stdout[-400:]} {r.stderr[-400:]}")
            viejo = time.mktime((2026, 8, 1, 12, 0, 0, 0, 0, -1))
            for d, _, fs in os.walk(raiz):
                for f in fs:
                    os.utime(os.path.join(d, f), (viejo, viejo))
        elif orden == "personas":              # personas: «Quién es quién» (1.26) por la cuenta del escenario, con los nombres que la raíz no dice
            real = os.environ.get("CLAUDE_CODE_USER_EMAIL", "").strip().lower() or e.get("cuenta", "ana@ejemplo.test")
            r = subprocess.run([sys.executable, str(AQUI.parent.parent / "plugins/memoria/skills/sesion/migrar_estructura.py"), str(raiz), "--cuenta", real,
                                "--personas", "--plugin", "1.26.0", "--nombres", "carla@ejemplo.test=Carla Prueba,eva@ejemplo.test=Eva Prueba"], capture_output=True, text=True)
            if r.returncode != 0 or (json.loads(r.stdout or "{}").get("personas") or {}).get("no_se_migra"):
                raise SystemExit(f"{e['nombre']}: la migración de las personas de preparar falló: {r.stdout[-400:]} {r.stderr[-400:]}")
            viejo = time.mktime((2026, 8, 1, 12, 0, 0, 0, 0, -1))
            for d, _, fs in os.walk(raiz):
                for f in fs:
                    os.utime(os.path.join(d, f), (viejo, viejo))
        elif orden == "tocar":                 # tocar <ruta>: fecha de archivo de ahora (trabajo sin sesión)
            os.utime(raiz / arg, None)
        elif orden == "escribir":              # escribir <ruta> <texto>: añade una línea al final
            r, _, texto = arg.partition(" ")
            with open(raiz / r, "a", encoding="utf-8") as f:
                f.write(texto + "\n")
        elif orden == "sustituir":             # sustituir <ruta> <viejo> => <nuevo>: cambia un texto del archivo (\n es salto de línea)
            r, _, resto = arg.partition(" ")
            viejo, _, nuevo = resto.partition(" => ")
            viejo, nuevo = viejo.replace("\\n", "\n"), nuevo.replace("\\n", "\n")
            # {HOY-N}: la fecha de hace N días, para que lo que depende de una ventana de días no caduque (revisión de la 1.26)
            nuevo = re.sub(r"\{HOY-(\d+)\}", lambda m: (datetime.date.fromisoformat(HOY) - datetime.timedelta(days=int(m.group(1)))).isoformat(), nuevo)
            t = (raiz / r).read_text(encoding="utf-8")
            if viejo not in t:
                raise SystemExit(f"{e['nombre']}: «{viejo}» no está en {r}")
            (raiz / r).write_text(t.replace(viejo, nuevo, 1), encoding="utf-8")
        elif orden == "nota":                  # nota <ruta> <KB> <aportacion>: una nota de taller de ese tamaño (1.26.10)
            # vieja como el resto (sin «trabajo sin sesión»), en KB de 1000 como los da abrir.py, y con marcas que dicen si se
            # leyó: NOTA-LEIDA-<nombre>-n desde la línea 20, y FIN-NOTA-LEIDA-<nombre> al final (lee, no-lee)
            r, _, resto = arg.partition(" ")
            kb, _, aport = resto.partition(" ")
            marca = "NOTA-LEIDA-" + pathlib.Path(r).stem
            cuerpo = f"---\nestado: borrador\nactualizado: 2026-09-20\naportacion: \"{aport}\"\n---\n\n# {aport}\n\n"
            n = 1
            while len(cuerpo.encode("utf-8")) < int(kb) * 1000:
                cuerpo += f"- Incidencia {n}: soporte pidió a cuentas que la respuesta a Cliente Uno saliera en el día; cuentas contestó al día siguiente." + (f" {marca}-{n}" if n >= 20 else "") + "\n"
                n += 1
            cuerpo += f"\nFIN-{marca}\n"
            (raiz / r).parent.mkdir(parents=True, exist_ok=True)
            (raiz / r).write_text(cuerpo, encoding="utf-8")
            viejo = time.mktime((2026, 8, 1, 12, 0, 0, 0, 0, -1))
            os.utime(raiz / r, (viejo, viejo))
        elif orden == "copiar":                # copiar <archivo de escenarios/> <ruta>: un archivo entero, viejo como el resto (1.27)
            o, _, r = arg.partition(" ")
            t = (AQUI / "escenarios" / o).read_text(encoding="utf-8")
            t = re.sub(r"\{HOY-(\d+)\}", lambda m: (datetime.date.fromisoformat(HOY) - datetime.timedelta(days=int(m.group(1)))).isoformat(), t)
            (raiz / r).parent.mkdir(parents=True, exist_ok=True)
            (raiz / r).write_text(t, encoding="utf-8")
            viejo = time.mktime((2026, 8, 1, 12, 0, 0, 0, 0, -1))
            os.utime(raiz / r, (viejo, viejo))
        elif orden == "otro-cierre":           # otro-cierre <area>/<proyecto>: otra persona cierra sesión ahora (entrada arriba y un paso nuevo)
            ses = raiz / arg / "sesiones.md"
            t = ses.read_text(encoding="utf-8")
            entrada = f"## {HOY} (cierre de otra persona)\nSesión de: Carla Prueba · plugin 1.19.0\nTrabajamos en: OTRO-CIERRE la revisión de la propuesta.\nAvances: OTRO-CIERRE propuesta revisada.\nPendiente: mandarla.\n\n"
            i = t.index("\n## ") + 1 if "\n## " in t else len(t)
            ses.write_text(t[:i] + entrada + t[i:], encoding="utf-8")
            pr = raiz / arg / "proyecto.md"
            tp = pr.read_text(encoding="utf-8")
            pr.write_text(tp.replace("## Siguientes pasos\n", "## Siguientes pasos\n- OTRO-CIERRE mandar la propuesta revisada a Cliente Uno.\n", 1), encoding="utf-8")
        else:
            raise SystemExit(f"{e['nombre']}: paso desconocido «{paso}»")


def huellas(raiz):
    out = {}
    for d, ds, fs in os.walk(raiz):
        # una carpeta nueva y vacía también es una escritura (1.26.6: el mantenimiento crea las que faltan)
        for x in ds:
            out[pathlib.Path(d, x).relative_to(raiz).as_posix() + "/"] = "carpeta"
        for f in fs:
            p = pathlib.Path(d, f)
            out[p.relative_to(raiz).as_posix()] = hashlib.sha1(p.read_bytes()).hexdigest()
    return out


# ---------- el plugin que se prueba ----------
def version_de(p):
    try:
        return json.loads((p / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    except (OSError, ValueError, KeyError):
        return None


def mayor(a, b):
    return tuple(int(x) for x in a.split(".")) > tuple(int(x) for x in b.split("."))


def preparar_plugin(origen, trabajo):
    """Una copia del plugin donde la skill lo encuentra (bajo /root/.claude/plugins, que es donde busca `sesion`),
    con una versión mayor que cualquier otra copia instalada, para que la elija; y metodo.md regenerado con ella."""
    instaladas = [v for p in PLUGINS_INSTALADOS.glob("*/*/memoria*") for v in [version_de(p)] if v and ".trash" not in str(p)]
    version = version_de(origen) or "0.0.0"
    # una rama de versión declara ya en el contrato su mayor.menor (1.22) antes de que release.sh suba plugin.json:
    # la copia del eval lleva al menos esa, para que build-metodo.sh no la rechace
    mc = re.search(r"Versión del método: \*\*(\d+)\.(\d+)\*\*", (origen / "skills/convenciones/SKILL.md").read_text(encoding="utf-8"))
    if mc and not mayor(version, f"{mc.group(1)}.{mc.group(2)}.0") and version != f"{mc.group(1)}.{mc.group(2)}.0":
        version = f"{mc.group(1)}.{mc.group(2)}.0"
    while any(not mayor(version, v) for v in instaladas):
        a, b, c = version.split("."); version = f"{a}.{b}.{int(c) + 1}"
    # restos de una corrida anterior que murió a medias (una copia con versión inventada que la siguiente sesión real
    # elegiría): fuera, siempre, al arrancar
    for viejo in PLUGINS_INSTALADOS.glob("evals*"):
        shutil.rmtree(viejo, ignore_errors=True)
    dest = PLUGINS_INSTALADOS / f"evals-{os.getpid()}" / "memoria"
    shutil.copytree(origen, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    pj = dest / ".claude-plugin" / "plugin.json"
    pj.write_text(re.sub(r'"version":\s*"[^"]+"', f'"version": "{version}"', pj.read_text(encoding="utf-8")), encoding="utf-8")
    # como release.sh: los scripts que comparan su versión con la mínima de la raíz llevan la de esta copia (1.26)
    for s in ("skills/sesion/abrir.py", "skills/sesion/cerrar.py", "skills/sesion/migrar_estructura.py", "skills/tablero/aplicar_cambios.py", "skills/tablero/generar_vista.py"):
        f = dest / s
        f.write_text(re.sub(r'^ESTE_PLUGIN = "[0-9.]+"', f'ESTE_PLUGIN = "{version}"', f.read_text(encoding="utf-8"), count=1, flags=re.M), encoding="utf-8")
    subprocess.run(["bash", str(dest / "build-metodo.sh")], check=True, capture_output=True)
    return dest, version


def sembrar_scripts(plugin, hogar):
    """Lo que las skills traen a la computadora con DESCARGA, ya puesto: así no hace falta red y se prueba la rama."""
    # metodo.md también (1.24.8; desde la 1.24.9 la mínima lo escribe con device_commit_files y no lo necesita aquí)
    for destino, rutas in (("memoria", ["skills/sesion/abrir.py", "skills/sesion/permisos.py", "skills/sesion/cerrar.py", "skills/sesion/migrar_estructura.py", "metodo.md", "verificar.sh", "skills/sesion/mantenimiento.py"]),
                           ("tablero", ["skills/tablero/generar_vista.py", "skills/tablero/aplicar_cambios.py", "skills/tablero/plan_subida.py"])):
        d = hogar / destino
        d.mkdir(parents=True, exist_ok=True)
        for r in rutas:
            shutil.copy2(plugin / r, d / pathlib.Path(r).name)


# ---------- GitHub de mentira (1.27) ----------
def github_falso(e, cwd):
    """Con `github: sin-acceso`, un `gh` de mentira (gh_falso.py) delante en el PATH de la conversación y de device_bash,
    que responde 404 a todo: la skill desarrollo no ve el repositorio, sin red. Sin la clave, nada cambia."""
    g = (e.get("github") or "").strip()
    if not g:
        return {}
    if g != "sin-acceso":
        raise SystemExit(f"github: «{g}»: solo vale «sin-acceso»")
    d = pathlib.Path(cwd) / ".gh-falso"
    d.mkdir(parents=True, exist_ok=True)
    gh = d / "gh"
    gh.write_text(f"#!/bin/sh\nexec {sys.executable} {AQUI / 'gh_falso.py'} \"$@\"\n", encoding="utf-8")
    gh.chmod(0o755)
    return {"PATH": f"{d}:{os.environ.get('PATH', '')}", "GH_TOKEN": "falso"}


# ---------- la conversación ----------
async def conversar(e, disp, plugin, modelo, cwd, transcripcion, tablero=None):
    from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, ClaudeSDKClient, ResultMessage, TextBlock, ToolResultBlock, ToolUseBlock, UserMessage

    # la conversación es de un proyecto de Claude (como en el uso real); la cuenta es la de quien corre el eval, y la
    # raíz de prueba ya la declara en el papel que pide el escenario (preparar_raiz)
    anexo = "# attachedProject\nThis session is attached to the Project \"Prueba\"."
    # como la app, que da a Claude el correo de la cuenta (sin él no sabe con qué --cuenta abrir); en GitHub no hay otra vía
    correo = os.environ.get("CLAUDE_CODE_USER_EMAIL", "").strip()
    if correo:
        anexo = f"# userEmail\nThe user's email address is {correo}.\n" + anexo
    opciones = ClaudeAgentOptions(
        system_prompt={"type": "preset", "preset": "claude_code", "append": anexo},
        mcp_servers={"remote-devices": disp.servidor(), **({"claude-artifacts": tablero.servidor()} if tablero else {})},
        plugins=[{"type": "local", "path": str(plugin)}],
        permission_mode="bypassPermissions",
        model=ALIAS.get(modelo, modelo) if modelo else None,
        max_turns=e["max_turnos"],
        cwd=str(cwd),
        env={"IS_SANDBOX": "1", "TZ": "America/Mexico_City", **disp.entorno},
        setting_sources=[],
    )
    turnos, medidas = [], {"tokens_entrada": 0, "tokens_salida": 0, "cache_leida": 0, "cache_escrita": 0, "costo_usd": 0.0, "duracion_s": 0.0, "llamadas": {}}
    t0 = time.time()
    async with ClaudeSDKClient(options=opciones) as c:
        for i, texto in enumerate(e["turnos"]):
            turno = {"persona": texto, "respuestas": [], "herramientas": [], "huellas": None}
            await c.query(texto)
            async for m in c.receive_response():
                if isinstance(m, AssistantMessage):
                    for b in m.content:
                        if isinstance(b, TextBlock):
                            turno["respuestas"].append(b.text)
                        elif isinstance(b, ToolUseBlock):
                            turno["herramientas"].append({"id": b.id, "nombre": b.name, "entrada": b.input})
                            medidas["llamadas"][b.name] = medidas["llamadas"].get(b.name, 0) + 1
                elif isinstance(m, UserMessage) and isinstance(m.content, list):
                    for b in m.content:
                        if isinstance(b, ToolResultBlock) and turno["herramientas"]:
                            cont = b.content if isinstance(b.content, str) else json.dumps(b.content, ensure_ascii=False)
                            h = next((x for x in turno["herramientas"] if x["id"] == b.tool_use_id), turno["herramientas"][-1])
                            cont = cont or ""
                            # las comprobaciones buscan secciones que pueden quedar lejos (REGISTROS); y el final, que dice si
                            # una lectura llegó entera (FIN- de la nota, 1.26.10)
                            h["resultado"] = cont[:30000] + ("\n[…]\n" + cont[-2000:] if len(cont) > 30000 else "")
                elif isinstance(m, ResultMessage):
                    u = m.usage or {}
                    medidas["tokens_entrada"] += u.get("input_tokens", 0)
                    medidas["tokens_salida"] += u.get("output_tokens", 0)
                    medidas["cache_leida"] += u.get("cache_read_input_tokens", 0)
                    medidas["cache_escrita"] += u.get("cache_creation_input_tokens", 0)
                    medidas["costo_usd"] += m.total_cost_usd or 0
                    medidas["modelos"] = sorted((m.model_usage or {}).keys())
                    if m.is_error:
                        turno["error"] = m.result
            turno["huellas"] = huellas(disp.raiz)
            turnos.append(turno)
            # lo que otra persona hace entre este turno y el siguiente («entre: N paso»)
            for paso in e["entre"]:
                n, _, resto = paso.partition(" ")
                if n.rstrip(":") == str(i + 1):
                    aplicar_paso(e, disp.raiz, resto.strip())
            with open(transcripcion, "a", encoding="utf-8") as f:
                f.write(f"\n\n## Turno {i + 1} · persona\n\n{texto}\n")
                for h in turno["herramientas"]:
                    f.write(f"\n### herramienta · {h['nombre']}\n\n```\n{json.dumps(h['entrada'], ensure_ascii=False)[:1500]}\n```\n")
                    if h.get("resultado"):
                        f.write(f"\n```\n{h['resultado'][:1500]}\n```\n")
                f.write("\n### Claude\n\n" + "\n\n".join(turno["respuestas"]) + "\n")
    medidas["duracion_s"] = round(time.time() - t0, 1)
    medidas["turnos_modelo"] = sum(len(t["herramientas"]) for t in turnos) + len(turnos)
    return turnos, medidas


# ---------- las comprobaciones ----------
def cambiados(antes, despues):
    return sorted(set(k for k in set(antes) | set(despues) if antes.get(k) != despues.get(k)))


def texto_de(turno):
    return "\n".join(turno["respuestas"])


def entradas_registro(texto):
    return re.findall(r"^## (\d{4}-\d{2}-\d{2}.*)$", texto, re.M)


COMPROBACIONES = {}
def comprobacion(nombre):
    def deco(f):
        COMPROBACIONES[nombre] = f
        return f
    return deco


def sin_codigo(t):
    """El texto sin los bloques de código (vallas de ``` o ~~~ al principio de línea, también sin cerrar): un recuadro
    dentro de un bloque de código no es el recuadro (1.23.2)."""
    return re.sub(r"(?ms)^(?:> ?)? {0,3}(`{3,}|~{3,}).*?(?:^(?:> ?)? {0,3}\1[ \t]*$|\Z)", "", t.replace("\r\n", "\n"))


def en_tabla(t, patron):
    """La cabecera va como primera celda de una tabla de Markdown de una columna, fuera de un bloque de código y fuera de
    una cita (la cita es para lo que se enseña antes de escribir, 1.23.2). Vale en negrita, con sangría de hasta tres
    espacios y con los separadores de GFM («|---|», «| --- |», «|:---|»)."""
    return bool(re.search(r"(?m)^ {0,3}\|? *(?:\*\*)?" + patron + r"[^|\n]*\|?[ \t]*\n {0,3}\|? *:?-{3,}:? *\|?[ \t]*$", sin_codigo(t)))


def al_final(t, patron):
    """El recuadro con esa cabecera cierra la respuesta (1.26.10): en el último bloque de texto del turno (lo escrito
    antes de una herramienta no cuenta como respuesta), con texto que no es tabla antes de él, sus filas «Leí:» y «Dejé
    fuera:», y detrás como mucho dos líneas, cada una una pregunta (la de si se lee). Devuelve (bien, por qué)."""
    s = sin_codigo(t)
    ms = list(re.finditer(r"(?m)^ {0,3}\|? *(?:\*\*)?" + patron + r"[^|\n]*\|?[ \t]*\n {0,3}\|? *:?-{3,}:? *\|?[ \t]*$", s))
    if not ms:
        return False, "no es la cabecera de una tabla de una columna"
    m = ms[-1]
    prosa = [l for l in s[:m.start()].splitlines() if l.strip() and not l.lstrip().startswith("|")]
    if not prosa:
        return False, "no hay respuesta antes del recuadro"
    resto = s[m.end():].split("\n")
    filas = []
    while resto and (resto[0].lstrip().startswith("|") or not resto[0].strip()):
        filas.append(resto.pop(0))
    filas = "\n".join(filas)
    if not ("Leí:" in filas and "Dejé fuera:" in filas):
        return False, "al recuadro le falta la fila «Leí:» o la de «Dejé fuera:»"
    lineas = [l for l in resto if l.strip()]
    if len(lineas) > 2 or any("?" not in l for l in lineas):
        return False, f"después del recuadro siguen {len(lineas)} líneas que no son la pregunta: la respuesta no termina con él"
    return True, "cierra la respuesta, con sus dos filas"


def tras_recuadro(t, patron):
    """El texto que sigue al último recuadro con esa cabecera, sin sus filas (1.26.10); vacío si no está."""
    s = sin_codigo(t)
    ms = list(re.finditer(r"(?m)^ {0,3}\|? *(?:\*\*)?" + patron + r"[^\n]*$", s))
    if not ms:
        return ""
    resto = s[ms[-1].end():].split("\n")
    while resto and (resto[0].lstrip().startswith("|") or not resto[0].strip()):
        resto.pop(0)
    return "\n".join(resto)


@comprobacion("recuadro")
def _(ctx, arg):
    """La primera respuesta lleva el recuadro «Memoria de trabajo · …» (1.22.1; antes, «Memoria activa»), como tabla de
    una columna (1.23.2)."""
    t = texto_de(ctx["turnos"][0])
    hay = en_tabla(t, r"Memoria de trabajo ·")
    return hay, "en la primera respuesta" if hay else ("no es una tabla de una columna fuera de cita y de código" if "Memoria de trabajo ·" in t else "no está en la primera respuesta")


@comprobacion("tabla")
def _(ctx, arg):
    """tabla <texto>[@N]: alguna respuesta (o la del turno N) lleva un recuadro cuya cabecera empieza por el texto, como
    tabla de una columna fuera de cita y de código (1.26.6: «Memoria · mantenimiento»)."""
    texto, _, n = arg.partition("@")
    turnos = [ctx["turnos"][int(n) - 1]] if n else ctx["turnos"]
    pat = re.escape(texto.strip()).replace("·", "(?:·|·)")
    hay = any(en_tabla(texto_de(t), pat) for t in turnos)
    return hay, "es una tabla" if hay else f"«{texto.strip()}» no es la cabecera de una tabla de una columna"


def _turnos(ctx, n):
    return [ctx["turnos"][int(n) - 1]] if n else ctx["turnos"]


@comprobacion("sin-tabla")
def _(ctx, arg):
    """sin-tabla <texto>[@N]: ninguna respuesta (o la del turno N) lleva un recuadro con esa cabecera, ni la cabecera
    suelta (1.26.10: la pregunta que se responde con la apertura no lleva «Memoria · lectura»)."""
    texto, _, n = arg.partition("@")
    pat = re.escape(texto.strip())
    malos = [i for i, t in enumerate(_turnos(ctx, n), int(n) if n else 1) if re.search(pat, texto_de(t))]
    return not malos, f"«{texto.strip()}» en el turno {malos[0]}" if malos else f"sin «{texto.strip()}»"


@comprobacion("tabla-al-final")
def _(ctx, arg):
    """tabla-al-final <texto>@N: la respuesta del turno N (su último bloque de texto) termina con el recuadro de esa
    cabecera, con sus filas «Leí:» y «Dejé fuera:»; detrás, como mucho la pregunta de si se lee (1.26.10)."""
    texto, _, n = arg.partition("@")
    r = _turnos(ctx, n)[0]["respuestas"]
    return al_final(r[-1] if r else "", re.escape(texto.strip()))


LEER = re.compile(r"\b(?:le[oaí]|leer(?:la|lo|las|los)?|l[ée]el[oa]s?|abro|abrir(?:la|lo)?)\b", re.I)


@comprobacion("pregunta-leer")
def _(ctx, arg):
    """pregunta-leer <texto>@N: debajo del recuadro «Memoria · lectura» del turno N, en texto y no con la herramienta de
    preguntas, una línea con «?» y un verbo de leer ofrece leer lo que nombra el texto, en esa línea o en la fila «Dejé
    fuera:» (1.26.10)."""
    texto, _, n = arg.partition("@")
    t = _turnos(ctx, n)[0]
    if any(h["nombre"] == "AskUserQuestion" for h in t["herramientas"]):
        return False, "pregunta con la herramienta de preguntas, no en texto bajo el recuadro"
    s = texto_de(t)
    tras = tras_recuadro(s, r"Memoria · lectura")
    fila = next((l for l in sin_codigo(s).splitlines() if l.lstrip().startswith("|") and "Dejé fuera:" in l), "")
    ofrece = [l for l in tras.splitlines() if "?" in l and LEER.search(l)]
    nombra = any(texto.strip().lower() in l.lower() for l in ofrece) or (ofrece and texto.strip().lower() in fila.lower())
    return bool(nombra), "ofrece leerlo, en texto bajo el recuadro" if nombra else (f"la pregunta no nombra «{texto.strip()}»" if ofrece else "no ofrece leer nada bajo el recuadro")


@comprobacion("pregunta-tamano")
def _(ctx, arg):
    """pregunta-tamano @N: en el turno N se pregunta antes de leer, diciendo cuánto pesa: con la herramienta de preguntas,
    o en texto con «?», y en los dos casos con «KB» (1.26.10, una petición de «todo» por encima de 50 KB)."""
    _, _, n = arg.partition("@")
    t = _turnos(ctx, n)[0]
    herr = any(h["nombre"] == "AskUserQuestion" and "KB" in json.dumps(h["entrada"], ensure_ascii=False) for h in t["herramientas"])
    txt = "?" in texto_de(t) and "KB" in texto_de(t)
    return herr or txt, ("con la herramienta" if herr else "en texto") if herr or txt else "no pregunta con el tamaño"


@comprobacion("primera-frase")
def _(ctx, arg):
    """primera-frase <texto>@N: la primera línea de texto de la respuesta del turno N (su último bloque, sin recuadros)
    lo nombra: una respuesta desde una parte lo dice al empezar (1.26.10)."""
    texto, _, n = arg.partition("@")
    r = _turnos(ctx, n)[0]["respuestas"]
    lineas = [l for l in sin_codigo(r[-1] if r else "").splitlines() if l.strip() and not l.lstrip().startswith("|")]
    hay = bool(lineas) and texto.strip().lower() in lineas[0].lower()
    return hay, "la primera frase lo dice" if hay else f"la primera línea no nombra «{texto.strip()}»: «{(lineas[0] if lineas else '')[:80]}»"


def _leidas(t, marca):
    return [h["nombre"] for h in t["herramientas"] if marca in str(h.get("resultado", ""))]


@comprobacion("lee")
def _(ctx, arg):
    """lee <marca>@N: algún resultado de herramienta del turno N trae «FIN-<marca>», la última línea de la nota que
    siembra el paso nota: se leyó entera (1.26.10)."""
    marca, _, n = arg.partition("@")
    h = [x for t in _turnos(ctx, n) for x in _leidas(t, "FIN-" + marca.strip())]
    return bool(h), f"la lee entera con {h[0]}" if h else f"no la lee entera («FIN-{marca.strip()}» no sale en ningún resultado)"


@comprobacion("no-lee")
def _(ctx, arg):
    """no-lee <marca>@N: ningún resultado de herramienta del turno N trae la marca de las líneas del cuerpo de la nota:
    medirla o mirar su cabecera no es leerla (1.26.10)."""
    marca, _, n = arg.partition("@")
    h = [x for t in _turnos(ctx, n) for x in _leidas(t, marca.strip())]
    return not h, f"la lee con {h[0]}" if h else "no abre su cuerpo"


@comprobacion("recuadro-cierre")
def _(ctx, arg):
    """La última respuesta termina el cierre con el recuadro «Memoria · sesión cerrada · …» (1.23), la misma tabla de una
    columna que la apertura y nunca un bloque de código (1.23.2)."""
    t = texto_de(ctx["turnos"][-1])
    pat = r"Memoria (?:·|·) sesión cerrada (?:·|·) \d+ archivos?"
    hay = en_tabla(t, pat)
    return hay, "en la última respuesta" if hay else ("no es una tabla de una columna fuera de cita y de código" if re.search(pat, t) else "no está en la última respuesta")


def cita_antes_de_escribir(t, con_decision=False, hoy=None):
    """Lo que se enseña antes de escribir, fuera de los bloques de código. Desde el cierre corto (1.26.4): las palabras
    «Bitácora» y «Estatus» solas en su línea y la frase del Estatus en cita, «> AAAA-MM-DD · **…»; la entrada de la bitácora
    ya no va en cita (basta su tema en una línea). Con decisión, «Decisiones» y cada decisión entera en cita con
    «## <fecha> · título»; la fecha es la de hoy, o la del Estatus. Devuelve (bien, qué falta)."""
    t = sin_codigo(t)
    sola = lambda w: re.search(r"(?m)^ {0,3}(?:\*\*)?" + w + r"(?:\*\*)?:?[ \t]*$", t)
    est = re.findall(r"(?m)^> ?(\d{4}-\d{2}-\d{2}) · \*\*", t)
    falta = [n for n, c in (("«Bitácora»", sola("Bitácora")), ("«Estatus»", sola("Estatus")), ("la frase del Estatus en cita", est)) if not c]
    if hoy and est and hoy not in est:
        falta.append(f"el Estatus de hoy ({hoy})")
    fecha = hoy if (hoy in est or not est) else max(est)
    if con_decision:
        if not sola("Decisiones"):
            falta.append("«Decisiones»")
        if not (fecha and re.search(r"(?m)^> ?## " + fecha + r" · \S", t)):
            falta.append("cada decisión en cita con su título")
        elif not re.search(r"(?m)^> ?Decidi[oó]\s*:", t) or not re.search(r"(?m)^> ?Por qu[eé]\s*:", t):
            falta.append("la decisión entera en cita (Decidió y Por qué)")
    return not falta, ", ".join(falta)


@comprobacion("cita-antes-de-escribir")
def _(ctx, arg):
    """cita-antes-de-escribir [decision]: la respuesta que pide el sí (la penúltima) enseña lo que se va a registrar en
    cita, tal como quedará escrito, bajo «Decisiones», «Bitácora» y «Estatus» (1.23.2; desde la 1.26.4, del Estatus solo su
    frase); con «decision», también cada decisión entera."""
    arg, _, n = (arg or "").strip().partition("@")
    if n:   # cita-antes-de-escribir solo-decision@N: la respuesta del turno N enseña la decisión en cita, sin cierre (1.26.4)
        if len(ctx["turnos"]) < int(n):
            return False, f"no hubo turno {n}"
        t = sin_codigo(texto_de(ctx["turnos"][int(n) - 1]))
        if arg.strip() == "solo-decision":
            bien = bool(re.search(r"(?m)^> ?## " + HOY + r" · \S", t)) and bool(re.search(r"(?m)^> ?Decidi[oó]\s*:", t))
            return bien, f"la decisión {'está' if bien else 'no está'} en cita en el turno {n}"
        bien, falta = cita_antes_de_escribir(t, arg.strip() == "decision", HOY)
        return bien, f"en el turno {n}" if bien else "falta " + falta
    if len(ctx["turnos"]) < 2:
        return False, "el escenario no tiene un turno de sí"
    bien, falta = cita_antes_de_escribir(texto_de(ctx["turnos"][-2]), arg.strip() == "decision", HOY)
    return bien, "en la respuesta que pide el sí" if bien else "falta " + falta


@comprobacion("escrito-en-el-turno")
def _(ctx, arg):
    """escrito-en-el-turno N <ruta>: al terminar el turno N el archivo ya había cambiado (1.26.4: una decisión se escribe en
    cuanto se confirma, antes del cierre)."""
    n, _, r = arg.partition(" ")
    n = int(n)
    if len(ctx["turnos"]) < n:
        return False, f"no hubo turno {n}"
    c = cambiados(ctx["antes"], ctx["turnos"][n - 1]["huellas"])
    return r.strip() in c, f"{r.strip()} {'cambió' if r.strip() in c else 'no había cambiado'} al terminar el turno {n}"


@comprobacion("una-vez")
def _(ctx, arg):
    """una-vez <ruta> <texto>: el archivo de la raíz contiene el texto exactamente una vez (1.26.4: una decisión registrada a
    mitad de sesión no se duplica al cerrar)."""
    r, _, texto = arg.partition(" ")
    p = ctx["raiz"] / r
    n = p.read_text(encoding="utf-8").count(texto) if p.exists() else 0
    return n == 1, f"«{texto}» está {n} veces en {r}"


@comprobacion("sin-escrituras")
def _(ctx, arg):
    c = cambiados(ctx["antes"], ctx["turnos"][-1]["huellas"])
    return not c, "nada cambió en la raíz" if not c else "cambió: " + ", ".join(c)


@comprobacion("nada-hasta-el-turno")
def _(ctx, arg):
    """nada-hasta-el-turno N [<ruta>,...]: la raíz no cambia antes del turno N (lo que se registra se enseña y espera el sí),
    salvo las rutas dichas (metodo.md, que la apertura pone al día)."""
    n, _, salvo = arg.partition(" ")
    n, salvo = int(n), [x.strip() for x in salvo.split(",") if x.strip()]
    for i, t in enumerate(ctx["turnos"][: n - 1], 1):
        c = [x for x in cambiados(ctx["antes"], t["huellas"]) if x not in salvo]
        if c:
            return False, f"ya había cambiado en el turno {i}: " + ", ".join(c)
    return True, f"nada escrito antes del turno {n}"


@comprobacion("apertura-completa")
def _(ctx, arg):
    """apertura-completa <area>/<proyecto>: abrir.py corrió con ese proyecto (no solo --minima)."""
    for t in ctx["turnos"]:
        for h in t["herramientas"]:
            cmd = json.dumps(h["entrada"], ensure_ascii=False)
            if "abrir.py" in cmd and arg in cmd and "--minima" not in cmd and "REGISTROS" in (h.get("resultado") or ""):
                return True, "abrir.py con el proyecto, y respondió"
    return False, "abrir.py no corrió con el proyecto (o no respondió)"


@comprobacion("minima-sin-ejecutar")
def _(ctx, arg):
    """En el primer turno no se ejecuta nada en la computadora (1.24.9): la apertura mínima lee una copia y corre abrir.py en
    el contenedor; device_bash, que el modo Auto frena cuando la petición no es de la memoria, no aparece."""
    n = [h for h in (ctx["turnos"][0]["herramientas"] if ctx["turnos"] else []) if h["nombre"].endswith("device_bash")]
    return (not n), ("sin device_bash en el primer turno" if not n else f"{len(n)} device_bash en el primer turno")


@comprobacion("orden")
def _(ctx, arg):
    """orden <ruta> <texto> | <texto> | …: el archivo de la raíz tiene los textos en ese orden, sin distinguir mayúsculas (1.26.3)."""
    r, _, resto = arg.partition(" ")
    p = ctx["raiz"] / r
    t = p.read_text(encoding="utf-8", errors="replace").lower() if p.exists() else ""
    pos, donde = -1, []
    for x in (s.strip().lower() for s in resto.split("|")):
        i = t.find(x, pos + 1)
        if i < 0:
            return False, f"«{x}» no está en {r} después de lo anterior ({donde})"
        donde.append(i); pos = i
    return True, f"en orden en {r}"


@comprobacion("basado-en")
def _(ctx, arg):
    """basado-en <ruta> <texto>: la cabecera del archivo tiene el texto en su basado_en (1.26.3)."""
    r, _, texto = arg.partition(" ")
    p = ctx["raiz"] / r
    t = p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""
    m = re.match(r"^---\n(.*?)\n---", t, re.S)
    b = re.search(r"^basado_en\s*:(.*(?:\n[ \t]*-.*)*)", m.group(1), re.M) if m else None
    bien = bool(b) and texto in b.group(1)
    return bien, f"«{texto}» {'está' if bien else 'no está'} en el basado_en de {r}"


@comprobacion("decision-reemplaza")
def _(ctx, arg):
    """decision-reemplaza <area>/<proyecto> <texto>: la decisión de hoy de arriba lleva «Reemplaza:» con el texto (1.26.3)."""
    a, _, texto = arg.partition(" ")
    p = ctx["raiz"] / a / "decisiones.md"
    t = p.read_text(encoding="utf-8") if p.exists() else ""
    m = re.search(r"^## " + re.escape(HOY) + r" · .*?(?=^## |\Z)", t, re.M | re.S)
    linea = re.search(r"^Reemplaza\s*:.*$", m.group(0), re.M) if m else None
    bien = bool(linea) and texto.lower() in linea.group(0).lower()
    return bien, (linea.group(0)[:120] if linea else ("la decisión de hoy no lleva «Reemplaza:»" if m else "sin decisión de hoy"))


@comprobacion("decision-sin-reemplaza")
def _(ctx, arg):
    """decision-sin-reemplaza <area>/<proyecto>: hay decisión de hoy arriba y no lleva «Reemplaza:» (1.26.7)."""
    p = ctx["raiz"] / arg.strip() / "decisiones.md"
    t = p.read_text(encoding="utf-8") if p.exists() else ""
    m = re.search(r"^## " + re.escape(HOY) + r" · .*?(?=^## |\Z)", t, re.M | re.S)
    if not m:
        return False, "sin decisión de hoy"
    linea = re.search(r"^Reemplaza\s*:.*$", m.group(0), re.M)
    return not linea, (linea.group(0)[:120] if linea else "sin «Reemplaza:»")


@comprobacion("decision-afecta")
def _(ctx, arg):
    """decision-afecta <area>/<proyecto> <texto>: la decisión de hoy de arriba lleva «Afecta a:» con el texto (1.26.5)."""
    a, _, texto = arg.partition(" ")
    if not texto.strip():
        return False, "decision-afecta pide el texto que tiene que estar en «Afecta a»"
    p = ctx["raiz"] / a / "decisiones.md"
    t = p.read_text(encoding="utf-8") if p.exists() else ""
    m = re.search(r"^## " + re.escape(HOY) + r" · .*?(?=^## |\Z)", t, re.M | re.S)
    if m and m.group(0).strip() in (ctx.get("antes_textos") or {}).get(f"{a}/decisiones.md", ""):
        m = None   # la de hoy tiene que ser nueva, no una que la raíz ya traía
    linea = re.search(r"^Afecta a\s*:.*$", m.group(0), re.M) if m else None
    bien = bool(linea) and re.search(r"(?<![\w/-])" + re.escape(texto.lower()) + r"(?![\w-])", linea.group(0).lower()) is not None
    return bien, (linea.group(0)[:120] if linea else ("la decisión de hoy no lleva «Afecta a:»" if m else "sin decisión de hoy"))


@comprobacion("cita-contiene")
def _(ctx, arg):
    """cita-contiene N <texto>: una línea en cita («> …») de la respuesta del turno N contiene el texto (1.26.5)."""
    n, _, texto = arg.partition(" ")
    if len(ctx["turnos"]) < int(n):
        return False, f"no hubo turno {n}"
    t = sin_codigo(texto_de(ctx["turnos"][int(n) - 1]))
    lineas = [l for l in t.split("\n") if l.lstrip().startswith(">") and texto.lower() in l.lower()]
    return bool(lineas), (lineas[0].strip()[:120] if lineas else f"ninguna línea en cita del turno {n} dice «{texto}»")


@comprobacion("apertura-minima")
def _(ctx, arg):
    for t in ctx["turnos"]:
        for h in t["herramientas"]:
            cmd = json.dumps(h["entrada"], ensure_ascii=False)
            if "abrir.py" in cmd and "--minima" in cmd and "=== CUENTA" in (h.get("resultado") or ""):
                return True, "abrir.py --minima corrió"
    return False, "abrir.py --minima no corrió"


@comprobacion("entrada-sesion")
def _(ctx, arg):
    """entrada-sesion <area>/<proyecto>: sesiones.md tiene una entrada nueva arriba, con la fecha de hoy."""
    p = ctx["raiz"] / arg / "sesiones.md"
    ent = entradas_registro(p.read_text(encoding="utf-8")) if p.exists() else []
    antes = ctx["antes_textos"].get(f"{arg}/sesiones.md", "")
    nuevas = [x for x in ent if x not in entradas_registro(antes)]
    if nuevas and ent[0] in nuevas and ent[0].startswith(HOY):
        return True, f"arriba: «{ent[0]}»"
    return False, "sin entrada nueva de hoy arriba" + (f" (arriba: «{ent[0]}»)" if ent else "")


@comprobacion("decision-registrada")
def _(ctx, arg):
    p = ctx["raiz"] / arg / "decisiones.md"
    ent = entradas_registro(p.read_text(encoding="utf-8")) if p.exists() else []
    antes = entradas_registro(ctx["antes_textos"].get(f"{arg}/decisiones.md", ""))
    nuevas = [x for x in ent if x not in antes]
    return bool(nuevas) and ent[0] in nuevas and ent[0].startswith(HOY), ("registrada: «" + ent[0] + "»") if nuevas else "sin decisión nueva"


@comprobacion("estatus")
@comprobacion("en-corto")
def _(ctx, arg):
    """estatus <area>/<proyecto> (en-corto, su nombre hasta la 1.21): el Estatus de proyecto.md, reescrito hoy, y sin
    un «En corto» al lado: desde la 1.22 el cierre escribe solo el nombre nuevo, también en una raíz sin migrar."""
    p = ctx["raiz"] / arg / "proyecto.md"
    t = p.read_text(encoding="utf-8") if p.exists() else ""
    m = re.search(r"^## Estatus\s*\n(.*?)(?=^## |\Z)", t, re.M | re.S)
    if not m:
        return False, "sin bloque Estatus"
    if re.search(r"^## En corto\s*$", t, re.M):
        return False, "quedó un bloque En corto junto al Estatus"
    cuerpo = m.group(1).strip()
    return cuerpo.startswith(HOY) or HOY in cuerpo.split("\n")[0], "primera línea: " + cuerpo.split("\n")[0][:100]


@comprobacion("nombres-nuevos")
def _(ctx, arg):
    """nombres-nuevos <area>/<proyecto>: lo que escribió esta conversación usa los nombres de la 1.22: la entrada nueva de
    sesiones.md con «Tema:» y sin «Trabajamos en:» ni «Pendiente:», y las decisiones nuevas sin «Descartamos:»."""
    malos = []
    for nombre, prohibidos in (("sesiones.md", ("Trabajamos en:", "Pendiente:")), ("decisiones.md", ("Descartamos:",))):
        p = ctx["raiz"] / arg / nombre
        t = p.read_text(encoding="utf-8") if p.exists() else ""
        antes = ctx["antes_textos"].get(f"{arg}/{nombre}", "")
        nuevas = [b for b in re.split(r"^(?=## )", t, flags=re.M) if b.startswith("## ") and b not in antes]
        for b in nuevas:
            malos += [f"{nombre}: {x}" for x in prohibidos if re.search(r"^" + re.escape(x), b, re.M)]
            if nombre == "sesiones.md" and "(migracion)" not in b.split("\n")[0] and not re.search(r"^Tema:", b, re.M):
                malos.append("sesiones.md: entrada sin «Tema:»")
    return not malos, "; ".join(malos) or "con los nombres nuevos"


@comprobacion("migrada")
def _(ctx, arg):
    """migrada <area>: el área y sus proyectos tienen la estructura de la 1.22 (abrir.py da AL DIA para la cuenta) y cada
    proyecto tiene su entrada «(migracion)»."""
    a = ctx["raiz"] / arg / "area.md"
    ta = a.read_text(encoding="utf-8") if a.exists() else ""
    viejo = [x for x in ("## Panorama", "## Prioridades ahora", "\nDueño:") if x in ta]
    sin_entrada = []
    for d in sorted(x for x in (ctx["raiz"] / arg).iterdir() if (x / "proyecto.md").is_file()):
        tp = (d / "proyecto.md").read_text(encoding="utf-8")
        viejo += [f"{d.name}: {x}" for x in ("## En corto", "## Estado actual", "## Terminado significa", "\nDueño:") if x in tp]
        # la entrada solo se pide donde había algo que migrar (proyecto.md cambió)
        antes_p = ctx["antes_textos"].get(f"{arg}/{d.name}/proyecto.md")
        if antes_p is not None and antes_p != tp and "(migracion)" not in (d / "sesiones.md").read_text(encoding="utf-8"):
            sin_entrada.append(d.name)
    return not viejo and not sin_entrada, ("quedan: " + ", ".join(viejo) if viejo else "") + (f"; sin entrada (migracion): {', '.join(sin_entrada)}" if sin_entrada else "") or "migrada"


@comprobacion("solo-escribe-en")
def _(ctx, arg):
    """solo-escribe-en <carpeta>[,<carpeta>]: todo lo que cambió está dentro de esas carpetas."""
    permitidas = [a.strip().strip("/") for a in arg.split(",")]
    c = cambiados(ctx["antes"], ctx["turnos"][-1]["huellas"])
    fuera = [x for x in c if not any(x == p or x.startswith(p + "/") for p in permitidas)]
    return not fuera, "fuera de lo permitido: " + ", ".join(fuera) if fuera else f"cambió solo dentro de {arg}: " + ", ".join(c)


@comprobacion("sin-rutas-absolutas")
def _(ctx, arg):
    c = cambiados(ctx["antes"], ctx["turnos"][-1]["huellas"])
    malas = []
    for x in c:
        p = ctx["raiz"] / x
        if p.is_file() and p.suffix == ".md" and x != "metodo.md":
            t = p.read_text(encoding="utf-8", errors="replace")
            if re.search(r"/Users/|C:/Users|\$HOME|/mnt/user-data|computer://", t):
                malas.append(x)
    return not malas, "con rutas absolutas: " + ", ".join(malas) if malas else "sin rutas absolutas en lo escrito"


@comprobacion("no-menciona")
def _(ctx, arg):
    for i, t in enumerate(ctx["turnos"], 1):
        if arg.lower() in texto_de(t).lower():
            return False, f"lo menciona en el turno {i}"
    return True, f"no menciona «{arg}»"


@comprobacion("no-menciona-re")
def _(ctx, arg):
    """no-menciona-re <regex>[@N]: ninguna respuesta (o la del turno N) casa con la expresión, sin distinguir mayúsculas."""
    pat, _, n = arg.rpartition("@") if re.search(r"@\d+$", arg) else (arg, "", "")
    turnos = [ctx["turnos"][int(n) - 1]] if n else ctx["turnos"]
    for i, t in enumerate(turnos, int(n) if n else 1):
        m = re.search(pat, texto_de(t), re.I)
        if m:
            return False, f"casa en el turno {i}: «{m.group(0)[:60]}»"
    return True, f"nada casa con «{pat}»"


@comprobacion("menciona")
def _(ctx, arg):
    """menciona <texto>[|<otro>...][@N]: alguna respuesta (o la del turno N) dice alguno de los textos."""
    textos, _, n = arg.partition("@")
    turnos = [ctx["turnos"][int(n) - 1]] if n else ctx["turnos"]
    for t in turnos:
        for texto in textos.split("|"):
            if texto.strip().lower() in texto_de(t).lower():
                return True, f"dice «{texto.strip()}»"
    return False, f"no dice «{textos}»"


@comprobacion("pregunta-claude-outputs")
def _(ctx, arg):
    """La primera respuesta pregunta si se colocan los archivos de «Claude outputs» (AskUserQuestion o texto)."""
    t = ctx["turnos"][0]
    pregunta = any(h["nombre"] == "AskUserQuestion" and "Claude outputs" in json.dumps(h["entrada"], ensure_ascii=False) for h in t["herramientas"])
    pregunta = pregunta or re.search(r"coloco|colocar|(los|las) (pongo|ordeno|muevo)", texto_de(t), re.I) is not None and "Claude outputs" in texto_de(t)
    return pregunta, "pregunta por Claude outputs" if pregunta else "no pregunta por Claude outputs"


@comprobacion("pregunta-antes")
def _(ctx, arg):
    """pregunta-antes N: en el turno N se pregunta si se migra (AskUserQuestion o texto, con «1.22», o con «Quién es quién»
    para la de las personas, 1.26) y la respuesta a lo pedido espera: no propone focos de trabajo en ese turno (1.22.1, la
    pregunta bloqueante)."""
    t = ctx["turnos"][int(arg or 1) - 1]
    marca = lambda s: "1.22" in s or "Quién es quién" in s
    preg = any(h["nombre"] == "AskUserQuestion" and marca(json.dumps(h["entrada"], ensure_ascii=False)) for h in t["herramientas"])
    preg = preg or (marca(texto_de(t)) and "?" in texto_de(t))
    espera = not re.search(r"por cu[aá]l empezamos", texto_de(t), re.I)      # los focos, que cierran la apertura completa
    return preg and espera, ("pregunta y espera" if preg and espera else "no pregunta por la migración" if not preg else "pregunta, pero ya propone focos en el mismo turno")


@comprobacion("contiene")
def _(ctx, arg):
    """contiene <ruta> <texto>: el archivo de la raíz lo contiene al final."""
    r, _, texto = arg.partition(" ")
    p = ctx["raiz"] / r
    t = p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""
    return texto in t, f"«{texto[:60]}» {'está' if texto in t else 'no está'} en {r}"


@comprobacion("no-contiene")
def _(ctx, arg):
    """no-contiene <texto>: ningún .md que cambió en la raíz lo contiene (lo que el cierre nunca guarda)."""
    c = cambiados(ctx["antes"], ctx["turnos"][-1]["huellas"])
    dentro = []
    for x in c:
        p = ctx["raiz"] / x
        if p.is_file() and p.suffix == ".md" and arg.lower() in p.read_text(encoding="utf-8", errors="replace").lower():
            dentro.append(x)
    return not dentro, f"«{arg}» está en: " + ", ".join(dentro) if dentro else f"«{arg}» no quedó en lo escrito"


@comprobacion("cambia")
def _(ctx, arg):
    """cambia <ruta>: el archivo cambió."""
    c = cambiados(ctx["antes"], ctx["turnos"][-1]["huellas"])
    return arg in c, f"{arg} {'cambió' if arg in c else 'no cambió'}"


@comprobacion("existe")
def _(ctx, arg):
    """existe <ruta>: el archivo o la carpeta existe en la raíz al final (1.26.6)."""
    return (ctx["raiz"] / arg).exists(), f"{arg} {'existe' if (ctx['raiz'] / arg).exists() else 'no existe'}"


@comprobacion("no-existe")
def _(ctx, arg):
    return not (ctx["raiz"] / arg).exists(), f"{arg} {'no existe' if not (ctx['raiz'] / arg).exists() else 'sigue ahí'}"


@comprobacion("bloque-igual")
def _(ctx, arg):
    """bloque-igual <ruta> <bloque>: el bloque «## bloque» del archivo quedó como estaba."""
    r, _, nombre = arg.partition(" ")
    bl = lambda t: (re.search(r"^## " + re.escape(nombre) + r"\s*\n(.*?)(?=^## |\Z)", t, re.M | re.S) or [None, ""])[1]
    antes = bl(ctx["antes_textos"].get(r, "")); p = ctx["raiz"] / r
    ahora = bl(p.read_text(encoding="utf-8", errors="replace") if p.exists() else "")
    return antes.strip() == ahora.strip(), f"«{nombre}» de {r} {'igual' if antes.strip() == ahora.strip() else 'cambió'}"


@comprobacion("conserva-entradas")
def _(ctx, arg):
    """conserva-entradas <area>/<proyecto>: sesiones.md tiene todas las entradas del original y de su copia en conflicto."""
    p = ctx["raiz"] / arg / "sesiones.md"
    ent = entradas_registro(p.read_text(encoding="utf-8")) if p.exists() else []
    faltan = []
    for k, t in ctx["antes_textos"].items():
        if k.startswith(arg + "/sesiones") and k.endswith(".md"):
            faltan += [x for x in entradas_registro(t) if x not in ent]
    return not faltan, "faltan: " + "; ".join(faltan) if faltan else f"las {len(ent)} entradas están"


@comprobacion("cierre-con-script")
def _(ctx, arg):
    """El cierre escribió con cerrar.py (una llamada que devolvió «escritos»), no con Write/Edit, ni con un script o una
    redirección propios sobre los cuatro archivos."""
    REG = ("sesiones.md", "decisiones.md", "proyecto.md", "area.md")
    con = sum(1 for t in ctx["turnos"] for h in t["herramientas"] if "cerrar.py" in json.dumps(h["entrada"], ensure_ascii=False) and h["nombre"].endswith(("device_bash", "Bash")) and "escritos" in (h.get("resultado") or ""))
    a_mano = []
    for t in ctx["turnos"]:
        for h in t["herramientas"]:
            ent = json.dumps(h["entrada"], ensure_ascii=False)
            # un Write sobre uno de los cuatro archivos, por su ruta; no el listado o el cambios.json que los nombran (1.25.1)
            if h["nombre"] in ("Write", "Edit", "MultiEdit") and str((h["entrada"] or {}).get("file_path") or "").endswith(REG):
                a_mano.append(h["nombre"])
            elif h["nombre"].endswith(("device_bash", "Bash")) and "cerrar.py" not in ent and re.search(r"(>>?\s*\\?\"?[^\s\"]*|\btee\s+(-a\s+)?\\?\"?[^\s\"]*|sed\s+-i[^;&|]*|open\([^)]*|write_text\([^)]*)(sesiones|decisiones|proyecto|area)\.md", ent) and "cambios" not in ent[:200]:
                a_mano.append(h["nombre"] + ": " + ent[:80])
    return con > 0 and not a_mano, f"cerrar.py con «escritos»: {con}" + (f"; a mano: {'; '.join(a_mano)}" if a_mano else "")


@comprobacion("marca-tablero")
def _(ctx, arg):
    """marca-tablero <area>/<proyecto>: el cierre dejó su marca en la colección «cierres» del tablero de mentira (1.25.1): un
    «set» en cierres/<area>--<proyecto>--<AAAAMMDDHHMM>, con proyecto, nombre, hora (minutos, en Z) y cuenta, sin ifVersion.
    En Smile Pill, el 2026-11-03, dos cierres completos la dejaron sin escribir y el tablero no avisó de nada."""
    tb = ctx.get("tablero")
    if tb is None:
        return False, "el escenario no tiene tablero de mentira"
    pid = arg.strip("/").replace("/", "--")
    marcas = [op for op in tb.escritos if op.get("op") == "set" and re.fullmatch(rf"cierres/{re.escape(pid)}--\d{{12}}", op.get("path") or "")]
    buenas = [op for op in marcas if (d := op.get("data") or {}) and d.get("proyecto") == pid and d.get("nombre") and d.get("cuenta")
              and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z", str(d.get("hora") or "")) and "ifVersion" not in op]
    return len(buenas) == 1 and len(marcas) == 1, f"marcas en cierres: {len(marcas)}, bien formadas: {len(buenas)}" + (f" ({marcas[0]})" if marcas and not buenas else "")


@comprobacion("herramienta")
def _(ctx, arg):
    """herramienta <nombre>: se llamó al menos una vez."""
    n = sum(1 for t in ctx["turnos"] for h in t["herramientas"] if h["nombre"].endswith(arg))
    return n > 0, f"{arg}: {n} llamadas"


@comprobacion("sin-herramienta")
def _(ctx, arg):
    """sin-herramienta <nombre>: no se llamó. Lo que se escribe con Write en el contenedor (/tmp, /mnt/user-data) no cuenta:
    el listado de «Claude outputs» de la apertura mínima (1.25.1) o el listado de una migración sin consola (1.26) no tocan
    la raíz."""
    fuera = lambda h: str((h.get("entrada") or {}).get("file_path", "")).startswith(("/tmp/", "/mnt/user-data/"))
    n = sum(1 for t in ctx["turnos"] for h in t["herramientas"] if h["nombre"].endswith(arg) and not fuera(h))
    return n == 0, f"{arg}: {n} llamadas"


@comprobacion("skill")
def _(ctx, arg):
    """skill <nombre> <N>: la skill se cargó exactamente N veces (con la herramienta Skill; 1.24.8). La apertura mínima no
    carga «sesion» (0) y la completa la carga una vez (1)."""
    nombre, _, n = arg.rpartition(" ")
    c = sum(1 for t in ctx["turnos"] for h in t["herramientas"] if h["nombre"] == "Skill" and str((h["entrada"] or {}).get("skill", "")).split(":")[-1] == nombre)
    return c == int(n), f"{nombre}: {c} cargas (se esperaban {n})"


@comprobacion("sin-buscar-plugin")
def _(ctx, arg):
    """sin-buscar-plugin: ningún comando busca el plugin en disco (find, ls o un glob bajo .claude/plugins) para correr algo
    desde ahí: en modo Auto la app lo frena con un permiso (1.24.7)."""
    malos = []
    for t in ctx["turnos"]:
        for h in t["herramientas"]:
            if h["nombre"].endswith(("Bash", "device_bash")):
                cmd = str((h["entrada"] or {}).get("command", ""))
                if re.search(r"\b(find|ls)\b[^|;&]*\.claude/plugins|\.claude/plugins/\*", cmd):
                    malos.append(cmd[:100])
    return not malos, "ningún comando busca el plugin" if not malos else "; ".join(malos)


@comprobacion("sin-comando")
def _(ctx, arg):
    """sin-comando <regex>: ningún comando de Bash ni de device_bash casa con la expresión, como una palabra (1.27: la
    apertura no lee GitHub, «sin-comando gh»)."""
    malos = [str((h["entrada"] or {}).get("command", ""))[:100] for x in ctx["turnos"] for h in x["herramientas"]
             if h["nombre"].endswith(("Bash", "device_bash"))
             and re.search(r"(?<![\w-])(?:" + arg + r")(?![\w-])", str((h["entrada"] or {}).get("command", "")))]
    return not malos, "ningún comando casa" if not malos else "; ".join(malos)


@comprobacion("palabras-maximo")
def _(ctx, arg):
    """palabras-maximo N[@T]: la respuesta de cada turno (o la del turno T) tiene como mucho N palabras, sin contar el
    recuadro «Memoria de trabajo». Mide que la conversación va al grano: la norma es la del hook («sobra toda palabra que se
    pueda borrar») y la skill estilo; el tope lo fija cada escenario según lo que pregunta."""
    n, _, t = arg.partition("@")
    turnos = [ctx["turnos"][int(t) - 1]] if t else ctx["turnos"]
    peor = 0
    for x in turnos:
        cuerpo = "\n".join(l for l in texto_de(x).split("\n") if not l.startswith("|"))
        peor = max(peor, len(cuerpo.split()))
    return peor <= int(n), f"{peor} palabras (tope {n})"


@comprobacion("sin-ingles")
def _(ctx, arg):
    """sin-ingles: lo que la persona lee de cada turno (el último bloque de texto, después de la última llamada) no
    empieza en inglés. Las notas que el modelo suelta entre llamadas no cuentan: la app no las enseña tal cual."""
    for i, x in enumerate(ctx["turnos"], 1):
        ultimo = x["respuestas"][-1] if x["respuestas"] else ""
        primera = next((l for l in ultimo.split("\n") if l.strip()), "")
        if re.search(r"\b(the|this|is|it's|so|open|let me|I'll|session)\b", primera, re.I) and not re.search(r"[áéíóúñ¿¡]", primera):
            return False, f"el turno {i} empieza en inglés: «{primera[:80]}»"
    return True, "ninguna respuesta empieza en inglés"


@comprobacion("llamadas-maximo")
def _(ctx, arg):
    """llamadas-maximo N[@T]: como mucho N llamadas a herramientas en total (o en el turno T)."""
    n, _, t = arg.partition("@")
    total = len(ctx["turnos"][int(t) - 1]["herramientas"]) if t else sum(len(x["herramientas"]) for x in ctx["turnos"])
    return total <= int(n), f"{total} llamadas (tope {n})"


def comprobar(e, ctx):
    out = []
    for linea in e["comprobar"]:
        nombre, _, arg = linea.partition(" ")
        f = COMPROBACIONES.get(nombre)
        if not f:
            out.append({"comprobacion": linea, "ok": False, "detalle": "comprobación desconocida"}); continue
        try:
            ok, detalle = f(ctx, arg.strip())
        except Exception as ex:  # noqa: BLE001
            ok, detalle = False, f"falló la comprobación: {ex}"
        out.append({"comprobacion": linea, "ok": bool(ok), "detalle": detalle})
    return out


# ---------- correr ----------
def correr(e, plugin, version, modelo, salida):
    trabajo = pathlib.Path(tempfile.mkdtemp(prefix="eval-"))
    raiz = preparar_raiz(e, trabajo)
    uploads = pathlib.Path("/mnt/user-data/uploads") / "Prueba"
    if uploads.exists():
        shutil.rmtree(uploads)
    disp = Dispositivo(raiz, "Prueba", consola=e["consola"], plataforma=e["plataforma"], hogar=trabajo / "hogar")
    sembrar_scripts(plugin, disp.hogar)
    antes = huellas(raiz)
    antes_textos = {k: (raiz / k).read_text(encoding="utf-8", errors="replace") for k in antes if k.endswith(".md")}
    cwd = trabajo / "conversacion"; cwd.mkdir()
    disp.entorno = github_falso(e, cwd)   # el mismo gh de mentira en la conversación y en device_bash (1.27)
    transcripcion = salida / f"{e['nombre']}.md"
    transcripcion.write_text(f"# {e['nombre']} · {modelo or 'modelo por defecto'} · plugin {version} · {HOY}\n\n{e['descripcion']}\n", encoding="utf-8")
    # el tablero de mentira (1.24.8), con la cola que trae el escenario
    tablero = None
    if e.get("tablero"):
        from tablero_falso import TableroFalso
        tablero = TableroFalso(json.loads((AQUI / "escenarios" / e["tablero"]).read_text(encoding="utf-8")))
    turnos, medidas = asyncio.run(conversar(e, disp, plugin, modelo, cwd, transcripcion, tablero))
    ctx = {"turnos": turnos, "antes": antes, "antes_textos": antes_textos, "raiz": raiz, "dispositivo": disp, "tablero": tablero}
    resultado = {"escenario": e["nombre"], "modelo": modelo, "plugin": version, "fecha": HOY, "consola": e["consola"],
                 "medidas": medidas, "archivos_cambiados": cambiados(antes, turnos[-1]["huellas"]) if turnos else [],
                 "comprobaciones": comprobar(e, ctx), "errores": [t["error"] for t in turnos if t.get("error")],
                 "transcripcion": str(transcripcion), "raiz_final": str(raiz)}
    return resultado


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("escenarios", nargs="*")
    ap.add_argument("--modelo", default="opus")
    ap.add_argument("--salida")
    ap.add_argument("--plugin", default=str(PLUGIN))
    a = ap.parse_args()
    nombres = a.escenarios or sorted(p.stem for p in (AQUI / "escenarios").glob("*.md"))
    cerrojo = pathlib.Path(tempfile.gettempdir()) / "memoria-evals.lock"
    try:
        fd = os.open(cerrojo, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise SystemExit(f"Ya hay evals corriendo ({cerrojo}); si no es verdad, borra ese archivo.")
    os.close(fd)
    import atexit, signal
    def limpiar(*_):
        for d in PLUGINS_INSTALADOS.glob("evals*"):
            shutil.rmtree(d, ignore_errors=True)
        shutil.rmtree("/mnt/user-data/uploads/Prueba", ignore_errors=True)
        try:
            cerrojo.unlink()
        except OSError:
            pass
    atexit.register(limpiar)
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, lambda *_: sys.exit(1))
    plugin, version = preparar_plugin(pathlib.Path(a.plugin), None)
    salida = pathlib.Path(a.salida) if a.salida else AQUI / "resultados" / f"{HOY}-{version}-{a.modelo}"
    salida.mkdir(parents=True, exist_ok=True)
    resultados, fallos = [], 0
    try:
        for n in nombres:
            e = leer_escenario(AQUI / "escenarios" / f"{n}.md")
            print(f"\n== {n}", flush=True)
            r = correr(e, plugin, version, a.modelo, salida)
            resultados.append(r)
            m = r["medidas"]
            print(f"   {m['duracion_s']} s · {sum(m['llamadas'].values())} llamadas · {m['tokens_entrada'] + m['cache_leida'] + m['cache_escrita']} tokens entrada · {m['tokens_salida']} salida · ${m['costo_usd']:.2f}")
            for c in r["comprobaciones"]:
                print(("   bien  " if c["ok"] else "   FALLA ") + c["comprobacion"] + " — " + c["detalle"])
                fallos += 0 if c["ok"] else 1
            for err in r["errores"]:
                print("   error: " + str(err)[:300])
            (salida / "resultados.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=1), encoding="utf-8")
    finally:
        limpiar()
    print(f"\n{'Todo bien.' if not fallos else str(fallos) + ' fallo(s).'} Resultados en {salida}")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
