#!/usr/bin/env python3
"""Los scripts del plugin compilan con el Python más viejo que haya a mano (1.23.1).

En la computadora de cada persona corre el Python que tenga: 3.10 en la consola de la app, el de serie en un Mac puede ser
3.9. Un script que solo compila con 3.12 o más (por ejemplo, una barra dentro de las llaves de un f-string) deja a esa
organización sin cerrar sesión, y las pruebas, que corren con el Python nuevo del contenedor, no lo ven. Este script compila
cada .py del plugin con cada python3.9, 3.10 y 3.11 que encuentre; si no hay ninguno, lo dice y no falla.

Uso: python3 pruebas/probar_compila.py
"""
import pathlib, shutil, subprocess, sys

PLUGIN = pathlib.Path(__file__).resolve().parents[1] / "plugins" / "memoria"
COMPILA = """import sys, re
f = sys.argv[1]
src = open(f, encoding="utf-8").read()
if f.endswith(".sh"):   # el Python que verificar.sh lleva dentro, entre «<<'PY'» y «PY»
    m = re.search(r"<<'PY'\\n(.*?)\\nPY\\n", src, re.S)
    src = m.group(1) if m else ""
compile(src, f, "exec")
"""
archivos = sorted(PLUGIN.rglob("*.py")) + [PLUGIN / "verificar.sh"]
viejos = [v for v in ("python3.9", "python3.10", "python3.11") if shutil.which(v)]
if not viejos:
    print("  aviso  no hay python3.9, 3.10 ni 3.11 en esta máquina: no se comprobó que los scripts compilen con un Python viejo"
          " (se instalan con «uv python install 3.9 3.10»)")
    sys.exit(0)
fallos = 0
for py in viejos:
    malos = 0
    for f in archivos:
        r = subprocess.run([py, "-c", COMPILA, str(f)], capture_output=True, text=True)
        if r.returncode:
            malos += 1
            print(f"  FALLA {f.relative_to(PLUGIN)} no compila con {py}: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ''}")
    print(f"  bien  {len(archivos)} scripts compilan con {py}" if not malos else f"  ({py}: {malos} no compilan)")
    fallos += malos
print("\nTodo bien." if not fallos else f"\n{fallos} fallo(s).")
sys.exit(1 if fallos else 0)
