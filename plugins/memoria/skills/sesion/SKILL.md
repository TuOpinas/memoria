---
name: sesion
description: Abre y cierra sesiones de trabajo sobre un proyecto. Usala cuando digan 'abre sesion', 'retomamos X', 'en que quedamos con...', 'cierra la sesion', 'guarda lo de hoy' o 'terminamos'.
---

# Sesión

Abrir y cerrar una sesión de trabajo sobre un proyecto. Antes de nada se carga la skill `convenciones`: su sección 12 fija qué se lee y en qué orden, y sus 19 prohibiciones aplican a todo lo que sigue.

## Cuándo

**Abrir**: "abre sesión en compras", "retomamos automatización de órdenes", "¿en qué quedamos con X?", o cualquier arranque de trabajo sobre un proyecto existente.

**Cerrar**: "cierra la sesión", "guarda lo de hoy", "terminamos".

Si no queda claro el proyecto, preguntarlo antes de leer nada. Nunca asumir el último proyecto usado.

---

# Abrir sesión

Abrir es solo lectura. No se escribe ningún archivo al abrir.

## Qué leo antes de responder

Por los niveles de la sección 12 de `convenciones`. Al abrir no se lee `base/`.

**Nivel 0**, siempre:

1. La primera línea de `metodo.md`, para la versión de la raíz
2. `guia.md` entero, para el mapa de áreas, quién responde por cada una y las reglas propias de la casa
3. El bloque `Proyectos` de `<area>/area.md`

**Nivel 1**, del proyecto ya identificado:

4. `<area>/<proyecto>/proyecto.md`
5. `decisiones.md` del proyecto, las 5 entradas más recientes
6. `sesiones.md`, las 3 entradas más recientes
7. `entregables/`, solo las cabeceras de cada archivo: nombre, estado, actualizado. `taller/` no se lee al abrir: entra a demanda, por su disparador de la sección 12

**El barrido de avisos**, que es lo único que recorre la raíz entera:

8. Las líneas `Afecta a:` de todos los `decisiones.md` de la raíz, buscando `area/proyecto` del proyecto activo. Es una búsqueda de un patrón de línea, no una lectura: solo se abre el encabezado de la entrada que dé positivo. Las carpetas restringidas a las que no tengo acceso fallan al leerse y se saltan sin más. Un aviso que salga de una carpeta restringida solo se da si el proyecto activo está dentro de ella

No leo `fuentes/`, ni `base/contexto.md`, ni `base/glosario.md`, ni `base/sistemas.md`, ni el resto de `area.md`. Entran cuando el trabajo del día los pida, por sus disparadores de la sección 12.

## Qué respondo

Tres bloques, en este orden y sin encabezados largos.

**Dónde quedó todo.** Cuatro o cinco líneas: objetivo del proyecto en una frase, qué se hizo en la última sesión, qué quedó pendiente. Nada de recapitular el proyecto entero.

**Avisos**, solo si aplican. Cinco comprobaciones:

- La versión de la primera línea de `metodo.md` es anterior a la del plugin. La raíz se quedó atrás y hay que regenerar `metodo.md`
- Alguna decisión de otro proyecto de la raíz nombra este proyecto en `Afecta a:`. Se cita la entrada con su fecha, quién decidió y de qué proyecto viene
- `base/contexto.md` lleva más de 90 días sin actualizarse, mirando solo su fecha `actualizado`, sin abrirlo
- Algún entregable tiene en `basado_en` un archivo cuya fecha `actualizado` es posterior a la suya, y por tanto puede estar desfasado
- Algún entregable lleva más de 30 días en `borrador`

Si no hay avisos, no se menciona que no los hay.

**Propuesta de trabajo.** Dos o tres focos posibles, tomados de los siguientes pasos de `proyecto.md`, de lo que quedó pendiente en la última sesión y de los avisos de otras áreas, cada uno con una línea de por qué ahora. Se ordenan por lo que desbloquea a otros: primero lo que otra persona está esperando, después lo que cierra algo empezado, al final lo que abre frente nuevo. Termina preguntando por cuál empezamos, y espera respuesta.

Si un aviso afecta al foco propuesto, se dice ahí mismo. No se empieza a trabajar sobre un entregable posiblemente desfasado sin avisar antes.

---

# Cerrar sesión

## Qué escribo y dónde

**1. `sesiones.md`.** Entrada nueva arriba del todo, sin tocar las anteriores:

```markdown
## 2026-08-29
Trabajamos en: rediseño del flujo de aprobación por monto.
Avances: mapa del proceso actual terminado, en borrador esperando a Ana.
Pendiente: confirmar con Finanzas el tope de 5.000 MXN.
```

Tres líneas. Si una sesión no cabe en tres líneas, es que hubo decisiones y esas van a su archivo.

**2. `decisiones.md`, solo si hubo decisiones.** Antes de escribir, se listan al usuario las decisiones detectadas y se pide confirmación explícita. El registro no se puede corregir después, así que nada entra sin que alguien lo confirme. Formato:

```markdown
## 2026-08-29 · Las órdenes bajo 5.000 MXN no pasan por aprobación
Decidió: Ana Pérez
Por qué: el 70% del volumen son órdenes pequeñas y consumían el 80% del tiempo de aprobación, según el export de órdenes de 2025.
Descartamos: tope acumulado mensual por proveedor, porque el ERP no expone el acumulado en tiempo real.
Afecta a: entregables/flujo-aprobacion.md · finanzas/cierre-mensual
```

Una decisión es un compromiso que cambia lo que se va a construir. Una preferencia expresada en voz alta no lo es. Ante la duda, se pregunta.

Si la decisión trae análisis detrás (opciones comparadas, tablas, cifras), el análisis va a un entregable del proyecto y la entrada lo cita. La entrada se queda con lo justo para entenderla sin abrir nada más.

Si `Afecta a` nombra un proyecto de otra área, se dice al usuario a quién tiene que avisar: el dueño de esa área, según `guia.md` o su `area.md`. La carpeta no notifica a nadie y la skill tampoco.

Si el proyecto activo lo lee todo el equipo y la decisión toca a un área o a un proyecto restringido, `Afecta a` lleva su nombre y nada más, porque ese nombre ya está listado: ni sus archivos, ni lo que contiene. Al revés, una decisión que se registra dentro de una carpeta restringida sí puede nombrar cualquier proyecto al que afecte.

**3. `proyecto.md`.** Se reescriben `Estado actual` y `Siguientes pasos`. Es un archivo vivo: se sustituye el contenido anterior, no se acumula.

**4. Bloque `Proyectos` de `area.md`.** Se reescribe la línea de este proyecto y, debajo, una línea por cada entregable `vigente` con su fecha `actualizado`. Solo esa parte del bloque; las líneas de los demás proyectos no se tocan. `Prioridades ahora` solo se reescribe si el dueño lo pide en esta sesión.

**5. Cabeceras de lo que se tocó.** Se actualiza `actualizado` en cada archivo modificado y se añade a `basado_en` cualquier fuente nueva que se haya usado.

**6. Lo que entró en `fuentes/` o en `taller/`.** Si durante la sesión se guardó algo en `fuentes/` sin haber pasado por la pregunta de si es confidencial, se pregunta ahora: si trae datos personales, facturación, contratos, credenciales o cualquier cosa que no todos deban ver, se propone llevarlo a `restringido/` del mismo proyecto y dejar su fila en el `fuentes/enlaces.md` público. El usuario decide; nada se mueve sin que lo confirme.

**7. Rotación.** Si `sesiones.md` supera las 1.500 líneas o cambia el año, se renombra con el año (`sesiones-2026.md`) y se abre uno nuevo. Sin preguntar.

## Qué respondo al terminar

Dos o tres líneas: qué archivos se escribieron y qué queda para la próxima. Si hay que avisar a otra área, se dice a quién. Si quedó algo en `fuentes/` pendiente de decidir si es confidencial, se dice. Nada más. El resumen largo ya está en los archivos.

---

## Lo que nunca hago

Además de las 19 prohibiciones de `convenciones`:

- Escribir algo al abrir sesión. Abrir es solo lectura
- Leer al abrir más de lo que dice el nivel 0 y el nivel 1
- Dar como aviso a alguien una decisión que leí en una carpeta restringida a la que su proyecto no pertenece
- Dar por cerrado un pendiente sin preguntar. Si no sé si algo quedó resuelto, lo pregunto

---

## Ejemplo completo

**Usuario:** retomamos automatización de órdenes

**Respuesta al abrir:**

> El proyecto busca quitar aprobaciones manuales en compras de bajo monto. La última sesión, el 14 de agosto, terminaste las entrevistas con Ana y con el equipo de Finanzas y quedó pendiente decidir el criterio de corte.
>
> Tres avisos. Finanzas registró el 20 de agosto en `finanzas/cierre-mensual/decisiones.md` que el cierre pasa al día 3, y marcó este proyecto como afectado: decidió Luis Romero. `base/contexto.md` no se toca desde hace 104 días. Y `entregables/mapa-proceso.md` lleva 41 días en borrador esperando a Ana.
>
> Tres focos posibles para hoy:
>
> 1. Cerrar el criterio de corte por monto. Es lo que bloquea el flujo de aprobación y Finanzas está esperando.
> 2. Revisar si el cambio de fecha de cierre toca el flujo de aprobación antes de seguir construyendo sobre él.
> 3. Empujar la revisión del mapa de proceso, que lleva seis semanas parado.
>
> ¿Por cuál empezamos?

**Usuario:** por el 1. [conversación de trabajo] ... cierra la sesión

**Antes de escribir:**

> Detecté una decisión en la conversación de hoy:
>
> Las órdenes bajo 5.000 MXN no pasan por aprobación. Decidió Ana Pérez. Descartamos el tope acumulado mensual porque el ERP no lo expone en tiempo real. Afecta al flujo de aprobación y al cierre mensual de Finanzas.
>
> ¿La registro así en `decisiones.md`?

**Usuario:** sí

**Respuesta al cerrar:**

> Escribí la entrada en `decisiones.md`, la sesión de hoy en `sesiones.md`, actualicé los siguientes pasos en `proyecto.md` y la línea del proyecto en `compras/area.md`. Marqué `entregables/flujo-aprobacion.md` como afectado por la decisión.
>
> La decisión afecta a `finanzas/cierre-mensual`. Avísale a Luis Romero, que es el dueño de Finanzas; la carpeta no lo hace por ti.
>
> Para la próxima queda validar el criterio con Finanzas y reanudar la revisión del mapa de proceso.
