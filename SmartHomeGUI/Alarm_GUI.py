import sys
import serial
import struct
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
import PyQt5

from_class = uic.loadUiType("./IOT_Project_2/GUI/GUI_v8.ui")[0]

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    PyQt5.QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    PyQt5.QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

class MainWindow(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        time.sleep(1)
        
        # self.conn = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
        self.conn = serial.Serial(port='com3', baudrate=9600, timeout=1)
        self.recv = Receiver(self.conn)
        self.recv.doorActionExecuted.connect(self.onDoorActionExecuted)
        self.recv.start()
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
        
        # 요일 버튼에 대한 이벤트 연결
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
        
        # 타이머 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(5000)  # 2초마다 타이머가 동작

        # 사용자 설정 시간 저장
        self.scheduled_times = []
        self.setup_alarm_table()
        self.load_scheduled_times_from_table()
    
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
                print(f"Loaded configuration for {day} at {time_str} with action '{action}'")

    def update_time(self):
        current_time = QDateTime.currentDateTime()

        current_day = current_time.toString("dddd")
        current_time_str = current_time.toString("HH:mm:ss")
        current_seconds = current_time.time().second()
        remaining_seconds = 60 - current_seconds
        print(f"Current Day: {current_day}, Time: {current_time_str}, Seconds: {current_seconds}")
        print(f"Seconds until the next full minute: {remaining_seconds}")

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

        # 디버깅: 예약된 작업을 확인
        print(f"[DEBUG] Checking scheduled actions for {current_day} at {current_time_only}...")

        for schedule in self.scheduled_times:
            # 방어 코드: 'action' 키가 존재하는지 확인
            if 'action' not in schedule:
                print(f"[DEBUG] Error: 'action' key is missing in schedule {schedule}. Skipping...")
                continue

            # 'count' 키가 없는 경우 초기화
            if 'count' not in schedule:
                schedule['count'] = 0

            print(f"[DEBUG] Comparing '{schedule['day']}' with '{current_day}' and '{schedule['time']}' with '{current_time_only}'")
            
            # 공백 제거 및 소문자로 변환하여 비교
            scheduled_day = schedule['day'].strip().lower()
            current_day_clean = current_day_english.strip().lower()
            scheduled_time = schedule['time'].strip()
            current_time_clean = current_time_only.strip()
            
            if scheduled_day == current_day_clean and scheduled_time == current_time_clean:
                if schedule["count"] == 0:  # 현재 카운트가 0일 때만 실행
                    print(f"[DEBUG] Match found! Executing action '{schedule['action']}'")
                    self.execute_action(schedule)
                    schedule["count"] += 1  # 카운트 증가
                break
            else:
                print(f"[DEBUG] No match: {scheduled_day} != {current_day_clean} or {scheduled_time} != {current_time_clean}")
        else:
            print(f"[DEBUG] No matching scheduled actions found.")

    def execute_action(self, schedule):
        action = schedule.get("action")
        print(f"Executing action: {action}")
        
        # Light, Blind, Alarm 상태에 따른 동작 수행
        light_status = schedule.get("light", "OFF")
        blind_status = schedule.get("blind", "Closed")
        alarm_status = schedule.get("alarm", "OFF")

        if light_status == "ON":
            self.sendByte(b'SLI', 1)  # Light ON
            print(f"Light is ON")
        else:
            self.sendByte(b'SLI', 0)  # Light OFF
            print(f"Light is OFF")

        if blind_status == "Open":
            self.sendByte(b'SBM', 1)  # Blind Open
            print(f"Blind is Open")
        else:
            self.sendByte(b'SBM', 0)  # Blind Closed
            print(f"Blind is Closed")

        if alarm_status == "ON":
            self.sendByte(b'SBU', 1)  # Alarm ON
            print(f"Alarm is ON")
            # QTimer.singleShot(2000, lambda: self.sendByte(b'SBU', 0))  # 3초 후 Alarm OFF
        else:
            self.sendByte(b'SBU', 0)  # Alarm OFF
            print(f"Alarm is OFF")

    def sendByte(self, command, data=0):
        req_data = struct.pack('<3sB', command, data) + b'\n'
        print("sendByte: ", req_data)
        self.conn.write(req_data)

    def setup_alarm_table(self):
        self.Alarm_tableWidget.setColumnCount(6)
        self.Alarm_tableWidget.setHorizontalHeaderLabels(["Day", "Time", "Action", "Light", "Blind", "Alarm"])
        self.Alarm_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        print("Alarm table initialized")

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

    def save_configuration(self, day):
        selected_days = []
        
        for day, button in self.weekday_buttons.items():
            if self.button_states[button]:  # Process only selected days
                selected_days.append(day)
                # print(f"Selected day: {day}")

        # Get the scheduled time and status of Light, Blind, and Alarm
        scheduled_time = self.IndoorTime_Wakeup_2.time().toString("HH:mm")
        wakeup_light_status = "ON" if self.button_states[self.IndoorBtn_Wakeup_Light] else "OFF"
        wakeup_blind_status = "Open" if self.button_states[self.IndoorBtn_Wakeup_Blind] else "Closed"
        wakeup_alarm_status = "ON" if self.button_states[self.IndoorBtn_Wakeup_Alarm] else "OFF"

        # Process each selected day
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
            # print(f"Added row for day={day}, Time={scheduled_time}, Light={wakeup_light_status}, Blind={wakeup_blind_status}, Alarm={wakeup_alarm_status}")
        
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
        # Create a list to hold the rows with their day and corresponding sort order
        rows = []

        # Extract the relevant data from each row
        for row in range(self.Alarm_tableWidget.rowCount()):
            day_item = self.Alarm_tableWidget.item(row, 0)
            if day_item:  # Ensure the day item exists
                day = day_item.text()
                order = custom_order.get(day, 7)  # Get the order from the custom_order dictionary
                row_data = [self.Alarm_tableWidget.item(row, col).text() for col in range(self.Alarm_tableWidget.columnCount())]
                rows.append((order, row_data))

        # Sort rows by the custom order
        rows.sort(key=lambda x: x[0])

        # Clear the table and reinsert rows in the sorted order
        self.Alarm_tableWidget.setRowCount(0)
        for _, row_data in rows:
            row_position = self.Alarm_tableWidget.rowCount()
            self.Alarm_tableWidget.insertRow(row_position)
            for col, data in enumerate(row_data):
                self.Alarm_tableWidget.setItem(row_position, col, QTableWidgetItem(data))

    def onDoorActionExecuted(self, message):
        print(message)  # "Door opened" 또는 "Door closed" 메시지를 출력

class Receiver(QThread):
    doorActionExecuted = pyqtSignal(str)  # 문이 열리거나 닫혔을 때의 신호

    def __init__(self, conn, parent=None):
        super(Receiver, self).__init__(parent)
        self.is_running = False
        self.conn = conn

    def run(self):
        self.is_running = True
        while self.is_running:
            if self.conn.readable():
                res = self.conn.read_until(b'\n') # 개행 문자가 나올 때까지 데이터 수신
                if len(res) > 0:
                    res = res.decode().strip()  # 수신된 데이터를 디코딩하고 공백 제거
                    cmd = res[:3]  # 첫 세 문자를 명령으로 인식
                    if cmd == 'SBU':
                        action = int(res[3])  # 네 번째 문자가 동작 값 (0 또는 1)
                        if action == 1:
                            self.doorActionExecuted.emit("SBU: Alarm ON")
                        elif action == 0:
                            self.doorActionExecuted.emit("SBU: Alarm OFF")
                    elif cmd == 'SBM':
                        action = int(res[3])
                        if action == 1:
                            self.doorActionExecuted.emit("Blind opened")
                        elif action == 0:
                            self.doorActionExecuted.emit("Blind closed")

    def stop(self):
        self.is_running = False
        self.wait()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
