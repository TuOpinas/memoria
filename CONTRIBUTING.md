# Contribuir

*Summary: issues are welcome. Pull requests are accepted for review only: the maintainer may reject them without explanation, and nobody else can write to `main`. Contributions are licensed under MIT. The TuOpinas name and logo are not licensed. No support, and no commitment to answer or to a timeline.*

## Issues

Son bienvenidos. Di la versión del plugin (`plugins/memoria/.claude-plugin/plugin.json`), qué hiciste, qué esperabas y qué pasó. No pegues contenido de la carpeta de tu organización, ni correos, ni nombres de clientes: si hace falta un ejemplo, usa uno inventado. No hay compromiso de respuesta ni de plazo.

## Pull requests

Se aceptan para revisión, no para fusión automática.

- Juanjo Jiménez-Alfaro los revisa y puede rechazarlos sin explicar el motivo. Que alguien revise un pull request no obliga a fusionarlo.
- `main` está protegida y nadie más tiene permiso de escritura: todo entra por pull request, desde una rama `version-X-Y-Z` o una de tu fork.
- Antes de abrirlo, corre lo de `pruebas/` que toque lo que cambias (con un Python 3.9 a mano, que `pruebas/probar_compila.py` usa para comprobar que los scripts corren en la computadora de cada persona: `uv python install 3.9`) (`pruebas/sesion/`, `pruebas/tablero/`, `pruebas/hook/`, `pruebas/verificar/`), y `plugins/memoria/verificar.sh` sobre una raíz de prueba si cambias el contrato. Los evals (`pruebas/evals/`) cuestan tokens y los corre quien publica.
- Antes del pull request de una versión, su revisión de calidad con la skill `calidad`, con el informe en `taller/revisiones-de-calidad/` del proyecto que mantiene el plugin: a fondo, con las seis lentes, una versión menor o mayor o un parche grande; errores y riesgos con dos revisores, un parche pequeño. Lo que impide o pone en riesgo el objetivo se arregla en la misma rama; lo demás va a la versión siguiente. `release.sh` no publica sin `--revisada <informe>`.
- No toques `metodo.md` a mano: se genera desde el plugin con `build-metodo.sh`.
- Un cambio por pull request, con el porqué en la descripción.

## Licencia de lo que aportas

Al enviar un pull request aceptas que tu aportación entra bajo la licencia MIT de este repositorio (`LICENSE`). El nombre TuOpinas y su logotipo no forman parte de esa licencia y no se pueden usar para presentar una adaptación como si fuera nuestra.
