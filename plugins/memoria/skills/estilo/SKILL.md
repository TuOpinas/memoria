---
name: estilo
description: Normas de estilo y de lectura rapida. Aplicala por defecto al redactar o revisar cualquier texto que se vaya a firmar o compartir, y tambien a las respuestas en el chat, sin que la invoquen; y de forma explicita cuando pidan 'que suene menos a IA', 'mas ejecutivo', 'mas al grano', 'mas compacto', 'que se lea rapido' o 'revisa el estilo'.
---

# Estilo

Estilo de todo lo que se escribe, firma o comparte en esta estructura:

> **Ejecutivo y al grano: el hecho relevante desde el inicio, sin rodeos ni expresiones que no aporten de manera directa.**

Se escribe para alguien con poco tiempo y muchas interrupciones. Tiene que poder leer en diagonal, quedarse con lo que decide y no perderse nada esencial por haberlo hecho así.

Este archivo es la fuente canónica del estilo. Si una plantilla del plugin lo contradice, manda este archivo.

## Cuándo se aplica

Siempre, sin que nadie la invoque, en cualquier redacción o revisión. Y de forma explícita cuando alguien pide que suene menos a IA, más ejecutivo, más al grano, más compacto, que se lea rápido, o que le quiten los rodeos.

**No se cambia por iniciativa propia.** Este es el estilo de la casa y se aplica por defecto, aunque el texto parezca pedir otro registro. Solo cambia si quien encarga el texto lo pide de forma expresa, y el cambio vale para ese texto: no se guarda como estándar nuevo ni se arrastra al siguiente entregable.

## Las dos preguntas que resuelven casi todo

1. **¿La primera frase ya dice el hecho, o lo anuncia?** Si lo anuncia, empieza por el hecho.
2. **¿Puedo borrar esta palabra y no se pierde información?** Entonces sobra.

## Lectura rápida

Los siete patrones de abajo arreglan la frase. Estas ocho reglas arreglan el documento, que es donde se pierde al lector que tiene prisa.

1. **La primera pantalla basta.** Quien solo lee eso sale sabiendo el estado y qué se decide. Nada esencial vive por debajo del primer pliegue.
2. **Los títulos dicen el hecho, no el tema.** *"El motor cuesta 2.44 M al año"*, no *"Costos del motor"*.
3. **Una idea por fila.** Si el contenido se puede enumerar, va en lista o tabla. La prosa se reserva para lo que necesita argumento.
4. **Si cabe en una fila de tabla, no va en un párrafo.**
5. **Cada afirmación trae su dato.** Un párrafo que no aporta un dato ni cambia una decisión se borra.
6. **La consecuencia va pegada a la acción.** El "si esto no ocurre, pasa aquello" debajo de su acción, no en una lista de riesgos al final que el lector ya no relaciona.
7. **Lo hecho antes de lo pendiente**, cuando el lector decide sobre el trabajo de otros.
8. **Sin preámbulo de sección.** Título y contenido. Las frases que presentan lo que viene se borran.

## Siete patrones a evitar

**1. Metadiscurso, frases que anuncian en vez de decir.** El patrón que más suena a IA: construye expectativa antes de entregar contenido.

- Mal: *"El punto central es que el motor propio sale más barato."* · *"Y el hallazgo que reordena la pregunta: no existe API fiscal mexicana."* · *"Lo que conviene tener claro:"* · *"para una lectura equilibrada"*
- Bien: *"El motor propio sale 5× más barato."* · *"No existe API fiscal mexicana en el mercado."*

**2. Guiones largos como muletilla.** Cuando el guion sustituye a dos puntos, coma o punto y coma, usa la puntuación normal. Resérvalos para incisos que funcionan como paréntesis.

- Mal: *"La decisión es clara — modernizar el motor."*
- Bien: *"La decisión es clara: modernizar el motor."*
- Bien, inciso legítimo: *"El motor —heredado de 2007— sigue en producción."*

El umbral: más de un guion largo cada 500 palabras en un entregable es muletilla, aunque cada uno por separado parezca defendible. Un entregable de 1.500 palabras con siete guiones largos tiene que bajar a tres como mucho.

- Mal: un brief de 600 palabras con cinco guiones largos, todos correctos como incisos. Son demasiados para lo que dice el texto.
- Bien: el mismo brief con uno, y los otros cuatro convertidos en dos puntos, paréntesis o frases separadas.

**3. Negaciones en espejo.** *"No es X, es Y."* Legítimas solo cuando corrigen una expectativa falsa que el lector traía. Si no la traía, di Y directamente.

- Mal: *"No es un problema de producto, es un problema de go-to-market."* (si nadie dijo que fuera de producto)
- Bien: *"El problema es de go-to-market."*

**4. Rodeos en las conclusiones.** La conclusión es lo que menos tolera preámbulo.

- Mal: *"La postura de fondo es modernizar."* → Bien: *"Modernizar."*

**5. Negritas como subrayado nervioso.** Una negrita destaca; cinco no destacan ninguna. En documentos internos ayudan a escanear; en un documento para terceros, tres por párrafo cansan.

**6. Signos que no se leen en voz alta en español.** Si no puedes leer el signo en voz alta, escribe la palabra. El caso cerrado es el signo de sección, que no aparece en ningún documento.

- Mal: el signo de sección pegado a un número o a un nombre, como abreviatura de "sección"
- Bien: *"ver la sección 4.1"* · *"secciones 2 y 3"* · *"de la sección 8"* · *"sección Nómina"*
- Se conservan `%`, `·`, `→`, el `#` de un ticket, y cualquier signo que sea parte de un identificador citado literalmente.

**7. Cifras sueltas.** Toda cifra en un entregable lleva fecha o fuente en el mismo párrafo. Una cifra sin ninguna de las dos no se puede comprobar ni saber si sigue valiendo, y el lector de dentro de seis meses no tiene a quién preguntar.

- Mal: *"El 70% del volumen son órdenes pequeñas."*
- Bien: *"El 70% del volumen son órdenes pequeñas (export de órdenes de 2025, `fuentes/ordenes-2025.csv`)."* · *"A agosto de 2026, el 70% del volumen son órdenes pequeñas."*

La fecha basta cuando el dato es de la propia organización y está en una fuente ya citada en la cabecera. La fuente hace falta cuando el dato viene de fuera.

## Alcance

- **Entregables y cualquier texto que salga del proyecto:** los siete patrones y las ocho reglas de lectura rápida, sin excepción.
- **Registros** (`sesiones.md`, `decisiones.md`): pueden ser más extensos, porque su función es dejar constancia del razonamiento. El metadiscurso y los rodeos sobran igual, y una cifra en `Por qué` también lleva su fecha o su fuente.
- **Respuestas de la IA en el chat:** la respuesta primero y el detalle después, sin recapitular lo que el usuario acaba de decir y sin narrar lo que se va a hacer. El único límite es no perder información que el usuario necesita para decidir: entre una respuesta corta y una completa gana la completa, pero sin relleno.

## Al revisar un texto existente

1. Señala los pasajes concretos y propón la reescritura. No reescribas el documento entero en silencio.
2. Lee solo la primera pantalla y pregúntate si con eso basta para saber el estado y qué se decide. Si no basta, el problema es de orden y se arregla antes que las frases.
3. Cuenta los guiones largos antes y después, y compáralos con el umbral de uno cada 500 palabras. Es la medida más rápida de si el texto mejoró.
4. Busca cada cifra y comprueba que tenga fecha o fuente al lado.
5. No toques las citas textuales de terceros ni los nombres propios de documentos y decisiones.
6. Corregir el estilo de un entregable de otro proyecto o de otra área es tocar contenido ajeno, no forma. Se propone al dueño, no se aplica.
