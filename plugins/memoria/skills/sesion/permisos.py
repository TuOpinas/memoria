#!/usr/bin/env python3
"""Compara los permisos reales de la carpeta compartida con lo que declara la raíz (guia.md, los area.md, las líneas
«Colabora:» de los proyectos y las carpetas restringido/). No escribe nada y no toca Drive: Claude lee los permisos
con el conector de Google Drive y se los pasa en un JSON. Lo usa la sesión del responsable de contexto (skill sesion,
anexo permisos.md).

Uso:
  permisos.py <raiz> --plan              qué carpetas hay que mirar en Drive (áreas, proyectos, restringido/)
  permisos.py <raiz> --drive drive.json  qué no cuadra, en llano, con lo que hay que cambiar en Drive

drive.json:
  {"raiz": {"permisos": [{"email": "...", "role": "organizer"}, ...]},
   "areas": {"<area>": {"permisos": [...], "limitada": false} | null},
   "proyectos": {"<area>/<proyecto>": {"permisos": [...], "limitada": false} | null},
   "restringidos": {"<area>/<proyecto>": {"permisos": [...], "limitada": true} | null}}
«limitada» es el inheritedPermissionsDisabled de la carpeta (acceso limitado); null, que no se encontró en Drive.
Los permisos de una carpeta incluyen los heredados de la unidad, como los da el conector.
"""
import json, pathlib, re, sys

# --- quién escribe: la celda Cuenta de guia.md y la línea «Colabora:» de un proyecto ---
# La misma función en abrir.py, aplicar_cambios.py, generar_vista.py y verificar.sh (cada uno se descarga suelto);
# pruebas/sesion/probar_cuentas.py comprueba que las cuatro copias son idénticas.
CORREO = re.compile(r"[\w.+'-]+@[\w-]+(?:\.[\w-]+)*")
PALABRA_COLABORA = re.compile(r"\bco-?labor\w*\s*:?", re.I)
LINEA_COLABORA = re.compile(r"^\s*[-*]?\s*\**\s*colabora[n]?\s*\**\s*:", re.I)
def cuentas(celda):
    """(dueño, colaboran, aviso) de una celda Cuenta: «dueno@x · colabora: a@x, b@x». Falla cerrado:
    con más de un correo antes de la palabra, o ninguno, nadie es dueño; cualquier palabra que empiece por
    «colabor» separa, para que «colaboradora:» o «colabora» sin dos puntos no conviertan a nadie en dueño."""
    texto = (celda or "").lower()
    partes = PALABRA_COLABORA.split(texto, maxsplit=1)
    antes = set(CORREO.findall(partes[0]))
    despues = set(CORREO.findall(partes[1])) if len(partes) > 1 else set()
    aviso = None
    if len(antes) > 1:
        aviso = "más de un correo antes de «colabora:»; nadie es dueño hasta que se corrija"
        antes = set()
    elif not antes:
        aviso = "sin el correo del dueño"
    elif len(partes) > 1 and not re.search(r"\bcolabora\s*:", texto):
        aviso = "la palabra para quien colabora va escrita «colabora:»"
    return antes, despues, aviso
def colaboran_en(quien):
    """Las cuentas de las líneas «Colabora:» de «Quién participa» de un proyecto (todas las líneas)."""
    return set(c for l in (quien or "").split("\n") if LINEA_COLABORA.match(l) for c in CORREO.findall(l.lower()))
# --- fin de quién escribe ---

ROL = {"organizer": "Administrador", "fileOrganizer": "Gestor de contenido", "writer": "Colaborador",
       "commenter": "Comentarista", "reader": "Lector", "owner": "Propietario"}
ROL_MI = {"owner": "Propietario", "writer": "Editor", "commenter": "Comentarista", "reader": "Lector"}
ESCRIBE = {"organizer", "fileOrganizer", "writer", "owner"}


def leer(p):
    try:
        return p.read_text(encoding="utf-8-sig")
    except OSError:
        return None


def seccion(texto, nombre):
    m = re.search(r"^##\s+" + re.escape(nombre) + r"\s*$(.*?)(?=^##\s|\Z)", texto or "", re.M | re.S)
    return m.group(1) if m else ""


def restringida_celda(celda):
    c = celda or ""
    if re.match(r"^[\W_]*restringid[oa]s?\b", c, re.I):
        return True
    return bool(re.search(r"\brestringidas?\b", c, re.I)) and not re.search(r"\b(?:nada|no|nunca|sin|antes)\s+(?:[^\s]+\s+)?restringid", c, re.I)


def solo_nombre(d):
    return re.sub(r"\s*\((?=[a-záéíóúñ`])[^)]*\)", "", d or "").strip()


def raiz_declarada(raiz):
    guia = leer(raiz / "guia.md") or ""
    areas, filas, cab = [], seccion(guia, "Áreas").split("\n"), False
    for l in filas:
        if not l.startswith("|") or re.match(r"^\|[\s:|-]+\|?\s*$", l):
            continue
        if not cab:
            cab = True; continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) >= 5:
            de, co, _ = cuentas(c[3])
            areas.append({"slug": c[0].strip("`").rstrip("/"), "nombre": c[0].strip("`").rstrip("/"), "dueno": solo_nombre(c[2]),
                          "duenos": de, "colaboran": co, "restringida": restringida_celda(c[4]), "lectores": c[4]})
    quien = seccion(guia, "Quién responde por qué")
    ctx, adm = "", ""
    for l in quien.split("\n"):
        s = l.strip().lstrip("-* ").strip()
        if s.lower().startswith("contexto común"):
            ctx = s.split(":", 1)[-1]
        elif s.lower().startswith("administra"):
            adm = s.split(":", 1)[-1]
    # cuenta de cada nombre, por la tabla de áreas (el dueño) y por los correos que la línea lleve entre paréntesis
    por_nombre = {}
    for a in areas:
        if a["dueno"] and len(a["duenos"]) == 1:
            por_nombre.setdefault(a["dueno"].lower(), set()).update(a["duenos"])
    def cuentas_de(linea):
        out = set(CORREO.findall(linea.lower()))
        nombres = re.sub(r"\([^)]*\)", "", linea)
        for n in re.split(r",|\by\b|\be\b|·", nombres):
            n = n.strip().rstrip(".").strip().lower()
            out |= por_nombre.get(n, set())
        return out
    admins, ctxc = cuentas_de(adm), cuentas_de(ctx)
    proyectos = []
    for a in areas:
        dir_a = raiz / a["slug"]
        if not dir_a.is_dir():
            continue
        lineas = {}
        for l in seccion(re.sub(r"^---.*?^---\s*$", "", leer(dir_a / "area.md") or "", count=1, flags=re.S | re.M), "Proyectos").split("\n"):
            m = re.match(r"^- `([^`/]+)/?`\s*[—–:-]?\s*(.*)$", l)
            if m:
                lineas[m.group(1)] = m.group(2)
        try:
            hijos = sorted(d for d in dir_a.iterdir() if d.is_dir() and not d.name.startswith("."))
        except OSError:
            hijos = []
        for d in hijos:
            pm = leer(d / "proyecto.md")
            if pm is None and d.name not in lineas:
                continue
            col = colaboran_en(seccion(pm or "", "Quién participa"))
            proyectos.append({"id": f"{a['slug']}/{d.name}", "area": a["slug"], "colaboran": col,
                              "restringido": bool(re.match(r"^[\W_]*restringid[oa]\b", lineas.get(d.name, ""), re.I)),
                              "tiene_restringido": (d / "restringido").is_dir()})
    return areas, proyectos, admins, ctxc, adm.strip(), ctx.strip()


def plan(raiz):
    areas, proyectos, admins, ctxc, adm, ctx = raiz_declarada(raiz)
    print("Carpetas que hay que mirar en Drive (permisos y si tienen acceso limitado):")
    print("- la raíz (la unidad compartida, o la carpeta raíz en «Mi unidad»)")
    for a in areas:
        print(f"- área {a['slug']}/" + (" (declarada restringida)" if a["restringida"] else ""))
    for p in proyectos:
        if p["colaboran"] or p["restringido"]:
            print(f"- proyecto {p['id']}/" + (" (con «Colabora:»)" if p["colaboran"] else "") + (" (declarado restringido)" if p["restringido"] else ""))
        if p["tiene_restringido"]:
            print(f"- restringido {p['id']}/restringido/")
    if not admins:
        print(f"(aviso: no se sabe la cuenta de quien administra la carpeta: «{adm or 'no consta'}» en guia.md)")


def comparar(raiz, drive):
    areas, proyectos, admins, ctxc, adm, ctx = raiz_declarada(raiz)
    raizp = (drive.get("raiz") or {}).get("permisos") or []
    mi_unidad = not any(x.get("role") in ("organizer", "fileOrganizer") for x in raizp) and any(x.get("role") == "owner" for x in raizp)
    NOM = ROL_MI if mi_unidad else ROL
    ESCRIBE_BIEN = {"writer", "owner"} if mi_unidad else {"organizer", "fileOrganizer"}
    BIEN = "«Editor»" if mi_unidad else "«Gestor de contenido»"
    def roles(perms):
        r = {}
        for x in perms or []:
            e = (x.get("email") or x.get("emailAddress") or "").lower()
            if e:
                r[e] = x.get("role", "")
        return r
    def admin(e, rol):
        return e in admins or (not admins and rol in ("organizer", "owner"))
    hall, notas = [], []
    rr = roles(raizp)
    if not raizp:
        hall.append("No llegaron los permisos de la raíz: sin ellos no se puede revisar nada. Vuelve a leerlos con el conector de Google Drive.")
    # 1. la raíz: quien no administra, solo lectura; quien administra, como dice guia.md
    escriben_en_raiz = set()
    for e, rol in sorted(rr.items()):
        if rol in ESCRIBE and not admin(e, rol):
            escriben_en_raiz.add(e)
            suyas = [a["slug"] for a in areas if e in a["duenos"] | a["colaboran"]]
            if suyas:
                hall.append(f"{e} tiene «{NOM.get(rol, rol)}» en toda la carpeta, así que puede escribir en todas las áreas. Cámbiale el rol a «Lector» en la raíz y dale {BIEN} solo en la carpeta de {', '.join(suyas)}.")
            else:
                hall.append(f"{e} tiene «{NOM.get(rol, rol)}» en toda la carpeta, así que puede escribir en todas las áreas, y no figura en guia.md como dueño ni colaborador de ninguna. Cámbiale el rol a «Lector» en la raíz; si debe escribir en un área, que el responsable de contexto lo declare en guia.md y dale {BIEN} en esa carpeta.")
    for e in sorted(admins):
        if rr and e not in rr:
            hall.append(f"{e} figura en guia.md como quien administra la carpeta, pero no tiene acceso a ella.")
        elif rr.get(e) and not mi_unidad and rr[e] != "organizer":
            hall.append(f"{e} figura en guia.md como quien administra la carpeta, pero en la unidad es «{NOM.get(rr[e], rr[e])}»: dale «Administrador».")
    declaradas = set()
    for a in areas:
        declaradas |= a["duenos"] | a["colaboran"]
    for p in proyectos:
        declaradas |= p["colaboran"]
    for e in sorted(declaradas | ctxc):
        if rr and e not in rr and not any(e in (a["duenos"] | a["colaboran"]) and a["restringida"] for a in areas):
            hall.append(f"{e} aparece en guia.md o en un proyecto, pero no tiene acceso a la carpeta: compártesela como «Lector».")
    # 2. cada área: escriben su dueño y quienes colaboran, nadie más
    for a in areas:
        info = (drive.get("areas") or {}).get(a["slug"])
        if info is None:
            if not a["restringida"] and (raiz / a["slug"]).is_dir():
                notas.append(f"El área {a['slug']}/ no se encontró en Drive con esta cuenta: puede faltar la carpeta o no tener acceso.")
            continue
        ar = roles(info.get("permisos"))
        for e in sorted(a["duenos"] | a["colaboran"]):
            rol = ar.get(e)
            papel = "dueño" if e in a["duenos"] else "colabora"
            if rol in ESCRIBE_BIEN:
                continue
            if rol == "writer" and not mi_unidad:
                hall.append(f"{e} ({papel} en {a['slug']}) tiene «Colaborador» en su área, que no deja mover ni borrar archivos: cámbialo a «Gestor de contenido» en la carpeta {a['slug']}.")
            else:
                hall.append(f"{e} ({papel} en {a['slug']}) no puede escribir en su área" + (f" (tiene «{NOM.get(rol, rol)}»)" if rol else " (no tiene acceso)") + f": dale {BIEN} en la carpeta {a['slug']}.")
        for e, rol in sorted(ar.items()):
            if rol in ESCRIBE and e not in a["duenos"] | a["colaboran"] and not admin(e, rol) and e not in escriben_en_raiz:
                hall.append(f"{e} puede escribir en {a['slug']} («{NOM.get(rol, rol)}») sin ser su dueño ni colaborar en ella: cámbiale el rol a «Lector» ahí, o que el responsable de contexto lo declare como colaborador en guia.md.")
        lim = bool(info.get("limitada"))
        if a["restringida"] and not lim:
            hall.append(f"El área {a['slug']}/ está declarada restringida en guia.md, pero en Drive no tiene acceso limitado: la lee todo el equipo. Márcala con acceso limitado desde la web.")
        elif lim and not a["restringida"]:
            hall.append(f"El área {a['slug']}/ tiene acceso limitado en Drive, pero guia.md no la declara restringida: escribe «Restringida: …» en su columna «Quién la lee», o quita el acceso limitado.")
        elif lim:
            fuera = sorted(e for e in ar if e not in a["duenos"] | a["colaboran"] and not admin(e, ar[e]))
            if fuera:
                notas.append(f"El área restringida {a['slug']}/ la leen además {', '.join(fuera)}; guia.md dice «{a['lectores']}». Compruébalo.")
    # 3. proyectos: quien colabora en uno escribe en su carpeta; los declarados restringidos, con acceso limitado
    for p in proyectos:
        info = (drive.get("proyectos") or {}).get(p["id"])
        if (p["colaboran"] or p["restringido"]) and info is None and p["id"] in (drive.get("proyectos") or {}):
            notas.append(f"El proyecto {p['id']}/ no se encontró en Drive con esta cuenta.")
        if info:
            pr = roles(info.get("permisos"))
            for e in sorted(p["colaboran"]):
                rol = pr.get(e)
                if rol not in ESCRIBE_BIEN:
                    hall.append(f"{e} colabora en {p['id']} pero no puede escribir en su carpeta" + (f" (tiene «{NOM.get(rol, rol)}»)" if rol else " (no tiene acceso)") + f": dale {BIEN} en la carpeta {p['id']}.")
            if p["restringido"] and not info.get("limitada"):
                hall.append(f"El proyecto {p['id']}/ está declarado restringido en su area.md, pero en Drive no tiene acceso limitado. Márcalo desde la web.")
        if p["tiene_restringido"] or p["id"] in (drive.get("restringidos") or {}):
            ri = (drive.get("restringidos") or {}).get(p["id"])
            if ri is not None and not ri.get("limitada"):
                hall.append(f"La carpeta restringido/ de {p['id']} no tiene acceso limitado en Drive: la lee todo el equipo. Márcala con acceso limitado desde la web.")
    print("=== PERMISOS")
    print(f"Tipo: {'«Mi unidad» (roles Lector y Editor)' if mi_unidad else 'unidad compartida'}")
    if not hall and not notas:
        print("Todo cuadra: los permisos de Drive son los que declara la carpeta.")
    if hall:
        print(f"Para cambiar en Drive ({len(hall)}):")
        for h in hall:
            print(f"- {h}")
    if notas:
        print("Para comprobar:")
        for n in notas:
            print(f"- {n}")


if __name__ == "__main__":
    if len(sys.argv) < 3 or not (pathlib.Path(sys.argv[1]) / "guia.md").is_file():
        sys.exit("Uso: permisos.py <raiz> --plan | --drive drive.json  (la raíz es la carpeta con guia.md y metodo.md)")
    R = pathlib.Path(sys.argv[1])
    if sys.argv[2] == "--plan":
        plan(R)
    elif sys.argv[2] == "--drive" and len(sys.argv) > 3:
        comparar(R, json.loads(pathlib.Path(sys.argv[3]).read_text(encoding="utf-8")))
    else:
        sys.exit("Uso: permisos.py <raiz> --plan | --drive drive.json")
