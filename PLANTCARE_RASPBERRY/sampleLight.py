import sys
import mysql.connector
import random
import datetime
import time
import serial
import string
from time import gmtime, strftime
from serial import SerialException

db_config = {
	'user': 'root', 
	'password': 'schlieffenplan', 
	'host': 'localhost', 
	'database': 'PLANT_CARE'
}

add_light = (
	"INSERT INTO FREQ_LIGHT(POT_ID, TIMESTAMP, LIGHT) "
	"VALUES(%s, NOW(), %s)")


def work(pot_id, ser):
	try:
		ser.isOpen()
		time.sleep(2)
		
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
			data_to_insert = (pot_id, out)
			db_cursor.execute(add_light, data_to_insert)
			db_cnx.commit()

		db_cursor.close()
		db_cnx.close()
	except mysql.connector.Error as ex:
		print 'database exception: ' + ex.__getitem__() + " " + ex.__str__()
	except SerialException as ex:
		print 'serial exception: ' + ex.__str__()
	except Exception as ex:
		print 'exception: ' #+ ex.__getitem__() + " " + ex.__str__()