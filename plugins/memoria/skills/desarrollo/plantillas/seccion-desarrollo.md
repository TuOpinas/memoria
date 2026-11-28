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

Recibe: Nombre Apellido (correo)

Modelos: por defecto
```

Cada línea va separada de la siguiente por una línea en blanco, para que cada una se vea aparte al leer el `proyecto.md`. Cada persona va como `Nombre Apellido (correo, @usuario)`; el usuario de GitHub se omite si no tiene cuenta. «Audita» puede decir `nadie`, y la línea «Recibe» es opcional: sin ella no falta nada. La plataforma y los repositorios van en una sola configuración (`configuracion.md`): las dos claves pueden apuntar al mismo archivo.

**Modelos** dice qué modelo hace cada tarea del proyecto. `Modelos: por defecto` dice que el proyecto sigue la tabla de abajo, también cuando cambie; para apartarse en una tarea, se añade detrás (`Modelos: por defecto · consulta nadie`). `por defecto` va siempre primero, con mayúsculas o sin ellas, y tiene el mismo efecto que no poner la línea, que sigue siendo opcional (shared-memory/plugin-memoria#2026-11-26-10). Una tarea que no sale toma el valor de la tabla de abajo, que es el único sitio donde están los valores por defecto (las skills `calidad` y `desarrollo`, los agentes y la plantilla del `CLAUDE.md` remiten aquí). Cada valor es `<tarea> <modelo> [esfuerzo]`, separados por ` · `: el modelo con su familia y versión («Opus 5.5»), y el esfuerzo, si se dice, `bajo`, `medio`, `alto`, `extra` o `máximo`. `consulta nadie` quiere decir que el proyecto no usa un segundo modelo en los puntos de control. Ningún script la lee (los de la apertura y el tablero la dejan pasar como clave que no conocen): la lee Claude.

| Tarea | Qué es | Por defecto |
|---|---|---|
| `construye` | la sesión que construye | Opus 5.5; lo elige la persona en el selector, Claude lo propone |
| `coordina` | la sesión principal que planea y coordina una fase | Opus 5.5, igual |
| `revisa` | los revisores de una revisión de calidad | Opus 5.5 medio |
| `contraste` | errores y riesgos otra vez, en otro modelo, donde lo pide la revisión | Sonnet 5.5 alto |
| `arreglos` | los revisores de una revisión de arreglos | Opus 5.5 medio |
| `verifica` | la verificación sobre Release, antes del sí | el más barato de los que no construyeron: Sonnet 5.5 alto si construyó Opus; Opus 5.5 medio si construyó otro |
| `escenarios` | el subagente que escribe las pruebas de aceptación | Opus 5.5 medio |
| `seguimiento` | el subagente que prepara el seguimiento | Sonnet 5.5 medio |
| `consulta` | el segundo modelo de los puntos de control del `CLAUDE.md` | Fable 5.2 medio; si construyó Fable, Opus 5.5 medio |

Salen de revisiones medidas (shared-memory/plugin-memoria#2026-11-26-8) y se revisan en cada lectura de la efectividad (paso 8 de `calidad`); `verifica` todavía no tiene verificaciones medidas con Sonnet.

- **Antes de lanzar**, la sesión dice en una línea qué modelo y qué esfuerzo corre cada tarea («revisa Opus 5.5 medio · contraste Sonnet 5.5 alto»), de la línea o por defecto. Una tarea que no es de la tabla, o un valor que no se entiende, se dice en esa línea y toma el valor por defecto.
- **La verificación nunca la hace el modelo que construyó** (tecnologia/metodologia-desarrollo#2026-11-19-10), ni la consulta: si `verifica` o `consulta` nombran ese modelo, o una variable de entorno lo impone, se usa el de la tabla para ese caso, y si no se puede, el paso espera. El modelo que construyó lo dice el pull request («Construyó:»).
- **Si un modelo no está disponible** (se acabó su presupuesto, o la herramienta no deja elegirlo), se dice y el paso espera: nunca se hace en silencio con otro modelo, ni la consulta con el que construye, que no sería un segundo parecer. Quien acepta elige: esperar, nombrar otro modelo, o seguir esa vez sin la consulta, con una nota en el pull request («Consulta no disponible: <motivo>; decidió <Nombre Apellido>»), que ocupa el sitio de la pregunta y su respuesta.
- **Lo que corrió de verdad** es lo que se apunta: el informe de la revisión y el de la verificación dicen el modelo y el esfuerzo con que corrieron, no los que se pidieron.

**Seguimiento** lo escribe Claude cuando alguien lo pide (skill `desarrollo`, con sus scripts `recoger_github.py` y `seguimiento.py`), y mientras diga `por crear` no cuenta como pieza que falta: el primero se crea en `entregables/seguimiento.md` del proyecto, que nace `vigente`, y pone aquí su ruta. Cada entrada va arriba de la anterior, sin borrarla, y lleva en este orden:
1. la fecha, quién lo pidió, desde cuándo se leyó y el último commit de la rama principal que se leyó en cada repositorio, y debajo el bloque «en llano» de la fase en curso, copiado del plan;
2. cada pieza del plan con su estado, en una tabla `| Pieza | Estado |` (el tablero la lee de la entrada más reciente, bajo su `## AAAA-MM-DD`);
3. lo que está fuera del plan: pull requests sin pieza o con una que el plan no tiene, y el código de una pieza unido en un pull request que no la nombra;
4. lo que lo unido añade y el diseño no tiene: datos, componentes o conceptos nuevos, también con otro nombre. Va con el rótulo «4. Lo que lo unido añade y el diseño no tiene:» y debajo una línea por cosa, «- <nombre> (<repositorio>#<número>)», o «- nada»: es la forma que lee el tablero. `seguimiento.py` lo deja «- pendiente de revisar» y lo llena el subagente `seguimiento` antes de guardar (shared-memory/plugin-memoria#2026-11-27-14);
5. si el check «pruebas de aceptación» es obligatorio en la regla de la rama principal; los pull requests unidos que tocaron las pruebas de aceptación, su workflow o su corredor propio, o sacaron una pieza de la lista de piezas activas (y las piezas con pruebas que siguen fuera de ella), con quién los unió o aprobó (o, si quien acepta no tiene cuenta de GitHub, la aprobación del plan que cita): si no fue quien acepta, se señala;
6. los pasos a Prod, con quién dio el sí (si fue quien construyó, se dice como un hecho), los que no tienen sí, y las verificaciones de las piezas unidas desde el anterior;
7. con «Recibe» en la sección, las fases recibidas y quién las recibió, por la línea «Recibió:» de cada fase en el plan; sin ella, «sin recibir por escrito».

Quien no tenga el plugin se lo pide a quien acepta o a quien construye.

**Paso a Prod** dice dónde queda escrito el sí que deja pasar algo a Prod. Lo recomendado es `release de GitHub`: quien administra publica un release sobre el commit que leyó el seguimiento, con la línea «Aprobó: Nombre Apellido, AAAA-MM-DD · seguimiento AAAA-MM-DD». Otras formas valen si se dicen aquí, por ejemplo `aprobación en <herramienta>` o, sin entorno de Release, `sí sobre el resumen del despliegue`. Donde unir publica (un plugin como Memoria), unir el pull request de versión es el paso a Prod: lo une quien administra, con el sí, después de verificar la candidata instalada en una raíz o un entorno de prueba.

**Qué hace cada rol**
- **Acepta:** aprueba el diseño, el plan y los escenarios de cada pieza (o que una pieza técnica no los tiene), decide en los puntos de control del `CLAUDE.md`, comprueba la configuración al montar el proyecto y cuando cambia, une o aprueba los pull requests que tocan las pruebas de aceptación, revisa lo delicado (dependencias nuevas, permisos, accesos, pagos, datos personales, cambios de base de datos) antes de unir, lee el reporte de la verificación y da el sí.
- **Audita:** mira después, cuando quiere, lo que se hizo: el diseño técnico, el plan y la configuración. Lo que encuentra se lo lleva a quien acepta; no detiene nada. Si el proyecto no tiene auditoría, la línea dice `nadie`.
- **Construye:** construye con Claude, por bloques de una o varias piezas en un pull request a la rama principal, y lo une con las pruebas en verde y la revisión de calidad hecha.
- **Administra:** mantiene la configuración y pasa a Prod lo que recibió el sí. Es el único que despliega a Prod; donde unir publica, es quien une el pull request de versión.
- **Recibe:** la persona a quien se entrega cada fase, por ejemplo el cliente. Es opcional: sin ella, nadie recibe por escrito.

Una o dos personas pueden llevar todos los roles. El segundo par de ojos lo da el proceso: las pruebas de aceptación las escribe aparte un subagente, antes de que exista el código de la pieza, la verificación la hace otra sesión en otro modelo, y el seguimiento se lee antes del sí. Si quien construye también da el sí, el seguimiento lo dice tal cual, como un hecho.
