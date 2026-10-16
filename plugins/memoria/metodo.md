# Método de trabajo · versión 1.14.5 · huella f8f19e3 · generado desde el plugin memoria, no se edita a mano

Este archivo reúne el contrato del método, las normas de estilo y el índice de skills del plugin `memoria`. Sirve a quien trabaja con Gemini u otro modelo sin el plugin, y a quien abre la carpeta sin IA delante. Para ponerlo al día se vuelve a generar desde el plugin y se copia a la raíz.

---

# Convenciones

Contrato base del método. El resto de skills del plugin lo cargan antes de escribir nada. Si una skill contradice algo de aquí, manda este documento. Dos anexos, junto a este archivo, se leen solo cuando hacen falta: `raices.md` (varias raíces, traspasos, registro de una migración) y `montaje.md` (montaje, publicación, bloque de instrucciones, programadores).

Versión del método: **1.14**

## 1. Las tres capas de propiedad

| Capa | Quién responde | Qué contiene |
|---|---|---|
| El plugin y `metodo.md` | Solo el responsable del método | Cómo se trabaja. Idéntico en todas las organizaciones |
| `guia.md` y `base/` | Un único responsable de contexto | Quién es la organización, cómo se organiza, qué sistemas usa, qué reglas propias tiene |
| Cada área | El dueño del área | El trabajo real |

Nadie responde fuera de su capa, y nadie pide que se escriba en la capa de otro. Un área lee `base/` y `metodo.md`, nunca los modifica. Las skills escriben en nombre de quien las usa y respetan las mismas capas. Una capa no cambia porque algo esté restringido: el dueño de un área lo es también de lo restringido dentro de ella.

### Quién teclea, y por dónde entra lo de fuera

Responder por un archivo y escribirlo son dos cosas distintas. **Lo que hay en una carpeta de trabajo lo escribe la IA en sesión**: `guia.md`, `base/`, los `area.md` y los `proyecto.md`, los registros y los entregables. Las personas deciden qué dice cada archivo y lo piden, la IA es la que teclea. `metodo.md` no es excepción: lo genera un script disparado desde una sesión.

De ahí sale el valor de la carpeta: todo lo que hay dentro entró por el método y alguien respondió por ello. En cuanto entra material que nadie puso a propósito, un almacén que una aplicación escribe sola, un archivo copiado a mano o un índice mantenido aparte, la carpeta deja de ser fiable y la IA lee ruido como si fuera contexto.

**La única puerta para el material que llega de fuera es `fuentes/`**, la del proyecto al que pertenece. De fuera es lo que no produjo el equipo del proyecto: un export, un PDF de un tercero, una transcripción, un documento que mandó un cliente. Entra a `fuentes/`, no se edita, y lo que se construya con él se escribe aparte y lo cita.

Los formatos que la IA no puede teclear, una presentación o una hoja de cálculo, son la excepción a quién escribe y no a por dónde se entra: los arma el equipo del proyecto con su herramienta y son producto suyo; si vinieron de fuera entran por `fuentes/` como cualquier otro material. La sección 3 lo detalla.

**Lo que se produce para un proyecto se guarda en su carpeta en cuanto existe**, no al cerrar la sesión: un documento, un PDF, una propuesta o un análisis van a `entregables/`, o a `taller/` si no salen del proyecto, con `estado: borrador`, aunque falte pulirlos, y aunque los haya hecho otra herramienta y no la skill `entregable`. Lo que solo vive en la conversación se pierde con ella y nadie más lo ve. Cerrar la sesión es registrar lo que pasó, no guardar lo que se hizo. Por la misma razón, una tarea programada que escribe en la carpeta algo más que fechas de pasos deja su línea en el `sesiones.md` del proyecto, con «(tarea)» en el título: si no, su trabajo parece una sesión que nadie cerró.

**«Claude outputs» no es parte de la memoria.** Es la carpeta donde la app de Claude guarda por su cuenta lo que produce cuando trabaja sobre una carpeta conectada. Lo que hay ahí no tiene proyecto, nadie lo encuentra y el tablero no lo ve como trabajo de nadie. Lo que se haga para un proyecto se guarda directamente en ese proyecto; si la app lo dejó en «Claude outputs», se mueve a su proyecto en cuanto existe. La sesión que lo produjo lo recoge al cerrar, y lo que se haya acumulado se ordena con la frase «ordena Claude outputs» (skill `donde-va`). `verificar.sh` y el tablero cuentan los archivos que siguen ahí.

Ninguna carpeta de trabajo aloja el almacén de datos de una aplicación. Lo escribe la aplicación sola, crece por su cuenta y nadie responde por lo que hay dentro.

La migración es la excepción declarada. El material que se adopta al migrar no llega de fuera: es el trabajo anterior de la propia organización, y entra donde le toque con `estado: borrador` y con la trazabilidad que se pueda reconstruir, salvo lo que su dueño en el origen pida publicar al migrar. Lo que en el origen ya era material de entrada entra por `fuentes/` como en cualquier proyecto. Lo detalla la skill `migrar`.

Es norma, no candado. Nada impide abrir un archivo y editarlo a mano, y a veces hay que hacerlo; detectar lo que entró por otro camino es trabajo de la skill `revisar`. La propiedad no cambia: quien responde por un archivo sigue siendo su dueño, lo que cambia es la mano que escribe.

La raíz es la carpeta que contiene `guia.md`, `metodo.md` y `base/`. Ninguna instrucción del método usa rutas absolutas, porque cada usuario tiene la carpeta sincronizada en un sitio distinto.

**La carpeta se lee y se escribe por su copia en la computadora**, con las herramientas de la carpeta conectada, y nunca por un conector de Google Drive u otro servicio en la nube, ni para buscar ni para escribir, aunque esté conectado. Por el conector no se ven la estructura, las cabeceras ni las fechas de los archivos, y lo que se escribe por ahí puede acabar en otro formato o fuera de su sitio. Si la carpeta no aparece entre las conectadas, se pide añadirla. **La única excepción es leer sin carpeta:** una sesión que no tiene ninguna carpeta conectada, como una desde el teléfono o la web, puede leer una raíz que vive en Google Drive por el conector de Drive, por niveles como siempre, y no escribe nada en ella; lo que salga de esa sesión se guarda como nota en la cola del tablero de la persona y lo registra la siguiente sesión con la carpeta (skill `sesion`, «Sin carpeta: solo lectura»). Con la carpeta conectada, el conector no se usa nunca para la memoria. El conector sirve además para lo que no es la memoria, como un documento que alguien comparte, y si eso entra a la memoria lo hace por `fuentes/`.

### Quién es el dueño

**El dueño por defecto de un área o de un proyecto nuevo es la persona desde cuya cuenta se abre la sesión.** Se propone su nombre al crear y solo se pregunta si en ese momento se asigna a otra persona. Un área o un proyecto sin dueño con nombre y apellido no se crea.

La cuenta de cada dueño queda escrita junto a su nombre en `guia.md`. Eso es lo que permite comprobar, y no solo suponer, que quien pide publicar es el dueño del proyecto. Si la identidad de la cuenta no está disponible, por ejemplo con otro modelo leyendo `metodo.md`, se pregunta el nombre y se anota de quién viene la petición.

### Independencia entre raíces

Se trabaja en una raíz a la vez: con más de una conectada, antes de leer o escribir se pregunta en cuál, cada escritura dice en qué raíz se hace y cambiar de raíz se anuncia. Nada que se escriba en una raíz usa hechos de otra, ni del repo del plugin, salvo por un traspaso que la persona pide y confirma pieza a pieza; y el repo del plugin no guarda hechos de ninguna organización. Cómo es un traspaso y dónde vive el registro de una migración lo dice `raices.md`, junto a este archivo, que se lee con más de una raíz conectada, cuando se pide un traspaso y al migrar.

### Permisos en la carpeta compartida

Valen para cualquier sistema de carpetas (Drive, OneDrive, iCloud…); el ejemplo de siempre es Drive, donde el acceso limitado se pone desde la web.

- Lectura de toda la raíz para todo el equipo, salvo lo restringido.
- Escritura en la carpeta de un área solo para su dueño y las personas que él designe.
- Escritura en `guia.md` y en `base/` solo para el responsable de contexto. La IA escribe los dos, y solo puede hacerlo en la sesión de esa persona; desde la sesión de otra área prepara el texto y se lo pasa.
- Administrar la carpeta compartida es del dueño de la organización, o de una persona de su total confianza, y de nadie más. Quien administra puede quitar cualquier restricción, así que todo lo que sigue se apoya en esa lista.

### Lo restringido

Lo que no puede leer todo el equipo se marca en la carpeta que lo contiene, ahí donde ya está, con el acceso limitado de Drive: esa carpeta deja de heredar los permisos de arriba y solo entra quien esté añadido a ella. No hay carpeta compartida aparte, ni espejos, ni rutas alternativas. Una organización tiene una sola carpeta compartida.

Se restringe en tres sitios y en ninguno más:

| Qué | Dónde se marca |
|---|---|
| Un área entera | La carpeta del área |
| Un proyecto entero, dentro de un área que sí lee todo el equipo | La carpeta del proyecto |
| Parte de un proyecto | `<proyecto>/restringido/` |

Lo que decide dónde va cada cosa es quién puede leerla, no de qué trata: da igual que sea una cuenta de cliente, recursos humanos, finanzas o legal.

**Un proyecto no se parte.** Sigue siendo uno, con un dueño, un `proyecto.md`, un `decisiones.md` y un `sesiones.md`. Lo que no puede leer todo el equipo va a `restringido/`, **una carpeta plana** con su propio `enlaces.md`. No repite dentro las carpetas del proyecto. Si hace falta saber si uno de ellos es un entregable o material de taller, lo dice su fila en ese `enlaces.md`.

En el `fuentes/enlaces.md` público queda la fila que dice que ese material existe y dónde está, nunca lo que dice. Sin ella nadie sabe que hay algo ni a quién pedirlo, que es lo mismo que busca el método al dejar visible el nombre de una carpeta restringida.

**Dónde escala.** En `restringido/` no entran nunca `proyecto.md`, `decisiones.md` ni `sesiones.md`. Si lo que hay que esconder es una decisión, el estado o el objetivo, el proyecto no se puede partir: se restringe entero.

**El nombre se ve.** Quien no tiene acceso ve la carpeta en gris, con su nombre, y un botón para solicitarlo que llega a quien administra. Por eso la carpeta de dentro de un proyecto se llama siempre `restringido` y no dice de qué trata. Las áreas y los proyectos se siguen listando en `guia.md` y en `area.md` con su nombre y su dueño, estén restringidos o no: el equipo tiene que poder saber que existen y a quién pedir acceso; lo que no puede es leerlos. Y lo dicen: un área restringida lleva «Restringida» al inicio de su columna «Quién la lee» en `guia.md`, y un proyecto restringido empieza su línea del bloque `Proyectos` de su `area.md` por esa palabra: `` - `slug/` — restringido: … ``. Decir en la línea que una parte del proyecto está en `restringido/` no lo declara restringido. Es lo único que deja ver que algo está restringido a quien sí puede leerlo, por ejemplo a la herramienta que genera un tablero con la cuenta de quien administra la carpeta.

Si una organización necesita que ni el nombre de un área se vea, o que quien administra la carpeta compartida no pueda ver algo, ese caso se resuelve con una carpeta compartida aparte y se escribe en las reglas propias de `guia.md`.

Poner y quitar el acceso limitado solo lo puede hacer quien administra la carpeta compartida, desde la web y de una carpeta en una. Ninguna skill lo hace: dicen qué carpeta hay que limitar y para quién, y esperan.

### Material sensible dentro de un proyecto que lee todo el equipo

Un archivo con datos personales, facturación, contratos o credenciales no se guarda en `fuentes/`: se guarda en `restringido/` del mismo proyecto, y en el `fuentes/enlaces.md` público queda una fila con qué es, dónde está y qué tener presente al usarlo. No obliga a restringir el proyecto entero.

La IA participa en esa decisión. Cuando una skill detecta indicios de información sensible en un material (nombres junto a RFC, CURP o NSS, facturación por cliente, contratos, contraseñas, datos de salud, salarios), lo dice y propone llevarlo a `restringido/`. El usuario decide si lo es o no. Nada se mueve sin que el usuario lo confirme.

Ese material se lee igual que `fuentes/`: es privado del proyecto y no se cita en `basado_en` salvo por su fila de `enlaces.md`.

## 2. Estructura

```
RAIZ/
  guia.md
  metodo.md
  base/
    contexto.md
    glosario.md
    sistemas.md
    premisas.md       (opcional: las premisas que confirmó la dirección)
  <area>/
    area.md
    <proyecto>/
      proyecto.md
      decisiones.md
      sesiones.md
      entregables/
      taller/
      fuentes/
        enlaces.md      (opcional)
      restringido/      (opcional: lo que no puede leer todo el equipo)
        enlaces.md
```

Tres niveles: área, proyecto, carpeta del proyecto. Un cuarto nivel significa que ahí había dos proyectos, con una excepción: dentro de `entregables/`, `taller/` y `fuentes/` se permite **un** nivel de agrupación cuando hay material suficiente para que la lista deje de leerse; el nombre de la subcarpeta sigue la convención de nombres y no lleva número de fase. Antes de crearla vale la pena probar con el asunto por delante del nombre del archivo, que agrupa igual en el listado y no añade nivel. `restringido/` no admite ninguno: es plano.

`guia.md` es de la organización y solo de ella: qué es la carpeta, qué áreas hay con su dueño y su cuenta, quién responde por el contexto, quién administra la carpeta compartida, las reglas propias de la casa y la receta para conectarse. Su título es «<Organización> · esta carpeta», y **el nombre de la organización**, el que usan el aviso de arranque y el tablero, es lo que va antes del «·». Nada de lo que es igual en cualquier organización entra ahí: eso vive en `metodo.md`, que genera el plugin y nadie edita, y que lleva este contrato, el estilo y el índice de skills para que funcionen también con otro modelo o con quien abra la carpeta sin el plugin.

### Los archivos de `base/`

| Archivo | Qué contiene |
|---|---|
| `contexto.md` | Quién es la organización, criterios transversales, qué datos son sensibles |
| `glosario.md` | Vocabulario de la casa: siglas, nombres internos, qué significa cada cosa |
| `sistemas.md` | Una tabla con cuatro columnas: sistema, para qué, quién da acceso, antes de usarlo |
| `premisas.md` | Las premisas que la dirección dio por confirmadas: sobre qué apuesta la organización y qué no está en discusión ahora. Solo existe si hay alguna |

Los tres primeros se leen a demanda, no al abrir sesión: `glosario.md` cuando aparece vocabulario de la casa, `sistemas.md` cuando el trabajo toca un sistema, `contexto.md` cuando la pregunta es sobre la organización. `premisas.md` se lee siempre al abrir, porque todo el trabajo se ancla en ella. La sección 12 lo fija.

### Las premisas

Una premisa es algo que la dirección confirmó y sobre lo que todos construyen: «este año vendemos solo en México», «el producto se construye en inglés». Las decide quien dirige la organización, las escribe el responsable de contexto en su sesión («registra como premisa que…», skill `sesion`), y viven en `base/premisas.md`, que es un registro: se añaden líneas y las que hay no se editan.

```markdown
## Premisas

- P1 · Este año se vende solo en México · Confirmó: Nombre Apellido · 2026-10-15
- P2 · El producto se construye en inglés · Confirmó: Nombre Apellido · 2026-10-11
- P3 · Se vende en México y en Estados Unidos · Confirmó: Nombre Apellido · 2027-01-10 · Reemplaza a P1
```

El identificador `P<n>` es correlativo y no se reutiliza. Una premisa que cambia no se corrige: se añade otra con `Reemplaza a P<n>`, y la anterior queda como historia. Una premisa se cita como `premisa P<n>` desde una decisión, un entregable o un cuestionamiento (sección 4).

Las reglas propias de una organización no llevan archivo: van en `guia.md`, que es donde vive todo lo suyo. Son las que este contrato no puede prever, como un tipo de dato adicional que cuenta como confidencial, una convención de nombres para las áreas o vocabulario que conviene fijar antes de que cada quien lo escriba distinto. No pueden cambiar ni contradecir nada de lo que dice este documento; si alguna lo hace, manda este documento y se avisa al responsable de contexto.

Las dos plantillas del método, brief y comparativo, viven en el plugin, dentro de la skill `nuevo`. No se copian a la raíz.

### Estructura de `area.md`

Fija, porque varias skills leen y escriben en ella:

```markdown
# [Nombre del área]

## Qué es
[Dos o tres líneas]

## Prioridades ahora
[Tres a cinco líneas. Las pide el dueño, las escriben las skills]

## Proyectos
- `nombre-del-proyecto/` — qué es
  - nombre-del-entregable — qué es · actualizado AAAA-MM-DD

## Panorama
AAAA-MM-DD · [Tres a cinco líneas del director del área: cómo está, qué se movió, qué preocupa]

## Quién participa
Dueño: [nombre y apellido]
[Otras personas y su papel]
```

`Panorama` es el resumen ejecutivo del área, con la fecha en que se escribió. Lo escribe la skill `director` al cerrar una sesión en esa área, o cuando su dueño pide «actualiza el panorama»; se reescribe entero cada vez y no lleva historia: lo que pasó está en los registros de los proyectos. Si no existe, el área todavía no tiene resumen; no se escribe a mano.

El bloque `Proyectos` es el índice de contexto del área: una línea por proyecto y, debajo, una línea por cada entregable `vigente`. Un proyecto cerrado ocupa solo su línea, sin desglose. Lo escriben el cierre de sesión y la creación de proyectos, no una persona, y `verificar.sh` avisa si falta algún proyecto o algún entregable vigente. No lo regenera ninguna herramienta: las descripciones de esas líneas son lo que hace útil el índice, y una lista rehecha desde los nombres de archivo dice menos que la que había. Es lo primero que lee cualquier skill antes de abrir un archivo del área.

`Quién participa` es donde vive el dueño del área. No hay otra clave para él.

## 3. Los archivos de un proyecto

| Archivo | Tipo | Qué contiene |
|---|---|---|
| `proyecto.md` | Vivo | Objetivo, alcance, quién participa, estado actual, siguientes pasos |
| `decisiones.md` | Registro | Qué se decidió, cuándo, por qué, qué se descartó y a qué afecta |
| `sesiones.md` | Registro | Qué se avanzó cada día y qué quedó pendiente |
| `entregables/` | Vivo | El producto del proyecto, en cualquier estado |
| `taller/` | Vivo | Lo que el equipo escribe para llegar al producto y no es el producto |
| `fuentes/` | Inmutable | Insumos crudos: exports, PDFs, transcripciones, material sin clasificar |
| `fuentes/enlaces.md` | Registro | Tabla de enlaces externos y de lo que está en `restringido/`: se le añaden filas, las que hay no se editan. Solo existe si hay filas |

Los tres archivos de la raíz del proyecto y las tres carpetas existen siempre, aunque estén vacías. `sesiones.md` es obligatorio y lo escribe la skill de cierre de sesión, no el usuario.

### Qué separa un entregable del taller

Un proyecto produce dos cosas y solo una sale. La prueba para saber cuál es cada archivo cabe en una pregunta: **¿se lo puedo dar a alguien de fuera del proyecto?** Si la respuesta es sí, es un entregable. Si es no, es taller.

`entregables/` es lo que otra área puede consumir cuando esté vigente. `taller/` es todo lo demás que escribió el equipo para llegar hasta ahí: el inventario que hubo que levantar, las notas de una conversación, el análisis intermedio, el diagnóstico del que sale una propuesta, el encuadre de un trabajo que se absorbió. Es de la casa, se escribió en sesión y nadie lo va a leer fuera del proyecto.

La secuencia las ordena sin que haya que pensarlo: **`fuentes/` es lo que entra, `taller/` es donde se trabaja, `entregables/` es lo que sale.**

El taller no lleva estado propio ni carpeta de borradores: sus archivos llevan la misma cabecera que cualquier otro, casi siempre en `borrador`.

En el taller **no se abren registros**. Las decisiones y las sesiones del proyecto, incluidas las que ocurren trabajando ahí dentro, van a `decisiones.md` y a `sesiones.md`, que son del proyecto entero. Lo único con forma de registro que puede vivir en el taller es material adoptado de otro sitio, congelado, al que no se le añaden entradas.

No hay carpeta de borradores. Un entregable a medias vive en `entregables/` con `estado: borrador`, y lo que todavía no es nada vive en la conversación hasta que merezca ser un archivo.

No hay carpeta aparte para binarios. Una presentación hecha directo en PowerPoint o Keynote, una hoja de cálculo hecha en Excel o Numbers, un PDF que nadie generó desde texto: lo que decide dónde va es quién lo produjo. Si lo hizo el equipo del proyecto, con las manos que sea, es producto suyo y va a `entregables/` con nombre en minúsculas y guiones, igual que cualquier otro entregable. Si vino de fuera, entra por `fuentes/` aunque el proyecto lo vaya a usar tal cual, y entonces el entregable es el documento que lo cita. No lleva cabecera propia porque el formato no la admite; su estado y de qué se construyó se anotan en `proyecto.md` o en la entrada de `decisiones.md` que lo produjo. El lugar donde vive la raíz de la organización ya previsualiza estos formatos, así que no hace falta sacarlos de la estructura para poder verlos.

### Estructura de `proyecto.md`

Fija, porque varias skills escriben en ella:

```markdown
# [Nombre del proyecto]

## En corto
AAAA-MM-DD · **[Lo último que se completó, y lo que sigue y cuándo.]**
- **Se completó:** [lo terminado desde el estatus anterior, con su fecha, y para qué sirve ya]
- **Siguiente:** [hasta tres pasos, cada uno con quién y para cuándo]
- **Falta decidir:** [qué, y quién lo decide]
- **Preocupa:** [lo que puede salir mal]

## Objetivo
[Una frase. Qué problema resuelve y para quién.]

## Terminado significa
[Cómo sabremos que se acabó. Concreto y comprobable.]

## Alcance
Sí: [lo que entra]
No: [lo que queda fuera]

## Quién participa
Dueño: [nombre] ([área])
Consumen esto: [áreas o personas]

## Estado actual
[Dos o tres líneas]

## Siguientes pasos
- [Lista corta]
```

`En corto`, `Estado actual` y `Siguientes pasos` son las tres únicas secciones que reescribe el cierre de sesión. El resto cambia poco y solo a petición del dueño.

`En corto` es el estatus para quien no va a leer más: lo primero que ve el tablero y lo que responde Claude cuando alguien pregunta cómo va. Lo escribe el cierre de sesión con la voz del director (skill `director`) y se sustituye entero cada vez. Es el reporte de un director: lo que completamos y lo que sigue. Cinco líneas como mucho. La primera empieza por la fecha en que se escribe, como el `Panorama` del área, y sigue con la frase en negrita: lo último que se completó y lo próximo que pasa y cuándo, en lenguaje de persona, no de archivo. «Se completó» y «Siguiente» van siempre (si en la sesión no se completó nada, «Se completó» dice lo último terminado y cuándo; al arrancar un proyecto, solo «Siguiente»); «Falta decidir» y «Preocupa», solo si tienen algo. Cada línea, de una o dos frases, con nombres de personas y fechas absolutas («el 19 de octubre», nunca «el lunes»), sin rutas ni identificadores. Lo que no aplica se omite: no se escribe «nada». Lo lee todo el equipo, también en el tablero que se comparte: no lleva nada de `restringido/` ni datos personales, ni en «Preocupa». `Estado actual` sigue siendo el detalle, para quien trabaja en el proyecto. Un proyecto sin `En corto` (anterior a la 1.14.4) sigue siendo válido: lo escribe su siguiente cierre.

`Dueño`, en `Quién participa`, es el dueño de todo el proyecto: sus entregables, sus decisiones, quién pide publicar. Si un documento concreto tiene otro responsable, se dice en la primera línea del cuerpo de ese documento, no en la cabecera.

### Un proyecto cerrado

Cuando se cumple lo que decía `Terminado significa`, el dueño lo pide y `Estado actual` abre diciendo **«Proyecto terminado el AAAA-MM-DD»**; `En corto` queda en una línea, la frase en negrita, que dice cómo acabó. A partir de ahí el proyecto no evoluciona: sus archivos siguen donde están, con el estado que tengan, y su `Siguientes pasos` dice que no queda ninguno propio.

Lo que cambia es el índice. En el bloque `Proyectos` de su `area.md` **un proyecto cerrado ocupa una línea y no desglosa sus entregables**. Quien necesite el detalle abre su `proyecto.md`, que sigue contándolo entero.

Un proyecto cerrado no se borra ni se saca de la raíz. Se sigue citando, sus entregables vigentes se siguen consumiendo y su `decisiones.md` sigue explicando por qué las cosas están como están.

### Los nombres reservados solo existen en su sitio

`proyecto.md`, `decisiones.md`, `sesiones.md` y `area.md` solo existen donde el método los pone. Todo lo que se adopte y los traiga se renombra a lo que de verdad es, porque un archivo llamado `proyecto.md` promete estar vivo y un `decisiones.md` promete ser un registro que solo crece y que nadie edita, y fuera de su sitio ninguna de las dos cosas es cierta.

El caso que más lo pide es un proyecto que se pliega dentro de otro, cuando dos trabajos dejan de ser distintos y pasan a ser el mismo. Su encuadre entra al `taller/` como un documento más. Sus registros **se funden** con los del proyecto que recibe, o entre sí si se absorben varios a la vez, copiando las entradas tal cual y añadiendo a cada encabezado de qué venían; ninguna se edita. Lo que no se hace nunca es dejar cinco bitácoras conviviendo dentro de una carpeta: nadie las abre y compiten con el registro vivo. El resto de su material se coloca por las reglas de siempre, y lo absorbido conserva su contenido y sus fechas: lo que se pierde es su maquinaria, y esa es la intención.

### Estructura de `fuentes/enlaces.md`

```markdown
| Qué es | Enlace | Qué tener presente |
|---|---|---|
| Documentación del ERP | https://… | Versión 2024, puede estar desfasada |
| Nómina del equipo, 2026 | `restringido/nomina-2026.xlsx` | Solo el total agregado sale a un entregable |
```

## 4. Vivo o registro, nunca las dos cosas

**Un archivo vivo se reescribe** y siempre refleja el presente. Nadie necesita leer su historia para entenderlo.

**Un registro solo crece.** Las entradas nuevas van arriba y las anteriores no se editan jamás, ni para corregir. Si una decisión cambia, se añade una entrada nueva que dice que reemplaza a la anterior.

Un registro nunca vive dentro de un archivo vivo, porque la primera reescritura lo borra.

### Formato de `decisiones.md`

Único para todos los proyectos:

```markdown
## AAAA-MM-DD · Título que dice la decisión en una frase
Decidió: Nombre Apellido
Por qué: … (puede ser más de un párrafo)
Descartamos: …
Afecta a: entregables/x.md · otra-area/proyecto (qué le cambia, en media línea)
```

Una decisión que contesta a un cuestionamiento añade `Responde a: <identificador del cuestionamiento>`, y una que se apoya en una premisa puede nombrarla en `Por qué` («premisa P2»).

**Identificador de una entrada.** Cada entrada de `decisiones.md`, decisión o cuestionamiento, se cita como `area/proyecto#AAAA-MM-DD`, la fecha de su encabezado. Si ese día hay más de una en el mismo `decisiones.md`, la más antigua es `#AAAA-MM-DD` y las siguientes `#AAAA-MM-DD-2`, `-3`, contando desde la de más abajo, que es la más antigua; los cuestionamientos cuentan en la misma serie. Se deduce del registro: no se escribe en el encabezado, y como las entradas no se editan ni se reordenan, no cambia nunca. Una entrada sin fecha válida en el encabezado no tiene identificador y no se puede citar. Dentro del mismo proyecto basta `#AAAA-MM-DD`.

**Cuestionamientos.** Cualquiera puede cuestionar una decisión de otro proyecto o una premisa. El cuestionamiento se escribe en el `decisiones.md` de un proyecto propio, desde una sesión de quien cuestiona, porque nadie escribe en el área de otro:

```markdown
## AAAA-MM-DD · Cuestionamiento: el tope de 5.000 MXN deja fuera las compras recurrentes
Planteó: Nombre Apellido
Por qué: … (qué no cuadra, con su dato o su fuente)
Cuestiona a: compras/automatizacion-ordenes#2026-08-29
```

`Cuestiona a` lleva un identificador de decisión o `premisa P<n>`. El cuestionamiento sigue abierto hasta que el dueño de lo cuestionado registra en su proyecto una decisión con `Responde a: <identificador del cuestionamiento>`, que mantiene lo decidido o lo reemplaza. Mantenerlo también es una decisión («lo mantengo, porque…»): se registra igual, con su por qué, y es lo que cierra el cuestionamiento. Una premisa la responde el responsable de contexto con una premisa nueva que lleve `Reemplaza a P<n>`, que cierra los cuestionamientos abiertos a `P<n>`, o con una entrada con `Responde a:` en el `decisiones.md` de un proyecto suyo si la mantiene. Un cuestionamiento no es una decisión, aunque viva en el mismo registro y se cite igual: no se cuenta como tal.

Una decisión recuperada al migrar que nadie ha confirmado todavía lleva `Decidió: Nombre Apellido (pendiente de confirmar)`. La confirma su dueño con una entrada nueva que la da por buena o la cambia; la recuperada no se edita.

Una entrada tiene lo justo para entender qué se decidió y por qué sin abrir nada más. El análisis que respalda la decisión (opciones, tablas, cifras) no va en la entrada: va a un entregable del proyecto y la entrada lo cita en `Afecta a` o en `Por qué`.

`Afecta a` lleva rutas relativas al proyecto para lo que está dentro de él, y `area/proyecto` cuando la decisión toca a otro proyecto de la raíz. Cada destino admite detrás un paréntesis corto con la consecuencia concreta; sin él, quien recibe el aviso sabe que algo le toca pero no qué. Los destinos se separan con `·` y la línea no se parte en varias.

### Formato de `sesiones.md`

```markdown
## AAAA-MM-DD
Trabajamos en: …
Avances: …
Pendiente: …
```

Entradas nuevas arriba. Una tarea programada que escribe en la carpeta deja su entrada como `## AAAA-MM-DD (tarea)`: cuenta lo que hizo, pero no es una sesión, y el tablero no la cuenta como tal.

### Regla de histórico

Las entradas escritas antes de adoptar este formato se dejan tal cual; el formato aplica desde la siguiente entrada. La excepción es la migración: un registro que se acaba de crear al migrar sí se convierte, porque nadie lo ha consumido todavía.

### Aviso entre áreas

La carpeta no notifica a nadie. Por eso `Afecta a` puede nombrar proyectos de otras áreas: al abrir sesión se buscan, en los `decisiones.md` de la raíz, las líneas `Afecta a:` y `Cuestiona a:` que nombren el proyecto activo (y, en la sesión del responsable de contexto, las que nombren una premisa). Es una búsqueda de un patrón de línea, no una lectura de archivos, y es la única operación que recorre la raíz entera al abrir. Al cerrar sesión, si una decisión afecta a otra área, se recuerda al usuario que avise a su dueño.

## 5. Cabecera

Todo `.md` empieza con una cabecera de estas claves y ninguna más, con dos excepciones: `guia.md` y `metodo.md`, que están hechos para leerse sin nada delante y empiezan directamente por el título, y el contenido de `fuentes/`, que es material y no se edita, así que añadirle una cabecera sería editarlo. El `enlaces.md` de `fuentes/` sí la lleva, porque ese lo escribimos nosotros.

```yaml
---
estado: vigente
actualizado: 2026-08-29
basado_en:
  - base/contexto.md
  - compras/automatizacion-ordenes/fuentes/entrevista-ana.md
---
```

Inmediatamente después va el título en `#`, para que quien abra el archivo sin renderizador vea de qué trata en la primera línea legible.

| Archivo | `estado` | `actualizado` | `basado_en` |
|---|---|---|---|
| Entregables | sí | sí | sí, obligatoria |
| `taller/` | sí, casi siempre `borrador` | sí | si se usó algo |
| `proyecto.md`, `base/` | sí | sí | no |
| `area.md`, `decisiones.md`, `sesiones.md`, `base/premisas.md`, los `enlaces.md` | `vigente` siempre | sí | no |

`area.md` y los registros llevan `vigente` desde que se crean y no lo cambian: son índice y registro, no algo que se publique. Lo que pasa de `borrador` a `vigente` es lo demás.

**estado**, tres valores y nada más:

- `borrador`: no se puede consumir todavía. Da igual si está a medias, terminado esperando al dueño, o adoptado de otro sitio sin revisar
- `vigente`: aprobado, se puede construir encima
- `reemplazado`: superado. Requiere una cuarta clave, `reemplazado_por`, con la ruta del sustituto

El paso a `vigente` lo pide siempre el dueño del proyecto de forma explícita y tiene requisitos: los aplica la skill `revisar`. Ninguna otra skill cambia ese estado por su cuenta. Que un borrador esté a medias o terminado se dice en `Estado actual` de `proyecto.md`.

**actualizado**: fecha en formato `AAAA-MM-DD`, la del último cambio de contenido real.

**basado_en**: rutas relativas a la raíz de todo lo que se usó para escribir el archivo. Es lo que permite detectar que un entregable quedó desactualizado cuando cambia algo aguas arriba. Es obligatoria en los entregables y la escribe la skill, no la persona. Para material adoptado sin trazabilidad se permite la lista vacía `[]`, y `revisar` la pide completa antes de publicar. Los registros, las fuentes y los archivos de `base/` no llevan esta clave.

No hay clave de dueño. El dueño vive en `area.md` y en `proyecto.md`, en `Quién participa`. Si un documento concreto tiene otro responsable, lo dice la primera línea de su cuerpo.

Las claves van sin acentos ni eñes.

## 6. Nombres

Minúsculas, guiones en vez de espacios, sin acentos ni eñes, sin fechas ni números de versión, sin números de fase ni de etapa. `flujo-aprobacion.md`, no `Flujo de Aprobación v2 FINAL.md` ni `fase1-flujo-aprobacion.md`.

El nombre de un archivo es estable durante toda su vida. El historial de versiones lo lleva la carpeta compartida (Drive, OneDrive…), el estado lo lleva la cabecera y el orden de las fases lo cuenta `proyecto.md`.

Las carpetas de área y de proyecto siguen la misma regla, y por una razón más: una referencia `area/proyecto#AAAA-MM-DD` en `Afecta a`, `Cuestiona a` o `Responde a` solo se resuelve con nombres así. `Ventas Norte/cuentas` no la encuentra nadie, y sin dar error.

### El nombre de una carpeta compartida

La raíz es una carpeta compartida y su nombre se ve en Drive, así que ese sí lleva mayúsculas y espacios: `Acme`. Solo letras, números, espacios y guiones, y los acentos y las eñes que traiga el nombre propio. Ningún otro signo, porque ese nombre se escribe a mano muchas veces y un signo raro se copia mal. Si una organización ya tiene una carpeta con un signo así, se propone renombrarla; el método no depende del nombre, porque ninguna instrucción usa rutas absolutas.

## 7. Qué es público

La superficie pública de un proyecto son `entregables/` y `decisiones.md`. Es lo único que otra área puede leer para construir encima, y solo si el entregable está `vigente`. `area.md` y `proyecto.md` también se leen desde fuera, porque son el índice que lleva hasta esa superficie.

`sesiones.md`, `taller/`, `fuentes/` y todo lo que está restringido son taller privado. Nadie de fuera del área los lee ni los cita en `basado_en`. Un entregable sí cita el taller de su propio proyecto, que es de donde salió.

Dentro de la misma área, un entregable puede citar en `basado_en` una fuente de otro proyecto del área, siempre la original y nunca una copia: un export vive en un solo `fuentes/` y los demás lo citan por su ruta. Entre áreas no se citan fuentes, solo entregables vigentes y decisiones.

### Lo restringido se cita en una sola dirección

Un archivo restringido puede citar en `basado_en` lo que quiera de lo que sí lee todo el equipo: entregables vigentes, decisiones, `base/`. Al revés, nunca. Nada que lea todo el equipo cita, nombra ni resume un archivo restringido, porque quien lo lea no va a poder abrirlo y porque la cita misma ya cuenta algo de lo que hay dentro. La única excepción es la fila de `fuentes/enlaces.md`, que dice que un material existe y dónde está, no lo que dice.

Vale igual para `Afecta a`: una decisión restringida puede apuntar a cualquier proyecto, y una decisión que lee todo el equipo apunta a un área o a un proyecto restringido por su nombre, que ya está listado, nunca a uno de sus archivos.

Lo aprendido dentro de un área restringida vuelve a la memoria común **reescrito, no movido**: se publica como entregable propio de un proyecto que lee todo el equipo, con lo que sirve para la próxima vez y sin los datos, las cifras ni los nombres de donde salió. Un archivo restringido no sale nunca de donde está; un aprendizaje sí cambia de sitio, y lo hace escribiéndolo de nuevo.

## 8. Rotación

Cuando `sesiones.md` o `decisiones.md` pasa de unas 1.500 líneas o cambia el año, se archiva en la misma carpeta con el año en el nombre (`sesiones-2026.md`; si en un mismo año hace falta otro, `sesiones-2026-2.md`) y se abre uno nuevo con su cabecera. Es la única excepción a los nombres sin fechas: el año es lo que distingue el registro archivado del vivo. Lo hace la skill de cierre de sesión, sin preguntar.

## 9. Lo que no existe en este sistema

- Una carpeta `metodo/` dentro de la raíz. El método vive en el plugin y en `metodo.md`
- Un archivo de reglas propias en `base/`. Lo propio de la organización vive en `guia.md`
- Una carpeta de plantillas en la raíz. Las dos plantillas del método viven en el plugin
- `AGENTS.md` ni ningún archivo de instrucciones para la IA dentro de la raíz. Las instrucciones son las skills, el aviso de arranque del plugin y `guia.md`
- Índices, inventarios o resúmenes mantenidos a mano o por otra herramienta. El único índice es el bloque `Proyectos` de cada `area.md`, es derivado y lo escriben las skills
- El almacén de datos de una aplicación dentro de la raíz. Lo escribe la aplicación sola y nadie responde por lo que hay dentro
- El tablero dentro de la raíz. La página que muestra la carpeta entera, su base de datos, sus scripts y su tarea viven fuera, en la cuenta de la persona que lo montó; es derivado de la raíz y nunca su fuente, y en la raíz no deja ni su enlace
- Material que llegó de fuera guardado en cualquier sitio que no sea `fuentes/`
- Una clave de dueño en la cabecera. El dueño está en `area.md` y `proyecto.md`
- Un estado intermedio entre `borrador` y `vigente`. Si un borrador está terminado y espera al dueño, lo dice `Estado actual` de `proyecto.md`
- Una carpeta compartida aparte para lo restringido, ni espejos de la raíz. Se restringe donde está
- Subcarpetas dentro de `restringido/`. Es plano, con su `enlaces.md`
- Una carpeta de trabajo intermedio con otro nombre. Lo que se escribió en sesión y no sale del proyecto va a `taller/`
- Registros propios dentro de `taller/`. Las decisiones y las sesiones son del proyecto entero
- Una carpeta restringida sin dueño en `area.md` o en `proyecto.md`. Restringir no cambia de quién es
- Copias de una fuente en dos proyectos. Se cita la original
- Carpetas numeradas (`01-`, `02-`) ni números de fase en los nombres
- Carpetas llamadas `varios`, `otros`, `temp` o `borrador`
- Un archivo por decisión
- Enlaces wiki `[[asi]]`, callouts propietarios, archivos `.canvas`
- Rutas absolutas dentro de cualquier archivo
- Estado del método guardado en la memoria del modelo ni en la memoria de proyecto de Claude: es por persona, no se comparte, no se ve y puede contradecir un archivo sin que nadie lo note. Si un dato importa, está en un `.md`
- Cualquier archivo que el usuario tenga que rellenar a mano

## 10. Prohibiciones

Valen para todas las skills y no se repiten en ninguna. Cada skill añade las suyas, que son las de su trabajo concreto.

1. No marcar nada como `vigente`. Solo lo hace `revisar`, y solo cuando lo pide el dueño del proyecto; y `migrar`, con lo que su dueño en el origen pide publicar al migrar. `area.md` y los registros nacen `vigente` (sección 5).
2. No editar una entrada ya escrita de `decisiones.md` o de `sesiones.md`, ni para corregir una errata. Un registro solo crece.
3. No registrar una decisión que el usuario no confirmó en esta sesión, salvo las recuperadas al migrar, que entran marcadas «pendiente de confirmar» (sección 4).
4. No escribir en `guia.md`, en `base/`, en `metodo.md` ni en la carpeta de otra área. Desde la sesión de otra área se prepara el texto y se le pasa a quien responde. Las excepciones: la sesión del responsable de contexto escribe `guia.md` y `base/`, y `metodo.md` lo pone al día cualquier cuenta con el plugin más nuevo (sección 11).
5. No tocar archivos fuera del proyecto activo, salvo la línea de ese proyecto en el bloque `Proyectos` de su `area.md`, `Panorama` de ese `area.md` al cerrar sesión o cuando su dueño lo pide (skill `director`), `Prioridades ahora` de ese `area.md` cuando su dueño lo pide en la sesión, y lo mecánico que la puesta al día del tablero escribe en los proyectos de las áreas de la cuenta: fechas de pasos y hechos marcados desde el tablero (skill `tablero`), nunca en las áreas de otra cuenta.
6. No leer `sesiones.md`, `taller/`, `fuentes/` ni lo restringido de otra área. Son taller privado y no responden a nadie de fuera.
7. No escribir en un archivo que lee todo el equipo la ruta ni el contenido de algo restringido, aunque sea resumido. Hacia fuera solo van el nombre del área o del proyecto, que ya están listados, y la fila de `enlaces.md`.
8. No guardar en `fuentes/` un material con indicios de información confidencial sin haberlo dicho y preguntado antes, ni mover nada a `restringido/` sin que el usuario lo confirme.
9. No guardar fuera de `fuentes/` material que llegó de fuera del equipo del proyecto, aunque venga terminado y listo para usarse.
10. No copiar a este `fuentes/` una fuente que ya existe en otro proyecto del área. Se cita la original por su ruta.
11. No crear un área ni un proyecto sin dueño con nombre y apellido.
12. No rellenar un hueco con una suposición razonable. Un hueco se marca como hueco, y "no consta" es una respuesta válida.
13. No escribir una cifra sin fecha ni fuente.
14. No poner número de fase, fecha ni versión en el nombre de un archivo o de una carpeta. El registro archivado por año es la única excepción (sección 8).
15. No crear carpetas que la estructura no contempla, ni un `AGENTS.md`, ni un índice a mano, ni una carpeta de borradores.
16. No dejar dentro de la raíz el almacén de datos de una aplicación, ni apuntar una aplicación a que escriba ahí.
17. No borrar un entregable superado. Pasa a `reemplazado` con `reemplazado_por`, porque alguien puede tenerlo citado.
18. No llevar a la raíz de una organización ningún hecho que venga de otra raíz, ni siquiera para comparar, salvo por un traspaso que la persona pidió y confirmó pieza a pieza (sección 1, «Independencia entre raíces»).
19. No guardar estado del método en la memoria del modelo. Si un dato importa, va a un `.md` de la carpeta.
20. No dejar en `entregables/` lo que no puede salir del proyecto. Si no se lo puedo dar a nadie de fuera, va a `taller/`.
21. No abrir un `decisiones.md` ni un `sesiones.md` dentro de `taller/`. Los registros del proyecto son los de su raíz.

## 11. Actualización del método

El método se actualiza publicando una versión nueva del plugin, y cada raíz recibe su `metodo.md` sola, de la primera cuenta con el plugin más nuevo que abre sesión o pone al día un tablero. Nadie edita `metodo.md` dentro de la carpeta de una organización. La regla completa (cuándo se copia, quién, qué pasa sin permiso), cómo se publica una versión y cómo se verifica una raíz están en `montaje.md`, junto a este archivo.

## 12. Cómo se lee

Nunca se lee todo, y casi nunca se lee `base/`. Al abrir, se carga lo justo para saber qué existe y dónde está cada cosa; el resto entra cuando el trabajo del día lo pide, y por su nombre.

**Nivel 0, siempre, y nada más que esto.** Cuatro lecturas cortas:

1. La primera línea de `metodo.md`, para la versión y la huella de la raíz.
2. `guia.md` entero. Es el mapa: qué áreas hay, quién responde por cada una y con qué cuenta, quién mantiene el contexto, quién administra la carpeta y las reglas propias de la casa. Cabe en una pantalla.
3. El bloque `Proyectos` del `area.md` que toca. Dice qué proyectos hay y qué entregables vigentes tiene cada uno.
4. `base/premisas.md`, si existe: las premisas vigentes, las que ninguna otra reemplaza. Es corta y todo se ancla en ella.

Con eso ya se sabe qué existe, de quién es y dónde está. Todo lo demás se pide por su nombre.

**Nivel 1, del proyecto activo, una vez que se sabe cuál es.** `proyecto.md`; las cinco entradas más recientes de `decisiones.md`; las tres más recientes de `sesiones.md`; y las cabeceras de `entregables/`, nunca su cuerpo. Para los avisos de apertura se miran además, sin abrirlos, la fecha `actualizado` de `base/contexto.md` y las cabeceras de lo que citan los entregables en `basado_en`. Si la cuenta tiene tablero (un artifact llamado «Tablero <organización>» o «Tablero <organización> completo», con la organización del título de `guia.md`; se busca listando los artifacts de la cuenta), también la cola de ese proyecto en ese tablero: lo que se fechó, marcó hecho, anotó o corrigió desde él y la carpeta todavía no refleja. Es lo primero que se resuelve en la sesión, antes de proponer en qué trabajar.

**Nivel 2, a demanda, cada uno con su disparador.**

| Se lee | Cuando |
|---|---|
| `base/glosario.md` | aparece una sigla o un nombre interno que no se entiende |
| `base/sistemas.md` | el trabajo toca un sistema |
| `base/contexto.md` | la pregunta es sobre la organización, o se va a escribir algo que sale del proyecto |
| `area.md` entero | la pregunta es sobre el área y no sobre un proyecto |
| `decisiones.md` completo | se va a escribir o revisar un entregable |
| El cuerpo de un entregable | la pregunta pide su contenido y no basta con saber que existe |
| Un archivo de `taller/` | hace falta cómo se llegó al entregable, y el entregable no basta |
| Un archivo de `fuentes/` | el trabajo del día lo pide, por su nombre |

Ningún nivel se salta: no se abre el cuerpo de un entregable sin haber visto su cabecera, ni un proyecto sin haber visto el bloque `Proyectos` de su área. Y se para en el primer nivel que responde: si `guia.md` ya dice quién lleva algo, ahí termina la lectura.

La única operación que recorre la raíz entera es la búsqueda de las líneas `Afecta a:` y `Cuestiona a:` que nombran el proyecto activo, al abrir sesión. Busca un patrón de línea, no lee archivos, y las carpetas restringidas sin acceso fallan y se saltan.

Si el camino lleva a una carpeta restringida sin acceso, la lectura falla. Eso no es un error ni un hueco: se dice qué área o qué proyecto es y quién es su dueño, y ahí se para. No se deduce lo que hay dentro por los nombres de las carpetas ni se da por hecho que no hay nada.

## 13. Montaje

Se conecta la raíz completa, nunca la carpeta de un área: `guia.md`, `metodo.md` y `base/` viven en la raíz y la lectura cruza áreas. Cada persona trabaja desde su cuenta, y dónde escribe sale de su fila en `guia.md`. El plugin trae un aviso de arranque que inyecta las instrucciones en cada sesión, así que nadie pega nada en el proyecto de Claude. El tablero es opcional y personal (skill `tablero`). El montaje en detalle, el bloque de instrucciones para quien use otro modelo sin el plugin y lo que vale para programadores están en `montaje.md`, junto a este archivo.

## Anexo: Varias raíces y traspasos

Anexo del contrato (`convenciones`, sección 1). Se lee cuando hay más de una raíz conectada, cuando alguien pide pasar algo de una raíz a otra y al migrar.

### Independencia entre raíces

Una sesión puede tener conectada más de una raíz a la vez, o una raíz y el repo del plugin. Se trabaja en una a la vez: si hay más de una carpeta con `guia.md` y `metodo.md`, antes de leer o escribir nada se pregunta en cuál, cada escritura dice en qué raíz se hace y cambiar de raíz se anuncia. Cada raíz sigue siendo de una sola organización: nada que se escriba en una raíz usa hechos, cifras, nombres o decisiones de otra raíz, ni del repo del plugin, salvo por un traspaso; y nada que se escriba en el repo del plugin usa hechos de una organización en particular, porque el plugin es idéntico para todas. Comparar la forma de dos raíces (¿tienen las mismas piezas?, ¿la misma cabecera?) no es tocar su contenido, y ese trabajo no se guarda dentro de ninguna de las dos. Lo que una organización guarda sobre otra, por ejemplo quien mantiene el método guardando el historial de una migración que hizo para un cliente, se limita a lo operativo de quien lo guarda: qué se entregó y cuándo, nunca el contenido del trabajo del cliente.

### Traspaso entre raíces

 A veces algo de una raíz tiene que llegar a otra: lo que se decidió sobre un cliente en la raíz de su proveedor y el cliente necesita en la suya, o al revés. Solo ocurre si lo pide la persona que trabaja, pieza a pieza, hacia una raíz donde puede escribir. Antes de escribir se le enseña el texto exacto que pasaría, a qué archivo de la otra raíz iría y qué se queda fuera y por qué (datos personales, contratos, credenciales, cifras internas, lo de otros clientes); se escribe solo cuando lo confirma. En el destino entra reescrito para su contexto y por la puerta que le toque: una decisión se registra como decisión de quien la asume ahí, y un documento entra por `fuentes/` o como entregable de quien lo hace suyo. La sesión del proyecto de destino anota qué vino, de qué raíz, quién lo pidió y cuándo. El origen no se toca. Credenciales, y datos de una organización hacia la raíz de otra que no tiene que ver con ellos, no pasan nunca, aunque se pida: se dice por qué. Lo demás lo decide quien pide el traspaso, que tiene la última palabra.

### Dónde vive el registro de una migración

Eso fija dónde vive cada cosa cuando una organización adopta el método. **El registro de la migración es de quien migra**: las auditorías, los planes y los manifiestos van a su raíz, en un proyecto por organización nombrado por la organización y no por el trabajo. Cuentan lo que hizo el proveedor y hablan del sistema del que se migró, que la organización que estrena el método no usó nunca y no le dice nada.

En la raíz de la organización entra solo lo que su equipo necesita para operar, y entra donde se usa, no en un proyecto aparte: las decisiones recuperadas de su material anterior, cada una en el `decisiones.md` del proyecto al que pertenecen y marcadas como pendientes de confirmar; y el material confidencial que quedó fuera de alcance, con su fila en el `fuentes/enlaces.md` que corresponda. Nada más: su raíz no guarda rastro del sistema del que se migró, ni en las rutas, ni en el vocabulario, ni en los nombres de sus archivos.

## Anexo: Montaje, publicación y otros modelos

Anexo del contrato (`convenciones`, secciones 11 y 13). Lo leen `nuevo` al montar una raíz, `tablero`, y quien pregunte cómo se monta o se publica el método. El bloque de instrucciones de abajo es el que inyecta el aviso de arranque del plugin en cada sesión.

### Actualización del método

El método se actualiza publicando una versión nueva del plugin. La primera línea legible de `metodo.md` lleva la versión y una huella de su contenido, que escribe `build-metodo.sh`: cualquier cambio de texto la cambia aunque el número no cambie. Al abrir sesión se compara esa línea en la raíz con la del `metodo.md` del plugin. La raíz está atrasada si la versión del plugin es mayor, o si es la misma y la raíz no lleva huella; con la misma versión y huellas distintas no se toca nada (solo pasa entre dos publicaciones). Si está atrasada, la sesión que abre (skill `sesion`) o la puesta al día de cualquier tablero (paso 0 de `tarea.md`) copia el `metodo.md` del plugin sobre el de la raíz, sin preguntar y sin tocar nada más, y lo dice en una línea. Lo hace cualquier cuenta, no solo el responsable de contexto, porque es una copia exacta del plugin y no contenido de la organización: una versión nueva llega a la carpeta con la primera persona que abre, cierra o sincroniza con el plugin actualizado. Nunca hacia atrás. Si la cuenta no tiene permiso para escribir en el primer nivel de la carpeta, la escritura se rechaza, no se intenta por otra vía, no se dice nada y lo hará la siguiente cuenta que pueda. Si el atrasado es el plugin de quien abre, se le dice que lo actualice. Nadie tiene que acordarse de copiarlo. Nadie edita `metodo.md` dentro de la carpeta de una organización.

Tres scripts acompañan al plugin y nadie tiene que recordar sus pasos. `release.sh` publica una versión: comprueba antes de tocar nada que la versión sea mayor que la actual, que el contrato declare la mayor.menor y que el README tenga su entrada; sube el número donde vive, regenera `metodo.md` y dice qué queda por hacer a mano. Si algo falla a mitad, deja los archivos como estaban. `verificar.sh` se pasa sobre la raíz de una organización: comprueba la estructura, los nombres, las cabeceras, los estados y que el bloque `Proyectos` de cada área liste todo lo que tiene que listar. No escribe nada: de cada `.md` lee la cabecera y busca enlaces wiki y rutas absolutas, no entra en `fuentes/` ni en `restringido/`, y una carpeta que no se deja leer la salta.

### Montaje en Claude

El uso principal del método es Claude con la raíz conectada y el plugin instalado. El montaje tiene dos reglas.

**Un proyecto de Claude por persona**, nombrado por su área, o por la organización si esa persona lleva todas las áreas. Dónde escribe no lo decide el nombre del proyecto sino su cuenta en `guia.md`, así que un solo proyecto sirve para todas las áreas de quien las lleva todas.

**Se conecta la raíz completa, nunca la carpeta de un área.** `guia.md`, `metodo.md` y `base/` viven en la raíz; la lectura cruza áreas; `consulta` busca en lo que produjo cualquier área y `sesion` avisa de las decisiones de otras que afectan al proyecto. Conectada solo un área, el método se rompe en la primera llamada. Conectar de más no abre ningún riesgo: quién puede leer y escribir dónde lo fijan los permisos de las carpetas, no el alcance de la conexión, y lo restringido sigue restringido dentro de una carpeta conectada.

Al proyecto se le vincula la raíz, y para trabajar en un área no hace falta ninguna carpeta más. Si se vinculan varias raíces, vale lo de «Independencia entre raíces» (sección 1).

**El tablero es opcional y personal.** Cualquiera lo monta desde su propia cuenta escribiendo «monta el tablero» con la raíz conectada; la skill `tablero` publica la página, que se regenera cada vez que esa persona cierra una sesión, desde su computadora y con sus permisos (una tarea que la regenere cada mañana solo se crea si se pide): lo que su cuenta no lee en la carpeta sale como restringido, y lo que su tarea escribe lo escribe con sus permisos. Tiene dos modos: público, la superficie pública del contrato con lo restringido declarado fuera y de las sesiones solo fecha y título, que se puede compartir con cualquiera de la organización desde el menú del artifact; y completo, con todo lo que la cuenta lee y las sesiones recientes enteras, que es para su dueño y no se comparte. Se encuentra por su nombre entre los artifacts de la cuenta; en la raíz no queda nada de él. Lo que se toca en el tablero espera en su cola hasta que la siguiente puesta al día lo escribe en la carpeta, o hasta la siguiente sesión del proyecto si pide juicio; la página nunca escribe en la raíz. Cuando sale una versión nueva del plugin, la siguiente puesta al día republica la página sobre la misma URL sin que nadie lo pida.

**Nadie pega instrucciones en el proyecto.** El plugin trae un hook de arranque que, al empezar cada sesión, inyecta el bloque de abajo como contexto, y con él cómo saber dónde escribe cada quien: la cuenta que abre la sesión se busca en la columna Cuenta de la tabla de áreas de `guia.md`, y esas áreas son las suyas. Así el método se aplica en cuanto la carpeta está conectada, se actualiza solo con cada versión del plugin y no depende de que nadie copie bien un texto. El bloque sigue aquí para quien trabaje con otro modelo sin el plugin, o en una superficie donde el arranque del plugin no corra: en ese caso se pega tal cual y se añade debajo una línea propia diciendo dónde se escribe. El texto no nombra skills, porque Claude las elige solo:

```
Este proyecto trabaja sobre una memoria de trabajo permanente: la carpeta conectada, que sigue el método del plugin `memoria`. Aplícalo en todo lo que hagas aquí, y no guardes nada en tu memoria: si un dato importa, va a un archivo de la carpeta.
Lee `guia.md` al empezar y no leas nada más hasta saber qué necesitas: la carpeta se lee por niveles y `guia.md` dice dónde está cada cosa.
Lee y escribe la carpeta por su copia en esta computadora, nunca por el conector de Google Drive aunque esté conectado; si no la ves, pídeme que la añada. Sin ninguna carpeta conectada (desde el teléfono o la web), la raíz se puede leer por el conector de Drive, sin escribir nada en ella.
Escribe solo en las áreas que `guia.md` asigna a tu cuenta, o donde te diga que trabajo si la cuenta no aparece, y en ningún otro sitio de la carpeta; si no está claro, pregúntamelo antes de escribir nada. Si algo le toca a otra área, dímelo y yo se lo pido a su dueño.
No des por aprobado ningún documento ni edites lo ya registrado en decisiones o sesiones.
Si una carpeta no se deja leer, está restringida: dímelo y sigue con lo que sí puedas leer, sin suponer lo que hay dentro.
Lo que hagas para un proyecto, un documento, un PDF o un análisis, guárdalo en su carpeta en cuanto exista, como borrador, y no en «Claude outputs»; cerrar sesión es registrar lo que pasó, no guardar.
Antes de guardar algo, pregúntate si alguien más lo va a leer y si contiene datos que no todos deben ver. Si algo parece confidencial, avísame y propón moverlo; no lo muevas tú.
```

El bloque es idéntico en cualquier organización: no nombra a ninguna, no lleva huecos que rellenar y nada de una raíz concreta entra en él. Lo propio de una raíz vive en `guia.md`, que la segunda línea manda leer. Dónde escribe cada quien sale de `guia.md` y de la cuenta de la sesión; si ninguna área coincide con la cuenta, la IA pregunta antes de escribir en vez de suponer.

La skill `nuevo` escribe todo esto en `guia.md` como una receta corta: crear el proyecto con el nombre del área, instalar el plugin desde el marketplace, conectar la raíz, comprobar con «abre sesión en...» y, si se quiere, montar el tablero, para que cada persona lo monte sola sin preguntarle a nadie.

**Otros modelos.** Gemini u otro modelo sin plugin leen `metodo.md`. Contiene el contrato con sus dos anexos, el estilo y el índice de skills, así que saben qué reglas seguir aunque no puedan ejecutarlas como skills.

**Programadores.** El `CLAUDE.md` de un repositorio enlaza la carpeta del proyecto en la raíz (`area/proyecto`). Las decisiones de código que dependen de un diseño se anclan en `decisiones.md` y en los entregables vigentes de ese proyecto, no en comentarios del código. Para saber qué se decidió antes de escribir código, usan la skill `consulta`.

---

# Estilo

Estilo de todo lo que se escribe, firma o comparte en esta estructura:

> **Ejecutivo y al grano: el hecho relevante desde el inicio, sin rodeos ni expresiones que no aporten de manera directa.**

Se escribe para alguien con poco tiempo y muchas interrupciones. Tiene que poder leer en diagonal, quedarse con lo que decide y no perderse nada esencial por haberlo hecho así.

Este archivo es la fuente canónica del estilo. Si una plantilla del plugin lo contradice, manda este archivo.

## Cuándo se aplica

Siempre, sin que nadie la invoque, en cualquier redacción o revisión. Y de forma explícita cuando alguien pide que suene menos a IA, más ejecutivo, más al grano, más compacto, que se lea rápido, o que le quiten los rodeos.

**No se cambia por iniciativa propia.** Este es el estilo de la casa y se aplica por defecto, aunque el texto parezca pedir otro registro. Solo cambia si quien encarga el texto lo pide de forma expresa, y el cambio vale para ese texto: no se guarda como estándar nuevo ni se arrastra al siguiente entregable.

## Las dos preguntas que resuelven casi todo

1. **¿La primera frase ya dice el hecho, o lo anuncia?** Si lo anuncia, empieza por el hecho.
2. **¿Puedo borrar esta palabra y no se pierde información?** Entonces sobra.

## Lectura rápida

Los siete patrones de abajo arreglan la frase. Estas ocho reglas arreglan el documento, que es donde se pierde al lector que tiene prisa.

1. **La primera pantalla basta.** Quien solo lee eso sale sabiendo el estado y qué se decide. Nada esencial vive por debajo del primer pliegue.
2. **Los títulos dicen el hecho, no el tema.** *"El motor cuesta 2.44 M al año"*, no *"Costos del motor"*.
3. **Una idea por fila.** Si el contenido se puede enumerar, va en lista o tabla. La prosa se reserva para lo que necesita argumento.
4. **Si cabe en una fila de tabla, no va en un párrafo.**
5. **Cada afirmación trae su dato.** Un párrafo que no aporta un dato ni cambia una decisión se borra.
6. **La consecuencia va pegada a la acción.** El "si esto no ocurre, pasa aquello" debajo de su acción, no en una lista de riesgos al final que el lector ya no relaciona.
7. **Lo hecho antes de lo pendiente**, cuando el lector decide sobre el trabajo de otros.
8. **Sin preámbulo de sección.** Título y contenido. Las frases que presentan lo que viene se borran.

## Siete patrones a evitar

**1. Metadiscurso, frases que anuncian en vez de decir.** El patrón que más suena a IA: construye expectativa antes de entregar contenido.

- Mal: *"El punto central es que el motor propio sale más barato."* · *"Y el hallazgo que reordena la pregunta: no existe API fiscal mexicana."* · *"Lo que conviene tener claro:"* · *"para una lectura equilibrada"*
- Bien: *"El motor propio sale 5× más barato."* · *"No existe API fiscal mexicana en el mercado."*

**2. Guiones largos como muletilla.** Cuando el guion sustituye a dos puntos, coma o punto y coma, usa la puntuación normal. Resérvalos para incisos que funcionan como paréntesis.

- Mal: *"La decisión es clara — modernizar el motor."*
- Bien: *"La decisión es clara: modernizar el motor."*
- Bien, inciso legítimo: *"El motor —heredado de 2007— sigue en producción."*

El umbral: más de un guion largo cada 500 palabras en un entregable es muletilla, aunque cada uno por separado parezca defendible. Un entregable de 1.500 palabras con siete guiones largos tiene que bajar a tres como mucho.

- Mal: un brief de 600 palabras con cinco guiones largos, todos correctos como incisos. Son demasiados para lo que dice el texto.
- Bien: el mismo brief con uno, y los otros cuatro convertidos en dos puntos, paréntesis o frases separadas.

**3. Negaciones en espejo.** *"No es X, es Y."* Legítimas solo cuando corrigen una expectativa falsa que el lector traía. Si no la traía, di Y directamente.

- Mal: *"No es un problema de producto, es un problema de go-to-market."* (si nadie dijo que fuera de producto)
- Bien: *"El problema es de go-to-market."*

**4. Rodeos en las conclusiones.** La conclusión es lo que menos tolera preámbulo.

- Mal: *"La postura de fondo es modernizar."* → Bien: *"Modernizar."*

**5. Negritas como subrayado nervioso.** Una negrita destaca; cinco no destacan ninguna. En documentos internos ayudan a escanear; en un documento para terceros, tres por párrafo cansan.

**6. Signos que no se leen en voz alta en español.** Si no puedes leer el signo en voz alta, escribe la palabra. El caso cerrado es el signo de sección, que no aparece en ningún documento.

- Mal: el signo de sección pegado a un número o a un nombre, como abreviatura de "sección"
- Bien: *"ver la sección 4.1"* · *"secciones 2 y 3"* · *"de la sección 8"* · *"sección Nómina"*
- Se conservan `%`, `·`, `→`, el `#` de un ticket, y cualquier signo que sea parte de un identificador citado literalmente.

**7. Cifras sueltas.** Toda cifra en un entregable lleva fecha o fuente en el mismo párrafo. Una cifra sin ninguna de las dos no se puede comprobar ni saber si sigue valiendo, y el lector de dentro de seis meses no tiene a quién preguntar.

- Mal: *"El 70% del volumen son órdenes pequeñas."*
- Bien: *"El 70% del volumen son órdenes pequeñas (export de órdenes de 2025, `fuentes/ordenes-2025.csv`)."* · *"A agosto de 2026, el 70% del volumen son órdenes pequeñas."*

La fecha basta cuando el dato es de la propia organización y está en una fuente ya citada en la cabecera. La fuente hace falta cuando el dato viene de fuera.

## Alcance

- **Entregables y cualquier texto que salga del proyecto:** los siete patrones y las ocho reglas de lectura rápida, sin excepción.
- **Registros** (`sesiones.md`, `decisiones.md`): pueden ser más extensos, porque su función es dejar constancia del razonamiento. El metadiscurso y los rodeos sobran igual, y una cifra en `Por qué` también lleva su fecha o su fuente.
- **Respuestas de la IA en el chat:** la respuesta primero y el detalle después, sin recapitular lo que el usuario acaba de decir y sin narrar lo que se va a hacer. El único límite es no perder información que el usuario necesita para decidir: entre una respuesta corta y una completa gana la completa, pero sin relleno.
- **Archivos citados en el chat:** cada archivo de la carpeta que se nombra en una respuesta va enlazado para abrirlo con un clic, y el enlace va en el nombre, no en una línea aparte: `[plan-implementacion.md](computer:///Users/ana/Memoria/Acme/ventas/cuentas/entregables/plan-implementacion.md)`. La ruta es la de la raíz en la computadora (la que da `get_device_info`) más la ruta dentro de la raíz, con `/` como separador y codificada entera como URL, en UTF-8 y con los acentos compuestos (NFC): un espacio es `%20`, una «á» es `%C3%A1`, y `#`, `?` y `%` también se codifican. En Windows, la letra de unidad va así: `computer:///C:/Users/…`. Sin la carpeta conectada, en solo lectura por Drive, el enlace es el `viewUrl` de Drive del archivo. Sin ninguno de los dos, la ruta en código, como hasta ahora.

## Al revisar un texto existente

1. Señala los pasajes concretos y propón la reescritura. No reescribas el documento entero en silencio.
2. Lee solo la primera pantalla y pregúntate si con eso basta para saber el estado y qué se decide. Si no basta, el problema es de orden y se arregla antes que las frases.
3. Cuenta los guiones largos antes y después, y compáralos con el umbral de uno cada 500 palabras. Es la medida más rápida de si el texto mejoró.
4. Busca cada cifra y comprueba que tenga fecha o fuente al lado.
5. No toques las citas textuales de terceros ni los nombres propios de documentos y decisiones.
6. Corregir el estilo de un entregable de otro proyecto o de otra área es tocar contenido ajeno, no forma. Se propone al dueño, no se aplica.

---

# Skills del plugin

Lo que hace cada una, en una línea. Con el plugin instalado se activan solas por las frases que menciona cada descripción.

- **convenciones**: Contrato base del metodo de trabajo: estructura de carpetas, cabecera de los archivos, estados, como se lee la raiz, que es publico y que se restringe. Consultala antes de crear o modificar cualquier archivo dentro de la memoria de una organizacion, y cuando pregunten como se organiza algo, donde va, que significa un estado o quien puede escribir donde.
- **estilo**: Normas de estilo y de lectura rapida. Aplicala por defecto al redactar o revisar cualquier texto que se vaya a firmar o compartir, y tambien a las respuestas en el chat, sin que la invoquen; y de forma explicita cuando pidan 'que suene menos a IA', 'mas ejecutivo', 'mas al grano', 'mas compacto', 'que se lea rapido' o 'revisa el estilo'.
- **sesion**: Abre y cierra sesiones de trabajo sobre un proyecto. Usala cuando digan 'abre sesion', 'retomamos X', 'en que quedamos con...', 'cierra la sesion', 'guarda lo de hoy', 'terminamos' o 'cierra el proyecto', y cuando el dueño de un proyecto pregunte por el suyo: '¿como va X?', '¿en que estatus esta X?', '¿que falta en X?'.
- **nuevo**: Da de alta lo que falte en la memoria de la organizacion: monta la raiz si la carpeta no tiene guia.md, crea el area si no existe y crea el paquete completo de un proyecto. Usala cuando digan 'nuevo proyecto', 'arranca un proyecto para...', 'necesito documentar esto como proyecto', 'nueva area', 'crea el area de...', 'monta la carpeta de...', 'nueva organizacion', 'arranca el metodo para este cliente', o cuando se trabaje en algo que todavia no tiene carpeta.
- **entregable**: Crea o actualiza un entregable de un proyecto. Usala cuando pidan 'prepara el documento de...', 'necesito un documento con...', 'documenta lo que decidimos sobre...', o 'actualiza el entregable X'.
- **revisar**: Revisa un entregable, detecta lo que quedo desfasado y lo publica de borrador a vigente. Usala con 'revisa X', 'esto esta listo?', 'que esta desactualizado?', 'pasalo a vigente' o 'ya lo aprobo...'.
- **donde-va**: Coloca cualquier material que llegue en el sitio correcto de la estructura. Usala cuando pregunten 'donde guardo esto?', peguen un documento o un enlace sin decir donde va, aparezca un archivo suelto en la raiz, o digan 'ordena Claude outputs'.
- **consulta**: Responde preguntas sobre lo que la organizacion ya sabe, leyendo solo la superficie publica de la raiz y sin escribir nada. Usala cuando pregunten 'que sabemos de X?', 'alguien ya trabajo esto?', 'que se decidio sobre...?', 'hay algo hecho sobre...?' o 'quien lleva...?'.
- **tablero**: Monta, actualiza y sincroniza el tablero de una persona sobre la carpeta de su organizacion, una pagina que muestra la carpeta entera (areas, proyectos, estado, decisiones, siguientes pasos) generada desde los archivos y puesta al dia al cerrar cada sesion. Usala cuando digan 'monta el tablero', 'monta mi tablero', 'quiero ver la carpeta sin abrirla', 'actualiza el tablero', 'sincroniza el tablero', 'regenera la vista', 'pon el tablero al dia cada manana', 'pon el boton de sincronizar' o pregunten por que el tablero no muestra algo.
- **migrar**: Adopta una carpeta que sigue otra estructura y la trae al metodo sin borrar los originales. Usala cuando digan 'migra esta carpeta', 'trae esto al metodo', 'adopta lo que hay en...', 'convierte estos documentos a la estructura' o cuando aparezca una carpeta con ADR, logs de sesion o carpetas numeradas.
- **director**: Actua como director de un area - resume como esta, cuestiona su contenido para encontrar oportunidades, revisa lo que otras areas decidieron o publicaron que le afecta, y escribe el Panorama del area al cerrar sesion. Usala cuando digan 'como va el area X?', 'resumen del area', 'panorama de...', 'cuestiona el area', 'que se nos escapa en...', 'que de otras areas me afecta?', 'revisa lo de otras areas' o 'actualiza el panorama'.
- **calidad**: Revision de calidad a fondo de algo que se esta construyendo - el contenido de un proyecto, un entregable, un desarrollo o plugin, o la carpeta entera (auditoria) - contra su objetivo, con revisores independientes, para encontrar errores, inconsistencias, riesgos, oportunidades y lo que cuesta de mas (tiempo, llamadas, tokens). Usala cuando digan 'revision de calidad', 'revisa a fondo...', 'audita la carpeta', 'que no cuadra en...', 'revisalo todo contra el objetivo' o cuando toque la revision periodica de un proyecto.
