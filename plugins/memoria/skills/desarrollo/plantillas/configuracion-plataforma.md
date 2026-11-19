---
estado: borrador
actualizado: AAAA-MM-DD
aportacion: "[Lo que este documento aporta, en una frase]"
basado_en: []
---

# Configuración de plataforma

La mantiene quien administra y la comprueba quien audita en la auditoría mensual. Los títulos de columna no se cambian: el plugin los lee. Dos proyectos que comparten plataforma apuntan al mismo archivo, y lo mantiene el proyecto donde vive.

| # | Qué se cumple | Qué tiene este proyecto | Cómo se comprueba | Estado |
|---|---|---|---|---|
| PL1 | GitHub es de la empresa, pide verificación en dos pasos y su plan permite reglas en repositorios privados | | En GitHub, la organización → Settings → Authentication security y Billing | |
| PL2 | Dos personas pueden administrar GitHub | | En GitHub, la organización → People → filtro Owners | |
| PL3 | El dominio y la nube están a nombre de la empresa | | El titular en el registrador y en la facturación de la nube | |
| PL4 | Hay un entorno de Release separado de Prod | | Los entornos de la nube | |
| PL5 | Los secretos viven en un gestor de secretos, nunca en el código | | El gestor tiene las claves; el control de secretos del repositorio pasa | |
| PL6 | La base de datos se respalda sola y la restauración se ha probado | | Los respaldos de la nube y la fecha de la última prueba | |
| PL7 | Si Prod se cae, avisa a una persona | | El servicio de monitoreo y a quién avisa | |

**Estado:** `cumple · AAAA-MM-DD`, `no cumple · AAAA-MM-DD`, `no aplica` o `excepción`. El porqué de un `no aplica` y la decisión de una `excepción` van en una nota debajo de la tabla, con su número.

## Cambios aprobados
Todo cambio de quien administra en lo que cubren PL1 a PL7, o en las reglas R1 a R4 de los repositorios, lo aprueba antes quien audita; los pasos a Prod no cuentan aquí. Uno urgente se aprueba después. Una línea por cambio, la más nueva arriba.

| Fecha | Qué cambió | Aprobó |
|---|---|---|
