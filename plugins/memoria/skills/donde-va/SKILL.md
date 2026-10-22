---
name: donde-va
description: Coloca cualquier material que llegue en el sitio correcto de la estructura. Usala cuando pregunten 'donde guardo esto?', peguen un documento o un enlace sin decir donde va, aparezca un archivo suelto en la raiz, o digan 'ordena Claude outputs'.
---

# Dónde va

Colocar cualquier cosa que llegue en el sitio correcto de la estructura. Es la skill que decide la adopción entre usuarios que no van a leer las convenciones. Antes de nada se cargan `convenciones` y su anexo `escribir.md`: sus prohibiciones aplican a todo lo que sigue.

## Cuándo

"¿Dónde guardo esto?", "me llegó este correo, ¿qué hago con él?", o cuando alguien pega un documento, un enlace o unas notas sin decir dónde van. También "ordena Claude outputs", o la frase que copia el tablero: va al final de esta skill.

También cuando aparece un archivo suelto en la raíz o en una carpeta que no le corresponde.

## Qué leo antes

1. `guia.md`: qué áreas hay, cuáles están restringidas y las reglas propias de la casa
2. El bloque `Proyectos` del `area.md` del área probable
3. El material en sí, lo justo para clasificarlo

Nada más. Colocar algo no necesita abrir un proyecto ni `base/`.

## La pregunta previa: a qué lado va

Antes de las seis, se resuelve si el proyecto al que pertenece el material está restringido. Si lo está, todo lo suyo va dentro de su carpeta, y nada de lo que hay dentro se nombra desde fuera. Si no lo está, va a su sitio normal, salvo el material sensible suelto de la pregunta 2.

Si el área o el proyecto están restringidos y no tengo acceso, la lectura falla y no coloco nada: lo digo, digo quién es su dueño y ahí se para.

## Las preguntas, en orden

Se para en la primera que dé un sí.

**1. ¿Es un enlace?** Va a `fuentes/enlaces.md` del proyecto, una fila con qué es, el enlace y qué tener presente. Si el archivo no existe, se crea con su tabla. No se guarda una copia de la página como archivo salvo que el usuario lo pida.

**2. ¿Lo produjo alguien de fuera del equipo del proyecto?** Exports, PDFs de terceros, transcripciones, correos, capturas, y también un documento o una presentación que ya vienen con forma de entregable. Va a `fuentes/` del proyecto, con un nombre legible. Las fuentes no se editan nunca.

No hay otra puerta. Todo lo que llega de fuera entra por `fuentes/`, aunque venga terminado y el proyecto lo vaya a usar tal cual: en ese caso el entregable es el documento que lo cita, no el archivo de fuera. Y no se guarda además una copia en ningún otro sitio de la raíz.

Antes de guardarlo se mira si trae indicios de información confidencial (la lista está en `convenciones`, sección 1, «Material sensible»). Si los trae, lo digo y propongo llevarlo a `restringido/`; el usuario decide si es confidencial o no. Si lo es, el archivo va a **`restringido/` del mismo proyecto**, y en el `fuentes/enlaces.md` público queda una fila con qué es, dónde está y qué tener presente (por ejemplo, que a los entregables solo sale el agregado). Nada se mueve sin que el usuario lo confirme.

Si la fuente ya existe en otro proyecto de la misma área, no se copia: se cita la original por su ruta.

**3. ¿Lo hizo el equipo del proyecto y se lo puedo dar a alguien de fuera del proyecto?** La pregunta 2 ya paró todo lo que venía de fuera, así que aquí solo queda lo propio. Si la respuesta es sí, va a `entregables/`, y entonces no se guarda tal cual: se convierte en un entregable con su cabecera, con la skill `entregable`.

**3b. ¿Lo hizo el equipo del proyecto pero no sale de él?** El inventario que hubo que levantar, las notas de una conversación, el análisis intermedio, el diagnóstico del que sale una propuesta, el encuadre de un trabajo que se absorbió. Va a `taller/` con su cabecera y su nombre en minúsculas y guiones, casi siempre en `borrador`. No es una fuente, porque lo escribió una sesión, y no es un entregable, porque nadie lo va a consumir desde fuera. La prueba es la de `convenciones`, sección 3: si no se lo puedo dar a nadie de fuera del proyecto, es taller.

**4. ¿Es un compromiso que cambia lo que se va a construir?** No es un archivo, es una entrada en `decisiones.md`. Se propone la entrada y se pide confirmación antes de registrarla.

**5. ¿Es contexto de la organización y no de un proyecto?** Organigrama, sistemas, políticas, vocabulario. Va a `base/`, que desde otra área no se toca. Se prepara el texto y se le pasa al responsable de contexto, que lo escribe en su sesión. Si es un sistema, el texto va en el formato de la tabla de `sistemas.md`: sistema, para qué, quién da acceso, antes de usarlo.

**6. Ninguna de las anteriores.** Va a `fuentes/` del proyecto más probable, y una fila en su `fuentes/enlaces.md` dice qué es y que está sin clasificar. Se decide más adelante, cuando esté claro.

No hay carpeta de borradores. Lo que no es material ni entregable ni decisión se guarda como fuente sin clasificar, o no se guarda.

## Si no hay proyecto al que pertenezca

Dos salidas, y ninguna es dejarlo suelto:

- Si el material sugiere un trabajo que va a durar, se propone crear el proyecto con la skill `nuevo`
- Si es contexto general de la organización, va por la vía de la pregunta 5

Nada se queda en la raíz ni en la carpeta del área. Un archivo huérfano hoy es un archivo que nadie encuentra en tres meses.

## Qué respondo

Una ruta concreta y un nombre de archivo propuesto. Un solo destino, no un menú de opciones. Si de verdad hay ambigüedad entre dos proyectos, una sola pregunta para desempatar.

Después de colocarlo, se dice en una línea qué es lo siguiente que hay que hacer con ese material, si es que hay algo.

## Ordenar «Claude outputs»

Es la carpeta donde la app de Claude deja lo que produce, fuera de cualquier proyecto (`convenciones`, sección 1). Ordenarla es llevar cada archivo a su proyecto.

Lo pide la persona con la frase, o lo propone la apertura mínima de cualquier conversación cuando encuentra algo ahí (skill `sesion`); en los dos casos es este mismo recorrido.

1. Se listan los archivos de «Claude outputs» con su fecha, sin abrirlos. Por el nombre, la fecha y las sesiones de esos días en los `sesiones.md` de la raíz, se propone a qué proyecto va cada uno y si va a `entregables/` (se puede dar a alguien de fuera) o a `taller/`. Lo que no tiene proyecto claro se pregunta; lo que ya existe dentro de un proyecto con el mismo contenido es una copia y se propone quitarlo.
2. La persona confirma la lista. Solo se mueve a las áreas que son suyas; lo que le toca a otra área se dice, con el nombre de su dueño, y se queda donde está.
3. Lo que por su nombre parece confidencial (contratos, propuestas con precio o cotización, currículums, nóminas, datos de clientes) va primero en la lista y se propone para `restringido/` del proyecto: en una carpeta compartida, «Claude outputs» la lee todo el equipo. Antes de mover el resto se pregunta lo de siempre: si algo trae datos personales, contratos, facturación o algo que no todos deban ver, también va a `restringido/`, con el sí de la persona.
4. Cada archivo se mueve con un nombre en minúsculas y guiones y entra como `borrador`. Sin consola en la computadora se mueve con el conector de Google Drive, como dice el anexo `sin-consola.md` de `convenciones`, y nunca se le pide a la persona que lo mueva a mano. En cada proyecto que recibió algo se deja una entrada en `sesiones.md`, «Ordenado desde Claude outputs», con lo que llegó.
5. Lo que sobra (copias, pruebas, capturas sin uso) no se borra sin el sí de la persona.

Se responde en dos o tres líneas: cuántos archivos fueron a qué proyectos, cuántos quedan y de quién son.

## Lo que nunca hago

Además de las prohibiciones de `convenciones` (anexo `escribir.md`):

- Crear una carpeta nueva para acomodar algo que no encaja. Si no encaja, es la pregunta 6
- Dejar algo en la raíz o en la carpeta de un área
- Colocar fuera de una carpeta restringida material que pertenece dentro de ella, aunque el usuario tenga acceso
- Mover archivos de un área que no es la del usuario, o colocar material en un proyecto ajeno sin avisar a su dueño
- Guardar un documento de terceros en `entregables/` tal cual, sin convertirlo
- Guardar en `fuentes/` algo que escribió una sesión. Eso es taller
- Dar tres opciones y dejar que el usuario elija. Si dudo, pregunto una cosa y decido

## Ejemplo completo

**Usuario:** me pasaron esto en una reunión, no sé dónde meterlo *[pega una tabla con los tiempos de aprobación por departamento]*

**Respuesta:**

> Es material crudo de una reunión, así que va a `compras/automatizacion-ordenes/fuentes/tiempos-aprobacion-por-departamento.md`. Lo guardo tal cual, y en `fuentes/enlaces.md` dejo una fila con quién lo pasó y en qué reunión.
>
> Lo siguiente: estos tiempos contradicen el export del ERP en el rango de 5.000 a 20.000 MXN, que es justo el hueco abierto del mapa de proceso. Cuando quieras lo miramos.

---

**Usuario:** y este Excel con los sueldos del equipo de compras, que lo necesito para el cálculo del tope

**Respuesta:**

> Trae nombres con salario, así que no lo guardo en `fuentes/`, donde lo lee todo el equipo. Propongo llevarlo a `compras/automatizacion-ordenes/restringido/` y dejar en `compras/automatizacion-ordenes/fuentes/enlaces.md` una fila: qué es, su liga, que lo pasó Recursos Humanos el 1 de septiembre y que a los entregables solo sale el total agregado. ¿Lo tratamos como confidencial?

**Usuario:** sí

**Respuesta:**

> Hecho. Para el cálculo del tope uso el total agregado, sin nombres.

---

**Usuario:** ¿y el organigrama nuevo de compras?

**Respuesta:**

> Eso es contexto de la organización, no de proyecto, así que va a `base/contexto.md` y esa carpeta no la toco yo.
>
> Te preparo el párrafo redactado para que se lo pases a quien mantiene el contexto. También conviene, porque `contexto.md` lleva 104 días sin actualizarse.
