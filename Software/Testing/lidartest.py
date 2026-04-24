import serial
import time

startTime = time.time()

f = open("lidardata.dat","w")

with serial.Serial('com5', 230400) as ser:
    ser.write(b'b')
    print('Start spinning')

    while (startTime + 20) > time.time():
        data = ser.read()
        print(data)
        f.write(data)

    ser.write(b'e')
    print('Stop spinning')

f.close