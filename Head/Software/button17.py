#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import subprocess
import syslog

def callback17(channel):
  print("Shutdown triggered")
  syslog.syslog(syslog.LOG_WARNING, "Shutdown button pressed")
  subprocess.call(['sudo', 'shutdown', '-h', 'now'])


GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)
GPIO.add_event_detect(17, GPIO.FALLING, callback=callback17)

try:
  while True:
    time.sleep(1)
except:
  pass
GPIO.cleanup()
