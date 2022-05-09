"""
author: Jerry Wu

This file contains the functionalities of the speaker
"""

from PIL import Image, ImageDraw, ImageFont

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

        # only need to import in speaker, otherwise slow down the program
        import pygame as pg

        # initialize mixer (for playing sound)
        self.mixer = pg.mixer
        self.mixer.init(freq, bitsize, channels, buffer)

        # set volume to 20%
        self.mixer.music.set_volume(0.5)

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


class Clock:
    def __init__(self, spi_dev=0, spi_ce=1):
        """
        initialize LED driver (max7219), using the luma library

        spi_ce: the ce line that connects to the driver
        """

        # create seven segment device
        # raspberry pi zero only have one SPI
        serial = spi(port=spi_dev, device=spi_ce, gpio=noop())
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
        self.clear_display()

        # create canvas for displaying
        # "1" for 1 bit pixel
        self.img = Image.new("1", (self.oled.width, self.oled.height))
        self.canvas = ImageDraw.Draw(self.img)
        self.x = 0
        self.y = 0
        # display text font
        self.font = ImageFont.load_default()  # TODO: change to a suitable font later
        self.font_height = self.font.getsize("A")[1]

    def clear_display(self):
        """
        clear the display
        """

        self.x = 0
        self.y = 0
        self.oled.fill(0)
        self.oled.show()

    def add_text(self, text, x=None, y=None):
        """
        add text to the display

        text: the text to display
        x, y: the position of the text
        """

        if x:
            self.x = x
        else:
            self.x = 0
        if y:
            self.y = y
        else:
            self.y += self.font_height

        self.canvas.text((self.x, self.y), text, font=self.font, fill=255)

    def update_display(self):
        """ 
        update the OLED display
        """

        # Display image
        self.oled.image(self.img)
        self.oled.show()


class RFID:
    def __init__(self):
        # the library doesn't support custom spi port, can only use SPI0 CE0
        self.reader = SimpleMFRC522()

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


class ADC:
    def __init__(self, spi_dev=0, spi_ce=2):
        # TODO: https://ffund.github.io/compe-design-project/lab7/adc.html
        self.cmd = [0b01101000, 0b01111000]   # command to read from ch0/1
        self.spi = spidev.SpiDev()
        self.spi.open(spi_dev, spi_ce)
        self.spi.mode = 0b00
        self.spi.max_speed_hz = 1200000  # 1.2 MHz

    def read(self, channel):
        readBytes = self.spi.xfer2([self.cmd[channel], 0x00])   # Read from CH0
        digitalValue = ((readBytes[0] & 0b11) << 8) | readBytes[1]
        voltage = digitalValue/1024 * 3.3  # 3.3 is Vref
        # TODO: further processing
        return voltage
