Pon al día el tablero ({{MODO}}) de la carpeta de memoria de {{ORGANIZACION}}. Trabaja en español.

Las instrucciones viven en el plugin `memoria` instalado, no en este mensaje, para que cada versión nueva llegue sin que nadie tenga que aprobar nada. Carga su skill `tarea-tablero` con la herramienta Skill (`memoria:tarea-tablero`) y síguela al pie de la letra, con estos cuatro valores:

- ORGANIZACION: {{ORGANIZACION}}
- RUTA_RAIZ: {{RUTA_RAIZ}}
- URL: {{URL}}
- MODO: {{MODO}}

Si la skill no carga, no improvises otra vía: avisa una sola vez con PushNotification (si no existe, SendUserMessage): «El tablero de {{ORGANIZACION}} no se puso al día: esta cuenta no tiene instalado el plugin memoria» y termina.
