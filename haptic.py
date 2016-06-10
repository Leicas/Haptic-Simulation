import sys
import time
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.widgets.RemoteGraphicsView
from pylibftdi import Device
import numpy as np
app = pg.mkQApp()
resang = 100

pg.setConfigOptions(antialias=True)  ## this will be expensive for the local plot


force = pg.SpinBox(value=0,int=True,minStep=1,step=10,bounds=(-128,128))#QtGui.QLineEdit()
phase = pg.SpinBox(value=1,minStep=0.1,step=0.1,bounds=(0,2))#QtGui.QLineEdit()
freq = pg.SpinBox(value=55,minStep=1,step=1,dec=True,bounds=(0,900))#QtGui.QLineEdit()
label = QtGui.QLabel()
labelf = QtGui.QLabel()
labelf.setText('Force')
labelp = QtGui.QLabel()
labelp.setText('Phase')
labelfr = QtGui.QLabel()
labelfr.setText('Frequence')
lcheck = QtGui.QCheckBox('plot local')
lcheck.setChecked(True)
lplt = pg.PlotWidget()
lplt.setYRange(-45,45)
lplt.setTitle('Position')
fplt = pg.PlotWidget()
fplt.setYRange(-150,150)
fplt.setTitle('Forces')
fplt.getAxis('bottom').setScale(1.0/resang)
layout = pg.LayoutWidget()
layout.addWidget(labelf)
layout.addWidget(labelp)
layout.addWidget(labelfr)
layout.addWidget(force,row=2, col=0)
layout.addWidget(phase,row=2,col=1)
layout.addWidget(freq,row=2,col=2)
layout.addWidget(lcheck, row=3, col=0)
layout.addWidget(label, row=3, col =1)
layout.addWidget(lplt, row=4, col=0, colspan=3)
layout.addWidget(fplt, row=5, col=0, colspan=3)
layout.resize(800,800)
layout.setWindowTitle('Timon 12: Demo')
layout.show()

## Create a PlotItem in the remote process that will be displayed locally
lastUpdate = pg.ptime.time()
data=[0]*1000
anglemax = 45
resang = 100
force=[0]*2*anglemax*resang
for num in range(0, 2*anglemax*resang):
    if num < anglemax*resang:
        if num < anglemax*resang/2:
            force[num]=(anglemax*resang-num*2)*1.0/resang
        else:
            force[num]=0
    else:
        if num > anglemax*resang + anglemax*resang/2:
            force[num]=(anglemax*resang-num+anglemax*resang/2)*2.0/resang
        else:
            force[num]=0
force2=[0]*100
force3=[0]*100
avgFps = 0.0
itera = 0
oldforce = 0
buffdata = [0]*100
iterfiltre = 0
dev = Device()
dev.baudrate = 230400
count = 10
i = 0
def update():
    global dev, i, count, label, avgFps, lastUpdate, plt, data, force, anglemax, resang
    rec = bytearray(dev.read(6))
    if len(rec) >= 6:
        if rec[0] != 5 or rec[3] != 5:
            rec = bytearray(dev.read(2))
            while(len(rec) < 1):
                  rec = bytearray(dev.read(1))
            while(rec[0] != 5):
                rec = bytearray(dev.read(1))
                while(len(rec) < 1):
                  rec = bytearray(dev.read(1))
            if len(rec) < 6:
                rec[1:5] = dev.read(5)
        if len(rec) == 6 and rec[3] == 5:
         i+=1
         angle = rec[1] + rec[2] * 256
         if angle > 32767:
            angle -= 65536
         degre = angle*360/20000
         data[:-1] = data[1:]
         data[-1] = degre
         #print(str(degre))
         indexf = max(min(int((anglemax+degre)*resang),anglemax*resang*2-1),0)
         forcenow=force[indexf]
         forcenowint = 32767*(1+forcenow/130)
         bufenvoi = bytearray(4)
         bufenvoi[0] = int(forcenowint) & int('0b00111111',2)
         bufenvoi[1] = ((int(forcenowint) >> 6) & int('0b00111111',2)) | int('0b01000000',2)
         bufenvoi[2] = ((int(forcenowint) >> 12) & int('0b00111111',2)) | int('0b10000000',2)
         bufenvoi[3] = int('0b11000000',2)
         dev.write(bufenvoi)
         if i>= count:
            lplt.plot(data, clear=True)
            #print(str(degre))
            #print(str(degre) + " | " +str(rec[0]) + " : " + str(rec[1]) + " : " +str(rec[2]))
            i=0
            #print(str(count/(end-start)))
            now = pg.ptime.time()
            fps = count / (now - lastUpdate)
            lastUpdate = now
            label.setText("Communication %0.2f Hz" % fps)
            fplt.plot(range(-anglemax*resang,anglemax*resang),force, clear=True)
            fplt.plot([degre*resang],[forcenow],pen=(0,0,255),symbolBrush=(255,0,0),symbolPen='r')
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


