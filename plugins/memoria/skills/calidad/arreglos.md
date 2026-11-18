# El informe de una revisión de arreglos

Anexo de la skill `calidad` (paso 1, «Una revisión de arreglos»). Se lee antes de guardar el informe de una ronda; `comprobar_informe.py` comprueba lo que aquí se pide.

- **Dónde va.** En un informe aparte, `revision-de-calidad-<tema>-arreglos-<n>.md`, junto al de la primera revisión, con `<n>` la ronda (1, 2…). No reescribe el cuerpo de ningún otro informe; el de una versión sigue siendo el que pide `release.sh`, que mira también la última ronda.
- **Tipo.** `Tipo: <tipo>, arreglos <n> de <informe de la primera revisión, sin .md>`, con el mismo `<n>` que el nombre del archivo.
- **Tamaño.** Las líneas que cambió el arreglo frente a lo que leyó la revisión anterior; si no se pueden contar (el arreglo no quedó en un commit propio), las leídas, diciéndolo.
- **Revisores.** Tres; con menos, el motivo entre paréntesis («Revisores: 2 (el arreglo es de una línea)»).
- **Origen de cada hallazgo**, tras `Pesa:`, con estas palabras exactas: «(en el original)», si ya estaba en lo que leyó la primera revisión; «(lo abrió un arreglo anterior)», si lo abrió el arreglo de una ronda anterior; «(lo abrió este arreglo)».
- **Lo que se escapó.** Un hallazgo «(en el original)» se le escapó a la primera revisión: lleva su línea en «Lo que se escapó» de ese informe, aparecido «en la ronda de arreglos <n>». Uno «(lo abrió un arreglo anterior)», en el de la ronda que revisó ese arreglo. La lectura de la efectividad los cuenta como escapados una sola vez, aparte de los que aparecieron fuera de las rondas.
- **Arreglados**, como en cualquier informe, con cuántos de los que impiden («Arreglados: 5 · impiden 1»): `release.sh` no publica una versión si su última ronda deja alguno sin arreglar.
