---
name: migrar
description: Adopta una carpeta que sigue otra estructura y la trae al metodo sin borrar los originales. Usala cuando digan 'migra esta carpeta', 'trae esto al metodo', 'adopta lo que hay en...', 'convierte estos documentos a la estructura' o cuando aparezca una carpeta con ADR, logs de sesion o carpetas numeradas.
---

# Migrar

Traer al método una carpeta que se organizó de otra forma: otro sistema de documentación, una carpeta de proyecto heredada, un repositorio con ADR y logs. La migración crea la estructura nueva al lado, deja los originales intactos y termina con un reporte de qué se trajo, qué se dejó y qué quedó como hueco. Antes de nada se carga `convenciones`: sus 19 prohibiciones aplican a todo lo que sigue.

## Cuándo

"Migra esta carpeta", "trae esto al método", "adopta lo que hay en la carpeta del cliente X", "convierte estos documentos a la estructura", o cuando aparece una carpeta con archivos como `ADR-004.md`, `00-contexto.md`, `AGENTS.md`, `sesion-2026-03-12.md` o carpetas numeradas.

Migrar es una tarea larga. Se hace por proyecto, no toda la carpeta de golpe, y se cierra cada proyecto antes de empezar el siguiente.

## Qué leo antes de escribir nada

1. `guia.md` y `<area>/area.md` de destino: qué proyectos ya existen, para no duplicar
2. `base/glosario.md` y las reglas propias de `guia.md`, para nombrar las cosas como las llama la casa
3. La carpeta origen entera, pero por capas: primero la lista de archivos con tamaño y fecha, después los índices o archivos de contexto que traiga (`README`, `00-contexto`, `AGENTS.md`), y solo al final el cuerpo de cada documento

## Los pasos

**1. Inventario.** Una tabla de todo lo que hay en el origen: ruta, qué es en una línea, fecha del último cambio, y a qué se va a convertir (registro, entregable, fuente, contexto de la organización, no se trae). Se enseña al usuario y se corrige con él antes de mover nada. Un archivo que el usuario no reconoce se pregunta, no se adivina.

**2. Mapeo a proyectos.** Cada grupo de archivos del origen se asigna a un proyecto del método, existente o nuevo. Antes, se decide si el destino está restringido: si lo que se migra es el trabajo de un área o de un proyecto que no puede leer todo el equipo, el destino entero es esa carpeta, y hace falta acceso a ella para poder escribir. Un mismo origen no se reparte entre lo restringido y lo que no: si trae cosas de los dos, son dos migraciones.

Los nombres reservados (`proyecto.md`, `decisiones.md`, `sesiones.md`, `area.md`) no sobreviven a una adopción: se renombran a lo que de verdad es cada archivo, como dice `convenciones`, sección 3. Y si lo que se adopta es un proyecto del propio método que se pliega dentro de otro, sus registros se funden con los del que recibe, sin editar ninguna entrada. Un proyecto nuevo se crea con la skill `nuevo`, con su dueño con nombre y apellido, que es bloqueante también aquí. Si el origen mezclaba dos trabajos en una carpeta, salen dos proyectos. Si el origen tenía un cuarto nivel de carpetas, ahí había dos proyectos.

**3. Decisiones.** Cada ADR o archivo de decisión del origen pasa a ser una entrada de `decisiones.md` con el formato del método: fecha, título en una frase, quién decidió, por qué, qué se descartó, a qué afecta. Si el ADR traía análisis (opciones comparadas, tablas, cifras), el análisis no cabe en la entrada: se convierte en un entregable del proyecto, con la plantilla `comparativo.md` si compara opciones, y la entrada lo cita en `Afecta a`. Si el ADR no dice quién decidió, se pregunta; si nadie lo sabe, se escribe "no consta" y queda como hueco en el reporte.

**4. Sesiones.** Todos los logs de sesión del origen, estén en un archivo por sesión o en una carpeta, se consolidan en un solo `sesiones.md` del proyecto. Cada log pasa a una entrada con encabezado `## AAAA-MM-DD`, tomada del nombre del archivo o de su contenido, y el cuerpo viejo se conserva debajo tal cual, con sus encabezados bajados a `###` para que no compitan con las fechas. Las entradas van de la más reciente a la más antigua. No se resume ni se reescribe lo que decían: la regla de histórico permite convertir este registro porque nadie lo ha consumido todavía, pero convertir es cambiar el formato, no el contenido.

**5. Entregables y taller.** Los documentos se reparten por una pregunta: ¿se lo puedo dar a alguien de fuera del proyecto? Los que sí pasan a `entregables/` con cabecera del método; los que no, a `taller/` con la misma cabecera. Casi todo lo que se adopta de un sistema anterior es taller: inventarios, notas de reunión, análisis intermedios, contextos de proyecto. Lo que sigue vale para los que van a `entregables/`. `estado: borrador` siempre, salvo el caso de abajo. `basado_en` se rellena con lo que se pueda rastrear; si no hay forma de saber de dónde salió el documento, se deja `[]` y `revisar` lo pedirá antes de publicar. Si el documento del origen tenía un responsable distinto del dueño del proyecto, se dice en la primera línea del cuerpo. Entran `vigente` solo si quien migra era el dueño del material en el origen y lo pide de forma explícita; en ese caso `sesiones.md` deja constancia de que se publicaron al migrar por esa razón. Si no, publicar lo pide el dueño del proyecto después.

Cuando un entregable entra con `basado_en: []`, la línea bajo el título dice de quién venía el material y con qué fecha, y por qué no hay trazabilidad. No nombra las rutas ni las carpetas del sistema de origen: la raíz que estrena el método no guarda rastro de él, y quien lea esa línea dentro de seis meses necesita saber de quién viene el documento, no en qué carpeta vivía antes. El mapa de rutas viejas a rutas nuevas vive en el manifiesto, que es de quien migró. Un entregable binario del origen (una presentación o una hoja de cálculo sin `.md` detrás, guardada antes en una carpeta aparte porque el sistema viejo no la previsualizaba) entra igual a `entregables/`, sin cabecera propia; su estado y procedencia se anotan en `proyecto.md`. Si lo produjo alguien ajeno a la organización que migra, no es un entregable suyo: va a `fuentes/`.

**6. Documentos largos.** Un documento de contexto largo del origen (`00-contexto.md`, un README de cuarenta pantallas) no se trae entero como entregable. Se extraen de él las cifras con su fecha y los pendientes abiertos: los del proyecto van a `Estado actual` y `Siguientes pasos` de `proyecto.md`; los del área van a `Prioridades ahora` de `area.md`, y ahí solo si el dueño del área lo aprueba. El documento entero se guarda en `fuentes/` como material adoptado, por si hace falta volver a él.

**7. Fuentes.** Migrar es la excepción declarada a la puerta única de `fuentes/`: lo que se adopta es el trabajo anterior de la propia organización, no material de fuera, y por eso puede entrar como entregable en borrador. Lo que en el origen ya era material de entrada sigue la regla normal. Exports, PDFs, transcripciones, correos, capturas: a `fuentes/` con nombre en minúsculas y guiones. Los enlaces sueltos, a `fuentes/enlaces.md`, una fila cada uno. Si una fuente ya está en otro proyecto de la misma área, no se duplica: se cita la original.

Antes de traer cada archivo se mira si trae indicios de información confidencial (la lista está en `convenciones`, sección 1, «Material sensible»). Los que los traen se listan al usuario en un bloque aparte del inventario, con la propuesta de llevarlos a `restringido/` del proyecto que les toca y dejar su fila en el `fuentes/enlaces.md` público. El usuario decide archivo por archivo. Ninguno va a `fuentes/` ni a `restringido/` sin esa confirmación; mientras no la haya, se quedan en el origen y constan como pendientes en el reporte.

**8. Nombres y enlaces.** Todo lo que se trae se renombra a la convención: sin prefijos numéricos, sin fechas, sin versiones, sin números de fase. Después se recorren los archivos traídos y se reescribe cada enlace interno para que apunte a la ruta nueva. Un enlace que apuntaba a algo que no se trajo se sustituye por una frase que dice a qué apuntaba y que quedó en el origen. Los enlaces wiki `[[asi]]` se convierten en enlaces normales.

**9. Lo que no se trae.** Una lista explícita, con el motivo de cada uno: archivos de instrucciones para la IA (`AGENTS.md`, `CLAUDE.md` de la carpeta, prompts), porque el método los sustituye por las skills y `guia.md`; índices mantenidos a mano, porque el bloque `Proyectos` de `area.md` los reemplaza; archivos `.canvas`, plantillas del sistema anterior, carpetas vacías, borradores que nadie reconoce, duplicados. Cada uno con su razón en una línea.

**10. Cierre.** La línea del proyecto y sus entregables en el bloque `Proyectos` de `area.md`, y una entrada en `sesiones.md` del proyecto que dice que se migró, desde dónde y qué día.

## Qué respondo al terminar

Un reporte de tres bloques, y nada más:

**Qué se trajo.** Una línea por archivo del origen con su ruta nueva y qué es ahora (entrada de decisión, entregable en borrador, fuente).

**Qué se dejó.** La lista del paso 9, con el motivo de cada uno.

**Qué quedó como hueco.** Decisiones sin quién decidió, entregables con `basado_en` vacía, cifras sin fecha, enlaces que apuntaban a algo que no existe, dueños por confirmar. Cada hueco con la ruta donde está marcado.

Si la migración se hace por proyectos, el reporte se da al cerrar cada uno.

El reporte se guarda como entregable en la raíz de quien migró, en su proyecto de la relación con esa organización. En la raíz de la organización migrada no entra: cuenta el trabajo del proveedor y habla del sistema de origen, que su equipo no usó. Lo que sí entra allá, y en el proyecto donde se usa, son las decisiones recuperadas pendientes de confirmar y las filas de material confidencial que quedó fuera de alcance.

## Lo que nunca hago

Además de las 19 prohibiciones de `convenciones`:

- Borrar, mover o modificar un archivo del origen. Se copia; el origen queda como estaba hasta que el usuario decida qué hacer con él
- Migrar sin enseñar antes el inventario y el mapeo
- Resumir o reescribir el contenido de un log de sesión al consolidarlo. Se cambia el formato, no lo que decía
- Dejar un entregable migrado en `vigente` sin que el dueño del origen lo haya pedido
- Traer `AGENTS.md`, índices manuales, prefijos numéricos o cualquier cosa de la lista de lo que no existe en `convenciones`
- Traer a `entregables/` un documento que produjo alguien ajeno a la organización que migra. Va a `fuentes/`
- Traer a `entregables/` un documento que no sale del proyecto. Va a `taller/`
- Sacar de una carpeta restringida un archivo que pertenece dentro de ella, o dejar fuera la ruta de lo que se migró dentro
- Escribir en el reporte de la migración el contenido de lo restringido. Se cuenta cuántos archivos fueron y a qué carpeta, nunca qué decían
- Dejar en la raíz migrada rastro del sistema de origen: sus rutas, sus nombres de carpeta, su vocabulario o el reporte de la migración
- Inventar una fecha para una entrada cuya fecha no se puede saber. Se usa la fecha del archivo y se marca como aproximada

## Ejemplo completo

**Usuario:** trae al método la carpeta del proyecto de automatización que tenemos en el sistema viejo

**Respuesta:**

> Inventario de `viejo/compras-automatizacion/`: 23 archivos.
>
> | Origen | Qué es | Va a |
> |---|---|---|
> | `00-contexto.md` | Contexto del proyecto, 1.800 líneas | Cifras y pendientes a `proyecto.md`; el archivo entero a `fuentes/contexto-original.md` |
> | `decisiones/ADR-001.md` a `ADR-004.md` | Cuatro decisiones, dos con tabla comparativa | Cuatro entradas en `decisiones.md`; las dos tablas, a un entregable `comparativo-topes-aprobacion.md` |
> | `sesiones/2026-03-12.md` … `2026-08-14.md` | Once logs | Un `sesiones.md` con once entradas |
> | `entregables/flujo-aprobacion-v3-FINAL.md` | El flujo, dado por bueno | `entregables/flujo-aprobacion.md`, en borrador |
> | `insumos/export-ordenes.csv` | Export de órdenes | `fuentes/` |
> | `insumos/nomina-compras.xlsx` | Nómina con nombres y salarios | Parece confidencial: propongo `restringido/` y su fila en `enlaces.md` |
> | `AGENTS.md`, `indice.md`, `plantilla-adr.md` | Instrucciones, índice manual, plantilla | No se traen |
>
> El destino es `compras/automatizacion-ordenes/`, que no existe. ¿La dueña es Ana Pérez? Sin eso no creo el proyecto. ¿Y la nómina la tratamos como confidencial?

**Usuario:** sí, Ana. Y sí, la nómina es confidencial. Adelante

**Respuesta al terminar:**

> **Qué se trajo.** Cuatro entradas en `decisiones.md` (2026-03-12, 04-02, 06-20, 08-14), con el análisis de las dos últimas en `entregables/comparativo-topes-aprobacion.md`, en borrador. Once entradas en `sesiones.md`. `entregables/flujo-aprobacion.md`, en borrador, con `basado_en` apuntando al export y a la entrevista. Cuatro archivos en `fuentes/`. `nomina-compras.xlsx` en `restringido/`, con su fila en `fuentes/enlaces.md`. Estado actual y cuatro pendientes en `proyecto.md`, sacados del contexto original.
>
> **Qué se dejó.** `AGENTS.md`: lo sustituyen las skills y `guia.md`. `indice.md`: lo sustituye el bloque Proyectos de `compras/area.md`. `plantilla-adr.md`: el formato de decisión es el del método. Dos borradores de `insumos/` que nadie reconoce, con el nombre `sin-titulo`. El origen sigue intacto en `viejo/`.
>
> **Qué quedó como hueco.** ADR-002 no dice quién decidió; está como "no consta". La cifra "40% de ahorro" del contexto no tiene fecha ni fuente y quedó marcada en `proyecto.md`. Tres enlaces del flujo apuntaban a un documento de Sistemas que no está en la carpeta; quedaron como frase con el nombre del documento.
