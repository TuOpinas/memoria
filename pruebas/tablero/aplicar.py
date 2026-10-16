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
ok({x["id"] for x in r1["sin_match"]} == {"f2", "f3"}, "un cambio sin paso o sin proyecto no rompe nada: queda sin aplicar")
ok(r1["para_sesion"] and r1["para_sesion"][0].get("campo") == "paso", "las correcciones llegan a la sesión con su campo")
ok({x["id"] for x in r1["para_su_dueno"]} == {"o1", "o2"} and r1["mis_areas"] == ["archivo", "futura", "operacion", "ventas"], "lo de un área de otra cuenta no se toca y se devuelve aparte")
r2 = corre("--cuenta", "Ana@Ejemplo.test")
ok([x["id"] for x in r2["aplicados"]] == ["f1"] and r2["aplicados"][0]["detalle"] == "ya estaba aplicada", "si una corrida anterior ya la aplicó, se da por aplicada")
print("\n" + ("Todo bien." if not fallos else f"{len(fallos)} fallo(s)."))
sys.exit(1 if fallos else 0)
