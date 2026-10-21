# 01 - Principios Fundamentales de Código

El diseño de software profesional requiere directrices rigurosas que prioricen la mantenibilidad, la simplicidad
conceptual y la verificación empírica. Dado que el código fuente se lee con una frecuencia decenas de veces
superior a la que se modifica, la claridad técnica prima sobre cualquier artificio sintáctico o solución ingeniosa.

---

## 1. Alcance y Separación con Gobernanza de Repositorio

Este estándar gobierna exclusivamente el diseño, estructuración y calidad interna del código fuente. Las políticas
de gobernanza de repositorio, automatización de flujos de trabajo en CI/CD, convenciones de Git y ciclo de vida de
versiones residen de forma separada en el kit hermano:

- [01 - Principios Fundamentales de Repositorio (principios-git)](https://github.com/kveld9/principios-git/blob/main/docs/01-principios.md)

Ambos conjuntos de principios operan de forma complementaria: la gobernanza de Git asegura la trazabilidad del cambio,
mientras que los estándares de código aseguran que la implementación sea legible, comprobable y desacoplada.

---

## 2. Legibilidad, Simplicidad y Diseño Explícito

La complejidad accidental es la principal causa de defectos y ralentización en el mantenimiento de software. La
comprensión del comportamiento del sistema debe ser directa e inequívoca.

### Reglas de Diseño

1. **Legibilidad sobre ingenio**: El código debe optimizarse para el lector, no para la brevedad del autor. Construcciones
   compactas pero crípticas (como comprensiones de listas anidadas o trucos a nivel de bits sin abstracción) aumentan la
   carga cognitiva y ocultan fallos lógicos.
2. **KISS (Keep It Simple, Stupid) y YAGNI con criterio**: Resolver únicamente el problema actual con la solución más
   simple que satisfaga los requerimientos técnicos comprobados. Queda prohibido introducir niveles de abstracción,
   indirección o parametrizaciones para casos de uso hipotéticos no solicitados.
3. **Explícito sobre implícito**: El flujo de datos y las dependencias de cada componente deben ser visibles. Deben
   evitarse estados globales mutables, mutaciones laterales ocultas y metaconvenciones opacas que alteren variables fuera
   del alcance local.

### Antes y Después: Legibilidad sobre Ingenio

#### Antes: Código Críptico

```python
# Cryptic comprehension relying on implicit structure and bitwise mask
def filter_active_records(records: list[dict]) -> list[str]:
    return [
        r["id"]
        for r in records
        if r.get("status") == "A" and not (r.get("meta", {}).get("flags", 0) & 2)
    ]
```

#### Después: Código Explícito y Legible

```python
# Named constants derived from external record specification
ACTIVE_STATUS = "A"
SUSPENDED_FLAG = 0b10


def extract_active_account_ids(records: list[dict]) -> list[str]:
    active_ids: list[str] = []

    for record in records:
        if record.get("status") != ACTIVE_STATUS:
            continue
        flags = record.get("meta", {}).get("flags", 0)
        if flags & SUSPENDED_FLAG:
            continue
        record_id = record.get("id")
        if record_id:
            active_ids.append(str(record_id))

    return active_ids
```

---

## 3. Principio del Cambio Mínimo y Regla del Boy Scout Acotada

Cada modificación al árbol de código debe perseguir el objetivo funcional concreto con la menor superficie de cambio
posible, reduciendo el riesgo de regresiones colaterales.

### Criterios Operativos

1. **Cambio mínimo necesario**: Implementar la solución que satisfaga los invariantes del problema sin alterar
   archivos, contratos ni configuraciones ajenas a la tarea. Las refactorizaciones a gran escala no deben camuflarse
   dentro de commits correctivos o funcionales.
2. **Regla del boy scout estrictamente acotada**: Dejar el código más limpio de lo que se encontró, pero limitando
   la limpieza al entorno inmediato del cambio (como renombrar una variable ambigua o eliminar código muerto local en la
   función intervenida).
3. **Prohibición de refactorizaciones oportunistas**: Queda prohibido reformatear archivos completos, reordenar
   importaciones no relacionadas o reescribir módulos enteros bajo la excusa de mejora estética si están fuera del alcance
   específico del requerimiento.

---

## 4. Correctitud, Optimización Medida y Falla Ruidosa

El valor primordial del software radica en su comportamiento correcto y predecible bajo cualquier condición operativa.

### Reglas de Ejecución

1. **Correctitud antes que velocidad**: Entregar código cuya correctitud esté verificada mediante pruebas automatizadas
   antes de considerar su rapidez de ejecución. Un algoritmo veloz que produce resultados incorrectos carece de valor
   técnico.
2. **Optimización solo con evidencia empírica**: Toda optimización de rendimiento debe fundamentarse en perfiles de
   ejecución (*profiling*), mediciones de asignación de memoria o pruebas de carga reproducibles. Se prohíben las
   micro-optimizaciones especulativas que sacrifiquen legibilidad sin aportar una mejora medible en el entorno destino.
3. **Fallar de forma ruidosa (Fail-Loud)**: Ante datos inválidos, configuraciones inconsistentes o rotura de invariantes,
   el código debe detenerse de inmediato y emitir un error explícito con contexto diagnóstico. Se prohíbe capturar
   excepciones para retornar valores centinela ambiguos (`None`, cadenas vacías) que propaguen fallos silenciosos
   (resumen técnico; detalle extensivo en doc 09, Manejo de Errores).

### Antes y Después: Falla Ruidosa

#### Antes: Silenciamiento y Ocultamiento de Fallos

```python
# Silent failure swallowing parsing errors and returning ambiguous sentinel
def read_port_number(config: dict[str, str]) -> int | None:
    try:
        raw_port = config.get("port")
        return int(raw_port) if raw_port is not None else 8080
    except (ValueError, TypeError):
        return None  # Masks invalid state; caller cannot detect root cause
```

#### Después: Validación Explícita y Fail-Loud

```python
# Fail-loud validation raising actionable error with diagnostic context
def parse_port_number(config: dict[str, str], default_port: int = 8080) -> int:
    raw_port = config.get("port")
    if raw_port is None:
        return default_port
    try:
        port = int(raw_port)
    except ValueError as err:
        msg = f"Configuration 'port' must be an integer, got: {raw_port!r}"
        raise ValueError(msg) from err
    if not (1 <= port <= 65535):
        msg = f"Port number out of valid range (1-65535): {port}"
        raise ValueError(msg)
    return port
```

---

## 5. Mapa de Principios del Kit

La siguiente tabla resume los principios fundamentales del diseño de código y su desarrollo en los documentos del kit:

| Principio / Estándar | Alcance Central | Documento de Referencia |
| :--- | :--- | :--- |
| Legibilidad y Simplicidad | Claridad léxica, KISS, YAGNI y comprensibilidad | [01 - Principios Fundamentales de Código](01-principios.md) |
| Diseño Modular y Fronteras | Cohesión, acoplamiento, contratos y descomposición | [02 - Diseño Modular y Eliminación de Monolitos](02-diseno-modular.md) |
| Dirección de Dependencias | Dominio puro, puertos, adaptadores y composition root | [03 - Arquitectura y Dirección de Dependencias](03-arquitectura.md) |
| Responsabilidad y Extensibilidad | Principios SOLID aplicados a clases y componentes | doc 04, Principios SOLID |
| Reducción de Complejidad | Funciones breves, guard clauses y CC <= 5 | doc 05, Funciones Pequeñas y Complejidad Ciclomática |
| Nomenclatura Intencional | Identificadores reveladores y ausencia de código muerto | doc 06, Nombres, Legibilidad y Comentarios |
| Desarrollo Guiado por Pruebas | Ciclo Red-Green-Refactor y diseño verificable | doc 07, Desarrollo Guiado por Pruebas (TDD) |
| Estrategia de Testing | Pirámide de pruebas, determinismo y contratos | doc 08, Estrategia de Testing |
| Robustez ante Excepciones | Fallar de forma ruidosa (fail-loud) y tipado de errores | doc 09, Manejo de Errores |
| Fuente Única de Verdad | Anti-hardcoding, constantes y valores derivados | doc 10, Anti-Hardcoding y Fuente Única de Verdad |
| Inyección de Dependencias | Inversión de control y resolución explícita | doc 11, Inyección y Gestión de Dependencias |
| Refactorización Segura | Detección de code smells y transformación incremental | doc 12, Code Smells y Refactorización Segura |
| Calidad y Auditoría de Código | Criterios de revisión por pares y verificación estática | doc 13, Revisión de Código |

---

## 6. Señales de Alerta

La presencia de cualquiera de los siguientes síntomas evidencia un incumplimiento de los principios fundamentales:

1. **Complejidad justificada por flexibilidad futura**: Clases abstractas o parámetros de configuración añadidos sin
   que exista un consumidor real en producción.
2. **Optimizaciones sin telemetría ni pruebas comparativas**: Reemplazo de código simple y legible por lógica compleja
   sin presentar mediciones de tiempo o memoria que justifiquen el cambio.
3. **Difusión desmedida del cambio**: Un requerimiento puntual que modifica decenas de archivos no relacionados debido a
   refactorizaciones estéticas no solicitadas.
4. **Capturas de error ciegas**: Bloques `except Exception: pass` o devoluciones de valores por defecto que encubren
   estados corruptos de ejecución.

---

## 7. Checklist de Verificación

Antes de aprobar o integrar un cambio en el código fuente, verificar los siguientes puntos:

- [ ] La solución implementada es la más directa y legible que satisface los requerimientos actuales.
- [ ] No se incorporaron abstracciones anticipadas, hooks genéricos ni parámetros para casos hipotéticos.
- [ ] Las modificaciones respetan el principio del cambio mínimo sin alterar archivos fuera del alcance.
- [ ] Cualquier limpieza menor se restringió estrictamente al entorno inmediato intervenido.
- [ ] Las decisiones de rendimiento cuentan con mediciones empíricas reproducibles previas.
- [ ] Los invariantes de negocio y validaciones de entrada fallan de forma ruidosa ante datos inválidos.

---

## Navegación

- Siguiente: [02 - Diseño Modular y Eliminación de Monolitos](02-diseno-modular.md)
- Volver al [README principal](../README.md)
