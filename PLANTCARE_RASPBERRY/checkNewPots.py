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


pi_id = sys.argv[1]

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
	
	
get_commands_address = 'http://152.66.254.93/speti/myapi.php/COMMANDS/PIS'
get_plant_configs_address = 'http://152.66.254.93/speti/myapi.php/PLANT_CONFIGS'
get_pot = 'http://152.66.254.93/speti/myapi.php/POTS'
delete_commands_address = 'http://152.66.254.93/speti/myapi.php/COMMANDS/PIS'

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
	if( taskparam.task == 'P_ADDED' ):
		try:
			payload = { 'ID' : taskparam.parameter }
			headers = {'content-type-*': 'application/json'}
			new_pot = requests.get(get_pot, data = json.dumps(payload), headers = headers)
			json_pot = new_pot.json()
			print 'POT: '
			print json.dumps(json_pot, indent=4, sort_keys=True)
			
			db_cnx = mysql.connector.connect(**db_config)
			db_cursor = db_cnx.cursor()
			
			#letolteni a json_pot[0]['plant_config_id'] id-ju plant configot
			payload = { 'ID' : json_pot[0]['plant_config_id'] }
			new_config = requests.get(get_plant_configs_address, data = json.dumps(payload), headers = headers)
			json_config = new_config.json()
			
			print 'POT: '
			print json.dumps(json_config, indent=4, sort_keys=True)
			
			#belerakni a letoltott plantconfigot az adatbazisba
			config_to_insert = (json_config[0]['plant_code'],json_config[0]['plant_name'],json_config[0]['req_light'],json_config[0]['req_moist'],json_config[0]['req_temp'], 480, json_pot[0]['id'])
			db_cursor.execute(insert_plant_config, config_to_insert)
			
			#megkeresni mi ennek a pot_id-s plantconfignak az id-je
			db_cursor.execute(get_new_plant_config_id, [json_pot[0]['id']])
			new_plant_config_id = db_cursor.fetchall()[0][0]
			
			db_cnx.commit()
			
			print 'New plant config id: ' + str(new_plant_config_id)
			
			#berakni ugy a potot, hogy azt a plant_config_id-t megkapja 
			pot_to_insert = (json_pot[0]['id'],json_pot[0]['name'],new_plant_config_id,json_pot[0]['sunrise'],json_pot[0]['sunset'], None)
			db_cursor.execute(insert_pot, pot_to_insert)
			
			db_cnx.commit()
			
			db_cursor.close()
			db_cnx.close()
			
			payload = { 'ID' : taskparam.ID }
			requests.delete(delete_commands_address, data = json.dumps(payload), headers = headers)
		except (mysql.connector.Error, serial.SerialException) as e:
			print e

payload = { 'PI_ID' : pi_id }
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
			
	if new_pot_commands:
		for t in new_pot_commands:
			print 'New pot command: ' + t.task
			executeOrder(t)
			
		os.system("sudo reboot")

		
except ValueError, e:
	print e
	print "Nothing to execute"