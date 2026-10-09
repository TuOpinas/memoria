---
name: tablero
description: Monta, actualiza y sincroniza el tablero de una persona sobre la carpeta de su organizacion, una pagina que muestra la carpeta entera (areas, proyectos, estado, decisiones, siguientes pasos) generada desde los archivos y puesta al dia por una tarea diaria. Usala cuando digan 'monta el tablero', 'monta mi tablero', 'quiero ver la carpeta sin abrirla', 'actualiza el tablero', 'sincroniza el tablero', 'regenera la vista' o pregunten por que el tablero no muestra algo.
---

# Tablero

Una página que muestra la carpeta de la organización sin abrirla: qué áreas hay y de quién son, en qué va cada proyecto, qué se decidió, qué entregables hay y qué pasos siguen. Se genera desde los archivos y se pone al día sola. Antes de nada se carga `convenciones`: sus prohibiciones aplican a todo lo que sigue.

Cuatro reglas que no cambian:

- **El tablero es de una persona.** Lo monta cada quien desde su propia cuenta, sobre la raíz conectada, y corre con sus permisos: lo que esa cuenta no puede leer en la carpeta sale como «restringido», y lo que su tarea escribe en la carpeta lo escribe con sus permisos. El de quien administra la carpeta es uno más. Su dueño puede compartirlo desde el menú del artifact, y esa es la única manera de que otra persona lo vea.
- **La carpeta es la fuente.** El tablero lee la superficie pública de la raíz (`guia.md`, los `area.md` y, de cada proyecto, `proyecto.md`, `decisiones.md`, `sesiones.md` y las cabeceras de `entregables/`) y nada más. Nunca abre `fuentes/`, `taller/`, `restringido/` ni `base/`.
- **El tablero no escribe en la carpeta.** Lo que alguien toca en él (fechar un paso, marcarlo hecho, anotar algo, corregir un estado) espera en una cola propia de la página, y lo escribe quien tiene contexto: la tarea diaria lo mecánico, la siguiente sesión del proyecto lo que pide juicio.
- **Vive fuera de la raíz.** La página, su base de datos, los scripts y la tarea son de la cuenta de su dueño. En la carpeta de la organización no entra nada: ni un enlace. El tablero se encuentra por su nombre, que es fijo, entre los artifacts de la cuenta; es así como `sesion` lo localiza para leer su cola, sin que nadie apunte la URL en ningún sitio.

## Dos modos

| | Público | Completo |
|---|---|---|
| Qué muestra | La superficie pública del contrato: `area.md`, `proyecto.md`, decisiones, entregables. De un área cuya columna «Quién la lee» diga «Restringida», y de un proyecto cuya línea del índice diga «restringido», solo nombre y dueño, aunque tu cuenta pueda leerlos. De cada sesión, solo fecha y título | Todo lo que tu cuenta lee, incluidas las áreas y proyectos restringidos a los que tienes acceso, con la bitácora entera |
| Para quién | Para compartirlo con cualquiera de la organización | Para ti. Lleva una marca fija que dice que no se comparte |
| Frase | «monta el tablero» (es el modo por defecto) | «monta el tablero completo», «monta el tablero con todo» |

Una persona puede tener los dos sobre la misma raíz. Antes de montar uno, la skill mira si ya existe un tablero con ese nombre y ese modo en la cuenta (`Artifact` con `list`) o una tarea con ese nombre (`list_triggers`); si existe, lo dice y propone actualizarlo o sincronizarlo en vez de montar otro. Un duplicado no rompe nada, pero son dos tareas y dos colas para lo mismo.

Lo que trae esta skill, en su carpeta: `vista.html` (la página), `generar_vista.py` (lee la raíz y produce los documentos de la base), `aplicar_cambios.py` (escribe en la carpeta lo mecánico de la cola) y `tarea.md` (el prompt de la tarea diaria, con cuatro huecos). Nada de esto se copia a la raíz.

## Cuándo

**Montar**: "monta el tablero", "monta mi tablero", "monta el tablero completo", "quiero ver la carpeta entera sin abrirla".

**Actualizar**: "actualiza el tablero", o cuando el tablero muestra que su página y el plugin corren versiones distintas.

**Sincronizar**: "sincroniza el tablero", "regenera la vista", "lo que marqué no aparece en la carpeta". Es la tarea diaria a mano.

Si hay más de una raíz conectada, se pregunta cuál. Una sesión monta un solo tablero.

## Antes de montar

Cuatro comprobaciones, y en la primera que falle se dice qué falta y se para:

1. **La raíz conectada es completa**: tiene `guia.md` y `metodo.md` en su primer nivel. Si solo está conectada la carpeta de un área, el tablero no se puede montar.
2. **No hay ya uno igual** en esta cuenta: mismo nombre («Tablero <organización>» o «Tablero <organización> completo») o misma tarea. Si lo hay, se ofrece actualizar o sincronizar.
3. **La cuenta tiene lo que hace falta**: la herramienta `Artifact` con las capacidades de base de datos, usuario y conector; `ArtifactData`; la herramienta de tareas programadas (`create_trigger`) con el conector «Claude Code Remote»; y el shell de la computadora (`device_bash`), porque el generador corre contra la carpeta sincronizada en ella. Se comprueba con `ToolSearch`; lo que no esté se nombra.
4. **La computadora está disponible** y la raíz se ve en `$HOME/mnt/` del shell. Si no, se pide con `device_request_folder_access` por su ruta.

Si el modo es público y la cuenta de la sesión lee áreas o proyectos restringidos, se avisa de una cosa antes de seguir: lo restringido queda fuera solo si está declarado (la columna «Quién la lee» en `guia.md`, la palabra «restringido» en la línea del proyecto en `area.md`); un proyecto restringido en Drive que nadie declaró entraría en el tablero público. Si hay duda, se monta el completo y no se comparte.

## Montar

**1. Publicar la página.** Se copia `vista.html` de esta skill al scratchpad con el nombre `tablero.html`, se sustituye su primera línea `<title>Tablero</title>` por `<title>Tablero <organización></title>` (y « completo» al final si es ese modo; el nombre de la organización sale del título de `guia.md`), y se publica como artifact nuevo con el icono `dashboard`, y esta declaración de capacidades, idéntica para todos los tableros:

```
db: reglas [{path: "", read: "view", write: "admin"}, {path: "cambios", read: "view", write: "interact"}]
user: {}
mcp: servers [{server: "Claude Code Remote", tools: ["fire_trigger"]}]
```

Con eso el dueño lo ve y lanza la sincronización; si lo comparte, un lector lee y un contribuidor puede además fechar, marcar y anotar (escribe solo en la cola); la base la escriben la tarea y los editores.

**2. Crear la tarea diaria.** Con `create_trigger`: nombre «Regenerar tablero <organización>» (con « completo» si lo es), de lunes a viernes a una hora de la mañana que no sea en punto (9:35 si no dicen otra), ligada a la computadora (`requires_local_device`) y con la carpeta de la raíz declarada en `folders`. El prompt es `tarea.md` de esta skill con sus cuatro huecos sustituidos: `{{ORGANIZACION}}`, `{{RUTA_RAIZ}}` (la ruta absoluta de la raíz en la computadora), `{{URL}}` (la del artifact del paso 1) y `{{MODO}}` (`publico` o `completo`). Se guarda el id que devuelve.

**3. Generar y cargar.** Se copian `generar_vista.py` y `aplicar_cambios.py` a `$HOME/tablero/` de la VM de la computadora con `device_bash` y un heredoc con delimitador entre comillas (la computadora no ve el contenedor), y se corre `python3 generar_vista.py "<raíz en $HOME/mnt>" salida --modo <modo> --ruta "<ruta de la raíz en la computadora>" --tarea <id> --version <versión del plugin, de plugin.json>`. La salida va a `$HOME/tablero/salida/`, fuera de la raíz. Cada JSON de `salida/areas`, `salida/proyectos` y `salida/meta` se escribe en la base del artifact con `ArtifactData` en lotes de hasta 50: colección y doc_id iguales a carpeta y archivo.

**4. El primer «Por dónde empezar».** Es el paso 6 de `tarea.md` y se hace aquí mismo, porque una tarea nueva no ha corrido todavía y la página saldría sin esa sección: se leen los grupos candidatos de `salida/meta/enfoque-candidatos.json` y los pasos con sus señales, se eligen tres o cuatro grupos con los tres criterios (prioridad del área, cliente o dinero, desbloquea a otros; vencido no suma) y se escribe `enfoque/actual`.

**5. Comprobar.** Se abre el artifact (`Artifact` con `open`) y se mira que pinte la raíz con sus áreas y que `meta/estado` tenga la tarea, el modo y la versión.

### Qué respondo al terminar

Cuatro líneas, sin recapitular los pasos:

- Qué quedó montado: el tablero, su modo, la tarea y su hora.
- **El modelo de la tarea.** Una tarea nace con el modelo de la sesión que la crea y desde Claude no se le puede cambiar; se fija en los ajustes de la tarea, en la app. El trabajo es mecánico con un solo paso de juicio («Por dónde empezar»), así que basta el modelo intermedio de la familia vigente. Cuando un modelo deje de existir, ahí mismo se cambia.
- **Compartir**, solo si es público: desde el menú del artifact, como contribuidor a quien vaya a actuar desde él, como lector al resto. Si es completo, que no se comparte.
- **La computadora encendida.** La tarea corre contra la carpeta sincronizada en la computadora de quien la creó; si está apagada a esa hora, la tarea avisa y reintenta hasta la una de la tarde.

## Actualizar

Cuando sale una versión nueva del plugin, la página del tablero y el generador cambian juntos, y **la cadena es automática**: la tarea diaria corre con el plugin nuevo, ve que la página es de otra versión, la republica sobre la misma URL y deja en Inicio el aviso «El tablero se actualizó a la versión X» durante una semana. Quien tenga el marketplace con actualización automática no hace nada; quien actualice el plugin a mano, lo hace y el resto viene en cadena. Lo único que la tarea no puede hacer sola es reescribir su propio prompt: si `tarea.md` cambió, lo marca en Inicio y pide «actualiza el tablero».

«Actualiza el tablero», a mano o cuando la tarea lo pide:

1. Se busca el artifact por su nombre con `Artifact` `list`.
2. Se vuelve a publicar `vista.html` de esta skill sobre esa URL (`Artifact` con `url`), con el `<title>` sustituido como en el paso 1 de montar y la misma declaración de capacidades. La base no se toca: la cola, el enfoque y las correcciones sobreviven.
3. Se compara el prompt de la tarea con `tarea.md` sustituido. Si cambió, se pide reescribirlo con `update_trigger`; en una tarea ligada a una computadora eso solo surte efecto cuando la persona lo aprueba en una conversación de la app ligada a esa misma computadora, y hasta entonces no cambia nada: se dice, no se rodea, y nunca se borra la tarea para crear otra, porque se pierde su historial y su computadora.
4. Se recuerda revisar el modelo de la tarea en sus ajustes: es el momento para cambiarlo si el que tenía ya no existe.
5. Se sincroniza una vez (abajo) para que `meta/estado` lleve la versión nueva y la banda de desfase desaparezca.

## Sincronizar

Es la tarea diaria a mano, en esta sesión, con la raíz conectada: los pasos 1 a 7 de `tarea.md` tal cual, con los scripts copiados a la VM de la computadora como en el paso 3 de montar y el modo del tablero. Sirve cuando alguien acaba de trabajar en la carpeta y quiere verlo reflejado, o cuando la cola tiene cosas que no esperan a mañana. Lo que la tarea deja «pendiente de cerrar en sesión» se cierra con `sesion`, que lee la cola al abrir el proyecto.

## Lo que nunca hago

Además de las prohibiciones de `convenciones`:

- Escribir en la raíz cualquier cosa: ni el enlace, ni scripts, ni la salida del generador, ni la cola, ni un archivo de configuración.
- Montar un tablero completo sin decir que no se comparte, o montar uno público sin avisar de lo restringido no declarado cuando la cuenta lo lee.
- Montar un segundo tablero igual sin avisar de que ya existe.
- Cambiar desde aquí el modelo de una tarea, o borrar una tarea para recrearla con otro prompt.
- Escribir en `proyecto.md`, `sesiones.md` o `decisiones.md` desde la página. La página solo escribe en su cola.
- Cerrar un hecho que huela a decisión, o una nota, sin una sesión del proyecto.
- Compartir el tablero: lo comparte su dueño desde el menú del artifact.

## Ejemplo

**Usuario:** monta el tablero

**Respuesta:**

> Montado. «Tablero Acme», público, con las 4 áreas y los 11 proyectos de la carpeta (`legal/` solo con nombre y dueño, como dice `guia.md`), «Por dónde empezar» con tres grupos, y la tarea «Regenerar tablero Acme» de lunes a viernes a las 9:35 ligada a esta computadora.
>
> Dos cosas quedan en tu mano. El modelo de la tarea: nació con el de esta sesión; en sus ajustes elige el intermedio vigente, que para este trabajo sobra. Y compartirlo, si quieres, desde su menú: como contribuidor a quien vaya a fechar o marcar pasos, como lector al resto. La computadora tiene que estar encendida a las 9:35, o la tarea avisará y reintentará hasta la una.
