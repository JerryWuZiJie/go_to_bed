"""
author: Jerry Wu

This file shows a simple demo of how to use speaker.py module
"""

import time
import sys
import RPi.GPIO as GPIO
from utils import Speaker  # for speaker


GPIO.setmode(GPIO.BCM)

################################################################
# speaker usage

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
        if speaker.is_paused():
            speaker.resume()
            print("sound resumed")
        else:
            speaker.pause()
            print("sound paused")


# pause/resume music when button pressed
GPIO.add_event_detect(BUTTON, GPIO.RISING, callback=pause_button)

# initialize speaker object
speaker = Speaker()
# set the sound you want to play
speaker.set_sound("sound/Let Her Go.mp3")
# start playing, non-blocking. The sound will stop if program ends or
# stop_sound() is called
speaker.play_sound()
print("Initial volume:", speaker.volume())
print("\n" + "-"*20 +
      "\nPress button connect on pin", BUTTON, "to pause/resume\n" +
      "Press 'Ctrl C' to exit\n"
      + "-"*20 + "\n")


try:
    while not speaker.is_stopped():
        time.sleep(0.01)
    print("finish playing")
except KeyboardInterrupt:
    print("Ctrl C pressed, sound stopped")
finally:
    print("exit")
    sys.exit(0)

################################################################
