#!/usr/bin/env python3
"""El barrido de lo que las sesiones olvidaron: propuestas para la cola del tablero.

Corre dentro de la puesta al día del tablero (`regenerar.md`, paso 5f2), en el contenedor, sobre la copia que ya trae
solo lo que cambió desde la última vez, y no escribe en la carpeta: deja en <salida> lo que hay que subir a la
colección «cambios» del tablero, donde cada propuesta es un documento de tipo «propuesta». La memoria propone y solo
su responsable decide: una propuesta no cambia ningún archivo; la sesión que el responsable abre la enseña y el cierre escribe
lo que él acepta.

Uso:  barrido.py <copia> <salida> [--cola <volcado de «cambios»>] [--base <volcado de la base>] [--hoy AAAA-MM-DD] [--cuenta <correo>]
          con --base lee `juzgado` de su meta/estado: lo que el modelo ya vio en corridas anteriores y no dio propuesta
          (extractos que no eran decisión, piezas sin `afirma` que no se pudo decir, conjuntos ya contrastados) no se vuelve a pedir
          con --cuenta solo barre las áreas donde la cuenta es responsable o colabora (y los proyectos ajenos que la nombran en
          «Colabora:»): la memoria propone a quien puede escribir, y lo de otra área lo barre el tablero de su responsable.
          «hoy» es, si no se da, el `snapshot` de <salida>/meta/estado.json (el día en la zona de la organización, que
          el generador ya puso ahí) y, si tampoco está, el de esta máquina, que va en UTC: no es una fecha para escribir.
      barrido.py --cola-pendiente <volcado de «cambios»>   → imprime cuántos cambios de la cola NO son propuestas
      barrido.py --sumar-juicio <salida> <juicio.json> [--cola <volcado de «cambios»>]
          suma al barrido lo que el modelo juzgó: <juicio.json> es {"decisiones": [{"proyecto": "area--slug",
          "fecha": "AAAA-MM-DD", "decision": "una línea"}], "afirma": [{"ruta": "area/proyecto/entregables/x.md",
          "afirma": "una línea"}], "candidatos": [{"proyecto": "area--slug", "rutas": ["…", "…"], "entregable": "una línea"}],
          "contradicciones": [{"proyecto": "area--slug", "rutas": ["…", "…"], "texto": "una línea"}],
          "resumenes": [{"proyecto": "area--slug", "publicado": "una o dos frases", "taller": "una o dos frases"}]}, solo de lo que
          «para_juicio», «para_afirma», «para_contraste» y «para_resumen» pidieron (una lista sola vale como decisiones)

Detecta, con lo que está escrito y sin modelo:
  estado-desfasado  `proyecto.md` es más viejo que la última sesión que registra `sesiones.md`.
  paso-hecho        un paso de «Siguientes pasos» cuyas palabras casi todas están en «Avances:» de una de las dos últimas
                    sesiones: el registro parece darlo por hecho y el paso sigue ahí.
  rotacion          `sesiones.md` o `decisiones.md` pasa de 1.500 líneas, o su entrada más nueva es de otro año que la
                    más vieja: toca archivarlo (`escribir.md`, sección 8).
y deja para el modelo lo que solo un modelo puede decidir:
  para_juicio   las sesiones de los últimos días que cuentan una decisión («decidimos», «se acordó»…) cuando
                `decisiones.md` no tiene ninguna entrada de esa fecha.
  para_afirma   los entregables y los archivos del taller que no llevan `afirma:` (hasta 24 por corrida; primero los de
                los proyectos con sesiones más recientes y, en cada uno, entregables antes que taller y vigentes antes que borradores), con su título y, en los entregables, el arranque de su cuerpo,
                para que el modelo escriba la línea que dice qué sostienen. Del taller solo hay título y cabecera (la copia
                no trae su cuerpo, que es privado del área): si con eso no se puede decir qué sostiene, se salta.
  para_contraste los proyectos (hasta 5) con dos o más piezas con `afirma`, con esas líneas: el modelo dice qué piezas
                del taller podrían alimentar un entregable que no existe (candidatos) y qué dos piezas sostienen cosas
                incompatibles (contradicciones). Solo las líneas «afirma», nunca los cuerpos.
  para_resumen  los proyectos (hasta 6, y unos 12 KB) de todo lo que lee la cuenta cuyo «Qué hay» cambió desde su
                último resumen escrito, o que no tienen ninguno, y que no se pidieron ya con la misma huella: título,
                estado y aportación de cada pieza, para que el modelo escriba dos frases,
                lo publicado y lo que hay en el taller (1.22.4). Se guardan en <salida>/resumenes/, no en la cola: no
                cambian la carpeta, solo lo que enseña la pestaña.

Cada propuesta tiene un id estable (`prop-<clase>-<huella>`): la misma observación no se vuelve a proponer, una que
el responsable descartó (estado «descartada») no vuelve, y una que ya no es cierta (el responsable puso al día lo que decía) se
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
MAX_AFIRMA = 24      # 1.22.3: el inventario necesita la línea de cada pieza; con 6 por corrida tardaba semanas
DATO_PERSONAL = re.compile(r"[\w.+'-]+@[\w-]+\.[\w.-]+|\b[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}\b|\b[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d\b|\b\d[\d .-]{9,}\d\b")
MAX_CONTRASTE = 5
MAX_RESUMEN = 6        # 1.22.4: los resúmenes de «Qué hay» que se piden por corrida, como mucho
BYTES_RESUMEN = 12000  # y lo que pesan juntas sus piezas: el tope es lo que entra al contexto del modelo
# la cola no crece sin tope (1.22.1, hallazgo 31 de la revisión de la 1.21): como mucho tantas propuestas pendientes por
# proyecto de las que se pueden volver a pedir (las mecánicas; las afirma, con su tope aparte), y una pendiente que una sesión posterior del
# proyecto dejó sin resolver durante tantos días se retira y queda juzgada, para que no vuelva igual
MAX_PENDIENTES = 8
# las «aportacion» pendientes llevan su propio tope (1.22.3): son muchas, se aceptan de golpe desde Qué hay y no deben
# quitarle hueco a lo mecánico
MAX_PENDIENTES_AFIRMA = 30
clave_pend = lambda proyecto, clase: f"{proyecto}|afirma" if clase == "afirma" else proyecto
CADUCIDAD_DIAS = 60
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
    """Las áreas donde la cuenta es responsable o colabora, por la columna Cuenta de guia.md (como aplicar_cambios.py); None sin cuenta."""
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
    """Los proyectos que el barrido mira: con --cuenta, solo los de las áreas donde es responsable o colabora, y los proyectos
    ajenos donde su «Colabora:» la nombra. La memoria propone a quien puede escribir; lo de otra área lo barre su responsable."""
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
        return {"ids": set(j.get("ids") or []), "contraste": set(j.get("contraste") or []), "resumenes": set(j.get("resumenes") or [])}
    except (OSError, ValueError):
        return {"ids": set(), "contraste": set(), "resumenes": set()}


def id_contraste(pid, rutas):
    return id_juicio("contraste", pid, "contraste|" + "|".join(sorted(rutas)))


def piezas_de(salida, pid):
    """Las piezas de «Qué hay» que dejó el generador para el proyecto (entregables y taller, solo cabeceras), o []."""
    try:
        det = json.loads((salida / "detalle" / f"{pid}.json").read_text(encoding="utf-8"))
        return (det.get("que_hay") or {}).get("piezas") or []
    except (OSError, ValueError):
        return []


def barrer(copia, hoy, hay_propuesta=lambda i: False, salida=None, en_cola=lambda pid: [], cuenta=None, juzgado=None, lleno=frozenset(), recientes=None, hueco=None):
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
        reales = [e for e in ses if "(tarea)" not in e[1] and "(migracion)" not in e[1]]
        cerrado = any(re.search(r"Proyecto terminado el \d{4}-\d{2}-\d{2}", seccion(tp, n_)) for n_ in ("Estatus", "Estado actual", "En corto"))
        reciente = max((e[0] for e in reales if fecha_ok(e[0])), default="")      # la última sesión real: el tope de afirma va primero a lo activo
        if recientes is not None:
            recientes[pid] = reciente      # y la caducidad de la cola solo cuenta si hubo sesión después de proponer

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
                     f"Poner al día «Estatus» y «Siguientes pasos»: son de {act} y la última sesión es de {ultima}.",
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
            if not registrada(e[0]) and DECIDIO.search(" ".join(campo(e[2], k) for k in ("Tema", "Trabajamos en", "Avances"))):
                validas.add(id_juicio("decision-sin-registrar", pid, "decision|" + e[0]))      # sigue siendo cierta mientras no se registre
        for e in reales[:3]:
            if e[0] >= limite and not registrada(e[0]):
                texto = " ".join(campo(e[2], k) for k in ("Tema", "Trabajamos en", "Avances"))
                if DECIDIO.search(texto) and not visto(id_juicio("decision-sin-registrar", pid, "decision|" + e[0])):
                    juicio.append({"proyecto": pid, "fecha": e[0], "extracto": una_linea(texto, 600)})
        # entregables que no dicen qué sostienen (en un proyecto terminado ya no se pide: nadie lo va a abrir)
        for f in sorted((proy / "entregables").glob("*.md")) if (proy / "entregables").is_dir() and not cerrado else []:
            ft = leer(f)
            cab = cabecera(ft)
            if cab.get("estado") == "reemplazado" or cab.get("aportacion", "").strip() or cab.get("afirma", "").strip():
                continue
            ruta = f"{area}/{proy.name}/entregables/{f.name}"
            validas.add(id_juicio("afirma", pid, "afirma|" + ruta))
            if not visto(id_juicio("afirma", pid, "afirma|" + ruta)):
                cuerpo = re.sub(r"^---\s*\n.*?\n---\s*\n", "", ft, count=1, flags=re.S)
                titulo = next((l[2:].strip() for l in cuerpo.split("\n") if l.startswith("# ")), f.stem)
                arranque = " ".join(l.strip() for l in cuerpo.split("\n") if l.strip() and not l.startswith("#"))[:400]
                afirma.append({"proyecto": pid, "ruta": ruta, "titulo": una_linea(titulo, 120), "arranque": una_linea(arranque, 400), "_vigente": cab.get("estado") == "vigente", "_reciente": reciente})
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
                               "arranque": None, "_vigente": pz.get("estado") == "vigente", "_taller": True, "_reciente": reciente})
        # candidatos a entregable y contradicciones: solo un modelo los ve, sobre las líneas «afirma» (nunca los cuerpos)
        # el contraste se pide una vez por conjunto de piezas: si ese conjunto ya se juzgó (con o sin hallazgo), no se repite
        if len(con_afirma) >= 2 and len(contraste) < MAX_CONTRASTE and id_contraste(pid, [x["ruta"] for x in con_afirma[:20]]) not in juzgado["contraste"]:
            contraste.append({"proyecto": pid, "piezas": con_afirma[:20]})
        # una propuesta de candidato o de contradicción sigue valiendo mientras existan todas las piezas que nombra
        for d in en_cola(pid):
            if d["data"].get("clase") in ("candidato-entregable", "contradiccion") and set(d["data"].get("rutas") or []) <= rutas and d["data"].get("rutas"):
                validas.add(d["id"])
    # el tope de MAX_AFIRMA, primero para los proyectos con sesiones más recientes (1.22.1: la primera puesta al día real
    # dio las seis a un solo proyecto por orden alfabético); dentro de cada uno, entregables antes que taller y vigentes antes
    afirma = [x for x in afirma if x["proyecto"] not in lleno]      # un proyecto ya al tope no recibe más: el modelo no lo juzga en balde
    afirma.sort(key=lambda x: x["ruta"])
    afirma.sort(key=lambda x: (x.get("_taller", False), not x["_vigente"]))
    afirma.sort(key=lambda x: x.get("_reciente") or "", reverse=True)
    # y a cada proyecto, como mucho los huecos que le quedan en la cola (1.22.3): lo que el tope tiraría no se juzga en balde
    usados, cabe = {}, []
    for x in afirma:
        lim = (hueco or {}).get(x["proyecto"], MAX_PENDIENTES_AFIRMA)
        if usados.get(x["proyecto"], 0) < lim:
            usados[x["proyecto"]] = usados.get(x["proyecto"], 0) + 1; cabe.append(x)
    afirma = [{k: v for k, v in x.items() if k not in ("_vigente", "_taller", "_reciente")} for x in cabe[:MAX_AFIRMA]]
    return props, juicio, afirma, contraste, vistos, validas


def sumar_juicio(salida, juicio, cola):
    """Convierte lo que el modelo juzgó en propuestas, sin dejarle escribir documentos de la cola: solo cuenta lo que el
    barrido pidió juzgar (mismo proyecto y misma fecha, o la misma ruta), con una línea de texto; lo ya propuesto no se repite."""
    bar = json.loads((salida / "barrido.json").read_text(encoding="utf-8"))
    if isinstance(juicio, list):
        juicio = {"decisiones": juicio}
    # todo lo que se puso delante del modelo queda juzgado, haya hallazgo o no: no se vuelve a pedir (plan_subida lo lleva a meta/estado)
    previo = bar.get("juzgado") or {}      # las caducadas que el barrido ya dejó juzgadas se conservan
    bar["juzgado"] = {"ids": sorted(set(previo.get("ids") or [])
                                    | {id_juicio("decision-sin-registrar", j["proyecto"], "decision|" + j["fecha"]) for j in bar.get("para_juicio", [])}
                                    | {id_juicio("afirma", j["proyecto"], "afirma|" + j["ruta"]) for j in bar.get("para_afirma", [])}),
                      "contraste": sorted(set(previo.get("contraste") or []) | {id_contraste(c["proyecto"], [x["ruta"] for x in c["piezas"]]) for c in bar.get("para_contraste", [])}),
                      # un resumen pedido no se vuelve a pedir con la misma huella, aunque el modelo lo saltara (revisión 1.22.4)
                      "resumenes": sorted(set(previo.get("resumenes") or []) | {f"{r['proyecto']}|{r['huella']}" for r in bar.get("para_resumen", [])})}
    # solo se guardan las huellas vigentes: la de otro «Qué hay» ya no frena nada y haría crecer meta/estado
    _vig = {f"{p_.stem}|{(_datos_doc(p_) or {}).get('que_hay_huella')}" for p_ in (salida / "proyectos").glob("*.json")} if (salida / "proyectos").exists() else set()
    if _vig:
        bar["juzgado"]["resumenes"] = [x for x in bar["juzgado"]["resumenes"] if x.removesuffix("|reintento") in _vig]
    pedido = {(j["proyecto"], j["fecha"]) for j in bar.get("para_juicio", [])}
    pedido_afirma = {j["ruta"]: j["proyecto"] for j in bar.get("para_afirma", [])}
    pedido_contraste = {c["proyecto"]: {x["ruta"] for x in c["piezas"]} for c in bar.get("para_contraste", [])}
    ya = {d["id"] for d in cargar_cola(cola) if d["data"].get("tipo") == "propuesta"} | {x["id"] for x in bar["anadir"]}
    ahora = ahora_en(salida)
    nuevas = {"decisiones": 0, "afirma": 0, "candidatos": 0, "contradicciones": 0}
    pendientes = dict(bar.get("pendientes") or {})      # las que el barrido dejó por proyecto, contando las suyas
    sin_hueco = set()

    def guardar(pid, data):
        # el tope solo frena lo que se puede volver a pedir sin perder nada (una línea aportacion); una decisión sin
        # registrar, un candidato o una contradicción entran siempre: son pocos y se piden una vez por conjunto
        k = clave_pend(data["proyecto"], data["clase"])
        if data["clase"] == "afirma" and pendientes.get(k, 0) >= MAX_PENDIENTES_AFIRMA:
            sin_hueco.add(pid)      # no entra, y se volverá a pedir cuando el proyecto tenga hueco
            return False
        pendientes[k] = pendientes.get(k, 0) + 1
        (salida / "cambios").mkdir(parents=True, exist_ok=True)
        (salida / "cambios" / f"{pid}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        bar["anadir"].append({"id": pid, "archivo": f"cambios/{pid}.json"}); ya.add(pid)
        return True

    for j in juicio.get("decisiones", []) if isinstance(juicio.get("decisiones"), list) else []:
        if not isinstance(j, dict) or (j.get("proyecto"), j.get("fecha")) not in pedido:
            continue
        dec = una_linea(str(j.get("decision") or ""), 200)
        pid = id_juicio("decision-sin-registrar", j["proyecto"], "decision|" + j["fecha"])
        if not dec or pid in ya:
            continue
        ok_ = guardar(pid, {"tipo": "propuesta", "clase": "decision-sin-registrar", "proyecto": j["proyecto"],
                      "texto": una_linea(f"Registrar en decisiones.md lo que la sesión del {j['fecha']} cuenta como decidido: {dec}"),
                      "por_que": "sesiones.md la narra y decisiones.md no tiene entrada de esa fecha", "origen": "barrido",
                      "estado": "pendiente", "creado": ahora})
        if ok_:
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
        ok_ = guardar(pid, {"tipo": "propuesta", "clase": "afirma", "proyecto": proy, "ruta": j["ruta"], "afirma": linea,
                      "texto": una_linea(f"Añadir a la cabecera de {j['ruta']}: aportacion: «{linea}»"),
                      "por_que": "el inventario del tablero necesita saber qué sostiene cada pieza", "origen": "barrido",
                      "estado": "pendiente", "creado": ahora})
        if ok_:
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
            ok_ = guardar(pid, {"tipo": "propuesta", "clase": clase, "proyecto": j["proyecto"], "rutas": rutas,
                          "texto": una_linea(f"{cabeza}: {linea} (de {cortas})"), "por_que": por_que, "origen": "barrido",
                          "estado": "pendiente", "creado": ahora})
            if ok_:
                nuevas[clave] += 1
    # los resúmenes de «Qué hay» (1.22.4): no son propuestas; van a <salida>/resumenes/ y al índice, para que la subida los lleve
    pedido_resumen = {r["proyecto"]: r["huella"] for r in bar.get("para_resumen", [])}
    n_res, rechazados = 0, []
    for j in juicio.get("resumenes", []) if isinstance(juicio.get("resumenes"), list) else []:
        if not isinstance(j, dict) or j.get("proyecto") not in pedido_resumen:
            continue
        ent, tal = una_linea(str(j.get("publicado") or ""), 320), una_linea(str(j.get("taller") or ""), 320)
        if not (ent or tal) or DATO_PERSONAL.search(ent + " " + tal):
            rechazados.append(f"{j['proyecto']}: {'vacío' if not (ent or tal) else 'parece llevar un dato personal'}")
            # uno rechazado por el filtro se vuelve a pedir una vez en la siguiente corrida; si vuelve a fallar, espera a que
            # cambie lo que hay (revisión 1.22.4, segunda vuelta)
            if ent or tal:
                clave_ = f"{j['proyecto']}|{pedido_resumen[j['proyecto']]}"
                if clave_ + "|reintento" not in (previo.get("resumenes") or []):
                    bar["juzgado"]["resumenes"] = [x for x in bar["juzgado"]["resumenes"] if x != clave_] + [clave_ + "|reintento"]
            continue
        doc = {"proyecto": j["proyecto"], "ent": ent, "tal": tal, "huella_qh": pedido_resumen[j["proyecto"]], "fecha": str(ahora)[:10]}
        doc["huella"] = hashlib.sha1(json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]
        (salida / "resumenes").mkdir(parents=True, exist_ok=True)
        ruta = salida / "resumenes" / f"{j['proyecto']}.json"
        ruta.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        ind_p = salida / "indice.json"
        try:
            ind = json.loads(ind_p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            ind = None
        if isinstance(ind, list):
            ind = [x for x in ind if not (x.get("coleccion") == "resumenes" and x.get("doc_id") == j["proyecto"])]
            ind.append({"coleccion": "resumenes", "doc_id": j["proyecto"], "archivo": f"resumenes/{j['proyecto']}.json", "huella": doc["huella"], "bytes": ruta.stat().st_size})
            ind_p.write_text(json.dumps(ind, ensure_ascii=False, indent=1), encoding="utf-8")
        n_res += 1
    bar["juzgado"]["ids"] = [i for i in bar["juzgado"]["ids"] if i not in sin_hueco]
    (salida / "barrido.json").write_text(json.dumps(bar, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"sin_hueco": len(sin_hueco), "propuestas_nuevas_por_juicio": nuevas["decisiones"], "propuestas_afirma": nuevas["afirma"],
                      "propuestas_candidatos": nuevas["candidatos"], "propuestas_contradicciones": nuevas["contradicciones"], "resumenes": n_res, "resumenes_rechazados": rechazados}, ensure_ascii=False))


def _datos_doc(p):
    try:
        d = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return d.get("data", d) if isinstance(d, dict) else None


def para_resumen(salida, base, vistos, juz=None):
    """Los proyectos cuyo «Qué hay» necesita un resumen escrito: todo lo que la cuenta lee, menos lo restringido y lo cerrado
    (el resumen solo usa títulos y aportaciones, que ya lee). Lo pedido queda juzgado con su huella y no se vuelve a pedir
    hasta que cambie, haya salido o no (revisión 1.22.4, hallazgo 4). Primero los que cambiaron en esta corrida, pero dos
    huecos son para los que nunca tuvieron resumen; tope de MAX_RESUMEN proyectos y BYTES_RESUMEN de piezas."""
    ya = (juz or {}).get("resumenes") or set()
    cambiados, nunca = [], []
    docs = sorted((salida / "proyectos").glob("*.json")) if (salida / "proyectos").exists() else []
    for p_ in docs:
        pd = _datos_doc(p_) or {}
        h = pd.get("que_hay_huella")
        if not h or pd.get("restringido") or pd.get("cerrado") or f"{p_.stem}|{h}" in ya:
            continue
        previo = _datos_doc(pathlib.Path(base) / "resumenes" / f"{p_.stem}.json") if base else None
        if previo and previo.get("huella_qh") == h:
            continue
        det = _datos_doc(salida / "detalle" / f"{p_.stem}.json") or {}
        qh = det.get("que_hay") if isinstance(det.get("que_hay"), dict) else pd.get("que_hay") if isinstance(pd.get("que_hay"), dict) else {}
        piezas = qh.get("piezas") or []
        if not piezas:
            continue
        item = {"proyecto": p_.stem, "huella": h, "nombre": pd.get("nombre") or p_.stem,
                "piezas": [{k: v for k, v in {"tipo": z.get("tipo"), "titulo": una_linea(z.get("titulo") or z.get("nombre") or "", 120),
                                              "estado": z.get("estado"), "aportacion": una_linea(z.get("afirma") or "", 220)}.items() if v}
                           for z in piezas[:30]]}
        (cambiados if p_.stem in vistos or previo else nunca).append(item)
    # los dos huecos de los que nunca tuvieron resumen van primero, para que los que cambiaron no llenen antes los bytes; uno
    # que no cabe se salta y se prueba con el siguiente (revisión 1.22.4, segunda vuelta)
    orden = nunca[:2] + cambiados[:MAX_RESUMEN - 2]
    orden += [x for x in cambiados + nunca if x not in orden]
    out, peso = [], 0
    for x in orden:
        b = len(json.dumps(x, ensure_ascii=False).encode("utf-8"))
        if len(out) >= MAX_RESUMEN:
            break
        if out and peso + b > BYTES_RESUMEN:
            continue
        out.append(x); peso += b
    return out


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
    juz = juzgado_de(opt("--base"))
    previas = {}
    for d in existentes:
        # las aceptadas ya no esperan juicio: no ocupan hueco en la cola (1.22.3)
        if d["data"].get("estado") not in ("descartada", "aceptada"):
            k = clave_pend(d["data"].get("proyecto"), d["data"].get("clase"))
            previas[k] = previas.get(k, 0) + 1
    recientes = {}
    props, juicio, afirma, contraste, vistos, validas = barrer(copia, hoy, lambda i: i in ya, salida, lambda pid: por_proyecto.get(pid, []),
                                                              (opt("--cuenta") or "").strip().lower() or None, juz,
                                                              lleno={k[:-7] for k, v in previas.items() if k.endswith("|afirma") and v >= MAX_PENDIENTES_AFIRMA}, recientes=recientes,
                                                              hueco={k[:-7]: max(0, MAX_PENDIENTES_AFIRMA - v) for k, v in previas.items() if k.endswith("|afirma")})
    nuevos_ids = {p["id"] for p in props} | validas      # las de juicio siguen valiendo mientras lo mecánico lo diga
    ahora = ahora_en(salida)
    # caduca una pendiente de hace más de CADUCIDAD_DIAS si su proyecto tuvo después una sesión real que no la resolvió
    # (la sesión la enseña al abrir): se retira y queda juzgada, para que no vuelva igual. Una que nadie pudo ver, porque
    # su proyecto no tuvo sesión, no caduca; una aceptada desde el tablero tampoco (1.22.3): la espera el próximo cierre.
    lim = (datetime.date.fromisoformat(hoy) - datetime.timedelta(days=CADUCIDAD_DIAS)).isoformat()
    caducadas = {d["id"] for d in existentes if d["data"].get("estado") not in ("descartada", "aceptada") and fecha_ok(str(d["data"].get("creado") or "")[:10])
                 and str(d["data"]["creado"])[:10] < lim and recientes.get(d["data"].get("proyecto"), "") > str(d["data"]["creado"])[:10]}
    pendientes = {}
    for d in existentes:
        if d["data"].get("estado") not in ("descartada", "aceptada") and d["id"] not in caducadas and (d["data"].get("proyecto") not in vistos or d["id"] in nuevos_ids):
            k = clave_pend(d["data"].get("proyecto"), d["data"].get("clase"))
            pendientes[k] = pendientes.get(k, 0) + 1
    (salida / "cambios").mkdir(parents=True, exist_ok=True)
    anadir, sin_hueco = [], 0
    for p in props:
        if p["id"] in ya or p["id"] in juz["ids"]:
            continue            # ya está (pendiente o descartada), o caducó sin que nadie la resolviera: no se vuelve a proponer
        k = clave_pend(p["data"]["proyecto"], p["data"].get("clase"))
        if pendientes.get(k, 0) >= MAX_PENDIENTES:
            sin_hueco += 1; continue      # el proyecto ya tiene bastantes pendientes: entra cuando se resuelvan
        pendientes[k] = pendientes.get(k, 0) + 1
        p["data"]["creado"] = ahora
        (salida / "cambios" / f"{p['id']}.json").write_text(json.dumps(p["data"], ensure_ascii=False), encoding="utf-8")
        anadir.append({"id": p["id"], "archivo": f"cambios/{p['id']}.json"})
    borrar = []
    for d in existentes:
        # una aceptada desde el tablero la espera el cierre, aunque lo mecánico deje de proponerla (1.22.3). Solo se retira la
        # aceptada de «aportacion» cuya pieza ya la tiene (la escribió el cierre o alguien a mano): ya no hay nada que aplicar
        if d["data"].get("estado") == "aceptada":
            if d["data"].get("clase") == "afirma" and d["data"].get("proyecto") in vistos and d["id"] not in nuevos_ids:
                borrar.append({"id": d["id"], "if_version": d["version"]})
            continue
        if (d["data"].get("proyecto") in vistos and d["id"] not in nuevos_ids) or d["id"] in caducadas:
            borrar.append({"id": d["id"], "if_version": d["version"]})
    resumen = para_resumen(salida, opt("--base"), set(vistos), juz)
    (salida / "barrido.json").write_text(json.dumps(
        {"anadir": anadir, "borrar": borrar, "para_juicio": juicio, "para_afirma": afirma, "para_contraste": contraste, "para_resumen": resumen, "proyectos": vistos,
         "pendientes": pendientes, "juzgado": {"ids": sorted(caducadas), "contraste": [], "resumenes": sorted(x for x in juz["resumenes"] if x.endswith("|reintento"))}}, ensure_ascii=False, indent=1), encoding="utf-8")
    cuenta = {"propuestas_nuevas": len(anadir), "propuestas_que_ya_no_valen": len(borrar), "caducadas": len(caducadas), "sin_hueco": sin_hueco, "para_juicio": len(juicio),
              "para_afirma": len(afirma), "para_contraste": len(contraste), "para_resumen": len(resumen), "proyectos_barridos": len(vistos)}
    # lo que el modelo tiene que juzgar viaja en la misma salida: no hace falta leer barrido.json (revisión 1.22.4, hallazgo 20)
    juzgar = {k: v for k, v in (("para_juicio", juicio), ("para_afirma", afirma), ("para_contraste", contraste), ("para_resumen", resumen)) if v}
    if juzgar:
        cuenta["juzgar"] = juzgar
    print(json.dumps(cuenta, ensure_ascii=False))


if __name__ == "__main__":
    main()
