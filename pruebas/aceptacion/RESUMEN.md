# Pruebas de aceptación · resumen para quien acepta

Escenarios aprobados por Juanjo Jiménez-Alfaro el 2026-11-22, en el plan (fase F1, versión 1.27.1). Este resumen está escrito a mano; desde la pieza P09 se genera desde las propias pruebas.

## Qué buscan

El kit entrega a cada proyecto una comprobación automática que GitHub corre en cada pull request. Aquí se llama «la comprobación»; los títulos de las pruebas la llaman «el check», que es lo mismo. Estas pruebas buscan que elija bien las pruebas de cada pieza, las corra todas de una vez y no deje pasar archivos o títulos mal puestos.

Una pieza está **activa** cuando sus pruebas ya cuentan: su pull request la añadió a la lista de piezas activas del repositorio. Las pruebas de una pieza que aún no está activa existen, fallan y no deben correr ni estorbar.

## Cómo están planteadas

Cada prueba arma un repositorio de mentira con un pull request de mentira, corre sobre él la comprobación tal como la entrega el kit y mira qué pasó: si quedó en verde o en rojo, qué pruebas corrieron y qué dijeron sus mensajes de error.

Cada fila de abajo lleva el título tal como lo imprime la prueba al correr, para poder casar un «FALLA» con su fila. Las filas marcadas **Añadido** no están en los escenarios aprobados: son casos de control, y se aprueban con este resumen.

Cuando se escribieron fallaban todas las filas menos una, y debían: las piezas aún no existían. Desde la 1.27.1 pasan. La columna «La pone en verde» dice qué pieza hace pasar cada fila.

## P01 · Selección exacta de la pieza

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Solo corren las pruebas de la pieza | P1 está activa y su prueba pasa. P10 y AP1 tienen pruebas en la carpeta, que fallan, y no están activas; la de P10 lleva «P1_» en su nombre interno | Corre la prueba de P1 y ninguna de las otras; queda en verde | P01 |
| El fallo nombra a su pieza (falla P1, pasa P10) | P1 y P10 activas; la prueba de P1 falla | Queda en rojo, y el error nombra a P1 y no a P10 | P01 |
| **Añadido:** El fallo nombra a su pieza (falla P10, pasa P1) | Lo mismo, al revés | Queda en rojo, y el error nombra a P10 y no a P1 | P01 |
| **Añadido:** Con todas las pruebas pasando, el check queda en verde | P1 y P10 activas; las dos pasan | Corren las dos y queda en verde | P01 |

**Cambia un escenario aprobado, y pide tu aprobación.** El primero decía «P1 y P10 activas; al correr P1, solo corre la de P1». Con la pieza P02 todas las activas corren juntas, así que «correr solo P1» deja de existir. La prueba lo plantea así: P10 tiene pruebas pero aún no está activa, y no debe correr.

## P02 · Una sola corrida

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Una corrida prueba todas las piezas activas | P1, P2 y P3 activas; fallan P1 y P3. **Añadido:** P4 tiene una prueba que falla y no está activa | Corren las tres en una sola corrida; queda en rojo, y el error nombra a P1 y a P3. **Añadido:** la de P4 no corre ni se nombra | P02, con P01 hecha |
| Una prueba saltada no cuenta como pasada (la saltada es de P1) | P1 y P2 activas; P1 tiene una prueba que pasa y otra que se salta | Queda en rojo y el error nombra a P1, no a P2 | P01 |
| **Añadido:** Una prueba saltada no cuenta como pasada (la saltada es de P2) | Lo mismo, al revés | Queda en rojo y el error nombra a P2, no a P1 | P01 |
| **Añadido:** Con todas las pruebas pasando, una sola corrida y el check en verde | P1, P2 y P3 activas y pasando; P4 falla y no está activa | Corren las tres en una sola corrida, no la de P4, y queda en verde | P02, con P01 hecha |

Las dos filas de la prueba saltada son un seguro: la comprobación de hoy ya rechaza las saltadas, y pasan en cuanto P01 está hecha. Están para que P02 no lo rompa.

## P03 · «Tiene pruebas» por el nombre del archivo

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| El archivo de una prueba empieza por su pieza (test_P1_extra.py) | Un pull request «Escenarios · P1» trae `P1_alta.py`, bien nombrado, y ese otro archivo | Queda en rojo, y el error nombra el archivo y dice que empieza por «P1_» | P03 |
| El archivo de una prueba empieza por su pieza (P1extra.py) | Lo mismo, con ese archivo | Lo mismo | P03 |
| El archivo de una prueba empieza por su pieza (extra_P1.py) | Lo mismo, con ese archivo | Lo mismo | P03 |
| **Añadido:** El archivo de una prueba empieza por su pieza (P2_extra.py) | Lo mismo, con un archivo de otra pieza | Lo mismo: en «Escenarios · P1» solo entran archivos de P1 | P03 |
| **Añadido:** Un pull request de escenarios bien nombrado queda en verde | «Escenarios · P1» con `P1_alta.py`, que falla porque la pieza no existe, y el archivo de apoyo `conftest.py`, que no es de ninguna pieza | Queda en verde | P01 |
| Un título mal escrito no se cuela («P01: alta») | P01 tiene pruebas; un pull request de código se titula así | Queda en rojo y el error dice que el título empieza «P01 · » | P03 |
| **Añadido:** Un título mal escrito no se cuela («P07: alta») | Lo mismo con P07, para que el mensaje no lleve «P01» fijo | Queda en rojo y el error dice «P07 · » | P03 |
| **Añadido:** Un título mal escrito no se cuela («P01 - alta») | Lo mismo con un guion en vez de dos puntos | Queda en rojo y el error dice «P01 · » | P03 |
| **Añadido:** Un título así, de una pieza sin pruebas, no falla por el título | P1 no tiene pruebas; sí las tienen P10 y P01, y un archivo de P01 lleva «P1» en el nombre. El pull request se titula «P1: algo» | Queda en verde. Es la única fila que hoy ya pasa | — |
| **Añadido:** El pull request de la pieza, bien titulado, queda en verde | «P01 · alta» añade P01 a la lista de activas, y su prueba pasa | Queda en verde | P01 |

## Lo que las pruebas piden de más

Además de lo marcado «Añadido», las pruebas exigen cinco cosas que tus escenarios no dicen con esas palabras:

1. El nombre de la pieza que falla tiene que ir en un mensaje de error de la comprobación, no en cualquier parte de la salida.
2. Ningún mensaje de error puede nombrar a una pieza que no falló entre las activas, ni a una que no está activa. Un error como «Falla P1 (activas: P1, P2, P3)» no vale.
3. La prueba que falla o se salta tiene que haber llegado a correr: no vale que la comprobación quede en rojo por otra razón.
4. «Queda en verde» quiere decir que la comprobación termina bien y sin ningún mensaje de error.
5. El error de un archivo mal nombrado tiene que traer el nombre del archivo y el prefijo «P1_» tal cual.

## P04 no está en este pull request

Su prueba es de otro tipo: el seguimiento lo hace Claude, sin programa, así que se prueba con una sesión real. Su escenario se retiró de aquí porque todavía no puede correr y no comprobaba la cita que no coincide con el plan. Vuelve en su propio pull request, con pull requests ya unidos, que es lo que mira el seguimiento.

## Lo que no es una prueba

- `correr.py` es el corredor propio del control: con archivos da `PASA`, `FALLA` o `NO_CORRIO` por cada uno, y por piezas termina con «N pasan · M fallan · K saltadas», que cuenta archivos de prueba, no filas de este resumen. Una prueba que no arranca o se salta no cuenta como pasada ni como fallo.
- `probar_control.py` comprueba que el control del repositorio es la plantilla con lo de memoria, y lo genera con `--escribe`.
- `flujo.py` arma el repositorio de mentira y corre la comprobación. Entiende una parte de lo que GitHub admite, que su cabecera lista; ante lo que no entiende, se detiene con un error en vez de correr otra cosa.

## Lo que queda sabido

- La regla del título se prueba con dos puntos y con guion, no con todas las formas de escribirlo mal.
- El seguro de las saltadas no cubre las pruebas marcadas «se espera que falle», que la comprobación de hoy también rechaza.
- Si se interrumpe con Ctrl-C a mitad, queda una carpeta temporal sin borrar.
- Con el bash de serie de un Mac las pruebas no corren: avisan y salen con error.

## Fase F2 · La vista de desarrollo del tablero

Escenarios aprobados por Juanjo Jiménez-Alfaro el 2026-11-23, en el plan (fase F2, versión 1.28.0).

**Cómo están planteadas.** Las cuatro piezas se prueban igual. Hay una organización de mentira, escrita dentro de la primera prueba: un área «ventas» con dos proyectos, «portal», que construye software (lleva la sección «Desarrollo», con su diseño, su plan, su seguimiento y un documento con el detalle de los datos), y «campaña», que no. Cada prueba la escribe en una carpeta temporal, le cambia lo que pide su escenario, genera el tablero sobre ella y lee lo que el tablero prepara para la pestaña Desarrollo del portal. No abre ningún navegador.

Hoy fallan todas las filas, y deben: el tablero todavía no prepara nada para esa pestaña. La columna «La pone en verde» dice qué pieza hace pasar cada fila.

**Lo que queda para la verificación en pantalla**, porque estas pruebas no lo ven: que la pestaña dibuje de verdad las columnas, las tarjetas, el flujo de pasos y los diagramas; que un clic abra el detalle de una fase, de una pieza o de una entidad; y que la marca «Desarrollo» se vea en cada sitio del tablero donde sale el proyecto. Las pruebas comprueban que todo eso está preparado con los datos correctos.

### P05 · Lectores y plantilla del diseño

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Se lee un diseño hecho con la plantilla | El diseño del portal, hecho con la plantilla, con «Grupo» en los datos, «Entidades» en los conceptos y «Conecta con» en componentes e infraestructura | Salen el objetivo, los tres pasos de «Cómo funciona», las dos reglas con su excepción, y cada entidad con su grupo y sus relaciones, cada concepto con sus entidades, y cada componente y pieza de infraestructura con lo que conecta | P05 |
| Se leen un plan y su último seguimiento | El plan con dos fases y tres piezas, y un seguimiento con dos entradas: la de arriba (20 de noviembre) dice el estado de P01 y P02; la de abajo (10 de noviembre), el de las tres | Salen las fases con sus piezas, cada pieza con sus escenarios, y P01 y P02 con el estado y la fecha de la entrada de arriba. P03, que solo sale en la de abajo, no se lleva su estado de ahí | P05 |
| Una tabla que no se puede leer se nombra, no rompe (sin la columna «Grupo» de «Datos») | Al diseño le falta esa columna | El tablero se genera sin romperse, un aviso nombra «Grupo», y el objetivo, los pasos, las reglas, los conceptos, los componentes y la infraestructura salen enteros | P05 |
| **Añadido:** Una tabla que no se puede leer se nombra, no rompe (sin la sección «Reglas») | Al diseño le falta esa sección | Lo mismo: un aviso nombra «Reglas» y lo demás sale entero, entidades incluidas | P05 |

### P08 · Pestaña Desarrollo: resumen y plan

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| La pestaña muestra el resumen y el plan como tablero | El portal con su sección, diseño, plan y seguimiento | Salen el objetivo, los pasos de «Cómo funciona» en orden y las reglas; el plan, una columna por fase en el orden del plan (F1 con P01 y P02, F2 con P03), cada pieza con el estado del último seguimiento, y la fecha de ese seguimiento | P08, con P05 hecha |
| Una fase abre su detalle | La misma | Cada fase trae su frase «en llano», qué podrá hacer quién, su versión y su «Listo cuando», tal como los dice el plan | P08, con P05 hecha |
| Una pieza abre su detalle | La misma | Cada pieza trae qué entrega, sus escenarios (título y su Dado, Cuando y Entonces) y quién los aprobó y cuándo | P08, con P05 hecha |
| Cada fuente dice su fecha | La misma | Salen la fecha del diseño (15 de noviembre), la del plan (18) y la del seguimiento (20), cada una con el documento del que sale | P08, con P05 hecha |
| Sin seguimiento el plan se sigue viendo | El proyecto dice «Seguimiento: por crear» y no hay archivo de seguimiento | Salen las fases y las tres piezas, ninguna con estado, y un aviso del seguimiento dice que aún no lo hay | P08, con P05 hecha |
| Lo que no se puede leer se dice, y lo demás se pinta | La tabla de piezas del plan está escrita como una frase, no como tabla | Un aviso del plan dice que no se pudo leer, y el objetivo, los pasos y las reglas salen enteros | P08, con P05 hecha |
| Los proyectos de desarrollo llevan una marca | El portal, con la sección, y la campaña, sin ella | El portal lleva la marca «Desarrollo» y tiene pestaña; la campaña no tiene ni marca ni pestaña | P08 |

### P10 · El modelo de datos en la pestaña

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Las entidades se dibujan con sus relaciones | Cuatro entidades en dos grupos (cliente y pedido en «Ventas», producto y categoría en «Catálogo»), con relaciones dentro de un grupo y entre los dos | Cada entidad sale con su grupo, cada relación con su tipo, y cada relación va a una entidad que está | P10, con P05 hecha |
| Una entidad muestra su detalle y sus conceptos | La línea «Detalle:» del diseño apunta a un documento con una fila para «cliente», y dos conceptos («Pedido» y «Cliente frecuente») la nombran | «cliente» trae los datos de su fila (campos y dónde se guarda) y esos dos conceptos | P10, con P05 hecha |
| Un desajuste se dice, no se esconde | El diseño tiene una entidad «factura» sin fila en el detalle, y el detalle una fila «envio» que el diseño no tiene | Salen las cinco entidades, y hay dos avisos de los datos: uno nombra «factura» y otro «envio» | P10, con P05 hecha |

### P11 · Componentes e infraestructura en la pestaña

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Cada diagrama muestra qué se conecta con qué | Cuatro componentes y tres piezas de infraestructura, con «Conecta con» lleno | Cada fila sale como una caja con lo que conecta, y cada conexión va a otra caja de la misma tabla | P11, con P05 hecha |
| Una conexión a algo desconocido se dice | «Panel interno» conecta también con «Buzón», que no está en los componentes, y «Dominio» con «CDN», que no está en la infraestructura | Salen todas las cajas y las conexiones que sí existen; un aviso de los componentes nombra «Buzón» y uno de la infraestructura nombra «CDN» | P11, con P05 hecha |

### Cómo se leyó lo que el escenario no precisa

1. «Lo nombra» quiere decir que el texto de un aviso trae el nombre tal cual: «Grupo», «Reglas», «factura», «envio», «Buzón», «CDN».
2. En el escenario del seguimiento con dos entradas, a P03, que solo sale en la de abajo, no se le pide un estado concreto: solo que no se lleve el de esa entrada.
3. Sin la columna «Grupo», «lo demás» son las otras partes del diseño; no se exige que las entidades salgan.
4. «Sin romperse» quiere decir que el tablero se genera entero, como hoy: sale bien, no a medias.
5. Del resumen «en llano» de una fase se comprueba su frase; la tabla de pieza y qué arregla no se comprueba aquí: cada pieza de la fase ya sale con lo que entrega.
6. Cada relación se espera en la entidad donde el diseño la escribe, una sola vez, no repetida en la otra.
7. En un desajuste de datos se piden dos avisos, uno por cada cosa que no cuadra.
8. Con el plan entero no puede haber ningún aviso del plan: así el aviso de «no se pudo leer» no vale si sale siempre.

## Fase F4 · Los diagramas como camino, y el detalle en una ventana

Escenarios aprobados por Juanjo Jiménez-Alfaro el 2026-11-23, en el plan (fase F4, versión 1.29.0).

**Cómo están planteadas.** P16, P17 y P18, como las de F2: a la organización de mentira se le cambia lo que pide el escenario (una línea «Flujo:», la columna «Externo», las columnas Proveedor, Cuenta y Ambiente), se genera el tablero y se lee lo que prepara para la pestaña Desarrollo. P15 es de pantalla: lee la página del tablero como texto, sin abrirla.

Hoy fallan todas las filas, y deben. «La pone en verde» dice qué pieza hace pasar cada fila.

**Queda para la verificación en pantalla**: el dibujo de las tres vistas (la fila del flujo con lo de arriba y abajo, las flechas de los componentes, los contenedores con su etiqueta, el verbo sobre la línea); que lo externo se distinga por algo más que el color; que la ventana se abra con el foco dentro, que Esc y el clic fuera la cierren y el foco vuelva; que diga «Sin detalle»; y que la marca sea un icono, sin la palabra, con su texto también al pasar el ratón.

### P15 · El detalle en una ventana, y el icono

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Una pieza se abre en una ventana | La página del tablero | Tiene una ventana (`<dialog`) | P15 |
| La ventana se cierra y devuelve el foco | La misma | Lo mismo: sin abrirla solo se ve que la ventana existe | P15 |
| Lo que no tiene nada que mostrar se dice | La misma | Tiene la ventana y el texto «Sin detalle» | P15 |
| La marca es un icono | La misma | Tiene, escrito tal cual, `aria-label="Proyecto de desarrollo"` | P15 |

### P16 · El modelo de datos como camino

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| El flujo es una fila, en su orden | «**Flujo:** cliente → pedido → producto» bajo «Datos», y otra línea «Flujo:» en «Componentes», antes | El flujo es cliente, pedido, producto; categoría va arriba y nada abajo. **Añadido:** cada entidad en un solo sitio, y ningún aviso pide «Flujo:» | P16, con P05 hecha |
| **Añadido:** El flujo es una fila, en su orden (lo que recibe dos flechas va abajo) | «Flujo: cliente → pedido», y cliente se relaciona con producto: a producto apuntan cliente y pedido | Producto va abajo, categoría arriba | P16, con P05 hecha |
| Una relación lleva su verbo | La relación de producto se escribe «categoria (vive en)» | Lleva el verbo «vive en» y el tipo vacío. **Añadido:** la de cliente sigue como en la 1.28.0, «1:N» sin verbo | P16, con P05 hecha |
| Sin flujo se dibuja como antes | La muestra tal cual | Las entidades y relaciones como en la 1.28.0, sin disposición en fila, y un aviso de los datos pide «Flujo:» | P16, con P05 hecha |
| Una entidad desconocida en el flujo se dice | «Flujo: cliente -> pedido -> envio -> producto» (sin negrita, con «->»); «envio» no está en «Datos» | Las entidades enteras, el flujo cliente, pedido, producto, y un aviso de los datos nombra «envio» | P16, con P05 hecha |

### P17 · Los componentes como recorrido

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| El recorrido es una fila de flechas | «Componentes» con la columna «Externo» y «**Flujo:** Tienda web → API → Motor de pagos»; «Datos» con su propia línea «Flujo:» | El recorrido es Tienda web, API, Motor de pagos, y las cuatro cajas salen con lo que conectan y si son externas | P17, con P05 hecha |
| Lo externo se distingue, no solo por el color | «Motor de pagos» con «sí» en «Externo»; los demás, vacía; sin línea «Flujo:» | Motor de pagos es externo y los otros tres propios. **Añadido:** sin «Flujo:» no hay recorrido | P17, con P05 hecha |
| Una conexión a algo desconocido se dice | La tabla nueva, «Flujo: Tienda web -> API -> Motor de pagos» (sin negrita, con «->»), y «Panel interno» conecta también con «Buzón», que no está | Un aviso de los componentes nombra «Buzón», y salen las cajas, lo externo y el recorrido | P17, con P05 hecha |

### P18 · La infraestructura por proveedor y cuenta

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Un contenedor por proveedor y cuenta | Con Proveedor, Cuenta y Ambiente: servidor web y base de datos en Nube · tienda-prod; dominio en Nube · cuenta-dominios | Dos contenedores, en ese orden: Nube · tienda-prod · producción con las dos piezas, y Nube · cuenta-dominios con el dominio. Cada pieza lleva su proveedor, cuenta y ambiente. **Añadido:** ningún aviso pide separar por proveedor | P18, con P05 hecha |
| La columna vieja se sigue dibujando | La muestra tal cual, con «Dónde» | Una caja por fila con lo que conecta, sin contenedores, y un aviso de la infraestructura nombra «Proveedor» | P18, con P05 hecha |
| Un servicio externo tiene su propio contenedor | Una fila más, «Carpeta de comprobantes», en Google Drive con la cuenta del cliente, entre las dos de tienda-prod | Un contenedor para ella sola, entre el de tienda-prod (con sus dos piezas) y el de cuenta-dominios | P18, con P05 hecha |

### Cómo se leyó lo que el escenario no precisa

1. «En una fila, en su orden» es la lista del flujo en el orden de la línea; abajo van las entidades que reciben dos o más relaciones escritas en filas del flujo; arriba, las demás.
2. Una relación con solo cardinalidad sigue como en la 1.28.0, sin verbo (así no cambian P05 ni P10); una con verbo lleva el tipo vacío.
3. «Lo nombra» y «dice qué añadir»: el texto de un aviso trae «envio», «Buzón», «Flujo:» o «Proveedor» tal cual.
4. La columna «Externo» va antes de «Conecta con»; «sí» es externo y la celda vacía, propio.
5. En la conexión desconocida de P17, «lo demás» es lo de la 1.29.0: cajas, lo externo y el recorrido. El aviso de «Buzón» ya sale hoy (lo pide P11); la fila falla por lo demás.
6. Los contenedores se comparan por proveedor, cuenta, ambiente y piezas, en orden; si traen más datos, no se miran.
7. El servicio externo se reconoce por otro proveedor y otra cuenta: el contrato no tiene marca de «del cliente».

### Lo que queda sabido

- Si dos filas comparten proveedor y cuenta pero no ambiente, el contrato no dice qué ambiente lleva el contenedor: la muestra usa uno solo.
- «Sin detalle» ya está hoy en la página (la ficha de una entidad sin detalle): la fila 3 de P15 solo prueba, de hecho, que hay ventana.
- P15 busca el atributo escrito exactamente `aria-label="Proyecto de desarrollo"`: otra forma de dar el mismo texto a los lectores de pantalla no la cuenta.

## P23 · La apertura conecta los repositorios

Escenarios aprobados por Juanjo Jiménez-Alfaro el 2026-11-23, en el plan.

**Cómo están planteadas.** La prueba escribe la misma organización de mentira de F2 en una carpeta temporal, abre la sesión de un proyecto con la apertura del plugin, como la cuenta de Ana Pérez, y lee lo que la apertura le pide a la sesión que responda: su lista de pasos numerados. El portal construye software y su sección «Desarrollo» dice «Repositorios: muestra/portal»; la campaña no tiene esa sección.

Hoy fallan las tres primeras filas, y deben: la apertura todavía no nombra los repositorios. La cuarta ya pasa hoy: la apertura de la campaña no habla de repositorios porque todavía no lo hace en ningún proyecto; está para que P23 no lo rompa.

**Queda para la verificación en pantalla**: que la sesión conecte de verdad cada repositorio con escritura antes de trabajar, y que, si uno no se puede conectar, lo diga en una línea con el motivo y siga. Eso lo hace el modelo con su herramienta de repositorios; la prueba solo comprueba que la apertura se lo pide.

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| La apertura nombra los repositorios que conectar | Se abre el portal, con «Repositorios: muestra/portal» | Un paso nombra `muestra/portal` tal cual y dice «con escritura» y «antes de trabajar» | P23 |
| **Añadido:** La apertura nombra los repositorios que conectar (dos repositorios) | La línea dice «Repositorios: muestra/portal · muestra/api» | Un mismo paso nombra los dos y dice «con escritura» y «antes de trabajar» | P23 |
| Un repositorio que no se puede conectar se dice | Se abre el portal | El paso que nombra `muestra/portal` dice «una línea», «motivo» y «sigue» | P23 |
| En otros proyectos no se dice nada | Se abre la campaña, sin «Desarrollo» | Lo que la apertura pide responder tiene pasos, y en ningún sitio dice «repositorio» ni «con escritura» | ya pasa hoy |

La fila de dos repositorios sale del contrato de la pieza, no de un escenario aparte: es cómo se comprueba «cada uno».

### Cómo se leyó lo que el escenario no precisa

1. «Lo que responde la apertura» es su sección «=== RESPUESTA», hasta la siguiente «=== » o el final; un paso va desde su «1. » hasta el siguiente número, aunque ocupe varias líneas.
2. Los nombres de los repositorios se buscan tal cual, con sus mayúsculas; «con escritura», «antes de trabajar», «una línea», «motivo» y «sigue» se buscan sin distinguir mayúsculas («Con escritura» también vale).
3. «Se dice en una línea con el motivo, y se sigue» se comprueba en el mismo paso que nombra los repositorios, no en otro.
4. En la campaña, «nada sobre repositorios» se mira en toda la apertura, no solo en lo que pide responder. **Añadido:** se pide que haya pasos, para que la fila no pase porque la apertura no diga nada de nada.

### Lo que queda sabido

- Un repositorio que no se puede conectar no se puede simular desde la apertura: la prueba no distingue qué repositorio falla, solo que el paso pide decirlo y seguir.
- La prueba busca palabras, no el sentido: un paso que dijera «no conectes con escritura… antes de trabajar» también pasaría. Eso lo ve quien verifica.

## Fase F5 · El tablero se lee de un vistazo

Escenarios aprobados por Juanjo Jiménez-Alfaro el 2026-11-23, en el plan (fase F5, versión 1.29.1): los dos nuevos de P15 y los de P19, P20, P21, P22 y P25.

**Cómo están planteadas.** Hay dos maneras de mirar.

- **Lo que el tablero prepara.** Como en F2 y F4: a la organización de mentira se le cambia lo que pide el escenario (una columna «En corto», una base, las columnas «Horas» y «Para antes»), se genera el tablero y se lee lo que prepara para la pestaña Desarrollo.
- **El dibujo.** P19, P20 y P21 miran además el dibujo. La página del tablero tendrá un trozo que calcula dónde va cada caja, cada línea y cada verbo. La prueba saca ese trozo de la página, lo corre aparte (con node) sobre lo que preparó el tablero y mide el resultado en píxeles. No abre ningún navegador.
- P21 se corre sobre dos muestras: el diseño de plugin-memoria tal cual y uno con la forma del de product-design (la nueva, con «En corto», ocho entidades y dos componentes externos) y otros nombres.
- P25 saca de la página, igual, el trozo que decide con qué pestaña se abre un proyecto, y lo corre aparte.
- P15 lee la página como texto, igual que en F4.

Hoy fallan todas las filas, y deben: la pieza que las pone en verde aún no existe. Las cuatro filas de P15 de F4 siguen pasando y no cambian.

**Lo que queda para la verificación en pantalla**, porque estas pruebas no lo ven:
- P15: que el icono se vea detrás de un nombre cortado, y que el tooltip salga al pasar el ratón, al enfocar y al tocar.
- P19: los colores de verdad, que la caja enseñe su línea corta bajo el nombre, y que la ventana de una caja diga su rol con palabras.
- P20: que la ventana de una entidad liste su relación con la base.
- P21: que un dibujo ancho se desplace de lado.
- P22: las horas y la marca en la tarjeta, la suma en la fase y lo que dice la ventana.
- P25: que al elegir otro proyecto en el menú lateral se abra de verdad en esa pestaña, y que desde Estatus a otro proyecto de desarrollo siga en Estatus.
- P20: que la banda quede debajo del flujo.
- P19 a P21: que lo que se ve sea lo que calculó el trazado (sin cruces, verbos libres, letra de 13 px) en los dos diseños reales, y que la infraestructura lleve sus contenedores.
- P15: el icono en los tres sitios (menú lateral, su área y junto al título).

Todo esto se recorre sobre la candidata, con los diseños reales de product-design y plugin-memoria.

### P15 · El icono, siempre visto y explicado (F5)

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| El icono sobrevive a un nombre largo | La página del tablero | El nombre del menú lateral va en su propio elemento (`class="side-nombre"`), y la página lo corta con «…» (una regla de `.side-nombre` con `text-overflow:ellipsis`) | P15 |
| El icono se explica al momento | La misma | El icono lleva el tooltip propio del tablero (`data-tip="Proyecto de desarrollo"`). **Añadido:** que no quede el del navegador (`title="Proyecto de desarrollo"`, que hoy sí está) | P15 |

### P19 · Cajas que dicen qué son

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Una caja lleva su línea corta | «En corto» en las tres secciones, en otro sitio en cada una (segunda columna en «Datos», última en «Componentes», tercera en «Infraestructura»), con una celda vacía en cada sección | Cada fila trae su línea corta tal cual, o vacía si la celda lo está. **Añadido:** la columna en otra posición en cada sección | P19 |
| Sin la columna nada cambia | La muestra tal cual | Cada caja trae la línea corta vacía, y ningún aviso nombra «En corto» | P19 |
| El color dice el rol | En «Componentes»: el flujo «Tienda web → API»; «Motor de pagos» es externo; «Buzón» recibe una línea y no saca ninguna; «Panel interno» saca líneas sin estar en el flujo | Tienda web y API son del flujo; Buzón es destino; Motor de pagos y Panel interno, del resto: salen los tres roles, y el externo va con el resto. **Añadido:** en «Datos» (el flujo cliente → pedido → producto, con categoría de base), los tres del flujo son del flujo y la base es del resto; en la infraestructura, que no tiene flujo, la base de datos es destino y las otras dos, del flujo | P19 |
| La leyenda nombra los roles | La misma, con la infraestructura sin conexiones (todo del resto) | Componentes tiene tres roles y Datos dos: su leyenda trae una entrada por cada rol, cada una con texto. **Añadido:** la infraestructura tiene uno solo y su leyenda va vacía | P19 |

### P20 · La base compartida, sin líneas

En todas las filas, la organización de mentira tiene el flujo «cliente → pedido → producto», y pedido y producto apuntan a «categoría», que queda fuera: categoría es la base. Pedido → producto lleva el verbo «lleva».

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| La base es una banda sin líneas | Esa | Las dos relaciones hacia categoría van marcadas como relaciones con la base, y las demás no. En el dibujo, categoría está en la banda, y ninguna línea llega a ella ni sale de ella. **Añadido:** con el diseño de plugin-memoria, donde la base, «Project», apunta a «Area», tampoco sale ninguna línea de «Project» | P20 |
| **Añadido:** La base es una banda sin líneas (sin «Flujo:» no hay base) | Las mismas relaciones, sin la línea «Flujo:» | Ninguna relación va marcada, y no hay banda | P20 |
| Las relaciones con la base se siguen contando | Esa | La relación producto → categoría sigue ahí con su verbo «vive en», marcada como relación con la base, y el dibujo trae una nota que dice dónde están | P20 |
| Cualquier otra relación guarda su línea | Esa | Pedido → producto tiene su línea y su verbo «lleva» | P20 |

### P21 · Líneas que se pueden seguir

Las tres vistas (datos, componentes, infraestructura) de los dos diseños de muestra.

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Ninguna línea pasa por encima de una caja | Las seis vistas | Cada tramo de cada línea es horizontal o vertical. Ningún tramo pasa por dentro de una caja que no sea una de las dos que une. **Añadido:** cada fila es una caja; cada relación o conexión tiene su línea; y cada línea sale de su caja y llega a la otra (cada extremo puede quedar hasta a 12 px de su caja, el sitio de la punta de flecha) | P21 |
| Un verbo va en un tramo libre | Las mismas | Ningún verbo se monta sobre una caja (tampoco sobre las dos que une) ni sobre otro verbo. **Añadido:** cada relación con verbo que se dibuja tiene el suyo; las que van a la base o salen de ella no se dibujan ni lo llevan | P21 |
| El texto guarda su tamaño | Las mismas | La página declara que su letra más pequeña es de 13 px o más, en cada dibujo | P21 |
| Un rótulo largo pasa a dos líneas | Las mismas, y además una caja de componentes con un nombre de 70 letras | Cada rótulo de caja y de contenedor tiene una o dos líneas. Uno de una línea va entero. Uno de dos líneas forma, junto, el texto entero; si se corta, se corta al final de la segunda línea con «…» y el tooltip lleva el texto entero. El de 70 letras va en dos líneas | P21 |

### P22 · Horas y paradas en el plan

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Una pieza enseña sus horas | «Horas» y «Para antes» detrás de «Qué entrega»: P01 «0.5», P02 «0,75», P03 «1.5 h» | Cada pieza trae sus horas (0.5, 0.75 y 1.5). F1 suma 1.25 y F2, 1.5. **Añadido:** ningún aviso del plan nombra las columnas | P22 |
| **Añadido:** Una pieza enseña sus horas (la celda vacía no cuenta) | P01 «1», P02 y P03 vacías | P01 tiene 1 hora y las otras dos, ninguna. F1 suma 1 y F2 se queda sin horas | P22 |
| Una parada se marca | P02 lleva «Que Ana Pérez apruebe la lista de precios» en «Para antes»; las otras, nada | P02 trae ese texto y las otras, el texto vacío | P22 |
| Sin las columnas el plan se dibuja como hoy | La muestra tal cual | Las fases y sus piezas como en la 1.29.0, sin horas y sin «Para antes», y ningún aviso del plan nombra las columnas | P22 |

### P25 · La pestaña se queda al cambiar de proyecto

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Desarrollo se queda abierta | Un proyecto abierto en su pestaña Desarrollo; se elige otro proyecto de desarrollo | Se abre en Desarrollo | P25 |
| Sin la pestaña, vuelve a Estatus | Lo mismo, y se elige un proyecto que no es de desarrollo | Se abre en Estatus | P25 |

### Cómo se leyó lo que el escenario no precisa

1. «Ve el nombre y la línea corta debajo» (P19) se comprueba en lo que prepara el tablero, no en el dibujo.
2. Los roles de P19 siguen este orden de reglas:
   - lo externo, y la base de P20, son del resto;
   - lo que nombra la línea «Flujo:» es del flujo;
   - lo que recibe líneas y no saca ninguna es destino;
   - en una sección sin «Flujo:» (la infraestructura nunca la tiene), lo que tiene alguna línea es del flujo;
   - lo demás es del resto.
3. «Ninguna línea llega a la base» (P20) quiere decir también que ninguna sale de ella: una relación de la base hacia otra entidad no se dibuja, no lleva verbo y no cuenta para el rol de la otra. Así, en plugin-memoria, «Project → Area» no tiene línea.
4. Un verbo no puede montarse ni sobre las dos cajas que une.
5. «Un dibujo más ancho que la página» (P21): como la prueba no conoce la página, el mínimo de 13 px se pide en todos los dibujos.
6. Dos líneas de un rótulo forman, juntas, el texto entero, separadas por un espacio o sin él (una palabra partida).
7. La suma de horas de una fase cuenta solo las piezas que tienen horas. Si ninguna tiene, la fase se queda sin horas, no en cero.

### Lo que queda sabido

- P21 no mide el ancho del texto. Un rótulo de una sola línea que se salga de su caja no lo ve. Solo comprueba la forma del rótulo y que el de 70 letras pase a dos líneas.
- Que un contenedor con un rótulo largo pase a dos líneas solo se ve si alguna de las muestras lo tiene; no hay un caso hecho a propósito, como el de la caja de 70 letras.
- P15 busca los textos escritos exactamente así: `class="side-nombre"`, `data-tip="Proyecto de desarrollo"` y `title="Proyecto de desarrollo"`. No ve si el nombre de cada proyecto del menú usa esa clase: solo que la clase y su regla existen.
- P25 solo prueba lo que pasa al salir de Desarrollo. Desde otra pestaña (Estatus, Pasos, Registro, Qué hay) los escenarios no dicen con cuál se abre, y la prueba no lo mira.
- Las pruebas de P19, P20, P21 y P25 necesitan node en el PATH (el de la imagen de GitHub); sin él no se montan y salen con 2, no con fallo.
- Un cambio en las pruebas de P21 o en la muestra de P05 se corre también contra P19, P20, P25 y P41, que dependen de ellos (P41 importa de P21, que importa de P05).

## Fase F6 · El plan por estado, los datos por grupos, el sistema y el proceso en la ayuda

Escenarios aprobados por Juanjo Jiménez-Alfaro el 2026-11-25, en el plan (fase F6, versión 1.30.0): los de P26, P27, P28 y P33.

**Cómo están planteadas.** Igual que en F5, de tres maneras:

- **Lo que el tablero prepara.** A la organización de mentira se le cambia lo que pide el escenario, se genera el tablero y se lee lo que prepara para la pestaña Desarrollo. Los cambios son, según el caso:
  - un seguimiento con otros estados;
  - las columnas «Horas», «Para antes» y «Horas de cierre»;
  - una pieza técnica;
  - la tabla «Grupos»;
  - las columnas «Tipo» y «Corre en».
- **El dibujo.** P27 y P28 sacan de la página el trozo que calcula el dibujo, lo corren aparte (con node) y miden lo que sale. No abren ningún navegador.
- **La página como texto.** P26, P27, P28 y P33 buscan en la página del tablero textos escritos tal cual: la marca «técnica» (`data-marca="tecnica"`), los textos de la decisión pendiente, «Cierre de fase», el botón «Todas las relaciones», «Arquitectura técnica» y los artículos de la ayuda.

Hoy fallan todas las filas, y deben: la pieza que las pone en verde aún no existe. Las de P16 a P22 siguen pasando y no cambian.

**Una pieza «hecha»** es la unida o la entregada. Lo decidió quien acepta el 2026-11-25: una pieza cuenta como terminada cuando su pull request se une, entregada o no. «En curso» y «Revertida» están en curso.

**Lo que queda para la verificación en pantalla**, porque estas pruebas no lo ven:
- **P26.**
  - Que la pieza hecha salga atenuada, con palomita y plegada al final de su columna, y la que va en curso primero y resaltada.
  - Lo que dice la cabecera de la fase: horas que faltan del total y piezas hechas del total.
  - Que la fase cerrada salga plegada.
  - Que la línea «Cierre de fase» salga al pie de la columna, con sus horas (la prueba solo ve que la página trae ese texto).
  - Que la marca diga «decisión pendiente» en la tarjeta que la lleva, y que la ventana diga «Decisión pendiente antes de construirla: …» con su texto.
  - Que la tarjeta técnica lleve el rótulo «técnica».
- **P27.**
  - El borde grueso del centro y el discontinuo del aparte, tal como se ven.
  - Los colores de cada grupo.
  - Que el botón «Todas las relaciones» cambie el dibujo y, al pulsarlo otra vez, vuelvan los grupos.
  - Que la ventana de una entidad liste sus relaciones con otros grupos.
- **P28.**
  - Que la vista se titule «Arquitectura técnica» y no haya dibujo de componentes (la prueba solo ve que la página trae ese texto y que el trazado deja sin dibujo los componentes).
  - El color de cada tipo.
  - Que la ventana de una pieza enseñe las filas de sus componentes.
- **P33.**
  - Leer si los once pasos son los del proceso y van en su orden: la prueba solo los cuenta.
  - Que el texto diga que la auditoría es a criterio del auditor: la prueba solo busca la palabra «auditor».
  - Que la ayuda se abra y se lea bien.
- **Todas.** Que los dibujos de product-design y de plugin-memoria se lean bien con sus tablas nuevas.

### P26 · El plan por estado

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Los estados se distinguen | El último seguimiento de la muestra da P01 «unida», P02 «en curso», y P03 no sale | P01 es hecha, P02 en curso y P03 pendiente | P26 |
| **Añadido:** Los estados se distinguen (unida, revertida, otro estado y entregada en mayúsculas) | P01 «UNIDA», P02 «revertida», P03 «pendiente»; y aparte, P01 «ENTREGADA (1.0.0)» | La unida en mayúsculas es hecha, la revertida en curso, el otro estado es pendiente, y la entregada en mayúsculas es hecha | P26 |
| La fase dice lo que le falta | Horas: P01 0.5 (unida), P02 0.75, P03 1.5; sin «Horas de cierre» | F1: 1.25 de total, faltan 0.75, 1 de 2 piezas hechas. F2: 1.5, faltan 1.5, 0 de 1. Con F1 cerrada, le faltan 0. **Añadido:** con P01 «Revertida», F1 tiene 0 hechas y le faltan 1.25. Ningún aviso nombra «Horas de cierre» | P26 |
| **Añadido:** La fase dice lo que le falta (sin horas) | Ni horas ni cierre en ninguna parte | El total y lo que falta, sin horas (null); las piezas se cuentan igual | P26 |
| Una decisión pendiente se lee como tal | P02 lleva texto en «Para antes» | Ese texto sigue llegando, y la página tiene «decisión pendiente» y «Decisión pendiente antes de construirla:» | P26 |
| El cierre de la fase se ve | Las horas de arriba, y «Horas de cierre» F1 «0,5» y F2 «1.5 h» | F1: 1.75 de total, faltan 1.25 (0.75 + 0.5). F2: 3 de total, faltan 3. La página tiene «Cierre de fase» | P26 |
| **Añadido:** El cierre de la fase se ve (celda vacía, y sin horas en las piezas) | Sin horas en las piezas; cierre F1 vacío y F2 «1» | F1, todo sin horas; F2: cierre 1, total 1, faltan 1 | P26 |
| Una pieza técnica se marca | El bloque de P03 en «Hecha cuando» dice «Pieza técnica, sin escenarios.» en vez de su escenario | P03 es técnica y P01 y P02 no, y la página tiene la marca `data-marca="tecnica"` | P26 |
| Sin seguimiento, como hoy | «Seguimiento: por crear» y sin el archivo | Las fases y piezas como en la 1.29.1, sin estado ni grupo, sin piezas hechas ni horas que faltan, y el aviso del seguimiento que ya sale. **Añadido:** con horas, el total sí se cuenta | P26 |

### P27 · Los datos por grupos

La muestra cambia las entidades de «Datos» por seis nuevas, en cuatro grupos, por este orden de la tabla «Grupos»:
- **Enlaces**, que relaciona: se relaciona con Cosas, con el verbo «une».
- **Cosas**, el centro.
- **Registro**, debajo, que actualiza Cosas.
- **Acceso**, aparte. Tiene una relación con Cosas y otra entre sus dos entidades, para ver que ninguna se dibuja.

Dentro de Cosas, «cosa» vive en «carpeta». «enlace» → «cosa» y «acto» → «cosa» son relaciones entre grupos distintos. La línea «Detalle:» se quita, para que un aviso de desajuste de P10 no nombre a cada entidad nueva.

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Los grupos se apilan | La muestra de cuatro grupos | El tablero trae los grupos como la tabla. El dibujo va por grupos, con un contenedor por grupo en el orden de la tabla, de arriba abajo, y cada entidad dentro del suyo con su nombre y su «En corto». **Añadido:** ningún aviso, de ninguna parte, pide «Grupos» | P27 |
| El centro, y lo que va aparte | La misma | Solo el centro es grueso y solo el aparte es discontinuo, y ninguna línea toca el aparte ni sus cajas | P27 |
| Líneas entre grupos y dentro de uno | La misma | Una línea entre Enlaces y Cosas con «une», y otra entre Registro y Cosas con «actualiza». Una entre cosa y carpeta con «vive en». Ninguna entre cajas de grupos distintos. Las relaciones entre grupos distintos siguen en las entidades. Sin banda | P27 |
| El color y la leyenda salen de los grupos | Tres grupos (sin Acceso ni sus entidades) | Cada contenedor con un color distinto; la leyenda, una entrada por grupo con su «En corto» | P27 |
| Todas las relaciones, a petición | La de cuatro | Sin opciones, por grupos. Con «todas», por flujo, y el dibujo es el mismo que el de ese diseño sin grupos (el de la 1.29.1), donde enlace → cosa sí tiene línea. La página tiene el botón `data-accion="todas-las-relaciones"` | P27 |
| Sin la tabla, como hoy | La muestra de P05 tal cual | Sin grupos; un aviso, de cualquier parte, nombra «Grupos»; los datos van por flujo, con una caja por entidad y una línea por relación | P27 |
| Una entidad sin grupo se dice | Una entidad más, «suelta», del grupo «Huérfanos», que no está en la tabla | Un aviso la nombra; su caja no tiene grupo, no está en ningún contenedor y queda debajo del último | P27 |

### P28 · El sistema

La infraestructura de la muestra pasa a tener «En corto», «Tipo», «Proveedor», «Cuenta» y «Ambiente». Son cuatro piezas, en dos proveedores (Nube y Banco) y tres contenedores:
- **Dominio**, externo: solo llama, al Servidor web.
- **Servidor web**, corre: llama a «Base de datos (lee)», con verbo, y a «Pasarela», sin él.
- **Base de datos**, guarda: solo recibe.
- **Pasarela**, externo: solo recibe.

En «Componentes», una columna «Corre en» al final: Tienda web y API corren en Servidor web.

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Un dibujo en lugar de dos | Esa | El diseño dice que hay sistema; el trazado trae «sistema» y deja sin dibujo los componentes y la infraestructura; la llamada que titula la sección del dibujo dice «Arquitectura técnica» (#2026-11-27-4). **Añadido:** ningún aviso, de ninguna parte, pide «Tipo» | P28 |
| Marcos y orden | Esa | Tres contenedores; cada caja dentro de uno solo. Servidor web y Base de datos en el mismo, y Dominio y Pasarela en otros. Dominio queda más arriba que Base de datos y que Pasarela | P28 |
| El color dice el tipo | Esa | Cada pieza y su caja con su tipo; la leyenda, una entrada por cada uno de los tres tipos, con texto | P28 |
| **Añadido:** El color dice el tipo (celda vacía) | La celda «Tipo» de Base de datos, vacía | Su tipo es el texto vacío | P28 |
| Los componentes van dentro de su pieza | Esa | Servidor web lista Tienda web y API, en el orden de «Componentes», en el tablero y en su caja; las demás, ninguno; cada componente dice dónde corre | P28 |
| **Añadido:** Los componentes van dentro de su pieza (sin «Corre en») | Con «Tipo» y sin «Corre en» | Ningún componente dice dónde corre y ninguna pieza lista componentes | P28 |
| Un verbo en la línea es opcional | Esa | «Conecta con» sigue siendo la lista de nombres (Servidor web: Base de datos y Pasarela), y los verbos van aparte (solo «lee»). En el dibujo, tres líneas y un solo verbo, «lee», en Servidor web → Base de datos | P28 |
| Sin «Tipo», como hoy | La muestra de P05 tal cual | No hay sistema; el trazado trae «sistema» vacío (null) y los dibujos de componentes e infraestructura con una caja por fila; un aviso, de cualquier parte, nombra «Tipo» | P28 |

### P33 · El proceso en la ayuda

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| El proceso, de principio a fin | La página del tablero | El primer artículo de «Proyectos de desarrollo de software» es `desarrollo-proceso`. Su texto trae una lista ordenada de exactamente once pasos y, fuera de ella, «en cualquier momento», «no detiene» y la palabra entera «auditor» (no vale «auditoría») | P33 |
| Los roles son los de hoy | La misma | «Quién hace qué» (`desarrollo-roles`) dice Acepta, Construye, Administra, Audita, «nadie» y Recibe, y la fila de Audita (la de la tabla cuya primera celda es Audita, hasta su `</tr>`) no dice «decide» | P33 |

### Cómo se leyó lo que el escenario no precisa

1. «Hecha» (P26) es la pieza cuyo estado empieza por «Unida» o «Entregada». «En curso» es la que empieza por «En curso» o «Revertida». Lo demás es pendiente, también si no sale en la última entrada. Sin distinguir mayúsculas.
2. Lo que falta a una fase cuenta como cero las piezas sin horas y el cierre sin horas. Una fase cerrada no tiene nada que falte. Sin seguimiento, lo que falta y las piezas hechas no se cuentan (null); el total sí.
3. «Tiene que ser null» y «el texto vacío» se piden con la clave presente, no ausente.
4. La pieza técnica se reconoce por «pieza técnica, sin escenarios» en su bloque de «Hecha cuando», también con mayúscula al principio.
5. «Su nombre y su “En corto”» (P27) se comprueba en la caja: sus líneas, juntas, son el nombre y el «En corto» de la entidad.
6. «Ninguna línea toca el aparte» vale también para sus relaciones con otros grupos y para las de dentro de él.
7. «El dibujo por flujo de 1.29.1» (P27) se compara con el mismo diseño sin grupos, que es como la 1.29.1 lo dibujaba. Así no hace falta guardar la salida de la 1.29.1.
8. «Una pieza de la que solo salen líneas» (P28) es Dominio. «Las que solo reciben» son Base de datos y Pasarela. Servidor web, que llama y recibe, no se compara.
9. «Los verbos» de una pieza sin ninguna conexión con verbo van vacíos, `{}`.
10. La sección de un artículo de la ayuda (P33) es su clave `g:"…"`, como en la página de hoy. «en cualquier momento», «no detiene» y «auditor» se buscan sin distinguir mayúsculas, «auditor» como palabra entera; los nombres de los roles, tal cual.
11. La fila de Audita es la fila de la tabla cuya primera celda (`<td>` o `<th>`, sin sus etiquetas) es «Audita», desde su `<tr>` hasta su `</tr>`; en ella no puede aparecer «decide». Lo que haya después de la tabla no cuenta.
12. Si el trazado de la página devuelve null o nada (P27 y P28), las filas que miran el dibujo fallan y lo dicen.

### Lo que queda sabido

- Los avisos de «Grupos» y de «Tipo» se buscan en todos los avisos, de cualquier parte, tanto donde se piden como donde se pide que no los haya: así lo dice la enmienda al contrato tras la revisión de calidad.
- Que una relación entre grupos distintos «se liste en la ventana de cada una» solo se comprueba a medias: la relación sigue en las entidades del tablero, pero la ventana no se mira.
- El aviso de la entidad sin grupo se busca en cualquier parte, porque el contrato no dice en cuál.
- P27 y P28 necesitan node en el PATH; sin él no se montan y salen con 2.
- P33 cuenta los `<li>` de la lista, no lee los pasos: once pasos cualesquiera pasan.

## Fase F7 · El kit (P29, P30 y P31)

Escenarios aprobados por Juanjo Jiménez-Alfaro el 2026-11-25, en el plan (fase F7, versión 1.30.0). El octavo de P30, «El corredor propio es parte del kit», lo aprobó el mismo día y entró en el plan después. P32 es una pieza técnica y no tiene pruebas.

**Cómo están planteadas.**
- **P29 y P31, por la apertura.** Se prueban como P23: la organización de mentira de F2 se escribe en una carpeta temporal, se le cambia lo que pide el escenario y se abre la sesión del proyecto con la cuenta de Ana Pérez. P29 lee los avisos de la apertura, las líneas que empiezan por «Desarrollo:». P31 lee los pasos que la apertura pide a la sesión.
- **P29, también por el lector de la sección.** Es la parte del plugin que lee la sección «Desarrollo» y dice qué falta. La prueba mira qué personas lee en cada rol y qué da como pieza que falta. Lee además dos plantillas del kit como texto: la de la sección y la de las reglas del repositorio.
- **P30, por el control.** Como P01 a P03: cada prueba monta un repositorio de mentira con un pull request de mentira y corre sobre él la comprobación tal como la entrega el kit. Para Vitest, la prueba escribe un Vitest de mentira. Deja el informe con la misma forma que el de verdad, sin instalar nada. Para el corredor propio escribe un corredor de pocas líneas que responde según el contrato.

**Lo que P30 necesita para correr.** El arnés de las pruebas del control (`flujo.py`) tiene que dejar cambiar por caso el corredor que declara el control y hacer ejecutable un archivo del repositorio de mentira. Eso llega en un pull request «Kit · » aparte, que se une antes que este. Sin él, P30 juzga las filas de pytest y después dice que no se pudo montar porque falta el cambio del kit (salida 2, no fallo). Hacen falta también `node` y `npx` en el PATH, porque el Vitest de mentira es un guion de `node`; sin ellos, P30 tampoco se monta.

**Qué falla hoy.** Hoy fallan, y deben, las filas de «Audita: nadie», «Recibe», las plantillas y P31 «La apertura pide comprobar el repositorio». En P30, con el arnés del kit, fallan todas las filas menos cinco, porque el control aún no entiende `CORREDOR`. Ya pasan hoy las filas de lo que tiene que seguir igual: P29 «Los otros tres siguen contando», P31 «En otros proyectos no se dice nada», en P30 las cuatro de «Una pieza ya construida entra pasando» y «Una pieza sin construir tiene que fallar» con pytest, y una del identificador (abajo). Esa parte del control ya existe hoy: ya trata como activa a una pieza que el mismo pull request de escenarios añade a la lista. Esas filas son un seguro para que F7 no rompa lo que ya funciona.

«Audita: nadie» ya no da aviso hoy en la apertura. Su fila falla solo por el lector, que lee «nadie» como una persona.

**Queda para la verificación sobre la candidata**, porque estas pruebas no lo ven:
- que la sesión de verdad compruebe el repositorio que conecta y diga lo que falta;
- que la comprobación lea bien el informe de un Vitest de verdad (se ve al montarla en un repositorio que lo usa);
- que una prueba de Vitest marcada con `test.fails` no cuente como que pasa: el informe no la distingue de una que pasa;
- que la skill `desarrollo` diga cómo adopta el kit un proyecto con el código ya construido;
- que un seguimiento traiga lo que añade P32.

### P29 · Roles que sirven a cualquier proyecto

| Título que imprime | Situación | Tiene que pasar | Hoy |
|---|---|---|---|
| «Audita: nadie» no es algo que falte («Audita: nadie») | La sección del portal dice «Audita: nadie» | El lector no lee a nadie en Audita (lista vacía) y no la da como pieza que falta; ningún aviso «Desarrollo:» de la apertura nombra «Audita» | falla (por el lector; la apertura ya no avisa) |
| **Añadido:** lo mismo con «Audita: Nadie» y con «Audita: NADIE» | Lo mismo, con otras mayúsculas | Lo mismo | falla (por el lector) |
| «Recibe» es opcional | La sección sin línea «Recibe», y otra con «Recibe: Ana Pérez (ana@muestra.mx)» | En las dos, ni el lector ni la apertura avisan de «Recibe». En la segunda, el lector lee en Recibe una sola persona, con el mismo nombre y correo que lee en «Acepta», que en la muestra es la misma persona | falla |
| Los otros tres siguen contando («Acepta» vacía) | La línea «Acepta:» sin nada detrás | El lector da «Acepta» como pieza que falta y un aviso «Desarrollo:» nombra «Acepta» | ya pasa |
| Los otros tres siguen contando («Construye» vacía) | Lo mismo con «Construye» | Lo mismo | ya pasa |
| Los otros tres siguen contando («Administra» vacía) | Lo mismo con «Administra» | Lo mismo | ya pasa |
| **Añadido:** Los otros tres siguen contando («Audita» vacía) | «Audita:» sin nada, ni «nadie» | Lo mismo: vacía no es «nadie» | ya pasa |
| Las plantillas llevan los roles | Las plantillas del kit | La plantilla de la sección trae las cinco líneas en su ejemplo y una viñeta por rol en «Qué hace cada rol», cada una con texto detrás del nombre. Las reglas del repositorio dicen «pregunta a quien acepta» y no «pregunta a quien audita». **Añadido, del encargo y no del escenario:** la viñeta de Audita dice «nadie» y ya no dice «da el sí» ni «decide en los puntos de control»; la de Acepta dice «puntos de control» y «da el sí» | falla |

### P30 · Un control, un corredor por proyecto

| Título que imprime | Situación | Tiene que pasar | Hoy, con el arnés del kit |
|---|---|---|---|
| Las mismas reglas con cualquiera de las dos (pytest) | El control declara `CORREDOR: pytest`; un pull request de código con la prueba de P05 (activa) fallando y la de P06 pasando | El control declara pytest; queda en rojo y el error nombra a P05, no a P06 | falla (el control no declara `CORREDOR`) |
| Las mismas reglas con cualquiera de las dos (vitest) | El mismo pull request, con `CORREDOR: vitest` y pruebas `.test.ts` | Lo mismo | falla |
| **Añadido:** Las mismas reglas con cualquiera de las dos (vitest, P05 «passed» con una prueba saltada) | El informe da el archivo de P05 como `passed`, con una prueba `skipped` | Queda en rojo y el error nombra a P05: una prueba saltada no cuenta, como con pytest | falla |
| El corredor propio de un proyecto (falla P05) | Un corredor del proyecto dice «FALLA» de la prueba de P05 | Queda en rojo y el error nombra a P05, no a P06 | falla |
| El corredor propio de un proyecto (todas pasan) | El corredor dice «PASA» de todas | Corren las dos y queda en verde | falla |
| El corredor propio de un proyecto («Escenarios · P05» sin añadirla, su prueba dice FALLA: verde) | Con el corredor propio, «Escenarios · P05» trae la prueba de P05 y no la añade a la lista; el corredor dice «FALLA» | Corre y queda en verde | falla |
| El corredor propio de un proyecto («Escenarios · P05» sin añadirla, su prueba dice PASA: rojo) | Lo mismo; el corredor dice «PASA» | Corre y queda en rojo | falla (no corre) |
| **Añadido:** El corredor propio de un proyecto (sale con 3) | El corredor sale con 3 | El corredor se llamó; queda en rojo y un error dice que las pruebas «no se pudieron correr» | falla |
| **Añadido, del encargo:** El corredor propio de un proyecto (sin SUFIJO) | Corredor propio con `SUFIJO` sin declarar, y con `SUFIJO` vacío | En los dos, queda en rojo y un error dice «SUFIJO» | falla |
| Un archivo que no se corrió cuenta como no corrido (el corredor propio no escribe su línea) | El corredor no escribe nada de la prueba de P05 | Queda en rojo y un error nombra el archivo | falla |
| **Añadido:** lo mismo (el corredor propio dice NO_CORRIO) | El corredor dice «NO_CORRIO» de ella | Lo mismo | falla |
| Un archivo que no se corrió cuenta como no corrido (el informe de Vitest no lo trae) | El informe de Vitest no trae la prueba de P05 | Lo mismo | falla |
| Sin corredor no hay control (CORREDOR vacío) | `CORREDOR` vacío | Queda en rojo y un error dice «CORREDOR» | falla |
| **Añadido:** Sin corredor no hay control (CORREDOR con otra palabra) | `CORREDOR: jest` | Lo mismo | falla |
| Sin corredor no hay control (vitest sin el archivo de CONFIG) | `CORREDOR: vitest` y el archivo de `CONFIG` no existe | Queda en rojo y un error dice «CONFIG» | falla |
| Un identificador puede acabar en letra («H22a · …» toma solo las de H22a) | H22, H22a y H22b con prueba; solo H22a activa y su prueba pasa; las otras fallarían | Corre solo la de H22a y queda en verde | falla |
| **Añadido:** Un identificador puede acabar en letra («H22 · …» no toma las de H22a ni H22b) | Al revés: H22 activa y pasando | Corre solo la de H22 y queda en verde | ya pasa |
| Un identificador puede acabar en letra («Escenarios · H22a» con un archivo de H22b) | «Escenarios · H22a» trae `H22a_x.py` y `H22b_x.py` | Queda en rojo; un error nombra `H22b_x.py` y ninguno `H22a_x.py` | falla (hoy no reconoce ninguno de los dos) |
| **Añadido:** Un identificador puede acabar en letra («Escenarios · H22a» con solo lo suyo) | «Escenarios · H22a» trae solo `H22a_x.py`, que falla como debe | Queda en verde | falla |
| Una pieza ya construida entra pasando (la añade y su prueba pasa: verde) | «Escenarios · P05» añade P05 a la lista y su prueba pasa | Queda en verde | ya pasa |
| Una pieza ya construida entra pasando (la añade y su prueba falla: rojo) | Lo mismo, y su prueba falla | Queda en rojo | ya pasa |
| Una pieza sin construir tiene que fallar (no la añade y su prueba falla: verde) | «Escenarios · P05» sin tocar la lista; su prueba falla | Queda en verde | ya pasa |
| Una pieza sin construir tiene que fallar (no la añade y su prueba pasa: rojo) | Lo mismo, y su prueba pasa | Queda en rojo | ya pasa |
| El corredor propio es parte del kit (un pull request que no es «Kit · » lo cambia: rojo) | «P09 · …» cambia el corredor propio, y todas las pruebas pasan | Queda en rojo y un error nombra la ruta del corredor | falla |
| El corredor propio es parte del kit (un pull request «Kit · …» lo cambia: verde) | «Kit · …» cambia solo el corredor propio, y todas las pruebas pasan | Queda en verde | falla |

### P31 · El kit, montado o dicho

| Título que imprime | Situación | Tiene que pasar | Hoy |
|---|---|---|---|
| La apertura pide comprobar el repositorio | Se abre el portal, con «Repositorios: muestra/portal» | El paso que nombra `muestra/portal`, o el de antes o el de después, dice en un mismo paso «comprueba», «CLAUDE.md», «control», «corredor», «una línea» y «falta» | falla |
| En otros proyectos no se dice nada | Se abre la campaña, sin «Desarrollo» | Lo que la apertura pide responder tiene pasos, y no dice «corredor» ni «control de pruebas» | ya pasa |

Lo que pedía P23 sigue ahí: sus pruebas siguen en la lista de activas y siguen pasando.

### Cómo se leyó lo que el escenario no precisa

1. «La apertura no avisa» (P29) se mira en dos sitios: en el lector de la sección (no da el rol como pieza que falta) y en las líneas «Desarrollo:» de los avisos de la apertura (ninguna nombra el rol).
2. «Lee a la persona como en los otros roles» (P29): mismo nombre y mismo correo que la misma persona escrita en «Acepta». El usuario de GitHub no se compara, porque la muestra no lo trae.
3. En las plantillas (P29), las palabras se buscan sin distinguir mayúsculas, y la viñeta de un rol llega hasta la siguiente viñeta. «Explica las cinco líneas» es que cada viñeta tiene texto detrás del nombre.
4. «Junto a él» (P31) es el paso de antes o el de después del que nombra los repositorios. Todas las palabras tienen que estar en un mismo paso. «CLAUDE.md» se busca tal cual; las demás, sin distinguir mayúsculas.
5. En la campaña (P31), «no dice nada» se mira solo en lo que la apertura pide responder, no en toda la apertura.
6. «Nombra la pieza», «nombra el archivo», «nombra el corredor» y «dice qué falta» (P30) se buscan en los mensajes de error de la comprobación, como en P01 a P03, no en toda su salida: «CORREDOR», «CONFIG» y «SUFIJO» tal cual; «no se pudieron correr», sin distinguir mayúsculas.
7. Con un corredor propio, los archivos de prueba terminan en el `SUFIJO` que declara el proyecto. La prueba usa `_test.go`, que no es `.py` ni `.test.ts`, para que no pase por el nombre de hoy.
8. El Vitest de mentira toma los archivos que le pasan como Vitest, que filtra por la ruta. Sin argumentos los toma todos.
9. «Las mismas reglas» del corredor propio se prueban también en el pull request de escenarios: la pieza sin construir tiene que fallar con él como con pytest.

### Lo que queda sabido

- P30 necesita el arnés del pull request «Kit · » de `flujo.py`, que se une antes que este, y `node` y `npx` en el PATH.
- La forma de los argumentos con que el control llama a Vitest («…» en el contrato) no está cerrada: el Vitest de mentira admite archivos, carpetas o trozos de ruta.
- Las pruebas buscan palabras, no el sentido: un paso que dijera «no compruebes el corredor» también pasaría. Eso lo ve quien verifica. «Una línea» ya está hoy en el paso de la apertura que nombra los repositorios; lo que le falta es lo demás.
- `test.fails` de Vitest no se distingue en el informe: queda para la verificación.
- Una prueba marcada `todo` cuenta como una saltada en el contrato, pero el Vitest de mentira solo da `skipped`: un control que mirase solo `skipped` pasaría. Queda para la verificación.
- Con el corredor propio, todas las filas tienen solo archivos que terminan en el sufijo declarado: no hay una fila que compruebe que un archivo de la pieza con otro final (`P05_notas.md`) se queda fuera. Queda para la verificación.
- Las filas de P30 que ya pasan hoy (las cuatro de la pieza construida y sin construir con pytest, y una del identificador) no prueban nada nuevo de P30: esa parte del control ya existe y son un seguro para que no se rompa.

## P39 · Un control sin agujeros

Escenarios aprobados por Juanjo Jiménez-Alfaro el 2026-11-26, en el plan («### P39»). Seis escenarios, un archivo por escenario.

**Cómo están planteadas.** Como P30: cada prueba monta un repositorio de mentira con un pull request de mentira y corre sobre él la comprobación tal como la entrega el kit, con `flujo.comprobar(…, env_wf=…, ejecutables=…)`. Con Vitest, la prueba escribe un Vitest de mentira (un guion de `node`) que deja un informe con la forma del de verdad. Con el corredor propio, escribe uno de pocas líneas que responde según el contrato. Nada se instala: el «plugin async» es uno de pocas líneas en el `conftest.py` de la carpeta de mentira, que corre con asyncio las pruebas async con su marca (`asincrona`) y deja las demás, como pytest-asyncio o anyio. En CI solo está pytest.

**Qué se mira.** El código de salida (0 verde, otro rojo) y, en los rojos, las líneas de error de la comprobación (no toda su salida). Las palabras exactas del mensaje no están decididas: se busca la idea con pocas palabras, sin distinguir mayúsculas.

**Qué falla hoy.** Fallan, y deben, los escenarios 1, 3 (con pytest y con Vitest), 4 y 5. Ya pasan hoy el 2 y el 6, que son un seguro, y la fila del 3 con corredor propio (abajo).

**El escenario 3 con corredor propio solo exige rojo.** El corredor da «NO_CORRIO» del archivo que se saltó, y el control no puede distinguir una prueba saltada de un archivo que no corrió. Por eso la fila no mira qué dice el error, y hoy ya pasa.

**Necesita** pytest en el `python3` del PATH, y `node` y `npx` para las filas de Vitest (3 y 6), como P30.

| Título que imprime | Situación | Tiene que pasar | Hoy |
|---|---|---|---|
| A file at the root does not stand in for pytest (pytest.py en la raíz, P05 activa falla) | P05 y P06 activas; la prueba de P05 falla y la de P06 pasa. Un pull request de código «P09 · …» añade en la raíz un `pytest.py` que escribe «PASSED …» de cada archivo y sale con 0 | Queda en rojo y un error nombra a P05 | falla (hoy queda en verde: el `pytest.py` de la raíz ocupa el sitio de pytest) |
| Code that is not installed is still found (Python actual, …) | P05 activa; su prueba importa, dentro de la prueba, el paquete `app` de la raíz, que no está instalado. Pull request de código | La prueba de P05 corre con ese Python, importa `app` y la comprobación queda en verde | ya pasa |
| Code that is not installed is still found (Python 3.9) | Lo mismo, con un `python3` que llama al `python3.9` del PATH | Lo mismo | ya pasa (si no hay `python3.9` con pytest, la prueba dice «sin comprobar» y no cuenta esta fila) |
| Scenarios that only skip are not green (pytest, pytest.skip) | «Escenarios · P05»: `P05_falla.py` falla; `P05_salta.py` solo hace `pytest.skip` | Queda en rojo, un error dice que no corrieron todas («salta», «sin correr» o «corrieron») y ninguno dice «no se pudo cargar» | falla |
| Scenarios that only skip are not green (pytest, pytest.importorskip) | Lo mismo, y `P05_salta.py` hace `pytest.importorskip` de un módulo que no está | Lo mismo | falla |
| Scenarios that only skip are not green (pytest, xfail) | Lo mismo, y `P05_salta.py` lleva una prueba `xfail` | Lo mismo | falla |
| Scenarios that only skip are not green (Vitest, una prueba skipped) | Lo mismo con Vitest: el informe da `P05_falla.test.ts` como `failed` y `P05_salta.test.ts` con su única prueba `skipped` | Lo mismo | falla |
| Scenarios that only skip are not green (corredor propio, NO_CORRIO del archivo saltado: solo rojo) | Lo mismo con el corredor propio: dice «FALLA» de `P05_falla` y «NO_CORRIO» de `P05_salta` | Queda en rojo; no se mira qué dice el error (abajo) | ya pasa |
| A failure in preparation is not the piece missing (ERROR en una fixture) | «Escenarios · P05»: la fixture de su prueba importa lo que la pieza aún no tiene y lanza `ModuleNotFoundError`; pytest da `ERROR …::prueba` | Queda en rojo; una línea de error dice «prepar» (falló la preparación) y, en la misma línea, «dentro» o «en la prueba» (se importa dentro de la prueba); ninguna dice «no se pudo cargar» | falla (hoy cuenta el `ERROR` como un fallo de la prueba y queda en verde) |
| An async test pytest cannot run (sin plugin async) | «Escenarios · P05»: una prueba `async def` con `@pytest.mark.asyncio` y ningún plugin async | Queda en rojo; una línea de error dice «async» y, en la misma, «plugin» o «marca»; ninguna culpa a la pieza («pieza aún no», «se importa dentro») | falla |
| An async test pytest cannot run (con el plugin y sin su marca) | Lo mismo, con el plugin de pocas líneas en el `conftest.py` y la prueba sin su marca | Queda en rojo; una línea de error dice «async» y «marca»; ninguna culpa a la pieza | falla |
| What already passed still passes (pytest) | P05 y P06 activas, sus pruebas pasan; pull request de código | Corren las dos y queda en verde | ya pasa |
| **Añadido:** What already passed still passes (pytest, con fixture, async con su plugin y su marca, y parametrizada) | P05 activa con una `conftest.py` (una fixture y el plugin async) y pruebas que la usan: con fixture, async con su marca y una parametrizada | Corren todas y queda en verde | ya pasa |
| What already passed still passes (Vitest) | Lo mismo con Vitest, las dos `passed` | Lo mismo | ya pasa |
| What already passed still passes (corredor propio) | Lo mismo con el corredor propio, las dos «PASA» | Lo mismo | ya pasa |

### Cómo se leyó lo que el escenario no precisa

1. «Names the piece» (1) es que una línea de error nombra a P05.
2. «On Python 3.9 and on the current one» (2): la actual es el `python3` del PATH, con el que corre el arnés. Para 3.9 la prueba pone delante del PATH un `python3` que llama al `python3.9` del PATH, y comprueba que la prueba de P05 corrió con 3.9.
3. «Says that not every test ran» (3) se busca con «salta», «sin correr» o «corrieron», y el error no puede ser el de hoy para un archivo que no carga («no se pudo cargar»). Con el corredor propio, «el archivo saltado» es uno del que el corredor dice «NO_CORRIO», como dice el encargo, y solo se exige rojo.
4. «Gives `ERROR` in a fixture» (4): la fixture está en el mismo archivo de prueba e importa lo que la pieza aún no tiene, que es el caso de verdad que este mensaje tiene que explicar. Una línea de error dice «prepar» y, en la misma, «dentro» o «en la prueba»; ninguna dice «no se pudo cargar».
5. «No async plugin» (5): la prueba lleva la marca de pytest-asyncio sin que el plugin esté, que es como suele pasar. «The plugin or the mark is missing» es una línea de error con «async» y «plugin» o «marca»; con el plugin y sin su marca, «async» y «marca». «Not the piece» es que ninguna línea de error dice «pieza aún no» ni «se importa dentro», que es como hoy culpa a la pieza.
6. «Each of the three runners» (6) es pytest, Vitest y un corredor propio, en pull requests de código.

### Lo que queda sabido

- El escenario 2 y el 6 ya pasan hoy: son un seguro para que lo que cierra el 1 (que pytest no se tome de la raíz) no deje de encontrar el código de la raíz, y para que nada de P39 ponga en rojo pruebas que pasan.
- El escenario 5 depende de la versión de pytest: con la de CI (8.3.5) una prueba async sin plugin se salta, y hoy la comprobación queda en rojo diciendo que el archivo «no corrió»; con pytest 8.4 o posterior la prueba falla, y hoy queda en verde. Las dos fallan hoy esta prueba: con 9.x queda en verde, y con 8.3.5 su error culpa a la pieza y no dice «async».
- La mitad de Python 3.9 del escenario 2 no corre en CI: allí no hay un `python3.9` con pytest y la fila queda «sin comprobar». La verificación corre ese archivo con un `python3.9` con pytest en el PATH.
- El plugin async es uno de pocas líneas, no pytest-asyncio ni anyio de verdad: que el mensaje acierte con ellos queda para la verificación.
- Las pruebas buscan palabras, no el sentido: un mensaje que diga «plugin» por otra razón también pasaría. Eso lo ve quien acepta.
- El Vitest de mentira, el corredor propio de mentira y el plugin async de pocas líneas están copiados en los archivos que los usan (3, 5 y 6, como en P30). No van en `flujo.py` porque cambiar `flujo.py` lo saca de este pull request: tendría que ir solo, en un «Kit · ».
- La prueba del escenario 2 usa `flujo._comprobado`, que es privado del arnés, para que vuelva a mirar pytest con el `python3` de 3.9. Si el arnés cambia ese nombre, la prueba se rompe y sale con 2, no con un fallo.
- Sin `node` y `npx` en el PATH, los archivos de los escenarios 3 y 6 salen con 2 (no se pudieron montar), igual que P30.
- Con Vitest, `test.fails` y las demás formas de esperar un fallo se ven en el texto del archivo, no en el informe, y el Vitest de mentira no las ejercita: las comprobó la verificación de la 1.31.2 con Vitest 2 a 5 (#2026-11-27-5 y -6).
- Un aviso de prueba async hecho buscando palabras sin más en la salida de pytest podría poner en rojo un pull request de escenarios válido: uno con una prueba async, con su plugin y su marca, que falla porque la pieza aún no existe. Estas pruebas no tienen esa fila. Lo mira la verificación.
- Otro módulo de la raíz que pytest importe más tarde, como un `pdb.py`, ocuparía el sitio del de verdad igual que el `pytest.py` del escenario 1. Sin fila propia: la 1.31.2 lo cierra poniendo la raíz una sola vez, por su ruta real, al final de `sys.path` antes de cargar pytest (#2026-11-27-3).

## P41 · Lo archivado, aparte y marcado

Escenarios aprobados por Juanjo Jiménez-Alfaro el 2026-11-27, en el plan: los de P41. P40 se quitó (#2026-11-27-9: la ventana de la fase ya muestra el resumen).

**Cómo están planteadas.** Como en F5 y F6, de dos maneras:

- **Un trozo de la página, corrido aparte.** La prueba saca de la página del tablero el trozo que arma el menú y lo corre con node, sin abrir un navegador. Le da listas de áreas y proyectos escritas en la propia prueba, y mira qué áreas y proyectos salen, en qué orden, cuáles van marcados como archivados o cerrados, y qué dice el botón. El trozo corre solo: no puede usar nada de fuera de él (otras funciones ni variables de la página).
- **La página como texto.** Que ya no traiga el botón de hoy («Mostrar áreas archivadas» / «Ocultar áreas archivadas»), que la pieza sustituye por el nuevo. Que traiga el rótulo «Archivado» y la marca de lo archivado, escrita «data-archivado» o «dataset.archivado». Y que nombre el trozo del menú (`menuArchivado`) fuera de él, para que no baste un trozo que nadie usa.

Hoy fallan todas las filas, y deben: la página aún no trae ese trozo, ni el rótulo, ni la marca.

**Lo que queda para la verificación en pantalla**, porque esta prueba no lo ve:
- El gris de la tarjeta y del título de un área archivada, su sitio al final bajo «Archivado» y «Archivada» donde va la cuenta.
- El gris del proyecto cerrado y la etiqueta «cerrado» a su derecha.
- Que el área vigente no cambie de sitio, tarjeta, título ni cuenta.
- Que el botón esté al pie del menú.
- Que la página guarde la elección del botón y que sobreviva a cerrar y abrir la página en el mismo navegador. La prueba solo ve que, con el botón encendido, el botón dice «Ocultar lo archivado».
- Que la página use de verdad el trozo del menú para pintarlo: la prueba solo ve que lo nombra fuera de él.
- Que la regla de área archivada sea la de `archivada()` de hoy, la misma en el menú y en el resto de la página (la cuenta del área, lo que se ve al abrir un proyecto): un área que se puede leer, con proyectos, todos cerrados y ninguno restringido. El trozo del menú recibe solo las áreas y proyectos que se le pasan, así que lo de leer y restringir lo decide la página antes de llamarlo.

La carpeta de la prueba tiene, en este orden: el área «archivo», archivada, con un proyecto cerrado; y el área «ventas», vigente, con un proyecto cerrado y después uno abierto. El orden está puesto así para ver que lo archivado pasa al final.

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Hidden by default | Esa carpeta, botón apagado | Solo sale «ventas», con su proyecto abierto; el botón dice «Mostrar lo archivado (2)». **Añadido:** con dos proyectos cerrados en el área archivada, sigue diciendo (2). La página ya no trae «Mostrar áreas archivadas» ni «Ocultar áreas archivadas», el botón de hoy | P41 |
| Shown, each one says what it is | La misma, botón encendido | «ventas» primero, con el abierto y después el cerrado, marcado como cerrado; «archivo» al final, marcada como archivada. La página tiene «Archivado», «data-archivado» o «dataset.archivado», y nombra el trozo del menú fuera de él | P41 |
| The choice stays | Botón encendido | El botón dice «Ocultar lo archivado» | P41 |
| Nothing archived, no button | Tres áreas sin nada cerrado. **Añadido:** una de ellas sin proyectos | Con el botón apagado y encendido: no hay botón, y salen todas las áreas, ninguna como archivada, con todos sus proyectos | P41 |

### Cómo se leyó lo que el escenario no precisa

1. El número del botón cuenta las áreas archivadas y los proyectos cerrados de áreas vigentes, como dice el contrato: los proyectos de un área archivada no suman aparte.
2. De un área archivada, la prueba solo mira que salga al final y marcada, no la lista de sus proyectos.
3. El orden de los proyectos de un área es el de su lista en la guía.
4. Un área sin proyectos no es archivada.

### Lo que queda sabido

- La página ya tiene hoy la palabra «Archivada», la etiqueta «cerrado» y la clave `ver-archivadas`: buscarlas no probaría nada, y la prueba no las busca. Lo ve la verificación.
- Que «Archivado» y la marca estén en el menú, y no en otra parte de la página, no lo distingue la prueba: lo ve la verificación. Un comentario que diga «data-archivado» ya cumple la fila; que la marca esté de verdad en lo que pinta el menú lo ve la verificación.
- P41 necesita node en el PATH; sin él no se monta y sale con 2.

## Fase F3 · Lo construido en los dibujos, la escritura para quien construye y los escenarios esenciales (P34, P35 y P36)

Escenarios aprobados por Juanjo Jiménez-Alfaro el 2026-11-27, en el plan (fase F3, versión 1.32.0): los de P34, P35 y P36.

**Cómo están planteadas.** De tres maneras, como en F5 y F6:

- **Lo que el tablero prepara (P34).** A la organización de mentira de P05 se le pone una columna «Pieza» al final de «Datos», «Componentes» e «Infraestructura» (en esta, la primera columna, el nombre de la caja, pasa a llamarse «Recurso»), y otra última entrada de seguimiento, con los siete puntos de la plantilla del seguimiento. Se genera el tablero y se lee lo que prepara para la pestaña Desarrollo: cada caja con su pieza y su estado, las piezas que el plan no tiene y lo unido fuera del diseño.
- **Lo que dice la apertura (P35).** Se abre la sesión del portal de mentira con una cuenta, como en P23, y se lee lo que la apertura le dice a la sesión. Para tener personas distintas en cada rol, la guía tiene cuatro personas con cuenta (Ana, Luis, Marta y Pablo); acepta Marta, audita Pablo, y construye y administra Ana.
- **Lo que lee el plan (P36).** Se le pasa al lector del plan el plan de mentira de P05, con títulos que terminan en «(esencial)» y con F1 cerrada y F2 en curso, y se mira qué escenarios marca y qué lista para la verificación de una fase.
- **La página como texto (P34 y P36).** Que la página del tablero traiga la marca del estado de las cajas (`data-estado`), nombre lo que va bajo el dibujo (`piezas_desconocidas` y `fuera_del_diseno`) y traiga la marca del escenario esencial (`data-esencial`).

Hoy fallan todas las filas, y deben: la pieza que las pone en verde aún no existe.

**Lo que queda para la verificación en pantalla**, porque estas pruebas no lo ven:
- **P34.** El borde y la intensidad de cada caja según el estado de su pieza, y que su color siga diciendo su grupo o tipo. Que la caja de una pieza desconocida salga sin estado. Que bajo el dibujo salgan, con sus palabras, la pieza que el plan no tiene y lo unido fuera del diseño (la prueba solo ve que la página nombra esos datos).
- **P35.** Que la sesión conecte de verdad los repositorios con escritura, que no conecte nada a quien no construye, y que los conecte solo para leer cuando lo que se pide necesita el código.
- **P36.** La marca de esencial en la ventana de la pieza (la prueba solo ve que la página trae `data-esencial`). Y el cuarto escenario entero: que la sesión no pida el sí cuando el informe de la verificación trae un esencial de una fase anterior fallado, y que diga cuál. El escenario dice que lo comprueba la verificación, no una prueba; P36 lo imprime como «queda para la verificación» y no lo cuenta.

### P34 · Lo construido, en los dibujos

La columna «Pieza» de la muestra: cliente P01, pedido P03, producto P02 y categoria sin pieza; Tienda web P01, API P02, Motor de pagos P03 y Panel interno sin pieza; Servidor web P02, Base de datos P01 y Dominio sin pieza. En «Infraestructura», con la columna del plan, la primera se llama «Recurso» («| Recurso | Para qué | Dónde | Conecta con | Pieza |»), como decidió quien acepta (shared-memory/plugin-memoria#2026-11-27-13).

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Each box takes its piece's state | La columna «Pieza» en las tres tablas; la última entrada da P01 `entregada`, P02 `en curso` y P03 `pendiente`, y su punto 4 dice «- pendiente de revisar» | Cada caja trae su pieza y el estado de esa pieza, tal cual; la caja sin pieza, los dos vacíos (null). El grupo y lo demás de cada caja, como hoy. Ninguna pieza desconocida y ningún aviso que nombre «Pieza». La página tiene `data-estado`. **Añadido:** lo unido fuera del diseño va vacío («pendiente de revisar» no es una cosa unida); y con otra última entrada que no nombra P03 (la anterior sí), las cajas de P03 salen sin estado | P34 |
| Without the column, as today | La muestra tal cual | Cada caja trae pieza y estado vacíos (null), ninguna pieza desconocida, ningún aviso que nombre «Pieza», y el diseño se lee como en P05 | P34 |
| **Añadido:** Without the column, as today (an «Infraestructura» without «Recurso»: its «Pieza» is the box's name) | Un diseño de antes: la muestra de P05 tal cual, cuya «Infraestructura» empieza por «Pieza» y no tiene «Recurso»; la última entrada da P01 `entregada`, P02 `en curso` y P03 `pendiente` | Servidor web, Base de datos y Dominio salen con su nombre y su «Conecta con» de P05, sin pieza ni estado (null), y ninguno de esos nombres está en las piezas desconocidas | P34 |
| A piece the plan does not have | «pedido» dice P09, que el plan no tiene. **Añadido:** el seguimiento da P09 `entregada` | «pedido» sale sin estado; las demás cajas, con el suyo. P09 está en las piezas desconocidas. La página nombra `piezas_desconocidas` | P34 |
| What was merged outside the design | La última entrada lleva los siete puntos; el 4, «4. Lo que lo unido añade y el diseño no tiene:» y debajo «- Servicio de cupones (muestra/portal#41)» y «- Exportación a Excel (muestra/portal#43)» | Lo unido fuera del diseño es la lista de esas dos líneas. **Añadido:** no trae el punto 4 de la entrada anterior («- Buscador de pedidos (muestra/portal#12)») ni nada de los otros seis puntos de la última. La página nombra `fuera_del_diseno` | P34 |

### P35 · Los repositorios, conectados solo para quien construye

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Whoever builds gets write access | Ana, en «Construye» con su correo, abre la sesión | Un paso de la apertura nombra el repositorio y pide conectarlo «con escritura» «antes de trabajar», como hoy. **Añadido:** con Marta, que solo acepta, ninguna línea dice «escritura» (sin esto la fila pasaría hoy, que todos reciben escritura) | P35 |
| Anyone else gets nothing at opening (only in Acepta) | Abre Marta | Ninguna línea de la apertura dice «escritura», en ninguna forma, y un paso dice «solo para leer» | P35 |
| Anyone else gets nothing at opening (only in Audita) | Abre Pablo | Lo mismo | P35 |
| Anyone else gets nothing at opening (in no role) | Abre una cuenta que no está en ningún rol ni en «Quién es quién» | Lo mismo | P35 |
| Several builders | «Construye: Ana Pérez (ana@muestra.mx) · Marta Ruiz (marta@muestra.mx)» | Con Ana y con Marta, la apertura pide conectar con escritura. Pasa hoy, que todos la reciben: ver «Lo que queda sabido» | P35 |
| A builder without an account is found by name | «Construye: Luis Gómez», y Luis con su correo en «Quién es quién» | Con Luis, la apertura pide conectar con escritura. **Añadido:** con Ana, que ya no construye, ninguna línea dice «escritura» | P35 |
| A builder without an account is found by name (the name is not in «Quién es quién») | «Construye: Rosa Vidal», que no está en «Quién es quién» | Con Ana, Marta, Luis y la cuenta sin rol, ninguna línea dice «escritura», y la apertura nombra a Rosa Vidal y «Quién es quién» | P35 |

### P36 · Los escenarios esenciales, antes de cada sí

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| An essential scenario is marked | El primer escenario de P01 termina en «(esencial)». **Añadido:** el de P02 lo lleva a mitad: «Cada producto (esencial) muestra su precio» | Ese escenario es esencial y los otros tres no (tampoco el de P02). La página tiene `data-esencial` | P36 |
| The verification gets the essential ones of earlier phases, apart | F1 cerrada, con los dos escenarios de P01 esenciales (el de P02 no); F2 en curso | Para F2: su escenario y, aparte, los dos de P01 con su pieza | P36 |
| **Añadido:** The verification gets the essential ones of earlier phases, apart (one of the phase's own) | Lo mismo, y el escenario de P03 (F2) también esencial | Para F2: el de P03 va con los de la fase, no aparte; aparte, los dos de P01 | P36 |
| No essential ones, only the phase's | F1 cerrada sin ningún esencial; F2 en curso | Para F2: su escenario y ningún esencial. **Añadido:** para F1, que no tiene fases antes, sus tres escenarios y ningún esencial, aunque el escenario de P03, de F2 (una fase posterior), sea esencial | P36 |
| (no se cuenta) A failing essential one stops the yes | — | Lo comprueba la verificación: la prueba lo imprime como «queda para la verificación» | la verificación |

### Cómo se leyó lo que el escenario no precisa

1. **P34.** La columna «Pieza» lleva el identificador de la pieza del plan («P01»), y va al final de cada tabla; en «Infraestructura», la primera columna se llama entonces «Recurso». Un diseño sin «Recurso» es de antes: su «Pieza» es el nombre de la caja y no hay pieza del plan. Una celda vacía se lee como sin pieza: la prueba acepta null o «» para la pieza, y exige null para el estado.
2. **P34.** El estado de una caja es el de su pieza en la última entrada del seguimiento, tal cual lo escribe; una pieza que esa entrada no nombra, o que el plan no tiene, deja la caja sin estado (null), aunque el seguimiento la nombre.
3. **P34.** «Lo que el seguimiento encontró unido y fuera del diseño» es lo que la última entrada dice en su punto 4. La entrada de la prueba sigue los siete puntos de la plantilla (`seccion-desarrollo.md`), con la tabla en el 2, y el punto 4 con la forma fija que decidió quien acepta (shared-memory/plugin-memoria#2026-11-27-14): «4. Lo que lo unido añade y el diseño no tiene:» y debajo una línea «- <nombre> (<repositorio>#<número>)» por cosa, o «- nada», o «- pendiente de revisar» mientras el subagente seguimiento no lo ha revisado. Lo unido fuera del diseño son los nombres de esas líneas, tal cual («Servicio de cupones (muestra/portal#41)»), sin «nada» ni «pendiente de revisar».
4. **P34.** «Sin aviso» quiere decir que ningún aviso nombra «Pieza».
5. **P35.** «Pide conectar con escritura» es lo que P23 ya pide: un paso que nombra el repositorio y dice «con escritura» y «antes de trabajar». «No conecta ninguno» es que, para quien no construye, la apertura no diga «escritura» en ninguna forma: ni «con escritura», ni «acceso de escritura», ni para decir que no («no conectes ningún repositorio con escritura» también falla). Es la lectura que aceptó quien acepta: así una apertura no puede colar la escritura con otras palabras. Lo de solo leer, que un paso diga «solo para leer». Por lo mismo, cuando el nombre de «Construye» no está en «Quién es quién», la apertura dice por qué sin la palabra: nombrando a la persona y «Quién es quién».
6. **P35.** Dos personas en «Construye» van separadas por « · », como los repositorios en «Repositorios:». Un nombre sin cuenta va solo («Construye: Luis Gómez»).
7. **P35.** «Dice por qué» es que la apertura nombre a la persona de «Construye» que no encuentra y «Quién es quién».
8. **P36.** El lector puede dejar o quitar « (esencial)» del título: la prueba compara los títulos sin él. Las listas de escenarios a verificar se comparan sin orden. La fase se pasa por su identificador («F2») y el plan es el que da `read_plan`.
9. **P36.** «F1 entregada» es F1 con el estado `cerrada` en «Fases».

### Lo que queda sabido

- **P34 y la tabla «Infraestructura».** Lo decidió quien acepta (shared-memory/plugin-memoria#2026-11-27-13): su primera columna pasa a llamarse «Recurso» (el nombre de la caja), y «Pieza», en las tres tablas, es la pieza del plan. Un diseño de antes, sin «Recurso» (la muestra de P05 y las de P21), se sigue leyendo como hoy: su «Pieza» es el nombre de la caja. La muestra de P34 con la columna lleva «Recurso»; la fila añadida de «Without the column» comprueba el diseño de antes. Cambiar la plantilla del diseño es de la pieza, no de estas pruebas.
- **P34, la forma del punto 4.** La fija la decisión shared-memory/plugin-memoria#2026-11-27-14 (ver punto 3 de arriba): `seguimiento.py` escribe el rótulo y «- pendiente de revisar», y el subagente seguimiento lo llena. P06 comprueba que el script lo deja así; P34, que el tablero lee esas líneas.
- **P35.** Las filas positivas («recibe escritura») pasan hoy, porque hoy todos la reciben; «Whoever builds» y «found by name» fallan solo por su parte añadida, la cuenta que no construye. **«Several builders» pasa hoy**: se le quitó la cuenta que no construye (Pablo) porque repetía lo que ya comprueban las otras filas; lo que comprueba, que las dos que construyen reciban escritura, lo cumple hoy el código.
- **P36.** El cuarto escenario no tiene prueba: lo dice el propio escenario.
- Ninguna de las tres necesita pytest ni node.

## Fase F3 · El seguimiento y la auditoría por script (P06 y P07)

Escenarios aprobados por Juanjo Jiménez-Alfaro el 2026-11-27, en el plan: los seis de P06 y los cuatro de P07.

**Cómo están planteadas.** Las piezas son tres scripts de `plugins/memoria/skills/desarrollo/`, con el contrato del encargo: `recoger_github.py` lee GitHub y escribe un JSON; `seguimiento.py` lo junta con la sección, el plan y el diseño e imprime la entrada (y con `--guardar` la escribe); `auditoria.py` propone los estados de la configuración (y con `--escribir` los escribe). Cada prueba:

- monta en una carpeta temporal la raíz de muestra de P05 (el portal de pedidos, con P01 a P03 en el plan), con «Zona horaria: UTC» en su `guia.md`, y, para P07, un `configuracion.md` con la tabla de la plantilla y estados ya puestos;
- pone delante en el PATH un **`gh` falso** que responde la API REST de GitHub desde datos que escribe cada escenario (pull requests con sus archivos y su descripción, releases, qué commits contiene cada etiqueta, la regla de la rama principal, la organización). Nunca toca la red: además, cualquier conexión directa va a un proxy que no existe;
- corre `recoger_github.py` y, con su JSON, el otro script, y mira lo que imprime, con qué código sale y cómo queda el archivo.

Hoy fallan las diez filas, y deben: los tres scripts no existen («no está recoger_github.py en …»).

### P06 · El seguimiento por script

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| Block pull requests and reverts give each piece its state | Unidos «P01 + P02 · Catálogo y precios», «P03 · Pedido en línea» y después «Revert "P03 · Pedido en línea"»; se guarda | Sale con 0 y guarda. La entrada más reciente, leída con el mismo lector que usa el tablero, es la de hoy y dice P01 y P02 `unida` y P03 `revertida`. El JSON dice que lo leyó todo (`completo` con `prs` y `releases` verdaderos; puede traer más claves) y trae la regla de la rama principal en `"reglas"`, aunque no se pidió la auditoría. **Añadido** (cubre la decisión #2026-11-27-14): la entrada trae el punto 4 con su rótulo «4. Lo que lo unido añade y el diseño no tiene:» y debajo solo «- pendiente de revisar»: el script no lo da por juzgado. **Añadido:** las entradas anteriores siguen tal cual, debajo. **Añadido:** con los mismos datos y la regla en 403, `--guardar` sale con 0 y guarda la entrada de hoy; el JSON trae `"reglas": null`, y la entrada dice «sin comprobar» en su punto 5 (en la línea que nombra el check «pruebas de aceptación», o bajo su rótulo) | P06 |
| An incomplete list is never saved as whole | GitHub devuelve páginas llenas de pull requests sin fin (cerrados sin unir, todos posteriores a la fecha); se pide guardar | Sale con 3; en la tabla, P01, P02 y P03 dicen «sin comprobar», y «sin comprobar» sale también fuera de la tabla; el seguimiento no cambia; el JSON dice que la lista de pull requests no está completa | P06 |
| Delivered only if the release contains the commit | Release v1.0.0 del 25, con «Aprobó:», que contiene el commit de «P02 · Precios» (unido el 18) y no el de «P01 · Lista de productos» (unido el 22) | P01 `unida`. **Añadido:** P02 `entregada`, para que no baste con no entregar nunca; el JSON trae en «contiene» el commit de P02 y no el de P01 | P06 |
| Where merging publishes, the version pull request's yes delivers | «Paso a Prod: unir el pull request de versión es el paso a Prod»; unido «P01 + P02 · 1.2.0» con «Aprobó: Ana Pérez, 2026-11-20» en su descripción | P01 y P02 `entregada`, y una línea de la entrada dice Ana Pérez y 2026-11-20 | P06 |
| What is outside the plan is listed | Unidos #41 «Arregla la portada», #42 «P09 · Exportar pedidos», #43 «Kit · Ajusta el control» que cambia un workflow y `src/api.py`, y #44 «Bump actions/checkout from 4 to 5», de dependabot, que solo cambia un workflow. **Añadido:** #40 «Ajusta el pie de página», sin pieza, unido el 10, antes de `--desde` | #41, #42 y #43 salen bajo «fuera del plan»; #44 no sale bajo «fuera del plan», y lo que se dice de él lo cuenta como kit. **Añadido:** #40 no sale bajo «fuera del plan» | P06 |
| No access to a repository is said, and nothing is saved | GitHub responde 404 a todo lo del repositorio; se pide guardar | Sale con 3; la tabla tiene P01, P02 y P03 sin ninguno de los cinco estados; la entrada nombra `muestra/portal` en una línea que dice que no se pudo leer o da su motivo; el seguimiento no cambia; el JSON dice acceso falso con su motivo | P06 |

### P07 · La auditoría mensual

| Título que imprime | Situación | Tiene que pasar | La pone en verde |
|---|---|---|---|
| A failing rule is proposed with its evidence | La regla de la rama principal exige «pruebas» y «secretos», no «pruebas de aceptación»; sin `--escribir` | R2 sale «no cumple» y lo que dice de R2 nombra «pruebas de aceptación»; `configuracion.md` no cambia | P06 + P07 |
| No access is said, not guessed | GitHub responde 403 a la regla y a los rulesets (y a la protección clásica) | R1 y R2 salen «sin comprobar», y lo que dice de cada una da el motivo; `configuracion.md` no cambia | P06 + P07 |
| A merged pull request without a piece fails R6 | Desde la última auditoría (28 de octubre), unido #51 «Arregla la portada», de una persona. **Añadido:** también #52 de pieza, #53 «Escenarios · », #54 «Kit · », #55 una reversión y #56 un «Bump …» de dependabot, y #50 «Ajusta el pie de página», sin pieza, unido el 20 de octubre, antes de la última auditoría | R6 sale «no cumple» con «#51». **Añadido:** ninguno de #50 y #52 a #56 sale como evidencia de R6 | P06 + P07 |
| With the yes, one change; what the API cannot see stays | La regla bien puesta salvo el check de aceptación; antes, R1 «no cumple» y R2 «cumple»; con `--escribir` | R1 queda «cumple · hoy» y R2 «no cumple · hoy»; PL3 a PL7, R4, R5 y R7 quedan como estaban y la salida nombra cada una por su identificador suelto; fuera de las filas que propone la auditoría (R1, R2, R3, R6, PL1, PL2) y de «actualizado:», el archivo no cambia | P06 + P07 |

Las filas de P07 las ponen en verde P06 + P07: la auditoría corre sobre el JSON de `recoger_github.py`, que es de P06.

### Cómo se leyó lo que el escenario no precisa

1. **El `gh` falso fija parte del contrato, y lo mantiene quien acepta.** Admite solo `gh auth status` y `gh api <ruta REST>` de lectura (`GET`, con `-X GET`, `-f`, `-F`, `-H`, `--hostname` y `--cache`); no admite `--jq`, `--paginate` ni GraphQL (`gh api graphql`, ni `gh pr list` o `gh repo view`, que van por GraphQL): el script lee el JSON tal cual y pide cada página con `page=`. Una ruta que no conoce da 404, como GitHub, y un método que no es `GET`, 403. La regla de la rama principal se sirve **solo por rulesets** (`rules/branches/<rama>`, `rulesets` y `rulesets/<id>`), igual con y sin `--auditoria`; la protección clásica, `branches/<rama>/protection`, da 404 «Branch not protected», como en un repositorio que solo usa rulesets; sin acceso, 403 a las tres. Cada respuesta trae los campos que da GitHub: la lista de `pulls` trae `merged_at` y `merge_commit_sha` pero no `merged` ni `merged_by`, que van solo en el GET de un pull request (`pulls/<n>`); la búsqueda (`search/issues`) da issues, sin `merged_at`, `merge_commit_sha` ni `base` sueltos, con `merged_at` dentro de `pull_request`, y filtra por los calificadores `merged:`, `updated:`, `created:`, `closed:` (con `>=`, `>`, `<=`, `<` o `A..B`), `is:`, `state:` y `base:`. `compare/` admite los dos órdenes: `<etiqueta>...<sha>` da `behind` (o `identical`) si la etiqueta contiene el commit, y `<sha>...<etiqueta>`, `ahead` (o `identical`); si no, `diverged`. Si quien construye necesita otra ruta o una de esas opciones, se cambia la prueba en un pull request de escenarios.
2. **«Cortada en el límite»**: GitHub no se acaba nunca (cada página llena y posterior a la fecha). Así vale cualquier límite de páginas que ponga el script, pero un script sin límite no termina: pasa de dos minutos y la fila falla.
3. **«Cada parte que lo necesita»**: con la lista cortada, ninguna pieza tiene estado seguro, así que las tres filas de la tabla dicen «sin comprobar», y al menos una línea fuera de la tabla también (lo fuera del plan sale de la misma lista).
4. **El estado se lee de la tabla `| Pieza | Estado |`** que imprime el script, sin mayúsculas ni acentos graves; la primera fila sí se lee de la entrada guardada, con el lector del tablero. «Sin estado» es cualquier cosa que no sea uno de los cinco estados.
5. **«Listado como fuera del plan»**: el número va como `#41`, y la frase «fuera del plan» está en su línea o en el rótulo de la lista donde sale. El rótulo de una línea es la más cercana por encima que no está en blanco ni es una viñeta o una fila de tabla; un punto numerado puede ser rótulo de lo que va debajo («3. Fuera del plan:» y debajo «- #41 …»), salvo de otro punto numerado. **#44 no puede salir bajo «fuera del plan»**: ni en una línea que lo diga antes de #44 o junto a él, ni en un elemento de lista (una viñeta o un punto numerado) cuyo rótulo lo diga; una línea suelta, como «Cuentan como kit: #44 …», es rótulo de sí misma. «Cuenta como kit»: la palabra «kit» está en lo que se dice de #44, que es su trozo de línea (desde #44 hasta la referencia `#N` siguiente o el final, con lo que va delante si #44 es la primera referencia de la línea, como en «Kit: #44 …») y, si su línea es un elemento que solo nombra a #44, su rótulo; no basta con que «kit» salga en otro sitio de la línea («#43 Kit · Ajusta el control · #44 Bump» no cuenta). Una línea «3. Fuera del plan: #41 · #42 · #43. Kit: #44» falla: #44 va en la línea de «fuera del plan».
6. **Lo que la auditoría dice de una fila** es desde la primera línea que nombra solo esa fila (una cabecera que nombra varias, como «Propuesta para R1, R2, R3, R6, PL1 y PL2:», no lo abre) hasta la siguiente que nombra otra y no esa; si ninguna línea la nombra sola, desde la primera que la nombra («R1 y R2: sin comprobar …»). Cada fila se nombra por su identificador suelto: «R2», «PL3»; «PL3 a PL7» o «R4-R5» no nombran PL4 ni R4. «El motivo» es que diga 403, acceso o permiso. **El código de salida de `auditoria.py`**: 0; con alguna fila «sin comprobar», 0 o 3, como `seguimiento.py` (el contrato no lo fija; es la lectura aceptada).
7. **«Desde la última auditoría»** se le pasa a `recoger_github.py` como `--desde 2026-10-28`, la fecha de la configuración de la muestra. **El sí** es `--escribir`.
8. **«En una sola escritura»**: la prueba ve que una sola llamada con `--escribir` deja los dos estados con la fecha de hoy y nada más cambiado; si el script escribe el archivo una vez o varias dentro de esa llamada, no lo distingue.
9. **La entrada anterior de la muestra se movió del 20 al 16 de noviembre**, para que «2026-11-20» solo salga en el «Aprobó:» de la cuarta fila de P06.
10. **La regla de la rama principal, siempre** (ajuste del contrato que decidió la sesión que construye): `recoger_github.py` la lee también sin `--auditoria` y la deja en `"reglas"` (una lista, como la da `rules/branches/<rama>`, o `null` con su motivo). Si no se puede leer, el punto 5 de la entrada dice «sin comprobar», pero eso no hace salir a `seguimiento.py` con 3 ni impide guardar: solo lo impiden una lista incompleta o un repositorio sin acceso. La prueba no fija dónde va el motivo de `"reglas": null` en el JSON (el contrato no le da clave), solo que la entrada diga «sin comprobar» en su punto 5.
11. **«Su punto 5»**: la entrada no tiene forma fija más allá de la tabla y del punto 4, así que vale una línea de la entrada de hoy con «sin comprobar» que nombra el check «pruebas de aceptación», o que está bajo un rótulo que lo nombra (un punto numerado vale como rótulo, como en el 5).
12. **«Hoy» es la fecha en la zona de la organización.** Los scripts fechan con la «Zona horaria:» de `guia.md` (Ciudad de México si no la hay); la raíz de muestra declara «Zona horaria: UTC» y la prueba compara con la fecha UTC, así que la fecha coincide en CI y en cualquier computadora, a cualquier hora.
13. **El punto 4 lo escribe el script sin juzgarlo** (decisión shared-memory/plugin-memoria#2026-11-27-14): `seguimiento.py` pone «4. Lo que lo unido añade y el diseño no tiene:» y debajo «- pendiente de revisar»; el subagente seguimiento lo llena después con «- <nombre> (<repositorio>#<número>)» o «- nada». La primera fila de P06 comprueba la forma que deja el script; P34, la que lee el tablero.
14. **«Desde la fecha»**: un pull request unido antes de `--desde` no se lee: no sale bajo «fuera del plan» (P06) ni como evidencia de R6 (P07).

### Lo que queda para la verificación en pantalla

Nada de P06 ni de P07: el tablero ya lee la tabla de la entrada. Lo ve la verificación, porque la prueba no lo distingue: que la entrada traiga los siete puntos de la plantilla en su orden, y que la evidencia y lo que se lista para quien administra se lean bien en llano.

### Lo que queda sabido

- P06 y P07 solo necesitan Python 3. P07 importa de P06 la raíz, el `gh` falso y cómo se corren los scripts; P06 importa la raíz de P05.
- Lo que se apunta como `recoger_github.py` salió sin JSON incluye las últimas llamadas que hizo a `gh`, para ver qué ruta pidió.
