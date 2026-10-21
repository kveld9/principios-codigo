# Cláusulas de Guarda y Tablas de Despacho (Guard Clauses)

Este ejemplo ilustra la reducción sistemática de complejidad ciclomática en el cálculo de tarifas
de envío mediante cláusulas de guarda, tablas de despacho y aritmética monetaria exacta con `Decimal`.

## El Problema

En `before.py`, la función `calculate_shipping_cost` implementa validaciones y tarifas mediante condicionales
anidados `if/else/elif` con CC >= 11 (Grado C en Radon) y utiliza `float`, lo que ocasiona imprecisión binaria.

## Qué Cambió

En `after.py`, se refactoriza el cálculo aplicando técnicas de código limpio y modelado exacto:

- **Cláusulas de guarda**: validación temprana de peso, distancia y restricciones con retorno inmediato.
- **Tabla de despacho (`SHIPPING_DISPATCH`)**: mapeo de categorías a objetos inmutables `ShippingTier`.
- **Aritmética monetaria exacta (`Decimal`)**: tarifas y recargos operan en `Decimal` con redondeo `ROUND_HALF_UP`.
- **Funciones de propósito único**: extracción de recargos especializados con CC <= 3.

## Qué Demuestran las Pruebas

El archivo `test_guard_clauses.py` implementa pruebas diferenciales que comprueban paridad con la versión
previa mediante conversión explícita (`Decimal(str(before_cost))`), validación de excepciones equivalentes, y
una prueba dedicada demostrando que la versión `after` es exacta donde el cálculo con `float` sufre deriva.
