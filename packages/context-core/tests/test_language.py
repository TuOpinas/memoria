"""Language packs: a root is read with the pack of its language. A root whose reserved folders and files are renamed,
read with a pack that names them so, gives the same records (decision of 2026-11-05: reserved names follow the root's
language). The first test pack renames only folders and files; spellings inside the files stay Spanish. The second
spells the area table and the words that decide restricted in another (made-up) language: a restricted area of a root in
that language reads restricted (review of 1.25.2, finding 9)."""
import dataclasses, pathlib, shutil, sys, tempfile, unittest

CORE = pathlib.Path(__file__).resolve().parents[1]
REPO = CORE.parent.parent
sys.path[:0] = [str(CORE)]

from context_core import language  # noqa: E402
from context_core.load import load_root  # noqa: E402

ROOT = REPO / "pruebas" / "tablero" / "raiz"
NAMES = {"guide": "guide.md", "method": "method.md", "area_file": "overview.md", "project_file": "project.md",
         "decisions_file": "decisions.md", "sessions_file": "log.md", "base": "common", "premises_file": "premises.md",
         "deliverables": "deliverables", "workshop": "workshop", "sources": "sources", "restricted": "restricted"}


def summary(r):
    return [(a.slug, a.restricted, [(p.slug, p.restricted, len(p.decisions), len(p.sessions), len(p.steps),
                                     sorted(d.file for d in p.deliverables), sorted(w.path for w in p.workshop))
                                    for p in a.projects]) for a in r.areas], [x.id for x in r.premises]


class Packs(unittest.TestCase):
    def test_no_language_is_spanish_unknown_fails(self):
        self.assertIs(language.pack(None), language.ES)
        self.assertEqual(load_root(ROOT).language, "es")
        for code in ("xx", "en"):
            with self.subTest(code=code), self.assertRaises(ValueError):
                load_root(ROOT, code)

    def test_renamed_root_reads_the_same(self):
        test_pack = dataclasses.replace(language.ES, code="zz", **NAMES)
        es = language.ES
        dst = pathlib.Path(tempfile.mkdtemp()) / "raiz"
        shutil.copytree(ROOT, dst)
        renames = {getattr(es, k): v for k, v in NAMES.items()}
        for p in sorted(dst.rglob("*"), key=lambda x: -len(x.parts)):   # deepest first, so parents move last
            if p.name in renames:
                p.rename(p.with_name(renames[p.name]))
        language.PACKS["zz"] = test_pack
        try:
            self.assertEqual(summary(load_root(dst, "zz")), summary(load_root(ROOT)))
            self.assertNotEqual(summary(load_root(dst)), summary(load_root(ROOT)))   # the Spanish pack does not find them
        finally:
            del language.PACKS["zz"]

    def test_restricted_words_come_from_the_pack(self):
        words = dict(
            NAMES, code="zz", areas="Areas", projects="Projects",
            area_columns={"responsible": ("owner",), "account": ("account",), "readers": ("who reads",),
                          "access": ("access",), "what": ("what",)},
            people_columns={"responsible": ("owner",), "account": ("account",), "collaborates": ("collaborates",)},
            restricted_lead=r"restricted", open_lead=r"open", restricted_inline=r"restricted", restricted_stem="restrict",
            restricted_negations=("not", "never"), restricted_line=r"restricted")
        dst = pathlib.Path(tempfile.mkdtemp()) / "root"
        files = {
            "guide.md": "# Acme\n\n## Areas\n\n| Area | What | Owner | Account | Who reads | Access |\n|---|---|---|---|---|---|\n"
                        "| `sales/` | Sales | Ana | ana@x.test | Everyone | Open |\n"
                        "| `people/` | Payroll | Beto | beto@x.test | Beto | Restricted |\n"
                        "| `legal/` | Contracts | Ana | ana@x.test | The legal team (restricted) |  |\n"
                        "| `ops/` | Support | Ana | ana@x.test | Everyone, never restricted |  |\n",
            "sales/overview.md": "# Sales\n\n## Projects\n\n- `deals/` — open to all\n- `margins/` — restricted: owner Ana.\n",
            "sales/deals/project.md": "# Deals\n", "sales/margins/project.md": "# Margins\n",
            "people/overview.md": "# People\n\n## Projects\n\n- `payroll/` — salaries\n", "people/payroll/project.md": "# Payroll\n",
            "legal/overview.md": "# Legal\n", "ops/overview.md": "# Ops\n",
        }
        for rel, text in files.items():
            (dst / rel).parent.mkdir(parents=True, exist_ok=True)
            (dst / rel).write_text(text, encoding="utf-8")
        read = lambda p: {a.slug: (a.restricted, {x.slug: x.restricted for x in a.projects}) for a in load_root(dst, p).areas}
        language.PACKS["zz"] = dataclasses.replace(language.ES, **words)
        language.PACKS["zz-names-only"] = dataclasses.replace(language.ES, **dict(NAMES, code="zz-names-only", areas="Areas", projects="Projects"))
        try:
            self.assertEqual(read("zz"), {"sales": (False, {"deals": False, "margins": True}), "people": (True, {}),
                                          "legal": (True, {}), "ops": (False, {})})
            # with the Spanish words, the same root would read its restricted area open: the words are the pack's
            self.assertFalse(read("zz-names-only")["people"][0])
        finally:
            del language.PACKS["zz"], language.PACKS["zz-names-only"]


if __name__ == "__main__":
    unittest.main()
