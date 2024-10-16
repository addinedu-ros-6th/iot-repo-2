const int buzzerPin = 13; // 부저가 연결된 핀
unsigned long buzzerStartTime = 0; // 부저가 켜진 시간을 저장할 변수
bool buzzerOn = false; // 부저가 켜져 있는지 여부를 추적

void setup() {
  Serial.begin(9600);
  pinMode(buzzerPin, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) 
  {
    char recv_buffer[5] = {0}; // 시리얼 버퍼 초기화
    int recv_size = Serial.readBytesUntil('\n', recv_buffer, 4);

    if (recv_size == 4) 
    {
      char cmd[4] = {0};  // cmd 초기화 및 Null-terminator 추가
      memcpy(cmd, recv_buffer, 3);
      byte value = recv_buffer[3]; // 네 번째 바이트는 명령 값 (0 또는 1)

      // 명령과 값을 디버깅용으로 출력
      Serial.print("Received command: ");
      Serial.print(cmd);
      Serial.print(", value: ");
      Serial.println(value);

      // 부저 제어
      if (strncmp(cmd, "SBU", 3) == 0 && (value == 0 || value == 1)) 
      {
        if (value == 1) 
        {
          Serial.println("SBU1");
          tone(buzzerPin, 50000); // 50kHz 톤 발생 (부저 켜기)
          buzzerStartTime = millis(); // 부저가 켜진 시간을 기록
          buzzerOn = true; // 부저가 켜졌음을 표시
        } else if (value == 0) 
        {
          Serial.println("SBU0");
          noTone(buzzerPin); // 부저 끄기
        }
      }
    }
  }
    // 부저가 켜진 상태에서 2초가 지났는지 확인
  if (buzzerOn && (millis() - buzzerStartTime >= 1000)) 
  {
    noTone(buzzerPin); // 부저 끄기
    buzzerOn = false; // 부저가 꺼졌음을 표시
  }
}
