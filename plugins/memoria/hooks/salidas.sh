#!/usr/bin/env bash
# Guarda de «Claude outputs» del plugin memoria (hooks PreToolUse y PostToolUse). «Claude outputs» es la carpeta donde
# la app de Claude deja lo que produce sobre una carpeta conectada; no es parte de la memoria, nadie lo encuentra y, en
# una carpeta compartida, la lee todo el equipo.
#
#   PreToolUse (Write, Edit, MultiEdit, NotebookEdit): rechaza escribir en «Claude outputs» de una raíz de memoria (la
#     carpeta con guia.md y metodo.md que la contiene) y dice dónde va; también en $HOME/mnt/outputs cuando es esa
#     misma carpeta. Sacar archivos de ahí («ordena Claude outputs») no pasa por estas herramientas y no se toca.
#   PostToolUse (las mismas y Bash): si desde la herramienta anterior apareció algo nuevo en «Claude outputs» de una
#     raíz bajo $HOME/mnt, se lo dice a Claude para que lo mueva a su proyecto. Lo que escribe un comando no se puede
#     saber antes; se ve después. La primera vez en una conversación mira los últimos diez minutos.
#
# Nunca frena con un error: rechaza con permissionDecision «deny», que Claude lee como motivo y no como fallo, y avisa
# con additionalContext. Sin raíz de memoria, ante cualquier duda o fallo, deja pasar sin decir nada. Sin python ni jq:
# grep, sed y awk, como los otros hooks. Sin consola (Google Drive en Windows) no hay raíz bajo $HOME/mnt y no hace
# nada: queda la apertura, que lista lo suelto.
set -u
HOME="${HOME:-}"
ENTRADA="$(cat 2>/dev/null)" || exit 0
EVENTO="$(printf '%s' "$ENTRADA" | sed -n 's/.*"hook_event_name"[[:space:]]*:[[:space:]]*"\([A-Za-z]*\)".*/\1/p' | head -n 1)"
MARCA='[memoria-salidas]'
DONDE="Guárdalo en su proyecto, en entregables/ o taller/ como borrador, y lo confidencial (contrato, propuesta con precio, currículum, datos de un cliente o de personas) en restringido/; si no está claro de qué proyecto es, pregúntalo. Lo de paso va en el \$HOME de la consola, fuera de mnt/."

json() { # json <evento> <texto>: en PreToolUse, el rechazo con su motivo; en PostToolUse, contexto para Claude
  local j=$2
  j=${j//\\/\\\\}; j=${j//\"/\\\"}; j=${j//$'\n'/\\n}; j=${j//$'\t'/ }
  if [ "$1" = PreToolUse ]; then
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$j"
  else
    printf '{"hookSpecificOutput":{"hookEventName":"%s","additionalContext":"%s"}}\n' "$1" "$j"
  fi
}

# las carpetas «Claude outputs» de las raíces conectadas (el nombre, sin distinguir mayúsculas), y mnt/outputs si es una de ellas
SALIDAS=()
[ -n "$HOME" ] && for g in "$HOME"/mnt/*/guia.md; do
  r="$(dirname "$g")"
  [ -f "$g" ] && [ -f "$r/metodo.md" ] || continue
  for d in "$r"/*/; do
    d="${d%/}"; [ -d "$d" ] || continue
    [ "$(basename "$d" | tr '[:upper:]' '[:lower:]')" = "claude outputs" ] && SALIDAS+=("$d")
  done
done
ENLAZADA=""
if [ -n "$HOME" ] && [ -d "$HOME/mnt/outputs" ]; then
  for d in ${SALIDAS[@]+"${SALIDAS[@]}"}; do [ "$HOME/mnt/outputs" -ef "$d" ] && ENLAZADA=1; done
fi

case "$EVENTO" in
PreToolUse)
  P="$(printf '%s' "$ENTRADA" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)"
  [ -n "$P" ] || P="$(printf '%s' "$ENTRADA" | sed -n 's/.*"notebook_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)"
  [ -n "$P" ] || exit 0
  case "$P" in /*) ;; *) exit 0 ;; esac
  # «…/<raíz>/Claude outputs/…»: la carpeta de antes de ese tramo tiene que ser una raíz de memoria
  PADRE="$(printf '%s' "$P" | awk '{ i = index(tolower($0), "/claude outputs/"); if (i > 1) print substr($0, 1, i - 1) }')"
  EN_SALIDAS=""
  [ -n "$PADRE" ] && [ -f "$PADRE/guia.md" ] && [ -f "$PADRE/metodo.md" ] && EN_SALIDAS=1
  if [ -z "$EN_SALIDAS" ] && [ -n "$ENLAZADA" ]; then
    case "$P" in "$HOME/mnt/outputs/"*) EN_SALIDAS=1 ;; esac
  fi
  [ -n "$EN_SALIDAS" ] || exit 0
  json PreToolUse "$MARCA No se escribe en «Claude outputs»: no es parte de la memoria, nadie lo encuentra y en una carpeta compartida la lee todo el equipo. $DONDE"
  ;;
PostToolUse)
  [ ${#SALIDAS[@]} -gt 0 ] || exit 0
  SID="$(printf '%s' "$ENTRADA" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([A-Za-z0-9_.-]*\)".*/\1/p' | head -n 1)"
  [ -n "$SID" ] || exit 0
  SELLOS="${CLAUDE_PLUGIN_DATA:-${TMPDIR:-/tmp}/memoria-control-$(id -u 2>/dev/null || echo x)}"
  SELLOS="${SELLOS%/}/memoria-salidas"
  SELLO="$SELLOS/$SID"
  NUEVOS=""
  for d in "${SALIDAS[@]}"; do
    if [ -e "$SELLO" ]; then
      n="$(find "$d" -type f -newer "$SELLO" ! -path '*/.*' 2>/dev/null | head -n 20)"
    else
      n="$(find "$d" -type f -mmin -10 ! -path '*/.*' 2>/dev/null | head -n 20)"
    fi
    pre="$(dirname "$d")/"
    while IFS= read -r f; do [ -n "$f" ] && NUEVOS="$NUEVOS${f#"$pre"}"$'\n'; done <<< "$n"
  done
  # el sello marca hasta dónde se miró; si no se puede apuntar, no se avisa (se repetiría)
  mkdir -p "$SELLOS" 2>/dev/null && : > "$SELLO" 2>/dev/null || exit 0
  [ -n "$NUEVOS" ] || exit 0
  LISTA="$(printf '%s' "$NUEVOS" | sed '/^$/d' | head -n 10 | sed 's/^/- /')"
  json PostToolUse "$MARCA Acaba de aparecer en «Claude outputs», que no es parte de la memoria y en una carpeta compartida la lee todo el equipo:
$LISTA
Si lo produjo esta conversación, muévelo ahora a su proyecto, como dice «Ordenar Claude outputs» de la skill donde-va, y sigue: $DONDE Si no lo produjo esta conversación, no lo toques."
  ;;
esac
exit 0
