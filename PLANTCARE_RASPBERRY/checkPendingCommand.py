import sys
import requests
import json
import mysql.connector
import random
import datetime
import time
import serial
from time import gmtime, strftime 


pot_id = 1
# configuration start
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
	
	
get_plant_config_id = (
	"select PLANT_CONFIG_ID from POTS where ID = %s")
	
update_plant_config = (
	"update PLANT_CONFIGS "
	"set PLANT_CODE = %s " 
	", PLANT_NAME = %s " 
	", REQ_TEMP = %s " 
	", REQ_MOIST = %s " 
	", REQ_LIGHT = %s " 
	", REQ_LIGHT_MINUTES = %s "
	"where ID = %s")
	
get_commands_address = 'http://152.66.254.93/speti/myapi.php/COMMANDS'
get_plant_configs_address = 'http://152.66.254.93/speti/myapi.php/PLANT_CONFIGS'
delete_commands_address = 'http://152.66.254.93/speti/myapi.php/COMMANDS'

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
		payload = { 'ID' : taskparam.ID }
		headers = {'content-type': 'application/json'}
		requests.delete(delete_commands_address, data = json.dumps(payload), headers = headers)
	if( taskparam.task == 'L_SPEC' ):
		payload = { 'ID' : taskparam.ID }
		headers = {'content-type': 'application/json'}
		requests.delete(delete_commands_address, data = json.dumps(payload), headers = headers)
	if( taskparam.task == 'C_CHNG' ):
		try:
			payload = { 'ID' : taskparam.parameter }
			headers = {'content-type-*': 'application/json'}
			new_config = requests.get('http://152.66.254.93/speti/myapi.php/PLANT_CONFIGS', data = json.dumps(payload), headers = headers)
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
	for rec in json_response:
		tsk = Task(rec["id"], rec["task"], rec["parameter"])
		tsk.ID = rec["id"]
		tsk.task = rec["task"]
		tsk.parameter = rec["parameter"]
		executeOrder(tsk)
		
except ValueError, e:
	print e
	print "Nothing to execute"