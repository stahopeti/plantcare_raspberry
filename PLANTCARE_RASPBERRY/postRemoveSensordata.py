import sys
import requests
import json
import mysql.connector
import random
import datetime
import time
#import servowave
import serial
from time import gmtime, strftime

# configuration start
pot_id = sys.argv[1]
address = 0x4b
db_config = {
	'user': 'root', 
	'password': 'schlieffenplan', 
	'host': 'localhost', 
	'database': 'PLANT_CARE'
}

post_address = 'http://152.66.254.93/speti/myapi.php/SENSOR_DATA'

# configuration end

#raw = bus.read_word_data(address, 0) 
#raw = ((raw << 8) & 0xFFFF) + (raw >> 8)
#temperature = (raw / 32.0) / 8.0
if True:
	temperature = random.randint(20, 25)
	moisture = random.randint(10,19)
	light = random.randint(0,9)

# input from serial
if False:
	ser = serial.Serial(
		port='/dev/ttyUSB0',
		baudrate=9600,
		parity=serial.PARITY_ODD,
		stopbits=serial.STOPBITS_TWO,
		bytesize=serial.SEVENBITS
	)

	if (ser.isOpen() == False):
		ser = serial.Serial(
			port='/dev/ttyUSB1',
			baudrate=9600,
			parity=serial.PARITY_ODD,
			stopbits=serial.STOPBITS_TWO,
			bytesize=serial.SEVENBITS
		)

	serial_data = ''
	tries = 0
	while ((serial_data == '')):
		ser.write("1")
		time.sleep(1)
		while ser.inWaiting() > 0:
			serial_data += ser.read(1)
			
		print "serial_data: " + serial_data
	ser.close()

# rest api request
if True:
	payload = {'POT_ID': pot_id, 'TIMESTAMP' : strftime("%Y-%m-%d %H:%M:%S", gmtime()), 'TEMPERATURE' : '{0:0.2f}'.format(temperature), 'MOISTURE':'{0:0.2f}'.format(moisture), 'LIGHT':'{0:0.2f}'.format(light), 'BLINDER_ON': 0, 'WATERTANK_EMPTY':0, 'CONNECTION_DOWN':0}
	headers = {'content-type': 'application/json'}
	r = requests.post(post_address, data = json.dumps(payload), headers = headers)

# local db querys
db_cnx = mysql.connector.connect(**db_config)
db_cursor = db_cnx.cursor()
add_sensordata = (
	"insert into SENSOR_DATA(POT_ID, TIMESTAMP, TEMPERATURE, MOISTURE, LIGHT, BLINDER_ON, WATERTANK_EMPTY, CONNECTION_DOWN) "
	"values(%s, NOW(), %s, %s, %s, %s, %s, %s)")
	
#remove_old_data = (
#	"delete from SENSOR_DATA "
#	"where TIMESTAMP < %s and POT_ID")

#serial_json = json.loads(serial_data)


get_light_percentage = (
	"select ((select COUNT(*) from FREQ_LIGHT " 
	"where LIGHT >= (select REQ_LIGHT from PLANT_CONFIGS " 
	"where ID in (select PLANT_CONFIG_ID from POTS " 
	"where ID = %s)))*100 / COUNT(*)) as PERCENTAGEOFSUFFICIENT from FREQ_LIGHT;")


db_cursor.execute(get_light_percentage, [pot_id]);

light_result = db_cursor.fetchall()
#data_to_insert = (1, strftime("%Y-%m-%d %H:%M:%S", gmtime()), serial_json["TEMPERATURE"], serial_json["MOISTURE"], serial_json["LIGHT"], serial_json["BLINDER_ON"], serial_json["WATERTANK_EMPTY"], serial_json["CONNECTION_DOWN"])
data_to_insert = (pot_id, random.randint(700,960), random.randint(700,960), light_result[0][0], random.randint(0,1), random.randint(0,1), random.randint(0,1))
db_cursor.execute(add_sensordata, data_to_insert)
#db_cursor.execute(remove_old_data, ( (datetime.datetime.now() - datetime.timedelta(hours=24)),) )

db_cursor.execute("delete from FREQ_LIGHT where POT_ID = %s", [pot_id])

# a time azert van (time ,) formatumban, mert az sql csak igy fogadja el 
db_cnx.commit()
db_cursor.close()
db_cnx.close()
