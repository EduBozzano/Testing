import socket
import select
import sys #para leer stdin

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

while True:

    #Revisamos la actividad, el socket y su entrada
    sockets_listos,_,_ = select.select([socket_cliente, sys.stdin], [], [])

    for sock in sockets_listos:
        if sock == socket_cliente:
            #Si el socket cliente tiene datos para mostrar lo guardamos
            mensaje = sock.recv(1024)
            if not mensaje: #si el mensaje esta vacio (0 bytes) entonces quiere decir que se cerro la conexion
                print("Servidor desconectado")
                socket_cliente.close()
                sys.exit()
            else: #si contiene algo, lo mostramos
                sys.stdout.write(mensaje.decode('utf-8'))
                sys.stdout.flush()
        else:
            #Si el cliente no tiene datos, quiere decir que escribio algo
            texto = sys.stdin.readline().rstrip('\n')#leemos el texto del usuario, stdin a diferencia de input, es mas rapido al ser de menor nivel
            if texto.strip().lower() == "/salir": #stdin lee con los caracteres \n, no los borra como input, entonces strip() quita los \n \t del comienzo y/o final del texto leido
                print("Saliendo del chat...")
                socket_cliente.close() #cerramos el socket
                sys.exit()
                
            else: #si no es /salir, entonces envia el mensaje
                try:
                    socket_cliente.send(texto.encode('utf-8'))
                except:
                    print('no se ha podido enviar el mensaje')

