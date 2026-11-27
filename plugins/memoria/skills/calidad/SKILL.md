---
name: calidad
description: Revision de calidad a fondo de algo que se esta construyendo - el contenido de un proyecto, un entregable, un desarrollo o plugin, o la carpeta entera (auditoria) - contra su objetivo, con revisores independientes, para encontrar errores, inconsistencias, riesgos, oportunidades y lo que cuesta de mas (tiempo, llamadas, tokens). Usala cuando digan 'revision de calidad', 'revisa a fondo...', 'audita la carpeta', 'que no cuadra en...', 'revisalo todo contra el objetivo', cuando toque la revision periodica de un proyecto, cuando pidan 'revisa los arreglos de...', cuando pregunten 'que tan bien funcionan las revisiones' o 'revisa la efectividad de las revisiones', y siempre antes de publicar una version de un desarrollo o plugin o abrir su pull request, o cuando haya que revisar un cambio con revisores independientes: no se montan revisores a mano.
---

# Revisión de calidad

Revisar a fondo algo que se está construyendo, midiéndolo contra su objetivo y no contra lo que ya tiene. Encuentra lo que está mal, lo que no cuadra entre sí, lo que sobra y lo que se está dejando pasar. No arregla nada por su cuenta: entrega hallazgos comprobados y ordenados, y la sesión del proyecto decide qué se hace. Antes de nada se cargan `convenciones`, con su anexo `escribir.md`, y `estilo`: sus prohibiciones aplican a todo lo que sigue.

No es `revisar`. `revisar` comprueba que un entregable puede publicarse y lo publica. Esta skill busca problemas y oportunidades en algo más grande, y no publica nada.

Cada informe lleva además su medición (paso 7), y cada cierto tiempo esta skill lee las mediciones del área para decir qué rinde cada lente, cada profundidad y cada modelo (paso 8). Así se decide con datos cómo revisar, y no por costumbre.

## Cuándo

«Revisión de calidad de X», «revisa a fondo el plugin», «audita la carpeta», «¿qué no cuadra en este proyecto?», «revísalo todo contra el objetivo». También cuando un proyecto tiene en sus siguientes pasos una revisión periódica y le tocó, y siempre antes de publicar una versión de un desarrollo o un plugin o de abrir su pull request: si el trabajo va hacia publicar, esta skill se invoca sin que nadie la nombre, y cualquier revisión con revisores independientes pasa por ella, nunca por agentes montados a mano. En el plugin `memoria`, `release.sh` no publica sin el informe y su medición.

## Paso 1 · Acordar el alcance

Antes de leer nada, en una sola pregunta (con `AskUserQuestion` si está), lo que no esté ya claro:

1. **Qué se revisa.** El contenido de un proyecto; un entregable concreto; un desarrollo, un repo o un plugin; o la carpeta entera de la organización, que es la auditoría.
2. **Sobre qué tema**, si no es todo: un flujo, una decisión, una parte del código, una versión.
3. **Qué buscar.** Por defecto, las lentes que pide el tamaño (abajo); la persona puede quitar o añadir.
4. **Qué tan a fondo.** Rápida (una lectura y los hallazgos más claros), normal, o a fondo (todo, con revisores independientes por lente y cada hallazgo comprobado).

Si algún proyecto del área tiene `taller/revisiones-de-calidad/efectividad-de-las-revisiones.md` (paso 8), se lee antes de preguntar (hay uno por área), y lo que dice para este tipo de revisión se propone citándolo en una línea. Manda lo que el proyecto que mantiene el método haya decidido; lo demás de ese archivo es una propuesta.

**Por tamaño, por defecto** (1.26.11, decisiones `shared-memory/plugin-memoria#2026-11-17-25` y `-26`, leídas 60 revisiones):

| Qué se revisa | Lentes | Revisores | Contraste |
|---|---|---|---|
| Menos de 300 líneas, de código o de texto | errores, riesgos y objetivo, y eficiencia donde toca (abajo) | tres, o cuatro con eficiencia, normal | no, salvo que toque bloqueos (que dos procesos no escriban a la vez), concurrencia, autenticación o una migración de datos: entonces errores y riesgos también con el otro modelo |
| 300 líneas o más, una versión menor o mayor, un diseño o una auditoría | errores, riesgos y objetivo, y eficiencia donde toca | cinco, o seis con eficiencia, a fondo | sí: errores y riesgos también con el otro modelo |
| Los arreglos de otra revisión, de cualquier tamaño y tipo: esta fila manda sobre las otras dos | errores, riesgos y objetivo, sin eficiencia | tres, normal; con menos, la sesión lo propone y la medición dice por qué (con dos, errores y riesgos, y el de errores hace la pregunta de objetivo; con uno, errores, con las tres); cinco con contraste | solo si toca bloqueos, concurrencia, autenticación o una migración de datos |

Las tres filas son lo que se propone si `efectividad-de-las-revisiones.md` no dice otra cosa para este tipo de revisión; las claves del informe (pasos 6 y 7) no las cambia ese archivo. Un cambio que mezcla arreglos y algo nuevo no es una revisión de arreglos: se revisa entero una vez, por su tamaño.

**Eficiencia, donde toca**, en una primera revisión de cualquier tamaño: un diseño; una versión del plugin, también un parche, porque sus skills son lo que carga cada conversación; un cambio o un material que toca bloqueos, recorre todos los datos o cambia lo que se carga en cada conversación; y cuando el tema es el costo. Si corre se propone al acordar el alcance, y cuando no corre `Lentes:` dice por qué (paso 7). **Inconsistencias** corre solo si la persona la pide; su pregunta la hace el revisor de objetivo (paso 4).

**Una revisión de arreglos** mira lo que se cambió para atender hallazgos numerados de otro informe, y una versión del plugin lleva siempre antes su propia revisión. Sus revisores leen el arreglo, los hallazgos que arregla y el material original que tocan, no solo las líneas cambiadas. Se propone solo cuando la revisión anterior encontró algo que impide el objetivo, o un riesgo que abrió un arreglo («(lo abrió este arreglo)» o «(lo abrió un arreglo anterior)»), y una vez arreglado; no hay tope (decisión `shared-memory/plugin-memoria#2026-11-17-27`). Cómo se escribe su informe está en el anexo `arreglos.md`, junto a este archivo, que se lee antes de guardarlo.

## Paso 2 · Decir los modelos

La revisión rinde según el modelo que la haga, y los modelos de los revisores se dicen siempre, en una línea propia, antes de lanzar. Los dice la línea «Modelos:» de la sección «Desarrollo» del proyecto (tareas `revisa`, `contraste` y `arreglos`), y lo que no dice, o en un proyecto sin esa sección, los valores por defecto de la tabla «Modelos» de la plantilla de la sección (`desarrollo/plantillas/seccion-desarrollo.md`), que es el único sitio donde están (shared-memory/plugin-memoria#2026-11-26-7 y -8): hoy, revisores en Opus 5.5 medio, contraste de errores y riesgos en Sonnet 5.5 alto si construyó Opus, arreglos en Opus 5.5 medio y ningún revisor en Fable. Si `efectividad-de-las-revisiones.md` dice otra cosa para este tipo de revisión, se cita; si la persona pide otro modelo para esta revisión, se usa ese. Los revisores corren con el modelo y el esfuerzo que se les pasan en la herramienta de agentes, sea cual sea el de la conversación, que es la que junta los hallazgos: no hace falta cambiarla. El **contraste**: las lentes de errores y riesgos corren dos veces, una con el modelo de `revisa` y otra con el de `contraste`, sobre lo mismo, donde lo pide el tamaño (paso 1), y salvo en una revisión de arreglos se puede ofrecer aunque el tamaño no lo pida, porque es lo único que deja comparar modelos sobre lo mismo (paso 8). Si el modelo de `contraste` es el mismo que el de `revisa`, o el que construyó, se usa el de la tabla para «si construyó otro» y se dice. Si un modelo no está disponible (sin presupuesto, o la herramienta no deja elegirlo), se dice y se pregunta: esperar, otro modelo, o seguir sin contraste, y la medición lo dice («sin contraste: <motivo>»); nunca se cambia en silencio. Si no se sabe el esfuerzo, el de la línea o el de la tabla; va a la medición tal como corrió. Si el paso 1 se pregunta con `AskUserQuestion`, la línea de modelos va con esa pregunta, y la persona puede cambiarlos ahí.

## Paso 3 · Partir del objetivo

Lo primero que se lee es la vara de medir, no el material:

- **De un proyecto:** `Objetivo` (con su segunda frase: cuándo termina o cada cuánto se revisa) y `Alcance` de su `proyecto.md`, sus decisiones completas y las premisas vigentes de `base/premisas.md`.
- **De un entregable:** su proyecto (lo de arriba) y lo que dice su primera línea que debe resolver.
- **De un desarrollo o un plugin:** su README, el proyecto de la carpeta que lo mantiene y sus decisiones; en un repo, también sus pruebas.
- **De la carpeta entera:** `guia.md`, `base/premisas.md` y el bloque `Proyectos` de cada `area.md`.

Se escribe en tres o cuatro líneas qué tendría que ser cierto si el objetivo se cumple. Contra eso se mide todo lo demás.

**Lo más sencillo que cubre el objetivo** (1.27.1). La vara lleva siempre esta línea: «lo básico para cumplirlo, sin estorbar». Se revisa contra el objetivo, no contra lo que se construyó ni contra una versión perfecta de ello: que algo pueda ser más completo, más fiel o más general no es un hallazgo si el objetivo no lo pide. Cada revisor lo recibe en su encargo y pregunta **qué sobra antes que qué falta**: lo que se puede quitar sin dejar de cumplir el objetivo es un hallazgo, y de los que más pesan.

## Paso 4 · Revisar por lentes

Cinco lentes, cada una con su pregunta; por defecto corren las que pide el tamaño (paso 1):

| Lente | Pregunta |
|---|---|
| Errores | ¿Qué está mal: un dato, una regla, un cálculo, un código que falla, una ruta rota? |
| Inconsistencias | ¿Qué dice una cosa aquí y otra allí: entre documentos, entre decisiones, entre el texto y el código, contra una premisa? |
| Objetivo | ¿Qué falta para cumplir el objetivo, qué se está construyendo que no lo sirve, qué cumple la letra y no la intención? |
| Riesgos | ¿Qué fallaría en manos de otra persona, con otros datos, a otra escala, o en silencio? |
| Eficiencia | ¿Qué cuesta de más: cada operación en tiempo, llamadas, bytes y tokens, qué se carga que la tarea no necesita, cómo crece ese coste con el tamaño de lo revisado, y qué se podría quitar o juntar sin perder nada? |

Hasta la 1.25.7 «lo que sobra» era una sexta lente; la 1.25.8 la junta con eficiencia, porque las dos preguntan qué cuesta de más y la sexta casi nunca encontraba sola algo grave. El revisor de eficiencia busca también lo que sobra aunque no se mida en bytes: dos documentos con la misma verdad, un paso que nadie usa.

La lente de eficiencia se mide, no se estima: bytes que entran al contexto por operación (instrucciones y datos por separado), número de llamadas, tiempo de carga o de repintado de una página, tamaño de lo que se escribe; y se compara con la versión anterior cuando la hay. Pesa sobre todo en un desarrollo o un plugin; en un proyecto es cuánto hay que leer para trabajar en él.

Cuando no corren sus lentes, el revisor de objetivo pregunta también qué dice una cosa aquí y otra allí (si no hay revisor de objetivo, el de errores), y el de riesgos qué crece mal con el tamaño de los datos (1.26.11). Lo que sale de esas preguntas lleva la lente que no corrió entre paréntesis, en minúscula y pegada a la lente que la hizo (`Lens: objective (inconsistencies), risks`); vale para cualquier lente que no corrió y cuya pregunta se hizo (`errors (objective)` en una ronda de dos), y una lente que corrió no va nunca entre paréntesis; su encargo lo dice, y al juntar hallazgos (paso 5) la marca se conserva: es lo que deja medir en el paso 8 si esas preguntas se siguen haciendo.

En la auditoría de la carpeta, además (si no corre eficiencia, lo busca el revisor de objetivo): lo duplicado (dos proyectos que son el mismo, dos documentos con la misma verdad), lo mal colocado (un proyecto que es un área, material de fuera fuera de `fuentes/`), lo que el contrato no permite, y lo que `verificar.sh` ya detecta, que se corre primero.

**A fondo, con revisores independientes.** Se lanza un revisor por lente con la herramienta de agentes, todos a la vez, cada uno con el objetivo del paso 3, el material, solo su lente y las reglas de lectura del párrafo siguiente. Ninguno ha visto el trabajo mientras se hacía, para que nadie se califique a sí mismo. Si la herramienta de agentes no está, se hace una pasada por lente y se dice que la revisión no fue independiente. De cada revisor se apunta su modelo y lo que gastó, si la herramienta lo dice (los tokens de su línea de uso): van a la medición. En un contraste, cada revisor lleva el nombre de su lente y de su modelo.

Lo que se lee sigue las reglas de siempre, y cada revisor las recibe con su encargo: de otras áreas, solo su superficie pública; lo restringido sin acceso se nombra y se salta; el cuerpo de `sesiones.md`, `taller/` y `fuentes/` de otras áreas no se lee.

## Paso 5 · Comprobar cada hallazgo

Un hallazgo entra solo si se puede señalar: la ruta, la línea, el identificador de la decisión o la prueba que falla. Se vuelve a mirar la fuente antes de darlo por bueno. Lo que no se puede comprobar se descarta o se da aparte como duda, en su sección «Dudas», sin línea `Lens:`, diciendo qué faltaría para confirmarlo. Dos revisores que dicen lo mismo son un solo hallazgo, y su línea `Lens:` nombra a todos los que lo encontraron; en un contraste, `Modelo:` dice «los dos» o el nombre corto del único que lo encontró. Si el hallazgo está en algo que ya revisó otro informe, se añade además su línea a «Lo que se escapó» de ese informe (paso 7, «en otra revisión»). Es lo que deja medir qué aporta cada lente y cada modelo. **El peso lo vuelve a juzgar esta sesión** contra la vara, hallazgo por hallazgo, lo diga el revisor que lo diga: Sonnet rebaja el peso (no dio como «impide» bloqueos que Opus y Fable sí, shared-memory/plugin-memoria#2026-11-26-8), y que nadie diga «impide» no basta para saltarse la revisión de arreglos.

## Paso 6 · Ordenar y entregar

Se ordenan por lo que pesan contra el objetivo, no por lente: primero lo que impide cumplirlo, después lo que lo pone en riesgo, después lo que lo mejora. Cada hallazgo comprobado, también las mejoras, en una entrada `###` numerada con estas líneas y estas palabras, que son las que lee la medición; ninguno en una lista ni en una tabla. `Lens:` nombra las lentes en inglés y en minúscula (errors, inconsistencies, objective, risks, efficiency: las iniciales E, I, O, R y F de la medición), en cualquier idioma del informe, con un paréntesis detrás si hace falta una aclaración; `Pesa:` es «impide cumplir el objetivo», «pone en riesgo el objetivo» o «lo mejora». `Modelo:` solo va en un contraste. Son claves que no se traducen:

```markdown
### 1. El cierre de sesión no pone al día el tablero si la cuenta tiene dos
Lens: errors, risks · Pesa: impide cumplir el objetivo · Modelo: los dos (solo en un contraste)
Dónde: plugins/memoria/skills/sesion/cerrar.md, paso 11
Qué pasa: … (con la evidencia)
Propuesta: … (qué cambiar, sin cambiarlo)
```

**Dónde se guarda.** En `taller/revisiones-de-calidad/` del proyecto que se revisó (o del proyecto que mantiene lo revisado), como `revision-de-calidad-<tema>.md` en `borrador`, con `basado_en` de lo que se leyó: cada revisión es un informe distinto, así que el número de la versión revisada va en el nombre (contrato, sección 6), y juntas en su subcarpeta no llenan el taller (1.23). Las que estén sueltas en `taller/` de antes se mueven ahí la primera vez que se guarda una nueva, sin cambiarles el nombre. Si ya existe uno del mismo tema, se reescribe su cuerpo (una revisión de arreglos no es el mismo tema: va en su propio informe, paso 1): la revisión anterior queda en el historial de la carpeta y lo que importaba de ella ya entró al proyecto. Sus secciones `Medición` y `Lo que se escapó` se conservan, y la medición nueva va encima de la anterior: una por corrida. La auditoría de la carpeta se guarda en el proyecto que su responsable de contexto elija. Antes de guardarlo se comprueba con `comprobar_informe.py`, junto a este archivo (`python3 <directorio de esta skill>/comprobar_informe.py <informe>`, en el contenedor sobre una copia si la consola no tiene el plugin): si dice algo, se arregla antes de guardar. Es lo mismo que mira `release.sh` antes de publicar una versión. El informe se guarda con su medición (paso 7) antes de responder.

**Ante cada hallazgo, tres salidas, en este orden** (1.27.1): quitar lo que lo causa, si el objetivo se cumple sin ello; aceptarlo por escrito, con su porqué, si no lo impide; y solo después arreglarlo. La propuesta de cada hallazgo dice cuál, y un arreglo que añade código o texto dice cuánto. **Se para y se pregunta a la persona antes de arreglar nada** cuando hay más de dos hallazgos que impiden el objetivo, cuando arreglar lo propuesto haría crecer lo revisado más de la mitad, o cuando una ronda de arreglos encuentra más que la anterior: eso dice que la pieza está mal planteada, y lo que toca es replantearla o quitarla, no otra ronda.

**Qué respondo.** Cuántos hallazgos hay por peso, los tres o cuatro primeros en una línea cada uno, dónde quedó el informe y la frase para trabajarlos en una sesión; si alguno impide el objetivo, o en una revisión de arreglos es un riesgo que abrió un arreglo, que al arreglarlo toca su revisión de arreglos («revisa los arreglos de <informe>»). Si la revisión es periódica, se propone la fecha de la siguiente para que la sesión la ponga en los siguientes pasos. Si con este informe hay diez mediciones en el área, sin contar las de arreglos («, arreglos» en `Tipo:`, o `-arreglos-`, `-fixes` o `-round-` en el nombre), fechadas después del `actualizado` de `efectividad-de-las-revisiones.md` (o diez en total, si aún no existe), o la revisión usó un modelo que ninguna medición tenía, se propone leer la efectividad (paso 8). Se cuentan con una búsqueda de líneas (`grep` de `^Fecha:`, `^Tipo:` y `^Modelo:` en los informes del área), sin abrirlos, como se buscan los «Afecta a:» al abrir sesión; la misma búsqueda dice en el paso 2 si un modelo ya tiene revisiones medidas.

## Paso 7 · Medir la corrida

Toda revisión, también la rápida y la que no fue independiente, termina su informe con una sección `## Medición`, siempre con estas líneas y en este orden, para que se puedan sumar (en un archivo vivo del taller, no en un registro: el contrato no abre registros en el taller):

```markdown
## Medición
Fecha: 2026-11-08
Tipo: componente · Tamaño: 219 líneas cambiadas
Profundidad: normal · Revisores: 5 · Lentes: E, R, O (sin F: toca autenticación, no bloqueos, datos ni lo que se carga)
Modelo: Fable 5.2 (E, R, O) · Opus 5.5 (E, R) · contraste
Razonamiento: medio
Construyó: Opus 5.5
Hallazgos: 17 · impiden 2 · riesgo 10 · mejoran 5
Arreglados: 15 · impiden 2
Tokens: 693k · Fable 5.2 360k (E, R 240k) · Opus 5.5 333k
```

- **Fecha**: la del día en la zona horaria de la organización (la línea HOY de la apertura), no la del reloj de la consola.
- **Tipo**: versión, parche, componente, diseño, documento o auditoría; en una revisión de arreglos, detrás «, arreglos <n> de <informe>» (anexo `arreglos.md`). **Tamaño**: siempre en líneas, con su unidad: las cambiadas, o las leídas si no hay cambio. **Revisores**, con el motivo entre paréntesis si una revisión de arreglos lleva menos de tres.
- **Lentes**, por sus iniciales: E errores, I inconsistencias, O objetivo, R riesgos, F eficiencia; si eficiencia no corre en una primera revisión, el porqué entre paréntesis (paso 1).
- **Razonamiento**: el nivel con el que corrieron los revisores: «máximo», «extra», «alto», «medio» o «bajo», uno por modelo si fueron distintos («Fable 5.2 medio · Opus 5.5 alto»), o «no consta» si nadie lo sabe tras preguntarlo (paso 2).
- **Modelo**: el de cada revisor como se lanzó, con su nombre corto (familia y versión: «Opus 5.5», «Fable 5.2»), y las lentes que corrió con cada uno; «contraste» si lo hubo. **Construyó**: el modelo con el que se hizo lo revisado; «no consta» si no se sabe.
- **Hallazgos** comprobados (las dudas no cuentan), por peso. Lo que encontró cada lente y cada modelo, y quién lo encontró solo, no se apunta aquí: sale de las líneas `Lens:`, `Pesa:` y `Modelo:` de cada hallazgo.
- **Arreglados**: los que se arreglaron antes de publicar o de abrir el pull request, y si alguno impide el objetivo, detrás cuántos de esos («Arreglados: 15 · impiden 2»); uno que se decide no arreglar cuenta si la decisión está registrada. Al guardar el informe es 0; la sesión que los arregla pone al día esta línea, porque el informe es un archivo vivo, y con ella su `actualizado`, como con cada línea que se añade a «Lo que se escapó».
- **Tokens**: la suma de los revisores en miles («693k»), si la herramienta la dio, y en un contraste también la de cada modelo, con la de sus revisores de errores y riesgos entre paréntesis si corrió más lentes, que es lo que se compara; si no, «no consta».

Nada se adivina: lo que no se sabe es «no consta».

**Lo que se escapó.** Cuando aparece después un fallo en algo que se revisó (en el uso real, en otra revisión, en una prueba en vivo o en los evals), se añade al final del informe de esa revisión una sección `## Lo que se escapó`, con una línea por fallo:

```markdown
- 2026-11-12 · uso real · a su alcance · lo habría visto: risks · impide · El cierre falló con Python 3.9 en un Mac.
```

Con la fecha (la de la organización, como en la medición), cómo apareció, la clase (**a su alcance**: estaba en lo revisado; **quedó como duda**; **fuera de lo revisado**; **sin decidir**: nadie había decidido cómo debía ser; **premisa errónea**: la vara del paso 3 estaba mal; **entorno**: una herramienta o un ajuste fuera de lo revisado; **antes de publicar**: lo pararon los evals o una prueba, no la revisión), la lente que lo habría visto, con su nombre de `Lens:` («ninguna» si ninguna podía), lo que pesa, con las palabras de `Pesa:` («impide», «riesgo» o «mejora»), y qué pasó. La escribe la sesión que trabaja en el proyecto del informe, y su cierre la propone cuando en la sesión apareció un fallo (`sesion`, `cerrar.md`, paso 4b), también cuando el fallo apareció en otro proyecto. Si el fallo aparece en otro proyecto, otra área u otra raíz, esa sesión no escribe en el informe: le prepara la línea a la persona para que se la pase al responsable de ese proyecto, y de otra raíz solo pasa lo que la persona confirme (contrato, «Independencia entre raíces»).

## Paso 8 · Leer la efectividad

Cuando el paso 6 lo propone, cuando cambia el modelo que se usa o cuando alguien lo pide («¿qué tan bien funcionan las revisiones?»), se lee el anexo `efectividad.md`, junto a este archivo, y se sigue: lee las mediciones del área y reescribe `taller/revisiones-de-calidad/efectividad-de-las-revisiones.md`, uno por área.

## Lo que nunca hago

Además de las prohibiciones de `convenciones` (anexo `escribir.md`):

- Arreglar lo que encuentro. Se propone; lo cambia la sesión del proyecto.
- Registrar decisiones. Si un hallazgo pide decidir, se dice y la sesión lo registra con la confirmación de su responsable: en cuanto sale, en cita (`sesion`, `cerrar.md`, «Al proponer», 1.26.9), sin esperar al final de la revisión.
- Dar un hallazgo sin evidencia, o una opinión como si fuera un hallazgo.
- Empezar sin acordar el alcance, o lanzar revisores sin haber dicho sus modelos y su esfuerzo.
- Guardar un informe sin su medición.
- Medir contra lo que ya existe, o contra su versión perfecta, en lugar de contra el objetivo.
- Proponer más maquinaria donde quitar algo cumple el objetivo.

## Ejemplo

**Usuario:** revisión de calidad del plugin

**Respuesta:**

> Antes de empezar, tres cosas: ¿reviso el plugin entero o una parte (el tablero, las skills, los scripts)? ¿Con las lentes por defecto (errores, riesgos y objetivo, y eficiencia, porque el plugin es lo que carga cada conversación)? ¿Rápida, normal o a fondo?

**Usuario:** entero, las de siempre, a fondo

**Respuesta:**

> Corren con los modelos por defecto, porque el proyecto no tiene línea «Modelos:»: revisa Opus 5.5 medio y, como es una versión, contraste de errores y riesgos en Sonnet 5.5 alto. No hace falta cambiar el modelo de esta conversación. Si quieres otro para esta revisión, dímelo; si no, lanzo los seis revisores.
