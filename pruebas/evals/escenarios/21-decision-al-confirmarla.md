---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 50
preparar:
  - "migrar"
  - "personas"
turnos:
  - "Abre sesión en ventas/cuentas. Con compras de Cliente Uno quedamos en algo: decidimos que el piloto se factura cada mes y no al final, porque así lo pide su área de compras para su presupuesto."
  - "Sí, regístrala."
  - "Bien. Cierra la sesión."
comprobar:
  - apertura-completa ventas/cuentas
  - nada-hasta-el-turno 2 metodo.md
  - cita-antes-de-escribir solo-decision@1
  - escrito-en-el-turno 2 ventas/cuentas/decisiones.md
  - nada-hasta-el-turno 3 metodo.md,ventas/cuentas/decisiones.md
  - decision-registrada ventas/cuentas
  - una-vez ventas/cuentas/decisiones.md se factura cada mes
  - entrada-sesion ventas/cuentas
  - cierre-con-script
  - no-menciona-re ¿Lo registro así@3
  - recuadro-cierre
  - solo-escribe-en ventas/cuentas,ventas/area.md,metodo.md
---
Una decisión se escribe en cuanto se confirma (1.26.4). En el turno 1 la persona decide sin pedir cerrar: la respuesta la
enseña en cita, tal como quedará, y pregunta si la registra; nada se escribe todavía. Con el sí (turno 2), `cerrar.py` con
solo `decisiones` la escribe y la sesión sigue abierta, sin marca del tablero ni recuadro de cierre. Al cerrar (turno 3),
`--comprobar` la da en `registradas_hoy`: no se vuelve a mandar ni a enseñar, el cierre no tiene decisiones ni preguntas y
escribe sin pedir el sí. La decisión queda una sola vez en el registro.
