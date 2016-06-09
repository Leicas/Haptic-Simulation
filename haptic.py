import sys
import time
from pylibftdi import Device

count = 1000
with Device() as dev:
    dev.baudrate = 230400
    i = 0
    start = time.time()
    while(1==1):
        
        rec = bytearray(dev.read(3))
        if len(rec) >= 3:
            if rec[0] != 5 or rec[1] == 5:
                rec = bytearray(dev.read(2))
                while(len(rec) < 1):
                      rec = bytearray(dev.read(1))
                while(rec[0] != 5):
                    rec = bytearray(dev.read(1))
                    while(len(rec) < 1):
                      rec = bytearray(dev.read(1))
                if len(rec) < 3:
                    rec[1:2] = dev.read(2)
            if len(rec) >= 3 and rec[1] != 5:
             i+=1
             if i>= count:
                angle = rec[1] + rec[2] * 256
                if angle > 32767:
                    angle -= 65536
                degre = angle*360/20000
                end = time.time()
                print(str(degre) + " | " +str(count/(end-start)))
                #print(str(degre) + " | " +str(rec[0]) + " : " + str(rec[1]) + " : " +str(rec[2]))
                i=0
                #print(str(count/(end-start)))
                start = time.time()
