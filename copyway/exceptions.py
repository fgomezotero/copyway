class CopyWayError(Exception):
    """Base exception para copyway"""
    pass


class ProtocolError(CopyWayError):
    """Error en operación de protocolo"""
    pass


class ValidationError(CopyWayError):
    """Error de validación"""
    pass


class ConfigError(CopyWayError):
    """Error de configuración"""
    pass
