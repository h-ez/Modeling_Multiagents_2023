#Librerias para el archivo
#pip install agentpy
#pip install owlready2
#pip install twilio
import agentpy as ap #Para los agentes y simulación 
#import numpy as np #Para ver los datos
import random #Para datos dummies
from owlready2 import * #Para ontologias
from twilio.rest import Client #Para enviar mensajes de whatsApp
from dotenv import load_dotenv #Para variables de entorno
import os


def camionDetectado(self): 
  #Cambiar esta funcion a la API de Roboflow para detectar camiones, que regrese True si se detecta camión
  numero_aleatorio_1 = random.random()
  numero_aleatorio_2 = random.random()

  if numero_aleatorio_1 >= numero_aleatorio_2:
    return True
  else:
     return False


class camara(ap.Agent): #Agente camara

  def setup(self):
    #Beliefs del agente

    self.detectCamion = False # Desires, contar los camiones detactados
    self.countTrucks = 0 # Intentions, cuantos camiones ha detectado
    self.totalTrucks = self.model.p.totalTrucks #El numero de camiones que han pagado
    self.intentions = True #Intentions si quiere detectar camiones
    self.conteoTotal = 0 #Conteo total de camiones de todos los agentes/camaras



  def see(self): #Ver en el mapa (Imagen/Video) si hay un camión a la vista
    if camionDetectado(self): #Enviar imagen a la funcion de camionDetected para que lo envie a roboflow
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


    def step(self):#En cada paso los agentes miran si detectan un camión
        self.agents.see()


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
    '''
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    message = client.messages.create(
    from_='whatsapp:+14155238886',
    body=mensajeEnviar,
    to= os.getenv('RECIPIENT_WHATSAPP_NUMBER_STEFANO')
    )

    print(message.sid)'''

    print("Mensajes de whatsApp")
    print(mensajeEnviar)


numCamaras = 4 #el numero de camaras/carpetas de imagenes
pasos = 8 #numero de iteraciones de los agentes, se cambia al numero de fotos a analizar
numeroCamiones = 15 #Camiones que pagaron

simi(numCamaras, pasos, numeroCamiones)