import time
import json
import serial
import requests
import schedule
import mysql.connector
from time import gmtime, strftime

#
import sampleLight
import persistData
import daily
#

pot_id = 1
post_address = 'http://152.66.254.93/speti/myapi.php/SENSOR_DATA'

db_config = {
	'user': 'root', 
	'password': 'schlieffenplan', 
	'host': 'localhost', 
	'database': 'PLANT_CARE'}
	
def connectToDB():
	try:	
		db_cnx = mysql.connector.connect(**db_config)
	except mysql.connector.errors.InterfaceError, e:
		time.sleep(5)
		connectToDB()
	return
	
ser = serial.Serial(
	port='/dev/ttyUSB0',
	baudrate=9600,
	parity=serial.PARITY_ODD,
	stopbits=serial.STOPBITS_TWO,
	bytesize=serial.SEVENBITS)

get_sunrise_sunset = (
	"select SUNRISE, SUNSET from POTS "
	"where ID = %s")

def samplingLight():
	sampleLight.work(1)

def persistingData():
	persistData.work(1)

def daily():
	daily.work(1)
			
connectToDB()
db_cnx = mysql.connector.connect(**db_config)
db_cursor = db_cnx.cursor()
db_cursor.execute(get_sunrise_sunset, [pot_id]);
result = db_cursor.fetchall()
sunrise = str(result[0][0])
sunset = str(result[0][1])
db_cnx.commit()
db_cursor.close()
db_cnx.close()
str_sunset = sunset[0] + sunset[1] + sunset[2] + sunset[3] + sunset[4]


schedule.every(5).seconds.do(samplingLight)
schedule.every(10).minutes.do(persistingData)
schedule.every().day.at(str_sunset).do(daily)

while True:
	schedule.run_pending()
	time.sleep(1)
