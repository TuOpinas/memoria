#!/usr/bin/env python3
"""Qué es la organización (1.22.4): el primer párrafo de guia.md sale arriba de Inicio solo si habla de la organización.
Con el párrafo de la plantilla de antes o con un hueco sin llenar no sale, y Mantenimiento lo pide; las frases sobre el
método o sus archivos se quitan.

Uso: python3 pruebas/tablero/probar_que_es.py
"""
import json, pathlib, shutil, subprocess, sys, tempfile

AQUI = pathlib.Path(__file__).resolve().parent
GV = AQUI.parents[1] / "plugins" / "memoria" / "skills" / "tablero" / "generar_vista.py"
fallos = 0


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1


def generar(parrafo):
    tmp = pathlib.Path(tempfile.mkdtemp())
    raiz = tmp / "raiz"; shutil.copytree(AQUI / "raiz", raiz)
    g = (raiz / "guia.md").read_text(encoding="utf-8")
    titulo, resto = g.split("\n", 1)
    viejo = resto.strip().split("\n\n", 1)
    (raiz / "guia.md").write_text(titulo + "\n\n" + parrafo + "\n\n" + viejo[1], encoding="utf-8")
    subprocess.run([sys.executable, str(GV), str(raiz), str(tmp / "out"), "--version", "prueba"], check=True, stdout=subprocess.DEVNULL)
    m = json.loads((tmp / "out" / "meta" / "estado.json").read_text(encoding="utf-8"))
    m = m.get("data", m)
    shutil.rmtree(tmp)
    return m.get("que_es", ""), [f for f in m.get("fuera", []) if f.get("que_es")]


print("Qué es la organización, arriba de Inicio")
q, f = generar("Esta carpeta es la memoria de trabajo de Acme, la empresa de Ana: cada área documenta aquí sus proyectos.")
ok(q == "" and len(f) == 1, "el párrafo de la plantilla de antes no sale, y Mantenimiento pide escribirlo")
q, f = generar("Acme es [a qué se dedica y para quién, en una o dos frases].")
ok(q == "" and len(f) == 1, "con el hueco de la plantilla sin llenar, tampoco")
q, f = generar("Acme fabrica [muebles](https://acme.test) para oficinas en Monterrey.")
ok(q.startswith("Acme fabrica") and not f, "un enlace no es un hueco de la plantilla")
q, f = generar("Esta carpeta es la memoria de los asuntos de Ana: su casa y su familia. Sigue el método del plugin `memoria`, porque la ventaja es la misma. Cómo se trabaja está en `metodo.md` y no hace falta leerlo.")
ok(q == "Esta carpeta es la memoria de los asuntos de Ana: su casa y su familia." and not f, "las frases sobre el método y sus archivos no salen; el resto sí")
q, f = generar("| Área | Qué es |\n|---|---|\n| `x/` | y |")
ok(not f, "una tabla no es un hueco: no se pide nada")
print("Personas de fuera, como dato (1.22.4)")
import ast, re
_src = GV.read_text(encoding="utf-8"); _ns = {"re": re}
for n in ast.parse(_src).body:
    if any(isinstance(t, ast.Name) and t.id in ("_PART", "PERSONA_FUERA") for t in getattr(n, "targets", [])):
        exec(compile(ast.Module([n], []), str(GV), "exec"), _ns)
pf = lambda t: [m.group(1) for m in _ns["PERSONA_FUERA"].finditer(t)]
ok(pf("Esperar la firma de Agustín Torres (Escuela Fácil) antes del viernes") == ["Agustín Torres"], "«Nombre Apellido (Organización)» es una persona de fuera")
ok(pf("Migrar el Sistema Nuevo Contable antes del cierre") == [], "unas palabras con mayúscula no son una persona")
ok(pf("Hablar con Ana María de la Fuente (Acme)") == ["Ana María de la Fuente"], "con partículas en el apellido")
ok(pf("Revisar con Luis Romero (luis@acme.test)") == [] and pf("Cierre de Finanzas (2026-10-03)") == [], "ni una cuenta ni una fecha entre paréntesis hacen una organización")
print("\nTodo bien." if not fallos else f"\n{fallos} fallos.")
sys.exit(1 if fallos else 0)
