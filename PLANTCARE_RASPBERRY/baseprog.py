import sys
import time
import json
import serial
import requests
import schedule
import subprocess
import mysql.connector
from time import gmtime, strftime

#
import sampleLight
import persistData
#import daily
#

pot_id = sys.argv[1]
serial_port = ''
post_address = 'http://152.66.254.93/speti/myapi.php/SENSOR_DATA'

ser = ()

db_config = {
	'user': 'root', 
	'password': 'schlieffenplan', 
	'host': 'localhost', 
	'database': 'PLANT_CARE'}
	
def connectToDB():
	try:	
		db_cnx = mysql.connector.connect(**db_config)
	except mysql.connector.Error, e:
		time.sleep(5)
		connectToDB()
	return

get_serial_port = (
	"select SERIAL_PORT from POTS where ID = %s")
	
get_sunrise_sunset = (
	"select SUNRISE, SUNSET, SERIAL_PORT from POTS where ID = %s")

def samplingLight():
	sampleLight.work(pot_id, ser);

def persistingData():
	persistData.work(pot_id, ser);

def dailyScript():
	subprocess.Popen('python /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/daily.py ' + pot_id + ' ' + serial_port, shell=True);

def checkingPendingCommand():
	subprocess.Popen('python /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/checkPendingCommand.py ' + pot_id + ' ' + serial_port, shell=True);

try:	
	connectToDB()
	db_cnx = mysql.connector.connect(**db_config)
	db_cursor = db_cnx.cursor()
	db_cursor.execute(get_sunrise_sunset, [pot_id]);
	result = db_cursor.fetchall()
	
	sunrise = str(result[0][0])
	sunset = str(result[0][1])
	serial_port = str(result[0][2])
	
	
	db_cnx.commit()
	db_cursor.close()
	db_cnx.close()
	str_sunset = sunset[0] + sunset[1] + sunset[2] + sunset[3] + sunset[4]
except mysql.connector.Error as ex:
	print 'database exception: ' #+ ex.__getitem__() + " " + ex.__str__()


	
ser = serial.Serial(
		port=serial_port,
		baudrate=9600,
		parity=serial.PARITY_ODD,
		stopbits=serial.STOPBITS_TWO,
		bytesize=serial.SEVENBITS)	
	
schedule.every(15).seconds.do(samplingLight)
schedule.every(10).minutes.do(persistingData)
schedule.every(10).minutes.do(checkingPendingCommand)
schedule.every().day.at(str_sunset).do(dailyScript)

while True:
	schedule.run_pending()
	time.sleep(1)
