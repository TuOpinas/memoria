#!/usr/bin/env python3
"""Prueba cerrar.py (skill sesion): escribe lo del cierre archivo por archivo sin pisar a nadie.

Uso: python3 pruebas/sesion/probar_cerrar.py
"""
import importlib.util, json, os, pathlib, shutil, subprocess, sys, tempfile, threading, time

AQUI = pathlib.Path(__file__).resolve().parent
CERRAR = AQUI.parent.parent / "plugins" / "memoria" / "skills" / "sesion" / "cerrar.py"
fallos = 0


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1


def raiz_nueva():
    r = pathlib.Path(tempfile.mkdtemp()) / "raiz"
    shutil.copytree(AQUI.parent / "tablero" / "raiz", r)
    return r


def corre(raiz, cambios, *extra, proyecto="ventas/cuentas", env=None):
    f = raiz.parent / f"cambios-{time.time_ns()}.json"; f.write_text(json.dumps(cambios, ensure_ascii=False), encoding="utf-8")
    r = subprocess.run([sys.executable, str(CERRAR), str(raiz), proyecto, str(f), *extra], capture_output=True, text=True, env={**os.environ, **(env or {})})
    try:
        return r.returncode, json.loads(r.stdout)
    except ValueError:
        return r.returncode, r.stdout + r.stderr


from zoneinfo import ZoneInfo
import datetime
HOY = datetime.datetime.now(ZoneInfo("America/Mexico_City")).date().isoformat()   # la zona de la raíz de prueba
SESION = f"## {HOY}\nTema: PRUEBA-CERRAR la llamada.\nAvances: PRUEBA-CERRAR cerrada.\nSesión de: Ana Prueba · plugin 9.9.9"
DEC = f"## {HOY} · El soporte de Cliente Uno responde en menos de 24 horas\nDecidió: Ana Prueba\nPor qué: es la condición para firmar."
CAMBIOS = {"sesion": SESION, "decisiones": [DEC],
           "proyecto": {"estatus": f"{HOY} · **Cliente Uno acepta si el soporte responde en 24 horas.**\n- **Siguiente:** firmar.",
                        "reemplazos": [{"de": "- Llamar a Cliente Uno antes del 2026-10-06 para cerrar la propuesta.", "a": "- Firmar con Cliente Uno."}]},
           "area": {"linea": "- `cuentas/` — las cuentas grandes; Cliente Uno a punto de firmar", "entregables": ["  - kit-cuentas — guía para preparar una cuenta · actualizado 2026-09-10"]},
           "estatus_area": f"{HOY} · **PANORAMA-NUEVO del área, escrito por su responsable.**\n- **Siguiente:**\n  - Cerrar la propuesta de Cliente Uno. Es la única cuenta grande abierta."}

print("cerrar.py: un cierre normal")
R = raiz_nueva()
c, s = corre(R, CAMBIOS, "--cuenta", "ana@ejemplo.test")
ok(c == 0 and set(s["escritos"]) == {"ventas/cuentas/sesiones.md", "ventas/cuentas/decisiones.md", "ventas/cuentas/proyecto.md", "ventas/area.md"}, f"escribe los cuatro archivos del cierre ({s if c else s['escritos']})")
ses = (R / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8")
ok(ses.index(f"## {HOY}\nTema: PRUEBA") < ses.index("## 2026-10-01") and "## 2026-10-01 (propuesta enviada)" in ses, "la entrada nueva va arriba y las anteriores siguen")
ok(f"actualizado: {HOY}" in ses.split("---")[1], "la cabecera dice actualizado hoy, en la zona de la organización")
dec = (R / "ventas/cuentas/decisiones.md").read_text(encoding="utf-8")
ok(dec.index(f"## {HOY} · El soporte") < dec.index("## 2026-09-26"), "la decisión nueva va arriba")
pro = (R / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8")
ok("- Firmar con Cliente Uno." in pro and "antes del 2026-10-06" not in pro and "Segundo párrafo con detalle" in pro, "el reemplazo exacto cambia solo ese paso")
ok(f"## Estatus\n{HOY} · **Cliente Uno" in pro and pro.index("## Estatus") < pro.index("## Objetivo") and "## En corto" not in pro, "el Estatus sustituye a En corto en su sitio, debajo del título")
area = (R / "ventas/area.md").read_text(encoding="utf-8")
ok("Cliente Uno a punto de firmar" in area and "propuesta-base" not in area.split("## Proyectos")[1].split("## ")[0] and "- `precios/` — restringido" in area, "la línea del proyecto y sus entregables se reescriben; las demás líneas no se tocan")
ok(f"## Estatus\n{HOY} · **PANORAMA-NUEVO" in area and "## Panorama" not in area and "## Prioridades ahora" not in area and area.index("## Estatus") < area.index("## Quién participa"), "en un área sin migrar, el Estatus sustituye al Panorama y retira Prioridades ahora")
ok("  - Ordenar los precios antes del cierre del trimestre." in area and s.get("fundidas") == ["Ordenar los precios antes del cierre del trimestre."], "la prioridad que el Estatus nuevo no traía entra en «Siguiente» y se devuelve en fundidas")
ok(s["sin_match"] == [] and s["ajenos"] == [] and s["rechazados"] == [] and s["fallidos"] == [] and s["hora"].endswith("Z") and s["documento"].startswith("ventas--cuentas--") and "escrito_en" in s, "sin_match, ajenos, rechazados y fallidos vacíos; hora, documento y escrito_en para seguir")
ok(not list((R / "ventas/cuentas").glob("*.cerrar-tmp")), "no deja temporales")

print("cerrar.py: repetir no duplica; un reemplazo que no cuadra, cruza encabezados o encoge se devuelve")
c, s2 = corre(R, CAMBIOS, "--cuenta", "ana@ejemplo.test")
ok(set(s2["escritos"]) <= {"ventas/area.md"} and ses == (R / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8"), "el mismo cierre otra vez no escribe nada (salvo el Estatus del área, que ya no tiene prioridades que fundir)")
c, s3 = corre(R, {"proyecto": {"reemplazos": [{"de": "- Sostener la llamada", "a": "- X"}, {"de": "no está en el archivo", "a": "y"}]}})
ok(len(s3["sin_match"]) == 1 and s3["sin_match"][0]["veces"] == 0 and "- X" in (R / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8"), "el reemplazo que no aparece va a sin_match; el que sí, se aplica")
pro = (R / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8")
grande = pro[pro.index("## Siguientes pasos"):]
c, s4 = corre(R, {"proyecto": {"reemplazos": [{"de": grande, "a": "## Siguientes pasos\n- Uno solo.\n"}]}})
ok(s4["escritos"] == [] and s4["sin_match"] and "cruza un encabezado" in s4["sin_match"][0]["motivo"], "un reemplazo que cruza un encabezado o pasa de doce líneas no se aplica")
c, s5 = corre(R, {"proyecto": {"reemplazos": [{"de": "## Estado actual\n" + pro.split("## Estado actual\n")[1].split("## Siguientes")[0], "a": "## Estado actual\nx\n\n"}]}})
ok(s5["escritos"] == [] and (s5["rechazados"] or s5["sin_match"]), "un archivo que encogería a menos de la mitad no se escribe sin --forzar")
c, s6 = corre(R, {"sesion": "Trabajamos en: sin fecha"})
ok(c == 1 and "error" in s6 and "sesion" in s6["error"], "una entrada sin «## AAAA-MM-DD» se rechaza antes de escribir nada")

print("cerrar.py: los nombres de la 1.21 entran y salen con los de la 1.22")
c, sv = corre(raiz_nueva(), {"sesion": f"## {HOY}\nTrabajamos en: x\nAvances: y\nPendiente: z"})
ok(c == 1 and "Tema" in sv.get("error", ""), "una entrada nueva con «Trabajamos en» o «Pendiente» se rechaza")
c, sv = corre(raiz_nueva(), {"decisiones": [DEC + "\nDescartamos: otra cosa."]})
ok(c == 1 and "Descartado" in sv.get("error", ""), "una decisión nueva con «Descartamos» se rechaza")
Rv = raiz_nueva()
c, sv = corre(Rv, {"proyecto": {"estatus": "VIEJA-CLAVE sin fecha ni negrita"}}, "--cuenta", "ana@ejemplo.test")
ok(c == 1 and "AAAA-MM-DD" in sv.get("error", ""), "un Estatus que no empieza por «AAAA-MM-DD · **frase**» se rechaza")
Rv2 = raiz_nueva()
av2 = (Rv2 / "ventas/area.md").read_text(encoding="utf-8"); import re as _re
(Rv2 / "ventas/area.md").write_text(_re.sub(r"## Panorama\n.*?(?=^## )", "", av2, flags=_re.S | _re.M), encoding="utf-8")
c, sv = corre(Rv2, {"estatus_area": f"{HOY} · **NUEVO-ESTATUS.**"}, "--cuenta", "ana@ejemplo.test")
av2 = (Rv2 / "ventas/area.md").read_text(encoding="utf-8")
ok(c == 0 and av2.index("## Estatus") < av2.index("## Qué es") and "## Prioridades ahora" not in av2, "en un área sin Panorama, el Estatus se crea debajo del título y retira Prioridades ahora")
pb = Rv2 / "ventas/cuentas/entregables/propuesta-base.md"
pb.write_text(pb.read_text(encoding="utf-8").replace("estado: vigente\n", 'estado: vigente\naportacion: "Toda propuesta parte de esta estructura."\n', 1), encoding="utf-8")
c, sv = corre(Rv2, {"area": {"linea": "- `cuentas/` — x", "entregables": [{"archivo": "propuesta-base.md"}, {"archivo": "no-existe.md"}]}}, "--cuenta", "ana@ejemplo.test")
av2 = (Rv2 / "ventas/area.md").read_text(encoding="utf-8")
ok("  - propuesta-base — Toda propuesta parte de esta estructura. · actualizado 2026-09-20" in av2 and len(sv["sin_match"]) == 1, "la línea del entregable se toma de su aportacion; uno que no existe va a sin_match")
# un entregable sin aportacion conserva su línea de antes; sin «entregables», se conservan todas
Rv2 = raiz_nueva()
c, sv = corre(Rv2, {"area": {"linea": "- `cuentas/` — y", "entregables": [{"archivo": "kit-cuentas.md"}]}}, "--cuenta", "ana@ejemplo.test")
av2 = (Rv2 / "ventas/area.md").read_text(encoding="utf-8")
ok("  - kit-cuentas — guía para preparar una cuenta · actualizado 2026-09-10" in av2 and sv["sin_match"] and "se conservó" in sv["sin_match"][0]["motivo"], "un entregable sin aportacion conserva su línea del índice y lo dice en sin_match")
c, sv = corre(Rv2, {"area": {"linea": "- `cuentas/` — z"}}, "--cuenta", "ana@ejemplo.test")
av2 = (Rv2 / "ventas/area.md").read_text(encoding="utf-8")
ok("- `cuentas/` — z\n  - kit-cuentas — guía" in av2 and sv["sin_match"] == [], "sin «entregables», las sublíneas que había se conservan")
# publicar en una llamada: «otros» pasa la cabecera a vigente antes de armar la línea en area.md
Rv3 = raiz_nueva()
pb3 = Rv3 / "ventas/cuentas/entregables/borrador-viejo.md"; tb = pb3.read_text(encoding="utf-8")
pb3.write_text(tb.replace("estado: borrador\n", 'estado: borrador\naportacion: "Vale para publicar."\n', 1), encoding="utf-8")
c, sv = corre(Rv3, {"otros": [{"ruta": "ventas/cuentas/entregables/borrador-viejo.md", "reemplazos": [{"de": "estado: borrador\naportacion", "a": f"estado: vigente\nactualizado: {HOY}\naportacion"}, {"de": "actualizado: 2026-08-01\n", "a": ""}]}], "area": {"linea": "- `cuentas/` — w", "entregables": [{"archivo": "borrador-viejo.md"}]}}, "--cuenta", "ana@ejemplo.test")
av3 = (Rv3 / "ventas/area.md").read_text(encoding="utf-8")
ok(c == 0 and f"  - borrador-viejo — Vale para publicar. · actualizado {HOY}" in av3, "la línea del entregable recién publicado lleva la fecha de hoy")
# un Estatus de proyecto sobre una raíz con «En corto» y «Estatus» a la vez: queda solo el Estatus
Rv4 = raiz_nueva()
pp4 = Rv4 / "ventas/precios/proyecto.md"; pp4.write_text(pp4.read_text(encoding="utf-8").replace("## En corto\n", "## Estatus\n2026-10-01 · **VIEJO.**\n\n## En corto\n", 1), encoding="utf-8")
c, sv = corre(Rv4, {"proyecto": {"estatus": f"{HOY} · **NUEVO.**"}}, "--cuenta", "ana@ejemplo.test", proyecto="ventas/precios")
pp4t = pp4.read_text(encoding="utf-8")
ok(c == 0 and "## En corto" not in pp4t and pp4t.count("## Estatus") == 1 and "**NUEVO.**" in pp4t, "con Estatus y En corto a la vez, el cierre deja solo el Estatus")

print("cerrar.py: la cuenta que solo colabora, y «otros» fuera del área")
R2 = raiz_nueva()
c, s7 = corre(R2, CAMBIOS, "--cuenta", "carla@ejemplo.test")
ok("ventas/cuentas/sesiones.md" in s7["escritos"] and "ventas/area.md" in s7["escritos"] and any("Estatus del área" in r["motivo"] for r in s7["rechazados"]) and "PANORAMA-NUEVO" not in (R2 / "ventas/area.md").read_text(encoding="utf-8") and "Cliente Uno a punto de firmar" in (R2 / "ventas/area.md").read_text(encoding="utf-8"), "quien colabora en el área escribe la línea del proyecto pero no el Estatus del área")
c, s8 = corre(R2, {"sesion": SESION, "area": {"linea": "- `soporte/` — x"}, "estatus_area": f"{HOY} · **y.**"}, "--cuenta", "carla@ejemplo.test", proyecto="operacion/soporte")
ok(len(s8["rechazados"]) == 2 and "operacion/area.md" not in s8["escritos"], "quien no es del área no escribe su area.md: se le dice que se lo pase al responsable")
# añadir `aportacion` a una cabecera no mueve `actualizado`; un cambio en el cuerpo sí
c, s8b = corre(R2, {"otros": [{"ruta": "ventas/cuentas/entregables/propuesta-base.md", "reemplazos": [{"de": "estado: vigente\nactualizado: 2026-09-20", "a": 'estado: vigente\naportacion: "La plantilla fija la estructura de toda propuesta."\nactualizado: 2026-09-20'}]}]}, "--cuenta", "ana@ejemplo.test")
pb = (R2 / "ventas/cuentas/entregables/propuesta-base.md").read_text(encoding="utf-8")
ok(c == 0 and "ventas/cuentas/entregables/propuesta-base.md" in s8b["escritos"] and 'aportacion: "La plantilla' in pb and "actualizado: 2026-09-20" in pb, "añadir aportacion por «otros» no mueve actualizado")
c, s8c = corre(R2, {"otros": [{"ruta": "ventas/cuentas/entregables/propuesta-base.md", "reemplazos": [{"de": "Cuerpo.", "a": "Cuerpo nuevo."}]}]}, "--cuenta", "ana@ejemplo.test")
ok(c == 0 and f"actualizado: {HOY}" in (R2 / "ventas/cuentas/entregables/propuesta-base.md").read_text(encoding="utf-8"), "un cambio en el cuerpo sí la pone a hoy")
c, s9 = corre(R2, {"otros": [{"ruta": "guia.md", "reemplazos": [{"de": "Ana Prueba", "a": "X"}]}]})
ok(c == 1 and "guia.md" in s9.get("error", ""), "«otros» nunca toca guia.md")
c, s10 = corre(R2, {"otros": [{"ruta": "operacion/soporte/proyecto.md", "reemplazos": [{"de": "## Objetivo", "a": "## Objetivo"}]}]})
ok(s10["rechazados"] and "fuera del área" in s10["rechazados"][0]["motivo"] and s10["escritos"] == [], "«otros» fuera del área del proyecto se rechaza sin --fuera-del-area")

print("cerrar.py: alguien escribió desde la apertura; lo propio no cuenta; sin consola no se mira")
R3 = raiz_nueva()
viejo = time.time() - 7200
for f_ in ("proyecto.md", "sesiones.md", "decisiones.md"):
    os.utime(R3 / "ventas/cuentas" / f_, (viejo, viejo))
os.utime(R3 / "ventas/area.md", (viejo, viejo))
p = R3 / "ventas/cuentas/proyecto.md"
p.write_text(p.read_text(encoding="utf-8") + "\n- Paso que puso otra persona.\n", encoding="utf-8")
abierto = datetime.datetime.now(ZoneInfo("America/Mexico_City")).replace(microsecond=0) - datetime.timedelta(hours=1)
c, s11 = corre(R3, CAMBIOS, "--abierto", abierto.isoformat(), "--cuenta", "ana@ejemplo.test")
ok([a["ruta"] for a in s11["ajenos"]] == ["ventas/cuentas/proyecto.md"] and "-06:00" in s11["ajenos"][0]["hora"] or "-05:00" in s11["ajenos"][0]["hora"], f"dice qué archivo cambió otra persona, con la hora en la zona de la organización ({s11['ajenos']})")
ok("- Paso que puso otra persona." in p.read_text(encoding="utf-8") and "- Firmar con Cliente Uno." in p.read_text(encoding="utf-8"), "escribe encima de su versión, no de la de la apertura")
c, s12 = corre(R3, {"proyecto": {"reemplazos": [{"de": "- Paso que puso otra persona.", "a": "- Paso ajeno, visto."}]}}, "--abierto", abierto.isoformat())
ok(s12["ajenos"] == [] and s12["escritos"] == ["ventas/cuentas/proyecto.md"], "la segunda llamada de la misma sesión no da por ajeno lo que ella misma escribió")
R4 = raiz_nueva()
for f_ in ("proyecto.md", "sesiones.md", "decisiones.md"):
    os.utime(R4 / "ventas/cuentas" / f_, None)   # como la copia sin consola: la fecha es la de la traída
c, s13 = corre(R4, CAMBIOS, "--abierto", abierto.isoformat(), "--sin-fechas")
ok(s13["ajenos"] == [] and len(s13["escritos"]) == 4, "con --sin-fechas (la copia) no se mira la fecha de nadie")
c, s14 = corre(raiz_nueva(), {"sesion": SESION}, "--abierto", "ahora: 2026-10-22")
ok(c == 2, "un --abierto que no es una hora ISO se rechaza con un mensaje")

print("cerrar.py: la fecha en la zona de la organización, no en la de la máquina")
R5 = raiz_nueva()
c, s15 = corre(R5, {"sesion": SESION}, env={"TZ": "UTC"})
ok(f"actualizado: {HOY}" in (R5 / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8"), "actualizado lleva la fecha de la organización aunque la máquina esté en UTC")
MANANA = (datetime.date.fromisoformat(HOY) + datetime.timedelta(days=1)).isoformat()
AYER = (datetime.date.fromisoformat(HOY) - datetime.timedelta(days=1)).isoformat()
R5b = raiz_nueva()
c, s15b = corre(R5b, {"sesion": SESION.replace(HOY, MANANA)})
ok(c == 1 and "error" in s15b and MANANA in s15b["error"] and HOY in s15b["error"] and "## " + MANANA not in (R5b / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8"), "una entrada fechada mañana (el reloj en UTC) se rechaza diciendo qué día es hoy en la zona")
c, s15c = corre(R5b, {"decisiones": [DEC.replace(HOY, "2026-01-05")]})
ok(c == 1 and "error" in s15c and "2026-01-05" in s15c["error"], "una decisión con una fecha vieja también")
c, s15d = corre(R5b, {"sesion": SESION.replace(HOY, AYER)})
ok(c == 0 and "## " + AYER in (R5b / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8"), "ayer vale: la sesión pudo cruzar la medianoche")
c, s15e = corre(R5b, {"decisiones": [DEC.replace(HOY, "2026-01-05")]}, "--cualquier-fecha")
ok(c == 0 and "## 2026-01-05 · El soporte" in (R5b / "ventas/cuentas/decisiones.md").read_text(encoding="utf-8"), "con --cualquier-fecha pasa una fecha a propósito")

print("cerrar.py: finales de línea de Windows, archivos que faltan y codificación")
R6 = raiz_nueva()
ps = R6 / "ventas/cuentas/sesiones.md"
ps.write_bytes(ps.read_text(encoding="utf-8").replace("\n", "\r\n").encode("utf-8"))
(R6 / "ventas/cuentas/decisiones.md").unlink()
c, s16 = corre(R6, CAMBIOS, "--cuenta", "ana@ejemplo.test")
b = ps.read_bytes()
ok(b"\r\n" in b and b"\n" not in b.replace(b"\r\n", b"") and f"actualizado: {HOY}".encode() in b and b"PRUEBA-CERRAR" in b, "un archivo con CRLF sigue en CRLF entero, con la cabecera al día")
ok(c == 0 and any(f["ruta"] == "ventas/cuentas/decisiones.md" for f in s16["fallidos"]) and "ventas/cuentas/proyecto.md" in s16["escritos"], "un archivo que falta va a fallidos y el resto se escribe igual, con el JSON")
f = R6.parent / "bom.json"; f.write_bytes(b"\xef\xbb\xbf" + json.dumps({"sesion": SESION.replace("PRUEBA", "BOM")}).encode())
r = subprocess.run([sys.executable, str(CERRAR), str(R6), "ventas/cuentas", str(f)], capture_output=True, text=True)
ok(r.returncode == 0 and "BOM-CERRAR" in ps.read_text(encoding="utf-8"), "un cambios.json con BOM se lee")

print("cerrar.py: quién escribió y quién publicó (1.23)")
RA = raiz_nueva()
abiertoA = (datetime.datetime.now(ZoneInfo("America/Mexico_City")) - datetime.timedelta(minutes=5)).isoformat()
(RA / "ventas/cuentas/taller/nota-nueva.md").write_text("---\nestado: borrador\nactualizado: 2026-10-01\naportacion: x\nbasado_en: []\n---\n# Nota\n", encoding="utf-8")
c, sa = corre(RA, {"sesion": SESION, "escribio": ["entregables/borrador-viejo.md", "/taller/nota-precios.md", "entregables/borrador-viejo.md"], "publico": ["entregables/kit-cuentas.md"]}, "--abierto", abiertoA)
sesA = (RA / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8")
ok(c == 0 and "Avances: PRUEBA-CERRAR cerrada.\nEscribió: entregables/borrador-viejo.md, taller/nota-precios.md\nPublicó: entregables/kit-cuentas.md\nSesión de: Ana Prueba" in sesA, "«Escribió:» y «Publicó:» van antes de «Sesión de:», sin repetir y con la ruta normalizada")
ok(sa.get("sin_nombrar") == ["taller/nota-nueva.md"], f"lo cambiado desde la apertura que no se nombró vuelve en sin_nombrar ({sa.get('sin_nombrar')})")
c, sb = corre(raiz_nueva(), {"sesion": SESION, "publico": ["entregables/borrador-viejo.md"]})
ok(c == 1 and "no está vigente" in sb.get("error", ""), "publicar algo que no está vigente se rechaza antes de escribir")
c, sc = corre(raiz_nueva(), {"sesion": SESION, "escribio": ["proyecto.md"]})
ok(c == 1 and "entregables/ o taller/" in sc.get("error", ""), "una ruta fuera de entregables/ y taller/ se rechaza")
c, sd = corre(raiz_nueva(), {"sesion": SESION, "escribio": ["entregables/no-existe.md"]})
ok(c == 1 and "no existe" in sd.get("error", ""), "un documento que no existe se rechaza")
c, se = corre(raiz_nueva(), {"escribio": ["entregables/kit-cuentas.md"]})
ok(c == 1 and "hace falta «sesion»" in se.get("error", ""), "sin entrada de sesión no hay dónde atribuir")
c, sf = corre(raiz_nueva(), {"sesion": SESION.replace("Sesión de", "Escribió: x\nSesión de"), "escribio": ["entregables/kit-cuentas.md"]})
ok(c == 1 and "ya trae" in sf.get("error", ""), "una entrada que ya trae «Escribió:» y además la lista se rechaza")
RG = raiz_nueva()
c, sg = corre(RG, {"sesion": SESION})
ok(c == 0 and "Escribió:" not in (RG / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8") and "sin_nombrar" not in sg, "sin documentos no hay líneas, y sin --abierto no hay sin_nombrar")

print("cerrar.py: la rotación de los registros (1.23)")
RR = raiz_nueva()
pdec = RR / "ventas/cuentas/decisiones.md"
viejo_dec = pdec.read_text(encoding="utf-8")
relleno = "".join(f"## 2026-09-{1 + i % 28:02d} · Decisión de relleno {i}\nDecidió: Ana Prueba\nPor qué: " + "x " * 600 + "\n\n" for i in range(90))
pdec.write_text(viejo_dec.replace("# Decisiones\n", "# Decisiones\n\n" + relleno, 1), encoding="utf-8")
grande = pdec.read_text(encoding="utf-8")
c, sr = corre(RR, {"sesion": SESION, "decisiones": [DEC]})
anio = HOY[:4]
arch = RR / f"ventas/cuentas/decisiones-2026.md"
vivo = pdec.read_text(encoding="utf-8")
ok(c == 0 and arch.is_file() and arch.read_text(encoding="utf-8") == grande, "un decisiones.md de más de 100 KB se archiva entero, tal cual, con el año de su entrada más nueva")
ok(vivo.startswith(f"---\nestado: vigente\nactualizado: {HOY}\n---\n# ") and "Archivado: decisiones-2026.md." in vivo and vivo.count("\n## ") == 1 and f"## {HOY} · El soporte" in vivo,
   "el vivo queda con su cabecera, su título, la línea «Archivado:» y solo la decisión de hoy")
ok(vivo.index("Archivado:") < vivo.index(f"## {HOY}"), "la línea «Archivado:» va delante de la primera entrada, fuera de ella")
ok([x["a"] for x in sr.get("rotados", [])] == ["ventas/cuentas/decisiones-2026.md"] and sr["rotados"][0]["motivo"] == "pasa de 100 KB" and "ventas/cuentas/decisiones-2026.md" in sr["escritos"],
   f"vuelve en «rotados» y en «escritos» ({sr.get('rotados')})")
ok(not (RR / "ventas/cuentas/sesiones-2026.md").exists(), "un registro pequeño no se archiva")
pdec.write_text(vivo + relleno, encoding="utf-8")
c, sr2 = corre(RR, {"sesion": SESION.replace("PRUEBA-CERRAR la llamada", "otra"), "decisiones": [DEC.replace("menos de 24", "menos de 12")]})
vivo2 = pdec.read_text(encoding="utf-8")
ok((RR / "ventas/cuentas/decisiones-2026-2.md").is_file() and "Archivado: decisiones-2026.md, decisiones-2026-2.md." in vivo2, "el segundo del mismo año es «-2», y «Archivado:» los lista a los dos")
RY = raiz_nueva()
pses = RY / "ventas/cuentas/sesiones.md"
pses.write_text(pses.read_text(encoding="utf-8").replace("2026-", "2025-"), encoding="utf-8")
c, sy = corre(RY, {"sesion": SESION})
ok((RY / "ventas/cuentas/sesiones-2025.md").is_file() and any(x["motivo"] == "cambió el año" for x in sy.get("rotados", [])) and f"## {HOY}" in pses.read_text(encoding="utf-8"),
   "al cambiar el año, la bitácora del año anterior se archiva con ese año y la entrada de hoy abre la nueva")
RN = raiz_nueva()
pn = RN / "ventas/cuentas/decisiones.md"; pn.write_text(grande, encoding="utf-8")
c, sn = corre(RN, {"decisiones": [DEC]}, "--sin-rotar")
ok(c == 0 and not (RN / "ventas/cuentas/decisiones-2026.md").exists() and "rotados" not in sn, "con --sin-rotar no se archiva nada")

print("cerrar.py: dos cierres a la vez sobre el mismo proyecto")
spec = importlib.util.spec_from_file_location("cerrar", CERRAR); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
R7 = raiz_nueva()
viejo = time.time() - 7200
for f_ in ("proyecto.md", "sesiones.md", "decisiones.md"):
    os.utime(R7 / "ventas/cuentas" / f_, (viejo, viejo))
os.utime(R7 / "ventas/area.md", (viejo, viejo))
leer_original = m.leer
cruce = threading.Event()
def leer_lento(p):
    """El cierre A lee y se entretiene antes de escribir; B llega mientras: el cerrojo lo hace esperar y después B
    escribe encima de lo de A, y lo de A le sale como ajeno «durante»."""
    t = leer_original(p)
    if threading.current_thread().name == "A" and not cruce.is_set():
        cruce.set(); time.sleep(0.5)
    return t
m.leer = leer_lento
cambA = dict(CAMBIOS, sesion=SESION.replace("PRUEBA-CERRAR la llamada", "cierre A"))
cambB = {"sesion": SESION.replace("PRUEBA-CERRAR la llamada", "cierre B"), "proyecto": {"reemplazos": [{"de": "- Sostener la llamada semanal con cada cliente.", "a": "- Llamada quincenal con cada cliente (B)."}]}}
fa, fb = R7.parent / "a.json", R7.parent / "b.json"
fa.write_text(json.dumps(cambA, ensure_ascii=False)); fb.write_text(json.dumps(cambB, ensure_ascii=False))
salidas = {}
m.print = lambda *a, **k: salidas.__setitem__(threading.current_thread().name, json.loads(a[0]))   # la salida de cada hilo, aparte
def cierre(nombre, f, abierto_):
    m.main(["cerrar.py", str(R7), "ventas/cuentas", str(f), "--abierto", abierto_])
hA = (abierto - datetime.timedelta(minutes=1)).isoformat(); hB = (abierto - datetime.timedelta(minutes=2)).isoformat()
ta = threading.Thread(target=cierre, args=("A", fa, hA), name="A"); tb = threading.Thread(target=cierre, args=("B", fb, hB), name="B")
ta.start(); cruce.wait(); time.sleep(0.05); tb.start(); ta.join(); tb.join()
ses7 = (R7 / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8"); pro7 = (R7 / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8")
ok("cierre A" in ses7 and "cierre B" in ses7 and "## 2026-10-01 (propuesta enviada)" in ses7, "las dos entradas quedan, y la anterior también")
ok("- Firmar con Cliente Uno." in pro7 and "(B)." in pro7, "los pasos que cambió cada cierre quedan los dos")
ok(any(a["ruta"] == "ventas/cuentas/sesiones.md" for a in salidas["B"]["ajenos"]) and not any(a["ruta"] == "ventas/cuentas/sesiones.md" for a in salidas["A"]["ajenos"]), f"cada cierre dice lo que escribió el otro y nunca lo suyo (A: {[a['ruta'] for a in salidas['A']['ajenos']]}; B: {[a['ruta'] for a in salidas['B']['ajenos']]})")

print("\n" + ("Todo bien." if not fallos else f"{fallos} fallo(s)."))
sys.exit(1 if fallos else 0)
