# Kata de Desarrollo Guiado por Pruebas (TDD Kata)

Este ejemplo implementa una política de validación de contraseñas siguiendo el ciclo estricto
de desarrollo guiado por pruebas (Red -> Green -> Refactor).

## El Problema

Las reglas de validación suelen acumular verificaciones ad-hoc difíciles de mantener, sin orden
garantizado y con lógica dispersa que tiende a omitir casos límite de seguridad.

## Qué Cambió (Ciclo TDD)

La solución se construyó paso a paso desde las pruebas en `test_policy.py` hacia `policy.py`:

1. `test_valid_password_returns_empty_violation_list`: contraseña válida retorna `[]`.
2. `test_too_short_password_returns_too_short_violation`: longitud < 12 reporta `TOO_SHORT`.
3. `test_missing_digit_returns_missing_digit_violation`: ausencia de dígitos reporta `MISSING_DIGIT`.
4. `test_missing_uppercase_returns_missing_uppercase_violation`: sin mayúsculas reporta `MISSING_UPPERCASE`.
5. `test_missing_lowercase_returns_missing_lowercase_violation`: sin minúsculas reporta `MISSING_LOWERCASE`.
6. `test_multiple_violations_reported_in_declaration_order`: múltiples fallas en orden de declaración.
7. **Paso de Refactorización**: tras superar las pruebas con condicionales simples, la lógica se transformó
   en un diseño orientado a datos mediante la tupla `PASSWORD_RULES` compuesta por pares `(Violation, predicate)`.

## Qué Demuestran las Pruebas

Las pruebas unitarias garantizan que el validador reporta exhaustivamente todas las infracciones
presentes en una contraseña, preservando el orden estricto de declaración del enum `Violation`.
