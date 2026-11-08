"""The minimum plugin version a root declares in guia.md (1.26): below it, a plugin reads but does not write.

Its own module, so only the scripts that gate writing carry it (abrir.py, cerrar.py, migrar_estructura.py,
aplicar_cambios.py, generar_vista.py; review of 1.26, finding on size). The English functions are the rule; the Spanish
names at the end are what the scripts use, as `compat` does.

The section is found tolerantly and read strictly, so that an error never opens the gate (review of 1.26): any heading
level, case, accents, bold or a colon after the title still declare it; its version is the first thing in the title
after the name or in its first paragraph, and anything else reads as unreadable, which closes writing. Two sections give
the highest version, and an unreadable one closes.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Optional

from .language import ES, Pack

__all__ = ["version_tuple", "minimum_plugin_version", "plugin_may_write", "STRUCTURE_MINIMUM",
           "VERSION_MINIMA_ESTRUCTURA", "RECETA_ACTUALIZAR", "puerta_de_escritura", "seccion_minima"]

# the minimum the current structure needs: what the migration writes, and what an opening calls «behind» (1.26: «Quién es
# quién»). Every structure change raises it with its migration
STRUCTURE_MINIMUM = "1.26.0"

_VERSION = re.compile(r"(?<![\d.])(\d+)\.(\d+)(?:\.(\d+))?(?!\.?\d)")
_LEADING = re.compile(r"^[\s*_`«\"(]*(?:v(?:ersi[oó]n)?\s*)?(\d+)\.(\d+)(?:\.(\d+))?(?!\.?\d)", re.I)


def version_tuple(text: str) -> Optional[tuple]:
    """«1.26» or «1.26.0» (the first version in `text`) as (1, 26, 0); None without one."""
    m = _VERSION.search(text or "")
    return (int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)) if m else None


def _key(t: str) -> str:
    t = "".join(c for c in unicodedata.normalize("NFD", t or "") if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9. ]", " ", t.lower())).strip()


def _leading(text: str) -> Optional[tuple]:
    m = _LEADING.match(text or "")
    return (int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)) if m else None


def minimum_plugin_version(guia: str, lang: Pack = ES) -> tuple[bool, Optional[tuple]]:
    """(declared, version) from the section «Versión mínima del plugin» of guia.md. (False, None): no such section,
    anyone may write. (True, None): a section whose version cannot be read, which nobody may write under until it is
    fixed. A heading counts as the section when it says «mínima» and «plugin» (any case, accents, level or bold)."""
    text = unicodedata.normalize("NFC", (guia or "").replace("\r\n", "\n").replace("\r", "\n"))
    name = _key(lang.minimum_plugin)
    words = [w for w in name.split() if len(w) > 3]
    heads = list(re.finditer(r"^[ \t]*#{1,6}[ \t]*(.*?)[ \t#]*$", text, re.M))
    found, versions = False, []
    for i, h in enumerate(heads):
        k = _key(h.group(1))
        if not (k.startswith(name) or all(w in k for w in words[-2:])):
            continue
        found = True
        body = text[h.end():heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        rest = k[len(name):] if k.startswith(name) else ""
        v = _leading(rest) if rest.strip() else None
        if v is None:
            first = next((b for b in re.split(r"\n\s*\n", body.strip()) if b.strip()), "")
            v = _leading(first)
        if v is None:
            return True, None
        versions.append(v)
    return (True, max(versions)) if found else (False, None)


def plugin_may_write(plugin_version: str, guia: str, lang: Pack = ES) -> tuple[str, Optional[tuple]]:
    """Whether a plugin may write in the root of this guia.md: ("ok", minimum or None), ("below", minimum),
    ("unreadable", None) for a section with no readable version, or ("unknown", minimum) for a plugin version that does
    not parse. Reading is never gated; only writing (decision of 2026-11-08)."""
    declared, minimum = minimum_plugin_version(guia, lang)
    if not declared:
        return "ok", None
    if minimum is None:
        return "unreadable", None
    mine = version_tuple(plugin_version)
    if mine is None:
        return "unknown", minimum
    return ("ok" if mine >= minimum else "below"), minimum


# ── las mismas reglas con los nombres de los scripts ─────────────────────────────────────────────────────────────

VERSION_MINIMA_ESTRUCTURA = STRUCTURE_MINIMUM
RECETA_ACTUALIZAR = ("en la app de Claude, Customize → Plugins, el botón Update del marketplace memoria-marketplace "
                     "(en Claude Code, /plugin marketplace update memoria-marketplace), o pide ayuda a quien administra la carpeta")


def seccion_minima(version: str = STRUCTURE_MINIMUM) -> str:
    """La sección que escribe la migración. Dice qué no hacer, porque un plugin anterior a la 1.26 solo la lee como regla."""
    return ("## Versión mínima del plugin\n"
            f"{version}. Con un plugin anterior, esta carpeta se lee y se consulta, pero no se escribe nada: no se cierra sesión, ni se "
            "registran decisiones, ni se crean o cambian documentos, ni se pone al día el tablero; primero se actualiza el plugin. "
            f"Para actualizar: {RECETA_ACTUALIZAR}.\n")


def puerta_de_escritura(version_plugin: str, guia: str) -> tuple:
    """(puede escribir, versión mínima como texto o None, motivo en llano o ""): la sección «Versión mínima del plugin»
    de guia.md frente a la versión del plugin que corre. El motivo es lo que se le dice a la persona."""
    estado, minima = plugin_may_write(version_plugin, guia)
    txt = ".".join(map(str, minima)) if minima else None
    if estado == "ok":
        return True, txt, ""
    if estado == "unreadable":
        return False, None, ("La sección «Versión mínima del plugin» de guia.md no dice qué versión: no se escribe nada en esta "
                             "carpeta hasta que su primer párrafo empiece por la versión (por ejemplo «1.26.0.»). La corrige el "
                             "responsable de contexto, en su sesión o a mano. Leer y consultar siguen funcionando.")
    if estado == "unknown":
        return False, txt, (f"No sé qué versión del plugin corre aquí («{version_plugin}») y esta carpeta pide la {txt} o una más "
                            "nueva para escribir: no se escribe nada. Leer y consultar siguen funcionando.")
    return False, txt, (f"Tu plugin memoria es la {version_plugin} y esta carpeta pide la {txt} o una más nueva para escribir: "
                        "puedes leer y consultar, pero no se escribe nada (ni sesiones, ni decisiones, ni documentos, ni el tablero) "
                        f"hasta que lo actualices: {RECETA_ACTUALIZAR}.")
