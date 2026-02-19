import pytest
from unittest.mock import MagicMock, patch
from servidor_controller import broadcast
from servidor_controller import remover_clientes
from servidor_controller import cerrar_servidor

def test_broadcast_envio_correcto():
    """
    Verifica que broadcast envía el mensaje
    a todos los clientes excepto al socket origen.
    """

    # Creamos sockets simulados
    socket_emisor = MagicMock()
    socket_cliente1 = MagicMock()
    socket_cliente2 = MagicMock()

    # Diccionario de clientes como en el servidor
    clientes = {
        socket_emisor: "Juan",
        socket_cliente1: "Ana",
        socket_cliente2: "Luis"
    }

    mensaje = "Hola a todos"

    # Ejecutamos la función
    broadcast(mensaje, socket_emisor, clientes)

    # El emisor NO debe recibir el mensaje
    socket_emisor.send.assert_not_called() #Verificar que el método send() nunca fue llamado.

    # Los demás sí deben recibirlo
    socket_cliente1.send.assert_called_once() #Verificar que send() fue llamado exactamente una vez.
    socket_cliente2.send.assert_called_once()

@patch("servidor_controller.remover_clientes")
def test_broadcast_fallo_cliente(mock_remover):
    """
    Verifica que si un cliente lanza excepción
    al enviar, el broadcast no colapsa.
    """

    socket_emisor = MagicMock()
    socket_ok = MagicMock()
    socket_falla = MagicMock()

    # Simulamos error en send
    socket_falla.send.side_effect = Exception("Error de envio")

    clientes = {
        socket_emisor: "Juan",
        socket_ok: "Ana",
        socket_falla: "Luis"
    }

    mensaje = "Mensaje prueba"

    # No debería lanzar excepción
    broadcast(mensaje, socket_emisor, clientes)

    socket_ok.send.assert_called_once()

def test_remover_cliente():
    socket_cliente = MagicMock()
    clientes = {socket_cliente: "Juan"}

    remover_clientes(socket_cliente, clientes)

    assert socket_cliente not in clientes
    socket_cliente.close.assert_called_once()

def test_cerrar_servidor_cierra_todo():
    socket_servidor = MagicMock()
    socket_cliente1 = MagicMock()
    socket_cliente2 = MagicMock()

    clientes = {
        socket_cliente1: "Ana",
        socket_cliente2: "Luis"
    }

    cerrar_servidor(socket_servidor, clientes)

    socket_cliente1.close.assert_called_once()
    socket_cliente2.close.assert_called_once()
    socket_servidor.close.assert_called_once()
