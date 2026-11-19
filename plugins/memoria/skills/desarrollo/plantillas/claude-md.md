# Plantilla de CLAUDE.md

Se copia a la raíz del repositorio como `CLAUDE.md` y se rellena la tabla. Debajo de las reglas va, libre, el contexto técnico del repositorio. Las reglas no se cambian sin una decisión del proyecto.

```markdown
# CLAUDE.md

| | |
|---|---|
| Qué es | [Una frase] |
| Proyecto en la memoria | [área/proyecto] |
| Diseño y plan | [rutas en la memoria] |
| Audita | [Nombre Apellido] |
| Cómo se revisa | [la skill calidad del plugin Memoria, o la que use el equipo] |
| Cómo se prueba | [comando] |
| Migraciones | [carpeta, o «no hay base de datos»] |
| No se toca | [lo que no se cambia nunca] |

## Reglas
1. Una rama por bloque (una o varias piezas) y nunca `main`. El título del pull request a `main` empieza por el identificador de su pieza, o por los de sus piezas unidos con « + », seguido de « · » («P03 · …», «P01 + P02 · …»).
2. Antes de abrir el pull request, la revisión de calidad, como dice «Cómo se revisa».
3. La base de datos cambia solo con una migración nueva; una ya unida no se edita.
4. Ningún secreto en el código.
5. No pases nada a Prod: lo hace quien administra, con el sí escrito.
6. Para y pregunta a quien audita antes de seguir, y escribe la pregunta y su respuesta en el pull request, cuando:
   - algo es difícil de revertir (un esquema, un contrato público, permisos, un proveedor, datos de clientes);
   - un enfoque falló dos veces;
   - la tarea añade una entidad, un componente o un concepto que no está en el diseño, o se sale del plan;
   - el diseño no cubre lo que la tarea necesita, o no puedes leerlo.

## Contexto técnico
[Arquitectura, módulos, pruebas, deuda conocida.]
```
