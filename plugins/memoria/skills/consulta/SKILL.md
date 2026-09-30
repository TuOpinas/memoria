---
name: consulta
description: Responde preguntas sobre lo que la organizacion ya sabe, leyendo solo la superficie publica de la raiz y sin escribir nada. Usala cuando pregunten 'que sabemos de X?', 'alguien ya trabajo esto?', 'que se decidio sobre...?', 'hay algo hecho sobre...?' o 'quien lleva...?'.
---

# Consulta

Responder una pregunta con lo que ya está escrito en la raíz, diciendo de dónde sale cada cosa. Es la skill que usa alguien de otra área, un programador antes de tocar código, o cualquiera que quiera saber si algo ya existe antes de empezarlo. Antes de nada se carga la skill `convenciones`: su sección 12 fija qué se lee y en qué orden, su sección 7 qué es público, y sus 19 prohibiciones aplican a todo lo que sigue.

## Cuándo

"¿Qué sabemos de X?", "¿alguien ya trabajó esto?", "¿qué se decidió sobre los topes de aprobación?", "¿hay algo hecho sobre proveedores?", "¿quién lleva el tema de facturación?".

También cuando en medio de otra tarea hace falta saber qué hizo otra área antes de construir encima.

No es abrir sesión. Si la pregunta es sobre el proyecto en el que el usuario va a trabajar hoy, eso es la skill `sesion`.

## Qué leo antes de responder

Por los niveles de la sección 12 de `convenciones`, parándome en el primero que responde:

1. `guia.md`: qué áreas hay, quién responde por cada una y las reglas propias de la casa
2. El bloque `Proyectos` del `area.md` de las áreas pertinentes. Casi siempre esto ya dice si existe algo y dónde
3. Solo si hace falta, del proyecto que toque: `proyecto.md`, `decisiones.md` completo y las cabeceras de `entregables/`. `taller/`, `fuentes/` y `sesiones.md` no: son taller privado y no se consultan desde fuera del proyecto
4. El cuerpo de un entregable `vigente`, solo si la pregunta pide el contenido y no basta con saber que existe

De `base/` no leo nada por defecto. `glosario.md` entra si la pregunta trae una sigla o un nombre interno que no entiendo; `contexto.md`, si la pregunta es sobre la organización; `sistemas.md`, si es sobre un sistema.

Un entregable en `borrador` se menciona si existe, con su estado, pero no se cita su contenido como si fuera verdad de la organización.

Si `guia.md` dice que un área está restringida, hay dos casos. Si tengo acceso, se lee igual que cualquier otra: su superficie pública son sus entregables vigentes y sus decisiones. Si no lo tengo, la lectura falla y ahí se para: se dice que el área existe, que su trabajo no es visible desde aquí y quién es su dueño, y la respuesta se da con lo que sí se puede leer. Lo mismo vale para un proyecto restringido dentro de un área que sí leo, y para `restringido/` dentro de un proyecto.

Al revés no se cruza nunca: una respuesta que se dé a alguien que no tiene ese acceso no lleva nada de lo leído en una carpeta restringida, ni siquiera resumido.

## Qué respondo

Respuesta corta y primero la respuesta, no el recorrido. Después, una línea por cada cosa que digo, con la ruta de donde salió:

> Sí, Compras decidió el 29 de agosto que las órdenes bajo 5.000 MXN no pasan por aprobación. Lo decidió Ana Pérez.
>
> De dónde sale: `compras/automatizacion-ordenes/decisiones.md`, entrada del 2026-08-29. El flujo completo está en `compras/automatizacion-ordenes/entregables/flujo-aprobacion.md`, vigente desde el 2026-08-30.

Si hay varias fuentes que se contradicen, se dicen las dos con su fecha y no se elige una.

Si no hay nada escrito sobre el tema, se dice en una línea y se propone dónde debería vivir: qué área y, si aplica, si merece un proyecto nuevo con la skill `nuevo` o una entrada en `base/`. No se inventa una respuesta con lo que parece razonable.

Si la pregunta es sobre quién lleva algo, la respuesta es la persona con nombre y apellido que dice `guia.md`, `area.md` o `proyecto.md`, nunca el nombre del área.

## Lo que nunca hago

Además de las 19 prohibiciones de `convenciones`:

- Escribir o modificar ningún archivo. Consultar es solo lectura
- Contar a alguien lo que leí en una carpeta restringida a la que esa persona no tiene acceso, aunque lo resuma o lo diga con otras palabras
- Deducir lo que hay en un área restringida por los nombres de sus carpetas, o dar por hecho que no hay nada solo porque no puedo abrirla
- Leer más de lo que hace falta. Si `guia.md` ya responde, no abro el área; si el bloque `Proyectos` responde, no abro el proyecto
- Citar el contenido de un entregable que no esté `vigente` como si lo estuviera
- Responder desde la memoria de la conversación en vez de desde los archivos
- Dar una respuesta sin la ruta de donde salió
- Inventar una respuesta cuando no hay nada escrito

## Ejemplo completo

**Usuario:** ¿alguien ya trabajó lo de los topes de aprobación por monto? Lo necesito para el conector del ERP

**Respuesta:**

> Sí. Compras lo tiene decidido y documentado.
>
> La decisión: las órdenes bajo 5.000 MXN no pasan por aprobación; entre 5.000 y 20.000 MXN aprueba el jefe de área. Decidió Ana Pérez el 29 de agosto de 2026. Sale de `compras/automatizacion-ordenes/decisiones.md`.
>
> El flujo completo, con los estados que espera el ERP, está en `compras/automatizacion-ordenes/entregables/flujo-aprobacion.md`, vigente desde el 30 de agosto. Es lo que tendrías que citar en tu `decisiones.md` cuando ancles la lógica del conector.
>
> Hay además un `mapa-proceso-actual.md` en el mismo proyecto, pero está en borrador: no lo uses como base todavía.

---

**Usuario:** ¿qué sabemos de la evaluación de proveedores de logística?

**Respuesta:**

> Nada escrito. Ni `operaciones/area.md` ni `compras/area.md` tienen un proyecto sobre proveedores de logística, y en `base/contexto.md` solo aparece el nombre del proveedor actual.
>
> Si se va a trabajar, le corresponde a Operaciones, cuyo dueño es Marta Ruiz según `guia.md`. Sería un proyecto nuevo; si quieres lo arrancamos con `nuevo`.
