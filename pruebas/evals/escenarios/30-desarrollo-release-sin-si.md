---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
github: 30-github.json
max_turnos: 45
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
  - existe ventas/cuentas/entregables/seguimiento.md
  - contiene ventas/cuentas/entregables/seguimiento.md no tiene «Aprobó:»
  - contiene ventas/cuentas/entregables/seguimiento.md estado: vigente
  - contiene ventas/cuentas/entregables/seguimiento.md acme/portal#1
  - contiene ventas/cuentas/proyecto.md Seguimiento: ventas/cuentas/entregables/seguimiento.md
  - menciona Aprobó
  - solo-escribe-en metodo.md,ventas/cuentas/proyecto.md,ventas/cuentas/entregables/seguimiento.md
  - sin-ingles
---
El seguimiento con un paso a Prod sin sí (1.27): el `gh` de mentira sirve `acme/portal` con P01 unida, P02 abierta, un
pull request sin pieza y el release v0.1.0 publicado sin la línea «Aprobó:». La skill `desarrollo` lee GitHub con
`recoger_github.py`, escribe la entrada con `seguimiento.py --escribir`, que crea `entregables/seguimiento.md` vigente
porque la línea decía «por crear», pone su ruta en `proyecto.md` con `cerrar.py` (solo `reemplazos`) y devuelve los
dos archivos. La respuesta dice que el release no tiene «Aprobó:» y que eso le toca a quien audita; el pull request sin
pieza sale fuera del plan.
