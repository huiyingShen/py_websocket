import sys
# import rel

from PyQt5.QtCore import Qt,QRect
from PyQt5.QtGui import QPainter,QPixmap,QPen,QTransform,QFont
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton,QLineEdit,QFileDialog,QScrollArea

import threading


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.img_label = QLabel(self)
        self.img_label.setGeometry(0, 0, 400, 300)
        self.scale = 1.0
        self.transform = QTransform().scale(self.scale,self.scale)
        self.fn = "market_smaller.jpg"
        self.image = QPixmap(self.fn).transformed(self.transform)

        self.img_label.setPixmap(self.image)
        self.img_label.resize(self.image.width(), self.image.height())

        self.setFixedSize(self.image.width(), self.image.height()+50)

        w,h = 150,40
        x,y = 5,self.image.height()+5
        self.xywh = x,y,w,h
        self.setWidgets(x,y,w,h)
    
        self.labeled_data = [(self.fn,self.scale),]
        self.pnts = []

    def setWidgets(self,x,y,w,h):
        self.setTextBox(x,y,w,h)
        x += w + 10
        self.addButton(x,y,w,h,"Save Landmark", self.saveLandmark)
        x += w + 10
        self.addButton(x,y,w,h,"Save Data", self.saveData)
        x += w + 10
        self.addButton(x,y,w,h,"New Image", self.getFile)
        x += w + 10
        self.fn_lbl = self.addLabel(x,y,w,h,self.fn)


    def getFile(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file','.',"Image files (*.jpg *.png)")[0]
        # print('fname = ',fname)
        if fname == '': return #file open canceled
        self.fn = fname.split('/')[-1]
        self.loadImage()

    def loadImage(self):
        self.image = QPixmap(self.fn).transformed(self.transform)
        self.img_label.setPixmap(self.image)
        self.fn_lbl.setText(self.fn)
        print(self.fn)

    def setTextBox(self,x,y,w,h):
        # Create textbox
        self.textbox = QLineEdit(self)
        self.textbox.move(x,y)
        self.textbox.resize(w,h)

    def addLabel(self,x,y,w,h,txt):
        lbl = QLabel(self)
        lbl.setGeometry(x, y, w, h)
        lbl.setText(txt)
        return lbl

    def addButton(self,x,y,w,h,title,fn):
        btn = QPushButton(title,self)
        btn.setFont(QFont("Helvetica [Cronyx]", 16))  
        btn.clicked.connect(fn)
        btn.setGeometry(x, y, w, h)

    def saveLandmark(self):
        print("save landmark():")
        polyline = []
        for x,y in self.pnts:
            tmp = '{:.1f} {:.1f}'.format(x/self.scale, y/self.scale)
            polyline.append((x/self.scale, y/self.scale))
            print(tmp)
        self.labeled_data.append((self.textbox.text(),polyline))
        self.textbox.clear()
        self.pnts = []
        self.loadImage()
        self.drawPolylines()

    def saveData(self):
        print(self.labeled_data[0][0])
        for l in self.labeled_data[1:]:
            nm,dat = l
            line = nm + ': '
            for x,y in dat:
                line += '{:.1f},{:.1f} '.format(x/self.scale, y/self.scale)
            print(line)
            


    def drawPolylines(self):
        painter = QPainter(self.img_label.pixmap())
        painter.setPen(QPen(Qt.green, 3, Qt.SolidLine))
        painter.setFont(QFont("Helvetica [Cronyx]",24))
        for dat in self.labeled_data[1:]:
            name , polyline = dat
            x,y = polyline[0]
            painter.drawText(int(x*self.scale),int(y*self.scale), name)
            self.draw1Polyline(painter,polyline)
        rect = QRect(100,150, 250,25)
        # painter.drawRect(rect)
        # painter.drawText(rect, Qt.AlignCenter, "Hello World")

    def draw1Polyline(self,painter,polyline):
        x1,y1 = polyline[0]
        for x2,y2 in polyline[1:]:
            painter.drawLine(int(x1*self.scale),int(y1*self.scale),int(x2*self.scale),int(y2*self.scale))
            x1,y1 = x2,y2

    def mousePressEvent(self, e):
        print(e.pos().x(),e.pos().y())
        # self.pnts += '\n{} {}'.format(e.pos().x(),e.pos().y())
        self.pnts.append([e.pos().x(),e.pos().y()])
        painter = QPainter(self.img_label.pixmap())
        painter.setPen(QPen(Qt.red, 3, Qt.SolidLine))
        painter.drawPoint(e.pos())
        self.update()
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()