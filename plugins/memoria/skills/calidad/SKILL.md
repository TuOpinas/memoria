---
name: calidad
description: Revision de calidad a fondo de algo que se esta construyendo - el contenido de un proyecto, un entregable, un desarrollo o plugin, o la carpeta entera (auditoria) - contra su objetivo, con revisores independientes, para encontrar errores, inconsistencias, riesgos, oportunidades y lo que cuesta de mas (tiempo, llamadas, tokens). Usala cuando digan 'revision de calidad', 'revisa a fondo...', 'audita la carpeta', 'que no cuadra en...', 'revisalo todo contra el objetivo' o cuando toque la revision periodica de un proyecto.
---

# Revisión de calidad

Revisar a fondo algo que se está construyendo, midiéndolo contra su objetivo y no contra lo que ya tiene. Encuentra lo que está mal, lo que no cuadra entre sí, lo que sobra y lo que se está dejando pasar. No arregla nada por su cuenta: entrega hallazgos comprobados y ordenados, y la sesión del proyecto decide qué se hace. Antes de nada se cargan `convenciones` y `estilo`: sus prohibiciones aplican a todo lo que sigue.

No es `revisar`. `revisar` comprueba que un entregable puede publicarse y lo publica. Esta skill busca problemas y oportunidades en algo más grande, y no publica nada.

## Cuándo

«Revisión de calidad de X», «revisa a fondo el plugin», «audita la carpeta», «¿qué no cuadra en este proyecto?», «revísalo todo contra el objetivo». También cuando un proyecto tiene en sus siguientes pasos una revisión periódica y le tocó.

## Paso 1 · Acordar el alcance

Antes de leer nada, en una sola pregunta (con `AskUserQuestion` si está), lo que no esté ya claro:

1. **Qué se revisa.** El contenido de un proyecto; un entregable concreto; un desarrollo, un repo o un plugin; o la carpeta entera de la organización, que es la auditoría.
2. **Sobre qué tema**, si no es todo: un flujo, una decisión, una parte del código, una versión.
3. **Qué buscar.** Por defecto, las seis lentes de abajo; la persona puede quitar o añadir.
4. **Qué tan a fondo.** Rápida (una lectura y los hallazgos más claros), normal, o a fondo (todo, con revisores independientes por lente y cada hallazgo comprobado).

## Paso 2 · Recomendar el modelo

La revisión rinde según el modelo que la haga, y la recomendación se hace siempre, también cuando la respuesta es quedarse como está. En una línea propia, no escondida en otra pregunta: el modelo con el que corre la conversación, si se sabe, y lo que conviene para el alcance acordado (para «a fondo», el más capaz que la persona tenga y el mayor nivel de razonamiento; para «rápida», el que esté usando). Si coinciden, se dice que conviene seguir con el actual; si no, que conviene cambiar. Claude no puede cambiar su propio modelo: lo cambia la persona en el selector de la conversación. Se pregunta con las dos opciones (cambiar o seguir), la recomendada primero, y no se empieza hasta que conteste. Si el paso 1 se pregunta con `AskUserQuestion`, esta va como una pregunta más de la misma llamada.

## Paso 3 · Partir del objetivo

Lo primero que se lee es la vara de medir, no el material:

- **De un proyecto:** `Objetivo`, `Terminado significa` y `Alcance` de su `proyecto.md`, sus decisiones completas y las premisas vigentes de `base/premisas.md`.
- **De un entregable:** su proyecto (lo de arriba) y lo que dice su primera línea que debe resolver.
- **De un desarrollo o un plugin:** su README, el proyecto de la carpeta que lo mantiene y sus decisiones; en un repo, también sus pruebas.
- **De la carpeta entera:** `guia.md`, `base/premisas.md` y el bloque `Proyectos` de cada `area.md`.

Se escribe en tres o cuatro líneas qué tendría que ser cierto si el objetivo se cumple. Contra eso se mide todo lo demás.

## Paso 4 · Revisar por lentes

Seis lentes, cada una con su pregunta:

| Lente | Pregunta |
|---|---|
| Errores | ¿Qué está mal: un dato, una regla, un cálculo, un código que falla, una ruta rota? |
| Inconsistencias | ¿Qué dice una cosa aquí y otra allí: entre documentos, entre decisiones, entre el texto y el código, contra una premisa? |
| Objetivo | ¿Qué falta para cumplir el objetivo, qué se está construyendo que no lo sirve, qué cumple la letra y no la intención? |
| Riesgos | ¿Qué fallaría en manos de otra persona, con otros datos, a otra escala, o en silencio? |
| Lo que sobra | ¿Qué se podría quitar o juntar sin perder nada? |
| Eficiencia | ¿Qué cuesta cada operación en tiempo, llamadas, bytes y tokens; qué se carga que la tarea no necesita; cómo crece ese coste con el tamaño de lo revisado? |

La lente de eficiencia se mide, no se estima: bytes que entran al contexto por operación (instrucciones y datos por separado), número de llamadas, tiempo de carga o de repintado de una página, tamaño de lo que se escribe; y se compara con la versión anterior cuando la hay. Pesa sobre todo en un desarrollo o un plugin; en un proyecto es cuánto hay que leer para trabajar en él.

En la auditoría de la carpeta, además: lo duplicado (dos proyectos que son el mismo, dos documentos con la misma verdad), lo mal colocado (un proyecto que es un área, material de fuera fuera de `fuentes/`), lo que el contrato no permite, y lo que `verificar.sh` ya detecta, que se corre primero.

**A fondo, con revisores independientes.** Se lanza un revisor por lente con la herramienta de agentes, todos a la vez, cada uno con el objetivo del paso 3, el material, solo su lente y las reglas de lectura del párrafo siguiente. Ninguno ha visto el trabajo mientras se hacía, para que nadie se califique a sí mismo. Si la herramienta de agentes no está, se hace una pasada por lente y se dice que la revisión no fue independiente.

Lo que se lee sigue las reglas de siempre, y cada revisor las recibe con su encargo: de otras áreas, solo su superficie pública; lo restringido sin acceso se nombra y se salta; el cuerpo de `sesiones.md`, `taller/` y `fuentes/` no se leen.

## Paso 5 · Comprobar cada hallazgo

Un hallazgo entra solo si se puede señalar: la ruta, la línea, el identificador de la decisión o la prueba que falla. Se vuelve a mirar la fuente antes de darlo por bueno. Lo que no se puede comprobar se descarta o se da aparte como duda, diciendo qué faltaría para confirmarlo. Dos revisores que dicen lo mismo son un solo hallazgo.

## Paso 6 · Ordenar y entregar

Se ordenan por lo que pesan contra el objetivo, no por lente: primero lo que impide cumplirlo, después lo que lo pone en riesgo, después lo que lo mejora. Cada hallazgo, en una entrada:

```markdown
### 1. El cierre de sesión no pone al día el tablero si la cuenta tiene dos
Lente: errores · Pesa: impide cumplir el objetivo
Dónde: plugins/memoria/skills/sesion/cerrar.md, paso 11
Qué pasa: … (con la evidencia)
Propuesta: … (qué cambiar, sin cambiarlo)
```

**Dónde se guarda.** En el `taller/` del proyecto que se revisó (o del proyecto que mantiene lo revisado), como `revision-de-calidad-<tema>.md` en `borrador`, con `basado_en` de lo que se leyó. Si ya existe uno del mismo tema, se reescribe: la revisión anterior queda en el historial de la carpeta y lo que importaba de ella ya entró al proyecto. La auditoría de la carpeta se guarda en el proyecto que su responsable de contexto elija.

**Qué respondo.** Cuántos hallazgos hay por peso, los tres o cuatro primeros en una línea cada uno, dónde quedó el informe y la frase para trabajarlos en una sesión. Si la revisión es periódica, se propone la fecha de la siguiente para que la sesión la ponga en los siguientes pasos.

## Lo que nunca hago

Además de las prohibiciones de `convenciones` (anexo `escribir.md`):

- Arreglar lo que encuentro. Se propone; lo cambia la sesión del proyecto.
- Registrar decisiones. Si un hallazgo pide decidir, se dice y la sesión lo registra con la confirmación de su dueño.
- Dar un hallazgo sin evidencia, o una opinión como si fuera un hallazgo.
- Empezar sin acordar el alcance, o una revisión a fondo sin haber recomendado el modelo.
- Medir contra lo que ya existe en lugar de contra el objetivo.

## Ejemplo

**Usuario:** revisión de calidad del plugin

**Respuesta:**

> Antes de empezar, tres cosas: ¿reviso el plugin entero o una parte (el tablero, las skills, los scripts)? ¿Con las seis lentes (errores, inconsistencias, objetivo, riesgos, lo que sobra, eficiencia)? ¿Rápida, normal o a fondo?

**Usuario:** entero, todas, a fondo

**Respuesta:**

> Para una revisión a fondo del plugin entero conviene el modelo más capaz que tengas y el razonamiento al máximo; cámbialo en el selector de la conversación y dime cuando esté. Si prefieres seguir con este, sigo.
