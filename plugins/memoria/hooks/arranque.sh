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

TEXTO="Plugin memoria ${VERSION}. Si esta conversación tiene conectada una carpeta con guia.md y metodo.md en su primer nivel, es la memoria de una organización que sigue el método Memoria. Compruébalo antes de responder al primer mensaje listando las carpetas conectadas con las herramientas del dispositivo: pueden estar sin cargar aunque la conversación empiece como un chat corriente, así que búscalas (get_device_info, device_list_dir); una carpeta vinculada al proyecto está ahí aunque nadie la mencione. Si no hay ninguna y piden algo del método («abre sesión», «¿qué sabemos de…?», un área, un proyecto), sigue el anexo sin-carpeta.md de la skill sesion; si no piden nada del método, ignora este aviso. Si la hay, esto vale como instrucciones del proyecto:

${BLOQUE}

Con más de una carpeta así, pregunta en cuál se trabaja antes de leer o escribir nada, y no pases nada de una a otra salvo por un traspaso que la persona pide y confirma pieza a pieza. Dónde escribes: en las áreas cuya columna Cuenta en guia.md lleva la cuenta de esta sesión, como dueño o tras «colabora:», en los proyectos cuya línea «Colabora:» la lleva, y en guia.md y base/ si guia.md te nombra responsable de contexto; si ninguna coincide, pregunta antes de escribir. Para abrir o cerrar sesión, consultar, guardar o revisar, usa las skills del plugin memoria: abrir sesión solo lee, y antes de escribir cualquier cosa en la carpeta se carga la skill convenciones."

# JSON a mano, sin python: el texto solo puede traer barras, comillas, tabuladores y saltos de línea
j=$TEXTO
j=${j//\\/\\\\}
j=${j//\"/\\\"}
j=${j//$'\t'/\\t}
j=${j//$'\r'/}
j=${j//$'\n'/\\n}
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$j"
