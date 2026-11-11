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
printf '%s' "$salida" | grep -q 'Apertura mínima, sin cargar la skill sesion' && printf '%s' "$salida" | grep -q '6\. Si la petición es trabajo de un proyecto'; ok $? "lleva la apertura mínima de minima.md, de la primera a la última línea"
# 1.24.9: la apertura mínima corre abrir.py en el contenedor desde PLUGIN, también sin python3 en el hook, con METODO
printf '%s' "$salida" | grep -q "^PLUGIN $PLUGIN\$\|PLUGIN $PLUGIN\\\\n"; ok $? "lleva PLUGIN, la ruta del plugin instalado"
# sin ninguna raíz en $HOME/mnt (la app de escritorio), una sola línea y sin descarga; con una, el aviso entero
casa="$(mktemp -d)"; mkdir -p "$casa/mnt/Otra"
corto="$(HOME="$casa" CLAUDE_PLUGIN_ROOT="$PLUGIN" bash "$PLUGIN/hooks/arranque.sh")"
printf '%s' "$corto" | python3 -c 'import json,sys; t=json.load(sys.stdin)["hookSpecificOutput"]["additionalContext"]; assert len(t) < 700 and "Ninguna de las carpetas montadas" in t and "minima.md" in t and "\nDESCARGA " not in t' 2>/dev/null; ok $? "con una carpeta montada que no es raíz, una línea corta, sin descarga y con la salida para Drive en Windows"
mkdir -p "$casa/mnt"; rmdir "$casa/mnt/Otra"
vacio="$(HOME="$casa" CLAUDE_PLUGIN_ROOT="$PLUGIN" bash "$PLUGIN/hooks/arranque.sh")"
printf '%s' "$vacio" | grep -q 'Apertura mínima, sin cargar'; ok $? "con \$HOME/mnt vacío (nada montado: Drive en Windows, o la nube) el aviso entero"
mkdir -p "$casa/mnt/Acme"; : > "$casa/mnt/Acme/guia.md"; : > "$casa/mnt/Acme/metodo.md"
largo="$(HOME="$casa" CLAUDE_PLUGIN_ROOT="$PLUGIN" bash "$PLUGIN/hooks/arranque.sh")"
printf '%s' "$largo" | grep -q 'Apertura mínima, sin cargar'; ok $? "con una raíz en \$HOME/mnt, el aviso entero"
rm -rf "$casa"
# 1.25.1: la descarga ya no viaja en el aviso (la skill sesion la calcula al abrir un proyecto); METODO sí, y sin python3 igual
printf '%s' "$salida" | python3 -c 'import json,sys; t=json.load(sys.stdin)["hookSpecificOutput"]["additionalContext"]; assert "\nDESCARGA " not in t and "METODO_DESCARGA" not in t and "\nVERSION " not in t and "\nMETODO # Método de trabajo" in t' 2>/dev/null; ok $? "lleva METODO y no lleva DESCARGA, METODO_DESCARGA ni VERSION"
sinpy="$(mktemp -d)"; for c in bash sed head tail grep printf cat dirname; do p="$(command -v $c)" && ln -s "$p" "$sinpy/$c"; done
nopy="$(PATH="$sinpy" CLAUDE_PLUGIN_ROOT="$PLUGIN" "$(command -v bash)" "$PLUGIN/hooks/arranque.sh")"; rm -rf "$sinpy"
printf '%s' "$nopy" | python3 -c 'import json,sys; t=json.load(sys.stdin)["hookSpecificOutput"]["additionalContext"]; assert "Antes de guardar algo" in t and "\nPLUGIN " in t and "\nMETODO # Método de trabajo" in t' 2>/dev/null; ok $? "sin python3 el aviso sale igual, con PLUGIN y METODO"
# copia del plugin con el bloque roto: el hook no inyecta nada, y release.sh lo detecta
tmp="$(mktemp -d)"; mkdir -p "$tmp/repo/plugins" "$tmp/repo/.claude-plugin"
cp -R "$PLUGIN" "$tmp/repo/plugins/memoria"; cp "$AQUI/../../.claude-plugin/marketplace.json" "$tmp/repo/.claude-plugin/"; cp "$AQUI/../../README.md" "$tmp/repo/"
copia="$tmp/repo/plugins/memoria"
sed -i.bak 's/^Antes de guardar algo/Antes de guardar nada/' "$copia/skills/convenciones/montaje.md"
roto="$(CLAUDE_PLUGIN_ROOT="$copia" bash "$copia/hooks/arranque.sh")"
[ -z "$roto" ]; ok $? "con el bloque roto el hook no inyecta nada (y release.sh lo detecta antes de publicar)"
echo "# informe de prueba" > "$tmp/revision-de-calidad-9-9-9.md"
( cd "$copia" && bash release.sh 9.9.9 --revisada "$tmp/revision-de-calidad-9-9-9.md" >/dev/null 2>"$tmp/err0" ); grep -q 'no tiene su medición completa' "$tmp/err0"; ok $? "release.sh se niega a publicar con un informe sin medición (1.25.8)"
printf '# informe\n\n## Medición\nFecha: 2026-11-08\nTipo: versión · Tamaño: 88 líneas de diff\nModelo: Opus 5.5 (E, R)\nProfundidad: normal · Revisores: 2 · Lentes: E, R\nHallazgos: 3 · impiden 1 · riesgo 1 · mejoran 1\nArreglados: no consta\n\n## Lo que se escapó\nArreglados: 2\n' > "$tmp/revision-de-calidad-9-9-9.md"
( cd "$copia" && bash release.sh 9.9.9 --revisada "$tmp/revision-de-calidad-9-9-9.md" >/dev/null 2>"$tmp/err0b" ); grep -q 'no tiene su medición completa' "$tmp/err0b"; ok $? "ni con los arreglados sin número, aunque otra sección diga un número"
sed -i.bak 's/^Arreglados: no consta$/Arreglados: 2/' "$tmp/revision-de-calidad-9-9-9.md"
( cd "$copia" && bash release.sh 9.9.9 --revisada "$tmp/revision-de-calidad-9-9-9.md" >/dev/null 2>"$tmp/err0c" ); grep -q 'no se puede medir' "$tmp/err0c"; ok $? "ni con hallazgos que la medición no puede contar (1.26.2; los casos, en pruebas/sesion/probar_informe_calidad.py)"
hall='### 1. Uno\nLens: errors, risks · Pesa: impide cumplir el objetivo\n\n### 2. Dos\nLens: risks · Pesa: pone en riesgo el objetivo\n\n### 3. Tres\nLens: efficiency · Pesa: lo mejora\n\n'
{ printf '# informe\n\n'; printf "$hall"; sed -n '/^## Medición/,$p' "$tmp/revision-de-calidad-9-9-9.md" | sed 's/^Arreglados: 2$/Arreglados: 2\nRazonamiento: medio\nTokens: 300k/'; } > "$tmp/r.md"; mv "$tmp/r.md" "$tmp/revision-de-calidad-9-9-9.md"
( cd "$copia" && bash release.sh 9.9.9 --revisada "$tmp/revision-de-calidad-9-9-9.md" >/dev/null 2>"$tmp/err" ); grep -q 'no inyecta el bloque' "$tmp/err"; ok $? "release.sh se niega a publicar con el bloque roto"
( cd "$copia" && bash release.sh 9.9.9 >/dev/null 2>"$tmp/err2" ); grep -q 'Falta la revisión de calidad de la 9.9.9' "$tmp/err2"; ok $? "release.sh se niega a publicar sin el informe de la revisión de calidad (1.22.3)"
( cd "$copia" && bash release.sh 9.9.9 --revisada taller/revision-de-calidad-1-0-0.md >/dev/null 2>"$tmp/err3" ); grep -q 'Falta la revisión de calidad de la 9.9.9' "$tmp/err3"; ok $? "y con el informe de otra versión, tampoco"
( cd "$copia" && bash release.sh 9.9.9 --revisada "$tmp/no-existe/revision-de-calidad-9-9-9.md" >/dev/null 2>"$tmp/err4" ); grep -q 'No encuentro el informe' "$tmp/err4"; ok $? "ni con una ruta que no existe"
echo x > "$tmp/revision-de-calidad-9-9-99.md"; ( cd "$copia" && bash release.sh 9.9.9 --revisada "$tmp/revision-de-calidad-9-9-99.md" >/dev/null 2>"$tmp/err5" ); grep -q 'Falta la revisión de calidad de la 9.9.9' "$tmp/err5"; ok $? "ni con el de una versión que empieza igual"
rm -rf "$tmp"
echo; if [ "$fallos" = 0 ]; then echo "Todo bien."; else echo "$fallos fallo(s)."; exit 1; fi
