"""compat returns exactly what the scripts' own copies of «quién escribe» return, on the test root in its three forms
and on the cases of pruebas/sesion/probar_cuentas.py. The copy is the frozen 1.25.1 block in tests/reference/, since every script now takes it from the package."""
import pathlib, re, sys, unicodedata, unittest

CORE = pathlib.Path(__file__).resolve().parents[1]
REPO = CORE.parent.parent
sys.path[:0] = [str(CORE), str(REPO / "pruebas")]

from context_core import compat, parse  # noqa: E402
import comun  # noqa: E402

GEN = REPO / "plugins" / "memoria" / "skills" / "tablero" / "generar_vista.py"


REF = pathlib.Path(__file__).resolve().parent / "reference" / "quien_escribe_1_25_1.py"


def block():
    """The block as the scripts carried it in 1.25.1, frozen in tests/reference/."""
    ns = {"re": re, "unicodedata": unicodedata}
    exec(REF.read_text(encoding="utf-8"), ns)
    return ns


S = block()
GUIAS = {}
EXTRA = ("- Ana Prueba · ana@ejemplo.test\n- Ana Prueba · otra@ejemplo.test\n- Luis · baja 2026-01-01\n"
         "- Mar · sin cuenta · registra: Beto Prueba\n- x@ejemplo.test\n- Pepe · cosa rara\n- Sol · sin confirmar · sol@x.mx · también: Soledad\n")


def setUpModule():
    GUIAS["1.21"] = (comun.RAIZ / "guia.md").read_text(encoding="utf-8")
    GUIAS["1.22"] = (comun.raiz_migrada()[0] / "guia.md").read_text(encoding="utf-8")
    g125 = comun.raiz_125()[0]
    GUIAS["1.25"] = (g125 / "guia.md").read_text(encoding="utf-8")
    GUIAS["1.25 raro"] = GUIAS["1.25"] + EXTRA
    GUIAS["vacía"] = ""


class Compat(unittest.TestCase):
    def test_registry(self):
        for v, g in GUIAS.items():
            with self.subTest(form=v):
                self.assertEqual(dict(compat.registro_personas(g)), S["registro_personas"](g))

    def test_rows_context_and_lookups(self):
        for v, g in GUIAS.items():
            new, old = compat.registro_personas(g), S["registro_personas"](g)
            header, rows = parse._table_rows(parse.section(g, "Áreas"))
            for cells in rows:
                with self.subTest(form=v, row=cells[0]):
                    self.assertEqual(compat.fila_cuentas(header, cells, new), S["fila_cuentas"](header, cells, old))
                    self.assertEqual(compat.columnas_personas(header), S["columnas_personas"](header))
            for line in ("Contexto común: Ana Prueba", "Contexto común: Ana Prueba (ana@ejemplo.test)", "Contexto común: Nadie, nunca"):
                self.assertEqual(compat.cuentas_contexto(line, new), S["cuentas_contexto"](line, old))
                self.assertEqual(compat.nombre_contexto(line), S["nombre_contexto"](line))
            for n in ("Ana Prueba", "ana@ejemplo.test", "Soledad", "Beto Prueba", "x@ejemplo.test", "Nadie"):
                self.assertEqual(compat.persona(n, new), S["persona"](n, old), n)
                self.assertEqual(compat.nombre_de(n, new), S["nombre_de"](n, old), n)

    def test_collaborators(self):
        quien = ["Responsable: Ana Prueba\nColabora: Carla Prueba, Eva Prueba",
                 "Dueño: Ana\nColabora: Dani (dani@x.com)\n- **Colabora:** Eva (eva@x.com)\nColabora : Fer (fer@x.com)\nConsumen esto: Luis (luis@x.com)",
                 "Colabora: Beto Prueba y Nuevo Nombre (nuevo@x.mx)", ""]
        for v, g in GUIAS.items():
            new, old = compat.registro_personas(g), S["registro_personas"](g)
            for q in quien:
                with self.subTest(form=v, quien=q[:30]):
                    self.assertEqual(compat.colaboran_en(q, new if new["hay"] else None), S["colaboran_en"](q, old if old["hay"] else None))
                    self.assertEqual(compat.altas_provisionales(q, new), S["altas_provisionales"](q, old))
                    self.assertEqual(compat.nombres_de(q, new), S["nombres_de"](q, old))

    def test_account_cells(self):
        for c in ["ana@x.mx", "ana@x.mx · colabora: beto@x.mx, carla@x.mx", "ana@x.mx, beto@x.mx", "", "Sin cuenta de Claude",
                  "ana@x.mx colaboradora: beto@x.mx", "ana@x.mx · colabora beto@x.mx", "ANA@X.MX · Colabora: Beto@X.mx",
                  "ana@x.mx · co-labora: b@x.mx", "o'brien@x.com", "ana@empresa"]:
            self.assertEqual(compat.cuentas(c), S["cuentas"](c), c)


if __name__ == "__main__":
    unittest.main()
