#!/usr/bin/env python3
"""P06 · `seguimiento.py` and `recoger_github.py` (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-27, en el plan).

- Block pull requests and reverts give each piece its state. Dado a merged block pull request «P01 + P02 · …» and a
  merged revert of P03, Cuando the follow-up runs, Entonces P01 and P02 are `unida` and P03 is `revertida`, in the
  entry's table that the board reads.
- An incomplete list is never saved as whole. Dado a pull request list cut at the limit, Cuando the follow-up runs,
  Entonces each part that needs it says «sin comprobar», and the entry is shown but not saved.
- Delivered only if the release contains the commit. Dado a piece merged after a release with «Aprobó:» that is dated
  later but whose tag does not contain the piece's merge commit, Cuando the follow-up runs, Entonces the piece is
  `unida`, not `entregada`.
- Where merging publishes, the version pull request's yes delivers. Dado «Paso a Prod» says merging the version pull
  request is the step to Prod, and a merged «P01 + P02 · 1.2.0» whose description says «Aprobó: Ana Pérez, 2026-11-20»,
  Cuando the follow-up runs, Entonces P01 and P02 are `entregada`, and the entry says Ana Pérez gave the yes on 2026-11-20.
- What is outside the plan is listed. Dado merged pull requests with no piece, with a piece the plan does not have, and
  a «Kit · » that changes code, and a «Bump …» that only changes workflows, Cuando the follow-up runs, Entonces the
  first three are listed as outside the plan and the «Bump …» counts as kit.
- No access to a repository is said, and nothing is saved. Dado a repository the follow-up cannot read, Cuando the
  follow-up runs, Entonces the entry shows the plan's pieces without state, names that repository, and is not saved.

Por el contrato del encargo (campo 3): «el seguimiento corre» es recoger_github.py con un `gh` falso delante en el PATH
(GH_FALSO, abajo: responde la API REST desde un JSON que escribe cada escenario, nunca la red) y, sobre su salida,
seguimiento.py --json contra la raíz de muestra de P05_lectores.py. La prueba mira el JSON de seguimiento.py
(#2026-11-27-15), su código de salida y el seguimiento guardado; el texto de la entrada y sus siete puntos, la
verificación. recoger_github.py lee siempre la regla de la rama principal y la deja en "reglas" (o null); si no se
puede leer, check_obligatorio es null, y eso no impide guardar ni hace salir con 3. Lo compartido con P07 (la raíz, el
`gh` falso y cómo se corren los scripts) está aquí y P07 lo importa. Cómo se lee cada escenario está en RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P06_seguimiento_por_script.py (0 pasa, 1 falla, 2 no se montó).
"""
import atexit, copy, datetime, json, os, pathlib, re, shutil, subprocess, sys, tempfile

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import flujo  # noqa: E402  (Informe, principal y Montaje)
from P05_lectores import MUESTRA, PROYECTO_MD, PLAN, SEGUIMIENTO, REPO  # noqa: E402  (la raíz de muestra: una sola copia)

SCRIPTS = REPO / "plugins" / "memoria" / "skills" / "desarrollo"
RECOGER, SEGUIR, AUDITAR = SCRIPTS / "recoger_github.py", SCRIPTS / "seguimiento.py", SCRIPTS / "auditoria.py"
LECTOR = REPO / "packages" / "context-core"   # context_core.dev_view.read_follow_up: lo que lee el tablero
REPOSITORIO, PROYECTO = "muestra/portal", "ventas/portal"
DESDE = "2026-11-16"
CONFIG = "ventas/portal/entregables/configuracion.md"
ESTADOS = ("pendiente", "en curso", "unida", "revertida", "entregada")
PASO_UNIR = "Paso a Prod: unir el pull request de versión es el paso a Prod"

# La entrada anterior de la muestra pasa del 2026-11-20 al 16: así «2026-11-20» solo sale en el «Aprobó:» del escenario 4.
# Y la organización declara su zona en guia.md, «Zona horaria: UTC», para que la fecha de hoy de los scripts (la de la
# zona de la organización) sea la que la prueba compara, la UTC, en CI y en cualquier computadora
GUIA = "guia.md"
BASE = [(SEGUIMIENTO, "## 2026-11-20\n", f"## {DESDE}\n"),
        (GUIA, "Una organización de muestra para las pruebas.\n", "Una organización de muestra para las pruebas.\n\n"
                                                                   "Zona horaria: UTC\n")]
CONFIGURACION = """---
estado: vigente
actualizado: 2026-10-28
aportacion: "La configuración de plataforma y repositorios del portal."
basado_en: []
---

# Configuración de plataforma y repositorios

## Plataforma

| # | Qué se cumple | Cómo se comprueba | Estado |
|---|---|---|---|
| PL1 | GitHub es de la empresa, pide verificación en dos pasos y su plan permite reglas en repositorios privados | En GitHub, la organización → Settings → Authentication security y Billing | |
| PL2 | Dos personas pueden administrar GitHub | En GitHub, la organización → People → filtro Owners | |
| PL3 | El dominio y la nube están a nombre de la empresa | El titular en el registrador y en la facturación de la nube | cumple · 2026-10-28 |
| PL4 | Hay un entorno de Release separado de Prod | Los entornos de la nube | no aplica |
| PL5 | Los secretos viven en un gestor de secretos, nunca en el código | El gestor tiene las claves | cumple · 2026-10-28 |
| PL6 | La base de datos se respalda sola y la restauración se ha probado | Los respaldos de la nube | excepción |
| PL7 | Si Prod se cae, avisa a una persona | El servicio de monitoreo y a quién avisa | no cumple · 2026-10-28 |

PL4: la verificación corre sobre una vista previa. PL6: decidió Ana Pérez, 2026-10-28.

## Repositorios

| # | Qué se cumple | Cómo se comprueba | muestra/portal |
|---|---|---|---|
| R1 | Nada llega a la rama principal sin pull request, se une con squash y nadie se salta la regla | La regla de la rama principal | no cumple · 2026-10-28 |
| R2 | Las pruebas pasan antes de unir, también las de aceptación de las piezas activas | La regla de la rama principal | cumple · 2026-10-28 |
| R3 | Ningún secreto entra en el código | El control de secretos es obligatorio | cumple · 2026-10-28 |
| R4 | La base de datos cambia solo con migraciones nuevas | Quien revisa el pull request | no aplica |
| R5 | A Prod solo despliega quien administra | Quién tiene permiso de desplegar en Prod | cumple · 2026-10-28 |
| R6 | Cada pull request empieza por el identificador de su pieza | El apartado «fuera del plan» del último seguimiento | cumple · 2026-10-28 |
| R7 | El `CLAUDE.md` existe y tiene las reglas de la plantilla del kit | El archivo | cumple · 2026-10-28 |

## Verificación

| | |
|---|---|
| Dónde corre | Una vista previa |
"""
CON_CONFIG = [(PROYECTO_MD, "Configuración de plataforma: por crear\nConfiguración de repositorios: por crear",
               f"Configuración de plataforma: {CONFIG}\nConfiguración de repositorios: {CONFIG}")]


def hoy():
    """La fecha de hoy en la zona de la organización de muestra («Zona horaria: UTC» en su guia.md)."""
    return datetime.datetime.now(datetime.timezone.utc).date().isoformat()


# ---------- la raíz de muestra ----------
def raiz(cambios=(), archivos=None):
    """La raíz de muestra de P05 en una carpeta temporal, con la entrada anterior del día 16, los cambios del escenario
    ((ruta, texto que está una sola vez, texto nuevo)) y archivos de más ({ruta: texto})."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="aceptacion-f3-"))
    atexit.register(shutil.rmtree, tmp, True)
    r = tmp / "raiz"
    todos = dict(MUESTRA)
    todos.update(archivos or {})
    for ruta, texto in todos.items():
        (r / ruta).parent.mkdir(parents=True, exist_ok=True)
        (r / ruta).write_text(texto, encoding="utf-8")
    for ruta, viejo, nuevo in list(BASE) + list(cambios):
        p = r / ruta
        texto = p.read_text(encoding="utf-8")
        if texto.count(viejo) != 1:
            raise flujo.Montaje(f"{ruta} de la muestra no tiene una sola vez «{viejo[:60]}»")
        p.write_text(texto.replace(viejo, nuevo), encoding="utf-8")
    return r


# ---------- lo que responde el gh falso ----------
def pr(n, titulo, unido="2026-11-18T10:00:00Z", archivos=("src/catalogo.py",), autor="ana", cuerpo="", sha=None):
    """Un pull request a main, abierto el mismo día en que se unió; unido=None es cerrado sin unir."""
    return {"number": n, "title": titulo, "state": "closed", "merged_at": unido, "body": cuerpo, "user": autor,
            "merge_commit_sha": sha or (f"{n:040x}" if unido else None),
            "created_at": f"{unido[:10]}T08:00:00Z" if unido else "2026-11-17T09:00:00Z",
            "updated_at": unido or "2026-11-17T09:30:00Z", "closed_at": unido or "2026-11-17T09:30:00Z",
            "base": "main", "files": list(archivos)}


REGLAS_BIEN = [   # la regla de main de un repositorio en regla: pull request, solo squash, sin excepciones, checks obligatorios
    {"type": "deletion", "ruleset_id": 7, "ruleset_source_type": "Repository", "ruleset_source": REPOSITORIO},
    {"type": "non_fast_forward", "ruleset_id": 7, "ruleset_source_type": "Repository", "ruleset_source": REPOSITORIO},
    {"type": "pull_request", "ruleset_id": 7, "ruleset_source_type": "Repository", "ruleset_source": REPOSITORIO,
     "parameters": {"allowed_merge_methods": ["squash"], "required_approving_review_count": 0,
                    "dismiss_stale_reviews_on_push": False, "require_code_owner_review": False,
                    "require_last_push_approval": False, "required_review_thread_resolution": False}},
    {"type": "required_status_checks", "ruleset_id": 7, "ruleset_source_type": "Repository", "ruleset_source": REPOSITORIO,
     "parameters": {"strict_required_status_checks_policy": False, "do_not_enforce_on_create": False,
                    "required_status_checks": [{"context": "pruebas"}, {"context": "secretos"},
                                               {"context": "pruebas de aceptación"}]}},
]


def github(prs=(), **mas):
    """Lo que el gh falso sabe del repositorio de la muestra. mas: releases, contiene ({etiqueta: [sha]}), acceso,
    pulls_sin_fin, reglas (None: la API dice 403 a la regla, a los rulesets y a la protección), org (None: 404).
    La regla se sirve igual con y sin --auditoria: recoger_github.py la lee siempre."""
    d = {"repo": REPOSITORIO, "acceso": True, "rama": "main", "ultimo_commit": "c0ffee" * 6 + "abcd",
         "repo_ajustes": {"allow_squash_merge": True, "allow_merge_commit": False, "allow_rebase_merge": False},
         "pulls": [copy.deepcopy(p) for p in prs], "pulls_sin_fin": False, "releases": [], "contiene": {},
         "reglas": copy.deepcopy(REGLAS_BIEN), "bypass": [],
         "org": {"login": "muestra", "two_factor_requirement_enabled": True, "plan": {"name": "team"}},
         "admins": ["ana", "luis"]}
    d.update(copy.deepcopy(mas))
    return d


GH_FALSO = r'''
"""gh falso de las pruebas de aceptación de P06 y P07: solo «gh auth status» y «gh api <ruta REST>» de lectura, con
-X GET, -f/-F, -H, --hostname y --cache; ni --jq, ni --paginate, ni GraphQL. Responde desde datos.json, a su lado, y
apunta cada llamada en llamadas.txt. Una ruta que no conoce da 404, como GitHub. La regla de la rama principal se sirve
solo por rulesets (rules/branches/<rama>, rulesets y rulesets/<id>), se pida o no la auditoría; la protección clásica
(branches/<rama>/protection) da 404 «Branch not protected», como en un repositorio que solo usa rulesets; sin «reglas»,
403 a las tres. Cada lista trae los campos que da GitHub: la de pulls, sin «merged» ni «merged_by» (van en pulls/<n>);
la búsqueda, sin «merged_at» ni «merge_commit_sha» sueltos («merged_at» va dentro de «pull_request»), y filtra por los
calificadores merged:, updated:, created:, closed:, is:, state: y base:. commits?sha= da la lista de esa rama o etiqueta
(404 si no la conoce). compare/ admite los dos órdenes, y una etiqueta con su propio commit da «identical»."""
import json, pathlib, re, sys, urllib.parse
AQUI = pathlib.Path(__file__).resolve().parent
D = json.loads((AQUI / "datos.json").read_text(encoding="utf-8"))
args = sys.argv[1:]
with open(AQUI / "llamadas.txt", "a", encoding="utf-8") as f:
    f.write(json.dumps(args, ensure_ascii=False) + "\n")

def sale(codigo, cuerpo, http=None, mensaje=None):
    sys.stdout.write(json.dumps(cuerpo, ensure_ascii=False) + "\n")
    if http:
        sys.stderr.write(f"gh: {mensaje} (HTTP {http})\n")
    sys.exit(codigo)

def error(http, mensaje):
    sale(1, {"message": mensaje, "documentation_url": "https://docs.github.com/rest", "status": str(http)}, http, mensaje)

if args[:2] == ["auth", "status"]:
    sys.stderr.write("github.com\n  Logged in to github.com account muestra (GH_TOKEN)\n"); sys.exit(0)
if not args or args[0] != "api":
    sys.stderr.write("el gh falso solo responde «gh api» con rutas REST\n"); sys.exit(1)
metodo, campos, ruta, i = None, {}, None, 1
while i < len(args):
    a = args[i]
    if a in ("-X", "--method"):
        metodo, i = args[i + 1].upper(), i + 2
    elif a in ("-f", "-F", "--raw-field", "--field"):
        k, _, v = args[i + 1].partition("="); campos[k] = v; i += 2
    elif a in ("-H", "--header", "--hostname", "--cache"):
        i += 2
    elif a.startswith("-"):
        sys.stderr.write(f"el gh falso no admite {a}: lee el JSON tal cual y pide cada página con page=\n"); sys.exit(1)
    else:
        ruta, i = a, i + 1
if ruta is None or ruta == "graphql":
    sys.stderr.write("el gh falso solo responde rutas REST\n"); sys.exit(1)
metodo = metodo or ("POST" if campos else "GET")
if metodo != "GET":
    error(403, "el gh falso solo lee (" + metodo + ")")
ruta, _, qs = ruta.lstrip("/").partition("?")
q = {k: v[-1] for k, v in urllib.parse.parse_qs(qs).items()}
q.update(campos)
pp, pag = min(int(q.get("per_page", 30)), 100), int(q.get("page", 1))

def pagina(lista):
    return lista[(pag - 1) * pp: pag * pp]

def sin_fin(n0):
    return [{"number": n0 - ((pag - 1) * pp + k), "title": f"Cambio de prueba {n0 - ((pag - 1) * pp + k)}",
             "state": "closed", "merged_at": None, "merge_commit_sha": None, "body": "", "user": "luis",
             "created_at": "2026-11-27T09:00:00Z", "updated_at": "2026-11-27T10:00:00Z",
             "closed_at": "2026-11-27T10:00:00Z", "base": "main"} for k in range(pp)]

def completo(p):
    """El pull request como lo da GET pulls/<n>."""
    o = {k: v for k, v in p.items() if k != "files"}
    o["user"] = {"login": p["user"], "type": "Bot" if p["user"].endswith("[bot]") else "User"}
    o["base"] = {"ref": p["base"]}
    o["merged"] = bool(p["merged_at"])
    o["merged_by"] = {"login": "ana"} if p["merged_at"] else None
    o["html_url"] = f"https://github.com/{D['repo']}/pull/{p['number']}"
    return o

def de_lista(p):
    """El pull request como lo da la lista de pulls: sin «merged» ni «merged_by»."""
    o = completo(p)
    del o["merged"], o["merged_by"]
    return o

def de_busqueda(p):
    """El pull request como lo da search/issues: un issue, con «merged_at» dentro de «pull_request»."""
    o = {k: v for k, v in de_lista(p).items() if k not in ("merged_at", "merge_commit_sha", "base")}
    o["pull_request"] = {"merged_at": p["merged_at"], "html_url": o["html_url"],
                         "url": f"https://api.github.com/repos/{D['repo']}/pulls/{p['number']}"}
    return o

def cumple(p, calificador):
    """Si el pull request cumple un calificador de la búsqueda (uno que no conoce lo deja pasar)."""
    k, _, v = calificador.partition(":")
    k, v = k.lower(), v.strip('"')
    if k == "is":
        return {"merged": bool(p["merged_at"]), "unmerged": not p["merged_at"], "closed": p["state"] == "closed",
                "open": p["state"] == "open"}.get(v.lower(), True)
    if k == "state":
        return p["state"] == v.lower()
    if k == "base":
        return p["base"] == v
    campo = {"merged": "merged_at", "updated": "updated_at", "created": "created_at", "closed": "closed_at"}.get(k)
    if campo is None:
        return True
    f = p.get(campo)
    if not f:
        return False
    def a(x):   # la fecha del pull request, cortada a la precisión del calificador
        return f if "T" in x else f[:10]
    if ".." in v:
        ini, fin = v.split("..", 1)
        return (ini == "*" or a(ini) >= ini) and (fin == "*" or a(fin) <= fin)
    for op in (">=", "<=", ">", "<"):
        if v.startswith(op):
            x = v[len(op):]
            return {">=": a(x) >= x, "<=": a(x) <= x, ">": a(x) > x, "<": a(x) < x}[op]
    return a(v) == v

if ruta == "search/issues":
    if D["pulls_sin_fin"]:
        if pag * pp > 1000:
            error(422, "Cannot access beyond the first 1000 results")
        sale(0, {"total_count": 5000, "incomplete_results": False, "items": [de_busqueda(p) for p in sin_fin(200000)]})
    if not D["acceso"]:
        error(422, "Validation Failed")
    trozos = q.get("q", "").split()
    palabras = [w for w in trozos if ":" not in w and w != "OR"]
    calificadores = [w for w in trozos if ":" in w]
    hay = [p for p in D["pulls"] if (not palabras or any(w.lower() in p["title"].lower() for w in palabras))
           and all(cumple(p, c) for c in calificadores)]
    hay.sort(key=lambda p: p["updated_at" if q.get("sort") == "updated" else "created_at"],
             reverse=q.get("order", "desc") == "desc")
    sale(0, {"total_count": len(hay), "incomplete_results": False, "items": pagina([de_busqueda(p) for p in hay])})
m = re.match(r"orgs/([^/]+)(/members)?$", ruta)
if m:
    if D["org"] is None or m.group(1) != D["repo"].split("/")[0]:
        error(404, "Not Found")
    if m.group(2):
        quien = D["admins"] if q.get("role") == "admin" else D["admins"] + ["eva"]
        sale(0, pagina([{"login": u, "type": "User"} for u in quien]))
    sale(0, D["org"])
if re.match(r"users/[^/]+$", ruta):
    sale(0, {"login": ruta.split("/")[1], "type": "Organization" if D["org"] else "User"})
m = re.match(r"repos/([^/]+/[^/]+)(?:/(.*))?$", ruta)
if not m or m.group(1) != D["repo"]:
    error(404, "Not Found")
if not D["acceso"]:
    error(404, "Not Found")
resto, rama, sha = m.group(2) or "", D["rama"], D["ultimo_commit"]
etiquetas = {r["tag_name"]: r.get("sha", "e" * 40) for r in D["releases"]}
if resto == "":
    o = {"full_name": D["repo"], "name": D["repo"].split("/")[1], "default_branch": rama, "private": True,
         "owner": {"login": D["repo"].split("/")[0], "type": "Organization" if D["org"] else "User"}}
    o.update(D["repo_ajustes"]); sale(0, o)
c = {"sha": sha, "commit": {"message": "Último commit", "committer": {"date": "2026-11-27T12:00:00Z"}}}
if resto == "commits":   # commits?sha=<rama, etiqueta o sha>: la lista desde ahí
    desde = q.get("sha", rama)
    if desde in (rama, sha):
        sale(0, pagina([c]))
    if desde in etiquetas or desde in etiquetas.values():
        s = etiquetas.get(desde, desde)
        sale(0, pagina([{"sha": s, "commit": {"message": "Release", "committer": {"date": "2026-11-25T12:00:00Z"}}}]))
    error(404, f"No commit found for SHA: {desde}")
if resto in (f"branches/{rama}", f"commits/{rama}"):
    sale(0, c if resto.startswith("commits") else {"name": rama, "commit": c, "protected": True})
if resto.startswith("commits/") and resto[8:] in etiquetas:
    sale(0, {"sha": etiquetas[resto[8:]]})
if resto in (f"git/ref/heads/{rama}", f"git/refs/heads/{rama}"):
    sale(0, {"ref": f"refs/heads/{rama}", "object": {"sha": sha, "type": "commit"}})
m = re.match(r"git/refs?/tags/(.+)$", resto)
if m and m.group(1) in etiquetas:
    sale(0, {"ref": f"refs/tags/{m.group(1)}", "object": {"sha": etiquetas[m.group(1)], "type": "commit"}})
if resto == "tags":
    sale(0, pagina([{"name": t, "commit": {"sha": s}} for t, s in etiquetas.items()]))
if resto.startswith("rules/") or resto.startswith("rulesets") or resto.endswith("/protection"):
    if D["reglas"] is None:
        error(403, "Resource not accessible by integration")
    if resto == f"rules/branches/{rama}":
        sale(0, D["reglas"])
    if resto == "rulesets":
        sale(0, [{"id": 7, "name": "main", "target": "branch", "enforcement": "active", "source": D["repo"]}])
    if resto == "rulesets/7":
        sale(0, {"id": 7, "name": "main", "target": "branch", "enforcement": "active", "bypass_actors": D["bypass"],
                 "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
                 "rules": [{k: v for k, v in r.items() if not k.startswith("ruleset")} for r in D["reglas"]]})
    error(404, "Branch not protected" if resto.endswith("/protection") else "Not Found")
if resto == "pulls":
    if D["pulls_sin_fin"]:
        sale(0, [de_lista(p) for p in sin_fin(100000)])
    hay = [p for p in D["pulls"] if q.get("state", "open") in ("all", p["state"]) and q.get("base", p["base"]) == p["base"]]
    hay.sort(key=lambda p: p["updated_at" if q.get("sort") in ("updated", "long-running") else "created_at"],
             reverse=q.get("direction", "desc") == "desc")
    sale(0, pagina([de_lista(p) for p in hay]))
m = re.match(r"pulls/(\d+)(/files|/reviews|/commits)?$", resto)
if m:
    p = next((p for p in D["pulls"] if p["number"] == int(m.group(1))), None)
    if p is None:
        error(404, "Not Found")
    if m.group(2) == "/files":
        sale(0, pagina([{"filename": f, "status": "modified", "additions": 1, "deletions": 0, "changes": 1} for f in p["files"]]))
    if m.group(2):
        sale(0, [])
    sale(0, completo(p))
if resto in ("releases", "releases/latest") or resto.startswith("releases/tags/"):
    rel = [dict({k: v for k, v in r.items() if k != "sha"}, draft=r.get("draft", False), prerelease=False)
           for r in D["releases"]]
    if resto == "releases":
        sale(0, pagina(rel))
    t = resto[len("releases/tags/"):] if resto.startswith("releases/tags/") else None
    r = next((r for r in rel if not r["draft"] and (t is None or r["tag_name"] == t)), None)
    sale(0, r) if r else error(404, "Not Found")
m = re.match(r"compare/(.+?)\.\.\.(.+)$", resto)
por_sha = {s: t for t, s in etiquetas.items()}
if m:   # compare/<etiqueta>...<sha> y compare/<sha>...<etiqueta> (la etiqueta también por su sha)
    x, y = m.groups()
    ex, ey = (t if t in etiquetas else por_sha.get(t) for t in (x, y))
    sx, sy = (etiquetas.get(t, t) for t in (x, y))
    if (ex or ey) and sx == sy:   # una etiqueta y su propio commit
        sale(0, {"status": "identical", "ahead_by": 0, "behind_by": 0})
    for etiqueta, otro, contenido in ((ex, sy, "behind"), (ey, sx, "ahead")):
        if etiqueta and not (ex and ey):
            if otro in D["contiene"].get(etiqueta, []):
                sale(0, {"status": contenido, "ahead_by": int(contenido == "ahead"), "behind_by": int(contenido == "behind")})
            sale(0, {"status": "diverged", "ahead_by": 1, "behind_by": 1})
error(404, "Not Found")
'''


def correr(args, timeout=120, gh=None):
    """Corre un script de la pieza con Python 3 -I desde la raíz del repositorio, con el gh falso delante en el PATH y
    la red cerrada por un proxy que no existe. Devuelve (código, stdout, stderr, llamadas a gh)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GH_") and not k.startswith("GITHUB_")
           and k.upper() not in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY")}
    llamadas = None
    if gh is not None:
        b = pathlib.Path(tempfile.mkdtemp(prefix="gh-falso-"))
        atexit.register(shutil.rmtree, b, True)
        (b / "datos.json").write_text(json.dumps(gh, ensure_ascii=False), encoding="utf-8")
        (b / "gh").write_text(f"#!{sys.executable} -I\n{GH_FALSO}", encoding="utf-8")
        (b / "gh").chmod(0o755)
        env["PATH"] = f"{b}{os.pathsep}{env.get('PATH', '')}"
        llamadas = b / "llamadas.txt"
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        env[k] = "http://127.0.0.1:9"
    try:
        r = subprocess.run([sys.executable, "-I"] + [str(a) for a in args], cwd=str(REPO), env=env,
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                           errors="replace", timeout=timeout)
        rc, out, err = r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        rc, out, err = None, "", f"pasó de {timeout} segundos"
    vistas = []
    if llamadas is not None and llamadas.is_file():
        vistas = [" ".join(json.loads(l)) for l in llamadas.read_text(encoding="utf-8").splitlines() if l.strip()]
    return rc, out, err, vistas


def ultimas(texto, n=4):
    return " | ".join([l.strip()[:160] for l in (texto or "").splitlines() if l.strip()][-n:])


def recoger(problemas, gh, auditoria=False, desde=DESDE):
    """recoger_github.py con el gh falso: el JSON que escribe en stdout (y la ruta donde la prueba lo guardó), o (None, None)."""
    if not RECOGER.is_file():
        problemas.append(f"no está recoger_github.py en {RECOGER.relative_to(REPO)}")
        return None, None
    rc, out, err, gh_vio = correr([RECOGER, REPOSITORIO, "--desde", desde] + (["--auditoria"] if auditoria else []), gh=gh)
    try:
        datos = json.loads(out)
    except ValueError:
        problemas.append(f"recoger_github.py salió con {rc} sin un JSON en stdout: {ultimas(err or out)}"
                         f"; pidió a gh: {ultimas(chr(10).join(gh_vio), 3) or 'nada'}")
        return None, None
    if not isinstance(datos, dict):
        problemas.append("el JSON de recoger_github.py no es un objeto")
        return None, None
    p = pathlib.Path(tempfile.mkdtemp(prefix="datos-")) / "github.json"
    atexit.register(shutil.rmtree, p.parent, True)
    p.write_text(out, encoding="utf-8")
    return datos, p


def json_de(problemas, script, rc, out, err, forma):
    """El objeto JSON que un script imprimió con --json, con las claves de su contrato y de su tipo; None si no lo hay."""
    try:
        j = json.loads(out)
    except ValueError:
        problemas.append(f"{script} --json salió con {rc} sin un JSON en stdout: {ultimas(err or out)}")
        return None
    if not isinstance(j, dict):
        problemas.append(f"el JSON de {script} --json no es un objeto: {out.strip()[:120]}")
        return None
    for k, tipos in forma.items():
        if k not in j:
            problemas.append(f"el JSON de {script} --json no trae «{k}»")
        elif not isinstance(j[k], tipos):
            problemas.append(f"«{k}» del JSON de {script} --json es {json.dumps(j[k], ensure_ascii=False)[:120]}, "
                             f"no {' o '.join('null' if t is type(None) else t.__name__ for t in tipos)}")
    return j


# La forma del --json de seguimiento.py (el contrato, campo 3: #2026-11-27-15)
FORMA = {"piezas": (dict,), "fuera_del_plan": (list,), "kit": (list,), "sin_leer": (list,),
         "check_obligatorio": (bool, type(None)), "punto4": (list,), "completa": (bool,), "guardada": (bool,)}


def seguir(problemas, r, datos, guardar=False):
    """seguimiento.py --json sobre la raíz r con los datos de recoger: (código, su JSON), o (None, None)."""
    if not SEGUIR.is_file():
        problemas.append(f"no está seguimiento.py en {SEGUIR.relative_to(REPO)}")
        return None, None
    rc, out, err, _ = correr([SEGUIR, r, PROYECTO, "--datos", datos, "--json"] + (["--guardar"] if guardar else []))
    if rc not in (0, 3):
        problemas.append(f"seguimiento.py --json salió con {rc}, no con 0 ni con 3: {ultimas(err or out)}")
    return rc, json_de(problemas, "seguimiento.py", rc, out, err, FORMA)


def seguimiento(problemas, gh, cambios=(), guardar=False):
    """El seguimiento entero: recoger_github.py y, con su JSON, seguimiento.py --json. Devuelve (raíz, datos, código, JSON)."""
    r = raiz(cambios)
    datos, ruta = recoger(problemas, gh)
    if datos is None:
        return r, None, None, None
    rc, j = seguir(problemas, r, ruta, guardar)
    return r, datos, rc, j


# ---------- leer el JSON y el archivo ----------
def numeros(lista):
    """Los números de pull request de una lista del JSON: 41, «41» o «#41» (y {"number": 41})."""
    out = set()
    for x in lista if isinstance(lista, list) else []:
        x = x.get("number") if isinstance(x, dict) else x
        if isinstance(x, int) and not isinstance(x, bool):
            out.add(x)
        elif isinstance(x, str) and re.fullmatch(r"#?\d+", x.strip()):
            out.add(int(x.strip().lstrip("#")))
    return out


def es(problemas, que, visto, esperado):
    if visto != esperado:
        problemas.append(f"{que} es {json.dumps(visto, ensure_ascii=False)[:200]}, no {json.dumps(esperado, ensure_ascii=False)}")


def estados_son(problemas, que, vistos, esperado):
    vistos = {k: (v.lower() if isinstance(v, str) else v) for k, v in (vistos or {}).items()}
    for pieza, estado in esperado.items():
        if pieza not in vistos:
            problemas.append(f"{que} no trae {pieza}: {json.dumps(vistos, ensure_ascii=False)[:200]}")
        elif vistos[pieza] != estado:
            problemas.append(f"en {que}, {pieza} está {json.dumps(vistos[pieza], ensure_ascii=False)}, y tiene que estar «{estado}»")


def igual_archivo(problemas, r, ruta, antes, por_que):
    ahora = (r / ruta).read_text(encoding="utf-8") if (r / ruta).is_file() else None
    if ahora != antes:
        problemas.append(f"{ruta} cambió, y {por_que}")


def entrada_de_hoy(texto):
    """La entrada «## <hoy>» del seguimiento, hasta el siguiente «## AAAA-MM-DD»; "" si no la hay."""
    m = re.search(r"^## " + re.escape(hoy()) + r"\s*$(.*?)(?=^## \d{4}-\d{2}-\d{2}\s*$|\Z)", texto, re.M | re.S)
    return m.group(1) if m else ""


ANTES = MUESTRA[SEGUIMIENTO].replace("## 2026-11-20\n", f"## {DESDE}\n")   # el seguimiento de la muestra, sin tocar


def guardada(problemas, r, j, rc, que):
    """Con --guardar: salió con 0, «guardada» es true, la entrada de hoy está arriba y las anteriores siguen debajo.
    Devuelve la entrada de hoy del archivo ("" si no está)."""
    if rc != 0:
        problemas.append(f"{que}, seguimiento.py --guardar salió con {rc}, no con 0")
    if j is not None and j.get("guardada") is not True:
        problemas.append(f"{que}, el JSON dice guardada={json.dumps(j.get('guardada'))}, no true")
    texto = (r / SEGUIMIENTO).read_text(encoding="utf-8")
    entrada = entrada_de_hoy(texto)
    if not entrada.strip():
        problemas.append(f"{que}, el seguimiento no tiene la entrada de hoy ({hoy()})")
    elif ANTES.split("\n# Seguimiento\n", 1)[1].strip() not in texto:   # Añadido
        problemas.append(f"{que}, al guardar, las entradas anteriores del seguimiento no quedaron tal cual, debajo")
    return entrada


def no_guardada(problemas, r, j, rc, que):
    """Con --guardar y algo sin comprobar: salió con 3, «guardada» es false y el seguimiento no cambió."""
    if rc != 3:
        problemas.append(f"{que}, seguimiento.py salió con {rc}, no con 3")
    if j is not None:
        if j.get("completa") is not False:
            problemas.append(f"{que}, el JSON dice completa={json.dumps(j.get('completa'))}, no false")
        if j.get("guardada") is not False:
            problemas.append(f"{que}, el JSON dice guardada={json.dumps(j.get('guardada'))}, no false")
    igual_archivo(problemas, r, SEGUIMIENTO, ANTES, f"{que} la entrada no se guarda")


# ---------- los escenarios ----------
def escenarios(inf):
    # 1 · Un pull request de bloque y una reversión dan su estado a cada pieza, en la tabla que lee el tablero
    problemas = []
    gh = github([pr(11, "P01 + P02 · Catálogo y precios", "2026-11-18T10:00:00Z"),
                 pr(12, "P03 · Pedido en línea", "2026-11-19T10:00:00Z", ["src/pedidos.py"]),
                 pr(13, 'Revert "P03 · Pedido en línea"', "2026-11-21T10:00:00Z", ["src/pedidos.py"],
                    cuerpo="Reverts muestra/portal#12")])
    r, datos, rc, j = seguimiento(problemas, gh, guardar=True)
    tres = {"P01": "unida", "P02": "unida", "P03": "revertida"}
    if datos is not None:
        completo = datos.get("completo")
        if datos.get("acceso") is not True or not isinstance(completo, dict) or completo.get("prs") is not True \
                or completo.get("releases") is not True:
            problemas.append(f"con todo leído, el JSON de recoger dice acceso={json.dumps(datos.get('acceso'))} y "
                             f"completo={json.dumps(datos.get('completo'))}, no true y {{prs: true, releases: true}}")
        if not isinstance(datos.get("reglas"), list):   # el contrato: la regla se lee siempre
            problemas.append(f"sin --auditoria, el JSON de recoger no trae la regla de la rama principal en «reglas» "
                             f"(dice {json.dumps(datos.get('reglas'), ensure_ascii=False)[:120]})")
    if rc is not None:
        guardada(problemas, r, j, rc, "con todo leído")
        sys.path.insert(0, str(LECTOR))
        from context_core.dev_view import read_follow_up   # el lector del tablero
        fecha, estados = read_follow_up((r / SEGUIMIENTO).read_text(encoding="utf-8"))
        if fecha != hoy():
            problemas.append(f"la entrada más reciente que lee el tablero es la del {fecha or '(ninguna)'}, no la de hoy ({hoy()})")
        else:
            estados_son(problemas, "la tabla de la entrada guardada, leída por el tablero", estados, tres)
    if j is not None:
        estados_son(problemas, "«piezas» del JSON", j.get("piezas"), tres)
        es(problemas, "«completa»", j.get("completa"), True)
        es(problemas, "«check_obligatorio», con «pruebas de aceptación» en la regla", j.get("check_obligatorio"), True)  # Añadido
        es(problemas, "«punto4», que el script no juzga (#2026-11-27-14)", j.get("punto4"), ["pendiente de revisar"])  # Añadido
    # Añadido: los mismos datos con la regla de la rama principal en 403. La lista está completa y hay acceso: se guarda,
    # sale con 0, y el check obligatorio queda sin comprobar (null)
    if RECOGER.is_file() and SEGUIR.is_file():
        r, datos, rc, j = seguimiento(problemas, dict(copy.deepcopy(gh), reglas=None), guardar=True)
        if datos is not None and datos.get("reglas", "(no está)") is not None:
            problemas.append(f"con la regla en 403, el JSON de recoger no trae «reglas»: null (dice "
                             f"{json.dumps(datos.get('reglas', '(no está)'), ensure_ascii=False)[:120]})")
        if rc is not None:
            guardada(problemas, r, j, rc, "con la regla en 403 y todo lo demás leído")
        if j is not None:
            es(problemas, "«check_obligatorio» con la regla en 403", j.get("check_obligatorio", "(no está)"), None)
            es(problemas, "«completa» con la regla en 403", j.get("completa"), True)
    inf.escenario("Block pull requests and reverts give each piece its state", problemas)

    # 2 · Una lista cortada en el límite: «sin comprobar» donde hace falta; se muestra y no se guarda
    problemas = []
    r, datos, rc, j = seguimiento(problemas, github(pulls_sin_fin=True), guardar=True)
    if datos is not None and (datos.get("completo") or {}).get("prs") is not False:
        problemas.append(f"con la lista de pull requests cortada, el JSON de recoger dice completo="
                         f"{json.dumps(datos.get('completo'))}, sin prs: false")
    if rc is not None:
        no_guardada(problemas, r, j, rc, "con una lista incompleta")
    if j is not None:
        estados_son(problemas, "«piezas» del JSON", j.get("piezas"), {p: "sin comprobar" for p in ("P01", "P02", "P03")})
    inf.escenario("An incomplete list is never saved as whole", problemas)

    # 3 · Entregada solo si el release contiene el commit, aunque su fecha sea posterior
    problemas = []
    gh = github([pr(21, "P01 · Lista de productos", "2026-11-22T10:00:00Z", sha="a" * 40),
                 pr(20, "P02 · Precios", "2026-11-18T10:00:00Z", ["src/precios.py"], sha="b" * 40)],
                releases=[{"tag_name": "v1.0.0", "name": "1.0.0", "body": "Aprobó: Ana Pérez, 2026-11-25 · seguimiento 2026-11-24",
                           "published_at": "2026-11-25T12:00:00Z", "created_at": "2026-11-25T12:00:00Z",
                           "target_commitish": "main", "sha": "d" * 40}],
                contiene={"v1.0.0": ["b" * 40]})
    r, datos, rc, j = seguimiento(problemas, gh)
    if datos is not None:
        rel = [x for x in datos.get("releases") or [] if isinstance(x, dict) and x.get("tag_name") == "v1.0.0"]
        contiene = rel[0].get("contiene") if rel else None
        if not isinstance(contiene, list) or "a" * 40 in contiene or "b" * 40 not in contiene:
            problemas.append(f"en el JSON de recoger, «contiene» del release v1.0.0 es {json.dumps(contiene)}: tiene que "
                             "traer el commit de P02 (#20) y no el de P01 (#21)")
    if j is not None:
        estados_son(problemas, "«piezas» del JSON", j.get("piezas"), {"P01": "unida", "P02": "entregada"})
    inf.escenario("Delivered only if the release contains the commit", problemas)

    # 4 · Donde unir publica, el sí del pull request de versión entrega; quién y cuándo, en la entrada guardada
    problemas = []
    gh = github([pr(31, "P01 + P02 · 1.2.0", "2026-11-21T10:00:00Z",
                    cuerpo="Catálogo y precios.\n\nAprobó: Ana Pérez, 2026-11-20\n")])
    r, datos, rc, j = seguimiento(problemas, gh, [(PROYECTO_MD, "Paso a Prod: release de GitHub", PASO_UNIR)], guardar=True)
    if rc is not None:
        entrada = guardada(problemas, r, j, rc, "con todo leído")
        if entrada.strip() and not [l for l in entrada.splitlines() if "Ana Pérez" in l and "2026-11-20" in l]:
            problemas.append("ninguna línea de la entrada guardada dice que Ana Pérez dio el sí el 2026-11-20")
    if j is not None:
        estados_son(problemas, "«piezas» del JSON", j.get("piezas"), {"P01": "entregada", "P02": "entregada"})
    inf.escenario("Where merging publishes, the version pull request's yes delivers", problemas)

    # 5 · Lo que está fuera del plan se lista; el «Bump …» que solo cambia workflows cuenta como kit
    problemas = []
    gh = github([pr(40, "Ajusta el pie de página", "2026-11-10T10:00:00Z", ["src/pie.py"]),   # Añadido: antes de --desde
                 pr(41, "Arregla la portada", "2026-11-18T10:00:00Z", ["src/portada.py"]),
                 pr(42, "P09 · Exportar pedidos", "2026-11-19T10:00:00Z", ["src/exportar.py"]),
                 pr(43, "Kit · Ajusta el control", "2026-11-20T10:00:00Z",
                    [".github/workflows/pruebas-aceptacion.yml", "src/api.py"]),
                 pr(44, "Bump actions/checkout from 4 to 5", "2026-11-21T10:00:00Z",
                    [".github/workflows/pruebas.yml"], autor="dependabot[bot]")])
    r, datos, rc, j = seguimiento(problemas, gh)
    if j is not None:
        fuera, kit = numeros(j.get("fuera_del_plan")), numeros(j.get("kit"))
        for n in (41, 42, 43):
            if n not in fuera:
                problemas.append(f"#{n} no está en «fuera_del_plan»: {json.dumps(j.get('fuera_del_plan'))}")
        if 44 not in kit:
            problemas.append(f"#44, el «Bump …» que solo cambia workflows, no está en «kit»: {json.dumps(j.get('kit'))}")
        if 44 in fuera:
            problemas.append("#44, el «Bump …» que solo cambia workflows, está en «fuera_del_plan»")
        if 40 in fuera | kit:   # Añadido: el anterior a --desde no se lee
            problemas.append(f"#40, unido el 2026-11-10, antes de --desde {DESDE}, está en «fuera_del_plan» o en «kit»")
    inf.escenario("What is outside the plan is listed", problemas)

    # 6 · Sin acceso al repositorio: las piezas sin estado, el repositorio nombrado con su motivo, y no se guarda
    problemas = []
    r, datos, rc, j = seguimiento(problemas, github(acceso=False), guardar=True)
    if datos is not None and (datos.get("acceso") is not False or not str(datos.get("motivo") or "").strip()):
        problemas.append(f"sin acceso, el JSON de recoger dice acceso={json.dumps(datos.get('acceso'))} y "
                         f"motivo={json.dumps(datos.get('motivo'), ensure_ascii=False)}, no false con su motivo")
    if rc is not None:
        no_guardada(problemas, r, j, rc, "sin acceso")
    if j is not None:
        piezas = j.get("piezas") if isinstance(j.get("piezas"), dict) else {}
        for p in ("P01", "P02", "P03"):
            if p not in piezas:
                problemas.append(f"«piezas» del JSON no trae {p}: el plan se muestra entero, sin estado")
            elif str(piezas[p]).lower() in ESTADOS:
                problemas.append(f"sin acceso, «piezas» da a {p} el estado «{piezas[p]}»")
        sin_leer = [x for x in j.get("sin_leer") or [] if isinstance(x, dict) and x.get("repo") == REPOSITORIO]
        if not sin_leer:
            problemas.append(f"«sin_leer» no nombra {REPOSITORIO}: {json.dumps(j.get('sin_leer'), ensure_ascii=False)[:200]}")
        elif not str(sin_leer[0].get("motivo") or "").strip():
            problemas.append(f"«sin_leer» nombra {REPOSITORIO} sin su motivo")
    inf.escenario("No access to a repository is said, and nothing is saved", problemas)


if __name__ == "__main__":   # P07 importa de aquí lo común
    flujo.principal("P06", escenarios)
