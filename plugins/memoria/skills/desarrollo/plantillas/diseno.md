---
estado: borrador
actualizado: AAAA-MM-DD
aportacion: "[Lo que este documento aporta, en una frase]"
basado_en: []
---

# Diseño

Lo redacta Claude al empezar; lo validan quien acepta (lo funcional) y quien audita (lo técnico). Los títulos de sección y de columna no se cambian: el plugin los lee para dibujar el modelo y compararlo con el código, y avisa si no encuentra alguno.

**La regla:** lo que no esté aquí (una entidad, un componente o un concepto) entra solo con una decisión, y esa sesión pone al día este documento.

## Objetivo
[Qué resuelve el producto y para quién, en dos líneas.]

## Reglas
Las reglas de negocio que el producto tiene que cumplir.

| Regla | Excepción |
|---|---|
| [Una frase] | [Cuándo no aplica] |

## Componentes
| Componente | Qué hace | Dónde vive |
|---|---|---|
| [Nombre] | [Una frase] | [organización/repositorio:ruta] |

## Datos
Una fila por entidad, con su nombre en el código. Cada relación se escribe una sola vez: `otra (1:N)` en la entidad del lado «uno» («una de esta, muchas de la otra»); `otra (1:1)` y `otra (N:M)` en la que va primero por orden alfabético. Varias, separadas por coma.

| Entidad | Qué es | Se relaciona con |
|---|---|---|
| [nombre_en_codigo] | [Una frase] | [otra_entidad (1:N)] |

## Conceptos
Las palabras del producto. Un sinónimo no es un concepto nuevo: va en «No es», separado por comas.

| Concepto | Significa | No es |
|---|---|---|
| [Palabra] | [Una frase] | [otra palabra, otra más] |

## Infraestructura
| Pieza | Para qué | Dónde |
|---|---|---|
| [Servidor, base de datos, dominio, servicio externo] | [Una frase] | [Proveedor · entorno] |

## Prototipo
[Enlace y fecha.]
