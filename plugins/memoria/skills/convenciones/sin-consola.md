# Sin consola

Anexo del contrato (`convenciones`, sección 1). Dice cómo se lee y se escribe la raíz cuando está conectada pero el shell de la computadora no la ve. Le pasa a una unidad de Google Drive para escritorio en Windows, con letra (G:) o colgada de una carpeta: la app no la monta en su shell aunque la carpeta esté conectada y con acceso. Las herramientas que listan, traen y escriben archivos sí llegan a ella, y con ellas se trabaja igual que con consola: abrir y cerrar sesión, guardar, crear áreas y proyectos, mover material, el tablero. Es más lento y cuesta más tokens, nada más. Lo lee cualquier skill en cuanto sabe que no hay consola, antes de leer o escribir en la carpeta.

## Cómo se sabe

Una vez por conversación, la primera vez que hace falta la carpeta: `device_bash` con `ls "$HOME/mnt/"`, buscando la carpeta de la raíz (la que tiene `guia.md` y `metodo.md`; con la consola, su nombre es el último tramo de su ruta en la computadora, a veces con el de la carpeta de encima delante). Si está, hay consola y nada de este anexo aplica. Si no está y la herramienta dice que no se pudo montar («failed to mount»), o si la conversación no tiene `device_bash` pero sí `device_stage_files`, no hay consola.

- No se vuelve a pedir acceso a la carpeta: ya lo tiene. No se le pide a la persona que cambie nada de Drive, que vuelva a añadir la carpeta ni que haga nada a mano.
- Se dice una sola vez, en una línea: «Tu computadora no deja abrir la carpeta desde la consola de Claude (pasa con Google Drive en Windows); trabajo igual, algo más lento.» Y se sigue.
- No se guarda en ningún sitio: cada conversación lo vuelve a comprobar, así que el día que la consola monte la carpeta se vuelve al camino de siempre sin que nadie haga nada.

## La copia

Se trabaja sobre una copia de lo que hace falta, en el contenedor de la conversación:

- **La ruta de la raíz en la computadora** es la que da `get_device_info` (`connectedFolders`). Todas las llamadas usan esa ruta más la ruta relativa del archivo.
- **Traer**: `device_stage_files`, hasta 50 archivos por llamada. Si un archivo de la lista no existe, la herramienta rechaza la llamada entera: se repite sin él. Los deja en `/mnt/user-data/uploads/<carpeta>/<ruta relativa>`; esa carpeta, «la copia», es la parte del primer `stagedPath` que va antes de la ruta relativa. Se lee con las herramientas de archivos del contenedor. Lo que no llega (no existe, o la cuenta no lo lee) se trata como con consola: lo que no se deja leer está restringido y no se supone lo que hay dentro.
- **Listar**: `device_list_dir` sobre la carpeta que haga falta, recursivo solo si hace falta (llega a cinco niveles y 2,000 entradas; más hondo, se lista la subcarpeta). Las fechas de verdad de los archivos están en su `mtimeMs`: las de la copia son las de cuándo se trajo.
- **`espejo.py`**, en la raíz del plugin (`../..` desde el directorio de cualquier skill), lleva la copia: qué traer para abrir (`rutas`), cómo estaba (`instantanea`) y qué devolver (`devolver`). Su cabecera dice cómo se usa.
- **Los scripts del plugin** (`abrir.py`, `generar_vista.py`, `aplicar_cambios.py`) corren en el contenedor, desde el plugin instalado, sobre la copia. No se descarga nada. `abrir.py` y `generar_vista.py` llevan `--sin-fechas`, porque las fechas de la copia no dicen nada.

## Escribir

1. **Antes de escribir encima de un archivo**, se trae otra vez si se trajo hace más de unos minutos o si esta sesión ya lo devolvió: vale lo de siempre, nunca se escribe encima de lo que no se ha leído. El `mtimeMs` que da `device_stage_files` es el que se usa para devolverlo.
2. **Se escribe en la copia**, con las herramientas de archivos del contenedor, con todas las reglas de `escribir.md`. Un archivo nuevo se crea en su sitio de la copia, con sus carpetas.
3. **Se devuelve**: con Bash, `python3 <raíz del plugin>/espejo.py devolver "<la copia>" "<ruta de la raíz en la computadora>"`, que imprime cada archivo cambiado o nuevo con su `stagedPath` y su `devicePath`. Se pasan tal cual a `device_commit_files`, con `expectedMtimeMs` (el de la última vez que se trajo) en los que no son nuevos. `device_commit_files` crea las carpetas que falten. Después, `espejo.py instantanea "<la copia>"`.
4. **Si rechaza un archivo por su fecha**, alguien escribió en él mientras tanto: se trae otra vez, lo de esta sesión se suma a lo que hay (como dice el cierre de sesión con dos personas) y se devuelve, una vez. Si vuelve a pasar, se dice y se para. Nunca se fuerza.

Una carpeta vacía no se puede devolver: aparece con su primer archivo. Si la estructura la pide vacía (las tres carpetas de un proyecto nuevo), se crea con el conector, como abajo.

## Mover, renombrar y mandar a la papelera

Las herramientas de la computadora no mueven ni borran. Sin consola, esto se hace con el conector de Google Drive, y es la única vez que una sesión con la carpeta conectada lo usa: nunca para leer ni para escribir contenido.

- **La raíz en Drive**: `search_files` con `title = 'guia.md'` y `excludeContentSnippets`; es la carpeta padre (`parentId`) del que tiene el mismo tamaño que el `guia.md` de la carpeta y un `metodo.md` al lado (`parentId = '<id>' and title = 'metodo.md'`). Si hay dudas entre dos, se pregunta. Su id vale para toda la conversación.
- **Cada archivo o carpeta**, tramo a tramo desde la raíz: `parentId = '<id del tramo anterior>' and title = '<tramo>'`.
- **Mover o renombrar**: `update_file` con `parentId` (la carpeta de destino) y, si cambia el nombre, `title`. El archivo es el mismo: conserva su historial y sus permisos. Una carpeta de destino que no existe se crea antes con `create_file` y el tipo de carpeta.
- **Mandar a la papelera**, solo donde el método deja borrar y con el sí de la persona: `trash_file`. Queda en la papelera de Drive.
- **Después**, el cambio tarda un poco en llegar a la computadora: se comprueba con `device_list_dir` de las carpetas tocadas, reintentando unas veces, y hasta que llega no se escribe en ellas. Al revés, un archivo que esta sesión acaba de devolver puede no estar aún en Drive: si `search_files` no lo encuentra, se espera y se reintenta, nunca se crea otro. Si con la escritura basta (un archivo que esta sesión crea), se escribe directamente en su sitio y no se mueve nada.
- **Sin el conector de Google Drive** no se puede mover. Se dice en una línea que hace falta conectarlo y se ofrece hacerlo (`SuggestConnectors`, que lo deja a un clic); mientras, se sigue con lo demás. Nunca se le pide a la persona que mueva archivos a mano.

## La marca en la bitácora

Cada entrada nueva de `sesiones.md` que escribe una sesión sin consola termina su última línea con « · sin consola»: `Sesión de: Nombre Apellido · plugin 1.17.0 · sin consola`. Es la manera de saber qué raíces trabajan así y, cuando dejen de aparecer, que la consola ya monta su carpeta.
