# Mantenimiento de la carpeta

Anexo de la skill `sesion` (1.26.6). Siete temas que quien administra la carpeta mira cada semana mientras el equipo arranca, y cada mes cuando ya trabaja solo: seis de uso (cómo se está usando la memoria) y el séptimo, la estructura (si sigue el método). Mirar solo lee: dos scripts y la explicación en llano. Arreglar es aparte, con la lista delante y el sí. También programa la revisión como una tarea que corre sola.

## Cuándo

- «haz el mantenimiento de la carpeta», «¿quién está usando la memoria?», «revisa el arranque del equipo».
- «haz el mantenimiento de lo mío»: lo mismo, recortado a lo de la cuenta (abajo).
- «verifica la carpeta», «pasa verificar.sh»: solo el tema 7.
- «programa el mantenimiento», «pasa el mantenimiento a mensual» (o a semanal): «Programarlo».
- Desde su tarea programada, que carga esta skill con `mantenimiento-prompt.md`.

**Quién y qué mira.** Lo decide `mantenimiento.py` con `--cuenta`, sin que la conversación lo juzgue. La cuenta del responsable de contexto, que administra la carpeta y lo lee todo (`convenciones`, «Permisos en la carpeta compartida»), mira la raíz entera, también las áreas y los proyectos restringidos: la respuesta es solo para ella, como su tablero. Cualquier otra cuenta hace «el mantenimiento de lo mío»: las áreas y proyectos donde es responsable o colabora, que es donde escribe (`escribir.md`, prohibición 5), y de lo restringido solo lo que ella lleva; lo demás ni se nombra. Necesita la consola de la computadora: sin consola (`sin-consola-sesion.md`) se dice en una línea que se hace desde una computadora con la carpeta montada.

## Los siete temas

| Tema | Qué se mira | Si aparece, quién y qué |
|---|---|---|
| 1. Adopción | Quién cerró sesión en la ventana y quién no; las firmas que no son de nadie del registro | Quien administra: diez minutos con quien no abrió (casi siempre le falta un primer proyecto propio, con final y fecha); una firma desconocida, un «también:» en su línea |
| 2. Estatus al día | Proyectos con el Estatus más viejo que su última sesión; áreas, contra las sesiones de su responsable | El responsable de cada uno, al cerrar su siguiente sesión |
| 3. Decisiones en espera | Pasos que nombran a alguien que no lleva el proyecto, primero los tuyos; cuestionamientos sin respuesta, con quién responde | Lo tuyo, tú; lo de otros, la persona nombrada o quien lleva el proyecto; un cuestionamiento, el responsable de lo cuestionado (de una premisa, el de contexto) |
| 4. Sincronización | Copias en conflicto de Drive («nota (1).md» junto a «nota.md») | Quien abra sesión en ese proyecto: Claude junta las dos versiones (`cerrar.md`, «Copias en conflicto»). No se borra nada |
| 5. Trabajo fuera de la memoria | Lo cambiado después del último cierre de su proyecto, y proyectos con archivos y ninguna sesión | El responsable del proyecto, en su siguiente sesión: se pregunta quién lo hizo y se registra |
| 6. Versión y permisos | El plugin de cada uno en su última sesión | La persona actualiza el plugin. Los permisos de Drive no se miran aquí: la fila dice «no revisados» y se ofrece «revisa los permisos» (`permisos.md`) |
| 7. Estructura | `verificar.sh` | «Arreglar», abajo |

Los pasos no llevan fecha: de lo que espera se dice dónde está, no desde cuándo. Un cuestionamiento sí: «abierto desde».

## Cómo

1. **Los scripts.** Con Bash, en el contenedor: `python3 "<PLUGIN>/preparar.py" '$HOME/memoria' skills/sesion/mantenimiento.py verificar.sh` (para el tema 7 solo, `verificar.sh` y nada más). Con device_bash, en la computadora, un solo comando: lo que va detrás de «DESCARGA » y ` && cd "$HOME/memoria" && python3 mantenimiento.py "<RAIZ>" --cuenta <correo> --dias <7 o 31> --plugin <VERSION> > mant.txt; echo "mantenimiento: $?"; bash verificar.sh "<RAIZ>" > ver.txt; echo "verificar: $?"; cat mant.txt; head -60 ver.txt; echo "verificar: $(grep -c '^- ' ver.txt) hallazgos"`. Si la descarga no pasa la comprobación, una vez con REINTENTO; si vuelve a fallar, no se sigue y se dice. RAIZ es `$HOME/mnt/<nombre de la carpeta>` (la línea RAIZ de `abrir.py` si la conversación la tiene). La salida va acotada: cada tema dice cuántos más hay, y `--tema <NOMBRE>` da uno entero cuando la persona lo pide.
   - `mantenimiento.py` sale con 0 si miró, 1 si a la raíz le falta `guia.md` (es lo primero que se arregla) y 2 si la ruta no es una raíz o un argumento está mal: con 2 se corrige la ruta o el comando, sin decírselo a la persona.
   - `verificar.sh`: 0 cumple, 1 hay hallazgos, 2 no es una raíz.
   - Su sección CUENTA dice qué mira la cuenta, y ESCRITURA si se puede arreglar algo.
2. **Qué se enseña.** Un recuadro «Memoria · mantenimiento · <fecha>» con una fila por tema y, en cada una, en llano, «bien», qué pasa («Mayra y Saúl no han cerrado ninguna sesión») o «no revisado aquí» y por qué; nunca «bien» de lo que no se miró. Debajo, solo los temas con algo, cada uno con lo que hay que hacer y quién, con nombres de personas y fechas y sin nombres de secciones, scripts ni hallazgos. Lo que NO_REVISADO dice, en una línea. Si todo está bien, el recuadro y una línea.
3. **Para los demás**, una frase por persona y tema, lista para mandar: el 1, «abre una sesión en un proyecto tuyo y ciérrala»; el 2 y el 5, «abre sesión en <proyecto> y ciérrala al terminar»; el 4, «abre sesión en <proyecto>»; el 3, «decide <lo que espera>»; para todo junto, «pide a Claude «haz el mantenimiento de lo mío»». A quien no administra no se le nombra un proyecto restringido que no lleva.
4. **Al final**, si ESCRITURA lo permite y hay algo que la cuenta arregla, la lista exacta de lo mecánico (ruta y qué se crea o escribe) y una pregunta: «¿Arreglo esto?».

## Arreglar, con el sí

Solo con la respuesta de la persona en la conversación; nunca solo. Antes: si pasó más de una hora desde que se miró, se repite solo `verificar.sh` (la descarga y `bash verificar.sh "<RAIZ>"`), no los temas de uso. Se carga `escribir.md` (y `convenciones` entera para crear o mover). Se arregla solo lo que la cuenta escribe según CUENTA y ESCRITURA: nada si ESCRITURA dice «solo lectura» o que no se arregla. Un proyecto terminado no se toca.

**Mecánico, con el sí a la lista del paso 4** (vale solo para esa lista):

| Hallazgo de la estructura | Cómo |
|---|---|
| proyecto incompleto: falta una carpeta | `mkdir` de la carpeta vacía |
| entregable vigente que no está en el bloque Proyectos; proyecto que ya tiene su línea y le falta un entregable | `cerrar.py --cuenta <correo>` sin `sesion`, con `area.linea` (la que el proyecto ya tiene, tal cual) y `area.entregables` con todos sus vigentes como `{"archivo": …}`. `cerrar.py` se descarga entonces (`preparar.py … skills/sesion/cerrar.py`) |

**Uno a uno, con su pregunta**:

| Hallazgo | Cómo |
|---|---|
| proyecto que no está en el bloque Proyectos | se pregunta antes si es restringido: si sí, «restringido: responsable Nombre.»; si no, una línea desde su `Objetivo`, que se enseña |
| nombre que no está en «Quién es quién», persona de baja | si es la misma persona con otro nombre, «también: …» en su línea; si es otra, su línea con su cuenta, que se pregunta; en `guia.md`, con un reemplazo exacto. Del responsable de contexto |
| área del mapa sin carpeta | crearla (skill `nuevo`) o quitar su fila; de una restringida, nada. Del responsable de contexto |
| filas, columnas o secciones de `guia.md` mal escritas, zona horaria, «falta en la raíz», falta `guia.md` | lo que dice el hallazgo, con un reemplazo exacto o el archivo con su plantilla (skill `nuevo`). Del responsable de contexto |
| copia en conflicto de Drive | es el tema 4: se junta en la sesión de ese proyecto |
| nombre de carpeta o de archivo | antes, se busca qué lo cita; si lo cita un registro o algo de otra área, no se renombra y se dice; si no, `mv -n` y se ponen al día las citas propias |
| sin cabecera, cabecera sin estado o sin actualizado | `borrador` y `basado_en: []`, con su `actualizado` y la `aportacion` que se pregunta; en `proyecto.md`, `area.md` o un registro no se toca y se dice |
| un nivel de agrupación de más, carpeta prohibida, archivos sueltos, «Claude outputs» | subir o mover lo que sirve (skill `donde-va`); borrar, solo con el permiso de borrar y su sí: en la consola, borrar es para siempre |
| dentro de un registro (enlace wiki, ruta absoluta en `sesiones.md` o `decisiones.md`) | un registro no se edita: se dice y se deja |
| lo demás | lo que dice el hallazgo, en llano, y se pregunta |

Tres hallazgos de una misma carpeta de área con mayúsculas o acento («área del mapa sin carpeta», «carpeta de área que no está en guia.md» y «nombre de carpeta») son uno: se renombra la carpeta, no se crea otra. Al terminar, `verificar.sh` otra vez y se dice lo que quedó. Mover o poner cabecera a un archivo de `taller/` o `entregables/` cambia su fecha: la siguiente apertura de ese proyecto lo avisará como trabajo sin sesión, y se dice.

## Programarlo

«Programa el mantenimiento», en la conversación de quien administra la carpeta, en la app de la computadora que la tiene montada (se comprueba antes con un device_bash; sin consola, no se programa y se dice). Hace falta el conector «Claude Code Remote» (`ToolSearch` de `create_trigger`, `list_triggers` y `update_trigger`).

- **La cadencia la elige la persona.** Se sugiere semanal mientras el equipo arranca y mensual cuando ya trabaja solo; se pregunta, con esa sugerencia.
- **Una sola tarea por organización.** Con `list_triggers` se busca «Mantenimiento de la memoria <organización>». Si existe, no se crea otra.
- **Crearla.** `create_trigger`: ese nombre, `CRON_TZ=<zona de guia.md> 40 12 * * 5` (los viernes a las 12:40; la mensual corre el primero del mes, lo decide su prompt), ligada a la computadora (`requires_local_device`), con la ruta absoluta de la raíz en esta computadora en `folders` (la de `get_device_info`). Sin zona válida en `guia.md`, se pregunta. El prompt es `mantenimiento-prompt.md`, junto a este archivo, con `{{ORGANIZACION}}`, `{{CARPETA}}` (el nombre de la carpeta bajo `$HOME/mnt/`), `{{CUENTA}}` (el correo de esta cuenta), `{{ZONA}}`, `{{DIAS}}` (7 o 31) y `{{CADENCIA}}` (`semanal` o `mensual`) sustituidos, todos a la vez. Crearla pide una aprobación en la app.
- **Cambiar la cadencia** es cambiar el prompt: `update_trigger` con el prompt nuevo entero (`{{DIAS}}` y `{{CADENCIA}}` juntos). En una tarea ligada a una computadora solo surte efecto cuando la persona lo aprueba en la app de esa computadora; hasta entonces se dice, no se rodea. Lo mismo si `mantenimiento-prompt.md` cambió con una versión del plugin.
- **Otra computadora.** La tarea no se puede pasar a otra computadora. Desde la nueva, con la raíz conectada, se crea la tarea como arriba y se apaga la vieja con `update_trigger` y `enabled: false`; no se borra, para no perder su historial.
- Se dice en tres líneas: cuándo corre; que la computadora tiene que estar encendida con la app abierta a esa hora, y si no lo está, avisa y reintenta hasta las 18:00 de ese día; y qué aprobación quedó (el `permission_mode` del resultado): si no es automática, que la ponga en «Automatically approve» en los ajustes de la tarea, porque corre scripts en la computadora sin nadie delante. Esa aprobación es para mirar: arreglar pide siempre la respuesta de la persona.

**Cuando corre la tarea** (lo sigue su prompt): los pasos 1 a 4 de «Cómo», con la cuenta y la carpeta del prompt, sin abrir sesión ni escribir nada; la lista y «¿Arreglo esto?» se quedan esperando a que la persona abra esa conversación y conteste. Si la computadora no responde, como la tarea del tablero: un aviso, «El mantenimiento de <organización> está esperando tu computadora: abre la app de Claude y lo corro en 15 minutos», un `send_later` a esta misma sesión dentro de 15 minutos, y así hasta las 18:00 (hora de la tarea), avisando solo la primera vez; si a esa hora sigue sin estar, un último aviso: «Hoy no corrió el mantenimiento de <organización>; pídelo cuando quieras: «haz el mantenimiento de la carpeta»». Al final, un aviso: con algo, «La memoria de <organización> tiene <n> cosas por atender: abre esta conversación»; con todo bien, «La memoria de <organización> está al día»; si no pudo correr por otra cosa (la descarga, la ruta, la cuenta), «El mantenimiento de <organización> no corrió: <motivo>». Los avisos van con PushNotification (si no existe, SendUserMessage).
