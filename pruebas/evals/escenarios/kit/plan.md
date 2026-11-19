---
estado: borrador
actualizado: {HOY-20}
aportacion: "El plan del portal de clientes: fases, piezas y sus escenarios."
basado_en: []
---

# Plan

Las fases dicen qué valor entrega cada una; las piezas, qué es estar hecha. El estado de las piezas no se escribe aquí: lo da el seguimiento, desde GitHub.

Cambiar una fase o el alcance pide una decisión. Añadir, partir o detallar piezas de la fase en curso, no.

## Fases
| Fase | Qué podrá hacer quién | Versión | Listo cuando | Estado |
|---|---|---|---|---|
| F1 · Portal | Cliente Uno ve sus propuestas | 0.1 | Cliente Uno entra y ve la suya | en curso |
| F2 · Firma | Cliente Uno firma en línea | 0.2 | Una propuesta firmada | pendiente |

Estado: `cerrada`, `en curso` (solo una) o `pendiente`.

## Piezas
Las de fases cerradas se quedan. Un identificador no se reutiliza nunca.

| Pieza | Fase | Qué entrega |
|---|---|---|
| P01 · Acceso | F1 | El acceso de cada cliente |
| P02 · Propuestas | F1 | La lista de sus propuestas |
| P03 · Firma | F2 | Firmar una propuesta |

## Hecha cuando
Una pieza está hecha cuando pasan sus escenarios. Claude los propone y quien acepta los aprueba antes de que se construya; un escenario aprobado no se cambia sin que lo apruebe otra vez.

### P01 · Acceso
Aprobó: Ana Prueba, {HOY-15}

- **Un cliente entra con su correo**
  Dado que Cliente Uno tiene cuenta
  Cuando entra con su correo y el código que le llega
  Entonces ve su portal
- **Un correo sin cuenta no entra**
  Dado un correo que no es de ningún cliente
  Cuando intenta entrar
  Entonces ve que no tiene acceso y no recibe código

### P02 · Propuestas
Aprobó: Ana Prueba, {HOY-15}

- **Ve las suyas y no las de otros**
  Dado que Cliente Uno y Cliente Dos tienen propuestas
  Cuando Cliente Uno entra a su portal
  Entonces ve solo las suyas

## Cómo avanza
- Una sesión aparte, que solo ve este plan y el diseño, convierte los escenarios aprobados en pruebas que fallan, en su propio pull request («Escenarios · P01»), que solo toca la carpeta de pruebas de aceptación. El pull request de la pieza no la toca: CI lo impide.
- Quien construye une la pieza cuando pasan sus pruebas de aceptación y las demás siguen en verde, con la revisión de calidad hecha.
- Antes del sí, una sesión de contexto limpio recorre Release contra los escenarios y deja un reporte con evidencia, criterio por criterio. Quien da el sí lo lee, con el seguimiento.
- Claude se para y pregunta a quien audita en los puntos de control del `CLAUDE.md`.
- Al cumplirse «Listo cuando», quien audita y quien acepta deciden si se sigue, se cambia el plan o se para. Si no coinciden, decide quien acepta.

## Cómo se sabe en qué estado está cada pieza
Por los pull requests a la rama principal cuyo título empieza por el identificador de la pieza: «P01 · …», o «P01 + P02 · …» si un mismo pull request lleva varias.
- **Pendiente:** no tiene ninguno abierto ni unido.
- **En curso:** tiene alguno abierto.
- **Unida:** todos están unidos (está en Release, si lo hay).
- **Entregada:** lo unido ya pasó a Prod con su sí.

Un pull request cerrado sin unir no cuenta, ni los que van a otras ramas, ni los de escenarios («Escenarios · P01»). Un arreglo lleva el identificador de la pieza que arregla. Los de bots no llevan ninguno; los demás sin pieza salen en el seguimiento como «fuera del plan».
