---
estado: vigente
actualizado: 2026-11-15
aportacion: "El diseño del portal de pedidos."
basado_en: []
---

# Diseño

Lo redacta Claude al empezar; lo validan quien acepta (lo funcional) y quien audita (lo técnico).

## Objetivo
Que los clientes de la tienda hagan y sigan sus pedidos en línea, sin llamar por teléfono.

## Cómo funciona
1. El cliente elige productos del catálogo.
2. El cliente confirma su pedido y lo paga.
3. La tienda prepara el pedido y avisa al cliente.

## Reglas
Las reglas de negocio que el producto tiene que cumplir.

| Regla | Excepción |
|---|---|
| Un pedido se paga antes de prepararse | Los clientes frecuentes pagan al recibir |
| Un producto agotado no se puede pedir | Ninguna |

## Componentes
| Componente | Qué hace | Dónde vive | Conecta con |
|---|---|---|---|
| Tienda web | La página donde el cliente pide | muestra/portal:web | API |
| API | Guarda y entrega los pedidos | muestra/portal:api | Motor de pagos |
| Motor de pagos | Cobra los pedidos | muestra/portal:pagos | |
| Panel interno | Donde la tienda prepara los pedidos | muestra/portal:panel | API · Motor de pagos |

## Datos
Una fila por entidad, con su nombre en el código, y cada relación escrita una sola vez.

| Entidad | Grupo | Qué es | Se relaciona con |
|---|---|---|---|
| cliente | Ventas | Quien compra en la tienda | pedido (1:N) |
| pedido | Ventas | Lo que un cliente pide de una vez | producto (N:M) |
| producto | Catálogo | Lo que la tienda vende | categoria (N:1) |
| categoria | Catálogo | Un grupo de productos | |

Detalle: ventas/portal/entregables/datos-detalle.md

## Conceptos
Las palabras del producto. Un sinónimo no es un concepto nuevo: va en «No es».

| Concepto | Significa | No es | Entidades |
|---|---|---|---|
| Pedido | Lo que un cliente compra de una vez | orden, carrito | pedido · cliente |
| Cliente frecuente | Un cliente con más de diez pedidos | socio | cliente |
| Catálogo | Todo lo que la tienda vende | inventario | producto · categoria |

## Infraestructura
| Pieza | Para qué | Dónde | Conecta con |
|---|---|---|---|
| Servidor web | Sirve la tienda y la API | Nube · producción | Base de datos |
| Base de datos | Guarda clientes, pedidos y productos | Nube · producción | |
| Dominio | La dirección de la tienda | Registrador · producción | Servidor web |

## Prototipo
Sin prototipo.
