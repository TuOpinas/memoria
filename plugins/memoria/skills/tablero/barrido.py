#!/usr/bin/env python3
"""El barrido de lo que las sesiones olvidaron: propuestas para la cola del tablero.

Corre dentro de la puesta al día del tablero (`regenerar.md`, paso 5f2), en el contenedor, sobre la copia que ya trae
solo lo que cambió desde la última vez, y no escribe en la carpeta: deja en <salida> lo que hay que subir a la
colección «cambios» del tablero, donde cada propuesta es un documento de tipo «propuesta». La memoria propone y solo
su dueño decide: una propuesta no cambia ningún archivo; la sesión que el dueño abre la enseña y el cierre escribe
lo que él acepta.

Uso:  barrido.py <copia> <salida> [--cola <volcado de «cambios»>] [--hoy AAAA-MM-DD]
          «hoy» es, si no se da, el `snapshot` de <salida>/meta/estado.json (el día en la zona de la organización, que
          el generador ya puso ahí) y, si tampoco está, el de esta máquina, que va en UTC: no es una fecha para escribir.
      barrido.py --cola-pendiente <volcado de «cambios»>   → imprime cuántos cambios de la cola NO son propuestas
      barrido.py --sumar-juicio <salida> <juicio.json> [--cola <volcado de «cambios»>]
          suma al barrido las decisiones que el modelo juzgó: <juicio.json> es una lista de
          {"proyecto": "area--slug", "fecha": "AAAA-MM-DD", "decision": "una línea"}, solo de lo que «para_juicio» pidió

Detecta, con lo que está escrito y sin modelo:
  estado-desfasado  `proyecto.md` es más viejo que la última sesión que registra `sesiones.md`.
  paso-hecho        un paso de «Siguientes pasos» cuyas palabras casi todas están en «Avances:» de una de las dos últimas
                    sesiones: el registro parece darlo por hecho y el paso sigue ahí.
  rotacion          `sesiones.md` o `decisiones.md` pasa de 1.500 líneas, o su entrada más nueva es de otro año que la
                    más vieja: toca archivarlo (`escribir.md`, sección 8).
y deja en «para_juicio» lo que solo un modelo puede decidir: las sesiones de los últimos días que cuentan una decisión
(«decidimos», «se acordó»…) cuando `decisiones.md` no tiene ninguna entrada de esa fecha.

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


def proyectos_de(copia):
    for area in sorted(p for p in copia.iterdir() if p.is_dir() and (p / "area.md").exists()):
        for proy in sorted(p for p in area.iterdir() if p.is_dir() and (p / "proyecto.md").exists()):
            yield area.name, proy


def barrer(copia, hoy):
    props, juicio, vistos = [], [], []
    for area, proy in proyectos_de(copia):
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
        # pasos que el registro da por hechos
        if reales and not cerrado:
            for e in reales[:2]:
                av = campo(e[2], "Avances")
                pav = palabras(av)
                if not pav:
                    continue
                for paso in pasos_de(tp):
                    pp = palabras(re.sub(r"\b20\d\d-\d\d-\d\d\b", " ", paso))
                    if len(pp) >= 3 and len(pp & pav) >= 0.7 * len(pp):
                        prop("paso-hecho", f"{paso}|{e[0]}",
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
        for e in reales[:3]:
            if e[0] >= limite and e[0] not in fechas_dec:
                texto = " ".join(campo(e[2], k) for k in ("Trabajamos en", "Avances"))
                if DECIDIO.search(texto):
                    juicio.append({"proyecto": pid, "fecha": e[0], "extracto": una_linea(texto, 600)})
    return props, juicio, vistos


def sumar_juicio(salida, juicio, cola):
    """Convierte lo que el modelo juzgó en propuestas, sin dejarle escribir documentos de la cola: solo cuenta lo que el
    barrido pidió juzgar (mismo proyecto y misma fecha), con una línea de texto; lo ya propuesto no se repite."""
    bar = json.loads((salida / "barrido.json").read_text(encoding="utf-8"))
    pedido = {(j["proyecto"], j["fecha"]) for j in bar.get("para_juicio", [])}
    ya = {d["id"] for d in cargar_cola(cola) if d["data"].get("tipo") == "propuesta"} | {x["id"] for x in bar["anadir"]}
    ahora = datetime.datetime.now().astimezone().isoformat(timespec="minutes")
    nuevas = 0
    for j in juicio if isinstance(juicio, list) else []:
        if not isinstance(j, dict) or (j.get("proyecto"), j.get("fecha")) not in pedido:
            continue
        dec = una_linea(str(j.get("decision") or ""), 200)
        if not dec:
            continue
        pid = f"prop-decision-sin-registrar-{huella(j['proyecto'], 'decision|' + j['fecha'])}"
        if pid in ya:
            continue
        data = {"tipo": "propuesta", "clase": "decision-sin-registrar", "proyecto": j["proyecto"],
                "texto": una_linea(f"Registrar en decisiones.md lo que la sesión del {j['fecha']} cuenta como decidido: {dec}"),
                "por_que": "sesiones.md la narra y decisiones.md no tiene entrada de esa fecha", "origen": "barrido",
                "estado": "pendiente", "creado": ahora}
        (salida / "cambios").mkdir(parents=True, exist_ok=True)
        (salida / "cambios" / f"{pid}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        bar["anadir"].append({"id": pid, "archivo": f"cambios/{pid}.json"}); ya.add(pid); nuevas += 1
    (salida / "barrido.json").write_text(json.dumps(bar, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"propuestas_nuevas_por_juicio": nuevas}, ensure_ascii=False))


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
    props, juicio, vistos = barrer(copia, hoy)
    existentes = [d for d in cargar_cola(opt("--cola")) if d["data"].get("tipo") == "propuesta"]
    ya = {d["id"]: d for d in existentes}
    nuevos_ids = {p["id"] for p in props}
    ahora = datetime.datetime.now().astimezone().isoformat(timespec="minutes")
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
        {"anadir": anadir, "borrar": borrar, "para_juicio": juicio, "proyectos": vistos}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"propuestas_nuevas": len(anadir), "propuestas_que_ya_no_valen": len(borrar),
                      "para_juicio": len(juicio), "proyectos_barridos": len(vistos)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
