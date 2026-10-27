# Escribir en la carpeta

Anexo del contrato (`convenciones`). Reúne lo que hace falta para escribir en un proyecto y en su área: la estructura de `area.md` y de `proyecto.md`, los formatos de los registros, la cabecera, la rotación y las prohibiciones. Se carga antes de cualquier escritura en la carpeta. Para cerrar sesión, registrar una premisa o escribir el `Estatus` de un área basta con este anexo; para crear un área o un proyecto, guardar o publicar un documento, mover material, migrar o montar una raíz se carga además el contrato entero (`SKILL.md`, junto a este archivo). Si la carpeta está conectada pero el shell de la computadora no la ve, se escribe además como dice el anexo `sin-consola.md`, junto a este archivo, y se lee antes de la primera escritura. Las secciones llevan el número que tienen en el contrato, y las que se citan sin estar aquí (1, 6, 7, 11, 12) son las del contrato.

**Los nombres de antes de la 1.22** (`Dueño`, `Panorama`, `En corto`, `afirma`, `enlaces.md`…) los lista el contrato, sección 11, «Los nombres de antes de la 1.22»: se leen las dos formas y se escribe solo la nueva. El cierre que escribe el `Estatus` en un área o un proyecto sin migrar retira los bloques viejos de estatus y lleva a «Siguiente» las prioridades que falten; lo demás lo renombra la migración (skill `sesion`).

## 2. Estructura de `area.md`

Fija, porque varias skills leen y escriben en ella. Responde las mismas preguntas que el proyecto y en el mismo orden: cómo va, qué es, qué contiene, quién. El orden de las secciones es este en los dos niveles; una sección que falta se crea en su sitio.

```markdown
# [Nombre del área]

## Estatus
AAAA-MM-DD · **[Cómo está el área, en una frase.]**
- **Se completó:** [lo terminado en el área desde el estatus anterior]
- **Siguiente:**
  - [una prioridad del área, con quién; de tres a cinco, una por línea]
- **Falta decidir:** [qué, y quién lo decide]
- **Preocupa:** [lo que puede salir mal]
- `nombre-del-proyecto/`: [cómo va, en una frase]

## Qué es
[Dos o tres líneas]

## Proyectos
- `nombre-del-proyecto/` — qué es
  - nombre-del-entregable — [su aportacion] · actualizado AAAA-MM-DD

## Quién participa
Responsable: [nombre y apellido]
Colabora: [nombre y apellido], solo si alguien colabora en el área
```

`Estatus` es el resumen ejecutivo del área, con la estructura y la voz del `Estatus` del proyecto (sección 3): la fecha en que se escribió, la frase en negrita, «Se completó» y «Siguiente» siempre, «Falta decidir» y «Preocupa» solo si tienen algo, y después una línea por proyecto activo del área, que dice cómo va, no qué es (eso lo dice el bloque `Proyectos`). «Siguiente» son las prioridades del área, una por línea debajo de él, en orden: se reescriben en cada `Estatus`, y por eso no envejecen; el tablero las numera y deja marcarlas cumplidas. Los proyectos cerrados no llevan línea, y los restringidos tampoco: de ellos no se dice nada más allá de su nombre, que ya está en `Proyectos`. Como `area.md` lo lee todo el equipo, en la carpeta y en el tablero de cada uno, no lleva nada de `restringido/` ni datos personales, aunque la sesión que lo escribe los haya leído. Lo estrena `nuevo` al crear el área, con la fecha y solo «Siguiente», y lo reescribe la skill `director` al cerrar una sesión en esa área, o cuando su responsable pide «actualiza el estatus del área»; se reescribe entero cada vez y no lleva historia: lo que pasó está en los registros de los proyectos. Si no existe, el área todavía no tiene estatus; no se escribe a mano.

El bloque `Proyectos` es el índice de contexto del área: una línea por proyecto y, debajo, una línea por cada entregable `vigente`. La línea del entregable dice lo que dice su clave `aportacion` (sección 5), copiada tal cual, para que el índice y el documento no digan dos cosas distintas; si el entregable no la tiene, lleva una línea de qué es hasta que la tenga. Un proyecto cerrado ocupa solo su línea, sin desglose. La línea de un proyecto restringido empieza por «restringido: responsable Nombre.» y sigue con su descripción (`` - `ronda/` — restringido: responsable Beto Prueba. Ronda de inversión ``): el nombre es lo único que ve quien no puede leerlo, y el tablero y la apertura lo toman de ahí. Lo escriben el cierre de sesión, la publicación de un entregable y la creación de proyectos, no una persona, y `verificar.sh` avisa si falta algún proyecto o algún entregable vigente. No lo regenera ninguna herramienta: las descripciones de los proyectos son lo que hace útil el índice, y una lista rehecha desde los nombres de archivo dice menos que la que había. Es lo primero que lee cualquier skill antes de abrir un archivo del área.

`Quién participa` es donde vive el responsable del área. No hay otra clave para él. Las cuentas de quienes colaboran en el área están en la celda Cuenta de `guia.md`, que es lo que decide quién escribe; la línea `Colabora:` del área dice sus nombres.

## 3. Estructura de `proyecto.md`

Fija, porque varias skills escriben en ella:

```markdown
# [Nombre del proyecto]

## Estatus
AAAA-MM-DD · **[Lo último que se completó, y lo que sigue y cuándo.]**
- **Se completó:** [lo terminado desde el estatus anterior, con su fecha, y para qué sirve ya]
- **Siguiente:** [hasta tres pasos, cada uno con quién y para cuándo]
- **Falta decidir:** [qué, y quién lo decide]
- **Preocupa:** [lo que puede salir mal]

## Objetivo
[Dos frases. Qué problema resuelve y para quién; y cuándo termina, concreto y comprobable, o cada cuánto se revisa si no termina.]

## Alcance
Entra: [lo que entra]
No entra: [lo que queda fuera]

## Siguientes pasos
- [Lista corta]

## Quién participa
Responsable: [nombre] ([área])
Colabora: [nombre (correo)], solo si alguien colabora en este proyecto sin colaborar en el área
```

Las secciones van en este orden, el mismo patrón que el área (sección 2): cómo va, qué es, qué contiene, quién.

`Estatus` y `Siguientes pasos` son las dos únicas secciones que reescribe el cierre de sesión. El resto cambia poco y solo a petición del responsable.

`Estatus` es el estatus para quien no va a leer más: lo primero que ve el tablero y lo que responde Claude cuando alguien pregunta cómo va. Lo escribe el cierre de sesión desde lo que pasó en ella, con la voz del director (skill `director`), lo enseña para que se confirme como la entrada de la bitácora, y se sustituye entero cada vez. Responde cuatro preguntas: qué se completó, qué sigue, qué falta decidir y qué preocupa. Cinco líneas como mucho. La primera empieza por la fecha en que se escribe y sigue con la frase en negrita: lo último que se completó y lo próximo que pasa y cuándo, en lenguaje de persona, no de archivo. «Se completó» y «Siguiente» van siempre (si en la sesión no se completó nada, «Se completó» dice lo último terminado y cuándo; al arrancar un proyecto, solo «Siguiente»); «Falta decidir» y «Preocupa», solo si tienen algo. Cada línea, de una o dos frases, con nombres de personas y fechas absolutas («el 19 de octubre», nunca «el lunes»), sin rutas ni identificadores. Lo que no aplica se omite: no se escribe «nada». Lo lee todo el equipo, en la carpeta y en el tablero de cada uno: no lleva nada de `restringido/` ni datos personales, ni en «Preocupa». No es una historia: lo que pasó está en `sesiones.md` y en `decisiones.md`, y el contexto que dura (dónde vive algo, desde cuándo se trabaja así) va a `Alcance` o a un archivo de `taller/`. Un proyecto sin `Estatus` sigue siendo válido: lo escribe su siguiente cierre.

`Responsable`, en `Quién participa`, responde por todo el proyecto: por sus entregables y sus decisiones, y es quien pide publicar. Quien colabora registra las decisiones de su propio trabajo, y el responsable puede reemplazarlas (sección 1, «Quién colabora»). Si un documento concreto tiene otro responsable, se dice en la primera línea del cuerpo de ese documento, no en la cabecera.

Quién consume un proyecto lo dicen las líneas `Afecta a:` y `basado_en` que lo nombran.

### Un proyecto cerrado

Cuando se cumple lo que dice la segunda frase de `Objetivo`, el responsable lo pide y el `Estatus` queda en una línea, la fecha y la frase en negrita, que empieza por **«Proyecto terminado el AAAA-MM-DD.»** y dice cómo acabó. A partir de ahí el proyecto no evoluciona: sus archivos siguen donde están, con el estado que tengan, y su `Siguientes pasos` dice que no queda ninguno propio.

Lo que cambia es el índice. En el bloque `Proyectos` de su `area.md` **un proyecto cerrado ocupa una línea y no desglosa sus entregables**, y el `Estatus` del área no le dedica línea. Quien necesite el detalle abre su `proyecto.md`.

Un proyecto cerrado no se borra ni se saca de la raíz. Se sigue citando, sus entregables vigentes se siguen consumiendo y su `decisiones.md` sigue explicando por qué las cosas están como están.

### Plazos: en tiempo de trabajo con IA

Cuando se dice cuánto lleva algo («para cuándo» en `Siguiente`, una propuesta de trabajo, un plan), se estima en el tiempo que de verdad cuesta trabajando con la IA, en sesiones o en horas, no en lo que tardaría un equipo de personas sin ella: construir, redactar o revisar algo acotado cabe casi siempre en una sesión. Lo que alarga un trabajo es lo que espera a una persona (que pruebe, apruebe, responda, firme o haga algo en otra herramienta), y eso se dice aparte, con quién y desde cuándo. Ante la duda, se da lo que cabe en la próxima sesión y lo que queda esperando a alguien, sin inventar fechas. En `Siguiente`, «para cuándo» es la fecha de la próxima sesión prevista si la hay, y si no, «cuando <persona> <haga X>»; nunca una fecha estimada de terminar.

### La voz del `Estatus`

Lo lee alguien con poco tiempo que no va a abrir nada más, en el proyecto y en el área. La primera frase dice el hecho, no lo anuncia, y sobra toda palabra que se puede borrar sin perder información. Personas con nombre, fechas absolutas, sin adjetivos y sin rutas. La primera frase no empieza por el nombre del área o del proyecto, que ya está en el título de todo lo que la enseña, y no dice «hoy», «ayer» ni «esta semana»: se lee días después, y la fecha ya va delante. Es la voz del director de área y el estilo de la casa (skills `director` y `estilo`); para escribir un `Estatus` basta con este párrafo.

### Personas de fuera

A una persona de fuera de la organización (de un cliente, un proveedor, un socio) se la escribe «Nombre Apellido (Organización)»: al menos una vez en el `Estatus` o en `Siguientes pasos` del proyecto que la nombra, y siempre en `Decidió:` cuando decide ella. Después, en el mismo texto, basta su nombre. Es la única forma en que el tablero la reconoce y la agrupa por organización en «Con otros»: no adivina personas por las mayúsculas, así que «Ana Ruiz» sin paréntesis no sale, y «Sistema Nuevo Contable» no es nadie. A quien es de la organización se la escribe con nombre y apellido, sin paréntesis; un correo nunca va en estos textos. Si su organización no consta, se pregunta: no se inventa.

### Qué guarda el cierre y qué no

**Siempre**: la entrada de la sesión; las decisiones confirmadas, con su porqué y lo que se descartó; `Estatus` y `Siguientes pasos` al día; el estado de cada entregable que se tocó (su cabecera y su fila en `area.md`).

**Nunca**:
- Un **valor vivo**: lo que cambia sin que nadie edite la memoria (un saldo, un precio de lista, cuántos registros hay en un sistema, el estado de un ticket). Se consulta en su fuente cuando hace falta; una cifra que sí se guarda lleva fecha y fuente (prohibición 13).
- Lo que **se puede consultar en una fuente**: se cita dónde está, no se copia.
- **Credenciales**, ni datos personales que el trabajo no necesita.
- Lo que la propia sesión **probó y desechó sin llegar a decisión**: un intento, un borrador tirado, un error corregido en la misma conversación. Lo que se descartó al decidir sí va, en `Descartado`.

Ante la duda de si algo merece quedar, se pregunta; no se guarda por si acaso.

## 4. Vivo o registro, nunca las dos cosas

**Un archivo vivo se reescribe** y siempre refleja el presente. Nadie necesita leer su historia para entenderlo.

**Un registro solo crece.** Las entradas nuevas van arriba y las anteriores no se editan jamás, ni para corregir. Si una decisión cambia, se añade una entrada nueva con la línea `Reemplaza:` que apunta a la anterior.

Un registro nunca vive dentro de un archivo vivo, porque la primera reescritura lo borra.

**La fecha de una entrada, y la de `actualizado`, es la del día en la zona horaria de la organización** («Zona horaria:» de `guia.md`; la línea HOY de `abrir.py`), no la del reloj de la consola ni del contenedor, que van en UTC y por la tarde ya dicen mañana. Una entrada fechada mañana desordena el registro: queda encima de las de hoy que se escriban después, y `cerrar.py` la rechaza.

### Formato de `decisiones.md`

Único para todos los proyectos:

```markdown
## AAAA-MM-DD · Título que dice la decisión en una frase
Decidió: Nombre Apellido
Por qué: … (puede ser más de un párrafo)
Descartado: …
Reemplaza: area/proyecto#AAAA-MM-DD · su título
Afecta a: entregables/x.md · otra-area/proyecto (qué le cambia, en media línea)
```

Las líneas van en este orden y solo están las que tienen algo que decir: `Descartado`, `Reemplaza` (o `Responde a`) y `Afecta a` son opcionales. `Afecta a` va siempre la última, porque es la que avisa a otros proyectos.

Una decisión que contesta a un cuestionamiento añade `Responde a: <identificador del cuestionamiento>`; una que sustituye a otra anterior añade `Reemplaza: <identificador de la sustituida> · <su título>` (la anterior no se edita: sigue en el registro, y el tablero encadena las dos en la trayectoria del proyecto); y una que se apoya en una premisa puede nombrarla en `Por qué` («premisa P2»).

**Identificador de una entrada.** Cada entrada de `decisiones.md`, decisión o cuestionamiento, se cita como `area/proyecto#AAAA-MM-DD`, la fecha de su encabezado. Si ese día hay más de una en el mismo `decisiones.md`, la más antigua es `#AAAA-MM-DD` y las siguientes `#AAAA-MM-DD-2`, `-3`, contando desde la de más abajo, que es la más antigua; los cuestionamientos cuentan en la misma serie. Se deduce del registro: no se escribe en el encabezado, y como las entradas no se editan ni se reordenan, no cambia nunca. Una entrada sin fecha válida en el encabezado no tiene identificador y no se puede citar. Dentro del mismo proyecto basta `#AAAA-MM-DD`.

**Cuestionamientos.** Cualquiera puede cuestionar una decisión de otro proyecto o una premisa. El cuestionamiento se escribe en el `decisiones.md` de un proyecto propio, desde una sesión de quien cuestiona, porque nadie escribe en el área de otro:

```markdown
## AAAA-MM-DD · Cuestionamiento: el tope de 5.000 MXN deja fuera las compras recurrentes
Planteó: Nombre Apellido
Por qué: … (qué no cuadra, con su dato o su fuente)
Cuestiona a: compras/automatizacion-ordenes#2026-08-29
```

`Cuestiona a` lleva un identificador de decisión o `premisa P<n>`. El cuestionamiento sigue abierto hasta que el responsable de lo cuestionado registra en su proyecto una decisión con `Responde a: <identificador del cuestionamiento>`, que mantiene lo decidido o lo reemplaza. Mantenerlo también es una decisión («lo mantengo, porque…»): se registra igual, con su por qué, y es lo que cierra el cuestionamiento. Una premisa la responde el responsable de contexto con una premisa nueva que lleve `Reemplaza P<n>`, que cierra los cuestionamientos abiertos a `P<n>`, o con una entrada con `Responde a:` en el `decisiones.md` de un proyecto suyo si la mantiene. Un cuestionamiento no es una decisión, aunque viva en el mismo registro y se cite igual: no se cuenta como tal.

Cuando decide alguien de fuera de la organización (un cliente, un proveedor, un socio), `Decidió: Nombre Apellido (Organización)` («Personas de fuera», sección 3): el tablero separa a quienes deciden de dentro y de fuera, y a los de fuera los agrupa por organización.

Una decisión recuperada al migrar que nadie ha confirmado todavía lleva `Decidió: Nombre Apellido (pendiente de confirmar)`. La confirma su responsable con una entrada nueva que la da por buena o la cambia; la recuperada no se edita.

Una entrada tiene lo justo para entender qué se decidió y por qué sin abrir nada más. El análisis que respalda la decisión (opciones, tablas, cifras) no va en la entrada: va a un entregable del proyecto y la entrada lo cita en `Afecta a` o en `Por qué`.

`Afecta a` lleva rutas relativas al proyecto para lo que está dentro de él, y `area/proyecto` cuando la decisión toca a otro proyecto de la raíz, o `area/` cuando toca a un área entera, que avisa en cualquiera de sus proyectos. Cada destino admite detrás un paréntesis corto con la consecuencia concreta; sin él, quien recibe el aviso sabe que algo le toca pero no qué. Los destinos se separan con `·` y la línea no se parte en varias.

### Formato de `sesiones.md`

```markdown
## AAAA-MM-DD
Tema: …
Avances: …
Escribió: entregables/arquitectura.md, taller/guia-fase-1.md
Publicó: entregables/mapa-epicas.md
Sesión de: Nombre Apellido · plugin 1.23.0
```

`Tema` dice en qué se trabajó, en una línea: es la cabecera pública de la entrada (contrato, sección 7). «Escribió:» lista los documentos de `entregables/` y `taller/` que la sesión creó o cambió en su contenido, y «Publicó:» los que pasó a `vigente` (skill `revisar`), con su ruta dentro del proyecto y separados por comas; cada línea, solo si trae algo. Las escribe `cerrar.py` desde lo que la sesión le dice, y nadie las teclea: el tablero cuenta cada documento como escrito para quien lo escribió y como publicado para quien lo publicó, aunque sean dos personas. Las entradas anteriores a la 1.23 no las llevan y se quedan así: lo que escribieron o publicaron no se atribuye a nadie. Publicado es solo lo que una entrada dice en «Publicó:»; un entregable vigente que cambió sin que ninguna entrada lo nombre se cuenta aparte, sin suponer quién. La última línea dice quién trabajó y con qué versión del plugin. Es del cuerpo, como «Avances», y no sale fuera del área. Lo que sigue no va en la entrada: lo dice «Siguiente» del `Estatus`, que el mismo cierre reescribe. Las entradas anteriores a la 1.16 no llevan «Sesión de:»; se quedan así. Una sesión sin consola (`sin-consola.md`) termina la línea con « · sin consola».

Entradas nuevas arriba. Una tarea programada que escribe en la carpeta deja su entrada como `## AAAA-MM-DD (tarea)`, y la migración de estructura de la 1.22, como `## AAAA-MM-DD (migracion)`: cuentan lo que hicieron, pero no son sesiones, y el tablero no las cuenta como tales.

### Regla de histórico

Las entradas escritas antes de adoptar este formato se dejan tal cual; el formato aplica desde la siguiente entrada. La excepción es la migración: un registro que se acaba de crear al migrar sí se convierte, porque nadie lo ha consumido todavía.

### Aviso entre áreas

La carpeta no notifica a nadie. Por eso `Afecta a` puede nombrar proyectos de otras áreas: al abrir sesión se buscan, en los `decisiones.md` de la raíz, las líneas `Afecta a:` y `Cuestiona a:` que nombren el proyecto activo o su área entera (`area/`) (y, en la sesión del responsable de contexto, las que nombren una premisa), y las `Responde a:`, que dicen qué cuestionamiento ya está cerrado y avisan a quien lo planteó, en su proyecto, de que le respondieron. Es una búsqueda de un patrón de línea, no una lectura de archivos, y es la única operación que recorre la raíz entera al abrir. Al cerrar sesión, si una decisión afecta a otra área, se recuerda al usuario que avise a su responsable.

## 5. Cabecera

Todo `.md` empieza con una cabecera de estas claves y ninguna más, con dos excepciones: `guia.md` y `metodo.md`, que están hechos para leerse sin nada delante y empiezan directamente por el título, y el contenido de `fuentes/`, que es material y no se edita, así que añadirle una cabecera sería editarlo. El `inventario.md` de `fuentes/` sí la lleva, porque ese lo escribimos nosotros.

```yaml
---
estado: vigente
actualizado: 2026-08-29
aportacion: "El tope de 5.000 MXN deja fuera las compras recurrentes."
basado_en:
  - base/contexto.md
  - compras/automatizacion-ordenes/fuentes/entrevista-ana.md
---
```

Inmediatamente después va el título en `#`, para que quien abra el archivo sin renderizador vea de qué trata en la primera línea legible.

| Archivo | `estado` | `actualizado` | `aportacion` y `basado_en` |
|---|---|---|---|
| `entregables/` y `taller/` | sí (en el taller, casi siempre `borrador`) | sí | sí, obligatorias las dos |
| `proyecto.md`, `base/` | sí | sí | no |
| `area.md`, `decisiones.md`, `sesiones.md`, `base/premisas.md`, los `inventario.md` | `vigente` siempre | sí | no |

`area.md` y los registros llevan `vigente` desde que se crean y no lo cambian: son índice y registro, no algo que se publique. Lo que pasa de `borrador` a `vigente` es lo demás.

**estado**, tres valores y nada más:

- `borrador`: no se puede consumir todavía. Da igual si está a medias, terminado esperando al responsable, o adoptado de otro sitio sin revisar
- `vigente`: aprobado, se puede construir encima
- `reemplazado`: superado. Requiere una clave más, `reemplazado_por`, con la ruta del sustituto

El paso a `vigente` lo pide siempre el responsable del proyecto de forma explícita y tiene requisitos: los aplica la skill `revisar`. Ninguna otra skill cambia ese estado por su cuenta. Que un borrador esté a medias o terminado se dice en el `Estatus` de `proyecto.md`.

**actualizado**: fecha en formato `AAAA-MM-DD`, la del último cambio de contenido real, en la zona horaria de la organización (sección 4).

**aportacion**: una línea que dice qué aporta la pieza a lo que el proyecto sabía, no de qué trata: «El tope de 5.000 MXN deja fuera las compras recurrentes», no «Análisis de compras». Vale para cualquier pieza: un análisis dice su conclusión, una guía lo que permite hacer, una plantilla para qué sirve. Es lo que deja ver, sin abrir el documento, qué hay en un proyecto y si sigue valiendo, y es la línea del entregable vigente en el bloque `Proyectos` de `area.md` (sección 2). Una sola línea de hasta unos 200 caracteres, sin saltos, entre comillas si lleva dos puntos. La escribe la skill, como `basado_en`; el barrido del tablero propone una línea para cada archivo que no la tiene, y quien escribe en el proyecto acepta las que valen, en su sesión o de golpe desde su tablero. La leen todos los que leen el área, en el tablero, aunque el cuerpo del taller sea privado, así que lleva la regla del `Estatus`: nada de `restringido/` ni datos personales. Añadir o cambiar `aportacion` sin tocar el contenido no mueve `actualizado`: esa fecha es la del último cambio de contenido, y moverla escondería lo que quedó viejo frente a una decisión o frente a su base.

**basado_en**: rutas relativas a la raíz de todo lo que se usó para escribir el archivo. Es lo que permite detectar que una pieza quedó desactualizada cuando cambia algo aguas arriba. La escribe la skill, no la persona. Si no se usó más que la conversación, o el material se adoptó sin trazabilidad, va la lista vacía `[]`; `revisar` la pide completa antes de publicar un entregable adoptado.

Las dos claves son obligatorias en lo que se crea en `entregables/` y `taller/`; en lo que ya existía sin ellas, `verificar.sh` las cuenta y el barrido propone la `aportacion`. Ningún otro archivo las lleva: ni los registros, ni `area.md`, ni `proyecto.md`, ni `base/`, ni `fuentes/`.

No hay clave de responsable. El responsable vive en `area.md` y en `proyecto.md`, en `Quién participa`. Si un documento concreto tiene otro responsable, lo dice la primera línea de su cuerpo.

Las claves van sin acentos ni eñes.

## 8. Rotación

Cuando `sesiones.md` o `decisiones.md` pasa de unas 1.500 líneas o de 100 KB, o su entrada más nueva es de un año anterior, se archiva entero en la misma carpeta con el año de su entrada más nueva en el nombre (`decisiones-2026.md`; si en un mismo año hace falta otro, `decisiones-2026-2.md`) y se abre uno nuevo con su cabecera, su título y una línea «Archivado:» con los archivados que tiene, para quien lo abra sin el plugin. El tamaño cuenta porque las entradas largas llenan un registro mucho antes de llegar a las líneas (1.23), y un registro grande es lo que más cuesta leer al abrir y al poner al día el tablero. Es la única excepción a los nombres sin fechas: el año es lo que distingue el registro archivado del vivo. Lo hace `cerrar.py` antes de escribir la entrada de hoy, sin preguntar.

Archivar no esconde nada: la apertura, el tablero y su barrido leen, junto al registro vivo, sus archivados de este año y del anterior, como si no se hubieran archivado. Una decisión archivada sigue avisando a quien nombra en `Afecta a`, un cuestionamiento sigue esperando respuesta y cada entrada conserva su identificador (`area/proyecto#AAAA-MM-DD-n`), que lleva el año y dice en qué archivado buscarla. Los de años anteriores no se leen enteros: lo que sostiene una decisión vieja ya está en `Alcance` o en el `Estatus`, y quien la cita la busca por su año. De ellos solo se buscan las líneas «Responde a:», que cierran cuestionamientos sin importar cuándo se respondieron. Un archivado no se edita, como el registro del que salió.

## 10. Prohibiciones

Valen para todas las skills y no se repiten en ninguna. Cada skill añade las suyas, que son las de su trabajo concreto.

1. No marcar nada como `vigente`. Solo lo hace `revisar`, y solo cuando lo pide el responsable del proyecto; y `migrar`, con lo que su responsable en el origen pide publicar al migrar. `area.md` y los registros nacen `vigente` (sección 5).
2. No editar una entrada ya escrita de `decisiones.md` o de `sesiones.md`, ni para corregir una errata. Un registro solo crece.
3. No registrar una decisión que el usuario no confirmó en esta sesión, salvo las recuperadas al migrar, que entran marcadas «pendiente de confirmar» (sección 4).
4. No escribir en `guia.md`, en `base/`, en `metodo.md` ni en la carpeta de un área de la que la cuenta no es responsable ni colabora. Desde la sesión de otra área se prepara el texto y se le pasa a quien responde. Las excepciones: la sesión del responsable de contexto escribe `guia.md` y `base/`, `metodo.md` lo pone al día cualquier cuenta con el plugin más nuevo (sección 11), y la migración de estructura del responsable de contexto, que administra la carpeta, renombra también las áreas de otros responsables, restringidas incluidas: lo hace el script y nada de lo que lee sale de su área (skill `sesion`).
5. No tocar archivos fuera del proyecto activo, salvo la línea de ese proyecto y las de sus entregables vigentes en el bloque `Proyectos` de su `area.md`, el `Estatus` de ese `area.md` al cerrar sesión o cuando su responsable lo pide (skill `director`), lo mecánico que la puesta al día del tablero escribe en los proyectos donde la cuenta es responsable o colabora: fechas de pasos y hechos marcados desde el tablero (skill `tablero`), nunca en los de otra cuenta, y lo que renombra la migración de estructura de la 1.22 (prohibición 4). El `Estatus` del área es solo de su responsable.
6. No leer el cuerpo de `taller/`, `fuentes/`, lo restringido de otra área, ni el cuerpo de su `sesiones.md`: de la bitácora ajena solo la fecha, el título y «Tema» de cada entrada; del taller ajeno solo la cabecera y el título de cada archivo, su inventario (sección 7). Son taller privado y no responden a nadie de fuera.
7. No escribir en un archivo que lee todo el equipo la ruta ni el contenido de algo restringido, aunque sea resumido. Hacia fuera solo van el nombre del área o del proyecto, que ya están listados, y la fila de `inventario.md`.
8. No guardar en `fuentes/` un material con indicios de información confidencial sin haberlo dicho y preguntado antes, ni mover nada a `restringido/` sin que el usuario lo confirme.
9. No guardar fuera de `fuentes/` material que llegó de fuera del equipo del proyecto, aunque venga terminado y listo para usarse.
10. No copiar a este `fuentes/` una fuente que ya existe en otro proyecto del área. Se cita la original por su ruta.
11. No crear un área ni un proyecto sin responsable con nombre y apellido.
12. No rellenar un hueco con una suposición razonable. Un hueco se marca como hueco, y "no consta" es una respuesta válida.
13. No escribir una cifra sin fecha ni fuente.
14. No poner número de fase, fecha ni versión del propio archivo en el nombre de un archivo o de una carpeta. Las excepciones: el registro archivado por año (sección 8) y un número que identifica el asunto, cuando cada archivo es un documento distinto y no una versión del mismo (contrato, sección 6).
15. No crear carpetas que la estructura no contempla, ni un `AGENTS.md` u otro archivo de instrucciones para la IA, ni un índice a mano, ni una carpeta de borradores, ni escribir rutas absolutas en ningún archivo.
16. No dejar dentro de la raíz el almacén de datos de una aplicación, ni apuntar una aplicación a que escriba ahí.
17. No borrar un entregable superado. Pasa a `reemplazado` con `reemplazado_por`, porque alguien puede tenerlo citado.
18. No llevar a la raíz de una organización ningún hecho que venga de otra raíz, ni siquiera para comparar, salvo por un traspaso que la persona pidió y confirmó pieza a pieza (sección 1, «Independencia entre raíces»).
19. No guardar estado del método en la memoria del modelo ni en la memoria de proyecto de Claude. Si un dato importa, va a un `.md` de la carpeta.
20. No dejar en `entregables/` lo que no puede salir del proyecto. Si no se lo puedo dar a nadie de fuera, va a `taller/`.
21. No abrir un `decisiones.md` ni un `sesiones.md` dentro de `taller/`. Los registros del proyecto son los de su raíz.
22. No dejar dentro de la raíz un script, una salida ni un archivo temporal, ni trabajar en `/tmp` de la consola de la computadora, que comparten todas las conversaciones: lo de paso va en `$HOME` de la consola, que es de esta conversación, fuera de `mnt/` (lo que hay ahí son carpetas de la persona, y `mnt/outputs` puede ser «Claude outputs» de la raíz), o en el contenedor, y nunca se corre un archivo que no escribió esta conversación.
23. No guardar en la carpeta un `.html` sin `<meta charset="utf-8">` en su `<head>`. Abierto desde la carpeta, el navegador no tiene quien le diga la codificación y los acentos salen rotos («Ã©»); publicado como artefacto se ve bien, y por eso el fallo pasa inadvertido hasta que alguien abre el archivo.
