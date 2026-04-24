#!/usr/bin/bash
echo "Preparing ROS2 environment"
source ~/ros2/install/local_setup.bash

echo "Staring Rhasspy"
nohup rhasspy -p en &

echo "Starting intent processor"
nohup ~pi/roverhead/intents.py &

echo "Starting servo controller"
nohup ~pi/roverhead/head_control.py &

echo "Starting ROS2 interface"
nohup ~pi/roverhead/ros2head.py &

echo "Arming self-destruct mechanism"
nohup ~pi/roverhead/button17.py &

echo "Finished"
echo ""
