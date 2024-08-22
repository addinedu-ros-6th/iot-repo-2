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

from_class =  uic.loadUiType("./IOT_Project_2/GUI/GUI_v7.ui")[0]

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    PyQt5.QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    PyQt5.QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connEnv = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
        # self.connHeater = serial.Serial(port='/dev/ttyACM1', baudrate=9600, timeout=1)
        self.connDevice = serial.Serial(port='/dev/ttyACM2', baudrate=9600, timeout=1)
        
        self.recv = Receiver(self.connEnv, self.connDevice)
        self.recv.update_signal.connect(self.update_sensor_data)
        self.recv.ac_status_signal.connect(self.update_ac_status)
        self.recv.start()

        self.controlBtn_AC_toggle.clicked.connect(self.control_AC_toggle)
        self.controlBtn_AC_toggle.setText('OFF')
        self.controlBtn_AC_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
        self.controlBtn_Heater_toggle.clicked.connect(self.MainHeaterPwrBtn)
        self.controlBtn_Heater_toggle.setText("OFF")
        self.controlBtn_Heater_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
        self.controlBtn_Dehum_toggle.clicked.connect(self.control_Dehum_toggle)
        self.controlBtn_Dehum_toggle.setText('OFF')
        self.controlBtn_Dehum_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
        self.controlBtn_Light_toggle.clicked.connect(self.control_Light_toggle)
        self.controlBtn_Light_toggle.setText('OFF')
        self.controlBtn_Light_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
        self.controlBtn_Blind_toggle.clicked.connect(self.control_Blind_toggle)
        self.controlBtn_Blind_toggle.setText('Open')
        self.controlBtn_Blind_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")
        self.controlBtn_Door_toggle.clicked.connect(self.control_Door_toggle)
        self.controlBtn_Door_toggle.setText('Open')
        self.controlBtn_Door_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")

        self.ac_on = False
        self.simulated_temperature = None  # 초기값을 None으로 설정
        self.last_real_temperature = None  # 마지막으로 받은 실제 온도 저장

        QTimer.singleShot(100, self.send_gth_command)
        
        self.gth_timer = QTimer(self)
        self.gth_timer.timeout.connect(self.send_gth_command)
        self.gth_timer.start(30000)  # 30초마다 GTH 명령 전송

        self.temp_timer = QTimer(self)
        self.temp_timer.timeout.connect(self.update_temperature)
        self.temp_timer.start(30000)  # 30초마다 온도 업데이트

    def send_gth_command(self):
        self.connEnv.write(b'GTH\n')
        print("Sent GTH command")
    
    def control_AC_toggle(self):
        if self.controlBtn_AC_toggle.text() == 'OFF':
            if self.last_real_temperature is not None:
                self.simulated_temperature = self.last_real_temperature  # AC를 켤 때 마지막 실제 온도로 초기화
            self.sendAC(b'SAC', 1)  # AC POWER
            self.ac_on = True
        else:
            self.sendAC(b'SAC', 0)  # AC OFF
            self.ac_on = False

    def sendAC(self, command, data):
        req_data = struct.pack('<3sB', command, data) + b'\n'
        print(f"Sending to AC Arduino: {req_data}")
        try:
            bytes_written = self.connDevice.write(req_data)
            print(f"Bytes written: {bytes_written}")
            self.connDevice.flush()
            print("Data flushed")
            
            time.sleep(0.1)
            if self.connDevice.in_waiting:
                response = self.connDevice.readline().decode().strip()
                print(f"Response from AC Arduino: {response}")
            else:
                print("No immediate response from AC Arduino")
        except Exception as e:
            print(f"Error in sendBinary: {e}")

    def update_ac_status(self, message):
        print(f"Updating AC status: {message}")
        if message == "AC ON":
            self.controlBtn_AC_toggle.setText('ON')
            self.ac_on = True
            if self.last_real_temperature is not None:
                self.simulated_temperature = self.last_real_temperature  # AC를 켤 때 마지막 실제 온도로 초기화
        elif message == "AC OFF":
            self.controlBtn_AC_toggle.setText('OFF')
            self.acIT_on = False
            
    def update_sensor_data(self, humidity, temperature):
        self.lcdHumidity.display(humidity)
        self.last_real_temperature = temperature  # 실제 온도 저장
        
        if self.simulated_temperature is None:
            self.simulated_temperature = temperature  # 첫 번째 온도 데이터로 초기화

        if not self.ac_on:
            self.simulated_temperature = temperature  # AC가 꺼져 있을 때 실제 온도로 업데이트

        self.lcdTemp.display(self.simulated_temperature)
        print(f"Updated sensor data: Humidity={humidity}, Temperature={self.simulated_temperature}")

    def update_temperature(self):
        if self.ac_on and self.simulated_temperature is not None:
            self.simulated_temperature = max(18.0, self.simulated_temperature - 1.0)  # 최소 온도를 18도로 제한
            self.lcdTemp.display(self.simulated_temperature)
            print(f"Updated simulated temperature: {self.simulated_temperature}")

    def MainHeaterPwrBtn(self):
        if self.controlBtn_Heater_toggle.text() == "ON":
            self.controlBtn_Heater_toggle.setText("OFF")
            self.controlBtn_Heater_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
            self.HeaterManual = 0
        elif self.controlBtn_Heater_toggle.text() == "OFF":
            self.controlBtn_Heater_toggle.setText("ON")
            self.controlBtn_Heater_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")
            self.HeaterManual = 1

    def control_Dehum_toggle(self):
        if self.controlBtn_Dehum_toggle.text() == 'ON':
            self.controlBtn_Dehum_toggle.setText('OFF')
            self.controlBtn_Dehum_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
            # self.sendByte(b'SHM', 0) # 0을 보내면 문을 닫기
        else:
            self.controlBtn_Dehum_toggle.setText('ON')
            self.controlBtn_Dehum_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")
            # self.sendByte(b'SHM', 1) # 1을 보내면 문을 열기
        return
    
    def control_Light_toggle(self):
        if self.controlBtn_Light_toggle.text() == 'ON':
            self.controlBtn_Light_toggle.setText('OFF')
            self.controlBtn_Light_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
            # self.sendByte(b'SLI', 0) # 0을 보내면 불 끄기
        else:
            self.controlBtn_Light_toggle.setText('ON')
            self.controlBtn_Light_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")
            # self.sendByte(b'SLI', 1) # 1을 보내면 불 켜기
    
    def control_Blind_toggle(self):
        if self.controlBtn_Blind_toggle.text() == 'Open':
            self.controlBtn_Blind_toggle.setText('Close')
            self.controlBtn_Blind_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
            # self.sendByte(b'SBM', 0) # 0을 보내면 블라인드 닫기
        else:
            self.controlBtn_Blind_toggle.setText('Open')
            self.controlBtn_Blind_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")
            # self.sendByte(b'SBM', 1) # 1을 보내면 블라인드 열기
    
    def control_Door_toggle(self):
        if self.controlBtn_Door_toggle.text() == 'Open':
            self.controlBtn_Door_toggle.setText('Close')
            self.controlBtn_Door_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
            # self.sendByte(b'SDM', 0) # 0을 보내면 문 닫기
        else:
            self.controlBtn_Door_toggle.setText('Open')
            self.controlBtn_Door_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")
            # self.sendByte(b'SDM', 1) # 1을 보내면 문 열기
        return

    def sendByte(self, command, data=0):
        if command in [b'SAC', b'SHM', b'SLI', b'SBM', b'SDM']:
            req_data = struct.pack('<3sB', command, data) + b'\n'
            print("sendByte: ", req_data)
            self.connEnv.write(req_data)
        return
    
    def update_sensor_data(self, humidity, temperature):
        self.lcdHumidity.display(humidity)
        self.last_real_temperature = temperature  # 실제 온도 저장
        
        if self.simulated_temperature is None:
            self.simulated_temperature = temperature  # 첫 번째 온도 데이터로 초기화

        if not self.ac_on:
            self.simulated_temperature = temperature  # AC가 꺼져 있을 때 실제 온도로 업데이트

        self.lcdTemp.display(self.simulated_temperature)
        print(f"Updated sensor data: Humidity={humidity}, Temperature={self.simulated_temperature}")
    
class Receiver(QThread):
    update_signal = pyqtSignal(float, float)
    ac_status_signal = pyqtSignal(str)

    def __init__(self, connEnv, connDevice, parent=None):
        super(Receiver, self).__init__(parent)
        self.is_running = False
        self.connEnv = connEnv
        self.connDevice = connDevice

    def run(self):
        self.is_running = True
        while self.is_running:
            if self.connEnv.readable():
                res = self.connEnv.read_until(b'\n') # 개행 문자가 나올 때까지 데이터 수신
                if len(res) > 0:
                    res = res.decode().strip()  # 수신된 데이터를 디코딩하고 공백 제거
                    cmd = res[:3]  # 첫 세 문자를 명령으로 인식
                    if cmd == 'GTH':
                        _, data = res.split("GTH")
                        humidity, temperature = map(float, data.split(","))
                        self.update_signal.emit(humidity, temperature)
                        
            if self.connDevice.in_waiting:
                res = self.connDevice.readline().decode().strip()
                print(f"Received from AC Arduino: {res}")
                if res.startswith("AC"):
                    self.ac_status_signal.emit(res)

    def stop(self):
        self.is_running = False
        self.wait()
        self.connEnv.close()
        self.connDevice.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    
    sys.exit(app.exec_())
