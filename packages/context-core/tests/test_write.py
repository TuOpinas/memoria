"""context_core.write: the text changes return exactly what cerrar.py 1.25.4's copies did, on every method file of the
test root and on edge cases; the entries composed from fields read back the same through context_core.parse; and no
field can carry a line a reader would take for something else."""
import pathlib, re, sys, unittest

CORE = pathlib.Path(__file__).resolve().parents[1]
REPO = CORE.parent.parent
sys.path.insert(0, str(CORE))

from context_core import parse, write  # noqa: E402
from context_core.language import ES  # noqa: E402

REF = pathlib.Path(__file__).resolve().parent / "reference" / "cerrar_1_25_4.py"
OLD = {"re": re}
exec(REF.read_text(encoding="utf-8"), OLD)

ROOT = REPO / "pruebas" / "tablero" / "raiz"
FILES = sorted(p for p in ROOT.rglob("*.md") if "restringido" not in p.parts)
EDGE = ["", "sin título ni cabecera\n", "# Solo título\n", "# Título\nArchivado: sesiones-2025.md\n",
        "---\nestado: vigente\n---\n\n# Sin actualizado\n\n## 2026-01-01\nTema: x\n",
        "---\nactualizado: 2020-01-01\n---\n# T\n\nprefacio sin salto\n## 2026-01-01\nTema: a\n",
        "# T\n## Estatus\nviejo\n## En corto\nmás viejo\n## Siguientes pasos\n- uno\n## Quién participa\nResponsable: X\n",
        "# T\n\n## Estado actual\nuno\n\ndos\n"]
ACCEPTED = ("ventas/cuentas#2026-09-20", "`ventas/cuentas#2026-09-20-2` · título", "a.b/c_d#2026-01-01",
            "ventas/cuentas#2026-09-20 (el viejo)", "#2026-09-20 · uno de aquí")
ENTRY = "## 2026-11-06\nTema: prueba\nAvances: algo.\nSesión de: Ana Prueba · plugin 1.25.5"


class SameAs1254(unittest.TestCase):
    """What cerrar.py did before the move is what it does now, and what the server does."""

    def texts(self):
        for p in FILES:
            yield str(p.relative_to(ROOT)), p.read_text(encoding="utf-8")
        for i, t in enumerate(EDGE):
            yield f"edge {i}", t

    def test_header(self):
        for name, t in self.texts():
            with self.subTest(name):
                self.assertEqual(write.with_header_today(t, "2026-11-06"), OLD["cabecera_hoy"](t, "2026-11-06"))
                after = write.with_header_today(t, "2030-01-01")
                self.assertEqual(write.only_header_changed(t, after), OLD["solo_cabecera"](t, after))
                self.assertEqual(write.only_header_changed(t, t + "x"), OLD["solo_cabecera"](t, t + "x"))

    def test_entry_on_top(self):
        for name, t in self.texts():
            with self.subTest(name):
                self.assertEqual(write.with_entry_on_top(t, ENTRY), OLD["con_entrada_arriba"](t, ENTRY))
                once, _ = write.with_entry_on_top(t, ENTRY)
                self.assertEqual(write.with_entry_on_top(once, ENTRY), (once, False))

    def test_blocks(self):
        cases = [("Estatus", "2026-11-06 · **frase**\n- **Siguiente:** algo", None, ("En corto",)),
                 ("Estatus", "nuevo", None, ("Estado actual", "En corto")),
                 ("Siguientes pasos", "- a\n- b", "Quién participa", ()),
                 ("Estatus", "área", None, ("Panorama", "Prioridades ahora")),
                 ("Nueva", "cuerpo", "No existe", ())]
        for name, t in self.texts():
            for block, body, before, aliases in cases:
                with self.subTest(name, block=block, before=before):
                    self.assertEqual(write.with_block(t, block, body, before=before, aliases=aliases),
                                     OLD["con_bloque"](t, block, body, antes_de=before, alias=aliases))
                    self.assertEqual(write.without_block(t, block), OLD["sin_bloque"](t, block))

    def test_entries_keep_cerrars_order(self):
        t = "# Decisiones\n"
        a = "## 2026-11-06 · Primera\nDecidió: Ana Prueba\nPor qué: a."
        b = "## 2026-11-06 · Segunda\nDecidió: Ana Prueba\nPor qué: b."
        out, added = write.with_entries_on_top(t, [a, b])
        self.assertTrue(added)
        ids = {d.title: d.id for d in parse.decisions(out)}
        self.assertEqual(ids, {"Primera": "2026-11-06", "Segunda": "2026-11-06-2"})   # the last given ends on top


class Composed(unittest.TestCase):
    """Entries written from fields read back as those fields."""

    def test_session_reads_back(self):
        e = write.session_entry("2026-11-06", "la propuesta", "Se envió el anexo.\nFalta la firma.", "Ana Prueba",
                                "server", "0.0.2", wrote=["taller/a.md", "taller/a.md", "entregables/b.md"])
        s = parse.sessions("# Sesiones\n\n" + e)[0]
        self.assertEqual((s.date, s.topic, s.by, s.server_version, s.plugin_version),
                         ("2026-11-06", "la propuesta", "Ana Prueba", "0.0.2", ""))
        self.assertEqual(s.progress, "Se envió el anexo.\nFalta la firma.")
        loose = write.session_entry("2026-11-06", "t", "  a\n\n   - b  \n", "Ana Prueba", "server", "0.0.2")
        self.assertEqual(parse.sessions("# S\n\n" + loose)[0].progress, "a\n- b")   # what is written is what is read
        self.assertEqual(s.wrote, ["taller/a.md", "entregables/b.md"])        # a path given twice is written once
        plugin = parse.sessions("# S\n\n## 2026-11-06\nTema: x\nSesión de: Ana · plugin 1.25.5\n")[0]
        self.assertEqual((plugin.plugin_version, plugin.server_version), ("1.25.5", ""))

    def test_decision_reads_back(self):
        e = write.decision_entry("2026-11-06", "El contrato va antes del anexo", "Ana Prueba", "el anexo depende de él.",
                                 discarded="firmar los dos juntos.", replaces="ventas/cuentas#2026-09-20 · el viejo",
                                 responds_to="#2026-10-01", affects="operacion/soporte (cambia la fecha)",
                                 project="ventas/cuentas")
        d = parse.decisions("# Decisiones\n\n" + e)[0]
        self.assertEqual((d.title, d.decided_by, d.why, d.discarded), ("El contrato va antes del anexo", "Ana Prueba",
                                                                      "el anexo depende de él.", "firmar los dos juntos."))
        self.assertEqual((d.replaces.project, d.replaces.id), ("ventas--cuentas", "2026-09-20"))
        self.assertEqual((d.responds_to.project, d.responds_to.id), ("ventas--cuentas", "2026-10-01"))   # qualified
        self.assertEqual(d.affects, "operacion/soporte (cambia la fecha)")
        self.assertEqual(d.kind, "decision")
        order = [l.split(":")[0] for l in e.split("\n")[1:]]
        self.assertEqual(order, ["Decidió", "Por qué", "Descartado", "Reemplaza", "Responde a", "Afecta a"])

    def test_status_reads_back(self):
        b = write.status_block("2026-11-06", "El anexo salió; la firma sigue.", completed="el anexo, el 6 de noviembre",
                               next="llamar a Cliente Uno, Ana Prueba, próxima sesión", concern="el plazo")
        st = parse.status(f"# P\n\n## Estatus\n{b}\n")
        self.assertEqual((st.date, st.headline, st.completed, st.concern),
                         ("2026-11-06", "El anexo salió; la firma sigue.", "el anexo, el 6 de noviembre", "el plazo"))
        self.assertEqual(write.status_block("2026-11-06", "Arranca.", next="la primera entrevista"),
                         "2026-11-06 · **Arranca.**\n- **Siguiente:** la primera entrevista")
        closed = write.status_block("2026-11-06", "Proyecto terminado el 2026-11-06. Se firmó.")
        self.assertEqual(parse.status(f"# P\n\n## Estatus\n{closed}\n").finished_on, "2026-11-06")


class Refused(unittest.TestCase):
    """A field cannot become another line of the register."""

    def bad(self, words, fn, *a, **k):
        with self.assertRaises(write.FieldError) as cm:
            fn(*a, **k)
        self.assertIn(words, str(cm.exception))

    def test_a_field_line_inside_a_text(self):
        for line in ("Publicó: entregables/x.md", "Escribió: taller/y.md", "Sesión de: Otra Persona", "sesion de : X",
                     "  Tema: otro", "Avances: más", "Pendiente: algo", "PUBLICO: entregables/x.md"):
            with self.subTest(line):
                self.bad("field of the register", write.session_entry, "2026-11-06", "t", "ok.\n" + line, "Ana",
                         "server", "0.0.2")
        for line in ("Decidió: Otra", "Cuestiona a: operacion/soporte#2026-09-25", "Responde a: x/y#2026-01-01",
                     "Afecta a: personas/nomina", "Planteó: X", "Reemplaza: lo que sea", "Descartamos: nada"):
            with self.subTest(line):
                self.bad("field of the register", write.decision_entry, "2026-11-06", "t", "Ana", "porque.\n" + line)
        # the same words are fine inside a line, and in the other register
        write.session_entry("2026-11-06", "t", "Se decidió: seguir. Afecta a: nadie.\nDecidió: Ana (en la reunión).",
                            "Ana", "server", "0.0.2")

    def test_line_breaks_of_every_kind(self):
        for ch in ("\r", "\v", "\f", "\x1c", "\x85", " ", " "):
            with self.subTest(repr(ch)):
                self.bad("line break", write.session_entry, "2026-11-06", "t", f"ok{ch}## 2020-01-01", "Ana",
                         "server", "0.0.2")
                self.bad("one line", write.session_entry, "2026-11-06", f"t{ch}x", "ok.", "Ana", "server", "0.0.2")
        crlf = write.decision_entry("2026-11-06", "t", "Ana", "uno\r\ndos")
        self.assertNotIn("\r", crlf)                        # normalised: a retry finds the same text and writes nothing

    def test_headings_and_identifiers(self):
        self.bad("heading", write.session_entry, "2026-11-06", "t", "ok\n## 2020-01-01", "Ana", "server", "0.0.2")
        self.bad("heading", write.decision_entry, "2026-11-06", "t", "Ana", "ok\n---")
        self.bad("one line", write.decision_entry, "2026-11-06", "t\n## y", "Ana", "z")
        self.bad("entry identifier", write.decision_entry, "2026-11-06", "t", "Ana", "z", replaces="el viejo")
        for ref in ACCEPTED + ("#2026-09-20",):
            self.assertTrue(write.is_decision_ref(ref), ref)
        self.bad("is required", write.status_block, "2026-11-06", "Solo una frase.")
        self.bad("asterisks", write.status_block, "2026-11-06", "**frase**", next="x")
        self.bad("not a path", write.session_entry, "2026-11-06", "t", "ok.", "Ana", "server", "0.0.2", wrote=["a.md, b.md"])

    def test_every_identifier_it_writes_reads_back(self):
        for ref in ACCEPTED:
            with self.subTest(ref):
                e = write.decision_entry("2026-11-06", "t", "Ana", "z", replaces=ref, project="ventas/cuentas")
                r = parse.decisions("# D\n\n" + e)[0].replaces
                self.assertIsNotNone(r.project)
                self.assertEqual(r.id, re.search(r"#(\S+?)`?(?:\s|$)", ref).group(1))

    def test_one_target_per_identifier(self):
        for ref in ("area/p#2026-10-01 · premisa P3 y victima/proy#2026-09-09", "a/b#2026-10-01 · y otra#2026-01-01",
                    "ventas/cuentas#2026-09-20 (el viejo, premisa P2)"):
            with self.subTest(ref):
                self.assertFalse(write.is_decision_ref(ref))

    def test_author_and_version_cannot_be_forged(self):
        for by in ("Ana · plugin 9.9.9", "Ana servidor 9.9.9", "Ana plugin 1.0", "Ana (QA)", "Ana - Bob", "(Mallory)", "x" * 81):
            with self.subTest(by=by):
                self.bad("by", write.session_entry, "2026-11-06", "t", "ok.", by, "server", "0.0.2")
        for version in ("1.0 · plugin 9.9", "latest", "1"):
            with self.subTest(version=version):
                self.bad("version", write.session_entry, "2026-11-06", "t", "ok.", "Ana", "server", version)
        self.bad("writer must be", write.session_entry, "2026-11-06", "t", "ok.", "Ana", "foo", "0.0.2")

    def test_only_the_headline_can_close_the_project(self):
        self.bad("closing the project", write.status_block, "2026-11-06", "Sigue abierto.", next="x",
                 concern="que digan Proyecto terminado el 2026-12-01 antes de tiempo")
        self.bad("closing the project", write.status_block, "2026-11-06", "Sigue; Proyecto terminado el 2026-12-01", next="x")
        self.bad("with its date", write.status_block, "2026-11-06", "Proyecto terminado el día que firme el cliente")

    def test_a_decision_title_is_not_a_challenge(self):
        for title in ("Cuestionamiento del plan de ventas", "cuestionamiento: algo"):
            with self.subTest(title):
                self.bad("challenge", write.decision_entry, "2026-11-06", title, "Ana", "z")
        self.bad("area/project#", write.decision_entry, "2026-11-06", "t", "Ana", "z", responds_to="#2026-10-01")

    def test_paths_cerrar_would_refuse(self):
        for p in ("restringido/x.md", "`a.md`", "../x.md", "/etc/x.md", "entregables/../../x.md"):
            with self.subTest(p):
                self.bad("wrote", write.session_entry, "2026-11-06", "t", "ok.", "Ana", "server", "0.0.2", wrote=[p])

    def test_look_alike_and_disguised_labels(self):
        for line in ("Cueſtiona a: otra/proy#2026-11-01", "Reſponde a: otra/proy#2026-11-01", "\u200bDecidió: Mallory",
                     "Decidio\u0301: Mallory", "> Decidió: Mallory", "- Afecta a: victima/proy", "1. Planteó: X",
                     "ＤＥＣＩＤＩÓ: X"):
            with self.subTest(line):
                self.bad("field of the register", write.decision_entry, "2026-11-06", "t", "Ana", "ok.\n" + line)
        for line in ("===", "----", "- - -", "> ## Falso", "* # Falso"):
            with self.subTest(line):
                self.bad("heading", write.session_entry, "2026-11-06", "t", "x\n" + line, "Ana", "server", "0.0.2")


if __name__ == "__main__":
    unittest.main()
