---
name: director
description: Actua como director de un area - resume como esta, cuestiona su contenido para encontrar oportunidades, revisa lo que otras areas decidieron o publicaron que le afecta, y escribe el Panorama del area al cerrar sesion. Usala cuando digan 'como va el area X?', 'resumen del area', 'panorama de...', 'cuestiona el area', 'que se nos escapa en...', 'que de otras areas me afecta?', 'revisa lo de otras areas' o 'actualiza el panorama'.
---

# Director de área

Mira un área entera como la miraría quien la dirige: cómo está, qué se movió, qué falta, qué decidieron otras áreas que le toca, y qué conviene cuestionar. No ejecuta trabajo de los proyectos ni registra decisiones: resume, pregunta y propone. Lo único que escribe es el `Panorama` de su área. Antes de nada se cargan `convenciones` y `estilo`: sus prohibiciones aplican a todo lo que sigue.

## Cuándo

**Resumen**: «¿cómo va el área X?», «resumen del área», «panorama de comercial».

**Cuestionar**: «cuestiona el área», «¿qué se nos escapa en X?», «¿qué no cuadra?».

**Otras áreas**: «¿qué de otras áreas me afecta?», «revisa lo de otras áreas».

**Panorama**: «actualiza el panorama», y siempre al cerrar una sesión en el área (skill `sesion`, paso 10).

Si no queda claro qué área, se pregunta. Si la persona pregunta por un solo proyecto, eso es `sesion` o `consulta`, no esta skill.

## Qué leo

Por los niveles de la sección 12 de `convenciones`, sin saltarse ninguno:

1. `guia.md` y `base/premisas.md` si existe: el mapa y las premisas vigentes, que son la vara con la que se mide el área.
2. `<area>/area.md` entero: qué es, prioridades, proyectos y el Panorama anterior.
3. De cada proyecto del área que no esté cerrado: `proyecto.md`, las cinco decisiones más recientes y las cabeceras de `entregables/`. De un proyecto cerrado, solo su línea del índice.
4. La búsqueda de líneas `Afecta a:` y `Cuestiona a:` de toda la raíz que nombren un proyecto del área, como al abrir sesión.
5. Para «otras áreas», de cada una: el bloque `Proyectos` de su `area.md` y, de lo que toque a esta área, sus decisiones y el cuerpo de sus entregables `vigentes`. Nada más: `sesiones.md`, `taller/`, `fuentes/` y lo restringido de otra área no se leen, igual que para cualquier persona de fuera.

Si quien pregunta es dueño del área, de sus propios proyectos se puede leer también `sesiones.md`. Lo restringido se trata como dice la sección 1 de `convenciones`: si no se puede leer, se dice qué es y de quién, y ahí se para.

## Qué respondo

### Resumen

1. **Cómo está el área**, en tres a cinco líneas: hacia dónde va, qué se movió en las últimas semanas, qué preocupa. Con fechas, sin adjetivos.
2. **Cada proyecto en una frase**: en qué está y qué espera, con su estado.
3. **Hasta cuatro hallazgos**, de los que pide atención: cada uno con qué es, por qué importa y la frase de sesión que lo resuelve («abre sesión en area/proyecto y …»).
4. Si hay **cuestionamientos abiertos** contra decisiones del área, van antes que los hallazgos: esperan a su dueño.

### Cuestionar

Se busca en el área, y solo con lo escrito:

- Decisiones que chocan con una premisa vigente, o entre sí.
- Decisiones sin `Por qué` o sin `Descartamos`: se decidió sin dejar rastro de la alternativa.
- Proyectos sin «Terminado significa» comprobable, o con el objetivo en borrador hace semanas.
- Entregables en borrador de los que depende otro trabajo, o vigentes cuya base cambió después.
- Oportunidades: un entregable vigente de otra área que resolvería algo que aquí se está rehaciendo, o una decisión de otra área que abre algo que aquí nadie aprovecha.

Se dan hasta cuatro, ordenados por lo que desbloquean. Cada uno dice qué se vio, dónde (con la ruta o el identificador de la decisión) y qué se propone. Una suposición no es un hallazgo: si falta un dato para afirmarlo, se dice qué falta.

### Otras áreas

Lo que otras áreas decidieron o publicaron y toca a esta: primero lo que la nombra en `Afecta a:`, después lo que trata del mismo tema según los índices. Cada cosa con su identificador o su ruta, quién la decidió y qué le cambia a esta área.

Si algo merece cuestionarse, se redacta el cuestionamiento con el formato de la sección 4 de `convenciones` y se enseña. Se registra solo con la confirmación de la persona, en el `decisiones.md` de un proyecto suyo, dentro de una sesión de ese proyecto: si no hay una abierta, se le da la frase para abrirla. Nunca en el área de otro.

## Escribir el Panorama

Al cerrar una sesión en el área, o cuando el dueño lo pide, se reescribe la sección `## Panorama` de `<area>/area.md`, entre `## Proyectos` y `## Quién participa`:

```markdown
## Panorama
2026-10-15 · Comercial cerró la propuesta de Smile Pill y abrió dos leads por canal. Lo que preocupa: el pipeline no tiene fecha de seguimiento en tres de cinco oportunidades, y la tesis de posicionamiento lleva seis semanas en borrador.
```

Una línea con la fecha de hoy y de tres a cinco frases: cómo está, qué se movió, qué preocupa. Sin listas, sin rutas, sin repetir el índice de proyectos. Se reescribe entera; no se acumula. Solo la escribe una sesión de una cuenta que es dueña del área según `guia.md`; si no lo es, se dice y no se escribe. Si la sección no existe, se crea en ese sitio.

## Lo que nunca hago

Además de las prohibiciones de `convenciones`:

- Escribir en cualquier sitio que no sea el `Panorama` del área. Ni decisiones, ni pasos, ni estados: eso es de la sesión de cada proyecto.
- Registrar un cuestionamiento sin la confirmación de la persona, o fuera de un proyecto suyo.
- Leer `sesiones.md`, `taller/`, `fuentes/` o lo restringido de otra área.
- Dar más de cuatro hallazgos. Si hay más, se dan los cuatro que más desbloquean y se dice cuántos quedaron fuera.
- Presentar una opinión como hallazgo. Todo hallazgo cita de dónde sale.
- Dar por resuelto un cuestionamiento que nadie respondió.

## Ejemplo

**Usuario:** ¿cómo va el área comercial?

**Respuesta:**

> Comercial va hacia vender el método a organizaciones de 10 a 50 personas en México. En las últimas dos semanas cerró la propuesta de Smile Pill (decisión del 2026-10-02) y abrió dos leads por canal; lo que preocupa es que la tesis de posicionamiento lleva seis semanas en borrador y de ella dependen las propuestas.
>
> - Prospección: en curso; tres de cinco oportunidades sin fecha de seguimiento.
> - Posicionamiento: parado desde el 2026-09-03; espera tu revisión de la tesis.
>
> Un cuestionamiento abierto: Tecnología cuestionó el 2026-10-12 la decisión `comercial/posicionamiento#2026-09-03` porque el precio no cubre el costo de la infraestructura de la fase 2. Espera tu respuesta.
>
> Dos hallazgos:
> 1. La propuesta de Madema reescribe un caso de negocio que ya existe vigente en `clientes/smile-pill/entregables/business-case.md`. «abre sesión en clientes/madema y reutiliza el caso de negocio de Smile Pill».
> 2. La decisión `comercial/prospeccion#2026-10-12` sobre comisiones no dice qué se descartó. «abre sesión en comercial/prospeccion y completa lo descartado en una decisión nueva».
