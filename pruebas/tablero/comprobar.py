#!/usr/bin/env python3
"""Comprueba lo que genera generar_vista.py sobre la raíz inventada de raiz/.
Uso: comprobar.py <salida-publico> <salida-completo>. Sale con 1 si algo falla."""
import json, glob, os, sys

def cargar(d):
    D = {}
    for f in glob.glob(os.path.join(d, "*", "*.json")):
        D.setdefault(os.path.basename(os.path.dirname(f)), {})[os.path.basename(f)[:-5]] = json.load(open(f, encoding="utf-8"))
    return D

pub, com = cargar(sys.argv[1]), cargar(sys.argv[2])
texto = lambda D: json.dumps(D, ensure_ascii=False)
fallos = []
def ok(cond, que):
    print(("  bien  " if cond else "  FALLA ") + que)
    if not cond: fallos.append(que)

print("Lo restringido")
ok("SECRETO-PRECIOS" not in texto(pub), "público: nada del proyecto que empieza su línea por «restringido»")
ok("SECRETO-NOMINA" not in texto(pub), "público: nada del área marcada «Restringida»")
ok("SECRETO-PRECIOS" in texto(com) and "SECRETO-NOMINA" in texto(com), "completo: sí sale lo que la cuenta lee")
ok("SECRETO-RESTRINGIDO" not in texto(pub) + texto(com), "ningún modo lee las carpetas restringido/")
ok(pub["proyectos"]["ventas--cuentas"]["legible"], "público: un proyecto que solo menciona algo restringido sale entero")
ok(all(set(s) <= {"fecha", "titulo"} for p in pub["proyectos"].values() for s in p.get("sesiones", [])), "público: de las sesiones, solo fecha y título")
ok("AVANCE-CUENTAS" in texto(com) and "AVANCE-CUENTAS" not in texto(pub), "completo trae la bitácora entera; público no")
ok(pub["meta"]["estado"]["modo"] == "publico" and com["meta"]["estado"]["modo"] == "completo", "cada salida dice su modo")

print("Plazos")
pasos = {s["texto"][:30]: s for s in com["proyectos"]["ventas--cuentas"]["pasos"]}
def paso(inicio): return next(v for k, v in pasos.items() if k.startswith(inicio))
ok(paso("Llamar a Cliente Uno")["fecha"] == "2026-10-06", "«antes del» es plazo")
ok(paso("Confirmar las decisiones")["fecha"] is None, "«registradas el … y el …» no es plazo")
ok(paso("Tras la publicación")["fecha"] is None, "«tras la publicación del …:» no es plazo")
rev = paso("Revisión trimestral")
ok(rev["fecha"] is None and rev.get("revisar") == "2026-10-01", "una revisión periódica lleva fecha de revisión, no de vencimiento")
ok(paso("Sostener")["naturaleza"] == "rutina", "«Sostener…» es rutina")
ok(paso("Decidir")["naturaleza"] == "decision", "«Decidir…» es decisión")
ok(paso("Esperar")["naturaleza"] == "espera", "«Esperar…» es espera")

print("Entregables y decisiones")
ents = {e["nombre"]: e for e in com["proyectos"]["ventas--cuentas"]["entregables"]}
ok(ents["kit-cuentas"]["titulo"] == "Kit para preparar una cuenta", "el título sale del cuerpo")
ok(ents["kit-cuentas"]["descripcion"].startswith("guía para preparar"), "la descripción sale del índice del área aunque el nombre lleve guiones")
ok(ents["kit-cuentas"].get("basado_en", [])[:1] == ["ventas/cuentas/entregables/propuesta-base.md"], "basado_en se lee como lista")
ok(ents["propuesta-base"].get("basado_en") == [], "basado_en vacío en línea («[]»)")
decs = com["proyectos"]["ventas--cuentas"]["decisiones"]
ok(decs[0].get("por_confirmar") is True and not decs[1].get("por_confirmar"), "se marca la decisión pendiente de confirmar, y solo esa")
ok(com["proyectos"]["operacion--soporte"]["estado_cabecera"] == "borrador", "el estado de proyecto.md llega a la página")

print("Trabajo sin sesión")
ss = com["proyectos"]["ventas--cuentas"].get("sin_sesion")
ok(bool(ss) and ss.get("donde") == {"entregables": 1}, "un entregable tocado después de la última sesión se avisa, y solo ese")
ok(not com["proyectos"]["operacion--soporte"].get("sin_sesion"), "un proyecto sin cambios desde su última sesión no se avisa")
ok(not pub["proyectos"]["ventas--precios"].get("sin_sesion"), "público: de un proyecto restringido no se dice nada")

print("\n" + ("Todo bien." if not fallos else f"{len(fallos)} fallo(s)."))
sys.exit(1 if fallos else 0)
