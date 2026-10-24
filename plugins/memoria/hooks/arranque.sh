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

TEXTO="Plugin memoria ${VERSION}. Una carpeta conectada con guia.md y metodo.md en su primer nivel es la memoria de una organización que sigue el método Memoria. Si la conversación tiene carpetas conectadas o es de un proyecto de Claude, la primera llamada de tu primera respuesta, sin escribir nada antes, es un solo ToolSearch que carga get_device_info, device_list_dir, device_bash, device_stage_files, device_commit_files, device_request_folder_access, device_request_delete_permission y, si la cuenta tiene tablero, ArtifactData; luego lista las carpetas (una vinculada al proyecto está ahí aunque nadie la nombre). Si hay memoria, haz la apertura mínima de la skill sesion antes de responder, sea cual sea la petición, en cada carpeta de memoria si hay varias; y la sesión completa del proyecto en cuanto la petición sea trabajo de uno aunque no lo nombre (cambiar el código de un repositorio conectado, un problema que alguien reporta, algo para un cliente). La puesta al día programada del tablero no la hace. Sin memoria: si piden algo del método, el anexo sin-carpeta.md de la skill sesion; si no, ignora este aviso. Con memoria, esto vale como instrucciones del proyecto:

${BLOQUE}

Con varias memorias, pregunta en cuál se trabaja antes de escribir o de abrir la sesión de un proyecto, y nada pasa de una a otra sin un traspaso que la persona confirma pieza a pieza. Abrir y cerrar sesión, consultar, guardar y revisar se hacen con las skills del plugin memoria, y antes de escribir en la carpeta se carga el anexo escribir.md de la skill convenciones. Si la consola de la computadora no monta la carpeta (Google Drive en Windows), no pidas acceso otra vez: se trabaja como dice el anexo sin-consola.md de convenciones. En la conversación, cada archivo de la carpeta que nombras va como enlace: [ruta relativa](computer:///<raíz de get_device_info>/<ruta>), con / y los espacios como %20 (en Windows, computer:///C:/Users/…); dentro de la carpeta nunca van rutas absolutas. Al redactar, la primera frase dice el hecho, sin anunciarlo, y sobra toda palabra que se pueda borrar; lo que se firma o se comparte sigue la skill estilo."

# JSON a mano, sin python: el texto solo puede traer barras, comillas, tabuladores y saltos de línea
j=$TEXTO
j=${j//\\/\\\\}
j=${j//\"/\\\"}
j=${j//$'\t'/\\t}
j=${j//$'\r'/}
j=${j//$'\n'/\\n}
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$j"
