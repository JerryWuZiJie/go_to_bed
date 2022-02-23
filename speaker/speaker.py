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
        # initialize pygame (for catching event)
        # TODO: event doesn't work with GUI
        pg.init()

        # initialize mixer (for playing sound)
        self.mixer = pg.mixer
        self.mixer.init(freq, bitsize, channels, buffer)

        # set volume to 20%
        self.mixer.music.set_volume(0.2)

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


    def get_keypress(self):
        """
        detect keypress for adjusting volume
        
        return False if q press, which indicates end of program
        """
        
        for event in pg.event.get():
            # checking if keydown event happened or not
            if event.type == pg.KEYDOWN:
                # checking if key "A" was pressed
                if event.key == pg.K_UP:
                    self.increase_volume()
                    print("Increase volume:", self.volume())
                
                # checking if key "J" was pressed
                if event.key == pg.K_DOWN:
                    self.decrease_volume()
                    print("Decrease volume:", self.volume())
                
                # checking if key "P" was pressed
                if event.key == pg.K_q:
                    return False
        
        return True

    def __del__(self):
        pg.quit()


    # TODO: trigger event when music stop?
    # pygame.mixer.music.set_endevent
    '''
    maybe use pause to indicate the user stop and unload it, and stop to indicate
    oversleep with callback handling that. Test needed
    '''

