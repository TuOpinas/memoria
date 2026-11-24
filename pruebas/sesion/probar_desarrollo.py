#!/usr/bin/env python3
"""Prueba el aviso del kit de desarrollo en abrir.py (1.27): solo en un proyecto con la sección «## Desarrollo», una línea
por motivo con las piezas que le faltan, y una raíz sin ella no ve nada nuevo (tecnologia/metodologia-desarrollo#2026-11-18-4
y #2026-11-19-2).

Uso: python3 pruebas/sesion/probar_desarrollo.py
Copia la raíz inventada de pruebas/tablero/raiz a una carpeta temporal, le pone la sección a ventas/cuentas y comprueba lo
que avisa la apertura.
"""
import pathlib, re, shutil, subprocess, sys, tempfile

AQUI = pathlib.Path(__file__).resolve().parent
ABRIR = AQUI.parent.parent / "plugins" / "memoria" / "skills" / "sesion" / "abrir.py"
fallos = 0


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


def del_kit(o):
    return [x for x in avisos(o) if x.startswith("Desarrollo")]


print("Una raíz sin proyectos de desarrollo no ve nada nuevo")
r = raiz()
c, o = abrir(r)
ok(c == 0 and not del_kit(o) and "Desarrollo:" not in o, "ventas/cuentas sin la sección: ningún aviso del kit")
c, o = abrir(r, "operacion/soporte")
ok(c == 0 and "Desarrollo:" not in o, "otro proyecto, tampoco")

print("Recién creado: todo por crear")
r = raiz()
kit(r)
c, o = abrir(r)
a = del_kit(o)
ok(c == 0, "abre sin error")
ok(len(a) == 1 and "Configuración de plataforma, Configuración de repositorios, Diseño, Plan están por crear" in a[0],
   "las piezas por crear van en una sola línea, sin contar el seguimiento")
ok("skills/desarrollo/plantillas/" in a[0], "y dice dónde están las plantillas")

print("Con el kit montado, una sola configuración para las dos claves")
r = raiz()
E = "ventas/cuentas/entregables/"
kit(r, **{"Configuración de plataforma": "operacion/plataforma.md", "Configuración de repositorios": "operacion/plataforma.md",
          "Diseño": E + "diseno.md", "Plan": E + "plan.md", "Seguimiento": E + "seguimiento.md"})
for ruta in ("operacion/plataforma.md", E + "diseno.md", E + "plan.md", E + "seguimiento.md"):
    (r / ruta).write_text("---\nestado: borrador\nactualizado: 2026-11-01\n---\n\n# X\n", encoding="utf-8")
c, o = abrir(r)
ok(c == 0 and not del_kit(o), "nada falta: ningún aviso del kit")
ok("GitHub" not in "\n".join(avisos(o)), "la apertura no habla de GitHub")

print("Una línea que falta, un archivo que no existe y lo que no se puede mirar")
r = raiz()
kit(r, **{"Diseño": "ventas/cuentas/entregables/no-esta.md", "Plan": "personas/nomina/plan.md", "Acepta": None,
          "Seguimiento": "ventas/cuentas/entregables/seguimiento.md"})
c, o = abrir(r)
a = del_kit(o)
ok(any("Diseño (ventas/cuentas/entregables/no-esta.md), Seguimiento (ventas/cuentas/entregables/seguimiento.md) apuntan a un archivo que no existe" in x for x in a),
   "los archivos que no existen, juntos en una línea")
ok(any("Acepta no tiene su línea en la sección" in x for x in a), "una línea que falta")
ok(any("no se pudo comprobar" in x and "personas/nomina/plan.md" in x for x in a), "un área restringida ajena no se abre ni se da por que falta")
ok(not any("Plan" in x and "no existe" in x for x in a), "y no sale como que no existe")

print("Lo que la sección dice y no se entiende")
r = raiz()
kit(r, **{"Repositorios": "https://github.com/acme/app", "Construye": "Ana Prueba (ana en el correo)",
          "Diseño": "ventas/cuentas/taller/no-esta.md"})
c, o = abrir(r)
a = del_kit(o)
ok(not any("Repositorios" in x and "vacía" in x for x in a), "un enlace de GitHub en Repositorios se entiende")
ok(any("en la sección" in x and "ana en el correo" in x for x in a), "una persona mal escrita se dice")
ok(any("Diseño (ventas/cuentas/taller/no-esta.md) apunta a un archivo que no existe" in x for x in a),
   "el taller del propio proyecto se comprueba")
ok(not any("Acepta" in x for x in a), "las personas bien escritas no salen")
r = raiz()
kit(r, **{"Repositorios": "acme/app, acme/web"})
a = del_kit(abrir(r)[1])
ok(not any("Repositorios" in x and "vacía" in x for x in a) and any("acme/app, acme/web" in x for x in a),
   "un valor que no se entiende se dice una vez, sin darlo por vacío")
r = raiz()
kit(r, **{"Acepta": "por crear", "Configuración de plataforma": "x/y.md", "Configuración de repositorios": "x/y.md",
          "Diseño": "x/y.md", "Plan": "x/y.md"})
(r / "x").mkdir(); (r / "x/y.md").write_text("---\nestado: borrador\nactualizado: 2026-11-01\n---\n", encoding="utf-8")
c, o = abrir(r)
a = del_kit(o)
ok(any("Acepta está por crear." in x for x in a) and not any("plantillas" in x for x in a), "a un rol por crear no se le mandan plantillas")

print("La sección después de «Quién participa» no cambia quién escribe")
c, o = abrir(r, cuenta="beto@ejemplo.test")
ok(re.search(r"=== CUENTA EN EL PROYECTO\nbeto@ejemplo.test: (?!colabora en este proyecto)", o) is not None,
   "Beto, que solo está en «Audita», no pasa a colaborar en el proyecto")

print("Los repositorios se conectan al abrir (1.29.1, P23)")


def paso_repos(o):
    m = re.search(r"=== RESPUESTA[^\n]*\n(.*?)(?=\n=== |\Z)", o, re.S)
    return [l for l in (m.group(1) if m else "").split("\n") if "Conecta con escritura" in l]


r = raiz()
c, o = abrir(r)
ok(c == 0 and not paso_repos(o), "sin la sección, la RESPUESTA no pide conectar nada")
kit(r, **{"Repositorios": "https://github.com/acme/app.git · acme/web"})
c, o = abrir(r)
p_ = paso_repos(o)
ok(c == 0 and len(p_) == 1 and "(acme/app · acme/web)" in p_[0], "un paso, con cada repositorio como organización/repositorio, también el pegado como enlace")
ok(p_ and "en remoto" in p_[0] and "una línea" in p_[0] and "motivo" in p_[0], "dice que el desarrollo es remoto y cómo decir el que no se pudo conectar")
r = raiz()
kit(r, **{"Repositorios": "por crear"})
ok(not paso_repos(abrir(r)[1]), "con «Repositorios: por crear», nada que conectar")
c, o = abrir(r, "ventas/cuentas", "beto@ejemplo.test")
ok(c == 0, "abre igual con otra cuenta")

print()
print("Todo bien." if not fallos else f"{fallos} fallo(s).")
sys.exit(1 if fallos else 0)
