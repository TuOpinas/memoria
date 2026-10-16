#!/usr/bin/env python3
"""Qué hay que subir a la base del tablero, sin traer ningún documento a la conversación.

Uso: plan_subida.py <salida-del-generador> <volcado-de-la-base> [--max-bytes 900000]

<volcado-de-la-base> es la carpeta donde ArtifactData dejó, con out_dir, lo que hay hoy en la base
(<volcado>/areas/*.json, <volcado>/proyectos/*.json, <volcado>/meta/estado.json).
Compara huellas e imprime un JSON con:
  «lotes»: listas de escrituras, cada una de menos de --max-bytes y de 50 entradas como mucho, con
           {op, collection, doc_id, file_path, existe}. «existe» dice si el documento ya está en la base:
           esos llevan «if_version» con la versión que dio la lectura. meta/estado va siempre, como «update».
  «borrar»: documentos de la base que ya no salen de la raíz (delete, con su if_version).
  «sin_cambios»: cuántos documentos no hace falta tocar.
No escribe nada.
"""
import sys, json, pathlib

SALIDA = pathlib.Path(sys.argv[1]).resolve()
VOLCADO = pathlib.Path(sys.argv[2]).resolve()
MAX = int(sys.argv[sys.argv.index("--max-bytes") + 1]) if "--max-bytes" in sys.argv else 900_000
COLECCIONES = ("areas", "proyectos")   # las que regenera el generador entero; «cambios» y «enfoque» no se tocan aquí


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
escrituras, sin_cambios, salen = [], 0, set()
for it in indice:
    col, doc = it["coleccion"], it["doc_id"]
    salen.add((col, doc))
    h, existe = huella_en_base(col, doc)
    es_meta = (col, doc) == ("meta", "estado")
    if not es_meta and existe and h == it["huella"]:
        sin_cambios += 1
        continue
    escrituras.append({"op": "update" if es_meta else "set", "collection": col, "doc_id": doc,
                       "file_path": str(SALIDA / it["archivo"]), "existe": existe, "bytes": it["bytes"]})

borrar = []
for col in COLECCIONES:
    d = VOLCADO / col
    for p in sorted(d.glob("*.json")) if d.exists() else []:
        if (col, p.stem) not in salen:
            borrar.append({"op": "delete", "collection": col, "doc_id": p.stem})

# lotes por tamaño: el cuerpo de un lote no puede pasar de 1 MiB
lotes, actual, peso = [], [], 0
for e in escrituras + borrar:
    b = e.get("bytes", 200) + 300
    if actual and (peso + b > MAX or len(actual) >= 50):
        lotes.append(actual); actual, peso = [], 0
    actual.append({k: v for k, v in e.items() if k != "bytes"})
    peso += b
if actual:
    lotes.append(actual)

print(json.dumps({"lotes": lotes, "borrar": [{"collection": e["collection"], "doc_id": e["doc_id"]} for e in borrar],
                  "sin_cambios": sin_cambios}, ensure_ascii=False, indent=1))
