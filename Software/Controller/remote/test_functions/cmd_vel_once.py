#!/usr/bin/python3

print("Importing libraries")
import rclpy
from geometry_msgs.msg import Twist
import time

def main():
    rclpy.init()
    node = rclpy.create_node('Twist_Sender')
    pub = node.create_publisher(Twist, 'cmd_vel', 10)
    msg = Twist()
  
    for x in range(30):
        print(x)
        msg.linear.x = 15.0-x
        msg.linear.y = 0.1*x
        msg.linear.z = 0.0
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = 1.5*x
        if rclpy.ok():
            node.get_logger().info("Publishing message {}".format(x))
            pub.publish(msg)
        time.sleep(2)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

