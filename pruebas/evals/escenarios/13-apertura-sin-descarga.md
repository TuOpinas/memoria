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
---
El 01 con un aviso de arranque que no trae la descarga, como cuando el hook corre donde no hay python3 (1.24.7). La
apertura mínima tiene que cargar la skill `sesion` y calcular la descarga con `preparar.py` desde el directorio de la skill,
con un comando simple, sin buscar el plugin en disco (`find`), que en modo Auto la app frena con un permiso. El eval corre
sin permisos, así que lo que mide es que no haya búsqueda: `sin-buscar-plugin`.
