#!/bin/bash
echo $(tty)
if [ $(tty) = "/dev/tty1" ]; then
    echo "Running on the console."
    echo "Starting kiosk application"
    cd ./remote/menu
    /usr/bin/python3 remote_console.py
else
    echo "Not running kiosk application"
fi
