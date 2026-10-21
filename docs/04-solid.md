# 04 - Principios SOLID

Los principios SOLID son directrices de diseño para software modular y orientado a objetos que garantizan la
mantenibilidad, facilitan las pruebas unitarias y definen límites de responsabilidad sin sobre-ingeniería.

---

## 1. Responsabilidad Única (SRP)

Una clase debe tener una sola razón para cambiar, resolviendo una única responsabilidad del dominio.
Señal de infracción: clases que combinan lógica de cálculo contable con persistencia en base de datos.

```python
# Before: Invoice class mixing tax calculation with database persistence
from decimal import Decimal
import sqlite3

TAX_RATE = Decimal("0.21")


class Invoice:
    def __init__(self, invoice_id: str, amount: Decimal) -> None:
        self.invoice_id = invoice_id
        self.amount = amount

    def save(self, database_path: str) -> None:
        total = self.amount * (Decimal("1.00") + TAX_RATE)
        with sqlite3.connect(database_path) as connection:
            connection.execute("INSERT INTO invoices VALUES (?, ?)", (self.invoice_id, str(total)))
```

```python
# After: Pure domain entity delegating persistence to repository protocol
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

TAX_RATE = Decimal("0.21")


@dataclass(frozen=True)
class Invoice:
    invoice_id: str
    amount: Decimal

    def calculate_total(self) -> Decimal:
        return self.amount * (Decimal("1.00") + TAX_RATE)


class InvoiceRepository(Protocol):
    def save(self, invoice: Invoice, total: Decimal) -> None: ...
```

---

## 2. Abierto/Cerrado (OCP)

Las entidades de software deben estar abiertas a la extensión, pero cerradas a la modificación de código probado.
Señal de infracción: cadenas `if-elif-else` que se editan ante cada nueva variante de negocio.
Esta refactorización polimórfica se justifica al crecer las variantes, según la regla de tres de la sección 6.

```python
# Before: Conditional dispatch requires editing existing code for new variants
from decimal import Decimal

VIP_DISCOUNT = Decimal("0.15")


def calculate_discount(customer_type: str, price: Decimal) -> Decimal:
    return price * VIP_DISCOUNT if customer_type == "VIP" else Decimal("0.00")
```

```python
# After: Polymorphic strategy allows extension without modifying existing code
from decimal import Decimal
from typing import Protocol

VIP_DISCOUNT = Decimal("0.15")


class DiscountPolicy(Protocol):
    def compute_discount(self, price: Decimal) -> Decimal: ...


class VipDiscountPolicy:
    def compute_discount(self, price: Decimal) -> Decimal:
        return price * VIP_DISCOUNT


class StandardDiscountPolicy:
    def compute_discount(self, price: Decimal) -> Decimal:
        return Decimal("0.00")


def calculate_discount(policy: DiscountPolicy, price: Decimal) -> Decimal:
    return policy.compute_discount(price)
```

---

## 3. Sustitución de Liskov (LSP)

Los subtipos deben sustituir a sus tipos base sin alterar la correctitud ni los invariantes del programa.
Señal de infracción: subclases que fortalecen precondiciones o lanzan excepciones en métodos heredados.

```python
# Before: Subclass strengthens preconditions, breaking caller expectations
from decimal import Decimal

MINIMUM_WITHDRAWAL = Decimal("1000.00")


class BankAccount:
    def __init__(self, balance: Decimal) -> None:
        self.balance = balance

    def withdraw(self, amount: Decimal) -> None:
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        self.balance -= amount


class InvestmentAccount(BankAccount):
    def withdraw(self, amount: Decimal) -> None:
        if amount < MINIMUM_WITHDRAWAL:
            raise ValueError("Amount below minimum")
        super().withdraw(amount)
```

```python
# After: Separate hierarchy ensures callers only interact with valid operations
from decimal import Decimal
from typing import Protocol

MINIMUM_WITHDRAWAL = Decimal("1000.00")


class WithdrawableAccount(Protocol):
    def withdraw(self, amount: Decimal) -> None: ...


class StandardAccount:
    def __init__(self, balance: Decimal) -> None:
        self.balance = balance

    def withdraw(self, amount: Decimal) -> None:
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        self.balance -= amount


class InvestmentAccount:
    def __init__(self, balance: Decimal) -> None:
        self.balance = balance

    def request_withdrawal(self, amount: Decimal) -> None:
        if amount < MINIMUM_WITHDRAWAL or amount > self.balance:
            raise ValueError("Invalid investment withdrawal amount")
        self.balance -= amount


def process_withdrawal(account: WithdrawableAccount, amount: Decimal) -> None:
    account.withdraw(amount)
```

---

## 4. Segregación de Interfaces (ISP)

Ningún cliente debe verse forzado a depender de métodos o contratos que no utiliza en su ejecución.
Señal de infracción: protocolos sobrecargados donde los clientes implementan métodos vacíos o con error.

```python
# Before: Fat protocol forcing implementations to declare unsupported operations
from typing import Protocol


class MultiFunctionDevice(Protocol):
    def print_document(self, content: str) -> None: ...
    def scan_document(self) -> str: ...


class BasicPrinter:
    def print_document(self, content: str) -> None: ...

    def scan_document(self) -> str:
        raise NotImplementedError("Scanning unsupported")
```

```python
# After: Fine-grained protocols allow clients to depend strictly on necessary methods
from typing import Protocol


class DocumentPrinter(Protocol):
    def print_document(self, content: str) -> None: ...


class BasicPrinter:
    def print_document(self, content: str) -> None: ...
```

---

## 5. Inversión de Dependencias (DIP)

Los módulos de alto nivel no deben depender de los de bajo nivel; ambos deben depender de abstracciones.
Señal de infracción: clases de negocio que instancian adaptadores de persistencia o red directamente.

```python
# Before: High-level service directly instantiating concrete persistence
class SqliteWriter:
    def write(self, recipient: str, message: str) -> None: ...


class NotificationService:
    def __init__(self) -> None:
        self.writer = SqliteWriter()

    def notify(self, recipient: str, message: str) -> None:
        self.writer.write(recipient, message)
```

```python
# After: Dependency inversion via Protocol abstraction and constructor injection
from typing import Protocol


class NotificationWriter(Protocol):
    def write(self, recipient: str, message: str) -> None: ...


class NotificationService:
    def __init__(self, writer: NotificationWriter) -> None:
        self.writer = writer

    def notify(self, recipient: str, message: str) -> None:
        self.writer.write(recipient, message)
```

---

## 6. SOLID con Proporción

1. **Interfaz por clase**: Crear un protocolo para cada clase concreta duplica archivos sin aportar valor.
2. **Abstracción especulativa**: Crear jerarquías para requerimientos hipotéticos viola el principio YAGNI.
3. **OCP y regla de tres**: Esperar a observar tres variantes concretas antes de formalizar abstracciones.

---

## 7. Señales de Alerta

1. Clases con nombres genéricos (`Manager`, `Handler`) con múltiples responsabilidades.
2. Clases derivadas que lanzan `NotImplementedError` en métodos de su interfaz o superclase.
3. Nuevas funcionalidades que obligan a modificar sentencias `if-elif` en módulos existentes.
4. Interfaces con una sola implementación en el sistema sin necesidad de pruebas aisladas.

---

## 8. Checklist de Verificación

- [ ] Cada clase responde a una única responsabilidad y una sola razón de cambio.
- [ ] La extensión prioriza añadir clases y no editar condicionales (OCP).
- [ ] Las subclases respetan precondiciones e invariantes del supertipo (LSP).
- [ ] Los contratos son específicos y los clientes consumen solo lo necesario (ISP).
- [ ] Las dependencias se inyectan en el constructor mediante abstracciones (DIP).
- [ ] No se crearon abstracciones especulativas antes de contar con variantes reales.

---

## Navegación

- Anterior: [03 - Arquitectura y Dirección de Dependencias](03-arquitectura.md)
- Siguiente: [05 - Funciones Pequeñas y Complejidad Ciclomática](05-funciones.md)
- Volver al [README principal](../README.md)
