import socket, select, signal, threading
from typing import Dict
from servidor_controller import cerrar_servidor, broadcast, remover_clientes, nombre_disponible

def iniciar_servidor(host = 'localhost', puerto = 12345, stop_event=None):
    # Registrar señal SOLO si estamos en el hilo principal
    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGINT, lambda sig, frame: cerrar_servidor(socket_servidor, clientes)) #esto captura el Ctrl + C para cerrar de manera adecuada el servidor

    #Creamos un socket servidor            #AF_INET Define la creacion del socket con el protocolo IPv4
    socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#SOCK_STEAM es para crear el socket con el protocolo TCP

    # Permitir reutilizar el puerto inmediatamente tras cerrar el servidor
    socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                                                        
    #Lo asociamos a un host y puerto
    socket_servidor.bind((host,puerto)) #bind espera una tupla

    #ponerlo para que escuche
    socket_servidor.listen()
    print("\nServidor Activo")

    #ahora hacemos la logica para que se pueda aceptar a los cientes que tienen mensajes por enviar
    clientes: Dict[socket.socket, str] = {} #Definimos la lista de clientes
    nombres_pendientes = [] #sockets que aun no enviaron su nombre 

    while not (stop_event and stop_event.is_set()):

        sockets_activos = [socket_servidor] + list(clientes.keys()) + nombres_pendientes #Definimos una lista de sockets activos

        #con select, seleccionamos solo los sockets que tienen datos listos para enviar (mensajes)
        try:
            sockets_listos, _, _ = select.select(sockets_activos, [], [], 1) #dentro del parentesis es (revisa si los sockets tienen datos, revisa si se puede escribir en el socket, revisa si el socket tiene errores, tiempo a esperar)
        except ValueError:
            break

        for sock in sockets_listos:
            if sock is socket_servidor:
                #quiere decir que un nuevo cliente esta intentando conectarse
                socket_cliente, cliente_direccion = socket_servidor.accept()
                print(f"nuevo cliente conectado desde {cliente_direccion}")
                #pedimos el nombre al cliente
                socket_cliente.send("Ingrese su nombre: ".encode('utf-8'))
                #agregamos al cliente en la lista de nombres pendientes para esperar recibir el nombre y no bloquear la ejecucion
                nombres_pendientes.append(socket_cliente)
            elif sock in nombres_pendientes:
                #Este cliente no mando su nombre todavia
                nombre_bytes = sock.recv(1024)
                if not nombre_bytes:
                    remover_clientes(sock, clientes)
                    return
                    
                nombre = nombre_bytes.decode('utf-8').strip()
                while not nombre_disponible(nombre, clientes):
                    socket_cliente.send("Nombre ya en uso o invalido, pruebe con otro: ".encode('utf-8'))
                    nombre = sock.recv(1024).decode('utf-8').strip()
                    
                if nombre:
                    #agregamos el socket y el nombre al diccionario clientes
                    clientes[sock] = nombre
                    #removemos de nombres pendientes
                    nombres_pendientes.remove(sock)

                    #imprimimos mensajes de que se ha unido al chat
                    print(f"{nombre} se ha unido al chat")
                    broadcast(f"{nombre} se ha unido al chat", None, clientes)

                    #mensaje de bienvenida al usuario
                    mensaje_bienvenida = "\nBienvenido al chat!!\n".encode('utf-8')
                    socket_cliente.send(mensaje_bienvenida)
            else:
                #quiere decir que un cliente envio un mensaje
                try:
                    mensaje_bytes = sock.recv(2024)
                    if not mensaje_bytes:
                        remover_clientes(sock, clientes)
                        return

                    mensaje = mensaje_bytes.decode('utf-8').strip() #rev recibe y lee el mensaje, el 1024 indica la cantidad de bytes hasta donde se puede leer
                    #el decode, decodifica el mensaje que se recibio en bytes, a tex
                    if mensaje: #si el mensaje contiene datos
                        broadcast(mensaje, sock, clientes)
                    else: # si no, el cliente se desconecto
                        remover_clientes(sock, clientes)
                except:
                    remover_clientes(sock, clientes)
                    continue

if __name__ == "__main__":
    iniciar_servidor()