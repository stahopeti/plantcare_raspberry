import sys
import mysql.connector
import random
import datetime
import time
import string
import serial
from time import gmtime, strftime

pot_id = sys.argv[1]
serial_port = sys.argv[2]

db_config = {
	'user': 'root', 
	'password': 'schlieffenplan', 
	'host': 'localhost', 
	'database': 'PLANT_CARE'
}
		
ser = serial.Serial(
	port=serial_port,
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

get_req_moisture = (
	"select REQ_MOIST from PLANT_CONFIGS where ID in ( select PLANT_CONFIG_ID from POTS where ID = %s);") 	

get_last_moisture = (
	"select MOISTURE from SENSOR_DATA where ID = %s limit 1;"
)
	
db_cnx = mysql.connector.connect(**db_config)
db_cursor = db_cnx.cursor()
db_cursor.execute(get_sunlight_minutes, (pot_id, pot_id)) 
sunlight_minutes = db_cursor.fetchall()[0][0]
db_cursor.execute(get_req_light_minutes, [pot_id])
req_light_time_minutes = db_cursor.fetchall()[0][0]

#checking whether moisture is sufficient enough
db_cursor.execute(get_req_moisture, [pot_id])
req_moisture = db_cursor.fetchall()[0][0]

db_cursor.execute(get_last_moisture, [pot_id])
last_moisture = db_cursor.fetchall()[0][0]

if( last_moisture > 600 ):
	out = ''
	input = 'E'
	ser.flush()
	ser.write(input)
	time.sleep(1)
	while ser.inWaiting() > 0:
		out += ser.read(1)


#lamp
if( req_light_time_minutes and sunlight_minutes ):
	time_for_lamp_minutes = req_light_time_minutes - sunlight_minutes
	time_for_lamp_seconds = time_for_lamp_minutes*60

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
