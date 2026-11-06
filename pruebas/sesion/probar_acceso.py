#!/usr/bin/env python3
"""Si un área está restringida lo decide una sola regla, la de context_core (la lectura de abrir.py de la 1.25.1), en la
apertura, el tablero, permisos.py y la migración; verificar.sh solo lee la palabra de «Acceso» (revisión de la 1.25.2, hallazgo 10). Con «Acceso:
Restringidas» el tablero de la 1.25.2 daba el área abierta y abrir.py cerrada: ahora todos la leen restringida.

Uso: python3 pruebas/sesion/probar_acceso.py
"""
import json, pathlib, re, subprocess, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1])); from comun import raiz_migrada, raiz_125
PL = pathlib.Path(__file__).resolve().parents[2] / "plugins" / "memoria"
fallos = 0
def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1
def correr(*a):
    return subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True).stdout
def con_acceso(raiz, area, valor):
    g = raiz / "guia.md"
    t = re.sub(r"(?m)^(\| `" + area + r"/` \|.*\| )(?:Restringida|Abierta)( \|)$", lambda m: m.group(1) + valor + m.group(2), g.read_text(encoding="utf-8"))
    g.write_text(t, encoding="utf-8")
def areas_del_tablero(salida):
    out = {}
    def ver(x):
        if isinstance(x, dict):
            if isinstance(x.get("slug"), str) and "restringido" in x and "lectores" in x:
                out[x["slug"]] = x["restringido"]
            for v in x.values():
                ver(v)
        elif isinstance(x, list):
            for v in x:
                ver(v)
    for f in salida.rglob("*.json"):
        ver(json.loads(f.read_text(encoding="utf-8")))
    return out

print("Una sola regla de acceso a un área")
for forma, (raiz, _) in (("1.22", raiz_migrada()), ("1.25", raiz_125())):
    con_acceso(raiz, "personas", "Restringidas")
    con_acceso(raiz, "operacion", "Abiertas")
    o = correr(PL / "skills/sesion/abrir.py", raiz, "--cuenta", "carla@ejemplo.test", "--sin-fechas")
    ok(re.search(r"^- personas/ · restringida", o, re.M) and not re.search(r"^- operacion/ · restringida", o, re.M), f"{forma}: la apertura lee «Restringidas» cerrada y «Abiertas» abierta")
    s = pathlib.Path(tempfile.mkdtemp())
    correr(PL / "skills/tablero/generar_vista.py", raiz, s, "--sin-fechas")
    a = areas_del_tablero(s)
    ok(a.get("personas") is True and a.get("operacion") is False, f"{forma}: el tablero también (hasta la 1.25.2 daba «Restringidas» abierta)")
    o = correr(PL / "skills/sesion/permisos.py", raiz, "--plan")
    ok("área personas/ (declarada restringida)" in o and "área operacion/ (declarada" not in o, f"{forma}: permisos.py también")
# 1.25, «Acceso» que no dice ni Abierta ni Restringida: falla cerrado en la apertura y el tablero; verificar.sh pide arreglar
# la celda y no toma «Todo el equipo» por un nombre
raiz, _ = raiz_125()
con_acceso(raiz, "operacion", "Restr.")
o = correr(PL / "skills/sesion/abrir.py", raiz, "--cuenta", "carla@ejemplo.test", "--sin-fechas")
ok(re.search(r"^- operacion/ · restringida", o, re.M), "1.25: un «Acceso» que no se entiende lee el área restringida en la apertura")
s = pathlib.Path(tempfile.mkdtemp()); correr(PL / "skills/tablero/generar_vista.py", raiz, s, "--sin-fechas")
ok(areas_del_tablero(s).get("operacion") is True, "y en el tablero")
v = subprocess.run(["bash", str(PL / "verificar.sh"), str(raiz)], capture_output=True, text=True).stdout
ok(re.search(r"columna Acceso sin «Abierta» ni «Restringida»\s+operacion", v) and "«Todo el equipo», en «Quién la lee»" not in v,
   "verificar.sh dice que «Acceso» no se entiende, sin tomar «Todo el equipo» por un nombre")
print("\n" + ("Todo bien." if not fallos else f"{fallos} fallo(s)."))
sys.exit(1 if fallos else 0)
