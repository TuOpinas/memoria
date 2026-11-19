---
estado: borrador
actualizado: AAAA-MM-DD
aportacion: "[Lo que este documento aporta, en una frase]"
basado_en: []
---

# Configuración de repositorios

La mantiene quien administra y la comprueba quien audita en la auditoría mensual. Un cambio en R1 a R4 se anota en «Cambios aprobados» de la configuración de plataforma. Los títulos de columna no se cambian: el plugin los lee. Una columna por repositorio, con su nombre de la línea «Repositorios:».

| # | Qué se cumple | Cómo se comprueba | [organización/repositorio] |
|---|---|---|---|
| R1 | Nada llega a `main` sin pull request, se une con squash y nadie se salta la regla | En GitHub, el repositorio → Settings → Rules: la regla de `main` existe y su lista de excepciones está vacía; en General, solo squash. Con la protección clásica de ramas, en Settings → Branches → la regla de `main`: *Require a pull request before merging* y *Do not allow bypassing the above settings* marcados | |
| R2 | Las pruebas pasan antes de unir | En la regla de `main`, las pruebas son obligatorias; con la protección clásica, *Require status checks to pass* con las pruebas en la lista y *Do not allow bypassing the above settings* marcado | |
| R3 | Ningún secreto entra en el código | En la regla de `main`, el control de secretos es obligatorio | |
| R4 | La base de datos cambia solo con migraciones nuevas, y una unida no se edita | «Rompe las reglas» de los seguimientos del último mes, si cubren el mes entero: lo confirma quien audita | |
| R5 | A Prod solo despliega quien administra, y solo lo que tiene el sí, como dice «Paso a Prod» | Quién tiene permiso de desplegar en Prod (no está en GitHub); los pasos a Prod del mes sin sí, con el de quien no acepta ni audita, publicados por quien no administra o con un seguimiento citado que no existe | |
| R6 | Cada pull request a `main`, salvo los de bots, empieza por el identificador de su pieza, o los de sus piezas unidos con « + », seguido de « · » | El apartado «fuera del plan» del último seguimiento | |
| R7 | El `CLAUDE.md` existe y tiene las reglas de la plantilla del kit | La sección «Reglas» del archivo, comparada con la de la plantilla: lo confirma quien audita | |

En cada celda: `cumple · AAAA-MM-DD`, `no cumple · AAAA-MM-DD`, `no aplica` o `excepción`. El porqué de un `no aplica` y la decisión de una `excepción` van en una nota debajo de la tabla, con su número y su repositorio. Sin base de datos, R4 no aplica.
