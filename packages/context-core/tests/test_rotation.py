"""context_core.write's rotation does what cerrar.py 1.25.8's did (frozen in tests/reference/cerrar_1_25_8_rotacion.py):
the same reason and archive name, the same archive text and the same live register, on the registers of the test root
and on the cases the plugin's tests cover (by size, by year, a second archive of the same year, an archive already there,
one given back halfway, a register without a header, an «Archivado:» line naming archives the copy does not have)."""
import os, pathlib, re, shutil, sys, tempfile, unittest

CORE = pathlib.Path(__file__).resolve().parents[1]
REPO = CORE.parent.parent
sys.path.insert(0, str(CORE))

from context_core import write  # noqa: E402

ROOT = REPO / "pruebas" / "tablero" / "raiz"
REF = pathlib.Path(__file__).resolve().parent / "reference" / "cerrar_1_25_8_rotacion.py"


class _Lock:
    def __init__(self, p):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _leer(p):
    b = p.read_bytes()
    t = b.decode("utf-8-sig")
    return t.replace("\r\n", "\n"), (os.stat(p).st_mtime_ns, len(b)), b"\r\n" in b


def _escribir(p, texto, crlf):
    p.write_text(texto.replace("\n", "\r\n") if crlf else texto, encoding="utf-8", newline="")
    return os.stat(p).st_mtime_ns


OLD = {"leer": _leer, "escribir": _escribir, "igual": lambda p, firma: True, "Cerrojo": _Lock}
exec(REF.read_text(encoding="utf-8"), OLD)
REASONS = {"lines": f"pasa de {write.ROTATE_LINES} líneas", "bytes": f"pasa de {write.ROTATE_BYTES // 1000} KB",
           "year": "cambió el año"}

DEC = "## {d} · Decisión {i}\nDecidió: Ana Prueba\nPor qué: {why}\n"
BIG = "---\nestado: vigente\nactualizado: 2026-03-01\n---\n# Decisiones\n\n" + "\n".join(
    DEC.format(d="2026-03-01", i=i, why="x" * 400) for i in range(300))
LONG = "# Bitácora\n\n" + "\n".join(f"## 2026-02-{1 + i % 27:02d}\nTema: t\nAvances: a\nb\nc\nd\n" for i in range(300))
OLD_YEAR = "---\nestado: vigente\nactualizado: 2025-12-30\n---\n# Bitácora\n\n## 2025-12-30\nTema: fin de año\nAvances: x\n"
NO_HEADER = "# Decisiones\n\n" + "\n".join(DEC.format(d="2026-01-05", i=i, why="y" * 400) for i in range(300))
NAMED = BIG.replace("# Decisiones\n\n", "# Decisiones\n\nArchivado: decisiones-2019.md.\n\n", 1)
SMALL = "# Decisiones\n\n## 2026-05-01 · Una\nDecidió: Ana\nPor qué: x\n"
UNDATED = "# Notas\n\n## Algo\n" + "z" * 120_000


def cases():
    """(name, register, text, files already in the folder, by_year, today)."""
    yield "big", "decisiones", BIG, {}, True, "2026-11-08"
    yield "long", "sesiones", LONG, {}, True, "2026-11-08"
    yield "year", "sesiones", OLD_YEAR, {}, True, "2026-01-02"
    yield "year not asked", "sesiones", OLD_YEAR, {}, False, "2026-01-02"
    yield "second of the year", "decisiones", BIG, {"decisiones-2026.md": "# otro\n\n## 2026-01-01 · Otra\nDecidió: X\n"}, True, "2026-11-08"
    yield "already there", "decisiones", BIG, {"decisiones-2026.md": BIG}, True, "2026-11-08"
    extra = "## 2026-11-08 · Llegó después\nDecidió: Beto\nPor qué: x.\n\n"
    yield "given back halfway", "decisiones", BIG.replace("# Decisiones\n\n", "# Decisiones\n\n" + extra, 1), {"decisiones-2026.md": BIG}, True, "2026-11-08"
    yield "no header, a hand-made archive", "decisiones", NO_HEADER, {"decisiones-2025.md": "# viejo\n"}, True, "2026-11-08"
    yield "names archives the copy lacks", "decisiones", NAMED, {}, True, "2026-11-08"
    yield "small", "decisiones", SMALL, {}, True, "2026-11-08"
    yield "undated", "decisiones", UNDATED, {}, True, "2026-11-08"
    for p in sorted(ROOT.rglob("*.md")):
        if p.name in ("sesiones.md", "decisiones.md") and "restringido" not in p.parts:
            yield str(p.relative_to(ROOT)), p.stem, p.read_text(encoding="utf-8"), {}, True, "2027-01-04"


class SameAs1258(unittest.TestCase):
    def test_reason(self):
        for name, reg, text, _, by_year, today in cases():
            with self.subTest(name):
                old = OLD["motivo_rotacion"](text, today, by_year)
                new = write.rotation_reason(text, today, by_year)
                self.assertEqual(old, (REASONS[new[0]], new[1]) if new else None)

    def test_same_files(self):
        for name, reg, text, files, by_year, today in cases():
            with self.subTest(name):
                got = []
                for side in ("old", "new"):
                    d = pathlib.Path(tempfile.mkdtemp())
                    try:
                        for n, t in files.items():
                            (d / n).write_text(t, encoding="utf-8")
                        (d / f"{reg}.md").write_text(text, encoding="utf-8")
                        if side == "old":
                            r = OLD["Rotador"](d, today)
                            r.rotar(d / f"{reg}.md", reg, by_year)
                        else:
                            plan = write.plan_rotation(text, reg, today, [x.name for x in d.iterdir()],
                                                       lambda n: (d / n).read_text(encoding="utf-8"), by_year)
                            if plan:
                                if plan.archive_text is not None:
                                    self.assertFalse((d / plan.archive).exists(), "never over an existing archive")
                                    (d / plan.archive).write_text(plan.archive_text, encoding="utf-8")
                                (d / f"{reg}.md").write_text(plan.live, encoding="utf-8")
                        got.append({x.name: x.read_text(encoding="utf-8") for x in d.iterdir()})
                    finally:
                        shutil.rmtree(d)
                self.assertEqual(got[0], got[1])

    def test_plan_fields(self):
        plan = write.plan_rotation(BIG, "decisiones", "2026-11-08", ["decisiones-2026.md"], lambda n: "# otro\n")
        self.assertEqual((plan.reason, plan.year, plan.archive, plan.entries), ("bytes", "2026", "decisiones-2026-2.md", 300))
        self.assertIn("Archivado: decisiones-2026.md, decisiones-2026-2.md.", plan.live)
        again = write.plan_rotation(BIG, "decisiones", "2026-11-08", ["decisiones-2026.md"], lambda n: BIG)
        self.assertIsNone(again.archive_text)
        self.assertEqual(again.archive, "decisiones-2026.md")


class RenderGuard(unittest.TestCase):
    def test_refused(self):
        for bad in ("<!-- oculto", "fin -->", "```", "~~~ py", "===", "--", "<script>x</script>", "<b>", "a\n----"):
            with self.subTest(bad):
                with self.assertRaises(write.FieldError):
                    write.text_field(bad, "progress", "sessions")
                if "\n" not in bad:
                    with self.assertRaises(write.FieldError):
                        write.one_line(bad, "topic")

    def test_allowed(self):
        for good in ("a < b y c > d", "1 - 2", "flecha -> derecha", "un `código` corto", "x = y", "--forzar ruta",
                     "se añadió `List<String>`", "usa `<correo>` en la línea"):
            with self.subTest(good):
                self.assertEqual(write.one_line(good, "topic"), good)


if __name__ == "__main__":
    unittest.main()
