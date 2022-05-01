"""
author: Jerry Wu

This file shows a simple demo of how to use speaker.py module
"""

import time
import sys
import RPi.GPIO as GPIO
import pyttsx3
import schedule

import go_to_bed

SNOOZE_BUT = 24                     # pins connects to snooze button
STOP_BUT = 23                       # pins connects to stop button
VOLUME = 1                          # volume range 0 to 1

GPIO.setmode(GPIO.BCM)
GPIO.setup(SNOOZE_BUT, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # pull up by default
GPIO.setup(STOP_BUT, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # pull up by default

################################################################
# speaker usage
print("=== speaker demo ===")

print("\n" + "-"*20 +
      "\nPress button connect on pin", SNOOZE_BUT, "to pause/resume\n" +
      "Press button connect on pin", STOP_BUT, "to stop\n" +
      "Press 'Ctrl C' to skip demo\n"
      + "-"*20 + "\n")

# initialize speaker object
speaker = go_to_bed.Speaker()
# set the sound you want to play
speaker.set_sound("sound/Let Her Go.mp3")

### play sound ###
print("\n--- play sound demo ---")


def pause_button(channel):
    """
    callback function to pause/resume sound
    """

    # debounce, wait for 20 milliseconds
    time.sleep(0.020)

    if not GPIO.input(channel):
        if speaker.is_paused():
            speaker.resume()
            print("sound resumed")
        else:
            speaker.pause()
            print("sound paused")


def stop_button(channel):
    """
    callback function to stop sound
    """

    speaker.stop_sound()


# pause/resume music when button pressed
GPIO.add_event_detect(SNOOZE_BUT, GPIO.FALLING, callback=pause_button)
# stop music when buttoin pressed
GPIO.add_event_detect(STOP_BUT, GPIO.FALLING, callback=stop_button)

# start playing, non-blocking. The sound will stop if program ends or
# stop_sound() is called
speaker.play_sound()
print("Initial volume:", speaker.volume())

try:
    while not speaker.is_stopped():
        time.sleep(0.01)
    print("finish playing")
except KeyboardInterrupt:
    print("Ctrl C pressed, sound stopped")
    speaker.stop_sound()

# remove event detect after test
GPIO.remove_event_detect(SNOOZE_BUT)
GPIO.remove_event_detect(STOP_BUT)

### TTS ###
print("\n--- TTS demo ---")
try:
    # # setup tts engine
    voice_engine = pyttsx3.init()
    # voice_engine.setProperty('rate', 170)
    voice_engine.setProperty('volume', VOLUME)
    voice_engine.setProperty('voice', "english-us")

    print('"Failed to wake you up"')
    voice_engine.say("Failed to wake you up")
    voice_engine.runAndWait()

    print('"Good Morning!"')
    voice_engine.say("Good Morning!")
    voice_engine.runAndWait()
except KeyboardInterrupt:
    print("Ctrl C pressed, TTS stopped")

### schedule alarm ###
print("\n--- schedule alarm demo ---")


def stop_alarm(channel):
    """
    callback function to pause/resume sound
    """

    speaker.stop_sound()


# stop alarm when button pressed
GPIO.add_event_detect(STOP_BUT, GPIO.FALLING, callback=stop_alarm)


def alarm():
    # set volume to max
    speaker.mixer.music.set_volume(VOLUME)
    # start alarm
    speaker.play_sound()
    print("Alarming... Press button to stop")

    while not speaker.is_stopped():
        if speaker.is_paused():
            break

    # if the sound finish playing and the user haven't push the button to
    # pause it, we consider the alarm failed to wake user up
    if speaker.is_stopped():
        print("sound stopped, initialize new alarm")
    else:
        print("sound paused, initialize new alarm")
    speaker.stop_sound()


# aram = schedule.every().day.at("07:00").do(alarm)  # repeat everyday at 7 AM
aram = schedule.every(3).seconds.do(alarm)  # repeat every 3 seconds

# nohup usage: https://www.computerhope.com/unix/unohup.htm#:~:text=nohup%20command%20%3E%20file%22.-,Examples,-nohup%20mycommand
print("Program running... (use nohup to keep runninging the background)")

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("Ctrl C pressed, schedule stopped")

# cancel schedule
schedule.cancel_job(alarm)


################################################################
# led usage
print('\n\n\n')
print("=== led demo ===")
SLEEP_TIME = 1

# initialize LED
led = go_to_bed.LED()

### display ###
print("\n--- display demo ---")
try:
    # display 8888
    led.set_display("88888888")  # str more than 4 will be auto truncate
    print(led.get_display())
    time.sleep(SLEEP_TIME)

    # clear display by setting empty string
    led.set_display("")
    print("clear display")
    time.sleep(SLEEP_TIME)

    def scrolling_message(led, msg, delay=0.5):
        """
        display scrolling text
        """

        width = 4
        padding = " " * width
        msg = padding + msg + padding

        for i in range(len(msg) - width + 1):
            led.set_display(msg[i:i + width])
            time.sleep(delay)

    # scrolling text
    print("scrolling 31415926")
    scrolling_message(led, "31415926")

    # display 12:34
    led.set_display("12:34")  # if third char is :, : will be turn on
    print(led.get_display())
    time.sleep(SLEEP_TIME)
except KeyboardInterrupt:
    print("Ctrl C pressed, display stopped")

### brightness ###
print("\n--- brightness demo ---")
try:
    # adjust brightness: 0 - 100
    # there's only 32 brightness level in hardware
    print("gradually increase brightness")
    for i in range(101):
        led.set_brightness(i)
        time.sleep(0.05)
    time.sleep(SLEEP_TIME)

    print("set 50% brightness")
    led.set_brightness(50)
    time.sleep(SLEEP_TIME)

    print("increase birghtness by 10%")
    led.increase_brightness()
    time.sleep(SLEEP_TIME)

    print("decrease birghtness by 10%")
    led.decrease_brightness()
    time.sleep(SLEEP_TIME)
except KeyboardInterrupt:
    print("Ctrl C pressed, brightness stopped")

print("All demo done")
