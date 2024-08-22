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

from_class = uic.loadUiType("./IOT_Project_2/GUI/GUI_v7.ui")[0]

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    PyQt5.QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    PyQt5.QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.conn_Env = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
        # self.conn_Env = serial.Serial(port='com4', baudrate=9600, timeout=1)
        self.recv = Receiver(self.conn_Env)
        self.recv.lightSensorValueReceived.connect(self.onLightSensorValueReceived)
        self.recv.start()
        self.count = 0
        self.initTimers()

    def initTimers(self):
        self.sensorTimer = QTimer(self)
        self.sensorTimer.timeout.connect(self.requestLightSensorValue)
        self.sensorTimer.start(500)  # Request every 0.5 seconds (500 ms)

    def requestLightSensorValue(self):
        self.sendBinary(b'GLI', 1)  # Send command to request light sensor value

    def sendBinary(self, command, data=0):
        if command in [b'GLI', b'SLI', b'SBM']:
            req_data = struct.pack('<3sB', command, data) + b'\n'
            self.conn_Env.write(req_data)
        return

    def onLightSensorValueReceived(self, value):
        print(f"Light Sensor Value: {value}")
        print(f"Count: {self.count}")
        
        light_mode = self.IndoorCombo_Light.currentText()
        if light_mode == "LightMode":
            if value <= 10:
                self.count += 1
                if self.count == 10:
                    self.sendBinary(b'SLI', 1)  # Turn on LED
                if self.count > 20:
                    self.count = 20
            else:
                if self.count > 0:
                    self.count -= 1
                if self.count == 0:
                    self.sendBinary(b'SLI', 0)  # Turn off LED
        elif light_mode == "DarkMode":
            if value > 10:
                self.count += 1
                if self.count == 10:
                    self.sendBinary(b'SLI', 0)  # Turn off LED
                if self.count > 20:
                    self.count = 20
            else:
                if self.count > 0:
                    self.count -= 1
                if self.count == 0:
                    self.sendBinary(b'SLI', 1)  # Turn on LED

        blind_mode = self.IndoorCombo_Blind.currentText()
        if blind_mode == "LightMode":
            if value <= 30:
                self.count += 1
                if self.count == 10:
                    self.sendBinary(b'SBM', 1)  # Open blinds
                if self.count > 20:
                    self.count = 20
            else:
                if self.count > 0:
                    self.count -= 1
                if self.count == 0:
                    self.sendBinary(b'SBM', 0)  # Close blinds
        elif blind_mode == "DarkMode":
            if value <= 30:
                self.count += 1
                if self.count == 10:
                    self.sendBinary(b'SBM', 0)  # Close blinds
                if self.count > 20:
                    self.count = 20
            else:
                if self.count > 0:
                    self.count -= 1
                if self.count == 0:
                    self.sendBinary(b'SBM', 1)  # Open blinds

class Receiver(QThread):
    doorActionExecuted = pyqtSignal(str)  # Signal for door actions
    lightSensorValueReceived = pyqtSignal(int)  # Signal for light sensor values

    def __init__(self, conn, parent=None):
        super(Receiver, self).__init__(parent)
        self.is_running = False
        self.conn_Env = conn

    def run(self):
        self.is_running = True
        while self.is_running:
            if self.conn_Env.readable():
                res = self.conn_Env.read_until(b'\n')  # Read data until newline
                if len(res) > 0:
                    res = res.decode().strip()  # Decode and strip whitespace
                    cmd = res[:3]  # First three characters as command
                    if cmd == 'GLI':
                        sensor_value = int(res[3:])  # Extract sensor value
                        self.lightSensorValueReceived.emit(sensor_value)

    def stop(self):
        self.is_running = False
        self.wait()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    
    sys.exit(app.exec_())
