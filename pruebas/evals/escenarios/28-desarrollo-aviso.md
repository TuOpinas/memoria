---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 25
preparar:
  - "migrar"
  - "personas"
  - "escribir ventas/cuentas/proyecto.md ## Desarrollo"
  - "escribir ventas/cuentas/proyecto.md Repositorios: acme/portal"
  - "escribir ventas/cuentas/proyecto.md Configuración de plataforma: por crear"
  - "escribir ventas/cuentas/proyecto.md Configuración de repositorios: por crear"
  - "escribir ventas/cuentas/proyecto.md Diseño: por crear"
  - "escribir ventas/cuentas/proyecto.md Plan: ventas/cuentas/entregables/plan.md"
  - "escribir ventas/cuentas/proyecto.md Seguimiento: por crear"
  - "escribir ventas/cuentas/proyecto.md Paso a Prod: release de GitHub"
  - "escribir ventas/cuentas/proyecto.md Acepta: Ana Prueba (ana@ejemplo.test, @ana-prueba)"
  - "escribir ventas/cuentas/proyecto.md Audita: Beto Prueba (beto@ejemplo.test, @beto-prueba)"
  - "escribir ventas/cuentas/proyecto.md Construye: Ana Prueba (ana@ejemplo.test, @ana-prueba)"
  - "escribir ventas/cuentas/proyecto.md Administra: Beto Prueba (beto@ejemplo.test, @beto-prueba)"
  - "copiar kit/plan-sin-columna.md ventas/cuentas/entregables/plan.md"
turnos:
  - "Retomamos ventas/cuentas."
comprobar:
  - recuadro
  - apertura-completa ventas/cuentas
  - tabla Memoria · avisos
  - menciona por crear|falta
  - menciona seguimiento
  - menciona Hecha cuando
  - no-menciona-re \bR[1-7]\b|\bPL[1-7]\b
  - solo-escribe-en metodo.md
  - sin-ingles
---
Un proyecto de desarrollo (1.27): `ventas/cuentas` lleva la sección «Desarrollo», con las configuraciones y el diseño por
crear, un plan sin la columna «Hecha cuando» y ningún seguimiento. La apertura lo avisa en llano, dentro del recuadro de
avisos: lo que está por crear, la columna que le falta al plan y que no hay seguimiento todavía. Sin leer GitHub, sin
códigos de regla («R1», «PL2») y sin escribir nada más que `metodo.md`.
