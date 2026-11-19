---
name: desarrollo
description: El kit de desarrollo de un proyecto que construye software (con la seccion «Desarrollo» en su proyecto.md) - el seguimiento desde GitHub, los escenarios de aceptacion de cada pieza y la verificacion sobre Release antes del si. Usala cuando digan 'seguimiento', 'haz el seguimiento de...', '¿como va el desarrollo?', '¿en que estado esta la pieza...?', 'escenarios de...', 'verifica la pieza...', o antes de dar el si para pasar algo a Prod.
---

# Desarrollo

El kit garantiza que lo que llega a Prod pasó los escenarios que aprobó quien acepta, y que cada cambio se puede rastrear hasta una pieza del plan (tecnologia/metodologia-desarrollo#2026-11-19-3). A quien no es técnico no le añade más pasos que aprobar los escenarios y leer el reporte: todo lo que se le dice es breve y en llano, sin códigos de regla.

Un proyecto de desarrollo es el que tiene la sección `## Desarrollo` en su `proyecto.md` (`convenciones`, `escribir.md`, sección 3). Sin ella, esta skill no hace nada salvo ofrecerla: en un proyecto que ya existe, se enseña en cita la sección rellena con lo que se sepa (`plantillas/seccion-desarrollo.md`, `por crear` en lo que falte) y, con el sí, la escribe `cerrar.py` con un solo reemplazo de `proyecto`, que pone la sección detrás de la última línea de `Quién participa`. La sesión del proyecto se abre antes, como siempre (skill `sesion`), y antes de escribir en la carpeta se carga `escribir.md`. Las plantillas están en `plantillas/`, junto a este archivo. Esta skill no tiene scripts: lee y juzga Claude.

## El seguimiento

Lo pide cualquiera que lea el proyecto, y quien da el sí lo pide antes de darlo (#2026-11-18-9). Nunca se hace al abrir ni sin que nadie lo pida.

1. **Lo de la memoria**: la sección, el plan, el diseño y la última entrada del seguimiento, por las rutas de la sección.
2. **GitHub**, de cada repositorio de «Repositorios:», con el conector de GitHub si la sesión lo tiene o con `gh` en el contenedor. **Desde cuándo**: desde la fecha de la entrada anterior; en el primer seguimiento, desde el «Aprobó:» más antiguo del plan, y si no hay ninguno, las dos últimas semanas, y la entrada lo dice. Se leen la rama principal y su último commit (`gh api repos/<repo>/commits/HEAD`), los pull requests a esa rama abiertos o unidos desde esa fecha (`gh pr list -R <repo> --base <rama> --state all --search "updated:>=<fecha>" --limit 200 --json number,title,state,mergedAt,mergeCommit,author`) y los que nombran una pieza del plan que aún no esté `entregada` (`--search "<pieza> in:title"`), y, con «Paso a Prod: release de GitHub», los releases con su texto en una llamada (`gh api repos/<repo>/releases`). Si una lista llega al límite, se dice que puede faltar algo; nada se da por leído si no se leyó. **Sin GitHub** (sin conector, sin `gh` o sin acceso al repositorio, y basta el primer intento que falle por acceso para no probar más con ese repositorio): se dice en una línea, se da lo que dice la memoria (las piezas del plan, sin estado) y no se escribe la entrada, porque su fecha diría que se comparó lo unido.
3. **El estado de cada pieza**, con la regla del plan («Cómo se sabe en qué estado está cada pieza»): solo cuentan los pull requests a la rama principal; uno de bloque («P01 + P02 · …») cuenta para cada pieza que nombra, y los de escenarios («Escenarios · P01») y del kit («Kit · ») no cuentan para el estado. Una pieza sale `entregada` solo si un paso a Prod con su sí cubre el commit de su unión (`mergeCommit`): con «release de GitHub», un release con la línea «Aprobó:» cuyo commit contiene ese (`gh api repos/<repo>/compare/<etiqueta>...<commit>` da `behind` o `identical`), nunca por fechas; con otra forma de «Paso a Prod», solo si quien administra dejó una etiqueta o un release en el commit desplegado, y si no, la entrada dice que el sí no se pudo comprobar.
4. **Lo que lo unido añade y el diseño no tiene**: de cada pull request unido desde esa fecha, primero sus archivos (`gh pr diff <n> --name-only`), y entero solo el diff de lo que toca datos, esquemas, componentes o nombres del producto, leído contra «Datos», «Componentes» y «Conceptos» del diseño. Los que tocaron la carpeta de pruebas de aceptación, el workflow `pruebas-aceptacion.yml` o el `CLAUDE.md` se nombran todos, con la fecha de «Aprobó:» de su pieza. Una entidad, un componente o un concepto nuevos, también con otro nombre o como sinónimo, se nombran con su pull request. Es juicio: se dice lo que se vio y en qué archivo, sin darlo por error.
5. **La entrada**, corta y en llano, en el orden de `plantillas/seccion-desarrollo.md`, arriba del archivo de «Seguimiento:», sin tocar las anteriores. Si la línea dice `por crear`, se crea `<proyecto>/entregables/seguimiento.md`, `vigente` (escribir.md, prohibición 1), y una sola llamada a `cerrar.py`, sin entrada de sesión (`sesion`, `cerrar.md`), pone la ruta en `proyecto.md` con un reemplazo de `proyecto` y la línea del seguimiento en `area.md` con `area` (la línea del proyecto tal como está y, en `entregables`, cada uno de los que ya lista como `{"archivo": …}` más `{"archivo": "seguimiento.md"}`). Si la cuenta no escribe en el proyecto, la entrada va solo en la conversación, y se dice que la guarde quien construye o quien audita.
6. **Responder** con la entrada y, si algo está fuera del plan o del diseño, una línea con a quién le toca: a quien construye; un paso a Prod sin sí, a quien audita.

## Los escenarios de una pieza

Antes de construirla. Claude propone en el plan («Hecha cuando») los escenarios Dado/Cuando/Entonces de la pieza, con sus casos de error, y quien acepta los aprueba: su nombre y la fecha van en «Aprobó:». Un escenario aprobado no se cambia sin otra aprobación.

Después, **una sesión aparte**, que solo ve el plan, el diseño y el `CLAUDE.md` del repositorio, y no el código de la aplicación, convierte los escenarios aprobados en pruebas que fallan, con el identificador de la pieza en su nombre, en la carpeta de «Pruebas de aceptación» del `CLAUDE.md` y en su propio pull request, titulado «Escenarios · P01», que no toca nada más. Esas pruebas no van en la suite obligatoria de «Cómo se prueba»: fallan hasta que la pieza se construye, y el pull request de la pieza enseña la salida de las suyas. Un subagente de la misma conversación no vale: comparte lo que ya se leyó. Lo que hace esta sesión es preparar el encargo para esa otra, en un mensaje que se copia tal cual. El pull request de la pieza no toca esa carpeta: el workflow `plantillas/pruebas-aceptacion.yml` falla si un mismo pull request cambia las pruebas de aceptación y otra cosa.

## La verificación sobre Release

Antes del sí de una pieza unida. La hace **una sesión de contexto limpio**, de preferencia con Fable 5.2 (el otro modelo que el que construyó), a la que se le da un encargo que se copia tal cual:

- Su trabajo es encontrar por qué la pieza no cumple sus escenarios. Recorre Release, nunca Prod, con una cuenta de prueba que da quien administra. Sin entorno de Release, recorre la aplicación levantada desde el commit unido (una vista previa o en local) y el reporte dice dónde.
- Revisa el diff completo de los pull requests de la pieza, no su resumen, y que lo que hace sea real y no de fachada.
- Entrega un reporte criterio por criterio: cada escenario, pasa o falla, con su evidencia (una captura, una respuesta de la API, un log). **Un criterio sin evidencia cuenta como fallado.**

El reporte se guarda como nota del proyecto, `taller/verificacion-<pieza>-AAAA-MM-DD.md`, con su ronda («Ronda: 1»), el modelo y cuánto costó si se sabe, y la siguiente entrada del seguimiento lo cita. Con algo fallado, la pieza vuelve a quien construye; tras dos o tres rondas sin pasar, se para y se le pregunta a quien audita. Si la sesión no pudo abrir la aplicación, el reporte dice «no se pudo verificar» y por qué, va a quien audita y no cuenta como ronda. Quien da el sí lee el reporte junto con el seguimiento.

## Lo que nunca hago

- Leer GitHub sin que nadie lo pida, o escribir en GitHub: ni comentarios, ni releases, ni cambios de configuración.
- Dar un estado de pieza sin haber leído sus pull requests, o una pieza por entregada sin un paso a Prod con su sí.
- Cambiar un escenario aprobado, o las pruebas de aceptación dentro del pull request de su pieza.
- Copiar las piezas a `Siguientes pasos`: en un proyecto de desarrollo, las tareas del código son las piezas del plan.
