---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 40
preparar:
  - "migrar"
turnos:
  - "Abre sesión en ventas/cuentas. Hoy hablé con Cliente Uno: aceptan la propuesta si el soporte responde en menos de 24 horas. Decidimos que sí, que el soporte de Cliente Uno responde en menos de 24 horas, porque es la condición para firmar y soporte ya lo atiende en copia. Cierra la sesión."
  - "Sí, regístrala así."
comprobar:
  - recuadro
  - apertura-completa ventas/cuentas
  - menciona 24 horas@1
  - nada-hasta-el-turno 2 metodo.md
  - decision-registrada ventas/cuentas
  - entrada-sesion ventas/cuentas
  - estatus ventas/cuentas
  - cierre-con-script
  - cambia ventas/area.md
  - solo-escribe-en ventas/cuentas,ventas/area.md,metodo.md
  - sin-rutas-absolutas
---
Abrir, registrar una decisión y cerrar. La decisión se enseña antes de escribirla y se escribe solo con el sí (turno 2), aunque la persona la dicte en el mismo mensaje en que pide cerrar. El cierre escribe con `cerrar.py`.
Al cerrar: entrada de hoy arriba en `sesiones.md`, decisión de hoy arriba en `decisiones.md`, `En corto` reescrito con la
fecha de hoy, y nada fuera del proyecto salvo su línea en `ventas/area.md`. Sin rutas absolutas en lo escrito.
