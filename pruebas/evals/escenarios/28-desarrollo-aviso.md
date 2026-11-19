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
  - "escribir ventas/cuentas/proyecto.md Acepta: Ana Prueba (ana@ejemplo.test, @ana-prueba)"
  - "escribir ventas/cuentas/proyecto.md Audita: Beto Prueba (beto@ejemplo.test, @beto-prueba)"
  - "escribir ventas/cuentas/proyecto.md Construye: Ana Prueba (ana@ejemplo.test, @ana-prueba)"
  - "escribir ventas/cuentas/proyecto.md Administra: Beto Prueba (beto@ejemplo.test, @beto-prueba)"
turnos:
  - "Retomamos ventas/cuentas."
comprobar:
  - recuadro
  - apertura-completa ventas/cuentas
  - tabla Memoria · avisos
  - menciona por crear|falta
  - menciona Paso a Prod
  - menciona plan
  - no-menciona-re \bR[1-7]\b|\bPL[1-7]\b
  - solo-escribe-en metodo.md
  - sin-herramienta mcp__remote-devices__device_commit_files
  - sin-ingles
---
Un proyecto de desarrollo (1.27): `ventas/cuentas` lleva la sección «Desarrollo», con las configuraciones y el diseño por
crear, sin la línea «Paso a Prod» y con un plan que apunta a un archivo que no existe. La apertura lo avisa en llano,
dentro del recuadro de avisos: lo que está por crear, la línea que falta y el plan que no está. Sin leer GitHub, sin
códigos de regla («R1», «PL2») y sin escribir nada más que `metodo.md`.
