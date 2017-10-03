import sys
import mysql.connector
import random
import datetime
import time
import serial
import string
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


add_light = (
	"INSERT INTO FREQ_LIGHT(POT_ID, TIMESTAMP, LIGHT) "
	"VALUES(%s, NOW(), %s)")

#pot_id = sys.argv[1]
#light_amount = sys.argv[2]

#get keyboard input

def work(pot_id):
	db_cnx = mysql.connector.connect(**db_config)
	db_cursor = db_cnx.cursor()
	input = '2'
	out = ''
	ser.flush()
	ser.write(input)
	time.sleep(1)
	while ser.inWaiting() > 0:
		out += ser.read(1)

	if (out != ''):
		#print out
		data_to_insert = (pot_id, out)
		db_cursor.execute(add_light, data_to_insert)
		db_cnx.commit()

	db_cursor.close()
	db_cnx.close()