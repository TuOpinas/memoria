---
name: sesion
description: Abre y cierra sesiones de trabajo sobre un proyecto. Usala cuando digan 'abre sesion', 'retomamos X', 'en que quedamos con...', 'cierra la sesion', 'guarda lo de hoy', 'terminamos' o 'cierra el proyecto', y cuando el dueño de un proyecto pregunte por el suyo: '¿como va X?', '¿en que estatus esta X?', '¿que falta en X?'.
---

# Sesión

Abrir y cerrar una sesión de trabajo sobre un proyecto. Antes de nada se carga la skill `convenciones`: su sección 12 fija qué se lee y en qué orden, y sus prohibiciones aplican a todo lo que sigue.

## Cuándo

**Abrir**: "abre sesión en compras", "retomamos automatización de órdenes", "¿en qué quedamos con X?", o cualquier arranque de trabajo sobre un proyecto existente.

**Abrir sin que lo pidan**: cuando el dueño de un proyecto pregunta cómo va el suyo: "¿en qué estatus está X?", "¿cómo va X?", "¿qué falta en X?", "¿qué sigue en X?". Dueño es quien tiene su cuenta junto al área del proyecto en `guia.md`, o figura como `Dueño` en su `proyecto.md`. Se abre sin preguntar, porque quien pregunta por lo suyo casi siempre va a trabajar en ello, y abrir no registra nada. Si quien pregunta no es el dueño, es `consulta`. Si solo preguntó y no trabaja, no hay nada que cerrar: nada se registra sin «cierra la sesión».

**Cerrar**: "cierra la sesión", "guarda lo de hoy", "terminamos".

**Cerrar el proyecto**: "cierra el proyecto", "esto ya está". Va al final de esta skill.

**Premisas**, solo en la sesión del responsable de contexto: "registra como premisa que…", "la premisa P2 cambia a…", "esa premisa ya no vale". Sección «Premisas», abajo.

**Responder un cuestionamiento**: "respondo al cuestionamiento…", "lo mantengo", "lo cambio", cuando al abrir se avisó de uno abierto. Se registra al cerrar como una decisión (paso 3).

Antes de nada se localiza la raíz entre las carpetas conectadas: la que tiene `guia.md` y `metodo.md` en su primer nivel. Si las herramientas de carpetas no están cargadas, se buscan y se cargan primero; nunca se dice que no hay carpeta sin haberlas listado, y con una carpeta conectada nunca se usa el conector de Google Drive (`convenciones`, sección 1). Si después de buscarlas no hay ninguna, se trabaja en solo lectura (abajo).

Si no queda claro el proyecto, preguntarlo antes de leer nada. Nunca asumir el último proyecto usado. Si hay más de una raíz conectada, se pregunta también en cuál, y la sesión se queda en esa: lo que haga falta de otra entra solo por un traspaso, que se hace como dice `raices.md`, junto al contrato.

---

# Abrir sesión

Abrir es solo lectura. No se escribe ningún archivo al abrir, salvo poner al día `metodo.md` cuando la raíz está atrasada (ver «Puesta al día del método»).

## Qué leo antes de responder

Por los niveles de la sección 12 de `convenciones`. Al abrir no se lee `base/`, salvo la fecha `actualizado` de `base/contexto.md` para su aviso.

**Nivel 0**, siempre:

1. La primera línea de `metodo.md`, para la versión y la huella de la raíz
2. `guia.md` entero, para el mapa de áreas, quién responde por cada una y las reglas propias de la casa
3. El bloque `Proyectos` de `<area>/area.md`
4. `base/premisas.md`, si existe: las premisas vigentes, las que ninguna otra reemplaza

**Nivel 1**, del proyecto ya identificado:

5. `<area>/<proyecto>/proyecto.md`
6. `decisiones.md` del proyecto, las 5 entradas más recientes
7. `sesiones.md`, las 3 entradas más recientes
8. `entregables/`, solo las cabeceras de cada archivo: nombre, estado, actualizado. `taller/` no se lee al abrir: entra a demanda, por su disparador de la sección 12
9. La cola del tablero, si la cuenta tiene uno: con `Artifact` (`list`, los de la cuenta) se buscan los artifacts llamados «Tablero <organización>» y «Tablero <organización> completo», donde <organización> es el nombre de la organización, lo que va antes del «·» en el título de `guia.md` (`convenciones`, sección 1); si no hay ninguno, no hay tablero y no se pregunta. De cada uno, con `ArtifactData` (se carga con `ToolSearch`), una consulta a la colección `cambios` con `proyecto` igual a `<area>--<proyecto>`, y otra con `tipo` igual a `prioridad` y `area` igual al área del proyecto: son prioridades del área marcadas como cumplidas o retiradas desde el tablero, que solo puede reescribir en `area.md` la sesión de su dueño. Trae fechas que la tarea no pudo aplicar, hechos con o sin nota, notas para la próxima sesión y correcciones de un paso o del estado del proyecto. Si la herramienta no está o el artifact no se deja leer, se dice en una línea y se sigue

**El barrido de avisos**, que es lo único que recorre la raíz entera:

10. Las líneas `Afecta a:` y `Cuestiona a:` de todos los `decisiones.md` de la raíz, buscando `area/proyecto` del proyecto activo (y `premisa P` si quien abre es el responsable de contexto). De cada `Cuestiona a:` que nombre este proyecto, se mira si alguna decisión de este proyecto lo responde con `Responde a:`; si no, está abierto. Es una búsqueda de un patrón de línea, no una lectura: solo se abre el encabezado de la entrada que dé positivo. Las carpetas restringidas a las que no tengo acceso fallan al leerse y se saltan sin más. Un aviso que salga de una carpeta restringida solo se da si el proyecto activo está dentro de ella

No leo `fuentes/`, ni `base/contexto.md`, ni `base/glosario.md`, ni `base/sistemas.md`, ni el resto de `area.md`. Entran cuando el trabajo del día los pida, por sus disparadores de la sección 12.

## Qué respondo

Si es la primera sesión que se abre en esta conversación, la respuesta empieza con la línea «Memoria activa · <organización> · método <versión> · escribes en <áreas de la cuenta>», como pide el aviso de arranque. Después, tres bloques, en este orden y sin encabezados largos.

**Dónde quedó todo.** Cuatro o cinco líneas: objetivo del proyecto en una frase, qué se hizo en la última sesión, qué quedó pendiente. Nada de recapitular el proyecto entero. Si la sesión se abrió por una pregunta de estado, este bloque es la respuesta y empieza por ella: si el proyecto tiene `En corto`, por él, tal cual o casi, y si hubo sesiones después de su fecha, se dice; si no, en qué está y qué espera.

**Lo que llegó del tablero**, solo si la cola trae algo de este proyecto. Una línea por cambio, con su fecha: el paso marcado hecho y su nota si la trae, la nota suelta, la corrección propuesta, la fecha que la tarea no encontró dónde aplicar. Termina preguntando qué pasó con cada hecho sin nota y si cada corrección va, porque eso es lo primero que se resuelve en la sesión: un hecho se cierra quitando el paso y contándolo en `sesiones.md`, y a veces trae una decisión.

**Avisos**, solo si aplican. Estas comprobaciones:

- Alguien cuestionó una decisión de este proyecto y nadie lo ha respondido. Va primero, porque espera al dueño: se cita qué decisión, quién lo planteó, su por qué en una línea y de qué proyecto viene. Si quien abre es el responsable de contexto, lo mismo con los cuestionamientos a una premisa
- Alguna decisión de otro proyecto de la raíz nombra este proyecto en `Afecta a:`. Se cita la entrada con su fecha, quién decidió y de qué proyecto viene
- Alguna decisión reciente de este proyecto choca con una premisa vigente. Se dice cuál y por qué, sin darlo por resuelto
- `base/contexto.md` lleva más de 90 días sin actualizarse, mirando solo su fecha `actualizado`, sin abrirlo
- Algún entregable tiene en `basado_en` un archivo cuya fecha `actualizado` es posterior a la suya, y por tanto puede estar desfasado
- Algún entregable lleva más de 30 días en `borrador`
- Algún entregable tiene una fecha `actualizado` posterior a la última entrada de `sesiones.md`: hubo trabajo que ninguna sesión registró, seguramente una que no se cerró. Se dice qué cambió y se propone registrarlo hoy, preguntando qué pasó

Si no hay avisos, no se menciona que no los hay.

**Puesta al día del método.** Se compara la primera línea del `metodo.md` de la raíz con la del `metodo.md` del plugin, versión y huella. Si coinciden, no se dice nada. Si no:

- **La raíz está atrasada**: la versión del plugin es más nueva, o es la misma y la raíz no lleva huella. Lo abra quien lo abra, se copia el `metodo.md` del plugin sobre el de la raíz sin preguntar (escrito directo desde el plugin como dice «Los archivos del plugin en la computadora» en la skill `tablero`, nunca pegado), porque es una copia exacta que nadie edita y no toca nada más, y se dice en una línea al final de la respuesta, sin nombres de archivo: «He puesto al día las reglas del método en esta carpeta, a la versión <versión del plugin>. No cambia nada de lo que hay en ella.» Si la escritura falla por permisos (la cuenta no puede escribir en el primer nivel de la carpeta), no se dice nada: la pondrá al día la siguiente cuenta que abra
- **El plugin de quien abre está atrasado**: la raíz lleva una versión más nueva. No se copia nada y se dice en una línea: «Esta carpeta usa una versión del método más nueva que la de tu Claude (<versión de la raíz> frente a <versión de tu plugin>). Actualízalo en la app de Claude, en Customize → Plugins, con el botón Update del marketplace memoria-marketplace, o pide ayuda a quien administra la carpeta.»
- **Misma versión con huellas distintas**: no se toca ni se dice nada. Solo pasa entre dos publicaciones y lo resuelve la siguiente versión

**Propuesta de trabajo.** Dos o tres focos posibles, tomados de los siguientes pasos de `proyecto.md`, de lo que quedó pendiente en la última sesión y de los avisos de otras áreas, cada uno con una línea de por qué ahora. Se ordenan por lo que desbloquea a otros: primero lo que otra persona está esperando, después lo que cierra algo empezado, al final lo que abre frente nuevo. Si en los avisos hay un cuestionamiento abierto a este proyecto, responderlo es el primer foco, porque alguien espera; basta con que el dueño diga si lo mantiene o lo cambia, y por qué. Termina preguntando por cuál empezamos, y espera respuesta.

Si un aviso afecta al foco propuesto, se dice ahí mismo. No se empieza a trabajar sobre un entregable posiblemente desfasado sin avisar antes.

---

# Sin carpeta: solo lectura

Cuando la sesión no tiene ninguna carpeta conectada (desde el teléfono, desde la web) y tiene el conector de Google Drive, se puede abrir sesión, consultar y preguntar al director leyendo la raíz en Drive. No se escribe nada en ella.

**Encontrar la raíz.** Con el conector, se buscan archivos llamados `guia.md` (`title = 'guia.md'`) y se queda la carpeta que además tiene `metodo.md` en su primer nivel. Si hay más de una, se pregunta cuál, como con varias raíces conectadas. Si no hay ninguna, se dice que la raíz no está en Drive o que esta cuenta no la ve, y que la memoria se trabaja desde la computadora con la carpeta conectada.

**Leer por niveles.** Los mismos niveles de la sección 12 de `convenciones`. Listar una carpeta con `parentId` devuelve cada archivo con un fragmento de su texto, que basta para las cabeceras y las fechas; un archivo entero se lee con `read_file_content`, que devuelve el Markdown con las marcas escapadas (`\#`, `\---`): se leen como si no lo estuvieran. La búsqueda de avisos se hace con `fullText contains 'Afecta a: <area>/<proyecto>'` y con `Cuestiona a:`, en lugar de recorrer los archivos.

**Qué se dice.** La primera respuesta empieza con «Memoria en solo lectura · <organización> · método <versión> · desde aquí no se registra nada», en lugar de «Memoria activa». Después, lo mismo que al abrir con la carpeta.

**Qué pasa con lo que sale de la sesión.** Nada se escribe en la raíz: ni decisiones, ni bitácora, ni pasos, ni el Panorama. Lo que haya que registrar se guarda, con el sí de la persona, como nota en la cola del tablero de su cuenta: un documento nuevo en la colección `cambios` con la forma exacta de las notas que escribe la página, `{tipo: "nota", proyecto: "<area>--<slug>", nota: "<texto>", creado: "<fecha y hora ISO>", estado: "pendiente"}`; si lo que sale es del área y no de un proyecto (un panorama, una prioridad), va con `area: "<slug del área>"` en lugar de `proyecto`, y lo enseña la siguiente sesión que su dueño abra en cualquier proyecto del área. La siguiente sesión con la carpeta lo enseña al abrir, como cualquier nota del tablero. Si la persona no tiene tablero, se le da el texto para que lo pegue al abrir la próxima sesión desde la computadora. Una decisión no se da por registrada hasta entonces.

---

# Premisas

Solo en la sesión del responsable de contexto según `guia.md`; a cualquier otra persona se le dice que una premisa la registra él, y se le prepara el texto. Se hace en el momento en que se pide, no al cerrar, porque la dirección la confirma en voz alta y lo que importa es que quede.

1. Se lee `base/premisas.md` entero si existe. Si no existe, se crea con su cabecera (`estado: vigente`, `actualizado` de hoy) y el título `# Premisas`.
2. Se redacta la línea con el formato de la sección 2 de `convenciones`: `- P<n> · <texto> · Confirmó: <nombre y apellido> · <fecha de hoy>`, con el `P<n>` siguiente al mayor que haya en el archivo, aunque alguna esté reemplazada. Si cambia una que existe («la premisa P2 cambia a…», «ya no vale»), la línea nueva termina en `· Reemplaza a P<n>`; la antigua no se toca. Quien confirma es quien dirige la organización, no quien abre la sesión, salvo que sean la misma persona: se pregunta si no está claro.
3. Se enseña la línea y se escribe solo con el sí. Se añade al final del archivo y se pone al día `actualizado`.
4. Si la premisa nueva reemplaza a una con cuestionamientos abiertos (los del barrido al abrir), se dice que quedan respondidos y a quién avisar: a quien los planteó. Si la premisa se mantiene frente a un cuestionamiento, no hay línea nueva: la respuesta es una entrada con `Responde a:` en el `decisiones.md` de un proyecto del responsable de contexto, como cualquier otra (paso 3 de cerrar).

Una premisa es algo que la dirección confirmó y sobre lo que todos construyen; un objetivo de un proyecto o una preferencia de un área no lo es. Ante la duda, se pregunta de quién es la confirmación.

---

# Cerrar sesión

## Qué escribo y dónde

**0. La cola del tablero**, si se leyó al abrir. Lo que la sesión resolvió se borra de la cola con `ArtifactData` y la versión leída: un hecho ya quitado de «Siguientes pasos» y contado en `sesiones.md`, una nota ya registrada donde le tocaba, una corrección ya aplicada reescribiendo el paso o el estado actual, una fecha ya puesta en su línea, una prioridad ya quitada de «Prioridades ahora» de `area.md` porque el dueño del área lo pidió en esta sesión. Lo que no se resolvió se queda, y el tablero lo sigue mostrando como pendiente.

**1. Lo que se hizo y aún no está en la carpeta.** Lo producido se guarda al crearlo, así que esto no debería pasar; si algo de la sesión (un documento, un PDF, un análisis) solo existe en la conversación, se guarda ahora en `entregables/` o en `taller/` como borrador, antes de registrar nada. Lo mismo con lo que la app haya dejado en «Claude outputs» durante esta sesión: se mueve a este proyecto y deja de estar ahí.

**2. `sesiones.md`.** Entrada nueva arriba del todo, sin tocar las anteriores:

```markdown
## 2026-08-29
Trabajamos en: rediseño del flujo de aprobación por monto.
Avances: mapa del proceso actual terminado, en borrador esperando a Ana.
Pendiente: confirmar con Finanzas el tope de 5.000 MXN.
```

Tres líneas. Si una sesión no cabe en tres líneas, es que hubo decisiones y esas van a su archivo.

**3. `decisiones.md`, solo si hubo decisiones.** Antes de escribir, se listan al usuario las decisiones detectadas y se pide confirmación explícita. El registro no se puede corregir después, así que nada entra sin que alguien lo confirme. Formato:

```markdown
## 2026-08-29 · Las órdenes bajo 5.000 MXN no pasan por aprobación
Decidió: Ana Pérez
Por qué: el 70% del volumen son órdenes pequeñas y consumían el 80% del tiempo de aprobación, según el export de órdenes de 2025.
Descartamos: tope acumulado mensual por proveedor, porque el ERP no expone el acumulado en tiempo real.
Afecta a: entregables/flujo-aprobacion.md (el paso de validación ya no aplica a todas) · finanzas/cierre-mensual (menos órdenes que conciliar)
```

**Responder un cuestionamiento.** Si al abrir se avisó de un cuestionamiento abierto a este proyecto y el dueño lo respondió en la sesión, la respuesta es una decisión más de esta lista, aunque solo mantenga lo que ya estaba: «lo mantengo» cambia algo, porque cierra una pregunta que alguien tenía abierta. La entrada lleva `Responde a: <identificador del cuestionamiento>` (el que se citó al abrir), dice en el título si mantiene o reemplaza lo cuestionado, y en `Por qué` la razón que dio el dueño. Se confirma como cualquier decisión y se dice a quién avisar: a quien lo planteó.

**Plantear un cuestionamiento.** Si la persona quiere cuestionar una decisión de otro proyecto o una premisa, se escribe en el `decisiones.md` del proyecto activo, con el formato de la sección 4 de `convenciones` (`Planteó`, `Por qué`, `Cuestiona a`), después de enseñárselo y con su confirmación, como una decisión. Se le dice a quién avisar: al dueño de lo cuestionado.

Una decisión es un compromiso que cambia lo que se va a construir. Una preferencia expresada en voz alta no lo es. Ante la duda, se pregunta.

Si la decisión trae análisis detrás (opciones comparadas, tablas, cifras), el análisis va a un entregable del proyecto y la entrada lo cita. La entrada se queda con lo justo para entenderla sin abrir nada más.

Si `Afecta a` nombra un proyecto de otra área, se dice al usuario a quién tiene que avisar: el dueño de esa área, según `guia.md` o su `area.md`. La carpeta no notifica a nadie y la skill tampoco.

Si el proyecto activo lo lee todo el equipo y la decisión toca a un área o a un proyecto restringido, `Afecta a` lleva su nombre y nada más, porque ese nombre ya está listado: ni sus archivos, ni lo que contiene. Al revés, una decisión que se registra dentro de una carpeta restringida sí puede nombrar cualquier proyecto al que afecte.

**4. `proyecto.md`.** Se ponen al día `En corto`, `Estado actual` y `Siguientes pasos`. Es un archivo vivo: lo que deja de ser cierto se sustituye, no se acumula. `Estado actual` y `Siguientes pasos` se editan, no se vuelven a escribir enteros: se quitan los pasos hechos, se añaden los nuevos y se cambian solo las frases que la sesión dejó viejas, con reemplazos exactos sobre el archivo (en la computadora, un script corto que lee el archivo y cambia cada texto viejo por el nuevo), sin volver a escribir lo que sigue valiendo. Si un texto viejo no aparece exactamente una vez (la tarea del tablero pudo poner una fecha en esa línea), se relee el archivo y se ajusta el reemplazo antes de escribir. Si `Estado actual` pasa de unas diez líneas, lo que ya es historia se quita, porque está en `sesiones.md` y `decisiones.md`. `En corto` se reescribe entero, en la misma escritura, con la voz del director y la forma de `convenciones`, sección 3: la fecha de hoy, la frase de lo completado y lo que sigue, y debajo «Se completó», «Siguiente» y, si tienen algo, «Falta decidir» y «Preocupa». Para alguien que no abrirá nada más y que puede verlo en un tablero compartido: personas y fechas absolutas, sin rutas, sin nada de `restringido/` ni datos personales. Si el proyecto no lo tenía, se crea debajo del título.

**5. Bloque `Proyectos` de `area.md`.** Se reescribe la línea de este proyecto y, debajo, una línea por cada entregable `vigente` con su fecha `actualizado`. Solo esa parte del bloque; las líneas de los demás proyectos no se tocan. `Prioridades ahora` solo se reescribe si el dueño lo pide en esta sesión.

**6. Cabeceras de lo que se tocó.** Se actualiza `actualizado` en cada archivo modificado y se añade a `basado_en` cualquier fuente nueva que se haya usado.

**7. Lo que entró en `fuentes/` o en `taller/`.** Si durante la sesión se guardó algo en `fuentes/` sin haber pasado por la pregunta de si es confidencial, se pregunta ahora: si trae datos personales, facturación, contratos, credenciales o cualquier cosa que no todos deban ver, se propone llevarlo a `restringido/` del mismo proyecto y dejar su fila en el `fuentes/enlaces.md` público. El usuario decide; nada se mueve sin que lo confirme.

**8. Traspasos.** Si en la sesión entró algo de otra raíz, la entrada de `sesiones.md` lo dice: qué vino, de qué raíz, quién lo pidió. Lo que se quedó fuera no se nombra.

**9. Rotación.** Si `sesiones.md` o `decisiones.md` supera las 1.500 líneas o cambia el año, se renombra con el año (`sesiones-2026.md`, o `sesiones-2026-2.md` si ya hay uno de ese año) y se abre uno nuevo con su cabecera. Sin preguntar.

**10. El Panorama del área.** Se reescribe `Panorama` de `<area>/area.md` con la forma que da la skill `director` en «Escribir el Panorama», en tres a cinco frases con la fecha de hoy: cómo está el área después de esta sesión. Al cerrar no se relee el área: se parte del Panorama anterior y de lo que esta sesión ya leyó y escribió, y de los demás proyectos del área solo se mira, en una sola llamada, la cabecera y el `En corto` de los que tienen `actualizado` posterior a la fecha del Panorama anterior, o de todos si no había Panorama con fecha. Va en la misma escritura de `area.md` que el paso 5. Solo si el área es de la cuenta que cierra; si no, se salta.

**11. El tablero, al día, sin esperarlo.** Si la cuenta tiene tablero (el que se buscó al abrir), después de escribir todo lo anterior se lanza su tarea del botón, que lo pone al día por su cuenta: con `list_triggers` (se carga con `ToolSearch`; con `enabled: true`, siguiendo `next_cursor` hasta encontrarla, porque la lista se corta por tamaño) se busca la tarea llamada «Regenerar tablero <organización>», con « completo» si es ese tablero. Se dispara con `fire_trigger`, con el texto «Lanzada al cerrar la sesión de <area>/<proyecto>», si cumple dos cosas: su aprobación es automática (`permission_mode` es `auto` en su `derived_state`) y su carpeta (`derived_state.folders`) es la raíz conectada en esta sesión, la de `get_device_info`, porque la tarea corre en la computadora que la creó. Una por cada tablero de la cuenta. Es lo mismo que pulsar «Sincronizar ahora»: corre en su propia sesión contra la carpeta y esta sesión no la espera; si ya hay una corrida a medias, se dispara igual, porque la tarea sabe empezar de nuevo cuando otra escribió entre medias. Si no hay tarea, no cumple esas dos cosas (sin aprobación automática se quedaría parada esperando a alguien; en otra computadora no encontraría la carpeta) o el disparo falla, se pone al día aquí mismo: es «Sincronizar» de la skill `tablero`. Se hace aunque la sesión no haya tocado la cola. Es invisible para la persona: nunca se le pide nada para hacerlo (ni una carpeta, ni un permiso, ni una acción), como dice «SIN PEDIR NADA A NADIE» en `tarea.md`. Si la computadora o la herramienta de artifacts no responden, o un paso falla, se dice en media línea y la sesión queda cerrada igual: el tablero se pondrá al día en el próximo cierre o con «sincroniza el tablero».

## Qué respondo al terminar

Dos o tres líneas: qué archivos se escribieron y qué queda para la próxima. Si hay que avisar a otra área, se dice a quién. Si quedó algo en `fuentes/` pendiente de decidir si es confidencial, se dice. Del tablero, media línea: que se está poniendo al día por su cuenta, que se puso al día aquí, o por qué no se pudo. Nada más. El resumen largo ya está en los archivos.

---

# Cerrar el proyecto

Cuando el dueño dice que el proyecto terminó («cierra el proyecto», «esto ya está»). Antes se comprueba con él que se cumple lo que dice `Terminado significa`; si no, se dice qué falta y se espera.

1. `Estado actual` de `proyecto.md` abre con «Proyecto terminado el AAAA-MM-DD» y una línea de cómo acabó, y `En corto` queda solo con su frase en negrita, que lo dice en lenguaje llano; `Siguientes pasos` dice que no queda ninguno propio, y lo que siga vivo se nombra con el proyecto que lo recoge.
2. La línea del proyecto en el bloque `Proyectos` de `area.md` se queda sola, sin desglosar sus entregables (`convenciones`, sección 3, «Un proyecto cerrado»).
3. Una entrada en `sesiones.md` que lo cuenta, y en `decisiones.md` solo si cerrarlo fue una decisión que alguien tomó.

Nada se borra ni se mueve: los entregables siguen con su estado y se siguen citando.

---

## Lo que nunca hago

Además de las prohibiciones de `convenciones`:

- Escribir algo al abrir sesión. Abrir es solo lectura, salvo poner al día `metodo.md` cuando la raíz está atrasada
- Leer al abrir más de lo que dice el nivel 0 y el nivel 1
- Dar como aviso a alguien una decisión que leí en una carpeta restringida a la que su proyecto no pertenece
- Dar por cerrado un pendiente sin preguntar. Si no sé si algo quedó resuelto, lo pregunto
- Borrar de la cola del tablero un cambio que la carpeta todavía no refleja

---

## Ejemplo completo

**Usuario:** retomamos automatización de órdenes

**Respuesta al abrir:**

> El proyecto busca quitar aprobaciones manuales en compras de bajo monto. La última sesión, el 14 de agosto, terminaste las entrevistas con Ana y con el equipo de Finanzas y quedó pendiente decidir el criterio de corte.
>
> Tres avisos. Finanzas registró el 20 de agosto en `finanzas/cierre-mensual/decisiones.md` que el cierre pasa al día 3, y marcó este proyecto como afectado: decidió Luis Romero. `base/contexto.md` no se toca desde hace 104 días. Y `entregables/mapa-proceso.md` lleva 41 días en borrador esperando a Ana.
>
> Tres focos posibles para hoy:
>
> 1. Cerrar el criterio de corte por monto. Es lo que bloquea el flujo de aprobación y Finanzas está esperando.
> 2. Revisar si el cambio de fecha de cierre toca el flujo de aprobación antes de seguir construyendo sobre él.
> 3. Empujar la revisión del mapa de proceso, que lleva seis semanas parado.
>
> ¿Por cuál empezamos?

**Usuario:** por el 1. [conversación de trabajo] ... cierra la sesión

**Antes de escribir:**

> Detecté una decisión en la conversación de hoy:
>
> Las órdenes bajo 5.000 MXN no pasan por aprobación. Decidió Ana Pérez. Descartamos el tope acumulado mensual porque el ERP no lo expone en tiempo real. Afecta al flujo de aprobación y al cierre mensual de Finanzas.
>
> ¿La registro así en `decisiones.md`?

**Usuario:** sí

**Respuesta al cerrar:**

> Escribí la entrada en `decisiones.md`, la sesión de hoy en `sesiones.md`, actualicé los siguientes pasos en `proyecto.md` y la línea del proyecto en `compras/area.md`. La decisión cita `entregables/flujo-aprobacion.md` en «Afecta a», así que conviene revisarlo antes de publicarlo.
>
> La decisión afecta a `finanzas/cierre-mensual`. Avísale a Luis Romero, que es el dueño de Finanzas; la carpeta no lo hace por ti.
>
> Para la próxima queda validar el criterio con Finanzas y reanudar la revisión del mapa de proceso.
