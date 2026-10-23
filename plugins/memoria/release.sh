#!/usr/bin/env bash
# Publica una versión del método: sube el número en los sitios donde vive,
# comprueba el contrato y el README, regenera metodo.md y dice qué queda por hacer a mano.
# Comprueba todo antes de tocar nada, y si algo falla a mitad deja los archivos como estaban.
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
VISTA="$PLUGIN_DIR/skills/tablero/vista.html"
README="$REPO_DIR/README.md"
REL_CONTRATO="plugins/memoria/skills/convenciones"
MONTAJE="$PLUGIN_DIR/skills/convenciones/montaje.md"
REL_MONTAJE="plugins/memoria/skills/convenciones/montaje.md"

for f in "$PLUGIN_JSON" "$MARKETPLACE" "$CONTRATO" "$VISTA" "$README"; do
  [ -f "$f" ] || { echo "No encuentro $f" >&2; exit 1; }
done

# --- comprobaciones, antes de tocar nada ---
ACTUAL="$(sed -n 's/.*"version": *"\([0-9.]*\)".*/\1/p' "$PLUGIN_JSON" | head -n 1)"
mayor() { [ "$1" != "$2" ] && [ "$(printf '%s\n%s\n' "$1" "$2" | sort -t. -k1,1n -k2,2n -k3,3n | tail -n 1)" = "$1" ]; }
if ! mayor "$VERSION" "$ACTUAL"; then
  echo "La versión $VERSION no es mayor que la actual, $ACTUAL." >&2; exit 1
fi
# el hook tiene que inyectar el bloque entero: si montaje.md perdió la última línea del bloque, el hook calla y nadie lo nota
HOOK_SALIDA="$(CLAUDE_PLUGIN_ROOT="$PLUGIN_DIR" bash "$PLUGIN_DIR/hooks/arranque.sh" 2>/dev/null || true)"
if [ -z "$HOOK_SALIDA" ] || ! printf '%s' "$HOOK_SALIDA" | grep -q 'Antes de guardar algo' || ! printf '%s' "$HOOK_SALIDA" | python3 -c 'import json,sys; json.load(sys.stdin)' 2>/dev/null; then
  echo "El hook de arranque no inyecta el bloque de instrucciones (¿cambió la primera o la última línea del bloque en montaje.md?). Corrígelo antes de publicar." >&2; exit 1
fi
# una sola frase para cuándo se pone al día el tablero: si vuelve «al cerrar sesión» a los sitios que la copiaban, se avisa
FRASE_VIEJA="se pone al día (cada vez que|al) (su dueño )?cierr|puesta al d[ií]a al cerrar cada sesi|se regenera cada vez que esa persona cierra|(tablero|p[aá]gina) se pone al d[ií]a sola|al d[ií]a sola al abrir|al abrirlo tras un cierre|abre despu[eé]s de cerrar|lanza al abrirse"
VIEJA="$( { grep -nE "$FRASE_VIEJA" "$PLUGIN_DIR/skills/tablero/SKILL.md" "$PLUGIN_DIR/skills/convenciones/montaje.md" "$PLUGIN_DIR/skills/nuevo/SKILL.md" "$PLUGIN_DIR/skills/tablero/vista.html" "$PLUGIN_DIR/skills/tablero/tarea.md" "$PLUGIN_DIR/skills/tablero/regenerar.md" "$PLUGIN_DIR/skills/sesion/SKILL.md" "$PLUGIN_DIR/skills/sesion/cerrar.md"; sed -n '1,/^## Versiones/p' "$README" | grep -nE "$FRASE_VIEJA" | sed 's/^/README.md:/'; } 2>/dev/null || true)"
if [ -n "$VIEJA" ]; then
  echo "Alguien volvió a escribir que el tablero se pone al día al cerrar sesión; la frase canónica vive en la regla «Se pone al día» de skills/tablero/SKILL.md:" >&2; printf '%s\n' "$VIEJA" >&2; exit 1
fi
if ! grep -q "Versión del método: \*\*$CONTRATO_VER\*\*" "$CONTRATO"; then
  echo "El contrato no declara la versión $CONTRATO_VER. Corrígelo antes de publicar." >&2; exit 1
fi
# la entrada del README tiene que ser de esta versión exacta (o de mayor.menor si es la .0)
VER_RE="${VERSION//./\\.}"; CON_RE="${CONTRATO_VER//./\\.}"
if ! grep -qE "^\*\*${VER_RE}\*\*" "$README" && ! { [ "${VERSION##*.}" = "0" ] && grep -qE "^\*\*${CON_RE}\*\*" "$README"; }; then
  echo "El README no tiene la entrada de la versión $VERSION en su sección de versiones." >&2; exit 1
fi
grep -q 'const VERSION_TABLERO = "' "$VISTA" || { echo "vista.html no tiene la línea VERSION_TABLERO" >&2; exit 1; }
[ -f "$PLUGIN_DIR/build-metodo.sh" ] || { echo "Falta build-metodo.sh" >&2; exit 1; }

# qué cambió desde la publicación anterior (el último commit que tocó plugin.json), contando lo no commiteado
PREV="$(git -C "$REPO_DIR" log -1 --format=%H -- plugins/memoria/.claude-plugin/plugin.json 2>/dev/null || true)"
TABLERO_CAMBIO=""; CONTRATO_CAMBIO=""; BLOQUE_CAMBIO=""
if [ -n "$PREV" ]; then
  DIF="$(git -C "$REPO_DIR" diff "$PREV" -- plugins/memoria/skills/tablero/ | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)' | grep -v 'VERSION_TABLERO' || true)"
  [ -n "$DIF" ] && TABLERO_CAMBIO=1
  git -C "$REPO_DIR" diff --quiet "$PREV" -- "$REL_CONTRATO" || CONTRATO_CAMBIO=1
  bloque() { sed -n '/^Este proyecto trabaja sobre una memoria/,/^Antes de guardar algo/p'; }
  # el bloque vivía en el contrato hasta la 1.12.5 y desde la 1.13 en su anexo montaje.md
  ANTES="$(git -C "$REPO_DIR" show "$PREV:$REL_MONTAJE" 2>/dev/null || git -C "$REPO_DIR" show "$PREV:$REL_CONTRATO/SKILL.md" 2>/dev/null || true)"
  if [ "$(bloque < "$MONTAJE")" != "$(printf '%s\n' "$ANTES" | bloque)" ]; then BLOQUE_CAMBIO=1; fi
fi

# --- cambios, con vuelta atrás si algo falla ---
COPIA="$(mktemp -d)"
for f in "$PLUGIN_JSON" "$MARKETPLACE" "$VISTA" "$PLUGIN_DIR/metodo.md"; do [ -f "$f" ] && cp -p "$f" "$COPIA/$(basename "$f").$(echo "$f" | cksum | cut -d' ' -f1)"; done
restaurar() {
  for f in "$PLUGIN_JSON" "$MARKETPLACE" "$VISTA" "$PLUGIN_DIR/metodo.md"; do
    c="$COPIA/$(basename "$f").$(echo "$f" | cksum | cut -d' ' -f1)"; [ -f "$c" ] && cp -p "$c" "$f"
  done
  echo "Algo falló: los archivos quedaron como estaban." >&2
}
trap 'restaurar' ERR
trap 'rm -rf "$COPIA"' EXIT

perl -0pi -e "s/(\"version\": *\")[0-9.]+(\")/\${1}$VERSION\${2}/" "$PLUGIN_JSON"
perl -0pi -e "s/(\"version\": *\")[0-9.]+(\")/\${1}$VERSION\${2}/" "$MARKETPLACE"
# La página del tablero lleva la misma versión que el plugin: es lo que compara la tarea para republicarla
perl -0pi -e "s/(const VERSION_TABLERO = \")[0-9.]+(\")/\${1}$VERSION\${2}/" "$VISTA"
for f in "$PLUGIN_JSON" "$MARKETPLACE" "$VISTA"; do
  grep -q "$VERSION\"" "$f" || { echo "No se pudo poner la versión en $f" >&2; false; }
done
bash "$PLUGIN_DIR/build-metodo.sh"
trap - ERR

echo
echo "Publicada la versión $VERSION en el repo. Lo que no hace este script:"
echo "  1. Commitear y llevar a main (pull request). La etiqueta v$VERSION la crea sola la acción de GitHub"
echo "     .github/workflows/etiquetar.yml al llegar a main; es de donde las sesiones descargan los scripts del tablero."
echo "     Compruébala después con:  git ls-remote --tags origin v$VERSION"
echo "  2. Copiar metodo.md a cada raíz: se copia sola en la próxima sesión o sincronización de cualquier cuenta con el plugin nuevo."
echo "     Compruébalo con:  head -1 plugins/memoria/metodo.md <raiz>/metodo.md"
[ -n "$TABLERO_CAMBIO" ] && echo "  2b. El tablero cambió: cada tablero republica su página en la siguiente puesta al día (con el botón, con «sincroniza el tablero» o con la tarea diaria); si no, «actualiza el tablero»."
[ -n "$CONTRATO_CAMBIO" ] && echo "  3. El contrato cambió: pasa verificar.sh por cada raíz antes de darla por al día."
[ -n "$BLOQUE_CAMBIO" ] && echo "  4. El bloque de instrucciones cambió. El hook de arranque lo inyecta solo al actualizar el plugin."
exit 0
