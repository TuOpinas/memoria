#!/usr/bin/env python3
"""Los datos del tablero entre sus archivos publicados, la base y las carpetas de trabajo de la puesta al día (1.24.1).

Desde la 1.24.1, lo que la puesta al día genera de la carpeta (áreas, proyectos, detalle, resúmenes de «Qué hay», «Por dónde
empezar», meta/estado y las propuestas del barrido) va como archivos del propio tablero, publicados junto con la página:

  datos/estado.json      meta/estado
  datos/tablero.json     {"areas": {id: doc}, "proyectos": {id: doc}, "resumenes": {id: doc}, "enfoque": doc | null}
  datos/propuestas.json  {id: doc}   las sugerencias del barrido
  datos/detalle.json     {id: doc}   lo que la página trae al entrar en un proyecto

La base guarda solo lo pequeño que se escribe a diario: lo que se marca en la página («cambios», incluida la marca de una
propuesta aceptada, descartada o aplicada, con el mismo id que la propuesta), los cierres de sesión («cierres»), los
permisos («meta/permisos») y la marca de la última publicación («publicado»). Así nada grande pasa por la conversación: los
archivos se leen y se publican desde disco, y lo de la base cabe en una llamada.

Uso:
  datos.py base <trabajo> [estado=<archivo>] [tablero=<archivo>] [propuestas=<archivo>] [detalle=<archivo>]
                [--cola <cola.jsonl>] [--cierres <cierres.jsonl>]
      Arma, desde los archivos descargados (la herramienta los guarda con el nombre que elige; se le pasan por su ruta), el
      volcado que leen generar_vista.py --previos y plan_subida.py: <trabajo>/base/<colección>/<id>.json, con {"id", "data"}.
      Con --cola (las líneas JSON que devolvió la consulta de «cambios», tal cual), <trabajo>/cola/<id>.json con {"id",
      "version", "data"}: lo marcado en la página y cada propuesta del archivo con su marca de la base encima. Con
      --cierres, <trabajo>/cierres/<id>.json igual. Un archivo que no se pasa se trata como vacío (el tablero aún no los
      tiene), salvo detalle: sin él, publicar no toca detalle.json. Imprime cuántos documentos hay de cada clase.

  datos.py publicar <trabajo> [--vista <vista.html> --titulo "Tablero <organización>"] [--enfoque <enfoque.json>]
      Aplica <trabajo>/salida/plan.json (lo que escribió plan_subida.py) sobre el volcado de <trabajo>/base y deja en
      <trabajo>/publicar/ los archivos que cambian, listos para una sola publicación. Imprime un JSON con «archivos» (la
      lista {"as", "path"} que se pasa tal cual a la herramienta de publicar) y «base» (las escrituras de la base, en lotes
      de 50 como mucho, con la forma de db_write: {"op", "path", "ifVersion"?, "data"?}), que se mandan después de publicar.
      Con --vista, la página va en la misma publicación como index.html, con su <title> sustituido. Con --enfoque (el
      «Por dónde empezar» que escribió el modelo), entra en tablero.json y la huella nueva de los candidatos en estado.json.
  datos.py propuestas <propuestas.json> <area>--<proyecto>
      Las sugerencias de un proyecto, una por línea en JSON con su id, para la apertura de una sesión (skill sesion): la
      sesión no carga el archivo entero.
No lee ni escribe nada de la carpeta de memoria.
"""
import sys, json, pathlib, re, datetime, html

ARCHIVO_COLS = ("areas", "proyectos", "resumenes")
ID_VALIDO = re.compile(r"^(?!\.\.?$)[A-Za-z0-9_\-.~:@+]{1,200}$")


def _json(p):
    try:
        return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return None


def _datos(d):
    return d.get("data", d) if isinstance(d, dict) and isinstance(d.get("data"), dict) else (d if isinstance(d, dict) else None)


def _escribe(p, obj):
    p = pathlib.Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def _lineas(p):
    """Los documentos de una consulta a la base: una línea JSON por documento, como las devuelve la herramienta
    ({"data", "id", "version", ...}); también acepta una lista JSON. Lo que no se entiende se salta y se cuenta."""
    if not p:
        return [], 0
    txt = pathlib.Path(p).read_text(encoding="utf-8").strip()
    if not txt:
        return [], 0
    if txt.startswith("["):
        try:
            v = json.loads(txt)
            return [x for x in v if isinstance(x, dict) and x.get("id")], 0
        except ValueError:
            pass
    docs, malas = [], 0
    for l in txt.splitlines():
        l = l.strip()
        if not l or l.startswith("<") or not l.startswith("{"):
            continue
        try:
            d = json.loads(l)
        except ValueError:
            malas += 1; continue
        if isinstance(d, dict) and d.get("id"):
            docs.append(d)
        else:
            malas += 1
    return docs, malas


def base(trabajo, args):
    trabajo = pathlib.Path(trabajo)
    arch, cola_p, cierres_p = {}, None, None
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--cola":
            cola_p = args[i + 1]; i += 2; continue
        if a == "--cierres":
            cierres_p = args[i + 1]; i += 2; continue
        k, _, v = a.partition("=")
        if k not in ("estado", "tablero", "propuestas", "detalle") or not v:
            sys.exit(f"No entiendo «{a}»: los archivos van como estado=<ruta>, tablero=<ruta>, propuestas=<ruta> o detalle=<ruta>.")
        if not pathlib.Path(v).exists():
            sys.exit(f"No encuentro {v}: pasa la ruta donde la herramienta guardó datos/{k}.json.")
        arch[k] = _json(v)
        if arch[k] is None:
            sys.exit(f"{v} no es JSON: vuelve a traer datos/{k}.json.")
        i += 1
    b = trabajo / "base"
    cuenta = {}
    if "estado" in arch:
        _escribe(b / "meta" / "estado.json", {"id": "estado", "data": _datos(arch["estado"]) or {}})
        cuenta["estado"] = 1
    tab = arch.get("tablero") or {}
    for col in ARCHIVO_COLS:
        for id_, d in (tab.get(col) or {}).items():
            if ID_VALIDO.match(id_) and isinstance(d, dict):
                _escribe(b / col / f"{id_}.json", {"id": id_, "data": d})
        cuenta[col] = len(tab.get(col) or {})
    if isinstance(tab.get("enfoque"), dict):
        _escribe(b / "enfoque" / "actual.json", {"id": "actual", "data": tab["enfoque"]})
    if "detalle" in arch:
        for id_, d in (arch["detalle"] or {}).items():
            if ID_VALIDO.match(id_) and isinstance(d, dict):
                _escribe(b / "detalle" / f"{id_}.json", {"id": id_, "data": d})
        (b / ".con-detalle").write_text("1", encoding="utf-8")
        cuenta["detalle"] = len(arch["detalle"] or {})
    props = arch.get("propuestas") or {}
    for id_, d in props.items():
        if ID_VALIDO.match(id_) and isinstance(d, dict):
            _escribe(b / "propuestas" / f"{id_}.json", {"id": id_, "data": d})
    cuenta["propuestas"] = len(props)
    if cola_p is not None:
        docs, malas = _lineas(cola_p)
        marcas = {d["id"]: d for d in docs}
        c = trabajo / "cola"
        n_marcas = 0
        for id_, d in marcas.items():
            data = _datos(d) or {}
            if data.get("tipo") == "propuesta" and id_ in props:
                continue            # va abajo, encima de su propuesta
            if not ID_VALIDO.match(id_):
                continue
            _escribe(c / f"{id_}.json", {"id": id_, "version": d.get("version"), "data": data})
            n_marcas += data.get("tipo") != "propuesta"
        for id_, d in props.items():
            if not (ID_VALIDO.match(id_) and isinstance(d, dict)):
                continue
            m = marcas.get(id_)
            data = dict(d, tipo="propuesta")
            if m:
                md = _datos(m) or {}
                for k in ("estado", "aceptada", "descartada", "por"):
                    if k in md:
                        data[k] = md[k]
            _escribe(c / f"{id_}.json", {"id": id_, "version": m.get("version") if m else None, "data": data})
        cuenta["cola_marcas"] = n_marcas
        if malas:
            cuenta["cola_lineas_no_leidas"] = malas
    if cierres_p is not None:
        docs, malas = _lineas(cierres_p)
        for d in docs:
            if ID_VALIDO.match(d["id"]):
                _escribe(trabajo / "cierres" / f"{d['id']}.json", {"id": d["id"], "version": d.get("version"), "data": _datos(d) or {}})
        cuenta["cierres"] = len(docs)
        if malas:
            cuenta["cierres_lineas_no_leidos"] = malas
    print(json.dumps(cuenta, ensure_ascii=False))


def _cargar(b, col):
    d = b / col
    out = {}
    for p in sorted(d.glob("*.json")) if d.exists() else []:
        v = _datos(_json(p))
        if isinstance(v, dict):
            out[p.stem] = v
    return out


def _lotes(ops, n=50):
    return [ops[i:i + n] for i in range(0, len(ops), n)]


def publicar(trabajo, args):
    trabajo = pathlib.Path(trabajo)
    opt = lambda n: args[args.index(n) + 1] if n in args and len(args) > args.index(n) + 1 else None
    b, salida, pub = trabajo / "base", trabajo / "salida", trabajo / "publicar"
    plan = _json(salida / "plan.json")
    if not isinstance(plan, dict):
        sys.exit("Falta <trabajo>/salida/plan.json: corre antes plan_subida.py.")
    # sin estado en la base, el tablero aún no tiene archivos: no hay detalle que traer y se parte de cero
    con_detalle = (b / ".con-detalle").exists() or not (b / "meta" / "estado.json").exists()
    antes = {"estado": (_datos(_json(b / "meta" / "estado.json")) or None),
             "tablero": {**{c: _cargar(b, c) for c in ARCHIVO_COLS}, "enfoque": _datos(_json(b / "enfoque" / "actual.json"))},
             "propuestas": _cargar(b, "propuestas"),
             "detalle": _cargar(b, "detalle") if con_detalle else None}
    ahora = json.loads(json.dumps(antes))
    estado = ahora["estado"] if isinstance(ahora["estado"], dict) else {}
    ops_base, sin_detalle = [], []
    for e in [x for lote in plan.get("lotes") or [] for x in lote]:
        col, doc, op = e.get("collection"), e.get("doc_id"), e.get("op")
        data = _datos(_json(e["file_path"])) if e.get("file_path") else None
        if op in ("set", "update") and data is None:
            sys.exit(f"No puedo leer {e.get('file_path')} ({col}/{doc}): vuelve a correr la generación.")
        if col == "meta" and doc == "estado":
            estado = dict(estado, **data) if op == "update" else dict(data)
        elif col in ARCHIVO_COLS:
            if op == "delete":
                ahora["tablero"][col].pop(doc, None)
            else:
                ahora["tablero"][col][doc] = data
        elif col == "detalle":
            if ahora["detalle"] is None:
                sin_detalle.append(doc); continue
            if op == "delete":
                ahora["detalle"].pop(doc, None)
            else:
                ahora["detalle"][doc] = data
        elif col == "enfoque":
            ahora["tablero"]["enfoque"] = None if op == "delete" else data
        elif col == "cambios":
            # las propuestas del barrido viven en el archivo; su marca en la base (si alguien la tocó) se borra con ella
            if op == "delete":
                ahora["propuestas"].pop(doc, None)
                if e.get("if_version") is not None:
                    ops_base.append({"op": "delete", "path": f"cambios/{doc}", "ifVersion": e["if_version"]})
            else:
                d_ = dict(data); d_.pop("tipo", None)
                ahora["propuestas"][doc] = dict(d_, tipo="propuesta")
        elif col == "cierres" and op == "delete":
            if e.get("if_version") is not None:
                ops_base.append({"op": "delete", "path": f"cierres/{doc}", "ifVersion": e["if_version"]})
        else:
            sys.exit(f"El plan trae una escritura que no sé hacer: {op} {col}/{doc}.")
    if sin_detalle:
        sys.exit("El plan cambia el detalle de " + ", ".join(sin_detalle[:5]) + " sin que se haya traído datos/detalle.json: tráelo y vuelve a correr «datos.py base».")
    enf = opt("--enfoque")
    if enf:
        e_ = _json(enf)
        if not isinstance(e_, dict) or not isinstance(e_.get("grupos"), list):
            sys.exit(f"{enf} no tiene la forma de «Por dónde empezar» (falta «grupos»).")
        ahora["tablero"]["enfoque"] = e_
        h = _json(salida / "meta" / "estado-enfoque.json")
        if isinstance(h, dict) and h.get("huella_candidatos"):
            estado["huella_candidatos"] = h["huella_candidatos"]
    # la marca de esta publicación, para que una página abierta sepa que hay datos nuevos; la de la anterior se borra
    sinc = estado.get("sincronizado")
    marca = None
    if sinc:
        marca = "p" + re.sub(r"[^0-9]", "", str(sinc))[:12]
        prev = (antes["estado"] or {}).get("publicado_id")
        if prev and prev != marca and ID_VALIDO.match(prev):
            ops_base.append({"op": "delete", "path": f"publicado/{prev}", "ifVersion": 1})
        if prev != marca:
            ops_base.append({"op": "set", "path": f"publicado/{marca}", "data": {"sincronizado": sinc}})
        estado["publicado_id"] = marca
    ahora["estado"] = estado
    pub.mkdir(parents=True, exist_ok=True)
    archivos = []

    def sale(nombre, obj, viejo):
        if viejo is not None and obj == viejo:
            return
        _escribe(pub / "datos" / nombre, obj)
        archivos.append({"as": f"datos/{nombre}", "path": str((pub / "datos" / nombre).resolve())})

    sale("estado.json", ahora["estado"], antes["estado"])
    sale("tablero.json", ahora["tablero"], antes["tablero"] if antes["estado"] is not None else None)
    sale("propuestas.json", ahora["propuestas"], antes["propuestas"] if antes["estado"] is not None else None)
    if ahora["detalle"] is not None:
        sale("detalle.json", ahora["detalle"], antes["detalle"] if antes["estado"] is not None else None)
    elif antes["estado"] is None:
        # un tablero sin archivos todavía: la página pide detalle.json aunque no haya ningún proyecto con detalle
        sale("detalle.json", {}, None)
    vista = opt("--vista")
    if vista:
        titulo = opt("--titulo") or "Tablero"
        txt = pathlib.Path(vista).read_text(encoding="utf-8")
        if "<title>Tablero</title>" not in txt:
            sys.exit(f"{vista} no empieza por <title>Tablero</title>: ¿es la vista.html del plugin?")
        txt = txt.replace("<title>Tablero</title>", f"<title>{html.escape(titulo)}</title>", 1)
        (pub / "index.html").write_text(txt, encoding="utf-8")
        archivos.insert(0, {"as": "index.html", "path": str((pub / "index.html").resolve())})
    pesos = {a["as"]: pathlib.Path(a["path"]).stat().st_size for a in archivos}
    print(json.dumps({"archivos": archivos, "base": _lotes(ops_base), "bytes": pesos,
                      "propuestas": len(ahora["propuestas"]), "proyectos": len(ahora["tablero"]["proyectos"])}, ensure_ascii=False, indent=1))


def propuestas(archivo, pid):
    d = _json(archivo)
    if not isinstance(d, dict):
        sys.exit(f"{archivo} no es el archivo de propuestas del tablero.")
    n = 0
    for id_, x in sorted(d.items(), key=lambda kv: str((kv[1] or {}).get("creado") or "")):
        if isinstance(x, dict) and x.get("proyecto") == pid:
            print(json.dumps(dict(x, id=id_), ensure_ascii=False)); n += 1
    if not n:
        print(f"Ninguna sugerencia para {pid}.")


def main():
    a = sys.argv[1:]
    if len(a) == 3 and a[0] == "propuestas":
        propuestas(a[1], a[2])
    elif len(a) >= 2 and a[0] == "base":
        base(a[1], a[2:])
    elif len(a) >= 2 and a[0] == "publicar":
        publicar(a[1], a[2:])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
