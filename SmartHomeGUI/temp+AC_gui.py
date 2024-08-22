import sys
import serial
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import time
import struct

form_class = uic.loadUiType("GUI_v6.ui")[0]

class Receiver(QThread):
    update_signal = pyqtSignal(float, float)
    ac_status_signal = pyqtSignal(str)

    def __init__(self, sensor_conn, ac_conn, parent=None):
        super().__init__()
        self.is_running = False
        self.sensor_conn = sensor_conn
        self.ac_conn = ac_conn
    
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
                print(f"Received from AC Arduino: {res}")
                if res.startswith("AC"):
                    self.ac_status_signal.emit(res)

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.sensor_conn = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
        self.ac_conn = serial.Serial(port='/dev/ttyACM1', baudrate=9600, timeout=1)
        time.sleep(2)  # Arduino 재시작을 위한 대기 시간
        
        self.recv = Receiver(self.sensor_conn, self.ac_conn)
        self.recv.update_signal.connect(self.update_sensor_data)
        self.recv.ac_status_signal.connect(self.update_ac_status)
        self.recv.start()

        self.controlBtn_AC_toggle.clicked.connect(self.control_AC_toggle)
        self.controlBtn_AC_toggle.setText('OFF')

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
        self.sensor_conn.write(b'GTH\n')
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
            bytes_written = self.ac_conn.write(req_data)
            print(f"Bytes written: {bytes_written}")
            self.ac_conn.flush()
            print("Data flushed")
            
            time.sleep(0.1)
            if self.ac_conn.in_waiting:
                response = self.ac_conn.readline().decode().strip()
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