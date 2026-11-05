"""Language packs: a root is read with the pack of its language. A root whose reserved folders and files are renamed,
read with a pack that names them so, gives the same records (decision of 2026-11-05: reserved names follow the root's
language). The test pack renames only folders and files; spellings inside the files stay Spanish."""
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
    def test_unknown_language_is_spanish(self):
        self.assertIs(language.pack(None), language.ES)
        self.assertIs(language.pack("xx"), language.ES)
        self.assertEqual(load_root(ROOT, "xx").language, "es")

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


if __name__ == "__main__":
    unittest.main()
