# Pasar a la estructura de la 1.22

Anexo de la skill `sesion`. Se lee cuando la sección ESTRUCTURA de `abrir.py` dice «ANTERIOR en …» y la persona dice que sí a migrar. Es la ronda de estructura decidida el 2026-10-24: una sola sección de estatus («Estatus») en `proyecto.md` y `area.md`, `Responsable` en lugar de «Dueño», `aportacion` en lugar de `afirma`, «Descartado», «Tema», la columna «Acceso» en `guia.md` y `fuentes/inventario.md` en lugar de `enlaces.md`. Cada raíz se migra sola, por partes: cada responsable migra sus áreas al abrir sesión, y el responsable de contexto, además, `guia.md`. Mientras tanto una raíz mezclada funciona, porque durante la 1.22 los scripts y las skills leen los nombres viejos y los nuevos y escriben solo los nuevos. No se carga `escribir.md` para esto: el script no redacta nada, solo renombra, y nunca borra contenido.

## La oferta

Una línea al final de la respuesta, después de lo que se pidió: «Tu parte de la carpeta usa la estructura de antes de la 1.22 (<lo que nombra el veredicto: las áreas y, si está, `guia.md`>). ¿La paso a la nueva? Renombra secciones y claves sin perder nada, y deja una línea en la bitácora de cada proyecto.» Con la herramienta de preguntas si está («Migrar ahora» / «Después»), o en texto. Una vez por conversación. Si esa respuesta ya pide confirmar otra cosa (las decisiones y el `Estatus` de un cierre, una prioridad), la oferta espera a la respuesta siguiente, para que un «sí» no valga por dos. Con «Después», no se vuelve a ofrecer en esa conversación y se trabaja igual.

**Sin consola** (la carpeta está conectada pero el shell de la computadora no la monta) no se ofrece: la migración renombra archivos y escribe en muchos a la vez, y por la copia del contenedor no hay camino seguro. Se dice en media línea que se migra en una sesión con consola, y se trabaja igual: la raíz sin migrar funciona.

**Las raíces de otras organizaciones** no se migran desde una sesión de otra raíz: cada una, en la apertura de su responsable. La skill `migrar` no interviene: es para adoptar estructuras ajenas.

**Si guia.md entra en la migración**, conviene que el equipo tenga ya el plugin 1.22: un plugin 1.21 lee lo restringido de la columna «Quién la lee», que la migración deja como estaba precisamente para eso, pero no lee el `Estatus` ni «Responsable», así que su apertura y su tablero verían vacíos esos datos hasta actualizar. Se dice en una línea si en la tabla de áreas hay más de una cuenta.

## Con el sí

1. Se trae el script, en la misma llamada que lo corre: con Bash en el contenedor, `python3 <directorio de esta skill>/../../preparar.py '$HOME/memoria' skills/sesion/migrar_estructura.py`, que imprime su línea DESCARGA (y REINTENTO), como con `abrir.py`; un script que no pasa la comprobación no se corre.
2. Con `device_bash`, en la computadora: lo que va detrás de «DESCARGA » seguido de ` && python3 migrar_estructura.py "<raíz en $HOME/mnt>" --cuenta <correo> --nombre "<nombre y apellido del responsable>" --plugin <versión del plugin>`. Una sola corrida, sin `--plan`: la persona ya dijo que sí. Imprime un JSON compacto; lo que hay que leer va primero: `conflictos` (un `inventario.md` o un `taller/estado-anterior.md` que ya existían: se dicen y se dejan para la sesión de ese proyecto), `fallidos` (se dicen y no se repite a ciegas; el script no deja nada a medias: si no pudo escribir el taller, no tocó ese `proyecto.md`), `entradas` (los `sesiones.md` donde dejó su línea «(migracion)») y `resumen` (cuántos archivos por tipo de cambio). `archivos`, al final, es el detalle por ruta y no hace falta leerlo entero.
3. Al terminar, dos o tres líneas: cuántos proyectos y áreas se migraron, que «Estado actual» de cada proyecto quedó en su `taller/estado-anterior.md` (lo que siga valiendo lo lleva al `Estatus` o a `Alcance` la siguiente sesión de ese proyecto), los conflictos si los hubo, y que las áreas de otras personas se migran cuando sus responsables abran sesión con el plugin 1.22.

La entrada «(migracion)» que deja en cada `sesiones.md` no es una sesión: la apertura y el tablero no la cuentan como tal ni la enseñan entre las recientes. Repetir el script no hace nada: lo ya migrado no tiene marcas viejas.

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
