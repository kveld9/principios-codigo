# 10 - Anti-Hardcoding y Fuente Única de Verdad

La dispersión de valores literales y rutas absolutas en el código compromete la portabilidad entre entornos,
aumenta el riesgo de incoherencias y fragiliza el mantenimiento. La disciplina de diseño exige una única fuente de
verdad autoritativa de la que se deriven valores secundarios y configuraciones desacopladas.

---

## 1. Patrón: Fuente Única de Verdad, Derivación y Consumidores

El principio de fuente única de verdad (*Single Source of Truth*) establece que cada elemento de conocimiento,
identificador de dominio, regla de validación o formato técnico debe residir en un único punto canónico dentro del
sistema. La arquitectura sigue un flujo unidireccional estricto:

```text
Fuente Única de Verdad ──► Derivación / Configuración ──► Consumidores
```

Cuando un concepto cambia, su definición debe actualizarse en un único lugar, propagándose automáticamente a todos
los componentes que dependen de él. Duplicar valores literales en múltiples archivos crea divergencias silenciosas
cuando un desarrollador actualiza una copia y olvida sincronizar las demás.

---

## 2. Derivación Dinámica frente a Copias Secundarias

En lugar de almacenar copias manuales de datos relacionados, los valores secundarios deben derivarse computacionalmente
a partir del origen autoritativo:

1. **Extensiones y tipos de contenido**: Derivar sufijos de archivo y tipos MIME a partir de una enumeración central.
2. **Vocabularios de dominio**: Centralizar catálogos, estados de ciclo de vida y listas de opciones en enumeraciones
   tipadas (`Enum`) o módulos de constantes canónicas.
3. **Atributos compuestos**: Derivar URLs de servicio, recuentos o nombres de archivos canónicos a partir de
   parámetros base en lugar de almacenar copias secundarias propensas a desincronización.

### Antes y Después: Derivación de Formatos desde un Origen Único

#### Antes: Formatos y Extensiones Duplicados en Múltiples Funciones

```python
# Anti-pattern: Formats and extensions duplicated across multiple functions
def is_supported_extension(extension: str) -> bool:
    return extension in [".json", ".yaml", ".csv"]


def get_content_type(extension: str) -> str:
    if extension == ".json":
        return "application/json"
    if extension == ".yaml":
        return "text/yaml"
    if extension == ".csv":
        return "text/csv"
    raise ValueError(f"Unsupported extension: {extension}")
```

#### Después: Fuente Única de Verdad con Derivación Dinámica

```python
# Single source of truth: Enum encapsulating extension and MIME type
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class FormatSpecification:
    extension: str
    content_type: str


class DocumentFormat(Enum):
    JSON = FormatSpecification(".json", "application/json")
    YAML = FormatSpecification(".yaml", "text/yaml")
    CSV = FormatSpecification(".csv", "text/csv")

    @property
    def extension(self) -> str:
        return self.value.extension

    @property
    def content_type(self) -> str:
        return self.value.content_type

    @classmethod
    def from_extension(cls, extension: str) -> "DocumentFormat":
        for document_format in cls:
            if document_format.extension == extension:
                return document_format
        raise ValueError(f"Unsupported extension: {extension}")


def is_supported_extension(extension: str) -> bool:
    return any(document_format.extension == extension for document_format in DocumentFormat)


def get_content_type(extension: str) -> str:
    return DocumentFormat.from_extension(extension).content_type
```

Ejemplo ejecutable: [examples/single_source_of_truth/](../examples/single_source_of_truth/)

---

## 3. Elementos que Jamás Deben Estar Hardcodeados

Cualquier valor sujeto a variación entre entornos, despliegues o políticas operativas debe desacoplarse del código
fuente. Queda prohibido incrustar como literales fijos:

1. **Rutas dependientes del entorno**: Directorios personales (`/home/usuario`, `C:\Users`), rutas absolutas del
   sistema operativo o estructuras dependientes del disco de una máquina de desarrollo concreta.
2. **Direcciones de red, hosts y puertos**: Direcciones IP fijas, números de puerto o URLs de servicios externos.
3. **Credenciales y secretos**: Claves de API, contraseñas de bases de datos, tokens de acceso o certificados.
4. **Versiones duplicadas**: Números de versión del producto o dependencias replicados a mano en múltiples archivos.
5. **Indicadores de funcionalidad (*feature flags*)**: Activación o desactivación de capacidades mediante condicionales
   rígidos incrustados en la lógica de negocio.
6. **Parámetros operativos sintonizables**: Tiempos de espera (*timeouts*), límites de paginación, umbrales de
   reintento o tamaños de lote; deben residir en configuración externa desacoplada.

---

## 4. Jerarquía de Configuración y Resolución de Rutas Portables

Para garantizar que el software se ejecute sin modificaciones en máquinas de desarrollo, contenedores Docker y
servidores de integración continua (CI), la resolución de parámetros debe estructurarse por capas de precedencia.

### Precedencia de Configuración

La configuración debe resolverse respetando el orden estricto de menor a mayor prioridad:

```text
Valores por Defecto ──► Archivo de Configuración ──► Variables de Entorno ──► Argumentos CLI
```

La validación de la configuración debe ejecutarse durante la inicialización de la aplicación (*startup*), fallando de
forma ruidosa si falta un valor obligatorio o si los parámetros provistos carecen de validez sintáctica.

### Portabilidad con `pathlib.Path`

- Utilizar `pathlib.Path` para toda manipulación de rutas en el sistema de archivos, garantizando compatibilidad entre
  separadores POSIX y Windows.
- Resolver ubicaciones relativas a la raíz del proyecto o directorios canónicos del sistema mediante paquetes estándar
  o variables de entorno, evitando presuponer la ubicación del directorio de trabajo actual (*working directory*).

### Antes y Después: Rutas Absolutas vs Resolución Portable

#### Antes: Rutas Absolutas Acopladas al Entorno Local

```python
# Anti-pattern: Hardcoded absolute user path tied to a developer machine
from pathlib import Path

DATA_BACKUP_DIRECTORY = "/home/developer/app_data/backups"


def write_backup(filename: str, payload: str) -> Path:
    target_path = Path(DATA_BACKUP_DIRECTORY) / filename
    target_path.write_text(payload, encoding="utf-8")
    return target_path
```

#### Después: Resolución Portable con Precedencia de Configuración

```python
# Portable directory resolution respecting defaults, environment, and injection
import os
from pathlib import Path

APPLICATION_NAME: str = "backup_service"
BACKUP_DIRECTORY_ENV_VAR: str = "APP_BACKUP_DIR"


def _derive_default_backup_directory() -> Path:
    xdg_state_home = os.environ.get("XDG_STATE_HOME")
    if xdg_state_home:
        base_state_directory = Path(xdg_state_home)
    else:
        base_state_directory = Path.home() / ".local" / "state"
    return base_state_directory / APPLICATION_NAME / "backups"


def resolve_backup_directory(explicit_directory: Path | None = None) -> Path:
    if explicit_directory is not None:
        return explicit_directory
    configured_path = os.environ.get(BACKUP_DIRECTORY_ENV_VAR)
    if configured_path:
        return Path(configured_path)
    return _derive_default_backup_directory()


def write_backup(
    filename: str, payload: str, base_directory: Path | None = None
) -> Path:
    target_directory = resolve_backup_directory(base_directory)
    target_directory.mkdir(parents=True, exist_ok=True)
    target_path = target_directory / filename
    target_path.write_text(payload, encoding="utf-8")
    return target_path
```

---

## 5. Literales Legítimos e Invarianza Documentada

No todo valor literal constituye una mala práctica. Determinados valores son intrínsecos a la definición del dominio
o al protocolo subyacente y no cambian según el entorno.

### Criterios de Literales Permitidos

1. **Constantes matemáticas o físicas**: Coeficientes de conversión fijos (como 60 segundos por minuto o factores
   geométricos inmutables).
2. **Especificaciones de protocolos**: Códigos de estado HTTP (como 200, 404 o 500) o delimitadores normativos de
   formato.
3. **Umbrales algorítmicos fijos**: Factores intrínsecos al algoritmo de cálculo definidos por especificación formal.

Cuando se emplee un literal intrínseco, debe asignarse a una constante en `SCREAMING_SNAKE_CASE` y documentar de forma
explícita su invarianza para distinguirlo de valores de configuración externa.

---

## 6. Señales de Alerta

- Rutas de archivo que incluyen carpetas personales de usuarios (`/home/` o `C:\Users\`).
- Necesidad de modificar más de un archivo para incorporar un nuevo formato de exportación o estado del sistema.
- Pruebas que fallan de forma no determinista en CI por depender de archivos fijos en ubicaciones de la máquina local.
- Cadenas repetidas para nombres de campos de base de datos o claves de diccionario sin constantes compartidas.
- Credenciales, puertos de conexión o claves secretas comprometidas en el árbol de código fuente.
- Concatenación manual de cadenas para componer rutas en lugar de operadores de `pathlib.Path`.

---

## 7. Checklist de Verificación

- [ ] Todo concepto de dominio, formato o estado posee una única fuente de verdad autoritativa.
- [ ] Las extensiones, tipos MIME y valores dependientes se derivan dinámicamente desde el origen canónico.
- [ ] No existen rutas absolutas atadas a directorios de usuario ni nombres de máquina específicos.
- [ ] La manipulación de archivos utiliza `pathlib.Path` y permite la inyección de rutas base.
- [ ] La configuración del sistema respeta la jerarquía `defaults < archivo < entorno < argumentos CLI`.
- [ ] No existen secretos, credenciales ni direcciones de red incrustadas en el código fuente.
- [ ] Los literales intrínsecos legítimos están identificados en constantes con su invarianza documentada.

---

## Navegación

- Anterior: [09 - Manejo de Errores](09-errores.md)
- Volver al [README principal](../README.md)
