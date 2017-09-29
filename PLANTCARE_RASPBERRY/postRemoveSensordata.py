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
pot_id = 1
address = 0x4b
db_config = {
	'user': 'root', 
	'password': 'schlieffenplan', 
	'host': 'localhost', 
	'database': 'PLANT_CARE'
}

# local db querys
db_cnx = mysql.connector.connect(**db_config)
db_cursor = db_cnx.cursor()

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
ser = serial.Serial(
	port='/dev/ttyUSB1',
	baudrate=9600,
	parity=serial.PARITY_ODD,
	stopbits=serial.STOPBITS_TWO,
	bytesize=serial.SEVENBITS
)


get_light_percentage = (
	"select ((select COUNT(*) from FREQ_LIGHT " 
	"where LIGHT >= (select REQ_LIGHT from PLANT_CONFIGS " 
	"where ID in (select PLANT_CONFIG_ID from POTS " 
	"where ID = %s)) and POT_ID = %s)*100 / COUNT(*)) as PERCENTAGEOFSUFFICIENT from FREQ_LIGHT;")


db_cursor.execute(get_light_percentage, (pot_id, pot_id));

light_result = db_cursor.fetchall()


data_to_insert = {}
out = ''
result = 'notok'
while result!='ok' :
    # get keyboard input
    input = '1'
    if input == 'exit':
        ser.close()
        exit()
    else:
        ser.write(input)
        time.sleep(1)
        time.sleep(1)
        while ser.inWaiting() > 0:
            out += ser.read(1)
	
	if (out != ''):
		try:
			serial_json = json.loads(out)
		except ValueError, e:
			print out
		else:
			#POT_ID, TEMPERATURE, MOISTURE, LIGHT, LAMP_ON, WATERTANK_EMPTY, CONNECTION_DOWN
			data_to_insert = {'POT_ID': pot_id, 'TIMESTAMP' : strftime("%Y-%m-%d %H:%M:%S", gmtime()), 'TEMPERATURE' : str(serial_json["TEMPERATURE"]), 'MOISTURE':str(serial_json["MOISTURE"]), 'LIGHT':str(light_result[0][0]), 'LAMP_ON': str(serial_json["BLINDER_ON"]), 'WATERTANK_EMPTY':str(serial_json["WATERTANK_EMPTY"]), 'CONNECTION_DOWN':str(serial_json["CONNECTION_DOWN"])}
			#print data_to_insert
		out = ''
		result = 'ok'
ser.close()

# rest api request
headers = {'content-type': 'application/json'}
r = requests.post(post_address, data = json.dumps(data_to_insert), headers = headers)

add_sensordata = (
	"insert into SENSOR_DATA(POT_ID, TIMESTAMP, TEMPERATURE, MOISTURE, LIGHT, BLINDER_ON, WATERTANK_EMPTY, CONNECTION_DOWN) "
	"values(%s, NOW(), %s, %s, %s, %s, %s, %s)")
	
#remove_old_data = (
#	"delete from SENSOR_DATA "
#	"where TIMESTAMP < %s and POT_ID")

#serial_json = json.loads(serial_data)


#POT_ID, TIMESTAMP, TEMPERATURE, MOISTURE, LIGHT, LAMP_ON, WATERTANK_EMPTY, CONNECTION_DOWN
local_data_to_insert = (str(data_to_insert['POT_ID']), str(data_to_insert['TEMPERATURE']), str(data_to_insert['MOISTURE']), str(data_to_insert['LIGHT']), str(data_to_insert['LAMP_ON']), str(data_to_insert['WATERTANK_EMPTY']), str(data_to_insert['CONNECTION_DOWN']))
db_cursor.execute(add_sensordata, local_data_to_insert)
#db_cursor.execute(remove_old_data, ( (datetime.datetime.now() - datetime.timedelta(hours=24)),) )

db_cursor.execute("delete from FREQ_LIGHT where POT_ID = %s", [pot_id])

# a time azert van (time ,) formatumban, mert az sql csak igy fogadja el 
db_cnx.commit()
db_cursor.close()
db_cnx.close()
