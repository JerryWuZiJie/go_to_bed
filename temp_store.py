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



################## enccoder #############################

GPIO.setmode(GPIO.BCM)

# setup rotary switch
OUTA = 17
OUTB = 27
BUT = 22

ccw_time = time.time()
cw_time = time.time()


last_state = GPIO.LOW
counter = 0


def rotation(pin):
    assert pin == OUTA

    global counter, ccw_time, cw_time
    if GPIO.input(OUTB) != GPIO.HIGH:
        if time.time() - cw_time < 0.1:
            pass  # still clockwise
        else:
            counter += 1
            ccw_time = time.time()
            print("Counter: ", counter)
    else:
        if time.time() - ccw_time < 0.1:
            pass  # still counter clockwise
        else:
            counter -= 1
            cw_time = time.time()
            print("Counter: ", counter)


def push_button(pin):
    global counter
    time.sleep(0.020)
    if GPIO.input(pin):
        counter = 0
        print("Button pressed")


# default to ground
GPIO.setup(OUTA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(OUTB, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.add_event_detect(OUTA, GPIO.FALLING, callback=rotation, bouncetime=20)
GPIO.add_event_detect(BUT, GPIO.RISING, callback=push_button)

print("all setup, start running")
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    pass

GPIO.cleanup()
