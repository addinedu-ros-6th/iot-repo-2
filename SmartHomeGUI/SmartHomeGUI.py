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
import mysql.connector
from datetime import datetime

mydb = mysql.connector.connect(
            host = "database-1.cpog6osggiv3.ap-northeast-2.rds.amazonaws.com",
            user = "arduino_PJT",
            password = "1234",
            database = "ardumension"
            )

# from_class =  uic.loadUiType("./IOT_Project_2/iot-repo-2/SmartHomeGUI/SmartHomeGUI.ui")[0]
from_class =  uic.loadUiType("/home/sh/dev_ws/PJT/IOT/iot-repo-2/SmartHomeGUI/SmartHomeGUI.ui")[0]

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    PyQt5.QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    PyQt5.QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.uidList = []
        self.prevLcdValue = 9
        self.cur = mydb.cursor(buffered=True)
        self.cycleTime = 500
        self.doorStatus = False # false : closed / true : opended
        self.LEDcount = 0 # merge Light_Dark_mode.py
        self.Blindcount = 0

        self.connEnv = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
        self.connHeater = serial.Serial(port='/dev/ttyACM1', baudrate=9600, timeout=1)
        self.connDevice = serial.Serial(port='/dev/ttyACM2', baudrate=9600, timeout=1)
        time.sleep(1)

        
        self.recv = Receiver(self.connEnv, self.connDevice)
        self.activationStatus = False
        # self.connSensorReader = serial.Serial(port='/dev/ttyACM2', baudrate= 9600, timeout= 1)
        # self.connHeaterController = serial.Serial(port='/dev/ttyACM1', baudrate= 9600, timeout= 1)
        # self.connHomeItemController = serial.Serial(port='/dev/ttyACM0', baudrate= 9600, timeout= 1)
        # self.recv = Receiver(self.connSensorReader)
        # self.recv.start()

        self.GetUidFromDB()

        self.recv.detectedTag.connect(self.detectedTag) #tag 감지 신호
        self.recv.unDetectedTag.connect(self.unDetectedTag) #tag 미감지 신호
        self.recv.detectedDoor.connect(self.detectedDoor) #도어 센서 감지 신호
        self.recv.detectedCard.connect(self.detectedCard) #카드 센서 감지 신호

        self.recv.lightSensorValueReceived.connect(self.onLightSensorValueReceived) # merge Light_Dark_mode.py

        self.RegistrationBtn_Activation.setCheckable(True)
        self.RegistrationBtn_Activation.clicked.connect(self.Activation) #UID 등록하기 위한 버튼
        self.RegistrationLine_UID.textChanged.connect(self.uidText) #등록할 UID 입력 시 
        self.RegistrationBtn_Register.clicked.connect(self.Register) #CARD에 UID, Name 등록하기 버튼
        self.Registration_Table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) #등록창 넓이 조절
        self.RegistrationBtn_Remove.clicked.connect(self.uidDelete)
        self.doorOpen.clicked.connect(self.dooropen)
        self.doorClose.clicked.connect(self.doorclose)
        
        self.recv.update_signal.connect(self.update_sensor_data)
        self.recv.ac_status_signal.connect(self.update_ac_status)
        self.recv.start()


        self.initialize_variables()
        self.setup_ui()
        self.connect_signals()

        QTimer.singleShot(100, self.send_gth_command)

        # self.controlBtn_AC_toggle.clicked.connect(self.control_AC_toggle)
        # self.controlBtn_AC_toggle.setText('OFF')
        # self.controlBtn_AC_toggle.setStyleSheet("background-color: rgb(255, 255, 255);")
        # self.controlBtn_Heater_toggle.clicked.connect(self.MainHeaterPwrBtn)
        # self.controlBtn_Heater_toggle.setText("OFF")
        # self.controlBtn_Heater_toggle.setStyleSheet("background-color: rgb(255, 255, 255);")
        # self.controlBtn_Dehum_toggle.clicked.connect(self.control_Dehum_toggle)
        # self.controlBtn_Dehum_toggle.setText('OFF')
        # self.controlBtn_Dehum_toggle.setStyleSheet("background-color: rgb(255, 255, 255);")
        # self.controlBtn_Light_toggle.clicked.connect(self.control_Light_toggle)
        # self.controlBtn_Light_toggle.setText('OFF')
        # self.controlBtn_Light_toggle.setStyleSheet("background-color: rgb(255, 255, 255);")
        # self.controlBtn_Blind_toggle.clicked.connect(self.control_Blind_toggle)
        # self.controlBtn_Blind_toggle.setText('Open')
        # self.controlBtn_Blind_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")
        # self.controlBtn_Door_toggle.clicked.connect(self.control_Door_toggle)
        # self.controlBtn_Door_toggle.setText('Open')
        # self.controlBtn_Door_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")

    #     self.controlBtn_Dehum_toggle.clicked.connect(self.control_Dehum_toggle)
    #     self.controlBtn_Dehum_toggle.setText('OFF')
    #     self.controlBtn_Dehum_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
    
    # # merge Blind_GUI.py   
        self.controlBtn_Blind_toggle.clicked.connect(self.control_Blind_toggle)
        self.controlBtn_Blind_toggle.setText('Open')
        self.controlBtn_Blind_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")

        self.timer = QTimer()
        self.timer.setInterval(self.cycleTime)
        self.timer.timeout.connect(self.getStatus)
        self.timer.start()
        
        self.gth_timer = QTimer(self)
        self.gth_timer.timeout.connect(self.send_gth_command)
        self.gth_timer.start(3000)  # 5초마다 GTH 명령 전송

        self.temp_timer = QTimer(self)
        self.temp_timer.timeout.connect(self.update_temperature)
        self.temp_timer.start(3000)  # 5초마다 온도 업데이트

        self.button_states = {}
        self.weekday_buttons = {
            "Monday": self.IndoorBtn_Mon,
            "Tuesday": self.IndoorBtn_Tue,
            "Wednesday": self.IndoorBtn_Wen,
            "Thursday": self.IndoorBtn_Thu,
            "Friday": self.IndoorBtn_Fri,
            "Saturday": self.IndoorBtn_Sat,
            "Sunday": self.IndoorBtn_Sun,
        }
        
        for button in self.weekday_buttons.values():
            self.button_states[button] = False
            button.setStyleSheet("background-color: rgb(255, 255, 255);")  # 기본 색상 white로 설정
            button.clicked.connect(lambda _, b=button: self.toggle_button_state(b))
        setting_button = [
            self.IndoorBtn_Wakeup_Light, self.IndoorBtn_Wakeup_Blind, self.IndoorBtn_Wakeup_Alarm,
            self.IndoorBtn_Sleep_Light, self.IndoorBtn_Sleep_Blind, self.IndoorBtn_Sleep_Alarm
        ]

        for button in setting_button:
            self.button_states[button] = False
            button.setStyleSheet("background-color: rgb(255, 255, 255);")
            button.clicked.connect(lambda _, b=button: self.toggle_button_state(b))
        self.IndoorCombo_Select.currentIndexChanged.connect(self.update_day_selection)
        self.IndoorBtn_Saveconfig.clicked.connect(self.save_configuration)

        self.schedule_timer = QTimer(self)
        self.schedule_timer.timeout.connect(self.update_time)
        self.schedule_timer.start(5000)  # 5초마다 타이머가 동작
        self.scheduled_times = []
        self.setup_alarm_table()
        self.load_scheduled_times_from_table()
    
    
    def initialize_variables(self):
        self.outdoor_ac_setting = 18
        self.indoor_ac_setting = 18
        self.outdoor_heater_setting = 18
        self.indoor_heater_setting = 18
        self.outdoor_ac_auto = False
        self.indoor_ac_auto = False
        self.outdoor_heater_auto = False
        self.indoor_heater_auto = False
        self.ac_on = False
        self.heater_on = False
        self.simulated_temperature = None
        self.last_real_temperature = None
        self.set_temperature = self.outdoor_ac_setting

    def setup_ui(self):
        self.Current_mode.setText("Outdoor")
        self.controlBtn_AC_toggle.setText('OFF')
        self.controlBtn_AC_toggle.setStyleSheet("background-color: red")
        self.controlBtn_Heater_toggle.setText('OFF')
        self.controlBtn_Heater_toggle.setStyleSheet("background-color: red")
        self.OutdoorLine_AC.setText(str(self.outdoor_ac_setting))
        self.IndoorLine_AC.setText(str(self.indoor_ac_setting))
        self.OutdoorLine_Heater.setText(str(self.outdoor_heater_setting))
        self.IndoorLine_Heater.setText(str(self.indoor_heater_setting))
        self.controlLine_AC.setText(str(self.set_temperature))
        self.controlLine_Heater.setText(str(self.outdoor_heater_setting))
        self.OutdoorLine_Timer.setText("0")
        self.OutdoorLine_Duration.setText("30")

    def connect_signals(self):
        self.OutdoorBtn_Saveconfig.clicked.connect(self.OutdoorSaveConfig)
        self.IndoorBtn_Saveconfig.clicked.connect(self.IndoorSaveConfig)
        self.OutdoorBtn_AC_decrease.clicked.connect(self.OutdoorACDec)
        self.OutdoorBtn_AC_increase.clicked.connect(self.OutdoorACInc)
        self.IndoorBtn_AC_decrease.clicked.connect(self.IndoorACDec)
        self.IndoorBtn_AC_increase.clicked.connect(self.IndoorACInc)
        self.OutdoorBtn_Heater_decrease.clicked.connect(self.OutdoorHeaterDec)
        self.OutdoorBtn_Heater_increase.clicked.connect(self.OutdoorHeaterInc)
        self.IndoorBtn_Heater_decrease.clicked.connect(self.IndoorHeaterDec)
        self.IndoorBtn_Heater_increase.clicked.connect(self.IndoorHeaterInc)
        self.pushButton.clicked.connect(self.TestChangeMode)
        self.Current_mode.textChanged.connect(self.ExecuteMode)

    def OutdoorACInc(self):
        self.outdoor_ac_setting = int(self.OutdoorLine_AC.text())
        self.outdoor_ac_setting += 1
        self.OutdoorLine_AC.setText(str(self.outdoor_ac_setting))

    def OutdoorACDec(self):
        self.outdoor_ac_setting = int(self.OutdoorLine_AC.text())
        self.outdoor_ac_setting -= 1
        self.OutdoorLine_AC.setText(str(self.outdoor_ac_setting))

    def IndoorACInc(self):
        self.indoor_ac_setting = int(self.IndoorLine_AC.text())
        self.indoor_ac_setting += 1
        self.IndoorLine_AC.setText(str(self.indoor_ac_setting))

    def IndoorACDec(self):
        self.indoor_ac_setting = int(self.IndoorLine_AC.text())
        self.indoor_ac_setting -= 1
        self.IndoorLine_AC.setText(str(self.indoor_ac_setting))

    def OutdoorHeaterInc(self):
        self.outdoor_heater_setting = int(self.OutdoorLine_Heater.text())
        self.outdoor_heater_setting += 1
        self.OutdoorLine_Heater.setText(str(self.outdoor_heater_setting))

    def OutdoorHeaterDec(self):
        self.outdoor_heater_setting = int(self.OutdoorLine_Heater.text())
        self.outdoor_heater_setting -= 1
        self.OutdoorLine_Heater.setText(str(self.outdoor_heater_setting))

    def IndoorHeaterInc(self):
        self.indoor_heater_setting = int(self.IndoorLine_Heater.text())
        self.indoor_heater_setting += 1
        self.IndoorLine_Heater.setText(str(self.indoor_heater_setting))

    def IndoorHeaterDec(self):
        self.indoor_heater_setting = int(self.IndoorLine_Heater.text())
        self.indoor_heater_setting -= 1
        self.IndoorLine_Heater.setText(str(self.indoor_heater_setting))

    def OutdoorSaveConfig(self):
        self.outdoor_ac_setting = int(self.OutdoorLine_AC.text())
        self.outdoor_heater_setting = int(self.OutdoorLine_Heater.text())
        self.outdoor_ac_auto = self.OutdoorCheck_AC_auto.isChecked()        
        self.outdoor_heater_auto = self.OutdoorCheck_Heater_auto.isChecked()

        if self.Current_mode.text() == "Outdoor":
            self.controlLine_AC.setText(str(self.outdoor_ac_setting))
            self.controlLine_Heater.setText(str(self.outdoor_heater_setting))
            self.set_temperature = float(self.controlLine_AC.text())
            self.ExecuteMode()

    def IndoorSaveConfig(self):
        self.indoor_ac_setting = int(self.IndoorLine_AC.text())
        self.indoor_heater_setting = int(self.IndoorLine_Heater.text())
        self.indoor_ac_auto = self.IndoorCheck_AC_auto.isChecked()
        self.indoor_heater_auto = self.IndoorCheck_Heater_auto.isChecked()

        if self.Current_mode.text() == "Indoor":
            self.controlLine_AC.setText(str(self.indoor_ac_setting))
            self.controlLine_Heater.setText(str(self.indoor_heater_setting))
            self.set_temperature = float(self.controlLine_AC.text())
            self.ExecuteMode()
    
    def TestChangeMode(self):
        if self.Current_mode.text() == "Indoor":
            self.Current_mode.setText("Outdoor")
        elif self.Current_mode.text() == "Outdoor":
            self.Current_mode.setText("Indoor")

    def ExecuteMode(self):
        if self.Current_mode.text() == "Outdoor":
            self.OutdoorAC()
            self.OutdoorHeater()
        elif self.Current_mode.text() == "Indoor":
            self.IndoorAC()
            self.IndoorHeater()

    def OutdoorAC(self):
        self.controlLine_AC.setText(str(self.outdoor_ac_setting))
        self.set_temperature = float(self.controlLine_AC.text())
        
        if self.outdoor_ac_auto:
            self.turn_ac_on()
        else:
            self.turn_ac_off()
        
    def OutdoorHeater(self):
        self.controlLine_Heater.setText(str(self.outdoor_heater_setting))
        self.set_temperature = float(self.controlLine_Heater.text())
        
        if self.outdoor_heater_auto:
            self.turn_heater_on()
        else:
            self.turn_heater_off()

    def IndoorAC(self):
        self.controlLine_AC.setText(str(self.indoor_ac_setting))
        self.set_temperature = float(self.controlLine_AC.text())
        
        if self.indoor_ac_auto:
            self.turn_ac_on()
        else:
            self.turn_ac_off()

    def IndoorHeater(self):
        self.controlLine_Heater.setText(str(self.indoor_heater_setting))
        self.set_temperature = float(self.controlLine_Heater.text())
        
        if self.indoor_heater_auto:
            self.turn_heater_on()
        else:
            self.turn_heater_off()

    def turn_ac_on(self):
        self.controlBtn_AC_toggle.setText('ON')
        self.controlBtn_AC_toggle.setStyleSheet("background-color: green")
        self.ac_on = True
        if self.simulated_temperature is None:
            self.simulated_temperature = self.last_real_temperature
        self.sendAC(b'SAC', 1)  # AC ON (LED ON)
        # print(f"AC turned ON, Set temperature: {self.set_temperature}, Current temperature: {self.simulated_temperature:.1f}")

    def turn_ac_off(self):
        self.controlBtn_AC_toggle.setText('OFF')
        self.controlBtn_AC_toggle.setStyleSheet("background-color: red")
        self.ac_on = False
        self.sendAC(b'SAC', 0)  # AC OFF (LED OFF)
        # print("AC turned OFF")

    def turn_heater_on(self):
        self.controlBtn_Heater_toggle.setText('ON')
        self.controlBtn_Heater_toggle.setStyleSheet("background-color: green")
        self.heater_on = True
        self.sendHeater(b'SHT', 1)
        # print(f"Heater turned ON, Set temperature: {self.controlLine_Heater.text()}")

    def turn_heater_off(self):
        self.controlBtn_Heater_toggle.setText('OFF')
        self.controlBtn_Heater_toggle.setStyleSheet("background-color: red")
        self.heater_on = False
        self.sendHeater(b'SHT',0)
        # print("Heater turned OFF")


     #        #Dehumidifier_GUI.py
    
    # #Dehumidifier_GUI.py
    def control_Dehum_toggle(self):
        if self.controlBtn_Dehum_toggle.text() == 'ON':
            self.controlBtn_Dehum_toggle.setText('OFF')
            self.controlBtn_Dehum_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
            self.sendHomeItemController(b'SHM', 0) # 0을 보내면 문을 닫기
        else:
            self.controlBtn_Dehum_toggle.setText('ON')
            self.controlBtn_Dehum_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")
            self.sendHomeItemController(b'SHM', 1) # 1을 보내면 문을 열기
        return
    
    # # merge Blind_GUI.py
    def control_Blind_toggle(self):
        if self.controlBtn_Blind_toggle.text() == 'Open':
            self.controlBtn_Blind_toggle.setText('Close')
            self.controlBtn_Blind_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
            self.sendHomeItemController(b'SBM', 0) # 0을 보내면 블라인드를 닫기
        else:
            self.controlBtn_Blind_toggle.setText('Open')
            self.controlBtn_Blind_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")
            self.sendHomeItemController(b'SBM', 1) # 1을 보내면 블라인드를 열기
        return
    
    # # merge Light_Dark_mode.py
    def onLightSensorValueReceived(self, value):
        # print(f"Light Sensor Value: {value}")
        # print(f"LEDcount: {self.LEDcount}")
        # print(f"BlindCount : {self.Blindcount}")
        light_mode = self.IndoorCombo_Light.currentText()
        if light_mode == "LightMode":
            if value <= 17: ##test 10
                self.LEDcount += 1
                if self.LEDcount == 10:
                    self.sendHomeItemController(b'SLI', 1)  # Turn on LED
                if self.LEDcount > 20:
                    self.LEDcount = 20
            else:
                if self.LEDcount > 0:
                    self.LEDcount -= 1
                if self.LEDcount == 0:
                    self.sendHomeItemController(b'SLI', 0)  # Turn off LED
        elif light_mode == "DarkMode":
            if value > 10:
                self.LEDcount += 1
                if self.LEDcount == 10:
                    self.sendHomeItemController(b'SLI', 0)  # Turn off LED
                if self.LEDcount > 20:
                    self.LEDcount = 20
            else:
                if self.LEDcount > 0:
                    self.LEDcount -= 1
                if self.LEDcount == 0:
                    self.sendHomeItemController(b'SLI', 1)  # Turn on LED

        blind_mode = self.IndoorCombo_Blind.currentText()
        if blind_mode == "LightMode":
            if value <= 18:
                self.Blindcount += 1
                if self.Blindcount == 10:
                    self.sendHomeItemController(b'SBM', 1)  # Open blinds
                if self.Blindcount > 20:
                    self.Blindcount = 20
            else:
                if self.Blindcount > 0:
                    self.Blindcount -= 1
                if self.Blindcount == 0:
                    self.sendHomeItemController(b'SBM', 0)  # Close blinds
        elif blind_mode == "DarkMode":
            if value <= 30:
                self.Blindcount += 1
                if self.Blindcount == 10:
                    self.sendHomeItemController(b'SBM', 0)  # Close blinds
                if self.Blindcount > 20:
                    self.Blindcount = 20
            else:
                if self.Blindcount > 0:
                    self.Blindcount -= 1
                if self.Blindcount == 0:
                    self.sendHomeItemController(b'SBM', 1)  # Open blinds

    def dooropen(self):
        self.sendHomeItemController(b'SDM',1)
        return
      
    def doorclose(self):
        if self.doorStatus == False:
            self.sendHomeItemController(b'SDM',0)
        return      

    def getStatus(self):
        # print("")
        self.sendSensorReader(b'GST')
        time.sleep(0.05)
        self.sendSensorReader(b'GDS')
        time.sleep(0.05)
        self.sendSensorReader(b'GCS')
        time.sleep(0.05)
        self.sendSensorReader(b'GLI')
        return
    
    def detectedDoor(self, value):
        # print("")          
        if (value == 1 and self.prevLcdValue != 1): 
            self.sendDisplayController(b'SLC',2)    # door close
            self.doorStatus = False  
            time.sleep(1)       
            self.sendHomeItemController(b'SDM',0) 
            self.sendDisplayController(b'SLC',3)   
            self.controlBtn_Door_toggle.setText('Close')
            self.controlBtn_Door_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
        elif (value == 0 and self.prevLcdValue != 0): 
            self.sendDisplayController(b'SLC',1)    # door open
            self.doorStatus = True
            self.controlBtn_Door_toggle.setText('Open')
            self.controlBtn_Door_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")
        self.prevLcdValue = value  
        return
    
    def detectedCard(self, value):
        # print("")  
        if value == 1:
            self.Current_mode.setText("Indoor")
            self.Current_mode.setStyleSheet("background-color : lightgreen")
        elif value == 0:
            self.Current_mode.setText("Outdoor")
            self.Current_mode.setStyleSheet("background-color : lightblue")    
        return
    
    def detectedTag(self, uid):
        # print("detected Tag")
        self.getUid = uid.decode('utf-8')
        self.RegistrationBtn_Register.setStyleSheet("background-color : lightgreen")
        self.judge()
    
    def judge(self):
        # print(self.uidList)
        # print(self.getUid)
        for i in range(len(self.uidList)):
            if self.getUid == self.uidList[i]: #현재는 무조건 8자를 입력해야 인식
                findUidlist = True
            else:
                findUidlist = False
        if findUidlist == True:
            self.sendDisplayController(b'SLC',0)
            if self.doorStatus == False:
                self.sendHomeItemController(b'SDM',1)
        else:
            self.sendDisplayController(b'SLC',4)
         
    def uidDelete(self):
        row = self.Registration_Table.currentRow() #선택한 아이템이 몇번째 row인지 저장
        uid = self.Registration_Table.item(row,1).text() #username
        self.Registration_Table.removeRow(row)
        # print(uid)
        sql = f"delete from RFID where RFID = '{uid}';"
        # print(sql)
        self.cur.execute(sql)
        mydb.commit()
        self.GetUidFromDB()
               
    def unDetectedTag(self):
        self.RegistrationBtn_Register.setStyleSheet("background-color : red")

    def GetUidFromDB(self):
        self.Registration_Table.setRowCount(0) #데이터 리셋
        self.cur.execute("select UserID, RFID from RFID order by 등록시간;")
        result = self.cur.fetchall()
        for i in range(len(result)):
            self.Registration_Table.insertRow(i)
            self.Registration_Table.setItem(i, 0, QTableWidgetItem(result[i][0])) #username
            self.Registration_Table.setItem(i, 1, QTableWidgetItem(result[i][1])) #UID
            self.uidList.append(result[i][1])
        return

    def Activation(self, state): #버튼 클릭 시 색 변환 및 상태 true 로 변환
        self.RegistrationBtn_Activation.setStyleSheet("background-color: %s" % ({True: "lightgreen", False: "red"}[state]))
        self.activationStatus = self.RegistrationBtn_Activation.isChecked() # true : button ON / false : button OFF 
        return
    
    def uidText(self): #8자까지 UID 입력 
        if len(self.RegistrationLine_UID.text()) <= 8:
            self.setUid = str(self.RegistrationLine_UID.text())                 
        elif len(self.RegistrationLine_UID.text()) > 8:
            self.RegistrationLine_UID.setText(self.setUid)
        return
    
    def Register(self): #Activation 버튼 눌렸을 때만 기록 
        if self.activationStatus == True:
            userName = self.RegistrationLine_Name.text()
            uid = self.setUid    

            self.sendSensorReader(b"SID", self.setUid)

            now = datetime.now()
            currentTime = now.strftime('%Y-%m-%d %H:%M:%S')

            sql = f"insert into RFID (RFID, 등록시간, UserID) values ('{uid}', '{currentTime}', '{userName}');"
            self.cur.execute(sql)
            mydb.commit()

            self.GetUidFromDB()

            self.RegistrationLine_UID.setText("")
            self.RegistrationLine_Name.setText("")
        else:
            self.RegistrationLine_UID.setText("")
            self.RegistrationLine_Name.setText("")
        return
    
    def sendSensorReader(self, command, id=""):      
        set_data = struct.pack('<3s8sc', command, id.encode(), b'\n')
        self.connEnv.write(set_data)
        # print("sendSensorReader = ", set_data)
        return

    def sendDisplayController(self, command, data = 0):
        set_data = struct.pack('<3sBc', command, data, b'\n')
        self.connHeater.write(set_data)
        # print("sendDisplayController = ", set_data)
        return
    
    def sendHomeItemController(self, command, data = 0):
        set_data = struct.pack('<3sBc', command, data, b'\n')
        self.connDevice.write(set_data)  ################conn 컨트롤러 변경 필요
        print("sendHomeItemController = ", set_data)
        return
    
    def send_gth_command(self):
        self.connEnv.write(b'GTH\n')
        # print("Sent GTH command")

    def sendAC(self, command, data):
        req_data = struct.pack('<3sB', command, data) + b'\n'
        # print(f"Sending to AC Arduino: {req_data}")
        try:
            bytes_written = self.connDevice.write(req_data)
            # print(f"Bytes written: {bytes_written}")
            self.connDevice.flush()
            # print("Data flushed")
            
            time.sleep(0.1)
            if self.connDevice.in_waiting:
                response = self.connDevice.readline().decode().strip()
                # print(f"Response from AC Arduino: {response}")
            else:
                print("No immediate response from AC Arduino")
        except Exception as e:
            print(f"Error in sendBinary: {e}")

    def sendHeater(self, command, data):  
        req_data = struct.pack('<3sB', command, data) + b'\n'
        print(f"Sending to Heater Arduino: {req_data}")
        try:
            bytes_written = self.connHeater.write(req_data) 
            # print(f"Bytes written: {bytes_written}")
            self.connHeater.flush()
            # print("Data flushed")
            
            time.sleep(0.1)
            if self.connHeater.in_waiting:
                response = self.connHeater.readline().decode().strip()
                # print(f"Response from Heater Arduino: {response}")
            else:
                print("No immediate response from Heater Arduino")
        except Exception as e:
            print(f"Error in sendHeater: {e}")

    def update_ac_status(self, message):
        # print(f"Updating AC status: {message}")
        if message == "AC ON":
            self.controlBtn_AC_toggle.setText('ON')
            self.controlBtn_AC_toggle.setStyleSheet("background-color: rgb(255, 255, 255);")
            self.ac_on = True
            if self.last_real_temperature is not None:
                self.simulated_temperature = self.last_real_temperature  # AC를 켤 때 마지막 실제 온도로 초기화
        elif message == "AC OFF":
            self.controlBtn_AC_toggle.setText('OFF')
            self.controlBtn_AC_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
            self.acIT_on = False
    
    def update_sensor_data(self, humidity, temperature):
    
        self.lcdHumidity.display(humidity)
        self.last_real_temperature = temperature  # 실제 온도 저장
        
        if self.simulated_temperature is None:
            self.simulated_temperature = temperature  # 첫 번째 온도 데이터로 초기화

        if not self.ac_on and not self.heater_on:
            temp_diff = self.last_real_temperature - self.simulated_temperature
            if abs(temp_diff) < 0.1:
                self.simulated_temperature = self.last_real_temperature
            elif temp_diff > 0:
                self.simulated_temperature = min(self.last_real_temperature, self.simulated_temperature + 0.5)
            else:
                self.simulated_temperature = max(self.last_real_temperature, self.simulated_temperature - 0.5)  # 에어컨과 히터가 둘다 꺼져있으면 실제온도로 가져옴

        self.lcdTemp.display(self.simulated_temperature)
        # print(f"Updated sensor data: Humidity={humidity}, Real Temperature={temperature}, Simulated Temperature={self.simulated_temperature:.1f}")
    
    def update_temperature(self):
        if self.simulated_temperature is None or self.last_real_temperature is None:
            return

        if self.ac_on:
            temp_diff = self.simulated_temperature - self.set_temperature
            
            if temp_diff > 2:
                self.simulated_temperature -= 1.0
                self.sendAC(b'SAC', 1)  # POWER
                # print("AC mode: POWER")
            elif 1 < temp_diff <= 2:
                self.simulated_temperature -= 0.6
                self.sendAC(b'SAC', 2)  # HIGH
                # print("AC mode: HIGH")
            elif 0 < temp_diff <= 1:
                self.simulated_temperature -= 0.2
                # self.sendAC(b'SAC', 3)  #
                self.sendAC(b'SAC', 3)  # MIDDLE
                # print("AC mode: MIDDLE")
            else:  # temp_diff <= 0
                self.sendAC(b'SAC', 4)  # LOW
                # print("AC mode: LOW")
            
            # 최소 온도 제한
            self.simulated_temperature = max(18.0, self.simulated_temperature)
        elif self.heater_on:
            temp_diff = self.set_temperature - self.simulated_temperature
            
            if temp_diff > 2:
                self.simulated_temperature += 1.0
                self.sendHeater(b'SHT', 4)  # POWER
                # print("Heater mode: POWER")
            elif 1 < temp_diff <= 2:
                self.simulated_temperature += 0.6
                self.sendHeater(b'SHT', 3)  # HIGH
                # print("Heater mode: HIGH")
            elif 0 < temp_diff <= 1:
                self.simulated_temperature += 0.2
                self.sendHeater(b'SHT', 2)  # MIDDLE
                # print("Heater mode: MIDDLE")
            else:  # temp_diff <= 0
                self.sendHeater(b'SHT', 1)  # LOW
                # print("Heater mode: LOW")
            # 최대 온도 제한
            self.simulated_temperature = min(30.0, self.simulated_temperature)
        else:
            # 에어컨과 히터가 꺼져 있을 때, 실제 온도로 천천히 수렴
            temp_diff = self.last_real_temperature - self.simulated_temperature
            if abs(temp_diff) < 0.1:
                self.simulated_temperature = self.last_real_temperature
            elif temp_diff > 0:
                self.simulated_temperature = min(self.last_real_temperature, self.simulated_temperature + 0.5)
            else:
                self.simulated_temperature = max(self.last_real_temperature, self.simulated_temperature - 0.5)
            self.sendAC(b'SAC', 0)  # AC OFF
            self.sendHeater(b'SHT',0) # HT OFF
        self.lcdTemp.display(round(self.simulated_temperature, 1))
        # print(f"Updated simulated temperature: {self.simulated_temperature:.1f}")
    
    def control_Dehum_toggle(self):
        if self.controlBtn_Dehum_toggle.text() == 'ON':
            self.controlBtn_Dehum_toggle.setText('OFF')
            self.controlBtn_Dehum_toggle.setStyleSheet("background-color: rgb(255, 255, 255);")
            self.sendByte(b'SHM', 0) # 0을 보내면 문을 닫기
        else:
            self.controlBtn_Dehum_toggle.setText('ON')
            self.controlBtn_Dehum_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")
            self.sendByte(b'SHM', 1) # 1을 보내면 문을 열기
        return
    
    def control_Light_toggle(self):
        if self.controlBtn_Light_toggle.text() == 'ON':
            self.controlBtn_Light_toggle.setText('OFF')
            self.controlBtn_Light_toggle.setStyleSheet("background-color: rgb(255, 255, 255);")
            self.sendByte(b'SLI', 0) # 0을 보내면 불 끄기
        else:
            self.controlBtn_Light_toggle.setText('ON')
            self.controlBtn_Light_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")
            self.sendByte(b'SLI', 1) # 1을 보내면 불 켜기
    
    def control_Blind_toggle(self):
        if self.controlBtn_Blind_toggle.text() == 'Open':
            self.controlBtn_Blind_toggle.setText('Close')
            self.controlBtn_Blind_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
            self.sendByte(b'SBM', 0) # 0을 보내면 블라인드 닫기
        else:
            self.controlBtn_Blind_toggle.setText('Open')
            self.controlBtn_Blind_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")
            self.sendByte(b'SBM', 1) # 1을 보내면 블라인드 열기
    
    def control_Door_toggle(self):
        if self.controlBtn_Door_toggle.text() == 'Open':
            self.controlBtn_Door_toggle.setText('Close')
            self.controlBtn_Door_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
            self.sendByte(b'SDM', 0) # 0을 보내면 문 닫기
        else:
            self.controlBtn_Door_toggle.setText('Open')
            self.controlBtn_Door_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")
            self.sendByte(b'SDM', 1) # 1을 보내면 문 열기
        return

    def sendByte(self, command, data=0):
        if command in [b'SAC', b'SHM', b'SLI', b'SBM', b'SDM', b'SBU']:
            req_data = struct.pack('<3sB', command, data) + b'\n'
            # print("sendByte: ", req_data)
            self.connDevice.write(req_data)
        return
     
    def load_scheduled_times_from_table(self):
        """Load scheduled times from the table into self.scheduled_times."""
        self.scheduled_times.clear()  # Clear any existing scheduled times

        row_count = self.Alarm_tableWidget.rowCount()
        for row in range(row_count):
            day_item = self.Alarm_tableWidget.item(row, 0)
            time_item = self.Alarm_tableWidget.item(row, 1)
            action_item = self.Alarm_tableWidget.item(row, 2)

            if day_item and time_item and action_item:
                day = day_item.text()
                time_str = time_item.text()
                action = action_item.text()

                self.scheduled_times.append({
                    "day": day,
                    "time": time_str,
                    "action": action
                })
                # print(f"Loaded configuration for {day} at {time_str} with action '{action}'")

    def update_time(self):
        current_time = QDateTime.currentDateTime()

        current_day = current_time.toString("dddd")
        current_time_str = current_time.toString("HH:mm:ss")
        current_seconds = current_time.time().second()
        remaining_seconds = 60 - current_seconds
        # print(f"Current Day: {current_day}, Time: {current_time_str}, Seconds: {current_seconds}")
        # print(f"Seconds until the next full minute: {remaining_seconds}")

        self.check_time_and_execute(current_day, current_time.toString("HH:mm"))

        # 1분이 지나면 count를 0으로 초기화
        if current_seconds == 0:
            for schedule in self.scheduled_times:
                schedule["count"] = 0

    def check_time_and_execute(self, current_day, current_time_only):
        # 요일을 영어로 변환, 변환하지 않으면 현재요일 == 스케줄요일 비교 시 문제 발생
        day_translation = {
            "월요일": "Monday",
            "화요일": "Tuesday",
            "수요일": "Wednesday",
            "목요일": "Thursday",
            "금요일": "Friday",
            "토요일": "Saturday",
            "일요일": "Sunday"
        }
        current_day_english = day_translation.get(current_day, current_day)

        for schedule in self.scheduled_times:
            # 'action' 키가 존재하는지 확인
            if 'action' not in schedule:
                # print(f"[DEBUG] Error: 'action' key is missing in schedule {schedule}. Skipping...")
                continue
            # 'count' 키가 없는 경우 초기화
            if 'count' not in schedule:
                schedule['count'] = 0
            
            # 공백 제거 및 소문자로 변환하여 비교
            scheduled_day = schedule['day'].strip().lower()
            current_day_clean = current_day_english.strip().lower()
            scheduled_time = schedule['time'].strip()
            current_time_clean = current_time_only.strip()
            
            if scheduled_day == current_day_clean and scheduled_time == current_time_clean:
                if schedule["count"] == 0:  # 현재 카운트가 0일 때만 실행, 1분에 한 번만 실행 
                    # print(f"[DEBUG] Match found! Executing action '{schedule['action']}'")
                    self.schedule_execute(schedule)
                    schedule["count"] += 1  # 카운트 증가
                break

    def setup_alarm_table(self):
        self.Alarm_tableWidget.setColumnCount(6)
        self.Alarm_tableWidget.setHorizontalHeaderLabels(["Day", "Time", "Action", "Light", "Blind", "Alarm"])
        self.Alarm_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # print("Alarm table initialized")

    def toggle_button_state(self, button):
        if self.button_states[button]:
            self.button_states[button] = False
            button.setStyleSheet("background-color: rgb(255, 255, 255);")
        else:
            self.button_states[button] = True
            button.setStyleSheet("background-color: rgb(0, 150, 0);")

    def update_day_selection(self):
        selected_option = self.IndoorCombo_Select.currentText()
        if selected_option == 'Weekday':
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                button = self.weekday_buttons[day]
                self.button_states[button] = True
                button.setStyleSheet("background-color: rgb(0, 150, 0);")  # Green
            for day in ["Saturday", "Sunday"]:
                button = self.weekday_buttons[day]
                self.button_states[button] = False
                button.setStyleSheet("background-color: rgb(255, 255, 255);")  # White
        elif selected_option == 'Weekend':
            for day in ["Saturday", "Sunday"]:
                button = self.weekday_buttons[day]
                self.button_states[button] = True
                button.setStyleSheet("background-color: rgb(0, 150, 0);")  # Green
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                button = self.weekday_buttons[day]
                self.button_states[button] = False
                button.setStyleSheet("background-color: rgb(255, 255, 255);")  # White

    def schedule_execute(self, schedule):
        action = schedule.get("action")
        # print(f"Executing action: {action}")
        
        light_status = schedule.get("light", "OFF")
        blind_status = schedule.get("blind", "Closed")
        alarm_status = schedule.get("alarm", "OFF")

        if light_status == "ON":
            self.sendByte(b'SLI', 1)  # Light ON
        else:
            self.sendByte(b'SLI', 0)  # Light OFF

        if blind_status == "Open":
            self.sendByte(b'SBM', 1)  # Blind Open
        else:
            self.sendByte(b'SBM', 0)  # Blind Closed

        if alarm_status == "ON":
            self.sendByte(b'SBU', 1)  # Alarm ON
            QTimer.singleShot(2000, lambda: self.sendByte(b'SBU', 0))  # 2초 후 Alarm OFF
        else:
            self.sendByte(b'SBU', 0)  # Alarm OFF

    def save_configuration(self, day):
        selected_days = []
        
        for day, button in self.weekday_buttons.items():
            if self.button_states[button]: 
                selected_days.append(day)

        # Get the scheduled time and status of Light, Blind, and Alarm
        scheduled_time = self.IndoorTime_Wakeup_2.time().toString("HH:mm")
        wakeup_light_status = "ON" if self.button_states[self.IndoorBtn_Wakeup_Light] else "OFF"
        wakeup_blind_status = "Open" if self.button_states[self.IndoorBtn_Wakeup_Blind] else "Closed"
        wakeup_alarm_status = "ON" if self.button_states[self.IndoorBtn_Wakeup_Alarm] else "OFF"

        for day in selected_days:
            # Remove any existing entry for the same day in the table
            for row in range(self.Alarm_tableWidget.rowCount()):
                if self.Alarm_tableWidget.item(row, 0).text() == day:
                    self.Alarm_tableWidget.removeRow(row)
                    break  # Exit after removing the row to prevent issues with row indices

            # Remove any existing entry for the same day in the scheduled_times list
            self.scheduled_times = [entry for entry in self.scheduled_times if entry["day"] != day]

            # Add the new configuration to the scheduled_times list and table
            self.scheduled_times.append({
                "day": day,
                "time": scheduled_time,
                "action": "Wakeup",
                "light": wakeup_light_status,
                "blind": wakeup_blind_status,
                "alarm": wakeup_alarm_status
            })

            # Add a new row to the table with the updated configuration
            row_position = self.Alarm_tableWidget.rowCount()
            self.Alarm_tableWidget.insertRow(row_position)
            self.Alarm_tableWidget.setItem(row_position, 0, QTableWidgetItem(day))
            self.Alarm_tableWidget.setItem(row_position, 1, QTableWidgetItem(scheduled_time))
            self.Alarm_tableWidget.setItem(row_position, 2, QTableWidgetItem("Wakeup"))
            self.Alarm_tableWidget.setItem(row_position, 3, QTableWidgetItem(wakeup_light_status))
            self.Alarm_tableWidget.setItem(row_position, 4, QTableWidgetItem(wakeup_blind_status))
            self.Alarm_tableWidget.setItem(row_position, 5, QTableWidgetItem(wakeup_alarm_status))
        
        self.sort_table_by_days()

    def sort_table_by_days(self):
        custom_order = {
            "Saturday": 0,
            "Sunday": 1,
            "Monday": 2,
            "Tuesday": 3,
            "Wednesday": 4,
            "Thursday": 5,
            "Friday": 6
        }
        rows = []

        for row in range(self.Alarm_tableWidget.rowCount()):
            day_item = self.Alarm_tableWidget.item(row, 0)
            if day_item:  # Ensure the day item exists
                day = day_item.text()
                order = custom_order.get(day, 7)  # Get the order from the custom_order dictionary
                row_data = [self.Alarm_tableWidget.item(row, col).text() for col in range(self.Alarm_tableWidget.columnCount())]
                rows.append((order, row_data))

        rows.sort(key=lambda x: x[0])

        # 초기화 후 정렬된 데이터로 테이블 채우기
        self.Alarm_tableWidget.setRowCount(0)
        for _, row_data in rows:
            row_position = self.Alarm_tableWidget.rowCount()
            self.Alarm_tableWidget.insertRow(row_position)
            for col, data in enumerate(row_data):
                self.Alarm_tableWidget.setItem(row_position, col, QTableWidgetItem(data))

    def stop(self):
        self.is_running = False
        self.wait()
        self.connEnv.close()
        self.connDevice.close()

class Receiver(QThread):
    update_signal = pyqtSignal(int, int)
    ac_status_signal = pyqtSignal(str)
    detectedTag = pyqtSignal(bytes)
    recvUID = pyqtSignal(int)
    unDetectedTag = pyqtSignal(int)
    detectedDoor = pyqtSignal(int)
    detectedCard = pyqtSignal(int)
    lightSensorValueReceived = pyqtSignal(int)


    def __init__(self, connEnv, connDevice, parent=None):
        super(Receiver, self).__init__(parent)
        self.is_running = False
        self.connEnv = connEnv
        self.connDevice = connDevice

    def run(self):
        self.is_running = True
        while (self.is_running == True):
            if self.connEnv.readable():
                res = self.connEnv.read_until(b'\n')
                if len(res) > 0:
                    print("res data = ", res)
                    res2 = res
                    res = res[:-2]
                    cmd = res[:3].decode()                    
                    if cmd == 'GST' and res[3] == 0:
                        # print('return_GST')
                        self.detectedTag.emit(res[4:]) #UID 부터 
                    elif cmd == 'GST' and res[3] == 1:
                        # print('return_GST', res)
                        self.unDetectedTag.emit(res[4])       
                    elif cmd == 'SID' and res[3] == 0:
                        # print('return_SID')
                        pass
                    elif cmd == 'GDS':
                        # print('return_GDS')
                        self.detectedDoor.emit(res[3]) #sensor 값만
                    elif cmd == 'GCS':
                        # print('return_GCS')
                        self.detectedCard.emit(res[3]) #sensor 값만
                    elif cmd == 'GLI':                      # merge Light_Dark_mode.py
                        # print('return_GLI')                 # merge Light_Dark_mode.py
                        self.lightSensorValueReceived.emit(res[3]) # merge Light_Dark_mode.py
                    elif cmd == 'GTH':
                        # print('return_GDS')
                        self.update_signal.emit(res[4], res[3]) #sensor 값만
                else:
                    # self.unDetected.emit()
                    pass

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
