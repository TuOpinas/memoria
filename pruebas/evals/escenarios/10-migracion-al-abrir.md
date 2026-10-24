---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 40
turnos:
  - "Abre sesión en ventas/cuentas."
  - "Sí, pásala a la nueva."
comprobar:
  - recuadro
  - apertura-completa ventas/cuentas
  - menciona 1.22@1
  - nada-hasta-el-turno 2 metodo.md
  - migrada ventas
  - migrada operacion
  - cambia guia.md
  - contiene guia.md | Acceso |
  - contiene ventas/cuentas/sesiones.md (migracion)
  - migrada personas
  - contiene personas/nomina/sesiones.md por Beto Prueba
  - pregunta-antes 1
  - solo-escribe-en ventas,operacion,archivo,personas,guia.md,metodo.md
  - sin-herramienta Write
  - sin-rutas-absolutas
---
La raíz de prueba sigue con la estructura de la 1.21. Al abrir, `abrir.py` dice «Estructura: ANTERIOR» para las áreas de Ana, para `personas/` (de Beto) y para `guia.md` (es la responsable de contexto), y la respuesta es el recuadro y la pregunta de migrar, antes de abrir el proyecto con sus focos, sin escribir nada (turno 1).
Con el sí (turno 2), corre `migrar_estructura.py` (primero con `--plan` y después sin él): migra las áreas de Ana, `personas/` de Beto y `guia.md`, y deja la entrada `(migracion)` en cada proyecto migrado; la de `personas/nomina` dice que la migró Ana por Beto. No escribe nada a mano.
