# 07 - Desarrollo Guiado por Pruebas (TDD)

El desarrollo guiado por pruebas (TDD) es una disciplina de diseño donde las pruebas automatizadas conducen
la implementación paso a paso. Al anteponer la especificación de comportamiento ejecutable al código de
producción, TDD asegura cobertura intrínseca, interfaces desacopladas y retroalimentación inmediata.

---

## 1. Las Tres Leyes y el Ciclo Red-Green-Refactor

La práctica de TDD se rige por las tres leyes de Robert C. Martin: no escribir código de producción sin
una prueba unitaria previa que falle; no escribir más prueba de la necesaria para fallar (no compilar
cuenta como fallo); y no escribir más código de producción del necesario para superar la prueba fallida.

El ciclo **Red -> Green -> Refactor** establece: en **Rojo**, diseñar la prueba mínima que falla;
en **Verde**, escribir la solución más simple que la supere (*fake-it*); en **Refactorización**,
limpiar duplicación y mejorar diseño exclusivamente con pruebas en verde, sin añadir nuevo comportamiento.

---

## 2. Lista de Pruebas, Selección del Siguiente Paso y Triangulación

Antes de codificar se elabora una **Lista de Pruebas** (*Test List*) con casos de uso, límites y errores:
se tachan casos completados e incorporan nuevos sin perder el foco; en cada paso se selecciona el caso
más elemental que aporte información estructural; y se aplica **triangulación** introduciendo dos o más
casos de prueba para justificar la generalización del algoritmo.

---

## 3. Kata Paso a Paso: Validador de Políticas de Contraseñas

La siguiente kata ilustra la construcción guiada de un validador de contraseñas
`check_password(password: str) -> list[Violation]`. El enum `Violation` define las infracciones posibles y
las violaciones deben reportarse en el orden estricto de declaración del enum.

### Iteración 1: Caso Base Válido (Fake-It)

```python
from enum import Enum


def test_valid_password_returns_empty_violation_list() -> None:
    assert check_password("ValidPassword123") == []


class Violation(Enum):
    TOO_SHORT = "TOO_SHORT"
    MISSING_DIGIT = "MISSING_DIGIT"
    MISSING_UPPERCASE = "MISSING_UPPERCASE"
    MISSING_LOWERCASE = "MISSING_LOWERCASE"


def check_password(password: str) -> list[Violation]:
    return []
```

### Iteración 2: Longitud Mínima Requerida

```python
MINIMUM_PASSWORD_LENGTH = 12


def test_too_short_password_returns_too_short_violation() -> None:
    assert check_password("Short1Aa") == [Violation.TOO_SHORT]


def check_password(password: str) -> list[Violation]:
    return [Violation.TOO_SHORT] if len(password) < MINIMUM_PASSWORD_LENGTH else []
```

### Iteración 3: Presencia de Dígitos Numéricos

```python
def test_missing_digit_returns_missing_digit_violation() -> None:
    assert check_password("PasswordWithoutDigit") == [Violation.MISSING_DIGIT]


def check_password(password: str) -> list[Violation]:
    violations = [Violation.TOO_SHORT] if len(password) < MINIMUM_PASSWORD_LENGTH else []
    if not any(character.isdigit() for character in password):
        violations.append(Violation.MISSING_DIGIT)
    return violations
```

### Iteración 4: Presencia de Mayúsculas

```python
def test_missing_uppercase_returns_missing_uppercase_violation() -> None:
    assert check_password("lowercasepassword123") == [Violation.MISSING_UPPERCASE]


def check_password(password: str) -> list[Violation]:
    violations = [Violation.TOO_SHORT] if len(password) < MINIMUM_PASSWORD_LENGTH else []
    if not any(character.isdigit() for character in password):
        violations.append(Violation.MISSING_DIGIT)
    if not any(character.isupper() for character in password):
        violations.append(Violation.MISSING_UPPERCASE)
    return violations
```

### Iteración 5: Presencia de Minúsculas

```python
def test_missing_lowercase_returns_missing_lowercase_violation() -> None:
    assert check_password("UPPERCASEPASSWORD123") == [Violation.MISSING_LOWERCASE]


def check_password(password: str) -> list[Violation]:
    violations = [Violation.TOO_SHORT] if len(password) < MINIMUM_PASSWORD_LENGTH else []
    if not any(character.isdigit() for character in password):
        violations.append(Violation.MISSING_DIGIT)
    if not any(character.isupper() for character in password):
        violations.append(Violation.MISSING_UPPERCASE)
    if not any(character.islower() for character in password):
        violations.append(Violation.MISSING_LOWERCASE)
    return violations
```

### Iteración 6: Triangulación y Refactorización a Tabla de Reglas

```python
def test_multiple_violations_reported_in_declaration_order() -> None:
    assert check_password("short") == [
        Violation.TOO_SHORT,
        Violation.MISSING_DIGIT,
        Violation.MISSING_UPPERCASE,
    ]
```

Con las pruebas en verde, se refactoriza para erradicar la duplicación hacia una tabla orientada a datos,
sin añadir nuevo comportamiento (extracto de `examples/tdd_kata/policy.py`):

```python
from collections.abc import Callable

PASSWORD_RULES: tuple[tuple[Violation, Callable[[str], bool]], ...] = (
    (Violation.TOO_SHORT, lambda password: len(password) < MINIMUM_PASSWORD_LENGTH),
    (Violation.MISSING_DIGIT, lambda password: not any(character.isdigit() for character in password)),
    (Violation.MISSING_UPPERCASE, lambda password: not any(character.isupper() for character in password)),
    (Violation.MISSING_LOWERCASE, lambda password: not any(character.islower() for character in password)),
)


def check_password(password: str) -> list[Violation]:
    return [violation for violation, predicate in PASSWORD_RULES if predicate(password)]
```

Ejemplo ejecutable: [examples/tdd_kata/](../examples/tdd_kata/)

---

## 4. Corrección de Defectos (Bug Fixing) con TDD

Ante un error en producción, el protocolo exige reproducir la falla mediante una prueba unitaria antes de editar
el código: primero reproducir (test rojo que aísle la causa raíz), luego aplicar la corrección mínima y
conservar la prueba como resguardo contra regresiones.

### Antes y Después: Corrección de Defectos

#### Antes: Código con Defecto en el Límite de Umbral

```python
from decimal import Decimal

DISCOUNT_THRESHOLD = Decimal("100.00")
DISCOUNT_RATE = Decimal("0.10")


def apply_promotional_discount(order_total: Decimal) -> Decimal:
    # Defect: Strict inequality (>) improperly excludes orders at exact threshold
    if order_total > DISCOUNT_THRESHOLD:
        return order_total * (Decimal("1.00") - DISCOUNT_RATE)
    return order_total
```

#### Después: Test Rojo de Reproducción y Corrección Focalizada

El test falla inicialmente con el código anterior al retornar `Decimal("100.00")`. Se corrige `>` a `>=`:

```python
def test_promotional_discount_applies_at_exact_threshold() -> None:
    assert apply_promotional_discount(Decimal("100.00")) == Decimal("90.00")


def apply_promotional_discount(order_total: Decimal) -> Decimal:
    if order_total >= DISCOUNT_THRESHOLD:
        return order_total * (Decimal("1.00") - DISCOUNT_RATE)
    return order_total
```

---

## 5. Ámbitos de Excepción al TDD Estricto

TDD estricto no aplica directamente a picos de exploración (*spikes* desechables), código autogenerado por
compiladores o configuraciones declarativas puras (`yaml`, `json`). Al concluir un *spike*, el código se descarta
y la solución definitiva se implementa guiada por pruebas.

---

## 6. Anti-patrones en TDD

- **Pruebas a posteriori**: Escribir producción antes sesga las comprobaciones.
- **Pasos gigantes**: Abarcar múltiples reglas complejas en una única iteración.
- **Probar métodos privados**: Acoplar pruebas a la estructura interna y no al contrato público.
- **Refactorizar en rojo**: Modificar la estructura de producción mientras existen pruebas rotas.
- **Pruebas espejo**: Validar la implementación interna en vez del resultado observable.

### Antes y Después: Verificación de Contrato vs Detalles Privados

#### Antes: Test Acoplado a Métodos Privados y Detalles de Implementación

```python
def _contains_digit(password: str) -> bool:
    return any(character.isdigit() for character in password)


def test_internal_digit_helper() -> None:
    assert _contains_digit("PasswordWithoutDigit") is False
```

#### Después: Test Basado en Contrato Público y Comportamiento Observable

```python
from examples.tdd_kata.policy import Violation, check_password


def test_check_password_reports_missing_digit_violation() -> None:
    assert check_password("PasswordWithoutDigit") == [Violation.MISSING_DIGIT]
```

---

## 7. Checklist de Verificación

- [ ] Cada nueva funcionalidad o corrección inicia con una prueba unitaria que falla.
- [ ] La solución inicial en verde utiliza el código más simple posible (*fake-it* o condicional elemental).
- [ ] La refactorización se ejecuta exclusivamente con todas las pruebas en estado verde.
- [ ] Se utilizó triangulación para justificar generalizaciones de diseño algorítmico.
- [ ] Los defectos reportados cuentan con una prueba roja de reproducción antes de modificar producción.
- [ ] Las pruebas evalúan comportamiento observable sobre contratos públicos sin acceder a métodos privados.

---

## Navegación

- Anterior: [06 - Nombres, Legibilidad y Comentarios](06-nombres.md)
- Siguiente: [08 - Estrategia de Testing](08-testing.md)
- Volver al [README principal](../README.md)
