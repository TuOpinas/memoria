# Sección «Desarrollo»

Va al final del `proyecto.md`, después de «Quién participa». Las claves se escriben tal cual, en español, aunque el proyecto esté en otro idioma. Las rutas son desde la raíz; lo que aún no existe dice `por crear`. Varios valores, separados por ` · `.

```markdown
## Desarrollo
Repositorios: organización/repositorio · organización/otro
Configuración de plataforma: ruta
Configuración de repositorios: ruta
Diseño: ruta
Plan: ruta
Seguimiento: ruta
Paso a Prod: release de GitHub
Acepta: Nombre Apellido (correo, @usuario)
Audita: Nombre Apellido (correo, @usuario)
Construye: Nombre Apellido (correo, @usuario) · Otra Persona (correo, @usuario)
Administra: Nombre Apellido (correo, @usuario)
```

Cada persona va como `Nombre Apellido (correo, @usuario)`; el usuario de GitHub se omite si no tiene cuenta.

**Seguimiento** lo escribe el plugin cuando alguien lo pide, y mientras diga `por crear` no cuenta como pieza que falta: el primero lo crea en `entregables/seguimiento.md` del proyecto, que nace `vigente`, y pone la ruta aquí. Cada seguimiento se añade arriba del anterior, sin borrarlo. Lleva:
- fecha, quién lo pidió, el commit de `main` que leyó en cada repositorio y qué pudo comparar;
- las piezas con su estado;
- lo que está fuera del plan;
- lo que no está en el diseño (datos, componentes y conceptos nuevos);
- lo que rompe las reglas: commits en `main` sin pull request, uniones sin squash, migraciones ya unidas que cambiaron, y cambios al `CLAUDE.md` o a los controles;
- los pasos a Prod que aprobó quien construyó.

Quien no tenga el plugin se lo pide a quien audita o a quien construye.

**Paso a Prod** dice dónde queda escrito el sí que deja pasar algo a Prod. Lo decide cada proyecto, y sea cual sea la forma el sí dice sobre qué seguimiento se dio, quién lo dio (como está escrito arriba) y cuándo. Lo recomendado es `release de GitHub`: quien administra publica un release sobre el commit que leyó ese seguimiento, con la línea «Aprobó: Nombre Apellido, AAAA-MM-DD · seguimiento AAAA-MM-DD». Solo cuenta un release publicado con esa línea; uno sin ella sale en el seguimiento como «paso a Prod sin sí». Otras formas valen si se dicen aquí, por ejemplo `aprobación en <herramienta>` o, sin entorno de Release, `sí sobre el resumen del despliegue`. Con otra forma, el plugin marca las piezas como entregadas solo si quien administra crea igualmente un release o una etiqueta en el commit desplegado. El seguimiento dice qué forma entendió.

**Qué hace cada rol**
- **Acepta:** valida lo funcional del diseño, prueba lo unido y da el sí sobre un seguimiento.
- **Audita:** valida el diseño técnico y el plan, decide en los puntos de control, da el sí, aprueba los cambios de la plataforma y hace la auditoría mensual.
- **Construye:** construye con Claude una pieza por pull request, la une con las pruebas en verde y la revisión de calidad hecha.
- **Administra:** mantiene las dos configuraciones y pasa a Prod lo que recibió el sí. Es el único que despliega a Prod.

Una persona puede tener varios roles. Los pasos a Prod que aprobó quien construyó salen en el seguimiento, para que los vea quien acepta.
