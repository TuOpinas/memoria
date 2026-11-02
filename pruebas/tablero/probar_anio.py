#!/usr/bin/env python3
"""El cambio de año en el tablero (1.24.8): un proyecto cuyo sesiones.md y decisiones.md se archivaron con el año anterior
(`sesiones-<año-1>.md`, `decisiones-<año-1>.md`) y se abrieron de nuevo, solo con la línea «Archivado:». El tablero sigue
contando lo del año anterior como si no se hubiera archivado, los identificadores salen iguales (`#<año-1>-12-31-2`) y un
proyecto reutilizado de la base (sin cambios) no pierde las decisiones que quedan fuera de las últimas cuatro semanas.

Uso: python3 pruebas/tablero/probar_anio.py
"""
import datetime, json, pathlib, shutil, subprocess, sys, tempfile
from zoneinfo import ZoneInfo

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1])); from comun import dos_corridas
AQUI = pathlib.Path(__file__).resolve().parent
GV = AQUI.parents[1] / "plugins" / "memoria" / "skills" / "tablero" / "generar_vista.py"
PID, CARPETA = "ventas--cuentas", "ventas/cuentas"
fallos = 0


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1


# el año del generador: la raíz de prueba no dice zona, así que es la de Ciudad de México
A = int(datetime.datetime.now(ZoneInfo("America/Mexico_City")).year) - 1
CAB = "---\nestado: vigente\nactualizado: {f}\n---\n\n# {t}\n"
DEC = f"""## {A}-12-31 · El piloto arranca en enero
Decidió: Ana Prueba
Por qué: el cliente cierra el año fiscal.
Afecta a: operacion/soporte

## {A}-12-31 · El piloto se cobra por mes
Decidió: Ana Prueba
Por qué: es lo que pidió compras.

## {A}-10-15 · Cliente Uno se atiende desde ventas
Decidió: Ana Prueba
Por qué: es la cuenta más grande.
"""
SES = f"""## {A}-12-31 (cierre del año)
Tema: el piloto.
Avances: dos decisiones.
Sesión de: Ana Prueba · plugin 1.24.7

## {A}-10-15
Tema: arranque.
Avances: plan.
Sesión de: Ana Prueba · plugin 1.24.7
"""


def raiz(archivada):
    tmp = pathlib.Path(tempfile.mkdtemp())
    r = tmp / "raiz"; shutil.copytree(AQUI / "raiz", r)
    pc = r / CARPETA
    if archivada:
        (pc / f"decisiones-{A}.md").write_text(CAB.format(f=f"{A}-12-31", t="Decisiones") + "\n" + DEC, encoding="utf-8")
        (pc / f"sesiones-{A}.md").write_text(CAB.format(f=f"{A}-12-31", t="Sesiones") + "\n" + SES, encoding="utf-8")
        (pc / "decisiones.md").write_text(CAB.format(f=f"{A + 1}-01-02", t="Decisiones") + f"\nArchivado: decisiones-{A}.md\n", encoding="utf-8")
        (pc / "sesiones.md").write_text(CAB.format(f=f"{A + 1}-01-02", t="Sesiones") + f"\nArchivado: sesiones-{A}.md\n", encoding="utf-8")
    else:
        (pc / "decisiones.md").write_text(CAB.format(f=f"{A}-12-31", t="Decisiones") + "\n" + DEC, encoding="utf-8")
        (pc / "sesiones.md").write_text(CAB.format(f=f"{A}-12-31", t="Sesiones") + "\n" + SES, encoding="utf-8")
    return tmp, r


def proyecto(sal):
    return json.loads((sal / "proyectos" / f"{PID}.json").read_text(encoding="utf-8"))


def generar(r, sal):
    subprocess.run([sys.executable, str(GV), str(r), str(sal), "--version", "prueba"], check=True, stdout=subprocess.DEVNULL)
    return proyecto(sal)


ids = lambda p: sorted(d.get("id") for d in p.get("decisiones") or [])
print("El cambio de año: registros archivados del año anterior")
t0, r0 = raiz(False)
t1, r1 = raiz(True)
try:
    p0, p1 = generar(r0, t0 / "sal"), generar(r1, t1 / "sal")
    ok(p1.get("sesiones_total") == p0.get("sesiones_total") == 2, f"las sesiones del año anterior se siguen contando ({p1.get('sesiones_total')})")
    ok(p1.get("decisiones_total") == p0.get("decisiones_total") == 3, f"las decisiones del año anterior se siguen contando ({p1.get('decisiones_total')})")
    ok(ids(p1) == ids(p0) == sorted([f"{A}-12-31", f"{A}-12-31-2", f"{A}-10-15"]), f"los identificadores salen iguales, también #{A}-12-31-2 ({ids(p1)})")
    d2 = next((d for d in p1.get("decisiones") or [] if d.get("id") == f"{A}-12-31-2"), {})
    ok(d2.get("titulo") == "El piloto arranca en enero" and d2.get("archivada") is True and "operacion/soporte" in (d2.get("afecta") or ""),
       "la de más arriba del día es la -2, marcada como archivada y con su «Afecta a»")
    ok(p1.get("ultima_sesion") == p0.get("ultima_sesion") == f"{A}-12-31", f"la última sesión es la del año anterior ({p1.get('ultima_sesion')})")
    # la puesta al día siguiente, sin cambios en el proyecto: se reutiliza de la base y no pierde nada
    o1, o2, reuso = dos_corridas(r1, t1)
    q1, q2 = proyecto(o1), proyecto(o2)
    est = json.loads((o1 / "meta" / "estado.json").read_text(encoding="utf-8"))
    inv = json.loads(subprocess.run([sys.executable, str(GV), str(r1), "--inventario", "--sin-cambios", ",".join(est.get("huellas") or [])],
                                    capture_output=True, text=True, check=True).stdout)
    ok(reuso and PID in (inv["inventario"].get("reusar") or []), "la segunda puesta al día reutiliza el proyecto, con sus archivados")
    ok(ids(q2) == ids(q1) == ids(p0) and q2.get("decisiones_total") == 3 and q2.get("sesiones_total") == 2,
       f"un proyecto reutilizado conserva las decisiones de fuera de las últimas cuatro semanas ({ids(q2)})")
finally:
    shutil.rmtree(t0, ignore_errors=True); shutil.rmtree(t1, ignore_errors=True)
print("\n" + ("Todo bien." if not fallos else f"{fallos} fallo(s)."))
sys.exit(1 if fallos else 0)
