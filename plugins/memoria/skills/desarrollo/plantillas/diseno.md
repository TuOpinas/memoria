---
estado: borrador
actualizado: AAAA-MM-DD
aportacion: "[Lo que este documento aporta, en una frase]"
basado_en: []
---

# Diseño

Lo redacta Claude al empezar; lo validan quien acepta (lo funcional) y quien audita (lo técnico). Las tablas son el formato recomendado: ningún script las lee, así que se pueden adaptar al proyecto.

**La regla:** lo que no esté aquí (una entidad, un componente o un concepto) entra solo con una decisión, y esa sesión pone al día este documento. El seguimiento compara lo unido con lo que dice este documento.

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
Una fila por entidad, con su nombre en el código, y cada relación escrita una sola vez.

| Entidad | Qué es | Se relaciona con |
|---|---|---|
| [nombre_en_codigo] | [Una frase] | [otra_entidad (1:N)] |

## Conceptos
Las palabras del producto. Un sinónimo no es un concepto nuevo: va en «No es».

| Concepto | Significa | No es |
|---|---|---|
| [Palabra] | [Una frase] | [otra palabra, otra más] |

## Infraestructura
| Pieza | Para qué | Dónde |
|---|---|---|
| [Servidor, base de datos, dominio, servicio externo] | [Una frase] | [Proveedor · entorno] |

## Prototipo
[Enlace y fecha.]
