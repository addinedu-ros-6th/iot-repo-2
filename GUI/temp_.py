import sys
import serial
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
import time
import struct

form_class = uic.loadUiType("GUI_v5.ui")[0]

class Receiver(QThread):
    update_signal = pyqtSignal(float, float)

    def __init__(self, conn,parent= None):
        super().__init__()
        self.is_running = False
        self.conn = conn
    
    def run(self):
        self.is_running = True
        while self.is_running:
            if self.conn.readable():
                res = self.conn.read_until(b'\n')
                if len(res)>0:
                    res = res.decode().strip()
                    cmd = res[:3]
                    if cmd == 'SAC' :
                        action = int(res[3])
                        if action == 0:
                            self.AC_status.emit("AC OFF")

                        elif action == 1 :
                            self.AC_status.emit("AC ON")
        

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.conn = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
        
        self.recv = Receiver(self.conn)
        self.recv.update_signal.connect(self.update_sensor_data)
        self.recv.start()

        self.controlBtn_AC_toggle.clicked.connect(self.control_AC_toggle)
        self.controlBtn_AC_toggle.setText('OFF')

        # while True:
        #     try:
        #         self.serial_port.write(b'GTH\n')
        #         response = self.serial_port.readline().decode().strip()
        #         humidity, temperature = map(float, response.split(','))
        #         self.update_signal.emit(humidity, temperature)
        #     except Exception as e:
        #         print(f"Error reading sensor data: {e}")

    def control_AC_toggle(self):
        if self.controlBtn_AC_toggle.text() == 'OFF' :
            self.controlBtn_AC_toggle.setText('ON')
            self.sendBinary(b'SAC',1) #ac on하기
        else :
            self.controlBtn_AC_toggle.setText('OFF')
            self.sendBinary(b'SAC',0) #ac off 하기

    def sendBinary(self, command, data=0):
        if command == b'SAC':
            req_data=struct.pack('<3sB',command,data)+b'\n'
            print("sendBinary:",req_data)
            self.conn.write(req_data)
        return
    
    def AC_stauts(self,message) :
        print(message)
    
    
    def update_sensor_data(self, humidity, temperature):
        self.lcdHumidity.display(humidity)
        self.lcdTemp.display(temperature)
    
    

    def closeEvent(self, event):
        self.sensor_thread.terminate()
        self.sensor_thread.wait()
        self.conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    sys.exit(app.exec_())