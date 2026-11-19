# Sección «Desarrollo»

Va al final del `proyecto.md`, después de «Quién participa». Las claves se escriben tal cual, en español, aunque el proyecto esté en otro idioma. Las rutas son desde la raíz; lo que aún no existe dice `por crear`. Varios valores, separados por ` · `.

```markdown
## Desarrollo
Repositorios: organización/repositorio · organización/otro
Configuración de plataforma: ruta
Configuración de repositorios: ruta
Diseño: ruta
Plan: ruta
Seguimiento: por crear
Paso a Prod: release de GitHub
Acepta: Nombre Apellido (correo, @usuario)
Audita: Nombre Apellido (correo, @usuario)
Construye: Nombre Apellido (correo, @usuario) · Otra Persona (correo, @usuario)
Administra: Nombre Apellido (correo, @usuario)
```

Cada persona va como `Nombre Apellido (correo, @usuario)`; el usuario de GitHub se omite si no tiene cuenta. La plataforma y los repositorios van en una sola configuración (`configuracion.md`): las dos claves pueden apuntar al mismo archivo.

**Seguimiento** lo escribe Claude cuando alguien lo pide (skill `desarrollo`), y mientras diga `por crear` no cuenta como pieza que falta: el primero se crea en `entregables/seguimiento.md` del proyecto, que nace `vigente`, y pone aquí su ruta. Cada entrada va arriba de la anterior, sin borrarla, y lleva en este orden:
1. la fecha, quién lo pidió y el último commit de la rama principal que se leyó en cada repositorio;
2. cada pieza del plan con su estado;
3. lo que está fuera del plan: pull requests sin pieza o con una que el plan no tiene;
4. lo que lo unido añade y el diseño no tiene: datos, componentes o conceptos nuevos, también con otro nombre;
5. los pasos a Prod sin sí, y las verificaciones de las piezas unidas desde el anterior.

Quien no tenga el plugin se lo pide a quien audita o a quien construye.

**Paso a Prod** dice dónde queda escrito el sí que deja pasar algo a Prod. Lo recomendado es `release de GitHub`: quien administra publica un release sobre el commit que leyó el seguimiento, con la línea «Aprobó: Nombre Apellido, AAAA-MM-DD · seguimiento AAAA-MM-DD». Otras formas valen si se dicen aquí, por ejemplo `aprobación en <herramienta>` o, sin entorno de Release, `sí sobre el resumen del despliegue`.

**Qué hace cada rol**
- **Acepta:** aprueba lo funcional del diseño y los escenarios de cada pieza, lee el reporte de la verificación y da el sí.
- **Audita:** valida el diseño técnico y el plan, decide en los puntos de control, da el sí y comprueba la configuración al montar el proyecto y cuando cambia.
- **Construye:** construye con Claude, por bloques de una o varias piezas en un pull request a la rama principal, y lo une con las pruebas en verde y la revisión de calidad hecha.
- **Administra:** mantiene la configuración y pasa a Prod lo que recibió el sí. Es el único que despliega a Prod.

Una persona puede tener varios roles.
