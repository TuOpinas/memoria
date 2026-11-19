#!/usr/bin/env python3
"""Prueba seguimiento.py (skill desarrollo, 1.27): la entrada del seguimiento, la auditoría y cómo escribe los estados de una
configuración, con un JSON de GitHub inventado (la forma de recoger_github.py) y un proyecto de prueba. Sin red.

Uso: python3 pruebas/sesion/probar_seguimiento.py
"""
import json, pathlib, re, shutil, subprocess, sys, tempfile

AQUI = pathlib.Path(globals().get("__file__", "pruebas/sesion/x")).resolve().parent
SKILL = AQUI.parent.parent / "plugins" / "memoria" / "skills" / "desarrollo"
SEG, PLANTILLAS = SKILL / "seguimiento.py", SKILL / "plantillas"
fallos = 0
HOY = "2026-11-18"


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t)
    fallos += 0 if c else 1


def correr(*a):
    if a and a[0] == "auditoria" and "--github" in a:
        # la auditoría lee el último mes: los JSON de prueba empiezan el 2026-11-01, y se le da desde hace 31 días
        g = pathlib.Path(str(a[a.index("--github") + 1])); d = json.loads(g.read_text(encoding="utf-8"))
        if d.get("desde") == "2026-11-01":
            d["desde"] = "2026-10-15"
            for r_ in d.get("repos", []):   # y la lista de commits llega a antes de esa fecha
                if r_.get("commits"):
                    r_["commits"] = r_["commits"] + [{"sha": "2" * 40, "parents": 0, "date": "2026-10-01T10:00:00Z", "message": "raíz", "author": "ana"}]
            g.write_text(json.dumps(d), encoding="utf-8")
    p = subprocess.run([sys.executable, str(SEG), *map(str, a)], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def raiz(seguimiento="por crear", paso="release de GitHub", construye="Ana Prueba (ana@ejemplo.test, @ana)"):
    r = pathlib.Path(tempfile.mkdtemp()) / "raiz"
    e = r / "ventas/app/entregables"
    e.mkdir(parents=True)
    (r / "guia.md").write_text("# Guía\n", encoding="utf-8")
    (r / "ventas/app/proyecto.md").write_text(f"""---
estado: vigente
actualizado: {HOY}
---

# App

## Quién participa
Responsable: Ana Prueba (ventas)

## Desarrollo
Repositorios: acme/app
Configuración de plataforma: ventas/app/entregables/plataforma.md
Configuración de repositorios: ventas/app/entregables/repositorios.md
Diseño: ventas/app/entregables/diseno.md
Plan: ventas/app/entregables/plan.md
Seguimiento: {seguimiento}
Paso a Prod: {paso}
Acepta: Ana Prueba (ana@ejemplo.test, @ana)
Audita: Beto Prueba (beto@ejemplo.test, @beto)
Construye: {construye}
Administra: Beto Prueba (beto@ejemplo.test, @beto)
""", encoding="utf-8")
    t = (PLANTILLAS / "diseno.md").read_text(encoding="utf-8")
    t = t.replace("| [nombre_en_codigo] | [Una frase] | [otra_entidad (1:N)] |", "| cliente | Quien compra | pedido (1:N) |\n| pedido | Una compra | |")
    t = t.replace("| [Nombre] | [Una frase] | [organización/repositorio:ruta] |", "| API | Atiende | acme/app:api |")
    t = t.replace("| [Palabra] | [Una frase] | [otra palabra, otra más] |", "| Pedido | Una compra | orden, order |")
    (e / "diseno.md").write_text(t, encoding="utf-8")
    t = (PLANTILLAS / "plan.md").read_text(encoding="utf-8")
    t = t.replace("| P01 · [nombre] | F1 | [Una frase] | [Lo que se comprueba antes de Prod] |",
                  "| P01 · Tablas | F1 | Tablas | Migradas |\n| P02 · API | F1 | La API | Responde |\n| P03 · Vista | F1 | La vista | Se ve |")
    (e / "plan.md").write_text(t, encoding="utf-8")
    shutil.copy(PLANTILLAS / "configuracion-plataforma.md", e / "plataforma.md")
    (e / "repositorios.md").write_text((PLANTILLAS / "configuracion-repositorios.md").read_text(encoding="utf-8").replace("[organización/repositorio]", "acme/app"), encoding="utf-8")
    return r


def c(sha, date, msg, parents=1):
    return {"sha": sha, "parents": parents, "date": date + "T10:00:00Z", "message": msg, "author": "ana"}


GH = {"leido": "gh", "hoy": HOY, "desde": "2026-11-01", "pedidos": ["acme/app"], "terminado": True, "repos": [{
    "repo": "acme/app", "rama": "main", "main_sha": "f" * 40,
    "pulls": [
        {"number": 1, "title": "P01 · tablas", "state": "merged", "author": "ana", "bot": False, "merge_commit": "a" * 40, "merged_at": "2026-11-02T10:00:00Z", "base": "main"},
        {"number": 2, "title": "P02 · api", "state": "merged", "author": "ana", "bot": False, "merge_commit": "c" * 40, "merged_at": "2026-11-10T10:00:00Z", "base": "main"},
        {"number": 3, "title": "P02 · arreglo", "state": "open", "author": "ana", "bot": False, "merge_commit": "", "merged_at": "", "base": "main"},
        {"number": 4, "title": "Arregla el README", "state": "merged", "author": "ana", "bot": False, "merge_commit": "d" * 40, "merged_at": "2026-11-12T10:00:00Z", "base": "main"},
        {"number": 5, "title": "Bump x", "state": "merged", "author": "dependabot[bot]", "bot": True, "merge_commit": "e" * 40, "merged_at": "2026-11-13T10:00:00Z", "base": "main"},
        {"number": 6, "title": "P03 · abandonado", "state": "closed", "author": "ana", "bot": False, "merge_commit": "", "merged_at": "", "base": "main"},
    ],
    "commits": [c("f" * 40, "2026-11-15", "directo a main"), c("e" * 40, "2026-11-13", "Bump x"),
                c("d" * 40, "2026-11-12", "Arregla el README", parents=2), c("c" * 40, "2026-11-10", "P02 · api"),
                c("b" * 40, "2026-11-05", "release"), c("a" * 40, "2026-11-02", "P01 · tablas"), c("1" * 40, "2026-10-25", "antes de la ventana")],
    "detalle": [
        {"sha": "f" * 40, "files": [{"filename": "migrations/001_init.sql", "status": "modified", "patch": "+ALTER TABLE x;"},
                                    {"filename": "CLAUDE.md", "status": "modified", "patch": "+regla"}]},
        {"sha": "c" * 40, "files": [{"filename": "api/pedidos.py", "status": "added", "patch": "+def crear_orden(order_id):\n+    pass"},
                                    {"filename": "worker/cola.py", "status": "added", "patch": "+x = 1"},
                                    {"filename": "migrations/002_facturas.sql", "status": "added",
                                     "patch": "+CREATE TABLE facturas (id int);\n+create table if not exists public.\"pedidos\" (id int);"}]},
        {"sha": "e" * 40, "files": []}, {"sha": "d" * 40, "files": []}, {"sha": "b" * 40, "files": []}, {"sha": "a" * 40, "files": []},
    ],
    "releases": [{"tag": "v2", "sha": "c" * 40, "draft": False, "published_at": "2026-11-11T10:00:00Z", "body": "Cambios", "author": "beto"},
                 {"tag": "v1", "sha": "a" * 40, "draft": False, "published_at": "2026-11-03T10:00:00Z",
                  "body": "Aprobó: Ana Prueba, 2026-11-03 · seguimiento 2026-11-03", "author": "beto"}],
    "tags": [{"name": "v2", "sha": "c" * 40}, {"name": "v1", "sha": "a" * 40}],
    "auditoria": {"repo": {"private": True, "allow_squash_merge": True, "allow_merge_commit": False, "allow_rebase_merge": False,
                           "default_branch": "main", "security_and_analysis": {"secret_scanning_push_protection": {"status": "enabled"}}},
                  "proteccion": {"required_status_checks": {"contexts": ["pruebas", "secretos"]}, "enforce_admins": {"enabled": False},
                                 "required_pull_request_reviews": None},
                  "rulesets": [{"name": "main", "enforcement": "active", "target": "branch", "bypass_actors": [],
                                "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"]}},
                                "rules": [{"type": "pull_request", "parameters": {"allowed_merge_methods": ["squash"]}}]}],
                  "org": None, "admins": None, "errores": {"org": "HTTP 403", "admins": "HTTP 403"}}}]}


def gh_json(d, completa=True):
    if completa:   # lo que escribe recoger_github.py al terminar
        d = dict(d, terminado=d.get("terminado", True), pedidos=d.get("pedidos", [r["repo"] for r in d.get("repos", [])]), hoy=d.get("hoy", HOY), desde=d.get("desde", "2026-11-01"))
    p = pathlib.Path(tempfile.mkdtemp()) / "gh.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    return p


def vista(a):
    """La auditoría solo propone (#2026-11-19-2): {fila: {columna: fila con «estado»}} de lo que trae propuesta, y la
    lista de lo que no, con «porque»."""
    co, pr = {}, []
    for x in a["filas"]:
        x = dict(x, estado=x["propuesta"], porque=x["evidencia"])
        if x["propuesta"]:
            co.setdefault(x["fila"], {})[x["columna"]] = x
        else:
            pr.append(x)
    return dict(a, comprobado=co, preguntar=pr)

print("El seguimiento")
r = raiz()
g = gh_json(GH)
rc, o, e = correr("seguimiento", r, "ventas/app", "--github", g, "--pidio", "Beto Prueba", "--fecha", HOY)
ok(rc == 0, "corre" + ("" if rc == 0 else ": " + e))
ok(o.startswith(f"## {HOY} · pidió Beto Prueba\nLeído: acme/app en `fffffff` (main), desde el 2026-11-01."), "cabecera con quién, el commit leído y desde cuándo")
ok("Comparó: piezas, diseño, reglas." in o, "dice qué pudo comparar")
ok("Paso a Prod: release de GitHub" in o, "dice qué forma de «Paso a Prod» entendió")
ok("| P01 · Tablas | F1 | unida | acme/app#1 |" in o and "cita el seguimiento del 2026-11-03, que no está en el archivo" in o,
   "con «por crear» no hay seguimientos: un sí que cita uno no entrega P01, y se dice")
ok("| P02 · API | F1 | en curso | acme/app#2, acme/app#3 |" in o, "P02 con un arreglo abierto: en curso (manda el menos avanzado)")
ok("| P03 · Vista | F1 | pendiente | — |" in o, "P03 con un pull request cerrado sin unir: pendiente")
ok("acme/app#4 «Arregla el README»" in o and "#5" not in o.split("**Fuera del plan:**")[1].split("\n")[0], "fuera del plan, sin los bots")
ok("la tabla «facturas»" in o and "«pedidos»" not in o, "una tabla nueva que no está en Datos (el plural de una entidad sí cuenta)")
ok("código nuevo en acme/app:worker" in o and "código nuevo en acme/app:api" not in o and "código nuevo en acme/app:migrations" not in o,
   "código nuevo fuera de los «Dónde vive», sin contar las migraciones, que se comparan con Datos")
ok("usa «orden»" in o and "usa «order»" not in o and "«Pedido»" in o,
   "nombres que el diseño dice que no son un concepto, en lo que se define (crear_orden) y no en un parámetro (order_id)")
ok("sin pull request" not in o and "se unió sin squash" not in o and "se editó" not in o and "En esta versión no se vigilan los commits directos" in o and "cambió CLAUDE.md" in o,
   "la 1.27.0 no recorre la historia (#2026-11-19-3): no da commits directos, uniones sin squash ni migraciones editadas, y lo dice")
ok("el release v2 (`ccccccc`) no tiene «Aprobó:»" in o, "un paso a Prod sin sí")
ok("Ana Prueba aprobó v1 (acme/app), que lleva su #1" in o, "un sí que se dio quien construyó")
datos = json.loads(o.split("=== DATOS\n")[1])
ok(datos["fuera_del_plan"] == ["acme/app#4"], "DATOS trae lo fuera del plan")

print("Quién construyó es el autor, no cualquiera de «Construye»")
r2 = raiz(construye="Ana Prueba (ana@ejemplo.test, @otra) · Carla Prueba (carla@ejemplo.test, @ana)")
rc, o, e = correr("seguimiento", r2, "ventas/app", "--github", g, "--pidio", "Beto Prueba", "--fecha", HOY)
ok("Pasos a Prod que aprobó quien construyó:** ninguno." in o, "Ana aprobó, pero el #1 es de @ana, que es Carla")

print("Escribir: crea el seguimiento, que nace vigente, y la entrada siguiente va arriba")
rc, o, e = correr("seguimiento", r, "ventas/app", "--github", g, "--pidio", "Beto Prueba", "--fecha", HOY, "--escribir", "--crear")
d = json.loads(o.split("=== DATOS\n")[1])
f = r / "ventas/app/entregables/seguimiento.md"
ok(rc == 0 and f.is_file() and d["escrito"] == "ventas/app/entregables/seguimiento.md", "crea entregables/seguimiento.md")
t = f.read_text(encoding="utf-8")
ok(t.startswith("---\nestado: vigente\n") and f"actualizado: {HOY}" in t, "nace vigente, con la fecha de hoy")
ok(d["reemplazo_proyecto"] == {"de": "Seguimiento: por crear", "a": "Seguimiento: ventas/app/entregables/seguimiento.md"},
   "devuelve el reemplazo de proyecto.md para cerrar.py")
p = r / "ventas/app/proyecto.md"
p.write_text(p.read_text(encoding="utf-8").replace("Seguimiento: por crear", "Seguimiento: ventas/app/entregables/seguimiento.md"), encoding="utf-8")
rc, o, e = correr("seguimiento", r, "ventas/app", "--github", g, "--pidio", "Ana Prueba", "--fecha", "2026-11-19", "--escribir")
t = f.read_text(encoding="utf-8")
ok(t.index("## 2026-11-19 · pidió Ana Prueba") < t.index(f"## {HOY} · pidió Beto Prueba"), "la nueva arriba, sin borrar la anterior")
ok(json.loads(o.split("=== DATOS\n")[1])["anterior"] == HOY, "dice de cuándo era el anterior")

print("Sin GitHub")
rc, o, e = correr("seguimiento", r, "ventas/app", "--github", gh_json({"repos": [{"repo": "acme/app", "error": "no hay gh en esta sesión"}]}),
                  "--pidio", "Ana Prueba", "--fecha", HOY)
ok(rc == 0 and "GitHub: no se pudo leer (acme/app: no hay gh en esta sesión). Solo va lo que dice la memoria." in o, "lo dice en la cabecera")
ok("Comparó: nada contra GitHub." in o and "| P01" not in o, "y no inventa estados")
antes = (r / "ventas/app/entregables/seguimiento.md").read_text(encoding="utf-8")
rc, o, e = correr("seguimiento", r, "ventas/app", "--github", gh_json({"repos": [{"repo": "acme/app", "error": "HTTP 404"}]}),
                  "--pidio", "Ana Prueba", "--fecha", "2026-11-20", "--escribir")
ok(json.loads(o.split("=== DATOS\n")[1]).get("no_escrito") and (r / "ventas/app/entregables/seguimiento.md").read_text(encoding="utf-8") == antes,
   "sin GitHub, --escribir no guarda nada")

print("Otra forma de «Paso a Prod»")
r3 = raiz(paso="sí sobre el resumen del despliegue")
rc, o, e = correr("seguimiento", r3, "ventas/app", "--github", g, "--pidio", "Beto Prueba", "--fecha", HOY)
ok("Paso a Prod: «sí sobre el resumen del despliegue». El sí no queda en GitHub" in o, "dice qué entendió")
ok("| P02 · API | F1 | en curso" in o and "no tiene «Aprobó:»" not in o, "una etiqueta cuenta como paso a Prod, y no se pide «Aprobó:»")

print("Un proyecto que no es de desarrollo")
r4 = raiz()
p = r4 / "ventas/app/proyecto.md"
p.write_text(p.read_text(encoding="utf-8").split("## Desarrollo")[0], encoding="utf-8")
rc, o, e = correr("seguimiento", r4, "ventas/app", "--github", g, "--pidio", "Beto Prueba", "--fecha", HOY)
ok(rc != 0 and "no es un proyecto de desarrollo" in (o + e), "se niega y dice por qué")

print("La auditoría")
rc, o, e = correr("auditoria", r, "ventas/app", "--github", g, "--fecha", HOY)
a = vista(json.loads(o))
co = a["comprobado"]
ok(co["R1"]["acme/app"]["estado"] == "cumple", "R1: el ruleset exige pull request sin excepciones y solo squash")
ok(co["R2"]["acme/app"]["estado"] == "no cumple" and "Do not allow bypassing" in co["R2"]["acme/app"]["evidencia"],
   "R2: comprobaciones obligatorias que un administrador se puede saltar")
ok(co["R3"]["acme/app"]["estado"] == "cumple", "R3: comprobación de secretos y protección al subir")
ok(co["R6"]["acme/app"]["estado"] == "no cumple" and "#4" in co["R6"]["acme/app"]["evidencia"], "R6: un pull request unido sin pieza")
_pf = {x["fila"] for x in a["preguntar"]}
ok(_pf >= {"PL1", "PL2", "PL3", "PL7", "R5", "R7"}, "lo que no se pudo, a preguntar: " + ", ".join(sorted(_pf)))
ok("R4" not in co and any(x["fila"] == "R4" and "historial" in x["porque"] for x in a["preguntar"]),
   "R4 se pregunta, con el historial de la carpeta de migraciones")
ok("R7" not in co and any(x["fila"] == "R7" and "CLAUDE.md" in x["porque"] for x in a["preguntar"]), "R7 tampoco: se pregunta con lo que tiene el CLAUDE.md")
ok(any(x["fila"] == "PL1" and "403" in x["porque"] for x in a["preguntar"]), "con el motivo")
ok(a["pasos_a_prod"]["acme/app"]["si_propio"] and a["pasos_a_prod"]["acme/app"]["si_propio"][0]["pr"] == 1, "los síes que alguien se dio a sí mismo")
ok(co["R2"]["acme/app"]["regla"] == "las pruebas pasan antes de unir" and all(x["regla"] for x in a["preguntar"]),
   "cada fila lleva su regla en llano")

print("Un bloque y los pasos dentro de él")
g2 = json.loads(json.dumps(GH))
g2["repos"][0]["pulls"] += [{"number": 9, "title": "P03 · paso interno", "state": "merged", "author": "ana", "bot": False,
                             "merge_commit": "9" * 40, "merged_at": "2026-11-14T10:00:00Z", "base": "version-2"},
                            {"number": 10, "title": "P02 + P03 · el bloque", "state": "open", "author": "ana", "bot": False,
                             "merge_commit": "", "merged_at": "", "base": "main"}]
rc, o, e = correr("seguimiento", r, "ventas/app", "--github", gh_json(g2), "--pidio", "Beto Prueba", "--fecha", HOY)
ok("| P03 · Vista | F1 | en curso | acme/app#10 |" in o and "#9" not in o, "el pull request del bloque cuenta para P02 y P03, y el paso interno no cuenta")

print("Aplicar los estados")
conf = r / "ventas/app/entregables/repositorios.md"
est = pathlib.Path(tempfile.mkdtemp()) / "e.json"
est.write_text(json.dumps({"R1": {"acme/app": "cumple"}, "R4": {"acme/app": "no aplica"}, "R2": {"acme/app": "no cumple"}}), encoding="utf-8")
antes = conf.read_text(encoding="utf-8")
rc, o, e = correr("aplicar", r, "ventas/app", conf, est, "--cuenta", "beto@ejemplo.test", "--fecha", HOY)
t = conf.read_text(encoding="utf-8")
ok(rc == 0 and f"| cumple · {HOY} |" in t and "| no aplica |" in t and f"| no cumple · {HOY} |" in t, "escribe cada estado, con fecha salvo «no aplica»")
import difflib
_dif = [l for l in difflib.ndiff(antes.split("\n"), t.split("\n")) if l.startswith("+ ") and l.strip() != "+" and not l.startswith("+ Última auditoría:")]
ok(f"actualizado: {HOY}" in t and f"Última auditoría: {HOY} · Beto Prueba" in t and len(_dif) == 4,
   "pone la fecha de la cabecera, quién confirmó, y cambia solo las tres filas")
est.write_text(json.dumps({"R1": {"acme/app": "regular"}}), encoding="utf-8")
rc, o, e = correr("aplicar", r, "ventas/app", conf, est, "--cuenta", "beto@ejemplo.test", "--fecha", HOY)
ok(rc != 0 and "no es cumple" in e, "un estado que no es de los cuatro se rechaza")
plat = r / "ventas/app/entregables/plataforma.md"
est.write_text(json.dumps({"PL1": "cumple", "PL3": "excepción"}), encoding="utf-8")
rc, o, e = correr("aplicar", r, "ventas/app", plat, est, "--cuenta", "beto@ejemplo.test", "--fecha", HOY)
t = plat.read_text(encoding="utf-8")
ok(rc == 0 and re.search(r"^\| PL1 \|.*\| cumple · " + HOY + r" \|$", t, re.M) and re.search(r"^\| PL3 \|.*\| excepción \|$", t, re.M),
   "en la de plataforma, la columna Estado")

print("Los arreglos de la revisión de la 1.27.0")
def gh_mod(f):
    g = json.loads(json.dumps(GH)); f(g["repos"][0]); return gh_json(g)
def entrada_de(raiz_, g, *extra):
    rc, o, e = correr("seguimiento", raiz_, "ventas/app", "--github", g, "--pidio", "Beto Prueba", "--fecha", HOY, *extra)
    return rc, o, json.loads(o.split("=== DATOS\n")[1]) if "=== DATOS" in o else {}
def raiz_con_seguimiento(**k):
    """Una raíz con el seguimiento del 2026-11-03 al que citan los síes de la prueba."""
    r_ = raiz(seguimiento="ventas/app/entregables/seguimiento.md", **k)
    (r_ / "ventas/app/entregables/seguimiento.md").write_text(
        f"---\nestado: vigente\nactualizado: {HOY}\n---\n\n# Seguimiento\n\n## 2026-11-03 · pidió Ana\nLeído: acme/app en `aaaaaaa` (main), desde el 2026-10-01.\nComparó: piezas, diseño, reglas.\n\n**Rompe las reglas:** nada.\n", encoding="utf-8")
    return r_
r5 = raiz()
r5s = raiz_con_seguimiento()
# hallazgo 2: una lectura parcial no da estados ni se guarda
rc, o, d = entrada_de(r5, gh_mod(lambda x: x.update(errores={"pulls": "HTTP 502"})), "--escribir")
ok("**Piezas:** sin estado" in o and "Incompleto, no se guarda" in o and d.get("no_escrito") and not (r5 / "ventas/app/entregables/seguimiento.md").exists(),
   "con los pull requests a medias, sin estado de piezas y sin guardar")
rc, o, d = entrada_de(r5, gh_mod(lambda x: x.update(truncado=["commits"])))
ok("Rompe las reglas:** sin vigilar" in o and "No está en el diseño:** sin comparar" in o and "| P01" in o, "con los commits cortados, ni reglas ni diseño, y las piezas sí")
# hallazgo 5: «Aprobó:» vacío o de quien no acepta ni audita
rc, o, d = entrada_de(r5, gh_mod(lambda x: x["releases"][1].update(body="Aprobó:\n\n## Cambios")))
ok("| P01 · Tablas | F1 | unida |" in o and "no tiene «Aprobó:»" in o, "un «Aprobó:» vacío no es un sí, y no toma la línea siguiente")
rc, o, d = entrada_de(r5, gh_mod(lambda x: x["releases"][1].update(body="Aprobó: Pepe Nadie, 2026-11-03")))
ok("| P01 · Tablas | F1 | unida |" in o and "lo aprobó «Pepe Nadie», que no acepta ni audita" in o, "un sí de quien no acepta ni audita no entrega y se dice")
rc, o, d = entrada_de(r5s, gh_mod(lambda x: x.update(base="aaaaaaa") or x["releases"][1].update(body="Aprobó: @ana · seguimiento 2026-11-03")))
ok("| P01 · Tablas | F1 | entregada |" in o and "Ana Prueba aprobó v1" in o, "el sí por @usuario, sobre un seguimiento que existe, entrega; y se dice que es propio")
rc, o, d = entrada_de(r5s, gh_mod(lambda x: x.update(base="aaaaaaa") or x["releases"][1].update(body="Aprobó: @ana, 2026-11-03")))
ok("| P01 · Tablas | F1 | unida |" in o and "Sí sin seguimiento" in o, "sin seguimiento citado no es un sí: no entrega, y se dice")
# hallazgo 6: sin forma, nada entregado; los prerelease no cuentan
r6 = raiz(paso="por crear")
rc, o, d = entrada_de(r6, gh_json(GH))
ok("entregada" not in o.split("**Piezas**")[1] and "no se puede comprobar con esta forma" in o, "«Paso a Prod: por crear»: nada sale entregado y no se dice «ninguno»")
rc, o, d = entrada_de(r5, gh_mod(lambda x: x["releases"][1].update(prerelease=True)))
ok("| P01 · Tablas | F1 | unida |" in o, "un prerelease no es un paso a Prod")
# hallazgo 7: una pieza unida antes de la ventana leída sigue entregada
rc, o, d = entrada_de(r5s, gh_mod(lambda x: x.update(commits=[c for c in x["commits"] if not c["sha"].startswith("a")])))
ok("| P01 · Tablas | F1 | entregada |" in o, "fuera de la ventana de commits, entregada por fecha frente al paso a Prod")
# hallazgo 3: sin rama base no cuenta
rc, o, d = entrada_de(r5, gh_mod(lambda x: [p.pop("base") for p in x["pulls"] if p["number"] == 3]))
ok("| P02 · API | F1 | unida |" in o and "Sin rama base, no cuentan: acme/app#3" in o, "un pull request sin base no cuenta y se dice")
# hallazgo 4 y 13: dónde se escribe, y el reemplazo solo dentro de la sección
r7 = raiz(seguimiento="../../fuera.md")
rc, o, d = entrada_de(r7, gh_json(GH), "--escribir")
ok(d.get("no_escrito") and not (r7.parent / "fuera.md").exists(), "fuera del proyecto, no se escribe")
r8 = raiz(seguimiento="ventas/app/entregables/plan.md")
antes_plan = (r8 / "ventas/app/entregables/plan.md").read_text(encoding="utf-8")
rc, o, d = entrada_de(r8, gh_json(GH), "--escribir")
ok(d.get("no_escrito") and (r8 / "ventas/app/entregables/plan.md").read_text(encoding="utf-8") == antes_plan, "encima de un archivo que no es un seguimiento, no")
r9 = raiz(seguimiento="ventas/app/entregables/seguimiento.md")
rc, o, d = entrada_de(r9, gh_json(GH), "--escribir")
ok(d.get("no_escrito") and "tráelo" in d["no_escrito"], "una ruta escrita que no está en la copia: no se crea sin --crear")
rc, o, d = entrada_de(r9, gh_json(GH), "--escribir", "--crear")
ok(d.get("creado") == "ventas/app/entregables/seguimiento.md" and "reemplazo_proyecto" not in d, "con --crear se crea, sin tocar proyecto.md")
r10 = raiz()
pp = r10 / "ventas/app/proyecto.md"
pp.write_text(pp.read_text(encoding="utf-8").replace("## Quién participa", "## Siguientes pasos\n- Seguimiento: llamar a Beto el lunes\n\n## Quién participa")
              .replace("Seguimiento: por crear", "- **Seguimiento:** por crear"), encoding="utf-8")
rc, o, d = entrada_de(r10, gh_json(GH), "--escribir")
ok(d.get("no_escrito") and "--crear" in d["no_escrito"], "«por crear» tampoco se crea sin --crear: pudo crearlo un seguimiento sin cerrar")
rc, o, d = entrada_de(r10, gh_json(GH), "--escribir", "--crear")
ok(d.get("reemplazo_proyecto") == {"de": "- **Seguimiento:** por crear", "a": "- **Seguimiento:** ventas/app/entregables/seguimiento.md"},
   "el reemplazo es la línea de la sección, con su forma")
ok("basado_en: [ventas/app/entregables/plan.md, ventas/app/entregables/diseno.md]" in (r10 / "ventas/app/entregables/seguimiento.md").read_text(encoding="utf-8"),
   "el seguimiento nace con basado_en")
# hallazgo 1: lo que la cuenta no ve va a preguntar
def sin_admin(x):
    a = x["auditoria"]
    a["rulesets"][0].pop("bypass_actors"); a["proteccion"] = None; a["errores"] = {"proteccion": "HTTP 403", "org": "HTTP 403", "admins": "HTTP 403"}
    a["repo"] = {"private": True, "default_branch": "main"}
rc, o, e = correr("auditoria", r, "ventas/app", "--github", gh_mod(sin_admin), "--fecha", HOY)
a2 = vista(json.loads(o))
pf = {x["fila"] for x in a2["preguntar"]}
ok("R1" in pf and "R3" in pf and "PL1" in pf and "R1" not in a2["comprobado"] and "R3" not in a2["comprobado"],
   "sin permisos de administración, R1, R3 y PL1 van a preguntar, no a cumple ni a no cumple")
# hallazgo 11: dos organizaciones
def dos_orgs(g):
    o1 = g["repos"][0]
    o1["auditoria"]["org"] = {"two_factor_requirement_enabled": False, "plan": "team"}; o1["auditoria"]["admins"] = ["ana", "beto"]
    o2 = json.loads(json.dumps(o1)); o2["repo"] = "otra/web"; o2["auditoria"]["org"] = {"two_factor_requirement_enabled": True, "plan": "team"}
    g["repos"].append(o2)
g = json.loads(json.dumps(GH)); dos_orgs(g)
rc, o, e = correr("auditoria", r, "ventas/app", "--github", gh_json(g), "--fecha", HOY)
pl1 = vista(json.loads(o))["comprobado"]["PL1"]["Estado"]
ok(pl1["estado"] == "no cumple" and "acme" in pl1["evidencia"] and "otra" in pl1["evidencia"], "con dos organizaciones, PL1 no cumple si una no cumple")
# hallazgo 10: aplicar rechaza filas que no están
est.write_text(json.dumps({"R9": {"acme/app": "cumple"}}), encoding="utf-8")
rc, o, e = correr("aplicar", r, "ventas/app", conf, est, "--cuenta", "beto@ejemplo.test", "--fecha", HOY)
ok(rc != 0 and "R9" in e, "una fila que no está se rechaza")
est.write_text(json.dumps({"R1": {"acme/app": "cumple"}}), encoding="utf-8")
rc, o, e = correr("aplicar", r, "ventas/app", conf, est, "--cuenta", "ana@ejemplo.test", "--fecha", HOY)
ok(rc != 0 and "Audita" in e, "solo quien audita escribe los estados")

print("Los arreglos de la primera ronda")
r11 = raiz()
for nombre, g_, que in (
        ("sin «terminado»", gh_json(dict(GH, terminado=False)), "no terminó"),
        ("un repositorio de la sección que falta", gh_json(dict(GH, repos=[dict(GH["repos"][0], repo="acme/otro")])), "acme/app: no está"),
        ("de otro día", gh_json(dict(GH, hoy="2026-11-10")), "no de hoy"),
        ("sin la lista de releases", gh_mod(lambda x: x.pop("releases")), "no trae releases"),
        ("un pull request unido sin fecha", gh_mod(lambda x: x["pulls"][0].update(merged_at=None)), "sin fecha (#1)")):
    rc, o, d = entrada_de(r11, g_, "--escribir", "--crear")
    ok(que in o and d.get("no_escrito") and not (r11 / "ventas/app/entregables/seguimiento.md").exists(), f"{nombre}: incompleto, no se guarda")
rc, o, d = entrada_de(r11, gh_mod(lambda x: x.update(truncado=["tags"])))
ok("tags cortado" not in o and "Incompleto" not in o and "Comparó: piezas, diseño, reglas" in o,
   "con «release de GitHub» las etiquetas cortadas no hacen falta: se guarda y no se dice que no se comparó")
rc, o, d = entrada_de(r11, gh_mod(lambda x: x.update(truncado=["releases"])))
ok("Sin leer entero, no se compara: acme/app: releases cortado" in o and "Incompleto" not in o, "con los releases cortados se guarda, y se dice qué no se comparó")
rc, o, d = entrada_de(r11, gh_mod(lambda x: x["pulls"][0].update(author=None, merge_commit=None, merged_at=None, state="open")))
ok(rc == 0, "un autor o un commit de unión nulos no rompen la lectura")
rc, o, d = entrada_de(r11, gh_mod(lambda x: x["releases"][1].update(author="ana")))
ok("el release v1 lo publicó @ana, que no administra" in o, "un release que publicó quien no administra rompe las reglas")
r14 = raiz(seguimiento="ventas/app/entregables/seguimiento.md")
(r14 / "ventas/app/entregables/seguimiento.md").write_text(f"---\nestado: vigente\nactualizado: {HOY}\n---\n\n# Seguimiento\n\n## 2026-11-01 · pidió Ana\nnada\n", encoding="utf-8")
rc, o, d = entrada_de(r14, gh_json(GH))
ok("cita el seguimiento del 2026-11-03, que no está en el archivo" in o and "| P01 · Tablas | F1 | unida |" in o,
   "el seguimiento citado en «Aprobó:» tiene que existir, o la pieza no sale entregada")
r18 = raiz(seguimiento="ventas/app/entregables/seguimiento.md")
rc, o, d = entrada_de(r18, gh_json(GH))
ok("no está en el archivo" not in o and "no se pudo comprobar la cita" in o and "| P01 · Tablas | F1 | unida |" in o,
   "sin el seguimiento en la copia, la cita no se da por mala, pero tampoco entrega")
for nombre, g_, que in (("sin «hoy»", gh_json(dict(GH, hoy=""), completa=True), "no dice de qué día"),
                        ("«hoy» con hora", gh_json(dict(GH, hoy="2026-11-18T10:00:00Z")), "no dice de qué día"),
                        ("un JSON de auditoría", gh_json(dict(GH, auditoria=True)), "es de una auditoría"),
                        ("releases con error", gh_mod(lambda x: x.update(errores={"releases": "HTTP 502"})), "releases HTTP 502")):
    rc, o, d = entrada_de(r11, g_, "--escribir", "--crear")
    ok(rc == 0 and que in o and d.get("no_escrito"), f"{nombre}: incompleto, no se guarda")
def migracion_secreta(x):
    x["detalle"][1]["files"].append({"filename": "migrations/005_add_password_hash.sql", "status": "added", "patch": "+CREATE TABLE claves (id int);"})
rc, o, d = entrada_de(r11, gh_mod(migracion_secreta))
ok("la tabla «claves»" in o, "una migración con «password» en el nombre se compara con el diseño")
ok(d.get("sin_mirar") == 0, "sin_mirar no cuenta lo que nunca se iba a mirar")
r15 = raiz(); (r15 / "guia.md").unlink()
est.write_text(json.dumps({"R1": {"acme/app": "cumple"}}), encoding="utf-8")
rc, o, e = correr("aplicar", r15, "ventas/app", r15 / "ventas/app/entregables/repositorios.md", est, "--cuenta", "beto@ejemplo.test", "--fecha", HOY)
ok(rc != 0 and "guia.md" in e, "aplicar sin guia.md en la copia no escribe")
r16 = raiz(); pp = r16 / "ventas/app/proyecto.md"
pp.write_text(re.sub(r"(?s)## Desarrollo.*", "## Desarrollo\nRepositorio: acme/app\nConstruyen: Ana\n", pp.read_text(encoding="utf-8")), encoding="utf-8")
rc, o, e = correr("seguimiento", r16, "ventas/app", "--github", gh_json(GH), "--pidio", "Ana", "--fecha", HOY)
ok(rc != 0 and "mal escrita" in e, "una sección con las claves mal escritas lo dice, no que no es de desarrollo")
r12 = raiz(); (r12 / "guia.md").unlink()
rc, o, d = entrada_de(r12, gh_json(GH), "--escribir", "--crear")
ok("guia.md" in (d.get("no_escrito") or "") and not (r12 / "ventas/app/entregables/seguimiento.md").exists(), "sin guia.md en la copia, no se escribe")
r13 = raiz(); pp = r13 / "ventas/app/proyecto.md"; pp.write_text(pp.read_text(encoding="utf-8").replace("Seguimiento: por crear\n", ""), encoding="utf-8")
rc, o, d = entrada_de(r13, gh_json(GH), "--escribir", "--crear")
ok("«Seguimiento:»" in (d.get("no_escrito") or ""), "sin la línea «Seguimiento:», pide añadirla")
def reglas_sin_leer(x):
    x["auditoria"]["errores"] = {"rulesets": "HTTP 502", "org": "HTTP 403", "admins": "HTTP 403"}
rc, o, e = correr("auditoria", r, "ventas/app", "--github", gh_mod(reglas_sin_leer), "--fecha", HOY)
a3 = vista(json.loads(o))
ok("R1" not in a3["comprobado"] and "R2" not in a3["comprobado"] and any(x["fila"] == "R1" and "502" in x["porque"] for x in a3["preguntar"]),
   "si los rulesets no se leyeron, R1 y R2 se preguntan aunque la protección clásica se vea")
vistas = {(f, c_) for f, cols in a["comprobado"].items() for c_ in cols} | {(x["fila"], x["columna"]) for x in a["preguntar"]}
ok({("R%d" % i, "acme/app") for i in range(1, 8)} <= vistas and {("PL%d" % i, "Estado") for i in range(1, 8)} <= vistas,
   "toda fila de las dos configuraciones sale comprobada o a preguntar")
otro = r / "ventas/app/entregables/plan.md"
est.write_text(json.dumps({"R1": {"acme/app": "cumple"}}), encoding="utf-8")
rc, o, e = correr("aplicar", r, "ventas/app", otro, est, "--cuenta", "beto@ejemplo.test", "--fecha", HOY)
ok(rc != 0 and "no es una de las configuraciones" in e, "aplicar solo escribe en las dos configuraciones de la sección")

print("Los arreglos de la segunda ronda: la auditoría solo propone")
def audita(g):
    rc, o, e = correr("auditoria", r, "ventas/app", "--github", g, "--fecha", HOY)
    return vista(json.loads(o)) if rc == 0 else {"comprobado": {}, "preguntar": [], "avisos": [e]}
def prop(a_, fila, col="acme/app"):
    return (a_["comprobado"].get(fila) or {}).get(col, {}).get("estado")
def sin_rulesets(err):
    def f(x):
        x["auditoria"]["rulesets"] = []; x["auditoria"]["proteccion"] = None; x["auditoria"]["errores"] = {"proteccion": err}
    return f
a4 = audita(gh_mod(sin_rulesets("gh: Not Found (HTTP 404)")))
ok(prop(a4, "R1") is None and prop(a4, "R2") is None, "un 404 «Not Found» de la protección no es «sin proteger»: sin propuesta")
a4 = audita(gh_mod(sin_rulesets("gh: Branch not protected (HTTP 404)")))
ok(prop(a4, "R1") == "no cumple", "«Branch not protected» sí propone «no cumple»")
def excluye(x):
    x["auditoria"]["rulesets"][0]["conditions"]["ref_name"] = {"include": ["~ALL"], "exclude": ["refs/heads/main"]}; x["auditoria"]["proteccion"] = None
a4 = audita(gh_mod(excluye))
ok(prop(a4, "R1") is None and any(x["fila"] == "R1" and "excluye" in x["porque"] for x in a4["preguntar"]), "un ruleset con exclusiones no se interpreta: se dice")
def saltan(x):
    x["auditoria"]["rulesets"] = []
    x["auditoria"]["proteccion"] = {"enforce_admins": {"enabled": True}, "required_status_checks": {"contexts": ["pruebas"]},
                                    "required_pull_request_reviews": {"bypass_pull_request_allowances": {"users": [{"login": "ana"}]}}}
a4 = audita(gh_mod(saltan))
ok(prop(a4, "R1") == "no cumple" and "ana" in a4["comprobado"]["R1"]["acme/app"]["evidencia"], "con gente en las excepciones de la protección clásica, R1 propone «no cumple»")
def solo_nombre(x):
    x["auditoria"]["repo"]["security_and_analysis"] = {"secret_scanning_push_protection": {"status": "disabled"}}
a4 = audita(gh_mod(solo_nombre))
ok(prop(a4, "R3") is None, "una comprobación llamada «secretos» no basta para proponer R3")
a4 = audita(gh_json(dict(GH, hoy="2026-06-01", terminado=False)))
ok(a4["avisos"] and not a4["comprobado"], "con el JSON viejo o sin terminar, nada se propone y se avisa")
a4 = audita(gh_mod(lambda x: x["pulls"].append({"number": 9, "title": "sin pieza", "state": "merged", "author": "ana", "base": "main", "merge_commit": "9" * 40, "merged_at": ""})))
ok(any("lo leído" in v or "sin fecha" in v for v in a4["avisos"]) and not a4["comprobado"], "un unido sin fecha deja la auditoría sin propuestas")
def free(g):
    o1 = g["repos"][0]; o1["auditoria"]["org"] = {"two_factor_requirement_enabled": True, "plan": "free"}; o1["auditoria"]["admins"] = ["beto"]
    o1["auditoria"]["repo"]["private"] = False
    g["repos"].append({"repo": "acme/privado", "error": "HTTP 404"})
g5 = json.loads(json.dumps(GH)); free(g5)
a4 = audita(gh_json(g5))
ok(prop(a4, "PL1", "Estado") is None and prop(a4, "PL2", "Estado") is None, "plan Free con un repositorio sin leer, y un solo owner visto: sin propuesta")
r17 = raiz(); pp = r17 / "ventas/app/proyecto.md"; pp.write_text(pp.read_text(encoding="utf-8").replace("Repositorios: acme/app", "Repositorios: Acme/App"), encoding="utf-8")
cf = r17 / "ventas/app/entregables/repositorios.md"; cf.write_text(cf.read_text(encoding="utf-8").replace("acme/app", "Acme/App"), encoding="utf-8")
rc, o, e = correr("auditoria", r17, "ventas/app", "--github", gh_json(GH), "--fecha", HOY)
a4 = vista(json.loads(o))
ok(not [x for x in a4["filas"] if "no se leyó" in x["evidencia"]] and all(x["columna"] in ("Acme/App", "Estado") for x in a4["filas"]),
   "la columna se compara sin mayúsculas y sale con la grafía de la tabla")
sys.path.insert(0, str(SKILL)); import recoger_github as _rg
ok(all(not _rg.quitar_patch(f) for f in ("migrations/005_add_password_hash.sql", "api/pedidos.py", "web/CrearOrden.vue"))
   and not any(_rg.CODIGO.search(f) for f in (".env.production", "certs/x.pem", "terraform.tfstate", ".pgpass", "config/credentials.json")),
   "lista blanca: solo el código y el SQL guardan su patch; la configuración y los secretos, nunca")

print("Los arreglos de la tercera ronda")
r19 = raiz()
r20 = raiz(seguimiento="ventas/app/entregables/seguimiento.md")
(r20 / "ventas/app/entregables/seguimiento.md").write_text(
    f"---\nestado: vigente\nactualizado: {HOY}\n---\n\n# Seguimiento\n\n## 2026-11-10 · pidió Ana\n\n**Rompe las reglas:** sin vigilar: no se leyeron enteros los commits.\n\n"
    "## 2026-10-25 · pidió Ana\nLeído: acme/app en `abcdef1` (main), desde el 2026-10-01.\nComparó: piezas, diseño, reglas.\n\n**Rompe las reglas:** nada.\n", encoding="utf-8")
rc, o, e = correr("desde", r20, "ventas/app")
dd = json.loads(o) if rc == 0 else {}
ok(dd.get("args") == "--desde 2026-10-25", "«desde» da la fecha del último seguimiento que vigiló los pasos a Prod: " + o.strip())
rc, o, d = entrada_de(r20, gh_json(GH), "--escribir")
ok("hay que leer desde el 2026-10-25" in o and d.get("no_escrito"), "lo leído desde después del último que vigiló no se guarda")
rc, o, d = entrada_de(r11, gh_json(dict(GH, hoy="2026-13-45")))
ok(rc == 0 and "no dice de qué día" in o, "un «hoy» imposible no rompe el script")
rc, o, d = entrada_de(r11, gh_mod(lambda x: x.update(errores={"pulls": "HTTP 502"})))
ok(o.split("=== DATOS")[0].count("pulls HTTP 502") == 1, "un error se dice una vez")
r21 = raiz(); pp = r21 / "ventas/app/proyecto.md"; pp.write_text(re.sub(r"(?m)^Administra:.*\n", "", pp.read_text(encoding="utf-8")), encoding="utf-8")
rc, o, d = entrada_de(r21, gh_json(GH))
ok("la sección no dice quién administra" in o, "sin «Administra», el motivo lo dice")
ok(o.index("**Rompe las reglas:**") < o.index("Quién publicó, sin comprobar"), "«Quién publicó» va con las reglas, no con el diseño")
a5 = audita(gh_json(dict(GH, desde="2026-11-14")))
ok(any("hay que leer desde" in v for v in a5["avisos"]) and not a5["comprobado"], "la auditoría con un mes sin leer entero avisa y no propone")
rc, o, e = correr("auditoria", r21, "ventas/app", "--github", gh_json(GH), "--fecha", HOY)
a5 = vista(json.loads(o))
ok("publico_sin_ver" in a5["pasos_a_prod"]["acme/app"] and any(x["fila"] == "R5" and "avisos" in x["porque"] and "no traen" not in x["porque"] for x in a5["preguntar"]),
   "R5 cuenta lo que no se pudo comprobar de quién publicó")
a5 = audita(gh_mod(lambda x: x.update(auditoria={"repo": x["auditoria"]["repo"], "errores": {}})))
ok(prop(a5, "R1") is None and prop(a5, "R2") is None, "un JSON sin rulesets ni protección no propone «no cumple»")
def dos_capas(x):
    x["auditoria"]["proteccion"] = {"enforce_admins": {"enabled": True},
                                    "required_pull_request_reviews": {"bypass_pull_request_allowances": {"users": [{"login": "ana"}]}}}
a5 = audita(gh_mod(dos_capas))
ok(prop(a5, "R1") == "cumple", "un ruleset sin excepciones manda sobre las excepciones de la protección clásica")
g6 = json.loads(json.dumps(GH)); g6["repos"].insert(0, {"repo": "acme/caido", "error": "HTTP 502"})
pp = r / "ventas/app/proyecto.md"; t0 = pp.read_text(encoding="utf-8")
pp.write_text(t0.replace("Repositorios: acme/app", "Repositorios: acme/caido · acme/app"), encoding="utf-8")
a5 = audita(gh_json(g6))
pl = [x for x in a5["comprobado"].get("PL1", {}).values()] + [x for x in a5["preguntar"] if x["fila"] == "PL1"]
ok(pl and "502" not in pl[0]["porque"], "el repositorio sin leer que va primero no se lleva los datos de la organización")
ok(prop(a5, "R1", "acme/app") == "cumple", "el error de un repositorio no quita las propuestas de otro")
pp.write_text(t0, encoding="utf-8")
r22 = raiz(); pp = r22 / "ventas/app/proyecto.md"
pp.write_text(pp.read_text(encoding="utf-8").replace("Configuración de plataforma: ventas/app/entregables/plataforma.md", "Configuración de plataforma: ../fuera.md"), encoding="utf-8")
est.write_text(json.dumps({"PL3": "cumple"}), encoding="utf-8")
rc, o, e = correr("aplicar", r22, "ventas/app", r22 / "../fuera.md", est, "--cuenta", "beto@ejemplo.test", "--fecha", HOY)
ok(rc != 0 and not (r22.parent / "fuera.md").exists(), "aplicar no escribe fuera de la raíz aunque la sección lo diga")
est.write_text("[1, 2]", encoding="utf-8")
rc, o, e = correr("aplicar", r, "ventas/app", r / "ventas/app/entregables/repositorios.md", est, "--cuenta", "beto@ejemplo.test", "--fecha", HOY)
ok(rc != 0 and "Traceback" not in e and "van como" in e, "un JSON de estados mal formado se dice en llano")
ok(all(_rg.quitar_patch(f) for f in ("config/secrets.yml", "id_rsa", "service-account.json", "prod.tfvars", ".npmrc", "wp-config.php",
                                     "config/secrets.py", "db/dump.sql", "src/environments/environment.prod.ts")),
   "ningún archivo de configuración guarda su patch")

print("Los arreglos de la cuarta ronda")
r23 = raiz_con_seguimiento()
rc, o, d = entrada_de(r23, gh_mod(lambda x: x.update(detalle=[])), "--escribir")
ok("6 de 6 commits sin sus cambios" in o and "No está en el diseño:** sin comparar" in o, "un «detalle» vacío no se compara como si no hubiera cambios")
r24 = raiz(seguimiento="ventas/app/entregables/seguimiento.md")
(r24 / "ventas/app/entregables/seguimiento.md").write_text(
    f"---\nestado: vigente\nactualizado: {HOY}\n---\n\n# Seguimiento\n\n## 2026-11-15 · nota de Ana\nrevisar luego\n\n"
    "## 2026-11-06 · pidió Ana\nLeído: acme/app en `bbbbbbb` (main), desde el 2026-10-01.\nComparó: piezas, diseño, reglas.\n\n**Rompe las reglas:** nada.\n", encoding="utf-8")
rc, o, e = correr("desde", r24, "ventas/app")
ok(json.loads(o)["args"] == "--desde 2026-11-06", "una nota a mano no cuenta como seguimiento")
r25 = raiz(seguimiento="ventas/app/entregables/seguimiento.md")
rc, o, e = correr("desde", r25, "ventas/app", "--crear")
ok(rc == 0 and json.loads(o)["args"] == "", "«desde --crear» da los args vacíos cuando el archivo no existe")
rc, o, d = entrada_de(r11, gh_mod(lambda x: x.update(truncado=["detalle"], commits_ventana=212)))
ok("repite con --max-detalle 212" in o, "con los cambios cortados, dice con qué tope repetir")
rc, o, d = entrada_de(r11, gh_mod(lambda x: x.update(errores={"detalle": "fffffff: HTTP 403: API rate limit exceeded"}, commits_ventana=212)))
ok("repite con --max-detalle" not in o, "con un error de GitHub, no sugiere subir el tope")
def capa_sin_ver(x):
    x["auditoria"].pop("rulesets")
    x["auditoria"]["proteccion"] = {"enforce_admins": {"enabled": True}, "required_status_checks": {"contexts": ["pruebas"]},
                                    "required_pull_request_reviews": {"bypass_pull_request_allowances": {"users": [{"login": "ana"}]}}}
a6 = audita(gh_mod(capa_sin_ver))
ok(prop(a6, "R1") is None, "con una capa sin ver, las excepciones de otra no dan «no cumple»")
a6 = audita(gh_mod(lambda x: x["auditoria"].update(proteccion=None, rulesets=[], errores={})))
ok(prop(a6, "R1") is None and prop(a6, "R2") is None, "una protección a null sin error es «no se leyó», no «no hay»")
pp = r / "ventas/app/proyecto.md"; t0 = pp.read_text(encoding="utf-8")
pp.write_text(t0.replace("Repositorios: acme/app", "Repositorios: acme/app · acme/otro"), encoding="utf-8")
a6 = audita(gh_json(GH))
ok(not a6["comprobado"] and any(x["columna"] == "acme/otro" and x["fila"] == "R1" for x in a6["preguntar"]),
   "un repositorio que falta deja todo sin propuesta y tiene sus filas")
pp.write_text(t0, encoding="utf-8")
g19 = json.loads(json.dumps(GH)); g19["desde"] = "2026-10-19"; g19["repos"][0]["commits"].append(c("2" * 40, "2026-10-01", "raíz", parents=0))
rc, o, e = correr("auditoria", r, "ventas/app", "--github", gh_json(g19), "--fecha", HOY)
ok(not vista(json.loads(o))["avisos"], "la auditoría da un día de margen al «desde»")
rc, o, e = correr("auditoria", r, "ventas/app", "--github", gh_json(GH), "--fecha", "2026-13-45")
ok(rc == 2 and "Traceback" not in e, "un --fecha imposible se rechaza en llano")
r26 = raiz(); pp = r26 / "ventas/app/proyecto.md"
pp.write_text(pp.read_text(encoding="utf-8").replace("Configuración de plataforma: ventas/app/entregables/plataforma.md",
                                                      "Configuración de plataforma: ventas/app/restringido/plataforma.md"), encoding="utf-8")
(r26 / "ventas/app/restringido").mkdir(); shutil.copy(r26 / "ventas/app/entregables/plataforma.md", r26 / "ventas/app/restringido/plataforma.md")
est.write_text(json.dumps({"PL3": "cumple"}), encoding="utf-8")
rc, o, e = correr("aplicar", r26, "ventas/app", r26 / "ventas/app/restringido/plataforma.md", est, "--cuenta", "beto@ejemplo.test", "--fecha", HOY)
ok(rc == 0, "aplicar escribe en el restringido/ del propio proyecto: " + e.strip()[:120])

print("Los arreglos de la quinta ronda")
def capa_sin_ver2(x):
    x["auditoria"].pop("rulesets"); x["auditoria"]["repo"]["allow_merge_commit"] = True
    x["auditoria"]["proteccion"] = {"enforce_admins": {"enabled": False}, "required_status_checks": {"contexts": ["pruebas"]},
                                    "required_pull_request_reviews": {}}
a7 = audita(gh_mod(capa_sin_ver2))
ok(prop(a7, "R1") is None and prop(a7, "R2") is None and any(x["fila"] == "R2" and "no se leyeron los rulesets" in x["porque"] for x in a7["preguntar"]),
   "con los rulesets sin leer, ni R1 por squash ni R2 dan «no cumple», y la evidencia lo dice en una frase propia")
a7 = audita(gh_mod(lambda x: x.update(truncado=["tags"])))
ok("acme/app" in a7["pasos_a_prod"], "con «release de GitHub», R5 no necesita las etiquetas enteras")
r27 = raiz(); pp = r27 / "ventas/app/proyecto.md"
pp.write_text(pp.read_text(encoding="utf-8").replace("Configuración de plataforma: ventas/app/entregables/plataforma.md",
                                                      "Configuración de plataforma: rrhh/otro/entregables/plataforma.md"), encoding="utf-8")
(r27 / "rrhh/otro/entregables").mkdir(parents=True); shutil.copy(r27 / "ventas/app/entregables/plataforma.md", r27 / "rrhh/otro/entregables/plataforma.md")
est.write_text(json.dumps({"PL3": "cumple"}), encoding="utf-8")
rc, o, e = correr("aplicar", r27, "ventas/app", r27 / "rrhh/otro/entregables/plataforma.md", est, "--cuenta", "beto@ejemplo.test", "--fecha", HOY)
ok(rc == 0, "aplicar escribe una configuración de plataforma compartida, la que dice la sección: " + e.strip()[:100])
rc, o, e = correr("aplicar", r, "ventas/app", r / "ventas/app/entregables/plataforma.md", est, "--cuenta", "beto@ejemplo.test", "--fecha", "2030-01-01")
ok(rc != 0 and "futuro" in e, "aplicar no acepta una fecha del futuro")
rc, o, d = entrada_de(r11, gh_mod(lambda x: x.update(commits=None)))
ok(rc == 2 and not d, "un JSON con otra forma no da un traceback")
r28 = raiz(seguimiento="ventas/app/entregables/seguimiento.md")
(r28 / "ventas/app/entregables/seguimiento.md").write_text(
    f"---\nestado: vigente\nactualizado: {HOY}\n---\n\n# Seguimiento\n\n## 2026-11-10 · pidió Ana\nLeído: acme/app en `abcdef1` (main), desde el 2026-10-01.\nComparó: piezas, diseño, reglas.\n\n"
    "**Rompe las reglas:** acme/app: el release v9 lo aprobó «x **Rompe las reglas:** sin vigilar», que no acepta ni audita.\n", encoding="utf-8")
rc, o, e = correr("desde", r28, "ventas/app")
ok(json.loads(o)["args"] == "--desde 2026-11-10", "un texto de GitHub dentro de la línea no hace pasar por no vigilada una entrada")

print("Los arreglos de la sexta ronda")
r29 = raiz()
for nombre, f_, que in (("sin commits", lambda x: x.update(commits=[], detalle=[]), "no trae commits"),
                        ("una lista que no llega a antes de la ventana", lambda x: x.update(commits=x["commits"][:2]), "no llega a uno anterior"),
                        ("el primer commit no es la punta", lambda x: x.update(main_sha="e" * 40), "no es la punta")):
    rc, o, d = entrada_de(r29, gh_mod(f_), "--escribir", "--crear")
    ok(que in o and d.get("no_escrito"), f"un JSON a mano {nombre}: no compara ni se guarda")
for nombre, f_ in (("un commit sin fecha", lambda x: x["commits"][1].update(date=None)),
                   ("un detalle sin «files»", lambda x: x["detalle"][1].pop("files")),
                   ("un pull request con «number» que no es número", lambda x: x["pulls"][0].update(number="uno"))):
    rc, o, e = correr("seguimiento", r29, "ventas/app", "--github", gh_mod(f_), "--pidio", "Ana", "--fecha", HOY)
    ok(rc == 2 and "Traceback" not in e and "forma" in e, f"{nombre}: se dice en llano")
r30 = raiz(paso="manual: despliega Beto")
rc, o, d = entrada_de(r30, gh_json(GH))
ok("**Rompe las reglas:** sin comprobar" in o and "Comparó: piezas, diseño." in o, "con otra forma de Paso a Prod no dice «nada» sin haberlo visto")
r31 = raiz(seguimiento="ventas/app/entregables/seguimiento.md")
(r31 / "ventas/app/entregables/seguimiento.md").write_text(
    f"---\nestado: vigente\nactualizado: {HOY}\n---\n\n# Seguimiento\n\n## 2026-11-10 · pidió Ana\nLeído: acme/app en `abcdef1` (main), desde el 2026-11-01.\n"
    "Comparó: piezas, reglas.\n\n**Rompe las reglas:** nada.\n\n## 2026-11-03 · pidió Ana\nLeído: acme/app en `aaaaaaa` (main), desde el 2026-10-01.\n"
    "Comparó: piezas, reglas.\n\n**Rompe las reglas:** sin vigilar: no se leyeron enteros los pasos a Prod.\n\n"
    "## 2026-10-20 · pidió Ana\nLeído: acme/app en `1111111` (main), desde el 2026-10-01.\nComparó: piezas, diseño, reglas.\n\n**Rompe las reglas:** nada.\n", encoding="utf-8")
rc, o, e = correr("desde", r31, "ventas/app")
ok(json.loads(o)["args"] == "--desde 2026-10-20", "una entrada que no comparó el diseño no mueve la ventana")
g31 = json.loads(json.dumps(GH)); g31["desde"] = "2026-10-20"; g31["repos"][0]["commits"].append(c("2" * 40, "2026-10-01", "raíz", parents=0))
g31["repos"][0]["detalle"].append({"sha": "1" * 40, "files": []})
rc, o, d = entrada_de(r31, gh_json(g31))
ok("| P01 · Tablas | F1 | unida |" in o and "no vigiló los pasos a Prod" in o, "un sí que cita una entrada «sin vigilar» no entrega")
ok("Primera lectura" not in o, "un repositorio que ya se leyó no es primera lectura")
pp = r31 / "ventas/app/proyecto.md"; pp.write_text(pp.read_text(encoding="utf-8").replace("Repositorios: acme/app", "Repositorios: acme/app · acme/otro"), encoding="utf-8")
g32 = json.loads(json.dumps(g31)); otro = json.loads(json.dumps(g31["repos"][0])); otro["repo"] = "acme/otro"; g32["repos"].append(otro)
rc, o, d = entrada_de(r31, gh_json(g32))
ok("Primera lectura de acme/otro: lo de antes del 2026-10-20 no se vigiló." in o, "un repositorio nuevo en la sección dice que es su primera lectura")
a8 = audita(gh_mod(lambda x: x.update(truncado=["commits"])))
ok(prop(a8, "R1") == "cumple" and prop(a8, "R6") is None, "con los commits cortados, solo R5 y R6 pierden la propuesta")
def sin_rs_push_off(x):
    x["auditoria"].pop("rulesets"); x["auditoria"]["repo"]["security_and_analysis"] = {"secret_scanning_push_protection": {"status": "disabled"}}
    x["auditoria"]["proteccion"]["required_status_checks"]["contexts"] = ["pruebas"]
a8 = audita(gh_mod(sin_rs_push_off))
ok(prop(a8, "R3") is None, "R3 sin «no cumple» con los rulesets sin leer")
a8 = audita(gh_mod(lambda x: x["auditoria"].update(migraciones={"db/migrations": [{"sha": "abc1234", "date": "2026-11-05", "message": "edita 001"}]})))
ok(any(x["fila"] == "R4" and "db/migrations: `abc1234` edita 001" in x["porque"] for x in a8["preguntar"]), "R4 lleva los commits del mes que tocan las migraciones")

print()
print("Todo bien." if not fallos else f"{fallos} fallo(s).")
sys.exit(1 if fallos else 0)
