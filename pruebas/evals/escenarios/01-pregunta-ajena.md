---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 20
turnos:
  - "¿Cuántos días tiene octubre?"
  - "Después."
comprobar:
  - recuadro
  - apertura-minima
  - pregunta-claude-outputs
  - menciona 31@1
  - solo-escribe-en metodo.md
  - palabras-maximo 120
  - sin-ingles
---
Una pregunta que no tiene que ver con la memoria, en una conversación con la carpeta conectada y la cuenta del
responsable de contexto. Lo que debe pasar: la apertura mínima antes de responder, el recuadro «Memoria de trabajo» en la
primera respuesta, la respuesta a la pregunta, y al final la pregunta por los archivos sueltos de «Claude outputs» (los hay
en la raíz de prueba). Con «Después», nada se mueve. Lo único que cambia en la raíz es `metodo.md`, que la cuenta pone al día porque la raíz de prueba lleva la 1.11.
