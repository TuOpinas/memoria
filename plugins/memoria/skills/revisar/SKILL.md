---
name: revisar
description: Revisa un entregable, detecta lo que quedo desfasado y lo publica de borrador a vigente. Usala con 'revisa X', 'esto esta listo?', 'que esta desactualizado?', 'pasalo a vigente' o 'ya lo aprobo...'.
---

# Revisar

Tres trabajos distintos sobre el mismo material: revisar un entregable, detectar lo que quedó desfasado y publicar. Antes de nada se carga la skill `convenciones`: sus secciones 5 y 7 fijan estados y superficie pública, y sus 19 prohibiciones aplican a todo lo que sigue.

## Cuándo

**Revisar**: "revisa el mapa de proceso", "¿esto está listo?", o antes de enseñar algo a alguien de fuera del proyecto.

**Barrido**: "¿qué está desactualizado?", "¿qué hay parado en compras?", "¿hay algo aquí que no debería estar?", o al abrir sesión cuando aparecen avisos de desfase.

**Publicar**: "esto ya está listo", "pásalo a vigente", "ya lo aprobó Ana".

---

# Revisar un entregable

## Qué leo antes

1. El entregable completo, con su cabecera
2. `decisiones.md` completo del proyecto
3. Cada archivo listado en `basado_en`, con su fecha `actualizado`
4. La skill `estilo`
5. Si el documento sigue el brief o el comparativo, esa plantilla, que está en `plantillas/` dentro de la skill `nuevo`

## Las cinco comprobaciones

**1. Trazabilidad.** Cada afirmación no obvia sale de un archivo citado. Se listan las que no salen de ninguno. Si `basado_en` está vacía (`[]`), se dice desde la primera línea: el documento no se puede publicar así. Si cita una fuente de otra área o un archivo guardado en `restringido/`, también es bloqueante: de otra área solo se citan entregables vigentes y decisiones, y lo restringido se cita por su fila de `enlaces.md`. Si el entregable lo lee todo el equipo y cita algo restringido, es bloqueante siempre: la cita solo va en la otra dirección.

**2. Coherencia con las decisiones.** Nada en el documento contradice una entrada de `decisiones.md`, ni siquiera de hace meses.

**3. Frescura.** Ningún archivo de `basado_en` tiene una fecha `actualizado` posterior a la del entregable. Si la tiene, se dice qué cambió aguas arriba.

**4. Huecos.** Los huecos declarados en el documento siguen abiertos, o ya hay material para cerrarlos.

**5. Estilo.** Los siete patrones de la skill `estilo`. Se cuentan los guiones largos y se comparan con el umbral: más de uno cada 500 palabras es muletilla. Se buscan cifras sin fecha ni fuente.

## Qué respondo

Los hallazgos separados en dos grupos, nunca mezclados:

**Bloqueantes**, que impiden publicar: contradicciones con decisiones, afirmaciones sin fuente, `basado_en` vacía, huecos abiertos, fuentes desfasadas.

**Mejoras**, que no impiden nada: estilo, estructura, extensión.

Cada hallazgo con el pasaje concreto y la reescritura propuesta. El documento no se reescribe entero en silencio.

Un problema de estilo nunca es bloqueante. Un entregable feo pero correcto se puede publicar; uno bonito que contradice una decisión, no.

---

# Barrido de desfase

Sobre un proyecto o sobre un área entera. Se leen el bloque `Proyectos` de `area.md`, las cabeceras de los entregables y el listado de archivos de cada proyecto. Nunca el contenido. El bloque `Proyectos` dice qué entregables vigentes debería haber; las cabeceras dicen en qué estado están de verdad. Si las dos cosas no coinciden, eso también es un hallazgo.

Se devuelve una tabla ordenada por lo que más gente consume:

| Entregable | Estado | Días sin tocar | Problema |
|---|---|---|---|
| compras/…/flujo-aprobacion.md | vigente | 12 | `decisiones.md` cambió después |
| compras/…/mapa-proceso.md | borrador | 41 | Parado esperando al dueño |
| compras/…/modelo-datos.md | vigente | 8 | `basado_en` vacía |

Cuatro cosas se marcan siempre: entregables `vigente` con una fuente más reciente que ellos, entregables con más de 30 días en `borrador`, entregables `vigente` que citan un archivo `reemplazado`, y entregables `vigente` con `basado_en` vacía.

No se toca ningún archivo durante un barrido.

## Lo que entró por otro camino

En el mismo barrido, tres comprobaciones más sobre cada proyecto. Son de listado de carpeta: se mira qué archivos hay, no qué dicen.

1. **Archivos en `entregables/` sin cabecera** que no estén anotados en `proyecto.md` ni en una entrada de `decisiones.md`. Un binario que produjo el equipo consta en uno de los dos; si no consta en ninguno, o llegó de fuera o nadie respondió por él.
2. **Carpetas que la estructura no contempla** dentro del proyecto: cualquiera que no sea `entregables/`, `taller/`, `fuentes/` o `restringido/`. Un nivel de agrupación dentro de las tres primeras está permitido y no se reporta; dentro de `restringido/` no, porque es plano.

3. **Entregables que no salen del proyecto.** Un archivo en `entregables/` que no se le puede dar a nadie de fuera es taller: un inventario interno, unas notas de conversación, el análisis del que salió otro documento. Se listan con `taller/` como destino propuesto. Es lo que evita que `entregables/` acabe con un entregable de verdad y treinta que no lo son.

4. **Registros dentro de `taller/`.** Un `decisiones.md` o un `sesiones.md` ahí dentro solo es legítimo si es material adoptado y congelado; si alguien le está añadiendo entradas, el registro vivo del proyecto es el de su raíz.
3. **Archivos sueltos en la raíz del proyecto**, más allá de `proyecto.md`, `decisiones.md` y `sesiones.md`.

Cada hallazgo se reporta con su ruta y un destino propuesto, casi siempre `fuentes/`. Ninguno bloquea una publicación y ninguno se mueve sin que el usuario lo confirme: la regla es norma y no candado, y hay motivos legítimos para que algo esté fuera de sitio un rato.

El almacén de datos de una aplicación apuntado a la raíz se dice aparte, en la primera línea del barrido. No es un archivo fuera de sitio: crece solo, nadie responde por lo que hay dentro y rompe la carpeta como memoria.

---

# Publicar

Pasar de `borrador` a `vigente`. Es el único momento en que un documento se vuelve consumible por otras áreas, así que tiene requisitos.

## Requisitos

1. La revisión se pasó y no quedan hallazgos bloqueantes
2. No hay huecos abiertos, o el dueño del proyecto los acepta de forma explícita y quedan escritos en el documento
3. `basado_en` no está vacía. Si el documento es material adoptado y no hay forma de reconstruir sus fuentes, el dueño del proyecto acepta el hueco de forma explícita y queda escrito en el documento, en una línea bajo el título: de quién venía el material, con qué fecha y por qué no hay trazabilidad. Esa línea no nombra rutas ni carpetas del sistema del que se migró
4. **Lo pide el dueño del proyecto, y se comprueba.** El dueño es quien figura en `Quién participa` de `proyecto.md`, y su cuenta está junto a su nombre en `guia.md`. Se contrasta contra la cuenta desde la que se abrió esta sesión. Si no coinciden, no se publica, y se dice quién tiene que pedirlo. Si la identidad de la cuenta no está disponible, se pregunta quién lo pide y se anota en `sesiones.md` de quién vino la petición

Si falta cualquiera de los cuatro, se dice cuál falta y no se publica.

## Qué escribo

1. `estado: vigente` y la fecha de hoy en `actualizado`
2. Si sustituye a otro entregable, el viejo pasa a `estado: reemplazado` con `reemplazado_por` apuntando al nuevo
3. La línea del entregable en el bloque `Proyectos` de `area.md`, debajo de su proyecto, con la fecha de hoy
4. Una línea en `sesiones.md` al cerrar la sesión, indicando qué se publicó

Publicar no es una decisión y no entra en `decisiones.md`. Lo que se decidió ya está registrado; publicar solo cambia quién puede leerlo.

## Después de publicar

Se avisa de quién consume este entregable, según el campo `Consumen esto` de `proyecto.md`, para que el dueño se lo comunique. El sistema no notifica a nadie, y no fingir que lo hace es parte del método.

---

## Lo que nunca hago

Además de las 19 prohibiciones de `convenciones`:

- Publicar sin comprobar que quien lo pide es el dueño del proyecto
- Publicar con `basado_en` vacía sin que el dueño acepte el hueco y quede escrito
- Reescribir un entregable durante una revisión sin aprobación previa
- Tratar un hallazgo de estilo como bloqueante
- Marcar algo como desfasado sin haber comparado fechas reales
- Leer el cuerpo de los entregables durante un barrido
- Revisar y modificar entregables de otra área. Se propone al dueño y ahí termina
- Cerrar un hueco eligiendo la fuente que parece más fiable
- Tratar como hallazgo bloqueante algo que apareció en el listado de carpeta. Se dice, no se detiene nada

## Ejemplo completo

**Usuario:** revisa el mapa de proceso, creo que ya está

**Respuesta:**

> Dos bloqueantes y tres mejoras.
>
> **Bloqueantes:**
>
> 1. Sigue abierto el hueco de quién aprueba entre 5.000 y 20.000 MXN. La entrevista y el export se contradicen y no ha entrado material nuevo.
> 2. El paso 4 dice que todas las órdenes pasan por validación presupuestal, pero la decisión del 29 de agosto exime a las de menos de 5.000 MXN. El documento quedó desfasado respecto a `decisiones.md`.
>
> **Mejoras:** siete guiones largos en 1.200 palabras, cuando el umbral es uno cada 500; dos párrafos que anuncian antes de decir; y la cifra "el 70% del volumen" sin decir de qué periodo ni de qué export sale. Te paso las reescrituras si quieres.
>
> El punto 2 lo puedo corregir ahora mismo con la decisión registrada. El punto 1 necesita que alguien confirme el dato, no lo puedo cerrar yo.

---

**Usuario:** pásalo a vigente, ya lo aprobó Ana

**Respuesta:**

> No lo publico. La dueña del proyecto es Ana Pérez según `proyecto.md`, y esta sesión está abierta desde tu cuenta, que en `guia.md` es la de Luis Romero. Tiene que pedirlo ella. Además sigue abierto el hueco de quién aprueba entre 5.000 y 20.000 MXN: si Ana acepta publicarlo con el hueco, lo dejo escrito en el documento y entonces sí pasa a vigente.
