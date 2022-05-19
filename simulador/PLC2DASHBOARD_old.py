#!/usr/bin/python3
#coding=utf-8

''' este programa lee el fichero asociado, y cuando detecta un cambio envía el valor
a todos los nodos'''

import paho.mqtt.client as mqtt
import os, time
import sys
from libseedlingmodbus import SeedlingModbusClient
import libseedlingmodbus as lsmodb

###################################################################################################################

def on_message(client, userdata, message):
  try:
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
  except e:
    print("error con el mensaje")

broker_address="127.0.0.1" #"iot.eclipse.org"
print("creating new instance")
client_mqtt = mqtt.Client("P1") #create new instance mqtt.Client()
client_mqtt.on_message = on_message
print("connecting to broker")
client_mqtt.connect(broker_address, 1883, 60) #connect to broker
client_mqtt.loop_start() #start the loop

####################################################################################################################
args = sys.argv

modServerIp = "192.168.1.103"
modServerPort = 502 #5030

tcpipvals={"modServerIp":modServerIp,"modServerPort":modServerPort}

tcpipdict = tcpipvals
client_modbus = SeedlingModbusClient(tcpipdict["modServerIp"], tcpipdict["modServerPort"])
client_modbus.connect()


####################################################################################################################
#client_modbus.writecurrentASeedlings(0)
#client_modbus.writecurrentBSeedlings(0)
#client_modbus.writecurrentCSeedlings(0)

#####################################################################################################################


#client_mqtt.publish("robot/bandejas/alimentadora/bandejas","{}".format(client_modbus.getProcessedTrays()))
#client_mqtt.publish("robot/bandejas/alimentadora/porprocesar","{}".format(client_modbus.getclassifiedSeedlings()))
#client_mqtt.publish("robot/bandejas/claseA/cantidad","{}".format(client_modbus.getcurrentASeedlings()))
#client_mqtt.publish("robot/bandejas/claseB/cantidad","{}".format(client_modbus.getcurrentBSeedlings()))
#client_mqtt.publish("robot/bandejas/claseC/cantidad","{}".format(client_modbus.getcurrentCSeedlings()))
#client_mqtt.publish("robot/bandejas/claseA/bandejas", str(client_modbus.gettotalATrays()))
#client_mqtt.publish("robot/bandejas/claseB/bandejas", str(client_modbus.gettotalBTrays()))
#client_mqtt.publish("robot/bandejas/claseC/bandejas", str(client_modbus.gettotalCTrays()))

#leer_fichero_envia_topic()      #ENVIA TODA LA INFORMACION AL DASHBOARD

################################################################################
cont = 0
#moddate = os.stat(fichero)[8]

while 1:
  plcInstruction = client_modbus.getPLCInstruction()
  client_mqtt.publish("robot/bandejas/alimentadora/bandejas","{}".format(client_modbus.getProcessedTrays()))
  client_mqtt.publish("robot/bandejas/alimentadora/porprocesar","{}".format(client_modbus.getclassifiedSeedlings()))
  client_mqtt.publish("robot/bandejas/claseA/cantidad","{}".format(client_modbus.getcurrentASeedlings()))
  client_mqtt.publish("robot/bandejas/claseB/cantidad","{}".format(client_modbus.getcurrentBSeedlings()))
  client_mqtt.publish("robot/bandejas/claseC/cantidad","{}".format(client_modbus.getcurrentCSeedlings()))
  client_mqtt.publish("robot/bandejas/claseA/bandejas", str(client_modbus.gettotalATrays()))
  client_mqtt.publish("robot/bandejas/claseB/bandejas", str(client_modbus.gettotalBTrays()))
  client_mqtt.publish("robot/bandejas/claseC/bandejas", str(client_modbus.gettotalCTrays()))
  client_mqtt.publish("robot/vision/imagen1/ruta",str("planta1.jpg"))
  client_mqtt.publish("robot/vision/imagen2/ruta",str("planta2.jpg"))
  client_mqtt.publish("robot/vision/imagen3/ruta",str("planta3.jpg"))
  time.sleep(1)
  
  if plcInstruction == lsmodb.PLC_PROCODD_INST or plcInstruction == lsmodb.PLC_PROCEVEN_INST:
    print("ENVIANDO DATOS")

    client_mqtt.publish("robot/vision/imagen1/calidad",str(client_modbus.getSeedling1Quality()))
    client_mqtt.publish("robot/vision/imagen2/calidad",str(client_modbus.getSeedling2Quality()))
    client_mqtt.publish("robot/vision/imagen3/calidad",str(client_modbus.getSeedling3Quality()))
    time.sleep(5)
  '''
  if moddate != os.stat(fichero)[8]:
    cont = cont + 1
    moddate = os.stat(fichero)[8]
    print("cambio el fichero " + str(cont))
    leer_fichero_envia_topic()
  '''


