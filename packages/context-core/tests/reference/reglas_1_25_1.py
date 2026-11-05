"""Frozen reference: three rules as abrir.py, generar_vista.py and barrido.py carried them in 1.25.1, before they took
them from context_core: the first paragraph of guia.md, the registers with their archives, and the restricted cell. Kept
only for the tests; never imported by the plugin or the server; do not edit."""
import pathlib, re
# --- el primer párrafo de guia.md sin lo que habla de la carpeta ---
# La misma función en abrir.py y en generar_vista.py (cada uno se descarga suelto); pruebas/tablero/paridad.py comprueba
# que las dos copias son idénticas y dan lo mismo (1.23; antes vivía dentro de cada script, fuera de la comprobación).
SOBRE_LA_CARPETA = r"`(?:metodo|guia)\.md`|plugin `memoria`|Aquí solo está lo nuestro"
def sin_carpeta(frases, rx=SOBRE_LA_CARPETA):
    """Las frases del primer párrafo de guia.md sin lo que habla de la carpeta o del método; de una frase unida con «;» a
    otra que no habla de ellos, se queda la otra (1.22.5), y no se parte por un «;» entre paréntesis. Dentro de cada parte,
    se queda lo que va antes de la coma, los dos puntos o la raya que abre lo de la carpeta, si es una frase de tres palabras
    o más: «Acme fabrica muebles, como dice `guia.md`» deja «Acme fabrica muebles» (1.24.8)."""
    out = []
    for f in frases:
        if not re.search(rx, f):
            out.append(f); continue
        quedan = []
        for c in [c.strip() for c in re.split(r";(?![^()]*\))", f)]:
            m = re.search(rx, c) if c else None
            if c and not m:
                quedan.append(c); continue
            cortes = [s.start() for s in re.finditer(r"[,:—](?![^()]*\))", c[:m.start()] if m else "")]
            t = c[:cortes[-1]].strip() if cortes else ""
            if len(t.split()) >= 3 and not re.search(rx, t):
                quedan.append(t)
        if quedan:
            t = "; ".join(quedan); t = t[0].upper() + t[1:]
            out.append(t if t[-1] in ".!?" else t + ".")
    return out
# --- los registros con sus archivados ---
# La misma función en abrir.py, generar_vista.py y barrido.py (cada uno se descarga suelto); pruebas/tablero/paridad.py
# comprueba que las tres copias son idénticas (1.23).
ARCHIVADO = re.compile(r"^(sesiones|decisiones)-(20\d\d)(?:-(\d+))?\.md$")
def archivados_de(carpeta, nombre, anio):
    """Los nombres de los archivados de un registro («sesiones» o «decisiones») de este año y del anterior, del más nuevo
    al más viejo. Los de años anteriores no se leen: lo que una decisión vieja sostiene ya está en Alcance o en el Estatus,
    y quien la cita la busca por el año que lleva su identificador."""
    vistos = []
    try:
        nombres = [x.name for x in pathlib.Path(carpeta).iterdir()]
    except OSError:
        nombres = []
    for n in nombres:
        m = ARCHIVADO.match(n)
        if m and m.group(1) == nombre and int(m.group(2)) >= int(anio) - 1:
            vistos.append((int(m.group(2)), int(m.group(3) or 1), n))
    return [n for _, _, n in sorted(vistos, reverse=True)]
def con_archivados(carpeta, nombre, vivo, anio, leer_):
    """(texto, entradas del vivo): el registro vivo seguido de las entradas de sus archivados recientes, como si no se
    hubiera archivado, así que los identificadores de cada decisión son los de siempre. Lo que no se deja leer se salta."""
    partes = [vivo or ""]
    for n in archivados_de(carpeta, nombre, anio):
        t = leer_(pathlib.Path(carpeta) / n) or ""
        m = re.search(r"^## ", t, re.M)
        if m:
            partes.append(t[m.start():])
    return "\n\n".join(p.strip("\n") for p in partes if p.strip()) + "\n", len(re.findall(r"^## ", vivo or "", re.M))
def respuestas_viejas(carpeta, anio, leer_):
    """Las líneas «Responde a:» de los archivados de decisiones de antes del año anterior, que no se leen enteros: un
    cuestionamiento respondido hace años sigue respondido (revisión de la 1.23, hallazgo 5). Es un patrón de línea."""
    recientes = set(archivados_de(carpeta, "decisiones", anio))
    out = []
    for n in archivados_de(carpeta, "decisiones", 0):
        if n not in recientes:
            out += re.findall(r"^Responde a:[ \t]*(.+)$", leer_(pathlib.Path(carpeta) / n) or "", re.M)
    return out
def restringida_celda(celda):
    """«Quién la lee» declara el área restringida: la palabra al inicio («Restringida: …», «Restringido a …»), o
    «restringida» como palabra suelta en otra parte de la celda («Dirección (restringida)») sin negarla («nunca
    restringida», «antes restringida»). «Los proyectos restringidos aparte» no la declara. Igual en abrir.py,
    generar_vista.py y vista.html (restringidaCelda)."""
    c = celda or ""
    if re.match(r"^[\W_]*restringid[oa]s?\b", c, re.I):
        return True
    return bool(re.search(r"\brestringidas?\b", c, re.I)) and not re.search(r"\b(?:nada|no|nunca|sin|antes)\s+(?:[^\s]+\s+)?restringid", c, re.I)


