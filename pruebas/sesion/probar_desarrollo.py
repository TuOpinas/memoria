#!/usr/bin/env python3
"""Prueba los avisos del kit de desarrollo en abrir.py (1.27): solo en un proyecto con la sección «## Desarrollo», y una
raíz sin ella no ve nada nuevo (tecnologia/metodologia-desarrollo#2026-11-18-4 y -8).

Uso: python3 pruebas/sesion/probar_desarrollo.py
Copia la raíz inventada de pruebas/tablero/raiz a una carpeta temporal, le pone la sección a ventas/cuentas y comprueba lo
que avisa la apertura: piezas que faltan, secciones o columnas que no están, un plan desfasado, el último seguimiento y la
auditoría mensual.
"""
import datetime, pathlib, re, shutil, subprocess, sys, tempfile

AQUI = pathlib.Path(__file__).resolve().parent
ABRIR = AQUI.parent.parent / "plugins" / "memoria" / "skills" / "sesion" / "abrir.py"
PLANTILLAS = AQUI.parent.parent / "plugins" / "memoria" / "skills" / "desarrollo" / "plantillas"
fallos = 0
# el día de la organización (America/Mexico_City en la raíz de prueba), no el del reloj, que va en UTC
from zoneinfo import ZoneInfo
HOY = datetime.datetime.now(ZoneInfo("America/Mexico_City")).date()
hace = lambda n: (HOY - datetime.timedelta(days=n)).isoformat()


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t)
    fallos += 0 if c else 1


def raiz():
    r = pathlib.Path(tempfile.mkdtemp()) / "raiz"
    shutil.copytree(AQUI.parent / "tablero" / "raiz", r)
    return r


def abrir(r, proyecto="ventas/cuentas", cuenta="ana@ejemplo.test"):
    p = subprocess.run([sys.executable, str(ABRIR), str(r), proyecto, "--cuenta", cuenta], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def avisos(o):
    m = re.search(r"=== AVISOS\n(.*?)(?=\n=== |\Z)", o, re.S)
    return [l[2:] for l in (m.group(1) if m else "").split("\n") if l.startswith("- ")]


def kit(r, **lineas):
    base = {"Repositorios": "acme/app", "Configuración de plataforma": "por crear", "Configuración de repositorios": "por crear",
            "Diseño": "por crear", "Plan": "por crear", "Seguimiento": "por crear", "Paso a Prod": "release de GitHub",
            "Acepta": "Ana Prueba (ana@ejemplo.test)", "Audita": "Beto Prueba (beto@ejemplo.test, @beto)",
            "Construye": "Ana Prueba (ana@ejemplo.test, @ana)", "Administra": "Beto Prueba (beto@ejemplo.test, @beto)"}
    base.update(lineas)
    p = r / "ventas/cuentas/proyecto.md"
    p.write_text(p.read_text(encoding="utf-8").rstrip() + "\n\n## Desarrollo\n"
                 + "".join(f"{k}: {v}\n" for k, v in base.items() if v is not None), encoding="utf-8")


def doc(r, ruta, plantilla, actualizado, cambia=None):
    t = (PLANTILLAS / plantilla).read_text(encoding="utf-8").replace("actualizado: AAAA-MM-DD", f"actualizado: {actualizado}")
    for a, b in (cambia or {}).items():
        t = t.replace(a, b)
    (r / ruta).parent.mkdir(parents=True, exist_ok=True)
    (r / ruta).write_text(t, encoding="utf-8")


print("Una raíz sin proyectos de desarrollo no ve nada nuevo")
r = raiz()
c, o = abrir(r)
ok(c == 0 and not any(a.startswith("Desarrollo") for a in avisos(o)) and "kit de desarrollo" not in o, "ventas/cuentas sin la sección: ningún aviso ni línea del kit")
c, o = abrir(r, "operacion/soporte")
ok(c == 0 and "Desarrollo:" not in o, "otro proyecto, tampoco")

print("Recién creado: todo por crear")
r = raiz()
kit(r)
c, o = abrir(r)
a = [x for x in avisos(o) if x.startswith("Desarrollo")]
ok(c == 0, "abre sin error")
ok(any("Configuración de plataforma, Configuración de repositorios, Diseño, Plan están por crear" in x for x in a),
   "las piezas por crear van en una línea, sin contar el seguimiento")
ok(any("todavía no hay ningún seguimiento" in x for x in a), "dice que no hay seguimiento")
ok(not any("auditoría" in x for x in a), "sin configuraciones, la auditoría no se avisa aparte")

print("Con el kit montado")
r = raiz()
E = "ventas/cuentas/entregables/"
kit(r, **{"Configuración de plataforma": "operacion/plataforma.md", "Configuración de repositorios": E + "repositorios.md",
          "Diseño": E + "diseno.md", "Plan": E + "plan.md", "Seguimiento": E + "seguimiento.md"})
doc(r, "operacion/plataforma.md", "configuracion-plataforma.md", hace(40),
    {"| PL1 | GitHub es de la empresa, pide verificación en dos pasos y su plan permite reglas en repositorios privados | | En GitHub, la organización → Settings → Authentication security y Billing | |":
     f"| PL1 | GitHub de la empresa | Acme | Settings | cumple · {hace(40)} |"})
doc(r, E + "repositorios.md", "configuracion-repositorios.md", hace(40),
    {"[organización/repositorio]": "acme/app", "| R1 | Nada llega a `main` sin pull request, se une con squash y nadie se salta la regla | En GitHub, el repositorio → Settings → Rules: la regla de `main` existe y su lista de excepciones está vacía; en General, solo squash | |":
     f"| R1 | Nada a main | Rules | cumple · {hace(35)} |"})
doc(r, E + "diseno.md", "diseno.md", hace(5), {"| Componente | Qué hace | Dónde vive |": "| Componente | Qué hace | Ruta |"})
doc(r, E + "plan.md", "plan.md", hace(10))
(r / E / "seguimiento.md").write_text(f"---\nestado: vigente\nactualizado: {hace(3)}\n---\n\n# Seguimiento\n\n## {hace(3)} · pedido por Ana Prueba\nTodo en orden.\n\n## {hace(20)} · pedido por Ana Prueba\n", encoding="utf-8")
dp = r / "ventas/cuentas/decisiones.md"
t = dp.read_text(encoding="utf-8")
i = t.index("\n## ")
dp.write_text(t[:i] + f"\n## {hace(2)} · La vista entra en la fase 2\nDecidió: Ana Prueba\nPor qué: prueba.\nAfecta a: entregables/plan.md (la fase 2)\n" + t[i:], encoding="utf-8")
c, o = abrir(r)
a = [x for x in avisos(o) if x.startswith("Desarrollo")]
ok(c == 0, "abre sin error")
ok(not any("por crear" in x or "no existe" in x for x in a), "nada falta")
ok(any("el diseño" in x and "columna Dónde vive en Componentes" in x for x in a), "una columna que el diseño no tiene")
ok(any("el plan" in x and "puede estar desfasado" in x and "La vista entra en la fase 2" in x for x in a), "el plan es anterior a una decisión que lo nombra")
ok(not any("el diseño" in x and "desfasado" in x for x in a), "el diseño, que nadie nombra, no")
ok(any(f"el último seguimiento es del {hace(3)} (hace 3 días)" in x for x in a), "la fecha del seguimiento es la de su entrada más nueva")
ok(any("toca la auditoría mensual" in x and hace(35) in x and "Beto Prueba" in x for x in a), "auditoría pendiente: la fecha más reciente de las dos, y quién la hace")
ok("kit de desarrollo, fuera de entregables/ del proyecto: configuración de plataforma operacion/plataforma.md" in o,
   "el inventario cuenta lo del kit que vive fuera del proyecto")
c, o = abrir(r, cuenta="beto@ejemplo.test")
ok(any("Te toca a ti" in x for x in avisos(o)), "a quien audita, como foco")

print("Auditoría al día")
p = r / E / "repositorios.md"
p.write_text(p.read_text(encoding="utf-8").replace(f"cumple · {hace(35)}", f"cumple · {hace(4)}"), encoding="utf-8")
c, o = abrir(r)
ok(not any("auditoría" in x for x in avisos(o)), "una comprobación de hace 4 días basta")

print("Rutas que no están o que no se leen")
r = raiz()
kit(r, **{"Diseño": "ventas/cuentas/entregables/no-esta.md", "Plan": "personas/nomina/plan.md", "Acepta": None,
          "Construye": "Ana Prueba (ana en el correo)"})
(r / "ventas/cuentas/proyecto.md").write_text((r / "ventas/cuentas/proyecto.md").read_text(encoding="utf-8") + "Revisa: alguien\n", encoding="utf-8")
c, o = abrir(r)
a = [x for x in avisos(o) if x.startswith("Desarrollo")]
ok(any("Diseño (ventas/cuentas/entregables/no-esta.md) apunta a un archivo que no existe" in x for x in a), "un archivo que no existe")
ok(any("Acepta no tiene su línea" in x for x in a), "una línea que falta")
ok(any("no se pudo comprobar" in x and "personas/nomina/plan.md" in x for x in a), "un área restringida ajena no se abre ni se da por que falta")
ok(any("líneas que no reconozco" in x and "Revisa: alguien" in x for x in a), "una línea que no reconoce")
ok(any("ana en el correo" in x for x in a), "una persona mal escrita")

print("La sección después de «Quién participa» no cambia quién escribe")
c, o = abrir(r, cuenta="beto@ejemplo.test")
ok(re.search(r"=== CUENTA EN EL PROYECTO\nbeto@ejemplo.test: (?!colabora en este proyecto)", o) is not None,
   "Beto, que solo está en «Audita», no pasa a colaborar en el proyecto")

print()
print("Todo bien." if not fallos else f"{fallos} fallo(s).")
sys.exit(1 if fallos else 0)
