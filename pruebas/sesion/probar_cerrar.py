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


def corre(raiz, cambios, *extra, proyecto="ventas/cuentas", env=None):
    f = raiz.parent / f"cambios-{time.time_ns()}.json"; f.write_text(json.dumps(cambios, ensure_ascii=False), encoding="utf-8")
    r = subprocess.run([sys.executable, str(CERRAR), str(raiz), proyecto, str(f), *extra], capture_output=True, text=True, env={**os.environ, **(env or {})})
    try:
        return r.returncode, json.loads(r.stdout)
    except ValueError:
        return r.returncode, r.stdout + r.stderr


from zoneinfo import ZoneInfo
import datetime
HOY = datetime.datetime.now(ZoneInfo("America/Mexico_City")).date().isoformat()   # la zona de la raíz de prueba
SESION = f"## {HOY}\nTrabajamos en: PRUEBA-CERRAR la llamada.\nAvances: PRUEBA-CERRAR cerrada.\nPendiente: nada.\nSesión de: Ana Prueba · plugin 9.9.9"
DEC = f"## {HOY} · El soporte de Cliente Uno responde en menos de 24 horas\nDecidió: Ana Prueba\nPor qué: es la condición para firmar."
CAMBIOS = {"sesion": SESION, "decisiones": [DEC],
           "proyecto": {"en_corto": f"**{HOY}: Cliente Uno acepta si el soporte responde en 24 horas.** Siguiente: firmar.",
                        "reemplazos": [{"de": "- Llamar a Cliente Uno antes del 2026-10-06 para cerrar la propuesta.", "a": "- Firmar con Cliente Uno."}]},
           "area": {"linea": "- `cuentas/` — las cuentas grandes; Cliente Uno a punto de firmar", "entregables": ["  - kit-cuentas — guía para preparar una cuenta · actualizado 2026-09-10"]},
           "panorama": "PANORAMA-NUEVO del área, escrito por el dueño."}

print("cerrar.py: un cierre normal")
R = raiz_nueva()
c, s = corre(R, CAMBIOS, "--cuenta", "ana@ejemplo.test")
ok(c == 0 and set(s["escritos"]) == {"ventas/cuentas/sesiones.md", "ventas/cuentas/decisiones.md", "ventas/cuentas/proyecto.md", "ventas/area.md"}, f"escribe los cuatro archivos del cierre ({s if c else s['escritos']})")
ses = (R / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8")
ok(ses.index(f"## {HOY}\nTrabajamos en: PRUEBA") < ses.index("## 2026-10-01") and "## 2026-10-01 (propuesta enviada)" in ses, "la entrada nueva va arriba y las anteriores siguen")
ok(f"actualizado: {HOY}" in ses.split("---")[1], "la cabecera dice actualizado hoy, en la zona de la organización")
dec = (R / "ventas/cuentas/decisiones.md").read_text(encoding="utf-8")
ok(dec.index(f"## {HOY} · El soporte") < dec.index("## 2026-09-26"), "la decisión nueva va arriba")
pro = (R / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8")
ok("- Firmar con Cliente Uno." in pro and "antes del 2026-10-06" not in pro and "Segundo párrafo con detalle" in pro, "el reemplazo exacto cambia solo ese paso")
ok(f"## En corto\n**{HOY}: Cliente Uno" in pro and pro.index("## En corto") < pro.index("## Objetivo"), "En corto entero, debajo del título")
area = (R / "ventas/area.md").read_text(encoding="utf-8")
ok("Cliente Uno a punto de firmar" in area and "propuesta-base" not in area.split("## Proyectos")[1].split("## ")[0] and "- `precios/` — restringido" in area, "la línea del proyecto y sus entregables se reescriben; las demás líneas no se tocan")
ok("## Panorama\nPANORAMA-NUEVO" in area and area.index("## Proyectos") < area.index("## Panorama") < area.index("## Quién participa"), "el Panorama queda entre Proyectos y Quién participa")
ok(s["sin_match"] == [] and s["ajenos"] == [] and s["rechazados"] == [] and s["fallidos"] == [] and s["hora"].endswith("Z") and s["documento"].startswith("ventas--cuentas--") and "escrito_en" in s, "sin_match, ajenos, rechazados y fallidos vacíos; hora, documento y escrito_en para seguir")
ok(not list((R / "ventas/cuentas").glob("*.cerrar-tmp")), "no deja temporales")

print("cerrar.py: repetir no duplica; un reemplazo que no cuadra, cruza encabezados o encoge se devuelve")
c, s2 = corre(R, CAMBIOS, "--cuenta", "ana@ejemplo.test")
ok(s2["escritos"] == [] and ses == (R / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8"), "el mismo cierre otra vez no escribe nada")
c, s3 = corre(R, {"proyecto": {"reemplazos": [{"de": "- Sostener la llamada", "a": "- X"}, {"de": "no está en el archivo", "a": "y"}]}})
ok(len(s3["sin_match"]) == 1 and s3["sin_match"][0]["veces"] == 0 and "- X" in (R / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8"), "el reemplazo que no aparece va a sin_match; el que sí, se aplica")
pro = (R / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8")
grande = pro[pro.index("## Siguientes pasos"):]
c, s4 = corre(R, {"proyecto": {"reemplazos": [{"de": grande, "a": "## Siguientes pasos\n- Uno solo.\n"}]}})
ok(s4["escritos"] == [] and s4["sin_match"] and "cruza un encabezado" in s4["sin_match"][0]["motivo"], "un reemplazo que cruza un encabezado o pasa de doce líneas no se aplica")
c, s5 = corre(R, {"proyecto": {"reemplazos": [{"de": "## Estado actual\n" + pro.split("## Estado actual\n")[1].split("## Siguientes")[0], "a": "## Estado actual\nx\n\n"}]}})
ok(s5["escritos"] == [] and (s5["rechazados"] or s5["sin_match"]), "un archivo que encogería a menos de la mitad no se escribe sin --forzar")
c, s6 = corre(R, {"sesion": "Trabajamos en: sin fecha"})
ok(c == 1 and "error" in s6 and "sesion" in s6["error"], "una entrada sin «## AAAA-MM-DD» se rechaza antes de escribir nada")

print("cerrar.py: la cuenta que solo colabora, y «otros» fuera del área")
R2 = raiz_nueva()
c, s7 = corre(R2, CAMBIOS, "--cuenta", "carla@ejemplo.test")
ok("ventas/cuentas/sesiones.md" in s7["escritos"] and "ventas/area.md" in s7["escritos"] and any("Panorama" in r["motivo"] for r in s7["rechazados"]) and "PANORAMA-NUEVO" not in (R2 / "ventas/area.md").read_text(encoding="utf-8") and "Cliente Uno a punto de firmar" in (R2 / "ventas/area.md").read_text(encoding="utf-8"), "quien colabora en el área escribe la línea del proyecto pero no el Panorama")
c, s8 = corre(R2, {"sesion": SESION, "area": {"linea": "- `soporte/` — x"}, "panorama": "y"}, "--cuenta", "carla@ejemplo.test", proyecto="operacion/soporte")
ok(len(s8["rechazados"]) == 2 and "operacion/area.md" not in s8["escritos"], "quien no es del área no escribe su area.md: se le dice que se lo pase al dueño")
c, s9 = corre(R2, {"otros": [{"ruta": "guia.md", "reemplazos": [{"de": "Ana Prueba", "a": "X"}]}]})
ok(c == 1 and "guia.md" in s9.get("error", ""), "«otros» nunca toca guia.md")
c, s10 = corre(R2, {"otros": [{"ruta": "operacion/soporte/proyecto.md", "reemplazos": [{"de": "## Objetivo", "a": "## Objetivo"}]}]})
ok(s10["rechazados"] and "fuera del área" in s10["rechazados"][0]["motivo"] and s10["escritos"] == [], "«otros» fuera del área del proyecto se rechaza sin --fuera-del-area")

print("cerrar.py: alguien escribió desde la apertura; lo propio no cuenta; sin consola no se mira")
R3 = raiz_nueva()
viejo = time.time() - 7200
for f_ in ("proyecto.md", "sesiones.md", "decisiones.md"):
    os.utime(R3 / "ventas/cuentas" / f_, (viejo, viejo))
os.utime(R3 / "ventas/area.md", (viejo, viejo))
p = R3 / "ventas/cuentas/proyecto.md"
p.write_text(p.read_text(encoding="utf-8") + "\n- Paso que puso otra persona.\n", encoding="utf-8")
abierto = datetime.datetime.now(ZoneInfo("America/Mexico_City")).replace(microsecond=0) - datetime.timedelta(hours=1)
c, s11 = corre(R3, CAMBIOS, "--abierto", abierto.isoformat(), "--cuenta", "ana@ejemplo.test")
ok([a["ruta"] for a in s11["ajenos"]] == ["ventas/cuentas/proyecto.md"] and "-06:00" in s11["ajenos"][0]["hora"] or "-05:00" in s11["ajenos"][0]["hora"], f"dice qué archivo cambió otra persona, con la hora en la zona de la organización ({s11['ajenos']})")
ok("- Paso que puso otra persona." in p.read_text(encoding="utf-8") and "- Firmar con Cliente Uno." in p.read_text(encoding="utf-8"), "escribe encima de su versión, no de la de la apertura")
c, s12 = corre(R3, {"proyecto": {"reemplazos": [{"de": "- Paso que puso otra persona.", "a": "- Paso ajeno, visto."}]}}, "--abierto", abierto.isoformat())
ok(s12["ajenos"] == [] and s12["escritos"] == ["ventas/cuentas/proyecto.md"], "la segunda llamada de la misma sesión no da por ajeno lo que ella misma escribió")
R4 = raiz_nueva()
for f_ in ("proyecto.md", "sesiones.md", "decisiones.md"):
    os.utime(R4 / "ventas/cuentas" / f_, None)   # como la copia sin consola: la fecha es la de la traída
c, s13 = corre(R4, CAMBIOS, "--abierto", abierto.isoformat(), "--sin-fechas")
ok(s13["ajenos"] == [] and len(s13["escritos"]) == 4, "con --sin-fechas (la copia) no se mira la fecha de nadie")
c, s14 = corre(raiz_nueva(), {"sesion": SESION}, "--abierto", "ahora: 2026-10-22")
ok(c == 2, "un --abierto que no es una hora ISO se rechaza con un mensaje")

print("cerrar.py: la fecha en la zona de la organización, no en la de la máquina")
R5 = raiz_nueva()
c, s15 = corre(R5, {"sesion": SESION}, env={"TZ": "UTC"})
ok(f"actualizado: {HOY}" in (R5 / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8"), "actualizado lleva la fecha de la organización aunque la máquina esté en UTC")
MANANA = (datetime.date.fromisoformat(HOY) + datetime.timedelta(days=1)).isoformat()
AYER = (datetime.date.fromisoformat(HOY) - datetime.timedelta(days=1)).isoformat()
R5b = raiz_nueva()
c, s15b = corre(R5b, {"sesion": SESION.replace(HOY, MANANA)})
ok(c == 1 and "error" in s15b and MANANA in s15b["error"] and HOY in s15b["error"] and "## " + MANANA not in (R5b / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8"), "una entrada fechada mañana (el reloj en UTC) se rechaza diciendo qué día es hoy en la zona")
c, s15c = corre(R5b, {"decisiones": [DEC.replace(HOY, "2026-01-05")]})
ok(c == 1 and "error" in s15c and "2026-01-05" in s15c["error"], "una decisión con una fecha vieja también")
c, s15d = corre(R5b, {"sesion": SESION.replace(HOY, AYER)})
ok(c == 0 and "## " + AYER in (R5b / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8"), "ayer vale: la sesión pudo cruzar la medianoche")
c, s15e = corre(R5b, {"decisiones": [DEC.replace(HOY, "2026-01-05")]}, "--cualquier-fecha")
ok(c == 0 and "## 2026-01-05 · El soporte" in (R5b / "ventas/cuentas/decisiones.md").read_text(encoding="utf-8"), "con --cualquier-fecha pasa una fecha a propósito")

print("cerrar.py: finales de línea de Windows, archivos que faltan y codificación")
R6 = raiz_nueva()
ps = R6 / "ventas/cuentas/sesiones.md"
ps.write_bytes(ps.read_text(encoding="utf-8").replace("\n", "\r\n").encode("utf-8"))
(R6 / "ventas/cuentas/decisiones.md").unlink()
c, s16 = corre(R6, CAMBIOS, "--cuenta", "ana@ejemplo.test")
b = ps.read_bytes()
ok(b"\r\n" in b and b"\n" not in b.replace(b"\r\n", b"") and f"actualizado: {HOY}".encode() in b and b"PRUEBA-CERRAR" in b, "un archivo con CRLF sigue en CRLF entero, con la cabecera al día")
ok(c == 0 and any(f["ruta"] == "ventas/cuentas/decisiones.md" for f in s16["fallidos"]) and "ventas/cuentas/proyecto.md" in s16["escritos"], "un archivo que falta va a fallidos y el resto se escribe igual, con el JSON")
f = R6.parent / "bom.json"; f.write_bytes(b"\xef\xbb\xbf" + json.dumps({"sesion": SESION.replace("PRUEBA", "BOM")}).encode())
r = subprocess.run([sys.executable, str(CERRAR), str(R6), "ventas/cuentas", str(f)], capture_output=True, text=True)
ok(r.returncode == 0 and "BOM-CERRAR" in ps.read_text(encoding="utf-8"), "un cambios.json con BOM se lee")

print("cerrar.py: dos cierres a la vez sobre el mismo proyecto")
spec = importlib.util.spec_from_file_location("cerrar", CERRAR); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
R7 = raiz_nueva()
viejo = time.time() - 7200
for f_ in ("proyecto.md", "sesiones.md", "decisiones.md"):
    os.utime(R7 / "ventas/cuentas" / f_, (viejo, viejo))
os.utime(R7 / "ventas/area.md", (viejo, viejo))
leer_original = m.leer
cruce = threading.Event()
def leer_lento(p):
    """El cierre A lee y se entretiene antes de escribir; B llega mientras: el cerrojo lo hace esperar y después B
    escribe encima de lo de A, y lo de A le sale como ajeno «durante»."""
    t = leer_original(p)
    if threading.current_thread().name == "A" and not cruce.is_set():
        cruce.set(); time.sleep(0.5)
    return t
m.leer = leer_lento
cambA = dict(CAMBIOS, sesion=SESION.replace("PRUEBA-CERRAR la llamada", "cierre A"))
cambB = {"sesion": SESION.replace("PRUEBA-CERRAR la llamada", "cierre B"), "proyecto": {"reemplazos": [{"de": "- Sostener la llamada semanal con cada cliente.", "a": "- Llamada quincenal con cada cliente (B)."}]}}
fa, fb = R7.parent / "a.json", R7.parent / "b.json"
fa.write_text(json.dumps(cambA, ensure_ascii=False)); fb.write_text(json.dumps(cambB, ensure_ascii=False))
salidas = {}
m.print = lambda *a, **k: salidas.__setitem__(threading.current_thread().name, json.loads(a[0]))   # la salida de cada hilo, aparte
def cierre(nombre, f, abierto_):
    m.main(["cerrar.py", str(R7), "ventas/cuentas", str(f), "--abierto", abierto_])
hA = (abierto - datetime.timedelta(minutes=1)).isoformat(); hB = (abierto - datetime.timedelta(minutes=2)).isoformat()
ta = threading.Thread(target=cierre, args=("A", fa, hA), name="A"); tb = threading.Thread(target=cierre, args=("B", fb, hB), name="B")
ta.start(); cruce.wait(); time.sleep(0.05); tb.start(); ta.join(); tb.join()
ses7 = (R7 / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8"); pro7 = (R7 / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8")
ok("cierre A" in ses7 and "cierre B" in ses7 and "## 2026-10-01 (propuesta enviada)" in ses7, "las dos entradas quedan, y la anterior también")
ok("- Firmar con Cliente Uno." in pro7 and "(B)." in pro7, "los pasos que cambió cada cierre quedan los dos")
ok(any(a["ruta"] == "ventas/cuentas/sesiones.md" for a in salidas["B"]["ajenos"]) and not any(a["ruta"] == "ventas/cuentas/sesiones.md" for a in salidas["A"]["ajenos"]), f"cada cierre dice lo que escribió el otro y nunca lo suyo (A: {[a['ruta'] for a in salidas['A']['ajenos']]}; B: {[a['ruta'] for a in salidas['B']['ajenos']]})")

print("\n" + ("Todo bien." if not fallos else f"{fallos} fallo(s)."))
sys.exit(1 if fallos else 0)
