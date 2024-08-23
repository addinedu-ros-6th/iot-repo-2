# include <Arduino.h>

const int buzzerPin = 8; // 부저가 연결된 핀

void setup() {
  Serial.begin(9600);
  pinMode(buzzerPin, OUTPUT); // 부저 핀을 출력으로 설정
}

void loop() {
  if (Serial.available() > 0) {
    char recv_buffer[5] = {0}; // 시리얼 버퍼 초기화
    int recv_size = Serial.readBytesUntil('\n', recv_buffer, 4);

    if (recv_size == 4) {
      char cmd[4] = {0};  // cmd 초기화 및 Null-terminator 추가
      memcpy(cmd, recv_buffer, 3);
      byte value = recv_buffer[3]; // 네 번째 바이트는 명령 값 (0 또는 1)

      // 부저 제어
      if (strncmp(cmd, "SBU", 3) == 0 && (value == 0 || value == 1)) {
        if (value == 1) {
          Serial.println("SBU");
          tone(buzzerPin, 1000); // 1kHz 톤 발생 (부저 켜기)
        } else if (value == 0) {
          Serial.println("SBU");
          noTone(buzzerPin); // 부저 끄기
        }
      }
    }
  }
}
