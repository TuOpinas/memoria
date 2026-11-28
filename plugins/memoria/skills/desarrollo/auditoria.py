#!/usr/bin/env python3
"""La auditoría mensual de la configuración: propone, con su evidencia, el estado de lo que GitHub deja ver.

Con lo que `recoger_github.py --auditoria` leyó de cada repositorio, propone el estado de R1 (sin pull request no se
llega a la rama principal, solo squash y nadie se salta la regla), R2 (el check «pruebas de aceptación» es obligatorio),
R3 (el control de secretos es obligatorio), R6 (cada pull request unido desde la última auditoría empieza por su pieza,
«Escenarios · », «Kit · », es una reversión o de un bot), PL1 (la organización pide verificación en dos pasos y tiene un
plan de pago) y PL2 (dos personas administran), y lista lo que la API no ve, para quien administra. Lo que no puede leer
lo dice «sin comprobar», con el motivo: nunca lo adivina. No escribe nada sin --escribir, que es el sí de quien acepta:
entonces cambia esas filas en el archivo de «Configuración de plataforma» y de «Configuración de repositorios» con la
fecha de hoy, en una sola escritura por archivo, sin tocar las demás. Python 3.9, sin dependencias.

Uso:  auditoria.py <raíz> <área/proyecto> --datos <json> [--datos <json> …] [--json] [--escribir]

  --json      en lugar del texto, {"filas": {"R1": {"estado", "evidencia"}, …}, "sin_api": ["PL3", …], "escrita"}
              (#2026-11-27-15); con varios repositorios, las filas de repositorio van como «R1 · owner/repo»

Sale con 0, con 3 si alguna fila queda «sin comprobar» y con 2 si no puede leer la raíz, la configuración o los datos.
"""
import argparse, json, pathlib, re, sys

sys.path.append(str(pathlib.Path(__file__).resolve().parent))   # seguimiento.py, a su lado: la misma lectura de la memoria
import seguimiento as S  # noqa: E402

CUMPLE, NO_CUMPLE, SIN = "cumple", "no cumple", "sin comprobar"
PLATAFORMA, REPOSITORIO = ("PL1", "PL2"), ("R1", "R2", "R3", "R6")
FILA = re.compile(r"^\s*\|\s*((?:PL|R)\d+)\s*\|")


def regla(reglas, tipo):
    return next((r for r in reglas or [] if isinstance(r, dict) and r.get("type") == tipo), None)


def checks(reglas):
    r = regla(reglas, "required_status_checks")
    return [x.get("context") if isinstance(x, dict) else x for x in ((r or {}).get("parameters") or {}).get("required_status_checks") or []]


def r1(d):
    if d.get("reglas") is None:
        return SIN, d.get("reglas_motivo") or "no se pudo leer la regla de la rama principal"
    rama = d.get("rama") or "la rama principal"
    pr = regla(d["reglas"], "pull_request")
    if pr is None:
        return NO_CUMPLE, f"la regla de {rama} no exige pull request"
    metodos = (pr.get("parameters") or {}).get("allowed_merge_methods")
    aj = d.get("ajustes") or {}
    solo_squash = metodos == ["squash"] or (aj.get("allow_squash_merge") and aj.get("allow_merge_commit") is False
                                            and aj.get("allow_rebase_merge") is False)
    if not solo_squash:
        return NO_CUMPLE, (f"la regla de {rama} exige pull request pero deja unir con {', '.join(metodos or ['cualquier método'])}"
                           " y el repositorio no admite solo squash")
    if d.get("bypass") is None:
        return SIN, f"la regla de {rama} exige pull request y solo squash; quién se la puede saltar: {d.get('bypass_motivo') or 'sin leer'}"
    if d["bypass"]:
        quien = ", ".join(str(b.get("actor_type") or "") + (f" {b.get('actor_id')}" if b.get("actor_id") else "")
                          for b in d["bypass"] if isinstance(b, dict))
        return NO_CUMPLE, f"la regla de {rama} exige pull request y solo squash, pero se la pueden saltar: {quien}"
    return CUMPLE, f"la regla de {rama} exige pull request, solo squash, y nadie se la puede saltar"


def r2(d):
    if d.get("reglas") is None:
        return SIN, d.get("reglas_motivo") or "no se pudo leer la regla de la rama principal"
    rama = d.get("rama") or "la rama principal"
    cs = checks(d["reglas"])
    if any(S.clave(c) == S.clave(S.CHECK) for c in cs):
        return CUMPLE, f"la regla de {rama} exige los checks: {', '.join(cs)}"
    return NO_CUMPLE, (f"la regla de {rama} exige {('los checks: ' + ', '.join(cs)) if cs else 'ningún check'}; "
                       f"falta «{S.CHECK}»")


def r3(d):
    if d.get("reglas") is None:
        return SIN, d.get("reglas_motivo") or "no se pudo leer la regla de la rama principal"
    cs = checks(d["reglas"])
    s = [c for c in cs if "secret" in S.clave(c)]
    if s:
        return CUMPLE, f"el control de secretos es obligatorio: {', '.join(s)}"
    return NO_CUMPLE, f"ningún check obligatorio es de secretos ({', '.join(cs) or 'no hay checks obligatorios'})"


def r6(d, ids):
    desde = d.get("desde") or "la última auditoría"
    if not (d.get("completo") or {}).get("prs"):
        return SIN, f"la lista de pull requests desde {desde} llegó al límite: puede faltar alguno"
    c = S.control_de(d)
    malos = []
    for p in d.get("prs") or []:
        if not p.get("merged_at"):
            continue
        tipo, que = S.clasificar(p, ids, c)
        if tipo == "fuera" and (que[0] == "sin pieza" or que[0].startswith("«Kit · »")):
            malos.append(f"#{p['number']} «{p.get('title')}» ({que[0]})")
    if malos:
        return NO_CUMPLE, f"unidos desde {desde} sin el identificador de su pieza: {'; '.join(malos)}"
    return CUMPLE, f"todos los pull requests unidos desde {desde} empiezan por su pieza, «Escenarios · » o «Kit · », son reversiones o de bots"


def pl1(d):
    o = d.get("organizacion")
    if o is None:
        m = d.get("organizacion_motivo") or "no se pudo leer la organización"
        return (NO_CUMPLE if "cuenta personal" in m else SIN), m
    if o.get("dos_pasos") is None:
        return SIN, (f"la organización {o.get('login')} no deja ver si pide verificación en dos pasos: hace falta "
                     "el token de quien la administra")
    if o.get("dos_pasos") is False:
        return NO_CUMPLE, f"la organización {o.get('login')} no pide verificación en dos pasos"
    plan = o.get("plan")
    if not plan:
        return SIN, f"la organización {o.get('login')} pide verificación en dos pasos; su plan no se deja ver"
    if S.clave(plan) == "free":
        return NO_CUMPLE, f"la organización {o.get('login')} pide verificación en dos pasos, pero su plan (free) no permite reglas en repositorios privados"
    return CUMPLE, f"la organización {o.get('login')} pide verificación en dos pasos y su plan es {plan}"


def pl2(d):
    o = d.get("organizacion")
    if o is None:
        m = d.get("organizacion_motivo") or "no se pudo leer la organización"
        return (NO_CUMPLE if "cuenta personal" in m else SIN), m
    ps = [p for p in o.get("propietarios") or [] if p]
    if len(ps) >= 2:
        return CUMPLE, f"administran la organización {o.get('login')}: {', '.join(ps)}"
    if not o.get("propietarios_completo", True):
        return SIN, f"la lista de propietarios de {o.get('login')} llegó al límite"
    return NO_CUMPLE, f"administra la organización {o.get('login')} solo {', '.join(ps) or 'nadie que se vea'}"


# ---------- la configuración ----------
def tablas(texto):
    """[(línea de títulos, [nº de línea de cada fila PL*/R*])] de las tablas del archivo."""
    out, lineas = [], texto.split("\n")
    i = 0
    while i < len(lineas):
        if lineas[i].strip().startswith("|"):
            j = i
            while j < len(lineas) and lineas[j].strip().startswith("|"):
                j += 1
            filas = [n for n in range(i + 2, j) if FILA.match(lineas[n])]
            if filas:
                out.append((i, filas))
            i = j
        else:
            i += 1
    return out


def celdas(linea):
    return [x.strip() for x in linea.strip().strip("|").split("|")]


def columna(titulos, repo, n_repos):
    """La columna de un repositorio en la tabla de repositorios: la que lo nombra; con uno solo, la última."""
    c = [S.clave(t.strip("`[] ")) for t in titulos]
    if S.clave(repo) in c:
        return c.index(S.clave(repo))
    return len(titulos) - 1 if n_repos == 1 and len(titulos) > 3 else None


def leer_config(raiz, rel):
    texto = S.leer(raiz / rel)
    if texto is None:
        raise S.Fallo(f"no se puede leer la configuración ({rel})")
    return texto


def proponer(raiz, proyecto, datos):
    sec = S.seccion(raiz, proyecto)
    plan_ruta = S.ruta(sec, "plan")
    ids = list(S.leer_plan(S.leer(raiz / plan_ruta) or "")["piezas"]) if plan_ruta else []
    repos = sec["_repos"] or [d.get("repo") for d in datos]
    por_repo = {d.get("repo"): d for d in datos}
    varios = len(repos) > 1
    filas = {}   # nombre en el JSON: (fila, repo o None, estado, evidencia)
    for repo in repos:
        d = por_repo.get(repo)
        for f, fn in (("R1", r1), ("R2", r2), ("R3", r3), ("R6", lambda x: r6(x, ids))):
            if d is None:
                e = (SIN, "no se recogió con recoger_github.py --auditoria")
            elif not d.get("acceso"):
                e = (SIN, d.get("motivo") or "sin acceso al repositorio")
            else:
                e = fn(d)
            filas[f"{f} · {repo}" if varios else f] = (f, repo, e[0], e[1])
    org = next((d for d in datos if d.get("acceso") and (d.get("organizacion") or "cuenta personal" in (d.get("organizacion_motivo") or ""))), None) \
        or next((d for d in datos if d.get("acceso")), None)
    for f, fn in (("PL1", pl1), ("PL2", pl2)):
        if org is None:
            e = (SIN, "no se pudo leer ningún repositorio")
        elif "organizacion" not in org:
            e = (SIN, "los datos no son de recoger_github.py --auditoria")
        else:
            e = fn(org)
        filas[f] = (f, None, e[0], e[1])
    return sec, filas, repos


def archivos_config(sec):
    out = []
    for k, que in (("configuracion de plataforma", "plataforma"), ("configuracion de repositorios", "repositorios")):
        r = S.ruta(sec, k)
        if r is None:
            raise S.Fallo(f"«{k.capitalize()}» de la sección dice «{sec.get(k) or 'nada'}»: no hay dónde escribir la {que}")
        out.append((que, r))
    return out


def sin_api(raiz, sec, propuestas):
    vistas, out = set(), []
    for _, rel in archivos_config(sec):
        for l in (leer_config(raiz, rel)).split("\n"):
            m = FILA.match(l)
            if m and m.group(1) not in propuestas and m.group(1) not in vistas:
                vistas.add(m.group(1))
                out.append(m.group(1))
    return out


def escribir(raiz, sec, filas, repos, hoy_):
    """Pone «<estado> · hoy» en las filas propuestas (no las «sin comprobar») y «actualizado:» a hoy, una escritura por
    archivo. Devuelve las filas escritas."""
    escritas, por_archivo = [], {}
    for que, rel in archivos_config(sec):
        por_archivo.setdefault(rel, []).append(que)
    for rel, ques in por_archivo.items():
        texto = leer_config(raiz, rel)
        lineas = texto.split("\n")
        for i_tit, ns in tablas(texto):
            titulos = celdas(lineas[i_tit])
            for n in ns:
                c = celdas(lineas[n])
                nombre = c[0]
                if nombre.startswith("PL") and "plataforma" in ques:
                    objetivo = [(k, v) for k, v in filas.items() if v[0] == nombre and v[1] is None]
                    cols = [(len(c) - 1, objetivo[0][1])] if objetivo else []
                elif nombre.startswith("R") and "repositorios" in ques:
                    cols = []
                    for k, v in filas.items():
                        if v[0] == nombre and v[1] is not None:
                            col = columna(titulos, v[1], len(repos))
                            if col is not None and col < len(c):
                                cols.append((col, v))
                else:
                    cols = []
                cambio = False
                for col, (fila, repo, estado, _) in cols:
                    if estado == SIN:
                        continue
                    c[col] = f"{estado} · {hoy_}"
                    cambio = True
                    escritas.append(fila if repo is None or len(repos) == 1 else f"{fila} · {repo}")
                if cambio:
                    lineas[n] = "| " + " | ".join(c) + " |"
        out = "\n".join(lineas)
        if out.startswith("---"):
            out = re.sub(r"^(actualizado:\s*).*$", lambda m: m.group(1) + hoy_, out, count=1, flags=re.M)
        if out != texto:
            p = raiz / rel
            tmp = p.with_name(p.name + ".tmp")
            tmp.write_text(out, encoding="utf-8")
            tmp.replace(p)
    return escritas


def texto_propuesta(filas, faltan, escritas, escribir_):
    L = ["Auditoría de la configuración: lo que GitHub deja ver, con su evidencia.", ""]
    for k, (_, _, estado, ev) in filas.items():
        L.append(f"- {k}: {estado}. {ev[:1].upper() + ev[1:]}.")
    L += ["", "La API no ve, y lo comprueba quien administra: " + (", ".join(faltan) if faltan else "nada más") + "."]
    if escribir_:
        L.append(f"Escrito con la fecha de hoy: {', '.join(escritas) or 'nada (todo quedó sin comprobar)'}; lo «sin comprobar» se queda como estaba.")
    else:
        L.append("No se escribió nada: con el sí de quien acepta, se escribe con --escribir.")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Propone el estado de la configuración con lo que GitHub deja ver.")
    ap.add_argument("raiz")
    ap.add_argument("proyecto")
    ap.add_argument("--datos", action="append", default=[], required=True)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--escribir", action="store_true")
    a = ap.parse_args(argv)
    raiz = pathlib.Path(a.raiz)
    try:
        datos = S.cargar_datos(a.datos)
        sec, filas, repos = proponer(raiz, a.proyecto.strip("/"), datos)
        faltan = sin_api(raiz, sec, PLATAFORMA + REPOSITORIO)
        escritas = escribir(raiz, sec, filas, repos, S.hoy(raiz)) if a.escribir else []
    except S.Fallo as e:
        sys.stderr.write(f"auditoria.py: {e}\n")
        return 2
    if a.json:
        sys.stdout.write(json.dumps({"filas": {k: {"estado": v[2], "evidencia": v[3]} for k, v in filas.items()},
                                     "sin_api": faltan, "escrita": bool(a.escribir)}, ensure_ascii=False) + "\n")
    else:
        sys.stdout.write(texto_propuesta(filas, faltan, escritas, a.escribir))
    return 3 if any(v[2] == SIN for v in filas.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
