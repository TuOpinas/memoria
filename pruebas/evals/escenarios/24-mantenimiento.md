---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 60
preparar:
  - "migrar"
  - "personas"
turnos:
  - "Haz el mantenimiento de la carpeta."
  - "Sí."
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
  - solo-escribe-en ventas,operacion,metodo.md
---
El mantenimiento de la carpeta (1.26.6). La responsable de contexto lo pide: la conversación corre `mantenimiento.py`
(con su cuenta, que administra la carpeta y lo mira todo, también el área restringida de Personas) y `verificar.sh`,
enseña el recuadro «Memoria · mantenimiento» con los siete temas en llano, sin nombres de scripts ni de secciones, y la
lista exacta de lo mecánico antes de «¿Arreglo esto?»; no escribe ni crea nada antes del sí. Con un «sí» a secas crea
las carpetas que faltan en los proyectos de las áreas que Ana lleva, y nada en el área de Beto, aunque la vea.
