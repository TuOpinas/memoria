---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 40
preparar:
  - "sustituir ventas/cuentas/proyecto.md - Preparar el contrato de Cliente Uno con la plantilla de propuesta. => - Preparar el contrato de Cliente Uno con la plantilla de propuesta.\n- Revisar el glosario de la propuesta.\n- Pedir a dirección la firma del anexo.\n- Archivar las versiones viejas de la propuesta."
  - "migrar"
  - "personas"
turnos:
  - "Abre sesión en ventas/cuentas. Ya quedó el plan para cerrar Cliente Uno, en este orden: primero Ana prepara el contrato marco; después Bea Prueba revisa con soporte el arranque de la fase 1; y al final Ana manda la factura del piloto. Con eso, cierra la sesión."
  - "Sí, así."
comprobar:
  - apertura-completa ventas/cuentas
  - nada-hasta-el-turno 2 metodo.md
  - entrada-sesion ventas/cuentas
  - estatus ventas/cuentas
  - orden ventas/cuentas/proyecto.md ## Siguientes pasos | contrato marco | Bea | factura del piloto
  - orden ventas/cuentas/proyecto.md factura del piloto | Archivar las versiones viejas
  - cierre-con-script
  - recuadro-cierre
---
El orden de trabajo acordado en la sesión vive solo en la conversación (1.26.3). El proyecto tiene once pasos, así que la
apertura imprime diez y cuenta uno más; el plan va arriba de la sección, donde la siguiente apertura lo imprime. Antes de enseñar el `Estatus`, el
cierre lo busca y lo lleva a «Siguientes pasos» de `proyecto.md`, en su orden y con quién hace cada paso, y lo escribe
con el mismo sí que la entrada.
