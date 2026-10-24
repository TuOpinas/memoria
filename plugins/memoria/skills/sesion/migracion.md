# Pasar a la estructura de la 1.22

Anexo de la skill `sesion`. Se lee cuando la sección ESTRUCTURA de `abrir.py` dice «ANTERIOR en …» y la persona dice que sí a migrar. Es la ronda de estructura decidida el 2026-10-24: una sola sección de estatus («Estatus») en `proyecto.md` y `area.md`, `Responsable` en lugar de «Dueño», `aportacion` en lugar de `afirma`, «Descartado», «Tema», la columna «Acceso» en `guia.md` y `fuentes/inventario.md` en lugar de `enlaces.md`. Cada raíz se migra sola, al abrir sesión: cada responsable migra sus áreas, y el responsable de contexto, además, `guia.md` y las áreas de los demás responsables que su carpeta le deja leer, para que una raíz no quede a medias porque alguien no abre sesión. Mientras tanto una raíz mezclada funciona, porque durante la 1.22 los scripts y las skills leen los nombres viejos y los nuevos y escriben solo los nuevos. No se carga `escribir.md` para esto: el script no redacta nada, solo renombra, y nunca borra contenido.

## La pregunta

Va antes de responder a lo que se pidió, y bloquea: la respuesta es el recuadro «Memoria de trabajo» y la pregunta, y nada más hasta que la persona conteste. Una línea al final de una respuesta larga no se ve; una pregunta que para la conversación, sí. Con la herramienta de preguntas si está (`AskUserQuestion`: una pregunta, «Tu parte de la carpeta usa la estructura de antes de la 1.22 (<lo que nombra el veredicto>). ¿La paso a la nueva antes de seguir? Renombra secciones y claves sin perder nada y deja una línea en la bitácora de cada proyecto.», con las opciones «Migrar ahora» y «Después»); si en esa app el texto que va antes de una herramienta no se muestra tal cual (hay `SendUserMessage`), el recuadro se manda antes con él. Sin la herramienta, la misma pregunta en texto, como única cosa después del recuadro, y se espera.

Si el veredicto nombra áreas «(de <nombre>)», la pregunta lo dice: son de otros responsables y las migra quien responde por el contexto, con una entrada en la bitácora de cada proyecto que dice por quién. Si nombra `guia.md` y la tabla de áreas tiene más de una cuenta, añade que conviene que el equipo actualice el plugin (abajo).

Con «Migrar ahora», se sigue «Con el sí» y después se responde a lo que se pidió; con «Después», se responde a lo que se pidió, no se vuelve a preguntar en esa conversación y se trabaja igual. Una vez por conversación. En una sesión sin nadie que conteste (una tarea programada), no se pregunta ni se migra.

**Sin consola** (la carpeta está conectada pero el shell de la computadora no la monta, `sin-consola.md` de `convenciones`) se pregunta igual, y con el sí se sigue «Sin consola», abajo. Ahí la apertura solo ve los `area.md` y el proyecto que se abre, así que el veredicto sale de ellos; un área ajena que no está en la copia no entra en el veredicto, y se migra cuando su responsable abra sesión.

**Las raíces de otras organizaciones** no se migran desde una sesión de otra raíz: cada una, en la apertura de su responsable. La skill `migrar` no interviene: es para adoptar estructuras ajenas.

**Si guia.md entra en la migración**, conviene que el equipo tenga ya el plugin 1.22: un plugin 1.21 lee lo restringido de la columna «Quién la lee», que la migración deja como estaba precisamente para eso, pero no lee el `Estatus` ni «Responsable», así que su apertura y su tablero verían vacíos esos datos hasta actualizar. Se dice en una línea si en la tabla de áreas hay más de una cuenta.

## Con el sí

1. Se trae el script, en la misma llamada que lo corre: con Bash en el contenedor, `python3 <directorio de esta skill>/../../preparar.py '$HOME/memoria' skills/sesion/migrar_estructura.py`, que imprime su línea DESCARGA (y REINTENTO), como con `abrir.py`; un script que no pasa la comprobación no se corre.
2. Con `device_bash`, en la computadora: lo que va detrás de «DESCARGA » seguido de ` && python3 migrar_estructura.py "<raíz en $HOME/mnt>" --cuenta <correo> --nombre "<nombre y apellido del responsable>" --plugin <versión del plugin>`. Una sola corrida, sin `--plan`: la persona ya dijo que sí. Imprime un JSON compacto; lo que hay que leer va primero: `conflictos` (un `inventario.md` o un `taller/estado-anterior.md` que ya existían: se dicen y se dejan para la sesión de ese proyecto), `fallidos` (se dicen y no se repite a ciegas; el script no deja nada a medias: si no pudo escribir el taller, no tocó ese `proyecto.md`), `entradas` (los `sesiones.md` donde dejó su línea «(migracion)»), `ajenas` (las áreas de otros responsables que migró, solo para el responsable de contexto) y `resumen` (cuántos archivos por tipo de cambio). `archivos`, al final, es el detalle por ruta y no hace falta leerlo entero.
3. Al terminar, dos o tres líneas: cuántos proyectos y áreas se migraron, que «Estado actual» de cada proyecto quedó en su `taller/estado-anterior.md` (lo que siga valiendo lo lleva al `Estatus` o a `Alcance` la siguiente sesión de ese proyecto), los conflictos si los hubo, las áreas de otros responsables que se migraron, si las hubo (`ajenas`), y, si no fue el responsable de contexto, que las áreas de otras personas se migran cuando sus responsables abran sesión con el plugin 1.22.

La entrada «(migracion)» que deja en cada `sesiones.md` no es una sesión: la apertura y el tablero no la cuentan como tal ni la enseñan entre las recientes. Repetir el script no hace nada: lo ya migrado no tiene marcas viejas.

## Sin consola

El mismo script corre en el contenedor sobre la copia, y lo que cambia vuelve con `espejo.py` como en un cierre sin consola; lo único que no puede devolver, renombrar `enlaces.md` a `inventario.md`, lo hace el conector de Google Drive. El resultado es el mismo que con consola. `espejo.py` está en la raíz del plugin; `<la copia>` es la de la apertura.

1. **El listado.** `device_list_dir` recursivo de cada área que nombra el veredicto (si sale `truncated`, por proyecto). Se escribe en un archivo del contenedor, una ruta relativa a la raíz por línea, solo lo que cuenta: `<area>/area.md`, el `proyecto.md` y el `sesiones.md` de cada proyecto, los `.md` de sus `entregables/` y `taller/`, y los `enlaces.md` o `inventario.md` de sus `fuentes/` y `restringido/`.
2. **La copia.** `espejo.py migracion "<la copia>" <listado>` imprime qué traer; se trae con `device_stage_files`, de 50 en 50 (lo que no existe, con `espejo.py falta`), y se repite hasta COMPLETA. Trae los `.md` del taller de las áreas que se migran: la migración reescribe sus cabeceras y su cuerpo no sale del contenedor ni se lee. De `fuentes/` y `restringido/` no trae nada.
3. **El plan.** `python3 migrar_estructura.py "<la copia>" --cuenta <correo> --plan > plan.json` y `espejo.py migracion "<la copia>" --plan plan.json`: declara nuevos los archivos del taller que crea e imprime TRAER, los archivos que va a cambiar. Si `renombrados` del plan no está vacío y no hay conector de Google Drive, se dice que hace falta conectarlo (`SuggestConnectors`) y se para aquí: nada se ha escrito.
4. **Registrar.** Lo de TRAER se trae otra vez y se registra con lo que dio `device_stage_files`: `espejo.py registrar "<la copia>" <ruta> <mtimeMs> <bytes> …`, todo en una llamada.
5. **Migrar la copia.** `python3 migrar_estructura.py "<la copia>" --cuenta <correo> --nombre "<nombre>" --plugin <versión> --sin-consola > salida.json` y `espejo.py migracion "<la copia>" --hecha salida.json`. Si no sale `listo`, lo de `sin_registrar` se trae, se registra y se repite este paso (el script no repite lo hecho).
6. **Renombrar.** Cada par de `renombrar`, con el conector, como dice «Mover, renombrar» de `sin-consola.md`: `update_file` con el `title` nuevo. Se comprueba con `device_list_dir`. Si uno falla, se para: lo renombrado ya vale, porque durante la 1.22 todo lee los dos nombres, y la copia se tira.
7. **Devolver.** `espejo.py devolver "<la copia>" "<ruta de la raíz en la computadora>"`: los archivos nuevos del taller van solos en el primer lote. Ese lote se devuelve con `device_commit_files`; solo si llegaron todos, los demás. Después, `espejo.py hecho` con lo escrito. Un rechazo por fecha (alguien cerró entre medias) se trata como en `sin-consola.md`, punto 5: se trae, se registra y se repite el paso 5 sobre lo nuevo.

Cuesta una llamada de listado por área, una de traer por cada 50 archivos (dos veces lo que cambia) y una de devolver por cada 50; en una raíz de 20 proyectos, unas quince llamadas.

## Lo que hace el script, en una tabla

| Dónde | Qué |
|---|---|
| `guia.md` (solo el responsable de contexto) | «Dueño» → «Responsable» en el encabezado; columna «Acceso» («Abierta» o «Restringida») detrás de «Quién la lee», que se deja como estaba; `enlaces.md` → `inventario.md` en el texto |
| `area.md` | «Panorama» y «Prioridades ahora» → «Estatus» (fecha y primera frase del Panorama en negrita, prioridades debajo de «Siguiente», una línea por proyecto activo); con un «Estatus» ya al lado, se queda el más reciente, las prioridades que falten entran en «Siguiente» y el otro bloque va al taller; «Dueño:» → «Responsable:»; la línea de cada entregable vigente, desde su `aportacion`; secciones en el orden de la 1.22 |
| `proyecto.md` | «En corto» → «Estatus» (con los dos, el más reciente); sin «En corto», un Estatus mínimo con la fecha de la cabecera y la primera frase de «Estado actual»; un proyecto cerrado dice en su Estatus que terminó y cómo; «Terminado significa» → segunda frase de «Objetivo»; «Sí/No» → «Entra/No entra»; «Dueño:» → «Responsable:», sale «Consumen esto:»; «Estado actual» entero → `taller/estado-anterior.md`; secciones en el orden de la 1.22 |
| cabeceras de `entregables/` y `taller/` | `afirma` → `aportacion`; `basado_en` con `inventario.md`; `actualizado` no se mueve |
| `fuentes/enlaces.md`, `restringido/enlaces.md` | → `inventario.md` |
| `sesiones.md` de cada proyecto migrado | una entrada «## AAAA-MM-DD (migracion)», de una frase |

No toca `decisiones.md`, las entradas ya escritas de `sesiones.md`, `base/` ni lo que hay dentro de `fuentes/` y `restringido/` salvo su inventario. Cada archivo se relee y se vuelve a transformar en el momento de escribirlo, bajo el cerrojo de `cerrar.py`, para no pisar un cierre que llegue entre medias.
