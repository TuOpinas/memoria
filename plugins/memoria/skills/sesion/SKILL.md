---
name: sesion
description: Abre y cierra sesiones de trabajo sobre un proyecto. Usala cuando digan 'abre sesion', 'retomamos X', 'en que quedamos con...', 'cierra la sesion', 'guarda lo de hoy', 'terminamos' o 'cierra el proyecto', y cuando el dueño de un proyecto pregunte por el suyo: '¿como va X?', '¿en que estatus esta X?', '¿que falta en X?'.
---

# Sesión

Abrir y cerrar una sesión de trabajo sobre un proyecto. Este archivo es lo que hace falta para abrir, que solo lee. Lo demás vive en anexos, junto a este archivo, y se lee cuando toca:

- `cerrar.md`: cerrar la sesión y cerrar el proyecto, y responder o plantear un cuestionamiento.
- `premisas.md`: registrar, cambiar o retirar una premisa, en la sesión del responsable de contexto.
- `sin-carpeta.md`: abrir, consultar o preguntar al director sin ninguna carpeta conectada, leyendo la raíz en Drive.

**Abrir no carga `convenciones`.** Antes de escribir cualquier cosa en la carpeta (cerrar, guardar un documento o un análisis, registrar una premisa o una decisión, mover algo) se carga la skill `convenciones` entera y, si es cerrar o una premisa, su anexo. Sin excepción, aunque sea una línea: sus prohibiciones aplican a toda escritura.

## Cuándo

**Abrir**: «abre sesión en compras», «retomamos automatización de órdenes», «¿en qué quedamos con X?», o cualquier arranque de trabajo sobre un proyecto existente. **Sin que lo pidan**, cuando el dueño de un proyecto pregunta por el suyo («¿en qué estatus está X?», «¿cómo va X?», «¿qué falta en X?»): dueño es quien tiene su cuenta junto al área del proyecto en `guia.md`, o figura como `Dueño` en su `proyecto.md`. Se abre sin preguntar, porque abrir no registra nada. Si quien pregunta no es el dueño, es `consulta`. Si solo preguntó y no trabaja, no hay nada que cerrar: nada se registra sin «cierra la sesión».

**Cerrar** («cierra la sesión», «guarda lo de hoy», «terminamos»), **cerrar el proyecto** («cierra el proyecto», «esto ya está») y **responder un cuestionamiento** («lo mantengo», «lo cambio»): `cerrar.md`. **Premisas**: `premisas.md`.

**Antes de nada** se localiza la raíz entre las carpetas conectadas: la que tiene `guia.md` y `metodo.md` en su primer nivel. Si las herramientas de carpetas no están cargadas, se buscan y se cargan primero; nunca se dice que no hay carpeta sin haberlas listado, y con una carpeta conectada nunca se usa el conector de Google Drive. Si después de buscarlas no hay ninguna, `sin-carpeta.md`. Si hay más de una raíz conectada, se pregunta en cuál y la sesión se queda en esa (lo de otra entra solo por un traspaso, como dice `raices.md` junto al contrato). Si no queda claro el proyecto, se pregunta; nunca se asume el último usado.

# Abrir sesión

Abrir es solo lectura. No se escribe ningún archivo, salvo poner al día `metodo.md` cuando la raíz está atrasada (abajo).

## Qué leo, en dos o tres llamadas

Todo lo que dice la sección 12 de `convenciones` para abrir (nivel 0, nivel 1 y el barrido de avisos) lo lee de una vez `abrir.py`, junto a este archivo, en la computadora. No escribe nada, nunca abre `taller/`, `fuentes/` ni `restringido/` (de `taller/` y `fuentes/` del proyecto solo mira fechas), de otros proyectos solo mira las líneas `Afecta a:`, `Cuestiona a:` y `Responde a:`, y lo restringido no sale salvo que el proyecto activo esté dentro.

1. **Con Bash, en el contenedor, una llamada**: el directorio de esta skill (`find /root/.claude/plugins -path '*/.trash' -prune -o -type d -path '*/memoria*/skills/sesion' -print`, y si hay varias copias del plugin, la de versión más alta en su `../../.claude-plugin/plugin.json`), la versión del plugin, el `sha256sum` de `abrir.py` y la primera línea del `metodo.md` del plugin (`../../metodo.md`).
2. **Con device_bash, en la computadora, una llamada**: `mkdir -p $HOME/memoria && cd $HOME/memoria && curl -sfL -o abrir.py https://raw.githubusercontent.com/TuOpinas/memoria/v<versión>/plugins/memoria/skills/sesion/abrir.py && echo "<huella>  abrir.py" | sha256sum -c && python3 abrir.py "<raíz en $HOME/mnt>" <area>/<proyecto> --cuenta <correo de la cuenta> --plugin "<primera línea del metodo.md del plugin, la de la llamada 1>"`. Sin proyecto todavía, sin `<area>/<proyecto>`: imprime el nivel 0 y la lista de proyectos de cada área, para saber cuál se abre; después se vuelve a correr con el proyecto (el script ya está, basta `cd $HOME/memoria && python3 abrir.py …`). Si `sha256sum -c` falla, se repite una vez con `main` en lugar de `v<versión>`; un script que no pasa la comprobación no se ejecuta nunca, ni se pega su contenido en un comando. Si tras ese reintento no hay un `abrir.py` comprobado (la computadora no llega a GitHub, o ninguna copia cuadra), se abre como sin consola (abajo) y se dice en media línea.
3. **La cola del tablero**, si la cuenta tiene uno: con `Artifact` (`list`) se buscan los artifacts llamados «Tablero <organización>» y «Tablero <organización> completo» (la organización es lo que va antes del «·» en el título de `guia.md`); de cada uno, con `ArtifactData` (se carga con `ToolSearch`), un `list` de la colección `cambios` con `query.limit` 1000 (y su `next_cursor` si lo trae), y de ahí se queda lo que tiene `proyecto` igual a `<area>--<proyecto>` y lo que tiene `area` igual al área del proyecto (prioridades marcadas desde el tablero y notas de área que dejó una sesión sin carpeta). Si no hay tablero, no se pregunta; si no se deja leer, se dice en una línea y se sigue.

Si la conversación no tiene consola en la computadora (solo las herramientas que traen archivos), o no hay un `abrir.py` comprobado, se carga `convenciones` y se lee por los niveles de su sección 12, y `metodo.md` no se toca: sin el script no hay veredicto de versión, y lo copiará la siguiente sesión que lo tenga. Nada más se lee al abrir: `base/`, `taller/`, `fuentes/` y el resto de `area.md` entran cuando el trabajo los pide, por sus disparadores de esa misma sección.

## Qué respondo

**La primera vez en la conversación** que se abre sesión sobre la carpeta, la respuesta empieza con una sola línea: «Memoria activa · <organización> · método <versión de la primera línea de `metodo.md` de la raíz> · escribes en <áreas de la cuenta con su papel, dueño o colabora, que dice la sección CUENTA de `abrir.py`, o «ninguna área: dime en cuál trabajas»>». Solo esa vez.

Después, cuatro bloques, en este orden y sin encabezados largos, y la puesta al día del método si toca.

**Dónde quedó todo.** Cuatro o cinco líneas: objetivo del proyecto en una frase, qué se hizo en la última sesión, qué quedó pendiente. Si la sesión se abrió por una pregunta de estado, este bloque es la respuesta y empieza por ella: por `En corto` si el proyecto lo tiene, tal cual o casi, diciendo si hubo sesiones después de su fecha; si no, en qué está y qué espera.

**Lo que llegó del tablero**, solo si la cola trae algo de este proyecto. Una línea por cambio, con su fecha: el paso marcado hecho y su nota, la nota suelta, la corrección propuesta, la fecha que la tarea no encontró dónde aplicar. Termina preguntando qué pasó con cada hecho sin nota y si cada corrección va: es lo primero que se resuelve en la sesión.

**Avisos**, los que da la sección AVISOS de `abrir.py`, contados en llano y en este orden:

- Un cuestionamiento abierto a una decisión de este proyecto (o, al responsable de contexto, a una premisa) va primero, porque espera al dueño: qué decisión, quién lo planteó, su por qué en una línea y de qué proyecto viene.
- Una decisión de otro proyecto que nombra este en `Afecta a:` desde la última sesión: la entrada, su fecha, quién decidió y de qué proyecto viene. Las anteriores a la última sesión ya se vieron y no se repiten.
- Una decisión reciente de este proyecto que choca con una premisa vigente: se dice cuál y por qué, sin darlo por resuelto. Esto no lo calcula el script: se mira con las premisas y las decisiones que imprime.
- `base/contexto.md` con más de 90 días; un entregable con una base más nueva que él; un borrador de más de 30 días.
- Trabajo sin sesión: archivos que cambiaron después de la última entrada de `sesiones.md`. Se dice qué cambió y se propone registrarlo hoy, preguntando qué pasó.

Si no hay avisos, no se menciona que no los hay.

**Puesta al día del método.** La sección METODO de `abrir.py` trae la primera línea del `metodo.md` de la raíz y, con `--plugin`, la línea «Veredicto», que compara versión y huella en numérico («1.14.10» es mayor que «1.14.9»); se hace lo que dice el veredicto, sin comparar a mano. Si dice «AL DIA», no se dice nada. Si no:

- **«RAIZ ATRASADA»** (la versión del plugin es más nueva, o es la misma y la raíz no lleva huella): lo abra quien lo abra, se copia el `metodo.md` del plugin sobre el de la raíz sin preguntar, escrito directo desde el plugin como dice «Los archivos del plugin en la computadora» en la skill `tablero`, nunca pegado; es una copia exacta que nadie edita y no toca nada más. Se dice en una línea al final: «He puesto al día las reglas del método en esta carpeta, a la versión <versión del plugin>. No cambia nada de lo que hay en ella.» Si la escritura falla por permisos, no se dice nada.
- **«PLUGIN ATRASADO»**: no se copia nada y se dice en una línea: «Esta carpeta usa una versión del método más nueva que la de tu Claude (<versión de la raíz> frente a <versión de tu plugin>). Actualízalo en la app de Claude, en Customize → Plugins, con el botón Update del marketplace memoria-marketplace, o pide ayuda a quien administra la carpeta.»
- **«MISMA VERSION, HUELLA DISTINTA»**: no se toca ni se dice nada.

**Propuesta de trabajo.** Dos o tres focos, tomados de los siguientes pasos de `proyecto.md`, de lo pendiente en la última sesión y de los avisos, cada uno con una línea de por qué ahora. Primero lo que otra persona está esperando (un cuestionamiento abierto es el primero: basta con que el dueño diga si lo mantiene o lo cambia, y por qué), después lo que cierra algo empezado, al final lo que abre frente nuevo. Si un aviso afecta a un foco, se dice ahí mismo. Termina preguntando por cuál empezamos, y espera.

## Lo que nunca hago al abrir

- Escribir algo, salvo poner al día `metodo.md` cuando la raíz está atrasada
- Escribir nada después de abrir sin haber cargado antes `convenciones`
- Leer más de lo que imprime `abrir.py`, o, sin él, más del nivel 0 y el nivel 1
- Dar como aviso a alguien una decisión que leí en una carpeta restringida a la que su proyecto no pertenece
- Deducir lo que hay en una carpeta que no se deja leer: se dice qué es y de quién, y ahí se para
- Usar el conector de Google Drive teniendo la carpeta conectada

## Ejemplo de apertura

**Usuario:** retomamos automatización de órdenes

> El proyecto busca quitar aprobaciones manuales en compras de bajo monto. La última sesión, el 14 de agosto, terminaste las entrevistas con Ana y con Finanzas y quedó pendiente decidir el criterio de corte.
>
> Dos avisos. Finanzas registró el 20 de agosto que el cierre pasa al día 3 y marcó este proyecto como afectado: decidió Luis Romero. Y el mapa de proceso lleva 41 días en borrador esperando a Ana.
>
> Tres focos posibles para hoy:
>
> 1. Cerrar el criterio de corte por monto. Es lo que bloquea el flujo de aprobación y Finanzas está esperando.
> 2. Revisar si el cambio de fecha de cierre toca el flujo de aprobación antes de seguir construyendo sobre él.
> 3. Empujar la revisión del mapa de proceso, que lleva seis semanas parado.
>
> ¿Por cuál empezamos?
