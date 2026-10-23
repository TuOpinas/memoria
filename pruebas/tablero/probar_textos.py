#!/usr/bin/env python3
"""El porqué de las decisiones viejas va aparte (1.19): de cada proyecto, las cinco decisiones más recientes y los
cuestionamientos se quedan enteros, y el «porque» y el «descartamos» de las demás van a detalle/<proyecto>.

Uso: python3 pruebas/tablero/probar_textos.py
"""
import json, pathlib, shutil, subprocess, sys, tempfile
AQUI = pathlib.Path(__file__).resolve().parent
T = AQUI.parent.parent / "plugins" / "memoria" / "skills" / "tablero"
tmp = pathlib.Path(tempfile.mkdtemp()); R = tmp / "raiz"
shutil.copytree(AQUI / "raiz", R)
dec = R / "archivo" / "historia" / "decisiones.md"
entradas = "".join(f"## 2026-08-{d:02d} · Decisión de prueba {d}\nDecidió: Ana Prueba\nPor qué: PORQUE-{d} explica la decisión.\nDescartamos: DESCARTE-{d}.\nAfecta a: entregables/x.md\n\n" for d in range(20, 12, -1))
dec.write_text(dec.read_text(encoding="utf-8") + "\n" + entradas, encoding="utf-8")
fallos = 0
def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1
print("El porqué de las decisiones viejas, aparte")
subprocess.run([sys.executable, str(T / "generar_vista.py"), str(R), str(tmp / "s"), "--version", "prueba"], check=True, capture_output=True)
p = json.loads((tmp / "s/proyectos/archivo--historia.json").read_text())
ds = [d for d in p["decisiones"] if d.get("tipo") != "cuestionamiento"]
ok(len(ds) == 8 and all(d.get("porque") for d in ds[:5]) and not any(d.get("porque") or d.get("descartamos") for d in ds[5:]), "las cinco más recientes se quedan enteras; las demás, sin porqué ni descartes")
ok(all(d.get("texto_aparte") for d in ds[5:]) and all(d.get("titulo") and d.get("fecha") for d in ds), "las demás conservan título y fecha y dicen dónde está su texto")
tx = json.loads((tmp / "s/detalle/archivo--historia.json").read_text())
ok(sorted(v["porque"] for v in tx["decisiones"].values()) == ["PORQUE-13 explica la decisión.", "PORQUE-14 explica la decisión.", "PORQUE-15 explica la decisión."], "su texto va a detalle/<proyecto>")
vc = tmp / "s/detalle/ventas--cuentas.json"
ok(not vc.exists() or "decisiones" not in json.loads(vc.read_text()), "un proyecto con cinco decisiones o menos no las parte")
pc = json.loads((tmp / "s/proyectos/ventas--cuentas.json").read_text())
dc = json.loads(vc.read_text()) if vc.exists() else {}
ok(len(pc.get("sesiones") or []) <= 1 and (not pc.get("sesiones_aparte") or len(dc.get("sesiones") or []) == pc["sesiones_aparte"]), "de la bitácora se queda la última sesión y las demás van al detalle")
ok(("estado_actual" in pc) != bool(pc.get("estado_aparte")) and (not pc.get("estado_aparte") or dc.get("estado_actual")), "el estado completo, o se queda o va al detalle, nunca se pierde")
idx = json.loads((tmp / "s/indice.json").read_text())
ok(any(i["coleccion"] == "detalle" for i in idx), "el índice lo lista para subirlo")
print("\n" + ("Todo bien." if not fallos else f"{fallos} fallo(s)."))
sys.exit(1 if fallos else 0)
