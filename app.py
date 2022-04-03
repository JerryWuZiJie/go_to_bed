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
import spidev
import busio
import board
# usage: https://learn.adafruit.com/monochrome-oled-breakouts/python-usage-2
import adafruit_ssd1306
# TODO: git clone https://github.com/pimylifeup/MFRC522-python
from mfrc522 import SimpleMFRC522

import go_to_bed

### onetime tasks ###
GPIO.setmode(GPIO.BCM)
# TODO
# setup RFID (SPI 0 1)
# TODO: connection https://ffund.github.io/compe-design-project/lab5/spi.html#:~:text=setup.py%20install-,Connect%20the%20MFRC522,-Connect%20the%20MFRC522
rfid_reader = SimpleMFRC522(bus=0, device=1, spd=10000)
# id, text = rfid_reader.read()  # or reader.read_no_block()
# rfid_reader.write(text)  # or id, text_in = reader.write_no_block(text)

# setup ADC for photodiode (SPI 1, 0)
# TODO: https://ffund.github.io/compe-design-project/lab7/adc.html
ADC_CH0 = 0b01101000
ADC_CH1 = 0b01111000
ADC = spidev.SpiDev()
ADC.open(0, 1)    # SPI Port 0, Chip Select 1
ADC.mode = 0b00
ADC.max_speed_hz = 1200000  # 1.2 MHz

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

# setup led (SPI 0 0)
led = go_to_bed.LED()

# setup speaker
speaker = go_to_bed.Speaker()

# setup webpage

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


def update_photodiode():
    """
    update photodiode value
    """
    # TODO

    readBytes = ADC.xfer2([ADC_CH0, 0x00])   # Read from CH0
    digitalValue = (((readBytes[0] & 0b11) << 8) | readBytes[1])
    ch0_v = digitalValue/1024 * 3.3  # 3.3 is Vref
    readBytes = ADC.xfer2([ADC_CH1, 0x00])   # Read from CH1
    digitalValue = (((readBytes[0] & 0b11) << 8) | readBytes[1])
    ch1_v = digitalValue/1024 * 3.3  # 3.3 is Vref
