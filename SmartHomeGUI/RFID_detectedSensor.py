import sys
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
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

class WindowClass(QMainWindow, from_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.uidList = []
        self.prevLcdValue = 9
        self.cur = mydb.cursor(buffered=True)
        self.cycleTime = 500
           
        self.activationStatus = False
        self.connSensorReader = serial.Serial(port='/dev/ttyACM0', baudrate= 9600, timeout= 1)
        self.connHeaterController = serial.Serial(port='/dev/ttyACM1', baudrate= 9600, timeout= 1)
        self.recv = Receiver(self.connSensorReader)
        self.recv.start()

        self.GetUidFromDB()

        self.recv.detectedTag.connect(self.detectedTag) #tag 감지 신호
        self.recv.unDetectedTag.connect(self.unDetectedTag) #tag 미감지 신호
        self.recv.detectedDoor.connect(self.detectedDoor) #도어 센서 감지 신호
        self.recv.detectedCard.connect(self.detectedCard) #카드 센서 감지 신호

        self.RegistrationBtn_Activation.setCheckable(True)
        self.RegistrationBtn_Activation.clicked.connect(self.Activation) #UID 등록하기 위한 버튼
        self.RegistrationLine_UID.textChanged.connect(self.uidText) #등록할 UID 입력 시 
        self.RegistrationBtn_Register.clicked.connect(self.Register) #CARD에 UID, Name 등록하기 버튼
        self.Registration_Table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) #등록창 넓이 조절
        self.RegistrationBtn_Remove.clicked.connect(self.uidDelete)

        self.timer = QTimer()
        self.timer.setInterval(self.cycleTime)
        self.timer.timeout.connect(self.getStatus)
        self.timer.start()

    def getStatus(self):
        print("")
        self.sendSensorReader(b'GST')
        time.sleep(0.05)
        self.sendSensorReader(b'GDS')
        time.sleep(0.05)
        self.sendSensorReader(b'GCS')
        return
    
    def detectedDoor(self, value):
        print("")  
        if (value == 1 and self.prevLcdValue != 1):
            self.sendDisplayController(b'SLC',2)  
        elif (value == 0 and self.prevLcdValue != 0):
            self.sendDisplayController(b'SLC',1)    
        self.prevLcdValue = value  
        return
    
    def detectedCard(self, value):
        print("")  
        if value == 1:
            self.Current_mode.setText("INDOOR")
            self.Current_mode.setStyleSheet("background-color : lightgreen")
        elif value == 0:
            self.Current_mode.setText("OUTDOOR")
            self.Current_mode.setStyleSheet("background-color : red")    
        return
    
    
    def detectedTag(self, uid):
        print("detected Tag")
        self.getUid = uid.decode('utf-8')
        self.RegistrationBtn_Register.setStyleSheet("background-color : lightgreen")
        self.judge()
    
    def judge(self):
        for i in range(len(self.uidList)):
            if self.getUid == self.uidList[i]: #현재는 무조건 8자를 입력해야 인식
                self.sendDisplayController(b'SLC',0)
            else:
                self.sendDisplayController(b'SLC',4)

    def uidDelete(self):
        row = self.Registration_Table.currentRow() #선택한 아이템이 몇번째 row인지 저장
        uid = self.Registration_Table.item(row,1).text() #username
        self.Registration_Table.removeRow(row)
        print(uid)
        sql = f"delete from RFID where RFID = '{uid}';"
        print(sql)
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
        print("sendSensorReader = ", set_data)
        return

    def sendDisplayController(self, command, data = 0):
        set_data = struct.pack('<3sBc', command, data, b'\n')
        self.connHeaterController.write(set_data)
        print("sendDisplayController = ", set_data)
        return
    

class Receiver(QThread):
    detectedTag = pyqtSignal(bytes)
    recvUID = pyqtSignal(int)
    unDetectedTag = pyqtSignal(int)
    detectedDoor = pyqtSignal(int)
    detectedCard = pyqtSignal(int)

    def __init__(self, conn, parent=None):
        super(Receiver, self).__init__(parent)
        self.is_running = False
        self.conn = conn
        print("recv init")

    def run(self):
        print("recv start")
        self.is_running = True
        while (self.is_running == True):
            if self.conn.readable():
                res = self.conn.read_until(b'\n')
                if len(res) > 0:
                    print("res data = ", res)
                    res = res[:-2]
                    cmd = res[:3].decode()                    
                    if cmd == 'GST' and res[3] == 0:
                        print('return_GST')
                        self.detectedTag.emit(res[4:]) #UID 부터 
                    elif cmd == 'GST' and res[3] == 1:
                        print('return_GST', res)
                        self.unDetectedTag.emit(res[4])       
                    elif cmd == 'SID' and res[3] == 0:
                        print('return_SID')
                    elif cmd == 'GDS':
                        print('return_GDS')
                        self.detectedDoor.emit(res[4]) #sensor 값만
                    elif cmd == 'GDS':
                        print('return_GDS')
                        self.detectedCard.emit(res[4]) #sensor 값만
                else:
                    # self.unDetected.emit()
                    pass

                
                
    def stop(self):
        print("recv stop")
        self.is_running = False


if __name__=="__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()    
    sys.exit(app.exec_()) 
    mydb.close()