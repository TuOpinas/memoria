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
  # sin retornos de carro: un archivo guardado con finales de Windows perdería su cuerpo entero
  tr -d '\r' < "$1" | awk 'BEGIN{n=0} /^---$/ && n<2 {n++; next} n>=2 {print}' | sed '1{/^$/d;}'
}

# Descripción de una skill, en una línea
descripcion() {
  tr -d '\r' < "$1" | sed -n 's/^description: *//p' | head -n 1
}

# Orden del índice: contrato y estilo primero, después el ciclo de trabajo, al final la migración
INDICE="convenciones estilo sesion nuevo entregable revisar donde-va consulta tablero migrar director calidad"

# El cuerpo se genera aparte para sacarle una huella: la primera línea lleva versión y huella,
# así que cualquier cambio de texto cambia esa línea aunque el número sea el mismo.
CUERPO="$(mktemp)"
trap 'rm -f "$CUERPO"' EXIT
{
  echo "Este archivo reúne el contrato del método, las normas de estilo y el índice de skills del plugin \`memoria\`. Sirve a quien trabaja con Gemini u otro modelo sin el plugin, y a quien abre la carpeta sin IA delante. Para ponerlo al día se vuelve a generar desde el plugin y se copia a la raíz."
  echo
  echo "---"
  echo
  for s in convenciones estilo; do
    if [ "$(cuerpo "$SKILLS/$s/SKILL.md" | wc -l)" -lt 5 ]; then
      echo "La skill $s sale vacía: revisa su cabecera" >&2; exit 1
    fi
  done
  cuerpo "$SKILLS/convenciones/SKILL.md"
  # los dos anexos del contrato, que el plugin lee a demanda, van enteros: metodo.md es para quien no tiene el plugin
  for anexo in raices montaje; do
    [ -f "$SKILLS/convenciones/$anexo.md" ] || { echo "Falta el anexo $anexo.md del contrato" >&2; exit 1; }
    echo
    tr -d '\r' < "$SKILLS/convenciones/$anexo.md" | sed 's/^## /### /; s/^# /## Anexo: /'
  done
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
  # quien trabaja sin el plugin no tiene las skills: los procedimientos que escriben en la carpeta van aquí enteros
  echo
  echo "---"
  echo
  echo "# Procedimientos sin plugin"
  echo
  echo 'Cerrar una sesión, registrar una premisa y publicar un documento, tal como los sigue Claude con el plugin. Donde se nombra una herramienta que no tienes (`abrir.py`, `device_bash`, `ArtifactData`, el tablero), haz lo mismo a mano o sáltalo. Lo que no se salta: los registros solo crecen, nada se registra sin el sí de quien decide, y nadie escribe fuera de su área.'
  for anexo in cerrar premisas; do
    [ -f "$SKILLS/sesion/$anexo.md" ] || { echo "Falta el anexo $anexo.md de sesion" >&2; exit 1; }
    echo
    tr -d '\r' < "$SKILLS/sesion/$anexo.md" | sed 's/^## /### /; s/^# /## /'
  done
  echo
  echo "## Publicar un documento: los requisitos"
  echo
  tr -d '\r' < "$SKILLS/revisar/SKILL.md" | awk '/^## Requisitos/{f=1; next} /^## /{f=0} f'
} > "$CUERPO"
HUELLA="$({ shasum -a 256 2>/dev/null || sha256sum; } < "$CUERPO" | cut -c1-7)"
[ ${#HUELLA} -eq 7 ] || { echo "No se pudo calcular la huella" >&2; exit 1; }
{
  echo "# Método de trabajo · versión $VERSION · huella $HUELLA · generado desde el plugin memoria, no se edita a mano"
  echo
  cat "$CUERPO"
} > "$OUT"

echo "Generado $OUT (versión $VERSION, huella $HUELLA, $(wc -l < "$OUT") líneas)"
