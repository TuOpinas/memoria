#!/usr/bin/env bash
# Genera plugins/memoria/metodo.md a partir de las skills del plugin memoria.
# metodo.md es el contrato legible que se copia a la raíz de cada organización.
# Nadie lo edita a mano: se vuelve a ejecutar este script y se vuelve a copiar.
set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS="$PLUGIN_DIR/skills"
OUT="$PLUGIN_DIR/metodo.md"

# Versión completa para metodo.md; mayor.menor para comprobar el contrato
VERSION="$(sed -n 's/.*"version": *"\([0-9]*\.[0-9]*\.[0-9]*\)".*/\1/p' "$PLUGIN_DIR/.claude-plugin/plugin.json")"
if [ -z "$VERSION" ]; then
  echo "No se pudo leer la versión de plugin.json" >&2
  exit 1
fi
VERSION_CONTRATO="${VERSION%.*}"
if ! grep -q "Versión del método: \*\*$VERSION_CONTRATO\*\*" "$SKILLS/convenciones/SKILL.md"; then
  echo "convenciones/SKILL.md no declara la versión $VERSION_CONTRATO. Corrígelo antes de generar." >&2
  exit 1
fi

# Cuerpo de una skill sin su frontmatter (el bloque entre los dos primeros '---')
cuerpo() {
  awk 'BEGIN{n=0} /^---$/ && n<2 {n++; next} n>=2 {print}' "$1" | sed '1{/^$/d}'
}

# Descripción de una skill, en una línea
descripcion() {
  sed -n 's/^description: *//p' "$1" | head -n 1
}

# Orden del índice: contrato y estilo primero, después el ciclo de trabajo, al final la migración
INDICE="convenciones estilo sesion nuevo entregable revisar donde-va consulta migrar"

{
  echo "# Método de trabajo · versión $VERSION · generado desde el plugin memoria, no se edita a mano"
  echo
  echo "Este archivo reúne el contrato del método, las normas de estilo y el índice de skills del plugin \`memoria\`. Sirve a quien trabaja con Gemini u otro modelo sin el plugin, y a quien abre la carpeta sin IA delante. Para ponerlo al día se vuelve a generar desde el plugin y se copia a la raíz."
  echo
  echo "---"
  echo
  cuerpo "$SKILLS/convenciones/SKILL.md"
  echo
  echo "---"
  echo
  cuerpo "$SKILLS/estilo/SKILL.md"
  echo
  echo "---"
  echo
  echo "# Skills del plugin"
  echo
  echo "Lo que hace cada una, en una línea. Con el plugin instalado se activan solas por las frases que menciona cada descripción."
  echo
  for s in $INDICE; do
    f="$SKILLS/$s/SKILL.md"
    if [ ! -f "$f" ]; then
      echo "Falta la skill $s" >&2
      exit 1
    fi
    echo "- **$s**: $(descripcion "$f")"
  done
} > "$OUT"

echo "Generado $OUT (versión $VERSION, $(wc -l < "$OUT") líneas)"
