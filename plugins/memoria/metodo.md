# Método de trabajo · versión 1.22.0 · huella 31e0bb8 · generado desde el plugin memoria, no se edita a mano

Este archivo reúne el contrato del método, las normas de estilo y el índice de skills del plugin `memoria`. Sirve a quien trabaja con Gemini u otro modelo sin el plugin, y a quien abre la carpeta sin IA delante. Para ponerlo al día se vuelve a generar desde el plugin y se copia a la raíz.

---

# Convenciones

Contrato base del método. Si una skill contradice algo de aquí o de sus anexos, manda el contrato. Cuatro anexos viven junto a este archivo. `escribir.md` reúne lo que hace falta para escribir (estructura de `area.md` y `proyecto.md`, formatos de los registros, cabecera, rotación y prohibiciones) y se carga antes de cualquier escritura en la carpeta; para cerrar sesión, registrar una premisa o escribir el `Estatus` de un área basta con él, y para crear, guardar o publicar un documento, mover, migrar o montar se carga además este archivo. Los otros tres se leen solo cuando hacen falta: `raices.md` (varias raíces, traspasos, registro de una migración), `montaje.md` (montaje, publicación, bloque de instrucciones, programadores) y `sin-consola.md` (cómo se lee y se escribe cuando la raíz está conectada pero el shell de la computadora no la ve).

Versión del método: **1.22**

## 1. Las tres capas de propiedad

| Capa | Quién responde | Qué contiene |
|---|---|---|
| El plugin y `metodo.md` | Solo el responsable del método | Cómo se trabaja. Idéntico en todas las organizaciones |
| `guia.md` y `base/` | Un único responsable de contexto | Quién es la organización, cómo se organiza, qué sistemas usa, qué reglas propias tiene |
| Cada área | El responsable del área | El trabajo real |

Nadie responde fuera de su capa, y nadie pide que se escriba en la capa de otro. Un área lee `base/` y `metodo.md`, nunca los modifica. Las skills escriben en nombre de quien las usa y respetan las mismas capas. Una capa no cambia porque algo esté restringido: el responsable de un área lo es también de lo restringido dentro de ella.

### Quién teclea, y por dónde entra lo de fuera

Responder por un archivo y escribirlo son dos cosas distintas. **Lo que hay en una carpeta de trabajo lo escribe la IA en sesión**: `guia.md`, `base/`, los `area.md` y los `proyecto.md`, los registros y los entregables. Las personas deciden qué dice cada archivo y lo piden, la IA es la que teclea. `metodo.md` no es excepción: lo genera un script disparado desde una sesión.

De ahí sale el valor de la carpeta: todo lo que hay dentro entró por el método y alguien respondió por ello. En cuanto entra material que nadie puso a propósito, un almacén que una aplicación escribe sola, un archivo copiado a mano o un índice mantenido aparte, la carpeta deja de ser fiable y la IA lee ruido como si fuera contexto.

**La única puerta para el material que llega de fuera es `fuentes/`**, la del proyecto al que pertenece. De fuera es lo que no produjo el equipo del proyecto: un export, un PDF de un tercero, una transcripción, un documento que mandó un cliente. Entra a `fuentes/`, no se edita, y lo que se construya con él se escribe aparte y lo cita.

Los formatos que la IA no puede teclear, una presentación o una hoja de cálculo, son la excepción a quién escribe y no a por dónde se entra: los arma el equipo del proyecto con su herramienta y son producto suyo; si vinieron de fuera entran por `fuentes/` como cualquier otro material. La sección 3 lo detalla.

**Lo que se produce para un proyecto se guarda en su carpeta en cuanto existe**, no al cerrar la sesión: un documento, un PDF, una propuesta o un análisis van a `entregables/`, o a `taller/` si no salen del proyecto, con `estado: borrador`, aunque falte pulirlos, y aunque los haya hecho otra herramienta y no la skill `entregable`. Lo que solo vive en la conversación se pierde con ella y nadie más lo ve. Cerrar la sesión es registrar lo que pasó, no guardar lo que se hizo. Por la misma razón, una tarea programada que escribe en la carpeta algo más que fechas de pasos deja su línea en el `sesiones.md` del proyecto, con «(tarea)» en el título: si no, su trabajo parece una sesión que nadie cerró.

**«Claude outputs» no es parte de la memoria.** Es la carpeta donde la app de Claude guarda por su cuenta lo que produce cuando trabaja sobre una carpeta conectada. Lo que hay ahí no tiene proyecto, nadie lo encuentra y el tablero no lo ve como trabajo de nadie. Lo que se haga para un proyecto se guarda directamente en ese proyecto; si la app lo dejó en «Claude outputs», se mueve a su proyecto en cuanto existe. La sesión que lo produjo lo recoge al cerrar; la apertura de cada conversación del responsable de contexto lista lo que quede y propone colocarlo (a los demás no se les dice al abrir), y se ordena también con la frase «ordena Claude outputs» (skill `donde-va`). Con el plugin, un hook no deja escribir ahí desde Claude y dice dónde va, y si algo aparece igual (un comando, la propia app) pide moverlo en ese momento; sin consola, cuando la carpeta no está montada en la computadora, quedan el cierre de la sesión que lo produjo y la apertura del responsable de contexto. `verificar.sh` y el tablero cuentan los archivos que siguen ahí.

Ninguna carpeta de trabajo aloja el almacén de datos de una aplicación. Lo escribe la aplicación sola, crece por su cuenta y nadie responde por lo que hay dentro.

La migración es la excepción declarada. El material que se adopta al migrar no llega de fuera: es el trabajo anterior de la propia organización, y entra donde le toque con `estado: borrador` y con la trazabilidad que se pueda reconstruir, salvo lo que su responsable en el origen pida publicar al migrar. Lo que en el origen ya era material de entrada entra por `fuentes/` como en cualquier proyecto. Lo detalla la skill `migrar`.

Es norma, no candado. Nada impide abrir un archivo y editarlo a mano, y a veces hay que hacerlo; detectar lo que entró por otro camino es trabajo de la skill `revisar`. La propiedad no cambia: quien responde por un archivo sigue siendo su responsable, lo que cambia es la mano que escribe.

La raíz es la carpeta que contiene `guia.md`, `metodo.md` y `base/`. Ninguna instrucción del método usa rutas absolutas, porque cada usuario tiene la carpeta sincronizada en un sitio distinto.

**La carpeta se lee y se escribe por su copia en la computadora**, con las herramientas de la carpeta conectada, y nunca por un conector de Google Drive u otro servicio en la nube, ni para buscar ni para escribir, aunque esté conectado. Por el conector no se ven la estructura, las cabeceras ni las fechas de los archivos, y lo que se escribe por ahí puede acabar en otro formato o fuera de su sitio. Si la carpeta no aparece entre las conectadas, se pide añadirla. **La única excepción es leer sin carpeta:** una sesión que no tiene ninguna carpeta conectada, como una desde el teléfono o la web, puede leer una raíz que vive en Google Drive por el conector de Drive, por niveles como siempre, y no escribe nada en ella; lo que salga de esa sesión se guarda como nota en la cola del tablero de la persona y lo registra la siguiente sesión con la carpeta (skill `sesion`, «Sin carpeta: solo lectura»). Con la carpeta conectada, el conector no se usa para la memoria, con una excepción: **sin consola** (la carpeta está conectada pero el shell de la computadora no la monta, como pasa con Google Drive en Windows), se lee y se escribe con las herramientas que traen y escriben archivos, y lo único que pasa por el conector es crear carpetas, mover, renombrar y mandar a la papelera (y localizar lo que se mueve), que esas herramientas no hacen; nunca leer ni escribir contenido. Cómo se sabe y cómo se trabaja así lo dice el anexo `sin-consola.md`. El conector sirve además para leer los permisos de la carpeta y compararlos con lo que declara la raíz, en la sesión del responsable de contexto, y para aplicar lo que deja (compartir como «Lector» o «Colaborador», marcar el acceso limitado) en la sesión de quien administra y con su sí (skill `sesion`, anexo `permisos.md`), y para lo que no es la memoria, como un documento que alguien comparte, y si eso entra a la memoria lo hace por `fuentes/`.

### Quién es el responsable

**El responsable por defecto de un área o de un proyecto nuevo es la persona desde cuya cuenta se abre la sesión.** Se propone su nombre al crear y solo se pregunta si en ese momento se asigna a otra persona. Un área o un proyecto sin responsable con nombre y apellido no se crea.

Hasta la 1.21 el responsable se llamaba «dueño», y así lo dicen todavía las raíces sin migrar (`Dueño:` en `Quién participa`, la columna «Dueño» de `guia.md`): los scripts y las skills leen las dos palabras durante la 1.22 y escriben solo «Responsable».

La cuenta de cada responsable queda escrita junto a su nombre en `guia.md`, y la del responsable de contexto, entre paréntesis en la línea «Contexto común» de «Quién responde por qué», para que se le reconozca aunque no sea responsable de ningún área. Eso es lo que permite comprobar, y no solo suponer, que quien pide publicar es el responsable del proyecto. Si la identidad de la cuenta no está disponible, por ejemplo con otro modelo leyendo `metodo.md`, se pregunta el nombre y se anota de quién viene la petición.

### Quién colabora

Un área tiene un solo responsable, pero pueden escribir en ella más personas: **quienes colaboran**. Se declaran en la misma celda Cuenta de la tabla de áreas de `guia.md`, después de la cuenta del responsable: `responsable@ejemplo.com · colabora: ana@ejemplo.com, luis@ejemplo.com`. Las cuentas se comparan enteras. Quien colabora en un solo proyecto, y no en toda el área, se declara en `Quién participa` de ese `proyecto.md`, con una línea `Colabora: Nombre Apellido (correo), Nombre Apellido (correo)`; la cuenta entre paréntesis es lo que permite comprobar quién escribe. La celda de `guia.md` la escribe el responsable de contexto; la línea del proyecto, la sesión del responsable del área.

| Puede | El responsable | Quien colabora |
|---|---|---|
| Abrir y cerrar sesión en los proyectos donde colabora, y escribir su bitácora | sí | sí |
| Guardar borradores en `entregables/`, `taller/` y `fuentes/` | sí | sí |
| Registrar las decisiones de su propio trabajo, con su nombre en `Decidió` | sí | sí |
| Poner al día `Estatus` y `Siguientes pasos` del proyecto al cerrar | sí | sí |
| Publicar un entregable como `vigente` | sí | no |
| Escribir el `Estatus` del área | sí | no |
| Crear o cerrar un proyecto, o declarar quién colabora en él | sí | no |

Una decisión de quien colabora vale como cualquier otra. Si el responsable no está de acuerdo, la reemplaza con una decisión suya o la cuestiona (sección 4), nunca la edita. En Drive, quien colabora en el área tiene escritura en la carpeta del área; quien colabora en un proyecto, solo en la carpeta de ese proyecto.

**Dos personas en el mismo proyecto no cierran sesión a la vez.** La carpeta no bloquea a nadie: si dos cierres escriben a la vez, el segundo puede pisar al primero. Por eso el cierre compara, antes de escribir, la hora de la última escritura de `proyecto.md`, `decisiones.md` y `sesiones.md` con la que vio al abrir, y si cambió, relee y suma lo suyo a lo que encontró (skill `sesion`, anexo `cerrar.md`). Reduce el riesgo, no lo elimina: lo que otra persona escribió y la carpeta compartida aún no bajó a esta computadora no se ve.

La carpeta tampoco impide que quien colabora edite la línea `Colabora:` de un proyecto, porque escribe en la misma carpeta. Las skills no la tocan desde su sesión; lo que de verdad decide quién escribe son los permisos de la carpeta compartida.

### Independencia entre raíces

Se trabaja en una raíz a la vez: con más de una conectada, antes de leer o escribir se pregunta en cuál, cada escritura dice en qué raíz se hace y cambiar de raíz se anuncia. Nada que se escriba en una raíz usa hechos de otra, ni del repo del plugin, salvo por un traspaso que la persona pide y confirma pieza a pieza; y el repo del plugin no guarda hechos de ninguna organización. Cómo es un traspaso y dónde vive el registro de una migración lo dice `raices.md`, junto a este archivo, que se lee con más de una raíz conectada, cuando se pide un traspaso y al migrar.

### Permisos en la carpeta compartida

Valen para cualquier sistema de carpetas (Drive, OneDrive, iCloud…); el ejemplo de siempre es Drive, donde el acceso limitado se pone desde la web.

- Lectura de toda la raíz para todo el equipo, salvo lo restringido.
- Escritura en la carpeta de un área solo para su responsable y quienes colaboran en ella, y en la de un proyecto, además, para quienes colaboran en ese proyecto (sección 1, «Quién colabora»).
- Escritura en `guia.md` y en `base/` solo para el responsable de contexto. La IA escribe los dos, y solo puede hacerlo en la sesión de esa persona; desde la sesión de otra área prepara el texto y se lo pasa.
- Administrar la carpeta compartida es de quien dirige la organización, o de una persona de su total confianza, y de nadie más. Quien administra puede quitar cualquier restricción, así que todo lo que sigue se apoya en esa lista.

### Lo restringido

Lo que no puede leer todo el equipo se marca en la carpeta que lo contiene, ahí donde ya está, con el acceso limitado de Drive: esa carpeta deja de heredar los permisos de arriba y solo entra quien esté añadido a ella. No hay carpeta compartida aparte, ni espejos, ni rutas alternativas. Una organización tiene una sola carpeta compartida.

Se restringe en tres sitios y en ninguno más:

| Qué | Dónde se marca |
|---|---|
| Un área entera | La carpeta del área |
| Un proyecto entero, dentro de un área que sí lee todo el equipo | La carpeta del proyecto |
| Parte de un proyecto | `<proyecto>/restringido/` |

Lo que decide dónde va cada cosa es quién puede leerla, no de qué trata: da igual que sea una cuenta de cliente, recursos humanos, finanzas o legal.

**Un proyecto no se parte.** Sigue siendo uno, con un responsable, un `proyecto.md`, un `decisiones.md` y un `sesiones.md`. Lo que no puede leer todo el equipo va a `restringido/`, **una carpeta plana** con su propio `inventario.md`. No repite dentro las carpetas del proyecto. Si hace falta saber si uno de ellos es un entregable o material de taller, lo dice su fila en ese `inventario.md`.

En el `fuentes/inventario.md` público queda la fila que dice que ese material existe y dónde está, nunca lo que dice. Sin ella nadie sabe que hay algo ni a quién pedirlo, que es lo mismo que busca el método al dejar visible el nombre de una carpeta restringida.

**Dónde escala.** En `restringido/` no entran nunca `proyecto.md`, `decisiones.md` ni `sesiones.md`. Si lo que hay que esconder es una decisión, el estado o el objetivo, el proyecto no se puede partir: se restringe entero.

**El nombre se ve.** Quien no tiene acceso ve la carpeta en gris, con su nombre, y un botón para solicitarlo que llega a quien administra. Por eso la carpeta de dentro de un proyecto se llama siempre `restringido` y no dice de qué trata. Las áreas y los proyectos se siguen listando en `guia.md` y en `area.md` con su nombre y su responsable, estén restringidos o no: el equipo tiene que poder saber que existen y a quién pedir acceso; lo que no puede es leerlos. Y lo dicen: un área restringida lleva «Restringida» en su columna «Acceso» de `guia.md`, y una que lee todo el equipo, «Abierta»; la columna «Quién la lee» dice quién la lee, en llano. En una `guia.md` sin migrar, que no tiene «Acceso», vale la regla de hasta la 1.21: «Restringida» al inicio de «Quién la lee» (si la palabra aparece en otra parte de la celda sin negarla, también cuenta: ante la duda, se trata como restringida). Un proyecto restringido empieza su línea del bloque `Proyectos` de su `area.md` por esa palabra: `` - `slug/` — restringido: … ``. Decir en la línea que una parte del proyecto está en `restringido/` no lo declara restringido. Es lo único que deja ver que algo está restringido a quien sí puede leerlo, por ejemplo a la herramienta que genera un tablero con la cuenta de quien administra la carpeta.

Si una organización necesita que ni el nombre de un área se vea, o que quien administra la carpeta compartida no pueda ver algo, ese caso se resuelve con una carpeta compartida aparte y se escribe en las reglas propias de `guia.md`.

Poner y quitar el acceso limitado solo lo puede hacer quien administra la carpeta compartida. Lo hace desde la web, o lo aplica Claude en su sesión con el conector de Google Drive, con su sí a la lista exacta de cambios (skill `sesion`, anexo `permisos.md`). Ninguna otra skill lo hace: dicen qué carpeta hay que limitar y para quién, y esperan.

### Material sensible dentro de un proyecto que lee todo el equipo

Un archivo con datos personales, facturación, contratos o credenciales no se guarda en `fuentes/`: se guarda en `restringido/` del mismo proyecto, y en el `fuentes/inventario.md` público queda una fila con qué es, dónde está y qué tener presente al usarlo. No obliga a restringir el proyecto entero.

La IA participa en esa decisión. Cuando una skill detecta indicios de información sensible en un material (nombres junto a RFC, CURP o NSS, facturación por cliente, contratos, contraseñas, datos de salud, salarios), lo dice y propone llevarlo a `restringido/`. El usuario decide si lo es o no. Nada se mueve sin que el usuario lo confirme.

Ese material se lee igual que `fuentes/`: es privado del proyecto y no se cita en `basado_en` salvo por su fila de `inventario.md`.

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
        inventario.md   (opcional)
      restringido/      (opcional: lo que no puede leer todo el equipo)
        inventario.md
```

Tres niveles: área, proyecto, carpeta del proyecto. Un cuarto nivel significa que ahí había dos proyectos, con una excepción: dentro de `entregables/`, `taller/` y `fuentes/` se permite **un** nivel de agrupación cuando hay material suficiente para que la lista deje de leerse; el nombre de la subcarpeta sigue la convención de nombres y no lleva número de fase. Antes de crearla vale la pena probar con el asunto por delante del nombre del archivo, que agrupa igual en el listado y no añade nivel. `restringido/` no admite ninguno: es plano.

`guia.md` es de la organización y solo de ella: qué es la carpeta, qué áreas hay con su responsable, su cuenta, quién las lee y su acceso, quién responde por el contexto, quién administra la carpeta compartida, las reglas propias de la casa y la receta para conectarse, y su zona horaria en una línea «Zona horaria:» si no es la de Ciudad de México, la que usan las fechas de la sesión y del tablero; y, si alguien entra a Drive con otra cuenta que la de la tabla, una línea «En Drive: cuenta@claude es cuenta@drive» en «Quién responde por qué», que usa la revisión de permisos. Su título es «<Organización> · esta carpeta», y **el nombre de la organización**, el que usan el aviso de arranque y el tablero, es lo que va antes del «·». Nada de lo que es igual en cualquier organización entra ahí: eso vive en `metodo.md`, que genera el plugin y nadie edita, y que lleva este contrato, el estilo y el índice de skills para que funcionen también con otro modelo o con quien abra la carpeta sin el plugin.

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
- P3 · Se vende en México y en Estados Unidos · Confirmó: Nombre Apellido · 2027-01-10 · Reemplaza P1
```

El identificador `P<n>` es correlativo y no se reutiliza. Una premisa que cambia no se corrige: se añade otra con `Reemplaza P<n>`, y la anterior queda como historia (las anteriores a la 1.22 dicen `Reemplaza a P<n>`, y se leen igual). Una premisa se cita como `premisa P<n>` desde una decisión, un entregable o un cuestionamiento (sección 4).

Las reglas propias de una organización no llevan archivo: van en `guia.md`, que es donde vive todo lo suyo. Son las que este contrato no puede prever, como un tipo de dato adicional que cuenta como confidencial, una convención de nombres para las áreas o vocabulario que conviene fijar antes de que cada quien lo escriba distinto. No pueden cambiar ni contradecir nada de lo que dice este documento; si alguna lo hace, manda este documento y se avisa al responsable de contexto.

Las dos plantillas del método, brief y comparativo, viven en el plugin, dentro de la skill `nuevo`. No se copian a la raíz.

### Estructura de `area.md`

Fija, porque varias skills leen y escriben en ella. Está en `escribir.md`, junto a este archivo, con lo que dice cada sección: el `Estatus`, el bloque `Proyectos`, que es el índice de contexto del área, y `Quién participa`, donde vive el responsable.

## 3. Los archivos de un proyecto

| Archivo | Tipo | Qué contiene |
|---|---|---|
| `proyecto.md` | Vivo | Estatus, objetivo, alcance, siguientes pasos, quién participa |
| `decisiones.md` | Registro | Qué se decidió, cuándo, por qué, qué se descartó y a qué afecta |
| `sesiones.md` | Registro | En qué se trabajó cada día y qué se avanzó |
| `entregables/` | Vivo | El producto del proyecto, en cualquier estado |
| `taller/` | Vivo | Lo que el equipo escribe para llegar al producto y no es el producto |
| `fuentes/` | Inmutable | Insumos crudos: exports, PDFs, transcripciones, material sin clasificar |
| `fuentes/inventario.md` | Registro | Tabla de lo que llegó de fuera y no vive en la carpeta, y de lo que está en `restringido/`: se le añaden filas, las que hay no se editan. Solo existe si hay filas |

Los tres archivos de la raíz del proyecto y las tres carpetas existen siempre, aunque estén vacías. `sesiones.md` es obligatorio y lo escribe la skill de cierre de sesión, no el usuario.

### Qué separa un entregable del taller

Un proyecto produce dos cosas y solo una sale. La prueba para saber cuál es cada archivo cabe en una pregunta: **¿se lo puedo dar a alguien de fuera del proyecto?** Si la respuesta es sí, es un entregable. Si es no, es taller.

`entregables/` es lo que otra área puede consumir cuando esté vigente. `taller/` es todo lo demás que escribió el equipo para llegar hasta ahí: el inventario que hubo que levantar, las notas de una conversación, el análisis intermedio, el diagnóstico del que sale una propuesta, el encuadre de un trabajo que se absorbió. Es de la casa, se escribió en sesión y nadie lo va a leer fuera del proyecto.

La secuencia las ordena sin que haya que pensarlo: **`fuentes/` es lo que entra, `taller/` es donde se trabaja, `entregables/` es lo que sale.**

El taller no lleva estado propio ni carpeta de borradores: sus archivos llevan la misma cabecera que cualquier otro, casi siempre en `borrador`.

En el taller **no se abren registros**. Las decisiones y las sesiones del proyecto, incluidas las que ocurren trabajando ahí dentro, van a `decisiones.md` y a `sesiones.md`, que son del proyecto entero. Lo único con forma de registro que puede vivir en el taller es material adoptado de otro sitio, congelado, al que no se le añaden entradas.

No hay carpeta de borradores. Un entregable a medias vive en `entregables/` con `estado: borrador`, y lo que todavía no es nada vive en la conversación hasta que merezca ser un archivo.

No hay carpeta aparte para binarios. Una presentación hecha directo en PowerPoint o Keynote, una hoja de cálculo hecha en Excel o Numbers, un PDF que nadie generó desde texto: lo que decide dónde va es quién lo produjo. Si lo hizo el equipo del proyecto, con las manos que sea, es producto suyo y va a `entregables/` con nombre en minúsculas y guiones, igual que cualquier otro entregable. Si vino de fuera, entra por `fuentes/` aunque el proyecto lo vaya a usar tal cual, y entonces el entregable es el documento que lo cita. No lleva cabecera propia porque el formato no la admite; su estado y de qué se construyó se anotan en la entrada de `decisiones.md` que lo produjo, o en el `Estatus` del proyecto. El lugar donde vive la raíz de la organización ya previsualiza estos formatos, así que no hace falta sacarlos de la estructura para poder verlos.

### Estructura de `proyecto.md`

Fija, porque varias skills escriben en ella. Está en `escribir.md`, junto a este archivo, con el `Estatus`, para quien no va a leer más, y con lo que cambia cuando el proyecto se cierra.

### Los nombres reservados solo existen en su sitio

`proyecto.md`, `decisiones.md`, `sesiones.md` y `area.md` solo existen donde el método los pone. Todo lo que se adopte y los traiga se renombra a lo que de verdad es, porque un archivo llamado `proyecto.md` promete estar vivo y un `decisiones.md` promete ser un registro que solo crece y que nadie edita, y fuera de su sitio ninguna de las dos cosas es cierta.

El caso que más lo pide es un proyecto que se pliega dentro de otro, cuando dos trabajos dejan de ser distintos y pasan a ser el mismo. Su encuadre entra al `taller/` como un documento más. Sus registros **se funden** con los del proyecto que recibe, o entre sí si se absorben varios a la vez, copiando las entradas tal cual y añadiendo a cada encabezado de qué venían; ninguna se edita. Lo que no se hace nunca es dejar cinco bitácoras conviviendo dentro de una carpeta: nadie las abre y compiten con el registro vivo. El resto de su material se coloca por las reglas de siempre, y lo absorbido conserva su contenido y sus fechas: lo que se pierde es su maquinaria, y esa es la intención.

### Estructura de `fuentes/inventario.md`

Hasta la 1.21 se llamaba `enlaces.md`, aunque casi nada de lo que lista es un enlace; la migración lo renombra, y mientras tanto los scripts leen los dos nombres. Si un proyecto tiene todavía `enlaces.md` y hay que añadirle una fila, primero se renombra a `inventario.md` (está en la carpeta donde la cuenta escribe) y la fila va ahí: nunca un segundo archivo al lado.

```markdown
| Qué es | Enlace | Qué tener presente |
|---|---|---|
| Documentación del ERP | https://… | Versión 2024, puede estar desfasada |
| Nómina del equipo, 2026 | `restringido/nomina-2026.xlsx` | Solo el total agregado sale a un entregable |
```

## 4. Vivo o registro, nunca las dos cosas

Un archivo vivo se reescribe y refleja el presente; un registro solo crece, con las entradas nuevas arriba, y las anteriores no se editan jamás. Los formatos de `decisiones.md` y `sesiones.md`, el identificador de una entrada, los cuestionamientos y el aviso entre áreas están en `escribir.md`.

## 5. Cabecera

Todo `.md` empieza con una cabecera de `estado` (`borrador`, `vigente` o `reemplazado`) y `actualizado`, y en `entregables/` y `taller/` además `aportacion` (una línea con lo que la pieza aporta) y `basado_en`, salvo `guia.md`, `metodo.md` y el contenido de `fuentes/`. Qué lleva cada archivo y qué significa cada estado está en `escribir.md`.

## 6. Nombres

Minúsculas, guiones en vez de espacios, sin acentos ni eñes, sin fechas ni números de versión, sin números de fase ni de etapa. `flujo-aprobacion.md`, no `Flujo de Aprobación v2 FINAL.md` ni `fase1-flujo-aprobacion.md`.

El nombre de un archivo es estable durante toda su vida. El historial de versiones lo lleva la carpeta compartida (Drive, OneDrive…), el estado lo lleva la cabecera y el orden de las fases lo cuenta `proyecto.md`.

Las carpetas de área y de proyecto siguen la misma regla, y por una razón más: una referencia `area/proyecto#AAAA-MM-DD` en `Afecta a`, `Cuestiona a` o `Responde a` solo se resuelve con nombres así. `Ventas Norte/cuentas` no la encuentra nadie, y sin dar error.

### El nombre de una carpeta compartida

La raíz es una carpeta compartida y su nombre se ve en Drive, así que ese sí lleva mayúsculas y espacios: `Acme`. Solo letras, números, espacios y guiones, y los acentos y las eñes que traiga el nombre propio. Ningún otro signo, porque ese nombre se escribe a mano muchas veces y un signo raro se copia mal. Si una organización ya tiene una carpeta con un signo así, se propone renombrarla; el método no depende del nombre, porque ninguna instrucción usa rutas absolutas.

## 7. Qué es público

La superficie pública de un proyecto son `entregables/` y `decisiones.md`. Es lo que otra área puede leer para construir encima, y solo si el entregable está `vigente`. `area.md` y `proyecto.md` también se leen desde fuera, porque son el índice que lleva hasta esa superficie, y de `sesiones.md`, la cabecera de cada entrada (abajo).

**Un proyecto es público** cuando su área no es «Restringida» en `guia.md` (sección 1, «Lo restringido»), su línea del bloque `Proyectos` de su `area.md` no empieza por «restringido» y esa línea existe. Fuera de su área, de un proyecto que no es público no sale más que su nombre y su responsable. El tablero no aplica este criterio: es de una persona, no se comparte y muestra todo lo que lee su cuenta (desde la 1.18 no hay tablero público).

El cuerpo de `sesiones.md`, `taller/`, `fuentes/` y todo lo que está restringido son taller privado. Nadie de fuera del área los lee ni los cita en `basado_en`. Un entregable sí cita el taller de su propio proyecto, que es de donde salió.

Del `taller/` también hay una parte pública: **su inventario**, que es la cabecera de cada archivo (`estado`, `actualizado`, `aportacion`, `basado_en`, `reemplazado_por`) y su título. Dice qué hay, en qué estado y qué sostiene cada pieza, sin contar cómo se llegó, y es lo que el tablero enseña en «Qué hay» a quien lee el área (decisión 2026-10-23). El cuerpo sigue siendo privado: nadie de fuera del área lo lee, lo cita ni lo copia. Por eso la línea `aportacion` de un archivo del taller, como su título, no lleva nada restringido ni personal.

De `sesiones.md` hay una parte pública: la cabecera de cada entrada, que es la fecha, el título y la línea «Tema» («Trabajamos en» en las anteriores a la 1.22). Dice qué está moviendo el proyecto sin contar cómo, y es lo que otra área, `consulta` y el director pueden leer de una bitácora ajena. El resto de la entrada es el cuerpo y sigue siendo taller privado. Lo que otra área necesita saber de un proyecto está pensado para leerse sin la bitácora: su `Estatus`, sus decisiones y sus entregables vigentes, y el `Estatus` de su área.

Dentro de la misma área, un entregable puede citar en `basado_en` una fuente de otro proyecto del área, siempre la original y nunca una copia: un export vive en un solo `fuentes/` y los demás lo citan por su ruta. Entre áreas no se citan fuentes, solo entregables vigentes y decisiones.

### Lo restringido se cita en una sola dirección

Un archivo restringido puede citar en `basado_en` lo que quiera de lo que sí lee todo el equipo: entregables vigentes, decisiones, `base/`. Al revés, nunca. Nada que lea todo el equipo cita, nombra ni resume un archivo restringido, porque quien lo lea no va a poder abrirlo y porque la cita misma ya cuenta algo de lo que hay dentro. La única excepción es la fila de `fuentes/inventario.md`, que dice que un material existe y dónde está, no lo que dice.

Vale igual para `Afecta a`: una decisión restringida puede apuntar a cualquier proyecto, y una decisión que lee todo el equipo apunta a un área o a un proyecto restringido por su nombre, que ya está listado, nunca a uno de sus archivos.

Lo aprendido dentro de un área restringida vuelve a la memoria común **reescrito, no movido**: se publica como entregable propio de un proyecto que lee todo el equipo, con lo que sirve para la próxima vez y sin los datos, las cifras ni los nombres de donde salió. Un archivo restringido no sale nunca de donde está; un aprendizaje sí cambia de sitio, y lo hace escribiéndolo de nuevo.

## 8. Rotación

Los registros que crecen demasiado o cambian de año se archivan con el año en el nombre: en `escribir.md`.

## 9. Lo que no existe en este sistema

Lo que ya excluyen las prohibiciones (`escribir.md`, sección 10) y el resto del contrato no se repite aquí. Además, no existen:

- Una carpeta `metodo/` dentro de la raíz. El método vive en el plugin y en `metodo.md`
- El tablero dentro de la raíz. La página que muestra la carpeta entera, su base de datos, sus scripts y su tarea viven fuera, en la cuenta de la persona que lo montó; es derivado de la raíz y nunca su fuente, y en la raíz no deja ni su enlace
- Carpetas llamadas `varios`, `otros`, `temp` o `borrador`
- Un archivo por decisión
- Enlaces wiki `[[asi]]`, callouts propietarios, archivos `.canvas`
- Cualquier archivo que el usuario tenga que rellenar a mano
- `AGENTS.md` ni ningún archivo de instrucciones para la IA dentro de la raíz. Las instrucciones son las skills, el aviso de arranque del plugin y `guia.md`
- Rutas absolutas dentro de cualquier archivo
- Estado del método guardado en la memoria del modelo ni en la memoria de proyecto de Claude: es por persona, no se comparte, no se ve y puede contradecir un archivo sin que nadie lo note. Si un dato importa, está en un `.md`

## 10. Prohibiciones

Valen para todas las skills, no se repiten en ninguna y están en `escribir.md`, que se carga antes de cualquier escritura.

## 11. Actualización del método

El método se actualiza publicando una versión nueva del plugin, y cada raíz recibe su `metodo.md` sola, de la primera cuenta con el plugin más nuevo que abre sesión o pone al día un tablero. Nadie edita `metodo.md` dentro de la carpeta de una organización. La regla completa (cuándo se copia, quién, qué pasa sin permiso), cómo se publica una versión y cómo se verifica una raíz están en `montaje.md`, junto a este archivo.

**Cuando una versión cambia la estructura**, como la 1.22 (`Estatus`, `Responsable`, `aportacion`, `Descartado`, `Tema`, «Acceso», `inventario.md`), cada raíz se migra sola, por partes: la apertura detecta la estructura anterior en las áreas de la cuenta, lo dice en una línea y ofrece migrar; con el sí, un script (`migrar_estructura.py`, skill `sesion`) renombra secciones, claves y archivos solo en las áreas donde la cuenta es responsable, y en `guia.md` si es el responsable de contexto, y deja una entrada `(migracion)` en el `sesiones.md` de cada proyecto migrado. Los registros no se editan: sus entradas viejas conservan sus nombres. Las áreas de otras personas esperan a que su responsable abra sesión; mientras, una raíz mezclada funciona, porque durante esa versión los scripts y las skills leen los nombres viejos y los nuevos y escriben solo los nuevos. La skill `migrar` no interviene: es para adoptar estructuras ajenas.

## 12. Cómo se lee

Nunca se lee todo, y casi nunca se lee `base/`. Al abrir, se carga lo justo para saber qué existe y dónde está cada cosa; el resto entra cuando el trabajo del día lo pide, y por su nombre.

**Nivel 0, siempre, y nada más que esto.** Cuatro lecturas cortas:

1. La primera línea de `metodo.md`, para la versión y la huella de la raíz.
2. `guia.md` entero. Es el mapa: qué áreas hay, quién responde por cada una y con qué cuenta, quién mantiene el contexto, quién administra la carpeta y las reglas propias de la casa. Cabe en una pantalla.
3. El bloque `Proyectos` del `area.md` que toca. Dice qué proyectos hay y qué entregables vigentes tiene cada uno.
4. `base/premisas.md`, si existe: las premisas vigentes, las que ninguna otra reemplaza. Es corta y todo se ancla en ella.

Con eso ya se sabe qué existe, de quién es y dónde está. Todo lo demás se pide por su nombre.

**La apertura mínima**, en la primera respuesta de cualquier conversación con la carpeta conectada aunque no se trabaje en ningún proyecto, lee menos que el nivel 0: la primera línea de `metodo.md`, el título y la tabla de áreas de `guia.md` (sin imprimirla), una línea por proyecto de cada área y los nombres y fechas de lo suelto en «Claude outputs». Sin premisas ni `guia.md` entero: entran con el nivel 0 en cuanto se abre un proyecto (skill `sesion`).

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

La única operación que recorre la raíz entera es la búsqueda de las líneas `Afecta a:`, `Cuestiona a:` y `Responde a:` que nombran el proyecto activo, al abrir sesión. Busca un patrón de línea, no lee archivos, y las carpetas restringidas sin acceso fallan y se saltan.

Si el camino lleva a una carpeta restringida sin acceso, la lectura falla. Eso no es un error ni un hueco: se dice qué área o qué proyecto es y quién es su responsable, y ahí se para. No se deduce lo que hay dentro por los nombres de las carpetas ni se da por hecho que no hay nada.

## 13. Montaje

Se conecta la raíz completa, nunca la carpeta de un área: `guia.md`, `metodo.md` y `base/` viven en la raíz y la lectura cruza áreas. Cada persona trabaja desde su cuenta, y dónde escribe sale de su fila en `guia.md`, como responsable o como colaborador, y de la línea `Colabora:` de los proyectos. El plugin trae un aviso de arranque que inyecta las instrucciones en cada sesión, así que nadie pega nada en el proyecto de Claude. El tablero es opcional y personal (skill `tablero`). El montaje en detalle, el bloque de instrucciones para quien use otro modelo sin el plugin y lo que vale para programadores están en `montaje.md`, junto a este archivo.

## Anexo: Escribir en la carpeta

Anexo del contrato (`convenciones`). Reúne lo que hace falta para escribir en un proyecto y en su área: la estructura de `area.md` y de `proyecto.md`, los formatos de los registros, la cabecera, la rotación y las prohibiciones. Se carga antes de cualquier escritura en la carpeta. Para cerrar sesión, registrar una premisa o escribir el `Estatus` de un área basta con este anexo; para crear un área o un proyecto, guardar o publicar un documento, mover material, migrar o montar una raíz se carga además el contrato entero (`SKILL.md`, junto a este archivo). Si la carpeta está conectada pero el shell de la computadora no la ve, se escribe además como dice el anexo `sin-consola.md`, junto a este archivo, y se lee antes de la primera escritura. Las secciones llevan el número que tienen en el contrato, y las que se citan sin estar aquí (1, 7, 11, 12) son las del contrato.

### 2. Estructura de `area.md`

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

Hasta la 1.21 el área llevaba `Prioridades ahora` y `Panorama`, y su responsable figuraba como `Dueño:`. Los scripts y las skills leen los nombres viejos durante la 1.22 y escriben solo los nuevos: el cierre que escribe el `Estatus` retira `Panorama` y `Prioridades ahora` y lleva a «Siguiente» las prioridades que falten; la apertura ofrece la migración (skill `sesion`).

### 3. Estructura de `proyecto.md`

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

Hasta la 1.21 el proyecto llevaba `En corto`, `Terminado significa`, `Estado actual` y `Consumen esto`, el alcance como «Sí / No» y el responsable como `Dueño:`. Quién consume un proyecto lo dicen las líneas `Afecta a:` y `basado_en` que lo nombran. Los scripts y las skills leen los nombres viejos durante la 1.22 y escriben solo los nuevos; la apertura ofrece la migración (skill `sesion`).

#### Un proyecto cerrado

Cuando se cumple lo que dice la segunda frase de `Objetivo`, el responsable lo pide y el `Estatus` queda en una línea, la fecha y la frase en negrita, que empieza por **«Proyecto terminado el AAAA-MM-DD.»** y dice cómo acabó. A partir de ahí el proyecto no evoluciona: sus archivos siguen donde están, con el estado que tengan, y su `Siguientes pasos` dice que no queda ninguno propio.

Lo que cambia es el índice. En el bloque `Proyectos` de su `area.md` **un proyecto cerrado ocupa una línea y no desglosa sus entregables**, y el `Estatus` del área no le dedica línea. Quien necesite el detalle abre su `proyecto.md`.

Un proyecto cerrado no se borra ni se saca de la raíz. Se sigue citando, sus entregables vigentes se siguen consumiendo y su `decisiones.md` sigue explicando por qué las cosas están como están.

#### Plazos: en tiempo de trabajo con IA

Cuando se dice cuánto lleva algo («para cuándo» en `Siguiente`, una propuesta de trabajo, un plan), se estima en el tiempo que de verdad cuesta trabajando con la IA, en sesiones o en horas, no en lo que tardaría un equipo de personas sin ella: construir, redactar o revisar algo acotado cabe casi siempre en una sesión. Lo que alarga un trabajo es lo que espera a una persona (que pruebe, apruebe, responda, firme o haga algo en otra herramienta), y eso se dice aparte, con quién y desde cuándo. Ante la duda, se da lo que cabe en la próxima sesión y lo que queda esperando a alguien, sin inventar fechas. En `Siguiente`, «para cuándo» es la fecha de la próxima sesión prevista si la hay, y si no, «cuando <persona> <haga X>»; nunca una fecha estimada de terminar.

#### La voz del `Estatus`

Lo lee alguien con poco tiempo que no va a abrir nada más, en el proyecto y en el área. La primera frase dice el hecho, no lo anuncia, y sobra toda palabra que se puede borrar sin perder información. Personas con nombre, fechas absolutas, sin adjetivos y sin rutas. Es la voz del director de área y el estilo de la casa (skills `director` y `estilo`); para escribir un `Estatus` basta con este párrafo.

#### Qué guarda el cierre y qué no

**Siempre**: la entrada de la sesión; las decisiones confirmadas, con su porqué y lo que se descartó; `Estatus` y `Siguientes pasos` al día; el estado de cada entregable que se tocó (su cabecera y su fila en `area.md`).

**Nunca**:
- Un **valor vivo**: lo que cambia sin que nadie edite la memoria (un saldo, un precio de lista, cuántos registros hay en un sistema, el estado de un ticket). Se consulta en su fuente cuando hace falta; una cifra que sí se guarda lleva fecha y fuente (prohibición 13).
- Lo que **se puede consultar en una fuente**: se cita dónde está, no se copia.
- **Credenciales**, ni datos personales que el trabajo no necesita.
- Lo que la propia sesión **probó y desechó sin llegar a decisión**: un intento, un borrador tirado, un error corregido en la misma conversación. Lo que se descartó al decidir sí va, en `Descartado`.

Ante la duda de si algo merece quedar, se pregunta; no se guarda por si acaso.

### 4. Vivo o registro, nunca las dos cosas

**Un archivo vivo se reescribe** y siempre refleja el presente. Nadie necesita leer su historia para entenderlo.

**Un registro solo crece.** Las entradas nuevas van arriba y las anteriores no se editan jamás, ni para corregir. Si una decisión cambia, se añade una entrada nueva con la línea `Reemplaza:` que apunta a la anterior.

Un registro nunca vive dentro de un archivo vivo, porque la primera reescritura lo borra.

**La fecha de una entrada, y la de `actualizado`, es la del día en la zona horaria de la organización** («Zona horaria:» de `guia.md`; la línea HOY de `abrir.py`), no la del reloj de la consola ni del contenedor, que van en UTC y por la tarde ya dicen mañana. Una entrada fechada mañana desordena el registro: queda encima de las de hoy que se escriban después, y `cerrar.py` la rechaza.

#### Formato de `decisiones.md`

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

Las entradas anteriores a la 1.22 dicen `Descartamos:`; se quedan así, y los scripts leen las dos formas.

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

Una decisión recuperada al migrar que nadie ha confirmado todavía lleva `Decidió: Nombre Apellido (pendiente de confirmar)`. La confirma su responsable con una entrada nueva que la da por buena o la cambia; la recuperada no se edita.

Una entrada tiene lo justo para entender qué se decidió y por qué sin abrir nada más. El análisis que respalda la decisión (opciones, tablas, cifras) no va en la entrada: va a un entregable del proyecto y la entrada lo cita en `Afecta a` o en `Por qué`.

`Afecta a` lleva rutas relativas al proyecto para lo que está dentro de él, y `area/proyecto` cuando la decisión toca a otro proyecto de la raíz, o `area/` cuando toca a un área entera, que avisa en cualquiera de sus proyectos. Cada destino admite detrás un paréntesis corto con la consecuencia concreta; sin él, quien recibe el aviso sabe que algo le toca pero no qué. Los destinos se separan con `·` y la línea no se parte en varias.

#### Formato de `sesiones.md`

```markdown
## AAAA-MM-DD
Tema: …
Avances: …
Sesión de: Nombre Apellido · plugin 1.22.0
```

`Tema` dice en qué se trabajó, en una línea: es la cabecera pública de la entrada (contrato, sección 7). La última línea dice quién trabajó y con qué versión del plugin. Es del cuerpo, como «Avances», y no sale fuera del área. Lo que sigue no va en la entrada: lo dice «Siguiente» del `Estatus`, que el mismo cierre reescribe. Las entradas anteriores a la 1.16 no llevan «Sesión de:», y las anteriores a la 1.22 dicen «Trabajamos en:» y llevan «Pendiente:»; se quedan así. Una sesión sin consola (`sin-consola.md`) termina la línea con « · sin consola».

Entradas nuevas arriba. Una tarea programada que escribe en la carpeta deja su entrada como `## AAAA-MM-DD (tarea)`, y la migración de estructura de la 1.22, como `## AAAA-MM-DD (migracion)`: cuentan lo que hicieron, pero no son sesiones, y el tablero no las cuenta como tales.

#### Regla de histórico

Las entradas escritas antes de adoptar este formato se dejan tal cual; el formato aplica desde la siguiente entrada. La excepción es la migración: un registro que se acaba de crear al migrar sí se convierte, porque nadie lo ha consumido todavía.

#### Aviso entre áreas

La carpeta no notifica a nadie. Por eso `Afecta a` puede nombrar proyectos de otras áreas: al abrir sesión se buscan, en los `decisiones.md` de la raíz, las líneas `Afecta a:` y `Cuestiona a:` que nombren el proyecto activo o su área entera (`area/`) (y, en la sesión del responsable de contexto, las que nombren una premisa), y las `Responde a:`, que dicen qué cuestionamiento ya está cerrado y avisan a quien lo planteó, en su proyecto, de que le respondieron. Es una búsqueda de un patrón de línea, no una lectura de archivos, y es la única operación que recorre la raíz entera al abrir. Al cerrar sesión, si una decisión afecta a otra área, se recuerda al usuario que avise a su responsable.

### 5. Cabecera

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

**aportacion**: una línea que dice qué aporta la pieza a lo que el proyecto sabía, no de qué trata: «El tope de 5.000 MXN deja fuera las compras recurrentes», no «Análisis de compras». Vale para cualquier pieza: un análisis dice su conclusión, una guía lo que permite hacer, una plantilla para qué sirve. Es lo que deja ver, sin abrir el documento, qué hay en un proyecto y si sigue valiendo, y es la línea del entregable vigente en el bloque `Proyectos` de `area.md` (sección 2). Una sola línea de hasta unos 200 caracteres, sin saltos, entre comillas si lleva dos puntos. La escribe la skill, como `basado_en`; el barrido del tablero propone una línea para cada archivo que no la tiene, y su responsable acepta las que valen. La leen todos los que leen el área, en el tablero, aunque el cuerpo del taller sea privado, así que lleva la regla del `Estatus`: nada de `restringido/` ni datos personales. Añadir o cambiar `aportacion` sin tocar el contenido no mueve `actualizado`: esa fecha es la del último cambio de contenido, y moverla escondería lo que quedó viejo frente a una decisión o frente a su base. Hasta la 1.21 se llamaba `afirma`; los scripts leen las dos durante la 1.22 y escriben solo `aportacion`.

**basado_en**: rutas relativas a la raíz de todo lo que se usó para escribir el archivo. Es lo que permite detectar que una pieza quedó desactualizada cuando cambia algo aguas arriba. La escribe la skill, no la persona. Si no se usó más que la conversación, o el material se adoptó sin trazabilidad, va la lista vacía `[]`; `revisar` la pide completa antes de publicar un entregable adoptado.

Las dos claves son obligatorias en lo que se crea en `entregables/` y `taller/`; en lo que ya existía sin ellas, `verificar.sh` las cuenta y el barrido propone la `aportacion`. Ningún otro archivo las lleva: ni los registros, ni `area.md`, ni `proyecto.md`, ni `base/`, ni `fuentes/`.

No hay clave de responsable. El responsable vive en `area.md` y en `proyecto.md`, en `Quién participa`. Si un documento concreto tiene otro responsable, lo dice la primera línea de su cuerpo.

Las claves van sin acentos ni eñes.

### 8. Rotación

Cuando `sesiones.md` o `decisiones.md` pasa de unas 1.500 líneas o cambia el año, se archiva en la misma carpeta con el año en el nombre (`sesiones-2026.md`; si en un mismo año hace falta otro, `sesiones-2026-2.md`) y se abre uno nuevo con su cabecera. Es la única excepción a los nombres sin fechas: el año es lo que distingue el registro archivado del vivo. Lo hace la skill de cierre de sesión, sin preguntar.

### 10. Prohibiciones

Valen para todas las skills y no se repiten en ninguna. Cada skill añade las suyas, que son las de su trabajo concreto.

1. No marcar nada como `vigente`. Solo lo hace `revisar`, y solo cuando lo pide el responsable del proyecto; y `migrar`, con lo que su responsable en el origen pide publicar al migrar. `area.md` y los registros nacen `vigente` (sección 5).
2. No editar una entrada ya escrita de `decisiones.md` o de `sesiones.md`, ni para corregir una errata. Un registro solo crece.
3. No registrar una decisión que el usuario no confirmó en esta sesión, salvo las recuperadas al migrar, que entran marcadas «pendiente de confirmar» (sección 4).
4. No escribir en `guia.md`, en `base/`, en `metodo.md` ni en la carpeta de un área de la que la cuenta no es responsable ni colabora. Desde la sesión de otra área se prepara el texto y se le pasa a quien responde. Las excepciones: la sesión del responsable de contexto escribe `guia.md` y `base/`, y `metodo.md` lo pone al día cualquier cuenta con el plugin más nuevo (sección 11).
5. No tocar archivos fuera del proyecto activo, salvo la línea de ese proyecto y las de sus entregables vigentes en el bloque `Proyectos` de su `area.md`, el `Estatus` de ese `area.md` al cerrar sesión o cuando su responsable lo pide (skill `director`), lo mecánico que la puesta al día del tablero escribe en los proyectos donde la cuenta es responsable o colabora: fechas de pasos y hechos marcados desde el tablero (skill `tablero`), nunca en los de otra cuenta, y lo que renombra la migración de estructura de la 1.22 en las áreas de la cuenta (skill `sesion`). El `Estatus` del área es solo de su responsable.
6. No leer el cuerpo de `taller/`, `fuentes/`, lo restringido de otra área, ni el cuerpo de su `sesiones.md`: de la bitácora ajena solo la fecha, el título y «Tema» de cada entrada («Trabajamos en» en las anteriores a la 1.22); del taller ajeno solo la cabecera y el título de cada archivo, su inventario (sección 7). Son taller privado y no responden a nadie de fuera.
7. No escribir en un archivo que lee todo el equipo la ruta ni el contenido de algo restringido, aunque sea resumido. Hacia fuera solo van el nombre del área o del proyecto, que ya están listados, y la fila de `inventario.md`.
8. No guardar en `fuentes/` un material con indicios de información confidencial sin haberlo dicho y preguntado antes, ni mover nada a `restringido/` sin que el usuario lo confirme.
9. No guardar fuera de `fuentes/` material que llegó de fuera del equipo del proyecto, aunque venga terminado y listo para usarse.
10. No copiar a este `fuentes/` una fuente que ya existe en otro proyecto del área. Se cita la original por su ruta.
11. No crear un área ni un proyecto sin responsable con nombre y apellido.
12. No rellenar un hueco con una suposición razonable. Un hueco se marca como hueco, y "no consta" es una respuesta válida.
13. No escribir una cifra sin fecha ni fuente.
14. No poner número de fase, fecha ni versión en el nombre de un archivo o de una carpeta. El registro archivado por año es la única excepción (sección 8).
15. No crear carpetas que la estructura no contempla, ni un `AGENTS.md` u otro archivo de instrucciones para la IA, ni un índice a mano, ni una carpeta de borradores, ni escribir rutas absolutas en ningún archivo.
16. No dejar dentro de la raíz el almacén de datos de una aplicación, ni apuntar una aplicación a que escriba ahí.
17. No borrar un entregable superado. Pasa a `reemplazado` con `reemplazado_por`, porque alguien puede tenerlo citado.
18. No llevar a la raíz de una organización ningún hecho que venga de otra raíz, ni siquiera para comparar, salvo por un traspaso que la persona pidió y confirmó pieza a pieza (sección 1, «Independencia entre raíces»).
19. No guardar estado del método en la memoria del modelo ni en la memoria de proyecto de Claude. Si un dato importa, va a un `.md` de la carpeta.
20. No dejar en `entregables/` lo que no puede salir del proyecto. Si no se lo puedo dar a nadie de fuera, va a `taller/`.
21. No abrir un `decisiones.md` ni un `sesiones.md` dentro de `taller/`. Los registros del proyecto son los de su raíz.
22. No dejar dentro de la raíz un script, una salida ni un archivo temporal, ni trabajar en `/tmp` de la consola de la computadora, que comparten todas las conversaciones: lo de paso va en `$HOME` de la consola, que es de esta conversación, fuera de `mnt/` (lo que hay ahí son carpetas de la persona, y `mnt/outputs` puede ser «Claude outputs» de la raíz), o en el contenedor, y nunca se corre un archivo que no escribió esta conversación.
23. No guardar en la carpeta un `.html` sin `<meta charset="utf-8">` en su `<head>`. Abierto desde la carpeta, el navegador no tiene quien le diga la codificación y los acentos salen rotos («Ã©»); publicado como artefacto se ve bien, y por eso el fallo pasa inadvertido hasta que alguien abre el archivo.

## Anexo: Varias raíces y traspasos

Anexo del contrato (`convenciones`, sección 1). Se lee cuando hay más de una raíz conectada, cuando alguien pide pasar algo de una raíz a otra y al migrar.

### Independencia entre raíces

Una sesión puede tener conectada más de una raíz a la vez, o una raíz y el repo del plugin. Se trabaja en una a la vez: si hay más de una carpeta con `guia.md` y `metodo.md`, antes de leer o escribir nada se pregunta en cuál, cada escritura dice en qué raíz se hace y cambiar de raíz se anuncia. Cada raíz sigue siendo de una sola organización: nada que se escriba en una raíz usa hechos, cifras, nombres o decisiones de otra raíz, ni del repo del plugin, salvo por un traspaso; y nada que se escriba en el repo del plugin usa hechos de una organización en particular, porque el plugin es idéntico para todas. Comparar la forma de dos raíces (¿tienen las mismas piezas?, ¿la misma cabecera?) no es tocar su contenido, y ese trabajo no se guarda dentro de ninguna de las dos. Lo que una organización guarda sobre otra, por ejemplo quien mantiene el método guardando el historial de una migración que hizo para un cliente, se limita a lo operativo de quien lo guarda: qué se entregó y cuándo, nunca el contenido del trabajo del cliente.

### Traspaso entre raíces

 A veces algo de una raíz tiene que llegar a otra: lo que se decidió sobre un cliente en la raíz de su proveedor y el cliente necesita en la suya, o al revés. Solo ocurre si lo pide la persona que trabaja, pieza a pieza, hacia una raíz donde puede escribir. Antes de escribir se le enseña el texto exacto que pasaría, a qué archivo de la otra raíz iría y qué se queda fuera y por qué (datos personales, contratos, credenciales, cifras internas, lo de otros clientes); se escribe solo cuando lo confirma. En el destino entra reescrito para su contexto y por la puerta que le toque: una decisión se registra como decisión de quien la asume ahí, y un documento entra por `fuentes/` o como entregable de quien lo hace suyo. La sesión del proyecto de destino anota qué vino, de qué raíz, quién lo pidió y cuándo. El origen no se toca. Credenciales, y datos de una organización hacia la raíz de otra que no tiene que ver con ellos, no pasan nunca, aunque se pida: se dice por qué. Lo demás lo decide quien pide el traspaso, que tiene la última palabra.

### Dónde vive el registro de una migración

Eso fija dónde vive cada cosa cuando una organización adopta el método. **El registro de la migración es de quien migra**: las auditorías, los planes y los manifiestos van a su raíz, en un proyecto por organización nombrado por la organización y no por el trabajo. Cuentan lo que hizo el proveedor y hablan del sistema del que se migró, que la organización que estrena el método no usó nunca y no le dice nada.

En la raíz de la organización entra solo lo que su equipo necesita para operar, y entra donde se usa, no en un proyecto aparte: las decisiones recuperadas de su material anterior, cada una en el `decisiones.md` del proyecto al que pertenecen y marcadas como pendientes de confirmar; y el material confidencial que quedó fuera de alcance, con su fila en el `fuentes/inventario.md` que corresponda. Nada más: su raíz no guarda rastro del sistema del que se migró, ni en las rutas, ni en el vocabulario, ni en los nombres de sus archivos.

## Anexo: Montaje, publicación y otros modelos

Anexo del contrato (`convenciones`, secciones 11 y 13). Lo leen `nuevo` al montar una raíz, `tablero`, y quien pregunte cómo se monta o se publica el método. El bloque de instrucciones de abajo es el que inyecta el aviso de arranque del plugin en cada sesión.

### Actualización del método

El método se actualiza publicando una versión nueva del plugin. La primera línea legible de `metodo.md` lleva la versión y una huella de su contenido, que escribe `build-metodo.sh`: cualquier cambio de texto la cambia aunque el número no cambie. Al abrir sesión se compara esa línea en la raíz con la del `metodo.md` del plugin. La raíz está atrasada si la versión del plugin es mayor, o si es la misma y la raíz no lleva huella; con la misma versión y huellas distintas no se toca nada (solo pasa entre dos publicaciones). Si está atrasada, la sesión que abre (skill `sesion`) o la puesta al día de cualquier tablero (paso 1c de `tarea.md`) copia el `metodo.md` del plugin sobre el de la raíz, sin preguntar y sin tocar nada más, y lo dice en una línea. Lo hace cualquier cuenta, no solo el responsable de contexto, porque es una copia exacta del plugin y no contenido de la organización: una versión nueva llega a la carpeta con la primera persona que abre sesión o sincroniza un tablero con el plugin actualizado. Nunca hacia atrás. Si la cuenta no tiene permiso para escribir en el primer nivel de la carpeta, la escritura se rechaza, no se intenta por otra vía, no se dice nada y lo hará la siguiente cuenta que pueda. Si el atrasado es el plugin de quien abre, se le dice que lo actualice. Nadie tiene que acordarse de copiarlo. Nadie edita `metodo.md` dentro de la carpeta de una organización.

Dos scripts acompañan al plugin y nadie tiene que recordar sus pasos (`build-metodo.sh`, que arma `metodo.md`, lo llama `release.sh`). `release.sh` publica una versión: comprueba antes de tocar nada que la versión sea mayor que la actual, que el contrato declare la mayor.menor y que el README tenga su entrada; sube el número donde vive, regenera `metodo.md` y dice qué queda por hacer a mano. Si algo falla a mitad, deja los archivos como estaban. `verificar.sh` se pasa sobre la raíz de una organización: comprueba la estructura, los nombres, las cabeceras, los estados y que el bloque `Proyectos` de cada área liste todo lo que tiene que listar. No escribe nada: de cada `.md` lee la cabecera y busca enlaces wiki y rutas absolutas, no entra en `fuentes/` ni en `restringido/`, y una carpeta que no se deja leer la salta.

### La carpeta en Google Drive

Es trabajo de quien administra la carpeta, una vez por organización, antes de que nadie se conecte. Vale lo mismo para otra nube con unidades de equipo; el ejemplo es Drive.

**Mejor una unidad compartida de la organización.** Sus archivos son de la organización y no de una persona: si alguien se va, nada se pierde ni cambia de dueño, y los permisos se dan por miembro. Las unidades compartidas son de Google Workspace; con una cuenta personal de Gmail no las hay, y entonces la raíz es una carpeta normal en «Mi unidad» de quien administra, compartida con el equipo. En ese caso los archivos son de esa persona: si deja la organización, hay que pasarlos antes a otra cuenta.

**La raíz** es la unidad entera o una carpeta de su primer nivel, con `guia.md` y `metodo.md` dentro, y un nombre que se pueda teclear (contrato, sección 6). Cada organización, una sola.

**Los permisos**, como dice la sección 1 del contrato:

- Todo el equipo, «Lector» en la unidad (o en la carpeta raíz).
- Cada responsable de área y quien colabora en ella, «Gestor de contenido» en la carpeta de esa área, que se da con clic derecho › Compartir sobre la carpeta; quien colabora en un solo proyecto, solo en la carpeta de ese proyecto. «Colaborador» no sirve, porque no deja mover ni borrar archivos, y «Gestor de contenido» en la unidad entera abre la escritura en todas las áreas.
- El responsable de contexto, «Gestor de contenido» en `guia.md` y `base/`.
- Quien administra, «Administrador» de la unidad, y nadie más.
- En «Mi unidad», sin unidad compartida, los roles son «Lector» y «Editor»: «Editor» donde arriba dice «Gestor de contenido».
- Lo restringido se marca en su carpeta con el acceso limitado de Drive, desde la web. En una unidad compartida lo pone quien la administra; Google lo admite en unidades compartidas desde 2025.

**En la computadora de cada persona**, Drive para escritorio solo transmite las unidades compartidas: no las copia enteras al disco como puede hacer con «Mi unidad». Por eso la carpeta se marca «Disponible sin conexión» en cada computadora, y se comprueba que sus archivos bajaron antes de conectar la carpeta a Claude. En Windows la unidad aparece como una letra de disco aparte (por ejemplo, G:) y se conecta igual. La consola de Claude no la monta, así que esas computadoras trabajan sin consola (anexo `sin-consola.md`): todo funciona, algo más lento, y para mover archivos hace falta el conector de Google Drive activado en Claude. Nadie tiene que cambiar nada de Drive.

### Montaje en Claude

El uso principal del método es Claude con la raíz conectada y el plugin instalado. El montaje tiene dos reglas.

**Un proyecto de Claude por persona**, nombrado por su área, o por la organización si esa persona lleva todas las áreas. Dónde escribe no lo decide el nombre del proyecto sino su cuenta en `guia.md`, así que un solo proyecto sirve para todas las áreas de quien las lleva todas.

**Se conecta la raíz completa, nunca la carpeta de un área.** `guia.md`, `metodo.md` y `base/` viven en la raíz; la lectura cruza áreas; `consulta` busca en lo que produjo cualquier área y `sesion` avisa de las decisiones de otras que afectan al proyecto. Conectada solo un área, el método se rompe en la primera llamada. Conectar de más no abre ningún riesgo: quién puede leer y escribir dónde lo fijan los permisos de las carpetas, no el alcance de la conexión, y lo restringido sigue restringido dentro de una carpeta conectada.

Al proyecto se le vincula la raíz, y para trabajar en un área no hace falta ninguna carpeta más. Si se vinculan varias raíces, vale lo de «Independencia entre raíces» (sección 1).

**El tablero es opcional y personal.** Cualquiera lo monta desde su propia cuenta escribiendo «monta el tablero» con la raíz conectada; la skill `tablero` publica la página, que se pone al día cuando esa persona lo pide, con su botón, desde su computadora y con sus permisos (al abrirla avisa de las sesiones cerradas que aún no muestra; una tarea que la regenere cada mañana solo se crea si se pide): lo que su cuenta no lee en la carpeta sale como restringido, y lo que su tarea escribe lo escribe con sus permisos. Muestra todo lo que la cuenta lee, con las sesiones recientes enteras, y por eso es solo de esa persona y no se comparte: quien quiera uno lo monta (hasta la 1.17 había además un modo público, que pasa solo a este). Se encuentra por su nombre entre los artifacts de la cuenta; en la raíz no queda nada de él. Lo que se toca en el tablero espera en su cola hasta que la siguiente puesta al día lo escribe en la carpeta, o hasta la siguiente sesión del proyecto si pide juicio; la página nunca escribe en la raíz. Cuando sale una versión nueva del plugin, la siguiente puesta al día republica la página sobre la misma URL sin que nadie lo pida.

**Nadie pega instrucciones en el proyecto.** El plugin trae un hook de arranque que, al empezar cada sesión, inyecta el bloque de abajo como contexto, y con él cómo saber dónde escribe cada quien: la cuenta que abre la sesión se busca en la columna Cuenta de la tabla de áreas de `guia.md`, como responsable o tras «colabora:», y en la línea `Colabora:` de cada proyecto, y esas áreas y proyectos son los suyos. Así el método se aplica en cuanto la carpeta está conectada, se actualiza solo con cada versión del plugin y no depende de que nadie copie bien un texto. El mismo aviso pide la apertura mínima de la skill `sesion` en la primera respuesta de cualquier conversación con la carpeta conectada, sea cual sea la petición, y un segundo hook, al terminar cada respuesta, la pide una vez por conversación si faltó; sin carpetas conectadas ninguno de los dos hace nada, y ante un error el segundo deja pasar. El bloque sigue aquí para quien trabaje con otro modelo sin el plugin, o en una superficie donde el arranque del plugin no corra: en ese caso se pega tal cual y se añade debajo una línea propia diciendo dónde se escribe. El texto no nombra skills, porque Claude las elige solo:

```
Este proyecto trabaja sobre una memoria de trabajo permanente: la carpeta conectada, que sigue el método del plugin `memoria`. Aplícalo en todo lo que hagas aquí, y no guardes nada en tu memoria: si un dato importa, va a un archivo de la carpeta.
Al empezar, lee solo lo justo para saber dónde está cada cosa (con el plugin, su apertura mínima; sin él, `guia.md`) y no leas nada más hasta saber qué necesitas: la carpeta se lee por niveles y `guia.md` dice dónde está cada cosa.
Lee y escribe la carpeta por su copia en esta computadora, nunca por el conector de Google Drive aunque esté conectado, salvo para crear carpetas, mover, renombrar o mandar a la papelera cuando la consola de la computadora no ve la carpeta, y para leer o aplicar los permisos de la carpeta cuando lo pido; si no la ves, pídeme que la añada. Sin ninguna carpeta conectada (desde el teléfono o la web), la raíz se puede leer por el conector de Drive, sin escribir nada en ella.
Escribe solo donde tu cuenta es responsable o colabora, según `guia.md` y la línea «Colabora:» de cada proyecto, o donde te diga que trabajo si la cuenta no aparece, y en ningún otro sitio de la carpeta; si no está claro, pregúntamelo antes de escribir nada. Si algo le toca a otra área, dímelo y yo se lo pido a su responsable.
No des por aprobado ningún documento ni edites lo ya registrado en decisiones o sesiones.
Si una carpeta no se deja leer, está restringida: dímelo y sigue con lo que sí puedas leer, sin suponer lo que hay dentro.
Lo que hagas para un proyecto, un documento, un PDF o un análisis, guárdalo en su carpeta en cuanto exista, como borrador, y no en «Claude outputs»; cerrar sesión es registrar lo que pasó, no guardar.
Las fechas que escribas en la carpeta son las del día en la zona horaria de la organización, la línea HOY de la apertura; nunca la del reloj de la consola ni del contenedor, que van en UTC y por la tarde ya dicen mañana.
Antes de guardar algo, pregúntate si alguien más lo va a leer y si contiene datos que no todos deben ver. Si algo parece confidencial, avísame y propón moverlo; no lo muevas tú.
```

El bloque es idéntico en cualquier organización: no nombra a ninguna, no lleva huecos que rellenar y nada de una raíz concreta entra en él. Lo propio de una raíz vive en `guia.md`, que la segunda línea manda consultar. Dónde escribe cada quien sale de `guia.md` y de la cuenta de la sesión; si ninguna área coincide con la cuenta, la IA pregunta antes de escribir en vez de suponer.

La skill `nuevo` escribe todo esto en `guia.md` como una receta corta: crear el proyecto con el nombre del área, instalar el plugin desde el marketplace, conectar la raíz, comprobar con «abre sesión en...» y, si se quiere, montar el tablero, para que cada persona lo monte sola sin preguntarle a nadie.

**Otros modelos.** Gemini u otro modelo sin plugin leen `metodo.md`. Contiene el contrato con sus anexos (menos `sin-consola.md`, que solo sirve con las herramientas del plugin), el estilo y el índice de skills, así que saben qué reglas seguir aunque no puedan ejecutarlas como skills.

**Programadores.** El `CLAUDE.md` de un repositorio enlaza la carpeta del proyecto en la raíz (`area/proyecto`). Las decisiones de código que dependen de un diseño se anclan en `decisiones.md` y en los entregables vigentes de ese proyecto, no en comentarios del código. Para saber qué se decidió antes de escribir código, usan la skill `consulta`.

---

# Estilo

Estilo de todo lo que se escribe, firma o comparte en esta estructura:

> **Ejecutivo y al grano: el hecho relevante desde el inicio, sin rodeos ni expresiones que no aporten de manera directa.**

Se escribe para alguien con poco tiempo y muchas interrupciones. Tiene que poder leer en diagonal, quedarse con lo que decide y no perderse nada esencial por haberlo hecho así.

Este archivo es la fuente canónica del estilo. Si una plantilla del plugin lo contradice, manda este archivo.

## Cuándo se aplica

Sin que nadie la invoque, en todo texto que se va a firmar o compartir: un entregable, un documento, un correo, lo que se escribe en la carpeta para que lo lea otra persona. El `Estatus` de un proyecto y el de un área no la cargan: su voz la da `escribir.md`. Para las respuestas del chat bastan las dos preguntas de abajo, que el aviso de arranque ya trae, sin cargar esta skill. Y de forma explícita cuando alguien pide que suene menos a IA, más ejecutivo, más al grano, más compacto, que se lea rápido, o que le quiten los rodeos.

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
6. Corregir el estilo de un entregable de otro proyecto o de otra área es tocar contenido ajeno, no forma. Se propone al responsable, no se aplica.

---

# Skills del plugin

Lo que hace cada una, en una línea. Con el plugin instalado se activan solas por las frases que menciona cada descripción.

- **convenciones**: Contrato base del metodo de trabajo: estructura de carpetas, cabecera de los archivos, estados, como se lee la raiz, que es publico y que se restringe. Consultala antes de crear o modificar cualquier archivo dentro de la memoria de una organizacion, y cuando pregunten como se organiza algo, donde va, que significa un estado o quien puede escribir donde.
- **estilo**: Normas de estilo y de lectura rapida. Aplicala por defecto al redactar o revisar un texto que se vaya a firmar o compartir (un entregable, un documento, un correo), sin que la invoquen; y de forma explicita cuando pidan 'que suene menos a IA', 'mas ejecutivo', 'mas al grano', 'mas compacto', 'que se lea rapido' o 'revisa el estilo'.
- **sesion**: Abre y cierra sesiones de trabajo sobre un proyecto. Usala cuando digan 'abre sesion', 'retomamos X', 'en que quedamos con...', 'cierra la sesion', 'guarda lo de hoy', 'terminamos' o 'cierra el proyecto', y cuando el responsable de un proyecto pregunte por el suyo: '¿como va X?', '¿en que estatus esta X?', '¿que falta en X?'. Tambien los permisos de la carpeta compartida: 'revisa los permisos', 'aplica los permisos', '¿quien puede escribir donde?'.
- **nuevo**: Da de alta lo que falte en la memoria de la organizacion: monta la raiz si la carpeta no tiene guia.md, crea el area si no existe y crea el paquete completo de un proyecto. Usala cuando digan 'nuevo proyecto', 'arranca un proyecto para...', 'necesito documentar esto como proyecto', 'nueva area', 'crea el area de...', 'monta la carpeta de...', 'nueva organizacion', 'arranca el metodo para este cliente', o cuando se trabaje en algo que todavia no tiene carpeta, y para sumar a alguien: 'añade a X como colaborador del area...' o 'de este proyecto'.
- **entregable**: Crea o actualiza un entregable de un proyecto. Usala cuando pidan 'prepara el documento de...', 'necesito un documento con...', 'documenta lo que decidimos sobre...', o 'actualiza el entregable X'.
- **revisar**: Revisa un entregable, detecta lo que quedo desfasado y lo publica de borrador a vigente. Usala con 'revisa X', 'esto esta listo?', 'que esta desactualizado?', 'pasalo a vigente' o 'ya lo aprobo...'. No para 'revisa los permisos', que es de sesion.
- **donde-va**: Coloca cualquier material que llegue en el sitio correcto de la estructura. Usala cuando pregunten 'donde guardo esto?', peguen un documento o un enlace sin decir donde va, aparezca un archivo suelto en la raiz, o digan 'ordena Claude outputs'.
- **consulta**: Responde preguntas sobre lo que la organizacion ya sabe, leyendo solo la superficie publica de la raiz y sin escribir nada. Usala cuando pregunten 'que sabemos de X?', 'alguien ya trabajo esto?', 'que se decidio sobre...?', 'hay algo hecho sobre...?' o 'quien lleva...?'.
- **tablero**: Monta, actualiza y sincroniza el tablero de una persona sobre la carpeta de su organizacion, una pagina que muestra la carpeta entera (areas, proyectos, estado, decisiones, siguientes pasos) generada desde los archivos y puesta al dia cuando quien lo monto lo pide, con el boton de la pagina o con 'sincroniza el tablero'. Usala cuando digan 'monta el tablero', 'monta mi tablero', 'quiero ver la carpeta sin abrirla', 'actualiza el tablero', 'sincroniza el tablero', 'regenera la vista', 'pon el tablero al dia cada manana', 'pon el boton de sincronizar', 'cambie de computadora' o pregunten por que el tablero no muestra algo.
- **migrar**: Adopta una carpeta que sigue otra estructura y la trae al metodo sin borrar los originales. Usala cuando digan 'migra esta carpeta', 'trae esto al metodo', 'adopta lo que hay en...', 'convierte estos documentos a la estructura' o cuando aparezca una carpeta con ADR, logs de sesion o carpetas numeradas.
- **director**: Actua como director de un area - resume como esta, cuestiona su contenido para encontrar oportunidades, revisa lo que otras areas decidieron o publicaron que le afecta, y escribe el Estatus del area al cerrar sesion. Usala cuando digan 'como va el area X?', 'resumen del area', 'estatus de...', 'panorama de...', 'cuestiona el area', 'que se nos escapa en...', 'que de otras areas me afecta?', 'revisa lo de otras areas', 'actualiza el estatus del area' o 'actualiza el panorama'.
- **calidad**: Revision de calidad a fondo de algo que se esta construyendo - el contenido de un proyecto, un entregable, un desarrollo o plugin, o la carpeta entera (auditoria) - contra su objetivo, con revisores independientes, para encontrar errores, inconsistencias, riesgos, oportunidades y lo que cuesta de mas (tiempo, llamadas, tokens). Usala cuando digan 'revision de calidad', 'revisa a fondo...', 'audita la carpeta', 'que no cuadra en...', 'revisalo todo contra el objetivo' o cuando toque la revision periodica de un proyecto.

---

# Procedimientos sin plugin

Cerrar una sesión, registrar una premisa y publicar un documento, tal como los sigue Claude con el plugin. Donde se nombra una herramienta que no tienes (`abrir.py`, `cerrar.py`, `device_bash`, `ArtifactData`, el tablero), haz lo mismo a mano o sáltalo: sin `cerrar.py`, escribe cada archivo del cierre a mano, releyéndolo justo antes. Lo que no se salta: los registros solo crecen, nada se registra sin el sí de quien decide, y nadie escribe fuera de su área.

## Cerrar sesión y cerrar el proyecto

Anexo de la skill `sesion`. Se lee al cerrar («cierra la sesión», «guarda lo de hoy», «terminamos», «cierra el proyecto»), y antes se carga el anexo `escribir.md` de la skill `convenciones`, que hasta aquí no hacía falta: cerrar escribe en la carpeta y sus prohibiciones aplican a todo lo que sigue. Con él basta, salvo que el paso 1 o el 7 guarde o mueva un archivo, que pide además `convenciones` entera (nombres, entregable o taller, `fuentes/inventario.md`, material sensible), o que haya un traspaso (paso 8), que pide `raices.md`. Las skills `director` y `estilo` no hacen falta para cerrar.

### Cerrar sesión

#### Qué escribo y dónde

**Las reglas del área, antes que nada.** El bloque `Proyectos` del `area.md` del proyecto (que `abrir.py` imprimió al abrir) y las reglas propias de la casa de `guia.md` pueden pedir algo al cerrar, como poner al día la fila de un pipeline o la ficha de otro proyecto del área. Se cumple en este mismo cierre, como un paso más y dentro de lo que la cuenta puede escribir; si pide escribir en un área de otra cuenta, se prepara el texto y se dice a quién pasárselo.

**Cómo se escribe: todo en una llamada, con `cerrar.py`.** La sesión prepara los textos y `cerrar.py` (junto a este archivo; llegó a la computadora con `abrir.py` en la llamada 1 de abrir, y si no está, se trae igual que él) los escribe. Un `cambios.json` con la forma que dice su cabecera: la entrada de `sesiones.md` (paso 2, con el formato de `escribir.md`: `## AAAA-MM-DD` y la última línea «Sesión de»), las decisiones confirmadas (paso 3), el `Estatus` entero (`estatus`) y los reemplazos exactos de `proyecto.md` (paso 4), la línea del proyecto y las de sus entregables vigentes en `area.md` (paso 5), el `Estatus` del área (`estatus_area`, paso 10) y, si una regla del área pide tocar otro archivo del área, sus reemplazos en «otros». Con consola: el JSON con un heredoc en `$HOME/memoria/` (fuera de la raíz) y, en la misma llamada de device_bash, `cd $HOME/memoria && python3 cerrar.py "<raíz en $HOME/mnt>" <area>/<proyecto> cambios.json --cuenta <correo de la cuenta> --abierto <la hora que imprime la línea «ahora» de REGISTROS de abrir.py, solo el valor>`. Sin consola: lo mismo con Bash en el contenedor sobre la copia (`python3 <directorio de esta skill>/cerrar.py "<la copia>" … --sin-fechas`, sin `--abierto`: las fechas de la copia son las de la traída y no dicen nada), con cada archivo traído y registrado antes como dice `sin-consola.md`, y después `espejo.py devolver`; si `device_commit_files` rechaza uno por `mtime-drift`, alguien lo cambió en la computadora: se trae otra vez, se registra, se repite `cerrar.py` sobre la copia (una entrada que ya está no se repite; los reemplazos van sobre lo nuevo) y se devuelve.

De cada archivo el script hace leer → cambiar → escribir bajo un cerrojo y, justo antes de escribir, comprueba que el archivo sigue como lo leyó; si cambió entre medias, vuelve a leer y aplica lo de esta sesión sobre lo nuevo. Así dos personas que cierran a la vez sobre el mismo proyecto, o dos sesiones de una misma cuenta, no se pierden una entrada ni un paso: cada entrada va encima de lo que haya y cada reemplazo se aplica sobre lo que está en el disco. Antes de escribir nada comprueba la forma de las entradas, que su fecha sea hoy o ayer en la zona de la organización (la línea HOY de `abrir.py`, nunca el reloj de la consola; otra fecha a propósito, solo con `--cualquier-fecha`) y que «otros» no salga del área (nunca `guia.md`, `base/` ni `restringido/`), que una entrada nueva no use los nombres de antes de la 1.22 («Trabajamos en», «Pendiente», «Descartamos»), y con `--cuenta` no escribe el `Estatus` del área si la cuenta no es su responsable ni la línea de `area.md` si tampoco colabora en ella. En una raíz sin migrar, el `Estatus` ocupa el sitio de «En corto» o del «Panorama»: escribe solo los nombres nuevos. Lo que devuelve: `escritos`; `sin_match` (un reemplazo que no cuadra, porque su texto viejo no aparece exactamente una vez, cruza un encabezado o pasa de doce líneas: se relee ese archivo, se parte o ajusta el reemplazo y se repite la llamada solo con él, pasando en `--abierto` la `escrito_en` que devolvió la anterior); `rechazados` (lo que la cuenta no puede escribir o un archivo que encogería a menos de la mitad: se prepara el texto y se le pasa al responsable, o `--forzar <ruta>` solo si el recorte es a propósito); `fallidos` (un archivo que no se pudo leer o escribir, con el motivo: se dice y no se repite a ciegas); `ajenos` (archivos que alguien cambió desde la apertura o mientras este cierre escribía, con la hora en la zona de la organización: se dice en media línea al terminar, «alguien escribió proyecto.md a las 10:03; sumé lo de hoy encima»); `reintentos`; `hora` y `documento` (para la marca del tablero, paso 11); `escrito_en`. Lo que el cierre escribe pasa por el script: nunca con `Write`, `Edit`, `sed -i` ni un `cat >`, que pueden pisar lo que otra persona escribió. Vale también durante la sesión: si la persona pide quitar un paso o cambiar el estado antes de cerrar, se apunta y se escribe al cerrar; si quiere verlo escrito ya, se escribe con `cerrar.py` y solo `reemplazos` (sin entrada de bitácora), nunca a mano. Lo único que se escribe fuera de él, antes de llamarlo, es juntar una copia en conflicto (abajo) y la rotación (paso 9), que crean o funden archivos enteros como dice `escribir.md`. Esto cierra la ventana entre leer y escribir en esta computadora; lo que la otra persona escribió y Drive aún no bajó no se ve: si los dos llegan a escribir a la vez, Drive guarda las dos versiones, y la siguiente apertura las junta («Copias en conflicto»).

**Copias en conflicto.** Cuando abrir sesión avisa de una copia en conflicto («sesiones (1).md», «proyecto [Conflict].md» junto a su original), se junta antes de cualquier otra cosa, porque hasta entonces una de las dos versiones no la lee nadie. Se leen las dos. En `sesiones.md` y `decisiones.md`, que solo crecen, se juntan las entradas de las dos, sin repetir ni editar ninguna, en el orden del archivo. En un archivo vivo (`proyecto.md`, `area.md`, `guia.md`) se le enseña a la persona lo que difiere entre las dos y se escribe lo que ella decida. Se escribe en el original, siguiendo `escribir.md`, y la copia va a la papelera con su sí: con consola, se pide el permiso de borrar; sin consola, con el conector (`sin-consola.md`). Se dice en una línea. Un archivo en conflicto de un área donde la cuenta no escribe se le dice a su responsable, y no se toca.

**Si la cuenta colabora y no es la del responsable** (sección CUENTA EN EL PROYECTO de `abrir.py`), cierra igual: bitácora, decisiones de su trabajo con su nombre en `Decidió`, `Estatus` y `Siguientes pasos`. No publica nada, ni toca el `Estatus` del área ni la línea `Colabora:` de `Quién participa` (`convenciones`, sección 1, «Quién colabora»). Si colabora solo en este proyecto y no puede escribir `area.md`, la línea del paso 5 se prepara y se le pasa al responsable del área.

**Qué entra y qué no.** Antes de preparar `cambios.json`, lo que la sesión trae se pasa por «Qué guarda el cierre y qué no» de `escribir.md`; ante la duda se pregunta en el mismo mensaje que enseña las decisiones.

**0. La cola del tablero**, si se leyó al abrir. Lo que la sesión resolvió se borra de la cola con `ArtifactData` y la versión leída: un hecho ya quitado de «Siguientes pasos» y contado en `sesiones.md`, una nota ya registrada donde le tocaba, una corrección ya aplicada reescribiendo el paso o el `Estatus`, una fecha ya puesta en su línea, una prioridad ya quitada de «Siguiente» del `Estatus` del área porque su responsable lo pidió en esta sesión. Lo que no se resolvió se queda, y el tablero lo sigue mostrando como pendiente. **Las propuestas** (`tipo` «propuesta») se resuelven con lo que la persona dijo al abrir: la aceptada y hecha se borra de la cola; la descartada se actualiza con `estado: descartada` (`update`, con la versión leída), para que el barrido no la vuelva a proponer mientras siga siendo cierta; la que no se vio en esta sesión se deja como está. Una propuesta no se da por aceptada por no haberla rechazado. Si la aceptada es de clase `afirma` (el nombre de la clase en la cola no cambia), se añade la línea `aportacion: "…"` a la cabecera de ese archivo con un reemplazo exacto en «otros»; `cerrar.py` no mueve `actualizado` cuando el cambio se queda en la cabecera. Una de clase `candidato-entregable` o `contradiccion` aceptada no crea ni corrige nada sola: si la sesión no la resolvió (el entregable con la skill `entregable`, la contradicción con una decisión), queda como una línea nueva en «Siguientes pasos» que diga qué piezas y qué hacer con ellas, y entonces se borra de la cola.

**1. Lo que se hizo y aún no está en la carpeta.** Lo producido se guarda al crearlo, así que esto no debería pasar; si algo de la sesión (un documento, un PDF, un análisis) solo existe en la conversación, se guarda ahora en `entregables/` o en `taller/` como borrador, antes de registrar nada. Lo mismo con lo que la app haya dejado en «Claude outputs» durante esta sesión: se mueve a este proyecto y deja de estar ahí.

**2. `sesiones.md`.** Entrada nueva arriba del todo, que se enseña junto a las decisiones y el `Estatus` antes de escribir, fechada con la línea HOY de `abrir.py`, con el formato de `escribir.md` (sección 4), sin tocar las anteriores: «Tema» y «Avances», más la de quién trabajó y con qué versión del plugin (la de `plugin.json`, la misma que la llamada 1 de abrir; quien trabaja sin el plugin escribe con qué lo hizo, por ejemplo «sin plugin, Gemini»). Lo que sigue no va aquí: va en «Siguiente» del `Estatus`. Si una sesión no cabe en esas líneas, es que hubo decisiones y esas van a su archivo.

**3. `decisiones.md`, solo si hubo decisiones.** Antes de escribir, se listan al usuario las decisiones detectadas, cada una como va a quedar escrita, y se pide confirmación explícita; la respuesta termina ahí y el cierre sigue en el turno siguiente, con el sí. También cuando la persona dictó la decisión en el mismo mensaje en que pide cerrar: dictarla no es confirmar la entrada. El registro no se puede corregir después, así que nada entra sin que alguien lo confirme. `Descartado`, `Reemplaza` y `Afecta a` van solo si hay algo que decir: nunca «no consta» ni «ninguno». Las líneas van en este orden, con `Afecta a` la última. Formato:

```markdown
## 2026-08-29 · Las órdenes bajo 5.000 MXN no pasan por aprobación
Decidió: Ana Pérez
Por qué: el 70% del volumen son órdenes pequeñas y consumían el 80% del tiempo de aprobación, según el export de órdenes de 2025.
Descartado: tope acumulado mensual por proveedor, porque el ERP no expone el acumulado en tiempo real.
Afecta a: entregables/flujo-aprobacion.md (el paso de validación ya no aplica a todas) · finanzas/cierre-mensual (menos órdenes que conciliar)
```

Si la decisión sustituye a una anterior de este proyecto (cambia de criterio, de precio, de fecha), lleva además `Reemplaza: <identificador de la anterior> · <su título>`, antes de `Afecta a`; se pregunta en el mismo mensaje que enseña la decisión cuando el extracto de la sesión lo sugiere («antes…», «ya no…», «en vez de…»). La anterior no se toca.

**Responder un cuestionamiento.** Si al abrir se avisó de un cuestionamiento abierto a este proyecto y lo respondió en la sesión el responsable, o quien colabora si la decisión cuestionada es suya (lo dicen CUENTA EN EL PROYECTO y el `Decidió` de la decisión), la respuesta es una decisión más de esta lista, aunque solo mantenga lo que ya estaba: «lo mantengo» cambia algo, porque cierra una pregunta que alguien tenía abierta. La entrada lleva `Responde a: <identificador del cuestionamiento>` (el que se citó al abrir), dice en el título si mantiene o reemplaza lo cuestionado, y en `Por qué` la razón que dio el responsable. Se confirma como cualquier decisión y se dice a quién avisar: a quien lo planteó. Además, Claude se lo enseñará a esa persona la próxima vez que abra sesión en su proyecto.

**Plantear un cuestionamiento.** Si la persona quiere cuestionar una decisión de otro proyecto o una premisa, se escribe en el `decisiones.md` del proyecto activo, con el formato de `escribir.md`, sección 4 (`Planteó`, `Por qué`, `Cuestiona a`), después de enseñárselo y con su confirmación, como una decisión. Se le dice a quién avisar: al responsable de lo cuestionado.

Una decisión es un compromiso que cambia lo que se va a construir. Una preferencia expresada en voz alta no lo es. Ante la duda, se pregunta.

Si la decisión trae análisis detrás (opciones comparadas, tablas, cifras), el análisis va a un entregable del proyecto y la entrada lo cita. La entrada se queda con lo justo para entenderla sin abrir nada más.

Antes de confirmar, si el título o el `Por qué` nombran un `area/proyecto` de la raíz que no está en `Afecta a`, se propone añadirlo: sin esa línea, su responsable no recibe aviso. `Afecta a` admite también un área entera (`area/`), que avisa en cualquier proyecto del área.

Si `Afecta a` nombra un proyecto de otra área, se dice al usuario a quién tiene que avisar: el responsable de esa área, según `guia.md` o su `area.md`. La carpeta no notifica a nadie y la skill tampoco.

Si el proyecto activo lo lee todo el equipo y la decisión toca a un área o a un proyecto restringido, `Afecta a` lleva su nombre y nada más, porque ese nombre ya está listado: ni sus archivos, ni lo que contiene. Al revés, una decisión que se registra dentro de una carpeta restringida sí puede nombrar cualquier proyecto al que afecte.

**4. `proyecto.md`.** Se ponen al día `Estatus` y `Siguientes pasos`. Es un archivo vivo: lo que deja de ser cierto se sustituye, no se acumula. `Siguientes pasos` se edita, no se vuelve a escribir entero: se quitan los pasos hechos, se añaden los nuevos y se cambian solo las frases que la sesión dejó viejas, con reemplazos exactos (los `reemplazos` de `cambios.json`). Si un texto viejo no aparece exactamente una vez (la tarea del tablero pudo poner una fecha en esa línea), `cerrar.py` lo devuelve en `sin_match`: se relee el archivo, se ajusta el reemplazo y se repite solo con él.

El `Estatus` se reescribe entero desde lo que pasó en esta sesión, con la plantilla de las cuatro preguntas (qué se completó, qué sigue, qué falta decidir, qué preocupa) y la forma y la voz que da `escribir.md` (sección 3 y «La voz del `Estatus`»); lo lee todo el equipo, en la carpeta y en el tablero de cada uno, así que nada de `restringido/` ni datos personales. **Se enseña antes de escribir**, en el mismo mensaje que la entrada de la bitácora y las decisiones, y se escribe con el sí de la persona, como ellas; si pide cambiarlo, se cambia y se vuelve a enseñar. El `Estatus` lo escribe la sesión, nunca el tablero. Si el proyecto no tenía `Estatus`, se crea debajo del título. `cerrar.py` retira un «En corto» que quede al lado. Si todavía tiene «Estado actual» o «Terminado significa» (una raíz sin migrar), no se tocan: los saca la migración de la apertura (`migracion.md`, junto a este archivo).

**5. Bloque `Proyectos` de `area.md`.** Se reescribe la línea de este proyecto y, debajo, una línea por cada entregable `vigente`, que es su `aportacion` con su fecha `actualizado`: en `cambios.json` cada entregable va como `{"archivo": "x.md"}` y `cerrar.py` arma la línea desde su cabecera; solo un entregable sin `aportacion` va con la línea escrita. Solo esa parte del bloque; las líneas de los demás proyectos no se tocan.

**6. Cabeceras de lo que se tocó.** `actualizado` lo pone `cerrar.py` en cada archivo que escribe; si se usó una fuente nueva, se añade a `basado_en` con un reemplazo exacto sobre la cabecera (en los `reemplazos` de `proyecto.md`, o en «otros»).

**7. Lo que entró en `fuentes/` o en `taller/`.** Si durante la sesión se guardó algo en `fuentes/` sin haber pasado por la pregunta de si es confidencial, se pregunta ahora: si trae datos personales, facturación, contratos, credenciales o cualquier cosa que no todos deban ver, se propone llevarlo a `restringido/` del mismo proyecto y dejar su fila en el `fuentes/inventario.md` público. El usuario decide; nada se mueve sin que lo confirme.

**8. Traspasos.** Si en la sesión entró algo de otra raíz, la entrada de `sesiones.md` lo dice: qué vino, de qué raíz, quién lo pidió. Lo que se quedó fuera no se nombra.

**9. Rotación.** Si `sesiones.md` o `decisiones.md` supera las 1.500 líneas o cambia el año, se archiva como dice `escribir.md`, sección 8. Sin preguntar.

**10. El `Estatus` del área.** Se reescribe el `Estatus` de `<area>/area.md` con la forma y la voz que da `escribir.md` (sección 2, «Estructura de `area.md`»): cómo está el área después de esta sesión, con sus prioridades debajo de «Siguiente» y una línea por proyecto activo. Al cerrar no se relee el área: se parte del `Estatus` anterior del área (en un área sin migrar, de su «Panorama» y sus «Prioridades ahora», que `cerrar.py` retira al escribir el `Estatus`; las prioridades que el nuevo no traiga las añade él debajo de «Siguiente» y las devuelve en `fundidas`) y de lo que esta sesión ya leyó y escribió, y de los demás proyectos del área solo se mira, en una sola llamada, la cabecera y el `Estatus` (o «En corto», sin migrar) de los que tienen `actualizado` posterior a la fecha del `Estatus` del área, o de todos si no había uno con fecha. Las prioridades se quedan como estaban salvo que el responsable del área las cambie en esta sesión. Se enseña con el `Estatus` del proyecto y va en la misma escritura de `area.md` que el paso 5. Solo si la cuenta que cierra es la del responsable del área; si solo colabora, o el área es de otra cuenta, se salta.

**10b. Los permisos, si cambiaron.** Si la cuenta es la del responsable de contexto y en esta sesión cambió quién escribe o qué se restringe (un área nueva, alguien añadido como responsable o colaborador, algo declarado restringido, una carpeta `restringido/` nueva), al final del cierre se propone en una línea revisar que Drive coincide, y con su sí se sigue `permisos.md`.

**11. El tablero, avisado.** Si la cuenta tiene tablero (el que se buscó al abrir), se apunta el cierre en su base, sin preguntar ni decir nada: con `ArtifactData` (se carga con `ToolSearch`), un `set` en la colección `cierres` con el documento que devolvió `cerrar.py` en `documento` (`<area>--<proyecto>--<AAAAMMDDHHMM>`, nuevo en cada cierre, así que no lleva `if_version`) y los campos `proyecto` (`<area>--<proyecto>`), `nombre` (el título de `proyecto.md`), `hora` (la `hora` que devolvió `cerrar.py`, tomada del reloj y nunca calculada a mano, como `2026-10-19T03:20Z`; una hora adelantada deja el aviso del tablero encendido hasta que llega) y `cuenta`. Uno por cada tablero de la cuenta de esa raíz (desde la 1.18 hay uno; quien tenía dos de antes, en los dos, hasta que borre uno). Al abrir el tablero, quien lo montó ve arriba que hubo sesiones que aún no muestra, con el botón que lo pone al día; la sincronización borra las marcas que recoge. No se lanza la tarea desde la conversación, porque la app pide permiso cada vez que una conversación lanza una tarea. Solo si la persona lo pide al cerrar («cierra y pon al día el tablero») se lanza con `fire_trigger`: con `list_triggers` (`enabled: true`, siguiendo `next_cursor`) se busca la tarea cuyo prompt lleva la URL del tablero (se llama «Regenerar tablero <organización>», o con « completo» si se montó antes de la 1.18), y se dispara si su aprobación es automática (`permission_mode` `auto`) y su carpeta (`derived_state.folders`) es la raíz conectada; la app pedirá permiso y la persona lo da. Si el tablero no tiene tarea o la cuenta no tiene el conector de tareas programadas, el botón no puede ponerse al día: entonces se pone al día aquí mismo, como «Sincronizar» de la skill `tablero`. Si la escritura falla, se dice en media línea y la sesión queda cerrada igual: el tablero se pondrá al día con su botón o con «sincroniza el tablero».

#### Qué respondo al terminar

Dos o tres líneas: qué archivos se escribieron y qué queda para la próxima. Si hay que avisar a otra área, se dice a quién. Si quedó algo en `fuentes/` pendiente de decidir si es confidencial, se dice. Del tablero no se dice nada si se apuntó el cierre; media línea solo si se lanzó porque la persona lo pidió, si se puso al día aquí o si algo falló. Nada más. El resumen largo ya está en los archivos.

---

### Cerrar el proyecto

Cuando el responsable dice que el proyecto terminó («cierra el proyecto», «esto ya está»). Antes se comprueba que la cuenta es la del responsable (CUENTA EN EL PROYECTO de `abrir.py`): si solo colabora, se dice que lo pida el responsable y no se cierra. Después se comprueba con él que se cumple lo que dice la segunda frase de `Objetivo` (o «Terminado significa», sin migrar); si no, se dice qué falta y se espera.

1. El `Estatus` de `proyecto.md` queda en una línea: la fecha y la frase en negrita que empieza por «Proyecto terminado el AAAA-MM-DD.» y dice cómo acabó, en lenguaje llano; `Siguientes pasos` dice que no queda ninguno propio, y lo que siga vivo se nombra con el proyecto que lo recoge.
2. La línea del proyecto en el bloque `Proyectos` de `area.md` se queda sola, sin desglosar sus entregables (`escribir.md`, «Un proyecto cerrado»).
3. Una entrada en `sesiones.md` que lo cuenta, y en `decisiones.md` solo si cerrarlo fue una decisión que alguien tomó.

Nada se borra ni se mueve: los entregables siguen con su estado y se siguen citando.

### Lo que nunca hago al cerrar

Además de las prohibiciones de `convenciones` (anexo `escribir.md`):

- Dar por cerrado un pendiente sin preguntar. Si no sé si algo quedó resuelto, lo pregunto
- Borrar de la cola del tablero un cambio que la carpeta todavía no refleja
- Registrar una decisión sin enseñarla antes y sin un sí

### Ejemplo de cierre

**Usuario:** [después de trabajar en el criterio de corte por monto de compras/automatizacion-ordenes] cierra la sesión

**Antes de escribir:**

> Detecté una decisión en la conversación de hoy:
>
> Las órdenes bajo 5.000 MXN no pasan por aprobación. Decidió Ana Pérez. Descartado: el tope acumulado mensual, porque el ERP no lo expone en tiempo real. Afecta al flujo de aprobación y al cierre mensual de Finanzas.
>
> La bitácora de hoy:
>
> ## 2026-08-29
> Tema: el criterio de corte por monto.
> Avances: criterio fijado en 5.000 MXN y descartado el tope acumulado.
> Sesión de: Ana Pérez · plugin 1.22.0
>
> El estatus quedaría así:
>
> 2026-08-29 · **Las órdenes bajo 5.000 MXN ya no pasan por aprobación; el 5 de septiembre se valida el criterio con Finanzas.**
> - **Se completó:** el criterio de corte por monto, el 29 de agosto.
> - **Siguiente:** validarlo con Luis Romero el 5 de septiembre; Ana retoma el mapa de proceso.
>
> ¿Los registro así?

**Usuario:** sí

**Respuesta al cerrar:**

> Escribí la entrada en `decisiones.md`, la sesión de hoy en `sesiones.md`, actualicé el estatus y los siguientes pasos en `proyecto.md` y la línea del proyecto en `compras/area.md`. La decisión cita `entregables/flujo-aprobacion.md` en «Afecta a», así que conviene revisarlo antes de publicarlo.
>
> La decisión afecta a `finanzas/cierre-mensual`. Avísale a Luis Romero, que es el responsable de Finanzas; la carpeta no lo hace por ti.
>
> Para la próxima queda validar el criterio con Finanzas y reanudar la revisión del mapa de proceso.

## Premisas

Anexo de la skill `sesion`. Se lee cuando el responsable de contexto pide registrar, cambiar o retirar una premisa («registra como premisa que…», «la premisa P2 cambia a…», «esa premisa ya no vale»), y antes se carga el anexo `escribir.md` de la skill `convenciones`, porque se escribe en `base/`.

Solo en la sesión del responsable de contexto según `guia.md`; a cualquier otra persona se le dice que una premisa la registra él, y se le prepara el texto. Se hace en el momento en que se pide, no al cerrar, porque la dirección la confirma en voz alta y lo que importa es que quede.

1. Se lee `base/premisas.md` entero si existe. Si no existe, se crea con su cabecera (`estado: vigente`, `actualizado` de hoy) y el título `# Premisas`.
2. Se redacta la línea con el formato de la sección 2 de `convenciones`: `- P<n> · <texto> · Confirmó: <nombre y apellido> · <fecha de hoy>`, con el `P<n>` siguiente al mayor que haya en el archivo, aunque alguna esté reemplazada. Si cambia una que existe («la premisa P2 cambia a…», «ya no vale»), la línea nueva termina en `· Reemplaza P<n>`; la antigua no se toca. Quien confirma es quien dirige la organización, no quien abre la sesión, salvo que sean la misma persona: se pregunta si no está claro.
3. Se enseña la línea y se escribe solo con el sí. Se añade al final del archivo y se pone al día `actualizado`.
4. Si la premisa nueva reemplaza a una con cuestionamientos abiertos (los del barrido al abrir), se dice que quedan respondidos y a quién avisar: a quien los planteó. Si la premisa se mantiene frente a un cuestionamiento, no hay línea nueva: la respuesta es una entrada con `Responde a:` en el `decisiones.md` de un proyecto del responsable de contexto, como cualquier otra (paso 3 de cerrar).

Una premisa es algo que la dirección confirmó y sobre lo que todos construyen; un objetivo de un proyecto o una preferencia de un área no lo es. Ante la duda, se pregunta de quién es la confirmación.

## Publicar un documento
### Las cinco comprobaciones

**1. Trazabilidad.** Cada afirmación no obvia sale de un archivo citado. Se listan las que no salen de ninguno. Si `basado_en` está vacía (`[]`), se dice desde la primera línea: el documento no se puede publicar así. Si cita una fuente de otra área o un archivo guardado en `restringido/`, también es bloqueante: de otra área solo se citan entregables vigentes y decisiones, y lo restringido se cita por su fila de `inventario.md`. Si el entregable lo lee todo el equipo y cita algo restringido, es bloqueante siempre: la cita solo va en la otra dirección.

**2. Coherencia con las decisiones.** Nada en el documento contradice una entrada de `decisiones.md`, ni siquiera de hace meses.

**3. Frescura.** Ningún archivo de `basado_en` tiene una fecha `actualizado` posterior a la del entregable. Si la tiene, se dice qué cambió aguas arriba.

**4. Huecos.** Los huecos declarados en el documento siguen abiertos, o ya hay material para cerrarlos.

**5. Estilo.** Los siete patrones de la skill `estilo`. Se cuentan los guiones largos y se comparan con el umbral: más de uno cada 500 palabras es muletilla. Las cifras sin fecha ni fuente se buscan aquí, pero no son estilo: son bloqueantes, porque el contrato las prohíbe.

### Requisitos

1. La revisión se pasó y no quedan hallazgos bloqueantes
2. No hay huecos abiertos, o el responsable del proyecto los acepta de forma explícita y quedan escritos en el documento
3. `basado_en` no está vacía y la cabecera lleva `aportacion` (si falta, se escribe ahora, con el responsable, porque es la línea del índice del área). Si el documento es material adoptado y no hay forma de reconstruir sus fuentes, el responsable del proyecto acepta el hueco de forma explícita y queda escrito en el documento, en una línea bajo el título: de quién venía el material, con qué fecha y por qué no hay trazabilidad. Esa línea no nombra rutas ni carpetas del sistema del que se migró
4. **Lo pide el responsable del proyecto, y se comprueba.** El responsable es quien figura en `Quién participa` de `proyecto.md`, y su cuenta está junto a su nombre en `guia.md`, la primera de la celda Cuenta, antes de «colabora:». Quien colabora en el área o en el proyecto no publica: su cuenta no cuenta como la del responsable. Se contrasta contra la cuenta desde la que se abrió esta sesión. Si no coinciden, no se publica, y se dice quién tiene que pedirlo. Si la identidad de la cuenta no está disponible, se pregunta quién lo pide y se anota en `sesiones.md` de quién vino la petición

Si falta cualquiera de los cuatro, se dice cuál falta y no se publica.

