import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
control_pins = [4,17,27,22]

GPIO.setup(5,GPIO.IN)
GPIO.setup(6,GPIO.IN)

for pin in control_pins:
  GPIO.setup(pin, GPIO.OUT)
  GPIO.output(pin, 0)
  
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
			
time.sleep(2)

if GPIO.input(6):
	for i in range(300):
		for halfstep in range(8):
			for pin in range(4):
				GPIO.output(control_pins[pin], halfstep_seq_rev[halfstep][pin])
			time.sleep(0.001)

GPIO.cleanup()

