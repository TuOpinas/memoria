# Evals del plugin

Las pruebas de `pruebas/` comprueban los scripts y la página. Los evals comprueban **lo que Claude hace con las skills**: una conversación guionada contra una raíz de prueba, con el plugin cargado y una computadora de mentira, y al final se mira lo que respondió, qué herramientas llamó y qué cambió en la raíz.

Cuestan tokens del plan (cada escenario es una conversación con el modelo: entre 0,5 y 1,5 USD en Opus, 30 a 90 segundos; el 07, sin consola, más), así que corren antes de publicar una versión y cuando se pide, no en cada commit.

## Correr

Desde una sesión de Claude Code (usa la cuenta de la sesión, que toma de `CLAUDE_CODE_USER_EMAIL`; con una clave de API hay que poner esa variable con el correo que la raíz de prueba va a declarar):

```
python3 pruebas/evals/correr.py                       # todos los escenarios, con Opus
python3 pruebas/evals/correr.py 03-cierre-con-decision --modelo sonnet
python3 pruebas/evals/correr.py --plugin /ruta/al/plugin/de/otra/rama
```

Deja en `resultados/<fecha>-<versión>-<modelo>/` un `resultados.json` (medidas y comprobaciones de cada escenario) y la transcripción de cada uno (`<escenario>.md`: cada turno, cada llamada con su entrada y su resultado, y la respuesta). `resultados/` no se versiona.

## Cómo funciona

- **El plugin que se prueba** se copia a `/root/.claude/plugins/evals/memoria`, que es donde la skill `sesion` lo busca, con una versión mayor que cualquier copia instalada (para que la elija si hay varias) y su `metodo.md` regenerado. Se borra al terminar.
- **La raíz** es una copia de `pruebas/tablero/raiz` con las fechas de archivo fijas (2026-08-01). La cuenta de la conversación es la de quien corre el eval (Claude Code la pone sola), así que el escenario dice qué cuenta de la raíz de prueba ocupa esa persona (`cuenta: ana@ejemplo.test`, la responsable de contexto; `carla@ejemplo.test`, que solo colabora en ventas) y la copia la escribe con el correo real.
- **La computadora** es `dispositivo.py`: las herramientas `get_device_info`, `device_list_dir`, `device_bash`, `device_stage_files`, `device_commit_files` y las de permisos, como servidor MCP en el proceso del eval. Con consola, `device_bash` corre bash con un `$HOME` propio donde la raíz está en `$HOME/mnt/Memoria--Prueba`, como en Mac; sin consola, el mismo bash sin nada bajo `$HOME/mnt`, como Google Drive en Windows. Los scripts que las skills traen con DESCARGA (`abrir.py`, `cerrar.py`, `permisos.py`, los del tablero) ya están sembrados en ese `$HOME`, con la huella de la rama: así no hace falta red y se prueba la rama, no `main`.
- **No hay tablero**: las herramientas `Artifact` y `ArtifactData` no existen en la conversación del eval, así que lo del tablero (la cola al abrir, la marca al cerrar) no se ejercita aquí; lo cubre `pruebas/tablero/`.

## Un escenario

Un `.md` en `escenarios/` con cabecera y una descripción de lo que debe pasar:

```
---
raiz: raiz                      # carpeta de pruebas/tablero/, o una ruta
cuenta: ana@ejemplo.test        # la cuenta de la raíz que ocupa quien conversa
consola: si                     # no: Windows sin consola
max_turnos: 40
preparar:                       # antes de empezar
  - "copia-en-conflicto ventas/cuentas/sesiones.md"
turnos:                         # lo que dice la persona, en orden
  - "Abre sesión en ventas/cuentas."
  - "Sí."
entre:                          # lo que otra persona hace después del turno N
  - "1 otro-cierre ventas/cuentas"
comprobar:
  - recuadro
  - entrada-sesion ventas/cuentas
---
```

Pasos de `preparar` y `entre`: `migrar` (la raíz pasa a la estructura de la 1.22 por la cuenta del escenario), `copia-en-conflicto <ruta.md>`, `tocar <ruta>`, `escribir <ruta> <línea>`, `otro-cierre <area>/<proyecto>`.

Comprobaciones: `recuadro`, `cambia <ruta>`, `no-existe <ruta>`, `bloque-igual <ruta> <bloque>`, `apertura-minima`, `apertura-completa <a>/<p>`, `pregunta-claude-outputs`, `sin-escrituras`, `solo-escribe-en <rutas>`, `nada-hasta-el-turno N [<rutas>]`, `entrada-sesion <a>/<p>`, `decision-registrada <a>/<p>`, `estatus <a>/<p>` (o `en-corto`), `nombres-nuevos <a>/<p>`, `migrada <area>`, `cierre-con-script`, `conserva-entradas <a>/<p>`, `contiene <ruta> <texto>`, `sin-rutas-absolutas`, `menciona <texto>[@N]`, `no-contiene <texto>`, `no-menciona <texto>`, `herramienta <nombre>`, `sin-herramienta <nombre>`, `llamadas-maximo N[@T]`, `palabras-maximo N[@T]`, `sin-ingles`. Se añaden en `correr.py` con `@comprobacion`.

## Los escenarios

| # | Qué | Qué tiene que pasar |
|---|---|---|
| 01 | Pregunta ajena a la memoria | recuadro en la primera respuesta, apertura mínima, pregunta por «Claude outputs» al responsable, nada escrito salvo `metodo.md` |
| 02 | Trabajo de un proyecto sin nombrarlo | apertura completa de `ventas/cuentas`, responde con lo de la carpeta, nada escrito |
| 03 | Cierre con una decisión | la decisión se enseña y se escribe solo con el sí; entrada, decisión, `En corto`, línea del área; con `cerrar.py` |
| 04 | Otra persona cierra mientras | las dos entradas y los dos pasos quedan; Claude dice que alguien escribió |
| 05 | Copia en conflicto de Drive | se juntan todas las entradas; la copia a la papelera con el sí |
| 06 | Cuenta que solo colabora | escribe solo en `ventas`; no toca el Panorama; no se le habla de «Claude outputs» |
| 07 | Cierre sin consola (Windows) con otra persona cerrando mientras | copia por `device_stage_files`, `cerrar.py --sin-fechas` sobre la copia, `device_commit_files` con rechazo por fecha y repetición; nada se pierde |
| 08 | Cierre con lo que no se guarda | la decisión entra con su porqué; el saldo de hoy, la contraseña y los borradores tirados no quedan en ningún archivo (`no-contiene`) |
| 09 | Cierre sobre una raíz migrada a la 1.22 | sin oferta de migrar; decisión y `Estatus` enseñados antes de escribir; entrada con «Tema:», decisión con «Descartado:», `Estatus` del proyecto y del área, con `cerrar.py` |
| 10 | Apertura sobre una raíz sin migrar | ofrece migrar en una línea sin escribir; con el sí, `migrar_estructura.py` migra solo las áreas de la cuenta y `guia.md`, con su entrada `(migracion)`; las de otra cuenta quedan igual |

Lo que encontraron los primeros (2026-10-23, 1.19 → 1.20), y qué pasó con cada cosa: la decisión dictada junto con «cierra la sesión» se escribía sin pedir el sí (corregido en `cerrar.md`); el cierre escribía con un script propio en cada sesión (de ahí `cerrar.py`); «Descartamos: no consta» como relleno (corregido en `cerrar.md`); la apertura probaba primero la ruta absoluta de la carpeta antes de `$HOME/mnt` (dos llamadas de más; sin cambio todavía, pendiente de ver si se repite).

Comprobaciones añadidas por la revisión de la 1.20: `cierre-con-script` exige que la llamada devolviera «escritos» y marca como «a mano» una redirección o un script propio sobre los cuatro archivos; `apertura-completa` exige que `abrir.py` respondiera. Lo que queda sin medir: que una sesión real (no un eval) elija una copia `plugins/evals-*` que una corrida muerta dejó atrás; por eso `correr.py` borra esas copias al arrancar y al salir, también con SIGTERM, y no deja correr dos evals a la vez.
