#!/usr/bin/env python3
"""Prueba verificar.sh: el nombre del dueño de area.md, sin la frase que le sigue, y las copias en conflicto de Drive.

Uso: python3 pruebas/verificar/probar_verificar.py
"""
import pathlib, re, shutil, subprocess, sys, tempfile
import sys as _s, pathlib as _p; _s.path.insert(0, str(_p.Path(__file__).resolve().parents[1])); from comun import guia_122, raiz_migrada

AQUI = pathlib.Path(__file__).resolve().parent
VER = AQUI.parent.parent / "plugins" / "memoria" / "verificar.sh"
tmp = pathlib.Path(tempfile.mkdtemp())
R = tmp / "raiz"
shutil.copytree(AQUI.parent / "tablero" / "raiz", R)
fallos = 0


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t)
    fallos += 0 if c else 1


def dueno_distinto():
    out = subprocess.run(["bash", str(VER), str(R)], capture_output=True, text=True).stdout
    return [l for l in out.split("\n") if "responsable distinto" in l and "ventas" in l]


print("verificar.sh: el dueño de area.md")
a = R / "ventas" / "area.md"
t = a.read_text(encoding="utf-8")
m = re.search(r"^Dueñ[oa]: *(.+?)\s*$", t, re.M)
nombre = re.split(r"\.(?:\s|$)", m.group(1))[0]
ok(not dueno_distinto(), "la raíz de prueba no da el hallazgo")
a.write_text(t.replace(m.group(0), f"Dueño: {nombre}. Consume esta área cualquier conversación comercial."), encoding="utf-8")
ok(not dueno_distinto(), "una frase después del nombre no cuenta como otro dueño")
a.write_text(t.replace(m.group(0), "Dueño: Otra Persona. Consume esta área cualquier conversación comercial."), encoding="utf-8")
ok(len(dueno_distinto()) == 1, "otro nombre sí da el hallazgo")
a.write_text(t, encoding="utf-8")
print("verificar.sh: copias en conflicto de Drive")
import shutil as _sh
_sh.copy(R / "ventas" / "cuentas" / "decisiones.md", R / "ventas" / "cuentas" / "decisiones [Conflict].md")
(R / "ventas" / "cuentas" / "fuentes").mkdir(exist_ok=True)
(R / "ventas" / "cuentas" / "fuentes" / "contrato (1).md").write_text("x", encoding="utf-8")
out = subprocess.run(["bash", str(VER), str(R)], capture_output=True, text=True).stdout
cf = [l for l in out.split("\n") if "copia en conflicto" in l]
ok(len(cf) == 1 and "decisiones [Conflict].md" in cf[0], f"marca la copia con su original al lado, y solo esa ({len(cf)})")
print("verificar.sh: la clave aportacion (afirma hasta la 1.21) se cuenta y no bloquea")
def sin_afirma():
    r = subprocess.run(["bash", str(VER), str(R)], capture_output=True, text=True)
    m = re.search(r"Nota: (\d+) archivos? de entregables/ y taller/ sin `aportacion:`", r.stdout)
    return (int(m.group(1)) if m else 0), r.returncode, r.stdout
ant = lambda t: int((re.search(r"Nota: (\d+) archivos? con la estructura de la 1\.21", t) or [0, 0])[1])
n0, rc0, o0 = sin_afirma()
ant0 = ant(o0)
ok(n0 > 0, f"la raíz de prueba, sin afirma en sus entregables y taller, lo dice ({n0})")
ent = next(p for p in R.rglob("*.md") if "/entregables/" in str(p).replace("\\", "/") and p.read_text(encoding="utf-8").startswith("---") and "estado: reemplazado" not in p.read_text(encoding="utf-8"))
tx = ent.read_text(encoding="utf-8")
ent.write_text(tx.replace("\nactualizado:", '\naportacion: "Una cosa que el documento aporta."\nactualizado:', 1), encoding="utf-8")
n1, rc1, _ = sin_afirma()
ok(n1 == n0 - 1, f"un entregable con afirma deja de contarse ({n0} → {n1})")
ok(rc1 == rc0, "no cambia el código de salida: no bloquea")
ent.write_text(tx.replace("\nactualizado:", '\naportacion: ""\nactualizado:', 1), encoding="utf-8")
n2, _, _ = sin_afirma()
ok(n2 == n0, "una afirma vacía cuenta como sin afirma")
ent.write_text(tx.replace("\nactualizado:", '\nafirma: "La clave vieja también vale."\nactualizado:', 1), encoding="utf-8")
n3, rc3, o3 = sin_afirma()
ok(n3 == n0 - 1 and rc3 == rc0 and ant(o3) == ant0 + 1, f"la clave vieja afirma vale, y se cuenta como estructura anterior sin bloquear ({ant0} → {ant(o3)})")
ent.write_text(tx, encoding="utf-8")
print("verificar.sh: la estructura de la 1.21 se cuenta y no bloquea; la de la 1.22 se lee")
r = subprocess.run(["bash", str(VER), str(R)], capture_output=True, text=True)
ok(re.search(r"Nota: \d+ archivos con la estructura de la 1\.21", r.stdout) and "guia.md (columnas" in r.stdout, "la raíz de prueba, sin migrar, lo dice en una nota")
g = R / "guia.md"; gt = g.read_text(encoding="utf-8")
g.write_text(gt.replace("| Área | Qué es | Dueño | Cuenta | Quién la lee |\n|---|---|---|---|---|", "| Área | Qué es | Responsable | Cuenta | Quién la lee | Acceso |\n|---|---|---|---|---|---|"), encoding="utf-8")
r2 = subprocess.run(["bash", str(VER), str(R)], capture_output=True, text=True)
ok("columnas de menos" in r2.stdout and "hacen falta 6" in r2.stdout, "con «Acceso» en el encabezado, una fila de cinco columnas se marca")
g.write_text(guia_122(gt, legal="Ana y Beto").replace("| Todo el equipo | Abierta |\n", "| Todo el equipo | Quizá |\n", 1), encoding="utf-8")
r3 = subprocess.run(["bash", str(VER), str(R)], capture_output=True, text=True)
ok("columna Acceso sin «Abierta» ni «Restringida»" in r3.stdout and "guia.md (columnas" not in r3.stdout and "columnas de menos" not in r3.stdout, "un valor que no es Abierta ni Restringida se marca; guia.md ya no cuenta como anterior")
g.write_text(gt, encoding="utf-8")
print("verificar.sh: un .html sin charset se avisa y no bloquea")
h1, h2 = ent.parent / "con-charset.html", ent.parent / "sin-charset.html"
h1.write_text('<!doctype html><html><head><META CHARSET="UTF-8"><title>x</title></head><body>á</body></html>', encoding="utf-8")
h2.write_text('<!doctype html><html><head><title>x</title></head><body>á</body></html>', encoding="utf-8")
r0 = subprocess.run(["bash", str(VER), str(R)], capture_output=True, text=True)
h1.unlink()
r = subprocess.run(["bash", str(VER), str(R)], capture_output=True, text=True)
cuenta = lambda t: int((re.search(r"Nota: (\d+) archivos? \.html sin `<meta charset", t) or [0, 0])[1])
ok(cuenta(r0.stdout) == cuenta(r.stdout) and "sin-charset.html" in r.stdout and "con-charset.html" not in r0.stdout, "cuenta solo el .html sin la etiqueta, sin distinguir mayúsculas")
ok(r.returncode == rc0, "no cambia el código de salida")
h2.unlink()
shutil.rmtree(tmp, ignore_errors=True)
print("\nTodo bien." if not fallos else f"\n{fallos} fallos.")
sys.exit(1 if fallos else 0)
