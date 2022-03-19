import RPi.GPIO as GPIO

import time

DIN = 10

CS = 8

CLK = 11

CLK_TIME = 0.01

TEST_TIME = 0.01


def setup():

    GPIO.setmode(GPIO.BCM)

    # BCM pin numbering

    GPIO.setup(DIN, GPIO.OUT)

    GPIO.setup(CS, GPIO.OUT)

    GPIO.setup(CLK, GPIO.OUT)

    GPIO.output(DIN, GPIO.LOW)

    GPIO.output(CS, GPIO.HIGH)

    GPIO.output(CLK, GPIO.LOW)


def pulse_clk(clk):

    GPIO.output(clk, GPIO.LOW)

    time.sleep(CLK_TIME)

    GPIO.output(clk, GPIO.HIGH)

    time.sleep(CLK_TIME)


def send_byte(byte):

    GPIO.output(DIN, GPIO.LOW)

    GPIO.output(CS, GPIO.LOW)

    bitarray = [int(b) for b in format(byte, '016b')]
    # print("sending", bitarray)

    for bit in bitarray:

        GPIO.output(DIN, bit)

        pulse_clk(CLK)

    GPIO.output(CS, GPIO.HIGH)
    GPIO.output(CLK, GPIO.LOW)
    GPIO.output(DIN, GPIO.LOW)


if __name__ == '__main__':

    setup()
    
    # new command
    dummy = 0b0000
    address = 0b1111
    segment = 0b00000001
    byte = (dummy << 12) + (address << 8) + segment
    print("run test")
    send_byte(byte)
    time.sleep(TEST_TIME)

    # new command
    dummy = 0b0000
    address = 0b1111
    segment = 0b00000000
    byte = (dummy << 12) + (address << 8) + segment
    print("stop test")
    send_byte(byte)
    time.sleep(TEST_TIME)
    
    # turn off
    dummy = 0b0000
    address = 0b1100
    segment = 0b00000000
    byte = (dummy << 12) + (address << 8) + segment
    print("turn off")
    send_byte(byte)
    time.sleep(TEST_TIME)
    
    # turn on
    dummy = 0b0000
    address = 0b1100
    segment = 0b00000001
    byte = (dummy << 12) + (address << 8) + segment
    print("turn on")
    send_byte(byte)
    time.sleep(TEST_TIME)

    # new command
    dummy = 0b0000
    address = 0b1010
    segment = 0b00000000
    byte = (dummy << 12) + (address << 8) + segment
    print("set intensity")
    send_byte(byte)
    time.sleep(TEST_TIME)

    # set digit 0 to decode mode, rest to non-decode mode
    dummy = 0b0000
    address = 0b1001
    segment = 0b00000001
    byte = (dummy << 12) + (address << 8) + segment
    print("set digit 0 to decode mode, rest to non-decode mode")
    send_byte(byte)
    time.sleep(TEST_TIME)

    # set 
    dummy = 0b0000
    address = 0b0001
    segment = 0b00001110
    byte = (dummy << 12) + (address << 8) + segment
    print("digit 0 set p")
    send_byte(byte)
    time.sleep(TEST_TIME)

    # set 
    dummy = 0b0000
    address = 0b0010
    segment = 0b00000110
    byte = (dummy << 12) + (address << 8) + segment
    print("digit 1 set 1")
    send_byte(byte)
    time.sleep(TEST_TIME)
    
    time.sleep(10)
    GPIO.cleanup()
