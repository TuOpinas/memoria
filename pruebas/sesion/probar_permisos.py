#!/usr/bin/env python3
"""Prueba permisos.py contra la raíz inventada de pruebas/tablero/raiz y unos permisos de Drive inventados.

Uso: python3 pruebas/sesion/probar_permisos.py
"""
import json, pathlib, subprocess, sys, tempfile
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
ok(c == 0 and "Todo cuadra" in o, "con los permisos que declara la carpeta, todo cuadra")
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
mi = {"raiz": {"permisos": [u("ana@ejemplo.test", "owner"), u("carla@ejemplo.test", "reader"), u("beto@ejemplo.test", "reader"), u("dani@ejemplo.test", "reader")]},
      "areas": {"ventas": {"permisos": [u("ana@ejemplo.test", "owner"), u("carla@ejemplo.test", "writer")], "limitada": False}}}
c, o = corre(mi)
ok("«Mi unidad»" in o and "carla@ejemplo.test (colabora en ventas)" not in o, "en «Mi unidad», «Editor» es el rol bueno para escribir en el área")
print("\n" + ("Todo bien." if not fallos else f"{fallos} fallo(s)."))
sys.exit(1 if fallos else 0)
