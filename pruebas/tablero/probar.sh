#!/usr/bin/env bash
# Prueba el tablero contra la raíz inventada de raiz/. No toca ninguna raíz real ni nada de lo que se instala.
# 1. Genera los datos en los dos modos y comprueba fugas, plazos, entregables y decisiones (solo Python).
# 2. Si hay Node con Playwright, monta las páginas y las recorre en claro, oscuro y móvil, con capturas.
# Uso: pruebas/tablero/probar.sh [carpeta-de-salida]   (por defecto, una carpeta temporal)
set -eu
AQUI="$(cd "$(dirname "$0")" && pwd)"
TABLERO="$AQUI/../../plugins/memoria/skills/tablero"
OUT="${1:-$(mktemp -d)}"
VERSION="$(sed -n 's/.*"version": *"\([0-9.]*\)".*/\1/p' "$TABLERO/../../.claude-plugin/plugin.json" 2>/dev/null | head -n 1)"
mkdir -p "$OUT/capturas"
# copia de la raíz con fechas de archivo fijas: todo del 2026-08-01 salvo un entregable tocado hoy,
# para probar el aviso de trabajo sin sesión sin depender de cuándo se clonó el repo
rm -rf "$OUT/raiz"; cp -R "$AQUI/raiz" "$OUT/raiz"
python3 - "$OUT/raiz" <<'PY'
import os, sys, time
viejo = time.mktime((2026, 8, 1, 12, 0, 0, 0, 0, -1))
for d, _, fs in os.walk(sys.argv[1]):
    for f in fs: os.utime(os.path.join(d, f), (viejo, viejo))
os.utime(os.path.join(sys.argv[1], "ventas/cuentas/entregables/kit-cuentas.md"), None)
PY
python3 "$TABLERO/generar_vista.py" "$OUT/raiz" "$OUT/publico" --modo publico --version "${VERSION:-prueba}" >/dev/null
python3 "$TABLERO/generar_vista.py" "$OUT/raiz" "$OUT/completo" --modo completo --version "${VERSION:-prueba}" >/dev/null
python3 "$AQUI/comprobar.py" "$OUT/publico" "$OUT/completo"
for m in publico completo; do python3 "$AQUI/montar.py" "$TABLERO/vista.html" "$OUT/$m" "$OUT/$m.html"; done
if command -v node >/dev/null && node -e "require('playwright')" 2>/dev/null; then
  node "$AQUI/recorrer.js" "$OUT" "$OUT/capturas"
  echo "Capturas en $OUT/capturas"
else
  echo "Sin Node con Playwright: se saltó el recorrido de la página. Las páginas de prueba están en $OUT (publico.html, completo.html)."
fi
