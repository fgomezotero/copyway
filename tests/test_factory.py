import pytest
from copyway.protocols import ProtocolFactory
from copyway.protocols.local import LocalProtocol
from copyway.exceptions import ProtocolError


def test_create_local_protocol():
    protocol = ProtocolFactory.create("local")
    assert isinstance(protocol, LocalProtocol)


def test_create_unknown_protocol():
    with pytest.raises(ProtocolError):
        ProtocolFactory.create("unknown")


def test_list_protocols():
    protocols = ProtocolFactory.list_protocols()
    assert "local" in protocols
    assert "ssh" in protocols
    assert "hdfs" in protocols


def test_register_custom_protocol():
    class CustomProtocol:
        def __init__(self, config=None):
            pass
    
    ProtocolFactory.register("custom", CustomProtocol)
    protocol = ProtocolFactory.create("custom")
    assert isinstance(protocol, CustomProtocol)
