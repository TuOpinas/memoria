---
estado: borrador
actualizado: AAAA-MM-DD
aportacion: "[Lo que este documento aporta, en una frase]"
basado_en: []
---

# Plan

Las fases dicen qué valor entrega cada una; las piezas, qué es estar hecha. El estado de las piezas no se escribe aquí: lo da el seguimiento, desde GitHub.

Cambiar una fase o el alcance pide una decisión. Añadir, partir o detallar piezas de la fase en curso, no.

## Fases
| Fase | Qué podrá hacer quién | Versión | Listo cuando | Estado | Horas de cierre |
|---|---|---|---|---|---|
| F1 · [nombre] | [Una frase] | [versión] | [Algo que se comprueba] | en curso | [3] |
| F2 · [nombre] | | | | pendiente | |

Estado: `cerrada`, `en curso` (solo una) o `pendiente`. «Horas de cierre», opcional: las de escenarios, revisión y verificación de la fase, que el tablero suma a las de sus piezas.

### F1 en llano
[Una frase: qué mejora esta fase para quien usa el producto, sin jerga.]

| Pieza | Qué arregla |
|---|---|
| P01 | [En llano, lo que cambia para la persona] |

Horas: espera a [persona]: [qué].
Recibió: [Nombre Apellido, AAAA-MM-DD]

Un bloque así por fase, escrito al planearla. «Recibió:», opcional, como el «Aprobó:» de las piezas: lo escribe quien acepta al cerrar la fase, cuando quien recibe da su conformidad.

## Piezas
Las de fases cerradas se quedan. Un identificador no se reutiliza nunca. «Horas» y «Para antes» son opcionales: las horas de sesión con IA de cada pieza, vacía si no se estiman (el tablero suma por fase las que hay), y lo que Claude pregunta antes de construirla, si se para en ella; las comprobaciones de siempre (los escenarios, la revisión, la verificación y el sí) no se escriben ahí.

| Pieza | Fase | Qué entrega | Horas | Para antes |
|---|---|---|---|---|
| P01 · [nombre] | F1 | [Una frase] | [1.5] | [Qué se pregunta antes de construirla, o vacía] |

## Hecha cuando
Una pieza está hecha cuando pasan sus escenarios. Claude los propone y quien acepta los aprueba antes de que se construya; un escenario aprobado no se cambia sin que lo apruebe otra vez. Lo que no se puede romper lo marca quien acepta con «(esencial)» al final del título del escenario: la verificación de cada fase siguiente lo recorre otra vez, aparte, y con un esencial fallado no hay sí. Una pieza puramente técnica no tiene escenarios ni verificación: lo dice aquí, «pieza técnica, sin escenarios», y también lo aprueba quien acepta.

### P01 · [nombre]
Aprobó: [Nombre Apellido, AAAA-MM-DD]

- **[Lo que se comprueba, en una frase]**
  Dado [la situación de partida]
  Cuando [lo que hace la persona]
  Entonces [lo que tiene que pasar]
- **[Lo que no se puede romper, en una frase] (esencial)**
  Dado [...]
  Cuando [...]
  Entonces [...]
- **[El caso de error]**
  Dado [...]
  Cuando [...]
  Entonces [...]

## Cómo avanza
- Se construye por bloques: una o varias piezas en un pull request a la rama principal, unido y desplegado antes del siguiente. Claude propone cómo se agrupan; lo normal es una pieza por pull request.
- Un subagente con contexto limpio, que lanza la sesión que construye antes de que exista el código de la pieza y que lee solo lo que su encargo nombra (este plan, el diseño, el `CLAUDE.md`), convierte los escenarios aprobados en pruebas, en archivos que empiezan por el identificador de su pieza y «_» (`P01_acceso.py`), en su propio pull request («Escenarios · P01»), que solo toca la carpeta de pruebas de aceptación. Se une en verde cuando CI comprueba que esas pruebas fallan, porque la pieza aún no existe.
- El pull request de la pieza no toca esa carpeta (CI lo impide) y añade el identificador de la pieza a la lista de piezas activas, fuera de la carpeta: desde ahí sus pruebas son obligatorias, y CI no deja quitarla de la lista. Una pieza técnica no entra en la lista. Quien construye lo une con todo en verde y la revisión de calidad hecha.
- **Cambiar los escenarios de una pieza ya activa**, con la nueva aprobación de quien acepta: su pull request de escenarios («Escenarios · P01») cambia las pruebas y, si la pieza aún no las cumple, la saca de la lista, sin tocar código; el siguiente pull request de la pieza la vuelve a añadir cuando las cumple. Solo él y una reversión de la pieza pueden sacarla.
- Un pull request que toca las pruebas de aceptación o su workflow, o saca una pieza de la lista, lo une, o lo aprueba por escrito, quien acepta. Sin cuenta de GitHub, quien acepta aprueba los escenarios en este plan, y quien une el pull request cita en él esa aprobación («Aprobó: Nombre Apellido, AAAA-MM-DD, en el plan»).
- Antes del sí de cada pieza con escenarios, una sesión de contexto limpio, en el modelo que no la construyó, recorre Release contra los escenarios y deja un reporte con evidencia, criterio por criterio (sin Release, la aplicación levantada desde lo unido, con datos de prueba). Quien da el sí lo lee, con el seguimiento.
- Claude se para y pregunta a quien acepta en los puntos de control del `CLAUDE.md`.
- Al cumplirse «Listo cuando», quien acepta decide si se sigue, se cambia el plan o se para.

## Cómo se sabe en qué estado está cada pieza
Por los pull requests a la rama principal cuyo título empieza por el identificador de la pieza: «P01 · …», o «P01 + P02 · …» si un mismo pull request lleva varias.
- **Pendiente:** no tiene ninguno abierto ni unido.
- **En curso:** tiene alguno abierto.
- **Unida:** todos están unidos (está en Release, si lo hay).
- **Revertida:** se unió una reversión («Revert "P01 · …"»); vuelve a `en curso` con el siguiente pull request de la pieza, y el seguimiento lo dice.
- **Entregada:** lo unido ya pasó a Prod con su sí. Donde unir publica («Paso a Prod» dice que unir el pull request de versión es el paso a Prod), una pieza unida con él ya está entregada, y el sí es la línea «Aprobó: Nombre Apellido, AAAA-MM-DD» de su descripción.

Un pull request cerrado sin unir no cuenta, ni los que van a otras ramas, ni los de escenarios («Escenarios · P01») ni los del kit («Kit · »), que el seguimiento lista aparte. Un arreglo lleva el identificador de la pieza que arregla. Los de bots no llevan ninguno; los demás sin pieza salen en el seguimiento como «fuera del plan».
