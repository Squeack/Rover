#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import paho.mqtt.client as mqtt
client = None

from std_msgs.msg import String

class RoverSubscriber(Node):
    def __init__(self):
        super().__init__('rover_subscriber')
        self.csubscription = self.create_subscription( Twist, 'rover/camera', self.camera_callback, 10)
        self.msubscription = self.create_subscription( Twist, 'rover/move', self.move_callback, 10)
        #self.subscription  # prevent unused variable warning

    def camera_callback(self, msg):
        global client
        # self.get_logger().info('Camera msg: {}, {}, {}'.format(msg.angular.x, msg.angular.y, msg.angular.z))
        if msg.angular.x != 0:
            client.publish("rover/head/left/x", msg.angular.x)
            client.publish("rover/head/right/x", msg.angular.x)
            client.publish("rover/head/head/rotate", msg.angular.x)
        if msg.angular.y != 0:
            client.publish("rover/head/left/y", msg.angular.y)
            client.publish("rover/head/right/y", msg.angular.y)
            client.publish("rover/head/head/tilt", msg.angular.y)
        if msg.angular.z != 0:
            client.publish("rover/head/camera/focus/delta", msg.angular.z)
            client.publish("rover/head/blink/bottom", msg.angular.z)
            client.publish("rover/head/blink/top", msg.angular.z)

    def move_callback(self, msg):
        self.get_logger().info('Move msg: {}, {}, {}'.format(msg.linear.x, msg.linear.y, msg.angular.z))


def on_connect(client, userdata, flags, rc):
    """Called when connected to MQTT broker."""
    if rc == 0:
        print("Connected to mqtt.")
    else:
        print("Connection error code =", rc)


def on_disconnect(client, userdata, rc):
    """Called when disconnected from MQTT broker."""
    print("Disconnect code =",rc)
    if rc != 0:
        client.reconnect()


def main(args=None):
    global client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect("localhost", 1883)
    client.loop_start()

    rclpy.init(args=args)

    rover_subscriber = RoverSubscriber()
    rclpy.spin(rover_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    rover_subscriber.destroy_node()
    rclpy.shutdown()
    client.loop_stop()
    client.disconnect()


if __name__ == '__main__':
    main()
