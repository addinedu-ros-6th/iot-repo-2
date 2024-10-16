# iot-repo-2
IoT 프로젝트 2조 저장소. 스마트홈 자동화 시스템
## 1.주제
다양한 가전제품과 기기를 인터넷에 연결해 사용자가 원격으로 제어하고 자동화 할수 있는 시스템을 구축하는것을 목표
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
## 3.2 시스템 설계
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

## 4.3 RFID 태그에 따른 LCD 

## 4.4 Door Lock/UnLock
[opendoor.webm](https://github.com/user-attachments/assets/70ab115c-16e1-4c17-8ff8-f1d00c6bf166)

## 4.4 온도에 따른 에어컨 자동제어
![GIFMaker_me (10)](https://github.com/user-attachments/assets/c74a62b1-56fb-433c-b0ff-204cdb233e59)
  
  설정 온도에 근접할수록 led색 변화 와 온도변화폭 감소 
## 4.5 커튼 제어
![GIFMaker_me (7)](https://github.com/user-attachments/assets/a5c11cb1-3128-48f1-8dc0-70c39bf23999)


## 4.6 Alarm Reservation 작동
