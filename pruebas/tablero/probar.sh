#!/usr/bin/env bash
# Prueba el tablero contra la raíz inventada de raiz/. No toca ninguna raíz real ni nada de lo que se instala.
# 1. Genera los datos y comprueba fugas, plazos, entregables y decisiones (solo Python).
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
python3 "$TABLERO/generar_vista.py" "$OUT/raiz" "$OUT/completo" --version "${VERSION:-prueba}" >/dev/null
# una tarea montada antes de la 1.18 pasa --modo publico: sale lo mismo, el tablero de un solo modo
python3 "$TABLERO/generar_vista.py" "$OUT/raiz" "$OUT/viejo" --modo publico --version "${VERSION:-prueba}" >/dev/null
# un tablero que era público, al ponerse al día con la 1.18: lo dice una semana en Inicio
mkdir -p "$OUT/base-publica/meta"; printf '%s' '{"id":"estado","data":{"modo":"publico","organizacion":"Prueba"},"version":3}' > "$OUT/base-publica/meta/estado.json"
python3 "$TABLERO/generar_vista.py" "$OUT/raiz" "$OUT/migrado" --previos "$OUT/base-publica" --version "${VERSION:-prueba}" >/dev/null
python3 "$AQUI/comprobar.py" "$OUT/completo" "$OUT/viejo" "$OUT/migrado"
# con la cuenta que genera el tablero: un área o un proyecto restringido que es suyo y falta en la computadora no le
# dice «pídeselo a ti»: sale «sin carpeta»
python3 "$TABLERO/generar_vista.py" "$OUT/raiz" "$OUT/beto" --cuenta beto@ejemplo.test --version "${VERSION:-prueba}" >/dev/null
python3 "$TABLERO/generar_vista.py" "$OUT/raiz" "$OUT/ana" --cuenta ana@ejemplo.test --version "${VERSION:-prueba}" >/dev/null
python3 "$TABLERO/generar_vista.py" "$OUT/raiz" "$OUT/eva" --cuenta eva@ejemplo.test --version "${VERSION:-prueba}" >/dev/null
python3 "$TABLERO/generar_vista.py" "$OUT/raiz" "$OUT/carla" --cuenta carla@ejemplo.test --version "${VERSION:-prueba}" >/dev/null
python3 - "$OUT" <<'PY2'
import json, sys, os
m = lambda d, c, i: json.load(open(os.path.join(sys.argv[1], d, c, i + ".json"), encoding="utf-8")).get("motivo")
casos = [(m("beto", "areas", "legal") == "sin-carpeta", "un área restringida de la cuenta que genera el tablero, sin carpeta, sale «sin carpeta»"),
         (m("beto", "proyectos", "ventas--ronda") == "restringido", "un proyecto restringido de un área ajena sigue restringido"),
         (m("ana", "proyectos", "ventas--ronda") == "sin-carpeta", "un proyecto restringido del área de la cuenta (dueña), sin carpeta, sale «sin carpeta»"),
         (m("ana", "areas", "legal") == "restringido", "un área restringida ajena sigue restringida"),
         (m("eva", "areas", "legal") == "sin-carpeta", "quien colabora en un área restringida sin carpeta la ve «sin carpeta»"),
         (m("eva", "proyectos", "ventas--ronda") == "restringido", "un proyecto restringido de un área ajena sigue restringido para quien colabora en otra"),
         (m("carla", "proyectos", "ventas--ronda") == "restringido", "un proyecto restringido del área donde la cuenta solo colabora sigue restringido: lo restringido de dentro es del dueño")]
for c, q in casos: print(("  bien  " if c else "  FALLA ") + q)
sys.exit(0 if all(c for c, _ in casos) else 1)
PY2
# los textos de la página para lo que no se lee, con celdas reales
node "$AQUI/textos.js" "$TABLERO/vista.html"
python3 "$AQUI/paridad.py" "$TABLERO/../.."
# una tarea sin horario: el tablero lo sabe, para no esperar que se ponga al día cada mañana
python3 "$TABLERO/generar_vista.py" "$OUT/raiz" "$OUT/manual" --tarea trig_prueba --manual --version "${VERSION:-prueba}" >/dev/null
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
python3 "$AQUI/../sesion/probar_cuentas.py"
# sin consola en la computadora: la copia de la raíz en el contenedor (espejo.py) y los scripts sin fechas de archivo
python3 "$AQUI/../sesion/probar_espejo.py"
# verificar.sh: el dueño de area.md por su nombre, y las copias en conflicto de Drive
python3 "$AQUI/../verificar/probar_verificar.py"
python3 "$AQUI/../sesion/probar_preparar.py"
# el hook de arranque: JSON válido, versión, bloque entero, y que release.sh pare si el bloque se rompe
bash "$AQUI/../hook/probar_hook.sh"
bash "$AQUI/../hook/probar_control.sh"
python3 "$AQUI/montar.py" "$TABLERO/vista.html" "$OUT/completo" "$OUT/completo.html"
python3 "$AQUI/montar.py" "$TABLERO/vista.html" "$OUT/completo" "$OUT/completo-cierres.html" --cierres
python3 "$AQUI/montar.py" "$TABLERO/vista.html" "$OUT/migrado" "$OUT/migrado.html"
if command -v node >/dev/null && node -e "require('playwright')" 2>/dev/null; then
  node "$AQUI/recorrer.js" "$OUT" "$OUT/capturas"
  echo "Capturas en $OUT/capturas"
else
  echo "Sin Node con Playwright: se saltó el recorrido de la página. Las páginas de prueba están en $OUT (completo.html)."
fi
