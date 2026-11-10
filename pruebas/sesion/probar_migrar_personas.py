#!/usr/bin/env python3
"""Prueba la migración de las personas a «Quién es quién» (1.26, migrar_estructura.py --personas) y lo que la apertura
dice de ella, sobre la raíz inventada ya pasada a la 1.22 (comun.raiz_migrada).

Uso: python3 pruebas/sesion/probar_migrar_personas.py

Lo que manda: nadie pierde escritura ni lectura. Se comprueba con las mismas funciones que usa el script (escritura(),
sobre context_core) antes y después, y además con la apertura: las áreas y proyectos donde escribe cada cuenta salen
iguales. Una cuenta sin nombre conocido no deja migrar guia.md hasta que se dé con --nombres. Los scripts corren desde
una copia con ESTE_PLUGIN en la versión que pide la estructura (lo que pone release.sh al publicar): con el de la rama, la
puerta dejaría la raíz migrada en solo lectura. La entrada vieja de la raíz de prueba se fecha relativa a hoy, para que la
ventana de 60 días no caduque la prueba.
"""
import datetime, importlib.util, json, pathlib, re, shutil, subprocess, sys, tempfile

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent)); from comun import raiz_migrada  # noqa: E402
PL = AQUI.parent.parent / "plugins" / "memoria"
sys.path.insert(0, str(AQUI.parent.parent / "packages" / "context-core"))
from context_core.minimum import STRUCTURE_MINIMUM  # noqa: E402
NOMBRES = "carla@ejemplo.test=Carla Prueba,eva@ejemplo.test=Eva Prueba"
fallos = 0

COPIA = pathlib.Path(tempfile.mkdtemp())
for n in ("abrir.py", "migrar_estructura.py"):
    t = (PL / "skills/sesion" / n).read_text(encoding="utf-8")
    (COPIA / n).write_text(re.sub(r'^ESTE_PLUGIN = "[0-9.]+"', f'ESTE_PLUGIN = "{STRUCTURE_MINIMUM}"', t, count=1, flags=re.M), encoding="utf-8")
ABRIR, MIG = COPIA / "abrir.py", COPIA / "migrar_estructura.py"
spec = importlib.util.spec_from_file_location("migrar_estructura", MIG)
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)


def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1


def migrar(r, *a):
    p = subprocess.run([sys.executable, str(MIG), str(r), *a], capture_output=True, text=True)
    return p.returncode, json.loads(p.stdout) if p.stdout.strip() else {"stderr": p.stderr}


def abrir(r, *a):
    p = subprocess.run([sys.executable, str(ABRIR), str(r), *a], capture_output=True, text=True)
    return p.stdout + p.stderr


def foto(r):
    return {p: p.read_bytes() for p in r.rglob("*") if p.is_file()}


def proyectos(r):
    return {d.parent.relative_to(r).as_posix(): d.read_text(encoding="utf-8") for d in r.rglob("proyecto.md")}


def escribe(r):
    return M.escritura((r / "guia.md").read_text(encoding="utf-8"), proyectos(r))


def cuentas_de(o):
    m = re.search(r"^(\S+@\S+): escribe en (.*)$", o, re.M)
    return m.group(2) if m else None


def raiz():
    r, _ = raiz_migrada()
    s = r / "ventas/cuentas/sesiones.md"
    reciente = (datetime.date.today() - datetime.timedelta(days=10)).isoformat()
    s.write_text(s.read_text(encoding="utf-8").replace("## 2026-10-01", "## " + reciente, 1), encoding="utf-8")
    return r


print("El plan, con el registro a la vista")
R = raiz()
antes = foto(R)
c, s = migrar(R, "--cuenta", "ana@ejemplo.test", "--personas", "--plan", "--plugin", "1.26.0")
sp = s.get("personas", {})
ok(sp.get("registro", "").startswith("- Ana Prueba · ana@ejemplo.test\n") and "- Dani Prueba · dani@ejemplo.test" in sp.get("registro", ""),
   "el registro sale de la tabla, de «Contexto común» y de los «Colabora: Nombre (correo)» de los proyectos")
ok(sp.get("faltan_nombres") == ["carla@ejemplo.test", "eva@ejemplo.test"], "las cuentas sin nombre conocido van en faltan_nombres")
ok(sp.get("atrasados") == ["Ana López (1.20.1)"], f"dice quién cerró en 60 días con un plugin anterior, sin la entrada (migracion) de quien migra ({sp.get('atrasados')})")
ok(sp.get("no_se_migra") and foto(R) == antes, "con nombres que faltan no se escribe nada, ni con --plan")
c, s = migrar(R, "--cuenta", "ana@ejemplo.test", "--personas", "--plugin", "1.26.0")
ok(foto(R) == antes, "sin --nombres tampoco, aunque no lleve --plan")
c, s = migrar(R, "--cuenta", "ana@ejemplo.test", "--plugin", "1.26.0", "--nombres", NOMBRES)
ok("personas" not in s and foto(R) == antes, "sin --personas la migración es solo la de la 1.22: las personas tienen su propia pregunta")

print("La apertura del responsable de contexto lo pregunta")
o = abrir(R, "ventas/cuentas", "--cuenta", "ana@ejemplo.test")
ok("Personas: ANTERIOR en guia.md" in o and "¿La paso a «Quién es quién»" in o, "ofrece «Migrar ahora» con la pregunta de las personas")
ok("Ana López" not in o.split("=== RESPUESTA")[1], "y no recorre las bitácoras: quién va atrasado lo dice la migración")
o_b = abrir(R, "ventas/cuentas", "--cuenta", "beto@ejemplo.test")
ok("Personas: ANTERIOR" not in o_b, "a otro responsable no se le pregunta: guia.md es del responsable de contexto")
c, s = migrar(R, "--cuenta", "beto@ejemplo.test", "--personas", "--plugin", "1.26.0", "--nombres", NOMBRES)
ok(s.get("personas", {}).get("no_se_migra") and foto(R) == antes, "y si corre el script, no toca nada")
escr_antes = escribe(R)
quien_antes = {c_: cuentas_de(abrir(R, "--cuenta", c_)) for c_ in ("ana@ejemplo.test", "beto@ejemplo.test", "carla@ejemplo.test", "eva@ejemplo.test", "dani@ejemplo.test")}
lee_antes = (R / "guia.md").read_text(encoding="utf-8").split("## Áreas")[1].split("## ")[0]

print("La migración")
c, s = migrar(R, "--cuenta", "ana@ejemplo.test", "--personas", "--plugin", "1.26.0", "--nombres", NOMBRES)
g = (R / "guia.md").read_text(encoding="utf-8")
ok(c == 0 and not s["fallidos"] and s["personas"].get("gana") == [], f"migra sin fallos ({s.get('fallidos')})")
ok("## Quién es quién\n- Ana Prueba · ana@ejemplo.test\n- Carla Prueba · carla@ejemplo.test\n" in g, "guia.md lleva «Quién es quién» con las cuentas")
ok("| Responsable | Colabora |" in g and "| Ana Prueba | Carla Prueba |" in g and "@" not in g.split("## Áreas")[1].split("## Quién es quién")[0],
   "la columna «Cuenta» pasa a «Colabora» con nombres, y la tabla y «Quién responde por qué» se quedan sin correos")
ok("Contratos con clientes y proveedores (escribe también Ana Prueba" in g and "| Beto Prueba | Eva Prueba |" in g, "el matiz del responsable pasa a «Qué es»")
ok("| Restringida: dirección | Restringida |" in g and "| Restringida: Ana Prueba y Beto Prueba | Restringida |" in g,
   "«Quién la lee» no se toca: un plugin 1.19–1.21 lee ahí lo restringido")
ok(g.index("## Quién es quién") < g.index("## Versión mínima del plugin") and f"\n{STRUCTURE_MINIMUM}. Con un plugin anterior" in g, "y al final, «Versión mínima del plugin»")
ok("Colabora: Dani Prueba\n" in (R / "operacion/soporte/proyecto.md").read_text(encoding="utf-8"), "«Colabora: Nombre (correo)» de un proyecto queda en el nombre")
ok("(migracion)\nTema: las personas pasan a «Quién es quién»" in (R / "operacion/soporte/sesiones.md").read_text(encoding="utf-8"), "y el proyecto deja su entrada «(migracion)»")
va = (R / "ventas/area.md").read_text(encoding="utf-8")
ok("Responsable y colaboradores: en la tabla de áreas de guia.md." in va and not re.search(r"^Responsable:", va, re.M), "area.md deja de repetir el responsable")
ok(M.diferencias(escr_antes, escribe(R)) == ([], []), "quién escribe en cada área, en el contexto común y en cada proyecto sale igual")
quien_despues = {c_: cuentas_de(abrir(R, "--cuenta", c_)) for c_ in quien_antes}
ok(quien_despues == quien_antes, f"y la apertura da a cada cuenta las mismas áreas ({quien_despues})")
o = abrir(R, "ventas/cuentas", "--cuenta", "ana@ejemplo.test")
ok("Personas: ANTERIOR" not in o and "ESCRITURA: abierta" in o, "después no se vuelve a preguntar, y la puerta abre a un plugin al día")
despues = foto(R)
c, s = migrar(R, "--cuenta", "ana@ejemplo.test", "--personas", "--plugin", "1.26.0")
ok(foto(R) == despues, "repetirla no cambia nada")

print("Un responsable migra sus area.md cuando guia.md ya tiene el registro")
pa = R / "personas" / "area.md"
pa.write_text(pa.read_text(encoding="utf-8").replace("Responsable y colaboradores: en la tabla de áreas de guia.md.", "Responsable: Beto Prueba"), encoding="utf-8")
o_b = abrir(R, "--cuenta", "beto@ejemplo.test")
ok("Personas: ANTERIOR en personas" in o_b, "su apertura lo ofrece para su área")
c, s = migrar(R, "--cuenta", "beto@ejemplo.test", "--personas", "--plugin", "1.26.0")
ok("Responsable y colaboradores" in pa.read_text(encoding="utf-8") and list(s.get("archivos", {})) == ["personas/area.md"], f"y solo toca su area.md ({s.get('archivos', s)})")
ok(M.personas_en_area(pa.read_text(encoding="utf-8")) == [], "personas_en_area ya no ve nada")

print("Una raíz con «Quién es quién» que no pide la versión mínima")
g_ = R / "guia.md"
g_.write_text(re.sub(r"\n## Versión mínima del plugin\n.*", "\n", g_.read_text(encoding="utf-8"), flags=re.S), encoding="utf-8")
o = abrir(R, "--cuenta", "ana@ejemplo.test")
ok("(falta la versión mínima del plugin)" in o and "¿Añado a guia.md la versión mínima del plugin?" in o, "la apertura del responsable de contexto lo ofrece")
c, s = migrar(R, "--cuenta", "ana@ejemplo.test", "--personas", "--plugin", "1.26.0")
ok("## Versión mínima del plugin" in g_.read_text(encoding="utf-8") and list(s.get("archivos", {})) == ["guia.md"], "y la migración solo la añade")

print("Lo que sigue al nombre en «Quién participa» de un area.md no se pierde")
reg = M.registro_personas(g_.read_text(encoding="utf-8"))
ta = "# A\n\n## Quién participa\nResponsable: Ana Prueba. Consumen esta área ventas y soporte.\nColabora: Carla Prueba\n\n## Otra\nx\n"
nt, av = M.area_con_personas(ta, reg)
ok("Consumen esta área ventas y soporte." in nt and "Ana Prueba" not in nt and "Carla" not in nt and nt.endswith("## Otra\nx\n"), f"sale el nombre y queda la frase ({nt!r})")
for linea in ("Responsable: Ana Prueba (decide precios; Carla propone)", "Responsable: Ana Prueba, que decide los precios",
              "Colabora: Carla Prueba en las propuestas grandes", "Colabora: Luis Mejía (Proveedor S.A.), que revisa los contratos"):
    nt, av = M.area_con_personas(f"# A\n\n## Quién participa\n{linea}\n", reg)
    ok(linea in nt and av, f"«{linea}» se queda entera, con aviso")

print("Si alguien perdería escritura, no se migra")
R2 = raiz()
g2 = R2 / "guia.md"
g2.write_text(g2.read_text(encoding="utf-8").replace("| ana@ejemplo.test | Todo el equipo | Abierta |\n| `futura/`", "| ana@ejemplo.test, eva@ejemplo.test | Todo el equipo | Abierta |\n| `futura/`", 1), encoding="utf-8")
antes2 = foto(R2)
c, s = migrar(R2, "--cuenta", "ana@ejemplo.test", "--personas", "--plugin", "1.26.0", "--nombres", NOMBRES)
ok(any("operacion" in x and "tabla de áreas" in x for x in s["personas"].get("no_se_migra", [])) and (R2 / "guia.md").read_bytes() == antes2[R2 / "guia.md"],
   f"una fila con dos correos antes de «colabora:» pasaría a tener responsable: se dice dónde y guia.md no se toca ({s['personas'].get('no_se_migra')})")

print("Lo que la migración pregunta en lugar de negarse")
R3 = raiz()
pr = R3 / "operacion/soporte/proyecto.md"
pr.write_text(pr.read_text(encoding="utf-8").replace("Colabora: Dani Prueba (dani@ejemplo.test)", "Colabora: Dani P. (dani@ejemplo.test), zoe@ejemplo.test"), encoding="utf-8")
c, s = migrar(R3, "--cuenta", "ana@ejemplo.test", "--personas", "--plan", "--plugin", "1.26.0", "--nombres", NOMBRES)
ok("zoe@ejemplo.test" in s["personas"]["faltan_nombres"], "un correo suelto en un «Colabora:» se pregunta")
c, s = migrar(R3, "--cuenta", "ana@ejemplo.test", "--personas", "--plugin", "1.26.0", "--nombres", NOMBRES + ",zoe@ejemplo.test=?,dani@ejemplo.test=Dani Prueba")
g3 = (R3 / "guia.md").read_text(encoding="utf-8")
ok(not s["personas"].get("no_se_migra") and "- ? · zoe@ejemplo.test" in g3 and "- Dani Prueba · dani@ejemplo.test · también: Dani P." in g3,
   f"«correo=?» la deja «? · correo», y la otra grafía queda como «también:» ({s['personas'].get('no_se_migra')})")
ok("Colabora: Dani Prueba, zoe@ejemplo.test" in pr.read_text(encoding="utf-8"), "y el proyecto queda con el nombre del registro")

print("Las plantillas de guia.md de la 1.22 a la 1.24")
plantilla = ("## Áreas\n\n| Área | Qué es | Responsable | Cuenta | Quién la lee | Acceso |\n|---|---|---|---|---|---|\n"
             "| `ventas/` | V | Ana Prueba | ana@ejemplo.test | Todo el equipo | Abierta |\n\n"
             "La cuenta es con la que esa persona trabaja con la IA. Es lo que permite comprobar\nque quien pide publicar algo es su responsable. Quien escribe en un área va en\n"
             "la misma celda, después de la cuenta del responsable: `responsable@… · colabora: ana@…`.\n\n## Quién responde por qué\nContexto común: Ana Prueba\n")
ng = M.guia_con_personas(plantilla, [["Ana Prueba", ["ana@ejemplo.test"], "", [], False]])
ok(M.PARRAFO_AREAS in ng and "colabora: ana@" not in ng and "## Quién responde por qué" in ng, "el párrafo partido en varias líneas que explicaba «Cuenta» se reemplaza entero")

print("La puerta, en la migración")
R4 = raiz()
(R4 / "guia.md").write_text((R4 / "guia.md").read_text(encoding="utf-8") + "\n## Versión mínima del plugin\n9.0.0.\n", encoding="utf-8")
antes4 = foto(R4)
c, s = migrar(R4, "--cuenta", "ana@ejemplo.test", "--personas", "--plugin", "1.26.0", "--nombres", NOMBRES)
ok(c == 6 and s.get("solo_lectura") and foto(R4) == antes4, "por debajo de la versión mínima de la raíz no migra nada y sale con 6")

# la cuenta del servidor («Servidor:», 1.26.1) no es una persona: no va al registro
R5, _ = raiz_migrada()
g5 = R5 / "guia.md"; g5.write_text(g5.read_text(encoding="utf-8").replace("Administra la carpeta: Ana Prueba", "Administra la carpeta: Ana Prueba\nServidor: org-prueba@proyecto.iam.gserviceaccount.com"), encoding="utf-8")
c, s5 = migrar(R5, "--cuenta", "ana@ejemplo.test", "--personas")
ok("org-prueba@proyecto.iam.gserviceaccount.com" not in json.dumps(s5), "la cuenta del servidor no entra en «Quién es quién» ni se pregunta su nombre")
shutil.rmtree(R5.parent, ignore_errors=True)

for d in (R, R2, R3, R4):
    shutil.rmtree(d.parent, ignore_errors=True)
shutil.rmtree(COPIA, ignore_errors=True)
print("Todo bien." if not fallos else f"{fallos} fallo(s).")
sys.exit(1 if fallos else 0)
