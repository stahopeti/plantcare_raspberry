import sys
import smbus
import requests
import json
import mysql.connector
import random
import datetime
import time
import servowave
import serial
from time import gmtime, strftime

# configuration start
address = 0x4b
bus = smbus.SMBus(1)
db_config = {
	'user': 'root', 
	'password': 'schlieffenplan', 
	'host': 'localhost', 
	'database': 'PLANT_CARE'
}
post_address = 'http://152.66.254.93/speti/myapi.php/SENSOR_DATA'
get_address = 'http://152.66.254.93/speti/myapi.php/REQUESTS'
delete_address = 'http://152.66.254.93/speti/myapi.php/REQUESTS'

class Order:
	ID = ""
	order = ""
	orderCount = 0
	def __init__(self, ID, order):
		self.ID
		self.order
		Order.orderCount += 1;

def executeOrder( orderparam ):
	if( orderparam.order == 'Move servo!'):
		print 'Moving servo ID: ' + orderparam.ID
		servowave.move_servo()
		payload = { 'ID' : orderparam.ID }
		headers = {'content-type': 'application/json'}
		requests.delete(delete_address, data = json.dumps(payload), headers = headers)
	if( orderparam.order == 'Water plant!'):
		print 'Watering plants ID: ' + orderparam.ID
		payload = { 'ID' : orderparam.ID }
		headers = {'content-type': 'application/json'}
		requests.delete(delete_address, data = json.dumps(payload), headers = headers)
	if( orderparam.order == 'Shut blinder!'):
		print 'Shutting blinders ID: ' + orderparam.ID
		payload = { 'ID' : orderparam.ID }
		headers = {'content-type': 'application/json'}
		requests.delete(delete_address, data = json.dumps(payload), headers = headers)
		
# configuration end

#raw = bus.read_word_data(address, 0) 
#raw = ((raw << 8) & 0xFFFF) + (raw >> 8)
#temperature = (raw / 32.0) / 8.0
temperature = random.randint(20, 25)
print 'Temp: {0:0.2f} Celsius'.format(temperature)
moisture = random.randint(10,19)
light = random.randint(0,9)

# rest api request
payload = {'POT_ID': 1, 'TIMESTAMP' : strftime("%Y-%m-%d %H:%M:%S", gmtime()), 'TEMPERATURE' : '{0:0.2f}'.format(temperature), 'MOISTURE':'{0:0.2f}'.format(moisture), 'LIGHT':'{0:0.2f}'.format(light), 'BLINDER_ON': 0, 'WATERTANK_EMPTY':0, 'CONNECTION_DOWN':0}
headers = {'content-type': 'application/json'}
r = requests.post(post_address, data = json.dumps(payload), headers = headers)
r = requests.get(get_address)

try:
	json_response = r.json()
	for rec in json_response:
		ord = Order(rec["ID"], rec["ORDERS"])
		ord.ID = rec["ID"]
		ord.order = rec["ORDERS"]
		executeOrder(ord)
	
	print json.dumps(json_response, indent=4, sort_keys=True)
except ValueError, e:
	print e
	print "Nothing to execute"
#print json_response['REQUESTS']['records'][0][0]
#records = json_response['REQUESTS']['records']

# local db querys
db_cnx = mysql.connector.connect(**db_config)
db_cursor = db_cnx.cursor()
add_sensordata = (
	"INSERT INTO SENSOR_DATA(POT_ID, TIMESTAMP, TEMPERATURE, MOISTURE, LIGHT, BLINDER_ON, WATERTANK_EMPTY, CONNECTION_DOWN) "
	"VALUES(%s, %s, %s, %s, %s, %s, %s, %s)")
	
remove_old_data = (
	"DELETE FROM SENSOR_DATA "
	"WHERE TIMESTAMP < %s")

data_to_insert = (1, strftime("%Y-%m-%d %H:%M:%S", gmtime()), temperature, moisture, light, 0, 1, 0)
db_cursor.execute(add_sensordata, data_to_insert)
#db_cursor.execute(remove_old_data, ( (datetime.datetime.now() - datetime.timedelta(hours=5)),) )
# a time azert van (time ,) formatumban, mert az sql csak igy fogadja el 
db_cnx.commit()
db_cursor.close()
db_cnx.close()
