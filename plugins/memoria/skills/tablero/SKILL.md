---
name: tablero
description: Monta, actualiza y sincroniza el tablero de una persona sobre la carpeta de su organizacion, una pagina que muestra la carpeta entera (areas, proyectos, estado, decisiones, siguientes pasos) generada desde los archivos y puesta al dia cuando quien lo monto lo pide, con el boton de la pagina o con 'sincroniza el tablero'. Usala cuando digan 'monta el tablero', 'monta mi tablero', 'quiero ver la carpeta sin abrirla', 'actualiza el tablero', 'sincroniza el tablero', 'regenera la vista', 'pon el tablero al dia cada manana', 'pon el boton de sincronizar', 'cambie de computadora' o pregunten por que el tablero no muestra algo.
---

# Tablero

Una página que muestra la carpeta de la organización sin abrirla, generada desde sus archivos. Antes de escribir en la carpeta se carga el anexo `escribir.md` de `convenciones`, cuyas prohibiciones aplican a todo lo que sigue; montar, y una sincronización con la cola vacía que solo pone al día `metodo.md` (una copia exacta del plugin), no lo necesitan.

Cinco reglas que no cambian:

- **El tablero es de una persona.** Lo monta cada quien desde su cuenta, sobre la raíz conectada, y corre con sus permisos: lo que esa cuenta no lee sale como «restringido», y lo que su puesta al día escribe en la carpeta lo escribe con sus permisos. Muestra todo lo que lee esa cuenta, también lo restringido y la bitácora, así que no se comparte: quien quiera verlo monta el suyo.
- **La carpeta es la fuente.** El tablero lee la superficie pública de la raíz (`guia.md`, los `area.md` y, de cada proyecto, `proyecto.md`, `decisiones.md`, `sesiones.md` y las cabeceras de `entregables/` y de `taller/`), más `base/premisas.md`. Nunca abre `fuentes/`, `restringido/` ni el resto de `base/`; del `taller/` lee solo cabecera y título, y de `fuentes/` y `taller/` mira las fechas, para avisar del trabajo sin sesión.
- **El tablero no escribe en la carpeta.** Lo que alguien toca en él espera en la cola de la página: la puesta al día escribe lo mecánico y la siguiente sesión del proyecto lo que pide juicio, y solo en las áreas y proyectos donde la cuenta que la lanza es responsable o colabora; lo de otra área espera en la cola, y el tablero dice a quién pasárselo.
- **Se pone al día cuando quien lo montó lo pide.** Esta es la frase, y es la misma en el contrato, en la receta de `nuevo`, en el README y en la ayuda. El cierre de una sesión no lanza nada (cada puesta al día gasta del plan): deja su marca en la colección `cierres` de la base, y la página, al abrirse, avisa con un punto en el botón «Sincronizar ahora» de los cierres que aún no muestra. Ese botón, junto al nombre de la organización, lanza la tarea del tablero (sin horario, creada al montarlo); también vale «sincroniza el tablero». Que corra cada mañana es opcional y se crea solo si lo piden.
- **Vive fuera de la raíz.** La página, sus archivos de datos, su base, los scripts y la tarea son de la cuenta de quien lo montó. En la carpeta no entra nada, ni un enlace: el tablero se encuentra por su nombre, que es fijo, entre los artifacts de la cuenta (así lo localiza `sesion` para leer su cola).

## Qué muestra

Un solo tablero por persona y raíz: todo lo que lee su cuenta; lo que no lee sale con su nombre y su responsable. Inicio, cada área y cada proyecto tienen cuatro pestañas, **Estatus · Acciones · Actividad · Qué hay** (en Inicio la última es **Mantenimiento**), y la Ayuda de la página («Ayuda» en el índice, y el «?» de cada bloque) explica cada una: para contar qué muestra, se lee de ahí y no se repite aquí. «Tarea» es la palabra de la página para cada línea de «Siguientes pasos».

En la carpeta de la skill: `vista.html` (la página), los scripts (`generar_vista.py`, `plan_subida.py`, `datos.py`, `aplicar_cambios.py`, `barrido.py`), los anexos de la puesta al día (`cola.md`, `regenerar.md` y `juicio.md`) `tarea-prompt.md` (el prompt de la tarea) y `tarea.md`, que solo redirige las tareas con el prompt de antes de la 1.24.9. Los pasos de la puesta al día son la skill `tarea-tablero`, que carga la tarea programada; en una sesión se leen de `../tarea-tablero/SKILL.md` desde este directorio. Nada de esto se copia a la raíz.

## Cuándo

**Montar**: "monta el tablero", "monta mi tablero", "quiero ver la carpeta entera sin abrirla". «Monta el tablero completo» o «el público», de quien conoció las versiones de antes, monta este mismo, y se dice en una línea que ya hay uno solo.

**Actualizar**: "actualiza el tablero", o cuando el tablero muestra que su página y el plugin corren versiones distintas.

**Sincronizar**: "sincroniza el tablero", "regenera la vista", "lo que marqué no aparece en la carpeta". Es la puesta al día a mano; la misma que lanza el botón de la página.

**Tarea diaria**: "pon el tablero al día cada mañana". Solo cuando la piden. El botón ya viene con el tablero; "pon el botón de sincronizar" en un tablero que no lo tiene es «Actualizar».

Si hay más de una raíz conectada, se pregunta cuál. Una sesión monta un solo tablero.

## Antes de montar

Cuatro comprobaciones, y en la primera que falle se dice qué falta y se para:

1. **La raíz conectada es completa**: tiene `guia.md` y `metodo.md` en su primer nivel. Si solo está conectada la carpeta de un área, el tablero no se puede montar.
2. **No hay ya uno** de esta raíz en esta cuenta (`list_artifacts`, o `Artifact` con `list`, y `list_triggers`): «Tablero <organización>» (o su nombre de antes de la 1.18, abajo). Si lo hay, se ofrece actualizar o sincronizar.
3. **La cuenta tiene lo que hace falta**: las herramientas del tablero (el conector `claude-artifacts`, o las de antes, `Artifact` y `ArtifactData`: «DÓNDE ESTÁ CADA COSA» de la skill `tarea-tablero`), con las capacidades de base de datos, usuario y conector, `device_stage_files` y `device_commit_files`. Se comprueba con `ToolSearch`; lo que no esté se nombra.
4. **La computadora está disponible** y la raíz conectada. Con consola, la raíz se ve en `$HOME/mnt/` del shell, y si no aparece se pide con `device_request_folder_access` por su ruta. Si el shell dice que no pudo montarla, es «SIN CONSOLA» de la skill `tarea-tablero`: no se pide nada y se monta igual, sobre una copia.

## Montar

**1. Publicar la página.** `python3 <directorio de la skill>/datos.py pagina <directorio de la skill>/vista.html <scratchpad>/pagina --titulo "Tablero <organización>"` (<organización>: lo que va antes del «·» en el título de `guia.md`) deja la portada `index.html` y su código en `vista-<versión>.css` y `.js`. Se publica como artifact nuevo con el icono `dashboard` y ese título: `publish_files`, sin `slug`, con los «archivos» que imprimió tal cual; o `Artifact`, con `index.html` como `file_path` y los otros dos en `files`. Y esta declaración de capacidades, idéntica para todos los tableros (con el conector, `mcp__claude-artifacts__declare_capabilities` justo después de publicar; con `Artifact`, en la misma publicación):

```
db: reglas [{path: "", read: "view", write: "admin"}, {path: "cambios", read: "view", write: "interact"}]
user: {}
mcp: servers [{server: "Claude Code Remote", tools: ["fire_trigger"]}]
```

Con eso quien lo montó lo ve, actúa desde él y lanza la sincronización; la base la escriben la tarea y los editores. La regla de `cambios` se queda igual en todos para que ninguno tenga que volver a publicarse con otras capacidades.

**2. La tarea del botón.** Se crea siempre, sin horario, como dice «La tarea del botón y la diaria» abajo, y su id se pasa al generador en el paso 3 con `--manual`; si la persona pide además que corra cada mañana, se crea con horario en vez de sin él. Crearla pide una aprobación en la app, que forma parte de montar. Si falta el conector «Claude Code Remote», se monta igual, con el botón apagado diciendo que falta el conector, y se dice en una línea.

**3. Generar.** Los pasos 0, 1 y 5 de la skill `tarea-tablero` y `regenerar.md` tal cual (la versión de partida es la que devolvió la publicación del paso 1; sin consola, con su «SIN CONSOLA»), como la primera vez (`--primera-vez`, `--sin-archivos`). Ningún documento pasa por la conversación.

**4. El primer «Por dónde empezar», y publicar.** El paso 6 de `regenerar.md` (cómo, en `juicio.md`), antes de publicar: si no, la página sale sin esa sección hasta la siguiente puesta al día. Después, PUBLICAR de la skill `tarea-tablero`, con `--vista` y `--enfoque`.

**5. Comprobar.** Se abre el artifact (el `Artifact` con `open`, o se da el enlace) y se mira que pinte la raíz con sus áreas.

### Qué respondo al terminar

Cuatro líneas, sin recapitular los pasos:

- Qué quedó montado: el tablero, con lo que muestra.
- **Cuándo se pone al día:** cuando quien lo montó lo pide, con el botón junto al nombre de la organización o con «sincroniza el tablero», con la computadora encendida y la app abierta; al abrirlo avisa de las sesiones cerradas que aún no muestra. Si en esa raíz escriben varias personas, se ofrece la tarea diaria en una línea.
- **No se comparte:** muestra todo lo que lee su cuenta, también lo restringido; quien quiera verlo monta el suyo.
- **La ayuda** está dentro del tablero, en «Ayuda» del índice, y cada bloque lleva un «?» que abre su artículo.

## Actualizar

Con una versión nueva del plugin, **la cadena es automática**: la siguiente puesta al día corre con el plugin nuevo, ve que la página es de otra versión y la republica en la misma URL (paso 1d de la skill `tarea-tablero`). La tarea carga la skill del plugin instalado (`tarea-prompt.md`), así que cada versión cambia lo que hace sin que nadie apruebe nada; solo si cambia ese prompt corto, Inicio lo marca y pide «actualiza el tablero» una vez.

«Actualiza el tablero», a mano o cuando la tarea lo pide:

1. Se busca el artifact por su nombre con `list_artifacts` (o `Artifact` `list`): «Tablero <organización>» (o su nombre de antes de la 1.18).
2. La página nueva va en la sincronización del paso 4, junto con los datos (paso 1d de la skill `tarea-tablero`): no se publica sola. Lo marcado, el enfoque y las correcciones sobreviven.
3. Si el tablero no tiene tarea, se crea la del botón como en el paso 2 de montar. Si la tiene, se compara su prompt con `tarea-prompt.md` sustituido, con el MODO que ya dice su prompt. Si cambió, se pide reescribirlo con `update_trigger`; en una tarea ligada a una computadora solo surte efecto cuando la persona lo aprueba en la app de esa computadora, y hasta entonces se dice, no se rodea. Nunca se borra la tarea para crear otra: se pierde su historial y su computadora.
4. Se sincroniza una vez (abajo) para que `meta/estado` lleve la versión nueva.

**Cambié de computadora.** La tarea está ligada a la computadora donde se creó y a la ruta de la raíz en ella. Desde una conversación de la app en la computadora nueva, con la raíz conectada: se busca la tarea por su nombre (`list_triggers`), se cambia con `update_trigger` su ruta (`{{RUTA_RAIZ}}` del prompt y `folders`) y se aprueba en la app. Nunca se borra para crear otra. Después se sincroniza una vez.

## Los tableros de antes de la 1.18

Hasta la 1.17 había dos modos, público y completo; cada tablero pasa solo al de ahora en su siguiente puesta al día, y su tarea, con el nombre y el prompt de antes, no se toca. Se llaman «Tablero <organización> completo», y su prompt dice MODO `publico` o `completo`, que no se cambia. **Quien tenía los dos** de la misma raíz se queda con dos tableros iguales: al abrir sesión, montar, sincronizar o actualizar se dice una vez y se propone quedarse con el que era completo y borrar el otro (el que lleva `paso_a_completo`, o `modo: publico` si aún no se puso al día) con su tarea, `Artifact` con `delete` y `delete_trigger`, solo con su sí; si dice que no, no se vuelve a proponer en esa conversación.

## Sincronizar

La puesta al día en esta sesión, con la raíz conectada: los pasos 0 a 8 de `../tarea-tablero/SKILL.md` tal cual, con sus anexos cuando los piden y su «SIN PEDIR NADA A NADIE», con la cuenta de la sesión en `--cuenta` (MODO, el del prompt de su tarea, o `completo`; el 1c se salta si esta sesión ya puso al día `metodo.md` al abrir). El id de la tarea, si la hay, se busca con `list_triggers` (la activa cuyo prompt lleva la URL del tablero). Sirve cuando otra persona trabajó en la carpeta o cuando la cola tiene cosas que no esperan a la siguiente sesión; lo que queda «pendiente de cerrar en sesión» lo cierra `sesion` al abrir el proyecto.

## La tarea del botón y la diaria

Es la misma tarea programada en los dos casos, con o sin horario, y en los dos la página tiene el botón «Sincronizar ahora». Hace falta el conector «Claude Code Remote»; se comprueba con `ToolSearch`.

- **Solo el botón**, la de siempre: se crea al montar, sin `cron_expression` ni `run_once_at`, así que solo corre cuando se pulsa.
- **Cada mañana**, si la piden: de lunes a viernes a una hora de la mañana que no sea en punto (9:35 si no dicen otra).

Con `create_trigger`: nombre «Regenerar tablero <organización>», ligada a la computadora (`requires_local_device`) y con la carpeta de la raíz en `folders`. El prompt es `tarea-prompt.md` con sus cuatro huecos sustituidos: `{{ORGANIZACION}}`, `{{RUTA_RAIZ}}` (la ruta absoluta de la raíz en la computadora), `{{URL}}` (la del artifact) y `{{MODO}}`, siempre `completo`. Si ya hay una tarea de ese tablero, se propone cambiarla como en el paso 3 de «Actualizar». Después se sincroniza una vez pasando su id al generador, con `--manual` si no tiene horario, y el botón se enciende.

Al terminar se dicen dos cosas. **El modelo de la tarea:** nace con el de la sesión que la crea y solo se cambia en sus ajustes, en la app; conviene Opus. **La computadora encendida:** con el botón, encendida y con la app abierta al pulsarlo; cada mañana, si está apagada a esa hora, avisa y reintenta hasta la una de la tarde.

## Los archivos del plugin en la computadora

La computadora no ve el plugin, y cada sesión empieza con el `$HOME` de su VM vacío. Hay dos casos:

- **`metodo.md`, al poner al día una raíz** (`sesion` al abrir, y el paso 1c de la skill `tarea-tablero`): va directo. Se copia el del plugin que se está usando (`../../metodo.md` desde el directorio de la skill; nunca se buscan otras copias con `find`) a una carpeta de salidas del contenedor (`/mnt/project-files/` si existe; si no, `/mnt/user-data/outputs/`), `metodo-<versión>/metodo.md`, una por versión, que se reutiliza (`abrir.py --metodo-para-subir` la hace y la comprueba: el contenido no cambia dentro de una versión, así que una copia anterior es la misma). Se escribe sobre el de la raíz con `device_commit_files` (`stagedPath`: esa copia; `devicePath`: la ruta de la raíz de `get_device_info` más `/metodo.md`) y se comprueba que la raíz dice la versión nueva: con consola, con `head -1`; sin ella, trayéndolo con `device_stage_files`. Si no la dice, se repite una vez con otra carpeta. Si esa herramienta no está o rechaza la escritura, se descarga como abajo (destino `$HOME/tablero`) y se copia desde ahí, ya comprobado.
- **Los scripts que corren en la computadora** (`abrir.py`, `cerrar.py` y `permisos.py` de `sesion`; `generar_vista.py` y `aplicar_cambios.py` de esta skill) no pueden ir a la raíz, así que se descargan. Sin consola no se descarga nada: corren en el contenedor, sobre la copia.

**La descarga, siempre igual.** Nunca se pega el contenido de un archivo en un comando. Con Bash, en el contenedor, `python3 <raíz del plugin>/preparar.py '<destino>' <rutas dentro del plugin>` (la raíz del plugin es `../..` desde cualquier skill; el destino, `$HOME/tablero` o `$HOME/memoria`, entre comillas simples). Imprime VERSION, METODO y dos comandos para `device_bash`: DESCARGA trae los archivos del repositorio público en la versión instalada y los comprueba; REINTENTO, lo mismo con `main`. Se usa lo que va detrás de la etiqueta y su espacio, seguido de ` && <lo que se corre>`. Si tampoco cuadra, se copia el archivo con un heredoc con delimitador entre comillas simples y se comprueba con `sha256sum`. Un archivo que no cuadra no se usa nunca, y el destino está siempre fuera de la raíz.

## Lo que nunca hago

Además de las prohibiciones de `convenciones` (anexo `escribir.md`):

- Pasar por la conversación el contenido de los documentos del tablero (con `cat`, pegado o como `data`).
- Escribir en la raíz nada del tablero (ni el enlace, ni scripts, ni salidas, ni la cola): en la carpeta solo entra lo mecánico de la cola.
- Montar un tablero sin decir que no se comparte.
- Cerrar un hecho que huela a decisión, o una nota, sin una sesión del proyecto.
- Compartir el tablero, o decirle a alguien cómo compartirlo.

## Ejemplo

**Usuario:** monta el tablero

**Respuesta:**

> Montado. «Tablero Acme», con las 4 áreas y los 11 proyectos de la carpeta (`legal/` solo con nombre y responsable: tu cuenta no la lee) y «Por dónde empezar» con tres grupos.
>
> Se pone al día cuando quieras, con el botón junto a «Acme», arriba a la izquierda; al abrirlo, un punto en ese botón te avisa si hay sesiones que aún no muestra. En Acme escriben cinco personas: si quieres ver lo de los demás cada mañana sin pulsar nada, puedo hacer que corra solo de lunes a viernes. Muestra todo lo que lee tu cuenta, así que es solo para ti: quien quiera uno, que lo monte. La ayuda está en el índice, en «Ayuda».
