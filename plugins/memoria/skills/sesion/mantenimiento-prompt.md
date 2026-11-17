Mantenimiento {{CADENCIA}} de la carpeta de memoria de {{ORGANIZACION}}. Trabaja en español.

Antes de nada, sin cargar nada: si la cadencia es mensual y hoy, en {{ZONA}}, es después del día 7 del mes, termina sin hacer nada y sin avisar (la mensual corre el primer viernes del mes).

Las instrucciones viven en el plugin `memoria` instalado, no en este mensaje. Carga la skill `memoria:sesion` con la herramienta Skill y sigue su anexo `mantenimiento.md`, la parte «Cuando corre la tarea», con estos valores:

- CARPETA: {{CARPETA}} (en la consola, `$HOME/mnt/{{CARPETA}}`)
- CUENTA: {{CUENTA}}
- ZONA: {{ZONA}}
- DIAS: {{DIAS}}
- CADENCIA: {{CADENCIA}}

No escribas nada en la carpeta: deja el resumen, la lista y la pregunta, y arregla solo si la persona contesta en esta conversación.

Si la skill no carga, no improvises otra vía: avisa una sola vez con PushNotification (si no existe, SendUserMessage), «El mantenimiento de {{ORGANIZACION}} no corrió: esta cuenta no tiene instalado el plugin memoria», y termina.
