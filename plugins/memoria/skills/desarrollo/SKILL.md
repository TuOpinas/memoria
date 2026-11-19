---
name: desarrollo
description: El kit de desarrollo de un proyecto que construye software (con la seccion «Desarrollo» en su proyecto.md) - el seguimiento desde GitHub, los escenarios de aceptacion de cada pieza y la verificacion sobre Release antes del si. Usala cuando digan 'seguimiento', 'haz el seguimiento de...', '¿como va el desarrollo?', '¿en que estado esta la pieza...?', 'escenarios de...', 'verifica la pieza...', o antes de dar el si para pasar algo a Prod.
---

# Desarrollo

El kit garantiza que lo que llega a Prod pasó los escenarios que aprobó quien acepta, y que cada cambio se puede rastrear hasta una pieza del plan (tecnologia/metodologia-desarrollo#2026-11-19-3). A quien no es técnico no le añade más pasos que aprobar los escenarios y leer el reporte: todo lo que se le dice es breve y en llano, sin códigos de regla.

Un proyecto de desarrollo es el que tiene la sección `## Desarrollo` en su `proyecto.md` (`convenciones`, `escribir.md`, sección 3). Sin ella, esta skill no hace nada: se dice en una línea y se ofrece `nuevo`, que la escribe. La sesión del proyecto se abre antes, como siempre (skill `sesion`), y antes de escribir en la carpeta se carga `escribir.md`. Las plantillas están en `plantillas/`, junto a este archivo. Esta skill no tiene scripts: lee y juzga Claude.

## El seguimiento

Lo pide cualquiera que lea el proyecto, y quien da el sí lo pide antes de darlo (#2026-11-18-9). Nunca se hace al abrir ni sin que nadie lo pida.

1. **Lo de la memoria**: la sección, el plan, el diseño y la última entrada del seguimiento, por las rutas de la sección.
2. **GitHub**, de cada repositorio de «Repositorios:», con el conector de GitHub si la sesión lo tiene o con `gh` en el contenedor: la rama principal (`gh repo view <repo> --json defaultBranchRef`), sus pull requests (`gh pr list -R <repo> --base <rama> --state all --limit 200 --json number,title,state,mergedAt,author,url`), el último commit de la rama, y, con «Paso a Prod: release de GitHub», los releases (`gh release list -R <repo>` y `gh release view`). Si una lista llega al límite, se dice que puede faltar algo; nada se da por leído si no se leyó. **Sin GitHub** (sin conector, sin `gh` o sin acceso al repositorio): se dice en una línea, se da lo que dice la memoria (las piezas del plan, sin estado) y no se escribe la entrada, porque su fecha diría que se comparó lo unido.
3. **El estado de cada pieza**, con la regla del plan («Cómo se sabe en qué estado está cada pieza»): solo cuentan los pull requests a la rama principal; uno de bloque («P01 + P02 · …») cuenta para cada pieza que nombra, y los de escenarios («Escenarios · P01») no cuentan ni salen fuera del plan. Una pieza solo sale `entregada` si un paso a Prod con su sí la cubre.
4. **Lo que lo unido añade y el diseño no tiene**: el diff de cada pull request unido desde el seguimiento anterior (`gh pr diff`), leído contra «Datos», «Componentes» y «Conceptos» del diseño. Una entidad, un componente o un concepto nuevos, también con otro nombre o como sinónimo, se nombran con su pull request. Es juicio: se dice lo que se vio y en qué archivo, sin darlo por error.
5. **La entrada**, corta y en llano, en el orden de `plantillas/seccion-desarrollo.md`, arriba del archivo de «Seguimiento:», sin tocar las anteriores. Si la línea dice `por crear`, se crea `<proyecto>/entregables/seguimiento.md`, `vigente`, y la ruta se pone en `proyecto.md` con `cerrar.py` y solo `reemplazos` de `proyecto` (`sesion`, `cerrar.md`). Si la cuenta no escribe en el proyecto, la entrada va solo en la conversación, y se dice que la guarde quien construye o quien audita.
6. **Responder** con la entrada y, si algo está fuera del plan o del diseño, una línea con a quién le toca: a quien construye; un paso a Prod sin sí, a quien audita.

## Los escenarios de una pieza

Antes de construirla. Claude propone en el plan («Hecha cuando») los escenarios Dado/Cuando/Entonces de la pieza, con sus casos de error, y quien acepta los aprueba: su nombre y la fecha van en «Aprobó:». Un escenario aprobado no se cambia sin otra aprobación.

Después, **una sesión aparte**, que solo ve el plan, el diseño y el `CLAUDE.md` del repositorio, y no el código de la aplicación, convierte los escenarios aprobados en pruebas que fallan, en la carpeta de «Pruebas de aceptación» del `CLAUDE.md` y en su propio pull request, titulado «Escenarios · P01», que no toca nada más. Un subagente de la misma conversación no vale: comparte lo que ya se leyó. Lo que hace esta sesión es preparar el encargo para esa otra, en un mensaje que se copia tal cual. El pull request de la pieza no toca esa carpeta: el workflow `plantillas/pruebas-aceptacion.yml` falla si un mismo pull request cambia las pruebas de aceptación y otra cosa.

## La verificación sobre Release

Antes del sí de una pieza unida, en piezas con reglas de negocio o con un punto de control; en las demás bastan la revisión de calidad y CI. La hace **una sesión de contexto limpio**, de preferencia con Fable 5.2 (el otro modelo que el que construyó), a la que se le da un encargo que se copia tal cual:

- Su trabajo es encontrar por qué la pieza no cumple sus escenarios. Recorre Release, nunca Prod, con una cuenta de prueba.
- Revisa el diff completo de los pull requests de la pieza, no su resumen, y que lo que hace sea real y no de fachada.
- Entrega un reporte criterio por criterio: cada escenario, pasa o falla, con su evidencia (una captura, una respuesta de la API, un log). **Un criterio sin evidencia cuenta como fallado.**

El reporte se guarda como nota del proyecto, `taller/verificacion-<pieza>-AAAA-MM-DD.md`, con su ronda («Ronda: 1»), el modelo y cuánto costó si se sabe, y la siguiente entrada del seguimiento lo cita. Con algo fallado, la pieza vuelve a quien construye; tras dos o tres rondas sin pasar, se para y se le pregunta a quien audita. Quien da el sí lee el reporte junto con el seguimiento.

## Lo que nunca hago

- Leer GitHub sin que nadie lo pida, o escribir en GitHub: ni comentarios, ni releases, ni cambios de configuración.
- Dar un estado de pieza sin haber leído sus pull requests, o una pieza por entregada sin un paso a Prod con su sí.
- Cambiar un escenario aprobado, o las pruebas de aceptación dentro del pull request de su pieza.
- Copiar las piezas a `Siguientes pasos`: en un proyecto de desarrollo, las tareas del código son las piezas del plan.
