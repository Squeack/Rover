#!/usr/bin/env python3
import sys
import json
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    """Called when connected to MQTT broker."""
    if rc != 0:
        print("Connection error code =", rc)


def on_disconnect(client, userdata, rc):
    """Called when disconnected from MQTT broker."""
    if rc != 0:
        print("Disconnect code =",rc)
        client.reconnect()

def on_message(client, userdata, msg):
    pass

if __name__ == '__main__':
    text = " ".join(sys.argv[1:])
    # print(text)
    # Create MQTT client and connect to broker
    client = mqtt.Client()
    client.connected_flag = False
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    client.connect("localhost", 1883)
    client.publish("hermes/tts/say", json.dumps({"text": text, "siteID": "default"}))

    client.disconnect()
    client.loop_stop()

