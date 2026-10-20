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
ok("@ejemplo.test" not in texto(pub), "público: ningún correo, ni de dueños ni de quien colabora")
ok(com["areas"]["ventas"].get("colaboran") == ["carla@ejemplo.test"] and pub["areas"]["ventas"].get("colaboran") == [], "quien colabora en un área: su cuenta en el completo, nada en el público")
ok(pub["proyectos"]["operacion--soporte"].get("colaboran") == ["Dani Prueba"] and "dani@" not in texto(com) and "quien" not in pub["proyectos"]["operacion--soporte"], "quien colabora en un proyecto: su nombre, sin su cuenta, y sin la sección en bruto")
ok(pub["proyectos"]["ventas--cuentas"]["legible"], "público: un proyecto que solo menciona algo restringido sale entero")
ok(all(set(s) <= {"fecha", "titulo", "trabajamos"} for p in pub["proyectos"].values() for s in p.get("sesiones", [])) and any(s.get("trabajamos") for p in pub["proyectos"].values() for s in p.get("sesiones", [])), "público: de las sesiones, solo su cabecera (fecha, título y «Trabajamos en»), nunca «Avances» ni «Pendiente»")
ok("SECRETO-CUERPO" not in json.dumps(pub, ensure_ascii=False) and "SECRETO-PENDIENTE" not in json.dumps(pub, ensure_ascii=False) and "SECRETO-CUERPO" in json.dumps(com, ensure_ascii=False), "público: una entrada sin «Avances:» no arrastra su cuerpo detrás de «Trabajamos en»")
ok("AVANCE-CUENTAS" in texto(com) and "AVANCE-CUENTAS" not in texto(pub), "completo trae la bitácora entera; público no")
ok(pub["meta"]["estado"]["modo"] == "publico" and com["meta"]["estado"]["modo"] == "completo", "cada salida dice su modo")
ok("SECRETO-MARGENES" not in texto(pub), "público: un proyecto restringido escrito con guion medio en el índice no se publica")
ok("SECRETO-OCULTO" not in texto(pub) and "SECRETO-OCULTO" in texto(com), "público: un proyecto que no está en el índice del área no se publica; completo sí")
ok(all("raiz" not in D["meta"]["estado"] for D in (pub, com)), "no se guarda la ruta de la carpeta (en Drive lleva el correo)")

print("Lo que dejó Claude fuera de los proyectos")
fp, fc = pub["meta"]["estado"].get("fuera", []), com["meta"]["estado"].get("fuera", [])
ok(len(fp) == 1 and fp[0]["de_claude"] and fp[0]["archivos"] == 2, "se cuentan los archivos de «Claude outputs»")
ok("nombres" not in fp[0] and "NOMBRE-SUELTO" not in texto(pub), "público: solo cuántos, sin nombres de archivo")
ok(any("NOMBRE-SUELTO" in n["nombre"] for n in fc[0].get("nombres", [])), "completo: con sus nombres")
ok("Claude outputs" not in pub["areas"], "«Claude outputs» no sale como área")

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

print("Lectura de la carpeta")
ok(len(com["areas"]) == 5 and "operacion" in com["areas"], "un área cuya descripción dice «Área» no se pierde")
ok(com["proyectos"]["archivo--historia"]["cerrado"] and com["areas"]["archivo"]["legible"], "un área con todos sus proyectos cerrados se lee entera (la página la trata como archivada)")
ok(com["meta"]["estado"].get("tarea_manual") is False, "sin --tarea no hay tarea, ni con botón ni diaria")
ok(com["areas"]["futura"]["legible"] is False and com["areas"]["futura"]["motivo"] == "sin-carpeta", "un área del mapa sin carpeta se marca «sin carpeta», no restringida")
ok(pub["areas"]["personas"]["motivo"] == "declarada" and com["areas"]["personas"]["legible"], "público: el área restringida se marca «declarada»; completo la lee")
sop = com["proyectos"]["operacion--soporte"]
ok(sop["ultima_sesion"] == "2026-08-15", "una entrada «(tarea)» de la bitácora no cuenta como sesión")
ok(any(s_.get("fecha") == "2026-08-20" for s_ in sop["pasos"]), "un plazo vencido no se esconde porque la tarea movió «actualizado»")
ok(any(s_.get("fecha") == "2026-06-30" for s_ in sop["pasos"]), "un plazo más de 30 días anterior a la última sesión sigue siendo plazo: está vencido, no es contexto")

print("Entregables y decisiones")
ents = {e["nombre"]: e for e in com["proyectos"]["ventas--cuentas"]["entregables"]}
ok(ents["kit-cuentas"]["titulo"] == "Kit para preparar una cuenta", "el título sale del cuerpo")
ok(ents["kit-cuentas"]["descripcion"].startswith("guía para preparar"), "la descripción sale del índice del área aunque el nombre lleve guiones")
ok(ents["kit-cuentas"].get("basado_en", [])[:1] == ["ventas/cuentas/entregables/propuesta-base.md"], "basado_en se lee como lista")
ok(ents["propuesta-base"].get("basado_en") == [], "basado_en vacío en línea («[]»)")
decs = com["proyectos"]["ventas--cuentas"]["decisiones"]
ok(sorted(d["titulo"][:20] for d in decs if d.get("por_confirmar")) == ["Decisión recuperada ", "La propuesta de Clie"], "se marca pendiente de confirmar solo con el marcador en «Decidió», no por mencionarlo en el porqué")
ok(next(d for d in decs if d["titulo"].startswith("Decisión recuperada"))["id"] == "" and all(d["id"] for d in decs if d["fecha"]), "una entrada sin fecha no tiene identificador y no desplaza a las demás")
ok(com["proyectos"]["operacion--soporte"]["estado_cabecera"] == "borrador", "el estado de proyecto.md llega a la página")
ok((com["proyectos"]["operacion--soporte"].get("en_corto") or "").startswith("2026-10-05 · **Terminamos"), "«En corto» de proyecto.md llega a la página, con su fecha")
ok("SECRETO-CORTO" not in json.dumps(pub, ensure_ascii=False), "público: el «En corto» de un proyecto restringido no llega")
ok(not com["proyectos"]["ventas--cuentas"].get("en_corto"), "un proyecto sin «En corto» no lo inventa")

print("Premisas, identificadores y cuestionamientos")
prem = {x["id"]: x for x in com["meta"]["estado"]["premisas"]}
ok(set(prem) == {"P1", "P2", "P3", "P4"} and not prem["P1"]["vigente"] and not prem["P2"]["vigente"] and prem["P3"]["vigente"] and prem["P3"]["reemplaza"] == "P1", "las premisas se leen y la reemplazada deja de estar vigente")
ok(prem["P2"]["confirmo"] == "Ana Prueba" and prem["P2"]["fecha"] == "2026-08-01", "cada premisa trae quién la confirmó y cuándo")
ok(pub["meta"]["estado"]["premisas"] == com["meta"]["estado"]["premisas"], "público: las premisas se ven, son de toda la organización")
idde = lambda t: next(d["id"] for d in decs if d["titulo"].startswith(t))
ok(idde("La propuesta de Cliente Uno") == "2026-09-21" and idde("El anexo de Cliente Uno") == "2026-09-21-2", "dos decisiones el mismo día: la más antigua sin sufijo y la siguiente con -2")
cq = {(c["a_proyecto"], c["a_id"]): c for c in com["meta"]["estado"]["cuestionamientos"]}
ok(cq[("ventas--cuentas", "2026-09-21")]["abierto"] and cq[("premisa", "P3")]["abierto"], "un cuestionamiento sin respuesta queda abierto, también el de una premisa")
ok(not cq[("premisa", "P2")]["abierto"], "una premisa nueva que reemplaza a la cuestionada cierra su cuestionamiento")
ok(all("huella" in d for D in (pub, com) for c in ("areas", "proyectos") for d in D[c].values()) and not any(x["doc_id"] == "enfoque-candidatos" for x in json.load(open(os.path.join(sys.argv[2], "indice.json"), encoding="utf-8"))) and com["meta"]["enfoque-candidatos"].get("huella"), "cada documento lleva su huella; los candidatos de enfoque llevan la suya y no van a la base")
ok(not cq[("ventas--cuentas", "2026-09-20")]["abierto"], "un cuestionamiento con una decisión que lo responde se cierra")
d0920 = next(d for d in decs if d["id"] == "2026-09-20")
ok(d0920.get("cuestionado_por") and d0920["cuestionado_por"][0]["desde"] == "operacion--soporte", "la decisión cuestionada sabe quién la cuestionó")
ok(com["proyectos"]["ventas--cuentas"].get("cuestionamientos_abiertos") == 1, "el proyecto cuenta sus cuestionamientos abiertos")
ok(com["proyectos"]["operacion--soporte"]["decisiones_total"] == 0, "un cuestionamiento no cuenta como decisión")
pan = com["areas"]["ventas"].get("panorama") or {}
ok(pan.get("fecha") == "2026-10-03" and pan.get("texto", "").startswith("Ventas tiene"), "el panorama del área se lee con su fecha")
ok(com["areas"]["operacion"].get("panorama") is None, "un área sin panorama no inventa uno")

ok(com["proyectos"]["ventas--cuentas"].get("sesiones_fechas") == ["2026-10-01", "2026-09-20"] and pub["proyectos"]["ventas--cuentas"].get("sesiones_fechas") == ["2026-10-01", "2026-09-20"], "cada proyecto trae las fechas de sus sesiones de los últimos 90 días, también en público")

print("Trabajo sin sesión")
ss = com["proyectos"]["ventas--cuentas"].get("sin_sesion")
ok(bool(ss) and ss.get("donde") == {"entregables": 1}, "un entregable tocado después de la última sesión se avisa, y solo ese")
ok(not com["proyectos"]["operacion--soporte"].get("sin_sesion"), "un proyecto sin cambios desde su última sesión no se avisa")
ok(not pub["proyectos"]["ventas--precios"].get("sin_sesion"), "público: de un proyecto restringido no se dice nada")

print("\n" + ("Todo bien." if not fallos else f"{len(fallos)} fallo(s)."))
sys.exit(1 if fallos else 0)
