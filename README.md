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
│   └── README.md                     # Descripción general y mapa de componentes
│
├── Configuración del Entorno
│   ├── .editorconfig                 # Reglas de formato, indentación y codificación
│   ├── .gitattributes                # Normalización forzada de finales de línea a LF
│   ├── .gitignore                    # Reglas de exclusión para SO, entornos y Python
│   └── .markdownlint.yaml            # Reglas de validación estática para Markdown
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

---

## Verificación de Estándares

La calidad de la documentación y la consistencia de formato se comprueban localmente con `markdownlint-cli2`:

```bash
npx -y markdownlint-cli2@0.18.1 "**/*.md"
```
