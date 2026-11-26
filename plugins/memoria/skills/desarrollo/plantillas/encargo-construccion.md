# Encargo de construcción

Lo escribe la sesión principal, la que planea, cuando los escenarios de una fase están aprobados y la persona acepta construirla en sesiones aparte: un encargo por sesión. Va como nota del proyecto (`taller/encargo-construccion-<fase>-<parte>.md`, o `-<fase>.md` si es una sola), en borrador. La sesión principal se queda con el plan, las decisiones y el sí; la que construye no cambia ninguno de los tres. Ningún campo se deja vacío: lo que no aplica dice «no aplica» y por qué.

# Encargo de construcción · [fase] · [parte]

Para una sesión nueva en **[modelo que construye]** con [la carpeta conectada]. [Si puede ir a la vez que otra: con cuál, y que tocan archivos distintos.] Decisión: [identificador de la decisión que planeó la fase].

## Qué leer primero
- [Del plan: el bloque «en llano» de la fase y los escenarios de sus piezas, con su «Aprobó:». Nada más del plan si no hace falta.]
- El `CLAUDE.md` del repositorio ([organización/repositorio], conectado con escritura al abrir).
- [Notas del taller que la fase cierra, y solo la parte que toca.]

## Orden
1. **Escenarios.** [Las piezas con escenarios: lanzar el subagente `escenarios` con el encargo de campos fijos (`plantillas/encargo-escenarios.md`) y abrir «Escenarios · P..» a la rama principal; quien acepta lo une.] [O: «no aplica», si son piezas técnicas.]
2. **Rama `[rama]`** desde [la rama principal o la de versión].
3. **[Pieza]**: [lo que hace, en una o dos frases]. [Una pieza por paso, en el orden en que se construyen; la que rehace lo que otra mueve, después.]
4. [Juntar ramas: qué sesión une la rama de cuál, y antes de qué.]
5. [Revisión de calidad, pull request de versión con «Construyó: [modelo]», verificación sobre la candidata por [modelo que verifica]; o, si lo hace otra sesión: «subir la rama y avisar a [persona]».]

## Archivos de esta sesión
[Los archivos y carpetas que esta sesión toca, y los que no toca porque son de otra. Dos sesiones a la vez nunca comparten un archivo.]

## Modelos
Construye: [modelo]. Verifica: [el que no construyó, con su subagente].

## Dónde parar y preguntar a [quien acepta]
- [Lo que se sale del diseño o del plan, o necesita escribir en la computadora de la persona.]
- [Un enfoque que falla dos veces: proponer pasar la pieza al otro modelo.]
- [Un tope de tamaño o de llamadas, si lo hay.]

## Horas
[Horas de sesión con IA por pieza y en total, más escenarios, revisión y verificación.] Espera a [persona]: [lo que espera a una persona, aparte: unir, mirar la candidata, el sí].

## Para arrancar
[La frase que se pega en la sesión nueva, por ejemplo: «Retomamos [proyecto]. Construye [fase] siguiendo taller/encargo-construccion-[fase]-[parte].md».]
