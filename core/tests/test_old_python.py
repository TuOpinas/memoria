"""The package runs inside the plugin scripts on each person's computer, with their Python (3.9 on a Mac): the modules
are inlined as strings, so pruebas/probar_compila.py does not see them. They must parse as 3.9 and use nothing newer."""
import ast, pathlib, unittest

PKG = pathlib.Path(__file__).resolve().parents[1] / "memoria_core"
NEWER = ("match ", "kw_only=", "slots=True", "zip(strict", "removeprefix", "TypeAlias", "ParamSpec")


class OldPython(unittest.TestCase):
    def test_parses_as_39(self):
        for f in sorted(PKG.glob("*.py")):
            src = f.read_text(encoding="utf-8")
            with self.subTest(module=f.name):
                ast.parse(src, feature_version=(3, 9))
                self.assertTrue(f.name == "__init__.py" or "from __future__ import annotations" in src)
                self.assertEqual([n for n in NEWER if n in src], [])


if __name__ == "__main__":
    unittest.main()
