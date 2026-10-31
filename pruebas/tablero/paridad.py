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
# cuentas (1.24.2): la celda Cuenta de guia.md se lee igual en los siete scripts que la copian (cada uno se descarga suelto)
CON_CUENTAS = ["skills/sesion/abrir.py", "verificar.sh", "skills/sesion/cerrar.py", "skills/sesion/permisos.py", "skills/sesion/migrar_estructura.py",
               "skills/tablero/generar_vista.py", "skills/tablero/aplicar_cambios.py"]
def con_cuentas(ruta):
    src = (P / ruta).read_text(encoding="utf-8"); ns = {"re": re}
    for c in ("CORREO", "PALABRA_COLABORA"):
        exec(re.search(rf"^{c}\s*=.*$", src, re.M).group(0), ns)
    exec(re.search(r"^def cuentas\(.*?(?=^\S)", src, re.M | re.S).group(0), ns)
    return ns["cuentas"]
CELDAS_CUENTA = ["ana@x.mx", "ana@x.mx · colabora: beto@x.mx, carla@x.mx", "ana@x.mx, beto@x.mx", "", "Sin cuenta de Claude",
                 "ana@x.mx colaboradora: beto@x.mx", "ana@x.mx · colabora beto@x.mx", "ANA@X.MX · Colabora: Beto@X.mx", "ana@x.mx · co-labora: b@x.mx"]
_ref = [con_cuentas(CON_CUENTAS[0])(c) for c in CELDAS_CUENTA]
for ruta in CON_CUENTAS[1:]:
    _f = con_cuentas(ruta); dif = [c for c, r in zip(CELDAS_CUENTA, _ref) if _f(c) != r]
    bien = not dif
    print(("  bien  " if bien else "  FALLA ") + f"cuentas() de {ruta.split('/')[-1]} lee la celda Cuenta como abrir.py" + ("" if bien else f": difiere en {dif}")); fallos += not bien
# la línea «Zona horaria:» de guia.md se reconoce igual en abrir.py y en espejo.py (1.24.2)
def _rx_zona(ruta):
    src = (P / ruta).read_text(encoding="utf-8")
    m = re.search(r'r"(\^\\s\*\[-\*\]\?\\s\*\\\*\*\\s\*zona horaria[^"]*)"', src)
    return m.group(1) if m else None
_za, _ze = _rx_zona("skills/sesion/abrir.py"), _rx_zona("espejo.py")
bien = bool(_za) and _za == _ze
print(("  bien  " if bien else "  FALLA ") + "la línea «Zona horaria:» se lee igual en abrir.py y en espejo.py"); fallos += not bien
# sin_carpeta (1.23): el primer párrafo de guia.md, igual en la sesión y en el tablero
bloque = lambda ruta: (lambda s: s[s.index("# --- el primer párrafo de guia.md"):s.index("# --- fin del primer párrafo ---")])((P / ruta).read_text(encoding="utf-8"))
ba, bg = bloque("skills/sesion/abrir.py"), bloque("skills/tablero/generar_vista.py")
bien = ba == bg
print(("  bien  " if bien else "  FALLA ") + "sin_carpeta es la misma en abrir.py y en generar_vista.py"); fallos += not bien
ns = {"re": re}; exec(ba, ns)
casos = [(["Acme fabrica muebles.", "Cómo se trabaja está en `metodo.md`."], ["Acme fabrica muebles."]),
         (["Acme fabrica muebles; lo demás está en `guia.md`."], ["Acme fabrica muebles."]),
         (["Acme (ver `guia.md`; abajo) fabrica muebles."], [])]
for entrada, sale in casos:
    bien = ns["sin_carpeta"](entrada) == sale
    print(("  bien  " if bien else "  FALLA ") + f"sin_carpeta({entrada!r})"); fallos += not bien
# con_archivados (1.23): los registros con sus archivados, igual en la sesión, el tablero y el barrido
bloque2 = lambda ruta: (lambda s: s[s.index("# --- los registros con sus archivados ---"):s.index("# --- fin de los registros ---")])((P / ruta).read_text(encoding="utf-8"))
b3 = [bloque2(r_) for r_ in ("skills/sesion/abrir.py", "skills/tablero/generar_vista.py", "skills/tablero/barrido.py")]
bien = b3[0] == b3[1] == b3[2]
print(("  bien  " if bien else "  FALLA ") + "con_archivados es la misma en abrir.py, generar_vista.py y barrido.py"); fallos += not bien
sys.exit(1 if fallos else 0)
