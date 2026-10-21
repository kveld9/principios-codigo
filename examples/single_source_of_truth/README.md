# Única Fuente de Verdad (Single Source of Truth)

Este ejemplo demuestra cómo centralizar definiciones de dominio en un único origen autoritativo y resolver
rutas de almacenamiento de forma independiente del entorno.

## El Problema

En `before.py`, la lista de formatos soportados y sus extensiones se duplican manualmente a lo largo de cuatro
funciones distintas. Además, las rutas de acceso a archivos emplean rutas absolutas fijadas al directorio
de un usuario local (`/home/developer/.config/app`), lo que rompe la portabilidad entre entornos y vuelve
frágiles las pruebas automatizadas.

## Qué Cambió

En `after.py`, se refactoriza el diseño aplicando una única fuente de verdad y desacoplamiento ambiental:

- **Enum `DocumentFormat`**: actúa como origen autoritativo del cual se derivan dinámicamente extensiones y tipos MIME.
- **Precedencia de configuración**: `resolve_storage_dir` resuelve respetando la jerarquía `defaults < env < explícito`.
- **Rutas portables (`pathlib.Path`)**: eliminación de rutas fijas; las operaciones aceptan directorios inyectables.

## Qué Demuestran las Pruebas

El archivo `test_single_source_of_truth.py` valida la derivación dinámica de formatos a partir del enum,
comprueba los tres niveles de precedencia de configuración empleando `monkeypatch` y verifica la escritura
y lectura determinista de documentos mediante directorios temporales aislados (`tmp_path`).
