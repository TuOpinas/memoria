# Pruebas de aceptación · resumen para quien acepta

Escenarios aprobados por Juanjo Jiménez-Alfaro el 2026-11-22, en el plan (fase F1, versión 1.27.1). Este resumen está escrito a mano; desde la pieza P09 lo genera `correr.py` desde la ficha de cada prueba y el check comprueba que coincide.

## Qué buscan

Que el check de pruebas de aceptación que el kit entrega a cada proyecto (la plantilla `pruebas-aceptacion.yml`) elija bien las pruebas de cada pieza, las corra de una vez y no deje pasar nombres o títulos mal puestos; y que el seguimiento compruebe la aprobación que cita un pull request.

## Cómo están planteadas

- **P01 a P03** montan un repositorio de mentira con un pull request de mentira (archivos, lista de piezas activas y título) y corren sobre él los pasos reales de la plantilla, como lo haría GitHub. Las pruebas «sembradas» dentro de ese repositorio dejan una marca al correr: así se sabe cuáles corrieron y en qué proceso.
- **P04** es un escenario de evals: el seguimiento lo hace el modelo, sin script, así que se prueba con una sesión real de Claude sobre un GitHub falso. No entra en el check obligatorio y todavía no corre: falta el modo de pull requests falsos del arnés, que llega con «Kit · ».
- Hoy todas fallan, y deben: las piezas aún no existen.

## P01 · Selección exacta de la pieza · `P01_seleccion_exacta.py`

| Escenario | Cómo se monta | Qué hace | Resultado esperado |
|---|---|---|---|
| Solo corren las pruebas de la pieza | P1 y P10 activas, con `P1_alta.py` y `P10_baja.py` | Corre las pruebas de P1 | Corre `P1_alta.py` y no `P10_baja.py` |
| El fallo nombra a su pieza | P1 y P10 activas; la prueba de P1 falla y la de P10 pasa | Corre el check en un pull request de código | Falla, la prueba de P1 llegó a correr, el error nombra a P1 y no a P10 |
| *Añadido:* el caso al revés | Lo mismo, con la de P10 fallando | Corre el check | Falla y nombra a P10, no a P1 |

## P02 · Una sola corrida · `P02_una_corrida.py`

| Escenario | Cómo se monta | Qué hace | Resultado esperado |
|---|---|---|---|
| Una corrida prueba todas las piezas activas | P1, P2 y P3 activas; fallan P1 y P3, pasa P2 | Corre el check | Corren las tres en un solo proceso; falla y nombra a P1 y a P3, no a P2 |
| Una prueba saltada no cuenta como pasada | P1 y P2 activas; P1 tiene una prueba que pasa y otra saltada | Corre el check | Falla y nombra a P1, no a P2 |
| *Añadido:* el caso al revés | La saltada está en P2 | Corre el check | Falla y nombra a P2, no a P1 |

## P03 · «Tiene pruebas» por el nombre del archivo · `P03_nombre_y_titulo.py`

| Escenario | Cómo se monta | Qué hace | Resultado esperado |
|---|---|---|---|
| El archivo de una prueba empieza por su pieza | Un pull request «Escenarios · P1» con `test_P1_alta.py`, con `P1alta.py` y con `alta_P1.py` (tres casos) | Corre el check | Falla y el error dice que el archivo tiene que empezar por «P1_» |
| Un título mal escrito no se cuela | P01 tiene pruebas; un pull request de código titulado «P01: alta» | Corre el check | Falla y el error dice que el título empieza por «P01 · » |

## P04 · La aprobación citada se comprueba · `pruebas/evals/escenarios/30-P04-aprobacion-citada.md`

| Escenario | Cómo se monta | Qué hace | Resultado esperado |
|---|---|---|---|
| Una cita que coincide con el plan cuenta | Quien acepta no tiene GitHub; el #11 toca las pruebas y cita su «Aprobó:» tal como está en el plan | Pide el seguimiento | El #11 sale como aprobado por quien acepta |
| Una cita que falta o no coincide se señala | El #12 no cita nada; el #13 cita a otra persona | Pide el seguimiento | Dice «sin aprobación de quien acepta» |

Límite de P04: con las comprobaciones que hoy tiene el arnés de evals se puede pedir que la frase aparezca y que el #11 no la lleve, pero no que la lleven en concreto el #12 y el #13.

## Lo que no es una prueba

- `correr.py`: el ejecutor. Corre los archivos que empiezan exactamente por la pieza y «_» y termina con «N pasan · M fallan · K saltadas». Sale con 0 si todo pasa, con 1 si algo falla o se salta y con 2 si no se pudo correr.
- `flujo.py`: el arnés que monta el repositorio de mentira y corre los pasos de la plantilla.

## Para tener presente al aprobar

- Los casos «al revés» de P01 y P02 no están en los escenarios aprobados. Se añadieron porque sin ellos la plantilla de hoy cumple «falla y nombra a P1» por accidente.
- La segunda prueba de P01 y las de P02 dependen de P03: usan archivos `P1_….py`, que la plantilla de hoy no recoge.
- Si P02 quita el comando «por pieza», el primer escenario de P01 hay que releerlo.
