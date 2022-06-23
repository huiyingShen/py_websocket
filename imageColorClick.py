# -*- coding: utf-8 -*-
import sys
from PyQt5.QtCore import Qt, QPoint
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPainter,QPixmap,QPen,QTransform
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel,QPushButton,QHBoxLayout,QVBoxLayout,QWidget

from PIL import ImageQt


class getColorLabel(QLabel):
    def __init__(self, widget):
        super().__init__(widget)
        self.main = widget

    def mousePressEvent(self, event):
        self.main.get(event.pos())
        painter = QPainter(self.main.label.pixmap())
        painter.setPen(QPen(Qt.red, 3, Qt.SolidLine))
        painter.drawPoint(event.pos())


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowTitle('Drop Event Test')

        # Get Position
        self.label = getColorLabel(self)
        self.label.setGeometry(0, 0, 400, 300)
        # transform = QTransform().rotate(-90).scale(1,-1)
        transform = QTransform().rotate(-90)
        self.image = QPixmap("some_image.jpg").transformed(transform)
        # self.image = QPixmap("image00.png")
        self.label.setPixmap(self.image)
        self.label.resize(self.image.width(), self.image.height())
        # self.label.setScaledContents(True)

        # Display
        self.displayLabel = QLabel(self)
        self.displayLabel.setGeometry(self.image.width(), 0, 100, 100)
        self.displayLabel.setStyleSheet('background-color: rgb(255, 255, 255);')

        self.setFixedSize(self.image.width()+100, self.image.height())
        


    def get(self, pos):
        print("pos: ",pos.x(), pos.y())
        index = pos.y()*self.label.size().width()+pos.x()
        image = ImageQt.fromqpixmap(self.label.pixmap())
        image = image.resize((self.label.size().width(), self.label.size().height()))
        image_data = image.getdata()
        r, g, b = image_data[index]
        self.displayLabel.setStyleSheet('background-color: rgb({},{},{});'.format(r, g, b))
        self.update()

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())