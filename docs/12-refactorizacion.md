# 12 - Code Smells y Refactorización Segura

La refactorización es la disciplina técnica de modificar la estructura interna de un sistema de software sin alterar
su comportamiento observable externo. Su objetivo consiste en controlar la deuda técnica, reducir la complejidad
ciclomática y mejorar la legibilidad para facilitar el mantenimiento y la evolución del código.

Este documento formaliza el procedimiento de transformación segura, el catálogo de síntomas de degradación
(*code smells*), las pautas para el principio DRY con criterio y la estrategia de migración mediante estrangulamiento.

---

## 1. Procedimiento de Refactorización Segura

Cualquier cambio estructural ejecutado sin una red de contención automatizada constituye una fuente directa de
regresiones en producción. La refactorización debe regirse por un ciclo estricto y disciplinado:

1. **Pruebas de caracterización previas**: Antes de modificar código legado o frágil, deben escribirse pruebas de
   caracterización (*pinning tests*) que congelen el comportamiento observable actual, incluyendo casos límite y fallos.
2. **Pasos pequeños que preservan comportamiento**: Aplicar transformaciones elementales (renombrar, extraer función,
   introducir parámetro) en pasos discretos de mínima superficie de cambio.
3. **Ejecución inmediata de pruebas**: La suite de pruebas debe ejecutarse tras cada micro-paso para validar que el
   comportamiento se mantiene intacto.
4. **Un commit por paso**: Registrar cada paso atómico individualmente en Git. Si un paso introduce una anomalía,
   debe revertirse de inmediato con `git revert` sin descartar los pasos previos ya consolidados.
5. **Separación estricta de intenciones**: Queda estrictamente prohibido combinar refactorizaciones estructurales y
   cambios de comportamiento de negocio en el mismo commit.

---

## 2. Código Comentado Muerto y Principio DRY con Criterio

### Prohibición de Código Comentado Muerto

El árbol de código debe contener únicamente lógica activa en producción o pruebas vigentes.

- **Git como única memoria histórica**: Nunca conservar bloques de código deshabilitados mediante comentarios
  bajo la justificación de "por si se necesita después". El historial de commits de Git es la herramienta
  diseñada para consultar implementaciones anteriores.
- **Eliminación sistemática**: Durante refactorizaciones o sustitución de algoritmos, el código obsoleto debe
  borrarse por completo del archivo fuente.
- **Comentarios orientados a la intención**: Los comentarios deben explicar el *por qué* de una decisión no obvia
  o una restricción externa de hardware o negocio, nunca relatar lo que el código ya describe explícitamente
  ni contener código muerto (ver [06 - Nombres, Legibilidad y Comentarios](06-nombres.md)).

### Principio DRY con Criterio (Don't Repeat Yourself)

La duplicación indiscriminada genera inconsistencias de mantenimiento; sin embargo, la abstracción prematura
produce sistemas rígidos e incomprensibles.

- **Duplicación de conocimiento vs coincidencia estructural**: El principio DRY busca unificar el conocimiento
  de negocio y las fuentes únicas de verdad (ver [10 - Anti-Hardcoding](10-hardcoding.md)). Dos bloques de código
  que lucen estructuralmente similares pero representan conceptos de dominio distintos no deben fusionarse
  precipitadamente.
- **La regla de tres**: Antes de extraer una abstracción genérica o framework interno, esperar a observar al menos
  tres instancias reales de duplicación idéntica.
- **Preferencia por el desacoplamiento local**: Una duplicación controlada y local es preferible a una abstracción
  incorrecta que acople fuertemente módulos independientes (*wrong abstraction is worse than duplication*).

---

## 3. Catálogo de Code Smells y Refactorizaciones Clave

| Code Smell | Síntoma Principal | Refactorización Recomendada | Documento Relacionado |
| :--- | :--- | :--- | :--- |
| **Long Function** | Función extensa con múltiples niveles de anidamiento | Extracción de funciones y cláusulas de guarda | [05 - Funciones Pequeñas](05-funciones.md) |
| **Large Class** | Clase con excesivas responsabilidades y métodos | Extracción de clases por responsabilidad única (SRP) | [04 - Principios SOLID](04-solid.md) |
| **Long Parameter List** | Firmas con más de 3 o 4 argumentos posicionales | Introducir objeto de parámetros o DTO inmutable | [05 - Funciones Pequeñas](05-funciones.md) |
| **Feature Envy** | Método que consulta intensivamente datos de otro objeto | Mover método hacia el objeto que posee los datos | [02 - Diseño Modular](02-diseno-modular.md) |
| **Shotgun Surgery** | Un cambio de requerimiento obliga a editar múltiples archivos | Centralizar lógica dispersa en un único módulo | [02 - Diseño Modular](02-diseno-modular.md) |
| **Divergent Change** | Una misma clase cambia por motivos y actores distintos | Separación de clases según razones de cambio | [04 - Principios SOLID](04-solid.md) |
| **Primitive Obsession** | Uso de escalares primitivos para conceptos de dominio | Reemplazar primitivo por Objeto de Valor (*Value Object*) | [03 - Arquitectura](03-arquitectura.md) |
| **Data Clumps** | Grupos de campos que siempre viajan juntos | Encapsular campos repetidos en dataclass inmutable | [05 - Funciones Pequeñas](05-funciones.md) |
| **Speculative Generality** | Abstracciones e interfaces creadas para casos hipotéticos | Eliminar código anticipado y aplicar YAGNI | [01 - Principios](01-principios.md) |
| **Dead Code** | Código inalcanzable, funciones huérfanas o bloques comentados | Eliminación total confiando en el historial de Git | [06 - Nombres](06-nombres.md) |
| **Duplicated Knowledge** | Múltiples fuentes de verdad para un mismo dato o regla | Centralizar en Fuente Única de Verdad (SSOT) | [10 - Anti-Hardcoding](10-hardcoding.md) |

---

## 4. Ejemplos de Refactorización Segura

### Extracción de Funciones (Extract Function)

#### Antes: Función Monolítica con Múltiples Responsabilidades

```python
# Monolithic function mixing input validation, discount math, and tax calculation
from decimal import Decimal


def calculate_invoice_total(
    base_amount: Decimal, discount_percentage: Decimal, tax_rate: Decimal
) -> Decimal:
    if base_amount <= Decimal("0"):
        raise ValueError("Base amount must be positive")
    discount_amount = base_amount * (discount_percentage / Decimal("100"))
    discounted_subtotal = base_amount - discount_amount
    tax_amount = discounted_subtotal * tax_rate
    return discounted_subtotal + tax_amount
```

#### Después: Orquestación Concisa con Funciones Puras Extraídas

```python
# Small focused pure functions preserving domain semantics and simplifying unit tests
from decimal import Decimal


def calculate_discount(base_amount: Decimal, discount_percentage: Decimal) -> Decimal:
    return base_amount * (discount_percentage / Decimal("100"))


def calculate_tax(taxable_amount: Decimal, tax_rate: Decimal) -> Decimal:
    return taxable_amount * tax_rate


def calculate_invoice_total(
    base_amount: Decimal, discount_percentage: Decimal, tax_rate: Decimal
) -> Decimal:
    if base_amount <= Decimal("0"):
        raise ValueError("Base amount must be positive")
    subtotal = base_amount - calculate_discount(base_amount, discount_percentage)
    return subtotal + calculate_tax(subtotal, tax_rate)
```

### Reemplazo de Primitivo por Objeto de Valor (Value Object)

#### Antes: Manejo de Moneda y Saldo como Primitivos Sueltos

```python
# Primitive obsession allows accidental currency mismatch and loose validation
from decimal import Decimal


def apply_fee(balance: Decimal, currency: str, fee_amount: Decimal, fee_currency: str) -> Decimal:
    if currency != fee_currency:
        raise ValueError(f"Currency mismatch: {currency} vs {fee_currency}")
    return balance - fee_amount
```

#### Después: Encapsulamiento en Objeto de Valor Inmutable

```python
# Immutable Money Value Object enforces currency matching and self-validating operations
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def subtract(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"Currency mismatch: {self.currency} vs {other.currency}")
        return Money(amount=self.amount - other.amount, currency=self.currency)


def apply_fee(current_balance: Money, fee: Money) -> Money:
    return current_balance.subtract(fee)
```

Ejemplo ejecutable: [examples/value_object/](../examples/value_object/)

---

## 5. Refactorización frente a Reescritura: El Patrón Strangler

Intentar una reescritura total (*big bang rewrite*) de un sistema legado presenta una tasa de fracaso extraordinariamente
alta: interrumpe la entrega de valor, desecha años de corrección de casos borde implícitos y genera retrasos crónicos.

En su lugar, debe aplicarse el **Patrón Estrangulador (*Strangler Fig Pattern*)**:

1. **Identificar una frontera vertical**: Seleccionar un caso de uso o subsistema acotado del módulo legado.
2. **Implementar el nuevo componente aislado**: Diseñar el nuevo módulo bajo arquitectura limpia y pruebas rigurosas.
3. **Interponer un enrutador o adaptador**: Desviar gradualmente el tráfico o las llamadas del componente antiguo hacia
   el nuevo.
4. **Retirar el código legado una vez reemplazado**: Eliminar las secciones obsoletas cuando la totalidad del tráfico
   sea atendida por el nuevo diseño.

Ejemplo ejecutable: [examples/god_module_split/](../examples/god_module_split/)

---

## 6. Señales de Alerta

- Iniciar reestructuraciones de código sin contar previamente con pruebas automatizadas que verifiquen el estado actual.
- Mezclar cambios de reglas de negocio con renombrados o extracciones de funciones en el mismo commit.
- Abstraer lógica tras observar únicamente dos casos con similitud sintáctica circunstancial.
- Presencia de bloques de código antiguo deshabilitados mediante comentarios en archivos activos.
- Ramas de refactorización de larga duración que acumulan divergencias graves respecto a `main`.

---

## 7. Checklist de Verificación

- [ ] Existen pruebas de caracterización que congelan el comportamiento observable antes de modificar el código.
- [ ] Las transformaciones se ejecutan en micro-pasos respaldados por la ejecución inmediata de la suite.
- [ ] Cada refactorización estructural reside en un commit atómico independiente sin mezclar cambios de negocio.
- [ ] No existen bloques de código comentado muerto ni funciones huérfanas en el árbol de código.
- [ ] La extracción de abstracciones DRY respeta la regla de tres y evita acoplar conceptos conceptualmente distintos.
- [ ] Los tipos primitivos con reglas de validación o monedas se encapsulan en Objetos de Valor (*Value Objects*).
- [ ] La modernización de subsistemas monolíticos aplica el patrón estrangulador en lugar de reescrituras masivas.

---

## Navegación

- Anterior: [11 - Inyección y Gestión de Dependencias](11-dependencias.md)
- Siguiente: [13 - Revisión de Código](13-revision.md)
- Volver al [README principal](../README.md)
