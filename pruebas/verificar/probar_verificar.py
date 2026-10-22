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
shutil.rmtree(tmp, ignore_errors=True)
print("\nTodo bien." if not fallos else f"\n{fallos} fallos.")
sys.exit(1 if fallos else 0)
