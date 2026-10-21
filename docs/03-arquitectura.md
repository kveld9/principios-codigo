# 03 - Arquitectura y Dirección de Dependencias

La arquitectura de software establece las fronteras estructurales y el sentido de las dependencias entre los componentes
de un sistema. Su propósito fundamental consiste en aislar la lógica de negocio nuclear respecto a los detalles
tecnológicos cambiantes, tales como motores de persistencia, protocolos de transporte, frameworks y servicios externos.

---

## 1. La Regla de Dependencia y el Núcleo de Dominio

Las dependencias en el código fuente deben apuntar siempre hacia adentro, en dirección a las políticas del dominio.

1. **Aislamiento absoluto**: El dominio no debe importar librerías de infraestructura, persistencia ni entrega.
2. **Dominio puro sin I/O**: Las entidades deben ser deterministas y libres de efectos de entrada/salida.
   Queda prohibido ejecutar consultas SQL, lecturas de archivos o llamadas HTTP dentro de métodos de entidad.
3. **Testeabilidad inmediata**: Un modelo puro se ejecuta y verifica en memoria sin levantar bases de datos ni redes.

### Antes y Después: Dominio Puro Desacoplado de I/O

#### Antes: Entidad de Dominio Contaminada con I/O

```python
# Domain entity polluted with direct database queries and side-effects
from decimal import Decimal
import sqlite3


class BankAccount:
    def __init__(self, account_id: str, balance: Decimal) -> None:
        self.account_id = account_id
        self.balance = balance

    def withdraw(self, amount: Decimal, db_path: str) -> None:
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        self.balance -= amount
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "UPDATE accounts SET balance = ? WHERE id = ?",
                (str(self.balance), self.account_id),
            )
```

#### Después: Entidad de Dominio Pura y Determinista

```python
# Pure domain entity with deterministic logic and zero I/O side effects
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class BankAccount:
    account_id: str
    balance: Decimal

    def withdraw(self, amount: Decimal) -> None:
        if amount <= Decimal("0"):
            raise ValueError(f"Withdrawal amount must be positive, got: {amount}")
        if amount > self.balance:
            raise ValueError(
                f"Insufficient funds: balance {self.balance}, requested {amount}"
            )
        self.balance -= amount
```

---

## 2. Capas Arquitectónicas Fundamentales

El sistema se organiza en cuatro capas concéntricas con responsabilidades delimitadas:

```text
[ Entrega ] ──► [ Aplicación ] ──► [ Dominio ] ◄── [ Infraestructura ]
```

1. **Dominio**: Entidades de negocio, invariantes y tipos fundamentales (`Value Objects`) sin dependencias.
2. **Aplicación**: Casos de uso que orquestan el flujo de información entre entidades y contratos de salida (puertos).
3. **Infraestructura**: Adaptadores para herramientas tecnológicas (SQL, clientes HTTP, colas) que implementan puertos.
4. **Entrega (*Delivery*)**: Puntos de entrada (APIs REST, CLI, suscriptores) que traducen peticiones hacia casos de uso.

---

## 3. Puertos y Adaptadores (Arquitectura Hexagonal)

La arquitectura hexagonal materializa la inversión de dependencias desacoplando la aplicación mediante **puertos**.

- **Puertos primarios (*driving*)**: Interfaces que exponen los casos de uso hacia la capa de entrega.
- **Puertos secundarios (*driven*)**: Contratos abstractos declarados por la aplicación para delegar I/O.
- **Adaptadores**: Implementaciones concretas de los puertos que conducen o son conducidos por la aplicación.

### Antes y Después: Puertos con Protocols y Adaptadores

#### Antes: Dependencia Acoplada a Driver Concreto

```python
# Direct dependency on concrete third-party database driver in business logic
import sqlite3


class OrderService:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def cancel_order(self, order_id: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE orders SET status = 'CANCELLED' WHERE id = ?",
                (order_id,),
            )
```

#### Después: Puerto Abstracto con Protocol y Adaptador en Memoria

```python
# Hexagonal port, domain entity, service, and in-memory adapter
from dataclasses import dataclass, replace
from typing import Protocol


@dataclass(frozen=True)
class Order:
    order_id: str
    status: str


class OrderRepository(Protocol):
    def get(self, order_id: str) -> Order | None: ...
    def save(self, order: Order) -> None: ...


class OrderService:
    def __init__(self, repo: OrderRepository) -> None:
        self._repo = repo

    def cancel_order(self, order_id: str) -> Order:
        order = self._repo.get(order_id)
        if order is None:
            raise KeyError(f"Order not found: {order_id}")
        cancelled = replace(order, status="CANCELLED")
        self._repo.save(cancelled)
        return cancelled


class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._storage: dict[str, Order] = {}

    def get(self, order_id: str) -> Order | None:
        return self._storage.get(order_id)

    def save(self, order: Order) -> None:
        self._storage[order.order_id] = order
```

---

## 4. Límites como Contratos de Datos: DTOs vs Entidades

El paso de información a través de las fronteras arquitectónicas debe regularse mediante contratos formales:

1. **DTOs (Data Transfer Objects)**: Estructuras inmutables sin lógica (`dataclass(frozen=True)`) para transferir datos
   entre capas externas y casos de uso.
2. **Entidades de dominio**: Objetos que encapsulan estado e invariantes. No deben serializarse directamente a HTTP ni
   construirse a partir de cargas no validadas.
3. **Mapeo en la frontera**: Los adaptadores traducen DTOs hacia entidades y viceversa para no contaminar el dominio.

---

## 5. El Composition Root (Punto Único de Ensamblaje)

El **Composition Root** es el único lugar centralizado donde se inicializa el grafo de dependencias de la aplicación.
Se ubica en el punto de arranque (`main.py` o bootstrap) y es el único componente autorizado a instanciar adaptadores:

```python
# Composition Root: sole factory instantiating adapters and wiring services
def build_order_service() -> OrderService:
    repository = InMemoryOrderRepository()
    return OrderService(repo=repository)


def main() -> None:
    service = build_order_service()
    service.cancel_order("ord-100")
```

Queda prohibido el uso de localizadores globales (*Service Locators*) o la resolución dispersa en capas de negocio.

---

## 6. Arquitectura Proporcional: Cuándo NO Aplicar Capas

La separación en capas e inversión mediante puertos introduce indirección que solo se justifica cuando la complejidad
del dominio lo amerita. Casos donde no debe aplicarse:

1. **Scripts monopropósito y automatizaciones**: Programas lineales de menos de 300 líneas.
2. **Prototipos exploratorios y pruebas de concepto**: Diseños descartables orientados a validar hipótesis con rapidez.
3. **Herramientas CLI simples**: Utilitarios con interacción directa y lineal sobre un único recurso.

---

## 7. Verificación Automatizada del Flujo de Dependencias

Para evitar la degradación de dependencias, las direcciones de importación deben verificarse en integración continua.
Herramientas como `import-linter` en Python formalizan contratos de arquitectura:

- El módulo `domain` no puede importar de `application`, `infrastructure` ni `delivery`.
- El módulo `application` no puede importar de `infrastructure` ni `delivery`.
- Las violaciones se detectan como fallos automáticos en el pipeline antes de fusionar el código.

---

## 8. Anti-patrones Arquitectónicos

1. **Fuga de I/O al dominio**: Entidades o servicios de dominio que realizan llamadas a disco, red o bases de datos.
2. **Entidades anémicas**: Clases reducidas a bolsas de atributos sin métodos de negocio ni validación de invariantes.
3. **Inversión cosmética**: Interfaces creadas dentro de infraestructura o asociadas 1:1 a una única implementación.
4. **Acoplamiento de entrega con persistencia**: Controladores web que ejecutan sentencias SQL directamente.

---

## 9. Checklist de Verificación

Antes de aprobar o integrar un diseño arquitectónico, verificar los siguientes puntos:

- [ ] Las dependencias de código fuente apuntan exclusivamente hacia el núcleo de dominio.
- [ ] Las entidades y reglas de dominio están libres de operaciones de entrada/salida (I/O).
- [ ] La capa de aplicación define contratos abstractos (puertos) para interactuar con infraestructura.
- [ ] Se utilizan DTOs inmutables para el cruce de fronteras entre entrega y aplicación.
- [ ] La instanciación y conexión de dependencias se centraliza en el Composition Root.
- [ ] No se aplicó una arquitectura en capas excesiva a scripts breves o utilitarios monopropósito.

---

## Navegación

- Anterior: [02 - Diseño Modular y Eliminación de Monolitos](02-diseno-modular.md)
- Volver al [README principal](../README.md)
