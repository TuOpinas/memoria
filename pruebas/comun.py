"""Lo que comparten las pruebas: la raíz inventada de pruebas/tablero/raiz en su forma de la 1.22.

guia_122(texto) pasa la tabla de áreas de su guia.md a la de la 1.22 («Responsable» y la columna «Acceso»), con las mismas
áreas y cuentas; raiz_migrada() copia la raíz a una carpeta temporal y la migra de verdad con migrar_estructura.py, por la
cuenta de Ana (responsable de contexto: migra todo lo que su carpeta deja leer). Así ninguna prueba fabrica a mano su propia
versión de la 1.22.
"""
import json, os, pathlib, shutil, subprocess, sys, tempfile, time

PRUEBAS = pathlib.Path(__file__).resolve().parent
RAIZ = PRUEBAS / "tablero" / "raiz"
MIG = PRUEBAS.parent / "plugins" / "memoria" / "skills" / "sesion" / "migrar_estructura.py"


def guia_122(texto, personas="Dirección", legal="Ana Prueba y Beto Prueba"):
    """La tabla de áreas de la guia.md de prueba, con «Responsable» y «Acceso»; «Quién la lee» de las dos áreas
    restringidas pasa a decir solo quién la lee (personas y legal, por defecto «Dirección» y «Ana Prueba y Beto Prueba»)."""
    return (texto.replace("| Área | Qué es | Dueño | Cuenta | Quién la lee |\n|---|---|---|---|---|",
                          "| Área | Qué es | Responsable | Cuenta | Quién la lee | Acceso |\n|---|---|---|---|---|---|")
            .replace("| Todo el equipo |\n", "| Todo el equipo | Abierta |\n")
            .replace("| Todo el equipo, nada restringido |", "| Todo el equipo, nada restringido | Abierta |")
            .replace("| Restringida: dirección |", f"| {personas} | Restringida |")
            .replace("| Restringida: Ana Prueba y Beto Prueba |", f"| {legal} | Restringida |"))


PERSONAS_125 = {"ana@ejemplo.test": "Ana Prueba", "beto@ejemplo.test": "Beto Prueba", "carla@ejemplo.test": "Carla Prueba",
                "eva@ejemplo.test": "Eva Prueba", "dani@ejemplo.test": "Dani Prueba"}


def guia_125(texto, extra=""):
    """La guia.md de la 1.22 (la salida de guia_122 o de la migración) en la forma de la 1.25: «Quién es quién» con una
    línea por persona, y la tabla con «Colabora» y nombres en lugar de «Cuenta» con correos. Las mismas áreas y las
    mismas personas, así que lo que cada cuenta puede hacer tiene que salir igual en las dos formas. «Dirección» (un grupo)
    pasa a ser Beto Prueba: desde la 1.25 «Quién la lee» lleva personas del registro. extra va al final del registro."""
    import re as _re
    nom = lambda celda: ", ".join(PERSONAS_125[c] for c in _re.findall(r"[\w.+-]+@[\w.-]+", celda))
    out, en_tabla, cab = [], False, None
    for l in texto.split("\n"):
        if l.startswith("| Área |"):
            cab = [x.strip() for x in l.strip().strip("|").split("|")]
            i = cab.index("Cuenta"); cab[i] = "Colabora"; out.append("| " + " | ".join(cab) + " |"); en_tabla = True; continue
        if en_tabla and l.startswith("|") and not _re.match(r"^\|[\s:|-]+\|?\s*$", l):
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            i = cab.index("Colabora")
            partes = c[i].split("colabora:")
            c[i] = nom(partes[1]) if len(partes) > 1 else ""
            c = [_re.sub(r"^Restringida:\s*", "", x.replace("Dirección", "Beto Prueba").replace("dirección", "Beto Prueba")) for x in c]
            out.append("| " + " | ".join(c) + " |"); continue
        if en_tabla and not l.startswith("|"):
            en_tabla = False
        out.append(l)
    t = "\n".join(out)
    reg = "## Quién es quién\n" + "".join(f"- {n} · {c}\n" for c, n in PERSONAS_125.items()) + extra + "\n"
    t = _re.sub(r"\s*\(([\w.+-]+@[\w.-]+)\)", "", t)   # «Contexto común: Nombre (correo)» se queda en el nombre
    return t.rstrip("\n") + "\n\n" + reg


def raiz_125(cuenta="ana@ejemplo.test", nombre="Ana Prueba"):
    """La raíz migrada a la 1.22 y después pasada a la forma de la 1.25 (guia.md y las líneas «Colabora:» con nombres)."""
    import re as _re
    r, sal = raiz_migrada(cuenta, nombre)
    g = r / "guia.md"; g.write_text(guia_125(g.read_text(encoding="utf-8")), encoding="utf-8")
    for pm in r.rglob("proyecto.md"):
        t = pm.read_text(encoding="utf-8")
        t2 = _re.sub(r"(?m)^(\s*[-*]?\s*\**\s*Colabora[n]?\s*\**\s*:.*)$", lambda m: _re.sub(r"\s*\([\w.+-]+@[\w.-]+\)", "", m.group(1)), t)
        if t2 != t:
            pm.write_text(t2, encoding="utf-8")
    return r, sal


def raiz_migrada(cuenta="ana@ejemplo.test", nombre="Ana Prueba"):
    """Una copia de la raíz de prueba migrada a la 1.22 con el script de verdad; devuelve (ruta, salida del script)."""
    r = pathlib.Path(tempfile.mkdtemp()) / "raiz"
    shutil.copytree(RAIZ, r)
    # fechas fijas, como probar.sh y raiz_nueva(): con la fecha del checkout, la migración tomaría por «en uso» (tocado hace
    # menos de dos horas) cualquier proyecto de un área ajena, y la raíz no quedaría migrada entera
    viejo = time.mktime((2026, 8, 1, 12, 0, 0, 0, 0, -1))
    for f in r.rglob("*"):
        os.utime(f, (viejo, viejo))
    p = subprocess.run([sys.executable, str(MIG), str(r), "--cuenta", cuenta, "--nombre", nombre, "--plugin", "1.22.1"],
                       capture_output=True, text=True)
    return r, json.loads(p.stdout)


GV = PRUEBAS.parent / "plugins" / "memoria" / "skills" / "tablero" / "generar_vista.py"


def dos_corridas(raiz, tmp, fuera=False):
    """Como la puesta al día real: inventario y generación sobre la copia, y una segunda corrida que reutiliza la base.
    Devuelve (primera, segunda, reutilizó algo); con fuera=True, «reutilizó» exige también lo de fuera de los proyectos.
    La usan probar_que_es.py y probar_personas.py (antes cada una tenía su copia)."""
    def corrida(sal, previos=None, sin_cambios=None):
        a = [sys.executable, str(GV), str(raiz), "--inventario"] + (["--sin-cambios", sin_cambios] if sin_cambios else [])
        inv = json.loads(subprocess.run(a, capture_output=True, text=True, check=True).stdout)
        ip = tmp / f"inv-{sal}.json"; ip.write_text(json.dumps(inv["inventario"]), encoding="utf-8")
        cop = tmp / f"copia-{sal}"
        for r_ in inv["leer"]:
            (cop / r_).parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(raiz / r_, cop / r_)
        cop.mkdir(exist_ok=True)
        subprocess.run([sys.executable, str(GV), str(cop), str(tmp / sal), "--desde-inventario", str(ip), "--version", "prueba"]
                       + (["--previos", str(previos)] if previos else []), check=True, stdout=subprocess.DEVNULL)
        return inv
    corrida("o1")
    est = json.loads((tmp / "o1" / "meta" / "estado.json").read_text(encoding="utf-8"))
    inv = corrida("o2", tmp / "o1", ",".join(est.get("huellas") or []))
    reuso = bool(inv["inventario"].get("reusar")) and (not fuera or bool(inv["inventario"].get("fuera_reusar")))
    return tmp / "o1", tmp / "o2", reuso
