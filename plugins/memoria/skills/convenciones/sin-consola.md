# Sin consola

Anexo del contrato (`convenciones`, sección 1). Dice cómo se lee y se escribe la raíz cuando está conectada pero el shell de la computadora no la ve. Le pasa a una unidad de Google Drive para escritorio en Windows, con letra (G:) o colgada de una carpeta: la app no la monta en su shell aunque la carpeta esté conectada y con acceso. Las herramientas que listan, traen y escriben archivos sí llegan a ella, y con ellas se trabaja igual que con consola: abrir y cerrar sesión, guardar, crear áreas y proyectos, mover material, el tablero. Es más lento y cuesta más tokens, nada más. Lo lee cualquier skill en cuanto sabe que no hay consola, antes de leer o escribir en la carpeta.

## Cómo se sabe

Una vez por conversación, la primera vez que hace falta la carpeta, con las herramientas de la computadora ya cargadas (`ToolSearch`, si están diferidas): `device_bash` con `ls "$HOME/mnt/"`, buscando la carpeta de la raíz (la que tiene `guia.md` y `metodo.md`; su nombre es el último tramo de su ruta en la computadora, a veces con el de la carpeta de encima delante). Si está, hay consola y nada de este anexo aplica. No hay consola si no está aunque `get_device_info` la da como conectada (la herramienta suele añadir que no se pudo montar), o si después de buscarla la conversación no tiene `device_bash` pero sí `device_stage_files`.

- No se vuelve a pedir acceso a la carpeta: ya lo tiene. No se le pide a la persona que cambie nada de Drive, que vuelva a añadir la carpeta ni que haga nada a mano.
- Se dice una sola vez, en una línea: «Tu computadora no deja abrir la carpeta desde la consola de Claude (pasa con Google Drive en Windows); trabajo igual, algo más lento.» Y se sigue.
- No se guarda en ningún sitio: cada conversación lo vuelve a comprobar, así que el día que la consola monte la carpeta se vuelve al camino de siempre sin que nadie haga nada.

## La copia

Se trabaja sobre una copia de lo que hace falta, en el contenedor de la conversación:

- **La ruta de la raíz en la computadora** es la que da `get_device_info` (`connectedFolders`). Todas las llamadas usan esa ruta más la ruta relativa del archivo.
- **Traer**: `device_stage_files`, hasta 50 archivos por llamada. Si un archivo de la lista no existe, la herramienta rechaza la llamada entera: se repite sin él. Los deja en `/mnt/user-data/uploads/<carpeta>/<ruta relativa>`; esa carpeta, «la copia», es la parte del primer `stagedPath` que va antes de la ruta relativa. Se lee con las herramientas de archivos del contenedor. Lo que no llega se trata como con consola, donde lo que la cuenta no puede leer tampoco baja a la computadora: no se supone lo que hay dentro. La copia se llama como la carpeta en la conversación, que no siempre es el nombre de la raíz: hasta tener el primer `stagedPath`, no se da por sabido.
- **Listar**: `device_list_dir` sobre la carpeta que haga falta, recursivo solo si hace falta (llega a cinco niveles y 2,000 entradas; más hondo, se lista la subcarpeta). Las fechas de verdad de los archivos están en su `mtimeMs`: las de la copia son las de cuándo se trajo.
- **`espejo.py`**, en la raíz del plugin (`../..` desde el directorio de cualquier skill), lleva la copia y su estado: qué traer para abrir (`rutas`, y `falta` para lo que no existe), qué se va a escribir (`registrar`, `nuevo`), qué devolver (`devolver`) y qué quedó escrito (`hecho`). Su cabecera dice cómo se usa. En cuanto la copia está completa, `espejo.py instantanea "<la copia>"`: así avisa de lo que cambie sin registrar.
- **Los scripts del plugin** (`abrir.py`, `generar_vista.py`, `aplicar_cambios.py`) corren en el contenedor, desde el plugin instalado, sobre la copia. No se descarga nada. `abrir.py` y `generar_vista.py` llevan `--sin-fechas`, porque las fechas de la copia no dicen nada.
- **Las salidas.** Lo que se devuelve pasa por una carpeta de salidas (`/mnt/project-files/` en una conversación de proyecto); `espejo.py hecho` la vacía en cuanto no queda nada pendiente, y no se deja ahí nada de `restringido/`.

## Escribir

Solo se devuelve lo que se registró al traerlo o se declaró nuevo: un archivo de la copia puede estar viejo, a medias o vacío, y escribirlo encima borraría el de verdad.

1. **Antes de escribir en un archivo que existe**, se trae (otra vez, si se trajo hace más de unos minutos o si esta sesión ya lo devolvió: nunca se escribe encima de lo que no se ha leído) y se registra con lo que dio `device_stage_files`: `espejo.py registrar "<la copia>" <ruta> <mtimeMs> <bytes>`. Si sale con 3, el archivo aún no llegó entero: se espera unos segundos y se repite.
2. **Un archivo nuevo**: antes, `device_list_dir` de su carpeta confirma que no existe (si existe, es el caso 1), y se declara con `espejo.py nuevo "<la copia>" <ruta>`.
3. **Se escribe en la copia**, con las herramientas de archivos del contenedor, con todas las reglas de `escribir.md`.
4. **Se devuelve**: `espejo.py devolver "<la copia>" "<ruta de la raíz en la computadora>"` imprime los lotes, cada entrada con su `stagedPath`, su `devicePath` y, si no es nueva, su `expectedMtimeMs`. Cada lote va tal cual a una llamada de `device_commit_files`, que crea las carpetas que falten. Después, `espejo.py hecho "<la copia>"` con las rutas relativas de lo que la herramienta escribió (`written`). Lo que sale en `retenidos` (un `.md` vacío, que perdió su cabecera o que encoge a menos de la mitad) no se devuelve: se revisa, y solo si el cambio es a propósito se repite con `--forzar <ruta>`. Lo que sale en `sin_registrar` cambió en la copia sin registrar: se registra o se declara, como en 1 o 2, y se devuelve otra vez.
5. **Si rechaza un archivo por su fecha**, alguien escribió en él mientras tanto. Lo de esta sesión está en el `stagedPath` que dio `devolver`: se trae el archivo otra vez, se registra, se suma lo de esta sesión a lo que hay (en un cierre, repitiendo `cerrar.py` sobre la copia con el mismo `cambios.json`: una entrada que ya está no se repite y los reemplazos van sobre lo nuevo) y se devuelve, una vez. Si vuelve a pasar, se dice y se para. Nunca se fuerza.

Una carpeta vacía no se puede devolver: aparece con su primer archivo. Si la estructura la pide vacía (las tres carpetas de un proyecto nuevo), se crea con el conector, como abajo.

## Mover, renombrar y mandar a la papelera

Las herramientas de la computadora no mueven, no borran y no crean carpetas vacías. Sin consola, esto se hace con el conector de Google Drive, y es, con los permisos (`permisos.md` de `sesion`), lo único para lo que una sesión con la carpeta conectada lo usa: para localizar archivos y carpetas, crear carpetas, mover, renombrar y mandar a la papelera; nunca para leer ni para escribir contenido. Antes de mover algo que esta sesión cambió, se devuelve; después de moverlo, se mueve igual en la copia.

- **La raíz en Drive**: `search_files` con `title = 'guia.md'` y `excludeContentSnippets`; es la carpeta padre (`parentId`) del que tiene el mismo tamaño que el `guia.md` de la carpeta y un `metodo.md` al lado (`parentId = '<id>' and title = 'metodo.md'`). Si hay dudas entre dos, se pregunta. Su id vale para toda la conversación.
- **Cada archivo o carpeta**, tramo a tramo desde la raíz: `parentId = '<id del tramo anterior>' and title = '<tramo>'`.
- **Mover o renombrar**: `update_file` con `parentId` (la carpeta de destino) y, si cambia el nombre, `title`. El archivo es el mismo: conserva su historial y sus permisos. Una carpeta de destino que no existe se crea antes con `create_file` y el tipo de carpeta.
- **Mandar a la papelera**, solo donde el método deja borrar y con el sí de la persona: `trash_file`. Queda en la papelera de Drive.
- **Después**, el cambio tarda un poco en llegar a la computadora: se comprueba con `device_list_dir` de las carpetas tocadas, reintentando unas veces, y hasta que llega no se escribe en ellas. Al revés, un archivo que esta sesión acaba de devolver puede no estar aún en Drive: si `search_files` no lo encuentra, se espera y se reintenta, nunca se crea otro. Si con la escritura basta (un archivo que esta sesión crea), se escribe directamente en su sitio y no se mueve nada.
- **Sin el conector de Google Drive** no se puede mover. Se dice en una línea que hace falta conectarlo y se ofrece hacerlo (`SuggestConnectors`, que lo deja a un clic); mientras, se sigue con lo demás. Nunca se le pide a la persona que mueva archivos a mano.

## Lo que el tablero no tiene sin consola

Sin fechas de archivo, el tablero de una persona sin consola no avisa del trabajo sin sesión (lo da la sesión al abrir el proyecto), no da fecha a un entregable que no la lleva en su cabecera (los que no son .md salen sin fecha) y no cuenta lo que hay en «Claude outputs». Lo demás es igual.

## La marca en la bitácora

Cada entrada nueva de `sesiones.md` que escribe una sesión sin consola termina su última línea con « · sin consola»: `Sesión de: Nombre Apellido · plugin 1.17.0 · sin consola`. Es la manera de saber qué raíces trabajan así y, cuando dejen de aparecer, que la consola ya monta su carpeta.
