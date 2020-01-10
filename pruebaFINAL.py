import paho.mqtt.client as mqttClient
import time

import RPi.GPIO as GPIO
import sys

GPIO.setwarnings(False) 
'''
################PRUEBA CON LEDS######################3
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(18,GPIO.OUT)

print("LED on")
GPIO.output(17,GPIO.HIGH)
time.sleep(1)
print("LED off")
GPIO.output(17,GPIO.LOW)
print("LED on")
GPIO.output(18,GPIO.HIGH)
time.sleep(1)
print("LED off")
GPIO.output(18,GPIO.LOW)


'''		


###################CONEXION MQTT############################## 
def get_user_input():
	global value
	
	hid = { 4: 'a', 5: 'b', 6: 'c', 7: 'd', 8: 'e', 9: 'f', 10: 'g', 11: 'h', 12: 'i', 13: 'j', 14: 'k', 15: 'l', 16: 'm', 17: 'n', 18: 'o', 19: 'p', 20: 'q', 21: 'r', 22: 's', 23: 't', 24: 'u', 25: 'v', 26: 'w', 27: 'x', 28: 'y', 29: 'z', 30: '1', 31: '2', 32: '3', 33: '4', 34: '5', 35: '6', 36: '7', 37: '8', 38: '9', 39: '0', 44: ' ', 45: '-', 46: '=', 47: '[', 48: ']', 49: '\\', 51: ';' , 52: '\'', 53: '~', 54: ',', 55: '.', 56: '/'  }

	hid2 = { 4: 'A', 5: 'B', 6: 'C', 7: 'D', 8: 'E', 9: 'F', 10: 'G', 11: 'H', 12: 'I', 13: 'J', 14: 'K', 15: 'L', 16: 'M', 17: 'N', 18: 'O', 19: 'P', 20: 'Q', 21: 'R', 22: 'S', 23: 'T', 24: 'U', 25: 'V', 26: 'W', 27: 'X', 28: 'Y', 29: 'Z', 30: '!', 31: '@', 32: '#', 33: '$', 34: '%', 35: '^', 36: '&', 37: '*', 38: '(', 39: ')', 44: ' ', 45: '_', 46: '+', 47: '{', 48: '}', 49: '|', 51: ':' , 52: '"', 53: '~', 54: '<', 55: '>', 56: '?'  }

	fp = open('/dev/hidraw0', 'rb')
	
	ss = ""
	shift = False

	done = False
	
	while not done:

		## Get the character from the HID
		buffer = fp.read(8)
		for c in buffer:
			if c > 0:

				##  40 is carriage return which signifies
				##  we are done looking for characters
				if int(c) == 40:
					done = True
					break;

				##  If we are shifted then we have to 
				##  use the hid2 characters.
				if shift: 

					## If it is a '2' then it is the shift key
					if int(c) == 2 :
						shift = True

					## if not a 2 then lookup the mapping
					else:
						ss += hid2[ int(ord(c)) ]
						shift = False

				##  If we are not shifted then use
				##  the hid characters

				else:

					## If it is a '2' then it is the shift key
					if int(c) == 2 :
						shift = True

					## if not a 2 then lookup the mapping
					else:
						ss += hid[ int(c) ]
				
	value = ss
	print(value)
	
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    #else:
	#	print("Connection failed")
 
Connected = False   #global variable for the state of the connection

#broker_address= "10.129.0.118" 
broker_address= "10.0.0.21"
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
	while(1):
		get_user_input()
		if value:
			client.publish("matricula/estacion1/mat/set",value,qos=2)
			value = ""
			print("entro al lector")

		#client.disconnect()
		#client.loop_forever()
	 
except KeyboardInterrupt:
 
    client.disconnect()
    client.loop_stop()


