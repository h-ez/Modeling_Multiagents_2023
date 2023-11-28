#Librerias para el archivo
import agentpy as ap
import numpy as np
import random
from owlready2 import *
from twilio.rest import Client
from dotenv import load_dotenv
import os
load_dotenv()

def camionDetectado(): #Cambiar esta funcion a la de Roboflow para detectar camiones
  numero_aleatorio_1 = random.random()
  numero_aleatorio_2 = random.random()

  if numero_aleatorio_1 >= numero_aleatorio_2:
    return True
  else:
     return False


class camara(ap.Agent):

  def setup(self, numerTrucks = 10):
    #Beliefs del agente

    self.detectCamion = False # Desires, contar los camiones detactados
    self.countTrucks = 0 # Intentions, cuantos camiones ha detectado
    self.totalTrucks = numerTrucks
    self.intentions = True #Intentions si quiere detectar camiones



  def see(self): # buscarMapa(self, x,y): funcion del grid, si es algo distinto a 0 hay un camion en su vista
    if camionDetectado(): #Enviar imagen a la funcion de camionDetected para que lo envie a roboflow
       self.brf()
     
    #Cambiar esto a que enc aso de que se detecte camion en el mapa


  def brf(self): #si detecta un camion su belief de ver camion cambia a true
    
    self.detectCamion = True
    self.options()


  def options(self): #si detecta camion y tiene la intencion de detectar va a dar la opcion de true
    if self.detectCamion == True and self.intentions == True:
      self.filter()
      return True
    
    else:
      return False

  def filter(self): #Si opciones da true, se detecta camion y esta la intencion de contar se llama a la acción
    if self.detectCamion and self.intentions: 
      """self.options() and""" 
      self.action()
      self.detectCamion = False


  def action(self): #Se cuenta el camion
    self.countTrucks = self.countTrucks + 1
 


class simulacion(ap.Model):

    def setup(self):
        """ Initialize the agents and network of the model. """

        # Create agents and network
        self.agents = ap.AgentList(self, self.p.numCamaras, camara)


    def step(self):
        """ Define the models' events per simulation step. """
        self.agents.see()

       

    def update(self):
        """"""
        total = 0
        for agentes in self.agents:
           total = total + agentes.countTrucks

        if total > self.p.totalTrucks:
           self.record('Camiones robados', total - self.p.totalTrucks)
           print('Camiones robados', total - self.p.totalTrucks)
           print("Camiones contados del camion 0 ",self.agents.countTrucks)
           print("Camiones pagados ",self.p.totalTrucks)
           print("Se estan robando")
        

    

    def end(self):
        """ Record evaluation measures at the end of the simulation. """

        # Record final evaluation measures
        print("Camiones contados totales ",self.agents.countTrucks)
        

def simi(numCam, pasos, total):
    parameters = {
        'numCamaras': numCam,
        'steps' : pasos,
        'totalTrucks' : total
    }

    model = simulacion(parameters)
    results = model.run()

    print(results)
    print(results.info)
    print(results.variables.simulacion)

    resultados = results.variables.simulacion.iloc[-1]
    resutadoFinal = resultados['Camiones robados']

    print(f"Se robaron {resutadoFinal} camiones")


    if resutadoFinal > 10:
        print("Se robaron más de 10")
        #enviarWhats()


def enviarWhats():
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    recipient_number = os.getenv('RECIPIENT_WHATSAPP_NUMBER')

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body='Estan robando el sitio',
        to=f'whatsapp:{recipient_number}'
    )

    print(message.sid)


numCamaras = 2
pasos = 30
numeroCamiones = 15

simi(numCamaras, pasos, numeroCamiones)