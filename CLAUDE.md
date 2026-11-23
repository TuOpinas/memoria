# CLAUDE.md

| | |
|---|---|
| Qué es | El plugin `memoria` de Claude, que aplica el método Memoria: una memoria de trabajo compartida en una carpeta |
| Proyecto en la memoria | `shared-memory/plugin-memoria`, en la raíz de TuOpinas |
| Diseño y plan | `shared-memory/plugin-memoria/entregables/plan.md`. Diseño por crear: mientras tanto hacen de diseño el contrato del método (`plugins/memoria/skills/convenciones/`) y las plantillas del kit (`plugins/memoria/skills/desarrollo/plantillas/`), y la regla 6 se aplica contra ellos |
| Audita | Juanjo Jiménez-Alfaro |
| Cómo se revisa | La skill `calidad` del plugin, con el informe en `taller/revisiones-de-calidad/` del proyecto; la descripción del pull request lo nombra en su línea «Revisión de calidad:» (check `Revisión`) |
| Cómo se prueba | Todo `.github/workflows/pruebas.yml`: los secretos, `python3 pruebas/probar_compila.py`, las de `packages/context-core/` (`unittest` e `inline.py --check`), cada `pruebas/sesion/probar_*.py` y los de `pruebas/tablero/`, con Python 3.9, 3.10 y el actual. No corre `pruebas/aceptacion/` |
| Pruebas de aceptación | `pruebas/aceptacion/<pieza>_<nombre>.py` (la pieza, «_» y un nombre: `P01_seleccion_exacta.py`) con su `RESUMEN.md`; para una pieza que hace el modelo sin script, un eval `pruebas/evals/escenarios/NN-<pieza>-<nombre>.md` (la pieza en mayúsculas, entre guiones: `30-P04-aprobacion-citada.md`), con sus datos al lado con el mismo comienzo (`30-P04-aprobacion-citada.json`). Lista de piezas activas: `.github/piezas-activas.txt`. Se corren con `python3 -I pruebas/aceptacion/correr.py P01 P02`, que sale con `0` si pasan, `1` si fallan o se saltan y `2` si no se pudieron correr; las de P01–P03 necesitan pytest en el `python3` del PATH. Las corre `.github/workflows/pruebas-aceptacion.yml`, y a ese workflow lo prueba `pruebas/sesion/probar_aceptacion_memoria.py` (decisiones shared-memory/plugin-memoria#2026-11-22-3 y -9) |
| Migraciones | No hay base de datos |
| No se toca | `metodo.md` a mano (lo genera `build-metodo.sh`); el número de versión a mano: lo sube `release.sh` en todos sus sitios, y a mano solo van la entrada del README y la línea de versión del contrato |

## Reglas
1. Nunca se escribe en `main`: todo entra por pull request. Las piezas de una versión se construyen en su rama, `version-X-Y-Z`, y el pull request de versión a `main` lleva en su título las piezas que entrega, con « · » detrás («P01 + P02 + P03 · 1.27.1»). Los escenarios de una pieza salen de su propia rama en un pull request a `main` titulado «Escenarios · P01», que solo cambia los archivos de las piezas de su título. El kit (este archivo, el workflow de aceptación, `pruebas/aceptacion/correr.py` y `flujo.py`, y `pruebas/sesion/probar_aceptacion_memoria.py`) va solo, en un pull request «Kit · ». Los de escenarios y los de kit los une quien acepta. Una reversión lleva el título que le da GitHub («Revert "P01 · …"»).
2. Antes de abrir el pull request, la revisión de calidad, como dice «Cómo se revisa». El pull request dice con qué modelo se construyó («Construyó: Opus 5.5»).
3. La base de datos cambia solo con una migración nueva; una ya unida no se edita. (Este repositorio no tiene base de datos.)
4. Ningún secreto en el código.
5. No pases nada a Prod: aquí unir el pull request de versión publica el plugin. Lo une quien administra, con el sí en su descripción en la línea «Aprobó: Nombre Apellido, AAAA-MM-DD», después de verificar la candidata instalada en una raíz de prueba de TuOpinas.
6. Para y pregunta a quien audita antes de seguir, y escribe la pregunta y su respuesta en el pull request, cuando:
   - algo es difícil de revertir (un esquema, un contrato público, permisos, un proveedor, datos de clientes);
   - un enfoque falló dos veces;
   - la tarea añade una entidad, un componente o un concepto que no está en el diseño, o se sale del plan;
   - el diseño no cubre lo que la tarea necesita, o no puedes leerlo.

   Si algo es difícil de revertir o se sale del diseño, consulta antes una vez a Fable 5.2 y lleva su respuesta a la pregunta. Si un enfoque falló dos veces, propón pasar la pieza a Fable 5.2.

**Hecha** quiere decir: pasan las pruebas de aceptación de la pieza y la suite de «Cómo se prueba» sigue en verde. El pull request de versión añade a la lista de piezas activas las piezas que tienen archivos en `pruebas/aceptacion/`, y no toca los escenarios; desde entonces CI exige que sus pruebas pasen, y solo saca una pieza de la lista el pull request de escenarios que cambia sus pruebas, o su reversión. Una pieza cuya prueba es un eval no entra en la lista: su pull request de escenarios nombra el eval en la línea «Evals:» de la descripción y tiene que fallar al correrlo con la etiqueta `evals`; el pull request de versión lo nombra igual y tiene que pasar antes del sí. Una pieza técnica, sin escenarios, no tiene pruebas ni entra en la lista. **Para** también si una prueba falla por una razón que no puedes explicar ni arreglar sin cambiarla, o si los escenarios contradicen el diseño.

**Lo que el check no cierra**: el código que importan las pruebas corre en su proceso y podría hacer trampa; el workflow que juzga un pull request es el que ese pull request trae; una reversión se reconoce por su título y por el asunto del commit que nombra, no por lo que deshace; y la excepción de Dependabot mira quién abrió el pull request. Por eso el kit va solo y lo une quien acepta, y lo demás lo ven quien une, la verificación sobre la candidata y el seguimiento. El check «pruebas de aceptación» cuenta solo si la regla de `main` lo tiene como obligatorio, y eso lo marca quien administra.

**Cada afirmación de avance** («hecho», «pasa», «arreglado») va con la evidencia de una herramienta: la salida de las pruebas, el commit, el enlace.

## Contexto técnico
- `plugins/memoria/`: el plugin. `skills/` (cada skill con su `SKILL.md`, anexos y scripts), `agents/` (los subagentes del kit de desarrollo, con su modelo fijado), `hooks/` (el aviso de arranque y los controles), `metodo.md` (generado), `release.sh` (prepara una versión en su rama y sube su número en todos sus sitios; no lo hace sin `--revisada <informe>`; publicar es unir), `verificar.sh` (revisa una raíz).
- `packages/context-core/`: las reglas que comparten los scripts, metidas en cada script con `inline.py`.
- `pruebas/`: las de cada parte (`sesion/`, `tablero/`, `hook/`, `verificar/`), los evals (`evals/`, cuestan tokens y los corre quien publica; su arnés y los escenarios sin pieza van con cualquier pull request) y las de aceptación (`aceptacion/`).
- Los scripts corren en la computadora de cada persona con el Python que tenga: todo tiene que correr con Python 3.9.
- `CONTRIBUTING.md` dice cómo se contribuye desde fuera.
