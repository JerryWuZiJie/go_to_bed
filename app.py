"""
author: Jerry Wu
all tasks to run are included in this file
"""
import os
import time
import threading

import schedule
import RPi.GPIO as GPIO

import go_to_bed

### onetime tasks ###
GPIO.setmode(GPIO.BCM)
# TODO
# setup RFID (SPI 0 1)
rfid = go_to_bed.RFID()

# setup ADC for photodiode (SPI 1, 0)
adc = go_to_bed.ADC()

# setup OLED (I2C)
oled = go_to_bed.OLED()

# setup push buttons
# TODO: need to specify pins
UP_PIN = 0
DOWN_PIN = 0
OK_PIN = 0
CANCEL_PIN = 0
GPIO.setup(UP_PIN, GPIO.IN)
GPIO.setup(DOWN_PIN, GPIO.IN)
GPIO.setup(OK_PIN, GPIO.IN)
GPIO.setup(CANCEL_PIN, GPIO.IN)

# setup led (SPI 0 0)
led = go_to_bed.LED()

# setup speaker
speaker = go_to_bed.Speaker()

# setup webpage

# scan for available alarm music in the sound folder
available_files = []
for (dirpath, dirnames, filenames) in os.walk("./sound"):
    available_files.extend(filenames)


### background tasks ###
def run_webpage():
    """
    process that runs the webpage continuously
    """
    # TODO
    pass


def update_time():
    """
    process that update the display time on LED continuously
    """
    led.set_display(time.strftime("%I:%M", time.localtime()))


def check_sleeping():
    """
    process that check whether light turns off and phone is nearby RFID
    """
    # TODO
    pass


def alarm_clock():
    """
    process for alarm clock, will be add to schedule
    """
    # TODO
    pass
