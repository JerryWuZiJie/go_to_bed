"""
author: Jerry Wu

This file shows a simple demo of how to use speaker.py module
"""

import time
from utils import Speaker

# initialize speaker object
speaker = Speaker()

# set the sound you want to play
speaker.set_sound("sound/Let Her Go.mp3")

# start playing, non-blocking. The sound will stop if program ends
speaker.play_sound()
print("Initial volume:", speaker.volume())
print("\n" + "-"*20 +
      "\nPress 'q' to exit\nPress 'up arrow' to increase volume'\nPress 'down arrow' to decrease volume\n"
      + "-"*20 + "\n")

try:
    while speaker.is_playing() and speaker.get_keypress():
        pass
except KeyboardInterrupt:
    print("Ctrl C pressed")
finally:
    print("stop playing, exit")
