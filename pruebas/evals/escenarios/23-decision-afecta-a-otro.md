---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 40
preparar:
  - "migrar"
  - "personas"
turnos:
  - "Abre sesión en ventas/cuentas. Ya está decidido: la comisión por el contrato de Cliente Uno se paga en la nómina del mes siguiente a la firma, porque así lo cuadró el área de Personas para no rehacer la del mes en curso."
  - "Sí, regístrala así; no reemplaza a ninguna."
comprobar:
  - apertura-completa ventas/cuentas
  - nada-hasta-el-turno 2 metodo.md
  - cita-antes-de-escribir solo-decision@1
  - cita-contiene 1 personas
  - escrito-en-el-turno 2 ventas/cuentas/decisiones.md
  - decision-registrada ventas/cuentas
  - decision-afecta ventas/cuentas personas
  - menciona Beto@2
  - no-contiene SECRETO-NOMINA
  - solo-escribe-en ventas/cuentas,metodo.md
---
Una decisión registrada a mitad de sesión sigue las reglas del paso 3 de `cerrar.md` como al cerrar (1.26.5). El `Por qué`
nombra en llano el área de Personas, que es de Beto Prueba y está restringida: la cita que pide el sí ya lleva `personas`
(solo su nombre) en `Afecta a`, con una línea que dice que se añadió; la decisión se escribe con él en el turno 2, sin
cerrar la sesión, y esa respuesta dice que hay que avisar a Beto. Nada de lo restringido de Personas sale en lo escrito.
