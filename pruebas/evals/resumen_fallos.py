#!/usr/bin/env python3
"""Para el comentario de evals.yml: de cada escenario con algún FALLA, las llamadas de cada turno (nombre y el principio
de su entrada y de su resultado) y el principio de cada respuesta, en un bloque plegado. Así quien lee el pull request
(o Claude, que no puede bajar el artefacto) ve por qué falló sin la transcripción entera.

Uso: python3 pruebas/evals/resumen_fallos.py <carpeta de resultados>
"""
import json, pathlib, sys

sal = pathlib.Path(sys.argv[1])
try:
    res = json.loads((sal / "resultados.json").read_text(encoding="utf-8"))
except (OSError, ValueError):
    sys.exit(0)
for r in res:
    nombre = r.get("escenario") or r.get("nombre") or ""
    if all(c.get("ok") for c in r.get("comprobaciones", [])):
        continue
    t = sal / f"{nombre}.md"
    if not t.is_file():
        continue
    lineas, dentro = [], None
    for bloque in t.read_text(encoding="utf-8").split("\n### "):
        cab, _, cuerpo = bloque.partition("\n")
        cuerpo = cuerpo.strip().replace("```", "ˋˋˋ")
        lineas.append(f"### {cab}\n{cuerpo[:600]}\n")
    texto = "\n".join(lineas)[:12000]
    print(f"<details><summary>{nombre}: llamadas y respuestas</summary>\n\n````\n{texto}\n````\n</details>\n")
