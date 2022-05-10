"""
author: Jerry Wu
all tasks to run are included in this file
"""
import os
import time
import threading

import RPi.GPIO as GPIO
from flask import Flask, render_template, redirect

import go_to_bed

### constants ###
MIN_DELAY = 10          # delay for tasks need to update within minute precision
FAST_DELAY = 0.01       # delay for tasks need to update immediately
SNOOZE_TIME = 10        # snooze time in minutes
SOUND_PATH = "sound/Let Her Go.mp3"  # path to sound file
# FUTURE scan for available alarm music in the sound folder
# available_files = []
# for (dirpath, dirnames, filenames) in os.walk("./sound"):
#     available_files.extend(filenames)
BED_TIME_THRESHOLD = 5  # minutes
SETTING_ITEM = ['bed time', 'wake up time']
LED_ON = GPIO.LOW
LED_OFF = GPIO.HIGH

# MAIN_STATUS: 0: wakeup, 1: sleep, 2: alarm
MAIN_STATUS = 'main status'
MAIN_STATUS_WAKEUP = 0
MAIN_STATUS_NEED_SLEEP = 1
MAIN_STATUS_SLEEP = 2
MAIN_STATUS_ALARM = 3
# ALARM_SWITCH: 0: on, 1: off
ALARM_STATUS = 'alarm status'
ALARM_ON = 0
ALARM_OFF = 1
# OLED_STATUS
OLED_STATUS = 'oled status'
OLED_DISPLAY = 0
OLED_SETTING = 1
OLED_SET_HOUR = 2
OLED_SET_MINUTE = 3

# setting status  TODO: when oled timeout or confirm, update status
# indicate which option is currently selected
SETTING_SELECTION = 0
# display time on oled
SETTING_TIME = 1

# global variables
current_status = {MAIN_STATUS: MAIN_STATUS_WAKEUP,
                  ALARM_STATUS: ALARM_OFF,
                  OLED_STATUS: OLED_DISPLAY}
bed_time = [22, 30]     # time to sleep (hour, minute)
today_bed_time = 0      # today's bed time (time.time())
up_time = [7, 0]        # time to wake up (hour, minute)
alarm_time = up_time    # time to play alarm clock sound (hour, minute)
sleep_info = []         # list to store sleep info (time, follow schedule)
light_threshold = 2     # threshold voltage for light sensor, user tunable
time_12_hour = False    # 12 hour mode or 24 hour mode
setting_status = {SETTING_SELECTION: 0,
                  SETTING_TIME: bed_time}
settings_info = [['sleep time', f'{bed_time[0]}:{bed_time[1]}'],
                 ['wake time', f"{up_time[0]}:{up_time[1]}"],
                 ['volume', '50%'],
                 ['brightness', '50%'],
                 ['light sensitivity', light_threshold],
                 ['12 hour format', time_12_hour]]
friends_sleep_info = [('Jerry', '83%'), ('Tom', '75%'), ('George', '50%')]

# GPIO pins
SNOOZE_BUT = 24
STOP_BUT = 23
RED_LED = 25
GREEN_LED = 26
ALARM_SWITCH = 22
ENCODER_L = 14
ENCODER_R = 15
ENCODER_BUT = 16

### onetime tasks ###


def simple_GPIO_setup():
    """
    setup some devices that only need input or output
    devices: red/green LEDs, snooze button, stop button, alarm switch
    """

    GPIO.setmode(GPIO.BCM)

    # setup red/green LED
    GPIO.setup(RED_LED, LED_OFF)
    GPIO.setup(GREEN_LED, LED_OFF)

    # setup stop/pause button pull up by default
    GPIO.setup(SNOOZE_BUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(SNOOZE_BUT, GPIO.RISING, callback=pause_alarm)
    GPIO.setup(STOP_BUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(STOP_BUT, GPIO.RISING, callback=stop_alarm)

    # setup alarm switch pull up by default
    GPIO.setup(ALARM_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    current_status[ALARM_STATUS] = GPIO.input(ALARM_SWITCH)
    GPIO.add_event_detect(ALARM_SWITCH, GPIO.BOTH, callback=alarm_switch)

    # setup encoder
    # default to ground
    GPIO.setup(ENCODER_L, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ENCODER_R, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ENCODER_BUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # add event detect
    GPIO.add_event_detect(ENCODER_L, GPIO.FALLING,
                          callback=encoder_rotate, bouncetime=20)
    GPIO.add_event_detect(ENCODER_BUT, GPIO.RISING, callback=encoder_but)
    # add timer
    global encoder_ccw_time, encoder_cw_time
    encoder_ccw_time = time.time()
    encoder_cw_time = time.time()


def peripheral_setup():
    """
    setup all the peripherals
    peripherals: rfid, oled, clock, speaker
    """

    global rfid, oled, clock, speaker, light_sensor
    # setup RFID
    rfid = go_to_bed.RFID()

    # setup OLED (I2C)
    oled = go_to_bed.OLED()

    # setup led
    clock = go_to_bed.Clock()

    # setup speaker
    speaker = go_to_bed.Speaker()
    speaker.set_sound(SOUND_PATH)  # FUTURE: let user choose sound

    # setup light sensor
    light_sensor = go_to_bed.ADC()


# setup webpage
webpage_flask = Flask(__name__, static_folder='assets')


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
        GPIO.output(GREEN_LED, LED_ON)
    else:
        current_status[ALARM_STATUS] = ALARM_OFF
        GPIO.output(GREEN_LED, LED_OFF)


def pause_alarm(channel):
    """
    callback function to pause the alarm
    """

    # debounce, wait for 20 milliseconds
    time.sleep(0.020)

    if GPIO.input(channel):
        # stop sound
        speaker.stop_sound()

        if current_status[MAIN_STATUS] == MAIN_STATUS_ALARM:
            # snooze alarm
            hour, minute, _ = get_time()
            set_time(alarm_time, hour, (minute + SNOOZE_TIME))

        # act as back button
        elif current_status[OLED_STATUS] == OLED_SETTING:
            setting_status[SETTING_SELECTION] = 0  # set selection back to 0
            current_status[OLED_STATUS] = OLED_DISPLAY
            oled_update_display()
        elif current_status[OLED_STATUS] == OLED_SET_HOUR:
            current_status[OLED_STATUS] = OLED_SETTING
            oled_update_display()
        elif current_status[OLED_STATUS] == OLED_SET_MINUTE:
            current_status[OLED_STATUS] = OLED_SET_HOUR
            oled_update_display()


def stop_alarm(channel):
    """
    callback function to stop alarm clock. If button pushed, alarm is stopped
    """

    # debounce, wait for 20 milliseconds
    time.sleep(0.020)

    if GPIO.input(channel):
        # turn off alarm
        speaker.stop_sound()

        if current_status[MAIN_STATUS] == MAIN_STATUS_ALARM:
            # set MAIN_STATUS to wakeup
            current_status[MAIN_STATUS] = MAIN_STATUS_WAKEUP
            oled_update_display()

            # set alarm_time to up_time
            set_time(alarm_time, *up_time)


def encoder_rotate(channel):
    assert channel == ENCODER_L

    global encoder_ccw_time, encoder_cw_time
    if GPIO.input(ENCODER_R) != GPIO.HIGH:
        if time.time() - encoder_cw_time < 0.1:
            pass  # still clockwise
        else:
            encoder_ccw_time = time.time()
            print("counter clockwise")  # TODO: test
            # TODO
            if current_status[OLED_STATUS] == OLED_SETTING:
                setting_status[SETTING_SELECTION] += 1
            elif current_status[OLED_STATUS] == OLED_SET_HOUR:
                setting_status[SETTING_TIME][0] = (
                    setting_status[SETTING_TIME][0] + 1) % 24
            elif current_status[OLED_STATUS] == OLED_SET_MINUTE:
                setting_status[SETTING_TIME][1] = (
                    setting_status[SETTING_TIME][1] + 1) % 60
    else:
        if time.time() - encoder_ccw_time < 0.1:
            pass  # still counter clockwise
        else:
            encoder_cw_time = time.time()
            print("clockwise")  # TODO: test
            # TODO
            if current_status[OLED_STATUS] == OLED_SETTING:
                setting_status[SETTING_SELECTION] -= 1
            elif current_status[OLED_STATUS] == OLED_SET_HOUR:
                setting_status[SETTING_TIME][0] = (
                    setting_status[SETTING_TIME][0] - 1) % 24
            elif current_status[OLED_STATUS] == OLED_SET_MINUTE:
                setting_status[SETTING_TIME][1] = (
                    setting_status[SETTING_TIME][1] - 1) % 60

    oled_update_display()


def encoder_but(channel):
    time.sleep(0.020)
    if GPIO.input(channel):
        print("Button pressed")  # TODO: test
        if current_status[OLED_STATUS] == OLED_DISPLAY:
            current_status[OLED_STATUS] = OLED_SETTING
            oled_update_display()
        elif current_status[OLED_STATUS] == OLED_SETTING:
            # determine whether to set bed time or up time
            if setting_status[SETTING_SELECTION] == 0:
                setting_status[SETTING_TIME] = bed_time
            else:
                setting_status[SETTING_TIME] = up_time

            current_status[OLED_STATUS] = OLED_SET_HOUR
            oled_update_display()
        elif current_status[OLED_STATUS] == OLED_SET_HOUR:
            current_status[OLED_STATUS] = OLED_SET_MINUTE
            oled_update_display()
        elif current_status[OLED_STATUS] == OLED_SET_MINUTE:
            # store current setting
            if setting_status[SETTING_SELECTION] == 0:
                bed_time[0] = setting_status[SETTING_TIME][0]
                bed_time[1] = setting_status[SETTING_TIME][1]
                print(bed_time)  # TODO: test
            else:
                up_time[0] = setting_status[SETTING_TIME][0]
                up_time[1] = setting_status[SETTING_TIME][1]
                print(up_time)  # TODO: test

            setting_status[SETTING_SELECTION] = 0
            current_status[OLED_STATUS] = OLED_DISPLAY
            oled_update_display()


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


def oled_update_display():
    """
    change the oled display according to different status
    should be manual called everytime the current_status is changed

    FUTURE: separate process to check for state change and call oled_display
    automatically?
    """

    oled.clear_display()

    if current_status[OLED_STATUS] == OLED_DISPLAY:
        if current_status[MAIN_STATUS] == MAIN_STATUS_WAKEUP:
            oled.add_text('wake up')  # TODO: change to picture
        elif current_status[MAIN_STATUS] == MAIN_STATUS_NEED_SLEEP:
            oled.add_text('need sleep')  # TODO: change to picture
        elif current_status[MAIN_STATUS] == MAIN_STATUS_SLEEP:
            oled.add_text('sleep')  # TODO: change to picture
        elif current_status[MAIN_STATUS] == MAIN_STATUS_ALARM:
            oled.add_text('alarm')  # TODO: change to picture
    elif current_status[OLED_STATUS] == OLED_SETTING:
        for i in range(len(SETTING_ITEM)):
            if i == (setting_status[SETTING_SELECTION] % len(SETTING_ITEM)):
                oled.add_text('> ' + SETTING_ITEM[i])
            else:
                oled.add_text(SETTING_ITEM[i])
    elif current_status[OLED_STATUS] == OLED_SET_HOUR:
        h, m = setting_status[SETTING_TIME]
        oled.add_text(f'-{h:02d}-:{m:02d}')
    elif current_status[OLED_STATUS] == OLED_SET_MINUTE:
        h, m = setting_status[SETTING_TIME]
        oled.add_text(f'{h:02d}:-{m:02d}-')

    oled.update_display()


@webpage_flask.route("/")
def home():
    return redirect("/index")


@webpage_flask.route("/index")
def home_template():
    return render_template("index.html",
                           sleep_info=sleep_info,
                           up_time=f"{up_time[0]}:{up_time[1]}",
                           bed_time=f"{bed_time[0]}:{bed_time[1]}",
                           other_info=friends_sleep_info,
                           status="TODO")


@webpage_flask.route("/settings")
def settings_template():
    global settings_info
    settings_info = [['sleep time', f'{bed_time[0]}:{bed_time[1]}'],
                     ['wake time', f"{up_time[0]}:{up_time[1]}"],
                     ['volume', '50%'],
                     ['brightness', '50%'],
                     ['light sensitivity', light_threshold],
                     ['12 hour format', time_12_hour]]
    return render_template("settings.html",
                           settings=settings_info)


### background tasks ###
def run_webpage():
    """
    process that runs the webpage continuously
    """
    # TODO
    pass


def update_time():
    """
    update the time shown on LED every 1 seconds, the ':' will blink
    """

    while True:
        hour, minute, _ = get_time()
        if time_12_hour:
            hour %= 12
            if hour == 0:
                hour = 12

        clock.set_display(str(hour)+":"+str(minute))
        time.sleep(1)
        clock.set_display(str(hour)+str(minute))
        time.sleep(1)


def check_sleeping():
    """
    process that check whether light turns off and phone is nearby RFID
    """

    while True:
        if current_status[MAIN_STATUS] == MAIN_STATUS_WAKEUP:
            h, m, _ = get_time()
            if h == bed_time[0] and m == bed_time[1]:
                current_status[MAIN_STATUS] = MAIN_STATUS_NEED_SLEEP
                oled_update_display()
                today_bed_time = time.time()
                GPIO.output(RED_LED, LED_ON)

        if current_status[MAIN_STATUS] == MAIN_STATUS_NEED_SLEEP:
            # check phone
            rfid.read()  # will block until RFID is read
            voltage = light_sensor.read()

            # check light sensor
            if voltage <= light_threshold:
                current_status[MAIN_STATUS] = MAIN_STATUS_SLEEP
                oled_update_display()

                # if sleep within BED_TIME_THRESHOLD, count as follow schedule
                if (time.time() - today_bed_time)/60 <= BED_TIME_THRESHOLD:
                    sleep_info.append(bed_time, True)
                else:
                    h, m, _ = get_time()
                    sleep_info.append([h, m], False)
                    
                GPIO.output(RED_LED, LED_OFF)

        time.sleep(MIN_DELAY)


def encoder_operation():
    """
    process for handling encoder operation based on the current status
    """

    # TODO
    pass


def alarm_clock():
    """
    process for alarm clock
    """

    while True:
        print("--- alarm clock ---")  # TODO: test
        print("alarm time", alarm_time)  # TODO: test
        print("current time", get_time())  # TODO: test

        h, m, _ = get_time()
        if current_status[MAIN_STATUS] == MAIN_STATUS_SLEEP:
            if h == up_time[0] and m == up_time[1]:
                if current_status[ALARM_STATUS] == ALARM_ON:
                    # set status to alarm if sleep before
                    current_status[MAIN_STATUS] = MAIN_STATUS_ALARM
                else:
                    current_status[MAIN_STATUS] = MAIN_STATUS_WAKEUP
                oled_update_display()

        if current_status[MAIN_STATUS] == MAIN_STATUS_ALARM:
            if h == alarm_time[0] and m == alarm_time[1]:
                # move next alarm to SNOOZE_TIME minutes later
                inc_time(alarm_time, minute=SNOOZE_TIME)
                speaker.play_sound()  # TODO
        print("alarm time", alarm_time)  # TODO: test
        print("--- alarm clock ---")  # TODO: test

        time.sleep(MIN_DELAY)


if __name__ == "__main__":
    # one time tasks
    simple_GPIO_setup()
    peripheral_setup()

    # background tasks
    background_tasks = [alarm_clock, update_time]

    # start background tasks
    for task in background_tasks:
        thread = threading.Thread(target=task, daemon=True)
        thread.start()

    # turn on webpage
    webpage_flask.run(host='0.0.0.0', port=80, debug=True, threaded=True)

    # TODO: test only
    try:
        print("program started")
        ex = input('type exit to exit: ')
        while ex != 'exit':
            ex = input('type exit to exit: ')
    except KeyboardInterrupt:
        pass
    print("program finished, perform GPIO cleanup")
    GPIO.cleanup()
