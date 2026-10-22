#!/usr/bin/env bash
# Prueba el control de apertura (hook Stop): nunca sale con error; sin carpetas conectadas, ante un fallo, en la puesta
# al día del tablero o después de una apertura no dice nada; con carpetas conectadas y sin apertura deja un
# recordatorio, una sola vez por conversación. Las conversaciones son registros JSONL inventados con la forma real de
# los de Claude (sin espacios, el aviso de carpetas dentro de un mensaje de usuario, los resultados de herramienta).
# Uso: pruebas/hook/probar_control.sh
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
CONTROL="$AQUI/../../plugins/memoria/hooks/control.sh"
fallos=0
ok() { if [ "$1" = 0 ]; then echo "  bien  $2"; else echo "  FALLA $2"; fallos=$((fallos+1)); fi; }
tmp="$(mktemp -d)"; mkdir -p "$tmp/casa-vacia" "$tmp/casa-codigo/mnt/Code" "$tmp/casa-memoria/mnt/Memoria TuOpinas"
touch "$tmp/casa-memoria/mnt/Memoria TuOpinas/guia.md" "$tmp/casa-memoria/mnt/Memoria TuOpinas/metodo.md" "$tmp/casa-codigo/mnt/Code/README.md"
# piezas de conversación, con la forma de los registros reales
pregunta='{"type":"user","message":{"role":"user","content":[{"type":"text","text":"¿cómo cambio el plugin?"}]}}'
elegidas='{"type":"user","message":{"role":"user","content":[{"type":"text","text":"hola"},{"text":"<system-reminder>\nThe user picked these folders on their computer for this task:\n/Users/x/Code\n</system-reminder>","type":"text"}]}}'
pegada='{"type":"user","message":{"role":"user","content":[{"type":"text","text":"mira este aviso: The user picked these folders on their computer for this task"}]}}'
respuesta='{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Respuesta."}]}}'
apertura_txt='{"type":"user","message":{"role":"user","content":[{"tool_use_id":"t1","type":"tool_result","content":"=== METODO (primera línea)\n# Método · versión 1.18.2"}]}}'
apertura_lista='{"type":"user","message":{"role":"user","content":[{"tool_use_id":"t1","type":"tool_result","content":[{"type":"text","text":"=== METODO (primera línea)\n# Método"}]}]}}'
codigo='{"type":"user","message":{"role":"user","content":[{"tool_use_id":"t2","type":"tool_result","content":"    80\tprint(\"=== METODO (primera línea)\")\n grep -Fq \"The user picked these folders on their computer\" [memoria-apertura]"}]}}'
aviso='{"type":"attachment","attachment":{"type":"hook_additional_context","content":["[memoria-apertura] Esta conversación tiene carpetas conectadas…"]}}'
escribe_marca='{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","name":"Write","input":{"content":"[memoria-apertura] … === METODO (primera línea)"}}]}}'
tarea='{"type":"user","message":{"role":"user","content":"Pon al día el tablero (completo) de la carpeta de memoria de TuOpinas. Trabaja en español."}}'
conv() { local f="$tmp/$1.jsonl"; shift; printf '%s\n' "$@" > "$f"; echo "$f"; }
corre() { # corre <HOME> <transcript> [stop_hook_active] [last_assistant_message]: deja la salida en $tmp/out y el código en $tmp/rc
  printf '{"session_id":"s","transcript_path":"%s","hook_event_name":"Stop","stop_hook_active":%s,"last_assistant_message":"%s"}' "$2" "${3:-false}" "${4:-Respuesta.}" \
    | HOME="$1" bash "$CONTROL" >"$tmp/out" 2>"$tmp/err"; echo $? > "$tmp/rc"; }
calla() { [ "$(cat "$tmp/rc")" = 0 ] && [ ! -s "$tmp/out" ] && [ ! -s "$tmp/err" ]; }
recuerda() { [ "$(cat "$tmp/rc")" = 0 ] && python3 -c 'import json,sys; d=json.load(open(sys.argv[1]))["hookSpecificOutput"]; assert d["hookEventName"]=="Stop" and d["additionalContext"].startswith("[memoria-apertura]")' "$tmp/out" 2>/dev/null; }

echo "El control de apertura"
corre "$tmp/casa-vacia" "$(conv a "$pregunta" "$respuesta")"; calla; ok $? "sin carpetas conectadas no dice nada (chat suelto, teléfono, web)"
corre "$tmp/casa-vacia" "$(conv a2 "$pegada" "$codigo" "$respuesta")"; calla; ok $? "sin carpetas, aunque la conversación pegue o muestre la frase del aviso de carpetas, no dice nada"
corre "$tmp/casa-codigo" "$(conv b "$pregunta" "$respuesta")"; calla; ok $? "con carpetas en la computadora pero ninguna memoria no dice nada"
corre "$tmp/casa-memoria" "$(conv c "$pregunta" "$respuesta")"; recuerda; ok $? "con una memoria conectada (ruta con espacios) y sin apertura deja el recordatorio, sin error"
grep -q 'apertura mínima' "$tmp/out"; ok $? "y dice qué hacer"
corre "$tmp/casa-vacia" "$(conv d "$elegidas" "$respuesta")"; recuerda; ok $? "en la nube, con carpetas elegidas y sin apertura, recuerda comprobarlo"
grep -q 'si ninguna carpeta lo es' "$tmp/out"; ok $? "y deja seguir sin más si ninguna es una memoria"
corre "$tmp/casa-memoria" "$(conv e "$pregunta" "$apertura_txt" "$respuesta")"; calla; ok $? "con una apertura ya hecha no dice nada"
corre "$tmp/casa-memoria" "$(conv e2 "$pregunta" "$apertura_lista" "$respuesta")"; calla; ok $? "también con el resultado en forma de lista"
corre "$tmp/casa-memoria" "$(conv e3 "$pregunta" "$respuesta")" false "Memoria activa · TuOpinas · método 1.18.2"; calla; ok $? "la respuesta que termina ya abrió, aunque el registro vaya con retraso"
corre "$tmp/casa-memoria" "$(conv f "$pregunta" "$respuesta" "$aviso" "$respuesta")"; calla; ok $? "recuerda una sola vez por conversación"
corre "$tmp/casa-memoria" "$(conv g "$pregunta" "$escribe_marca" "$codigo" "$respuesta")"; recuerda; ok $? "mostrar o escribir el código del plugin no cuenta como apertura ni como recordatorio"
corre "$tmp/casa-memoria" "$(conv t "$tarea" "$respuesta")"; calla; ok $? "en la puesta al día del tablero no dice nada"
corre "$tmp/casa-memoria" "$(conv h "$pregunta" "$respuesta")" true; calla; ok $? "lo que sigue a su propio recordatorio no se vuelve a mirar"
corre "$tmp/casa-memoria" "$tmp/no-existe.jsonl"; calla; ok $? "sin registro de la conversación no dice nada"
printf 'esto no es JSON' | HOME="$tmp/casa-memoria" bash "$CONTROL" >"$tmp/out" 2>"$tmp/err"; echo $? > "$tmp/rc"; calla; ok $? "con una entrada rota no dice nada"
rm -rf "$tmp"
echo; if [ "$fallos" = 0 ]; then echo "Todo bien."; else echo "$fallos fallo(s)."; exit 1; fi
