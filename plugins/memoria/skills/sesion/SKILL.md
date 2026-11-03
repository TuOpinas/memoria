---
name: sesion
description: Abre y cierra sesiones de trabajo sobre un proyecto. Usala cuando digan 'abre sesion', 'retomamos X', 'en que quedamos con...', 'cierra la sesion', 'guarda lo de hoy', 'terminamos' o 'cierra el proyecto', y cuando el responsable de un proyecto pregunte por el suyo: '¿como va X?', '¿en que estatus esta X?', '¿que falta en X?'. Tambien los permisos de la carpeta compartida: 'revisa los permisos', 'aplica los permisos', '¿quien puede escribir donde?'.
---

# Sesión

Abrir y cerrar una sesión de trabajo sobre un proyecto. Este archivo es lo que hace falta para abrir, que solo lee. Lo demás vive en anexos, junto a este archivo, y se lee cuando toca:

- `minima.md`: la apertura mínima. El aviso de arranque la inyecta en cada conversación y no hace falta cargar esta skill para ella.
- `cola.md`: la cola del tablero (lo marcado desde la página y las sugerencias), al abrir un proyecto cuando la cuenta tiene tablero y al cerrar si la cola trajo algo.
- `cerrar.md`: cerrar la sesión y el proyecto, y responder («lo mantengo», «lo cambio») o plantear un cuestionamiento.
- `sin-consola-sesion.md`: abrir y cerrar cuando la raíz está conectada pero el shell de la computadora no la ve.
- `migracion.md`: pasar la carpeta a la estructura de la 1.22, con «Migrar ahora».
- `premisas.md`: registrar, cambiar o retirar una premisa, en la sesión del responsable de contexto.
- `sin-carpeta.md`: abrir, consultar o preguntar al director sin ninguna carpeta conectada, leyendo la raíz en Drive.
- `permisos.md`: revisar y aplicar los permisos de Drive («revisa los permisos», «aplica los permisos»).

Abrir solo lee. Antes de escribir cualquier cosa en la carpeta se carga el anexo `escribir.md` de `convenciones`, aunque sea una línea; para guardar un documento, mover algo o crear, `convenciones` entera.

## Cuándo

**Abrir**: «abre sesión en compras», «retomamos X», «¿en qué quedamos con X?», o cualquier trabajo sobre un proyecto existente aunque no lo nombre («guíame en el paso 4», «cambia el plugin para que…», «a un usuario le sale este error…», algo para un cliente que tiene su proyecto). Se abre antes de responder, sin preguntar y sin pedir que digan «abre sesión»; la respuesta empieza por lo que pidió, y lo de la apertura va en pocas líneas, solo lo que cambia lo que se va a hacer. También cuando el responsable de un proyecto pregunta por el suyo («¿cómo va X?», «¿qué falta en X?»): responsable es quien figura como Responsable del área en la tabla de `guia.md` (su cuenta, en «Quién es quién») o como `Responsable` en su `proyecto.md`. Si quien pregunta no es el responsable, es `consulta`. Si solo preguntó, no hay nada que cerrar.

**La raíz** es la carpeta conectada con `guia.md` y `metodo.md` en su primer nivel. A `abrir.py` se le pasa la ruta que da `get_device_info`: si en la consola la carpeta cuelga de `$HOME/mnt/…`, el script la resuelve y la imprime en su línea RAIZ, que es la que se usa después, sin `ls` ni `find`. Nunca se dice que no hay carpeta sin haberlas listado; si no hay ninguna, `sin-carpeta.md`. Con más de una raíz, se pregunta en cuál se trabaja y la sesión se queda en esa (lo de otra entra solo por un traspaso, `raices.md` junto al contrato). Si no queda claro el proyecto, se pregunta; nunca se asume el último usado.

## Apertura mínima

La hace la conversación con lo que trae el aviso de arranque, sin esta skill, y siempre igual, con consola o sin ella: lista la raíz, trae una copia de lo que lee y corre `abrir.py` en el contenedor, desde el plugin instalado (1.24.9). En la computadora no ejecuta nada descargado, que el modo Auto frena cuando la petición no tiene que ver con la memoria. Se sigue aquí cuando el aviso fue el corto o no trajo PLUGIN, o cuando el control del plugin la pide: se lee `minima.md`, junto a este archivo, con `<directorio de esta skill>/../..` como PLUGIN y la primera línea de su `metodo.md` como METODO; lo que diga la sección RESPUESTA de `abrir.py` es lo que se hace. Nunca en una tarea programada.

## Abrir sesión

### Qué leo, y en cuántas llamadas

`abrir.py`, junto a este archivo, lee de una vez lo que dice la sección 12 de `convenciones` (nivel 0, nivel 1 y el barrido de avisos) y no escribe nada. Nunca abre `taller/`, `fuentes/` ni `restringido/`, de otros proyectos solo mira las líneas `Afecta a:`, `Cuestiona a:` y `Responde a:`, y lo restringido no sale salvo que el proyecto activo esté dentro.

1. **La descarga**: VERSION, METODO y DESCARGA vienen al final del aviso de arranque, ya calculados; si hay dos avisos, el de versión más alta. Si el aviso no trae DESCARGA, se calcula con Bash en el contenedor, un comando simple y sin `find`: `python3 <PLUGIN del aviso, o el directorio de esta skill con ../..>/preparar.py '$HOME/memoria' skills/sesion/abrir.py skills/sesion/cerrar.py`. REINTENTO es la misma DESCARGA con `main` en lugar de `v<versión>` en sus dos direcciones.
2. **Con device_bash, en la computadora, directo con el proyecto**: lo que va detrás de «DESCARGA » seguido de ` && python3 abrir.py "<ruta de get_device_info>" <area>/<proyecto> --cuenta <correo> --plugin "<la línea METODO sin «METODO »>" --origen "<la misma ruta>"`. Si ya se descargó en esta conversación, basta `cd $HOME/memoria && python3 abrir.py …`. Si la petición nombra el proyecto, aunque sea con otras palabras, o se reconoce en la lista de proyectos de la mínima, se corre ya con él; sin proyecto (imprime `guia.md` y la lista) solo cuando de verdad no se sabe cuál es. Si la comprobación falla, una vez con REINTENTO; un script que no la pasa no se ejecuta nunca, ni se pega su contenido en un comando. Sin un `abrir.py` comprobado, se carga `convenciones` y se lee por los niveles de su sección 12, `metodo.md` no se toca y se dice en media línea. Su sección RESPUESTA dice qué hacer con el método, la estructura, los permisos y «Claude outputs»: lo que la apertura mínima ya hizo o preguntó en esta conversación no se repite.
3. **La cola del tablero**, si la sesión tiene el conector de artifacts y la cuenta tiene tablero (lo pide la RESPUESTA): `cola.md`.

Lo que la apertura mínima no cargó va en un solo ToolSearch al empezar: `device_bash`, `device_request_delete_permission` y las del tablero que pide la RESPUESTA, más `db_get`, `db_write` y `publish_files`.

## Qué respondo

La apertura son unas pocas llamadas seguidas, sin mensajes entre ellas, y la respuesta llega entera al final. Si hay SendUserMessage, todo lo que va antes de una herramienta de preguntas se manda con él.

**El recuadro.** La primera vez en la conversación, la respuesta empieza con el recuadro que trae la sección RESPUESTA de `abrir.py`, tal cual: una tabla de Markdown de una columna con la cabecera «Memoria de trabajo · <organización> · v<versión>» y solo las filas que piden algo (sin ninguna, basta la cabecera). Si ya salió, no se repite, y una pregunta que ya se hizo en la conversación tampoco. El cierre termina con un recuadro como este (`cerrar.md`). Toda tabla de la memoria sigue la misma regla: nunca un bloque de código ni un recuadro dibujado, y sus celdas sin saltos de línea ni «|» (se cambian por «·»).

Después, estos bloques, en este orden y sin encabezados largos.

**Dónde quedó todo.** Cuatro o cinco líneas: el objetivo en una frase, qué se hizo en la última sesión y qué sigue. Si la sesión se abrió por una pregunta de estado, este bloque es la respuesta y empieza por el `Estatus`, diciendo si hubo sesiones después de su fecha.

**Lo que viene de la memoria va en recuadros**, para que se distinga de lo que escribe Claude: una tabla por bloque con la cabecera «Memoria · <qué es> · <cuántos>», una fila por cosa con lo que dice y de dónde sale. Lo que dice Claude va debajo, en texto normal. Solo salen los que traen algo, en este orden: lo marcado en el tablero y las sugerencias (`cola.md`) y los avisos.

**Avisos**: recuadro «Memoria · avisos · <cuántos>», una fila por cada línea de la sección AVISOS de `abrir.py`, en el orden en que las da (lo que espera a alguien va primero) y en llano. Una copia en conflicto se junta antes de seguir (`cerrar.md`); un trabajo sin sesión se pregunta qué pasó y se propone registrarlo hoy, con quien lo hizo en «Sesión de:». Además, y esto no lo calcula el script, una decisión reciente de este proyecto que choca con una premisa vigente, sin darlo por resuelto. Sin avisos, no se menciona que no los hay.

**El método y la estructura** los resuelve la RESPUESTA, sin comparar a mano. Con «RAIZ ATRASADA», lo abra quien lo abra, copia el `metodo.md` del plugin sin preguntar ni decirlo y sin cargar `escribir.md`; si su descarga no cuadra o el aviso no la trae, se escribe directo desde el plugin como dice «Los archivos del plugin en la computadora» en la skill `tablero`, nunca pegado. Con «ANTERIOR en …», su pregunta bloquea, y con «Migrar ahora», `migracion.md`.

**Propuesta de trabajo.** Dos o tres focos, de «Siguientes pasos», de «Siguiente» del `Estatus` y de los avisos, cada uno con una línea de por qué ahora: primero lo que espera otra persona (un cuestionamiento abierto el primero), después lo que cierra algo empezado y al final lo que abre frente nuevo. Si se dice cuánto lleva un foco, en tiempo de trabajo con IA y aparte lo que espera a una persona (`escribir.md`, «Plazos»). Termina con la pregunta de por cuál empezamos, con la herramienta de preguntas si está (una opción por foco, junto a la de las sugerencias), y espera.

## Lo que nunca hago al abrir

- Tocar `proyecto.md`, `sesiones.md`, `decisiones.md` o `area.md` a mano durante la sesión (`sed`, `Write`, un `cat >`): lo que se pide cambiar ahí lo escribe `cerrar.py`, al cerrar o antes si la persona quiere verlo ya (`cerrar.md`)
- Dar como aviso a alguien una decisión que leí en una carpeta restringida a la que su proyecto no pertenece
- Deducir lo que hay en una carpeta que no se deja leer: se dice qué es y de quién, y ahí se para

## Ejemplo de apertura

Sin herramienta de preguntas. La respuesta de Claude va aquí tal cual se escribe.

**Usuario:** retomamos automatización de órdenes

| Memoria de trabajo · Acme · v1.24.8 |
|---|

El proyecto busca quitar aprobaciones manuales en compras de bajo monto. La última sesión, el 14 de agosto, terminaste las entrevistas con Ana y con Finanzas y quedó pendiente decidir el criterio de corte.

| Memoria · avisos · 2 |
|---|
| Finanzas registró el 20 de agosto que el cierre pasa al día 3 y marca este proyecto como afectado · decidió Luis Romero. |
| El mapa de proceso lleva 41 días en borrador, esperando a Ana. |

Tres focos posibles para hoy:

1. Cerrar el criterio de corte por monto. Es lo que bloquea el flujo de aprobación y Finanzas está esperando.
2. Revisar si el cambio de fecha de cierre toca el flujo de aprobación antes de seguir construyendo sobre él.
3. Empujar la revisión del mapa de proceso, que lleva seis semanas parado.

¿Por cuál empezamos?
