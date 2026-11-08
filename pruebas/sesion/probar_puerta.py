#!/usr/bin/env python3
"""Prueba la puerta de la versión mínima del plugin (1.26): una raíz cuya guia.md declara «Versión mínima del plugin» se lee
con cualquier plugin, pero solo escribe un plugin de esa versión o más nuevo. Sobre la raíz inventada de pruebas/tablero/raiz.

Uso: python3 pruebas/sesion/probar_puerta.py

Comprueba que abrir.py abre en solo lectura (la fila del recuadro, el paso de la RESPUESTA, sin cola del tablero ni migración),
que cerrar.py, aplicar_cambios.py y el veredicto de generar_vista.py se niegan con el código 6 sin escribir nada, que con la
versión justa todo sigue como antes, que una sección sin versión cierra (no abre) la puerta, y que la versión que llevan los
cuatro scripts en ESTE_PLUGIN es la de plugin.json (la pone release.sh).
"""
import json, os, pathlib, re, shutil, subprocess, sys, tempfile, time

AQUI = pathlib.Path(__file__).resolve().parent
PL = AQUI.parent.parent / "plugins" / "memoria"
ABRIR, CERRAR = PL / "skills/sesion/abrir.py", PL / "skills/sesion/cerrar.py"
APLICAR, GENERAR = PL / "skills/tablero/aplicar_cambios.py", PL / "skills/tablero/generar_vista.py"
VERSION = json.loads((PL / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
fallos = 0


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1


def mayor(v):
    a, b, c = (int(x) for x in v.split("."))
    return f"{a}.{b + 1}.0"


def raiz(seccion=None):
    r = pathlib.Path(tempfile.mkdtemp()) / "raiz"
    shutil.copytree(AQUI.parent / "tablero" / "raiz", r)
    viejo = time.mktime((2026, 8, 1, 12, 0, 0, 0, 0, -1))
    for d, _, fs in os.walk(r):
        for n in fs:
            os.utime(os.path.join(d, n), (viejo, viejo))
    if seccion is not None:
        g = r / "guia.md"
        g.write_text(g.read_text(encoding="utf-8").rstrip("\n") + "\n\n## Versión mínima del plugin\n" + seccion + "\n", encoding="utf-8")
        os.utime(g, (viejo, viejo))
    return r


def foto(r):
    return {p: p.read_bytes() for p in r.rglob("*") if p.is_file()}


def corre(*a):
    p = subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def cerrar(r):
    f = r.parent / "cambios.json"
    hoy = subprocess.run([sys.executable, "-c", "import datetime, zoneinfo; print(datetime.datetime.now(zoneinfo.ZoneInfo('America/Mexico_City')).date())"],
                         capture_output=True, text=True).stdout.strip()
    f.write_text(json.dumps({"sesion": f"## {hoy}\nTema: prueba de la puerta.\nAvances: nada.\nSesión de: Ana Prueba · plugin {VERSION}"}, ensure_ascii=False), encoding="utf-8")
    return corre(CERRAR, r, "ventas/cuentas", f, "--cuenta", "ana@ejemplo.test", "--cualquier-fecha")


def aplicar(r):
    cola = r.parent / "cola.json"
    cola.write_text(json.dumps([{"id": "f1", "tipo": "fecha", "proyecto": "ventas--cuentas",
                                 "paso": "Llamar a Cliente Uno antes del 2026-10-06 para cerrar la propuesta.",
                                 "fecha_anterior": "2026-10-06", "fecha_nueva": "2026-10-09"}]), encoding="utf-8")
    return corre(APLICAR, r, cola, "--cuenta", "ana@ejemplo.test")


print("La versión de los scripts")
for s in (ABRIR, CERRAR, APLICAR, GENERAR):
    m = re.search(r'^ESTE_PLUGIN = "([0-9.]+)"', s.read_text(encoding="utf-8"), re.M)
    ok(m and m.group(1) == VERSION, f"{s.name} lleva ESTE_PLUGIN = {VERSION}, la de plugin.json")

print("Una raíz con una versión mínima más nueva que el plugin")
R = raiz(f"{mayor(VERSION)}. Con un plugin anterior, esta carpeta se lee pero no se escribe.")
antes = foto(R)
c, o = corre(ABRIR, R, "ventas/cuentas", "--cuenta", "ana@ejemplo.test")
ok(c == 0 and "=== PROYECTO" in o, "abrir.py lee igual: el proyecto sale entero")
ok(f"ESCRITURA: SOLO LECTURA (plugin {VERSION}, mínima de la raíz {mayor(VERSION)})" in o, "abrir.py dice ESCRITURA: SOLO LECTURA con las dos versiones")
ok("| **Solo lectura:** Tu plugin memoria es la " in o and "Customize → Plugins" in o, "el recuadro lleva la fila «Solo lectura» con cómo actualizar")
ok("Esta conversación es de solo lectura en la carpeta" in o, "la RESPUESTA dice que no se escribe nada")
ok("la cola del tablero" not in o, "sin cola del tablero: resolverla es escribir")
ok("ana@ejemplo.test: escribe en nada: SOLO LECTURA" in o, "CUENTA dice que la cuenta no escribe en nada")
ok("## Versión mínima del plugin" not in o.split("=== GUIA", 1)[1].split("===", 1)[0], "la sección no se repite en GUIA: va en ESCRITURA")
c, o = corre(ABRIR, R, "--minima", "--cuenta", "ana@ejemplo.test")
ok(c == 0 and "| **Solo lectura:**" in o, "la apertura mínima también lleva la fila «Solo lectura»")
c, o = cerrar(R)
ok(c == 6 and json.loads(o.strip().splitlines()[-1]).get("solo_lectura") is True, "cerrar.py se niega con 6 y «solo_lectura»")
c, o = aplicar(R)
ok(c == 6 and "SOLO LECTURA:" in o, "aplicar_cambios.py se niega con 6")
c, o = corre(GENERAR, R, "--veredicto-metodo", (PL / "metodo.md").read_text(encoding="utf-8").splitlines()[0])
ok(c == 6 and o.startswith("SOLO LECTURA:"), "el veredicto del tablero para con 6: la puesta al día no sigue")
ok(foto(R) == antes, "nada de la raíz cambió")

print("Una raíz cuya versión mínima es la del plugin")
R = raiz(f"{VERSION}. Con un plugin anterior, esta carpeta se lee pero no se escribe.")
c, o = corre(ABRIR, R, "ventas/cuentas", "--cuenta", "ana@ejemplo.test")
ok(c == 0 and f"ESCRITURA: abierta (plugin {VERSION}, mínima de la raíz {VERSION})" in o and "Solo lectura" not in o, "abrir.py abre para escribir")
ok("la cola del tablero" in o, "con la cola del tablero, como siempre")
c, o = cerrar(R)
ok(c == 0 and "Sesión de: Ana Prueba" in (R / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8"), "cerrar.py escribe")
c, o = aplicar(R)
ok(c == 0 and json.loads(o)["aplicados"], "aplicar_cambios.py aplica")
c, o = corre(GENERAR, R, "--veredicto-metodo", (PL / "metodo.md").read_text(encoding="utf-8").splitlines()[0])
ok(c == 0 and not o.startswith("SOLO LECTURA"), "el veredicto del tablero sale como siempre")

print("Una sección que no dice qué versión")
R = raiz("La que diga el administrador.")
antes = foto(R)
c, o = corre(ABRIR, R, "ventas/cuentas", "--cuenta", "ana@ejemplo.test")
ok("ESCRITURA: SOLO LECTURA" in o and "no dice qué versión" in o, "abrir.py la toma por cerrada y dice por qué")
c, o = cerrar(R)
ok(c == 6, "cerrar.py se niega")
ok(foto(R) == antes, "nada de la raíz cambió")

print("Una raíz sin la sección")
R = raiz()
c, o = corre(ABRIR, R, "ventas/cuentas", "--cuenta", "ana@ejemplo.test")
ok(c == 0 and "ESCRITURA:" not in o and "Solo lectura" not in o, "abrir.py no dice nada de la puerta")
c, o = cerrar(R)
ok(c == 0, "cerrar.py escribe como siempre")

print("Todo bien." if not fallos else f"{fallos} fallo(s).")
sys.exit(1 if fallos else 0)
