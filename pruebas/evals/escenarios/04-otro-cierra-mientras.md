---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 40
preparar:
  - "migrar"
turnos:
  - "Abre sesión en ventas/cuentas. Hoy llamé a Cliente Uno y me confirmaron que firman la semana que viene; quita el paso de llamarlos."
  - "Cierra la sesión."
  - "Sí, regístralo así."
entre:
  - "1 otro-cierre ventas/cuentas"
comprobar:
  - apertura-completa ventas/cuentas
  - cierre-con-script
  - entrada-sesion ventas/cuentas
  - contiene ventas/cuentas/sesiones.md OTRO-CIERRE propuesta revisada
  - contiene ventas/cuentas/proyecto.md OTRO-CIERRE mandar la propuesta
  - menciona mientras|también cerró|otra sesión|Carla|alguien más escribió|alguien escribió
  - cita-antes-de-escribir
  - recuadro-cierre
  - solo-escribe-en ventas/cuentas,ventas/area.md,metodo.md
---
Mientras la sesión está abierta, otra persona cierra la suya sobre el mismo proyecto (entre el turno 1 y el 2: una
entrada nueva arriba de `sesiones.md` y un paso nuevo en `proyecto.md`). Desde la 1.22 el cierre enseña el `Estatus` antes de escribir y escribe con el sí (turno 3). Al cerrar, `cerrar.py` escribe encima de lo
nuevo: las dos entradas quedan, el paso de la otra persona queda, y Claude dice en media línea que alguien escribió
mientras tanto (`ajenos`).
