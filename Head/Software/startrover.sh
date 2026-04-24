#!/usr/bin/bash
source ~/ros2/install/local_setup.bash
rhasspy -p en &
~pi/roverhead/intents.py &
~pi/roverhead/head_control.py &
~pi/roverhead/ros2head.py &

