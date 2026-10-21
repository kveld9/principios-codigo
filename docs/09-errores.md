# 09 - Manejo de Errores

El manejo de errores determina la fiabilidad, predictibilidad y capacidad de diagnóstico de un sistema. La
contención temprana de anomalías y la propagación explícita de excepciones previenen estados corruptos
silenciosos y reducen drásticamente el tiempo medio de resolución de incidentes en entornos de producción.

---

## 1. Filosofía Fail-Loud y Detección Temprana

El principio fundamental ante fallos inesperados es fallar de inmediato y de forma ruidosa (*fail-loud*). Un error
silenciado o postergado permite que el flujo de ejecución continúe con datos corruptos, provocando fallos en cascada
lejos del origen real y haciendo que el diagnóstico forense sea costoso o inviable.

1. **Prohibición de enmascarar errores**: Ningún bloque de código debe silenciar excepciones de forma indiscriminada.
   Quedan prohibidos los bloques de captura vacíos (`except Exception: pass`), el silenciamiento en scripts mediante
   `|| true` o redirecciones a `/dev/null`, la omisión deliberada de errores (como `_ = err`) y el retorno silencioso
   de `None` o `False` ante fallas catastróficas que ocultan defectos de programación y corrompen el flujo.
2. **Fallo inmediato ante violaciones de invariantes**: Si el sistema detecta un estado inconsistente o una violación
   de contrato en una frontera interna, debe interrumpir la ejecución sin intentar adivinar la intención del usuario.
3. **Contexto diagnóstico suficiente**: Identificar con precisión qué operación falló, qué entrada o estado la provocó
   (sin exponer credenciales ni secretos) y cuál fue la causa raíz detectable o excepción subyacente.

---

## 2. Validación en Frontera: Analizar en Lugar de Validar

Las fronteras del sistema (controladores HTTP, comandos CLI, interfaces de base de datos o clientes de API externa)
constituyen los únicos puntos donde los datos de entrada carecen de garantía estructural.

El principio *Parse, don't validate* establece que los datos crudos no deben atravesar las capas internas
acompañados de validaciones booleanas dispersas. En su lugar, los datos crudos se analizan y transforman una única vez
en la frontera hacia entidades o modelos de dominio inmutables y fuertemente tipados. Una vez que una estructura
traspasa la frontera, el núcleo del dominio asume que sus invariantes son válidos por construcción, eliminando
comprobaciones defensivas duplicadas en capas profundas.

### Antes y Después: Modelado en Frontera vs Validación Defensiva

#### Antes: Validación Defensiva Repetitiva sobre Diccionarios Crudos

```python
# Unstructured dictionary passed across layers with repetitive defensive checks
from decimal import Decimal

MINIMUM_MEMBER_AGE: int = 18
SENIOR_AGE_THRESHOLD: int = 65
STANDARD_FEE: Decimal = Decimal("100.00")
DISCOUNTED_FEE: Decimal = Decimal("50.00")


def calculate_membership_fee(raw_payload: dict[str, object]) -> Decimal:
    raw_age = raw_payload.get("age")
    if not isinstance(raw_age, int) or raw_age < MINIMUM_MEMBER_AGE:
        raise ValueError("Invalid member age")

    raw_status = raw_payload.get("status")
    if raw_status not in {"active", "suspended"}:
        raise ValueError("Invalid member status")

    if raw_age >= SENIOR_AGE_THRESHOLD and raw_status == "active":
        return DISCOUNTED_FEE
    return STANDARD_FEE
```

#### Después: Análisis en Frontera hacia Modelos Tipados Inmutables

```python
# Immutable typed model parsed once at boundary; domain trusts invariants
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

MINIMUM_MEMBER_AGE: int = 18
SENIOR_AGE_THRESHOLD: int = 65
STANDARD_FEE: Decimal = Decimal("100.00")
DISCOUNTED_FEE: Decimal = Decimal("50.00")


class MemberStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"


class MemberParsingError(ValueError):
    """Raised when boundary payload cannot be parsed into a MemberProfile."""


@dataclass(frozen=True)
class MemberProfile:
    age: int
    status: MemberStatus


def parse_member_profile(raw_payload: dict[str, object]) -> MemberProfile:
    age = raw_payload.get("age")
    if isinstance(age, bool) or not isinstance(age, int) or age < MINIMUM_MEMBER_AGE:
        raise MemberParsingError(f"Age must be an integer >= {MINIMUM_MEMBER_AGE}, got: {age}")
    raw_status = raw_payload.get("status")
    try:
        status = MemberStatus(raw_status)
    except ValueError as error:
        raise MemberParsingError(f"Invalid member status: {raw_status}") from error
    return MemberProfile(age=age, status=status)


def calculate_membership_fee(member: MemberProfile) -> Decimal:
    if member.age >= SENIOR_AGE_THRESHOLD and member.status == MemberStatus.ACTIVE:
        return DISCOUNTED_FEE
    return STANDARD_FEE
```

Ejemplo ejecutable: [examples/parse_dont_validate/](../examples/parse_dont_validate/)

---

## 3. Captura Precisa, Encadenamiento y Jerarquía de Excepciones

La captura de excepciones debe ser deliberada, granular y contextual. Capturar excepciones genéricas desactiva las
garantías del lenguaje y enmascara errores tipográficos (`AttributeError`), claves ausentes (`KeyError`) o defectos
en tipos (`TypeError`).

1. **Capturar exclusivamente lo recuperable**: Se debe interceptar únicamente la excepción específica que la rutina
   sabe mitigar o traducir. Si una función no puede resolver la condición de error, debe permitir que se propague.
2. **Encadenamiento con `raise ... from error`**: Al traducir una excepción de bajo nivel o de infraestructura a una
   excepción de dominio, es obligatorio preservar la excepción causal mediante `from error`. Esto conserva el
   atributo `__cause__` y el rastreo de pila (*traceback*) original completo.
3. **Jerarquía de dominio compacta y significativa**: Mantener una estructura jerárquica superficial. Una clase base
   de dominio derivada de `Exception` o `ValueError`, junto con subclases específicas únicamente cuando los llamadores
   requieran ejecutar ramas lógicas diferenciadas ante cada tipo de fallo.

### Antes y Después: Preservación de Causa Raíz

#### Antes: Silenciamiento Indiscriminado y Pérdida de Causa Raíz

```python
# Swallowing exceptions with broad catch and losing diagnostic stack trace
from decimal import Decimal, InvalidOperation


def parse_transaction_amount(raw_amount: str) -> Decimal | None:
    try:
        return Decimal(raw_amount)
    except Exception:
        # Loses InvalidOperation root cause and original input context
        return None
```

#### Después: Captura Específica y Encadenamiento con Causa Preservada

```python
# Catching specific exception and chaining root cause into domain exception
from decimal import Decimal, InvalidOperation


class InvalidTransactionAmountError(ValueError):
    """Domain exception raised when transaction amount is invalid."""


def parse_transaction_amount(raw_amount: str) -> Decimal:
    try:
        amount = Decimal(raw_amount)
    except InvalidOperation as error:
        raise InvalidTransactionAmountError(
            f"Failed to parse transaction amount {raw_amount!r}: {error}"
        ) from error

    if amount <= Decimal("0.00"):
        raise InvalidTransactionAmountError(
            f"Amount must be strictly positive, got: {amount}"
        )
    return amount
```

La versión refactorizada incorpora además la regla de dominio que rechaza importes no positivos, arrojando
directamente la excepción específica en lugar de admitir montos monetarios inválidos.

---

## 4. Fallos Esperados frente a Defectos de Invariante

El diseño distingue entre dos naturalezas dispares de error:

1. **Fallos esperados de negocio**: Situaciones previstas por las reglas de la aplicación (por ejemplo, saldo
   insuficiente para una extracción o credenciales inválidas). Deben modelarse mediante excepciones de dominio tipadas
   o tipos de resultado explícitos (`Result[Value, Error]`).
2. **Defectos de invariante (Bugs)**: Supuestos que jamás deberían incumplirse en una ejecución correcta (como un
   atributo obligatorio en None tras la inicialización interna). Los enunciados `assert` se eliminan bajo `python -O`,
   por lo que los invariantes críticos en producción requieren un `raise RuntimeError(...)` explícito (o una excepción
   de dominio específica); `assert` queda reservado para depuración y aserciones en pruebas automatizadas.

---

## 5. Gestión Segura de Recursos y Reintentos Acotados

Toda adquisición de recursos volátiles del sistema operativo (descriptores de archivos, sockets de red, conexiones a
bases de datos o bloqueos concurrentes) debe garantizar su liberación incondicional.

1. **Administradores de contexto**: Emplear siempre la sentencia `with` (en Python) o estructuras `try-finally` para
   asegurar que la limpieza ocurra tanto en trayectorias exitosas como ante excepciones no controladas.
2. **Reintentos restringidos a fallos transitorios**: Los reintentos automáticos solo son válidos ante fallos de
   naturaleza efímera (como caídas intermitentes de red o respuestas HTTP 503). Errores deterministas (como 400 Bad
   Request o 401 Unauthorized) deben fallar inmediatamente.
3. **Retroceso exponencial acotado (*Bounded Exponential Backoff*)**: Limitar estrictamente los reintentos
   (por ejemplo, tres) e incorporar retardos crecientes con variación aleatoria (*jitter*).
4. **Idempotencia obligatoria**: Jamás se debe reintentar una operación que mute estado a menos que disponga de una
   clave de idempotencia verificada en el receptor.

---

## 6. Registro de Errores en la Frontera (Logging)

El registro en bitácoras (*logging*) proporciona la visibilidad operativa del comportamiento del sistema. Su aplicación
debe seguir principios de contención para no saturar las plataformas de observabilidad.

1. **Registrar una sola vez en la frontera**: El error debe registrarse en el componente que lo absorbe o lo traduce
   hacia el cliente (controlador web, comando CLI o despachador de eventos). Registrar un error en un nivel intermedio
   y volver a lanzarlo (*log and rethrow*) provoca duplicación de trazas para un único incidente.
2. **Estructura semántica**: Emitir registros estructurados con campos clave (identificador de correlación, código de
   operación y duración), facilitando la agregación y consulta automatizada.
3. **Aislamiento de secretos y datos sensibles**: Queda estrictamente prohibido emitir contraseñas, tokens de acceso,
   claves criptográficas o información de identificación personal (PII) en los mensajes o parámetros de log.

---

## 7. Señales de Alerta

- Bloques `except Exception: pass` o ausencia de `from error` al traducir excepciones de infraestructura.
- Funciones del dominio interno repitiendo validaciones defensivas sobre tipos recibidos de otras capas.
- Funciones intermedias que capturan una excepción, emiten un registro en log y vuelven a lanzar la misma excepción.
- Mecanismos de reintento infinito o aplicados a operaciones de mutación sin garantía de idempotencia.
- Retorno de tuplas de estado ambiguas (`(None, False)`) para comunicar excepciones técnicas de bajo nivel.

---

## 8. Checklist de Verificación

- [ ] Las entradas externas se analizan en tipos inmutables en la frontera; el dominio interno confía en ellos.
- [ ] Se prohíbe silenciar excepciones (`pass`) y solo se capturan las fallas específicas recuperables.
- [ ] La traducción de excepciones preserva el rastreo de causa raíz mediante `raise ... from error`.
- [ ] La liberación de recursos está garantizada mediante administradores de contexto (`with`) o `try-finally`.
- [ ] Los reintentos se restringen a fallos transitorios con retroceso exponencial acotado e idempotencia estricta.
- [ ] El registro en log ocurre exactamente una vez en la frontera que gestiona la falla, sin datos confidenciales.

---

## Navegación

- Anterior: [08 - Estrategia de Testing](08-testing.md)
- Siguiente: [10 - Anti-Hardcoding y Fuente Única de Verdad](10-hardcoding.md)
- Volver al [README principal](../README.md)
