# Máquinas de Estado Explícitas (Explicit State Machines)

Este ejemplo demuestra cómo el modelado formal de fases operativas mediante tipos algebraicos inmutables
y una función de transición única previene estados imposibles, carreras de callbacks y corrupciones silenciosas.

## El Problema

En `before.py`, el ciclo de vida de un trabajo de sincronización asíncrona está gobernado por múltiples variables
booleanas independientes (`is_running`, `is_completed`, `is_cancelled`, `has_error`) y un búfer nulo `data_buffer`.

Esta arquitectura implícita sufre fallas graves ante concurrencia o eventos desordenados:

- **Carrera de cancelación**: Si el usuario cancela un trabajo en ejecución y posteriormente arriba un callback
  demorado de red con datos, el método `finish` marca `is_completed = True` sin verificar la cancelación previa.
  El objeto queda en un estado corrupto donde tanto `is_cancelled` como `is_completed` son verdaderos.
- **Datos residuales**: Una falla posterior no limpia los búferes previos, induciendo a consumidores a procesar
  datos obsoletos creyéndolos válidos.
- **Transiciones descontroladas**: Cualquier método puede invocarse en cualquier orden, permitiendo reiniciar
  trabajos ya activos o completar tareas no iniciadas.

## Qué Cambió

En `after.py`, se implementa una máquina de estados finitos explícita respaldada por tipos algebraicos:

- **Variantes inmutables de estado**: Cada fase (`IdleState`, `RunningState`, `CompletedState`, `FailedState`,
  `CancelledState`) es una dataclass congelada que solo contiene los atributos válidos para su momento de vida.
- **Función de transición determinista y total**: Toda mutación pasa por `transition(current_state, event)`,
  la cual evalúa el par de estado actual y evento de dominio.
- **Rechazo ruidoso (*fail-loud*)**: Cualquier evento inválido para el estado actual (como recibir un resultado
  cuando el proceso ya fue cancelado) arroja `IllegalStateTransitionError`.
- **Propietario único**: La clase `ExplicitSyncCoordinator` encapsula el estado y expone `dispatch()`,
  asegurando que no existan variables paralelas dispersas.

## Qué Demuestran las Pruebas

El archivo `test_explicit_state_machine.py` comprueba:

1. El recorrido determinista en caminos exitosos, fallidos y cancelados.
2. El rechazo mediante excepción de cualquier transición no permitida según la matriz de estados.
3. La reproducción directa de la condición de carrera con callbacks demorados, evidenciando el estado
   inconsistente en `before.py` frente al blindaje determinista en `after.py`.
