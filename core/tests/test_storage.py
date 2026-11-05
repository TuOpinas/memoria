"""The folder adapter keeps the three rules of storage.py: nothing outside the root, no delete, writes that fail on a
changed file. Same results from load_root through the adapter as before it (test_records covers the model)."""
import os, pathlib, sys, tempfile, unittest

CORE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CORE))

from memoria_core.storage import Conflict, FolderStorage, OutsideRoot, Storage  # noqa: E402


class Folder(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.root = self.tmp / "raiz"
        (self.root / "ventas").mkdir(parents=True)
        (self.root / "ventas" / "area.md").write_bytes("\ufeff# Ventas\r\n\r\nx\r\n".encode())
        (self.tmp / "fuera.md").write_text("secreto", encoding="utf-8")
        self.st = FolderStorage(self.root)

    def test_is_a_storage(self):
        self.assertIsInstance(self.st, Storage)

    def test_outside_the_root_fails(self):
        for p in ("/etc/passwd", "../fuera.md", "ventas/../../fuera.md", "C:/x", "..\\fuera.md"):
            with self.subTest(path=p), self.assertRaises(OutsideRoot):
                self.st.read(p)
        os.symlink(self.tmp / "fuera.md", self.root / "enlace.md")
        with self.assertRaises(OutsideRoot):
            self.st.read("enlace.md")

    def test_no_delete(self):
        self.assertFalse(any(hasattr(self.st, n) for n in ("delete", "remove", "unlink", "trash")))

    def test_read_normalizes_and_write_keeps_crlf(self):
        doc = self.st.read("ventas/area.md")
        self.assertEqual(doc.text, "# Ventas\n\nx\n")
        self.assertTrue(doc.crlf)
        self.st.write("ventas/area.md", doc.text + "y\n", expected=doc.version, crlf=doc.crlf)
        self.assertEqual((self.root / "ventas" / "area.md").read_bytes(), b"# Ventas\r\n\r\nx\r\ny\r\n")
        self.assertEqual([e.name for e in self.st.list("ventas")], ["area.md"])   # no temporary left behind

    def test_write_fails_on_a_changed_file(self):
        doc = self.st.read("ventas/area.md")
        (self.root / "ventas" / "area.md").write_text("otra persona escribió", encoding="utf-8")
        with self.assertRaises(Conflict):
            self.st.write("ventas/area.md", "mío", expected=doc.version)
        with self.assertRaises(Conflict):
            self.st.write("ventas/area.md", "mío", expected=None)      # it exists
        v = self.st.write("ventas/nuevo.md", "hola", expected=None)
        self.assertEqual(self.st.read("ventas/nuevo.md").version, v)

    def test_move_never_overwrites(self):
        self.st.write("ventas/a.md", "a", expected=None)
        self.st.write("ventas/b.md", "b", expected=None)
        with self.assertRaises(Conflict):
            self.st.move("ventas/a.md", "ventas/b.md")
        self.st.move("ventas/a.md", "ventas/archivo/a.md")
        self.assertEqual(self.st.read("ventas/archivo/a.md").text, "a")

    def test_lock(self):
        with self.st.lock("ventas"):
            pass


if __name__ == "__main__":
    unittest.main()
