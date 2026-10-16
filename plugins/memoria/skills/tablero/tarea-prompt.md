Pon al día el tablero ({{MODO}}) de la carpeta de memoria de {{ORGANIZACION}}. Trabaja en español.

Las instrucciones viven en el plugin `memoria` instalado, no en este mensaje, para que cada versión nueva llegue sin que nadie tenga que aprobar nada. Busca el directorio de su skill `tablero` con Bash `find /root/.claude/plugins -type d -path "*memoria/skills/tablero" | head -1`, lee entero el archivo `tarea.md` que hay en él y síguelo al pie de la letra, con estos cuatro valores:

- ORGANIZACION: {{ORGANIZACION}}
- RUTA_RAIZ: {{RUTA_RAIZ}}
- URL: {{URL}}
- MODO: {{MODO}}

Si no encuentras el plugin o su `tarea.md`, no improvises otra vía: avisa una sola vez con PushNotification (si no existe, SendUserMessage): «El tablero de {{ORGANIZACION}} no se puso al día: esta cuenta no tiene instalado el plugin memoria» y termina.
