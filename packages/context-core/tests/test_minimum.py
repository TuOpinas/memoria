"""The minimum plugin version a root declares in guia.md (1.26): below it a plugin reads but does not write. A section
with no version closes the gate instead of opening it, so a typo never lets an old plugin write."""
import dataclasses, pathlib, sys, unittest

CORE = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CORE)]

from context_core import compat, language, rules  # noqa: E402

GUIA = "# Org\n\nTexto.\n\n## Versión mínima del plugin\n{}\n\n## Áreas\n\n| Área |\n|---|\n"


class Version(unittest.TestCase):
    def test_parses(self):
        self.assertEqual(rules.version_tuple("1.26.0."), (1, 26, 0))
        self.assertEqual(rules.version_tuple("la 1.26 o más nueva"), (1, 26, 0))
        self.assertEqual(rules.version_tuple("1.25.10"), (1, 25, 10))
        self.assertIsNone(rules.version_tuple("la nueva"))

    def test_numeric_not_text(self):
        self.assertEqual(rules.plugin_may_write("1.26.10", GUIA.format("1.26.9."))[0], "ok")
        self.assertEqual(rules.plugin_may_write("1.26.9", GUIA.format("1.26.10."))[0], "below")


class Gate(unittest.TestCase):
    def test_no_section_anyone_writes(self):
        self.assertEqual(rules.plugin_may_write("1.19.0", "# Org\n\n## Áreas\n"), ("ok", None))

    def test_below_equal_above(self):
        g = GUIA.format("1.26.0. Con un plugin anterior, esta carpeta se lee pero no se escribe.")
        self.assertEqual(rules.plugin_may_write("1.25.8", g), ("below", (1, 26, 0)))
        self.assertEqual(rules.plugin_may_write("1.26.0", g), ("ok", (1, 26, 0)))
        self.assertEqual(rules.plugin_may_write("1.27.1", g), ("ok", (1, 26, 0)))

    def test_section_without_version_closes(self):
        self.assertEqual(rules.plugin_may_write("9.0.0", GUIA.format("La que diga el administrador.")), ("unreadable", None))

    def test_only_the_first_paragraph_counts(self):
        g = GUIA.format("Sin número aquí.\n\nLa receta menciona la 1.24 de paso.")
        self.assertEqual(rules.plugin_may_write("1.30.0", g)[0], "unreadable")

    def test_a_version_elsewhere_in_guia_does_not_count(self):
        g = "# Org\n\n## Versión del método\n1.99.0\n\n## Áreas\n"
        self.assertEqual(rules.plugin_may_write("1.0.0", g), ("ok", None))

    def test_unknown_plugin_version_closes(self):
        self.assertEqual(rules.plugin_may_write("", GUIA.format("1.26.0"))[0], "unknown")

    def test_section_name_from_the_language_pack(self):
        other = dataclasses.replace(language.ES, minimum_plugin="Minimum plugin version")
        g = "# Org\n\n## Minimum plugin version\n1.26.0\n"
        self.assertEqual(rules.plugin_may_write("1.25.0", g, other)[0], "below")
        self.assertEqual(rules.plugin_may_write("1.25.0", g)[0], "ok")


class Compat(unittest.TestCase):
    def test_reason_in_plain_words(self):
        puede, minima, motivo = compat.puerta_de_escritura("1.25.8", GUIA.format("1.26.0."))
        self.assertFalse(puede)
        self.assertEqual(minima, "1.26.0")
        self.assertIn("1.25.8", motivo)
        self.assertIn("Customize → Plugins", motivo)
        self.assertEqual(compat.puerta_de_escritura("1.26.0", GUIA.format("1.26.0.")), (True, "1.26.0", ""))


if __name__ == "__main__":
    unittest.main()
