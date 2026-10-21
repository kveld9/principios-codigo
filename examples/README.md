# Ejemplos Ejecutables de Principios de Código

Compendio de ejemplos prácticos en Python que demuestran principios profesionales de diseño,
modularización, calidad de código y arquitectura de software. Cada ejemplo incluye una versión
inicial con el antipatrón (`before.py`), la versión refactorizada (`after.py` o paquete `after/`),
pruebas automatizadas con `pytest` y documentación explicativa.

---

## Índice de Ejemplos

| Directorio | Principio de Diseño | Documento |
|---|---|---|
| `god_module_split` | Separación de Módulo Dios y Responsabilidad Única | doc 02 |
| `ports_adapters` | Puertos y Adaptadores (Arquitectura Hexagonal) | doc 03, 11 |
| `guard_clauses` | Cláusulas de Guarda y Tablas de Despacho | doc 05 |
| `tdd_kata` | Desarrollo Guiado por Pruebas (TDD Kata) | doc 07 |
| `parse_dont_validate` | Analizar en Lugar de Validar (*Parse, Don't Validate*) | doc 09 |
| `single_source_of_truth` | Única Fuente de Verdad y Precedencia de Configuración | doc 10 |
| `value_object` | Objetos de Valor e Inmutabilidad (*Value Objects*) | doc 12 |

---

## Ejecución Local de Puertas de Calidad (Gates)

Instalación inicial de dependencias de desarrollo (requiere `pip >= 25.1`):

```bash
python -m pip install --group dev
```

Comandos para ejecutar localmente la suite de verificación de calidad:

### 1. Verificación Estática y Estilo con Ruff

```bash
ruff check .
ruff format --check .
```

### 2. Ejecución de la Suite de Pruebas con Pytest

```bash
pytest
```

### 3. Control de Complejidad Ciclomática con Radon

Se exige que ninguna función nueva o modificada (fuera de los archivos de antipatrón `before`)
supere una complejidad ciclomática de CC <= 5 (Grado A):

```bash
radon cc --min B --show-complexity --exclude "examples/*/before.py,examples/*/before/*" examples
```

El resultado de este comando debe ser vacío. Para verificar la presencia del antipatrón en `guard_clauses`:

```bash
radon cc --min C --show-complexity examples/guard_clauses/before.py
```

### 4. Validación de Markdown

```bash
npx -y markdownlint-cli2@0.18.1 "**/*.md"
```
