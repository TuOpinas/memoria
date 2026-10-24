#!/usr/bin/env python3
"""Qué hay que subir a la base del tablero, sin traer ningún documento a la conversación.

Uso: plan_subida.py <salida-del-generador> <volcado-de-la-base> [--max-bytes 900000] [--cierres <volcado de «cierres»>]
                    [--inicio <trabajo>/inicio.json] [--llamadas <n>] [--pagina '<json de pagina_actualizada>']
                    [--tarea-desfasada true|false]
     plan_subida.py --guardada <volcado-de-la-base> --version <versión del plugin> [--tarea <id>] [--manual]
     plan_subida.py --cierre <volcado-de-la-base> <carpeta de salida> --sincronizado <instante que imprimió el inventario>
                    [--cierres …] [--inicio …] [--llamadas …] [--pagina …] [--tarea-desfasada …]
                    [--retenidos <retenidos.json>] [--ajenos <ajenos.json>]

Lo que cierra la puesta al día va en el mismo lote que meta/estado, el último, y nadie escribe una hora a mano:
  --cierres   el volcado de la colección «cierres» (las marcas que deja cada cierre de sesión): van como «delete», con su
              if_version, las de `hora` anterior o igual al `sincronizado` de esta corrida y las de `hora` posterior a
              ahora (mal puestas); las demás se quedan, que son de un cierre que esta corrida pudo no ver.
  --inicio    el inicio.json que dejó preparar.py --trabajo: de ahí sale `duracion_min` de la corrida.
  --llamadas  cuántas llamadas a herramientas llevó la corrida (las cuenta quien la corre); se guarda tal cual.
  --pagina    el campo pagina_actualizada que escribe el paso de versiones; --tarea-desfasada, su campo.
Con --cierre (el tablero ya estaba al día: no hubo generación) escribe <salida>/meta/estado.json con solo lo que cambia
(«sincronizado», el que imprimió el inventario en la zona de la organización, `cola_retenida`, `cola_ajena`, la duración,
las llamadas, la página) y planea un lote: los «delete» de cierres y meta/estado como «update» (sin if_version: solo esta
corrida escribe esos campos). Las huellas de la raíz y de los proyectos no se tocan.

Con --guardada no planea nada: imprime dos líneas. La primera, la huella de la raíz que guardó la última puesta al día
si el tablero sigue valiendo tal cual (misma versión del plugin, misma tarea, mismo «sin horario»), o «-» si hay que
regenerar. La segunda, las huellas de cada proyecto que guardó (separadas por comas, para --sin-cambios del inventario)
si los documentos de la base son de esta misma versión del plugin, o «-» si no hay ninguna que valga.

<volcado-de-la-base> es la carpeta donde ArtifactData dejó, con out_dir, lo que hay hoy en la base
(<volcado>/areas/*.json, <volcado>/proyectos/*.json, <volcado>/meta/estado.json).
Compara huellas e imprime un JSON con:
  «lotes»: listas de escrituras, cada una de menos de --max-bytes y de 50 entradas como mucho, con
           {op, collection, doc_id, file_path, existe}. «existe» dice si el documento ya está en la base:
           esos llevan «if_version» con la versión que dio la lectura. meta/estado va siempre, como «update» (o «set» si la base está vacía).
  Los documentos de la base que ya no salen de la raíz van en los lotes como «delete» (con su if_version).
  Si <salida-del-generador>/barrido.json existe (lo deja `barrido.py`), suma a los lotes las propuestas nuevas de la cola
  («set» en «cambios», sin if_version) y las que ya no valen («delete» con el if_version que dio la lectura de la cola).
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
    # los documentos de la base se pueden reutilizar si los hizo esta misma versión; la tarea no entra en un proyecto
    hs = d.get("huellas") if d.get("version_tablero") == _a("--version") else None
    print(",".join(hs) if isinstance(hs, list) and hs else "-")
    sys.exit(0)

import datetime
ID_VALIDO = re.compile(r"^(?!\.\.?$)[A-Za-z0-9_\-.~:@+]{1,200}$")   # lo que la base admite como doc_id


def _opt(n, defecto=None):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv and len(sys.argv) > sys.argv.index(n) + 1 else defecto


def _json(p):
    if not p:
        return None
    try:
        d = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return d


def _datos(d):
    return d.get("data", d) if isinstance(d, dict) and "data" in d else (d if isinstance(d, dict) else {})


def _zona(nombre):
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(nombre or "America/Mexico_City")
    except Exception:
        return datetime.timezone.utc


def extras_cierre(sincronizado, zona):
    """Los campos de meta/estado que cierran la corrida, y los «delete» de cierres. `sincronizado` lleva zona."""
    campos = {}
    ini = _json(_opt("--inicio"))
    ahora = datetime.datetime.now(_zona(zona))
    if ini and ini.get("inicio"):
        try:
            t0 = datetime.datetime.fromisoformat(ini["inicio"])
            campos["duracion_min"] = round(max(0, (ahora - t0).total_seconds()) / 60, 1)
        except ValueError:
            pass
    if _opt("--llamadas") and _opt("--llamadas").isdigit():
        campos["llamadas"] = int(_opt("--llamadas"))
    if _opt("--pagina"):
        try:
            campos["pagina_actualizada"] = json.loads(_opt("--pagina"))
        except ValueError:
            pass
    if _opt("--tarea-desfasada") in ("true", "false"):
        campos["tarea_desfasada"] = _opt("--tarea-desfasada") == "true"
    borrar = []
    d = pathlib.Path(_opt("--cierres")) if _opt("--cierres") else None
    try:
        t_sinc = datetime.datetime.fromisoformat(sincronizado) if sincronizado else None
    except ValueError:
        t_sinc = None
    # la herramienta deja cada documento en <out_dir>/<colección>/<id>.json: se baja un nivel, como cargar_cola en barrido.py
    for p in sorted(d.rglob("*.json")) if d and d.is_dir() else []:
        raw = _json(p)
        dd = _datos(raw)
        try:
            h = datetime.datetime.fromisoformat(str(dd.get("hora", "")))
            if h.tzinfo is None:
                h = h.replace(tzinfo=ahora.tzinfo)
        except ValueError:
            h = None
        fuera = h is None or (t_sinc is not None and h <= t_sinc) or h > ahora
        if fuera and ID_VALIDO.match(p.stem):
            e = {"op": "delete", "collection": "cierres", "doc_id": p.stem}
            if isinstance(raw, dict) and raw.get("version") is not None:
                e["if_version"] = raw["version"]
            borrar.append(e)
    return campos, borrar


if "--cierre" in sys.argv:
    i = sys.argv.index("--cierre")
    VOLCADO, SALIDA = pathlib.Path(sys.argv[i + 1]).resolve(), pathlib.Path(sys.argv[i + 2]).resolve()
    base = _datos(_json(VOLCADO / "meta" / "estado.json") or {})
    sinc = _opt("--sincronizado") or datetime.datetime.now(_zona(base.get("zona"))).isoformat(timespec="minutes")
    campos, borrar = extras_cierre(sinc, base.get("zona"))
    campos["sincronizado"] = sinc
    for k, f in (("cola_retenida", _opt("--retenidos")), ("cola_ajena", _opt("--ajenos"))):
        v = _json(f) if f else None
        campos[k] = v if isinstance(v, list) else []
    (SALIDA / "meta").mkdir(parents=True, exist_ok=True)
    (SALIDA / "meta" / "estado.json").write_text(json.dumps(campos, ensure_ascii=False, indent=1), encoding="utf-8")
    lote = borrar + [{"op": "update" if base else "set", "collection": "meta", "doc_id": "estado", "file_path": str(SALIDA / "meta" / "estado.json")}]
    print(json.dumps({"lotes": [lote], "cierres_borrados": len(borrar), "duracion_min": campos.get("duracion_min")}, ensure_ascii=False, indent=1))
    sys.exit(0)

SALIDA = pathlib.Path(sys.argv[1]).resolve()
VOLCADO = pathlib.Path(sys.argv[2]).resolve()
MAX = int(sys.argv[sys.argv.index("--max-bytes") + 1]) if "--max-bytes" in sys.argv else 900_000
COLECCIONES = ("areas", "proyectos", "detalle")   # las que regenera el generador entero; «cambios» y «enfoque» no se tocan aquí
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


# lo que cierra la corrida entra en meta/estado antes de planear, para que suba en el mismo lote, el último
_meta_p = SALIDA / "meta" / "estado.json"
_meta_d = _json(_meta_p) or {}
_campos, _borrar_cierres = extras_cierre(_meta_d.get("sincronizado"), _meta_d.get("zona"))
# lo que el modelo ya juzgó sin hallazgo (barrido.py --sumar-juicio lo deja en barrido.json) se suma a lo de la base, acotado
_bar_j = (_json(SALIDA / "barrido.json") or {}).get("juzgado") or {}
_base_j = (_datos(_json(VOLCADO / "meta" / "estado.json") or {}).get("juzgado")) or {}
if _bar_j or _base_j:
    _campos["juzgado"] = {k: (list(dict.fromkeys(list(_base_j.get(k) or []) + list(_bar_j.get(k) or []))))[-600:] for k in ("ids", "contraste")}
if _campos:
    _meta_d.update(_campos)
    _meta_p.write_text(json.dumps(_meta_d, ensure_ascii=False, indent=1), encoding="utf-8")
# «Por dónde empezar» solo se renueva si cambiaron los candidatos: la huella de los de hoy frente a la que guardó la base
_cand = _json(SALIDA / "meta" / "enfoque-candidatos.json") or {}
_base_meta = _datos(_json(VOLCADO / "meta" / "estado.json") or {})
enfoque_cambio = bool(_cand.get("huella")) and _cand.get("huella") != _base_meta.get("huella_candidatos")

indice = json.loads((SALIDA / "indice.json").read_text(encoding="utf-8"))
escrituras, sin_cambios, salen, invalidos, grandes = [], 0, set(), [], []
for it in indice:
    col, doc = it["coleccion"], it["doc_id"]
    salen.add((col, doc))
    if not ID_VALIDO.match(doc):
        invalidos.append(f"{col}/{doc}"); continue      # carpeta con espacios o acentos: la base no la admite
    if (col, doc) == ("meta", "estado"):
        it["bytes"] = _meta_p.stat().st_size      # cambió al sumarle lo que cierra la corrida
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
# el detalle de un proyecto va pegado a su proyecto, para que caigan en el mismo lote cuando quepan: si el lote falla,
# la página no se queda con un proyecto nuevo y su detalle viejo (o al revés)
_det = {e["doc_id"]: e for e in escrituras if e["collection"] == "detalle"}
orden = []
for e in escrituras:
    if e in _meta or e["collection"] == "detalle":
        continue
    orden.append(e)
    if e["collection"] == "proyectos" and e["doc_id"] in _det:
        orden.append(_det.pop(e["doc_id"]))
# las propuestas del barrido (colección «cambios», que el generador no toca): nuevas como «set», las que ya no valen como «delete»
propuestas = []
_b = SALIDA / "barrido.json"
if _b.exists():
    bar = json.loads(_b.read_text(encoding="utf-8"))
    for x in bar.get("anadir", []):
        f = SALIDA / x["archivo"]
        if not ID_VALIDO.match(x["id"]) or not f.exists() or f.stat().st_size > LIMITE:
            invalidos.append(f"cambios/{x['id']}"); continue
        propuestas.append({"op": "set", "collection": "cambios", "doc_id": x["id"], "file_path": str(f), "existe": False, "bytes": f.stat().st_size})
    for x in bar.get("borrar", []):
        if ID_VALIDO.match(x["id"]):
            e = {"op": "delete", "collection": "cambios", "doc_id": x["id"]}
            if x.get("if_version") is not None:
                e["if_version"] = x["if_version"]
            propuestas.append(e)
orden += list(_det.values()) + borrar + propuestas + _borrar_cierres + _meta
lotes, actual, peso = [], [], 0
for e in orden:
    b = e.get("bytes", 200) + 300
    if actual and (peso + b > MAX or len(actual) >= 50):
        lotes.append(actual); actual, peso = [], 0
    actual.append({k: v for k, v in e.items() if k != "bytes"})
    peso += b
if actual:
    lotes.append(actual)

print(json.dumps({"lotes": lotes, "sin_cambios": sin_cambios, "borrados": len(borrar), "cierres_borrados": len(_borrar_cierres),
                  "enfoque_cambio": enfoque_cambio, "duracion_min": _campos.get("duracion_min"),
                  "propuestas": {"nuevas": sum(1 for e in propuestas if e["op"] == "set"), "retiradas": sum(1 for e in propuestas if e["op"] == "delete")},
                  "no_se_suben": {"id_no_valido": invalidos, "demasiado_grandes": grandes}}, ensure_ascii=False, indent=1))
