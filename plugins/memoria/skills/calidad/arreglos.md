# El informe de una revisión de arreglos

Anexo de la skill `calidad` (paso 1, «Una revisión de arreglos»). Se lee al acordar el alcance de una ronda, porque los revisores marcan el origen de cada hallazgo. `comprobar_informe.py` comprueba el nombre y el tipo, los revisores, el origen y los arreglados; `release.sh`, además, la medición entera de cada ronda de una versión.

- **Dónde va.** En un informe aparte, `revision-de-calidad-<tema>-arreglos-<n>.md`, junto al de la primera revisión, con `<n>` la ronda (1, 2…). No reescribe el cuerpo de ningún otro informe; el de una versión sigue siendo el que pide `release.sh`, que mira también la última ronda.
- **Tipo.** `Tipo: <tipo>, arreglos <n> de <informe de la primera revisión, sin .md>`, con el mismo `<n>` que el nombre del archivo.
- **Tamaño.** Las líneas que cambió el arreglo frente a lo que leyó la revisión anterior; si no se pueden contar porque el arreglo no se guardó aparte, «no consta» y por qué.
- **Revisores.** Tres; con menos, el motivo entre paréntesis («Revisores: 2 (el arreglo es de una línea)»).
- **Origen de cada hallazgo**, tras `Pesa:`, con estas palabras exactas: «(en el original)», si ya estaba en lo que leyó la primera revisión; «(lo abrió un arreglo anterior)», si lo abrió el arreglo de una ronda anterior; «(lo abrió este arreglo)».
- **Lo que se escapó.** Un hallazgo «(en el original)» se le escapó a la primera revisión: lleva su línea en «Lo que se escapó» de ese informe, aparecido «en la ronda de arreglos <n>». Uno «(lo abrió un arreglo anterior)», en el de la ronda que revisó ese arreglo. La lectura de la efectividad los cuenta como escapados una sola vez, aparte de los que aparecieron fuera de las rondas.
- **Arreglados**, como en cualquier informe, con cuántos de los que impiden («Arreglados: 5 · impiden 1»): `release.sh` no publica una versión si su informe o alguna de sus rondas deja alguno sin arreglar. Detrás puede ir una nota entre paréntesis («Arreglados: 4 · impiden 1 (el 3 no se arregla: decisión del 18 de noviembre)»).
