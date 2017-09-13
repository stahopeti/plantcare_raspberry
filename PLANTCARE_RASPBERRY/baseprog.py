#import serial

#ser = serial.Serial('/dev/ttyUSB0',9600)
#s = [0]
#while True:
#	read_serial=ser.readline()
#	s[0] = str(int (ser.readline(),16))
#	print s[0]
#	print read_serial

	
import time
import serial

ser = serial.Serial(
    port='/dev/ttyUSB1',
    baudrate=9600,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.SEVENBITS
)

ser.isOpen()

print 'Enter your commands below.\r\nInsert "exit" to leave the application.'

input=1
out = ''
while 1 :
    # get keyboard input
    input = raw_input(">> ")
    if input == 'exit':
        ser.close()
        exit()
    else:
        # send the character to the device
        # (note that I happend a \r\n carriage return and line feed to the characters - this is requested by my device)
        ser.write(input)
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(1)
        while ser.inWaiting() > 0:
            out += ser.read(1)
		
	print out
	out = ''
    
