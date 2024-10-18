# iot-repo-2
IoT 프로젝트 2조 저장소. 스마트홈 자동화 시스템
## 1.주제
다양한 가전제품과 기기를 인터넷에 연결해 사용자가 원격으로 제어하고 자동화 할수 있는 시스템을 구축하는것을 목표

<img src="https://github.com/user-attachments/assets/cfc6e7cd-015c-4695-b0b7-901b68ea8567" width="400"/> <img src="https://github.com/user-attachments/assets/f6dac7f0-b4cc-40b8-abe5-5a32efa9427e" width="420"/>

## 팀원
|이름|담당|
|:---:|:---:|
|이은휘|하드웨어 kit 제작, gui 설계, 모터 gui 제어|
|강지훈|db 설계, 온습도 gui 제어, 에어컨 gui 제어 |
|서성혁(팀장)|system architecture 설계, rfid gui 제어, 근접 센서 gui 제어|
|김정현|순서도 설계 , heater gui 제어, lcd gui 제어|
## 2.활용 기술
|No|Category|Detail|
|:---:|:---:|:---:|
|1|Development Environment|<img src="https://github.com/user-attachments/assets/a44df9af-fb71-4e29-9afe-6e8db0e3581e" alt="Sample Image" width="100" height="30"> <img src="https://github.com/user-attachments/assets/189e5a66-e293-4249-a64e-6adaf69db1dc" alt="Sample Image" width="100" height="30">|
|2|Collaboration Tools|<img src="https://github.com/user-attachments/assets/1b08e141-39dc-43c0-a5f2-27e9f148e0d1" alt="Sample Image" width="100" height="30"> <img src="https://github.com/user-attachments/assets/e058d6ea-48dc-41ac-b22e-27fc6d664f83" alt="Sample Image" width="100" height="30"> ![image](https://github.com/user-attachments/assets/68944b2b-7494-47d2-96ec-433bb8a5dce1) ![image](https://github.com/user-attachments/assets/da51b00b-459e-4327-9120-e185a51024a6)|

## 3.설계
## 3.1 기능리스트
| **Categories**                | **Function**                 | **Description**                                                                                     |
|--------------------------------|------------------------------|-----------------------------------------------------------------------------------------------------|
| **모드 변경**                  | **카드 유무 감지**           | 카드 유무 확인 <br> - 카드가 있으면 집콕모드 전환 <br> - 카드가 없으면 외출모드 전환                           |
| **RFID**                       | **카드 등록**                | Door를 Open할 수 있는 CardKey 등록 또는 제거 기능                                                    |
|                                | **카드 등록정보 확인**       | 사전에 등록된 Card Key 확인 <br> - 등록된 Key일 경우 Door Unlock <br> - 미등록된 Key일 경우 Door Lock        |
| **집콕 모드 / 외출 모드(공통)**      | **실내 온도 제어**           | 현재 온도를 측정하여 Auto로 선택된 기능으로 온도 제어 <br> - Airconditional : setting된 온도에 도달할 때까지 냉방 유지 <br> - Heater : setting된 온도에 도달할 때까지 난방 유지 |
|                                | **실내 습도 제어**           | 현재 습도를 측정하여 습도 제어 <br> - Dehumidifier : setting된 습도에 도달할 때까지 습도 조절                    |
| **외출모드**                   | **조명 제어**                | 실내 밝기를 측정하여 실내 조명 제어 <br> - 외출 모드로 전환 시 Setting된 값으로 조명 ON / OFF                   |
|                                | **커튼 제어**                | 외출 모드로 전환 시 Setting된 값으로 커튼 Open / Close                                               |
|                                | **외출모드 시작 / 종료 타이머** | Timer After Outdoor : 외출모드 전환 후 Auto Mode 시작 시간 <br> Duration : 외출모드 Auto Mode 종료 시간         |
| **집콕모드**                   | **조명 제어**                | 집콕 모드로 전환 시 Setting된 값으로 조명 ON / OFF                                                   |
|                                | **커튼 제어**                | 집콕 모드로 전환 시 Setting된 값으로 커튼 Open / Close                                               |
|                                | **알람**                     | 요일 별 알람 설정 가능 <br> - Wake-up : 설정된 시간에 알람, 조명, 커튼 ON <br> - Sleep : 설정된 시간에 알람, 조명, 커튼 OFF |

## 3.2 시스템 설계
<img src="https://github.com/user-attachments/assets/dfae5500-7ca7-4380-bd09-0aef5aafcf32" alt="Image" width="650" height="500"/>


## 3.3 ui 설계
### 외출모드 설정
![image](https://github.com/user-attachments/assets/bc22fba4-b1a6-41c7-a70d-5254f33ca1e9)
### 집콕모드 설정
![image](https://github.com/user-attachments/assets/3bb57cde-89a6-4948-9eea-0991017ab5fd)
### rfid 등록
![image](https://github.com/user-attachments/assets/c041ad00-81a2-45b8-9cab-eb7c96aa9256)
1. registration 탭으로 이동
2. register btn색상을 통해 rifd tag 상태 확인
3. rfid uid 입력(최대 8글자)
4. user name 입력
5. activation btn 클릭
6. register btn 클릭
### reservation
![image](https://github.com/user-attachments/assets/942d3f39-76f4-4f80-b612-9f9f443e6c45)
![image](https://github.com/user-attachments/assets/f43345dc-7526-4e92-9674-666758f826ad)
1. indoor config 탭으로 이동
2. select day에서 요일 및 시간,기능 선택
3. save configuration 클릭
4. table widget에 해당 기록 확인
## 3.4 DB 설계
![image](https://github.com/user-attachments/assets/a407489b-787e-4dfc-9163-76a0d1823b3a)

## 4 시연 영상
## 4.1 UI 
[Gui.webm](https://github.com/user-attachments/assets/2dbf4d66-cf11-4b51-8525-4fec628cbc3e)

## 4.2 RFID 등록
[card_registration.webm](https://github.com/user-attachments/assets/263e7c94-74c7-4204-8c24-9f12a471a38d)

![Screenshot from 2024-10-18 13-50-07](https://github.com/user-attachments/assets/f1669b0d-7866-4b2b-a56e-a163b538b679)

## 4.3 RFID 태그에 따른 LCD 
[RFID_LCD.webm](https://github.com/user-attachments/assets/b51aedf6-63be-4ffb-a414-0217388a537a)

![Screenshot from 2024-10-17 10-43-07](https://github.com/user-attachments/assets/1c45e409-35c3-4292-9390-5418557302d4)

## 4.4 Door Lock/UnLock
[opendoor.webm](https://github.com/user-attachments/assets/70ab115c-16e1-4c17-8ff8-f1d00c6bf166)

## 4.4 온도에 따른 에어컨 자동제어
[Screencast from 10-16-2024 08:50:18 PM.webm](https://github.com/user-attachments/assets/462d61e4-800e-4cad-8235-b7ac53590f5e)

![image](https://github.com/user-attachments/assets/ba4f3f60-f7ab-4d82-aaf8-11e7362d77d3)


  설정 온도에 근접할수록 led색 변화 와 온도변화폭 감소 

## 4.5 LED 및 커튼 제어

[Screencast from 10-16-2024 08:33:27 PM.webm](https://github.com/user-attachments/assets/f620eb0b-4ae6-4330-9cfe-3d85bd9430a9)

<img src="https://github.com/user-attachments/assets/a774c4df-9bc9-4580-8c07-d5c4d8d3272b" width="650" />

## 4.6 Alarm Reservation 작동

[Alarm 예약 제어.webm](https://github.com/user-attachments/assets/df9e4688-e160-44d6-872c-13818555c36a)
