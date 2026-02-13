def recibir_mensajes(socket_cliente):
    while True:
        try:
            #Si el socket cliente tiene datos para mostrar lo guardamos
            mensaje = socket_cliente.recv(1024)
            if not mensaje: #si el mensaje esta vacio (0 bytes) entonces quiere decir que se cerro la conexion
                print("Servidor desconectado")
                socket_cliente.close()
                break
            else: #si contiene algo, lo mostramos
                print("\n" + mensaje.decode('utf-8'))
        except:
            print("\nError en la conexión.")
            socket_cliente.close()
            break