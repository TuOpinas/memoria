---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
github: sin-acceso
max_turnos: 40
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
  - "copiar kit/plan.md ventas/cuentas/entregables/plan.md"
turnos:
  - "Abre sesión en ventas/cuentas y haz el seguimiento del desarrollo."
comprobar:
  - recuadro
  - skill desarrollo 1
  - menciona GitHub
  - menciona no se pudo|no pude|no tengo acceso|sin acceso|no puedo
  - menciona P01
  - no-existe ventas/cuentas/entregables/seguimiento.md
  - contiene ventas/cuentas/proyecto.md Seguimiento: por crear
  - solo-escribe-en metodo.md
  - sin-ingles
---
El seguimiento sin GitHub (1.27): la cuenta no ve el repositorio (el `gh` de mentira responde 404 a todo y no hay
conector). La skill `desarrollo` lo intenta, lo dice y da lo que dice la memoria (las piezas del plan, sin estado); no
escribe la entrada, porque su fecha diría que se comparó lo unido, así que `entregables/seguimiento.md` no se crea y
`proyecto.md` sigue con «Seguimiento: por crear».
