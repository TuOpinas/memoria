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
    # un tablero de la 1.24.0: lo marcado, las sugerencias enteras en la base (una aceptada, una pendiente), un cierre
    jl = lambda f, docs: (f.parent.mkdir(parents=True, exist_ok=True), f.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in docs) + "\n", encoding="utf-8"))
    vieja = lambda id_, estado, v: {"data": {"tipo": "propuesta", "clase": "decision-sin-registrar", "proyecto": "ventas--cuentas", "texto": f"T {id_}", "por_que": "p", "origen": "barrido", "creado": "2026-10-02T09:00-06:00", "estado": estado}, "id": id_, "updatedAt": "x", "version": v}
    jl(t1 / "cola.jsonl", [{"count": 3, "nextCursor": ""},
                           {"data": {"tipo": "nota", "proyecto": "ventas--cuentas", "nota": "n", "creado": "2026-10-03T10:00-06:00"}, "id": "c1", "updatedAt": "x", "version": 1},
                           vieja("prop-decision-sin-registrar-acep", "aceptada", 2), vieja("prop-decision-sin-registrar-pend", "pendiente", 1)])
    jl(t1 / "cierres.jsonl", [{"data": {"proyecto": "ventas--cuentas", "hora": "2000-01-01T09:00Z", "cuenta": "a@b.c"}, "id": "ventas--cuentas--200001010900", "version": 1}])
    rc, out, err = corre(DATOS, "base", t1, "--primera-vez", "--cola", t1 / "cola.jsonl", "--cierres", t1 / "cierres.jsonl", "--publicado", t1 / "no-hay.jsonl")
    ok(rc == 0 and out == "", f"el paso 1a no imprime nada: la tarea lee cinco líneas de los scripts que siguen ({out!r} {err[-200:]})")
    ok((t1 / "cola" / "c1.json").exists() and not (t1 / "cola" / "prop-decision-sin-registrar-acep.json").exists(), "en 1a la cola lleva lo marcado; las marcas de sugerencias se guardan aparte")
    rc, out, err = corre(PLAN, "--guardada", t1 / "base", "--version", "prueba")
    ok(rc == 0 and out.splitlines()[0] == "-", "sin archivos hay que regenerar")
    rc, out, err = corre(DATOS, "base", t1, "--sin-archivos")
    ok(rc == 0 and out == "", f"el paso e sin archivos ({err[-200:]})")
    acep = lee(t1 / "cola" / "prop-decision-sin-registrar-acep.json")
    ok(acep["version"] == 2 and acep["data"]["estado"] == "aceptada" and acep["data"]["texto"] == "T prop-decision-sin-registrar-acep",
       "una sugerencia aceptada en la 1.24.0 llega a la cola con su texto y su marca")
    pend = lee(t1 / "cola" / "prop-decision-sin-registrar-pend.json")
    ok(pend["version"] is None and pend["data"]["estado"] == "pendiente", "una pendiente de la 1.24.0 pasa al archivo y su documento de la base sobra")
    rc, out, err = corre(PLAN, t1 / "salida", t1 / "base", "--cierres", t1 / "cierres")
    ok(rc == 0 and "lotes" not in json.loads(out) and (t1 / "salida" / "plan.json").exists(), "el plan va a plan.json y por la conversación solo pasa el resumen")
    rc, out, err = corre(DATOS, "publicar", t1)
    ok(rc != 0 and "--vista" in err, "la primera vez no se publica sin la página: la de antes no sabe leer los archivos")
    rc, out, err = corre(DATOS, "publicar", t1, "--vista", VISTA)
    ok(rc == 0, f"se publica ({err[-300:]})")
    res = json.loads(out) if rc == 0 else {"archivos": [], "base": []}
    nombres = [a["as"] for a in res["archivos"]]
    det_areas = sorted({p.stem.split("--")[0] for p in (t1 / "salida" / "detalle").glob("*.json")})
    pro_areas = sorted({p.stem.split("--")[0] for p in (t1 / "salida" / "proyectos").glob("*.json")})
    VER = __import__("re").search(r'VERSION_TABLERO = "([^"]+)"', VISTA.read_text(encoding="utf-8")).group(1)
    ok(nombres == ["index.html", f"vista-{VER}.css", f"vista-{VER}.js", "datos/estado.json", "datos/tablero.json", "datos/propuestas.json"] + [f"datos/proyectos/{a}.json" for a in pro_areas] + [f"datos/detalle/{a}.json" for a in det_areas],
       f"la primera vez salen la página, los tres archivos, los proyectos (1.24.4) y el detalle (1.24.2) de cada área ({nombres})")
    ok(lee(t1 / "publicar" / "datos" / "estado.json").get("detalle_areas") == det_areas, "estado.json dice qué áreas tienen su archivo de detalle")
    pag = (t1 / "publicar" / "index.html").read_text(encoding="utf-8")
    est = lee(t1 / "publicar" / "datos" / "estado.json")
    ok(f"<title>Tablero {est.get('organizacion')}</title>" in pag, "la página lleva el título de su organización, tomado de meta/estado")
    ok(len(pag.encode()) < 4000 and f'<script src="vista-{VER}.js"></script>' in pag and "<style>" not in pag and "const VERSION_TABLERO" not in pag,
       f"la página es una portada corta que carga su código aparte (1.24.5: {len(pag.encode())} bytes)")
    _js = (t1 / "publicar" / f"vista-{VER}.js").read_text(encoding="utf-8")
    ok(f'const VERSION_TABLERO = "{VER}"' in _js and "<script" not in _js and "</style>" not in (t1 / "publicar" / f"vista-{VER}.css").read_text(encoding="utf-8"),
       "el código y los estilos salen enteros y sin etiquetas")
    tab = lee(t1 / "publicar" / "datos" / "tablero.json")
    gen_proys = {p.stem for p in (t1 / "salida" / "proyectos").glob("*.json")}
    _pro = {k: v for a in pro_areas for k, v in lee(t1 / "publicar" / "datos" / "proyectos" / f"{a}.json").items()}
    ok("proyectos" not in tab and lee(t1 / "publicar" / "datos" / "estado.json").get("proyectos_areas") == pro_areas, "tablero.json ya no lleva los proyectos, y estado.json dice qué áreas tienen su archivo (1.24.4)")
    ok(set(_pro) == gen_proys and set(tab["areas"]) == {p.stem for p in (t1 / "salida" / "areas").glob("*.json")}, "tablero.json trae todas las áreas y todos los proyectos generados")
    ok(est.get("huella_raiz") and est.get("publicado_id") and (est.get("pagina_actualizada") or {}).get("version") == "prueba", "estado.json trae la huella, la marca de la publicación y la versión de la página")
    props1 = lee(t1 / "publicar" / "datos" / "propuestas.json")
    ok("prop-decision-sin-registrar-acep" in props1 and "prop-decision-sin-registrar-pend" in props1, "las sugerencias de la 1.24.0 pasan al archivo")
    ok("estado" not in props1.get("prop-decision-sin-registrar-acep", {}) or props1["prop-decision-sin-registrar-acep"]["estado"] == "pendiente", "en el archivo la sugerencia no lleva la marca: esa sigue en la base")
    lotes = res["base"]
    ok(lotes and lotes[0] == [{"op": "set", "path": f"publicado/{est['publicado_id']}", "data": {"sincronizado": est["sincronizado"]}}], f"la marca de la publicación va sola y primero ({lotes[:1]})")
    ops = [o for l in lotes for o in l]
    ok({"op": "delete", "path": "cambios/prop-decision-sin-registrar-pend", "ifVersion": 1} in ops and not any(o["path"] == "cambios/prop-decision-sin-registrar-acep" for o in ops),
       "el documento de una pendiente de la 1.24.0 se borra; la marca de la aceptada se queda")
    ok({"op": "delete", "path": "cierres/ventas--cuentas--200001010900", "ifVersion": 1} in ops, "los cierres ya recogidos se borran con su versión")
    ok(all(len(l) <= 50 for l in lotes), "las escrituras de la base van en lotes de 50 como mucho")

    print("La siguiente puesta al día, desde los archivos publicados")
    pub = t1 / "publicar" / "datos"
    DET = [f"detalle:{p.stem}={p}" for p in sorted((pub / "detalle").glob("*.json"))]
    PRO = [f"proyectos:{p.stem}={p}" for p in sorted((pub / "proyectos").glob("*.json"))]
    t2 = tmp / "t2"
    jl(t2 / "cola.jsonl", [{"data": {"tipo": "propuesta", "estado": "aplicada", "proyecto": "ventas--cuentas", "clase": "decision-sin-registrar"}, "id": "prop-decision-sin-registrar-acep", "version": 3}])
    jl(t2 / "publicado.jsonl", [{"data": {"sincronizado": est["sincronizado"]}, "id": est["publicado_id"], "version": 1}, {"data": {"sincronizado": "x"}, "id": "p20000101", "version": 4}])
    rc, out, err = corre(DATOS, "base", t2, f"estado={pub / 'estado.json'}", "--cola", t2 / "cola.jsonl", "--cierres", t2 / "no-hay.jsonl", "--publicado", t2 / "publicado.jsonl")
    ok(rc == 0 and out == "", f"paso 1a desde los archivos ({err[-200:]})")
    rc, out, err = corre(PLAN, "--guardada", t2 / "base", "--version", "prueba")
    ok(rc == 0 and out.splitlines()[0] == est["huella_raiz"], "con lo publicado, la huella guardada dice que el tablero sigue valiendo")
    # al día: solo cambia meta/estado, y no se publica
    shutil.copytree(t1 / "salida", t2 / "salida-dia")
    rc, out, err = corre(PLAN, "--cierre", t2 / "base", t2 / "salida", "--sincronizado", "2026-10-31T09:00-06:00", "--cierres", t2 / "cierres")
    ok(rc == 0, f"plan al día ({err[-200:]})")
    rc, out, err = corre(DATOS, "publicar", t2)
    res = json.loads(out) if rc == 0 else {"archivos": None, "base": []}
    ok(rc == 0 and res["archivos"] == [], f"una corrida al día no publica nada ({res.get('archivos')} {err[-200:]})")
    ops = [o for l in res["base"] for o in l]
    marca = next((o for o in ops if o["op"] == "set"), {})
    ok(marca.get("data", {}).get("solo_estado") is True and marca["data"].get("sincronizado") == "2026-10-31T09:00-06:00" and marca["data"].get("publicado_id") == est["publicado_id"],
       "su marca lleva la hora, dice que solo cambió el estado y con qué publicación cuenta")
    ok({"op": "delete", "path": "publicado/p20000101", "ifVersion": 4} in ops and {"op": "delete", "path": f"publicado/{est['publicado_id']}", "ifVersion": 1} in ops,
       "las marcas anteriores se borran con la versión leída, no con una inventada")
    ok(ops and ops[-1]["path"].startswith("publicado/") and res["base"][0][0]["op"] == "set", "la marca nueva va primero y las viejas al final, en su propio lote")
    # una regeneración que no cambia ningún documento pero sí la huella de la raíz publica estado.json: si no, la siguiente regeneraría otra vez
    t4 = tmp / "t4"; shutil.copytree(t2, t4)
    rc, out, err = corre(DATOS, "base", t4, f"tablero={pub / 'tablero.json'}", f"propuestas={pub / 'propuestas.json'}", *PRO, *DET)
    pl = {"lotes": [[{"op": "update", "collection": "meta", "doc_id": "estado", "file_path": str(t4 / "e.json")}]]}
    (t4 / "e.json").write_text(json.dumps({"huella_raiz": "otra-huella", "sincronizado": "2026-10-31T10:00-06:00"}), encoding="utf-8")
    shutil.rmtree(t4 / "salida", ignore_errors=True); (t4 / "salida").mkdir(); (t4 / "salida" / "plan.json").write_text(json.dumps(pl), encoding="utf-8")
    rc, out, err = corre(DATOS, "publicar", t4)
    res = json.loads(out) if rc == 0 else {"archivos": []}
    ok(rc == 0 and [a["as"] for a in res["archivos"]] == ["datos/estado.json"] and lee(t4 / "publicar" / "datos" / "estado.json")["huella_raiz"] == "otra-huella",
       f"una regeneración con la huella nueva y los mismos documentos publica estado.json ({res.get('archivos')} {err[-200:]})")
    # una regeneración: el paso e trae los tres archivos; la aceptada que un cierre aplicó se retira
    for x in ("salida",): shutil.rmtree(t2 / x, ignore_errors=True)
    rc, out, err = corre(DATOS, "base", t2, f"tablero={pub / 'tablero.json'}", f"propuestas={pub / 'propuestas.json'}", *PRO, *DET)
    ok(rc == 0, f"paso e con los archivos ({err[-200:]})")
    c = lee(t2 / "cola" / "prop-decision-sin-registrar-acep.json")
    ok(c["version"] == 3 and c["data"]["estado"] == "aplicada" and c["data"]["texto"], "una sugerencia del archivo lleva encima su marca de la base, con la versión de la marca")
    shutil.copytree(t2 / "salida-dia", t2 / "salida"); (t2 / "salida" / "plan.json").unlink(missing_ok=True)
    (t2 / "salida" / "barrido.json").write_text(json.dumps({"anadir": [], "borrar": [{"id": "prop-decision-sin-registrar-acep", "if_version": 3}]}), encoding="utf-8")
    rc, out, err = corre(PLAN, t2 / "salida", t2 / "base")
    enf = t2 / "enfoque.json"; enf.write_text(json.dumps({"generado": "2026-10-02", "grupos": [{"titulo": "G"}]}), encoding="utf-8")
    (t2 / "salida" / "meta" / "estado-enfoque.json").write_text(json.dumps({"huella_candidatos": "hc-nueva"}), encoding="utf-8")
    rc, out, err = corre(DATOS, "publicar", t2, "--enfoque", enf)
    res = json.loads(out) if rc == 0 else {"archivos": [], "base": []}
    ok(rc == 0, f"se publica la regeneración ({err[-300:]})")
    nombres = [a["as"] for a in res["archivos"]]
    ok(not any(n.startswith("datos/detalle/") for n in nombres) and "index.html" not in nombres and "datos/estado.json" in nombres, f"lo que no cambió no se vuelve a publicar ({nombres})")
    props2 = lee(t2 / "publicar" / "datos" / "propuestas.json")
    ok("prop-decision-sin-registrar-acep" not in props2 and "prop-decision-sin-registrar-pend" in props2, "la sugerencia retirada sale del archivo; las demás se quedan")
    ops = [o for l in res["base"] for o in l]
    ok({"op": "delete", "path": "cambios/prop-decision-sin-registrar-acep", "ifVersion": 3} in ops, "y su marca se borra de la base con su versión")
    tab2 = lee(t2 / "publicar" / "datos" / "tablero.json"); est2 = lee(t2 / "publicar" / "datos" / "estado.json")
    ok(tab2["enfoque"]["grupos"][0]["titulo"] == "G" and est2.get("huella_candidatos") == "hc-nueva", "«Por dónde empezar» entra en tablero.json y su huella en estado.json")
    ok("proyectos" not in tab2 and not any(n.startswith("datos/proyectos") for n in nombres), "solo cambió «Por dónde empezar»: no se vuelve a publicar ningún archivo de proyectos")

    print("La página partida (1.24.5)")
    _ep = t2 / "base" / "meta" / "estado.json"; _eo = _ep.read_text(encoding="utf-8")
    _e = json.loads(_eo); _d = _e.get("data", _e) if isinstance(_e.get("data"), dict) else _e
    _d["pagina_actualizada"] = {"version": VER}; _ep.write_text(json.dumps(_e), encoding="utf-8")
    rc, out, err = corre(DATOS, "publicar", t2, "--enfoque", enf, "--portada", VISTA)
    n3 = [a["as"] for a in json.loads(out)["archivos"]] if rc == 0 else []
    ok(rc == 0 and n3[0] == "index.html" and not any(n.startswith("vista-") for n in n3) and "datos/estado.json" in n3,
       f"con las herramientas de antes, --portada añade solo la portada, que ya carga el código publicado ({n3})")
    _ep = t2 / "base" / "meta" / "estado.json"; _eo = _ep.read_text(encoding="utf-8")
    _e = json.loads(_eo); _d = _e.get("data", _e) if isinstance(_e.get("data"), dict) else _e
    rc, out, err = corre(DATOS, "partida", t2)
    for v_, r_ in (("1.24.4", "no"), ("1.24.5", "si"), ("1.24.10", "si"), ("1.25.0", "si")):
        _d["pagina_actualizada"] = {"version": v_}; _ep.write_text(json.dumps(_e), encoding="utf-8")
        rc, out, err = corre(DATOS, "partida", t2)
        ok(rc == 0 and out.strip() == r_, f"«partida» compara en números: una página {v_} es «{r_}» ({out.strip()} {err[-150:]})")
    _d["pagina_actualizada"] = {"version": "1.0.0"}; _ep.write_text(json.dumps(_e), encoding="utf-8")
    rc, out, err = corre(DATOS, "publicar", t2, "--enfoque", enf, "--portada", VISTA)
    ok(rc != 0 and "--vista" in err, "--portada no sale si la página publicada es de otra versión: cargaría un código que no está")
    rc, out, err = corre(DATOS, "publicar", t2, "--enfoque", enf, "--vista", VISTA)
    r4 = json.loads(out) if rc == 0 else {}
    prev = "1.0.0"
    _ep.write_text(_eo, encoding="utf-8")
    ok(rc == 0 and f"vista-{VER}.js" in [a["as"] for a in r4.get("archivos", [])]
       and {f"vista-{prev}.css", f"vista-{prev}.js"} <= set(r4.get("quitar") or []),
       f"con --vista sale el código de esta versión y se quita el de la anterior ({prev} → {VER}: {r4.get('quitar')})")
    rc, out, err = corre(DATOS, "publicar", t2, "--vista", VISTA, "--portada", VISTA)
    ok(rc != 0 and "solo una" in err, "--vista y --portada no van juntas")
    _vieja = t2 / "estado-vieja.json"
    _vieja.write_text(json.dumps({"organizacion": "Ana & Co", "version_tablero": "1.24.3", "pagina_actualizada": {"version": "1.24.3"}, "publicado_id": "x"}), encoding="utf-8")
    rc, out, err = corre(DATOS, "partir", _vieja, VISTA, t2 / "partir")
    r5 = json.loads(out) if rc == 0 else {}
    e5 = lee(t2 / "partir" / "datos" / "estado.json") if rc == 0 else {}
    ok(rc == 0 and r5.get("partida") is False and [a["as"] for a in r5["archivos"]] == ["index.html", f"vista-{VER}.css", f"vista-{VER}.js", "datos/estado.json"]
       and e5.get("pagina_actualizada", {}).get("version") == VER and e5.get("pagina_actualizada", {}).get("desde") == "1.24.3"
       and e5.get("publicado_id") == "x" and r5.get("titulo") == "Tablero Ana & Co",
       f"«partir» parte una página de una pieza y apunta su versión en estado.json sin tocar lo demás ({err[-200:]})")
    _vieja.write_text(json.dumps({"organizacion": "X", "version_tablero": "1.24.10", "pagina_actualizada": {"version": "1.24.10"}}), encoding="utf-8")
    rc, out, err = corre(DATOS, "partir", _vieja, VISTA, t2 / "partir")
    ok(rc == 0 and json.loads(out) == {"partida": True}, "y con la página ya partida no hace nada")
    _vieja.write_text(json.dumps({"organizacion": "X", "version_tablero": "1.24.3"}), encoding="utf-8")
    for dest in ("", ".", "relativo", "/", str(pathlib.Path.cwd())):
        rc, out, err = corre(DATOS, "partir", _vieja, VISTA, dest)
        ok(rc != 0 and "absoluta" in err, f"«partir» no acepta «{dest}» como salida: la vacía antes de escribir")
    _vieja.write_text("{}", encoding="utf-8")
    rc, out, err = corre(DATOS, "partir", _vieja, VISTA, t2 / "partir")
    ok(rc != 0 and "organizacion" in err, "«partir» no publica un estado.json sin organización ni versión")
    rc, out, err = corre(DATOS, "pagina", VISTA, t2 / "pagina", "--titulo", "Tablero <Ana & Co>")
    ok(rc == 0 and [a["as"] for a in json.loads(out)["archivos"]] == ["index.html", f"vista-{VER}.css", f"vista-{VER}.js"]
       and "<title>Tablero &lt;Ana &amp; Co&gt;</title>" in (t2 / "pagina" / "index.html").read_text(encoding="utf-8"),
       "«pagina», al montar, deja los tres archivos con el título escapado")

    print("El detalle, un archivo por área (1.24.2)")
    rc, out, err = corre(DATOS, "rutas", t4)
    ok(rc == 0 and json.loads(out) == ["datos/tablero.json", "datos/propuestas.json"] + [f"datos/proyectos/{a}.json" for a in pro_areas] + [f"datos/detalle/{a}.json" for a in det_areas], f"«rutas» dice qué traer en el paso e ({out.strip()[:200]})")
    def con_plan(t, ops):
        shutil.rmtree(t / "salida", ignore_errors=True); (t / "salida").mkdir()
        lot = []
        for i, (op, col, doc, data) in enumerate(ops):
            e = {"op": op, "collection": col, "doc_id": doc}
            if data is not None:
                f = t / f"op{i}.json"; f.write_text(json.dumps({"id": doc, "data": data}), encoding="utf-8"); e["file_path"] = str(f)
            lot.append(e)
        (t / "salida" / "plan.json").write_text(json.dumps({"lotes": [lot]}), encoding="utf-8")
        rc, out, err = corre(DATOS, "publicar", t)
        return rc, (json.loads(out) if rc == 0 else {"archivos": [], "base": []}), err
    pid1 = next(p.stem for p in (t1 / "salida" / "detalle").glob("*.json"))
    a1 = pid1.split("--")[0]
    t5 = tmp / "t5"; shutil.copytree(t2, t5)
    corre(DATOS, "base", t5, f"tablero={pub / 'tablero.json'}", f"propuestas={pub / 'propuestas.json'}", *PRO, *DET)
    rc, res, err = con_plan(t5, [("set", "detalle", pid1, {"estado_actual": "CAMBIADO"})])
    nombres = [x["as"] for x in res["archivos"]]
    ok(rc == 0 and [n for n in nombres if n.startswith("datos/detalle")] == [f"datos/detalle/{a1}.json"] and res.get("quitar") == ["datos/detalle.json"]
       and [n for n in nombres if n.startswith("datos/proyectos")] == [],
       f"si cambia el detalle de un proyecto, solo se publica el archivo de su área ({nombres} {err[-200:]})")
    t5b = tmp / "t5b"; shutil.copytree(t2, t5b)
    corre(DATOS, "base", t5b, f"tablero={pub / 'tablero.json'}", f"propuestas={pub / 'propuestas.json'}", *PRO, *DET)
    _pd = dict(_pro[pid1], nombre="CAMBIADO")
    rc, res, err = con_plan(t5b, [("set", "proyectos", pid1, _pd)])
    nombres = [x["as"] for x in res["archivos"]]
    ok(rc == 0 and [n for n in nombres if n.startswith("datos/proyectos")] == [f"datos/proyectos/{a1}.json"] and "datos/tablero.json" not in nombres
       and lee(t5b / "publicar" / "datos" / "proyectos" / f"{a1}.json")[pid1]["nombre"] == "CAMBIADO",
       f"si cambia un proyecto, solo se publica el archivo de proyectos de su área, sin tablero.json (1.24.4) ({nombres} {err[-200:]})")
    # dos versiones del plugin sobre el mismo tablero: si tablero.json vuelve a traer los proyectos, mandan esos y los
    # archivos por área se rehacen desde ellos (revisión de la 1.24.4)
    t5c = tmp / "t5c"; shutil.copytree(t2, t5c)
    tab_mixto = tmp / "tablero-mixto.json"; _pm = {k: dict(v, nombre="DE-TABLERO") for k, v in _pro.items()}
    tab_mixto.write_text(json.dumps({**lee(pub / "tablero.json"), "proyectos": _pm}), encoding="utf-8")
    corre(DATOS, "base", t5c, f"tablero={tab_mixto}", f"propuestas={pub / 'propuestas.json'}", *PRO, *DET)
    rc, res, err = con_plan(t5c, [])
    _f = lee(t5c / "publicar" / "datos" / "proyectos" / f"{a1}.json") if (t5c / "publicar" / "datos" / "proyectos" / f"{a1}.json").exists() else {}
    ok(rc == 0 and _f and all(v.get("nombre") == "DE-TABLERO" for v in _f.values()), f"si tablero.json trae los proyectos, mandan esos y no los archivos por área ({err[-200:]})")
    otras = [a for a in det_areas if a != a1]
    if otras:
        quita = [p.stem for p in (t1 / "salida" / "detalle").glob("*.json") if p.stem.split("--")[0] == otras[0]]
        t6 = tmp / "t6"; shutil.copytree(t2, t6)
        corre(DATOS, "base", t6, f"tablero={pub / 'tablero.json'}", f"propuestas={pub / 'propuestas.json'}", *PRO, *DET)
        rc, res, err = con_plan(t6, [("delete", "detalle", x, None) for x in quita])
        ok(rc == 0 and res.get("quitar") == [f"datos/detalle/{otras[0]}.json", "datos/detalle.json"] and otras[0] not in lee(t6 / "publicar" / "datos" / "estado.json").get("detalle_areas", []),
           f"el archivo de un área que se queda sin detalle se quita al publicar ({res.get('quitar')} {err[-200:]})")
    # un tablero de la 1.24.1: un solo datos/detalle.json
    uno = tmp / "detalle-uno.json"
    uno.write_text(json.dumps({p.stem: lee(p).get("data", lee(p)) for p in (t1 / "salida" / "detalle").glob("*.json")}), encoding="utf-8")
    e_viejo = tmp / "estado-viejo.json"; ev = lee(pub / "estado.json"); ev.pop("detalle_areas", None); ev.pop("proyectos_areas", None); e_viejo.write_text(json.dumps(ev), encoding="utf-8")
    t7 = tmp / "t7"; t7.mkdir()
    corre(DATOS, "base", t7, f"estado={e_viejo}", "--cola", t7 / "no.jsonl", "--cierres", t7 / "no.jsonl", "--publicado", t7 / "no.jsonl")
    rc, out, err = corre(DATOS, "rutas", t7)
    ok(rc == 0 and json.loads(out)[-1] == "datos/detalle.json", f"en un tablero de la 1.24.1, «rutas» pide el detalle.json único ({out.strip()})")
    tab_viejo = tmp / "tablero-viejo.json"; tab_viejo.write_text(json.dumps({**lee(pub / "tablero.json"), "proyectos": _pro}), encoding="utf-8")
    rc, out, err = corre(DATOS, "base", t7, f"tablero={tab_viejo}", f"propuestas={pub / 'propuestas.json'}", f"detalle={uno}")
    ok(rc == 0, f"el paso e acepta el detalle.json de la 1.24.1 ({err[-200:]})")
    rc, res, err = con_plan(t7, [])
    nombres = [x["as"] for x in res["archivos"]]
    ok(rc == 0 and [n for n in nombres if n.startswith("datos/detalle")] == [f"datos/detalle/{a}.json" for a in det_areas] and res.get("quitar") == ["datos/detalle.json"]
       and [n for n in nombres if n.startswith("datos/proyectos")] == [f"datos/proyectos/{a}.json" for a in pro_areas] and "proyectos" not in lee(t7 / "publicar" / "datos" / "tablero.json")
       and lee(t7 / "publicar" / "datos" / "estado.json").get("detalle_areas") == det_areas and lee(t7 / "publicar" / "datos" / "estado.json").get("proyectos_areas") == pro_areas,
       f"en la primera regeneración se parten por áreas el detalle y los proyectos y se quita el detalle.json de la 1.24.1, aunque nada cambie ({nombres} {res.get('quitar')} {err[-200:]})")
    # el paso e tiene que traer todo el detalle que el tablero tiene
    t8 = tmp / "t8"; shutil.copytree(t2, t8)
    rc, out, err = corre(DATOS, "base", t8, f"tablero={pub / 'tablero.json'}", f"propuestas={pub / 'propuestas.json'}", *PRO, *DET[1:])
    ok(rc != 0 and "Faltan detalles" in err, f"si falta el detalle de un área que el tablero tiene, el paso e para ({err[-200:]})")
    rc, out, err = corre(DATOS, "base", t8, f"tablero={pub / 'tablero.json'}", f"propuestas={pub / 'propuestas.json'}", *PRO, *DET[1:], DET[0].split("=")[0] + "=-")
    ok(rc == 0, f"uno que read_file dijo que no existe se pasa como detalle:<área>=- ({err[-200:]})")
    rc, res, err = con_plan(t8, [])
    ok(rc == 0 and "aviso_detalle" in res, f"y si sus proyectos se quedan sin detalle, publicar lo avisa ({res.get('aviso_detalle')} {err[-200:]})")
    t9 = tmp / "t9"; t9.mkdir()
    corre(DATOS, "base", t9, f"estado={e_viejo}", "--cola", t9 / "no.jsonl", "--cierres", t9 / "no.jsonl", "--publicado", t9 / "no.jsonl")
    rc, out, err = corre(DATOS, "base", t9, f"tablero={pub / 'tablero.json'}", f"propuestas={pub / 'propuestas.json'}")
    ok(rc != 0 and "detalle=" in err, f"un tablero de la 1.24.1 sin su detalle.json en el paso e, para ({err[-200:]})")

    print("Lo que no se puede hacer")
    t3 = tmp / "t3"
    rc, out, err = corre(DATOS, "base", t3, f"estado={pub / 'estado.json'}", "--cola", t3 / "no.jsonl", "--cierres", t3 / "no.jsonl", "--publicado", t3 / "no.jsonl")
    ok(rc == 0, "una consulta que no dejó archivo cuenta como vacía")
    shutil.copytree(t1 / "salida", t3 / "salida")
    rc, out, err = corre(DATOS, "publicar", t3)
    ok(rc != 0 and "paso e" in err, "un plan que regenera sin haber traído los archivos se para, en vez de publicar un tablero vacío")
    jl(t3 / "mala.jsonl", [{"data": {"tipo": "nota"}, "id": "c1", "version": 1}]); (t3 / "mala.jsonl").write_text('{"data": {"tipo": "nota"}, "id": "c1", "version": 1}\n{"data": {"tipo": "no', encoding="utf-8")
    rc, out, err = corre(DATOS, "base", t3, f"estado={pub / 'estado.json'}", "--cola", t3 / "mala.jsonl")
    ok(rc == 2 and "vuelve a copiarlas" in err, "una línea mal copiada para el paso y pide repetir la copia")
    rc, out, err = corre(DATOS, "base", t3, "estado=/no/existe.json")
    ok(rc != 0 and "No encuentro" in err, "un archivo descargado que no está se dice")
    jl(t3 / "grande.jsonl", [{"id": "c9", "version": 1, "tooLarge": True}])
    rc, out, err = corre(DATOS, "base", t3, f"estado={pub / 'estado.json'}", "--cola", t3 / "grande.jsonl")
    ok(rc == 2 and not (t3 / "cola" / "c9.json").exists(), "un documento que la consulta trae sin cuerpo no entra como un cambio vacío (se borraría)")
    rc, out, err = corre(DATOS, "propuestas", pub / "propuestas.json", "ventas--cuentas")
    ok(rc == 0 and "prop-decision-sin-registrar-acep" in out, "la sesión ve las sugerencias de su proyecto")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print("\nTodo bien." if not fallos else f"\n{len(fallos)} fallo(s).")
sys.exit(1 if fallos else 0)
