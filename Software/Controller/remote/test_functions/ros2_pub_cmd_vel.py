#!/usr/bin/python3

print("Importing libraries")
import rclpy
import rclpy.node
from rcl_interfaces.msg import ParameterDescriptor
from rclpy.parameter import Parameter
from geometry_msgs.msg import Twist
import time

class VelParam(rclpy.node.Node):
    def __init__(self):
        super().__init__('param_vel_node')
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.msg = Twist()
        fparam_descriptor = ParameterDescriptor(
            description='Sets the forward velocity (in m/s) of the robot.')
        self.declare_parameter('fvel', 0.0, fparam_descriptor)
        rparam_descriptor = ParameterDescriptor(
            description='Sets the side velocity (in m/s, +ve = right) of the robot.')
        self.declare_parameter('rvel', 0.0, rparam_descriptor)
        aparam_descriptor = ParameterDescriptor(
            description='Sets the angular velocity (in deg/s clockwise) of the robot.')
        self.declare_parameter('avel', 0.0, aparam_descriptor)
        # self.add_on_set_parameters_callback(self.parameter_callback)

    def timer_callback(self):
        fparam = self.get_parameter('fvel').value
        rparam = self.get_parameter('rvel').value
        aparam = self.get_parameter('avel').value

        self.get_logger().info("Velocity parameters = {:.2f}, {:.2f}, {:.2f}".format(fparam, rparam, aparam))

        self.msg.linear.x = fparam
        self.msg.linear.y = rparam
        self.msg.linear.z = 0.0
        self.msg.angular.x = 0.0
        self.msg.angular.y = 0.0
        self.msg.angular.z = aparam
        self.publisher.publish(self.msg)

def main():
    rclpy.init()
    node = VelParam()
    for x in range(30):
        print(x)
        fparam = Parameter('fvel', Parameter.Type.DOUBLE, 15.0-x)
        rparam = Parameter('rvel', Parameter.Type.DOUBLE, 0.1*x)
        aparam = Parameter('avel', Parameter.Type.DOUBLE, 2.0*x)
        node.set_parameters([fparam, rparam, aparam])
        rclpy.spin_once(node)
        time.sleep(2)


if __name__ == '__main__':
    main()

