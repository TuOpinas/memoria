"""The package parses like the scripts. Takes the functions out of generar_vista.py (the board's generator, the widest
reader of the method), runs them and the package on every file of the test root in its three forms, and compares.
When a script moves onto the package (step 0, task 3) its copy goes away and this test keeps the other copies honest
until they go too."""
import pathlib, re, sys, unittest, unicodedata, datetime, os

CORE = pathlib.Path(__file__).resolve().parents[1]
REPO = CORE.parent.parent
sys.path[:0] = [str(CORE), str(REPO / "pruebas")]

from context_core import parse  # noqa: E402
import comun  # noqa: E402

GEN = REPO / "plugins" / "memoria" / "skills" / "tablero" / "generar_vista.py"
NAMES = ["fecha_valida", "fechas_en", "frontmatter", "seccion", "bullets", "clave_nombre", "_titulo", "cuentas",
         "registro_personas", "persona", "nombres_de", "restringida_celda", "prioridades_area", "parse_decisiones",
         "ref_decision", "parse_sesiones", "parse_indice_proyectos", "colaboran_en", "cuentas_de_nombres",
         "altas_provisionales"]


def script_functions():
    src = GEN.read_text(encoding="utf-8")
    ns = {"re": re, "unicodedata": unicodedata, "datetime": datetime, "os": os}
    for line in ("CORREO", "PALABRA_COLABORA", "LINEA_COLABORA"):
        exec(re.search(rf"^{line} = .*$", src, re.M).group(0), ns)
    for n in NAMES:
        exec(re.search(rf"^def {n}\(.*?(?=^\S)", src, re.M | re.S).group(0), ns)
    return ns


S = script_functions()
ROOTS = {}


def setUpModule():
    ROOTS["1.21"] = comun.RAIZ
    ROOTS["1.22"] = comun.raiz_migrada()[0]
    ROOTS["1.25"] = comun.raiz_125()[0]


def files(root, name):
    return [p for p in root.rglob(name) if "restringido" not in p.parts]


def ref_tuple(r):
    return (r.project, r.id) if r and r.project else None


class Parity(unittest.TestCase):
    def test_decisions(self):
        for v, root in ROOTS.items():
            for f in files(root, "decisiones*.md"):
                t = f.read_text(encoding="utf-8")
                old, new = S["parse_decisiones"](t), parse.decisions(t)
                with self.subTest(form=v, file=str(f.relative_to(root))):
                    self.assertEqual([(d["id"], d["fecha"], d["titulo"], d["decidio"], d["porque"], d["descartamos"],
                                       d["afecta"], d.get("tipo", "decision").replace("cuestionamiento", "challenge"),
                                       bool(d.get("por_confirmar"))) for d in old],
                                     [(d.id, d.date, d.title, d.decided_by, d.why, d.discarded, d.affects, d.kind,
                                       d.pending_confirmation) for d in new])
                    self.assertEqual([S["ref_decision"](d.get("responde", ""))[0] and S["ref_decision"](d["responde"]) for d in old],
                                     [ref_tuple(d.responds_to) for d in new])

    def test_sessions(self):
        for v, root in ROOTS.items():
            for f in files(root, "sesiones*.md"):
                t = f.read_text(encoding="utf-8")
                old, new = S["parse_sesiones"](t), parse.sessions(t)
                with self.subTest(form=v, file=str(f.relative_to(root))):
                    self.assertEqual([(e["n"], e["fecha"], e["titulo"], e["trabajamos"], e["avances"], e["pendiente"],
                                       e.get("quien", ""), e.get("escribio", []), e.get("publico", [])) for e in old],
                                     [(e.n, e.date, e.title, e.topic, e.progress, e.pending, e.by, e.wrote, e.published)
                                      for e in new])

    def test_area_index_and_priorities(self):
        for v, root in ROOTS.items():
            for f in files(root, "area.md"):
                t = f.read_text(encoding="utf-8")
                old, new = S["parse_indice_proyectos"](t), parse.project_index(t)
                with self.subTest(form=v, file=str(f.relative_to(root))):
                    self.assertEqual({k: (x["descripcion"], {s: (e["descripcion"], e["actualizado"]) for s, e in x["entregables"].items()}, x["notas"]) for k, x in old.items()},
                                     {k: (x.description, {s: (e["description"], e["updated"]) for s, e in x.deliverables.items()}, x.notes) for k, x in new.items()})
                    self.assertEqual(S["prioridades_area"](parse.frontmatter(t)[1]), parse.area_priorities(parse.frontmatter(t)[1]))

    def test_frontmatter(self):
        for v, root in ROOTS.items():
            for f in files(root, "*.md"):
                t = f.read_text(encoding="utf-8")
                with self.subTest(form=v, file=str(f.relative_to(root))):
                    self.assertEqual(S["frontmatter"](t), parse.frontmatter(t))

    def test_people_and_accounts(self):
        for v, root in ROOTS.items():
            g = (root / "guia.md").read_text(encoding="utf-8")
            old, new = S["registro_personas"](g), parse.people_registry(g)
            with self.subTest(form=v):
                self.assertEqual(old["hay"], new.declared)
                self.assertEqual([(p["nombre"], p["cuentas"], p["baja"], p["alias"]) for p in old["personas"]],
                                 [(p.name, p.accounts, p.left_on, p.aliases) for p in new.people])
                self.assertEqual(old["avisos"], new.warnings)
                for pm in files(root, "proyecto.md"):
                    q = parse.section(parse.frontmatter(pm.read_text(encoding="utf-8"))[1], "Quién participa")
                    self.assertEqual(S["colaboran_en"](q, old), parse.collaborator_accounts(q, new), str(pm))

    def test_restricted_cells(self):
        for c in ["Restringida: Ana Prueba y Beto Prueba", "Dirección (restringida)", "Todo el equipo",
                  "Todo el equipo; los proyectos restringidos aparte", "Abierta (antes restringida)", "nunca restringida"]:
            self.assertEqual(S["restringida_celda"](c), parse.is_restricted_cell(c), c)


if __name__ == "__main__":
    unittest.main()
