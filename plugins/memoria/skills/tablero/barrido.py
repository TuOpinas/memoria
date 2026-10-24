#!/usr/bin/env python3
"""El barrido de lo que las sesiones olvidaron: propuestas para la cola del tablero.

Corre dentro de la puesta al día del tablero (`regenerar.md`, paso 5f2), en el contenedor, sobre la copia que ya trae
solo lo que cambió desde la última vez, y no escribe en la carpeta: deja en <salida> lo que hay que subir a la
colección «cambios» del tablero, donde cada propuesta es un documento de tipo «propuesta». La memoria propone y solo
su dueño decide: una propuesta no cambia ningún archivo; la sesión que el dueño abre la enseña y el cierre escribe
lo que él acepta.

Uso:  barrido.py <copia> <salida> [--cola <volcado de «cambios»>] [--base <volcado de la base>] [--hoy AAAA-MM-DD] [--cuenta <correo>]
          con --base lee `juzgado` de su meta/estado: lo que el modelo ya vio en corridas anteriores y no dio propuesta
          (extractos que no eran decisión, piezas sin `afirma` que no se pudo decir, conjuntos ya contrastados) no se vuelve a pedir
          con --cuenta solo barre las áreas donde la cuenta es dueña o colabora (y los proyectos ajenos que la nombran en
          «Colabora:»): la memoria propone a quien puede escribir, y lo de otra área lo barre el tablero de su dueño.
          «hoy» es, si no se da, el `snapshot` de <salida>/meta/estado.json (el día en la zona de la organización, que
          el generador ya puso ahí) y, si tampoco está, el de esta máquina, que va en UTC: no es una fecha para escribir.
      barrido.py --cola-pendiente <volcado de «cambios»>   → imprime cuántos cambios de la cola NO son propuestas
      barrido.py --sumar-juicio <salida> <juicio.json> [--cola <volcado de «cambios»>]
          suma al barrido lo que el modelo juzgó: <juicio.json> es {"decisiones": [{"proyecto": "area--slug",
          "fecha": "AAAA-MM-DD", "decision": "una línea"}], "afirma": [{"ruta": "area/proyecto/entregables/x.md",
          "afirma": "una línea"}], "candidatos": [{"proyecto": "area--slug", "rutas": ["…", "…"], "entregable": "una línea"}],
          "contradicciones": [{"proyecto": "area--slug", "rutas": ["…", "…"], "texto": "una línea"}]}, solo de lo que
          «para_juicio», «para_afirma» y «para_contraste» pidieron (una lista sola vale como decisiones)

Detecta, con lo que está escrito y sin modelo:
  estado-desfasado  `proyecto.md` es más viejo que la última sesión que registra `sesiones.md`.
  paso-hecho        un paso de «Siguientes pasos» cuyas palabras casi todas están en «Avances:» de una de las dos últimas
                    sesiones: el registro parece darlo por hecho y el paso sigue ahí.
  rotacion          `sesiones.md` o `decisiones.md` pasa de 1.500 líneas, o su entrada más nueva es de otro año que la
                    más vieja: toca archivarlo (`escribir.md`, sección 8).
y deja para el modelo lo que solo un modelo puede decidir:
  para_juicio   las sesiones de los últimos días que cuentan una decisión («decidimos», «se acordó»…) cuando
                `decisiones.md` no tiene ninguna entrada de esa fecha.
  para_afirma   los entregables y los archivos del taller que no llevan `afirma:` (hasta 6 por corrida; entregables antes
                que taller, vigentes antes que borradores), con su título y, en los entregables, el arranque de su cuerpo,
                para que el modelo escriba la línea que dice qué sostienen. Del taller solo hay título y cabecera (la copia
                no trae su cuerpo, que es privado del área): si con eso no se puede decir qué sostiene, se salta.
  para_contraste los proyectos (hasta 5) con dos o más piezas con `afirma`, con esas líneas: el modelo dice qué piezas
                del taller podrían alimentar un entregable que no existe (candidatos) y qué dos piezas sostienen cosas
                incompatibles (contradicciones). Solo las líneas «afirma», nunca los cuerpos.

Cada propuesta tiene un id estable (`prop-<clase>-<huella>`): la misma observación no se vuelve a proponer, una que
el dueño descartó (estado «descartada») no vuelve, y una que ya no es cierta (el dueño puso al día lo que decía) se
borra de la cola. Solo se toca lo de los proyectos que vienen en la copia; los demás se dejan como están.

Salida, en <salida>: `barrido.json` con «anadir» (id y archivo), «borrar» (id y if_version), «para_juicio» y
«proyectos» (los que se barrieron), y un `cambios/<id>.json` por propuesta nueva. Todo texto va en una sola línea.
"""
import sys, re, json, pathlib, hashlib, datetime, unicodedata

STOP = set("de la el los las un una y o en a al del para por con sin que se su sus lo le les es son como más ya no si este esta esto "
           "esos esas pero cuando donde sobre entre desde hasta hay ser fue han había solo todo todos cada otro otra muy también "
           "paso pasos hacer hecho hacer queda quedó falta".split())
STOP = {"".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c) != "Mn") for w in STOP}
LIMITE_LINEAS = 1500
MAX_AFIRMA = 6
DATO_PERSONAL = re.compile(r"[\w.+'-]+@[\w-]+\.[\w.-]+|\b[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}\b|\b[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d\b|\b\d[\d .-]{9,}\d\b")
MAX_CONTRASTE = 5
NIEGA = re.compile(r"\b(no|falta|faltan|pendiente|pendientes|sin|todav[ií]a|a[úu]n|hasta que|queda|quedan|sigue|siguen)\b", re.I)
DECIDIO = re.compile(r"\b(decidimos|decidí|decidieron|se decidi[óo]|se acord[óo]|acordamos|quedó acordado|quedó decidido|elegimos|se eligi[óo]|aprobamos|se aprob[óo]|descartamos|se descart[óo])\b", re.I)


def una_linea(s, tope=300):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= tope else s[:tope - 1].rstrip() + "…"


def leer(p):
    try:
        return p.read_text(encoding="utf-8-sig")
    except OSError:
        return ""


def cabecera(texto):
    m = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", texto, re.S)
    out = {}
    for l in (m.group(1).split("\n") if m else []):
        k, _, v = l.partition(":")
        if _:
            out[k.strip()] = v.strip().strip("'\"")
    return out


def seccion(texto, nombre):
    m = re.search(r"^## " + re.escape(nombre) + r"\s*\n(.*?)(?=^## |\Z)", texto, re.S | re.M)
    return m.group(1) if m else ""


def fecha_ok(f):
    try:
        datetime.date.fromisoformat(f)
        return bool(re.fullmatch(r"20\d\d-\d\d-\d\d", f))
    except ValueError:
        return False


def entradas(texto):
    """[(fecha, titulo, cuerpo)] de un registro, en el orden del archivo."""
    out, parts = [], re.split(r"^## (?=\d{4}-\d{2}-\d{2})", texto, flags=re.M)
    for p in parts[1:]:
        cab, _, cuerpo = p.partition("\n")
        f = cab[:10]
        if fecha_ok(f):
            out.append((f, cab, cuerpo))
    return out


def campo(cuerpo, nombre):
    m = re.search(r"^" + nombre + r":\s*(.*?)(?=^\w[\wñáéíóú ]*:|\Z)", cuerpo, re.S | re.M)
    return m.group(1).strip() if m else ""


def palabras(t):
    """Raíces de las palabras con contenido (cuatro letras, sin tildes): «mandar» y «mandó» cuentan como la misma."""
    sin = unicodedata.normalize("NFD", t.lower())
    sin = "".join(c for c in sin if unicodedata.category(c) != "Mn" or c == "\u0303")
    return {w[:4] for w in re.findall(r"[a-zñ]{4,}", sin) if w not in STOP}


def pasos_de(texto):
    out = []
    for l in seccion(texto, "Siguientes pasos").split("\n"):
        if re.match(r"^\s*[-*]\s+\S", l):
            out.append(re.sub(r"^\s*[-*]\s+", "", l).strip())
    return out


def huella(*partes):
    return hashlib.sha1("\x1f".join(partes).encode("utf-8")).hexdigest()[:10]


def id_juicio(clase, pid, clave):
    return f"prop-{clase}-{huella(pid, clave)}"


def cargar_cola(carpeta):
    docs = []
    if carpeta and pathlib.Path(carpeta).exists():
        for p in sorted(pathlib.Path(carpeta).rglob("*.json")):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if not isinstance(d, dict):
                continue
            data = d["data"] if isinstance(d.get("data"), dict) else d
            docs.append({"id": d.get("id") or d.get("doc_id") or p.stem, "version": d.get("version"), "data": data})
    return docs


CORREO = re.compile(r"[\w.+'-]+@[\w-]+(?:\.[\w-]+)*")
PALABRA_COLABORA = re.compile(r"\bco-?labor\w*\s*:?", re.I)
LINEA_COLABORA = re.compile(r"^\s*[-*]?\s*\**\s*colabora[n]?\s*\**\s*:", re.I)


def areas_de_la_cuenta(copia, cuenta):
    """Las áreas donde la cuenta es dueña o colabora, por la columna Cuenta de guia.md (como aplicar_cambios.py); None sin cuenta."""
    if not cuenta:
        return None
    guia = leer(copia / "guia.md")
    m = re.search(r"^## Áreas\s*\n(.*?)(?=^## |\Z)", guia, re.S | re.M)
    out, primera = set(), True
    for l in (m.group(1).split("\n") if m else []):
        if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
            continue
        if primera:
            primera = False; continue
        celdas = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(celdas) >= 5:
            partes = PALABRA_COLABORA.split(celdas[3].lower(), maxsplit=1)
            if cuenta in set(CORREO.findall(partes[0])) | (set(CORREO.findall(partes[1])) if len(partes) > 1 else set()):
                out.add(celdas[0].strip("`").rstrip("/"))
    return out


def colabora_en(proy, cuenta):
    tp = leer(proy / "proyecto.md")
    m = re.search(r"^## Quién participa\s*\n(.*?)(?=^## |\Z)", tp, re.S | re.M)
    return bool(cuenta) and any(cuenta in CORREO.findall(l.lower()) for l in (m.group(1) if m else "").split("\n") if LINEA_COLABORA.match(l))


def proyectos_de(copia, cuenta=None):
    """Los proyectos que el barrido mira: con --cuenta, solo los de las áreas donde es dueña o colabora, y los proyectos
    ajenos donde su «Colabora:» la nombra. La memoria propone a quien puede escribir; lo de otra área lo barre su dueño."""
    mias = areas_de_la_cuenta(copia, cuenta)
    for area in sorted(p for p in copia.iterdir() if p.is_dir() and (p / "area.md").exists()):
        for proy in sorted(p for p in area.iterdir() if p.is_dir() and (p / "proyecto.md").exists()):
            if mias is not None and area.name not in mias and not colabora_en(proy, cuenta):
                continue
            yield area.name, proy


def zona_de(salida):
    """La zona horaria que el generador dejó en <salida>/meta/estado.json, o la de México; `creado` se estampa con ella."""
    try:
        from zoneinfo import ZoneInfo
        m = json.loads((pathlib.Path(salida) / "meta" / "estado.json").read_text(encoding="utf-8"))
        m = m.get("data", m) if isinstance(m, dict) and "data" in m else m
        return ZoneInfo((m or {}).get("zona") or "America/Mexico_City")
    except Exception:
        return datetime.timezone(datetime.timedelta(hours=-6))


def ahora_en(salida):
    return datetime.datetime.now(zona_de(salida)).isoformat(timespec="minutes")


def juzgado_de(base):
    """Lo que el modelo ya juzgó sin hallazgo, guardado en meta/estado por plan_subida.py: {"ids": [...], "contraste": [...]}."""
    try:
        d = json.loads((pathlib.Path(base) / "meta" / "estado.json").read_text(encoding="utf-8")) if base else {}
        d = d.get("data", d) if isinstance(d, dict) and "data" in d else d
        j = (d or {}).get("juzgado") or {}
        return {"ids": set(j.get("ids") or []), "contraste": set(j.get("contraste") or [])}
    except (OSError, ValueError):
        return {"ids": set(), "contraste": set()}


def id_contraste(pid, rutas):
    return id_juicio("contraste", pid, "contraste|" + "|".join(sorted(rutas)))


def piezas_de(salida, pid):
    """Las piezas de «Qué hay» que dejó el generador para el proyecto (entregables y taller, solo cabeceras), o []."""
    try:
        det = json.loads((salida / "detalle" / f"{pid}.json").read_text(encoding="utf-8"))
        return (det.get("que_hay") or {}).get("piezas") or []
    except (OSError, ValueError):
        return []


def barrer(copia, hoy, hay_propuesta=lambda i: False, salida=None, en_cola=lambda pid: [], cuenta=None, juzgado=None):
    juzgado = juzgado or {"ids": set(), "contraste": set()}
    visto = lambda i: hay_propuesta(i) or i in juzgado["ids"]      # ya propuesto, o ya juzgado sin hallazgo
    """(propuestas, para_juicio, para_afirma, para_contraste, vistos, ids de las propuestas de juicio que siguen siendo ciertas)."""
    props, juicio, afirma, contraste, vistos, validas = [], [], [], [], [], set()
    for area, proy in proyectos_de(copia, cuenta):
        pid = f"{area}--{proy.name}"
        vistos.append(pid)
        tp = leer(proy / "proyecto.md")
        ses_t, dec_t = leer(proy / "sesiones.md"), leer(proy / "decisiones.md")
        ses = entradas(ses_t)
        reales = [e for e in ses if "(tarea)" not in e[1]]
        cerrado = bool(re.search(r"Proyecto terminado el \d{4}-\d{2}-\d{2}", seccion(tp, "Estado actual")))

        def prop(clase, clave, texto, por_que):
            props.append({"id": f"prop-{clase}-{huella(pid, clave)}", "data": {
                "tipo": "propuesta", "clase": clase, "proyecto": pid, "texto": una_linea(texto), "por_que": una_linea(por_que),
                "origen": "barrido", "estado": "pendiente"}})

        # estado desfasado
        act = cabecera(tp).get("actualizado", "")
        if reales and not cerrado and fecha_ok(act):
            ultima = max(e[0] for e in reales)
            if act < ultima:
                prop("estado-desfasado", f"{act}>{ultima}",
                     f"Poner al día «Estado actual» y «Siguientes pasos»: son de {act} y la última sesión es de {ultima}.",
                     "proyecto.md es más viejo que la última entrada de sesiones.md")
        # pasos que el registro da por hechos: las palabras del paso están en una frase de Avances que no lo niega.
        # Se mira frase por frase, porque «revisamos la encuesta; falta mandarla» comparte las palabras del paso y dice lo contrario.
        if reales and not cerrado:
            for e in reales[:2]:
                frases = [f for f in re.split(r"[.;\n]+", campo(e[2], "Avances")) if f.strip()]
                if not frases:
                    continue
                for paso in pasos_de(tp):
                    pp = palabras(re.sub(r"\b20\d\d-\d\d-\d\d\b", " ", paso))
                    if len(pp) < 3:
                        continue
                    # la frase que coincide no lo niega, y la siguiente tampoco lo niega hablando de lo mismo («…; falta mandarla»)
                    hecho = any(len(pp & palabras(f)) >= 0.7 * len(pp) and not NIEGA.search(f)
                                and not (i + 1 < len(frases) and NIEGA.search(frases[i + 1]) and pp & palabras(frases[i + 1]))
                                for i, f in enumerate(frases))
                    if hecho:
                        # el id sale de las raíces del paso, no de su texto: fecharlo o retocarlo no lo convierte en otra observación
                        prop("paso-hecho", "|".join(sorted(pp)) + f"|{e[0]}",
                             f"Quitar de «Siguientes pasos»: «{una_linea(paso, 140)}». La sesión del {e[0]} parece darlo por hecho.",
                             f"sesiones.md ({e[0]}) lo cuenta en Avances")
        # rotación
        for nombre, texto, es in (("sesiones.md", ses_t, ses), ("decisiones.md", dec_t, entradas(dec_t))):
            n = texto.count("\n") + 1 if texto else 0
            anios = {e[0][:4] for e in es}
            if n > LIMITE_LINEAS or len(anios) > 1:
                motivo = f"pasa de {LIMITE_LINEAS} líneas" if n > LIMITE_LINEAS else "mezcla años"
                prop("rotacion", f"{nombre}|{motivo}", f"Archivar {nombre} por año: {motivo}.", "escribir.md, sección 8")
        # decisiones que se cuentan en una sesión y no están registradas
        fechas_dec = {e[0] for e in entradas(dec_t)}
        limite = (datetime.date.fromisoformat(hoy) - datetime.timedelta(days=14)).isoformat()
        # registrada el mismo día o el siguiente: el cierre acepta hoy o ayer, y una sesión que cruza la medianoche fecha la
        # bitácora un día y la decisión el otro
        registrada = lambda f: f in fechas_dec or (fecha_ok(f) and (datetime.date.fromisoformat(f) + datetime.timedelta(days=1)).isoformat() in fechas_dec)
        for e in reales:
            if not registrada(e[0]) and DECIDIO.search(" ".join(campo(e[2], k) for k in ("Trabajamos en", "Avances"))):
                validas.add(id_juicio("decision-sin-registrar", pid, "decision|" + e[0]))      # sigue siendo cierta mientras no se registre
        for e in reales[:3]:
            if e[0] >= limite and not registrada(e[0]):
                texto = " ".join(campo(e[2], k) for k in ("Trabajamos en", "Avances"))
                if DECIDIO.search(texto) and not visto(id_juicio("decision-sin-registrar", pid, "decision|" + e[0])):
                    juicio.append({"proyecto": pid, "fecha": e[0], "extracto": una_linea(texto, 600)})
        # entregables que no dicen qué sostienen (en un proyecto terminado ya no se pide: nadie lo va a abrir)
        for f in sorted((proy / "entregables").glob("*.md")) if (proy / "entregables").is_dir() and not cerrado else []:
            ft = leer(f)
            cab = cabecera(ft)
            if cab.get("estado") == "reemplazado" or cab.get("afirma", "").strip():
                continue
            ruta = f"{area}/{proy.name}/entregables/{f.name}"
            validas.add(id_juicio("afirma", pid, "afirma|" + ruta))
            if not visto(id_juicio("afirma", pid, "afirma|" + ruta)):
                cuerpo = re.sub(r"^---\s*\n.*?\n---\s*\n", "", ft, count=1, flags=re.S)
                titulo = next((l[2:].strip() for l in cuerpo.split("\n") if l.startswith("# ")), f.stem)
                arranque = " ".join(l.strip() for l in cuerpo.split("\n") if l.strip() and not l.startswith("#"))[:400]
                afirma.append({"proyecto": pid, "ruta": ruta, "titulo": una_linea(titulo, 120), "arranque": una_linea(arranque, 400), "_vigente": cab.get("estado") == "vigente"})
        # el taller: sus cabeceras las dejó el generador en el detalle; su cuerpo no está en la copia ni se lee nunca
        piezas = piezas_de(salida, pid) if salida else []
        if not any(pz.get("tipo") == "taller" for pz in piezas):
            # sin inventario del taller (sin consola, o un detalle que no lo trae), lo que nombra «/taller/» ni se juzga ni se retira
            for d in en_cola(pid):
                if "/taller/" in json.dumps(d["data"].get("rutas") or d["data"].get("ruta") or ""):
                    validas.add(d["id"])
        rutas = set()
        con_afirma = []
        for pz in piezas:
            ruta = f"{area}/{proy.name}/{'entregables' if pz.get('tipo') == 'entregable' else 'taller'}/{pz.get('archivo', '')}"
            rutas.add(ruta)
            if pz.get("afirma") and pz.get("estado") != "reemplazado":
                con_afirma.append({"ruta": ruta, "estado": pz.get("estado"), "afirma": una_linea(pz["afirma"], 240)})
            if pz.get("tipo") != "taller" or not str(pz.get("archivo", "")).endswith(".md") or pz.get("estado") == "reemplazado" or pz.get("afirma"):
                continue
            validas.add(id_juicio("afirma", pid, "afirma|" + ruta))
            if not visto(id_juicio("afirma", pid, "afirma|" + ruta)):
                afirma.append({"proyecto": pid, "ruta": ruta, "titulo": una_linea(pz.get("titulo") or pz.get("nombre") or "", 120),
                               "arranque": None, "_vigente": pz.get("estado") == "vigente", "_taller": True})
        # candidatos a entregable y contradicciones: solo un modelo los ve, sobre las líneas «afirma» (nunca los cuerpos)
        # el contraste se pide una vez por conjunto de piezas: si ese conjunto ya se juzgó (con o sin hallazgo), no se repite
        if len(con_afirma) >= 2 and len(contraste) < MAX_CONTRASTE and id_contraste(pid, [x["ruta"] for x in con_afirma[:20]]) not in juzgado["contraste"]:
            contraste.append({"proyecto": pid, "piezas": con_afirma[:20]})
        # una propuesta de candidato o de contradicción sigue valiendo mientras existan todas las piezas que nombra
        for d in en_cola(pid):
            if d["data"].get("clase") in ("candidato-entregable", "contradiccion") and set(d["data"].get("rutas") or []) <= rutas and d["data"].get("rutas"):
                validas.add(d["id"])
    afirma.sort(key=lambda x: (x.get("_taller", False), not x["_vigente"], x["ruta"]))
    afirma = [{k: v for k, v in x.items() if k not in ("_vigente", "_taller")} for x in afirma[:MAX_AFIRMA]]
    return props, juicio, afirma, contraste, vistos, validas


def sumar_juicio(salida, juicio, cola):
    """Convierte lo que el modelo juzgó en propuestas, sin dejarle escribir documentos de la cola: solo cuenta lo que el
    barrido pidió juzgar (mismo proyecto y misma fecha, o la misma ruta), con una línea de texto; lo ya propuesto no se repite."""
    bar = json.loads((salida / "barrido.json").read_text(encoding="utf-8"))
    if isinstance(juicio, list):
        juicio = {"decisiones": juicio}
    # todo lo que se puso delante del modelo queda juzgado, haya hallazgo o no: no se vuelve a pedir (plan_subida lo lleva a meta/estado)
    bar["juzgado"] = {"ids": sorted({id_juicio("decision-sin-registrar", j["proyecto"], "decision|" + j["fecha"]) for j in bar.get("para_juicio", [])}
                                    | {id_juicio("afirma", j["proyecto"], "afirma|" + j["ruta"]) for j in bar.get("para_afirma", [])}),
                      "contraste": sorted(id_contraste(c["proyecto"], [x["ruta"] for x in c["piezas"]]) for c in bar.get("para_contraste", []))}
    pedido = {(j["proyecto"], j["fecha"]) for j in bar.get("para_juicio", [])}
    pedido_afirma = {j["ruta"]: j["proyecto"] for j in bar.get("para_afirma", [])}
    pedido_contraste = {c["proyecto"]: {x["ruta"] for x in c["piezas"]} for c in bar.get("para_contraste", [])}
    ya = {d["id"] for d in cargar_cola(cola) if d["data"].get("tipo") == "propuesta"} | {x["id"] for x in bar["anadir"]}
    ahora = ahora_en(salida)
    nuevas = {"decisiones": 0, "afirma": 0, "candidatos": 0, "contradicciones": 0}

    def guardar(pid, data):
        (salida / "cambios").mkdir(parents=True, exist_ok=True)
        (salida / "cambios" / f"{pid}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        bar["anadir"].append({"id": pid, "archivo": f"cambios/{pid}.json"}); ya.add(pid)

    for j in juicio.get("decisiones", []) if isinstance(juicio.get("decisiones"), list) else []:
        if not isinstance(j, dict) or (j.get("proyecto"), j.get("fecha")) not in pedido:
            continue
        dec = una_linea(str(j.get("decision") or ""), 200)
        pid = id_juicio("decision-sin-registrar", j["proyecto"], "decision|" + j["fecha"])
        if not dec or pid in ya:
            continue
        guardar(pid, {"tipo": "propuesta", "clase": "decision-sin-registrar", "proyecto": j["proyecto"],
                      "texto": una_linea(f"Registrar en decisiones.md lo que la sesión del {j['fecha']} cuenta como decidido: {dec}"),
                      "por_que": "sesiones.md la narra y decisiones.md no tiene entrada de esa fecha", "origen": "barrido",
                      "estado": "pendiente", "creado": ahora})
        nuevas["decisiones"] += 1
    for j in juicio.get("afirma", []) if isinstance(juicio.get("afirma"), list) else []:
        if not isinstance(j, dict) or j.get("ruta") not in pedido_afirma:
            continue
        linea = una_linea(str(j.get("afirma") or "").replace('"', "'"), 200)
        if DATO_PERSONAL.search(linea):
            continue      # un correo, un RFC o CURP, una cuenta o un número largo no van a una línea que lee todo el que lee el área
        proy = pedido_afirma[j["ruta"]]
        pid = id_juicio("afirma", proy, "afirma|" + j["ruta"])
        if not linea or pid in ya:
            continue
        guardar(pid, {"tipo": "propuesta", "clase": "afirma", "proyecto": proy, "ruta": j["ruta"], "afirma": linea,
                      "texto": una_linea(f"Añadir a la cabecera de {j['ruta']}: afirma: «{linea}»"),
                      "por_que": "el inventario del tablero necesita saber qué sostiene cada pieza", "origen": "barrido",
                      "estado": "pendiente", "creado": ahora})
        nuevas["afirma"] += 1
    for clase, clave, campo_txt, cabeza, por_que in (
            ("candidato-entregable", "candidatos", "entregable", "Candidato a entregable", "varias piezas del taller sostienen lo mismo y ningún entregable lo recoge"),
            ("contradiccion", "contradicciones", "texto", "Contradicción", "dos piezas del proyecto sostienen cosas que no pueden ser ciertas a la vez")):
        for j in juicio.get(clave, []) if isinstance(juicio.get(clave), list) else []:
            if not isinstance(j, dict) or j.get("proyecto") not in pedido_contraste:
                continue
            rutas = sorted({str(r) for r in (j.get("rutas") or []) if isinstance(r, str)})
            if len(rutas) < 2 or not set(rutas) <= pedido_contraste[j["proyecto"]]:
                continue      # solo piezas que el barrido puso delante, y al menos dos
            linea = una_linea(str(j.get(campo_txt) or ""), 200)
            pid = id_juicio(clase, j["proyecto"], clase + "|" + "|".join(rutas))
            if not linea or pid in ya:
                continue
            cortas = ", ".join(r.split("/", 2)[-1] for r in rutas)
            guardar(pid, {"tipo": "propuesta", "clase": clase, "proyecto": j["proyecto"], "rutas": rutas,
                          "texto": una_linea(f"{cabeza}: {linea} (de {cortas})"), "por_que": por_que, "origen": "barrido",
                          "estado": "pendiente", "creado": ahora})
            nuevas[clave] += 1
    (salida / "barrido.json").write_text(json.dumps(bar, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"propuestas_nuevas_por_juicio": nuevas["decisiones"], "propuestas_afirma": nuevas["afirma"],
                      "propuestas_candidatos": nuevas["candidatos"], "propuestas_contradicciones": nuevas["contradicciones"]}, ensure_ascii=False))


def main():
    a = sys.argv[1:]
    if a and a[0] == "--sumar-juicio":
        opt = lambda n: a[a.index(n) + 1] if n in a and len(a) > a.index(n) + 1 else None
        sumar_juicio(pathlib.Path(a[1]), json.loads(pathlib.Path(a[2]).read_text(encoding="utf-8")), opt("--cola"))
        return
    if a and a[0] == "--cola-pendiente":
        docs = cargar_cola(a[1] if len(a) > 1 else None)
        print(sum(1 for d in docs if d["data"].get("tipo") != "propuesta"))
        return
    if len(a) < 2:
        sys.exit(__doc__)
    copia, salida = pathlib.Path(a[0]), pathlib.Path(a[1])
    opt = lambda n: a[a.index(n) + 1] if n in a and len(a) > a.index(n) + 1 else None
    hoy = opt("--hoy")
    if not hoy:
        try:
            m = json.loads((salida / "meta" / "estado.json").read_text(encoding="utf-8"))
            hoy = (m.get("data", m) if isinstance(m, dict) else {}).get("snapshot")
        except (OSError, ValueError):
            hoy = None
        hoy = hoy or datetime.date.today().isoformat()
    if not fecha_ok(hoy):
        sys.exit("--hoy no es una fecha AAAA-MM-DD")
    existentes = [d for d in cargar_cola(opt("--cola")) if d["data"].get("tipo") == "propuesta"]
    ya = {d["id"]: d for d in existentes}
    por_proyecto = {}
    for d in existentes:
        por_proyecto.setdefault(d["data"].get("proyecto"), []).append(d)
    props, juicio, afirma, contraste, vistos, validas = barrer(copia, hoy, lambda i: i in ya, salida, lambda pid: por_proyecto.get(pid, []),
                                                              (opt("--cuenta") or "").strip().lower() or None, juzgado_de(opt("--base")))
    nuevos_ids = {p["id"] for p in props} | validas      # las de juicio siguen valiendo mientras lo mecánico lo diga
    ahora = ahora_en(salida)
    (salida / "cambios").mkdir(parents=True, exist_ok=True)
    anadir = []
    for p in props:
        if p["id"] in ya:
            continue            # ya está (pendiente o descartada): no se vuelve a proponer
        p["data"]["creado"] = ahora
        (salida / "cambios" / f"{p['id']}.json").write_text(json.dumps(p["data"], ensure_ascii=False), encoding="utf-8")
        anadir.append({"id": p["id"], "archivo": f"cambios/{p['id']}.json"})
    borrar = []
    for d in existentes:
        if d["data"].get("proyecto") in vistos and d["id"] not in nuevos_ids:
            borrar.append({"id": d["id"], "if_version": d["version"]})
    (salida / "barrido.json").write_text(json.dumps(
        {"anadir": anadir, "borrar": borrar, "para_juicio": juicio, "para_afirma": afirma, "para_contraste": contraste, "proyectos": vistos}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"propuestas_nuevas": len(anadir), "propuestas_que_ya_no_valen": len(borrar), "para_juicio": len(juicio),
                      "para_afirma": len(afirma), "para_contraste": len(contraste), "proyectos_barridos": len(vistos)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
