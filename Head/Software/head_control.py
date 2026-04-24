#!/usr/bin/env python3
import sys
from adafruit_servokit import ServoKit
import paho.mqtt.client as mqtt
from threading import Thread
import time
from datetime import datetime

# Set up global variables
minangles = {} # negative position = left or down or open
midangles = {}
maxangles = {} # positive position = right or up or closed
servonum = {}
servonum["right/x"] = 0
minangles["right/x"] = 120 # look left
midangles["right/x"] = 90 # look forward
maxangles["right/x"] = 70 # look right
servonum["right/y"] = 1
minangles["right/y"] = 120 # look down
midangles["right/y"] = 80 # look forward
maxangles["right/y"] = 50 # look up
servonum["left/x"] = 4
minangles["left/x"] = 110 # look left
midangles["left/x"] = 90 # look forward
maxangles["left/x"] = 65 # look right
servonum["left/y"] = 5
minangles["left/y"] = 55 # look down
midangles["left/y"] = 95 # look forward
maxangles["left/y"] = 125 # look up
servonum["blink/top"] = 2
minangles["blink/top"] = 65 # open wide
midangles["blink/top"] = 80 # normal
maxangles["blink/top"] = 130 # closed
servonum["blink/bottom"] = 6
minangles["blink/bottom"] = 65 # open wide
midangles["blink/bottom"] = 90 # normal
maxangles["blink/bottom"] = 110 # closed
servonum["head/rotate"] = 9
minangles["head/rotate"] = 0 # left
midangles["head/rotate"] = 90 # forward
maxangles["head/rotate"] = 180 # right
servonum["head/tilt"] = 10
minangles["head/tilt"] = 110 # down
midangles["head/tilt"] = 90 # normal
maxangles["head/tilt"] = 65 # up
servonum["camera/focus"] = 11
minangles["camera/focus"] = 70 # near
midangles["camera/focus"] = 90 # about 2 meters
maxangles["camera/focus"] = 110 # far
target = [90.0] * 16

macro_blink = [
    [("blink/top",1),("blink/bottom",1),("pause",0.5)],
    [("blink/top",0),("blink/bottom",0)]
    ]
macro_roll = [
    [("right/x",0),("right/y",0.5),("left/x",0),("left/y",0.5),("pause",0.2)],
    [("right/x",-0.5),("right/y",1),("left/x",-0.5),("left/y",1),("pause",0.2)],
    [("right/x",0),("right/y",1),("left/x",0),("left/y",1),("pause",0.2)],
    [("right/x",0.71),("right/y",0.71),("left/x",0.71),("left/y",0.71),("pause",0.2)],
    [("right/x",1),("right/y",0),("left/x",1),("left/y",0),("pause",0.2)],
    [("right/x",0.71),("right/y",-0.71),("left/x",0.71),("left/y",-0.71),("pause",0.2)],
    [("right/x",0),("right/y",-1),("left/x",0),("left/y",-1),("pause",0.2)],
    [("right/x",-0.71),("right/y",-0.71),("left/x",-0.71),("left/y",-0.71),("pause",0.2)],
    [("right/x",-1),("right/y",0),("left/x",-1),("left/y",0),("pause",0.2)],
    [("right/x",-0.71),("right/y",0.71),("left/x",-0.71),("left/y",0.71),("pause",0.2)],
    [("right/x",0),("right/y",1),("left/x",0),("left/y",1),("pause",0.5)],
    [("right/x",0),("right/y",0),("left/x",0),("left/y",0)]
    ]

eye_macros={"blink":macro_blink, "roll":macro_roll}

class ServoWorker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.current = [90.0] * 16
        self.servos = ServoKit(channels=16)
        # shift = 0.1 = 44 steps for 99% movement
        # shift = 0.2 = 21 steps for 99% movement
        # shift = 0.3 = 13 steps for 99% movement
        # shift = 0.4 = 10 steps for 99% movement
        # shift = 0.5 = 7 steps for 99% movement
        # shift = 0.6 = 5 steps for 99% movement
        self.shift = 0.4

    def run(self):
        global target
        while True:
            for i in range(len(self.current)):
                c = self.current[i]
                t = target[i]
                self.current[i] = c * (1.0 - self.shift) + t * self.shift
                self.servos.servo[i].angle = self.current[i]
            time.sleep(0.03333)

def positionToAngle(servoname, position):
    if position < -1.0:
        position = -1.0
    if position > 1.0:
        position = 1.0
    minang = minangles[servoname]
    midang = midangles[servoname]
    maxang = maxangles[servoname]
    angle = midang
    if position < 0:
        range = midang - minang
        angle = midang + range * position
    elif position > 0:
        range = maxang - midang
        angle = midang + range * position
    return angle

def angleToPosition(servoname, angle):
    snum = servonum[servoname]
    minang = minangles[servoname]
    midang = midangles[servoname]
    maxang = maxangles[servoname]
    position = 0.0
    if angle <= minang and minang < maxang:
        position = -1.0;
    elif angle >= maxang and maxang > minang:
        position = 1.0;
    elif angle >= minang and minang > maxang:
        position = -1.0;
    elif angle <= maxang and maxang < minang:
        position = 1.0;
    elif minang <= angle <= midang:
        range = float(midang - minang)             # +
        position = float(angle - midang) / range   # -/+
    elif minang >= angle >= midang:
        range = float(midang - minang)             # -
        position = float(angle - midang) / range   # +/-
    elif midang <= angle <= maxang:
        range = float(maxang - midang)             # +
        position = float(angle - midang) / range   # +/+
    elif midang >= angle >= maxang:
        range = float(maxang - midang)             # -
        position = float(angle - midang) / range   # -/-
    return position


def move_servo(servoname, position):
    # print(servoname, position)
    if position < -1.0:
        position = -1.0
    if position > 1.0:
        position = 1.0
    if servoname not in servonum:
        print("Servo name {} not recognised".format(servoname))
        return
    snum = servonum[servoname]
    angle = positionToAngle(servoname, position)
    nowtime = datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]
    print("{}: Moving servo {} to angle {}".format(nowtime, snum, angle))
    target[snum] = angle


def run_macro(mname):
    print("Running macro", mname)
    if mname not in eye_macros:
        print("Not defined")
        return
    mlist = eye_macros[mname]
    for action in mlist:
        print(action)
        for what, where in action:
            if what == "pause":
                time.sleep(where)
            else:
                move_servo(what, where)


def on_connect(client, userdata, flags, rc):
    """Called when connected to MQTT broker."""
    if rc == 0:
        client.subscribe("rover/head/#")
        print("Connected. Waiting for eyeballs.")
    else:
        print("Connection error code =", rc)


def on_disconnect(client, userdata, rc):
    """Called when disconnected from MQTT broker."""
    print("Disconnect code =",rc)
    if rc != 0:
        client.reconnect()


def on_message(client, userdata, msg):
    """Called each time a message is received on a subscribed topic."""
    if msg.topic.lower() == "rover/head/macro":
        run_macro(msg.payload.decode('ASCII'))
    else:
        servoname = msg.topic.lower().replace("rover/head/","")
        if servoname[-5:] == "delta":
            servoname = servoname[:-6] # remote "/delta"
            snum = servonum[servoname]
            position = float(msg.payload) * 0.1 + angleToPosition(servoname, target[snum])
            print("Delta movement of {} by {} to {}".format(servoname, float(msg.payload) * 0.1, position))
        else:
            position = float(msg.payload)
        move_servo(servoname, position)


if __name__ == "__main__":
    for sname in servonum:
        snum = servonum[sname]
        target[snum] = midangles[sname]
    print(target)
    servoworker = ServoWorker()
    servoworker.daemon = True
    servoworker.start()
    # Create MQTT client and connect to broker
    client = mqtt.Client()
    client.connected_flag = False
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    client.connect("localhost", 1883)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        pass

    client.disconnect()
    client.loop_stop()

