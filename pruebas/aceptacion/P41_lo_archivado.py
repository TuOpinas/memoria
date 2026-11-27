#!/usr/bin/env python3
"""P41 · What is archived, out of the way and marked (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-27, en el plan).

- Hidden by default. Dado an active area with a closed project, and an archived area, Cuando the board opens with the
  button off, Entonces neither shows in the side menu, and the button at its foot reads «Mostrar lo archivado (2)».
- Shown, each one says what it is. Dado the same folder, Cuando the button is turned on, Entonces the archived area goes
  to the end of the menu under the heading «Archivado», with a grey card, a grey title and «Archivada» where the count
  goes; the closed project goes to the end of its area's list, in grey and with the label «cerrado» on the right; and
  the active area keeps its place, card, title and count.
- The choice stays. Dado the button turned on, Cuando the board is opened again in the same browser, Entonces what is
  archived still shows, and the button reads «Ocultar lo archivado».
- Nothing archived, no button. Dado a folder with no closed project and no archived area, Cuando the board opens,
  Entonces the menu has no button for the archived.

Por una función de la página: menuArchivado(areas, proyectos, ver), del bloque entre «// >>> archivado» y
«// <<< archivado» de vista.html, que se saca como texto y se corre con node como pestanaAlCambiar en P25, sobre listas
de áreas y proyectos escritas aquí. Devuelve {"boton", "grupos": [{"slug", "archivada", "proyectos": [{"id",
"cerrado"}]}]}. Y la página leída como texto: el rótulo «Archivado», «Archivada», la etiqueta «cerrado» y el atributo
data-archivado, y que lea y escriba la clave «ver-archivadas». El gris, los sitios en pantalla y que la elección
sobreviva a cerrar y abrir la página quedan para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P41_lo_archivado.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P21_lineas_que_se_siguen import *  # noqa: E402,F401,F403  (cómo se saca y se corre un bloque de la página)

INICIO_A, FIN_A = "// >>> archivado", "// <<< archivado"
CLAVE = "ver-archivadas"
MOSTRAR, OCULTAR = "Mostrar lo archivado", "Ocultar lo archivado"

# La carpeta del encargo. En el orden de la guía, el área archivada va primero, para ver que pasa al final; y en
# ventas, el proyecto cerrado va primero, para ver que pasa detrás del abierto
AREAS = [{"slug": "archivo", "nombre": "Archivo", "proyectos": ["archivo--feria"]},
         {"slug": "ventas", "nombre": "Ventas", "proyectos": ["ventas--campana", "ventas--portal"]}]
PROYECTOS = [{"id": "archivo--feria", "area": "archivo", "nombre": "Feria 2025", "cerrado": True},
             {"id": "ventas--campana", "area": "ventas", "nombre": "Campaña", "cerrado": True},
             {"id": "ventas--portal", "area": "ventas", "nombre": "Portal", "cerrado": False}]
OCULTO = [{"slug": "ventas", "archivada": False, "proyectos": [{"id": "ventas--portal", "cerrado": False}]}]
VISTO = [{"slug": "ventas", "archivada": False,
          "proyectos": [{"id": "ventas--portal", "cerrado": False}, {"id": "ventas--campana", "cerrado": True}]},
         {"slug": "archivo", "archivada": True}]

# Sin nada archivado: dos áreas con proyectos abiertos y (añadido) una sin proyectos, que no es archivada
AREAS_LIMPIAS = [{"slug": "ventas", "nombre": "Ventas", "proyectos": ["ventas--portal", "ventas--campana"]},
                 {"slug": "compras", "nombre": "Compras", "proyectos": ["compras--proveedores"]},
                 {"slug": "nueva", "nombre": "Nueva", "proyectos": []}]
PROYECTOS_LIMPIOS = [{"id": "ventas--portal", "area": "ventas", "nombre": "Portal", "cerrado": False},
                     {"id": "ventas--campana", "area": "ventas", "nombre": "Campaña", "cerrado": False},
                     {"id": "compras--proveedores", "area": "compras", "nombre": "Proveedores", "cerrado": False}]
LIMPIO = [{"slug": "ventas", "archivada": False, "proyectos": [{"id": "ventas--portal", "cerrado": False},
                                                               {"id": "ventas--campana", "cerrado": False}]},
          {"slug": "compras", "archivada": False, "proyectos": [{"id": "compras--proveedores", "cerrado": False}]},
          {"slug": "nueva", "archivada": False, "proyectos": []}]


def menu(areas, proyectos, ver, problemas):
    r = correr(INICIO_A, FIN_A, "menuArchivado", [areas, proyectos, ver], problemas)
    if r is None:
        return None
    if not isinstance(r, dict) or "boton" not in r or not isinstance(r.get("grupos"), list):
        problemas.append(f"menuArchivado(...) devolvió {json.dumps(r, ensure_ascii=False)[:120]}, no {{\"boton\", \"grupos\"}}")
        return None
    return r


def forma(grupos, esperado):
    """De cada grupo, lo que el esperado mira: slug y archivada; y los proyectos (id y cerrado) si el esperado los trae."""
    out = []
    for g, e in zip(grupos, esperado + [{}] * len(grupos)):
        if not isinstance(g, dict):
            out.append(g)
            continue
        f = {"slug": g.get("slug"), "archivada": g.get("archivada")}
        if "proyectos" in e:
            ps = g.get("proyectos")
            f["proyectos"] = ([{"id": saca(p, "id"), "cerrado": saca(p, "cerrado")} for p in ps]
                              if isinstance(ps, list) else ps)
        out.append(f)
    return out


def grupos_igual(problemas, que, r, esperado):
    igual(problemas, que, forma(r["grupos"], esperado), esperado)


def pagina():
    if not VISTA.is_file():
        raise flujo.Montaje(f"no está la página del tablero en {VISTA}")
    return VISTA.read_text(encoding="utf-8", errors="replace")


def escenarios(inf):
    # 1 · Oculto por defecto: con el botón apagado, ni el área archivada ni el proyecto cerrado; el botón dice
    #     «Mostrar lo archivado (2)» (un área archivada + un proyecto cerrado de un área vigente)
    problemas = []
    r = menu(AREAS, PROYECTOS, False, problemas)
    if r is not None:
        igual(problemas, "el botón con lo archivado oculto", r["boton"], f"{MOSTRAR} (2)")
        grupos_igual(problemas, "el menú con lo archivado oculto", r, OCULTO)
    # Añadido: los proyectos cerrados del área archivada no cuentan aparte: con dos, el botón sigue en (2)
    r = menu([dict(AREAS[0], proyectos=["archivo--feria", "archivo--expo"])] + AREAS[1:],
             PROYECTOS + [{"id": "archivo--expo", "area": "archivo", "nombre": "Expo", "cerrado": True}], False, problemas)
    if r is not None:
        igual(problemas, "el botón con un área archivada de dos proyectos", r["boton"], f"{MOSTRAR} (2)")
    inf.escenario("Hidden by default", problemas)

    # 2 · Visto, cada uno dice qué es: el área vigente en su sitio, con el abierto y después el cerrado marcado; el área
    #     archivada al final y marcada. Y la página trae «Archivado», «Archivada», «cerrado» y data-archivado
    problemas = []
    r = menu(AREAS, PROYECTOS, True, problemas)
    if r is not None:
        grupos_igual(problemas, "el menú con lo archivado visto", r, VISTO)
    texto = pagina()
    for cadena, que in (("Archivado", "el rótulo del grupo del final"), ("Archivada", "lo que va donde la cuenta"),
                        ("cerrado", "la etiqueta del proyecto cerrado"), ("data-archivado", "el atributo de lo que marca")):
        if cadena not in texto:
            problemas.append(f"la página del tablero no tiene «{cadena}» ({que})")
    inf.escenario("Shown, each one says what it is", problemas)

    # 3 · La elección se queda: la página lee y escribe la clave «ver-archivadas», y con ver verdadero el botón dice
    #     «Ocultar lo archivado» y lo archivado sale
    problemas = []
    texto = pagina()
    for patron, que in ((r'getItem\(\s*["\']' + CLAVE + r'["\']\s*\)', "la lee"),
                        (r'setItem\(\s*["\']' + CLAVE + r'["\']\s*,', "la escribe")):
        if not re.search(patron, texto):
            problemas.append(f"la página del tablero no {que} con la clave «{CLAVE}»")
    r = menu(AREAS, PROYECTOS, True, problemas)
    if r is not None:
        igual(problemas, "el botón con lo archivado visto", r["boton"], OCULTAR)
        grupos_igual(problemas, "el menú con lo archivado visto", r, VISTO)
    inf.escenario("The choice stays", problemas)

    # 4 · Nada archivado, sin botón: con el botón apagado y encendido, boton es null y el menú trae todo como está.
    #     Añadido: un área sin proyectos no es archivada
    problemas = []
    for ver in (False, True):
        r = menu(AREAS_LIMPIAS, PROYECTOS_LIMPIOS, ver, problemas)
        if r is not None:
            igual(problemas, f"el botón sin nada archivado (ver {str(ver).lower()})", r["boton"], None)
            grupos_igual(problemas, f"el menú sin nada archivado (ver {str(ver).lower()})", r, LIMPIO)
    inf.escenario("Nothing archived, no button", problemas)


flujo.principal("P41", escenarios)
