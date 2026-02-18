import pytest
import tempfile
from pathlib import Path
from copyway.config import Config
from copyway.exceptions import ConfigError


class TestConfig:
    def test_config_file_not_exists(self):
        config = Config("/nonexistent/config.yml")
        assert config.data == {}
    
    def test_config_load_valid_yaml(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("protocols:\n  ssh:\n    port: 2222\n")
            config_path = f.name
        
        config = Config(config_path)
        assert config.data["protocols"]["ssh"]["port"] == 2222
        Path(config_path).unlink()
    
    def test_config_get_existing_key(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("test_key: test_value\n")
            config_path = f.name
        
        config = Config(config_path)
        assert config.get("test_key") == "test_value"
        Path(config_path).unlink()
    
    def test_config_get_missing_key_with_default(self):
        config = Config("/nonexistent/config.yml")
        assert config.get("missing", "default") == "default"
    
    def test_config_get_protocol_config(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("protocols:\n  hdfs:\n    replication: 5\n")
            config_path = f.name
        
        config = Config(config_path)
        hdfs_config = config.get_protocol_config("hdfs")
        assert hdfs_config["replication"] == 5
        Path(config_path).unlink()
    
    def test_config_get_protocol_config_missing(self):
        config = Config("/nonexistent/config.yml")
        assert config.get_protocol_config("unknown") == {}
    
    def test_config_invalid_yaml(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("invalid: yaml: content:\n  - broken")
            config_path = f.name
        
        with pytest.raises(ConfigError):
            Config(config_path)
        
        Path(config_path).unlink()
