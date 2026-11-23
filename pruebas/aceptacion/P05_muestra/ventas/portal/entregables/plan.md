---
estado: vigente
actualizado: 2026-11-18
aportacion: "El plan del portal de pedidos."
basado_en: []
---

# Plan

Las fases dicen qué valor entrega cada una; las piezas, qué es estar hecha.

## Fases
| Fase | Qué podrá hacer quién | Versión | Listo cuando | Estado |
|---|---|---|---|---|
| F1 · Catálogo | El cliente ve los productos y sus precios | 1.0.0 | P01 y P02 pasan | en curso |
| F2 · Pedidos | El cliente pide y paga en línea | 1.1.0 | P03 pasa | pendiente |

Estado: `cerrada`, `en curso` (solo una) o `pendiente`.

### F1 en llano
El cliente puede ver en línea qué vende la tienda y a qué precio.

| Pieza | Qué arregla |
|---|---|
| P01 | Ver los productos sin llamar |
| P02 | Saber el precio de cada producto |

### F2 en llano
El cliente puede hacer y pagar su pedido sin llamar.

| Pieza | Qué arregla |
|---|---|
| P03 | Pedir y pagar en línea |

## Piezas
Las de fases cerradas se quedan. Un identificador no se reutiliza nunca.

| Pieza | Fase | Qué entrega |
|---|---|---|
| P01 · Lista de productos | F1 | La tienda muestra todos los productos con su categoría |
| P02 · Precios | F1 | Cada producto muestra su precio vigente |
| P03 · Pedido en línea | F2 | El cliente arma un pedido y lo paga |

## Hecha cuando
Una pieza está hecha cuando pasan sus escenarios.

### P01 · Lista de productos
Aprobó: Ana Pérez, 2026-11-12

- **Se ven todos los productos**
  Dado un catálogo con tres productos
  Cuando el cliente abre la tienda
  Entonces ve los tres productos con su categoría
- **Un catálogo vacío se dice**
  Dado un catálogo sin productos
  Cuando el cliente abre la tienda
  Entonces la tienda dice que aún no hay productos

### P02 · Precios
Aprobó: Ana Pérez, 2026-11-13

- **Cada producto muestra su precio**
  Dado un producto con precio
  Cuando el cliente lo ve
  Entonces ve su precio vigente

### P03 · Pedido en línea
Aprobó: Ana Pérez, 2026-11-14

- **Un pedido pagado queda registrado**
  Dado un cliente con dos productos elegidos
  Cuando paga su pedido
  Entonces el pedido queda registrado como pagado

## Cómo avanza
- Se construye por bloques.
