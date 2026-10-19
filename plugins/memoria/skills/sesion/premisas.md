# Premisas

Anexo de la skill `sesion`. Se lee cuando el responsable de contexto pide registrar, cambiar o retirar una premisa («registra como premisa que…», «la premisa P2 cambia a…», «esa premisa ya no vale»), y antes se carga entera la skill `convenciones`, porque se escribe en `base/`.

Solo en la sesión del responsable de contexto según `guia.md`; a cualquier otra persona se le dice que una premisa la registra él, y se le prepara el texto. Se hace en el momento en que se pide, no al cerrar, porque la dirección la confirma en voz alta y lo que importa es que quede.

1. Se lee `base/premisas.md` entero si existe. Si no existe, se crea con su cabecera (`estado: vigente`, `actualizado` de hoy) y el título `# Premisas`.
2. Se redacta la línea con el formato de la sección 2 de `convenciones`: `- P<n> · <texto> · Confirmó: <nombre y apellido> · <fecha de hoy>`, con el `P<n>` siguiente al mayor que haya en el archivo, aunque alguna esté reemplazada. Si cambia una que existe («la premisa P2 cambia a…», «ya no vale»), la línea nueva termina en `· Reemplaza a P<n>`; la antigua no se toca. Quien confirma es quien dirige la organización, no quien abre la sesión, salvo que sean la misma persona: se pregunta si no está claro.
3. Se enseña la línea y se escribe solo con el sí. Se añade al final del archivo y se pone al día `actualizado`.
4. Si la premisa nueva reemplaza a una con cuestionamientos abiertos (los del barrido al abrir), se dice que quedan respondidos y a quién avisar: a quien los planteó. Si la premisa se mantiene frente a un cuestionamiento, no hay línea nueva: la respuesta es una entrada con `Responde a:` en el `decisiones.md` de un proyecto del responsable de contexto, como cualquier otra (paso 3 de cerrar).

Una premisa es algo que la dirección confirmó y sobre lo que todos construyen; un objetivo de un proyecto o una preferencia de un área no lo es. Ante la duda, se pregunta de quién es la confirmación.
