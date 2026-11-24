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

- `correr.py` corre las pruebas de las piezas que se le piden. Su última línea, «N pasan · M fallan · K saltadas», cuenta archivos de prueba, no filas de este resumen. Una prueba que no arranca cuenta como error, no como fallo.
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
