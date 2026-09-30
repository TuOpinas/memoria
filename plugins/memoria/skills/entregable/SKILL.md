---
name: entregable
description: Crea o actualiza un entregable de un proyecto. Usala cuando pidan 'prepara el documento de...', 'necesito un documento con...', 'documenta lo que decidimos sobre...', o 'actualiza el entregable X'.
---

# Entregable

Crear o actualizar un entregable. Antes de nada se cargan `convenciones`, cuyas 19 prohibiciones aplican a todo lo que sigue, y `estilo`, sin excepciones, porque un entregable sale del proyecto.

## Cuándo

**Crear**: "prepara el mapa del proceso", "necesito un documento con X", "documenta lo que decidimos sobre Y".

**Actualizar**: "actualiza el flujo de aprobación", "esto cambia el modelo de datos", o cuando una decisión registrada afecta a un entregable existente.

## Qué leo antes de escribir nada

Por los niveles de la sección 12 de `convenciones`. Escribir un entregable es de los pocos trabajos que justifican bajar a casi todo:

1. El bloque `Proyectos` de `<area>/area.md`, para saber qué entregables vigentes hay ya en el área
2. `<area>/<proyecto>/proyecto.md`
3. `decisiones.md` **completo**, no solo las últimas. Un entregable que contradice una decisión de hace ocho meses es peor que no tenerlo
4. Las cabeceras de los demás entregables del proyecto
5. `base/contexto.md`, porque el documento sale del proyecto y hay criterios transversales que aplican sin que nadie los diga
6. `base/glosario.md`, si el documento usa siglas o nombres internos; `base/sistemas.md`, si toca un sistema
7. La plantilla, si el documento es un brief o un comparativo: están en `plantillas/` dentro de la skill `nuevo`
8. Las fuentes concretas que apliquen, de `fuentes/`
9. Si el entregable ya existe, el entregable entero

## Antes de escribir

Tres comprobaciones, resueltas con el usuario en dos o tres líneas, no con un interrogatorio.

**¿Ya existe algo que cubra esto?** Si hay un entregable vigente sobre el mismo tema, en este proyecto o en otro del área según el bloque `Proyectos`, se actualiza ese o se construye encima. No se crea uno nuevo. Una sola verdad por tema.

**¿Quién lo va a leer?** Un documento para el equipo del proyecto y uno para el comité de dirección no se escriben igual. Si es para fuera del proyecto, el estilo se aplica con más rigor y se asume que el lector no conoce el contexto.

**¿De dónde sale cada cosa?** Toda afirmación no obvia tiene que poder rastrearse a un archivo de `basado_en`. Si algo importante viene solo de la conversación de hoy, se guarda primero en `fuentes/` como nota y luego se cita. Lo que solo existe en el chat se pierde. Toda cifra lleva fecha o fuente en el mismo párrafo.

**¿Hay algo que no todos deban ver?** Si el material que voy a usar trae indicios de información confidencial (la lista está en `convenciones`, sección 1, «Material sensible»), lo digo y propongo dos cosas: llevar ese material a `restringido/` del proyecto con su fila en el `enlaces.md` público, y dejar en el entregable solo lo agregado o anonimizado que sí puede leer todo el equipo. El usuario decide si es confidencial. Un entregable es superficie pública: lo que entra en él lo lee toda la organización.

## Qué escribo y dónde

**Ubicación**: `entregables/`, dentro del proyecto. Nombre en minúsculas y guiones, estable de por vida, sin número de fase ni de versión.

Antes de escribirlo compruebo que de verdad es un entregable: **¿se lo puedo dar a alguien de fuera del proyecto?** Si la respuesta es no, lo que me están pidiendo vive en `taller/` y lo digo. Un inventario que hubo que levantar, unas notas de conversación o el análisis intermedio del que saldrá después el entregable son taller, aunque estén bien escritos.

**Cabecera**: tres claves. `estado: borrador` siempre al crear, la fecha de hoy en `actualizado`, y en `basado_en` todas las rutas que se usaron de verdad. La clave la escribo yo siempre; la persona no tiene que rellenarla. No se listan archivos que se leyeron por encima y no aportaron nada. No hay clave de dueño: el dueño es el del proyecto, en `proyecto.md`. Si este documento tiene otro responsable, se dice en la primera línea del cuerpo, debajo del título.

El `taller/` del propio proyecto sí se cita en `basado_en`: es de donde sale el entregable. El de otro proyecto no, igual que su `fuentes/`. Una fuente de otro proyecto de la misma área se cita por su ruta original, nunca se copia a este `fuentes/`. Fuentes de otra área no se citan: de otra área solo entregables vigentes y decisiones. El material guardado en `restringido/` no se cita directamente; se cita su fila de `fuentes/enlaces.md`.

Un entregable restringido puede citar en `basado_en` lo que quiera de lo que sí lee todo el equipo. Uno que lee todo el equipo no cita nada restringido, ni por su ruta ni contando lo que dice: la cita va en una sola dirección. Lo aprendido en una carpeta restringida sale reescrito, como entregable propio de un proyecto que lee todo el equipo y sin los datos ni los nombres de donde salió.

La lista vacía `[]` solo se admite para material adoptado, que ya existía antes de entrar en la estructura y del que no hay forma de saber de dónde salió. Un entregable escrito aquí siempre tiene fuentes, aunque sea una sola nota en `fuentes/`. Un `[]` lo detiene `revisar` antes de publicar.

Un entregable a medias vive en `entregables/` con `estado: borrador`, no en otra carpeta. El estado es lo que avisa a los demás de que todavía no se puede consumir.

**Cuerpo**: título en `#` inmediatamente después de la cabecera. Si el documento es un brief o un comparativo, su plantilla; si no, la estructura que pida el contenido, siempre con la conclusión primero.

**Al actualizar**: se reescribe en su sitio, porque un entregable es un archivo vivo. No se acumulan secciones de "actualización de agosto". Se pone la fecha nueva en `actualizado` y se añaden las fuentes nuevas.

**Al reemplazar**: cuando un entregable queda superado por otro distinto, el viejo pasa a `estado: reemplazado` con la clave `reemplazado_por` y su ruta. No se borra nunca, porque alguien puede tenerlo citado.

**Cuando respalda una decisión**: si el documento es el análisis detrás de una entrada de `decisiones.md` (opciones, tablas, cifras), la entrada lo cita en `Afecta a` o en `Por qué` y el análisis vive aquí, no en el registro.

**Formatos finales** (PPTX, HTML, PDF): se generan desde el `.md` y se guardan junto a él, con el mismo nombre. El `.md` sigue siendo la fuente de verdad y el derivado se regenera cuando cambia. Un derivado editado a mano deja de ser un entregable y pasa a ser un problema.

**Binarios nativos** (una presentación armada directo en PowerPoint o Keynote, una hoja de cálculo armada en Excel o Numbers, sin ningún `.md` detrás): lo que decide dónde van es quién los produjo. Si los hizo el equipo del proyecto, con las manos que sea, son producto suyo y van a `entregables/` con el mismo nombre en minúsculas y guiones. Si vinieron de fuera van a `fuentes/`, aunque lleguen terminados, y el entregable es el documento que los cita. No llevo cabecera dentro del archivo porque el formato no la admite; anoto su estado y de qué se construyó en `proyecto.md` o en la entrada de `decisiones.md` que lo produjo. No hay carpeta aparte para binarios: donde vive la raíz ya los previsualiza.

## Qué respondo al terminar

Dónde quedó, en qué estado, y qué le falta para poder pasar a revisión. Dos o tres líneas.

Si al escribirlo aparecieron decisiones que nadie había tomado, se listan al usuario. No se meten en el documento como si estuvieran cerradas.

## Lo que nunca hago

Además de las 19 prohibiciones de `convenciones`:

- Escribir una afirmación que no sale de una fuente citable
- Dejar `basado_en` vacía en un entregable que escribí yo
- Citar en `basado_en` un `sesiones.md`, una fuente o un `taller/` de otra área, o un archivo de `restringido/`
- Escribir en `entregables/` algo que no sale del proyecto. Eso es `taller/`
- Construir sobre un entregable que no esté `vigente`, sin avisar de que no lo está
- Crear un entregable nuevo cuando ya hay uno vigente sobre el mismo tema
- Meter en un entregable datos que parecen confidenciales sin haberlo dicho antes

## Ejemplo completo

**Usuario:** prepara el mapa del proceso de compras actual

**Respuesta:**

> Antes de escribir, dos cosas.
>
> En `compras/area.md` no hay ningún entregable vigente sobre el proceso actual, y en `entregables/` de este proyecto tampoco, así que lo creo nuevo. Voy a construirlo con la grabación de la entrevista con Ana, el export de órdenes y las tres decisiones registradas sobre los topes por monto, siguiendo la plantilla de brief.
>
> ¿Esto lo va a leer solo el equipo del proyecto, o también Finanzas y Sistemas?

**Usuario:** también Finanzas y Sistemas

**Respuesta:**

> Listo: `entregables/mapa-proceso-actual.md`, en `borrador`.
>
> Escrito para alguien de fuera de Compras, con el glosario de la organización para las siglas del ERP. Basado en la entrevista con Ana, el export de órdenes de 2025 y `decisiones.md`; las tres rutas están en la cabecera. Del Excel de sueldos, que está en `restringido/`, solo entra el total agregado del equipo, citado por su fila en `enlaces.md`.
>
> Le falta una cosa para pasar a revisión: en el paso de validación presupuestal, la entrevista y el export se contradicen sobre quién aprueba entre 5.000 y 20.000 MXN. Lo dejé marcado como hueco en el documento en lugar de elegir uno.
