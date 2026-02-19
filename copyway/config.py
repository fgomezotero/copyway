"""Gestión de configuración para CopyWay.

Este módulo maneja la carga y acceso a la configuración desde archivos YAML.
Soporta configuración global y específica por protocolo.
"""

import os
import yaml
from pathlib import Path
from .exceptions import ConfigError


class Config:
    """Gestor de configuración YAML para CopyWay.
    
    Carga configuración desde archivo YAML y proporciona acceso a
    configuraciones globales y específicas por protocolo.
    
    Attributes:
        config_file (str): Ruta al archivo de configuración
        data (dict): Datos de configuración cargados
    
    Example:
        >>> config = Config()
        >>> ssh_config = config.get_protocol_config('ssh')
        >>> port = ssh_config.get('port', 22)
    """
    
    def __init__(self, config_file=None):
        """Inicializa el gestor de configuración.
        
        Args:
            config_file (str, optional): Ruta al archivo de configuración.
                Si no se especifica, usa COPYWAY_CONFIG env var o ~/.copyway.yml
        """
        self.config_file = config_file or os.getenv("COPYWAY_CONFIG", str(Path.home() / ".copyway.yml"))
        self.data = self._load()

    def _load(self):
        """Carga el archivo de configuración YAML.
        
        Returns:
            dict: Datos de configuración parseados o dict vacío si no existe
            
        Raises:
            ConfigError: Si hay error al parsear el archivo YAML
        """
        path = Path(self.config_file)
        if not path.exists():
            return {}
        try:
            with open(path) as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise ConfigError(f"Error cargando configuración: {e}")

    def get(self, key, default=None):
        """Obtiene un valor de configuración.
        
        Args:
            key (str): Clave de configuración
            default: Valor por defecto si la clave no existe
            
        Returns:
            Valor de configuración o default
        """
        return self.data.get(key, default)

    def get_protocol_config(self, protocol):
        """Obtiene configuración específica de un protocolo.
        
        Args:
            protocol (str): Nombre del protocolo (local, ssh, sftp, hdfs)
            
        Returns:
            dict: Configuración del protocolo o dict vacío
            
        Example:
            >>> config = Config()
            >>> ssh_config = config.get_protocol_config('ssh')
            >>> print(ssh_config.get('port', 22))
            22
        """
        return self.data.get("protocols", {}).get(protocol, {})
