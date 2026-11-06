#!/usr/bin/env python3
"""Las dos copias de la regla de lo restringido dicen lo mismo: context_core (la sesión y el tablero, desde el paso 0 de
la versión alojada) y vista.html (la página). Las corre con las mismas celdas de «Quién la lee» y compara.
Uso: paridad.py <raíz del plugin>. Sale con 1 si algo difiere o no da lo esperado."""
import json, pathlib, re, subprocess, sys
P = pathlib.Path(sys.argv[1])
# desde el paso 0 de la versión alojada, la regla de lo restringido, el primer párrafo y los archivados viven en context_core
sys.path.insert(0, str(P.resolve().parent.parent / "packages" / "context-core"))
from context_core import compat as _cc  # noqa: E402
def funciones(ruta, nombres):
    src = (P / ruta).read_text(encoding="utf-8"); ns = {"re": re}
    for n in nombres:
        m = re.search(rf"^def {n}\(.*?(?=^\S)", src, re.M | re.S); exec(m.group(0), ns)
    return ns
A = funciones("skills/sesion/abrir.py", ["lectores_de", "solo_nombre"]); A["restringida_celda"] = _cc.restringida_celda
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
print("La regla de lo restringido, igual en la sesión y el tablero (context_core) y en la página")
for (celda, (r, lect)), (rj, lj) in zip(CELDAS.items(), J):
    ra = A["restringida_celda"](celda)
    la = A["lectores_de"](celda) if r else None
    bien = ra == rj == r and (not r or la == lj == lect)
    print(("  bien  " if bien else "  FALLA ") + f"«{celda}»" + ("" if bien else f": sesión y tablero {ra}/{la!r}, página {rj}/{lj!r}"))
    fallos += not bien
for d in ("Agustín Torres (escribe también Patricio Torres, dueño de `ronda-semilla/`)", "Dirección (Ana, Beto)"):
    j_ = subprocess.run(["node", "-e", js.split("\nconst c = ")[0] + f"\nconsole.log(soloNombre({json.dumps(d)}))"], capture_output=True, text=True).stdout.strip()
    bien = A["solo_nombre"](d) == j_
    print(("  bien  " if bien else "  FALLA ") + f"el dueño «{d}» sale igual"); fallos += not bien
# cuentas (1.24.2): desde el paso 0 de la versión alojada la celda Cuenta se lee en un solo sitio, context_core; los ocho
# scripts lo llevan metido igual (pruebas/sesion/probar_cuentas.py) y test_compat.py lo compara con la copia de la 1.25.1
# la línea «Zona horaria:» de guia.md se reconoce igual en abrir.py y en espejo.py (1.24.2)
def _rx_zona(ruta):
    src = (P / ruta).read_text(encoding="utf-8")
    m = re.search(r'r"(\^\\s\*\[-\*\]\?\\s\*\\\*\*\\s\*zona horaria[^"]*)"', src)
    return m.group(1) if m else None
_za, _ze = _rx_zona("skills/sesion/abrir.py"), _rx_zona("espejo.py")
bien = bool(_za) and _za == _ze
print(("  bien  " if bien else "  FALLA ") + "la línea «Zona horaria:» se lee igual en abrir.py y en espejo.py"); fallos += not bien
# sin_carpeta (1.23): el primer párrafo de guia.md; la sesión y el tablero la toman de context_core
ns = {"sin_carpeta": _cc.sin_carpeta}
casos = [(["Acme fabrica muebles.", "Cómo se trabaja está en `metodo.md`."], ["Acme fabrica muebles."]),
         (["Acme fabrica muebles; lo demás está en `guia.md`."], ["Acme fabrica muebles."]),
         (["Acme (ver `guia.md`; abajo) fabrica muebles."], []),
         # 1.24.8 (d5): sin «;», se queda lo que dice qué es la organización, antes de lo de la carpeta
         (["Acme fabrica muebles para oficinas, como explica `guia.md`."], ["Acme fabrica muebles para oficinas."]),
         (["Acme fabrica muebles: el mapa está en `guia.md`; lo aplica el plugin `memoria`."], ["Acme fabrica muebles."]),
         (["Sigue el método del plugin `memoria`, porque la ventaja es la misma."], []),
         (["Acme, ver `guia.md`."], [])]
for entrada, sale in casos:
    bien = ns["sin_carpeta"](entrada) == sale
    print(("  bien  " if bien else "  FALLA ") + f"sin_carpeta({entrada!r})"); fallos += not bien
# ID_VALIDO (1.24.8): generar_vista.py va suelto a la computadora y lleva su copia; la de datos.py la usa también plan_subida.py
_idv = lambda ruta: (re.search(r'^ID_VALIDO = re\.compile\((r"[^"]*")\)', (P / ruta).read_text(encoding="utf-8"), re.M) or [None, None])[1]
bien = bool(_idv("skills/tablero/datos.py")) and _idv("skills/tablero/datos.py") == _idv("skills/tablero/generar_vista.py") and "ID_VALIDO = " not in (P / "skills/tablero/plan_subida.py").read_text(encoding="utf-8")
print(("  bien  " if bien else "  FALLA ") + "ID_VALIDO es el mismo en datos.py y generar_vista.py, y plan_subida.py usa el de datos.py"); fallos += not bien
# con_archivados (1.23): la sesión, el tablero y el barrido la toman de context_core; test_compat.py la compara con la 1.25.1
sys.exit(1 if fallos else 0)
