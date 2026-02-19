"""Interfaz de línea de comandos (CLI) para CopyWay.

Este módulo implementa la interfaz CLI usando Click, manejando argumentos,
opciones y orquestando la ejecución de protocolos de copia.
"""

import click
import logging
from pathlib import Path
from .protocols import ProtocolFactory
from .config import Config
from .exceptions import CopyWayError
from .utils.logger import logger, setup_logger


@click.command()
@click.option("-p", "--protocol", type=click.Choice(ProtocolFactory.list_protocols()), required=True, help="Protocolo de copia")
@click.option("--config", type=click.Path(exists=True), help="Archivo de configuración")
@click.option("--dry-run", is_flag=True, help="Simular sin ejecutar")
@click.option("--verbose", "-v", is_flag=True, help="Modo verbose")
@click.option("--port", type=int, help="Puerto SSH/SFTP")
@click.option("--user", help="Usuario SSH/SFTP")
@click.option("--password", help="Password para SFTP")
@click.option("--key-file", type=click.Path(exists=True), help="Archivo de clave privada SSH/SFTP")
@click.option("--compress", is_flag=True, help="Comprimir transferencia SSH")
@click.option("--replication", type=int, help="Factor de replicación HDFS")
@click.option("--overwrite", is_flag=True, help="Sobrescribir archivos existentes")
@click.option("--permission", help="Permisos HDFS (ej: 755)")
@click.option("--preserve-metadata", is_flag=True, default=True, help="Preservar metadata (local)")
@click.option("--follow-symlinks", is_flag=True, help="Seguir symlinks (local)")
@click.option("--progress/--no-progress", default=True, help="Mostrar progreso")
@click.argument("source")
@click.argument("destination")
def main(protocol, source, destination, config, dry_run, verbose, progress, **options):
    """Copiar archivos/directorios usando diferentes protocolos.
    
    CopyWay soporta múltiples protocolos de transferencia con validación
    completa y modo dry-run para simular operaciones.
    
    Args:
        protocol (str): Protocolo a usar (local, ssh, sftp, hdfs)
        source (str): Ruta de origen
        destination (str): Ruta de destino
        config (str): Ruta a archivo de configuración YAML
        dry_run (bool): Si True, simula sin ejecutar
        verbose (bool): Si True, activa logging detallado
        progress (bool): Si True, muestra barra de progreso
        **options: Opciones específicas del protocolo
    
    Examples:
        $ copyway -p local /origen /destino
        $ copyway -p sftp --password secret archivo.txt user@host:/ruta/
        $ copyway -p ssh --dry-run archivo.txt user@host:/ruta/
    
    Raises:
        click.Abort: Si ocurre algún error durante la ejecución
    """
    
    if verbose:
        setup_logger(level=logging.DEBUG)
    
    try:
        cfg = Config(config)
        protocol_config = cfg.get_protocol_config(protocol)
        
        protocol_instance = ProtocolFactory.create(protocol, protocol_config)
        
        # Filtrar opciones None
        filtered_options = {k: v for k, v in options.items() if v is not None}
        
        # Validar siempre (incluso en dry-run)
        if protocol == "local":
            if progress and not dry_run:
                with click.progressbar(length=1, label="Validando") as bar:
                    protocol_instance.validate(source, destination)
                    bar.update(1)
            else:
                click.echo("Validando...")
                protocol_instance.validate(source, destination)
                click.secho("✓ Validación exitosa", fg="green")
        
        if dry_run:
            click.echo(f"\n[DRY-RUN] Operación que se ejecutaría:")
            click.echo(f"  Protocolo: {protocol}")
            click.echo(f"  Origen: {source}")
            click.echo(f"  Destino: {destination}")
            if filtered_options:
                click.echo(f"  Opciones: {filtered_options}")
            click.secho("\n✓ Dry-run completado. No se copiaron archivos.", fg="yellow")
            return
        # Ejecutar copia con progress
        if progress and protocol == "local":
            with click.progressbar(length=1, label="Copiando") as bar:
                protocol_instance.copy(source, destination, **filtered_options)
                bar.update(1)
        else:
            protocol_instance.copy(source, destination, **filtered_options)
        
        click.secho(f"✓ Copia completada: {source} -> {destination}", fg="green")
        
    except CopyWayError as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        raise click.Abort()
    except Exception as e:
        logger.exception("Error inesperado")
        click.secho(f"✗ Error inesperado: {e}", fg="red", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
