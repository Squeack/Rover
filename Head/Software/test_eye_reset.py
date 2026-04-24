#!/usr/bin/env python3
import json
import paho.mqtt.client as mqtt
import time


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
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect("localhost", 1883)
    client.loop_start()
    client.publish("rover/head/left/x", 0)
    client.publish("rover/head/left/y", 0)
    client.publish("rover/head/right/x", 0)
    client.publish("rover/head/right/y", 0)
    client.publish("rover/head/blink/top", 0)
    client.publish("rover/head/blink/bottom", 0)
    client.loop_stop()
    client.disconnect()

   
