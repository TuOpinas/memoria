"""Frozen reference: whether a row of the area table of guia.md is restricted, as the 1.25.1 scripts decided it, before
they took the rule from context_core (review of 1.25.2, finding 10). abrir.py's reading is the reference: it is the
strictest, and where another copy disagreed, abrir.py read the area restricted. The board's and the migration's 1.25.1
copies are kept too, to show where they differed. The functions are copied as the scripts carried them at the 1.25.2
tag (whose outputs the review of 1.25.2 found identical to 1.25.1's, with this divergence already there); the board's and
the migration's are cut down to the lines that decide restricted. `columnas_personas` and `restringida_celda` come from
the other two files of this folder. Kept only for the tests; never imported by the plugin or the server; do not edit."""
import re


# --- abrir.py (1.25.1): columnas_areas() and area_restringida(); cab_areas is the header row, a global of the script ---
def columnas_areas(cab):
    """Dónde está cada columna de la tabla de áreas, por su encabezado: la 1.22 dice «Responsable» y añade «Acceso»;
    hasta la 1.21, «Dueño» y sin «Acceso». Sin encabezado reconocible, las posiciones de siempre."""
    n = [re.sub(r"[*_`]", "", x).strip().lower() for x in cab]
    def pos(*nombres, defecto=None):
        return next((i for i, x in enumerate(n) if x in nombres), defecto)
    return {"responsable": pos("responsable", "dueño", "dueno", defecto=2), "cuenta": pos("cuenta", "colabora", defecto=3),
            "lectores": pos("quién la lee", "quien la lee", defecto=4), "acceso": pos("acceso")}


def area_restringida(c, col):
    """Con columna «Acceso» (1.22), restringida si dice «Restringida» y abierta si dice «Abierta»; con otra cosa o vacía,
    y sin la columna, la regla de «Quién la lee» de la 1.21: nunca se falla abierto."""
    if col["acceso"] is not None and col["acceso"] < len(c):
        v = c[col["acceso"]]
        if re.match(r"^[\W_]*restringid[oa]s?\b", v, re.I):
            return True
        if re.match(r"^[\W_]*abiert[oa]s?\b", v, re.I):
            return False
    if cab_areas is not None and columnas_personas(cab_areas)["colabora"] is not None:
        return True   # 1.25: «Quién la lee» ya no lleva «Restringida:», así que un «Acceso» vacío o mal escrito falla cerrado
    return restringida_celda(c[col["lectores"]] if col["lectores"] < len(c) else "")


def abrir(cab, c):
    """The reference reading: abrir.py's, for one header and one row."""
    globals()["cab_areas"] = cab
    return area_restringida(c, columnas_areas(cab))


# --- generar_vista.py (1.25.1): the board; RE_RESTRINGIDA lacks «s?», so «Restringidas» in «Acceso» read open ---
RE_RESTRINGIDA = re.compile(r"^[\W_]*restringid[oa]\b", re.I)


def tablero(celdas, cab_guia):
    n_ = [re.sub(r"[*_`]", "", x).strip().lower() for x in cab_guia]
    pos = lambda *ns, d=None: next((i for i, x in enumerate(n_) if x in ns), d)
    col = {"resp": pos("responsable", "dueño", "dueno", d=2), "cuenta": pos("cuenta", "colabora", d=3), "lee": pos("quién la lee", "quien la lee", d=4), "acceso": pos("acceso")}
    lect = celdas[col["lee"]]
    acceso_vale = col["acceso"] is not None and bool(re.match(r"^[\W_]*(restringid|abiert)[oa]s?\b", celdas[col["acceso"]], re.I))
    if acceso_vale:
        restr = bool(RE_RESTRINGIDA.match(celdas[col["acceso"]]))
    return restr if acceso_vale else (True if columnas_personas(cab_guia)["colabora"] is not None else restringida_celda(lect))


# --- migrar_estructura.py (1.25.1): without the «Colabora» fail-closed step ---
def migrar(c, cab):
    n_ = [re.sub(r"[*_`]", "", x).strip().lower() for x in cab]
    pos = lambda *ns: next((i for i, x in enumerate(n_) if x in ns), None)
    cc = {"lee": pos("quién la lee", "quien la lee"), "acc": pos("acceso")}
    lee_, acc_ = cc["lee"] if cc["lee"] is not None else 4, cc["acc"]
    v_acc = c[acc_] if acc_ is not None and acc_ < len(c) else ""
    return (True if re.match(r"^[\W_]*restringid[oa]s?\b", v_acc, re.I) else False if re.match(r"^[\W_]*abiert[oa]s?\b", v_acc, re.I)
            else restringida_celda(c[lee_] if lee_ < len(c) else ""))


# --- the reference cases: (header, row, restricted as abrir.py read it in 1.25.1) ---
H121 = ["Área", "Qué es", "Dueño", "Cuenta", "Quién la lee"]
H122 = ["Área", "Qué es", "Responsable", "Cuenta", "Quién la lee", "Acceso"]
H125 = ["Área", "Qué es", "Responsable", "Colabora", "Quién la lee", "Acceso"]
H125_SIN_ACCESO = ["Área", "Qué es", "Responsable", "Colabora", "Quién la lee"]
CASOS = [
    # 1.21: «Quién la lee» decides
    (H121, ["a", "", "Ana", "a@x.mx", "Todo el equipo"], False),
    (H121, ["a", "", "Ana", "a@x.mx", "Restringida: dirección"], True),
    (H121, ["a", "", "Ana", "a@x.mx", "Dirección (restringida)"], True),
    (H121, ["a", "", "Ana", "a@x.mx", "Abierta (antes restringida)"], False),
    (H121, ["a", "", "Ana", "a@x.mx", "Todo el equipo; los proyectos restringidos aparte"], False),
    # 1.22: «Acceso» decides when it says Abierta or Restringida, in any gender and number
    (H122, ["a", "", "Ana", "a@x.mx", "Todo el equipo", "Abierta"], False),
    (H122, ["a", "", "Ana", "a@x.mx", "Todo el equipo", "Abiertas"], False),
    (H122, ["a", "", "Ana", "a@x.mx", "Dirección", "Restringida"], True),
    (H122, ["a", "", "Ana", "a@x.mx", "Dirección", "Restringidas"], True),    # the board read it open (finding 10)
    (H122, ["a", "", "Ana", "a@x.mx", "Dirección", "Restringidos"], True),    # the board read it open
    (H122, ["a", "", "Ana", "a@x.mx", "Dirección", "**Restringido**"], True),
    (H122, ["a", "", "Ana", "a@x.mx", "Restringida: dirección", "Abierta"], False),
    # 1.22, «Acceso» empty or unclear: the «Quién la lee» rule
    (H122, ["a", "", "Ana", "a@x.mx", "Todo el equipo", ""], False),
    (H122, ["a", "", "Ana", "a@x.mx", "Restringida: dirección", ""], True),
    (H122, ["a", "", "Ana", "a@x.mx", "Todo el equipo", "Restr."], False),
    (H122, ["a", "", "Ana", "a@x.mx", "Restringida: dirección", "Cerrada"], True),
    # 1.25 («Colabora»): «Acceso» decides; empty or unclear fails closed
    (H125, ["a", "", "Ana", "Beto", "Todo el equipo", "Abierta"], False),
    (H125, ["a", "", "Ana", "Beto", "Beto", "Restringida"], True),
    (H125, ["a", "", "Ana", "Beto", "Beto", "Restringidas"], True),           # the board read it open
    (H125, ["a", "", "Ana", "Beto", "Todo el equipo", ""], True),             # the migration read it open
    (H125, ["a", "", "Ana", "Beto", "Todo el equipo", "Restr."], True),       # the migration read it open
    (H125, ["a", "", "Ana", "Beto", "Todo el equipo", "Cerrada"], True),      # the migration read it open
    (H125_SIN_ACCESO, ["a", "", "Ana", "Beto", "Todo el equipo"], True),      # the migration read it open
    # a row shorter than the header: what is missing reads as empty
    (H122, ["a", "", "Ana", "a@x.mx", "Restringida: dirección"], True),
    (H125, ["a", "", "Ana", "Beto"], True),
]
