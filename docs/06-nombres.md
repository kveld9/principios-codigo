# 06 - Nombres, Legibilidad y Comentarios

La selección precisa de identificadores y el uso disciplinado de comentarios constituyen los pilares fundamentales
de la legibilidad del código. El código fuente debe estructurarse como su propia documentación técnica: los nombres
deben comunicar su intención sin ambigüedad y los comentarios deben reservarse para justificar decisiones no evidentes.

---

## 1. Convenciones para Archivos y Directorios

Los nombres en el sistema de archivos deben ser predecibles, uniformes y portables entre distintos sistemas operativos:

1. **Minúsculas con guion (`kebab-case`)**: Convención por defecto para scripts, documentación técnica y recursos
   generales del repositorio (`deploy-service.sh`, `06-nombres.md`).
2. **Módulos y paquetes en Python**: Emplear **`snake_case`** en minúsculas sin caracteres especiales (`order_service.py`,
   `database_connection.py`).
3. **Excepciones canónicas en la raíz**: Respetar los nombres exigidos por plataformas de alojamiento y gobernanza
   (`README.md`, `LICENSE`, `CONTRIBUTING.md`).
4. **Política de Emojis Centralizada**: Los nombres de archivos, directorios, ramas y código fuente quedan estrictamente
   libres de emojis. La política integral se consulta en el kit hermano:
   [Política Estricta sobre Emojis (principios-git)](https://github.com/kveld9/principios-git/blob/main/docs/11-estilo.md).

---

## 2. Identificadores: Reglas de Diseño Semántico

Los nombres de variables, funciones, clases y módulos deben comunicar con claridad su función en el dominio:

### Reglas Semánticas Fundamentales

1. **Nombres que revelan intención**: Un identificador debe responder por qué existe, qué representa y cómo se utiliza.
   Si un nombre requiere un comentario explicativo adyacente para entenderse, el nombre es defectuoso.
2. **Regla de longitud según el alcance (*Scope-Length Rule*)**:
   - Variables de alcance mínimo (1-2 líneas en una iteración simple o comprensión): se admiten identificadores breves
     convencionales (`i` para índices, `row` para registros inmediatos).
   - Variables globales, atributos de clase o funciones públicas: deben emplear nombres descriptivos y completos
     (`connection_timeout_seconds`, `calculate_compound_interest`).
3. **Verbos para acciones, sustantivos para datos**:
   - Funciones y métodos representan transformaciones: emplear verbos (`calculate_tax`, `validate_order`).
   - Clases y estructuras representan conceptos de dominio: emplear sustantivos (`Invoice`, `CustomerRepository`).
4. **Predicados booleanos como preguntas**: Variables y funciones booleanas deben utilizar prefijos interrogativos o de
   estado (`is_active`, `has_permission`, `can_retry`, `should_flush`).
5. **Prohibición de prefijos de tipo y notación húngara**: No incorporar el tipo de dato en el identificador
   (`customer_list`, `str_name`, `account_dict`). Los sistemas de tipado estático ya documentan este aspecto.
6. **Prohibición de abreviaturas crípticas**: No utilizar contracciones informales (`calc_del`, `mgr`, `repo`, `fn`).
   Se admiten únicamente acrónimos estándar del dominio del software (`url`, `id`, `html`, `sql`).
7. **Consistencia léxica (Una palabra por concepto)**: Mantener un término uniforme para la misma operación en todo el
   código. Se prohíbe alternar entre `get`, `fetch` y `retrieve` para operaciones de consulta idénticas.
8. **Idioma técnico uniforme**: Todo identificador, parámetro y comentario de código debe redactarse en idioma inglés.

---

## 3. Comentarios: Explicar el Por Qué, Nunca el Qué

El código fuente describe con precisión técnica **qué** ocurre y **cómo** se ejecuta. Los comentarios deben
reservarse exclusivamente para explicar **por qué** se tomó una decisión particular o qué restricciones condicionan el flujo.

### Cuándo Está Justificado un Comentario

1. **Restricciones externas no evidentes**: Limitaciones impuestas por protocolos de hardware, normativas legales o
   APIs de terceros que obligan a utilizar un algoritmo contraintuitivo.
2. **Soluciones temporales con enlace (*Workaround*)**: Correcciones provisionales ante fallos externos que deben
   vincular el ticket o enlace de seguimiento (`# Bug tracking: https://github.com/vendor/repo/issues/1042`).
3. **Docstrings en interfaces y APIs públicas**: Especificación contractual de funciones públicas detallando
   precondiciones, argumentos y excepciones esperadas.

### Erradicación de Código Muerto Comentado

Queda terminantemente prohibido conservar bloques de código comentados ("por si se necesita después"). El historial de
Git constituye la única memoria histórica del proyecto; cualquier fragmento en desuso debe eliminarse de inmediato
(ver doc 12, Code Smells y Refactorización Segura).

### Política Estricta de Marcadores TODO

Los marcadores `TODO` solo son válidos si contienen un responsable explícito o una referencia a una incidencia activa:

```python
# Format: TODO(username): Issue #ID - Actionable description
# TODO(jdoe): Issue #482 - Migrate to bulk insert once backend endpoint is deployed
```

---

## 4. Formato Automatizado: Delegación a Herramientas

El estilo visual del código (espaciado, saltos de línea, orden de importaciones, formato de comillas) no debe consumirse
como tiempo de debate en revisiones por pares:

1. **Formateadores automáticos deterministas**: El formateo se delega completamente a herramientas estandarizadas del
   ecosistema (`ruff format` / `black` en Python, `prettier` en TypeScript, `ktlint` en Kotlin).
2. **Validación en pipelines de CI**: Si un archivo presenta discrepancias con el estándar del formateador, el pipeline
   de integración continua rechaza el cambio de forma automática.
3. **Cero debate en Pull Requests**: Ningún revisor debe comentar sobre estilo visual o indentación; el estándar
   formalizado por la herramienta es inapelable.

---

## 5. Antes y Después: Nomenclatura y Comentarios

### Ejemplo 1: Nombres Reveladores vs Notación Críptica

#### Antes: Identificadores Ambiguos y Comentarios Redundantes

```python
# Function to get users from database
# l: list of users, f: flag for active
def get_usr_data(l: list[dict[str, object]], f: bool) -> list[str]:
    # create empty result list
    res_arr: list[str] = []
    for item in l:
        # check if active
        if item.get("act") == f:
            res_arr.append(str(item.get("nid")))  # append numeric id
    return res_arr
```

#### Después: Identificadores Semánticos y Predicado Explícito

```python
# Named constants mirroring upstream record schema keys
ACTIVE_FIELD = "act"
ACCOUNT_ID_FIELD = "nid"


def extract_account_identifiers(
    accounts: list[dict[str, object]], is_active_required: bool
) -> list[str]:
    matching_identifiers: list[str] = []

    for account in accounts:
        if bool(account.get(ACTIVE_FIELD)) == is_active_required:
            identifier = account.get(ACCOUNT_ID_FIELD)
            if identifier is not None:
                matching_identifiers.append(str(identifier))

    return matching_identifiers
```

### Ejemplo 2: Comentarios Justificados y Eliminación de Código Muerto

#### Antes: Código Comentado Muerto y Comentarios Evidentes

```python
from decimal import Decimal

# TODO: fix this later
# def calculate_tax(amount: Decimal) -> Decimal:
#     return amount * Decimal("0.15")


def calculate_tax(amount: Decimal) -> Decimal:
    # Multiply amount by twenty-one percent
    return amount * Decimal("0.21")
```

#### Después: Restricción Explicada y TODO Trazable

```python
from decimal import Decimal

# Standard VAT rate mandated by national fiscal directive (Statute 14-A)
STANDARD_VAT_RATE = Decimal("0.21")

# TODO(jdoe): Issue #402 - Support reduced rate when product category is registered


def calculate_value_added_tax(amount: Decimal) -> Decimal:
    return amount * STANDARD_VAT_RATE
```

---

## 6. Señales de Alerta

1. **Variables de una sola letra fuera de iteraciones breves**: Identificadores como `d`, `tmp` o `val` en ámbitos amplios.
2. **Prefijos de tipo en nombres de variables**: Identificadores como `customer_list`, `int_timeout` o `order_dict`.
3. **Bloques de código comentado en archivos activos**: Indican desconfianza en el historial de Git.
4. **Comentarios que parafrasean el código**: Anotaciones redundantes que narran la sintaxis en lugar de la intención.
5. **Alineación manual o discrepancias de estilo en revisiones**: Síntoma de ausencia de formateador automático configurado.

---

## 7. Checklist de Verificación

- [ ] Los archivos y directorios siguen las convenciones del ecosistema (`kebab-case` o `snake_case`) sin emojis.
- [ ] Los identificadores revelan intención y están redactados íntegramente en idioma inglés técnico.
- [ ] Las funciones emplean verbos de acción y las clases o datos emplean sustantivos.
- [ ] Las variables booleanas están formuladas como predicados interrogativos (`is_`, `has_`, `can_`).
- [ ] Se evitaron abreviaturas crípticas y no se utilizaron prefijos de tipos húngaros.
- [ ] No existen bloques de código comentado ni marcadores TODO sin responsable o número de issue.
- [ ] Los comentarios justifican decisiones no evidentes (*por qué*) y no describen la sintaxis (*qué*).
- [ ] El formato visual se delega a formateadores automáticos (`ruff format`, `black`, `prettier`).

---

## Navegación

- Anterior: [05 - Funciones Pequeñas y Complejidad Ciclomática](05-funciones.md)
- Siguiente: [07 - Desarrollo Guiado por Pruebas (TDD)](07-tdd.md)
- Volver al [README principal](../README.md)
