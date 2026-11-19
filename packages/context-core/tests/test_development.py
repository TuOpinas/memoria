"""The development kit's reading (1.27): the «Desarrollo» section, the missing pieces, the design, the plan, the two
configurations and the status of each piece (tecnologia/metodologia-desarrollo#2026-11-18-4, -10 and -11)."""
import pathlib, sys, unicodedata, unittest

CORE = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CORE)]

from context_core import development as dev, parse  # noqa: E402
from context_core.development import PullRequest as PR  # noqa: E402

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

    def test_a_heading_without_kit_keys_is_not_development(self):
        # «Desarrollo» is a common heading: without one key of the kit it marks nothing (review of 1.27.0, finding 20)
        text = "# P\n\n## Quién participa\nResponsable: Ana\n\n## Desarrollo\nEl proyecto avanza por trimestres.\n"
        self.assertFalse(dev.development_section(text).found)
        self.assertFalse(dev.development_section(text + "Plan: lanzar la campaña en marzo\n").found)
        self.assertFalse(dev.development_section(text + "Plan: lanzar la campaña en marzo\n").near_miss)
        self.assertFalse(dev.development_section(text + "<!-- Plan: ruta -->\n<!-- Diseño: ruta -->\n").found)
        self.assertTrue(dev.development_section(text + "Plan: por crear\nDiseño: por crear\n").found)
        self.assertTrue(dev.development_section(text + "Repositorios: acme/app\n").found)
        miss = dev.development_section(text.replace("El proyecto", "Repositorio: acme/app\nConstruyen: Ana\nAudito: Beto\nEl proyecto"))
        self.assertEqual((miss.found, miss.near_miss), (False, True))

    def test_github_user_with_underscore_and_dot(self):
        s = dev.development_section(PROYECTO.replace("@analopez", "@ana_acme").replace("@juanjo-jimenez-alfaro)", "@juanjo.j)"))
        self.assertEqual(s.roles["Construye"][1].user, "ana_acme")
        self.assertEqual(s.roles["Audita"][0].user, "juanjo.j")
        self.assertEqual(s.warnings, [])

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


DISENO = """# Diseño

## Objetivo
Una memoria compartida.

## Reglas
| Regla | Excepción |
|---|---|
| Una decisión no se edita | Nunca |

## Componentes
| Componente | Qué hace | Dónde vive |
|---|---|---|
| Servidor | Atiende a la IA | `decisionbits/work-memory:server/` |
| [Nombre] | [Una frase] | [organización/repositorio:ruta] |

## Datos
| Entidad | Qué es | Se relaciona con |
|---|---|---|
| organization | La empresa | `root` (1:N), person (1:n) |
| root | Una memoria | thing (1:N) |
| thing | Una cosa | act (N:M) |
| act | Un acto | thing (N:1), ghost (1:1) |
| person | Una persona | |

## Conceptos
| Concepto | Significa | No es |
|---|---|---|
| Cosa | Lo que se recuerda | objeto, item |

## Infraestructura
| Pieza | Para qué | Dónde |
|---|---|---|
| Postgres | El registro | Google Cloud · Prod |

## Prototipo
https://ejemplo.mx · 2026-11-10
"""


class Design(unittest.TestCase):
    def test_tables(self):
        d = dev.leer_diseno(DISENO)
        self.assertEqual(d.missing, [])
        self.assertEqual(d.objective, "Una memoria compartida.")
        self.assertEqual(d.components, [{"componente": "Servidor", "que_hace": "Atiende a la IA",
                                         "donde_vive": "decisionbits/work-memory:server/"}])
        self.assertEqual([e.name for e in d.entities], ["organization", "root", "thing", "act", "person"])
        org = d.entities[0]
        self.assertEqual([(r.target, r.cardinality) for r in org.relations], [("root", "1:N"), ("person", "1:N")])
        self.assertEqual(d.concepts[0]["no_es"], ["objeto", "item"])
        self.assertEqual(d.rules[0]["excepcion"], "Nunca")
        self.assertEqual(d.infrastructure[0]["donde"], "Google Cloud · Prod")

    def test_bad_relations_warn(self):
        d = dev.read_design(DISENO)
        self.assertTrue(any("N:1" in w for w in d.warnings))
        self.assertTrue(any("ghost" in w for w in d.warnings))
        self.assertEqual([r.target for r in d.entities[3].relations], ["ghost"])

    def test_missing_column_and_section(self):
        cases = [
            ("columna", DISENO.replace("| Componente | Qué hace | Dónde vive |", "| Componente | Qué hace | Ruta |"),
             ["columna Dónde vive en Componentes"]),
            ("sección", DISENO.replace("## Conceptos", "## Glosario"), ["sección Conceptos"]),
            ("sin acentos", strip_accents(DISENO), []),
        ]
        for name, text, want in cases:
            with self.subTest(name):
                self.assertEqual(dev.read_design(text).missing, want)

    def test_template_rows_are_skipped(self):
        d = dev.read_design(DISENO)
        self.assertEqual(len(d.components), 1)


PLAN = """# Plan

## Fases
| Fase | Qué podrá hacer quién | Versión | Listo cuando | Estado |
|---|---|---|---|---|
| F1 · Registro | La IA guarda | 0.3 | Las piezas en Prod | cerrada |
| F2 · Tablero | Quien dirige ve | 0.4 | El tablero lee | en curso |

## Piezas
| Pieza | Fase | Qué entrega | Hecha cuando |
|---|---|---|---|
| P01 · Tablas | F1 | Las tablas | Migración aplicada |
| P02 · Lectura | F2 · Tablero | La lectura | Pruebas en verde |
| P03 · Vista | F2 | La vista | Se ve |
"""


class PlanTests(unittest.TestCase):
    def test_tables(self):
        p = dev.leer_plan(PLAN)
        self.assertEqual(p.missing, [])
        self.assertEqual([(f.id, f.name, f.state) for f in p.phases], [("F1", "Registro", "cerrada"), ("F2", "Tablero", "en curso")])
        self.assertEqual([(x.id, x.name, x.phase) for x in p.pieces],
                         [("P01", "Tablas", "F1"), ("P02", "Lectura", "F2"), ("P03", "Vista", "F2")])
        self.assertEqual(p.warnings, [])

    def test_warnings(self):
        text = (PLAN.replace("| cerrada |", "| en curso |")
                .replace("| P03 · Vista | F2 |", "| P01 · Otra | F9 |"))
        w = dev.read_plan(text).warnings
        self.assertTrue(any("más de una en curso" in x for x in w))
        self.assertTrue(any("P01" in x and "dos veces" in x for x in w))
        p = dev.read_plan(PLAN.replace("| P03 · Vista | F2 |", "| P03 · Vista | F9 |"))
        self.assertTrue(any("F9" in x for x in p.warnings))
        self.assertTrue(any("terminada" in x for x in dev.read_plan(PLAN.replace("| cerrada |", "| terminada |")).warnings))

    def test_missing_column(self):
        self.assertEqual(dev.read_plan(PLAN.replace("| Hecha cuando |", "| Cuándo |")).missing, ["columna Hecha cuando en Piezas"])
        self.assertEqual(dev.read_plan(PLAN.split("## Piezas")[0]).missing, ["sección Piezas"])


PLATAFORMA = """# Configuración de plataforma

| # | Qué se cumple | Qué tiene este proyecto | Cómo se comprueba | Estado |
|---|---|---|---|---|
| PL1 | GitHub de la empresa | TuOpinas | Settings | cumple · 2026-11-10 |
| PL2 | Dos personas | Una | People | no cumple · 2026-11-12 |
| PL3 | Dominio | | Registrador | no aplica |
| PL4 | Release | | Entornos | excepción |
| PL5 | Secretos | | Gestor | |

## Cambios aprobados
| Fecha | Qué cambió | Aprobó |
|---|---|---|
| 2026-11-12 | Se quitó un owner | Juanjo Jiménez-Alfaro |
"""

REPOSITORIOS = """# Configuración de repositorios

| # | Qué se cumple | Cómo se comprueba | TuOpinas/memoria | decisionbits/work-memory |
|---|---|---|---|---|
| R1 | Nada a main | Rules | cumple · 2026-11-01 | cumple · 2026-11-15 |
| R4 | Migraciones | Seguimiento | no aplica | cumple · 2026-11-15 |
| R7 | CLAUDE.md | El archivo | listo | cumple |
"""


class Configuration(unittest.TestCase):
    def test_platform(self):
        c = dev.leer_configuracion(PLATAFORMA)
        self.assertEqual(c.kind, "plataforma")
        self.assertEqual([r.id for r in c.rows], ["PL1", "PL2", "PL3", "PL4", "PL5"])
        self.assertEqual(c.rows[0].states["Estado"], {"estado": "cumple", "fecha": "2026-11-10", "texto": "cumple · 2026-11-10"})
        self.assertEqual(c.rows[2].states["Estado"]["estado"], "no aplica")
        self.assertEqual(c.rows[3].states["Estado"]["estado"], "excepción")
        self.assertIsNone(c.rows[4].states["Estado"])
        self.assertEqual(c.latest, "2026-11-12")
        self.assertEqual(c.changes[0].approved_by, "Juanjo Jiménez-Alfaro")
        self.assertEqual((c.missing, c.warnings), ([], []))

    def test_repositories(self):
        c = dev.read_configuration(REPOSITORIOS)
        self.assertEqual(c.kind, "repositorios")
        self.assertEqual(c.columns, ["TuOpinas/memoria", "decisionbits/work-memory"])
        self.assertEqual(c.rows[0].states["decisionbits/work-memory"]["fecha"], "2026-11-15")
        self.assertEqual(c.latest, "2026-11-15")
        self.assertTrue(any("listo" in w for w in c.warnings))
        self.assertTrue(any("sin fecha" in w for w in c.warnings))

    def test_oldest_and_unchecked(self):
        c = dev.leer_configuracion(PLATAFORMA)
        self.assertEqual(c.oldest, "2026-11-10")
        self.assertEqual(c.unchecked, ["PL5"])
        r = dev.read_configuration(REPOSITORIOS)
        self.assertEqual(r.oldest, "2026-11-01")

    def test_empty_changes_section_at_the_end(self):
        # an empty «Cambios aprobados» used to remove every line break (review of 1.27.0, finding 26)
        text = PLATAFORMA.split("## Cambios aprobados")[0] + "## Cambios aprobados\n\n"
        c = dev.read_configuration(text)
        self.assertEqual((c.kind, len(c.rows)), ("plataforma", 5))

    def test_missing(self):
        self.assertIn("sección Cambios aprobados", dev.read_configuration(PLATAFORMA.split("## Cambios")[0]).missing)
        self.assertEqual(dev.read_configuration("# Nada\n\nSin tabla.\n").missing, ["tabla con la columna #"])
        self.assertIn("columna Cómo se comprueba",
                      dev.read_configuration(PLATAFORMA.replace("Cómo se comprueba", "Cómo")).missing)


class Status(unittest.TestCase):
    PLAN = dev.read_plan(PLAN)
    REPO = "TuOpinas/memoria"

    def status(self, prs, delivered=None):
        r = dev.estado_piezas(self.PLAN, prs, delivered)
        return {p.id: p.status for p in r.pieces}, r

    def pr(self, n, title, state, **kw):
        return PR(repo=kw.pop("repo", self.REPO), number=n, title=title, state=state, **kw)

    def test_rule(self):
        cases = [
            ("sin pull requests", [], None, {"P01": "pendiente", "P02": "pendiente", "P03": "pendiente"}),
            ("uno abierto", [self.pr(1, "P01 · tablas", "open")], None, {"P01": "en curso"}),
            ("todos unidos", [self.pr(1, "P01 · a", "merged"), self.pr(2, "P01 · b", "merged")], None, {"P01": "unida"}),
            ("manda el menos avanzado", [self.pr(1, "P01 · a", "merged"), self.pr(2, "P01 · b", "open")], None,
             {"P01": "en curso"}),
            ("cerrado sin unir no cuenta", [self.pr(1, "P01 · a", "closed")], None, {"P01": "pendiente"}),
            ("entregada solo con todos dentro", [self.pr(1, "P01 · a", "merged"), self.pr(2, "P01 · b", "merged")],
             {self.REPO: [1]}, {"P01": "unida"}),
            ("entregada", [self.pr(1, "P01 · a", "merged"), self.pr(2, "P01 · b", "merged")], {self.REPO: [1, 2]},
             {"P01": "entregada"}),
            ("el paso a Prod de otro repositorio no cuenta", [self.pr(1, "P01 · a", "merged")], {"decisionbits/work-memory": [1]},
             {"P01": "unida"}),
            ("un arreglo lleva su pieza", [self.pr(1, "P02 · a", "merged"), self.pr(2, "P02 · arreglo de a", "open")], None,
             {"P02": "en curso"}),
            ("un revert de GitHub lleva su pieza", [self.pr(1, "P03 · a", "merged"), self.pr(2, 'Revert "P03 · a"', "open")],
             None, {"P03": "en curso"}),
            ("identificador sin importar mayúsculas", [self.pr(1, "p01 · a", "open")], None, {"P01": "en curso"}),
            ("un bloque con varias piezas", [self.pr(1, "P01 + P02 · bloque", "merged")], {self.REPO: [1]},
             {"P01": "entregada", "P02": "entregada", "P03": "pendiente"}),
            ("solo cuentan los de la rama principal", [self.pr(1, "P01 · a", "merged"), self.pr(2, "P01 · paso interno", "open", to_main=False)],
             None, {"P01": "unida"}),
        ]
        for name, prs, delivered, want in cases:
            with self.subTest(name):
                got, _ = self.status(prs, delivered)
                for k, v in want.items():
                    self.assertEqual(got[k], v)

    def test_a_revert_merged_last_undoes_the_piece(self):
        r = dev.estado_piezas(self.PLAN, [self.pr(1, "P01 · a", "merged", merged_at="2026-11-01T10:00:00Z"),
                                          self.pr(2, 'Revert "P01 · a"', "merged", merged_at="2026-11-05T10:00:00Z")], {self.REPO: [1, 2]})
        self.assertEqual((r.pieces[0].status, r.pieces[0].reverted), ("en curso", True))
        r = dev.estado_piezas(self.PLAN, [self.pr(2, 'Revert "P01 · a"', "merged", merged_at="2026-11-05T10:00:00Z"),
                                          self.pr(3, "P01 · otra vez", "merged", merged_at="2026-11-07T10:00:00Z")], {self.REPO: [2, 3]})
        self.assertEqual((r.pieces[0].status, r.pieces[0].reverted), ("entregada", False))

    def test_reverting_a_revert_puts_the_piece_back(self):
        r = dev.estado_piezas(self.PLAN, [self.pr(1, "P01 · a", "merged", merged_at="2026-11-01T10:00:00Z"),
                                          self.pr(2, 'Revert "P01 · a"', "merged", merged_at="2026-11-05T10:00:00Z"),
                                          self.pr(3, 'Revert "Revert "P01 · a""', "merged", merged_at="2026-11-07T10:00:00Z")], {self.REPO: [1, 2, 3]})
        self.assertEqual((r.pieces[0].status, r.pieces[0].reverted, r.pieces[0].pull_requests),
                         ("entregada", False, ["TuOpinas/memoria#1", "TuOpinas/memoria#2", "TuOpinas/memoria#3"]))
        self.assertEqual(r.outside_plan, [])

    def test_outside_plan_and_bots(self):
        _, r = self.status([
            self.pr(1, "Arregla el README", "merged"),
            self.pr(2, "P09 · algo que no está", "open"),
            self.pr(3, "P01· pegado", "open"),
            self.pr(4, "Bump actions/checkout", "merged", author="dependabot[bot]"),
            self.pr(5, "Otra cosa", "open", author="renovate", bot=True),
            self.pr(6, "Sin pieza y cerrado", "closed"),
            self.pr(7, "P01 + P09 · bloque con una que no está", "open"),
            self.pr(8, "Sin pieza, a una rama intermedia", "merged", to_main=False),
        ])
        self.assertEqual([p.number for p in r.outside_plan], [1, 2, 3, 7])
        self.assertEqual(sorted(p.number for p in r.ignored), [4, 5, 6, 8])
        self.assertTrue(all(p.status == "pendiente" for p in r.pieces))

    def test_reports_pull_requests_and_plain_dicts(self):
        _, r = self.status([self.pr(7, "P02 · a", "merged", repo="decisionbits/work-memory")])
        self.assertEqual(r.pieces[1].pull_requests, ["decisionbits/work-memory#7"])
        d = dev.as_dict(r)
        self.assertEqual(d["pieces"][1]["status"], "unida")


if __name__ == "__main__":
    unittest.main()


class FollowUpEntriesTest(unittest.TestCase):
    def test_real_watched_design(self):
        t = ("---\nestado: vigente\n---\n\n# Seguimiento\n\n## 2026-11-15 · nota\nmirar\n\n"
             "## 2026-11-10 · pidió Ana\nLeído: acme/app en `abcdef1` (main), desde el 2026-11-01.\nComparó: piezas, reglas.\n\n"
             "**Rompe las reglas:** nada. Un commit dice «**Rompe las reglas:** sin vigilar».\n\n"
             "## 2026-11-01 · pidió Ana\nLeído: acme/app en `1234567` (main), desde el 2026-10-01.\nComparó: piezas, diseño, reglas.\n\n"
             "**Rompe las reglas:** sin vigilar: no se leyeron enteros los pasos a Prod.\n")
        e = dev.follow_up_entries(t)
        self.assertEqual([x["date"] for x in e], ["2026-11-10", "2026-11-01"])
        self.assertEqual([(x["watched"], x["design"]) for x in e], [(True, False), (False, True)])
        self.assertEqual(e[0]["repos"], ["acme/app"])
