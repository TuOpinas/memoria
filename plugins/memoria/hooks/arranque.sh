#!/usr/bin/env bash
# Hook de arranque del plugin memoria. Inyecta como contexto el bloque de instrucciones
# del contrato (su anexo montaje.md), cómo reconocer la carpeta, qué hacer con varias y dónde
# escribe la cuenta; lo demás lo dicen las skills. El texto del bloque vive en el anexo y aquí
# solo se lee: una sola fuente.
set -u
RAIZ="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
CONTRATO="$RAIZ/skills/convenciones/montaje.md"
VERSION="$(sed -n 's/.*"version": *"\([0-9.]*\)".*/\1/p' "$RAIZ/.claude-plugin/plugin.json" 2>/dev/null | head -n 1)"
BLOQUE="$(sed -n '/^Este proyecto trabaja sobre una memoria/,/^Antes de guardar algo/p' "$CONTRATO" 2>/dev/null)"
# Si el contrato perdió la línea final del bloque, sed llegaría hasta el final del archivo: mejor no inyectar nada
[ -n "$BLOQUE" ] && printf '%s\n' "$BLOQUE" | tail -n 1 | grep -q '^Antes de guardar algo' || exit 0

TEXTO="Plugin memoria ${VERSION}. Una carpeta conectada con guia.md y metodo.md en su primer nivel es la memoria de una organización que sigue el método Memoria. Si la conversación tiene carpetas conectadas o es de un proyecto de Claude, la primera llamada de tu primera respuesta, sin escribir nada antes, es un solo ToolSearch que carga get_device_info, device_list_dir, device_bash, device_stage_files, device_commit_files, device_request_folder_access, device_request_delete_permission y, si la cuenta tiene tablero, las del tablero (mcp__claude-artifacts__list_artifacts, mcp__claude-artifacts__read_file, mcp__claude-artifacts__db_query, mcp__claude-artifacts__db_get y mcp__claude-artifacts__db_write, o ArtifactData si la sesión tiene las de antes); luego lista las carpetas (una vinculada al proyecto está ahí aunque nadie la nombre). Si hay memoria, haz la apertura mínima de la skill sesion antes de responder, sea cual sea la petición, en cada carpeta de memoria si hay varias; y la sesión completa del proyecto en cuanto la petición sea trabajo de uno aunque no lo nombre (cambiar el código de un repositorio conectado, un problema que alguien reporta, algo para un cliente). La puesta al día programada del tablero no la hace. Sin memoria: si piden algo del método, el anexo sin-carpeta.md de la skill sesion; si no, ignora este aviso. Con memoria, esto vale como instrucciones del proyecto:

${BLOQUE}

Con varias memorias, pregunta en cuál se trabaja antes de escribir o de abrir la sesión de un proyecto, y nada pasa de una a otra sin un traspaso que la persona confirma pieza a pieza. Abrir y cerrar sesión, consultar, guardar y revisar se hacen con las skills del plugin memoria, y antes de escribir en la carpeta se carga el anexo escribir.md de la skill convenciones. Si la consola de la computadora no monta la carpeta (Google Drive en Windows), no pidas acceso otra vez: se trabaja como dice el anexo sin-consola.md de convenciones. En la conversación, cada archivo de la carpeta que nombras va como enlace: [ruta relativa](computer:///<raíz de get_device_info>/<ruta>), con / y los espacios como %20 (en Windows, computer:///C:/Users/…); dentro de la carpeta nunca van rutas absolutas. Al redactar, la primera frase dice el hecho, sin anunciarlo, y sobra toda palabra que se pueda borrar; lo que se firma o se comparte sigue la skill estilo."

# La descarga de la apertura, ya preparada (1.24.7), el único paso del hook con python3: así la apertura no corre en el contenedor el comando que buscaba el
# plugin con find, que el modo Auto de la app frenaba con un permiso. Sin python3 o si preparar.py falla, no se añade nada
# y la skill sesion lo pide con un comando simple.
PREP=""
# python3 -c '' además de command -v: en un Mac sin las herramientas de desarrollo, /usr/bin/python3 existe pero no corre
if command -v python3 >/dev/null 2>&1 && python3 -c '' >/dev/null 2>&1 && [ -f "$RAIZ/preparar.py" ]; then
  # con tope propio, más corto que el del hook (10 s), para que un Python lento nunca se lleve el aviso entero
  T3=""; command -v timeout >/dev/null 2>&1 && T3="timeout 3"
  PREP="$($T3 python3 "$RAIZ/preparar.py" '$HOME/memoria' skills/sesion/abrir.py skills/sesion/cerrar.py 2>/dev/null)" || PREP=""
  printf '%s\n' "$PREP" | grep -q '^DESCARGA ' || PREP=""
  # REINTENTO no viaja: es DESCARGA con main en lugar de v<versión>, y la skill lo arma (la mitad del texto añadido)
  PREP="$(printf '%s\n' "$PREP" | grep -v '^REINTENTO ')"
fi
[ -n "$PREP" ] && TEXTO="${TEXTO}

Para la apertura de la skill sesion (paso 1 de «Qué leo»), ya preparado por este aviso con preparar.py; se usa tal cual, sin calcularlo otra vez en el contenedor:
${PREP}"

# JSON a mano, sin python: el texto solo puede traer barras, comillas, tabuladores y saltos de línea
j=$TEXTO
j=${j//\\/\\\\}
j=${j//\"/\\\"}
j=${j//$'\t'/\\t}
j=${j//$'\r'/}
j=${j//$'\n'/\\n}
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$j"
