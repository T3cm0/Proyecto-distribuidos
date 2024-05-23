import zmq
import threading
import time

cantidad_alertas = 0

def sistema_calidad():
    global cantidad_alertas
    
    # Configuración de la comunicación
    contexto = zmq.Context()
    
    recibidor = contexto.socket(zmq.PULL)
    recibidor.bind("tcp://*:8080")
    
    threading.Thread(target=escribir_alertas, daemon=True).start()
    threading.Thread(target=escribir_cantidad_mensajes, daemon=True).start()
    
    while True:
        mensaje = recibidor.recv_string()
        print(mensaje)
        cantidad_alertas += 1
  
def escribir_alertas():
    while True:
        time.sleep(10)
        if cantidad_alertas > 0:
            with open("cantidad_alertas.txt", "w") as archivo:
                archivo.write("Cantidad de alertas: "+ str(cantidad_alertas) + "\n")
                
def escribir_cantidad_mensajes():
    while True:
        time.sleep(10)
        if cantidad_alertas > 0:
            with open("cantidad_mensajes.txt", "a") as archivo:
                archivo.write("Cantidad de mensajes en sistema de calidad: "+ str(cantidad_alertas) + "\n")

sistema_calidad()