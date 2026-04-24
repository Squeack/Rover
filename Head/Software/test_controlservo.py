#!/usr/bin/env python3
import json
import paho.mqtt.client as mqtt
import time
import sys


def on_connect(client, userdata, flags, rc):
    """Called when connected to MQTT broker."""
    if rc == 0:
        print("Connected. Serving eyeballs.")
    else:
        print("Connection error code =", rc)


def on_disconnect(client, userdata, rc):
    """Called when disconnected from MQTT broker."""
    print("Disconnect code =",rc)
    if rc != 0:
        client.reconnect()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage {} servoname position".format(sys.argv[0]))
        sys.exit(1)
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect("localhost", 1883)
    client.loop_start()
    servoname = sys.argv[1]
    position = sys.argv[2]
    client.publish("rover/head/{}".format(servoname), position)
    time.sleep(0.5)
    client.loop_stop()
    client.disconnect()

   
