# 11 - Inyección y Gestión de Dependencias

La inyección y gestión rigurosa de dependencias garantiza que los componentes del sistema permanezcan desacoplados,
verificables mediante pruebas unitarias y aislados de cambios volátiles en librerías externas o infraestructura.
Este documento establece las reglas para la provisión de colaboradores, contratos propios frente a dependencias de
terceros y directrices de gobernanza de paquetes en el repositorio.

---

## 1. Inversión de Control e Inyección de Dependencias

Un módulo o clase de dominio nunca debe instanciar directamente sus dependencias de infraestructura ni acceder a
variables globales o localizadores de servicios (*Service Locators*).

1. **Inyección por constructor como estándar**: Las clases deben declarar todos sus colaboradores obligatorios en el
   método `__init__`. Esto hace explícito el grafo de dependencias y facilita la provisión de dobles en pruebas.
2. **Inyección por parámetros en funciones puras**: Las funciones deben recibir sus entradas y utilidades como
   argumentos formales, evitando lecturas directas del entorno o estado mutable global.
3. **Valores por defecto convenientes sin ocultar la costura**: Se admiten argumentos con valores predeterminados
   únicamente si representan variantes seguras en memoria o configuraciones neutras, sin ocultar dependencias con
   I/O ni suprimir la posibilidad de sustitución.
4. **Prohibición de Singletons y Service Locators**: El acceso a colaboradores mediante llamadas globales oculta
   el acoplamiento, dificulta el paralelismo en suites de pruebas y propaga estado compartido no determinista.

### Antes y Después: Inyección por Constructor frente a Instanciación Oculta

#### Antes: Servicio con Instanciación Rígida y Dependencia Oculta

```python
# Direct instantiation couples the service to a concrete database implementation
from decimal import Decimal


class SqliteOrderRepository:
    def save_order(self, order_id: str, amount: Decimal) -> None:
        pass


class OrderService:
    def __init__(self) -> None:
        self.repository = SqliteOrderRepository()

    def register_order(self, order_id: str, amount: Decimal) -> None:
        if amount <= Decimal("0"):
            raise ValueError(f"Order amount must be positive, got: {amount}")
        self.repository.save_order(order_id, amount)
```

#### Después: Inyección de Dependencia mediante Contrato Protocol

```python
# Explicit constructor injection enables deterministic unit testing with test doubles
from decimal import Decimal
from typing import Protocol


class OrderRepository(Protocol):
    def save_order(self, order_id: str, amount: Decimal) -> None:
        ...


class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def register_order(self, order_id: str, amount: Decimal) -> None:
        if amount <= Decimal("0"):
            raise ValueError(f"Order amount must be positive, got: {amount}")
        self._repository.save_order(order_id, amount)
```

---

## 2. Composición en la Raíz (Composition Root)

El ensamblado del grafo de objetos debe ocurrir exclusivamente en el punto de entrada de la aplicación, denominado
*Composition Root* (ver [03 - Arquitectura y Dirección de Dependencias](03-arquitectura.md)).

- **Fábricas y configuradores centralizados**: La creación de adaptadores concretos (persistencia, clientes de red,
  variables de entorno) se ubica en funciones de arranque o módulos de composición dedicados.
- **Lógica de negocio agnóstica**: Los servicios de dominio reciben instancias ya configuradas, sin participar en
  decisiones sobre cómo se construyeron ni de qué variables del sistema operativo provienen sus parámetros.

Ejemplo ejecutable: [examples/ports_adapters/](../examples/ports_adapters/)

---

## 3. Aislamiento de Librerías de Terceros mediante Puertos

Las dependencias externas son detalles volátiles que escapan al control del proyecto. Una actualización mayor, un
cambio de API o el abandono de una librería no deben forzar la reescritura de la lógica de negocio.

1. **Definición de puertos propios**: La aplicación define contratos abstractos (`typing.Protocol` o interfaces)
   que modelan las operaciones requeridas desde la perspectiva del dominio.
2. **Adaptadores delgados**: Se implementa un adaptador específico que traduce el contrato del dominio hacia las
   llamadas concretas del paquete externo.
3. **Contención de tipos y excepciones**: Las excepciones propietarias de la librería externa deben capturarse
   dentro del adaptador y traducirse a excepciones del dominio (ver [09 - Manejo de Errores](09-errores.md)).

### Antes y Después: Envoltorio de Librería Externa tras Puerto Propio

#### Antes: Llamada Directa a SDK Externo en Lógica de Dominio

```python
# Direct usage of a third-party SDK leaks foreign signatures and errors into domain
from decimal import Decimal


class ExternalSmsError(Exception):
    pass


class ExternalSmsClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def send_sms_payload(self, payload: dict[str, str]) -> None:
        pass


class PaymentNotifier:
    def __init__(self, api_key: str) -> None:
        self._client = ExternalSmsClient(api_key=api_key)

    def notify_payment(self, phone_number: str, amount: Decimal) -> None:
        self._client.send_sms_payload({"recipient": phone_number, "body": f"Paid: {amount}"})
```

#### Después: Adaptador Dedicado Implementando Puerto del Dominio

```python
# Domain port and adapter isolate business logic and translate vendor exceptions
from decimal import Decimal
from typing import Protocol


class NotificationDeliveryError(Exception):
    pass


class ExternalSmsError(Exception):
    pass


class NotificationPort(Protocol):
    def send_notification(self, recipient: str, message: str) -> None:
        ...


class ExternalSmsClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def send_sms_payload(self, payload: dict[str, str]) -> None:
        pass


class SmsNotificationAdapter:
    def __init__(self, client: ExternalSmsClient) -> None:
        self._client = client

    def send_notification(self, recipient: str, message: str) -> None:
        try:
            self._client.send_sms_payload({"recipient": recipient, "body": message})
        except ExternalSmsError as error:
            raise NotificationDeliveryError(
                f"Failed to deliver notification to {recipient}"
            ) from error


class PaymentNotifier:
    def __init__(self, notifier: NotificationPort) -> None:
        self._notifier = notifier

    def notify_payment(self, phone_number: str, amount: Decimal) -> None:
        self._notifier.send_notification(phone_number, f"Paid: {amount}")
```

---

## 4. Criterios de Selección y Adopción de Dependencias

Antes de evaluar un paquete externo, debe comprobarse si la biblioteca estándar resuelve el problema de forma concisa.
En Python moderno, módulos como `pathlib`, `dataclasses`, `typing`, `json`, `sqlite3` y `urllib.request` cubren
necesidades habituales sin agregar pasivos técnicos externos ni riesgos de cadena de suministro.

Toda librería candidata debe evaluarse contra cuatro criterios:

1. **Mantenimiento activo**: Registro de versiones periódicas, respuesta oportuna a reportes de defectos y
   actividad sostenida de la comunidad mantenedora.
2. **Licencia compatible**: Licencia explícita y admisible para el proyecto (MIT, Apache 2.0, BSD) sin restricciones
   víricas no deseadas.
3. **Árbol de dependencias transitivas**: Preferir paquetes autónomos con mínimas dependencias secundarias para evitar
   bloqueos de resolución y riesgos colaterales.
4. **Registro de seguridad**: Historial de vulnerabilidades conocidas (CVEs) y velocidad de remediación ante incidentes.

---

## 5. Fijación de Versiones y Gobernanza en CI

La reproducibilidad de las compilaciones exige control estricto de las versiones instaladas en desarrollo y producción.

1. **Fijación estricta de versiones**: Las aplicaciones y servicios desplegables deben versionar un archivo de bloqueo
   (*lockfile*) como `uv.lock`, `poetry.lock` o `package-lock.json`. Los proyectos de utilitarios, librerías o kits de
   herramientas pueden alternativamente fijar versiones exactas (`==`) en su propio manifiesto (`pyproject.toml`).
   Queda estrictamente prohibido el uso de especificadores flotantes o de rango (`>=`, `~=`) en entornos de CI y
   despliegue.
2. **Actualizaciones automatizadas**: Emplear herramientas como Dependabot o Renovate para auditar vulnerabilidades
   y proponer actualizaciones periódicas en lotes (ver lineamientos de CI en el
   [Kit principios-git](https://github.com/kveld9/principios-git)).
3. **Depuración de dependencias obsoletas**: Ejecutar análisis periódicos con herramientas de detección de dependencias
   inactivas o no utilizadas, eliminando paquetes huérfanos del manifiesto del proyecto.

---

## 6. Señales de Alerta

- Clases que instancian adaptadores de persistencia, red o almacenamiento directamente en sus constructores.
- Invocaciones a métodos estáticos de servicios o variables globales para acceder a recursos de infraestructura.
- Tipos de datos o excepciones pertenecientes a librerías de terceros presentes en firmas de entidades de dominio.
- Dependencias añadidas al proyecto para resolver tareas realizables con menos de diez líneas de biblioteca estándar.
- Instalación de paquetes con rangos flotantes (`>=`) sin archivo de bloqueo ni fijación exacta en el manifiesto.
- Manifiestos con dependencias sin uso activo en el código fuente.

---

## 7. Checklist de Verificación

- [ ] Todas las dependencias de colaboradores se reciben explícitamente vía constructor o parámetros de función.
- [ ] La lógica de negocio está libre de llamadas directas a singletons o localizadores de servicios globales.
- [ ] La instanciación y conexión de dependencias se concentra en el Composition Root de la aplicación.
- [ ] Las librerías externas volátiles están encapsuladas tras puertos y adaptadores definidos por el dominio.
- [ ] Se priorizó la biblioteca estándar antes de incorporar nuevos paquetes externos al proyecto.
- [ ] Cada paquete externo cumple con los criterios de mantenimiento activo, licencia y seguridad.
- [ ] Las versiones están estrictamente fijadas mediante archivo de bloqueo (*lockfile*) o fijación exacta (`==`).
- [ ] No existen dependencias huérfanas o sin utilizar registradas en el manifiesto de configuración.

---

## Navegación

- Anterior: [10 - Anti-Hardcoding y Fuente Única de Verdad](10-hardcoding.md)
- Siguiente: [12 - Code Smells y Refactorización Segura](12-refactorizacion.md)
- Volver al [README principal](../README.md)
