#!/usr/bin/env bash
# Prueba el control de apertura (hook Stop): no frena nunca sin carpetas conectadas ni ante un error, frena una sola vez
# por conversación si hay carpetas conectadas y la memoria no se abrió, y deja pasar en cuanto hay una apertura.
# Las conversaciones son registros JSONL inventados con la forma de los de Claude.
# Uso: pruebas/hook/probar_control.sh
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
CONTROL="$AQUI/../../plugins/memoria/hooks/control.sh"
fallos=0
ok() { if [ "$1" = 0 ]; then echo "  bien  $2"; else echo "  FALLA $2"; fallos=$((fallos+1)); fi; }
tmp="$(mktemp -d)"; mkdir -p "$tmp/casa-vacia" "$tmp/casa-codigo/mnt/Code" "$tmp/casa-memoria/mnt/Memoria"
touch "$tmp/casa-memoria/mnt/Memoria/guia.md" "$tmp/casa-memoria/mnt/Memoria/metodo.md" "$tmp/casa-codigo/mnt/Code/README.md"
# piezas de conversación
pregunta='{"type":"user","message":{"role":"user","content":[{"type":"text","text":"¿cómo cambio el plugin?"}]}}'
elegidas='{"type":"user","message":{"role":"user","content":[{"type":"text","text":"hola"},{"type":"text","text":"<system-reminder>\nThe user picked these folders on their computer for this task:\n/Users/x/Code\n</system-reminder>"}]}}'
respuesta='{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Respuesta."}]}}'
apertura='{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":"=== METODO (primera línea)\n# Método · versión 1.18.2"}]}}'
aviso='{"type":"user","message":{"role":"user","content":"Stop hook feedback:\n[bash control.sh]: [memoria-apertura] Esta conversación tiene carpetas conectadas…"}}'
escribe_marca='{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","name":"Write","input":{"content":"[memoria-apertura] … Stop hook feedback … === METODO (primera línea)"}}]}}'
conv() { local f="$tmp/$1.jsonl"; shift; printf '%s\n' "$@" > "$f"; echo "$f"; }
corre() { # corre <HOME> <transcript> [stop_hook_active]
  printf '{"session_id":"s","transcript_path":"%s","hook_event_name":"Stop","stop_hook_active":%s}' "$2" "${3:-false}" \
    | HOME="$1" bash "$CONTROL" >/dev/null 2>"$tmp/err"; echo $?; }

echo "El control de apertura"
[ "$(corre "$tmp/casa-vacia" "$(conv a "$pregunta" "$respuesta")")" = 0 ]; ok $? "sin carpetas conectadas no frena (chat suelto, teléfono, web)"
[ "$(corre "$tmp/casa-codigo" "$(conv b "$pregunta" "$respuesta")")" = 0 ]; ok $? "con carpetas en la computadora pero ninguna memoria no frena"
[ "$(corre "$tmp/casa-memoria" "$(conv c "$pregunta" "$respuesta")")" = 2 ]; ok $? "con una memoria conectada y sin apertura frena"
grep -q '\[memoria-apertura\]' "$tmp/err" && grep -q 'apertura mínima' "$tmp/err"; ok $? "y dice qué hacer, con su marca"
[ "$(corre "$tmp/casa-vacia" "$(conv d "$elegidas" "$respuesta")")" = 2 ]; ok $? "en la nube, con carpetas elegidas y sin apertura, frena para comprobarlo"
grep -q 'si ninguna carpeta lo es' "$tmp/err"; ok $? "y deja terminar sin más si ninguna es una memoria"
[ "$(corre "$tmp/casa-memoria" "$(conv e "$pregunta" "$apertura" "$respuesta")")" = 0 ]; ok $? "con una apertura ya hecha no frena"
[ "$(corre "$tmp/casa-memoria" "$(conv f "$pregunta" "$respuesta" "$aviso" "$respuesta")")" = 0 ]; ok $? "frena una sola vez por conversación"
[ "$(corre "$tmp/casa-memoria" "$(conv g "$pregunta" "$escribe_marca" "$respuesta")")" = 2 ]; ok $? "un texto que solo menciona la marca o la cabecera no cuenta como aviso ni como apertura"
[ "$(corre "$tmp/casa-memoria" "$(conv h "$pregunta" "$respuesta")" true)" = 0 ]; ok $? "lo que sigue a su propio aviso no se vuelve a frenar"
[ "$(corre "$tmp/casa-memoria" "$tmp/no-existe.jsonl")" = 0 ]; ok $? "sin registro de la conversación deja pasar"
[ "$(printf 'esto no es JSON' | HOME="$tmp/casa-memoria" bash "$CONTROL" >/dev/null 2>&1; echo $?)" = 0 ]; ok $? "con una entrada rota deja pasar"
rm -rf "$tmp"
echo; if [ "$fallos" = 0 ]; then echo "Todo bien."; else echo "$fallos fallo(s)."; exit 1; fi
