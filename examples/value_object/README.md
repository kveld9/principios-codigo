# Objeto de Valor (Value Object)

Este ejemplo demuestra el reemplazo de tipos primitivos por objetos de valor inmutables (*Value Objects*)
para encapsular reglas de validación y eliminar la imprecisión en aritmética monetaria.

## El Problema

En `before.py`, las cantidades de dinero se representan mediante números de punto flotante primitivos (`float`).
La aritmética de punto flotante binaria introduce imprecisión intrínseca (por ejemplo `0.1 + 0.2 != 0.3` o
`1.03 - 0.42 != 0.61`), pérdidas de centavos por redondeo acumulado y permite sumar montos con monedas
incompatibles sin ningún tipo de validación o restricción semántica.

## Qué Cambió

En `after.py`, se implementa el objeto de valor inmutable `Money`:

- **Precisión decimal exacta**: utiliza `Decimal` cuantizado a dos decimales con redondeo `ROUND_HALF_UP`.
- **Inmutabilidad y validación**: construcción validada que exige códigos de moneda ISO válidos de 3 letras.
- **Operaciones seguras**: los operadores aritméticos verifican coincidencia de moneda y rechazan monedas mixtas.
- **Reparto sin pérdidas**: el método `split` distribuye un monto entre partes sin perder centavos por truncamiento.

## Qué Demuestran las Pruebas

El archivo `test_value_object.py` comprueba que `Money` resuelve con exactitud las operaciones donde
`float` falla por imprecisión, rechaza operaciones aritméticas entre distintas monedas y divide cantidades
de forma exacta preservando la suma total.
