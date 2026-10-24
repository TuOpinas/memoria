#!/usr/bin/env python3
"""Prueba verificar.sh: el nombre del dueño de area.md, sin la frase que le sigue, y las copias en conflicto de Drive.

Uso: python3 pruebas/verificar/probar_verificar.py
"""
import pathlib, re, shutil, subprocess, sys, tempfile

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
    return [l for l in out.split("\n") if "dueño distinto" in l and "ventas" in l]


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
print("verificar.sh: la clave afirma se cuenta y no bloquea")
def sin_afirma():
    r = subprocess.run(["bash", str(VER), str(R)], capture_output=True, text=True)
    m = re.search(r"Nota: (\d+) archivos? de entregables/ y taller/ sin `afirma:`", r.stdout)
    return (int(m.group(1)) if m else 0), r.returncode, r.stdout
n0, rc0, _ = sin_afirma()
ok(n0 > 0, f"la raíz de prueba, sin afirma en sus entregables y taller, lo dice ({n0})")
ent = next(p for p in R.rglob("*.md") if "/entregables/" in str(p).replace("\\", "/") and p.read_text(encoding="utf-8").startswith("---") and "estado: reemplazado" not in p.read_text(encoding="utf-8"))
tx = ent.read_text(encoding="utf-8")
ent.write_text(tx.replace("\nactualizado:", '\nafirma: "Una cosa que el documento sostiene."\nactualizado:', 1), encoding="utf-8")
n1, rc1, _ = sin_afirma()
ok(n1 == n0 - 1, f"un entregable con afirma deja de contarse ({n0} → {n1})")
ok(rc1 == rc0, "no cambia el código de salida: no bloquea")
ent.write_text(tx.replace("\nactualizado:", '\nafirma: ""\nactualizado:', 1), encoding="utf-8")
n2, _, _ = sin_afirma()
ok(n2 == n0, "una afirma vacía cuenta como sin afirma")
ent.write_text(tx, encoding="utf-8")
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
