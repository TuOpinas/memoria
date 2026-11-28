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
plantilla; «con el sí» es auditoria.py --escribir. Cómo se lee cada escenario está en RESUMEN.md.
Uso, desde la raíz del repositorio: python3 -I pruebas/aceptacion/P07_auditoria_mensual.py (0 pasa, 1 falla, 2 no se montó).
"""
import pathlib, re, sys

sys.dont_write_bytecode = True   # no deja __pycache__ en la carpeta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from P06_seguimiento_por_script import (flujo, REPO, AUDITAR, CONFIG, CONFIGURACION, CON_CONFIG, REGLAS_BIEN,  # noqa: E402
                                        PROYECTO, raiz, github, pr, recoger, correr, ultimas, hoy, igual_archivo)
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


def auditar(problemas, gh, escribir=False):
    """recoger_github.py --auditoria y auditoria.py sobre una raíz con configuracion.md. Devuelve (raíz, código, salida)."""
    r = raiz(CON_CONFIG, {CONFIG: CONFIGURACION})
    datos, ruta = recoger(problemas, gh, auditoria=True, desde=ULTIMA_AUDITORIA)
    if datos is None:
        return r, None, ""
    if not AUDITAR.is_file():
        problemas.append(f"no está auditoria.py en {AUDITAR.relative_to(REPO)}")
        return r, None, ""
    rc, out, err, _ = correr([AUDITAR, r, PROYECTO, "--datos", ruta] + (["--escribir"] if escribir else []))
    if rc != 0:
        problemas.append(f"auditoria.py{' --escribir' if escribir else ''} salió con {rc}, no con 0: {ultimas(err or out)}")
    return r, rc, out


def bloque(texto, fila):
    """Lo que la salida dice de una fila: desde la primera línea que la nombra hasta la siguiente que nombra otra."""
    out, dentro = [], False
    for l in texto.splitlines():
        nombra = [f for f in FILAS if re.search(r"(?<![A-Za-z0-9])" + f + r"(?![0-9])", l)]
        if dentro and nombra and fila not in nombra:
            break
        if fila in nombra:
            dentro = True
        if dentro:
            out.append(l)
    return "\n".join(out)


def propone(problemas, out, fila, estado, evidencia=()):
    b = bloque(out, fila).lower()
    if not b:
        problemas.append(f"la propuesta no nombra {fila}")
        return b
    dice = "no cumple" if "no cumple" in b else "sin comprobar" if "sin comprobar" in b else (
        "cumple" if re.search(r"\bcumple\b", b) else "nada")
    if dice != estado:
        problemas.append(f"{fila} sale propuesta como «{dice}», no como «{estado}»: {b[:200]!r}")
    for e in evidencia:
        if e.lower() not in b:
            problemas.append(f"lo que dice de {fila} no trae «{e}» como evidencia: {b[:200]!r}")
    return b


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
    r, rc, out = auditar(problemas, github(PRS_EN_REGLA, reglas=sin_aceptacion()))
    if rc is not None:
        propone(problemas, out, "R2", "no cumple", ["pruebas de aceptación"])
        igual_archivo(problemas, r, CONFIG, CONFIGURACION, "sin --escribir (sin el sí) no se escribe nada")
    inf.escenario("A failing rule is proposed with its evidence", problemas)

    # 2 · Sin acceso a las reglas se dice, no se adivina
    problemas = []
    r, rc, out = auditar(problemas, github(PRS_EN_REGLA, reglas=None))
    if rc is not None:
        for fila in ("R1", "R2"):
            b = propone(problemas, out, fila, "sin comprobar")
            if b and not re.search(r"403|acceso|permiso|not accessible", b):
                problemas.append(f"lo que dice de {fila} no da el motivo (que no hay acceso a las reglas: HTTP 403): {b[:200]!r}")
        igual_archivo(problemas, r, CONFIG, CONFIGURACION, "sin --escribir (sin el sí) no se escribe nada")
    inf.escenario("No access is said, not guessed", problemas)

    # 3 · Un pull request unido sin pieza hace fallar R6, con su número
    problemas = []
    r, rc, out = auditar(problemas, github(PRS_EN_REGLA + [pr(51, "Arregla la portada", "2026-11-05T10:00:00Z",
                                                              ["src/portada.py"], autor="luis")]))
    if rc is not None:
        b = propone(problemas, out, "R6", "no cumple", ["#51"])
        for n in (52, 53, 54, 55, 56):   # Añadido: los de pieza, escenarios, kit, reversión y bot no son evidencia
            if re.search(rf"#{n}(?![0-9])", b):
                problemas.append(f"R6 da como evidencia #{n}, que está en regla")
    inf.escenario("A merged pull request without a piece fails R6", problemas)

    # 4 · Con el sí, un solo cambio; lo que la API no ve se queda y se lista
    problemas = []
    antes = hoy()
    r, rc, out = auditar(problemas, github(PRS_EN_REGLA, reglas=sin_aceptacion()), escribir=True)
    if rc is not None:
        fechas = {antes, hoy()}
        texto = (r / CONFIG).read_text(encoding="utf-8")
        vistas, eran = celdas(texto), celdas(CONFIGURACION)
        for fila, estado in (("R1", "cumple"), ("R2", "no cumple")):
            if vistas.get(fila) not in {f"{estado} · {f}" for f in fechas}:
                problemas.append(f"en configuracion.md, {fila} dice «{vistas.get(fila)}», no «{estado} · {hoy()}»")
        for fila in LA_API_NO_VE:
            if vistas.get(fila) != eran[fila]:
                problemas.append(f"en configuracion.md, {fila} pasó de «{eran[fila]}» a «{vistas.get(fila)}»: la API no lo ve")
            if not re.search(r"(?<![A-Za-z0-9])" + fila + r"(?![0-9])", out):
                problemas.append(f"la salida no lista {fila} para quien administra")
        def fuera(t):   # todo menos las filas que propone la auditoría y la línea «actualizado:»
            return [l for l in t.splitlines() if not l.startswith("actualizado:")
                    and not re.match(r"\|\s*(R1|R2|R3|R6|PL1|PL2)\s*\|", l)]
        if fuera(texto) != fuera(CONFIGURACION):
            problemas.append("configuracion.md cambió fuera de las filas que propone la auditoría")
    inf.escenario("With the yes, one change; what the API cannot see stays", problemas)


if __name__ == "__main__":
    flujo.principal("P07", escenarios)
