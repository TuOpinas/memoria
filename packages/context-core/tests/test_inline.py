"""The region inline.py puts in the scripts: only what compat reaches, and never mixed with another version of the
package in the same process (review of 1.25.2, findings 4 and 6). Each case runs in its own Python process."""
import pathlib, shutil, subprocess, sys, tempfile, unittest

CORE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CORE))

import inline  # noqa: E402

SCRIPT = inline.SCRIPTS[1]   # cerrar.py; the region is the same in every script


def region_of(path=SCRIPT):
    t = path.read_text(encoding="utf-8")
    return t[t.index(inline.BEGIN):t.index(inline.END) + len(inline.END)]


def run(code, *path):
    env_path = ":".join(str(p) for p in path)
    # -S and a neutral cwd: neither an installed package nor the current directory may shadow the copy on PYTHONPATH
    r = subprocess.run([sys.executable, "-S", "-c", code], capture_output=True, text=True, cwd=tempfile.gettempdir(),
                       env={"PYTHONPATH": env_path, "PATH": "/usr/bin:/bin"})
    return r.returncode, r.stdout + r.stderr


class Region(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = pathlib.Path(tempfile.mkdtemp())
        cls.region = cls.tmp / "region.py"
        cls.region.write_text(region_of(), encoding="utf-8")

    def exec_region(self, path=None):
        return f"exec(open({str(path or self.region)!r}, encoding='utf-8').read(), {{'__file__': 'script.py'}})\n"

    def test_each_script_carries_what_it_imports(self):
        cerrar = (inline.PL / "skills/sesion/cerrar.py").read_text(encoding="utf-8")
        abrir = (inline.PL / "skills/sesion/abrir.py").read_text(encoding="utf-8")
        self.assertIn("write", inline.modules_for(cerrar))
        self.assertNotIn("write", inline.modules_for(abrir))     # only cerrar.py pays for the write module
        self.assertNotIn("'write': (", abrir)

    def test_only_what_compat_reaches(self):
        self.assertEqual(inline.MODULES, ["language", "records", "rules", "compat"])
        r = region_of()
        for m in ("parse", "load", "storage"):
            self.assertNotIn(f"'{m}': (", r)

    def test_alone_and_twice(self):
        code = self.exec_region() + self.exec_region() + "import context_core.compat as c; print(c.acceso_de('Restringidas'))"
        rc, out = run(code)
        self.assertEqual((rc, out.strip()), (0, "True"))

    def test_the_installed_package_when_it_is_the_same(self):
        code = "import context_core.compat as c0\n" + self.exec_region() + "import context_core.compat as c\nprint(c is c0)"
        rc, out = run(code, CORE)
        self.assertEqual((rc, out.strip()), (0, "True"))

    def test_another_version_already_loaded_fails(self):
        other = self.tmp / "other"
        shutil.copytree(CORE / "context_core", other / "context_core")
        with open(other / "context_core" / "rules.py", "a", encoding="utf-8") as f:
            f.write("\n# another version\n")
        rc, out = run("import context_core.compat\n" + self.exec_region(), other)
        self.assertNotEqual(rc, 0)
        self.assertIn("ImportError: context_core.rules is already loaded", out)
        self.assertIn("script.py", out)

    def test_another_region_already_loaded_fails(self):
        changed = self.tmp / "changed.py"
        changed.write_text(region_of().replace("    'compat': (\n", "    'compat': (\n        '# another version\\n'\n", 1)
                           .replace(inline.fingerprint((CORE / "context_core" / "compat.py").read_text(encoding="utf-8")),
                                    inline.fingerprint("# another version\n" + (CORE / "context_core" / "compat.py").read_text(encoding="utf-8"))),
                           encoding="utf-8")
        rc, out = run(self.exec_region(changed) + self.exec_region())
        self.assertNotEqual(rc, 0)
        self.assertIn("context_core.compat is already loaded", out)


if __name__ == "__main__":
    unittest.main()
