import pytest
import tempfile
from pathlib import Path
from click.testing import CliRunner
from copyway.cli import main


class TestCLI:
    def test_cli_local_copy(self):
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "source.txt"
            src.write_text("test content")
            dest = Path(tmpdir) / "dest.txt"
            
            result = runner.invoke(main, ['-p', 'local', str(src), str(dest)])
            
            assert result.exit_code == 0
            assert dest.exists()
            assert "Copia completada" in result.output
    
    def test_cli_dry_run(self):
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "source.txt"
            src.write_text("test")
            dest = Path(tmpdir) / "dest.txt"
            
            result = runner.invoke(main, ['-p', 'local', '--dry-run', str(src), str(dest)])
            
            assert result.exit_code == 0
            assert "DRY-RUN" in result.output
            assert not dest.exists()
    
    def test_cli_verbose(self):
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "source.txt"
            src.write_text("test")
            dest = Path(tmpdir) / "dest.txt"
            
            result = runner.invoke(main, ['-p', 'local', '-v', str(src), str(dest)])
            
            assert result.exit_code == 0
    
    def test_cli_source_not_exists(self):
        runner = CliRunner()
        
        result = runner.invoke(main, ['-p', 'local', '/nonexistent/file.txt', '/tmp/dest.txt'])
        
        assert result.exit_code == 1
        assert "Error" in result.output
    
    def test_cli_invalid_protocol(self):
        runner = CliRunner()
        
        result = runner.invoke(main, ['-p', 'invalid', 'source.txt', 'dest.txt'])
        
        assert result.exit_code != 0
    
    def test_cli_missing_protocol(self):
        runner = CliRunner()
        
        result = runner.invoke(main, ['source.txt', 'dest.txt'])
        
        assert result.exit_code != 0
    
    def test_cli_with_config(self):
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "source.txt"
            src.write_text("test")
            dest = Path(tmpdir) / "dest.txt"
            
            config = Path(tmpdir) / "config.yml"
            config.write_text("protocols:\n  local:\n    preserve_metadata: true\n")
            
            result = runner.invoke(main, ['-p', 'local', '--config', str(config), str(src), str(dest)])
            
            assert result.exit_code == 0
