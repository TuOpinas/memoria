#!/usr/bin/env python3
"""P33 · The process in the help (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-25, en el plan).

- The process, from start to end. Dado the board's help, Cuando «Proyectos de desarrollo de software» opens, Entonces
  its first article walks the eleven steps in order, and says apart that an audit happens at any moment, at the
  auditor's choice, and stops nothing.
- The roles are today's. Dado «Quién hace qué», Cuando it opens, Entonces it names Acepta, Construye and Administra,
  Audita as one that may have nobody, and Recibe as whoever a phase is delivered to.

Por la página del tablero (vista.html) leída como texto: los artículos de la ayuda son objetos con id:"…", t:"…" y h:
seguido de una plantilla entre acentos graves; su sección es la clave g:"…" del mismo objeto. Que los once pasos sean
los del proceso y estén en su orden, y que la ayuda se abra y se lea bien, quedan para la verificación: lo dice
RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P33_proceso_en_la_ayuda.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, re, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P05_lectores import *  # noqa: E402,F401,F403  (REPO, flujo: una sola copia)

VISTA = REPO / "plugins" / "memoria" / "skills" / "tablero" / "vista.html"
SECCION = "Proyectos de desarrollo de software"
ROLES = ("Acepta", "Construye", "Administra", "Audita", "nadie", "Recibe")


def pagina():
    if not VISTA.is_file():
        raise flujo.Montaje(f"no está la página del tablero en {VISTA}")
    return VISTA.read_text(encoding="utf-8", errors="replace")


def articulos(texto):
    """Los artículos de la ayuda, en el orden de la página: [{"g", "id", "t", "h"}]. Un artículo es un objeto «{… h:`…`}»
    cuyas claves de texto van antes de «h:»; la plantilla acaba en el primer acento grave que no va escapado."""
    out = []
    for m in re.finditer(r"\{([^{}`]*?)\bh:\s*`", texto):
        claves = dict(re.findall(r'\b(\w+)\s*:\s*"((?:[^"\\]|\\.)*)"', m.group(1)))
        if "id" not in claves or "t" not in claves:
            continue
        i, fin = m.end(), None
        while i < len(texto):
            if texto[i] == "\\":
                i += 2
                continue
            if texto[i] == "`":
                fin = i
                break
            i += 1
        if fin is None:
            continue
        out.append(dict(claves, h=texto[m.end():fin]))
    return out


FILA = re.compile(r"<tr\b[^>]*>((?:(?!<tr\b|</table>).)*?)</tr>", re.S)   # una fila, cortada en su </tr>
CELDA = re.compile(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", re.S)


def primera_celda(fila):
    """El texto de la primera celda (<td> o <th>) de una fila, sin etiquetas ni espacios a los lados."""
    m = CELDA.search(fila)
    return re.sub(r"<[^>]*>", "", m.group(1)).strip() if m else None


def escenarios(inf):
    arts = articulos(pagina())

    # 1 · El proceso, de principio a fin: el primer artículo de la sección es «desarrollo-proceso»; su h trae una
    #     lista ordenada con once <li>, y fuera de ella un texto con «en cualquier momento», «no detiene» y la palabra
    #     entera «auditor»
    problemas = []
    de_la_seccion = [a for a in arts if a.get("g") == SECCION]
    if not de_la_seccion:
        problemas.append(f"la ayuda no tiene ningún artículo con g:\"{SECCION}\" (hay {len(arts)} artículos)")
    else:
        primero = de_la_seccion[0]
        if primero.get("id") != "desarrollo-proceso":
            problemas.append(f"el primer artículo de «{SECCION}» es id:\"{primero.get('id')}\" («{primero.get('t')}»), no "
                             "id:\"desarrollo-proceso\"")
        else:
            h = primero["h"]
            listas = re.findall(r"<ol\b[^>]*>(.*?)</ol>", h, re.S)
            if len(listas) != 1:
                problemas.append(f"el h de «desarrollo-proceso» tiene {len(listas)} listas ordenadas (<ol>), no una")
            else:
                n = len(re.findall(r"<li\b", listas[0]))
                if n != 11:
                    problemas.append(f"la lista ordenada de «desarrollo-proceso» tiene {n} <li>, no once")
                fuera = re.sub(r"<ol\b[^>]*>.*?</ol>", " ", h, flags=re.S).lower()
                for palabra in ("en cualquier momento", "no detiene"):
                    if palabra not in fuera:
                        problemas.append(f"fuera de la lista, «desarrollo-proceso» no dice «{palabra}»")
                if not re.search(r"\bauditor\b", fuera):
                    problemas.append("fuera de la lista, «desarrollo-proceso» no dice la palabra «auditor» (no vale «auditoría»)")
    inf.escenario("El proceso, de principio a fin", problemas)

    # 2 · Los roles son los de hoy: el h de «desarrollo-roles» nombra los seis, y la fila de Audita (la de la tabla cuya
    #     primera celda es Audita, hasta su </tr>) no dice «decide»
    problemas = []
    roles = [a for a in arts if a.get("id") == "desarrollo-roles"]
    if len(roles) != 1:
        problemas.append(f"la ayuda tiene {len(roles)} artículos id:\"desarrollo-roles\", no uno")
    else:
        h = roles[0]["h"]
        for palabra in ROLES:
            if palabra not in h:
                problemas.append(f"«Quién hace qué» no dice «{palabra}»")
        filas = [f for f in FILA.findall(h) if primera_celda(f) == "Audita"]
        if not filas:
            problemas.append("«Quién hace qué» no tiene una fila de la tabla (<tr>…</tr>) cuya primera celda sea Audita")
        elif any("decide" in f for f in filas):
            problemas.append("la fila de Audita de «Quién hace qué» aún dice «decide» (decide en los puntos de control)")
    inf.escenario("Los roles son los de hoy", problemas)


flujo.principal("P33", escenarios)
