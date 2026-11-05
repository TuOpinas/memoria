"""The package runs inside the plugin scripts on each person's computer, with their Python (3.9 on a Mac): the modules
are inlined as strings, so pruebas/probar_compila.py does not see them. They must parse as 3.9 and use nothing newer."""
import ast, pathlib, unittest

PKG = pathlib.Path(__file__).resolve().parents[1] / "context_core"
NEWER = ("match ", "kw_only=", "slots=True", "zip(strict", "removeprefix", "TypeAlias", "ParamSpec")


class OldPython(unittest.TestCase):
    def test_parses_as_39(self):
        for f in sorted(PKG.glob("*.py")):
            src = f.read_text(encoding="utf-8")
            with self.subTest(module=f.name):
                ast.parse(src, feature_version=(3, 9))
                self.assertTrue(f.name == "__init__.py" or "from __future__ import annotations" in src)
                self.assertEqual([n for n in NEWER if n in src], [])


class InlinedRegion(unittest.TestCase):
    """Python 3.9 misreads very long source lines with non-ASCII characters («Non-UTF-8 code»): the region inline.py
    writes into the scripts is short ASCII lines only (found by CI on 2026-11-05, in permisos.py)."""
    def test_region_is_short_ascii(self):
        import sys as _sys
        _sys.path.insert(0, str(PKG.parent))
        import inline
        for script in inline.SCRIPTS:
            t = script.read_text(encoding="utf-8")
            region = t[t.index(inline.BEGIN):t.index(inline.END)]
            with self.subTest(script=script.name):
                self.assertTrue(region.isascii())
                self.assertLess(max(len(l) for l in region.split("\n")), 1000)


if __name__ == "__main__":
    unittest.main()
