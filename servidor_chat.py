import socket
import select
import sys
import signal
from typing import Dict

def broadcast(mensaje, socket_emisor):
    nombre_emisor = clientes.get(socket_emisor, "Servidor") #get obtiene el valor de socket emisor, y si es none, devuelve Servidor
    mensaje_final = f"{nombre_emisor}: {mensaje} \n"

    for cliente in list(clientes.keys()):
        if cliente != socket_emisor:#enviamos mensaje a todos los sockets, excepto al emisor
            try:
                cliente.send(mensaje_final.encode('utf-8'))
            except:
                #Si da error, el cliente se desconecto, entonces lo quitamos
                remover_clientes(cliente)

def remover_clientes(sock):
    if sock in clientes:
        nombre = clientes[sock] #guardamos el nombre de usuario del socket a eliminar para luego imprimirlo
        del clientes[sock] #eliminamos del diccionario el socket mandado

        print(f"{nombre} se ha desconectado.")
        broadcast(f"{nombre} ha salido del chat.\n", sock) #avisamos al chat que un usuario se desconecto
    try:
        sock.close() #cerramos el socket para liberar recursos
    except:
        pass #por si ya estaba cerrado

def cerrar_servidor(sig=None, frame=None):
    print("Cerrando servidor y desconectando clientes")
    #con el for desconectamos todos los clientes
    for cliente in list(clientes.keys()):
        cliente.close()
    
    #luego cerramos el servidor y salimos
    socket_servidor.close()
    sys.exit()

signal.signal(signal.SIGINT, cerrar_servidor) #esto captura el Ctrl + C para cerrar de manera adecuada el servidor

#Creamos un socket servidor            #AF_INET Define la creacion del socket con el protocolo IPv4
socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#SOCK_STEAM es para crear el socket con el protocolo TCP

# Permitir reutilizar el puerto inmediatamente tras cerrar el servidor
socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                                                    
#Lo asociamos a un host y puerto
socket_servidor.bind(('localhost',12345)) #bind espera una tupla

#ponerlo para que escuche
socket_servidor.listen()

#ahora hacemos la logica para que se pueda aceptar a los cientes que tienen mensajes por enviar
clientes: Dict[socket.socket, str] = {} #Definimos la lista de clientes
nombres_pendientes = [] #sockets que aun no enviaron su nombre 

while True:
    sockets_activos = [socket_servidor] + list(clientes.keys()) + nombres_pendientes #Definimos una lista de sockets activos

    #con select, seleccionamos solo los sockets que tienen datos listos para enviar (mensajes)
    sockets_listos, _, _ = select.select(sockets_activos, [], [], 1) #dentro del parentesis es (revisa si los sockets tienen datos, revisa si se puede escribir en el socket, revisa si el socket tiene errores, tiempo a esperar)

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
            nombre = sock.recv(1024).decode('utf-8').strip()
            if nombre:
                #agregamos el socket y el nombre al diccionario clientes
                clientes[sock] = nombre
                #removemos de nombres pendientes
                nombres_pendientes.remove(sock)

                #imprimimos mensajes de que se ha unido al chat
                print(f"{nombre} se ha unido al chat")
                broadcast(f"{nombre} se ha unido al chat", None)

                #mensaje de bienvenida al usuario
                mensaje_bienvenida = "\nBienvenido al chat!!\n".encode('utf-8')
                socket_cliente.send(mensaje_bienvenida)
        else:
            #quiere decir que un cliente envio un mensaje
            mensaje = sock.recv(1024).decode('utf-8') #rev recibe y lee el mensaje, el 1024 indica la cantidad de bytes hasta donde se puede leer
            #el decode, decodifica el mensaje que se recibio en bytes, a tex        
            if mensaje: #si el mensaje contiene datos
                broadcast(mensaje, sock)
            else: # si no, el cliente se desconecto
                remover_clientes(sock)
   