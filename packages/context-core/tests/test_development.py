"""The development kit's reading (1.27): the «Desarrollo» section and the missing pieces
(tecnologia/metodologia-desarrollo#2026-11-18-4 and #2026-11-19-2)."""
import pathlib, re, sys, unicodedata, unittest

CORE = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CORE)]

from context_core import development as dev, dev_view, parse  # noqa: E402

PROYECTO = """---
estado: vigente
actualizado: 2026-11-18
---

# Servidor

## Estatus
2026-11-18 · **En curso.**

## Quién participa
Responsable: Ana Pérez (shared-memory)
Colabora: Ana López (ana@acme.mx)

## Desarrollo
Repositorios: decisionbits/work-memory · `TuOpinas/memoria`
Configuración de plataforma: tecnologia/plataforma.md
Configuración de repositorios: shared-memory/product-design/entregables/repositorios.md
Diseño: shared-memory/product-design/entregables/diseno.md
Plan: shared-memory/product-design/entregables/plan.md
Seguimiento: por crear
Paso a Prod: sí sobre el resumen del despliegue
Acepta: Luisa Gómez (luisa@ejemplo.test)
Audita: Ana Pérez (ana@ejemplo.test, @ana-perez)
Construye: Ana Pérez (ana@ejemplo.test, @ana-perez) · Ana López (ana@acme.mx, @analopez)
Administra: Ana Pérez (ana@ejemplo.test, @ana-perez)
"""


def strip_accents(t):
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")


class Section(unittest.TestCase):
    def test_reads_every_line(self):
        s = dev.seccion_desarrollo(PROYECTO)
        self.assertTrue(s.found)
        self.assertEqual(s.repositories, ["decisionbits/work-memory", "TuOpinas/memoria"])
        self.assertEqual(s.paths[dev.DESIGN], "shared-memory/product-design/entregables/diseno.md")
        self.assertEqual(s.paths[dev.FOLLOW_UP], dev.TO_BUILD)
        self.assertEqual(s.step_to_prod, "sí sobre el resumen del despliegue")
        self.assertEqual([p.name for p in s.roles["Construye"]], ["Ana Pérez", "Ana López"])
        self.assertEqual(s.roles["Construye"][1].user, "analopez")
        self.assertEqual(s.roles["Audita"][0].email, "ana@ejemplo.test")
        self.assertEqual(s.unknown, [])
        self.assertEqual(s.warnings, [])

    def test_person_without_github_user(self):
        p = dev.seccion_desarrollo(PROYECTO).roles["Acepta"][0]
        self.assertEqual((p.name, p.email, p.user), ("Luisa Gómez", "luisa@ejemplo.test", ""))

    def test_keys_without_accents_nfd_and_case(self):
        cases = {
            "sin acentos": strip_accents(PROYECTO).replace("## Desarrollo", "## Desarrollo"),
            "NFD": unicodedata.normalize("NFD", PROYECTO),
            "mayúsculas": PROYECTO.replace("Diseño:", "DISEÑO:").replace("Paso a Prod:", "paso a prod:"),
            "viñetas y negrita": PROYECTO.replace("Diseño:", "- **Diseño:**").replace("Plan:", "* Plan:"),
        }
        for name, text in cases.items():
            with self.subTest(name):
                s = dev.development_section(text)
                self.assertTrue(s.found)
                self.assertEqual(len(s.present), len(dev.ALL_KEYS) - len(dev.OPTIONAL_KEYS), s.unknown)
                self.assertTrue(s.paths[dev.DESIGN].endswith(strip_accents("diseno.md")))

    def test_no_section_is_not_development(self):
        text = PROYECTO.split("## Desarrollo")[0]
        s = dev.development_section(text)
        self.assertFalse(s.found)
        self.assertEqual(dev.missing_pieces(s, lambda p: False), [])

    def test_unknown_lines_and_duplicates(self):
        s = dev.development_section(PROYECTO + "Prueba: algo\nDiseño: otra/ruta.md\n")
        self.assertEqual(s.unknown, ["Prueba: algo"])
        self.assertEqual(s.paths[dev.DESIGN], "shared-memory/product-design/entregables/diseno.md")
        self.assertTrue(any("dos veces" in w for w in s.warnings))

    def test_github_link_in_repositories(self):
        s = dev.development_section(PROYECTO.replace("decisionbits/work-memory", "https://github.com/decisionbits/work-memory.git"))
        self.assertEqual(s.repositories, ["decisionbits/work-memory", "TuOpinas/memoria"])
        self.assertEqual(s.warnings, [])

    def test_bad_values_warn(self):
        s = dev.development_section(PROYECTO.replace("decisionbits/work-memory", "work-memory")
                                    .replace("(luisa@ejemplo.test)", "(luisa en ejemplo)"))
        self.assertEqual(s.repositories, ["TuOpinas/memoria"])
        self.assertTrue(any("work-memory" in w for w in s.warnings))
        self.assertTrue(any("luisa en ejemplo" in w for w in s.warnings))

    def test_section_stops_at_next_heading_and_ignores_fences(self):
        text = PROYECTO + "\n## Otra\nPlan: no/es/de/aqui.md\n"
        self.assertEqual(dev.development_section(text).paths[dev.PLAN], "shared-memory/product-design/entregables/plan.md")
        fenced = PROYECTO.replace("## Desarrollo", "```\n## Desarrollo\nPlan: ejemplo.md\n```\n\n## Desarrollo", 1)
        self.assertEqual(dev.development_section(fenced).paths[dev.PLAN], "shared-memory/product-design/entregables/plan.md")

    def test_quien_participa_does_not_take_the_section(self):
        # abrir.py, cerrar.py and verificar.sh cut «Quién participa» at the next «## » (the doubt of the kit's first
        # review): a «Desarrollo» after it does not leak its people into the project's collaborators
        resp, coll, _, raw = parse.who_takes_part(parse.frontmatter(PROYECTO)[1])
        self.assertEqual(resp, "Ana Pérez")
        self.assertNotIn("Construye", raw)
        self.assertNotIn("analopez", raw)
        self.assertEqual(parse.section(PROYECTO, "Quién participa").count("\n"), 1)


class Missing(unittest.TestCase):
    EXIST = {"tecnologia/plataforma.md", "shared-memory/product-design/entregables/diseno.md",
             "shared-memory/product-design/entregables/plan.md",
             "shared-memory/product-design/entregables/repositorios.md"}

    def missing(self, text, exist=None):
        exist = self.EXIST if exist is None else exist
        return [(m.key, m.reason) for m in dev.piezas_faltantes(dev.seccion_desarrollo(text), lambda p: p in exist)]

    def test_complete_and_follow_up_to_build_does_not_count(self):
        self.assertEqual(self.missing(PROYECTO), [])

    def test_one_configuration_for_both_keys(self):
        # the kit has one configuration template for the platform and the repositories: both keys may point to it
        text = PROYECTO.replace("shared-memory/product-design/entregables/repositorios.md", "tecnologia/plataforma.md")
        self.assertEqual(self.missing(text), [])

    def test_cases(self):
        cases = [
            ("línea ausente", PROYECTO.replace("Plan: shared-memory/product-design/entregables/plan.md\n", ""), None,
             [("Plan", "sin línea")]),
            ("archivo que no está", PROYECTO, self.EXIST - {"tecnologia/plataforma.md"},
             [("Configuración de plataforma", "no existe")]),
            ("por crear cuenta salvo el seguimiento", PROYECTO.replace("Diseño: shared-memory/product-design/entregables/diseno.md",
                                                                      "Diseño: por crear"), None,
             [("Diseño", "por crear")]),
            ("rol vacío", PROYECTO.replace("Administra: Ana Pérez (ana@ejemplo.test, @ana-perez)",
                                           "Administra:"), None, [("Administra", "vacía")]),
            ("repositorios por crear", PROYECTO.replace("Repositorios: decisionbits/work-memory · `TuOpinas/memoria`",
                                                        "Repositorios: Por Crear"), None, [("Repositorios", "por crear")]),
            ("seguimiento que no existe", PROYECTO.replace("Seguimiento: por crear", "Seguimiento: x/seguimiento.md"), None,
             [("Seguimiento", "no existe")]),
        ]
        for name, text, exist, want in cases:
            with self.subTest(name):
                self.assertEqual(self.missing(text, exist), want)

    def test_audit_may_be_nobody_and_receives_is_optional(self):
        # 1.30.0 (shared-memory/plugin-memoria#2026-11-25-4): «Audita: nadie» is a value, an empty «Audita:» is missing,
        # and «Recibe» counts neither without its line nor empty
        audit = "Audita: Ana Pérez (ana@ejemplo.test, @ana-perez)"
        for nobody in ("nadie", "Nadie", "NADIE"):
            with self.subTest(nobody):
                text = PROYECTO.replace(audit, f"Audita: {nobody}")
                self.assertEqual(dev.seccion_desarrollo(text).roles["Audita"], [])
                self.assertEqual(self.missing(text), [])
        self.assertEqual(self.missing(PROYECTO.replace(audit, "Audita:")), [("Audita", "vacía")])
        self.assertEqual(self.missing(PROYECTO + "Recibe:\n"), [])
        s = dev.seccion_desarrollo(PROYECTO + "Recibe: Ana López (ana@cliente.mx)\n")
        self.assertEqual([(p.name, p.email) for p in s.roles["Recibe"]], [("Ana López", "ana@cliente.mx")])
        # «nadie» is only Audita's: in another role it is read as written
        self.assertEqual(dev.seccion_desarrollo(PROYECTO + "Recibe: nadie\n").roles["Recibe"][0].name, "nadie")


class PieceIdentifier(unittest.TestCase):
    """A piece whose identifier ends in a letter (review of 1.30.0, finding 3): read as its own piece."""
    PLAN = ("## Fases\n| Fase | Qué podrá hacer quién | Versión | Listo cuando |\n|---|---|---|---|\n| F1 · Uno | x | 1.0.0 | x |\n\n"
            "## Piezas\n| Pieza | Fase | Qué entrega |\n|---|---|---|\n| P02 · Lista | F1 | a |\n| P02a · Filtro | F1 | b |\n\n"
            "## Hecha cuando\n### P02 · Lista\nAprobó: Ana Pérez, 2026-11-20\n- **Lista** se ve\n\n"
            "### P02a · Filtro\nAprobó: pendiente\n- **Filtro** filtra\n")

    def test_p02a(self):
        plan, warnings = dev_view.read_plan(self.PLAN)
        self.assertEqual(warnings, [])
        self.assertEqual([p["id"] for p in plan["piezas"]], ["P02", "P02a"])
        self.assertEqual(plan["fases"][0]["piezas"], ["P02", "P02a"])
        p02, p02a = plan["piezas"]
        self.assertEqual([e["titulo"] for e in p02["escenarios"]], ["Lista"])
        self.assertEqual([e["titulo"] for e in p02a["escenarios"]], ["Filtro"])
        self.assertEqual(p02a["aprobo"], "")
        seg = "## 2026-11-25\n| Pieza | Estado |\n|---|---|\n| p02A | En curso |\n"
        self.assertEqual(dev_view.read_follow_up(seg), ("2026-11-25", {"P02a": "En curso"}))
        self.assertTrue(re.fullmatch(dev_view.PIECE_ID, "H22a"))



if __name__ == "__main__":
    unittest.main()
