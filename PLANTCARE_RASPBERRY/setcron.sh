#!/bin/bash

#input parameter: 
#$1 pot_id $2 sunset time for pot_id$1 daily script 
#$3 pot_id $4 sunset time for pot_id$3 daily script 
#$5 pot_id $6 sunset time for pot_id$5 daily script 
#...

sudo crontab -u root -l > mycron
sed -i '/\#POT ID: 1/Q' mycron

#grep -B 9999999 "\#POTID: 1"

#sed '/\#POTID: 1/,$d' mycron

if [[ $1 ]]; then
	echo \#POT ID: $1 >> mycron
	echo '@reboot /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/start5secondsscript.sh '$1' >> /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/logs/log10min.log 2>&1' >> mycron
	echo '*/10 * * * * /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/start10minutesscript.sh '$1' >> /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/logs/log10min.log 2>&1' >> mycron
	echo "$2" ' /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/startdailyscript.sh '$1' >> /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/logs/logdaily.log 2>&1' >> mycron
fi

if [[ $3 ]]; then
	echo \#POT ID: $3 >> mycron
	echo '@reboot /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/start5secondsscript.sh '$3' >> /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/logs/log10min.log 2>&1' >> mycron
	echo '*/10 * * * * /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/start10minutesscript.sh '$3' >> /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/logs/log10min.log 2>&1' >> mycron
	echo "$4" ' /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/startdailyscript.sh '$3' >> /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/logs/logdaily.log 2>&1' >> mycron
fi
	
sudo crontab -u root mycron
sudo rm mycron