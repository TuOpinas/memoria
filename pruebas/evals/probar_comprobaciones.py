#!/usr/bin/env python3
"""Las comprobaciones de formato de los evals (1.23.2), sin modelo: el recuadro como tabla de una columna fuera de cita y
de código, y lo que se enseña en cita antes de escribir. Corre con las demás pruebas del repo.

Uso: python3 pruebas/evals/probar_comprobaciones.py
"""
import pathlib, re, sys
src = (pathlib.Path(__file__).resolve().parent / "correr.py").read_text(encoding="utf-8")
g = {"re": re}
exec(src[src.index("def sin_codigo"):src.index('@comprobacion("recuadro")')], g)
exec(src[src.index("def cita_antes_de_escribir"):src.index('@comprobacion("cita-antes-de-escribir")')], g)
en_tabla, cita = g["en_tabla"], g["cita_antes_de_escribir"]
fallos = 0
def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1

C = r"Memoria (?:·|·) sesión cerrada (?:·|·) \d+ archivos?"
A = r"Memoria de trabajo ·"
print("El recuadro")
ok(en_tabla("Hecho.\n\n| Memoria · sesión cerrada · 5 archivos |\n|---|\n| a |", C), "tabla de una columna")
ok(en_tabla("| **Memoria de trabajo · Acme · v1.23.2** |\n| --- |\n", A), "cabecera en negrita y separador con espacios")
ok(en_tabla("| Memoria de trabajo · Acme · v1.23.2 |\r\n|:---|\r\n", A), "CRLF y separador alineado")
ok(not en_tabla("```\nMemoria · sesión cerrada · 5 archivos\n──\n```", C), "en bloque de código no vale")
ok(not en_tabla("```\n| Memoria · sesión cerrada · 5 archivos |\n|---|\n```", C), "tabla dentro de un bloque de código no vale")
ok(not en_tabla("~~~\n| Memoria · sesión cerrada · 5 archivos |\n|---|\n~~~", C), "ni dentro de ~~~")
ok(not en_tabla("> | Memoria · sesión cerrada · 5 archivos |\n> |---|\n", C), "en cita no vale")
ok(not en_tabla("| Memoria · sesión cerrada · 5 archivos |\n\n|---|\n", C), "una línea en blanco antes del separador no es tabla")
ok(en_tabla("Usa `` ``` `` para código.\n\n| Memoria · sesión cerrada · 2 archivos |\n|---|\n", C), "``` en prosa no se come el resto")

print("Lo que se enseña antes de escribir")
H = "2026-10-27"
bien = f"""Decisiones

> ## {H} · Una decisión
> Decidió: Ana Pérez
> Por qué: x.

Bitácora

> ## {H}
> Tema: y.
> Sesión de: Ana Pérez · plugin 1.23.2

Estatus

> {H} · **Todo bien.**
> - **Siguiente:** z.

¿Lo registro así?"""
ok(cita(bien, True, H)[0], "decisiones, bitácora y Estatus en cita")
lista = bien.replace(f"> ## {H} · Una decisión\n> Decidió: Ana Pérez\n> Por qué: x.", "- Una decisión, de Ana Pérez.")
ok(not cita(lista, True, H)[0], "decisiones resumidas en lista no vale")
ok(not cita(bien.replace(f"> {H} · **Todo bien.**\n> - **Siguiente:** z.", f"```\n{H} · **Todo bien.**\n```"), False, H)[0], "Estatus en bloque de código no vale")
ok(not cita(bien.replace(H, "2025-01-01"), False, H)[0], "una entrada vieja citada no cuenta como la de hoy")
ok(cita(bien.replace("Decisiones\n", "**Decisiones**\n").replace("Bitácora\n", "**Bitácora**\n"), True, H)[0], "las palabras en negrita valen")
ok(not cita(bien.replace("\nBitácora\n", "\n"), False, H)[0], "sin «Bitácora» no vale")

print("Cargas de skill y búsquedas del plugin (1.24.8)")
reg = {}
g2 = {"re": re, "comprobacion": lambda n: (lambda f: reg.__setitem__(n, f) or f)}
exec(src[src.index('@comprobacion("skill")'):src.index('@comprobacion("palabras-maximo")')], g2)
exec(src[src.index('@comprobacion("no-menciona-re")'):src.index('@comprobacion("menciona")')], g2)
H_ = lambda n, e: {"nombre": n, "entrada": e}
ctx = {"turnos": [{"herramientas": [H_("Skill", {"skill": "memoria:sesion"}), H_("mcp__remote-devices__device_bash", {"command": "cd $HOME/memoria && python3 abrir.py x"})]}]}
ok(reg["skill"](ctx, "sesion 1")[0] and not reg["skill"](ctx, "sesion 0")[0], "cuenta las cargas de una skill con su prefijo de plugin")
ok(reg["sin-buscar-plugin"](ctx, "")[0], "abrir.py desde $HOME/memoria no es buscar el plugin")
ctx["turnos"][0]["herramientas"].append(H_("Bash", {"command": "find /root/.claude/plugins -path '*/memoria*/skills/tablero'"}))
ok(not reg["sin-buscar-plugin"](ctx, "")[0], "un find bajo .claude/plugins sí")
g2["texto_de"] = lambda t: "\n".join(t["respuestas"])
ctx2 = {"turnos": [{"respuestas": ["| Memoria · lo que marcaste en el tablero · 2 |\n| **Beto Prueba** aceptó «x» |"]}]}
pat = r"Beto( Prueba)?\W{0,8}(acept|cuestion)|(acept|cuestion)\w*\W{0,12}Beto"
ok(not reg["no-menciona-re"](ctx2, pat + "@1")[0], "«**Beto Prueba** aceptó» casa con la expresión del eval 14")
ctx2["turnos"][0]["respuestas"] = ["Aceptaste «x», de Beto Prueba."]
ok(reg["no-menciona-re"](ctx2, pat + "@1")[0], "«Aceptaste «x», de Beto Prueba» no casa")
print("La marca del tablero (1.25.1)")
g["json"] = __import__("json")
exec("COMPROBACIONES = {}\ndef comprobacion(n):\n    def d(f):\n        COMPROBACIONES[n] = f\n        return f\n    return d\n", g)
exec(src[src.index('@comprobacion("marca-tablero")'):src.index('@comprobacion("herramienta")')], g)
marca = g["COMPROBACIONES"]["marca-tablero"]
class _T:
    escritos = [{"op": "set", "path": "cierres/ventas--cuentas--202611032159", "data": {"proyecto": "ventas--cuentas", "nombre": "Cuentas", "hora": "2026-11-03T21:59Z", "cuenta": "ana@ejemplo.test"}}]
ok(marca({"tablero": _T()}, "ventas/cuentas")[0], "una marca bien formada en cierres pasa")
_T.escritos = [dict(_T.escritos[0], ifVersion=1)]
ok(not marca({"tablero": _T()}, "ventas/cuentas")[0], "con ifVersion no pasa (es un documento nuevo)")
_T.escritos = []
ok(not marca({"tablero": _T()}, "ventas/cuentas")[0], "sin marca no pasa")
ok(not marca({"tablero": None}, "ventas/cuentas")[0], "sin tablero de mentira no pasa")

print("El cierre con su script (1.25.1)")
exec(src[src.index('@comprobacion("cierre-con-script")'):src.index('@comprobacion("herramienta")')], g)
cs = g["COMPROBACIONES"]["cierre-con-script"]
_cerr = {"nombre": "Bash", "entrada": {"command": "python3 cerrar.py x"}, "resultado": '{"escritos": []}'}
_lst = {"nombre": "Write", "entrada": {"file_path": "/tmp/listado.json", "content": '{"entries": [{"name": "proyecto.md"}, {"name": "sesiones.md"}]}'}}
_mal = {"nombre": "Write", "entrada": {"file_path": "/tmp/copia/ventas/cuentas/sesiones.md", "content": "x"}}
ok(cs({"turnos": [{"herramientas": [_lst, _cerr]}]}, "")[0], "un Write del listado o de cambios.json que nombra los registros no es escribir a mano")
ok(not cs({"turnos": [{"herramientas": [_mal, _cerr]}]}, "")[0], "un Write sobre sesiones.md sí")

print("El cierre corto (1.26.4)")
_c = f"""Decisiones

> ## {H} · Una decisión
> Decidió: Ana Pérez
> Por qué: x.

Bitácora

La revisión de la propuesta; escribió taller/x.md.

Estatus

> {H} · **Todo bien.**

¿Lo registro así?"""
ok(cita(_c, True, H)[0], "la bitácora en una línea y del Estatus solo su frase en cita valen")
ok(not cita(_c.replace(f"> {H} · **Todo bien.**", f"{H} · Todo bien."), True, H)[0], "la frase del Estatus sin cita no vale")
ok(not cita(_c.replace(f"> ## {H} · Una decisión\n> Decidió: Ana Pérez\n> Por qué: x.", "La decisión: una decisión."), True, H)[0], "la decisión sigue yendo entera en cita")
ok(not cita(_c.replace("> Decidió: Ana Pérez\n> Por qué: x.", "Decidió Ana; por x."), True, H)[0], "solo el título en cita no basta: Decidió y Por qué también")

print("La decisión de hoy con su «Afecta a» (1.26.5)")
import tempfile, datetime as _dt
from zoneinfo import ZoneInfo as _Z
g3 = {"re": re, "pathlib": pathlib, "HOY": _dt.datetime.now(_Z("America/Mexico_City")).date().isoformat()}
exec("COMPROBACIONES = {}\ndef comprobacion(n):\n    def d(f):\n        COMPROBACIONES[n] = f\n        return f\n    return d\n", g3)
exec(src[src.index('@comprobacion("decision-afecta")'):src.index('@comprobacion("apertura-minima")')], g3)
da = g3["COMPROBACIONES"]["decision-afecta"]
_r = pathlib.Path(tempfile.mkdtemp()); (_r / "v/c").mkdir(parents=True)
_vieja = "## 2026-09-26 · Vieja\nDecidió: A\nAfecta a: personas\n"
_hoy = g3["HOY"]
def _con(texto):
    (_r / "v/c/decisiones.md").write_text("# Decisiones\n\n" + texto + _vieja, encoding="utf-8")
    return {"raiz": _r, "antes_textos": {"v/c/decisiones.md": "# Decisiones\n\n" + _vieja}}
ok(da(_con(f"## {_hoy} · Nueva\nDecidió: A\nAfecta a: personas (la nómina)\n\n"), "v/c personas")[0], "la nueva de hoy con el área pasa")
ok(not da(_con(f"## {_hoy} · Nueva\nDecidió: A\n\n"), "v/c personas")[0], "sin «Afecta a» no pasa, aunque la vieja lo lleve")
ok(not da(_con(f"## {_hoy} · Nueva\nDecidió: A\nAfecta a: personas-x\n\n"), "v/c personas")[0], "otro nombre que empieza igual no pasa")
ok(not da(_con(f"## {_hoy} · Nueva\nDecidió: A\nAfecta a: personas\n\n"), "v/c")[0], "sin texto no pasa")

print("El recuadro del mantenimiento como tabla (1.26.6)")
g4 = {"re": re}
exec("COMPROBACIONES = {}\ndef comprobacion(n):\n    def d(f):\n        COMPROBACIONES[n] = f\n        return f\n    return d\n", g4)
exec(src[src.index("def texto_de("):src.index("def entradas_registro(")], g4)
exec(src[src.index("def sin_codigo("):src.index('@comprobacion("recuadro")')], g4)
exec(src[src.index('@comprobacion("tabla")'):src.index('@comprobacion("recuadro-cierre")')], g4)
tb = g4["COMPROBACIONES"]["tabla"]
_t = lambda r: {"turnos": [{"respuestas": [r]}]}
ok(tb(_t("| Memoria · mantenimiento · 2026-11-17 |\n|---|\n| Adopción · bien |"), "Memoria · mantenimiento@1")[0], "la cabecera en una tabla pasa")
ok(not tb(_t("Memoria · mantenimiento · 2026-11-17: todo bien"), "Memoria · mantenimiento@1")[0], "como texto no pasa")
ok(not tb(_t("```\n| Memoria · mantenimiento |\n|---|\n```"), "Memoria · mantenimiento@1")[0], "dentro de un bloque de código no pasa")

print("El recuadro de lectura, al final y con su pregunta (1.26.10)")
import json
g5 = {"re": re, "json": json}
exec("COMPROBACIONES = {}\ndef comprobacion(n):\n    def d(f):\n        COMPROBACIONES[n] = f\n        return f\n    return d\n", g5)
exec(src[src.index("def texto_de("):src.index("def entradas_registro(")], g5)
exec(src[src.index("def sin_codigo("):src.index('@comprobacion("recuadro")')], g5)
exec(src[src.index('@comprobacion("tabla")'):src.index('@comprobacion("recuadro-cierre")')], g5)
K = g5["COMPROBACIONES"]
_h = lambda r, h=(): {"turnos": [{"respuestas": r if isinstance(r, list) else [r], "herramientas": list(h)}]}
LECT = "| Memoria · lectura · cuentas y soporte |\n|---|\n| **Leí:** las decisiones · 9 KB |\n| **Dejé fuera:** la nota de incidencias (60 KB) |\n"
PREG = "¿Leo también la nota de incidencias? Son 60 KB: enseguida."
bien = "Cuadran, salvo el plazo de soporte.\n\n" + LECT + "\n" + PREG
ok(K["tabla-al-final"](_h(bien), "Memoria · lectura@1")[0], "respuesta, recuadro y pregunta pasa")
ok(not K["tabla-al-final"](_h(LECT), "Memoria · lectura@1")[0], "el recuadro sin respuesta antes no pasa")
ok(not K["tabla-al-final"](_h(["Leo soporte y precios.", LECT + "Cuadran.\n" + PREG]), "Memoria · lectura@1")[0], "narración antes de una herramienta y la respuesta detrás del recuadro no pasa")
ok(not K["tabla-al-final"](_h("Reviso.\n" + LECT + "Cuadran.\nSalvo el plazo."), "Memoria · lectura@1")[0], "una respuesta corta detrás del recuadro no pasa")
ok(not K["tabla-al-final"](_h("Cuadran.\n\n| Memoria · lectura · cuentas |\n|---|\n| algo |\n"), "Memoria · lectura@1")[0], "sin las filas Leí y Dejé fuera no pasa")
ok(not K["tabla-al-final"](_h("Lectura: a fondo · Memoria · lectura · x\n\nCuadran."), "Memoria · lectura@1")[0], "como texto no pasa")
ok(not K["tabla-al-final"](_h(bien + "\n\n| Memoria · avisos · 1 |\n|---|\n| x |"), "Memoria · lectura@1")[0], "otro recuadro después no pasa")
ok(K["tabla-al-final"](_h(["Leo soporte.", bien]), "Memoria · lectura@1")[0], "mide el último bloque del turno")
ok(K["sin-tabla"](_h("Va bien: falta la firma."), "Memoria · lectura@1")[0], "sin recuadro pasa")
ok(not K["sin-tabla"](_h(bien), "Memoria · lectura@1")[0], "con recuadro no pasa")
ok(K["pregunta-leer"](_h(bien), "incidencias@1")[0], "la pregunta en texto bajo el recuadro pasa")
ok(K["pregunta-leer"](_h("Cuadran.\n\n" + LECT + "\n¿La leo también? Son 60 KB."), "incidencias@1")[0], "con el nombre en la fila Dejé fuera pasa")
ok(not K["pregunta-leer"](_h("Cuadran.\n\n" + LECT + "\n¿Registramos hoy el trabajo de la nota de incidencias?"), "incidencias@1")[0], "otra pregunta que la nombra no pasa")
ok(not K["pregunta-leer"](_h(PREG + "\n\n" + LECT), "incidencias@1")[0], "la pregunta antes del recuadro no pasa")
ok(not K["pregunta-leer"](_h("Cuadran.\n\n" + LECT), "incidencias@1")[0], "sin pregunta no pasa")
ok(not K["pregunta-leer"](_h(bien, [{"nombre": "AskUserQuestion", "entrada": {"questions": [{"question": "¿Leo la nota de incidencias?"}]}}]), "incidencias@1")[0], "con la herramienta de preguntas no pasa")
ok(K["pregunta-tamano"](_h("Son 619 KB. ¿Los leo todos o solo los de 1.26?"), "@1")[0], "la pregunta previa con el tamaño pasa")
ok(not K["pregunta-tamano"](_h("Resumen: todo bien."), "@1")[0], "sin preguntar no pasa")
ok(K["primera-frase"](_h("Esto resume la nota de incidencias, una de las cinco.\nDetalle."), "incidencias@1")[0], "la primera frase dice la parte")
ok(not K["primera-frase"](_h("Detalle.\nEsto resume solo la de incidencias."), "incidencias@1")[0], "dicho después no pasa")
M = "NOTA-LEIDA-incidencias-cliente-uno"
leer = {"nombre": "mcp__remote-devices__device_bash", "entrada": {"command": "cat ventas/cuentas/taller/*.md"}, "resultado": f"... {M}-20\n...\nFIN-{M}\n"}
medir = {"nombre": "mcp__remote-devices__device_bash", "entrada": {"command": "head -6 ventas/cuentas/taller/incidencias-cliente-uno.md"}, "resultado": "---\nestado: borrador\n"}
ok(K["lee"](_h("x", [leer]), M + "@1")[0], "leerla entera, aunque sea con un comodín, cuenta")
ok(not K["lee"](_h("x", [medir]), M + "@1")[0], "mirar su cabecera no es leerla")
ok(K["no-lee"](_h("x", [medir]), M + "@1")[0], "y no-lee pasa con la cabecera")
ok(not K["no-lee"](_h("x", [leer]), M + "@1")[0], "no-lee falla si la abrió")
NIV = [r"(?m)^\W*lectura\W{0,3}:", r"lectura · (?:de |nivel )?(?:proyecto|a fondo|básico)\b"]
mal = ["**Lectura:** de proyecto · decisiones.md", "Lectura:\nde proyecto", "| Memoria · lectura · de proyecto |", "| Memoria · lectura · a fondo |"]
ok(all(any(re.search(p, x, re.I) for p in NIV) for x in mal), "las expresiones del eval 19 cazan la línea vieja y el nivel en la cabecera")
ok(not any(re.search(p, x, re.I) for p in NIV for x in ["Dejé fuera de la lectura: la nota", "lo reviso a fondo mañana", "A nivel de proyecto, va bien"]), "y no el español corriente")

print("\n" + ("Todo bien." if not fallos else f"{fallos} fallo(s)."))
sys.exit(1 if fallos else 0)
