#!/bin/env python3

print("Importing libraries")
print("  OS handling")
import sys
import select
import tty
import termios
import time
print("  ROS2")
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
print("Libraries imported")


class MoveListener(Node):
  def __init__(self):
    super().__init__('move_subscriber')
    self.subscription = self.create_subscription(Twist, 'rover/move', self.listener_callback, 10)
    self.subscription # prevent unused variable warning

  def listener_callback(self, msg):
    linx = msg.linear.x
    liny = msg.linear.y
    linz = msg.linear.z
    angx = msg.angular.x
    angy = msg.angular.y
    angz = msg.angular.z
    self.get_logger().info(f"Move message: Linear=({linx}, {liny}, {linz}), Angular=({angx}, {angy}, {angz})")


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
    self.get_logger().info(f"Camera message: Linear=({linx}, {liny}, {linz}), Angular=({angx}, {angy}, {angz})")


def setupROS2():
  print("Setting up ROS2")
  rclpy.init()


def main(args):
  setupROS2()
  nodequeue = []
  nodequeue.append(MoveListener())
  nodequeue.append(CameraListener())
  while rclpy.ok():
    try:
      for node in nodequeue:
        rclpy.spin_once(node, timeout_sec=0.005) # 5ms timeout per node
    except Exception as e:
      print(f"Exception during ROS processing loop: {e}")

if __name__ == '__main__':
  try:
    main(sys.argv)
  except KeyboardInterrupt:
    print("Interrupted")
  finally:
    if rclpy.ok():
      rclpy.shutdown()
