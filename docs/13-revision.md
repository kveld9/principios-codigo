# 13 - Revisión de Código

La revisión de código por pares (*code review*) es una disciplina de ingeniería diseñada para asegurar la correctitud
técnica, preservar la coherencia arquitectónica y facilitar la transferencia de conocimiento antes de incorporar
cualquier cambio a la rama principal.

Este documento establece la jerarquía de objetivos durante la revisión, las responsabilidades del autor, el
procedimiento de inspección técnica para el revisor y las convenciones de etiqueta y severidad de comentarios.

---

## 1. Jerarquía de Objetivos en la Revisión

El tiempo de los revisores humanos debe invertirse en aspectos de alto nivel cognitivo. La revisión de código debe
respetar la siguiente jerarquía de prioridades:

1. **Correctitud**: Cumplimiento fiel de los requerimientos, preservación de invariantes de dominio, ausencia de
   condiciones de carrera y tratamiento exhaustivo de casos de borde.
2. **Diseño y arquitectura**: Respeto a los límites de módulos, acoplamiento débil, dirección de dependencias hacia el
   dominio y aplicación coherente de principios SOLID (ver [02 - Diseño Modular](02-diseno-modular.md),
   [03 - Arquitectura](03-arquitectura.md) y [04 - SOLID](04-solid.md)).
3. **Legibilidad y mantenibilidad**: Claridad conceptual de los identificadores, funciones pequeñas y control de
   complejidad ciclomática (ver [05 - Funciones](05-funciones.md) y [06 - Nombres](06-nombres.md)).
4. **Estrategia de pruebas**: Pruebas unitarias deterministas, cobertura de casos borde reales y ausencia de
   retardos temporales fijos (ver [07 - TDD](07-tdd.md) y [08 - Testing](08-testing.md)).
5. **Seguridad**: Validación estricta en fronteras, ausencia de credenciales incrustadas y registros de log sin datos
   confidenciales (ver [09 - Manejo de Errores](09-errores.md) y [10 - Anti-Hardcoding](10-hardcoding.md)).

### El Estilo es Responsabilidad del Formateador

Las discrepancias de indentación, saltos de línea, orden de importaciones o longitud de línea deben ser resueltas por
herramientas automáticas (`ruff format`, `black`, `prettier`) y linters en el pipeline de CI. Un revisor humano nunca
debe emitir observaciones sobre formato visual automatizable.

---

## 2. Preparación y Responsabilidad del Autor

Antes de solicitar la revisión de un compañero, el autor del cambio debe completar una verificación previa rigurosa:

- **Auto-revisión exhaustiva del diff (`git diff`)**: Inspeccionar la totalidad de las líneas modificadas antes de abrir
  el Pull Request. Este paso detecta archivos residuales, logs de depuración y descuidos evidentes.
- **Suite de pruebas y linters en verde**: El código debe compilar, formatearse y aprobar la totalidad de las pruebas
  automatizadas localmente y en el pipeline de CI.
- **Tamaño acotado del Pull Request**: Mantener los cambios por debajo de 400 líneas modificadas como umbral por
  defecto. Los cambios extensos inducen fatiga cognitiva y reducen drásticamente la tasa de detección de defectos.
  Consultar los lineamientos de PRs en el
  [Kit principios-git](https://github.com/kveld9/principios-git/blob/main/docs/05-pull-requests.md).
- **Sincronización documental**: Si la modificación altera contratos públicos, configuración o comportamientos de
  usuario, la documentación técnica debe actualizarse en el mismo conjunto de cambios.

---

## 3. Protocolo de Inspección para el Revisor

El revisor debe evaluar el cambio mediante una secuencia sistemática:

1. **Comprender la intención**: Leer la descripción técnica del cambio y el issue vinculado antes de mirar el código.
2. **Leer las pruebas primero**: Examinar los archivos de prueba para entender el comportamiento esperado y los
   contratos de entrada y salida asumidos por el autor.
3. **Identificar casos no contemplados**: Buscar activamente valores nulos, colecciones vacías, desconexiones de red,
   desbordamientos numéricos o estados no sincronizados ausentes en la suite.
4. **Verificar caminos de error**: Comprobar que los fallos operen bajo filosofía *fail-loud* con excepciones tipadas
   y sin capturas vacías (`pass`).
5. **Auditar nombres y modularidad**: Contrastar los nuevos identificadores y estructuras contra los estándares de
   [05 - Funciones Pequeñas](05-funciones.md) y [06 - Nombres, Legibilidad y Comentarios](06-nombres.md).

> [!NOTE]
> Para auditar el cumplimiento integral de los estándares de código en cualquier fase del proyecto, remitirse a la
> lista consolidada en [CHECKLIST.md](../CHECKLIST.md).

---

## 4. Etiqueta y Convención de Severidad en Comentarios

La comunicación en revisiones debe ser estrictamente técnica, objetiva y orientada a mejorar la solución:

- **Criticar el código, no a la persona**: Formular observaciones impersonales centradas en el comportamiento del
  sistema ("Esta función produce un error si el balance es negativo" en lugar de "Olvidaste validar el balance").
- **Comentarios accionables y fundamentados**: Explicar el impacto técnico concreto y sugerir una alternativa viable.
- **Clasificación explícita de severidad**:
  - `[Bloqueante]`: Defecto funcional, falla de seguridad o violación arquitectónica grave; impide la aprobación.
  - `[Sugerencia]`: Alternativa de diseño o simplificación opcional; queda a criterio del autor.
  - `[Pregunta]`: Consulta para aclarar el razonamiento de una decisión no evidente.
  - `[Nit]`: Detalle menor no automatizado; no bloquea la integración bajo ninguna circunstancia.

---

## 5. Ejemplos de Hallazgos en Revisión de Código

### Validación de Fronteras e Invariantes de Dominio

#### Antes: Omisión de Validación en Entrada de Crédito

```python
# Code submitted for review: author omitted boundary checks on credit adjustments
from decimal import Decimal


def apply_promotional_credit(balance: Decimal, credit_amount: Decimal) -> Decimal:
    return balance + credit_amount
```

#### Después: Corrección de Caso Borde Señalado por el Revisor

```python
# Reviewer noted negative credits would withdraw funds; guard clause enforces invariant
from decimal import Decimal


def apply_promotional_credit(balance: Decimal, credit_amount: Decimal) -> Decimal:
    if credit_amount <= Decimal("0"):
        raise ValueError(f"Credit amount must be positive, got: {credit_amount}")
    return balance + credit_amount
```

### Separación de Cálculo y Efectos Secundarios

#### Antes: Mezcla de Lógica Contable con Efectos de Salida

```python
# Submitted code mixes mathematical calculation with console side effect
from decimal import Decimal

DAILY_LATE_FEE_RATE: Decimal = Decimal("0.02")


def calculate_late_fee(balance: Decimal, overdue_days: int) -> Decimal:
    fee = balance * DAILY_LATE_FEE_RATE * overdue_days
    print(f"Computed late fee: {fee}")  # Side effect pollutes domain calculation
    return fee
```

#### Después: Función Pura Determinista Desacoplada de I/O

```python
# Review feedback extracted pure deterministic calculation, delegating presentation
from decimal import Decimal

DAILY_LATE_FEE_RATE: Decimal = Decimal("0.02")


def calculate_late_fee(balance: Decimal, overdue_days: int) -> Decimal:
    if overdue_days < 0:
        raise ValueError(f"Overdue days cannot be negative, got: {overdue_days}")
    return balance * DAILY_LATE_FEE_RATE * overdue_days


# Caller at presentation boundary prints or renders: print(f"Computed late fee: {fee}")
```

La presentación y visualización en consola se delegan al llamador en la frontera de entrega, manteniendo la función de
cálculo pura, determinista y directamente verificable mediante pruebas unitarias.

---

## 6. Señales de Alerta

- Pull Requests aprobados en menos de dos minutos con comentarios superficiales como "LGTM" sin revisión real.
- Hilos de discusión extensos sobre preferencias estéticas que deberían delegarse al formateador automático.
- Pull Requests abiertos con pruebas fallidas o que rompen la compilación en CI.
- Comentarios con tono condescendiente, sarcasmo o dirigidos hacia las capacidades del autor.
- Aprobaciones concedidas mientras persisten comentarios marcados como `[Bloqueante]` sin resolver.

---

## 7. Checklist de Verificación de Revisión

- [ ] El autor ejecutó una auto-revisión exhaustiva de su propio `git diff` antes de asignar revisores.
- [ ] La totalidad de las pruebas automatizadas, linters y verificaciones de CI están en estado verde.
- [ ] El Pull Request se mantiene dentro del umbral de tamaño recomendado (< 400 líneas modificadas).
- [ ] La documentación técnica y las notas de cambio se actualizaron en el mismo conjunto de cambios.
- [ ] El revisor leyó las pruebas antes que el código de producción para validar los contratos observables.
- [ ] Se verificaron los casos de borde, entradas inválidas y caminos de excepción (*fail-loud*).
- [ ] Los comentarios de revisión son objetivos, accionables y emplean etiquetas de severidad explícitas.
- [ ] No se aprobaron cambios que mantengan observaciones bloqueantes pendientes de resolución.

---

## Navegación

- Anterior: [12 - Code Smells y Refactorización Segura](12-refactorizacion.md)
- Volver al [README principal](../README.md)
