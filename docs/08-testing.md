# 08 - Estrategia de Testing

Una estrategia de pruebas profesional organiza las verificaciones en niveles complementarios para maximizar
la detección temprana de defectos y minimizar el costo de mantenimiento. El determinismo riguroso, la
independencia de la infraestructura y el enfoque en el comportamiento observable garantizan suites sostenibles.

---

## 1. Niveles de Prueba: Pirámide y Trofeo de Testing

La distribución equilibrada del esfuerzo previene suites lentas y frágiles. La **Pirámide de Pruebas**
organiza tres niveles: **Unitarias** (base rápida en memoria que valida lógica e invariantes sin I/O),
**Integración** (intermedia para colaboración entre módulos, persistencia y contratos) y **End-to-End**
(cúspide para validar flujos de usuario sobre infraestructura real). El **Trofeo de Pruebas** prioriza
la integración con dependencias en memoria, respaldada por pruebas unitarias y un mínimo de E2E:
la unidad prueba algoritmos; la integración, contratos; y E2E, viabilidad operativa.

---

## 2. Propiedades F.I.R.S.T. y Estructura de Casos de Prueba

Las pruebas eficaces satisfacen los atributos **F.I.R.S.T.**: **Fast** (milisegundos), **Independent** (aisladas),
**Repeatable** (deterministas), **Self-validating** (retorno binario) y **Timely** (escritas justo antes del
código de producción que las hace pasar; variantes posteriores mencionan *Thorough* como deseable).
Cada prueba se organiza en tres fases: **Arrange** (organizar datos), **Act** (ejecutar operación) y **Assert**
(comprobar resultado observable). Se valida un solo comportamiento bajo `test_<behavior>_when_<condition>`
(ejemplo: `test_returns_discounted_total_when_customer_is_vip`).

---

## 3. Dobles de Prueba: Clasificación y Uso Proporcional

Los dobles de prueba reemplazan colaboradores reales: **Dummy** (objeto de relleno para completar firmas sin
ser utilizado), **Stub** (provee respuestas prefijadas ante consultas), **Fake** (implementación liviana pero
funcional en memoria), **Spy** (registra llamadas e inspecciona parámetros de forma pasiva) y **Mock** (objeto
con expectativas de invocación verificadas al final).

Se prefieren Fakes sobre Mocks para puertos propios del dominio (ver
[03 - Arquitectura y Dirección de Dependencias](03-arquitectura.md)). Queda prohibido simular librerías
ajenas (*Do not mock what you do not own*); se encapsulan tras puertos propios con un fake para pruebas.

---

## 4. Probar Comportamiento y No Implementación

Las pruebas deben verificar contratos públicos y resultados observables, no la implementación: prohibido
realizar aserciones sobre cadenas del código fuente o AST, acceder a métodos o atributos privados protegidos
por convención (`_internal_state`), o verificar el orden de llamadas internas salvo que sea el contrato formal.

### Antes y Después: Comportamiento Observable vs Detalles Internos

#### Antes: Test Acoplado a Detalles de Implementación Internos

```python
from unittest.mock import Mock


def send_welcome(mailer: Mock, recipient: str) -> None:
    mailer._connect()
    mailer._send(recipient, "Welcome")


def test_send_welcome_calls_internal_smtp_methods() -> None:
    mailer = Mock()
    send_welcome(mailer=mailer, recipient="user@example.com")
    mailer._connect.assert_called_once()
```

#### Después: Test Orientado a Comportamiento y Estado Observable

```python
from typing import Protocol


class NotificationSender(Protocol):
    def send(self, recipient: str, body: str) -> None: ...


class FakeNotificationSender:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    def send(self, recipient: str, body: str) -> None:
        self.messages.append((recipient, body))


def send_welcome(sender: NotificationSender, recipient: str) -> None:
    sender.send(recipient, "Welcome")


def test_send_welcome_delivers_message() -> None:
    sender = FakeNotificationSender()
    send_welcome(sender=sender, recipient="user@example.com")
    assert sender.messages == [("user@example.com", "Welcome")]
```

---

## 5. Determinismo: Tiempo, Aleatoriedad y Aislamiento de I/O

Las pruebas automatizadas deben ser estrictamente deterministas y herméticas: **cero retardos fijos**
(prohibido usar `time.sleep()`), **inyección de tiempo y aleatoriedad** (el reloj y generadores se inyectan
como parámetros o dependencias) y **ejecución hermética** (sin red externa, aislando la persistencia en
directorios temporales).

### Antes y Después: Determinismo Temporal

#### Antes: Test Dependiente de Temporización Real y Reloj del Sistema

```python
import time


def is_session_expired(creation: float, duration: float) -> bool:
    return (time.time() - creation) >= duration


def test_session_expires_after_duration() -> None:
    creation_time = time.time()
    time.sleep(0.05)
    assert is_session_expired(creation=creation_time, duration=0.01) is True
```

#### Después: Test Determinista con Inyección de Reloj Controlado

```python
def is_session_expired(creation: float, duration: float, current: float) -> bool:
    return (current - creation) >= duration


def test_session_expires_deterministically() -> None:
    assert is_session_expired(creation=100.0, duration=10.0, current=110.0) is True
```

---

## 6. Cobertura de Código y Pruebas de Mutación

La cobertura de líneas mide código transitado, no correctitud: el 100% con aserciones superficiales
genera falsa seguridad. Las pruebas de mutación con `mutmut` evalúan la suite introduciendo fallas
sintácticas: mutantes eliminados (*killed*) validan las pruebas; mutantes sobrevivientes (*survived*)
delatan aserciones ineficaces.

---

## 7. Patrones Prácticos con Pytest

El ecosistema de Pytest permite verificar unidades de negocio mediante fixtures inyectadas, parametrización
y aislamiento hermético de archivos temporales con `tmp_path`:

```python
from pathlib import Path
import pytest

PENDING_STATUS = "PENDING"
PROCESSING_STATUS = "PROCESSING"
SHIPPED_STATUS = "SHIPPED"
CANCELLED_STATUS = "CANCELLED"


class InMemoryOrderRepository:
    def __init__(self) -> None:
        self.records: dict[str, str] = {}

    def get(self, order_id: str) -> str | None:
        return self.records.get(order_id)

    def save(self, order_id: str, status: str) -> None:
        self.records[order_id] = status


def cancel_order(repository: InMemoryOrderRepository, order_id: str) -> str:
    if repository.get(order_id) == SHIPPED_STATUS:
        raise ValueError(f"Cannot cancel shipped order: {order_id}")
    repository.save(order_id, CANCELLED_STATUS)
    return CANCELLED_STATUS


def write_audit_entry(directory: Path, entry: str) -> Path:
    path = directory / "audit.log"
    path.write_text(f"{entry}\n", encoding="utf-8")
    return path


@pytest.fixture
def order_repository() -> InMemoryOrderRepository:
    repository = InMemoryOrderRepository()
    for order_id, status in [("order-1", PENDING_STATUS), ("order-2", PROCESSING_STATUS), ("order-3", SHIPPED_STATUS)]:
        repository.save(order_id, status)
    return repository


@pytest.mark.parametrize("order_id", ["order-1", "order-2"])
def test_cancels_order_when_status_is_cancellable(
    order_repository: InMemoryOrderRepository, order_id: str
) -> None:
    assert cancel_order(order_repository, order_id) == CANCELLED_STATUS
    assert order_repository.get(order_id) == CANCELLED_STATUS


def test_rejects_cancellation_when_order_is_shipped(
    order_repository: InMemoryOrderRepository,
) -> None:
    with pytest.raises(ValueError, match="Cannot cancel shipped"):
        cancel_order(order_repository, "order-3")
    assert order_repository.get("order-3") == SHIPPED_STATUS


def test_writes_entry_when_log_directory_is_empty(tmp_path: Path) -> None:
    log_file = write_audit_entry(tmp_path, "order-1:CANCELLED")
    assert log_file.read_text(encoding="utf-8") == "order-1:CANCELLED\n"
```

---

## 8. Señales de Alerta

- **Pruebas intermitentes (*flaky tests*)**: Fallos esporádicos causados por reloj o red.
- **Llamadas a `sleep`**: Evidencia de carencia de sincronización determinista.
- **Mocks de librerías externas**: Síntoma de ausencia de puertos propios del dominio.
- **Fases Arrange desmedidas**: Acoplamiento excesivo de dependencias.
- **Aserciones sobre métodos privados**: Acoplan las pruebas a la estructura interna.

---

## 9. Checklist de Verificación

- [ ] La suite prioriza pruebas unitarias rápidas e integración sobre contratos.
- [ ] Cada caso de prueba sigue Arrange-Act-Assert evaluando un único comportamiento.
- [ ] Los nombres de prueba describen comportamiento y condición (`test_<behavior>_when_<condition>`).
- [ ] Se prefieren Fakes en memoria sobre Mocks para puertos propios del dominio.
- [ ] Las dependencias externas se aíslan tras puertos propios sin falsear librerías de terceros.
- [ ] No existen retardos fijos (`sleep`); el tiempo y factores volátiles se inyectan.
- [ ] Las pruebas de disco utilizan carpetas temporales aisladas (`tmp_path`).

---

## Navegación

- Anterior: [07 - Desarrollo Guiado por Pruebas (TDD)](07-tdd.md)
- Siguiente: [09 - Manejo de Errores](09-errores.md)
- Volver al [README principal](../README.md)
