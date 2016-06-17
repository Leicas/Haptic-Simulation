"""
Created on Thu Jun 16 17:54:49 2016

@author: antoine
"""
from threading import Thread
from multiprocessing import Process, Queue
from pylibftdi import Device

class _DeviceProcess(Process):
    """ Process for in/out control """
    def __init__(self, FIFOreception, FIFOenvoi):
        super(_DeviceProcess, self).__init__()
        self.fifoin = FIFOreception
        self.fifoout = FIFOenvoi
    def lecture(self, name):
        """ Read the device informations """
        print(name +' started')
        while True:
            try:
                self.fifoin.put(self.dev.read(1))
            except (KeyboardInterrupt, SystemExit):
                print("Exiting lecture...")
                break
    def write(self, name):
        """ Write the information to the device """
        print(name +' started')
        while True:
            if self.fifoout.qsize() >= 1:
                tosend = self.fifoout.get()
                self.dev.write(tosend)
    def run(self):
        self.dev = Device()#pylint: disable=W0201
        self.dev.baudrate = 230400
        writing = Thread(target=self.write, args=("Thread-write",))
        writing.start()
        lecturing = Thread(target=self.lecture, args=("Thread-read",))
        lecturing.start()
#DEV = Device()
class HDevice:
    """ Function to read/write to device """
    def __init__(self):
        super(HDevice, self).__init__()
        self.fifoin = Queue()
        self.fifoout = Queue()
        self.processdev = _DeviceProcess(self.fifoin, self.fifoout)
    def launch(self):
        """ Launch the process for device communication """
        self.processdev.start()
    def get(self):
        """ get byte from device """
        return self.fifoin.get()
    def quit(self):
        """ quit device process """
        self.processdev.terminate()
        self.processdev.join()
    def extract(self, size):
        """ Extract 'size' bytes from 'fifo' and return a bytearray """
        rec = bytearray([0]*size)
        for i in range(0, size):
            rec[i] = int.from_bytes(self.fifoin.get(), 'big')
        return rec
    def readarray(self, size):
        """ read a bytearray from device """
        return bytearray(self.extract(size))
    def incommingsize(self):
        """get the incomming buffer size"""
        return self.fifoin.qsize()
    def writeint(self, tosend):
        """write data to haptic device"""
        bufenvoi = bytearray(4)
        bufenvoi[0] = int(tosend) & int('0b00111111', 2)
        bufenvoi[1] = ((int(tosend) >> 6) & int('0b00111111', 2)) | int('0b01000000', 2)
        bufenvoi[2] = ((int(tosend) >> 12) & int('0b00111111', 2)) | int('0b10000000', 2)
        bufenvoi[3] = int('0b11000000', 2)
        self.fifoout.put(bufenvoi)
    def write(self, tosend):
        """ convert and send data to haptic device"""
        forcenow = max(min(tosend, 130), -130)
        forcenowint = 32767*(1+forcenow/130)
        self.writeint(forcenowint)




