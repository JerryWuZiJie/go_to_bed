"""
author: Jerry Wu
all tasks to run are included in this file
"""
import os
import time

import schedule

import go_to_bed

### onetime tasks ###
### setup ###
# setup led
led = go_to_bed.LED()
# setup speaker
speaker = go_to_bed.Speaker()
# TODO
# setup RFID
# setup ADC for photodiode
# setup OLED
# setup push buttons
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
