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
# una tarea sin horario: el tablero lo sabe, para no esperar que se ponga al día cada mañana
python3 "$TABLERO/generar_vista.py" "$OUT/raiz" "$OUT/manual" --modo publico --tarea trig_prueba --manual --version "${VERSION:-prueba}" >/dev/null
python3 - "$OUT/manual/meta/estado.json" <<'PY'
import json, sys
m = json.load(open(sys.argv[1], encoding="utf-8"))
ok = m.get("tarea") == "trig_prueba" and m.get("tarea_manual") is True
print(("  bien  " if ok else "  FALLA ") + "una tarea sin horario (--manual) queda marcada como tal")
sys.exit(0 if ok else 1)
PY
# en dos tiempos (inventario en la computadora, generación sobre la copia) sale exactamente lo mismo
python3 "$AQUI/dos_tiempos.py" "$TABLERO/generar_vista.py" "$TABLERO/plan_subida.py" "$OUT/raiz" "$OUT/dos-tiempos"
rm -rf "$OUT/raiz-cola"; cp -R "$OUT/raiz" "$OUT/raiz-cola"
python3 "$AQUI/aplicar.py" "$TABLERO/aplicar_cambios.py" "$OUT/raiz-cola"
# la apertura de sesión en una llamada (skill sesion, abrir.py), contra la misma raíz inventada
python3 "$AQUI/../sesion/probar_abrir.py"
# el hook de arranque: JSON válido, versión, bloque entero, y que release.sh pare si el bloque se rompe
bash "$AQUI/../hook/probar_hook.sh"
for m in publico completo; do python3 "$AQUI/montar.py" "$TABLERO/vista.html" "$OUT/$m" "$OUT/$m.html"; done
python3 "$AQUI/montar.py" "$TABLERO/vista.html" "$OUT/completo" "$OUT/completo-cierres.html" --cierres
python3 "$AQUI/montar.py" "$TABLERO/vista.html" "$OUT/publico" "$OUT/publico-lector.html" --lector
if command -v node >/dev/null && node -e "require('playwright')" 2>/dev/null; then
  node "$AQUI/recorrer.js" "$OUT" "$OUT/capturas"
  echo "Capturas en $OUT/capturas"
else
  echo "Sin Node con Playwright: se saltó el recorrido de la página. Las páginas de prueba están en $OUT (publico.html, completo.html)."
fi
