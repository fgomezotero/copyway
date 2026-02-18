# Guía de Contribución

¡Gracias por tu interés en contribuir a CopyWay!

## 🚀 Cómo Contribuir

### 1. Fork y Clone

```bash
git clone https://github.com/tu-usuario/copyway.git
cd copyway
```

### 2. Configurar Entorno

```bash
poetry install --with dev
```

### 3. Crear Rama

```bash
git checkout -b feature/mi-nueva-funcionalidad
```

### 4. Hacer Cambios

- Escribe código limpio y documentado
- Agrega tests para nuevas funcionalidades
- Mantén la cobertura de tests > 75%

### 5. Ejecutar Tests

```bash
poetry run pytest
poetry run pytest --cov=copyway
```

### 6. Commit

```bash
git add .
git commit -m "feat: descripción clara del cambio"
```

Usa prefijos convencionales:
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Documentación
- `test:` Tests
- `refactor:` Refactorización

### 7. Push y Pull Request

```bash
git push origin feature/mi-nueva-funcionalidad
```

Abre un Pull Request en GitHub con:
- Descripción clara del cambio
- Referencias a issues relacionados
- Screenshots si aplica

## 📋 Checklist

- [ ] Tests pasan (`pytest`)
- [ ] Cobertura > 75% (`pytest --cov`)
- [ ] Código formateado (`black copyway/`)
- [ ] Sin errores de linting (`flake8 copyway/`)
- [ ] Documentación actualizada
- [ ] CHANGELOG.md actualizado

## 🐛 Reportar Bugs

Usa GitHub Issues con:
- Descripción del problema
- Pasos para reproducir
- Comportamiento esperado vs actual
- Versión de Python y CopyWay
- Logs relevantes

## 💡 Sugerir Features

Abre un Issue con:
- Descripción de la funcionalidad
- Casos de uso
- Ejemplos de implementación

## 📝 Estilo de Código

- PEP 8
- Docstrings en funciones públicas
- Type hints cuando sea posible
- Nombres descriptivos

## ✅ Revisión

Los maintainers revisarán tu PR y pueden:
- Aprobar y mergear
- Solicitar cambios
- Discutir implementación

¡Gracias por contribuir! 🎉
