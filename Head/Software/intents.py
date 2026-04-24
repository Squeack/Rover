#!/usr/bin/env python3
import json
import pprint
import board
import adafruit_dotstar
import RPi.GPIO as GPIO
import time
from datetime import datetime
import paho.mqtt.client as mqtt

# Initialise hardware and debug
pp = pprint.PrettyPrinter(indent = 1)
DOTSTAR_DATA = board.D5
DOTSTAR_CLOCK = board.D6
BUTTON_GPIO = 17
dotlevel = 0.1
numlights = 3
dots = [0] * numlights
client = None

def button_pressed_callback(channel):
    global client
    print("Button pressed")
    #if client is not None:
    #    client.publish("hermes/hotword/bumblebee_raspberry-pi/detected",'{"siteId": "default"}')


def tidyText(t):
    while t.find(" ,") > 0:
        t = t.replace(" ,", ",")
    while t.find("  ") > 0:
        t = t.replace("  ", " ")
    if 96 < ord(t[0]) < 123:
        t = chr(ord(t[0])-32) + t[1:]
    return t


def getSlotValue(slots, slotname):
    for slot in slots:
        if slot["slotName"] == slotname:
            return slot["rawValue"]
    return None


def getDictFromSlots(slots):
    d = {}
    for s in slots:
        k = s["slotName"]
        v = s["rawValue"]
        d[k] = v
    pp.pprint(d)
    return d


def colourLookup(colour):
    if colour == "white":
        r,g,b = 255,255,255
    elif colour == "red":
        r,g,b = 255,0,0
    elif colour == "yellow":
        r,g,b = 255,255,0
    elif colour == "green":
        r,g,b = 0,255,0
    elif colour == "cyan":
        r,g,b = 0,255,255
    elif colour == "blue":
        r,g,b = 0,0,255
    elif colour == "magenta":
        r,g,b = 255,0,255
    elif colour == "pink":
        r,g,b = 255,128,192
    else:
        r,g,b = 0,0,0
    sum = r + g + b
    if sum > 255:
        factor = 255.0 / float(sum)
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
    return r, g, b


def setStatusLight(r,g,b):
    dots[1] = (g, b, r, 1.0)
    dots.show()
    time.sleep(0.1)


def scaleBrightness(r,g,b):
    global dotlevel
    return(int(g*dotlevel), int(b*dotlevel), int(r*dotlevel))


def hotwordDetected():
    global numlights
    print("Wakey-wakey")
    setStatusLight(0,0,0)
    setStatusLight(255,255,255)
    setStatusLight(0,0,0)
    setStatusLight(0,255,0)


def hotwordToggleOn():
    pass


def hotwordToggleOff():
    pass


def intentChangeLightState(intentdict):
    global dots
    global numlights
    lightname = intentdict["name"]
    lightstate = intentdict["state"]
    if lightstate == "off":
       for n in range(numlights):
           dots[n] = (0, 0, 0)
    elif lightstate == "on":
       for n in range(numlights):
           dots[n] = scaleBrightness(255, 255, 255)
    setStatusLight(0,0,0)
    return None


def intentChangeLightColour(intentdict):
    global dots
    location = intentdict["light_location"]
    lightword = intentdict["light"]
    colour = intentdict["colour"]
    print("Change Light Colour:", location, lightword, colour)
    lights = []
    if location == "left":
        lights.append(2)
    # Centre light is used for status, and only set internally
    #if location in ["status", "center", "middle"]:
    #    lights.append(1)
    if location == "right":
        lights.append(0)
    if location == "both":
        lights.append(0)
        lights.append(2)
    colr, colg, colb = colourLookup(colour)
    col = scaleBrightness(colr, colg, colb)
    for n in lights:
        dots[n] = col
    setStatusLight(0,0,0)
    return None


def intentChangeBrightness(intentdict):
    global dotlevel
    level = intentdict["level"]
    print("Change Light Brightness:", level)
    rg,rb,rr,ra = dots[0]
    lg,lb,lr,la = dots[2]
    print(rr,rg,rb,ra)
    print(lr,lg,lb,la)
    rg = min(int(rg/dotlevel), 255)
    rb = min(int(rb/dotlevel), 255)
    rr = min(int(rr/dotlevel), 255)
    lg = min(int(lg/dotlevel), 255)
    lb = min(int(lb/dotlevel), 255)
    lr = min(int(lr/dotlevel), 255)
    if level == "one":
        dotlevel = 0.1
    elif level == "two":
        dotlevel = 0.2
    elif level == "three":
        dotlevel = 0.3
    elif level == "four":
        dotlevel = 0.4
    elif level == "five":
        dotlevel = 0.5
    elif level == "six":
        dotlevel = 0.6
    elif level == "seven":
        dotlevel = 0.7
    elif level == "eight":
        dotlevel = 0.8
    elif level == "nine":
        dotlevel = 0.9
    elif level == "ten":
        dotlevel = 1.0
    rg *= dotlevel
    rb *= dotlevel
    rr *= dotlevel
    lg *= dotlevel
    lb *= dotlevel
    lr *= dotlevel
    dots[0] = (rg, rb, rr)
    dots[2] = (lg, lb, lr)
    setStatusLight(0,0,0)
    if dotlevel < 0.25:
        return "I'm feeling gloomy"
    elif dotlevel > 0.75:
        return "Too bright"
    else:
        return None


def intentBlink(intentdict):
    global client
    client.publish("rover/head/macro", "blink")
    return None


def intentRollEyes(intentdict):
    global client
    client.publish("rover/head/macro", "roll")
    return None


def intentBark(intentdict):
    return "Wuf wuf bark wuf."


def intentGreeting(intentdict):
    timeh = int(time.strftime("%H", time.localtime()))
    if timeh < 7:
        return "I'm still sleeping"
    if 7 <= timeh < 12:
        return "Good morning"
    if 12 <= timeh < 13:
        return "Is it lunch time yet?"
    if 13 <= timeh < 18:
        return "Good afternoon"
    if 18 <= timeh < 19:
        return "Is it dinner time yet?"
    if 19 <= timeh < 21:
        return "Good evening"
    return "Good night"


def intentGetTime(intentdict):
    timenow = time.localtime()
    timeh = int(time.strftime("%H", timenow))
    timem = int(time.strftime("%M", timenow))
    # Round to nearest five minutes
    timem = 5*int((timem+2.5)/5) 
    timerel = "past"
    timeafter = ""
    if timem > 30:
        timem = 60 - timem
        timeh += 1
        timerel = "to"
    if timem == 0:
        timem = ""
        timerel = ""
        timeafter = "o clock"
    elif timem == 15:
        timem = "quarter"
    elif timem == 30:
        timem = "half"
    else:
        timem = str(timem)
    if timeh > 12:
        timeh -= 12
        timeafter = timeafter + " p m"
    day= time.strftime("%A", timenow)
    date = int(time.strftime("%d", timenow).lstrip("0"))
    suffix = { 1: "st", 2: "nd", 3: "rd" }.get(date if (date < 20) else (date % 10), 'th')
    month = time.strftime("%B", timenow)
    return "The time is {} {} {} {}, on {} {}{} {}".format(timem, timerel, timeh, timeafter, day, date, suffix, month)

def on_connect(client, userdata, flags, rc):
    """Called when connected to MQTT broker."""
    if rc == 0:
        client.subscribe("hermes/intent/#")
        client.subscribe("hermes/hotword/#")
        client.subscribe("hermes/nlu/intentNotRecognized")
        print("Connected. Waiting for intents.")
    else:
        print("Connection error code =", rc)


def on_disconnect(client, userdata, rc):
    """Called when disconnected from MQTT broker."""
    print("Disconnect code =",rc)
    if rc != 0:
        client.reconnect()


def on_message(client, userdata, msg):
    """Called each time a message is received on a subscribed topic."""
    global pp
    # print(msg.topic)
    nlu_payload = json.loads(msg.payload)
    category = "/".join(msg.topic.split("/")[:2])
    command = "/".join(msg.topic.split("/")[2:])
    sentence = None
    reply = None
    print("Category =",category, "+", command)
    if category == "hermes/nlu":
        if command == "intentNotRecognized":
            sentence = "Unrecognized command!"
            print("Recognition failure")
            setStatusLight(255,0,0)
            time.sleep(0.5)
            setStatusLight(0,0,0)
    elif category == "hermes/hotword":
        pp.pprint(nlu_payload)
        if command == "bumblebee_raspberry-pi/detected":
            hotwordDetected()
        elif command == "toggleOn":
            hotwordToggleOn()
        elif command == "toggleOff":
            hotwordToggleOff()
    elif category == "hermes/intent":
        # Intent
        # pp.pprint(nlu_payload["intent"])
        slots = nlu_payload["slots"]
        dots[1] = (0,0,0)
        intentdict = getDictFromSlots(slots)
        # pp.pprint(slots)
        if command == "ChangeLightColour":
            reply = intentChangeLightColour(intentdict)
        elif command == "ChangeLightState":
            reply = intentChangeLightState(intentdict)
        elif command == "ChangeBrightness":
            reply = intentChangeBrightness(intentdict)
        elif command == "GetTime":
            reply = intentGetTime(intentdict)
        elif command == "Blink":
            reply = intentBlink(intentdict)
        elif command == "RollEyes":
            reply = intentRollEyes(intentdict)
        elif command == "Bark":
            reply = intentBark(intentdict)
        elif command == "Greeting":
            reply = intentGreeting(intentdict)
        # Speak the text from the intent
        sentence = nlu_payload["input"]

    if sentence is not None and reply is None:
        site_id = nlu_payload["siteId"]
        client.publish("hermes/tts/say", json.dumps({"text": sentence, "siteId": site_id}))
        print("Saying", sentence)
    if reply is not None:
        reply = tidyText(reply)
        site_id = nlu_payload["siteId"]
        client.publish("hermes/tts/say", json.dumps({"text": reply, "siteId": site_id}))
        print("Saying", reply)

if __name__ == '__main__':
    dots = adafruit_dotstar.DotStar(DOTSTAR_CLOCK, DOTSTAR_DATA, numlights, brightness=1)
    for n in range(numlights):
        dots[n] = (0, 0, 0)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON_GPIO, GPIO.FALLING, callback=button_pressed_callback, bouncetime=100)
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
    dots.deinit()
    GPIO.cleanup()
   
