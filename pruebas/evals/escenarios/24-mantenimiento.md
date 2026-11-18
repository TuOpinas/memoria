---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 60
preparar:
  - "escribir ventas/cuentas/taller/llamada-cliente-uno.md Notas de la llamada con Cliente Uno: piden soporte en 24 horas."
  - "migrar"
  - "personas"
turnos:
  - "Haz el mantenimiento de la carpeta."
  - "Sí."
  - "La nota de la llamada con Cliente Uno: ponle su cabecera, su aportación es lo que Cliente Uno pidió en la llamada. Lo demás, déjalo."
  - "Abre sesión en cuentas."
comprobar:
  - recuadro
  - nada-hasta-el-turno 2 metodo.md
  - tabla Memoria · mantenimiento@1
  - menciona Adopción@1
  - menciona Arreglo esto@1
  - no-menciona-re proyecto incompleto|verificar\.sh|mantenimiento\.py|=== |NO_REVISADO@1
  - existe ventas/cuentas/fuentes/
  - existe ventas/margenes/taller/
  - no-existe personas/nomina/entregables
  - no-existe personas/nomina/fuentes
  - contiene ventas/cuentas/taller/llamada-cliente-uno.md estado: borrador
  - contiene ventas/cuentas/sesiones.md (mantenimiento)
  - contiene ventas/cuentas/sesiones.md Arregló: taller/llamada-cliente-uno.md (cabecera)
  - contiene ventas/cuentas/sesiones.md Sesión de: mantenimiento de Ana Prueba
  - contiene ventas/cuentas/sesiones.md Último cierre:
  - contiene ventas/cuentas/sesiones.md Escrita:
  - no-menciona sesión cerrada@3
  - no-menciona-re trabajo sin sesi[oó]n[^|]*llamada-cliente-uno@4
  - solo-escribe-en ventas,operacion,metodo.md
---
El mantenimiento de la carpeta (1.26.6). La responsable de contexto lo pide: la conversación corre `mantenimiento.py`
(con su cuenta, que administra la carpeta y lo mira todo, también el área restringida de Personas) y `verificar.sh`,
enseña el recuadro «Memoria · mantenimiento» con los siete temas en llano, sin nombres de scripts ni de secciones, y la
lista exacta de lo mecánico antes de «¿Arreglo esto?»; no escribe ni crea nada antes del sí. Con un «sí» a secas crea
las carpetas que faltan en los proyectos de las áreas que Ana lleva, y nada en el área de Beto, aunque la vea.

El rastro (1.26.8): una nota de taller sin cabecera es un arreglo uno a uno. Cuando Ana dice cuál es su aportación, la
conversación le pone cabecera y deja en la bitácora del proyecto, con `cerrar.py` y la clave `mantenimiento`, una entrada
«(mantenimiento)» que la nombra (con «Último cierre» y «Escrita», que solo pone el script), sin decir que cerró una sesión.
Al abrir después sesión en el proyecto, la nota no sale como trabajo sin sesión.
