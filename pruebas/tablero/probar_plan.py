#!/usr/bin/env python3
"""plan_subida.py: lo que cierra la corrida va en el último lote con meta/estado, sin que nadie escriba una hora (1.21)."""
import json, pathlib, subprocess, sys, tempfile, shutil, datetime
AQUI = pathlib.Path(__file__).resolve().parent
TABLERO = AQUI.parent.parent / "plugins" / "memoria" / "skills" / "tablero"
PLAN, PREPARAR = TABLERO / "plan_subida.py", TABLERO.parent.parent / "preparar.py"
fallos = []
def ok(c, m):
    print(("  bien  " if c else "  FALLA ") + m)
    if not c: fallos.append(m)
def escribir(p, t):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(t, encoding="utf-8")
def corre(*a):
    r = subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr

tmp = pathlib.Path(tempfile.mkdtemp())
try:
    print("preparar.py --trabajo deja la carpeta de trabajo lista")
    trab = tmp / "trabajo"; escribir(trab / "base" / "viejo.json", "{}")
    rc, out, err = corre(PREPARAR, "$HOME/tablero", "skills/tablero/generar_vista.py", "--trabajo", trab)
    ini = json.loads((trab / "inicio.json").read_text(encoding="utf-8")) if (trab / "inicio.json").exists() else {}
    ok(rc == 0 and out.startswith("VERSION ") and not (trab / "base").exists() and ini.get("inicio"), f"vacía la base, escribe inicio.json y sigue imprimiendo VERSION ({err[-120:]})")
    # un inicio hace 7 minutos, para que la duración se vea
    escribir(trab / "inicio.json", json.dumps({"inicio": (datetime.datetime.now().astimezone() - datetime.timedelta(minutes=7)).isoformat(timespec="seconds")}))

    print("plan_subida.py --cierre: la corrida al día")
    base = tmp / "base"; escribir(base / "meta" / "estado.json", json.dumps({"data": {"huella_raiz": "h1", "zona": "America/Mexico_City", "huellas": ["a"]}, "version": 4}))
    cierres = tmp / "cierres" / "cierres"      # como lo deja ArtifactData con out_dir: <out_dir>/<colección>/<id>.json
    sinc = "2026-09-01T18:30-06:00"
    escribir(cierres / "c-vieja.json", json.dumps({"data": {"hora": "2026-09-01T18:00-06:00"}, "version": 1}))
    escribir(cierres / "c-igual.json", json.dumps({"data": {"hora": "2026-09-02T00:30:00Z"}, "version": 2}))     # el mismo instante, en otra zona
    escribir(cierres / "c-nueva.json", json.dumps({"data": {"hora": "2026-09-01T18:45-06:00"}, "version": 3}))   # posterior: se queda
    escribir(cierres / "c-futura.json", json.dumps({"data": {"hora": "2099-01-01T00:00-06:00"}, "version": 5}))  # mal puesta
    escribir(tmp / "ret.json", '["c9"]'); escribir(tmp / "aj.json", "[]")
    rc, out, err = corre(PLAN, "--cierre", base, tmp / "salida", "--sincronizado", sinc, "--cierres", cierres.parent, "--inicio", trab / "inicio.json",
                         "--llamadas", "9", "--retenidos", tmp / "ret.json", "--ajenos", tmp / "aj.json", "--pagina", '{"version": "1.21.0", "fecha": "2026-10-23", "desde": "1.20.1"}', "--tarea-desfasada", "false")
    res = json.loads(out) if rc == 0 else {}
    lote = (res.get("lotes") or [[]])[0]
    meta = json.loads((tmp / "salida" / "meta" / "estado.json").read_text(encoding="utf-8")) if rc == 0 else {}
    ok(rc == 0 and len(res["lotes"]) == 1 and lote[-1] == {"op": "update", "collection": "meta", "doc_id": "estado", "file_path": str((tmp / "salida" / "meta" / "estado.json").resolve())}, f"un solo lote que termina en meta/estado como update sin if_version ({err[-200:]})")
    ok(sorted((e["doc_id"], e["if_version"]) for e in lote[:-1] if e["op"] == "delete" and e["collection"] == "cierres") == [("c-futura", 5), ("c-igual", 2), ("c-vieja", 1)], "borra las marcas anteriores o iguales al sincronizado (comparadas como instantes) y las del futuro, con su if_version; la posterior se queda")
    ok(meta.get("sincronizado") == sinc and meta.get("cola_retenida") == ["c9"] and meta.get("cola_ajena") == [] and meta.get("llamadas") == 9 and meta.get("pagina_actualizada", {}).get("desde") == "1.20.1" and meta.get("tarea_desfasada") is False, "meta/estado lleva el sincronizado que imprimió el inventario, la cola, las llamadas y la página")
    ok(6.5 <= (meta.get("duracion_min") or 0) <= 8, f"la duración sale de inicio.json ({meta.get('duracion_min')} min)")
    ok("huella_raiz" not in meta and "huellas" not in meta, "no toca las huellas: es un update parcial")
    rc2, out2, _ = corre(PLAN, "--cierre", tmp / "base-vacia", tmp / "salida2", "--sincronizado", sinc)
    ok(rc2 == 0 and json.loads(out2)["lotes"][0][-1]["op"] == "set" and json.loads((tmp / "salida2/meta/estado.json").read_text())["cola_retenida"] == [], "sin base ni archivos de cola, meta/estado va como set con la cola vacía")

    print("plan_subida.py al regenerar: los cierres y lo que cierra van en el último lote, y dice si el enfoque cambió")
    sal = tmp / "sal"
    escribir(sal / "meta" / "estado.json", json.dumps({"organizacion": "x", "sincronizado": sinc, "zona": "America/Mexico_City", "huella_candidatos": "cand-nueva"}))
    escribir(sal / "meta" / "enfoque-candidatos.json", json.dumps({"huella": "cand-nueva", "grupos": []}))
    escribir(sal / "indice.json", json.dumps([{"coleccion": "meta", "doc_id": "estado", "archivo": "meta/estado.json", "bytes": 10, "huella": "h"}]))
    escribir(base / "meta" / "estado.json", json.dumps({"data": {"huella_raiz": "h1", "zona": "America/Mexico_City", "huella_candidatos": "cand-vieja"}, "version": 4}))
    rc, out, err = corre(PLAN, sal, base, "--cierres", cierres.parent, "--inicio", trab / "inicio.json", "--llamadas", "14", "--pagina", '{"version": "1.21.0"}')
    res = json.loads(out) if rc == 0 else {}
    ult = (res.get("lotes") or [[]])[-1]
    meta = json.loads((sal / "meta" / "estado.json").read_text(encoding="utf-8"))
    ok(rc == 0 and ult[-1]["collection"] == "meta" and [e["doc_id"] for e in ult if e["collection"] == "cierres"] == ["c-futura", "c-igual", "c-vieja"], f"los delete de cierres van justo antes de meta/estado, en el último lote ({err[-200:]})")
    ok(meta.get("llamadas") == 14 and meta.get("pagina_actualizada") == {"version": "1.21.0"} and 6.5 <= (meta.get("duracion_min") or 0) <= 8 and meta.get("sincronizado") == sinc, "meta/estado del generador gana las llamadas, la duración y la página, y conserva el sincronizado que estampó")
    ok(res.get("enfoque_cambio") is True and res.get("cierres_borrados") == 3, "dice que el enfoque cambió cuando la huella de los candidatos no es la de la base")
    ok(meta.get("huella_candidatos") == "cand-vieja" and json.loads(pathlib.Path(res["enfoque_meta"]).read_text())["huella_candidatos"] == "cand-nueva", "la huella nueva no sube con meta/estado: la deja aparte para que el paso 6 la escriba junto al enfoque")
    escribir(base / "meta" / "estado.json", json.dumps({"data": {"huella_raiz": "h1", "zona": "America/Mexico_City", "huella_candidatos": "cand-nueva"}, "version": 4}))
    rc, out, _ = corre(PLAN, sal, base)
    ok(json.loads(out).get("enfoque_cambio") is False and json.loads(out).get("cierres_borrados") == 0, "con la misma huella no hay que renovar el enfoque; sin --cierres no borra nada")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print("\n" + ("Todo bien." if not fallos else f"{len(fallos)} fallo(s)."))
sys.exit(1 if fallos else 0)
