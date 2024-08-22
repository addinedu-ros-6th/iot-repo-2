import sys
import serial
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import struct
import time

form_class = uic.loadUiType("GUI_v6.ui")[0]

class Receiver(QThread):
    update_signal = pyqtSignal(float, float)
    ac_status_signal = pyqtSignal(str)

    def __init__(self, sensor_conn, ac_conn, parent=None):
        super().__init__()
        self.is_running = False
        self.sensor_conn = sensor_conn  # 센서 Arduino
        self.ac_conn = ac_conn  # 에어컨 Arduino
    
    def run(self):
        self.is_running = True
        while self.is_running:
            if self.sensor_conn.in_waiting:
                res = self.sensor_conn.readline().decode().strip()
                if res.startswith("GTH"):
                    _, data = res.split("GTH")
                    humidity, temperature = map(float, data.split(","))
                    self.update_signal.emit(humidity, temperature)
            
            if self.ac_conn.in_waiting:
                res = self.ac_conn.readline().decode().strip()
                if res.startswith("AC"):
                    self.ac_status_signal.emit(res)

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.sensor_conn = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
        self.ac_conn = serial.Serial(port='/dev/ttyACM1', baudrate=9600, timeout=1)
        self.indoorMode = False
        self.outdoorMode = False
        
        self.recv = Receiver(self.sensor_conn, self.ac_conn)
        self.recv.update_signal.connect(self.update_sensor_data)
        self.recv.ac_status_signal.connect(self.update_ac_status)
        self.recv.start()

        self.controlBtn_AC_toggle.clicked.connect(self.control_AC_toggle)
        self.controlBtn_AC_toggle.setText('OFF')

        # 초기 센서값 요청
        QTimer.singleShot(100, self.send_gth_command)  # 100ms 후 첫 번째 요청

        # 30초마다 GTH 명령을 보내는 타이머 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.send_gth_command)
        self.timer.start(30000)  # 30초

    def send_gth_command(self):
        self.sensor_conn.write(b'GTH\n')
        print("Sent GTH command")  # 디버깅을 위한 출력

    def control_AC_toggle(self):
        if self.controlBtn_AC_toggle.text() == 'OFF':
            # self.controlBtn_AC_toggle.setText('ON')
            self.sendAC(b'SAC', 1)  # AC ON
        else:
            # self.controlBtn_AC_toggle.setText('OFF')
            self.sendAC(b'SAC', 0)  # AC OFF

    def sendAC(self,command, data=0):
        req_data = struct.pack('<3sB', command, data) + b'\n'
        self.ac_conn.write(req_data)

    def update_ac_status(self, message):
        print(message)
        if message == "AC ON":
            self.controlBtn_AC_toggle.setText('ON')
        elif message == "AC OFF":
            self.controlBtn_AC_toggle.setText('OFF')
    
    def update_sensor_data(self, humidity, temperature):
        self.lcdHumidity.display(humidity)
        self.lcdTemp.display(temperature)
        print(f"Updated sensor data: Humidity={humidity}, Temperature={temperature}")  # 디버깅을 위한 출력
    
    def closeEvent(self, event):
        self.recv.is_running = False
        self.recv.wait()
        self.sensor_conn.close()
        self.ac_conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    sys.exit(app.exec_())