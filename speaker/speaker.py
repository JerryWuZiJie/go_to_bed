"""
author: Jerry Wu

This file contains the functionalities of the speaker
"""

import pygame as pg
import time


class Speaker:
    def __init__(self, freq=44100, bitsize=-16, channels=2, buffer=2048):
        """
        initialize the speaker module

        freq: audio CD quality
        bitsize: unsigned 16 bit
        channels: 1 is mono, 2 is stereo
        buffer: number of samples (experiment to get right sound)
        """
        self.mixer = pg.mixer
        self.mixer.init(freq, bitsize, channels, buffer)

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
            print("File {} not found! {}".format(self.sound, pg.get_error()))  # TODO: maybe change to blink of led
            return

        self.mixer.music.play()

        # If you want to fade in the audio...
        # for x in range(0,100):
        #     pg.mixer.music.set_volume(float(x)/100.0)
        #     time.sleep(.0075)
        # check if playback has finished

    def stop_sound(self):
        """
        stop playing sound if any
        """

        self.mixer.music.stop()

    def is_playing(self):
        """
        check if playing sound now
        """

        return self.mixer.music.get_busy()
    
    def volume(self):
        """
        get the volume of the speaker
        """

        return self.mixer.music.get_volume()

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

    # TODO: trigger event when music stop?
    # pygame.mixer.music.set_endevent
    '''
    maybe use pause to indicate the user stop and unload it, and stop to indicate
    oversleep with callback handling that. Test needed
    '''

speaker = Speaker()
speaker.set_sound("sound/Let Her Go.mp3")
speaker.play_sound()

speaker.decrease_volume()
print(speaker.volume())
if speaker.is_playing():
    time.sleep(5)

speaker.mixer.music.fadeout(1000)

print("exit")
