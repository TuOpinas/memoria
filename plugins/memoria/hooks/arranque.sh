#!/usr/bin/env bash
# Hook de arranque del plugin memoria. Inyecta como contexto el bloque de instrucciones
# del contrato (convenciones, sección 13) más cómo deducir el área y el tablero de quien
# abre la sesión. El texto del bloque vive en el contrato y aquí solo se lee: una sola fuente.
set -u
RAIZ="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
CONTRATO="$RAIZ/skills/convenciones/SKILL.md"
VERSION="$(sed -n 's/.*"version": *"\([0-9.]*\)".*/\1/p' "$RAIZ/.claude-plugin/plugin.json" 2>/dev/null | head -n 1)"
BLOQUE="$(sed -n '/^Este proyecto trabaja sobre una memoria/,/^Antes de guardar algo/p' "$CONTRATO" 2>/dev/null)"
[ -n "$BLOQUE" ] || exit 0

TEXTO="Plugin memoria ${VERSION}. Esta sesión puede tener conectada una carpeta que sigue el método Memoria: se reconoce porque su primer nivel tiene guia.md y metodo.md. Compruébalo con las herramientas de carpetas conectadas antes de dar nada por hecho. Si no hay ninguna carpeta así, ignora este aviso. Si la hay, aplica esto, que vale como instrucciones del proyecto aunque el proyecto no tenga ninguna:

${BLOQUE}

Si hay más de una carpeta así, antes de leer o escribir nada pregunta en cuál se trabaja; trabaja en una a la vez, di en cuál escribes y anuncia cada cambio de raíz. Nada de una pasa a otra salvo por un traspaso que la persona pide y confirma pieza a pieza (contrato, sección 1, «Independencia entre raíces»).

Dónde escribes: tu cuenta es la que abre esta sesión. En la tabla de áreas de guia.md, las áreas cuya columna Cuenta coincide con ella son tuyas, y ahí escribes; si guia.md te nombra responsable de contexto, también en guia.md y base/. Si ninguna coincide, pregunta antes de escribir nada.

Tu tablero, si lo tienes: un artifact de tu cuenta llamado «Tablero <organización>» o «Tablero <organización> completo», donde <organización> es el título de guia.md. Al abrir sesión en un proyecto se busca por ese nombre para leer su cola; si no existe, no hay tablero y no se pregunta."

python3 - "$TEXTO" <<'PY' 2>/dev/null || printf '%s\n' "$TEXTO"
import json, sys
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": sys.argv[1]}}, ensure_ascii=False))
PY
