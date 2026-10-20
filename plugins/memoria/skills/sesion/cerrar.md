# Cerrar sesión y cerrar el proyecto

Anexo de la skill `sesion`. Se lee al cerrar («cierra la sesión», «guarda lo de hoy», «terminamos», «cierra el proyecto»), y antes se carga entera la skill `convenciones`, que hasta aquí no hacía falta: cerrar escribe en la carpeta y sus prohibiciones aplican a todo lo que sigue.

## Cerrar sesión

### Qué escribo y dónde

**Las reglas del área, antes que nada.** El bloque `Proyectos` del `area.md` del proyecto (que `abrir.py` imprimió al abrir) y las reglas propias de la casa de `guia.md` pueden pedir algo al cerrar, como poner al día la fila de un pipeline o la ficha de otro proyecto del área. Se cumple en este mismo cierre, como un paso más y dentro de lo que la cuenta puede escribir; si pide escribir en un área de otra cuenta, se prepara el texto y se dice a quién pasárselo.

**Antes de escribir: ¿escribió alguien más?** `abrir.py` imprimió en REGISTROS la hora de la última escritura de `proyecto.md`, `decisiones.md` y `sesiones.md`. Antes del primer cambio se mira otra vez (`stat` en la computadora). Si alguna cambió y no fue esta sesión, otra persona escribió en el proyecto mientras tanto: se releen esos archivos, lo de esta sesión se suma a lo que hay (la entrada nueva va encima de la suya, los pasos se editan sobre su versión) y se dice en media línea al terminar. Nunca se escribe encima de lo que no se ha leído.

**Si la cuenta colabora y no es la del dueño** (sección CUENTA EN EL PROYECTO de `abrir.py`), cierra igual: bitácora, decisiones de su trabajo con su nombre en `Decidió`, `En corto`, `Estado actual` y `Siguientes pasos`. No publica nada, ni toca `Prioridades ahora` ni el `Panorama` (`convenciones`, sección 1, «Quién colabora»). Si colabora solo en este proyecto y no puede escribir `area.md`, la línea del paso 5 se prepara y se le pasa al dueño del área.

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

**10. El Panorama del área.** Se reescribe `Panorama` de `<area>/area.md` con la forma que da la skill `director` en «Escribir el Panorama», en tres a cinco frases con la fecha de hoy: cómo está el área después de esta sesión. Al cerrar no se relee el área: se parte del Panorama anterior y de lo que esta sesión ya leyó y escribió, y de los demás proyectos del área solo se mira, en una sola llamada, la cabecera y el `En corto` de los que tienen `actualizado` posterior a la fecha del Panorama anterior, o de todos si no había Panorama con fecha. Va en la misma escritura de `area.md` que el paso 5. Solo si la cuenta que cierra es la del dueño del área; si solo colabora, o el área es de otra cuenta, se salta.

**11. El tablero, avisado.** Si la cuenta tiene tablero (el que se buscó al abrir), se apunta el cierre en su base, sin preguntar ni decir nada: con `ArtifactData` (se carga con `ToolSearch`), un `set` en la colección `cierres` con el documento `<area>--<proyecto>--<AAAAMMDDHHMM>` (nuevo en cada cierre, así que no lleva `if_version`) y los campos `proyecto` (`<area>--<proyecto>`), `nombre` (el título de `proyecto.md`), `hora` (ahora, ISO 8601 con zona, en minutos, como `2026-10-18T21:40-06:00`) y `cuenta`. Uno por cada tablero de la cuenta, con una excepción: la base del tablero público la lee cualquiera con quien se comparta, así que en ese tablero la marca se escribe solo si el proyecto es público (`convenciones`, sección 7: su área no es restringida, y su línea del índice existe y no empieza por «restringido»); si no, solo en el completo, y si la cuenta solo tiene el público, no se escribe y se dice en media línea que el tablero se pone al día con su botón. Al abrir el tablero, su dueño ve arriba que hubo sesiones que aún no muestra, y la página se pone al día sola con la tarea del botón; la sincronización borra las marcas que recoge. No se lanza la tarea desde la conversación, porque la app pide permiso cada vez que una conversación lanza una tarea. Solo si la persona lo pide al cerrar («cierra y pon al día el tablero») se lanza con `fire_trigger`: con `list_triggers` (`enabled: true`, siguiendo `next_cursor`) se busca la tarea llamada «Regenerar tablero <organización>», con « completo» si es ese tablero, y se dispara si su aprobación es automática (`permission_mode` `auto`) y su carpeta (`derived_state.folders`) es la raíz conectada; la app pedirá permiso y la persona lo da. Si el tablero no tiene tarea o la cuenta no tiene el conector de tareas programadas, la página no puede ponerse al día sola: entonces se pone al día aquí mismo, como «Sincronizar» de la skill `tablero`. Si la escritura falla, se dice en media línea y la sesión queda cerrada igual: el tablero se pondrá al día con su botón o con «sincroniza el tablero».

### Qué respondo al terminar

Dos o tres líneas: qué archivos se escribieron y qué queda para la próxima. Si hay que avisar a otra área, se dice a quién. Si quedó algo en `fuentes/` pendiente de decidir si es confidencial, se dice. Del tablero no se dice nada si se apuntó el cierre; media línea solo si se lanzó porque la persona lo pidió, si se puso al día aquí o si algo falló. Nada más. El resumen largo ya está en los archivos.

---

## Cerrar el proyecto

Cuando el dueño dice que el proyecto terminó («cierra el proyecto», «esto ya está»). Antes se comprueba con él que se cumple lo que dice `Terminado significa`; si no, se dice qué falta y se espera.

1. `Estado actual` de `proyecto.md` abre con «Proyecto terminado el AAAA-MM-DD» y una línea de cómo acabó, y `En corto` queda solo con su frase en negrita, que lo dice en lenguaje llano; `Siguientes pasos` dice que no queda ninguno propio, y lo que siga vivo se nombra con el proyecto que lo recoge.
2. La línea del proyecto en el bloque `Proyectos` de `area.md` se queda sola, sin desglosar sus entregables (`convenciones`, sección 3, «Un proyecto cerrado»).
3. Una entrada en `sesiones.md` que lo cuenta, y en `decisiones.md` solo si cerrarlo fue una decisión que alguien tomó.

Nada se borra ni se mueve: los entregables siguen con su estado y se siguen citando.

## Lo que nunca hago al cerrar

Además de las prohibiciones de `convenciones`:

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
