"""Whether an area is restricted: one rule in context_core (rules.area_is_restricted, compat.area_restringida) for the
opening, the board, the permissions check, the migration and verificar.sh, and it is abrir.py's 1.25.1 reading, frozen
with its cases in tests/reference/acceso_1_25_1.py (review of 1.25.2, finding 10). Where the board's or the migration's
1.25.1 copy disagreed, abrir.py read the area restricted: aligning everyone on it only ever closes an area."""
import itertools, pathlib, re, sys, unicodedata, unittest

CORE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CORE))

from context_core import compat, parse, rules  # noqa: E402

REFS = pathlib.Path(__file__).resolve().parent / "reference"


def frozen():
    ns = {"re": re, "unicodedata": unicodedata}
    for f in ("quien_escribe_1_25_1.py", "reglas_1_25_1.py", "acceso_1_25_1.py"):
        exec((REFS / f).read_text(encoding="utf-8"), ns)
    return ns


R = frozen()
HEADERS = [R["H121"], R["H122"], R["H125"], R["H125_SIN_ACCESO"], ["a", "b", "c", "d", "e"],
           ["Área", "Qué es", "Responsable", "Cuenta", "Acceso", "Quién la lee"]]
ACCESS = ["Abierta", "abiertas", "Abierto", "Restringida", "Restringidas", "restringidos", "**Restringido**", "«Restringida»",
          "", "Restr.", "Cerrada", "Restringidísima", "Abiertamente", "Restringida: Ana"]
READERS = ["Todo el equipo", "Restringida: dirección", "Dirección (restringida)", "nunca restringida", "Restringidas a Beto",
           "Todo el equipo; los proyectos restringidos aparte", ""]


def rows(header):
    for acc, rd in itertools.product(ACCESS, READERS):
        cells = ["a", "", "Ana", "Beto"] + [""] * (len(header) - 4)
        for name, value in (("quién la lee", rd), ("acceso", acc)):
            i = next((i for i, x in enumerate(header) if x.lower() == name), None)
            if i is not None:
                cells[i] = value
            elif name == "quién la lee" and len(cells) > 4:
                cells[4] = value
        yield cells


class Access(unittest.TestCase):
    def test_reference_cases(self):
        for header, cells, expected in R["CASOS"]:
            with self.subTest(header=header[3:], row=cells[3:]):
                self.assertEqual(R["abrir"](header, cells), expected)
                self.assertEqual(rules.area_is_restricted(cells, header), expected)
                self.assertEqual(compat.area_restringida(cells, header), expected)

    def test_restringidas(self):
        """«Acceso: Restringidas»: abrir.py read it closed and the 1.25.1 board open; now everyone reads it closed."""
        for header in (R["H122"], R["H125"]):
            cells = ["a", "", "Ana", "Beto", "Todo el equipo", "Restringidas"]
            self.assertFalse(R["tablero"](cells, header))
            self.assertTrue(R["abrir"](header, cells))
            self.assertTrue(compat.area_restringida(cells, header))
            self.assertTrue(compat.acceso_de("Restringidas"))

    def test_same_as_abrir_everywhere(self):
        for header in HEADERS:
            for cells in rows(header):
                for short in (cells, cells[:4]):
                    with self.subTest(header=header, row=short):
                        self.assertEqual(rules.area_is_restricted(short, header), R["abrir"](header, short))

    def test_other_copies_only_close(self):
        """Wherever the board's or the migration's 1.25.1 copy differed from abrir.py, abrir.py said restricted."""
        differ = 0
        for header in HEADERS:
            for cells in rows(header):
                ref = R["abrir"](header, cells)
                for other in (R["tablero"](cells, header), R["migrar"](cells, header)):
                    if other != ref:
                        differ += 1
                        self.assertTrue(ref, (header, cells))
        self.assertGreater(differ, 0)

    def test_access_word(self):
        for v in ACCESS:
            with self.subTest(value=v):
                word = (True if re.match(r"^[\W_]*restringid[oa]s?\b", v, re.I) else False
                        if re.match(r"^[\W_]*abiert[oa]s?\b", v, re.I) else None)
                self.assertEqual(compat.acceso_de(v), word)
                self.assertEqual(parse.access_word(v), word)


if __name__ == "__main__":
    unittest.main()
