import sys
import time
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.widgets.RemoteGraphicsView
from pylibftdi import Device

app = pg.mkQApp()

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
lplt.setTitle('Temperature')
fplt = pg.PlotWidget()
fplt.setYRange(0,255)
fplt.setTitle('Forces')
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
layout.setWindowTitle('pyqtgraph example: RemoteSpeedTest')
layout.show()

## Create a PlotItem in the remote process that will be displayed locally
lastUpdate = pg.ptime.time()
data=[0]*1000
force1=[0]*100
force2=[0]*100
force3=[0]*100
avgFps = 0.0
itera = 0
oldforce = 0
buffdata = [0]*100
iterfiltre = 0
dev = Device()
dev.baudrate = 230400
count = 100
i = 0
def update():
    global dev, i, count, label, avgFps, lastUpdate, plt, data
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
        if len(rec) == 3 and rec[1] != 5:
         i+=1
         angle = rec[1] + rec[2] * 256
         if angle > 32767:
            angle -= 65536
         degre = angle*360/20000
         data[:-1] = data[1:]
         data[-1] = degre
         #print(str(degre))
         if i>= count:
            lplt.plot(data, clear=True)
            print(str(degre))
            #print(str(degre) + " | " +str(rec[0]) + " : " + str(rec[1]) + " : " +str(rec[2]))
            i=0
            #print(str(count/(end-start)))
    now = pg.ptime.time()
    fps = 1.0 / (now - lastUpdate)
    lastUpdate = now
    avgFps = avgFps * 0.8 + fps * 0.2
    label.setText("Generating %0.2f fps" % avgFps)
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


