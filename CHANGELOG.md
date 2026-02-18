# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [0.1.0] - 2024-01-15

### Agregado
- Protocolo de copia local con validaciones completas
- Protocolo SSH con soporte para puerto, usuario, clave privada y compresión
- Protocolo HDFS bidireccional (upload/download) con replicación y permisos
- Modo dry-run con validaciones completas
- Sistema de configuración YAML
- Logging detallado y configurable
- Progress feedback con barras de progreso
- Factory pattern para extensibilidad
- 43 tests unitarios con 77% de cobertura
- Documentación completa en README
- Ejemplos de uso y configuración

### Características
- Validación de source, destination, permisos y espacio en disco
- Manejo robusto de errores con excepciones personalizadas
- Soporte para archivos y directorios
- Opciones específicas por protocolo
- CLI intuitivo con Click

[0.1.0]: https://github.com/fgomezotero/copyway/releases/tag/v0.1.0
