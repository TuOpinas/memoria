---
name: nuevo
description: Da de alta lo que falte en la memoria de la organizacion: monta la raiz si la carpeta no tiene guia.md, crea el area si no existe y crea el paquete completo de un proyecto. Usala cuando digan 'nuevo proyecto', 'arranca un proyecto para...', 'necesito documentar esto como proyecto', 'nueva area', 'crea el area de...', 'monta la carpeta de...', 'nueva organizacion', 'arranca el metodo para este cliente', o cuando se trabaje en algo que todavia no tiene carpeta.
---

# Nuevo

Dar de alta lo que falte, de fuera hacia dentro: la raíz de la organización, el área, el proyecto. La skill detecta en qué nivel está la carpeta conectada y empieza por ahí. Antes de nada se carga `convenciones`, y al montar una raíz también su anexo `montaje.md`, que dice cómo se conecta cada persona: sus prohibiciones aplican a todo lo que sigue.

## Cuándo

"Nuevo proyecto", "arranca un proyecto para X", "necesito documentar esto como proyecto", "nueva área", "crea el área de operaciones", "monta la carpeta de Acme", "nueva organización", "arranca el método para este cliente", o cuando alguien empieza a trabajar en algo que todavía no tiene carpeta.

También cuando una conversación de trabajo lleva veinte minutos sobre algo que no existe en ninguna carpeta. En ese caso se propone crear el proyecto, no se crea sin avisar.

## Qué leo antes de escribir nada

1. La carpeta conectada: si tiene `guia.md`. Si no lo tiene, falta la raíz y se empieza por el nivel 1. Si tiene documentos de otra estructura, se para y se propone `migrar` después de montar la raíz
2. `guia.md`: qué áreas hay, quién responde por cada una, y las reglas propias de la casa. Si el área del dueño no está, falta el área y se pasa por el nivel 2
3. El bloque `Proyectos` del `area.md` que toca: qué proyectos hay ya, para no duplicar
4. El nombre de la carpeta conectada: si trae algún signo que no sea letra, número, espacio o guion, se dice y se propone renombrarla antes de seguir. Un nombre que no se puede teclear se copia mal y se escribe distinto cada vez

Nada más. Dar algo de alta no necesita abrir `base/` ni ningún proyecto.

Si el proyecto se parece a uno existente, se dice antes de crear nada. Dos proyectos sobre el mismo tema son la forma más rápida de romper el sistema. Lo mismo con un área parecida a otra.

## El dueño

**El dueño por defecto es quien abre la sesión.** Se propone su nombre y su cuenta, y solo se pregunta si en este momento se asigna a otra persona:

> Lo creo contigo como dueño, o dime de quién es.

Si la identidad de la cuenta no está disponible, se pregunta el nombre y apellido y se espera: un área o un proyecto sin dueño no se crea.

Las demás preguntas de cada nivel se hacen juntas, en una sola tanda, en lenguaje llano. Nadie tiene que saber qué es un alcance ni un entregable para responderlas. Si el usuario responde a medias, se crea igual con lo que haya y lo que falta queda marcado como hueco.

---

# Nivel 1. La raíz

Solo si la carpeta no tiene `guia.md`. Se hace una vez por organización.

## Las cuatro preguntas

1. ¿Cómo se llama la organización?
2. ¿Quién mantiene el contexto común, la parte de quién sois y qué usáis? Por defecto, quien abre la sesión
3. ¿Qué sistemas usáis a diario? Nombre y para qué, aunque sea una lista rápida
4. ¿Hay ya una primera área con la que empezar, y de quién es?

Y una más, que se pregunta siempre porque de ella cuelga todo lo restringido: ¿quién administra la carpeta compartida? Tiene que ser el dueño de la organización o una persona de su total confianza, porque quien administra puede quitar cualquier restricción.

## Qué escribo y dónde

**1. `guia.md`.** Es lo único de la raíz que es de la organización, y cabe en una pantalla. No lleva cabecera de método y no repite nada de `metodo.md`:

```markdown
# [Organización] · esta carpeta

Esta carpeta es la memoria de trabajo de [organización]: cada área documenta aquí sus
proyectos, y la IA la lee antes de ayudar a cualquiera. Cómo se trabaja está en
`metodo.md`, que no hace falta leer: lo aplica el plugin `memoria` cuando trabajas
con Claude. Aquí solo está lo nuestro.

## Áreas

| Área | Qué es | Dueño | Cuenta | Quién la lee |
|---|---|---|---|---|
| `comercial/` | … | Nombre Apellido | correo@… | Todo el equipo |
| `nordia/` | … | Nombre Apellido | correo@… | Restringida |

La cuenta es con la que esa persona trabaja con la IA. Es lo que permite comprobar
que quien pide publicar algo es su dueño.

## Quién responde por qué

Contexto común (`guia.md` y `base/`): [nombre y apellido].
Administra la carpeta compartida y pone o quita los accesos: [nombre y apellido].
Cada área, su dueño de la tabla de arriba.

## Reglas propias de la casa

[Solo si las hay. Lo que el método no puede prever porque es nuestro: un tipo de dato
que aquí cuenta como confidencial, una convención de nombres, vocabulario que conviene
fijar. No pueden contradecir `metodo.md`; si alguna lo hace, manda `metodo.md`.]

## Cómo conectarte

Se hace una sola vez y lleva unos 15 minutos. Sigue los pasos en orden y no te saltes
ninguno.

**Paso 1. Comprueba que tu computadora sirve**

Necesitas una Mac con macOS 14 (Sonoma) o más nuevo, o una computadora con Windows 10 o
Windows 11, y una cuenta de Claude de pago (Pro, Max, Team o Enterprise). En Windows,
mejor la edición Pro, Enterprise o Education: en Windows Home la función de carpetas
puede no funcionar, y el verificador de abajo te lo dice. Deja también espacio libre en
el disco: la primera vez la app descarga más de 1 GB, y con el disco lleno no se instala.

1. Descarga el verificador de Claude para tu computadora:
   - Mac: https://claude.ai/api/desktop/darwin/universal/cowork-readiness-check/latest/redirect
   - Windows: https://claude.ai/api/desktop/win32/x64/cowork-readiness-check/latest/redirect
   - Windows con procesador Snapdragon (ARM):
     https://claude.ai/api/desktop/win32/arm64/cowork-readiness-check/latest/redirect
2. Abre el archivo que se descargó. No instala nada.
3. Si dice **This computer is ready for Cowork**, sigue al paso 2.
4. Si dice otra cosa, haz una captura de pantalla y mándasela a quien administra la
   carpeta (lo dice «Quién responde por qué», arriba). No sigas hasta resolverlo.

**Recomendado: un lector de archivos Markdown**

Los documentos de la carpeta son archivos `.md`. Sin un lector se ven como texto lleno de
símbolos; con uno se ven como un documento normal. No es obligatorio: Claude los lee
igual. Algunas opciones, solo como sugerencia:

- Mac, la más completa: **OpenMark**, en la App Store (pago único de 9.99 USD; con la
  misma compra lo tienes en iPhone y iPad). Pide macOS 26.
- Mac, gratis: **QLMarkdown**, para verlos con la barra espaciadora desde el Finder. Es
  la opción si no quieres gastar o si tu Mac tiene una versión anterior a macOS 26.
- Windows: **PowerToys** de Microsoft (gratis), que los muestra en el panel de vista
  previa del Explorador de archivos, o **MarkText** (gratis).

Úsalo para leer; los cambios se los pides a Claude. Abre los archivos de uno en uno: no
abras la carpeta entera como «bóveda» o espacio de trabajo en apps como Obsidian, porque
crean dentro su propia carpeta de configuración.

**Paso 2. Instala la app de Claude**

Todo se hace en la app de Claude para computadora, no en el navegador ni en el teléfono.

1. Entra en claude.com/download y descarga la app.
2. Instálala:
   - Mac: abre el archivo descargado y arrastra **Claude** a la carpeta **Aplicaciones**.
   - Windows: abre el archivo descargado y pulsa **Instalar**. Si te pide contraseña de
     administrador, pídesela a quien se encarga de las computadoras.
3. Abre Claude e inicia sesión con tu cuenta.
4. Si arriba ves dos opciones, **Chat** y **Cowork**, elige **Cowork**. Todo lo que sigue
   se hace ahí.

**Paso 3. Ten la carpeta en tu computadora**

La carpeta de [Organización] tiene que estar en tu computadora, no solo en internet.

1. Si vive en Google Drive, instala **Google Drive para escritorio** (google.com/drive/download)
   e inicia sesión con el correo con el que te compartieron la carpeta.
2. Si te la compartieron y no la ves en tu computadora, entra en drive.google.com, búscala
   en **Compartido conmigo** y añádela a tu unidad. Así aparece en tu computadora.
3. Búscala en el Finder (Mac) o en el Explorador de archivos (Windows), no en la web.
   Haz clic derecho sobre la carpeta y elige **Disponible sin conexión** (en inglés,
   **Make available offline**). Así sus archivos están siempre en tu computadora y
   Claude puede leerlos.
4. En Windows, Google Drive puede mostrar sus carpetas en una unidad aparte (por ejemplo,
   G:) que Claude no consigue conectar. Si te pasa en el paso 4, en las preferencias de
   Google Drive elige que guarde una copia de tus archivos en la computadora y conecta
   la carpeta desde esa copia.
5. Si no la ves, pídele acceso a quien administra la carpeta.

**Paso 4. Crea tu proyecto y conecta la carpeta**

1. En el menú de la izquierda, entra en **Projects** y crea uno nuevo.
2. Ponle de nombre "[Organización] · [tu área]" y déjalo privado. Por ejemplo: "[Organización] · comercial".
   Cada persona crea el suyo.
3. Conecta la carpeta **[Organización] completa**, la que tiene dentro `guia.md` y `metodo.md`. No
   elijas la carpeta de tu área: Claude necesita ver todas para decirte qué se sabe ya.
   Conéctala en el proyecto, no en una conversación suelta: así la tienen todas las
   conversaciones del proyecto.
   Si no te la pide al crear el proyecto, añádela con el botón «+».

4. Si trabajas con código, sus repositorios van en otra carpeta de tu computadora (por
   ejemplo, una carpeta Code con todos los repositorios de la organización dentro), nunca
   dentro de la carpeta de la memoria: Drive le añade archivos que confunden a Git.
   Conéctala también al proyecto.

**Paso 5. Instala el plugin Memoria**

Si tu organización ya te lo instaló, sáltate este paso.

1. En el menú de la izquierda, pulsa **Customize** y luego **Plugins**.
2. Pulsa la flechita junto al botón **Add** y elige **Add marketplace** ›
   **Add from a repository**.
3. Escribe exactamente: `TuOpinas/memoria`
4. Deja encendido **Sync automatically** y pulsa **Sync**. Así las versiones nuevas te
   llegan solas.
5. Ve a la pestaña **Discover**, busca **Memoria** y pulsa **Add**.
6. Comprueba que quedó activo, porque en algunas versiones de Claude hace falta: pulsa
   otra vez la flechita junto a **Add** y elige **Manage marketplaces**. Tiene que
   aparecer **memoria** con la etiqueta **Synced**. Pulsa **Done**. Si no aparece, repite
   los pasos 2 a 4.
7. Comprueba también que el plugin quedó encendido: en algunas versiones de Claude se
   instala apagado. Búscalo entre tus plugins y, si está apagado, actívalo.

**Paso 6. Pruébalo**

1. Dentro de tu proyecto, abre una conversación nueva.
2. Escribe: «abre sesión en» y el nombre de un proyecto de tu área.
3. Si Claude te pide permiso para usar la carpeta, elige que lo permita siempre, para que
   no te lo vuelva a preguntar.
4. Claude te dirá en qué va ese proyecto y qué propone hacer. Si lo hace, ya estás
   conectado. No hay que pegar nada en las instrucciones del proyecto.
5. Si Claude no reconoce la memoria, revisa tres cosas: que la conversación está dentro
   del proyecto, que es de Cowork (si tu versión separa Chat y Cowork) y que el plugin
   está encendido.

Para trabajar cada día bastan dos frases: «abre sesión en…» al empezar y «cierra la
sesión» al terminar. Dos cosas que conviene saber desde el principio:

- Si dos personas escriben en la misma área, que no cierren sesión del mismo proyecto
  al mismo tiempo: las dos escrituras pueden pisarse.
- Para diseñar, pídeselo a Claude en una conversación normal de tu proyecto: el diseño
  sale como un artifact y la memoria funciona como en cualquier otra conversación. No uses
  la interfaz aparte de Claude Design, que se retira en diciembre.

**Paso 7. Monta tu tablero**

El tablero es una página con toda la carpeta a la vista: áreas, proyectos, en qué va
cada uno, qué se decidió y qué sigue.

1. En una conversación de tu proyecto, escribe: «monta el tablero».
2. Claude te pedirá aprobar una tarea. Apruébala: es la que hace funcionar el botón
   **Sincronizar ahora**.
3. Espera unos minutos. Al terminar aparece una tarjeta llamada «Tablero [Organización]». Ábrela.
4. **Lo primero: abre «Ayuda»** en el índice del tablero. En pocos minutos te explica qué
   muestra cada parte y qué puedes hacer desde ahí. Cada parte tiene además un «?» con
   su explicación.

Se pone al día solo cuando lo abres después de cerrar sesiones, siempre que tu
computadora esté encendida y la app de Claude abierta. Para ver lo que escribieron otras
personas, pulsa **Sincronizar ahora**, junto al nombre de la organización. El tablero es
tuyo: si quieres compartirlo, hazlo desde su menú.

Para sumar a un compañero, abre en el tablero **Ayuda › Sumar a un compañero**: dice qué
hacer de tu lado y trae el mensaje con las instrucciones, listo para copiar.

**Paso 8. Ten el tablero siempre a mano en Chrome**

1. Abre Chrome y entra en claude.ai con la misma cuenta que usas en la app.
2. Escribe en la barra de direcciones `claude.ai/artifacts` y abre «Tablero [Organización]».
   Si no lo ves, pídele a Claude en la app «dame el enlace de mi tablero» y ábrelo.
3. Guárdalo en tus marcadores: pulsa ⌘ + D en Mac o Ctrl + D en Windows, elige
   **Barra de marcadores** y pulsa **Listo**.
4. Para que se abra solo cada vez que abras Chrome:
   - Pulsa los tres puntos ⋮ arriba a la derecha y entra en **Configuración**.
   - En el menú de la izquierda, elige **Al iniciar**.
   - Marca **Abrir una página específica o un conjunto de páginas**.
   - Pulsa **Añadir una página nueva**, pega la dirección del tablero y pulsa
     **Añadir**.
5. Si quieres, fija la pestaña: clic derecho sobre ella › **Fijar**.

Chrome solo muestra el tablero. Para que se ponga al día, la app de Claude tiene que
estar abierta en tu computadora.

**Para avanzados: instalar el plugin con comandos**

En lugar del paso 5, puedes escribirle a Claude estas dos líneas, una y luego la otra:

    /plugin marketplace add TuOpinas/memoria
    /plugin install memoria@memoria-marketplace

Después, en `/plugin`, pestaña Marketplaces, elige `memoria-marketplace` y activa la
actualización automática.

## Versión del método
La primera línea de `metodo.md` dice cuál corre esta carpeta. Se pone al día sola la
primera vez que alguien con una versión nueva del plugin abre sesión o pone al día su tablero.
```

**2. `metodo.md`.** Copia exacta del `metodo.md` del plugin, que está en la raíz de la carpeta del plugin, dos niveles por encima de esta skill, escrita en la raíz como dice «Los archivos del plugin en la computadora» en la skill `tablero` (directo desde el plugin con `device_commit_files`, nunca pegada). No se edita ni una línea: su primera línea lleva la versión y es lo que `sesion` compara al abrir.

**3. `base/contexto.md`.** Esqueleto con las secciones y cada una con su hueco marcado, para que el responsable de contexto las rellene en su primera sesión:

```markdown
---
estado: borrador
actualizado: AAAA-MM-DD
---

# [Organización]

## Quién es
[Hueco: qué hace la organización, para quién, tamaño, dónde opera]

## Cómo se organiza
[Hueco: áreas, quién responde por cada una, cómo se decide]

## Criterios transversales
[Hueco: lo que aplica a todo proyecto sin que nadie lo diga. Presupuesto, plazos, idioma, formato de los documentos, quién firma]

## Datos sensibles
[Hueco: qué tipos de datos se restringen, qué áreas no puede leer todo el equipo, qué no se cita en entregables, qué no se comparte fuera del área]
```

**4. `base/glosario.md`.** Cabecera, título y una lista vacía con el formato `término: qué significa`. Si el usuario dio siglas o nombres internos al responder, se meten ya.

**5. `base/sistemas.md`.** Cabecera, título y la tabla con sus cuatro columnas, con las filas de la pregunta 3 si las hubo:

```markdown
| Sistema | Para qué | Quién da acceso | Antes de usarlo |
|---|---|---|---|
```

**6. La primera área**, si la hay, por el nivel 2. Si no la hay, la tabla de áreas de `guia.md` queda con una fila que dice que todavía no hay ninguna.

Nada más. No se crea carpeta de plantillas, ni archivo de reglas propias en `base/`: las dos plantillas del método viven en el plugin, y las reglas propias van en `guia.md`, que ya tiene su sección.

## Qué respondo al terminar

Tres o cuatro líneas: qué se creó, quién responde por qué, y los siguientes pasos. Permisos en Drive (lectura de la raíz para todo el equipo, escritura en `guia.md` y `base/` para el responsable de contexto, escritura en cada área para su dueño, y administrar la carpeta solo quien se nombró), y rellenar `contexto.md` en una primera sesión con el responsable. Si había documentos de otra estructura, se recuerda que el siguiente paso es `migrar`.

Si quien monta la raíz mantiene el método para otros, se recuerda además abrir en su propia raíz un proyecto con el nombre de esta organización: ahí va el registro de la relación, qué se entregó, cuándo y con qué versión, y si hubo migración, su reporte. Del contenido del trabajo de la organización no entra nada.

---

# Nivel 2. El área

Solo si el área del dueño no está en `guia.md`.

Antes de crearla se dice en una línea: un área es una capa de propiedad nueva, con un dueño que responde por todo lo que hay dentro, y conviene que lo sepa el responsable de contexto. Si el usuario confirma, se sigue.

## Las cuatro preguntas

1. ¿De quién es el área? Por defecto, de quien abre la sesión
2. ¿Qué es el área, en dos o tres líneas?
3. ¿Qué tiene entre manos ahora? Tres a cinco prioridades
4. ¿La puede leer todo el equipo, o solo quien trabaja en ella?

## Qué escribo y dónde

**1. La carpeta**, con nombre en minúsculas y guiones, en la raíz. Sin número delante.

**2. `area.md`**, con la estructura fija de `convenciones`, sección 2:

```markdown
---
estado: vigente
actualizado: 2026-09-01
---

# Operaciones

## Qué es
[Lo que dijo el usuario, en dos o tres líneas]

## Prioridades ahora
[Tres a cinco líneas]

## Proyectos
[Vacío. Lo escriben esta skill al crear un proyecto y el cierre de sesión]

## Quién participa
Dueño: Marta Ruiz
```

Sin `## Panorama`: esa sección la crea la skill `director` al cerrar la primera sesión en el área, entre `Proyectos` y `Quién participa`.

**3. La fila del área en la tabla de `guia.md`**, con su dueño, su cuenta y quién la lee. La escribe la sesión del responsable de contexto; desde la de otra persona se prepara la fila y se le pasa, y el área existe igual mientras tanto.

Nada más: ni proyectos vacíos, ni plantillas, ni un `README`.

## Si el área es restringida

La carpeta y su `area.md` se crean igual, en su sitio de la raíz, y su fila en `guia.md` dice que está restringida. Lo que cambia es el permiso, y la skill no lo pone: se dice qué carpeta hay que limitar y con acceso para quién, y se avisa de que hasta que no se haga, lo que hay dentro lo lee todo el equipo. Ponerle el acceso limitado a una carpeta lo hace quien administra la carpeta compartida, desde la web de Drive.

Un área que ya existe no se convierte en restringida por las buenas: se dice qué carpeta habría que limitar y se espera confirmación, porque cambia quién ve qué y eso lo decide su dueño.

## Qué respondo al terminar

Dos líneas: qué se creó, dónde, y de quién es, más el recordatorio de que su dueño necesita permiso de escritura sobre la carpeta en Drive y, si el área es restringida, que alguien tiene que ponerle el acceso limitado. Eso no lo da la skill.

---

# Nivel 3. El proyecto

## Las cinco preguntas

1. ¿Qué problema resuelve y para quién?
2. ¿Cómo sabremos que está terminado?
3. ¿De quién es? Por defecto, de quien abre la sesión
4. ¿Quién más va a usar lo que salga de aquí?
5. ¿Qué material ya existe? Documentos, exports, correos, grabaciones, enlaces

Un proyecto a medio encuadrar es mejor que una conversación sin carpeta.

## Qué escribo y dónde

**1. La carpeta**, con nombre en minúsculas y guiones, sin número de fase ni de etapa, dentro del área del dueño. Si el proyecto entero no lo puede leer todo el equipo y su área sí, se dice que hay que limitar el acceso a esta carpeta y quién tiene que hacerlo, y su línea en el bloque `Proyectos` del área empieza por «restringido». Si solo una parte no lo puede leer, el proyecto se crea normal y esa parte va a `restringido/`.

**2. `proyecto.md`**, con la estructura fija de `convenciones`, sección 3. Se rellena con las respuestas: `Quién participa` lleva al dueño, `En corto` lleva la fecha de hoy, su frase («Arrancamos <proyecto>; lo primero es …») y la línea «Siguiente», sin «Se completó»; `Estado actual` queda como "arrancando" y `Siguientes pasos` recoge lo que salga de la conversación de arranque. Las secciones sin respuesta se dejan con el hueco marcado, nunca se borran ni se rellenan con supuestos.

**3. `decisiones.md`**, con cabecera y solo el título. Vacío de entradas: las que haya se registran al cerrar la primera sesión.

**4. `sesiones.md`**, con la entrada de arranque:

```markdown
## 2026-08-29
Trabajamos en: arranque del proyecto.
Avances: encuadre definido con Ana Pérez.
Pendiente: reunir los exports del ERP.
```

**5. Las tres carpetas** `entregables/`, `taller/` y `fuentes/`, vacías.

**6. El material existente** se mueve a `fuentes/` con nombres legibles, si el usuario lo tiene a mano. Si no, queda como siguiente paso. Los enlaces van a `fuentes/enlaces.md`, una fila por enlace; ese archivo solo se crea si hay filas. Antes de guardar cada archivo se mira si trae indicios de información confidencial (la lista está en `convenciones`, sección 1, «Material sensible»); si los trae, se dice y se propone llevarlo a `restringido/` con su fila en el `enlaces.md` público. El usuario decide.

**7. La línea del proyecto en el bloque `Proyectos` de `area.md`**: `` `nombre-del-proyecto/` — qué es ``, sin entregables debajo porque todavía no hay ninguno vigente. Es lo único que se toca de `area.md`.

## Qué respondo al terminar

El nombre de la carpeta creada y el primer siguiente paso. Dos líneas.

---

## Lo que nunca hago

Además de las prohibiciones de `convenciones`:

- Crear un área sin decir antes que es una decisión organizativa
- Montar la raíz encima de una carpeta con documentos sin avisar de que después toca `migrar`
- Editar `metodo.md` al copiarlo, o montar la raíz en una carpeta donde una aplicación escribe sola
- Rellenar `contexto.md` con lo que parece razonable para una organización de ese tipo
- Crear entregables vacíos "para ir rellenando", o `fuentes/enlaces.md` sin filas
- Inventar alcance, plazos o participantes que nadie mencionó
- Crear un proyecto en un área que no es la del dueño
- Crear un área restringida sin su fila en `guia.md`, o dar por restringida una carpeta cuyo acceso limitado nadie ha puesto todavía
- Proponer para una carpeta compartida un nombre con signos fuera de letras, números, espacios y guiones
- Proponer restringir un área existente sin que su dueño lo haya confirmado
- Tocar de `area.md` o de `guia.md` algo que no sea la línea o la fila nueva
- Duplicar un proyecto o un área existente sin avisar antes

---

## Ejemplo completo

**Usuario:** vamos a arrancar un proyecto para automatizar las órdenes de compra

**Respuesta:**

> En `guia.md` está Compras con Ana Pérez como dueña, y en su bloque `Proyectos` hay dos que no se parecen, así que solo falta el proyecto. Cuatro preguntas y lo creo, contigo como dueño salvo que me digas otra cosa:
>
> 1. ¿Qué problema resuelve y para quién?
> 2. ¿Cómo sabremos que está terminado?
> 3. ¿Quién más va a usar lo que salga?
> 4. ¿Qué material ya existe?

**Usuario:** las aprobaciones manuales tardan días y frenan a operaciones. Terminado cuando las órdenes bajo cierto monto se aprueben solas en el ERP. La dueña es Ana Pérez. Lo usarán Finanzas y Sistemas. Tengo un export de órdenes del último año, la grabación de la reunión con Ana, el enlace a la documentación del ERP y un Excel con los sueldos del equipo para calcular el tope.

**Respuesta:**

> Creado `compras/automatizacion-ordenes/` con el paquete completo, con Ana Pérez como dueña, y su línea en `compras/area.md`. El enlace del ERP ya está en `fuentes/enlaces.md`.
>
> El Excel de sueldos trae nombres con salario, así que no lo guardo en `fuentes/`. Si lo confirmas, va a `restringido/` de este proyecto y dejo su fila en `enlaces.md` con la nota de que a los entregables solo sale el total agregado. ¿Lo tratamos como confidencial?

**Usuario:** sí

**Respuesta:**

> Hecho. Queda por meter el export y la grabación en `fuentes/`; pásamelos cuando puedas y los coloco con nombres legibles.

---

**Usuario:** vamos a abrir un área para la cuenta de un cliente nuevo, pero eso no lo puede ver todo el mundo

**Respuesta:**

> Un área es una capa de propiedad nueva: alguien responde por todo lo que hay dentro, y conviene que lo sepa el responsable de contexto. Cuatro preguntas y la creo, contigo como dueño salvo que me digas otra cosa:
>
> 1. ¿Qué es el área, en dos o tres líneas?
> 2. ¿Qué tiene entre manos ahora?
> 3. Me dices que no la puede leer todo el equipo, así que la carpeta se crea aquí y hay que ponerle el acceso limitado. ¿Quién entra?

**Usuario:** la dueña es Marta Ruiz. Es la cuenta del cliente: campañas, automatizaciones y lo que nos pidan. Ahora mismo la revisión de automatizaciones. Entra la gente que ya trabaja en ella

**Respuesta:**

> Creada la carpeta del área con su `area.md`, con Marta Ruiz como dueña, y su fila en `guia.md`: nombre, dueña, cuenta y que está restringida, para que el equipo sepa que existe y a quién pedir acceso. Falta lo único que no puedo hacer yo: que quien administra la carpeta compartida le ponga el acceso limitado desde la web de Drive, con Marta y quien decidas. Hasta entonces la lee todo el equipo.
>
> Y una cosa más que no hace la skill: darle a Marta escritura sobre esa carpeta en Drive.

---

**Usuario:** monta la carpeta para Acme, que empezamos con ellos el lunes

**Respuesta:**

> La carpeta conectada no tiene `guia.md`, así que monto la raíz desde cero. Cinco preguntas:
>
> 1. ¿El nombre es Acme, o tiene otro nombre completo?
> 2. ¿Quién mantiene el contexto común? Por defecto, tú
> 3. ¿Quién administra la carpeta compartida? Tiene que ser el dueño de la organización o alguien de su total confianza: puede quitar cualquier restricción
> 4. ¿Qué sistemas usan a diario?
> 5. ¿Hay una primera área con la que empezar, y de quién es?

**Usuario:** Acme Distribución. El contexto lo lleva Jorge Salas y la carpeta la administra él también. Usan SAP para compras y finanzas, HubSpot en comercial y Google Workspace. Empezamos por Compras, con Ana Pérez.

**Respuesta:**

> Montada la raíz de Acme Distribución: `guia.md` con la tabla de áreas y la receta para conectarse, `metodo.md` copiado del plugin, `base/` con contexto, glosario y sistemas (tres filas, con "quién da acceso" como hueco), y `compras/` con Ana Pérez como dueña, que la lee todo el equipo.
>
> Me faltan las cuentas de Jorge y de Ana para la tabla de `guia.md`: son las que permiten comprobar después que quien pide publicar algo es su dueño.
>
> Dos siguientes pasos. Permisos en Drive: lectura de la raíz para todo el equipo, escritura en `base/` para Jorge y en `compras/` para Ana. Y una sesión con Jorge para rellenar `contexto.md`, que ahora mismo son cuatro huecos.
