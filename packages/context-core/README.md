# context-core

The Memoria method as records: one Python package that the plugin scripts, the hosted server and the board share
(step 0 of `shared-memory/product-design/entregables/hosted-path.md`). Python 3.9 or later, no dependencies.

| Module | What it holds |
|---|---|
| `context_core/records.py` | The record model: root, people, area rows, areas, projects, Estatus, decisions, sessions, steps, deliverables, workshop files, premises |
| `context_core/language.py` | Language packs: how a root in one language names its reserved folders and files, sections, register fields and header keys, and the words that decide what is restricted. Spanish is the first pack; a root has one language (decision of 2026-11-05) |
| `context_core/rules.py` | The rules the plugin scripts already take from the package: who writes, whether an area or a cell is restricted (one rule for the opening, the board, permissions and the migration; `verificar.sh` reads only the «Acceso» word), guia.md's first paragraph, the archived registers. Pure functions |
| `context_core/parse.py` | One method file's text to records (decisions, sessions, Estatus, the area index, deliverables). Pure functions. Re-exports `rules`; the scripts still carry their own copy of these parsers, compared in `test_parity.py`, and move onto them in step 1 |
| `context_core/storage.py` | The storage adapter: read with a version, stat, list, write only if unchanged, make_dir, move without overwriting, lock. No delete; nothing outside the root. `FolderStorage` first |
| `context_core/load.py` | A whole root to a `Root`, through the storage adapter, never reading `restringido/`, `fuentes/` or restricted areas |
| `context_core/compat.py` | The scripts' Spanish names and dict shapes over the package, while they move; retires with the language packs |
| `schema/records.sql` | The record model as PostgreSQL tables with row-level security per organization; unused until step 2 |
| `inline.py` | Puts what `compat` reaches (language, records, rules, compat) inside the eight plugin scripts that use it, so each runs when downloaded alone, with a fingerprint per module: a script stops if another version of the package is already loaded in its process; `--check` in CI and `release.sh` |

The method's files keep their Spanish names and keys; the code names them in English.

## Tests

From the repository root:

    python3 -m unittest discover -s packages/context-core/tests

`test_records.py` builds the model from `pruebas/tablero/raiz` in its 1.21, 1.22 and 1.25 forms; `test_parity.py`
compares the parsers with `generar_vista.py`'s; `test_compat.py` compares `compat` with the 1.25.1 rules frozen in
`tests/reference/`, and `test_access.py` the area access rule with abrir.py's 1.25.1 reading and its frozen cases;
`test_language.py` reads a root with renamed reserved names, and one whose area table and restricted words are in
another (made-up) language, through test packs; `test_inline.py` checks what goes into the scripts and that a script
refuses another version of the package; `test_schema.py` checks every record field has a column and every table
row-level security; `test_old_python.py` checks the package parses as Python 3.9. CI runs them on 3.9, 3.10 and the
current Python.

## Not yet in the package

The archived registers inside `load_root` (the plugin's scripts read them through `compat`), the `fuentes/` inventory,
«Claude outputs», the header of `base/contexto.md`, the fields of «Quién es quién» in the language pack, and the
scripts' operations themselves (opening, closing, the board's generator), which move one by one as step 1
builds each server tool.
