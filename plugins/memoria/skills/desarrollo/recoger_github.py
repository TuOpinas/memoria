#!/usr/bin/env python3
"""Lee de GitHub lo que el seguimiento y la auditoría necesitan de un repositorio, y lo escribe en stdout como JSON.

No escribe nada en GitHub ni en la carpeta. Lee con la API REST de `gh` (`gh api <ruta>`, solo GET, cada página con
`page=`): los comandos de `gh` que van por GraphQL (`gh pr list`, `gh repo view`) no funcionan en una sesión de Claude en
la nube. Python 3.9, sin dependencias.

Uso:  recoger_github.py <owner/repo> --desde AAAA-MM-DD [--auditoria] [--paginas N]

Lee la rama principal y su último commit; los pull requests a esa rama, del más reciente hacia atrás hasta --desde (los
unidos desde esa fecha y los abiertos), con sus archivos, su descripción y quién los unió; los releases publicados desde
esa fecha, cada uno con los commits de esos pull requests que contiene (por `compare/`, nunca por fechas); la regla de la
rama principal, siempre, y el control de pruebas de aceptación del repositorio si está. Con --auditoria, además, quién se
puede saltar la regla, cómo se une en el repositorio y, si es de una organización, su verificación en dos pasos, su plan
y sus propietarios.

Forma: {"repo", "rama", "ultimo_commit", "desde", "acceso", "motivo", "prs": [{"number", "title", "state", "merged_at",
"merge_commit_sha", "user", "body", "files", "merged_by"}], "releases": [{"tag_name", "body", "published_at", "contiene"}],
"completo": {"prs", "releases"}, "reglas": [...] | null, "reglas_motivo", "control": {...} | null}; con --auditoria,
también "ajustes", "bypass", "bypass_motivo", "organizacion" y "organizacion_motivo". Una lista que llega al límite de
páginas sin pasar de la fecha da su «completo» falso: puede faltar algo.

Sale con 0 si escribió el JSON (aunque diga que no hubo acceso) y con 2 si los argumentos no valen.
"""
import argparse, base64, json, re, shutil, subprocess, sys

POR_PAGINA = 100


class ErrorGH(Exception):
    def __init__(self, http, mensaje):
        super().__init__(mensaje)
        self.http, self.mensaje = http, mensaje

    def motivo(self):
        return f"HTTP {self.http}: {self.mensaje}" if self.http else self.mensaje


def gh(ruta, **q):
    """GET de la API REST con `gh api`; devuelve el JSON. Un error de GitHub da ErrorGH con su código HTTP."""
    if q:
        ruta += ("&" if "?" in ruta else "?") + "&".join(f"{k}={v}" for k, v in q.items())
    try:
        r = subprocess.run(["gh", "api", "-X", "GET", "-H", "Accept: application/vnd.github+json", ruta],
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                           errors="replace", timeout=60)
    except FileNotFoundError:
        raise ErrorGH(None, "no está `gh` en esta máquina")
    except subprocess.TimeoutExpired:
        raise ErrorGH(None, f"`gh api {ruta}` no respondió en 60 segundos")
    if r.returncode != 0:
        m = re.search(r"\(HTTP (\d{3})\)", r.stderr or "")
        mensaje = ""
        try:
            mensaje = json.loads(r.stdout).get("message") or ""
        except (ValueError, AttributeError):
            pass
        lineas = (r.stderr or "").strip().splitlines()
        mensaje = mensaje or (lineas[-1] if lineas else f"`gh api` salió con {r.returncode}")
        raise ErrorGH(int(m.group(1)) if m else None, mensaje)
    try:
        return json.loads(r.stdout) if r.stdout.strip() else None
    except ValueError:
        raise ErrorGH(None, f"`gh api {ruta}` no devolvió JSON")


def paginas(ruta, limite, sigue=lambda pagina: True, **q):
    """Las páginas de una lista, mientras `sigue(pagina)` sea cierto. Devuelve (elementos, completa): completa es falso si
    se llegó al límite de páginas con la última llena y sin que `sigue` dijera que basta."""
    out = []
    for n in range(1, limite + 1):
        pag = gh(ruta, per_page=POR_PAGINA, page=n, **q)
        pag = pag if isinstance(pag, list) else []
        out.extend(pag)
        if len(pag) < POR_PAGINA or not sigue(pag):
            return out, True
    return out, False


def login(u):
    return (u or {}).get("login") if isinstance(u, dict) else u


def dia(iso):
    return (iso or "")[:10]


def leer_pulls(repo, rama, desde, limite):
    """Los pull requests a la rama: los unidos desde la fecha y los abiertos. (lista, completa)"""
    def sigue(pag):   # ordenados por actualización, del más reciente: basta cuando una página entera es anterior
        return any(dia(p.get("updated_at")) >= desde for p in pag)
    todos, completa = paginas(f"repos/{repo}/pulls", limite, sigue, state="all", base=rama, sort="updated",
                              direction="desc")
    out, vistos = [], set()
    for p in todos:
        n = p.get("number")
        if n in vistos:
            continue
        vistos.add(n)
        unido = p.get("merged_at")
        abierto = p.get("state") == "open"
        if not abierto and not (unido and dia(unido) >= desde):
            continue
        o = {"number": n, "title": p.get("title") or "", "state": p.get("state"), "merged_at": unido,
             "merge_commit_sha": p.get("merge_commit_sha") if unido else None, "user": login(p.get("user")),
             "body": p.get("body") or "", "files": [], "merged_by": None, "updated_at": p.get("updated_at")}
        if unido:
            archivos, ok = paginas(f"repos/{repo}/pulls/{n}/files", 30)
            o["files"] = [a.get("filename") for a in archivos if isinstance(a, dict) and a.get("filename")]
            completa = completa and ok
            try:
                o["merged_by"] = login((gh(f"repos/{repo}/pulls/{n}") or {}).get("merged_by"))
            except ErrorGH:
                pass
        out.append(o)
    return out, completa


def leer_releases(repo, desde, prs, limite):
    """Los releases publicados desde la fecha, con los commits de unión que contiene cada uno. (lista, completa)"""
    def sigue(pag):
        return any(dia(r.get("published_at") or r.get("created_at")) >= desde for r in pag)
    todos, completa = paginas(f"repos/{repo}/releases", limite, sigue)
    shas = [p["merge_commit_sha"] for p in prs if p.get("merge_commit_sha")]
    out = []
    for r in todos:
        if r.get("draft") or dia(r.get("published_at") or r.get("created_at")) < desde:
            continue
        etiqueta = r.get("tag_name")
        contiene = []
        for s in shas:
            try:
                estado = (gh(f"repos/{repo}/compare/{etiqueta}...{s}") or {}).get("status")
            except ErrorGH:
                completa = False
                continue
            if estado in ("behind", "identical"):
                contiene.append(s)
        out.append({"tag_name": etiqueta, "name": r.get("name"), "body": r.get("body") or "",
                    "published_at": r.get("published_at"), "contiene": contiene})
    return out, completa


ENV_CONTROL = re.compile(r"^\s{2}(ACEPTACION|ACTIVAS|CORREDOR|CONFIG|SUFIJO):\s*(\S*)", re.M)


def leer_control(repo, rama):
    """Las claves del control de pruebas de aceptación (`.github/workflows/pruebas-aceptacion.yml`), o None."""
    try:
        c = gh(f"repos/{repo}/contents/.github/workflows/pruebas-aceptacion.yml", ref=rama) or {}
        texto = base64.b64decode(c.get("content") or "").decode("utf-8", errors="replace")
    except (ErrorGH, ValueError):
        return None
    out = {}
    for k, v in ENV_CONTROL.findall(texto):
        out[k] = v.strip("\"'")
    return out or None


def leer_proteccion(repo, rama):
    """La protección clásica de la rama, con la forma de `rules/branches/<rama>` (un repositorio puede tener las dos:
    los checks obligatorios en la clásica y el pull request en un ruleset). [] si no hay; None si no se pudo leer."""
    try:
        p = gh(f"repos/{repo}/branches/{rama}/protection") or {}
    except ErrorGH as e:
        return [] if e.http == 404 else None
    fuente = {"ruleset_source_type": "Protección clásica", "ruleset_source": repo}
    out = []
    rsc = p.get("required_status_checks")
    if isinstance(rsc, dict):
        cs = [c.get("context") for c in rsc.get("checks") or [] if isinstance(c, dict)] or list(rsc.get("contexts") or [])
        out.append(dict(fuente, type="required_status_checks",
                        parameters={"required_status_checks": [{"context": c} for c in cs if c]}))
    if isinstance(p.get("required_pull_request_reviews"), dict):
        out.append(dict(fuente, type="pull_request", parameters={}))
    if not (p.get("allow_deletions") or {}).get("enabled"):
        out.append(dict(fuente, type="deletion"))
    if not (p.get("allow_force_pushes") or {}).get("enabled"):
        out.append(dict(fuente, type="non_fast_forward"))
    if not (p.get("enforce_admins") or {}).get("enabled"):   # sin «Do not allow bypassing», los administradores se la saltan
        out.append(dict(fuente, type="bypass_administradores"))
    return out


def recoger(repo, desde, auditoria, limite):
    d = {"repo": repo, "rama": None, "ultimo_commit": None, "desde": desde, "acceso": False, "motivo": "",
         "prs": [], "releases": [], "completo": {"prs": False, "releases": False}, "reglas": None,
         "reglas_motivo": "sin leer", "control": None}
    if auditoria:
        d.update({"ajustes": None, "bypass": None, "bypass_motivo": "sin leer", "organizacion": None,
                  "organizacion_motivo": "sin leer"})
    if shutil.which("gh") is None:
        d["motivo"] = "no está `gh` en esta máquina"
        return d
    try:
        info = gh(f"repos/{repo}") or {}
    except ErrorGH as e:
        d["motivo"] = f"no se pudo leer el repositorio ({e.motivo()})"
        return d
    d["acceso"] = True
    rama = d["rama"] = info.get("default_branch") or "main"
    try:
        d["ultimo_commit"] = (gh(f"repos/{repo}/commits/{rama}") or {}).get("sha")
    except ErrorGH:
        pass
    try:
        d["prs"], d["completo"]["prs"] = leer_pulls(repo, rama, desde, limite)
    except ErrorGH as e:
        d["motivo"] = f"no se pudo leer la lista de pull requests ({e.motivo()})"
    try:
        d["releases"], d["completo"]["releases"] = leer_releases(repo, desde, d["prs"], limite)
    except ErrorGH as e:
        d["motivo"] = (d["motivo"] + "; " if d["motivo"] else "") + f"no se pudieron leer los releases ({e.motivo()})"
    clasica = None
    try:
        reglas = gh(f"repos/{repo}/rules/branches/{rama}")
        d["reglas"], d["reglas_motivo"] = (reglas if isinstance(reglas, list) else []), ""
        clasica = leer_proteccion(repo, rama)
        if clasica is None:
            d["reglas_motivo"] = f"la protección clásica de {rama} no se pudo leer: solo cuentan los rulesets"
        else:
            d["reglas"] += clasica
    except ErrorGH as e:
        d["reglas_motivo"] = f"no se pudo leer la regla de {rama} ({e.motivo()})"
    d["control"] = leer_control(repo, rama)
    if not auditoria:
        return d
    d["ajustes"] = {k: info.get(k) for k in ("allow_squash_merge", "allow_merge_commit", "allow_rebase_merge")}
    if d["reglas"] is not None:
        bypass, motivo = [], ""
        for rid in sorted({r.get("ruleset_id") for r in d["reglas"] if isinstance(r, dict) and r.get("ruleset_id")}):
            try:
                rs = gh(f"repos/{repo}/rulesets/{rid}") or {}
                bypass.extend(rs.get("bypass_actors") or [])
            except ErrorGH as e:
                motivo = f"no se pudo leer el ruleset {rid} ({e.motivo()})"
        if any(r.get("type") == "bypass_administradores" for r in d["reglas"] if isinstance(r, dict)):
            bypass.append({"actor_type": "RepositoryRole", "actor_id": "admin", "bypass_mode": "protección clásica sin «enforce admins»"})
        d["bypass"], d["bypass_motivo"] = (None, motivo) if motivo else (bypass, "")
    else:
        d["bypass_motivo"] = d["reglas_motivo"]
    duenio = info.get("owner") or {}
    if duenio.get("type") != "Organization":
        d["organizacion_motivo"] = f"el repositorio es de una cuenta personal ({duenio.get('login')}), no de una organización"
        return d
    try:
        org = gh(f"orgs/{duenio.get('login')}") or {}
        admins, ok = paginas(f"orgs/{duenio.get('login')}/members", 10, role="admin")
        d["organizacion"] = {"login": org.get("login"), "dos_pasos": org.get("two_factor_requirement_enabled"),
                             "plan": (org.get("plan") or {}).get("name") if isinstance(org.get("plan"), dict) else None,
                             "propietarios": [login(a) for a in admins], "propietarios_completo": ok}
        d["organizacion_motivo"] = ""
    except ErrorGH as e:
        d["organizacion_motivo"] = f"no se pudo leer la organización {duenio.get('login')} ({e.motivo()})"
    return d


def main(argv=None):
    ap = argparse.ArgumentParser(description="Lee de GitHub lo que piden el seguimiento y la auditoría.")
    ap.add_argument("repo")
    ap.add_argument("--desde", required=True)
    ap.add_argument("--auditoria", action="store_true")
    ap.add_argument("--paginas", type=int, default=10, help="límite de páginas de 100 por lista (10)")
    a = ap.parse_args(argv)
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", a.repo) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.desde):
        sys.stderr.write("uso: recoger_github.py <owner/repo> --desde AAAA-MM-DD [--auditoria]\n")
        return 2
    d = recoger(a.repo, a.desde, a.auditoria, max(1, a.paginas))
    sys.stdout.write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
