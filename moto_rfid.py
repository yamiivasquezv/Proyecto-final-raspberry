#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
control_pins = [4,17,27,22]

GPIO.setup(5,GPIO.IN)
GPIO.setup(6,GPIO.IN)

for pin in control_pins:
  GPIO.setup(pin, GPIO.OUT)
  GPIO.output(pin, 0)

import sys
sys.path.append('/home/pi/MFRC522-python')
from mfrc522 import SimpleMFRC522

#from pymongo import MongoClient, GEO2D
import datetime
import serial
import time
#import pynmea2
import sys
import threading

def main():
	while(1):
		reader = SimpleMFRC522()

		print("Hold a tag near the reader")

		try:
			id, text = reader.read()
			print(id)
			print(text)
			#reader.write("Panchito")
			time.sleep(1)
			

		except KeyboardInterrupt:
			print('bye')
		GPIO.cleanup()	
		
def main2():
	
	while(1):
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

		if GPIO.input(5):
			for i in range(300):
				for halfstep in range(8):
					for pin in range(4):
						GPIO.output(control_pins[pin], halfstep_seq[halfstep][pin])
					time.sleep(0.001)
		time.sleep(6)

		if GPIO.input(31):
			for i in range(300):
				for halfstep in range(8):
					for pin in range(4):
						GPIO.output(control_pins[pin], halfstep_seq_rev[halfstep][pin])
					time.sleep(0.001)

		GPIO.cleanup()		

hilo1 = threading.Thread(target=main)
hilo2 = threading.Thread(target=main2)
hilo1.start()
hilo2.start()
	
