---
raiz: raiz
cuenta: ana@ejemplo.test
consola: no
max_turnos: 80
turnos:
  - "Abre sesión en ventas/cuentas."
  - "Sí, pásala a la nueva."
comprobar:
  - recuadro
  - apertura-completa ventas/cuentas
  - menciona 1.22@1
  - herramienta device_stage_files
  - herramienta device_commit_files
  - migrada ventas
  - migrada operacion
  - cambia guia.md
  - contiene guia.md | Acceso |
  - contiene ventas/cuentas/sesiones.md (migracion)
  - contiene ventas/cuentas/sesiones.md sin consola
  - contiene personas/area.md ## Panorama
  - solo-escribe-en ventas,operacion,archivo,guia.md,metodo.md
  - sin-herramienta Write
  - sin-rutas-absolutas
---
El 10 en Windows sin consola. Al abrir, `abrir.py` corre sobre la copia y dice «Estructura: ANTERIOR» para las áreas de Ana y
`guia.md`, y la respuesta lo ofrece en una línea (turno 1). Con el sí (turno 2) sigue «Sin consola» de `migracion.md`: lista las
áreas, arma la copia con `espejo.py migracion`, corre el plan, trae y registra lo que cambia, migra la copia con
`--sin-consola`, comprueba con `--hecha` y devuelve con `device_commit_files`, los archivos nuevos del taller primero. La raíz de
prueba no tiene `enlaces.md`, así que no hay nada que renombrar ni hace falta el conector. No toca `personas/`, que es de Beto.
