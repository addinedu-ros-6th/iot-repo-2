#include <AccelStepper.h>

#define BLUE 5
#define GREEN 6
#define RED 7
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
  // stepper.setC urrentPosition(0);  // 현재 위치를 0으로 설정, 초기 위치 설정 (옵션)

  pinMode(RED, OUTPUT);
  pinMode(GREEN, OUTPUT);
  pinMode(BLUE, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    char recv_buffer[5] = {0}; // Initialize serial buffer
    int recv_size = Serial.readBytesUntil('\n', recv_buffer, 4);

    if (recv_size == 4) {
      char cmd[4] = {0};  // Add null-terminator and initialize
      memcpy(cmd, recv_buffer, 3);
      byte value = recv_buffer[3]; // The fourth byte is the command value (0 or 1)

      if (strncmp(cmd, "GLI", 3) == 0) {
        int sensorValue = analogRead(A0);  // Read the light sensor value from A0
        byte scaledValue = map(sensorValue, 0, 1023, 0, 255);  // Scale to 0-255
        Serial.print("GLI");
        Serial.println(scaledValue);  // Send the scaled value as a byte
      }
      else if (strncmp(cmd, "SLI", 3) == 0) {
        setLEDColor(value);  // Set the LED color based on the value
      }
      else if (strncmp(cmd, "SBM", 3) == 0 && (value == 0 || value == 1)) {
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

void setLEDColor(byte value) {
  switch (value) {
    case 0:
      // Turn off all colors (LED off)
      analogWrite(RED, 0);
      analogWrite(GREEN, 0);
      analogWrite(BLUE, 0);
      break;
    case 1:
      // Set LED to red
      analogWrite(RED, 255);
      analogWrite(GREEN, 0);
      analogWrite(BLUE, 0);
      break;
    case 2:
      // Set LED to green
      analogWrite(RED, 0);
      analogWrite(GREEN, 255);
      analogWrite(BLUE, 0);
      break;
    case 3:
      // Set LED to blue
      analogWrite(RED, 0);
      analogWrite(GREEN, 0);
      analogWrite(BLUE, 255);
      break;
    case 4:
      // Set LED to yellow (red + green)
      analogWrite(RED, 255);
      analogWrite(GREEN, 255);
      analogWrite(BLUE, 0);
      break;
    case 5:
      // Set LED to cyan (green + blue)
      analogWrite(RED, 0);
      analogWrite(GREEN, 255);
      analogWrite(BLUE, 255);
      break;
    case 6:
      // Set LED to magenta (red + blue)
      analogWrite(RED, 255);
      analogWrite(GREEN, 0);
      analogWrite(BLUE, 255);
      break;
    case 7:
      // Set LED to white (red + green + blue)
      analogWrite(RED, 255);
      analogWrite(GREEN, 255);
      analogWrite(BLUE, 255);
      break;
    default:
      // If an unknown value is received, turn off the LED
      analogWrite(RED, 0);
      analogWrite(GREEN, 0);
      analogWrite(BLUE, 0);
      break;
  }
}