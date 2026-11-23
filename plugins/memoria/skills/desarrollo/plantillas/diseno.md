---
estado: borrador
actualizado: AAAA-MM-DD
aportacion: "[Lo que este documento aporta, en una frase]"
basado_en: []
---

# Diseño

Lo redacta Claude al empezar; lo validan quien acepta (lo funcional) y quien audita (lo técnico). Las tablas las lee el tablero para dibujar la pestaña Desarrollo: se pueden añadir columnas, pero estas se quedan con su nombre. Varios valores en una celda van separados por « · ».

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
| Componente | Qué hace | Dónde vive | Conecta con |
|---|---|---|---|
| [Nombre] | [Una frase] | [organización/repositorio:ruta] | [otro componente · otro más] |

## Datos
Una fila por entidad, con su nombre en el código, y cada relación escrita una sola vez.

| Entidad | Grupo | Qué es | Se relaciona con |
|---|---|---|---|
| [nombre_en_codigo] | [Un grupo de entidades] | [Una frase] | [otra_entidad (1:N) · otra (N:M)] |

Detalle: [ruta desde la raíz de un documento con una tabla cuya primera columna es la entidad; sin él, se quita esta línea]

## Conceptos
Las palabras del producto. Un sinónimo no es un concepto nuevo: va en «No es».

| Concepto | Significa | No es | Entidades |
|---|---|---|---|
| [Palabra] | [Una frase] | [otra palabra, otra más] | [entidad · otra] |

## Infraestructura
| Pieza | Para qué | Dónde | Conecta con |
|---|---|---|---|
| [Servidor, base de datos, dominio, servicio externo] | [Una frase] | [Proveedor, entorno] | [otra pieza] |

## Prototipo
[Enlace y fecha.]
