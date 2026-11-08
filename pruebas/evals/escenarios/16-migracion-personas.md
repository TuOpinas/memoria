---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
max_turnos: 45
preparar:
  - "migrar"
turnos:
  - "Abre sesión en ventas/cuentas."
  - "Sí, migra ahora."
  - "Carla es Carla Prueba y Eva es Eva Prueba. El resto está bien."
comprobar:
  - recuadro
  - pregunta-antes 1
  - menciona Quién es quién@1
  - menciona Ana López@1
  - nada-hasta-el-turno 3 metodo.md
  - menciona carla@2
  - contiene guia.md ## Quién es quién
  - contiene guia.md - Carla Prueba · carla@ejemplo.test
  - contiene guia.md ## Versión mínima del plugin
  - contiene guia.md | Ana Prueba | Carla Prueba |
  - contiene operacion/soporte/proyecto.md Colabora: Dani Prueba
  - contiene operacion/soporte/sesiones.md (migracion)
  - solo-escribe-en ventas,operacion,archivo,personas,guia.md,metodo.md
  - sin-herramienta Write
  - sin-rutas-absolutas
---
La raíz de prueba está en la 1.22 con las personas como antes de la 1.25: correos en la columna «Cuenta» y «Nombre (correo)» en los proyectos. Ana es la responsable de contexto. Al abrir (turno 1), `abrir.py` dice «Personas: ANTERIOR en guia.md» y la respuesta es el recuadro y la pregunta de pasar a «Quién es quién», que nombra a Ana López, que cerró hace poco con el plugin 1.20.1; no escribe nada salvo `metodo.md`.
Con el sí (turno 2), corre `migrar_estructura.py --personas --plan`, enseña el registro y pregunta de una vez los nombres de carla@ejemplo.test y eva@ejemplo.test, que no salen de la raíz; tampoco escribe nada.
Con los nombres (turno 3), corre `migrar_estructura.py --personas --nombres …` sin `--plan`: `guia.md` lleva «Quién es quién», la columna «Colabora» con nombres y «Versión mínima del plugin»; el «Colabora:» de `operacion/soporte` queda con el nombre y deja su entrada `(migracion)`. No escribe nada a mano.
