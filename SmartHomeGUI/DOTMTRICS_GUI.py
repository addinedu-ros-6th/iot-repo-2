import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtCore import QMetaObject, Qt
import serial
import struct
from datetime import datetime, timedelta

from_class = uic.loadUiType("/home/jh/dev_ws/Project/IoT/local_iot-repo-2/GUI_v7.ui")[0]
class WindowClass(QMainWindow, from_class) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.connHeater = \
        #     serial.Serial(port='/dev/ttyACM0', baudrate = 9600, timeout = 1)
        
        HeaterDefault = "18"

        self.Current_mode.setText("Outdoor") ###Test

        self.controlBtn_Heater_toggle.setText("OFF")
        self.controlBtn_Heater_toggle.setStyleSheet("background-color: red")

        self.OutdoorLine_Heater.setText(HeaterDefault)

        self.controlLine_Heater.setText("0")
        self.OutdoorLine_Timer.setText("0")
        self.OutdoorLine_Duration.setText("30")

        self.OutdoorSaveConfig()
        self.controlBtn_Heater_toggle.clicked.connect(self.MainHeaterPwrBtn)

        self.OutdoorBtn_Saveconfig.clicked.connect(self.OutdoorSaveConfig)
        self.OutdoorBtn_Heater_decrease.clicked.connect(self.OutdoorHeaterDec)
        self.OutdoorBtn_Heater_increase.clicked.connect(self.OutdoorHeaterInc)
        self.pushButton.clicked.connect(self.TestChangeMode) ##테스트 버튼

        self.Current_mode.textChanged.connect(self.ExecuteMode)

    def TestChangeMode(self):
        if self.Current_mode.text() == "Indoor":
            self.Current_mode.setText("Outdoor")
        elif self.Current_mode.text() == "Outdoor":
            self.Current_mode.setText("Indoor")

    def ExecuteMode(self):
        if self.Current_mode.text() == "Outdoor":
            self.OutdoorHeater()
        # elif self.Current_mode.text() == "Indoor":
        #     self.IndoorHeater()

    def sendDisplay(self, command, data = 0):
        print("send")
        req_data = struct.pack('<3sBc', command, data, b'\n')
        self.connHeater.write(req_data)
        print(data)
        return

    def MainHeaterPwrBtn(self):
        self.MainHeaterStatus = self.controlBtn_Heater_toggle.text()

        if self.MainHeaterStatus == "ON":
            self.controlBtn_Heater_toggle.setText("OFF")
            self.controlBtn_Heater_toggle.setStyleSheet("background-color: red")
        elif self.MainHeaterStatus == "OFF":
            self.controlBtn_Heater_toggle.setText("ON")
            self.controlBtn_Heater_toggle.setStyleSheet("background-color: lightgreen")
        
        if self.Current_mode.text() == "Outdoor":
            self.OutdoorHeater()
        elif self.Current_mode.text() == "Indoor":
            self.IndoorHeater()

    def IndoorHeaterInc(self):
        self.OutdoorHeaterSetting = int(self.OutdoorLine_Heater.text())
        self.OutdoorHeaterSetting += 1
        self.OutdoorLine_Heater.setText(str(self.OutdoorHeaterSetting))

    def IndoorHeaterDec(self):
        self.OutdoorHeaterSetting = int(self.OutdoorLine_Heater.text())
        self.OutdoorHeaterSetting -= 1
        self.OutdoorLine_Heater.setText(str(self.OutdoorHeaterSetting))
        
    def OutdoorHeaterInc(self):
        self.OutdoorHeaterSetting = int(self.OutdoorLine_Heater.text())
        self.OutdoorHeaterSetting += 1
        self.OutdoorLine_Heater.setText(str(self.OutdoorHeaterSetting))

    def OutdoorHeaterDec(self):
        self.OutdoorHeaterSetting = int(self.OutdoorLine_Heater.text())
        self.OutdoorHeaterSetting -= 1
        self.OutdoorLine_Heater.setText(str(self.OutdoorHeaterSetting))

    def IndoorSaveConfig(self):
        self.IndoorCheck_Heater_Auto = self.IndoorCheck_Heater_auto.isChecked()

        self.IndoorHeaterSetting = int(self.IndoorLine_Heater.text())

        if self.Current_mode.text() == "Indoor":
            self.controlLine_Heater.setText(str(self.IndoorHeaterSetting))

            if self.IndoorCheck_Heater_Auto == True:
                self.controlBtn_Heater_toggle.setDisabled(True)
            else:
                self.controlBtn_Heater_toggle.setEnabled(True)

    def OutdoorSaveConfig(self):
        self.OutdoorHeaterAuto = self.OutdoorCheck_Heater_auto.isChecked()
        self.OutdoorTimerAuto = self.OutdoorCheck_Time_auto.isChecked()
        self.OutdoorDurationAuto = self.OutdoorCheck_Duration_auto.isChecked()

        self.OutdoorHeaterSetting = int(self.OutdoorLine_Heater.text())
        self.OutdoorTimer = int(self.OutdoorLine_Timer.text())
        self.OutdoorDuration = int(self.OutdoorLine_Duration.text())

        if self.Current_mode.text() == "Outdoor":
            self.controlLine_Heater.setText(str(self.OutdoorHeaterSetting))

            if self.OutdoorHeaterAuto == True:
                self.controlBtn_Heater_toggle.setDisabled(True)
            else:
                self.controlBtn_Heater_toggle.setEnabled(True)

    def OutdoorHeater(self):#, Temp):  ## 수동모드에서 OFF 시 전원 OFF되는거 추가 필요. ##온도 센서 입력 시 해당 함수 call 필요.
        HeaterLevel = 0
        Temp = 5

        if ((self.OutdoorTimerAuto == True) and (self.OutdoorHeaterAuto == True)):
            CurrentTime = datetime.now()
            OutdoorRunTime = CurrentTime + timedelta(hours = self.OutdoorTimer)
            OutdoorStopTime = OutdoorRunTime + timedelta(hours = self.OutdoorDuration)
            if CurrentTime >= OutdoorRunTime:
                if ((self.OutdoorDurationAuto == False) and (CurrentTime <= OutdoorStopTime)):
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
                elif self.OutdoorDurationAuto == True:
                    if CurrentTime > OutdoorStopTime:
                        HeaterLevel = 0
                self.controlBtn_Heater_toggle.setText("ON")
                self.controlBtn_Heater_toggle.setStyleSheet("background-color: lightgreen")
        elif ((self.OutdoorTimerAuto == False) and (self.controlBtn_Heater_toggle.text() == "ON")):
            TempGap = self.OutdoorHeaterSetting - Temp
            if TempGap >= 10:
                HeaterLevel = 4
            elif (TempGap >= 7 and TempGap < 10):
                HeaterLevel = 3
            elif (TempGap >= 4 and TempGap < 7):
                HeaterLevel = 2
            elif (TempGap >= 0.1 and TempGap < 4):
                HeaterLevel = 1
            else:
                HeaterLevel = 0
        elif (self.controlBtn_Heater_toggle.text() == "OFF"):
            HeaterLevel = 0


        print("HeaterLevel : ", int(HeaterLevel))
        # self.sendDisplay(b'SHT',HeaterLevel)

        pass



    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    

    sys.exit(app.exec_())
