import sys
from PyQt5.QtCore import Qt, QPoint
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPainter,QPixmap,QPen
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel,QPushButton,QHBoxLayout,QVBoxLayout,QWidget


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.image = QPixmap("image00.png")
        self.setGeometry(30,30,600,400)
        self.drawing = False
        self.lastPoint = QPoint()
        self.resize(self.image.width(), self.image.height())
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.image)
 
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()
 
    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.LeftButton and self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(Qt.red, 3, Qt.SolidLine))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()
 
    def mouseReleaseEvent(self, event):
        if event.button == Qt.LeftButton:
            self.drawing = False


def test0():
    app = QtWidgets.QApplication(sys.argv)
    window = MyWidget()
    window.show()
    app.aboutToQuit.connect(app.deleteLater)
    sys.exit(app.exec_())    

if __name__ == '__main__':
    test0()