int IN1Pin = 3;
int IN2Pin = 4;
int ENPin = 5;

void setup() {
  Serial.begin(9600);
  pinMode(IN1Pin, OUTPUT);
  pinMode(IN2Pin, OUTPUT);
  pinMode(ENPin, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    char recv_buffer[5] = {0}; // 시리얼 버퍼 초기화
    int recv_size = Serial.readBytesUntil('\n', recv_buffer, 4);

    if (recv_size == 4) {
      char cmd[4] = {0};  // Null-terminator 추가 및 초기화
      memcpy(cmd, recv_buffer, 3);
      byte value = recv_buffer[3]; // 네 번째 바이트는 명령 값 (0 또는 1)
      
      if (strncmp(cmd, "SHM", 3) == 0 && (value == 0 || value == 1)) {
        if (value == 1) {
          Serial.println("SHM1");
          analogWrite(ENPin, 100);     // 속도를 200으로 설정 (0~255 범위)
          digitalWrite(IN1Pin, LOW);
          digitalWrite(IN2Pin, HIGH);
        } else if (value == 0) {
          Serial.println("SHM0");
          digitalWrite(IN1Pin, HIGH);
          digitalWrite(IN2Pin, HIGH);
          analogWrite(ENPin, 0);       // 모터 정지
        }
      }
    }
  }
}