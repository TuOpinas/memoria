---
raiz: raiz
cuenta: carla@ejemplo.test
consola: si
max_turnos: 40
turnos:
  - "Abre sesión en ventas/cuentas y anota en los siguientes pasos que mando la propuesta revisada a Cliente Uno el lunes. Cierra la sesión."
  - "Sí, soy Carla Prueba. Deja el paso viejo como está."
comprobar:
  - recuadro
  - no-menciona Claude outputs
  - apertura-completa ventas/cuentas
  - solo-escribe-en ventas,metodo.md
  - entrada-sesion ventas/cuentas
  - cierre-con-script
  - bloque-igual ventas/area.md Panorama
  - bloque-igual ventas/area.md Prioridades ahora
  - no-contiene ventas/area.md ## Estatus
  - sin-rutas-absolutas
---
Una cuenta que colabora en `ventas` (carla@) y no es responsable de contexto: escribe solo dentro de `ventas`, y no se
le dice nada de «Claude outputs» en la apertura. El cierre enseña la entrada y el `Estatus` del proyecto y escribe con el sí (turno 2); el `Estatus` del área no lo toca, porque es de su responsable (desde la 1.18.4 eso es del responsable; a los demás los cubre el hook).
