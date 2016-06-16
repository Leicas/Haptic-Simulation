"""
Created on Thu Jun 16 17:54:49 2016

@author: antoine
"""
from pylibftdi import Device
def lecture(sortie):
    """ Read the device informations """
    dev = Device()
    dev.baudrate = 230400
    while True:
        try:
            sortie.put(dev.read(1))
        except (KeyboardInterrupt, SystemExit):
            print("Exiting lecture...")
            break
