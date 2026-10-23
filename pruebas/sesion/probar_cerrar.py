#!/usr/bin/env python3
"""Prueba cerrar.py (skill sesion): escribe lo del cierre archivo por archivo sin pisar a nadie.

Uso: python3 pruebas/sesion/probar_cerrar.py
"""
import importlib.util, json, os, pathlib, shutil, subprocess, sys, tempfile, threading, time

AQUI = pathlib.Path(__file__).resolve().parent
CERRAR = AQUI.parent.parent / "plugins" / "memoria" / "skills" / "sesion" / "cerrar.py"
fallos = 0


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1


def raiz_nueva():
    r = pathlib.Path(tempfile.mkdtemp()) / "raiz"
    shutil.copytree(AQUI.parent / "tablero" / "raiz", r)
    return r


def corre(raiz, cambios, *extra):
    f = raiz.parent / "cambios.json"; f.write_text(json.dumps(cambios, ensure_ascii=False), encoding="utf-8")
    r = subprocess.run([sys.executable, str(CERRAR), str(raiz), "ventas/cuentas", str(f), *extra], capture_output=True, text=True)
    return r.returncode, (json.loads(r.stdout) if r.stdout.strip().startswith("{") else r.stdout + r.stderr)


HOY = time.strftime("%Y-%m-%d")
SESION = f"## {HOY} (cierre de prueba)\nSesión de: Ana Prueba · plugin 9.9.9\nTrabajamos en: PRUEBA-CERRAR la llamada.\nAvances: PRUEBA-CERRAR cerrada.\nPendiente: nada."
DEC = f"## {HOY} · El soporte de Cliente Uno responde en menos de 24 horas\nDecidió: Ana Prueba\nPor qué: es la condición para firmar."
CAMBIOS = {"sesion": SESION, "decisiones": [DEC],
           "proyecto": {"en_corto": f"**{HOY}: Cliente Uno acepta si el soporte responde en 24 horas.** Siguiente: firmar.",
                        "reemplazos": [{"de": "- Llamar a Cliente Uno antes del 2026-10-06 para cerrar la propuesta.", "a": "- Firmar con Cliente Uno."}]},
           "area": {"linea": "- `cuentas/` — las cuentas grandes; Cliente Uno a punto de firmar", "entregables": ["  - kit-cuentas — guía para preparar una cuenta · actualizado 2026-09-10"]}}

print("cerrar.py: un cierre normal")
R = raiz_nueva()
antes_area = (R / "ventas" / "area.md").read_text(encoding="utf-8")
c, s = corre(R, CAMBIOS, "--version", "9.9.9")
ok(c == 0 and set(s["escritos"]) == {"ventas/cuentas/sesiones.md", "ventas/cuentas/decisiones.md", "ventas/cuentas/proyecto.md", "ventas/area.md"}, f"escribe los cuatro archivos del cierre ({s if c else s['escritos']})")
ses = (R / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8")
ok(ses.index(f"## {HOY} (cierre de prueba)") < ses.index("## 2026-10-01") and "## 2026-10-01 (propuesta enviada)" in ses, "la entrada nueva va arriba y las anteriores siguen")
ok(f"actualizado: {HOY}" in ses.split("---")[1], "la cabecera dice actualizado hoy")
dec = (R / "ventas/cuentas/decisiones.md").read_text(encoding="utf-8")
ok(dec.index(f"## {HOY} · El soporte") < dec.index("## 2026-09-26"), "la decisión nueva va arriba")
pro = (R / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8")
ok("- Firmar con Cliente Uno." in pro and "antes del 2026-10-06" not in pro and "Segundo párrafo con detalle" in pro, "el reemplazo exacto cambia solo ese paso")
ok(f"## En corto\n**{HOY}: Cliente Uno" in pro and pro.index("## En corto") < pro.index("## Objetivo"), "En corto entero, debajo del título")
area = (R / "ventas/area.md").read_text(encoding="utf-8")
ok("Cliente Uno a punto de firmar" in area and "propuesta-base" not in area.split("## Proyectos")[1].split("## ")[0] and "- `precios/` — restringido" in area, "la línea del proyecto y sus entregables se reescriben; las demás líneas no se tocan")
ok(s["sin_match"] == [] and s["ajenos"] == [] and s["hora"].endswith("Z") and s["documento"].startswith("ventas--cuentas--"), "sin_match y ajenos vacíos; hora y documento para la marca del tablero")

print("cerrar.py: repetir no duplica, y un reemplazo que no cuadra se devuelve")
c, s2 = corre(R, CAMBIOS)
ok(s2["escritos"] == [] and ses == (R / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8"), "el mismo cierre otra vez no escribe nada")
c, s3 = corre(R, {"sesion": SESION, "proyecto": {"reemplazos": [{"de": "- Sostener la llamada", "a": "- X"}, {"de": "no está en el archivo", "a": "y"}]}})
ok(len(s3["sin_match"]) == 1 and s3["sin_match"][0]["veces"] == 0 and "- X" in (R / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8"), "el reemplazo que no aparece va a sin_match; el que sí, se aplica")

print("cerrar.py: alguien escribió desde la apertura")
R2 = raiz_nueva()
p = R2 / "ventas/cuentas/proyecto.md"
viejo = time.time() - 7200
for f_ in ("proyecto.md", "sesiones.md", "decisiones.md"):
    os.utime(R2 / "ventas/cuentas" / f_, (viejo, viejo))
os.utime(R2 / "ventas/area.md", (viejo, viejo))
p.write_text(p.read_text(encoding="utf-8") + "\n- Paso que puso otra persona.\n", encoding="utf-8")   # ahora, después de abrir
abierto = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() - 3600))
c, s4 = corre(R2, CAMBIOS, "--abierto", abierto)
ok([a["ruta"] for a in s4["ajenos"]] == ["ventas/cuentas/proyecto.md"] and "- Paso que puso otra persona." in p.read_text(encoding="utf-8") and "- Firmar con Cliente Uno." in p.read_text(encoding="utf-8"), "dice qué archivo cambió otra persona y escribe encima de su versión, no de la de la apertura")

print("cerrar.py: dos cierres a la vez sobre el mismo proyecto")
spec = importlib.util.spec_from_file_location("cerrar", CERRAR); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
R3 = raiz_nueva()
leer_original = m.leer
cruce = threading.Event()
def leer_lento(p):
    """El cierre A lee y, entre la lectura y la escritura, el cierre B escribe: A tiene que verlo y repetir."""
    t = leer_original(p)
    if threading.current_thread().name == "A" and not cruce.is_set():
        cruce.set(); time.sleep(0.4)
    return t
m.leer = leer_lento
cambA = dict(CAMBIOS, sesion=SESION.replace("cierre de prueba", "cierre A"))
cambB = {"sesion": SESION.replace("cierre de prueba", "cierre B"), "proyecto": {"reemplazos": [{"de": "- Sostener la llamada semanal con cada cliente.", "a": "- Llamada quincenal con cada cliente (B)."}]}}
fa, fb = R3.parent / "a.json", R3.parent / "b.json"
fa.write_text(json.dumps(cambA, ensure_ascii=False)); fb.write_text(json.dumps(cambB, ensure_ascii=False))
salidas = {}
def cierre(nombre, f):
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        m.main(["cerrar.py", str(R3), "ventas/cuentas", str(f)])
    salidas[nombre] = json.loads(buf.getvalue())
ta = threading.Thread(target=cierre, args=("A", fa), name="A"); tb = threading.Thread(target=cierre, args=("B", fb), name="B")
ta.start(); cruce.wait(); time.sleep(0.05); tb.start(); ta.join(); tb.join()
ses3 = (R3 / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8"); pro3 = (R3 / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8")
ok("(cierre A)" in ses3 and "(cierre B)" in ses3 and "## 2026-10-01 (propuesta enviada)" in ses3, f"las dos entradas quedan, y la anterior también (reintentos A: {salidas['A']['reintentos']})")
ok("- Firmar con Cliente Uno." in pro3 and "(B)." in pro3, "los pasos que cambió cada cierre quedan los dos")
ok(salidas["A"]["reintentos"] >= 1, "el cierre que leyó antes de la otra escritura lo notó y repitió")

print("\n" + ("Todo bien." if not fallos else f"{fallos} fallo(s)."))
sys.exit(1 if fallos else 0)
