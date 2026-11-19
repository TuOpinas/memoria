---
estado: borrador
actualizado: AAAA-MM-DD
aportacion: "[Lo que este documento aporta, en una frase]"
basado_en: []
---

# Configuración de plataforma y repositorios

Lo imprescindible para que cada cambio se pueda rastrear y nadie libere directo a la rama principal. La mantiene quien administra y la comprueba quien audita al montar el proyecto y cada vez que algo de esto cambia. Dos proyectos que comparten plataforma apuntan al mismo archivo, y lo mantiene el proyecto donde vive.

En cada estado: `cumple · AAAA-MM-DD`, `no cumple · AAAA-MM-DD`, `no aplica` o `excepción`. El porqué de un `no aplica` y la decisión de una `excepción` van en una nota debajo de su tabla.

## Plataforma

| # | Qué se cumple | Cómo se comprueba | Estado |
|---|---|---|---|
| PL1 | GitHub es de la empresa, pide verificación en dos pasos y su plan permite reglas en repositorios privados | En GitHub, la organización → Settings → Authentication security y Billing | |
| PL2 | Dos personas pueden administrar GitHub | En GitHub, la organización → People → filtro Owners | |
| PL3 | El dominio y la nube están a nombre de la empresa | El titular en el registrador y en la facturación de la nube | |
| PL4 | Hay un entorno de Release separado de Prod | Los entornos de la nube | |
| PL5 | Los secretos viven en un gestor de secretos, nunca en el código | El gestor tiene las claves | |
| PL6 | La base de datos se respalda sola y la restauración se ha probado | Los respaldos de la nube y la fecha de la última prueba | |
| PL7 | Si Prod se cae, avisa a una persona | El servicio de monitoreo y a quién avisa | |

## Repositorios
Una columna por repositorio de la línea «Repositorios:».

| # | Qué se cumple | Cómo se comprueba | [organización/repositorio] |
|---|---|---|---|
| R1 | Nada llega a la rama principal sin pull request, se une con squash y nadie se salta la regla | En GitHub, el repositorio → Settings → Rules: la regla de la rama principal, sin excepciones; en General, solo squash | |
| R2 | Las pruebas pasan antes de unir, y el pull request de una pieza no cambia sus pruebas de aceptación | En la regla de la rama principal, las pruebas y «pruebas de aceptación» (`.github/workflows/pruebas-aceptacion.yml`) son obligatorias | |
| R3 | Ningún secreto entra en el código | En la regla de la rama principal, el control de secretos es obligatorio | |
| R4 | La base de datos cambia solo con migraciones nuevas, y una unida no se edita | Quien revisa el pull request; sin base de datos, `no aplica` | |
| R5 | A Prod solo despliega quien administra, y solo lo que tiene el sí, como dice «Paso a Prod» | Quién tiene permiso de desplegar en Prod | |
| R6 | Cada pull request, salvo los de bots, empieza por el identificador de su pieza, o por «Escenarios · » y la pieza | El apartado «fuera del plan» del último seguimiento | |
| R7 | El `CLAUDE.md` existe y tiene las reglas de la plantilla del kit | El archivo | |

Un cambio al workflow de las pruebas de aceptación va en su propio pull request, y lo revisa quien audita: en su pull request corre ya la versión cambiada.
