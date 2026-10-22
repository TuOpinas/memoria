#!/usr/bin/env bash
# Prueba la guarda de «Claude outputs» (hooks PreToolUse y PostToolUse): nunca sale con error; rechaza escribir en
# «Claude outputs» de una raíz de memoria (y en mnt/outputs cuando es esa carpeta) y deja escribir en todo lo demás;
# después de una herramienta avisa de lo nuevo que apareció ahí, una vez por archivo, y calla sin raíz o ante un fallo.
# Uso: pruebas/hook/probar_salidas.sh
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
SALIDAS="$AQUI/../../plugins/memoria/hooks/salidas.sh"
fallos=0
ok() { if [ "$1" = 0 ]; then echo "  bien  $2"; else echo "  FALLA $2"; fallos=$((fallos+1)); fi; }
tmp="$(mktemp -d)"
M="$tmp/casa/mnt/Memoria TuOpinas"; C="$tmp/casa/mnt/Code"
mkdir -p "$M/Claude outputs" "$M/ventas/cuentas/entregables" "$C/Claude outputs" "$tmp/vacia" "$tmp/enlazada/mnt/Memoria" "$tmp/suelta/mnt/Memoria/claude outputs" "$tmp/suelta/mnt/outputs"
touch "$M/guia.md" "$M/metodo.md" "$tmp/enlazada/mnt/Memoria/guia.md" "$tmp/enlazada/mnt/Memoria/metodo.md" "$tmp/suelta/mnt/Memoria/guia.md" "$tmp/suelta/mnt/Memoria/metodo.md"
mkdir -p "$tmp/montada/mnt/Memoria/Claude outputs" "$tmp/montada/mnt/outputs"; touch "$tmp/montada/mnt/Memoria/guia.md" "$tmp/montada/mnt/Memoria/metodo.md" "$tmp/montada/mnt/Memoria/Claude outputs/a.pdf" "$tmp/montada/mnt/outputs/a.pdf"
mkdir -p "$tmp/enlazada/mnt/Memoria/Claude outputs"; ln -s "$tmp/enlazada/mnt/Memoria/Claude outputs" "$tmp/enlazada/mnt/outputs"
corre() { # corre <HOME> <json>
  printf '%s' "$2" | HOME="$1" CLAUDE_PLUGIN_DATA="$tmp/datos" bash "$SALIDAS" >"$tmp/out" 2>"$tmp/err"; echo $? > "$tmp/rc"; }
pre() { corre "$1" "{\"session_id\":\"s1\",\"hook_event_name\":\"PreToolUse\",\"tool_name\":\"$2\",\"tool_input\":{\"$3\":\"$4\",\"content\":\"x\"}}"; }
post() { corre "$1" "{\"session_id\":\"$2\",\"hook_event_name\":\"PostToolUse\",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"${3:-ls}\"},\"tool_response\":{}}"; }
calla() { [ "$(cat "$tmp/rc")" = 0 ] && [ ! -s "$tmp/out" ] && [ ! -s "$tmp/err" ]; }
rechaza() { [ "$(cat "$tmp/rc")" = 0 ] && python3 -c 'import json,sys; d=json.load(open(sys.argv[1]))["hookSpecificOutput"]; assert d["hookEventName"]=="PreToolUse" and d["permissionDecision"]=="deny" and d["permissionDecisionReason"].startswith("[memoria-salidas]")' "$tmp/out" 2>/dev/null; }
avisa() { [ "$(cat "$tmp/rc")" = 0 ] && python3 -c 'import json,sys; d=json.load(open(sys.argv[1]))["hookSpecificOutput"]; assert d["hookEventName"]=="PostToolUse" and d["additionalContext"].startswith("[memoria-salidas]") and sys.argv[2] in d["additionalContext"]' "$tmp/out" "$1" 2>/dev/null; }

echo "Antes de escribir"
pre "$tmp/casa" Write file_path "$M/Claude outputs/propuesta.pdf"; rechaza; ok $? "rechaza escribir en «Claude outputs» de la memoria (ruta con espacios), sin error"
grep -q 'restringido/' "$tmp/out" && grep -q 'fuera de mnt/' "$tmp/out"; ok $? "y dice dónde va, lo confidencial y lo de paso"
pre "$tmp/casa" Edit file_path "$M/claude OUTPUTS/notas.md"; rechaza; ok $? "sin distinguir mayúsculas, también al editar"
pre "$tmp/casa" NotebookEdit notebook_path "$M/Claude outputs/a.ipynb"; rechaza; ok $? "y en un cuaderno"
pre "$tmp/casa" Write file_path "$M/ventas/cuentas/entregables/propuesta.md"; calla; ok $? "deja escribir en un proyecto"
pre "$tmp/casa" Write file_path "$C/Claude outputs/x.py"; calla; ok $? "deja escribir en «Claude outputs» de una carpeta que no es memoria"
pre "$tmp/casa" Write file_path "$tmp/casa/x/Claude outputs/y.md"; calla; ok $? "ni en una ruta cuya carpeta no es una raíz"
pre "$tmp/casa" Write file_path "relativa/Claude outputs/y.md"; calla; ok $? "una ruta relativa no se juzga"
pre "$tmp/enlazada" Write file_path "$tmp/enlazada/mnt/outputs/informe.pdf"; rechaza; ok $? "rechaza mnt/outputs cuando es «Claude outputs» de la memoria"
pre "$tmp/montada" Write file_path "$tmp/montada/mnt/outputs/b.pdf"; rechaza; ok $? "y cuando la app la monta aparte con el mismo contenido"
pre "$tmp/suelta" Write file_path "$tmp/suelta/mnt/outputs/borrador.py"; calla; ok $? "deja mnt/outputs cuando es otra carpeta (lo de paso)"
pre "$tmp/vacia" Write file_path "$M/Claude outputs/x.md"; rechaza; ok $? "la ruta manda aunque la raíz no esté bajo este HOME"
corre "$tmp/casa" '{"hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{}}'; calla; ok $? "sin ruta no dice nada"

echo "Después de una herramienta"
post "$tmp/vacia" p0; calla; ok $? "sin memoria conectada no dice nada"
post "$tmp/casa" p1; calla; ok $? "sin nada nuevo no dice nada"
sleep 1; echo x > "$M/Claude outputs/cv.pdf"; echo y > "$C/Claude outputs/ajeno.txt"
post "$tmp/casa" p1; avisa "Claude outputs/cv.pdf"; ok $? "avisa de lo nuevo en «Claude outputs» de la memoria"
! grep -q 'ajeno.txt' "$tmp/out"; ok $? "y no de lo que aparece en otra carpeta"
grep -q 'no lo toques' "$tmp/out" && grep -q 'pregúntale dónde lo quiere' "$tmp/out"; ok $? "y dice que no toque lo que no produjo esta conversación"
post "$tmp/casa" p1; calla; ok $? "no repite el mismo archivo"
post "$tmp/casa" p2; avisa "cv.pdf"; ok $? "una conversación nueva mira los últimos diez minutos"
# (lo que lleva más de diez minutos ahí no se puede fabricar en una prueba sin cambiar la hora del sistema: lo da la apertura)
touch -t 202601010000 "$M/Claude outputs/viejo.pdf"; post "$tmp/casa" p3; post "$tmp/casa" p3; ! grep -q viejo.pdf "$tmp/out"; ok $? "lo ya avisado en una conversación no vuelve a salir en ella"
touch -t 202601010000 "$tmp/movido.pdf"; sleep 1; mv "$tmp/movido.pdf" "$M/Claude outputs/"; post "$tmp/casa" p1 'mv movido.pdf x'; avisa "movido.pdf (nombrado en tu comando)"; ok $? "avisa de lo movido ahí aunque conserve su fecha, y marca lo que nombraba el comando"
sleep 1; echo r > "$M/Claude outputs/$(printf 'raro\r.pdf')"; post "$tmp/casa" p1; avisa "raro.pdf"; ok $? "un nombre con caracteres de control no rompe el JSON"
mkdir -p "$M/Claude outputs/.oculta"; sleep 1; echo z > "$M/Claude outputs/.DS_Store"; echo z > "$M/Claude outputs/.oculta/a"; post "$tmp/casa" p1; calla; ok $? "lo oculto no cuenta"
sleep 1; echo z > "$tmp/suelta/mnt/Memoria/claude outputs/b.md"; post "$tmp/suelta" s1; avisa "claude outputs/b.md"; ok $? "encuentra la carpeta sin distinguir mayúsculas"
corre "$tmp/casa" '{"hook_event_name":"PostToolUse","tool_name":"Bash"}'; calla; ok $? "sin session_id no dice nada"
printf '{"session_id":"z","hook_event_name":"PostToolUse"}' | HOME="$tmp/casa" CLAUDE_PLUGIN_DATA="/dev/null/no" bash "$SALIDAS" >"$tmp/out" 2>"$tmp/err"; echo $? > "$tmp/rc"; calla; ok $? "si no puede apuntar hasta dónde miró, no avisa (se repetiría)"

echo "Entradas raras"
printf 'esto no es JSON' | HOME="$tmp/casa" bash "$SALIDAS" >"$tmp/out" 2>"$tmp/err"; echo $? > "$tmp/rc"; calla; ok $? "con una entrada rota no dice nada"
printf '{"session_id":"h","hook_event_name":"PostToolUse"}' | env -u HOME bash "$SALIDAS" >"$tmp/out" 2>"$tmp/err"; echo $? > "$tmp/rc"; calla; ok $? "sin HOME no falla"
corre "$tmp/casa" '{"session_id":"s","hook_event_name":"Stop"}'; calla; ok $? "otro evento no dice nada"
rm -rf "$tmp"
echo; if [ "$fallos" = 0 ]; then echo "Todo bien."; else echo "$fallos fallo(s)."; exit 1; fi
