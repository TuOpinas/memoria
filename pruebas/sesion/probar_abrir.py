#!/usr/bin/env python3
"""Prueba abrir.py (la apertura de sesión en una llamada) contra la raíz inventada de pruebas/tablero/raiz.

Uso: python3 pruebas/sesion/probar_abrir.py
Copia la raíz a una carpeta temporal con fechas de archivo fijas (todo del 2026-08-01 salvo un entregable tocado hoy),
como probar.sh del tablero, y comprueba lo que sale y, sobre todo, lo que no debe salir.
"""
import os, pathlib, shutil, subprocess, sys, tempfile, time

AQUI = pathlib.Path(__file__).resolve().parent
ABRIR = AQUI.parent.parent / "plugins" / "memoria" / "skills" / "sesion" / "abrir.py"
tmp = pathlib.Path(tempfile.mkdtemp())
R = tmp / "raiz"
shutil.copytree(AQUI.parent / "tablero" / "raiz", R)
viejo = time.mktime((2026, 8, 1, 12, 0, 0, 0, 0, -1))
for d, _, fs in os.walk(R):
    for f in fs:
        os.utime(os.path.join(d, f), (viejo, viejo))
os.utime(R / "ventas/cuentas/entregables/kit-cuentas.md", None)
fallos = 0


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t)
    fallos += 0 if c else 1


def abrir(*a):
    r = subprocess.run([sys.executable, str(ABRIR), str(R), *a], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


print("Abrir sesión en una llamada")
c, o = abrir()
ok(c == 0 and "=== METODO" in o and "=== GUIA" in o and "=== PREMISAS VIGENTES" in o, "sin proyecto: nivel 0 (método, guía, premisas)")
ok("`ventas/cuentas/`" in o and "`operacion/soporte/`" in o, "sin proyecto: lista los proyectos de cada área como area/proyecto")
ok("personas/ · restringida" in o and "nomina" not in o, "sin proyecto: de un área restringida solo su nombre y su dueño")
ok("futura/ · su carpeta no está en esta computadora" in o, "un área del mapa sin carpeta se dice tal cual")
ok("P1 ·" not in o and "P3 ·" in o, "solo las premisas vigentes, no las reemplazadas")
ok("=== DECISIONES" not in o and "=== SESIONES" not in o, "sin proyecto no se lee ningún registro")

c, o = abrir("ventas/cuentas", "--cuenta", "ana@ejemplo.test")
ok(c == 0 and "=== PROYECTO ventas/cuentas/proyecto.md" in o, "con proyecto: su proyecto.md")
dec = o.split("=== DECISIONES")[1].split("=== SESIONES")[0]
ok(sum(1 for l in dec.split("\n") if l.startswith("## ")) == 5, "las cinco decisiones más recientes y no más")
ses = o.split("=== SESIONES")[1].split("=== ENTREGABLES")[0]
ok(sum(1 for l in ses.split("\n") if l.startswith("## ")) <= 3, "como mucho tres sesiones")
ok("SECRETO-RESTRINGIDO" not in o, "nunca sale el contenido de restringido/")
ok("ana@ejemplo.test: escribe en ventas, operacion" in o and "responsable de contexto" in o, "dice dónde escribe la cuenta y si responde por el contexto")
ok("Cuestionamiento abierto (operacion/soporte#2026-10-03)" in o, "avisa del cuestionamiento abierto a una decisión del proyecto")
ok("operacion/soporte#2026-09-25" not in o.split("=== AVISOS")[1], "no avisa de un cuestionamiento ya respondido")
ok("Cuestiona a: la premisa P3" in o and "premisa P2" not in o.split("=== AVISOS")[1], "al responsable de contexto, la premisa cuestionada y vigente sí; la reemplazada después, no")
ok("Borrador viejo: entregables/borrador-viejo.md" in o, "avisa del borrador de más de 30 días")
ok("Puede estar desfasado: entregables/kit-cuentas.md" in o, "avisa del entregable con una base más nueva que él")
ok("Trabajo sin sesión" in o and "kit-cuentas.md" in o, "avisa del trabajo sin sesión")
c, o2 = abrir("ventas/cuentas", "--cuenta", "beto@ejemplo.test")
ok("premisa P3" not in o2.split("=== AVISOS")[1], "a otra cuenta no se le avisa de los cuestionamientos a premisas")
c, o3 = abrir("ventas/cuentas")
ok("=== CUENTA" not in o3 and "premisa P3" not in o3.split("=== AVISOS")[1], "sin cuenta, ni áreas propias ni premisas")

c, o = abrir("operacion/soporte")
av = o.split("=== AVISOS")[1]
ok("Le afecta una decisión de ventas/cuentas" in av, "avisa de las decisiones de otros proyectos que lo nombran en «Afecta a:» desde su última sesión de trabajo (una entrada «(tarea)» no cuenta como sesión)")
ok("Decisión recuperada" not in o and "TRABAJO-CUENTAS" not in o, "de otros proyectos no lee sesiones ni decisiones enteras")
c, o = abrir("ventas/precios")
ok(c == 0, "un proyecto declarado restringido que la cuenta puede leer se abre")
c, o = abrir("ventas/no-existe")
ok("no se pudo leer proyecto.md" in o, "un proyecto que no existe se dice y se para")
c, o = abrir("cuentas")
ok(c != 0 and "<area>/<proyecto>" in o, "el proyecto se pide como area/proyecto")
# casos que encontró la revisión de la 1.14.8, sobre la misma copia
(R / "ventas/oculto/decisiones.md").write_text((R / "ventas/oculto/decisiones.md").read_text(encoding="utf-8")
    + "\n## 2026-10-15 · Algo de un proyecto fuera del índice\nDecidió: Ana Prueba\nPor qué: prueba.\nAfecta a: operacion/soporte (SECRETO-OCULTO)\n", encoding="utf-8")
c, o = abrir("operacion/soporte")
ok("SECRETO-OCULTO" not in o, "una decisión de un proyecto que no está en el índice de su área no sale en los avisos")
g = (R / "guia.md").read_text(encoding="utf-8")
(R / "guia.md").write_text(g.replace("Contexto común: Ana Prueba", "Contexto común (`guia.md` y `base/`): Ana Prueba."), encoding="utf-8")
c, o = abrir("ventas/cuentas", "--cuenta", "ana@ejemplo.test")
ok("responsable de contexto" in o and "premisa P3" in o.split("=== AVISOS")[1], "reconoce al responsable de contexto con la línea que escribe la plantilla de nuevo")
pm = (R / "base/premisas.md").read_text(encoding="utf-8")
(R / "base/premisas.md").write_text(pm + "\n- P5 · Desde 2026-01-01 se vende también a cuentas pequeñas · Confirmó: Ana Prueba · 2026-10-10 · Reemplaza a P3\n", encoding="utf-8")
c, o = abrir("ventas/cuentas", "--cuenta", "ana@ejemplo.test")
ok("premisa P3" not in o.split("=== AVISOS")[1], "una premisa que reemplaza a la cuestionada después del cuestionamiento lo responde, aunque su texto lleve otra fecha")
shutil.rmtree(tmp, ignore_errors=True)
print("\nTodo bien." if not fallos else f"\n{fallos} fallos.")
sys.exit(1 if fallos else 0)
