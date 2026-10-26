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


def dos_corridas(raiz, tmp):
    """Como la puesta al día real: inventario y generación sobre la copia, y una segunda corrida que reutiliza la base.
    Devuelve (primera, segunda, reutilizó algo)."""
    def corrida(sal, previos=None, sin_cambios=None):
        a = [sys.executable, str(GV), str(raiz), "--inventario"] + (["--sin-cambios", sin_cambios] if sin_cambios else [])
        inv = json.loads(subprocess.run(a, capture_output=True, text=True, check=True).stdout)
        ip = tmp / f"inv-{sal}.json"; ip.write_text(json.dumps(inv["inventario"]), encoding="utf-8")
        cop = tmp / f"copia-{sal}"
        for r_ in inv["leer"]:
            (cop / r_).parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(raiz / r_, cop / r_)
        cop.mkdir(exist_ok=True)
        subprocess.run([sys.executable, str(GV), str(cop), str(tmp / sal), "--desde-inventario", str(ip), "--version", "prueba"]
                       + (["--previos", str(previos)] if previos else []), check=True, stdout=subprocess.DEVNULL)
        return inv
    corrida("o1")
    est = json.loads((tmp / "o1" / "meta" / "estado.json").read_text(encoding="utf-8"))
    inv = corrida("o2", tmp / "o1", ",".join(est.get("huellas") or []))
    return tmp / "o1", tmp / "o2", bool(inv["inventario"].get("reusar")) and bool(inv["inventario"].get("fuera_reusar"))


def generar(parrafo, dos_veces=False, abrir=False):
    tmp = pathlib.Path(tempfile.mkdtemp())
    raiz = tmp / "raiz"; shutil.copytree(AQUI / "raiz", raiz)
    g = (raiz / "guia.md").read_text(encoding="utf-8")
    titulo, resto = g.split("\n", 1)
    viejo = resto.strip().split("\n\n", 1)
    (raiz / "guia.md").write_text(titulo + "\n\n" + parrafo + "\n\n" + viejo[1], encoding="utf-8")
    subprocess.run([sys.executable, str(GV), str(raiz), str(tmp / "out"), "--version", "prueba"], check=True, stdout=subprocess.DEVNULL)
    if dos_veces:   # la segunda corrida reutiliza la base: «fuera» viene de meta/estado (revisión 1.22.4, hallazgo 1)
        _, o2, reuso = dos_corridas(raiz, tmp)
        m = json.loads((o2 / "meta" / "estado.json").read_text(encoding="utf-8")); m["_reuso"] = reuso
        if not reuso: m["fuera"] = m.get("fuera", []) + [{"que_es": True}] * 9   # sin reutilizar, la prueba no prueba nada: falla
    else:
        m = json.loads((tmp / "out" / "meta" / "estado.json").read_text(encoding="utf-8"))
    if abrir:
        r = subprocess.run([sys.executable, str(AQUI.parents[1] / "plugins" / "memoria" / "skills" / "sesion" / "abrir.py"), str(raiz), "--minima", "--cuenta", "ana@ejemplo.test"], capture_output=True, text=True)
        m["_abrir"] = r.stdout
    m = m.get("data", m)
    shutil.rmtree(tmp)
    if abrir:
        return m
    return m.get("que_es", ""), [f for f in m.get("fuera", []) if f.get("que_es")]


print("Qué es la organización, arriba de Inicio")
q, f = generar("Esta carpeta es la memoria de trabajo de Acme, la empresa de Ana: cada área documenta aquí sus proyectos.")
ok(q == "" and len(f) == 1, "el párrafo de la plantilla de antes no sale, y Mantenimiento pide escribirlo")
q, f = generar("Acme es [a qué se dedica y para quién, en una o dos frases].")
ok(q == "" and len(f) == 1, "con el hueco de la plantilla sin llenar, tampoco")
q, f = generar("Acme fabrica muebles para oficinas en Monterrey; el mapa de la carpeta está en `guia.md`. Esto lo aplica el plugin `memoria`.")
ok(q == "Acme fabrica muebles para oficinas en Monterrey." and not f, f"de una frase unida con «;» a otra sobre la carpeta se queda lo de la organización (1.22.5) ({q!r})")
q, f = generar("Acme fabrica [muebles](https://acme.test) para oficinas en Monterrey.")
ok(q.startswith("Acme fabrica") and not f, "un enlace no es un hueco de la plantilla")
q, f = generar("Esta carpeta es la memoria de los asuntos de Ana: su casa y su familia. Sigue el método del plugin `memoria`, porque la ventaja es la misma. Cómo se trabaja está en `metodo.md` y no hace falta leerlo.")
ok(q == "Esta carpeta es la memoria de los asuntos de Ana: su casa y su familia." and not f, "las frases sobre el método y sus archivos no salen; el resto sí")
q, f = generar("**Acme** fabrica muebles para oficinas en Monterrey.")
ok(q.startswith("Acme fabrica") and not f, "la negrita no esconde el párrafo")
q, f = generar("Acme vende [sic] muebles y cita a [Bodegas][1].")
ok(q.startswith("Acme vende") and not f, "«[sic]» o un enlace por referencia no son huecos de la plantilla")
q, f = generar("Cómo se trabaja está en `metodo.md`, que no hace falta leer.")
ok(q == "" and len(f) == 1, "si solo tenía frases del método, queda vacío y se pide")
q, f = generar("Esta carpeta es la memoria de trabajo de Acme: cada área documenta aquí sus proyectos.", dos_veces=True)
ok(len(f) == 1, f"al reutilizar la base, el aviso no se duplica ({len(f)})")

m_ = generar("Esta carpeta es la memoria de trabajo de Acme: cada área documenta aquí sus proyectos.", abrir=True)
ok("no dice qué es la organización" in m_.get("_abrir", ""), "la apertura se lo dice a quien responde por el contexto")
print("Personas de fuera, como dato (1.22.4)")
import ast, re
_src = GV.read_text(encoding="utf-8"); _ns = {"re": re}
for n in ast.parse(_src).body:
    if any(isinstance(t, ast.Name) and t.id in ("_PART", "PERSONA_FUERA", "NO_PERSONA", "NOMBRES_COMO_VERBO", "COSA_SIEMPRE") for t in getattr(n, "targets", [])):
        exec(compile(ast.Module([n], []), str(GV), "exec"), _ns)
_names = ("_PART", "PERSONA_FUERA", "NO_PERSONA")
for n in ast.parse(_src).body:
    if isinstance(n, ast.FunctionDef) and n.name == "persona_fuera":
        exec(compile(ast.Module([n], []), str(GV), "exec"), _ns)
pf = lambda t: [x["nombre"] for x in (_ns["persona_fuera"](m.group(1), m.group(2)) for m in _ns["PERSONA_FUERA"].finditer(t)) if x]
ok(pf("Esperar la firma de Agustín Torres (Escuela Fácil) antes del viernes") == ["Agustín Torres"], "«Nombre Apellido (Organización)» es una persona de fuera")
ok(pf("Migrar el Sistema Nuevo Contable antes del cierre") == [], "unas palabras con mayúscula no son una persona")
ok(pf("Hablar con Ana María de la Fuente (Acme)") == ["Ana María de la Fuente"], "con partículas en el apellido")
ok(pf("Revisar con Luis Romero (luis@acme.test)") == [] and pf("Cierre de Finanzas (2026-10-03)") == [], "ni una cuenta ni una fecha entre paréntesis hacen una organización")
ok(pf("Enviar la Propuesta Técnica (Escuela Fácil)") == [] and pf("Revisar el Contrato Marco (Acme)") == [], "un documento con su cliente entre paréntesis no es una persona")
ok(pf("Esperar de Agustín Torres (Escuela Fácil)") == ["Agustín Torres"], "un verbo delante no se pega al nombre")
ok(pf("Pilar de la Fuente (Acme)") == ["Pilar de la Fuente"] and pf("Javier de Dios (Acme)") == ["Javier de Dios"], "un nombre que acaba como un verbo sigue siendo un nombre")
ok(pf("Carlos Mesa (Banco Azul)") == ["Carlos Mesa"], "un apellido que también es una cosa no descarta a la persona")
ok(pf("Esperar Visto Bueno de Juan Pérez (Acme)") == ["Juan Pérez"] and pf("Revisar el Diagrama de Flujo (Acme)") == [] and pf("La Secretaría de Hacienda (SAT)") == [], "las cosas de delante se quitan, y una cosa sola no es nadie")
ok(pf("Configurar Salesforce Service Cloud (Acme)") == [] and pf("Migrar a Google Workspace (Banco Azul)") == [] and pf("Esperar a Ana Centeno (Acme)") == ["Ana Centeno"], "una herramienta con su cliente entre paréntesis no es una persona (1.22.5)")
print("Nombres que se quedan al reutilizar la base (revisión 1.22.4, hallazgo 5)")
tmp = pathlib.Path(tempfile.mkdtemp()); raiz = tmp / "raiz"; shutil.copytree(AQUI / "raiz", raiz)
pp = raiz / "ventas" / "cuentas" / "proyecto.md"
t = pp.read_text(encoding="utf-8").replace("Dueño: Ana Prueba\n", "Dueño: Ana Prueba\nColabora: Carla Prueba (carla@ejemplo.test)\n")
t = t.replace("## Siguientes pasos\n", "## Siguientes pasos\n- Esperar la firma de Agustín Torres (Escuela Fácil) para cerrar el piloto.\n")
pp.write_text(t, encoding="utf-8")
_o1, _o2, reuso = dos_corridas(raiz, tmp)
ok(reuso, "la segunda corrida reutiliza de verdad proyectos y «fuera»")
a1 = json.loads((tmp / "o1" / "areas" / "ventas.json").read_text(encoding="utf-8")); a2 = json.loads((tmp / "o2" / "areas" / "ventas.json").read_text(encoding="utf-8"))
ok(a1.get("colaboran_ver") == ["Carla Prueba"] and a2.get("colaboran_ver") == ["Carla Prueba"], f"quien colabora conserva su nombre al reutilizar ({a1.get('colaboran_ver')} → {a2.get('colaboran_ver')})")
pc = json.loads((tmp / "o1" / "proyectos" / "ventas--cuentas.json").read_text(encoding="utf-8"))
ok({"nombre": "Agustín Torres", "organizacion": "Escuela Fácil"} in (pc.get("personas_fuera") or []), "el paso deja a la persona de fuera con su organización")
ok("carla@" not in json.dumps(pc), "y el proyecto no lleva el correo")
shutil.rmtree(tmp)
print("\nTodo bien." if not fallos else f"\n{fallos} fallos.")
sys.exit(1 if fallos else 0)
