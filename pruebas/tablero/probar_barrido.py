#!/usr/bin/env python3
"""Prueba el barrido (skills/tablero/barrido.py) con una raíz inventada: cada detector, la reconciliación con la cola
(no repite, no vuelve a proponer lo descartado, borra lo que ya no es cierto, no toca lo de proyectos que no vienen)
y que aplicar_cambios.py deja las propuestas en paz. No toca ninguna raíz real."""
import sys, json, pathlib, subprocess, tempfile, shutil

AQUI = pathlib.Path(__file__).resolve().parent
TABLERO = AQUI.parent.parent / "plugins/memoria/skills/tablero"
BARRIDO, APLICAR = TABLERO / "barrido.py", TABLERO / "aplicar_cambios.py"
fallos = []
def ok(c, q):
    print(("  bien  " if c else "  FALLA ") + q)
    if not c: fallos.append(q)

def escribir(p, t):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(t, encoding="utf-8")

def proyecto(raiz, area, nombre, actualizado, pasos, sesiones, decisiones=""):
    escribir(raiz / area / "area.md", "---\nestado: vigente\n---\n# Área\n") if not (raiz / area / "area.md").exists() else None
    escribir(raiz / area / nombre / "proyecto.md",
             f"---\nestado: vigente\nactualizado: {actualizado}\n---\n# {nombre}\n\n## Estado actual\nEn marcha.\n\n## Siguientes pasos\n" + "".join(f"- {p}\n" for p in pasos))
    escribir(raiz / area / nombre / "sesiones.md", "---\nestado: vigente\n---\n# Sesiones\n\n" + sesiones)
    escribir(raiz / area / nombre / "decisiones.md", "---\nestado: vigente\n---\n# Decisiones\n\n" + decisiones)

def sesion(fecha, trabajamos, avances, extra=""):
    return f"## {fecha}\nTrabajamos en: {trabajamos}\nAvances: {avances}\nPendiente: nada\nSesión de: Ana · plugin 1.21.0\n\n{extra}"

def correr(raiz, salida, cola=None, hoy="2026-10-23"):
    cmd = [sys.executable, str(BARRIDO), str(raiz), str(salida), "--hoy", hoy] + (["--cola", str(cola)] if cola else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(r.stdout, r.stderr); fallos.append("barrido.py falló"); return None
    return json.loads((salida / "barrido.json").read_text(encoding="utf-8")), {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (salida / "cambios").glob("*.json")}

tmp = pathlib.Path(tempfile.mkdtemp())
try:
    raiz = tmp / "raiz"
    proyecto(raiz, "ventas", "viejo", "2026-09-01", ["Llamar a Luis"], sesion("2026-10-10", "el seguimiento", "Se habló con Luis."))
    proyecto(raiz, "ventas", "hecho", "2026-10-20", ["Mandar la propuesta de una página a Cliente Uno", "Pedir el precio de la fase 2"],
             sesion("2026-10-20", "la propuesta", "Se mandó a Cliente Uno la propuesta en una página."))
    proyecto(raiz, "ventas", "limpio", "2026-10-20", ["Revisar la plantilla"], sesion("2026-10-20", "la plantilla", "Se revisó el índice del catálogo."))
    proyecto(raiz, "ventas", "anios", "2026-10-20", ["Seguir"], sesion("2026-10-20", "x", "Avance sin más.", extra="## 2025-12-01\nTrabajamos en: y\nAvances: z\nSesión de: Ana\n"))
    proyecto(raiz, "ventas", "decidimos", "2026-10-22", ["Esperar respuesta"], sesion("2026-10-22", "el precio", "Decidimos cobrar el piloto en dos pagos."),
             decisiones="## 2026-09-01 · Otra cosa\nDecidió: Ana\nPor qué: x\n")
    proyecto(raiz, "ventas", "tarea", "2026-10-05", ["Llamar"], sesion("2026-10-05", "x", "algo") + "## 2026-10-21 (tarea)\nTrabajamos en: lo marcado.\nAvances: marcado.\nSesión de: tarea del tablero\n")
    proyecto(raiz, "ventas", "cerrado", "2026-08-01", [], sesion("2026-10-10", "x", "y"))
    t = raiz / "ventas/cerrado/proyecto.md"; t.write_text(t.read_text().replace("En marcha.", "Proyecto terminado el 2026-10-10"), encoding="utf-8")

    salida = tmp / "s1"; salida.mkdir()
    b, docs = correr(raiz, salida)
    por = lambda clase: sorted(d["proyecto"] for d in docs.values() if d["clase"] == clase)
    print("detectores")
    ok(por("estado-desfasado") == ["ventas--viejo"], f"estado desfasado: solo el proyecto cuya cabecera es más vieja que su última sesión real (hay {por('estado-desfasado')})")
    ok("ventas--tarea" not in por("estado-desfasado"), "una entrada «(tarea)» no cuenta como sesión")
    ok("ventas--cerrado" not in por("estado-desfasado"), "un proyecto terminado no se propone")
    ok(por("paso-hecho") == ["ventas--hecho"] and len([d for d in docs.values() if d["clase"] == "paso-hecho"]) == 1, "paso hecho: solo el paso que la sesión cuenta, no el otro ni los de otros proyectos")
    ok(por("rotacion") == ["ventas--anios"], "rotación: un registro que mezcla años")
    ok([j["proyecto"] for j in b["para_juicio"]] == ["ventas--decidimos"], "una decisión contada en una sesión y no registrada va a juicio del modelo, no a la cola")
    ok(all(d["tipo"] == "propuesta" and d["origen"] == "barrido" and d["estado"] == "pendiente" for d in docs.values()), "todo documento es de tipo «propuesta», de origen barrido, pendiente")
    ok(all("\n" not in d["texto"] and "\n" not in d["por_que"] and len(d["texto"]) <= 300 for d in docs.values()), "los textos van en una sola línea y cortos")
    ok(all(i.startswith("prop-") for i in docs), "los id son «prop-…»")
    ok(len(b["anadir"]) == len(docs) and b["borrar"] == [], "primera corrida: se añaden todas y no se borra nada")
    ok(sorted(b["proyectos"]) == sorted(f"ventas--{n}" for n in ("viejo", "hecho", "limpio", "anios", "decidimos", "tarea", "cerrado")), "dice qué proyectos barrió")

    print("reconciliación con la cola")
    cola = tmp / "cola"; cola.mkdir()
    for i, d in docs.items():
        escribir(cola / f"{i}.json", json.dumps({"id": i, "data": d, "version": 3}))
    escribir(cola / "nota1.json", json.dumps({"id": "nota1", "data": {"tipo": "nota", "proyecto": "ventas--viejo", "nota": "ojo"}, "version": 1}))
    b2, d2 = correr(raiz, tmp / "s2", cola)
    ok(b2["anadir"] == [] and b2["borrar"] == [], "misma observación, misma cola: no se repite ni se borra")
    # el dueño descarta una; otra deja de ser cierta
    idv = next(i for i, d in docs.items() if d["clase"] == "estado-desfasado")
    escribir(cola / f"{idv}.json", json.dumps({"id": idv, "data": {**docs[idv], "estado": "descartada"}, "version": 4}))
    b3, d3 = correr(raiz, tmp / "s3", cola)
    ok(b3["anadir"] == [] and b3["borrar"] == [], "lo descartado no vuelve a proponerse mientras siga siendo cierto")
    t = raiz / "ventas/viejo/proyecto.md"; t.write_text(t.read_text().replace("2026-09-01", "2026-10-23"), encoding="utf-8")
    b4, d4 = correr(raiz, tmp / "s4", cola)
    ok([x["id"] for x in b4["borrar"]] == [idv] and b4["borrar"][0]["if_version"] == 4, "cuando ya no es cierto (el dueño puso al día) se borra, con la versión leída, también lo descartado")
    ok(all(x["id"] != "nota1" for x in b4["borrar"]), "lo que no es una propuesta no se toca")
    # un proyecto que no viene en la copia conserva sus propuestas
    escribir(cola / "prop-estado-desfasado-ajeno.json", json.dumps({"id": "prop-estado-desfasado-ajeno", "version": 1, "data": {"tipo": "propuesta", "clase": "estado-desfasado", "proyecto": "otra--cosa", "texto": "x", "estado": "pendiente"}}))
    b5, _ = correr(raiz, tmp / "s5", cola)
    ok(all(x["id"] != "prop-estado-desfasado-ajeno" for x in b5["borrar"]), "una propuesta de un proyecto que no está en la copia se deja como está")
    r = subprocess.run([sys.executable, str(BARRIDO), "--cola-pendiente", str(cola)], capture_output=True, text=True)
    ok(r.stdout.strip() == "1", f"--cola-pendiente cuenta lo que no es propuesta (dijo {r.stdout.strip()!r})")

    # sin --hoy: el día de la zona de la organización que dejó el generador en meta/estado.json
    sh = tmp / "sh"; (sh / "meta").mkdir(parents=True); escribir(sh / "meta/estado.json", '{"snapshot": "2026-10-23"}')
    r = subprocess.run([sys.executable, str(BARRIDO), str(raiz), str(sh)], capture_output=True, text=True)
    ok(r.returncode == 0 and json.loads((sh / "barrido.json").read_text())["para_juicio"][0]["fecha"] == "2026-10-22", "sin --hoy toma el snapshot de meta/estado.json")

    print("lo que el modelo juzga")
    sj = tmp / "sj"; sj.mkdir()
    correr(raiz, sj)
    escribir(tmp / "juicio.json", json.dumps([
        {"proyecto": "ventas--decidimos", "fecha": "2026-10-22", "decision": "Cobrar el piloto en dos pagos\ncon salto"},
        {"proyecto": "ventas--limpio", "fecha": "2026-10-20", "decision": "algo que el barrido no pidió juzgar"},
        {"proyecto": "ventas--decidimos", "fecha": "2026-10-01", "decision": "otra fecha que no se pidió"},
        {"proyecto": "ventas--decidimos", "fecha": "2026-10-22", "decision": ""}]))
    r = subprocess.run([sys.executable, str(BARRIDO), "--sumar-juicio", str(sj), str(tmp / "juicio.json")], capture_output=True, text=True)
    bj = json.loads((sj / "barrido.json").read_text(encoding="utf-8"))
    nuevas = [x for x in bj["anadir"] if x["id"].startswith("prop-decision-sin-registrar-")]
    ok(json.loads(r.stdout)["propuestas_nuevas_por_juicio"] == 1 and len(nuevas) == 1, "solo entra lo que el barrido pidió juzgar (mismo proyecto y fecha) y con texto")
    dj = json.loads((sj / nuevas[0]["archivo"]).read_text(encoding="utf-8"))
    ok(dj["clase"] == "decision-sin-registrar" and "\n" not in dj["texto"] and "2026-10-22" in dj["texto"], "la propuesta nombra la fecha y va en una sola línea")
    r = subprocess.run([sys.executable, str(BARRIDO), "--sumar-juicio", str(sj), str(tmp / "juicio.json")], capture_output=True, text=True)
    ok(json.loads(r.stdout)["propuestas_nuevas_por_juicio"] == 0, "repetirlo no duplica")

    print("aplicar_cambios.py y las propuestas")
    guia = raiz / "guia.md"
    escribir(guia, "# Org\n\n## Áreas\n\n| Área | Qué es | Dueño | Cuenta | Quién la lee |\n|---|---|---|---|---|\n| `ventas/` | v | Ana | ana@ejemplo.test | Todo el equipo |\n\n## Quién responde por qué\n")
    lista = [{"id": i, "tipo": "propuesta", "proyecto": d["proyecto"], "clase": d["clase"], "texto": d["texto"], "por_que": d["por_que"], "origen": "barrido", "estado": "pendiente"} for i, d in docs.items()]
    lista.append({"id": "mala", "tipo": "propuesta", "proyecto": "../x", "texto": "x"})
    lista.append({"id": "multi", "tipo": "propuesta", "proyecto": "ventas--viejo", "texto": "a\nb"})
    escribir(tmp / "q.json", json.dumps(lista))
    r = subprocess.run([sys.executable, str(APLICAR), str(raiz), str(tmp / "q.json"), "--cuenta", "ana@ejemplo.test", "--dry-run"], capture_output=True, text=True)
    rep = json.loads(r.stdout)
    ok(not any(x["id"].startswith("prop-") for x in rep["sin_match"]), "una propuesta no sale como «tipo desconocido»")
    ok(sorted(rep.get("propuestas", [])) == sorted(i for i in docs), "aplicar_cambios.py las reporta aparte, retenidas, sin aplicarlas")
    ok({x["id"] for x in rep["rechazados"]} == {"mala", "multi"}, "una propuesta con id de proyecto malo o con saltos de línea se rechaza")
    r2 = subprocess.run([sys.executable, str(APLICAR), str(raiz), str(tmp / "q.json"), "--cuenta", "otra@ejemplo.test", "--dry-run"], capture_output=True, text=True)
    rep2 = json.loads(r2.stdout)
    ok(len(rep2["para_su_dueno"]) >= len(docs) and all(x["id"].startswith("prop-") for x in rep2["para_su_dueno"] if x["id"] not in ("mala", "multi")) and not rep2.get("propuestas"), "la cuenta de otra área no las toca: esperan a su dueño")

    print("plan_subida.py sube las propuestas")
    PLAN = TABLERO / "plan_subida.py"
    sal = tmp / "salida"; (sal / "meta").mkdir(parents=True)
    escribir(sal / "meta/estado.json", '{"x":1}')
    escribir(sal / "indice.json", json.dumps([{"coleccion": "meta", "doc_id": "estado", "archivo": "meta/estado.json", "bytes": 7, "huella": "h"}]))
    # la raíz con el proyecto «viejo» al día: la propuesta que estaba en la cola ya no vale
    cola2 = tmp / "cola2"; cola2.mkdir()
    escribir(cola2 / f"{idv}.json", json.dumps({"id": idv, "data": docs[idv], "version": 7}))
    r = subprocess.run([sys.executable, str(BARRIDO), str(raiz), str(sal), "--cola", str(cola2), "--hoy", "2026-10-23"], capture_output=True, text=True)
    r = subprocess.run([sys.executable, str(PLAN), str(sal), str(tmp / "volcado")], capture_output=True, text=True)
    plan = json.loads(r.stdout)
    ops = [e for lote in plan["lotes"] for e in lote]
    sets = [e for e in ops if e["op"] == "set" and e["collection"] == "cambios"]
    dels = [e for e in ops if e["op"] == "delete" and e["collection"] == "cambios"]
    ok(len(sets) == len(docs) - 1 and all(e["doc_id"].startswith("prop-") and not e["existe"] and pathlib.Path(e["file_path"]).exists() for e in sets), "las propuestas nuevas van como «set» en «cambios», con su archivo")
    ok(dels == [{"op": "delete", "collection": "cambios", "doc_id": idv, "if_version": 7}], "la que ya no vale va como «delete» con la versión leída")
    ok(ops[-1]["collection"] == "meta" and ops[-1]["doc_id"] == "estado", "meta/estado sigue yendo la última")
    ok(plan["propuestas"] == {"nuevas": len(docs) - 1, "retiradas": 1}, "el plan cuenta las propuestas")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n" + ("Todo bien." if not fallos else f"{len(fallos)} fallo(s)."))
sys.exit(1 if fallos else 0)
