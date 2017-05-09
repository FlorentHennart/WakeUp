from __future__ import print_function
from flask import Flask, request
from flask import jsonify
from random import randint
import sys
import smbus

app = Flask(__name__)
import logging
logging.basicConfig()
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

# for RPI version 1, use “bus = smbus.SMBus(0)”
bus = smbus.SMBus(1)

# This is the address we setup in the Arduino Program
address = 0x04
			
def WakeUp():
	# Turn on GPIO
	# GPIO.output(chan_list, GPIO.HIGH)
	startTime = time.time()
	while(time.time()-startTime)<5*60:
		for led in range(0,60,1):
			# Draw a color 255 [100-150] [50-100]
			# Increase brightness during 5 minutes
			brightness = (time.time()-startTime)/(5*60)
			r = int(255*brightness)
			g = int(randint(100,150)*brightness)
			b = int(randint(50,100)*brightness)
			setLed(led,r,g,b)
			time.sleep(0.1)
	# then increase green to get more yellow	
	while (time.time()-startTime)<10*60:
		yellowNess = (time.time()-(startTime+5*60))/(5*60)
		for led in range(0,60,1):
			r = (255)
			g = int(randint(100,150)+yellowNess*randint(0,105))
			b = int(randint(50,100))
			setLed(led,r,g,b)
			time.sleep(0.1)
	print ('Waked!');

def quickDemo():	
	startTime = time.time()
	while (time.time()-startTime)<30:
		for led in range(0,60,1):
			# Draw a color 255 [100-150] [50-100]
			# Increase brightness during 5 minutes
			brightness = (time.time()-startTime)/(30)
			r = int(255*brightness)
			g = int(randint(100,150)*brightness)
			b = int(randint(50,100)*brightness)
			setLed(led,r,g,b)
			time.sleep(0.1)
	# then increase green to get more yellow	
	while (time.time()-startTime)<60:
		yellowNess = (time.time()-(startTime+30))/(60)
		for led in range(0,60,1):
			r = (255)
			g = int(randint(100,150)+yellowNess*randint(0,105))
			b = int(randint(50,100))
			setLed(led,r,g,b)
			time.sleep(0.1)
	time.sleep(10)
	EndOfWakeUp()
	
def EndOfWakeUp():
	# Turn of GPIO
	setLed(0,0,0,0)
	time.sleep(1)		
	GPIO.output(chan_list, GPIO.LOW)
	print ('End!');

def setLed(ledNb,r,g,b):
	print (str(ledNb) + ' : r ' + str(r) + ' g '+str(g) + ' b '+str(b))
	bus.write_byte(address, 0xFF) # First word
	bus.write_byte(address, ledNb)
	bus.write_byte(address, min(254,r))
	bus.write_byte(address, min(254,g))
	bus.write_byte(address, min(254,b))

def stopAllJobs():
	scheduler = BackgroundScheduler()
	currentJobs = scheduler.get_jobs();
	for aJob in currentJobs:
		aJob.remove()
	
@app.route('/')
def index():
    return 'Hello world'
    
@app.route('/lights', methods=['GET','POST'])
def lights():
	lcommand=request.args.get('Command')
	# First, log
	with open('serverLog.txt', 'a') as f:
		f.write(time.strftime('%Y %m %d : %H %M %S') + ' : ' +request.remote_addr + ' : ' + lcommand + '\n')
		print (time.strftime('%Y %m %d : %H %M %S') + ' : ' +request.remote_addr + ' : ' + lcommand, file=sys.stderr)
	scheduler = BackgroundScheduler()
	if lcommand=='WakeUp':
		stopAllJobs()
		scheduler.add_job(WakeUp, 'date', run_date=datetime.now()+timedelta(seconds=1), id='WakeUpSched', replace_existing=True) #modify to minutes=30
		scheduler.add_job(EndOfWakeUp, 'date', run_date=datetime.now()+timedelta(minutes=30), id='EndOfWakeUpSched', replace_existing=True) #modify to minutes=30
		scheduler.start()	
	elif lcommand=='Demo':
		stopAllJobs()
		quickDemo()
	elif lcommand=='Stop':
		stopAllJobs()
		EndOfWakeUp()
	return 'Lights!'
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
    
GPIO.cleanup()
