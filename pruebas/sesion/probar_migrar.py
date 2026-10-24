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


print("migrar_estructura.py: las marcas de la estructura vieja son las mismas que mira abrir.py")
def marcas(ruta):
    src = ruta.read_text(encoding="utf-8"); i = src.index("ESTRUCTURA_VIEJA = {"); j = src.index("\n}\n", i) + 2
    ns = {}; exec(src[i:j], ns); return ns["ESTRUCTURA_VIEJA"]
ok(marcas(MIG) == marcas(ABRIR), "ESTRUCTURA_VIEJA igual en los dos scripts")

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
ok("| Área | Qué es | Responsable | Cuenta | Quién la lee | Acceso |" in g and "| Dirección | Restringida |" in g and "| Todo el equipo | Abierta |" in g, "guia.md: Responsable, Acceso y «Quién la lee» con a quiénes")
a = (R / "ventas/area.md").read_text(encoding="utf-8")
ok("## Panorama" not in a and "## Prioridades ahora" not in a and a.index("## Estatus") < a.index("## Qué es") < a.index("## Proyectos") < a.index("## Quién participa"), "area.md: Estatus primero, sin Panorama ni Prioridades ahora")
ok("2026-10-03 · **Ventas tiene una sola cuenta grande abierta" in a and "  - Cerrar la propuesta de Cliente Uno." in a and "Responsable: Ana Prueba" in a and "restringido: responsable Beto Prueba." in a, "el Estatus lleva la fecha y la frase del Panorama y las prioridades debajo de «Siguiente»")
ok("  - kit-cuentas — Una cuenta se prepara en cinco pasos. · actualizado 2026-09-10" in a, "la línea del entregable vigente se toma de su aportacion")
p = (R / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8")
ok("## Terminado significa" not in p and "a la firma. Cliente Uno firmado." in p and "Entra: Cliente Uno. No entra: precios" in p, "proyecto.md: Terminado significa en Objetivo; Entra / No entra")
ok("## Estado actual" not in p and "Consumen esto" not in p and "Responsable: Ana Prueba" in p and p.index("## Objetivo") < p.index("## Alcance") < p.index("## Siguientes pasos") < p.index("## Quién participa"), "sin Estado actual ni Consumen esto, y en el orden de la 1.22")
t = (R / "ventas/cuentas/taller/estado-anterior.md").read_text(encoding="utf-8")
ok("Segundo párrafo con detalle" in t and t.startswith("---\nestado: borrador\nactualizado: 2026-10-01\naportacion: ") and "basado_en:\n  - ventas/cuentas/proyecto.md" in t, "el Estado actual va entero al taller, con su cabecera")
h = (R / "archivo/historia/proyecto.md").read_text(encoding="utf-8")
ok("## Estatus\n2026-09-01 · **Proyecto terminado el 2026-09-01.**" in h, "un proyecto cerrado lo dice en su Estatus")
k = (R / "ventas/cuentas/entregables/kit-cuentas.md").read_text(encoding="utf-8")
ok('aportacion: "Una cuenta se prepara en cinco pasos."' in k and "afirma:" not in k and "fuentes/inventario.md" in k and "actualizado: 2026-09-10" in k, "cabecera: afirma → aportacion, basado_en al inventario, y actualizado no se mueve")
ok((R / "ventas/cuentas/fuentes/inventario.md").is_file() and not (R / "ventas/cuentas/fuentes/enlaces.md").exists(), "fuentes/enlaces.md pasa a inventario.md")
ses = (R / "ventas/cuentas/sesiones.md").read_text(encoding="utf-8")
cuerpo_antes = ses_antes.split("\n# ", 1)[1].split("\n", 1)[1]
ok(ses.split("\n## ")[1].startswith(s["hoy"] + " (migracion)\nTema: ") and "Sesión de: Ana Prueba · plugin 1.22.0" in ses and cuerpo_antes.strip() in ses, "una entrada (migracion) arriba, y las de antes, intactas")
ok(set(s["entradas"]) >= {"ventas/cuentas/sesiones.md", "archivo/historia/sesiones.md"}, "dice en qué sesiones.md dejó su entrada")

print("migrar_estructura.py: repetirlo no hace nada, y la raíz queda al día para abrir.py")
antes = huellas(R)
c, s2 = corre(R, "--cuenta", "ana@ejemplo.test")
ok(c == 0 and not s2["archivos"] and not s2["entradas"] and huellas(R) == antes, "la segunda vez no escribe nada")
o = subprocess.run([sys.executable, str(ABRIR), str(R), "--cuenta", "ana@ejemplo.test", "--minima"], capture_output=True, text=True).stdout
ok("Veredicto: AL DIA en lo que escribe esta cuenta" in o, "abrir.py la da por al día para Ana")
o = subprocess.run([sys.executable, str(ABRIR), str(R), "--cuenta", "beto@ejemplo.test", "--minima"], capture_output=True, text=True).stdout
ok("Veredicto: ANTERIOR en personas:" in o, "y a Beto le ofrece migrar su área")

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
