# Revisar los permisos de la carpeta compartida

Anexo de la skill `sesion`. Compara los permisos reales de la carpeta en Drive con lo que declara la raíz: quién lee, quién escribe en cada área y en cada proyecto, y qué está restringido. Revisar solo lee. Lo que no cuadra se le dice a la persona que responde por el contexto común, con lo que hay que cambiar en Drive. Una parte la puede aplicar Claude con el conector de Google Drive, solo en la sesión de quien administra la carpeta y con su sí, cambio por cambio («Aplicar lo que el conector permite», abajo); el resto lo cambia quien administra desde la web (contrato, sección 1, «Permisos en la carpeta compartida»).

## Cuándo

- **Lo pide el responsable de contexto**: «revisa los permisos», «¿están bien los permisos de Drive?», «¿quién puede escribir dónde?».
- **Lo pide quien administra para aplicar los cambios**: «aplica los permisos» (abajo, «Aplicar lo que el conector permite»).
- **Al cerrar una sesión suya en la que cambió quién escribe o qué se restringe**: un área nueva, alguien añadido como dueño o colaborador en `guia.md` o en un proyecto, un área o un proyecto declarado restringido, una carpeta `restringido/` nueva. Se propone en una línea al final del cierre («¿Reviso ahora que Drive coincide?») y se hace con su sí.
- **Al terminar de montar una raíz o sumar a alguien** (skill `nuevo`), cuando quien administra dice que ya dio los permisos.

Solo en la sesión del responsable de contexto (CUENTA de `abrir.py` dice «es la del responsable de contexto»), porque es quien responde por `guia.md` y la única a quien se avisa. A otra cuenta que lo pida se le dice que lo revisa esa persona, con su nombre. Solo cuando la raíz vive en Google Drive y está el conector de Google Drive; en otra nube, se dice que esta revisión es para Drive. En una sesión sin carpeta (`sin-carpeta.md`) no se hace.

## Cómo

1. **El plan, en la computadora.** `permisos.py` vive junto a este archivo y se trae como `abrir.py` (paso 1 de «Qué leo» en el `SKILL.md`, con `skills/sesion/permisos.py` en lugar de `skills/sesion/abrir.py`). Con device_bash: `python3 permisos.py "<raíz en $HOME/mnt>" --plan`. Dice qué carpetas mirar: la raíz, cada área, los proyectos con «Colabora:» o declarados restringidos y cada carpeta `restringido/`. Sin consola, corre en el contenedor sobre la copia de la apertura más los `proyecto.md` de las áreas (`espejo.py`), y las carpetas `restringido/` se buscan en Drive (paso 2).
2. **Los permisos, con el conector de Google Drive.** Es una de las excepciones del contrato: el conector se usa para leer permisos, no contenido.
   - La raíz: `search_files` con `title = 'guia.md' and fullText contains '<organización> · esta carpeta'`; su `parentId` es la raíz (en una unidad compartida, el id de la unidad, que empieza por `0A`). Si salen varias, la que coincide en fecha de modificación con el `guia.md` de la computadora.
   - Las áreas y los proyectos: `search_files` con `parentId = '<id>' and mimeType = 'application/vnd.google-apps.folder'`, con `excludeContentSnippets`, de la raíz y de cada área que lo necesite. De cada carpeta se toma su `id` y su `inheritedPermissionsDisabled`, que dice si tiene acceso limitado.
   - Las carpetas `restringido/`: `search_files` con `parentId = '<id del proyecto>' and title = 'restringido'`; sin consola, `title = 'restringido' and mimeType = 'application/vnd.google-apps.folder'` y se ubica cada una por su `parentId`.
   - Los permisos: `get_file_permissions` de la raíz y de cada carpeta del plan. Los de una carpeta traen también los heredados de la unidad.
   Una carpeta que no aparece con esta cuenta va como `null`: puede no existir o estar restringida para ella, y no se deduce más.
3. **La comparación.** Se escribe `drive.json` con la forma que dice la cabecera de `permisos.py` (en la computadora, con un heredoc en `$HOME/memoria/`, fuera de la raíz; sin consola, en el contenedor) y se corre `python3 permisos.py "<raíz>" --drive drive.json`.
4. **Qué se dice.** Lo que imprime, en llano y casi tal cual: primero «Para cambiar en Drive», una línea por persona o carpeta con el cambio exacto (el rol que tiene, el que debería tener y en qué carpeta), y después «Para comprobar». Si todo cuadra, una línea. Si quien administra no es el responsable de contexto, se dice que esos cambios los hace quien administra, con su nombre. No se guarda nada en la carpeta: la revisión vale para ese momento y se repite cuando haga falta. Si la cuenta tiene tablero, se guarda en su base para que Inicio lo muestre: con `ArtifactData`, un `set` del documento `meta/permisos` con `revisado` (la hora, ISO 8601) y lo que imprime `permisos.py … --tablero` (`cambios`, `comprobar`, `tipo_unidad`). Si lo que no cuadra es la declaración (alguien escribe a propósito y `guia.md` no lo dice), se propone corregir `guia.md` en esa misma sesión, con el sí de la persona.

## Aplicar lo que el conector permite

El conector de Google Drive deja hacer dos cosas, y nada más: **compartir** con alguien como «Lector» o «Colaborador» (o subirle el rol hasta ahí) y **marcar o quitar el acceso limitado** de una carpeta. No deja dar «Gestor de contenido» ni «Administrador», ni bajar un rol, ni quitar a nadie: eso queda a mano. La sección ACCIONES de `permisos.py` separa lo uno de lo otro.

- **Solo quien administra.** Se aplica en la sesión de quien administra la carpeta, según «Quién responde por qué» de `guia.md`, y si la cuenta no puede, Drive lo rechaza: se dice en una línea y se da como instrucción.
- **Con su sí, viendo cada cambio.** Antes de tocar nada se enseña la lista: a quién se comparte qué y con qué rol, y qué carpeta se limita. Nada se aplica sin un sí explícito a esa lista.
- **Compartir** (`share_file`): en la raíz, como «Lector», a quien figura en `guia.md` o en un «Colabora:» y no tiene acceso.
- **Limitar** (`update_file` con `inheritedPermissionsDisabled` en `true`): primero se comparte la carpeta con quien la tiene que seguir leyendo («conservan»: el dueño del área y quienes colaboran) y se comprueba con `get_file_permissions` que están; solo entonces se limita. Quien escribe ahí queda como «Colaborador» si el conector no da más: se dice que quien administra le suba el rol a «Gestor de contenido» desde la web. Nunca se limita una carpeta sin haber comprobado quién conserva el acceso, porque quien no esté pierde la entrada.
- **Después**, se vuelve a correr la comparación y se dice qué quedó resuelto y qué sigue a mano.

## Los roles

En una unidad compartida: todo el equipo «Lector» en la unidad; quien administra, «Administrador»; el dueño de un área y quienes colaboran en ella, «Gestor de contenido» en la carpeta del área; quien colabora en un proyecto, «Gestor de contenido» solo en la de ese proyecto. «Colaborador» no sirve para escribir con el método, porque no deja mover ni borrar archivos, y «Gestor de contenido» en la unidad entera abre la escritura en todas las áreas. En «Mi unidad» los roles son «Lector» y «Editor», y «Editor» hace de «Gestor de contenido». Lo restringido lleva acceso limitado en su carpeta.
