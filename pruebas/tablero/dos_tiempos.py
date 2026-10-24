#!/usr/bin/env python3
"""Prueba la generación en dos tiempos: inventario en la computadora y generación sobre una copia.

Uso: dos_tiempos.py <generar_vista.py> <plan_subida.py> <raiz> <carpeta-de-trabajo>

Comprueba que generar sobre la copia de «leer» con el inventario da exactamente los mismos documentos que generar
sobre la raíz; que una copia incompleta o con archivos de más se rechaza; que el --modo de una tarea de antes de la
1.18 no cambia nada (hay un solo modo); y que el plan de subida solo propone lo que cambió.
"""
import json, re, os, shutil, subprocess, sys, pathlib

GEN, PLAN, RAIZ, TRAB = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3]), pathlib.Path(sys.argv[4])
fallos = 0


def ok(cond, texto):
    global fallos
    print(("  bien  " if cond else "  FALLA ") + texto)
    if not cond:
        fallos += 1


def correr(*args):
    return subprocess.run([sys.executable, GEN, *map(str, args)], capture_output=True, text=True)


def docs(carpeta):
    """{coleccion/doc: contenido sin la hora de sincronización}"""
    out = {}
    for p in sorted(pathlib.Path(carpeta).rglob("*.json")):
        if p.name == "indice.json":
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        d.pop("sincronizado", None); d.pop("generado", None); d.pop("huella_raiz", None); d.pop("huellas", None)
        out[p.relative_to(carpeta).as_posix()] = d
    return out


def copiar(leer, destino):
    shutil.rmtree(destino, ignore_errors=True)
    for r in leer:
        (destino / r).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(RAIZ / r, destino / r)   # como la herramienta: sin conservar las fechas


print("Dos tiempos: inventario en la computadora, generación sobre la copia")
shutil.rmtree(TRAB, ignore_errors=True); TRAB.mkdir(parents=True)
for modo in ("completo",):   # un solo modo desde la 1.18; los nombres de las carpetas de trabajo se quedan
    r1 = correr(RAIZ, "--inventario")
    ok(r1.returncode == 0, f"{modo}: el inventario sale sin errores")
    salida = json.loads(r1.stdout)
    leer, inv = salida["leer"], salida["inventario"]
    ok(len(json.dumps(inv)) < 20_000, f"{modo}: el inventario es pequeño ({len(json.dumps(inv))} bytes), porque pasa por la conversación")
    ok(all(not r.startswith(("base/", )) or r == "base/premisas.md" for r in leer), f"{modo}: de base/ solo se trae premisas.md")
    ok(not any(seg in ("fuentes", "taller", "restringido") for r in leer for seg in r.split("/")), f"{modo}: nunca se trae nada de fuentes/, taller/ ni restringido/")
    copia = TRAB / f"copia-{modo}"
    copiar(leer, copia)
    (TRAB / f"inv-{modo}.json").write_text(json.dumps(inv, ensure_ascii=False), encoding="utf-8")
    correr(RAIZ, TRAB / f"directo-{modo}", "--version", "prueba")
    r2 = correr(copia, TRAB / f"dos-{modo}", "--desde-inventario", TRAB / f"inv-{modo}.json", "--version", "prueba")
    ok(r2.returncode == 0, f"{modo}: la generación sobre la copia sale sin errores")
    a, b = docs(TRAB / f"directo-{modo}"), docs(TRAB / f"dos-{modo}")
    distintos = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    ok(not distintos, f"{modo}: los dos caminos dan los mismos documentos" + (f" (difieren: {', '.join(distintos[:5])})" if distintos else ""))

# una copia con un archivo vaciado o truncado tampoco
truncado = sorted(copia.rglob("sesiones.md"))[0] if (copia := TRAB / "copia-completo") else None
_g = truncado.read_bytes(); truncado.write_bytes(b"")
r = correr(copia, TRAB / "x", "--desde-inventario", TRAB / "inv-completo.json")
ok(r.returncode == 3, "una copia con un archivo que llegó vacío o a medias se rechaza")
truncado.write_bytes(_g)
# un inventario copiado con un cambio se rechaza
mal = json.loads((TRAB / "inv-completo.json").read_text(encoding="utf-8")); mal["version_metodo"] = "9.9"
(TRAB / "inv-mal.json").write_text(json.dumps(mal), encoding="utf-8")
r = correr(copia, TRAB / "x", "--desde-inventario", TRAB / "inv-mal.json")
ok(r.returncode == 4, "un inventario que se copió con algún cambio se rechaza")
# una copia con un archivo de más (de una corrida anterior) o de menos no se acepta
copia = TRAB / "copia-completo"
extra = copia / "ventas" / "sobra.md"; extra.write_text("x", encoding="utf-8")
r = correr(copia, TRAB / "x", "--desde-inventario", TRAB / "inv-completo.json")
ok(r.returncode == 3 and "no coincide" in r.stderr, "una copia con archivos de más se rechaza y dice qué hacer")
extra.unlink()
falta = sorted(copia.rglob("sesiones.md"))[0]; guardado = falta.read_bytes(); falta.unlink()
r = correr(copia, TRAB / "x", "--desde-inventario", TRAB / "inv-completo.json")
ok(r.returncode == 3, "una copia a la que le falta un archivo se rechaza")
falta.write_bytes(guardado)
r = correr(copia, TRAB / "x", "--desde-inventario", TRAB / "inv-completo.json", "--modo", "publico")
ok(r.returncode == 0, "una tarea de antes de la 1.18 que pasa --modo publico genera igual: hay un solo modo")

# huella de la raíz: la misma raíz da la misma huella; tocar un archivo que el tablero lee la cambia; llega a meta/estado
RAIZ2 = TRAB / "raiz-tocada"; shutil.rmtree(RAIZ2, ignore_errors=True); shutil.copytree(RAIZ, RAIZ2)   # copy2 conserva las fechas
_s_a = json.loads(subprocess.run([sys.executable, GEN, RAIZ2, "--inventario"], capture_output=True, text=True).stdout)
r_a, _leer = _s_a["inventario"], _s_a["leer"]
r_b = json.loads(subprocess.run([sys.executable, GEN, RAIZ2, "--inventario"], capture_output=True, text=True).stdout)["inventario"]
ok(bool(r_a.get("huella_raiz")) and r_a["huella_raiz"] == r_b["huella_raiz"], "huella de la raíz: dos inventarios seguidos dan la misma")
_al = subprocess.run([sys.executable, GEN, RAIZ2, "--inventario", "--lineas", "--si-cambia", r_a["huella_raiz"]], capture_output=True, text=True).stdout.strip().split("\n")
ok(_al[0] == "AL DIA" and len(_al) == 2 and re.fullmatch(r"20\d\d-\d\d-\d\dT\d\d:\d\d[+-]\d\d:\d\d", _al[1]), f"con la huella guardada igual, el inventario dice «AL DIA» y el instante en la zona de la organización ({_al})")
_ln = subprocess.run([sys.executable, GEN, RAIZ2, "--inventario", "--lineas", "--si-cambia", "otra"], capture_output=True, text=True).stdout.split("\n")
ok(json.loads(_ln[0]).get("sello") == r_a["sello"] and int(_ln[1]) == len(_leer) and _ln[2] == _leer[0], "con otra huella, el inventario sale en líneas: inventario, cuántos archivos y sus rutas")
tocado = RAIZ2 / _leer[1]
_st = tocado.stat()
os.utime(tocado, (_st.st_atime, _st.st_mtime + 120))
r_c = json.loads(subprocess.run([sys.executable, GEN, RAIZ2, "--inventario"], capture_output=True, text=True).stdout)["inventario"]
ok(r_c["huella_raiz"] != r_a["huella_raiz"], "huella de la raíz: cambiar la fecha de un archivo que el tablero lee la cambia")
_est = json.loads((TRAB / "dos-completo" / "meta" / "estado.json").read_text(encoding="utf-8"))
ok(_est.get("huella_raiz") == json.loads((TRAB / "inv-completo.json").read_text(encoding="utf-8"))["huella_raiz"], "huella de la raíz: la generación la deja en meta/estado")

# la huella guardada vale solo si la versión del plugin, la tarea y «sin horario» siguen igual
_g = TRAB / "guardada"; (_g / "meta").mkdir(parents=True, exist_ok=True)
(_g / "meta" / "estado.json").write_text(json.dumps({"huella_raiz": "h1", "version_tablero": "9.9.9", "tarea": "trig_x", "tarea_manual": True}), encoding="utf-8")
def _guard(*a): return subprocess.run([sys.executable, PLAN, "--guardada", _g, *a], capture_output=True, text=True).stdout.split("\n")[0].strip()
ok(_guard("--version", "9.9.9", "--tarea", "trig_x", "--manual") == "h1", "huella guardada: misma versión y misma tarea, vale")
ok(_guard("--version", "9.9.10", "--tarea", "trig_x", "--manual") == "-", "huella guardada: con otra versión del plugin hay que regenerar")
ok(_guard("--version", "9.9.9", "--tarea", "trig_x") == "-", "huella guardada: si la tarea pasó a tener horario, hay que regenerar")
ok(_guard("--version", "9.9.9") == "-", "huella guardada: sin tarea, hay que regenerar")
ok(subprocess.run([sys.executable, PLAN, "--guardada", TRAB / "no-existe", "--version", "9.9.9"], capture_output=True, text=True).stdout.split() == ["-", "-"], "huella guardada: con la base vacía (al montar), hay que regenerar")
# la cola retenida llega a meta/estado
(TRAB / "ret.json").write_text('["c9", "c3"]', encoding="utf-8")
(TRAB / "aj.json").write_text('["c9"]', encoding="utf-8")
correr(TRAB / "copia-completo", TRAB / "dos-ret", "--desde-inventario", TRAB / "inv-completo.json", "--modo", "completo", "--version", "prueba", "--cola-retenida", TRAB / "ret.json", "--cola-ajena", TRAB / "aj.json")
_est = json.loads((TRAB / "dos-ret" / "meta" / "estado.json").read_text(encoding="utf-8"))
ok(_est.get("cola_retenida") == ["c3", "c9"], "lo que la sincronización deja en la cola a propósito llega a meta/estado")
ok(_est.get("cola_ajena") == ["c9"], "lo que es de un área de otra cuenta llega aparte, para que la página diga a quién pasárselo")
# con la cuenta que genera el tablero, en dos tiempos sale lo mismo que en la computadora (los motivos de lo que no se lee)
correr(TRAB / "copia-completo", TRAB / "dos-beto", "--desde-inventario", TRAB / "inv-completo.json", "--modo", "completo", "--version", "prueba", "--cuenta", "beto@ejemplo.test")
subprocess.run([sys.executable, GEN, RAIZ, TRAB / "dir-beto", "--modo", "completo", "--version", "prueba", "--cuenta", "beto@ejemplo.test"], capture_output=True, text=True)
_mot = lambda d: {f"{c}/{f.stem}": (json.loads(f.read_text(encoding="utf-8")).get("motivo"), json.loads(f.read_text(encoding="utf-8")).get("mio")) for c in ("areas", "proyectos") for f in (d / c).glob("*.json")}
ok(_mot(TRAB / "dos-beto") == _mot(TRAB / "dir-beto") and _mot(TRAB / "dos-beto").get("areas/legal") == ("sin-carpeta", True), "con --cuenta, en dos tiempos los motivos salen igual que en la computadora")

# huella por proyecto: lo que no cambió no se trae y su documento sale de la base; el resultado es el mismo que rehacerlo todo
for modo in ("completo", "publico"):
    R3 = TRAB / f"raiz-inc-{modo}"; shutil.rmtree(R3, ignore_errors=True); shutil.copytree(RAIZ, R3)
    def _inv(*extra):
        r_ = subprocess.run([sys.executable, GEN, R3, "--inventario", "--modo", modo, *extra], capture_output=True, text=True)
        return json.loads(r_.stdout)
    def _gen(sal, s_, previos=None):
        inv_p = TRAB / f"inv-inc-{modo}.json"; inv_p.write_text(json.dumps(s_["inventario"], ensure_ascii=False), encoding="utf-8")
        cop = TRAB / f"copia-inc-{modo}"; shutil.rmtree(cop, ignore_errors=True)
        for r_ in s_["leer"]:
            (cop / r_).parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(R3 / r_, cop / r_)
        cop.mkdir(parents=True, exist_ok=True)
        extra = ["--previos", previos] if previos else []
        return subprocess.run([sys.executable, GEN, cop, sal, "--desde-inventario", inv_p, "--modo", modo, "--version", "prueba", *extra], capture_output=True, text=True)
    def _volcar(sal, dest, envolver=False):
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(sal, dest, ignore=shutil.ignore_patterns("indice.json", "enfoque-candidatos.json"))
        if envolver:   # ArtifactData a veces deja cada documento envuelto en «data»
            for p_ in dest.rglob("*.json"):
                p_.write_text(json.dumps({"data": json.loads(p_.read_text(encoding="utf-8")), "version": 3}), encoding="utf-8")
    s0 = _inv(); _gen(TRAB / f"inc0-{modo}", s0)
    _volcar(TRAB / f"inc0-{modo}", TRAB / f"base-inc-{modo}", envolver=(modo == "publico"))
    hs = json.loads((TRAB / f"inc0-{modo}" / "meta" / "estado.json").read_text(encoding="utf-8")).get("huellas") or []
    ok(len(hs) >= 2, f"{modo}: la generación guarda en meta/estado una huella por proyecto ({len(hs)})")
    s1 = _inv("--sin-cambios", ",".join(hs))
    ok(not any(r_.count("/") >= 2 for r_ in s1["leer"]), f"{modo}: sin cambios, el inventario solo pide guia.md, premisas y los area.md ({len(s1['leer'])} de {len(s0['leer'])})")
    ok(s1["inventario"].get("fuera_reusar") is True and "fuera" not in s1["inventario"], f"{modo}: sin cambios, lo de fuera de la memoria también se reutiliza")
    ok(len(json.dumps(s1["inventario"])) < len(json.dumps(s0["inventario"])), f"{modo}: el inventario reutilizando es más pequeño ({len(json.dumps(s1['inventario']))} frente a {len(json.dumps(s0['inventario']))} bytes)")
    r1 = _gen(TRAB / f"inc1-{modo}", s1, TRAB / f"base-inc-{modo}")
    a, b = docs(TRAB / f"inc0-{modo}"), docs(TRAB / f"inc1-{modo}")
    dif = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    ok(r1.returncode == 0 and not dif, f"{modo}: reutilizando la base sale lo mismo que rehaciéndolo todo" + (f" (difieren: {', '.join(dif[:4])}{r1.stderr[-200:]})" if dif or r1.returncode else ""))
    # reescribir el Panorama de un área no obliga a rehacer sus proyectos; tocar la bitácora de uno, solo ese
    am = next(R3.glob("*/area.md")); t_ = am.read_text(encoding="utf-8")
    am.write_text(t_.replace("## Proyectos", "## Panorama\n2026-10-16 · Otro panorama de prueba.\n\n## Proyectos", 1) if "## Panorama" not in t_ else re.sub(r"(## Panorama\n)(.*?)(\n## )", r"\1 2026-10-16 · Otro panorama.\3", t_, count=1, flags=re.S), encoding="utf-8")
    ses_ = sorted(p_ for p_ in R3.glob("*/*/sesiones.md") if p_.relative_to(R3).as_posix() in s0["leer"])[0]
    ses_.write_text(ses_.read_text(encoding="utf-8") + "\n## 2026-08-02 · Una sesión más\nTrabajamos en: prueba.\n", encoding="utf-8")
    s2 = _inv("--sin-cambios", ",".join(hs))
    tocado_ = ses_.parent.relative_to(R3).as_posix()
    pide = {r_.rsplit("/", 1)[0] for r_ in s2["leer"] if r_.count("/") >= 2}
    pide = {"/".join(x.split("/")[:2]) for x in pide}
    ok(pide == {tocado_}, f"{modo}: con un proyecto tocado y el Panorama reescrito, solo se traen los archivos de ese proyecto" + ("" if pide == {tocado_} else f" (pide {sorted(pide)})"))
    r2 = _gen(TRAB / f"inc2-{modo}", s2, TRAB / f"base-inc-{modo}")
    subprocess.run([sys.executable, GEN, R3, TRAB / f"inc2-directo-{modo}", "--modo", modo, "--version", "prueba"], capture_output=True, text=True)
    a, b = docs(TRAB / f"inc2-directo-{modo}"), docs(TRAB / f"inc2-{modo}")
    dif = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    ok(r2.returncode == 0 and not dif, f"{modo}: con un proyecto tocado, el resultado es el mismo que generar en la computadora" + (f" (difieren: {', '.join(dif[:4])}{r2.stderr[-200:]})" if dif or r2.returncode else ""))
    # si la base no tiene lo que se pide reutilizar, la generación lo dice y pide el inventario entero
    falta_ = TRAB / f"base-inc-{modo}" / "proyectos" / f"{s2['inventario']['reusar'][0]}.json"; falta_.unlink()
    r3 = _gen(TRAB / f"inc3-{modo}", s2, TRAB / f"base-inc-{modo}")
    ok(r3.returncode == 5 and "sin --sin-cambios" in r3.stderr, f"{modo}: si a la base le falta un proyecto que se reutiliza, se para con código 5 y dice qué hacer")
    r4 = _gen(TRAB / f"inc4-{modo}", s2)
    ok(r4.returncode == 5, f"{modo}: sin --previos, un inventario que reutiliza se rechaza")
# un proyecto cuyo id la base no admite (acentos) no guarda huella: nunca se pide reutilizarlo
R4 = TRAB / "raiz-acento"; shutil.rmtree(R4, ignore_errors=True); shutil.copytree(RAIZ, R4)
_area = next(R4.glob("*/area.md")).parent
(_area / "diseño").mkdir(); (_area / "diseño" / "proyecto.md").write_text("---\nestado: vigente\nactualizado: 2026-08-01\n---\n\n# Diseño\n", encoding="utf-8")
_i = json.loads(subprocess.run([sys.executable, GEN, R4, "--inventario"], capture_output=True, text=True).stdout)
_pid = f"{_area.name}--diseño"
_i2 = json.loads(subprocess.run([sys.executable, GEN, R4, "--inventario", "--sin-cambios", ",".join(_i["inventario"]["huellas"].values())], capture_output=True, text=True).stdout)
ok(_pid not in _i["inventario"]["huellas"] and _pid not in _i2["inventario"].get("reusar", []) and f"{_area.name}/diseño/proyecto.md" in _i2["leer"],
   "un proyecto con acentos en su carpeta no guarda huella y se trae siempre")

_g2 = TRAB / "guardada2"; (_g2 / "meta").mkdir(parents=True, exist_ok=True)
(_g2 / "meta" / "estado.json").write_text(json.dumps({"data": {"huella_raiz": "h1", "version_tablero": "9.9.9", "huellas": ["aa", "bb"]}}), encoding="utf-8")
_o = lambda *a: subprocess.run([sys.executable, PLAN, "--guardada", _g2, *a], capture_output=True, text=True).stdout.split("\n")
ok(_o("--version", "9.9.9")[:2] == ["h1", "aa,bb"], "huellas guardadas: con la misma versión salen la huella de la raíz y las de cada proyecto")
ok(_o("--version", "9.9.9", "--tarea", "trig_y")[:2] == ["-", "aa,bb"], "huellas guardadas: si cambió la tarea hay que regenerar, pero los proyectos se reutilizan")
ok(_o("--version", "9.9.10")[:2] == ["-", "-"], "huellas guardadas: con otra versión del plugin no se reutiliza nada")

# plan de subida: con la base igual a la salida, solo meta/estado; con un proyecto cambiado, ese y meta; lo que sobra se borra
salida = TRAB / "dos-completo"
volcado = TRAB / "volcado"
shutil.rmtree(volcado, ignore_errors=True)
shutil.copytree(salida, volcado, ignore=shutil.ignore_patterns("indice.json", "enfoque-candidatos.json"))
plan = json.loads(subprocess.run([sys.executable, PLAN, salida, volcado], capture_output=True, text=True).stdout)
escr = [e for l in plan["lotes"] for e in l]
ok([(e["collection"], e["doc_id"], e["op"]) for e in escr] == [("meta", "estado", "update")], "plan: sin cambios, solo se sube meta/estado (como update)")
vacio = TRAB / "vacio"; vacio.mkdir(exist_ok=True)
plan0 = json.loads(subprocess.run([sys.executable, PLAN, salida, vacio], capture_output=True, text=True).stdout)
e0 = [e for l in plan0["lotes"] for e in l]
ok(all(e["op"] == "set" and not e["existe"] for e in e0) and len(e0) == len(json.loads((salida / "indice.json").read_text())), "plan: con la base vacía (al montar) todo va como set, también meta/estado")
uno = sorted((volcado / "proyectos").glob("*.json"))[0]
d = json.loads(uno.read_text(encoding="utf-8")); d["huella"] = "otra"; uno.write_text(json.dumps(d), encoding="utf-8")
(volcado / "proyectos" / "ya-no-existe.json").write_text(json.dumps({"huella": "h"}), encoding="utf-8")
plan = json.loads(subprocess.run([sys.executable, PLAN, salida, volcado], capture_output=True, text=True).stdout)
escr = [e for l in plan["lotes"] for e in l]
ok(any(e["doc_id"] == uno.stem and e["op"] == "set" and e["existe"] for e in escr), "plan: un proyecto que cambió se sube entero, marcado como existente")
ok(any(e["doc_id"] == "ya-no-existe" and e["op"] == "delete" for e in escr), "plan: un proyecto que ya no sale de la raíz se borra")
(volcado / "detalle").mkdir(exist_ok=True); (volcado / "detalle" / "ya-no-existe.json").write_text(json.dumps({"huella": "h"}), encoding="utf-8")
plan = json.loads(subprocess.run([sys.executable, PLAN, salida, volcado], capture_output=True, text=True).stdout)
escr = [e for l in plan["lotes"] for e in l]
ok(any(e["collection"] == "detalle" and e["doc_id"] == "ya-no-existe" and e["op"] == "delete" for e in escr), "plan: el detalle de un proyecto que ya no sale también se borra (1.19)")
ids = [(e["collection"], e["doc_id"]) for e in e0]
ok(all(("detalle", d) not in ids or ids.index(("detalle", d)) == ids.index(("proyectos", d)) + 1 for _, d in ids if _ == "proyectos"), "plan: el detalle de un proyecto va justo después de su proyecto, para caer en el mismo lote")
ok(all(pathlib.Path(e["file_path"]).is_file() for e in escr if e["op"] != "delete"), "plan: cada escritura apunta a un archivo que existe")
ok(all(len(l) <= 50 for l in plan["lotes"]), "plan: ningún lote pasa de 50 entradas")
ok([e for l in plan["lotes"] for e in l][-1]["doc_id"] == "estado", "plan: meta/estado va el último, para que un lote que falla no deje la huella nueva")

print("\nTodo bien." if not fallos else f"\n{fallos} fallos.")
sys.exit(1 if fallos else 0)
