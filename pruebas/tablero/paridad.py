#!/usr/bin/env python3
"""Las tres copias de la regla de lo restringido dicen lo mismo: abrir.py (sesión), generar_vista.py (tablero) y
vista.html (la página). Saca las funciones de cada archivo, las corre con las mismas celdas de «Quién la lee» y compara.
Uso: paridad.py <raíz del plugin>. Sale con 1 si algo difiere o no da lo esperado."""
import json, pathlib, re, subprocess, sys
P = pathlib.Path(sys.argv[1])
def funciones(ruta, nombres):
    src = (P / ruta).read_text(encoding="utf-8"); ns = {"re": re}
    for n in nombres:
        m = re.search(rf"^def {n}\(.*?(?=^\S)", src, re.M | re.S); exec(m.group(0), ns)
    return ns
A = funciones("skills/sesion/abrir.py", ["restringida_celda", "lectores_de", "solo_nombre"])
G = funciones("skills/tablero/generar_vista.py", ["restringida_celda"])
CELDAS = {  # celda: (restringida, a quiénes)
    "Restringida: Ana Prueba y Beto Prueba": (True, "a Ana Prueba y Beto Prueba"),
    "Restringida a dirección": (True, "a dirección"),
    "Restringidas a dirección": (True, "a dirección"),
    "Restringido al equipo directivo": (True, "al equipo directivo"),
    "Restringida para dirección": (True, "para dirección"),
    "Restringida (dirección)": (True, "a dirección"),
    "**Restringida**: dirección": (True, "a dirección"),
    "«Restringida» — dirección": (True, "a dirección"),
    "Restringida: la leen Ana y Beto": (True, "a Ana y Beto"),
    "Dirección (restringida)": (True, "a Dirección"),
    "Ana (restringida), Beto (restringida)": (True, "a Ana, Beto"),
    "Restringida": (True, ""),
    "Todo el equipo": (False, None),
    "Todo el equipo, nada restringido": (False, None),
    "Todo el equipo; los proyectos restringidos aparte": (False, None),
    "Irrestringida": (False, None),
    "Abierta (antes restringida)": (False, None),
    "nunca restringida": (False, None),
    "no (aún) restringida": (False, None),
}
h = (P / "skills/tablero/vista.html").read_text(encoding="utf-8")
js = h[h.index("const restringidaCelda"):h.index("\nfunction noLeido")] + "\n" + h[h.index("const soloNombre"):h.index("\n", h.index("const soloNombre"))]
js += "\nconst c = " + json.dumps(list(CELDAS)) + ";\nconsole.log(JSON.stringify(c.map(x => [restringidaCelda(x), lectoresDe(x)])));"
J = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True).stdout)
fallos = 0
print("La regla de lo restringido, igual en la sesión, el tablero y la página")
for (celda, (r, lect)), (rj, lj) in zip(CELDAS.items(), J):
    ra, rg = A["restringida_celda"](celda), G["restringida_celda"](celda)
    la = A["lectores_de"](celda) if r else None
    bien = ra == rg == rj == r and (not r or la == lj == lect)
    print(("  bien  " if bien else "  FALLA ") + f"«{celda}»" + ("" if bien else f": abrir {ra}/{la!r}, tablero {rg}, página {rj}/{lj!r}"))
    fallos += not bien
for d in ("Agustín Torres (escribe también Patricio Torres, dueño de `ronda-semilla/`)", "Dirección (Ana, Beto)"):
    j_ = subprocess.run(["node", "-e", js.split("\nconst c = ")[0] + f"\nconsole.log(soloNombre({json.dumps(d)}))"], capture_output=True, text=True).stdout.strip()
    bien = A["solo_nombre"](d) == j_
    print(("  bien  " if bien else "  FALLA ") + f"el dueño «{d}» sale igual"); fallos += not bien
sys.exit(1 if fallos else 0)
