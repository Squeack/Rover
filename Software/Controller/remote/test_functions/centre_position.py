#!/usr/bin/env python3
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
from statistics import mean

# Slave Addresses
I2C_SLAVE_ADDRESS = 16

# This function converts a string to an array of bytes.
def ConvertStringsToBytes(src):
  converted = []
  for b in src:
    converted.append(ord(b))
  return converted

def main(args):
    rxval = [0] * 100
    ryval = [0] * 100
    rrval = [0] * 100
    rbut = [0] * 100
    lxval = [0] * 100
    lyval = [0] * 100
    lrval = [0] * 100
    lbut = [0] * 100
    # Create the I2C bus
    I2Cbus = smbus.SMBus(1)
    with smbus.SMBus(1) as I2Cbus:
        slaveAddress = I2C_SLAVE_ADDRESS
        cmd = '?'
        BytesToSend = ConvertStringsToBytes(cmd)
        print("Sent " + str(slaveAddress) + " the " + str(cmd) + " command.")
        print(BytesToSend )
        looping = True
        n=0
        while looping:
            gotReply = True
            try:
                I2Cbus.write_i2c_block_data(slaveAddress, 0x00, BytesToSend)
                gotReply = False;
            except IOError:
                print("Failed on I2C write")
                continue
            while looping and not gotReply:
                try:
                    data=I2Cbus.read_i2c_block_data(slaveAddress,0x00,16)
                    # print("receive from slave:")
                    lxval[n] = data[0] + data[1] * 256
                    lyval[n] = data[2] + data[3] * 256
                    lrval[n] = data[4] + data[5] * 256
                    lbut[n] = data[6] + data[7] * 256
                    rxval[n] = data[8] + data[9] * 256
                    ryval[n] = data[10] + data[11] * 256
                    rrval[n] = data[12] + data[13] * 256
                    rbut[n] = data[14] + data[15] * 256

                    # jleft = "LX:{} LY:{} LR:{} LB:{}".format(lxval[n], lyval[n], lrval[n], lbut[n])
                    # jright = "RX:{} RY:{} RR:{} RB:{}".format(rxval[n], ryval[n], rrval[n], rbut[n])
                    # print(jleft, jright)
                    gotReply = True
                    n = (n + 1) % 100
                    if n == 0:
                        print("LX: {} - {} - {}".format(min(lxval), mean(lxval), max(lxval)))
                        print("LY: {} - {} - {}".format(min(lyval), mean(lyval), max(lyval)))
                        print("LR: {} - {} - {}".format(min(lrval), mean(lrval), max(lrval)))
                        print("RX: {} - {} - {}".format(min(rxval), mean(rxval), max(rxval)))
                        print("RY: {} - {} - {}".format(min(ryval), mean(ryval), max(ryval)))
                        print("RR: {} - {} - {}".format(min(rrval), mean(rrval), max(rrval)))
                        print("")
                except IOError:
                    print("Failed on I2C read")
                    time.sleep(0.5)
                if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
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
