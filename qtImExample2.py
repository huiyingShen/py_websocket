import sys
from tkinter import Button
import PyQt5
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel,QPushButton,QHBoxLayout,QVBoxLayout,QWidget


class MyLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setAutoFillBackground(True)
        # p = self.palette()
        # p.setColor(self.backgroundRole(), QColor(223, 230, 248))
        # self.setPalette(p)
        self.setMouseTracking(True)

    # def mouseMoveEvent(self, event):
        # print ("On Hover",event.pos())

    def mousePressEvent(self, event):
        print(event.pos(),self.margin())

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = "Image Viewer"
        self.setWindowTitle(self.title)

        self.button = QPushButton("Press Me!")
        self.button.clicked.connect(self.the_button_was_clicked)

        label =QLabel(self)
        self.label = label
        pixmap = QPixmap('image00.png')
        label.setPixmap(pixmap)
        label.resize(pixmap.width(), pixmap.height())
        label.setScaledContents(True)
        self.im = pixmap

         
        layoutH = QHBoxLayout()
        # Add widgets to the layout
        layoutH.addWidget(QPushButton("Left-Most"))
        layoutH.addWidget(QPushButton("Center"), 1)
        layoutH.addWidget(QPushButton("Right-Most"), 2)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addLayout(layoutH)
        layout.addWidget(self.button)
        self.layout = layout

        container = QWidget()
        container.setLayout(layout)
        self.container = container

        # Set the central widget of the Window.
        self.setCentralWidget(container)
        self.setFixedSize(pixmap.width(), pixmap.height())
        
   
    def mousePressEvent(self, e):
        # print(type(e.pos().x()))
        print(e.pos().x(),e.pos().y())
        print(self.label.pos()) 
        
    def the_button_was_clicked(self):
        print("Clicked.")


app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())