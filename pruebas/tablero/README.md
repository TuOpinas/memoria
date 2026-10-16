# Pruebas del tablero

`probar.sh` comprueba el tablero contra `raiz/`, una organización inventada que reúne los casos difíciles: un área restringida, un proyecto declarado restringido y otro que solo menciona algo restringido, una carpeta `restringido/`, fechas que son plazo y fechas que no, una revisión trimestral, un entregable con la base más nueva que él, un borrador viejo, una decisión pendiente de confirmar, otra que afecta a otro proyecto, y un área archivada, con todos sus proyectos cerrados.

Primero genera los datos en modo público y completo y comprueba que no se filtra nada y que los plazos, los entregables y las decisiones se leen bien. Después, si hay Node con Playwright, recorre la página en claro, oscuro y móvil, abre cada ventana y falla si la página da algún error; las capturas quedan en la carpeta de salida.

Se pasa antes de publicar cualquier cambio al tablero. No forma parte de lo que se instala: el plugin es `plugins/memoria/`.
