# 14 - Máquinas de Estado Explícitas

El modelado de ciclos de vida y fases operativas mediante variables booleanas sueltas, centinelas nulos o cadenas
literales sin tipar constituye el antipatrón de máquinas de estado implícitas. Este diseño dispersa la lógica de
transición, permite combinaciones de estado ilegales y provoca condiciones de carrera críticas. La ingeniería
robusta exige modelar todo ciclo de vida como una máquina de estados finitos explícita respaldada por tipos algebraicos.

---

## 1. El Antipatrón: Máquinas de Estado Implícitas

Una máquina de estados implícita surge cuando el ciclo de vida de un componente se distribuye entre múltiples
variables mutables independientes (`is_loading`, `has_error`, `is_cancelled`, `data_buffer: dict | None`).

El riesgo central radica en la explosión de estados representables frente a los estados válidos del dominio:
con $N$ banderas booleanas existen $2^N$ combinaciones en memoria. En un sistema gobernado por 3 booleanos existen
8 combinaciones posibles, aunque solo 3 o 4 tengan sentido operativo. Las combinaciones restantes (como
`is_loading=True` simultáneamente con `has_error=True` y `is_cancelled=True`) son estados ilegales que el sistema
puede alcanzar ante eventos concurrentes, callbacks desordenados o excepciones mal contenidas.

```text
Antipatrón (Implícito):      Estado Válido (Explícito):
┌─────────────────────────┐   ┌──────────────────────────────────────────────┐
│ is_loading: True        │   │                                              │
│ has_error: True         ├──►│  Estado Ilegal: ¿está cargando o falló?      │
│ data_buffer: {'id': 1}  │   │  Los datos pueden ser residuales o parciales.│
└─────────────────────────┘   └──────────────────────────────────────────────┘
```

---

## 2. The Stop Test: Criterio de Parada ante Estado Mutable

Antes de introducir o aprobar variables mutables para coordinar una fase o proceso, es obligatorio aplicar las cuatro
preguntas del *Stop Test*:

1. **¿La fase depende de más de una variable mutable coordinada?** (ej. `is_active` + `is_busy`).
2. **¿Se utiliza un centinela nulo o mágico para denotar ausencia o fallo?** (`None`, `-1`, `0` para "no listo").
3. **¿La fase se compara mediante cadenas de texto crudas?** (`if status == "running"` propenso a erratas).
4. **¿Puede llegar un callback concurrente, reintento o evento desordenado mientras se ejecuta esta fase?**

Si la respuesta a cualquiera de estas preguntas es afirmativa, la fase no está formalmente modelada. No debe enviarse
ni aprobarse código en ese estado.

---

## 3. Las Tres Leyes de las Máquinas de Estado Explícitas

Para erradicar la ambigüedad y blindar el sistema contra corrupciones de estado, toda fase debe satisfacer tres leyes:

### 1. Un Solo Propietario (Single Owner)

El estado completo del ciclo de vida reside en un único contenedor o atributo estructurado. Queda prohibido mantener
estado sombra en variables globales a nivel de módulo, variables de contexto (`ContextVar`), almacenes locales por
hilo (`ThreadLocal`) o diccionarios auxiliares que dupliquen o contradigan el estado principal.

### 2. Función de Transición Única y Total

Toda mutación de estado ocurre exclusivamente mediante una función de transición centralizada:

```text
transition(current_state, event) ──► new_state
```

Las transiciones deben ser totales: para cualquier par `(estado, evento)` debe existir un resultado determinista. Si un
evento es inválido para el estado actual (por ejemplo, recibir una confirmación de datos cuando el proceso fue
cancelado), la función debe rechazarlo explícitamente arrojando una excepción tipada o descartando el evento sin mutar.

### 3. Tipos Suma y Variantes Mutuamente Excluyentes

Los estados se modelan como variantes de un tipo suma (unión discriminada, `Enum` con carga útil o clases inmutables
mutuamente excluyentes). Cada variante transporta únicamente los atributos válidos en su fase:

- El estado `Loading` no posee campo de datos ni error.
- El estado `Success` contiene obligatoriamente la carga útil (`payload`), garantizando que no sea nula.
- El estado `Failed` contiene la excepción o causa raíz diagnóstica.

De este modo, los estados imposibles se vuelven irrepresentables en tiempo de compilación o análisis estático.

---

## 4. Índice de Síntomas Recurrentes

| Síntoma en Código | Defecto Subyacente | Solución Correctiva |
| :--- | :--- | :--- |
| Par de booleanos (`isLoading` y `hasError`) | Combinaciones ilegales representables y alcanzables | Unificar en un Enum/Unión: `Idle`, `Loading`, `Success`, `Failed` |
| Centinela `None` o `-1` como estado | Imposible distinguir fallo de "aún no ejecutado" | Modelar `Option[T]` explícito o variantes de estado con resultado |
| Cadenas crudas (`if status == "pending"`) | Erratas tipográficas caen silenciosamente en ramas por defecto | Enumeración exhaustiva con verificación estática de variantes |
| Temporizador o callback sin vía de cancelación | Un callback tardío se dispara en una fase posterior y la corrompe | Retener el manejador y cancelar en toda transición de salida |
| Variable mutable `var` o `global` en módulo | Fuga de estado entre ejecuciones concurrentes o tareas | Mover el estado a la instancia propietaria del contexto |
| Caché que solo almacena resultados positivos | Recomputación infinita y saturación ante fallos o vacíos | Cachear tanto el éxito como el resultado negativo explícito |

---

## 5. Antes y Después: Gestión de Tarea Asíncrona

### Antes: Banderas Booleanas y Centinelas Mutables

```python
# Anti-pattern: Implicit state machine with loose booleans and nullable buffers
class JobRunner:

    def __init__(self) -> None:
        self.is_running: bool = False
        self.has_error: bool = False
        self.data: dict[str, str] | None = None
        self.error_message: str | None = None

    def start(self) -> None:
        self.is_running = True
        self.has_error = False

    def finish(self, payload: dict[str, str]) -> None:
        # Race condition: payload accepted even if cancelled or already failed
        self.is_running = False
        self.data = payload

    def fail(self, message: str) -> None:
        # Bug: fails to reset data buffer, leaving inconsistent stale state
        self.is_running = False
        self.has_error = True
        self.error_message = message
```

### Después: Máquina de Estados Explícita con Unión Discriminada

```python
# Explicit state machine: sealed state variants with single transition function
from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class IdleState:
    pass


@dataclass(frozen=True)
class RunningState:
    job_id: str


@dataclass(frozen=True)
class CompletedState:
    job_id: str
    result: dict[str, str]


@dataclass(frozen=True)
class FailedState:
    job_id: str
    error: str


JobState = Union[IdleState, RunningState, CompletedState, FailedState]


class IllegalStateTransitionError(RuntimeError):
    """Raised when an event cannot be applied to the current lifecycle state."""


def transition(current_state: JobState, event: str, **kwargs: object) -> JobState:
    match current_state:
        case IdleState():
            if event == "START":
                return RunningState(job_id=str(kwargs["job_id"]))
        case RunningState(job_id=jid):
            if event == "SUCCESS":
                return CompletedState(job_id=jid, result=dict(kwargs["result"]))
            if event == "FAIL":
                return FailedState(job_id=jid, error=str(kwargs["error"]))
        case CompletedState() | FailedState():
            if event == "RESET":
                return IdleState()
    raise IllegalStateTransitionError(f"Invalid transition '{event}' from state {current_state}")
```

---

## 6. Auditoría y Trazabilidad (`STATE_MACHINES_AUDIT.md`)

Para auditar y sanear sistemas existentes, se sigue un protocolo estructurado de auditoría adversarial:

1. **Inspección por Capas**: Examinar manejadores de eventos en UI, clientes de sincronización de red, tareas en segundo
   plano y consumidores de colas de mensajes.
2. **Identificación de Variables Acopladas**: Aislar componentes donde dos o más variables mutables gobiernen una fase
   operativa y donde una llamada desordenada provoque un estado incoherente.
3. **Clasificación por Severidad**:
   - **Alta**: Corrupción de datos, bloqueos mutuos (*deadlocks*), duplicación de efectos secundarios (cobros, envíos).
   - **Media**: Desincronización de interfaz gráfica, estados trabados recuperables mediante reinicio de la aplicación.
4. **Registro Trazable**: Consolidar los hallazgos en un archivo `STATE_MACHINES_AUDIT.md` con identificadores únicos
   secuenciales (`[ISM-001]`), archivo y línea exactos, escenario de falla verificado y propuesta de refactorización.

---

## 7. Señales de Alerta

- Condicionales complejos que evalúan múltiples booleanos (`if is_loading and not is_error and not ready`).
- Bloques de código donde se actualiza un booleano pero se olvida limpiar un búfer de datos o mensaje previo.
- Métodos de callback que asumen que el estado no cambió mientras se completaba una operación asíncrona o de I/O.
- Variables de estado que admiten valores `None` cuyo significado oscila entre "no comenzado", "vacío" o "fallido".
- Comentarios explicativos en el código advirtiendo que ciertas variables "deben modificarse siempre juntas".
- Uso de `status: str` con comparaciones literales repartidas a lo largo de múltiples funciones o archivos.

---

## 8. Checklist de Verificación

- [ ] Las fases operativas y ciclos de vida están modelados con variantes exhaustivas de un tipo suma o `Enum`.
- [ ] No existen dos o más variables booleanas coordinadas gobernando el mismo ciclo de vida.
- [ ] Los estados imposibles son irrepresentables mediante estructuras que solo contienen datos válidos para su fase.
- [ ] Todas las mutaciones de estado ocurren a través de una función de transición única y determinista.
- [ ] Eventos inválidos para el estado actual son rechazados mediante excepciones tipadas (*fail-loud*).
- [ ] Los temporizadores, promesas o callbacks asociados a un estado se cancelan explícitamente al salir de la fase.
- [ ] El componente pasa las cuatro preguntas del *Stop Test* antes de fusionarse a la rama principal.

---

## Navegación

- Anterior: [13 - Revisión de Código](13-revision.md)
- Volver al [README principal](../README.md)
