#! python3.4
import paho.mqtt.client as mqtt
import time
import json
import threading
import logging
import RPi.GPIO as GPIO
from pymongo import MongoClient

broker="10.129.0.15"
#broker="10.0.0.21"
port =1883
ssl_port=8883 #ssl
value = ''
num = 0 

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
control_pins = [4,17,27,22]
Connected = True
Connected2 = True

server_ip = '10.129.0.15'
#server_ip = '10.0.0.21'

client = MongoClient(server_ip, 27017)
print (client)
db = client['proyecto']

GPIO.setup(5,GPIO.IN)
GPIO.setup(6,GPIO.IN)

Normal_connections=1
SSL_Connections=0 #no ssl connections illustration only
#message="test message"
topic="candado/slot0/set"
topic2="viaje/bici1"
out_queue=[] #use simple array to get printed messages in some form of order

#######################MOTOR DE PASOS#####################################
for pin in control_pins:
  GPIO.setup(pin, GPIO.OUT)
  GPIO.output(pin, 0)

def motor_open():
	
	global control_pins	
	  
	halfstep_seq = [
	  [1,0,0,0],
	  [1,1,0,0],
	  [0,1,0,0],
	  [0,1,1,0],
	  [0,0,1,0],
	  [0,0,1,1],
	  [0,0,0,1],
	  [1,0,0,1]
	]

	if GPIO.input(5):
		for i in range(310):
			for halfstep in range(8):
				for pin in range(4):
					GPIO.output(control_pins[pin], halfstep_seq[halfstep][pin])
				time.sleep(0.001)
		
			
def motor_close():
	
	global control_pins
		
	halfstep_seq_rev = [
		[1,0,0,1],
		[0,0,0,1],
		[0,0,1,1],
		[0,0,1,0],
		[0,1,1,0],
		[0,1,0,0],
		[1,1,0,0],
		[1,0,0,0]
	]	

	if GPIO.input(6):
		for i in range(310):
			for halfstep in range(8):
				for pin in range(4):
					GPIO.output(control_pins[pin], halfstep_seq_rev[halfstep][pin])
				time.sleep(0.001)

###########################################################################################
def get_user_input():
	global value
	value = input()
	print(value)
	
def on_message(client, userdata, msg):

	x = msg.payload.decode()
	y = msg.topic
	print(x)
	print(y)
	 
	print("llego")
	if x == 'OFF':
		motor_open()
		buscar_viaje()	
	if x == 'ON':
		motor_close()
			
def buscar_viaje():
	global db
	global num
	print ('entro a la funcion para buscar viaje')
	num=0
	i=0
	for i in db.viajeactuals.find({}):
		if i['viaje'] > num:
			num = i['viaje']
	print (num)	
	
def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        client.subscribe(topic)
    else:
        print("Bad connection Returned code=",rc)
        client.loop_stop()
        
def on_disconnect(client, userdata, rc):
   pass
   #print("client disconnected ok")
   
   
def on_publish(client, userdata, mid):
   time.sleep(1)
   print("In on_pub callback mid= "  ,mid)


def Create_connections(nclients,port,SSL_Flag=False):
	
   for i in range(nclients):
      if SSL_Flag:
         cname ="python-ssl"+str(i)
      else:
         cname ="python-"+str(i)
      client = mqtt.Client(cname)             #create new instance

      if SSL_Flag:
         client.tls_set('c:/python34/steve/MQTT-demos/certs/ca-pi.crt')
      #client.connected_flag=False #create flag in client

      client.connect(broker,port)           #establish connection
      #client.on_log=on_log #this gives getailed logging
      client.on_connect = on_connect
      client.on_disconnect = on_disconnect
      #client.on_publish = on_publish
      clients.append(client)
      client.loop_start()
      while not client.connected_flag:
         time.sleep(0.05)


mqtt.Client.connected_flag=False #create flag in class
clients=[]
no_threads=threading.active_count()
print("current threads =",no_threads)
print("Creating Normal Connections ",Normal_connections," clients")
Create_connections(Normal_connections,port,False)

if SSL_Connections!=0:
   print("Creating SSL Connections ",SSL_Connections," clients")
   Create_connections(SSL_Connections,ssl_port,True)


print("All clients connected ")
time.sleep(5)

count =0
no_threads=threading.active_count()
print("current threads =",no_threads)
print("Publishing ")

Run_Flag=True
def main():
	global num
	global value
	aux = 0
	aux2 = 0 
	try:
		while Run_Flag:
			for client in clients:
				if GPIO.input(6) and aux==0:
					client.publish(topic,"off",qos=0,retain=True)
					print("enviando off")
					aux=1
				time.sleep(1)
					
				if GPIO.input(5) and aux2==0:
					client.publish(topic,"on",qos=0,retain=True)
					print("enviando on")
					aux2=1
				time.sleep(1)
				
				if GPIO.input(6) == 0:
					aux = 0
				if GPIO.input(5) == 0:
					aux2 = 0
				client.on_message = on_message
				if num !=0:
					time.sleep(1)
					client.publish(topic2,num,qos=0,retain=True)
					buscar_viaje()
					num =0
		  
	except KeyboardInterrupt:
	   print("interrupted  by keyboard")

	#client.loop_stop() #stop loop
	for client in clients:
	   client.disconnect()
	   client.loop_stop()
	   
	#allow time for allthreads to stop before existing
	time.sleep(10)


#************INCIALIZANDO LOS HILOS***********
hilo1 = threading.Thread(target=main)
hilo1.start()

