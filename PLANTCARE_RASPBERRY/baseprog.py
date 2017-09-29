import time
import json
import serial
import requests
import schedule
import mysql.connector
from time import gmtime, strftime

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

add_light = (
	"INSERT INTO FREQ_LIGHT(POT_ID, TIMESTAMP, LIGHT) "
	"VALUES(%s, NOW(), %s)")

get_freq_light_percentage = (
	"select ((select COUNT(*) from FREQ_LIGHT " 
	"where LIGHT <= (select REQ_LIGHT from PLANT_CONFIGS " 
	"where ID in (select PLANT_CONFIG_ID from POTS " 
	"where ID = %s)) and POT_ID = %s)*100 / COUNT(*)) as PERCENTAGEOFSUFFICIENT from FREQ_LIGHT;")

get_sunlight_minutes = (
	"select (SUM(LIGHT)) from SENSOR_DATA "
	"where cast(TIMESTAMP as time) >= ( "
		"select SUNRISE from POTS "
		"where ID = %s) and POT_ID = %s "
		"and cast(TIMESTAMP as date) = cast(NOW() as date);")
			
add_sensordata = (
	"insert into SENSOR_DATA(POT_ID, TIMESTAMP, TEMPERATURE, MOISTURE, LIGHT, BLINDER_ON, WATERTANK_EMPTY, CONNECTION_DOWN) "
	"values(%s, NOW(), %s, %s, %s, %s, %s, %s)")
	
get_sunrise_sunset = (
	"select SUNRISE, SUNSET from POTS "
	"where ID = %s")
	
get_req_light_minutes = (
	"select REQ_LIGHT_MINUTES from PLANT_CONFIGS where ID in ( select PLANT_CONFIG_ID from POTS where ID = %s);") 
	
def lightSampling():
	db_cnx = mysql.connector.connect(**db_config)
	db_cursor = db_cnx.cursor()
    # get keyboard input
    
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
    
def persistingData():
	#get_freq_light_percentage
	db_cnx = mysql.connector.connect(**db_config)
	db_cursor = db_cnx.cursor()
	db_cursor.execute(get_freq_light_percentage, (pot_id, pot_id));
	light_result = db_cursor.fetchall()
	light_result = (light_result[0][0])/10
	data_to_insert = {}
	input = '1'
	out = ''
	ser.flush()
	ser.write(input)
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
			data_to_insert = {'POT_ID': pot_id, 'TIMESTAMP' : strftime("%Y-%m-%d %H:%M:%S", gmtime()), 'TEMPERATURE' : str(serial_json["TEMPERATURE"]), 'MOISTURE':str(serial_json["MOISTURE"]), 'LIGHT':str(light_result), 'LAMP_ON': str(serial_json["BLINDER_ON"]), 'WATERTANK_EMPTY':str(serial_json["WATERTANK_EMPTY"]), 'CONNECTION_DOWN':str(serial_json["CONNECTION_DOWN"])}
			#print data_to_insert
			
	headers = {'content-type': 'application/json'}
	r = requests.post(post_address, data = json.dumps(data_to_insert), headers = headers)
	local_data_to_insert = (str(data_to_insert['POT_ID']), str(data_to_insert['TEMPERATURE']), str(data_to_insert['MOISTURE']), str(data_to_insert['LIGHT']), str(data_to_insert['LAMP_ON']), str(data_to_insert['WATERTANK_EMPTY']), str(data_to_insert['CONNECTION_DOWN']))
	db_cursor.execute(add_sensordata, local_data_to_insert)
	db_cursor.execute("delete from FREQ_LIGHT where POT_ID = %s", [pot_id])
	db_cnx.commit()
	db_cursor.close()
	db_cnx.close()

def openValve():
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


schedule.every(5).seconds.do(lightSampling)
schedule.every(10).minutes.do(persistingData)
schedule.every().day.at(str_sunset).do(openValve)

while True:
	schedule.run_pending()
	time.sleep(1)
