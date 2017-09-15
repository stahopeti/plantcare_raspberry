import mysql.connector
import random
import datetime
import time
import string
from time import gmtime, strftime

db_config = {
	'user': 'root', 
	'password': 'schlieffenplan', 
	'host': 'localhost', 
	'database': 'PLANT_CARE'
}

db_cnx = mysql.connector.connect(**db_config)
db_cursor = db_cnx.cursor()

get_sunlight_percentage = (
	"select (SUM(LIGHT)) from SENSOR_DATA "
	"where cast(TIMESTAMP as time) >= ( "
		"select SUNRISE from POTS "
		"where ID = SENSOR_DATA.POT_ID);")

db_cursor.execute(get_sunlight_percentage)
		
sunlight_percentage = db_cursor.fetchall()[0][0]

#print sunlight_percentage/10

print 'Need ' + str(480-(sunlight_percentage/10)) + ' more minutes of light' 

print 'Turning on light at: ' + strftime("%H:%M:%S", time.localtime())

time.sleep(60)
print 'Turning off light one minute: ' + strftime("%H:%M:%S", time.localtime())

