---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
tablero: 14-cola.json
max_turnos: 25
preparar:
  - "migrar"
turnos:
  - "Abre sesión en ventas/cuentas."
comprobar:
  - recuadro
  - apertura-completa ventas/cuentas
  - skill sesion 1
  - herramienta db_query
  - menciona Aceptaste@1
  - no-menciona Cuestionaste
  - no-menciona Beto Prueba aceptó
  - no-menciona Beto Prueba cuestionó
  - menciona Eva@1
  - solo-escribe-en metodo.md
  - sin-ingles
---
La cola del tablero trae tres respuestas a decisiones de Beto Prueba (operacion/soporte): dos aceptadas por la dueña del
tablero, sin `por` (de antes de la 1.24.8), y una cuestionada por Eva Prueba, con `por`. Lo que debe pasar (1.24.8): el
recuadro «lo que marcaste en el tablero» dice «Aceptaste…» para las dos aceptadas y nombra a Eva (por su correo, que es lo que hay) como quien cuestionó la tercera, con Beto Prueba como quien
decidió y nunca como quien marcó (en Smile Pill, el 2026-11-02, salió «Marco Herrero aceptó»). Abrir solo lee.
