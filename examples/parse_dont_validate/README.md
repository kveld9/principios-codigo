# Analizar en Lugar de Validar (Parse, Don't Validate)

Este ejemplo demuestra cómo el modelado tipado en las fronteras del sistema elimina la validación
defensiva repetitiva y previene la pérdida de causas raíz en el manejo de excepciones.

## El Problema

En `before.py`, los datos sin estructura (diccionarios primitivos) atraviesan múltiples capas del sistema.
Cada función consumidora repite verificaciones defensivas sobre claves, tipos y rangos. Además,
se capturan excepciones genéricas que son silenciadas sin registrar el error original, imposibilitando
el diagnóstico preciso de fallas.

## Qué Cambió

En `after.py`, se implementa el principio *Parse, don't validate*:

- **Análisis en frontera**: `parse_user_profile` transforma el diccionario crudo en un modelo inmutable `UserProfile`.
- **Excepciones de dominio encadenadas**: los errores arrojan `UserParsingError`
  preservando la causa con `raise ... from err`.
- **Invariantes garantizados**: las funciones del dominio operan directamente sobre tipos seguros sin revalidación defensiva.

## Qué Demuestran las Pruebas

El archivo `test_parse_dont_validate.py` comprueba que las entradas válidas generan entidades tipadas
inmutables, que cada campo defectuoso arroja `UserParsingError` con la excepción original encadenada
en `__cause__`, y evidencia cómo el antipatrón silencia excepciones.
