---
name: convenciones
description: Contrato base del metodo de trabajo: estructura de carpetas, cabecera de los archivos, estados, como se lee la raiz, que es publico y que se restringe. Consultala antes de crear o modificar cualquier archivo dentro de la memoria de una organizacion, y cuando pregunten como se organiza algo, donde va, que significa un estado o quien puede escribir donde.
---

# Convenciones

Contrato base del método. El resto de skills del plugin lo cargan antes de escribir nada y no repiten sus reglas. Si una skill contradice algo de aquí, manda este documento.

Versión del método: **1.10**

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

Ninguna carpeta de trabajo aloja el almacén de datos de una aplicación. Lo escribe la aplicación sola, crece por su cuenta y nadie responde por lo que hay dentro.

La migración es la excepción declarada. El material que se adopta al migrar no llega de fuera: es el trabajo anterior de la propia organización, y entra donde le toque con `estado: borrador` y con la trazabilidad que se pueda reconstruir. Lo que en el origen ya era material de entrada entra por `fuentes/` como en cualquier proyecto. Lo detalla la skill `migrar`.

Es norma, no candado. Nada impide abrir un archivo y editarlo a mano, y a veces hay que hacerlo; detectar lo que entró por otro camino es trabajo de la skill `revisar`. La propiedad no cambia: quien responde por un archivo sigue siendo su dueño, lo que cambia es la mano que escribe.

La raíz es la carpeta que contiene `guia.md`, `metodo.md` y `base/`. Ninguna instrucción del método usa rutas absolutas, porque cada usuario tiene la carpeta sincronizada en un sitio distinto.

### Quién es el dueño

**El dueño por defecto de un área o de un proyecto nuevo es la persona desde cuya cuenta se abre la sesión.** Se propone su nombre al crear y solo se pregunta si en ese momento se asigna a otra persona. Un área o un proyecto sin dueño con nombre y apellido no se crea.

La cuenta de cada dueño queda escrita junto a su nombre en `guia.md`. Eso es lo que permite comprobar, y no solo suponer, que quien pide publicar es el dueño del proyecto. Si la identidad de la cuenta no está disponible, por ejemplo con otro modelo leyendo `metodo.md`, se pregunta el nombre y se anota de quién viene la petición.

### Independencia entre raíces

Un mismo trabajo puede tener conectada más de una raíz a la vez, o una raíz y el repo del plugin, y solo por una razón: ajustar la estructura o comparar cómo está montada cada organización. Nunca se conectan dos raíces para trabajar el contenido de una. Cada raíz sigue siendo de una sola organización: nada que se escriba en una raíz usa hechos, cifras, nombres o decisiones de otra raíz, ni del repo del plugin, y nada que se escriba en el repo del plugin usa hechos de una organización en particular, porque el plugin es idéntico para todas. Comparar la forma de dos raíces (¿tienen las mismas piezas?, ¿la misma cabecera?) no es tocar su contenido, y ese trabajo no se guarda dentro de ninguna de las dos. Lo que una organización guarda sobre otra, por ejemplo quien mantiene el método guardando el historial de una migración que hizo para un cliente, se limita a lo operativo de quien lo guarda: qué se entregó y cuándo, nunca el contenido del trabajo del cliente.

Eso fija dónde vive cada cosa cuando una organización adopta el método. **El registro de la migración es de quien migra**: las auditorías, los planes y los manifiestos van a su raíz, en un proyecto por organización nombrado por la organización y no por el trabajo. Cuentan lo que hizo el proveedor y hablan del sistema del que se migró, que la organización que estrena el método no usó nunca y no le dice nada.

En la raíz de la organización entra solo lo que su equipo necesita para operar, y entra donde se usa, no en un proyecto aparte: las decisiones recuperadas de su material anterior, cada una en el `decisiones.md` del proyecto al que pertenecen y marcadas como pendientes de confirmar; y el material confidencial que quedó fuera de alcance, con su fila en el `fuentes/enlaces.md` que corresponda. Nada más: su raíz no guarda rastro del sistema del que se migró, ni en las rutas, ni en el vocabulario, ni en los nombres de sus archivos.

### Permisos en Drive

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

**Un proyecto no se parte.** Sigue siendo uno, con un dueño, un `proyecto.md`, un `decisiones.md` y un `sesiones.md`. Lo que no puede leer todo el equipo va a `restringido/`, **una carpeta plana** con su propio `enlaces.md`. No repite dentro las carpetas del proyecto: un espejo cuesta más de mantener de lo que ordena, y lo que vive ahí suele ser un puñado de archivos. Si hace falta saber si uno de ellos es un entregable o material de taller, lo dice su cabecera.

En el `fuentes/enlaces.md` público queda la fila que dice que ese material existe y dónde está, nunca lo que dice. Sin ella nadie sabe que hay algo ni a quién pedirlo, que es lo mismo que busca el método al dejar visible el nombre de una carpeta restringida.

**Dónde escala.** En `restringido/` no entran nunca `proyecto.md`, `decisiones.md` ni `sesiones.md`. Si lo que hay que esconder es una decisión, el estado o el objetivo, el proyecto no se puede partir: se restringe entero.

**El nombre se ve.** Quien no tiene acceso ve la carpeta en gris, con su nombre, y un botón para solicitarlo que llega a quien administra. Por eso la carpeta de dentro de un proyecto se llama siempre `restringido` y no dice de qué trata. Las áreas y los proyectos se siguen listando en `guia.md` y en `area.md` con su nombre y su dueño, estén restringidos o no: el equipo tiene que poder saber que existen y a quién pedir acceso; lo que no puede es leerlos.

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

`guia.md` es de la organización y solo de ella: qué es la carpeta, qué áreas hay con su dueño y su cuenta, quién responde por el contexto, quién administra la carpeta compartida, las reglas propias de la casa y la receta para conectarse. Nada de lo que es igual en cualquier organización entra ahí: eso vive en `metodo.md`, que genera el plugin y nadie edita, y que lleva este contrato, el estilo y el índice de skills para que funcionen también con otro modelo o con quien abra la carpeta sin el plugin.

### Los archivos de `base/`

| Archivo | Qué contiene |
|---|---|
| `contexto.md` | Quién es la organización, criterios transversales, qué datos son sensibles |
| `glosario.md` | Vocabulario de la casa: siglas, nombres internos, qué significa cada cosa |
| `sistemas.md` | Una tabla con cuatro columnas: sistema, para qué, quién da acceso, antes de usarlo |

Los tres se leen a demanda, no al abrir sesión: `glosario.md` cuando aparece vocabulario de la casa, `sistemas.md` cuando el trabajo toca un sistema, `contexto.md` cuando la pregunta es sobre la organización. La sección 12 lo fija.

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

## Quién participa
Dueño: [nombre y apellido]
[Otras personas y su papel]
```

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
| `fuentes/enlaces.md` | Inmutable | Tabla de enlaces externos y de lo que está en `restringido/`. Solo existe si hay filas |

Los tres archivos de la raíz del proyecto y las tres carpetas existen siempre, aunque estén vacías. `sesiones.md` es obligatorio y lo escribe la skill de cierre de sesión, no el usuario.

### Qué separa un entregable del taller

Un proyecto produce dos cosas y solo una sale. La prueba para saber cuál es cada archivo cabe en una pregunta: **¿se lo puedo dar a alguien de fuera del proyecto?** Si la respuesta es sí, es un entregable. Si es no, es taller.

`entregables/` es lo que otra área puede consumir cuando esté vigente. `taller/` es todo lo demás que escribió el equipo para llegar hasta ahí: el inventario que hubo que levantar, las notas de una conversación, el análisis intermedio, el diagnóstico del que sale una propuesta, el encuadre de un trabajo que se absorbió. Es de la casa, se escribió en sesión y nadie lo va a leer fuera del proyecto.

La secuencia las ordena sin que haya que pensarlo: **`fuentes/` es lo que entra, `taller/` es donde se trabaja, `entregables/` es lo que sale.**

Sin esa separación, un proyecto con un diagnóstico largo y una propuesta corta acaba con un entregable de verdad y treinta archivos que no lo son en la misma carpeta, y el índice del área y la lectura de nivel 1 dejan de servir. El taller no lleva estado propio ni carpeta de borradores: sus archivos llevan la misma cabecera que cualquier otro, casi siempre en `borrador`.

En el taller **no se abren registros**. Las decisiones y las sesiones del proyecto, incluidas las que ocurren trabajando ahí dentro, van a `decisiones.md` y a `sesiones.md`, que son del proyecto entero. Lo único con forma de registro que puede vivir en el taller es material adoptado de otro sitio, congelado, al que no se le añaden entradas.

No hay carpeta de borradores. Un entregable a medias vive en `entregables/` con `estado: borrador`, y lo que todavía no es nada vive en la conversación hasta que merezca ser un archivo.

No hay carpeta aparte para binarios. Una presentación hecha directo en PowerPoint o Keynote, una hoja de cálculo hecha en Excel o Numbers, un PDF que nadie generó desde texto: lo que decide dónde va es quién lo produjo. Si lo hizo el equipo del proyecto, con las manos que sea, es producto suyo y va a `entregables/` con nombre en minúsculas y guiones, igual que cualquier otro entregable. Si vino de fuera, entra por `fuentes/` aunque el proyecto lo vaya a usar tal cual, y entonces el entregable es el documento que lo cita. No lleva cabecera propia porque el formato no la admite; su estado y de qué se construyó se anotan en `proyecto.md` o en la entrada de `decisiones.md` que lo produjo. El lugar donde vive la raíz de la organización ya previsualiza estos formatos, así que no hace falta sacarlos de la estructura para poder verlos.

### Estructura de `proyecto.md`

Fija, porque varias skills escriben en ella:

```markdown
# [Nombre del proyecto]

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

`Estado actual` y `Siguientes pasos` son las dos únicas secciones que reescribe el cierre de sesión. El resto cambia poco y solo a petición del dueño.

`Dueño`, en `Quién participa`, es el dueño de todo el proyecto: sus entregables, sus decisiones, quién pide publicar. Si un documento concreto tiene otro responsable, se dice en la primera línea del cuerpo de ese documento, no en la cabecera.

### Un proyecto cerrado

Cuando se cumple lo que decía `Terminado significa`, el dueño lo pide y `Estado actual` abre diciendo **«Proyecto terminado el AAAA-MM-DD»**. A partir de ahí el proyecto no evoluciona: sus archivos siguen donde están, con el estado que tengan, y su `Siguientes pasos` dice que no queda ninguno propio.

Lo que cambia es el índice. En el bloque `Proyectos` de su `area.md` **un proyecto cerrado ocupa una línea y no desglosa sus entregables**. El desglose existe para saber sobre qué se puede construir hoy; en un proyecto que ya no evoluciona solo añade líneas que nadie lee, y uno con quince entregables llega a ocupar más del índice que el resto del área junta. Quien necesite el detalle abre su `proyecto.md`, que sigue contándolo entero.

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

Una entrada tiene lo justo para entender qué se decidió y por qué sin abrir nada más. El análisis que respalda la decisión (opciones, tablas, cifras) no va en la entrada: va a un entregable del proyecto y la entrada lo cita en `Afecta a` o en `Por qué`.

`Afecta a` lleva rutas relativas al proyecto para lo que está dentro de él, y `area/proyecto` cuando la decisión toca a otro proyecto de la raíz. Cada destino admite detrás un paréntesis corto con la consecuencia concreta; sin él, quien recibe el aviso sabe que algo le toca pero no qué. Los destinos se separan con `·` y la línea no se parte en varias.

### Formato de `sesiones.md`

```markdown
## AAAA-MM-DD
Trabajamos en: …
Avances: …
Pendiente: …
```

Entradas nuevas arriba.

### Regla de histórico

Las entradas escritas antes de adoptar este formato se dejan tal cual; el formato aplica desde la siguiente entrada. La excepción es la migración: un registro que se acaba de crear al migrar sí se convierte, porque nadie lo ha consumido todavía.

### Aviso entre áreas

La carpeta no notifica a nadie. Por eso `Afecta a` puede nombrar proyectos de otras áreas: al abrir sesión se buscan, en los `decisiones.md` de la raíz, las líneas `Afecta a:` que nombren el proyecto activo. Es una búsqueda de un patrón de línea, no una lectura de archivos, y es la única operación que recorre la raíz entera al abrir. Al cerrar sesión, si una decisión afecta a otra área, se recuerda al usuario que avise a su dueño.

## 5. Cabecera

Todo `.md` empieza con estas tres claves y ninguna más, con dos excepciones: `guia.md` y `metodo.md`, que están hechos para leerse sin nada delante y empiezan directamente por el título, y el contenido de `fuentes/`, que es material y no se edita, así que añadirle una cabecera sería editarlo. El `enlaces.md` de `fuentes/` sí la lleva, porque ese lo escribimos nosotros.

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

**estado**, tres valores y nada más:

- `borrador`: no se puede consumir todavía. Da igual si está a medias, terminado esperando al dueño, o adoptado de otro sitio sin revisar
- `vigente`: aprobado, se puede construir encima
- `reemplazado`: superado. Requiere una cuarta clave, `reemplazado_por`, con la ruta del sustituto

El paso a `vigente` lo pide siempre el dueño del proyecto de forma explícita y tiene requisitos: los aplica la skill `revisar`. Ninguna otra skill cambia ese estado por su cuenta. Que un borrador esté a medias o terminado se dice en `Estado actual` de `proyecto.md`, que es un archivo vivo y sirve para eso; no hacía falta un estado para distinguirlo, y el que había no lo usaba nadie.

**actualizado**: fecha en formato `AAAA-MM-DD`, la del último cambio de contenido real.

**basado_en**: rutas relativas a la raíz de todo lo que se usó para escribir el archivo. Es lo que permite detectar que un entregable quedó desactualizado cuando cambia algo aguas arriba. Es obligatoria en los entregables y la escribe la skill, no la persona. Para material adoptado sin trazabilidad se permite la lista vacía `[]`, y `revisar` la pide completa antes de publicar. Los registros, las fuentes y los archivos de `base/` no llevan esta clave.

No hay clave de dueño. El dueño vive en `area.md` y en `proyecto.md`, en `Quién participa`. Si un documento concreto tiene otro responsable, lo dice la primera línea de su cuerpo.

Las claves van sin acentos ni eñes.

## 6. Nombres

Minúsculas, guiones en vez de espacios, sin acentos ni eñes, sin fechas ni números de versión, sin números de fase ni de etapa. `flujo-aprobacion.md`, no `Flujo de Aprobación v2 FINAL.md` ni `fase1-flujo-aprobacion.md`.

El nombre de un archivo es estable durante toda su vida. La versión la lleva Drive, el estado lo lleva la cabecera y el orden de las fases lo cuenta `proyecto.md`.

### El nombre de una carpeta compartida

La raíz es una carpeta compartida y su nombre se ve en Drive, así que ese sí lleva mayúsculas y espacios: `Acme`. Solo letras, números, espacios y guiones, y los acentos y las eñes que traiga el nombre propio. Ningún otro signo: el nombre de una carpeta compartida se escribe a mano muchas veces, al buscarla, al pedir acceso, al nombrarla en un correo, al usarla en la terminal o en un script, y cualquier signo que no esté en el teclado se copia mal, se escribe distinto cada vez y obliga a comprobar si una herramienta lo admite. Si una organización ya tiene una carpeta con un signo así, se propone renombrarla; el método no depende del nombre, porque ninguna instrucción usa rutas absolutas.

## 7. Qué es público

La superficie pública de un proyecto son `entregables/` y `decisiones.md`. Es lo único que otra área puede leer para construir encima, y solo si el entregable está `vigente`. `area.md` y `proyecto.md` también se leen desde fuera, porque son el índice que lleva hasta esa superficie.

`sesiones.md`, `taller/`, `fuentes/` y todo lo que está restringido son taller privado. Nadie de fuera del área los lee ni los cita en `basado_en`. Un entregable sí cita el taller de su propio proyecto, que es de donde salió.

Dentro de la misma área, un entregable puede citar en `basado_en` una fuente de otro proyecto del área, siempre la original y nunca una copia: un export vive en un solo `fuentes/` y los demás lo citan por su ruta. Entre áreas no se citan fuentes, solo entregables vigentes y decisiones.

### Lo restringido se cita en una sola dirección

Un archivo restringido puede citar en `basado_en` lo que quiera de lo que sí lee todo el equipo: entregables vigentes, decisiones, `base/`. Al revés, nunca. Nada que lea todo el equipo cita, nombra ni resume un archivo restringido, porque quien lo lea no va a poder abrirlo y porque la cita misma ya cuenta algo de lo que hay dentro. La única excepción es la fila de `fuentes/enlaces.md`, que dice que un material existe y dónde está, no lo que dice.

Vale igual para `Afecta a`: una decisión restringida puede apuntar a cualquier proyecto, y una decisión que lee todo el equipo apunta a un área o a un proyecto restringido por su nombre, que ya está listado, nunca a uno de sus archivos.

Lo aprendido dentro de un área restringida vuelve a la memoria común **reescrito, no movido**: se publica como entregable propio de un proyecto que lee todo el equipo, con lo que sirve para la próxima vez y sin los datos, las cifras ni los nombres de donde salió. Un archivo restringido no sale nunca de donde está; un aprendizaje sí cambia de sitio, y lo hace escribiéndolo de nuevo.

## 8. Rotación

Cuando un registro pasa de unas 1.500 líneas o cambia el año, se archiva con el año en el nombre (`sesiones-2026.md`) y se abre uno nuevo. Lo hace la skill de cierre de sesión, sin preguntar.

## 9. Lo que no existe en este sistema

- Una carpeta `metodo/` dentro de la raíz. El método vive en el plugin y en `metodo.md`
- Un archivo de reglas propias en `base/`. Lo propio de la organización vive en `guia.md`
- Una carpeta de plantillas en la raíz. Las dos plantillas del método viven en el plugin
- `AGENTS.md` ni ningún archivo de instrucciones para la IA dentro de la raíz. Las instrucciones son las skills y el texto que cada persona pega en su proyecto
- Índices, inventarios o resúmenes mantenidos a mano o por otra herramienta. El único índice es el bloque `Proyectos` de cada `area.md`, es derivado y lo escriben las skills
- El almacén de datos de una aplicación dentro de la raíz. Lo escribe la aplicación sola y nadie responde por lo que hay dentro
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
- Estado del método guardado en la memoria del modelo ni en la memoria de proyecto de Claude, que hoy sí existe como función y viene activada. Es por persona y por proyecto, no se comparte con el equipo, no se audita, no se ve, y puede contradecir un archivo sin que nadie lo note. Si un dato importa, está en un `.md`
- Cualquier archivo que el usuario tenga que rellenar a mano

## 10. Prohibiciones

Valen para todas las skills y no se repiten en ninguna. Cada skill añade las suyas, que son las de su trabajo concreto.

1. No marcar nada como `vigente`. Solo lo hace `revisar`, y solo cuando lo pide el dueño del proyecto.
2. No editar una entrada ya escrita de `decisiones.md` o de `sesiones.md`, ni para corregir una errata. Un registro solo crece.
3. No registrar una decisión que el usuario no confirmó en esta sesión.
4. No escribir en `guia.md`, en `base/`, en `metodo.md` ni en la carpeta de otra área. Desde la sesión de otra área se prepara el texto y se le pasa a quien responde.
5. No tocar archivos fuera del proyecto activo, salvo la línea de ese proyecto en el bloque `Proyectos` de su `area.md`.
6. No leer `sesiones.md`, `taller/`, `fuentes/` ni lo restringido de otra área. Son taller privado y no responden a nadie de fuera.
7. No escribir en un archivo que lee todo el equipo la ruta ni el contenido de algo restringido, aunque sea resumido. Hacia fuera solo van el nombre del área o del proyecto, que ya están listados, y la fila de `enlaces.md`.
8. No guardar en `fuentes/` un material con indicios de información confidencial sin haberlo dicho y preguntado antes, ni mover nada a `restringido/` sin que el usuario lo confirme.
9. No guardar fuera de `fuentes/` material que llegó de fuera del equipo del proyecto, aunque venga terminado y listo para usarse.
10. No copiar a este `fuentes/` una fuente que ya existe en otro proyecto del área. Se cita la original por su ruta.
11. No crear un área ni un proyecto sin dueño con nombre y apellido.
12. No rellenar un hueco con una suposición razonable. Un hueco se marca como hueco, y "no consta" es una respuesta válida.
13. No escribir una cifra sin fecha ni fuente.
14. No poner número de fase, fecha ni versión en el nombre de un archivo o de una carpeta.
15. No crear carpetas que la estructura no contempla, ni un `AGENTS.md`, ni un índice a mano, ni una carpeta de borradores.
16. No dejar dentro de la raíz el almacén de datos de una aplicación, ni apuntar una aplicación a que escriba ahí.
17. No borrar un entregable superado. Pasa a `reemplazado` con `reemplazado_por`, porque alguien puede tenerlo citado.
18. No llevar a la raíz de una organización ningún hecho que venga de otra raíz conectada en la misma sesión, aunque sea para comparar.
19. No guardar estado del método en la memoria del modelo. Si un dato importa, va a un `.md` de la carpeta.
20. No dejar en `entregables/` lo que no puede salir del proyecto. Si no se lo puedo dar a nadie de fuera, va a `taller/`.
21. No abrir un `decisiones.md` ni un `sesiones.md` dentro de `taller/`. Los registros del proyecto son los de su raíz.

## 11. Actualización del método

El método se actualiza publicando una versión nueva del plugin. La versión vive en el plugin y en la primera línea legible del `metodo.md` de cada raíz. Al abrir sesión se comparan las dos y se avisa si la raíz se quedó atrás; ponerla al día es volver a generar `metodo.md` desde el plugin. Nadie edita `metodo.md` dentro de la carpeta de una organización.

Dos scripts acompañan al plugin y nadie tiene que recordar sus pasos. `release.sh` publica una versión: sube el número en los tres sitios donde vive, comprueba que este documento declare la mayor.menor, regenera `metodo.md` y dice qué queda por hacer a mano. `verificar.sh` se pasa sobre la raíz de una organización: comprueba la estructura, los nombres, las cabeceras, los estados y que el bloque `Proyectos` de cada área liste todo lo que tiene que listar. No lee el contenido de ningún archivo y no escribe nada.

## 12. Cómo se lee

Nunca se lee todo, y casi nunca se lee `base/`. Al abrir, se carga lo justo para saber qué existe y dónde está cada cosa; el resto entra cuando el trabajo del día lo pide, y por su nombre.

**Nivel 0, siempre, y nada más que esto.** Tres lecturas cortas:

1. La primera línea de `metodo.md`, para la versión de la raíz.
2. `guia.md` entero. Es el mapa: qué áreas hay, quién responde por cada una y con qué cuenta, quién mantiene el contexto, quién administra la carpeta y las reglas propias de la casa. Cabe en una pantalla.
3. El bloque `Proyectos` del `area.md` que toca. Dice qué proyectos hay y qué entregables vigentes tiene cada uno.

Con eso ya se sabe qué existe, de quién es y dónde está. Todo lo demás se pide por su nombre.

**Nivel 1, del proyecto activo, una vez que se sabe cuál es.** `proyecto.md`; las cinco entradas más recientes de `decisiones.md`; las tres más recientes de `sesiones.md`; y las cabeceras de `entregables/`, nunca su cuerpo.

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

La única operación que recorre la raíz entera es la búsqueda de las líneas `Afecta a:` que nombran el proyecto activo, al abrir sesión. Busca un patrón de línea, no lee archivos, y las carpetas restringidas sin acceso fallan y se saltan.

Si el camino lleva a una carpeta restringida sin acceso, la lectura falla. Eso no es un error ni un hueco: se dice qué área o qué proyecto es y quién es su dueño, y ahí se para. No se deduce lo que hay dentro por los nombres de las carpetas ni se da por hecho que no hay nada.

## 13. Cowork y programadores

**Cowork.** El uso principal del método es Claude Cowork con la raíz conectada y el plugin instalado. El montaje tiene dos reglas.

**Un proyecto por persona**, nombrado por su área. Es lo que hace que la línea del área en las instrucciones signifique algo y que el aviso de «esto le toca a otra área» tenga a quién señalar.

**Se conecta la raíz completa, nunca la carpeta de un área.** `guia.md`, `metodo.md` y `base/` viven en la raíz; la lectura cruza áreas; `consulta` busca en lo que produjo cualquier área y `sesion` avisa de las decisiones de otras que afectan al proyecto. Conectada solo un área, el método se rompe en la primera llamada. Conectar de más no abre ningún riesgo: quién puede leer y escribir dónde lo fijan los permisos de las carpetas, no el alcance de la conexión, y lo restringido sigue restringido dentro de una carpeta conectada.

Un proyecto de Claude admite una sola carpeta, que se elige al crearlo y no se puede ampliar después. Es la raíz, y no hace falta ninguna más. Si se eligió mal, se crea otro proyecto.

El texto para pegar en las instrucciones del proyecto no nombra skills, porque Claude las elige solo:

```
Este proyecto trabaja sobre una memoria de trabajo permanente: la carpeta conectada, que sigue el método del plugin `memoria`. Aplícalo en todo lo que hagas aquí, y no guardes nada en tu memoria: si un dato importa, va a un archivo de la carpeta.
Lee `guia.md` al empezar y no leas nada más hasta saber qué necesitas: la carpeta se lee por niveles y `guia.md` dice dónde está cada cosa.
Escribe solo donde te haya dicho que trabajo, y en ningún otro sitio de la carpeta; si no te lo he dicho, pregúntamelo antes de escribir nada. Si algo le toca a otra área, dímelo y yo se lo pido a su dueño.
No des por aprobado ningún documento ni edites lo ya registrado en decisiones o sesiones.
Si una carpeta no se deja leer, está restringida: dímelo y sigue con lo que sí puedas leer, sin suponer lo que hay dentro.
Antes de guardar algo, pregúntate si alguien más lo va a leer y si contiene datos que no todos deben ver. Si algo parece confidencial, avísame y propón moverlo; no lo muevas tú.
```

El bloque es idéntico en cualquier organización: no nombra a ninguna, no lleva huecos que rellenar y nada de una raíz concreta entra en él. Lo propio de una raíz vive en `guia.md`, que la segunda línea manda leer. Debajo del bloque cada persona añade una línea suya diciendo dónde escribe, su área, sus áreas o `base/`; esa línea es de ella, no del método. Si falta, la IA pregunta antes de escribir en vez de suponer.

La skill `nuevo` escribe todo esto en `guia.md` como una receta de cinco pasos: crear el proyecto con el nombre del área, instalar el plugin desde el marketplace, conectar la raíz, pegar el texto y comprobar con «abre sesión en...», para que cada persona lo monte sola sin preguntarle a nadie.

**Otros modelos.** Gemini u otro modelo sin plugin leen `metodo.md`. Contiene este contrato, el estilo y el índice de skills, así que saben qué reglas seguir aunque no puedan ejecutarlas como skills.

**Programadores.** El `CLAUDE.md` de un repositorio enlaza la carpeta del proyecto en la raíz (`area/proyecto`). Las decisiones de código que dependen de un diseño se anclan en `decisiones.md` y en los entregables vigentes de ese proyecto, no en comentarios del código. Para saber qué se decidió antes de escribir código, usan la skill `consulta`.
