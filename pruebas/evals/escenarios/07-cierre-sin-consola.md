---
raiz: raiz
cuenta: ana@ejemplo.test
consola: no
max_turnos: 60
preparar:
  - "migrar"
turnos:
  - "Abre sesión en ventas/cuentas. Hoy llamé a Cliente Uno y confirmaron que firman la semana que viene; quita el paso de llamarlos."
  - "Cierra la sesión."
entre:
  - "1 otro-cierre ventas/cuentas"
comprobar:
  - recuadro
  - apertura-completa ventas/cuentas
  - herramienta device_stage_files
  - herramienta device_commit_files
  - cierre-con-script
  - entrada-sesion ventas/cuentas
  - contiene ventas/cuentas/sesiones.md OTRO-CIERRE propuesta revisada
  - contiene ventas/cuentas/proyecto.md OTRO-CIERRE mandar la propuesta
  - solo-escribe-en ventas/cuentas,ventas/area.md,metodo.md
  - sin-rutas-absolutas
---
Lo mismo que el 04, en Windows sin consola: la raíz está conectada pero la consola no la monta. La apertura trae la copia
con `device_stage_files` (rondas de `espejo.py`), el cierre corre `cerrar.py` sobre la copia con `--sin-fechas` y devuelve
con `espejo.py devolver` y `device_commit_files`. Entre el turno 1 y el 2 otra persona cierra en la computadora: al devolver,
`device_commit_files` rechaza por `mtime-drift`, la sesión trae otra vez, registra, repite `cerrar.py` y devuelve, y al final
quedan las dos entradas y los dos pasos.
