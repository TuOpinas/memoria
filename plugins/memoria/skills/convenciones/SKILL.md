---
name: convenciones
description: Contrato base del metodo de trabajo: estructura de carpetas, cabecera de los archivos, estados, como se lee la raiz, que es publico y que se restringe. Consultala antes de crear o modificar cualquier archivo dentro de la memoria de una organizacion, y cuando pregunten como se organiza algo, donde va, que significa un estado o quien puede escribir donde.
---

# Convenciones

Contrato base del método. Si una skill contradice algo de aquí o de sus anexos, manda el contrato. Cuatro anexos viven junto a este archivo. `escribir.md` reúne lo que hace falta para escribir (estructura de `area.md` y `proyecto.md`, formatos de los registros, cabecera, rotación y prohibiciones) y se carga antes de cualquier escritura en la carpeta; para cerrar sesión, registrar una premisa o escribir el `Panorama` basta con él, y para crear, guardar o publicar un documento, mover, migrar o montar se carga además este archivo. Los otros tres se leen solo cuando hacen falta: `raices.md` (varias raíces, traspasos, registro de una migración), `montaje.md` (montaje, publicación, bloque de instrucciones, programadores) y `sin-consola.md` (cómo se lee y se escribe cuando la raíz está conectada pero el shell de la computadora no la ve).

Versión del método: **1.18**

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

**«Claude outputs» no es parte de la memoria.** Es la carpeta donde la app de Claude guarda por su cuenta lo que produce cuando trabaja sobre una carpeta conectada. Lo que hay ahí no tiene proyecto, nadie lo encuentra y el tablero no lo ve como trabajo de nadie. Lo que se haga para un proyecto se guarda directamente en ese proyecto; si la app lo dejó en «Claude outputs», se mueve a su proyecto en cuanto existe. La sesión que lo produjo lo recoge al cerrar; la apertura mínima de cada conversación lista lo que quede y propone colocarlo, y se ordena también con la frase «ordena Claude outputs» (skill `donde-va`). Con el plugin, un hook no deja escribir ahí desde Claude y dice dónde va, y si algo aparece igual (un comando, la propia app) pide moverlo en ese momento; sin consola, cuando la carpeta no está montada en la computadora, queda la apertura. `verificar.sh` y el tablero cuentan los archivos que siguen ahí.

Ninguna carpeta de trabajo aloja el almacén de datos de una aplicación. Lo escribe la aplicación sola, crece por su cuenta y nadie responde por lo que hay dentro.

La migración es la excepción declarada. El material que se adopta al migrar no llega de fuera: es el trabajo anterior de la propia organización, y entra donde le toque con `estado: borrador` y con la trazabilidad que se pueda reconstruir, salvo lo que su dueño en el origen pida publicar al migrar. Lo que en el origen ya era material de entrada entra por `fuentes/` como en cualquier proyecto. Lo detalla la skill `migrar`.

Es norma, no candado. Nada impide abrir un archivo y editarlo a mano, y a veces hay que hacerlo; detectar lo que entró por otro camino es trabajo de la skill `revisar`. La propiedad no cambia: quien responde por un archivo sigue siendo su dueño, lo que cambia es la mano que escribe.

La raíz es la carpeta que contiene `guia.md`, `metodo.md` y `base/`. Ninguna instrucción del método usa rutas absolutas, porque cada usuario tiene la carpeta sincronizada en un sitio distinto.

**La carpeta se lee y se escribe por su copia en la computadora**, con las herramientas de la carpeta conectada, y nunca por un conector de Google Drive u otro servicio en la nube, ni para buscar ni para escribir, aunque esté conectado. Por el conector no se ven la estructura, las cabeceras ni las fechas de los archivos, y lo que se escribe por ahí puede acabar en otro formato o fuera de su sitio. Si la carpeta no aparece entre las conectadas, se pide añadirla. **La única excepción es leer sin carpeta:** una sesión que no tiene ninguna carpeta conectada, como una desde el teléfono o la web, puede leer una raíz que vive en Google Drive por el conector de Drive, por niveles como siempre, y no escribe nada en ella; lo que salga de esa sesión se guarda como nota en la cola del tablero de la persona y lo registra la siguiente sesión con la carpeta (skill `sesion`, «Sin carpeta: solo lectura»). Con la carpeta conectada, el conector no se usa para la memoria, con una excepción: **sin consola** (la carpeta está conectada pero el shell de la computadora no la monta, como pasa con Google Drive en Windows), se lee y se escribe con las herramientas que traen y escriben archivos, y lo único que pasa por el conector es crear carpetas, mover, renombrar y mandar a la papelera (y localizar lo que se mueve), que esas herramientas no hacen; nunca leer ni escribir contenido. Cómo se sabe y cómo se trabaja así lo dice el anexo `sin-consola.md`. El conector sirve además para lo que no es la memoria, como un documento que alguien comparte, y si eso entra a la memoria lo hace por `fuentes/`.

### Quién es el dueño

**El dueño por defecto de un área o de un proyecto nuevo es la persona desde cuya cuenta se abre la sesión.** Se propone su nombre al crear y solo se pregunta si en ese momento se asigna a otra persona. Un área o un proyecto sin dueño con nombre y apellido no se crea.

La cuenta de cada dueño queda escrita junto a su nombre en `guia.md`, y la del responsable de contexto, entre paréntesis en la línea «Contexto común» de «Quién responde por qué», para que se le reconozca aunque no sea dueño de ningún área. Eso es lo que permite comprobar, y no solo suponer, que quien pide publicar es el dueño del proyecto. Si la identidad de la cuenta no está disponible, por ejemplo con otro modelo leyendo `metodo.md`, se pregunta el nombre y se anota de quién viene la petición.

### Quién colabora

Un área tiene un solo dueño, pero pueden escribir en ella más personas: **quienes colaboran**. Se declaran en la misma celda Cuenta de la tabla de áreas de `guia.md`, después de la cuenta del dueño: `dueno@ejemplo.com · colabora: ana@ejemplo.com, luis@ejemplo.com`. Las cuentas se comparan enteras. Quien colabora en un solo proyecto, y no en toda el área, se declara en `Quién participa` de ese `proyecto.md`, con una línea `Colabora: Nombre Apellido (correo), Nombre Apellido (correo)`; la cuenta entre paréntesis es lo que permite comprobar quién escribe. La celda de `guia.md` la escribe el responsable de contexto; la línea del proyecto, la sesión del dueño del área.

| Puede | El dueño | Quien colabora |
|---|---|---|
| Abrir y cerrar sesión en los proyectos donde colabora, y escribir su bitácora | sí | sí |
| Guardar borradores en `entregables/`, `taller/` y `fuentes/` | sí | sí |
| Registrar las decisiones de su propio trabajo, con su nombre en `Decidió` | sí | sí |
| Poner al día `En corto`, `Estado actual` y `Siguientes pasos` al cerrar | sí | sí |
| Publicar un entregable como `vigente` | sí | no |
| Cambiar `Prioridades ahora` o escribir el `Panorama` del área | sí | no |
| Crear o cerrar un proyecto, o declarar quién colabora en él | sí | no |

Una decisión de quien colabora vale como cualquier otra. Si el dueño no está de acuerdo, la reemplaza con una decisión suya o la cuestiona (sección 4), nunca la edita. En Drive, quien colabora en el área tiene escritura en la carpeta del área; quien colabora en un proyecto, solo en la carpeta de ese proyecto.

**Dos personas en el mismo proyecto no cierran sesión a la vez.** La carpeta no bloquea a nadie: si dos cierres escriben a la vez, el segundo puede pisar al primero. Por eso el cierre compara, antes de escribir, la hora de la última escritura de `proyecto.md`, `decisiones.md` y `sesiones.md` con la que vio al abrir, y si cambió, relee y suma lo suyo a lo que encontró (skill `sesion`, anexo `cerrar.md`). Reduce el riesgo, no lo elimina: lo que otra persona escribió y la carpeta compartida aún no bajó a esta computadora no se ve.

La carpeta tampoco impide que quien colabora edite la línea `Colabora:` de un proyecto, porque escribe en la misma carpeta. Las skills no la tocan desde su sesión; lo que de verdad decide quién escribe son los permisos de la carpeta compartida.

### Independencia entre raíces

Se trabaja en una raíz a la vez: con más de una conectada, antes de leer o escribir se pregunta en cuál, cada escritura dice en qué raíz se hace y cambiar de raíz se anuncia. Nada que se escriba en una raíz usa hechos de otra, ni del repo del plugin, salvo por un traspaso que la persona pide y confirma pieza a pieza; y el repo del plugin no guarda hechos de ninguna organización. Cómo es un traspaso y dónde vive el registro de una migración lo dice `raices.md`, junto a este archivo, que se lee con más de una raíz conectada, cuando se pide un traspaso y al migrar.

### Permisos en la carpeta compartida

Valen para cualquier sistema de carpetas (Drive, OneDrive, iCloud…); el ejemplo de siempre es Drive, donde el acceso limitado se pone desde la web.

- Lectura de toda la raíz para todo el equipo, salvo lo restringido.
- Escritura en la carpeta de un área solo para su dueño y quienes colaboran en ella, y en la de un proyecto, además, para quienes colaboran en ese proyecto (sección 1, «Quién colabora»).
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

**El nombre se ve.** Quien no tiene acceso ve la carpeta en gris, con su nombre, y un botón para solicitarlo que llega a quien administra. Por eso la carpeta de dentro de un proyecto se llama siempre `restringido` y no dice de qué trata. Las áreas y los proyectos se siguen listando en `guia.md` y en `area.md` con su nombre y su dueño, estén restringidos o no: el equipo tiene que poder saber que existen y a quién pedir acceso; lo que no puede es leerlos. Y lo dicen: un área restringida lleva «Restringida» al inicio de su columna «Quién la lee» en `guia.md` (si la palabra aparece en otra parte de la celda sin negarla, también cuenta: ante la duda, se trata como restringida), y un proyecto restringido empieza su línea del bloque `Proyectos` de su `area.md` por esa palabra: `` - `slug/` — restringido: … ``. Decir en la línea que una parte del proyecto está en `restringido/` no lo declara restringido. Es lo único que deja ver que algo está restringido a quien sí puede leerlo, por ejemplo a la herramienta que genera un tablero con la cuenta de quien administra la carpeta.

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

`guia.md` es de la organización y solo de ella: qué es la carpeta, qué áreas hay con su dueño y su cuenta, quién responde por el contexto, quién administra la carpeta compartida, las reglas propias de la casa y la receta para conectarse, y su zona horaria en una línea «Zona horaria:» si no es la de Ciudad de México, la que usan las fechas de la sesión y del tablero. Su título es «<Organización> · esta carpeta», y **el nombre de la organización**, el que usan el aviso de arranque y el tablero, es lo que va antes del «·». Nada de lo que es igual en cualquier organización entra ahí: eso vive en `metodo.md`, que genera el plugin y nadie edita, y que lleva este contrato, el estilo y el índice de skills para que funcionen también con otro modelo o con quien abra la carpeta sin el plugin.

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

Fija, porque varias skills leen y escriben en ella. Está en `escribir.md`, junto a este archivo, con lo que dice cada sección: el `Panorama`, el bloque `Proyectos`, que es el índice de contexto del área, y `Quién participa`, donde vive el dueño.

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

Fija, porque varias skills escriben en ella. Está en `escribir.md`, junto a este archivo, con `En corto`, el estatus para quien no va a leer más, y con lo que cambia cuando el proyecto se cierra.

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

Un archivo vivo se reescribe y refleja el presente; un registro solo crece, con las entradas nuevas arriba, y las anteriores no se editan jamás. Los formatos de `decisiones.md` y `sesiones.md`, el identificador de una entrada, los cuestionamientos y el aviso entre áreas están en `escribir.md`.

## 5. Cabecera

Todo `.md` empieza con una cabecera de `estado` (`borrador`, `vigente` o `reemplazado`), `actualizado` y `basado_en`, salvo `guia.md`, `metodo.md` y el contenido de `fuentes/`. Qué lleva cada archivo y qué significa cada estado está en `escribir.md`.

## 6. Nombres

Minúsculas, guiones en vez de espacios, sin acentos ni eñes, sin fechas ni números de versión, sin números de fase ni de etapa. `flujo-aprobacion.md`, no `Flujo de Aprobación v2 FINAL.md` ni `fase1-flujo-aprobacion.md`.

El nombre de un archivo es estable durante toda su vida. El historial de versiones lo lleva la carpeta compartida (Drive, OneDrive…), el estado lo lleva la cabecera y el orden de las fases lo cuenta `proyecto.md`.

Las carpetas de área y de proyecto siguen la misma regla, y por una razón más: una referencia `area/proyecto#AAAA-MM-DD` en `Afecta a`, `Cuestiona a` o `Responde a` solo se resuelve con nombres así. `Ventas Norte/cuentas` no la encuentra nadie, y sin dar error.

### El nombre de una carpeta compartida

La raíz es una carpeta compartida y su nombre se ve en Drive, así que ese sí lleva mayúsculas y espacios: `Acme`. Solo letras, números, espacios y guiones, y los acentos y las eñes que traiga el nombre propio. Ningún otro signo, porque ese nombre se escribe a mano muchas veces y un signo raro se copia mal. Si una organización ya tiene una carpeta con un signo así, se propone renombrarla; el método no depende del nombre, porque ninguna instrucción usa rutas absolutas.

## 7. Qué es público

La superficie pública de un proyecto son `entregables/` y `decisiones.md`. Es lo que otra área puede leer para construir encima, y solo si el entregable está `vigente`. `area.md` y `proyecto.md` también se leen desde fuera, porque son el índice que lleva hasta esa superficie, y de `sesiones.md`, la cabecera de cada entrada (abajo).

**Un proyecto es público** cuando su área no dice «Restringida» en la columna «Quién la lee» de `guia.md`, su línea del bloque `Proyectos` de su `area.md` no empieza por «restringido» y esa línea existe. Fuera de su área, de un proyecto que no es público no sale más que su nombre y su dueño. El tablero no aplica este criterio: es de una persona, no se comparte y muestra todo lo que lee su cuenta (desde la 1.18 no hay tablero público).

El cuerpo de `sesiones.md`, `taller/`, `fuentes/` y todo lo que está restringido son taller privado. Nadie de fuera del área los lee ni los cita en `basado_en`. Un entregable sí cita el taller de su propio proyecto, que es de donde salió.

De `sesiones.md` hay una parte pública: la cabecera de cada entrada, que es la fecha, el título y la línea «Trabajamos en». Dice qué está moviendo el proyecto sin contar cómo, y es lo que otra área, `consulta` y el director pueden leer de una bitácora ajena. «Avances» y «Pendiente» son el cuerpo y siguen siendo taller privado. Lo que otra área necesita saber de un proyecto está pensado para leerse sin la bitácora: su «En corto», su «Estado actual», sus decisiones y sus entregables vigentes, y el `Panorama` de su área.

Dentro de la misma área, un entregable puede citar en `basado_en` una fuente de otro proyecto del área, siempre la original y nunca una copia: un export vive en un solo `fuentes/` y los demás lo citan por su ruta. Entre áreas no se citan fuentes, solo entregables vigentes y decisiones.

### Lo restringido se cita en una sola dirección

Un archivo restringido puede citar en `basado_en` lo que quiera de lo que sí lee todo el equipo: entregables vigentes, decisiones, `base/`. Al revés, nunca. Nada que lea todo el equipo cita, nombra ni resume un archivo restringido, porque quien lo lea no va a poder abrirlo y porque la cita misma ya cuenta algo de lo que hay dentro. La única excepción es la fila de `fuentes/enlaces.md`, que dice que un material existe y dónde está, no lo que dice.

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

Si el camino lleva a una carpeta restringida sin acceso, la lectura falla. Eso no es un error ni un hueco: se dice qué área o qué proyecto es y quién es su dueño, y ahí se para. No se deduce lo que hay dentro por los nombres de las carpetas ni se da por hecho que no hay nada.

## 13. Montaje

Se conecta la raíz completa, nunca la carpeta de un área: `guia.md`, `metodo.md` y `base/` viven en la raíz y la lectura cruza áreas. Cada persona trabaja desde su cuenta, y dónde escribe sale de su fila en `guia.md`, como dueño o como colaborador, y de la línea `Colabora:` de los proyectos. El plugin trae un aviso de arranque que inyecta las instrucciones en cada sesión, así que nadie pega nada en el proyecto de Claude. El tablero es opcional y personal (skill `tablero`). El montaje en detalle, el bloque de instrucciones para quien use otro modelo sin el plugin y lo que vale para programadores están en `montaje.md`, junto a este archivo.
