import sys
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import PyQt5
import serial
import struct
import mysql.connector
import time
from datetime import datetime

mydb = mysql.connector.connect(
            host = "database-1.cpog6osggiv3.ap-northeast-2.rds.amazonaws.com",
            user = "arduino_PJT",
            password = "1234",
            database = "ardumension"
            )

from_class = uic.loadUiType("/home/sh/dev_ws/PJT/Arduino/GUI_v7.ui")[0]

# merge Blind_GUI.py
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    PyQt5.QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    PyQt5.QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

class WindowClass(QMainWindow, from_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.uidList = []
        self.prevLcdValue = 9
        self.cur = mydb.cursor(buffered=True)
        self.cycleTime = 500
        self.doorStatus = False # false : closed / true : opended
        self.LEDcount = 0 # merge Light_Dark_mode.py
        self.Blindcount = 0 
           
        self.activationStatus = False
        self.connSensorReader = serial.Serial(port='/dev/ttyACM2', baudrate= 9600, timeout= 1)
        self.connHeaterController = serial.Serial(port='/dev/ttyACM1', baudrate= 9600, timeout= 1)
        self.connHomeItemController = serial.Serial(port='/dev/ttyACM0', baudrate= 9600, timeout= 1)
        self.recv = Receiver(self.connSensorReader)
        self.recv.start()

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

    #Dehumidifier_GUI.py
        self.controlBtn_Dehum_toggle.clicked.connect(self.control_Dehum_toggle)
        self.controlBtn_Dehum_toggle.setText('OFF')
        self.controlBtn_Dehum_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
    # merge Blind_GUI.py   
        self.controlBtn_Blind_toggle.clicked.connect(self.control_Blind_toggle)
        self.controlBtn_Blind_toggle.setText('Open')
        self.controlBtn_Blind_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")


        self.timer = QTimer()
        self.timer.setInterval(self.cycleTime)
        self.timer.timeout.connect(self.getStatus)
        self.timer.start()


    #Dehumidifier_GUI.py
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
    
    # merge Blind_GUI.py
    def control_Blind_toggle(self):
        if self.controlBtn_Blind_toggle.text() == 'Open':
            self.controlBtn_Blind_toggle.setText('Close')
            self.controlBtn_Blind_toggle.setStyleSheet("background-color: rgb(200, 0, 0);")
            self.sendHomeItemController(b'SBM', 0) # 0을 보내면 블라인드를 닫기
        else:
            self.controlBtn_Blind_toggle.setText('Open')
            self.controlBtn_Blind_toggle.setStyleSheet("background-color: rgb(0, 150, 0);")
            self.sendHomeItemController(b'SBM', 1) # 1을 보내면 블라인드를 열기

    # merge Light_Dark_mode.py
    def onLightSensorValueReceived(self, value):
        print(f"Light Sensor Value: {value}")
        print(f"LEDcount: {self.LEDcount}")
        print(f"BlindCount : {self.Blindcount}")
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
        time.sleep(0.05)
        return
    
    def detectedDoor(self, value):
        # print("")          
        if (value == 1 and self.prevLcdValue != 1): 
            self.sendDisplayController(b'SLC',2)    # door close
            self.doorStatus = False  
            time.sleep(1)       
            self.sendHomeItemController(b'SDM',0) 
            self.sendDisplayController(b'SLC',3)   
        elif (value == 0 and self.prevLcdValue != 0): 
            self.sendDisplayController(b'SLC',1)    # door open
            self.doorStatus = True
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
        self.connSensorReader.write(set_data)
        # print("sendSensorReader = ", set_data)
        return

    def sendDisplayController(self, command, data = 0):
        set_data = struct.pack('<3sBc', command, data, b'\n')
        self.connHeaterController.write(set_data)
        # print("sendDisplayController = ", set_data)
        return
    
    def sendHomeItemController(self, command, data = 0):
        set_data = struct.pack('<3sBc', command, data, b'\n')
        self.connHomeItemController.write(set_data)  ################conn 컨트롤러 변경 필요
        print("sendHomeItemController = ", set_data)
        return

class Receiver(QThread):
    detectedTag = pyqtSignal(bytes)
    recvUID = pyqtSignal(int)
    unDetectedTag = pyqtSignal(int)
    detectedDoor = pyqtSignal(int)
    detectedCard = pyqtSignal(int)
    lightSensorValueReceived = pyqtSignal(int)

    def __init__(self, conn, parent=None):
        super(Receiver, self).__init__(parent)
        self.is_running = False
        self.conn = conn
        # print("recv init")

    def run(self):
        # print("recv start")
        self.is_running = True
        while (self.is_running == True):
            if self.conn.readable():
                res = self.conn.read_until(b'\n')
                if len(res) > 0:
                    # print("res data = ", res)
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
                        self.lightSensorValueReceived.emit(int(res[3])) # merge Light_Dark_mode.py
                else:
                    # self.unDetected.emit()
                    pass

                
                
    def stop(self):
        # print("recv stop")
        self.is_running = False


if __name__=="__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()    
    sys.exit(app.exec_()) 
    mydb.close()