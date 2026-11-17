---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 40
preparar:
  - "sustituir ventas/cuentas/decisiones.md \n## 2026-09-26 · Cliente Uno se sigue atendiendo => \n## {HOY-30} · El piloto de Cliente Uno se factura cada mes\nDecidió: Ana Prueba\nPor qué: así lo pidió su área de compras.\n\n## 2026-09-26 · Cliente Uno se sigue atendiendo"
  - "sustituir ventas/cuentas/decisiones.md \n## Decisión recuperada sin fecha => \n## 2025-12-01 · El soporte de Cliente Uno responde en 48 horas\nDecidió: Ana Prueba\nPor qué: soporte atiende de lunes a viernes y no cubre más.\n\n## Decisión recuperada sin fecha"
  - "migrar"
  - "personas"
turnos:
  - "Abre sesión en ventas/cuentas. Cliente Uno firma si el soporte le responde en menos de 24 horas, y decidimos que sí: soporte ya lo atiende en copia y es la condición para firmar. Cierra la sesión."
  - "Sí, regístrala así; reemplaza a la de 48 horas."
comprobar:
  - apertura-completa ventas/cuentas
  - menciona 48 horas@1
  - menciona reemplaza@1
  - nada-hasta-el-turno 2 metodo.md
  - decision-registrada ventas/cuentas
  - decision-reemplaza ventas/cuentas 48 horas
  - cierre-con-script
  - solo-escribe-en ventas/cuentas,ventas/area.md,metodo.md
  - recuadro-cierre
---
La decisión de hoy contradice una anterior del mismo proyecto que ni la sesión ni la apertura mencionan: es de 2025 y queda
fuera de las cinco que se imprimen (1.26.3). Antes de enseñarla, `cerrar.py --comprobar` devuelve en `parecidas` la de
48 horas, y la respuesta que pide el sí la enseña debajo de la decisión con la pregunta de si la reemplaza. La persona da el sí
y dice cuál en el segundo turno, y la decisión se escribe con su `Reemplaza:`, nunca antes. La primera corrida (1.26.3)
escribió así con el sí y el nombre juntos; desde entonces `cerrar.md` lo permite.
