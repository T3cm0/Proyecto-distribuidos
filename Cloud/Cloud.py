import zmq
import threading
from collections import deque
import time

# Configuración de ZMQ para recibir y enviar datos
contexto = zmq.Context()
receptor = contexto.socket(zmq.PULL)
receptor.bind("tcp://10.43.103.126:5555") #ip de esta maquina donde le lleguen

sc_cloud = contexto.socket(zmq.PUSH)
sc_cloud.connect("tcp://localhost:5550")


# Deque para almacenar humedades
humedades = deque(maxlen=4)

# Cantidad de mensajes recibidos
cantidad_mensajes = 0

# Escribe la alerta recibida en un archivo (BD)
def escribir_alerta(alerta):
    with open("alertas.txt", "a") as archivo:
        archivo.write(alerta + "\n")

# Procesamiento de los mensajes recibidos
def procesar_mensaje(mensaje):
    
    global cantidad_mensajes
    
    cantidad_mensajes += 1
    
    partes = mensaje.split(',')
    if partes[0] == "Alerta":
        escribir_alerta(mensaje)
        
            
    elif partes[0] == "Promedio":
        humedad = float(mensaje.split(": ")[1])
        humedades.append(humedad)
        
# Escribe la cantidad de mensajes recibidos
def escribir_cantidad_mensajes():
    global cantidad_mensajes
    while True:
        time.sleep(10)
        if cantidad_mensajes > 0:
            with open("cantidad_mensajes.txt", "a") as archivo:
                archivo.write("Cantidad de mensajes en cloud: "+ str(cantidad_mensajes) + "\n")


# Calcula el promedio de humedad mensual
def calcular_promedio_humedad():
    while True:
        time.sleep(20)
        promedio_hum = sum(humedades) / len(humedades)
        if promedio_hum < 70:
            alerta = (f"Promedio de humedad bajo: {promedio_hum}")
            sc_cloud.send_string(alerta)
        print(f"Promedio, de humedad: {promedio_hum}")
        humedades.clear()
        
            
    
if __name__ == "__main__":
    threading.Thread(target=calcular_promedio_humedad, daemon=True).start()
    threading.Thread(target=escribir_cantidad_mensajes, daemon=True).start()
    try:
        while True:
            mensaje = receptor.recv_string()
            #print(f"Recibido: {mensaje}")
            procesar_mensaje(mensaje)
    except KeyboardInterrupt:
        print("\nFinalizando el proxy...")