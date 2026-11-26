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
| Pruebas de aceptación | [carpeta, con los archivos de cada pieza como `<pieza>_<nombre>.py`, lista de piezas activas, cómo se corren las de una pieza y con qué código sale el ejecutor cuando fallan, los mismos que en .github/workflows/pruebas-aceptacion.yml, p. ej. `tests/aceptacion`, `.github/piezas-activas.txt`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTEST_ADDOPTS= PYTEST_PLUGINS= python3 -m pytest -c /dev/null --rootdir=. --confcutdir=tests/aceptacion -p no:cacheprovider tests/aceptacion/P01_*.py`, que no lee configuración de fuera de la carpeta (lo que necesiten va en un `conftest.py` de la carpeta, que no lleva `__init__.py`), `1`] |
| Migraciones | [carpeta, o «no hay base de datos»] |
| No se toca | [lo que no se cambia nunca] |

## Reglas
1. Una rama por bloque (una o varias piezas) y nunca `main`. El título del pull request empieza por el identificador de la pieza seguido de « · », o por las piezas que lleva («P01 + P02 · »); el de los escenarios de una pieza, por «Escenarios · P01», y el que solo cambia el kit (este archivo o el workflow), por «Kit · ». Una reversión lleva el título que le da GitHub («Revert "P01 · …"»).
2. Antes de abrir el pull request, la revisión de calidad, como dice «Cómo se revisa». El pull request dice con qué modelo se construyó («Construyó: Opus 5.5»).
3. La base de datos cambia solo con una migración nueva; una ya unida no se edita.
4. Ningún secreto en el código.
5. No pases nada a Prod: lo hace quien administra, con el sí escrito.
6. Para y pregunta a quien acepta antes de seguir, y escribe la pregunta y su respuesta en el pull request, cuando:
   - algo es difícil de revertir (un esquema, un contrato público, permisos, un proveedor, datos de clientes);
   - un enfoque falló dos veces;
   - la tarea añade una entidad, un componente o un concepto que no está en el diseño, o se sale del plan;
   - el diseño no cubre lo que la tarea necesita, o no puedes leerlo;
   - vas a construir algo que no entrega valor a quien usa el producto (un arnés, un generador, una imitación de otro sistema) y pasa de unas 200 líneas: di antes cuánto pesa y qué alternativa más barata hay.

   Si algo es difícil de revertir o se sale del diseño, consulta antes una vez a Fable 5.2 y lleva su respuesta a la pregunta. Si un enfoque falló dos veces, propón pasar la pieza a Fable 5.2.

**Hecha** quiere decir: pasan las pruebas de aceptación de la pieza y la suite de «Cómo se prueba» sigue en verde. El pull request de la pieza añade su identificador a la lista de piezas activas, y no toca la carpeta de aceptación; desde entonces CI exige que sus pruebas pasen, y solo la saca de la lista su pull request de escenarios, si cambian, o su reversión. Una pieza técnica, sin escenarios, no tiene pruebas ni entra en la lista. **Para** también si una prueba falla por una razón que no puedes explicar ni arreglar sin cambiarla, o si los escenarios contradicen el diseño.

**Cada afirmación de avance** («hecho», «pasa», «arreglado») va con la evidencia de una herramienta: la salida de las pruebas, el commit, el enlace.

## Contexto técnico
[Arquitectura, módulos, pruebas, deuda conocida.]
```
