#!/usr/bin/env python3
"""Prueba que verificar.sh compara el nombre del dueño y no la frase que puede seguirle en area.md.

Uso: python3 pruebas/verificar/probar_dueno.py
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
shutil.rmtree(tmp, ignore_errors=True)
print("\nTodo bien." if not fallos else f"\n{fallos} fallos.")
sys.exit(1 if fallos else 0)
