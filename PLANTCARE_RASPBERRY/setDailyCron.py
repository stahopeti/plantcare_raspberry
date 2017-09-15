import subprocess
import mysql.connector
import string

db_config = {
	'user': 'root', 
	'password': 'schlieffenplan', 
	'host': 'localhost', 
	'database': 'PLANT_CARE'
}

db_cnx = mysql.connector.connect(**db_config)
db_cursor = db_cnx.cursor()

get_pots_sunset = ('select ID, SUNSET from POTS;')
db_cursor.execute(get_pots_sunset)

pot_id_sunset_list = db_cursor.fetchall()

setdaily_arguments = ''

#01:34:56

for element in pot_id_sunset_list:
	id_str = str(element[0])
	time_str = str(element[1])
	setdaily_arguments = setdaily_arguments + id_str + ' "' + time_str[3] + time_str[4] + ' ' + time_str[0] + time_str[1] + ' * * *" '

subprocess.call("./setcron.sh " + setdaily_arguments, shell=True)

