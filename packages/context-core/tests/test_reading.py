"""What the server serves through the package (review of `consultar`, findings 1, 2, 4, 5, 6 and 7): session headings
without bodies, an area declared twice read closed, no symbolic links, the challenge index over archives, the bare
«#AAAA-MM-DD» reference, the loader by level, and references cut at a restricted zone."""
import os, pathlib, sys, tempfile, textwrap, unittest

CORE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CORE))

from context_core import parse, views  # noqa: E402
from context_core.load import PUBLIC, REGISTERS, load_root  # noqa: E402
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
        self.assertTrue(any("dos filas" in w for w in r.warnings))
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


if __name__ == "__main__":
    unittest.main()
