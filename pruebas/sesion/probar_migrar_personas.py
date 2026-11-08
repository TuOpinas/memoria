#!/usr/bin/env python3
"""Prueba la migración de las personas a «Quién es quién» (1.26, migrar_estructura.py --personas) y lo que la apertura
dice de ella, sobre la raíz inventada ya pasada a la 1.22 (comun.raiz_migrada).

Uso: python3 pruebas/sesion/probar_migrar_personas.py

Lo que manda: nadie gana ni pierde escritura. Se comprueba con las mismas funciones que usa el script (escritura(),
sobre context_core) antes y después, y además con la apertura: las áreas y proyectos donde escribe cada cuenta salen
iguales. Una cuenta sin nombre conocido no deja migrar guia.md hasta que se dé con --nombres.
"""
import importlib.util, json, pathlib, re, shutil, subprocess, sys

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent)); from comun import raiz_migrada, MIG  # noqa: E402
PL = AQUI.parent.parent / "plugins" / "memoria"
ABRIR = PL / "skills/sesion/abrir.py"
VERSION = json.loads((PL / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
NOMBRES = "carla@ejemplo.test=Carla Prueba,eva@ejemplo.test=Eva Prueba"
fallos = 0

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


print("El plan, con el registro a la vista")
R, _ = raiz_migrada()
antes = foto(R)
c, s = migrar(R, "--cuenta", "ana@ejemplo.test", "--personas", "--plan", "--plugin", "1.26.0")
sp = s.get("personas", {})
ok(sp.get("registro", "").startswith("- Ana Prueba · ana@ejemplo.test\n") and "- Dani Prueba · dani@ejemplo.test" in sp.get("registro", ""),
   "el registro sale de la tabla, de «Contexto común» y de los «Colabora: Nombre (correo)» de los proyectos")
ok(sp.get("faltan_nombres") == ["carla@ejemplo.test", "eva@ejemplo.test"], "las cuentas sin nombre conocido van en faltan_nombres")
ok(sp.get("no_se_migra") and foto(R) == antes, "con nombres que faltan no se escribe nada, ni con --plan")
c, s = migrar(R, "--cuenta", "ana@ejemplo.test", "--personas", "--plugin", "1.26.0")
ok(foto(R) == antes, "sin --nombres tampoco, aunque no lleve --plan")
c, s = migrar(R, "--cuenta", "ana@ejemplo.test", "--plugin", "1.26.0", "--nombres", NOMBRES)
ok("personas" not in s and foto(R) == antes, "sin --personas la migración es solo la de la 1.22: las personas tienen su propia pregunta")

print("La apertura del responsable de contexto lo pregunta")
o = abrir(R, "ventas/cuentas", "--cuenta", "ana@ejemplo.test")
ok("Personas: ANTERIOR en guia.md" in o and "¿La paso a «Quién es quién»" in o, "ofrece «Migrar ahora» con la pregunta de las personas")
ok("Ana López (1.20.1)" in o and "Ana Prueba (1." not in o.split("=== RESPUESTA")[1], "dice quién cerró con un plugin anterior a la 1.26 en 60 días, sin contar a quien migra")
o_b = abrir(R, "ventas/cuentas", "--cuenta", "beto@ejemplo.test")
ok("Personas: ANTERIOR" not in o_b, "a otro responsable no se le pregunta: guia.md es del responsable de contexto")
c, s = migrar(R, "--cuenta", "beto@ejemplo.test", "--personas", "--plugin", "1.26.0", "--nombres", NOMBRES)
ok(s.get("personas", {}).get("no_se_migra") and foto(R) == antes, "y si corre el script, no toca nada")
escr_antes = escribe(R)
quien_antes = {c_: cuentas_de(abrir(R, "--cuenta", c_)) for c_ in ("ana@ejemplo.test", "beto@ejemplo.test", "carla@ejemplo.test", "eva@ejemplo.test", "dani@ejemplo.test")}

print("La migración")
c, s = migrar(R, "--cuenta", "ana@ejemplo.test", "--personas", "--plugin", "1.26.0", "--nombres", NOMBRES)
g = (R / "guia.md").read_text(encoding="utf-8")
ok(c == 0 and not s["fallidos"] and s["personas"].get("gana") == [], f"migra sin fallos ({s.get('fallidos')})")
ok("## Quién es quién\n- Ana Prueba · ana@ejemplo.test\n- Carla Prueba · carla@ejemplo.test\n" in g, "guia.md lleva «Quién es quién» con las cuentas")
ok("| Responsable | Colabora |" in g and "| Ana Prueba | Carla Prueba |" in g and "@" not in g.split("## Áreas")[1].split("## Quién es quién")[0],
   "la columna «Cuenta» pasa a «Colabora» con nombres, y la tabla y «Quién responde por qué» se quedan sin correos")
ok("Contratos con clientes y proveedores (escribe también Ana Prueba" in g and "| Beto Prueba | Eva Prueba |" in g, "el matiz del responsable pasa a «Qué es»")
ok("| Ana Prueba y Beto Prueba | Restringida |" in g, "«Quién la lee» pierde «Restringida:» cuando «Acceso» lo dice")
ok(g.index("## Quién es quién") < g.index("## Versión mínima del plugin") and "\n1.26.0. Con un plugin anterior" in g, "y al final, «Versión mínima del plugin» con la 1.26.0")
ok("Colabora: Dani Prueba\n" in (R / "operacion/soporte/proyecto.md").read_text(encoding="utf-8"), "«Colabora: Nombre (correo)» de un proyecto queda en el nombre")
ok("(migracion)\nTema: las personas pasan a «Quién es quién»" in (R / "operacion/soporte/sesiones.md").read_text(encoding="utf-8"), "y el proyecto deja su entrada «(migracion)»")
va = (R / "ventas/area.md").read_text(encoding="utf-8")
ok("Responsable y colaboradores: en la tabla de áreas de guia.md." in va and not re.search(r"^Responsable:", va, re.M), "area.md deja de repetir el responsable")
ok(M.diferencias(escr_antes, escribe(R)) == ([], []), "quién escribe en cada área, en el contexto común y en cada proyecto sale igual")
quien_despues = {c_: cuentas_de(abrir(R, "--cuenta", c_)) for c_ in quien_antes}
# con un plugin por debajo de la mínima la apertura dice «nada: SOLO LECTURA … ; con un plugin al día, en …»: se compara eso
def norm(x):
    x = x or ""
    if "con un plugin al día, en " in x:
        return x.split("con un plugin al día, en ", 1)[1]
    return "" if x.startswith(("nada: SOLO LECTURA", "ninguna área")) else x
ok(all(norm(quien_despues[c_]) == norm(quien_antes[c_]) for c_ in quien_antes), f"y la apertura da a cada cuenta las mismas áreas ({quien_despues})")
o = abrir(R, "ventas/cuentas", "--cuenta", "ana@ejemplo.test")
ok("Personas: ANTERIOR" not in o, "después no se vuelve a preguntar")
debe = tuple(int(x) for x in VERSION.split(".")) >= (1, 26, 0)
ok(("ESCRITURA: abierta" in o) == debe, f"y la puerta abre o no según la versión de este plugin ({VERSION})")
despues = foto(R)
c, s = migrar(R, "--cuenta", "ana@ejemplo.test", "--personas", "--plugin", "1.26.0")
ok(foto(R) == despues, "repetirla no cambia nada")

print("Un responsable migra sus area.md cuando guia.md ya tiene el registro")
pa = R / "personas" / "area.md"
pa.write_text(pa.read_text(encoding="utf-8").replace("Responsable y colaboradores: en la tabla de áreas de guia.md.", "Responsable: Beto Prueba"), encoding="utf-8")
o_b = abrir(R, "--cuenta", "beto@ejemplo.test")
ok("Personas: ANTERIOR en personas" in o_b, "su apertura lo ofrece para su área")
c, s = migrar(R, "--cuenta", "beto@ejemplo.test", "--personas", "--plugin", "1.26.0")
ok("Responsable y colaboradores" in pa.read_text(encoding="utf-8") and list(s["archivos"]) == ["personas/area.md"], f"y solo toca su area.md ({list(s['archivos'])})")
ok(M.personas_en_area(pa.read_text(encoding="utf-8")) == [], "personas_en_area ya no ve nada")

print("Lo que sigue al nombre en «Quién participa» de un area.md se queda")
ta = "# A\n\n## Quién participa\nResponsable: Ana Prueba. Consumen esta área ventas y soporte.\nColabora: Carla Prueba\n\n## Otra\nx\n"
nt = M.area_con_personas(ta)
ok("Consumen esta área ventas y soporte." in nt and "Ana Prueba" not in nt and "Carla" not in nt and nt.endswith("## Otra\nx\n"), f"sale el nombre y queda la frase ({nt!r})")

print("Si cambiaría quién escribe, no se migra")
R2, _ = raiz_migrada()
g2 = R2 / "guia.md"
g2.write_text(g2.read_text(encoding="utf-8").replace("| ana@ejemplo.test | Todo el equipo | Abierta |\n| `futura/`", "| ana@ejemplo.test, eva@ejemplo.test | Todo el equipo | Abierta |\n| `futura/`", 1), encoding="utf-8")
antes2 = foto(R2)
c, s = migrar(R2, "--cuenta", "ana@ejemplo.test", "--personas", "--plugin", "1.26.0", "--nombres", NOMBRES)
ok(any("operacion" in x for x in s["personas"].get("no_se_migra", [])) and (R2 / "guia.md").read_bytes() == antes2[R2 / "guia.md"],
   f"una fila con dos correos antes de «colabora:» (nadie responde) pasaría a tener responsable: se dice y guia.md no se toca ({s['personas'].get('no_se_migra')})")

print("La misma función en abrir.py y en migrar_estructura.py")
src = ABRIR.read_text(encoding="utf-8")
ok("def personas_en_area(texto_area):" in src and "LINEA_PERSONA = re.compile(r\"^\\s*[-*]?\\s*\\**\\s*(?:colabora[n]?|responsable|due[ñn][oa])\\s*\\**\\s*:\", re.I)" in src
   and M.LINEA_PERSONA.pattern == r"^\s*[-*]?\s*\**\s*(?:colabora[n]?|responsable|due[ñn][oa])\s*\**\s*:", "las dos leen las mismas líneas de «Quién participa»")

shutil.rmtree(R.parent, ignore_errors=True); shutil.rmtree(R2.parent, ignore_errors=True)
print("Todo bien." if not fallos else f"{fallos} fallo(s).")
sys.exit(1 if fallos else 0)
