#!/usr/bin/env bash
# Prueba el hook de arranque: emite JSON válido, lleva la versión del plugin y el bloque de instrucciones entero,
# y si el bloque de montaje.md pierde su última línea, lo dice en vez de callar.
# Uso: pruebas/hook/probar_hook.sh
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$AQUI/../../plugins/memoria"
fallos=0
ok() { if [ "$1" = 0 ]; then echo "  bien  $2"; else echo "  FALLA $2"; fallos=$((fallos+1)); fi; }
echo "El hook de arranque"
salida="$(CLAUDE_PLUGIN_ROOT="$PLUGIN" bash "$PLUGIN/hooks/arranque.sh")"
printf '%s' "$salida" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["hookSpecificOutput"]["hookEventName"]=="SessionStart"' 2>/dev/null; ok $? "emite JSON válido de SessionStart"
version="$(sed -n 's/.*"version": *"\([0-9.]*\)".*/\1/p' "$PLUGIN/.claude-plugin/plugin.json" | head -n 1)"
printf '%s' "$salida" | grep -q "Plugin memoria $version\."; ok $? "lleva la versión del plugin ($version)"
printf '%s' "$salida" | grep -q 'Este proyecto trabaja sobre una memoria' && printf '%s' "$salida" | grep -q 'Antes de guardar algo'; ok $? "lleva el bloque de instrucciones entero, de la primera a la última línea"
printf '%s' "$salida" | grep -q 'sin-carpeta.md'; ok $? "nombra el anexo sin-carpeta.md, que existe"; [ -f "$PLUGIN/skills/sesion/sin-carpeta.md" ] || fallos=$((fallos+1))
# copia del plugin con el bloque roto: el hook no inyecta nada, y release.sh lo detecta
tmp="$(mktemp -d)"; mkdir -p "$tmp/repo/plugins" "$tmp/repo/.claude-plugin"
cp -R "$PLUGIN" "$tmp/repo/plugins/memoria"; cp "$AQUI/../../.claude-plugin/marketplace.json" "$tmp/repo/.claude-plugin/"; cp "$AQUI/../../README.md" "$tmp/repo/"
copia="$tmp/repo/plugins/memoria"
sed -i.bak 's/^Antes de guardar algo/Antes de guardar nada/' "$copia/skills/convenciones/montaje.md"
roto="$(CLAUDE_PLUGIN_ROOT="$copia" bash "$copia/hooks/arranque.sh")"
[ -z "$roto" ]; ok $? "con el bloque roto el hook no inyecta nada (y release.sh lo detecta antes de publicar)"
( cd "$copia" && bash release.sh 9.9.9 >/dev/null 2>"$tmp/err" ); grep -q 'no inyecta el bloque' "$tmp/err"; ok $? "release.sh se niega a publicar con el bloque roto"
rm -rf "$tmp"
echo; if [ "$fallos" = 0 ]; then echo "Todo bien."; else echo "$fallos fallo(s)."; exit 1; fi
