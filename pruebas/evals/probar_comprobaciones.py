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
print("\n" + ("Todo bien." if not fallos else f"{fallos} fallo(s)."))
sys.exit(1 if fallos else 0)
