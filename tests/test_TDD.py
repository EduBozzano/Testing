import pytest 
from unittest.mock import MagicMock
from servidor_controller import nombre_disponible

def test_nombre_duplicado():
    socket1 = MagicMock()
    clientes = {socket1: "Carlos"}
    
    assert nombre_disponible("Juan", clientes) is True

    clientes["socket1"] = "Juan"

    assert nombre_disponible("Juan", clientes) is False
    