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
@click.option("--port", type=int, help="Puerto SSH")
@click.option("--user", help="Usuario SSH")
@click.option("--key-file", type=click.Path(exists=True), help="Archivo de clave privada SSH")
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
    """Copiar archivos/directorios usando diferentes protocolos"""
    
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
