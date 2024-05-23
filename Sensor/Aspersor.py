import zmq

def aspersor():
    contexto = zmq.Context()
    recibidor = contexto.socket(zmq.PULL)
    recibidor.bind("tcp://*:5557")  # Asume que se conecta a este puerto para escuchar señales de los sensores de humo

    print("Actuador aspersor listo para recibir señales.")

    while True:
        mensaje = recibidor.recv_string()
        print("Actuador aspersor activado debido a la detección de humo.")
 
aspersor()
