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

## En GitHub, sin sesión

`.github/workflows/evals.yml` los corre en GitHub cuando un pull request recibe la etiqueta `evals` (los escenarios, de la línea «Evals:» de su descripción; sin ella, 01, 02 y 03), o a mano desde Actions con los escenarios y el modelo. Gasta del plan de la cuenta cuyo token está en el secreto `CLAUDE_CODE_OAUTH_TOKEN` (`claude setup-token`), con su correo en `EVALS_CORREO`. Deja el resumen como comentario del pull request y los resultados como artefacto. Así quien prepara una versión los lanza poniendo la etiqueta, sin depender de su sesión ni de su computadora.

## Cómo funciona

- **El plugin que se prueba** se copia bajo `/root/.claude/plugins/evals-<pid>/memoria`, con una versión mayor que cualquier copia instalada y su `metodo.md` regenerado; la conversación lo carga como plugin local, y ningún comando lo busca en disco (`sin-buscar-plugin`). Se borra al terminar.
- **La raíz** es una copia de `pruebas/tablero/raiz` con las fechas de archivo fijas (2026-08-01). La cuenta de la conversación es la de quien corre el eval (Claude Code la pone sola), así que el escenario dice qué cuenta de la raíz de prueba ocupa esa persona (`cuenta: ana@ejemplo.test`, la responsable de contexto; `carla@ejemplo.test`, que solo colabora en ventas) y la copia la escribe con el correo real.
- **La computadora** es `dispositivo.py`: las herramientas `get_device_info`, `device_list_dir`, `device_bash`, `device_stage_files`, `device_commit_files` y las de permisos, como servidor MCP en el proceso del eval. Con consola, `device_bash` corre bash con un `$HOME` propio donde la raíz está en `$HOME/mnt/Memoria--Prueba`, como en Mac; sin consola, el mismo bash sin nada bajo `$HOME/mnt`, como Google Drive en Windows. Los scripts que las skills traen con DESCARGA (`abrir.py`, `cerrar.py`, `permisos.py`, los del tablero) ya están sembrados en ese `$HOME`, con la huella de la rama: así no hace falta red y se prueba la rama, no `main`.
- **El tablero, de mentira y solo si el escenario lo pide** (1.24.8): con `tablero: <archivo>.json` de `escenarios/`, `tablero_falso.py` sirve `list_artifacts`, `db_query`, `db_get`, `read_file` y `db_write` del conector `claude-artifacts` con la cola `cambios` del archivo (`read_file` dice que no hay archivos: sin sugerencias ni página que partir). Sin él no hay tablero; la página y la puesta al día las cubre `pruebas/tablero/`.

## Un escenario

Un `.md` en `escenarios/` con cabecera y una descripción de lo que debe pasar:

```
---
raiz: raiz                      # carpeta de pruebas/tablero/, o una ruta
tablero: 14-cola.json           # opcional: la cola del tablero de mentira
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

Pasos de `preparar` y `entre`: `migrar` (la raíz pasa a la estructura de la 1.22 por la cuenta del escenario), `copia-en-conflicto <ruta.md>`, `tocar <ruta>`, `escribir <ruta> <línea>`, `sustituir <ruta> <viejo> => <nuevo>` (con `\n` para un salto de línea), `otro-cierre <area>/<proyecto>`.

Comprobaciones: `recuadro` (tabla de una columna, fuera de cita y de código), `recuadro-cierre` (igual, en la última respuesta), `cita-antes-de-escribir [decision]` (la respuesta que pide el sí enseña en cita la entrada, el `Estatus` y, con `decision`, cada decisión), `cambia <ruta>`, `no-existe <ruta>`, `bloque-igual <ruta> <bloque>`, `apertura-minima`, `apertura-completa <a>/<p>`, `pregunta-claude-outputs`, `pregunta-antes N`, `sin-escrituras`, `solo-escribe-en <rutas>`, `nada-hasta-el-turno N [<rutas>]`, `entrada-sesion <a>/<p>`, `decision-registrada <a>/<p>`, `estatus <a>/<p>` (o `en-corto`), `nombres-nuevos <a>/<p>`, `migrada <area>`, `cierre-con-script`, `conserva-entradas <a>/<p>`, `contiene <ruta> <texto>`, `sin-rutas-absolutas`, `menciona <texto>[@N]`, `no-contiene <texto>`, `no-menciona <texto>`, `herramienta <nombre>`, `sin-herramienta <nombre>`, `llamadas-maximo N[@T]`, `palabras-maximo N[@T]`, `sin-ingles`, `skill <nombre> <N>` (la skill se cargó exactamente N veces), `sin-buscar-plugin` (ningún comando busca el plugin en disco) y `no-menciona-re <regex>[@N]`. Se añaden en `correr.py` con `@comprobacion`.

## Los escenarios

Del 01 al 09, y el 12, corren sobre la raíz ya migrada a la 1.22 (`preparar: migrar`): sin migrar, la pregunta bloqueante de la estructura ocupa el primer turno, y eso lo prueban el 10 y el 11.

| # | Qué | Qué tiene que pasar |
|---|---|---|
| 01 | Pregunta ajena a la memoria | recuadro en la primera respuesta, apertura mínima sin cargar la skill `sesion` (1.24.8), pregunta por «Claude outputs» al responsable, nada escrito salvo `metodo.md` |
| 02 | Trabajo de un proyecto sin nombrarlo | apertura completa de `ventas/cuentas`, responde con lo de la carpeta, nada escrito |
| 03 | Cierre con una decisión | la decisión se enseña y se escribe solo con el sí; entrada, decisión, `Estatus`, línea del área; con `cerrar.py` |
| 04 | Otra persona cierra mientras | las dos entradas y los dos pasos quedan; Claude dice que alguien escribió |
| 05 | Copia en conflicto de Drive | se juntan todas las entradas; la copia a la papelera con el sí |
| 06 | Cuenta que solo colabora | escribe solo en `ventas`; no toca el `Estatus` del área; no se le habla de «Claude outputs» |
| 07 | Cierre sin consola (Windows) con otra persona cerrando mientras | copia por `device_stage_files`, `cerrar.py --sin-fechas` sobre la copia, `device_commit_files` con rechazo por fecha y repetición; nada se pierde |
| 08 | Cierre con lo que no se guarda | la decisión entra con su porqué; el saldo de hoy, la contraseña y los borradores tirados no quedan en ningún archivo (`no-contiene`) |
| 09 | Cierre sobre una raíz migrada a la 1.22 | sin oferta de migrar; decisión y `Estatus` enseñados antes de escribir; entrada con «Tema:», decisión con «Descartado:», `Estatus` del proyecto y del área, con `cerrar.py` |
| 10 | Apertura sobre una raíz sin migrar | pregunta si se migra antes de responder, sin escribir; con el sí, `migrar_estructura.py` migra las áreas de la cuenta, `guia.md` y, porque es la responsable de contexto, las de otra cuenta, con su entrada `(migracion)` (la de las ajenas dice por quién) |
| 11 | El 10 sin consola | lo mismo por la copia, con `espejo.py migracion` y `device_commit_files` |
| 12 | Escribe, publica y cierra (1.23) | la entrada lleva «Escribió:» y «Publicó:» escritos por `cerrar.py`; el entregable queda vigente; lo que se registra se enseña en cita antes del sí (`cita-antes-de-escribir`) y el cierre termina con el recuadro «Memoria · sesión cerrada» (`recuadro-cierre`) |
| 13 | El 01 midiendo la apertura mínima | corre `abrir.py` desde PLUGIN sin buscar el plugin en disco (`sin-buscar-plugin`) ni ejecutar nada en la computadora (`minima-sin-ejecutar`) |
| 14 | La cola del tablero con respuestas (1.24.8) | «Aceptaste…» para lo que marcó la dueña del tablero, «alguien con acceso a tu tablero» para lo marcado sin cuenta (`por: null`), y quien decidió nunca como quien marcó |
| 15 | El cierre deja su marca en el tablero (1.25.1) | con un tablero de la cuenta, el cierre escribe la marca en «cierres» como dice `respuesta` de `cerrar.py` (`marca-tablero`) y el recuadro lleva «Tablero: avisado» |

Lo que encontraron los primeros (2026-10-23, 1.19 → 1.20), y qué pasó con cada cosa: la decisión dictada junto con «cierra la sesión» se escribía sin pedir el sí (corregido en `cerrar.md`); el cierre escribía con un script propio en cada sesión (de ahí `cerrar.py`); «Descartamos: no consta» como relleno (corregido en `cerrar.md`); la apertura probaba primero la ruta absoluta de la carpeta antes de `$HOME/mnt` (dos llamadas de más; sin cambio todavía, pendiente de ver si se repite).

Comprobaciones añadidas por la revisión de la 1.20: `cierre-con-script` exige que la llamada devolviera «escritos» y marca como «a mano» una redirección o un script propio sobre los cuatro archivos; `apertura-completa` exige que `abrir.py` respondiera. Lo que queda sin medir: que una sesión real (no un eval) elija una copia `plugins/evals-*` que una corrida muerta dejó atrás; por eso `correr.py` borra esas copias al arrancar y al salir, también con SIGTERM, y no deja correr dos evals a la vez.
