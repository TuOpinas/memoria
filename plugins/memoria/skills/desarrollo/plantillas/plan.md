---
estado: borrador
actualizado: AAAA-MM-DD
aportacion: "[Lo que este documento aporta, en una frase]"
basado_en: []
---

# Plan

Los títulos de sección y de columna no se cambian: el plugin los lee, y avisa si no encuentra alguno. El estado de las piezas no se escribe aquí: lo calcula el plugin desde GitHub.

Cambiar una fase o el alcance pide una decisión. Añadir, partir o detallar piezas de la fase en curso, no.

## Fases
| Fase | Qué podrá hacer quién | Versión | Listo cuando | Estado |
|---|---|---|---|---|
| F1 · [nombre] | [Una frase] | [versión] | [Algo que se comprueba] | en curso |
| F2 · [nombre] | | | | pendiente |

Estado: `cerrada`, `en curso` (solo una) o `pendiente`.

## Piezas
Las de fases cerradas se quedan. Un identificador no se reutiliza nunca.

| Pieza | Fase | Qué entrega | Hecha cuando |
|---|---|---|---|
| P01 · [nombre] | F1 | [Una frase] | [Lo que se comprueba antes de Prod] |

**Estado de una pieza**, desde los pull requests a la rama principal cuyo título empieza por su identificador seguido de « · », o por los identificadores de un bloque unidos con « + » («P01 + P02 · …»); un arreglo o un revert llevan el de su pieza. Los pull requests a otras ramas son pasos dentro de un bloque y no cuentan. Con varios pull requests, manda el menos avanzado:
- sin pull request unido ni abierto: `pendiente`;
- alguno abierto, o una reversión de la pieza unida después de su último pull request: `en curso`;
- todos unidos: `unida` (en Release, si lo hay);
- todos dentro del último paso a Prod de su repositorio: `entregada` (si «Paso a Prod» deja un release o una etiqueta).

Un pull request cerrado sin unir no cuenta. Los de bots no llevan pieza. Los demás sin pieza, o que nombran un identificador que no está en el plan, salen en el seguimiento como «fuera del plan».

## Cómo avanza
- Se construye por **bloques**: una o varias piezas en un pull request a la rama principal, revisado, unido y desplegado antes de empezar el siguiente. Claude propone cómo se agrupan al estimar; lo normal es una pieza por pull request.
- Quien construye une cada bloque con las pruebas en verde y la revisión de calidad hecha.
- Antes de dar el sí, quien lo da pide el seguimiento, que compara lo unido con el diseño. El sí se da sobre ese seguimiento y cubre todo lo unido hasta el commit que leyó. Quien administra pasa a Prod ese commit, como dice «Paso a Prod».
- Claude se para y pregunta a quien audita en los puntos de control del `CLAUDE.md`.
- Al cumplirse «Listo cuando», quien audita y quien acepta deciden si se sigue, se cambia el plan o se para. Si no coinciden, decide quien acepta.
- Cada mes, quien audita hace la auditoría: comprueba las dos configuraciones y revisa lo que alguien se aprobó a sí mismo.
