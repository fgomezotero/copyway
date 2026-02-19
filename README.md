# CopyWay

[![Tests](https://github.com/fgomezotero/copyway/workflows/Tests/badge.svg)](https://github.com/fgomezotero/copyway/actions)
[![Coverage](https://img.shields.io/badge/coverage-77%25-brightgreen)](https://github.com/fgomezotero/copyway)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

CLI para copiar archivos y directorios usando diferentes protocolos (local, SSH, SFTP, HDFS).

## 🚀 Características

- ✅ **Múltiples protocolos**: Local, SSH, SFTP, HDFS
- ✅ **Progress bar en tiempo real**: Tracking completo con SFTP (porcentaje, velocidad, bytes)
- ✅ **Validación completa**: Permisos, espacio en disco, conectividad
- ✅ **Dry-run mode**: Simula operaciones sin ejecutar
- ✅ **Configuración flexible**: Archivo YAML
- ✅ **Logging detallado**: Debug y auditoría
- ✅ **Progress feedback**: Barras de progreso
- ✅ **Extensible**: Plugin system para protocolos personalizados
- ✅ **Tests**: 77% cobertura con 43 tests

## 📦 Instalación

```bash
# Con Poetry
poetry install

# O con pip
pip install -e .
```

## 🎯 Inicio Rápido

### Protocolo Local
```bash
# Local → Local (archivo)
copyway -p local /origen/archivo.txt /destino/archivo.txt

# Local → Local (directorio)
copyway -p local /origen/carpeta /destino/carpeta
```

### Protocolo SSH
```bash
# Local → Remoto
copyway -p ssh archivo.txt usuario@servidor:/ruta/destino/

# Remoto → Local
copyway -p ssh usuario@servidor:/ruta/archivo.txt /local/destino/

# Remoto → Remoto (mismo servidor)
copyway -p ssh usuario@servidor:/origen/archivo.txt usuario@servidor:/destino/
```

### Protocolo SFTP
```bash
# Local → Remoto (con progress bar en tiempo real)
copyway -p sftp archivo.txt usuario@servidor:/ruta/destino/

# Remoto → Local
copyway -p sftp usuario@servidor:/ruta/archivo.txt /local/destino/

# Con autenticación
copyway -p sftp --key-file ~/.ssh/id_rsa archivo.txt usuario@servidor:/ruta/
copyway -p sftp --password mipassword archivo.txt usuario@servidor:/ruta/
```

### Protocolo HDFS
```bash
# Local → HDFS
copyway -p hdfs /local/archivo.txt /hdfs/ruta/destino/

# HDFS → Local
copyway -p hdfs /hdfs/ruta/archivo.txt /local/destino/

# HDFS → HDFS
copyway -p hdfs /hdfs/origen/archivo.txt /hdfs/destino/
```

## ⚙️ Opciones Avanzadas

### SSH
```bash
copyway -p ssh --port 2222 --user admin --key-file ~/.ssh/id_rsa --compress archivo.txt servidor:/ruta/
```

### SFTP
```bash
# Con progress bar en tiempo real
copyway -p sftp --port 2222 --user admin --key-file ~/.ssh/id_rsa archivo.txt servidor:/ruta/

# Con password
copyway -p sftp --password mipassword archivo.txt usuario@servidor:/ruta/
```

### HDFS
```bash
copyway -p hdfs --replication 3 --overwrite --permission 755 archivo.txt /hdfs/ruta/
```

### Local
```bash
copyway -p local --follow-symlinks --preserve-metadata /origen /destino
```

## 🔍 Dry-run

Simula la operación **validando todo** (permisos, conectividad, espacio) sin copiar archivos:

```bash
# Valida source existe, destination tiene permisos, espacio suficiente
copyway -p local --dry-run /origen /destino

# Valida conectividad SSH antes de copiar
copyway -p ssh --dry-run archivo.txt usuario@servidor:/ruta/

# Valida que hdfs está disponible
copyway -p hdfs --dry-run /local/file.txt /hdfs/path/
```

**Validaciones en dry-run:**
- ✅ Source existe y es accesible
- ✅ Destination tiene permisos de escritura
- ✅ Espacio en disco suficiente (local)
- ✅ Conectividad SSH (ssh)
- ✅ Comando hdfs disponible (hdfs)

## 📝 Configuración

Crear archivo `~/.copyway.yml`:

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
  hdfs:
    replication: 3
    overwrite: false
```

## 🔌 Extensibilidad

Registrar protocolos personalizados:

```python
from copyway.protocols import ProtocolFactory
from copyway.protocols.base import Protocol

class S3Protocol(Protocol):
    def validate(self, source, destination):
        return True
    
    def copy(self, source, destination, **options):
        # Implementación
        pass

ProtocolFactory.register("s3", S3Protocol)
```

## 🧪 Desarrollo

### Instalación para desarrollo

```bash
git clone https://github.com/fgomezotero/copyway.git
cd copyway
poetry install --with dev
```

### Usando Conda

```bash
# Crear entorno conda
conda create -n copyway python=3.10 -y
conda activate copyway

# Instalar dependencias
pip install -e ".[dev]"

# O con Poetry
pip install poetry
poetry install --with dev
```

### Ejecutar tests

```bash
# Con Poetry
poetry install --with dev
poetry run pytest
poetry run pytest --cov=copyway

# Con Conda
conda activate copyway
pytest
pytest --cov=copyway

# O con pip
pip install -e ".[dev]"
pytest
pytest --cov=copyway
```

### Linting y formato

```bash
poetry run black copyway/
poetry run flake8 copyway/
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.

## 📄 Licencia

Distribuido bajo la licencia MIT. Ver `LICENSE` para más información.

## 👤 Autor

**Franklin Gomez Otero**

- GitHub: [@fgomezotero](https://github.com/fgomezotero)

## 🙏 Agradecimientos

- Click - Framework CLI
- PyYAML - Parsing de configuración
- Pytest - Testing framework

## 📊 Estado del Proyecto

- ✅ Protocolo Local: Completo
- ✅ Protocolo SSH: Completo
- ✅ Protocolo SFTP: Completo (con progress bar en tiempo real)
- ✅ Protocolo HDFS: Completo (bidireccional)
- 🚧 Protocolo S3: Planeado
- 🚧 Protocolo FTP: Planeado
