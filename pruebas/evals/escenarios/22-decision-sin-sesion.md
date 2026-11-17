---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 50
preparar:
  - "migrar"
  - "personas"
  - "sustituir ventas/cuentas/decisiones.md \n## 2026-09-26 · Cliente Uno se sigue atendiendo => \n## {HOY-1} · El piloto de Cliente Uno se factura cada mes\nDecidió: Ana Prueba\nPor qué: así lo pidió su área de compras.\n\n## 2026-09-26 · Cliente Uno se sigue atendiendo"
  - "tocar ventas/cuentas/decisiones.md"
turnos:
  - "Abre sesión en ventas/cuentas."
  - "Fue mía, ayer se me quedó la conversación abierta. Cierra la sesión."
comprobar:
  - apertura-completa ventas/cuentas
  - menciona Decisiones sin sesión|ninguna entrada|no se cerró@1
  - menciona factura cada mes@1
  - entrada-sesion ventas/cuentas
  - contiene ventas/cuentas/sesiones.md factura
  - una-vez ventas/cuentas/decisiones.md se factura cada mes
  - no-menciona-re ¿Lo registro así@2
  - cierre-con-script
  - recuadro-cierre
  - solo-escribe-en ventas/cuentas,ventas/area.md,metodo.md
---
Una sesión de ayer registró una decisión y nunca se cerró (1.26.4): `decisiones.md` es más nuevo que `sesiones.md`. La
apertura lo avisa («Decisiones sin sesión», con el título) y pregunta de quién es. La persona dice que fue suya y pide
cerrar: la decisión no se vuelve a escribir, la entrada de hoy la cuenta, y como el cierre no tiene decisiones ni preguntas
escribe sin pedir el sí.
