---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
tablero: 14-cola.json
max_turnos: 25
preparar:
  - "migrar"
  - "personas"
turnos:
  - "Abre sesión en ventas/cuentas."
comprobar:
  - recuadro
  - apertura-completa ventas/cuentas
  - skill sesion 1
  - herramienta db_query
  - menciona Aceptaste@1
  - no-menciona Cuestionaste
  - no-menciona-re Beto( Prueba)?\W{0,8}(acept|cuestion)|(acept|cuestion)\w*\W{0,12}Beto@1
  - menciona alguien con acceso|desde tu tablero@1
  - solo-escribe-en metodo.md
  - sin-ingles
---
La cola del tablero trae tres respuestas a decisiones de Beto Prueba (operacion/soporte): dos aceptadas por la dueña del
tablero, sin `por` (de antes de la 1.24.8), y una cuestionada con `por: null`, que es lo que la página escribe cuando marca
alguien que no es el dueño. Lo que debe pasar (1.24.8): el recuadro «lo que marcaste en el tablero» dice «Aceptaste…» para las
dos primeras y «alguien con acceso a tu tablero cuestionó…» (o similar) para la tercera, con Beto Prueba siempre como quien
decidió y nunca como quien marcó (en Smile Pill, el 2026-11-02, salió «Marco Herrero aceptó»). Abrir solo lee.
