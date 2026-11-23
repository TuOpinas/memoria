# Encargo de escenarios

Lo rellena la sesión que construye antes de lanzar al subagente `escenarios`, y no lo lanza con un campo vacío: lo que no aplica dice «no aplica» y por qué. Va como nota del proyecto (`taller/encargo-escenarios-<fase o pieza>.md`).

## 1. Piezas y escenarios
[Las piezas, y dónde están sus escenarios aprobados con su «Aprobó:». No se les cambia una palabra. Una prueba por escenario, también los de error.]

## 2. Qué se puede leer
[El `CLAUDE.md` del repositorio, su carpeta de pruebas de aceptación y lo que nombre el campo 5. Del código, nada más: ni lo que las pruebas van a llamar ni otras pruebas.]

## 3. Cómo llama una prueba a cada pieza, y qué comprueba
[El punto de entrada (un comando, una función, una ruta), lo que devuelve y cómo cae cada escenario sobre eso. Si la pieza aún no tiene punto de entrada, se decide aquí: es lo primero que se construye.]

## 4. Qué solo se ve en pantalla
[Lo que las pruebas no ven (que se dibuje, que un clic abra) y queda para la verificación. El resumen de las pruebas lo dice en llano.]

## 5. Materiales para los ejemplos
[Las plantillas o los datos de muestra que hacen falta y dónde están; la forma de lo que aún no tiene plantilla.]

## 6. Dónde van los archivos y lo compartido
[Como dice «Pruebas de aceptación» del `CLAUDE.md`: el nombre de los archivos, cómo los corre el ejecutor y dónde va lo que comparten. Antes de lanzar se comprueba qué archivos admite el workflow de aceptación en esa carpeta: lo que no admite no se pide.]

## 7. Dónde se deja el trabajo
[Una rama local, con un commit, sin subirla ni abrir el pull request: lo abre la sesión que lanzó, después de la revisión y de avisar a quien acepta. La lista de piezas activas no se toca.]

## 8. Qué devuelve
[La lista escenario → prueba; la salida del ejecutor, donde cada prueba falla porque la pieza no existe y no por la muestra ni por un import; y lo que el contrato del campo 3 deja sin poder probar, sin cambiar el escenario.]
