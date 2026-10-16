---
name: tablero
description: Monta, actualiza y sincroniza el tablero de una persona sobre la carpeta de su organizacion, una pagina que muestra la carpeta entera (areas, proyectos, estado, decisiones, siguientes pasos) generada desde los archivos y puesta al dia al cerrar cada sesion. Usala cuando digan 'monta el tablero', 'monta mi tablero', 'quiero ver la carpeta sin abrirla', 'actualiza el tablero', 'sincroniza el tablero', 'regenera la vista', 'pon el tablero al dia cada manana', 'pon el boton de sincronizar' o pregunten por que el tablero no muestra algo.
---

# Tablero

Una página que muestra la carpeta de la organización sin abrirla: qué áreas hay y de quién son, en qué va cada proyecto, qué se decidió, qué entregables hay y qué pasos siguen. Se genera desde los archivos y se pone al día cada vez que su dueño cierra una sesión. Antes de nada se carga `convenciones`: sus prohibiciones aplican a todo lo que sigue.

Cinco reglas que no cambian:

- **El tablero es de una persona.** Lo monta cada quien desde su propia cuenta, sobre la raíz conectada, y corre con sus permisos: lo que esa cuenta no puede leer en la carpeta sale como «restringido», y lo que su puesta al día escribe en la carpeta lo escribe con sus permisos. El de quien administra la carpeta es uno más. Su dueño puede compartirlo desde el menú del artifact, y esa es la única manera de que otra persona lo vea.
- **La carpeta es la fuente.** El tablero lee la superficie pública de la raíz (`guia.md`, los `area.md` y, de cada proyecto, `proyecto.md`, `decisiones.md`, `sesiones.md` y las cabeceras de `entregables/`) y nada más. Nunca abre `fuentes/`, `taller/`, `restringido/` ni `base/`, salvo `base/premisas.md`, que es de toda la organización y va arriba de todo; de `fuentes/` y `taller/` solo mira las fechas de los archivos, para avisar del trabajo sin sesión.
- **El tablero no escribe en la carpeta.** Lo que alguien toca en él (fechar un paso, marcarlo hecho, anotar algo, corregir un estado) espera en una cola propia de la página, y lo escribe quien tiene contexto: la puesta al día lo mecánico, la siguiente sesión del proyecto lo que pide juicio. Y la puesta al día escribe solo en las áreas de la cuenta que la lanza: lo que un contribuidor marcó en un proyecto de otra área espera en la cola a que su dueño ponga al día su tablero o cierre una sesión.
- **Se pone al día al cerrar sesión.** Desde la 1.14, el cierre de cada sesión de su dueño (skill `sesion`, paso 11) rehace el tablero entero y aplica lo mecánico de la cola. No hay tarea programada por defecto: se crea solo si la piden, para tener el botón «Sincronizar ahora» o para que corra cada mañana, por ejemplo en una raíz donde escriben varias personas, porque lo que escriben los demás no llega a un tablero hasta que su dueño cierra una sesión o sincroniza.
- **Vive fuera de la raíz.** La página, su base de datos, los scripts y la tarea, si la hay, son de la cuenta de su dueño. En la carpeta de la organización no entra nada: ni un enlace. El tablero se encuentra por su nombre, que es fijo, entre los artifacts de la cuenta; es así como `sesion` lo localiza para leer su cola, sin que nadie apunte la URL en ningún sitio.

## Dos modos

| | Público | Completo |
|---|---|---|
| Qué muestra | La superficie pública del contrato: `area.md`, `proyecto.md`, decisiones, entregables. De un área cuya columna «Quién la lee» diga «Restringida», y de un proyecto cuya línea del índice empiece por «restringido» o que no esté en el índice, solo nombre y dueño, aunque tu cuenta pueda leerlos. De cada sesión, solo fecha y título | Todo lo que tu cuenta lee, incluidas las áreas y proyectos restringidos a los que tienes acceso, con las cinco sesiones más recientes enteras |
| Para quién | Para compartirlo con cualquiera de la organización | Para ti. Lleva una marca fija que dice que no se comparte |
| Frase | «monta el tablero» (es el modo por defecto) | «monta el tablero completo», «monta el tablero con todo» |

Una persona puede tener los dos sobre la misma raíz. Antes de montar uno, la skill mira si ya existe un tablero con ese nombre y ese modo en la cuenta (`Artifact` con `list`) o una tarea con ese nombre (`list_triggers`); si existe, lo dice y propone actualizarlo o sincronizarlo en vez de montar otro. Un duplicado no rompe nada, pero son dos tareas y dos colas para lo mismo.

Lo que trae esta skill, en su carpeta: `vista.html` (la página), `generar_vista.py` (lee la raíz y produce los documentos de la base, en dos tiempos: un inventario corto en la computadora y la generación en Claude sobre una copia de lo que lee), `plan_subida.py` (dice qué documentos cambiaron y los reparte en lotes), `aplicar_cambios.py` (escribe en la carpeta lo mecánico de la cola) y `tarea.md` (los pasos de la puesta al día, que siguen al pie de la letra la sincronización, el cierre de sesión y la tarea diaria cuando la hay; con cuatro huecos). Nada de esto se copia a la raíz.

## Cuándo

**Montar**: "monta el tablero", "monta mi tablero", "monta el tablero completo", "quiero ver la carpeta entera sin abrirla".

**Actualizar**: "actualiza el tablero", o cuando el tablero muestra que su página y el plugin corren versiones distintas.

**Sincronizar**: "sincroniza el tablero", "regenera la vista", "lo que marqué no aparece en la carpeta". Es la puesta al día a mano; la misma que hace cada cierre de sesión.

**Botón o tarea diaria**: "pon el botón de sincronizar", "quiero sincronizarlo yo cuando quiera", "pon el tablero al día cada mañana". Solo cuando la piden.

Si hay más de una raíz conectada, se pregunta cuál. Una sesión monta un solo tablero.

## Antes de montar

Cuatro comprobaciones, y en la primera que falle se dice qué falta y se para:

1. **La raíz conectada es completa**: tiene `guia.md` y `metodo.md` en su primer nivel. Si solo está conectada la carpeta de un área, el tablero no se puede montar.
2. **No hay ya uno igual** en esta cuenta: mismo nombre («Tablero <organización>» o «Tablero <organización> completo»). Si lo hay, se ofrece actualizar o sincronizar.
3. **La cuenta tiene lo que hace falta**: la herramienta `Artifact` con las capacidades de base de datos, usuario y conector; `ArtifactData`; el shell de la computadora (`device_bash`), porque el inventario y la cola corren contra la carpeta sincronizada en ella; y `device_stage_files`, que trae a Claude la copia de lo que el tablero lee. Se comprueba con `ToolSearch`; lo que no esté se nombra.
4. **La computadora está disponible** y la raíz se ve en `$HOME/mnt/` del shell. Si no, se pide con `device_request_folder_access` por su ruta.

Si el modo es público y la cuenta de la sesión lee áreas o proyectos restringidos, se avisa de una cosa antes de seguir: lo restringido queda fuera solo si está declarado (la columna «Quién la lee» en `guia.md`, la palabra «restringido» al inicio de la línea del proyecto en `area.md`); un proyecto restringido en Drive que nadie declaró entraría en el tablero público. Si hay duda, se monta el completo y no se comparte.

## Montar

**1. Publicar la página.** Se copia `vista.html` de esta skill al scratchpad con el nombre `tablero.html`, se sustituye su primera línea `<title>Tablero</title>` por `<title>Tablero <organización></title>` (y « completo» al final si es ese modo; <organización> es el nombre de la organización: lo que va antes del «·» en el título de `guia.md`, `convenciones` sección 1), y se publica como artifact nuevo con el icono `dashboard`, y esta declaración de capacidades, idéntica para todos los tableros:

```
db: reglas [{path: "", read: "view", write: "admin"}, {path: "cambios", read: "view", write: "interact"}]
user: {}
mcp: servers [{server: "Claude Code Remote", tools: ["fire_trigger"]}]
```

Con eso el dueño lo ve y lanza la sincronización; si lo comparte, un lector lee y un contribuidor puede además fechar, marcar y anotar (escribe solo en la cola); la base la escriben la tarea y los editores.

**2. Sin tarea programada.** No se crea ninguna: el tablero se pondrá al día en cada cierre de sesión. Si la persona pide el botón o la tarea diaria al montar, se crea como dice «Botón o tarea diaria» abajo y su id se pasa al generador en el paso 3.

**3. Generar y cargar.** Es el paso 5 de `tarea.md` tal cual, con la base todavía vacía: inventario en la computadora, copia de los archivos con `device_stage_files`, generación en Claude, `plan_subida.py` (con la base vacía lo propone todo) y lotes de `ArtifactData` con `file_path`. Ningún documento pasa por la conversación. En `meta/estado` se añade `pagina_actualizada: {version: <versión del plugin>, fecha: <hoy>}`, que es como la puesta al día sabe qué versión de la página hay publicada sin leerla.

**4. El primer «Por dónde empezar».** Es el paso 6 de `tarea.md` y se hace aquí mismo, porque la página saldría sin esa sección hasta el primer cierre de sesión: se leen los grupos candidatos de `salida/meta/enfoque-candidatos.json` y los pasos con sus señales, se eligen tres o cuatro grupos con los tres criterios (prioridad del área, cliente o dinero, desbloquea a otros; vencido no suma) y se escribe `enfoque/actual`.

**5. Comprobar.** Se abre el artifact (`Artifact` con `open`) y se mira que pinte la raíz con sus áreas y que `meta/estado` tenga el modo y la versión.

### Qué respondo al terminar

Cuatro líneas, sin recapitular los pasos:

- Qué quedó montado: el tablero y su modo.
- **Cuándo se pone al día:** cada vez que su dueño cierra una sesión; lo que escriban otras personas, con «sincroniza el tablero». Si en esa raíz escriben varias personas, se ofrece la tarea diaria en una línea.
- **Compartir**, solo si es público: desde el menú del artifact, como contribuidor a quien vaya a actuar desde él, como lector al resto. Si es completo, que no se comparte.
- **La ayuda** está dentro del tablero, en «Ayuda» del índice, y cada bloque lleva un «?» que abre su artículo.

## Actualizar

Cuando sale una versión nueva del plugin, la página del tablero y el generador cambian juntos, y **la cadena es automática**: la siguiente puesta al día (un cierre de sesión, una sincronización o la tarea diaria si la hay) corre con el plugin nuevo, ve que la página es de otra versión, la republica sobre la misma URL y deja en Inicio el aviso «El tablero se actualizó a la versión X» durante una semana. Quien tenga el marketplace con actualización automática no hace nada; quien actualice el plugin a mano, lo hace y el resto viene en cadena. Lo único que una tarea diaria no puede hacer sola es reescribir su propio prompt: si `tarea.md` cambió, lo marca en Inicio y pide «actualiza el tablero».

«Actualiza el tablero», a mano o cuando la tarea lo pide:

1. Se busca el artifact por su nombre con `Artifact` `list`.
2. Se vuelve a publicar `vista.html` de esta skill sobre esa URL (`Artifact` con `url`), con el `<title>` sustituido como en el paso 1 de montar y sin pasar `capabilities`, para que conserve las que tiene. La base no se toca, salvo `pagina_actualizada` en `meta/estado`, que pasa a la versión nueva con la fecha de hoy y `desde` con la anterior: la cola, el enfoque y las correcciones sobreviven.
3. Si hay tarea programada (cada mañana o solo el botón), se compara su prompt con `tarea.md` sustituido. Si cambió, se pide reescribirlo con `update_trigger`; en una tarea ligada a una computadora eso solo surte efecto cuando la persona lo aprueba en una conversación de la app ligada a esa misma computadora, y hasta entonces no cambia nada: se dice, no se rodea, y nunca se borra la tarea para crear otra, porque se pierde su historial y su computadora.
4. **Una tarea diaria de antes de la 1.14** se queda donde está, pero se pregunta en una línea qué se quiere ahora que el tablero se pone al día al cerrar cada sesión: que siga cada mañana, solo el botón, o nada. Si es nada, se desactiva con `update_trigger` (`enabled: false`); nunca se borra, porque se pierde su historial. Si es solo el botón, se desactiva igual y se crea una sin horario como dice «Botón o tarea diaria». Si sigue, se recuerda revisar su modelo en sus ajustes.
5. Se sincroniza una vez (abajo) para que `meta/estado` lleve la versión nueva y la banda de desfase desaparezca.

## Sincronizar

La puesta al día, en esta sesión, con la raíz conectada: los pasos 1 a 7 de `tarea.md` tal cual, también su «SIN PEDIR NADA A NADIE», con la cuenta de la sesión en `--cuenta`, los scripts de la VM comparados por huella y traídos solo si cambiaron, y el modo del tablero; el id de la tarea, si la hay, se busca con `list_triggers` (la activa, por su nombre) y se pasa al generador con `--tarea`, más `--manual` si no tiene horario; si no hay, se omite `--tarea`. Sube a la base solo los documentos cuya huella cambió y no lee la página: lo normal al cerrar una sesión es un proyecto, su área y `meta/estado`. Es lo que hace cada cierre de sesión (skill `sesion`, paso 11), y a mano sirve cuando otra persona trabajó en la carpeta o cuando la cola tiene cosas que no esperan a la siguiente sesión. Lo que la tarea deja «pendiente de cerrar en sesión» se cierra con `sesion`, que lee la cola al abrir el proyecto.

## Botón o tarea diaria, si los piden

Es la misma tarea programada en los dos casos, con o sin horario, y en los dos la página gana el botón «Sincronizar ahora». Hace falta el conector «Claude Code Remote»; se comprueba con `ToolSearch`.

- **Solo el botón**: «pon el botón de sincronizar». Para quien quiere ponerlo al día cuando quiera sin pedírselo a Claude, sin que corra solo: por ejemplo, el tablero de una raíz donde escribe sobre todo otra persona. La tarea se crea sin `cron_expression` ni `run_once_at`, así que nunca corre por su cuenta.
- **Cada mañana**: «pon el tablero al día cada mañana». Tiene sentido en una raíz donde escriben varias personas: sin ella, lo que escriben los demás no llega al tablero hasta el siguiente cierre de sesión de su dueño. De lunes a viernes a una hora de la mañana que no sea en punto (9:35 si no dicen otra).

Con `create_trigger`: nombre «Regenerar tablero <organización>» (con « completo» si lo es), ligada a la computadora (`requires_local_device`) y con la carpeta de la raíz declarada en `folders`. El prompt es `tarea.md` de esta skill con sus cuatro huecos sustituidos: `{{ORGANIZACION}}`, `{{RUTA_RAIZ}}` (la ruta absoluta de la raíz en la computadora), `{{URL}}` (la del artifact) y `{{MODO}}` (`publico` o `completo`). Si ya hay una tarea con ese nombre, se dice y se propone cambiarla en vez de crear otra: de una diaria a solo el botón, se desactiva la diaria (nunca se borra) y se crea la nueva. Después se sincroniza una vez pasando su id al generador, con `--manual` si no tiene horario, y la página gana el botón.

Al terminar se dicen dos cosas. **El modelo de la tarea:** nace con el de la sesión que la crea y solo se cambia en sus ajustes, en la app; basta el intermedio vigente. **La computadora encendida:** la tarea corre contra la carpeta sincronizada en la computadora de quien la creó; con el botón, tiene que estar encendida con la app abierta al pulsarlo; cada mañana, si está apagada a esa hora, avisa y reintenta hasta la una de la tarde.

## Los archivos del plugin en la computadora

La computadora no ve el plugin, y cada sesión empieza con el `$HOME` de su VM vacío. Hay dos casos:

- **`metodo.md`, al poner al día una raíz** (skill `sesion`): va directo, sin descargar nada. Se copia el del plugin a `/mnt/user-data/outputs/metodo.md` del contenedor y se escribe sobre el de la raíz con `device_commit_files` (`devicePath`: la ruta de la raíz en la computadora, la de `get_device_info`, más `/metodo.md`). Si esa herramienta no está, se usa la descarga de abajo.
- **Los dos scripts que corren en la computadora** (`generar_vista.py`, para el inventario, y `aplicar_cambios.py`): `device_commit_files` solo escribe dentro de carpetas conectadas y los scripts no pueden ir a la raíz, así que se descargan.

Para descargar no se pega el contenido en un comando: cuesta decenas de miles de tokens y el control de permisos puede frenarlo como código nuevo. Se descarga del repositorio público del plugin, en la versión instalada, y se comprueba que es idéntico:

1. Con `device_bash`: `mkdir -p $HOME/tablero && curl -sfL -o <destino> https://raw.githubusercontent.com/TuOpinas/memoria/v<versión>/plugins/memoria/<ruta dentro del plugin>` y `sha256sum <destino>`. La versión es la de `plugin.json`; la ruta, por ejemplo, `skills/tablero/generar_vista.py` o `metodo.md`.
2. Con Bash, `sha256sum` del mismo archivo en el plugin. Si coinciden, se usa.
3. Si no coinciden o la descarga falla, se prueba una vez con `main` en lugar de `v<versión>`. Si tampoco, se copia con un heredoc con delimitador entre comillas simples (`cat > <destino> <<'EOF' … EOF`).

Un archivo descargado que no coincide no se usa nunca. El destino es siempre `$HOME/tablero/` de la VM, fuera de la raíz; `metodo.md`, cuando va por aquí, se copia a la raíz desde ahí, ya comprobado. Los scripts que ya estén en `$HOME/tablero/` con la huella del plugin no se vuelven a traer. Cada versión queda etiquetada en el repositorio sola, al llegar a `main` (una acción de GitHub la crea), así que la descarga por `v<versión>` funciona desde el primer día.

## Lo que nunca hago

Además de las prohibiciones de `convenciones`:

- Pedir, para poner al día un tablero, acceso a otra carpeta que no sea la raíz, o pedirle a la persona que haga algo (añadir una carpeta, conectar, aprobar, pulsar). La puesta al día es invisible para quien la tiene; si algo falla, se dice en una línea y la siguiente lo reintenta.
- Pasar por la conversación el contenido de los documentos del tablero (con `cat`, pegado o como `data`): se generan en Claude y se suben con `file_path`.

- Escribir en la raíz nada del tablero: ni el enlace, ni scripts, ni la salida del generador, ni la cola, ni un archivo de configuración. En la carpeta solo entra lo mecánico de la cola (fechas y hechos con nota), y solo en las áreas de la cuenta.
- Montar un tablero completo sin decir que no se comparte, o montar uno público sin avisar de lo restringido no declarado cuando la cuenta lo lee.
- Montar un segundo tablero igual sin avisar de que ya existe.
- Cambiar desde aquí el modelo de una tarea, o borrar una tarea para recrearla con otro prompt.
- Escribir en `proyecto.md`, `sesiones.md` o `decisiones.md` desde la página. La página solo escribe en su cola.
- Cerrar un hecho que huela a decisión, o una nota, sin una sesión del proyecto.
- Compartir el tablero: lo comparte su dueño desde el menú del artifact.

## Ejemplo

**Usuario:** monta el tablero

**Respuesta:**

> Montado. «Tablero Acme», público, con las 4 áreas y los 11 proyectos de la carpeta (`legal/` solo con nombre y dueño, como dice `guia.md`) y «Por dónde empezar» con tres grupos.
>
> Se pone al día cada vez que cierras una sesión. En Acme escriben cinco personas: si quieres ver lo de los demás sin esperar a tu siguiente cierre, puedo añadir una tarea que lo ponga al día cada mañana. Compartirlo, si quieres, desde su menú: como contribuidor a quien vaya a fechar o marcar pasos, como lector al resto. La ayuda está en el índice, en «Ayuda».
