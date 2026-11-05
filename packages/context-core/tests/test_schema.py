"""The first SQL schema covers the record model: every field of every stored record has a column, every tenant table
carries org_id, and every table, organization included, has row-level security. Parses the SQL with pglast when it is installed (it is not a dependency)."""
import dataclasses, pathlib, re, sys, unittest

CORE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CORE))

from context_core import records  # noqa: E402

SQL = (CORE / "schema" / "records.sql").read_text(encoding="utf-8")
TABLES = {"Root": "root", "Person": "person", "AreaRow": "area_row", "Premise": "premise", "Area": "area",
          "IndexEntry": "index_entry", "Project": "project", "Step": "step", "Decision": "decision",
          "SessionEntry": "session_entry", "Deliverable": "deliverable", "WorkshopFile": "workshop_file"}
# fields stored elsewhere: children in their own tables, the registry's lookups (derived), the area's own row
ELSEWHERE = {"Root": {"people", "area_rows", "areas", "premises"}, "Area": {"row", "index", "projects"},
             "Project": {"steps", "decisions", "sessions", "deliverables", "workshop", "index", "area"},
             "IndexEntry": set()}
RENAMED = {("SessionEntry", "by"): "by_name"}


def columns(table):
    m = re.search(rf"CREATE TABLE {table} \((.*?)\n\);", SQL, re.S)
    return {l.split()[0] for l in m.group(1).split("\n") if l.strip() and not l.strip().startswith(("--", "PRIMARY"))}


class Schema(unittest.TestCase):
    def test_every_field_has_a_column(self):
        for cls, table in TABLES.items():
            cols = columns(table)
            for f in dataclasses.fields(getattr(records, cls)):
                if f.name in ELSEWHERE.get(cls, set()):
                    continue
                with self.subTest(record=cls, field=f.name):
                    self.assertIn(RENAMED.get((cls, f.name), f.name), cols)

    def test_every_table_is_isolated(self):
        listed = re.search(r"ARRAY\[(.*?)\] LOOP", SQL, re.S).group(1)
        for table in TABLES.values():
            with self.subTest(table=table):
                self.assertIn("org_id", columns(table))
                self.assertIn(f"'{table}'", listed)
        self.assertIn("FORCE ROW LEVEL SECURITY", SQL)

    def test_no_table_without_isolation(self):
        """Every table the file creates is isolated: the tenant tables by org_id in the loop, organization by its id."""
        created = set(re.findall(r"^CREATE TABLE (\w+)", SQL, re.M))
        listed = set(re.findall(r"'(\w+)'", re.search(r"ARRAY\[(.*?)\] LOOP", SQL, re.S).group(1)))
        self.assertEqual(created - listed, {"organization"})
        self.assertRegex(SQL, r"ALTER TABLE organization FORCE ROW LEVEL SECURITY")
        self.assertRegex(SQL, r"CREATE POLICY tenant ON organization USING \(id = ")

    def test_parses(self):
        try:
            import pglast
        except ImportError:
            self.skipTest("pglast not installed")
        self.assertGreater(len(pglast.parse_sql(SQL)), 10)


if __name__ == "__main__":
    unittest.main()
