---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 40
preparar:
  - "migrar"
  - "personas"
turnos:
  - "¿Cómo va ventas/cuentas?"
  - "¿Lo que decidimos en cuentas cuadra con lo que decidieron soporte y precios?"
comprobar:
  - apertura-completa ventas/cuentas
  - no-menciona-re Lectura:@1
  - menciona Lectura: a fondo@2
  - menciona soporte@2
  - menciona no leí|sin leer|no se leyó|no leído|no he leído@2
  - solo-escribe-en metodo.md
  - sin-rutas-absolutas
---
Cuánto se lee (1.26.3). La primera pregunta se responde con lo que imprimió la apertura (nivel básico): sin la línea
«Lectura:». La segunda cruza proyectos: antes de leer dice «Lectura: a fondo» y qué carga (la superficie pública de
`operacion/soporte` y `ventas/precios`), y la respuesta termina con lo que no leyó. Nada se escribe salvo `metodo.md`.
