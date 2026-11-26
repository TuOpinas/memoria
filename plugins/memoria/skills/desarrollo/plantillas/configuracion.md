---
estado: borrador
actualizado: AAAA-MM-DD
aportacion: "[Lo que este documento aporta, en una frase]"
basado_en: []
---

# Configuración de plataforma y repositorios

Lo imprescindible para que cada cambio se pueda rastrear y nadie libere directo a la rama principal. La mantiene quien administra y la comprueba quien acepta al montar el proyecto y cada vez que algo de esto cambia. Dos proyectos que comparten plataforma apuntan al mismo archivo, y lo mantiene el proyecto donde vive.

En cada estado: `cumple · AAAA-MM-DD`, `no cumple · AAAA-MM-DD`, `no aplica` o `excepción`. El porqué de un `no aplica` y la decisión de una `excepción` van en una nota debajo de su tabla.

## Plataforma

| # | Qué se cumple | Cómo se comprueba | Estado |
|---|---|---|---|
| PL1 | GitHub es de la empresa, pide verificación en dos pasos y su plan permite reglas en repositorios privados | En GitHub, la organización → Settings → Authentication security y Billing | |
| PL2 | Dos personas pueden administrar GitHub | En GitHub, la organización → People → filtro Owners | |
| PL3 | El dominio y la nube están a nombre de la empresa | El titular en el registrador y en la facturación de la nube | |
| PL4 | Hay un entorno de Release separado de Prod | Los entornos de la nube; con `no aplica`, la verificación corre sobre una vista previa o en local | |
| PL5 | Los secretos viven en un gestor de secretos, nunca en el código | El gestor tiene las claves | |
| PL6 | La base de datos se respalda sola y la restauración se ha probado | Los respaldos de la nube y la fecha de la última prueba | |
| PL7 | Si Prod se cae, avisa a una persona | El servicio de monitoreo y a quién avisa | |

## Repositorios
Una columna por repositorio de la línea «Repositorios:».

| # | Qué se cumple | Cómo se comprueba | [organización/repositorio] |
|---|---|---|---|
| R1 | Nada llega a la rama principal sin pull request, se une con squash y nadie se salta la regla | En GitHub, el repositorio → Settings → Rules: la regla de la rama principal, sin excepciones; en General, solo squash | |
| R2 | Las pruebas pasan antes de unir, también las de aceptación de las piezas activas; el pull request de una pieza no cambia las suyas, y uno que toca las pruebas de aceptación o su workflow lo une o lo aprueba quien acepta | En la regla de la rama principal, la suite de «Cómo se prueba», que deja fuera la carpeta de aceptación, y el check «pruebas de aceptación» (`.github/workflows/pruebas-aceptacion.yml`, con su carpeta, su lista y su comando puestos, y el comando sin leer configuración del ejecutor de fuera de la carpeta, que un pull request de código podría cambiar: con pytest, el de la plantilla y su paso con `PYTEST_DISABLE_PLUGIN_AUTOLOAD`, `PYTEST_ADDOPTS` y `PYTEST_PLUGINS`; con otro ejecutor, quien acepta revisa qué lee de fuera) son obligatorios; si quien acepta no es quien construye y tiene cuenta, un `CODEOWNERS` le pone en la carpeta y el workflow (la lista no: cada pieza se añade en su propio pull request, y quitar una solo lo deja CI a su pull request de escenarios o a su reversión), con la revisión de propietarios obligatoria | |
| R3 | Ningún secreto entra en el código | En la regla de la rama principal, el control de secretos es obligatorio | |
| R4 | La base de datos cambia solo con migraciones nuevas, y una unida no se edita | Quien revisa el pull request; sin base de datos, `no aplica` | |
| R5 | A Prod solo despliega quien administra, y solo lo que tiene el sí, como dice «Paso a Prod» | Quién tiene permiso de desplegar en Prod | |
| R6 | Cada pull request, salvo los de bots, empieza por el identificador de su pieza, por «Escenarios · » y la pieza, o por «Kit · » si solo cambia el `CLAUDE.md` o el workflow; una reversión, con el título que le da GitHub | El apartado «fuera del plan» del último seguimiento | |
| R7 | El `CLAUDE.md` existe y tiene las reglas de la plantilla del kit | El archivo | |

**Al montar** un repositorio, el `CLAUDE.md` y el workflow van en un pull request «Kit · », en cualquier orden con los primeros escenarios: mientras no exista la carpeta de aceptación, el check pasa. Después, un cambio al workflow va en su propio pull request («Kit · »), sin código, y lo une o lo aprueba quien acepta: si va con otra cosa, el propio check falla, pero en su pull request corre ya la versión cambiada, así que el seguimiento lista cada pull request que tocó el workflow o las pruebas de aceptación, con quién lo unió o lo aprobó.

## Verificación
Dónde encuentra la verificación la aplicación antes del sí (decisión tecnologia/metodologia-desarrollo#2026-11-19-8).

| | |
|---|---|
| Dónde corre | [Release; sin Release, la aplicación levantada desde el commit unido, con su comando; si unir publica, la candidata instalada en una raíz o un entorno de prueba] |
| Cuentas de prueba | [cuáles, y quién las da] |
| Datos de prueba | [de dónde salen, nunca de clientes] |
