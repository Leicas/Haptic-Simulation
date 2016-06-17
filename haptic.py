""" Module for Communication and Ploting of Force """
import os
import time
from threading import Thread
import multiprocessing
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from pylibftdi import Device
import com

RESANG = 100

COUNT = 100
ANGLEMAX = 45



def compute(threadname):
    """ Compute the force """
    dev = Device()
    dev.baudrate = 230400
    lastupdate = pg.ptime.time()
    i = 0
    while True:
        taille = HAPTICDEV.incommingsize() #FIFO.qsize()
        if taille >= 3:
            rec = HAPTICDEV.readarray(3)#bytearray(extract(FIFO, 3))
            taille = taille - 3
            if rec[0] != 5:
                while rec[0] != 5:
                    rec = HAPTICDEV.readarray(1)#bytearray(extract(FIFO, 1))
                    taille = taille - 1
                rec[1:2] = HAPTICDEV.readarray(2)#bytearray(extract(FIFO, 2))
                taille = taille - 2
            if rec[0] == 5:
                i += 1
                angle = rec[1] + rec[2] * 256
                if angle > 32767:
                    angle -= 65536
                degre = angle*360/20000
                data = SHARED['data']
                data[:-1] = data[1:]
                data[-1] = degre
                SHARED['data'] = data
                indexf = max(min(int((ANGLEMAX+degre)*RESANG), ANGLEMAX*RESANG*2-1), 0)
                forcenow = FORCE[indexf]
                forcenow = max(min(forcenow, 130), -130)
                HAPTICDEV.write(forcenow)
                SHARED['degre'] = degre
                SHARED['forcenow'] = forcenow

                if i >= COUNT:
                    i = 0
                    now = pg.ptime.time()
                    SHARED['fps'] = COUNT / (now - lastupdate)
                    SHARED['taille'] = taille
                    lastupdate = now
                #dev.write(bufenvoi)

def affichage(name, shareddic):
    """ Ploting and Display """
    pg.mkQApp()
    pg.setConfigOptions(antialias=True)  ## this will be expensive for the local plot
    force = pg.SpinBox(value=0, int=True, minStep=1, step=10, bounds=(-128, 128))#QtGui.QLineEdit()
    phase = pg.SpinBox(value=1, minStep=0.1, step=0.1, bounds=(0, 2))#QtGui.QLineEdit()
    freq = pg.SpinBox(value=55, minStep=1, step=1, dec=True, bounds=(0, 900))#QtGui.QLineEdit()
    label = QtGui.QLabel()
    #self.data = data
    #self.fps = fps
    labelf = QtGui.QLabel()
    labelf.setText('Force')
    labelp = QtGui.QLabel()
    labelp.setText('Phase')
    labelfr = QtGui.QLabel()
    labelfr.setText('Frequence')
    lcheck = QtGui.QCheckBox('plot local')
    lcheck.setChecked(True)
    lplt = pg.PlotWidget()
    lplt.setYRange(-45, 45)
    lplt.setTitle('Position')
    fplt = pg.PlotWidget()
    fplt.setYRange(-150, 150)
    fplt.setTitle('Forces')
    fplt.getAxis('bottom').setScale(1.0/RESANG)
    layout = pg.LayoutWidget()
    layout.addWidget(labelf)
    layout.addWidget(labelp)
    layout.addWidget(labelfr)
    layout.addWidget(force, row=2, col=0)
    layout.addWidget(phase, row=2, col=1)
    layout.addWidget(freq, row=2, col=2)
    layout.addWidget(lcheck, row=3, col=0)
    layout.addWidget(label, row=3, col=1)
    layout.addWidget(lplt, row=4, col=0, colspan=3)
    layout.addWidget(fplt, row=5, col=0, colspan=3)
    layout.resize(800, 800)
    layout.setWindowTitle('Timon 12: Demo')
    layout.show()
    def update(shareddic):
        """ Every refresh of the display """
        localdata = [0]*1000
        taille = shareddic['taille']
        localdata = shareddic['data']
        lplt.plot(localdata, clear=True)
        fps = shareddic['fps']
        label.setText("Communication %0.2f Hz Taille buffer: %0.2f" % (fps, taille/3.0))
        force = shareddic['force']
        degre = shareddic['degre']
        forcenow = shareddic['forcenow']
        fplt.plot(range(-ANGLEMAX*RESANG, ANGLEMAX*RESANG), force, clear=True)
        fplt.plot([degre*RESANG], [forcenow], pen=(0, 0, 255), symbolBrush=(255, 0, 0), symbolPen='r')
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: update(shareddic))
    timer.start(50)
    QtGui.QApplication.instance().exec_()

def setforce():
    """ init force field """
    force = [0]*2*ANGLEMAX*RESANG
    for num in range(0, 2*ANGLEMAX*RESANG):
        if num < ANGLEMAX*RESANG:
            if num < ANGLEMAX*RESANG/2:
                force[num] = (ANGLEMAX*RESANG-num*2)*4.0/RESANG
            else:
                force[num] = 0
        else:
            if num > ANGLEMAX*RESANG + ANGLEMAX*RESANG/2:
                force[num] = (ANGLEMAX*RESANG-num+ANGLEMAX*RESANG/2)*8.0/RESANG
            else:
                force[num] = 0
    return force

if __name__ == '__main__':
    #FIFO = multiprocessing.Queue()
    FORCE = setforce()
    MANAGER = multiprocessing.Manager()
    SHARED = MANAGER.dict()
    SHARED['data'] = [0] * 1000
    SHARED['fps'] = 0.0
    SHARED['ANGLEMAX'] = ANGLEMAX
    SHARED['RESANG'] = RESANG
    SHARED['force'] = FORCE
    SHARED['degre'] = 0
    SHARED['forcenow'] = 0
    COMPUTE = Thread(target=compute, args=("Thread-2",))
    HAPTICDEV = com.HDevice()
    HAPTICDEV.launch()
    time.sleep(0.5)
    print(HAPTICDEV.get())
    COMPUTE.start()
    AFFP = multiprocessing.Process(target=affichage, args=("test", SHARED,))
    AFFP.start()
    while True:
        try:
            print("encore")
            #SHARED['data']=data
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            print("Exiting lecture...")
            HAPTICDEV.quit()
            print("lecture excited...")
            AFFP.terminate()
            AFFP.join()
            print("Exiting...")
            os._exit(0)
            break
