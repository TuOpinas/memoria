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

# La apertura mínima vive en su anexo de la skill sesion (1.24.8): se inyecta aquí para que la conversación no tenga que
# cargar la skill entera solo para abrir. Igual que el bloque: si perdió su última línea, no se inyecta nada.
MINIMA="$(sed -n '/^Apertura mínima, sin cargar la skill sesion/,/^6\. Si la petición es trabajo de un proyecto/p' "$RAIZ/skills/sesion/minima.md" 2>/dev/null)"
printf '%s\n' "$MINIMA" | tail -n 1 | grep -q '^6\. Si la petición' || exit 0

# En la app de escritorio las carpetas conectadas están montadas en $HOME/mnt: si hay alguna montada y ninguna es una raíz,
# basta una línea (1.24.8). Sin nada montado no se sabe (la nube enlazada a la computadora no monta nada aquí, y Google
# Drive en Windows no se monta aunque esté conectado): va el aviso entero.
HAY_RAIZ=""
if [ -n "${HOME:-}" ] && [ -d "$HOME/mnt" ]; then
  for d in "$HOME"/mnt/*/; do
    [ -d "$d" ] || continue
    HAY_RAIZ=no
    [ -f "$d/guia.md" ] && [ -f "$d/metodo.md" ] && { HAY_RAIZ=1; break; }
  done
fi

if [ "$HAY_RAIZ" = no ]; then
  TEXTO="Plugin memoria ${VERSION}. Ninguna de las carpetas montadas en esta consola es una memoria (con guia.md y metodo.md en su primer nivel). Si get_device_info lista una carpeta conectada que no está en \$HOME/mnt (Google Drive en Windows), o se conecta una memoria más tarde, carga la skill sesion de memoria y sigue su «Apertura mínima» (su anexo minima.md). Si piden algo del método sin carpeta, su anexo sin-carpeta.md. Si no, ignora este aviso."
else
TEXTO="Plugin memoria ${VERSION}. Una carpeta conectada con guia.md y metodo.md en su primer nivel es la memoria de una organización que sigue el método Memoria. Si la conversación tiene carpetas conectadas o es de un proyecto de Claude, la primera llamada de tu primera respuesta, sin escribir nada antes, es la del paso 1 de abajo. Sin memoria: si piden algo del método, el anexo sin-carpeta.md de la skill sesion; si no, ignora este aviso.

${MINIMA}

Con memoria, esto vale como instrucciones del proyecto:

${BLOQUE}

Con varias memorias, la apertura mínima se hace en cada una; antes de escribir o de abrir la sesión de un proyecto se pregunta en cuál se trabaja, y nada pasa de una a otra sin un traspaso que la persona confirma pieza a pieza. Abrir y cerrar sesión, consultar, guardar y revisar se hacen con las skills del plugin memoria, y antes de escribir en la carpeta se carga el anexo escribir.md de la skill convenciones. Si la consola de la computadora no monta la carpeta (Google Drive en Windows), no pidas acceso otra vez: se trabaja como dice el anexo sin-consola.md de convenciones. En la conversación, cada archivo de la carpeta que nombras va como enlace: [ruta relativa](computer:///<raíz de get_device_info>/<ruta>), con / y los espacios como %20 (en Windows, computer:///C:/Users/…); dentro de la carpeta nunca van rutas absolutas. Al redactar, la primera frase dice el hecho, sin anunciarlo, y sobra toda palabra que se pueda borrar; lo que se firma o se comparte sigue la skill estilo."
fi

# La descarga de la apertura, ya preparada (1.24.7), el único paso del hook con python3: así la apertura no corre en el contenedor el comando que buscaba el
# plugin con find, que el modo Auto de la app frenaba con un permiso. Sin python3 o si preparar.py falla, no se añade nada
# y la skill sesion lo pide con un comando simple.
PREP=""
# python3 -c '' además de command -v: en un Mac sin las herramientas de desarrollo, /usr/bin/python3 existe pero no corre
if [ "$HAY_RAIZ" != no ] && command -v python3 >/dev/null 2>&1 && python3 -c '' >/dev/null 2>&1 && [ -f "$RAIZ/preparar.py" ]; then
  # con tope propio, más corto que el del hook (10 s), para que un Python lento nunca se lleve el aviso entero
  T3=""; command -v timeout >/dev/null 2>&1 && T3="timeout 3"
  PREP="$($T3 python3 "$RAIZ/preparar.py" '$HOME/memoria' skills/sesion/abrir.py skills/sesion/cerrar.py 2>/dev/null)" || PREP=""
  printf '%s\n' "$PREP" | grep -q '^DESCARGA ' || PREP=""
  # REINTENTO no viaja: es DESCARGA con main en lugar de v<versión>, y la skill lo arma (la mitad del texto añadido)
  PREP="$(printf '%s\n' "$PREP" | grep -v '^REINTENTO ')"
fi
# dónde está el plugin instalado (1.24.9): la apertura mínima corre abrir.py desde aquí, en el contenedor, sin descargar nada
# a la computadora; METODO va aunque no haya python3, leído con sed de metodo.md
if [ "$HAY_RAIZ" != no ]; then
  METODO_L="$(sed -n '/^# Método de trabajo/{p;q;}' "$RAIZ/metodo.md" 2>/dev/null)"
  TEXTO="${TEXTO}

Para la apertura mínima:
PLUGIN ${RAIZ}"
  [ -n "$METODO_L" ] && ! printf '%s\n' "$PREP" | grep -q '^METODO ' && TEXTO="${TEXTO}
METODO ${METODO_L}"
fi
[ -n "$PREP" ] && TEXTO="${TEXTO}

Para abrir un proyecto, ya preparado por este aviso con preparar.py; se usa tal cual, sin calcularlo otra vez en el contenedor (METODO_DESCARGA solo cuando la RESPUESTA de abrir.py lo pida):
${PREP}"

# JSON a mano, sin python: el texto solo puede traer barras, comillas, tabuladores y saltos de línea
j=$TEXTO
j=${j//\\/\\\\}
j=${j//\"/\\\"}
j=${j//$'\t'/\\t}
j=${j//$'\r'/}
j=${j//$'\n'/\\n}
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$j"
