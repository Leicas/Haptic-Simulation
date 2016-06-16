import os
import time
from threading import Thread
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from pylibftdi import Device
import multiprocessing

# Classe de lecture
def lecture(fifo):
    dev = Device()
    dev.baudrate = 230400
    while True:
        try:
            fifo.put(dev.read(1))
        except (KeyboardInterrupt, SystemExit):
            print ("Exiting lecture...")
            break

def extract(fifo, size):
    rec = bytearray([0]*size)
    for i in range(0,size):
        rec[i] = int.from_bytes(fifo.get(), 'big')
    return rec
            
def compute(threadname):
    global fifo, i, fps, count, label, avgFps, plt, shared, Force, Anglemax, Resang, Taille
    dev = Device()
    dev.baudrate = 230400
    lastUpdate = pg.ptime.time()
    while True:
        Taille = fifo.qsize()
        if(Taille>=3):
            rec = bytearray(extract(fifo,3))
            Taille = Taille - 3
            if rec[0] != 5:
                while rec[0] != 5:
                    rec = bytearray(extract(fifo,1))
                    Taille = Taille - 1
                rec[1:2] = bytearray(extract(fifo,2))
                Taille = Taille - 2
            if rec[0] == 5:
                i+=1
                angle = rec[1] + rec[2] * 256
                if angle > 32767:
                   angle -= 65536
                degre = angle*360/20000
                data = shared['data']
                data[:-1] = data[1:]
                data[-1] = degre
                shared['data'] = data
                indexf = max(min(int((Anglemax+degre)*Resang),Anglemax*Resang*2-1),0)
                forcenow=Force[indexf]
                forcenow = max(min(forcenow,130),-130)
                forcenowint = 32767*(1+forcenow/130)
                shared['degre'] = degre
                shared['forcenow'] = forcenow
                bufenvoi = bytearray(4)
                bufenvoi[0] = int(forcenowint) & int('0b00111111',2)
                bufenvoi[1] = ((int(forcenowint) >> 6) & int('0b00111111',2)) | int('0b01000000',2)
                bufenvoi[2] = ((int(forcenowint) >> 12) & int('0b00111111',2)) | int('0b10000000',2)
                bufenvoi[3] = int('0b11000000',2)
                if i>= count:
                    i= 0
                    now = pg.ptime.time()
                    shared['fps'] = count / (now - lastUpdate)
                    shared['Taille'] = Taille
                    lastUpdate = now
                dev.write(bufenvoi)

Resang = 100


## Create a PlotItem in the remote process that will be displayed locally
Anglemax = 45
Resang = 100
degre = 0
forcenow = 0
Taille = 0
Force=[0]*2*Anglemax*Resang
for num in range(0, 2*Anglemax*Resang):
    if num < Anglemax*Resang:
        if num < Anglemax*Resang/2:
            Force[num]=(Anglemax*Resang-num*2)*4.0/Resang
        else:
            Force[num]=0
    else:
        if num > Anglemax*Resang + Anglemax*Resang/2:
            Force[num]=(Anglemax*Resang-num+Anglemax*Resang/2)*8.0/Resang
        else:
            Force[num]=0

force3=[0]*100
fps = multiprocessing.Value('d',0.0)
itera = 0
oldforce = 0
buffdata = [0]*100
iterfiltre = 0
#data=[0]*1000

count = 100
i = 0



class Graph(pg.QtCore.QThread):
    newData = pg.QtCore.Signal()
    def __init__(self):
        super(Graph, self).__init__()
        self.stopMutex = Lock()
        self._stop = False
    def run(self):
        while True:
            with self.stopMutex:
                if self._stop:
                    break
            self.newData.emit()
            time.sleep(0.2)
    def stop(self):
        with self.stopMutex:
            self._stop = True

def Affichage(name, shared):
    pg.mkQApp()
    pg.setConfigOptions(antialias=True)  ## this will be expensive for the local plot
    force = pg.SpinBox(value=0,int=True,minStep=1,step=10,bounds=(-128,128))#QtGui.QLineEdit()
    phase = pg.SpinBox(value=1,minStep=0.1,step=0.1,bounds=(0,2))#QtGui.QLineEdit()
    freq = pg.SpinBox(value=55,minStep=1,step=1,dec=True,bounds=(0,900))#QtGui.QLineEdit()
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
    lplt.setYRange(-45,45)
    lplt.setTitle('Position')
    fplt = pg.PlotWidget()
    fplt.setYRange(-150,150)
    fplt.setTitle('Forces')
    fplt.getAxis('bottom').setScale(1.0/Resang)
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
    #data = shared['data']
    def update(shared):
        localdata=[0]*1000
        Taille = shared['Taille']
        localdata=shared['data']
        #for i in range(0,1000):
        #    localdata[i] = shared['data'][i]
        lplt.plot(localdata, clear=True)
        fps = shared['fps']
        label.setText("Communication %0.2f Hz Taille buffer: %0.2f" % (fps, Taille/3.0))
        Anglemax = shared['anglemax']
        Resang = shared['Resang']
        Force = shared['force']
        degre = shared['degre']
        forcenow = shared['forcenow']
        fplt.plot(range(-Anglemax*Resang,Anglemax*Resang),Force, clear=True)
        fplt.plot([degre*Resang],[forcenow],pen=(0,0,255),symbolBrush=(255,0,0),symbolPen='r')
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: update(shared))
    timer.start(50)
    QtGui.QApplication.instance().exec_()

    
if __name__ == '__main__':
    fifo = multiprocessing.Queue()
    manager = multiprocessing.Manager()
    shared = manager.dict()
    data = manager.list()
    data = [0] * 1000
    shared['data'] = data
    shared['fps'] = 0.0
    shared['anglemax'] = Anglemax
    shared['Resang'] = Resang
    shared['force'] = Force
    shared['degre'] = degre
    shared['forcenow'] = forcenow
    ##lecture = Thread(target=lecture, args=("Thread-1", ) )
    compute = Thread(target=compute, args=("Thread-2", ) )
    lecturep = multiprocessing.Process(target=lecture, args=(fifo,))
    lecturep.start()
    time.sleep(0.5)
    print(fifo.get())
    compute.start()
    affp = multiprocessing.Process(target=Affichage, args=("test",shared,))
    affp.start()
    while True:
        try:
            print("encore")
            #shared['data']=data
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            print ("Exiting lecture...")
            lecturep.terminate()
            lecturep.join()
            print ("lecture excited...")
            affp.terminate()
            affp.join()
            print ("Exiting...")
            os._exit(0)
            break
##    graph = Graph()
##    graph.newData.connect(update)
##    graph.start()

        

