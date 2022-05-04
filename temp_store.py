import go_to_bed
import time

import RPi.GPIO as GPIO
from PIL import Image


print("create")
oled = go_to_bed.OLED()
print("setup")


print("setup done")

img = Image.open('img/sun.jpg')
img = img.convert('1')
print('ready to go')
oled.img.paste(img)

oled.update_display()

time.sleep(10)