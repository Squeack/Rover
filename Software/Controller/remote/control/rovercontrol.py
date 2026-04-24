#!/bin/env python3

print("Importing libraries")
print("  OS handling")
import sys
import select
import tty
import termios
import time
print("  Local hardware")
import smbus2 as smbus#,smbus2
print("  ROS2")
import rclpy
from geometry_msgs.msg import Twist
print("Libraries imported")

# Local hardware details
ARDUINO_ADDRESS = 16
I2Cbus = None

# ROS details
rosnode = None
pub_rovermove = None
pub_pantilt = None

# Controller zones - should be in external config file
JMIDLX = 510
JMIDLY = 506
JMIDLR = 499
JMIDRX = 509
JMIDRY = 499
JMIDRR = 516
JDEAD = 10

# Old values to avoid resending
oldfvel = 9999
oldrvel = 9999
oldavel = 9999
oldx = 9999
oldy = 9999
oldz = 9999

# This function converts a string to an array of bytes.
def ConvertStringsToBytes(src):
  converted = []
  for b in src:
    converted.append(ord(b))
  return converted


def setupHardware():
  global I2Cbus
  print("Setting up local hardware")
  I2Cbus = smbus.SMBus(1)


def setupROS2():
  global rosnode
  global pub_rovermove
  global pub_pantilt
  print("Setting up ROS2")
  rclpy.init()
  rosnode = rclpy.create_node('RemoteControl')
  pub_rovermove = rosnode.create_publisher(Twist, 'rover/move', 10)
  pub_pantilt = rosnode.create_publisher(Twist, 'rover/camera', 10)


def scaleJvalue(v,mid,dead,low,high):
  if mid-dead < v < mid+dead:
    return 0.0, True
  lorange = mid - dead - low
  hirange = high - (mid + dead)
  if v < mid:
    scaled = float(v - (mid - dead)) / lorange
  else:
    scaled = float(v - (mid + dead)) / hirange
  # Check for extreme values from misreads
  if scaled < -1.1 or scaled > 1.1:
    return 0, False
  # Clip minor overruns
  if scaled < -1:
    scaled = -1
  if scaled > 1:
    scaled = 1
  return scaled, True

def getJoystickState():
  global I2Cbus
  sentcmd = False
  while not sentcmd:
    try:
      cmd = '?'
      BytesToSend = ConvertStringsToBytes(cmd)
      I2Cbus.write_i2c_block_data(ARDUINO_ADDRESS, 0x00, BytesToSend)
      # print("Sent I2C data request")
      sentcmd = True
    except IOError:
      print("Failed on I2C write")
  gotreply = False
  jstate = {}
  valid = True
  while not gotreply:
    try:
      data=I2Cbus.read_i2c_block_data(ARDUINO_ADDRESS,0x00,16)
      jstate['lx'],ok = scaleJvalue(int(data[0]) + int(data[1]) * 256, JMIDLX, JDEAD, 0, 1024)
      valid = valid and ok
      jstate['ly'],ok = scaleJvalue(int(data[2]) + int(data[3]) * 256, JMIDLY, JDEAD, 0, 1024)
      valid = valid and ok
      jstate['lr'],ok = scaleJvalue(int(data[4]) + int(data[5]) * 256, JMIDLR, JDEAD, 0, 1024)
      valid = valid and ok
      jstate['lb'] = int(data[6]) + int(data[7]) * 256
      jstate['rx'],ok = scaleJvalue(int(data[8]) + int(data[9]) * 256, JMIDRX, JDEAD, 0, 1024)
      valid = valid and ok
      jstate['ry'],ok = scaleJvalue(int(data[10]) + int(data[11]) * 256, JMIDRY, JDEAD, 0, 1024)
      valid = valid and ok
      jstate['rr'],ok = scaleJvalue(int(data[12]) + int(data[13]) * 256, JMIDRR, JDEAD, 0, 1024)
      valid = valid and ok
      jstate['rb'] = data[14] + data[15] * 256
      # print("Received I2C reply")
      gotreply = True
    except IOError:
      print("Failed on I2C read")
      time.sleep(0.05)
  return valid, jstate


def moveRange(ov, v, e=0.0025):
  return abs(v-ov) >= e


def sendMoveCmd(fvel, rvel, avel):
  global rosnode
  global pub_rovermove
  global oldfvel, oldrvel, oldavel
  change = moveRange(oldfvel, fvel) or moveRange(oldrvel, rvel) or moveRange(oldavel, avel)
  if change:
    try:
      msg = Twist()
      msg.linear.x = fvel
      msg.linear.y = rvel
      msg.angular.z = avel
      if rclpy.ok():
        rosnode.get_logger().info("Publishing move message {:.3f}, {:.3f}, {:.3f}".format(fvel, rvel, avel))
        pub_rovermove.publish(msg) 
      oldfvel = fvel
      oldrvel = rvel
      oldavel = avel
    except:
      print(F"Exception in sendMoveCmd({fvel}, {rvel}, {avel})")


def sendPanTiltCmd(x,y,z):
  global rosnode
  global pub_pantilt
  global oldx, oldy, oldz
  change = moveRange(oldx, x) or moveRange(oldy, y) or moveRange(oldz, z)
  if change:
    msg = Twist()
    msg.angular.x = x
    msg.angular.y = y
    msg.angular.z = z # Use for focus
    if rclpy.ok():
      rosnode.get_logger().info("Publishing camera message {:.3f}, {:.3f}, {:.3f}".format(x, y, z))
      pub_pantilt.publish(msg) 
    oldx = x
    oldy = y
    oldz = z


def main(args):
  setupHardware()
  setupROS2()
  print("Initialisation complete")
  looping = True
  while looping:
    valid, jstate = getJoystickState()
    if valid:
      sendMoveCmd(float(jstate['rx']), float(jstate['ry']), float(jstate['rr']))
      sendPanTiltCmd(float(jstate['lx']), float(jstate['ly']), float(jstate['lr']))
    else:
      rosnode.get_logger().info("Invalid state read")
    if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
      inp = sys.stdin.read(1)
      if 'q' in inp:
        looping = False


if __name__ == '__main__':
  try:
    oldtty = termios.tcgetattr(sys.stdin)
    stdinnum = sys.stdin.fileno()
    tty.setcbreak(stdinnum)
    main(sys.argv)
  except KeyboardInterrupt:
    print("program was interrupted")
  finally:
    rclpy.shutdown()
    termios.tcsetattr(stdinnum, termios.TCSADRAIN, oldtty)

