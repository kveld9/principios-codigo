# 02 - Diseño Modular y Eliminación de Monolitos

La modularización es la disciplina de descomponer un sistema de software en componentes cohesivos, autónomos y
débilmente acoplados. Su objetivo radica en establecer límites nítidos de responsabilidad que permitan aislar cambios,
garantizar la verificación independiente y erradicar la degradación del código hacia arquitecturas monolíticas.

---

## 1. Principio de Responsabilidad y Fronteras Modulares

Un módulo es una unidad lógica de empaquetado (directorio, paquete o biblioteca) bajo una frontera explícita.

1. **Alta cohesión interna**: Los componentes colaboran para resolver un único subproblema del dominio.
2. **Bajo acoplamiento externo**: Interacción mediante interfaces mínimas sin conocer detalles internos ajenos.
3. **Una sola razón para cambiar**: Si un módulo acumula cambios por causas dispares, existe acoplamiento espurio.
4. **Fronteras sobre recuento de archivos**: La modularidad se define por límites nítidos, evitando nano-módulos
   y capas intermedias anémicas (*wrappers*) que no aporten aislamiento.

---

## 2. Superficie Pública y Contratos Explícitos

Los módulos interactúan mediante contratos estables y tipados, ocultando detalles internos de almacenamiento.

1. **Superficie pública mínima**: Exponer únicamente los tipos y firmas estrictamente requeridos por consumidores.
2. **Invariancia del contrato**: Depender de contratos estables, nunca de esquemas de persistencia ni estados mutables.
3. **Evolución sin ruptura**: Reestructurar el interior preservando contratos públicos no debe afectar a terceros.

### Antes y Después: Encapsulamiento y Contratos Explícitos

#### Antes: Acoplamiento a Estructuras Internas

```python
# Direct external access to raw mutable dictionary breaks encapsulation
class OrderRegistry:
    def __init__(self) -> None:
        self.orders: dict[str, dict[str, float]] = {}


registry = OrderRegistry()
registry.orders["ord-99"] = {"amount": 42.0, "status": 1.0}
```

#### Después: Contrato Público con Encapsulamiento

```python
# Minimal public interface hiding storage and preserving state invariants
from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    order_id: str
    amount: float


class OrderRegistry:
    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}

    def register(self, order: Order) -> None:
        if order.order_id in self._orders:
            raise KeyError(f"Order {order.order_id!r} already registered")
        self._orders[order.order_id] = order

    def get(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)
```

---

## 3. Dependencias Unidireccionales y Prevención de Ciclos

El grafo de dependencias entre módulos debe constituir un **Grafo Acíclico Dirigido (DAG)**.

```text
CORRECTO (DAG): [Entrega] ──► [Aplicación] ──► [Dominio]
INCORRECTO (Ciclo): [Módulo A] ──► [Módulo B] ──► [Módulo C] ──► [Módulo A]
```

1. **Flujo unidireccional**: Las dependencias apuntan en un único sentido sin referencias circulares.
2. **Impacto de ciclos**: Bloquean la verificación aislada, impiden el reuso e inducen bloqueos de inicialización.
3. **Técnicas de resolución**: Inversión de dependencias mediante abstracciones o extracción de tipos a un módulo base.

---

## 4. Política de Cero Monolitos y Procedimiento Seguro de División

Un monolito representa una concentración desmedida de responsabilidades en una sola unidad de ejecución.

### Niveles de Monolito y Umbrales Cuantitativos

Umbrales por defecto (los linters configurados en el proyecto tienen prioridad):

| Nivel | Definición de Monolito | Señal Cuantitativa por Defecto |
| :--- | :--- | :--- |
| **Función** | Mezcla de orquestación, validación, I/O y mutaciones. | > 40 líneas de código o CC > 5. |
| **Clase** (*God Class*) | Concentración de atributos y métodos de múltiples conceptos. | > 300 líneas de código o > 10 métodos públicos. |
| **Archivo** (*God File*) | Agrupación de lógicas heterogéneas sin cohesión temática. | > 400 líneas de código. |
| **Módulo** | Paquete importado masivamente sin frontera delimitada. | > 7-10 archivos densos o dependencia global sin contrato. |

### Señales Técnicas para Dividir un Archivo

Más allá de las líneas de código, un archivo debe dividirse de inmediato ante cualquiera de estos síntomas:

1. **Imposibilidad de resumir su rol en una frase concisa**: Si la descripción requiere conjunciones copulativas.
2. **Mezcla de niveles de abstracción**: Combina orquestación de alto nivel con lógica de bajo nivel (sockets, I/O).
3. **Conflictos de merge recurrentes**: Múltiples desarrolladores colisionan con tareas funcionales no relacionadas.
4. **Importaciones excesivas y dispares**: Acumula decenas de dependencias de dominios heterogéneos.

### Procedimiento Seguro de Descomposición

1. **Pruebas de caracterización**: Capturar el comportamiento observable actual antes de efectuar modificaciones.
2. **Extracción por responsabilidad**: Extraer bloques lógicos a funciones auxiliares en el mismo archivo.
3. **Mover a nuevo módulo**: Trasladar la estructura a un nuevo archivo con contratos tipados y límites definidos.
4. **Reexportación temporal**: Exponer temporalmente los símbolos desde el archivo original para compatibilidad.
5. **Retiro de reexportación**: Migrar importaciones en consumidores y eliminar los alias temporales del archivo.

### Antes y Después: Descomposición de Monolito

#### Antes: Función Monolítica con Múltiples Responsabilidades

```python
# God function: parses payload, connects to database, and sends notification
def process_user_signup(data: dict[str, str], db_cursor: object) -> None:
    email = data.get("email", "").strip().lower()
    if "@" not in email:
        raise ValueError("Invalid email format")

    db_cursor.execute("INSERT INTO users VALUES (?, ?)", (email, data["password"]))  # type: ignore[attr-defined]

    import smtplib
    server = smtplib.SMTP("smtp.internal", 25)
    server.sendmail("noreply@internal", email, "Account created")
    server.quit()
```

#### Después: Componentes Cohesivos y Caso de Uso Orquestador

```python
# Cohesive domain model, protocols, and orchestrating use case
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class UserCredentials:
    email: str
    password_hash: str

    @classmethod
    def create(cls, raw_email: str, password_hash: str) -> "UserCredentials":
        email = raw_email.strip().lower()
        if "@" not in email:
            raise ValueError(f"Invalid email format: {raw_email}")
        return cls(email=email, password_hash=password_hash)


class UserRepository(Protocol):
    def save(self, credentials: UserCredentials) -> None: ...


class UserNotifier(Protocol):
    def send_welcome(self, email: str) -> None: ...


def register_user(
    raw_email: str, pwd_hash: str, repo: UserRepository, notifier: UserNotifier
) -> UserCredentials:
    user = UserCredentials.create(raw_email, pwd_hash)
    repo.save(user)
    notifier.send_welcome(user.email)
    return user
```

---

## 5. Organización del Proyecto: Por Feature vs Por Capa

La disposición física de directorios debe reflejar las fronteras de dominio.

### Comparativa de Modelos

| Modelo | Definición | Contexto Adecuado | Riesgo a Escala |
| :--- | :--- | :--- | :--- |
| **Package by Layer** | Agrupación por rol técnico (`controllers/`, `services/`, `models/`). | Proyectos pequeños (< 15 archivos). | Dispersa funcionalidades en múltiples directorios distantes. |
| **Package by Feature** | Agrupación por caso de uso o subdominio (`auth/`, `billing/`). | Sistemas medianos, grandes y en evolución. | Requiere delimitación previa de los contextos de dominio. |

### Ejemplos de Estructura de Directorios

#### Escala Pequeña / Mediana (Por Feature)

```text
src/
├── auth/
│   ├── api.py           # Endpoints de autenticación
│   ├── service.py       # Lógica y credenciales
│   └── repository.py    # Persistencia
├── billing/
│   ├── api.py           # Endpoints de facturación
│   └── service.py       # Procesamiento de pagos
└── shared/
    ├── config.py        # Configuración
    └── database.py      # Conexión a base de datos
```

#### Escala Modular Amplia (Fronteras Explícitas)

```text
modules/
├── identity/
│   ├── public/          # Contratos exportables
│   └── internal/        # Implementación privada
└── billing/
    ├── public/
    └── internal/
```

---

## 6. Anti-patrones de Modularización

1. **El cajón de sastre (`utils/`, `helpers/`, `common/`)**: Carpetas que acumulan algoritmos heterogéneos sin cohesión.
   Todo código auxiliar debe pertenecer a su módulo o a una librería con propósito acotado (`crypto-primitives/`).
2. **Micro-fragmentación prematura**: Dividir archivos breves en submódulos de pocas líneas, generando dispersión.
3. **Fronteras porosas**: Módulos que acceden a atributos privados, variables globales o persistencia ajena.

---

## 7. Checklist de Verificación

Antes de cerrar o integrar una unidad modular, validar los siguientes puntos:

- [ ] Cada módulo responde a una sola razón para cambiar dentro del dominio.
- [ ] La superficie pública del módulo está delimitada y oculta sus estructuras internas.
- [ ] El grafo de dependencias entre módulos es estrictamente acíclico (DAG).
- [ ] No existen funciones (> 40 líneas o CC > 5), clases (> 300 líneas o > 10 métodos), archivos (> 400 líneas) ni
      módulos (> 7-10 archivos densos) que superen los umbrales de monolito.
- [ ] Las divisiones de componentes contaron con pruebas de caracterización previas a la migración.
- [ ] Se evitó la creación de módulos cajón de sastre (`utils/`, `common/`) sin cohesión semántica.

---

## Navegación

- Anterior: [01 - Principios Fundamentales de Código](01-principios.md)
- Siguiente: [03 - Arquitectura y Dirección de Dependencias](03-arquitectura.md)
- Volver al [README principal](../README.md)
