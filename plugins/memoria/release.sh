#!/usr/bin/env bash
# Publica una versión del método: sube el número en los tres sitios donde vive,
# comprueba el contrato, regenera metodo.md y dice qué queda por hacer a mano.
#
#   ./release.sh 1.8.0
set -euo pipefail
VERSION="${1:?Falta la versión, con el formato mayor.menor.parche}"
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "Versión mal formada: $VERSION" >&2; exit 1; }
CONTRATO_VER="${VERSION%.*}"

PLUGIN_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$PLUGIN_DIR/../.." && pwd)"
PLUGIN_JSON="$PLUGIN_DIR/.claude-plugin/plugin.json"
MARKETPLACE="$REPO_DIR/.claude-plugin/marketplace.json"
CONTRATO="$PLUGIN_DIR/skills/convenciones/SKILL.md"
README="$REPO_DIR/README.md"

for f in "$PLUGIN_JSON" "$MARKETPLACE" "$CONTRATO" "$README"; do
  [ -f "$f" ] || { echo "No encuentro $f" >&2; exit 1; }
done

if ! grep -q "Versión del método: \*\*$CONTRATO_VER\*\*" "$CONTRATO"; then
  echo "El contrato no declara la versión $CONTRATO_VER. Corrígelo antes de publicar." >&2
  exit 1
fi

if ! grep -q "^\*\*$CONTRATO_VER\*\*\|^\*\*$VERSION\*\*" "$README"; then
  echo "El README no tiene la entrada de la versión $VERSION en su sección de versiones." >&2
  exit 1
fi

perl -0pi -e "s/(\"version\": *\")[0-9.]+(\")/\${1}$VERSION\${2}/" "$PLUGIN_JSON"
perl -0pi -e "s/(\"version\": *\")[0-9.]+(\")/\${1}$VERSION\${2}/" "$MARKETPLACE"

"$PLUGIN_DIR/build-metodo.sh"

echo
echo "Publicada la versión $VERSION en el repo. Lo que no hace este script:"
echo "  1. Commitear y pushear. El push lo hace una persona desde su máquina."
echo "  2. Copiar metodo.md a la raíz de cada organización que corra el método."
echo "     Compruébalo con:  shasum plugins/memoria/metodo.md <raiz>/metodo.md"
if git -C "$REPO_DIR" diff --name-only HEAD 2>/dev/null | grep -q "skills/convenciones/SKILL.md"; then
  echo "  3. El contrato cambió: pasa verificar.sh por cada raíz antes de darla por al día."
fi
BLOQUE_ACTUAL="$(sed -n '/^Este proyecto trabaja sobre una memoria/,/^Antes de guardar algo/p' "$CONTRATO")"
BLOQUE_PREVIO="$(git -C "$REPO_DIR" show HEAD:plugins/memoria/skills/convenciones/SKILL.md 2>/dev/null | sed -n '/^Este proyecto trabaja sobre una memoria/,/^Antes de guardar algo/p' || true)"
if [ -n "$BLOQUE_PREVIO" ] && [ "$BLOQUE_ACTUAL" != "$BLOQUE_PREVIO" ]; then
  echo "  4. El texto de las instrucciones cambió: TODAS las personas tienen que volver"
  echo "     a pegarlo en su proyecto. Eso no se propaga solo."
fi
