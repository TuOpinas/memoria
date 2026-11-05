"""context-core: the Memoria method as records.

The method's files keep their Spanish names and keys (`estado`, `Afecta a`, `Siguientes pasos`) until the language
packs; this package reads them as they are and names them in English inside the code (decision of 2026-11-04).

- `records`: the record model, the types every caller works on.
- `parse`: text of one method file -> records. Pure functions, no I/O.
- `load`: a whole root -> `Root`. Reads through a storage adapter (step 0, task 2); for now, a folder on disk.
"""
from .records import (  # noqa: F401
    Person, PeopleRegistry, AreaRow, Premise, Status, DecisionRef,
    Decision, SessionEntry, Step, Deliverable, WorkshopFile, IndexEntry,
    Project, Area, Root,
)
