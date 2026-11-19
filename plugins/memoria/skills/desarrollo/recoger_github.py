#!/usr/bin/env python3
"""Lee de GitHub lo que necesitan el seguimiento y la auditoría del kit de desarrollo (skill desarrollo, 1.27), con `gh api`
(solo la API REST), y lo deja en un JSON. No escribe en GitHub ni en la carpeta. Es lo único del plugin que lee GitHub, y
solo corre cuando alguien pide un seguimiento o la auditoría (tecnologia/metodologia-desarrollo#2026-11-18-8).

Uso:
  recoger_github.py <organización/repositorio>... --salida <archivo.json> [--desde AAAA-MM-DD] [--auditoria]
                    [--max-commits N] [--max-detalle N]

  --salida       dónde deja el JSON; se escribe después de cada repositorio, así que un corte deja lo ya leído (sin él,
                 por la salida estándar, al final)
  --desde        desde cuándo se vigilan los commits de la rama principal con sus archivos; por defecto, 31 días antes de hoy
  --auditoria    lee además la configuración del repositorio, su CLAUDE.md y su organización, y no lee los archivos de
                 cada commit, que la auditoría no usa
  --max-commits  cuántos commits de la rama principal se leen como mucho (500): con ellos se sabe qué entró en cada paso
                 a Prod; si no llegan hasta --desde, el repositorio lo dice en «truncado»
  --max-detalle  de cuántos commits desde --desde se leen los archivos como mucho (150)

Lo que no se pudo leer o se cortó se dice, nunca se calla: cada repositorio lleva «errores» ({lista: motivo}) y «truncado»
([listas]), y el seguimiento no se guarda si falta algo (revisión de la 1.27.0, hallazgo 2). Solo se leen los pull
requests a la rama principal (decisión tecnologia/metodologia-desarrollo#2026-11-18-12). De cada archivo se guarda el
`patch` solo si es código que el seguimiento compara, y cortado a 4.000 caracteres.

Con un conector de GitHub en lugar de `gh`, la sesión arma el mismo JSON a mano, con esta forma; `base` y `merged_at` de
cada pull request son obligatorios (sin `base`, el pull request no cuenta), y lo que no se tenga va en «errores»:

  {"leido": "conector", "cuenta": "login", "hoy": "AAAA-MM-DD", "desde": "AAAA-MM-DD",
   "repos": [{"repo": "org/r", "rama": "main", "main_sha": "…",
              "pulls": [{"number": 1, "title": "P01 · …", "state": "open|closed|merged", "author": "login", "bot": false,
                         "base": "main", "merge_commit": "sha", "merged_at": "ISO"}],
              "commits": [{"sha": "…", "parents": 1, "date": "ISO", "message": "primera línea", "author": "login"}],
              "commits_hasta": "AAAA-MM-DD",
              "detalle": [{"sha": "…", "files": [{"filename": "…", "status": "added|modified|removed|renamed",
                                                  "previous_filename": "…", "patch": "…"}]}],
              "releases": [{"tag": "v1", "sha": "commit", "draft": false, "prerelease": false, "published_at": "ISO",
                            "body": "…", "author": "login"}],
              "tags": [{"name": "v1", "sha": "…"}],
              "auditoria": {"repo": {…}, "proteccion": {…}, "rulesets": [{…}], "claude_md": "texto", "org": {…},
                            "admins": ["login"], "errores": {"org": "…"}},
              "errores": {"pulls": "…"}, "truncado": ["commits"]}]}
"""
import base64, datetime, json, re, subprocess, sys

PAGINAS_PR = 20
PATCH_MAX = 4000
# lo que el seguimiento no compara: no se guarda su patch (dependencias bloqueadas, documentación, pruebas, generados)
SIN_PATCH = re.compile(r"(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|poetry\.lock|uv\.lock|Cargo\.lock|go\.sum|"
                       r"Gemfile\.lock|composer\.lock)$|^(docs?|tests?|pruebas|spec|__snapshots__|dist|build|vendor)/|"
                       r"\.(md|txt|png|jpe?g|gif|svg|pdf|lock|min\.js|map)$", re.I)


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
    """(lista, error, truncado): truncado si llenó las n páginas y quedaba más."""
    out = []
    sep = "&" if "?" in path else "?"
    for i in range(1, n + 1):
        d, e = gh(f"{path}{sep}per_page=100&page={i}")
        if e:
            return out, e, False
        out += d or []
        if len(d or []) < 100:
            return out, None, False
    return out, None, True


def es_bot(user):
    user = user or {}
    return user.get("type") == "Bot" or (user.get("login") or "").endswith("[bot]")


def repo(nombre, desde, auditoria, max_commits, max_detalle, orgs):
    r = {"repo": nombre, "errores": {}, "truncado": []}
    info, e = gh(f"repos/{nombre}")
    if e:
        r["error"] = e
        return r
    rama = info.get("default_branch") or "main"
    r["rama"] = rama
    # solo los pull requests a la rama principal (decisión -12): los de otras ramas son pasos dentro de un bloque
    pulls, e, t = paginas(f"repos/{nombre}/pulls?state=all&base={rama}&sort=created&direction=desc", PAGINAS_PR)
    if e:
        r["errores"]["pulls"] = e
    if t:
        r["truncado"].append("pulls")
    r["pulls"] = [{"number": p["number"], "title": p.get("title") or "",
                   "state": "merged" if p.get("merged_at") else ("open" if p.get("state") == "open" else "closed"),
                   "author": (p.get("user") or {}).get("login") or "", "bot": es_bot(p.get("user")),
                   "merge_commit": (p.get("merge_commit_sha") or "") if p.get("merged_at") else "",
                   "merged_at": p.get("merged_at") or "", "base": (p.get("base") or {}).get("ref") or rama} for p in pulls]
    commits, e, _ = paginas(f"repos/{nombre}/commits?sha={rama}", max(1, (max_commits + 99) // 100))
    if e:
        r["errores"]["commits"] = e
    commits = commits[:max_commits]
    r["main_sha"] = commits[0]["sha"] if commits else ""
    r["commits"] = [{"sha": c["sha"], "parents": len(c.get("parents") or []),
                     "date": ((c.get("commit") or {}).get("committer") or {}).get("date") or "",
                     "message": ((c.get("commit") or {}).get("message") or "").split("\n", 1)[0][:200],
                     "author": (c.get("author") or {}).get("login") or ""} for c in commits]
    r["commits_hasta"] = r["commits"][-1]["date"][:10] if r["commits"] else ""
    if len(r["commits"]) >= max_commits and r["commits_hasta"] > desde:
        r["truncado"].append("commits")
    r["detalle"] = []
    if not auditoria:
        recientes = [c for c in r["commits"] if c["date"][:10] >= desde]
        if len(recientes) > max_detalle:
            r["truncado"].append("detalle")
        fallos = []
        for c in recientes[:max_detalle]:
            d, e = gh(f"repos/{nombre}/commits/{c['sha']}")
            if e:
                fallos.append(f"{c['sha'][:7]}: {e}")
                continue
            files = []
            for f in d.get("files") or []:
                x = {k: f.get(k) for k in ("filename", "status", "previous_filename") if f.get(k) is not None}
                if f.get("patch") and not SIN_PATCH.search(f.get("filename") or ""):
                    x["patch"] = f["patch"][:PATCH_MAX]
                    if len(f["patch"]) > PATCH_MAX:
                        x["patch_cortado"] = True
                elif f.get("status") in ("added", "modified") and "patch" not in f and not SIN_PATCH.search(f.get("filename") or ""):
                    x["sin_patch"] = True          # GitHub no da el patch de un archivo grande
                files.append(x)
            if len(d.get("files") or []) >= 300:
                r["truncado"].append(f"archivos de {c['sha'][:7]}")
            r["detalle"].append({"sha": c["sha"], "files": files})
        if fallos:
            r["errores"]["detalle"] = "; ".join(fallos[:5]) + (f" y {len(fallos) - 5} más" if len(fallos) > 5 else "")
    # las etiquetas traen su commit: con ellas se sabe el de cada release sin una llamada por release (hallazgo 8)
    tags, e, t = paginas(f"repos/{nombre}/tags", 5)
    if e:
        r["errores"]["tags"] = e
    if t:
        r["truncado"].append("tags")
    r["tags"] = [{"name": x.get("name") or "", "sha": (x.get("commit") or {}).get("sha") or ""} for x in tags]
    sha_de = {x["name"]: x["sha"] for x in r["tags"]}
    rels, e, t = paginas(f"repos/{nombre}/releases", 2)
    if e:
        r["errores"]["releases"] = e
    if t:
        r["truncado"].append("releases")
    for x in rels:
        tn = x.get("tag_name") or ""
        if tn and tn not in sha_de and not x.get("draft"):
            dt, e = gh(f"repos/{nombre}/commits/{tn}")
            sha_de[tn] = (dt or {}).get("sha", "")
            if e:
                r["errores"]["releases"] = f"{tn}: {e}"
    r["releases"] = [{"tag": x.get("tag_name") or "", "sha": sha_de.get(x.get("tag_name") or "", ""), "draft": bool(x.get("draft")),
                      "prerelease": bool(x.get("prerelease")), "published_at": x.get("published_at") or "",
                      "body": x.get("body") or "", "author": (x.get("author") or {}).get("login") or ""} for x in rels]
    if auditoria:
        a = {"repo": {k: info.get(k) for k in ("private", "allow_squash_merge", "allow_merge_commit", "allow_rebase_merge",
                                                "security_and_analysis", "default_branch") if k in info}, "errores": {}}
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
            if e:
                a["errores"]["rulesets"] = f"{rs.get('name')}: {e}"
        cm, e = gh(f"repos/{nombre}/contents/CLAUDE.md?ref={rama}")
        if cm and cm.get("content"):
            try:
                a["claude_md"] = base64.b64decode(cm["content"]).decode("utf-8", "replace")[:20000]
            except ValueError:
                a["errores"]["claude_md"] = "no se pudo leer el contenido"
        elif e:
            a["errores"]["claude_md"] = e
        org = nombre.split("/")[0]
        if org not in orgs:           # una vez por organización
            o, eo = gh(f"orgs/{org}")
            adm, ea = gh(f"orgs/{org}/members?role=admin&per_page=100")
            orgs[org] = (o, eo, adm, ea)
        o, eo, adm, ea = orgs[org]
        a["org"] = {k: o.get(k) for k in ("two_factor_requirement_enabled",) if k in o} if o else None
        if o and "plan" in o:
            a["org"]["plan"] = (o.get("plan") or {}).get("name")
        if eo:
            a["errores"]["org"] = eo
        a["admins"] = [m.get("login") for m in adm] if isinstance(adm, list) else None
        if ea:
            a["errores"]["admins"] = ea
        r["auditoria"] = a
    if not r["errores"]:
        del r["errores"]
    if not r["truncado"]:
        del r["truncado"]
    return r


def main(argv):
    repos, desde, auditoria, max_commits, max_detalle, salida = [], None, False, 500, 150, None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--desde":
            desde = argv[i + 1]; i += 2; continue
        if a == "--salida":
            salida = argv[i + 1]; i += 2; continue
        if a == "--max-commits":
            max_commits = int(argv[i + 1]); i += 2; continue
        if a == "--max-detalle":
            max_detalle = int(argv[i + 1]); i += 2; continue
        if a == "--auditoria":
            auditoria = True; i += 1; continue
        repos.append(a.strip().strip("`")); i += 1
    if not repos:
        print(__doc__, file=sys.stderr)
        return 2
    hoy = datetime.date.today()
    desde = desde or (hoy - datetime.timedelta(days=31)).isoformat()
    yo, _ = gh("user")
    out = {"leido": "gh", "cuenta": (yo or {}).get("login", ""), "hoy": hoy.isoformat(), "desde": desde, "repos": []}
    orgs = {}

    def guardar():
        if salida:
            with open(salida, "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

    for nombre in repos:
        out["repos"].append(repo(nombre, desde, auditoria, max_commits, max_detalle, orgs))
        guardar()                 # un corte deja lo ya leído
    if salida:
        avisos = [f"{r['repo']}: " + "; ".join([r["error"]] if r.get("error") else
                                                [f"{k}: {v}" for k, v in (r.get("errores") or {}).items()]
                                                + ([f"cortado: {', '.join(r['truncado'])}"] if r.get("truncado") else []))
                  for r in out["repos"] if r.get("error") or r.get("errores") or r.get("truncado")]
        print(f"{salida}: {len(out['repos'])} repositorios, leídos como {out['cuenta'] or '?'}"
              + ("; incompleto: " + " · ".join(avisos) if avisos else ""))
    else:
        json.dump(out, sys.stdout, ensure_ascii=False, separators=(",", ":"))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
