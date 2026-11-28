#!/usr/bin/env python3
"""Calcula la entrada del seguimiento de un proyecto de desarrollo con lo que `recoger_github.py` leyó de GitHub.

Lee de la raíz la sección «Desarrollo» del `proyecto.md`, el plan, el diseño y la última entrada del seguimiento, junta
con ellos el JSON de cada repositorio y da a cada pieza su estado con la regla del plan («Cómo se sabe en qué estado
está cada pieza»): las mismas listas de GitHub dan siempre la misma entrada. Imprime la entrada con los siete puntos de
`plantillas/seccion-desarrollo.md`; el punto 4 (lo que lo unido añade y el diseño no tiene) es juicio y lo deja
«- pendiente de revisar»: lo llena el subagente `seguimiento` antes de guardar (shared-memory/plugin-memoria#2026-11-27-14).
Python 3.9, sin dependencias.

Uso:  seguimiento.py <raíz> <área/proyecto> --datos <json> [--datos <json> …] [--pidio "Nombre Apellido"] [--json] [--guardar]

  --datos    la salida de recoger_github.py, una por repositorio de «Repositorios:» (un repositorio sin la suya queda
             sin leer)
  --json     en lugar del texto, {"piezas", "fuera_del_plan", "kit", "sin_leer", "check_obligatorio", "punto4",
             "completa", "guardada"} (#2026-11-27-15)
  --guardar  escribe la entrada arriba del archivo de «Seguimiento:», sin tocar las anteriores, solo si está entera
  --punto4   un archivo con las líneas del punto 4 ya juzgadas («- <nombre> (<repositorio>#<número>)» o «- nada»): las
             pone en lugar de «- pendiente de revisar»

Sale con 0 si la entrada está entera, con 3 si algo dice «sin comprobar» (una lista cortada, un repositorio sin leer:
entonces no se guarda, porque su fecha diría que se comparó lo unido) y con 2 si no puede leer la raíz o los datos.
Que no se pueda leer la regla de la rama principal se dice en el punto 5 y no impide guardar.
"""
import argparse, datetime, json, pathlib, re, sys, unicodedata

ESTADOS = ("pendiente", "en curso", "unida", "revertida", "entregada")
SIN_COMPROBAR, SIN_ESTADO = "sin comprobar", "sin estado"
PUNTO4 = "4. Lo que lo unido añade y el diseño no tiene:"
SIN_REVISAR = "- pendiente de revisar"
ID = r"[A-Za-z]+\d+[A-Za-z]?"
CHECK = "pruebas de aceptación"
CONTROL = ".github/workflows/pruebas-aceptacion.yml"
POR_DEFECTO = {"ACEPTACION": "tests/aceptacion", "ACTIVAS": ".github/piezas-activas.txt", "CORREDOR": "pytest"}
APROBO = re.compile(r"Aprob[oó]\s*:\s*([^,\n]+?)\s*,\s*(\d{4}-\d{2}-\d{2})")


class Fallo(Exception):
    """La raíz, el proyecto o los datos no se pueden leer: sale con 2."""


def nfc(t):
    return unicodedata.normalize("NFC", t or "")


def clave(t):
    t = unicodedata.normalize("NFKD", t or "")
    return re.sub(r"\s+", " ", "".join(c for c in t if not unicodedata.combining(c))).strip().lower()


def pieza(raw):
    """«p02A» → «P02a», como lo leen el control y el tablero."""
    m = re.match(r"^([A-Za-z]+)(\d+)([A-Za-z]?)$", raw or "")
    return m.group(1).upper() + m.group(2) + m.group(3).lower() if m else raw


def leer(p):
    try:
        return nfc(p.read_bytes().decode("utf-8-sig", errors="replace").replace("\r\n", "\n"))
    except OSError:
        return None


# ---------- la fecha de hoy, en la zona de la organización ----------
def zona(raiz):
    """La «Zona horaria:» de guia.md (Ciudad de México si no la hay), como la leen abrir.py y cerrar.py."""
    g = leer(raiz / "guia.md") or ""
    m = re.search(r"^\s*[-*]?\s*\**\s*zona horaria\s*\**\s*:\s*\**\s*`?\s*([A-Za-z0-9_+-]+(?:/[A-Za-z0-9_+-]+){0,2})", g, re.M | re.I)
    try:
        from zoneinfo import ZoneInfo
    except ImportError:
        return None
    for nombre in ([m.group(1)] if m else []) + ["America/Mexico_City"]:
        try:
            return ZoneInfo(nombre)
        except Exception:
            continue
    return None


def hoy(raiz):
    tz = zona(raiz)
    if tz is None:   # sin base de zonas: Ciudad de México va en UTC-6 todo el año desde 2022
        tz = datetime.timezone(datetime.timedelta(hours=-6))
    return datetime.datetime.now(tz).date().isoformat()


# ---------- la memoria ----------
def secciones(texto):
    """{clave del título: (título, cuerpo)} de las secciones «## » de un texto."""
    out, nombre, cuerpo = {}, None, []
    for l in texto.split("\n"):
        m = re.match(r"^##\s+(.+?)\s*$", l)
        if m and not l.startswith("###"):
            if nombre is not None:
                out.setdefault(clave(nombre), (nombre, "\n".join(cuerpo)))
            nombre, cuerpo = m.group(1), []
        elif nombre is not None:
            cuerpo.append(l)
    if nombre is not None:
        out.setdefault(clave(nombre), (nombre, "\n".join(cuerpo)))
    return out


def personas(valor):
    """«Ana Pérez (ana@x.mx, @ana) · Luis» → [{"nombre", "correo", "usuario"}]."""
    out = []
    for trozo in [t.strip() for t in re.split(r"\s+·\s+", valor or "") if t.strip()]:
        m = re.match(r"^(.*?)\s*(?:\((.*)\))?$", trozo)
        nombre, dentro = m.group(1).strip(), m.group(2) or ""
        correo = next((x.strip() for x in dentro.split(",") if "@" in x and not x.strip().startswith("@")), "")
        usuario = next((x.strip()[1:] for x in dentro.split(",") if x.strip().startswith("@")), "")
        if nombre and clave(nombre) != "nadie":
            out.append({"nombre": nombre, "correo": correo, "usuario": usuario})
    return out


def seccion(raiz, proyecto):
    """La sección «Desarrollo» del proyecto: {clave: valor} con las claves tal como se escriben, en minúsculas y sin
    acentos («paso a prod», «repositorios»)."""
    texto = leer(raiz / proyecto / "proyecto.md")
    if texto is None:
        raise Fallo(f"no se puede leer {proyecto}/proyecto.md en {raiz}")
    s = secciones(texto).get("desarrollo")
    if s is None:
        raise Fallo(f"{proyecto}/proyecto.md no tiene la sección «## Desarrollo»: no es un proyecto de desarrollo")
    out = {}
    for l in s[1].split("\n"):
        m = re.match(r"^\s*([^:|#][^:]*?)\s*:\s*(.*?)\s*$", l)
        if m and not l.lstrip().startswith(("-", "*", ">")):
            out.setdefault(clave(m.group(1)), m.group(2))
    out["_repos"] = [r.strip() for r in re.split(r"\s+·\s+|,", out.get("repositorios", "")) if r.strip()]
    return out


def ruta(sec, nombre):
    v = (sec.get(nombre) or "").strip().strip("`")
    return None if not v or clave(v) == "por crear" else v


def tabla(lineas):
    """La primera tabla de unas líneas: (títulos, filas)."""
    filas, titulos, i = [], [], 0
    while i < len(lineas) and not lineas[i].strip().startswith("|"):
        i += 1
    for l in lineas[i:]:
        if not l.strip().startswith("|"):
            break
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if not titulos:
            titulos = c
        elif not all(re.fullmatch(r":?-+:?", x or "-") for x in c):
            filas.append(c)
    return titulos, filas


def ident(celda):
    m = re.match(r"^\s*(" + ID + r")\s*(?:[·:—-]\s*(.*))?$", (celda or "").strip().strip("*`"))
    return (pieza(m.group(1)), (m.group(2) or "").strip()) if m else ("", celda or "")


def leer_plan(texto):
    """{"fases": [{"id", "nombre", "estado", "en_llano", "recibio"}], "piezas": {id: {"nombre", "fase", "aprobo"}}}."""
    secs = secciones(texto)
    fases, piezas = [], {}
    nombre, cuerpo = secs.get("fases", ("", ""))
    t, filas = tabla(cuerpo.split("\n"))
    col = {clave(x): n for n, x in enumerate(t)}
    for f in filas:
        fid, fn = ident(f[0])
        if fid:
            fases.append({"id": fid, "nombre": fn, "estado": clave(f[col["estado"]]) if "estado" in col and col["estado"] < len(f) else "",
                          "en_llano": [], "recibio": ""})
    por_id = {f["id"]: f for f in fases}
    actual = None
    for l in cuerpo.split("\n"):
        m = re.match(r"^###\s+(" + ID + r")\s+(?:en llano|in plain words)\s*$", l.strip(), re.I)
        if m:
            actual = por_id.get(pieza(m.group(1)))
            continue
        if l.startswith("### "):
            actual = None
        elif actual is not None:
            r = re.match(r"^\s*Recibi[oó]\s*:\s*(.+)$", l)
            if r:
                actual["recibio"] = r.group(1).strip()
            else:
                actual["en_llano"].append(l)
    for f in fases:
        f["en_llano"] = "\n".join(f["en_llano"]).strip()
    t, filas = tabla(secs.get("piezas", ("", ""))[1].split("\n"))
    col = {clave(x): n for n, x in enumerate(t)}
    for f in filas:
        pid, pn = ident(f[0])
        if pid:
            piezas[pid] = {"nombre": pn, "fase": ident(f[col["fase"]])[0] if "fase" in col and col["fase"] < len(f) else "",
                           "aprobo": ""}
    actual = None
    for l in secs.get("hecha cuando", ("", ""))[1].split("\n"):
        m = re.match(r"^###\s+(" + ID + r")\b", l)
        if m:
            actual = piezas.get(pieza(m.group(1)))
        elif actual is not None and not actual["aprobo"]:
            a = re.match(r"^\s*\**\s*Aprob[oó]\s*\**\s*:\s*(.+)$", l)
            if a:
                actual["aprobo"] = a.group(1).strip()
    return {"fases": fases, "piezas": piezas}


def ultima_entrada(texto):
    """(fecha, {pieza: estado}) de la entrada más reciente del seguimiento."""
    mejor = ("", {})
    for nombre, cuerpo in secciones(texto or "").values():
        m = re.match(r"^(\d{4}-\d{2}-\d{2})\b", nombre)
        if not m or m.group(1) <= mejor[0]:
            continue
        estados, lineas = {}, cuerpo.split("\n")
        t, filas, col = [], [], {}
        while lineas:   # la tabla «| Pieza | Estado |», aunque antes vaya otra (la del bloque en llano)
            t, filas = tabla(lineas)
            col = {clave(x): n for n, x in enumerate(t)}
            if not t or ("pieza" in col and "estado" in col):
                break
            i = next(n for n, l in enumerate(lineas) if l.strip().startswith("|"))
            lineas = lineas[i + 2 + len(filas):]
        if "pieza" in col and "estado" in col:
            for f in filas:
                pid = ident(f[col["pieza"]])[0] if col["pieza"] < len(f) else ""
                if pid and col["estado"] < len(f):
                    estados[pid] = clave(f[col["estado"]])
        mejor = (m.group(1), estados)
    return mejor


# ---------- los pull requests ----------
def piezas_del_titulo(titulo):
    """Los identificadores con que empieza un título («P01 + P02 · …»), o []."""
    m = re.match(r"^\s*(" + ID + r"(?:\s*\+\s*" + ID + r")*)\s*·", titulo or "")
    return [pieza(x.strip()) for x in m.group(1).split("+")] if m else []


def es_bot(pr):
    return str(pr.get("user") or "").endswith("[bot]")


def control_de(datos):
    c = dict(POR_DEFECTO)
    leido = bool(datos.get("control"))
    c.update({k: v for k, v in (datos.get("control") or {}).items() if v})
    c["_leido"] = leido
    return c


def corredor_propio(c):
    v = (c.get("CORREDOR") or "").strip()
    return v[2:] if v.startswith("./") else (v if "/" in v else None)


def es_del_kit(archivo, c):
    """El kit: el CLAUDE.md, los workflows, el corredor propio y la configuración del repositorio (R6)."""
    a = archivo or ""
    return (a == "CLAUDE.md" or a.startswith(".github/workflows/") or a in ("CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS")
            or a in (".github/dependabot.yml", ".github/dependabot.yaml") or (corredor_propio(c) is not None and a == corredor_propio(c)))


def en_aceptacion(archivo, c):
    carpeta = (c.get("ACEPTACION") or "").strip("/")
    return bool(carpeta) and (archivo == carpeta or (archivo or "").startswith(carpeta + "/"))


def arnes(archivo, c):
    """Un archivo de la carpeta de aceptación que no es de ninguna pieza (no empieza por «P01_»): el arnés que van
    con el control en su «Kit · » (flujo.py, probar_control.py, el RESUMEN)."""
    return en_aceptacion(archivo, c) and not re.match(r"^" + ID + r"_", archivo.rsplit("/", 1)[-1])


def toca_pruebas(archivo, c):
    """Lo que cuenta en el punto 5: las pruebas de aceptación, su workflow, su corredor propio o la lista de activas."""
    return en_aceptacion(archivo, c) or archivo in (CONTROL, c.get("ACTIVAS")) or archivo == corredor_propio(c)


def clasificar(pr, ids_del_plan, c):
    """Qué es un pull request unido: ("pieza", [ids]), ("reversion", [ids]), ("escenarios", [ids]), ("kit", []),
    ("bot", []) o ("fuera", [motivo])."""
    titulo, archivos = pr.get("title") or "", pr.get("files") or []
    solo_workflows = bool(archivos) and all(a.startswith(".github/workflows/") for a in archivos)
    r = re.match(r'^\s*Revert\s+"(.*)"\s*$', titulo)
    if r:
        ids = piezas_del_titulo(r.group(1))
        fuera = [i for i in ids if i not in ids_del_plan]
        return ("fuera", [f"revierte {', '.join(fuera)}, que el plan no tiene"]) if fuera else ("reversion", ids)
    m = re.match(r"^\s*Escenarios\s*·\s*(.*)$", titulo)
    if m:
        ids = [pieza(x) for x in re.findall(ID, m.group(1).split("·")[0])]
        ajenos = [a for a in archivos if not en_aceptacion(a, c) and a != c.get("ACTIVAS")]
        if ajenos:
            return ("fuera", [f"«Escenarios · » que toca fuera de las pruebas de aceptación ({', '.join(ajenos[:3])})"])
        return ("escenarios", ids)
    if re.match(r"^\s*Kit\s*·", titulo):
        ajenos = [a for a in archivos if not es_del_kit(a, c) and a not in (c.get("ACTIVAS"), c.get("CONFIG"))
                  and not arnes(a, c)]
        if ajenos:
            return ("fuera", [f"«Kit · » que cambia código ({', '.join(ajenos[:3])})"])
        return ("kit", [])
    if solo_workflows:
        return ("kit", [])
    ids = piezas_del_titulo(titulo)
    if ids:
        ajenos = [i for i in ids if i not in ids_del_plan]
        return ("fuera", [f"nombra {', '.join(ajenos)}, que el plan no tiene"]) if ajenos else ("pieza", ids)
    if es_bot(pr):
        return ("bot", [])
    return ("fuera", ["sin pieza"])


def aprobo(texto):
    """(nombre, fecha) de la línea «Aprobó: Nombre Apellido, AAAA-MM-DD», o None."""
    m = APROBO.search(texto or "")
    return (m.group(1).strip(), m.group(2)) if m else None


# ---------- el cálculo ----------
def calcular(raiz, proyecto, datos_lista, pidio=""):
    sec = seccion(raiz, proyecto)
    plan_ruta, diseno_ruta, seg_ruta = ruta(sec, "plan"), ruta(sec, "diseno"), ruta(sec, "seguimiento")
    plan_txt = leer(raiz / plan_ruta) if plan_ruta else None
    if plan_txt is None:
        raise Fallo(f"no se puede leer el plan ({sec.get('plan') or 'la sección no lo nombra'})")
    plan = leer_plan(plan_txt)
    ids = list(plan["piezas"])
    fecha_ant, antes = ultima_entrada(leer(raiz / seg_ruta) if seg_ruta else "")
    paso = clave(sec.get("paso a prod", ""))
    unir_publica = bool(re.search(r"unir el pull request de version", paso))
    por_release = "release" in paso and not unir_publica
    construye = {clave(p["nombre"]) for p in personas(sec.get("construye"))}
    acepta = personas(sec.get("acepta"))

    por_repo = {}
    for d in datos_lista:
        por_repo.setdefault(d.get("repo"), d)
    sin_leer, leidos = [], []
    for repo in sec["_repos"] or list(por_repo):
        d = por_repo.get(repo)
        if d is None:
            sin_leer.append({"repo": repo, "motivo": "no se recogió con recoger_github.py"})
        elif not d.get("acceso"):
            sin_leer.append({"repo": repo, "motivo": d.get("motivo") or "sin acceso"})
        else:
            leidos.append(d)
    cortadas = [d["repo"] for d in leidos if not (d.get("completo") or {}).get("prs")]
    rel_cortados = [d["repo"] for d in leidos if por_release and not (d.get("completo") or {}).get("releases")]

    # cada pull request de pieza, en el orden en que se unió; los abiertos aparte
    eventos, abiertos, fuera, kit, escenarios, bots, tocan = [], {}, [], [], [], [], []
    for d in leidos:
        c = control_de(d)
        releases = [r for r in d.get("releases") or [] if aprobo(r.get("body"))]
        for p in d.get("prs") or []:
            n = p.get("number")
            if p.get("state") == "open" and not p.get("merged_at"):
                for i in piezas_del_titulo(p.get("title")):
                    abiertos.setdefault(i, []).append(f"{d['repo']}#{n}")
                continue
            if not p.get("merged_at"):
                continue
            tipo, que = clasificar(p, ids, c)
            ref = {"repo": d["repo"], "number": n, "title": p.get("title") or "", "merged_by": p.get("merged_by"),
                   "user": p.get("user")}
            if any(toca_pruebas(a, c) for a in p.get("files") or []):
                tocan.append(ref)
            if tipo == "fuera":
                fuera.append(dict(ref, motivo=que[0]))
            elif tipo == "kit":
                kit.append(ref)
            elif tipo == "escenarios":
                escenarios.append(dict(ref, piezas=que))
            elif tipo == "bot":
                bots.append(ref)
            else:
                si = None
                if tipo == "reversion":
                    pass
                elif unir_publica:
                    si = aprobo(p.get("body"))
                    si = {"como": "pull request", "nombre": si[0], "fecha": si[1]} if si else {"como": "pull request"}
                elif por_release:
                    for r in releases:
                        if p.get("merge_commit_sha") and p["merge_commit_sha"] in (r.get("contiene") or []):
                            a = aprobo(r.get("body"))
                            si = {"como": "release", "etiqueta": r.get("tag_name"), "nombre": a[0], "fecha": a[1]}
                            break
                eventos.append((p.get("merged_at"), tipo, que, dict(ref, si=si)))
    eventos.sort(key=lambda e: e[0] or "")

    estados, detalle = {}, {}
    for i in ids:
        estados[i] = antes.get(i) if antes.get(i) in ESTADOS else "pendiente"
    for _, tipo, que, ref in eventos:
        for i in que:
            if tipo == "reversion":
                estados[i], detalle[i] = "revertida", ref
            else:
                estados[i] = "entregada" if ref["si"] is not None else "unida"
                detalle[i] = ref
    for i in ids:
        if i in abiertos and estados[i] != "entregada":   # alguno abierto: en curso (lo entregado sigue entregado)
            estados[i] = "en curso"
    if not leidos:
        estados = {i: SIN_ESTADO for i in ids}
    elif cortadas:
        estados = {i: SIN_COMPROBAR for i in ids}
    elif rel_cortados:
        estados = {i: (SIN_COMPROBAR if e in ("unida", "entregada") else e) for i, e in estados.items()}

    reglas = [d.get("reglas") for d in leidos]
    if not leidos or any(r is None for r in reglas):
        check = False if any(isinstance(r, list) and not tiene_check(r) for r in reglas) else None
    else:
        check = all(tiene_check(r) for r in reglas)

    completa = bool(leidos) and not sin_leer and not cortadas and not rel_cortados
    return {"sec": sec, "plan": plan, "estados": estados, "detalle": detalle, "abiertos": abiertos, "fuera": fuera,
            "kit": kit, "escenarios": escenarios, "bots": bots, "tocan": tocan, "sin_leer": sin_leer, "leidos": leidos,
            "cortadas": cortadas, "rel_cortados": rel_cortados, "check": check, "completa": completa,
            "fecha_ant": fecha_ant, "unir_publica": unir_publica, "por_release": por_release, "construye": construye,
            "acepta": acepta, "pidio": pidio, "seg_ruta": seg_ruta, "diseno_ruta": diseno_ruta, "plan_ruta": plan_ruta,
            "proyecto": proyecto, "desde": min([d.get("desde") or "" for d in datos_lista] or [""])}


def tiene_check(reglas):
    for r in reglas or []:
        if isinstance(r, dict) and r.get("type") == "required_status_checks":
            for x in (r.get("parameters") or {}).get("required_status_checks") or []:
                if clave(x.get("context") if isinstance(x, dict) else x) == clave(CHECK):
                    return True
    return False


# ---------- la entrada ----------
def num(ref):
    return f"{ref['repo']}#{ref['number']}"


def quien(login, acepta):
    """Cómo se dice quién unió: «ana (quien acepta)», «luis, que no es quien acepta» o «sin saber quién»."""
    if not login:
        return "sin saber quién lo unió"
    usuarios = {clave(p["usuario"]) for p in acepta if p["usuario"]}
    if not usuarios:
        return f"lo unió {login}; quien acepta no tiene usuario de GitHub en la sección"
    return f"lo unió {login}" + ("" if clave(login) in usuarios else ", que no es quien acepta")


def entrada(x, hoy_, punto4=None):
    sec, plan, est = x["sec"], x["plan"], x["estados"]
    L = [f"## {hoy_}", ""]
    commits = "; ".join(f"{d['repo']} en {d.get('rama')} hasta {(d.get('ultimo_commit') or 'sin leer')[:12]}" for d in x["leidos"])
    sl = "; ".join(f"{s['repo']} sin leer: {s['motivo']}" for s in x["sin_leer"])
    desde = x["desde"] or x["fecha_ant"] or "sin fecha"
    L.append(f"1. Pidió: {x['pidio'] or 'sin decir'} · desde {desde}"
             + (f" (la entrada anterior es del {x['fecha_ant']})" if x["fecha_ant"] and x["fecha_ant"] != desde else "")
             + f" · {'; '.join(t for t in (commits, sl) if t) or 'ningún repositorio leído'}.")
    fase = next((f for f in plan["fases"] if f["estado"] == "en curso"), None) or \
        next((f for f in plan["fases"] if f["estado"] == "pendiente"), None)
    if fase and fase["en_llano"]:
        L += ["", f"Fase en curso, {fase['id']} · {fase['nombre']}:", "", fase["en_llano"]]
    L += ["", "2. Cada pieza:", "", "| Pieza | Estado |", "|---|---|"]
    for i, info in plan["piezas"].items():
        L.append(f"| {i} | {est.get(i, SIN_ESTADO)} |")
    notas = []
    for i, ref in sorted(x["detalle"].items()):
        if est.get(i) in (SIN_COMPROBAR, SIN_ESTADO):
            continue
        n = f"{i}: {est[i]} con {num(ref)}"
        si = ref.get("si") or {}
        if est[i] == "entregada" and si.get("nombre"):
            n += f", sí de {si['nombre']} el {si['fecha']}" + (f" en el release {si['etiqueta']}" if si.get("etiqueta") else "")
        elif est[i] == "entregada":
            n += ", sin la línea «Aprobó:» en su descripción"
        notas.append(n)
    for i, refs in sorted(x["abiertos"].items()):
        notas.append(f"{i}: abierto {', '.join(refs)}")
    if notas:
        L += [""] + [f"- {n}" for n in notas]
    if x["cortadas"]:
        L += ["", f"- sin comprobar: la lista de pull requests de {', '.join(x['cortadas'])} llegó al límite y puede faltar algo"]
    if x["rel_cortados"]:
        L += ["", f"- sin comprobar si se entregó: la lista de releases de {', '.join(x['rel_cortados'])} llegó al límite"]
    if not x["leidos"]:
        L += ["", "- sin estado: no se pudo leer ningún repositorio; son las piezas del plan"]
    L += ["", "3. Fuera del plan:"]
    if x["cortadas"]:
        L.append("- sin comprobar: sale de la misma lista, que llegó al límite")
    elif not x["leidos"]:
        L.append("- sin comprobar: no se leyó ningún repositorio")
    L += [f"- {num(f)} «{f['title']}»: {f['motivo']}" for f in x["fuera"]] or ([] if x["cortadas"] or not x["leidos"] else ["- nada"])
    aparte = [f"- {num(k)} «{k['title']}»: kit" for k in x["kit"]] + \
             [f"- {num(e)} «{e['title']}»: escenarios" for e in x["escenarios"]] + \
             [f"- {num(b)} «{b['title']}»: de un bot" for b in x["bots"]]
    if aparte:
        L += ["", "Aparte, sin contar para el estado:"] + aparte
    L += ["", PUNTO4] + (punto4 or [SIN_REVISAR])
    L += ["", "5. Las pruebas de aceptación:"]
    L.append("- el check «pruebas de aceptación» " + {True: "es obligatorio en la regla de la rama principal",
                                                      False: "no es obligatorio en la regla de la rama principal",
                                                      None: "sin comprobar: no se pudo leer la regla de la rama principal"}[x["check"]]
             + (f" ({'; '.join(d['reglas_motivo'] for d in x['leidos'] if d.get('reglas') is None and d.get('reglas_motivo'))})"
                if x["check"] is None and x["leidos"] else ""))
    for d in x["leidos"]:
        if not control_de(d)["_leido"]:
            L.append(f"- {d['repo']}: no se pudo leer {CONTROL}; la carpeta y la lista son las de la plantilla")
    for t in x["tocan"]:
        L.append(f"- {num(t)} «{t['title']}» tocó las pruebas de aceptación, su workflow o la lista de piezas activas; "
                 + quien(t.get("merged_by"), x["acepta"]))
    if not x["tocan"] and x["leidos"] and not x["cortadas"]:
        L.append("- ningún pull request unido tocó las pruebas de aceptación, su workflow ni la lista de piezas activas")
    L += ["", "6. Pasos a Prod:"]
    pasos = []
    vistos = set()
    for i, ref in sorted(x["detalle"].items()):
        si = ref.get("si")
        if si is None or num(ref) in vistos or est.get(i) in (SIN_COMPROBAR, SIN_ESTADO):
            continue
        vistos.add(num(ref))
        if si.get("nombre"):
            hecho = f"- {num(ref)} «{ref['title']}»: sí de {si['nombre']} el {si['fecha']}"
            if clave(si["nombre"]) in x["construye"]:
                hecho += "; lo dio quien construye"
            pasos.append(hecho)
        else:
            pasos.append(f"- {num(ref)} «{ref['title']}»: unido sin la línea «Aprobó:» en su descripción, sin sí")
    if not (x["unir_publica"] or x["por_release"]):
        pasos.append(f"- el sí no se lee en GitHub: «Paso a Prod» dice «{sec.get('paso a prod') or 'sin decir'}»")
    L += pasos or ["- ninguno desde la entrada anterior"]
    taller = x["proyecto"].rstrip("/") + "/taller"
    verifs = []
    raiz = x.get("_raiz")
    for i in sorted(x["detalle"]):
        if raiz is not None:
            verifs += sorted(p.name for p in (raiz / taller).glob(f"verificacion-{i}-*.md"))
    L.append(f"- verificaciones: {', '.join(verifs)}" if verifs else "- verificaciones: ninguna de las piezas unidas")
    L += ["", "7. Recibidas:"]
    if "recibe" in sec and personas(sec.get("recibe")):
        rec = [f"- {f['id']} · {f['nombre']}: {f['recibio']}" for f in plan["fases"] if f["recibio"]]
        L += rec or ["- ninguna fase recibida todavía"]
    else:
        L.append("- sin recibir por escrito")
    return "\n".join(L).rstrip() + "\n"


def para_json(x, punto4, guardada_):
    return {"piezas": dict(x["estados"]), "fuera_del_plan": [f["number"] for f in x["fuera"]],
            "kit": [k["number"] for k in x["kit"]], "sin_leer": x["sin_leer"], "check_obligatorio": x["check"],
            "punto4": [l for l in (punto4 or [SIN_REVISAR])], "completa": x["completa"], "guardada": guardada_}


# ---------- guardar ----------
CABECERA_NUEVA = """---
estado: vigente
actualizado: {hoy}
aportacion: "El seguimiento del desarrollo: cada pieza con su estado desde GitHub, lo fuera del plan y lo que el diseño no tiene."
basado_en:
{basado}
---

# Seguimiento

"""


def guardar(raiz, x, texto, hoy_):
    """Escribe la entrada arriba de las anteriores, sin tocarlas, y pone «actualizado:» a hoy. Devuelve la ruta y si
    el archivo es nuevo (con «Seguimiento: por crear», la ruta hay que ponerla en proyecto.md con cerrar.py)."""
    rel = x["seg_ruta"] or f"{x['proyecto'].rstrip('/')}/entregables/seguimiento.md"
    p = raiz / rel
    viejo = leer(p)
    nuevo = viejo is None
    if nuevo:
        basado = "\n".join(f"  - {r}" for r in (x["plan_ruta"], x["diseno_ruta"]) if r) or "  []"
        viejo = CABECERA_NUEVA.format(hoy=hoy_, basado=basado)
    m = re.search(r"^## \d{4}-\d{2}-\d{2}\b", viejo, re.M)
    if m:
        out = viejo[:m.start()] + texto + "\n" + viejo[m.start():]
    else:
        out = viejo.rstrip("\n") + "\n\n" + texto
    out = re.sub(r"^(actualizado:\s*).*$", lambda mm: mm.group(1) + hoy_, out, count=1, flags=re.M) \
        if out.startswith("---") else out
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(out, encoding="utf-8")
    tmp.replace(p)
    return rel, nuevo


def cargar_datos(rutas):
    out = []
    for r in rutas:
        try:
            d = json.loads(pathlib.Path(r).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise Fallo(f"no se pueden leer los datos de {r}: {e}")
        for x in (d if isinstance(d, list) else [d]):
            if not isinstance(x, dict) or not x.get("repo"):
                raise Fallo(f"{r} no es la salida de recoger_github.py")
            out.append(x)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="La entrada del seguimiento, calculada con lo leído de GitHub.")
    ap.add_argument("raiz")
    ap.add_argument("proyecto")
    ap.add_argument("--datos", action="append", default=[], required=True)
    ap.add_argument("--pidio", default="")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--guardar", action="store_true")
    ap.add_argument("--punto4")
    a = ap.parse_args(argv)
    raiz = pathlib.Path(a.raiz)
    try:
        x = calcular(raiz, a.proyecto.strip("/"), cargar_datos(a.datos), a.pidio)
        p4 = None
        if a.punto4:
            p4 = [l.rstrip() for l in (leer(pathlib.Path(a.punto4)) or "").split("\n") if re.match(r"\s*- \S", l)]
            if not p4:
                raise Fallo(f"{a.punto4} no trae ninguna línea «- …» para el punto 4")
    except Fallo as e:
        sys.stderr.write(f"seguimiento.py: {e}\n")
        return 2
    x["_raiz"] = raiz
    h = hoy(raiz)
    texto = entrada(x, h, p4)
    guardada_, aviso = False, ""
    if a.guardar and x["completa"]:
        rel, nuevo = guardar(raiz, x, texto, h)
        guardada_ = True
        aviso = f"Guardada arriba de {rel}." + (" El archivo es nuevo: pon su ruta en «Seguimiento:» de proyecto.md con "
                                                "cerrar.py." if nuevo else "")
    elif a.guardar:
        aviso = "No se guardó: algo quedó sin comprobar, y su fecha diría que se comparó lo unido."
    if a.json:
        sys.stdout.write(json.dumps(para_json(x, p4, guardada_), ensure_ascii=False) + "\n")
    else:
        sys.stdout.write(texto + (f"\n{aviso}\n" if aviso else ""))
    return 0 if x["completa"] else 3


if __name__ == "__main__":
    sys.exit(main())
