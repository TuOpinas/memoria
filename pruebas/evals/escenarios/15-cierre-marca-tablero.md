---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
tablero: 15-tablero-vacio.json
max_turnos: 40
preparar:
  - "migrar"
turnos:
  - "Abre sesión en ventas/cuentas. Hoy revisé con Cliente Uno la propuesta y quedó en que la responden el viernes. Cierra la sesión."
  - "Sí."
comprobar:
  - recuadro
  - apertura-completa ventas/cuentas
  - herramienta db_query
  - entrada-sesion ventas/cuentas
  - cierre-con-script
  - marca-tablero ventas/cuentas
  - menciona Tablero: avisado@2
  - recuadro-cierre
  - solo-escribe-en ventas/cuentas,ventas/area.md,metodo.md
---
Abrir con un tablero de la cuenta (la cola vacía) y cerrar sin decisión. Lo que debe pasar (1.25.1): el cierre deja su marca en
la colección «cierres» del tablero con `db_write`, como dice el primer paso de `respuesta` de `cerrar.py`, y el recuadro de
cierre lleva la fila «Tablero: avisado». En Smile Pill, el 2026-11-03, dos cierres completos se saltaron la marca y la página
no pidió sincronizar.
