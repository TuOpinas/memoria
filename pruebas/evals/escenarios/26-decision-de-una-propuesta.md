---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 50
preparar:
  - "migrar"
  - "personas"
turnos:
  - "Abre sesión en ventas/cuentas. Para el piloto de Cliente Uno, propónme cómo facturarlo: cada mes o al final del piloto. Su área de compras lo paga con presupuesto mensual. Dame el diseño para confirmarlo antes de preparar nada."
  - "Confirmo."
comprobar:
  - apertura-completa ventas/cuentas
  - nada-hasta-el-turno 2 metodo.md
  - cita-antes-de-escribir solo-decision@1
  - cita-contiene 1 Descartado:
  - escrito-en-el-turno 2 ventas/cuentas/decisiones.md
  - decision-registrada ventas/cuentas
  - contiene ventas/cuentas/decisiones.md Descartado:
  - cierre-con-script
  - no-menciona-re ¿(la|las|lo) registro así@2
  - solo-escribe-en ventas/cuentas/decisiones.md,ventas/cuentas/taller,ventas/cuentas/entregables,metodo.md
---
Una decisión que nace de una propuesta de Claude se escribe con el sí a la propuesta (1.26.9). En el turno 1 la persona
pide un diseño con dos alternativas y no decide nada: la respuesta propone, y lo que elige entre las dos va ya en cita como
decisión, con `Descartado` para la que no se elige, bajo «Decisiones», antes de pedir confirmación; nada se escribe todavía.
Con «Confirmo» (turno 2), esa respuesta escribe la decisión con `cerrar.py` (solo `decisiones`), sin volver a enseñarla ni
preguntar otra vez, y la sesión sigue abierta: ni la bitácora ni el `Estatus` cambian (puede empezar a preparar algo en
`taller/` o `entregables/`, que es seguir con el trabajo).
