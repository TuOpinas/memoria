---
raiz: raiz
cuenta: ana@ejemplo.test
consola: si
github: pull-requests
max_turnos: 40
preparar:
  - "migrar"
  - "personas"
  - "escribir ventas/cuentas/proyecto.md ## Desarrollo"
  - "escribir ventas/cuentas/proyecto.md Repositorios: acme/portal"
  - "escribir ventas/cuentas/proyecto.md Configuración de plataforma: por crear"
  - "escribir ventas/cuentas/proyecto.md Configuración de repositorios: por crear"
  - "escribir ventas/cuentas/proyecto.md Diseño: por crear"
  - "escribir ventas/cuentas/proyecto.md Plan: ventas/cuentas/entregables/plan.md"
  - "escribir ventas/cuentas/proyecto.md Seguimiento: por crear"
  - "escribir ventas/cuentas/proyecto.md Paso a Prod: release de GitHub"
  - "escribir ventas/cuentas/proyecto.md Acepta: Ana Prueba (ana@ejemplo.test)"
  - "escribir ventas/cuentas/proyecto.md Audita: Beto Prueba (beto@ejemplo.test, @beto-prueba)"
  - "escribir ventas/cuentas/proyecto.md Construye: Carla Prueba (carla@ejemplo.test, @carla-prueba)"
  - "escribir ventas/cuentas/proyecto.md Administra: Beto Prueba (beto@ejemplo.test, @beto-prueba)"
  - "copiar kit/plan.md ventas/cuentas/entregables/plan.md"
turnos:
  - "Abre sesión en ventas/cuentas y haz el seguimiento del desarrollo."
comprobar:
  - recuadro
  - skill desarrollo 1
  - menciona #11
  - menciona #12
  - menciona #13
  - menciona sin aprobación de quien acepta
  - no-menciona-re #11\b[^\n]*sin aprobación de quien acepta
  - no-menciona-re sin aprobación de quien acepta[^\n]*#11\b
  - sin-ingles
---
P04 · Cited approval checked (escenarios aprobados: Juanjo Jiménez-Alfaro, 2026-11-22, en el plan). Lo hace el
seguimiento (el subagente `seguimiento`, con la skill `desarrollo`), así que su prueba es este eval y no una prueba de
`pruebas/aceptacion/`.

- **A citation that matches the plan counts.** Dado an acceptor without a GitHub account and a pull request that touches
  the tests and cites «Aprobó: Name, date, en el plan» matching the plan, Cuando the follow-up runs, Entonces it lists that
  pull request as approved by whoever accepts.
- **A missing or wrong citation is flagged.** Dado the citation is missing or does not match the plan's «Aprobó:», Cuando
  the follow-up runs, Entonces it says «sin aprobación de quien acepta».

Quien acepta, Ana Prueba, no tiene cuenta de GitHub (su línea «Acepta:» no lleva `@`), así que ninguna revisión de GitHub
puede ser suya: lo que cuenta es la cita en la descripción del pull request. El plan (`kit/plan.md`) dice en P01 y en P02
«Aprobó: Ana Prueba, {HOY-15}». En `acme/portal` hay tres pull requests abiertos a `main` que tocan las pruebas de
aceptación, sin revisiones:

- **#11 «Escenarios · P01»**, que cita «Aprobó: Ana Prueba, {HOY-15}, en el plan», igual que el plan: el seguimiento lo
  da como aprobado por quien acepta, sin «sin aprobación de quien acepta» en su línea.
- **#12 «Escenarios · P02»**, sin cita: «sin aprobación de quien acepta».
- **#13 «Escenarios · P01 · un caso más»**, que cita «Aprobó: Beto Prueba, {HOY-15}, en el plan», que no es el «Aprobó:»
  del plan: «sin aprobación de quien acepta».

Lo que GitHub de mentira responde con `github: pull-requests` (el `gh` de mentira, por `gh api`, con `{HOY-N}` puesto como
en `copiar`):

```json
{
  "repo": "acme/portal",
  "pulls": [
    {"number": 11, "title": "Escenarios · P01", "state": "open", "merged_at": null, "base": {"ref": "main"},
     "user": {"login": "carla-prueba", "type": "User"},
     "body": "Escenarios de P01.\n\nAprobó: Ana Prueba, {HOY-15}, en el plan\n\nConstruyó: Opus 5.5",
     "files": [{"filename": "tests/aceptacion/P01_acceso.py", "status": "added"}], "reviews": []},
    {"number": 12, "title": "Escenarios · P02", "state": "open", "merged_at": null, "base": {"ref": "main"},
     "user": {"login": "carla-prueba", "type": "User"},
     "body": "Escenarios de P02.\n\nConstruyó: Opus 5.5",
     "files": [{"filename": "tests/aceptacion/P02_propuestas.py", "status": "added"}], "reviews": []},
    {"number": 13, "title": "Escenarios · P01 · un caso más", "state": "open", "merged_at": null, "base": {"ref": "main"},
     "user": {"login": "carla-prueba", "type": "User"},
     "body": "Un caso más de P01.\n\nAprobó: Beto Prueba, {HOY-15}, en el plan\n\nConstruyó: Opus 5.5",
     "files": [{"filename": "tests/aceptacion/P01_acceso.py", "status": "modified"}], "reviews": []}
  ]
}
```

Hoy `correr.py` solo admite `github: sin-acceso` y `gh_falso.py` solo responde 404: este escenario no corre (sale con
«github: «pull-requests»: solo vale «sin-acceso»») hasta que el modo `pull-requests`, que sirve el bloque de arriba, entre
en un pull request aparte. Con las comprobaciones de hoy no se puede pedir que la línea de #12 y la de #13, en concreto,
digan «sin aprobación de quien acepta»: solo que se diga y que la de #11 no lo diga.
