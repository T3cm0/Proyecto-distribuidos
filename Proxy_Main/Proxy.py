import zmq
import time
from collections import deque
import threading

# Configuración de ZeroMQ para recibir y enviar datos 
contexto = zmq.Context()
receptor = contexto.socket(zmq.PULL)
receptor.bind("tcp://10.43.100.232:5555") #De acuerdo a IP de las máquinas

cloud = contexto.socket(zmq.PUSH) #Comunicación con la nube
cloud.connect("tcp://10.43.103.126:5555") #De acuerdo a IP de la maquina

sc_fog = contexto.socket(zmq.PUSH)
sc_fog.connect("tcp://localhost:8080") 

# Deques para almacenar los datos
temperaturas = deque(maxlen=10)
humedades = deque(maxlen=10)
tiempos_temperaturas = deque(maxlen=10)

# Cantidad de mensajes recibidos
cantidad_mensajes = 0


# Escribe el mensaje recibido en un archivo (BD)
def escribir_mensaje(mensaje):
    with open("datos_sensores.txt", "a") as archivo:
        archivo.write(mensaje + "\n")

# Procesa cada mensaje recibido, asegurandose que esté completo, que el tipo de sensor sea correcto, y que los valores sean positivos
def procesar_mensaje(mensaje):
    
    global cantidad_mensajes
    cantidad_mensajes += 1
    
    try:
        partes = mensaje.split(', ')
        if len(partes) != 4:  # Validar la cantidad correcta de partes
            raise ValueError("Formato incorrecto")
        sensor_id, tipo, valor, timestamp = [parte.split(': ')[1] for parte in partes]

        if tipo not in ["temperatura", "humedad", "humo"]:  # Validar tipo de sensor
            raise ValueError("Tipo de sensor desconocido")
        
        # Validación para evitar valores negativos en temperatura y humedad
        if tipo in ["temperatura", "humedad"]:
            valor = float(valor)
            if valor < 0:
                raise ValueError("Valor negativo")
            
        # Lógica para temperatura
        if tipo == "temperatura":
            temperatura = float(valor)
            temperaturas.append(temperatura)
            tiempos_temperaturas.append(time.ctime(float(timestamp)))
            if temperatura > 29.4:  # Umbral de alerta de temperatura
                alerta = f"Alerta, alta temperatura: {temperatura} sensor: {sensor_id} a las {time.ctime(float(timestamp))}"
                cloud.send_string(alerta)
                sc_fog.send_string(alerta)
            
        # Lógica para humedad
        elif tipo == "humedad":
            humedad = float(valor)
            humedades.append(humedad)
            if humedad < 70:
                alerta = f"Alerta, baja humedad: {humedad} sensor: {sensor_id} a las {time.ctime(float(timestamp))}"
                cloud.send_string(alerta)
                sc_fog.send_string(alerta)
                
        # Lógica para humo
        elif tipo == "humo":
            humo = bool(valor)
            if (humo):
                alerta = f"Alerta, presencia de humo: {humo} sensor: {sensor_id} a las {time.ctime(float(timestamp))}"
                cloud.send_string(alerta)
                
                
        # Escribe las mediciones en el archivo
        escribir_mensaje(mensaje)
        
    except ValueError as e:
        print(f"Error al procesar el mensaje: {e}")
        return  

# Calcula el promedio de las temperaturas de los sensores e imprime sus tiempos
def calcular_promedio_temperatura():
    while True:
        if len(temperaturas) != 0:
            time.sleep(10)
            promedio_temp = sum(temperaturas) / len(temperaturas)
            if promedio_temp > 29.4:
                alerta = f"Alerta, temperatura promedio: {promedio_temp} a las {time.time()}"
                sc_fog.send_string(alerta)
            print(f"Promedio de temperatura: {promedio_temp}°")
            print("Tiempos registrados")
            for tiempo in tiempos_temperaturas:
                print(tiempo)
        
        
# Calcula el promedio de las humedades de los sensores y lo envia a cloud
def calcular_promedio_humedad():
    while True:
        if len(humedades) != 0:
            time.sleep(5)
            promedio_hum = sum(humedades) / len(humedades)
            mensaje = (f"Promedio, de humedad: {promedio_hum}")
            cloud.send_string(mensaje)
       
# Escribe la cantidad de mensajes recibidos
def escribir_cantidad_mensajes():
    while True:
        time.sleep(10)
        if cantidad_mensajes > 0:
            with open("cantidad_mensajes.txt", "a") as archivo:
                archivo.write("Cantidad de mensajes en proxy: "+ str(cantidad_mensajes) + "\n")

if __name__ == "__main__":
    threading.Thread(target=calcular_promedio_temperatura, daemon=True).start()
    threading.Thread(target=calcular_promedio_humedad, daemon=True).start()
    threading.Thread(target=escribir_cantidad_mensajes, daemon=True).start()
    try:
        while True:
            mensaje = receptor.recv_string()
            #print(f"Recibido: {mensaje}")
            procesar_mensaje(mensaje)
    except KeyboardInterrupt:
        print("\nFinalizando el proxy...")