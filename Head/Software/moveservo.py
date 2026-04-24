#!/usr/bin/env python3
import sys
import time
from adafruit_servokit import ServoKit

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage {} servonum angle".format(sys.argv[0]))
        sys.exit(1)
    servonum = int(sys.argv[1])
    angle = int(sys.argv[2])
    kit = ServoKit(channels=16)
    kit.servo[servonum].angle = angle
    time.sleep(0.2)
