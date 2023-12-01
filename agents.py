#Librerias para el archivo
#pip install agentpy
#pip install owlready2
#pip install twilio
#pip install roboflow
import agentpy as ap #Para los agentes y simulación 
#import numpy as np #Para ver los datos
import random #Para datos dummies
from owlready2 import * #Para ontologias
from twilio.rest import Client #Para enviar mensajes de whatsApp
from dotenv import load_dotenv #Para variables de entorno
from roboflow import Roboflow #Para la API de Roboflow
import os

# Initialize Roboflow model
load_dotenv()
rf = Roboflow(api_key=os.getenv('ROBOFLOW_API_KEY'))
project = rf.workspace().project("tc2008")
model = project.version(1).model


def camionDetectado(self, camera_id, current_step): 
    # Mapping camera_id to directory names
    camera_dirs = {1: "camera1Images", 2: "camera2Images", 3: "camera3Images"}
    camera_dir = camera_dirs.get(camera_id)
    print(f"Folder: {camera_dir}")
    if camera_dir is None:
        print(f"Invalid camera ID: {camera_id}")
        return False

    image_file = f"{current_step}.png"
    image_path = os.path.join(camera_dir, image_file)

    # Check if the file exists and process it
    if os.path.isfile(image_path):
        json_output = model.predict(image_path, confidence=70, overlap=30).json()
        for prediction in json_output['predictions']:
            if prediction['class'] == 'full_truck':
                print(f"Full truck found in {image_file} in directory {camera_dir}: {prediction}")
                return True  # Return True as soon as a full_truck is detected

    return False  # Return False if the file doesn't exist or no full_truck is detected


class camara(ap.Agent): #Agente camara
  def setup(self):
    #Beliefs del agente
    self.detectCamion = False # Desires, contar los camiones detactados
    self.countTrucks = 0 # Intentions, cuantos camiones ha detectado
    self.totalTrucks = self.model.p.totalTrucks #El numero de camiones que han pagado
    self.intentions = True #Intentions si quiere detectar camiones
    self.conteoTotal = 0 #Conteo total de camiones de todos los agentes/camaras

  def see(self, current_step): #Ver en el mapa (Imagen/Video) si hay un camión a la vista
    if camionDetectado(self, self.id, current_step): #Enviar imagen a la funcion de camionDetected para que lo envie a roboflow
      self.communicate("Camion detectado por camara ", self.id) #Hablar con el resto de las camaras y avisarles de su avistamiento
      self.brf() #Cambiar las beliefs del agente

  def brf(self): #si detecta un camion su belief de ver camion cambia a true y ve sus opciones
    self.detectCamion = True
    self.options()

  def options(self): #si detecta camion y tiene la intencion de detectar va a dar la opcion de true y seguir al filtro
    if self.detectCamion == True and self.intentions == True:
      self.filter()
      return True
    else:
      return False

  def filter(self): #Si se detecta camion y esta la intencion de contar se llama a la acción
    if self.detectCamion and self.intentions: 
      self.action()
      self.detectCamion = False

  def action(self): #Se cuenta el camion, se vota si reportarlo
    self.countTrucks = self.countTrucks + 1
    self.votacion()
    self.conteoTotal = 0
    #enviarWhats(f"Se detecto robo por la camara {self.id}")
  
  def communicate(self, message, ids): #Comunicación entre agentes, el agente que detecte camión le avisa al resto de los agentes
    for agente in self.model.agents:#Se envia mensaje a todos menos a si mismo
      if self != agente:
        agente.receive_message(message, ids)

  def receive_message(self, message, id): #Metodo para recivir mensajes de otro agente
        print("")
        print(f"Agente {self.id} recibe el mensade: {message} del agente ", id)
        self.reply(id)
  
  def reply(self,ids):
    for agente in self.model.agents:
      if ids == agente.id:
        agente.receive_reply(self.countTrucks , self.id)

  def receive_reply(self, message, id): #Metodo para recivir mensajes de otro agente
        print("Reply del agente ", id," : ",message," camiones detectados")
        self.conteoTotal = self.conteoTotal + message

  def votacion(self):
    self.conteoTotal = self.conteoTotal + self.countTrucks
    eleccion = 1

    print("Conteo de camiones del agente ",self.id," : ",self.conteoTotal)

    if self.conteoTotal > self.totalTrucks: #Si el numero de camiones totales es mayor al esperado se manda votar
      print("Eleccion : el agente ",self.id," llama a votar, voto +")
      for agente in self.model.agents:#Se envia mensaje a todos menos a si mismo
        if self != agente:
          eleccion = eleccion + agente.votar()
      self.conteoTotal = 0

      if eleccion >= self.model.p.numCamaras/2:
        print("Se ha votado por que se reporte el robo")
        mensaje = "Se ha detectado un robo en la camara " + str(self.id)
        enviarWhats(mensaje)

      else:
        print("Se ha votado por no reportar el robo")
  
  def votar(self): #Se vota para reportar el robo
    if self.intentions:
      print("El agente ",self.id," vota +")
      return 1
    else:
       print("El agente ",self.id," vota -")
       return 0

class simulacion(ap.Model):

    def setup(self):#Set up de los agentes dentro de la simulacion
        # Create agents list
        self.agents = ap.AgentList(self, self.p.numCamaras, camara)
        self.current_step = 0  # Initialize step counter

    def step(self):#En cada paso los agentes miran si detectan un camión
      self.current_step += 1  # Increment step counter
      for agent in self.agents:
        agent.see(self.current_step)  # Pass the current step to the see method

    def update(self): #Por cada update se ve el numero de camiones detectados por camara
        camionesContados = 0
        total = 0
        for agentes in self.agents:
           camionesContados =  agentes.countTrucks
           total = total + camionesContados
           print("Total de camiones detectado por camara ",agentes.id," -> ",camionesContados )
        
        self.record('Camionestotales', total)             
          
    def end(self):#AL final de la evaluación se ve el numero de camiones contados por camara
      mensaje = "Reporte del día : "
      print("Camiones contados por agente durante la simulación")
      for agente in self.agents:
        mensaje = mensaje + " La camara "+str(agente.id)+" detecto "+str(agente.countTrucks)+" camiones. "
        print("La camara ",agente.id," detecto ",agente.countTrucks)
 
      enviarWhats(mensaje)

def simi(numCam, pasos, total):#Prep para la simulación
    parameters = { #Parametros de la simulación
        'numCamaras': numCam, #EL numero de camaras/agentes
        'steps' : pasos, #El numero de pasos a realizar
        'totalTrucks' : total #El numero de camiones pagados
    }

    model = simulacion(parameters)
    results = model.run()

    print(results)
    print(results.info)
    #print(results.variables.simulacion)

    resultados = results.variables.simulacion.iloc[-1]
    resutadoFinal = resultados['Camionestotales']
    enviarWhats(f"Se robaron {resutadoFinal-total} camiones")

def enviarWhats(mensajeEnviar): #No subir esto a github porque me dexean
    account_sid = 'AC7f1e0c3b454857c4c3937768d5eff2d3'
    auth_token = 'e29cf6ac1f18445ad26ae35a0b39a225'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
    from_='whatsapp:+14155238886',
    body=mensajeEnviar,
    to='whatsapp:+5214771811509'
    )

    print(message.sid)
    
    print("Mensajes de whatsApp")
    print(mensajeEnviar)

numCamaras = 3 #el numero de camaras/carpetas de imagenes
pasos = 40 #numero de iteraciones de los agentes, se cambia al numero de fotos a analizar
numeroCamiones = 4 #Camiones que pagaron

simi(numCamaras, pasos, numeroCamiones)