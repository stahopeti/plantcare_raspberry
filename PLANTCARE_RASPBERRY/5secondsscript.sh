#!/bin/bash

while true
do
    python /home/pi/plantcare_raspberry/PLANTCARE_RASPBERRY/lightSampling.py $1
    sleep 5
done
