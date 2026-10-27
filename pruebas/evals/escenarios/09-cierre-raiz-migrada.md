---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 40
preparar:
  - "migrar"
turnos:
  - "Abre sesión en ventas/cuentas. Hoy hablé con Cliente Uno: aceptan la propuesta si el soporte responde en menos de 24 horas. Decidimos que sí, que el soporte de Cliente Uno responde en menos de 24 horas, porque es la condición para firmar y soporte ya lo atiende en copia; descartamos ofrecer un plazo de 48 horas. Cierra la sesión."
  - "Sí, regístralo así."
comprobar:
  - recuadro
  - apertura-completa ventas/cuentas
  - nada-hasta-el-turno 2 metodo.md
  - decision-registrada ventas/cuentas
  - entrada-sesion ventas/cuentas
  - estatus ventas/cuentas
  - nombres-nuevos ventas/cuentas
  - cierre-con-script
  - cambia ventas/area.md
  - contiene ventas/area.md ## Estatus
  - no-contiene ventas/area.md ## Panorama
  - solo-escribe-en ventas/cuentas,ventas/area.md,metodo.md
  - no-menciona estructura de antes
  - cita-antes-de-escribir decision
  - recuadro-cierre
  - sin-rutas-absolutas
---
El mismo cierre que el 03, sobre una raíz que ya pasó a la estructura de la 1.22 (la cuenta de Ana la migró antes de empezar; las áreas de Beto siguen como estaban: raíz mezclada).
La apertura no ofrece migrar nada, porque lo de Ana está al día. Antes de escribir, el cierre enseña la decisión y el `Estatus` y espera el sí (turno 2). Al cerrar: la entrada nueva con «Tema:» y sin «Pendiente:», la decisión con «Descartado:» y no «Descartamos:», el `Estatus` del proyecto con la fecha de hoy y el del área reescrito, todo con `cerrar.py`.
