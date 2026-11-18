#!/usr/bin/env python3
"""El rastro del mantenimiento en el tablero (1.26.8): una entrada «(mantenimiento)» encima de la bitácora no pasa por la
última sesión, no se cuenta como sesión, y su trabajo sin sesión compara con la última entrada que no es un arreglo,
descontando solo lo que la entrada nombra. Con la generación directa y con el inventario de la computadora.

Uso: python3 pruebas/tablero/probar_mantenimiento.py
"""
import datetime, json, os, pathlib, shutil, subprocess, sys, tempfile, time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1])); from comun import dos_corridas
AQUI = pathlib.Path(__file__).resolve().parent
GV = AQUI.parents[1] / "plugins" / "memoria" / "skills" / "tablero" / "generar_vista.py"
PID, CARPETA = "ventas--cuentas", "ventas/cuentas"
fallos = 0


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1


tmp = pathlib.Path(tempfile.mkdtemp())
R = tmp / "raiz"; shutil.copytree(AQUI / "raiz", R)
viejo = time.mktime((2026, 8, 1, 12, 0, 0, 0, 0, -1))
for d, _, fs in os.walk(R):
    for f in fs:
        os.utime(os.path.join(d, f), (viejo, viejo))
pc = R / CARPETA
HOY = datetime.date.today().isoformat()
ahora = time.time()
(pc / "taller/nota-anterior.md").write_text("---\nestado: borrador\nactualizado: " + HOY + "\nbasado_en: []\n---\n# Nota\n", encoding="utf-8")
os.utime(pc / "taller/nota-anterior.md", (ahora - 3700, ahora - 3700))
(pc / "taller/nota-precios.md").write_text("Carla, sin sesión.\n", encoding="utf-8")
os.utime(pc / "taller/nota-precios.md", (ahora - 4000, ahora - 4000))
sm = pc / "sesiones.md"
sm.write_text(sm.read_text(encoding="utf-8").replace("# Sesiones\n", f"# Sesiones\n\n## {HOY} (mantenimiento)\nTema: arreglos del mantenimiento de la carpeta.\n"
              "Arregló: taller/nota-anterior.md (cabecera)\nÚltimo cierre: 2026-10-01T18:00:00-06:00\nEscrita: "
              + datetime.datetime.fromtimestamp(ahora - 3600).astimezone().isoformat(timespec="seconds") + "\nSesión de: mantenimiento de Ana Prueba · plugin 1.26.8\n", 1), encoding="utf-8")
os.utime(sm, (ahora - 3600, ahora - 3600))


def proyecto(sal):
    return json.loads((sal / "proyectos" / f"{PID}.json").read_text(encoding="utf-8"))


try:
    subprocess.run([sys.executable, str(GV), str(R), str(tmp / "sal"), "--version", "prueba"], check=True, stdout=subprocess.DEVNULL)
    p = proyecto(tmp / "sal")
    ok(p.get("ultima_sesion") == "2026-10-01", f"la última sesión es la real, no el arreglo ({p.get('ultima_sesion')})")
    ok(p.get("sesiones_total") == 2, f"el arreglo no cuenta como sesión ({p.get('sesiones_total')})")
    ok(not any("(mantenimiento)" in (s.get("titulo") or "") for s in (p.get("sesiones_recientes") or []) + (p.get("sesiones") or [])), "ni entra en la actividad reciente ni viaja como sesión")
    ok((p.get("arreglos") or [{}])[0].get("arreglo") == ["taller/nota-anterior.md"] and not any("_texto" in s for s in p.get("sesiones") or []),
       f"va aparte, para el Registro, sin su texto entero ({p.get('arreglos')})")
    ss = p.get("sin_sesion") or {}
    arch = [x["archivo"] for x in ss.get("lista") or []]
    ok("taller/nota-precios.md" in arch and "taller/nota-anterior.md" not in arch and ss.get("desde") == "2026-10-01",
       f"el trabajo sin sesión compara con la última entrada que no es un arreglo y descuenta solo lo nombrado ({ss})")
    o1, _, _ = dos_corridas(R, tmp)
    p2 = proyecto(o1)
    arch2 = [x["archivo"] for x in (p2.get("sin_sesion") or {}).get("lista") or []]
    ok("taller/nota-precios.md" in arch2 and "taller/nota-anterior.md" not in arch2 and p2.get("ultima_sesion") == "2026-10-01",
       f"lo mismo con el inventario de la computadora ({arch2})")
    sm.write_text(sm.read_text(encoding="utf-8").replace("# Sesiones\n", f"# Sesiones\n\n## {HOY} (tarea)\nTema: lo marcado como hecho en el tablero.\n", 1), encoding="utf-8")
    os.utime(sm, (ahora - 3500, ahora - 3500))
    subprocess.run([sys.executable, str(GV), str(R), str(tmp / "sal3"), "--version", "prueba"], check=True, stdout=subprocess.DEVNULL)
    p3 = proyecto(tmp / "sal3"); arch4 = [x["archivo"] for x in (p3.get("sin_sesion") or {}).get("lista") or []]
    ok("taller/nota-anterior.md" not in arch4 and "taller/nota-precios.md" in arch4, f"con una tarea encima, lo mismo ({arch4})")
    os.utime(pc / "taller/nota-anterior.md", (ahora - 10, ahora - 10))
    subprocess.run([sys.executable, str(GV), str(R), str(tmp / "sal2"), "--version", "prueba"], check=True, stdout=subprocess.DEVNULL)
    arch3 = [x["archivo"] for x in (proyecto(tmp / "sal2").get("sin_sesion") or {}).get("lista") or []]
    ok("taller/nota-anterior.md" in arch3, "si alguien cambia lo arreglado después, vuelve a salir")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print("\nTodo bien." if not fallos else f"\n{fallos} fallos.")
sys.exit(1 if fallos else 0)
