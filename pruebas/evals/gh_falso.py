#!/usr/bin/env python3
"""Un `gh` de mentira para los evals de la skill desarrollo (1.27): con `github: sin-acceso` en el escenario responde a
todo como un repositorio que la cuenta no ve («HTTP 404», y sale con 1), sin red. correr.py pone una carpeta con este
`gh` delante en el PATH de la conversación.
"""
import sys

print("gh: Not Found (HTTP 404)", file=sys.stderr)
sys.exit(1)
