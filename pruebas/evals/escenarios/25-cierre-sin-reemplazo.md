---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 40
preparar:
  - "sustituir ventas/cuentas/decisiones.md \n## Decisión recuperada sin fecha => \n## 2025-11-15 · El anexo de Cliente Uno se firma en papel\nDecidió: Ana Prueba\nPor qué: su área legal no acepta firma electrónica.\n\n## Decisión recuperada sin fecha"
  - "migrar"
  - "personas"
turnos:
  - "Abre sesión en ventas/cuentas. Decidimos que el anexo de Cliente Uno lo firma su director comercial, porque es quien tiene poder notarial. Cierra la sesión."
  - "Sí."
comprobar:
  - apertura-completa ventas/cuentas
  - no-menciona-re ¿Reemplaza a alguna|[Ll]leva «Reemplaza»|[Cc]reo que reemplaza@1
  - nada-hasta-el-turno 2 metodo.md
  - decision-registrada ventas/cuentas
  - decision-sin-reemplaza ventas/cuentas
  - cierre-con-script
  - solo-escribe-en ventas/cuentas,ventas/area.md,metodo.md
  - recuadro-cierre
---
El caso contrario del 17 (1.26.7). `cerrar.py --comprobar` devuelve en `parecidas` una decisión anterior de título
parecido («El anexo de Cliente Uno se firma en papel») que no choca con la nueva: una dice quién firma y la otra cómo. La
sesión lee esa entrada y no dice nada: ni la lista, ni «¿Reemplaza a alguna?», ni una propuesta. La decisión se escribe sin
`Reemplaza:`.
