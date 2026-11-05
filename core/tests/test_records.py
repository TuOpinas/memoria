"""The record model builds from the test root in its three forms: 1.21 as written, migrated to 1.22 by the real
migration, and in the 1.25 form («Quién es quién»). Same areas, projects and people must come out of all three.
Run: python3 -m unittest discover -s core/tests (from the repository root)."""
import pathlib, sys, unittest

CORE = pathlib.Path(__file__).resolve().parents[1]
REPO = CORE.parent
sys.path[:0] = [str(CORE), str(REPO / "pruebas")]

from memoria_core.load import load_root  # noqa: E402
import comun  # noqa: E402

FORMS = {}


def setUpModule():
    FORMS["1.21"] = load_root(comun.RAIZ)
    FORMS["1.22"] = load_root(comun.raiz_migrada()[0])
    FORMS["1.25"] = load_root(comun.raiz_125()[0])


class EveryForm(unittest.TestCase):
    def test_same_areas_and_restrictions(self):
        for v, r in FORMS.items():
            with self.subTest(form=v):
                self.assertEqual([a.slug for a in r.areas], ["ventas", "personas", "operacion", "archivo"])
                self.assertEqual({a.slug for a in r.areas if a.restricted}, {"personas"})
                self.assertEqual({x.slug for x in r.area_rows if x.restricted}, {"personas", "legal"})

    def test_same_accounts_per_area(self):
        want = {"ventas": ({"ana@ejemplo.test"}, {"carla@ejemplo.test"}), "legal": ({"beto@ejemplo.test"}, {"eva@ejemplo.test"}),
                "operacion": ({"ana@ejemplo.test"}, set())}
        for v, r in FORMS.items():
            rows = {x.slug: x for x in r.area_rows}
            for slug, (resp, coll) in want.items():
                with self.subTest(form=v, area=slug):
                    self.assertEqual(rows[slug].responsible_accounts, resp)
                    self.assertEqual(rows[slug].collaborator_accounts, coll)

    def test_restricted_projects_are_not_read(self):
        for v, r in FORMS.items():
            ventas = r.area("ventas")
            with self.subTest(form=v):
                closed = {p.slug for p in ventas.projects if p.restricted}
                self.assertTrue({"precios", "ronda", "secreto", "margenes"} <= closed)
                for p in ventas.projects:
                    if p.restricted:
                        self.assertEqual((p.decisions, p.sessions, p.steps, p.deliverables), ([], [], [], []))

    def test_project_cuentas(self):
        for v, r in FORMS.items():
            p = r.project("ventas--cuentas")
            with self.subTest(form=v):
                self.assertEqual(p.key, "ventas--cuentas")
                self.assertEqual(p.responsible, "Ana Prueba")
                self.assertIsNotNone(p.status)
                self.assertEqual(len(p.steps), 8)
                ids = [d.id for d in p.decisions if d.id]
                self.assertEqual(ids[:4], ["2026-09-26", "2026-09-21-2", "2026-09-21", "2026-09-20"])
                d26 = p.decisions[0]
                self.assertEqual((d26.responds_to.project, d26.responds_to.id), ("operacion--soporte", "2026-09-25"))
                self.assertTrue(any(d.pending_confirmation for d in p.decisions))
                states = {d.name: d.state for d in p.deliverables}
                self.assertEqual(states.get("kit-cuentas"), "vigente")
                self.assertFalse(any("restringido" in s for e in p.sessions for s in e.wrote))

    def test_premises(self):
        for v, r in FORMS.items():
            with self.subTest(form=v):
                self.assertEqual([p.id for p in r.current_premises], [p.id for p in r.premises if p.id not in {"P1", "P2"}])

    def test_people_registry_only_in_125(self):
        self.assertFalse(FORMS["1.21"].people.declared)
        reg = FORMS["1.25"].people
        self.assertTrue(reg.declared)
        self.assertEqual(reg.by_account["ana@ejemplo.test"].name, "Ana Prueba")


class StatusForms(unittest.TestCase):
    """The Estatus of 1.22+, with the bold before or after the colon and «Siguiente» with sub-bullets."""
    TEXT = """## Estatus
2026-11-05 · **Step 0 starts.**
- **Se completó:** the stack.
- Siguiente: the record model
  - then the adapter
- **Falta decidir**: groups.
- Preocupa: one bug exposes a zone.
  It is the server's check.

## Objetivo
x
"""

    def test_fields(self):
        from memoria_core import parse
        st = parse.status(self.TEXT)
        self.assertEqual((st.source, st.date, st.headline), ("Estatus", "2026-11-05", "Step 0 starts."))
        self.assertEqual(st.completed, "the stack.")
        self.assertEqual(st.next, ["the record model", "then the adapter"])
        self.assertEqual(st.next, parse.area_priorities(self.TEXT))
        self.assertEqual(st.to_decide, "groups.")
        self.assertEqual(st.concern, "one bug exposes a zone.\nIt is the server's check.")

    def test_migrated_roots_have_estatus(self):
        for v in ("1.22", "1.25"):
            with self.subTest(form=v):
                self.assertEqual(FORMS[v].project("ventas--cuentas").status.source, "Estatus")


if __name__ == "__main__":
    unittest.main()
