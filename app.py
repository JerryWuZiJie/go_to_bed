"""
author: Jerry Wu
all tasks to run are included in this file
"""
import os
import time
import threading

import RPi.GPIO as GPIO

import go_to_bed

### constants ###
MIN_DELAY = 10          # delay for tasks need to update within minute precision
SNOOZE_TIME = 10        # snooze time in minutes
SOUND_PATH = "sound/Let Her Go.mp3" # path to sound file
# MAIN_STATUS: 0: wakeup, 1: sleep, 2: alarm
MAIN_STATUS = 'main status'
MAIN_STATUS_WAKEUP = 0
MAIN_STATUS_SLEEP = 1
MAIN_STATUS_ALARM = 2
# ALARM_SWITCH: 0: on, 1: off
ALARM_STATUS = 'alarm status'
ALARM_ON = 0
ALARM_OFF = 1

# global variables
current_status = {MAIN_STATUS: MAIN_STATUS_WAKEUP,
                  ALARM_STATUS: ALARM_OFF}
bed_time = [22, 30]     # time to sleep (hour, minute)
up_time = [7, 0]        # time to wake up (hour, minute)
alarm_time = up_time    # time to play alarm clock sound (hour, minute)

# GPIO pins
SNOOZE_BUT = 24
STOP_BUT = 23
RED_LED = 25
GREEN_LED = 26
ALARM_SWITCH = 22

### onetime tasks ###

GPIO.setmode(GPIO.BCM)
# setup red/green LED
GPIO.setup(RED_LED, GPIO.LOW)  # low by default
GPIO.setup(GREEN_LED, GPIO.LOW)  # low by default
# setup stop/pause button
GPIO.setup(SNOOZE_BUT, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # pull up by default
GPIO.setup(STOP_BUT, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # pull up by default
# setup alarm switch
# pull up by default
GPIO.setup(ALARM_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# setup RFID
rfid = go_to_bed.RFID()

# setup OLED (I2C)
oled = go_to_bed.OLED()

# setup led
led = go_to_bed.LED()

# setup speaker
speaker = go_to_bed.Speaker()
speaker.set_sound(SOUND_PATH)  # FUTURE: let user choose sound

# setup webpage

# scan for available alarm music in the sound folder
available_files = []
for (dirpath, dirnames, filenames) in os.walk("./sound"):
    available_files.extend(filenames)


### interrupt ###


def alarm_switch(channel):
    """
    callback function to determine alarm switch state
    if switch is on, turn off the alarm, green LED off
    otherwise, turn on the alarm, green LED on
    """

    # debounce, wait for 20 milliseconds
    time.sleep(0.020)

    if GPIO.input(channel) == ALARM_ON:
        current_status[ALARM_STATUS] = ALARM_ON
        GPIO.output(GREEN_LED, GPIO.LOW)
    else:
        current_status[ALARM_STATUS] = ALARM_OFF
        GPIO.output(GREEN_LED, GPIO.HIGH)


current_status[ALARM_STATUS] = GPIO.input(ALARM_SWITCH)
GPIO.add_event_detect(ALARM_SWITCH, GPIO.BOTH, callback=alarm_switch)


def pause_alarm(channel):
    """
    callback function to pause the alarm
    """

    # debounce, wait for 20 milliseconds
    time.sleep(0.020)

    if not GPIO.input(channel):
        # stop sound
        speaker.stop_sound()
        
        # snooze alarm
        hour, minute, _ = get_time()
        set_time(alarm_time, hour, (minute + SNOOZE_TIME))


GPIO.add_event_detect(SNOOZE_BUT, GPIO.FALLING, callback=pause_alarm)


def stop_alarm(channel):
    """
    callback function to stop alarm clock. If button pushed, alarm is stopped
    """

    # debounce, wait for 20 milliseconds
    time.sleep(0.020)

    if not GPIO.input(channel):
        # turn off alarm
        speaker.stop_sound()

        # set MAIN_STATUS to wakeup
        current_status[MAIN_STATUS] = MAIN_STATUS_WAKEUP

        # set alarm_time to up_time
        set_time(alarm_time, *up_time)


GPIO.add_event_detect(STOP_BUT, GPIO.FALLING, callback=stop_alarm)


### helper functions ###
def get_time():
    """
    get current time

    @return: hour, min, sec
    """

    current_time = time.localtime()
    hour = current_time.tm_hour
    minute = current_time.tm_min
    sec = current_time.tm_sec

    return hour, minute, sec


def get_date():
    """
    get today's date

    @return: month, day
    """

    current_time = time.localtime()
    month = current_time.tm_mon
    day = current_time.tm_mday

    return month, day


def set_time(time_object, hour, minute):
    """
    set time given hour and min in 24hr format

    @param time_object: time object to set
    @param hour: hour to set
    @param min: minute to set
    """

    time_object[1] = minute % 60
    time_object[0] = (hour + minute // 60) % 24


def inc_time(time_object, hour=0, minute=0):
    """
    increment 

    @param time_object: time object to increase
    @param hour: hour increment
    @param min: minute to increment
    """

    set_time(time_object, time_object[0] + hour, time_object[1] + minute)


### background tasks ###
def run_webpage():
    """
    process that runs the webpage continuously
    """
    # TODO
    pass


def update_time():
    """
    update the time shown on LED every MIN_DELAY seconds
    """

    while True:
        hour, minute, _ = get_time()
        led.set_display(str(hour)+":"+str(minute))
        time.sleep(MIN_DELAY)


def check_sleeping():
    """
    process that check whether light turns off and phone is nearby RFID
    """

    # TODO
    pass


def alarm_clock():
    """
    process for alarm clock
    """

    while True:
        time.sleep(MIN_DELAY)
        if current_status[ALARM_STATUS] == ALARM_ON:
            hour, minute, _ = get_time()
            if [hour, minute] == up_time and current_status[MAIN_STATUS] == MAIN_STATUS_SLEEP:
                # set status to alarm if sleep before
                current_status[MAIN_STATUS] = MAIN_STATUS_WAKEUP
            if [hour, minute] == alarm_time:
                if current_status[MAIN_STATUS] == MAIN_STATUS_WAKEUP:
                    # move next alarm to SNOOZE_TIME minutes later
                    inc_time(alarm_time, minute=SNOOZE_TIME)
                    speaker.play_sound()  # TODO
