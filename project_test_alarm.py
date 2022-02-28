"""
author: Jerry Wu

Test if the speaker can wake me up

Use the 'schedule' module, documentation can be found at
https://schedule.readthedocs.io/en/stable/
"""

import time
import sys

import schedule
import pyttsx3
import RPi.GPIO as GPIO

from utils import Speaker  # for speaker


GPIO.setmode(GPIO.BCM)

# pins connects to push button
BUTTON = 17
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # pull down by default


def pause_button(channel):
    """
    callback function to pause/resume sound
    """

    # debounce, wait for 20 milliseconds
    time.sleep(0.020)

    if GPIO.input(channel):
        speaker.pause()


# pause/resume music when button pressed
GPIO.add_event_detect(BUTTON, GPIO.RISING, callback=pause_button)


# setup tts engine
voice_engine = pyttsx3.init()
# voice_engine.setProperty('rate', 170)
voice_engine.setProperty('volume', 1.0)
voice_engine.setProperty('voice', "english-us")

# initialize speaker object
speaker = Speaker()
# set the sound you want to play
speaker.set_sound("sound/Let Her Go.mp3")


def alarm():
    try:
        # set volume to max
        speaker.mixer.music.set_volume(1)
        # start alarm
        speaker.play_sound()
        print("Alarming... Press button to stop")

        while not speaker.is_stopped():
            if speaker.is_paused():
                break

        # if the sound finish playing and the user haven't push the button to
        # pause it, we consider the alarm failed to wake user up
        if speaker.is_stopped():
            voice_engine.say("Failed to wake you up")
            voice_engine.runAndWait()
        else:
            voice_engine.say("Good Morning!")
            voice_engine.runAndWait()
    except KeyboardInterrupt:
        print("Ctrl C pressed, alarm stopped")
    finally:
        speaker.stop_sound()


# aram = schedule.every().day.at("07:00").do(alarm)  # repeat everyday at 7 AM
aram = schedule.every().second.do(alarm)  # repeat everyday at 7 AM

print("Program running... (use nohup to keep runninging the background)")
print("nohup usage: https://www.computerhope.com/unix/unohup.htm#:~:text=nohup%20command%20%3E%20file%22.-,Examples,-nohup%20mycommand")
while True:
    schedule.run_pending()
    time.sleep(1)


# to remove alarm, just put here for demonstration, code will not run
schedule.cancel_job(alarm)
