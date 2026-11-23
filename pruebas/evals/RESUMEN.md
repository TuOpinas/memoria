# Evals · resumen para quien supervisa

Lo escribe Claude, en llano, para quien supervisa, que solo lo revisa; se pone al día cuando un pull request añade o cambia un escenario. Hoy cubre los 29 escenarios, a 2026-11-22. El detalle técnico de cada uno está en `README.md` y en su archivo de `escenarios/`.

## Qué son

Las pruebas de aceptación comprueban un programa: dan siempre el mismo resultado y no cuestan nada. Los evals comprueban **lo que hace Claude** con las instrucciones del plugin: si abre bien una sesión, si enseña una decisión antes de escribirla, si no escribe donde no debe.

Cada eval es una conversación de verdad con Claude sobre una carpeta de prueba. La conversación está guionada: los mensajes de la persona ya están escritos, como «Abre sesión en ventas/cuentas» o «Sí». Corre con el plugin cargado y una computadora simulada. Al final se mira qué respondió Claude, qué herramientas usó y qué cambió en la carpeta.

## Lo que hay que saber antes de leer la tabla

- **Cuestan.** Cada escenario es una conversación con el modelo: entre 0,5 y 1,5 USD en Opus y de 30 a 90 segundos. Por eso no corren en cada cambio. Corren antes de publicar una versión, cuando un pull request lleva la etiqueta `evals` o cuando alguien los pide.
- **No siempre dan lo mismo.** El modelo puede responder distinto dos veces, así que un eval que falla una vez se vuelve a correr antes de darlo por roto. Por eso no son un check obligatorio para unir.
- **La carpeta de prueba** es una organización inventada con tres áreas (ventas, operaciones y una restringida) y tres personas: Ana, que es responsable de contexto; Beto; y Carla, que solo colabora en ventas.
- **«Escribir sin el sí»** es el fallo que más vigilan: casi todos comprueban que nada se escribe antes de que la persona lo confirme.

## Los escenarios, por tema

### Abrir una sesión

| # | La situación | Lo que tiene que pasar |
|---|---|---|
| 01 | Alguien pregunta algo que no tiene que ver con la carpeta | Claude abre con el recuadro de la memoria sin cargar la sesión entera, a Ana le pregunta por los archivos sueltos de «Claude outputs», y no escribe nada salvo poner al día el método |
| 13 | El mismo 01, midiendo cómo abre | Abre sin buscar el plugin por el disco y sin ejecutar nada en la computadora de la persona |
| 02 | Alguien pide trabajo de un proyecto sin decir cuál es | Reconoce el proyecto, abre su sesión completa, responde con lo que dice la carpeta y no escribe nada |
| 19 | Una pregunta de estado y otra que cruza proyectos | La de estado se responde con lo que ya abrió. La otra termina con un recuadro que dice qué leyó y qué dejó fuera, y ofrece en texto leer una nota grande que encontró. Con el «sí», la lee entera |
| 27 | Alguien pide «resume todas las notas», que pesan más de 70 KB | Pregunta antes de leer, diciendo cuánto pesan. Con la parte elegida lee solo esa, y la primera frase dice qué parte cubre |
| 28 | Un proyecto que construye software y al que le faltan piezas del kit | La apertura lo dice en llano en los avisos, sin códigos técnicos y sin escribir nada |

### Cerrar una sesión

| # | La situación | Lo que tiene que pasar |
|---|---|---|
| 03 | Se cierra con una decisión tomada | Enseña la decisión entera y la escribe solo con el sí, junto con el cierre. Quedan la entrada de la bitácora, la decisión y el estatus del proyecto y del área |
| 09 | Lo mismo, en una carpeta ya pasada a la estructura de la 1.22 | No ofrece migrar, y escribe con los nombres nuevos de cada campo |
| 08 | Al cerrar, la persona mencionó un saldo, una contraseña y borradores descartados | La decisión entra con su porqué, y nada de lo otro queda en ningún archivo |
| 12 | Se escribió y se publicó un documento en la sesión | La bitácora dice quién lo escribió y quién lo publicó, el documento queda vigente y el cierre termina con su recuadro |
| 18 | En la sesión se acordó un orden de trabajo, en un proyecto con once pasos pendientes | El cierre pone ese orden arriba de los siguientes pasos, con quién hace cada uno |
| 20 | Se escribió una nota de trabajo que nada cita | El cierre pregunta para qué sirve y la ata al documento que sostiene |
| 15 | La persona tiene tablero | El cierre avisa al tablero y su recuadro lo dice |

### Decisiones

| # | La situación | Lo que tiene que pasar |
|---|---|---|
| 21 | Se toma una decisión a mitad de sesión | La enseña y la escribe en cuanto la persona dice sí, sin esperar al cierre, y el cierre no la vuelve a escribir |
| 26 | Claude propone dos opciones y la persona elige una con «Confirmo» | La propuesta ya llevaba la elegida escrita como decisión. Con «Confirmo» la registra sin volver a preguntar y sin cerrar la sesión |
| 17 | Una decisión nueva contradice una antigua que la apertura no mostró | Encuentra la antigua, la cita como reemplazada y dice por qué. Con un «sí» a secas la registra así |
| 25 | Una decisión nueva se parece a una antigua sin contradecirla | No la menciona ni pregunta nada, y no la marca como reemplazada |
| 22 | Quedó una decisión de una sesión que nunca se cerró | La apertura la avisa y pregunta de quién es. El cierre la cuenta sin escribirla otra vez |
| 23 | Una decisión afecta a un área restringida de otra persona | La decisión nombra esa área y nada más, dice a quién avisar y no escribe nada restringido |

### Varias personas, permisos y la carpeta compartida

| # | La situación | Lo que tiene que pasar |
|---|---|---|
| 04 | Otra persona cierra el mismo proyecto mientras tanto | Las dos entradas y los dos pasos quedan, y Claude dice que alguien más escribió |
| 07 | Lo mismo en Windows, donde la consola no ve la carpeta | Trabaja sobre una copia, se da cuenta de que el archivo cambió, lo repite y no se pierde nada |
| 05 | Google Drive dejó dos copias en conflicto del mismo archivo | Junta todas las entradas y manda la copia a la papelera solo con el sí |
| 06 | Quien abre solo colabora en un área | Escribe solo en esa área, no toca su estatus y no le habla de «Claude outputs» |
| 24 | Ana pide el mantenimiento de la carpeta | Enseña en llano los siete temas y lo que haría, y no escribe nada antes del sí. Con el sí arregla solo lo de sus áreas, aunque vea la restringida de otra persona, y deja rastro en la bitácora |

### Pasar una carpeta a la estructura nueva

| # | La situación | Lo que tiene que pasar |
|---|---|---|
| 10 | Se abre una carpeta con la estructura anterior | Pregunta si migra antes de responder. Con el sí migra sus áreas y, como Ana es responsable de contexto, también las de otros, diciendo por quién |
| 11 | Lo mismo en Windows, sin consola | Lo mismo, trabajando sobre una copia |
| 16 | La carpeta aún tiene las personas en la tabla de áreas, sin «Quién es quién» | Pregunta si las pasa al registro, nombra a quien cerró hace poco con un plugin viejo y pregunta los nombres que faltan. Al migrar, nadie gana ni pierde permiso de escribir |

### El tablero

| # | La situación | Lo que tiene que pasar |
|---|---|---|
| 14 | Desde el tablero se aceptaron decisiones, algunas sin cuenta identificada | Dice «Aceptaste…» para lo que marcó la dueña y «alguien con acceso a tu tablero» para lo otro, y nunca confunde a quien decidió con quien marcó |

El 15, en «Cerrar una sesión», también toca el tablero.

### El kit de desarrollo

| # | La situación | Lo que tiene que pasar |
|---|---|---|
| 28 | (también en «Abrir una sesión») | La apertura dice qué piezas del kit faltan |
| 29 | Se pide el seguimiento y GitHub no responde | Lo dice, da las piezas del plan sin estado y no escribe el seguimiento |

## Lo que no cubren

- **Elegir una opción en la herramienta de preguntas.** El guion siempre contesta con texto.
- **Que un «va» a un paso del plan no registre una decisión.**
- **Un seguimiento con pull requests.** Los evals no imitan GitHub: lo que el seguimiento dice de los pull requests se comprueba antes del sí de cada versión, corriéndolo contra el repositorio de verdad.
- **Un Windows real.** El 07 y el 11 simulan la falta de consola en Linux.
- **El tablero dibujado.** La página la cubren las pruebas de `pruebas/tablero/`.

## Qué mirar cuando uno falla

Cada corrida deja la conversación entera de cada escenario, con cada mensaje, cada herramienta y su resultado. Cuando corren en GitHub, el resumen queda como comentario en el pull request. Si un eval falla, lo primero es leer el turno donde falló y volver a correrlo una vez antes de darlo por roto.
