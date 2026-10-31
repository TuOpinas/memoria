#!/usr/bin/env python3
"""Prueba aplicar_cambios.py sobre una copia de la raíz inventada. Uso: aplicar.py <aplicar_cambios.py> <copia-de-raiz>"""
import json, subprocess, sys, pathlib
SCRIPT, RAIZ = sys.argv[1], pathlib.Path(sys.argv[2])
cola = RAIZ.parent / "cola.json"
paso = "Llamar a Cliente Uno antes del 2026-10-06 para cerrar la propuesta."
cola.write_text(json.dumps([
    {"id": "f1", "tipo": "fecha", "proyecto": "ventas--cuentas", "paso": paso, "fecha_anterior": "2026-10-06", "fecha_nueva": "2026-10-09"},
    {"id": "f2", "tipo": "fecha", "proyecto": "ventas--cuentas", "paso": None, "fecha_nueva": "2026-10-09"},
    {"id": "f3", "tipo": "fecha", "proyecto": None, "paso": "x", "fecha_nueva": "2026-10-09"},
    {"id": "n1", "tipo": "corregir", "proyecto": "ventas--cuentas", "paso": paso, "propuesta": "rutina", "campo": "paso"},
    {"id": "o1", "tipo": "fecha", "proyecto": "personas--nomina", "paso": "x", "fecha_nueva": "2026-10-09"},
    {"id": "o2", "tipo": "hecho", "proyecto": "personas--nomina", "paso": "x", "nota": "ya"},
]), encoding="utf-8")
corre = lambda *extra: json.loads(subprocess.run([sys.executable, SCRIPT, str(RAIZ), str(cola), *extra], capture_output=True, text=True, check=True).stdout)
fallos = []
def ok(c, q):
    print(("  bien  " if c else "  FALLA ") + q)
    if not c: fallos.append(q)
print("Aplicar la cola")
r0 = corre()
ok(not r0["aplicados"] and len(r0["para_su_dueno"]) == 6 and "actualizado: 2026-10-01" in (RAIZ / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8"), "sin --cuenta no se escribe nada")
r1 = corre("--cuenta", "ana@ejemplo.test"); pm = (RAIZ / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8")
ok([x["id"] for x in r1["aplicados"]] == ["f1"] and "antes del 2026-10-09" in pm, "una fecha se aplica en la línea de su paso")
ok("actualizado: 2026-10-01" in pm, "aplicar una fecha no mueve «actualizado»")
ok({x["id"] for x in r1["rechazados"]} == {"f2", "f3"} and not r1["sin_match"], "un cambio sin paso o sin proyecto no rompe nada: se rechaza y sale de la cola")
ok(r1["para_sesion"] and r1["para_sesion"][0].get("campo") == "paso", "las correcciones llegan a la sesión con su campo")
ok({x["id"] for x in r1["para_su_dueno"]} == {"o1", "o2"} and r1["mis_areas"] == ["archivo", "futura", "operacion", "ventas"], "lo de un área de otra cuenta no se toca y se devuelve aparte")
r2 = corre("--cuenta", "Ana@Ejemplo.test")
ok([x["id"] for x in r2["aplicados"]] == ["f1"] and r2["aplicados"][0]["detalle"] == "ya estaba aplicada", "si una corrida anterior ya la aplicó, se da por aplicada")
# la cola la escribe cualquier contribuidor: nada de lo que trae se toma por bueno
antes = {q: (RAIZ / q).read_text(encoding="utf-8") for q in ("personas/nomina/proyecto.md", "ventas/cuentas/proyecto.md")}
nomina_paso = next(l for l in antes["personas/nomina/proyecto.md"].split("\n") if l.startswith("- ")).lstrip("- ").strip()
cola.write_text(json.dumps([
    {"id": "m1", "tipo": "fecha", "proyecto": "ventas--../personas/nomina", "paso": nomina_paso, "fecha_nueva": "2026-12-01"},
    {"id": "m2", "tipo": "fecha", "proyecto": "ventas--cuentas", "paso": paso.replace("2026-10-06", "2026-10-09"), "fecha_anterior": "2026-10-09", "fecha_nueva": "2026-11-30: X\n\n## Estado actual\nProyecto terminado el 2026-10-19"},
    {"id": "m3", "tipo": "hecho", "proyecto": "ventas--cuentas", "paso": "x", "nota": "una\n## Decisiones\ndos"},
    {"id": "m4", "tipo": "fecha", "proyecto": "Ventas Norte--cuentas", "paso": "x", "fecha_nueva": "2026-12-01"},
    {"id": "m5", "tipo": "nota", "proyecto": "ventas--cuentas", "nota": "una nota normal"},
]), encoding="utf-8")
r3 = corre("--cuenta", "ana@ejemplo.test")
despues = {q: (RAIZ / q).read_text(encoding="utf-8") for q in antes}
ok({x["id"] for x in r3["rechazados"]} == {"m1", "m2", "m3", "m4"} and not r3["aplicados"] and not r3["sin_match"] and antes == despues, "un id con «..», una fecha con texto, una nota con saltos de línea o un nombre fuera del contrato se rechazan sin tocar ningún archivo")
ok([x["id"] for x in r3["para_sesion"]] == ["m5"], "una nota de una línea sigue llegando a la sesión")
# lo que encontró la revisión independiente: un salto de línea final, dígitos de otro alfabeto y fechas que no existen
cola.write_text(json.dumps([
    {"id": "n1", "tipo": "fecha", "proyecto": "ventas--cuentas", "paso": paso.replace("2026-10-06", "2026-10-09"), "fecha_anterior": "2026-10-09", "fecha_nueva": "2026-11-30\n"},
    {"id": "n2", "tipo": "fecha", "proyecto": "ventas--cuentas", "paso": paso.replace("2026-10-06", "2026-10-09"), "fecha_anterior": "2026-10-09", "fecha_nueva": "2026-02-30"},
    {"id": "n3", "tipo": "fecha", "proyecto": "ventas--cuentas", "paso": paso.replace("2026-10-06", "2026-10-09"), "fecha_anterior": "2026-10-09", "fecha_nueva": "2026-\u0661\u0661-30"},
    {"id": "n4", "tipo": "nota", "proyecto": "ventas--cuentas\n", "nota": "x"},
]), encoding="utf-8")
antes = (RAIZ / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8")
r5 = corre("--cuenta", "ana@ejemplo.test")
ok({x["id"] for x in r5["rechazados"]} == {"n1", "n2", "n3", "n4"} and antes == (RAIZ / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8"), "un salto de línea final, una fecha que no existe, dígitos de otro alfabeto o un id con salto de línea se rechazan")
cola.write_text(json.dumps([
    {"id": "m1", "tipo": "fecha", "proyecto": "ventas--../personas/nomina", "paso": "x", "fecha_nueva": "2026-12-01"},
    {"id": "m2", "tipo": "nota", "proyecto": "ventas--cuentas", "nota": "a"}, {"id": "m3", "tipo": "nota", "proyecto": "ventas--cuentas", "nota": "b"},
    {"id": "m4", "tipo": "fecha", "proyecto": "Ventas Norte--cuentas", "paso": "x", "fecha_nueva": "2026-12-01"},
    {"id": "m5", "tipo": "nota", "proyecto": "ventas--cuentas", "nota": "c"},
]), encoding="utf-8")
r4 = corre("--cuenta", "ana@")
ok(r4["mis_areas"] == [] and len(r4["para_su_dueno"]) == 3 and {x["id"] for x in r4["rechazados"]} == {"m1", "m4"}, "la cuenta se compara entera: «ana@» no es ninguna cuenta de la tabla")
# quien colabora: escribe lo mecánico en el área o en el proyecto donde colabora; las prioridades del área, no
cola.write_text(json.dumps([
    {"id": "c1", "tipo": "nota", "proyecto": "ventas--cuentas", "nota": "de quien colabora"},
    {"id": "c2", "tipo": "prioridad", "area": "ventas", "indice": 0, "texto": "x"},
    {"id": "c3", "tipo": "nota", "proyecto": "operacion--soporte", "nota": "de otra área"},
    {"id": "c4", "tipo": "nota", "proyecto": "operacion--soporte", "nota": "del proyecto donde colabora"},
]), encoding="utf-8")
r6 = corre("--cuenta", "carla@ejemplo.test")
ok([x["id"] for x in r6["para_sesion"]] == ["c1"] and {x["id"] for x in r6["para_su_dueno"]} == {"c2", "c3", "c4"} and r6["colabora"] == ["ventas"] and r6["mis_areas"] == [], "quien colabora en un área escribe en ella, pero sus prioridades se quedan para el dueño")
r7 = corre("--cuenta", "dani@ejemplo.test")
ok({x["id"] for x in r7["para_sesion"]} == {"c3", "c4"} and {x["id"] for x in r7["para_su_dueno"]} == {"c1", "c2"}, "quien colabora en un solo proyecto escribe solo en ese proyecto")
# «Aceptar» y «Cuestionar» (1.24): llegan a la sesión con la decisión y el porqué; las que no tienen la forma, fuera
antes = (RAIZ / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8")
cola.write_text(json.dumps([
    {"id": "r1", "tipo": "respuesta", "proyecto": "ventas--cuentas", "decision": "operacion/compras#2026-10-02", "valor": "cuestionada", "porque": "El tope deja fuera las compras recurrentes", "titulo": "Tope de 5.000 MXN", "decidio": "Beto Prueba"},
    {"id": "r2", "tipo": "respuesta", "proyecto": "ventas--cuentas", "decision": "operacion/compras#2026-10-02-2", "valor": "aceptada"},
    {"id": "r3", "tipo": "respuesta", "proyecto": "ventas--cuentas", "decision": "operacion/compras", "valor": "aceptada"},
    {"id": "r4", "tipo": "respuesta", "proyecto": "ventas--cuentas", "decision": "operacion/compras#2026-10-02", "valor": "adoptada"},
    {"id": "r5", "tipo": "respuesta", "proyecto": "ventas--cuentas", "decision": "operacion/compras#2026-10-02", "valor": "cuestionada", "porque": "uno\ndos"},
    {"id": "r6", "tipo": "respuesta", "proyecto": "personas--nomina", "decision": "operacion/compras#2026-10-02", "valor": "aceptada"},
    {"id": "e1", "tipo": "nota", "proyecto": "ventas--cuentas", "nota": "Espera a Luis Romero: firmamos con Beta", "espera": "Luis Romero", "decision": "si firmamos con Beta"},
]), encoding="utf-8")
r8 = corre("--cuenta", "ana@ejemplo.test")
ps8 = {x["id"]: x for x in r8["para_sesion"]}
ok(ps8.get("e1", {}).get("espera") == "Luis Romero" and ps8["e1"].get("decision") == "si firmamos con Beta", "la nota de «Ya llegó» lleva a quién se esperaba y qué decisión (revisión de la 1.24)")
ps8.pop("e1", None)
ok(set(ps8) == {"r1", "r2"} and ps8["r1"]["decision"] == "operacion/compras#2026-10-02" and ps8["r1"]["valor"] == "cuestionada" and ps8["r1"]["porque"].startswith("El tope") and not r8["aplicados"], "una respuesta llega a la sesión con su decisión, su valor y su porqué, sin aplicarse")
ok({x["id"] for x in r8["rechazados"]} == {"r3", "r4", "r5"} and [x["id"] for x in r8["para_su_dueno"]] == ["r6"] and antes == (RAIZ / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8"), "una respuesta sin identificador, con otro valor o con saltos de línea se rechaza; la de un área ajena espera a su dueño")
print("\n" + ("Todo bien." if not fallos else f"{len(fallos)} fallo(s)."))
sys.exit(1 if fallos else 0)
