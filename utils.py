"""
author: Jerry Wu

This file contains the functionalities of the speaker
"""

import pygame as pg


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

        # pause status
        self.paused = True


    def set_sound(self, sound):
        """
        set the sound that will be play

        sound: the name of the sound file
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

        self.paused = False

    def stop_sound(self):
        """
        stop playing sound if any
        """

        self.mixer.music.stop()
        self.paused = True

    def is_stopped(self):
        """
        check if sound stopped, pause is not stop
        """

        return not self.mixer.music.get_busy()

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

