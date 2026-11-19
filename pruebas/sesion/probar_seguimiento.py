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
    p = subprocess.run([sys.executable, str(SEG), *map(str, a)], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def raiz(seguimiento="por crear", paso="release de GitHub", construye="Ana Prueba (ana@ejemplo.test, @ana)"):
    r = pathlib.Path(tempfile.mkdtemp()) / "raiz"
    e = r / "ventas/app/entregables"
    e.mkdir(parents=True)
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
Acepta: Beto Prueba (beto@ejemplo.test, @beto)
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


GH = {"leido": "gh", "hoy": HOY, "desde": "2026-11-01", "repos": [{
    "repo": "acme/app", "rama": "main", "main_sha": "f" * 40,
    "pulls": [
        {"number": 1, "title": "P01 · tablas", "state": "merged", "author": "ana", "bot": False, "merge_commit": "a" * 40, "merged_at": "2026-11-02T10:00:00Z"},
        {"number": 2, "title": "P02 · api", "state": "merged", "author": "ana", "bot": False, "merge_commit": "c" * 40, "merged_at": "2026-11-10T10:00:00Z"},
        {"number": 3, "title": "P02 · arreglo", "state": "open", "author": "ana", "bot": False, "merge_commit": "", "merged_at": ""},
        {"number": 4, "title": "Arregla el README", "state": "merged", "author": "ana", "bot": False, "merge_commit": "d" * 40, "merged_at": "2026-11-12T10:00:00Z"},
        {"number": 5, "title": "Bump x", "state": "merged", "author": "dependabot[bot]", "bot": True, "merge_commit": "e" * 40, "merged_at": "2026-11-13T10:00:00Z"},
        {"number": 6, "title": "P03 · abandonado", "state": "closed", "author": "ana", "bot": False, "merge_commit": "", "merged_at": ""},
    ],
    "commits": [c("f" * 40, "2026-11-15", "directo a main"), c("e" * 40, "2026-11-13", "Bump x"),
                c("d" * 40, "2026-11-12", "Arregla el README", parents=2), c("c" * 40, "2026-11-10", "P02 · api"),
                c("b" * 40, "2026-11-05", "release"), c("a" * 40, "2026-11-02", "P01 · tablas")],
    "detalle": [
        {"sha": "f" * 40, "files": [{"filename": "migrations/001_init.sql", "status": "modified", "patch": "+ALTER TABLE x;"},
                                    {"filename": "CLAUDE.md", "status": "modified", "patch": "+regla"}]},
        {"sha": "c" * 40, "files": [{"filename": "api/pedidos.py", "status": "added", "patch": "+def crear_orden(order_id):\n+    pass"},
                                    {"filename": "worker/cola.py", "status": "added", "patch": "+x = 1"},
                                    {"filename": "migrations/002_facturas.sql", "status": "added",
                                     "patch": "+CREATE TABLE facturas (id int);\n+create table if not exists public.\"pedidos\" (id int);"}]},
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


def gh_json(d):
    p = pathlib.Path(tempfile.mkdtemp()) / "gh.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    return p


print("El seguimiento")
r = raiz()
g = gh_json(GH)
rc, o, e = correr("seguimiento", r, "ventas/app", "--github", g, "--pidio", "Beto Prueba", "--fecha", HOY)
ok(rc == 0, "corre" + ("" if rc == 0 else ": " + e))
ok(o.startswith(f"## {HOY} · pidió Beto Prueba\nLeído: acme/app en `fffffff` (main), desde el 2026-11-01."), "cabecera con quién, el commit leído y desde cuándo")
ok("Comparó: piezas, diseño, reglas." in o, "dice qué pudo comparar")
ok("Paso a Prod: release de GitHub" in o, "dice qué forma de «Paso a Prod» entendió")
ok("| P01 · Tablas | F1 | entregada | acme/app#1 |" in o, "P01, dentro del último release con «Aprobó:», entregada")
ok("| P02 · API | F1 | en curso | acme/app#2, acme/app#3 |" in o, "P02 con un arreglo abierto: en curso (manda el menos avanzado)")
ok("| P03 · Vista | F1 | pendiente | — |" in o, "P03 con un pull request cerrado sin unir: pendiente")
ok("acme/app#4 «Arregla el README»" in o and "#5" not in o.split("**Fuera del plan:**")[1].split("\n")[0], "fuera del plan, sin los bots")
ok("la tabla «facturas»" in o and "«pedidos»" not in o, "una tabla nueva que no está en Datos (el plural de una entidad sí cuenta)")
ok("código nuevo en acme/app:worker" in o and "código nuevo en acme/app:api" not in o and "código nuevo en acme/app:migrations" not in o,
   "código nuevo fuera de los «Dónde vive», sin contar las migraciones, que se comparan con Datos")
ok("usa «orden»" in o and "usa «order»" in o and "«Pedido»" in o, "nombres que el diseño dice que no son un concepto")
ok("`fffffff` en la rama principal sin pull request" in o, "un commit directo a main")
ok("acme/app#4 se unió sin squash" in o, "una unión sin squash")
ok("la migración ya unida migrations/001_init.sql se editó" in o, "una migración unida que cambió")
ok("cambió CLAUDE.md" in o, "un cambio al CLAUDE.md")
ok("el release v2 (`ccccccc`) no tiene «Aprobó:»" in o, "un paso a Prod sin sí")
ok("Ana Prueba aprobó v1 (acme/app), que lleva su #1" in o, "un sí que se dio quien construyó")
datos = json.loads(o.split("=== DATOS\n")[1])
ok(datos["fuera_del_plan"] == ["acme/app#4"], "DATOS trae lo fuera del plan")

print("Quién construyó es el autor, no cualquiera de «Construye»")
r2 = raiz(construye="Ana Prueba (ana@ejemplo.test, @otra) · Carla Prueba (carla@ejemplo.test, @ana)")
rc, o, e = correr("seguimiento", r2, "ventas/app", "--github", g, "--pidio", "Beto Prueba", "--fecha", HOY)
ok("Pasos a Prod que aprobó quien construyó:** ninguno." in o, "Ana aprobó, pero el #1 es de @ana, que es Carla")

print("Escribir: crea el seguimiento, que nace vigente, y la entrada siguiente va arriba")
rc, o, e = correr("seguimiento", r, "ventas/app", "--github", g, "--pidio", "Beto Prueba", "--fecha", HOY, "--escribir")
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
a = json.loads(o)
co = a["comprobado"]
ok(co["R1"]["acme/app"]["estado"] == "cumple", "R1: el ruleset exige pull request sin excepciones y solo squash")
ok(co["R2"]["acme/app"]["estado"] == "no cumple" and "Do not allow bypassing" in co["R2"]["acme/app"]["evidencia"],
   "R2: comprobaciones obligatorias que un administrador se puede saltar")
ok(co["R3"]["acme/app"]["estado"] == "cumple", "R3: comprobación de secretos y protección al subir")
ok(co["R6"]["acme/app"]["estado"] == "no cumple" and "#4" in co["R6"]["acme/app"]["evidencia"], "R6: un pull request unido sin pieza")
ok({x["fila"] for x in a["preguntar"]} >= {"PL1", "PL2", "PL3", "PL7", "R4", "R5", "R7"}, "lo que no se pudo, a preguntar")
ok(any(x["fila"] == "PL1" and "403" in x["porque"] for x in a["preguntar"]), "con el motivo")
ok(a["si_propio"] and a["si_propio"][0]["pr"] == 1, "los síes que alguien se dio a sí mismo")

print("Aplicar los estados")
conf = r / "ventas/app/entregables/repositorios.md"
est = pathlib.Path(tempfile.mkdtemp()) / "e.json"
est.write_text(json.dumps({"R1": {"acme/app": "cumple"}, "R4": {"acme/app": "no aplica"}, "R2": {"acme/app": "no cumple"}}), encoding="utf-8")
antes = conf.read_text(encoding="utf-8")
rc, o, e = correr("aplicar", conf, est, "--fecha", HOY)
t = conf.read_text(encoding="utf-8")
ok(rc == 0 and f"| cumple · {HOY} |" in t and "| no aplica |" in t and f"| no cumple · {HOY} |" in t, "escribe cada estado, con fecha salvo «no aplica»")
_dif = [(x, y) for x, y in zip(antes.split("\n"), t.split("\n")) if x != y]
ok(f"actualizado: {HOY}" in t and len(antes.split("\n")) == len(t.split("\n")) and len(_dif) == 4,
   "pone la fecha de la cabecera y cambia solo las tres filas")
est.write_text(json.dumps({"R1": {"acme/app": "regular"}}), encoding="utf-8")
rc, o, e = correr("aplicar", conf, est, "--fecha", HOY)
ok(rc != 0 and "no es cumple" in e, "un estado que no es de los cuatro se rechaza")
plat = r / "ventas/app/entregables/plataforma.md"
est.write_text(json.dumps({"PL1": "cumple", "PL3": "excepción"}), encoding="utf-8")
rc, o, e = correr("aplicar", plat, est, "--fecha", HOY)
t = plat.read_text(encoding="utf-8")
ok(rc == 0 and re.search(r"^\| PL1 \|.*\| cumple · " + HOY + r" \|$", t, re.M) and re.search(r"^\| PL3 \|.*\| excepción \|$", t, re.M),
   "en la de plataforma, la columna Estado")

print()
print("Todo bien." if not fallos else f"{fallos} fallo(s).")
sys.exit(1 if fallos else 0)
