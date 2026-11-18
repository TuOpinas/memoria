---
name: sesion
description: Abre y cierra sesiones de trabajo sobre un proyecto. Usala cuando digan 'abre sesion', 'retomamos X', 'en que quedamos con...', 'cierra la sesion', 'guarda lo de hoy', 'terminamos' o 'cierra el proyecto', y cuando el responsable de un proyecto pregunte por el suyo: '¿como va X?', '¿en que estatus esta X?', '¿que falta en X?'. Tambien los permisos de la carpeta compartida: 'revisa los permisos', 'aplica los permisos', '¿quien puede escribir donde?'; y el mantenimiento de la carpeta: 'haz el mantenimiento de la carpeta', 'programa el mantenimiento'.
---

# Sesión

Abrir y cerrar una sesión de trabajo sobre un proyecto. Este archivo es lo que hace falta para abrir, que solo lee. Lo demás vive en anexos, junto a este archivo, y se lee cuando toca:

- `minima.md`: la apertura mínima. El aviso de arranque la inyecta en cada conversación y no hace falta cargar esta skill para ella.
- `cola.md`: la cola del tablero (lo marcado desde la página y las sugerencias), al abrir un proyecto cuando la cuenta tiene tablero y al cerrar si la cola trajo algo.
- `cerrar.md`: registrar una decisión en cuanto se confirma (1.26.4) y proponer para que un sí la registre (1.26.9), cerrar la sesión y el proyecto, y responder («lo mantengo», «lo cambio») o plantear un cuestionamiento.
- `sin-consola-sesion.md`: abrir y cerrar cuando la raíz está conectada pero el shell de la computadora no la ve.
- `migracion.md`: pasar la carpeta a la estructura de la 1.22, con «Migrar ahora».
- `premisas.md`: registrar, cambiar o retirar una premisa, en la sesión del responsable de contexto.
- `sin-carpeta.md`: abrir, consultar o preguntar al director sin ninguna carpeta conectada, leyendo la raíz en Drive.
- `permisos.md`: revisar y aplicar los permisos de Drive («revisa los permisos», «aplica los permisos»).
- `mantenimiento.md`: el mantenimiento de la carpeta en siete temas (seis de uso y la estructura), arreglar con el sí lo propio y programarlo como tarea («haz el mantenimiento de la carpeta», «haz el mantenimiento de lo mío», «verifica la carpeta», «programa el mantenimiento», 1.26.6), con el rastro de sus arreglos en la bitácora de cada proyecto (1.26.8).

Abrir solo lee. Antes de escribir cualquier cosa en la carpeta se carga el anexo `escribir.md` de `convenciones`, aunque sea una línea; para guardar un documento, mover algo o crear, `convenciones` entera.

## Cuándo

**Abrir**: «abre sesión en compras», «retomamos X», «¿en qué quedamos con X?», o cualquier trabajo sobre un proyecto existente aunque no lo nombre («guíame en el paso 4», «cambia el plugin para que…», «a un usuario le sale este error…», algo para un cliente que tiene su proyecto). Se abre antes de responder, sin preguntar y sin pedir que digan «abre sesión»; la respuesta empieza por lo que pidió, y lo de la apertura va en pocas líneas, solo lo que cambia lo que se va a hacer. También cuando el responsable de un proyecto pregunta por el suyo («¿cómo va X?», «¿qué falta en X?»): responsable es quien figura como Responsable del área en la tabla de `guia.md` (su cuenta, en «Quién es quién») o como `Responsable` en su `proyecto.md`. Si quien pregunta no es el responsable, es `consulta`. Si solo preguntó, no hay nada que cerrar.

**Durante la sesión, una decisión** (1.26.4): cuando la persona da algo por decidido («decidimos que…», «va así»), no espera al cierre: se carga `cerrar.md` («Una decisión, en cuanto se confirma») y `escribir.md`, se enseña en cita tal como quedará, y con su sí `cerrar.py` la escribe sin cerrar la sesión. Varias juntas, un solo sí. También decide un sí a opciones que propuso Claude («Confirmo», «va», una opción elegida en la herramienta de preguntas) cuando elige entre alternativas y compromete lo que se va a hacer o construir (1.26.9): por eso `cerrar.md` y `escribir.md` se cargan antes de cerrar una propuesta así, que termina en «Para confirmar» con cada punto que elige ya en cita, y su sí la escribe en ese turno; no decide aprobar que se construya algo ya decidido, un paso del plan sin alternativa, el foco de hoy, cuánto se lee ni un permiso (`cerrar.md`, «Al proponer»).

**La raíz** es la carpeta conectada con `guia.md` y `metodo.md` en su primer nivel. A `abrir.py` se le pasa la ruta que da `get_device_info`: si en la consola la carpeta cuelga de `$HOME/mnt/…`, el script la resuelve y la imprime en su línea RAIZ, que es la que se usa después, sin `ls` ni `find`. Nunca se dice que no hay carpeta sin haberlas listado; si no hay ninguna, `sin-carpeta.md`. Con más de una raíz, se pregunta en cuál se trabaja y la sesión se queda en esa (lo de otra entra solo por un traspaso, `raices.md` junto al contrato). Si no queda claro el proyecto, se pregunta; nunca se asume el último usado.

## Apertura mínima

La hace la conversación con lo que trae el aviso de arranque, sin esta skill, y siempre igual, con consola o sin ella: lista la raíz, trae una copia de lo que lee y corre `abrir.py` en el contenedor, desde el plugin instalado (1.24.9). En la computadora no ejecuta nada descargado, que el modo Auto frena cuando la petición no tiene que ver con la memoria. Se sigue aquí cuando el aviso fue el corto o no trajo PLUGIN, o cuando el control del plugin la pide: se lee `minima.md`, junto a este archivo, con `<directorio de esta skill>/../..` como PLUGIN y la primera línea de su `metodo.md` como METODO; lo que diga la sección RESPUESTA de `abrir.py` es lo que se hace. Nunca en una tarea programada.

## Abrir sesión

### Qué leo, y en cuántas llamadas

`abrir.py`, junto a este archivo, lee de una vez lo que dice la sección 12 de `convenciones` (nivel 0, nivel 1 y el barrido de avisos) y no escribe nada. Nunca abre el cuerpo de `taller/` ni de `fuentes/`, ni `restringido/` (del taller del proyecto solo mira cabeceras y tamaños, y de `fuentes/` las filas de su inventario), de otros proyectos solo mira las líneas `Afecta a:`, `Cuestiona a:` y `Responde a:`, y lo restringido no sale salvo que el proyecto activo esté dentro.

1. **La descarga**: METODO viene al final del aviso de arranque (si hay dos avisos, el de versión más alta); DESCARGA se calcula aquí, con Bash en el contenedor, un comando simple y sin `find` ni redirecciones: `python3 "<PLUGIN del aviso, o el directorio de esta skill con ../..>/preparar.py" '$HOME/memoria' skills/sesion/abrir.py skills/sesion/cerrar.py`, que imprime VERSION, METODO, DESCARGA y REINTENTO (desde la 1.25.1 el aviso no las trae: solo las paga quien abre un proyecto). Se usa lo que va detrás de «DESCARGA » y su espacio; REINTENTO es lo mismo con `main` en lugar de `v<versión>`.
2. **Con device_bash, en la computadora, directo con el proyecto**: lo que va detrás de «DESCARGA » seguido de ` && python3 abrir.py "<ruta de get_device_info>" <area>/<proyecto> --cuenta <correo> --plugin "<la línea METODO sin «METODO »>" --origen "<la misma ruta>"`. Si ya se descargó en esta conversación, basta `cd $HOME/memoria && python3 abrir.py …`. Si la petición nombra el proyecto, aunque sea con otras palabras, o se reconoce en la lista de proyectos de la mínima, se corre ya con él; sin proyecto (imprime `guia.md` y la lista) solo cuando de verdad no se sabe cuál es. Si la comprobación falla, una vez con REINTENTO; un script que no la pasa no se ejecuta nunca, ni se pega su contenido en un comando. Sin un `abrir.py` comprobado, se carga `convenciones` y se lee por los niveles de su sección 12, `metodo.md` no se toca y se dice en media línea. Su sección RESPUESTA dice qué hacer con el método, la estructura, los permisos y «Claude outputs»: lo que la apertura mínima ya hizo o preguntó en esta conversación no se repite.
3. **La cola del tablero**, si la sesión tiene el conector de artifacts y la cuenta tiene tablero (lo pide la RESPUESTA): `cola.md`.

Lo que la apertura mínima no cargó va en un solo ToolSearch al empezar: `device_bash`, `device_request_delete_permission` y las del tablero que pide la RESPUESTA, más `db_get`, `db_write` y `publish_files`; `device_commit_files` solo cuando la RESPUESTA lo pide (la raíz atrasada).

## Qué respondo

La apertura son unas pocas llamadas seguidas, sin mensajes entre ellas, y la respuesta llega entera al final. Si hay SendUserMessage, todo lo que va antes de una herramienta de preguntas se manda con él.

**El recuadro.** La primera vez en la conversación, la respuesta empieza con el recuadro que trae la sección RESPUESTA de `abrir.py`, tal cual: una tabla de Markdown de una columna con la cabecera «Memoria de trabajo · <organización> · v<versión>» y solo las filas que piden algo (sin ninguna, basta la cabecera). Si ya salió, no se repite, y una pregunta que ya se hizo en la conversación tampoco. El cierre termina con un recuadro como este (`cerrar.md`). Toda tabla de la memoria sigue la misma regla: nunca un bloque de código ni un recuadro dibujado, y sus celdas sin saltos de línea ni «|» (se cambian por «·»).

Después, estos bloques, en este orden y sin encabezados largos.

**Dónde quedó todo.** Cuatro o cinco líneas: el objetivo en una frase, qué se hizo en la última sesión y qué sigue. Si SESIONES trae «arreglos del mantenimiento desde tu última sesión aquí», una frase en llano: qué arregló el mantenimiento y cuándo (1.26.8). Si la sesión se abrió por una pregunta de estado, este bloque es la respuesta y empieza por el `Estatus`, diciendo si hubo sesiones después de su fecha.

**Lo que viene de la memoria va en recuadros**, para que se distinga de lo que escribe Claude: una tabla por bloque con la cabecera «Memoria · <qué es> · <cuántos>», una fila por cosa con lo que dice y de dónde sale. Lo que dice Claude va debajo, en texto normal. Solo salen los que traen algo, en este orden: lo marcado en el tablero y las sugerencias (`cola.md`) y los avisos.

**Avisos**: recuadro «Memoria · avisos · <cuántos>», una fila por cada línea de la sección AVISOS de `abrir.py`, en el orden en que las da (lo que espera a alguien va primero) y en llano. Una copia en conflicto se junta antes de seguir (`cerrar.md`); un trabajo sin sesión se pregunta qué pasó y se propone registrarlo hoy, con quien lo hizo en «Sesión de:»; unas «Decisiones sin sesión» (1.26.4) ya están registradas: no se vuelven a escribir, y la entrada de hoy dice que se tomaron en una sesión que no se cerró. Además, y esto no lo calcula el script, una decisión reciente de este proyecto que choca con una premisa vigente, sin darlo por resuelto. Sin avisos, no se menciona que no los hay.

**El método y la estructura** los resuelve la RESPUESTA, sin comparar a mano. Con «RAIZ ATRASADA», lo abra quien lo abra, se escribe el `metodo.md` del plugin sin preguntar ni decirlo y sin cargar `escribir.md`, como dice la RESPUESTA: sin descargar nada en la computadora, con `device_commit_files` desde una copia hecha en el contenedor (`abrir.py --metodo-para-subir`); si esa copia no sale, no se pone al día en esta conversación y no se dice: lo hará la siguiente apertura o la puesta al día del tablero. Nunca se descarga en la computadora ni se pega. Con «ANTERIOR en …», su pregunta bloquea, y con «Migrar ahora», `migracion.md`.

**Cuánto se lee después** (1.26.3; lo que se ve, 1.26.10). La sección INVENTARIO de `abrir.py` dice lo que la apertura no imprimió y cuánto pesa, y ENTREGABLES el tamaño de cada entregable. Con eso, Claude decide en cuál de estos tres niveles se responde cada pregunta de la sesión; los niveles son su criterio, y sus nombres no salen en lo que ve la persona:

| Nivel | Qué se lee | Para |
|---|---|---|
| Básico | lo que imprimió la apertura | el estado, lo que sigue, lo que se decidió hace poco |
| Proyecto | además, `decisiones.md` vivo, de sus archivados solo las entradas que la pregunta pide (buscadas por su título), los pasos sin imprimir y las notas de `taller/` que la pregunta nombra, por su cabecera antes que por su cuerpo | por qué se decidió algo, qué se probó, de dónde sale un entregable |
| A fondo | además, los cuerpos que la pregunta necesita y la superficie pública de otros proyectos (su `Estatus`, sus decisiones y sus entregables vigentes) | un análisis, algo que cruza proyectos o áreas |

Se carga sin preguntar hasta unos 50 KB por encima de la apertura, con los tamaños del INVENTARIO y de ENTREGABLES; lo que no trae tamaño (otros proyectos, una nota fuera de las cinco) se mide antes de cargarlo. El tope se mide contra todo lo que la pregunta pide, no contra lo que Claude elegiría cargar: «resume todas las revisiones» pide todos los informes (1.26.10). Lo que pasa de los 50 KB se trata de una de dos formas, según lo pida o no la petición:

- **Lo que la petición nombra o enumera** («todas las revisiones», «el informe X»), o aquello sin lo que no hay respuesta: se pregunta antes de leer nada, con la herramienta de preguntas si está y en texto si no, una opción por forma de leer, cada una con su tamaño y su tiempo (todo; la parte que Claude propone, diciendo cuál). Si al final se responde con una parte, porque la persona la eligió o porque no hay nadie a quien preguntar, la primera frase de la respuesta dice qué parte cubre, y el recuadro nombra el resto en «Dejé fuera:» sin volver a ofrecerlo.
- **Lo que Claude encuentra y la petición no nombra**, que podría completar la respuesta: se responde con lo demás y se ofrece debajo del recuadro, pese a lo que pese.

El tiempo, a ojo y sin medir: «enseguida» hasta unos 100 KB; por encima, por partes y varios minutos, y por encima de unos 200 KB «todo» no se ofrece de una vez, sino por partes.

**El recuadro de lectura** (1.26.10). La respuesta a una pregunta que leyó en este turno algo más que lo que imprimió la apertura termina con un recuadro, después de la respuesta: «Memoria · lectura · <de dónde leyó>», con lo leído nombrado en llano («este proyecto»; «este proyecto y product-design»), nunca con el nombre del nivel. Dos filas:

- **«Leí:»** qué leyó, por lo que es y no por su ruta, y cuánto pesa en total.
- **«Dejé fuera:»** lo que hay y no abrió: qué es y cuánto pesa, y, de lo que puede tratar de la pregunta, qué podría aportar. Solo lo que esta sesión puede leer: del proyecto activo, todo salvo lo restringido sin acceso; de otros proyectos, su superficie pública. Lo demás se nombra como mucho por su sitio («el taller de soporte no se lee desde aquí»), sin tamaño ni lo que diría. Que nada trata de esto se dice solo de lo que se miró por su cabecera o su título («los informes de revisión, que por su título son de otras versiones; nada de eso trata de esto»); lo que no se pudo contar, sin consola el taller y `fuentes/`, se dice así («el taller no se pudo contar desde aquí»).

Por ejemplo, tras responder si el criterio de corte de compras cuadra con lo que decidió Finanzas:

| Memoria · lectura · este proyecto y Finanzas |
|---|
| **Leí:** las decisiones del proyecto, y el estatus y las decisiones de Finanzas · 14 KB |
| **Dejé fuera:** las entrevistas con Finanzas del taller (70 KB), con sus cifras de conciliaciones: pueden mostrar que el tope de 5.000 MXN se queda corto |

¿Leo también las entrevistas con Finanzas? Son 70 KB: enseguida.

Debajo del recuadro, y solo cuando lo que quedó fuera puede cambiar o completar la respuesta, la pregunta de si se lee: en texto, en una línea, con qué leería, cuánto pesa y cuánto tarda. En texto y no con la herramienta de preguntas, porque sigue a una respuesta ya dada: así queda bajo el recuadro, donde se mira, y no bloquea la pregunta siguiente. Si la fila dice que nada trata de esto, no se pregunta. Con un «sí», la respuesta siguiente lee lo que ofreció, y solo eso, entero, y responde otra vez con su recuadro. Un aviso de que algo puede estar resuelto en lo que no se abrió es justo lo que pide la pregunta. El recuadro se queda aunque la persona pida respuestas breves: se acorta lo de alrededor. Lo que nombra puede ir como enlace, con su nombre en llano como texto.

No lleva recuadro, ni pregunta, lo que solo usó la apertura ni lo que no es la respuesta a una pregunta: el cierre, la respuesta que pide el sí para escribir (una decisión, «Para confirmar», un cuestionamiento), los turnos de trabajo que leen para editar y lo que corre sin nadie delante. Si lo que quedó fuera podría cambiar una propuesta, se lee, o se pregunta, antes de proponer; así un «sí» nunca contesta a la vez a una lectura y a un registro.

**Propuesta de trabajo.** Dos o tres focos, de «Siguientes pasos», de «Siguiente» del `Estatus` y de los avisos, cada uno con una línea de por qué ahora: primero lo que espera otra persona (un cuestionamiento abierto el primero), después lo que cierra algo empezado y al final lo que abre frente nuevo. Si se dice cuánto lleva un foco, en tiempo de trabajo con IA y aparte lo que espera a una persona (`escribir.md`, «Plazos»). Termina con la pregunta de por cuál empezamos, con la herramienta de preguntas si está (una opción por foco, junto a la de las sugerencias), y espera.

## Lo que nunca hago al abrir

- Tocar `proyecto.md`, `sesiones.md`, `decisiones.md` o `area.md` a mano durante la sesión (`sed`, `Write`, un `cat >`): lo que se pide cambiar ahí lo escribe `cerrar.py`; una decisión, en cuanto la persona la confirma (1.26.4; también con un sí a una propuesta, 1.26.9), y lo demás al cerrar o antes si la persona quiere verlo ya (`cerrar.md`)
- Dar como aviso a alguien una decisión que leí en una carpeta restringida a la que su proyecto no pertenece
- Deducir lo que hay en una carpeta que no se deja leer: se dice qué es y de quién, y ahí se para
- Escribir nada en una raíz cuya «Versión mínima del plugin» es más nueva que este plugin (fila «Solo lectura» del recuadro, 1.26): se lee y se consulta, y lo que habría que escribir se prepara en la conversación hasta que la persona actualice

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
