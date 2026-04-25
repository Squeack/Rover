#!/bin/env python3

DEBUG = False

print("Importing libraries")
print("  OS handling")
import sys
import select
import tty
import termios
import time
print("  MQTT")
import paho.mqtt.client as mqtt
mqtt_connected = False
mqttc = None
print("  ROS2")
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import marsrover
print("Libraries imported")

heartbeat_time = time.time()
rover = marsrover.Rover(sr=270)

class MoveListener(Node):
  def __init__(self):
    super().__init__('move_subscriber')
    self.subscription = self.create_subscription(Twist, 'rover/move', self.listener_callback, 10)
    self.subscription # prevent unused variable warning

  def listener_callback(self, msg):
    global mqttc
    global rover
    linx = msg.linear.x
    liny = msg.linear.y
    linz = msg.linear.z
    angx = msg.angular.x
    angy = msg.angular.y
    angz = msg.angular.z
    if DEBUG: self.get_logger().info(f"Move message: Linear=({linx}, {liny}, {linz}), Angular=({angx}, {angy}, {angz})")
    if mqttc is not None:
      rover.set_control(liny, linx, -angz)
      vl, al, vr, ar = rover.get_drive_front()
      mqttc.publish("rover/motor/cmd/motor1/speedl",str(vl))
      mqttc.publish("rover/motor/cmd/motor1/anglel",str(al))
      mqttc.publish("rover/motor/cmd/motor1/speedr",str(vr))
      mqttc.publish("rover/motor/cmd/motor1/angler",str(ar))
      vl, al, vr, ar = rover.get_drive_mid()
      mqttc.publish("rover/motor/cmd/motor2/speedl",str(vl))
      mqttc.publish("rover/motor/cmd/motor2/anglel",str(al))
      mqttc.publish("rover/motor/cmd/motor2/speedr",str(vr))
      mqttc.publish("rover/motor/cmd/motor2/angler",str(ar))
      vl, al, vr, ar = rover.get_drive_rear()
      mqttc.publish("rover/motor/cmd/motor3/speedl",str(vl))
      mqttc.publish("rover/motor/cmd/motor3/anglel",str(al))
      mqttc.publish("rover/motor/cmd/motor3/speedr",str(vr))
      mqttc.publish("rover/motor/cmd/motor3/angler",str(ar))

class CameraListener(Node):
  def __init__(self):
    super().__init__('camera_subscriber')
    self.subscription = self.create_subscription(Twist, 'rover/camera', self.listener_callback, 10)
    self.subscription # prevent unused variable warning

  def listener_callback(self, msg):
    linx = msg.linear.x
    liny = msg.linear.y
    linz = msg.linear.z
    angx = msg.angular.x
    angy = msg.angular.y
    angz = msg.angular.z
    if DEBUG: self.get_logger().info(f"Camera message: Linear=({linx}, {liny}, {linz}), Angular=({angx}, {angy}, {angz})")


def setupROS2():
  print("Setting up ROS2")
  rclpy.init()


def on_subscribe(client, userdata, mid, reason_code_list):
  # Since we subscribed only for a single channel, reason_code_list contains
  # a single entry
  if reason_code_list[0] != 0:
    print(f"Broker rejected your subscription: {reason_code_list[0]}")
  else:
    print(f"Broker granted the following QoS: {reason_code_list[0]}")


def on_unsubscribe(client, userdata, mid, reason_code_list):
  # Be careful, the reason_code_list is only present in MQTTv5.
  # In MQTTv3 it will always be empty
  if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
    print("unsubscribe succeeded (if SUBACK is received in MQTTv3 it success)")
  else:
    print(f"Broker replied with failure: {reason_code_list[0]}")
  client.disconnect()


def on_message(client, userdata, message):
  # userdata is the structure we choose to provide
  if DEBUG: print(f"MQTT message: {message.topic}={message.payload.decode('utf-8')}")


def on_connect(client, userdata, flags, reason_code):
  global mqtt_connected
  if reason_code != 0:
    print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
  else:
    print("Connected to MQTT broker")
    mqtt_connected = True
    # we should always subscribe from on_connect callback to be sure
    # our subscribed is persisted across reconnections.
    print("Subscribing to topics of interest")
    client.subscribe("rover/#")


def on_disconnect(client, userdata, reason_code):
  global mqtt_connected
  mqtt_connected = False
  if reason_code != 0:
    print(f"MQTT disconnection for reason {reason_code}. Trying to reconnect...")
    client.connect("localhost")
  else:
    client.close()
    print("MQTT disconnected cleanly")
    

def setupMQTT():
  print("Setting up MQTT")
  mqttc = mqtt.Client("hub")
  mqttc.username_pw_set("hub", "Opportunity")
  mqttc.on_connect = on_connect
  mqttc.on_disconnect = on_disconnect
  mqttc.on_message = on_message
  mqttc.on_subscribe = on_subscribe
  mqttc.on_unsubscribe = on_unsubscribe
  print("About to connect")
  mqttc.loop_start()
  mqttc.connect("localhost") 
  while not mqtt_connected:
    time.sleep(0.25)
  mqttc.loop_stop()
  return mqttc


def main(args):
  global mqttc
  global heartbeat_time
  mqttc = setupMQTT()
  setupROS2()
  nodequeue = []
  nodequeue.append(MoveListener())
  nodequeue.append(CameraListener())
  mqttc.loop_start()
  print("Now active...")
  while rclpy.ok():
    now = time.time()
    if now - heartbeat_time > 10:
      heartbeat_time = now
      mqttc.publish("rover/motor/heartbeat", "hub")
    try:
      for node in nodequeue:
        rclpy.spin_once(node, timeout_sec=0.002) # 2ms timeout per node
    except Exception as e:
      print(f"Exception during ROS processing loop: {e}")
      raise
  mqttc.loop_stop()

if __name__ == '__main__':
  try:
    main(sys.argv)
  except KeyboardInterrupt:
    print("Interrupted")
  finally:
    if rclpy.ok():
      rclpy.shutdown()
