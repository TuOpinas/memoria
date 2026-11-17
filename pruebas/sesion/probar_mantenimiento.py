#!/usr/bin/env python3
"""Prueba mantenimiento.py (skill sesion, anexo mantenimiento.md, 1.26.6): los seis temas de uso, sin escribir, con las
reglas de los demás scripts para lo restringido y las personas (revisión de la 1.26.6, segunda vuelta).

Uso: python3 pruebas/sesion/probar_mantenimiento.py
"""
import datetime, os, pathlib, re, subprocess, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1])); from comun import raiz_migrada

AQUI = pathlib.Path(__file__).resolve().parent
MANT = AQUI.parent.parent / "plugins" / "memoria" / "skills" / "sesion" / "mantenimiento.py"
MIG = AQUI.parent.parent / "plugins" / "memoria" / "skills" / "sesion" / "migrar_estructura.py"
fallos = 0


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1


def escribir(p, t):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(t, encoding="utf-8")


def anadir(p, despues, texto):
    t = p.read_text(encoding="utf-8")
    assert despues in t, (p, despues)
    p.write_text(t.replace(despues, despues + texto, 1), encoding="utf-8")


R, _ = raiz_migrada()
subprocess.run([sys.executable, str(MIG), str(R), "--cuenta", "ana@ejemplo.test", "--personas", "--plugin", "1.26.0",
                "--nombres", "carla@ejemplo.test=Carla Prueba,eva@ejemplo.test=Eva Prueba"], capture_output=True, text=True)
G = R / "guia.md"
anadir(G, "- Dani Prueba · dani@ejemplo.test", "\n- Mariana Ruiz · mariana@ejemplo.test · también: Mari\n- Saúl Prueba · saul@ejemplo.test · baja 2026-09-01\n")
# un área con «Acceso» en negrita: restringida igual, como en abrir.py
g = G.read_text(encoding="utf-8")
g = g.replace("| `personas/` | Nómina y contratos del equipo | Beto Prueba |  | Restringida: dirección | Restringida |",
              "| `personas/` | Nómina y contratos del equipo | Beto Prueba |  | dirección | **Restringida** |")
G.write_text(g, encoding="utf-8")

viejo = time.mktime((2026, 8, 1, 12, 0, 0, 0, 0, -1))
for f in R.rglob("*"):
    os.utime(f, (viejo, viejo))
VC = R / "ventas/cuentas"
anadir(VC / "sesiones.md", "# Sesiones\n", "\n## 2026-11-16\nTema: x.\nAvances: y.\nSesión de: Carla Prueba · plugin 1.25.0 · sin consola\n"
       "\n## 2026-11-15\nTema: x.\nSesión de: Mari · plugin 1.26.6\n")
anadir(VC / "proyecto.md", "## Siguientes pasos\n", "- Que Beto firme el anexo de nómina.\n- Revisar con Ana el margen.\n- Llamar a Mariana Ruiz por el contrato.\n")
anadir(R / "ventas/precios/proyecto.md", "## Siguientes pasos\n", "- SECRETO-PRECIOS: que Carla Prueba apruebe el 40 %.\n")
anadir(R / "personas/nomina/proyecto.md", "## Siguientes pasos\n", "- SECRETO-NOMINA: que Eva Prueba firme el finiquito.\n")
escribir(VC / "taller/nota (1).md", "x")
escribir(VC / "taller/nota.md", "x")
escribir(VC / "taller/resolucion-de-conflictos.md", "x")
escribir(VC / "fuentes/contrato (2).pdf", "x")
for f in list(R.rglob("*")):
    if f.stat().st_mtime > viejo + 1:
        os.utime(f, (viejo, viejo))
from zoneinfo import ZoneInfo
MX = ZoneInfo("America/Mexico_City")
ultimo = datetime.datetime(2026, 11, 16, 17, 0, tzinfo=MX).timestamp()
os.utime(VC / "sesiones.md", (ultimo, ultimo))
# un archivo de la tarde del día del cierre, después de él: en UTC ya es «mañana», en la zona de la organización no
tarde = escribir(VC / "taller/nota-nueva.md", "---\nestado: borrador\n---\n# x\n") or (VC / "taller/nota-nueva.md")
t_ = datetime.datetime(2026, 11, 16, 19, 30, tzinfo=MX).timestamp()   # 01:30 del 17 en UTC
os.utime(tarde, (t_, t_))
# un proyecto terminado con una sesión de esta semana: cuenta para la adopción
DH = R / "archivo/historia"
anadir(DH / "sesiones.md", "# Sesiones\n", "\n## 2026-11-14\nTema: cierre.\nSesión de: Dani Prueba · plugin 1.26.5\n")
# cuestionamientos: uno respondido en un registro archivado, dos del mismo día con respuesta solo al segundo
OS = R / "operacion/soporte"
escribir(R / "ventas/cuentas/decisiones-2026.md", "---\nestado: vigente\n---\n# Decisiones archivadas\n\n## 2026-10-06 · Mantenemos el precio\nDecidió: x.\nResponde a: operacion/soporte#2026-10-03\n")
anadir(OS / "decisiones.md", "# Decisiones\n", "\n## 2026-11-12 · Cuestionamiento: segundo\nPlanteó: Ana Prueba.\nCuestiona a: ventas/cuentas#2026-09-21\n"
       "\n## 2026-11-12 · Cuestionamiento: primero\nPlanteó: Ana Prueba.\nCuestiona a: ventas/cuentas#2026-09-21\n")
anadir(VC / "decisiones.md", "# Decisiones\n", "\n## 2026-11-13 · Respondemos al segundo\nDecidió: x.\nResponde a: operacion/soporte#2026-11-12-2\n")
for f in (R / "ventas/cuentas/decisiones-2026.md", OS / "decisiones.md", VC / "decisiones.md"):
    os.utime(f, (viejo, viejo))

antes = {p: p.stat().st_mtime for p in R.rglob("*") if p.is_file()}
corre = lambda *a: subprocess.run([sys.executable, str(MANT), str(R), "--hoy", "2026-11-17", "--plugin", "1.26.6", *a], capture_output=True, text=True)
r = corre("--cuenta", "ana@ejemplo.test")
o = r.stdout
sec = lambda o, n: o.split("=== " + n)[1].split("\n=== ")[0] if "=== " + n in o else ""

print("mantenimiento.py: el responsable de contexto mira la raíz entera")
ok(r.returncode == 0, f"corre sobre la raíz de prueba ({r.stderr[-300:]})")
ok("administra la carpeta" in sec(o, "CUENTA"), "la cuenta del responsable de contexto se reconoce")
ok("SECRETO-NOMINA" in o and "SECRETO-PRECIOS" in o, "lo restringido se mira: quien administra lo lee todo")
ad = sec(o, "ADOPCION")
ok("Carla Prueba · última sesión el 2026-11-16 en ventas/cuentas · plugin 1.25.0 (anterior al tuyo, 1.26.6)" in ad, "una sesión «sin consola» cuenta, con su plugin")
ok("Mariana Ruiz · última sesión el 2026-11-15" in ad, "una sesión firmada con el alias cuenta para su persona")
ok("Ana Prueba · última sesión el 2026-11-15" not in ad and "Ana Prueba · última sesión el 2026-11-16" not in ad, "la sesión de Mariana no se le cuenta a Ana")
ok("Dani Prueba · última sesión el 2026-11-14 en archivo/historia" in ad, "la sesión de un proyecto terminado cuenta para la adopción")
ok("Saúl" not in ad.split("no cuentan")[0] and "de baja: Saúl Prueba" in ad, "quien está de baja no sale como sin sesiones")
ok("«Ana López»" in ad, "una firma que no es de nadie del registro se dice")
es = sec(o, "ESPERA")
ok("espera a Beto Prueba" in es and "Que Beto firme" in es, "un paso con el nombre de pila único se reconoce")
ok("espera a Ana Prueba" not in es, "Ana lleva ventas/cuentas: un paso que la nombra no le espera «en proyectos de otros»")
ok("te esperan a ti" not in es, "a la cuenta no le espera nada aquí")
cq = sec(o, "CUESTIONAMIENTOS")
ok("operacion/soporte#2026-10-03" not in cq, "un cuestionamiento respondido en un registro archivado no sale abierto")
ok("operacion/soporte#2026-11-12 ·" in cq and "operacion/soporte#2026-11-12-2" not in cq, "responder al -2 no cierra el del mismo día sin sufijo")
ok("responde Ana Prueba" in cq, "dice quién responde")
cf = sec(o, "CONFLICTOS")
ok("nota (1).md" in cf and "resolucion-de-conflictos" not in cf and "contrato (2).pdf" not in cf, f"solo copias en conflicto con su original al lado ({cf.strip()})")
ss = sec(o, "SIN_SESION")
ok("nota-nueva.md · cambió el 2026-11-16 a las 19:30" in ss, f"la fecha va en la zona de la organización, no en UTC ({ss.strip()[:200]})")
ok("personas/nomina" not in ss, "lo que escribe una migración no es trabajo sin sesión")
ok("revisa los permisos" in sec(o, "NO_REVISADO"), "los permisos se dicen como no revisados")
ok(all(p.stat().st_mtime == m for p, m in antes.items()), "no escribe nada")

print("mantenimiento.py: otra cuenta, solo lo suyo")
r = corre("--cuenta", "carla@ejemplo.test")
o = r.stdout
ok(r.returncode == 0 and "no administra la carpeta" in sec(o, "CUENTA") and "ventas (colabora)" in sec(o, "CUENTA"), "la cuenta dice qué es suyo")
ok("SECRETO-PRECIOS" not in o and "SECRETO-NOMINA" not in o and "nomina" not in o and "precios" not in o, "nada restringido que no lleve: ni pasos ni nombres")
ok("operacion" not in sec(o, "CUESTIONAMIENTOS") or "(ninguno" in sec(o, "CUESTIONAMIENTOS"), "lo de áreas ajenas no se mira")
ok("las áreas que no son de esta cuenta" in sec(o, "NO_REVISADO"), "dice que lo demás lo revisa quien administra")

print("mantenimiento.py: argumentos y rutas")
r = subprocess.run([sys.executable, str(MANT), "/tmp/no-es-una-raiz-xyz", "--cuenta", "ana@ejemplo.test"], capture_output=True, text=True)
ok(r.returncode == 2 and "No es una raíz" in r.stdout, "una ruta que no es raíz sale con 2")
for a in (["--cuenta", "ana@ejemplo.test", "--dias", "siete"], ["--cuenta", "ana@ejemplo.test", "--hoy", "17/11/2026"], ["--dias", "7"], ["--cuenta"]):
    r = subprocess.run([sys.executable, str(MANT), str(R), *a], capture_output=True, text=True)
    ok(r.returncode == 2 and "Traceback" not in r.stderr, f"{' '.join(a)}: mensaje claro y salida 2")
r = corre("--cuenta", "ana@ejemplo.test", "--tope", "1")
ok("… y " in r.stdout and "--tema" in r.stdout, "con muchos, cada tema se acota y dice cuántos más")
G.rename(R / "guia (1).md")
r = corre("--cuenta", "ana@ejemplo.test")
ok(r.returncode == 1 and "falta guia.md" in r.stdout, "una raíz que perdió guia.md lo dice, no se calla")
(R / "guia (1).md").rename(G)

print("\nTodo bien." if not fallos else f"\n{fallos} fallos.")
sys.exit(1 if fallos else 0)
