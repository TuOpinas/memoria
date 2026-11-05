"""The scripts' Spanish names over the package, with the shapes they use today (dicts and tuples).

The plugin scripts keep their Spanish until the language packs (decision of 2026-11-04). While each one moves onto the
package, it imports these names in place of its own copy of the code, and nothing else in the script changes. A script
that has moved no longer carries the copy; `packages/context-core/tests/test_compat.py` checks these return exactly what the copies do.
"""
from __future__ import annotations

import pathlib
import re
from typing import Optional

from . import parse
from .records import PeopleRegistry, Person

__all__ = ["SOBRE_LA_CARPETA", "sin_carpeta", "ARCHIVADO", "archivados_de", "con_archivados", "respuestas_viejas",
           "restringida_celda", "CORREO", "PALABRA_COLABORA", "LINEA_COLABORA", "cuentas", "clave_nombre", "_titulo", "registro_personas",
           "persona", "nombres_de", "cuentas_de_nombres", "altas_provisionales", "columnas_personas", "fila_cuentas",
           "nombre_contexto", "cuentas_contexto", "nombre_de", "colaboran_en"]

CORREO = parse.EMAIL
PALABRA_COLABORA = parse._WORD_COLLABORATES
LINEA_COLABORA = parse._LINE_COLLABORATES

cuentas = parse.account_cell
clave_nombre = parse.name_key
_titulo = parse.heading_key
nombre_contexto = parse.context_owner_name


def _persona(p: Person) -> dict:
    return {"nombre": p.name, "cuentas": p.accounts, "drive": p.drive_accounts, "sin_cuenta": p.no_account,
            "sin_confirmar": p.unconfirmed, "alias": p.aliases, "de": p.organization, "baja": p.left_on,
            "compartida": p.shared_with, "registra": p.registered_by}


class _Registro(dict):
    """registro_personas()'s dict, carrying the PeopleRegistry it was made from."""
    registry: PeopleRegistry


def _registro(reg: PeopleRegistry) -> _Registro:
    dicts = {id(p): _persona(p) for p in reg.people}
    r = _Registro(hay=reg.declared, personas=[dicts[id(p)] for p in reg.people],
                  nombre={k: dicts[id(p)] for k, p in reg.by_name.items()},
                  cuenta={k: dicts[id(p)] for k, p in reg.by_account.items()}, avisos=reg.warnings)
    r.registry = reg
    return r


def _reg(reg) -> PeopleRegistry:
    """Accepts what the scripts pass: the dict from registro_personas(), None or {}."""
    return getattr(reg, "registry", None) or PeopleRegistry()


def registro_personas(guia: str) -> dict:
    return _registro(parse.people_registry(guia))


def persona(nombre: str, reg) -> Optional[dict]:
    """The person with that name, alias or account; None if missing or ambiguous."""
    t = (nombre or "").strip()
    if CORREO.fullmatch(t.lower()):
        return (reg or {}).get("cuenta", {}).get(t.lower())
    return (reg or {}).get("nombre", {}).get(clave_nombre(t))


def nombres_de(texto: str, reg=None) -> list[str]:
    return parse.names_in(texto, _reg(reg))


def cuentas_de_nombres(texto: str, reg) -> tuple[set, list]:
    return parse.accounts_of_names(texto, _reg(reg))


def altas_provisionales(quien: str, reg) -> list:
    return parse.provisional_people(quien, _reg(reg))


def columnas_personas(cab: list) -> dict:
    c = parse._people_columns(cab)
    return {"responsable": c["responsible"], "cuenta": c["account"], "colabora": c["collaborates"]}


def fila_cuentas(cab: list, celdas: list, reg) -> tuple:
    return parse.row_accounts(cab, celdas, _reg(reg))


def cuentas_contexto(linea: str, reg) -> set:
    return parse.context_owner_accounts(linea, _reg(reg))


def nombre_de(cuenta: str, reg) -> str:
    return parse.name_of_account(cuenta, _reg(reg))


def colaboran_en(quien: str, reg=None) -> set:
    return parse.collaborator_accounts(quien, _reg(reg) if reg else None)


# ── el primer párrafo de guia.md, los registros con sus archivados y la regla de lo restringido ──────────────────────

SOBRE_LA_CARPETA = parse.ABOUT_THE_FOLDER
sin_carpeta = parse.drop_folder_talk
ARCHIVADO = parse.ARCHIVED
restringida_celda = parse.is_restricted_cell


def _nombres(carpeta) -> list:
    try:
        return [x.name for x in pathlib.Path(carpeta).iterdir()]
    except OSError:
        return []


def archivados_de(carpeta, nombre, anio) -> list:
    return parse.archived_names(_nombres(carpeta), nombre, anio)


def con_archivados(carpeta, nombre, vivo, anio, leer_) -> tuple:
    return parse.with_archives(vivo, [leer_(pathlib.Path(carpeta) / n) for n in archivados_de(carpeta, nombre, anio)])


def respuestas_viejas(carpeta, anio, leer_) -> list:
    """The «Responde a:» lines of decision archives older than last year, which are not read whole."""
    recientes = set(archivados_de(carpeta, "decisiones", anio))
    out = []
    for n in archivados_de(carpeta, "decisiones", 0):
        if n not in recientes:
            out += re.findall(r"^Responde a:[ \t]*(.+)$", leer_(pathlib.Path(carpeta) / n) or "", re.M)
    return out
