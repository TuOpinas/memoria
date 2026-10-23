#!/usr/bin/env python3
"""Comprueba lo que genera generar_vista.py sobre la raíz inventada de raiz/.
Uso: comprobar.py <salida> <salida-con-modo-viejo> <salida-de-un-tablero-que-era-público>. Sale con 1 si algo falla.
Desde la 1.18 hay un solo modo: todo lo que la cuenta lee. Las tareas montadas antes pasan --modo publico o completo,
y tiene que salir lo mismo."""
import json, glob, os, sys

def cargar(d):
    D = {}
    for f in glob.glob(os.path.join(d, "*", "*.json")):
        D.setdefault(os.path.basename(os.path.dirname(f)), {})[os.path.basename(f)[:-5]] = json.load(open(f, encoding="utf-8"))
    return D

com, viejo, migrado = cargar(sys.argv[1]), cargar(sys.argv[2]), cargar(sys.argv[3])
texto = lambda D: json.dumps(D, ensure_ascii=False)
fallos = []
def ok(cond, que):
    print(("  bien  " if cond else "  FALLA ") + que)
    if not cond: fallos.append(que)

print("Un solo modo: todo lo que la cuenta lee")
ok("SECRETO-PRECIOS" in texto(com) and "SECRETO-NOMINA" in texto(com) and "SECRETO-MARGENES" in texto(com), "sale lo declarado restringido que la cuenta lee")
ok("SECRETO-OCULTO" in texto(com), "sale un proyecto que no está en el índice de su área")
ok("SECRETO-RESTRINGIDO" not in texto(com), "nunca lee las carpetas restringido/")
ok("SECRETO-PANORAMA" in texto(com), "el Panorama de un área restringida que la cuenta lee")
ok(com["areas"]["ventas"].get("colaboran") == ["carla@ejemplo.test"], "quien colabora en un área: con su cuenta")
ok(com["proyectos"]["operacion--soporte"].get("colaboran") == ["Dani Prueba"] and "dani@" not in texto(com) and "quien" not in com["proyectos"]["operacion--soporte"], "quien colabora en un proyecto: su nombre, sin su cuenta, y sin la sección en bruto")
ok("AVANCE-CUENTAS" in texto(com) and "SECRETO-CUERPO" in texto(com), "la bitácora entera")
ok(com["meta"]["estado"]["modo"] == "completo", "meta/estado dice «completo»")
ok("raiz" not in com["meta"]["estado"], "no se guarda la ruta de la carpeta (en Drive lleva el correo)")
sin_hora = lambda D: {c: {k: ({kk: vv for kk, vv in v.items() if kk != "sincronizado"} if c == "meta" and k == "estado" else v) for k, v in D[c].items()} for c in D}
ok(sin_hora(viejo) == sin_hora(com), "una tarea de antes de la 1.18 que pasa --modo publico genera exactamente lo mismo")
ok("paso_a_completo" not in com["meta"]["estado"] and migrado["meta"]["estado"].get("paso_a_completo") == com["meta"]["estado"]["snapshot"], "un tablero que era público lleva la fecha en que pasó a mostrarlo todo; uno nuevo, no")

print("Lo que dejó Claude fuera de los proyectos")
fc = com["meta"]["estado"].get("fuera", [])
ok(len(fc) == 1 and fc[0]["de_claude"] and fc[0]["archivos"] == 2, "se cuentan los archivos de «Claude outputs»")
ok(any("NOMBRE-SUELTO" in n["nombre"] for n in fc[0].get("nombres", [])), "con sus nombres")
ok("Claude outputs" not in com["areas"], "«Claude outputs» no sale como área")

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
ok(len(com["areas"]) == 6 and "operacion" in com["areas"], "un área cuya descripción dice «Área» no se pierde")
ok(com["proyectos"]["archivo--historia"]["cerrado"] and com["areas"]["archivo"]["legible"], "un área con todos sus proyectos cerrados se lee entera (la página la trata como archivada)")
ok(com["meta"]["estado"].get("tarea_manual") is False, "sin --tarea no hay tarea, ni con botón ni diaria")
ok(com["areas"]["futura"]["legible"] is False and com["areas"]["futura"]["motivo"] == "sin-carpeta", "un área del mapa sin carpeta se marca «sin carpeta», no restringida")
ok(com["areas"]["personas"]["legible"], "un área declarada «Restringida» que la cuenta lee se lee")
ok(com["areas"]["legal"]["legible"] is False and com["areas"]["legal"]["motivo"] == "restringido", "un área declarada «Restringida» que no está en la computadora sale restringida, no «sin carpeta» (Drive no baja lo que la cuenta no abre)")
ok(com["areas"]["futura"]["restringido"] is False, "«restringida» solo cuenta al inicio de «Quién la lee»: «Todo el equipo, nada restringido» no lo es")
bon, sue, sec = (com["proyectos"].get(x, {}) for x in ("personas--bonos", "personas--sueldos", "ventas--secreto"))
ok(bon.get("motivo") == "sin-carpeta", "un proyecto sin carpeta dentro de un área restringida que la cuenta lee sale «sin carpeta», no restringido")
ok(sue.get("motivo") == "restringido" and sue.get("descripcion") == "sueldos individuales, solo Beto y Ana", "un proyecto declarado restringido dentro de un área restringida que la cuenta lee sale restringido, con su línea")
ok(sec.get("motivo") == "restringido" and sec.get("descripcion") == "un acuerdo con un socio", "«**restringido**:» en el índice también lo declara, y la palabra no queda en la línea")
ron = com["proyectos"].get("ventas--ronda", {})
ok(ron.get("legible") is False and ron.get("motivo") == "restringido" and ron.get("descripcion") == "dueño Beto Prueba. Ronda de inversión, solo dirección", "un proyecto declarado restringido que no está en la computadora sale restringido, con su línea pública del índice y sin la palabra")
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
ok(not com["proyectos"]["ventas--cuentas"].get("en_corto"), "un proyecto sin «En corto» no lo inventa")

print("Premisas, identificadores y cuestionamientos")
prem = {x["id"]: x for x in com["meta"]["estado"]["premisas"]}
ok(set(prem) == {"P1", "P2", "P3", "P4"} and not prem["P1"]["vigente"] and not prem["P2"]["vigente"] and prem["P3"]["vigente"] and prem["P3"]["reemplaza"] == "P1", "las premisas se leen y la reemplazada deja de estar vigente")
ok(prem["P2"]["confirmo"] == "Ana Prueba" and prem["P2"]["fecha"] == "2026-08-01", "cada premisa trae quién la confirmó y cuándo")
idde = lambda t: next(d["id"] for d in decs if d["titulo"].startswith(t))
ok(idde("La propuesta de Cliente Uno") == "2026-09-21" and idde("El anexo de Cliente Uno") == "2026-09-21-2", "dos decisiones el mismo día: la más antigua sin sufijo y la siguiente con -2")
cq = {(c["a_proyecto"], c["a_id"]): c for c in com["meta"]["estado"]["cuestionamientos"]}
ok(cq[("ventas--cuentas", "2026-09-21")]["abierto"] and cq[("premisa", "P3")]["abierto"], "un cuestionamiento sin respuesta queda abierto, también el de una premisa")
ok(not cq[("premisa", "P2")]["abierto"], "una premisa nueva que reemplaza a la cuestionada cierra su cuestionamiento")
ok(all("huella" in d for D in (com,) for c in ("areas", "proyectos") for d in D[c].values()) and not any(x["doc_id"] == "enfoque-candidatos" for x in json.load(open(os.path.join(sys.argv[2], "indice.json"), encoding="utf-8"))) and com["meta"]["enfoque-candidatos"].get("huella"), "cada documento lleva su huella; los candidatos de enfoque llevan la suya y no van a la base")
ok(not cq[("ventas--cuentas", "2026-09-20")]["abierto"], "un cuestionamiento con una decisión que lo responde se cierra")
d0920 = next(d for d in decs if d["id"] == "2026-09-20")
ok(d0920.get("cuestionado_por") and d0920["cuestionado_por"][0]["desde"] == "operacion--soporte", "la decisión cuestionada sabe quién la cuestionó")
ok(com["proyectos"]["ventas--cuentas"].get("cuestionamientos_abiertos") == 1, "el proyecto cuenta sus cuestionamientos abiertos")
ok(com["proyectos"]["operacion--soporte"]["decisiones_total"] == 0, "un cuestionamiento no cuenta como decisión")
pan = com["areas"]["ventas"].get("panorama") or {}
ok(pan.get("fecha") == "2026-10-03" and pan.get("texto", "").startswith("Ventas tiene"), "el panorama del área se lee con su fecha")
ok(com["areas"]["operacion"].get("panorama") is None, "un área sin panorama no inventa uno")

ok(com["proyectos"]["ventas--cuentas"].get("sesiones_fechas") == ["2026-10-01", "2026-09-20"], "cada proyecto trae las fechas de sus sesiones de los últimos 90 días")

print("Trabajo sin sesión")
ss = com["proyectos"]["ventas--cuentas"].get("sin_sesion")
ok(bool(ss) and ss.get("donde") == {"entregables": 1}, "un entregable tocado después de la última sesión se avisa, y solo ese")
ok(not com["proyectos"]["operacion--soporte"].get("sin_sesion"), "un proyecto sin cambios desde su última sesión no se avisa")

print("\n" + ("Todo bien." if not fallos else f"{len(fallos)} fallo(s)."))
sys.exit(1 if fallos else 0)
