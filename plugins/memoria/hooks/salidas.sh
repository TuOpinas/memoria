#!/usr/bin/env bash
# Guarda de «Claude outputs» del plugin memoria (hooks PreToolUse y PostToolUse). «Claude outputs» es la carpeta donde
# la app de Claude deja lo que produce sobre una carpeta conectada; no es parte de la memoria, nadie lo encuentra y, en
# una carpeta compartida, la lee todo el equipo.
#
#   PreToolUse (Write, Edit, MultiEdit, NotebookEdit): rechaza escribir en «Claude outputs» de una raíz de memoria (la
#     carpeta con guia.md y metodo.md que la contiene) y dice dónde va; también en $HOME/mnt/outputs cuando es esa
#     misma carpeta. Sacar archivos de ahí («ordena Claude outputs») no pasa por estas herramientas y no se toca.
#   PostToolUse (Bash): si desde el comando anterior apareció algo nuevo en «Claude outputs» de una raíz bajo
#     $HOME/mnt (creado, o movido o copiado ahí: también por fecha de cambio), se lo dice a Claude para que lo mueva a
#     su proyecto, marcando lo que nombraba el comando. Lo que escribe un comando no se puede saber antes; se ve después.
#     La primera vez en una conversación mira los últimos diez minutos. Las herramientas MCP (device_bash en una sesión
#     en la nube enlazada a la computadora) no pasan por aquí: queda la apertura, que lista lo suelto.
#
# Nunca frena con un error: rechaza con permissionDecision «deny», que Claude lee como motivo y no como fallo, y avisa
# con additionalContext. Sin raíz de memoria, ante cualquier duda o fallo, deja pasar sin decir nada. Sin python ni jq:
# grep, sed y awk, como los otros hooks. Sin consola (Google Drive en Windows) no hay raíz bajo $HOME/mnt y no hace
# nada: queda la apertura, que ahí mira la carpeta con device_list_dir para toda cuenta (skill sesion).
set -u
HOME="${HOME:-}"
ENTRADA="$(cat 2>/dev/null)" || exit 0
EVENTO="$(printf '%s' "$ENTRADA" | sed -n 's/.*"hook_event_name"[[:space:]]*:[[:space:]]*"\([A-Za-z]*\)".*/\1/p' | head -n 1)"
MARCA='[memoria-salidas]'
DONDE="Guárdalo en su proyecto, en entregables/ o taller/ como borrador, y lo confidencial (contrato, propuesta con precio, currículum, datos de un cliente o de personas) en restringido/; si no está claro de qué proyecto es, pregúntalo, y si no es de ningún proyecto y la persona lo quiere para sí, pregúntale dónde lo quiere. Lo de paso va en el \$HOME de la consola, fuera de mnt/."

json() { # json <evento> <texto>: en PreToolUse, el rechazo con su motivo; en PostToolUse, contexto para Claude
  local j
  j="$(printf '%s' "$2" | tr -d '\000-\010\013-\037')"   # sin caracteres de control salvo tabulador y salto
  j=${j//\\/\\\\}; j=${j//\"/\\\"}; j=${j//$'\n'/\\n}; j=${j//$'\t'/ }
  if [ "$1" = PreToolUse ]; then
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$j"
  else
    printf '{"hookSpecificOutput":{"hookEventName":"%s","additionalContext":"%s"}}\n' "$1" "$j"
  fi
}

campo() { # el primer valor de texto de una clave del JSON de entrada
  printf '%s' "$ENTRADA" | grep -o "\"$1\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | head -n 1 | sed 's/.*:[[:space:]]*"\(.*\)"$/\1/'
}

salidas() { # las carpetas «Claude outputs» de las raíces conectadas (el nombre, sin distinguir mayúsculas)
  SALIDAS=()
  [ -n "$HOME" ] || return 0
  local g r d
  for g in "$HOME"/mnt/*/guia.md; do
    r="$(dirname "$g")"
    [ -f "$g" ] && [ -f "$r/metodo.md" ] || continue
    for d in "$r"/*/; do
      d="${d%/}"; [ -d "$d" ] || continue
      [ "$(basename "$d" | tr '[:upper:]' '[:lower:]')" = "claude outputs" ] && SALIDAS+=("$d")
    done
  done
}

enlazada() { # ¿mnt/outputs es una de esas carpetas? El mismo inodo, o, si la app la monta aparte, el mismo contenido no vacío
  [ -n "$HOME" ] && [ -d "$HOME/mnt/outputs" ] || return 1
  local d a b
  a="$(ls -A "$HOME/mnt/outputs" 2>/dev/null)"
  for d in ${SALIDAS[@]+"${SALIDAS[@]}"}; do
    [ "$HOME/mnt/outputs" -ef "$d" ] && return 0
    b="$(ls -A "$d" 2>/dev/null)"
    [ -n "$a" ] && [ "$a" = "$b" ] && return 0
  done
  return 1
}

case "$EVENTO" in
PreToolUse)
  P="$(campo file_path)"
  [ -n "$P" ] || P="$(campo notebook_path)"
  [ -n "$P" ] || exit 0
  case "$P" in /*) ;; *) exit 0 ;; esac
  # «…/<raíz>/Claude outputs/…»: la carpeta de antes de ese tramo tiene que ser una raíz de memoria
  PADRE="$(printf '%s' "$P" | awk '{ i = index(tolower($0), "/claude outputs/"); if (i > 1) print substr($0, 1, i - 1) }')"
  EN_SALIDAS=""
  [ -n "$PADRE" ] && [ -f "$PADRE/guia.md" ] && [ -f "$PADRE/metodo.md" ] && EN_SALIDAS=1
  if [ -z "$EN_SALIDAS" ] && [ -n "$HOME" ]; then
    case "$P" in "$HOME/mnt/outputs/"*) salidas; enlazada && EN_SALIDAS=1 ;; esac
  fi
  [ -n "$EN_SALIDAS" ] || exit 0
  json PreToolUse "$MARCA No se escribe en «Claude outputs»: no es parte de la memoria, nadie lo encuentra y en una carpeta compartida la lee todo el equipo. $DONDE"
  ;;
PostToolUse)
  salidas
  [ ${#SALIDAS[@]} -gt 0 ] || exit 0
  SID="$(campo session_id | tr -cd 'A-Za-z0-9_.-')"
  [ -n "$SID" ] || exit 0
  SELLOS="${CLAUDE_PLUGIN_DATA:-${TMPDIR:-/tmp}/memoria-control-$(id -u 2>/dev/null || echo x)}"
  SELLOS="${SELLOS%/}/memoria-salidas"
  SELLO="$SELLOS/$SID"
  # el sello nuevo se pone antes de mirar, para que nada caiga entre las dos cosas; si no se puede, no se avisa (se repetiría)
  mkdir -p "$SELLOS" 2>/dev/null && : > "$SELLO.$$" 2>/dev/null || exit 0
  COMANDO="$(campo command)"
  NUEVOS=""
  for d in "${SALIDAS[@]}"; do
    # por fecha de cambio también: mv, cp -p o descomprimir conservan la de modificación
    if [ -e "$SELLO" ]; then
      n="$(find "$d" -type f \( -newer "$SELLO" -o -cnewer "$SELLO" \) 2>/dev/null | head -n 40)"
    else
      n="$(find "$d" -type f \( -mmin -10 -o -cmin -10 \) 2>/dev/null | head -n 40)"
    fi
    pre="$(dirname "$d")/"
    while IFS= read -r f; do
      [ -n "$f" ] || continue
      case "${f#"$d"/}" in .*|*/.*) continue ;; esac   # lo oculto (.DS_Store, temporales de Drive) no cuenta
      linea="${f#"$pre"}"
      b="$(basename "$f")"
      [ -n "$COMANDO" ] && case "$COMANDO" in *"$b"*) linea="$linea (nombrado en tu comando)" ;; esac
      NUEVOS="$NUEVOS$linea"$'\n'
    done <<< "$n"
  done
  mv -f "$SELLO.$$" "$SELLO" 2>/dev/null || { rm -f "$SELLO.$$" 2>/dev/null; exit 0; }
  [ -n "$NUEVOS" ] || exit 0
  LISTA="$(printf '%s' "$NUEVOS" | sed '/^$/d' | head -n 10 | sed 's/^/- /')"
  json PostToolUse "$MARCA Acaba de aparecer en «Claude outputs», que no es parte de la memoria y en una carpeta compartida la lee todo el equipo:
$LISTA
Lo que produjo esta conversación (lo nombrado en tu comando, o lo que sabes que hiciste) muévelo ahora a su proyecto, como dice «Ordenar Claude outputs» de la skill donde-va, y sigue: $DONDE Lo demás puede ser de otra conversación o de otra persona: no lo toques; si ya se dijo al abrir, no lo repitas."
  ;;
esac
exit 0
