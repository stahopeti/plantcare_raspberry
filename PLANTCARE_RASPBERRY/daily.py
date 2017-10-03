import sys
import mysql.connector
import random
import datetime
import time
import string
import serial
from time import gmtime, strftime

db_config = {
	'user': 'root', 
	'password': 'schlieffenplan', 
	'host': 'localhost', 
	'database': 'PLANT_CARE'
}
		
ser = serial.Serial(
	port='/dev/ttyUSB0',
	baudrate=9600,
	parity=serial.PARITY_ODD,
	stopbits=serial.STOPBITS_TWO,
	bytesize=serial.SEVENBITS)

get_sunlight_minutes = (
	"select (SUM(LIGHT)) from SENSOR_DATA "
	"where cast(TIMESTAMP as time) >= ( "
		"select SUNRISE from POTS "
		"where ID = %s) and POT_ID = %s "
		"and cast(TIMESTAMP as date) = cast(NOW() as date);")
	
get_req_light_minutes = (
	"select REQ_LIGHT_MINUTES from PLANT_CONFIGS where ID in ( select PLANT_CONFIG_ID from POTS where ID = %s);") 
	
def work(pot_id):
	db_cnx = mysql.connector.connect(**db_config)
	db_cursor = db_cnx.cursor()
	db_cursor.execute(get_sunlight_minutes, (pot_id, pot_id)) 
	sunlight_minutes = db_cursor.fetchall()[0][0]
	db_cursor.execute(get_req_light_minutes, [pot_id])
	req_light_time_minutes = db_cursor.fetchall()[0][0]
	
	time_for_lamp_minutes = req_light_time_minutes - sunlight_minutes
	time_for_lamp_seconds = time_for_lamp_minutes*60
	
	print 'openvalve'
	out = ''
	#while out != 'Opening valve!':
	out = ''
	input = '8'
	ser.flush()
	ser.write(input)
	time.sleep(1)
	while ser.inWaiting() > 0:
		out += ser.read(1)

	time.sleep(time_for_lamp_seconds)
	#while out != 'Closing valve!':
	out = ''
	input = '7'
	ser.flush()
	ser.write(input)
	time.sleep(1)
	while ser.inWaiting() > 0:
		out += ser.read(1)
	out = ''
	ser.flush()
