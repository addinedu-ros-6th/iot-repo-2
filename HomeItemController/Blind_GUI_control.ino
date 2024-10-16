#include <AccelStepper.h>

// 핀 번호 정의 (ULN2003 드라이버 보드에 연결)
#define IN1  8
#define IN2  9
#define IN3  10
#define IN4  11

// 4선 스텝퍼 모터 초기화
AccelStepper stepper(AccelStepper::FULL4WIRE, IN1, IN3, IN2, IN4);

void setup() {
  Serial.begin(9600);
  stepper.setMaxSpeed(500.0);  // 최대 속도 설정 (스텝/초)
  stepper.setAcceleration(500.0);  // 가속도 설정 (스텝/초^2)
  // stepper.setCurrentPosition(0);  // 현재 위치를 0으로 설정, 초기 위치 설정 (옵션)
}

void loop() {
  if (Serial.available() > 0) {
    char recv_buffer[5] = {0}; // 시리얼 버퍼 초기화
    int recv_size = Serial.readBytesUntil('\n', recv_buffer, 4);

    if (recv_size == 4) {
      char cmd[4] = {0};  // Null-terminator 추가 및 초기화
      memcpy(cmd, recv_buffer, 3);
      byte value = recv_buffer[3]; // 네 번째 바이트는 명령 값 (0 또는 1)
      
      if (strncmp(cmd, "SBM", 3) == 0 && (value == 0 || value == 1)) {
        if (value == 1) {
          Serial.println("Opening Blind");
          stepper.moveTo(0);  // 블라인드를 올리기 (0 스텝, 초기 위치 )
        } else if (value == 0) {
          Serial.println("Closing Blind");
          stepper.moveTo(-5500);  // 블라인드를 내리기 (2048 스텝, 한 바퀴 반대 방향)
        }
      }
    }
  }
  stepper.run(); // 스텝퍼 모터를 이동시킴
}
