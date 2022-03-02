import RPi.GPIO as GPIO

import time

SDI = 10

RCLK = 8

SRCLK = 11

CLK_TIME = 0.05

def setup():

  GPIO.setwarnings(False)

  GPIO.setmode(GPIO.BCM)

# BCM pin numbering

  GPIO.setup(SDI, GPIO.OUT)

  GPIO.setup(RCLK, GPIO.OUT)

  GPIO.setup(SRCLK, GPIO.OUT)

  GPIO.output(SDI, GPIO.LOW)

  GPIO.output(RCLK, GPIO.LOW)

  GPIO.output(SRCLK, GPIO.LOW)

def pulse_clk(clk):

  GPIO.output(clk, GPIO.LOW)

  time.sleep(CLK_TIME)

  GPIO.output(clk, GPIO.HIGH)

  time.sleep(CLK_TIME)

def send_byte(byte):

  GPIO.output(SDI,GPIO.LOW)

  GPIO.output(RCLK,GPIO.LOW)

  bitarray = [int(b) for b in format(byte, '08b')]

  for bit in bitarray:

    GPIO.output(SDI, bit)

    pulse_clk(SRCLK)

  pulse_clk(RCLK)

  GPIO.output(RCLK,GPIO.HIGH)
  
  GPIO.output(SDI,GPIO.LOW)

if __name__ == '__main__':

  setup()

  send_byte(0b1111111111111111)


  time.sleep(10)
  

  GPIO.cleanup()
