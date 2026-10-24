#!/usr/bin/env python3
"""Prueba migrar_estructura.py (la migración a la estructura de la 1.22) contra la raíz inventada de pruebas/tablero/raiz.

Uso: python3 pruebas/sesion/probar_migrar.py
"""
import hashlib, importlib.util, json, pathlib, shutil, subprocess, sys, tempfile

AQUI = pathlib.Path(__file__).resolve().parent
SES = AQUI.parent.parent / "plugins" / "memoria" / "skills" / "sesion"
MIG, ABRIR = SES / "migrar_estructura.py", SES / "abrir.py"
fallos = 0


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1


def raiz_nueva():
    r = pathlib.Path(tempfile.mkdtemp()) / "raiz"
    shutil.copytree(AQUI.parent / "tablero" / "raiz", r)
    (r / "ventas/cuentas/fuentes").mkdir(exist_ok=True)
    (r / "ventas/cuentas/fuentes/enlaces.md").write_text("---\nestado: vigente\nactualizado: 2026-09-01\n---\n\n# Enlaces\n\n| Qué es | Enlace | Qué tener presente |\n|---|---|---|\n| ERP | https://x | — |\n", encoding="utf-8")
    e = r / "ventas/cuentas/entregables/kit-cuentas.md"
    e.write_text(e.read_text(encoding="utf-8").replace("estado: vigente\n", 'estado: vigente\nafirma: "Una cuenta se prepara en cinco pasos."\nbasado_en:\n  - ventas/cuentas/fuentes/enlaces.md\n', 1), encoding="utf-8")
    return r


def corre(raiz, *a):
    r = subprocess.run([sys.executable, str(MIG), str(raiz), *a], capture_output=True, text=True)
    try:
        return r.returncode, json.loads(r.stdout)
    except ValueError:
        return r.returncode, r.stdout + r.stderr


def huellas(r):
    return {p.relative_to(r).as_posix(): hashlib.sha1(p.read_bytes()).hexdigest() for p in r.rglob("*") if p.is_file()}


print("migrar_estructura.py: la detección de abrir.py y lo que la migración renombra son la misma función")
def func(ruta):
    src = ruta.read_text(encoding="utf-8"); i = src.index("def marcas_anteriores"); j = src.index("\n\n", src.index("ARCHIVOS_ANTERIORES", i))
    return src[i:j]
ok(func(MIG) == func(ABRIR), "marcas_anteriores y ARCHIVOS_ANTERIORES iguales en los dos scripts")

print("migrar_estructura.py: --plan no escribe nada")
R = raiz_nueva(); antes = huellas(R)
c, s = corre(R, "--cuenta", "ana@ejemplo.test", "--plan")
ok(c == 0 and s["plan"] and s["archivos"] and huellas(R) == antes, "dice qué haría y la carpeta queda igual")

print("migrar_estructura.py: la migración de la cuenta de Ana")
dec_antes = {k: v for k, v in huellas(R).items() if k.endswith("decisiones.md") or k.startswith("base/") or k.startswith("personas/")}
ses_antes = (R / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8")
c, s = corre(R, "--cuenta", "ana@ejemplo.test", "--nombre", "Ana Prueba", "--plugin", "1.22.0")
ok(c == 0 and s["guia"] and set(s["areas"]) == {"ventas", "operacion", "futura", "archivo"} and set(s["pendientes"]) == {"personas", "legal"}, "solo sus áreas, y guia.md porque responde por el contexto; las de Beto quedan pendientes")
ok({k: v for k, v in huellas(R).items() if k in dec_antes} == dec_antes, "no toca decisiones.md, base/ ni las áreas de otra cuenta")
g = (R / "guia.md").read_text(encoding="utf-8")
ok("| Área | Qué es | Responsable | Cuenta | Quién la lee | Acceso |" in g and "| Restringida: dirección | Restringida |" in g and "| Todo el equipo | Abierta |" in g, "guia.md: Responsable y Acceso; «Quién la lee» se queda como estaba, para los plugins 1.21")
a = (R / "ventas/area.md").read_text(encoding="utf-8")
ok("## Panorama" not in a and "## Prioridades ahora" not in a and a.index("## Estatus") < a.index("## Qué es") < a.index("## Proyectos") < a.index("## Quién participa"), "area.md: Estatus primero, sin Panorama ni Prioridades ahora")
ok("2026-10-03 · **Ventas tiene una sola cuenta grande abierta" in a and "  - Cerrar la propuesta de Cliente Uno." in a and "Responsable: Ana Prueba" in a and "restringido: responsable Beto Prueba." in a, "el Estatus lleva la fecha y la frase del Panorama y las prioridades debajo de «Siguiente»")
ok("- `cuentas/`: En curso desde el 2026-09-01." in a and "`precios/`:" not in a and "SECRETO" not in a.split("## Qué es")[0], "y una línea por proyecto activo, sin los restringidos")
ok("  - kit-cuentas — Una cuenta se prepara en cinco pasos. · actualizado 2026-09-10" in a, "la línea del entregable vigente se toma de su aportacion")
p = (R / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8")
ok("## Terminado significa" not in p and "a la firma. Cliente Uno firmado." in p and "Entra: Cliente Uno. No entra: precios" in p, "proyecto.md: Terminado significa en Objetivo; Entra / No entra")
ok("## Estado actual" not in p and "Consumen esto" not in p and "Responsable: Ana Prueba" in p and p.index("## Estatus") < p.index("## Objetivo") < p.index("## Alcance") < p.index("## Siguientes pasos") < p.index("## Quién participa"), "sin Estado actual ni Consumen esto, y en el orden de la 1.22")
ok("## Estatus\n2026-10-01 · **En curso desde el 2026-09-01.**" in p, "sin En corto, un Estatus mínimo con la fecha de la cabecera y la primera frase de Estado actual")
t = (R / "ventas/cuentas/taller/estado-anterior.md").read_text(encoding="utf-8")
ok("Segundo párrafo con detalle" in t and t.startswith("---\nestado: borrador\nactualizado: 2026-10-01\naportacion: ") and "basado_en:\n  - ventas/cuentas/proyecto.md" in t, "el Estado actual va entero al taller, con su cabecera")
h = (R / "archivo/historia/proyecto.md").read_text(encoding="utf-8")
ok("## Estatus\n2026-09-01 · **Proyecto terminado el 2026-09-01.** El sistema anterior quedó respaldado y retirado." in h and not (R / "archivo/historia/taller/estado-anterior.md").exists(), "un proyecto cerrado lo dice en su Estatus, con cómo acabó, y no estrena un archivo en el taller")
k = (R / "ventas/cuentas/entregables/kit-cuentas.md").read_text(encoding="utf-8")
ok('aportacion: "Una cuenta se prepara en cinco pasos."' in k and "afirma:" not in k and "fuentes/inventario.md" in k and "actualizado: 2026-09-10" in k, "cabecera: afirma → aportacion, basado_en al inventario, y actualizado no se mueve")
ok((R / "ventas/cuentas/fuentes/inventario.md").is_file() and not (R / "ventas/cuentas/fuentes/enlaces.md").exists(), "fuentes/enlaces.md pasa a inventario.md")
ses = (R / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8")
cuerpo_antes = ses_antes.split("\n# ", 1)[1].split("\n", 1)[1]
ok(ses.split("\n## ")[1].startswith(s["hoy"] + " (migracion)\nTema: ") and "Sesión de: Ana Prueba · plugin 1.22.0" in ses and cuerpo_antes.strip() in ses and len(ses.split("\n## ")[1]) < 400, "una entrada (migracion) corta arriba, y las de antes, intactas")
ok(set(s["entradas"]) >= {"ventas/cuentas/sesiones.md", "archivo/historia/sesiones.md"}, "dice en qué sesiones.md dejó su entrada")

print("migrar_estructura.py: repetirlo no hace nada, y la raíz queda al día para abrir.py")
antes = huellas(R)
c, s2 = corre(R, "--cuenta", "ana@ejemplo.test")
ok(c == 0 and not s2["archivos"] and not s2["entradas"] and huellas(R) == antes, "la segunda vez no escribe nada")
o = subprocess.run([sys.executable, str(ABRIR), str(R), "--cuenta", "ana@ejemplo.test", "--minima"], capture_output=True, text=True).stdout
ok("Veredicto: AL DIA" in o, "abrir.py la da por al día para Ana")
o = subprocess.run([sys.executable, str(ABRIR), str(R), "--cuenta", "beto@ejemplo.test", "--minima"], capture_output=True, text=True).stdout
ok("Veredicto: ANTERIOR en personas" in o, "y a Beto le ofrece migrar su área")

print("migrar_estructura.py: nada se pierde cuando conviven el nombre viejo y el nuevo")
R5 = raiz_nueva()
am = R5 / "ventas/area.md"; t5 = am.read_text(encoding="utf-8")
# un cierre 1.22 escribió el Estatus sobre el Panorama y dejó «Prioridades ahora» (la persona dijo «Después» a la migración)
t5 = t5.replace("## Panorama\n2026-10-03 · Ventas tiene", "## Estatus\n2026-10-20 · **ESTATUS-NUEVO del área.**\n- **Siguiente:**\n  - Cerrar la propuesta de Cliente Uno. Es la única cuenta grande abierta.\n\n## Panorama-no\n2026-10-03 · Ventas tenía").replace("## Panorama-no", "## Qué era")
am.write_text(t5, encoding="utf-8")
pm = R5 / "ventas/precios/proyecto.md"; tp5 = pm.read_text(encoding="utf-8")
# alguien con el plugin 1.21 cerró después sobre un proyecto ya migrado: «En corto» nuevo junto a un «Estatus» viejo
tp5 = tp5.replace("## En corto\n", "## Estatus\n2026-10-01 · **ESTATUS-VIEJO.**\n\n## En corto\n").replace("## En corto\n2026-", "## En corto\n2026-10-22 · **CORTO-DE-CARLA.** Lo demás.\n- **Preocupa:** PREOCUPA-CARLA\n\n## X\n2026-", 1)
pm.write_text(tp5.replace("\n## X\n", "\n## Nota\n"), encoding="utf-8")
c, s5 = corre(R5, "--cuenta", "ana@ejemplo.test")
a5 = am.read_text(encoding="utf-8"); p5 = pm.read_text(encoding="utf-8")
ok(c == 0 and "## Prioridades ahora" not in a5 and "  - Ordenar los precios antes del cierre del trimestre." in a5 and "ESTATUS-NUEVO" in a5, "las prioridades que faltaban entran en «Siguiente» del Estatus que ya había")
ok("## En corto" not in p5 and "CORTO-DE-CARLA" in p5 and "PREOCUPA-CARLA" in p5 and "ESTATUS-VIEJO" not in p5 and "ESTATUS-VIEJO" in (R5 / "ventas/precios/taller/estado-anterior.md").read_text(encoding="utf-8"), "de dos bloques se queda el más reciente, con sus viñetas, y el otro va al taller")

print("migrar_estructura.py: si el taller no se deja escribir, proyecto.md no se toca")
R6 = raiz_nueva()
(R6 / "ventas/cuentas/taller").rename(R6 / "ventas/cuentas/taller-x"); (R6 / "ventas/cuentas/taller").write_text("no soy una carpeta", encoding="utf-8")
c, s6 = corre(R6, "--cuenta", "ana@ejemplo.test")
p6 = (R6 / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8")
ok(c == 1 and "## Estado actual" in p6 and "Segundo párrafo con detalle" in p6 and any(f["ruta"] == "ventas/cuentas/proyecto.md" and "nada se perdió" in f["motivo"] for f in s6["fallidos"]), "el Estado actual sigue en proyecto.md y fallidos lo dice")
R7 = raiz_nueva()
(R7 / "ventas/cuentas/taller/estado-anterior.md").write_text("ya estaba\n", encoding="utf-8")
c, s7 = corre(R7, "--cuenta", "ana@ejemplo.test")
p7 = (R7 / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8")
ok("## Estado actual" in p7 and "Responsable: Ana Prueba" in p7 and "Entra: Cliente Uno" in p7 and any("ya existía" in x["motivo"] for x in s7["conflictos"]) and (R7 / "ventas/cuentas/taller/estado-anterior.md").read_text(encoding="utf-8") == "ya estaba\n", "con un estado-anterior.md que ya existía, el resto se migra y «Estado actual» se queda")
o7 = subprocess.run([sys.executable, str(ABRIR), str(R7), "--cuenta", "ana@ejemplo.test", "--minima"], capture_output=True, text=True).stdout
ok("Veredicto: ANTERIOR en ventas" in o7, "y la apertura lo sigue ofreciendo, porque queda «Estado actual»")

print("migrar_estructura.py: plantillas, comillas y una segunda tabla")
R8 = raiz_nueva()
am8 = R8 / "operacion/area.md"; am8.write_text(am8.read_text(encoding="utf-8").replace("## Panorama\n", "## Panorama\n[Tres a cinco líneas del director]\nBORRAR\n").replace("BORRAR\n2026", "ZZ"), encoding="utf-8")
import re as _re
t8 = am8.read_text(encoding="utf-8"); t8 = _re.sub(r"## Panorama\n\[Tres a cinco líneas del director\]\n.*?(?=\n## )", "## Panorama\n[Tres a cinco líneas del director]\n", t8, flags=_re.S); am8.write_text(t8, encoding="utf-8")
pm8 = R8 / "ventas/cuentas/proyecto.md"; pm8.write_text(pm8.read_text(encoding="utf-8").replace("# Cuentas\n", '# Cuentas "grandes": el plan\n', 1), encoding="utf-8")
g8 = R8 / "guia.md"; g8.write_text(g8.read_text(encoding="utf-8").replace("\n## Quién responde por qué", "\nÁreas archivadas:\n\n| Área | Qué era | Dueño | Cuenta | Quién la lee |\n|---|---|---|---|---|\n| `vieja/` | nada | Ana Prueba | ana@ejemplo.test | Todo el equipo |\n\n## Quién responde por qué", 1), encoding="utf-8")
c, s8 = corre(R8, "--cuenta", "ana@ejemplo.test")
a8 = am8.read_text(encoding="utf-8")
ok(c == 0 and "**[" not in a8 and "- **Siguiente:**" in a8, "un Panorama de plantilla no da frase; las prioridades sí")
t8 = (R8 / "ventas/cuentas/taller/estado-anterior.md").read_text(encoding="utf-8")
ok(_re.search(r'^aportacion: "[^"\n]*(\\"[^"\n]*)*"$', t8, _re.M) is not None, "las comillas del título no rompen el YAML de aportacion")
g8t = g8.read_text(encoding="utf-8")
ok("| `vieja/` | nada | Ana Prueba | ana@ejemplo.test | Todo el equipo |" in g8t and "| Área | Qué era | Dueño |" in g8t and "| Responsable | Cuenta | Quién la lee | Acceso |" in g8t, "solo la primera tabla de «Áreas» se transforma")

print("migrar_estructura.py: otra cuenta y los conflictos")
R2 = raiz_nueva()
c, s3 = corre(R2, "--cuenta", "beto@ejemplo.test")
ok(c == 0 and s3["areas"] == ["personas", "legal"] and not s3["guia"] and "guia.md" not in s3["archivos"] and "Dueño" in (R2 / "guia.md").read_text(encoding="utf-8"), "quien no responde por el contexto no toca guia.md")
ok("ventas/area.md" not in s3["archivos"] and "## Panorama" in (R2 / "ventas/area.md").read_text(encoding="utf-8"), "ni las áreas de otra cuenta")
R3 = raiz_nueva()
(R3 / "ventas/cuentas/fuentes/inventario.md").write_text("ya estaba\n", encoding="utf-8")
c, s4 = corre(R3, "--cuenta", "ana@ejemplo.test")
ok(any("enlaces.md" in x["ruta"] for x in s4["conflictos"]) and (R3 / "ventas/cuentas/fuentes/enlaces.md").is_file() and (R3 / "ventas/cuentas/fuentes/inventario.md").read_text(encoding="utf-8") == "ya estaba\n", "si ya hay un inventario.md, no lo pisa y lo dice")
R4 = raiz_nueva()
f = R4 / "operacion/area.md"; f.write_bytes(f.read_text(encoding="utf-8").replace("\n", "\r\n").encode())
c, s5 = corre(R4, "--cuenta", "ana@ejemplo.test")
b = f.read_bytes()
ok(b"\r\n" in b and b"\n" not in b.replace(b"\r\n", b"") and b"## Estatus" in b, "un archivo con finales de línea de Windows sigue así")
c, s6 = corre(R4, "--cuenta", "nadie@ejemplo.test")
ok(c == 0 and not s6["areas"] and not s6["archivos"], "una cuenta sin áreas no migra nada")

print("\n" + ("Todo bien." if not fallos else f"{fallos} fallo(s)."))
sys.exit(1 if fallos else 0)
