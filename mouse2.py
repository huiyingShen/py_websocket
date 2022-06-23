import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter,QPixmap,QPen,QTransform,QFont
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton

from webSocketServerClient import getClient,b64toImg
import threading

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, 400, 300)
        transform = QTransform().rotate(-90)
        self.btn1 = self.addButton("Reload Image", self.reloadImage)
        self.btn2 = self.addButton("New Image", self.ask4Image)
        self.btn3 = self.addButton("Send Data", self.sendData)
        self.loadImage(QPixmap("some_image.jpg").transformed(transform))
        self.pnts = []

        self.ws = getClient("34.237.62.252",8001)
        threading.Thread(target=self.receiving, args=(self.ws,)).start()
        
    def receiving(self,ws):
        print("start receiving")
        while True:
            txt = ws.recv()
            if len(txt) < 100:
                print("txt = ", txt)
            else:
                print("len = ",len(txt))
                print("txt[:100] = ",txt[:100])
                s = txt[:100]+"_test"
                pos = s.find(' - ')
                print("pos = ", pos)
                print(txt[pos+3:100])
                try:
                    b64toImg(txt[pos+3:])
                    transform = QTransform().rotate(-90)
                    self.loadImage(QPixmap("some_image.jpg").transformed(transform))
                    self.pnts = []
                except:
                    pass

    def addButton(self,txt,fn):
        btn = QPushButton(txt,self)
        btn.setFont(QFont('Times', 18))  
        btn.clicked.connect(fn)
        return btn

    def reloadImage(self):
        self.image = self.imgCopy.transformed(QTransform().scale(1,1))
        self.pnts = []
        self.setLayout()

    def ask4Image(self):
        self.ws.send(f"image, please")

    def sendData(self):
        # jnk = self.pnts.splitlines()
        h = self.image.height()
        jnk = ""
        for p in self.pnts:
            x,y = h-p[1], p[0]
            jnk += '\n{} {}'.format(h-p[1], p[0])
        print(jnk[1:])
        self.ws.send(f"New Landmark Data:" + jnk[1:])


    def setLayout(self):
        self.label.setPixmap(self.image)
        self.label.resize(self.image.width(), self.image.height())
        self.setFixedSize(self.image.width(), self.image.height()+50)

        self.btn1.setGeometry(10, self.image.height()+5, 200, 40)
        self.btn2.setGeometry(210, self.image.height()+5, 200, 40)
        self.btn3.setGeometry(420, self.image.height()+5, 200, 40)

    def loadImage(self,pix):
        self.imgCopy = pix.transformed(QTransform().scale(1,1))
        self.image = pix
        self.setLayout()


    def mousePressEvent(self, e):
        print(e.pos().x(),e.pos().y())
        # self.pnts += '\n{} {}'.format(e.pos().x(),e.pos().y())
        self.pnts.append([e.pos().x(),e.pos().y()])
        painter = QPainter(self.label.pixmap())
        painter.setPen(QPen(Qt.red, 3, Qt.SolidLine))
        painter.drawPoint(e.pos())
        self.update()
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()