import config
import wifi
import time
from umqtt.simple import MQTTClient
from umqtt.simple import MQTTException
from picographics import PicoGraphics, DISPLAY_INKY_PACK

led = machine.Pin("LED", machine.Pin.OUT)
led.on()
wifi_client = wifi.WIFI(config.wifi_ssid, config.wifi_password)
mqtt_client = None
mqtt_connected = False
MQTT_CHANNEL_ROOT = "rover/motor/"
MQTT_CHANNEL_HEARTBEAT = MQTT_CHANNEL_ROOT + "heartbeat"
MQTT_HEARTBEAT = 10 * 1000
heartbeat_time_sent = time.ticks_ms()
seen={}
livelist = []
deadlist = []
graphics = PicoGraphics(DISPLAY_INKY_PACK)
WIDTH, HEIGHT = graphics.get_bounds()
graphics.set_update_speed(2)
graphics.set_font("bitmap8")


def draw_box(x,y,s):
    graphics.line(x, y, x, y+7*s)
    graphics.line(x, y+7*s, x+7*s, y+7*s)
    graphics.line(x+7*s, y+7*s, x+7*s, y)
    graphics.line(x+7*s, y, x, y)
    if s>1.5:
        graphics.line(x+1, y+1, x+1, y+7*s-1)
        graphics.line(x+1, y+7*s-1, x+7*s-1, y+7*s-1)
        graphics.line(x+7*s-1, y+7*s-1, x+7*s-1, y+1)
        graphics.line(x+7*s-1, y+1, x+1, y+1)

def draw_tick(x,y,s):
    graphics.line(x+2+s, y+4*s, x+2+s, y+6*s-1)
    graphics.line(x+2+s, y+6*s-1, x+6*s, y+1+s)
    if s>1.5:
        graphics.line(x+3+s, y+4*s, x+3+s, y+6*s-2)
        graphics.line(x+3+s, y+6*s-2, x+6*s-1, y+1+s)


def show_seen():
    global seen
    global livelist
    global deadlist
    oldlive = livelist.copy()
    olddead = deadlist.copy()
    posx = 16
    posy =0
    now = time.ticks_ms()
    livelist.clear()
    deadlist.clear()
    for k in seen:
        v = seen[k]
        if time.ticks_diff(now, v) < MQTT_HEARTBEAT * 3:
            livelist.append(k)
        else:
            deadlist.append(k)
    livelist.sort()
    deadlist.sort()
    samelive = livelist == oldlive
    samedead = deadlist == olddead
    if not samelive or not samedead:
        graphics.set_pen(15)
        graphics.clear()
        graphics.set_pen(0)
        for item in livelist:
            draw_box(0, posy, 2)
            draw_tick(0, posy, 2)
            graphics.text(item, posx, posy, scale=2)
            posy += 14
        for item in deadlist:
            draw_box(0, posy, 2)
            graphics.text(item, posx, posy, scale=2)
            posy += 14
        graphics.update()


def mqtt_message(topic, msg):
    global seen
    led.on()
    stopic = topic.decode("UTF-8")
    smsg = msg.decode("UTF-8")
    print(stopic, smsg)
    beatlen = len(MQTT_CHANNEL_HEARTBEAT)
    if stopic[:beatlen] == MQTT_CHANNEL_HEARTBEAT:
        now = time.ticks_ms()
        if smsg in seen:
            lasttime = seen[smsg]
            diff = time.ticks_diff(now, lasttime)
            print(smsg + " last seen " + str(int(diff/1000)) +"s ago")
        else:
            print(smsg + " seen for the first time")
        seen[smsg] = now
        show_seen()
    led.off()
    
def wifi_connect():
    if not wifi_client.isconnected():
        graphics.text("Connecting to WiFi", 0, 0, scale=2)
        graphics.update()
        print("Connecting to WiFi")
        wifi_client.connect()
        
def mqtt_connect():
    global heartbeat_time_sent
    global mqtt_connected
    try:
        if mqtt_client is not None:
            mqtt_client.disconnect()
            time.sleep(5)
    except:
        pass
    mqtt_client = MQTTClient(
        client_id=config.mqtt_username,
        server=config.mqtt_server,
        user=config.mqtt_username,
        password=config.mqtt_password)
    mqtt_client.set_callback(mqtt_message)
    mqtt_connected = False
    graphics.text("Connecting to MQTT", 0, 16, scale=2)
    graphics.update()
    while not mqtt_connected:
        try:
            print("Connecting to MQTT")
            wifi_connect()
            mqtt_client.connect()
            mqtt_connected = True
        except:
            time.sleep(0.1)
    graphics.text("Connection established", 0, 32, scale=2)
    graphics.update()
    print("Listening on " + MQTT_CHANNEL_HEARTBEAT)
    mqtt_client.subscribe(MQTT_CHANNEL_HEARTBEAT)
    mqtt_client.publish(MQTT_CHANNEL_ROOT+"join", "Hello from "+config.mqtt_username.decode("UTF-8"))
    heartbeat_time_sent = time.ticks_ms()
    return mqtt_client

def network_connect():
    graphics.set_pen(15)
    graphics.clear()
    graphics.set_pen(0)
    wifi_connect()
    return mqtt_connect()

def send_heartbeat():
    global heartbeat_time_sent
    global led
    led.on()
    mqtt_client.publish(MQTT_CHANNEL_HEARTBEAT, config.mqtt_username)
    heartbeat_time_sent = time.ticks_ms()
    led.off()
    
led.off()
while True:
    try:
        if not wifi_client.isconnected() or not mqtt_connected:
            mqtt_client = network_connect()
        mqtt_client.check_msg()
        now = time.ticks_ms()
        if time.ticks_diff(now, heartbeat_time_sent) > MQTT_HEARTBEAT:
            send_heartbeat()
        time.sleep(0.1)
    except MQTTException:
        print("MQTT exception raised")
        mqtt_connected = False
