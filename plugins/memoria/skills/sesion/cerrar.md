# Cerrar sesión y cerrar el proyecto

Anexo de la skill `sesion`. Se lee al cerrar («cierra la sesión», «guarda lo de hoy», «terminamos», «cierra el proyecto»), y antes se carga el anexo `escribir.md` de la skill `convenciones`, que hasta aquí no hacía falta: cerrar escribe en la carpeta y sus prohibiciones aplican a todo lo que sigue. Con él basta, salvo que el paso 1 o el 7 guarde o mueva un archivo, que pide además `convenciones` entera (nombres, entregable o taller, `fuentes/inventario.md`, material sensible), o que haya un traspaso (paso 8), que pide `raices.md`.

## Cerrar sesión

### Qué escribo y dónde

**Las reglas del área, antes que nada.** El bloque `Proyectos` del `area.md` del proyecto (que `abrir.py` imprimió al abrir) y las reglas propias de la casa de `guia.md` pueden pedir algo al cerrar, como poner al día la fila de un pipeline o la ficha de otro proyecto del área. Se cumple en este mismo cierre, como un paso más y dentro de lo que la cuenta puede escribir; si pide escribir en un área de otra cuenta, se prepara el texto y se dice a quién pasárselo.

**Cómo se escribe: con `cerrar.py`, en dos llamadas: `--comprobar` antes de enseñar la entrada (paso 2) y la que escribe.** La sesión prepara los textos y `cerrar.py` (junto a este archivo; llegó a la computadora con `abrir.py` en la llamada 1 de abrir, y si no está, se trae igual que él) los escribe. Un `cambios.json` con la forma que dice su cabecera: la entrada de `sesiones.md` (paso 2, con el formato de `escribir.md`: `## AAAA-MM-DD` y la última línea «Sesión de»), los documentos que la sesión escribió y los que publicó (`escribio` y `publico`, paso 2), las decisiones confirmadas (paso 3), el `Estatus` entero (`estatus`) y los reemplazos exactos de `proyecto.md` (paso 4), la línea del proyecto y las de sus entregables vigentes en `area.md` (paso 5), el `Estatus` del área (`estatus_area`, paso 10) y, si una regla del área pide tocar otro archivo del área, sus reemplazos en «otros». Con consola: el JSON con un heredoc en `$HOME/memoria/` (fuera de la raíz) y, en la misma llamada de device_bash, `cd $HOME/memoria && python3 cerrar.py "<la línea RAIZ de abrir.py>" <area>/<proyecto> cambios.json --cuenta <correo de la cuenta> --abierto <el valor de la línea «ahora» de REGISTROS de abrir.py>`. Sin consola, como dice `sin-consola-sesion.md`.

De cada archivo el script hace leer → cambiar → escribir bajo un cerrojo y, justo antes de escribir, comprueba que el archivo sigue como lo leyó; si cambió entre medias, vuelve a leer y aplica lo de esta sesión sobre lo nuevo. Así dos personas que cierran a la vez sobre el mismo proyecto, o dos sesiones de una misma cuenta, no se pierden una entrada ni un paso: cada entrada va encima de lo que haya y cada reemplazo se aplica sobre lo que está en el disco. Si la raíz pide una versión del plugin más nueva que la de este script («Versión mínima del plugin» de `guia.md`, 1.26), no escribe nada, ni con `--comprobar`: sale con 6 y un `error` con el motivo y cómo actualizar, que se dice tal cual; la sesión no se cierra hasta actualizar, y lo que había para escribir se deja preparado en la conversación. Si algo no cumple (la forma de una entrada, una fecha que no es la de hoy o ayer en la zona de la organización, «otros» fuera del área, un nombre de antes de la 1.22, lo que la cuenta no puede escribir), lo rechaza con su motivo. Lo que devuelve, con `respuesta` primero (1.25.1: lo que la conversación hace con esta salida en cuanto la lee, con la marca del tablero ya armada y los avisos en llano; se sigue tal cual, en su orden; una salida con `error` no la trae, porque no escribió nada y se arregla primero): `escritos`; `sin_match` (un reemplazo que no cuadra, porque su texto viejo no aparece exactamente una vez, cruza un encabezado o pasa de doce líneas: se relee ese archivo, se parte o ajusta el reemplazo y se repite la llamada solo con él, pasando en `--abierto` la `escrito_en` que devolvió la anterior); `rechazados` (lo que la cuenta no puede escribir o un archivo que encogería a menos de la mitad: se prepara el texto y se le pasa al responsable, o `--forzar <ruta>` solo si el recorte es a propósito); `fallidos` (un archivo que no se pudo leer o escribir, con el motivo: se dice y no se repite a ciegas); `ajenos` (archivos que alguien cambió desde la apertura o mientras este cierre escribía, con la hora en la zona de la organización: se dice en media línea al terminar, «alguien escribió proyecto.md a las 10:03; sumé lo de hoy encima»); `sin_nombrar` (con `--abierto`: documentos de `entregables/` o `taller/` que cambiaron desde la apertura y no van en `escribio` ni en `publico`; con la llamada `--comprobar` del paso 2 no debería quedar ninguno, y si queda, otra persona trabajó en el proyecto y se dice como `ajenos`; nunca se nombran en una sesión posterior, que los atribuiría a otra fecha y quizá a otra persona); `no_publicado` (1.24.2: un documento de `publico` que no quedó vigente tras los reemplazos de «otros», por un `sin_match`, un rechazo o un fallo al escribirlo; sale con `error` y no se escribió la entrada ni lo demás, solo «otros» y, si tocaba, la rotación: se arregla y se repite la llamada sin los reemplazos de «otros» que ya salieron en `escritos`, y escribe la entrada una sola vez); `reintentos`; `hora` y `documento` (para la marca del tablero, paso 11); `escrito_en`. Lo que el cierre escribe pasa por el script: nunca con `Write`, `Edit`, `sed -i` ni un `cat >`, que pueden pisar lo que otra persona escribió. Si durante la sesión la persona quiere ver ya escrito un cambio de `proyecto.md`, se escribe con `cerrar.py` y solo `reemplazos`, sin entrada de bitácora; su `respuesta` dice entonces que la sesión sigue abierta, sin marca del tablero ni recuadro de cierre. Lo único que se escribe fuera de él, antes de llamarlo, es juntar una copia en conflicto (abajo), que funde archivos enteros como dice `escribir.md`; la rotación (paso 9) la hace el propio script. Esto cierra la ventana entre leer y escribir en esta computadora; lo que la otra persona escribió y Drive aún no bajó no se ve: si los dos llegan a escribir a la vez, Drive guarda las dos versiones, y la siguiente apertura las junta («Copias en conflicto»).

**Copias en conflicto.** Cuando abrir sesión avisa de una copia en conflicto («sesiones (1).md», «proyecto [Conflict].md» junto a su original), se junta antes de cualquier otra cosa, porque hasta entonces una de las dos versiones no la lee nadie. Se leen las dos. En `sesiones.md` y `decisiones.md`, que solo crecen, se juntan las entradas de las dos, sin repetir ni editar ninguna, en el orden del archivo. En un archivo vivo (`proyecto.md`, `area.md`, `guia.md`) se le enseña a la persona lo que difiere entre las dos y se escribe lo que ella decida. Se escribe en el original, siguiendo `escribir.md`, y la copia va a la papelera con su sí: con consola, se pide el permiso de borrar; sin consola, con el conector (`sin-consola.md`). Se dice en una línea. Un archivo en conflicto de un área donde la cuenta no escribe se le dice a su responsable, y no se toca.

**Si la cuenta colabora y no es la del responsable** (sección CUENTA EN EL PROYECTO de `abrir.py`), cierra igual: bitácora, decisiones de su trabajo con su nombre en `Decidió`, `Estatus` y `Siguientes pasos`. No publica nada, ni toca el `Estatus` del área ni la línea `Colabora:` de `Quién participa` (`convenciones`, sección 1, «Quién colabora»). Si colabora solo en este proyecto y no puede escribir `area.md`, la línea del paso 5 se prepara y se le pasa al responsable del área.

**Qué entra y qué no.** Antes de preparar `cambios.json`, lo que la sesión trae se pasa por «Qué guarda el cierre y qué no» de `escribir.md`; ante la duda se pregunta en el mismo mensaje que enseña las decisiones.

**0. La cola del tablero**, si se leyó al abrir: se resuelve como dice «Al cerrar» de `cola.md`.

**1. Lo que se hizo y aún no está en la carpeta.** Lo producido se guarda al crearlo, así que esto no debería pasar; si algo de la sesión (un documento, un PDF, un análisis) solo existe en la conversación, se guarda ahora en `entregables/` o en `taller/` como borrador, antes de registrar nada. Lo mismo con lo que la app haya dejado en «Claude outputs» durante esta sesión: se mueve a este proyecto y deja de estar ahí.

**2. `sesiones.md`.** Entrada nueva arriba del todo, que se enseña junto a las decisiones y el `Estatus` antes de escribir, fechada con la línea HOY de `abrir.py`, con el formato de `escribir.md` (sección 4), sin tocar las anteriores: «Tema» y «Avances», más la de quién trabajó y con qué versión del plugin (la de `plugin.json`, la misma que la llamada 1 de abrir; quien trabaja sin el plugin escribe con qué lo hizo, por ejemplo «sin plugin, Gemini»). Lo que sigue no va aquí: va en «Siguiente» del `Estatus`. Si una sesión no cabe en esas líneas, es que hubo decisiones y esas van a su archivo.

Quién escribió y quién publicó lo pone `cerrar.py`: en `escribio`, cada documento de `entregables/` o `taller/` del proyecto que la sesión creó o cambió en su contenido (no los que solo leyó, ni una `aportacion` añadida a una cabecera); en `publico`, cada entregable que la skill `revisar` pasó a `vigente` en esta sesión (el paso a `vigente` puede ir en «otros» de la misma llamada); rutas dentro del proyecto. No se teclean en el texto de la entrada: el script rechaza una «Escribió:» o «Publicó:» escrita a mano y, con cualquiera de las dos listas, una entrada sin «Sesión de: Nombre». **Antes de enseñar la entrada**, una llamada con `--comprobar` (y el mismo `--abierto`) valida sin escribir la forma de las entradas y la autoría, y devuelve la entrada tal como quedará, con sus líneas, y `sin_nombrar` (sin consola no lo hay, porque las fechas de la copia no dicen nada; los reemplazos y los permisos se comprueban en la llamada que escribe): lo que cambió desde la apertura y no va en las listas. Si es de esta sesión, se añade a `escribio`; si no, es de otra persona y se dice. Lo que se enseña para confirmar es esa `entrada`.

**3. `decisiones.md`, solo si hubo decisiones.** Antes de escribir, se enseñan al usuario las decisiones detectadas, cada una como va a quedar escrita (abajo, «Cómo se enseña antes de escribir»), y se pide confirmación explícita; la respuesta termina ahí y el cierre sigue en el turno siguiente, con el sí. También cuando la persona dictó la decisión en el mismo mensaje en que pide cerrar: dictarla no es confirmar la entrada. El registro no se puede corregir después, así que nada entra sin que alguien lo confirme. Con el formato de `escribir.md` (sección 4), y con su ejemplo al final de este anexo. `Descartado`, `Reemplaza` y `Afecta a` van solo si hay algo que decir: nunca «no consta» ni «ninguno».

Si el extracto de la sesión sugiere que una decisión sustituye a otra anterior («antes…», «ya no…», «en vez de…»), se pregunta por su `Reemplaza:` en el mismo mensaje que la enseña.

**Cómo se enseña antes de escribir**. La respuesta que pide el sí lleva estos bloques, en este orden y cada uno con su palabra sola encima, en texto normal y con estas palabras exactas, sin cambiarlas ni ampliarlas: «Decisiones» (si las hay, y ahí también un cuestionamiento que se plantea o se responde), «Bitácora», «Estatus» y, si tocan, «Estatus del área» y «Lo que se escapó» (paso 4b), este último antes de la pregunta final. Dentro, cada pieza va en una cita con barra lateral (`>` delante de cada línea) y tal como va a quedar escrita, sin resumirla ni traducirla: una cita por decisión, con su línea `## AAAA-MM-DD · título` (sale como título dentro de la cita, y es lo que se quiere) y debajo sus campos (`Decidió`, `Por qué`, `Descartado`, `Afecta a`…), cada uno empezando en su línea, y un `Por qué` de varios párrafos con una línea `>` vacía entre ellos, como en el archivo; la entrada de la bitácora, la que devolvió `--comprobar`, con su `## AAAA-MM-DD`; y el `Estatus` entero. Los reemplazos de «Siguientes pasos» y la línea del área van debajo, en una o dos líneas en llano, porque son cambios en un archivo vivo y no registro. La respuesta termina con la pregunta en texto («¿Lo registro así?»), no con la herramienta de preguntas; si hay `SendUserMessage`, las citas y la pregunta van con él. Nunca una lista que resume las decisiones en lugar de enseñarlas, ni un bloque de código, tampoco en un cliente que no pinta Markdown. Esto vale aunque la persona pida respuestas breves: es lo único que confirma de un registro que no se corrige, así que se acorta el texto de alrededor y nunca las citas. Lo mismo vale fuera del cierre para todo lo que se enseña antes de escribirlo en un registro o en un `Estatus`: un cuestionamiento del director, el `Estatus` del área, una premisa.

**Responder un cuestionamiento.** Si al abrir se avisó de un cuestionamiento abierto a este proyecto y lo respondió en la sesión el responsable, o quien colabora si la decisión cuestionada es suya (lo dicen CUENTA EN EL PROYECTO y el `Decidió` de la decisión), la respuesta es una decisión más de esta lista, aunque solo mantenga lo que ya estaba: «lo mantengo» cambia algo, porque cierra una pregunta que alguien tenía abierta. La entrada lleva `Responde a: <identificador del cuestionamiento>` (el que se citó al abrir), dice en el título si mantiene o reemplaza lo cuestionado, y en `Por qué` la razón que dio el responsable. Se confirma como cualquier decisión y se dice a quién avisar: a quien lo planteó. Además, Claude se lo enseñará a esa persona la próxima vez que abra sesión en su proyecto.

**Plantear un cuestionamiento.** Con la forma de `escribir.md` («Cuestionamientos»), en el `decisiones.md` del proyecto activo, enseñado y con su sí, como una decisión; se dice a quién avisar.

Una decisión es un compromiso que cambia lo que se va a construir. Una preferencia expresada en voz alta no lo es. Ante la duda, se pregunta.

Antes de confirmar, si el título o el `Por qué` nombran un `area/proyecto` de la raíz que no está en `Afecta a`, se propone añadirlo: sin esa línea, su responsable no recibe aviso.

Si `Afecta a` nombra un proyecto de otra área, se dice al usuario a quién tiene que avisar: el responsable de esa área, según `guia.md` o su `area.md`. La carpeta no notifica a nadie y la skill tampoco.

Si el proyecto activo lo lee todo el equipo y la decisión toca a un área o a un proyecto restringido, `Afecta a` lleva su nombre y nada más, porque ese nombre ya está listado: ni sus archivos, ni lo que contiene. Al revés, una decisión que se registra dentro de una carpeta restringida sí puede nombrar cualquier proyecto al que afecte.

**4. `proyecto.md`.** Se ponen al día `Estatus` y `Siguientes pasos`. A una persona de fuera de la organización se la nombra en ellos como dice `escribir.md` («Personas de fuera»): «Nombre Apellido (Organización)» al menos una vez. Es un archivo vivo: lo que deja de ser cierto se sustituye, no se acumula. `Siguientes pasos` se edita, no se vuelve a escribir entero: se quitan los pasos hechos, se añaden los nuevos y se cambian solo las frases que la sesión dejó viejas, con reemplazos exactos (los `reemplazos` de `cambios.json`). Un reemplazo que no cuadra vuelve en `sin_match` (arriba).

El `Estatus` se reescribe entero desde lo que pasó en esta sesión, con la plantilla de las cuatro preguntas (qué se completó, qué sigue, qué falta decidir, qué preocupa) y la forma y la voz que da `escribir.md` (sección 3 y «La voz del `Estatus`»); lo lee todo el equipo, en la carpeta y en el tablero de cada uno, así que nada de `restringido/` ni datos personales. **Se enseña antes de escribir**, en el mismo mensaje que la entrada de la bitácora y las decisiones, y se escribe con el sí de la persona, como ellas; si pide cambiarlo, se cambia y se vuelve a enseñar. El `Estatus` lo escribe la sesión, nunca el tablero.

**4b. Lo que se escapó.** Si en la sesión apareció un fallo en algo que ya pasó por una revisión de calidad (en el uso real, en otra revisión, en una prueba o en los evals), se propone su línea de «Lo que se escapó» (skill `calidad`, paso 7). Si el informe es de este proyecto, la sesión la escribe en él (es un archivo vivo de su taller, y va en «escribio»); si es de otro proyecto u otra raíz, se le prepara a la persona para que se la pase a su responsable. Si el proyecto tiene informes en `taller/revisiones-de-calidad/` (basta su listado, sin abrirlos), la sesión cambió código o corrió pruebas o evals, y nadie habló de fallos, el mensaje que se enseña lleva el bloque «Lo que se escapó» con una sola línea: «Si algo de lo ya revisado falló, dímelo y lo apunto». Callar es que no. Sin esa línea no se puede saber qué se le escapa a cada revisión (1.26.2).

**5. Bloque `Proyectos` de `area.md`.** Se reescribe la línea de este proyecto y, debajo, una línea por cada entregable `vigente`, que es su `aportacion` con su fecha `actualizado`: en `cambios.json` cada entregable va como `{"archivo": "x.md"}` y `cerrar.py` arma la línea desde su cabecera; solo un entregable sin `aportacion` va con la línea escrita. Solo esa parte del bloque; las líneas de los demás proyectos no se tocan.

**6. Cabeceras de lo que se tocó.** `actualizado` lo pone `cerrar.py` en cada archivo que escribe; si se usó una fuente nueva, se añade a `basado_en` con un reemplazo exacto sobre la cabecera (en los `reemplazos` de `proyecto.md`, o en «otros»).

**7. Lo que entró en `fuentes/` o en `taller/`.** Si durante la sesión se guardó algo en `fuentes/` sin haber pasado por la pregunta de si es confidencial, se pregunta ahora: si trae datos personales, facturación, contratos, credenciales o cualquier cosa que no todos deban ver, se propone llevarlo a `restringido/` del mismo proyecto y dejar su fila en el `fuentes/inventario.md` público. El usuario decide; nada se mueve sin que lo confirme.

**8. Traspasos.** Si en la sesión entró algo de otra raíz, la entrada de `sesiones.md` lo dice: qué vino, de qué raíz, quién lo pidió. Lo que se quedó fuera no se nombra.

**9. Rotación.** La hace `cerrar.py` antes de escribir la entrada de hoy: si `sesiones.md` o `decisiones.md` pasa de 1.500 líneas o de 100 KB, o su entrada más nueva es de un año anterior, lo archiva entero como `<registro>-<año>.md` y abre uno nuevo con la línea «Archivado:» (`escribir.md`, sección 8), y lo devuelve en `rotados`. Se dice como una fila más del recuadro del cierre, en llano: «decisiones-2026.md · las decisiones anteriores se archivaron aquí; se siguen leyendo y citando igual». Sin consola, como dice `sin-consola-sesion.md`.

**10. El `Estatus` del área.** Se reescribe el `Estatus` de `<area>/area.md` con la forma y la voz que da `escribir.md` (sección 2, «Estructura de `area.md`»): cómo está el área después de esta sesión, con sus prioridades debajo de «Siguiente» y una línea por proyecto activo. Al cerrar no se relee el área: se parte del `Estatus` anterior del área y de lo que esta sesión ya leyó y escribió, y de los demás proyectos del área solo se mira, en una sola llamada, la cabecera y el `Estatus` (o «En corto», sin migrar) de los que tienen `actualizado` posterior a la fecha del `Estatus` del área, o de todos si no había uno con fecha. Las prioridades se quedan como estaban salvo que el responsable del área las cambie en esta sesión. Se enseña con el `Estatus` del proyecto y va en la misma escritura de `area.md` que el paso 5. Solo si la cuenta que cierra es la del responsable del área; si solo colabora, o el área es de otra cuenta, se salta.

**10b. Los permisos, si cambiaron.** Si la cuenta es la del responsable de contexto y en esta sesión cambió quién escribe o qué se restringe (un área nueva, alguien añadido como responsable o colaborador, algo declarado restringido, una carpeta `restringido/` nueva), al final del cierre se propone en una línea revisar que Drive coincide, y con su sí se sigue `permisos.md`.

**11. El tablero, avisado.** Lo dice el primer paso de `respuesta` de `cerrar.py`, con la escritura ya armada: si la cuenta tiene tablero (el que se buscó al abrir; si no se buscó, `list_artifacts` ahora), se apunta el cierre en su base antes de responder, sin preguntar ni decir nada, con `db_write` del conector `claude-artifacts` (se carga con `ToolSearch` si hace falta): un `set` en la colección `cierres` con ese documento (`<area>--<proyecto>--<AAAAMMDDHHMM>`, nuevo en cada cierre, así que no lleva `ifVersion`) y los campos `proyecto`, `nombre`, `hora` (la que devolvió `cerrar.py`, tomada del reloj y nunca calculada a mano; una hora adelantada deja el aviso del tablero encendido hasta que llega) y `cuenta`. Si la cuenta tiene dos tableros de esa raíz (de antes de la 1.18), en los dos. La tarea no se lanza desde la conversación, salvo que la persona lo pida («cierra y pon al día el tablero»): entonces se lanza con `fire_trigger`: con `list_triggers` (`enabled: true`, siguiendo `next_cursor`) se busca la tarea cuyo prompt lleva la URL del tablero, y se dispara si su aprobación es automática (`permission_mode` `auto`) y su carpeta (`derived_state.folders`) es la raíz conectada; la app pedirá permiso y la persona lo da. Si el tablero no tiene tarea o la cuenta no tiene el conector de tareas programadas, el botón no puede ponerse al día: entonces se pone al día aquí mismo, como «Sincronizar» de la skill `tablero`. Si la escritura falla o la app la frena, la sesión queda cerrada igual y la fila del tablero del recuadro lo dice (abajo): el tablero se pondrá al día con su botón o con «sincroniza el tablero».

### Qué respondo al terminar

Lo que escribió el cierre va en un recuadro como el de la apertura, con la cabecera «Memoria · sesión cerrada · <n> archivos» (los `escritos` de `cerrar.py`, que ya incluyen el archivado si hubo rotación, más la copia en conflicto si se juntó una) y una fila por archivo, con su enlace (`computer://`, como cualquier archivo que se nombra en la conversación) y en pocas palabras qué cambió en él, y una última fila para el tablero, siempre: «Tablero: avisado», «Tablero: no se pudo avisar (<motivo>): sincronízalo desde su botón o con «sincroniza el tablero»», «Tablero: sin el conector de artifacts en esta conversación: sincronízalo desde su botón» o «Tablero: esta cuenta no tiene» (1.25.1: un cierre dejó la marca sin escribir y nadie lo vio). Debajo, en texto normal y solo si hay algo: qué queda para la próxima en una línea, a quién avisar de otra área, lo que quedó en `fuentes/` pendiente de decidir si es confidencial, y `ajenos` o `sin_nombrar` en llano («alguien más escribió proyecto.md a las 10:03; sumé lo de hoy encima», «taller/x.md cambió mientras trabajábamos y no lo escribió esta sesión»). Del tablero, además de su fila, media línea solo si se lanzó porque la persona lo pidió o si se puso al día aquí. Nada más: el resumen largo ya está en los archivos. La cita con barra lateral se queda para lo que se enseña antes de escribir (la entrada, las decisiones y el `Estatus`, arriba en «Cómo se enseña antes de escribir»), no para el resumen.

---

## Cerrar el proyecto

Cuando el responsable dice que el proyecto terminó («cierra el proyecto», «esto ya está»). Antes se comprueba que la cuenta es la del responsable (CUENTA EN EL PROYECTO de `abrir.py`): si solo colabora, se dice que lo pida el responsable y no se cierra. Después se comprueba con él que se cumple lo que dice la segunda frase de `Objetivo` (o «Terminado significa», sin migrar); si no, se dice qué falta y se espera.

1. El `Estatus` de `proyecto.md` queda en una línea: la fecha y la frase en negrita que empieza por «Proyecto terminado el AAAA-MM-DD.» y dice cómo acabó, en lenguaje llano; `Siguientes pasos` dice que no queda ninguno propio, y lo que siga vivo se nombra con el proyecto que lo recoge.
2. La línea del proyecto en el bloque `Proyectos` de `area.md` se queda sola, sin desglosar sus entregables (`escribir.md`, «Un proyecto cerrado»).
3. Una entrada en `sesiones.md` que lo cuenta, y en `decisiones.md` solo si cerrarlo fue una decisión que alguien tomó.

Nada se borra ni se mueve: los entregables siguen con su estado y se siguen citando.

## Lo que nunca hago al cerrar

Además de las prohibiciones de `convenciones` (anexo `escribir.md`):

- Dar por cerrado un pendiente sin preguntar. Si no sé si algo quedó resuelto, lo pregunto

## Ejemplo de cierre

Las respuestas de Claude van aquí tal cual se escriben: la `>` es la cita que ve la persona.

**Usuario:** [después de trabajar en el criterio de corte por monto de compras/automatizacion-ordenes] cierra la sesión

**Antes de escribir:**

Decisiones

> ## 2026-08-29 · Las órdenes bajo 5.000 MXN no pasan por aprobación
> Decidió: Ana Pérez
> Por qué: el 70% del volumen son órdenes pequeñas y consumían el 80% del tiempo de aprobación, según el export de órdenes de 2025.
> Descartado: tope acumulado mensual por proveedor, porque el ERP no expone el acumulado en tiempo real.
> Afecta a: entregables/flujo-aprobacion.md (el paso de validación ya no aplica a todas) · finanzas/cierre-mensual (menos órdenes que conciliar)

Bitácora

> ## 2026-08-29
> Tema: el criterio de corte por monto.
> Avances: criterio fijado en 5.000 MXN y descartado el tope acumulado.
> Escribió: entregables/flujo-aprobacion.md
> Sesión de: Ana Pérez · plugin 1.23.2

Estatus

> 2026-08-29 · **Las órdenes bajo 5.000 MXN ya no pasan por aprobación; el 5 de septiembre se valida el criterio con Finanzas.**
> - **Se completó:** el criterio de corte por monto, el 29 de agosto.
> - **Siguiente:** validarlo con Luis Romero el 5 de septiembre; Ana retoma el mapa de proceso.

En «Siguientes pasos» quito «fijar el criterio de corte» y añado «validar el criterio con Finanzas el 5 de septiembre»; en `compras/area.md`, la línea del proyecto (Ana no es la responsable del área, así que su `Estatus` no se toca).

¿Lo registro así?

**Usuario:** sí

**Respuesta al cerrar:**

| Memoria · sesión cerrada · 4 archivos |
|---|
| [compras/automatizacion-ordenes/decisiones.md](computer:///…/compras/automatizacion-ordenes/decisiones.md) · el corte en 5.000 MXN |
| [compras/automatizacion-ordenes/sesiones.md](computer:///…/compras/automatizacion-ordenes/sesiones.md) · la sesión de hoy |
| [compras/automatizacion-ordenes/proyecto.md](computer:///…/compras/automatizacion-ordenes/proyecto.md) · estatus y siguientes pasos |
| [compras/area.md](computer:///…/compras/area.md) · la línea del proyecto |
| Tablero: avisado |

La decisión cita `entregables/flujo-aprobacion.md` en «Afecta a»: conviene revisarlo antes de publicarlo. Afecta también a `finanzas/cierre-mensual`: avísale a Luis Romero, responsable de Finanzas; la carpeta no lo hace por ti. Para la próxima, validar el criterio con Finanzas y retomar el mapa de proceso.
