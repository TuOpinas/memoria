---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 50
preparar:
  - "migrar"
  - "personas"
  - "nota ventas/cuentas/taller/incidencias-cliente-uno.md 55 Lo que soporte pidió a cuentas en cada incidencia de Cliente Uno"
turnos:
  - "¿Cómo va ventas/cuentas?"
  - "¿Lo que decidimos en cuentas cuadra con lo que decidió soporte?"
  - "Sí."
comprobar:
  - apertura-completa ventas/cuentas
  - sin-tabla Memoria · lectura@1
  - tabla-al-final Memoria · lectura@2
  - menciona soporte@2
  - no-menciona-re (?m)^\W*lectura\W{0,3}:
  - no-menciona-re lectura · (?:de |nivel )?(?:proyecto|a fondo|básico)\b
  - pregunta-leer incidencias@2
  - no-lee NOTA-LEIDA-incidencias-cliente-uno@2
  - lee NOTA-LEIDA-incidencias-cliente-uno@3
  - tabla Memoria · lectura@3
  - solo-escribe-en metodo.md
  - sin-rutas-absolutas
---
Cuánto se lee y cómo se ve (1.26.3; el recuadro, 1.26.10). La primera pregunta se responde con lo que imprimió la apertura
(nivel básico): sin recuadro de lectura. La segunda cruza proyectos: la respuesta lee las decisiones de cuentas y la
superficie pública de `operacion/soporte`, y termina con el recuadro «Memoria · lectura · …», con sus filas «Leí:» y «Dejé
fuera:», que dice de dónde leyó en llano, sin «Lectura:» ni el nombre de un nivel. La nota de las incidencias de Cliente
Uno, de 55 KB y en el taller de cuentas, no la nombra la pregunta: Claude la encuentra en el inventario de la apertura, y
como pasa del tope de 50 KB y podría completar la respuesta, queda en «Dejé fuera:» y debajo del recuadro se ofrece leerla,
en texto, sin abrirla. Con el «sí» del tercer turno se lee entera y la respuesta lleva otra vez su recuadro. Nada se
escribe salvo `metodo.md`.
