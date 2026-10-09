# Varias raíces y traspasos

Anexo del contrato (`convenciones`, sección 1). Se lee cuando hay más de una raíz conectada, cuando alguien pide pasar algo de una raíz a otra y al migrar.

## Independencia entre raíces

Una sesión puede tener conectada más de una raíz a la vez, o una raíz y el repo del plugin. Se trabaja en una a la vez: si hay más de una carpeta con `guia.md` y `metodo.md`, antes de leer o escribir nada se pregunta en cuál, cada escritura dice en qué raíz se hace y cambiar de raíz se anuncia. Cada raíz sigue siendo de una sola organización: nada que se escriba en una raíz usa hechos, cifras, nombres o decisiones de otra raíz, ni del repo del plugin, salvo por un traspaso; y nada que se escriba en el repo del plugin usa hechos de una organización en particular, porque el plugin es idéntico para todas. Comparar la forma de dos raíces (¿tienen las mismas piezas?, ¿la misma cabecera?) no es tocar su contenido, y ese trabajo no se guarda dentro de ninguna de las dos. Lo que una organización guarda sobre otra, por ejemplo quien mantiene el método guardando el historial de una migración que hizo para un cliente, se limita a lo operativo de quien lo guarda: qué se entregó y cuándo, nunca el contenido del trabajo del cliente.

## Traspaso entre raíces

 A veces algo de una raíz tiene que llegar a otra: lo que se decidió sobre un cliente en la raíz de su proveedor y el cliente necesita en la suya, o al revés. Solo ocurre si lo pide la persona que trabaja, pieza a pieza, hacia una raíz donde puede escribir. Antes de escribir se le enseña el texto exacto que pasaría, a qué archivo de la otra raíz iría y qué se queda fuera y por qué (datos personales, contratos, credenciales, cifras internas, lo de otros clientes); se escribe solo cuando lo confirma. En el destino entra reescrito para su contexto y por la puerta que le toque: una decisión se registra como decisión de quien la asume ahí, y un documento entra por `fuentes/` o como entregable de quien lo hace suyo. La sesión del proyecto de destino anota qué vino, de qué raíz, quién lo pidió y cuándo. El origen no se toca. Credenciales, y datos de una organización hacia la raíz de otra que no tiene que ver con ellos, no pasan nunca, aunque se pida: se dice por qué. Lo demás lo decide quien pide el traspaso, que tiene la última palabra.

## Dónde vive el registro de una migración

Eso fija dónde vive cada cosa cuando una organización adopta el método. **El registro de la migración es de quien migra**: las auditorías, los planes y los manifiestos van a su raíz, en un proyecto por organización nombrado por la organización y no por el trabajo. Cuentan lo que hizo el proveedor y hablan del sistema del que se migró, que la organización que estrena el método no usó nunca y no le dice nada.

En la raíz de la organización entra solo lo que su equipo necesita para operar, y entra donde se usa, no en un proyecto aparte: las decisiones recuperadas de su material anterior, cada una en el `decisiones.md` del proyecto al que pertenecen y marcadas como pendientes de confirmar; y el material confidencial que quedó fuera de alcance, con su fila en el `fuentes/enlaces.md` que corresponda. Nada más: su raíz no guarda rastro del sistema del que se migró, ni en las rutas, ni en el vocabulario, ni en los nombres de sus archivos.
