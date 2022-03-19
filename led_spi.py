import RPi.GPIO as GPIO
import time
import spidev

TEST_TIME = 0.1

spi = spidev.SpiDev()
spi.open(0,0)
spi.mode = 0b00
spi.max_speed_hz = 10000000  # 10MHz max speed

# run test
print("run test")
readBytes = spi.xfer2([0b1111, 0b00000001])
print(readBytes)
time.sleep(TEST_TIME)

# stop test
print("stop test")
readBytes = spi.xfer2([0b1111, 0b00000000])
print(readBytes)
time.sleep(TEST_TIME)

# exit shutdown mode
print("exit shutdown mode")
readBytes = spi.xfer2([0b00001100, 0b00000001])
print(readBytes)
time.sleep(TEST_TIME)

# set all to decode mode
print("set all to decode mode")
readBytes = spi.xfer2([0b1001, 0b1111111])
print(readBytes)
time.sleep(TEST_TIME)

# set 1 to 1
print("set 1 to 1")
readBytes = spi.xfer2([0b0001, 0b0001])
print(readBytes)
time.sleep(TEST_TIME)

# set 2 to 2
print("set 3 to 2")
readBytes = spi.xfer2([0b0010, 0b0010])
print(readBytes)
time.sleep(TEST_TIME)

# set 3 to 3
print("set 3 to 3")
readBytes = spi.xfer2([0b0011, 0b0011])
print(readBytes)
time.sleep(TEST_TIME)

# set 4 to 4
print("set 4 to 4")
readBytes = spi.xfer2([0b0100, 0b0100])
print(readBytes)
time.sleep(TEST_TIME)


time.sleep(10)
