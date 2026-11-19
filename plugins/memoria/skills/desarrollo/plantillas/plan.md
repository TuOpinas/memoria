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
| Fase | Qué podrá hacer quién | Versión | Listo cuando | Estado |
|---|---|---|---|---|
| F1 · [nombre] | [Una frase] | [versión] | [Algo que se comprueba] | en curso |
| F2 · [nombre] | | | | pendiente |

Estado: `cerrada`, `en curso` (solo una) o `pendiente`.

## Piezas
Las de fases cerradas se quedan. Un identificador no se reutiliza nunca.

| Pieza | Fase | Qué entrega |
|---|---|---|
| P01 · [nombre] | F1 | [Una frase] |

## Hecha cuando
Una pieza está hecha cuando pasan sus escenarios. Claude los propone y quien acepta los aprueba antes de que se construya; un escenario aprobado no se cambia sin que lo apruebe otra vez.

### P01 · [nombre]
Aprobó: [Nombre Apellido, AAAA-MM-DD]

- **[Lo que se comprueba, en una frase]**
  Dado [la situación de partida]
  Cuando [lo que hace la persona]
  Entonces [lo que tiene que pasar]
- **[El caso de error]**
  Dado [...]
  Cuando [...]
  Entonces [...]

## Cómo avanza
- Se construye por bloques: una o varias piezas en un pull request a la rama principal, unido y desplegado antes del siguiente. Claude propone cómo se agrupan; lo normal es una pieza por pull request.
- Una sesión aparte, que ve este plan, el diseño y el `CLAUDE.md` del repositorio pero no el código de la aplicación, convierte los escenarios aprobados en pruebas que fallan, con el identificador de su pieza en el nombre, en su propio pull request («Escenarios · P01»), que solo toca la carpeta de pruebas de aceptación. Esas pruebas no van en la suite obligatoria hasta que su pieza se une: el pull request de la pieza las añade al comando de la suite, que vive fuera de esa carpeta. El pull request de la pieza no toca la carpeta: CI lo impide.
- Quien construye une la pieza cuando pasan sus pruebas de aceptación, con su salida en el pull request, y la suite obligatoria sigue en verde, con la revisión de calidad hecha.
- Antes del sí, una sesión de contexto limpio, en otro modelo, recorre Release (sin Release, la aplicación levantada desde lo unido) contra los escenarios y deja un reporte con evidencia, criterio por criterio. Quien da el sí lo lee, con el seguimiento.
- Claude se para y pregunta a quien audita en los puntos de control del `CLAUDE.md`.
- Al cumplirse «Listo cuando», quien audita y quien acepta deciden si se sigue, se cambia el plan o se para. Si no coinciden, decide quien acepta.

## Cómo se sabe en qué estado está cada pieza
Por los pull requests a la rama principal cuyo título empieza por el identificador de la pieza: «P01 · …», o «P01 + P02 · …» si un mismo pull request lleva varias.
- **Pendiente:** no tiene ninguno abierto ni unido.
- **En curso:** tiene alguno abierto.
- **Unida:** todos están unidos (está en Release, si lo hay).
- **Revertida:** se unió una reversión («Revert "P01 · …"»); vuelve a `en curso` con el siguiente pull request de la pieza, y el seguimiento lo dice.
- **Entregada:** lo unido ya pasó a Prod con su sí.

Un pull request cerrado sin unir no cuenta, ni los que van a otras ramas, ni los de escenarios («Escenarios · P01») ni los del kit («Kit · »), que el seguimiento lista aparte. Un arreglo lleva el identificador de la pieza que arregla. Los de bots no llevan ninguno; los demás sin pieza salen en el seguimiento como «fuera del plan».
