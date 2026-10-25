#!/usr/bin/env python3
"""Los resúmenes de «Qué hay» que escribe la puesta al día (1.22.4): qué proyectos se piden al modelo, qué se guarda de lo
que contesta y que la subida lo lleva en el índice.

Uso: python3 pruebas/tablero/probar_resumenes.py
"""
import importlib.util, json, pathlib, shutil, subprocess, sys, tempfile

AQUI = pathlib.Path(__file__).resolve().parent
BARRIDO = AQUI.parents[1] / "plugins" / "memoria" / "skills" / "tablero" / "barrido.py"
spec = importlib.util.spec_from_file_location("barrido", BARRIDO); B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
fallos = 0


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1


def doc(p, d):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")


tmp = pathlib.Path(tempfile.mkdtemp())
try:
    sal, base = tmp / "salida", tmp / "base"
    piezas = [{"tipo": "entregable", "titulo": "Kit de cuentas", "estado": "vigente", "afirma": "Cómo preparar una cuenta en una tarde"},
              {"tipo": "taller", "titulo": "Notas de precios", "estado": "borrador"}]
    for pid, extra in (("ventas--nuevo", {}), ("ventas--igual", {}), ("ventas--viejo", {}), ("ventas--ajeno", {"escribe": False}),
                       ("ventas--cerrado", {"cerrado": True}), ("ventas--sin", {"que_hay_huella": None})):
        d = {"nombre": pid.split("--")[1], "escribe": True, "que_hay_huella": "h-" + pid, "que_hay_aparte": True}
        d.update(extra)
        if d["que_hay_huella"] is None: d.pop("que_hay_huella")
        doc(sal / "proyectos" / f"{pid}.json", d)
        doc(sal / "detalle" / f"{pid}.json", {"que_hay": {"piezas": piezas, "trayectoria": []}})
    doc(base / "resumenes" / "ventas--igual.json", {"data": {"huella_qh": "h-ventas--igual", "ent": "x", "tal": "y"}, "version": 2})
    doc(base / "resumenes" / "ventas--viejo.json", {"data": {"huella_qh": "otra", "ent": "x", "tal": "y"}, "version": 2})
    pr = B.para_resumen(sal, str(base), {"ventas--viejo"})
    ids = [x["proyecto"] for x in pr]
    print("Qué proyectos se piden")
    ok(ids[0] == "ventas--viejo", "primero los que cambiaron en esta corrida")
    ok(set(ids) == {"ventas--viejo", "ventas--nuevo", "ventas--ajeno"}, f"los que no tienen resumen o lo tienen viejo, también donde no se escribe; no el que sigue valiendo, ni uno cerrado, ni sin piezas ({ids})")
    ok(all(set(z) <= {"tipo", "titulo", "estado", "aportacion"} for x in pr for z in x["piezas"]), "de cada pieza, solo tipo, título, estado y aportación")

    print("Lo que contesta el modelo")
    doc(sal / "barrido.json", {"anadir": [], "borrar": [], "para_resumen": pr, "juzgado": {"ids": [], "contraste": []}})
    doc(sal / "indice.json", [])
    doc(sal / "meta" / "estado.json", {"snapshot": "2026-10-25", "sincronizado": "2026-10-25T10:00-06:00"})
    juicio = {"resumenes": [{"proyecto": "ventas--nuevo", "publicado": "Un kit para preparar una cuenta en una tarde.", "taller": "Se afinan los precios."},
                            {"proyecto": "ventas--igual", "publicado": "No se pidió", "taller": "x"},
                            {"proyecto": "ventas--viejo", "publicado": "Escribe a ana@acme.test", "taller": "x"}]}
    j = tmp / "juicio.json"; j.write_text(json.dumps(juicio, ensure_ascii=False), encoding="utf-8")
    r = subprocess.run([sys.executable, str(BARRIDO), "--sumar-juicio", str(sal), str(j)], capture_output=True, text=True)
    ok(r.returncode == 0, "--sumar-juicio corre" + (f": {r.stderr[-300:]}" if r.returncode else ""))
    hechos = sorted(p.stem for p in (sal / "resumenes").glob("*.json")) if (sal / "resumenes").exists() else []
    ok(hechos == ["ventas--nuevo"], f"solo se guarda lo pedido y sin datos personales ({hechos})")
    d = json.loads((sal / "resumenes" / "ventas--nuevo.json").read_text(encoding="utf-8")) if hechos else {}
    ok(d.get("huella_qh") == "h-ventas--nuevo" and d.get("ent") and d.get("tal") and d.get("huella"), "con la huella de lo que hay, para saber cuándo queda viejo")
    ind = json.loads((sal / "indice.json").read_text(encoding="utf-8"))
    ok([x["doc_id"] for x in ind if x["coleccion"] == "resumenes"] == ["ventas--nuevo"], "y entra en el índice, para que la subida lo lleve")
    ok(not (sal / "cambios").exists() or not any((sal / "cambios").iterdir()), "un resumen no es una propuesta: no va a la cola")
    bar = json.loads((sal / "barrido.json").read_text(encoding="utf-8"))
    juz = set(bar["juzgado"].get("resumenes") or [])
    ok({"ventas--viejo|h-ventas--viejo", "ventas--ajeno|h-ventas--ajeno"} <= juz, "lo pedido queda juzgado con su huella, haya salido o no")
    pr2 = B.para_resumen(sal, str(base), set(), {"resumenes": juz})
    ok(not ({x["proyecto"] for x in pr2} & {"ventas--viejo", "ventas--ajeno"}), "y no se vuelve a pedir mientras la huella no cambie")
    ok("parece llevar un dato personal" in r.stdout, "--sumar-juicio dice qué rechazó y por qué")

    print("La subida")
    PLAN = BARRIDO.parent / "plan_subida.py"
    vol = tmp / "vol"
    doc(vol / "resumenes" / "ventas--borrado.json", {"data": {"huella_qh": "x"}, "version": 3})
    doc(vol / "resumenes" / "ventas--igual.json", {"data": {"huella_qh": "h-ventas--igual"}, "version": 2})
    ind = json.loads((sal / "indice.json").read_text(encoding="utf-8"))
    ind += [{"coleccion": "proyectos", "doc_id": p_.stem, "archivo": f"proyectos/{p_.stem}.json", "huella": "z", "bytes": p_.stat().st_size} for p_ in (sal / "proyectos").glob("*.json")]
    (sal / "indice.json").write_text(json.dumps(ind), encoding="utf-8")
    r2 = subprocess.run([sys.executable, str(PLAN), str(sal), str(vol)], capture_output=True, text=True)
    txt = r2.stdout
    ok(r2.returncode == 0 and '"ventas--borrado"' in txt and '"ventas--igual"' not in txt.split('"delete"')[-1] if r2.returncode == 0 else False,
       "el resumen de un proyecto que ya no existe se borra; el de uno que sigue, no" + (f" ({r2.stderr[-200:]})" if r2.returncode else ""))
finally:
    shutil.rmtree(tmp)
print("\nTodo bien." if not fallos else f"\n{fallos} fallos.")
sys.exit(1 if fallos else 0)
