# Leer la efectividad de las revisiones

Anexo de la skill `calidad` (su paso 8). Se lee solo cuando toca leer la efectividad.

Cuando el paso 6 lo propone, cuando cambia el modelo que se usa o cuando alguien lo pide («¿qué tan bien funcionan las revisiones?»), se leen los informes de `taller/revisiones-de-calidad/` de los proyectos del área que no son restringidos (sus secciones `Medición` y `Lo que se escapó` y las líneas `Lens:`, `Pesa:` y `Modelo:` de cada hallazgo; los informes de antes de la 1.26.2 pueden llevar `Lente:` con las lentes en español, o las mejoras en una lista con las lentes entre paréntesis, y se leen igual) y se reescribe `taller/revisiones-de-calidad/efectividad-de-las-revisiones.md`, uno solo por área: el que ya exista en algún proyecto del área, o si no, en el proyecto donde se pidió; en `borrador`, con `aportacion` y `basado_en`. Como su `aportacion` la ve el área entera, solo lleva cifras agregadas y nombres de proyectos que no son restringidos.

Dice, con el número de revisiones detrás de cada cifra:

- **Por lente:** a cuántos hallazgos llega cada una y a cuántos sola, por peso; la que no encuentra sola nada que impida el objetivo es candidata a juntarse con otra o a quitarse, y la que encuentra sola lo grave no se toca.
- **Por profundidad y tamaño:** hallazgos por cada cien líneas y fallos escapados, según cuántos revisores hubo, y aparte las revisiones de arreglos: desde la 1.26.11 por «, arreglos» en `Tipo:`, y por el nombre del archivo (`-arreglos-`; antes, `-fixes` y `-round-`). Al juzgar las lentes, las revisiones de antes y de después de la 1.26.11 se leen por separado (son de después las fechadas desde la primera sesión del área con «plugin 1.26.11» o más en «Sesión de:»); los paréntesis de `Lens:` con una lente que no corrió se cuentan por peso, y en las rondas, los hallazgos por su origen.
- **Por modelo:** con los contrastes, qué encontró cada modelo que el otro no, por peso y con su costo; sin contraste, solo entre revisiones del mismo tipo y tamaño, diciendo que la comparación es débil. También si revisar con un modelo distinto del que construyó encuentra más.
- **Lo que se escapó:** cuántos estaban al alcance de la revisión y qué lente los habría visto; los que aparecieron en una ronda de arreglos, aparte y una sola vez.
- **Qué cambiar:** cada propuesta con cómo se va a juzgar y tras cuántas revisiones. Esta skill no la adopta: si cambia cómo se revisa, la sesión del proyecto que mantiene el método la registra como decisión, y la versión siguiente del plugin la lleva a la skill.
