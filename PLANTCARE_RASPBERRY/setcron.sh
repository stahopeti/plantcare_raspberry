#!/bin/bash

sudo crontab -u root -l > mycron

echo '@reboot /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/start10minutesscrip.sh >> /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/logs/log10min.log 2>&1' >> mycron
echo '*/10 * * * * /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/start10minutesscrip.sh >> /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/logs/log10min.log 2>&1' >> mycron

sudo crontab -u root mycron
sudo rm mycron