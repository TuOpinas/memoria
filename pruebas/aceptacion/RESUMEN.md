# Pruebas de aceptación · resumen para quien acepta

Escenarios aprobados por Juanjo Jiménez-Alfaro el 2026-11-22, en el plan (fase F1, versión 1.27.1). Este resumen está escrito a mano; desde la pieza P09 se genera desde las propias pruebas.

## Qué buscan

El kit entrega a cada proyecto una comprobación automática que GitHub corre en cada pull request (aquí, «la comprobación»). Estas pruebas buscan que esa comprobación elija bien las pruebas de cada pieza, las corra todas de una vez y no deje pasar archivos o títulos mal puestos.

## Cómo están planteadas

Cada prueba arma un repositorio de mentira con un pull request de mentira, corre sobre él la comprobación tal como la entrega el kit y mira qué pasó: si quedó en verde o en rojo, qué pruebas corrieron y qué dijeron sus mensajes de error.

Cada fila de abajo lleva el título tal como lo imprime la prueba al correr, para poder casar un «FALLA» con su fila. Las filas marcadas **Añadido** no están en los escenarios aprobados: son casos de control, y se aprueban con este resumen.

Hoy fallan todas las filas menos una, y deben: las piezas aún no existen. La columna «La pone en verde» dice qué pieza hace pasar cada fila.

## P01 · Selección exacta de la pieza

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Solo corren las pruebas de la pieza | P1 está activa y su prueba pasa. P10 tiene una prueba en la carpeta, que falla, y todavía no está activa | Corre la prueba de P1 y no la de P10; la comprobación queda en verde | P01 |
| El fallo nombra a su pieza (falla P1, pasa P10) | P1 y P10 activas; la prueba de P1 falla | Queda en rojo, y el error nombra a P1 y no a P10 | P01 |
| **Añadido:** El fallo nombra a su pieza (falla P10, pasa P1) | Lo mismo, al revés | Queda en rojo, y el error nombra a P10 y no a P1 | P01 |
| **Añadido:** Con todas las pruebas pasando, el check queda en verde | P1 y P10 activas; las dos pasan | Corren las dos y queda en verde | P01 |

**Cambia un escenario aprobado, y pide tu aprobación.** El primero decía «P1 y P10 activas; al correr P1, solo corre la de P1». Con la pieza P02 todas las activas corren juntas, así que «correr solo P1» deja de existir. La prueba lo plantea así: P10 tiene pruebas pero aún no está activa, y no debe correr.

## P02 · Una sola corrida

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Una corrida prueba todas las piezas activas | P1, P2 y P3 activas; fallan P1 y P3. P4 tiene una prueba que falla y no está activa | Corren las tres en una sola corrida y no la de P4; queda en rojo, y el error nombra a P1 y a P3 | P02 |
| Una prueba saltada no cuenta como pasada (la saltada es de P1) | P1 y P2 activas; P1 tiene una prueba que pasa y otra que se salta | Queda en rojo y el error nombra a P1, no a P2 | P01 |
| **Añadido:** Una prueba saltada no cuenta como pasada (la saltada es de P2) | Lo mismo, al revés | Queda en rojo y el error nombra a P2, no a P1 | P01 |
| **Añadido:** Con todas las pruebas pasando, una sola corrida y el check en verde | P1, P2 y P3 activas y pasando; P4 falla y no está activa | Corren las tres en una sola corrida, no la de P4, y queda en verde | P02 |

Las dos filas de la prueba saltada son un seguro: la comprobación de hoy ya rechaza las saltadas, y pasan en cuanto P01 está hecha. Están para que P02 no lo rompa.

## P03 · «Tiene pruebas» por el nombre del archivo

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| El archivo de una prueba empieza por su pieza (tres casos) | Un pull request «Escenarios · P1» trae `P1_alta.py`, bien nombrado, y otro archivo mal nombrado: `test_P1_extra.py`, `P1extra.py` o `extra_P1.py` | Queda en rojo, y el error nombra el archivo malo y dice que empieza por «P1_» | P03 |
| **Añadido:** Un pull request de escenarios bien nombrado queda en verde | «Escenarios · P1» solo con `P1_alta.py`, que falla porque la pieza no existe | Queda en verde | P01 |
| Un título mal escrito no se cuela («P01: alta») | P01 tiene pruebas; un pull request de código se titula «P01: alta» | Queda en rojo y el error dice que el título empieza «P01 · » | P03 |
| **Añadido:** Un título mal escrito no se cuela («P07: alta») | Lo mismo con P07, para que el mensaje no lleve «P01» fijo | Queda en rojo y el error dice «P07 · » | P03 |
| **Añadido:** Un título así, de una pieza sin pruebas, no falla por el título | P09 no tiene pruebas; el pull request se titula «P09: algo» | Queda en verde. Es la única fila que hoy ya pasa | — |
| **Añadido:** El pull request de la pieza, bien titulado, queda en verde | «P01 · alta» añade P01 a la lista de activas, y su prueba pasa | Queda en verde | P01 |

## Lo que las pruebas piden de más

Además de las filas «Añadido», las pruebas exigen cuatro cosas que tus escenarios no dicen con esas palabras:

1. El nombre de la pieza que falla tiene que ir en un mensaje de error de la comprobación, no en cualquier parte de la salida.
2. Ningún mensaje de error puede nombrar a una pieza cuyas pruebas pasan. Un error como «Falla P1 (activas: P1, P2, P3)» no vale.
3. «Una sola corrida» se comprueba viendo que todas las pruebas corrieron en el mismo proceso.
4. El error de un archivo mal nombrado tiene que traer el nombre del archivo y el prefijo «P1_» tal cual.

## P04 no está en este pull request

Su prueba es de otro tipo: el seguimiento lo hace Claude, sin programa, así que se prueba con una sesión real. Su escenario se retiró de aquí porque todavía no puede correr y no comprobaba la cita que no coincide con el plan. Vuelve en su propio pull request, con pull requests ya unidos, que es lo que mira el seguimiento.

## Lo que no es una prueba

- `correr.py` corre las pruebas de las piezas que se le piden. Su última línea, «N pasan · M fallan · K saltadas», cuenta archivos de prueba, no filas de este resumen. Una prueba que no arranca cuenta como error, no como fallo.
- `flujo.py` arma el repositorio de mentira y corre la comprobación. Entiende una parte de lo que GitHub admite; ante lo que no entiende, se detiene con un error en vez de correr otra cosa.
