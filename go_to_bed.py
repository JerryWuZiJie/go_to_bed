"""
author: Jerry Wu

This file contains the functionalities of the speaker
"""

import time
from PIL import Image, ImageDraw, ImageFont

import pygame as pg

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.virtual import viewport, sevensegment
import busio
import board
# usage: https://learn.adafruit.com/monochrome-oled-breakouts/python-usage-2
import adafruit_ssd1306
# TODO: git clone https://github.com/pimylifeup/MFRC522-python
from mfrc522 import SimpleMFRC522
import spidev

# TODO: change sound level from 0-1 to 0-100


class Speaker:
    def __init__(self, freq=44100, bitsize=-16, channels=2, buffer=2048):
        """
        initialize the speaker module

        freq: audio CD quality
        bitsize: unsigned 16 bit
        channels: 1 is mono, 2 is stereo
        buffer: number of samples (experiment to get right sound)
        """

        # initialize mixer (for playing sound)
        self.mixer = pg.mixer
        self.mixer.init(freq, bitsize, channels, buffer)

        # set volume to 20%
        self.mixer.music.set_volume(0.2)

        # pause status, stop is not paused, only pause will turn paused to True
        self.paused = False

    def set_sound(self, sound):
        """
        set the sound that will be play

        sound: the relative path to the sound file
        """

        self.sound = sound

    def play_sound(self):
        """
        stream music with mixer.music module in non-blocking manner
        this will stream the sound from disk while playing
        """

        try:
            self.mixer.music.load(self.sound)
        except pg.error:
            # TODO: maybe change to blink of led
            print("File {} not found! {}".format(self.sound, pg.get_error()))
            return

        self.mixer.music.play()

    def stop_sound(self):
        """
        stop playing sound if any
        """

        self.mixer.music.stop()
        # unload the file to free up resource
        self.mixer.music.unload()
        self.paused = False

    def is_stopped(self):
        """
        check if sound stopped, pause is not stop
        """

        return (not self.mixer.music.get_busy()) and (not self.paused)

    def is_paused(self):
        """
        check if sound paused
        """

        return self.paused

    def volume(self):
        """
        get the volume of the speaker
        """

        return round(self.mixer.music.get_volume(), 1)

    def set_volume(self, volume):
        """
        set volume
        """

        self.mixer.music.set_volume(volume)

    def increase_volume(self):
        """
        increase 10% of the total volume
        """

        # the set_volume function will auto truncate the input
        self.mixer.music.set_volume(self.volume() + 0.1)

    def decrease_volume(self):
        """
        decrease 10% of the total volume
        """

        self.mixer.music.set_volume(self.volume() - 0.1)

    def pause(self):
        """
        pause the sound
        """

        self.mixer.music.pause()
        self.paused = True

    def resume(self):
        """
        resume the sound
        """

        self.mixer.music.unpause()
        self.paused = False

    def __del__(self):
        pg.quit()


class LED:
    def __init__(self, spi_ce=0):
        """
        initialize LED driver (max7219), using the luma library

        spi_ce: the ce line that connects to the driver
        """

        # create seven segment device
        # raspberry pi zero only have one SPI
        serial = spi(port=0, device=spi_ce, gpio=noop())
        self.device = max7219(serial, cascaded=1)
        self.seg = sevensegment(self.device)

        # display text
        self.text = self.seg.text

    def get_brightness(self):
        return self.brightness

    def increase_brightness(self):
        """
        increase brightness
        """

        self.set_brightness(self.brightness+10)

    def decrease_brightness(self):
        """
        decrease brightness
        """

        self.set_brightness(self.brightness-10)

    def set_brightness(self, level):
        """
        set the brightness

        level: integer between 0 to 100
        """

        level = max(min(100, level), 0)  # scale between 0 - 100
        self.brightness = level

        level = int(level/100*255)  # scale to 0 - 255
        self.seg.device.contrast(level)

    def set_display(self, text):
        """
        set the display text, only 4 digits will get displayed
        """

        # if ':' is the third in text, turn on colon
        if len(text) >= 3 and text[2] == ':':
            self.text = text[:5]
        else:
            # add ' ' to turn off ':'
            self.text = text[:2] + " " + text[2:4]

        # update displayed text
        self.seg.text = self.text

    def get_display(self):
        """
        return the displayed text
        """

        return self.text


class OLED:
    def __init__(self, width=128, height=64, addr=0x3c):
        # Initialize I2C library busio
        i2c = busio.I2C(board.SCL, board.SDA)  # TODO: board.I2C()?
        self.oled = adafruit_ssd1306.SSD1306_I2C(width, height, i2c, addr=addr)

        # clear display
        self.oled.fill(0)
        self.oled.show()

        # create canvas for displaying
        # "1" for 1 bit pixel
        self.img = Image.new("1", (self.oled.width, self.oled.height))
        self.canvas = ImageDraw.Draw(self.img)

    def update_OLED(self, text):
        """ 
        update the OLED display

        @param text: text to display
        """

        # Draw a black rectangle (background) to clear previous display
        self.canvas.rectangle((0, 0, self.oled.width-1, self.oled.height-1),  # (x0, y0, x1, y1)
                              outline=255, fill=0, width=5)
        # Draw the text
        font = ImageFont.load_default()  # TODO: change to a suitable font later
        # multiline_text usage: https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html#:~:text=ImageDraw.multiline_text
        self.canvas.multiline_text(
            (0, 0),
            text,
            font=font,
            fill=255,
            spacing=1  # 1 empty pixel between lines
        )
        # Display image
        self.oled.image(self.img)
        self.oled.show()


class RFID:
    def __init__(self, spi_dev=0, spi_ce=1):
        # TODO: connection https://ffund.github.io/compe-design-project/lab5/spi.html#:~:text=setup.py%20install-,Connect%20the%20MFRC522,-Connect%20the%20MFRC522
        self.reader = SimpleMFRC522(bus=spi_dev, device=spi_ce, spd=10000)

    def read(self):
        """
        read the RFID card
        """

        id, text = self.reader.read()
        return id, text

    def read_no_block(self):
        """
        read the RFID card without blocking
        """

        id, text = self.reader.read_no_block()
        return id, text

    def write(self, text):
        """
        write the RFID card
        """

        id, text_in = self.reader.write(text)
        return id, text_in

    def write_no_block(self, text):
        """
        write the RFID card without blocking
        """

        id, text_in = self.reader.write_no_block(text)
        return id, text_in

# TODO: RC timing circuit for photodiode    