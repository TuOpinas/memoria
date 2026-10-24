---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 25
turnos:
  - "¿Qué le ofrecimos a Cliente Uno en la propuesta y qué falta para cerrarla?"
comprobar:
  - recuadro
  - apertura-completa ventas/cuentas
  - menciona Cliente Uno
  - solo-escribe-en metodo.md
  - llamadas-maximo 12
  - palabras-maximo 450
  - sin-ingles
---
Trabajo de un proyecto sin nombrarlo: la pregunta es de `ventas/cuentas` (Cliente Uno). Debe abrir la sesión completa
de ese proyecto antes de responder (abrir.py con el proyecto, no solo la apertura mínima), responder con lo que dice la
carpeta y no escribir nada más que `metodo.md` (la raíz de prueba está atrasada): abrir solo lee.
