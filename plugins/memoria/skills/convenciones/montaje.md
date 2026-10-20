# Montaje, publicación y otros modelos

Anexo del contrato (`convenciones`, secciones 11 y 13). Lo leen `nuevo` al montar una raíz, `tablero`, y quien pregunte cómo se monta o se publica el método. El bloque de instrucciones de abajo es el que inyecta el aviso de arranque del plugin en cada sesión.

## Actualización del método

El método se actualiza publicando una versión nueva del plugin. La primera línea legible de `metodo.md` lleva la versión y una huella de su contenido, que escribe `build-metodo.sh`: cualquier cambio de texto la cambia aunque el número no cambie. Al abrir sesión se compara esa línea en la raíz con la del `metodo.md` del plugin. La raíz está atrasada si la versión del plugin es mayor, o si es la misma y la raíz no lleva huella; con la misma versión y huellas distintas no se toca nada (solo pasa entre dos publicaciones). Si está atrasada, la sesión que abre (skill `sesion`) o la puesta al día de cualquier tablero (paso 0 de `tarea.md`) copia el `metodo.md` del plugin sobre el de la raíz, sin preguntar y sin tocar nada más, y lo dice en una línea. Lo hace cualquier cuenta, no solo el responsable de contexto, porque es una copia exacta del plugin y no contenido de la organización: una versión nueva llega a la carpeta con la primera persona que abre sesión o sincroniza un tablero con el plugin actualizado. Nunca hacia atrás. Si la cuenta no tiene permiso para escribir en el primer nivel de la carpeta, la escritura se rechaza, no se intenta por otra vía, no se dice nada y lo hará la siguiente cuenta que pueda. Si el atrasado es el plugin de quien abre, se le dice que lo actualice. Nadie tiene que acordarse de copiarlo. Nadie edita `metodo.md` dentro de la carpeta de una organización.

Tres scripts acompañan al plugin y nadie tiene que recordar sus pasos. `release.sh` publica una versión: comprueba antes de tocar nada que la versión sea mayor que la actual, que el contrato declare la mayor.menor y que el README tenga su entrada; sube el número donde vive, regenera `metodo.md` y dice qué queda por hacer a mano. Si algo falla a mitad, deja los archivos como estaban. `verificar.sh` se pasa sobre la raíz de una organización: comprueba la estructura, los nombres, las cabeceras, los estados y que el bloque `Proyectos` de cada área liste todo lo que tiene que listar. No escribe nada: de cada `.md` lee la cabecera y busca enlaces wiki y rutas absolutas, no entra en `fuentes/` ni en `restringido/`, y una carpeta que no se deja leer la salta.

## La carpeta en Google Drive

Es trabajo de quien administra la carpeta, una vez por organización, antes de que nadie se conecte. Vale lo mismo para otra nube con unidades de equipo; el ejemplo es Drive.

**Mejor una unidad compartida de la organización.** Sus archivos son de la organización y no de una persona: si alguien se va, nada se pierde ni cambia de dueño, y los permisos se dan por miembro. Las unidades compartidas son de Google Workspace; con una cuenta personal de Gmail no las hay, y entonces la raíz es una carpeta normal en «Mi unidad» de quien administra, compartida con el equipo. En ese caso los archivos son de esa persona: si deja la organización, hay que pasarlos antes a otra cuenta.

**La raíz** es la unidad entera o una carpeta de su primer nivel, con `guia.md` y `metodo.md` dentro, y un nombre que se pueda teclear (contrato, sección 6). Cada organización, una sola.

**Los permisos**, como dice la sección 1 del contrato:

- Todo el equipo, lectura en toda la unidad o la carpeta raíz.
- Cada dueño de área y quien colabora en ella, edición en la carpeta de esa área; quien colabora en un solo proyecto, solo en la carpeta de ese proyecto.
- El responsable de contexto, edición en `guia.md` y `base/`.
- Quien administra, administrador de la unidad, y nadie más.
- Lo restringido se marca en su carpeta con el acceso limitado de Drive, desde la web. En una unidad compartida lo pone quien la administra; Google lo admite en unidades compartidas desde 2025.

**En la computadora de cada persona**, Drive para escritorio solo transmite las unidades compartidas: no las copia enteras al disco como puede hacer con «Mi unidad». Por eso la carpeta se marca «Disponible sin conexión» en cada computadora, y se comprueba que sus archivos bajaron antes de conectar la carpeta a Claude. En Windows la unidad aparece como una letra de disco aparte (por ejemplo, G:); si Claude no consigue conectarla en una computadora, se dice en la guía de esa raíz y se decide con quien administra cómo seguir.

## Montaje en Claude

El uso principal del método es Claude con la raíz conectada y el plugin instalado. El montaje tiene dos reglas.

**Un proyecto de Claude por persona**, nombrado por su área, o por la organización si esa persona lleva todas las áreas. Dónde escribe no lo decide el nombre del proyecto sino su cuenta en `guia.md`, así que un solo proyecto sirve para todas las áreas de quien las lleva todas.

**Se conecta la raíz completa, nunca la carpeta de un área.** `guia.md`, `metodo.md` y `base/` viven en la raíz; la lectura cruza áreas; `consulta` busca en lo que produjo cualquier área y `sesion` avisa de las decisiones de otras que afectan al proyecto. Conectada solo un área, el método se rompe en la primera llamada. Conectar de más no abre ningún riesgo: quién puede leer y escribir dónde lo fijan los permisos de las carpetas, no el alcance de la conexión, y lo restringido sigue restringido dentro de una carpeta conectada.

Al proyecto se le vincula la raíz, y para trabajar en un área no hace falta ninguna carpeta más. Si se vinculan varias raíces, vale lo de «Independencia entre raíces» (sección 1).

**El tablero es opcional y personal.** Cualquiera lo monta desde su propia cuenta escribiendo «monta el tablero» con la raíz conectada; la skill `tablero` publica la página, que se pone al día sola cuando esa persona la abre después de cerrar sesiones, desde su computadora y con sus permisos (lo que escriben otras personas se trae con su botón; una tarea que la regenere cada mañana solo se crea si se pide): lo que su cuenta no lee en la carpeta sale como restringido, y lo que su tarea escribe lo escribe con sus permisos. Tiene dos modos: público, la superficie pública del contrato con lo restringido declarado fuera y de las sesiones solo su cabecera (fecha, título y «Trabajamos en»), que se puede compartir con cualquiera de la organización desde el menú del artifact; y completo, con todo lo que la cuenta lee y las sesiones recientes enteras, que es para su dueño y no se comparte. Se encuentra por su nombre entre los artifacts de la cuenta; en la raíz no queda nada de él. Lo que se toca en el tablero espera en su cola hasta que la siguiente puesta al día lo escribe en la carpeta, o hasta la siguiente sesión del proyecto si pide juicio; la página nunca escribe en la raíz. Cuando sale una versión nueva del plugin, la siguiente puesta al día republica la página sobre la misma URL sin que nadie lo pida.

**Nadie pega instrucciones en el proyecto.** El plugin trae un hook de arranque que, al empezar cada sesión, inyecta el bloque de abajo como contexto, y con él cómo saber dónde escribe cada quien: la cuenta que abre la sesión se busca en la columna Cuenta de la tabla de áreas de `guia.md`, como dueño o tras «colabora:», y en la línea `Colabora:` de cada proyecto, y esas áreas y proyectos son los suyos. Así el método se aplica en cuanto la carpeta está conectada, se actualiza solo con cada versión del plugin y no depende de que nadie copie bien un texto. El bloque sigue aquí para quien trabaje con otro modelo sin el plugin, o en una superficie donde el arranque del plugin no corra: en ese caso se pega tal cual y se añade debajo una línea propia diciendo dónde se escribe. El texto no nombra skills, porque Claude las elige solo:

```
Este proyecto trabaja sobre una memoria de trabajo permanente: la carpeta conectada, que sigue el método del plugin `memoria`. Aplícalo en todo lo que hagas aquí, y no guardes nada en tu memoria: si un dato importa, va a un archivo de la carpeta.
Lee `guia.md` al empezar y no leas nada más hasta saber qué necesitas: la carpeta se lee por niveles y `guia.md` dice dónde está cada cosa.
Lee y escribe la carpeta por su copia en esta computadora, nunca por el conector de Google Drive aunque esté conectado; si no la ves, pídeme que la añada. Sin ninguna carpeta conectada (desde el teléfono o la web), la raíz se puede leer por el conector de Drive, sin escribir nada en ella.
Escribe solo donde tu cuenta es dueña o colabora, según `guia.md` y la línea «Colabora:» de cada proyecto, o donde te diga que trabajo si la cuenta no aparece, y en ningún otro sitio de la carpeta; si no está claro, pregúntamelo antes de escribir nada. Si algo le toca a otra área, dímelo y yo se lo pido a su dueño.
No des por aprobado ningún documento ni edites lo ya registrado en decisiones o sesiones.
Si una carpeta no se deja leer, está restringida: dímelo y sigue con lo que sí puedas leer, sin suponer lo que hay dentro.
Lo que hagas para un proyecto, un documento, un PDF o un análisis, guárdalo en su carpeta en cuanto exista, como borrador, y no en «Claude outputs»; cerrar sesión es registrar lo que pasó, no guardar.
Antes de guardar algo, pregúntate si alguien más lo va a leer y si contiene datos que no todos deben ver. Si algo parece confidencial, avísame y propón moverlo; no lo muevas tú.
```

El bloque es idéntico en cualquier organización: no nombra a ninguna, no lleva huecos que rellenar y nada de una raíz concreta entra en él. Lo propio de una raíz vive en `guia.md`, que la segunda línea manda leer. Dónde escribe cada quien sale de `guia.md` y de la cuenta de la sesión; si ninguna área coincide con la cuenta, la IA pregunta antes de escribir en vez de suponer.

La skill `nuevo` escribe todo esto en `guia.md` como una receta corta: crear el proyecto con el nombre del área, instalar el plugin desde el marketplace, conectar la raíz, comprobar con «abre sesión en...» y, si se quiere, montar el tablero, para que cada persona lo monte sola sin preguntarle a nadie.

**Otros modelos.** Gemini u otro modelo sin plugin leen `metodo.md`. Contiene el contrato con sus dos anexos, el estilo y el índice de skills, así que saben qué reglas seguir aunque no puedan ejecutarlas como skills.

**Programadores.** El `CLAUDE.md` de un repositorio enlaza la carpeta del proyecto en la raíz (`area/proyecto`). Las decisiones de código que dependen de un diseño se anclan en `decisiones.md` y en los entregables vigentes de ese proyecto, no en comentarios del código. Para saber qué se decidió antes de escribir código, usan la skill `consulta`.
