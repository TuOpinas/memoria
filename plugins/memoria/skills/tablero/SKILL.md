---
name: tablero
description: Monta, actualiza y sincroniza el tablero de una organizacion, una pagina que muestra su carpeta entera (areas, proyectos, estado, decisiones, siguientes pasos) generada desde los archivos y puesta al dia por una tarea diaria. Usala cuando digan 'monta el tablero', 'quiero ver la carpeta sin abrirla', 'actualiza el tablero', 'sincroniza el tablero', 'regenera la vista' o pregunten por que el tablero no muestra algo.
---

# Tablero

Una página por raíz que muestra la organización entera sin abrir carpetas: qué áreas hay y de quién son, en qué va cada proyecto, qué se decidió, qué entregables hay y qué pasos siguen. Se genera desde los archivos y se pone al día sola. Antes de nada se carga `convenciones`: sus prohibiciones aplican a todo lo que sigue.

Tres reglas que no cambian:

- **La carpeta es la fuente.** El tablero lee la superficie pública de la raíz (`guia.md`, los `area.md` y, de cada proyecto, `proyecto.md`, `decisiones.md`, `sesiones.md` y las cabeceras de `entregables/`) y nada más. Nunca abre `fuentes/`, `taller/`, `restringido/` ni `base/`; de un área o un proyecto restringido muestra el nombre y el dueño, que ya están listados.
- **El tablero no escribe en la carpeta.** Lo que alguien toca en él (fechar un paso, marcarlo hecho, anotar algo, corregir un estado) espera en una cola propia de la página, y lo escribe quien tiene contexto: la tarea diaria lo mecánico, la siguiente sesión del proyecto lo que pide juicio. Nada entra en un archivo sin pasar por el método.
- **Vive fuera de la raíz.** La página, su base de datos y la tarea son de la cuenta de quien administra la carpeta. En la raíz solo queda una línea en `guia.md` con el enlace. Ningún script, salida ni dato de la aplicación entra en la carpeta de la organización.

Lo que trae esta skill, en su carpeta: `vista.html` (la página), `generar_vista.py` (lee la raíz y produce los documentos de la base), `aplicar_cambios.py` (escribe en la carpeta lo mecánico de la cola) y `tarea.md` (el prompt de la tarea diaria, con tres huecos). Nada de esto se copia a la raíz.

## Cuándo

**Montar**: "monta el tablero", "quiero ver la carpeta entera sin abrirla", "arranca la vista de la organización".

**Actualizar**: "actualiza el tablero", o cuando el tablero muestra que su página y el plugin corren versiones distintas.

**Sincronizar**: "sincroniza el tablero", "regenera la vista", "lo que marqué no aparece en la carpeta". Es la tarea diaria a mano.

Si no queda claro de qué raíz se habla, se pregunta. Una sesión monta un solo tablero sobre la raíz conectada.

## Antes de montar

Cinco comprobaciones, y en la primera que falle se dice qué falta y se para:

1. **La raíz conectada es completa**: tiene `guia.md` y `metodo.md` en su primer nivel. Si solo está conectada la carpeta de un área, el tablero no se puede montar.
2. **Quien pide es quien administra la carpeta.** `guia.md` dice quién administra la carpeta compartida y con qué cuenta. La cuenta de la sesión tiene que ser esa, porque el artifact, su base y la tarea quedan en esa cuenta y es la única que puede lanzar la sincronización y ver su botón. Si es otra persona, se le dice a quién le toca y se para.
3. **No hay ya un tablero.** Si `guia.md` lleva la línea «El tablero de esta carpeta: …», lo que toca es actualizar o sincronizar, no montar otro.
4. **La cuenta tiene lo que hace falta**: la herramienta `Artifact` con las capacidades de base de datos, usuario y conector; `ArtifactData`; la herramienta de tareas programadas (`create_trigger`) con el conector «Claude Code Remote»; y el shell de la computadora (`device_bash`), porque el generador corre contra la carpeta sincronizada en ella. Se comprueba con `ToolSearch`; lo que no esté se nombra.
5. **La computadora está disponible** y la raíz se ve en `$HOME/mnt/` del shell. Si no, se pide con `device_request_folder_access` por su ruta.

## Montar

**1. Publicar la página.** `vista.html` de esta skill se publica como artifact nuevo con título «Tablero <organización>» (el nombre de la organización sale del título de `guia.md`), icono genérico, y esta declaración de capacidades, idéntica para todas las organizaciones:

```
db: reglas [{path: "", read: "view", write: "admin"}, {path: "cambios", read: "view", write: "interact"}]
user: {}
mcp: servers [{server: "Claude Code Remote", tools: ["fire_trigger"]}]
```

Con eso cualquiera con el enlace lee; un contribuidor puede fechar, marcar y anotar (escribe solo en la cola); la base la escriben la tarea y los editores; y el botón «Sincronizar ahora» lo ve el dueño.

**2. Crear la tarea diaria.** Con `create_trigger`: nombre «Regenerar tablero <organización>», de lunes a viernes a una hora de la mañana que no sea en punto (9:35 si no dicen otra), ligada a la computadora (`requires_local_device`) y con la carpeta de la raíz declarada en `folders`. El prompt es `tarea.md` de esta skill con sus tres huecos sustituidos: `{{ORGANIZACION}}`, `{{RUTA_RAIZ}}` (la ruta absoluta de la raíz en la computadora) y `{{URL}}` (la del artifact del paso 1). Se guarda el id que devuelve.

**3. Generar y cargar.** Se copian `generar_vista.py` y `aplicar_cambios.py` a `$HOME/tablero/` de la VM de la computadora con `device_bash` y un heredoc con delimitador entre comillas (la computadora no ve el contenedor), y se corre `python3 generar_vista.py "<raíz>" salida --tarea <id> --version <versión del plugin, de plugin.json>`. La salida va a `$HOME/tablero/salida/`, fuera de la raíz. Cada JSON de `salida/areas`, `salida/proyectos` y `salida/meta` se escribe en la base del artifact con `ArtifactData` en lotes de hasta 50: colección y doc_id iguales a carpeta y archivo.

**4. El primer «Por dónde empezar».** Es el paso 6 de `tarea.md` y se hace aquí mismo, porque una tarea nueva no ha corrido todavía y la página saldría sin esa sección: se leen los grupos candidatos de `salida/meta/enfoque-candidatos.json` y los pasos con sus señales, se eligen tres o cuatro grupos con los tres criterios (prioridad del área, cliente o dinero, desbloquea a otros; vencido no suma) y se escribe `enfoque/actual`.

**5. La línea en `guia.md`.** Al final de «Cómo conectarte», después del paso 5, un párrafo:

```markdown
**El tablero de esta carpeta:** <URL>. Muestra la carpeta entera sin abrirla y se pone
al día cada mañana. Quien tenga el enlace lo lee; para fechar o marcar pasos desde él
hace falta que lo compartan como contribuidor.
```

`guia.md` lo escribe solo el responsable de contexto. Si la sesión es la suya, se escribe; si no, se le pasa el párrafo y se dice que sin esa línea `sesion` no encuentra la cola.

**6. Comprobar.** Se abre el artifact (`Artifact` con `open`) y se mira que pinte la raíz con sus áreas y que `meta/estado` tenga la tarea y la versión.

### Qué respondo al terminar

Cinco líneas, sin recapitular los pasos:

- Qué quedó montado: el tablero, la tarea y su hora.
- **El modelo de la tarea.** Una tarea nace con el modelo de la sesión que la crea y desde Claude no se le puede cambiar; se fija en los ajustes de la tarea, en la app. El trabajo de la tarea es mecánico con un solo paso de juicio («Por dónde empezar»), así que basta el modelo intermedio de la familia vigente; el más potente es gasto sin ganancia. Cuando un modelo deje de existir, ahí mismo se cambia.
- **A quién compartir el tablero y cómo**: desde el menú de compartir del artifact; como contribuidor a quien vaya a actuar desde él, como lector al resto. El enlace no se comparte solo.
- **La computadora encendida.** La tarea corre contra la carpeta sincronizada en la computadora de quien la creó; si está apagada a esa hora, la tarea avisa y reintenta hasta la una de la tarde.
- Si `guia.md` no se pudo escribir, el párrafo del paso 5 y a quién le toca ponerlo.

## Actualizar

Cuando sale una versión nueva del plugin, la página del tablero y el generador cambian juntos. «Actualiza el tablero»:

1. Se lee la URL de la línea de `guia.md`.
2. Se vuelve a publicar `vista.html` de esta skill sobre esa URL (`Artifact` con `url`), con la misma declaración de capacidades del paso 1 de montar. La base no se toca: la cola, el enfoque y las correcciones son de la raíz y sobreviven.
3. Se compara el prompt de la tarea con `tarea.md` sustituido. Si cambió, se pide reescribirlo con `update_trigger`; en una tarea ligada a una computadora eso solo surte efecto cuando la persona lo aprueba en una conversación de la app ligada a esa misma computadora, y hasta entonces no cambia nada: se dice, no se rodea, y nunca se borra la tarea para crear otra, porque se pierde su historial y su computadora.
4. Se recuerda revisar el modelo de la tarea en sus ajustes: es el momento para subirlo o bajarlo, o para cambiarlo si el que tenía ya no existe.
5. Se sincroniza una vez (abajo) para que `meta/estado` lleve la versión nueva y la banda de desfase desaparezca.

## Sincronizar

Es la tarea diaria a mano, en esta sesión, con la raíz conectada: los pasos 1 a 7 de `tarea.md` tal cual, con los scripts copiados a la VM de la computadora como en el paso 3 de montar. Sirve cuando alguien acaba de trabajar en la carpeta y quiere verlo reflejado, cuando la cola tiene cosas que no esperan a mañana, o cuando «Sincronizar ahora» no está a mano porque quien mira no es el dueño del artifact. Lo que la tarea deja «pendiente de cerrar en sesión» se cierra con `sesion`, que lee la cola al abrir el proyecto.

## Lo que nunca hago

Además de las prohibiciones de `convenciones`:

- Montar un tablero desde una cuenta que no sea la de quien administra la carpeta.
- Escribir en la raíz cualquier cosa que no sea la línea de `guia.md`: ni scripts, ni la salida del generador, ni la cola, ni un archivo de configuración.
- Montar un segundo tablero sobre una raíz que ya tiene uno. Se actualiza.
- Cambiar desde aquí el modelo de una tarea, o borrar una tarea para recrearla con otro prompt.
- Escribir en `proyecto.md`, `sesiones.md` o `decisiones.md` desde la página. La página solo escribe en su cola.
- Cerrar un hecho que huela a decisión, o una nota, sin una sesión del proyecto.
- Dar por compartido el tablero: el enlace lo comparte una persona desde el menú del artifact.

## Ejemplo

**Usuario:** monta el tablero

**Respuesta:**

> Montado. Tablero «Tablero Acme» publicado con las 4 áreas y los 11 proyectos de la carpeta, «Por dónde empezar» con tres grupos, y la tarea «Regenerar tablero Acme» de lunes a viernes a las 9:35 ligada a esta computadora. Añadí el enlace a `guia.md`, en «Cómo conectarte».
>
> Tres cosas quedan en tu mano. El modelo de la tarea: nació con el de esta sesión; en sus ajustes elige el modelo intermedio vigente, que para este trabajo sobra. Compartir el tablero desde su menú: como contribuidor a quien vaya a fechar o marcar pasos, como lector al resto. Y tener la computadora encendida a las 9:35, o la tarea avisará y reintentará hasta la una.
