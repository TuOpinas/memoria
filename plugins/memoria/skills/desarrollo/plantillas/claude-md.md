# Plantilla de CLAUDE.md

Se copia a la raíz del repositorio como `CLAUDE.md` y se rellena la tabla. Debajo de las reglas va, libre, el contexto técnico del repositorio. Las reglas no se cambian sin una decisión del proyecto.

```markdown
# CLAUDE.md

| | |
|---|---|
| Qué es | [Una frase] |
| Proyecto en la memoria | [área/proyecto] |
| Diseño y plan | [rutas en la memoria] |
| Acepta | [Nombre Apellido] |
| Cómo se revisa | [la skill calidad del plugin Memoria, o la que use el equipo] |
| Cómo se prueba | [comando de la suite de pruebas del código, que deja fuera la carpeta de aceptación, p. ej. `pytest --ignore=tests/aceptacion`] |
| Pruebas de aceptación | [carpeta, lista de piezas activas y corredor, los mismos que `ACEPTACION`, `ACTIVAS` y `CORREDOR` en .github/workflows/pruebas-aceptacion.yml, y cómo se llaman los archivos de cada pieza. Con pytest, p. ej. `tests/aceptacion`, `.github/piezas-activas.txt`, `pytest`, archivos `<pieza>_<nombre>.py`, que no leen configuración de fuera de la carpeta (lo que necesiten va en un `conftest.py` de la carpeta, que no lleva `__init__.py`); fuera del control, el mismo comando que el control, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTEST_ADDOPTS= PYTEST_PLUGINS= python3 -c 'import os, sys; c = os.path.realpath("."); sys.path[:] = [p for p in sys.path if os.path.realpath(p or ".") != c] + [c]; import pytest; sys.exit(pytest.console_main())' -c /dev/null --rootdir=. --confcutdir=tests/aceptacion -p no:cacheprovider --continue-on-collection-errors -r fEsxXp tests/aceptacion/P01_*.py`. Con Vitest, `vitest`, archivos `<pieza>_<nombre>.test.ts` y la configuración de `CONFIG`, dentro de la carpeta; fuera del control, `npx --no-install vitest run --config tests/aceptacion/vitest.config.ts --root . tests/aceptacion/P01_*.test.ts`. Con un corredor propio, su ruta (`./scripts/corredor`) y el final de sus archivos (`SUFIJO`, p. ej. `_test.go`); fuera del control, `./scripts/corredor tests/aceptacion/P01_*_test.go`] |
| Migraciones | [carpeta, o «no hay base de datos»] |
| No se toca | [lo que no se cambia nunca] |

## Reglas
1. Una rama por bloque (una o varias piezas) y nunca `main`. El título del pull request empieza por el identificador de la pieza seguido de « · », o por las piezas que lleva («P01 + P02 · »); el de los escenarios de una pieza, por «Escenarios · P01», y el que solo cambia el kit (este archivo, el workflow, el corredor propio o la configuración del repositorio), por «Kit · »: el workflow es el de las pruebas de aceptación y los demás de `.github/workflows/`, y la configuración del repositorio, `CODEOWNERS` (en la raíz, `.github/` o `docs/`) y `.github/dependabot.yml` (o `.yaml`); salvo si solo cambia workflows, que pasa con cualquier título (el «Bump …» de Dependabot), sin código. Un identificador de pieza puede acabar en una letra (`H22a`). Una reversión lleva el título que le da GitHub («Revert "P01 · …"»).
2. Antes de abrir el pull request, la revisión de calidad, como dice «Cómo se revisa». El pull request dice con qué modelo se construyó («Construyó: Opus 5.5»).
3. La base de datos cambia solo con una migración nueva; una ya unida no se edita.
4. Ningún secreto en el código.
5. No pases nada a Prod: lo hace quien administra, con el sí escrito.
6. Para y pregunta a quien acepta antes de seguir, y escribe la pregunta y su respuesta en el pull request, cuando:
   - algo es difícil de revertir (un esquema, un contrato público, permisos, un proveedor, datos de clientes);
   - el cambio toca lo delicado, que quien acepta revisa antes de unir (una dependencia nueva, permisos, accesos, pagos, datos personales, un cambio de base de datos);
   - un enfoque falló dos veces;
   - la tarea añade una entidad, un componente o un concepto que no está en el diseño, o se sale del plan;
   - el diseño no cubre lo que la tarea necesita, o no puedes leerlo;
   - vas a construir algo que no entrega valor a quien usa el producto (un arnés, un generador, una imitación de otro sistema) y pasa de unas 200 líneas: di antes cuánto pesa y qué alternativa más barata hay.

   Si algo es difícil de revertir o se sale del diseño, consulta antes una vez al modelo de `consulta` de la línea «Modelos:» del proyecto (si la línea no lo nombra, el de la plantilla de la sección; nunca el que construye) y lleva su respuesta a la pregunta; si no está disponible, dilo, y quien acepta decide si se espera, se consulta a otro o se sigue sin consulta, con la nota «Consulta no disponible: <motivo>; decidió <Nombre Apellido>» en el pull request. Si un enfoque falló dos veces, propón pasar la pieza a ese modelo.

**Hecha** quiere decir: pasan las pruebas de aceptación de la pieza y la suite de «Cómo se prueba» sigue en verde. El pull request de la pieza añade su identificador a la lista de piezas activas, y no toca la carpeta de aceptación; una pieza con el código ya construido la añade su pull request de escenarios, y sus pruebas tienen que pasar en él. Desde entonces CI exige que sus pruebas pasen, y solo la saca de la lista su pull request de escenarios, si cambian, o su reversión. Una pieza técnica, sin escenarios, no tiene pruebas ni entra en la lista. **Para** también si una prueba falla por una razón que no puedes explicar ni arreglar sin cambiarla, o si los escenarios contradicen el diseño.

**Cada afirmación de avance** («hecho», «pasa», «arreglado») va con la evidencia de una herramienta: la salida de las pruebas, el commit, el enlace.

## Contexto técnico
[Arquitectura, módulos, pruebas, deuda conocida.]
```
