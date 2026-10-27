---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 50
preparar:
  - "migrar"
turnos:
  - "Abre sesión en ventas/cuentas. Escríbeme en el taller una nota corta, nota-soporte.md, con lo que acordamos hoy con Cliente Uno: el soporte responde en menos de 24 horas. Después publica el entregable borrador-viejo.md tal como está, que ya lo revisé. Y cierra la sesión."
  - "Sí, así."
comprobar:
  - recuadro
  - apertura-completa ventas/cuentas
  - entrada-sesion ventas/cuentas
  - cierre-con-script
  - contiene ventas/cuentas/sesiones.md Escribió: taller/nota-soporte.md
  - contiene ventas/cuentas/sesiones.md Publicó: entregables/borrador-viejo.md
  - contiene ventas/cuentas/entregables/borrador-viejo.md estado: vigente
  - recuadro-cierre
  - solo-escribe-en ventas/cuentas,ventas/area.md,metodo.md
  - sin-rutas-absolutas
---
Quién escribió y quién publicó (1.23). La sesión escribe un documento del taller y publica un entregable con la skill
`revisar` (Ana es la responsable del proyecto), y el cierre los nombra en `escribio` y `publico`: `cerrar.py` escribe
«Escribió:» y «Publicó:» en la entrada, antes de «Sesión de:», sin que nadie los teclee. Antes de enseñar la entrada, una
llamada con `--comprobar` la devuelve completa. El cierre termina con el recuadro «Memoria · sesión cerrada · N archivos».
