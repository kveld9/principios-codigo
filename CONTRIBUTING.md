# Guía de Contribución

Normas técnicas y de ingeniería para contribuir a este kit de principios de código.

---

## Principios de Colaboración

- **Unidad lógica por commit**: Cada commit debe representar un cambio atómico e independiente.
  No se deben agrupar correcciones no relacionadas, formateos masivos ni múltiples características
  en un único commit.
- **Conventional Commits**: Los mensajes deben seguir la especificación
  [Conventional Commits](https://www.conventionalcommits.org/) (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`).
  El mensaje se redacta en inglés, en modo imperativo y sin emojis.
- **Sincronización de documentación**: Cualquier modificación que altere comportamiento, interfaces,
  configuraciones o ejemplos debe actualizar la documentación afectada en el mismo commit.
- **Prohibición de emojis**: No se admiten emojis en código fuente, scripts, configuraciones, flujos de CI,
  nombres de archivos ni mensajes de commit.
- **Redacción impersonal**: La prosa debe emplear voz técnica e impersonal, evitando la primera persona del plural.

---

## Verificación Local de Markdown

Antes de enviar cambios, se debe ejecutar la validación estática de Markdown con la configuración del repositorio:

```bash
npx -y markdownlint-cli2@0.18.1 "**/*.md"
```

El comando debe concluir con código de salida `0` sin advertencias ni errores.

---

## Ramas, Pull Requests y Releases

Las directrices detalladas sobre ramas (Trunk-Based Development), preparación de Pull Requests,
políticas de merge y gobierno de versiones se gestionan de forma centralizada en el repositorio hermano
[principios-git](https://github.com/kveld9/principios-git). Dicho estándar rige el flujo de trabajo en Git.
