#!/usr/bin/env bash
# Control de apertura del plugin memoria (hook Stop). Al terminar una respuesta, si la conversación tiene conectada
# una carpeta y todavía no se abrió la memoria, le pide a Claude, una sola vez por conversación, que la abra.
#
# No bloquea nunca sin carpetas conectadas, y ante cualquier duda o error deja pasar (sale con 0). Interviene
# (sale con 2 y el aviso en stderr) solo si se cumplen las tres cosas:
#   1. Hay carpetas conectadas: una raíz con guia.md y metodo.md bajo $HOME/mnt (la app de escritorio), o la
#      conversación dice qué carpetas eligió la persona (una sesión en la nube enlazada a su computadora).
#   2. La conversación no tiene ninguna apertura: ningún resultado de herramienta con lo que imprime abrir.py.
#   3. Este control no intervino antes en esta conversación.
# Sin python ni jq: grep y sed, como el hook de arranque.
set -u
ENTRADA="$(cat 2>/dev/null)" || exit 0
# lo que sigue a un aviso de este mismo control no se vuelve a frenar
printf '%s' "$ENTRADA" | grep -Eq '"stop_hook_active"[[:space:]]*:[[:space:]]*true' && exit 0
T="$(printf '%s' "$ENTRADA" | sed -n 's/.*"transcript_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)"
T="${T/#\~/$HOME}"
[ -n "$T" ] && [ -r "$T" ] || exit 0

MARCA='[memoria-apertura]'
# 3. ya intervino en esta conversación
grep -F -- "$MARCA" "$T" | grep -Eq '"content":[[:space:]]*"Stop hook feedback' && exit 0
# 2. ya hubo apertura: un resultado de herramienta con la cabecera que imprime abrir.py
grep -F '"tool_result"' "$T" | grep -Fq '=== METODO (primera l' && exit 0

# 1. hay carpetas conectadas
RAIZ_LOCAL=""
for g in "$HOME"/mnt/*/guia.md; do
  [ -f "$g" ] && [ -f "$(dirname "$g")/metodo.md" ] && { RAIZ_LOCAL=1; break; }
done
ELEGIDAS=""
grep -Fq 'picked these folders on their computer' "$T" && ELEGIDAS=1
[ -n "$RAIZ_LOCAL$ELEGIDAS" ] || exit 0

if [ -n "$RAIZ_LOCAL" ]; then
  QUE="Esta conversación tiene conectada una carpeta de memoria (con guia.md y metodo.md) y todavía no se abrió."
else
  QUE="Esta conversación tiene carpetas conectadas y todavía no se comprobó si alguna es una carpeta de memoria (con guia.md y metodo.md en su primer nivel)."
fi
printf '%s\n' "$MARCA $QUE Antes de terminar, haz la apertura mínima de la skill sesion de memoria (si ninguna carpeta lo es, basta con haberlo comprobado: termina sin decir nada de esto). Si la abres, añade a tu respuesta solo la línea «Memoria activa…» y lo que cambie lo que ya respondiste; si la petición era trabajo de un proyecto, abre también su sesión. Este aviso no se repite en esta conversación." >&2
exit 2
