import socket
import threading
import sys #para leer stdin
from cliente_controller import recibir_mensajes

#Creamos el socket cliente (con IPv4 y TCP)
socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Nos conectamos al servidor
IP_SERVIDOR = 'localhost' #el nombre o ip del servidor creado
PUERTO_SERVIDOR = 12345 #el puerto que pusimos al servidor

try:
    socket_cliente.connect((IP_SERVIDOR,PUERTO_SERVIDOR))#conectamos al servidor con el ip y el puerto correspondiente
    print("Conectando al servidor...\n")

    #ESperamos el mensaje del servidor (el que le pide su nombre)
    print(socket_cliente.recv(1024).decode('utf-8'), end='')
    
    #Input para ingresar el nombre, y le mandamos el dato al servidor
    nombre = input()
    socket_cliente.send(nombre.encode('utf-8'))

except Exception as e:
    print(f"No se pudo conectar al servidor: {e}")
    sys.exit()

hilo_recepcion = threading.Thread(target=recibir_mensajes, args=(socket_cliente,)) #funcion a ejecutar en el otro hilo, y parametros a recibir
hilo_recepcion.daemon = True #Marca que el hilo muera al terminar de ejecutarse
hilo_recepcion.start()

try:
    while True:

        texto = input()#leemos el texto del usuario
        if texto.strip().lower() == "/salir":
            print("Saliendo del chat...")
            socket_cliente.close() #cerramos el socket
            break
            
        else: #si no es /salir, entonces envia el mensaje
            try:
                socket_cliente.send(texto.encode('utf-8'))
            except:
                print('no se ha podido enviar el mensaje')
except:
    print("\nSaliendo del Chat...")
    socket_cliente.close()
    sys.exit()
