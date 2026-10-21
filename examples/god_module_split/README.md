# Separación de Módulo Dios (God Module Split)

Este ejemplo aborda el antipatrón de diseño conocido como Módulo Dios (*God Module*), donde un único
archivo concentra múltiples responsabilidades arquitectónicas divergentes y usa aritmética imprecisa.

## El Problema

En `before.py`, la función monolítica `process_order` ejecuta secuencialmente deserialización de cargas,
validación de negocio, cálculo de precios con `float`, mutación de un almacén global y formateo de texto.
Esta concentración genera acoplamiento, estado mutable compartido e imprecisión en los cálculos monetarios.

## Qué Cambió

En el paquete `after/`, cada preocupación se extrae a un módulo con responsabilidad única:

- `models.py`: define entidades inmutables y valores monetarios con `Decimal`.
- `parsing.py`: transforma diccionarios primitivos en modelos tipados.
- `validation.py`: comprueba invariantes de negocio (identificadores, correos, productos).
- `pricing.py`: computa subtotales, descuentos e impuestos usando `Decimal` exacto.
- `storage.py`: encapsula el repositorio de persistencia en memoria sin estado global.
- `notification.py`: construye el cuerpo textual del aviso de confirmación.
- `service.py`: orquesta la secuencia de procesamiento mediante inyección de dependencias.
- `__init__.py`: expone `OrderProcessingService` y la raíz de composición `build_order_service`.

## Qué Demuestran las Pruebas

El archivo `test_god_module_split.py` comprueba equivalencia diferencial mediante conversión explícita
(`Decimal(str(before_value))`), demostrando que la versión `after` es exacta donde `float` puede sufrir
deriva, y valida el aislamiento de repositorios inyectados sin singleton global.
