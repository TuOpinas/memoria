"""The maintenance trace (1.26.8): which entries of sesiones.md are sessions, and what a maintenance entry discounts."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from context_core import rules  # noqa: E402

FIX = ("2026-11-17 (mantenimiento)",
       "## 2026-11-17 (mantenimiento)\nTema: arreglos del mantenimiento de la carpeta.\n"
       "Arregló: taller/a.md (cabecera), entregables/b.md (antes entregables/B, viejo.md)\n"
       "Último cierre: 2026-11-17T18:44:27-06:00\nEscrita: 2026-11-17T19:00:00-06:00\n"
       "Sesión de: mantenimiento de Ana Ruiz · plugin 1.26.8")
SES = ("2026-11-16", "## 2026-11-16\nTema: algo.\nSesión de: Ana Ruiz · plugin 1.26.8")
TASK = ("2026-11-18 (tarea)", "## 2026-11-18 (tarea)\nTema: x.")
CLOSE, WRITTEN = 1794962667.0, 1794963600.0


class TestNonSession(unittest.TestCase):
    def test_kinds(self):
        for h in ("2026-11-17 (tarea)", "2026-11-17 (Tablero)", "## 2026-11-17 (migracion)", "2026-11-17 (mantenimiento)"):
            self.assertFalse(rules.is_session(h), h)
        self.assertTrue(rules.is_session("2026-11-17"))
        self.assertTrue(rules.is_session("2026-11-17 · mantenimiento de la casa"))
        self.assertTrue(rules.is_maintenance("2026-11-17 (mantenimiento)"))
        self.assertFalse(rules.is_maintenance("2026-11-17 (tarea)"))

    def test_finished(self):
        self.assertTrue(rules.project_finished("## Estado actual\nProyecto terminado el 2026-10-30. Firmado.\n"))
        self.assertTrue(rules.project_finished("# x\n## Estatus\nProyecto terminado el 2026-10-30.\n## Objetivo\ny"))
        self.assertFalse(rules.project_finished("## Objetivo\nProyecto terminado el 2026-10-30 no es esto.\n"))


class TestTrace(unittest.TestCase):
    def test_files(self):
        self.assertEqual(rules.maintenance_files(FIX[1]), ["taller/a.md", "entregables/b.md"])

    def test_top_maintenance(self):
        ref, disc = rules.maintenance_trace([FIX, SES], 2e9)
        self.assertAlmostEqual(ref, CLOSE)
        self.assertEqual(set(disc), {"taller/a.md", "entregables/b.md"})
        self.assertAlmostEqual(disc["taller/a.md"], WRITTEN + 60)
        self.assertTrue(rules.discounted_file("taller/a.md", WRITTEN, disc))
        self.assertFalse(rules.discounted_file("taller/a.md", WRITTEN + 120, disc), "changed after its entry: someone's work")
        self.assertFalse(rules.discounted_file("taller/c.md", 1.0, disc))

    def test_each_file_has_its_own_bound(self):
        later = (FIX[0], FIX[1].replace("taller/a.md", "taller/c.md").replace("Escrita: 2026-11-17T19:00:00", "Escrita: 2026-11-17T21:00:00"))
        ref, disc = rules.maintenance_trace([later, FIX, SES], 2e9)
        self.assertAlmostEqual(disc["taller/a.md"], WRITTEN + 60, msg="a second fix does not extend the first one's files")
        self.assertAlmostEqual(disc["taller/c.md"], WRITTEN + 7200 + 60)

    def test_a_task_on_top_keeps_the_trace(self):
        ref, disc = rules.maintenance_trace([TASK, FIX, SES], 2e9)
        self.assertAlmostEqual(ref, CLOSE)
        self.assertIn("taller/a.md", disc)

    def test_session_on_top(self):
        self.assertEqual(rules.maintenance_trace([SES, FIX], 123.0), (123.0, {}))
        self.assertEqual(rules.maintenance_trace([TASK, SES], 123.0), (123.0, {}))

    def test_paths_compare_normalised(self):
        import unicodedata
        nfd = unicodedata.normalize("NFD", "taller/económica.md")
        e = (FIX[0], FIX[1].replace("taller/a.md", "taller/Económica.md"))
        _, disc = rules.maintenance_trace([e], 2e9)
        self.assertTrue(rules.discounted_file(nfd, WRITTEN, disc))

    def test_none_and_unreadable(self):
        self.assertIsNone(rules.maintenance_trace([(FIX[0], FIX[1].replace("2026-11-17T18:44:27-06:00", "ninguno"))], 9.0)[0])
        self.assertEqual(rules.maintenance_trace([(FIX[0], FIX[1].replace("2026-11-17T18:44:27-06:00", "ayer"))], 9.0)[0], 9.0)
        self.assertEqual(rules.maintenance_trace([(FIX[0], FIX[1].replace("2026-11-17T18:44:27-06:00", "2026-11-17T18:44:27"))], 9.0)[0], 9.0,
                         "without an offset it does not read")
        self.assertEqual(rules.maintenance_trace([(FIX[0], "## x\nTema: y")], 9.0)[0], 9.0)


class TestRotation(unittest.TestCase):
    def test_year_of_the_newest_session(self):
        from context_core import write
        self.assertEqual(write.rotation_reason("## 2026-01-02 (mantenimiento)\nx\n## 2025-05-01\ny\n", "2026-01-03"), ("year", "2025"))


class TestOneList(unittest.TestCase):
    """The board's page and the scripts say the same list as the package (1.26.8: it was six copies that disagreed)."""
    REPO = pathlib.Path(__file__).resolve().parents[3]

    def test_page(self):
        import re
        from context_core.language import ES
        html = (self.REPO / "plugins/memoria/skills/tablero/vista.html").read_text(encoding="utf-8")
        m = re.search(r"const esSesion = t => !/\\\(\(([a-z|]+)\)\\\)/i", html)
        self.assertIsNotNone(m, "vista.html has no esSesion")
        self.assertEqual(set(m.group(1).split("|")), set(ES.non_session_tags))

    def test_no_copies_in_scripts(self):
        import re
        for f in (self.REPO / "plugins/memoria").rglob("*.py"):
            body = f.read_text(encoding="utf-8")
            body = re.sub(r"# --- context_core: generated.*?# --- end of context_core ---", "", body, flags=re.S)
            self.assertNotRegex(body, r"\(\((?:tarea|migracion)\|", f"{f.name} keeps its own list of entries that are not sessions")


if __name__ == "__main__":
    unittest.main()
