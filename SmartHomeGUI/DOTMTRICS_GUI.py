import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import serial
import struct
from datetime import datetime, timedelta

from_class = uic.loadUiType("/home/jh/dev_ws/temp_Folder/GUI_v6.ui")[0]
class WindowClass(QMainWindow, from_class) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connHeater = \
            serial.Serial(port='/dev/ttyACM0', baudrate = 9600, timeout = 1)
        
        HeaterDefault = "18"

        self.Current_mode.setText("Testing")

        self.controlBtn_Heater_toggle.setText("OFF")
        self.controlBtn_Heater_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")

        self.OutdoorLine_Heater.setText(HeaterDefault)

        self.controlLine_Heater.setText("0")
        self.controlBtn_Heater_toggle.clicked.connect(self.MainHeaterPwrBtn)

        self.OutdoorBtn_Saveconfig.clicked.connect(self.OutdoorSaveConfig)
        self.OutdoorBtn_Heater_decrease.clicked.connect(self.controlHeaterDec)
        self.OutdoorBtn_Heater_increase.clicked.connect(self.controlHeaterInc)
        self.pushButton.clicked.connect(self.HeaterOpeartion)


    def send(self, command, data = 0):
        print("send")
        req_data = struct.pack('<3sBc', command, data, b'\n')
        self.connHeater.write(req_data)
        print(data)
        return

    def MainHeaterPwrBtn(self):
        self.MainHeaterStatus = self.controlBtn_Heater_toggle.text()
        if self.MainHeaterStatus == "ON":
            self.controlBtn_Heater_toggle.setText("OFF")
            self.controlBtn_Heater_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")
            self.HeaterManual = 0
        elif self.MainHeaterStatus == "OFF":
            self.controlBtn_Heater_toggle.setText("ON")
            self.controlBtn_Heater_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
            self.HeaterManual = 1

    def OutdoorSaveConfig(self):
        self.OutdoorHeaterAuto = self.OutdoorCheck_AC_auto.isChecked()
        self.OutdoorTimerAuto = self.OutdoorCheck_Time_auto.isChecked()
        self.OutdoorDurationAuto = self.OutdoorCheck_Duration_auto.isChecked()

        self.OutdoorHeaterSetting = int(self.OutdoorLine_Heater.text())
        self.OutdoorTimer = int(self.OutdoorLine_Timer.text())
        self.OutdoorDuration = int(self.OutdoorLine_Duration.text())
        
    def controlHeaterInc(self):
        self.OutdoorHeaterSetting = int(self.OutdoorLine_Heater.text())
        self.OutdoorHeaterSetting += 1
        self.OutdoorLine_Heater.setText(str(self.OutdoorHeaterSetting))

    def controlHeaterDec(self):
        self.OutdoorHeaterSetting = int(self.OutdoorLine_Heater.text())
        self.OutdoorHeaterSetting -= 1
        self.OutdoorLine_Heater.setText(str(self.OutdoorHeaterSetting))

    def OutdoorHeater(self, Temp):  ## 수동모드에서 OFF 시 전원 OFF되는거 추가 필요. ##온도 센서 입력 시 해당 함수 call 필요.
        if self.OutdoorTimerAuto == True:
            CurrentTime = datetime.now()
            OutdoorRunTime = CurrentTime + timedelta(hours=self.OutdoorTimer)
            OutdoorStopTime = OutdoorRunTime + self.OutdoorDuration
            if CurrentTime >= OutdoorRunTime:
                if ((self.OutdoorDurationAuto == False) and (CurrentTime < self.OutdoorStopTime)):
                    TempGap = self.OutdoorHeaterSetting - Temp
                    if TempGap >= 10:
                        HeaterLevel = 4
                    elif (TempGap >= 7 and TempGap < 10):
                        HeaterLevel = 3
                    elif (TempGap >= 4 and TempGap < 7):
                        HeaterLevel = 2
                    elif (TempGap >= 0.5 and TempGap < 4):
                        HeaterLevel = 1
                    else:
                        HeaterLevel = 0
                    self.send(b'SHT',HeaterLevel)
                elif self.OutdoorDurationAuto == True:
                    if CurrentTime > OutdoorStopTime:
                        self.send(b'SHT',0)
                            
        else :
            self.send(b'SHT',0)


    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    

    sys.exit(app.exec_())