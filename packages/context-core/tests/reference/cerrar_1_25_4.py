"""cerrar.py 1.25.4's text changes, frozen: context_core.write must return exactly what these did
(tests/test_write.py). Copied verbatim from plugins/memoria/skills/sesion/cerrar.py at v1.25.4; never edited."""
import re


def cabecera_hoy(t, hoy):
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m:
        return t
    cab = re.sub(r"^actualizado:.*$", f"actualizado: {hoy}", m.group(1), count=1, flags=re.M)
    if "actualizado:" not in cab:
        cab += f"\nactualizado: {hoy}"
    return f"---\n{cab}\n---\n" + t[m.end():]


def solo_cabecera(antes, despues):
    """Cierto si lo único que cambió entre los dos textos está dentro de la cabecera (entre los dos «---» iniciales)."""
    m1, m2 = re.match(r"^---\n.*?\n---\n", antes, re.S), re.match(r"^---\n.*?\n---\n", despues, re.S)
    return bool(m1 and m2) and antes[m1.end():] == despues[m2.end():] and antes != despues


def con_entrada_arriba(t, entrada):
    """Una entrada nueva de registro, debajo del título y encima de las demás; si ya está, nada."""
    entrada = entrada.strip() + "\n"
    if entrada.strip() in t:
        return t, False
    m = re.search(r"^# .*\n", t, re.M)
    if m:
        i = m.end()
        resto = t[i:]
        j = re.search(r"^## ", resto, re.M)
        if j:
            prefacio, cuerpo = resto[:j.start()], resto[j.start():]
            if not prefacio.strip():
                prefacio = "\n"
            elif not prefacio.endswith("\n\n"):
                prefacio = prefacio.rstrip("\n") + "\n\n"
            return t[:i] + prefacio + entrada + "\n" + cuerpo, True
        # sin entradas todavía (un registro recién abierto, o recién archivado con su línea «Archivado:»): lo que haya
        # debajo del título se queda delante de la primera entrada
        return t[:i] + ("\n" + resto.strip("\n") + "\n" if resto.strip() else "") + "\n" + entrada, True
    return t.rstrip("\n") + "\n\n" + entrada, True


def sin_bloque(t, nombre):
    """Quita entero el bloque «## nombre», si está."""
    return re.sub(r"^## " + re.escape(nombre) + r"\s*\n.*?(?=^## |\Z)", "", t, count=1, flags=re.M | re.S)


def con_bloque(t, nombre, cuerpo, antes_de=None, alias=()):
    """Reescribe entero el bloque «## nombre». Si no existe, lo crea debajo del título o, con antes_de, justo antes de
    ese bloque (al final si tampoco está). Los bloques de alias (los nombres de la 1.21) se retiran siempre: desde la
    1.22 solo queda el nombre nuevo, y en su sitio de la 1.22, no en el que tenía el viejo."""
    cuerpo = cuerpo.strip() + "\n"
    for viejo in alias:
        t = sin_bloque(t, viejo)
    m = re.search(r"^## " + re.escape(nombre) + r"\s*\n(.*?)(?=^## |\Z)", t, re.M | re.S)
    if m:
        return t[:m.start(1)] + cuerpo + "\n" + t[m.end(1):]
    nuevo = f"## {nombre}\n{cuerpo}\n"
    if antes_de:
        ma = re.search(r"^## " + re.escape(antes_de) + r"\s*$", t, re.M)
        if ma:
            return t[:ma.start()] + nuevo + t[ma.start():]
        return t.rstrip("\n") + "\n\n" + nuevo
    mt = re.search(r"^# .*\n", t, re.M)
    i = mt.end() if mt else 0
    return t[:i] + "\n" + nuevo + t[i:].lstrip("\n")
