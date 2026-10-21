# Checklist Consolidada de Estándares de Código

Esta lista de verificación condensada permite auditar el diseño, implementación, pruebas y revisión de cualquier
base de código. Diseñada para imprimirse o utilizarse como plantilla de seguimiento en revisiones técnicas y auditorías,
agrupa las reglas fundamentales de ingeniería por fases del ciclo de desarrollo.

---

## 1. Diseño (Docs 01 - 04)

- [ ] **Solución Directa**: La solución es la más directa y legible para los requerimientos actuales (doc 01)
- [ ] **Cero Anticipación**: No se incorporan abstracciones ni parámetros para casos hipotéticos (doc 01)
- [ ] **Cambio Mínimo**: Modificaciones acotadas estrictamente al alcance sin alterar archivos ajenos (doc 01)
- [ ] **Responsabilidad de Módulo**: Cada módulo responde a una sola razón para cambiar en el dominio (doc 02)
- [ ] **Encapsulamiento**: La superficie pública está delimitada y oculta detalles internos (doc 02)
- [ ] **Grafo Acíclico**: El grafo de dependencias entre módulos es estrictamente acíclico (DAG) (doc 02)
- [ ] **Límites de Monolito**: Funciones, clases, archivos y módulos bajo los umbrales definidos (doc 02)
- [ ] **Dirección hacia el Dominio**: Las dependencias apuntan exclusivamente hacia el núcleo de dominio (doc 03)
- [ ] **Dominio Libre de I/O**: Entidades y reglas de dominio libres de operaciones de entrada y salida (doc 03)
- [ ] **Composition Root**: El ensamblado e instanciación de dependencias ocurre en el punto de entrada (doc 03)
- [ ] **Responsabilidad Única (SRP)**: Cada clase responde a una sola responsabilidad y razón de cambio (doc 04)
- [ ] **Sustitución de Liskov (LSP)**: Las subclases respetan precondiciones e invariantes del supertipo (doc 04)
- [ ] **Inversión de Dependencias (DIP)**: Dependencias inyectadas en el constructor mediante abstracciones (doc 04)

---

## 2. Implementación (Docs 05, 06, 09, 10, 11)

- [ ] **Complejidad Ciclomática**: Complejidad ciclomática CC <= 5 por función, con límite estricto de 10 (doc 05)
- [ ] **Cláusulas de Guarda**: Precondiciones validadas al inicio de la función para evitar anidamientos (doc 05)
- [ ] **Separación Consulta-Comando**: Consultas sin efectos colaterales y mutaciones sin retorno de cálculo (doc 05)
- [ ] **Nombres Intencionales**: Identificadores en inglés con verbos en funciones y sustantivos en clases (doc 06)
- [ ] **Predicados Booleanos**: Variables booleanas formuladas como predicados interrogativos (is_, has_, can_) (doc 06)
- [ ] **Cero Código Muerto**: Eliminación de código comentado y comentarios enfocados en explicar el porqué (doc 06)
- [ ] **Validación en Frontera**: Entradas externas analizadas hacia tipos inmutables en los bordes (doc 09)
- [ ] **Prohibición de Silenciamiento**: Cero capturas vacías (pass) y captura de fallas recuperables (doc 09)
- [ ] **Causa Raíz Preservada**: Traducción de excepciones preservando el rastreo con raise from (doc 09)
- [ ] **Fuente Única de Verdad**: Todo concepto de dominio, formato o estado posee un único punto canónico (doc 10)
- [ ] **Derivación Dinámica**: Valores dependientes derivados del origen canónico y rutas con Path (doc 10)
- [ ] **Cero Secretos en Código**: Ausencia total de credenciales, tokens o direcciones de red incrustadas (doc 10)
- [ ] **Inyección de Dependencias**: Dependencias recibidas por constructor o parámetro sin singletons (doc 11)
- [ ] **Aislamiento de Paquetes Externos**: Librerías externas volátiles encapsuladas tras puertos (doc 11)
- [ ] **Archivos de Bloqueo**: Entornos reproducibles con versiones fijadas: lockfile o pins exactos (doc 11)

---

## 3. Tests (Docs 07 - 08)

- [ ] **Disciplina Red-Green-Refactor**: Cada funcionalidad o corrección inicia con una prueba unitaria roja (doc 07)
- [ ] **Refactorización sobre Verde**: La reestructuración de código se ejecuta con las pruebas pasando (doc 07)
- [ ] **Comportamiento Observable**: Pruebas sobre contratos públicos sin acceder a estado privado (doc 07)
- [ ] **Pirámide de Pruebas**: Prioridad de pruebas unitarias rápidas e integración con Arrange-Act-Assert (doc 08)
- [ ] **Fakes sobre Mocks**: Preferencia por dobles en memoria (Fakes) frente a simulación interna con mocks (doc 08)
- [ ] **Determinismo sin Esperas**: Cero retardos fijos (sleep); tiempo y aleatoriedad inyectados (doc 08)

---

## 4. Refactor y Revisión (Docs 12 - 13)

- [ ] **Pruebas de Caracterización**: Comportamiento congelado con pruebas antes de iniciar reestructuración (doc 12)
- [ ] **Commits Atómicos**: Pasos pequeños preservando comportamiento, separados de cambios de negocio (doc 12)
- [ ] **DRY con Criterio**: Aplicación de la regla de tres antes de abstraer, tolerando duplicación accidental (doc 12)
- [ ] **Auto-Revisión del Autor**: Verificación del diff propio, suite en verde, PR < 400 líneas y docs al día (doc 13)
- [ ] **Jerarquía de Revisión**: Priorización de correctitud, diseño, legibilidad, pruebas y seguridad (doc 13)
- [ ] **Severidad en Comentarios**: Observaciones técnicas despersonalizadas y con severidad explícita (doc 13)

---

## Matriz de Evaluación por Fase

| Fase | Foco Técnico Principal | Criterio de Cumplimiento |
| :--- | :--- | :--- |
| **Diseño** | Modularidad, contratos y aislamiento de dominio | Grafos acíclicos y dominio puro sin I/O (docs 01-04) |
| **Implementación** | Complejidad acotada, nombres, tipado y SSOT | CC <= 5, fail-loud, cero hardcoding e inyección (docs 05, 06, 09, 10, 11) |
| **Tests** | TDD, pirámide de pruebas y determinismo | Ciclo Red-Green, Fakes en memoria y cero sleep (docs 07, 08) |
| **Refactor y Revisión** | Pasos seguros, code smells y revisión de pares | Pruebas de caracterización, commits atómicos y PRs < 400 líneas (docs 12, 13) |
