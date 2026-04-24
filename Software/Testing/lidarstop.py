import serial
import time

startTime = time.time()

with serial.Serial('com5', 230400) as ser:
    ser.write(b'e')
