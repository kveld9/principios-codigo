# 05 - Funciones Pequeñas y Complejidad Ciclomática

Funciones breves y con flujo directo reducen la carga cognitiva y evitan defectos en producción.
Toda función debe resolver un único problema en un único nivel de abstracción.

---

## 1. Umbrales Cuantitativos por Defecto

Límites por defecto (los linters configurados en el proyecto tienen prioridad):

| Métrica | Objetivo Recomendado | Límite Estricto | Justificación Técnica |
| :--- | :--- | :--- | :--- |
| **Complejidad Ciclomática (CC)** | CC <= 5 | CC <= 10 | Limita los caminos independientes que requieren pruebas. |
| **Longitud de Función** | <= 20-30 líneas | <= 40 líneas | Permite visualizar la unidad de código en una sola pantalla. |
| **Número de Parámetros** | <= 2 parámetros | <= 3-4 parámetros | Reduce el acoplamiento y previene errores en argumentos. |
| **Profundidad de Anidamiento** | <= 1 nivel | <= 2 niveles | Erradica el anti-patrón de flecha (*arrow anti-pattern*). |

---

## 2. Cálculo de Complejidad Ciclomática

Complejidad Ciclomática (McCabe): $\text{CC} = 1 + D$, con $D$ como puntos de decisión (`if`, bucles, `except`, `case`).

```python
# Worked example: Base CC = 1; two decision points (if) yield CC = 3
def classify_tier(points: int) -> str:
    if points >= 1000:
        return "PLATINUM"
    if points >= 500:
        return "GOLD"
    return "STANDARD"
```

---

## 3. Técnicas de Refactorización para Reducir Complejidad

### Cláusulas de Guarda (Early Return) y Extracción de Funciones

```python
# Before: Arrow anti-pattern with deep nesting and multiple branches
from decimal import Decimal

VIP_RATE = Decimal("0.80")
STANDARD_RATE = Decimal("0.90")


def process_order(price: Decimal, is_active: bool, is_vip: bool) -> Decimal:
    if is_active:
        if price > Decimal("0.00"):
            return price * (VIP_RATE if is_vip else STANDARD_RATE)
        raise ValueError("Price must be positive")
    return price
```

```python
# After: Guard clauses preserving semantics with flat control flow and pure helper
from decimal import Decimal

VIP_RATE = Decimal("0.80")
STANDARD_RATE = Decimal("0.90")


def apply_discount(price: Decimal, is_vip: bool) -> Decimal:
    return price * (VIP_RATE if is_vip else STANDARD_RATE)


def process_order(price: Decimal, is_active: bool, is_vip: bool) -> Decimal:
    if not is_active:
        return price
    if price <= Decimal("0.00"):
        raise ValueError("Price must be positive")
    return apply_discount(price, is_vip)
```

Ejemplo ejecutable: [examples/guard_clauses/](../examples/guard_clauses/)

### Tabla de Búsqueda (Lookup Table / Dict Dispatch)

Sustituir cadenas de `if-elif-else` por diccionarios asegura que la función de despacho mantenga CC = 1
independientemente del número de entradas.

```python
# Before: Conditional if-elif chain increasing cyclomatic complexity
from decimal import Decimal


def resolve_shipping_cost(zone: str) -> Decimal:
    if zone == "LOCAL":
        return Decimal("5.00")
    if zone == "REGIONAL":
        return Decimal("12.00")
    return Decimal("25.00")
```

```python
# After: Constant lookup table keeping cyclomatic complexity at CC = 1
from decimal import Decimal

SHIPPING_RATES: dict[str, Decimal] = {"LOCAL": Decimal("5.00"), "REGIONAL": Decimal("12.00")}
DEFAULT_SHIPPING_RATE = Decimal("25.00")


def resolve_shipping_cost(zone: str) -> Decimal:
    return SHIPPING_RATES.get(zone, DEFAULT_SHIPPING_RATE)
```

### Reemplazo de Argumento de Bandera por Dos Funciones

```python
# Before: Boolean flag argument bifurcating internal execution flow
def export_dataset(records: list[str], to_pdf: bool) -> str:
    return f"PDF:{','.join(records)}" if to_pdf else f"CSV:{','.join(records)}"
```

```python
# After: Dedicated functions with explicit intent and no flag parameter
def export_dataset_to_pdf(records: list[str]) -> str:
    return f"PDF:{','.join(records)}"


def export_dataset_to_csv(records: list[str]) -> str:
    return f"CSV:{','.join(records)}"
```

### Objeto de Parámetros (Parameter Object)

```python
# Before: Multiple loose parameters exceeding recommended parameter threshold
def register_customer(first_name: str, last_name: str, email: str, postal_code: str) -> str:
    return f"{first_name} {last_name} <{email}> ({postal_code})"
```

```python
# After: Immutable parameter object encapsulating all four related domain attributes
from dataclasses import dataclass


@dataclass(frozen=True)
class CustomerProfile:
    first_name: str
    last_name: str
    email: str
    postal_code: str


def register_customer(profile: CustomerProfile) -> str:
    return f"{profile.first_name} {profile.last_name} <{profile.email}> ({profile.postal_code})"
```

### Separación de Comandos y Consultas (CQS) y Núcleo Puro

```python
# Before: Mutating state while returning data couples calculation with side effects
from decimal import Decimal


def deduct_and_record_balance(account: dict[str, Decimal], amount: Decimal) -> Decimal:
    new_balance = account["balance"] - amount
    account["balance"] = new_balance
    return new_balance
```

```python
# After: Separation between pure calculation query and state mutation command
from decimal import Decimal


def calculate_deducted_balance(current_balance: Decimal, amount: Decimal) -> Decimal:
    if amount > current_balance:
        raise ValueError("Insufficient balance")
    return current_balance - amount


def apply_balance_mutation(account: dict[str, Decimal], new_balance: Decimal) -> None:
    account["balance"] = new_balance
```

---

## 4. Medición Automatizada y Herramientas

La complejidad ciclomática debe verificarse de manera continua mediante herramientas de análisis estático:

| Herramienta | Comando / Regla | Umbral | Observaciones |
| :--- | :--- | :--- | :--- |
| **Python (Radon)** | `radon cc --min B --show-complexity src/` | Rango B+ | Informa funciones con complejidad B o superior. |
| **Python (Ruff)** | `ruff check --select C901` | CC <= 5 | Falla automáticamente si una función supera el límite. |
| **ESLint** | `complexity: ["error", 5]` | CC <= 5 | Regla nativa en pipelines de Node.js y navegadores. |
| **Kotlin (Detekt)** | `CyclomaticComplexMethod: 5` | CC <= 5 | Análisis estático para proyectos en Kotlin. |
| **Go (Gocyclo)** | `gocyclo -over 5 .` | CC <= 5 | Evalúa funciones y métodos en árboles de código Go. |
| **Lizard** | `lizard -C 5 src/` | CC <= 5 | Analizador agnóstico compatible con múltiples lenguajes. |

---

## 5. Anti-patrón: Compresión Artificial en Una Línea

Comprimir bifurcaciones en expresiones ternarias para sortear linters incrementa la carga cognitiva:

```python
# Artificial branch compression to evade line counter limits
result = val * 2 if condition_a else (val * 3 if condition_b else (val * 4 if condition_c else 0))
```

---

## 6. Señales de Alerta

1. **Indentación > 2 niveles**: Acumulación de bucles y condicionales anidados.
2. **Funciones extensas**: Dificultan el seguimiento visual del flujo de datos.
3. **Parámetros booleanos de bifurcación**: Evidencian dos tareas dentro de la misma función.
4. **Listas de argumentos > 3 parámetros**: Propensas a errores de invocación posicional.

---

## 7. Checklist de Verificación

- [ ] Complejidad ciclomática CC <= 5 (límite estricto 10).
- [ ] Longitud de la función <= 30-40 líneas de código.
- [ ] Cláusulas de guarda al inicio para validar precondiciones y abortar tempranamente.
- [ ] Argumentos booleanos de bifurcación eliminados y separados en funciones dedicadas.
- [ ] Agrupaciones de más de 3 parámetros encapsuladas en objetos inmutables.
- [ ] Consultas libres de efectos colaterales y mutaciones sin retorno de cálculo (CQS).

---

## Navegación

- Anterior: [04 - Principios SOLID](04-solid.md)
- Siguiente: [06 - Nombres, Legibilidad y Comentarios](06-nombres.md)
- Volver al [README principal](../README.md)
