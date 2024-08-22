import sys
import serial
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import time
import struct

form_class = uic.loadUiType("GUI_v7.ui")[0]

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

        # outdoor mode
        self.Current_mode.setText("Outdoor")
        ACDefault = "15" 
        self.controlLine_Heater.setText("0")
        self.OutdoorLine_Timer.setText("0")
        self.OutdoorLine_Duration.setText("30")

        self.controlBtn_AC_toggle.clicked.connect(self.control_AC_toggle)
        self.controlBtn_AC_toggle.setText('OFF')
        self.controlBtn_AC_toggle.setStyleSheet("background-color: red")

        self.OutdoorLine_AC.setText(ACDefault)
        
        self.OutdoorSaveConfig()
        self.OutdoorBtn_Saveconfig.clicked.connect(self.OutdoorSaveConfig)
        self.OutdoorBtn_AC_decrease.clicked.connect(self.OutdoorACDec)
        self.OutdoorBtn_AC_increase.clicked.connect(self.OutdoorACInc)
        self.pushButton.clicked.connect(self.TestChangeMode)
        # self.Current_mode.textChanged.connect(self.ExecuteMode)

        # AC제어
        self.ac_on = False
        self.simulated_temperature = None
        self.last_real_temperature = None
        self.set_temperature = float(self.controlLine_AC.text())

        QTimer.singleShot(100, self.send_gth_command)
        
        self.gth_timer = QTimer(self)
        self.gth_timer.timeout.connect(self.send_gth_command)
        self.gth_timer.start(5000)  # 5초마다 GTH 명령 전송

        self.temp_timer = QTimer(self)
        self.temp_timer.timeout.connect(self.update_temperature)
        self.temp_timer.start(5000)  # 5초마다 온도 업데이트

    def OutdoorACInc(self):
        self.OutdoorACSetting = int(self.OutdoorLine_AC.text())
        self.OutdoorACSetting += 1
        self.OutdoorLine_AC.setText(str(self.OutdoorACSetting))
        self.set_temperature = float(self.OutdoorLine_AC.text())

    def OutdoorACDec(self):
        self.OutdoorACSetting = int(self.OutdoorLine_AC.text())
        self.OutdoorACSetting -= 1
        self.OutdoorLine_AC.setText(str(self.OutdoorACSetting))
        self.set_temperature = float(self.OutdoorLine_AC.text())
        
    def OutdoorSaveConfig(self):
        self.OutdoorACAuto = self.OutdoorCheck_AC_auto.isChecked()
        self.OutdoorTimerAuto = self.OutdoorCheck_Time_auto.isChecked()
        self.OutdoorDurationAuto = self.OutdoorCheck_Duration_auto.isChecked()

        self.OutdoorACSetting = int(self.OutdoorLine_AC.text())
        self.OutdoorTimer = int(self.OutdoorLine_Timer.text())
        self.OutdoorDuration = int(self.OutdoorLine_Duration.text())

        if self.Current_mode.text() == "Outdoor":
            self.controlLine_AC.setText(str(self.OutdoorACSetting))
            self.set_temperature = float(self.controlLine_AC.text())
            
            if self.OutdoorACAuto:
                self.controlBtn_AC_toggle.setDisabled(True)
            else:
                self.controlBtn_AC_toggle.setEnabled(True)

    def TestChangeMode(self):
        if self.Current_mode.text() == "Indoor":
            self.Current_mode.setText("Outdoor")
        elif self.Current_mode.text() == "Outdoor":
            self.Current_mode.setText("Indoor")
    
    # def ExecuteMode(self):
    #     if self.Current_mode.text() == "Outdoor":
    #         self.OutdoorHeater()
            
    def send_gth_command(self):
        self.sensor_conn.write(b'GTH\n')
        print("Sent GTH command")

    def control_AC_toggle(self):
        if self.controlBtn_AC_toggle.text() == 'OFF':
            if self.last_real_temperature is not None:
                self.simulated_temperature = self.last_real_temperature
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
                self.simulated_temperature = self.last_real_temperature
        elif message == "AC OFF":
            self.controlBtn_AC_toggle.setText('OFF')
            self.ac_on = False
    
    def update_sensor_data(self, humidity, temperature):
        self.lcdHumidity.display(humidity)
        self.last_real_temperature = temperature
        
        if self.simulated_temperature is None:
            self.simulated_temperature = temperature

        if not self.ac_on:
            self.simulated_temperature = temperature

        self.lcdTemp.display(self.simulated_temperature)
        print(f"Updated sensor data: Humidity={humidity}, Temperature={self.simulated_temperature}")
    
    def update_temperature(self):
        if self.ac_on and self.simulated_temperature is not None:
            temp_diff = self.set_temperature - self.simulated_temperature
            
            if temp_diff > 2 or self.controlBtn_AC_toggle.text() == 'ON':
                self.simulated_temperature = max(18.0, self.simulated_temperature - 1.0)
                self.sendAC(b'SAC', 1)  # POWER
                
            elif 1 < temp_diff <= 2:
                self.simulated_temperature = max(18.0, self.simulated_temperature - 0.6)
                self.sendAC(b'SAC', 2)  # HIGH
               
            elif 0 < temp_diff <= 1:
                self.simulated_temperature = max(18.0, self.simulated_temperature - 0.2)
                self.sendAC(b'SAC', 3)  # MIDDLE
                
            elif temp_diff == 0:
                self.sendAC(b'SAC', 4)  # LOW
                
            else:
                self.simulated_temperature = min(self.last_real_temperature, self.simulated_temperature + 1.0)
                if self.simulated_temperature == self.last_real_temperature:
                    self.sendAC(b'SAC', 0)  # OFF
                    self.ac_on = False
                    self.controlBtn_AC_toggle.setText('OFF')
                    self.controlBtn_AC_toggle.setStyleSheet("background-color: red")

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