# CopyWay

[![Tests](https://github.com/fgomezotero/copyway/workflows/Tests/badge.svg)](https://github.com/fgomezotero/copyway/actions)
[![Coverage](https://img.shields.io/badge/coverage-77%25-brightgreen)](https://github.com/fgomezotero/copyway)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

CLI para copiar archivos y directorios usando diferentes protocolos (local, SSH, SFTP, HDFS).

## 🚀 Características

- **Múltiples protocolos**: Local, SSH, SFTP, HDFS
- **Progress bar en tiempo real**: Tracking con porcentaje, velocidad y bytes transferidos
- **Validación completa**: Permisos, espacio en disco, conectividad
- **Dry-run mode**: Simula operaciones sin ejecutar
- **Configuración flexible**: Archivo YAML o línea de comandos
- **Extensible**: Plugin system para protocolos personalizados
- **Tests**: 77% cobertura con 43 tests

## 📦 Instalación

```bash
# Con Poetry
poetry install

# Con pip
pip install -e .
```

## 🎯 Uso

### Sintaxis General
```bash
copyway -p <protocolo> [opciones] <origen> <destino>
```

### Protocolo Local
```bash
copyway -p local /origen/archivo.txt /destino/
copyway -p local --follow-symlinks /origen/carpeta /destino/
```

### Protocolo SSH
```bash
copyway -p ssh archivo.txt usuario@servidor:/ruta/
copyway -p ssh --port 2222 --key-file ~/.ssh/id_rsa archivo.txt servidor:/ruta/
```

### Protocolo SFTP
```bash
# Con usuario en la ruta
copyway -p sftp --password secret archivo.txt usuario@servidor:/ruta/

# Con --user como fallback
copyway -p sftp --user admin --key-file ~/.ssh/id_rsa archivo.txt servidor:/ruta/

# Puerto personalizado
copyway -p sftp --port 2222 --password secret archivo.txt usuario@servidor:/ruta/
```

### Protocolo HDFS
```bash
copyway -p hdfs /local/archivo.txt /hdfs/ruta/
copyway -p hdfs --replication 3 --permission 755 archivo.txt /hdfs/ruta/
```

### Dry-run
Valida sin ejecutar:
```bash
copyway -p sftp --dry-run --password secret archivo.txt usuario@servidor:/ruta/
```

## ⚙️ Opciones

### Comunes
- `--dry-run`: Simular sin ejecutar
- `--verbose, -v`: Modo verbose
- `--config`: Archivo de configuración personalizado
- `--progress/--no-progress`: Mostrar/ocultar progreso

### SSH/SFTP
- `--port`: Puerto (default: 22)
- `--user`: Usuario (opcional si está en la ruta)
- `--password`: Password para SFTP
- `--key-file`: Archivo de clave privada
- `--compress`: Comprimir transferencia (solo SSH)

### HDFS
- `--replication`: Factor de replicación
- `--overwrite`: Sobrescribir archivos existentes
- `--permission`: Permisos (ej: 755)

### Local
- `--preserve-metadata`: Preservar metadata (default: true)
- `--follow-symlinks`: Seguir symlinks

## 📝 Configuración

Crear `~/.copyway.yml`:

```yaml
protocols:
  ssh:
    port: 22
    user: admin
    key_file: ~/.ssh/id_rsa
    compress: true
  
  sftp:
    port: 22
    user: admin
    key_file: ~/.ssh/id_rsa
    # password: "secret"  # Alternativa a key_file
  
  hdfs:
    replication: 3
    overwrite: false
    permission: "755"
```

**Seguridad**: Usa `key_file` en lugar de `password`. Si usas password:
```bash
chmod 600 ~/.copyway.yml
```

## 🧪 Desarrollo

### Setup
```bash
git clone https://github.com/fgomezotero/copyway.git
cd copyway
poetry install --with dev
```

### Tests
```bash
poetry run pytest --cov=copyway
```

### Linting
```bash
poetry run black copyway/
poetry run flake8 copyway/
```

## 🔌 Extensibilidad

```python
from copyway.protocols import ProtocolFactory
from copyway.protocols.base import Protocol

class S3Protocol(Protocol):
    def validate(self, source, destination, **options):
        return True
    
    def copy(self, source, destination, **options):
        # Implementación
        pass

ProtocolFactory.register("s3", S3Protocol)
```

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/AmazingFeature`
3. Commit: `git commit -m 'feat: add AmazingFeature'`
4. Push: `git push origin feature/AmazingFeature`
5. Abre un Pull Request

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para detalles.

## 📊 Estado

- ✅ Protocolo Local
- ✅ Protocolo SSH
- ✅ Protocolo SFTP (con progress bar)
- ✅ Protocolo HDFS (bidireccional)
- 🚧 Protocolo S3 (planeado)
- 🚧 Protocolo FTP (planeado)

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE)

## 👤 Autor

**Franklin Gomez Otero** - [@fgomezotero](https://github.com/fgomezotero)
