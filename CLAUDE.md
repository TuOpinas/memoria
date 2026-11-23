# CLAUDE.md

| | |
|---|---|
| Qué es | El plugin `memoria` de Claude, que aplica el método Memoria: una memoria de trabajo compartida en una carpeta |
| Proyecto en la memoria | `shared-memory/plugin-memoria`, en la raíz de TuOpinas |
| Diseño y plan | `shared-memory/plugin-memoria/entregables/plan.md`; diseño por crear |
| Audita | Juanjo Jiménez-Alfaro |
| Cómo se revisa | La skill `calidad` del plugin, con el informe en `taller/revisiones-de-calidad/` del proyecto; la descripción del pull request lo nombra en su línea «Revisión de calidad:» (check `Revisión`) |
| Cómo se prueba | `.github/workflows/pruebas.yml`: `python3 pruebas/probar_compila.py`, cada `pruebas/sesion/probar_*.py` y los de `pruebas/tablero/`, con Python 3.9, 3.10 y el actual. No corre `pruebas/aceptacion/` |
| Pruebas de aceptación | `pruebas/aceptacion/` (un archivo `<pieza>_<nombre>.py` por pieza) y, para una pieza que hace el modelo sin script, un escenario de `pruebas/evals/escenarios/` con la pieza en su nombre. Lista de piezas activas: `.github/piezas-activas.txt`. Se corren con `python3 -I pruebas/aceptacion/correr.py P01 P02`, que sale con `1` cuando fallan y con `2` si no se pudieron correr. Las corre `.github/workflows/pruebas-aceptacion.yml` (decisiones shared-memory/plugin-memoria#2026-11-22-3 y -8) |
| Migraciones | No hay base de datos |
| No se toca | `metodo.md` a mano (lo genera `build-metodo.sh`); el número de versión fuera de `plugin.json`, la línea de versión del contrato y el README, que dicen el mismo |

## Reglas
1. Una rama por versión, `version-X-Y-Z`, y nunca `main`. Las piezas de la versión se construyen ahí. El pull request de versión a `main` lleva en su título las piezas que entrega, con « · » detrás («P01 + P02 + P03 · 1.27.1»). El de los escenarios de una pieza empieza por «Escenarios · P01» y va directo a `main`. El que solo cambia el kit (este archivo o el workflow de aceptación) empieza por «Kit · ». Una reversión lleva el título que le da GitHub («Revert "P01 · …"»).
2. Antes de abrir el pull request, la revisión de calidad, como dice «Cómo se revisa». El pull request dice con qué modelo se construyó («Construyó: Opus 5.5»).
3. La base de datos cambia solo con una migración nueva; una ya unida no se edita. (Este repositorio no tiene base de datos.)
4. Ningún secreto en el código.
5. No pases nada a Prod: aquí unir el pull request de versión publica el plugin. Lo une quien administra, con el sí escrito, después de verificar la candidata instalada en una raíz de prueba de TuOpinas.
6. Para y pregunta a quien audita antes de seguir, y escribe la pregunta y su respuesta en el pull request, cuando:
   - algo es difícil de revertir (un esquema, un contrato público, permisos, un proveedor, datos de clientes);
   - un enfoque falló dos veces;
   - la tarea añade una entidad, un componente o un concepto que no está en el diseño, o se sale del plan;
   - el diseño no cubre lo que la tarea necesita, o no puedes leerlo.

   Si algo es difícil de revertir o se sale del diseño, consulta antes una vez a Fable 5.2 y lleva su respuesta a la pregunta. Si un enfoque falló dos veces, propón pasar la pieza a Fable 5.2.

**Hecha** quiere decir: pasan las pruebas de aceptación de la pieza y la suite de «Cómo se prueba» sigue en verde. El pull request de versión añade a la lista de piezas activas las piezas que tienen archivos en `pruebas/aceptacion/`, y no toca `pruebas/aceptacion/` ni `pruebas/evals/`; desde entonces CI exige que sus pruebas pasen, y solo saca una pieza de la lista su pull request de escenarios, si cambian, o su reversión. Una pieza cuya prueba es un eval no entra en la lista: su eval se corre con la etiqueta `evals` antes del sí. Una pieza técnica, sin escenarios, no tiene pruebas ni entra en la lista. **Para** también si una prueba falla por una razón que no puedes explicar ni arreglar sin cambiarla, o si los escenarios contradicen el diseño.

**Cada afirmación de avance** («hecho», «pasa», «arreglado») va con la evidencia de una herramienta: la salida de las pruebas, el commit, el enlace.

## Contexto técnico
- `plugins/memoria/`: el plugin. `skills/` (cada skill con su `SKILL.md`, anexos y scripts), `agents/` (los subagentes del kit de desarrollo, con su modelo fijado), `hooks/` (el aviso de arranque y los controles), `metodo.md` (generado), `release.sh` (publica una versión: no lo hace sin `--revisada <informe>`), `verificar.sh` (revisa una raíz).
- `packages/context-core/`: las reglas que comparten los scripts, metidas en cada script con `inline.py`.
- `pruebas/`: las de cada parte (`sesion/`, `tablero/`, `hook/`, `verificar/`), los evals (`evals/`, cuestan tokens y los corre quien publica) y las de aceptación (`aceptacion/`).
- Los scripts corren en la computadora de cada persona con el Python que tenga: todo tiene que correr con Python 3.9.
- `CONTRIBUTING.md` dice cómo se contribuye desde fuera.
