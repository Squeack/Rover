#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Raspberry Pi to Arduino I2C Communication
#i2cdetect -y 1

#library
import sys
import select
import tty
import termios
import smbus2 as smbus#,smbus2
import time

# Slave Addresses
I2C_SLAVE_ADDRESS = 16

# This function converts a string to an array of bytes.
def ConvertStringsToBytes(src):
  converted = []
  for b in src:
    converted.append(ord(b))
  return converted

def main(args):
    # Create the I2C bus
    I2Cbus = smbus.SMBus(1)
    with smbus.SMBus(1) as I2Cbus:
        slaveAddress = I2C_SLAVE_ADDRESS
        cmd = '?'
        BytesToSend = ConvertStringsToBytes(cmd)
        print("Sent " + str(slaveAddress) + " the " + str(cmd) + " command.")
        print(BytesToSend )
        looping = True
        while looping:
                I2Cbus.write_i2c_block_data(slaveAddress, 0x00, BytesToSend)
                gotReply = False;
                while looping and not gotReply:
                    try:
                        data=I2Cbus.read_i2c_block_data(slaveAddress,0x00,16)
                        # print("receive from slave:")
                        jleft = "LX:{} LY:{} LR:{} LB:{}".format(data[0]+data[1]*256,data[2]+data[3]*256,data[4]+data[5]*256,data[6]+data[7]*256)
                        jright = "RX:{} RY:{} RR:{} RB:{}".format(data[8]+data[9]*256,data[10]+data[11]*256,data[12]+data[13]*256,data[14]+data[15]*256)
                        print(jleft, jright)
                        gotReply = True
                    except:
                        print("remote i/o error")
                        time.sleep(0.5)
                    if sys.stdin in select.select([sys.stdin], [], [], 0.25)[0]:
                        inp = sys.stdin.read(1)
                        if 'q' in inp:
                            looping = False
    return 0

if __name__ == '__main__':
     try:
        oldtty = termios.tcgetattr(sys.stdin)
        stdinnum = sys.stdin.fileno()
        tty.setcbreak(stdinnum)
        main(sys.argv)
     except KeyboardInterrupt:
        print("program was stopped manually")
     finally:
         termios.tcsetattr(stdinnum, termios.TCSADRAIN, oldtty)
