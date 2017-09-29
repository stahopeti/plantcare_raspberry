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
#light_amount = sys.argv[2]


db_cnx = mysql.connector.connect(**db_config)
db_cursor = db_cnx.cursor()
add_light = (
	"INSERT INTO FREQ_LIGHT(POT_ID, TIMESTAMP, LIGHT) "
	"VALUES(%s, NOW(), %s)")

remove_old_data = (
	"DELETE FROM FREQ_LIGHT "
	"WHERE TIMESTAMP < %s")
	
data_to_insert = (pot_id, random.randint(700,960))
db_cursor.execute(add_light, data_to_insert)
db_cnx.commit()
db_cursor.close()
db_cnx.close()