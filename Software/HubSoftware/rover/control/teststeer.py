#!/bin/env python3

import marsrover

rover = marsrover.Rover(sr=270)

print("Straight ahead")
rover.set_control(1,0,0)
print(rover.get_drive_front())

print("Ahead diagonal right")
rover.set_control(1,-1,0)
print(rover.get_drive_front())

print("Ahead diagonal left")
rover.set_control(1,1,0)
print(rover.get_drive_front())

print("Spin right")
rover.set_control(0,0,1)
print(rover.get_drive_front())

print("Spin left")
rover.set_control(0,0,-1)
print(rover.get_drive_front())

print("Ahead turning right")
rover.set_control(1,0,1)
print(rover.get_drive_front())

print("Ahead turning left")
rover.set_control(1,0,-1)
print(rover.get_drive_front())

print("Straight left")
rover.set_control(0,1,0)
print(rover.get_drive_front())

print("Straight right")
rover.set_control(0,-1,0)
print(rover.get_drive_front())

print("Straight back")
rover.set_control(-1,0,0)
print(rover.get_drive_front())

print("Back diagonal right")
rover.set_control(-1,-1,0)
print(rover.get_drive_front())

print("Back diagonal left")
rover.set_control(-1,1,0)
print(rover.get_drive_front())

print("Back turning right")
rover.set_control(-1,0,1)
print(rover.get_drive_front())

print("Back turning left")
rover.set_control(-1,0,-1)
print(rover.get_drive_front())


