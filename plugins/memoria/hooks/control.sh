#!/usr/bin/env bash
# Control de apertura del plugin memoria (hook Stop). Al terminar una respuesta, si la conversación tiene conectada
# una carpeta y todavía no se abrió la memoria, se lo recuerda a Claude, una sola vez por conversación.
#
# Nunca frena con un error: cuando interviene sale con 0 y deja el recordatorio como contexto
# (hookSpecificOutput.additionalContext de Stop, que sigue la conversación sin mostrar un error a la persona).
# No hace nada sin carpetas conectadas, y ante cualquier duda o fallo deja pasar sin decir nada. Interviene solo si:
#   1. Hay carpetas conectadas: una raíz con guia.md y metodo.md bajo $HOME/mnt (la app de escritorio), o el aviso
#      del sistema que lista las carpetas que eligió la persona (una sesión en la nube enlazada a su computadora).
#   2. No hubo apertura: ningún resultado de herramienta que empiece por lo que imprime abrir.py, ni la línea
#      «Memoria activa» en la respuesta que acaba de terminar.
#   3. No es la puesta al día del tablero (una tarea programada que no es una sesión de trabajo).
#   4. Este control no intervino antes en esta conversación.
# Sin python ni jq: grep y sed, como el hook de arranque.
set -u
ENTRADA="$(cat 2>/dev/null)" || exit 0
# lo que sigue a un recordatorio de este mismo control no se vuelve a mirar
printf '%s' "$ENTRADA" | grep -Eq '"stop_hook_active"[[:space:]]*:[[:space:]]*true' && exit 0
# la respuesta que acaba de terminar ya abrió (el registro puede ir con retraso)
printf '%s' "$ENTRADA" | grep -Fq 'Memoria activa' && exit 0
T="$(printf '%s' "$ENTRADA" | sed -n 's/.*"transcript_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)"
T="${T/#\~/$HOME}"
[ -n "$T" ] && [ -r "$T" ] || exit 0

MARCA='[memoria-apertura]'
# 4. ya intervino: la marca en una línea que no es de Claude ni el resultado de una herramienta (leer este archivo
#    o pegar la marca no cuenta como su recordatorio; si alguien la pega, como mucho deja de intervenir: falla abierto)
grep -F -- "$MARCA" "$T" | grep -v '"type":"assistant"' | grep -vq '"tool_result"' && exit 0
# 2. ya hubo apertura: un resultado de herramienta que empieza por la cabecera de abrir.py (mostrar su código no cuenta)
grep -Eq '"type":"tool_result","content":("|\[\{"type":"text","text":")=== METODO \(primera l' "$T" && exit 0
# 3. la puesta al día del tablero
grep -m 1 '"type":"user"' "$T" | grep -Fq 'Pon al día el tablero (' && exit 0

# 1. hay carpetas conectadas
RAIZ_LOCAL=""
for g in "$HOME"/mnt/*/guia.md; do
  [ -f "$g" ] && [ -f "$(dirname "$g")/metodo.md" ] && { RAIZ_LOCAL=1; break; }
done
ELEGIDAS=""
grep -Fq '"text":"<system-reminder>\nThe user picked these folders on their computer' "$T" && ELEGIDAS=1
[ -n "$RAIZ_LOCAL$ELEGIDAS" ] || exit 0

if [ -n "$RAIZ_LOCAL" ]; then
  QUE="Esta conversación tiene conectada una carpeta de memoria (con guia.md y metodo.md) y todavía no se abrió."
else
  QUE="Esta conversación tiene carpetas conectadas y todavía no se comprobó si alguna es una carpeta de memoria (con guia.md y metodo.md en su primer nivel)."
fi
TEXTO="$MARCA $QUE Haz ahora la apertura mínima de la skill sesion de memoria; si ninguna carpeta lo es, basta con haberlo comprobado y no digas nada de esto. Si la abres, añade a tu respuesta solo la línea «Memoria activa…» y lo que cambie lo que ya respondiste; si la petición era trabajo de un proyecto, abre también su sesión. Este recordatorio no se repite en esta conversación."
j=$TEXTO
j=${j//\\/\\\\}
j=${j//\"/\\\"}
printf '{"hookSpecificOutput":{"hookEventName":"Stop","additionalContext":"%s"}}\n' "$j"
exit 0
