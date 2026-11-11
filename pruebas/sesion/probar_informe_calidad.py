#!/usr/bin/env python3
"""Prueba comprobar_informe.py de la skill calidad (1.26.2): qué informe se puede medir y cuál no.

Uso: python3 pruebas/sesion/probar_informe_calidad.py

Está aquí porque CI corre pruebas/sesion/probar_*.py con el Python de la matriz (también 3.9).
"""
import pathlib, subprocess, sys, tempfile

AQUI = pathlib.Path(__file__).resolve().parent
SCRIPT = AQUI.parent.parent / "plugins/memoria/skills/calidad/comprobar_informe.py"
fallos = 0


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1


def medicion(hall="3 · impiden 1 · riesgo 1 · mejoran 1", modelo="Fable 5.2 (E, R, O)", raz="medio", tokens="432k"):
    return ("## Medición\nFecha: 2026-11-10\nTipo: parche · Tamaño: 58 líneas de diff\nProfundidad: normal · Revisores: 3 · Lentes: E, R, O\n"
            f"Modelo: {modelo}\nRazonamiento: {raz}\nConstruyó: Opus 5.5\nHallazgos: {hall}\nArreglados: 0\nTokens: {tokens}\n")


E1 = "### 1. Uno\nLens: errors, risks · Pesa: impide cumplir el objetivo\nDónde: a.sh:1\n\n"
E2 = "### 2. Dos\nLens: risks (planteado como duda por objective) · Pesa: pone en riesgo el objetivo\nDónde: b.sh:2\n\n"
E3 = "### 3. Tres\nLens: efficiency · Pesa: lo mejora\nPropuesta:\n1. **Primero** (risks, si aplica) esto.\n\n"
BUENO = "# Informe\n\n## Yardstick\n1. **La regla** (errores, riesgos y objetivo).\n\n## Hallazgos\n\n" + E1 + E2 + E3


def corre(texto):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8", newline="") as f:
        f.write(texto)
    r = subprocess.run([sys.executable, str(SCRIPT), f.name], capture_output=True, text=True)
    pathlib.Path(f.name).unlink()
    return r.returncode, r.stdout


def acepta(texto, t):
    c, out = corre(texto); ok(c == 0, t + ("" if c == 0 else f" — dijo: {out.strip()[:160]}"))


def rechaza(texto, que, t):
    c, out = corre(texto); ok(c == 1 and que in out, t + ("" if c == 1 and que in out else f" — dijo: {out.strip()[:160]}"))


print("comprobar_informe.py")
acepta(BUENO + medicion(), "acepta un informe con sus tres entradas, una lista en el yardstick y otra dentro de una propuesta")
acepta(BUENO.replace("\n", "\r\n") + medicion().replace("\n", "\r\n"), "acepta el mismo con CRLF")
acepta(BUENO + "## Dudas\n\n### Una duda\nQué faltaría: x\n\n```\nLente: errores · Pesa: lo mejora\nLens: errors · Pesa: lo mejora\n```\n\n" + medicion()
       + "\n" + medicion(hall="9 · impiden 0 · riesgo 9 · mejoran 0") + "\n## Lo que se escapó\n- 2026-11-12 · uso real · a su alcance · lo habría visto: risks · impide · x\n",
       "acepta dudas sin «Lens:», un bloque de código que cita los dos formatos y una medición anterior debajo")
rechaza(BUENO.replace(E3, "") + "## Improves it\n\n3. **Tres** (efficiency): una mejora en lista.\n\n" + medicion(), "en una lista",
        "rechaza una mejora en una lista numerada")
rechaza(BUENO.replace(E3, "") + "## Lo mejora\n\n- **Tres** (eficiencia): una mejora.\n\n" + medicion(), "en una lista", "y en una lista con guiones y la lente en español")
rechaza(BUENO.replace("Lens: efficiency", "Lente: eficiencia") + medicion(), "«Lente:» pasó a «Lens:»", "rechaza «Lente:»")
rechaza(BUENO.replace("Lens: efficiency", "Lens: eficiencia") + medicion(), "no existen o no van en inglés", "rechaza una lente en español con las cuentas bien")
rechaza(BUENO.replace("Lens: efficiency", "Lens: E") + medicion(), "la forma", "rechaza «Lens: E»")
rechaza(BUENO.replace("Lens: efficiency", "Lens: banana") + medicion(), "no existen", "rechaza una lente inventada")
rechaza(BUENO.replace("· Pesa: lo mejora", "· Pesa: grave") + medicion(), "«Pesa: grave»", "rechaza un peso inventado")
rechaza(BUENO.replace("Lens: errors, risks · Pesa", "Lens: errors, risks | Pesa") + medicion(), "la forma", "rechaza otro separador")
rechaza(BUENO + "Lens: errors · Pesa: lo mejora\n" + medicion(), "fuera de una entrada", "rechaza un «Lens:» suelto")
rechaza(BUENO.replace("### 3. Tres\nLens: efficiency · Pesa: lo mejora\n", "### 3. Tres\nTexto.\n") + medicion(), "no lleva su línea", "rechaza una entrada sin «Lens:»")
rechaza(BUENO + medicion(hall="4 · impiden 1 · riesgo 1 · mejoran 2"), "su medición más nueva dice 4", "rechaza menos entradas que hallazgos")
rechaza(BUENO + medicion(hall="3 · impiden 0 · riesgo 1 · mejoran 2"), "impiden 0", "rechaza los pesos que no cuadran")
rechaza(BUENO + medicion(modelo="Fable 5.2 (E, R, O) · Opus 5.5 (E, R) · contraste", tokens="693k · Fable 5.2 360k · Opus 5.5 333k"),
        "«· Modelo: los dos»", "rechaza un contraste sin «Modelo:» en cada hallazgo")
rechaza(BUENO.replace("lo mejora\n", "lo mejora · Modelo: los dos\n").replace("objetivo\nD", "objetivo · Modelo: Fable 5.2\nD")
        + medicion(modelo="Fable 5.2 (E, R, O) · Opus 5.5 (E, R) · contraste"), "los de cada modelo", "rechaza un contraste sin los tokens de cada modelo")
rechaza(BUENO + medicion(raz="normalito"), "el nivel es uno de", "rechaza un nivel de razonamiento fuera de la lista")
rechaza(BUENO + medicion().replace("Razonamiento: medio\n", ""), "Razonamiento: medio", "rechaza una medición sin razonamiento")
rechaza(BUENO + "## Doubts\n\n### 4. Duda\nLens: risks · Pesa: lo mejora\n\n" + medicion(), "una duda no lleva", "rechaza una duda con «Lens:»")
acepta(BUENO + medicion(raz="Fable 5.2 medio · Opus 5.5 alto"), "acepta un nivel por modelo")
print(); print("Todo bien." if fallos == 0 else f"{fallos} fallo(s).")
sys.exit(1 if fallos else 0)
