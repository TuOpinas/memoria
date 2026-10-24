#!/usr/bin/env python3
"""Prueba las reglas de «Qué hay» de generar_vista.py que no cubre la raíz de prueba (1.22.1, hallazgos 26 y 27 de la
revisión de la 1.21): qué paso nombra una pieza y cómo se resuelve reemplazado_por.

Uso: python3 pruebas/tablero/probar_que_hay.py
"""
import ast, datetime, pathlib, re, sys

GV = pathlib.Path(__file__).resolve().parents[2] / "plugins" / "memoria" / "skills" / "tablero" / "generar_vista.py"
src = GV.read_text(encoding="utf-8")
arbol = ast.parse(src)
ns = {"re": re, "datetime": datetime, "SIN_FECHAS": False}
for n in arbol.body:   # solo lo que hace falta, sin correr el script
    nombres = [t.id for t in getattr(n, "targets", []) if isinstance(t, ast.Name)]
    if (isinstance(n, ast.FunctionDef) and n.name in ("que_hay", "nombra_pieza", "fecha_valida")) or set(nombres) & {"STOP", "PALABRAS_SIG"}:
        exec(compile(ast.Module([n], []), str(GV), "exec"), ns)
fallos = 0


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1


def pieza(archivo, titulo=None, **kw):
    return dict({"archivo": archivo, "nombre": pathlib.Path(archivo).stem, "titulo": titulo, "estado": "borrador", "actualizado": "2026-10-01"}, **kw)


print("Qué hay: qué paso nombra una pieza")
nom = ns["nombra_pieza"]
ok(not nom(pieza("plan.md"))("Usar la plantilla del plan de ventas."), "«plan» suelto, ni dentro de «plantilla», nombra plan.md")
ok(nom(pieza("plan.md"))("Revisar plan.md con Ana.") and nom(pieza("plan.md"))("Revisar el «plan» con Ana."), "con su extensión o entre comillas, sí")
ok(nom(pieza("kit-cuentas.md"))("Actualizar el kit-cuentas antes del lunes.") and not nom(pieza("kit-cuentas.md"))("Actualizar el kit-cuentas-v2."), "un nombre compuesto, como palabra entera")
pdoc = {"pasos": [{"texto": "Mandar la propuesta al cliente nuevo.", "naturaleza": "x"},
                  {"texto": "Decidir el precio de la fase 2.", "naturaleza": "x"}],
        "entregables": []}
taller = [pieza("nota-a.md", "Propuesta de precios para el cliente grande"), pieza("nota-b.md", "Precio de la fase 2")]
_, det = ns["que_hay"](pdoc, [dict(t, tipo="taller") for t in taller], [], "ventas/cuentas")
pz = {p["archivo"]: p for p in det["piezas"]}
ok("pasos" not in pz["nota-a.md"], "dos palabras sueltas en común ({propuesta, cliente}) ya no bastan con un título de más")
ok(pz["nota-b.md"].get("pasos") == ["Decidir el precio de la fase 2."], "un título de dos palabras significativas se nombra con las dos")

print("Qué hay: reemplazado_por por ruta")
ents = [pieza("v1.md", "Versión uno", estado="reemplazado", reemplazado_por="ventas/cuentas/entregables/v2.md"),
        pieza("v2.md", "Versión dos", estado="reemplazado", reemplazado_por="entregables/v3.md"),
        pieza("v3.md", "Versión tres", estado="vigente"),
        pieza("viejo.md", "Viejo", estado="reemplazado", reemplazado_por="otra/cosa/entregables/v3.md"),
        pieza("doble.md", "Doble", estado="reemplazado", reemplazado_por="nota.md")]
tall = [pieza("nota.md", "Nota del taller"), pieza("previa.md", "Previa", estado="reemplazado", reemplazado_por="taller/nota.md")]
ents.append(pieza("nota.md", "Nota entregable", estado="vigente"))
res, det = ns["que_hay"]({"pasos": [], "entregables": ents}, tall, [], "ventas/cuentas")
cad = [[n["titulo"] for n in c["pasos"]] for c in det["trayectoria"]]
ok(["Versión uno", "Versión dos", "Versión tres"] in cad, f"la cadena se arma con la ruta desde la raíz y desde el proyecto ({cad})")
ok(["Previa", "Nota del taller"] in cad, "taller/nota.md apunta a la del taller, no al entregable del mismo nombre")
ok(res.get("reemplazos_sin_resolver") == 2, f"los de otro proyecto y el nombre ambiguo no resuelven, y se cuentan ({res.get('reemplazos_sin_resolver')})")

print("\n" + ("Todo bien." if not fallos else f"{fallos} fallo(s)."))
sys.exit(1 if fallos else 0)
