#!/usr/bin/env python3
"""P18 · Infrastructure by provider and account (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-23, en el plan).

- One container per provider and account. Dado two rows of «Infraestructura» with the same Proveedor and Cuenta, Cuando
  the infrastructure opens, Entonces both are drawn inside one container labelled with the provider, the account and the
  environment.
- The old column still draws. Dado a design with the old «Dónde» column, Cuando the infrastructure opens, Entonces it is
  drawn one box per row and the tab says how to split it.
- An external service has its own container. Dado a row whose provider is the customer's, such as its Drive, Cuando the
  infrastructure opens, Entonces it is drawn in a container of its own.

Por la entrada de F2: el generador del tablero sobre la raíz de muestra de P05_lectores.py, y lo que escribe en
desarrollo/ventas--portal.json: diseno.infraestructura[] con proveedor, cuenta y ambiente, y
diseno.infraestructura_contenedores (o null con la columna «Dónde»). El dibujo de los contenedores y su etiqueta queda
para la verificación: lo dice RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P18_infraestructura_por_cuenta.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P05_lectores import *  # noqa: E402,F401,F403  (la muestra, cómo se corre el generador y lo que dice la muestra: una sola copia)

TABLA_VIEJA = """| Pieza | Para qué | Dónde | Conecta con |
|---|---|---|---|
| Servidor web | Sirve la tienda y la API | Nube · producción | Base de datos |
| Base de datos | Guarda clientes, pedidos y productos | Nube · producción | |
| Dominio | La dirección de la tienda | Registrador · producción | Servidor web |
"""
CABECERA = "| Pieza | Para qué | Proveedor | Cuenta | Ambiente | Conecta con |\n|---|---|---|---|---|---|\n"
FILAS = {   # nombre: (fila, proveedor, cuenta, ambiente)
    "Servidor web": ("| Servidor web | Sirve la tienda y la API | Nube | tienda-prod | producción | Base de datos |\n",
                     "Nube", "tienda-prod", "producción"),
    "Base de datos": ("| Base de datos | Guarda clientes, pedidos y productos | Nube | tienda-prod | producción | |\n",
                      "Nube", "tienda-prod", "producción"),
    "Dominio": ("| Dominio | La dirección de la tienda | Registrador | cuenta-tienda | producción | Servidor web |\n",
                "Registrador", "cuenta-tienda", "producción"),
    "Carpeta de comprobantes": ("| Carpeta de comprobantes | Guarda los comprobantes de pago | Google Drive | Drive de la tienda "
                                "(del cliente) | producción | |\n", "Google Drive", "Drive de la tienda (del cliente)",
                                "producción"),
}


def tabla_nueva(orden):
    """El cambio que pone la tabla de «Infraestructura» con Proveedor, Cuenta y Ambiente, con esas filas en ese orden."""
    return (DISENO, TABLA_VIEJA, CABECERA + "".join(FILAS[n][0] for n in orden))


def contenedores(d, problemas):
    """diseno.infraestructura_contenedores, con solo las cuatro claves del contrato, o None con el porqué."""
    cs = saca(d, "diseno", "infraestructura_contenedores")
    if not isinstance(cs, list) or not all(isinstance(c, dict) for c in cs):
        problemas.append(f"«infraestructura_contenedores» es {json.dumps(cs, ensure_ascii=False)}, no una lista de contenedores")
        return None
    return [{k: c.get(k) for k in ("proveedor", "cuenta", "ambiente", "piezas")} for c in cs]


def piezas(d, problemas, orden, conecta):
    """Cada fila es una pieza con su proveedor, cuenta, ambiente y lo que conecta."""
    vistas = por_clave(saca(d, "diseno", "infraestructura"), "nombre")
    igual(problemas, "las piezas de infraestructura", sorted(vistas), sorted(orden))
    for n in orden:
        _, prov, cuenta, amb = FILAS[n]
        for campo, esperado in (("proveedor", prov), ("cuenta", cuenta), ("ambiente", amb), ("conecta_con", conecta[n])):
            igual(problemas, f"«{campo}» de «{n}»", saca(vistas, n, campo), esperado)


def escenarios(inf):
    # 1 · Un contenedor por proveedor y cuenta: «Servidor web» y «Base de datos» comparten Nube y tienda-prod
    problemas = []
    orden = ["Servidor web", "Base de datos", "Dominio"]
    d = pestana(*generar([tabla_nueva(orden)]), problemas)
    if d is not None:
        piezas(d, problemas, orden, INFRAESTRUCTURA)
        cs = contenedores(d, problemas)
        if cs is not None:
            igual(problemas, "los contenedores", cs,
                  [{"proveedor": "Nube", "cuenta": "tienda-prod", "ambiente": "producción", "piezas": ["Servidor web", "Base de datos"]},
                   {"proveedor": "Registrador", "cuenta": "cuenta-tienda", "ambiente": "producción", "piezas": ["Dominio"]}])
        malos = [t for t in avisos(d, "infraestructura") if "Proveedor" in t]
        if malos:
            problemas.append(f"con la tabla nueva, un aviso pide separar por proveedor: {json.dumps(malos, ensure_ascii=False)}")
    inf.escenario("Un contenedor por proveedor y cuenta", problemas)

    # 2 · La columna vieja se sigue dibujando: la muestra tal cual, con «Dónde»
    problemas = []
    d = pestana(*generar(), problemas)
    if d is not None:
        vistas = por_clave(saca(d, "diseno", "infraestructura"), "nombre")
        igual(problemas, "las cajas de infraestructura", sorted(vistas), sorted(INFRAESTRUCTURA))
        for nombre, conecta in INFRAESTRUCTURA.items():
            igual(problemas, f"«Conecta con» de «{nombre}»", saca(vistas, nombre, "conecta_con"), conecta)
        dis = saca(d, "diseno")
        if not isinstance(dis, dict) or "infraestructura_contenedores" not in dis:
            problemas.append("«diseno» no trae «infraestructura_contenedores» (tiene que ser null con la columna «Dónde»)")
        elif dis["infraestructura_contenedores"] is not None:
            problemas.append(f"con la columna «Dónde», «infraestructura_contenedores» es "
                             f"{json.dumps(dis['infraestructura_contenedores'], ensure_ascii=False)}, no null")
        if not any("Proveedor" in t for t in avisos(d, "infraestructura")):
            problemas.append(f"ningún aviso de la parte «infraestructura» dice cómo separarla («Proveedor»): "
                             f"avisos = {json.dumps(saca(d, 'avisos'), ensure_ascii=False)}")
    inf.escenario("La columna vieja se sigue dibujando", problemas)

    # 3 · Un servicio externo tiene su propio contenedor: «Carpeta de comprobantes» en el Drive del cliente, puesta
    #     entre las dos filas de Nube
    problemas = []
    orden = ["Servidor web", "Carpeta de comprobantes", "Base de datos", "Dominio"]
    conecta = dict(INFRAESTRUCTURA, **{"Carpeta de comprobantes": []})
    d = pestana(*generar([tabla_nueva(orden)]), problemas)
    if d is not None:
        piezas(d, problemas, orden, conecta)
        cs = contenedores(d, problemas)
        if cs is not None:
            igual(problemas, "los contenedores", cs,
                  [{"proveedor": "Nube", "cuenta": "tienda-prod", "ambiente": "producción", "piezas": ["Servidor web", "Base de datos"]},
                   {"proveedor": "Google Drive", "cuenta": "Drive de la tienda (del cliente)", "ambiente": "producción",
                    "piezas": ["Carpeta de comprobantes"]},
                   {"proveedor": "Registrador", "cuenta": "cuenta-tienda", "ambiente": "producción", "piezas": ["Dominio"]}])
    inf.escenario("Un servicio externo tiene su propio contenedor", problemas)


flujo.principal("P18", escenarios)
