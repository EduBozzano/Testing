import socket
import threading
import time
from servidor_chat import iniciar_servidor
from cliente_controller import recibir_mensajes

host = 'localhost'
puerto = 12345

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
        args=(host, puerto, stop_event,),
        daemon=True
    )
    server_thread.start()

    # Esperar que el servidor arranque
    time.sleep(1)

    # Crear clientes reales
    cliente1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    cliente1.connect((host, puerto))
    cliente2.connect((host, puerto))

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
