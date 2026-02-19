import socket, threading, time, pytest
from servidor_chat import iniciar_servidor
from cliente_controller import recibir_mensajes

HOST = 'localhost'
PUERTO = 12345

def test_clientes_interactuan():
    """
    Prueba de integración:
    - Levanta servidor real
    - Conecta dos clientes
    - Uno envía mensaje
    - El otro lo recibe
    """

    stop_event = threading.Event()
    print("Intenta iniciar server")
    # Iniciar servidor en hilo
    server_thread = threading.Thread(
        target=iniciar_servidor,
        args=(HOST, PUERTO, stop_event,),
        daemon=True
    )
    server_thread.start()

    # Esperar que el servidor arranque
    time.sleep(1)

    # Crear clientes reales
    cliente1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    cliente1.connect((HOST, PUERTO))
    cliente2.connect((HOST, PUERTO))

    # Recibir mensaje de solicitud de nombre
    cliente1.recv(1024)
    cliente1.send(b"Juan")
    

    cliente2.recv(1024)
    cliente2.send(b"Ana")

    time.sleep(0.5)

    # Enviar mensaje desde cliente1
    cliente1.send(b"Hola Ana")

    time.sleep(0.5)

    # Cliente2 debería recibir el mensaje
    mensaje_recibido = cliente2.recv(1024).decode("utf-8")

    assert "Hola Ana" in mensaje_recibido

    # Cerrar servidor
    stop_event.set()
    server_thread.join(timeout=2)

    cliente1.close()
    cliente2.close()

def test_desconexion_abrupta():
    stop_event = threading.Event()
    print("Intenta iniciar server")
    # Iniciar servidor en hilo
    server_thread = threading.Thread(
        target=iniciar_servidor,
        args=(HOST, PUERTO, stop_event,),
        daemon=True
    )
    server_thread.start()

    # Esperar que el servidor arranque
    time.sleep(1)

    # Cliente A
    cliente_a = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente_a.connect((HOST, PUERTO))
    cliente_a.sendall(b"Alice")

    # Cliente B
    cliente_b = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente_b.connect((HOST, PUERTO))
    cliente_b.sendall(b"Bob")

    time.sleep(1)

    # Cliente A se desconecta abruptamente
    cliente_a.close()

    time.sleep(0.5)

    # Cliente B intenta enviar mensaje después de que A murió
    try:
        cliente_b.sendall(b"Hola despues de desconexion")
    except Exception as e:
        pytest.fail(f"El cliente B no deberia fallar: {e}")

    time.sleep(0.5)

    # Intentamos recibir algo para verificar que sigue conectado
    try:
        cliente_b.settimeout(1)
        cliente_b.recv(1024)
    except socket.timeout:
        pass  # es válido que no llegue nada
    except Exception as e:
        pytest.fail(f"Cliente B no deberia desconectarse: {e}")

    cliente_b.close()

    # Cerrar servidor
    stop_event.set()
    server_thread.join(timeout=2)