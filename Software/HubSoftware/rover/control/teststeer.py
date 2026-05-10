#!/bin/env python3

import marsrover

rover = marsrover.Rover(sr=180)

print(rover.get_wheel_pos_front())
print(rover.get_wheel_pos_mid())
print(rover.get_wheel_pos_rear())

print("Straight ahead 1 0 0")
rover.set_control(1,0,0)
rover.set_control(1,0,0,True)
print(rover.get_drive_front())
print(rover.get_drive_mid())
print(rover.get_drive_rear())

print("Ahead diagonal right 1 -1 0")
rover.set_control(1,0,0)
rover.set_control(1,-1,0,True)
print(rover.get_drive_front())
print(rover.get_drive_mid())
print(rover.get_drive_rear())

print("Ahead diagonal left 1 1 0")
rover.set_control(1,0,0)
rover.set_control(1,1,0,True)
print(rover.get_drive_front())
print(rover.get_drive_mid())
print(rover.get_drive_rear())

print("Spin right 0 0 1")
rover.set_control(1,0,0)
rover.set_control(0,0,1,True)
print(rover.get_drive_front())
print(rover.get_drive_mid())
print(rover.get_drive_rear())

print("Spin left 0 0 -1")
rover.set_control(1,0,0)
rover.set_control(0,0,-1,True)
print(rover.get_drive_front())
print(rover.get_drive_mid())
print(rover.get_drive_rear())

print("Ahead turning right 1 0 0.5")
rover.set_control(1,0,0)
rover.set_control(1,0,0.5,True)
print(rover.get_drive_front())
print(rover.get_drive_mid())
print(rover.get_drive_rear())

print("Ahead turning left 1 0 -0.5")
rover.set_control(1,0,0)
rover.set_control(1,0,-0.5,True)
print(rover.get_drive_front())
print(rover.get_drive_mid())
print(rover.get_drive_rear())

print("Straight left 0 1 0")
rover.set_control(1,0,0)
rover.set_control(0,1,0,True)
print(rover.get_drive_front())
print(rover.get_drive_mid())
print(rover.get_drive_rear())

print("Straight right 0 -1 0")
rover.set_control(1,0,0)
rover.set_control(0,-1,0,True)
print(rover.get_drive_front())
print(rover.get_drive_mid())
print(rover.get_drive_rear())

print("Straight back -1 0 0")
rover.set_control(1,0,0)
rover.set_control(-1,0,0,True)
print(rover.get_drive_front())
print(rover.get_drive_mid())
print(rover.get_drive_rear())

print("Back diagonal right -1 -1 0")
rover.set_control(1,0,0)
rover.set_control(-1,-1,0,True)
print(rover.get_drive_front())
print(rover.get_drive_mid())
print(rover.get_drive_rear())

print("Back diagonal left -1 1 0")
rover.set_control(1,0,0)
rover.set_control(-1,1,0,True)
print(rover.get_drive_front())
print(rover.get_drive_mid())
print(rover.get_drive_rear())

print("Back turning right -1 0 0.5")
rover.set_control(1,0,0)
rover.set_control(-1,0,0.5,True)
print(rover.get_drive_front())
print(rover.get_drive_mid())
print(rover.get_drive_rear())

print("Back turning left -1 0 -0.5")
rover.set_control(1,0,0)
rover.set_control(-1,0,-0.5,True)
print(rover.get_drive_front())
print(rover.get_drive_mid())
print(rover.get_drive_rear())


