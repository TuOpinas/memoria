#!/usr/bin/env python3
"""P07 · Monthly audit with evidence (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-27, en el plan).

- A failing rule is proposed with its evidence. Dado a branch rule without the acceptance check required, Cuando the
  audit runs, Entonces R2 is proposed as «no cumple» with its evidence, and nothing is written without the yes.
- No access is said, not guessed. Dado no access to the repository's rules, Cuando the audit runs, Entonces R1 and R2
  are «sin comprobar» with the reason.
- A merged pull request without a piece fails R6. Dado a pull request merged since the last audit whose title names no
  piece and is not «Escenarios · », «Kit · », a revert or a bot's, Cuando the audit runs, Entonces R6 is proposed as
  «no cumple», with that pull request's number as evidence.
- With the yes, one change; what the API cannot see stays. Dado an audit that proposes R1 «cumple» and R2 «no cumple»,
  and the yes of whoever accepts, Cuando the audit is written, Entonces `configuracion.md` changes in one write with both
  states and today's date, and PL3 to PL7, R4, R5 and R7 keep their state and are listed for whoever administers.

Por el contrato del encargo (campo 3): «la auditoría corre» es recoger_github.py --auditoria con el `gh` falso de
P06_seguimiento_por_script.py y, sobre su salida, auditoria.py contra la raíz de muestra con un configuracion.md de la
plantilla; «con el sí» es auditoria.py --escribir. La prueba mira el JSON de auditoria.py --json (#2026-11-27-15), su
código de salida y configuracion.md; el texto de la propuesta, la verificación. Cómo se lee cada escenario está en RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P07_auditoria_mensual.py (0 pasa, 1 falla, 2 no se montó).
"""
import json, pathlib, re, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P06_seguimiento_por_script import (flujo, REPO, AUDITAR, CONFIG, CONFIGURACION, CON_CONFIG, REGLAS_BIEN,  # noqa: E402
                                        PROYECTO, raiz, github, pr, recoger, correr, ultimas, hoy, igual_archivo,
                                        json_de)
import copy  # noqa: E402

ULTIMA_AUDITORIA = "2026-10-28"
FILAS = ("PL1", "PL2", "PL3", "PL4", "PL5", "PL6", "PL7", "R1", "R2", "R3", "R4", "R5", "R6", "R7")
LA_API_NO_VE = ("PL3", "PL4", "PL5", "PL6", "PL7", "R4", "R5", "R7")


def sin_aceptacion():
    """La regla de main bien puesta, salvo el check «pruebas de aceptación», que no es obligatorio."""
    reglas = copy.deepcopy(REGLAS_BIEN)
    for r in reglas:
        if r["type"] == "required_status_checks":
            r["parameters"]["required_status_checks"] = [{"context": "pruebas"}, {"context": "secretos"}]
    return reglas


PRS_EN_REGLA = [pr(52, "P01 · Lista de productos", "2026-11-03T10:00:00Z"),
                pr(53, "Escenarios · P02", "2026-11-04T10:00:00Z", ["pruebas/aceptacion/P02_precios.py"]),
                pr(54, "Kit · El control", "2026-11-06T10:00:00Z", [".github/workflows/pruebas-aceptacion.yml"]),
                pr(55, 'Revert "P01 · Lista de productos"', "2026-11-07T10:00:00Z"),
                pr(56, "Bump requests from 2.31 to 2.32", "2026-11-08T10:00:00Z", ["requirements.txt"],
                   autor="dependabot[bot]")]


# La forma del --json de auditoria.py (el contrato, campo 3: #2026-11-27-15)
FORMA = {"filas": (dict,), "sin_api": (list,), "escrita": (bool,)}


def auditar(problemas, gh, escribir=False):
    """recoger_github.py --auditoria y auditoria.py --json sobre una raíz con configuracion.md. Devuelve (raíz, código,
    JSON); el JSON es None si no lo hay."""
    r = raiz(CON_CONFIG, {CONFIG: CONFIGURACION})
    datos, ruta = recoger(problemas, gh, auditoria=True, desde=ULTIMA_AUDITORIA)
    if datos is None:
        return r, None, None
    if not AUDITAR.is_file():
        problemas.append(f"no está auditoria.py en {AUDITAR.relative_to(REPO)}")
        return r, None, None
    rc, out, err, _ = correr([AUDITAR, r, PROYECTO, "--datos", ruta, "--json"] + (["--escribir"] if escribir else []))
    j = json_de(problemas, "auditoria.py", rc, out, err, FORMA)
    filas = j.get("filas") if j is not None and isinstance(j.get("filas"), dict) else {}
    sin = [f for f, v in filas.items() if isinstance(v, dict) and v.get("estado") == "sin comprobar"]
    # Sale con 0, o con 3 si alguna fila queda «sin comprobar»; con alguna así, también vale 0
    if rc not in (0, 3) or (rc == 3 and j is not None and not sin):
        problemas.append(f"auditoria.py --json{' --escribir' if escribir else ''} salió con {rc}, no con 0 (ni con 3 con "
                         f"alguna fila «sin comprobar»): {ultimas(err or out)}")
    if j is not None and j.get("escrita") is not escribir:
        problemas.append(f"el JSON de auditoria.py dice escrita={json.dumps(j.get('escrita'))}"
                         f"{' con' if escribir else ' sin'} --escribir")
    return r, rc, j


def fila(problemas, j, nombre, estado, evidencia=()):
    """La fila del JSON tiene ese estado y su evidencia nombra cada cosa de evidencia. Devuelve su evidencia ("" si no)."""
    if j is None:
        return ""
    f = (j.get("filas") or {}).get(nombre) if isinstance(j.get("filas"), dict) else None
    if not isinstance(f, dict):
        problemas.append(f"«filas» del JSON de auditoria.py no trae {nombre}")
        return ""
    if f.get("estado") != estado:
        problemas.append(f"{nombre} sale propuesta como {json.dumps(f.get('estado'), ensure_ascii=False)}, no como «{estado}»")
    ev = f.get("evidencia") if isinstance(f.get("evidencia"), str) else json.dumps(f.get("evidencia"), ensure_ascii=False)
    if not (ev or "").strip() or ev == "null":
        problemas.append(f"{nombre} no trae evidencia")
        return ""
    for e in evidencia:
        if e.lower() not in ev.lower():
            problemas.append(f"la evidencia de {nombre} no nombra «{e}»: {ev[:200]!r}")
    return ev


def celdas(texto):
    """{fila: estado} de las dos tablas de configuracion.md (la última celda de cada fila PL*/R*)."""
    out = {}
    for l in texto.splitlines():
        c = [x.strip() for x in l.strip().strip("|").split("|")] if l.strip().startswith("|") else []
        if c and c[0] in FILAS:
            out[c[0]] = c[-1]
    return out




def escenarios(inf):
    # 1 · Una regla que falla se propone con su evidencia, y sin el sí no se escribe nada
    problemas = []
    r, rc, j = auditar(problemas, github(PRS_EN_REGLA, reglas=sin_aceptacion()))
    if rc is not None:
        fila(problemas, j, "R2", "no cumple", ["pruebas de aceptación"])
        igual_archivo(problemas, r, CONFIG, CONFIGURACION, "sin --escribir (sin el sí) no se escribe nada")
    inf.escenario("A failing rule is proposed with its evidence", problemas)

    # 2 · Sin acceso a las reglas se dice, no se adivina
    problemas = []
    r, rc, j = auditar(problemas, github(PRS_EN_REGLA, reglas=None))
    if rc is not None:
        for nombre in ("R1", "R2"):
            ev = fila(problemas, j, nombre, "sin comprobar")
            if ev and not re.search(r"403|acceso|permiso|accessible", ev, re.I):
                problemas.append(f"la evidencia de {nombre} no da el motivo (HTTP 403, sin acceso a las reglas): {ev[:200]!r}")
        igual_archivo(problemas, r, CONFIG, CONFIGURACION, "sin --escribir (sin el sí) no se escribe nada")
    inf.escenario("No access is said, not guessed", problemas)

    # 3 · Un pull request unido sin pieza hace fallar R6, con su número
    problemas = []
    r, rc, j = auditar(problemas, github(PRS_EN_REGLA + [pr(51, "Arregla la portada", "2026-11-05T10:00:00Z",
                                                            ["src/portada.py"], autor="luis"),
                                                         pr(50, "Ajusta el pie de página", "2026-10-20T10:00:00Z",
                                                            ["src/pie.py"], autor="luis")]))
    if rc is not None:
        ev = fila(problemas, j, "R6", "no cumple")
        if ev and not re.search(r"(?<![0-9])51(?![0-9])", ev):
            problemas.append(f"la evidencia de R6 no da el número de #51: {ev[:200]!r}")
        for n in (52, 53, 54, 55, 56):   # Añadido: los de pieza, escenarios, kit, reversión y bot no son evidencia
            if re.search(rf"(?<![0-9]){n}(?![0-9])", ev):
                problemas.append(f"R6 da como evidencia #{n}, que está en regla")
        if re.search(r"(?<![0-9])50(?![0-9])", ev):   # Añadido: el unido antes de la última auditoría no cuenta
            problemas.append(f"R6 da como evidencia #50, unido el 2026-10-20, antes de la última auditoría ({ULTIMA_AUDITORIA})")
    inf.escenario("A merged pull request without a piece fails R6", problemas)

    # 4 · Con el sí, un solo cambio; lo que la API no ve se queda y se lista
    problemas = []
    antes = hoy()
    r, rc, j = auditar(problemas, github(PRS_EN_REGLA, reglas=sin_aceptacion()), escribir=True)
    if rc is not None:
        fila(problemas, j, "R1", "cumple")
        fila(problemas, j, "R2", "no cumple")
        fechas = {antes, hoy()}
        texto = (r / CONFIG).read_text(encoding="utf-8")
        vistas, eran = celdas(texto), celdas(CONFIGURACION)
        for nombre, estado in (("R1", "cumple"), ("R2", "no cumple")):
            if vistas.get(nombre) not in {f"{estado} · {f}" for f in fechas}:
                problemas.append(f"en configuracion.md, {nombre} dice «{vistas.get(nombre)}», no «{estado} · {hoy()}»")
        sin_api = set(x for x in (j or {}).get("sin_api") or [] if isinstance(x, str))
        for nombre in LA_API_NO_VE:
            if vistas.get(nombre) != eran[nombre]:
                problemas.append(f"en configuracion.md, {nombre} pasó de «{eran[nombre]}» a «{vistas.get(nombre)}»: la API no lo ve")
            if j is not None and nombre not in sin_api:
                problemas.append(f"«sin_api» del JSON no lista {nombre} para quien administra: {json.dumps(j.get('sin_api'))}")
        def fuera(t):   # todo menos las filas que propone la auditoría y la línea «actualizado:»
            return [l for l in t.splitlines() if not l.startswith("actualizado:")
                    and not re.match(r"\|\s*(R1|R2|R3|R6|PL1|PL2)\s*\|", l)]
        if fuera(texto) != fuera(CONFIGURACION):
            problemas.append("configuracion.md cambió fuera de las filas que propone la auditoría")
    inf.escenario("With the yes, one change; what the API cannot see stays", problemas)


if __name__ == "__main__":
    flujo.principal("P07", escenarios)
