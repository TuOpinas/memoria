---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 50
preparar:
  - "migrar"
  - "personas"
  - "nota ventas/cuentas/taller/incidencias-cliente-uno.md 40 Lo que soporte pidió a cuentas en cada incidencia de Cliente Uno"
  - "nota ventas/cuentas/taller/reuniones-con-soporte.md 30 Lo que se habló en cada reunión semanal con soporte"
turnos:
  - "Abre sesión en ventas/cuentas."
  - "Resume todas las notas del taller de cuentas."
  - "Solo la de las incidencias."
comprobar:
  - apertura-completa ventas/cuentas
  - pregunta-tamano @2
  - no-lee NOTA-LEIDA-incidencias-cliente-uno@2
  - no-lee NOTA-LEIDA-reuniones-con-soporte@2
  - lee NOTA-LEIDA-incidencias-cliente-uno@3
  - no-lee NOTA-LEIDA-reuniones-con-soporte@3
  - primera-frase incidencias@3
  - tabla Memoria · lectura@3
  - solo-escribe-en metodo.md
---
Una petición de «todo» se mide contra todo lo que pide (1.26.10). Las notas del taller de cuentas suman más de 70 KB, por
encima del tope de 50: el segundo turno pregunta antes de leer ninguna, con el tamaño de cada forma de leer (con la
herramienta de preguntas si la hay, en texto si no), y no abre ninguna. Con la parte elegida, el tercer turno lee solo esa
nota, entera, y la primera frase de la respuesta dice que cubre la de las incidencias; termina con el recuadro de lectura,
que nombra la otra en «Dejé fuera:». Es lo que en la prueba de la 1.26.3 se respondió con 30 KB de 619 sin preguntar.
