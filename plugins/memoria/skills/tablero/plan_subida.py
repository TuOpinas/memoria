#!/usr/bin/env python3
"""Qué hay que subir a la base del tablero, sin traer ningún documento a la conversación.

Uso: plan_subida.py <salida-del-generador> <volcado-de-la-base> [--max-bytes 900000]
     plan_subida.py --guardada <volcado-de-la-base> --version <versión del plugin> [--tarea <id>] [--manual]

Con --guardada no planea nada: imprime la huella de la raíz que guardó la última puesta al día si el tablero
sigue valiendo tal cual (misma versión del plugin, misma tarea, mismo «sin horario»), o «-» si hay que regenerar.

<volcado-de-la-base> es la carpeta donde ArtifactData dejó, con out_dir, lo que hay hoy en la base
(<volcado>/areas/*.json, <volcado>/proyectos/*.json, <volcado>/meta/estado.json).
Compara huellas e imprime un JSON con:
  «lotes»: listas de escrituras, cada una de menos de --max-bytes y de 50 entradas como mucho, con
           {op, collection, doc_id, file_path, existe}. «existe» dice si el documento ya está en la base:
           esos llevan «if_version» con la versión que dio la lectura. meta/estado va siempre, como «update» (o «set» si la base está vacía).
  Los documentos de la base que ya no salen de la raíz van en los lotes como «delete» (con su if_version).
  «sin_cambios»: cuántos documentos no hace falta tocar; «borrados»: cuántos deletes hay en los lotes.
  «no_se_suben»: lo que la base rechazaría (un doc_id con espacios o acentos, un documento de más de 1 MB);
           se dice en el resumen, y el resto se sube igual.
No escribe nada.
"""
import sys, json, pathlib, re

if "--guardada" in sys.argv:
    def _a(n):
        return sys.argv[sys.argv.index(n) + 1] if n in sys.argv and len(sys.argv) > sys.argv.index(n) + 1 else None
    p = pathlib.Path(_a("--guardada")) / "meta" / "estado.json"
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        d = d.get("data", d) if isinstance(d, dict) else {}
    except (OSError, ValueError):
        d = {}
    tarea = _a("--tarea")
    vale = (bool(d.get("huella_raiz")) and d.get("version_tablero") == _a("--version")
            and (d.get("tarea") or None) == tarea and bool(d.get("tarea_manual")) == (bool(tarea) and "--manual" in sys.argv))
    print(d["huella_raiz"] if vale else "-")
    sys.exit(0)

SALIDA = pathlib.Path(sys.argv[1]).resolve()
VOLCADO = pathlib.Path(sys.argv[2]).resolve()
MAX = int(sys.argv[sys.argv.index("--max-bytes") + 1]) if "--max-bytes" in sys.argv else 900_000
COLECCIONES = ("areas", "proyectos")   # las que regenera el generador entero; «cambios» y «enfoque» no se tocan aquí
ID_VALIDO = re.compile(r"^(?!\.\.?$)[A-Za-z0-9_\-.~:@+]{1,200}$")   # lo que la base admite como doc_id
LIMITE = 1_000_000                                                    # un documento solo no puede pasar del cuerpo de un lote


def huella_en_base(col, doc):
    p = VOLCADO / col / f"{doc}.json"
    if not p.exists():
        return None, False
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, True
    d = d.get("data", d) if isinstance(d, dict) else {}
    return d.get("huella"), True


indice = json.loads((SALIDA / "indice.json").read_text(encoding="utf-8"))
escrituras, sin_cambios, salen, invalidos, grandes = [], 0, set(), [], []
for it in indice:
    col, doc = it["coleccion"], it["doc_id"]
    salen.add((col, doc))
    if not ID_VALIDO.match(doc):
        invalidos.append(f"{col}/{doc}"); continue      # carpeta con espacios o acentos: la base no la admite
    if it["bytes"] > LIMITE:
        grandes.append(f"{col}/{doc}"); continue
    h, existe = huella_en_base(col, doc)
    es_meta = (col, doc) == ("meta", "estado")
    if not es_meta and existe and h == it["huella"]:
        sin_cambios += 1
        continue
    escrituras.append({"op": "update" if (es_meta and existe) else "set", "collection": col, "doc_id": doc,
                       "file_path": str(SALIDA / it["archivo"]), "existe": existe, "bytes": it["bytes"]})

borrar = []
for col in COLECCIONES:
    d = VOLCADO / col
    for p in sorted(d.glob("*.json")) if d.exists() else []:
        if (col, p.stem) not in salen and ID_VALIDO.match(p.stem):
            borrar.append({"op": "delete", "collection": col, "doc_id": p.stem})

# meta/estado va el último: lleva la huella de la raíz, y si un lote anterior falla, la siguiente
# puesta al día no debe creer que el tablero ya estaba al día
_meta = [e for e in escrituras if (e["collection"], e["doc_id"]) == ("meta", "estado")]
orden = [e for e in escrituras if e not in _meta] + borrar + _meta
lotes, actual, peso = [], [], 0
for e in orden:
    b = e.get("bytes", 200) + 300
    if actual and (peso + b > MAX or len(actual) >= 50):
        lotes.append(actual); actual, peso = [], 0
    actual.append({k: v for k, v in e.items() if k != "bytes"})
    peso += b
if actual:
    lotes.append(actual)

print(json.dumps({"lotes": lotes, "sin_cambios": sin_cambios, "borrados": len(borrar),
                  "no_se_suben": {"id_no_valido": invalidos, "demasiado_grandes": grandes}}, ensure_ascii=False, indent=1))
