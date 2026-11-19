"""The development kit's reading (1.27): the «Desarrollo» section and the missing pieces
(tecnologia/metodologia-desarrollo#2026-11-18-4 and #2026-11-19-2)."""
import pathlib, sys, unicodedata, unittest

CORE = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CORE)]

from context_core import development as dev, parse  # noqa: E402

PROYECTO = """---
estado: vigente
actualizado: 2026-11-18
---

# Servidor

## Estatus
2026-11-18 · **En curso.**

## Quién participa
Responsable: Juanjo Jiménez-Alfaro (shared-memory)
Colabora: Ana López (ana@acme.mx)

## Desarrollo
Repositorios: decisionbits/work-memory · `TuOpinas/memoria`
Configuración de plataforma: tecnologia/plataforma.md
Configuración de repositorios: shared-memory/product-design/entregables/repositorios.md
Diseño: shared-memory/product-design/entregables/diseno.md
Plan: shared-memory/product-design/entregables/plan.md
Seguimiento: por crear
Paso a Prod: sí sobre el resumen del despliegue
Acepta: Fabiola Davó (fabi@smilepill.mx)
Audita: Juanjo Jiménez-Alfaro (juanjo@tuopinas.mx, @juanjo-jimenez-alfaro)
Construye: Juanjo Jiménez-Alfaro (juanjo@tuopinas.mx, @juanjo-jimenez-alfaro) · Ana López (ana@acme.mx, @analopez)
Administra: Juanjo Jiménez-Alfaro (juanjo@tuopinas.mx, @juanjo-jimenez-alfaro)
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
        self.assertEqual([p.name for p in s.roles["Construye"]], ["Juanjo Jiménez-Alfaro", "Ana López"])
        self.assertEqual(s.roles["Construye"][1].user, "analopez")
        self.assertEqual(s.roles["Audita"][0].email, "juanjo@tuopinas.mx")
        self.assertEqual(s.unknown, [])
        self.assertEqual(s.warnings, [])

    def test_person_without_github_user(self):
        p = dev.seccion_desarrollo(PROYECTO).roles["Acepta"][0]
        self.assertEqual((p.name, p.email, p.user), ("Fabiola Davó", "fabi@smilepill.mx", ""))

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
                self.assertEqual(len(s.present), len(dev.ALL_KEYS), s.unknown)
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

    def test_bad_values_warn(self):
        s = dev.development_section(PROYECTO.replace("decisionbits/work-memory", "work-memory")
                                    .replace("(fabi@smilepill.mx)", "(fabi en smile pill)"))
        self.assertEqual(s.repositories, ["TuOpinas/memoria"])
        self.assertTrue(any("work-memory" in w for w in s.warnings))
        self.assertTrue(any("fabi en smile pill" in w for w in s.warnings))

    def test_section_stops_at_next_heading_and_ignores_fences(self):
        text = PROYECTO + "\n## Otra\nPlan: no/es/de/aqui.md\n"
        self.assertEqual(dev.development_section(text).paths[dev.PLAN], "shared-memory/product-design/entregables/plan.md")
        fenced = PROYECTO.replace("## Desarrollo", "```\n## Desarrollo\nPlan: ejemplo.md\n```\n\n## Desarrollo", 1)
        self.assertEqual(dev.development_section(fenced).paths[dev.PLAN], "shared-memory/product-design/entregables/plan.md")

    def test_quien_participa_does_not_take_the_section(self):
        # abrir.py, cerrar.py and verificar.sh cut «Quién participa» at the next «## » (the doubt of the kit's first
        # review): a «Desarrollo» after it does not leak its people into the project's collaborators
        resp, coll, _, raw = parse.who_takes_part(parse.frontmatter(PROYECTO)[1])
        self.assertEqual(resp, "Juanjo Jiménez-Alfaro")
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
            ("rol vacío", PROYECTO.replace("Administra: Juanjo Jiménez-Alfaro (juanjo@tuopinas.mx, @juanjo-jimenez-alfaro)",
                                           "Administra:"), None, [("Administra", "vacía")]),
            ("repositorios por crear", PROYECTO.replace("Repositorios: decisionbits/work-memory · `TuOpinas/memoria`",
                                                        "Repositorios: Por Crear"), None, [("Repositorios", "por crear")]),
            ("seguimiento que no existe", PROYECTO.replace("Seguimiento: por crear", "Seguimiento: x/seguimiento.md"), None,
             [("Seguimiento", "no existe")]),
        ]
        for name, text, exist, want in cases:
            with self.subTest(name):
                self.assertEqual(self.missing(text, exist), want)



if __name__ == "__main__":
    unittest.main()
