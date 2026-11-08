---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 25
preparar:
  - "migrar"
  - "personas"
turnos:
  - "¿Qué le ofrecimos a Cliente Uno en la propuesta y qué falta para cerrarla?"
comprobar:
  - recuadro
  - apertura-completa ventas/cuentas
  - menciona Cliente Uno
  - solo-escribe-en metodo.md
  - llamadas-maximo 14
  - palabras-maximo 520
  - sin-ingles
  - skill sesion 1
  - sin-buscar-plugin
---
Trabajo de un proyecto sin nombrarlo: la pregunta es de `ventas/cuentas` (Cliente Uno). Debe abrir la sesión completa
de ese proyecto antes de responder (abrir.py con el proyecto, no solo la apertura mínima), responder con lo que dice la
carpeta y no escribir nada más que `metodo.md` (la raíz de prueba está atrasada): abrir solo lee. La skill `sesion` se carga una sola vez (1.24.8), y `abrir.py` corre directo con el proyecto. Desde la 1.24.9 la apertura mínima que va antes, para reconocer el proyecto, cuesta unas seis llamadas más (lee una copia en el contenedor en lugar de ejecutar en la computadora): el tope sube de 12 a 14.
