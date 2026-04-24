#!/usr/bin/env python3

# A python script to do both listening and talking. This is the basic model
# for an audio-only mumble client.

# Usage:

# Install pyaudio (instructions: https://people.csail.mit.edu/hubert/pyaudio/#downloads)
# If `fatal error: 'portaudio.h' file not found` is encountered while installing
# pyaudio even after following the instruction, this solution might be of help:
# https://stackoverflow.com/questions/33513522/when-installing-pyaudio-pip-cannot-find-portaudio-h-in-usr-local-include
#
# Install dependencies for pymumble.
#
# Set up a mumber server. For testing purpose, you can use https://guildbit.com/
# to spin up a free server. Hard code the server details in this file.
#
# run `python3 ./listen_n_talk.py`. Now an audio-only mumble client is connected
# to the server.
#
# To test its functionality, in a separate device, use some official mumble
# client (https://www.mumble.com/mumble-download.php) to verbally communicate
# with this audio-only client.
#
# Works on MacOS. Does NOT work on RPi 3B+ (I cannot figure out why. Help will
# be much appreciated)

import pymumble_py3 as pymumble_py3
from pymumble_py3.callbacks import PYMUMBLE_CLBK_SOUNDRECEIVED as PCS
import pyaudio
import argparse
import sys

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s -I input sound device -O output sound device",
        description="Connect as two way audio client to a Mumble server."
    )
    parser.add_argument(
        "-I", "--input", help="ALSA device for sound input"
    )
    parser.add_argument(
        "-O", "--output", help="ALSA device for sound output"
    )
    return parser


parser = init_argparse()
args = parser.parse_args()

# Connection details for mumble server. Hardcoded for now, will have to be
# command line arguments eventually
pwd = ""  # password
server = "192.168.8.10"  # server address
nick = "rover"
port = 64738  # port number


# pyaudio set up
CHUNK = 1024
FORMAT = pyaudio.paInt16  # pymumble soundchunk.pcm is 16 bits
CHANNELS = 1
RATE = 48000  # pymumble soundchunk.pcm is 48000Hz

print("Initialising PyAudio")
p = pyaudio.PyAudio()
try:
  DefaultInDev = p.get_default_input_device_info()
  print("Default input device:", DefaultInDev["name"])
except IOError:
  print("No default input device")
  sys.exit(1)
try:
  DefaultOutDev = p.get_default_output_device_info()
  print("Default output device:", DefaultOutDev["name"])
except IOError:
  print("No default output device")
  sys.exit(1)

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,  # enable talk
                output=True, # and listen
                input_device_index=DefaultInDev["index"],
                output_device_index=DefaultOutDev["index"],
                frames_per_buffer=CHUNK)


# mumble client set up
def sound_received_handler(user, soundchunk):
    """ play sound received from mumble server upon its arrival """
    print("Chunk size:", soundchunk.size)
    print("Chunk duration (ms):", soundchunk.duration * 1000)
    print("Chunk type:", soundchunk.type)
    #stream.write(soundchunk.pcm)
    pass


# Spin up a client and connect to mumble server
mumble = pymumble_py3.Mumble(server, nick, password=pwd, port=port)
# set up callback called when PCS event occurs
mumble.callbacks.set_callback(PCS, sound_received_handler)
mumble.set_receive_sound(1)  # Enable receiving sound from mumble server
mumble.start()
mumble.is_ready()  # Wait for client is ready


# constant capturing sound and sending it to mumble server
print("Connected")
while True:
    data = stream.read(CHUNK, exception_on_overflow=False)
    mumble.sound_output.add_sound(data)


# close the stream and pyaudio instance
stream.stop_stream()
stream.close()
p.terminate()

