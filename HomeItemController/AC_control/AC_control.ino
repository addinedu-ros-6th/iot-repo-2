#define BLUE A3
#define GREEN A4
#define RED A5 //아날로그핀으로 변경

void setup() {
  Serial.begin(9600);
  pinMode(RED, OUTPUT);
  pinMode(GREEN, OUTPUT);
  pinMode(BLUE, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) 
  {
    char recv_buffer[5] = {0};
    int recv_size = Serial.readBytesUntil('\n', recv_buffer, 4);

    if (recv_size == 4)
    {
      char cmd[4] = {0};
      strncpy(cmd, recv_buffer, 3);
      byte value = recv_buffer[3];

      if (strncmp(cmd, "SAC", 3) == 0)
      {
        switch(value)
        {
          case 0:
            Serial.println("AC OFF");
            analogWrite(RED, 0);
            analogWrite(GREEN, 0);
            analogWrite(BLUE, 0);
            break;
          case 1:
            Serial.println("AC POWER");
            analogWrite(RED, 255);
            analogWrite(GREEN, 0);
            analogWrite(BLUE, 0);
            break;
          case 2:
            Serial.println("AC HIGH");
            analogWrite(RED, 0);
            analogWrite(GREEN, 0);
            analogWrite(BLUE, 255);
            break;
          case 3:
            Serial.println("AC Middle");
            analogWrite(RED, 0);
            analogWrite(GREEN, 255);
            analogWrite(BLUE, 0);
            break;
          case 4:
            Serial.println("AC LOW");
            analogWrite(RED, 255);
            analogWrite(GREEN, 255);
            analogWrite(BLUE, 255);
            break;
          default:
            Serial.println("Unknown command");
            break;
        }
      } 
    }
  } 
}