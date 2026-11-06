#!/usr/bin/env python3
"""«Quién es quién» (1.25): el registro de personas, y una raíz en la forma de la 1.25 da
a cada cuenta exactamente lo mismo que la misma raíz en la forma de la 1.22 (la celda Cuenta con correos).

Uso: python3 pruebas/sesion/probar_registro.py
"""
import json, pathlib, re, subprocess, sys, tempfile, unicodedata
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1])); from comun import raiz_migrada, raiz_125
PL = pathlib.Path(__file__).resolve().parents[2] / "plugins" / "memoria"
ABRIR, PERM, VERIF = PL / "skills/sesion/abrir.py", PL / "skills/sesion/permisos.py", PL / "verificar.sh"
fallos = 0
def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1

print("El registro de personas")
# abrir.py lo toma de context_core (paso 0 de la versión alojada): estos casos prueban el paquete, que es lo que corre, tal
# como va metido en el script
t = (PL / "skills/sesion/abrir.py").read_text(encoding="utf-8")
exec(t[t.index("# --- quién escribe"):t.index("# --- fin de quién escribe ---")], {"re": re})
ns = vars(sys.modules["context_core.compat"])
R_ = ns["registro_personas"]; F = ns["fila_cuentas"]; C = ns["colaboran_en"]
G = """## Quién es quién
- Juanjo Jiménez-Alfaro · jjalfaro@me.com · de: TuOpinas
- **Gabby Meade** · gabriela.meade@smilepill.mx · también: Gabriela Meade
- Marco Herrero · marco.herrero@smilepill.mx · en Drive: mherrero@gmail.com
- Fabiola Davó · sin cuenta · registra: Marco Herrero
- ? · eva@smilepill.mx
- Luis Mejía · lmejia@smilepill.mx · baja 2026-10-15
- Sara Doble · cuentas: sara@a.mx, sara@b.mx
- Pepa Sola · sin cuenta
## Otra
- Nadie · nadie@x.mx
"""
r = R_(G)
ok(r["hay"] and len(r["personas"]) == 8 and not r["avisos"], "ocho líneas, sin avisos, y lo que sigue a otra sección no cuenta")
ok(r["cuenta"]["eva@smilepill.mx"]["nombre"] == "?" and ns["nombre_de"]("EVA@smilepill.mx", r) == "", "«?» es una cuenta sin nombre: escribe, pero no tiene nombre")
ok(ns["persona"]("gabriela  meade", r)["nombre"] == "Gabby Meade", "un alias resuelve a la misma persona, sin mayúsculas ni espacios dobles")
nfd = unicodedata.normalize("NFD", "Fabiola Davó")
ok(ns["persona"](nfd, r) is not None and ns["persona"]("Fabiola Davo", r) is None, "la tilde escrita en NFD (Mac) es la misma; sin tilde, no")
cab = ["Área", "Qué es", "Responsable", "Colabora", "Quién la lee", "Acceso"]
ok(F(cab, ["a", "", "Gabby Meade", "Marco Herrero, Luis Mejía", "", "Abierta"], r) == ({"gabriela.meade@smilepill.mx"}, {"marco.herrero@smilepill.mx"}, None), "responsable y colabora por nombre; quien está de baja no escribe")
de, co, av = F(cab, ["a", "", "Fabiola Davó (interina)", "", "", "Abierta"], r)
ok(de == {"marco.herrero@smilepill.mx"} and av is None, "un responsable «sin cuenta» con «registra:» escribe por la cuenta de quien registra")
ok(F(cab, ["a", "", "Pepa Sola", "", "", ""], r)[0] == set() and "no tiene cuenta" in F(cab, ["a", "", "Pepa Sola", "", "", ""], r)[2], "un responsable «sin cuenta» sin «registra:» no deja escribir a nadie, y avisa")
ok(F(cab, ["a", "", "Nadie Nunca", "Otro", "", ""], r)[0] == set() and "Otro" in F(cab, ["a", "", "Nadie Nunca", "Otro", "", ""], r)[2], "un nombre que no está no es nadie (falla cerrado), y se dice cuál")
ok(F(cab, ["a", "", "Sara Doble", "", "", ""], r)[0] == {"sara@a.mx", "sara@b.mx"}, "una persona con dos cuentas responde con las dos")
ok(F(cab, ["a", "", "Gabby Meade", "", "", ""], R_(""))[2] and F(cab, ["a", "", "Gabby Meade", "", "", ""], R_(""))[0] == set(), "la tabla nueva sin «Quién es quién»: nadie escribe, y avisa")
ok(F(["Área", "Qué es", "Responsable", "Cuenta", "Quién la lee", "Acceso"], ["a", "", "X", "x@a.mx · colabora: y@a.mx", "", ""], r)[:2] == ({"x@a.mx"}, {"y@a.mx"}), "con la columna Cuenta, como siempre (aunque haya registro)")
ok(F(["a", "b", "c", "d", "e"], ["a", "", "X", "x@a.mx", ""], r)[0] == {"x@a.mx"}, "sin encabezado reconocible, la cuarta columna como Cuenta")
ok(C("Responsable: Gabby Meade (diseño)\nColabora: Marco Herrero, Nuevo Tipo (nuevo@x.mx)\nLo lee: Sara Doble", r) == {"marco.herrero@smilepill.mx", "nuevo@x.mx"}, "«Colabora:» por nombre y el alta provisional «Nombre (correo)»; «Lo lee:» no da escritura")
ok(C("Colabora: Marco Herrero (marco.herrero@smilepill.mx)") == {"marco.herrero@smilepill.mx"} and C("Colabora: Marco Herrero") == set(), "sin registro, «Colabora:» solo cuenta con el correo, como hasta la 1.24")
for av_, g_ in [("dos veces", "## Quién es quién\n- Ana · a@x.mx\n- Ana · b@x.mx\n"), ("dos líneas", "## Quién es quién\n- Ana · a@x.mx\n- Beto · a@x.mx\n"),
                ("no lleva", "## Quién es quién\n- Ana\n"), ("no se entiende", "## Quién es quién\n- Ana · a@x.mx · jefa\n")]:
    ok(any(av_ in x for x in R_(g_)["avisos"]), f"avisa: {av_}")

print("\nLa misma raíz en la forma de la 1.22 y en la de la 1.25")
R2, _ = raiz_migrada(); R5, _ = raiz_125()
def cuenta_de(raiz, c, *extra):
    o = subprocess.run([sys.executable, str(ABRIR), str(raiz), *extra, "--cuenta", c], capture_output=True, text=True).stdout
    m = re.search(r"^=== CUENTA\n(.*?)(?=^===|\Z)", o, re.M | re.S)
    return (m.group(1) if m else ""), o
for c in ["ana@ejemplo.test", "beto@ejemplo.test", "carla@ejemplo.test", "eva@ejemplo.test", "dani@ejemplo.test"]:
    a2, _ = cuenta_de(R2, c); a5, o5 = cuenta_de(R5, c)
    l2 = re.search(r"^" + re.escape(c) + r": .*$", a2, re.M); l5 = re.search(r"^" + re.escape(c) + r": .*$", a5, re.M)
    ok(l2 and l5 and l2.group(0) == l5.group(0), f"{c}: escribe en lo mismo ({l5.group(0)[len(c)+2:] if l5 else '—'})")
    if c != "dani@ejemplo.test":
        ok(re.search(r"^NOMBRE \S", a5, re.M) is not None, f"{c}: la apertura dice su nombre, para «Sesión de:»")
_, o5 = cuenta_de(R5, "dani@ejemplo.test", "operacion/soporte")
_, o2 = cuenta_de(R2, "dani@ejemplo.test", "operacion/soporte")
ok(("operacion/soporte (colabora en el proyecto)" in o5) == ("operacion/soporte (colabora en el proyecto)" in o2) and "operacion/soporte (colabora en el proyecto)" in o5, "quien colabora solo en un proyecto, por su nombre en «Colabora:»")
_, ox = cuenta_de(R5, "nadie@ejemplo.test")
ok("no está en «Quién es quién»" in ox, "una cuenta que no está en el registro: la apertura lo dice (y dónde se corrige)")
g = (R5 / "guia.md").read_text(encoding="utf-8")
(R5 / "guia.md").write_text(g.replace("| Eva Prueba |", "| eva@ejemplo.test |").replace("- Eva Prueba · eva@ejemplo.test", "- ? · eva@ejemplo.test\n- Zoe Nueva · zoe@ejemplo.test · sin confirmar"), encoding="utf-8")
_, oa = cuenta_de(R5, "ana@ejemplo.test")
ok("sin nombre (eva@ejemplo.test)" in oa and "«sin confirmar»: Zoe Nueva" in oa, "al responsable de contexto se le dicen las cuentas sin nombre y las líneas «sin confirmar»")
_, oe = cuenta_de(R5, "eva@ejemplo.test")
ok("legal (colabora)" in oe and "sin nombre" in oe, "«? · cuenta» sigue escribiendo, y a esa persona se le pide su nombre")
(R5 / "guia.md").write_text(g, encoding="utf-8")

print("\nPermisos de Drive, igual en las dos formas")
def drive():
    u = lambda e, r: {"email": e, "role": r}
    B = [u("ana@ejemplo.test", "organizer"), u("beto@ejemplo.test", "reader"), u("carla@ejemplo.test", "reader"), u("eva@ejemplo.test", "reader"), u("dani@ejemplo.test", "reader")]
    return {"raiz": {"permisos": B}, "areas": {"ventas": {"permisos": B[:1] + [u("beto@ejemplo.test", "reader"), u("carla@ejemplo.test", "fileOrganizer")], "limitada": False},
            "personas": {"permisos": [u("ana@ejemplo.test", "organizer"), u("beto@ejemplo.test", "fileOrganizer")], "limitada": True},
            "operacion": {"permisos": B, "limitada": False}, "legal": {"permisos": [u("ana@ejemplo.test", "organizer"), u("beto@ejemplo.test", "reader")], "limitada": False},
            "archivo": {"permisos": B, "limitada": False}}, "proyectos": {}, "restringidos": {}}
f = pathlib.Path(tempfile.mkdtemp()) / "drive.json"; f.write_text(json.dumps(drive()))
q2 = subprocess.run([sys.executable, str(PERM), str(R2), "--drive", str(f)], capture_output=True, text=True).stdout
q5 = subprocess.run([sys.executable, str(PERM), str(R5), "--drive", str(f)], capture_output=True, text=True).stdout
ok(q2.strip() and q2 == q5, "permisos.py dice exactamente lo mismo" + ("" if q2 == q5 else ":\n" + "\n".join(f"      1.22 {a}\n      1.25 {b}" for a, b in zip(q2.split("\n"), q5.split("\n")) if a != b)))
pl5 = subprocess.run([sys.executable, str(PERM), str(R5), "--plan"], capture_output=True, text=True).stdout
pm = R5 / "operacion/soporte/proyecto.md"; tp = pm.read_text(encoding="utf-8")
pm.write_text(tp.replace("Colabora: Dani Prueba", "Colabora: Dani Prueba, Fede Nuevo (fede@ejemplo.test)"), encoding="utf-8")
pl6 = subprocess.run([sys.executable, str(PERM), str(R5), "--plan"], capture_output=True, text=True).stdout
ok("ALTA Fede Nuevo · fede@ejemplo.test" in pl6 and "ALTA" not in pl5, "el alta provisional de un proyecto la dice el plan de permisos, para pasarla al registro")
o_ = subprocess.run([sys.executable, str(ABRIR), str(R5), "--cuenta", "fede@ejemplo.test", "operacion/soporte"], capture_output=True, text=True).stdout
ok("operacion/soporte (colabora en el proyecto)" in o_, "y mientras tanto esa persona ya escribe en el proyecto")
v6 = subprocess.run(["bash", str(VERIF), str(R5)], capture_output=True, text=True).stdout
ok("Fede Nuevo (fede@ejemplo.test) colabora en" in v6 and "nombre que no está en «Quién es quién»" not in v6, "verificar lo deja como nota, no como error")
pm.write_text(tp.replace("Colabora: Dani Prueba", "Colabora: Dani Prueba, Fabi"), encoding="utf-8")
v7 = subprocess.run(["bash", str(VERIF), str(R5)], capture_output=True, text=True).stdout
ok("nombre que no está en «Quién es quién»" in v7 and "«Fabi»" in v7, "un nombre que no está en el registro, en un proyecto abierto: verificar lo señala")
pm.write_text(tp, encoding="utf-8")

print("\nverificar")
v2 = subprocess.run(["bash", str(VERIF), str(R2)], capture_output=True, text=True).stdout
v5 = subprocess.run(["bash", str(VERIF), str(R5)], capture_output=True, text=True).stdout
h = lambda s: sorted(l for l in s.split("\n") if l.startswith("  "))
ok(h(v2) == h(v5), "da los mismos hallazgos en las dos formas" + ("" if h(v2) == h(v5) else ": " + str(sorted(set(h(v2)) ^ set(h(v5))))))
g5 = (R5 / "guia.md").read_text(encoding="utf-8")
(R5 / "guia.md").write_text(g5.replace("| Carla Prueba |", "| Carla Pruebas |").replace("- Beto Prueba · beto@ejemplo.test", "- Beto Prueba · beto@ejemplo.test\n- Beto Prueba · otra@ejemplo.test\n- ? · x@ejemplo.test\n- Pepa Sola · sin cuenta"), encoding="utf-8")
v8 = subprocess.run(["bash", str(VERIF), str(R5)], capture_output=True, text=True).stdout
ok("fila de la tabla de áreas que no se deja leer" in v8 and "Carla Pruebas" in v8, "un nombre de la tabla que no está en el registro")
ok("dos veces" in v8 and "cuenta sin nombre en «Quién es quién»" in v8 and "Pepa Sola no tiene cuenta" in v8, "nombres repetidos y cuentas sin nombre son hallazgos; «sin cuenta», una nota")
(R5 / "guia.md").write_text(g5.split("## Quién es quién")[0], encoding="utf-8")
v9 = subprocess.run(["bash", str(VERIF), str(R5)], capture_output=True, text=True).stdout
ok("guia.md sin «Quién es quién»" in v9, "la tabla con Colabora y sin registro")
(R5 / "guia.md").write_text(g5, encoding="utf-8")

print("\nEl tablero, igual en las dos formas")
GV = PL / "skills/tablero/generar_vista.py"
def tablero(raiz, c):
    out = pathlib.Path(tempfile.mkdtemp()) / "t"
    subprocess.run([sys.executable, str(GV), str(raiz), str(out), "--cuenta", c, "--version", "prueba"], check=True, stdout=subprocess.DEVNULL)
    j = lambda *a: json.loads((out.joinpath(*a[:-1]) / (a[-1] + ".json")).read_text(encoding="utf-8"))
    return out, j
for c in ["ana@ejemplo.test", "beto@ejemplo.test", "carla@ejemplo.test", "eva@ejemplo.test", "dani@ejemplo.test"]:
    o2_, j2 = tablero(R2, c); o5_, j5 = tablero(R5, c)
    clave = lambda j: ([(x.stem, j("areas", x.stem).get("escribe"), j("areas", x.stem).get("motivo")) for x in sorted((o2_ / "areas").glob("*.json"))],
                       [(x.stem, j("proyectos", x.stem).get("escribe"), j("proyectos", x.stem).get("motivo")) for x in sorted((o2_ / "proyectos").glob("*.json"))],
                       j("meta", "estado").get("soy_contexto"))
    ok(clave(j2) == clave(j5), f"{c}: escribe y ve lo mismo en cada área y cada proyecto")
    t5 = j5("meta", "estado").get("tablero_de"); t2 = j2("meta", "estado").get("tablero_de")
    ok(t5 == {"ana": "Ana Prueba", "beto": "Beto Prueba", "carla": "Carla Prueba", "eva": "Eva Prueba", "dani": "Dani Prueba"}[c.split("@")[0]], f"{c}: el tablero sabe de quién es por el registro ({t5}; con la celda Cuenta, «{t2}»)")
v_ = j5("areas", "ventas")
ok(v_.get("colaboran_ver") == ["Carla Prueba"] and not any("@" in x for x in v_.get("colaboran") or []) and not v_.get("colaboran_nombres") and not v_.get("colaboran_sin_nombre"),
   "quien colabora sale por su nombre, y los datos del área no llevan correos de nadie")
ok(j5("meta", "estado").get("registro") is True and j2("meta", "estado").get("registro") is False, "la página sabe si la raíz tiene «Quién es quién»")
ok(not [f for f in j5("meta", "estado").get("fuera", []) if f.get("personas")], "sin nada que arreglar en el registro, Mantenimiento no dice nada")
(R5 / "guia.md").write_text(g.replace("- Eva Prueba · eva@ejemplo.test", "- ? · eva@ejemplo.test").replace("| Eva Prueba |", "| eva@ejemplo.test |"), encoding="utf-8")
_, jx = tablero(R5, "ana@ejemplo.test")
ok(any(f.get("personas") and "eva@ejemplo.test" in f.get("guia", "") for f in jx("meta", "estado").get("fuera", [])), "una cuenta «?» sale en Mantenimiento, para ponerle nombre")
(R5 / "guia.md").write_text(g, encoding="utf-8")

print("\nLa puesta al día programada, igual en las dos formas")
if True:
    src = (PL / "skills/tablero/barrido.py").read_text(encoding="utf-8")
    nsb = {"__name__": "x"}
    exec(compile(src.split("\nif __name__")[0], "barrido.py", "exec"), nsb)
    for c in ["ana@ejemplo.test", "beto@ejemplo.test", "carla@ejemplo.test", "eva@ejemplo.test"]:
        ok(nsb["areas_de_la_cuenta"](R2, c) == nsb["areas_de_la_cuenta"](R5, c) and nsb["areas_de_la_cuenta"](R5, c), f"barrido.py: {c} tiene las mismas áreas ({sorted(nsb['areas_de_la_cuenta'](R5, c))})")
    ok(nsb["colabora_en"](R5 / "operacion" / "soporte", "dani@ejemplo.test") and nsb["colabora_en"](R2 / "operacion" / "soporte", "dani@ejemplo.test"), "barrido.py: quien colabora en un proyecto, por su nombre")
AC = PL / "skills/tablero/aplicar_cambios.py"
_src = AC.read_text(encoding="utf-8"); _src = _src[:_src.index("MIAS, COLABORA = mis_areas()")]
def mis(raiz, c):
    _a = sys.argv; sys.argv = ["x", str(raiz), "/dev/null", "--cuenta", c]
    try:
        n_ = {"__name__": "x"}; exec(compile(_src, "aplicar_cambios.py", "exec"), n_); return n_["mis_areas"]()
    finally:
        sys.argv = _a
for c in ["ana@ejemplo.test", "beto@ejemplo.test", "carla@ejemplo.test", "eva@ejemplo.test"]:
    ok(mis(R2, c) == mis(R5, c) and any(mis(R5, c)), f"aplicar_cambios.py: {c} es responsable y colabora en lo mismo ({mis(R5, c)})")

_cs = (PL / "skills/sesion/cerrar.py").read_text(encoding="utf-8")
_nc = {"__name__": "x"}; exec(compile(_cs.split("\nif __name__")[0], "cerrar.py", "exec"), _nc)
for a_ in ["ventas", "legal", "personas", "operacion"]:
    ok(_nc["celda_cuenta"](R2, a_) == _nc["celda_cuenta"](R5, a_) and _nc["celda_cuenta"](R5, a_)[0], f"cerrar.py: quién escribe el Estatus de {a_} es lo mismo ({_nc['celda_cuenta'](R5, a_)})")
MIG = PL / "skills/sesion/migrar_estructura.py"
m5 = subprocess.run([sys.executable, str(MIG), str(R5), "--cuenta", "ana@ejemplo.test", "--plan"], capture_output=True, text=True)
ok(m5.returncode == 0 and json.loads(m5.stdout).get("pendiente") in (None, [], False, 0) or "nada" in m5.stdout.lower() or '"cambios": []' in m5.stdout, "migrar_estructura.py no ve nada que migrar en una raíz de la 1.25: " + m5.stdout[:160].replace("\n", " "))

print("\nLo que encontró la revisión de la 1.25: nada da escritura a quien no debe")
g0 = (R5 / "guia.md").read_text(encoding="utf-8"); pm = R5 / "operacion/soporte/proyecto.md"; tp0 = pm.read_text(encoding="utf-8")
def con(guia=None, proy=None):
    (R5 / "guia.md").write_text(guia if guia is not None else g0, encoding="utf-8"); pm.write_text(proy if proy is not None else tp0, encoding="utf-8")
def linea(c, *extra):
    a_, o_ = cuenta_de(R5, c, *extra)
    m_ = re.search(r"^" + re.escape(c) + r": .*$", a_, re.M)
    return (m_.group(0) if m_ else ""), o_
con(g0.replace("- Dani Prueba · dani@ejemplo.test", "- Dani Prueba · dani@ejemplo.test · baja 2026-10-15"), tp0.replace("Colabora: Dani Prueba", "Colabora: Dani Prueba (dani@ejemplo.test)"))
ok("ninguna área" in linea("dani@ejemplo.test", "operacion/soporte")[0], "quien está de baja no escribe aunque su correo siga junto a su nombre en el proyecto")
con(g0.replace("- Dani Prueba · dani@ejemplo.test", "- Dani Prueba · dani@ejemplo.test · dado de baja el 2026-10-15"))
ok("ninguna área" in linea("dani@ejemplo.test", "operacion/soporte")[0], "la baja escrita de otra forma («dado de baja el…») también vale")
con(None, tp0.replace("Colabora: Dani Prueba", "Colabora: Carla Prueba (intrusa@otro.test)"))
ok("ninguna área" in linea("intrusa@otro.test", "operacion/soporte")[0], "un correo junto al nombre de alguien del registro no da escritura a ese correo")
v_ = subprocess.run(["bash", str(VERIF), str(R5)], capture_output=True, text=True).stdout
ok("intrusa" not in v_, "y verificar no lo toma por un alta provisional")
con(g0.replace("| Carla Prueba |", "| Carla Prueba, zzz@otra.test |"))
ok("ventas" not in linea("zzz@otra.test")[0], "un correo suelto en Colabora que no está en el registro no da escritura")
con(g0.replace("- Carla Prueba · carla@ejemplo.test", "- Carla Ortega y Gasset · carla@ejemplo.test").replace("| Carla Prueba |", "| Carla Ortega y Gasset |"))
ok("ventas (colabora)" in linea("carla@ejemplo.test")[0], "un nombre con « y » se queda entero si así está en el registro")
con(g0.replace("- Eva Prueba · eva@ejemplo.test", "- Eva Prueba · eva@ejemplo.test\n- Ana Prueba · otra@ejemplo.test"))
ok("ventas" not in linea("ana@ejemplo.test")[0] and "ventas" not in linea("otra@ejemplo.test")[0], "un nombre en dos líneas no es de nadie (falla cerrado)")
q_ = subprocess.run([sys.executable, str(PERM), str(R5), "--drive", str(f)], capture_output=True, text=True).stdout
ok("otra@ejemplo.test figura" not in q_, "y la revisión de permisos no propone nada para la segunda línea")
con(g0.replace("| Eva Prueba | Ana Prueba y Beto Prueba | Restringida |", "| Eva Prueba | Ana Prueba y Beto Prueba |  |"))
_, o_ = cuenta_de(R5, "carla@ejemplo.test"); ok("legal/ · restringida" in o_ or "legal · restringida" in o_ or re.search(r"legal/?\s*·\s*restringid", o_), "con «Colabora», un Acceso vacío deja el área restringida, no abierta")
con(g0.replace("Contexto común: Ana Prueba", "Contexto común: Ana Prueba, que también administra la carpeta"))
ok("responsable de contexto" in linea("ana@ejemplo.test")[0], "«Contexto común» con una coletilla tras la coma sigue reconociendo a quien responde")
con(g0.replace("Contexto común: Ana Prueba", "Contexto común: Ana Pruebas"))
ok("nadie responde por guia.md" in cuenta_de(R5, "ana@ejemplo.test")[1] and "«Ana Pruebas», en «Contexto común»" in subprocess.run(["bash", str(VERIF), str(R5)], capture_output=True, text=True).stdout, "un «Contexto común» que no está en el registro: lo dicen la apertura y verificar")
for t_ in ("## Quién es Quién", "### Quién es quién", "## Quien es quien:"):
    con(g0.replace("## Quién es quién", t_))
    ok("ventas (colabora)" in linea("carla@ejemplo.test")[0], f"el registro se reconoce con «{t_}»")
con(g0.replace("| Colabora |", "| Colaboradores |"))
ok("ventas (colabora)" in linea("carla@ejemplo.test")[0], "y la columna «Colaboradores»")
con(g0.replace("| Ana Prueba | Carla Prueba |", "| Ana Prueba, interina | Carla Prueba |"))
l_, o_ = linea("ana@ejemplo.test"); ok("ventas (responsable)" in l_ and "va en «Qué es»" in o_, "un matiz tras la coma en Responsable: sigue siendo responsable, y se dice dónde va el matiz")
con(None, tp0.replace("Colabora: Dani Prueba", "Colabora: Dani Prueba, Fede Nuevo (fede@ejemplo.test)"))
_, o_ = cuenta_de(R5, "fede@ejemplo.test", "operacion/soporte")
ok("alta provisional" in o_ and "no escribes en ninguna área" not in o_, "quien entra por alta provisional oye que escribe en el proyecto, no que no escribe")
con()
ok(not re.search(r"^NOMBRE", cuenta_de(R5, "ana@ejemplo.test", "--minima")[0], re.M), "la apertura mínima no imprime NOMBRE (no cierra sesión)")
n_ = ns
ok(n_["fila_cuentas"](["Área", "Qué es", "Quién la lee", "Acceso", "Responsable", "Colabora"], ["a", "b", "c"], n_["registro_personas"](g0))[0] == set(), "una fila corta no rompe nada")
o3, j3 = tablero(R5, "ana@ejemplo.test")
_base = pathlib.Path(tempfile.mkdtemp()) / "t2"
con(g0.replace("- Eva Prueba · eva@ejemplo.test", "- Eva Prueba · intrusa@otra.test"))
subprocess.run([sys.executable, str(GV), str(R5), str(_base), "--cuenta", "ana@ejemplo.test", "--version", "prueba", "--previos", str(o3)], check=True, stdout=subprocess.DEVNULL)
_e = json.loads((_base / "meta" / "estado.json").read_text(encoding="utf-8"))
_e = _e.get("data", _e)
ok(_e.get("registro_cambios") == ["Eva Prueba"] and any("Eva Prueba" in x.get("guia", "") and x.get("personas") for x in _e.get("fuera", [])), "el tablero de quien responde por el contexto dice qué línea de «Quién es quién» cambió")
ok("intrusa" not in json.dumps(_e), "sin poner la cuenta en claro en los datos de la página")
con(g0.replace("- Dani Prueba · dani@ejemplo.test", "- Dani Prueba · dani@ejemplo.test\n- Fabiola Davó · sin cuenta · registra: Dani Prueba").replace("| `operacion/` | Área de soporte y entregas | Ana Prueba |", "| `operacion/` | Área de soporte y entregas | Fabiola Davó |"))
_, jd = tablero(R5, "dani@ejemplo.test")
ok(jd("meta", "estado").get("tablero_de") == "Dani Prueba" and jd("areas", "operacion").get("escribe") is True, "el tablero de quien registra por otra persona es suyo, con su nombre del registro, y escribe en esa área")
con()

print("\n" + ("Todo bien." if not fallos else f"{fallos} fallo(s)."))
sys.exit(1 if fallos else 0)
