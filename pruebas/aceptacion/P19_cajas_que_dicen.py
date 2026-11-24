#!/usr/bin/env python3
"""P19 · Boxes that say what they are (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-23, en el plan).

- A box carries its short line. Dado a row of «Datos», «Componentes» or «Infraestructura» with «En corto», Cuando its
  drawing opens, Entonces the box shows the name and, under it, that line.
- Without the column nothing changes. Dado a design with no «En corto» column, Cuando its drawings open, Entonces each
  box carries only its name and the tab does not warn.
- Colour tells the role. Dado a drawing with boxes on the flow, a box that lines reach and none leave, and others,
  Cuando it opens, Entonces the three kinds have different colours, and what is external goes with the others.
- The legend names the roles. Dado a drawing with more than one colour, Cuando it opens, Entonces a legend under it
  names each colour, and a box's window says its role in words.

Por las dos entradas de F5: los tres primeros, por el generador del tablero sobre la raíz de muestra de P05_lectores.py
(en_corto y rol de cada elemento de diseno.entidades, componentes e infraestructura); el cuarto, por trazarDesarrollo
(diseno) de la página, corrido con node como en P21_lineas_que_se_siguen.py (la leyenda). Los colores y que la ventana
de una caja diga su rol quedan para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P19_cajas_que_dicen.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P21_lineas_que_se_siguen import *  # noqa: E402,F401,F403  (la muestra de P05, cómo se saca y se corre el trazado, y la base de P20)

PARTES = ("entidades", "componentes", "infraestructura")

# «En corto» en otra posición en cada sección: segunda en «Datos», última en «Componentes», tercera en «Infraestructura»
CORTO = {
    "entidades": {"cliente": "Quien compra", "pedido": "Una compra", "producto": "Lo que se vende", "categoria": ""},
    "componentes": {"Tienda web": "Donde se pide", "API": "Guarda pedidos", "Motor de pagos": "Cobra",
                    "Panel interno": ""},
    "infraestructura": {"Servidor web": "Sirve todo", "Base de datos": "", "Dominio": "La dirección"},
}
CON_CORTO = (
    [(DISENO, "| Entidad | Grupo | Qué es | Se relaciona con |\n|---|---|---|---|",
      "| Entidad | En corto | Grupo | Qué es | Se relaciona con |\n|---|---|---|---|---|")]
    + [(DISENO, f"| {n} | {g} |", f"| {n} | {CORTO['entidades'][n]} | {g} |") for n, (g, _) in ENTIDADES.items()]
    + [(DISENO, "| Componente | Qué hace | Dónde vive | Conecta con |\n|---|---|---|---|",
        "| Componente | Qué hace | Dónde vive | Conecta con | En corto |\n|---|---|---|---|---|")]
    + [(DISENO, f"| muestra/portal:{d} | {c} |".replace("|  |", "| |"),
        f"| muestra/portal:{d} | {c} | {CORTO['componentes'][n]} |".replace("|  |", "| |"))
       for n, d, c in (("Tienda web", "web", "API"), ("API", "api", "Motor de pagos"), ("Motor de pagos", "pagos", ""),
                       ("Panel interno", "panel", "API · Motor de pagos"))]
    + [(DISENO, "| Pieza | Para qué | Dónde | Conecta con |\n|---|---|---|---|",
        "| Pieza | Para qué | En corto | Dónde | Conecta con |\n|---|---|---|---|---|")]
    + [(DISENO, f"| {n} | {p} |", f"| {n} | {p} | {CORTO['infraestructura'][n]} |")
       for n, p in (("Servidor web", "Sirve la tienda y la API"), ("Base de datos", "Guarda clientes, pedidos y productos"),
                    ("Dominio", "La dirección de la tienda"))])

# Los tres roles: «Componentes» con «Externo» y «Flujo: Tienda web → API»; Motor de pagos es externo; Buzón recibe y no
# saca; Panel interno saca líneas sin estar en el flujo. «Datos» con la base de P20. La infraestructura, sin «Flujo:»
CON_ROLES = CON_BASE + [
    (DISENO, "| Componente | Qué hace | Dónde vive | Conecta con |\n|---|---|---|---|",
     "| Componente | Qué hace | Dónde vive | Externo | Conecta con |\n|---|---|---|---|---|"),
    (DISENO, "| muestra/portal:web | API |", "| muestra/portal:web | | API |"),
    (DISENO, "| muestra/portal:api | Motor de pagos |", "| muestra/portal:api | | Motor de pagos |"),
    (DISENO, "| muestra/portal:pagos | |", "| muestra/portal:pagos | sí | |"),
    (DISENO, "| muestra/portal:panel | API · Motor de pagos |\n",
     "| muestra/portal:panel | | API · Motor de pagos · Buzón |\n| Buzón | Recibe los avisos | muestra/portal:buzon | | |\n"),
    (DISENO, "\n\n## Datos\n", "\n\n**Flujo:** Tienda web → API\n\n## Datos\n")]
ROLES = {
    "componentes": {"Tienda web": "flujo", "API": "flujo", "Motor de pagos": "resto", "Panel interno": "resto",
                    "Buzón": "destino"},
    "entidades": {"cliente": "flujo", "pedido": "flujo", "producto": "flujo", "categoria": "resto"},
    "infraestructura": {"Servidor web": "flujo", "Base de datos": "destino", "Dominio": "flujo"},
}
# Para la leyenda: la misma, con la infraestructura sin conexiones (todo «resto»: un solo color)
CON_UN_COLOR = CON_ROLES + [(DISENO, "| Nube · producción | Base de datos |", "| Nube · producción | |"),
                            (DISENO, "| Registrador · producción | Servidor web |", "| Registrador · producción | |")]


def elementos(d, parte):
    return por_clave(saca(d, "diseno", parte), "nombre")


def sin_aviso_de_corto(d, problemas):
    malos = [t for t in avisos(d) if "En corto" in t]
    if malos:
        problemas.append(f"un aviso menciona «En corto»: {json.dumps(malos, ensure_ascii=False)}")


def escenarios(inf):
    # 1 · Una caja lleva su línea corta: cada fila de las tres secciones trae su «En corto» (vacía donde la celda lo está)
    problemas = []
    d = pestana(*generar(CON_CORTO), problemas)
    if d is not None:
        for parte, cortos in CORTO.items():
            vistas = elementos(d, parte)
            for nombre, corto in cortos.items():
                if nombre not in vistas:
                    problemas.append(f"falta «{nombre}» en {parte}")
                else:
                    igual(problemas, f"«en_corto» de «{nombre}» ({parte})", vistas[nombre].get("en_corto"), corto)
    inf.escenario("Una caja lleva su línea corta", problemas)

    # 2 · Sin la columna nada cambia: la muestra tal cual; cada elemento con en_corto "" y ningún aviso de «En corto»
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        for parte in PARTES:
            vistas = elementos(d, parte)
            if not vistas:
                problemas.append(f"no hay elementos en {parte}")
            for nombre, e in vistas.items():
                if "en_corto" not in e:
                    problemas.append(f"«{nombre}» ({parte}) no trae «en_corto» (tiene que ser \"\")")
                else:
                    igual(problemas, f"«en_corto» de «{nombre}» ({parte})", e["en_corto"], "")
        sin_aviso_de_corto(d, problemas)
    inf.escenario("Sin la columna nada cambia", problemas)

    # 3 · El color dice el rol: en «Componentes» hay de los tres (flujo, destino y resto) y el externo va con el resto.
    #     Añadido: lo mismo en «Datos» (la base es resto) y en la infraestructura, que no tiene «Flujo:»
    problemas = []
    d = pestana(*generar(CON_ROLES), problemas)
    if d is not None:
        for parte, roles in ROLES.items():
            vistas = elementos(d, parte)
            for nombre, rol in roles.items():
                igual(problemas, f"«rol» de «{nombre}» ({parte})", saca(vistas, nombre, "rol"), rol)
        distintos = {saca(elementos(d, "componentes"), n, "rol") for n in ROLES["componentes"]}
        if distintos != {"flujo", "destino", "resto"}:
            problemas.append(f"los roles de los componentes son {json.dumps(sorted(map(str, distintos)))}, no los tres")
    inf.escenario("El color dice el rol", problemas)

    # 4 · La leyenda nombra los roles: en cada dibujo con más de un rol, una entrada por rol con texto; con uno solo
    #     (la infraestructura sin conexiones, toda «resto»), vacía
    problemas = []
    d = pestana(*generar(CON_UN_COLOR), problemas)
    if d is not None:
        t = trazar(saca(d, "diseno"), problemas)
        if t is not None:
            for vista, cuantos in (("componentes", 3), ("datos", 2), ("infraestructura", 1)):
                v = dibujo(t, vista, problemas)
                if v is None:
                    continue
                roles = {c.get("rol") for c in v["cajas"] if isinstance(c, dict)}
                if len(roles) != cuantos:
                    problemas.append(f"las cajas de «{vista}» tienen {len(roles)} roles ({json.dumps(sorted(map(str, roles)))}), "
                                     f"y la muestra pide {cuantos}")
                ley = [x for x in v["leyenda"] if isinstance(x, dict)]
                if len(roles) <= 1:
                    if v["leyenda"]:
                        problemas.append(f"«{vista}» tiene un solo color y su leyenda no está vacía: "
                                         f"{json.dumps(v['leyenda'], ensure_ascii=False)}")
                    continue
                if sorted(str(x.get("rol")) for x in ley) != sorted(map(str, roles)) or len(ley) != len(v["leyenda"]):
                    problemas.append(f"la leyenda de «{vista}» es {json.dumps(v['leyenda'], ensure_ascii=False)}, y no trae "
                                     f"una entrada por cada rol del dibujo ({json.dumps(sorted(map(str, roles)))})")
                vacias = [x.get("rol") for x in ley if not isinstance(x.get("texto"), str) or not x["texto"].strip()]
                if vacias:
                    problemas.append(f"en la leyenda de «{vista}», no tienen texto los roles {json.dumps(vacias)}")
    inf.escenario("La leyenda nombra los roles", problemas)


flujo.principal("P19", escenarios)
