"""What the server serves through the package (review of `consultar`, findings 1, 2, 4, 5, 6 and 7): session headings
without bodies, an area declared twice read closed, no symbolic links, the challenge index over archives, the bare
«#AAAA-MM-DD» reference, the loader by level, and references cut at a restricted zone."""
import os, pathlib, sys, tempfile, textwrap, unicodedata, unittest

CORE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CORE))

from context_core import parse, views  # noqa: E402
from context_core.load import PUBLIC, REGISTERS, load_public, load_root  # noqa: E402
from context_core.storage import FolderStorage, OutsideRoot  # noqa: E402

GUIA = """# Prueba · esta carpeta

## Áreas

| Área | Qué es | Responsable | Cuenta | Quién la lee | Acceso |
|---|---|---|---|---|---|
| `ventas/` | Ventas | Ana | ana@x.mx | Todo el equipo | Abierta |
| `personas/` | Nómina | Beto | beto@x.mx | Dirección | Restringida |
{extra}
## Quién responde por qué

Contexto común: Ana (ana@x.mx).
Zona horaria: America/Mexico_City
"""

AREA = """# Ventas

## Proyectos
- `cuentas/` — las cuentas grandes.
- `secreto/` — restringido: dueño Beto.
"""

PROYECTO = """---
estado: borrador
actualizado: 2026-11-01
---

# Cuentas

## Objetivo
Vender.
"""

SESIONES = """# Sesiones

## 2026-11-02
Tema: seguimiento
El cliente dijo LEAK-TOPIC
Avances: LEAK-PROGRESS
Sesión de: Ana · plugin 1.25.5

## 2026-11-01
Tema: arranque
Avances: algo
Sesión de: Ana · plugin 1.25.5
"""

DECISIONES = """# Decisiones

## 2026-11-03 · Respuesta al cuestionamiento del día 2
Decidió: Ana
Por qué: se mantiene.
Responde a: #2026-01-02-2

## 2026-11-01 · Cuestionamiento: el corte
Planteó: Ana
Por qué: no cuadra.
Cuestiona a: ventas/cuentas#2026-01-02
Afecta a: ventas/secreto/plan.md · ventas/cuentas/restringido/sueldos.md · personas/nomina · ventas/cuentas/entregables/a.md
"""

ARCHIVO = """# Decisiones de 2026

## 2026-01-02 · Cuestionamiento: segundo del día
Planteó: Ana
Por qué: tampoco.
Cuestiona a: #2026-01-02

## 2026-01-02 · El corte por monto
Decidió: Ana
Por qué: así.
"""

VIEJO = """# Decisiones de 2024

## 2024-03-01 · Responde a algo de 2026 por error
Decidió: Ana
Por qué: prueba.
Responde a: ventas/cuentas#2026-11-01
"""


def make(root: pathlib.Path, extra: str = "") -> None:
    w = lambda rel, t: ((root / rel).parent.mkdir(parents=True, exist_ok=True), (root / rel).write_text(t, encoding="utf-8"))
    w("guia.md", GUIA.format(extra=extra))
    w("metodo.md", "# Método de trabajo · versión 1.25.6 · huella x\n")
    w("ventas/area.md", AREA)
    w("ventas/cuentas/proyecto.md", PROYECTO)
    w("ventas/cuentas/sesiones.md", SESIONES)
    w("ventas/cuentas/decisiones.md", DECISIONES)
    w("ventas/cuentas/decisiones-2026.md", ARCHIVO)
    w("ventas/cuentas/decisiones-2024.md", VIEJO)
    w("ventas/cuentas/entregables/a.md", "---\nestado: vigente\n---\n# A\n")
    w("ventas/cuentas/taller/notas.md", "# Notas\n")
    w("ventas/cuentas/restringido/sueldos.md", "---\nestado: vigente\n---\n# SECRET-BODY\n")
    w("ventas/secreto/proyecto.md", "# Secreto\n")
    w("personas/area.md", "# Personas\nPANORAMA-SECRET\n")


class Counting(FolderStorage):
    def __init__(self, root):
        super().__init__(root)
        self.reads = []

    def read(self, path):
        self.reads.append(path)
        return super().read(path)


class Reading(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        make(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_sessions_keep_no_body(self):
        r = load_root(self.root, year=2026, parts=PUBLIC)
        s = r.project("ventas/cuentas").sessions
        self.assertEqual(s[0].topic, "seguimiento")
        for e in s:
            self.assertNotIn("LEAK", e.topic + e.progress + e.pending)
        full = load_root(self.root, year=2026).project("ventas/cuentas").sessions
        self.assertIn("LEAK-PROGRESS", full[0].progress)

    def test_area_declared_twice_loads_closed(self):
        make(self.root, extra="| `personas/` | Otra | Ana | ana@x.mx | Todo el equipo | Abierta |\n")
        r = load_root(self.root, year=2026)
        self.assertEqual([x.slug for x in r.area_rows].count("personas"), 1)
        self.assertTrue(r.area("personas").restricted)
        self.assertTrue(any("filas en la tabla" in w for w in r.warnings))
        self.assertNotIn("PANORAMA-SECRET", repr(r.area("personas")))

    def test_bare_reference_takes_this_project(self):
        ref = parse.decision_ref("#2026-01-02-2", "ventas--cuentas")
        self.assertEqual((ref.project, ref.id), ("ventas--cuentas", "2026-01-02-2"))
        self.assertIsNone(parse.decision_ref("#2026-01-02").id)            # no project to resolve it against
        self.assertEqual(parse.decision_ref("a/b#2026-01-02", "x--y").project, "a--b")

    def test_archives_keep_ids_and_challenges(self):
        pr = load_root(self.root, year=2026).project("ventas/cuentas")
        ids = {d.id: d.title for d in pr.decisions}
        self.assertEqual(ids["2026-01-02"], "El corte por monto")          # counted from the oldest of the day
        self.assertEqual(ids["2026-01-02-2"], "Segundo del día")
        self.assertTrue(any(d.archived for d in pr.decisions))
        self.assertEqual(len(pr.old_responses), 1)

    def test_challenge_index(self):
        r = load_root(self.root, year=2026, parts=REGISTERS)
        idx = {c.key: c for c in views.challenge_index(r)}
        self.assertEqual(set(idx), {"ventas--cuentas#2026-11-01", "ventas--cuentas#2026-01-02-2"})
        self.assertEqual(idx["ventas--cuentas#2026-01-02-2"].answers, ["ventas--cuentas#2026-11-03"])   # bare form
        self.assertEqual(idx["ventas--cuentas#2026-11-01"].answers, ["ventas--cuentas (archivo antiguo)"])
        self.assertEqual(views.open_challenges(r), [])

    def test_loader_by_level(self):
        st = Counting(self.root)
        r = load_root(st, year=2026, projects=False)
        self.assertEqual(st.reads, ["guia.md", "metodo.md", "base/premisas.md", "ventas/area.md"])
        self.assertFalse(r.project("ventas/cuentas").loaded)
        st = Counting(self.root)
        load_root(st, year=2026, projects=["ventas--cuentas"], parts=PUBLIC)
        self.assertFalse([p for p in st.reads if "/taller/" in p or "restringido" in p])
        st = Counting(self.root)
        load_root(st, year=2026, parts=REGISTERS)
        self.assertFalse([p for p in st.reads if p.endswith(("sesiones.md", "proyecto.md")) or "/entregables/" in p])

    def test_public_reference(self):
        r = load_root(self.root, year=2026, projects=False)
        text = parse.decisions(DECISIONES)[1].affects
        out = views.public_reference(text, r)
        self.assertEqual(out, "ventas/secreto · ventas/cuentas · personas/ · ventas/cuentas/entregables/a.md")
        self.assertEqual(views.public_reference("`ventas/secreto#2026-01-02`", r), "ventas/secreto")
        cases = {   # review of 1.25.6, findings 1 and 2: the whole reference is cut, in any spelling
            "ventas/cuentas/restringido/plan de sueldos.md": "ventas/cuentas",
            "personas/nomina/restringido/sueldos.md": "personas/",
            "Ventas/Secreto/plan.md": "ventas/secreto",
            "ventas\\secreto\\plan.md": "ventas/secreto",
            "/Users/ana/Drive/org/ventas/secreto/plan.md": "ventas/secreto",
            "../secreto/plan.md": "ventas/secreto",
            "restringido/acta.md": "ventas/cuentas",
            "ventas/cuentas/Restringido/x.md": "ventas/cuentas",
            "x · personas/nómina 2026.xlsx, ventas/cuentas/entregables/a b.md": "x · personas/, ventas/cuentas/entregables/a b.md",
            "entregables/hosted-path.md (rebuilt)": "entregables/hosted-path.md (rebuilt)",
        }
        for given, want in cases.items():
            with self.subTest(given=given):
                self.assertEqual(views.public_reference(given, r, here="ventas--cuentas"), want)

    def test_an_area_not_loaded_is_cut(self):
        import shutil
        shutil.rmtree(self.root / "personas")     # on Drive the server may not list a restricted area's folder
        r = load_root(self.root, year=2026, projects=False)
        self.assertEqual(views.public_reference("personas/nomina/sueldos.md", r), "personas/")

    def test_short_or_respelled_rows_load_closed(self):
        make(self.root, extra="| `personas/` | Otra | Ana | ana@x.mx | Todo el equipo | Abierta |\n")
        r = load_root(self.root, year=2026)
        self.assertEqual([x.slug for x in r.area_rows].count("personas"), 1)
        self.assertTrue(r.area("personas").restricted)
        self.assertTrue(any("filas en la tabla" in w for w in r.warnings))
        self.assertNotIn("PANORAMA-SECRET", repr(r.area("personas")))

    def test_bare_reference_takes_this_project(self):
        ref = parse.decision_ref("#2026-01-02-2", "ventas--cuentas")
        self.assertEqual((ref.project, ref.id), ("ventas--cuentas", "2026-01-02-2"))
        self.assertIsNone(parse.decision_ref("#2026-01-02").id)            # no project to resolve it against
        self.assertEqual(parse.decision_ref("a/b#2026-01-02", "x--y").project, "a--b")

    def test_archives_keep_ids_and_challenges(self):
        pr = load_root(self.root, year=2026).project("ventas/cuentas")
        ids = {d.id: d.title for d in pr.decisions}
        self.assertEqual(ids["2026-01-02"], "El corte por monto")          # counted from the oldest of the day
        self.assertEqual(ids["2026-01-02-2"], "Segundo del día")
        self.assertTrue(any(d.archived for d in pr.decisions))
        self.assertEqual(len(pr.old_responses), 1)

    def test_challenge_index(self):
        r = load_root(self.root, year=2026, parts=REGISTERS)
        idx = {c.key: c for c in views.challenge_index(r)}
        self.assertEqual(set(idx), {"ventas--cuentas#2026-11-01", "ventas--cuentas#2026-01-02-2"})
        self.assertEqual(idx["ventas--cuentas#2026-01-02-2"].answers, ["ventas--cuentas#2026-11-03"])   # bare form
        self.assertEqual(idx["ventas--cuentas#2026-11-01"].answers, ["ventas--cuentas (archivo antiguo)"])
        self.assertEqual(views.open_challenges(r), [])

    def test_loader_by_level(self):
        st = Counting(self.root)
        r = load_root(st, year=2026, projects=False)
        self.assertEqual(st.reads, ["guia.md", "metodo.md", "base/premisas.md", "ventas/area.md"])
        self.assertFalse(r.project("ventas/cuentas").loaded)
        st = Counting(self.root)
        load_root(st, year=2026, projects=["ventas--cuentas"], parts=PUBLIC)
        self.assertFalse([p for p in st.reads if "/taller/" in p or "restringido" in p])
        st = Counting(self.root)
        load_root(st, year=2026, parts=REGISTERS)
        self.assertFalse([p for p in st.reads if p.endswith(("sesiones.md", "proyecto.md")) or "/entregables/" in p])

    def test_public_reference(self):
        r = load_root(self.root, year=2026, projects=False)
        text = parse.decisions(DECISIONES)[1].affects
        out = views.public_reference(text, r)
        self.assertEqual(out, "ventas/secreto · ventas/cuentas · personas/ · ventas/cuentas/entregables/a.md")
        self.assertEqual(views.public_reference("`ventas/secreto#2026-01-02`", r), "ventas/secreto")
        cases = {   # review of 1.25.6, findings 1 and 2: the whole reference is cut, in any spelling
            "ventas/cuentas/restringido/plan de sueldos.md": "ventas/cuentas",
            "personas/nomina/restringido/sueldos.md": "personas/",
            "Ventas/Secreto/plan.md": "ventas/secreto",
            "ventas\\secreto\\plan.md": "ventas/secreto",
            "/Users/ana/Drive/org/ventas/secreto/plan.md": "ventas/secreto",
            "../secreto/plan.md": "ventas/secreto",
            "restringido/acta.md": "ventas/cuentas",
            "ventas/cuentas/Restringido/x.md": "ventas/cuentas",
            "x · personas/nómina 2026.xlsx, ventas/cuentas/entregables/a b.md": "x · personas/, ventas/cuentas/entregables/a b.md",
            "entregables/hosted-path.md (rebuilt)": "entregables/hosted-path.md (rebuilt)",
        }
        for given, want in cases.items():
            with self.subTest(given=given):
                self.assertEqual(views.public_reference(given, r, here="ventas--cuentas"), want)

    def test_an_area_not_loaded_is_cut(self):
        import shutil
        shutil.rmtree(self.root / "personas")     # on Drive the server may not list a restricted area's folder
        r = load_root(self.root, year=2026, projects=False)
        self.assertEqual(views.public_reference("personas/nomina/sueldos.md", r), "personas/")

    def test_short_or_respelled_rows_load_closed(self):
        for extra in ("| `personas/` | Otra | Abierta |\n",                                     # short
                      "| `Personas/` | Otra | Ana | ana@x.mx | Todo el equipo | Abierta |\n"):  # another case
            make(self.root, extra=extra)
            g = (self.root / "guia.md").read_text(encoding="utf-8")
            g = g.replace("| `personas/` | Nómina | Beto | beto@x.mx | Dirección | Restringida |", "")
            g = g.replace("{x}", "")
            (self.root / "guia.md").write_text(g.replace("| `ventas/` |", "| `personas/` | Nómina | Restringida |\n| `ventas/` |") if "Otra | Abierta |\n" == extra[-18:] else g + "", encoding="utf-8")
        make(self.root, extra="| `personas/` | Otra | Ana | ana@x.mx | Todo el equipo | Abierta |\n")
        g = (self.root / "guia.md").read_text(encoding="utf-8").replace(
            "| `personas/` | Nómina | Beto | beto@x.mx | Dirección | Restringida |", "| `personas/` | Nómina | Restringida |")
        (self.root / "guia.md").write_text(g, encoding="utf-8")
        self.assertTrue(load_root(self.root, year=2026).area("personas").restricted)
        make(self.root, extra="| `Personas/` | Otra | Ana | ana@x.mx | Todo el equipo | Abierta |\n")
        self.assertTrue(load_root(self.root, year=2026).area("personas").restricted)
        nfd = unicodedata.normalize("NFD", "diseño")
        make(self.root, extra=f"| `diseño/` | D | Ana | ana@x.mx | Dirección | Restringida |\n| `{nfd}/` | D | Ana | ana@x.mx | Todo | Abierta |\n")
        (self.root / "diseño").mkdir(exist_ok=True)
        (self.root / "diseño" / "area.md").write_text("# D\nSECRET-AREA\n", encoding="utf-8")
        r = load_root(self.root, year=2026)
        self.assertNotIn("SECRET-AREA", repr(r))

    def test_headers_keep_the_first_topic_and_no_workshop(self):
        text = "## 2026-11-02\nTema: seguimiento\nAvances:\n- algo\ntrabajamos en: LEAK-BODY\nEscribió: taller/b.md, Restringido/acta.md, entregables/a.md\n"
        e = parse.sessions(text, headers_only=True)[0]
        self.assertEqual(e.topic, "seguimiento")
        self.assertEqual(e.wrote, ["entregables/a.md"])

    def test_reference_spellings(self):
        for given, want in {"Ventas/cuentas#2026-01-02": ("ventas--cuentas", "2026-01-02"),
                            "ventas/cuentas/decisiones.md#2026-01-02": ("ventas--cuentas", "2026-01-02"),
                            "otro#2026-01-02": ("ventas--otro", "2026-01-02"),
                            "decisiones.md#2026-01-02-3": ("ventas--cuentas", "2026-01-02-3")}.items():
            with self.subTest(given=given):
                ref = parse.decision_ref(given, "ventas--cuentas")
                self.assertEqual((ref.project, ref.id), want)

    def test_the_public_reading(self):
        st = Counting(self.root)
        r = load_public(st, year=2026)
        self.assertFalse([p for p in st.reads if "/taller/" in p])
        d = next(x for x in r.project("ventas/cuentas").decisions if x.affects)
        self.assertNotIn("sueldos", d.affects)
        self.assertNotIn("LEAK", repr(r.project("ventas/cuentas").sessions))
        with self.assertRaises(TypeError):
            load_root(self.root, parts="decisions")
        with self.assertRaises(ValueError):
            load_root(self.root, parts={"session"})
        self.assertTrue(load_root(self.root, projects="ventas/cuentas", year=2026).project("ventas/cuentas").loaded)

    def test_sessions_keep_their_numbers_by_default(self):
        (self.root / "ventas/cuentas/sesiones-2026.md").write_text("# S\n\n## 2026-01-05\nTema: viejo\n", encoding="utf-8")
        s = load_root(self.root, year=2026).project("ventas/cuentas").sessions
        self.assertEqual([e.n for e in s], [1, 0])
        s = load_root(self.root, year=2026, parts=PUBLIC | {"session_archives"}).project("ventas/cuentas").sessions
        self.assertEqual(len(s), 3)

    def test_year_follows_the_organization(self):
        from context_core.load import current_year
        self.assertIsInstance(current_year("America/Mexico_City"), int)
        self.assertIsInstance(current_year("No/Such_Zone"), int)


@unittest.skipIf(os.name == "nt", "symbolic links need privileges on Windows")
class Links(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        make(self.root)
        d = self.root / "ventas/cuentas"
        os.symlink(d / "restringido/sueldos.md", d / "entregables/c.md")
        os.symlink(d / "taller", d / "entregables/dir")
        self.st = FolderStorage(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_links_are_not_served(self):
        self.assertIsNone(self.st.read("ventas/cuentas/entregables/c.md"))
        self.assertIsNone(self.st.stat("ventas/cuentas/entregables/c.md"))
        self.assertIsNone(self.st.read("ventas/cuentas/entregables/dir/notas.md"))
        self.assertEqual(self.st.list("ventas/cuentas/entregables/dir"), [])
        self.assertEqual([e.name for e in self.st.list("ventas/cuentas/entregables")], ["a.md"])
        with self.assertRaises(OutsideRoot):
            self.st.write("ventas/cuentas/entregables/c.md", "x", expected=None)
        r = load_root(self.st, year=2026)
        self.assertNotIn("SECRET-BODY", repr(r))

    def test_a_link_out_of_the_root_reads_as_missing(self):
        out = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
        out.write("## 2026-01-01 · fuera\n"); out.close()
        reg = self.root / "ventas/cuentas/decisiones.md"
        reg.unlink(); os.symlink(out.name, reg)
        self.assertIsNone(self.st.read("ventas/cuentas/decisiones.md"))
        self.assertIsNone(self.st.stat("ventas/cuentas/decisiones.md"))
        load_root(self.st, year=2026)              # the root still loads
        os.unlink(out.name)


if __name__ == "__main__":
    unittest.main()
