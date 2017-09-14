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
add_light = (
	"INSERT INTO FREQ_LIGHT(TIMESTAMP, LIGHT, POT_ID) "
	"VALUES(NOW(), %s, %s)")

remove_old_data = (
	"DELETE FROM FREQ_LIGHT "
	"WHERE TIMESTAMP < %s")
	
data_to_insert = (random.randint(700,960), 1)
db_cursor.execute(add_light, data_to_insert)
db_cnx.commit()
db_cursor.close()
db_cnx.close()