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
        ACDefault     = "18"
        DehumDefault  = "18"

        self.Current_mode.setText("Outdoor") ###Test

        self.controlBtn_AC_toggle.setText("OFF")
        self.controlBtn_Heater_toggle.setText("OFF")
        self.controlBtn_Dehum_toggle.setText("OFF")
        self.controlBtn_AC_toggle.setStyleSheet("background-color: red")
        self.controlBtn_Heater_toggle.setStyleSheet("background-color: red")
        self.controlBtn_Dehum_toggle.setStyleSheet("background-color: red")

        self.OutdoorLine_Heater.setText(HeaterDefault)
        self.IndoorLine_Heater.setText(HeaterDefault)
        self.OutdoorLine_AC.setText(ACDefault)
        self.IndoorLine_AC.setText(ACDefault)
        self.IndoorLine_Dehum.setText(DehumDefault)
        self.OutdoorLine_Dehum.setText(DehumDefault)

        self.controlLine_Heater.setText("0")
        self.OutdoorLine_Timer.setText("0")
        self.OutdoorLine_Duration.setText("30")

        self.OutdoorSaveConfig()
        self.IndoorSaveConfig()

        # self.controlBtn_Heater_toggle.clicked.connect(self.MainHeaterPwrBtn)

        self.OutdoorBtn_Saveconfig.clicked.connect(self.OutdoorSaveConfig)
        self.IndoorBtn_Saveconfig.clicked.connect(self.IndoorSaveConfig)

        self.IndoorBtn_AC_decrease.clicked.connect(self.IndoorACDec)
        self.IndoorBtn_AC_increase.clicked.connect(self.IndoorACInc)
        self.IndoorBtn_Heater_decrease.clicked.connect(self.IndoorHeaterDec)
        self.IndoorBtn_Heater_increase.clicked.connect(self.IndoorHeaterInc)
        self.IndoorBtn_Dehum_decrease.clicked.connect(self.IndoorDehumDec)
        self.IndoorBtn_Dehum_increase.clicked.connect(self.IndoorDehumInc)

        self.OutdoorBtn_AC_decrease.clicked.connect(self.OutdoorACDec)
        self.OutdoorBtn_AC_increase.clicked.connect(self.OutdoorACInc)
        self.OutdoorBtn_Heater_decrease.clicked.connect(self.OutdoorHeaterDec)
        self.OutdoorBtn_Heater_increase.clicked.connect(self.OutdoorHeaterInc)
        self.OutdoorBtn_Dehum_decrease.clicked.connect(self.OutdoorDehumDec)
        self.OutdoorBtn_Dehum_increase.clicked.connect(self.OutdoorDehumInc)


        self.pushButton.clicked.connect(self.TestChangeMode) ##테스트 버튼

        self.Current_mode.textChanged.connect(self.ExecuteMode)

    def TestChangeMode(self):
        if self.Current_mode.text() == "Indoor":
            self.Current_mode.setText("Outdoor")
        elif self.Current_mode.text() == "Outdoor":
            self.Current_mode.setText("Indoor")

    def ExecuteMode(self):
        if self.Current_mode.text() == "Outdoor":
            self.OutdoorAC()
            self.OutdoorHeater()
            self.OutdoorDehum()
        elif self.Current_mode.text() == "Indoor":
            self.IndoorAC()
            self.IndoorHeater()
            self.IndoorDehum()

    def sendDisplay(self, command, data = 0):
        print("send")
        req_data = struct.pack('<3sBc', command, data, b'\n')
        self.connHeater.write(req_data)
        print(data)
        return

    def IndoorACInc(self):
        self.IndoorACSetting = int(self.IndoorLine_AC.text())
        self.IndoorACSetting += 1
        self.IndoorLine_AC.setText(str(self.IndoorACSetting))

    def IndoorACDec(self):
        self.IndoorACSetting = int(self.IndoorLine_AC.text())
        self.IndoorACSetting -= 1
        self.IndoorLine_AC.setText(str(self.IndoorACSetting))
    
    def IndoorHeaterInc(self):
        self.IndoorHeaterSetting = int(self.IndoorLine_Heater.text())
        self.IndoorHeaterSetting += 1
        self.IndoorLine_Heater.setText(str(self.IndoorHeaterSetting))

    def IndoorHeaterDec(self):
        self.IndoorHeaterSetting = int(self.IndoorLine_Heater.text())
        self.IndoorHeaterSetting -= 1
        self.IndoorLine_Heater.setText(str(self.IndoorHeaterSetting))
    
    def IndoorDehumInc(self):
        self.IndoorDehumSetting = int(self.IndoorLine_Dehum.text())
        self.IndoorDehumSetting += 1
        self.IndoorLine_Dehum.setText(str(self.IndoorDehumSetting))

    def IndoorDehumDec(self):
        self.IndoorDehumSetting = int(self.IndoorLine_Dehum.text())
        self.IndoorDehumSetting -= 1
        self.IndoorLine_Dehum.setText(str(self.IndoorDehumSetting))

    def OutdoorACInc(self):
        self.OutdoorACSetting = int(self.OutdoorLine_AC.text())
        self.OutdoorACSetting += 1
        self.OutdoorLine_AC.setText(str(self.OutdoorACSetting))

    def OutdoorACDec(self):
        self.OutdoorACSetting = int(self.OutdoorLine_AC.text())
        self.OutdoorACSetting -= 1
        self.OutdoorLine_AC.setText(str(self.OutdoorACSetting))
        
    def OutdoorHeaterInc(self):
        self.OutdoorHeaterSetting = int(self.OutdoorLine_Heater.text())
        self.OutdoorHeaterSetting += 1
        self.OutdoorLine_Heater.setText(str(self.OutdoorHeaterSetting))

    def OutdoorHeaterDec(self):
        self.OutdoorHeaterSetting = int(self.OutdoorLine_Heater.text())
        self.OutdoorHeaterSetting -= 1
        self.OutdoorLine_Heater.setText(str(self.OutdoorHeaterSetting))

    def OutdoorDehumInc(self):
        self.OutdoorDehumSetting = int(self.OutdoorLine_Dehum.text())
        self.OutdoorDehumSetting += 1
        self.OutdoorLine_Dehum.setText(str(self.OutdoorDehumSetting))

    def OutdoorDehumDec(self):
        self.OutdoorDehumSetting = int(self.OutdoorLine_Dehum.text())
        self.OutdoorDehumSetting -= 1
        self.OutdoorLine_Dehum.setText(str(self.OutdoorDehumSetting))

    def IndoorSaveConfig(self):
        self.IndoorCheckACAuto = self.IndoorCheck_AC_auto.isChecked()
        self.IndoorCheckHeaterAuto = self.IndoorCheck_Heater_auto.isChecked()
        self.IndoorCheckDehumAuto = self.IndoorCheck_Dehum_auto.isChecked()
        
        self.IndoorACSetting = int(self.IndoorLine_AC.text())
        self.IndoorHeaterSetting = int(self.IndoorLine_Heater.text())
        self.IndoorDehumSetting = int(self.IndoorLine_Dehum.text())

        if self.Current_mode.text() == "Indoor":
            # self.controlLine_Heater.setText(str(self.IndoorHeaterSetting))
            self.IndoorAC()
            self.IndoorHeater()
            self.IndoorDehum()

    def OutdoorSaveConfig(self):
        self.OutdoorACAuto = self.OutdoorCheck_AC_auto.isChecked()
        self.OutdoorHeaterAuto = self.OutdoorCheck_Heater_auto.isChecked()
        self.OutdoorDehumAuto = self.OutdoorCheck_Dehum_auto.isChecked()

        self.OutdoorTimerAuto = self.OutdoorCheck_Time_auto.isChecked()
        self.OutdoorDurationAuto = self.OutdoorCheck_Duration_auto.isChecked()

        self.OutdoorACSetting = int(self.OutdoorLine_AC.text())
        self.OutdoorHeaterSetting = int(self.OutdoorLine_Heater.text())
        self.OutdoorDehumSetting = int(self.OutdoorLine_Dehum.text())

        self.OutdoorTimer = int(self.OutdoorLine_Timer.text())
        self.OutdoorDuration = int(self.OutdoorLine_Duration.text())

        if self.Current_mode.text() == "Outdoor":
            self.controlLine_Heater.setText(str(self.OutdoorHeaterSetting))
            self.OutdoorAC()
            self.OutdoorHeater()
            self.OutdoorDehum()

    def IndoorAC(self):#, Temp): 
        ACLevel = 0
        Temp = 5
        ACTempGap = self.IndoorACSetting - Temp
        self.controlLine_AC.setText(str(self.IndoorACSetting))
        if (self.IndoorCheckACAuto == True):
            if ACTempGap >= 10:
                ACLevel = 4
            elif (ACTempGap >= 7 and ACTempGap < 10):
                ACLevel = 3
            elif (ACTempGap >= 4 and ACTempGap < 7):
                ACLevel = 2
            elif (ACTempGap >= 0.5 and ACTempGap < 4):
                ACLevel = 1
            else:
                ACLevel = 0
            self.controlBtn_AC_toggle.setText("ON")
            self.controlBtn_AC_toggle.setStyleSheet("background-color: lightgreen")
        elif (self.IndoorCheckACAuto == False):
            ACLevel = 0
            self.controlBtn_AC_toggle.setText("OFF")
            self.controlBtn_AC_toggle.setStyleSheet("background-color: red")

        print("ACLevel : ", int(ACLevel))

    def IndoorHeater(self):#, Temp):
        HeaterLevel = 0
        Temp = 5
        TempGap = self.IndoorHeaterSetting - Temp
        self.controlLine_Heater.setText(str(self.IndoorHeaterSetting))
        if (self.IndoorCheckHeaterAuto == True):
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
            self.controlBtn_Heater_toggle.setText("ON")
            self.controlBtn_Heater_toggle.setStyleSheet("background-color: lightgreen")
        elif (self.IndoorCheckHeaterAuto == False):
            HeaterLevel = 0
            self.controlBtn_Heater_toggle.setText("OFF")
            self.controlBtn_Heater_toggle.setStyleSheet("background-color: red")

        print("HeaterLevel : ", int(HeaterLevel))

    def IndoorDehum(self):#, Temp):
        DehumLevel = 0
        Temp = 5
        DehumTempGap = self.IndoorDehumSetting - Temp
        self.controlLine_Dehum.setText(str(self.IndoorDehumSetting))
        if (self.IndoorCheckDehumAuto == True):
            if DehumTempGap >= 10:
                DehumLevel = 4
            elif (DehumTempGap >= 7 and DehumTempGap < 10):
                DehumLevel = 3
            elif (DehumTempGap >= 4 and DehumTempGap < 7):
                DehumLevel = 2
            elif (DehumTempGap >= 0.5 and DehumTempGap < 4):
                DehumLevel = 1
            else:
                DehumLevel = 0
            self.controlBtn_Dehum_toggle.setText("ON")
            self.controlBtn_Dehum_toggle.setStyleSheet("background-color: lightgreen")
        elif (self.IndoorCheckDehumAuto == False):
            DehumLevel = 0
            self.controlBtn_Dehum_toggle.setText("OFF")
            self.controlBtn_Dehum_toggle.setStyleSheet("background-color: red")

        print("DehumLevel : ", int(DehumLevel))

    def OutdoorAC(self):#, Temp):
        ACLevel = 0
        Temp = 5
        self.controlLine_AC.setText(str(self.OutdoorACSetting))

        if ((self.OutdoorTimerAuto == True) and (self.OutdoorACAuto == True)):
            CurrentTime = datetime.now()
            OutdoorRunTime = CurrentTime + timedelta(hours = self.OutdoorTimer)
            OutdoorStopTime = OutdoorRunTime + timedelta(hours = self.OutdoorDuration)
            if CurrentTime >= OutdoorRunTime:
                if ((self.OutdoorDurationAuto == False) and (CurrentTime <= OutdoorStopTime)):
                    ACTempGap = self.OutdoorACSetting - Temp
                    if ACTempGap >= 10:
                        ACLevel = 4
                    elif (ACTempGap >= 7 and ACTempGap < 10):
                        ACLevel = 3
                    elif (ACTempGap >= 4 and ACTempGap < 7):
                        ACLevel = 2
                    elif (ACTempGap >= 0.5 and ACTempGap < 4):
                        ACLevel = 1
                    else:
                        ACLevel = 0
                elif self.OutdoorDurationAuto == True:
                    if CurrentTime > OutdoorStopTime:
                        ACLevel = 0
                self.controlBtn_AC_toggle.setText("ON")
                self.controlBtn_AC_toggle.setStyleSheet("background-color: lightgreen")
        else :
            ACLevel = 0
            self.controlBtn_AC_toggle.setText("OFF")
            self.controlBtn_AC_toggle.setStyleSheet("background-color: red")

        print("ACLevel : ", int(ACLevel))
        # self.sendDisplay(b'SHT',ACLevel)
        pass

    def OutdoorHeater(self):#, Temp):  ## 수동모드에서 OFF 시 전원 OFF되는거 추가 필요. ##온도 센서 입력 시 해당 함수 call 필요.
        HeaterLevel = 0
        Temp = 5
        self.controlLine_Heater.setText(str(self.OutdoorHeaterSetting))

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
        else :
            HeaterLevel = 0
            self.controlBtn_Heater_toggle.setText("OFF")
            self.controlBtn_Heater_toggle.setStyleSheet("background-color: red")

        print("HeaterLevel : ", int(HeaterLevel))
        # self.sendDisplay(b'SHT',HeaterLevel)
        pass

    def OutdoorDehum(self):#, Temp):  ## 수동모드에서 OFF 시 전원 OFF되는거 추가 필요. ##온도 센서 입력 시 해당 함수 call 필요.
        DehumLevel = 0
        Temp = 5
        self.controlLine_Dehum.setText(str(self.OutdoorDehumSetting))

        if ((self.OutdoorTimerAuto == True) and (self.OutdoorHeaterAuto == True)):
            CurrentTime = datetime.now()
            OutdoorRunTime = CurrentTime + timedelta(hours = self.OutdoorTimer)
            OutdoorStopTime = OutdoorRunTime + timedelta(hours = self.OutdoorDuration)
            if CurrentTime >= OutdoorRunTime:
                if ((self.OutdoorDurationAuto == False) and (CurrentTime <= OutdoorStopTime)):
                    DehumTempGap = self.OutdoorDehumSetting - Temp
                    if DehumTempGap >= 10:
                        DehumLevel = 4
                    elif (DehumTempGap >= 7 and DehumTempGap < 10):
                        DehumLevel = 3
                    elif (DehumTempGap >= 4 and DehumTempGap < 7):
                        DehumLevel = 2
                    elif (DehumTempGap >= 0.5 and DehumTempGap < 4):
                        DehumLevel = 1
                    else:
                        DehumLevel = 0
                elif self.OutdoorDurationAuto == True:
                    if CurrentTime > OutdoorStopTime:
                        DehumLevel = 0
                self.controlBtn_Dehum_toggle.setText("ON")
                self.controlBtn_Dehum_toggle.setStyleSheet("background-color: lightgreen")
        else :
            DehumLevel = 0
            self.controlBtn_Dehum_toggle.setText("OFF")
            self.controlBtn_Dehum_toggle.setStyleSheet("background-color: red")

        print("DehumLevel : ", int(DehumLevel))
        # self.sendDisplay(b'SHT',DehumLevel)
        pass

    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    

    sys.exit(app.exec_())