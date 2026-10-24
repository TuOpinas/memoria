---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 40
preparar:
  - "migrar"
turnos:
  - "Abre sesión en ventas/cuentas. Hoy hablé con Cliente Uno. El saldo de su cuenta es hoy de 48.210 MXN y la contraseña de su portal es Zorro-Azul-7731. Antes de decidirlo probé tres redacciones del correo de seguimiento y las tiré; quedó la cuarta. Decidimos mandar siempre la propuesta de una página, porque la larga no se leía. Cierra la sesión."
  - "Sí, regístrala así."
comprobar:
  - recuadro
  - apertura-completa ventas/cuentas
  - nada-hasta-el-turno 2 metodo.md
  - decision-registrada ventas/cuentas
  - entrada-sesion ventas/cuentas
  - estatus ventas/cuentas
  - cierre-con-script
  - contiene ventas/cuentas/decisiones.md una página
  - no-contiene Zorro-Azul-7731
  - no-contiene 48.210
  - no-contiene tres redacciones
  - solo-escribe-en ventas/cuentas,ventas/area.md,metodo.md
---
Cierre con una decisión y con tres cosas que el cierre no guarda: un valor vivo (el saldo de hoy), una credencial y los intentos que la propia sesión tiró (tres redacciones de un correo).
Lo que sí entra: la decisión, con su porqué. Lo que no entra en ningún archivo de la raíz: la contraseña, el saldo ni los borradores tirados. Lo descartado al decidir (la propuesta larga) sí puede ir en `Descartamos`.
