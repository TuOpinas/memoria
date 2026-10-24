---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 40
preparar:
  - "migrar"
  - "copia-en-conflicto ventas/cuentas/sesiones.md"
turnos:
  - "Abre sesión en ventas/cuentas."
  - "Sí, júntalas y manda la copia a la papelera."
comprobar:
  - apertura-completa ventas/cuentas
  - menciona conflicto@1
  - conserva-entradas ventas/cuentas
  - contiene ventas/cuentas/sesiones.md ENTRADA-CONFLICTO
  - herramienta device_request_delete_permission
  - no-existe ventas/cuentas/sesiones (1).md
  - solo-escribe-en ventas/cuentas,metodo.md
---
Drive dejó `sesiones (1).md` junto a `sesiones.md` con una entrada que el original no tiene. La apertura avisa de la
copia en conflicto; con el sí, se juntan las entradas de las dos en el original (ninguna se pierde) y la copia va a la
papelera (con consola, pidiendo el permiso de borrar).
