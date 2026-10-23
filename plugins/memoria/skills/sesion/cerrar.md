# Cerrar sesión y cerrar el proyecto

Anexo de la skill `sesion`. Se lee al cerrar («cierra la sesión», «guarda lo de hoy», «terminamos», «cierra el proyecto»), y antes se carga el anexo `escribir.md` de la skill `convenciones`, que hasta aquí no hacía falta: cerrar escribe en la carpeta y sus prohibiciones aplican a todo lo que sigue. Con él basta, salvo que el paso 1 o el 7 guarde o mueva un archivo, que pide además `convenciones` entera (nombres, entregable o taller, `fuentes/enlaces.md`, material sensible), o que haya un traspaso (paso 8), que pide `raices.md`. Las skills `director` y `estilo` no hacen falta para cerrar.

## Cerrar sesión

### Qué escribo y dónde

**Las reglas del área, antes que nada.** El bloque `Proyectos` del `area.md` del proyecto (que `abrir.py` imprimió al abrir) y las reglas propias de la casa de `guia.md` pueden pedir algo al cerrar, como poner al día la fila de un pipeline o la ficha de otro proyecto del área. Se cumple en este mismo cierre, como un paso más y dentro de lo que la cuenta puede escribir; si pide escribir en un área de otra cuenta, se prepara el texto y se dice a quién pasárselo.

**Cómo se escribe: todo en una llamada, con `cerrar.py`.** La sesión prepara los textos y `cerrar.py` (junto a este archivo; llegó a la computadora con `abrir.py` en la llamada 1 de abrir, y si no está, se trae igual que él) los escribe. Un `cambios.json` con la forma que dice su cabecera: la entrada de `sesiones.md` (paso 2, con el formato de `escribir.md`: `## AAAA-MM-DD` y la última línea «Sesión de»), las decisiones confirmadas (paso 3), `En corto` entero y los reemplazos exactos de `proyecto.md` (paso 4), la línea del proyecto y las de sus entregables en `area.md` (paso 5), el `Panorama` (paso 10) y, si una regla del área pide tocar otro archivo del área, sus reemplazos en «otros». Con consola: el JSON con un heredoc en `$HOME/memoria/` (fuera de la raíz) y, en la misma llamada de device_bash, `cd $HOME/memoria && python3 cerrar.py "<raíz en $HOME/mnt>" <area>/<proyecto> cambios.json --cuenta <correo de la cuenta> --abierto <la hora que imprime la línea «ahora» de REGISTROS de abrir.py, solo el valor>`. Sin consola: lo mismo con Bash en el contenedor sobre la copia (`python3 <directorio de esta skill>/cerrar.py "<la copia>" … --sin-fechas`, sin `--abierto`: las fechas de la copia son las de la traída y no dicen nada), con cada archivo traído y registrado antes como dice `sin-consola.md`, y después `espejo.py devolver`; si `device_commit_files` rechaza uno por `mtime-drift`, alguien lo cambió en la computadora: se trae otra vez, se registra, se repite `cerrar.py` sobre la copia (una entrada que ya está no se repite; los reemplazos van sobre lo nuevo) y se devuelve.

De cada archivo el script hace leer → cambiar → escribir bajo un cerrojo y, justo antes de escribir, comprueba que el archivo sigue como lo leyó; si cambió entre medias, vuelve a leer y aplica lo de esta sesión sobre lo nuevo. Así dos personas que cierran a la vez sobre el mismo proyecto, o dos sesiones de una misma cuenta, no se pierden una entrada ni un paso: cada entrada va encima de lo que haya y cada reemplazo se aplica sobre lo que está en el disco. Antes de escribir nada comprueba la forma de las entradas y que «otros» no salga del área (nunca `guia.md`, `base/` ni `restringido/`), y con `--cuenta` no escribe el `Panorama` si la cuenta no es la dueña del área ni la línea de `area.md` si tampoco colabora en ella. Lo que devuelve: `escritos`; `sin_match` (un reemplazo que no cuadra, porque su texto viejo no aparece exactamente una vez, cruza un encabezado o pasa de doce líneas: se relee ese archivo, se parte o ajusta el reemplazo y se repite la llamada solo con él, pasando en `--abierto` la `escrito_en` que devolvió la anterior); `rechazados` (lo que la cuenta no puede escribir o un archivo que encogería a menos de la mitad: se prepara el texto y se le pasa al dueño, o `--forzar <ruta>` solo si el recorte es a propósito); `fallidos` (un archivo que no se pudo leer o escribir, con el motivo: se dice y no se repite a ciegas); `ajenos` (archivos que alguien cambió desde la apertura o mientras este cierre escribía, con la hora en la zona de la organización: se dice en media línea al terminar, «alguien escribió proyecto.md a las 10:03; sumé lo de hoy encima»); `reintentos`; `hora` y `documento` (para la marca del tablero, paso 11); `escrito_en`. Lo que el cierre escribe pasa por el script: nunca con `Write`, `Edit`, `sed -i` ni un `cat >`, que pueden pisar lo que otra persona escribió. Vale también durante la sesión: si la persona pide quitar un paso o cambiar el estado antes de cerrar, se apunta y se escribe al cerrar; si quiere verlo escrito ya, se escribe con `cerrar.py` y solo `reemplazos` (sin entrada de bitácora), nunca a mano. Lo único que se escribe fuera de él, antes de llamarlo, es juntar una copia en conflicto (abajo) y la rotación (paso 9), que crean o funden archivos enteros como dice `escribir.md`. Esto cierra la ventana entre leer y escribir en esta computadora; lo que la otra persona escribió y Drive aún no bajó no se ve: si los dos llegan a escribir a la vez, Drive guarda las dos versiones, y la siguiente apertura las junta («Copias en conflicto»).

**Copias en conflicto.** Cuando abrir sesión avisa de una copia en conflicto («sesiones (1).md», «proyecto [Conflict].md» junto a su original), se junta antes de cualquier otra cosa, porque hasta entonces una de las dos versiones no la lee nadie. Se leen las dos. En `sesiones.md` y `decisiones.md`, que solo crecen, se juntan las entradas de las dos, sin repetir ni editar ninguna, en el orden del archivo. En un archivo vivo (`proyecto.md`, `area.md`, `guia.md`) se le enseña a la persona lo que difiere entre las dos y se escribe lo que ella decida. Se escribe en el original, siguiendo `escribir.md`, y la copia va a la papelera con su sí: con consola, se pide el permiso de borrar; sin consola, con el conector (`sin-consola.md`). Se dice en una línea. Un archivo en conflicto de un área donde la cuenta no escribe se le dice a su dueño, y no se toca.

**Si la cuenta colabora y no es la del dueño** (sección CUENTA EN EL PROYECTO de `abrir.py`), cierra igual: bitácora, decisiones de su trabajo con su nombre en `Decidió`, `En corto`, `Estado actual` y `Siguientes pasos`. No publica nada, ni toca `Prioridades ahora`, el `Panorama` ni la línea `Colabora:` de `Quién participa` (`convenciones`, sección 1, «Quién colabora»). Si colabora solo en este proyecto y no puede escribir `area.md`, la línea del paso 5 se prepara y se le pasa al dueño del área.

**0. La cola del tablero**, si se leyó al abrir. Lo que la sesión resolvió se borra de la cola con `ArtifactData` y la versión leída: un hecho ya quitado de «Siguientes pasos» y contado en `sesiones.md`, una nota ya registrada donde le tocaba, una corrección ya aplicada reescribiendo el paso o el estado actual, una fecha ya puesta en su línea, una prioridad ya quitada de «Prioridades ahora» de `area.md` porque el dueño del área lo pidió en esta sesión. Lo que no se resolvió se queda, y el tablero lo sigue mostrando como pendiente.

**1. Lo que se hizo y aún no está en la carpeta.** Lo producido se guarda al crearlo, así que esto no debería pasar; si algo de la sesión (un documento, un PDF, un análisis) solo existe en la conversación, se guarda ahora en `entregables/` o en `taller/` como borrador, antes de registrar nada. Lo mismo con lo que la app haya dejado en «Claude outputs» durante esta sesión: se mueve a este proyecto y deja de estar ahí.

**2. `sesiones.md`.** Entrada nueva arriba del todo, con el formato de `escribir.md` (sección 4), sin tocar las anteriores: tres líneas, más la de quién trabajó y con qué versión del plugin (la de `plugin.json`, la misma que la llamada 1 de abrir; quien trabaja sin el plugin escribe con qué lo hizo, por ejemplo «sin plugin, Gemini»). Si una sesión no cabe en tres líneas, es que hubo decisiones y esas van a su archivo.

**3. `decisiones.md`, solo si hubo decisiones.** Antes de escribir, se listan al usuario las decisiones detectadas, cada una como va a quedar escrita, y se pide confirmación explícita; la respuesta termina ahí y el cierre sigue en el turno siguiente, con el sí. También cuando la persona dictó la decisión en el mismo mensaje en que pide cerrar: dictarla no es confirmar la entrada. El registro no se puede corregir después, así que nada entra sin que alguien lo confirme. `Descartamos` y `Afecta a` van solo si hay algo que decir: nunca «no consta» ni «ninguno». Formato:

```markdown
## 2026-08-29 · Las órdenes bajo 5.000 MXN no pasan por aprobación
Decidió: Ana Pérez
Por qué: el 70% del volumen son órdenes pequeñas y consumían el 80% del tiempo de aprobación, según el export de órdenes de 2025.
Descartamos: tope acumulado mensual por proveedor, porque el ERP no expone el acumulado en tiempo real.
Afecta a: entregables/flujo-aprobacion.md (el paso de validación ya no aplica a todas) · finanzas/cierre-mensual (menos órdenes que conciliar)
```

**Responder un cuestionamiento.** Si al abrir se avisó de un cuestionamiento abierto a este proyecto y lo respondió en la sesión el dueño, o quien colabora si la decisión cuestionada es suya (lo dicen CUENTA EN EL PROYECTO y el `Decidió` de la decisión), la respuesta es una decisión más de esta lista, aunque solo mantenga lo que ya estaba: «lo mantengo» cambia algo, porque cierra una pregunta que alguien tenía abierta. La entrada lleva `Responde a: <identificador del cuestionamiento>` (el que se citó al abrir), dice en el título si mantiene o reemplaza lo cuestionado, y en `Por qué` la razón que dio el dueño. Se confirma como cualquier decisión y se dice a quién avisar: a quien lo planteó. Además, Claude se lo enseñará a esa persona la próxima vez que abra sesión en su proyecto.

**Plantear un cuestionamiento.** Si la persona quiere cuestionar una decisión de otro proyecto o una premisa, se escribe en el `decisiones.md` del proyecto activo, con el formato de `escribir.md`, sección 4 (`Planteó`, `Por qué`, `Cuestiona a`), después de enseñárselo y con su confirmación, como una decisión. Se le dice a quién avisar: al dueño de lo cuestionado.

Una decisión es un compromiso que cambia lo que se va a construir. Una preferencia expresada en voz alta no lo es. Ante la duda, se pregunta.

Si la decisión trae análisis detrás (opciones comparadas, tablas, cifras), el análisis va a un entregable del proyecto y la entrada lo cita. La entrada se queda con lo justo para entenderla sin abrir nada más.

Antes de confirmar, si el título o el `Por qué` nombran un `area/proyecto` de la raíz que no está en `Afecta a`, se propone añadirlo: sin esa línea, su dueño no recibe aviso. `Afecta a` admite también un área entera (`area/`), que avisa en cualquier proyecto del área.

Si `Afecta a` nombra un proyecto de otra área, se dice al usuario a quién tiene que avisar: el dueño de esa área, según `guia.md` o su `area.md`. La carpeta no notifica a nadie y la skill tampoco.

Si el proyecto activo lo lee todo el equipo y la decisión toca a un área o a un proyecto restringido, `Afecta a` lleva su nombre y nada más, porque ese nombre ya está listado: ni sus archivos, ni lo que contiene. Al revés, una decisión que se registra dentro de una carpeta restringida sí puede nombrar cualquier proyecto al que afecte.

**4. `proyecto.md`.** Se ponen al día `En corto`, `Estado actual` y `Siguientes pasos`. Es un archivo vivo: lo que deja de ser cierto se sustituye, no se acumula. `Estado actual` y `Siguientes pasos` se editan, no se vuelven a escribir enteros: se quitan los pasos hechos, se añaden los nuevos y se cambian solo las frases que la sesión dejó viejas, con reemplazos exactos (los `reemplazos` de `cambios.json`), sin volver a escribir lo que sigue valiendo. Si un texto viejo no aparece exactamente una vez (la tarea del tablero pudo poner una fecha en esa línea), `cerrar.py` lo devuelve en `sin_match`: se relee el archivo, se ajusta el reemplazo y se repite solo con él. Si `Estado actual` pasa de unas diez líneas, lo que ya es historia se quita, pero antes se comprueba que su hecho está en `sesiones.md` o en `decisiones.md`; si no está en ninguno, se lleva a la entrada de hoy antes de quitarlo. Nada sale de `Estado actual` sin quedar en un registro. `En corto` se reescribe entero, en la misma escritura, con la forma y la voz que da `escribir.md` (sección 3 y «La voz de `En corto` y del `Panorama`»); lo lee todo el equipo, en la carpeta y en el tablero de cada uno, así que nada de `restringido/` ni datos personales. Si el proyecto no lo tenía, se crea debajo del título.

**5. Bloque `Proyectos` de `area.md`.** Se reescribe la línea de este proyecto y, debajo, una línea por cada entregable `vigente` con su fecha `actualizado`. Solo esa parte del bloque; las líneas de los demás proyectos no se tocan. `Prioridades ahora` solo se reescribe si el dueño lo pide en esta sesión.

**6. Cabeceras de lo que se tocó.** `actualizado` lo pone `cerrar.py` en cada archivo que escribe; si se usó una fuente nueva, se añade a `basado_en` con un reemplazo exacto sobre la cabecera (en los `reemplazos` de `proyecto.md`, o en «otros»).

**7. Lo que entró en `fuentes/` o en `taller/`.** Si durante la sesión se guardó algo en `fuentes/` sin haber pasado por la pregunta de si es confidencial, se pregunta ahora: si trae datos personales, facturación, contratos, credenciales o cualquier cosa que no todos deban ver, se propone llevarlo a `restringido/` del mismo proyecto y dejar su fila en el `fuentes/enlaces.md` público. El usuario decide; nada se mueve sin que lo confirme.

**8. Traspasos.** Si en la sesión entró algo de otra raíz, la entrada de `sesiones.md` lo dice: qué vino, de qué raíz, quién lo pidió. Lo que se quedó fuera no se nombra.

**9. Rotación.** Si `sesiones.md` o `decisiones.md` supera las 1.500 líneas o cambia el año, se archiva como dice `escribir.md`, sección 8. Sin preguntar.

**10. El Panorama del área.** Se reescribe `Panorama` de `<area>/area.md` con la forma y la voz que da `escribir.md` (sección 2, «Estructura de `area.md`»): cómo está el área después de esta sesión. Al cerrar no se relee el área: se parte del Panorama anterior y de lo que esta sesión ya leyó y escribió, y de los demás proyectos del área solo se mira, en una sola llamada, la cabecera y el `En corto` de los que tienen `actualizado` posterior a la fecha del Panorama anterior, o de todos si no había Panorama con fecha. Va en la misma escritura de `area.md` que el paso 5. Solo si la cuenta que cierra es la del dueño del área; si solo colabora, o el área es de otra cuenta, se salta.

**10b. Los permisos, si cambiaron.** Si la cuenta es la del responsable de contexto y en esta sesión cambió quién escribe o qué se restringe (un área nueva, alguien añadido como dueño o colaborador, algo declarado restringido, una carpeta `restringido/` nueva), al final del cierre se propone en una línea revisar que Drive coincide, y con su sí se sigue `permisos.md`.

**11. El tablero, avisado.** Si la cuenta tiene tablero (el que se buscó al abrir), se apunta el cierre en su base, sin preguntar ni decir nada: con `ArtifactData` (se carga con `ToolSearch`), un `set` en la colección `cierres` con el documento que devolvió `cerrar.py` en `documento` (`<area>--<proyecto>--<AAAAMMDDHHMM>`, nuevo en cada cierre, así que no lleva `if_version`) y los campos `proyecto` (`<area>--<proyecto>`), `nombre` (el título de `proyecto.md`), `hora` (la `hora` que devolvió `cerrar.py`, tomada del reloj y nunca calculada a mano, como `2026-10-19T03:20Z`; una hora adelantada deja el aviso del tablero encendido hasta que llega) y `cuenta`. Uno por cada tablero de la cuenta de esa raíz (desde la 1.18 hay uno; quien tenía dos de antes, en los dos, hasta que borre uno). Al abrir el tablero, su dueño ve arriba que hubo sesiones que aún no muestra, con el botón que lo pone al día; la sincronización borra las marcas que recoge. No se lanza la tarea desde la conversación, porque la app pide permiso cada vez que una conversación lanza una tarea. Solo si la persona lo pide al cerrar («cierra y pon al día el tablero») se lanza con `fire_trigger`: con `list_triggers` (`enabled: true`, siguiendo `next_cursor`) se busca la tarea cuyo prompt lleva la URL del tablero (se llama «Regenerar tablero <organización>», o con « completo» si se montó antes de la 1.18), y se dispara si su aprobación es automática (`permission_mode` `auto`) y su carpeta (`derived_state.folders`) es la raíz conectada; la app pedirá permiso y la persona lo da. Si el tablero no tiene tarea o la cuenta no tiene el conector de tareas programadas, el botón no puede ponerse al día: entonces se pone al día aquí mismo, como «Sincronizar» de la skill `tablero`. Si la escritura falla, se dice en media línea y la sesión queda cerrada igual: el tablero se pondrá al día con su botón o con «sincroniza el tablero».

### Qué respondo al terminar

Dos o tres líneas: qué archivos se escribieron y qué queda para la próxima. Si hay que avisar a otra área, se dice a quién. Si quedó algo en `fuentes/` pendiente de decidir si es confidencial, se dice. Del tablero no se dice nada si se apuntó el cierre; media línea solo si se lanzó porque la persona lo pidió, si se puso al día aquí o si algo falló. Nada más. El resumen largo ya está en los archivos.

---

## Cerrar el proyecto

Cuando el dueño dice que el proyecto terminó («cierra el proyecto», «esto ya está»). Antes se comprueba que la cuenta es la del dueño (CUENTA EN EL PROYECTO de `abrir.py`): si solo colabora, se dice que lo pida el dueño y no se cierra. Después se comprueba con él que se cumple lo que dice `Terminado significa`; si no, se dice qué falta y se espera.

1. `Estado actual` de `proyecto.md` abre con «Proyecto terminado el AAAA-MM-DD» y una línea de cómo acabó, y `En corto` queda solo con su frase en negrita, que lo dice en lenguaje llano; `Siguientes pasos` dice que no queda ninguno propio, y lo que siga vivo se nombra con el proyecto que lo recoge.
2. La línea del proyecto en el bloque `Proyectos` de `area.md` se queda sola, sin desglosar sus entregables (`escribir.md`, «Un proyecto cerrado»).
3. Una entrada en `sesiones.md` que lo cuenta, y en `decisiones.md` solo si cerrarlo fue una decisión que alguien tomó.

Nada se borra ni se mueve: los entregables siguen con su estado y se siguen citando.

## Lo que nunca hago al cerrar

Además de las prohibiciones de `convenciones` (anexo `escribir.md`):

- Dar por cerrado un pendiente sin preguntar. Si no sé si algo quedó resuelto, lo pregunto
- Borrar de la cola del tablero un cambio que la carpeta todavía no refleja
- Registrar una decisión sin enseñarla antes y sin un sí

## Ejemplo de cierre

**Usuario:** [después de trabajar en el criterio de corte por monto de compras/automatizacion-ordenes] cierra la sesión

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
