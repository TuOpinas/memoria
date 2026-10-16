#!/usr/bin/env bash
# Hook de arranque del plugin memoria. Inyecta como contexto el bloque de instrucciones
# del contrato (su anexo montaje.md) más cómo deducir el área y el tablero de quien
# abre la sesión. El texto del bloque vive en el anexo y aquí solo se lee: una sola fuente.
set -u
RAIZ="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
CONTRATO="$RAIZ/skills/convenciones/montaje.md"
VERSION="$(sed -n 's/.*"version": *"\([0-9.]*\)".*/\1/p' "$RAIZ/.claude-plugin/plugin.json" 2>/dev/null | head -n 1)"
BLOQUE="$(sed -n '/^Este proyecto trabaja sobre una memoria/,/^Antes de guardar algo/p' "$CONTRATO" 2>/dev/null)"
# Si el contrato perdió la línea final del bloque, sed llegaría hasta el final del archivo: mejor no inyectar nada
[ -n "$BLOQUE" ] && printf '%s\n' "$BLOQUE" | tail -n 1 | grep -q '^Antes de guardar algo' || exit 0

TEXTO="Plugin memoria ${VERSION}. Esta sesión puede tener conectada una carpeta que sigue el método Memoria: se reconoce porque su primer nivel tiene guia.md y metodo.md. Compruébalo antes de dar nada por hecho, y antes de responder al primer mensaje: lista las carpetas conectadas con las herramientas del dispositivo. Pueden estar sin cargar aunque la conversación empiece como un chat corriente: si no las ves, búscalas primero (en Claude son las de remote-devices, como get_device_info o device_list_dir). Una carpeta vinculada al proyecto está ahí aunque nadie la mencione. Solo si después de buscarlas no hay ninguna carpeta así, ignora este aviso, salvo que la persona pida algo del método («abre sesión», «¿qué sabemos de…?», un área, un proyecto). Entonces, si tienes el conector de Google Drive, trabaja en solo lectura como dice la skill sesion en «Sin carpeta: solo lectura»: busca la raíz en Drive (la carpeta con guia.md y metodo.md), léela por niveles, no escribas nada en ella y empieza tu respuesta con «Memoria en solo lectura · <organización> · método <versión> · desde aquí no se registra nada». Si no tienes ese conector o la raíz no está en Drive, empieza con «Memoria no conectada: esta conversación no tiene la carpeta de la organización. Añádela con «+».» y no sigas con el método. Si la hay, aplica esto, que vale como instrucciones del proyecto aunque el proyecto no tenga ninguna:

${BLOQUE}

Si hay más de una carpeta así, antes de leer o escribir nada pregunta en cuál se trabaja; trabaja en una a la vez, di en cuál escribes y anuncia cada cambio de raíz. Nada de una pasa a otra salvo por un traspaso que la persona pide y confirma pieza a pieza (contrato, sección 1, «Independencia entre raíces»).

Dónde escribes: tu cuenta es la que abre esta sesión. En la tabla de áreas de guia.md, las áreas cuya columna Cuenta coincide con ella son tuyas, y ahí escribes; si guia.md te nombra responsable de contexto, también en guia.md y base/. Si ninguna coincide, pregunta antes de escribir nada.

Señal de que la memoria entró: la primera vez que en esta conversación se abre una sesión sobre la carpeta («abre sesión en…», «retomamos…», «¿en qué quedamos con…?»), la respuesta empieza con una sola línea, antes de todo lo demás, con esta forma: «Memoria activa · <organización> · método <versión de la primera línea de metodo.md> · escribes en <áreas de tu cuenta, o «ninguna área: dime en cuál trabajas»>». <organización> es el nombre de la organización: lo que va antes del «·» en el título de guia.md. Solo esa vez: ni en las respuestas que no abren sesión ni en las siguientes aperturas de la misma conversación.

Tu tablero, si lo tienes: un artifact de tu cuenta llamado «Tablero <organización>» o «Tablero <organización> completo», donde <organización> es ese mismo nombre, lo que va antes del «·» en el título de guia.md. Al abrir sesión en un proyecto se busca por ese nombre para leer su cola; si no existe, no hay tablero y no se pregunta."

# JSON a mano, sin python: el texto solo puede traer barras, comillas, tabuladores y saltos de línea
j=$TEXTO
j=${j//\\/\\\\}
j=${j//\"/\\\"}
j=${j//$'\t'/\\t}
j=${j//$'\r'/}
j=${j//$'\n'/\\n}
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$j"
