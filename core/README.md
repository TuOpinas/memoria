# memoria-core

The Memoria method as records: one Python package that the plugin scripts, the hosted server and the board will share
(step 0 of `shared-memory/product-design/entregables/hosted-path.md`). Python 3.10 or later, no dependencies.

- `memoria_core/records.py` — the record model: root, people, area rows, areas, projects, Estatus, decisions, sessions,
  steps, deliverables, workshop files, premises.
- `memoria_core/parse.py` — one method file's text to records. Pure functions, ported from the scripts with the same rules.
- `memoria_core/load.py` — a whole root to a `Root`. Reads a folder directly until the storage adapter lands.

The method's files keep their Spanish names and keys; the code names them in English.

## Tests

From the repository root:

    python3 -m unittest discover -s core/tests

`test_records.py` builds the model from `pruebas/tablero/raiz` in its 1.21, 1.22 and 1.25 forms; `test_parity.py`
runs the parsing functions of `generar_vista.py` and the package on the same files and fails on any difference.

## Not yet in the model

Archived `decisiones-AAAA.md` / `sesiones-AAAA.md`, the `fuentes/` inventory, «Claude outputs», the header of
`base/contexto.md`, and the sync inventory the board's two-step generator uses.
