#!/usr/bin/env python3
"""datos.py (1.24.1): los datos del tablero van como archivos publicados y vuelven de ellos sin perder nada; la base guarda
solo lo pequeño (lo marcado, los cierres, la marca de la publicación)."""
import json, pathlib, subprocess, sys, tempfile, shutil

AQUI = pathlib.Path(__file__).resolve().parent
TABLERO = AQUI.parent.parent / "plugins" / "memoria" / "skills" / "tablero"
GEN, PLAN, DATOS, VISTA = (TABLERO / n for n in ("generar_vista.py", "plan_subida.py", "datos.py", "vista.html"))
fallos = []


def ok(c, q):
    print(("  bien  " if c else "  FALLA ") + q)
    if not c:
        fallos.append(q)


def corre(*a):
    r = subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def lee(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


tmp = pathlib.Path(tempfile.mkdtemp())
try:
    raiz = tmp / "raiz"; shutil.copytree(AQUI / "raiz", raiz)
    t1 = tmp / "t1"
    print("La primera publicación, sin archivos todavía")
    # en dos tiempos, como la puesta al día: el inventario da la huella de la raíz
    rc, out, err = corre(GEN, raiz, "--inventario")
    inv = json.loads(out)
    copia = tmp / "copia"
    for r in inv["leer"]:
        (copia / r).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(raiz / r, copia / r)
    (tmp / "inv.json").write_text(json.dumps(inv["inventario"], ensure_ascii=False), encoding="utf-8")
    rc, _, err = corre(GEN, copia, t1 / "salida", "--desde-inventario", tmp / "inv.json", "--version", "prueba")
    ok(rc == 0, f"se genera ({err[-200:]})")
    rc, out, err = corre(DATOS, "base", t1, "--cola", "/dev/null")
    ok(rc == 0, f"un tablero sin archivos arma una base vacía ({err[-200:]})")
    rc, out, err = corre(PLAN, t1 / "salida", t1 / "base")
    ok(rc == 0 and "lotes" not in json.loads(out) and (t1 / "salida" / "plan.json").exists(), "el plan va a plan.json y por la conversación solo pasa el resumen")
    rc, out, err = corre(DATOS, "publicar", t1, "--vista", VISTA, "--titulo", "Tablero Prueba & Co")
    ok(rc == 0, f"se publica ({err[-300:]})")
    res = json.loads(out) if rc == 0 else {"archivos": [], "base": []}
    nombres = [a["as"] for a in res["archivos"]]
    ok(nombres == ["index.html", "datos/estado.json", "datos/tablero.json", "datos/propuestas.json", "datos/detalle.json"], f"la primera vez salen la página y los cuatro archivos ({nombres})")
    pag = (t1 / "publicar" / "index.html").read_text(encoding="utf-8")
    ok("<title>Tablero Prueba &amp; Co</title>" in pag and "<title>Tablero</title>" not in pag, "la página lleva el título de su organización")
    tab = lee(t1 / "publicar" / "datos" / "tablero.json"); est = lee(t1 / "publicar" / "datos" / "estado.json")
    gen_proys = {p.stem for p in (t1 / "salida" / "proyectos").glob("*.json")}
    ok(set(tab["proyectos"]) == gen_proys and set(tab["areas"]) == {p.stem for p in (t1 / "salida" / "areas").glob("*.json")}, "tablero.json trae todas las áreas y todos los proyectos generados")
    ok(est.get("huella_raiz") and est.get("publicado_id"), "estado.json trae la huella de la raíz y la marca de esta publicación")
    ops = [o for l in res["base"] for o in l]
    ok(ops == [{"op": "set", "path": f"publicado/{est['publicado_id']}", "data": {"sincronizado": est["sincronizado"]}}], f"en la base solo va la marca de la publicación ({ops})")
    ok(all(len(l) <= 50 for l in res["base"]), "las escrituras de la base van en lotes de 50 como mucho")

    print("La siguiente puesta al día, desde los archivos publicados")
    pub = t1 / "publicar" / "datos"
    t2 = tmp / "t2"
    cola = t2 / "cola.jsonl"; cola.parent.mkdir(parents=True)
    # lo que devuelve la consulta de «cambios»: una nota marcada y la marca de una propuesta del archivo
    props = {"prop-paso-hecho-x1": {"tipo": "propuesta", "clase": "paso-hecho", "proyecto": "ventas--cuentas", "texto": "Quitar «X».", "estado": "pendiente", "creado": "2026-10-02T09:00-06:00", "origen": "barrido", "por_que": "p"},
             "prop-paso-hecho-x2": {"tipo": "propuesta", "clase": "paso-hecho", "proyecto": "ventas--cuentas", "texto": "Quitar «Y».", "estado": "pendiente", "creado": "2026-10-02T09:00-06:00", "origen": "barrido", "por_que": "p"}}
    (pub / "propuestas.json").write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")
    cola.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in [
        {"data": {"tipo": "nota", "proyecto": "ventas--cuentas", "nota": "n", "creado": "2026-10-03T10:00-06:00"}, "id": "c1", "updatedAt": "x", "version": 1},
        {"data": {"tipo": "propuesta", "estado": "aplicada", "proyecto": "ventas--cuentas"}, "id": "prop-paso-hecho-x1", "updatedAt": "x", "version": 3},
    ]) + "\n<untrusted-document-abc>\n", encoding="utf-8")
    cierres = t2 / "cierres.jsonl"
    cierres.write_text(json.dumps({"data": {"proyecto": "ventas--cuentas", "hora": "2000-01-01T09:00Z", "cuenta": "a@b.c"}, "id": "ventas--cuentas--200001010900", "version": 1}) + "\n", encoding="utf-8")
    rc, out, err = corre(DATOS, "base", t2, f"estado={pub / 'estado.json'}", f"tablero={pub / 'tablero.json'}", f"propuestas={pub / 'propuestas.json'}", f"detalle={pub / 'detalle.json'}", "--cola", cola, "--cierres", cierres)
    cuenta = json.loads(out) if rc == 0 else {}
    ok(rc == 0 and cuenta.get("cola_marcas") == 1 and cuenta.get("cierres") == 1 and cuenta.get("propuestas") == 2, f"la base y la cola se arman desde los archivos y la consulta ({cuenta} {err[-200:]})")
    c1 = lee(t2 / "cola" / "prop-paso-hecho-x1.json")
    ok(c1["version"] == 3 and c1["data"]["estado"] == "aplicada" and c1["data"]["texto"] == "Quitar «X».", "una propuesta del archivo lleva encima su marca de la base, con la versión de la marca")
    c2 = lee(t2 / "cola" / "prop-paso-hecho-x2.json")
    ok(c2["version"] is None and c2["data"]["estado"] == "pendiente", "una propuesta que nadie tocó no tiene versión en la base")
    ok(lee(t2 / "base" / "meta" / "estado.json")["data"]["huella_raiz"] == est["huella_raiz"], "meta/estado vuelve igual que se publicó")
    rc, out, err = corre(PLAN, "--guardada", t2 / "base", "--version", "prueba")
    ok(rc == 0 and out.splitlines()[0] == est["huella_raiz"], "con lo publicado, la huella guardada dice que el tablero sigue valiendo")
    # regenerar sin cambios en la raíz: los proyectos se reutilizan y tablero.json no cambia
    shutil.copytree(t1 / "salida", t2 / "salida")
    (t2 / "salida" / "plan.json").unlink()
    (t2 / "salida" / "barrido.json").write_text(json.dumps({"anadir": [], "borrar": [{"id": "prop-paso-hecho-x1", "if_version": 3}, {"id": "prop-paso-hecho-x2", "if_version": None}]}), encoding="utf-8")
    rc, out, err = corre(PLAN, t2 / "salida", t2 / "base", "--cierres", t2 / "cierres")
    ok(rc == 0, f"plan de la segunda ({err[-200:]})")
    # «Por dónde empezar» que escribió el modelo
    enf = t2 / "enfoque.json"; enf.write_text(json.dumps({"generado": "2026-10-02", "grupos": [{"titulo": "G"}]}), encoding="utf-8")
    (t2 / "salida" / "meta" / "estado-enfoque.json").write_text(json.dumps({"huella_candidatos": "hc-nueva"}), encoding="utf-8")
    rc, out, err = corre(DATOS, "publicar", t2, "--enfoque", enf)
    res = json.loads(out) if rc == 0 else {"archivos": [], "base": []}
    ok(rc == 0, f"se publica la segunda ({err[-300:]})")
    nombres = [a["as"] for a in res["archivos"]]
    ok("datos/detalle.json" not in nombres and "index.html" not in nombres, f"lo que no cambió no se vuelve a publicar ({nombres})")
    ok("datos/propuestas.json" in nombres and lee(t2 / "publicar" / "datos" / "propuestas.json") == {}, "las propuestas retiradas salen del archivo")
    ops = [o for l in res["base"] for o in l]
    ok({"op": "delete", "path": "cambios/prop-paso-hecho-x1", "ifVersion": 3} in ops and not any(o["path"] == "cambios/prop-paso-hecho-x2" for o in ops),
       "se borra de la base la marca de una propuesta retirada; una sin marca no pide nada a la base")
    ok({"op": "delete", "path": "cierres/ventas--cuentas--200001010900", "ifVersion": 1} in ops, "los cierres ya recogidos se borran con su versión")
    ok({"op": "delete", "path": f"publicado/{est['publicado_id']}", "ifVersion": 1} in ops or est["publicado_id"] == lee(t2 / "publicar" / "datos" / "estado.json").get("publicado_id"),
       "la marca de la publicación anterior se borra (o es la misma)")
    tab2 = lee(t2 / "publicar" / "datos" / "tablero.json")
    est2 = lee(t2 / "publicar" / "datos" / "estado.json")
    ok(tab2["enfoque"]["grupos"][0]["titulo"] == "G" and est2.get("huella_candidatos") == "hc-nueva", "«Por dónde empezar» entra en tablero.json y su huella en estado.json")
    ok(tab2["proyectos"] == tab["proyectos"], "los proyectos que no cambiaron salen idénticos")

    print("Lo que no se puede hacer")
    t3 = tmp / "t3"; shutil.copytree(t2, t3, ignore=shutil.ignore_patterns("publicar"))
    (t3 / "base" / ".con-detalle").unlink()
    pl = lee(t3 / "salida" / "plan.json"); pl["lotes"].append([{"op": "set", "collection": "detalle", "doc_id": "ventas--cuentas", "file_path": str(t3 / "salida" / "meta" / "estado.json")}])
    (t3 / "salida" / "plan.json").write_text(json.dumps(pl), encoding="utf-8")
    rc, out, err = corre(DATOS, "publicar", t3)
    ok(rc != 0 and "detalle.json" in err, "un plan que cambia el detalle sin haberlo traído se para, en vez de publicar un detalle vacío")
    rc, out, err = corre(DATOS, "base", t3, "estado=/no/existe.json")
    ok(rc != 0 and "No encuentro" in err, "un archivo descargado que no está se dice")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print("\nTodo bien." if not fallos else f"\n{len(fallos)} fallo(s).")
sys.exit(1 if fallos else 0)
