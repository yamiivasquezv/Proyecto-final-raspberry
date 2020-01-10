import paho.mqtt.client as mqttClient
import time

import RPi.GPIO as GPIO
import sys
from pymongo import MongoClient
import datetime
import serial
import time
import pynmea2


sys.path.append('/home/pi/MFRC522-python')
from mfrc522 import SimpleMFRC522
reader = SimpleMFRC522()
global value

#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(6,GPIO.IN)
GPIO.setup(31,GPIO.IN)
GPIO.setup(29,GPIO.IN)


server_ip = '10.129.0.15'
#server_ip = '10.0.0.21'

client = MongoClient(server_ip, 27017)
print (client)
db = client['proyecto']
	
#############RFID READER######################################

def rfid_reader():
	global value
	var = False 
	print("Hold a tag near the reader")

	try:
		id, text = reader.read()
		print(id)
		value = id
		print(value)
		print(text)

	except KeyboardInterrupt:
		print("interrupted  by keyboard")
		
		
	return value 
	
def publicar_bd():
	global db
	slotestados = db.slotestados
	bicicletas = db.bicicletas

	result = slotestados.find_one_and_update({'slot':'slot0'},{'$set': {'rfid': value,'estado':'ocupado'}})
	result2= bicicletas.find_one_and_update({'ident':'bici1'},{'$set': {'estado':'disponible'}})
		
#################MOTOR PASOS##################################
		
		
###################CONEXION MQTT############################## 
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    #else:
	#	print("Connection failed")
 
Connected = False   #global variable for the state of the connection
 
broker_address= "10.129.0.15"
#broker_address= "10.0.0.21"

port = 1883
#user = "yamilkav"
#password = "Proyectofinal"
 
client = mqttClient.Client()               #create new instance
#client.username_pw_set(user, password=password)    #set username and password
client.on_connect= on_connect                      #attach function to callback
client.connect(broker_address, port=port)          #connect to broker
 
client.loop_start()        #start the loop
 
while Connected != True:    #Wait for connection
    time.sleep(0.1)
 
try:
	cnt = 0
	while(1):
		
		#if GPIO.input(29):
		#	client.publish("candado/slot0/set","OFF")
			
		detect_rfid = rfid_reader()
		if detect_rfid != None and cnt == 0:
			print ("entro en el primer if")
			time.sleep(5)
			detect_rfid2 = rfid_reader()
			if detect_rfid2 != None:
				print ("entro en el segundo if")
				time.sleep(2)
				client.publish("candado/slot0/set","ON")
				publicar_bd()
				print("enviando on rfid a base de datos")
				cnt = 1
				time.sleep(1)
					
		elif GPIO.input(31) and cnt != 0:
			cnt = 0
			print ('el cnt es 0')
			
		
			
			
		time.sleep(1)
		#client.disconnect()
		#client.loop_forever()
	 
except KeyboardInterrupt:
 
    client.disconnect()
    client.loop_stop()
    GPIO.cleanup()	

