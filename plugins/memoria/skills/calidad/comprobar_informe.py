#!/usr/bin/env python3
"""Comprueba que un informe de la skill calidad se puede medir (pasos 6 y 7; 1.26.2).

Uso: python3 comprobar_informe.py <informe.md>

Sale con 0 si el informe vale; con 1 y una línea por problema, con su número de línea, si no. Lo llaman la skill antes de
guardar un informe y release.sh antes de publicar una versión: un hallazgo que la lectura de la efectividad (paso 8) no
puede contar deja sin crédito a la lente que lo encontró.

- Cada hallazgo es una entrada «### n.» seguida de su línea «Lens: <lentes> · Pesa: <peso>[ · Modelo: …]», con las lentes
  en inglés y en minúscula; «Modelo:» es obligatorio si la medición dice «contraste». Una lente puede llevar pegada entre
  paréntesis otra que no corrió y cuya pregunta hizo («objective (inconsistencies), risks»; 1.26.11).
- En una revisión de arreglos («, arreglos» en «Tipo:»), cada «Pesa:» dice de dónde viene el hallazgo: «(en el original)»,
  «(lo abrió un arreglo anterior)» o «(lo abrió este arreglo)», y con menos de tres revisores, el motivo; un archivo
  «…-arreglos-<n>.md» es una ronda y su «Tipo:» lleva «, arreglos <n> de …» (1.26.11, anexo arreglos.md).
- En una ronda, «Arreglados:» lleva detrás «· impiden n» cuando hay hallazgos que impiden y se arregló alguno; release.sh
  lo pide también al informe de la versión (1.26.11).
- Ninguna otra línea lleva «Lens:» o «Lente:», y en las secciones de hallazgos no hay listas ni tablas con lentes.
- Las dudas van en su sección («## Dudas», «## Doubts»…), sin «Lens:».
- La medición más nueva es la primera «## Medición»; sus «Hallazgos» por peso cuadran con las entradas, y lleva
  «Razonamiento:» (máximo, alto, medio, bajo o no consta, uno por modelo si se quiere) y «Tokens:».
Los bloques de código (```) no se miran: un informe puede citar el formato.
"""
import re, sys

LENTES = ("errors", "inconsistencies", "objective", "risks", "efficiency")
PESOS = {"impide cumplir el objetivo": "impiden", "pone en riesgo el objetivo": "riesgo", "lo mejora": "mejoran"}
NIVELES = ("máximo", "alto", "medio", "bajo", "no consta")
ORIGENES = ("en el original", "lo abrió un arreglo anterior", "lo abrió este arreglo")
LENTE = r"[a-z]+(?: \((?:errors|inconsistencies|objective|risks|efficiency)\))?"
INICIAL = {"errors": "E", "inconsistencies": "I", "objective": "O", "risks": "R", "efficiency": "F"}
LENS_RE = re.compile(r"^Lens: (?P<lentes>" + LENTE + r"(?:, " + LENTE + r")*)(?: \([^)]*\))? · Pesa: (?P<pesa>[^·(]+?)(?: \((?P<origen>[^)]*)\))?"
                     r"(?: · Modelo: (?P<modelo>\S.*))?$")
NOMBRES = r"errors|inconsistencies|objective|risks|efficiency|errores|inconsistencias|objetivo|riesgos|eficiencia"
LISTA_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)]|\|).*[(\[]\s*(?:%s)\b" % NOMBRES, re.I)
HALLAZGOS_RE = re.compile(r"^Hallazgos: (\d+) · impiden (\d+) · riesgo (\d+) · mejoran (\d+)\s*$")
DUDAS_RE = re.compile(r"^## .*\b(dudas?|doubts?)\b", re.I)
SECCION_HALLAZGOS_RE = re.compile(r"^## .*\b(impide|riesgo|mejora|hallazgos|blocks?|risk|improves?|findings)\b", re.I)


def comprobar(texto, ruta=""):
    lineas = texto.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    problemas = []
    seccion, en_codigo, entrada_abierta = "", False, None
    entradas, medicion = [], None
    contraste = False
    # primero la medición más nueva, para saber si hay contraste
    for i, l in enumerate(lineas):
        if l.strip() == "## Medición":
            medicion = []
            for m in lineas[i + 1:]:
                if m.startswith("## "):
                    break
                medicion.append(m)
            break
    if medicion is None:
        return ["falta la sección «## Medición» (paso 7)"]
    modelo = next((m for m in medicion if m.startswith("Modelo: ")), "")
    contraste = "contraste" in modelo
    tipo = next((m for m in medicion if m.startswith("Tipo: ")), "")
    arreglos = ", arreglos" in tipo.split("·")[0]
    ronda = re.search(r"-arreglos-(\d+)\.md$", ruta or "")
    if ronda and not re.search(r", arreglos %s de \S" % ronda.group(1), tipo.split("·")[0]):
        return [f"una ronda de arreglos lleva en «Tipo:» «, arreglos {ronda.group(1)} de <informe de la primera revisión>», con el número de su nombre (anexo arreglos.md)"]
    arreglos = arreglos or bool(ronda)
    prof = next((m for m in medicion if m.startswith("Profundidad: ")), "")
    corrieron = set(re.findall(r"\b[EIORF]\b", prof.split("Lentes:", 1)[1].split("(")[0])) if "Lentes:" in prof else set()
    rev = re.search(r"Revisores: (\d+)( \()?", prof)
    if arreglos and rev and int(rev.group(1)) < 3 and not rev.group(2):
        problemas.append("una ronda de arreglos con menos de tres revisores dice por qué entre paréntesis («Revisores: 2 (…)»)")
    for n, l in enumerate(lineas, 1):
        if l.lstrip().startswith("```"):
            en_codigo = not en_codigo
            continue
        if en_codigo:
            continue
        if l.startswith("## "):
            seccion, entrada_abierta = l, None
            continue
        if seccion.strip() in ("## Medición", "## Lo que se escapó"):
            continue
        if re.match(r"^### \d+\. ", l):
            entrada_abierta = [n, l, False]
            entradas.append(entrada_abierta)
            continue
        if l.startswith("### "):
            entrada_abierta = None
            continue
        if re.match(r"^(Lens|Lente):", l):
            if DUDAS_RE.match(seccion):
                problemas.append(f"línea {n}: una duda no lleva «{l.split(':')[0]}:» (va en su sección, sin línea de lentes): {l[:80]}")
                continue
            if l.startswith("Lente:"):
                problemas.append(f"línea {n}: «Lente:» pasó a «Lens:», con las lentes en inglés: {l[:80]}")
                continue
            if entrada_abierta is None or entrada_abierta[2]:
                problemas.append(f"línea {n}: «Lens:» fuera de una entrada «### n.» (o una segunda en la misma): {l[:80]}")
                continue
            entrada_abierta[2] = True
            m = LENS_RE.match(l.rstrip())
            if not m:
                problemas.append(f"línea {n}: la línea no tiene la forma «Lens: errors, risks · Pesa: lo mejora[ · Modelo: …]»: {l[:80]}")
                entrada_abierta.append(None)
                continue
            malas = []
            for x in m.group("lentes").split(", "):
                nombre, _, preg = x.partition(" (")
                preg = preg.rstrip(")")
                if nombre not in LENTES:
                    malas.append(nombre)
                if preg and (preg not in LENTES or preg == nombre):
                    malas.append(f"({preg})")
                elif preg and INICIAL[preg] in corrieron:
                    problemas.append(f"línea {n}: «{preg}» corrió en esta revisión: una lente que corrió no va entre paréntesis")
            libre = re.search(r"^Lens: [^·]*\(([^)]*)\) · Pesa", l)
            if libre and " " not in libre.group(1).strip() and libre.group(1).strip().lower() in LENTES and libre.group(1).strip() not in LENTES:
                problemas.append(f"línea {n}: la lente pegada va en minúscula y sola: ({libre.group(1)})")
            if malas:
                problemas.append(f"línea {n}: lentes que no existen o no van en inglés ({', '.join(malas)}); son {', '.join(LENTES)}")
            pesa = m.group("pesa").strip()
            if pesa not in PESOS:
                problemas.append(f"línea {n}: «Pesa: {pesa}» no es «impide cumplir el objetivo», «pone en riesgo el objetivo» ni «lo mejora»")
            if arreglos and (m.group("origen") or "").strip() not in ORIGENES:
                problemas.append(f"línea {n}: en una revisión de arreglos, «Pesa:» dice de dónde viene: «(en el original)», «(lo abrió un arreglo anterior)» o «(lo abrió este arreglo)»")
            if contraste and not m.group("modelo"):
                problemas.append(f"línea {n}: en un contraste cada hallazgo dice «· Modelo: los dos» o el modelo que lo encontró")
            entrada_abierta.append(PESOS.get(pesa))
            continue
        if SECCION_HALLAZGOS_RE.match(seccion) and not DUDAS_RE.match(seccion) and entrada_abierta is None and LISTA_RE.match(l):
            problemas.append(f"línea {n}: un hallazgo en una lista o una tabla; va como entrada «### n.» con su «Lens:»: {l[:80]}")
    for e in entradas:
        if not e[2]:
            problemas.append(f"línea {e[0]}: la entrada no lleva su línea «Lens:» justo debajo: {e[1][:80]}")
    # la medición
    for clave, patron, ejemplo in (
            ("Razonamiento", r"^Razonamiento: (.+)$", "Razonamiento: medio"),
            ("Tokens", r"^Tokens: (\d+k|no consta)\b.*$", "Tokens: 432k")):
        linea = next((m for m in medicion if m.startswith(clave + ":")), None)
        if linea is None or not re.match(patron, linea.strip()):
            problemas.append(f"la medición no lleva «{ejemplo}» (paso 7)")
        elif clave == "Razonamiento":
            valor = linea.split(":", 1)[1].strip()
            niveles = [p.strip().split(" ")[-1] if not p.strip().endswith("no consta") else "no consta" for p in valor.split("·")]
            if any(x not in NIVELES for x in niveles):
                problemas.append(f"«{linea.strip()}»: el nivel es uno de {', '.join(NIVELES)} (o uno por modelo: «Fable 5.2 medio · Opus 5.5 alto»)")
        elif clave == "Tokens" and contraste and "no consta" not in linea and len(re.findall(r"\d+k", linea)) < 3:
            problemas.append(f"«{linea.strip()}»: en un contraste van también los de cada modelo («Tokens: 693k · Fable 5.2 360k (E, R 240k) · Opus 5.5 333k»)")
    h = next((HALLAZGOS_RE.match(m.strip()) for m in medicion if m.startswith("Hallazgos:")), None)
    if arreglos and not h:
        problemas.append("una ronda de arreglos lleva «Hallazgos: n · impiden n · riesgo n · mejoran n» (paso 7)")
    if h:
        total, imp, rie, mej = (int(x) for x in h.groups())
        arr = next((re.match(r"^Arreglados: (\d+)(?: · impiden (\d+))?\s*$", m.strip()) for m in medicion if m.startswith("Arreglados:")), None)
        if arr is None:
            problemas.append("la medición no lleva «Arreglados: n» (paso 7)")
        elif arreglos and imp and int(arr.group(1)) > 0 and arr.group(2) is None:
            problemas.append(f"«Arreglados:» dice detrás cuántos de los {imp} que impiden se arreglaron («Arreglados: {arr.group(1)} · impiden {imp}»)")
        if imp + rie + mej != total:
            problemas.append(f"«Hallazgos: {total}» no es la suma de sus pesos ({imp} + {rie} + {mej})")
        cuenta = {"impiden": 0, "riesgo": 0, "mejoran": 0}
        for e in entradas:
            if len(e) > 3 and e[3]:
                cuenta[e[3]] += 1
        if len(entradas) != total or (cuenta["impiden"], cuenta["riesgo"], cuenta["mejoran"]) != (imp, rie, mej):
            problemas.append(f"el informe tiene {len(entradas)} hallazgos (impiden {cuenta['impiden']} · riesgo {cuenta['riesgo']} · "
                             f"mejoran {cuenta['mejoran']}) y su medición más nueva dice {total} (impiden {imp} · riesgo {rie} · mejoran {mej})")
    return problemas


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip().split("\n")[2], file=sys.stderr)
        return 2
    with open(sys.argv[1], encoding="utf-8") as f:
        problemas = comprobar(f.read(), sys.argv[1])
    for p in problemas:
        print(p)
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
