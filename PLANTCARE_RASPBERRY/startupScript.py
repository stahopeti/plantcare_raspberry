import time
import string
import schedule
import subprocess
import mysql.connector
import serial.tools.list_ports
from serial import SerialException

db_config = {
	'user': 'root', 
	'password': 'schlieffenplan', 
	'host': 'localhost', 
	'database': 'PLANT_CARE'
}

get_pots = (
	"select COUNT(*) from POTS;"
)

update_pots = (
	"update POTS set SERIAL_PORT = %s where ID = %s")
	
#check the connected serial_ports
list = serial.tools.list_ports.comports()

#
#
# HA POTS uRES, NeZNI A SZERVEREN HOGY VAN-E create pot COMMAND
# letoltjuk megcsinaljuk reboot
#
#

def connectToDB():
	try:	
		db_cnx = mysql.connector.connect(**db_config)
	except mysql.connector.Error, e:
		time.sleep(5)
		connectToDB()
	return

connectToDB()
	
db_cnx = mysql.connector.connect(**db_config)
db_cursor = db_cnx.cursor()

db_cursor.execute(get_pots)
count_of_pots = db_cursor.fetchall()[0][0]

if( count_of_pots == 0 ):
	print "no pots in db bruh"
	schedule.every(1).minutes.do(subprocess.Popen('python /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/checkNewPots.py ' + str(1), shell=True))
	while True:
		schedule.run_pending()
		time.sleep(1)
else:
	for element in list:
		device = element.device
		try:
			ser = serial.Serial(
			port=device,
			baudrate=9600,
			parity=serial.PARITY_ODD,
			stopbits=serial.STOPBITS_TWO,
			bytesize=serial.SEVENBITS)
			ser.isOpen()
			time.sleep(3)

			input = 'C'
			out = ''
			ser.write(input)
			time.sleep(1)
			while ser.inWaiting() > 0:
				out += ser.read(1)
				
			if (out != ''):
				print out
				
			db_cursor.execute(update_pots, (device, out))
			db_cnx.commit()

			ser.flush()
			
		except SerialException as ex:
			print device + ' isn\'t an arduino'
		except mysql.connector.Error as ex:
			print ex



	#getting pots, and starting a process for each
	get_pots_ID = ('select ID from POTS;')
	db_cursor.execute(get_pots_ID)

	pot_id_list = db_cursor.fetchall()

	db_cursor.close()
	db_cnx.close()	

	for element in pot_id_list:
		id_str = str(element[0])
		subprocess.Popen("python /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/baseprog.py " + id_str, shell=True)
