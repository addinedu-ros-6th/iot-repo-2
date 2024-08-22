import serial
import struct
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
import PyQt5
import time
import numpy as np
import datetime

from_class =  uic.loadUiType("./IOT_Project_2/GUI/GUI_v5.ui")[0]

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    PyQt5.QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    PyQt5.QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # self.conn = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
        self.conn = serial.Serial(port='com3', baudrate=9600, timeout=1)
        self.recv = Receiver(self.conn)
        self.recv.doorActionExecuted.connect(self.onDoorActionExecuted)
        self.recv.start()
        
        self.controlBtn_Blind_toggle.clicked.connect(self.control_Blind_toggle)
        self.controlBtn_Blind_toggle.setText('Open')
        self.controlBtn_Blind_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")
    
    def control_Blind_toggle(self):
        if self.controlBtn_Blind_toggle.text() == 'Open':
            self.controlBtn_Blind_toggle.setText('Close')
            self.controlBtn_Blind_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
            self.sendBinary(b'SBM', 0) # 0을 보내면 블라인드를 닫기
        else:
            self.controlBtn_Blind_toggle.setText('Open')
            self.controlBtn_Blind_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")
            self.sendBinary(b'SBM', 1) # 1을 보내면 블라인드를 열기

    def sendBinary(self, command, data=0):
        if command == b'SBM':
            req_data = struct.pack('<3sB', command, data) + b'\n'
            print("sendBinary: ", req_data)
            self.conn.write(req_data)
        return

    def onDoorActionExecuted(self, message):
        print(message)  # "Door opened" 또는 "Door closed" 메시지를 출력
    
class Receiver(QThread):
    doorActionExecuted = pyqtSignal(str)  # 문이 열리거나 닫혔을 때의 신호

    def __init__(self, conn, parent=None):
        super(Receiver, self).__init__(parent)
        self.is_running = False
        self.conn = conn

    def run(self):
        self.is_running = True
        while self.is_running:
            if self.conn.readable():
                res = self.conn.read_until(b'\n') # 개행 문자가 나올 때까지 데이터 수신
                if len(res) > 0:
                    res = res.decode().strip()  # 수신된 데이터를 디코딩하고 공백 제거
                    cmd = res[:3]  # 첫 세 문자를 명령으로 인식
                    if cmd == 'SDM':
                        action = int(res[3])  # 네 번째 문자가 동작 값 (0 또는 1)
                        if action == 1:
                            self.doorActionExecuted.emit("Door opened")
                        elif action == 0:
                            self.doorActionExecuted.emit("Door closed")
                    elif cmd == 'SBM':
                        action = int(res[3])
                        if action == 1:
                            self.doorActionExecuted.emit("Blind opened")
                        elif action == 0:
                            self.doorActionExecuted.emit("Blind closed")

    def stop(self):
        self.is_running = False
        self.wait()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    
    sys.exit(app.exec_())
