#!/usr/bin/env python3
"""Los datos del tablero entre sus archivos publicados, la base y las carpetas de trabajo de la puesta al día (1.24.1).

Desde la 1.24.1, lo que la puesta al día genera de la carpeta (áreas, proyectos, detalle, resúmenes de «Qué hay», «Por dónde
empezar», meta/estado y las propuestas del barrido) va como archivos del propio tablero, publicados junto con la página:

  datos/estado.json      meta/estado
  datos/tablero.json     {"areas": {id: doc}, "proyectos": {id: doc}, "resumenes": {id: doc}, "enfoque": doc | null}
  datos/propuestas.json  {id: doc}   las sugerencias del barrido
  datos/detalle/<área>.json  {id: doc}   lo que la página trae al entrar en un proyecto, un archivo por área (1.24.2;
                                       en la 1.24.1 era un solo datos/detalle.json, que se sigue leyendo y se quita al publicar)

La base guarda solo lo pequeño que se escribe a diario: lo que se marca en la página («cambios»; la marca de una sugerencia
lleva su mismo id y solo dice qué se hizo con ella), los cierres de sesión («cierres»), los permisos («meta/permisos») y una
marca por publicación («publicado»). Los archivos se leen y se publican desde disco; por la conversación pasa solo lo de la
base, que cabe en una llamada.

Uso, en el orden de la puesta al día:
  datos.py base <trabajo> (estado=<archivo> | --primera-vez) --cola <cola.jsonl> --cierres <cierres.jsonl> --publicado <publicado.jsonl>
      Paso 1a. Vacía y arma <trabajo>/base/meta/estado.json, <trabajo>/cola/ (lo marcado en la página, sin las marcas de
      sugerencias, que guarda aparte), <trabajo>/cierres/ y <trabajo>/publicado.json. Los .jsonl son las líneas JSON que
      devolvió la herramienta, tal cual (un archivo que falta o está vacío es una consulta sin documentos). --primera-vez:
      el tablero aún no tiene archivos (read_file dijo que datos/estado.json no existe); nada más cuenta como primera vez.
      No imprime nada; sale con 2 si alguna línea no se pudo leer (se repite la copia).
  datos.py base <trabajo> (tablero=<archivo> propuestas=<archivo> [detalle:<área>=<archivo> …] [detalle=<archivo>] | --sin-archivos)
      Paso e, al regenerar. Arma <trabajo>/base/<colección>/<id>.json, que leen generar_vista.py --previos y plan_subida.py,
      y pone cada marca de la base encima de su sugerencia en <trabajo>/cola. Una marca completa de la 1.24.0 (con su texto)
      cuya sugerencia no está en el archivo pasa al archivo; una «pendiente», o una que se queda sin sugerencia, se borra
      de la base al publicar. El detalle va con un detalle:<área>=… por cada archivo datos/detalle/<área>.json que el tablero
      tenga (los que dice «datos.py rutas»; uno que read_file dijo que no existe, detalle:<área>=-), y detalle=… si aún tiene
      el datos/detalle.json de la 1.24.1; si falta alguno, para. --sin-archivos, en la primera vez. No imprime nada.
  datos.py publicar <trabajo> [--vista <vista.html>] [--enfoque <enfoque.json>]
      Aplica <trabajo>/salida/plan.json (plan_subida.py) sobre lo traído y deja en <trabajo>/publicar/ los archivos que
      cambian. Imprime un JSON con «archivos» (la lista {"as", "path"} que va tal cual a la publicación; vacía si no hay
      nada que publicar), «base» (lotes de escrituras con la forma de db_write, que se mandan después, en orden, uno cada
      vez), «quitar» si lo hay (los archivos que la publicación borra: el detalle de un área que ya no tiene proyectos y el
      datos/detalle.json de la 1.24.1) y, si lo hay, «aviso». Del detalle solo salen las áreas que cambiaron. Con --vista la página va en la misma publicación, con el título de la organización que
      dice meta/estado; la primera vez es obligatoria, porque la página de antes no sabe leer los archivos. Con --enfoque
      (el «Por dónde empezar» que escribió el modelo), entra en tablero.json y la huella nueva de los candidatos en
      estado.json. Si lo único que cambia es meta/estado (una corrida al día), no publica: la marca de la base lleva la hora
      y lo que enseñan el pie y el botón.
  datos.py rutas <trabajo>
      Paso e (1.24.2): imprime en una línea la lista JSON de los archivos que hay que traer con read_file (tablero.json,
      propuestas.json y el detalle de cada área que el tablero tiene; el detalle.json único si es de la 1.24.1).
  datos.py propuestas <propuestas.json> <area>--<proyecto>
      Las sugerencias de un proyecto, una por línea en JSON con su id, para la apertura de una sesión (skill sesion).
No lee ni escribe nada de la carpeta de memoria.
"""
import sys, json, pathlib, re, html, shutil, time

ARCHIVO_COLS = ("areas", "proyectos", "resumenes")
ID_VALIDO = re.compile(r"^(?!\.\.?$)[A-Za-z0-9_\-.~:@+]{1,200}$")   # lo que la base admite como id de documento
TOPE_LECTURA = 3_500_000      # read_file trae como mucho 4 MiB por llamada: se avisa antes de llegar
CAMPOS_MARCA = ("estado", "aceptada", "descartada", "por")
CAMPOS_AL_DIA = ("sincronizado", "duracion_min", "llamadas", "cola_retenida", "cola_ajena")


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


def _vacia(p):
    p = pathlib.Path(p)
    if p.is_dir():
        shutil.rmtree(p)
    elif p.exists():
        p.unlink()


def _lineas(p):
    """Los documentos de una consulta a la base: una línea JSON por documento, como las devuelve la herramienta
    ({"data", "id", "version", ...}); también una lista JSON. Se saltan las etiquetas y la línea de resumen (count,
    nextCursor). Un archivo que no existe es una consulta vacía. Devuelve (documentos, líneas que no se entendieron)."""
    try:
        txt = pathlib.Path(p).read_text(encoding="utf-8").strip() if p else ""
    except OSError:
        txt = ""
    if not txt:
        return [], 0
    if txt.startswith("["):
        try:
            return [_norm(x) for x in json.loads(txt) if _norm(x)], 0
        except ValueError:
            pass
    docs, malas = [], 0
    for l in txt.splitlines():
        l = l.strip()
        if not l.startswith("{"):
            continue
        try:
            d = json.loads(l)
        except ValueError:
            malas += 1; continue
        if isinstance(d, dict) and ("count" in d or "nextCursor" in d or "notice" in d) and "data" not in d:
            continue            # la línea de resumen de la consulta
        n = _norm(d)
        if n:
            docs.append(n)
        else:
            malas += 1
    return docs, malas


def _norm(d):
    """Un documento de la base como {"id", "version", "data"}: acepta id, doc_id o path («colección/id»)."""
    if not isinstance(d, dict):
        return None
    id_ = d.get("id") or d.get("doc_id") or (str(d.get("path") or "").rsplit("/", 1)[-1] or None)
    if not id_ or not ID_VALIDO.match(str(id_)):
        return None
    if not isinstance(d.get("data"), dict):
        return None             # sin cuerpo (la consulta lo dejó fuera por tamaño): no se toma por un cambio vacío
    return {"id": str(id_), "version": d.get("version"), "data": _datos(d["data"])}


def _opciones(args, nombres, banderas):
    vals, flags, arch = {}, set(), {}
    i = 0
    while i < len(args):
        a = args[i]
        if a in nombres:
            if i + 1 >= len(args):
                sys.exit(f"Falta el valor de {a}.")
            vals[a] = args[i + 1]; i += 2; continue
        if a in banderas:
            flags.add(a); i += 1; continue
        k, _, v = a.partition("=")
        area = k.split(":", 1)[1] if k.startswith("detalle:") else None
        if (k not in ("estado", "tablero", "propuestas", "detalle") and not (area and ID_VALIDO.match(area))) or not v:
            sys.exit(f"No entiendo «{a}»: los archivos van como estado=<ruta>, tablero=<ruta>, propuestas=<ruta>, detalle:<área>=<ruta> "
                     "(uno por área, 1.24.2) o detalle=<ruta> (el único de un tablero de la 1.24.1).")
        nombre = f"detalle/{area}.json" if area else f"{k}.json"
        if area and v == "-":
            arch.setdefault("detalle_areas", {})[area] = None     # read_file dijo «no file at»: el área no tiene archivo
            i += 1; continue
        if not pathlib.Path(v).exists():
            sys.exit(f"No encuentro {v}: pasa la ruta donde la herramienta guardó datos/{nombre}.")
        d = _json(v)
        if not isinstance(d, dict):
            sys.exit(f"{v} no es el JSON de datos/{nombre}: vuelve a traerlo.")
        if area:
            arch.setdefault("detalle_areas", {})[area] = d
        else:
            arch[k] = d
        i += 1
    return vals, flags, arch


def base(trabajo, args):
    trabajo = pathlib.Path(trabajo)
    vals, flags, arch = _opciones(args, ("--cola", "--cierres", "--publicado"), ("--primera-vez", "--sin-archivos"))
    b = trabajo / "base"
    if "estado" in arch or "--primera-vez" in flags:
        # paso 1a: se parte de cero, también al repetir la corrida tras un conflicto
        for x in (b, trabajo / "cola", trabajo / "cierres", trabajo / "marcas.json", trabajo / "marcas-sobran.json", trabajo / "publicado.json", trabajo / "publicar"):
            _vacia(x)
        b.mkdir(parents=True, exist_ok=True)
        if "estado" in arch:
            _escribe(b / "meta" / "estado.json", {"id": "estado", "data": _datos(arch["estado"]) or {}})
        else:
            (b / ".primera-vez").write_text("1", encoding="utf-8")
        malas = 0
        docs, m = _lineas(vals.get("--cola")); malas += m
        marcas = []
        for d in docs:
            if d["data"].get("tipo") == "propuesta":
                marcas.append(d)
            else:
                _escribe(trabajo / "cola" / f"{d['id']}.json", d)
        (trabajo / "cola").mkdir(parents=True, exist_ok=True)
        _escribe(trabajo / "marcas.json", marcas)
        docs, m = _lineas(vals.get("--cierres")); malas += m
        for d in docs:
            _escribe(trabajo / "cierres" / f"{d['id']}.json", d)
        docs, m = _lineas(vals.get("--publicado")); malas += m
        _escribe(trabajo / "publicado.json", [{"id": d["id"], "version": d["version"]} for d in docs])
        if malas:
            sys.stderr.write(f"{malas} línea(s) de la base no se pudieron leer: vuelve a copiarlas tal cual, sin cambiar nada.\n")
            sys.exit(2)
        return
    if not (arch or "--sin-archivos" in flags):
        sys.exit("Nada que armar: pasa estado=… o --primera-vez (paso 1a), o tablero=… propuestas=… detalle=… o --sin-archivos (paso e).")
    # paso e: lo publicado de la regeneración
    if not ((b / "meta" / "estado.json").exists() or (b / ".primera-vez").exists()):
        sys.exit("Falta el paso 1a: corre antes «datos.py base <trabajo> estado=…» (o --primera-vez).")
    if (b / ".primera-vez").exists() and arch:
        sys.exit("Es la primera vez (el tablero no tenía datos/estado.json): el paso e va con --sin-archivos.")
    if not (b / ".primera-vez").exists() and "--sin-archivos" in flags:
        sys.exit("El tablero tiene datos/estado.json: el paso e trae tablero.json, propuestas.json y el detalle.")
    if arch and not {"tablero", "propuestas"} <= set(arch):
        sys.exit("El paso e trae tablero=…, propuestas=… y el detalle: detalle:<área>=… de cada área que tenga su archivo, o detalle=… si el tablero es de la 1.24.1.")
    if arch:
        # el detalle que se trae tiene que ser el que el tablero tiene: sin uno, la publicación lo daría por vacío y la
        # página perdería el detalle de los proyectos de esa área que no cambiaron (revisión de la 1.24.2)
        est_ = _datos(_json(b / "meta" / "estado.json")) or {}
        deben = est_.get("detalle_areas")
        traidos = arch.get("detalle_areas") or {}
        if isinstance(deben, list):
            faltan = [a_ for a_ in deben if a_ not in traidos]
            if faltan:
                sys.exit("Faltan detalles del paso e: " + ", ".join(f"detalle:{a_}=<ruta>" for a_ in faltan) + " (los dice «datos.py rutas»; "
                         "si read_file dijo que uno no existe, pásalo como detalle:<área>=-).")
        elif "detalle" not in arch:
            sys.exit("Este tablero tiene aún el detalle de la 1.24.1: el paso e trae también detalle=<ruta de datos/detalle.json> (lo dice «datos.py rutas»).")
    for x in ARCHIVO_COLS + ("detalle", "propuestas", "enfoque"):
        _vacia(b / x)
    tab = arch.get("tablero") or {}
    for col in ARCHIVO_COLS:
        for id_, d in (tab.get(col) or {}).items():
            if isinstance(d, dict):
                _escribe(b / col / f"{id_}.json", {"id": id_, "data": d})
    if isinstance(tab.get("enfoque"), dict):
        _escribe(b / "enfoque" / "actual.json", {"id": "actual", "data": tab["enfoque"]})
    # el detalle, por área desde la 1.24.2 (datos/detalle/<área>.json) o entero en un tablero de la 1.24.1 (datos/detalle.json):
    # los dos son {proyecto: doc}. Se apunta qué archivos había, para quitar al publicar los que ya no tocan
    det = dict(arch.get("detalle") or {})
    for _a, d_ in (arch.get("detalle_areas") or {}).items():
        det.update(d_ or {})
    for id_, d in det.items():
        if isinstance(d, dict):
            _escribe(b / "detalle" / f"{id_}.json", {"id": id_, "data": d})
    _escribe(b / ".detalle-archivos.json", {"uno": "detalle" in arch, "areas": sorted(a_ for a_, d_ in (arch.get("detalle_areas") or {}).items() if d_ is not None)})
    (b / ".con-archivos").write_text("1", encoding="utf-8")
    props = {k: v for k, v in (arch.get("propuestas") or {}).items() if isinstance(v, dict)}
    marcas = {m["id"]: m for m in (_json(trabajo / "marcas.json") or []) if isinstance(m, dict) and m.get("id")}
    sobran = []
    for id_, m in marcas.items():
        md = m.get("data") or {}
        if id_ not in props and md.get("texto") and md.get("clase") and md.get("proyecto"):
            # una sugerencia de la 1.24.0, que vivía entera en la base: pasa al archivo, y su marca se queda encima
            props[id_] = {k: v for k, v in md.items() if k not in CAMPOS_MARCA + ("tipo",)}
            props[id_]["estado"] = "pendiente"
        if id_ not in props or md.get("estado") in (None, "pendiente"):
            sobran.append({"id": id_, "version": m.get("version")})     # sin sugerencia, o sin nada que decir: se borra
    for id_, d in props.items():
        _escribe(b / "propuestas" / f"{id_}.json", {"id": id_, "data": d})
        data = dict(d, tipo="propuesta")
        m = marcas.get(id_)
        quita = any(s["id"] == id_ for s in sobran)
        if m and not quita:
            for k in CAMPOS_MARCA:
                if k in (m.get("data") or {}):
                    data[k] = m["data"][k]
        _escribe(trabajo / "cola" / f"{id_}.json", {"id": id_, "version": m.get("version") if (m and not quita) else None, "data": data})
    _escribe(trabajo / "marcas-sobran.json", sobran)


def _cargar(b, col):
    d = b / col
    out = {}
    for p in sorted(d.glob("*.json")) if d.exists() else []:
        v = _datos(_json(p))
        if isinstance(v, dict):
            out[p.stem] = v
    return out


def _por_area(det):
    """{área: {proyecto: doc}}: el detalle partido por el área de cada proyecto (su id es <área>--<proyecto>)."""
    out = {}
    for pid, d in (det or {}).items():
        out.setdefault(str(pid).split("--", 1)[0], {})[pid] = d
    return out


def _lotes(ops, n=50):
    return [ops[i:i + n] for i in range(0, len(ops), n)]


def publicar(trabajo, args):
    trabajo = pathlib.Path(trabajo)
    vals, flags, arch = _opciones(args, ("--vista", "--enfoque"), ())
    if arch:
        sys.exit("publicar no lleva archivos: se arman con «datos.py base».")
    b, salida, pub = trabajo / "base", trabajo / "salida", trabajo / "publicar"
    plan = _json(salida / "plan.json")
    if not isinstance(plan, dict):
        sys.exit("Falta <trabajo>/salida/plan.json: corre antes plan_subida.py.")
    primera = (b / ".primera-vez").exists()
    if not primera and not (b / "meta" / "estado.json").exists():
        sys.exit("Falta lo publicado: corre antes «datos.py base <trabajo> estado=…» (o --primera-vez si el tablero no tiene archivos).")
    if primera and not vals.get("--vista"):
        sys.exit("La primera vez la página va con los datos: añade --vista <directorio de la skill>/vista.html.")
    con_archivos = primera or (b / ".con-archivos").exists()
    antes = {"estado": None if primera else _datos(_json(b / "meta" / "estado.json")),
             "tablero": {**{c: _cargar(b, c) for c in ARCHIVO_COLS}, "enfoque": _datos(_json(b / "enfoque" / "actual.json"))} if con_archivos else None,
             "propuestas": _cargar(b, "propuestas") if con_archivos else None,
             "detalle": _cargar(b, "detalle") if con_archivos else None}
    ahora = json.loads(json.dumps(antes))
    estado = dict(antes["estado"] or {})
    ops_marcas, sin_traer = [], []
    for e in [x for lote in plan.get("lotes") or [] for x in lote]:
        col, doc, op = e.get("collection"), e.get("doc_id"), e.get("op")
        data = _datos(_json(e["file_path"])) if e.get("file_path") else None
        if op in ("set", "update") and data is None:
            sys.exit(f"No puedo leer {e.get('file_path')} ({col}/{doc}): vuelve a correr la generación.")
        if col == "meta" and doc == "estado":
            estado = dict(estado, **data) if op == "update" else dict(data)
            continue
        if col == "cierres" and op == "delete":
            if e.get("if_version") is not None:
                ops_marcas.append({"op": "delete", "path": f"cierres/{doc}", "ifVersion": e["if_version"]})
            continue
        if not con_archivos:
            sin_traer.append(f"{col}/{doc}"); continue
        if col in ARCHIVO_COLS:
            if op == "delete":
                ahora["tablero"][col].pop(doc, None)
            else:
                ahora["tablero"][col][doc] = data
        elif col == "detalle":
            if op == "delete":
                ahora["detalle"].pop(doc, None)
            else:
                ahora["detalle"][doc] = data
        elif col == "enfoque":
            ahora["tablero"]["enfoque"] = None if op == "delete" else data
        elif col == "cambios":
            # las sugerencias viven en el archivo; su marca en la base (si alguien la tocó) se borra con ella
            if op == "delete":
                ahora["propuestas"].pop(doc, None)
                if e.get("if_version") is not None:
                    ops_marcas.append({"op": "delete", "path": f"cambios/{doc}", "ifVersion": e["if_version"]})
            else:
                ahora["propuestas"][doc] = {k: v for k, v in data.items() if k != "tipo"}
        else:
            sys.exit(f"El plan trae una escritura que no sé hacer: {op} {col}/{doc}.")
    if sin_traer:
        sys.exit("El plan cambia " + ", ".join(sin_traer[:5]) + " sin que se hayan traído los archivos del tablero: es una regeneración, y lleva el paso e.")
    # las marcas que se quedaron sin nada que decir (paso e): se borran, una vez y con su versión
    for s in _json(trabajo / "marcas-sobran.json") or []:
        if s.get("version") is not None and not any(o["path"] == f"cambios/{s['id']}" for o in ops_marcas):
            ops_marcas.append({"op": "delete", "path": f"cambios/{s['id']}", "ifVersion": s["version"]})
    enf = vals.get("--enfoque")
    if enf:
        if not con_archivos:
            sys.exit("«Por dónde empezar» se renueva al regenerar, con los archivos traídos en el paso e.")
        e_ = _json(enf)
        if not isinstance(e_, dict) or not isinstance(e_.get("grupos"), list):
            sys.exit(f"{enf} no tiene la forma de «Por dónde empezar» (falta «grupos»).")
        ahora["tablero"]["enfoque"] = e_
        h = _json(salida / "meta" / "estado-enfoque.json")
        if isinstance(h, dict) and h.get("huella_candidatos"):
            estado["huella_candidatos"] = h["huella_candidatos"]
    vista = vals.get("--vista")
    # la versión de la página publicada, para que la siguiente corrida no tenga que leerla
    if not isinstance(estado.get("pagina_actualizada"), dict) and estado.get("version_tablero") and (vista or not primera):
        estado["pagina_actualizada"] = {"version": estado["version_tablero"]}
    sinc = estado.get("sincronizado")
    # el id lleva el minuto del inventario y el instante de la corrida: dos puestas al día en el mismo minuto no comparten marca
    marca = "p" + re.sub(r"[^0-9]", "", str(sinc))[:12] + "-" + format(int(time.time() * 1000) % 10**8, "08d") if sinc else None
    previas = [x for x in (_json(trabajo / "publicado.json") or []) if isinstance(x, dict) and x.get("id")]
    cambia = {k for k in ("tablero", "propuestas", "detalle") if ahora[k] is not None and (primera or ahora[k] != antes[k])}
    # qué archivos de detalle tiene el tablero (1.24.2), para que el paso e de la siguiente corrida sepa cuáles traer
    # («datos.py rutas»); un tablero que sigue con el detalle.json de la 1.24.1 no lo lleva hasta que su detalle cambie
    # un tablero que sigue con el detalle.json único de la 1.24.1 pasa a un archivo por área en la primera regeneración,
    # cambie o no su detalle: si no, ese archivo podría crecer sin aviso hasta no poder traerse (revisión de la 1.24.2)
    previos_det = _json(b / ".detalle-archivos.json") or {}
    if con_archivos and ahora["detalle"] is not None and previos_det.get("uno"):
        cambia.add("detalle")
    por_a = _por_area(ahora["detalle"]) if ahora["detalle"] is not None else {}
    if con_archivos and ahora["detalle"] is not None:
        estado["detalle_areas"] = sorted(por_a)
    # solo la hora: nada de los archivos ni de meta/estado cambió salvo lo de la corrida (una regeneración que deja la
    # huella de la raíz nueva sí publica estado.json, o la siguiente volvería a regenerar)
    resto = lambda e: {k: v for k, v in (e or {}).items() if k not in CAMPOS_AL_DIA + ("publicado_id",)}
    solo_estado = not vista and not cambia and not primera and resto(estado) == resto(antes["estado"])
    if not solo_estado:
        estado["publicado_id"] = marca
    ahora["estado"] = estado
    _vacia(pub)
    pub.mkdir(parents=True, exist_ok=True)
    archivos = []

    def sale(nombre, obj):
        _escribe(pub / "datos" / nombre, obj)
        archivos.append({"as": f"datos/{nombre}", "path": str((pub / "datos" / nombre).resolve())})

    quitar = []
    if not solo_estado:
        sale("estado.json", estado)
        for k in ("tablero", "propuestas"):
            if k in cambia:
                sale(f"{k}.json", ahora[k])
        if "detalle" in cambia:
            # un archivo por área (1.24.2): solo salen las áreas cuyo detalle cambió, y se quitan las que ya no tienen y el
            # detalle.json único de la 1.24.1
            por_a0 = _por_area(antes["detalle"] or {})
            ya = set(previos_det.get("areas") or [])
            for a_, d_ in sorted(por_a.items()):
                if primera or a_ not in ya or d_ != por_a0.get(a_):
                    sale(f"detalle/{a_}.json", d_)
            quitar = [f"datos/detalle/{a_}.json" for a_ in sorted(ya - set(por_a))] + (["datos/detalle.json"] if previos_det.get("uno") else [])
    if vista:
        txt = pathlib.Path(vista).read_text(encoding="utf-8")
        if "<title>Tablero</title>" not in txt:
            sys.exit(f"{vista} no empieza por <title>Tablero</title>: ¿es la vista.html del plugin?")
        org = str(estado.get("organizacion") or "").strip()
        txt = txt.replace("<title>Tablero</title>", f"<title>{html.escape(('Tablero ' + org).strip())}</title>", 1)
        (pub / "index.html").write_text(txt, encoding="utf-8")
        archivos.insert(0, {"as": "index.html", "path": str((pub / "index.html").resolve())})
    # la base, en lotes que no se arrastran entre sí: primero la marca de esta publicación (un documento nuevo, que no
    # puede chocar con nada), después lo que borra esta corrida con las versiones que leyó, y al final las marcas viejas
    base = []
    if marca and not any(x["id"] == marca for x in previas):
        datos_marca = {"sincronizado": sinc}
        if solo_estado:
            # con la publicación que esta corrida dio por buena: si la página enseña otra, le toca recargar
            datos_marca.update({k: estado[k] for k in CAMPOS_AL_DIA if k in estado}, solo_estado=True, publicado_id=estado.get("publicado_id"))
        base.append([{"op": "set", "path": f"publicado/{marca}", "data": datos_marca}])
    base += _lotes(ops_marcas)
    base += _lotes([{"op": "delete", "path": f"publicado/{x['id']}", "ifVersion": x["version"]}
                    for x in previas if x["id"] != marca and x.get("version") is not None])
    salida_ = {"archivos": archivos, "base": base}
    if quitar:
        salida_["quitar"] = quitar
    if archivos:
        # el nombre del artifact: la publicación lo pasa como «title» si el de get_artifact es otro (« completo», de antes de la 1.18)
        salida_["titulo"] = ("Tablero " + str(estado.get("organizacion") or "").strip()).strip()
    # el paso e trae tablero, propuestas y el detalle de cada área en llamadas de 4 MiB como mucho: se mira cada archivo
    _peso = lambda o: len(json.dumps(o, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    pesos = {f"datos/{k}.json": _peso(ahora[k]) for k in ("tablero", "propuestas") if ahora[k] is not None}
    pesos.update({f"datos/detalle/{a_}.json": _peso(d_) for a_, d_ in por_a.items()})
    grandes = [f"{k} ({v // 1024} KB)" for k, v in pesos.items() if v > TOPE_LECTURA]
    if not grandes and sum(pesos.values()) > TOPE_LECTURA:
        # cada uno cabe, pero el paso e los trae juntos: se partirá en dos o más llamadas (revisión de la 1.24.2)
        grandes = [f"todos juntos ({sum(pesos.values()) // 1024} KB: el paso e los traerá en dos o más llamadas)"]
    if grandes:
        salida_["aviso"] = ("Pasa de 3,5 MB y la siguiente puesta al día puede no poder traerlo (read_file admite 4 MiB por "
                            "llamada): " + ", ".join(grandes) + ". Dilo en el resumen: esa área tiene demasiado detalle para un archivo, y hay que partirla en la versión siguiente del plugin (avísalo a quien lo mantiene).")
    print(json.dumps(salida_, ensure_ascii=False, indent=1))


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


def rutas(trabajo):
    """Paso e: los archivos que hay que traer, como lista JSON de rutas para read_file (paths), desde el meta/estado del paso
    1a: tablero.json, propuestas.json y el detalle de cada área que dice «detalle_areas»; sin esa clave (un tablero de la
    1.24.1), el detalle.json único."""
    est = _datos(_json(pathlib.Path(trabajo) / "base" / "meta" / "estado.json"))
    if not isinstance(est, dict):
        sys.exit("Falta el paso 1a (o es la primera vez, que no trae nada: --sin-archivos).")
    det = est.get("detalle_areas")
    r = ["datos/tablero.json", "datos/propuestas.json"] + ([f"datos/detalle/{a}.json" for a in det if ID_VALIDO.match(str(a))] if isinstance(det, list) else ["datos/detalle.json"])
    print(json.dumps(r, ensure_ascii=False))


def main():
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "rutas":
        rutas(a[1])
    elif len(a) == 3 and a[0] == "propuestas":
        propuestas(a[1], a[2])
    elif len(a) >= 2 and a[0] == "base":
        base(a[1], a[2:])
    elif len(a) >= 2 and a[0] == "publicar":
        publicar(a[1], a[2:])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
