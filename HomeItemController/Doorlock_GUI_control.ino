#include <Servo.h>

Servo myservo;
int doorLockPos = 130;
int doorOpenedPos = 130;
int doorClosedPos = 80;
int doorLockStatus = 0;

void setup() {
  Serial.begin(9600);
  myservo.attach(7);
  myservo.write(doorLockPos);
}

void loop() {
  if (Serial.available() > 0) {
    char recv_buffer[5] = {0}; // 시리얼 버퍼 초기화
    int recv_size = Serial.readBytesUntil('\n', recv_buffer, 4);

    if (recv_size == 4) {
      char cmd[4] = {0};  // cmd 초기화 및 Null-terminator 추가
      memcpy(cmd, recv_buffer, 3);
      byte value = recv_buffer[3]; // 네 번째 바이트는 명령 값 (0 또는 1)
      if (strncmp(cmd, "SDM", 3) == 0 && (value == 0 || value == 1)) {
        if (value == 1) {  
          Serial.println("SDM1");
          myservo.write(doorOpenedPos); // 문 열기
        } else if (value == 0) { 
          Serial.println("SDM0");
          myservo.write(doorClosedPos); // 문 닫기
        }
      }
    }
  }
}

// void loop() {
//   if (Serial.available() > 0) {
//     String data = Serial.readStringUntil('\n'); // SDM0 or SDM1 문자열을 data에 저장
    
//     char cmd[4] = {0};  // cmd 초기화 및 Null-terminator 추가
//     data.toCharArray(cmd, 4);
//     byte action = data[3];

//     if (strncmp(cmd, "SDM", 3) == 0) {
//       if (action == 1) {
//         myservo.write(doorOpenedPos);
//       } else if (action == 0) {
//         myservo.write(doorClosedPos);
//       }
//     } 
//   }
// }
