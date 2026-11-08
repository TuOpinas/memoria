---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 20
preparar:
  - "migrar"
  - "personas"
turnos:
  - "¿Cuántos días tiene octubre?"
  - "Después."
comprobar:
  - recuadro
  - apertura-minima
  - pregunta-claude-outputs
  - menciona 31@1
  - solo-escribe-en metodo.md
  - sin-buscar-plugin
  - sin-ingles
  - minima-sin-ejecutar
---
El 01 midiendo cómo abre la mínima: desde la 1.24.9 lee una copia y corre `abrir.py` en el contenedor desde PLUGIN, que el
aviso trae siempre, y desde la 1.25.1 el aviso ya no trae ninguna descarga (nació como «el aviso sin descarga», 1.24.7). Mide
que no busque el plugin en disco (`sin-buscar-plugin`) ni ejecute nada en la computadora (`minima-sin-ejecutar`).
