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
# 1.24.8: la apertura mínima viaja en el aviso, entera, desde su anexo (la conversación no carga la skill para ella)
printf '%s' "$salida" | grep -q 'Apertura mínima, sin cargar la skill sesion' && printf '%s' "$salida" | grep -q '4\. Si la petición es trabajo de un proyecto'; ok $? "lleva la apertura mínima de minima.md, de la primera a la última línea"
# sin ninguna raíz en $HOME/mnt (la app de escritorio), una sola línea y sin descarga; con una, el aviso entero
casa="$(mktemp -d)"; mkdir -p "$casa/mnt/Otra"
corto="$(HOME="$casa" CLAUDE_PLUGIN_ROOT="$PLUGIN" bash "$PLUGIN/hooks/arranque.sh")"
printf '%s' "$corto" | python3 -c 'import json,sys; t=json.load(sys.stdin)["hookSpecificOutput"]["additionalContext"]; assert len(t) < 600 and "Ninguna carpeta conectada" in t and "\nDESCARGA " not in t' 2>/dev/null; ok $? "sin raíz en \$HOME/mnt, una línea corta y sin descarga"
mkdir -p "$casa/mnt/Acme"; : > "$casa/mnt/Acme/guia.md"; : > "$casa/mnt/Acme/metodo.md"
largo="$(HOME="$casa" CLAUDE_PLUGIN_ROOT="$PLUGIN" bash "$PLUGIN/hooks/arranque.sh")"
printf '%s' "$largo" | grep -q 'Apertura mínima, sin cargar'; ok $? "con una raíz en \$HOME/mnt, el aviso entero"
rm -rf "$casa"
# 1.24.7: la descarga de la apertura viene hecha, la misma que imprime preparar.py; sin python3, el aviso sale igual sin ella
esperada="$(python3 "$PLUGIN/preparar.py" '$HOME/memoria' skills/sesion/abrir.py skills/sesion/cerrar.py | grep -v '^REINTENTO ')"
printf '%s' "$salida" | python3 -c 'import json,sys; t=json.load(sys.stdin)["hookSpecificOutput"]["additionalContext"]; e=sys.argv[1]; assert e.count("\n")==2 and "REINTENTO" not in t and t.endswith("\n"+e)' "$esperada" 2>/dev/null; ok $? "termina con VERSION, METODO y DESCARGA de la apertura, iguales a los de preparar.py (sin REINTENTO, que la skill arma)"
sinpy="$(mktemp -d)"; for c in bash sed head tail grep printf cat dirname; do p="$(command -v $c)" && ln -s "$p" "$sinpy/$c"; done
nopy="$(PATH="$sinpy" CLAUDE_PLUGIN_ROOT="$PLUGIN" "$(command -v bash)" "$PLUGIN/hooks/arranque.sh")"; rm -rf "$sinpy"
printf '%s' "$nopy" | python3 -c 'import json,sys; t=json.load(sys.stdin)["hookSpecificOutput"]["additionalContext"]; assert "Antes de guardar algo" in t and "\nDESCARGA " not in t' 2>/dev/null; ok $? "sin python3 el aviso sale entero, sin la descarga"
# copia del plugin con el bloque roto: el hook no inyecta nada, y release.sh lo detecta
tmp="$(mktemp -d)"; mkdir -p "$tmp/repo/plugins" "$tmp/repo/.claude-plugin"
cp -R "$PLUGIN" "$tmp/repo/plugins/memoria"; cp "$AQUI/../../.claude-plugin/marketplace.json" "$tmp/repo/.claude-plugin/"; cp "$AQUI/../../README.md" "$tmp/repo/"
copia="$tmp/repo/plugins/memoria"
sed -i.bak 's/^Antes de guardar algo/Antes de guardar nada/' "$copia/skills/convenciones/montaje.md"
roto="$(CLAUDE_PLUGIN_ROOT="$copia" bash "$copia/hooks/arranque.sh")"
[ -z "$roto" ]; ok $? "con el bloque roto el hook no inyecta nada (y release.sh lo detecta antes de publicar)"
echo "# informe de prueba" > "$tmp/revision-de-calidad-9-9-9.md"
( cd "$copia" && bash release.sh 9.9.9 --revisada "$tmp/revision-de-calidad-9-9-9.md" >/dev/null 2>"$tmp/err" ); grep -q 'no inyecta el bloque' "$tmp/err"; ok $? "release.sh se niega a publicar con el bloque roto"
( cd "$copia" && bash release.sh 9.9.9 >/dev/null 2>"$tmp/err2" ); grep -q 'Falta la revisión de calidad de la 9.9.9' "$tmp/err2"; ok $? "release.sh se niega a publicar sin el informe de la revisión de calidad (1.22.3)"
( cd "$copia" && bash release.sh 9.9.9 --revisada taller/revision-de-calidad-1-0-0.md >/dev/null 2>"$tmp/err3" ); grep -q 'Falta la revisión de calidad de la 9.9.9' "$tmp/err3"; ok $? "y con el informe de otra versión, tampoco"
( cd "$copia" && bash release.sh 9.9.9 --revisada "$tmp/no-existe/revision-de-calidad-9-9-9.md" >/dev/null 2>"$tmp/err4" ); grep -q 'No encuentro el informe' "$tmp/err4"; ok $? "ni con una ruta que no existe"
echo x > "$tmp/revision-de-calidad-9-9-99.md"; ( cd "$copia" && bash release.sh 9.9.9 --revisada "$tmp/revision-de-calidad-9-9-99.md" >/dev/null 2>"$tmp/err5" ); grep -q 'Falta la revisión de calidad de la 9.9.9' "$tmp/err5"; ok $? "ni con el de una versión que empieza igual"
rm -rf "$tmp"
echo; if [ "$fallos" = 0 ]; then echo "Todo bien."; else echo "$fallos fallo(s)."; exit 1; fi
