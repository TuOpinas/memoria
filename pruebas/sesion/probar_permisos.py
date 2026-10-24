#!/usr/bin/env python3
"""Prueba permisos.py contra la raíz inventada de pruebas/tablero/raiz y unos permisos de Drive inventados.

Uso: python3 pruebas/sesion/probar_permisos.py
"""
import json, pathlib, subprocess, sys, tempfile
import sys as _s, pathlib as _p; _s.path.insert(0, str(_p.Path(__file__).resolve().parents[1])); from comun import guia_122, raiz_migrada
AQUI = pathlib.Path(__file__).resolve().parent
P = AQUI.parent.parent / "plugins" / "memoria" / "skills" / "sesion" / "permisos.py"
R = AQUI.parent / "tablero" / "raiz"
fallos = 0
def ok(c, t):
    global fallos
    print(("  bien  " if c else "  FALLA ") + t); fallos += 0 if c else 1
def corre(drive):
    f = pathlib.Path(tempfile.mkdtemp()) / "drive.json"; f.write_text(json.dumps(drive))
    r = subprocess.run([sys.executable, str(P), str(R), "--drive", str(f)], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr
u = lambda e, r: {"email": e, "role": r}
BASE = [u("ana@ejemplo.test", "organizer"), u("beto@ejemplo.test", "reader"), u("carla@ejemplo.test", "reader"), u("eva@ejemplo.test", "reader"), u("dani@ejemplo.test", "reader")]
def bien():
    return {"raiz": {"permisos": BASE},
            "areas": {"ventas": {"permisos": BASE[:1] + [u("beto@ejemplo.test", "reader"), u("carla@ejemplo.test", "fileOrganizer")], "limitada": False},
                      "personas": {"permisos": [u("ana@ejemplo.test", "organizer"), u("beto@ejemplo.test", "fileOrganizer")], "limitada": True},
                      "operacion": {"permisos": BASE, "limitada": False}, "futura": None, "legal": None,
                      "archivo": {"permisos": BASE, "limitada": False}},
            "proyectos": {"ventas/margenes": {"permisos": [], "limitada": True}, "ventas/precios": {"permisos": [], "limitada": True},
                          "operacion/soporte": {"permisos": BASE[:4] + [u("dani@ejemplo.test", "fileOrganizer")], "limitada": False}},
            "restringidos": {"ventas/cuentas": {"permisos": [], "limitada": True}}}

print("Permisos de Drive contra lo declarado")
c, o = subprocess.run([sys.executable, str(P), str(R), "--plan"], capture_output=True, text=True).returncode, ""
r = subprocess.run([sys.executable, str(P), str(R), "--plan"], capture_output=True, text=True).stdout
ok("área personas/ (declarada restringida)" in r and "restringido ventas/cuentas/restringido/" in r and "proyecto operacion/soporte/ (con «Colabora:»)" in r, "el plan nombra áreas, proyectos con colaboradores o restringidos y carpetas restringido/")
c, o = corre(bien())
ok(c == 0 and "Todo cuadra" in o and "Para cambiar" not in o and "No se pudo mirar personas/bonos/" in o, "con los permisos que declara la carpeta, todo cuadra, y dice qué no pudo mirar")
d = bien(); d["raiz"]["permisos"] = [u("ana@ejemplo.test", "organizer"), u("beto@ejemplo.test", "fileOrganizer"), u("carla@ejemplo.test", "reader"), u("eva@ejemplo.test", "reader"), u("dani@ejemplo.test", "reader")]
c, o = corre(d)
ok("beto@ejemplo.test tiene «Gestor de contenido» en toda la carpeta" in o and "Cámbiale el rol a «Lector» en la raíz y dale «Gestor de contenido» solo en la carpeta de personas, legal" in o, "quien escribe en toda la unidad sin administrarla: bajarlo a Lector y darle su área")
d = bien(); d["areas"]["ventas"]["permisos"][2] = u("carla@ejemplo.test", "writer")
c, o = corre(d)
ok("carla@ejemplo.test (colabora en ventas) tiene «Colaborador»" in o and "cámbialo a «Gestor de contenido»" in o, "«Colaborador» en el área: no deja mover ni borrar")
d = bien(); d["areas"]["ventas"]["permisos"][2] = u("carla@ejemplo.test", "reader")
c, o = corre(d)
ok("carla@ejemplo.test (colabora en ventas) no puede escribir en su área (tiene «Lector»)" in o, "quien colabora sin edición en su área")
d = bien(); d["areas"]["ventas"]["permisos"].append(u("eva@ejemplo.test", "fileOrganizer"))
c, o = corre(d)
ok("eva@ejemplo.test puede escribir en ventas" in o, "quien escribe en un área sin ser de ella")
d = bien(); d["areas"]["personas"]["limitada"] = False
c, o = corre(d)
ok("El área personas/ está declarada restringida en guia.md, pero en Drive no tiene acceso limitado" in o, "área declarada restringida sin acceso limitado")
d = bien(); d["areas"]["operacion"]["limitada"] = True
c, o = corre(d)
ok("El área operacion/ tiene acceso limitado en Drive, pero guia.md no la declara restringida" in o, "acceso limitado sin declararlo")
d = bien(); d["restringidos"]["ventas/cuentas"]["limitada"] = False
c, o = corre(d)
ok("La carpeta restringido/ de ventas/cuentas no tiene acceso limitado" in o, "carpeta restringido/ sin acceso limitado")
d = bien(); d["proyectos"]["operacion/soporte"]["permisos"][-1] = u("dani@ejemplo.test", "reader")
c, o = corre(d)
ok("dani@ejemplo.test colabora en operacion/soporte pero no puede escribir en su carpeta" in o, "quien colabora en un proyecto sin edición en su carpeta")
d = bien(); d["raiz"]["permisos"] = [x for x in BASE if x["email"] != "eva@ejemplo.test"]
c, o = corre(d)
ok("eva@ejemplo.test" not in o, "a quien solo colabora en un área restringida no se le pide acceso a la raíz")
d = bien(); d["raiz"]["permisos"] = [x for x in BASE if x["email"] != "carla@ejemplo.test"]
c, o = corre(d)
ok("carla@ejemplo.test aparece en guia.md o en un proyecto, pero no tiene acceso a la carpeta" in o, "quien figura en guia.md sin acceso a la carpeta")
import re as _re
def acciones(o):
    return json.loads(o.split("=== ACCIONES\n", 1)[1].strip())
d = bien(); d["areas"]["personas"]["limitada"] = False; d["raiz"]["permisos"] = [x for x in BASE if x["email"] != "carla@ejemplo.test"]
c, o = corre(d); a = acciones(o)
ok(not any(x["tipo"] == "limitar" for x in a["con_conector"]) and "aquí no se sabe la cuenta de dirección" in o and {"tipo": "compartir", "cuenta": "carla@ejemplo.test", "carpeta": "", "rol": "reader"} in a["con_conector"], "limitar con el conector solo si se sabe a quién conservar: «dirección» no es una cuenta, va a la web; compartir como Lector a quien falta")
d = bien(); d["areas"]["legal"] = {"permisos": BASE, "limitada": False}
c, o = corre(d); a = acciones(o)
ok({"tipo": "limitar", "carpeta": "legal", "conservan": ["beto@ejemplo.test", "eva@ejemplo.test"], "escriben": []} in a["con_conector"], "limitar con el conector conserva a quien lee (guia.md) y a quien escribe, sin quien administra")
d = bien(); d["proyectos"]["operacion/soporte"]["limitada"] = False
d["areas"]["operacion"]["permisos"] = BASE[:4] + [u("dani@ejemplo.test", "fileOrganizer")]
# un proyecto declarado restringido con dueño en su proyecto.md y colaborador: conservan el dueño del área, el colaborador y el dueño
import shutil
R2 = pathlib.Path(tempfile.mkdtemp()) / "raiz"; shutil.copytree(R, R2)
am = R2 / "operacion" / "area.md"; am.write_text(am.read_text().replace("- `soporte/`", "- `soporte/` — restringido:", 1))
f = pathlib.Path(tempfile.mkdtemp()) / "drive.json"; f.write_text(json.dumps(d))
o2 = subprocess.run([sys.executable, str(P), str(R2), "--drive", str(f)], capture_output=True, text=True).stdout; a2 = acciones(o2)
ok({"tipo": "limitar", "carpeta": "operacion/soporte", "conservan": ["dani@ejemplo.test"], "escriben": ["dani@ejemplo.test"]} in a2["con_conector"], "limitar un proyecto conserva a quien colabora y dice quién escribe (el dueño que administra no hace falta)")
g = bien(); g["raiz"]["permisos"] = BASE + [{"email": "equipo@ejemplo.test", "role": "fileOrganizer", "type": "group"}, {"role": "reader", "type": "domain", "domain": "ejemplo.test"}]
c, o = corre(g)
ok("El grupo equipo@ejemplo.test tiene «Gestor de contenido»" in o and "la lee todo el dominio ejemplo.test" in o, "un grupo que escribe y un dominio que lee se ven, no se tiran")
g["raiz"]["permisos"] = [x for x in g["raiz"]["permisos"] if x.get("email") != "carla@ejemplo.test"]
c, o = corre(g); a = acciones(o)
ok("carla@ejemplo.test aparece en guia.md o en un proyecto y no figura con su correo" in o and "puede entrar por un grupo" in o and not any(x["tipo"] == "compartir" for x in a["con_conector"]), "con un grupo o un dominio en la raíz, a quien no figura no se le comparte a ciegas")
g = bien(); g["raiz"]["permisos"] = BASE + [{"role": "writer", "type": "anyone"}]
c, o = corre(g)
ok("está abierta a cualquiera con el enlace con «Colaborador»" in o, "«cualquiera con el enlace» que escribe es un cambio, no un silencio")
R3 = pathlib.Path(tempfile.mkdtemp()) / "raiz"; shutil.copytree(R, R3)
gm = R3 / "guia.md"; gm.write_text(gm.read_text().replace("Administra la carpeta: Ana Prueba", "Administra la carpeta: Juanjo").replace("| ana@ejemplo.test · colabora: carla@ejemplo.test |", "| ana@ejemplo.test, carla@ejemplo.test |", 1))
d = bien(); d["areas"]["ventas"]["permisos"] = BASE[:1] + [u("beto@ejemplo.test", "reader"), u("carla@ejemplo.test", "fileOrganizer")]
f = pathlib.Path(tempfile.mkdtemp()) / "drive.json"; f.write_text(json.dumps(d))
o3 = subprocess.run([sys.executable, str(P), str(R3), "--drive", str(f)], capture_output=True, text=True).stdout
ok("No se sabe la cuenta de quien administra la carpeta («Juanjo»" in o3 and "ana@ejemplo.test" in o3.split("se tomó por administrador")[1].split("\n")[0], "sin la cuenta de quien administra, se dice a quién se tomó por administrador")
ok("La celda Cuenta del área ventas/ no se deja leer" in o3 and "cámbiale el rol a «Lector» ahí" not in o3 and "corrige la celda antes de tocar su rol" in o3, "una celda Cuenta que no se deja leer no manda bajar a nadie: pide corregirla")
d = bien(); d["raiz"]["permisos"][1] = u("beto@ejemplo.test", "fileOrganizer")
c, o = corre(d); a = acciones(o)
ok(a["con_conector"] == [] and a["a_mano"] >= 1, "bajar un rol no se puede con el conector: queda a mano")
mi = {"raiz": {"permisos": [u("ana@ejemplo.test", "owner"), u("carla@ejemplo.test", "reader"), u("beto@ejemplo.test", "reader"), u("dani@ejemplo.test", "reader")]},
      "areas": {"ventas": {"permisos": [u("ana@ejemplo.test", "owner"), u("carla@ejemplo.test", "writer")], "limitada": False}}}
c, o = corre(mi)
ok("«Mi unidad»" in o and "carla@ejemplo.test (colabora en ventas)" not in o, "en «Mi unidad», «Editor» es el rol bueno para escribir en el área")
# lo que enseñó el tablero de Smile Pill el 2026-10-23: la cuenta de Claude no es la de Drive, el dueño «, de forma
# provisional», y un área cuya celda dice «Sin cuenta de Claude: registra …»
R4 = pathlib.Path(tempfile.mkdtemp()) / "raiz"; shutil.copytree(R, R4)
gm = R4 / "guia.md"; g = gm.read_text()
g = g.replace("| `ventas/` | Clientes, propuestas y precios | Ana Prueba | ana@ejemplo.test · colabora: carla@ejemplo.test |",
              "| `ventas/` | Clientes, propuestas y precios | Ana Prueba, de forma provisional | ana@ejemplo.test · colabora: carla@ejemplo.test |", 1)
g = g.replace("| `operacion/` | Área de soporte y entregas | Ana Prueba | ana@ejemplo.test |", "| `operacion/` | Área de soporte y entregas | Gabi Prueba | Sin cuenta de Claude: registra Ana Prueba |", 1)
g = g.replace("Administra la carpeta: Ana Prueba", "Administra la carpeta compartida y pone o quita los accesos: Ana Prueba, de forma provisional. Hoy vive en otra unidad.\nEn Drive: ana@ejemplo.test es ana@empresa.test")
gm.write_text(g)
BASE4 = [u("ana@empresa.test", "organizer"), u("beto@ejemplo.test", "reader"), u("carla@ejemplo.test", "reader"), u("eva@ejemplo.test", "reader"), u("dani@ejemplo.test", "reader"), u("gabi@empresa.test", "reader")]
d = bien(); d["raiz"]["permisos"] = BASE4
d["areas"]["ventas"] = {"permisos": BASE4[:1] + [u("beto@ejemplo.test", "reader"), u("carla@ejemplo.test", "fileOrganizer")], "limitada": False}
d["areas"]["operacion"] = {"permisos": BASE4 + [u("gabi@empresa.test", "fileOrganizer")], "limitada": False}
d["areas"]["futura"] = {"permisos": BASE4, "limitada": False}; d["areas"]["archivo"] = {"permisos": BASE4, "limitada": False}
d = json.loads(json.dumps(d).replace("ana@ejemplo.test", "ana@empresa.test"))
f = pathlib.Path(tempfile.mkdtemp()) / "drive.json"; f.write_text(json.dumps(d))
o4 = subprocess.run([sys.executable, str(P), str(R4), "--drive", str(f)], capture_output=True, text=True).stdout
ok("ana@ejemplo.test" not in o4 and "No se sabe la cuenta de quien administra" not in o4, "«En Drive:» traduce la cuenta de Claude a la de Drive: ni «sin acceso» ni administrador desconocido")
ok("Para cambiar" not in o4, f"con la cuenta de Drive declarada y el dueño «, de forma provisional», nada que cambiar ({[l for l in o4.split(chr(10)) if l.startswith('- ')][:3]})")
ok("gabi@empresa.test escribe en operacion" in o4 and "el área no declara ninguna cuenta" in o4 and "si es su responsable Gabi Prueba" in o4, "quien escribe en un área sin cuenta declarada va a «Para comprobar», con el dueño por su nombre")
d["areas"]["ventas"]["permisos"][0] = u("ana@empresa.test", "reader")
f.write_text(json.dumps(d)); o5 = subprocess.run([sys.executable, str(P), str(R4), "--drive", str(f)], capture_output=True, text=True).stdout
ok("ana@empresa.test (responsable en ventas) no puede escribir en su área (tiene «Lector»): dale" in o5, "la frase de quien no puede escribir en su área está bien formada")
# «En Drive:» con « y », al revés, mal escrita; y la cuenta de Claude que también está en Drive
def con_linea(linea, drive):
    R5 = pathlib.Path(tempfile.mkdtemp()) / "raiz"; shutil.copytree(R4, R5)
    g5 = R5 / "guia.md"; g5.write_text(g5.read_text().replace("En Drive: ana@ejemplo.test es ana@empresa.test", linea))
    f5 = pathlib.Path(tempfile.mkdtemp()) / "drive.json"; f5.write_text(json.dumps(drive))
    return subprocess.run([sys.executable, str(P), str(R5), "--drive", str(f5)], capture_output=True, text=True).stdout
d2 = dict(d); d2["areas"]["ventas"]["permisos"][0] = u("ana@empresa.test", "organizer")
o6 = con_linea("En Drive: ana@ejemplo.test es ana@empresa.test y beto@ejemplo.test es beto@ejemplo.test", d2)
ok("Para cambiar" not in o6, "«En Drive:» admite « y » entre pares")
o7 = con_linea("En Drive: ana@empresa.test es ana@ejemplo.test", d2)
ok("está al revés" in o7 and '"compartir"' not in o7.split("=== ACCIONES")[1], "una línea al revés se avisa y no se comparte nada a ciegas")
o8 = con_linea("En Drive: ana@ejemplo.test ana@empresa.test; beto", d2)
ok("no da dos correos" in o8 and "compartir" not in o8.split("=== ACCIONES")[1], "un tramo que no da dos correos se avisa, sin acción de compartir")
d3 = json.loads(json.dumps(d2)); d3["raiz"]["permisos"].append(u("ana@ejemplo.test", "organizer"))
o9 = con_linea("En Drive: ana@ejemplo.test es ana@empresa.test", d3)
ok("ana@ejemplo.test tiene" not in o9 and "Para cambiar" not in o9, "la cuenta de Claude que también está en Drive es la misma persona, no alguien sin declarar")
print("La guia.md de la 1.22: «Acceso» y «Responsable»")
BASE[:] = [u("ana@ejemplo.test", "organizer"), u("beto@ejemplo.test", "reader"), u("carla@ejemplo.test", "reader"), u("eva@ejemplo.test", "reader"), u("dani@ejemplo.test", "reader")]   # las pruebas de arriba la tocan
import shutil as _sh
R22 = pathlib.Path(tempfile.mkdtemp()) / "raiz"; _sh.copytree(R, R22)
g = R22 / "guia.md"; t = g.read_text(encoding="utf-8")
t = guia_122(t, personas="Beto Prueba")
g.write_text(t, encoding="utf-8")
f = pathlib.Path(tempfile.mkdtemp()) / "drive.json"; f.write_text(json.dumps(bien()))
o22 = subprocess.run([sys.executable, str(P), str(R22), "--drive", str(f)], capture_output=True, text=True).stdout
ok("Todo cuadra" in o22 and "Para cambiar" not in o22, "con «Acceso», los mismos permisos cuadran igual")
d = bien(); d["areas"]["personas"]["limitada"] = False; f.write_text(json.dumps(d))
o22 = subprocess.run([sys.executable, str(P), str(R22), "--drive", str(f)], capture_output=True, text=True).stdout
ok("personas/ está declarada restringida en guia.md, pero en Drive no tiene acceso limitado" in o22, "un área «Restringida» en «Acceso» sin acceso limitado en Drive se avisa")
d = bien(); d["areas"]["ventas"]["limitada"] = True; f.write_text(json.dumps(d))
o22 = subprocess.run([sys.executable, str(P), str(R22), "--drive", str(f)], capture_output=True, text=True).stdout
ok("pon «Restringida» en su columna «Acceso»" in o22, "y al revés, se le dice que la marque en «Acceso»")
print("\n" + ("Todo bien." if not fallos else f"{fallos} fallo(s)."))
sys.exit(1 if fallos else 0)
