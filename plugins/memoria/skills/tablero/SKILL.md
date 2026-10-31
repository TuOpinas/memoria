---
name: tablero
description: Monta, actualiza y sincroniza el tablero de una persona sobre la carpeta de su organizacion, una pagina que muestra la carpeta entera (areas, proyectos, estado, decisiones, siguientes pasos) generada desde los archivos y puesta al dia cuando quien lo monto lo pide, con el boton de la pagina o con 'sincroniza el tablero'. Usala cuando digan 'monta el tablero', 'monta mi tablero', 'quiero ver la carpeta sin abrirla', 'actualiza el tablero', 'sincroniza el tablero', 'regenera la vista', 'pon el tablero al dia cada manana', 'pon el boton de sincronizar', 'cambie de computadora' o pregunten por que el tablero no muestra algo.
---

# Tablero

Una página que muestra la carpeta de la organización sin abrirla: qué áreas hay y de quién son, en qué va cada proyecto, qué se decidió, qué entregables hay y qué tareas siguen. Se genera desde los archivos y se pone al día cuando su responsable lo pide. Antes de escribir en la carpeta se carga el anexo `escribir.md` de `convenciones`, cuyas prohibiciones aplican a todo lo que sigue; montar, y una sincronización con la cola vacía que solo pone al día `metodo.md` (una copia exacta del plugin), no lo necesitan.

Cinco reglas que no cambian:

- **El tablero es de una persona.** Lo monta cada quien desde su propia cuenta, sobre la raíz conectada, y corre con sus permisos: lo que esa cuenta no puede leer en la carpeta sale como «restringido», y lo que su puesta al día escribe en la carpeta lo escribe con sus permisos. El de quien administra la carpeta es uno más. Muestra todo lo que lee la cuenta de su responsable, también lo restringido y la bitácora (las cinco sesiones más recientes a la vista, y las demás al abrir la pestaña), así que no se comparte: quien quiera verlo monta el suyo.
- **La carpeta es la fuente.** El tablero lee la superficie pública de la raíz (`guia.md`, los `area.md` y, de cada proyecto, `proyecto.md`, `decisiones.md`, `sesiones.md` y las cabeceras de `entregables/` y de `taller/`) y nada más. Nunca abre `fuentes/`, `restringido/` ni `base/`, salvo `base/premisas.md`, que es de toda la organización y va arriba de todo; del `taller/` lee solo la cabecera y el título de cada archivo (su inventario, para «Qué hay»; el cuerpo es privado del área y no viaja), y de `fuentes/` y `taller/` mira las fechas de los archivos, para avisar del trabajo sin sesión.
- **El tablero no escribe en la carpeta.** Lo que alguien toca en él (fechar una tarea, marcarla hecha, anotar algo, corregir un estado) espera en una cola propia de la página, y lo escribe quien tiene contexto: la puesta al día lo mecánico, la siguiente sesión del proyecto lo que pide juicio. Y la puesta al día escribe solo en las áreas y proyectos donde la cuenta que la lanza es responsable o colabora: lo que su responsable marcó en un proyecto de otra área espera en la cola, y el tablero dice a quién pasárselo.
- **Se pone al día cuando quien lo montó lo pide.** Esta es la frase, y es la misma en el contrato, en la receta de `nuevo`, en el README y en la ayuda. Hasta la 1.18 la puesta al día se lanzaba sola al abrirse tras un cierre; desde la 1.19 no, porque cada puesta al día es una tarea que gasta del plan y varias sesiones al día lanzaban varias (decisión del 2026-10-23). El cierre de una sesión (skill `sesion`, anexo `cerrar.md`, paso 11) no lanza nada: deja apuntado el cierre en la colección `cierres` de la base, y al abrir el tablero la página ve los cierres posteriores a la última sincronización y avisa en Mantenimiento de Inicio, de cuáles son, con el botón que lanza la tarea, que solo trae lo que cambió y aplica lo mecánico de la cola. Lo que escriben otras personas no deja marca: se trae con el botón «Sincronizar ahora», que todo tablero tiene junto al nombre de la organización (su tarea, sin horario, se crea al montarlo y solo corre cuando su responsable lo pulsa), o con «sincroniza el tablero». Que corra también cada mañana es opcional y se crea solo si lo piden.
- **Vive fuera de la raíz.** La página, sus archivos de datos, su base, los scripts y la tarea del botón son de la cuenta de quien lo montó. En la carpeta de la organización no entra nada: ni un enlace. El tablero se encuentra por su nombre, que es fijo, entre los artifacts de la cuenta; es así como `sesion` lo localiza para leer su cola, sin que nadie apunte la URL en ningún sitio.

## Qué muestra

Un solo tablero por persona y raíz, desde la 1.18: todo lo que su cuenta lee, incluidas las áreas y proyectos restringidos a los que tiene acceso, con las cinco sesiones más recientes de cada proyecto enteras; lo que la cuenta no puede leer sale con su nombre y su responsable, y nada más. Desde la 1.22.3 no lleva la marca «Personal · no compartir»: no aportaba en la página de cada quien; que no se comparte lo dicen esta regla y la ayuda.

La página se ordena igual en los tres niveles (1.24): Inicio, cada área y cada proyecto tienen cuatro pestañas, **Estatus · Acciones · Actividad · Qué hay** (en Inicio la última es **Mantenimiento**), y cada una contesta una sola pregunta. **Estatus**, cómo está y qué cambió: la línea «Últimos 7 días», «Avanzaron otros» (lo que otras personas trabajaron en tus proyectos desde tu última sesión en cada uno, con el tema y los avances de cada sesión y sus decisiones), el Estatus firmado (en el área, con sus prioridades debajo de «Siguiente» y «Atender»), las fichas de los hijos con un pie que solo cuenta lo que pide algo, y «Esperas a» (por persona, con «Ya llegó» y «Ya no aplica»). **Acciones**, lo que el tablero calcula para ti: «Por dónde empezar», «Te toca decidir» (con señal solo cuando la decisión bloquea algo), «Tareas críticas» (fecha a dos semanas de hoy, hacia atrás o hacia delante, y en «Siguiente», en una prioridad del área o con un cliente; vencidas primero) y «Decisiones que te afectan», con «Aceptar» y «Cuestionar», que van a la cola como `respuesta` y registra la sesión del proyecto elegido (`sesion`, `cerrar.md`, paso 0); su número cuenta solo lo tuyo, igual en los tres niveles (1.24.2). **Actividad**, lo que pasó, con el mismo arranque en los tres niveles (periodo y cifras); «Por persona» lista a todos los que escriben en la carpeta, con sus sesiones, decisiones, documentos escritos y publicados y tareas abiertas. **Mantenimiento**, solo en Inicio: «Arreglar ya» (el único número; si trae algo, una línea amarilla encima de las pestañas) y «Proyectos por poner al día». **Qué hay**, en área y proyecto: primero «Por poner al día», cuyo número lleva la pestaña (1.24.2); después «Lo publicado / En el taller» y, plegados, los entregables, el taller (cada pieza reemplazada dice por cuál) y todas las tareas. La cabecera de área y proyecto enseña su descripción en dos líneas con «Ver más». «Tarea» es la palabra de la página para cada línea de «Siguientes pasos». La pestaña elegida se conserva al pasar a otra área o a otro proyecto, también desde el lateral, las migas o un enlace guardado (1.22.4); solo la cambia un clic en otra pestaña. El grupo **Consulta** del lateral reúne Agenda (las tareas con fecha), Decisiones (por área, por persona, de dentro y de fuera) y Entregables (con su aportación y cuántos proyectos los citan). Las frases de resumen (`aportacion`) que sugiere la memoria salen como provisionales en «Qué hay», y quien monta el tablero las acepta de golpe en los proyectos donde su cuenta escribe; las escribe el próximo cierre del proyecto (`sesion`, `cerrar.md`, paso 0). Antes de la 1.18 había dos modos, público y completo, y la gente montaba el que no le servía o miraba uno creyendo que era el otro; cómo pasan los de entonces está en «Los tableros de antes de la 1.18», abajo.

Antes de montar, la skill mira si la cuenta ya tiene un tablero de esa raíz (`list_artifacts` del conector `claude-artifacts`, o `Artifact` con `list`, por los nombres de abajo) o su tarea (`list_triggers`); si lo tiene, lo dice y propone actualizarlo o sincronizarlo en vez de montar otro.

Lo que trae esta skill, en su carpeta: `vista.html` (la página), `generar_vista.py` (lee la raíz y produce los documentos del tablero, en dos tiempos: un inventario corto en la computadora y la generación en Claude sobre una copia de lo que lee), `plan_subida.py` (dice qué documentos cambiaron), `datos.py` (desde la 1.24.1, pasa los documentos a los archivos que se publican con la página, y de vuelta, y dice lo poco que se escribe en la base), `aplicar_cambios.py` (escribe en la carpeta lo mecánico de la cola), `barrido.py` (el barrido de lo que las sesiones olvidaron: deja propuestas en la cola, sin escribir en la carpeta), `tarea.md` (los pasos de la puesta al día, que siguen al pie de la letra la sincronización en sesión y la tarea; con cuatro valores), sus anexos `cola.md` y `regenerar.md`, que se leen solo si la cola trae algo o si hay que regenerar, y `tarea-prompt.md` (el prompt corto de la tarea, que solo manda leer `tarea.md` del plugin instalado). Nada de esto se copia a la raíz.

## Cuándo

**Montar**: "monta el tablero", "monta mi tablero", "quiero ver la carpeta entera sin abrirla". «Monta el tablero completo» o «el público», de quien conoció las versiones de antes, monta este mismo, y se dice en una línea que ya hay uno solo.

**Actualizar**: "actualiza el tablero", o cuando el tablero muestra que su página y el plugin corren versiones distintas.

**Sincronizar**: "sincroniza el tablero", "regenera la vista", "lo que marqué no aparece en la carpeta". Es la puesta al día a mano; la misma que lanza el botón de la página.

**Tarea diaria**: "pon el tablero al día cada mañana". Solo cuando la piden. El botón ya viene con el tablero; "pon el botón de sincronizar" en un tablero que no lo tiene es «Actualizar».

Si hay más de una raíz conectada, se pregunta cuál. Una sesión monta un solo tablero.

## Antes de montar

Cuatro comprobaciones, y en la primera que falle se dice qué falta y se para:

1. **La raíz conectada es completa**: tiene `guia.md` y `metodo.md` en su primer nivel. Si solo está conectada la carpeta de un área, el tablero no se puede montar.
2. **No hay ya uno** de esta raíz en esta cuenta: «Tablero <organización>», o «Tablero <organización> completo» si es de antes de la 1.18. Si lo hay, se ofrece actualizar o sincronizar.
3. **La cuenta tiene lo que hace falta**: las herramientas del tablero (el conector `claude-artifacts`, o las de antes, `Artifact` y `ArtifactData`: «DÓNDE ESTÁ CADA COSA» de `tarea.md`), con las capacidades de base de datos, usuario y conector; `device_stage_files`, que trae a Claude la copia de lo que el tablero lee, y `device_commit_files`, que escribe en la carpeta lo de la cola. Se comprueba con `ToolSearch`; lo que no esté se nombra.
4. **La computadora está disponible** y la raíz conectada. Con consola, la raíz se ve en `$HOME/mnt/` del shell, y si no aparece se pide con `device_request_folder_access` por su ruta. Si el shell dice que no pudo montarla, es sin consola (anexo `sin-consola.md` de `convenciones`): no se pide nada, y el tablero se monta y se pone al día igual, sobre una copia, como dice «SIN CONSOLA» en `tarea.md`.

## Montar

**1. Publicar la página.** Se copia `vista.html` de esta skill al scratchpad con el nombre `tablero.html`, se sustituye su primera línea `<title>Tablero</title>` por `<title>Tablero <organización></title>` (<organización> es el nombre de la organización: lo que va antes del «·» en el título de `guia.md`, `convenciones` sección 1), y se publica como artifact nuevo con el icono `dashboard` (`publish_files`, sin `slug`, con `tablero.html` como `index.html` y el título; o `Artifact`), y esta declaración de capacidades, idéntica para todos los tableros (con el conector, `mcp__claude-artifacts__declare_capabilities` justo después de publicar; con `Artifact`, en la misma publicación):

```
db: reglas [{path: "", read: "view", write: "admin"}, {path: "cambios", read: "view", write: "interact"}]
user: {}
mcp: servers [{server: "Claude Code Remote", tools: ["fire_trigger"]}]
```

Con eso quien lo montó lo ve, actúa desde él (lo que toca va a la cola) y lanza la sincronización; la base la escriben la tarea y los editores. La regla de `cambios` para quien no es editor viene de cuando el tablero se compartía, y se queda igual en todos para que ninguno tenga que volver a publicarse con otras capacidades.

**2. La tarea del botón.** Se crea siempre, sin horario, como dice «La tarea del botón y la diaria» abajo, y su id se pasa al generador en el paso 3 con `--manual`; si la persona pide además que corra cada mañana, se crea con horario en vez de sin él. Crearla pide una aprobación en la app, que forma parte de montar. Si falta el conector «Claude Code Remote», se monta igual, con el botón apagado diciendo que falta el conector, y se dice en una línea.

**3. Generar.** Son los pasos 0, 1 y 5 de `tarea.md` y `regenerar.md` tal cual (la versión de partida es la que devolvió la publicación del paso 1) (sin consola, con lo que dice su «SIN CONSOLA», copia incluida), como la primera vez (`--primera-vez`, `--sin-archivos`): inventario en la computadora, copia de los archivos con `device_stage_files`, generación en Claude y `plan_subida.py`, que sin nada publicado lo propone todo. Ningún documento pasa por la conversación.

**4. El primer «Por dónde empezar», y publicar.** Es el paso 6 de `regenerar.md` (cómo, en `juicio.md`) y va antes de publicar, porque la página saldría sin esa sección hasta la siguiente puesta al día: se leen los grupos candidatos de `<trabajo>/salida/meta/enfoque-candidatos.json` y los pasos con sus señales, se eligen tres o cuatro grupos con los tres criterios (prioridad del área, cliente o dinero, desbloquea a otros; vencido no suma) y se escribe en `<trabajo>/enfoque.json`. Después, PUBLICAR de `tarea.md`, con `--vista` y `--enfoque`: la página y sus cuatro archivos de datos en una sola publicación, que apunta en meta/estado la versión de la página (`pagina_actualizada`), para que la puesta al día no tenga que leerla.

**5. Comprobar.** Se abre el artifact (el `Artifact` con `open`, o se da el enlace) y se mira que pinte la raíz con sus áreas.

### Qué respondo al terminar

Cuatro líneas, sin recapitular los pasos:

- Qué quedó montado: el tablero, con lo que muestra.
- **Cuándo se pone al día:** cuando quien lo montó lo pide, con el botón junto al nombre de la organización o con «sincroniza el tablero», con la computadora encendida y la app abierta; al abrirlo avisa de las sesiones cerradas que aún no muestra. Si en esa raíz escriben varias personas, se ofrece la tarea diaria en una línea.
- **No se comparte:** muestra todo lo que lee su cuenta, también lo restringido; quien quiera verlo monta el suyo.
- **La ayuda** está dentro del tablero, en «Ayuda» del índice, y cada bloque lleva un «?» que abre su artículo.

## Actualizar

Cuando sale una versión nueva del plugin, la página del tablero y el generador cambian juntos, y **la cadena es automática**: la siguiente puesta al día (el botón, «sincroniza el tablero» o la tarea diaria si la hay) corre con el plugin nuevo, ve que la página es de otra versión, la republica sobre la misma URL y apunta la versión en `meta/estado` (`pagina_actualizada`); desde la 1.23.3 la página ya no lo avisa, porque no pide nada. Quien tenga el marketplace con actualización automática no hace nada; quien actualice el plugin a mano, lo hace y el resto viene en cadena. La tarea no lleva las instrucciones dentro: su prompt (`tarea-prompt.md`) solo manda leer `tarea.md` del plugin instalado, así que cada versión nueva cambia lo que hace la tarea sin que nadie apruebe nada. Solo si cambia ese prompt corto, Inicio lo marca y pide «actualiza el tablero» una vez.

«Actualiza el tablero», a mano o cuando la tarea lo pide:

1. Se busca el artifact por su nombre con `list_artifacts` (o `Artifact` `list`): «Tablero <organización>», o con « completo» si es de antes de la 1.18.
2. La página nueva va en la sincronización del paso 4, que la publica junto con los datos (paso 1d de `tarea.md`) y apunta `pagina_actualizada` en meta/estado con la versión nueva, la fecha de hoy y `desde` con la anterior: no se publica sola, porque desde la 1.24.1 la página lee sus datos de los archivos que van con ella. Lo marcado, el enfoque y las correcciones sobreviven.
3. Si el tablero no tiene tarea, se crea la del botón como en el paso 2 de montar. Si la tiene (cada mañana o solo el botón), se compara su prompt con `tarea-prompt.md` sustituido, con el MODO que ya dice su prompt (en los de antes de la 1.18, `publico` o `completo`: no se cambia por eso). Si cambió, se pide reescribirlo con `update_trigger`, y desde entonces las versiones nuevas llegan sin volver a pedirlo; en una tarea ligada a una computadora eso solo surte efecto cuando la persona lo aprueba en una conversación de la app ligada a esa misma computadora, y hasta entonces no cambia nada: se dice, no se rodea, y nunca se borra la tarea para crear otra, porque se pierde su historial y su computadora.
4. Se sincroniza una vez (abajo) para que `meta/estado` lleve la versión nueva y la banda de desfase desaparezca.

**Cambié de computadora.** La tarea del botón está ligada a la computadora donde se creó y a la ruta de la raíz en ella; con otra, cada pulsación falla aunque la nueva esté encendida. Desde una conversación de la app en la computadora nueva, con la raíz conectada: se busca la tarea por su nombre (`list_triggers`), se cambia con `update_trigger` su ruta (`{{RUTA_RAIZ}}` del prompt y `folders`) y se aprueba en la app, que la liga a esta computadora. Nunca se borra para crear otra, porque se pierde su historial. Después se sincroniza una vez para comprobarlo.

## Los tableros de antes de la 1.18

Hasta la 1.17 había dos modos, público y completo. **Nadie tiene que borrar ni volver a montar nada:** cada tablero pasa solo en su siguiente puesta al día con la 1.18 (con el botón, con «sincroniza el tablero» o con la tarea diaria), que republica la página en la misma dirección, con el nombre «Tablero <organización>», y genera todo lo que lee la cuenta.

- **Uno público** pasa a mostrarlo todo, y su página lo avisa una semana en Mantenimiento de Inicio, con que no se comparte y que, si se compartió, se quite el acceso desde su menú: el generador ve en la base que era público y escribe `paso_a_completo` con la fecha en `meta/estado`.
- **Uno completo** solo cambia de nombre.
- **Su tarea** conserva el nombre y el prompt que tenía («Regenerar tablero <organización> completo», o «MODO: publico» en el prompt). No hace falta tocarla: `tarea.md` encuentra su tarea por la URL del tablero que lleva el prompt, y el modo ya no cambia nada. Por eso «actualiza el tablero» no la reescribe por el modo.
- **Quien tenía los dos** de la misma raíz se queda con dos tableros iguales y dos tareas. Al abrir sesión (skill `sesion`) o al montar, sincronizar o actualizar, se dice una vez y se propone quedarse con el que era completo y borrar el otro (el que lleva `paso_a_completo` en `meta/estado`, o `modo: publico` si aún no se puso al día) con su tarea: `Artifact` con `delete` y `delete_trigger`, solo con su sí. Si dice que no, no se vuelve a proponer en esa conversación.

## Sincronizar

La puesta al día, en esta sesión, con la raíz conectada: los pasos 0 a 8 de `tarea.md` tal cual, con `cola.md`, `regenerar.md` y `juicio.md` cuando los piden (el 1c, `metodo.md`, se salta si esta misma sesión ya lo puso al día al abrir; las marcas de `cierres` las borra el último lote también en sesión), también su «SIN PEDIR NADA A NADIE», con la cuenta de la sesión en `--cuenta` y los scripts de la VM preparados como dice `tarea.md` (MODO, el que diga el prompt de su tarea, o `completo`); el id de la tarea, si la hay, se busca con `list_triggers` (la activa cuyo prompt lleva la URL del tablero) y se pasa al generador con `--tarea`, más `--manual` si no tiene horario; si no hay, se omite `--tarea`. Al empezar compara la huella de la raíz entera con la de la última sincronización: si nada cambió, solo anota la hora y termina. Si no, compara la huella de cada proyecto: de los que no cambiaron no trae nada y reutiliza su documento de la base, así que lo normal tras un cierre de sesión es traer guia.md, los area.md y un proyecto, y subir ese proyecto, su área y `meta/estado`. No lee la página. El cierre de sesión (skill `sesion`, anexo `cerrar.md`, paso 11) no la hace ni la lanza: apunta el cierre en la base, y la página, al abrirse, avisa de los cierres que aún no muestra con el botón que la pone al día. A mano sirve cuando otra persona trabajó en la carpeta o cuando la cola tiene cosas que no esperan a la siguiente sesión. Lo que la tarea deja «pendiente de cerrar en sesión» se cierra con `sesion`, que lee la cola al abrir el proyecto.

## La tarea del botón y la diaria

Es la misma tarea programada en los dos casos, con o sin horario, y en los dos la página tiene el botón «Sincronizar ahora». Hace falta el conector «Claude Code Remote»; se comprueba con `ToolSearch`.

- **Solo el botón**, la de siempre: se crea al montar. Para ponerlo al día cuando quiera sin pedírselo a Claude, sin que corra solo: por ejemplo, para traer lo que escribieron otras personas. La tarea se crea sin `cron_expression` ni `run_once_at`, así que nunca corre por su cuenta.
- **Cada mañana**: «pon el tablero al día cada mañana». Tiene sentido en una raíz donde escriben varias personas: sin ella, lo que escriben los demás no llega al tablero hasta que su responsable pulse el botón. De lunes a viernes a una hora de la mañana que no sea en punto (9:35 si no dicen otra).

Con `create_trigger`: nombre «Regenerar tablero <organización>», ligada a la computadora (`requires_local_device`) y con la carpeta de la raíz declarada en `folders`. El prompt es `tarea-prompt.md` de esta skill con sus cuatro huecos sustituidos (no `tarea.md`, que la tarea lee del plugin en cada corrida): `{{ORGANIZACION}}`, `{{RUTA_RAIZ}}` (la ruta absoluta de la raíz en la computadora), `{{URL}}` (la del artifact) y `{{MODO}}`, que es siempre `completo` (el hueco se queda para que el prompt de los tableros de antes de la 1.18 no cuente como desfasado). Si ya hay una tarea de ese tablero, se dice y se propone cambiarla en vez de crear otra, como en el paso 4 de «Actualizar». Después se sincroniza una vez pasando su id al generador, con `--manual` si no tiene horario, y el botón se enciende.

Al terminar se dicen dos cosas. **El modelo de la tarea:** nace con el de la sesión que la crea y solo se cambia en sus ajustes, en la app; conviene el mismo que para el método (Opus; la ayuda del tablero, «Qué modelo usar»). **La computadora encendida:** la tarea corre contra la carpeta sincronizada en la computadora de quien la creó; con el botón, tiene que estar encendida con la app abierta al pulsarlo; cada mañana, si está apagada a esa hora, avisa y reintenta hasta la una de la tarde.

## Los archivos del plugin en la computadora

La computadora no ve el plugin, y cada sesión empieza con el `$HOME` de su VM vacío. Hay dos casos:

- **`metodo.md`, al poner al día una raíz** (skill `sesion` al abrir, y el paso 1c de `tarea.md` en cada puesta al día, la lance quien la lance): va directo, sin descargar nada. Se copia el del plugin (el de la copia de versión más alta, si hay varias) a una carpeta nueva dentro de la de salidas del contenedor (`/mnt/project-files/` si existe, porque la conversación es de un proyecto; si no, `/mnt/user-data/outputs/`), con la versión y la hora en su nombre, `metodo-<versión>-<AAAAMMDDHHMMSS>/metodo.md`, nunca en una ruta ya usada en la sesión: con una ruta repetida la herramienta puede mandar la copia anterior sin avisar. Se escribe sobre el de la raíz con `device_commit_files` (`stagedPath`: esa copia; `devicePath`: la ruta de la raíz en la computadora, la de `get_device_info`, más `/metodo.md`) y se comprueba que la raíz dice la versión nueva: con consola, con `head -1`; sin ella, trayéndolo otra vez con `device_stage_files`. Si no la dice, se repite una vez con otra carpeta. Si esa herramienta no está o rechaza la escritura, se descarga como abajo (`metodo.md`, destino `$HOME/tablero`) y se copia a la raíz desde ahí, ya comprobado, sin preguntar.
- **Los scripts que corren en la computadora** (`abrir.py`, `cerrar.py` y `permisos.py` de `sesion`; `generar_vista.py` y `aplicar_cambios.py` de esta skill): `device_commit_files` solo escribe dentro de carpetas conectadas y los scripts no pueden ir a la raíz, así que se descargan. Sin consola no se descarga nada: corren en el contenedor, desde el plugin, sobre la copia.

**La descarga, siempre igual.** Nunca se pega el contenido de un archivo en un comando: cuesta decenas de miles de tokens y el control de permisos puede frenarlo como código nuevo. Con Bash, en el contenedor, `python3 <raíz del plugin>/preparar.py '<destino>' <rutas dentro del plugin>` (la raíz del plugin es `../..` desde el directorio de cualquier skill; el destino, `$HOME/tablero` o `$HOME/memoria`, entre comillas simples para que `$HOME` llegue sin expandir). Imprime la versión del plugin (VERSION), la primera línea de su `metodo.md` (METODO) y dos comandos para `device_bash`: DESCARGA trae cada archivo del repositorio público del plugin en la versión instalada, salvo los que ya están en el destino con su huella, y termina comprobándolos todos; REINTENTO es el mismo con `main`, para cuando la comprobación falla. De esas dos líneas se usa lo que va detrás de la etiqueta y su espacio, y detrás del comando se añade ` && <lo que se corre>`, que solo corre si todo cuadra. Si tampoco cuadra con REINTENTO, se copia el archivo con un heredoc con delimitador entre comillas simples (`cat > <destino> <<'EOF' … EOF`) y se vuelve a comprobar con `sha256sum`. Un archivo que no cuadra no se usa nunca, y el destino está siempre fuera de la raíz. Cada versión queda etiquetada en el repositorio sola, al llegar a `main` (una acción de GitHub la crea), así que la descarga por `v<versión>` funciona desde el primer día.

## Lo que nunca hago

Además de las prohibiciones de `convenciones` (anexo `escribir.md`):

- Pedir, para poner al día un tablero, acceso a otra carpeta que no sea la raíz, o pedirle a la persona que haga algo (añadir una carpeta, conectar, aprobar, pulsar). La puesta al día es invisible para quien la tiene; si algo falla, se dice en una línea y la siguiente lo reintenta.
- Pasar por la conversación el contenido de los documentos del tablero (con `cat`, pegado o como `data`): se generan en Claude y van como archivos del tablero, publicados desde disco; por la conversación pasa solo lo pequeño de la base (`tarea.md`, «SIN PEDIR NADA A NADIE»).

- Escribir en la raíz nada del tablero: ni el enlace, ni scripts, ni la salida del generador, ni la cola, ni un archivo de configuración. En la carpeta solo entra lo mecánico de la cola (fechas y hechos con nota), y solo donde la cuenta es responsable o colabora.
- Montar un tablero sin decir que no se comparte.
- Montar un segundo tablero de la misma raíz sin avisar de que ya existe.
- Cambiar desde aquí el modelo de una tarea, o borrar una tarea para recrearla con otro prompt.
- Escribir en `proyecto.md`, `sesiones.md` o `decisiones.md` desde la página. La página solo escribe en su cola.
- Cerrar un hecho que huela a decisión, o una nota, sin una sesión del proyecto.
- Compartir el tablero, o decirle a alguien cómo compartirlo: muestra lo restringido que lee la cuenta que lo montó. Quien quiera verlo monta el suyo.
- Borrar un tablero o su tarea sin el sí de quien lo montó, también el que sobra de quien tenía dos.

## Ejemplo

**Usuario:** monta el tablero

**Respuesta:**

> Montado. «Tablero Acme», con las 4 áreas y los 11 proyectos de la carpeta (`legal/` solo con nombre y responsable: tu cuenta no la lee) y «Por dónde empezar» con tres grupos.
>
> Se pone al día cuando quieras, con el botón junto a «Acme», arriba a la izquierda; al abrirlo te avisa si hay sesiones que aún no muestra. En Acme escriben cinco personas: si quieres ver lo de los demás cada mañana sin pulsar nada, puedo hacer que corra solo de lunes a viernes. Muestra todo lo que lee tu cuenta, así que es solo para ti: quien quiera uno, que lo monte. La ayuda está en el índice, en «Ayuda».
