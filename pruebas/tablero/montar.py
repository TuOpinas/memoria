#!/usr/bin/env python3
"""Monta una página de prueba: la página del tablero con una base falsa que trae lo generado.
Uso: montar.py <vista.html> <salida-del-generador> <página.html>"""
import json, glob, os, sys
vista, salida, pagina = sys.argv[1:4]
D = {}
for f in glob.glob(os.path.join(salida, "*", "*.json")):
    D.setdefault(os.path.basename(os.path.dirname(f)), {})[os.path.basename(f)[:-5]] = json.load(open(f, encoding="utf-8"))
# lo que en la vida real escriben la página y la tarea: dos cambios en la cola y un «por dónde empezar»
D["cambios"] = {
    "c1": {"tipo": "nota", "proyecto": "ventas--cuentas", "nota": "Cliente Uno pidió mover la llamada", "creado": "2026-10-02T10:00:00-06:00"},
    "c2": {"tipo": "hecho", "proyecto": "ventas--cuentas", "paso": "Preparar el contrato de Cliente Uno con la plantilla de propuesta.", "nota": None, "creado": "2026-10-02T11:00:00-06:00"},
}
D["enfoque"] = {"actual": {"generado": "2026-10-02", "criterios": ["prioridad del área", "cliente o dinero", "desbloquea"], "grupos": [
    {"titulo": "Cerrar Cliente Uno", "razon": "Es la primera prioridad de ventas y toca dinero. La sesión decide.", "sesion": "abre sesión en ventas/cuentas y cierra la propuesta de Cliente Uno",
     "pasos": [{"proyecto": "ventas--cuentas", "paso": "Llamar a Cliente Uno"}, {"proyecto": "operacion--soporte", "paso": "Abrir su canal de soporte"}]}]}}
pre = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "base-falsa.js"), encoding="utf-8").read().replace("__DATA__", json.dumps(D, ensure_ascii=False))
open(pagina, "w", encoding="utf-8").write("<script>\n" + pre + "\n</script>\n" + open(vista, encoding="utf-8").read())
