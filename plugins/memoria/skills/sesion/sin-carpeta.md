# Sin carpeta: solo lectura

Anexo de la skill `sesion` (y de `consulta` y `director`). Se lee cuando la conversación no tiene ninguna carpeta conectada con `guia.md` y `metodo.md` después de buscarla, y piden algo del método.

Cuando la sesión no tiene ninguna carpeta conectada (desde el teléfono, desde la web) y tiene el conector de Google Drive, se puede abrir sesión, consultar y preguntar al director leyendo la raíz en Drive. No se escribe nada en ella.

**Sin el conector, o sin la raíz en Drive**, no se sigue con el método y la respuesta empieza así:
- Sin el conector de Google Drive: «Memoria no conectada: esta conversación no tiene la carpeta de la organización, y desde aquí no tengo cómo buscarla en Google Drive. Abre Claude en la computadora donde está la carpeta, o añádela con «+».»
- Con el conector, si la raíz no está en Drive: «Memoria no conectada: esta conversación no tiene la carpeta de la organización, y no la encuentro en Google Drive (puede estar en iCloud, en otra nube o en otra cuenta). Abre Claude en la computadora donde está la carpeta, o añádela con «+».»

**Encontrar la raíz.** Con el conector, se buscan archivos llamados `guia.md` (`title = 'guia.md'`) y se queda la carpeta que además tiene `metodo.md` en su primer nivel. Si hay más de una, se pregunta cuál, como con varias raíces conectadas. Si no hay ninguna, se dice que la raíz no está en Drive o que esta cuenta no la ve, y que la memoria se trabaja desde la computadora con la carpeta conectada.

**Leer por niveles.** Los mismos niveles de la sección 12 de `convenciones`. Listar una carpeta con `parentId` devuelve cada archivo con un fragmento de su texto, que basta para las cabeceras y las fechas; un archivo entero se lee con `read_file_content`, que devuelve el Markdown con las marcas escapadas (`\#`, `\---`): se leen como si no lo estuvieran. La búsqueda de avisos se hace con `fullText contains 'Afecta a: <area>/<proyecto>'` y con `Cuestiona a:`, en lugar de recorrer los archivos.

**Qué se dice.** La primera respuesta empieza con «Memoria en solo lectura · <organización> · método <versión> · desde aquí no se registra nada», en lugar de «Memoria activa». Después, lo mismo que al abrir con la carpeta.

**Qué pasa con lo que sale de la sesión.** Nada se escribe en la raíz: ni decisiones, ni bitácora, ni pasos, ni el Panorama. Lo que haya que registrar se guarda, con el sí de la persona, como nota en la cola del tablero de su cuenta: un documento nuevo en la colección `cambios` con la forma exacta de las notas que escribe la página, `{tipo: "nota", proyecto: "<area>--<slug>", nota: "<texto>", creado: "<fecha y hora ISO>", estado: "pendiente"}`; si lo que sale es del área y no de un proyecto (un panorama, una prioridad), va con `area: "<slug del área>"` en lugar de `proyecto`, y lo enseña la siguiente sesión que su dueño abra en cualquier proyecto del área. La siguiente sesión con la carpeta lo enseña al abrir, como cualquier nota del tablero. Si la persona no tiene tablero, se le da el texto para que lo pegue al abrir la próxima sesión desde la computadora. Una decisión no se da por registrada hasta entonces.
