import sys
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

pot_id = sys.argv[1]

db_cnx = mysql.connector.connect(**db_config)
db_cursor = db_cnx.cursor()
get_sunlight_minutes = (
	"select (SUM(LIGHT)) from SENSOR_DATA "
	"where cast(TIMESTAMP as time) >= ( "
		"select SUNRISE from POTS "
		"where ID = %s) and POT_ID = %s "
		"and cast(TIMESTAMP as date) = cast(NOW() as date);")
db_cursor.execute(get_sunlight_minutes, (pot_id, pot_id)) 
sunlight_percentage = db_cursor.fetchall()[0][0]
#print 'Need ' + str(480-(sunlight_percentage/10)) + ' more minutes of light' 
print 'sun shined for: ' + str((sunlight_percentage)) + ' minutes' 
