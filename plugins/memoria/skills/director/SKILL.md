---
name: director
description: Actua como director de un area - resume como esta, cuestiona su contenido para encontrar oportunidades, revisa lo que otras areas decidieron o publicaron que le afecta, y escribe el Estatus del area al cerrar sesion. Usala cuando digan 'como va el area X?', 'resumen del area', 'estatus de...', 'panorama de...', 'cuestiona el area', 'que se nos escapa en...', 'que de otras areas me afecta?', 'revisa lo de otras areas', 'actualiza el estatus del area' o 'actualiza el panorama'.
---

# Director de área

Mira un área entera como la miraría quien la dirige: cómo está, qué se movió, qué falta, qué decidieron otras áreas que le toca, y qué conviene cuestionar. No ejecuta trabajo de los proyectos ni registra decisiones: resume, pregunta y propone. Lo único que escribe es el `Estatus` de su área, con sus prioridades. Antes de nada se cargan `convenciones`, cuya sección 12 dice cómo se lee, con su anexo `escribir.md` (formatos y prohibiciones), y `estilo`. La excepción es el `Estatus` del área al cerrar sesión: ahí basta `escribir.md`, que trae su forma y su voz; «actualiza el estatus del área» (o «actualiza el panorama», como se decía hasta la 1.21) lee el área y carga todo lo anterior.

## Cuándo

**Resumen**: «¿cómo va el área X?», «resumen del área», «estatus de comercial».

**Cuestionar**: «cuestiona el área», «¿qué se nos escapa en X?», «¿qué no cuadra?».

**Otras áreas**: «¿qué de otras áreas me afecta?», «revisa lo de otras áreas».

**Estatus del área**: al cerrar una sesión en el área (skill `sesion`, anexo `cerrar.md`, paso 10), o cuando su responsable dice «actualiza el estatus del área» (o «actualiza el panorama»), o pide cambiar sus prioridades. Son los únicos disparadores, y todos piden la cuenta del responsable del área: si cierra quien colabora, el `Estatus` del área no se toca.

Si no queda claro qué área, se pregunta. Si la persona pregunta por un solo proyecto, no es esta skill: si es su responsable, se abre sesión (`sesion`); si no, es `consulta`.

## Qué leo

Por los niveles de la sección 12 de `convenciones`, sin saltarse ninguno:

1. `guia.md` y `base/premisas.md` si existe: el mapa y las premisas vigentes, que son la vara con la que se mide el área.
2. `<area>/area.md` entero: su `Estatus` anterior con las prioridades (o, sin migrar, `Prioridades ahora` y `Panorama`), qué es y sus proyectos.
3. De cada proyecto del área que no esté cerrado: `proyecto.md`, las cinco decisiones más recientes y las cabeceras de `entregables/`. De un proyecto cerrado, solo su línea del índice.
4. La búsqueda de líneas `Afecta a:` y `Cuestiona a:` de toda la raíz que nombren un proyecto del área o el área entera (`area/`), como al abrir sesión.
5. Para «otras áreas», de cada una: su `Estatus` (o `Panorama`, sin migrar) y el bloque `Proyectos` de su `area.md`, el «Estatus» de los proyectos que toquen a esta área, y de esos, sus decisiones, el cuerpo de sus entregables `vigentes` y la cabecera de sus sesiones (fecha, título y «Tema»). Nada más: el cuerpo de `sesiones.md`, `taller/`, `fuentes/` y lo restringido de otra área no se leen, igual que para cualquier persona de fuera. Lo que se dice de otra área empieza por lo que su director escribió.

Sin carpeta conectada (teléfono, web), se lee la raíz en Drive en solo lectura como dice el anexo `sin-carpeta.md` de la skill `sesion`, y el `Estatus` del área no se escribe: se guarda como nota del área en la cola del tablero, con la forma que dice ese anexo (`area` en lugar de `proyecto`), y la siguiente sesión del responsable en cualquier proyecto del área lo enseña al abrir. Si quien pregunta solo colabora, el `Estatus` del área no se guarda ni como nota: es del responsable.

Si quien pregunta es responsable del área o colabora en ella, de los proyectos del área se puede leer también `sesiones.md`; quien colabora solo en un proyecto, el de ese proyecto. Lo restringido se trata como dice la sección 1 de `convenciones`: si no se puede leer, se dice qué es y de quién, y ahí se para.

## Qué respondo

### Resumen

1. **Cómo está el área**, en tres a cinco líneas: hacia dónde va, qué se movió en las últimas semanas, qué preocupa. Con fechas, sin adjetivos.
2. **Cada proyecto en una frase**: en qué está y qué espera, con su estado.
3. **Hasta cuatro hallazgos**, de los que pide atención: cada uno con qué es, por qué importa y la frase de sesión que lo resuelve («abre sesión en area/proyecto y …»).
4. Si hay **cuestionamientos abiertos** contra decisiones del área, van antes que los hallazgos: esperan a su responsable.

### Cuestionar

Se busca en el área, y solo con lo escrito:

- Decisiones que chocan con una premisa vigente, o entre sí.
- Decisiones sin `Por qué` o sin `Descartado`: se decidió sin dejar rastro de la alternativa.
- Proyectos sin una segunda frase de `Objetivo` comprobable (cuándo termina o cada cuánto se revisa), o con el objetivo en borrador hace semanas.
- Entregables en borrador de los que depende otro trabajo, o vigentes cuya base cambió después.
- Oportunidades: un entregable vigente de otra área que resolvería algo que aquí se está rehaciendo, o una decisión de otra área que abre algo que aquí nadie aprovecha.

Se dan hasta cuatro, ordenados por lo que desbloquean. Cada uno dice qué se vio, dónde (con la ruta o el identificador de la decisión) y qué se propone. Una suposición no es un hallazgo: si falta un dato para afirmarlo, se dice qué falta.

### Otras áreas

Lo que otras áreas decidieron o publicaron y toca a esta: primero lo que la nombra en `Afecta a:`, después lo que trata del mismo tema según los índices. Cada cosa con su identificador o su ruta, quién la decidió y qué le cambia a esta área.

Si algo merece cuestionarse, se redacta el cuestionamiento con el formato de la sección 4 de `escribir.md` y se enseña en cita, tal como quedará escrito («Cómo se enseña antes de escribir» de `sesion/cerrar.md`). Se registra solo con la confirmación de la persona, en el `decisiones.md` de un proyecto suyo, dentro de una sesión de ese proyecto: si no hay una abierta, se le da la frase para abrirla. Nunca en el área de otro.

## Escribir el Estatus del área

Con los disparadores de arriba, se reescribe la sección `## Estatus` de `<area>/area.md` (en un área sin migrar, ocupa el sitio del `Panorama`; `cerrar.py` lo hace solo) con la forma y la voz de `escribir.md` (sección 2, «Estructura de `area.md`»): se reescribe entera, no se acumula: la fecha, la frase en negrita, «Se completó», las prioridades del área debajo de «Siguiente» (las que había, salvo que su responsable las cambie), «Falta decidir» y «Preocupa» si tienen algo, y una línea por proyecto activo que dice cómo va. No lleva nada de `restringido/`, ni línea de un proyecto restringido, ni ningún dato personal, aunque la sesión los haya leído. Solo la escribe una sesión de una cuenta que es responsable del área según `guia.md`; si no lo es, se dice y no se escribe.

Al cerrar una sesión no se relee el área para escribirlo: basta el `Estatus` anterior del área, lo que la sesión ya leyó y escribió y, de los demás proyectos del área, la cabecera y el `Estatus` de los que cambiaron después de su fecha (`sesion`, `cerrar.md`, paso 10). «Actualiza el estatus del área» sí lee lo que dice «Qué leo».

Con la misma voz escribe el cierre de sesión el `Estatus` de cada proyecto (`escribir.md`, sección 3): lo de un proyecto, para quien no va a abrir nada más. Al resumir el área, la línea de cada proyecto sale de su `Estatus` cuando lo tiene.

## Lo que nunca hago

Además de las prohibiciones de `convenciones` (anexo `escribir.md`):

- Escribir en cualquier sitio que no sea el `Estatus` del área. Ni decisiones, ni pasos, ni estados: eso es de la sesión de cada proyecto.
- Registrar un cuestionamiento sin la confirmación de la persona, o fuera de un proyecto suyo.
- Dar más de cuatro hallazgos. Si hay más, se dan los cuatro que más desbloquean y se dice cuántos quedaron fuera.
- Presentar una opinión como hallazgo. Todo hallazgo cita de dónde sale.
- Dar por resuelto un cuestionamiento que nadie respondió.

## Ejemplo

**Usuario:** ¿cómo va el área comercial?

**Respuesta:**

> Comercial va hacia vender el servicio a organizaciones de 10 a 50 personas. En las últimas dos semanas cerró la propuesta de Lumbre (decisión del 2026-10-02) y abrió dos leads por canal; lo que preocupa es que la tesis de posicionamiento lleva seis semanas en borrador y de ella dependen las propuestas.
>
> - Prospección: en curso; tres de cinco oportunidades sin fecha de seguimiento.
> - Posicionamiento: parado desde el 2026-09-03; espera tu revisión de la tesis.
>
> Un cuestionamiento abierto: Tecnología cuestionó el 2026-10-12 la decisión `comercial/posicionamiento#2026-09-03` porque el precio no cubre el costo de la infraestructura de la fase 2. Espera tu respuesta.
>
> Dos hallazgos:
> 1. La propuesta de Arcadia reescribe un caso de negocio que ya existe vigente en `clientes/lumbre/entregables/caso-de-negocio.md`. «abre sesión en clientes/arcadia y reutiliza el caso de negocio de Lumbre».
> 2. La decisión `comercial/prospeccion#2026-10-12` sobre comisiones no dice qué se descartó. «abre sesión en comercial/prospeccion y completa lo descartado en una decisión nueva».
