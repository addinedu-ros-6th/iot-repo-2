#include <AccelStepper.h>
#include <Servo.h>

Servo myservo;
const int ACBlue = A3;
const int ACGREEN = A4;
const int ACRED = A5;
const int doorLockPos = 130;
const int doorOpenedPos = 130;
const int doorClosedPos = 80;
const int LightBlue = 2;
const int LightGREEN = 3;
const int LightRED = 4;
const int ENPin = 5; // DC 모터 드라이버
const int IN2Pin = 6; // DC 모터 드라이버
const int IN1Pin = 7; // DC 모터 드라이버
const int IN1 = 8; // ULN 2003 드라이버
const int IN2 = 9; // ULN 2003 드라이버
const int IN3 = 10; // ULN 2003 드라이버
const int IN4 = 11; // ULN 2003 드라이버
const int buzzerPin = 13;

// 4선 스텝퍼 모터 초기화
AccelStepper stepper(AccelStepper::FULL4WIRE, IN1, IN3, IN2, IN4);

void setup() {
  Serial.begin(9600);
  myservo.attach(12);
  myservo.write(doorLockPos);
  stepper.setMaxSpeed(500.0);  // 최대 속도 설정 (스텝/초)
  stepper.setAcceleration(500.0);  // 가속도 설정 (스텝/초^2)
  pinMode(IN1Pin, OUTPUT);
  pinMode(IN2Pin, OUTPUT);
  pinMode(ENPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
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
      
      if (strncmp(cmd, "SAC", 3) == 0)
      {
        switch(value)
        {
          case 0:
            Serial.println("AC OFF");
            analogWrite(ACRED, 0);
            analogWrite(ACGREEN, 0);
            analogWrite(ACBlue, 0);
            break;
          case 1:
            Serial.println("AC POWER");
            analogWrite(ACRED, 255);
            analogWrite(ACGREEN, 0);
            analogWrite(ACBlue, 0);
            break;
          case 2:
            Serial.println("AC HIGH");
            analogWrite(ACRED, 0);
            analogWrite(ACGREEN, 0);
            analogWrite(ACBlue, 255);
            break;
          case 3:
            Serial.println("AC Middle");
            analogWrite(ACRED, 0);
            analogWrite(ACGREEN, 255);
            analogWrite(ACBlue, 0);
            break;
          case 4:
            Serial.println("AC LOW");
            analogWrite(ACRED, 255);
            analogWrite(ACGREEN, 255);
            analogWrite(ACBlue, 255);
            break;
          default:
            Serial.println("Unknown command");
            break;
        }

      else if (strncmp(cmd, "SBM", 3) == 0 && (value == 0 || value == 1)) 
      {
        if (value == 1) 
        {
          // Serial.println("Opening Blind");
          stepper.moveTo(0);  // 블라인드를 올리기 (0 스텝, 초기 위치 )
        } 
        else if (value == 0) 
        {
          // Serial.println("Closing Blind");
          stepper.moveTo(-5500);  // 블라인드를 내리기 (2048 스텝, 한 바퀴 반대 방향)
        }
      } 
      else if (strncmp(cmd, "SDM", 3) == 0 && (value == 0 || value == 1)) 
      {
        if (value == 1) 
        {  
          // Serial.println("SDM1");
          myservo.write(doorOpenedPos); // 문 열기
        } else if (value == 0) 
        { 
          // Serial.println("SDM0");
          myservo.write(doorClosedPos); // 문 닫기
        }
      } 
      else if (strncmp(cmd, "SHM", 3) == 0 && (value == 0 || value == 1)) 
      {
        if (value == 1) 
        {
          Serial.println("SHM1");
          analogWrite(ENPin, 100);     // 속도를 200으로 설정 (0~255 범위)
          digitalWrite(IN1Pin, LOW);
          digitalWrite(IN2Pin, HIGH);
        } else if (value == 0) 
        {
          Serial.println("SHM0");
          digitalWrite(IN1Pin, HIGH);
          digitalWrite(IN2Pin, HIGH);
          analogWrite(ENPin, 0);       // 모터 정지
        }
      }
      else if (strncmp(cmd, "SLI", 3) == 0) 
      {
        setLEDColor(value);  // Set the LED color based on the value
      } 
    }
  }
  stepper.run(); // 스텝퍼 모터를 이동시킴
}

void setLEDColor(byte value) 
{
  switch (value) 
  {
    case 0:
      // Turn off all colors (LED off)
      digitalWrite(LightRED, LOW);
      digitalWrite(LightGREEN, LOW);
      digitalWrite(LightBlue, LOW);
      break;
    case 1:
      // Set LED to ACRED
      digitalWrite(LightED, HIGH);
      digitalWrite(LightGREEN, HIGH);
      digitalWrite(LightBlue, HIGH);
      break;
    default:
      // If an unknown value is received, turn off the LED
      digitalWrite(LightRED, LOW);
      digitalWrite(LightGREEN, LOW);
      digitalWrite(LightBlue, LOW);
      break;
  }
}