#!/usr/bin/env python3
"""Un `gh` de mentira para los evals de la skill desarrollo (1.27): responde `gh api <ruta>` desde un JSON de
escenarios/, sin red. El escenario lo pide con `github: <archivo>.json` (o `github: sin-acceso`, que responde a todo
como un repositorio que la cuenta no ve); correr.py pone una carpeta con este `gh` delante en el PATH de la conversación.

El JSON es {"<ruta sin la consulta>": <respuesta>}, con las rutas como las pide recoger_github.py («repos/acme/app»,
«repos/acme/app/pulls», «repos/acme/app/commits/<sha o etiqueta>»…). Una lista solo sale en la página 1. Una ruta que
no está responde «HTTP 404» y sale con 1, como gh. «{HOY-N}» es la fecha de hace N días, en la zona de la conversación.
"""
import datetime, json, os, re, sys
from zoneinfo import ZoneInfo


def main(argv):
    if not argv or argv[0] != "api":
        print("gh de mentira: solo «gh api»", file=sys.stderr)
        return 1
    ruta = next((a for a in argv[1:] if not a.startswith("-") and not a.startswith("Accept:")), "")
    origen = os.environ.get("GH_FALSO", "")
    if origen == "sin-acceso" or not origen:
        print("gh: Not Found (HTTP 404)", file=sys.stderr)
        return 1
    hoy = datetime.datetime.now(ZoneInfo("America/Mexico_City")).date()
    texto = re.sub(r"\{HOY-(\d+)\}", lambda m: (hoy - datetime.timedelta(days=int(m.group(1)))).isoformat(),
                   open(origen, encoding="utf-8").read())
    datos = json.loads(texto)
    base, _, consulta = ruta.partition("?")
    if base not in datos:
        print("gh: Not Found (HTTP 404)", file=sys.stderr)
        return 1
    r = datos[base]
    pagina = re.search(r"(?:^|&)page=(\d+)", consulta)
    if isinstance(r, list) and pagina and pagina.group(1) != "1":
        r = []
    print(json.dumps(r))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
