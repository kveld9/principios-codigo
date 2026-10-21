# Kit de Principios de Código

Plantilla de ingeniería y compendio de estándares profesionales para el diseño, modularización y construcción
de software mantenible, comprobable y desacoplado.

Este kit unifica principios de ingeniería agnósticos del lenguaje (modularización, límites arquitectónicos,
TDD, Clean Code, SOLID, reducción de complejidad ciclomática, convenciones de nomenclatura, manejo robusto de
errores, anti-hardcoding y técnicas de refactorización) con ejemplos ejecutables en Python.

---

## Relación con principios-git

Este kit se enfoca exclusivamente en la calidad, estructura y organización del código fuente. Las responsabilidades
de gobernanza de repositorios, automatización de CI/CD, políticas de ramas, Conventional Commits y releases
se gestionan de forma complementaria en el kit hermano:

- [Kit principios-git](https://github.com/kveld9/principios-git): gobernanza, CI y estándares de repositorio.

Ambos proyectos forman una suite coherente: `principios-git` define el gobierno y ciclo de vida del repositorio,
mientras que `principios-codigo` define los estándares del código que alberga.

---

## Mapa del Kit

Estructura física del repositorio tras la fase de andamiaje inicial:

```text
.
├── Licencia y Gobernanza
│   ├── LICENSE                       # Licencia MIT base
│   ├── CONTRIBUTING.md               # Guía técnica de contribución y validación local
│   ├── CHECKLIST.md                  # Lista de verificación consolidada por fases
│   └── README.md                     # Descripción general y mapa de componentes
│
├── Documentación Técnica (docs/)
│   ├── 01-principios.md              # Principios fundamentales y mapa conceptual
│   ├── 02-diseno-modular.md          # Modularidad, contratos y eliminación de monolitos
│   ├── 03-arquitectura.md            # Arquitectura hexagonal y dirección de dependencias
│   ├── 04-solid.md                   # Principios SOLID y abstracción proporcional
│   ├── 05-funciones.md               # Funciones pequeñas y complejidad ciclomática
│   ├── 06-nombres.md                 # Nombres, legibilidad y comentarios
│   ├── 07-tdd.md                     # Desarrollo guiado por pruebas, ciclo y katas
│   ├── 08-testing.md                 # Estrategia de testing, pirámide y determinismo
│   ├── 09-errores.md                 # Filosofía fail-loud, análisis en frontera y excepciones
│   ├── 10-hardcoding.md              # Fuente única de verdad, derivación y portabilidad
│   ├── 11-dependencias.md            # Inyección de dependencias, puertos y librerías externas
│   ├── 12-refactorizacion.md         # Code smells, pruebas de caracterización y refactor seguro
│   └── 13-revision.md                # Revisión de código, prioridades, etiqueta y tamaño de PR
│
├── Ejemplos Ejecutables (examples/)
│   ├── god_module_split/             # Separación de monolito en módulos cohesivos
│   ├── ports_adapters/               # Arquitectura hexagonal con puertos Protocol
│   ├── guard_clauses/                # Reducción de CC con cláusulas de guarda
│   ├── tdd_kata/                     # Desarrollo guiado por pruebas paso a paso
│   ├── parse_dont_validate/          # Modelado tipado inmutable en la frontera
│   ├── single_source_of_truth/       # Única fuente de verdad y rutas desacopladas
│   └── value_object/                 # Objeto de valor Money con precisión Decimal
│
├── Configuración del Entorno
│   ├── .editorconfig                 # Reglas de formato, indentación y codificación
│   ├── .gitattributes                # Normalización forzada de finales de línea a LF
│   ├── .gitignore                    # Reglas de exclusión para SO, entornos y Python
│   ├── .markdownlint.yaml            # Reglas de validación estática para Markdown
│   └── pyproject.toml                # Configuración de dependencias dev, ruff, pytest y radon
│
└── Automatización y GitHub (.github/)
    ├── dependabot.yml                # Actualizaciones periódicas de GitHub Actions
    └── workflows/
        └── ci.yml                    # Verificación automatizada de Markdown y ejecución limpia
```

---

## Documentación

Los módulos de documentación técnica y principios conceptuales se incorporan de forma incremental en
fases posteriores, preservando la trazabilidad de cada estándar.

- [01 - Principios Fundamentales de Código](docs/01-principios.md): Legibilidad, cambio mínimo y correctitud.
- [02 - Diseño Modular y Eliminación de Monolitos](docs/02-diseno-modular.md): Cohesión, contratos y cero monolitos.
- [03 - Arquitectura y Dirección de Dependencias](docs/03-arquitectura.md): Regla de dependencia y dominio sin I/O.
- [04 - Principios SOLID](docs/04-solid.md): Responsabilidad, extensibilidad y abstracción proporcional.
- [05 - Funciones Pequeñas y Complejidad Ciclomática](docs/05-funciones.md): Umbrales, métricas y refactorización.
- [06 - Nombres, Legibilidad y Comentarios](docs/06-nombres.md): Nomenclatura intencional, comentarios y formato.
- [07 - Desarrollo Guiado por Pruebas (TDD)](docs/07-tdd.md): Ciclo Red-Green-Refactor, triangulación y katas.
- [08 - Estrategia de Testing](docs/08-testing.md): Pirámide de pruebas, dobles, determinismo y mutación.
- [09 - Manejo de Errores](docs/09-errores.md): Filosofía fail-loud, análisis en frontera y excepciones tipadas.
- [10 - Anti-Hardcoding y Fuente Única de Verdad](docs/10-hardcoding.md): Única fuente de verdad, derivación y portabilidad.
- [11 - Inyección y Gestión de Dependencias](docs/11-dependencias.md): Inversión de control, puertos y lockfiles.
- [12 - Code Smells y Refactorización Segura](docs/12-refactorizacion.md): Catálogo de smells y refactorización segura.
- [13 - Revisión de Código](docs/13-revision.md): Jerarquía de revisión, etiqueta y tamaño de PR.

---

## Ejemplos Ejecutables

El kit incluye ejemplos prácticos en Python con versiones antes/después y pruebas que demuestran la
aplicación concreta de cada principio. La documentación detallada de cada caso se encuentra en
[examples/README.md](examples/README.md).

```bash
python -m pip install --group dev
ruff check . && ruff format --check . && pytest
```

---

## Verificación de Estándares

La calidad de la documentación y la consistencia de formato se comprueban localmente con `markdownlint-cli2`:

```bash
npx -y markdownlint-cli2@0.18.1 "**/*.md"
```

El flujo de integración continua (CI) ejecuta adicionalmente el trabajo `python-examples`, verificando el
formato con Ruff, la suite de pruebas unitarias con Pytest y el umbral de complejidad ciclomática
(CC <= 5 fuera de anti-patrones intencionales) con Radon.
