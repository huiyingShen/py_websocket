from webSocketServerClient import launchServer,getClient
from audio_drawing import PozClient

from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox
from PyQt5.QtGui import QPixmap
import sys, csv
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
from time import time,sleep
from datetime import datetime
import threading
from os import rename

# adapted from https://gist.github.com/docPhil99/ca4da12c9d6f29b9cea137b617c7b8b1


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self, receiver, map_filename):
        super().__init__()
        self.run_flag = True
        self.change_map_flag = True
        self.receiver = receiver
        self.map_filename = map_filename
        self.pozClient = PozClient(map_filename)
        self.log_header = []
        self.log_filename = ""
        self.log_flag = "wait"

    def run(self):
        self.run_flag = True
        # capture from web cam
        cap = None
        csvwriter = None
        # cap = cv2.VideoCapture(0)
        i = 0
        while self.run_flag:
            if self.change_map_flag or 'map' not in locals():
                fn = self.map_filename
                map = cv2.imread(fn)
                print(f'Change map to {self.map_filename}')
                self.change_map_flag = False
                self.pozClient.update_map(fn)
            if self.log_flag == "stop":
                if self.logfile is not None:
                    self.logfile.close()
                    print(f"Closing file: {self.log_filename}")
                    self.logfile = None
                else:
                    print("Warning, no log file to close.")
                self.log_flag = "wait"
                self.pozClient.mute_tone()
            if self.log_flag == "abort":
                if self.logfile is not None:
                    self.logfile.close()
                    rename(self.log_filename, self.log_filename+'.abort')
                    print(f"Closing file: {self.log_filename+'.abort'}")
                    self.logfile = None
                self.log_flag = "wait"
                self.pozClient.mute_tone()
            if self.log_flag == "new":
                print(f"Writing to file: {self.log_filename}")
                self.logfile = open(self.log_filename, 'w', newline='')
                for header_line in self.log_header:
                    self.logfile.write(header_line)
                csvwriter = csv.writer(self.logfile, delimiter=',')
                self.log_flag = "write"
                self.pozClient.unmute_tone()

            ret = True
            if cap is not None: ret, cv_img = cap.read()
            else: cv_img = map.copy()

            if ret:
                txt = self.receiver.recv().split()
                #print(txt)
                if len(txt) == 9:
                    try:
                        if self.log_flag == "write":
                            csvwriter.writerow(txt[2:])
                        # previous version expected x,y,theta = txt[2],txt[3],-txt[4],time
                        # current expects x,y,z,angle0,-theta,angle2,time
                        # txt = txt[2] +', ' + txt[3]
                        xf = float(txt[2])*100 + 300
                        yf = 300 - float(txt[3])*100
            
                        theta = -float(txt[6])
                        i += 1
                        cv_img = self.pozClient.oneStep(xf,yf,theta,i)
                    except: 
                        pass
                elif self.log_flag != "write":
                    txt = 'Waiting for data stream...'
                    thickness=2
                    size=1
                    cv2.putText(cv_img, txt, (25,100), cv2.FONT_HERSHEY_SIMPLEX, size, (0,0,255), thickness)
                self.change_pixmap_signal.emit(cv_img)
        # shut down capture system
        if cap is not None: cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self.end_log()
        sleep(.05)
        self.run_flag = False
        sleep(.1)
        del self.pozClient
        #self.wait()

    def change_map(self, map_filename):
        if self.map_filename != map_filename:
            self.map_filename = map_filename
            self.change_map_flag = True
            #self.stop()
            #self.pozClient.update_map(map_filename)
            #self.run()

    def start_log(self, header):
        timestamp_string = datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
        self.log_filename = "logs/" + timestamp_string + "_log.csv"
        # Only create a new log file from a "wait" state
        if self.log_flag == "wait":
            self.log_flag = "new"
            header_row = "X,Y,Z,angle0,Theta,angle2,Timestamp"
            null_row   = f"0,0,0,0,0,0,0"
            for title, entry in header.items():
                header_row += f",{title}"
                null_row   += f",{entry}"
            self.log_header.clear()
            self.log_header.append(header_row + "\n")
            self.log_header.append(null_row   + "\n")
        else:
            print("Warning, already logging")

    def end_log(self):
        self.log_flag = "stop"

    def abort_log(self):
        self.log_flag = "abort"


class App(QWidget):
    def __init__(self, port=8001, launchSender = False):
        self._run_flag = True
        self._sim_flag = False
        self.available_maps = ["image00.png",
                               "image01.png",
                               "image02.png"]
        self.map_filename = self.available_maps[0]
        super().__init__()

        # Time ping sending thread if launchSender == True
        def sending(web_socket_client, sleep_time=.1):
            while self._run_flag is True:
                web_socket_client.send(f"time = {time()}")
                # print("sending...")
                sleep(sleep_time)

        def iPhone_simulator(web_socket_client, fps=30):
            start_flag = False
            while self._sim_flag is True:
                web_socket_client.send("iPhoneMessage")
                sleep(1/fps)

        self.server = launchServer(port=port)
        self.receiver = getClient(port=port)
        if launchSender:
            sender = getClient(port=port)
            threading.Thread(target=sending, name='Time Ping Sender', args=(sender,.1,)).start()

        self.setWindowTitle("iVEERS controller")
        # self.display_width = 640
        # self.display_height = 480 
        self.display_width = 600
        self.display_height = 600
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.display_width, self.display_height)
        # create a text label
        self.textLabel = QLabel('iVEERS')
        # create the buttons
        self.btnStart = QPushButton('START', self)
        self.btnStart.setEnabled(True)
        self.btnStop  = QPushButton('STOP and SAVE ', self)
        self.btnStop.setEnabled(False)
        self.btnAbort = QPushButton('ABORT', self)
        self.btnAbort.setEnabled(False)

        # create the layout
        interface_box = QVBoxLayout()
        interface_box.addWidget(self.image_label)

        # Controls
        control_box = QHBoxLayout()
        control_box.addWidget(self.btnStart)
        control_box.addWidget(self.btnStop)
        control_box.addWidget(self.btnAbort)
        interface_box.addLayout(control_box)

        # Selectors
        self.selector_box = QVBoxLayout()
        self.selector_list = []
        # Map Interface
        self.comboMap = QComboBox(self)
        for map_file in self.available_maps:
            self.comboMap.addItem(map_file)
        map_box = QHBoxLayout()
        map_box.addWidget(QLabel("Session Type:"))
        map_box.addWidget(self.comboMap)
        self.selector_box.addLayout(map_box)
        self.selector_list.append(self.comboMap)
        # Participants
        self.comboParticipant = QComboBox(self)
        for participant in range(10):
            self.comboParticipant.addItem(f"BN{participant:03d}")
        self.comboParticipant.setEditable(True)
        participant_box = QHBoxLayout()
        participant_box.addWidget(QLabel("Participant ID:"))
        participant_box.addWidget(self.comboParticipant)
        self.selector_box.addLayout(participant_box)
        self.selector_list.append(self.comboParticipant)
        # Task
        self.comboTask = QComboBox(self)
        for task in range(10):
            self.comboTask.addItem(f"{task:02d}")
        task_box = QHBoxLayout()
        task_box.addWidget(QLabel("Task ID:"))
        task_box.addWidget(self.comboTask)
        self.selector_box.addLayout(task_box)
        self.selector_list.append(self.comboTask)
        # Session Type
        self.comboType = QComboBox(self)
        for type in ["Familiarization", "Pre", "Post-1", "Post-2", "Post-3"]:
            self.comboType.addItem(type)
        type_box = QHBoxLayout()
        type_box.addWidget(QLabel("Session Type:"))
        type_box.addWidget(self.comboType)
        self.selector_box.addLayout(type_box)
        self.selector_list.append(self.comboType)

        interface_box.addLayout(self.selector_box)
        interface_box.addWidget(self.textLabel)
        # set the interface_box layout as the widgets layout
        self.setLayout(interface_box)

        # Connect the button clicks with their respective actions
        self.btnStart.clicked.connect(self.onStart)
        self.btnStop.clicked.connect(self.onStop)
        self.btnAbort.clicked.connect(self.onAbort)
        self.comboParticipant.activated.connect(self.selectParticipant)
        self.comboMap.activated.connect(self.selectMap)

        # create the video capture thread
        self.thread = VideoThread(self.receiver, self.map_filename)
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()

    @pyqtSlot()
    def onStart(self):
        log_header = {"ParticipantID": self.comboParticipant.currentText(),
                      "MapID": self.map_filename,
                      "TaskID": self.comboTask.currentText(),
                      "SessionType": self.comboType.currentText(),
                      "Date": f'{datetime.now():%Y-%m-%d}',
                      "Time": f'{datetime.now():%H:%M:%S}'}
        self.thread.start_log(log_header)
        print('Sending START,...')
        self.receiver.send("START")
        # Enable and Disable GUI for state control
        self.btnStart.setEnabled(False)
        self.btnStop.setEnabled(True)
        self.btnAbort.setEnabled(True)
        for sel in self.selector_list:
            sel.setEnabled(False)
    @pyqtSlot()
    def onStop(self):
        self.thread.end_log()
        print('Sending STOP,...')
        self.receiver.send("STOP")
        # Enable and Disable GUI for state control
        self.btnStart.setEnabled(True)
        self.btnStop.setEnabled(False)
        self.btnAbort.setEnabled(False)
        for sel in self.selector_list:
            sel.setEnabled(True)
    @pyqtSlot()
    def onAbort(self):
        self.thread.abort_log()
        self.receiver.send("STOP")
        # Enable and Disable GUI for state control
        self.btnStart.setEnabled(True)
        self.btnStop.setEnabled(False)
        self.btnAbort.setEnabled(False)
        for sel in self.selector_list:
            sel.setEnabled(True)
    @pyqtSlot()
    def selectParticipant(self):
        print(f'Selected {self.comboParticipant.currentText()} as the participant.')
    @pyqtSlot()
    def selectMap(self):
        map_index = self.comboMap.currentIndex()
        print(f'Map {map_index+1} selected')
        self.receiver.send(f'MAP {map_index+1}')
        self.map_filename = self.available_maps[map_index]
        self.thread.change_map(self.map_filename)

    def closeEvent(self, event):
        self.server.stop()
        self._run_flag = False
        self.thread.stop()
        event.accept()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    
if __name__=="__main__":
    app = QApplication(sys.argv)
    a = App(launchSender = True)
    a.show()
    execid = app.exec_()
    sys.exit(execid)

