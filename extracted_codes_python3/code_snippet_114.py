#!/usr/bin/python
#
# PiPlate.py: Display important information on Adafruit LCD Screen for RPi
#
# Copyright (C) 2016 Devon J. Smith
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Module imports
import time
import Adafruit_CharLCD as LCD
import time
import subprocess	
import re
import argparse

# Initialize the LCD using the pins 
lcd = LCD.Adafruit_CharLCDPlate()

# Arguments Parser
parser = argparse.ArgumentParser()
parser.add_argument('--start')
args = parser.parse_args()

def getCpuTemp():
        with open('/sys/class/thermal/thermal_zone0/temp') as f:
            readableTemp = float(f.read())/1000.
            return repr(readableTemp) + 'C'


def getCpuGov():
	with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq') as f:
	    speed = int(f.read())/1000
	    return repr(speed) + 'MHz'


def getIPAddress(ifname):
	ipAddrOut = subprocess.getoutput('ip addr show dev ' + ifname + ' | grep inet | awk \'NR=1{printf $2; exit}\'')
	return ipAddrOut


# Begin Program Logic
lcd.clear()

hostname = subprocess.getoutput('hostname')
lcd.message(hostname + ' is\nalive!!')
time.sleep(5)
lcd.clear()

if args.start:
	while 1:
		h = 0
		i = 0
	
		# Display IP Addresses
		while h < 7:
			lcd.message(" eth0: " + getIPAddress('eth0') + "\n" + " wlan0: " + getIPAddress('wlan0'))
			lcd.move_left()
			time.sleep(1)
			h += 1
		time.sleep(2)
		lcd.clear()
	
		# Display CPU Temp and CPU gov setting 
		while i < 3:
			lcd.autoscroll(lcd.message(" CPU Temp: " + getCpuTemp() + "\n" + " CPU Gov: " + getCpuGov()))
			lcd.move_left()
			time.sleep(1)
			i += 1
		time.sleep(2)
		lcd.clear()
