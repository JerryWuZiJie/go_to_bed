"""
author: Jerry Wu

This file shows a simple demo of how to use speaker.py module
"""

import time
import sys
import RPi.GPIO as GPIO
import pyttsx3
import schedule
from go_to_bed import Speaker  # for speaker

BUTTON = 17                     # pins connects to push button
VOLUME = 0.2                    # volume range 0 to 1

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # pull down by default

################################################################
# speaker usage
print("\n" + "-"*20 +
      "\nPress button connect on pin", BUTTON, "to pause/resume\n" +
      "Press 'Ctrl C' to skip test\n"
      + "-"*20 + "\n")

# initialize speaker object
speaker = Speaker()
# set the sound you want to play
speaker.set_sound("sound/Let Her Go.mp3")

### play sound ###
print("\n--- testing play sound ---")


def pause_button(channel):
    """
    callback function to pause/resume sound
    """

    # debounce, wait for 20 milliseconds
    time.sleep(0.020)

    if GPIO.input(channel):
        if speaker.is_paused():
            speaker.resume()
            print("sound resumed")
        else:
            speaker.pause()
            print("sound paused")


# pause/resume music when button pressed
# TODO: bouncetime=20
GPIO.add_event_detect(BUTTON, GPIO.RISING, callback=pause_button)

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

### TTS ###
print("\n--- testing TTS ---")
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

### schedule alarm ###
print("\n--- testing schedule alarm ---")


def pause_alarm(channel):
    """
    callback function to pause/resume sound
    """

    # debounce, wait for 20 milliseconds
    time.sleep(0.020)

    if GPIO.input(channel):
        speaker.pause()


# pause alarm when button pressed
GPIO.remove_event_detect(BUTTON)
GPIO.add_event_detect(BUTTON, GPIO.RISING, callback=pause_alarm)


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
aram = schedule.every(3).seconds.do(alarm)  # repeat every second

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
