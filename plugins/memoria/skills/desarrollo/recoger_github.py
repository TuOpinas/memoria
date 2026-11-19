#!/usr/bin/env python3
"""Lee de GitHub lo que necesitan el seguimiento y la auditoría del kit de desarrollo (skill desarrollo, 1.27), con `gh api`
(solo la API REST), y lo deja en un JSON. No escribe en GitHub ni en la carpeta. Es lo único del plugin que lee GitHub, y
solo corre cuando alguien pide un seguimiento o la auditoría (tecnologia/metodologia-desarrollo#2026-11-18-8).

Uso:
  recoger_github.py <organización/repositorio>... --salida <archivo.json> [--desde AAAA-MM-DD] [--auditoria] [--max-commits N]

  --salida       dónde deja el JSON (sin él, por la salida estándar); así no hace falta una redirección en el comando

  --desde        desde cuándo se miran los commits de la rama principal con sus archivos (lo que vigila las reglas y lo
                 que se compara con el diseño); por defecto, 31 días antes de hoy. Los pull requests, los releases y las
                 etiquetas se leen todos (hasta 1.000 pull requests por repositorio)
  --auditoria    lee además la configuración del repositorio y de su organización (R1, R2, R3, PL1, PL2); lo que la
                 cuenta no puede leer queda como error, sin suponer nada
  --max-commits  cuántos commits de la rama principal se leen como mucho (300); con sus archivos, solo los de --desde

Sin `gh` o sin acceso, cada repositorio sale con su «error» y el seguimiento lo dice. Con un conector de GitHub en lugar
de `gh`, la sesión arma el mismo JSON a mano, con esta forma (lo que no tenga, lo omite):

  {"leido": "gh", "hoy": "AAAA-MM-DD", "desde": "AAAA-MM-DD",
   "repos": [{"repo": "org/r", "rama": "main", "main_sha": "…",
              "pulls": [{"number": 1, "title": "P01 · …", "state": "open|closed|merged", "author": "login", "bot": false,
                         "merge_commit": "sha", "merged_at": "ISO"}],
              "commits": [{"sha": "…", "parents": 1, "date": "ISO", "message": "primera línea", "author": "login"}],
              "detalle": [{"sha": "…", "files": [{"filename": "…", "status": "added|modified|removed|renamed",
                                                  "previous_filename": "…", "patch": "…"}]}],
              "releases": [{"tag": "v1", "sha": "commit", "draft": false, "published_at": "ISO", "body": "…", "author": "login"}],
              "tags": [{"name": "v1", "sha": "…"}],
              "auditoria": {"repo": {…}, "proteccion": {…}, "rulesets": [{…}], "org": {…}, "admins": ["login"],
                            "errores": {"org": "…"}},
              "error": "…"}]}
"""
import datetime, json, subprocess, sys

PAGINAS_PR = 10


def gh(path):
    """(datos, error) de `gh api <path>`."""
    try:
        p = subprocess.run(["gh", "api", "-H", "Accept: application/vnd.github+json", path], capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        return None, "no hay gh en esta sesión"
    except subprocess.TimeoutExpired:
        return None, "GitHub no respondió en un minuto"
    if p.returncode != 0:
        msg = (p.stderr or p.stdout or "").strip().splitlines()
        return None, (msg[-1] if msg else f"gh salió con {p.returncode}")[:300]
    try:
        return json.loads(p.stdout or "null"), None
    except ValueError:
        return None, "GitHub devolvió algo que no es JSON"


def paginas(path, n):
    out = []
    sep = "&" if "?" in path else "?"
    for i in range(1, n + 1):
        d, e = gh(f"{path}{sep}per_page=100&page={i}")
        if e:
            return out, e
        out += d or []
        if len(d or []) < 100:
            break
    return out, None


def es_bot(user):
    user = user or {}
    return user.get("type") == "Bot" or (user.get("login") or "").endswith("[bot]")


def repo(nombre, desde, auditoria, max_commits):
    r = {"repo": nombre}
    info, e = gh(f"repos/{nombre}")
    if e:
        r["error"] = e
        return r
    rama = info.get("default_branch") or "main"
    r["rama"] = rama
    pulls, e = paginas(f"repos/{nombre}/pulls?state=all&sort=created&direction=desc", PAGINAS_PR)
    if e:
        r["error"] = "pull requests: " + e
    r["pulls"] = [{"number": p["number"], "title": p.get("title") or "",
                   "state": "merged" if p.get("merged_at") else ("open" if p.get("state") == "open" else "closed"),
                   "author": (p.get("user") or {}).get("login") or "", "bot": es_bot(p.get("user")),
                   "merge_commit": (p.get("merge_commit_sha") or "") if p.get("merged_at") else "",
                   "merged_at": p.get("merged_at") or "", "base": (p.get("base") or {}).get("ref") or ""} for p in pulls]
    commits, e = paginas(f"repos/{nombre}/commits?sha={rama}", max(1, (max_commits + 99) // 100))
    if e and "error" not in r:
        r["error"] = "commits: " + e
    commits = commits[:max_commits]
    r["main_sha"] = commits[0]["sha"] if commits else ""
    r["commits"] = [{"sha": c["sha"], "parents": len(c.get("parents") or []),
                     "date": ((c.get("commit") or {}).get("committer") or {}).get("date") or "",
                     "message": ((c.get("commit") or {}).get("message") or "").split("\n", 1)[0][:200],
                     "author": (c.get("author") or {}).get("login") or ""} for c in commits]
    r["detalle"] = []
    for c in r["commits"]:
        if c["date"][:10] < desde:
            break
        d, e = gh(f"repos/{nombre}/commits/{c['sha']}")
        if e:
            r.setdefault("errores_detalle", []).append(f"{c['sha'][:7]}: {e}")
            continue
        r["detalle"].append({"sha": c["sha"], "files": [{k: f.get(k) for k in ("filename", "status", "previous_filename", "patch") if f.get(k) is not None}
                                                        for f in (d.get("files") or [])]})
    rels, e = paginas(f"repos/{nombre}/releases", 2)
    shas = {}
    for x in rels:
        t = x.get("tag_name") or ""
        if t and t not in shas:
            dt, _ = gh(f"repos/{nombre}/commits/{t}")
            shas[t] = (dt or {}).get("sha", "")
    r["releases"] = [{"tag": x.get("tag_name") or "", "sha": shas.get(x.get("tag_name") or "", ""), "draft": bool(x.get("draft")),
                      "prerelease": bool(x.get("prerelease")), "published_at": x.get("published_at") or "",
                      "body": x.get("body") or "", "author": (x.get("author") or {}).get("login") or ""} for x in rels]
    tags, _ = paginas(f"repos/{nombre}/tags", 1)
    r["tags"] = [{"name": t.get("name") or "", "sha": (t.get("commit") or {}).get("sha") or ""} for t in tags]
    if auditoria:
        a = {"repo": {k: info.get(k) for k in ("private", "allow_squash_merge", "allow_merge_commit", "allow_rebase_merge",
                                                "security_and_analysis", "default_branch")}, "errores": {}}
        prot, e = gh(f"repos/{nombre}/branches/{rama}/protection")
        a["proteccion"] = prot
        if e:
            a["errores"]["proteccion"] = e
        lista, e = gh(f"repos/{nombre}/rulesets?includes_parents=true")
        a["rulesets"] = []
        if e:
            a["errores"]["rulesets"] = e
        for rs in lista or []:
            d, e = gh(f"repos/{nombre}/rulesets/{rs['id']}")
            if d:
                a["rulesets"].append(d)
        org = nombre.split("/")[0]
        o, e = gh(f"orgs/{org}")
        a["org"] = {"two_factor_requirement_enabled": (o or {}).get("two_factor_requirement_enabled"),
                    "plan": ((o or {}).get("plan") or {}).get("name")} if o else None
        if e:
            a["errores"]["org"] = e
        adm, e = gh(f"orgs/{org}/members?role=admin&per_page=100")
        a["admins"] = [m.get("login") for m in adm or []] if adm is not None else None
        if e:
            a["errores"]["admins"] = e
        r["auditoria"] = a
    return r


def main(argv):
    repos, desde, auditoria, max_commits, salida = [], None, False, 300, None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--desde":
            desde = argv[i + 1]; i += 2; continue
        if a == "--salida":
            salida = argv[i + 1]; i += 2; continue
        if a == "--max-commits":
            max_commits = int(argv[i + 1]); i += 2; continue
        if a == "--auditoria":
            auditoria = True; i += 1; continue
        repos.append(a.strip().strip("`")); i += 1
    if not repos:
        print(__doc__, file=sys.stderr)
        return 2
    hoy = datetime.date.today()
    desde = desde or (hoy - datetime.timedelta(days=31)).isoformat()
    out = {"leido": "gh", "hoy": hoy.isoformat(), "desde": desde, "repos": [repo(r, desde, auditoria, max_commits) for r in repos]}
    if salida:
        with open(salida, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        errores = [f"{r['repo']}: {r['error']}" for r in out["repos"] if r.get("error")]
        print(f"{salida}: {len(out['repos'])} repositorios" + (f"; no se pudo leer {'; '.join(errores)}" if errores else ""))
    else:
        json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
