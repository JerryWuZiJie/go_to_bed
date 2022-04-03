"""
author: Jerry Wu
all tasks to run are included in this file
"""
import os
import time
import threading
from PIL import Image, ImageDraw, ImageFont

import schedule
import RPi.GPIO as GPIO
import busio
import board
# usage: https://learn.adafruit.com/monochrome-oled-breakouts/python-usage-2
import adafruit_ssd1306

import go_to_bed

### onetime tasks ###
GPIO.setmode(GPIO.BCM)
# TODO
# setup RFID (SPI)
# setup ADC for photodiode
# setup OLED (I2C)
OLED_WIDTH = 128
OLED_HEIGHT = 64  # TODO: might need to change to 32
OLED_ADDRESS = 0x3c  # TODO: might subject to changes
# Initialize I2C library busio
i2c = busio.I2C(board.SCL, board.SDA)  # TODO: board.I2C()?
oled = adafruit_ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT,
                                    i2c, addr=OLED_ADDRESS)
# clear display
oled.fill(0)
oled.show()
# create canvas for displaying
# Graphics stuff - create a canvas to draw/write on
oled_img = Image.new("1", (oled.width, oled.height))  # "1" for 1 bit pixel
oled_canvas = ImageDraw.Draw(oled_img)

# setup push buttons
# TODO: need to specify pins
UP_PIN = 0
DOWN_PIN = 0
OK_PIN = 0
CANCEL_PIN = 0
GPIO.setup(UP_PIN, GPIO.IN)
GPIO.setup(DOWN_PIN, GPIO.IN)
GPIO.setup(OK_PIN, GPIO.IN)
GPIO.setup(CANCEL_PIN, GPIO.IN)

# setup webpage

# setup led (SPI)
led = go_to_bed.LED()

# setup speaker
speaker = go_to_bed.Speaker()

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


### other functions ###
def update_OLED(text):
    """
    update the OLED display

    @param text: text to display
    """
    # Draw a black rectangle (background) to clear previous display
    oled_canvas.rectangle((0, 0, oled.width-1, oled.height-1),  # (x0, y0, x1, y1)
                          outline=255, fill=0, width=5)
    # Draw the text
    font = ImageFont.load_default()  # TODO: change to a suitable font later
    # multiline_text usage: https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html#:~:text=ImageDraw.multiline_text
    oled_canvas.multiline_text(
        (0, 0),
        text,
        font=font,
        fill=255,
        spacing=1  # 1 empty pixel between lines
    )
    # Display image
    oled.image(oled_img)
    oled.show()
