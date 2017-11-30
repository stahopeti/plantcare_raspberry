import os
import sys
import requests
import json
import mysql.connector
import random
import datetime
import time
import serial
from time import gmtime, strftime 


pot_id = sys.argv[1]
serial_port = sys.argv[2]

	
ser = serial.Serial(
		port=serial_port,
		baudrate=9600,
		parity=serial.PARITY_ODD,
		stopbits=serial.STOPBITS_TWO,
		bytesize=serial.SEVENBITS)	
		
# configuration start
db_config = {
	'user': 'root', 
	'password': 'schlieffenplan', 
	'host': 'localhost', 
	'database': 'PLANT_CARE'
}
	
get_plant_config_id = (
	"select PLANT_CONFIG_ID from POTS where ID = %s")
	
insert_pot = (
	"insert into POTS(ID, NAME, PLANT_CONFIG_ID, SUNRISE, SUNSET, SERIAL_PORT) "
	"values(%s, %s, %s, %s, %s, %s)")

get_new_plant_config_id = (
	"select ID from PLANT_CONFIGS where POT_ID = %s")

insert_plant_config = (
	"insert into PLANT_CONFIGS(PLANT_CODE, PLANT_NAME, REQ_TEMP, REQ_MOIST, REQ_LIGHT, REQ_LIGHT_MINUTES, POT_ID)"
	"values(%s, %s, %s, %s, %s, %s, %s)")
	
update_plant_config = (
	"update PLANT_CONFIGS "
	"set PLANT_CODE = %s " 
	", PLANT_NAME = %s " 
	", REQ_TEMP = %s " 
	", REQ_MOIST = %s " 
	", REQ_LIGHT = %s " 
	", REQ_LIGHT_MINUTES = %s "
	"where ID = %s")
	
get_commands_address = 'http://152.66.254.93/speti/myapi.php/COMMANDS/POTS'
get_plant_configs_address = 'http://152.66.254.93/speti/myapi.php/PLANT_CONFIGS'
get_pot = 'http://152.66.254.93/speti/myapi.php/POTS'
delete_commands_address = 'http://152.66.254.93/speti/myapi.php/COMMANDS/POTS'

class Task:
	ID = ""
	task = ""
	parameter = ""
	taskCount = 0
	def __init__(self, ID, task, parameter):
		self.ID
		self.task
		self.parameter
		Task.taskCount= 1;

def executeOrder( taskparam ):
	if( taskparam.task == 'W' ):
		try:
			payload = { 'ID' : taskparam.ID }
			deciliters = int(taskparam.parameter)
			iterations = 0
			while ( iterations < deciliters ):
				iterations = iterations + 1
				out = ''
				input = 'E'
				ser.flush()
				ser.write(input)
				time.sleep(1)
				while ser.inWaiting() > 0:
					out += ser.read(1)
				
			headers = {'content-type': 'application/json'}
			requests.delete(delete_commands_address, data = json.dumps(payload), headers = headers)
		except (mysql.connector.Error, serial.SerialException) as e:
			print e
	if( taskparam.task == 'L_SPEC' ):
		try:
			payload = { 'ID' : taskparam.ID }
			time_for_lamp_seconds = int(taskparam.parameter)*60
			print 'lampseconds: ' + str(time_for_lamp_seconds)
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
			headers = {'content-type': 'application/json'}
			requests.delete(delete_commands_address, data = json.dumps(payload), headers = headers)
		except (mysql.connector.Error, serial.SerialException) as e:
			print e
	if( taskparam.task == 'C_CHNG' ):
		try:
			payload = { 'ID' : taskparam.parameter }
			headers = {'content-type-*': 'application/json'}
			new_config = requests.get(get_plant_configs_address, data = json.dumps(payload), headers = headers)
			json_config = new_config.json()
			
			db_cnx = mysql.connector.connect(**db_config)
			db_cursor = db_cnx.cursor()
			db_cursor.execute(get_plant_config_id, [pot_id]);
			
			plant_config_id = db_cursor.fetchall()[0][0]
			data_to_update = (json_config[0]['plant_code'],json_config[0]['plant_name'],json_config[0]['req_light'],json_config[0]['req_moist'],json_config[0]['req_temp'], 480, plant_config_id)
			db_cursor.execute(update_plant_config, data_to_update)
			
			db_cnx.commit()
			db_cursor.close()
			db_cnx.close()
			
			payload = { 'ID' : taskparam.ID }
			requests.delete(delete_commands_address, data = json.dumps(payload), headers = headers)
		except (mysql.connector.Error, serial.SerialException) as e:
			print e

payload = { 'POT_ID' : pot_id }
headers = {'content-type': 'application/json'}
commands = requests.get(get_commands_address, data = json.dumps(payload), headers = headers)

try:
	json_response = commands.json()
	print 'DUMPS: '
	print json.dumps(json_response, indent=4, sort_keys=True)
	#print 'REC: '
	basic_commands = []
	new_pot_commands = []
	
	for rec in json_response:
		tsk = Task(rec["id"], rec["task"], rec["parameter"])
		tsk.ID = rec["id"]
		tsk.task = rec["task"]
		tsk.parameter = rec["parameter"]
		
		if (tsk.task == 'P_ADDED'): 
			new_pot_commands.append(tsk)
		else:
			basic_commands.append(tsk)
		
		#executeOrder(tsk)
	if basic_commands:
		for t in basic_commands:
			print 'Basic command: ' + t.task
			executeOrder(t)
	
		
except ValueError, e:
	print e
	print "Nothing to execute"