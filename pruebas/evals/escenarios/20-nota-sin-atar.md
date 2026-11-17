---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 50
preparar:
  - "migrar"
  - "personas"
turnos:
  - "Abre sesión en ventas/cuentas. Guárdame en el taller una nota corta, condiciones-cliente-uno.md, con las condiciones que puso Cliente Uno para firmar: soporte en menos de 24 horas y el anexo después de la propuesta. Luego cierra la sesión."
  - "Es la base de la propuesta base."
  - "Sí."
comprobar:
  - apertura-completa ventas/cuentas
  - nada-hasta-el-turno 2 metodo.md,ventas/cuentas/taller/condiciones-cliente-uno.md
  - entrada-sesion ventas/cuentas
  - contiene ventas/cuentas/sesiones.md Escribió: taller/condiciones-cliente-uno.md
  - basado-en ventas/cuentas/entregables/propuesta-base.md taller/condiciones-cliente-uno.md
  - cierre-con-script
  - solo-escribe-en ventas/cuentas,ventas/area.md,metodo.md
---
Una nota de taller que nada cita (1.26.3). La sesión escribe la nota y, al cerrar, `cerrar.py --comprobar` la devuelve en
`sin_citar`: la respuesta que pide el sí pregunta para qué sirve, y nada más que la nota se escribe antes del segundo
turno (el entregable no se ata solo). La persona dice que es la base de la propuesta, y el
cierre la ata con un campo que ya existe, el `basado_en` de `entregables/propuesta-base.md`, por «otros».
