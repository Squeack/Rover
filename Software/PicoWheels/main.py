import time
import bts7960
import servo
import wifi
from umqtt.simple import MQTTClient
from umqtt.simple import MQTTException
from utime import sleep_ms

DEBUGINPUT = False
DEBUGOUTPUT = False
DEBUGMOTOR = False
DEBUGSERVO = False

motor1 = None
motor2 = None

# Network credentials
WIFISSID = 'RoverNet'
WIFIPWD = 'Opportunity'

# MQTT credentials
MQTT_HOST = "192.168.8.8"
MQTT_USER = "motor1"
MQTT_PWD = "Opportunity"
MQTT_CHANNEL_ROOT = "rover/motor/"
MQTT_CHANNEL_CMD = MQTT_CHANNEL_ROOT + "cmd/" + MQTT_USER + "/"
MQTT_CHANNEL_ERROR = MQTT_CHANNEL_ROOT + "error/" + MQTT_USER
MQTT_CHANNEL_HEARTBEAT = MQTT_CHANNEL_ROOT + "heartbeat"
MQTT_HEARTBEAT = 10 * 1000
heartbeat_time_sent = time.ticks_ms()
heartbeat_time_heard = time.ticks_ms()

# Motor 1 pins
F_EN1 = 19
FPWM1 = 21
BPWM1 = 20
F_IS1 = 27
B_EN1 = F_EN1
B_IS1 = F_IS1

# Motor 2 pins
F_EN2 = 11
FPWM2 = 12
BPWM2 = 13
F_IS2 = 26
B_EN2 = F_EN2
B_IS2 = F_IS2

# Servo pins
SERVO1 = 2
SERVO2 = 3
SERVORANGE = 180

def cmd_speedl(speed):
    global motor1
    if DEBUGMOTOR: print("Left motor:", speed)
    motor1.speed = speed

def cmd_speedr(speed):
    global motor2
    if DEBUGMOTOR: print("Right motor:", speed)
    motor2.speed = speed

def cmd_anglel(angle):
    global servo1
    if DEBUGSERVO: print("Left angle:", angle)
    servo1.angle = angle

def cmd_angler(angle):
    global servo2
    if DEBUGSERVO: print("Right angle:", angle)
    servo2.angle = angle

def mqtt_message(topic, msg):
    global heartbeat_time_heard
    heartbeat_time_heard = time.ticks_ms() # Any message is as good as a heartbeat
    stopic = topic.decode("UTF-8")
    smsg = msg.decode("UTF-8")
    if DEBUGINPUT: print(stopic, smsg)
    cmdlen = len(MQTT_CHANNEL_CMD)
    if stopic[:cmdlen] == MQTT_CHANNEL_CMD:
        stopic=stopic[cmdlen:]
        if stopic == "speedl":
            cmd_speedl(100 * float(msg))
        elif stopic == "anglel":
            cmd_anglel(float(msg))
        elif stopic == "speedr":
            cmd_speedr(100 * float(msg))
        elif stopic == "angler":
            cmd_angler(float(msg))
        else:
            mqtt_client.publish(MQTT_CHANNEL_ERROR, "Unrecognised command = " + stopic + ":" + smsg)
            print("Unrecognised command = " + stopic + ":" + smsg)
    elif stopic[:len(MQTT_CHANNEL_HEARTBEAT)] == MQTT_CHANNEL_HEARTBEAT:
        if DEBUGINPUT: print("Heard heartbeat from", smsg)
    else:
        print("Not a command:", stopic, smsg)


def wifi_connect():
    if not wificlient.isconnected():
        print("Connecting to WiFi")
        wificlient.connect()


def mqtt_connect():
    global heartbeat_time_sent
    global heartbeat_time_heard
    try:
        if mqtt_client is not None:
            mqtt_client.disconnect()
            time.sleep(5)
    except:
        pass
    mqtt_client = MQTTClient(
            client_id=MQTT_USER,
            server=MQTT_HOST,
            user=MQTT_USER,
            password=MQTT_PWD)

    mqtt_client.set_callback(mqtt_message)
    mqtt_connected = False
    while not mqtt_connected:
        try:
            print("Connecting to MQTT")
            mqtt_client.connect()
            mqtt_connected = True
        except:
            time.sleep(0.1)
    print("Listening on " + MQTT_CHANNEL_CMD + "#")
    mqtt_client.subscribe(MQTT_CHANNEL_CMD + "#")
    print("Listening on " + MQTT_CHANNEL_ROOT + "join")
    mqtt_client.subscribe(MQTT_CHANNEL_ROOT + "join")
    print("Listening on " + MQTT_CHANNEL_HEARTBEAT)
    mqtt_client.subscribe(MQTT_CHANNEL_HEARTBEAT)
    mqtt_client.publish(MQTT_CHANNEL_ROOT+"join", "Hello from " + MQTT_USER)
    heartbeat_time_sent = time.ticks_ms()
    heartbeat_time_heard = time.ticks_ms()
    return mqtt_client
    

def network_connect():
    wifi_connect();
    return mqtt_connect();


def send_heartbeat():
    global heartbeat_time_sent
    if DEBUGOUTPUT: print("Sending heartbeat")
    mqtt_client.publish(MQTT_CHANNEL_HEARTBEAT, MQTT_USER)
    heartbeat_time_sent = now
    
motor1 = bts7960.motor((F_EN1, FPWM1), (B_EN1, BPWM1))
motor2 = bts7960.motor((F_EN2, FPWM2), (B_EN2, BPWM2))
servo1 = servo.Servo(SERVO1, SERVORANGE, 575, 2425, 50)
servo2 = servo.Servo(SERVO2, SERVORANGE, 575, 2425, 50)

wificlient = wifi.WIFI(WIFISSID, WIFIPWD)
mqtt_connected = False
speeddelta = 10
while True:
    try:
        if not wificlient.isconnected() or not mqtt_connected:
            mqtt_client = network_connect()
        mqtt_connected = True
        mqtt_client.check_msg()
        now = time.ticks_ms()
        if time.ticks_diff(now, heartbeat_time_sent) > MQTT_HEARTBEAT:
            send_heartbeat()
        wait_time = time.ticks_diff(now, heartbeat_time_heard)
        if wait_time > MQTT_HEARTBEAT:
            print("It's quiet.", wait_time)
            if wait_time > MQTT_HEARTBEAT * 5:
                print("    Too quiet!")
        #motor1.speed = motor1.speed + speeddelta
        #motor2.speed = motor1.speed
        #if motor1.speed >= 100 or motor1.speed <= -100:
        #    speeddelta = -speeddelta
        #servo1.angle = 90 + motor1.speed*0.9
        #servo2.angle = servo1.angle
    except MQTTException:
        print("MQTT exception raised")
        mqtt_connected = False