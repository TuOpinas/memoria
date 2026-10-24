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
  - contiene personas/area.md ## Panorama
  - solo-escribe-en ventas,operacion,archivo,guia.md,metodo.md
  - sin-herramienta Write
  - sin-rutas-absolutas
---
La raíz de prueba sigue con la estructura de la 1.21. Al abrir, `abrir.py` dice «Estructura: ANTERIOR» para las áreas de Ana y para `guia.md` (es la responsable de contexto), y la respuesta lo ofrece en una línea, sin escribir nada (turno 1).
Con el sí (turno 2), corre `migrar_estructura.py` (primero con `--plan` y después sin él): migra solo las áreas de Ana y `guia.md`, deja la entrada `(migracion)` en cada proyecto migrado y no toca `personas/`, que es de Beto. No escribe nada a mano.
