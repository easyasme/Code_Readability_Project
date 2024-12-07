#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Run a recognizer using the Google Assistant Library.

The Google Assistant Library has direct access to the audio API, so this Python
code doesn't need to record audio. Hot word detection "OK, Google" is supported.

It is available for Raspberry Pi 2/3 only; Pi Zero is not supported.
"""

import logging
import platform
import subprocess
import sys

import aiy.assistant.auth_helpers
from aiy.assistant.library import Assistant
import aiy.audio
import aiy.voicehat
from google.assistant.library.event import EventType

import RPi.GPIO as GPIO
import time
from gpioController import GPIOController

from lcd_i2c import *

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)


SUB_PATH = "/home/pi/python/voicekit-pi-gpio"

def lcd_print(text):
    if(USE_LCD):
        lcd_print_wrap(text)


def power_off_pi():
    aiy.audio.say('Good bye!')
    subprocess.call('sudo shutdown now', shell=True)


def reboot_pi():
    aiy.audio.say('See you in a bit!')
    subprocess.call('sudo reboot', shell=True)


def say_ip():
    ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
    aiy.audio.say('My IP address is %s' % ip_address.decode('utf-8'))

def play_leds():
    process = SUB_PATH + "/led/led_patterns.py"
    print("running " + process + " ...")
    subprocess.Popen(process , shell=True)

def cooling_fan_on():
    process = SUB_PATH + "/motor/fan_on.py"
    print("running " + process + " ...")
    subprocess.Popen(process , shell=True)

def relays_on():
    process = SUB_PATH + "/relay/relay_on.py"
    print("running " + process + " ...")
    subprocess.Popen(process , shell=True)

def read_temperature():
    process = SUB_PATH + "/temperature/read_temp.py 22 12"
    print("running " + process + " ...")
    try:
        result = subprocess.check_output(process , shell=True)
        values = result.decode('utf-8').strip().split("|")
        print("temperature = " + values[0] + "C")
        print("humidity    = " + values[1] + "%")
        message = "the current temperature is " + values[0] + " celsius, with " + values[1] + " percent humidity"
        aiy.audio.say(message)
    except Exception as e:
            print("ERROR:", e)
            aiy.audio.say("cannot read the temperature at this time")
            return False

"""
names = ["light one","light two","light three","light four"]
operation_on_words = [" on "]
operation_off_words = [" off "]
"""

def is_found(keyword,text):
    words = text.lower().split(" ")
    keyword = keyword.lower()
    for word in words:
        if(word == keyword):
            return True
    return False

def is_request_on(input_text):
    for word in operation_on_words:
        #keyword = " " + word + " "
        #print("index of " + keyword + " = " + str(input_text.find(keyword)))
        if(is_found(word,input_text)):
            #print("on word found")
            return True
    return False

def is_request_off(input_text):
    for word in operation_off_words:
        if(is_found(word,input_text)):
            return True
    return False


def change_all_states(state):
    i = 0
    for control in controls:	    
        print("changing control " + str(i) + " to " + str(state))
        control.output(state)
        print("GPIO state for " + str(i) + " = " + str(control.input()))
    aiy.audio.say("OK !!")	

def change_gpio_state(index,state):

    # if index > number of control, change all
    if(index >= len(controls)):
        change_all_states(state)
    else:
       print("changing control " + str(index) + " to " + str(state))
       controls[index].output(state)
       print("GPIO state for " + str(index) + " = " + str(controls[index].input()))
       aiy.audio.say("OK !!")	

def control_gpio(index,input_text):
    print("detecting operation for control index: " + str(index))
    if(is_request_on(input_text)):
        print("ON requested")
        change_gpio_state(index,GPIO.HIGH)	
    elif(is_request_off(input_text)):    
        print("OFF requested")
        change_gpio_state(index,GPIO.LOW)
    else:
        aiy.audio.say("I don't understand the operation requested")

def handle_gpio_request(input_text):
    print("handling GPIO REQUEST")
    
    # find device names
    i = 0
    for name in names:
        if(input_text.find(name) > -1):
            # we'll handle the request ourself,
            # stop the assistant for further conversation
            assistant.stop_conversation()
            control_gpio(i,input_text)
        i = i + 1


def process_event(assistant, event):

    print("processing event: " + str(event.type))

    status_ui = aiy.voicehat.get_status_ui()
    if event.type == EventType.ON_START_FINISHED:
        status_ui.status('ready')
        if sys.stdout.isatty():
            print('Say "OK, Google" then speak, or press Ctrl+C to quit...')
            lcd_print("Say 'OK, Google' then speak")

    elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        status_ui.status('listening')
        lcd_print("I'm listening ...")

    elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
        print("")
        print("You said: '" + event.args['text'] + "'")
        print("")
        lcd_print(event.args['text'])
        text = event.args['text'].lower()
        if text == 'power off':
            assistant.stop_conversation()
            power_off_pi()
        elif text == 'reboot':
            assistant.stop_conversation()
            reboot_pi()
        elif text == 'ip address':
            assistant.stop_conversation()
            say_ip()
        elif text.replace("the ","") == 'turn on leds':
            assistant.stop_conversation()
            play_leds()
            aiy.audio.say("here they are, enjoy !")
        elif text.replace("the ","") == 'turn on cooling fan':
            assistant.stop_conversation()
            cooling_fan_on()
            aiy.audio.say("turning the fan on for 10 seconds")
        elif text.replace("the ","") == 'turn on switches':
            assistant.stop_conversation()
            relays_on()
            aiy.audio.say("turning the switches on for 5 seconds")
        elif text.replace("the ","") == 'read temperature':
            assistant.stop_conversation()
            aiy.audio.say("reading present temperature from the sensor, please wait")
            read_temperature()
        else:
            print("other things ...")
            handle_gpio_request(text)


    elif event.type == EventType.ON_END_OF_UTTERANCE:
        status_ui.status('thinking')

    elif (event.type == EventType.ON_CONVERSATION_TURN_FINISHED
          or event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT
          or event.type == EventType.ON_NO_RESPONSE):
        status_ui.status('ready')
        lcd_print("ready")

    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)

# voice hat servo pins
pins = [26,6,13,5]
names = ["switch one","switch two","switch three","switch four","everything"]
operation_on_words = ["on"]
operation_off_words = ["off"]

# GPIO controllers
controls = []

def init_gpio_controllers():
    i = 0
    for pin in pins:
        controls.append(GPIOController(pin,GPIO.LOW))
        print("control " + str(i) + " initiated for gpio pin " + str(pin))
        i = i + 1

# USE LCD
USE_LCD = True
    
def main():
    if platform.machine() == 'armv6l':
        print('Cannot run hotword demo on Pi Zero!')
        exit(-1)

    lcd_init()
    
try:
    #init the GPIO controllers
    print("initiating GPIO pins ...")
    init_gpio_controllers()
    time.sleep(2)

    print("getting assistant credentials ...")
    lcd_print("getting assistant credentials ...")
    credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
    print("starting assistant ...")
    with Assistant(credentials) as assistant:
        for event in assistant.start():
            process_event(assistant, event)

# End program cleanly with keyboard
except KeyboardInterrupt:
    print ("Quit")

    # Reset GPIO settings
    GPIO.cleanup()

if __name__ == '__main__':
    main()
