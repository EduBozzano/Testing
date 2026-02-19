import sys
import socket
from typing import Dict

def broadcast(mensaje, socket_emisor, clientes: Dict[socket.socket, str]):
    nombre_emisor = clientes.get(socket_emisor, "Servidor") #get obtiene el valor de socket emisor, y si es none, devuelve Servidor
    mensaje_final = f"{nombre_emisor}: {mensaje} \n"

    for cliente in list(clientes.keys()):
        if cliente != socket_emisor:#enviamos mensaje a todos los sockets, excepto al emisor
            try:
                cliente.send(mensaje_final.encode('utf-8'))
            except:
                #Si da error, el cliente se desconecto, entonces lo quitamos
                remover_clientes(cliente, clientes)

def remover_clientes(sock, clientes: Dict[socket.socket, str]):
    if sock in clientes:
        nombre = clientes[sock] #guardamos el nombre de usuario del socket a eliminar para luego imprimirlo
        del clientes[sock] #eliminamos del diccionario el socket mandado

        print(f"{nombre} se ha desconectado.")
        broadcast(f"{nombre} ha salido del chat.\n", sock, clientes) #avisamos al chat que un usuario se desconecto
    try:
        sock.close() #cerramos el socket para liberar recursos
    except:
        pass #por si ya estaba cerrado

def cerrar_servidor(socket_servidor, clientes: Dict[socket.socket, str]):
    print("Cerrando servidor y desconectando clientes")
    #con el for desconectamos todos los clientes
    for cliente in list(clientes.keys()):
        cliente.close()
    
    #luego cerramos el servidor y salimos
    socket_servidor.close()
    try:
        sys.exit()
    except:
        print("Sistema Cerrado Correctamente")