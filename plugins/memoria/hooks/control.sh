#!/usr/bin/env bash
# Control de apertura del plugin memoria (hook Stop). Al terminar una respuesta, si la conversación tiene conectada
# una carpeta y todavía no se abrió la memoria, se lo recuerda a Claude, una sola vez por conversación.
#
# Nunca frena con un error: cuando interviene sale con 0 y deja el recordatorio como contexto
# (hookSpecificOutput.additionalContext de Stop, que sigue la conversación sin mostrar un error a la persona).
# No hace nada sin carpetas conectadas, y ante cualquier duda o fallo deja pasar sin decir nada. Interviene solo si:
#   1. Hay una memoria conectada: una raíz con guia.md y metodo.md bajo $HOME/mnt (la app de escritorio); o, en una
#      sesión en la nube enlazada a la computadora, el aviso del sistema que lista las carpetas que eligió la persona
#      y Claude todavía no las miró (get_device_info, device_list_dir): si las miró y no abrió, no hay memoria.
#   2. No hubo apertura: ningún resultado de herramienta que empiece por lo que imprime abrir.py, ni la línea
#      «Memoria activa» en la respuesta que acaba de terminar.
#   3. No es la puesta al día del tablero (una tarea programada que no es una sesión de trabajo).
#   4. Este control no intervino antes en esta conversación: lo apunta en un sello por conversación (session_id),
#      fuera de la carpeta; si no puede apuntarlo, no interviene, para no repetirse.
# Sin python ni jq: grep y sed, como el hook de arranque.
set -u
HOME="${HOME:-}"
ENTRADA="$(cat 2>/dev/null)" || exit 0
# lo que sigue a un recordatorio de este mismo control no se vuelve a mirar
printf '%s' "$ENTRADA" | grep -Eq '"stop_hook_active"[[:space:]]*:[[:space:]]*true' && exit 0
# la respuesta que acaba de terminar ya abrió (el registro puede ir con retraso)
printf '%s' "$ENTRADA" | grep -Fq 'Memoria activa' && exit 0
T="$(printf '%s' "$ENTRADA" | sed -n 's/.*"transcript_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)"
T="${T/#\~/$HOME}"
[ -n "$T" ] && [ -r "$T" ] || exit 0

MARCA='[memoria-apertura]'
# 4. ya intervino en esta conversación
SID="$(printf '%s' "$ENTRADA" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([A-Za-z0-9_.-]*\)".*/\1/p' | head -n 1)"
[ -n "$SID" ] || exit 0
SELLOS="${CLAUDE_PLUGIN_DATA:-${TMPDIR:-/tmp}}/memoria-control"
[ -e "$SELLOS/$SID" ] && exit 0
# 2. ya hubo apertura: un resultado de herramienta que empieza por la cabecera de abrir.py (mostrar su código no cuenta)
grep -Eq '"type":"tool_result","content":("|\[\{"type":"text","text":")=== METODO \(primera l' "$T" && exit 0
# 3. la puesta al día del tablero: su prompt, como mensaje de la persona (en una sesión enlazada a la computadora,
#    la primera línea de usuario es un aviso del sistema, no el prompt)
grep -Eq '"(content|text)":"Pon al día el tablero \(' "$T" && exit 0

# 1. hay carpetas conectadas
RAIZ_LOCAL=""
for g in "$HOME"/mnt/*/guia.md; do
  [ -f "$g" ] && [ -f "$(dirname "$g")/metodo.md" ] && { RAIZ_LOCAL=1; break; }
done
ELEGIDAS=""
grep -Fq '"text":"<system-reminder>\nThe user picked these folders on their computer' "$T" \
  && ! grep -Eq '"type":"tool_use","id":"[^"]*","name":"[^"]*(get_device_info|device_list_dir)"' "$T" && ELEGIDAS=1
[ -n "$RAIZ_LOCAL$ELEGIDAS" ] || exit 0

if [ -n "$RAIZ_LOCAL" ]; then
  QUE="Esta conversación tiene conectada una carpeta de memoria (con guia.md y metodo.md) y todavía no se abrió."
else
  QUE="Esta conversación tiene carpetas conectadas y todavía no se comprobó si alguna es una carpeta de memoria (con guia.md y metodo.md en su primer nivel)."
fi
mkdir -p "$SELLOS" 2>/dev/null && : > "$SELLOS/$SID" 2>/dev/null || exit 0
TEXTO="$MARCA $QUE Haz ahora la apertura mínima de la skill sesion de memoria; si ninguna carpeta lo es, basta con haberlo comprobado y no digas nada de esto. Si la abres, añade a tu respuesta solo la línea «Memoria activa…» y lo que cambie lo que ya respondiste; si la petición era trabajo de un proyecto, abre también su sesión. Este recordatorio no se repite en esta conversación."
j=$TEXTO
j=${j//\\/\\\\}
j=${j//\"/\\\"}
printf '{"hookSpecificOutput":{"hookEventName":"Stop","additionalContext":"%s"}}\n' "$j"
exit 0
