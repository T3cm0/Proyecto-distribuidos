import zmq
import time
import random
import threading
import argparse
import socket


#Porcentajes de funcionalidad de los sensores
proba_correcto = 0
proba_fuera_rango = 0
proba_error = 0

cont_total=0
cont_correcto = 0
cont_fuera_rango = 0
cont_error = 0


# Guardar indicador la ip del proxy actual
indicador = 0


# Lectura del archivo de configuración
def Config_Sensor_Archivo(nombreArchivo):
    with open(nombreArchivo, 'r') as archivo:
        print("Leyendo el archivo " + nombreArchivo)
        proba_correcto = float(archivo.readline().strip())
        proba_fuera_rango = float(archivo.readline().strip())
        proba_error = float(archivo.readline().strip())
    return proba_correcto, proba_fuera_rango, proba_error

#Sensor de humo
def Sensor_Humo(sensor_id):
    contexto = zmq.Context()
    proxy = contexto.socket(zmq.PUSH)
    proxy.connect("tcp://localhost:5555")
    
    proxy_alt = contexto.socket(zmq.PUSH)
    proxy_alt.connect("tcp://localhost:5555") #"tcp://10.43.103.60:5555"
    
    
    # Conexión para enviar mensaje a aspersor
    aspersor = contexto.socket(zmq.PUSH)
    aspersor.connect("tcp://localhost:5557")
    
    sistema_calidad = contexto.socket(zmq.PUSH)
    sistema_calidad.connect("tcp://localhost:5550") 
    
    global indicador
    
    while True:
        detecta_humo = random.choice([True, False])  # Simula la detección de humo de manera aleatoria
        timestamp = time.time()
        mensaje = (f"sensor_id: {sensor_id}, tipo: humo, valor: {detecta_humo}, timestamp: {timestamp}")
        if indicador == 0:
            proxy.send_string(mensaje)
            print("tcp://localhost:5555") 
        else:
            proxy_alt.send_string(mensaje)
            print("tcp://localhost:5555") #"tcp://10.43.103.60:5555"
            
        if (detecta_humo): 
            alerta = f"Alerta, deteccion de humo sensor: {sensor_id} a las {time.ctime(float(timestamp))}"
            sistema_calidad.send_string(alerta) # Envia mensaje al sistema de calidad
            aspersor.send_string("Humo") # Envia mensaje al aspersor
        #print(f"Enviado: {mensaje}")
        time.sleep(3)  # Cada 3 segundos

#Sensor de temperatura
def Sensor_Temperatura(sensor_id):
    contexto = zmq.Context()
    proxy = contexto.socket(zmq.PUSH)
    proxy.connect("tcp://localhost:5555")
    
    proxy_alt = contexto.socket(zmq.PUSH)
    proxy_alt.connect("tcp://localhost:5555") #"tcp://10.43.103.60:5555"
    
    global cont_total
    global cont_correcto
    global cont_fuera_rango
    global cont_error
    global indicador
    
    while True:
        temperatura = 0
        #Cambiar de acuerdo a los procentajes   
        probabilidades = [proba_correcto, proba_fuera_rango, proba_error ]    
        evento = random.choices([0,1,2], probabilidades)[0]   
        #Valor correcto
        if evento == 0:
            temperatura = random.uniform(11, 29.4)
            cont_total += 1
            cont_correcto += 1
        #Valor fuera de rango    
        elif evento == 1:
            temperatura = random.uniform(29.5, 38)
            cont_total += 1
            cont_fuera_rango += 1
        #Valor error
        elif evento == 2:
            temperatura = random.uniform(-10,-1)
            cont_total += 1
            cont_error += 1
    
        #print(f"Temperatura: {temperatura}")
        #print(f"Total: {cont_total}")
        #print(f"Correcto: {cont_correcto}, Fuera de rango: {cont_fuera_rango}, Error: {cont_error}")
        timestamp = time.time()
        mensaje = (f"sensor_id: {sensor_id}, tipo: temperatura, valor: {temperatura}, timestamp: {timestamp}")
        if indicador == 0:
            proxy.send_string(mensaje)
            print("tcp://localhost:5555")
        else:
            proxy_alt.send_string(mensaje)
            print("tcp://localhost:5555") #"tcp://10.43.103.60:5555"
            
        #print(f"Enviado: {mensaje}")
        time.sleep(6)  # Cada 6 segundos 

#Sensor de humedad
def Sensor_Humedad(sensor_id):
    contexto = zmq.Context()
    proxy = contexto.socket(zmq.PUSH)
    proxy.connect("tcp://localhost:5555")
    
    proxy_alt = contexto.socket(zmq.PUSH)
    proxy_alt.connect("tcp://localhost:5555") 
    
    global cont_total
    global cont_correcto
    global cont_fuera_rango
    global cont_error
    global indicador
    while True:
        humedad = 0
        #Cambiar de acuerdo a los procentajes
        probabilidades = [proba_correcto, proba_fuera_rango, proba_error ]    
        evento = random.choices([0,1,2], probabilidades)[0]
        #Valor Correcto
        if evento == 0:
            humedad = random.uniform(70, 100)
            cont_total += 1
            cont_correcto += 1
        #Valor fuera de rango
        elif evento == 1:
            humedad = random.uniform(0,69)
            cont_total += 1
            cont_fuera_rango += 1
        #Valor error
        elif evento == 2:
            humedad = random.uniform(-10,-1)
            cont_total += 1
            cont_error += 1
        
        #print(f"Humedad: {humedad}")
        #print(f"Total: {cont_total}")
        #print(f"Correcto: {cont_correcto}, Fuera de rango: {cont_fuera_rango}, Error: {cont_error}")
        timestamp = time.time()
        mensaje = (f"sensor_id: {sensor_id}, tipo: humedad, valor: {humedad}, timestamp: {timestamp}")
        if indicador == 0:
            proxy.send_string(mensaje)
            print("tcp://localhost:5555")
        else:
            proxy_alt.send_string(mensaje)
            print("tcp://localhost:5555") 
            
        #print(f"Enviado: {mensaje}")
        time.sleep(5)  # Cada 5 segundos según el ejemplo

#Creación de hilos
def Tipo_Sensor(tipo):
    if tipo == 0: #Sensor de humo
        for i in range(0, 10):
            threading.Thread(target=Sensor_Humo, args=(i+1,)).start()
    elif tipo == 1: #Sensor de temperatura
        for i in range(10, 20):
            threading.Thread(target=Sensor_Temperatura, args=(i+1,)).start()
    elif tipo == 2: #Sensor de humedad
        for i in range(20, 30):
            threading.Thread(target=Sensor_Humedad, args=(i+1,)).start()


# Healthcheck
def healthcheck():
    global indicador
    ip_main = "1localhost"
    puerto = 5555
    try:
        with socket.create_connection((ip_main, puerto), timeout=10) as sock:
            indicador = 0
            return True
    except (socket.timeout, socket.error):
        indicador = 1
        return False

# Revisa conexión con proxy
def revisar_proxy():
    while True:
        healthcheck()

if __name__ == "__main__":
    print("Inicializando")
    threading.Thread(target=revisar_proxy, daemon=True).start()
    entrada = argparse.ArgumentParser("Inicializar sensor")
    entrada.add_argument("-t", "--tipo", choices=[0,1,2], type=int, help="Tipo de sensor")
    entrada.add_argument("-a", "--archivo", type=str, help="Archivo de configuración")
    args = entrada.parse_args()
    proba_correcto, proba_fuera_rango, proba_error = Config_Sensor_Archivo(args.archivo)
    Tipo_Sensor(args.tipo)
    
    