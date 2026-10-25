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

    for n, cab, cuerpo in [("sin.md", "estado: vigente", "# Tope de compras\n\nEl tope deja fuera lo recurrente."),
                           ("con.md", 'estado: vigente\nafirma: "Ya lo dice."', "# Con\n\nTexto."),
                           ("viejo.md", "estado: reemplazado", "# Viejo\n\nTexto."),
                           ("borrador.md", "estado: borrador", "# Borrador\n\nTexto.")]:
        escribir(raiz / "ventas/limpio/entregables" / n, f"---\n{cab}\nactualizado: 2026-10-01\n---\n{cuerpo}\n")
    salida = tmp / "s1"; salida.mkdir()
    b, docs = correr(raiz, salida)
    por = lambda clase: sorted(d["proyecto"] for d in docs.values() if d["clase"] == clase)
    print("detectores")
    ok(por("estado-desfasado") == ["ventas--viejo"], f"estado desfasado: solo el proyecto cuya cabecera es más vieja que su última sesión real (hay {por('estado-desfasado')})")
    ok("ventas--tarea" not in por("estado-desfasado"), "una entrada «(tarea)» no cuenta como sesión")
    ok("ventas--cerrado" not in por("estado-desfasado"), "un proyecto terminado no se propone")
    ok(por("paso-hecho") == ["ventas--hecho"] and len([d for d in docs.values() if d["clase"] == "paso-hecho"]) == 1, "paso hecho: solo el paso que la sesión cuenta, no el otro ni los de otros proyectos")
    ok(por("rotacion") == ["ventas--anios"], "rotación: un registro que mezcla años")
    # una frase que comparte las palabras del paso pero lo niega no lo da por hecho; fechar el paso no cambia el id
    proyecto(raiz, "ventas", "niega", "2026-10-20", ["Mandar la encuesta de satisfacción al equipo"], sesion("2026-10-20", "la encuesta", "Revisamos el borrador de la encuesta de satisfacción con el equipo; falta mandarla."))
    b2, docs2 = correr(raiz, tmp / "s1b")
    ok("ventas--niega" not in [d["proyecto"] for d in docs2.values() if d["clase"] == "paso-hecho"], "«falta mandarla» no da el paso por hecho")
    id_antes = next(i for i, d in docs2.items() if d["clase"] == "paso-hecho" and d["proyecto"] == "ventas--hecho")
    tp_ = raiz / "ventas/hecho/proyecto.md"; tx_ = tp_.read_text(encoding="utf-8")
    tp_.write_text(tx_.replace("- Mandar la propuesta de una página a Cliente Uno", "- 2026-11-05: Mandar la propuesta de una página a Cliente Uno"), encoding="utf-8")
    b3, docs3 = correr(raiz, tmp / "s1c")
    ok(id_antes in docs3, "el mismo paso con fecha delante da el mismo id: fecharlo desde el tablero no resucita una propuesta descartada")
    tp_.write_text(tx_, encoding="utf-8"); shutil.rmtree(raiz / "ventas/niega")
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

    print("afirma")
    pa = [x["ruta"] for x in bj["para_afirma"]]
    ok(pa == ["ventas/limpio/entregables/sin.md", "ventas/limpio/entregables/borrador.md"], f"pide afirma solo de lo que no la tiene y no está reemplazado, vigentes primero ({pa})")
    escribir(tmp / "juicio2.json", json.dumps({"afirma": [
        {"ruta": "ventas/limpio/entregables/sin.md", "afirma": 'El tope deja fuera "lo recurrente".'},
        {"ruta": "ventas/limpio/entregables/con.md", "afirma": "no se pidió"}]}))
    r = subprocess.run([sys.executable, str(BARRIDO), "--sumar-juicio", str(sj), str(tmp / "juicio2.json")], capture_output=True, text=True)
    bj = json.loads((sj / "barrido.json").read_text(encoding="utf-8"))
    af = [x for x in bj["anadir"] if x["id"].startswith("prop-afirma-")]
    ok(json.loads(r.stdout)["propuestas_afirma"] == 1 and len(af) == 1, "solo entra el afirma que se pidió")
    da = json.loads((sj / af[0]["archivo"]).read_text(encoding="utf-8"))
    ok(da["clase"] == "afirma" and da["ruta"].endswith("sin.md") and '"' not in da["afirma"] and "\n" not in da["texto"], "la propuesta lleva ruta y línea, sin comillas dobles")
    ok(json.loads(subprocess.run([sys.executable, str(BARRIDO), "--sumar-juicio", str(sj), str(tmp / "juicio2.json")], capture_output=True, text=True).stdout)["propuestas_afirma"] == 0, "repetirlo no duplica")
    # con la propuesta ya en la cola, no se vuelve a pedir
    (tmp / "cola3").mkdir()
    escribir(tmp / "cola3" / f"{af[0]['id']}.json", json.dumps({"id": af[0]["id"], "data": da, "version": 1}))
    s3 = tmp / "s3afirma"; s3.mkdir()
    r = subprocess.run([sys.executable, str(BARRIDO), str(raiz), str(s3), "--cola", str(tmp / "cola3"), "--hoy", "2026-10-23"], capture_output=True, text=True)
    ok([x["ruta"] for x in json.loads((s3 / "barrido.json").read_text())["para_afirma"]] == ["ventas/limpio/entregables/borrador.md"], "lo ya propuesto no se vuelve a pedir")

    print("taller, candidatos y contradicciones")
    sc = tmp / "sc"; (sc / "detalle").mkdir(parents=True)
    escribir(sc / "detalle/ventas--limpio.json", json.dumps({"que_hay": {"piezas": [
        {"tipo": "entregable", "archivo": "con.md", "estado": "vigente", "afirma": "Ya lo dice."},
        {"tipo": "taller", "archivo": "nota-a.md", "estado": "borrador", "titulo": "Nota A", "afirma": "El tope deja fuera lo recurrente."},
        {"tipo": "taller", "archivo": "nota-b.md", "estado": "borrador", "titulo": "Nota B", "afirma": "El tope incluye lo recurrente."},
        {"tipo": "taller", "archivo": "sin-afirma.md", "estado": "borrador", "titulo": "Sin afirma"},
        {"tipo": "taller", "archivo": "vieja.md", "estado": "reemplazado", "titulo": "Vieja"},
        {"tipo": "taller", "archivo": "hoja.xlsx", "estado": None}]}}))
    r = subprocess.run([sys.executable, str(BARRIDO), str(raiz), str(sc), "--hoy", "2026-10-23"], capture_output=True, text=True)
    bc = json.loads((sc / "barrido.json").read_text(encoding="utf-8"))
    pa = [x["ruta"] for x in bc["para_afirma"]]
    ok(pa[-1] == "ventas/limpio/taller/sin-afirma.md" and pa[0].startswith("ventas/limpio/entregables/") and "leer_en_computadora" not in bc["para_afirma"][-1] and bc["para_afirma"][-1]["arranque"] is None and bc["para_afirma"][-1]["titulo"] == "Sin afirma", f"pide afirma del taller después de los entregables, solo con título y cabecera, nunca su cuerpo ({pa})")
    # con --cuenta, solo las áreas de la cuenta (y los proyectos ajenos que la nombran en «Colabora:»)
    raiz2 = tmp / "raiz-cuenta"; shutil.copytree(raiz, raiz2)
    guia_ = raiz2 / "guia.md"
    escribir(guia_, "# Prueba · guía\n\n## Áreas\n\n| Área | Qué | Dueño | Cuenta | Quién la lee |\n|---|---|---|---|---|\n| `ventas/` | v | Ana | ana@ejemplo.test · colabora: carla@ejemplo.test | Todo el equipo |\n| `otra/` | o | Beto | beto@ejemplo.test | Todo el equipo |\n")
    proyecto(raiz2, "otra", "cosa", "2026-09-01", ["Llamar"], sesion("2026-10-10", "x", "Se habló."))
    so = tmp / "so"; so.mkdir()
    r = subprocess.run([sys.executable, str(BARRIDO), str(raiz2), str(so), "--hoy", "2026-10-23", "--cuenta", "ana@ejemplo.test"], capture_output=True, text=True)
    vistos_ = json.loads((so / "barrido.json").read_text())["proyectos"]
    ok(vistos_ and all(v.startswith("ventas--") for v in vistos_), f"con --cuenta no barre las áreas de otra cuenta ({[v for v in vistos_ if not v.startswith('ventas--')]})")
    r = subprocess.run([sys.executable, str(BARRIDO), str(raiz2), str(tmp / "so2"), "--hoy", "2026-10-23", "--cuenta", "carla@ejemplo.test"], capture_output=True, text=True)
    ok("ventas--viejo" in json.loads((tmp / "so2" / "barrido.json").read_text())["proyectos"], "quien colabora en el área también barre")
    r = subprocess.run([sys.executable, str(BARRIDO), str(raiz2), str(tmp / "so3"), "--hoy", "2026-10-23"], capture_output=True, text=True)
    ok("otra--cosa" in json.loads((tmp / "so3" / "barrido.json").read_text())["proyectos"], "sin --cuenta barre todo (las pruebas y el montaje)")
    ok(len(bc["para_contraste"]) == 1 and bc["para_contraste"][0]["proyecto"] == "ventas--limpio" and {x["ruta"] for x in bc["para_contraste"][0]["piezas"]} == {"ventas/limpio/entregables/con.md", "ventas/limpio/taller/nota-a.md", "ventas/limpio/taller/nota-b.md"}, "pone a contraste solo las piezas con afirma, del proyecto que tiene dos o más")
    escribir(tmp / "juicio3.json", json.dumps({
        "candidatos": [{"proyecto": "ventas--limpio", "rutas": ["ventas/limpio/taller/nota-a.md", "ventas/limpio/taller/nota-b.md"], "entregable": "Una política de compras recurrentes"},
                       {"proyecto": "ventas--limpio", "rutas": ["ventas/limpio/taller/nota-a.md"], "entregable": "una sola pieza no vale"},
                       {"proyecto": "ventas--limpio", "rutas": ["ventas/limpio/taller/nota-a.md", "ventas/limpio/taller/otra.md"], "entregable": "una ruta que no se puso delante"}],
        "contradicciones": [{"proyecto": "ventas--limpio", "rutas": ["ventas/limpio/taller/nota-b.md", "ventas/limpio/taller/nota-a.md"], "texto": "Una incluye lo recurrente y la otra lo deja fuera"},
                            {"proyecto": "ventas--hecho", "rutas": ["a", "b"], "texto": "proyecto que no se pidió"}]}))
    r = subprocess.run([sys.executable, str(BARRIDO), "--sumar-juicio", str(sc), str(tmp / "juicio3.json")], capture_output=True, text=True)
    res = json.loads(r.stdout)
    bc = json.loads((sc / "barrido.json").read_text(encoding="utf-8"))
    nuevas = {x["id"]: json.loads((sc / x["archivo"]).read_text(encoding="utf-8")) for x in bc["anadir"] if x["id"].startswith(("prop-candidato-entregable-", "prop-contradiccion-"))}
    ok(res["propuestas_candidatos"] == 1 and res["propuestas_contradicciones"] == 1 and len(nuevas) == 2, f"solo entran el candidato y la contradicción con dos o más piezas puestas delante ({res})")
    ok(all(d["rutas"] == ["ventas/limpio/taller/nota-a.md", "ventas/limpio/taller/nota-b.md"] and "\n" not in d["texto"] and "nota-a.md" in d["texto"] for d in nuevas.values()), "la propuesta lleva las rutas ordenadas y las nombra en el texto")
    # siguen valiendo mientras existan las piezas; si una desaparece, se retiran
    cola4 = tmp / "cola4"; cola4.mkdir()
    for i, (k, d) in enumerate(nuevas.items()):
        escribir(cola4 / f"{k}.json", json.dumps({"id": k, "data": d, "version": 10 + i}))
    s4 = tmp / "s4"; shutil.copytree(sc / "detalle", s4 / "detalle")
    r = subprocess.run([sys.executable, str(BARRIDO), str(raiz), str(s4), "--cola", str(cola4), "--hoy", "2026-10-23"], capture_output=True, text=True)
    ok(json.loads((s4 / "barrido.json").read_text())["borrar"] == [], "con las piezas en su sitio, el candidato y la contradicción siguen en la cola")
    det = json.loads((s4 / "detalle/ventas--limpio.json").read_text()); det["que_hay"]["piezas"] = [x for x in det["que_hay"]["piezas"] if x["archivo"] != "nota-b.md"]
    escribir(s4 / "detalle/ventas--limpio.json", json.dumps(det))
    r = subprocess.run([sys.executable, str(BARRIDO), str(raiz), str(s4), "--cola", str(cola4), "--hoy", "2026-10-23"], capture_output=True, text=True)
    ok(sorted(x["id"] for x in json.loads((s4 / "barrido.json").read_text())["borrar"]) == sorted(nuevas), "si una de las piezas desaparece, se retiran")

    print("sin inventario del taller, lo que nombra el taller no se toca; creado va en la zona de la organización")
    sn = tmp / "sn"; sn.mkdir()      # sin detalle: como una puesta al día sin consola
    r = subprocess.run([sys.executable, str(BARRIDO), str(raiz), str(sn), "--cola", str(cola4), "--hoy", "2026-10-23"], capture_output=True, text=True)
    ok(json.loads((sn / "barrido.json").read_text())["borrar"] == [], "sin piezas del taller en el detalle, el candidato y la contradicción del taller se quedan en la cola")
    (sn / "meta").mkdir(); escribir(sn / "meta/estado.json", json.dumps({"snapshot": "2026-10-23", "zona": "America/Mexico_City"}))
    r = subprocess.run([sys.executable, str(BARRIDO), str(raiz), str(sn), "--hoy", "2026-10-23"], capture_output=True, text=True)
    creados = [json.loads(p.read_text())["creado"] for p in (sn / "cambios").glob("*.json")]
    ok(creados and all(c.endswith(("-06:00", "-05:00")) for c in creados), f"creado lleva la zona de la organización, no la del contenedor ({creados[:1]})")
    # una decisión registrada al día siguiente de la sesión cuenta como registrada; un proyecto terminado no pide afirma
    proyecto(raiz, "ventas", "medianoche", "2026-10-22", ["Esperar"], sesion("2026-10-21", "el precio", "Decidimos cobrar en dos pagos."), decisiones="## 2026-10-22 · Dos pagos\nDecidió: Ana\nPor qué: x\n")
    escribir(raiz / "ventas/cerrado/entregables/viejo.md", "---\nestado: vigente\nactualizado: 2026-08-01\n---\n# Viejo\n\nCuerpo.\n")
    b4, _ = correr(raiz, tmp / "s4m")
    ok("ventas--medianoche" not in [j["proyecto"] for j in b4["para_juicio"]], "una decisión registrada al día siguiente de la sesión no va a juicio")
    ok(not any(x["ruta"].startswith("ventas/cerrado/") for x in b4["para_afirma"]), "un proyecto terminado no pide afirma")
    shutil.rmtree(raiz / "ventas/medianoche"); (raiz / "ventas/cerrado/entregables/viejo.md").unlink()

    print("lo juzgado no se vuelve a pedir")
    sj2 = tmp / "sj2"; shutil.copytree(sc / "detalle", sj2 / "detalle")
    r = subprocess.run([sys.executable, str(BARRIDO), str(raiz), str(sj2), "--hoy", "2026-10-23"], capture_output=True, text=True)
    b0 = json.loads((sj2 / "barrido.json").read_text())
    ok(b0["para_juicio"] and b0["para_afirma"] and b0["para_contraste"], "antes de juzgar se pide todo")
    escribir(tmp / "vacio.json", json.dumps({"decisiones": [], "afirma": [{"ruta": b0["para_afirma"][0]["ruta"], "afirma": "Escríbele a juan.perez@ejemplo.test o al RFC PEJJ800101AB1."}], "candidatos": [], "contradicciones": []}))
    r = subprocess.run([sys.executable, str(BARRIDO), "--sumar-juicio", str(sj2), str(tmp / "vacio.json")], capture_output=True, text=True)
    bj2 = json.loads((sj2 / "barrido.json").read_text())
    ok(json.loads(r.stdout)["propuestas_afirma"] == 0 and not any(x["id"].startswith("prop-afirma-") for x in bj2["anadir"]), "una línea afirma con un correo o un RFC no entra en la cola")
    ok(len(bj2["juzgado"]["ids"]) == len(b0["para_juicio"]) + len(b0["para_afirma"]) and len(bj2["juzgado"]["contraste"]) == len(b0["para_contraste"]), "todo lo que se puso delante del modelo queda apuntado como juzgado")
    # plan_subida lo lleva a meta/estado, y el barrido siguiente lo lee de la base
    (sj2 / "meta").mkdir(); escribir(sj2 / "meta/estado.json", '{"zona": "America/Mexico_City"}')
    escribir(sj2 / "indice.json", json.dumps([{"coleccion": "meta", "doc_id": "estado", "archivo": "meta/estado.json", "bytes": 7, "huella": "h"}]))
    base_j = tmp / "base-j"; (base_j / "meta").mkdir(parents=True); escribir(base_j / "meta/estado.json", json.dumps({"data": {"juzgado": {"ids": ["prop-viejo-1"], "contraste": []}}, "version": 2}))
    r = subprocess.run([sys.executable, str(TABLERO / "plan_subida.py"), str(sj2), str(base_j)], capture_output=True, text=True)
    meta_j = json.loads((sj2 / "meta/estado.json").read_text())["juzgado"]
    ok("prop-viejo-1" in meta_j["ids"] and set(bj2["juzgado"]["ids"]) <= set(meta_j["ids"]) and meta_j["contraste"] == bj2["juzgado"]["contraste"], "plan_subida suma lo juzgado a lo que ya tenía la base en meta/estado")
    base_j2 = tmp / "base-j2"; (base_j2 / "meta").mkdir(parents=True); escribir(base_j2 / "meta/estado.json", json.dumps({"data": {"juzgado": meta_j}, "version": 3}))
    sj3 = tmp / "sj3"; shutil.copytree(sc / "detalle", sj3 / "detalle")
    r = subprocess.run([sys.executable, str(BARRIDO), str(raiz), str(sj3), "--hoy", "2026-10-23", "--base", str(base_j2)], capture_output=True, text=True)
    b3 = json.loads((sj3 / "barrido.json").read_text())
    ok(not b3["para_juicio"] and not b3["para_afirma"] and not b3["para_contraste"], f"con la base, nada de lo juzgado se vuelve a pedir ({len(b3['para_juicio'])}, {len(b3['para_afirma'])}, {len(b3['para_contraste'])})")

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
    ok(not rep2["para_su_dueno"] and set(rep2["propuestas"]) == {i for i in docs if i not in ("mala", "multi")}, "con la cuenta de otra área tampoco se aplican ni esperan a nadie: se cuentan aparte, como propuestas")

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

    print("la cola con tope y caducidad (1.22.1)")
    rz = tmp / "raiz-tope"
    # un proyecto con nueve pasos que la sesión da por hechos: nueve propuestas posibles, entran ocho
    pasos9 = [f"Revisar el contrato con {n} esta semana" for n in ("Acmetec", "Bodegas", "Cartones", "Dulceria", "Empaques", "Farmacos", "Grafica", "Herrajes", "Imprenta")]
    proyecto(rz, "ventas", "lleno", "2026-10-20", pasos9, sesion("2026-10-20", "contratos", ". ".join(f"Se revisó el contrato con {n} esta semana" for n in ("Acmetec", "Bodegas", "Cartones", "Dulceria", "Empaques", "Farmacos", "Grafica", "Herrajes", "Imprenta")) + "."))
    st = tmp / "st"; st.mkdir()
    bt, dt = correr(rz, st)
    ok(len(dt) == 8, f"como mucho ocho pendientes por proyecto ({len(dt)})")
    # la cola trae una pendiente de hace 70 días y otra descartada igual de vieja
    colt = tmp / "colat"; colt.mkdir()
    vieja = next(iter(dt)); dv = dict(dt[vieja], creado="2026-08-10T10:00-06:00")
    escribir(colt / f"{vieja}.json", json.dumps({"id": vieja, "data": dv, "version": 3}))
    escribir(colt / "prop-x-aceptada.json", json.dumps({"id": "prop-x-aceptada", "data": {"tipo": "propuesta", "clase": "afirma", "proyecto": "ventas--lleno", "ruta": "ventas/lleno/entregables/z.md", "estado": "aceptada", "creado": "2026-07-01T10:00-06:00"}, "version": 1}))
    escribir(colt / "prop-x-descartada.json", json.dumps({"id": "prop-x-descartada", "data": {"tipo": "propuesta", "clase": "rotacion", "proyecto": "ventas--lleno", "estado": "descartada", "creado": "2026-08-01T10:00-06:00"}, "version": 1}))
    st2 = tmp / "st2"; st2.mkdir()
    bt2, dt2 = correr(rz, st2, colt)
    ok(vieja in {x["id"] for x in bt2["borrar"]} and "prop-x-descartada" not in bt2["juzgado"]["ids"], "la pendiente de hace más de 60 días se retira; una descartada no caduca")
    ok(vieja in bt2["juzgado"]["ids"] and vieja not in dt2, "y queda juzgada: no vuelve igual en la misma corrida")
    ok("prop-x-aceptada" not in bt2["juzgado"]["ids"], "una aceptada desde el tablero no caduca: la espera el próximo cierre (1.22.3)")
    vol = tmp / "volt"; (vol / "meta").mkdir(parents=True)
    escribir(vol / "meta/estado.json", json.dumps({"juzgado": bt2["juzgado"]}))
    st3 = tmp / "st3"; st3.mkdir()
    r = subprocess.run([sys.executable, str(BARRIDO), str(rz), str(st3), "--hoy", "2026-10-23", "--base", str(vol)], capture_output=True, text=True)
    d3 = {q.stem for q in (st3 / "cambios").glob("*.json")}
    ok(r.returncode == 0 and vieja not in d3 and len(d3) == 8, f"ni en la siguiente, y su hueco lo ocupa la novena ({len(d3)})")

    # una pendiente vieja de un proyecto sin sesión después no caduca: nadie la ha podido ver
    proyecto(rz, "ventas", "quieto", "2026-07-01", ["Llamar a Luis por el contrato"], sesion("2026-07-01", "x", "Se llamó a Luis por el contrato."))
    colq = tmp / "colaq"; colq.mkdir()
    escribir(colq / "prop-q.json", json.dumps({"id": "prop-q", "data": {"tipo": "propuesta", "clase": "rotacion", "proyecto": "ventas--quieto", "estado": "pendiente", "creado": "2026-07-02T10:00-06:00"}, "version": 1}))
    sq = tmp / "sq"; sq.mkdir()
    bq, _ = correr(rz, sq, colq)
    ok("prop-q" not in bq["juzgado"]["ids"], "una pendiente vieja de un proyecto sin sesión posterior no caduca")
    # con el proyecto al tope, una decisión sin registrar entra igual; una línea aportacion, no
    jl = tmp / "juicio-lleno.json"
    bl = json.loads((st / "barrido.json").read_text(encoding="utf-8"))
    bl["para_juicio"] = [{"proyecto": "ventas--lleno", "fecha": "2026-10-20", "extracto": "x"}]
    bl["para_afirma"] = [{"proyecto": "ventas--lleno", "ruta": "ventas/lleno/entregables/x.md", "titulo": "x", "arranque": "x"}]
    (st / "barrido.json").write_text(json.dumps(bl), encoding="utf-8")
    jl.write_text(json.dumps({"decisiones": [{"proyecto": "ventas--lleno", "fecha": "2026-10-20", "decision": "Se cobra en dos pagos."}],
                              "afirma": [{"ruta": "ventas/lleno/entregables/x.md", "afirma": "Dice algo."}]}), encoding="utf-8")
    r = subprocess.run([sys.executable, str(BARRIDO), "--sumar-juicio", str(st), str(jl)], capture_output=True, text=True)
    rj = json.loads(r.stdout)
    ok(rj["propuestas_nuevas_por_juicio"] == 1 and rj["propuestas_afirma"] == 1 and rj["sin_hueco"] == 0, f"con lo mecánico al tope, la decisión entra y la aportacion también, que lleva su propio tope (1.22.3) ({rj})")
    bl = json.loads((st / "barrido.json").read_text(encoding="utf-8"))
    bl["pendientes"] = {**(bl.get("pendientes") or {}), "ventas--lleno|afirma": 30}
    bl["para_afirma"] = [{"proyecto": "ventas--lleno", "ruta": "ventas/lleno/entregables/y.md", "titulo": "y", "arranque": "y"}]
    (st / "barrido.json").write_text(json.dumps(bl), encoding="utf-8")
    jl.write_text(json.dumps({"afirma": [{"ruta": "ventas/lleno/entregables/y.md", "afirma": "Dice otra cosa."}]}), encoding="utf-8")
    r = subprocess.run([sys.executable, str(BARRIDO), "--sumar-juicio", str(st), str(jl)], capture_output=True, text=True)
    rj = json.loads(r.stdout)
    ok(rj["propuestas_afirma"] == 0 and rj["sin_hueco"] == 1, f"con 30 aportaciones pendientes, la siguiente espera hueco ({rj})")

    print("el tope de afirma, primero para lo activo (1.22.1)")
    ra = tmp / "raiz-afirma"
    proyecto(ra, "aaa", "dormido", "2026-06-01", ["Nada"], sesion("2026-06-01", "x", "y"))
    proyecto(ra, "zzz", "activo", "2026-10-22", ["Nada"], sesion("2026-10-22", "x", "y"))
    for pr in ("aaa/dormido", "zzz/activo"):
        for k in range(5):
            escribir(ra / pr / "entregables" / f"e{k}.md", f"---\nestado: vigente\nactualizado: 2026-10-01\n---\n# Pieza {k}\n\nTexto.\n")
    sa = tmp / "sa"; sa.mkdir()
    ba, _ = correr(ra, sa)
    ok([x["proyecto"] for x in ba["para_afirma"]] == ["zzz--activo"] * 5 + ["aaa--dormido"] * 5, f"las cinco del proyecto con la sesión más reciente van antes que las del dormido, aunque este vaya antes por nombre ({[x['proyecto'] for x in ba['para_afirma']]})")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n" + ("Todo bien." if not fallos else f"{len(fallos)} fallo(s)."))
sys.exit(1 if fallos else 0)
