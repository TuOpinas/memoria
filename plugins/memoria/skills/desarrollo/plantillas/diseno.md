---
estado: borrador
actualizado: AAAA-MM-DD
aportacion: "[Lo que este documento aporta, en una frase]"
basado_en: []
---

# Diseño

Lo redacta Claude al empezar; lo validan quien acepta (lo funcional) y quien audita (lo técnico). Las tablas las lee el tablero para dibujar la pestaña Desarrollo: se pueden añadir columnas, pero estas se quedan con su nombre. Varios valores en una celda van separados por « · ». La columna «En corto», en «Componentes», «Datos» e «Infraestructura», es opcional: lo que dice, en unas palabras, sale bajo el nombre de su caja; sin ella, cada caja lleva solo su nombre.

**La regla:** lo que no esté aquí (una entidad, un componente o un concepto) entra solo con una decisión, y esa sesión pone al día este documento. El seguimiento compara lo unido con lo que dice este documento.

## Objetivo
[Qué resuelve el producto y para quién, en dos líneas.]

## Cómo funciona
1. [Lo primero que pasa, en una frase de quien lo usa]
2. [Lo siguiente]

## Reglas
Las reglas de negocio que el producto tiene que cumplir.

| Regla | Excepción |
|---|---|
| [Una frase] | [Cuándo no aplica] |

## Componentes
| Componente | En corto | Qué hace | Dónde vive | Externo | Conecta con | Corre en |
|---|---|---|---|---|---|---|
| [Cliente o servicio de fuera] | [Qué es, en unas palabras] | [Una frase] | [quién lo da] | sí | [componente al que llama] | [pieza de «Infraestructura»] |
| [Nombre] | [Qué es, en unas palabras] | [Una frase] | [organización/repositorio:ruta] | | [otro componente · otro más] | [pieza de «Infraestructura»] |

**Flujo:** [componente → otro → otro: el recorrido de la llamada principal, desde quien la hace. Solo vale sin «Tipo» en «Infraestructura»: con ella, cada componente se dibuja dentro de la pieza de su «Corre en»]

## Datos
Una fila por entidad, con su nombre en el código, y cada relación escrita una sola vez, en la fila de la entidad que apunta a la otra. Entre paréntesis va la cardinalidad (1:N, N:M) o, mejor, el verbo que dice qué hace la relación (vive en, deja, firma).

| Entidad | En corto | Grupo | Qué es | Se relaciona con |
|---|---|---|---|---|
| [nombre_en_codigo] | [Qué es, en unas palabras] | [Un grupo de entidades] | [Una frase] | [otra_entidad (vive en) · otra (N:M)] |

Cada grupo de la columna «Grupo», una fila, en el orden en que se apilan en el dibujo. Papel: `centro` en el grupo con el que trabaja la gente (borde grueso), `aparte` en el que no se une a los demás (sin líneas), o vacío.

| Grupo | En corto | Papel | Se relaciona con |
|---|---|---|---|
| [Un grupo de entidades] | [Qué es, en unas palabras] | [centro, aparte o vacío] | [otro grupo (actualiza)] |

**Flujo:** [entidad → otra → otra: por las que pasa un cambio, en orden; la que reciben dos o más de ellas es la base que comparten: va en una banda debajo, sin líneas, y sus relaciones se dicen en la ventana de cada entidad; las demás, encima]

Detalle: [ruta desde la raíz de un documento con una tabla cuya primera columna es la entidad; sin él, se quita esta línea]

## Conceptos
Las palabras del producto. Un sinónimo no es un concepto nuevo: va en «No es».

| Concepto | Significa | No es | Entidades |
|---|---|---|---|
| [Palabra] | [Una frase] | [otra palabra, otra más] | [entidad · otra] |

## Infraestructura
Cada proveedor y cuenta se dibuja como un contenedor con sus piezas dentro. Un servicio del cliente (su Drive, su correo) lleva su propia cuenta.

| Pieza | En corto | Tipo | Para qué | Proveedor | Cuenta | Ambiente | Conecta con |
|---|---|---|---|---|---|---|---|
| [Servidor, base de datos, dominio, servicio externo] | [Qué es, en unas palabras] | [corre, guarda o externo] | [Una frase] | [Google Cloud, Cloudflare…] | [proyecto o cuenta] | [Prod, Release] | [otra pieza (lee)] |

## Prototipo
[Enlace y fecha.]
