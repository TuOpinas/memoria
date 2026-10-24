---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 25
preparar:                       # la raíz ya en la 1.22: sin migrar, la pregunta bloqueante ocuparía el turno 1 (eval 10)
  - "migrar"
turnos:
  - "¿Qué le ofrecimos a Cliente Uno en la propuesta y qué falta para cerrarla?"
comprobar:
  - recuadro
  - apertura-completa ventas/cuentas
  - menciona Cliente Uno
  - solo-escribe-en metodo.md
  - llamadas-maximo 12
  - palabras-maximo 520
  - sin-ingles
---
Trabajo de un proyecto sin nombrarlo: la pregunta es de `ventas/cuentas` (Cliente Uno). Debe abrir la sesión completa
de ese proyecto antes de responder (abrir.py con el proyecto, no solo la apertura mínima), responder con lo que dice la
carpeta y no escribir nada más que `metodo.md` (la raíz de prueba está atrasada): abrir solo lee.
