---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
aviso: sin-descarga
max_turnos: 20
preparar:
  - "migrar"
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
El 01 con un aviso de arranque que no trae la descarga, como cuando el hook corre donde no hay python3 (1.24.7). Desde la
1.24.9 la apertura mínima no la necesita: lee una copia y corre `abrir.py` en el contenedor desde PLUGIN, que el aviso trae
siempre. Mide que no busque el plugin en disco (`sin-buscar-plugin`) ni ejecute nada en la computadora (`minima-sin-ejecutar`).
