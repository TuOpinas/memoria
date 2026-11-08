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
| `context_core/load.py` | A root to a `Root`, through the storage adapter, never reading `restringido/`, `fuentes/` or restricted areas. By level: the guide, the premises and the open areas always; projects and their parts (`PARTS`, `PUBLIC`, `REGISTERS`) only when asked. Decisions with this year's and last year's archives, so ids are counted over the merged register; sessions without their bodies unless asked, and with their archives only on request. `load_public` is what a reader outside a session gets, with every reference cut at a restricted zone |
| `context_core/views.py` | What a reader may be served of a loaded root: the challenge index (each challenge with what answers it, in any project or archive) and references cut at the edge of a restricted zone |
| `context_core/write.py` | Writing the method's files: the text changes every writer applies (the header's `actualizado`, a register entry on top, a whole «## » block), moved from `cerrar.py` with the same results; and the entries a writer composes from fields (session, decision, Estatus), each field checked so it cannot carry a heading, a line break of another kind, a line a reader would take for another field, or Markdown that would hide or reshape the file when rendered; and the rotation of the registers (whether to archive, the archive's name and text, the live register that stays), moved from `cerrar.py` in 1.26. The plugin's `cerrar.py` and the hosted server call the same functions |
| `context_core/minimum.py` | The minimum plugin version a root declares in guia.md (1.26): the section found tolerantly and read strictly, so an error closes writing and never opens it; the structure's own minimum (`STRUCTURE_MINIMUM`), the update recipe and the section the migration writes. Its own module, so only the five scripts that gate writing carry it |
| `context_core/compat.py` | The scripts' Spanish names and dict shapes over the package, while they move; retires with the language packs |
| `schema/records.sql` | The record model as PostgreSQL tables with row-level security per organization; unused until step 2 |
| `inline.py` | Puts what each script imports, and what that imports, inside the eight plugin scripts that use the package (language, records, rules and compat in all of them; `write` only in `cerrar.py`), so each runs when downloaded alone, with a fingerprint per module: a script stops if another version of the package is already loaded in its process; `--check` in CI and `release.sh` |

The method's files keep their Spanish names and keys; the code names them in English.

## Tests

From the repository root:

    python3 -m unittest discover -s packages/context-core/tests

`test_records.py` builds the model from `pruebas/tablero/raiz` in its 1.21, 1.22 and 1.25 forms; `test_parity.py`
compares the parsers with `generar_vista.py`'s; `test_compat.py` compares `compat` with the 1.25.1 rules frozen in
`tests/reference/`, and `test_access.py` the area access rule with abrir.py's 1.25.1 reading and its frozen cases;
`test_language.py` reads a root with renamed reserved names, and one whose area table and restricted words are in
another (made-up) language, through test packs; `test_rotation.py` checks the rotation against cerrar.py 1.25.8's and `test_minimum.py` the minimum plugin version, mistyped headings included; `test_write.py` checks the text changes against cerrar.py 1.25.4's, frozen in `tests/reference/`, and that the
entries composed from fields read back the same and refuse forged lines; `test_inline.py` checks what goes into the scripts and that a script
refuses another version of the package; `test_schema.py` checks every record field has a column and every table
row-level security; `test_old_python.py` checks the package parses as Python 3.9. CI runs them on 3.9, 3.10 and the
current Python.

## Not yet in the package

the `fuentes/` inventory,
«Claude outputs», the header of `base/contexto.md`, the fields of «Quién es quién» in the language pack, and the
scripts' operations themselves (opening, closing, the board's generator), which move one by one as step 1
builds each server tool.
