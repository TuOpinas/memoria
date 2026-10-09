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
]), encoding="utf-8")
corre = lambda: json.loads(subprocess.run([sys.executable, SCRIPT, str(RAIZ), str(cola)], capture_output=True, text=True, check=True).stdout)
fallos = []
def ok(c, q):
    print(("  bien  " if c else "  FALLA ") + q)
    if not c: fallos.append(q)
print("Aplicar la cola")
r1 = corre(); pm = (RAIZ / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8")
ok([x["id"] for x in r1["aplicados"]] == ["f1"] and "antes del 2026-10-09" in pm, "una fecha se aplica en la línea de su paso")
ok("actualizado: 2026-10-01" in pm, "aplicar una fecha no mueve «actualizado»")
ok({x["id"] for x in r1["sin_match"]} == {"f2", "f3"}, "un cambio sin paso o sin proyecto no rompe nada: queda sin aplicar")
ok(r1["para_sesion"] and r1["para_sesion"][0].get("campo") == "paso", "las correcciones llegan a la sesión con su campo")
r2 = corre()
ok([x["id"] for x in r2["aplicados"]] == ["f1"] and r2["aplicados"][0]["detalle"] == "ya estaba aplicada", "si una corrida anterior ya la aplicó, se da por aplicada")
print("\n" + ("Todo bien." if not fallos else f"{len(fallos)} fallo(s)."))
sys.exit(1 if fallos else 0)
